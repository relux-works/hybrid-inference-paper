# Task: benchmark Qwen3.8-27B at long context on this NVIDIA GPU

You are running a measurement kit on a Linux machine with an NVIDIA GPU. The goal is to repeat on this card the
long-context prefill and decode measurement that was made on an Apple M3 Max with 128 GB for a paper on hybrid
inference, where a GPU server reads the context and a client generates. Everything stays the same as in that run:
the llama.cpp commit, the model file, the server flags and the benchmark script. Only the backend is CUDA instead of
Metal. Then you pack the results for the owner to send back.

Work only inside this kit directory. Run the provided scripts in order and read their output. Report problems
honestly. Never invent, adjust or "clean up" numbers.

## Rules
1. **No sudo, no changes to system settings, no installs without the owner's explicit yes.** If a tool is missing,
   give the owner the exact command and wait.
2. **Network.** Contact only github.com (llama.cpp sources) and Hugging Face for the model: huggingface.co and its download
   hosts (`*.huggingface.co`, `*.hf.co`). Upload nothing.
3. **Processes.**
   - The scripts start one `llama-server` at a time, bound to 127.0.0.1, record its PID in `work/server.pid` and
     stop only that process, after checking that it runs the kit's own binary.
   - Never kill other processes and never kill by name or pattern. If other processes use the GPU, tell the owner;
     do not stop them yourself.
   - If port 8080 is busy, ask the owner or rerun the step with `PORT=8091`.
4. **GPU.** The kit uses one GPU, index 0 by default. On a multi-GPU machine ask the owner which one to use and set
   `GPU_INDEX=<n>` for every step.
5. **Files.**
   - Write only under `work/` and `results/`.
   - The depth and scaling steps delete their own slot files.
   - Ask before deleting anything else, the downloaded model included.
6. **Do not edit the scripts in `tools/`.** The SHA-256 of `tools/hybrid_bench.py` is pinned so that the results
   compare with the reference run, and the scripts refuse to run a modified copy. Edit nothing else either.

## Steps
0. `bash scripts/00-check.sh`: checks the GPU, the driver, the CUDA toolkit, the tools and the disk, and writes
   `results/system.json`. It also prints the largest context that fits on this card next to the model. If it reports
   a problem, stop and tell the owner what to fix.
1. `bash scripts/10-build-llama.sh`: clones llama.cpp, checks out commit `c21284cdf5fd833b90ac1f824cdf8065e2700dc4`
   (build 11087, as in the reference run) and builds `llama-server` with CUDA for this GPU's architecture. About
   5–15 minutes.
2. `bash scripts/20-fetch-model.sh`: downloads `Qwen3.8-27B-Q4_K_M.gguf` from `ggml-org/Qwen3.8-27B-GGUF` at the
   pinned revision (18,973,870,432 bytes) and verifies its SHA-256. If the owner already has this exact file, run
   `MODEL_PATH=/path/to/Qwen3.8-27B-Q4_K_M.gguf bash scripts/20-fetch-model.sh` and keep the same `MODEL_PATH` for
   the later steps.
3. `bash scripts/30-run-smoke.sh`: a smoke test of about two minutes. Read the `results/hybrid-bench-*smoke*.md`
   summary before going on.
4. `bash scripts/40-run-depth.sh`: the main run.
   - One slot. The context is 262,144 tokens when the card fits it (32 GB and up), otherwise the largest that fits
     (about 95–100k on a headless 24 GB card; step 0 prints the exact value). The depths are 16k, 50k, 100k, 150k and
     200k where they fit, then the deepest level that fits: 249k at full context, as in the reference run, about 85k
     on a 24 GB card.
   - If the server cannot allocate the context, the step tries again with 16k less: four attempts in all. If even
     that fails, ask the owner before rerunning with a larger `RESERVE_MIB` (default 2560).
   - Turn deltas of 512, 2k and 10k tokens at each depth, each followed by 128 decoded tokens. Slot save/restore
     runs when 35 GB are free at this point.
   - Usually 20–60 minutes on a recent GPU.
5. `bash scripts/50-run-parallel.sh`: parallel decode at 32k, four streams as in the reference (two on a 24 GB card).
   A few minutes. If neither fits, the step skips itself and says so. `SKIP_PARALLEL=1` skips it.
6. `bash scripts/55-run-scaling.sh`: how total decode speed grows with the number of parallel agents at 64k, 128k
   and 260k. The stream counts (up to 32 at 64k, 16 at 128k and 8 at 260k) are those that fit in this card's memory;
   if the server
   still cannot start with the largest, the step drops it and tries again. Each round
   reports `restore_reused`; if it is false, that round's numbers are not valid, so tell the owner. `SKIP_SCALING=1`
   skips the step.
6c. `bash scripts/57-run-agents.sh`: realistic agent sessions on the GPU, as on a server that runs all calls: sessions
   start at 128k and go through four turns of a tool result and an answer with sizes from the measured call mix, all at
   once; 1, 2, 4, 8 and 16 sessions as far as the card's memory allows. The start context comes from
   `work/slots-import/parallel-depth-131072.bin` if present, otherwise it is filled here. If a round reports re-reads,
   tell the owner. `SKIP_AGENTS=1` skips it.
7. `bash scripts/90-collect.sh`: writes the archive `qwen27b-gpu-bench-results-<UTC>.tar.gz` in the kit directory.
   It packs a scrubbed copy: the kit, work, model, results and home folders, the user name and the host name are
   replaced by placeholders. If it lists paths it could not scrub, show the list to the owner. If the owner confirms
   that the listed paths hold nothing personal, rerun with them allowed:
   `SCRUB_ALLOW='/first/path,/second/path' bash scripts/90-collect.sh`. Do not edit the result files yourself.

8. Optional, `bash scripts/60-make-slots.sh`: slot files for Macs, so that a Mac can measure 260k and 1M contexts
   without filling them itself. Files made below carry one stream (`-np 1`); Mac kit 1.4.0 validates and restreams
   them for its server count without modifying the import. Compare the import SHA-256 with this GPU log;
   the Mac also logs the copy SHA-256. It fills one session to 260,000 and to 1,040,000 tokens (the latter with YaRN rope
   scaling) and saves `work/slots-export/parallel-depth-260000.bin` (about 9 GB) and `parallel-depth-1040000.bin`
   (about 36 GB), logging their sizes and SHA-256 in `results/kit.log`. Needs the disk for them;
   `SLOT_DEPTHS="260000"` limits the depths, and `SLOT_DEPTHS="131072 260000 1040000"` also makes the 128k start
   context of the Mac's step 6c. Tell the owner where the files are; the Mac side copies them with scp
   through the same SSH access, for example
   `scp -P <port> <user>@<host>:<kit>/work/slots-export/parallel-depth-260000.bin <mac kit>/work/slots-import/`, and
   checks the SHA-256 against the log. Both machines must use the same model file, the same llama.cpp commit (CUDA on one side, Metal on the other), the
   q8_0 KV cache with flash attention, and the same rope settings; the kits pin all of these, so leave
   `LLAMA_COMMIT`, `MODEL_PATH` and the server flags at their defaults on both sides. Step 8 runs after the archive of
   step 7: run `scripts/90-collect.sh` again if its records should be packed too.

`bash scripts/run-all.sh` runs steps 0–7 in order and stops at the first failure. If a step fails, fix the cause
with the owner and rerun from that step. The finished steps do not need to run again.

## Long steps
Steps 4, 5 and 6, and `run-all.sh`, run longer than the command timeout of most agent shells. Start them detached and
follow their progress:
```bash
nohup bash scripts/40-run-depth.sh > work/step-40.out 2>&1 &
echo $!          # the step's own PID; keep it
tail -n 20 results/kit.log work/step-40.out
```
Your environment's own background facility works too. Do not wait on the step in the foreground. Run one step at a
time: a step refuses to start while another step of the kit is running and names its PID. To stop a step, send it a
plain `kill <pid>` (SIGTERM) with the step's own PID, or with the PID of `run-all.sh`, which passes it on; the step
stops its benchmark and its server within seconds and frees the lock (steps 1 and 2 first finish a running git or
checksum command, and a compile started by cmake may run on for a minute: do not restart step 1 until it has ended).
Never use
`kill -9` or kill by name: a step killed that way cannot stop its server. (`kill -INT` does not reach a step started
with `nohup ... &`.) A server left over from an interrupted run is recognised by its binary path and stopped at the
next start; any other process is never touched. The kit itself force-stops only its own server, by the PID it
recorded and after checking its command line, if that server ignores a normal stop for 60 seconds; that is not the
`kill -9` the agent must avoid.

If a step fails, read the end of its output and `results/kit.log`. Steps 5 and 6 skip what does not fit and go on.
After a failure in step 4 you can still pack the results so far with `bash scripts/90-collect.sh`; say in the report
which steps are missing.

## Report to the owner
When everything is done, give the owner:
- the archive path and the instruction to send it to the person who asked them to run the kit;
- a short table from the `results/hybrid-bench-*.md` summaries: the marginal prefill rate, the turn prefill rates
  and the decode rate at each depth;
- the parallel and scaling results;
- a comparison with the Mac reference run, `../mac/reference/m3max-128gb.md`;
- anything unusual: errors, skipped depths or steps, retries with a smaller context, other processes on the GPU,
  thermal or power throttling (`nvidia-smi -q -d PERFORMANCE`), a different llama.cpp build or model hash.
