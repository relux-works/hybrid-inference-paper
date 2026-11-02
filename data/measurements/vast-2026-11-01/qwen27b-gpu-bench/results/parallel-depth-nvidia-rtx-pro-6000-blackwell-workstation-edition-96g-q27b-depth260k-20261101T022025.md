# Parallel decode at depth 260000: nvidia-rtx-pro-6000-blackwell-workstation-edition-96g-q27b-depth260k

parallel_depth 1.1; model Qwen3.8-27B-Q4_K_M.gguf; build b11087-c21284cdf; 128 tokens per stream.

One-time prefill of 260000 tokens: 899.8 tok/s.

| Streams | Aggregate decode, tok/s | Mean per stream, tok/s | Gain over one stream | Restore reused |
|---:|---:|---:|---:|---|
| 1 | 23.233 | 23.23 | 1.0 | True |
| 2 | 26.841 | 13.42 | 1.155 | True |
| 4 | 28.878 | 7.22 | 1.243 | True |
| 8 | 34.15 | 4.27 | 1.47 | True |

Aggregate: timed decode steps of all streams divided by the longest server decode interval. A round with restore_reused false re-read more than the suffix; treat its numbers with care.
