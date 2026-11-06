# Engine run26 — closed contour: hybrid against internal inference

Parent: run25 `ec28e37c58f49e7109178d1c23334c4c7e0aad38`, Muse r5x9 ACCEPT; review arrived during this run. Run24 `ca7f228a` was accepted. This separate run adds files only; every parent-tracked byte, including run24/run25, is frozen. No inference, native builds, model downloads or pushes. Public source/price pages only.

## Section8: Closed contour («Закрытый контур»)

The organization first chooses the model class. Cloud-class2.4T FP8 belongs on an internal multi-node cluster and cannot be offered to the hybrid512GB client. The dense27B middle class can use measured M5 Max64 clients (128GB is same-SoC portability); the320B MoE can be investigated on an EXTRAPOLATED Ultra256/512. The own cluster does both phases; the primary hybrid server does prefill only. All generation exceeding client capacity REFUSES, rather than quietly migrating to the server. Buying a client is charged in full amortization; owned capital is sunk. Own-cluster rows price server hardware only; ordinary terminal/common organizational costs are outside both alternatives.

At s=1 every model call is internal. At s=.2/.5, the remaining80%/50% is on an INTERNAL large model, whose common cost C is identical in both alternatives. Htotal=Hmiddle+C; Ototal=Omiddle+C; the difference and strict crossings cancel C exactly. The numerical common C shown is a capacity-cost FLOOR, not a service price. Additional large-model service, communication, storage and quality costs are pending, identical symbolic additions in both alternatives. Historical s=.2 with80% to a cloud API was not a closed contour. A task share is an input scenario, not evidence that the middle model solves that share at equal quality. Call price is not price of completed work.

## Sources and explicit projections

[Qwen model card](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) specifies2.4T total/95B active,92 layers and512 routed experts/top10+shared. [GLM model card](https://huggingface.co/zai-org/GLM-5.3-Flash) specifies320B/18B; its [config](https://huggingface.co/zai-org/GLM-5.3-Flash/blob/main/config.json) supplies288 routed/top8, one shared,45 layers (34 linear/11 sparse),512-dimensional MLA latent,2048 sparse index cap,1048576 context. Captures/source hashes are in `calc/run26/data/source-index.json`. No model weights were fetched.

[Apple specifications](https://www.apple.com/mac-studio/specs/) confirm an M5 Ultra with256/512GB and1.2TB/s. [Macworld’s Apple-list-price report](https://www.macworld.com/article/3271691/the-mac-studio-with-512gb-of-ram-is-shipping-and-it-costs-new-car-money.html) gives US$10,799/22,299 for256/512GB,36CPU/80GPU,1TB. These are sourced purchase-cost proxies before tax, not quotes. The official store capture lists the chip/configuration; its static price bootstrap does not expose the configured memory surcharge. MacRumors HTTP403 is recorded, not claimed as a successful second fetch. The obsolete$8,000 Studio estimate is not used.

Every Ultra timing is UNMEASURED: measure-derived effective M5 Max bandwidth at the same depth = Qwen single-stream tok/s ×(18,973,870,432B weights +34,816B/token×depth +156,893,184B recurrent state), then multiply by2. Divide by the GLM active/expert-union+per-session state traffic. Prefill = measured Max Qwen elapsed time × GLM/Qwen FLOP proxy /2. This is the owner-authorized two-die scaling assumption, not an Ultra benchmark or a claim of perfect observed scaling. GLM B300 prefill = measured Qwen single-B300 elapsed time × FLOP ratio /2; x2 slower sensitivity applies to both GLM alternatives. No GLM kernel, collective, Studio decode/prefill, bridge or B300 prefill measurement exists; rental failed to start. Legacy Studio57min/1M is not a timing anchor.

GLM FLOP proxy =2×18B +4×11×64×256×min(depth,2048) +4×34×64×128²; Qwen54B+393216×depth. FLOP portability omits routing/indexer/collective overhead. The expert weight partition solves total=A+R and active=A+R×8/288; it is not the older inconsistent shared/routed constants. Q4 residency181.4GB and FP8 allocation328GB are inherited sizing estimates. Client q8_0 MLA =11×512×34/32=5984B/token; server bf16 MLA11264B/token. Estimated fp32 linear+conv state152,633,344B, hypothetical bf16 transport76,316,672B. These layouts, sparse-KV read behavior, conversion and GLM bf16 quality are unmeasured; Qwen’s accepted bf16 quality does not qualify GLM. Whole MLA KV is charged per generated token conservatively, so sparse gather optimization is an open bound.

GLM twoB300/replica, four replicas/eightGPU paid node, ideal summed2×8TB/s×70% bandwidth, no collective overhead. Native fleet model caps decode at32 streams/replica and finite4×team concurrency, includes tool pauses, retained-copy residency and nonresident cold-rebuild proxy; no new restore measurement is claimed. Qwen PRO decode uses run23 measured surface, B300 decode remains modelled. Measured PR16 Qwen bridge envelope and run16 Mac import are reused for GLM only as UNMEASURED portability. Bought link125MB/s/1ms office; rental112.5MB/s/400ms engine WAN estimate,730h/month, inherited egress/storage. A rented node represents an internal contour only under an approved trust-boundary assumption.

Coverage: combined10885/39904=27.28%, Claude554/1000=55.40%, shares of fitted/reconstructed CALL SHAPES inside Qwen’s measured ladder, normalized to full declared intensities per person-month, not a quarter of tokens/work. Profiles are aggregate reconstructions, not raw chronological traces. For GLM the same shapes ensure comparison consistency, not measured GLM coverage. Light/medium typical200/800 calls/day, heavy2500/day is the owner’s intensity,21days/month,8h/day. No second Mac.

## s=100% bought dedicated: crossings through500 and team50

Costs below USD/person-month; × means no finite prefill-only certificate. Each cost includes its dedicated service occupancy in parentheses. Inherited fleets are sufficient, not globally minimal. Conditional projections are not measured results.

| Profile | Model/client | Client capital | Load | Sustained from | Team50 hybrid (occupancy) | Team50 own (occupancy) |
|---|---|---|---|---:|---:|---:|
| existing_combined | qwen m5max64 | owned | light | 4 | 56.64 (18.1%) | 159.65 (68.4%) |
| existing_combined | qwen m5max64 | new | light | 4 | 125.69 (18.1%) | 159.65 (68.4%) |
| existing_combined | qwen m5max | owned | light | 4 | 56.64 (18.1%) | 159.65 (68.4%) |
| existing_combined | qwen m5max | new | light | 20 | 147.36 (18.1%) | 159.65 (68.4%) |
| existing_combined | qwen m5max64 | owned | medium | 2 | 68.93 (58.6%) | 442.12 (68.4%) |
| existing_combined | qwen m5max64 | new | medium | 2 | 137.97 (58.6%) | 442.12 (68.4%) |
| existing_combined | qwen m5max | owned | medium | 2 | 68.93 (58.6%) | 442.12 (68.4%) |
| existing_combined | qwen m5max | new | medium | 2 | 159.64 (58.6%) | 442.12 (68.4%) |
| existing_combined | qwen m5max64 | owned | heavy | none | × | 761.43 (67.3%) |
| existing_combined | qwen m5max64 | new | heavy | none | × | 761.43 (67.3%) |
| existing_combined | qwen m5max | owned | heavy | none | × | 761.43 (67.3%) |
| existing_combined | qwen m5max | new | heavy | none | × | 761.43 (67.3%) |
| existing_combined | glm ultra256 | owned | light | none | 348.32 (0.0%) | 337.02 (4.1%) |
| existing_combined | glm ultra256 | new | light | none | 494.55 (0.0%) | 337.02 (4.1%) |
| existing_combined | glm ultra512 | owned | light | none | 348.32 (0.0%) | 337.02 (4.1%) |
| existing_combined | glm ultra512 | new | light | none | 650.28 (0.0%) | 337.02 (4.1%) |
| existing_combined | glm ultra256 | owned | medium | 346 | 348.32 (0.0%) | 337.02 (16.5%) |
| existing_combined | glm ultra256 | new | medium | none | 494.55 (0.0%) | 337.02 (16.5%) |
| existing_combined | glm ultra512 | owned | medium | 346 | 348.32 (0.0%) | 337.02 (16.5%) |
| existing_combined | glm ultra512 | new | medium | none | 650.28 (0.0%) | 337.02 (16.5%) |
| existing_combined | glm ultra256 | owned | heavy | 68 | 348.32 (0.0%) | 337.02 (51.6%) |
| existing_combined | glm ultra256 | new | heavy | none | 494.55 (0.0%) | 337.02 (51.6%) |
| existing_combined | glm ultra512 | owned | heavy | 68 | 348.32 (0.0%) | 337.02 (51.6%) |
| existing_combined | glm ultra512 | new | heavy | none | 650.28 (0.0%) | 337.02 (51.6%) |
| claude_deep | qwen m5max64 | owned | light | 3 | 56.64 (0.0%) | 221.06 (69.4%) |
| claude_deep | qwen m5max64 | new | light | 3 | 125.69 (0.0%) | 221.06 (69.4%) |
| claude_deep | qwen m5max | owned | light | 3 | 56.64 (0.0%) | 221.06 (69.4%) |
| claude_deep | qwen m5max | new | light | 3 | 147.36 (0.0%) | 221.06 (69.4%) |
| claude_deep | qwen m5max64 | owned | medium | none | × | 638.62 (69.2%) |
| claude_deep | qwen m5max64 | new | medium | none | × | 638.62 (69.2%) |
| claude_deep | qwen m5max | owned | medium | none | × | 638.62 (69.2%) |
| claude_deep | qwen m5max | new | medium | none | × | 638.62 (69.2%) |
| claude_deep | qwen m5max64 | owned | heavy | none | × | × |
| claude_deep | qwen m5max64 | new | heavy | none | × | × |
| claude_deep | qwen m5max | owned | heavy | none | × | × |
| claude_deep | qwen m5max | new | heavy | none | × | × |
| claude_deep | glm ultra256 | owned | light | none | 348.32 (0.0%) | 337.02 (15.5%) |
| claude_deep | glm ultra256 | new | light | none | 494.55 (0.0%) | 337.02 (15.5%) |
| claude_deep | glm ultra512 | owned | light | none | 348.32 (0.0%) | 337.02 (15.5%) |
| claude_deep | glm ultra512 | new | light | none | 650.28 (0.0%) | 337.02 (15.5%) |
| claude_deep | glm ultra256 | owned | medium | 57 | 348.32 (0.0%) | 337.02 (62.1%) |
| claude_deep | glm ultra256 | new | medium | 339 | 494.55 (0.0%) | 337.02 (62.1%) |
| claude_deep | glm ultra512 | owned | medium | 57 | 348.32 (0.0%) | 337.02 (62.1%) |
| claude_deep | glm ultra512 | new | medium | none | 650.28 (0.0%) | 337.02 (62.1%) |
| claude_deep | glm ultra256 | owned | heavy | none | × | × |
| claude_deep | glm ultra256 | new | heavy | none | × | × |
| claude_deep | glm ultra512 | owned | heavy | none | × | × |
| claude_deep | glm ultra512 | new | heavy | none | × | × |

`crossings.csv` also gives first wins, exact finite/winning team intervals, both bought/rented, Qwen PRO and B300, both profiles, s=.2/.5/1, both client memories/capital bases and GLM prefill x1/x2. A first integer-fleet step win is not a sustained crossing. `mixed_scheme.csv` gives identical common-large columns, middle difference and conditional capacity-floor totals for teams1/3/5/10/20/50/100/500.

## Run25 fleet sensitivity

The PRO queue/storage contract applies to Qwen, not automatically to a two-GPU GLM replica. `fleet_variants.csv` recomputes team50 with64/128GB vectors, owned/new clients, s=.2/.5/1, light/medium/heavy, fixed1/2/4 and first-certified minimum through4T; original900GB NVMe, expanded3.6TB NVMe,3.6TB warmRAM and x2 slower proxies. Every server restore remains UNMEASURED:7GB/s NVMe read/write,50GB/s warm RAM/PCIe; capacities/prices and independent Poisson/M/G/1 mean queue are exactly run25 declarations, including extra$400/$10k capex. Mean queue≤5s and occupancy≤70%, no p95 or peak guarantee. Checkpoint read/write, pending replay, wire/import and local-prefill fallback change TTFT and routing; each is exported. Primary rows additionally refuse server generation overflow. Thus old run25 heavy generation-fallback results cannot be quoted as a prefill-only win. Minimum is within the declared grid, not a runtime optimum. Own reference here retains the inherited own policy, explicitly not paired optimized storage.

## Cloud-class reference: capacity cost, service pending

One8×B300 node has2.304TB raw HBM. At90% allocation and8GB workspace/GPU,2.4TB FP8 weights need at least two nodes. The weight-only cost floor omits session storage and task throughput. A separate all-resident-copy scenario holds4copies/person at262144 depth in HBM:23 full layers×2K/V×4heads×256×2B=94208B/token plus estimated69 linear-layer state. Its larger fleet is a declared residency alternative, not a minimum that precludes off-GPU storage. Multi-node interconnect, quantization extras and effective throughput remain pending. No cloud-class hybrid is feasible.

| Billing | Retention | Team50 capacity cost/person-month | First within declared $1000 budget |
|---|---|---:|---:|
| bought | weights_only_floor | 674.03 | 34 |
| bought | all_resident_sessions | 1348.06 | 135 |
| rented | weights_only_floor | 2219.20 | 111 |
| rented | all_resident_sessions | 4438.40 | none through500 |

The$1000/person-month threshold is a declared affordability criterion for the hardware capacity floor only. It certifies neither serving the requested load nor price/quality parity with the middle model. It is not an API comparison.

## MoE hypothesis: compute the bound, do not presume a cost victory

For E=288, top8, batch B, expected expert union is E[1−(1−8/E)^B]. Single-client decode reads its active experts; batch traffic reads the union plus every session’s own KV/state. `moe_decode.csv` compares the resulting gain with dense Qwen at16k/64k/164k/256k/512k/1M, including large-batch resident limits. Less KV raises the GLM batch cap; weak expert overlap delays weight sharing. Uniform independent routing, full-KV reads, ideal sharding and no communication make this a model, not measured server scaling. Economic verdict must be conditional on both client purchase and GLM portability; smaller KV alone is insufficient.

## Gates and remaining inputs

New rules have named negatives with positive controls. Source hashes, all parent files, report and compact outputs are audited. No supplied attack-surface table (brief gap). Runtime GLM/Ultra, cloud-class service, raw-log correlations, parity of completed tasks and trust-boundary certification remain outside the measured contract. See `pending_inputs.csv` and `calc/run26/UNRESOLVED_QUESTIONS.md`. Validation receipts are published separately; no unrun gate is asserted here.

## Numerical MoE result and ownership limits

At the same requested32 streams, the modelled server gains are:

| Depth | GLM two-B300 gain | Dense Qwen one-B300 gain | Expert-read amortization |
|---:|---:|---:|---:|
| 16000 | 2.870 | 13.764 | 1.496 |
| 64000 | 2.728 | 6.035 | 1.496 |
| 164000 | 2.491 | 3.138 | 1.496 |
| 256000 | 2.324 | 2.329 | 1.496 |
| 512000 | 2.009 | 1.616 | 1.496 |
| 1000000 | 1.593 | 1.241 | 1.290 |

The expert-read amortization is B×topk/expected_union; it can remain small when dense weights share once across the entire batch. Smaller MLA KV raises the resident batch limit but does not give dense-style weight sharing. This mechanism supports testing the MoE hypothesis, not presuming its economic answer.

For a hardware-matched paid eight-B300 node comparison, team50 s=1 bought, combined measured-shape profile:

| Model/client | Client basis | Light own/hybrid | Medium own/hybrid | Heavy own/hybrid |
|---|---|---:|---:|---:|
| m5max64 | owned | 0.989 | 0.989 | capacity shortfall |
| m5max64 | new | 0.898 | 0.898 | capacity shortfall |
| m5max | owned | 0.989 | 0.989 | capacity shortfall |
| m5max | new | 0.873 | 0.873 | capacity shortfall |
| ultra256 | owned | 0.968 | 0.968 | 0.968 |
| ultra256 | new | 0.681 | 0.681 | 0.681 |
| ultra512 | owned | 0.968 | 0.968 | 0.968 |
| ultra512 | new | 0.518 | 0.518 | 0.518 |

Conditional engine verdict: on the bought B300-node control, owned GLM/Ultra clients have a sustained medium/heavy crossing where Qwen/Max does not; light and newly purchased Studio clients do not establish a sustained advantage through500 in the combined profile. This is conditional cost support for decode on the client, not an empirical GLM result. The GLM team50 policy selects zero prefill offloads: it is projected local compute plus paid retention, and does not demonstrate a prefill-offload speed benefit. `moe_verdict.csv` gives both profiles and both Studio memories. Qwen on PRO is a different and cheaper hardware option, so this is not a general economic superiority claim.

Values above1 favor the hybrid. GLM rows remain UNMEASURED Ultra/GLM projections (prefill x1; x2 is in root outputs), and client purchase can reverse a win. The table reports the hypothesis conditionally by load and ownership; it establishes no universal MoE advantage or completed-task parity. Qwen PRO remains the dedicated paper headline; this same-B300 control isolates part of the hardware-price confound.

## Mixed scheme and fleet boundaries

All s=.2/.5 crossings in `crossings.csv` are legitimate closed-contour segment comparisons ONLY when the remainder runs internally at the identical common cost. `mixed_scheme.csv` has both copies of C and symbolic-pending cost labels. The numerical two-node weight floor is not a measured large-model service bill. The middle-model delta, not the capacity-floor total, is the reliable algebraic comparison.

Fleet-size variants in this run are team50 sensitivities, not fresh integer-team crossings under every storage policy. Run25’s legacy crossing tables remain frozen with their explicit server-generation fallback; they cannot substitute for the new prefill-only crossings. Full1..500 primary crossings are recomputed for the inherited dedicated policy. No GLM fleet-queue extension is claimed from the PRO-only run25 contract.

Compact `quotes.csv` binds each printed crossing/team50 cost, cloud affordability coordinate and32-stream MoE gain to an exact CSV cell; it is not a full quote dump.

## Zero-offload boundary at team50

A paid retained-copy fleet with zero offload is a local-compute/retention scenario, not evidence of faster hybrid prefill. The costs remain charged. The routing shares below prevent interpreting a zero-offload win as an offload-speed benefit.

| Profile | Model/client, owned | Load | Prefill offload share | Client capacity/day |
|---|---|---|---:|---:|
| existing_combined | qwen/m5max64 | light | 10.71% | 916.3 |
| existing_combined | qwen/m5max | light | 10.71% | 921.5 |
| existing_combined | qwen/m5max64 | medium | 10.76% | 917.5 |
| existing_combined | qwen/m5max | medium | 10.76% | 922.7 |
| existing_combined | qwen/m5max64 | heavy | client_decode_capacity_shortfall | 1066.4 |
| existing_combined | qwen/m5max | heavy | client_decode_capacity_shortfall | 1073.5 |
| existing_combined | glm/ultra256 | light | 0.00% | 4251.6 |
| existing_combined | glm/ultra512 | light | 0.00% | 4251.6 |
| existing_combined | glm/ultra256 | medium | 0.00% | 4251.6 |
| existing_combined | glm/ultra512 | medium | 0.00% | 4251.6 |
| existing_combined | glm/ultra256 | heavy | 0.00% | 4251.6 |
| existing_combined | glm/ultra512 | heavy | 0.00% | 4251.6 |
| claude_deep | qwen/m5max64 | light | 0.00% | 675.4 |
| claude_deep | qwen/m5max | light | 0.00% | 688.1 |
| claude_deep | qwen/m5max64 | medium | client_decode_capacity_shortfall | 675.4 |
| claude_deep | qwen/m5max | medium | client_decode_capacity_shortfall | 688.1 |
| claude_deep | qwen/m5max64 | heavy | capacity_shortfall | undefined |
| claude_deep | qwen/m5max | heavy | capacity_shortfall | undefined |
| claude_deep | glm/ultra256 | light | 0.00% | 1702.5 |
| claude_deep | glm/ultra512 | light | 0.00% | 1702.5 |
| claude_deep | glm/ultra256 | medium | 0.00% | 1702.5 |
| claude_deep | glm/ultra512 | medium | 0.00% | 1702.5 |
| claude_deep | glm/ultra256 | heavy | client_decode_capacity_shortfall | 1702.5 |
| claude_deep | glm/ultra512 | heavy | client_decode_capacity_shortfall | 1702.5 |

## Delivery validation

Engine:606 cases (580 original/reviewer cases +26 new),0 failures/errors/skips; kit24 cases, exit0. Completed receipts are `engine-historical-03`, `engine-current-06`, `kit-01`. Publication04, source/manifest audit and576 crossing-interval checks exit0. All1,987 parent-tracked files including1,072 historical outputs are byte-identical. All CSVs total13632019B (<50MB);386 quoted coordinates are exact. Full receipts/source identities and honest interrupted attempts are in `calc/R26-VALIDATION-261105.json`. No attack-surface table supplied (brief gap); runtime/quality/complete-task claims outside the brief’s measured contract remain pending.

| Mutant | Gate narrowed to | Named failing test | Outcome |
|---|---|---|---|
| client_fit_removed | client admission narrowed to unconditional success | test_run26.Run26Contracts.test_cloud_class_hybrid_refuses_not_fitting_client_positive_middle | one intended assertion failure, zero errors |
| generation_hidden | prefill-only gate narrowed to paying for any generation overflow | test_run26.Run26Contracts.test_prefill_only_refuses_decode_overflow_positive_zero_overflow | one intended assertion failure, zero errors |
| large_model_free | mixed common part narrowed to a free unpriced remainder | test_run26.Run26Contracts.test_mixed_common_cost_cancels_positive_equal_common_negative_invalid | one intended assertion failure, zero errors |

All three mutants killed; no survivor. Harness exit0 verifies the expected-red assertion failures, not a passing mutated test. Pristine controls pass in the26-case suite.

Interrupted export01/historical02 were actual-15 resource stops, not passing gates; historical01 failed before discovery. Current01 exposed one missing owned-capital zero on refused rows; `publication-metadata-fixes.csv` records the cells, with no other cell changes in that normalization. Final source/current tests passed after correction. The shared disk briefly fell below28GiB during the interrupted attempt; the guards stopped work, and sequential gates passed after recovery. No published write below the floor is claimed.

Additional declared inputs: Ultra250W and90% usable memory/4GB reserve are unmeasured sizing/energy assumptions. Client capital uses accepted residual/years inputs, full8h/day energy is charged at every load. s scales the same conditional profile; no difficulty-conditioned task distribution was measured. GLM ports the Qwen bridge-containing elapsed envelope through the same FLOP/two-GPU scaling; no separate GLM conversion measurement or bound exists. The constant-at-end GLM cold-rebuild FLOP ratio is a portability scenario, not a measured curve or a conservative bound. These limits can change the projected applicability.

Parent run25 ec28e37c received Muse r5x9 ACCEPT during this run. Its notes are carried: off-GPU sensitivity counts54 reserved copies/node vs inherited54+3 GPU copies; both give4 nodes at team50; TMPDIR stays inside the checkout; zero-offload savings remain distinct from real prefill gains.
