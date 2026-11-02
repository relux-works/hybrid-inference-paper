| depth | segment prefill tok/s | Δ512 prefill tok/s | Δ2000 prefill tok/s | Δ10000 prefill tok/s | decode tok/s (at depth) |
|---|---|---|---|---|---|
| 16k (cum. 0.1 min) | 3756.4 | 1599.6 | 2875.6 | 3263.1 | 61.87 |
| 50k (cum. 0.2 min) | 2895.2 | 1416.8 | 2286.8 | 2437.2 | 55.98 |
| 100k (cum. 0.5 min) | 2118.1 | 1190.0 | 1731.4 | 1776.3 | 48.74 |
| 150k (cum. 0.9 min) | 1587.4 | 997.0 | 1352.3 | 1387.8 | 43.04 |
| 200k (cum. 1.4 min) | 1266.2 | 842.3 | 1111.7 | 1142.8 | 38.51 |
| 249k (cum. 1.9 min) | 1055.9 | 741.6 | 946.3 | 972.7 | 34.72 |
slot save at 16k: 714 MB = 43.6 KiB/token, 206.802 ms
slot save at 50k: 1899 MB = 37.1 KiB/token, 538.839 ms
slot save at 100k: 3641 MB = 35.6 KiB/token, 1055.696 ms
slot save at 150k: 5383 MB = 35.0 KiB/token, 1512.738 ms
slot save at 200k: 7126 MB = 34.8 KiB/token, 2220.887 ms
slot save at 249k: 8833 MB = 34.6 KiB/token, 2646.475 ms
