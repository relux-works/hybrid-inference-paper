| depth | segment prefill tok/s | Δ512 prefill tok/s | Δ2000 prefill tok/s | Δ10000 prefill tok/s | decode tok/s (at depth) |
|---|---|---|---|---|---|
| 16k (cum. 0.1 min) | 3935.2 | 3509.4 | 3547.4 | 3435.4 | 61.81 |
| 50k (cum. 0.2 min) | 2963.3 | 2509.2 | 2567.2 | 2513.9 | 55.96 |
| 100k (cum. 0.5 min) | 2135.4 | 1734.0 | 1741.1 | 1790.7 | 48.65 |
| 150k (cum. 0.9 min) | 1596.3 | 1306.4 | 1325.1 | 1392.8 | 43.02 |
| 200k (cum. 1.3 min) | 1271.7 | 1066.6 | 1075.4 | 1143.5 | 38.5 |
| 249k (cum. 1.9 min) | 1061.5 | 898.3 | 905.1 | 971.0 | 34.64 |
slot save at 16k: 714 MB = 43.6 KiB/token, 204.97 ms
slot save at 50k: 1899 MB = 37.1 KiB/token, 540.638 ms
slot save at 100k: 3641 MB = 35.6 KiB/token, 1059.042 ms
slot save at 150k: 5383 MB = 35.0 KiB/token, 1748.405 ms
slot save at 200k: 7126 MB = 34.8 KiB/token, 3385.21 ms
slot save at 249k: 8833 MB = 34.6 KiB/token, 2728.522 ms
