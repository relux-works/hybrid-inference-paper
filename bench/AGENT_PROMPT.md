# Task: collect measurements for the hybrid-inference paper on this machine

You are an agent helping the owner of this machine contribute data to the paper "Hybrid Inference with
Client–Server Prefill–Decode Disaggregation" (repository `relux-works/hybrid-inference-paper`). In the hybrid scheme a
GPU server reads the long context of an agent session (prefill) and the user's machine, such as a Mac, generates
(decode). The paper needs three kinds of data:

1. **Client measurements.** Long-context prefill and decode of Qwen3.8-27B in llama.cpp on Apple Silicon Macs:
   how fast a Mac reads context at each depth, how fast it generates there, and how many agents it can carry.
2. **Server measurements.** The same benchmark on NVIDIA GPUs (RTX 3090 to RTX 5090, RTX PRO 6000, data-centre
   cards): how fast a card reads context, which sets the server side of the economics.
3. **Agent-session statistics**, with the owner's consent: the shape of real agent calls (context depth, new tokens
   per call, output, tool-result sizes), computed locally. Sessions themselves never leave the machine.

A fourth kind, end-to-end hybrid runs through the project's own client against a prefill node the project
provides, comes later with its own instructions (see the last section).

## Rules for every track
1. **Consent first.** Before each track, tell the owner what it does, how long it takes, how much disk and
   network it uses and what file it produces, and get an explicit yes. Session statistics need their own yes.
2. **Nothing leaves the machine through you.** You never upload, post or send files. You hand the owner the result
   archives; the owner decides whether to send them.
3. **No sudo, no system changes, no installs without the owner's yes.** Give exact commands and wait.
4. **Processes.** Only the kits' own servers, stopped by their recorded PIDs. Never kill by name or pattern.
5. **Files.** The kits write only inside their own `work/` and `results/` folders and the result archive in the kit
   folder. Ask before deleting anything else.
6. **Honesty.** Do not edit the kits' scripts or pinned tools. Never invent, adjust or "clean up" numbers. Report
   errors, skipped steps and anything unusual.

The kits' long steps run for an hour or more: start them detached as each kit's prompt explains (section "Long
steps"), never in the foreground of a shell with a timeout.

## Step 1: what this machine can do
Run `uname -s; uname -m` and, on Linux, `nvidia-smi -L`.
- macOS on arm64 (Apple Silicon) with 48 GB or more: the Mac track.
- Linux with an NVIDIA GPU: the GPU track. On a machine with several GPUs, ask the owner which one to use.
- Anything else: only the session statistics, if the owner uses Claude Code, Codex or Muse here.

Tell the owner which tracks apply, with the time each takes, and ask which to run.

## Step 2: the Mac track
Follow `bench/mac/AGENT_PROMPT.md` from inside `bench/mac`. About 3–5 hours on an idle Mac on AC power, about 55 GB
of disk for the base run; with GPU imports allow about 73 GB for 260k alone, or 136 GB for both 260k/1M
(55 GB baseline + 9/45 GB imports + 9/36 GB restream copy). Result: `bench/mac/qwen27b-mac-bench-results-<UTC>.tar.gz`.

The Mac kit is 1.4.0; steps 56/57 restream one-stream GPU imports into temporary copies for
multi-stream servers, check disk first and retain the originals (see the kit prompt).

## Step 3: the GPU track
Follow `bench/gpu/AGENT_PROMPT.md` from inside `bench/gpu`. Usually 1–2 hours, about 55 GB of disk, and the CUDA
toolkit for the build. Result: `bench/gpu/qwen27b-gpu-bench-results-<UTC>.tar.gz`.

GPU kit 1.2.1 still generates one-stream slot files in step 60; the Mac kit handles stream conversion.

## Step 4: session statistics (only with the owner's explicit yes)
1. Explain from `bench/sessions/README.md` what the step reads and what it writes. Make clear that the logs are
   read locally and that only aggregate numbers go into the file.
2. If the owner agrees, run `CONSENT=yes bash bench/sessions/run.sh` from the repository root.
3. Show the owner the resulting `bench/sessions/results/session-stats-<UTC>.json`, or at least its top-level fields
   and the model list, and let them decide whether to send it.

## Step 5: report
Give the owner:
- the paths of the result archives and of the session-statistics file;
- the key numbers from each kit's summaries (each kit's prompt lists them) and how they compare with the Mac
  reference run in `bench/mac/reference/m3max-128gb.md`;
- every error, skipped step, retry or warning;
- the reminder to send the files to the person who asked them to run the kits (for this paper, Ivan Oparin).

## Later: end-to-end hybrid runs
When the project gives the owner the address of a prefill node, the hybrid benchmark runs through the project's
client: the node reads the context on its GPU, this machine generates. Its tools and instructions live in the
prototype repository `relux-works/hybrid-inference`, under `tools/hybrid-bench/`. Do not improvise this track: if those
instructions are not there yet, tell the owner and stop.
