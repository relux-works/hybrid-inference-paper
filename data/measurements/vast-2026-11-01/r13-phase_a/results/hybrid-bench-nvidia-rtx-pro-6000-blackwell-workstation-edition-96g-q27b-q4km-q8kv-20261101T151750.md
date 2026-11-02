| depth | segment prefill tok/s | Δ512 prefill tok/s | Δ2000 prefill tok/s | Δ10000 prefill tok/s | decode tok/s (at depth) |
|---|---|---|---|---|---|
| 16k (cum. 0.1 min) | 3933.3 | 3509.6 | 3548.2 | 3433.8 | 61.87 |
| 50k (cum. 0.2 min) | 2963.5 | 2510.8 | 2569.0 | 2513.6 | 56.02 |
| 100k (cum. 0.5 min) | 2135.5 | 1732.4 | 1747.3 | 1792.3 | 48.71 |
| 150k (cum. 0.9 min) | 1598.1 | 1315.9 | 1328.8 | 1392.1 | 42.98 |
| 200k (cum. 1.3 min) | 1271.5 | 1062.6 | 1074.6 | 1142.2 | 38.51 |
| 249k (cum. 1.9 min) | 1062.0 | 870.7 | 906.6 | 972.3 | 34.69 |
slot save at 16k: 714 MB = 43.6 KiB/token, 205.982 ms
slot save at 50k: 1899 MB = 37.1 KiB/token, 543.952 ms
slot save at 100k: 3641 MB = 35.6 KiB/token, 1034.389 ms
slot save at 150k: 5383 MB = 35.0 KiB/token, 1572.426 ms
slot save at 200k: 7126 MB = 34.8 KiB/token, 2461.765 ms
slot save at 249k: 8833 MB = 34.6 KiB/token, 3689.011 ms
