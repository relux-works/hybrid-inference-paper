# Paper v2 (0.1.0 candidate): measured facts to bring into the text

Maintained by the orchestrator (agents1_hybrid_orch). Every number below is a measurement, or arithmetic on one, with
its evidence. "Pending" items are still running: the text must state them as pending, never as results. Lane notes:
`/home/agent/lanes/hybrid/NOTES.md`, 2026-11-01 entries.

## 1. Server: RTX PRO 6000 Blackwell Workstation (96 GB, 600 W)

Setup for all rows: llama.cpp `c21284cd` built from source with CUDA 12.8, arch `120a-real`, `-ngl 999 -fa on -ctk q8_0
-ctv q8_0`; Qwen3.8-27B Q4_K_M (sha256 31629f53…3d34).
- **Reproduced base, checkpoints off.** Two runs agree within 0.355% (engine run 13 fit; archives fd0bc08c… and
  e80d4240… in `.temp/gpu-results-261101/`).

  | Depth | Δ512 | Δ2000 | Δ10000 | Decode |
  |---|---|---|---|---|
  | 16k | 3,509 | 3,547 | 3,435 | 61.8 tok/s |
  | 249k | 898 | 905 | 971 | 34.6 tok/s |

  Prefill columns are tok/s.
- **Server default checkpoints (A/B, archive 92828a6c…).** Decode is the same.

  | Depth | Δ512 | Δ2000 | Δ10000 |
  |---|---|---|---|
  | 16k | 1,600 | 2,876 | 3,263 |
  | 249k | 742 | 946 | 973 |

  Checkpoints cost mainly on short deltas.
- **The earlier series (run 12 basis, archive 9accab80…, same card model and commit) was slower.** Δ2000 was 2,147 at 16k
  and 533 at 249k, and decode was 15–30% lower. The checkpoint A/B does not explain it. In run 13 it is a sensitivity
  case.
- **FP8 fraction.** The effective model-FLOP fraction of the dense FP8 peak is 14.1–21.1% across depths, against 8–13%
  in the earlier series. Formula: `(54e9 + 393216·depth)/(a+b·depth)/peak`. It is not nvidia-smi utilisation.
- **llama-bench sweep (step 70).** The newer upstream build `dde879bc` is 9–20% faster than `c21284cd`; ubatch tuning
  adds 2–5%. pp4096 at depth 0: 3,950 tok/s (`c21284cd`, ubatch 4096), 4,793 tok/s (`dde879bc`, ubatch 512).
- **vLLM 0.32.0, Qwen3.8-27B-FP8, same card, server only.**
  - Cold prefill: 8,122 tok/s at 16k, 2,209 at 249k.
  - Prefix caching works in Mamba "align" mode with 784-token blocks.
  - Cached deltas, Δ2000/Δ10000: 5,370/7,144 at 16k; 3,162/4,598 at 65k; 2,177/3,130 at 131k; 1,258/1,962 at 249k.
  - NVFP4 and FP8 KV did not start.
  - Not yet usable by our client: the state bridge is in qualification (pending).

## 1a. Server: kit 1.6.5 on the PRO 6000, llama.cpp `dde879bc`, Q4_K_M, q8_0 KV (host2, 2026-11-02 02:48-03:09Z)

Archives in `.temp/kit165-host2/`:
- `qwen27b-gpu-bench-results-20261102T030926Z.tar.gz` (3364b8a1...fe5);
- `gemma31-...030127Z` (a8b38efb...dc602);
- `glimmer30-...024947Z` (a9c8887e...606c).

Columns: segment prefill / Δ512 / Δ2000 / Δ10000 in tok/s, then decode tok/s at depth.

| Model | 16k | 50k | 100k | 150k | 200k | 249k |
|---|---|---|---|---|---|---|
| Qwen3.8-27B | 4,295 / 3,876 / 3,909 / 3,778 / 63.8 | 3,241 / 2,653 / 2,716 / 2,657 / 57.3 | 2,255 / 1,807 / 1,767 / 1,888 / 49.6 | 1,699 / 1,382 / 1,345 / 1,477 / 43.5 | 1,365 / 1,111 / 1,097 / 1,214 / 38.4 | 1,144 / 950 / 925 / 1,035 / 34.5 |
| Gemma 4 31B (SWA) | 3,476 / 3,025 / 2,977 / 2,684 / 56.0 | 1,959 / 1,614 / 1,633 / 1,560 / 44.1 | 1,248 / 1,019 / 1,039 / 1,018 / 33.5 | 879 / 746 / 767 / 761 / 27.0 | 681 / 593 / 613 / 610 / 22.6 | 559 / 492 / 511 / 511 / 19.5 |
| Glimmer 30B (SWA) | 4,468 / 4,042 / 4,171 / 4,221 / 73.4 | 3,986 / 3,378 / 3,616 / 3,712 / 68.1 | 3,428 / 2,725 / 3,015 / 3,126 / 61.6 | | | 118k: 3,028 / 2,531 / 2,823 / 2,936 / 59.4 |

- Qwen on the new build against `c21284cd` (section 1): Δ2000 at 16k is 3,909 against 3,547 (+10%), at 249k 925
  against 905; decode 63.8 against 61.8 at 16k.
- SWA models now run on the GPU depth ladder.
- Re-reads: none. Every delta row in the three JSONL files (12 Glimmer, 18 Qwen, 18 Gemma) processed only its delta.

## 1b. Server: B300 SXM6 AC (275 GB, 1100 W, CUDA 12.9, Vast 58724229, 2026-11-01)

Kit 1.6.5, llama.cpp `dde879bc` built for `103a-real` (native), Qwen3.8-27B Q4_K_M, q8_0 KV, checkpoints 0. Results in
`/root/kitb300/gpu/results/` on the host; the archive follows.

| Depth | Segment | Δ512 | Δ2000 | Δ10000 | Decode |
|---|---|---|---|---|---|
| 16k | 1,757 | 1,658 | 1,659 | 1,663 | 79.6 |
| 50k | 1,580 | 1,456 | 1,475 | 1,485 | 67.6 |
| 100k | 1,388 | 1,232 | 1,267 | 1,284 | 54.8 |
| 150k | 1,212 | 1,066 | 1,110 | 1,131 | 46.3 |
| 200k | 1,074 | 941 | 990 | 1,010 | 40.1 |
| 249k | 966 | 844 | 892 | 915 | 35.4 |

All columns are tok/s.
- Against the PRO 6000 (`c21284cd`), Δ2000 is 1,659 vs 3,547 at 16k and 892 vs 905 at 249k. Decode is faster: 79.6 vs
  61.8 at 16k, 35.4 vs 34.6 at 249k.
- llama.cpp's Q4 kernels do not reach the B300's datacenter-Blackwell tensor throughput. So the paper's ×4.466
  peak-ratio scaling from the PRO 6000 does not hold for llama.cpp.
- vLLM FP8 on the B300 (step 71) and the sweep (step 70) are running. The B300 server case must come from them, not from
  peak ratios.
- Note: the PRO 6000 comparison mixes builds (`c21284cd` vs `dde879bc`). The same-build PRO 6000 numbers on `dde879bc`
  come tonight from host 2 (kit 1.6.5, qwen27 step 40).

## 1c. Server: vLLM 0.32.0 FP8 on the B300 SXM6 AC (same host, 2026-11-01)

Archive `qwen27b-gpu-bench-results-b300-20261101T232533Z.tar.gz`, sha256 1325ae41…11bc, in
`.temp/b300-results-261101/`. Kit 1.6.5 step 71. The model is Qwen3.8-27B-FP8.
- **Cold prefill**, fitted marginal rate:

  | Depth | fp8-default | fp8-kv |
  |---|---|---|
  | 16k | 24,031 | 24,841 |
  | 50k | 19,096 | 21,846 |
  | 100k | 14,667 | 18,555 |
  | 249k | 8,673 | 12,806 |

  All in tok/s; fitted Δ10000 at 16k is 23,151. FP8 KV started on the B300; on the PRO 6000 it did not.
- **Cached deltas, fp8-default**, 784-token blocks, Δ2000/Δ10000: 11,638/20,140 at 16k; 8,755/14,768 at 65k;
  7,251/11,185 at 131k; 4,134/6,987 at 249k. With fp8-kv, 1568-token blocks: 13,761/20,961 at 16k.
- **Against llama.cpp on the same B300:** Δ10000 at 16k is 23,151 against 1,663, about 14x. Against vLLM on the PRO 6000
  (cold 8,122 at 16k, 2,209 at 249k): about 3.0x at 16k and 3.9x at 249k, default KV.
- **Conclusion for the paper:** on datacenter Blackwell, llama.cpp does not deliver the GPU's prefill throughput and vLLM
  does. A hybrid server on such cards needs the vLLM state bridge, which is in qualification.

## 2. Clients

- **Apple M3 Max 128 GB (40-core GPU).**
  - Canonical run, kit 1.6.0, `c21284cd`, checkpoints 0 (archive 13bff62f…, `.temp/mac-results-261101/canonical-qwen27-2110/`):

    | Depth | Δ-prefill, tok/s |
    |---|---|
    | 16k | 162–176 |
    | 50k | 93–101 |
    | 100k | 47–60 |
    | 150k | 28–31 |
    | 200k | 21–26 |
    | 249k | 16.5–20.7 |

    Decode over 128 tokens: 4.3–7.7 tok/s (noisy). 18 delta turns, no re-reads.
  - Earlier runs, same machine: decode 7.68 tok/s at 131k.
  - **PRIORITY A/B: kit 1.6.7 step 40 at normal priority, PRI 31 (incident lane, 2026-11-03 05:00-06:28Z).**
    - Archive `qwen27b-mac-bench-results-20261103T062853Z.tar.gz`, sha256 c2e83fbd...ace5, in `.temp/mac-results-261103/`.
    - Same build `dde879bc`, model and step-40 code as the background-root run of 10:33Z on 2026-11-02 (raw
      3afa4a6c...). Kit 1.6.7 recorded the ancestry: normal priority, no override.
    - Slots on the external SSD, so save and restore times are excluded from the comparison.
    - Columns: segment / Δ512 / Δ2000 / Δ10000 prefill tok/s, then decode tok/s.

      | Depth | PRI 31 values | Δ512 change | Decode before |
      |---|---|---|---|
      | 16k | 191.5 / 174.2 / 176.9 / 156.3 / 14.99 | +17% | 7.85 |
      | 50k | 128.8 / 121.7 / 116.1 / 106.7 / 13.52 | +61% | 6.59 |
      | 100k | 81.4 / 65.3 / 66.2 / 63.5 / 10.36 | +73% | 5.52 |
      | 150k | 52.5 / 46.2 / 47.1 / 44.4 / 8.99 | +22% | 5.16 |
      | 200k | 38.2 / 36.5 / 36.8 / 34.5 / 7.82 | +34% | 5.34 |
      | 249k | 30.1 / 28.7 / 29.7 / 27.8 / 6.93 | +37% | 5.27 |

    - Cumulative prefill to 249k: 59.7 min, against 84.8 min in the background.
    - Across all 18 cells, Δ-prefill rose 9-85% and decode 28-203%.
    - Conclusion: every earlier incident-lane M3 Max kit measurement ran in the macOS background band (PRI 4) and is
      throttled. That includes the canonical kit 1.6.0 run, the cooled kit 1.6.6 parallel sweep, Gemma, Glimmer and
      step 40.
    - The engine's M3 Max anchors must move to PRI-31 data. Re-measurement of the parallel sweep, Glimmer and Gemma
      was ordered at 06:35Z.
    - The decode at 100-143k in the growing-session run (10.0-12.3 tok/s, PRI 31) agrees with this.
  - **Kit 1.6.5 on the new build, `dde879bc`, checkpoints 0, step 40 only (incident lane, 2026-11-02, started
    10:33Z; the file tag 20261102T143351 is local +04:00 time).** Archive `qwen27b-mac-bench-step40-only-20261102.tar.gz`, sha256 b3d907c0...8c68, in
    `.temp/mac-results-261102/`; raw JSONL 3afa4a6c...eb08. Step 40 exited 0. The supervisor then stopped on its 55 GiB
    disk gate before step 90, which did not run.
    - Columns: segment / Δ512 / Δ2000 / Δ10000 prefill tok/s, then decode tok/s.

      | Depth | Values |
      |---|---|
      | 16k | 175.1 / 149.0 / 159.8 / 143.1 / 7.85 |
      | 50k | 81.5 / 75.8 / 89.0 / 57.7 / 6.59 |
      | 100k | 47.3 / 37.8 / 45.8 / 40.4 / 5.52 |
      | 150k | 38.6 / 37.8 / 41.9 / 39.5 / 5.16 |
      | 200k | 27.1 / 27.2 / 28.5 / 24.5 / 5.34 |
      | 249k | 22.3 / 21.0 / 26.2 / 21.0 / 5.27 |

    - 18 delta turns, 6 save and restore pairs, no re-reads. Slot size: 43.6 KiB/token at 16k, 37.1 at 50k.
    - Against the canonical run on `c21284cd` (above), Δ-prefill is lower at 50k-100k (100k: 37.8-45.8 against 47-60)
      and higher from 150k on (150k: 37.8-41.9 against 28-31; 249k: 21.0-26.2 against 16.5-20.7). Decode stays inside
      the old noisy range (4.3-7.7).
    - The Mac was not isolated for this run; the lane's other work at that time is not recorded. So the cause, the
      build or the conditions, is not established. The engine still uses the `c21284cd` canonical rates.
  - Parallel at 260k, aggregate tok/s for 1/2/4/6/8 streams: 5.98/7.63/7.03/6.68/6.42.
  - **Parallel sweeps not yet in the paper or the engine** (restored by engine run 14, dev-e r4):
    - Step 55 at 64k, aggregate tok/s for 1/2/4/8/16/24 streams: 7.2/11.9/13.9/15.6/27.2/31.9.
    - Step 55 at 128k, 1/2/4/8/12 streams: 6.3/8.9/9.7/10.1/13.9. These rounds ran right after a 34-minute prefill.
    - The 128k control from a restored context, 1/2/4/6/8 streams: 7.683/11.488/12.966/13.348/12.670, which is 21-33%
      above step 55. Archive 409bd7ef...d73e.
    - Step 57, realistic agents at 128k, 1/2/4/8 sessions, the Mac against the PRO 6000 on the same calls (archive
      9b7019cd...3ac2):
      - mean stream speed on the Mac: 7.00/4.73/2.97/1.63 tok/s;
      - call p90: 270.8/262.5/903.8/1142.0 s;
      - prefill share of call time: 3.9/26.1/14.4/9.6% on the Mac, against 1.6/8.7/4.5/3.6% on the PRO 6000;
      - an 8,193-token tool output takes the Mac 241-247 s at 4-8 sessions and the PRO 6000 9.8-10.2 s.
  - **Kit 1.6.6 cooled parallel sweep, M3 Max 128 GB, Qwen3.8-27B Q4_K_M, llama.cpp `dde879bc`, incident lane,
    2026-11-02 ~10:55-13:40Z.** Archive sha256 916891bd...d618, in `.temp/mac-results-261102/qwen27-kit166-scaling.tar.gz`.
    - Protocol: fill once per depth, a 300 s pause, then restore the slot before every round. Median of 3 rounds, no
      re-reads. The server ran with the largest fitting np.
    - Aggregate decode tok/s by stream count:

      | Depth | 1 | 2 | 4 | 8 | 12 | 16 | 24 | 32 |
      |---|---|---|---|---|---|---|---|---|
      | 32k | 8.77 | 14.66 | 24.03 | 33.39 | 38.46 | 44.41 | 43.50 | 47.83 |
      | 64k | 6.42 | 9.89 | 20.08 | 29.97 | 30.60 | 33.97 | 32.93 | 35.56 |
      | 128k, np 16 | 5.38 | 9.37 | 14.35 | 18.93 | 19.77 | 20.22 | | |

    - Rounding: each cell is the engine run 15 median (`calc/out/run15/base/parallel_anchors.csv`), rounded once to two
      decimals. The 8- and 12-stream cells at 32k were 33.40 and 38.47 here before 2026-11-02 12:10Z, rounded twice.
    - np control at 128k: 4 streams on a server started with np 4 give 16.03, against 14.35 under np 16.
    - Against step 55 (old build `c21284cd`, rounds right after a long prefill), the curve is smooth: the old jump
      between 8 and 16 streams at 64k is gone. At 8 streams, 64k gives 29.97 against 15.6 and 128k gives 18.93 against
      10.1.
    - Single-stream rounds vary: at 128k, 3.6/5.4/6.0.
  - **Kit 1.6.7 cooled sweep at normal priority (PRI 31), anchor counts only, M3 Max, same build `dde879bc` and
    model, incident lane, 2026-11-03 06:36-07:59Z.** Archive `qwen27b-mac-bench-results-20261103T075927Z.tar.gz`,
    sha256 801232de...3735, in `.temp/mac-results-261103/`.
    - Same protocol: fill once per depth, 300 s pause, slot restored before each of 3 rounds, median, no re-reads.
      Slots on the external SSD.
    - Only the largest stream count per depth was run (32, 32 and 16), plus 4 streams at 128k under np 16 and a fresh
      np 4 control. The intermediate counts at normal priority are not measured.

      | Depth | Streams | PRI 31 aggregate tok/s | Rounds | Background (above) | Change |
      |---|---|---|---|---|---|
      | 32k | 32 | 57.375 | 57.375 / 57.53 / 56.241 | 47.83 | +20.0% |
      | 64k | 32 | 37.862 | | 35.56 | +6.5% |
      | 128k, np 16 | 4 | 18.77 | 18.77 / 18.69 / 18.906 | 14.35 | +30.8% |
      | 128k, np 16 | 16 | 18.705 | 18.702 / 18.705 / 18.916 | 20.22 | -7.5% |
      | 128k, np 4 | 4 | 18.498 | | 16.03 | +15.4% |

    - Per stream: 1.793 tok/s at 32k with 32 streams, 1.169 at 128k with 16, 4.693 at 128k with 4.
    - At 128k, 4 and 16 streams give the same aggregate, 18.77 and 18.705.
    - Single-stream decode at PRI 31 (step 40 above): 10.36 tok/s at 100k and 8.99 at 150k.
    - Run-to-run spread seen elsewhere on the same protocol: the M5 Max 128k np 4 repeat gave 23.76 against 20.69
      (+15%).
  - **Why tab:clients gains are modest** (engine run 13, `paper.py` `throughput`).
    - Mean client seconds per call, from 8 h / (sessions x 116):

      | Client | Alone | Hybrid | Gain |
      |---|---|---|---|
      | M3 Max | 73.6 | 46.8 | x1.57 |
      | M5 Ultra 96 | 18.5 | 16.2 | x1.14 |

    - With 4 agents, the hybrid bound is each agent's own cycle: answer generation at the per-stream rate, plus tool time
      and wait. On the M3 Max the per-stream rate is 3.51 tok/s, so a 512-token answer takes about 146 s.
    - History of the gain, from NOTES: x3.5 (model v3, synthetic deltas, every agent decoding at the single-stream rate),
      then x2.1 (real call distribution), then x1.42 (measured 4-stream scaling, r5), then x1.57 (run 13).
    - Known biases of the M5 rows:
      - the M5 Max 128 GB estimate decodes at 12.96 tok/s, against 18.29 measured on the same SoC (64 GB);
      - its prefill scaling is x4.29, against x2.00-2.86 measured.
      - Run 14 rebuilds the M5 rows from the measured M5 Max.
  - 1.04M (YaRN): 1.67 tok/s.
- **Apple M3 Max 128 GB, Gemma 4 31B (SWA), kit 1.6.5, llama.cpp `dde879bc`, checkpoints 0 (incident lane, 2026-11-02 ~01:30-03:59Z).**
  Archive `gemma31-mac-bench-results-20261102T035935Z.tar.gz`, sha256 c9ad47e8...5272, in `.temp/mac-results-261102/`.
  Columns: segment / Δ512 / Δ2000 / Δ10000 prefill tok/s, then decode tok/s.

  | Depth | Values |
  |---|---|
  | 16k | 134.8 / 114.9 / 116.0 / 105.5 / 9.04 |
  | 50k | 71.1 / 58.9 / 50.2 / 42.1 / 6.58 |
  | 100k | 30.9 / 24.8 / 26.2 / 25.7 / 5.01 |
  | 150k | 20.2 / 20.0 / 20.3 / 16.8 / 4.20 |
  | 200k | 15.6 / 16.2 / 16.5 / 13.8 / 3.64 |
  | 249k | 11.7 / 14.2 / 13.3 / 10.9 / 3.15 |

  - No re-reads: 18 delta turns, prompt_n equal to the delta (512, 2001, 10001), and 6 slot saves and restores.
  - The ladder took 149 minutes.
  - Against the PRO 6000 on the same build (FACTS 1a), Δ2000 is about 26x faster on the server at 16k (2,977 against
    116) and about 38x at 249k (511 against 13.3).
- **Apple M3 Max 128 GB, Glimmer 30B (SWA 2048), kit 1.6.5, llama.cpp `dde879bc`, checkpoints 0 (incident lane,
  2026-11-02 ~10:15-10:28Z).** Archive `glimmer30-mac-bench-results-20261102T102823Z.tar.gz`, sha256 188f9790...a065, in
  `.temp/mac-results-261102/`. Native context 131072.
  Columns: segment / Δ512 / Δ2000 / Δ10000 prefill tok/s, then decode tok/s.

  | Depth | Values |
  |---|---|
  | 16k | 186.6 / 173.2 / 174.7 / 174.6 / 10.48 |
  | 50k | 135.4 / 104.5 / 105.8 / 101.1 / 9.29 |
  | 100k | 85.3 / 87.6 / 69.6 / 80.0 / 7.61 |
  | 118k | 52.6 / 50.4 / 54.0 / 58.0 / 7.21 |

  - No re-reads: 12 delta turns, prompt_n equal to the delta, and 4 complete saves and restores.
  - Slot size: 9.6 KiB/token at 16k and 7.8 KiB/token at 50k.
  - Against the PRO 6000 on the same build (FACTS 1a), Δ2000 is 4,171 against 174.7 at 16k (about 24x) and 2,823
    against 54.0 at 118k (about 52x).
- **Apple M5 Max 64 GB (Mac17,6, 40-core GPU, macOS 27.0.1), kit 1.6.6 cooled parallel sweep, llama.cpp `dde879bc`,
  Qwen3.8-27B Q4_K_M, q8_0 KV, FA on (Sergey, via Ivan, 2026-11-02 17:02-17:47Z).** Archive
  `qwen27b-mac-bench-results-20261102T174709Z.tar.gz`, sha256 b17ef9d9...b778, in `.temp/m5max64-results-261102/`.
  AC power, low power mode off, Metal working set 55.7 GB.
  - Same protocol as the M3 Max sweep: fill once per depth, a 300 s cool-down, the slot restored before every round,
    median of 3 rounds. The server ran with the largest np that fits 64 GB: 16 at 32k, 8 at 64k, 4 at 128k.
  - Priority, Sergey's answer via Ivan (2026-11-03 09:11Z):
    - he ran the kit through Codex inside the ChatGPT app, without ssh, tmux or nohup;
    - the same Codex process and a check command show PRI 31 and nice 0 now;
    - the priority and QoS of llama-server during the run were not recorded, so throttling cannot be excluded after the
      fact;
    - no heavy background load was seen before the start, and there was no continuous monitoring of other load.
    - Label: priority not recorded; the launching process was at PRI 31 when checked afterwards. A rerun on kit 1.6.7,
      which records the priority, would remove the caveat.
  - Aggregate decode tok/s by stream count:

    | Depth | 1 | 2 | 4 | 8 | 12 | 16 |
    |---|---|---|---|---|---|---|
    | 32k (np 16) | 22.62 | 31.89 | 47.78 | 62.32 | 62.78 | 65.54 |
    | 64k (np 8) | 19.88 | 26.00 | 32.55 | 40.23 | | |
    | 128k (np 4) | 15.73 | 18.35 | 20.69 | | | |

  - np 4 control at 128k: a second server with the same np gave 23.76 at 4 streams, against 20.69. That is the
    run-to-run spread of the same configuration.
  - Against the M3 Max cooled sweep: one stream is 22.62 against 8.77 at 32k, 19.88 against 6.42 at 64k, and 15.73
    against 5.38 at 128k. At 16 streams, 32k gives 65.54 against 44.41.
  - Step 90 (the depth ladder) is not in this archive. How the processes were launched (priority) is not recorded.
- **Apple M5 Max 64 GB (40-core GPU, macOS 27.0.1, kit 1.4.1).** Archive c7ceab57…, in `.temp/m5max64-results-261101/`.

  | Depth | Segment prefill, tok/s | Decode, tok/s |
  |---|---|---|
  | 16k | 586 | 23.1 |
  | 50k | 269 | 19.8 |
  | 100k | 151 | 14.6 |
  | 150k | 95 | 12.2 |
  | 200k | 70 | 10.6 |
  | 249k | 55 | 9.25 |

  - Δ2000: 394 → 51 tok/s.
  - 4 streams at 32k: 33.37 tok/s aggregate (single 18.29, ×1.82).
  - Step 57 ran with 5.1 GB of swap and is excluded from machine-speed figures.
  - Whether the M5 tensor units were used is not visible in the logs.

## 3. Prototype (repository relux-works/hybrid-inference)

- **27B on CUDA (PRO 6000), same partition, bit-exact.** Depths 132, 39,538 and 127,538: maximum logit difference 0.0.
  KL to the whole prompt is 0.0010–0.0036, within the client's own partition noise of 0.0014–0.0112. PR #9 landed
  (`f65c5948`).
- **Per-call import cost on a CUDA client (PR #9 run, node and client on one PRO 6000 over localhost).**
  Files: `.temp/pr9-results/hybrid-bench-r13-27b-cuda-*.jsonl`.
  - Offloads of 44-92 tokens carry 158-160 MB per call, mostly the recurrent state. Each takes 1.58-1.77 s of import,
    0.27-0.31 s of transfer and 0.02-0.05 s of server prefill.
  - 39,146 tokens: wire 1.99 GB, transfer 2.7-3.3 s, server prefill 10.6-10.8 s, import 20.2-20.3 s, TTFT 51.8-52.4 s.
    The same delta prefilled locally takes 11.0 s on that GPU.
  - 87,788 tokens at depth 39,702: wire 4.47 GB, transfer 7.4 s, server prefill 41.4 s, import 45.2 s, TTFT 152.3 s.
    Locally it takes 42.2 s.
  - Import rate: about 0.52 ms/token plus about 1.6 s fixed. The M3 Max over 5G took 1.07 ms/token (42.4 s for 39,504
    tokens).
  - Same-GPU offload is a functional test, not a speed case. These runs predate import-speed-v2.
- **End to end over 5G.**
  - Setup: node on CUDA in the UK, client the M3 Max on Metal, iPhone 5G by USB; RTT 110 ms, 16.0 MB/s down,
    9.78 MB/s up.
  - First call, fresh 39,504-token context:

    | Mode | TTFT | Breakdown |
    |---|---|---|
    | local | 271.5 s | |
    | hybrid | 201.7 s | server prefill 10.6 s + transfer 123.2 s + import 42.4 s |
    | offload | 211.7 s | |

    Hybrid is 26% faster than local.
  - Wire: 2,004,023,525 B. That is KV 39,504 × 34,840 B plus 4 copies of the 156.9 MB state, one per 512 MiB chunk.
  - The cross-backend equivalence check is labelled uncalibrated (calibration pending).
- **State transfer CUDA → Metal at depth.** This was kit step 56, stock llama.cpp, not the prototype.
  - Slots prefilled on the PRO 6000 restored exactly on the M3 Max: 260,000 tokens in each of 8 slots, and 1,040,000
    (YaRN) in each of 2. No re-reads.
  - The 1.04M session was filled on the PRO 6000 in 61 min, and 36.4 GB moved to the Mac.
- **Improvements since that end-to-end run.** Their effect on end-to-end time is not yet measured; a rerun is pending.

  | Improvement | Measured on CPU | Status |
  |---|---|---|
  | Fixed state only in the final chunk | 40k/27B wire 2,021,340,960 → 1,550,658,451 B (−470,682,509 B, synthetic) | accepted |
  | Local-kept short calls skip the node | TTFT 815 → 264 ms, CPU loopback | landed, PR #12 |
  | Client import | 2.1–2.6× faster | accepted, being rebased |
  | Model file hash | 19 GB on the M3 Max: 40.9 s with CommonCrypto against 256.3 s portable | landed, PR #7 |

- **vLLM → llama.cpp state bridge, first live run (B300, 2026-11-02 ~00:00Z).**
  - Server: vLLM 0.32.0, Qwen3.8-27B-FP8, with a post-forward hook that captures one request's paged attention KV and
    gated-delta-net state. A converter writes our native delta (q8_0 with Hadamard rotation, f32 state, layout
    fingerprint). Branch `m3-vllm-bridge` `4a25d528`, review pending.
  - Client: llama.cpp prototype on the same GPU, importing at 784 tokens, then 64 positions compared with the client's
    own prefill:

    | Client | Top-1 | Mean KL | First free-running divergence |
    |---|---|---|---|
    | BF16 GGUF | 64/64 | 0.00055 nats | none in 64 tokens |
    | Q4_K_M | 64/64 | 0.0027 nats | none in 64 tokens |

  - Labelled uncalibrated: the weights differ (FP8 on the server, GGUF on the client), so the result is approximate
    equivalence, never bit-exact.
  - Evidence: `/root/bridge/run2/` on Vast 58724229.
  - A depth run at 31,360 tokens is in progress (pending).
  - A node adapter, so the proxy and bench can use vLLM as the prefill node unchanged, is in development: `m3-vllm-node`,
    with a NumPy converter at 21.9 s for 40,000 tokens on CPU, against about 25 min before.
- **vLLM bridge at 31,360 tokens (B300, same head `4a25d528`, `/root/bridge/run3`, 2026-11-02 00:57Z).**
  - BF16 client: top-1 64/64, mean KL 0.0031 nats.
  - Q4_K_M client: top-1 64/64, mean KL 0.0061 nats.
  - No free-running divergence in 64 tokens. Checker exit 5, uncalibrated and heterogeneous.
  - KL grows with depth (0.00055 to 0.0031 for BF16, 0.0027 to 0.0061 for Q4_K_M), below the kit limit of 0.01.
  - The old scalar converter took about 22 min per client at this depth.
- **KL quantization study, stage 2 (host1 PRO 6000, `hetero_study.py`, build `m3-study-fast`, seed 42, 2026-11-01/02).**
  Report sha256 510c40d9...a6a8e, in `.temp/kl-study/kl-report-stage2.tar.gz` (`report27b-seed42`).
  - Reference: Qwen3.8-27B BF16. 20 Gutenberg documents, 40,960 scored positions, score batch 32.
  - Mean KL in nats, then top-1 agreement:

    | Arm | Mean KL | Top-1 |
    |---|---|---|
    | D-local (BF16 against itself, floor) | 1.6e-7 | 1.000 |
    | C-Q4-local (Q4_K_M client alone) | 0.0543 | 0.912 |
    | A-Mirai-local (trellis 27B client alone) | 0.382 | 0.749 |
    | B-Mirai, state imported from a Q4 / Q8 / BF16 node | 0.385 / 0.387 / 0.387 | 0.750 |
    | A-Bonsai-local (ternary 27B client alone) | 0.672 | 0.665 |
    | B-Bonsai, state imported from a Q4 / Q8 / BF16 node | 0.718 / 0.719 / 0.719 | 0.649 |

  - Reading: the client's own weights set the divergence. For an imported state, the node's precision (Q4, Q8 or
    BF16) makes no measurable difference. Importing adds nothing for Mirai and about 7% KL for Bonsai.
  - Stage 3 (unsloth UD quants) was stopped at 10:12Z for budget, after the UD-IQ2_XXS local arm; it is not in the
    report.
- **Heterogeneous task-quality run: Qwen3.8-27B Q8_0 node, Q4_K_M client (`--hetero-quant`), host2 PRO 6000, main
  `528724c9`, stages eval5-eval7, 2026-11-02 03:48-05:28Z.**
  - Same seed (17), tasks and positions as the homogeneous pilot; one evaluator run per depth, with the clients'
    saved slots deleted between depths. Local copy `.temp/eval5-results/`.
  - Correct out of 15 per depth, identical in every treatment (local Q4, offload of the Q8 node's state, a second local
    partition, a same-partition repeat): 12 at 8k, 11 at 32k, 9 at 64k.
  - Answer and token disagreements with local Q4, out of 15: offload 1/1/1 at 8k/32k/64k; a different local partition
    2/1/1; the repeat 0.
  - Reading: the Q8 server state changes the Q4 client's answers no more often than a different prefill partition does.
    Accuracy is unchanged at these depths. Not run at 128k.
- **vLLM as the hybrid prefill node, first end-to-end smoke (B300, `m3-vllm-node` `7936196c`, 2026-11-02 01:45Z).**
  - Setup: vLLM 0.32.0 FP8 node behind the adapter, llama.cpp Q4_K_M client on the same card, the standard proxy and
    `hybrid_bench.py --smoke --check`. Archive sha256 d343468d...ec244, local copy `.temp/node-smoke-b300/`.
  - Every import succeeded. Mean TTFT over 8 calls: local 2.72 s, offload 4.15 s. That is the same GPU, so a
    functional check only. Decode ran at about 96 tok/s.
  - 8k: hybrid against the whole prompt, KL 0.0055, top-1 63/64; the client's own partition noise KL is 0.0043-0.0063;
    ratio 0.87.
  - 32k: hybrid KL 0.0256 (append chain 0.0232), top-1 60/64, free-running divergence at token 9; local partition
    noise KL 0.0060-0.0108 at 62/64; ratio 2.38.
  - The checker exits 5: heterogeneous, FP8 on the node and Q4 on the client, uncalibrated.
  - A repeat of the same partition is bit-exact (KL 0).
  - The final reviewed head `c2f47472` (Muse r7q ACCEPT) repeated the smoke with identical equivalence numbers. Its CUDA
    byte gate ran inside the adapter at start. TTFT local 2.69 s, offload 4.04 s. Results archive in
    `.temp/node-smoke-b300/b300-bridge-node-evidence.tar.gz` (3f48838a...d1ff), with all bridge and node evidence. The
    B300 was destroyed at about 03:45Z.
  - **Exact landed head `9348ecd6` (main after PR #16), RTX PRO 6000 on host1, 2026-11-02 10:13-10:38Z.**
    - Same setup: vLLM 0.32.0 FP8 node, Q4_K_M client on the same card. Gather and the CUDA byte gate passed.
      Archive sha256 839911233bc550f5...a9c4, in `.temp/node-smoke-pro6000/`.
    - TTFT over 8 calls: local 1.571 s, offload 4.497 s. That is the same card, so a functional check only. Decode
      73.6-74.5 tok/s.
    - 8k: hybrid KL 0.0202, top-1 61/64, divergence at token 8. Local partition noise KL 0.0053-0.0099 at 62-63/64.
      Ratio 2.03.
    - 32k: hybrid KL 0.0233, top-1 60/64, divergence at token 9. The delta came in 5 chunks. The append chain gave
      the same numbers, with endpoints 7,840 / 31,360 / 32,144. Local partition noise KL 0.0022-0.0030 at 63-64/64.
      Ratio 7.83.
    - A repeat of the same partition is bit-exact (KL 0). Checker exit 5: heterogeneous and uncalibrated.
    - Against the B300 run, 32k is the same (0.0233 against 0.0256). At 8k the PRO 6000 shows about 4x the KL (0.0202
      against 0.0055), and its own partition noise at 32k is about 3x lower, so the ratios are higher. Its FP8 kernels
      differ from the B300's; the cause was not isolated.
- **Task-quality pilot, homogeneous Qwen3.8-27B Q4_K_M node and client (host2 PRO 6000, `tools/hybrid-eval`, stage
  eval4).** Archive sha256 181c02ec...d78d6, local copy `.temp/eval4-results/`.
  - Coverage: five task types x three positions x depths 8k/32k/64k, plus 128k for single_needle only. The run aborted
    at 128k on a full disk (HTTPError), so 48 cases per treatment.
  - Correct answers: 35/48 in every treatment (local, offload, local_partition, local_repeat).
  - Disagreements with local, out of 48: offload 4 token and 4 answer disagreements; a second local client with the
    node's batch partition, also 4 and 4; a same-partition repeat, 0.
  - McNemar exact p = 1 in every cell.
  - Reading: offload changes answers exactly as often as a different prefill partition does. This does not establish
    equivalence, and the heterogeneous-quant variant is still pending.
- **Mirai S (trellis-quantized Qwen3.8-27B).** Port matches the alesha-pro fork greedily 10/10. The hybrid is bit-exact
  at depths 516–6,182 on CUDA. Landed, PR #11. KL results pending.
- **Sliding-window models (Gemma 4 31B, window 1024; Muse Glimmer 30B, window 2048).**
  - Two upstream llama-server behaviours forced whole-prompt re-reads:
    - a context shorter than the window;
    - a slot restore, on `c21284cd`, fixed upstream by #30580.
  - The kit moved to `dde879bc` (kit 1.6.5).
  - The prototype's window transfer was not bit-exact beyond the window, because cell compaction changed the reduction
    order. It is fixed and bit-exact on CPU.
  - GPU qualification pending (tonight).

- **Growing session: mechanism and gate (dev-b r38-r42, reviews r7v and r7w; landed as PR #17, main `fca0fe31`).**
  - After an append import, the client keeps its own attention-KV rows for earlier positions and imports the node's
    new range plus its recurrent state. The attention KV therefore has mixed provenance; that is the source of the
    deviation from a whole-prompt local prefill. A deterministic replay of the same import chain (CHAIN-H) is
    bit-exact.
  - Gate at each checkpoint: 10 exact controls, plus journal, hash and raw-logit integrity, plus L-H top-1 of at least
    63/64. The 10 controls are node, restore, state and range imports; own native and range; the chain and its
    attention and recurrent parts; A against L. Free-running divergence and the fidelity flag are report-only.
  - Alternative contract: a full attention-KV refresh after every catch-up costs 34,816 B/token (Qwen3.8-27B q8_0), so
    3.48 GB at 100k and 7.52 GB at 216,064 per offload.
- **Growing session, GPU rehearsal (host2 RTX PRO 6000, node and client on the same card over loopback, CUDA to CUDA,
  `57e3a232`, 2026-11-02 07:16-13:20Z).** Evidence `.temp/grow2-rehearsal/grow2-rehearsal-evidence.tar.gz` (4d9062cc...c5d):
  trace, checkpoint results and checker logs.
  - Setup:
    - 100k start, 40 sampled turns (seed 1), pre-staged;
    - outage at turn 20 for 3 turns;
    - policy with the M3 Max target rates, the PRO 6000 node rate at 100k, the 5G link (16 MB/s, 110 ms) and the
      PR #9 CUDA import fit.
  - Hybrid arm: 17 policy offloads and 20 policy local turns after the pre-staged base. The 3 outage turns ran locally:
    1 transport fallback and 2 disconnected turns. 35 background catch-up events. Imports: 18 (base included), 77.4 s
    in total.
  - Arm windows: hybrid 1,798.5 s, local 1,470.6 s, partition arm with the checkpoints 18,115.6 s. Both roles run on
    one card, so this is a functional check, not a timing comparison.
  - Cleanup: no remote session left.
  - Every checkpoint passed with all 10 exact controls, top-1 64/64, and no free-running divergence in 64 tokens.
    Columns: depth / mean KL / p95 KL / local partition KL / ratio to partition KL / checker time.

    | Turn | Values |
    |---|---|
    | 10 | 109,591 / 1.06e-4 / 3.35e-4 / 6.12e-4 / 0.17 / 31 min |
    | 20 | 123,135 / 1.54e-4 / 4.26e-4 / 3.48e-5 / 4.43 / 56 min |
    | 30, after the outage | 134,015 / 2.45e-4 / 4.69e-4 / 1.60e-4 / 1.53 / 85 min |
    | 40 | 143,439 / 6.2e-5 / 1.50e-4 / 1.80e-4 / 0.35 / 66 min |

  - Checkpoint cost on the M3 Max is about 4-11 h each, by dev-b's model (r44 PLAN.md), so the Mac run checks turn 10
    only.

- **Growing session on the M3 Max over home Wi-Fi: the preflight refuses an all-local plan (incident lane,
  2026-11-02 18:40-20:15Z; packet r44c SHA256SUMS 3ea9fc62, code `5be993f2`, node `fca0fe31`).**
  - Node: Vast RTX PRO 6000 Server Edition in Bulgaria (58864154). The first node, in Texas, measured 3.25 MB/s down
    and 1.27 MB/s up with RTT 641 ms from the Mac, and was replaced.
  - The Mac's home internet, by `networkQuality` (16 flows): 56.6 Mbit/s down, 55.0 Mbit/s up, idle RTT 105 ms.
  - Link to the Bulgaria node through one SSH stream (link probe, 21 samples): 5.19 MB/s down, 4.49 MB/s up, warm RTT
    125.8 ms. All processes at PRI 31.
  - M3 Max import fit on this head, Metal, 16 forced offloads in one repetition: 1.498 s fixed plus 0.0487 ms per
    transferred token, R2 0.12.
    - The import time grows with the conditioning depth: the same 539 tokens took 0.36 / 0.97 / 2.02 / 3.75 s at
      prefixes of 2k / 20k / 50k / 100k.
    - The policy models only fixed plus per-token, so it under-predicts the import at depth.
  - Preflight with that link and fit, over the 40-turn seed-1 workload from 100k:
    - all 37 connected turns route local and none offloads, so the run was refused as degenerate;
    - turn 7 (a 2,343-token delta) predicts 42.7 s local against 57.2 s offload;
    - an offload of a small delta predicts about 37.5 s, mostly the 157 MB fixed state at 5.19 MB/s.
    - By the same formula, turn 7 offloads only above about 8.45 MB/s at the same RTT and fit.
  - Route-plan extract `.temp/growing-mac-261102/PREFLIGHT-ROUTE-PLAN.json.gz` (a51c1358...89bd6).

- **Why the import time grows with depth (dev-d r12, CPU replay on agents1, prototype `fca0fe31`, branch
  `m3-import-depth` `313289af`, diagnosis only, not yet reviewed).**
  - A fixed 539-token append import, median proxy import time at depths 2,116 / 8,192 / 32,768 / 65,536: 48.18 /
    54.08 / 104.01 / 178.27 ms.
  - Cause: `import_ms` includes a full save of the client's old slot, taken as a recovery point before the final
    import. That save grows with the session and explains 94.2% of the fitted depth slope.
  - Copying the native KV metadata is secondary (0.45 to 3.85 ms). Delta validation and tensor writes stay nearly flat.
  - A bounded undo, saving only what the import overwrites, would remove the slope. It exists in draft and needs
    transaction and lost-acknowledgement qualification before use; not implemented.
  - The Mac's depth dependence (0.36 to 3.75 s, FACTS above) is consistent with it, but the Mac benefit of a fix is
    not measured. Report `tools/hybrid/RESULTS-hybrid-d-r12-261102.md` in `~/Werkstatt/hybrid-d/llama.cpp`.
- **Growing session on the M3 Max over 5G (owner's iPhone over USB, en19) to the Bulgaria node: preflight passes,
  run started 2026-11-02 22:56:32Z.**
  - Link through one SSH stream: 9.75 MB/s down, 12.09 MB/s up, warm RTT 140.6 ms. The owner's nominal 5G is
    250-300 Mbit/s.
  - The same import fit and policy as on Wi-Fi.
  - Preflight: 35 connected turns local and 2 offloads, at turns 7 and 31. Each predicts 42.7 s local against 31.8 s
    offload. At turn 5: 14.5 s local against 24.4 s offload, so it stays local.
  - The checkpoint at turn 10 follows the turn-7 import, which comes after the resync at turn 5.
  - RAM gate 70.33 GiB below 102.4; disk 605.6 GB free against 325.
  - Route plan `.temp/growing-mac-261102/5g-PREFLIGHT-ROUTE-PLAN.json.gz`. Results pending.

- **Growing session CUDA to Metal over 5G, the main run: both timing arms complete, the checkpoint unmeasured
  (2026-11-02 22:56Z to 2026-11-03 02:44Z).**
  - Setup:
    - client M3 Max (Metal, prototype `fca0fe31` plus the r44 driver `5be993f2`), every process at PRI 31;
    - node RTX PRO 6000 Server in Bulgaria;
    - link through one SSH stream: 9.75 MB/s down, RTT 140.6 ms;
    - 100k pre-staged start, 40 turns (seed 1), outage at turns 2-4.
    - Timing extract `.temp/growing-mac-261102/TIMING-EXTRACT.json.gz` (d0d3f021...). Private archive on the owner's
      LaCie: 4.13 GB, sha256 93ab0d9b....
  - Hybrid arm: 40 turns, 38 local and 2 offloads (turns 7 and 31). Local arm: 40 turns, all local.

    | Arm | TTFT sum / mean / median | Total time | Local prefill | Decode |
    |---|---|---|---|---|
    | Hybrid | 1,158.7 / 28.97 / 2.35 s | 3,646.4 s | 173.3 s | 11.06 tok/s (10.00-12.16) |
    | Local | 262.9 / 6.57 / 2.24 s | 2,736.8 s | 246.0 s | 11.12 tok/s (10.03-12.29) |

    The hybrid arm also spent 9.7 s on imports and 134.9 s on catch-up, with 477 MB on the wire.
  - The two offloads, against the same turns run locally:

    | Turn | Delta | Hybrid TTFT | Wire | Import | Catch-up | Local TTFT |
    |---|---|---|---|---|---|---|
    | 7 | 2,343 tokens | 468.7 s | 238.5 MB | 4.0 s | 3.3 s | 33.7 s |
    | 31 | 2,343 tokens | 490.5 s | 238.5 MB | 5.6 s | 3.8 s | 38.9 s |

  - Instrumentation split (`.temp/growing-mac-261102/INSTRUMENTATION-TIMING-EXTRACT.json.gz`, trace e38da6db...).
    The checker's full node snapshot captures run synchronously inside the call's TTFT. TTFT minus capture is an
    arithmetic residual, not a production TTFT.

    | Call | TTFT | Captures | Capture time | Residual | Local, same call |
    |---|---|---|---|---|---|
    | Base 100k | 2,896.8 s | 10, 22.11 GB | 2,413.5 s | 483.3 s | 884.0 s |
    | Turn 7 | 468.7 s | 1, 3.88 GB | 425.6 s | 43.1 s | 33.7 s |
    | Turn 31 | 490.5 s | 1, 4.91 GB | 455.2 s | 35.3 s | 38.9 s |

    - Captures ran at 9.1-10.8 MB/s.
    - Base components: server prefill 41.9 s, transfer 397.4 s (3.64 GB in 10 chunks), final import 2.9 s, staged
      chunk imports 0.26-0.34 s each.
    - Reading:
      - over this 5G link, the 100k base minus instrumentation took 483 s against 884 s local, about 1.8x faster;
      - the two per-turn offloads came out 9.4 s slower and 3.6 s faster than local. The policy predicted 31.8 s
        offload against 42.7 s local, but its local rates came from the background-root fixture, and the local Mac
        at PRI 31 was faster than that.
  - Base 100k:
    - hybrid pre-stage TTFT 2,896.8 s, with 3.64 GB on the wire and a 2.9 s import; that includes the snapshot
      captures (see the split above);
    - local prefill 884.0 s (880.2 s prefill).
  - Checkpoint 10 was not measured. The checker labelled the Metal backend `MTL` (ggml registry name), and
    `check.cpp:523` maps only `Metal`, so the guard refused. A fix and a checkpoint-only recheck on the preserved inputs
    are in progress.
  - Resync: the last import boundary before checkpoint 10 (106,849) lies past the outage depth (103,024).
  - Decode at PRI 31 was 10.0-12.3 tok/s from 100k to 143k in both arms. The background-root kit runs gave 5.2-7.5 tok/s
    at those depths on stock `dde879bc`. The kit 1.6.7 A/B on stock `dde879bc` at PRI 31 (section 2, PRIORITY A/B)
    gave 10.36 tok/s at 100k and 8.99 at 150k.

- **Paired RULER, 8k depth (RTX PRO 6000, Vast 58864154, Bulgaria; prototype `m3-ruler-eval` `18d3f114`, Muse r7ag
  ACCEPT; 2026-11-03 05:52-07:32Z).** Archive `depth-8192-complete.tar.gz`, sha256 2be3eae6...48aa4, in
  `.temp/ruler-results-261103/`.
  - Design:
    - Qwen3.8-27B Q4_K_M on CUDA in all three arms;
    - 13 RULER tasks x 30 examples = 390, seed 261102, the same examples in every arm;
    - arms: local (client, batch 64), offload (prefill on the node, state imported by the client), partition (local,
      batch 256).
  - RULER score: 97.01% in all three arms.
    - Per-example scores agree in all 390 examples: 0 disagreements of offload against local, 0 of partition against
      local.
    - Per task, in every arm: 100% in 10 tasks, fwe 97.78%, qa_1 96.67%, qa_2 66.67%.
  - Answer text changed against local (outer-whitespace equality):
    - offload 34/390 = 8.72% (95% Wilson 6.31-11.94%);
    - partition 32/390 = 8.21% (5.87-11.35%);
    - 29 examples changed in both arms, 5 only under offload, 3 only under partition; McNemar exact p = 0.727.
  - Excess, offload minus partition: 95% interval -2.13 to +3.12 pp (Bonferroni exact cell bounds). Equivalence at the
    declared 2 pp margin is not established at this n.
  - Where the changes fall:
    - cwe: offload 12/30, partition 11/30;
    - fwe: 10/30 and 9/30;
    - niah_multikey_3: 5 and 6;
    - niah_multivalue: 3 and 2;
    - niah_multiquery: 2 and 1;
    - niah_multikey_2: 1 and 2;
    - qa_1: 1 and 1;
    - none in the other six tasks.
  - Run time: 1 h 40 min for 390 examples x 3 arms, 15.4 s per example. The 32k depth started at 07:32Z; its first 33
    examples took 57 s each.
  - The earlier `b63d9019` run stopped after 17 examples on a full disk (a slot-file leak, fixed in `18d3f114`). Its
    rows are kept as incident evidence and are not part of these results.

## 4. Economics inputs

- Claude Sonnet 5.5 cache hits cost $0.10/MTok, 0.05x of base input. Verified 2026-11-01 on
  platform.claude.com/docs/en/about-claude/pricing.
- Gemma 4 31B full-attention KV is 43,520 B/token at q8_0; the old value was 21,760.
- Engine run 13 carries both; it is on local branch `engine-r13`, with ledger `calc/ENGINE-QUOTES-R13-261101.csv`.

## 5. Pending: state as pending, with the expected date

Updated 2026-11-03 08:25Z (the v4 brief labels it 08:40Z).
- Paired RULER at 32k: running since 07:32Z on 2026-11-03, about 6 h. 64k and 128k: after the owner's budget decision.
- Fidelity of the CUDA to Metal main run: the checkpoint-10 recheck on the M3 Max. The first attempt on 2026-11-03
  stopped before the checker started (a RAM preflight refusal) and is under investigation.
- The full parallel curve on the M3 Max at normal priority (the intermediate stream counts): needs an idle Mac window
  from the owner.
- Glimmer 30B and Gemma 4 31B on the M3 Max at normal priority: the same window. Their kit 1.6.5 Mac numbers were
  measured at background priority.
- Engine run 16b: the normal-priority multi-stream M3 anchors, after the full curve.
- CUDA to Metal calibration against the BF16 reference: needs the Mac.
- vLLM state bridge on GPU: after its rework.
- Bonsai 2 ladder 2B/4B/9B: later.
- Measured since the earlier pending list, so no longer pending: the KL study (stage 2; stage 3 stopped and not
  reported), the task-level evaluation (eval4-eval7), the sliding-window GPU qualification, GPU kit 1.6.5, the B300 runs,
  the Mac kit 1.6.5 runs of Gemma 4 and Glimmer (at background priority), and the end-to-end CUDA to Metal run over 5G.

## 6. Future work: name it, no new claims

- Split point inside the model.
- Speculative decoding with a local drafter and server verification.
- MoE with experts streamed from SSD (Qwen3.8-Flash-Next).
- NVFP4 on the server.
- Server attestation for verifiable prefill.
- Task evaluation at 300 cases per cell.
- Gigabit-link measurements.
