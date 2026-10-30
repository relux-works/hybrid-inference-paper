#!/usr/bin/env python3
"""Read-only, local Claude Code / Codex / Muse usage statistics, including backups.

Standard library only; no network or provider requests. Contents and native IDs are
never exported. Inputs are bounded to the length seen at file open. ZIP members
are streamed, CRC checked, and never extracted. Reports distinguish usage records
from estimates: new_in is a context-growth heuristic, NOT uncached billing input.
Muse input_tokens are reported unchanged; cache accounting is not guessed.
"""
import argparse
import collections
import contextlib
import datetime as dt
import fnmatch
import glob
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import sys
import time
import zipfile

VERSION = '1.5-call-time'
CHARS_PER_TOKEN = 3.6
AGENTS = ('claude', 'codex', 'muse')
ZIP_HANDLES = {}


def parse_ts(value):
    try:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            x = float(value)
            x /= 1e9 if x > 1e17 else 1e6 if x > 1e14 else 1e3 if x > 1e11 else 1
        elif isinstance(value, str):
            d = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
            x = d.replace(tzinfo=dt.timezone.utc).timestamp() if d.tzinfo is None else d.timestamp()
        else:
            return None
        if not math.isfinite(x):
            return None
        dt.datetime.fromtimestamp(x, dt.timezone.utc)  # require a representable UTC instant
        return x
    except (ValueError, OverflowError, OSError):
        return None


def text_len(value):
    if isinstance(value, str):
        return len(value)
    if isinstance(value, list):
        return sum(map(text_len, value))
    if isinstance(value, dict) and value.get('type') not in ('image', 'input_image'):
        for key in ('text', 'content', 'output'):
            if key in value:
                return text_len(value[key])
    return 0


def number(value):
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError('INVALID_TOKEN_COUNT')
    return value


def usage(u, agent):
    if not isinstance(u, dict) or 'input_tokens' not in u or 'output_tokens' not in u:
        raise ValueError('INCOMPLETE_USAGE')
    inp = number(u.get('input_tokens'))
    cached = number(u.get('cache_read_input_tokens') if agent == 'claude' else
                    u.get('cached_input_tokens') if agent == 'codex' else
                    u.get('cache_read_tokens', u.get('cached_tokens')))
    write = number(u.get('cache_creation_input_tokens')) if agent == 'claude' else 0
    output = number(u.get('output_tokens'))
    details = u.get('output_tokens_details') or {}
    reasoning = number(details.get('thinking_tokens')) if agent == 'claude' else number(
        u.get('reasoning_output_tokens') if agent == 'codex' else u.get('reasoning_tokens'))
    return inp + write + (cached if agent == 'claude' else 0), cached, output, reasoning


class Stream:
    def __init__(self, agent, key):
        self.agent, self.key = agent, key
        self.calls, self.tool_map = {}, {}
        self.order = 0

    @property
    def tools(self):
        return self.tool_map.values()


class Corpus:
    def __init__(self):
        self.streams = {}
        self.seen = {}
        self.unique_calls = 0
        self.seen_tools = {}
        self.audit = {a: collections.Counter() for a in AGENTS}
        self.file_audit = None

    def bump(self, agent, key, count=1):
        self.audit[agent][key] += count
        if self.file_audit is not None:
            self.file_audit[key] += count

    def stream(self, agent, key):
        return self.streams.setdefault((agent, key), Stream(agent, key))

    def timestamp(self, agent, c, value):
        parsed = parse_ts(value)
        if parsed is None:
            c['invalid_timestamp'] |= value is not None
        elif c['t'] is None:
            c['t'] = parsed
        elif c['t'] != parsed:
            c['conflicting_timestamp'] = True
            self.bump(agent, 'conflicting_timestamp_records')

    def call(self, agent, stream, cid, timestamp, u, model, fallback, aliases=()):
        try:
            prompt, cached, output, reasoning = usage(u, agent)
        except (ValueError, AttributeError):
            self.bump(agent, 'invalid_usage_records')
            return
        self.bump(agent, 'usage_records')
        if agent == 'muse' and not any((prompt, cached, output, reasoning)):
            self.bump(agent, 'zero_usage_completions')
        if cached > prompt:
            self.bump(agent, 'cache_greater_than_reported_input')
        if not cid:
            self.bump(agent, 'calls_with_fallback_identity')
            cid = ('fallback', fallback)
        ident = (agent, str(cid))
        identities = [ident] + [(agent, str(x)) for x in aliases]
        old = next((self.seen[x] for x in identities if x in self.seen), None)
        if old is not None and ident != old['primary_identity']:
            self.bump(agent, 'cross_format_identity_matches')
        if old is not None:
            for x in identities:
                self.seen[x] = old
        if old is not None:
            self.bump(agent, 'duplicate_call_records')
            c = old
            if (prompt, cached, output, reasoning) != (c['prompt'], c['cached'], c['output'], c['reasoning']):
                self.bump(agent, 'usage_update_records')
            for k, v in [('prompt', prompt), ('cached', cached), ('output', output), ('reasoning', reasoning)]:
                c[k] = max(c[k], v)
            if not c['model'] and isinstance(model, str):
                c['model'] = model
            self.timestamp(agent, c, timestamp)
            return c
        s = self.stream(agent, stream)
        s.order += 1
        c = dict(t=None, invalid_timestamp=False, conflicting_timestamp=False,
                 prompt=prompt, cached=cached, output=output,
                 reasoning=reasoning, model=model if isinstance(model, str) else None, n=s.order, primary_identity=ident)
        self.timestamp(agent, c, timestamp)
        s.calls[str(cid)] = c
        self.unique_calls += 1
        for x in identities:
            self.seen[x] = c
        return c

    def tool(self, agent, stream, cid, content):
        ident = (agent, cid)
        s = self.seen_tools.get(ident)
        if s is None:
            s = self.stream(agent, stream)
            self.seen_tools[ident] = s
        else:
            self.bump(agent, 'duplicate_tool_records')
        s.tool_map[cid] = max(s.tool_map.get(cid, 0), text_len(content))


def records(source, corpus, agent):
    with source.open() as f:
        remaining = source.size
        i = 0
        while remaining:
            line = f.readline(remaining)
            if not line:
                corpus.bump(agent, 'truncated_source_files')
                break
            remaining -= len(line)
            i += 1
            if not line.strip():
                continue
            try:
                e = json.loads(line)
                if not isinstance(e, dict):
                    corpus.bump(agent, 'non_object_rows')
                    continue
                yield i, e
            except (ValueError, UnicodeError):
                corpus.bump(agent, 'invalid_json_rows')
    if source.member is None:
        after = source.path.stat()
        if after.st_size > source.size:
            corpus.bump(agent, 'files_appended_during_read')
        elif after.st_size != source.size or after.st_mtime_ns != source.mtime_ns:
            corpus.bump(agent, 'files_changed_in_place')


def read_claude(source, corpus):
    for row, e in records(source, corpus, 'claude'):
        session = e.get('sessionId') or e.get('session_id') or source.session_hint
        key = (str(session), bool(e.get('isSidechain')), str(e.get('agentId') or 'main'))
        m = e.get('message') or {}
        if not isinstance(m, dict):
            continue
        if e.get('type') == 'assistant' and m.get('model') != '<synthetic>':
            if m.get('usage') is not None:
                corpus.call('claude', key, m.get('id') or e.get('requestId') or e.get('uuid'),
                            e.get('timestamp'), m['usage'], m.get('model'), (key, row))
            else:
                corpus.bump('claude', 'assistant_rows_without_usage')
        elif e.get('type') == 'user' and isinstance(m.get('content'), list):
            for i, b in enumerate(m['content']):
                if isinstance(b, dict) and b.get('type') == 'tool_result':
                    cid = b.get('tool_use_id') or e.get('uuid') or (source.digest, row, i)
                    corpus.tool('claude', key, str(cid), b.get('content'))


def codex_signature(u, totals):
    fields = ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']
    values = [u.get(k,0) for k in fields] if isinstance(u,dict) else None
    return json.dumps([values, (totals or {}).get('total_tokens')], separators=(',', ':'))


def legacy_identity(session, total):
    fields = ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']
    return ('legacy', session, total.get('total_tokens'), tuple(total.get(k,0) for k in fields))


def read_codex(source, corpus):
    session = source.session_hint
    model = None
    pending, modern = [], {}
    for row, e in records(source, corpus, 'codex'):
        typ, p = e.get('type'), e.get('payload') or {}
        if not isinstance(p, dict):
            continue
        if typ == 'session_meta':
            session = p.get('id') or p.get('session_id') or session
        elif typ == 'turn_context':
            model = p.get('model') or model
        elif typ == 'token_usage_record':
            tid = p.get('thread_id') or p.get('session_id') or session
            u = p.get('usage')
            total = p.get('thread_token_usage') or {}
            # Both formats may coexist. Suppress only the matching cumulative
            # update, never the entire older history of a migrated rollout.
            c = corpus.call('codex', str(tid), p.get('response_id'), e.get('timestamp'), u, model,
                            (session, e.get('ordinal') or row, codex_signature(u, total)),
                            aliases=[legacy_identity(str(tid), total)] if total.get('total_tokens') is not None else [])
            if isinstance(u, dict):
                modern[codex_signature(u, total)] = c
        elif typ == 'event_msg' and p.get('type') == 'token_count':
            info = p.get('info') or {}
            if isinstance(info, dict) and isinstance(info.get('last_token_usage'), dict):
                u, total = info['last_token_usage'], info.get('total_token_usage')
                if isinstance(total, dict):
                    pending.append((u, total, e.get('timestamp'), model, session))
                else:
                    corpus.bump('codex', 'invalid_usage_records')
        elif typ == 'response_item' and p.get('type') in (
                'function_call_output', 'custom_tool_call_output', 'local_shell_call_output', 'tool_search_output'):
            cid = p.get('call_id') or p.get('id') or (source.digest, row)
            corpus.tool('codex', str(session), str(cid), p.get('output'))
    last = None
    for u, total, timestamp, model, session in pending:
        sig = codex_signature(u, total)
        if sig in modern:
            corpus.bump('codex', 'legacy_updates_matched_to_modern')
            # Suppression removes duplicate token usage, not timestamp evidence.
            c = modern[sig]
            if c is not None:
                corpus.timestamp('codex', c, timestamp)
            continue
        cid = legacy_identity(str(session), total)
        if sig == last:
            corpus.bump('codex', 'repeated_legacy_updates')
            c = corpus.seen.get(('codex', str(cid)))
            if c is not None:
                corpus.timestamp('codex', c, timestamp)
            continue
        last = sig
        corpus.call('codex', str(session), cid, timestamp, u, model, cid)


def read_muse(source, corpus):
    model = None
    for row, frame in records(source, corpus, 'muse'):
        entries = []
        if 'children' in frame:
            for child in frame.get('children') or []:
                try:
                    entries.append(json.loads(child.get('record_json') or ''))
                except (ValueError, AttributeError, TypeError):
                    corpus.bump('muse', 'invalid_child_json')
        else:
            entries = [frame]
        for r in entries:
            if not isinstance(r, dict) or r.get('payload_type') != 'runtime.session':
                continue
            p = r.get('payload') or {}
            ev = p.get('event') or {}
            if not isinstance(ev, dict):
                continue
            stream = r.get('stream')
            key = json.dumps(stream, sort_keys=True) if stream else source.session_hint
            kind = ev.get('kind')
            if kind in ('model_request_configured', 'model_started'):
                model = ev.get('model') or model
            elif kind == 'model_completed':
                # Projected runtime.session events identify the original run
                # record; prefer it over projection IDs duplicated across streams.
                cid = p.get('source_run_record_id') or r.get('id')
                corpus.call('muse', key, cid, r.get('recorded_at'), ev.get('usage'),
                            ev.get('model') or model, (key, r.get('sequence') or row))
            elif kind == 'tool_result_batch_committed':
                for i, res in enumerate(ev.get('results') or []):
                    if isinstance(res, dict):
                        cid = res.get('tool_call_id') or (p.get('source_run_record_id') or r.get('id') or source.digest, i)
                        corpus.tool('muse', key, str(cid), res.get('text'))


READERS = {'claude': read_claude, 'codex': read_codex, 'muse': read_muse}


class Source:
    def __init__(self, agent, path, member=None, info=None):
        self.agent, self.path, self.member = agent, Path(path), member
        self.zip_info = info
        st = self.path.stat()
        self.size = info.file_size if info else st.st_size
        self.mtime_ns = st.st_mtime_ns
        self.inode = None if member is not None else (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
        self.session_hint = Path(member or path).stem
        self.digest = None

    @contextlib.contextmanager
    def open(self):
        if self.member is None:
            with self.path.open('rb') as f:
                yield f
        else:
            key = str(self.path.resolve())
            z = ZIP_HANDLES.get(key)
            if z is None:
                z = ZIP_HANDLES[key] = zipfile.ZipFile(self.path)
            with z.open(self.zip_info or self.member) as f:
                yield f

    def fingerprint(self):
        h, remaining = hashlib.sha256(), self.size
        with self.open() as f:
            while remaining:
                b = f.read(min(8 * 1024 * 1024, remaining))
                if not b:
                    raise OSError('SOURCE_SHRANK')
                h.update(b)
                remaining -= len(b)
        self.digest = h.hexdigest()
        return self.digest


def matches(agent, name):
    p = Path(name)
    if agent == 'codex':
        return fnmatch.fnmatch(p.name, 'rollout-*.jsonl')
    if agent == 'muse':
        return p.name == 'session.jsonl'
    # Exclude history/index/metadata logs and arbitrary files in saved tool CWDs.
    return p.suffix == '.jsonl' and any(x == 'projects' or x.endswith('-projects') or
        x == 'claude-desktop-local-sessions' or x == 'local-agent-mode-sessions' for x in p.parts)


def default_roots():
    h = Path.home()
    roots = {a: [] for a in AGENTS}
    claude_homes = [h/'.claude', h/'.config/claude', h/'Library/Developer/Xcode/CodingAssistant/ClaudeAgentConfig']
    codex_homes = [h/'.codex']
    codex_homes.extend(p for p in h.glob('.codex*') if p.is_dir() and
                       ((p/'sessions').is_dir() or (p/'archived_sessions').is_dir()))
    claude_homes.extend(p for p in h.glob('.claude*') if p.is_dir() and (p/'projects').is_dir())
    for p in (h/'.curator/environments').glob('*'):
        claude_homes.append(p/'claude_code')
        codex_homes.extend(p.glob('codex*'))
        roots['muse'].append(str(p/'muse/data/muse/sessions'))
    if os.environ.get('CLAUDE_CONFIG_DIR'):
        claude_homes.append(Path(os.environ['CLAUDE_CONFIG_DIR']))
    if os.environ.get('CODEX_HOME'):
        codex_homes.append(Path(os.environ['CODEX_HOME']))
    for p in claude_homes:
        roots['claude'].extend(str(p/x) for x in ['projects', '.agent-environment-backup'])
    for p in codex_homes:
        roots['codex'].extend(str(p/x) for x in ['sessions', 'archived_sessions', '.agent-environment-backup'])
    roots['muse'].extend(str(p/'muse/sessions') for p in [h/'.local/share', h/'Library/Application Support'])
    if os.environ.get('XDG_DATA_HOME'):
        roots['muse'].append(str(Path(os.environ['XDG_DATA_HOME'])/'muse/sessions'))
    roots['claude'].extend(str(h/p) for p in ['Library/Application Support/Claude/local-agent-mode-sessions',
        'Library/Application Support/ClaudeUsageArchive/raw', 'Library/Application Support/ClaudeUsageArchive/raw-revisions'])
    zip_roots = []
    for p in [h/'Backups/AgentSessions', Path('/Volumes/LaCie/Archives/AgentSessions')]:
        for a in ('claude', 'codex'):
            roots[a].extend(str(p/x) for x in ['cumulative', 'versions'])
        zip_roots.append(str(p/'archives'))
    return {'roots': {a:list(dict.fromkeys(v)) for a,v in roots.items()}, 'zip_roots': zip_roots}


def discover(config):
    sources, coverage, seen = [], [], set()
    for agent in AGENTS:
        for root in config['roots'].get(agent, []):
            item = dict(agent=agent, root=root, present=False, matches=0, errors=0)
            for name in glob.glob(os.path.expanduser(root)):
                item['present'] = True
                def error(_):
                    item['errors'] += 1
                for d, dirs, files in os.walk(name, onerror=error):
                    dirs[:] = [x for x in dirs if x not in {'.git', 'node_modules', '__pycache__'}]
                    for f in files:
                        path = Path(d)/f
                        if not matches(agent, str(path)):
                            continue
                        item['matches'] += 1
                        key = (agent, str(path.resolve()))
                        if key in seen:
                            continue
                        seen.add(key)
                        try:
                            sources.append(Source(agent, path))
                        except OSError:
                            item['errors'] += 1
            coverage.append(item)
    for root in config.get('zip_roots', []):
        item = dict(agent='zip', root=root, present=Path(root).exists(), matches=0, errors=0)
        for path in sorted(Path(root).glob('*.zip')):
            try:
                with zipfile.ZipFile(path) as z:
                    for info in z.infolist():
                        for agent in AGENTS:
                            if matches(agent, info.filename):
                                key = (agent, str(path.resolve()), info.filename, info.header_offset)
                                if key not in seen:
                                    sources.append(Source(agent, path, info.filename, info))
                                    seen.add(key)
                                item['matches'] += 1
                                break
            except (OSError, zipfile.BadZipFile):
                item['errors'] += 1
        coverage.append(item)
    return sources, coverage

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


def call_time(calls):
    times, days = [], set()
    missing = invalid = conflicts = 0
    for c in calls:
        if c['t'] is not None:
            times.append(c['t'])
            days.add(dt.datetime.fromtimestamp(c['t'], dt.timezone.utc).date())
        elif c['invalid_timestamp']:
            invalid += 1
        else:
            missing += 1
        conflicts += c['conflicting_timestamp']
    def utc(t):
        return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    status = ('no_calls' if not calls else 'no_timestamped_calls' if not times else
              'partial' if missing or invalid or conflicts else 'complete')
    return dict(first_utc=utc(min(times)) if times else None,
                last_utc=utc(max(times)) if times else None,
                distinct_utc_days=len(days), timestamped_calls=len(times),
                missing_timestamp_calls=missing, invalid_timestamp_calls=invalid,
                conflicting_timestamp_calls=conflicts, status=status)


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



def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--auto', action='store_true')
    ap.add_argument('--sources', help='JSON manifest: roots per provider and zip_roots; additive to --auto')
    for agent in AGENTS:
        ap.add_argument('--'+agent, nargs='*', default=[])
    ap.add_argument('--sample', type=int, default=0, help='0 = every discovered file/member')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--min-calls', type=int, default=1)
    ap.add_argument('--max-mb', type=float, default=0, help='0 = no size cutoff')
    ap.add_argument('--out', default='agent_session_stats.json')
    ap.add_argument('--coverage', help='PRIVATE root coverage, salted file references, no contents/native IDs')
    ap.add_argument('--csv', help='Optional numeric calls with salted context identifiers')
    args = ap.parse_args()
    if args.sample < 0 or args.min_calls < 1 or not math.isfinite(args.max_mb) or args.max_mb < 0:
        ap.error('invalid sampling/size/context limit')
    config = default_roots() if args.auto else {'roots': {a: [] for a in AGENTS}, 'zip_roots': []}
    if args.sources:
        supplied = json.loads(Path(args.sources).read_text())
        for a in AGENTS:
            config['roots'][a] += supplied['roots'].get(a, [])
        config['zip_roots'] += supplied.get('zip_roots', [])
    for a in AGENTS:
        config['roots'][a] += getattr(args, a)
    start = time.monotonic()
    sources, coverage = discover(config)
    corpus = Corpus()
    salt = os.urandom(32)
    details = []
    digests, inodes = set(), set()
    selected = {a: [] for a in AGENTS}
    for source in sources:
        corpus.bump(source.agent, 'files_discovered')
        corpus.bump(source.agent, 'bytes_discovered', source.size)
        if args.max_mb and source.size > args.max_mb*1e6:
            corpus.bump(source.agent, 'files_size_filtered')
        else:
            selected[source.agent].append(source)
    if args.sample:
        rnd = random.Random(args.seed)
        for a in AGENTS:
            files = selected[a]
            if len(files) > args.sample:
                corpus.bump(a, 'files_sample_filtered', len(files)-args.sample)
                selected[a] = rnd.sample(files, args.sample)
    sequence = sorted([s for ss in selected.values() for s in ss], key=lambda s: (s.member is not None, -s.size))
    progress = time.monotonic()
    pid_path = Path(args.out).with_suffix('.pid')
    pid_path.write_text(str(os.getpid())+'\n')
    for i, source in enumerate(sequence):
        a = source.agent
        file_audit = collections.Counter()
        corpus.file_audit = file_audit
        status = 'read'
        try:
            inode_key = (a, source.inode)
            if source.inode is not None and inode_key in inodes:
                corpus.bump(a, 'duplicate_physical_files')
                status = 'duplicate_physical'
            else:
                digest = source.fingerprint()
                corpus.bump(a, 'bytes_hashed', source.size)
                if source.inode is not None:
                    inodes.add(inode_key)
                if (a, digest) in digests:
                    corpus.bump(a, 'duplicate_content_files')
                    status = 'duplicate_content'
                else:
                    digests.add((a, digest))
                    READERS[a](source, corpus)
                    corpus.bump(a, 'files_parsed')
                    if not file_audit['usage_records']:
                        corpus.bump(a, 'files_without_usage')
                    else:
                        corpus.bump(a, 'files_with_usage')
        except (OSError, ValueError, TypeError, AttributeError, zipfile.BadZipFile, EOFError, RuntimeError) as error:
            corpus.bump(a, 'files_failed')
            file_audit['error_class_'+type(error).__name__] += 1
            status = 'failed'
        finally:
            corpus.file_audit = None
        ref = hashlib.sha256(salt+str((source.path, source.member)).encode()).hexdigest()[:20]
        details.append(dict(ref=ref, agent=a, archive_member=source.member is not None,
                            bytes=source.size, status=status, audit=dict(file_audit)))
        if time.monotonic()-progress > 10 or i+1 == len(sequence):
            print(f'progress {i+1}/{len(sequence)}; unique calls {corpus.unique_calls}; elapsed {time.monotonic()-start:.0f}s', file=sys.stderr, flush=True)
            progress = time.monotonic()
    for archive in ZIP_HANDLES.values():
        archive.close()
    ZIP_HANDLES.clear()
    report = dict(tool='agent_session_stats', version=VERSION,
                  generated=dt.datetime.now(dt.timezone.utc).isoformat(),
                  python=sys.version.split()[0], platform=sys.platform,
                  params=dict(sample=args.sample, min_calls=args.min_calls, max_mb=args.max_mb, chars_per_token=CHARS_PER_TOKEN),
                  notes=[
                      'Session counts are contexts WITH recorded usage, not every discovered transcript. Zero-usage and unreadable files are explicit in coverage.',
                      'new_in is an estimate from context growth, not exact prefill traffic or uncached input; compaction, forks and reasoning retention affect it.',
                      'Muse input_tokens are unchanged as recorded. Cache semantics are unverified; no value-dependent addition is performed.',
                      'Output/reasoning are logged usage fields; reasoning is not added to output. Tool token sizes are character-based estimates.',
                      'Each file is read to its observed length; the corpus is not an atomic cross-session snapshot. Append/in-place changes are counted.',
                      'Copies deduplicate by inode then SHA256; model calls deduplicate by provider response/message/source-record identity.',
                      'Missing response IDs use session/cumulative counters or row identity; fallback identities cannot prove cross-fork equivalence.',
                      'call_time uses recorded usage-event time (Claude/Codex envelope timestamp; Muse recorded_at), not exact model start time or file dates.',
                      'Naive ISO timestamps assume UTC. Numeric timestamps use the existing positive seconds/milliseconds/microseconds/nanoseconds magnitude heuristic.',
                      'Call times use the first valid deduplicated timestamp; later copies can fill absent/invalid time, and disagreements are flagged without adding days.',
                      'Time coverage is independent of source-reading status; distinct UTC days are a set union after min-call filtering, not calendar span or provider sum.'
                  ], agents={})
    all_streams = list(corpus.streams.values())
    all_rows = []
    models = collections.Counter()
    for a in (*AGENTS, 'all'):
        streams = [s for s in all_streams if a == 'all' or s.agent == a]
        stats, rows = analyse(streams, args.min_calls)
        if a != 'all':
            stats['coverage'] = dict(corpus.audit[a])
            all_rows += rows
        cs = [c for s in streams for c in s.calls.values() if len(s.calls) >= args.min_calls]
        stats['call_time'] = call_time(cs)
        stats['totals'] = {k: sum(c[k] for c in cs) for k in ['prompt', 'cached', 'output', 'reasoning']}
        stats['unknown_model_calls'] = sum(not c['model'] for c in cs)
        stats['zero_usage_calls'] = sum(not any(c[k] for k in ['prompt','cached','output','reasoning']) for c in cs)
        report['agents'][a] = stats
    for s in all_streams:
        for c in s.calls.values():
            if c['model']:
                models[(s.agent, c['model'])] += 1
    report['models'] = [dict(agent=a, model=m, calls=n) for (a,m),n in models.most_common()]
    error_keys = ['invalid_json_rows','non_object_rows','invalid_usage_records','invalid_child_json',
                  'files_failed','truncated_source_files','files_changed_in_place','files_size_filtered','files_sample_filtered']
    incomplete = sum(v for a in AGENTS for k,v in corpus.audit[a].items() if k in error_keys)
    incomplete += sum(x['errors'] for x in coverage)
    report['status'] = 'partial' if incomplete or args.min_calls > 1 or not any(s.calls for s in all_streams) else 'complete_for_discovered_sources'
    report['seconds'] = round(time.monotonic()-start, 1)
    os.umask(0o077)
    Path(args.out).write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    if args.coverage:
        Path(args.coverage).write_text(json.dumps(dict(roots=coverage, files=details),indent=2)+'\n')
    if args.csv:
        import csv
        with open(args.csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['agent','model','stream','call','t_rel_s','depth','new_in_est','output','reasoning'])
            first = {}
            for agent,model,key,n,t,depth,new,out,reasoning in all_rows:
                stream = hashlib.sha256(salt+repr((agent,key)).encode()).hexdigest()[:20]
                if t is not None:
                    first.setdefault(stream,t)
                writer.writerow([agent,model,stream,n,round(t-first[stream],1) if t is not None else '',depth,new,out,reasoning])
    print(json.dumps(dict(status=report['status'],seconds=report['seconds'],agents={a:dict(
        contexts=s['streams'],calls=s['calls'],totals=s['totals']) for a,s in report['agents'].items()}),indent=2))
    return 2 if report['status']=='partial' else 0

if __name__ == '__main__':
    sys.exit(main())
