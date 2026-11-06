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
