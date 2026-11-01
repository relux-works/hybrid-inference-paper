#!/usr/bin/env python3
"""Long-context prefill/decode benchmark for the hybrid-inference study.

Measures on a local inference server, at context depths up to 260k (or more):
  * marginal prefill rate of each depth segment (a "ladder"). Every request strictly extends
    what the server already holds, generated tokens included, like a real agent session.
    That matters for hybrid models (Gated DeltaNet + attention): their recurrent state cannot
    be rolled back to an earlier position, so any divergence forces a full re-prefill;
  * prefill of a fresh turn delta (512 / 2k / 10k tokens) on top of a cached context of
    depth L: this is the per-turn cost the hybrid offloads to the server;
  * decode rate at depth L (one stream), and optionally the aggregate decode rate of
    K parallel streams (batching gain);
  * optionally the size and time of a KV-cache slot save/restore (bytes per token incl.
    the recurrent state), when llama-server runs with --slot-save-path.

Two server APIs:
  --api llama   llama.cpp llama-server native API (/tokenize, /completion, exact token counts,
                server-side timings). Preferred.
  --api openai  any OpenAI-compatible server with streaming (/v1/completions): mlx_lm.server,
                LM Studio, oMLX, vllm-metal. Timings are client-side (time to first token,
                streaming rate); token counts come from the usage block when the server sends it.
  --api chat    servers with only the chat API (/v1/chat/completions), such as Strata. The session
                is a growing message list and every reply is appended verbatim. Thinking is off
                (chat_template_kwargs enable_thinking=false) unless --thinking is given. Server-side
                timings are used when the server sends llama.cpp-style `timings` (Strata does).

Nothing leaves the machine: the script talks only to --url and writes results locally.
Prompts are synthetic (generated text), never user files.

Example (Qwen3.8-27B, llama-server started with a single slot and enough context):
  llama-server -m Qwen3.8-27B-Q4_K_M.gguf -c 290000 -np 1 -fa on -ctk q8_0 -ctv q8_0 --port 8080
  python3 hybrid_bench.py --label q27b-q4km-q8kv --notes "fa on, q8_0 KV"
Smoke test first (two minutes): add --smoke.
Parallel decode needs a second server run with -np 4 (and -c large enough for 4 x depth):
  python3 hybrid_bench.py --label q27b-par4 --only-parallel --parallel 4 --parallel-depth 32k

Python 3.8+, standard library only.
"""
import argparse
import json
import os
import platform
import random
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

VERSION = "1.1"


# ------------------------------------------------------------------ utils
def parse_k(s):
    s = s.strip().lower()
    mult = 1
    if s.endswith("k"):
        mult, s = 1000, s[:-1]
    elif s.endswith("m"):
        mult, s = 1000000, s[:-1]
    return int(float(s) * mult)


def http(url, payload=None, timeout=4 * 3600, method=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode() or "{}")


def sysinfo():
    info = dict(python=sys.version.split()[0], platform=platform.platform(), machine=platform.machine())
    if sys.platform == "darwin":
        for key in ("machdep.cpu.brand_string", "hw.memsize", "hw.model"):
            try:
                info[key] = subprocess.run(["sysctl", "-n", key], capture_output=True, text=True, timeout=5).stdout.strip()
            except Exception:
                pass
    return info


WORDS = ("cache prefill decode tensor kernel stream batch token layer head query value buffer "
         "server client network session state model weight memory bandwidth latency request "
         "schedule queue worker thread result error retry config module import return yield").split()
NAMES = ("alpha beta gamma delta sigma omega kappa theta lambda zeta nova orbit pixel vector "
         "matrix packet socket router signal sensor ledger anchor bridge harbor").split()


def synth_text(n_chars, seed):
    """Deterministic code-and-prose mix; no external data."""
    rnd = random.Random(seed)
    out, size = [], 0
    while size < n_chars:
        kind = rnd.random()
        if kind < 0.55:
            fn = f"{rnd.choice(NAMES)}_{rnd.choice(WORDS)}_{rnd.randint(0, 999)}"
            args = ", ".join(f"{rnd.choice(WORDS)}{rnd.randint(0, 9)}" for _ in range(rnd.randint(1, 4)))
            body = [f"    {rnd.choice(WORDS)}_{i} = {rnd.choice(NAMES)}.{rnd.choice(WORDS)}({rnd.randint(0, 4096)})"
                    for i in range(rnd.randint(2, 7))]
            block = f"def {fn}({args}):\n" + "\n".join(body) + f"\n    return {rnd.choice(WORDS)}_0\n\n"
        else:
            sent = " ".join(rnd.choice(WORDS + NAMES) for _ in range(rnd.randint(8, 22)))
            block = f"# {sent.capitalize()}. Step {rnd.randint(1, 99)} of {rnd.choice(NAMES)}.\n"
        out.append(block)
        size += len(block)
    return "".join(out)[:n_chars]


class Recorder:
    def __init__(self, path):
        self.path = path
        self.rows = []

    def add(self, **kw):
        kw["ts"] = round(time.time(), 3)
        self.rows.append(kw)
        with open(self.path, "a") as f:
            f.write(json.dumps(kw) + "\n")
        brief = {k: v for k, v in kw.items() if k not in ("ts",)}
        print("  " + json.dumps(brief), flush=True)


# ------------------------------------------------------------------ llama-server backend
class Llama:
    def __init__(self, url):
        self.url = url.rstrip("/")

    def wait(self):
        for _ in range(120):
            try:
                if http(self.url + "/health", timeout=10).get("status") in ("ok", "no slot available"):
                    return
            except (urllib.error.URLError, OSError, ValueError):
                pass
            time.sleep(5)
        raise SystemExit("server not healthy at " + self.url)

    def props(self):
        p = http(self.url + "/props", timeout=30)
        g = p.get("default_generation_settings") or {}
        n_ctx = g.get("n_ctx") or p.get("n_ctx")
        mp = p.get("model_path") or ""
        return dict(n_ctx=n_ctx, total_slots=p.get("total_slots"), model_file=os.path.basename(mp),
                    build=p.get("build_info"))

    def tokenize(self, text):
        return http(self.url + "/tokenize", {"content": text, "add_special": False}, timeout=600)["tokens"]

    def complete(self, tokens, n_predict, slot=0):
        t0 = time.time()
        r = http(self.url + "/completion", {
            "prompt": tokens, "n_predict": n_predict, "cache_prompt": True, "id_slot": slot,
            "temperature": 0.0, "ignore_eos": True, "stream": False, "return_tokens": True})
        wall = time.time() - t0
        t = r.get("timings") or {}
        gen = r.get("tokens")
        exact = isinstance(gen, list) and (len(gen) > 0 or n_predict == 0)
        if not exact:
            gen = self.tokenize(r.get("content") or "") if n_predict else []
        out = dict(prompt_n=t.get("prompt_n"), prompt_ms=t.get("prompt_ms"), predicted_n=t.get("predicted_n"),
                   predicted_ms=t.get("predicted_ms"), cached=r.get("tokens_cached"), wall_s=round(wall, 3),
                   truncated=r.get("truncated"), gen_tokens_exact=exact)
        return out, list(gen)

    def slot(self, action, filename, slot=0):
        return http(f"{self.url}/slots/{slot}?action={action}", {"filename": filename}, timeout=3600)


def build_tokens(backend, n_tokens, seed):
    toks, chunk, i = [], 200000, 0
    while len(toks) < n_tokens:
        toks.extend(backend.tokenize(synth_text(chunk, seed * 1000 + i)))
        i += 1
    return toks[:n_tokens]


def run_llama(args, rec):
    b = Llama(args.url)
    b.wait()
    pr = b.props()
    rec.add(kind="server", api="llama", **pr)
    n_ctx = pr["n_ctx"] or 0
    depths, deltas = [parse_k(x) for x in args.depths.split(",")], [parse_k(x) for x in args.deltas.split(",")]
    if not args.only_parallel:
        room = n_ctx - max(deltas) - args.gen - 32
        usable = [L for L in depths if L <= room]
        for L in depths:
            if L > room:
                rec.add(kind="skip", depth=L, reason=f"n_ctx per slot {n_ctx} too small; start the server with -c >= {L + max(deltas) + args.gen + 64} and -np 1")
        if usable:
            per_level = sum(deltas) + args.gen * len(deltas)
            print(f"tokenizing synthetic prompt ({usable[-1]} + deltas) ...", flush=True)
            T = build_tokens(b, usable[-1], seed=1)
            U = build_tokens(b, max(sum(deltas), 1), seed=2)
            seq, t_used, reuse_ok = [], 0, True
            for L in usable:
                need = L - len(seq)
                if need <= 0:
                    rec.add(kind="skip", depth=L, reason="already past this depth")
                    continue
                if t_used + need > len(T):
                    T += build_tokens(b, need + 1000, seed=100 + L)
                prompt = seq + T[t_used:t_used + need]
                t_used += need
                r, _ = b.complete(prompt, 0)
                seq = prompt
                rate = r["prompt_n"] / (r["prompt_ms"] / 1000) if r.get("prompt_ms") else None
                reused = (r["prompt_n"] or 0) <= need + 2048
                rec.add(kind="segment", depth_from=len(seq) - need, depth=len(seq), **r,
                        prefill_tok_s=round(rate, 1) if rate else None, cache_reused=reused)
                if not reused:
                    reuse_ok = False
                    print("WARNING: the server re-processed the whole prompt: no prefix-cache reuse. "
                          "Turn deltas would each cost a full re-prefill and are skipped.", flush=True)
                if args.slot_save:
                    try:
                        sv = b.slot("save", f"hybrid-bench-{L}.bin")
                        rec.add(kind="slot_save", depth=len(seq), n_saved=sv.get("n_saved"), bytes=sv.get("n_written"),
                                ms=(sv.get("timings") or {}).get("save_ms"))
                        sv = b.slot("restore", f"hybrid-bench-{L}.bin")
                        rec.add(kind="slot_restore", depth=len(seq), n_restored=sv.get("n_restored"), bytes=sv.get("n_read"),
                                ms=(sv.get("timings") or {}).get("restore_ms"))
                    except Exception as e:   # endpoint disabled without --slot-save-path
                        rec.add(kind="slot_save", depth=len(seq), error=str(e)[:200])
                if not reuse_ok and not args.force:
                    continue
                off = 0
                for d in deltas:
                    piece = [U[(off + i) % len(U)] for i in range(d)]
                    off += d
                    prompt = seq + piece
                    r, gen = b.complete(prompt, args.gen)
                    seq = prompt + gen
                    pre = r["prompt_n"] / (r["prompt_ms"] / 1000) if r.get("prompt_ms") else None
                    dec = r["predicted_n"] / (r["predicted_ms"] / 1000) if r.get("predicted_ms") else None
                    rec.add(kind="turn", level=L, depth=len(prompt) - d, delta=d, **r,
                            prefill_tok_s=round(pre, 1) if pre else None, decode_tok_s=round(dec, 2) if dec else None)
                    if (r["prompt_n"] or 0) > d + 2048:
                        reuse_ok = False
                        print("WARNING: a turn delta was re-processed from scratch; skipping further deltas.", flush=True)
                        break
    if args.parallel:
        run_parallel_llama(b, args, rec, pr)


def run_parallel_llama(b, args, rec, pr):
    K, Lp = args.parallel, parse_k(args.parallel_depth)
    slots = pr.get("total_slots") or 1
    if slots < K:
        rec.add(kind="skip", parallel=K, reason=f"server has {slots} slots; restart with -np {K}")
        return
    per_slot = (pr["n_ctx"] or 0)
    if per_slot and per_slot < Lp + args.gen + 64:
        rec.add(kind="skip", parallel=K, reason=f"per-slot context {per_slot} < {Lp + args.gen + 64}; raise -c")
        return
    seqs = [build_tokens(b, Lp + 64, seed=10 + k) for k in range(K)]
    held = []
    for k in range(K):
        b.complete(seqs[k][:Lp], 0, slot=k)          # fill each slot's cache
        held.append(seqs[k][:Lp])
    r0, g0 = b.complete(held[0] + seqs[0][Lp:Lp + 16], args.gen, slot=0)
    held[0] = held[0] + seqs[0][Lp:Lp + 16] + g0
    s_rate = r0["predicted_n"] / (r0["predicted_ms"] / 1000)
    res = [None] * K

    def worker(k):
        res[k], _ = b.complete(held[k] + seqs[k][Lp + 16:Lp + 32], args.gen, slot=k)
    t0 = time.time()
    th = [threading.Thread(target=worker, args=(k,)) for k in range(K)]
    for t in th:
        t.start()
    for t in th:
        t.join()
    wall = time.time() - t0
    tokens = sum(r["predicted_n"] or 0 for r in res)
    dec_ms = max(r["predicted_ms"] or 0 for r in res)
    rec.add(kind="parallel", streams=K, depth=Lp, single_decode_tok_s=round(s_rate, 2),
            per_stream_decode_tok_s=[round(r["predicted_n"] / (r["predicted_ms"] / 1000), 2) for r in res],
            aggregate_decode_tok_s=round(tokens / (dec_ms / 1000), 2), batching_gain=round(tokens / (dec_ms / 1000) / s_rate, 2),
            wall_s=round(wall, 2))


# ------------------------------------------------------------------ OpenAI-compatible backend
class OpenAI:
    def __init__(self, url, model):
        self.url, self.model = url.rstrip("/"), model

    def stream(self, prompt, max_tokens):
        body = {"prompt": prompt, "max_tokens": max_tokens, "temperature": 0.0, "stream": True,
                "stream_options": {"include_usage": True}}
        if self.model:
            body["model"] = self.model
        req = urllib.request.Request(self.url + "/v1/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.time()
        t_first, n_chunks, usage, pieces = None, 0, None, []
        with urllib.request.urlopen(req, timeout=4 * 3600) as r:
            for raw in r:
                line = raw.decode(errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    ev = json.loads(data)
                except ValueError:
                    continue
                if ev.get("usage"):
                    usage = ev["usage"]
                ch = (ev.get("choices") or [{}])[0]
                if ch.get("text"):
                    pieces.append(ch["text"])
                    n_chunks += 1
                    if t_first is None:
                        t_first = time.time()
        t_end = time.time()
        u = usage or {}
        out_tok = u.get("completion_tokens") or n_chunks
        cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens")
        dec = (out_tok - 1) / (t_end - t_first) if t_first and out_tok > 1 and t_end > t_first else None
        return dict(ttft_s=round((t_first or t_end) - t0, 3), prompt_tokens=u.get("prompt_tokens"), cached_tokens=cached,
                    completion_tokens=out_tok, decode_tok_s=round(dec, 2) if dec else None), "".join(pieces)


def run_openai(args, rec):
    b = OpenAI(args.url, args.model)
    depths, deltas = [parse_k(x) for x in args.depths.split(",")], [parse_k(x) for x in args.deltas.split(",")]
    probe, _ = b.stream(synth_text(40000, 3), 1)
    cpt = 40000 / probe["prompt_tokens"] if probe.get("prompt_tokens") else 3.6
    rec.add(kind="server", api="openai", model=args.model, chars_per_token=round(cpt, 3),
            usage_reported=bool(probe.get("prompt_tokens")))
    text = synth_text(int((depths[-1] + 1000) * cpt), 1)
    dtext = synth_text(int(sum(deltas) * cpt) + 1000, 2)
    seq, used, prev = "", 0, 0
    for L in depths:
        need = int(L * cpt) - len(seq)
        if need <= 0:
            continue
        seq_new = seq + text[used:used + need]
        used += need
        r, g = b.stream(seq_new, 1)
        seq = seq_new + g
        new = (r["prompt_tokens"] - (r["cached_tokens"] or 0)) if r.get("prompt_tokens") else L - prev
        rec.add(kind="segment", depth_from=prev, depth=L, **r, prefill_tok_s=round(new / r["ttft_s"], 1) if r["ttft_s"] else None)
        off = 0
        for d in deltas:
            piece = dtext[off:off + int(d * cpt)]
            off += int(d * cpt)
            r, g = b.stream(seq + piece, args.gen)
            seq = seq + piece + g
            new = (r["prompt_tokens"] - (r["cached_tokens"] or 0)) if r.get("prompt_tokens") and r.get("cached_tokens") is not None else d
            rec.add(kind="turn", level=L, depth=L, delta=d, **r, prefill_tok_s=round(new / r["ttft_s"], 1) if r["ttft_s"] else None)
        prev = L


class Chat:
    """OpenAI chat API with streaming (/v1/chat/completions)."""

    def __init__(self, url, model, thinking):
        self.url, self.model, self.thinking = url.rstrip("/"), model, thinking

    def stream(self, messages, max_tokens):
        body = {"messages": messages, "max_tokens": max_tokens, "temperature": 0.0, "stream": True,
                "stream_options": {"include_usage": True}}
        if not self.thinking:
            body["chat_template_kwargs"] = {"enable_thinking": False}
        if self.model:
            body["model"] = self.model
        req = urllib.request.Request(self.url + "/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.time()
        t_first, n_chunks, usage, tm, content, reasoning = None, 0, None, None, [], []
        with urllib.request.urlopen(req, timeout=4 * 3600) as r:
            for raw in r:
                line = raw.decode(errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    ev = json.loads(data)
                except ValueError:
                    continue
                if ev.get("usage"):
                    usage = ev["usage"]
                if ev.get("timings"):
                    tm = ev["timings"]
                d = (ev.get("choices") or [{}])[0].get("delta") or {}
                if d.get("content"):
                    content.append(d["content"])
                if d.get("reasoning_content"):
                    reasoning.append(d["reasoning_content"])
                if d.get("content") or d.get("reasoning_content"):
                    n_chunks += 1
                    if t_first is None:
                        t_first = time.time()
        t_end = time.time()
        u, tm = usage or {}, tm or {}
        out_tok = u.get("completion_tokens") or n_chunks
        dec = (out_tok - 1) / (t_end - t_first) if t_first and out_tok > 1 and t_end > t_first else None
        res = dict(ttft_s=round((t_first or t_end) - t0, 3), prompt_tokens=u.get("prompt_tokens"),
                   cached_tokens=(u.get("prompt_tokens_details") or {}).get("cached_tokens"), completion_tokens=out_tok,
                   decode_tok_s=round(dec, 2) if dec else None)
        if tm.get("prompt_ms") is not None:      # server-side timings in llama.cpp's names
            res.update(prompt_n=tm.get("prompt_n"), prompt_ms=tm.get("prompt_ms"), cache_n=tm.get("cache_n"),
                       server_decode_tok_s=tm.get("predicted_per_second"))
        reply = {"role": "assistant", "content": "".join(content)}
        if reasoning:
            reply["reasoning_content"] = "".join(reasoning)
        return res, reply


def run_chat(args, rec):
    b = Chat(args.url, args.model, args.thinking)
    depths, deltas = [parse_k(x) for x in args.depths.split(",")], [parse_k(x) for x in args.deltas.split(",")]
    probe, _ = b.stream([{"role": "user", "content": synth_text(40000, 3)}], 1)
    cpt = 40000 / probe["prompt_tokens"] if probe.get("prompt_tokens") else 3.6
    rec.add(kind="server", api="chat", model=args.model, thinking=args.thinking, chars_per_token=round(cpt, 3),
            usage_reported=bool(probe.get("prompt_tokens")), server_timings=probe.get("prompt_ms") is not None)
    text = synth_text(int((depths[-1] + 1000) * cpt), 1)
    dtext = synth_text(int(sum(deltas) * cpt) + 1000, 2)
    msgs, used = [], 0
    state = {"held": 0, "reuse_ok": True}

    def ask(n_new, max_tokens):
        # Send the session, append the reply verbatim; return the row, the tokens read and the seconds spent.
        r, reply = b.stream(msgs, max_tokens)
        msgs.append(reply)
        if r.get("prompt_n") is not None:
            new, secs = r["prompt_n"], (r.get("prompt_ms") or 0) / 1000
        elif r.get("prompt_tokens") and r.get("cached_tokens") is not None:
            new, secs = r["prompt_tokens"] - r["cached_tokens"], r["ttft_s"]
        else:
            new, secs = n_new, r["ttft_s"]
        reused = state["held"] == 0 or new <= 1.15 * n_new + 256   # read only the new part (token estimates are approximate)
        if not reused and state["reuse_ok"]:
            state["reuse_ok"] = False
            print("WARNING: the server re-processed the conversation: no prefix-cache reuse. Turn deltas would "
                  "each cost a full re-prefill and are skipped (--force measures them anyway).", flush=True)
        state["held"] = (r.get("prompt_tokens") or state["held"] + n_new) + (r.get("completion_tokens") or 0)
        return r, new, secs, reused

    prev = 0
    for L in depths:
        need = L - state["held"]
        if need <= 0:
            rec.add(kind="skip", depth=L, reason="already past this depth")
            continue
        msgs.append({"role": "user", "content": text[used:used + int(need * cpt)]})
        used += int(need * cpt)
        r, new, secs, reused = ask(need, 1)
        rec.add(kind="segment", level=L, depth_from=prev, depth=r.get("prompt_tokens") or L, **r,
                prefill_tok_s=round(new / secs, 1) if secs else None, cache_reused=reused)
        prev = r.get("prompt_tokens") or L
        if not state["reuse_ok"] and not args.force:
            continue
        off = 0
        for d in deltas:
            msgs.append({"role": "user", "content": dtext[off:off + int(d * cpt)]})
            off += int(d * cpt)
            r, new, secs, reused = ask(d, args.gen)
            client_dec = r.pop("decode_tok_s")
            rec.add(kind="turn", level=L, depth=(r.get("prompt_tokens") or L + d) - d, delta=d, **r,
                    client_decode_tok_s=client_dec, decode_tok_s=r.get("server_decode_tok_s") or client_dec,
                    prefill_tok_s=round(new / secs, 1) if secs else None, cache_reused=reused)
            if not reused and not args.force:
                break


# ------------------------------------------------------------------ summary
def summary(rows, path):
    seg = [r for r in rows if r["kind"] == "segment"]
    turns = [r for r in rows if r["kind"] == "turn"]
    out = ["| depth | segment prefill tok/s | " + " | ".join(f"Δ{d} prefill tok/s" for d in sorted({t['delta'] for t in turns}))
           + " | decode tok/s (at depth) |", "|---" * (3 + len({t['delta'] for t in turns})) + "|"]
    cum = 0.0
    for s in seg:
        ms = s.get("prompt_ms") or (s.get("ttft_s") or 0) * 1000
        cum += ms / 1000
        tt = [t for t in turns if t.get("level") in (s["depth"], s.get("level")) or abs(t["depth"] - s["depth"]) <= 1]
        cells = []
        for d in sorted({t['delta'] for t in turns}):
            t = next((t for t in tt if t["delta"] == d), None)
            cells.append("-" if t is None else f"{t.get('prefill_tok_s')}" + (" (full re-prefill)" if t.get("cache_reused") is False else ""))
        dec = [t.get("decode_tok_s") for t in tt if t.get("decode_tok_s")]
        out.append(f"| {s['depth']//1000}k (cum. {cum/60:.1f} min) | {s.get('prefill_tok_s')} | " + " | ".join(cells)
                   + f" | {round(sum(dec)/len(dec), 2) if dec else '-'} |")
    for r in rows:
        if r["kind"] == "parallel":
            out.append(f"\nparallel: {r['streams']} streams at {r['depth']//1000}k: aggregate {r['aggregate_decode_tok_s']} tok/s, "
                       f"single {r['single_decode_tok_s']}, gain x{r['batching_gain']}")
        if r["kind"] == "slot_save" and r.get("bytes"):
            out.append(f"slot save at {r['depth']//1000}k: {r['bytes']/1e6:.0f} MB = {r['bytes']/max(r['n_saved'],1)/1024:.1f} KiB/token, {r['ms']} ms")
    txt = "\n".join(out)
    with open(path, "w") as f:
        f.write(txt + "\n")
    print("\n" + txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8080")
    ap.add_argument("--api", choices=("llama", "openai", "chat"), default="llama")
    ap.add_argument("--model", default="", help="model name for --api openai or chat")
    ap.add_argument("--thinking", action="store_true", help="--api chat: leave the model's thinking on")
    ap.add_argument("--label", required=True, help="short name of the model/quant/engine run, used in file names")
    ap.add_argument("--notes", default="", help="free text: engine flags, KV type, quant")
    ap.add_argument("--depths", default="16k,50k,100k,150k,200k,260k")
    ap.add_argument("--deltas", default="512,2k,10k")
    ap.add_argument("--gen", type=int, default=128, help="tokens to decode after each turn delta")
    ap.add_argument("--parallel", type=int, default=0, help="also measure K parallel decode streams")
    ap.add_argument("--parallel-depth", default="32k")
    ap.add_argument("--only-parallel", action="store_true")
    ap.add_argument("--slot-save", action="store_true", help="measure KV slot save/restore (needs --slot-save-path)")
    ap.add_argument("--smoke", action="store_true", help="tiny run to check the setup")
    ap.add_argument("--force", action="store_true", help="measure turn deltas even without prefix-cache reuse")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()
    if args.smoke:
        args.depths, args.deltas, args.gen = "2k,4k", "256,512", 16
        if args.parallel:
            args.parallel_depth = "2k"
    stamp = time.strftime("%Y%m%dT%H%M%S")
    base = os.path.join(args.outdir, f"hybrid-bench-{args.label}-{stamp}")
    rec = Recorder(base + ".jsonl")
    rec.add(kind="meta", tool="hybrid_bench", version=VERSION, label=args.label, notes=args.notes,
            depths=args.depths, deltas=args.deltas, gen=args.gen, smoke=args.smoke, **sysinfo())
    t0 = time.time()
    try:
        {"llama": run_llama, "openai": run_openai, "chat": run_chat}[args.api](args, rec)
    except KeyboardInterrupt:
        rec.add(kind="interrupted")
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        rec.add(kind="error", error=f"{type(e).__name__}: {str(e)[:300]}")
    rec.add(kind="done", minutes=round((time.time() - t0) / 60, 1))
    summary(rec.rows, base + ".md")
    print(f"\nresults: {base}.jsonl and {base}.md")


if __name__ == "__main__":
    main()
