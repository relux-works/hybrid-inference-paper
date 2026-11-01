#!/usr/bin/env python3
"""Aggregate decode of K parallel streams at a deep context, on llama-server.

One slot is filled to the requested depth once and saved. Before every measurement round the saved state is
restored into each slot of the round, because a hybrid model's recurrent state cannot be rolled back after
generation. Each round then sends the same prompt plus a short new suffix to K slots at once and decodes --gen
tokens per stream. The suffix makes every request extend what its slot holds, so the server never has to roll
back. K streams at 64k or 128k therefore cost one prefill instead of K.

Aggregate decode follows the reference convention: the sum of timed decode steps divided by the longest server
decode interval of the round.

Needs llama-server started with -np >= max(streams), a per-slot context above depth + 1024, and --slot-save-path.

Two modes move the long fill to another machine: --fill-only fills and saves the slot file parallel-depth-<depth>.bin
and stops (run it on a GPU); --from-slot skips the fill and restores that file, which must already be in the server's
--slot-save-path (copy it there from the GPU). The token sequence is the same on both machines: it is generated from a
fixed seed and the server's own tokenizer, so the restored slot matches the prompt. Both servers need the same model
file, the same llama.cpp build, the same KV cache type and the same rope settings.
Python 3.8+, standard library only. It talks only to --url and writes results to --outdir.
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import threading
import time
import urllib.request

VERSION = "1.1"
SUFFIX_TOKENS = 16


def http(url, payload=None, timeout=4 * 3600):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def parse_k(text):
    text = text.strip().lower()
    return int(float(text[:-1]) * 1024) if text.endswith("k") else int(text)


def sysinfo():
    info = dict(python=sys.version.split()[0], platform=platform.platform(), machine=platform.machine())
    if sys.platform == "darwin":
        for key in ("machdep.cpu.brand_string", "hw.memsize", "hw.model"):
            try:
                info[key] = subprocess.run(["sysctl", "-n", key], capture_output=True, text=True, timeout=5).stdout.strip()
            except Exception:
                pass
    return info


def synth_tokens(url, count, seed):
    """Deterministic synthetic text, tokenized by the server, cut to exactly `count` token IDs."""
    words = ["model", "cache", "state", "token", "agent", "server", "client", "memory", "depth", "stream",
             "prefill", "decode", "layer", "attention", "linear", "batch", "slot", "delta", "journal", "route"]
    out, i = [], 0
    while len(out) < count:
        chunk = " ".join(words[(seed * 13 + i * 7 + j * 3) % len(words)] + str((seed * 101 + i * 31 + j) % 997)
                         for j in range(2000))
        out += http(url + "/tokenize", {"content": chunk})["tokens"]
        i += 1
    return out[:count]


def complete(url, tokens, n_predict, slot):
    t0 = time.time()
    r = http(url + "/completion", {"prompt": tokens, "n_predict": n_predict, "id_slot": slot, "cache_prompt": True,
                                   "temperature": 0.0, "ignore_eos": True, "stream": False, "return_tokens": True})
    t = r.get("timings") or {}
    return dict(slot=slot, prompt_n=t.get("prompt_n"), prompt_ms=t.get("prompt_ms"), predicted_n=t.get("predicted_n"),
                predicted_ms=t.get("predicted_ms"), cached=r.get("tokens_cached"), wall_s=round(time.time() - t0, 3))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8080")
    ap.add_argument("--label", required=True, help="short run name used in file names")
    ap.add_argument("--notes", default="")
    ap.add_argument("--depth", default="64k", help="context depth of every stream, for example 64k or 128k")
    ap.add_argument("--streams", default="1,2,4,8", help="comma-separated numbers of parallel streams")
    ap.add_argument("--gen", type=int, default=128, help="tokens decoded per stream in each round")
    ap.add_argument("--outdir", default=".")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--fill-only", action="store_true", help="fill and save the slot file, then stop")
    mode.add_argument("--from-slot", action="store_true", help="restore an existing slot file instead of filling")
    args = ap.parse_args()

    url = args.url.rstrip("/")
    depth = parse_k(args.depth)
    streams = sorted({int(x) for x in args.streams.split(",") if x.strip()})
    if not streams or streams[0] < 1:
        sys.exit("--streams needs positive integers")
    props = http(url + "/props")
    n_ctx = (props.get("default_generation_settings") or {}).get("n_ctx")
    slots = props.get("total_slots")
    if args.fill_only:
        streams = [1]
    if slots is not None and max(streams) > slots:
        sys.exit(f"the server has {slots} slots; {max(streams)} are needed (start it with -np {max(streams)})")
    if n_ctx is not None and n_ctx < depth + SUFFIX_TOKENS + args.gen + 8:
        sys.exit(f"per-slot context {n_ctx} is below depth {depth} + suffix + {args.gen} generated tokens")

    os.makedirs(args.outdir, exist_ok=True)
    base = os.path.join(args.outdir, f"parallel-depth-{args.label}-{time.strftime('%Y%m%dT%H%M%S')}")
    rows = []
    jl = open(base + ".jsonl", "w")

    def rec(**kw):
        kw["ts"] = round(time.time(), 3)
        rows.append(kw)
        jl.write(json.dumps(kw) + "\n")
        jl.flush()

    rec(kind="meta", tool="parallel_depth", version=VERSION, label=args.label, notes=args.notes, depth=depth,
        streams=streams, gen=args.gen, n_ctx_slot=n_ctx, total_slots=slots,
        mode="fill-only" if args.fill_only else "from-slot" if args.from_slot else "fill-and-measure",
        model_file=os.path.basename(props.get("model_path") or ""), build=props.get("build_info"), system=sysinfo())

    tokens = synth_tokens(url, depth, seed=1)
    suffix = synth_tokens(url, SUFFIX_TOKENS, seed=2)
    filename = f"parallel-depth-{depth}.bin"

    pre, rate = {}, None
    if args.from_slot:
        rec(kind="from_slot", filename=filename)
        print(f"using the existing slot file {filename} for {len(tokens)} tokens", flush=True)
    else:
        pre = complete(url, tokens, 0, 0)
        rate = pre["prompt_n"] / (pre["prompt_ms"] / 1000) if pre.get("prompt_ms") else None
        rec(kind="prefill", depth=len(tokens), prefill_tok_s=round(rate, 1) if rate else None, **pre)
        saved = http(url + f"/slots/0?action=save", {"filename": filename}, timeout=3600)
        rec(kind="slot_save", filename=filename, n_saved=saved.get("n_saved"), bytes=saved.get("n_written"),
            timings=saved.get("timings"))
        print(f"filled one slot to {len(tokens)} tokens and saved it ({saved.get('n_written')} bytes)", flush=True)
    if args.fill_only:
        with open(base + ".md", "w") as md:
            md.write(f"# Slot file for depth {depth}: {args.label}\n\n")
            md.write(f"parallel_depth {VERSION}; model {os.path.basename(props.get('model_path') or '')}; "
                     f"build {props.get('build_info')}.\n\n")
            if rate:
                md.write(f"Prefill of {len(tokens)} tokens: {rate:.1f} tok/s.\n\n")
            md.write(f"Saved `{filename}` in the server's --slot-save-path.\n")
        jl.close()
        print(f"results: {base}.jsonl and {base}.md")
        return

    summary = []
    for k in streams:
        restore_errors = []
        for slot in range(k):
            r = http(url + f"/slots/{slot}?action=restore", {"filename": filename}, timeout=3600)
            rec(kind="slot_restore", streams=k, slot=slot, n_restored=r.get("n_restored"), bytes=r.get("n_read"),
                timings=r.get("timings"))
            if r.get("n_restored") != len(tokens):
                restore_errors.append(f"slot {slot}: restored {r.get('n_restored')} tokens, expected {len(tokens)}")
        if restore_errors:
            rec(kind="round", streams=k, depth=len(tokens) + SUFFIX_TOKENS, valid=False, restore_reused=False,
                aggregate_tok_s=None, per_stream_tok_s=None, wall_s=0, errors=restore_errors, requests=[])
            summary.append((k, None, None, False, restore_errors))
            print(f"{k} stream(s): restore failed, round skipped: {restore_errors}", flush=True)
            continue
        results = [None] * k
        errors = []

        def run(i):
            try:
                results[i] = complete(url, tokens + suffix, args.gen, i)
            except Exception as e:  # recorded below; the round is then marked invalid
                errors.append(f"slot {i}: {e}")

        threads = [threading.Thread(target=run, args=(i,)) for i in range(k)]
        t0 = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wall = time.time() - t0
        valid = not errors and all(r and r.get("predicted_n") and r.get("predicted_ms") for r in results)
        reused = valid and all((r.get("prompt_n") or 0) <= SUFFIX_TOKENS + 2 for r in results)
        steps = sum(max((r.get("predicted_n") or 0) - 1, 0) for r in results) if valid else None
        longest = max(r["predicted_ms"] for r in results) / 1000 if valid else None
        aggregate = round(steps / longest, 3) if valid and longest else None
        per_stream = [round(max(r["predicted_n"] - 1, 0) / (r["predicted_ms"] / 1000), 3) for r in results] if valid else None
        rec(kind="round", streams=k, depth=len(tokens) + SUFFIX_TOKENS, valid=valid, restore_reused=reused,
            aggregate_tok_s=aggregate, per_stream_tok_s=per_stream, wall_s=round(wall, 3), errors=errors,
            requests=results)
        summary.append((k, aggregate, per_stream, reused, errors))
        print(f"{k} stream(s) at {len(tokens)}: aggregate {aggregate} tok/s, restore reused: {reused}"
              + (f", errors: {errors}" if errors else ""), flush=True)

    base_rate = summary[0][1] if summary and summary[0][0] == 1 else None
    with open(base + ".md", "w") as md:
        md.write(f"# Parallel decode at depth {depth}: {args.label}\n\n")
        md.write(f"parallel_depth {VERSION}; model {os.path.basename(props.get('model_path') or '')}; "
                 f"build {props.get('build_info')}; {args.gen} tokens per stream.\n\n")
        if pre.get("prompt_ms"):
            md.write(f"One-time prefill of {len(tokens)} tokens: {rate:.1f} tok/s.\n\n")
        md.write("| Streams | Aggregate decode, tok/s | Mean per stream, tok/s | Gain over one stream | Restore reused |\n")
        md.write("|---:|---:|---:|---:|---|\n")
        for k, aggregate, per_stream, reused, errors in summary:
            mean = round(sum(per_stream) / len(per_stream), 2) if per_stream else None
            gain = round(aggregate / base_rate, 3) if aggregate and base_rate else None
            md.write(f"| {k} | {aggregate} | {mean} | {gain} | {reused}{' (errors)' if errors else ''} |\n")
        md.write("\nAggregate: timed decode steps of all streams divided by the longest server decode interval. "
                 "A round with restore_reused false re-read more than the suffix; treat its numbers with care.\n")
    jl.close()
    print(f"results: {base}.jsonl and {base}.md")


if __name__ == "__main__":
    main()
