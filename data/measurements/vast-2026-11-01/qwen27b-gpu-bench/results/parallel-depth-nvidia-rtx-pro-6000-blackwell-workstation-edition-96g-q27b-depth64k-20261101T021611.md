# Parallel decode at depth 65536: nvidia-rtx-pro-6000-blackwell-workstation-edition-96g-q27b-depth64k

parallel_depth 1.1; model Qwen3.8-27B-Q4_K_M.gguf; build b11087-c21284cdf; 128 tokens per stream.

One-time prefill of 65536 tokens: 1889.9 tok/s.

| Streams | Aggregate decode, tok/s | Mean per stream, tok/s | Gain over one stream | Restore reused |
|---:|---:|---:|---:|---|
| 1 | 42.052 | 42.05 | 1.0 | True |
| 2 | 56.593 | 28.3 | 1.346 | True |
| 4 | 66.287 | 16.57 | 1.576 | True |
| 8 | 101.854 | 12.73 | 2.422 | True |
| 16 | 114.775 | 7.17 | 2.729 | True |

Aggregate: timed decode steps of all streams divided by the longest server decode interval. A round with restore_reused false re-read more than the suffix; treat its numbers with care.
