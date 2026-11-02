# Parallel decode at depth 131072: nvidia-rtx-pro-6000-blackwell-workstation-edition-96g-q27b-depth128k

parallel_depth 1.1; model Qwen3.8-27B-Q4_K_M.gguf; build b11087-c21284cdf; 128 tokens per stream.

One-time prefill of 131072 tokens: 1387.7 tok/s.

| Streams | Aggregate decode, tok/s | Mean per stream, tok/s | Gain over one stream | Restore reused |
|---:|---:|---:|---:|---|
| 1 | 33.16 | 33.16 | 1.0 | True |
| 2 | 41.359 | 20.68 | 1.247 | True |
| 4 | 46.255 | 11.56 | 1.395 | True |
| 8 | 61.261 | 7.66 | 1.847 | True |

Aggregate: timed decode steps of all streams divided by the longest server decode interval. A round with restore_reused false re-read more than the suffix; treat its numbers with care.
