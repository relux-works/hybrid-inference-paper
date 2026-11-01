# Measurement kits

Kits for contributing data to the paper. Each kit is self-contained, needs no sudo, sends nothing anywhere and writes
only inside its own folder. To run them through an agent (Claude Code, Codex or another), open the repository in it
and ask: "Do the task in bench/AGENT_PROMPT.md". The agent checks the machine, asks before each step, runs the kits
and hands you the result files to send.

| Kit | Machine | What it measures | Time | Result |
|---|---|---|---|---|
| [`mac/`](mac/) | Apple Silicon Mac, 48 GB or more | Qwen3.8-27B prefill and decode by context depth up to 249k; parallel agents at 32k–1M; realistic agent sessions | 4–9 h | `qwen27b-mac-bench-results-*.tar.gz` |
| [`gpu/`](gpu/) | Linux with an NVIDIA GPU, 24 GB or more | The same benchmark on the GPU, context sized to the card; parallel and realistic agent sessions; slot files for Macs | 2–3 h | `qwen27b-gpu-bench-results-*.tar.gz` |
| [`sessions/`](sessions/) | Any machine with Claude Code, Codex or Muse logs | Aggregate statistics of agent calls, only with your consent | minutes | `session-stats-*.json` |

The Mac and GPU kits use the same llama.cpp commit (build 11087), the same model file (`Qwen3.8-27B-Q4_K_M.gguf`,
pinned revision and SHA-256), the same server flags and the same pinned benchmark script as the reference run on an
Apple M3 Max with 128 GB (`mac/reference/m3max-128gb.md`), so every result compares directly with it.

The archives hold the numbers, the server logs and the machine's hardware and software versions. They hold no host
name, user name, serial number or files from the disk; the benchmark prompts are generated text.

End-to-end hybrid runs (a GPU prefill node reading the context, a client generating) use the prototype's own client and
live in the prototype repository, `relux-works/hybrid-inference`, under `tools/hybrid-bench/`.

Mac kit 1.4.0 restreams the one-stream exports from GPU kit 1.2.1 for multi-stream servers,
using temporary copies with disk checks and cleanup. See the Mac README for format limits and commands.
Allow about 73 GB total for the base Mac run with a 260k import and its copy, or 136 GB with both 260k/1M imports and the largest copy; disk exhaustion falls back to one stream reading the import directly.

Tests of the kits' shared helper (`*/scripts/kitlib.py`: the depth ladder, the record check, the scrubbing of result
archives, strict slot parsing, power parsing and Mac import control flow): `python3 -m unittest discover -s bench/tests` from the repository root.

CPU integration (explicit, separate from unit tests; use an already built c21284cd CPU server and a local hybrid model):
`python3 bench/tests/check_restream_cpu.py --server /path/to/llama-server --model /path/to/Qwen3.5-0.8B-Q4_0.gguf --out .temp/restream-cpu`.
It writes HTTP evidence, server logs, PID records and `result.json`, requires 25 GiB free,
and stops only its own servers by PID. It performs no build, download or GPU use.
