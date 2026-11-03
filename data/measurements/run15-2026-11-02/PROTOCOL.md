# Owner-supplied protocol

Source: /home/agent/lanes/hybrid/.temp/paper-v2/FACTS.md :: Kit1.6.6 cooled parallel sweep, supplied2026-11-02

  - **Kit 1.6.6 cooled parallel sweep, M3 Max 128 GB, Qwen3.8-27B Q4_K_M, llama.cpp `dde879bc`, incident lane,
    2026-11-02 ~10:55-13:40Z.** Archive sha256 916891bd...d618, in `.temp/mac-results-261102/qwen27-kit166-scaling.tar.gz`.
    - Protocol: fill once per depth, a 300 s pause, then restore the slot before every round. Median of 3 rounds, no
      re-reads. The server ran with the largest fitting np.
    - Aggregate decode tok/s by stream count:

      | Depth | 1 | 2 | 4 | 8 | 12 | 16 | 24 | 32 |
      |---|---|---|---|---|---|---|---|---|
      | 32k | 8.77 | 14.66 | 24.03 | 33.40 | 38.47 | 44.41 | 43.50 | 47.83 |
      | 64k | 6.42 | 9.89 | 20.08 | 29.97 | 30.60 | 33.97 | 32.93 | 35.56 |
      | 128k, np 16 | 5.38 | 9.37 | 14.35 | 18.93 | 19.77 | 20.22 | | |

    - np control at 128k: 4 streams on a server started with np 4 give 16.03, against 14.35 under np 16.
    - Against step 55 (old build `c21284cd`, rounds right after a long prefill), the curve is smooth: the old jump
      between 8 and 16 streams at 64k is gone. At 8 streams, 64k gives 29.97 against 15.6 and 128k gives 18.93 against
      10.1.
    - Single-stream rounds vary: at 128k, 3.6/5.4/6.0.

Archive kit.log uses UTC06:46-09:40Z and JSONL filenames use10:46-13:38 labels. FACTS labels approximately10:55-13:40Z; labels are retained, not silently reconciled. No rerun or thermal telemetry is inferred.
