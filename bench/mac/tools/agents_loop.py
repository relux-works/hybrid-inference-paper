#!/usr/bin/env python3
"""Several agent sessions working at once on one llama-server, the way agents do.

Each session starts from the same context of --depth tokens and then, for --turns turns, receives a tool result (new
tokens), reads it and generates an answer. The sizes are drawn, with a fixed seed, from the measured call mix of the
paper: new tokens per call and generated tokens per call. The generated tokens are the logged output, which already
contains the reasoning (for Claude and Codex the reasoning counter is a breakdown inside the output, not an addition;
--with-reasoning adds it on top as an upper bound). The quantiles below come from
data/measurements/ivmbp-2026-10-30/session-call-dates/stats.json ("agents.all", 1,528,194 calls). Sizes are capped at
--max-new and --max-gen, and clamped so that a session never outgrows its slot (clamps are counted).

All sessions run concurrently, so a session's tool result is read while other sessions generate, as on a real client.
Per call the record keeps the new and generated token counts, the server's prefill and decode times and the wall time.
Each session has its own slot, so the interference of the other sessions shows up as slower prefill and decode inside
the server times and a longer wall time; the excess of the wall time over the server times is request overhead. A call
whose server read more than its new tokens (a re-read of the context) is flagged. The JSONL names the overhead wait_s
and mean_wait_s, as version 1.0 did.

The start context: --from-slot restores parallel-depth-<depth>.bin from the server's --slot-save-path (made with
parallel_depth.py, possibly on another machine; same model, llama.cpp commit, KV type and rope settings); otherwise one
slot is filled once here and saved as agents-loop-<depth>.bin. The token sequence comes from parallel_depth.py, so both
paths give the same context.

Needs llama-server with -np >= max(agents), a per-slot context of at least depth + --room, and --slot-save-path.
Python 3.8+, standard library only. Nothing leaves the machine: the tool talks only to --url.
"""
import argparse
import json
import math
import os
import random
import statistics
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parallel_depth as pd  # noqa: E402  (same folder: token synthesis and HTTP helpers)

VERSION = "1.1"
# Quantiles of the measured call mix (see the docstring for the source).
NEW_TOKENS = [(0.10, 0), (0.25, 32), (0.50, 157), (0.75, 804), (0.90, 3048), (0.99, 10875)]
OUTPUT_TOKENS = [(0.10, 54), (0.25, 113), (0.50, 229), (0.75, 531), (0.90, 1136), (0.99, 4502)]
REASONING_TOKENS = [(0.10, 0), (0.25, 0), (0.50, 27), (0.75, 166), (0.90, 516), (0.99, 2583)]
SUFFIX_TOKENS = 16


def sample(quantiles, u):
    """Inverse CDF through the quantiles: linear below the median, log-linear above it, flat beyond p99."""
    pts = [(0.0, 0.0)] + [(q, float(v)) for q, v in quantiles]
    if u >= pts[-1][0]:
        return int(pts[-1][1])
    for (q0, v0), (q1, v1) in zip(pts, pts[1:]):
        if q0 <= u <= q1:
            t = (u - q0) / (q1 - q0) if q1 > q0 else 0.0
            if q0 >= 0.5 and v0 > 0 and v1 > 0:
                return int(round(math.exp(math.log(v0) + t * (math.log(v1) - math.log(v0)))))
            return int(round(v0 + t * (v1 - v0)))
    return int(pts[-1][1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8080")
    ap.add_argument("--label", required=True)
    ap.add_argument("--notes", default="")
    ap.add_argument("--depth", default="128k")
    ap.add_argument("--agents", default="1,4,8", help="comma-separated numbers of concurrent sessions")
    ap.add_argument("--turns", type=int, default=4, help="tool-result-and-answer turns per session")
    ap.add_argument("--room", type=int, default=49152, help="tokens each slot has above the depth")
    ap.add_argument("--max-new", type=int, default=8192)
    ap.add_argument("--max-gen", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--from-slot", action="store_true")
    ap.add_argument("--with-reasoning", action="store_true", help="add the reasoning counter on top (upper bound)")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    url = args.url.rstrip("/")
    depth = pd.parse_k(args.depth)
    agents = sorted({int(x) for x in args.agents.split(",") if x.strip()})
    if not agents or agents[0] < 1 or args.turns < 1:
        sys.exit("--agents needs positive integers and --turns at least 1")
    props = pd.http(url + "/props")
    n_ctx = (props.get("default_generation_settings") or {}).get("n_ctx")
    slots = props.get("total_slots")
    if slots is not None and max(agents) > slots:
        sys.exit(f"the server has {slots} slots; {max(agents)} are needed (start it with -np {max(agents)})")
    if n_ctx is not None and n_ctx < depth + args.room:
        sys.exit(f"per-slot context {n_ctx} is below depth {depth} + room {args.room}")
    limit = (n_ctx or depth + args.room) - 64

    os.makedirs(args.outdir, exist_ok=True)
    base = os.path.join(args.outdir, f"agents-loop-{args.label}-{time.strftime('%Y%m%dT%H%M%S')}")
    jl = open(base + ".jsonl", "w")
    lock = threading.Lock()

    def rec(**kw):
        kw["ts"] = round(time.time(), 3)
        with lock:
            jl.write(json.dumps(kw) + "\n")
            jl.flush()

    rec(kind="meta", tool="agents_loop", version=VERSION, label=args.label, notes=args.notes, depth=depth, agents=agents,
        turns=args.turns, room=args.room, max_new=args.max_new, max_gen=args.max_gen, seed=args.seed,
        mode="from-slot" if args.from_slot else "fill", with_reasoning=args.with_reasoning, n_ctx_slot=n_ctx, total_slots=slots,
        model_file=os.path.basename(props.get("model_path") or ""), build=props.get("build_info"), system=pd.sysinfo())

    tokens = pd.synth_tokens(url, depth, seed=1)
    filename = f"parallel-depth-{depth}.bin" if args.from_slot else f"agents-loop-{depth}.bin"
    if not args.from_slot:
        pre = pd.complete(url, tokens, 0, 0)
        rate = pre["prompt_n"] / (pre["prompt_ms"] / 1000) if pre.get("prompt_ms") else None
        rec(kind="prefill", depth=len(tokens), prefill_tok_s=round(rate, 1) if rate else None, **pre)
        saved = pd.http(url + "/slots/0?action=save", {"filename": filename}, timeout=3600)
        rec(kind="slot_save", filename=filename, n_saved=saved.get("n_saved"), bytes=saved.get("n_written"))
    pool = pd.synth_tokens(url, args.max_new + SUFFIX_TOKENS * max(agents) + 1024, seed=3)

    summary = []
    for n in agents:
        errors = []
        for slot in range(n):
            r = pd.http(url + f"/slots/{slot}?action=restore", {"filename": filename}, timeout=3600)
            rec(kind="slot_restore", agents=n, slot=slot, n_restored=r.get("n_restored"))
            if r.get("n_restored") != len(tokens):
                errors.append(f"slot {slot}: restored {r.get('n_restored')} tokens, expected {len(tokens)}")
        if errors:
            row = dict(agents=n, streams=n, valid=False, calls=0, errors=errors)
            rec(kind="round", **row)
            summary.append(dict(row, elapsed_s=0, clamps=0, aggregate_decode_tok_s=None, mean_stream_decode_tok_s=None,
                                mean_prefill_tok_s=None, call_wall_p50_s=None, call_wall_p90_s=None, mean_wait_s=None,
                                rereads=0))
            print(f"{n} session(s): restore failed, round skipped: {errors}", flush=True)
            continue
        calls = []
        clamps = [0]

        def session(i):
            rnd = random.Random(args.seed * 1000 + n * 100 + i)
            seq = tokens + pool[i * SUFFIX_TOKENS:(i + 1) * SUFFIX_TOKENS]
            offset = rnd.randrange(0, max(1, len(pool) - args.max_new))
            for turn in range(args.turns):
                new = min(sample(NEW_TOKENS, rnd.random()), args.max_new)
                gen = sample(OUTPUT_TOKENS, rnd.random())
                if args.with_reasoning:
                    gen += sample(REASONING_TOKENS, rnd.random())
                gen = min(gen, args.max_gen)
                gen = max(gen, 1)
                room = limit - len(seq)
                if new + gen > room:
                    with lock:
                        clamps[0] += 1
                    new, gen = max(0, min(new, room - gen)), max(1, min(gen, room))
                if room < 2:
                    with lock:
                        errors.append(f"session {i} turn {turn}: the slot is full")
                    break
                prompt = seq + pool[offset:offset + new]
                t0 = time.time()
                try:
                    r = pd.http(url + "/completion", {"prompt": prompt, "n_predict": gen, "id_slot": i, "cache_prompt": True,
                                                      "temperature": 0.0, "ignore_eos": True, "stream": False,
                                                      "return_tokens": True})
                except Exception as e:  # recorded; the round is then invalid
                    with lock:
                        errors.append(f"session {i} turn {turn}: {e}")
                    return
                wall = time.time() - t0
                t = r.get("timings") or {}
                out = r.get("tokens") or []
                seq = prompt + list(out)
                offset = (offset + new) % max(1, len(pool) - args.max_new)
                c = dict(agents=n, session=i, turn=turn, new=new, gen=gen, depth_before=len(prompt) - new,
                         prompt_n=t.get("prompt_n"), prompt_ms=t.get("prompt_ms"), predicted_n=t.get("predicted_n"),
                         predicted_ms=t.get("predicted_ms"), cached=r.get("tokens_cached"), wall_s=round(wall, 3))
                server_s = ((t.get("prompt_ms") or 0) + (t.get("predicted_ms") or 0)) / 1000
                c["wait_s"] = round(max(0.0, wall - server_s), 3)
                c["reread"] = (t.get("prompt_n") or 0) > new + SUFFIX_TOKENS + 2
                with lock:
                    calls.append(c)
                rec(kind="call", **c)
                if len(out) != gen:
                    with lock:
                        errors.append(f"session {i} turn {turn}: {len(out)} tokens back, {gen} asked")

        threads = [threading.Thread(target=session, args=(i,)) for i in range(n)]
        t0 = time.time()
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        elapsed = time.time() - t0
        valid = not errors and len(calls) == n * args.turns
        walls = sorted(c["wall_s"] for c in calls)
        gen_total = sum(c.get("predicted_n") or 0 for c in calls)
        new_total = sum(c["new"] for c in calls)
        dec = [c["predicted_n"] / (c["predicted_ms"] / 1000) for c in calls if c.get("predicted_ms")]
        pre_rates = [c["prompt_n"] / (c["prompt_ms"] / 1000) for c in calls if c.get("prompt_ms") and c.get("prompt_n")]
        rereads = sum(1 for c in calls if c.get("reread"))
        row = dict(agents=n, streams=n, valid=valid, calls=len(calls), elapsed_s=round(elapsed, 1), clamps=clamps[0],
                   rereads=rereads,
                   generated=gen_total, new_tokens=new_total,
                   aggregate_decode_tok_s=round(gen_total / elapsed, 3) if elapsed else None,
                   mean_stream_decode_tok_s=round(statistics.mean(dec), 3) if dec else None,
                   mean_prefill_tok_s=round(statistics.mean(pre_rates), 1) if pre_rates else None,
                   call_wall_p50_s=round(walls[len(walls) // 2], 2) if walls else None,
                   call_wall_p90_s=round(walls[min(len(walls) - 1, int(len(walls) * 0.9))], 2) if walls else None,
                   mean_wait_s=round(statistics.mean(c["wait_s"] for c in calls), 2) if calls else None,
                   errors=errors)
        rec(kind="round", **row)
        summary.append(row)
        print(f"{n} session(s): {len(calls)} calls in {elapsed:.0f}s, aggregate decode {row['aggregate_decode_tok_s']} tok/s, "
              f"call p50 {row['call_wall_p50_s']}s, p90 {row['call_wall_p90_s']}s" + (f", errors: {errors}" if errors else ""),
              flush=True)

    with open(base + ".md", "w") as md:
        md.write(f"# Agent sessions at depth {depth}: {args.label}\n\n")
        md.write(f"agents_loop {VERSION}; model {os.path.basename(props.get('model_path') or '')}; build "
                 f"{props.get('build_info')}; {args.turns} turns per session; sizes from the measured call mix, capped at "
                 f"{args.max_new} new and {args.max_gen} generated tokens; generated tokens "
                 f"{'output plus reasoning (upper bound)' if args.with_reasoning else 'from the output'}; seed {args.seed}.\n\n")
        md.write("| Sessions | Calls | Elapsed, s | Aggregate decode, tok/s | Mean stream decode, tok/s | Mean prefill, tok/s "
                 "| Call p50, s | Call p90, s | Mean overhead, s | Clamps | Re-reads | Valid |\n")
        md.write("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")
        for r in summary:
            md.write(f"| {r['agents']} | {r['calls']} | {r['elapsed_s']} | {r['aggregate_decode_tok_s']} | "
                     f"{r['mean_stream_decode_tok_s']} | {r['mean_prefill_tok_s']} | {r['call_wall_p50_s']} | "
                     f"{r['call_wall_p90_s']} | {r['mean_wait_s']} | {r['clamps']} | {r.get('rereads', 0)} | {r['valid']} |\n")
        md.write("\nAggregate decode: tokens generated by all sessions divided by the round's elapsed time. The other "
                 "sessions' load shows as slower prefill and decode and longer calls; overhead is a call's wall time beyond "
                 "the server's own prefill and decode time. Re-reads: calls whose server read more than the new tokens; "
                 "they should be zero.\n")
    jl.close()
    print(f"results: {base}.jsonl and {base}.md")


if __name__ == "__main__":
    main()
