# API cache report - r15d

Whole window: 2026-11-03T14:39:44.389926+00:00 through 2026-11-04T07:22:22.114713+00:00. Final: True.

Identity-refused accepted rows: 0. The identity filter excludes accepted rows with absent provider or unknown/absent model from cache/price metrics. Under r15j, HTTP200 with usable complete usage is successful availability even when identity/depth is unproven; no usable usage is a failure. Earlier rows retain their recorded availability. Original raw rows and financial charges stay unchanged; rejected identities are recorded in analysis.json.

The whole Chutes smoke and every call_index0 are excluded from cache metrics. All attempted calls, including seeds and charge-resolved timeouts, count toward availability. Old full-v3 attempts join both new phases; pilot/configuration cohorts do not.

Known zero hits are priced at the measured rate. Missing usage stays unknown. Core and long-pause prices stay separate. Remote rolling daily statistics are metadata, not a substitute for whole-window own availability.

Headline1M is pooled across restarted-v1 multi-pause cadence and amendment core cadence. Per-phase1M figures are beside it; the separate long-pause substudy and probes are excluded.

| Endpoint | Attempts | Errors | Timeouts | Availability | Cache analysis calls at1M | Pooled1M USD/1000 | V1-only1M USD/1000 | Amendment-core1M USD/1000 | Eligibility |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| qwen/qwen3.8-27b / alibaba | 13 | 2 | 0 | 0.846154 | 1 | unknown | unknown | unknown | excluded-availability |
| z-ai/glm-5.3-flash / morph/fp8 | 44 | 3 | 0 | 0.931818 | 18 | 22.3124 | 25.0281 | 20.2001 | excluded-availability |
| qwen/qwen3.8-27b / streamlake | 30 | 6 | 0 | 0.8 | 0 | unknown | unknown | unknown | excluded-availability |
| z-ai/glm-5.3-flash / relace/fp4 | 41 | 9 | 0 | 0.780488 | 16 | 28.1732 | unknown | 28.1732 | excluded-availability |
| qwen/qwen3.8-27b / deepinfra/bf16 | 21 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / coreweave/fp8 | 11 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / parasail/fp8 | 21 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / modelrun/fp4 | 11 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / wafer/nvfp4 | 11 | 0 | 0 | 1 | 9 | 53.5477 | 53.5477 | unknown | eligible |
| z-ai/glm-5.3-flash / friendli | 22 | 0 | 0 | 1 | 9 | 83.7927 | 83.7927 | unknown | eligible |
| z-ai/glm-5.3-flash / deepinfra/fp4 | 21 | 0 | 0 | 1 | 9 | 123.622 | 123.622 | unknown | eligible |
| z-ai/glm-5.3-flash / together | 11 | 0 | 0 | 1 | 9 | 150.256 | 150.256 | unknown | eligible |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | 44 | 1 | 0 | 0.977273 | 18 | 70.2554 | 97.9968 | 42.514 | eligible |
| z-ai/glm-5.3-flash / sail-research/fp4 | 33 | 1 | 0 | 0.969697 | 9 | 23.0271 | unknown | 23.0271 | eligible |
| z-ai/glm-5.3-flash / streamlake/fp8 | 32 | 1 | 0 | 0.96875 | 9 | 41.5507 | unknown | 41.5507 | eligible |
| z-ai/glm-5.3-flash / parasail/fp4 | 10 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / reka | 38 | 20 | 0 | 0.473684 | 14 | unknown | unknown | unknown | excluded-availability |
| qwen/qwen3.8-27b / dekallm | 10 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / phala | 32 | 4 | 0 | 0.875 | 9 | 54.2087 | unknown | 54.2087 | excluded-availability |
| qwen/qwen3.8-27b / cloudflare | 20 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / phala/nvfp4 | 38 | 0 | 0 | 1 | 14 | 61.3228 | 58.755 | 62.7494 | eligible |
| z-ai/glm-5.3-flash / inference-net/us | 10 | 0 | 0 | 1 | 8 | 32.2689 | 32.2689 | unknown | eligible |
| z-ai/glm-5.3-flash / modal/fp4 | 10 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / fireworks/us | 10 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / wafer/fp8 | 9 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / tenstorrent/fp4 | 9 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / novita | 31 | 17 | 1 | 0.451613 | 16 | 421.536 | unknown | 421.536 | excluded-availability |
| qwen/qwen3.8-27b / darkbloom/fp4 | 10 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / open-inference/fp4 | 30 | 0 | 0 | 1 | 9 | 20.2488 | unknown | 20.2488 | eligible |
| z-ai/glm-5.3-flash / primeintellect | 6 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / siliconflow/fp8 | 3 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / digitalocean | 22 | 0 | 0 | 1 | 9 | 30.2969 | unknown | 30.2969 | eligible |
| z-ai/glm-5.3-flash / crusoe/fp4 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / makora | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / near-ai/fp8 | 22 | 8 | 0 | 0.636364 | 9 | 46.3497 | unknown | 46.3497 | excluded-availability |
| qwen/qwen3.8-27b / ionstream/fp8 | 2 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / z-ai/fp8 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / baseten/fp8 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| qwen/qwen3.8-27b / modal | 2 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / akashml/fp8 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / nextbit/fp4 | 22 | 5 | 0 | 0.772727 | 9 | 30.4929 | unknown | 30.4929 | excluded-availability |
| z-ai/glm-5.3-flash / baseten/fp8/us | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / sail-research/us | 22 | 5 | 0 | 0.772727 | 9 | 23.0299 | unknown | 23.0299 | excluded-availability |
| qwen/qwen3.8-27b / chutes/fp8 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| qwen/qwen3.8-27b / reka/fp8 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / fireworks | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / gmicloud/fp8 | 22 | 0 | 0 | 1 | 9 | 15.1938 | unknown | 15.1938 | eligible |
| z-ai/glm-5.3-flash / atlas-cloud/fp8 | 16 | 0 | 0 | 1 | 9 | 137.009 | unknown | 137.009 | eligible |
| z-ai/glm-5.3-flash / wafer/us | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / nebius/fp4 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / novita/fp8 | 22 | 0 | 0 | 1 | 9 | 17.0173 | unknown | 17.0173 | eligible |
| z-ai/glm-5.3-flash / venice | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / mistral | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / cohere | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / inceptron/fp8 | 0 | 0 | 0 | unknown | 0 | unknown | unknown | unknown | unqualified-no-attempts |
| z-ai/glm-5.3-flash / inference-net/fp4 | 1 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| qwen/qwen3.8-27b / near-ai/fp8 | 1 | 0 | 0 | 1 | 0 | unknown | unknown | unknown | eligible |
| z-ai/glm-5.3-flash / particle-ai/nvfp4 | 22 | 0 | 0 | 1 | 9 | 45.9132 | unknown | 45.9132 | eligible |

## Output-length non-compliance (r15f)

Full valid usage above the requested16 output tokens remains successful availability and cache-eligible. Every seed remains excluded from cache inference. The numeric completion_over_cap is the actual reported count. A guard cancellation without final usage is censored and remains an availability failure, with its charge reconciled before another call.

| Endpoint | Confirmed over-cap calls | Guard cancellations | Unknown final token count |
|---|---:|---:|---:|
| qwen/qwen3.8-27b / alibaba | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / morph/fp8 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / streamlake | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / relace/fp4 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / deepinfra/bf16 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / coreweave/fp8 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / parasail/fp8 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / modelrun/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / wafer/nvfp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / friendli | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / deepinfra/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / together | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / sail-research/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / streamlake/fp8 | 2 | 1 | 1 |
| z-ai/glm-5.3-flash / parasail/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / reka | 0 | 0 | 0 |
| qwen/qwen3.8-27b / dekallm | 0 | 0 | 0 |
| qwen/qwen3.8-27b / phala | 0 | 0 | 0 |
| qwen/qwen3.8-27b / cloudflare | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / phala/nvfp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / inference-net/us | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / modal/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / fireworks/us | 0 | 0 | 0 |
| qwen/qwen3.8-27b / wafer/fp8 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / tenstorrent/fp4 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / novita | 0 | 0 | 0 |
| qwen/qwen3.8-27b / darkbloom/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / open-inference/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / primeintellect | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / siliconflow/fp8 | 1 | 0 | 0 |
| z-ai/glm-5.3-flash / digitalocean | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / crusoe/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / makora | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / near-ai/fp8 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / ionstream/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / z-ai/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / baseten/fp8 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / modal | 0 | 0 | 0 |
| qwen/qwen3.8-27b / akashml/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / nextbit/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / baseten/fp8/us | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / sail-research/us | 0 | 0 | 0 |
| qwen/qwen3.8-27b / chutes/fp8 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / reka/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / fireworks | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / gmicloud/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / atlas-cloud/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / wafer/us | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / nebius/fp4 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / novita/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / venice | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / mistral | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / cohere | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / inceptron/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / inference-net/fp4 | 0 | 0 | 0 |
| qwen/qwen3.8-27b / near-ai/fp8 | 0 | 0 | 0 |
| z-ai/glm-5.3-flash / particle-ai/nvfp4 | 0 | 0 | 0 |

## Profile and logs comparison

| Endpoint | Phase/cohort | Warm accepted | Cached fraction | Uncached/call | Delta vs3200 | USD/1000 measured depth mix |
|---|---|---:|---:|---:|---:|---:|
| qwen/qwen3.8-27b / alibaba | v1/v1 | 9 | 0 | 126996 | 123796 | 126.643 |
| z-ai/glm-5.3-flash / morph/fp8 | v1/v1 | 16 | 0.619841 | 218394 | 215194 | 15.8183 |
| z-ai/glm-5.3-flash / morph/fp8 | amendment/core | 18 | 0.997013 | 2263.67 | -936.333 | 15.4414 |
| qwen/qwen3.8-27b / streamlake | v1/v1 | 19 | 0.516983 | 72855.8 | 69655.8 | 28.1145 |
| z-ai/glm-5.3-flash / relace/fp4 | v1/v1 | 9 | 0.543051 | 112372 | 109172 | 8.17056 |
| z-ai/glm-5.3-flash / relace/fp4 | amendment/core | 17 | 0.997035 | 2204.82 | -995.176 | 20.7514 |
| qwen/qwen3.8-27b / deepinfra/bf16 | v1/v1 | 17 | 0.509312 | 89662.4 | 86462.4 | 18.2492 |
| qwen/qwen3.8-27b / coreweave/fp8 | v1/v1 | 9 | 0.757317 | 30820.2 | 27620.2 | 28.9567 |
| qwen/qwen3.8-27b / parasail/fp8 | v1/v1 | 17 | 0.42915 | 81895.9 | 78695.9 | 24.4384 |
| qwen/qwen3.8-27b / modelrun/fp4 | v1/v1 | 9 | 0.285515 | 20500 | 17300 | 6.67665 |
| z-ai/glm-5.3-flash / wafer/nvfp4 | v1/v1 | 9 | 0.55364 | 444540 | 441340 | 53.5477 |
| z-ai/glm-5.3-flash / friendli | v1/v1 | 18 | 0.529909 | 291889 | 288689 | 54.2032 |
| z-ai/glm-5.3-flash / deepinfra/fp4 | v1/v1 | 17 | 0.247902 | 483406 | 480206 | 77.9469 |
| z-ai/glm-5.3-flash / together | v1/v1 | 9 | 0 | 995919 | 992719 | 150.256 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | v1/v1 | 18 | 0.242508 | 470340 | 467140 | 59.9474 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | amendment/core | 18 | 0.852469 | 111800 | 108600 | 26.696 |
| z-ai/glm-5.3-flash / sail-research/fp4 | v1/v1 | 9 | 0.758306 | 59437.2 | 56237.2 | 15.0474 |
| z-ai/glm-5.3-flash / sail-research/fp4 | amendment/core | 17 | 0.997981 | 1557.71 | -1642.29 | 18.0211 |
| z-ai/glm-5.3-flash / streamlake/fp8 | v1/v1 | 8 | 0.123707 | 215058 | 211858 | 20.0733 |
| z-ai/glm-5.3-flash / streamlake/fp8 | amendment/core | 17 | 0.650282 | 269845 | 266645 | 33.1167 |
| z-ai/glm-5.3-flash / parasail/fp4 | v1/v1 | 8 | 0.49398 | 124187 | 120987 | 22.8325 |
| z-ai/glm-5.3-flash / reka | v1/v1 | 7 | 0.420345 | 142218 | 139018 | 20.6027 |
| z-ai/glm-5.3-flash / reka | amendment/core | 7 | 0.711825 | 149573 | 146373 | 29.497 |
| qwen/qwen3.8-27b / dekallm | v1/v1 | 8 | 0.45064 | 15487 | 12287 | 2.2741 |
| qwen/qwen3.8-27b / phala | v1/v1 | 8 | 0.242976 | 95762 | 92562 | 22.6409 |
| qwen/qwen3.8-27b / phala | amendment/core | 16 | 0.986829 | 9595.81 | 6395.81 | 39.349 |
| qwen/qwen3.8-27b / cloudflare | v1/v1 | 16 | 0 | 136811 | 133611 | 65.2612 |
| z-ai/glm-5.3-flash / phala/nvfp4 | v1/v1 | 13 | 0.571029 | 228772 | 225572 | 33.1389 |
| z-ai/glm-5.3-flash / phala/nvfp4 | amendment/core | 18 | 0.553786 | 338143 | 334943 | 47.9203 |
| z-ai/glm-5.3-flash / inference-net/us | v1/v1 | 8 | 0.99888 | 1115 | -2085 | 32.2689 |
| z-ai/glm-5.3-flash / modal/fp4 | v1/v1 | 8 | 0.122696 | 215307 | 212107 | 34.0223 |
| z-ai/glm-5.3-flash / fireworks/us | v1/v1 | 8 | 0.995779 | 1036 | -2164 | 11.8323 |
| qwen/qwen3.8-27b / wafer/fp8 | v1/v1 | 7 | 0.381682 | 17121.9 | 13921.9 | 3.13011 |
| qwen/qwen3.8-27b / tenstorrent/fp4 | v1/v1 | 7 | 0.140506 | 210513 | 207313 | 34.9682 |
| qwen/qwen3.8-27b / novita | v1/v1 | 0 | unknown | unknown | unknown | unknown |
| qwen/qwen3.8-27b / novita | amendment/core | 10 | 0.730711 | 152714 | 149514 | 101.846 |
| qwen/qwen3.8-27b / darkbloom/fp4 | v1/v1 | 8 | 0.0136158 | 214434 | 211234 | 8.49829 |
| z-ai/glm-5.3-flash / open-inference/fp4 | v1/v1 | 6 | 0.9026 | 23808 | 20608 | 5.89219 |
| z-ai/glm-5.3-flash / open-inference/fp4 | amendment/core | 18 | 0.968584 | 23808 | 20608 | 15.5159 |
| z-ai/glm-5.3-flash / open-inference/fp4 | amendment/long | 0 | unknown | unknown | unknown | unknown |
| z-ai/glm-5.3-flash / primeintellect | v1/v1 | 5 | 0.789665 | 51304.6 | 48104.6 | 14.0941 |
| z-ai/glm-5.3-flash / siliconflow/fp8 | v1/v1 | 2 | 0.995553 | 1078 | -2122 | 7.89344 |
| z-ai/glm-5.3-flash / digitalocean | amendment/core | 18 | 0.998337 | 1260 | -1940 | 23.1604 |
| z-ai/glm-5.3-flash / near-ai/fp8 | amendment/core | 11 | 0.531975 | 324447 | 321247 | 30.8334 |
| qwen/qwen3.8-27b / ionstream/fp8 | v1/v1 | 1 | 0.958976 | 1013 | -2187 | 1.67541 |
| qwen/qwen3.8-27b / modal | v1/v1 | 1 | 0 | 24692 | 21492 | 2.48832 |
| z-ai/glm-5.3-flash / nextbit/fp4 | amendment/core | 14 | 0.8364 | 112884 | 109684 | 31.3062 |
| z-ai/glm-5.3-flash / sail-research/us | amendment/core | 15 | 0.99783 | 1610.6 | -1589.4 | 17.3576 |
| z-ai/glm-5.3-flash / gmicloud/fp8 | amendment/core | 18 | 0.997691 | 1749.61 | -1450.39 | 11.6658 |
| z-ai/glm-5.3-flash / atlas-cloud/fp8 | amendment/core | 12 | 0.0943144 | 793322 | 790122 | 122.481 |
| z-ai/glm-5.3-flash / novita/fp8 | amendment/core | 18 | 0.997863 | 1619.61 | -1580.39 | 13.0568 |
| qwen/qwen3.8-27b / near-ai/fp8 | v1/v1 | 0 | unknown | unknown | unknown | unknown |
| z-ai/glm-5.3-flash / particle-ai/nvfp4 | amendment/core | 18 | 0.81271 | 141929 | 138729 | 33.0822 |

## Pooled1M with and without Alibaba

qwen/qwen3.8-27b / with_alibaba: unknown USD/1000 over 0 qualified, measured providers; all retained provider identities are in analysis.json.
qwen/qwen3.8-27b / without_alibaba: unknown USD/1000 over 0 qualified, measured providers; all retained provider identities are in analysis.json.
z-ai/glm-5.3-flash / with_alibaba: 60.3548 USD/1000 over 15 qualified, measured providers; all retained provider identities are in analysis.json.
z-ai/glm-5.3-flash / without_alibaba: 60.3548 USD/1000 over 15 qualified, measured providers; all retained provider identities are in analysis.json.

## Cold-probe latency

| Endpoint | Depth | Classification | TTFT seconds |
|---|---:|---|---:|
| z-ai/glm-5.3-flash / morph/fp8 | 1000000 | confirmed-cache-miss | 29.8812 |
| z-ai/glm-5.3-flash / morph/fp8 | 524288 | confirmed-cache-miss | 14.8084 |
| z-ai/glm-5.3-flash / relace/fp4 | 1000000 | confirmed-cache-miss | 44.5566 |
| z-ai/glm-5.3-flash / relace/fp4 | 524288 | confirmed-cache-miss | 19.6814 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | 1000000 | confirmed-cache-miss | 36.1557 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | 524288 | confirmed-cache-miss | 16.0596 |
| z-ai/glm-5.3-flash / sail-research/fp4 | 1000000 | confirmed-cache-miss | 82.3375 |
| z-ai/glm-5.3-flash / sail-research/fp4 | 524288 | confirmed-cache-miss | 27.8669 |
| z-ai/glm-5.3-flash / streamlake/fp8 | 1000000 | confirmed-cache-miss | 54.959 |
| z-ai/glm-5.3-flash / streamlake/fp8 | 524288 | confirmed-cache-miss | 38.7318 |
| z-ai/glm-5.3-flash / reka | 1000000 | failed-or-unverified | unknown |
| z-ai/glm-5.3-flash / reka | 524288 | confirmed-cache-miss | 29.0828 |
| qwen/qwen3.8-27b / phala | 1000000 | failed-or-unverified | unknown |
| qwen/qwen3.8-27b / phala | 524288 | confirmed-cache-miss | 110.473 |
| z-ai/glm-5.3-flash / phala/nvfp4 | 1000000 | confirmed-cache-miss | 85.8875 |
| z-ai/glm-5.3-flash / phala/nvfp4 | 524288 | confirmed-cache-miss | 42.8918 |
| qwen/qwen3.8-27b / novita | 1000000 | failed-or-unverified | unknown |
| qwen/qwen3.8-27b / novita | 524288 | confirmed-cache-miss | 144.393 |
| z-ai/glm-5.3-flash / open-inference/fp4 | 1000000 | cache-hit | unknown |
| z-ai/glm-5.3-flash / open-inference/fp4 | 524288 | cache-hit | unknown |
| z-ai/glm-5.3-flash / digitalocean | 1000000 | confirmed-cache-miss | 33.4093 |
| z-ai/glm-5.3-flash / digitalocean | 524288 | confirmed-cache-miss | 17.2868 |
| z-ai/glm-5.3-flash / near-ai/fp8 | 1000000 | no-observed-token | unknown |
| z-ai/glm-5.3-flash / near-ai/fp8 | 524288 | failed-or-unverified | unknown |
| z-ai/glm-5.3-flash / nextbit/fp4 | 1000000 | failed-or-unverified | unknown |
| z-ai/glm-5.3-flash / nextbit/fp4 | 524288 | confirmed-cache-miss | 56.4915 |
| z-ai/glm-5.3-flash / sail-research/us | 1000000 | failed-or-unverified | unknown |
| z-ai/glm-5.3-flash / sail-research/us | 524288 | confirmed-cache-miss | 27.3493 |
| z-ai/glm-5.3-flash / gmicloud/fp8 | 1000000 | confirmed-cache-miss | 77.3599 |
| z-ai/glm-5.3-flash / gmicloud/fp8 | 524288 | confirmed-cache-miss | 39.7884 |
| z-ai/glm-5.3-flash / atlas-cloud/fp8 | 1000000 | confirmed-cache-miss | 82.23 |
| z-ai/glm-5.3-flash / atlas-cloud/fp8 | 524288 | confirmed-cache-miss | 18.0176 |
| z-ai/glm-5.3-flash / novita/fp8 | 1000000 | confirmed-cache-miss | 76.4662 |
| z-ai/glm-5.3-flash / novita/fp8 | 524288 | confirmed-cache-miss | 39.8705 |
| z-ai/glm-5.3-flash / inference-net/fp4 | 1000000 | confirmed-cache-miss | 41.631 |
| z-ai/glm-5.3-flash / particle-ai/nvfp4 | 1000000 | confirmed-cache-miss | 39.9237 |
| z-ai/glm-5.3-flash / particle-ai/nvfp4 | 524288 | confirmed-cache-miss | 16.329 |

Equal provider weights in these aggregates; per-provider prices retain disclosed depth/profile assumptions. The JSON contains core/long pause hit rates, measured depth mixes and differences from the logs baseline (98.1% cached, 3200 uncached tokens/call). Availability is request-sampled over the whole stated window and does not prove continuous uptime. Rolling daily observations and missing samples are retained per provider in JSON. No surface table or independent review was supplied.


## Permanent billing reservations (r15k)

Never-stable failed calls without a generation id retain their full maximum permanently against both caps. They are availability failures, excluded from cache metrics; a reservation is not an observed debit. A fourth lifetime reservation halts. Handoff/end cumulative rechecks never release these holds or invent per-call cost attribution.

| Call | Maximum USD | Status | Last recheck |
|---|---:|---|---|

## Interrupted series (r15m)

Rows after a resumed partial cell carry resumed_cell and a first-call resume_boundary. The original rows remain unchanged. Analysis separates entire interrupted cells, their continuation rows, and uninterrupted cells; no long stop gap is treated as an8s/35s TTL result. Headline pooled figures retain all admitted measurements; cadence subsets are disclosed below and in JSON.

| Endpoint | Phase/cohort | Cadence subset | Warm accepted | Cached fraction | USD/1000 measured depth mix |
|---|---|---|---:|---:|---:|
| qwen/qwen3.8-27b / alibaba | v1/v1 | uninterrupted | 9 | 0 | 126.643 |
| z-ai/glm-5.3-flash / morph/fp8 | v1/v1 | uninterrupted | 16 | 0.619841 | 15.8183 |
| z-ai/glm-5.3-flash / morph/fp8 | amendment/core | uninterrupted | 18 | 0.997013 | 15.4414 |
| qwen/qwen3.8-27b / streamlake | v1/v1 | uninterrupted | 19 | 0.516983 | 28.1145 |
| z-ai/glm-5.3-flash / relace/fp4 | v1/v1 | uninterrupted | 9 | 0.543051 | 8.17056 |
| z-ai/glm-5.3-flash / relace/fp4 | amendment/core | uninterrupted | 17 | 0.997035 | 20.7514 |
| qwen/qwen3.8-27b / deepinfra/bf16 | v1/v1 | uninterrupted | 17 | 0.509312 | 18.2492 |
| qwen/qwen3.8-27b / coreweave/fp8 | v1/v1 | uninterrupted | 9 | 0.757317 | 28.9567 |
| qwen/qwen3.8-27b / parasail/fp8 | v1/v1 | uninterrupted | 17 | 0.42915 | 24.4384 |
| qwen/qwen3.8-27b / modelrun/fp4 | v1/v1 | uninterrupted | 9 | 0.285515 | 6.67665 |
| z-ai/glm-5.3-flash / wafer/nvfp4 | v1/v1 | uninterrupted | 9 | 0.55364 | 53.5477 |
| z-ai/glm-5.3-flash / friendli | v1/v1 | uninterrupted | 18 | 0.529909 | 54.2032 |
| z-ai/glm-5.3-flash / deepinfra/fp4 | v1/v1 | uninterrupted | 17 | 0.247902 | 77.9469 |
| z-ai/glm-5.3-flash / together | v1/v1 | uninterrupted | 9 | 0 | 150.256 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | v1/v1 | uninterrupted | 18 | 0.242508 | 59.9474 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | amendment/core | uninterrupted | 9 | 0.996228 | 10.8779 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | amendment/core | resumed_cells | 9 | 0.777396 | 42.514 |
| z-ai/glm-5.3-flash / coreweave/nvfp4 | amendment/core | continuation_only | 6 | 0.832683 | 36.9706 |
| z-ai/glm-5.3-flash / sail-research/fp4 | v1/v1 | uninterrupted | 9 | 0.758306 | 15.0474 |
| z-ai/glm-5.3-flash / sail-research/fp4 | amendment/core | uninterrupted | 17 | 0.997981 | 18.0211 |
| z-ai/glm-5.3-flash / streamlake/fp8 | v1/v1 | uninterrupted | 8 | 0.123707 | 20.0733 |
| z-ai/glm-5.3-flash / streamlake/fp8 | amendment/core | uninterrupted | 17 | 0.650282 | 33.1167 |
| z-ai/glm-5.3-flash / parasail/fp4 | v1/v1 | uninterrupted | 8 | 0.49398 | 22.8325 |
| z-ai/glm-5.3-flash / reka | v1/v1 | uninterrupted | 7 | 0.420345 | 20.6027 |
| z-ai/glm-5.3-flash / reka | amendment/core | uninterrupted | 7 | 0.711825 | 29.497 |
| qwen/qwen3.8-27b / dekallm | v1/v1 | uninterrupted | 8 | 0.45064 | 2.2741 |
| qwen/qwen3.8-27b / phala | v1/v1 | uninterrupted | 8 | 0.242976 | 22.6409 |
| qwen/qwen3.8-27b / phala | amendment/core | uninterrupted | 16 | 0.986829 | 39.349 |
| qwen/qwen3.8-27b / cloudflare | v1/v1 | uninterrupted | 16 | 0 | 65.2612 |
| z-ai/glm-5.3-flash / phala/nvfp4 | v1/v1 | uninterrupted | 13 | 0.571029 | 33.1389 |
| z-ai/glm-5.3-flash / phala/nvfp4 | amendment/core | uninterrupted | 18 | 0.553786 | 47.9203 |
| z-ai/glm-5.3-flash / inference-net/us | v1/v1 | uninterrupted | 8 | 0.99888 | 32.2689 |
| z-ai/glm-5.3-flash / modal/fp4 | v1/v1 | uninterrupted | 8 | 0.122696 | 34.0223 |
| z-ai/glm-5.3-flash / fireworks/us | v1/v1 | uninterrupted | 8 | 0.995779 | 11.8323 |
| qwen/qwen3.8-27b / wafer/fp8 | v1/v1 | uninterrupted | 7 | 0.381682 | 3.13011 |
| qwen/qwen3.8-27b / tenstorrent/fp4 | v1/v1 | uninterrupted | 7 | 0.140506 | 34.9682 |
| qwen/qwen3.8-27b / novita | v1/v1 | uninterrupted | 0 | unknown | unknown |
| qwen/qwen3.8-27b / novita | amendment/core | uninterrupted | 10 | 0.730711 | 101.846 |
| qwen/qwen3.8-27b / darkbloom/fp4 | v1/v1 | uninterrupted | 8 | 0.0136158 | 8.49829 |
| z-ai/glm-5.3-flash / open-inference/fp4 | v1/v1 | uninterrupted | 6 | 0.9026 | 5.89219 |
| z-ai/glm-5.3-flash / open-inference/fp4 | amendment/core | uninterrupted | 18 | 0.968584 | 15.5159 |
| z-ai/glm-5.3-flash / open-inference/fp4 | amendment/long | uninterrupted | 0 | unknown | unknown |
| z-ai/glm-5.3-flash / primeintellect | v1/v1 | uninterrupted | 5 | 0.789665 | 14.0941 |
| z-ai/glm-5.3-flash / siliconflow/fp8 | v1/v1 | uninterrupted | 2 | 0.995553 | 7.89344 |
| z-ai/glm-5.3-flash / digitalocean | amendment/core | uninterrupted | 18 | 0.998337 | 23.1604 |
| z-ai/glm-5.3-flash / near-ai/fp8 | amendment/core | uninterrupted | 11 | 0.531975 | 30.8334 |
| qwen/qwen3.8-27b / ionstream/fp8 | v1/v1 | uninterrupted | 1 | 0.958976 | 1.67541 |
| qwen/qwen3.8-27b / modal | v1/v1 | uninterrupted | 1 | 0 | 2.48832 |
| z-ai/glm-5.3-flash / nextbit/fp4 | amendment/core | uninterrupted | 14 | 0.8364 | 31.3062 |
| z-ai/glm-5.3-flash / sail-research/us | amendment/core | uninterrupted | 15 | 0.99783 | 17.3576 |
| z-ai/glm-5.3-flash / gmicloud/fp8 | amendment/core | uninterrupted | 18 | 0.997691 | 11.6658 |
| z-ai/glm-5.3-flash / atlas-cloud/fp8 | amendment/core | uninterrupted | 12 | 0.0943144 | 122.481 |
| z-ai/glm-5.3-flash / novita/fp8 | amendment/core | uninterrupted | 18 | 0.997863 | 13.0568 |
| qwen/qwen3.8-27b / near-ai/fp8 | v1/v1 | uninterrupted | 0 | unknown | unknown |
| z-ai/glm-5.3-flash / particle-ai/nvfp4 | amendment/core | uninterrupted | 18 | 0.81271 | 33.0822 |
## r15e cost source and read-only generation cross-check

Per-call billed cost is streamed usage.cost; cumulative /key plus the retained-reservation ledger bounds spending. This audit changes no financial or live-run state.
Captured 743 accepted calls. Agreements: 742; mismatches: 0; unverified: 1. Largest absolute difference USD9E-10 (toleranceUSD1E-8).
Cost scope includes 7 accepted smoke/pilot calls for financial verification only. They never enter the research availability, cache metrics or effective-price figures above.
all accepted calls at fixed capture; no sampling. Per-call agreement and exact differences: cost-cross-check.csv and audit.json. Missing/limited generation records are unverified, never agreement.

## Frozen snapshot versus live endpoint prices

Live requests re-estimate reservations and projected effective prices against per-call live list prices. A rise is accepted if the shared cap permits it; the frozen snapshot remains the declared candidate list and historical comparison, not a price-rise refusal. Raw billed costs use usage.cost.
Every accepted call records its price source in audit.json. The historical seed rows lack per-call prices and are excluded from effective-price samples. Current snapshot/live rates, deltas and missing/new endpoints follow.

| Provider | Model / endpoint | Status | Changed fields: snapshot -> live (delta) |
|---|---|---|---|
| AkashML | qwen/qwen3.8-27b / akashml/fp8 | agreement | none |
| Alibaba | qwen/qwen3.8-27b / alibaba | agreement | none |
| Cerebras | qwen/qwen3.8-27b / cerebras/fp16 | agreement | none |
| Chutes | qwen/qwen3.8-27b / chutes/fp8 | agreement | none |
| Cloudflare | qwen/qwen3.8-27b / cloudflare | agreement | none |
| CoreWeave | qwen/qwen3.8-27b / coreweave/fp8 | agreement | none |
| Darkbloom | qwen/qwen3.8-27b / darkbloom/fp4 | agreement | none |
| DeepInfra | qwen/qwen3.8-27b / deepinfra/bf16 | agreement | none |
| DekaLLM | qwen/qwen3.8-27b / dekallm | agreement | none |
| Ionstream | qwen/qwen3.8-27b / ionstream/fp8 | agreement | none |
| Mancer 2 | qwen/qwen3.8-27b / mancer/fp8 | agreement | none |
| Modal | qwen/qwen3.8-27b / modal | agreement | none |
| ModelRun | qwen/qwen3.8-27b / modelrun/fp4 | agreement | none |
| Near AI | qwen/qwen3.8-27b / near-ai/fp8 | agreement | none |
| Novita | qwen/qwen3.8-27b / novita | agreement | none |
| Parasail | qwen/qwen3.8-27b / parasail/fp8 | agreement | none |
| Phala | qwen/qwen3.8-27b / phala | agreement | none |
| PrimeIntellect | qwen/qwen3.8-27b / primeintellect/fp8 | drift | prompt: 0.000000022 -> 0.000000029 (7E-9), completion: 0.0000012 -> 0.000001591 (3.91E-7), input_cache_read: 0.00000002 -> 0.000000026 (6E-9) |
| Reka | qwen/qwen3.8-27b / reka/fp8 | agreement | none |
| StreamLake | qwen/qwen3.8-27b / streamlake | drift | prompt: 0.0000003 -> 0.00000025 (-5E-8), completion: 0.0000018 -> 0.0000015 (-3E-7), input_cache_read: 0.00000006 -> 0.00000005 (-1E-8) |
| Tenstorrent | qwen/qwen3.8-27b / tenstorrent/fp4 | agreement | none |
| Venice | qwen/qwen3.8-27b / venice/fp8 | agreement | none |
| Wafer | qwen/qwen3.8-27b / wafer/fp8 | agreement | none |
| AtlasCloud | z-ai/glm-5.3-flash / atlas-cloud/fp8 | agreement | none |
| BaseTen | z-ai/glm-5.3-flash / baseten/fp8 | agreement | none |
| BaseTen | z-ai/glm-5.3-flash / baseten/fp8/us | agreement | none |
| Cohere | z-ai/glm-5.3-flash / cohere | agreement | none |
| CoreWeave | z-ai/glm-5.3-flash / coreweave/nvfp4 | agreement | none |
| Crusoe | z-ai/glm-5.3-flash / crusoe/fp4 | agreement | none |
| Darkbloom | z-ai/glm-5.3-flash / darkbloom/fp4 | agreement | none |
| DeepInfra | z-ai/glm-5.3-flash / deepinfra/fp4 | agreement | none |
| DigitalOcean | z-ai/glm-5.3-flash / digitalocean | agreement | none |
| Fireworks | z-ai/glm-5.3-flash / fireworks | agreement | none |
| Fireworks | z-ai/glm-5.3-flash / fireworks/us | agreement | none |
| Friendli | z-ai/glm-5.3-flash / friendli | agreement | none |
| GMICloud | z-ai/glm-5.3-flash / gmicloud/fp8 | agreement | none |
| Inceptron | z-ai/glm-5.3-flash / inceptron/fp8 | agreement | none |
| InferenceNet | z-ai/glm-5.3-flash / inference-net/fp4 | agreement | none |
| InferenceNet | z-ai/glm-5.3-flash / inference-net/us | agreement | none |
| Makora | z-ai/glm-5.3-flash / makora | agreement | none |
| Mistral | z-ai/glm-5.3-flash / mistral | agreement | none |
| Modal | z-ai/glm-5.3-flash / modal/fp4 | agreement | none |
| Morph | z-ai/glm-5.3-flash / morph/fp8 | drift | prompt: 0.000000042 -> 0.000000047 (5E-9), input_cache_read: 0.000000018 -> 0.00000002 (2E-9) |
| Near AI | z-ai/glm-5.3-flash / near-ai/fp8 | agreement | none |
| Nebius | z-ai/glm-5.3-flash / nebius/fp4 | agreement | none |
| NextBit | z-ai/glm-5.3-flash / nextbit/fp4 | agreement | none |
| Novita | z-ai/glm-5.3-flash / novita/fp8 | agreement | none |
| OpenInference | z-ai/glm-5.3-flash / open-inference/fp4 | drift | prompt: 0.000000033 -> 0.0000000283 (-4.7E-9), completion: 0.000000242 -> 0.000000208 (-3.4E-8), input_cache_read: 0.000000022 -> 0.0000000189 (-3.1E-9) |
| Parasail | z-ai/glm-5.3-flash / parasail/fp4 | agreement | none |
| Particle AI | z-ai/glm-5.3-flash / particle-ai/nvfp4 | agreement | none |
| Phala | z-ai/glm-5.3-flash / phala/nvfp4 | agreement | none |
| PrimeIntellect | z-ai/glm-5.3-flash / primeintellect | agreement | none |
| Reka | z-ai/glm-5.3-flash / reka | agreement | none |
| Relace | z-ai/glm-5.3-flash / relace/fp4 | drift | prompt: 0.0000000313 -> 0.0000000269 (-4.4E-9), completion: 0.0000000846 -> 0.0000000996 (1.50E-8), input_cache_read: 0.00000003 -> 0.0000000269 (-3.1E-9) |
| Sail Research | z-ai/glm-5.3-flash / sail-research/fp4 | agreement | none |
| Sail Research | z-ai/glm-5.3-flash / sail-research/us | agreement | none |
| SiliconFlow | z-ai/glm-5.3-flash / siliconflow/fp8 | agreement | none |
| StreamLake | z-ai/glm-5.3-flash / streamlake/fp8 | agreement | none |
| Tenstorrent | z-ai/glm-5.3-flash / tenstorrent/fp8 | new-endpoint | none |
| Together | z-ai/glm-5.3-flash / together | agreement | none |
| Venice | z-ai/glm-5.3-flash / venice | agreement | none |
| Wafer | z-ai/glm-5.3-flash / wafer/nvfp4 | agreement | none |
| Wafer | z-ai/glm-5.3-flash / wafer/us | agreement | none |
| Z.AI | z-ai/glm-5.3-flash / z-ai/fp8 | agreement | none |
