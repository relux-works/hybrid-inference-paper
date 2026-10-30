#!/usr/bin/env python3
"""Agent session statistics for the hybrid-inference study (server prefill, client decode).

Reads Claude Code, Codex CLI and Muse session logs and reports, per model call:
  depth      context tokens the call was conditioned on (cached + uncached input);
  new_in     input tokens added since the previous call, excluding the previous
             call's own output (tool results, user text, injected reminders);
  output     generated tokens (thinking/reasoning included);
  gap        seconds between consecutive calls of the same agent (model + tool time);
and per tool result its size. These are the inputs of the hybrid model: new_in is what
the server would prefill per turn, output is what the client decodes.

Privacy: only numbers leave the script. No text, no file paths, no project names; the
optional per-call CSV carries salted hashes instead of session ids.

Python 3.8+, standard library only. Examples:
  python3 agent_session_stats.py --auto --out stats.json
  python3 agent_session_stats.py --auto --sample 300 --since 2026-06-01 --csv calls.csv
  python3 agent_session_stats.py --claude ~/.claude/projects --codex ~/.codex/sessions
"""
import argparse
import datetime as dt
import fnmatch
import glob
import hashlib
import json
import os
import random
import statistics
import sys
import time

VERSION = "1.0"
CHARS_PER_TOKEN = 3.6     # rough, for tool-result sizes measured in characters


# ------------------------------------------------------------------ helpers
def parse_ts(v):
    """ISO string or epoch number (s, ms, us, ns) -> epoch seconds, or None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        x = float(v)
        if x > 1e17:
            return x / 1e9      # ns
        if x > 1e14:
            return x / 1e6      # us
        if x > 1e11:
            return x / 1e3      # ms
        return x
    if isinstance(v, str):
        s = v.strip().replace("Z", "+00:00")
        try:
            return dt.datetime.fromisoformat(s).timestamp()
        except ValueError:
            try:
                return dt.datetime.fromisoformat(s[:26] + s[-6:]).timestamp()
            except ValueError:
                return None
    return None


def text_len(v):
    """Total length of text in a tool result (str, list of parts, or dict)."""
    if v is None:
        return 0
    if isinstance(v, str):
        return len(v)
    if isinstance(v, list):
        return sum(text_len(x) for x in v)
    if isinstance(v, dict):
        if v.get("type") in ("image", "input_image"):
            return 0
        for k in ("text", "content", "output"):
            if k in v:
                return text_len(v[k])
    return 0


def lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except ValueError:
                continue


class Stream:
    """One agent context: ordered model calls and tool results."""

    def __init__(self, agent, key):
        self.agent, self.key = agent, key
        self.calls = {}        # call id -> dict(t, prompt, cached, output, reasoning, model)
        self.tools = []        # tool result sizes, chars
        self.order = 0

    def add_call(self, cid, t, prompt, cached, output, reasoning, model):
        c = self.calls.get(cid)
        if c is None:
            self.order += 1
            self.calls[cid] = dict(t=t, prompt=prompt, cached=cached, output=output,
                                   reasoning=reasoning, model=model, n=self.order)
        else:   # streamed blocks repeat usage; keep the final (largest) output
            c["output"] = max(c["output"], output)
            c["reasoning"] = max(c["reasoning"], reasoning)
            if c["t"] is None:
                c["t"] = t


# ------------------------------------------------------------------ readers
def read_claude(path):
    streams = {}
    for e in lines(path):
        typ = e.get("type")
        key = (bool(e.get("isSidechain")), e.get("agentId"))
        if typ == "assistant":
            m = e.get("message") or {}
            u = m.get("usage")
            if not isinstance(u, dict) or m.get("model") == "<synthetic>":
                continue
            inp = int(u.get("input_tokens") or 0)
            cw = int(u.get("cache_creation_input_tokens") or 0)
            cr = int(u.get("cache_read_input_tokens") or 0)
            out = int(u.get("output_tokens") or 0)
            reas = int(((u.get("output_tokens_details") or {}).get("thinking_tokens")) or 0)
            cid = m.get("id") or e.get("requestId") or e.get("uuid")
            s = streams.setdefault(key, Stream("claude", (path, key)))
            s.add_call(cid, parse_ts(e.get("timestamp")), inp + cw + cr, cr, out, reas, m.get("model"))
        elif typ == "user":
            c = (e.get("message") or {}).get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        streams.setdefault(key, Stream("claude", (path, key))).tools.append(text_len(b.get("content")))
    return list(streams.values())


def read_codex(path):
    streams, model, have_records, last_total = {}, None, False, {}
    pending = []
    for e in lines(path):
        typ, p = e.get("type"), e.get("payload") or {}
        if typ == "turn_context":
            model = p.get("model") or model
        elif typ == "token_usage_record":
            have_records = True
            u = p.get("usage") or {}
            tid = p.get("thread_id") or "main"
            s = streams.setdefault(tid, Stream("codex", (path, tid)))
            s.add_call(p.get("response_id") or e.get("ordinal"), parse_ts(e.get("timestamp")),
                       int(u.get("input_tokens") or 0), int(u.get("cached_input_tokens") or 0),
                       int(u.get("output_tokens") or 0), int(u.get("reasoning_output_tokens") or 0), model)
        elif typ == "event_msg" and p.get("type") == "token_count":
            info = p.get("info") or {}
            lu, tu = info.get("last_token_usage"), info.get("total_token_usage")
            if isinstance(lu, dict) and isinstance(tu, dict):
                sig = tu.get("total_tokens")
                if last_total.get("main") != sig:
                    last_total["main"] = sig
                    pending.append((sig, parse_ts(e.get("timestamp")), lu, model))
        elif typ == "response_item" and p.get("type") in (
                "function_call_output", "custom_tool_call_output", "local_shell_call_output", "tool_search_output"):
            tid = "main"
            streams.setdefault(tid, Stream("codex", (path, tid))).tools.append(text_len(p.get("output")))
    if not have_records:   # older rollouts: per-response usage only via token_count events
        s = streams.setdefault("main", Stream("codex", (path, "main")))
        for sig, t, lu, mdl in pending:
            s.add_call(sig, t, int(lu.get("input_tokens") or 0), int(lu.get("cached_input_tokens") or 0),
                       int(lu.get("output_tokens") or 0), int(lu.get("reasoning_output_tokens") or 0), mdl)
    return list(streams.values())


def muse_events(path):
    for r in lines(path):
        if "children" in r:
            for ch in r.get("children") or []:
                try:
                    yield json.loads(ch.get("record_json") or "")
                except (ValueError, AttributeError):
                    continue
        elif r.get("record_type") == "event":
            yield r


def read_muse(path):
    s = Stream("muse", (path, "main"))
    for r in muse_events(path):
        if r.get("payload_type") != "runtime.session":
            continue
        p = r.get("payload") or {}
        ev = p.get("event") if isinstance(p.get("event"), dict) else {}
        kind = ev.get("kind")
        if kind == "model_completed":
            u = ev.get("usage") or {}
            inp = int(u.get("input_tokens") or 0)
            cached = int(u.get("cache_read_tokens") or u.get("cached_tokens") or 0)
            prompt = inp + cached if cached > inp else inp     # Anthropic-style vs OpenAI-style accounting
            s.add_call(r.get("id") or r.get("sequence"), parse_ts(r.get("recorded_at")), prompt, cached,
                       int(u.get("output_tokens") or 0), int(u.get("reasoning_tokens") or 0), ev.get("model"))
        elif kind == "tool_result_batch_committed":
            for res in ev.get("results") or []:
                s.tools.append(text_len(res.get("text")))
    return [s]


READERS = {"claude": read_claude, "codex": read_codex, "muse": read_muse}


# ------------------------------------------------------------------ discovery
def default_roots():
    h = os.path.expanduser("~")
    cur = os.path.join(h, ".curator", "environments", "*")
    roots = {
        "claude": [os.path.join(h, ".claude", "projects"), os.path.join(cur, "claude_code", "projects")],
        "codex": [os.path.join(h, ".codex", "sessions"), os.path.join(cur, "codex*", "sessions")],
        "muse": [os.path.join(h, ".local", "share", "muse", "sessions"),
                 os.path.join(h, "Library", "Application Support", "muse", "sessions"),
                 os.path.join(cur, "muse", "data", "muse", "sessions")],
    }
    for env, agent in (("CLAUDE_CONFIG_DIR", "claude"), ("CODEX_HOME", "codex")):
        if os.environ.get(env):
            roots[agent].append(os.path.join(os.environ[env], "projects" if agent == "claude" else "sessions"))
    return roots


PATTERNS = {"claude": "*.jsonl", "codex": "rollout-*.jsonl", "muse": "session.jsonl"}


def find_files(agent, roots):
    out = set()
    for root in roots:
        for r in glob.glob(os.path.expanduser(root)):
            for dirpath, _, files in os.walk(r):
                for fn in files:
                    if fnmatch.fnmatch(fn, PATTERNS[agent]):
                        out.add(os.path.join(dirpath, fn))
    return sorted(out)


# ------------------------------------------------------------------ statistics
def pct(xs, ps=(10, 25, 50, 75, 90, 99)):
    if not xs:
        return None
    xs = sorted(xs)
    res = {}
    for p in ps:
        k = (len(xs) - 1) * p / 100
        lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
        res[f"p{p}"] = round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 1)
    res["mean"] = round(statistics.fmean(xs), 1)
    res["n"] = len(xs)
    return res


def analyse(streams, min_calls):
    calls, first, gaps, depth, outs, reas, tools = [], [], [], [], [], [], []
    per_stream, resets, uncarried = [], 0, 0
    by_depth = {"<50k": [], "50-100k": [], "100-200k": [], "200k+": []}
    rows = []
    for s in streams:
        tools.extend(t / CHARS_PER_TOKEN for t in s.tools)   # tool results count even without usage records
        cs = sorted(s.calls.values(), key=lambda c: (c["t"] if c["t"] is not None else 0, c["n"]))
        if len(cs) < min_calls:
            continue
        first.append(cs[0]["prompt"])
        prev = None
        news = []
        for c in cs:
            new = None
            if prev is not None:
                growth = c["prompt"] - prev["prompt"]
                if growth < -0.2 * prev["prompt"]:
                    resets += 1                   # compaction or a fresh context
                elif growth >= prev["output"]:
                    new = growth - prev["output"]
                else:
                    uncarried += 1                # previous output (e.g. thinking) not carried in full
                    new = max(growth, 0)
                if c["t"] is not None and prev["t"] is not None and c["t"] >= prev["t"]:
                    gaps.append(c["t"] - prev["t"])
            if new is not None:
                calls.append(new)
                news.append(new)
                b = "<50k" if c["prompt"] < 50e3 else "50-100k" if c["prompt"] < 100e3 else \
                    "100-200k" if c["prompt"] < 200e3 else "200k+"
                by_depth[b].append(new)
            depth.append(c["prompt"])
            outs.append(c["output"])
            reas.append(c["reasoning"])
            rows.append((s.agent, c["model"], s.key, c["n"], c["t"], c["prompt"], new, c["output"], c["reasoning"]))
            prev = c
        ts = [c["t"] for c in cs if c["t"] is not None]
        per_stream.append(dict(calls=len(cs), max_depth=max(c["prompt"] for c in cs),
                               duration=(max(ts) - min(ts)) if len(ts) > 1 else 0,
                               new_total=sum(news), out_total=sum(c["output"] for c in cs)))
    tot_new = sum(calls) or 1
    share = {f">={k//1000}k": round(sum(x for x in calls if x >= k) / tot_new, 3) for k in (2000, 5000, 10000, 30000)}
    return dict(
        streams=len(per_stream), calls=len(depth),
        new_in_per_call=pct(calls), output_per_call=pct(outs), reasoning_per_call=pct(reas),
        depth_per_call=pct(depth), first_call_prompt=pct(first), gap_seconds=pct(gaps),
        tool_result_tokens_est=pct(tools),
        new_in_by_depth={k: pct(v, (50, 90)) for k, v in by_depth.items()},
        share_of_new_tokens_in_calls=share,
        calls_per_stream=pct([x["calls"] for x in per_stream]),
        max_depth_per_stream=pct([x["max_depth"] for x in per_stream]),
        duration_s_per_stream=pct([x["duration"] for x in per_stream]),
        new_in_total_per_stream=pct([x["new_total"] for x in per_stream]),
        output_total_per_stream=pct([x["out_total"] for x in per_stream]),
        resets=resets, calls_with_uncarried_output=uncarried,
    ), rows


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--auto", action="store_true", help="scan the default locations of all three agents")
    for a in READERS:
        ap.add_argument(f"--{a}", nargs="*", default=[], metavar="DIR", help=f"{a} session directories")
    ap.add_argument("--sample", type=int, default=0, help="random sample of N files per agent (0 = all)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--since", help="only files modified on or after YYYY-MM-DD")
    ap.add_argument("--min-calls", type=int, default=3, help="skip contexts with fewer model calls")
    ap.add_argument("--max-mb", type=float, default=500, help="skip files larger than this")
    ap.add_argument("--out", default="agent_session_stats.json")
    ap.add_argument("--csv", help="optional per-call numeric CSV (hashed ids, no content)")
    args = ap.parse_args()

    roots = default_roots() if args.auto else {a: [] for a in READERS}
    for a in READERS:
        roots[a] = roots.get(a, []) + getattr(args, a)
    since = dt.datetime.fromisoformat(args.since).timestamp() if args.since else None
    rnd = random.Random(args.seed)
    salt = os.urandom(8)
    report = dict(tool="agent_session_stats", version=VERSION, generated=dt.datetime.utcnow().isoformat() + "Z",
                  python=sys.version.split()[0], platform=sys.platform, params=dict(
                      sample=args.sample, since=args.since, min_calls=args.min_calls, chars_per_token=CHARS_PER_TOKEN),
                  agents={})
    all_streams, all_rows, models = [], [], {}
    t0 = time.time()
    for agent, reader in READERS.items():
        files = find_files(agent, roots[agent])
        files = [f for f in files if os.path.getsize(f) <= args.max_mb * 1e6 and (since is None or os.path.getmtime(f) >= since)]
        found = len(files)
        if args.sample and len(files) > args.sample:
            files = rnd.sample(files, args.sample)
        streams, errors = [], 0
        for i, f in enumerate(files):
            try:
                streams.extend(reader(f))
            except Exception:       # a broken or foreign file must not stop the run
                errors += 1
            if (i + 1) % 50 == 0:
                print(f"  {agent}: {i+1}/{len(files)} files", file=sys.stderr)
        for s in streams:
            for c in s.calls.values():
                if c["model"]:
                    models[(agent, c["model"])] = models.get((agent, c["model"]), 0) + 1
        stats, rows = analyse(streams, args.min_calls)
        stats.update(files_found=found, files_read=len(files), files_failed=errors)
        report["agents"][agent] = stats
        all_streams.extend(streams)
        all_rows.extend(rows)
    report["agents"]["all"], _ = analyse(all_streams, args.min_calls)
    report["models"] = [dict(agent=a, model=m, calls=n) for (a, m), n in sorted(models.items(), key=lambda x: -x[1])]
    report["seconds"] = round(time.time() - t0, 1)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=1)
    if args.csv:
        import csv
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["agent", "model", "stream", "call", "t_rel_s", "depth", "new_in", "output", "reasoning"])
            t_first = {}
            for agent, model, key, n, t, depth, new, out, reas in all_rows:
                h = hashlib.sha256(salt + repr(key).encode()).hexdigest()[:12]
                if t is not None:
                    t_first.setdefault(h, t)
                w.writerow([agent, model, h, n, round(t - t_first[h], 1) if t is not None else "",
                            depth, "" if new is None else new, out, reas])

    def m(d, k="p50"):
        return "-" if not d else f"{d[k]:,.0f}"
    print(f"agent_session_stats {VERSION}: {report['seconds']} s -> {args.out}")
    print("agent   files  contexts  calls | new_in p50 / p90 / mean | output p50 / mean | depth p50 / p90 | tool result p50 / p90 | gap p50 s")
    for a, s in report["agents"].items():
        if not s.get("calls"):
            print(f"{a:<7} no data (files found: {s.get('files_found', '-')})")
            continue
        print(f"{a:<7} {s.get('files_read', '-'):>5} {s['streams']:>9} {s['calls']:>6} | "
              f"{m(s['new_in_per_call'])} / {m(s['new_in_per_call'], 'p90')} / {m(s['new_in_per_call'], 'mean')} | "
              f"{m(s['output_per_call'])} / {m(s['output_per_call'], 'mean')} | "
              f"{m(s['depth_per_call'])} / {m(s['depth_per_call'], 'p90')} | "
              f"{m(s['tool_result_tokens_est'])} / {m(s['tool_result_tokens_est'], 'p90')} | {m(s['gap_seconds'])}")


if __name__ == "__main__":
    main()
