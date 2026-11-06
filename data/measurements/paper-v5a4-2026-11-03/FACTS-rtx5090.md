- **NVIDIA RTX 5090 32 GB as a client (rented, Vast 58945901, Oregon; Intel i9-14900KF, 32 threads, 31 GB RAM; driver
  580.178.04, CUDA 12.8; GPU kit 1.6.7, llama.cpp `dde879bc` built for sm_120a; q8_0 KV; scheduling class TS, normal
  priority; 2026-11-03 09:46-10:26Z).** Archives in `.temp/ckit-results-261103/5090/`:
  `qwen27-rtx5090-20261103T100641Z.tar.gz` (sha256 b10541aa...e3e8; corrected on 2026-11-03; an earlier entry wrongly read ...16b) and `glimmer30-rtx5090-20261103T102603Z.tar.gz`
  (3f3f0506...bd16b). All kit steps exited 0. One slot fits 262,144 tokens of Qwen.
  - Columns: segment / Δ512 / Δ2000 / Δ10000 prefill tok/s, then decode tok/s.

    | Depth | Qwen3.8-27B Q4_K_M | Glimmer 30B Q4_K_M |
    |---|---|---|
    | 16k | 3,757.7 / 3,650.0 / 3,366.4 / 3,190.9 / 65.68 | 3,822.9 / 3,841.2 / 3,572.8 / 3,555.9 / 73.85 |
    | 50k | 2,585.7 / 2,326.7 / 2,186.0 / 2,001.9 / 57.95 | 3,347.4 / 3,297.3 / 3,154.6 / 3,121.3 / 67.49 |
    | 100k | 1,590.0 / 1,368.0 / 1,373.2 / 1,324.2 / 48.64 | 2,868.8 / 2,689.4 / 2,611.9 / 2,578.2 / 59.63 |
    | 118k | | 2,500.0 / 2,490.9 / 2,436.4 / 2,402.5 / 57.19 |
    | 150k | 1,145.7 / 1,013.1 / 1,032.5 / 1,006.5 / 41.66 | |
    | 200k | 895.2 / 807.8 / 828.7 / 808.2 / 36.43 | |
    | 249k | 738.8 / 667.7 / 692.9 / 680.0 / 32.42 | |

  - Qwen's cumulative prefill to 249k: 2.6 min. On the M3 Max at PRI 31 it was 59.7 min.
  - Against the M3 Max at PRI 31, the same depths: prefill to 249k 59.7 / 2.6 = 23 times; decode 65.68 / 14.99 = 4.38
    at 16k, 57.95 / 13.52 = 4.29 at 50k, 48.64 / 10.36 = 4.70 at 100k, 41.66 / 8.99 = 4.63 at 150k,
    36.43 / 7.82 = 4.66 at 200k and 32.42 / 6.93 = 4.68 at 249k.
  - Against the RTX PRO 6000 server (section 1a, same build), Qwen's Δ2000 is 3,366.4 against 3,909 at 16k (86%) and
    1,373.2 against 1,767 at 100k (78%). Decode is 65.68 against 63.8 at 16k, and 48.64 against 49.6 at 100k.
  - Aggregate decode tok/s by stream count:
    - Qwen at 32k with 4 streams: 124.02, single 62.98, ×1.97. At 64k: 1 → 55.19, 2 → 77.62, 4 → 95.52. At 128k:
      1 → 44.29, 2 → 57.77. At 260k: 1 → 31.83.
    - Glimmer at 32k with 4 streams: 129.43, single 71.47, ×1.81. At 64k: 1 → 65.13, 2 → 92.15, 4 → 110.75,
      8 → 211.72, 16 → 250.27.
