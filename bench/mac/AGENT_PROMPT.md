# Task: benchmark Qwen3.8-27B at long context on this Mac

You are running a measurement kit on the user's Mac. The goal is to repeat on this machine a long-context prefill
and decode measurement that was made on an Apple M3 Max with 128 GB for a paper on hybrid inference. Everything
stays the same as in that run: the llama.cpp commit, the model file, the server flags and the benchmark script.
Then you pack the results for the user to send back.

Work only inside this kit directory. Run the provided scripts in order and read their output. Report problems
honestly. Never invent, adjust or "clean up" numbers.

## Rules
1. **No sudo, no changes to system settings, no installs without the user's explicit yes.** If a tool is missing,
   give the user the exact command (for example `xcode-select --install` or `brew install cmake`) and wait.
2. **Network.** Contact only github.com (llama.cpp sources) and Hugging Face for the model: huggingface.co and its download
   hosts (`*.huggingface.co`, `*.hf.co`). Upload nothing.
3. **Processes.**
   - The scripts start one `llama-server` at a time, record its PID in `work/server.pid` and stop only that process,
     after checking that it runs the kit's own binary.
   - Never kill other processes and never kill by name or pattern.
   - If port 8080 is busy, ask the user or rerun the step with `PORT=8091`.
4. **Files.**
   - Write only under `work/` and `results/`.
   - The depth step deletes its own slot files.
   - Ask before deleting anything else, the downloaded model included.
5. **Do not edit the scripts in `tools/`.** The SHA-256 of `tools/hybrid_bench.py` is pinned so that the results
   compare with the reference run, and the scripts refuse to run a modified copy. Edit nothing else either.
6. **Conditions.**
   - Keep the Mac on AC power and awake; the scripts use `caffeinate`.
   - Keep other heavy work off the machine while measuring.
   - Tell the user before each long step and how long it should take.

## Steps
0. `bash scripts/00-check.sh`: checks the machine, tools, disk and power and writes `results/system.json`. If it
   reports a problem, stop and tell the user what to fix. It reads both legacy `lowpowermode` and macOS 26+
   `powermode`, records `low_power_mode` 0 or 1 only from a known value, records null with status "unknown"
   otherwise, and warns in `results/kit.log` when it is on or unknown; tell the owner about either warning.
1. `bash scripts/10-build-llama.sh`: clones llama.cpp, checks out commit `c21284cdf5fd833b90ac1f824cdf8065e2700dc4`
   (build 11087, as in the reference run) and builds `llama-server` with Metal. About 5–10 minutes.
2. `bash scripts/20-fetch-model.sh`: downloads `Qwen3.8-27B-Q4_K_M.gguf` from `ggml-org/Qwen3.8-27B-GGUF` at the
   pinned revision (18,973,870,432 bytes) and verifies its SHA-256. If the user already has this exact file, run
   `MODEL_PATH=/path/to/Qwen3.8-27B-Q4_K_M.gguf bash scripts/20-fetch-model.sh`, keep the same `MODEL_PATH` for the
   later steps, and the script only verifies the file.
3. `bash scripts/30-run-smoke.sh`: a smoke test of about two minutes. Read the `results/hybrid-bench-*smoke*.md`
   summary before going on.
4. `bash scripts/40-run-depth.sh`: the main run, usually one to three hours.
   - One slot with context 262,144.
   - Depths 16k, 50k, 100k, 150k, 200k and 249k, as in the reference run, and turn deltas of 512, 2k and 10k tokens,
     each followed by 128 decoded tokens.
   - Slot save/restore runs when the disk has room.
5. `bash scripts/50-run-parallel.sh`: four parallel streams at 32k with the reference settings (`-np 4 -c 140000`),
   about 20 minutes.
6. `bash scripts/55-run-scaling.sh`: how total decode speed grows with the number of parallel agents at realistic
   depths. This step is new and not in the reference.
   - `tools/parallel_depth.py` fills one slot to the depth once, saves it and restores it into every stream, so
     several streams cost one prefill.
   - With 64 GB it runs 1, 2, 4 and 8 streams at 64k, then 1, 2 and 4 streams at 128k. With 96 GB or more it runs
     up to 16 streams at 64k and up to 8 at 128k.
   - About 40–60 minutes.
   - Each round reports `restore_reused`. If it is false, the server re-read the whole context, and that round's
     numbers are not valid. Tell the user.
   - Skip the step with `SKIP_SCALING=1` if the user is short of time.
6b. `bash scripts/56-run-maxctx.sh`: total decode speed of several sessions at the longest contexts this Mac holds:
   260k (nearly the full native context) and 1M (with YaRN rope scaling).
   - Stream counts 1, 2, 4, 6 and 8, as far as they fit in about three quarters of the memory next to the model (about
     8 at 260k and 2 at 1M on 128 GB, 2 at 260k on 64 GB; 1M does not fit in 64 GB). If the server cannot start, the
     largest count is dropped.
   - The long fill can come from a GPU: the GPU kit's step 8 makes `parallel-depth-260000.bin` and
     `parallel-depth-1040000.bin` (about 9 GB and 36 GB). Ask the owner to copy them into `work/slots-import/` of this
     kit, or set `SLOT_FROM=<folder with the files>`. The step logs each file's SHA-256: compare it with the GPU's log.
     GPU files carry one stream. For `-np > 1` the Mac validates and restreams a copy in
     `work/slots-restream/step-*/`, uses it as the server slot directory, and logs its SHA-256 as well.
     Allow free disk equal to the import plus `4 * (np - 1)` bytes and 1 MiB headroom; otherwise it logs a fallback
     to one stream using the import directly. Budget about 73 GB with 260k alone, or 136 GB with both imports:
     the 55 GB baseline plus 9/45 GB of imports and 9/36 GB for the largest temporary copy.
     A fallback regenerates the copy for the new stream count. It is removed on exit, failure and handled signals;
     the original stays unchanged. `-np 1` uses the import directly.
     Both machines must use the same model file, the same llama.cpp commit (CUDA on one side, Metal on the other), the
     q8_0 KV cache with flash attention, and the same rope settings; the kits pin all of these, so leave
     `LLAMA_COMMIT`, `MODEL_PATH` and the server flags at their defaults on both sides.
   - Without a file the Mac fills 260k itself (about two hours on an M3 Max) and skips 1M (about a day).
   - `MAXCTX_DEPTHS="260000"` limits the depths; `SKIP_MAXCTX=1` skips the step.
6c. `bash scripts/57-run-agents.sh`: realistic agent sessions. Sessions start at 128k (about the median depth of the
   measured calls) and each goes through four turns of a tool result and an answer, with sizes drawn from the measured
   call mix; all run at once, so one session's tool result is read while the others generate. Session counts 1, 2, 4
   and 8 as far as memory allows. The start context comes from `work/slots-import/parallel-depth-131072.bin` if the
   GPU made one (GPU kit step 8 with `SLOT_DEPTHS="131072 260000 1040000"`), otherwise the Mac fills it (about 35
   minutes on an M3 Max). The same restream/disk/cleanup rules as step 6b apply, including `SLOT_FROM`.
   Reports per call the prefill and decode rates and the call time; the other sessions' load
   shows as slower rates and longer calls. If a round reports re-reads, tell the owner: the start context did not
   match the prompts. About one to one and a half hours. `SKIP_AGENTS=1` skips it.
7. `bash scripts/90-collect.sh`: writes the archive `qwen27b-mac-bench-results-<UTC>.tar.gz` in the kit directory.
   It packs a scrubbed copy: the kit, work, model, results and home folders, the user name and the host name are
   replaced by placeholders. If it lists paths it could not scrub, show the list to the owner. If the owner confirms
   that the listed paths hold nothing personal, rerun with them allowed:
   `SCRUB_ALLOW='/first/path,/second/path' bash scripts/90-collect.sh`. Do not edit the result files yourself.

`bash scripts/run-all.sh` runs steps 0–7 (6b and 6c included) in order and stops at the first failure. If a step fails, fix the cause
with the user and rerun from that step. The finished steps do not need to run again.

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
stops its benchmark and its server within seconds and frees the lock (steps 1, 2 and 6b first finish a running git or
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

## Report to the user
When everything is done, give the user:
- the archive path and the instruction to send it to the person who asked them to run the kit;
- a short table from the `results/hybrid-bench-*.md` summaries:
  - the marginal prefill rate and the decode rate at each depth;
  - the 4-stream aggregate decode and its gain over one stream;
  - the 64k and 128k scaling tables from `results/parallel-depth-*.md`, if that step ran;
- a comparison with `reference/m3max-128gb.md`;
- anything unusual: errors, skipped steps, signs of thermal throttling, other load on the machine, a different
  llama.cpp build or model hash.

## Optional, only if the user asks
- **Power.** The user may run `sudo powermetrics --samplers cpu_power,gpu_power -i 1000 -o results/powermetrics.txt`
  in a separate terminal during steps 4–6 and stop it afterwards. You never run sudo yourself.
- **A newer llama.cpp.**
  - Rebuild with `LLAMA_COMMIT=<newer commit> WORK=$PWD/work/latest RESULTS=$PWD/work/results-latest
    MODEL_PATH=$PWD/work/models/Qwen3.8-27B-Q4_K_M.gguf`.
  - Run steps 4–6 again with the same variables plus `LABEL_SUFFIX=-latest`, and pack them with the same variables
    and `bash scripts/90-collect.sh`.
  - Report these results separately from the comparable run.
