# Parallel decode at depth 131072: apple-m5-max-64g-q27b-depth128k

parallel_depth 1.1; model Qwen3.8-27B-Q4_K_M.gguf; build b11087-c21284cdf; 128 tokens per stream.

One-time prefill of 131072 tokens: 165.7 tok/s.

| Streams | Aggregate decode, tok/s | Mean per stream, tok/s | Gain over one stream | Restore reused |
|---:|---:|---:|---:|---|
| 1 | 12.891 | 12.89 | 1.0 | True |
| 2 | 15.509 | 7.75 | 1.203 | True |
| 4 | 18.057 | 4.51 | 1.401 | True |

Aggregate: timed decode steps of all streams divided by the longest server decode interval. A round with restore_reused false re-read more than the suffix; treat its numbers with care.
