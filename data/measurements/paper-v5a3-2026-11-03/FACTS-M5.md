# FACTS section2 accepted M5 block

- **Apple M5 Max 64 GB at recorded normal priority, kit 1.6.7, llama.cpp `dde879bc`, Qwen3.8-27B and Glimmer 30B
  (Sergey, via Ivan, 2026-11-03; launched from Terminal).** Archives in `.temp/m5max64-results-261103/`:
  - `qwen27b-mac-bench-results-20261103T171250Z.tar.gz`, sha256 1d0d04a3...704c, model 31629f53...;
  - `glimmer30-mac-bench-results-20261103T183326Z.tar.gz`, 89211edd...9f9f, model 4cc57c0f...;
  - Both manifests: `normal_priority: true`, `priority_override_used: false`, ctx checkpoints 0. The readiness records
    show llama-server and its ancestry at PRI 31, nice 0 in every sample (Qwen 36, Glimmer 31). Both runs together took
    3 h 31 min (Sergey).
  - **Qwen, step 40, depth ladder** (prefill tok/s for the segment / Δ512 / Δ2000 / Δ10000, then decode tok/s):

    | Depth | Prefill | Decode |
    |---|---|---|
    | 16k | 662.9 / 550.3 / 475.9 / 447.9 | 23.26 |
    | 50k | 417.0 / 415.9 / 368.3 / 352.1 | 19.93 |
    | 100k | 281.2 / 265.6 / 234.6 / 232.7 | 15.54 |
    | 150k | 203.7 / 196.4 / 177.2 / 173.9 | 12.96 |
    | 200k | 156.1 / 155.3 / 139.5 / 137.7 | 11.11 |
    | 249k | 127.8 / 130.5 / 117.6 / 116.2 | 9.78 |

    Slot saves: 714 MB at 16k (43.6 KiB/token, 62 ms) to 8,833 MB at 249k (34.6 KiB/token, 702 ms). Four streams at 32k:
    40.08 tok/s aggregate, single 19.64, x2.04.
  - **Qwen, step 55, parallel decode by depth** (median aggregate tok/s by stream count; gain against one stream):
    - 32k, np 16: 23.108, 32.834, 46.87, 60.964, 57.089, 62.727 at 1/2/4/8/12/16 streams; x2.71 at 16.
    - 64k, np 8: 20.163, 26.257, 33.09, 40.816 at 1/2/4/8; x2.02 at 8.
    - 128k, np 4: 16.186, 18.825, 20.778 at 1/2/4; x1.28 at 4. A second np-4 server gave 24.351 at 4 streams (rounds
      22.80-26.29).
    - Against the kit 1.6.6 sweep of 2026-11-02, whose priority was not recorded: -2.2% to +3.0% at every point except
      12 and 16 streams on 32k, -9.1% and -4.3%.
  - **Qwen, step 56, 260k:** one-time prefill of 260,000 tokens at 199.2 tok/s; decode 9.711 tok/s with one stream and
    10.643 with two (x1.10). 1.04M was skipped: no slot file on this Mac.
  - **Qwen, step 57, agent sessions at 128k:** aggregate decode 12.373 / 11.159 / 12.576 tok/s with 1 / 2 / 4 sessions;
    mean prefill 89-92 tok/s; call p50 49.5 / 18.2 / 87.6 s, p90 150.9 / 107.4 / 357.8 s.
  - **Glimmer, step 40** (native context 131,072; prefill segment / Δ512 / Δ2000 / Δ10000, then decode):

    | Depth | Prefill | Decode |
    |---|---|---|
    | 16k | 662.2 / 630.9 / 541.0 / 516.1 | 27.08 |
    | 50k | 446.7 / 421.7 / 377.4 / 383.4 | 22.65 |
    | 100k | 347.9 / 323.6 / 304.3 / 308.0 | 20.83 |
    | 118k | 296.8 / 302.2 / 281.6 / 285.5 | 20.09 |

    Slot saves: 7.3-9.6 KiB/token. Four streams at 32k: 48.6 tok/s aggregate, single 23.72, x2.05.
  - **Glimmer, step 55:**
    - 32k, np 32: 29.045, 39.291, 59.22, 91.628, 90.835, 94.004, 75.543, 92.291 at 1/2/4/8/12/16/24/32; x3.24 at 16.
    - 64k, np 32: 27.122, 35.397, 50.784, 70.949, 64.977, 72.154, 60.715, 70.45; x2.66 at 16.
    - The 128k series was skipped: no stream count fits the native context.
  - **Glimmer, step 56, 129k, np 8:** 19.863, 24.397, 34.727, 42.214, 46.938 at 1/2/4/6/8 streams; x2.36 at 8.
  - **Glimmer, step 57, agent sessions at 64k:** aggregate decode 20.688 / 19.827 / 23.21 / 28.45 tok/s with 1 / 2 / 4 /
    8 sessions; mean prefill 169-190 tok/s.
  - **Decode batching against depth on the same Mac:** Qwen (34.6-43.6 KiB/token) keeps x2.71 at 32k, x2.02 at 64k and
    x1.28 at 128k. Glimmer (7.3-9.6 KiB/token) keeps x3.24, x2.66 and x2.36 at 129k.
  - **Against the M3 Max at PRI 31, Glimmer:** decode at 118k 20.09 against 8.82-10.0; Δ2000 prefill at 118k 281.6
    against 67.4.
