# Parallel decode at depth 65536: apple-m5-max-64g-q27b-depth64k

parallel_depth 1.1; model Qwen3.8-27B-Q4_K_M.gguf; build b11087-c21284cdf; 128 tokens per stream.

One-time prefill of 65536 tokens: 260.3 tok/s.

| Streams | Aggregate decode, tok/s | Mean per stream, tok/s | Gain over one stream | Restore reused |
|---:|---:|---:|---:|---|
| 1 | 16.297 | 16.3 | 1.0 | True |
| 2 | 21.106 | 10.55 | 1.295 | True |
| 4 | 25.466 | 6.37 | 1.563 | True |
| 8 | 27.442 | 3.43 | 1.684 | True |

Aggregate: timed decode steps of all streams divided by the longest server decode interval. A round with restore_reused false re-read more than the suffix; treat its numbers with care.
