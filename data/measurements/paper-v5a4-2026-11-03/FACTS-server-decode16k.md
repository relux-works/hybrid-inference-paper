- **vLLM decode batching at 16k on the RTX PRO 6000 Workstation, measured; kit 1.6.9 `924a72af`, Muse r7ar ACCEPT;
  Vast node G, New York, 2026-11-03 18:40-19:35Z).** vLLM 0.32.0, Qwen3.8-27B-FP8, default KV. Every stream has its own
  context of 16,384 tokens with a private prefix and salt, and generates 256 tokens. Three rounds; median aggregate over
  the common decode interval. Evidence: `.temp/evidence/vllm-pro-g169-261103/`.

  | Streams | Aggregate tok/s | Per stream | TTFT median s | Gain |
  |---|---|---|---|---|
  | 1 | 48.72 | 48.72 | 0.111 | x1.00 |
  | 8 | 302.98 | 37.87 | 0.725 | x6.22 |
  | 32 | 686.80 | 21.46 | 2.431 | x14.10 |
  | 39 (largest resident) | 738.10 | 18.93 | 2.520 | x15.15 |

  - FP8 KV did not start on this card: `No supported CUDA architectures found for major versions [9, 10, 12]`.
  - The stage failed afterwards at 64k and is not complete. N = 1 at 64k was measured. The concurrent probes refused,
    because vLLM merged several tokens into one SSE chunk and the kit then required one token per chunk. Kit 1.6.11
    (dev-a r39h) counts tokens exactly in merged chunks, and the whole grid will be rerun. These 16k rows passed the
    kit's own checks.
