# Models, APIs and price trends (research note, 2026-10-30)

Scope: four questions for the inference-economics study. Primary sources only where possible: Hugging Face model cards, `config.json` files and the Hub API, vendor docs, the OpenRouter API, and Artificial Analysis (AA) pages, with Wayback snapshots used for older AA index versions.

Conventions:
- **Estimate** = my own calculation or inference. Everything else is quoted or copied from the cited source.
- **Not found** = I searched and found no primary statement.
- OpenRouter data was pulled from `https://openrouter.ai/api/v1/models` and the `/endpoints` URLs on 2026-10-30 between 02:48 and 03:05 UTC. OpenRouter prices are stored per token; below they are converted to USD per 1M tokens (×1e6). Prices change often.
- Hugging Face checkpoint sizes are byte sums of `.safetensors`/`.gguf` files from `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`.

---

## 1. GLM-5.3-Flash (Z.ai / Zhipu)

### 1.1 Does it exist, and is "320B total / 18B active" right?
Yes, the model exists, and the owner's numbers are correct.
- HF model card, https://huggingface.co/zai-org/GLM-5.3-Flash: "With 320B total parameters and just 18B active parameters, it outperforms GLM-5.2 across benchmarks and real-world workloads at one-tenth the price, while approaching Claude Opus 4.8 on coding and agentic benchmarks."
- Z.ai docs, https://docs.z.ai/guides/llm/glm-5.3-flash: "GLM-5.3-Flash has 320B total parameters with 18B activated."
- HF Hub API, https://huggingface.co/api/models/zai-org/GLM-5.3-Flash: `"safetensors": {"parameters": {"BF16": 6926096640, "F8_E4M3": 314396639232, "F32": 295518}, "total": 321323031390}`. The count is 321.3B because it includes the vision tower and the MTP layer.
- vLLM recipe, https://recipes.vllm.ai/zai-org/GLM-5.3-Flash: "approximately 321B total parameters and 18B active parameters per token. Its 45-layer language model combines KDA linear-attention layers with NoPE sparse MLA layers, routes each token through 8 of 288 experts".
- **Estimate (check against the config):** routed experts 42 × 288 × 3 × 4096 × 2048 ≈ 304.4B, plus shared and dense MLPs ≈ 1.5B, attention ≈ 6.0B, the MTP layer ≈ 7.4B, embeddings and LM head ≈ 1.3B, and vision ≈ 0.6B, for ≈ 321B in total. Active: 8 experts × 42 layers ≈ 8.5B, plus the shared expert ≈ 1.1B, dense MLPs 0.45B, attention ≈ 6.0B and embeddings/head ≈ 1.3B, for ≈ 17–18B. Both totals match the published figures.

### 1.2 Release date
- **2026-08-26.** Z.ai release notes, https://docs.z.ai/release-notes/new-released: "**2026-08-26** GLM-5.3-Flash … Efficient hybrid architecture: Combines linear and sparse attention with 320B total parameters and 18B activated".
- Corroborating dates: the HF repo `createdAt` is "2026-08-25T06:43:14.000Z" (repo creation; this can come before the public release). The Transformers doc says "This model was contributed to Hugging Face Transformers on 2026-08-26." On OpenRouter, `"created": 1787752741` = 2026-08-26 13:59 UTC and `"canonical_slug": "z-ai/glm-5.3-flash-20260826"`. AA: "released on August 26, 2026".
- The docs page also says: "Before release, we tested GLM-5.3-Flash anonymously as ox-alpha on OpenCode and OpenRouter".

### 1.3 Architecture (from `config.json` → `text_config`)
Source: https://huggingface.co/zai-org/GLM-5.3-Flash/blob/main/config.json (`"architectures": ["Glm5NextForConditionalGeneration"]`, `"model_type": "glm5_next"`). This main repo holds the **FP8** checkpoint (`"quant_method": "fp8"`, `"fmt": "e4m3"`, `"weight_block_size": [128,128]`). A BF16 copy is published as `zai-org/GLM-5.3-Flash-BF16`.

| Field | Value |
|---|---|
| num_hidden_layers | 45 (plus `num_nextn_predict_layers: 1`, an MTP layer) |
| layer_types | 34 × `"linear_attention"` + 11 × `"deepseek_sparse_attention"`. Pattern: 3 linear + 1 sparse, repeated; sparse at layers 3, 7, …, 43; layer 44 is linear |
| linear_attn_config | `num_heads: 64`, `head_dim: 128`, `short_conv_kernel_size: 4`, `gate_lower_bound: -5.0`. `kda_layers` lists the 34 linear layers and `full_attn_layers: [3,7,11,15,19,23,27,31,35,39,43]` |
| Attention type | **Hybrid.** Linear layers are **KDA** (Kimi Delta Attention). Sparse layers are **MLA with DeepSeek Sparse Attention (DSA) indexer**, **NoPE** (no RoPE) |
| num_attention_heads / num_key_value_heads | 64 / 64 (MLA; the cache holds the shared latent, not per-head K/V) |
| head_dim | `0` (Transformers sets `head_dim = qk_rope_head_dim`). `qk_head_dim: 256` (`qk_nope_head_dim: 256` + `qk_rope_head_dim: 0`), `v_head_dim: 256` |
| kv_lora_rank / q_lora_rank | 512 / 1536 |
| qk_rope_head_dim | **0**, with `mla_use_nope: true` |
| Indexer (DSA) | `index_n_heads: 32`, `index_head_dim: 128`, `index_topk: 2048`, `index_kpool: 4`, `index_kpool_compress: true`, `index_kpool_always_select_tail: true`, `index_share_for_mtp_iteration: true`, `indexer_types`: all `"full"` |
| MoE | `n_routed_experts: 288`, `num_experts_per_tok: 8`, `n_shared_experts: 1`, `moe_intermediate_size: 2048`, `first_k_dense_replace: 3` (layers 0–2 dense, `intermediate_size: 12288`), `scoring_func: "sigmoid"`, `topk_method: "noaux_tc"`, `routed_scaling_factor: 2.5` |
| Residual | `mhc: true`, `hc_mult: 4`, `hc_sinkhorn_iters: 20` (Manifold-Constrained Hyper-Connections) |
| hidden_size / vocab_size | 4096 / 154880 |
| max_position_embeddings | **1048576** |
| Vision | `vision_config.depth: 24`, `hidden_size: 1024`, `patch_size: 14` |

Supporting quotes:
- Transformers config docstring (https://github.com/huggingface/transformers/blob/main/src/transformers/models/glm5_next/configuration_glm5_next.py): "`"linear_attention"` for KDA layers and `"indexed_attention"` for MLA (DSA) layers". On `index_kpool`: "Pool size of the compressed token groups selected by the DSA indexer". The config check raises "Expecting NoPE for the DSA attention layers" if `qk_rope_head_dim > 0`.
- Modeling code (`modeling_glm5_next.py`, same directory): "Kimi-style KDA (Kimi Linear Attention) for GLM-5.3-Flash." and "DeepSeek Sparse Attention (DSA) indexer with k-pool compression for GLM-5.3-Flash." In MLA: "Cache read / write is performed while latent KV is still compressed".
- Z.ai docs: "we introduce IndexPool, which compresses four indexer key vectors into one through weighted pooling." Also: "Despite a similar total parameter count (320B vs. 355B), it nearly halves both the activated parameter count (18B vs. 32B) and the number of layers (45 vs. 92)." The baseline is not named. **Estimate:** 355B/32B/92 layers matches GLM-4.5/4.6/4.7 (GLM-4.7 `config.json`: `num_hidden_layers: 92`; Hub total 358,337,791,296). It does not match GLM-5.3, which is 753B/40B with 78 layers.

### 1.4 Context: native vs extended
- Config: `max_position_embeddings: 1048576`. There is no `rope_scaling`/`rope_theta`. Text attention is NoPE, and the Transformers code passes `position_embeddings=None` to text layers. So no YaRN-style extension exists or is needed; 1M is the declared native maximum.
- Z.ai docs: "Context Length 1M", "Maximum Output Tokens 128K", and "Text parameters are consistent with GLM-5.3, with support for a 1M-token context window."
- OpenRouter: `"context_length": 1048576`, `"max_completion_tokens": 131072`.
- **Not found:** the context length used in pre-training or long-context training.

### 1.5 KV cache per token at 8-bit (estimate)
Formula. Only the 11 sparse (MLA/DSA) layers keep a per-token cache. The 34 KDA layers keep a fixed-size recurrent state per sequence.

```
KV_bytes/token = N_dsa × [ (kv_lora_rank + qk_rope_head_dim) + index_head_dim / index_kpool ] × bytes_per_value
               = 11 × [ (512 + 0) + 128/4 ] × 1 B
               = 11 × 544 = 5,984 B ≈ 5.8 KiB per token  (8-bit)
```
| Variant (8-bit) | Bytes/token |
|---|---:|
| MLA latent only, no indexer cache (lower bound) | 11 × 512 = **5,632** |
| + indexer keys pooled 4:1 (IndexPool) — main estimate | **5,984** |
| + indexer keys not pooled (DeepSeek-V3.2-style, one 128-d key per token) | 7,040 |
| + MTP draft layer cached (12 sparse layers; mlx-community lists layer 45 as a sparse-attention layer) | 6,528 |
| FP8 with per-128 FP32 scales (DeepSeek FlashMLA-style layout: 512+16 B latent, (128+4)/4 B indexer) | ≈ 6,171 |
| BF16 (2× main estimate) | 11,968 |

Per sequence at 8-bit with the 5,984 B/token estimate: 32K tokens → 0.196 GB; 128K → 0.78 GB; 262,144 → 1.57 GB; **1,048,576 → 6.27 GB (5.84 GiB)**.

Fixed per-sequence state of the KDA layers: 34 × 64 heads × 128 × 128 = 35,651,584 values. That is 142.6 MB in FP32 (Transformers stores it as `torch.float32`), 71.3 MB in BF16, or 35.7 MB at 8-bit. The conv state adds about 34 × 24,576 × 3 ≈ 2.5M values (≈5 MB in BF16). **Estimate:** below about 24K tokens per sequence, the FP32 KDA state is larger than the 8-bit MLA cache. The fixed per-request state therefore dominates memory for short, high-concurrency traffic.

Cross-checks:
- Z.ai claims "reducing attention computation and KV cache by 3.01× and 4.44× versus GLM-5.3". Their method: "we calculate the attention compute per head per layer and average KV cache size per layer (BF16)". Figure: https://cloud-document-converter.oss-cn-beijing.aliyuncs.com/feishu2md/20260826/1787756367780-5fet8o.png. **Estimate:** GLM-5.3 (`config.json`: 78 layers, `kv_lora_rank` 512, `qk_rope_head_dim` 64) stores 576 values per layer. GLM-5.3-Flash averages 5,632/45 to 5,984/45 = 125–133 values per layer. That gives a ratio of 4.3–4.6×, consistent with the 4.44× claim. Per token over the whole model, the ratio is larger: GLM-5.3 at 78 × (512+64+128) = 54,912 B is 9.2× Flash.
- vLLM recipe (AMD section): "At TP=4 the FP8 checkpoint reports a 14.92M-token KV pool and ~113.81x max concurrency at 128K context; the BF16 checkpoint reports an 8.87M-token KV pool at the same TP and context." **Estimate:** the FP8 and BF16 weights differ by 292.7 GiB, about 78.6 GB per GPU. That memory buys 6.05M extra tokens, or about 13.0 KB per token per GPU with BF16 KV (the AMD command does not pass `--kv-cache-dtype fp8`). This matches the BF16 formula value of 11,968–14,080 B if the MLA latent is replicated on every TP rank, which is how MLA normally runs under TP.
- vLLM recipe: "Hopper does not support FP8 KV cache for this model and must run BF16 KV." On Blackwell, `--kv-cache-dtype fp8` is shown.
- Z.ai's own serving uses "hybrid INT8/FP8/BF16 cache quantization" (docs page).
- For scale (8-bit, **estimates** from each `config.json`): GLM-4.7 (GQA, 92 layers × 2 × 8 KV heads × 128) = 188,416 B/token, 31× Flash. Qwen3.8-27B (16 full-attention layers × 2 × 4 × 256) = 32,768 B/token. Qwen3.8-Flash-Next (12 QSA layers × 2 × 2 × 256, plus indexer 12 × 128/4) ≈ 12,672 B/token.

### 1.6 Published quantized sizes
Sums of file sizes from the HF tree API:

| Repo | Variant | Size |
|---|---|---:|
| zai-org/GLM-5.3-Flash (official) | FP8 (62 shards) | 328.3 GB (305.8 GiB). vLLM: "about 306 GiB for the default native FP8 checkpoint before runtime and KV-cache overhead" |
| zai-org/GLM-5.3-Flash-BF16 | BF16 | 642.7 GB |
| unsloth/GLM-5.3-Flash-GGUF | UD-Q4_K_XL | **199.7 GB (186.0 GiB)** |
| unsloth/GLM-5.3-Flash-GGUF | UD-IQ4_XS | 156.8 GB (146.1 GiB) |
| unsloth/GLM-5.3-Flash-GGUF | Q8_0 / BF16 | 341.0 GB / 641.6 GB (+ mmproj ≈1.1–1.2 GB) |
| ggml-org/GLM-5.3-Flash-GGUF | Q4_K | **181.4 GB (168.9 GiB)** (+ separate `mtp-…-Q4_0.gguf` 4.9 GB, mmproj Q8_0 0.65 GB) |
| bartowski/GLM-5.3-Flash-BF16-GGUF | Q4_K_M / Q4_K_S / IQ4_XS / Q4_0 | 200.8 / 189.3 / 177.7 / 184.1 GB |
| mlx-community/GLM-5.3-Flash-4bit | MLX "mixed 4/5/6-bit, group size 64" | **203,992,076,296 bytes (190 GiB)**. Card: "It needs a Mac with 256 GB of memory or more." Linear-attention layers, indexer, router, mHC, embeddings and head are kept in bf16 |
| pipenetwork/GLM-5.3-Flash-MLX-4bit | MLX 4-bit | 177.5 GB (165.4 GiB) |
| nvidia/GLM-5.3-Flash-NVFP4 | NVFP4 | 204.4 GB (190.4 GiB) |

### 1.7 Prices
Z.ai first-party price list (https://docs.z.ai/guides/overview/pricing, "Prices per 1M tokens"): `GLM-5.3-Flash | $0.15 | $0.03 | Limited-time Free | $0.50`. The columns are Input | Cached Input | Cached Input Storage | Output. FlashX: `$0.37 | $0.075 | … | $1.25`. GLM-5.3: `$1.4 | $0.26 | … | $4.4`.

OpenRouter, model `z-ai/glm-5.3-flash` (`"hugging_face_id": "zai-org/GLM-5.3-Flash"`), endpoints at https://openrouter.ai/api/v1/models/z-ai/glm-5.3-flash/endpoints. There are 40 endpoints from 35 providers. No endpoint lists a cache-write price. Unit: USD per 1M tokens.

| Provider (tag) | Quant | Input | Output | Cache read | Context | Max out | `discount` |
|---|---|---:|---:|---:|---:|---:|---:|
| Relace | unknown | 0.0477 | 0.0701 | 0.03 | 1048576 | 131072 | 0 |
| Wafer (nvfp4) | nvfp4 | 0.054 | 0.20 | 0.053 | 1048576 | 131072 | 0 |
| OpenInference (fp4) | fp4 | 0.0639 | 0.0687 | 0.0581 | 1048576 | 943718 | 0 |
| Darkbloom (fp4) | fp4 | 0.065 | 0.18 | 0.012 | 262144 | 65536 | 0 |
| Wafer (us) | nvfp4 | 0.07 | 0.20 | 0.069 | 1048576 | 131072 | 0 |
| GMICloud (fp8) | fp8 | 0.075 | 0.25 | 0.015 | 1048576 | 943718 | 0.5 |
| Sail Research (us / fp4) | fp4 | 0.07835 | 0.25 | 0.0261 | 1048576 | 131072 | 0 |
| Near AI (fp8) | fp8 | 0.08 | 0.50 | 0.012 | 1048576 | 943718 | 0 |
| Novita (fp8) | fp8 | 0.084 | 0.28 | 0.0168 | 1048576 | 131072 | 0.44 |
| StreamLake (fp8) | fp8 | 0.0885 | 0.295 | 0.0177 | 1024000 | 128000 | 0.41 |
| InferenceNet (us / fp4) | fp4 | 0.108 | 0.35 | 0.032 | 1048576 | 262144 | 0 |
| DigitalOcean | unknown | 0.1125 | 0.375 | 0.03 | 1048576 | 131072 | 0 |
| Reka | unknown | 0.12 | 0.30 | 0.03 | 1048576 | 943718 | 0 |
| CoreWeave (nvfp4) | nvfp4 | 0.12 | 0.38 | 0.02 | 1048576 | 943718 | 0 |
| NextBit (fp4) | fp4 | 0.12 | 0.48 | 0.04 | 1048576 | 128000 | 0 |
| Phala (nvfp4) | nvfp4 | 0.1275 | 0.425 | 0.0255 | 1048576 | 131072 | 0.15 |
| Morph (fp8) | fp8 | 0.138 | 0.226 | 0.05 | 1048576 | 943718 | 0 |
| Makora | unknown | 0.14 | 0.47 | 0.024 | 1048576 | 131072 | 0 |
| **Z.AI (fp8)** and 17 more endpoints at the same price: Particle AI, Mistral, Cohere, PrimeIntellect, Nebius, Modal, BaseTen (×2), Crusoe, AtlasCloud, Fireworks, Friendli, SiliconFlow (status −2), Together, Parasail, Venice, DeepInfra | mixed | **0.15** | **0.50** | **0.03** | ~1M | 131072–943718 | 0 |
| Inceptron (fp8) | fp8 | 0.17 | 0.60 | 0.06 | 1048576 | 943718 | 0 |
| Fireworks (us) | unknown | 0.225 | 0.75 | 0.045 | 1048576 | 943718 | 0 |

Summary across the 40 endpoints: input min / median / max = 0.0477 / 0.145 / 0.225; output 0.0687 / 0.50 / 0.75; cache read 0.012 / 0.03 / 0.069. The model-level `pricing` in `/api/v1/models` shows the cheapest endpoint: `"prompt": "0.0000000477", "completion": "0.0000000701", "input_cache_read": "0.00000003"`. I did not verify whether listed prices are before or after the `discount` field is applied.

Batch variant `z-ai/glm-5.3-flash:batch`: Sail Research 0.05 / 0.18 / cache read 0.01, and DeepInfra 0.12 / 0.40 / 0.024. The alias `~z-ai/glm-flash-latest` ("always redirects to the latest model in the GLM Flash family") currently has the same price as the base model.

### 1.8 Benchmarks (for context)
- AA Index v4.1.1, from the 2026-08-30 Wayback data: **57.5**. Z.ai docs: "scoring 57 at just \$0.045 per task (discounted)".
- AA Index v5.0, current (https://artificialanalysis.ai/models/glm-5-3-flash): "scores 28 on the Artificial Analysis Intelligence Index". The OpenRouter `benchmarks.artificial_analysis` field shows `"intelligence_index": 27.8, "coding_index": 71.5, "agentic_index": 50.9`, which are v5.0 values.

---

## 2. Qwen3.8-Flash-Next (open weights) vs `qwen3.8-flash` (API)

### 2.1 Open-weight model
- HF: https://huggingface.co/Qwen/Qwen3.8-Flash-Next. License `qwen-community-1.0` (not Apache). Hub `createdAt` 2026-08-24, but the release date is **2026-08-26**: GitHub https://github.com/QwenLM/Qwen3.8-Flash-Next says "2026-08-26: We release Qwen3.8-Flash-Next."
- Card: "Number of Parameters: 125B with 6B activated, plus 51B n-gram embedding and 4B MTP". The Hub safetensors total is 179,999,981,459 (≈180B). "About 125B total, 6B active" is therefore right for the main model, but the full checkpoint is ≈180B.
- Architecture (card and `config.json`): 48 layers. "Hidden Layout: 12 × (3 × (Gated DeltaNet → MoE) → 1 × (Qwen Sparse Attention → MoE))". QSA: "24 for Q and 2 for KV", head dim 256, RoPE dim 64, indexer "MQA with 4 Query Heads and 1 Shared Key Head", indexer head dim 128, "Budget: 512 blocks or 2048 tokens" (config `indexer_compress_ratio: 4`). MoE: 512 experts, "10 Routed + 1 Shared", expert intermediate size 640. `model_type: "qwen4_exp_text"`, architecture `Qwen4ExpForConditionalGeneration`.
- Context: "262,144 natively and extensible up to 1,000,000 tokens" (config `max_position_embeddings: 262144`). The card gives YaRN `factor: 4.0` overrides for 1M.

### 2.2 API model IDs
- Alibaba Cloud Model Studio, https://www.alibabacloud.com/help/en/model-studio/qwen3-8-flash ("Last Updated:Oct 30, 2026"): model invocation ID **`qwen3.8-flash`**. No dated snapshot ID was found on the Model Studio, Aliyun or Qwen Cloud pages.
- Qwen Cloud: https://www.qwencloud.com/models/qwen3.8-flash (`qwen3.8-flash`). `https://www.qwencloud.com/models/qwen3.8-flash-next` returns 404, so there is no separate Flash-Next API page.
- OpenRouter: **`qwen/qwen3.8-flash`**, with `"canonical_slug": "qwen/qwen3.8-flash-20260826"` and **`"hugging_face_id": "Qwen/Qwen3.8-Flash-Next"`**. `created` 1787773060 = 2026-08-26.

### 2.3 Same model? What the sources say
- HF card (primary): "**Qwen3.8-Flash** is the official version based on Qwen3.8-Flash-Next with more production features, e.g., 1M context length by default, official built-in tools."
- GitHub README: "QwenCloud provides first-class support for Qwen3.8-Flash-Next".
- Model Studio and Qwen Cloud text for the API: "It natively supports a million-token context window". The open-weights card says 262,144 native.
- OpenRouter links the API model to the open-weights repo through `hugging_face_id`. AA lists only "Qwen3.8-Flash-Next" (180B / 6B active), priced at the API's $0.15/$0.47.
- **Conclusion:** the API model is officially "based on" the open weights. Documented differences: 1M context by default (vs 262K native plus YaRN), built-in tools, and the Responses/Anthropic API features. **Not found:** any statement on whether the served weights are byte-identical or whether the API runs a further post-trained or different checkpoint. **Estimate:** probably the same base model with serving-side context extension and a tool layer.

### 2.4 Prices for `qwen3.8-flash` (per 1M tokens)
Model Studio international page, USD (the page "only shows the original pricing … excluding any limited-time promotions"):

| Deployment / scope | Input | Output | Input (implicit cache) | Explicit cache creation | Explicit cache read |
|---|---:|---:|---:|---:|---:|
| Singapore (International), Hong Kong, Germany (EU), US (Virginia, "Scope: US") | **0.15** | **0.47** | **0.016** | **0.2** | **0.016** |
| China (Beijing), and the "Scope: Global" rows (Tokyo, Virginia, Frankfurt, HK) | 0.113 | 0.382 | 0.014 | 0.177 | 0.014 |

- CNY list (https://help.aliyun.com/en/model-studio/qwen3-8-flash): Beijing 0.8 / 2.7 / cache hit 0.1 / explicit cache creation 1.25 / explicit hit 0.1. International 1.094 / 3.427 / 0.117 / 1.458 / 0.117.
- Qwen Cloud: Input $0.15, Output $0.47, "Input(Implicit Cache)" $0.016, "Explicit Cache Creation" $0.2, "Explicit Cache Read" $0.016.
- **Tiers by prompt length: none.** Every source shows one flat price over the whole 1M window. No 0–256K / 256K–1M tiers were found for this model.
- OpenRouter (https://openrouter.ai/api/v1/models/qwen/qwen3.8-flash/endpoints) has one provider, Alibaba, with two endpoints. `alibaba`: prompt 0.15, completion 0.47, `input_cache_read` 0.016, `input_cache_write` 0.20. `alibaba/us-east-1`: the same without a cache-write field. `context_length` 1000000, `max_completion_tokens` 131072, `max_prompt_tokens` 983616.

### 2.5 API context limits (Model Studio)
Max input 991,808; max output 131,072; max input in thinking mode 983,616; context window 1,000,000; "Max Chain-of-Thought Length" 262,144. Qwen Cloud lists TPM 2,500,000. Model Studio global deployments list RPM 30,000 and TPM 5,000,000.

### 2.6 Qwen3.8-27B: API vs open weights, OpenRouter providers
- HF card (https://huggingface.co/Qwen/Qwen3.8-27B): "**Qwen3.8-27B** will be available as a hosted version with more production features, e.g., 1M context length by default, official built-in tools. … The service is coming soon." The hosted model is now live as `qwen3.8-27b`.
- Open weights: dense 27B, 64 layers, "16 × (3 × (Gated DeltaNet → FFN) → 1 × (Gated Attention → FFN))", Gated Attention "24 for Q and 4 for KV", head dim 256, "262,144 natively and extensible up to 1,000,000 tokens". Apache-2.0.
- Model Studio (https://www.alibabacloud.com/help/en/model-studio/qwen3-8-27b), USD per 1M:
  - Singapore (International): input 0.5, output 3, implicit cache 0.1, explicit cache creation 0.625, explicit cache read 0.05.
  - China (Beijing): 0.424, 1.696, 0.085, 0.53, 0.042.
  - Context window 1,000,000. No length tiers.
  - Qwen Cloud: same International prices.
- OpenRouter `qwen/qwen3.8-27b` (https://openrouter.ai/api/v1/models/qwen/qwen3.8-27b/endpoints) has 21 providers. USD per 1M:

| Provider | Quant | Input | Output | Cache read | Cache write | Context |
|---|---|---:|---:|---:|---:|---:|
| Darkbloom | fp4 | 0.035 | 1.50 | 0.0175 | – | 262144 |
| Chutes | fp8 | 0.039 | 1.25 | 0.0039 | – | 262144 |
| Near AI | fp8 | 0.04 | 1.35 | 0.018 | – | 262144 |
| Ionstream | fp8 | 0.04 | 1.95 | 0.02 | – | 262144 |
| Reka | fp8 | 0.04 | 2.20 | 0.02 | – | 262144 |
| Modal | unknown | 0.04 | 2.30 | 0.02 | – | 262144 |
| DekaLLM | unknown | 0.04 | 2.50 | 0.02 | – | 262144 |
| Wafer | fp8 | 0.06 | 2.30 | 0.059 | – | 262144 |
| DeepInfra | bf16 | 0.15 | 1.875 | 0.0375 | – | 262144 (`discount` 0.25) |
| Tenstorrent | fp4 | 0.15 | 2.00 | 0.05 | – | 262144 |
| Mancer 2 | fp8 | 0.18 | 2.50 | – | – | 262144 (status −2) |
| ModelRun | fp4 | 0.20 | 2.50 | 0.09 | – | 262144 |
| Phala | unknown | 0.20 | 2.50 | 0.05 | – | 1000000 |
| AkashML | fp8 | 0.225 | 1.98 | 0.05 | – | 262144 |
| Parasail | fp8 | 0.24 | 2.20 | 0.05 | – | 262144 |
| CoreWeave | fp8 | 0.40 | 3.00 | 0.15 | – | 262144 |
| Novita | unknown | 0.42 | 3.00 | 0.085 | – | 1000000 |
| **Alibaba** | unknown | **0.425** | **2.55** | **0.085** | **0.53125** | 1000000 |
| Cloudflare | unknown | 0.45 | 3.20 | 0.05 | – | 262144 |
| Venice | fp8 | 0.45 | 3.20 | – | – | 262144 |
| Cerebras | fp16 | 0.99 | 1.49 | 0.99 | – | 65536 |

Medians: input 0.18, output 2.30, cache read 0.05. **Estimate:** OpenRouter's Alibaba endpoint price is exactly 0.85 × the Model Studio International list (0.5→0.425, 3→2.55, 0.1→0.085, 0.625→0.53125). Most third-party hosts serve the native 262K window, and only Alibaba, Novita and Phala offer 1M.

---

## 3. Release timeline and capability of the ~27B class

### 3.1 Timeline (primary sources)
GitHub News at https://github.com/QwenLM/Qwen3.8. The Qwen3.5 and Qwen3.6 repo URLs now 301-redirect there.
- "2026-02-16: We release Qwen3.5. The first release includes a 397B-A17B MoE model."
- "2026-02-24: Qwen3.5-122B-A10B, Qwen3.5-35B-A3B, and Qwen3.5-27B are released."
- "2026-03-02: Qwen3.5-9B, Qwen3.5-4B, Qwen3.5-2B, and Qwen3.5-0.8B are now available". Base models also exist on HF for 35B-A3B, 9B, 4B, 2B and 0.8B.
- "2026-04-16: Qwen3.6-35B-A3B is now available"; "2026-04-22: Qwen3.6-27B is now available".
- "2026-08-12: Qwen3.8-2.4T-A95B is now available"; "2026-08-14: Qwen3.8-27B is now available".
- Qwen3.8-Flash-Next open weights: 2026-08-26 (§2.1).
- Earlier hybrid/Flash-class model: "2025-09-11: We release Qwen3-Next-80B-A3B".

**Was Qwen3.6 released in March 2026?** Only as a preview.
- OpenRouter still lists `qwen/qwen3.6-plus-preview:free`, "Qwen3.6 Plus Preview", with `created` 1774891569 = **2026-03-30 17:26 UTC**. It now has 0 endpoints.
- Official launch: Qwen3.6-Plus (API, closed) on **2026-04-02**. Caixin, "Published: Apr. 2, 2026": "Alibaba Group Holding Ltd. on Thursday released Qwen 3.6-Plus" (https://www.caixinglobal.com/2026-04-02/alibaba-releases-qwen-36-plus-ai-model-with-enhanced-coding-capabilities-102430395.html). AA release date 2026-04-02, OpenRouter `qwen/qwen3.6-plus` created 2026-04-02.
- Open weights followed on Apr 16 and Apr 22.

Other API releases, by OpenRouter `created` date or AA release date:
- Qwen3.5-Plus 2026-02-16 and Qwen3.5-Flash 2026-02-25.
- Qwen3.6-Max (AA 2026-04-20) and Qwen3.6-Flash 2026-04-27.
- Qwen3.7 was API-only: Max 2026-05-21, Plus 2026-06-03, Flash 2026-07-27. HF search found no Qwen3.7 open weights.
- Qwen3.8-Max (AA 2026-08-03), Qwen3.8-Flash 2026-08-26, Qwen3.8-Max-0902 (2026-09-03), Qwen3.8-Omni-Flash (2026-09-18/21) and Qwen3.8-Max-Prime (2026-09-23).

### 3.2 Qwen 4
- Alibaba press release (Media OutReach, "HANGZHOU, CHINA – … – 22 September 2026", republished at https://macaubusiness.com/alibaba-unveils-roadmap-on-full-stack-ai-strategy-from-chips-cloud-infrastructure-models-to-agents/): "At the conference, Alibaba revealed that its next-generation model, Qwen 4, is currently in training." It also mentions a roadmap for "the upcoming Qwen 4.5 and Qwen 5 model series" … "projected to scale up to 5 to 10 trillion parameters."
- Qwen3.8-Flash-Next card: "This experimental preview of the architecture that will underpin Qwen4". GitHub: "an early preview of the architecture used in **Qwen4** … before the full Qwen4 model family is built on top of them."
- **Not found:** a Qwen 4 release date, sizes or license. Names circulating in the press ("Qwen-4-Max, Qwen-4-Plus, Qwen-4-Flash and Qwen-4-27B") trace to an X post. NYU-Shanghai RITS (secondary) says "Alibaba's published materials do not name these variants".

### 3.3 Capability on one consistent set: AA Intelligence Index
AA changed its index twice in 2026, so each row below comes from **a single snapshot**. Values were read from the JSON embedded in each AA page.

| AA index version (snapshot) | Qwen3.5-27B (Feb 24) | Qwen3.6-27B (Apr 22) | Qwen3.8-27B (Aug 14, xhigh) |
|---|---:|---:|---:|
| v4.0 (Wayback 2026-05-26, qwen3-6-27b page) | 42.1 | 45.8 | (not yet released) |
| **v4.1.1 (Wayback 2026-08-30, qwen3-8-27b page)** | **34.6** (`intelligenceIndexIsEstimated: true`) | **37.7** | **52.0** (medium 44.5, low 42.9, non-reasoning 34.7) |
| v5.0 (live page, 2026-10-30) | null (not scored) | null (not scored) | 20.1 (medium 17.5, low 15.7) |

Index definitions, from the pages:
- v4.0: "Intelligence Index v4.0 incorporates 10 evaluations: GDPval-AA, 𝜏²-Bench Telecom, Terminal-Bench Hard, SciCode, AA-LCR, AA-Omniscience, IFBench, Humanity's Last Exam, GPQA Diamond, CritPt".
- v4.1.1: "… incorporates 9 evaluations: GDPval-AA v2, 𝜏³-Banking, Terminal-Bench v2.1, SciCode, Humanity's Last Exam, GPQA Diamond, CritPt, AA-Omniscience, AA-LCR".
- v5.0: "… incorporates 9 evaluations: AA-Briefcase v1.1, AutomationBench-AA, Terminal-Bench 4.0, FrontierCode 2.0, AA-Omniscience v1.1, GDP.pdf, HLE-Diamond, CritPt v2 (Hard Subset), and Terminal-Bench-Science 0.1".

Page sentences:
- Qwen3.5 27B (2026-03-27 snapshot): "scores 42 on the Artificial Analysis Intelligence Index".
- Qwen3.6 27B (2026-05-26): "scores 46".
- Qwen3.8 27B (2026-08-30): "scores 52".
- Qwen3.8 27B (live): "scores 20 … it generated 130M tokens, which is very verbose in comparison to the median of 78M".

URLs:
- http://web.archive.org/web/20260327162147/https://artificialanalysis.ai/models/qwen3-5-27b
- http://web.archive.org/web/20260526031431/https://artificialanalysis.ai/models/qwen3-6-27b
- http://web.archive.org/web/20260830213601/https://artificialanalysis.ai/models/qwen3-8-27b
- https://artificialanalysis.ai/models/qwen3-8-27b

### 3.4 AA per-evaluation results, measured independently (v4.1.1 snapshot, 2026-08-30)
| AA eval | 3.5-27B | 3.6-27B | 3.8-27B (xhigh) |
|---|---:|---:|---:|
| GPQA Diamond | 85.8 | 84.2 | 90.5 |
| Humanity's Last Exam | 23.9 | 23.1 | 33.9 |
| SciCode | 39.5 | 39.8 | 44.7 |
| AA-LCR | 72.3 | 73.3 | 77.3 |
| AA-Omniscience (index) | −44.0 | −20.0 | −10.0 |
| CritPt | 0.85 | 1.14 | 5.43 |
| Terminal-Bench Hard | 32.6 | 34.8 | – |
| Terminal-Bench v2.1 | – | 60.7 | 79.8 |
| τ²-Bench Telecom | 93.9 | 94.2 | – |
| IFBench | 75.6 | 67.6 | – |
| GDPval-AA (ELO) | – | 1138 | 1543 |
| τ³-Banking | – | 16.7 | 48.0 |

AA does not currently publish LiveCodeBench or SWE-bench Verified for these models (`livecodebench: null`).

### 3.5 Vendor-reported benchmarks (self-reported; harness-dependent)
Sources: https://huggingface.co/Qwen/Qwen3.5-27B, https://huggingface.co/Qwen/Qwen3.6-27B, https://huggingface.co/Qwen/Qwen3.8-27B

| Benchmark | 3.5-27B | 3.6-27B | 3.8-27B | Frontier column in the same table |
|---|---:|---:|---:|---|
| SWE-bench Verified | 72.4 (own card); 75.0 (in the 3.6 card) | 77.2 | **not found** (3.8 card does not report it) | Claude 4.5 Opus 80.9 (3.6 card) |
| SWE-bench Pro | 51.2 (3.6 card) | 53.5 | 61.7 | Opus 4.6 Max 53.4 (3.8 card) |
| LiveCodeBench v6 | 80.7 | 83.9 | 90.3 | Claude 4.5 Opus 84.8; Opus 4.6 Max 88.8 |
| Terminal-Bench 2.0 | 41.6 | 59.3 | – | Claude 4.5 Opus 59.3 |
| Terminal Bench 2.1 (Terminus) | – | 63.4 (3.8 card) | 73.0 | Opus 4.6 Max 78.2 |
| GPQA Diamond | 85.5 | 87.8 | 89.2 | Opus 4.6 Max 91.3 |
| HLE | 24.3 | 24.0 | 30.8 | Opus 4.6 Max 40.0 |

Note that the "frontier" columns in the Qwen cards are older Claude versions than the frontier on each release date.

### 3.6 Frontier at the same dates (AA, same snapshot as the 27B number)
| Date | v4.1.1 frontier (2026-08-30 data) | 27B gap | v4.0 frontier (2026-05-26 data) | 27B gap |
|---|---|---:|---|---:|
| 2026-02-24 (Qwen3.5-27B) | Claude Sonnet 4.6 adaptive 48.4; Gemini 3.1 Pro Preview 47.7 | 13.8 | Gemini 3.1 Pro Preview 57.2 | 15.1 |
| 2026-04-22 (Qwen3.6-27B) | Claude Opus 4.7 55.0 (GPT-5.5, Apr 23: 56.3) | 17.3 | Claude Opus 4.7 57.3 | 11.5 |
| 2026-08-14 (Qwen3.8-27B) | Claude Opus 5 63.1; Claude Fable 5 62.1; GPT-5.6 Sol 60.9; best open Kimi K3 59.7 | 11.1 | – | – |
| 2026-10-30 (v5.0, live) | Gemini 4 Carbon 59.4; Claude Opus 5.5 58.4; GPT-6 Astra 56.9 | 39.3 (vs 3.8-27B 20.1) | – | – |

AA independent Terminal-Bench v2.1 for scale: Claude Opus 4.7 83.1, GPT-5.5 84.3, Claude Opus 5 89.1, GPT-5.6 Sol 88.0, against 60.7 (3.6-27B) and 79.8 (3.8-27B).

### 3.7 Longer series and lag to the frontier (estimates from AA v4.1.1, 2026-08-30 data)
Dense ~27–33B Qwen reasoning models (est. = AA marks the value as estimated):
- Qwen2.5-32B (2024-09) 7.2 est.
- QwQ-32B (2025-03) 13.4 est.
- Qwen3-32B (2025-04-28) 11.4
- Qwen3-VL-32B (2025-10-21) 18.1 est.
- Qwen3.5-27B (2026-02-24) 34.6 est.
- Qwen3.6-27B (2026-04-22) 37.7
- Qwen3.8-27B (2026-08-14) 52.0

Best open model ≤40B on the same index:
- Aug 2025: Seed-OSS-36B, 18.5
- Jan 2026: GLM-4.7-Flash, 23.3 est.
- Feb–Apr 2026: the Qwen 27Bs. Gemma 4 31B (2026-04-02) scored 29.7.
- Aug 2026: Qwen3.8-27B. Muse Glimmer (2026-08-10) scored 35.1.

Flash/MoE line:
- Qwen3-Next-80B-A3B (2025-09-11): 16.9
- Qwen3.5-35B-A3B (2026-02-24): 29.9 est.
- Qwen3.6-35B-A3B (2026-04-16): 32.1
- Qwen3.8-Flash-Next (2026-08-26): 55.8
- For comparison, GLM-5.3-Flash (2026-08-26): 57.5

**Lag to the frontier** is my estimate: the date at which the first model of any kind reached at least the 27B's score.
- Qwen3.8-27B (52.0): matched by GPT-5.4 (2026-03-05, 53.1), a lag of about 5.3 months.
- Qwen3.6-27B (37.7): matched by Gemini 3 Pro (2025-11-18, 40.6 est.), about 5.1 months. Claude 4.5 Sonnet at 37.4 on 2025-09-29 would put it at about 6.8 months.
- Qwen3.5-27B (34.6): matched by GPT-5 (2025-08-07, 35.3), about 6.6 months.
- Lags in 2025 were longer: about 10–14 months for Qwen3-32B and Qwen3-VL-32B.

### 3.8 The thesis "~27B capability reaches a new level about every 6 months"
**For:**
- On one fixed index (AA v4.1.1), the Qwen dense ~27–33B line steps up roughly twice a year. The big steps were Oct 2025 → Feb 2026 (+16.5) and Feb → Aug 2026 (+17.4); the steps in 2025 were smaller (+5 to +7). Qwen3.5-27B (Feb 2026) → Qwen3.8-27B (Aug 2026) is +17.4 points (+50%) in 5.6 months.
- Independent AA evals agree for Feb → Aug 2026: GPQA 85.8 → 90.5, HLE 23.9 → 33.9, AA-LCR 72.3 → 77.3. Terminal-Bench v2.1 rose 60.7 → 79.8 from Apr to Aug.
- Vendor numbers agree: LCB v6 80.7 → 83.9 → 90.3; SWE-bench Pro 51.2 → 53.5 → 61.7.
- In 2026 the 27B class trailed the frontier by a fairly stable **~5–7 months**, down from ~10–14 months in 2025. A model that reaches "frontier minus ~6 months" every ~6 months fits the thesis.
- AA's Aug-30 page puts Qwen3.8 27B's 52 far above the size-class median of 9.

**Against / caveats:**
- The steps are irregular, not smooth. Qwen3.5 → 3.6 (2 months) gained only +3.1 on v4.1.1 or +3.7 on v4.0, and some AA evals went down: GPQA 85.8 → 84.2, HLE 23.9 → 23.1, IFBench 75.6 → 67.6. The cadence follows Qwen's release schedule; with one vendor over about 2.5 years, it is not a law.
- Part of the 3.8 jump is test-time compute. At medium/low effort, 3.8-27B scores 44.5/42.9, only +5 to +7 over 3.6-27B. AA calls the xhigh setting "very verbose": 130M output tokens against a 78M median on v5.0. Capability per dollar rose less than capability.
- The index versions disagree. Feb → Apr, the gap to the frontier narrowed on v4.0 (15.1 → 11.5) but widened on v4.1.1 (13.8 → 17.3). On v5.0, which uses harder agentic evals, Qwen3.8-27B scores 20.1 against a frontier of about 58–59. The absolute gap there is about 39 points, so "frontier minus 6 months" depends on the yardstick.
- Qwen3.5-27B's v4.1.1 value is AA-estimated; it was not run on GDPval-AA v2, τ³-Banking or Terminal-Bench v2.1. Vendor scores move with the harness: Qwen3.5-27B's SWE-bench Verified is 72.4 in its own card and 75.0 in the 3.6 card.

---

## 4. LLM API price decline at fixed capability

| Source (date) | Finding (exact wording) | URL |
|---|---|---|
| a16z, Guido Appenzeller, "LLMflation" (Nov 12, 2024) | "For an LLM of equivalent performance, the cost is decreasing by 10x every year." "The cost of LLM inference has dropped by a factor of 1,000 in 3 years" (MMLU ≥ 42: $60 → $0.06/M). At MMLU 83, prices fell "by about a factor of 62" since GPT-4 (Mar 2023). | https://a16z.com/llmflation-llm-inference-cost/ |
| Epoch AI data insight (Mar 12, 2025), Cottier, Snodin, Owen, Adamczewski | "ranging from 9x to 900x per year". GPT-4-level GPQA price "fell by 40x per year". "we found prices declining between 9x per year and 900x per year, with a median of 50x per year". Post-Jan-2024 data: "the median rate increased from 50x per year to 200x per year". | https://epoch.ai/data-insights/llm-inference-price-trends |
| Stanford AI Index 2025 | "the inference cost for a system performing at the level of GPT-3.5 dropped over 280-fold between November 2022 and October 2024". Hardware "costs have declined by 30% annually". | https://hai.stanford.edu/ai-index/2025-ai-index-report |
| Gundlach, Lynch, Mertens, Thompson, "The Price of Progress" (arXiv 2511.23455; v2 Mar 23, 2026) | "the price for a given level of benchmark performance has decreased remarkably fast, around 5× to 10× per year, for frontier models". "algorithmic efficiency progress is around 3× per year". "the price of running frontier models is rising between 3× to 18× per year due to bigger models and larger reasoning demands." | https://arxiv.org/abs/2511.23455 |
| Demirer, Fradkin, Tadelis, Peng, NBER w34608 (Dec 2025) | "open-source models being 90% cheaper than comparable closed-source models of the same intelligence". "preliminary short-run price elasticities just above one". No per-year rate in the abstract. | https://www.nber.org/papers/w34608 |
| **Epoch AI, "The plunging price of thought" (Sep 22, 2026), Emberson and Roodman. Main 2026 update.** | "The cost of achieving a given level of AI performance has fallen about 47% per quarter since 2023, or 13× per year." By domain: "39–43% per quarter (7–10× per year)" for games, "50–52% per quarter (16–19× per year)" for math. "cost falls 66% per quarter (75× per year) for performance that has just debuted as SOTA. Two years later … 32% per quarter (4.7× per year)." Example: o3 at about $0.30 per question for 75% GPQA (Jan 2025) vs GPT-5.6 Luna at "$0.0004", "a 725-fold drop … in under 18 months". Cites Ihle (LessWrong, Sep 2025): "costs halved every 1.4–2 months (64–380× per year)". | https://epoch.ai/publications/the-plunging-price-of-thought |

Notes:
- The 2026 Epoch report measures the **cost to reach a score**, including token counts, across reasoning-effort settings. The 2024–25 studies measure **price per token** for models able to reach a score. That difference largely explains why 13×/yr is lower than the 2025 median of 50×/yr.
- **Not found:** an a16z update in 2026. The AI Index 2026 landing page (https://hai.stanford.edu/ai-index/2026-ai-index-report) has no inference-price headline; I did not check the full PDF.

**Estimate from AA v4.1.1 list prices** (3:1 input:output blend, per token, ignoring tokens used per task):
- AA ≈ 52–53 level. GPT-5.4 (2026-03-05; 53.1; $2.5/$15) blends to $5.63/M. Qwen3.8-27B (2026-08-14; 52.0; $0.5/$3) blends to $1.13/M. That is 5× cheaper in 5.3 months, about 38×/yr annualized.
- GLM-5.3-Flash (2026-08-26; 57.5, a higher score; $0.15/$0.50) blends to $0.24/M, 24× cheaper than GPT-5.4 in 5.7 months.
- Both fit Epoch's pattern that prices fall fastest just after a level debuts as SOTA. Qwen3.8-27B's high token use (above) cuts into the per-task saving.

---

## 5. Could not confirm / not found
- GLM-5.3-Flash: the pre-training/native training context length. The `config.json` declares 1,048,576 with NoPE, and docs say 1M.
- GLM-5.3-Flash: Z.ai's exact KV accounting behind "4.44×". My formula gives 4.3–4.6×.
- GLM-5.3-Flash: whether OpenRouter's listed prices already include the `discount` field (GMICloud 0.5, Novita 0.44, StreamLake 0.41, Phala 0.15).
- `qwen3.8-flash`: whether the API weights are identical to the Qwen3.8-Flash-Next open weights. The only statement is "official version based on Qwen3.8-Flash-Next with more production features".
- `qwen3.8-flash`: prompt-length price tiers. None exist on Model Studio, Qwen Cloud or OpenRouter.
- Qwen3.8-27B SWE-bench Verified. It is not in the official card, and AA does not run it.
- LiveCodeBench and SWE-bench Verified from an independent evaluator for all three 27Bs. AA no longer runs them.
- Qwen 4 release date, sizes or license. The only official statement is "currently in training" (2026-09-22).
- a16z LLMflation 2026 update. None found.

## 6. Method notes
- AA numbers were read from the model JSON embedded in each AA page (fields `intelligenceIndex`, `intelligenceIndexIsEstimated`, `gpqa`, `hle`, `terminalbenchV21`, etc.), from the live site and from Wayback raw captures (`…id_/…`). Each comparison uses values from a single snapshot.
- I verified the KV formula against the Transformers `glm5_next` modeling code. MLA caches the compressed 512-d latent with `qk_rope_head_dim` = 0. The indexer stores one 128-d key per token, which IndexPool compresses 4:1. KDA keeps a 64×128×128 FP32 state per layer.
