- **vLLM decode batching by depth on the RTX PRO 6000 Workstation, measured (GPU kit 1.6.11 `cd85a194`, Muse r7at
  ACCEPT; Vast node G, New York; stage 2026-11-03 20:10:09-23:35:50Z, receipt status done, 3.43 h, $6.53).** vLLM
  0.32.0, Qwen3.8-27B-FP8, default KV (FP8 KV does not start on SM 12.0). Each stream has its own context with a private
  prefix and salt and generates 256 tokens. Three rounds, median aggregate over the common decode interval. Timing
  granularity: SSE chunk receipt, with exact token ids per chunk (vLLM merges queued tokens when the reader lags).
  Evidence: `.temp/evidence/vllm-pro-g1611-261103/` (g1611.tar.gz, sha256 8a58f122...efe0).

  | Depth | Largest resident | Aggregate tok/s at N = 1 / mid / max | Gain at max |
  |---|---|---|---|
  | 16,384 | 39 | 48.70 / 302.60 (8) / 737.93 (39) | x15.15 |
  | 65,536 | 12 | 44.46 / 190.29 (8) / 225.35 (12) | x5.07 |
  | 164,000 | 5 | 38.11 / - / 84.22 (5) | x2.21 |
  | 256,000 | 3 | 33.07 / - / 57.73 (3) | x1.75 |

  - The largest resident count falls with depth because each session's KV must stay resident; larger N are no-fit.
    At 16k, N = 32 gives 686.82 (x14.10).
  - Per-stream rate at the largest N: 18.92 / 18.78 / 16.84 / 19.24 tok/s.
  - TTFT median at the largest N: 2.55 / 1.37 / 0.61 / 0.97 s.
  - The kit 1.6.9 run's 16k rows (48.72 / 302.98 / 686.80 / 738.10) agree within 0.1%.
  - **1M on the PRO 6000 (step 74), refused as accepted outcome data:** default KV needs 61.97 GiB for 1,010,001 tokens,
    and 56.62 GiB is available. FP8 KV is unavailable.
  - **vLLM-to-client bridge timing (prototype `m3-vllm-bridge-timing` `82843cee`, loopback, CUDA client), medians:**
    - 16k, Δ2343: TTFT 1,710.6 ms. Server prefill 335.1, export 72.6, conversion 570.2, transfer 39.5, import 349.0,
      other and local tail 315.9.
    - 16k, Δ10000: TTFT 4,741.7 ms. Prefill 1,616.2, export 226.6, conversion 1,606.5, transfer 89.5, import 771.4,
      other 435.5.
    - Deeper rows: in `bridge/timing/bridge-timing.json`.

## 1a. Server: kit 1.6.5 on the PRO 6000, llama.cpp `dde879bc`, Q4_K_M, q8_0 KV (host2, 2026-11-02 02:48-03:09Z)

Archives in `.temp/kit165-host2/`:
- `qwen27b-gpu-bench-results-20261102T030926Z.tar.gz` (3364b8a1...fe5);
  - **The Mac's direct 512k and 1.04M measurement, complete** (kit 1.6.12 `7ca3c4f8` step 56, verified handoff;
    owner's M3 Max 128 GB at normal priority, warm, no purge; slots and references read from LaCie, model internal;
    incident lane, started 22:33Z, completed about 00:39Z on 2026-11-04; root review ACCEPT).
    - Strict archive 1,069,117 B, sha256 90723f8c...be43, with the incident lane. All per-child restore times and raw VM
      snapshots are in `PAPER-NUMBERS-AND-PER-CHILD-MEMORY.json`.
    - The raw-logit bound was 4.0. It was raised from 1.0 after the first attempt refused at 524,288 (block above). Both
      attempts must be stated; 4.0 is not a calibrated bound.
    - Each delta shape is one excluded warm-up plus three timed rounds, with medians. Every round first restores the
      original slot. The prefill seconds exclude the restore. Decode is 255 steps after the seed. Server TTFT is not
      available on the native path.

    | Metric | 524,288 | 1,040,000 |
    |---|---|---|
    | Restore before the probe, s | 20.523 | 40.465 |
    | Restore before a timed decode round, median s | 2.965 | 40.479 |
    | Gate: max KL / mean KL, nats | 0.0017539 / 0.00032912 | 0.0021309 / 0.00032571 |
    | Gate: top-1 / max abs logit difference | 64/64 / 1.08298 | 63/64 / 3.01402 |
    | Decode, median tok/s | 3.8409 | 1.6638 |
    | Δ690 prefill, median | 48.255 s, 14.299 tok/s | 72.408 s, 9.5293 tok/s |
    | Δ2000 prefill, median | 161.768 s, 12.363 tok/s | 296.966 s, 6.7348 tok/s |
    | Δ10000 prefill, median | 843.260 s, 11.859 tok/s | refused: 1,050,000 > 1,048,576 |

    - At 524,288 the later restores are faster than the first (2.97 s against 20.5 s): the 18.4 GB file stays in the OS
      cache. At 1.04M every restore takes about 40.5 s: the 36.4 GB file does not stay cached next to the wired model
      and KV.
    - Memory: all 30 native children stayed within the bound, the largest at 1,064 pages. Total pageouts were 7,755
      pages (127,057,920 B). Swapouts were 0.
    - Against engine run 22's estimates for the M3 Max at 1M (`link_thresholds.csv`):
      - the local Δ690 prefill was 70.53 s by the anchored FLOP-efficiency extension, and 120 s in the analyst's
        sensitivity; measured 72.408 s at 1,040,000, 2.7% above the anchored value;
      - the Mac import was 34.94 s, an extrapolated depth slope; the measured restore is 40.47 s, from LaCie.
      - Engine run 23 replaces both estimates with these measurements.

- **Quality at depth, 512k and 1.04M (prototype `m3-depth-quality` with the r47c fixes, stage source `4268306c`; Vast
  node F, RTX PRO 6000 Server Edition, Nevada; 2026-11-03 16:59:05-22:46:47Z, 20,861.7 s).** Stage archive
  `stage-metadata.tar.gz`, sha256 e46e8ed1...8773, with the five `report.json` (hashes as in `complete.json`), the reports
  and the per-case `results.tar.gz`, in `.temp/evidence/depth-quality-f-261103/`. The per-arm full-document f32 logits
  (4.07 GB each) were not kept; node F was destroyed after the fetch.
  - **Design.**
    - Llama.cpp, Qwen3.8-27B Q4_K_M, YaRN for 1.04M.
    - Each case: 4,096 teacher-forced positions in the final window, plus 16 sequential needle questions.
    - Arms:
      - local;
      - offload: the same device, an f32 delta-v2 handoff at the window boundary;
      - partition: a different batch partition.
    - It is descriptive: no network, no equivalence threshold, one document per case.
  - **Offload against local, every case: mean KL 0, top-1 1.000000, maximum absolute logit difference 0.** Every arm
    answered 16/16 needles exactly, and offload answers equalled local in 16/16.
  - **Partition noise against local** (mean KL nats / top-1 / max |Δlogit|):

    | Depth | Document | Values |
    |---|---|---|
    | 524,288 | llama-source | 0.0285748 / 0.991211 / 27.83 |
    | 524,288 | oasst-public | 0.0037251 / 0.996338 / 30.42 |
    | 524,288 | tiny-stories | 0.0082421 / 0.978027 / 24.40 |
    | 1,040,000 | llama-source | 0.0101671 / 0.963867 / 15.34 |
    | 1,040,000 | oasst-public | 0.0077366 / 0.987549 / 22.82 |

  - Windows: positions after 520,192 at 524,288, and after 1,035,904 at 1,040,000.
- **Engine run 23 (dev-e r17, `engine-r23` `9064701a`, parent `9053089e`; Muse r5x5 ACCEPT, 2026-11-04 ~02:13Z).**
  Report `calc/ENGINE-REPORT-R23-261104.md`, outputs `calc/out/run23/`. Suites: engine 543, kit 24, report, manifest
  and audits exit 0. The 1,014 historical outputs are byte-identical.
  - **Inputs replaced with measurements:**
    - the Mac's local Δ690 at 1,040,000: 72.408 s, against run 22's 70.53 s estimate;
    - the PRO 6000 server decode at 16k / 64k / 164k / 256k, measured. It is interpolated between those points, by a
      stated method, and modelled beyond 256k. B300 decode stays modelled.
    - The Mac import is charged as the full-slot warm LaCie restore, 40.479 s. This is an explicit proxy
      (`recovery_kind=full_slot_restore_proxy`) and never a measured delta import.
  - **1M routing,** M3 Max, Δ690, B300 FP8 with FP8 KV, RTT 126 ms:
    - bf16 threshold 3.351 MB/s at a nominal 1M and 3.356 at 1,040,000;
    - f32 control 5.916 and 5.925;
    - 120 s sensitivity: 1.311 with bf16, 2.314 with f32.
    - Run 22 had 2.992 and 5.283.
    - bf16 offloads at 5.19, 9.75 and 5.18 MB/s, and stays local at 0.8 and 2.8.
  - **The PRO 6000 at 1M is impossible** in every export row: 61.97 GiB needed against 56.62 GiB available.
  - **Changes against run 22:**
    - 39 of the 377 abstract-bound coordinates changed, and 14 crossing rows.
    - The claude_deep measured-shape light crossing against the own cluster, on the rented WAN server, went from 87 to
      73 people.
    - The bought-office headline crossings are unchanged: own cluster never / 5 / 2, median API heavy from 45, cheapest
      never.

## 4. Economics inputs

- Claude Sonnet 5.5 cache hits cost $0.10/MTok, 0.05x of base input. Verified 2026-11-01 on
  platform.claude.com/docs/en/about-claude/pricing.
- Gemma 4 31B full-attention KV is 43,520 B/token at q8_0; the old value was 21,760.
- Engine run 13 carries both; it is on local branch `engine-r13`, with ledger `calc/ENGINE-QUOTES-R13-261101.csv`.

## 5. Pending: state as pending, with the expected date

Updated 2026-11-03 08:25Z (the v4 brief labels it 08:40Z).
- Paired RULER (updated 2026-11-03 15:40Z). Qwen 8k and 32k are complete (section 3). Running:
  - node A (Bulgaria): the bf16 arms at 8k and 32k from 14:24Z, then the three-arm 64k depth;
  - node B (Czechia): 128k from 14:29Z, about 32-36 h, so until about 00:00-02:00Z on 2026-11-05;
  - node D (Japan): Glimmer 8k is complete (section 3); 32k, 64k and 122,880 follow, 33-50 h for all four depths.
  - The pre-registered equivalence analysis (`m3-ruler-prereg` 7556f461) applies to the depths that finish before the
    RC4 data cut-off, 2026-11-05 12:00Z.
- Fidelity of the CUDA to Metal main run: measured on 2026-11-03 (checkpoint 10 recheck, section 3). Calibration of
  the heterogeneous tolerance is still pending, so its exit 5 is not a calibrated acceptance.
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
