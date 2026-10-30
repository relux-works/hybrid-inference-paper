# Hybrid-inference measurement tools

Two standalone scripts for the hybrid-inference study (server prefill, client decode).
Both need only Python 3.8+ and its standard library. Neither sends data anywhere: the
session script reads local logs, the benchmark talks only to a local inference server.
Both write their results to the current directory.

## 1. `agent_session_stats.py`: what agent turns look like

Reads Claude Code, Codex CLI and Muse session logs. It reports the distribution of four
things per model call: context depth, new input tokens since the previous call (tool
output, user text), output tokens, and the time between calls. It also reports tool
result sizes. Only numbers are written. There is no text, no paths and no project names,
and the per-call CSV carries salted hashes instead of session ids.

```bash
python3 agent_session_stats.py --auto --out stats.json --csv calls.csv
# a sample instead of everything, recent sessions only:
python3 agent_session_stats.py --auto --sample 500 --since 2026-06-01 --out stats.json
```

`--auto` scans these locations:

| Agent | Locations |
|---|---|
| Claude Code | `~/.claude/projects` and `$CLAUDE_CONFIG_DIR/projects` |
| Codex | `~/.codex/sessions` and `$CODEX_HOME/sessions` |
| Muse | `~/.local/share/muse/sessions` and `~/Library/Application Support/muse/sessions` |
| All three | the Curator homes `~/.curator/environments/*` |

Add `--claude DIR`, `--codex DIR` or `--muse DIR` for other places.

Runtime: about 15 s per 600 MB of logs.

Send back `stats.json`. `calls.csv` is optional: it holds per-call numbers and model names
only.

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
