# Qwen3.8-27B long-context benchmark on an NVIDIA GPU

This kit repeats on an NVIDIA GPU the measurement made on an Apple M3 Max with 128 GB for the paper: prefill and
decode of Qwen3.8-27B at context depths up to 249k tokens in llama.cpp. The llama.cpp commit (build 11087), the model
file, the server flags (all layers on the GPU, flash attention, KV cache q8_0) and the benchmark script are the same
as in the Mac kit, so GPU and Mac results compare directly.

## Requirements
- Linux with an NVIDIA GPU of 24 GB or more and its driver (`nvidia-smi`).
- The CUDA toolkit (`nvcc`) for the build; 12.8 or newer for Blackwell cards (RTX 50xx, RTX PRO 6000, B200).
- git, cmake, a C++ compiler, curl, python3 3.8 or newer.
- About 55 GB of free disk: the model takes 19 GB and the build about 1 GB, and the depth step keeps the saved slot
  of every level, up to about 28 GB in all. With less, the depth step skips slot save/restore; 25 GB is the minimum.

## How much context fits
The 19 GB model leaves room for the cache: 34,816 bytes per token in q8_0 plus a 157 MB recurrent state per slot.
The kit computes the largest context from the free GPU memory, keeping 2.5 GB in reserve (`RESERVE_MIB`). The
table is for a card that drives no display; a display takes about 1 GB, and the value step 0 prints is the one that
counts:

| Card memory | One slot | Parallel at 32k | Streams at 64k / 128k / 260k |
|---|---|---|---|
| 24 GB (RTX 3090, 4090) | about 95k | 2 | 1 / none / none |
| 32 GB (RTX 5090) | 262k | 4 | up to 4 / up to 2 / 1 |
| 96 GB (RTX PRO 6000) | 262k | 4 | up to 32 / up to 16 / up to 8 |

If the server still cannot allocate the context, the depth step tries again with 16k less, four attempts in all. The
parallel step falls back from four slots to two and skips itself if neither fits; the scaling step drops the largest
stream count until the server starts.

## How to run
Through an agent: open this folder in your agent and ask it to do the task in `AGENT_PROMPT.md`.

By hand: `bash scripts/run-all.sh`, or the steps one by one (`00-check` to `90-collect`). `GPU_INDEX=<n>` selects
the GPU on a multi-GPU machine; `PORT=<p>` moves the server off port 8080; `MODEL_PATH=<file>` reuses a downloaded
copy of the model.

## What to send
The archive `qwen27b-gpu-bench-results-*.tar.gz` from this folder, to the person who asked you to run the kit. It
holds the numbers, the server logs, the llama.cpp and model versions, and the GPU, driver, CUDA, CPU, RAM and OS
versions. It holds no host name, user name, IP address or serial number.

## How to stop
Ctrl-C. The scripts stop only their own llama-server, by its recorded PID. Everything the kit creates is inside this
folder, in `work/` and `results/`.

## Slot files for Macs (kit 1.2.1)

`SLOT_DEPTHS="131072 260000 1040000" bash scripts/60-make-slots.sh` writes
`work/slots-export/parallel-depth-<depth>.bin` and logs each SHA-256. Files carry
one stream (`-np 1`). Mac kit 1.4.0 steps 56/57 validate and restream a temporary
copy for their server's stream count, preserve the original, and log both hashes.
GPU measurement and slot-generation behavior is unchanged in 1.2.1.

## Tools

| Tool | Command | Output |
|---|---|---|
| Kit steps (bash, Python 3, git, cmake, CUDA, curl, shasum) | `bash scripts/run-all.sh` | `work/`, `results/` and result archive |
| GPU slot generation | `SLOT_DEPTHS="131072 260000" bash scripts/60-make-slots.sh` | One-stream files in `work/slots-export/` |
| Shared Python helper | `python3 scripts/kitlib.py --help` | Command help; restream support is used by the Mac kit |
