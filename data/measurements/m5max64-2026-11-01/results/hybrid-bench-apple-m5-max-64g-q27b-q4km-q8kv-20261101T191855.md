| depth | segment prefill tok/s | Δ512 prefill tok/s | Δ2000 prefill tok/s | Δ10000 prefill tok/s | decode tok/s (at depth) |
|---|---|---|---|---|---|
| 16k (cum. 0.5 min) | 586.4 | 372.8 | 394.2 | 372.4 | 23.13 |
| 50k (cum. 1.8 min) | 268.7 | 257.7 | 212.0 | 206.1 | 19.81 |
| 100k (cum. 5.9 min) | 150.6 | 122.2 | 119.4 | 114.8 | 14.56 |
| 150k (cum. 12.4 min) | 95.1 | 83.7 | 82.0 | 79.4 | 12.24 |
| 200k (cum. 21.2 min) | 69.7 | 64.7 | 62.7 | 61.0 | 10.56 |
| 249k (cum. 32.2 min) | 55.0 | 52.4 | 50.8 | 50.0 | 9.25 |
slot save at 16k: 714 MB = 43.6 KiB/token, 87.22 ms
slot save at 50k: 1899 MB = 37.1 KiB/token, 218.073 ms
slot save at 100k: 3641 MB = 35.6 KiB/token, 344.394 ms
slot save at 150k: 5383 MB = 35.0 KiB/token, 549.151 ms
slot save at 200k: 7126 MB = 34.8 KiB/token, 721.195 ms
slot save at 249k: 8833 MB = 34.6 KiB/token, 831.376 ms
