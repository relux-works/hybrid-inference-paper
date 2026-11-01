# Reference run: Apple M3 Max, 128 GB (2026-10-30)

Machine: MacBook Pro, Apple M3 Max (40-core GPU), 128 GB, macOS 27.2, on AC power. Other applications ran during
the measurement, so the machine was not fully idle.

Engine: llama.cpp build 11087, commit `c21284cdf5fd833b90ac1f824cdf8065e2700dc4`, Metal, all layers on the GPU, flash
attention on, KV cache q8_0. Model: `Qwen3.8-27B-Q4_K_M.gguf`, 18,973,870,432 bytes, SHA-256
`31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34`. Script: `hybrid_bench.py` 1.1.

## Depth run (one slot, context 262,144)

| Depth | Marginal prefill | Turn prefill 512 / 2k / 10k | Decode after 512 / 2k / 10k | Slot size |
|---|---:|---:|---:|---:|
| 16k | 173.6 tok/s | 132.1 / 163.4 / 144.1 tok/s | 7.48 / 8.47 / 8.82 tok/s | 0.714 GB |
| 50k | 93.7 tok/s | 71.5 / 75.6 / 70.6 tok/s | 7.54 / 7.78 / 7.54 tok/s | 1.899 GB |
| 100k | 49.9 tok/s | 40.0 / 46.5 / 41.9 tok/s | 6.98 / 6.59 / 5.30 tok/s | 3.641 GB |
| 150k | 41.2 tok/s | 37.2 / 42.4 / 38.5 tok/s | 6.79 / 5.43 / 6.18 tok/s | 5.383 GB |
| 200k | 27.7 tok/s | 28.9 / 34.8 / 26.7 tok/s | 4.34 / 6.00 / 5.34 tok/s | 7.126 GB |
| 249k | 22.2 tok/s | 22.8 / 24.5 / 20.8 tok/s | 5.44 / 5.25 / 4.82 tok/s | 8.833 GB |

The decode rate is the server's `timings.predicted_per_second`.

## Four parallel streams at 32k (`-np 4 -c 140000`)

| Metric | Value |
|---|---:|
| Single-stream decode | 8.44 tok/s |
| Per stream with four running | 3.51 tok/s |
| Aggregate decode, four streams | 14.05 tok/s |
| Gain over one stream | 1.665× |

The depth run took about two hours and the parallel run about 17 minutes.
