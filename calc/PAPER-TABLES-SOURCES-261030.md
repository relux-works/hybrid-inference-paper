# Paper table input custody — run 5, 2026-10-30

> Run11 accounting correction: current nonlegacy base scenarios use output alone (mean511.9); reasoning is informational. Provider evidence and Muse's unverified treatment are recorded in workload provenance and [the Run11 report](ENGINE-REPORT-261030.md#run-11-output-includes-reasoning). Earlier summed numerical examples below are historical and recoverable with explicit fraction1; the separately historical crossover bridge and legacy transcripts remain unchanged.

This run uses offline files only. No source URL was fetched, no price refreshed,
and no package installed. All physical/economic quantities are validated inputs
with units and fact/measured/estimate provenance. New quantities live in
`hybridcalc/data/paper-tables.json`; the scenario combines the existing hardware,
model, price, workload, economics, ownership and operations files.

| Evidence | Identity / treatment |
|---|---|
| Reviewed run 4 | Signed `2c4ca6fdb183ec2632d0893bf0f4c952f45676d5` |
| Full04 call mix | `stats.json`, SHA-256 `8c5f1f2c44e344b78d32d0b4c216d0ebdf2ecdae3cde0f1a983cb329e488e2a7`; seeded marginal sampler, 39,904 calls grouped by 116 |
| M3 Max benchmark | Package `ivmbp-qwen27b-bench-20261030`, archive SHA-256 `5c393bdf40052eb582b5c17aac6176a9273a866c4fadde999ee19afa30924439` |
| Measured prefill segments/slot geometry | `depth.jsonl`, SHA-256 `a75b1aefd40df99d96d8a96ff4eac20073b239c39d4d4d4332fa23da1b9acb5b`; curve midpoints and affine slot slope/intercept are fitted by the engine |
| Measured parallel anchor | `normalized-results.json`, SHA-256 `d7c7cbc72d5ee69991aafdc3b3579dd13d5cd956cb9d4a99d05a25dac7743fb5`; native single 8.440946539830035 tok/s, four-stream interval aggregate 14.054306337676012, gain 1.665015442445748, depth 32k |
| Affine 27B memory | Fitted 34,844 B/token and 156,894,784 B state/intercept; serialized KV remains 34,816 B/token, excluding per-cell metadata |
| Other hardware/price envelopes | Existing offline calc4/NOTES and `SERVICE-SOURCES-261030.md`, `ENGINE-REPORT-261030.md`, `CROSSOVER-SOURCES-261030.md`; not new measurements |

The measured interval aggregate is not request-wall throughput: wall scheduling
and tiny prefill overhead gave 13.1597 tok/s in the package. The requested paper
comparison uses the explicit normalized decode-interval convention. OS/app reserve
is 12 decimal GB. RAM labels retain the repository's conservative decimal-GB
normalization, rather than claim an exact available GiB allocation.

## New estimates, and no invented measurements

| Quantity | Value and reason |
|---|---|
| M3 Max compute reference | 14 TFLOP/s, inherited NOTES envelope; anchors compute ratios, not a replacement for measured prefill |
| M5 Max compute | 60 TFLOP/s, supplied NOTES effective envelope; equal FLOP-efficiency portability is estimated |
| Ultra 96 / 256 compute | 112 / 140 TFLOP/s, supplied NOTES envelope for 64/80 GPU cores |
| M4 Max configuration | 128 GB, 546 GB/s, 28 TFLOP/s; unmeasured comparison estimate, with compute explicitly set to twice M3 |
| M4 Max purchased valuation | $5,999 estimate, not a quote |
| M3 Max purchased valuation | $6,000 replacement estimate below the supplied M5 Max 128 $6,699 reference; not an original receipt |
| Strix / Spark compute | 37 / 99.8 TFLOP/s from supplied offline NOTES envelopes; no exact-model package measurement |
| Purchase basis | Existing Mac: zero acquisition charge. Bought laptop premium: max(0,purchase−$2,499 baseline); bought Studio: full additional device, zero laptop credit. Residual/years and electricity remain declared inputs |
| Local prefill portability | Effective compute at depth = measured M3 curve × Qwen FLOPs/token × device_compute/reference_compute; then target-model FLOPs and memory roofline. GLM adds the explicit calc4 MoE factor 0.5 |
| Dense parallel extrapolation | `min(single*k^gamma, calibrated_bandwidth*k/(weights+k*state_traffic))`, gamma=`log(measured_gain)/log(4)`; exact at one/four streams at 32k, monotone in available streams and roofline-capped elsewhere. No fifth-stream extrapolation |
| GLM activity | Two growing sessions/person/active day; adjustable, not inferred from real chronology |
| GLM growing sessions | Start at depth zero, replay measured sampled delta/output/tool increments to 200k/400k/600k/800k/1M, clipping the last call. Midpoint integration step 1k tokens for cold ingest; refinement tested |

M4 values and all cross-device/GLM kernel assumptions need actual measurements
before a runtime claim. Quantization changes resident weights and decode traffic;
Q3 does not silently receive an assumed compute speedup. Q4/Q6/Q8 server weights
use the stated INT8/FP8 tensor class, NVFP4 needs engine-supported Blackwell FP4,
and BF16 overrides are labelled academic. Server replicas reserve weights and
workspace separately on each GPU. GLM expert-union traffic is estimated from
calc4's declared routing geometry, not calibrated using the Qwen batching gain.

## Workload and cost boundaries

The paper scenario explicitly keeps calc8's conservative output+reasoning sum
for comparability with r4. Counter disjointness is unresolved. Use
`--set workload.reasoning_extra_fraction=0` for an output-only sensitivity;
this does not silently change the independent historical crossover reference.
The sampler represents measured marginal statistics, not recovered sessions or
arrival/peak/SLA evidence. One short-table row cannot resolve this usage contract.

For each requested call, eligibility is checked against its final KV/state memory.
Capacity limits accepted calls; remaining calls go to API. API vectors are built
before routing and retain original 116-call cache boundaries. Memory-ineligible
calls keep their own (often higher) API costs rather than the supported-call mean.
Both median and cheapest spill bills are exposed, with matching full-demand API
comparisons. Selection within supported calls is a proportional workload estimate,
not a queueing simulation. Actual streams shrink where output growth consumes RAM.

At the reviewed r4 head, `owners-economics` already included cheapest spill in
`hybrid_user`. Run 5 exposes that existing charge, adds median spill/total, and
keeps the original number as the cheapest alias. It does not falsely claim that
an omitted charge caused the observed 348.4-call cap. The new paper scenario also
changes the client calibration and uses shared rented B300 prefill, so its totals
are intentionally different from the old L40S/ideal-weight-sharing model.

Remote rent/buy is a dedicated prefill-service comparison before individual Mac
caps. Offered demand is 50% of the heavy profile, 21 active days, 10h or 24h warm
billing; capacity target 70% is separate from 30% MFU and energy duty. Server KV
nonfit calls are median-API priced in both ownership/rental totals. Small hosts
retain r4's capex, nonzero colocation minimum, energy/support and residual grid.
Office options are visibly excluded for small remote teams. `buy_beats_rent=1`
means cheaper four-year residual-adjusted monthly cost, not cash payback.

GLM charts buy the full Studio and integer owned B300 nodes, including depreciation,
energy, colo, support, front, egress and API spill. All costs divide by requested
sessions, not only served ones. The minimum node creates a real small-team penalty.
Cold ingest is separate from steady growing-session economics: local integration,
one B300 replica's prefill, and a single full KV/state download. No semantic
state-interchange correctness or million-token runtime performance is proven.

Traffic reports both offered demand and actual Mac-capped hybrid downloads, so
an overloaded heavy user does not receive free device capacity. API overflow
creates no hybrid-download charge. Decimal TB and all four egress tariffs are
explicit. Offload table D separately uses its historical line-rate goodput=1;
client economics uses the declared WAN goodput=0.9. State 16 conversion remains
an estimate; measured resident state remains f32.

## Historical reference and export custody

The short crossover table recomputes the r4 bridge using its own unchanged
scenario inputs, and prefixes its dependencies/sources with `r4_reference.`.
These are independent reference inputs, not current-client inputs. To explore
other reference assumptions, run `crossover-bridge --set ...` separately. The
current paper scenario must not rewrite historical thresholds when a client,
traffic parameter or sampler prefix is overridden.

`calc/out/paper/manifest.json` records every generated file hash, complete
code/data generation hashes and the result digest. `sources.json` records the
used quantities and measured-file hashes; `schema.json` records units and row
counts. `alarms.json` identifies every noncomputable cell. Alarm cells are `nan`,
with status/alarm_inputs columns, never blank or zero. Verify hashes before
consuming a generation; the manifest is replaced last. Foreign files are neither
deleted nor included as generated artifacts. CSV display labels replace commas/quotes/newlines with safe display punctuation;
`schema.json.csv_labels` retains the exact originals and rejects display-label
collisions. This keeps rows rectangular even for simple pgfplots readers.
CSV numbers retain Python's full float representation; ordinary human-readable formatters retain their compact
presentation. Export is deterministic for unchanged code, data and runtime.

The optional committed `tests/paper_tables_smoke.tex` reads every default CSV
with native pgfplots, checks expected row counts and plots the documented GLM
team filter. Tectonic 0.17.0 passed with `--only-cached`, using existing cached
resources and writing only task-local PDF/log artifacts. It is not a paper
PDF build or a Python-package dependency.
