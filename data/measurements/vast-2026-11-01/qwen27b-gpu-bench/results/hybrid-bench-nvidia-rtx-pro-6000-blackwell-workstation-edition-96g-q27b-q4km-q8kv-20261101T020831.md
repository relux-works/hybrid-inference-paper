| depth | segment prefill tok/s | Δ512 prefill tok/s | Δ2000 prefill tok/s | Δ10000 prefill tok/s | decode tok/s (at depth) |
|---|---|---|---|---|---|
| 16k (cum. 0.1 min) | 2497.3 | 1712.9 | 2147.3 | 2140.9 | 52.36 |
| 50k (cum. 0.3 min) | 1795.6 | 1293.6 | 1503.8 | 1476.1 | 44.44 |
| 100k (cum. 0.8 min) | 1225.1 | 926.1 | 1032.4 | 1017.8 | 36.35 |
| 150k (cum. 1.5 min) | 892.5 | 712.5 | 785.4 | 780.2 | 30.74 |
| 200k (cum. 2.4 min) | 702.5 | 581.0 | 631.8 | 631.2 | 26.74 |
| 249k (cum. 3.4 min) | 580.1 | 492.5 | 533.0 | 531.7 | 23.66 |
slot save at 16k: 714 MB = 43.6 KiB/token, 736.428 ms
slot save at 50k: 1899 MB = 37.1 KiB/token, 1266.195 ms
slot save at 100k: 3641 MB = 35.6 KiB/token, 1977.332 ms
slot save at 150k: 5383 MB = 35.0 KiB/token, 2621.921 ms
slot save at 200k: 7126 MB = 34.8 KiB/token, 2181.164 ms
slot save at 249k: 8833 MB = 34.6 KiB/token, 3287.173 ms
