# Hybrid-inference measurement tools

Two standalone scripts for the hybrid-inference study (server prefill, client decode).
Both scripts use Python 3.8+ and its standard library. Neither sends data anywhere: the
session script reads local logs, the benchmark talks only to a local inference server.
Outputs go to the requested paths (defaults are in the current directory).

## 1. `agent_session_stats.py`: what agent turns look like

Reads recorded Claude Code, Codex CLI and Muse usage locally, including live,
Curator, alternate/isolated homes, archived Codex sessions and configured backup
folders/ZIPs. Version 1.5 starts from the validated 1.4 backup-aware implementation;
the delivered 1.4 source and full04 measurements under `data/measurements/` remain
historical evidence. No model/provider or network request is made.

From the repository root:

```bash
mkdir -p .temp/session-stats
python3 tools/agent_session_stats.py --auto --out .temp/session-stats/stats.json \
  --coverage .temp/session-stats/coverage.json
# Explicit reproducible inventory, instead of automatic discovery:
python3 tools/agent_session_stats.py --sources /private/path/sources.json \
  --out .temp/session-stats/stats.json --coverage .temp/session-stats/coverage.json
# Intentional partial sample, capped per provider:
python3 tools/agent_session_stats.py --auto --sample 500 --out .temp/session-stats/sample.json
```

The private source manifest is `{"roots":{"claude":["/path/projects"],
"codex":["/path/sessions"],"muse":["/path/sessions"]},"zip_roots":["/path/archives"]}`.
Add `--claude DIR`, `--codex DIR` or `--muse DIR` for more roots. `--auto` also
considers provider environment variables, local Claude usage archives, default
AgentSessions backups and the mounted LaCie archive. Custom/older backup layouts
need explicit roots. Absent defaults are recorded in private coverage; a successful
exit cannot prove an unconfigured location was scanned. ZIPs are streamed without
extraction. Inode/content copies and provider call identities are deduplicated;
updated partial usage records retain their maximum logged token counts.

`stats.json` contains numeric aggregates/model labels, no transcripts, paths or
native session IDs. Optional `--csv .temp/session-stats/calls.csv` contains per-call
numbers and salted context identifiers; keep it local unless specifically requested.
**Coverage is private**: it contains root paths, source counts and salted references.
Exit 2/`partial` marks parse/read errors, intentional filtering or an empty corpus;
inspect coverage, missing roots and provider counts before claiming completeness.
Every input is bounded to its length at open, not an atomic cross-session snapshot.
Runtime depends on bytes and archive compression; full historical inventories can
take tens of minutes. There is no `--since` filter.

Per provider and for `all`, `call_time` reports:

| Field | Meaning |
|---|---|
| `first_utc`, `last_utc` | Earliest/latest retained valid usage-event time; null without time coverage |
| `distinct_utc_days` | UTC dates containing retained calls, not the calendar span; `all` is a set union |
| `timestamped_calls` | Deduplicated, min-call-filtered calls with valid time |
| `missing_timestamp_calls` | No supplied timestamp on any copy and no valid time |
| `invalid_timestamp_calls` | Supplied invalid time and no valid copy; includes bool, nonfinite and unrepresentable UTC dates |
| `conflicting_timestamp_calls` | Unique calls with differing valid projection timestamps; never extra calls/days |
| `status` | `no_calls`, `no_timestamped_calls`, `partial` (missing/invalid/conflicting), or `complete` |

Time coverage is separate from source-reading status. Claude/Codex use the usage
envelope `timestamp`; Muse uses runtime.session `recorded_at`. These are event
logging times, not evidence of exact inference start. Naive ISO timestamps assume
UTC; positive numeric values retain the prior seconds/ms/us/ns magnitude heuristic.
The first valid time in discovery/reader order is retained. A later duplicate can
fill missing/invalid time; other valid times flag a conflict, without extending the
date range. File names, backup labels and mtimes never supply call dates.

`new_in` estimates context growth after previous output; it is **not** billed
uncached input or measured prefill traffic. Muse input/cache fields remain unchanged
and their cache semantics are unverified. Reasoning is not added to output. Tool
sizes use a character heuristic. Model labels are logged metadata, not attested IDs.

### Executable checks

```bash
swift test --package-path tools/tests --scratch-path .temp/session-stats-build
# Expected red control: the six date tests must fail on the frozen pre-feature source.
SESSION_STATS_TEST_SCRIPT="$PWD/data/measurements/ivmbp-2026-10-30/agent_session_stats.py" \
  swift test --package-path tools/tests --scratch-path .temp/session-stats-build --filter CallTimeTests
```

Swift 6/Swift Testing and Python 3 standard library are required for these checks.
Fixtures stay under `.temp/session-stats-tests/`, never touch real user data, and
exercise the ten retained backup/dedup/privacy groups plus date normalization,
invalid/missing times, duplicate conflicts/fill, all three readers, UTC set union,
min-call filtering and absent mtime fallback. A passing synthetic fixture does not
establish source completeness for a real machine.

## 2. `hybrid_bench.py`: prefill and decode at long context

Measures four things on a local server:
- the marginal prefill rate of each depth segment, from 16k to 260k;
- the prefill of a fresh turn delta of 512, 2k or 10k tokens on top of a cached context;
- the decode rate at each depth;
- optionally, the aggregate decode rate of K parallel streams and the size of a saved KV slot.

Every request strictly extends what the server already holds, generated tokens included.
This matters for hybrid DeltaNet models, whose recurrent state cannot be rolled back: a
diverging prompt would force a full re-prefill. The script stops measuring turn deltas if
it detects that.

Prompts are synthetic generated text.

It supports three APIs:
- `--api llama` (default): llama.cpp `llama-server`. It gives exact token counts and
  server-side timings.
- `--api openai`: any OpenAI-compatible streaming server with `/v1/completions`, such as
  mlx_lm.server, LM Studio, oMLX or vllm-metal. Here time to first token is measured on
  the client.
- `--api chat`: servers that offer only `/v1/chat/completions`, such as Strata. The session
  is a growing message list, and every reply is appended verbatim. Thinking is turned off
  (`enable_thinking=false`) so that the history stays identical to what the server cached;
  `--thinking` leaves it on. When the server sends llama.cpp-style `timings` (Strata does),
  prefill and decode rates are the server's own.

### Suggested overnight plan (M3 Max 128 GB)

1. Smoke test first (about 2 minutes per model):
   `python3 hybrid_bench.py --label smoke --smoke`.
2. Qwen3.8-27B, one slot, 8-bit KV (about 2 h):
   ```bash
   llama-server -m <Qwen3.8-27B-Q4_K_M.gguf> -c 300000 -np 1 -fa on -ctk q8_0 -ctv q8_0 \
     --port 8080 --slot-save-path /tmp/hybrid-bench-slots
   python3 hybrid_bench.py --label q27b-q4km-q8kv --notes "Q4_K_M, fa on, q8_0 KV" --slot-save
   ```
   Then remove `/tmp/hybrid-bench-slots`; at 260k each slot file is several GB.
3. The same with the KV type you use day to day, if it differs (for example the default
   f16): `--label q27b-q4km-f16kv`.
4. Parallel decode, 4 streams at 32k (about 15 min). Restart the server with
   `-np 4 -c 140000`, then run:
   `python3 hybrid_bench.py --label q27b-par4 --only-parallel --parallel 4 --parallel-depth 32k`
5. Flash-Next, 3-bit, in Strata (about 1 h):
   - Start the model with a long context. Strata's Mac setup takes `--context N`; the model
     allows 262,144 tokens, Strata itself has measured the Mac engine only up to 32K. If only
     128k can be set, use `--depths 16k,50k,100k`.
   - Strata serves the OpenAI chat API on `http://127.0.0.1:8080/v1`, one request at a time
     (no parallel slots on the Mac), so there is no parallel test here:
     ```bash
     python3 hybrid_bench.py --api chat --url http://127.0.0.1:8080 --label flash-iq3-strata \
       --notes "Strata <version>, <pack, e.g. IQ3_S>, context <N>" --depths 16k,50k,100k,150k,200k
     ```
   - If the summary marks deltas "(full re-prefill)", Strata did not reuse the cached
     prefix. Send the files anyway: that is a result too.
   - Flash-Next in llama-server or MLX instead: the commands of steps 2 and 4 with the Flash
     model, or `--api openai` for a server with `/v1/completions`.

Defaults: depths `16k,50k,100k,150k,200k,260k`, deltas `512,2k,10k`, 128 decoded tokens
per delta. Change them with `--depths` and `--deltas`. Each depth adds about 13k tokens
of drift from the deltas, so the recorded depth is the real one.

Send back `hybrid-bench-*.jsonl` and `hybrid-bench-*.md`. The JSONL holds the model file
name (basename only), llama.cpp build, chip and RAM size, and the numbers.

### What the numbers feed

- Segment prefill rates give the curve P(L): local prefill speed at each depth. The study
  currently interpolates it from two points.
- Delta prefill at depth is the per-turn cost that the hybrid offloads.
- Decode at depth and the parallel gain give how many agents a device can carry.
- Slot bytes per token give the real transfer size of KV plus recurrent state in llama.cpp's
  format.

## Checks done before release

Both scripts were run on agents1 (Linux, Python 3.12):

- `agent_session_stats.py` ran on 638 local session files: Claude Code, Codex and Muse.
- `hybrid_bench.py` ran against a mock llama-server and a mock OpenAI endpoint with three
  behaviours:
  - prefix reuse: the deltas are processed exactly;
  - recurrent state without checkpoints: the append-only flow still reuses the prefix;
  - no reuse: the script warns and skips deltas.

- Version 1.1 added `--api chat`. It ran against a mock chat server in four modes:
  - prefix reuse: segments and deltas are measured from the server's timings;
  - a template that drops thinking from the history, on a server that cannot roll back
    recurrent state: the script detects the full re-prefill and skips the deltas;
  - the same server with thinking off: the deltas are measured again;
  - no reuse at all, and no server timings: detected, or measured from usage and client time.

  Neither mode has yet run against a real llama-server or Strata.
