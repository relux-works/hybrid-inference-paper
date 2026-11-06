# Engine run25 — dedicated fleets, closed contour and coverage

Parent: accepted run24 `ca7f228a` (Muse r5x6 ACCEPT). Separate sensitivity; every accepted parent-tracked byte, including run24, stays unchanged. No GPU/CPU inference, downloads or API requests.

## Why the accepted fleet has four nodes

The lower bound is retained-session STORAGE, not peak concurrency: `calc/hybridcalc/measurements_r20.py:99` (`storage_boxes`), called before compute sizing at `:181` (`hybrid`). Run23 uses this inherited code through `calc/run22/economics.py:108`. The249k reservation comes from `calc/hybridcalc/measurements_r21.py:77` and `calc/run23/engine.py:96`.

PRO default KV is65,536B/token and recurrent resident state156,893,184B: a249,000-token copy is16,475,357,184B. Of96GB VRAM,27GB weights and8GB workspace leave61GB, admitting3 reserved GPU copies (measured decode surface also caps residency). Per-node900GB NVMe holds floor(900e9/16,475,357,184)=54 copies. Four sessions/person ×50people=200 copies; ceil(200/(54+3))=4 nodes. At4 nodes12/200 copies are resident, giving94% expected misses. The subsequent compute test does not add a light-load node. Claudedeep still pays for200 copies even when routing offloads zero calls.

The accepted $56.6446/person-month =4×$614.0575/50+$2.52 client energy+$5 front. Light service occupancy3.61399% is an allocated-service model output, not a measured GPU-utilization trace. The accepted fleet is sufficient; minimality across alternative retention policies was never established.

## Explicit unmeasured proxies and admission

All sensitivity checkpoints live OFF GPU. Every catch-up reads a full server-format copy, replays the existing expected pending work, and writes a full updated checkpoint. Client bf16 wire remains78,446,592B recurrent state plus34,816B/delta token; it does not halve the server checkpoint. No cold-prefix rebuild is charged in addition to restore. State serialization/conversion metadata overhead beyond byte IO is assumed zero, unmeasured; ×2 IO sensitivity does not calibrate that overhead. No runtime vLLM slot-restore implementation is claimed.

Inherited NVMe:900GB usable/node,256GB host RAM declared but no cache credited. Expanded NVMe:3.6TB usable/node,256GB RAM, extra$400 capex/node. Warm RAM:3.6TB usable RAM/node,900GB NVMe not counted for warm capacity, extra$10,000 capex/node; volatile, no cold persistence guarantee. Expansion prices are declared scenarios, not sourced offers or hardware recommendations. They use the accepted residual/depreciation/support formula. The NEW fleet policy is bought-office only; rental rows in the closed-contour control retain the accepted run24 engine and egress accounting. The new office proxy refuses rental billing.

NVMe read/write7GB/s uses the existing declared tier bandwidth; RAM50GB/s is min(100GB/s RAM,50GB/s PCIe). Both are UNMEASURED server restore proxies, with×2 slower read AND write. The actual Mac/LaCie reference (`calc/run23/data/MAC-FACTS.md`) is18.425GB/20.523s first and2.965s warm at524k;36.4GB/about40.5s at1.04M, warm/no purge. Those timings are context, not server measurements or server conversion calibration.

Accepted routing treats calls as exchangeable Bernoulli opportunities (`calc/hybridcalc/session_hosting.py:15`); no ordered arrival process was delivered. Here independent homogeneous Poisson arrivals are an UNMEASURED proxy at accepted calls/day over8h, randomly split across nodes. Per-node M/G/1 mean delay is λE[S²]/(2(1−ρ)); collisions are charged. Restore, catch-up, response wire and checkpoint write reserve the node sequentially. Overflow generation uses the accepted depth-dependent measured PRO batch surface/finite4T concurrency as equivalent service work; that queue surrogate does not reproduce the real batching scheduler or its latency distribution. Tool/session occupancy is retained in the equivalent overflow work.

For each fleet we test queue budgets0,.05,.1,.25,.5,1,2,3,4,5seconds, rerun the greatest-stable offload policy with restore+charged queue+pending catch-up, and recompute client capacity/overflow and service moments. A row is certified only if actual modelled mean queue ≤charged budget and service occupancy≤70%. Minimum means the first integer fleet certified on this declared queue grid, not a hardware/runtime optimum. Storage/latency/compute shortfalls have no finite cost or ratio. Mean TTFT covers local and offloaded client-served calls; the offload mean includes client import, link and pending. Overflow uses a workload proxy, so its request TTFT and latency tails remain unqualified. No peak-arrival or p95 guarantee is inferred.

When the offload queue cannot certify, the policy explicitly tries LOCAL PREFILL, retaining all required copies and charging any generation exceeding Mac capacity to the server. This can make a smaller fleet feasible with zero prefill offload; it is a retention/local-compute alternative, not an offload speedup. Overflow also catches up the deferred local journal. With no offloads, expected local replay work per overflow refresh is capped by the full existing-prefix cold-work bound; with positive offload share the existing offload-only pending bound is also charged to overflow conservatively. Full-depth copy bytes reserve an upper bound for an older checkpoint; no fresh checkpoint or free replay is invented.

The overflow TTFT column is an UNMEASURED surrogate: mean restore+cached prefill+journal+charged node queue+link RTT, with no client state import. The all-call TTFT combines this with client-served TTFT by their actual served/overflow counts. It is not a measured batching scheduler latency. The latency table keeps the client-only and all-call means separate.

## Team50 fleet costs and latency

All following prices are per person-month, owned M5 Max64 PRI31, bf16-default transport, bought PRO vLLM node over office125MB/s, RTT1ms. Light/medium are typical; heavy2500calls/day is the owner’s intensity. s=.2 prices only the open-model segment (80% still goes to a stronger cloud model); s=1 sends every model call in-house. These are normalized selected-shape scenarios, never full-log performance claims.

Cost cells show USD/person-month and node service occupancy together. Shortfall cells have no finite cost.

| Profile | s | Restore proxy | Fleet | Light $ / occupancy | Medium $ / occupancy | Heavy $ / occupancy | Heavy nodes if minimum |
|---|---:|---|---|---:|---:|---:|---:|
| existing_combined | 0.2 | inherited_nvme ×1 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 0.2 | inherited_nvme ×1 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 0.2 | inherited_nvme ×1 | 4 | 56.645 / 5.96% | 56.645 / 22.44% | 56.645 / 0.00% |  |
| existing_combined | 0.2 | inherited_nvme ×1 | minimum | 56.645 / 5.96% | 56.645 / 22.44% | 56.645 / 0.00% | 4 |
| existing_combined | 0.2 | inherited_nvme ×2 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 0.2 | inherited_nvme ×2 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 0.2 | inherited_nvme ×2 | 4 | 56.645 / 7.07% | 56.645 / 24.08% | 56.645 / 0.00% |  |
| existing_combined | 0.2 | inherited_nvme ×2 | minimum | 56.645 / 7.07% | 56.645 / 24.08% | 56.645 / 0.00% | 4 |
| existing_combined | 0.2 | expanded_nvme ×1 | 1 | 19.948 / 22.44% | 19.948 / 0.00% | 19.948 / 0.00% |  |
| existing_combined | 0.2 | expanded_nvme ×1 | 2 | 32.376 / 11.69% | 32.376 / 36.91% | 32.376 / 0.00% |  |
| existing_combined | 0.2 | expanded_nvme ×1 | 4 | 57.231 / 5.96% | 57.231 / 22.44% | 57.231 / 0.00% |  |
| existing_combined | 0.2 | expanded_nvme ×1 | minimum | 19.948 / 22.44% | 19.948 / 0.00% | 19.948 / 0.00% | 1 |
| existing_combined | 0.2 | expanded_nvme ×2 | 1 | 19.948 / 24.08% | 19.948 / 0.00% | 19.948 / 0.00% |  |
| existing_combined | 0.2 | expanded_nvme ×2 | 2 | 32.376 / 12.87% | 32.376 / 0.00% | 32.376 / 0.00% |  |
| existing_combined | 0.2 | expanded_nvme ×2 | 4 | 57.231 / 7.07% | 57.231 / 24.08% | 57.231 / 0.00% |  |
| existing_combined | 0.2 | expanded_nvme ×2 | minimum | 19.948 / 24.08% | 19.948 / 0.00% | 19.948 / 0.00% | 1 |
| existing_combined | 0.2 | all_ram_warm ×1 | 1 | 23.468 / 19.07% | 23.468 / 0.00% | 23.468 / 0.00% |  |
| existing_combined | 0.2 | all_ram_warm ×1 | 2 | 39.416 / 9.70% | 39.416 / 35.62% | 39.416 / 0.00% |  |
| existing_combined | 0.2 | all_ram_warm ×1 | 4 | 71.311 / 4.89% | 71.311 / 19.07% | 71.311 / 0.00% |  |
| existing_combined | 0.2 | all_ram_warm ×1 | minimum | 23.468 / 19.07% | 23.468 / 0.00% | 23.468 / 0.00% | 1 |
| existing_combined | 0.2 | all_ram_warm ×2 | 1 | 23.468 / 19.08% | 23.468 / 0.00% | 23.468 / 0.00% |  |
| existing_combined | 0.2 | all_ram_warm ×2 | 2 | 39.416 / 10.09% | 39.416 / 36.82% | 39.416 / 0.00% |  |
| existing_combined | 0.2 | all_ram_warm ×2 | 4 | 71.311 / 5.10% | 71.311 / 19.08% | 71.311 / 0.00% |  |
| existing_combined | 0.2 | all_ram_warm ×2 | minimum | 23.468 / 19.08% | 23.468 / 0.00% | 23.468 / 0.00% | 1 |
| existing_combined | 1.0 | inherited_nvme ×1 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 1.0 | inherited_nvme ×1 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 1.0 | inherited_nvme ×1 | 4 | 56.645 / 26.45% | 56.645 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | inherited_nvme ×1 | minimum | 56.645 / 26.45% | 56.645 / 0.00% | finite_concurrency_shortfall |  |
| existing_combined | 1.0 | inherited_nvme ×2 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 1.0 | inherited_nvme ×2 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| existing_combined | 1.0 | inherited_nvme ×2 | 4 | 56.645 / 27.23% | 56.645 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | inherited_nvme ×2 | minimum | 56.645 / 27.23% | 56.645 / 0.00% | finite_concurrency_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×1 | 1 | 19.948 / 0.00% | 19.948 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×1 | 2 | 32.376 / 0.00% | 32.376 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×1 | 4 | 57.231 / 26.45% | 57.231 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×1 | minimum | 19.948 / 0.00% | 19.948 / 0.00% | finite_concurrency_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×2 | 1 | 19.948 / 0.00% | 19.948 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×2 | 2 | 32.376 / 0.00% | 32.376 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×2 | 4 | 57.231 / 27.23% | 57.231 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | expanded_nvme ×2 | minimum | 19.948 / 0.00% | 19.948 / 0.00% | finite_concurrency_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×1 | 1 | 23.468 / 0.00% | 23.468 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×1 | 2 | 39.416 / 42.60% | 39.416 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×1 | 4 | 71.311 / 23.01% | 71.311 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×1 | minimum | 23.468 / 0.00% | 23.468 / 0.00% | finite_concurrency_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×2 | 1 | 23.468 / 0.00% | 23.468 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×2 | 2 | 39.416 / 43.86% | 39.416 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×2 | 4 | 71.311 / 23.85% | 71.311 / 0.00% | latency_or_compute_shortfall |  |
| existing_combined | 1.0 | all_ram_warm ×2 | minimum | 23.468 / 0.00% | 23.468 / 0.00% | finite_concurrency_shortfall |  |
| claude_deep | 0.2 | inherited_nvme ×1 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 0.2 | inherited_nvme ×1 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 0.2 | inherited_nvme ×1 | 4 | 56.645 / 0.00% | 56.645 / 0.00% | 56.645 / 0.00% |  |
| claude_deep | 0.2 | inherited_nvme ×1 | minimum | 56.645 / 0.00% | 56.645 / 0.00% | 56.645 / 0.00% | 4 |
| claude_deep | 0.2 | inherited_nvme ×2 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 0.2 | inherited_nvme ×2 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 0.2 | inherited_nvme ×2 | 4 | 56.645 / 0.00% | 56.645 / 0.00% | 56.645 / 0.00% |  |
| claude_deep | 0.2 | inherited_nvme ×2 | minimum | 56.645 / 0.00% | 56.645 / 0.00% | 56.645 / 0.00% | 4 |
| claude_deep | 0.2 | expanded_nvme ×1 | 1 | 19.948 / 0.00% | 19.948 / 0.00% | 19.948 / 0.00% |  |
| claude_deep | 0.2 | expanded_nvme ×1 | 2 | 32.376 / 0.00% | 32.376 / 0.00% | 32.376 / 0.00% |  |
| claude_deep | 0.2 | expanded_nvme ×1 | 4 | 57.231 / 0.00% | 57.231 / 0.00% | 57.231 / 0.00% |  |
| claude_deep | 0.2 | expanded_nvme ×1 | minimum | 19.948 / 0.00% | 19.948 / 0.00% | 19.948 / 0.00% | 1 |
| claude_deep | 0.2 | expanded_nvme ×2 | 1 | 19.948 / 0.00% | 19.948 / 0.00% | 19.948 / 0.00% |  |
| claude_deep | 0.2 | expanded_nvme ×2 | 2 | 32.376 / 0.00% | 32.376 / 0.00% | 32.376 / 0.00% |  |
| claude_deep | 0.2 | expanded_nvme ×2 | 4 | 57.231 / 0.00% | 57.231 / 0.00% | 57.231 / 0.00% |  |
| claude_deep | 0.2 | expanded_nvme ×2 | minimum | 19.948 / 0.00% | 19.948 / 0.00% | 19.948 / 0.00% | 1 |
| claude_deep | 0.2 | all_ram_warm ×1 | 1 | 23.468 / 0.00% | 23.468 / 0.00% | 23.468 / 0.00% |  |
| claude_deep | 0.2 | all_ram_warm ×1 | 2 | 39.416 / 0.00% | 39.416 / 0.00% | 39.416 / 0.00% |  |
| claude_deep | 0.2 | all_ram_warm ×1 | 4 | 71.311 / 0.00% | 71.311 / 0.00% | 71.311 / 0.00% |  |
| claude_deep | 0.2 | all_ram_warm ×1 | minimum | 23.468 / 0.00% | 23.468 / 0.00% | 23.468 / 0.00% | 1 |
| claude_deep | 0.2 | all_ram_warm ×2 | 1 | 23.468 / 0.00% | 23.468 / 0.00% | 23.468 / 0.00% |  |
| claude_deep | 0.2 | all_ram_warm ×2 | 2 | 39.416 / 0.00% | 39.416 / 0.00% | 39.416 / 0.00% |  |
| claude_deep | 0.2 | all_ram_warm ×2 | 4 | 71.311 / 0.00% | 71.311 / 0.00% | 71.311 / 0.00% |  |
| claude_deep | 0.2 | all_ram_warm ×2 | minimum | 23.468 / 0.00% | 23.468 / 0.00% | 23.468 / 0.00% | 1 |
| claude_deep | 1.0 | inherited_nvme ×1 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 1.0 | inherited_nvme ×1 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 1.0 | inherited_nvme ×1 | 4 | 56.645 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | inherited_nvme ×1 | minimum | 56.645 / 0.00% | 388.236 / 17.73% | finite_concurrency_shortfall |  |
| claude_deep | 1.0 | inherited_nvme ×2 | 1 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 1.0 | inherited_nvme ×2 | 2 | storage_shortfall | storage_shortfall | storage_shortfall |  |
| claude_deep | 1.0 | inherited_nvme ×2 | 4 | 56.645 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | inherited_nvme ×2 | minimum | 56.645 / 0.00% | 461.923 / 16.95% | finite_concurrency_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×1 | 1 | 19.948 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×1 | 2 | 32.376 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×1 | 4 | 57.231 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×1 | minimum | 19.948 / 0.00% | 392.782 / 17.73% | finite_concurrency_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×2 | 1 | 19.948 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×2 | 2 | 32.376 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×2 | 4 | 57.231 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | expanded_nvme ×2 | minimum | 19.948 / 0.00% | 467.349 / 16.95% | finite_concurrency_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×1 | 1 | 23.468 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×1 | 2 | 39.416 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×1 | 4 | 71.311 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×1 | minimum | 23.468 / 0.00% | 438.111 / 18.15% | finite_concurrency_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×2 | 1 | 23.468 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×2 | 2 | 39.416 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×2 | 4 | 71.311 / 0.00% | latency_or_compute_shortfall | latency_or_compute_shortfall |  |
| claude_deep | 1.0 | all_ram_warm ×2 | minimum | 23.468 / 0.00% | 438.111 / 18.44% | finite_concurrency_shortfall |  |

## Closed contour on the accepted dedicated basis

s=20% thresholds describe a segment: the other80% goes to a stronger cloud model. They cannot substantiate an all-in-house closed contour. Only s=100% rows below make every call open-model/in-house. Own cluster uses the same PRO6000 engine and billing as its hybrid alternative. This is the inherited no-queue fleet control; the alternative off-GPU policies and mean delays are separate in `crossings.csv`.

| Profile | s | Billing / link | Load | Hybrid $ / service occupancy at50 | Own $ / service occupancy at50 | Sustained hybrid win through500 |
|---|---:|---|---|---:|---:|---|
| existing_combined | 0.2 | bought / office125MB/s RTT1ms | light | 56.645 / 3.61% | 49.125 / 50.07% | no sustained crossing through 500 people |
| existing_combined | 0.2 | rented / engine WAN112.5MB/s RTT400ms estimated | light | 142.343 / 3.38% | 134.675 / 50.07% | no sustained crossing through 500 people |
| existing_combined | 0.2 | bought / office125MB/s RTT1ms | medium | 56.645 / 14.46% | 135.093 / 66.46% | cheaper from 5 people through 500 scanned people |
| existing_combined | 0.2 | rented / engine WAN112.5MB/s RTT400ms estimated | medium | 142.789 / 13.51% | 358.823 / 66.46% | cheaper from 5 people through 500 scanned people |
| existing_combined | 0.2 | bought / office125MB/s RTT1ms | heavy | 56.645 / 45.17% | 331.591 / 66.61% | cheaper from 2 people through 500 scanned people |
| existing_combined | 0.2 | rented / engine WAN112.5MB/s RTT400ms estimated | heavy | 144.051 / 42.21% | 871.161 / 66.61% | cheaper from 2 people through 500 scanned people |
| existing_combined | 1.0 | bought / office125MB/s RTT1ms | light | 56.645 / 18.07% | 159.655 / 68.38% | cheaper from 4 people through 500 scanned people |
| existing_combined | 1.0 | rented / engine WAN112.5MB/s RTT400ms estimated | light | 142.937 / 16.89% | 422.865 / 68.38% | cheaper from 4 people through 500 scanned people |
| existing_combined | 1.0 | bought / office125MB/s RTT1ms | medium | 68.926 / 58.64% | 442.121 / 68.41% | cheaper from 2 people through 500 scanned people |
| existing_combined | 1.0 | rented / engine WAN112.5MB/s RTT400ms estimated | medium | 145.165 / 67.54% | 1159.351 / 68.41% | cheaper from 2 people through 500 scanned people |
| existing_combined | 1.0 | bought / office125MB/s RTT1ms | heavy | 1468.977 / 27.45% | 761.431 / 67.31% | no sustained crossing through 500 people |
| existing_combined | 1.0 | rented / engine WAN112.5MB/s RTT400ms estimated | heavy | 3840.834 / 27.51% | 1991.901 / 67.31% | no sustained crossing through 500 people |
| claude_deep | 0.2 | bought / office125MB/s RTT1ms | light | 56.645 / 0.00% | 61.406 / 57.56% | no sustained crossing through 500 people |
| claude_deep | 0.2 | rented / engine WAN112.5MB/s RTT400ms estimated | light | 142.195 / 0.00% | 166.696 / 57.56% | cheaper from 73 people through 500 scanned people |
| claude_deep | 0.2 | bought / office125MB/s RTT1ms | medium | 56.645 / 0.00% | 184.217 / 68.95% | cheaper from 4 people through 500 scanned people |
| claude_deep | 0.2 | rented / engine WAN112.5MB/s RTT400ms estimated | medium | 142.195 / 0.00% | 486.907 / 68.95% | cheaper from 4 people through 500 scanned people |
| claude_deep | 0.2 | bought / office125MB/s RTT1ms | heavy | 56.645 / 0.00% | 454.403 / 69.17% | cheaper from 2 people through 500 scanned people |
| claude_deep | 0.2 | rented / engine WAN112.5MB/s RTT400ms estimated | heavy | 142.195 / 0.00% | 1191.373 / 69.17% | cheaper from 2 people through 500 scanned people |
| claude_deep | 1.0 | bought / office125MB/s RTT1ms | light | 56.645 / 0.00% | 221.061 / 69.45% | cheaper from 3 people through 500 scanned people |
| claude_deep | 1.0 | rented / engine WAN112.5MB/s RTT400ms estimated | light | 142.195 / 0.00% | 582.971 / 69.45% | cheaper from 3 people through 500 scanned people |
| claude_deep | 1.0 | bought / office125MB/s RTT1ms | medium | 167.175 / 63.34% | 638.620 / 69.19% | cheaper from 1 people through 500 scanned people |
| claude_deep | 1.0 | rented / engine WAN112.5MB/s RTT400ms estimated | medium | 430.385 / 63.34% | 1671.690 / 69.19% | cheaper from 1 people through 500 scanned people |
| claude_deep | 1.0 | bought / office125MB/s RTT1ms | heavy | capacity shortfall | capacity shortfall | no sustained crossing through 500 people |
| claude_deep | 1.0 | rented / engine WAN112.5MB/s RTT400ms estimated | heavy | capacity shortfall | capacity shortfall | no sustained crossing through 500 people |

## Coverage and representativeness

The owner package explicitly excludes raw per-call CSV, transcripts and timestamps (`data/measurements/ivmbp-2026-10-30/README.md`, `REPORT.md`). Exact joint observed subset input/output/work shares cannot be recomputed from marginal aggregates. The accepted10,885/39,904(27.28%) is a share of fitted CALL SHAPES, normalized to declared intensity, not a measured share of total work or tokens. Claudedeep is a1000-point aggregate reconstruction. Blank observed-share columns mean unknown; fitted estimates below are not promoted to measured log fractions.

| Fitted profile | Shape share | Full-input token share | New-token share | Output-token share | Prefill seconds share | Decode seconds share | Work seconds share |
|---|---:|---:|---:|---:|---:|---:|---:|
| existing_combined | 27.28% | 20.52% | 65.41% | 27.38% | 58.88% | 24.04% | 28.68% |
| claude_deep | 55.40% | 24.88% | 69.41% | 45.58% | 44.77% | 28.02% | 29.43% |

Work proxy =M5 measured-anchor prefill seconds +single-stream decode seconds, excluding tool pauses. Outside the measured ladder it uses the accepted depth/delta extrapolation, so the full-profile denominator is modelled. No exact measured-only full-work fraction is available. The code records any context clipping; clipped shapes are never admitted as valid hardware requests.

The representativeness sensitivity reweights the measured shapes by maximum entropy to match the FULL FITTED profile’s mean NEW and OUTPUT tokens, reprices each API provider and reranks it, and recalculates hybrid/own-server work using the same weights. It preserves the measured shape envelope, but does not recover deep input-context distributions, correlations or real arrivals. The deep full mean input exceeds the measured subset’s attainable range; it cannot be fixed by honest in-envelope reweighting. Results are conditional stress tests, not a full-log correction.

| Profile | s | Load | Expanded NVMe speed | Accepted-shape minimum win vs own | Reweighted minimum win vs own | Reweighted $ at50 | Reweighted offload at50 |
|---|---:|---|---:|---|---|---:|---:|
| existing_combined | 0.2 | light | 1 | cheaper from 15 people through 500 scanned people | cheaper from 15 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| existing_combined | 0.2 | medium | 1 | cheaper from 5 people through 500 scanned people | cheaper from 5 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| existing_combined | 0.2 | heavy | 1 | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| existing_combined | 1.0 | light | 1 | cheaper from 4 people through 500 scanned people | cheaper from 4 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| existing_combined | 1.0 | medium | 1 | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| existing_combined | 1.0 | heavy | 1 | no sustained crossing through 500 people | no sustained crossing through 500 people | finite_concurrency_shortfall |  |
| claude_deep | 0.2 | light | 1 | cheaper from 13 people through 500 scanned people | cheaper from 10 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| claude_deep | 0.2 | medium | 1 | cheaper from 4 people through 500 scanned people | cheaper from 3 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| claude_deep | 0.2 | heavy | 1 | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| claude_deep | 1.0 | light | 1 | cheaper from 3 people through 500 scanned people | cheaper from 3 people through 500 scanned people | 19.948 / 0.00% | 0.0 |
| claude_deep | 1.0 | medium | 1 | cheaper from 1 people through 500 scanned people | no sustained crossing through 500 people | finite_concurrency_shortfall |  |
| claude_deep | 1.0 | heavy | 1 | no sustained crossing through 500 people | no sustained crossing through 500 people | finite_concurrency_shortfall |  |

## Reading the compact outputs

`fleet_summary.csv` carries capacity, shortfalls, charged/actual mean queue, restore/read/write, TTFT, utilization, offload and client/overflow capacity. `comparisons.csv` reports own/API ratios at50 for BOTH v1-long-pause and amendment-core cadence, no-cache/owner98.1%/measured points; Qwen core measured remains unknown. Thin final-study points remain descriptive, especially the one-warm-call Qwen v1 cheapest point. `crossings.csv` scans every integer1..500: fixed fleets can win on intervals then fail storage, so first win is not mislabelled a sustained crossing. Every case includes1/2/4 nodes and the first certified minimum. `closed_contour.csv` preserves the accepted fleet control at both shares. Coverage, reweighting and per-depth full-copy sizes are separate small CSVs. No full quote dump is generated.

API references retain the accepted run24 whole-window admission, cadence and aggregate-token price formula, including unknown core measured Qwen. Reweighted API prices assume the same cache fractions and live tariffs transfer to the altered token mix. Comparisons of the open-model segment do not price the stronger-cloud remainder. The API is only a reference for closed-contour teams, which cannot use it.

Dedicated paid storage is retained even for zero offloads; such rows may be cheaper solely because fewer boxes retain copies. They do not demonstrate useful prefill offload. Light-load one-node costs require the declared expanded capacity; one inherited900GB node REFUSES. The warm3.6TB RAM configuration and its capex are hypothetical. Failure of the assumed runtime checkpoint restore/serialization, hardware attachment, arrivals or latency policy invalidates that sensitivity, without changing accepted run24.

Validation receipts and source/file hashes are in `calc/out/run25/manifest.json`; executable paired negatives cover storage/latency rejection, queue instability, checkpoint writeback, pending catch-up, token reweighting, refusal-sensitive crossings and unchanged uniform-weight own-cluster controls. No independent run25 acceptance is claimed.

## Changed crossings and the latency price

At the accepted light-load routing, prefill83.2663 GPU-seconds/person-day ×50=4163.3 GPU-seconds/day. One node has28800×70%=20160 service-seconds/day: this work alone fits one node. That is a diagnostic holding routing fixed, not a claim the original900GB one-node retention policy fits. Failed sensitivity rows mean no fleet certified under the declared storage/mean-delay/occupancy/concurrency rules, not measured physical impossibility.

Sensitivity service occupancy reserves the node during IO, wire and equivalent GPU work; it is not GPU-busy utilization and differs in scope from the accepted3.61% GPU-service diagnostic. Calendar occupancy uses the same node-reservation scope.

Rented all-open-model rows assume the dedicated rental is approved inside the team trust boundary; this removes external model APIs but does not establish a physical office perimeter or provider privacy assurance. Bought-office rows are the closed-contour headline.

All rows below use accepted fitted call shapes, bf16, owned M5Max64 PRI31 and bought PRO6000 vLLM over office125MB/s RTT1ms; expanded3.6TB NVMe,7GB/s full read/write and declared$400/node capex upgrade. Minimum fleet is certified against the declared Poisson/random-node mean-queue model (≤5s,≤70% service occupancy), not a measured scheduler. Copy retention is4/person; fractions cover call shapes normalized per person-month, not full work. API rows use their stated cadence/cache point; core measured Qwen remains unknown.

| Profile | s | Load | Reference | Cache/cadence | Accepted sustained crossing | Sensitivity sustained crossing | First feasible win |
|---|---:|---|---|---|---|---|---:|
| existing_combined | 0.2 | light | own_cluster | not applicable/not applicable | no sustained crossing through 500 people | cheaper from 15 people through 500 scanned people | 15 |
| existing_combined | 0.2 | light | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| existing_combined | 0.2 | light | api_median | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| existing_combined | 0.2 | medium | own_cluster | not applicable/not applicable | cheaper from 5 people through 500 scanned people | cheaper from 5 people through 500 scanned people | 5 |
| existing_combined | 0.2 | medium | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| existing_combined | 0.2 | medium | api_median | measured/v1_long_pause | no sustained crossing through 500 people | cheaper from 18 people through 500 scanned people | 18 |
| existing_combined | 0.2 | heavy | own_cluster | not applicable/not applicable | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | 2 |
| existing_combined | 0.2 | heavy | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | cheaper from 21 people through 500 scanned people | 21 |
| existing_combined | 0.2 | heavy | api_median | measured/v1_long_pause | cheaper from 5 people through 500 scanned people | cheaper from 6 people through 500 scanned people | 6 |
| existing_combined | 1.0 | light | own_cluster | not applicable/not applicable | cheaper from 4 people through 500 scanned people | cheaper from 4 people through 500 scanned people | 4 |
| existing_combined | 1.0 | light | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| existing_combined | 1.0 | light | api_median | measured/v1_long_pause | cheaper from 272 people through 500 scanned people | cheaper from 14 people through 500 scanned people | 14 |
| existing_combined | 1.0 | medium | own_cluster | not applicable/not applicable | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | 2 |
| existing_combined | 1.0 | medium | api_cheapest | measured/v1_long_pause | cheaper from 267 people through 500 scanned people | cheaper from 12 people through 500 scanned people | 12 |
| existing_combined | 1.0 | medium | api_median | measured/v1_long_pause | cheaper from 4 people through 500 scanned people | cheaper from 4 people through 500 scanned people | 4 |
| existing_combined | 1.0 | heavy | own_cluster | not applicable/not applicable | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| existing_combined | 1.0 | heavy | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| existing_combined | 1.0 | heavy | api_median | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 0.2 | light | own_cluster | not applicable/not applicable | no sustained crossing through 500 people | cheaper from 13 people through 500 scanned people | 13 |
| claude_deep | 0.2 | light | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 0.2 | light | api_median | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 0.2 | medium | own_cluster | not applicable/not applicable | cheaper from 4 people through 500 scanned people | cheaper from 4 people through 500 scanned people | 4 |
| claude_deep | 0.2 | medium | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 0.2 | medium | api_median | measured/v1_long_pause | no sustained crossing through 500 people | cheaper from 16 people through 500 scanned people | 16 |
| claude_deep | 0.2 | heavy | own_cluster | not applicable/not applicable | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | 2 |
| claude_deep | 0.2 | heavy | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | cheaper from 18 people through 500 scanned people | 18 |
| claude_deep | 0.2 | heavy | api_median | measured/v1_long_pause | cheaper from 5 people through 500 scanned people | cheaper from 5 people through 500 scanned people | 5 |
| claude_deep | 1.0 | light | own_cluster | not applicable/not applicable | cheaper from 3 people through 500 scanned people | cheaper from 3 people through 500 scanned people | 3 |
| claude_deep | 1.0 | light | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 1.0 | light | api_median | measured/v1_long_pause | cheaper from 60 people through 500 scanned people | cheaper from 13 people through 500 scanned people | 13 |
| claude_deep | 1.0 | medium | own_cluster | not applicable/not applicable | cheaper from 1 people through 500 scanned people | cheaper from 1 people through 500 scanned people | 1 |
| claude_deep | 1.0 | medium | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 1.0 | medium | api_median | measured/v1_long_pause | cheaper from 9 people through 500 scanned people | no sustained crossing through 500 people |  |
| claude_deep | 1.0 | heavy | own_cluster | not applicable/not applicable | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 1.0 | heavy | api_cheapest | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |
| claude_deep | 1.0 | heavy | api_median | measured/v1_long_pause | no sustained crossing through 500 people | no sustained crossing through 500 people |  |

| Profile | s | Load | Nodes | Client-served mean TTFT s | All-call mean TTFT proxy s | Accepted client mean TTFT s | Offload mean TTFT s | Restore read/write s per offload | Charged/model queue s | Offload share | Service occupancy |
|---|---:|---|---:|---:|---:|---:|---:|---|---|---:|---:|
| existing_combined | 0.2 | light | 1 | 8.658 | 8.658 | 11.260 | 16.092 | 1.184/1.241 | 2.000/1.568 | 0.308 | 0.224 |
| existing_combined | 0.2 | medium | 1 | 11.824 | 11.824 | 11.260 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| existing_combined | 0.2 | heavy | 1 | 11.824 | 11.824 | 11.260 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| existing_combined | 1.0 | light | 1 | 11.824 | 11.824 | 11.260 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| existing_combined | 1.0 | medium | 1 | 11.824 | 11.824 | 11.260 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| existing_combined | 1.0 | heavy |  | unknown | unknown | 11.260 | unknown | unknown/unknown | unknown/unknown | unknown | unknown |
| claude_deep | 0.2 | light | 1 | 5.955 | 5.955 | 5.955 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| claude_deep | 0.2 | medium | 1 | 5.955 | 5.955 | 5.955 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| claude_deep | 0.2 | heavy | 1 | 5.955 | 5.955 | 5.955 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| claude_deep | 1.0 | light | 1 | 5.955 | 5.955 | 5.955 | 0.000 | 0.000/0.000 | 0.000/0.000 | 0.000 | 0.000 |
| claude_deep | 1.0 | medium | 31 | 5.955 | 7.138 | 5.955 | 0.000 | 0.000/0.000 | 5.000/4.818 | 0.000 | 0.177 |
| claude_deep | 1.0 | heavy |  | unknown | unknown | 5.955 | unknown | unknown/unknown | unknown/unknown | unknown | unknown |

The changed ledger includes all declared bought-office fixed/minimum fleets. The inherited rented control is separate. A fixed fleet that exhausts storage before500 people has only finite feasible/winning intervals; its sustained crossing is correctly absent. No result proves the full raw-log workload has the same crossing. Material changes under delta/output reweighting are shown above; a surviving crossing can coexist with zero prefill offload and therefore cannot be quoted as an offload performance benefit.

## Paired retention fairness control

The main ratios use the accepted own-cluster comparator, which retains its original storage/rebuild policy. To expose that asymmetry, this additional control optimizes BOTH hybrid and own cluster with the SAME expanded3.6TB NVMe,7GB/s read/write,$400 extra-capex proxy and ≤5s mean queue/≤70% occupancy. Own cluster keeps the accepted server-only price boundary; hybrid includes$2.52 Mac energy+$5 front. These are sufficient certified model fleets, not runtime latency measurements or proven global optima. Only this primary1× storage proxy is paired; other proxies remain sensitivities against the accepted comparator.

| Profile | s | Load | Hybrid nodes at50 | Own nodes at50 | Hybrid $ / occupancy at50 | Own $ / occupancy at50 | Sustained win vs paired own through500 |
|---|---:|---|---:|---:|---:|---:|---|
| existing_combined | 0.2 | light | 1 | 3 | 19.948 / 22.44% | 37.283 / 21.17% | cheaper from 25 people through 500 scanned people |
| existing_combined | 0.2 | medium | 1 | 9 | 19.948 / 0.00% | 111.850 / 28.24% | cheaper from 7 people through 500 scanned people |
| existing_combined | 0.2 | heavy | 1 | 27 | 19.948 / 0.00% | 335.551 / 30.10% | cheaper from 2 people through 500 scanned people |
| existing_combined | 1.0 | light | 1 | 11 | 19.948 / 0.00% | 136.706 / 28.89% | cheaper from 5 people through 500 scanned people |
| existing_combined | 1.0 | medium | 1 | 48 | 19.948 / 0.00% | 596.535 / 29.44% | cheaper from 2 people through 500 scanned people |
| existing_combined | 1.0 | heavy |  |  | finite_concurrency_shortfall | finite_concurrency_shortfall | no sustained crossing through 500 people |
| claude_deep | 0.2 | light | 1 | 7 | 19.948 / 0.00% | 86.995 / 17.87% | cheaper from 8 people through 500 scanned people |
| claude_deep | 0.2 | medium | 1 | 28 | 19.948 / 0.00% | 347.979 / 18.44% | cheaper from 2 people through 500 scanned people |
| claude_deep | 0.2 | heavy | 1 |  | 19.948 / 0.00% | finite_concurrency_shortfall | no sustained crossing through 500 people |
| claude_deep | 1.0 | light | 1 | 40 | 19.948 / 0.00% | 497.113 / 17.39% | cheaper from 2 people through 500 scanned people |
| claude_deep | 1.0 | medium | 31 |  | 392.782 / 17.73% | finite_concurrency_shortfall | no sustained crossing through 500 people |
| claude_deep | 1.0 | heavy |  |  | finite_concurrency_shortfall | finite_concurrency_shortfall | no sustained crossing through 500 people |

## Validation and delivery limits

580 native engine cases (562 accepted +18 run25), disjoint IDs/no skips, both shards exit0; kit24 exit0. Parent SHA256 manifest and byte audit exit0. All accepted parent files remain identical. Three narrowing mutants fail their named assertions (actual1); no survivors. Root manifest stays frozen; the new output manifest binds new files. New CSVs total17792462 bytes, below50MB. CPU-only; no inference, download, native build or push.

| Mutant | Gate narrowed to | Named test that fails |
|---|---|---|
| mutant-queue-05 | eliminates collisions/instability from the mean-delay gate | `test_unstable_queue_cannot_report_zero_delay_with_analytic_control` |
| mutant-storage-05 | admits checkpoints beyond declared storage | `test_too_small_storage_refuses_with_expanded_positive_control` |
| mutant-local-01 | always keeps prefill local, hiding profitable admissible offload | `test_queue_refusal_uses_local_capacity_without_dropping_overflow` |

On bought-office PRO6000 vLLM, office125MB/s RTT1ms, owned M5Max64 PRI31 and bf16 transport, the primary expanded3.6TB NVMe/7GBs/$400-upgrade proxy gives unchanged combined-profile own-cluster crossings after delta/output reweighting. For Claude-deep selected shapes (554/1000,55.4%, normalized per person-month; full log mix unsupported), s20 light/medium crossings move13/4 to10/3 people, while s100 medium loses its sustained crossing through500 because the reweighted comparison is capacity-refused. These are materially conditional model changes, not observed raw-log reweighting results. API cache pricing does not enter this same-model own-cluster comparison.

Actual failed attempts remain in the validation JSON: resource stop(-15), scope-superseded draft(-15), temporary shard-runner syntax error(1). The broader unpublished rental draft omitted egress; final sensitivity is bought-office only and has a named rejection for rental reuse. Accepted rental controls retain their full original billing. A later report/metadata refresh preserved every original calculation cell; per-table counts/hashes are in the manifest. Exact raw-log joint shares remain an external input gap, not a passing measurement claim. Independent run25 review is pending.
