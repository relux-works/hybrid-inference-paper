# Calculation assumptions requiring later evidence

The offline calculation delivery does not block on these measurements. They
bound the claims made by the canonical and owners' economics scenarios.

| Question | Current declared assumption | Needed evidence |
|---|---|---|
| What do the M3 Ultra 256 GB configuration and current systems cost? | M3 Ultra $8,000 and 819.2 GB/s; other prices retain the dated repository snapshot | A dated configuration/price source; no live pricing was queried in this run |
| Which Strix Halo boxes expose suitable expansion and support the assumed link? | Two $3,449 systems plus $600 total NIC/cabling allowance; direct 10GbE, 80% goodput, 100 microseconds per message | Exact systems, NIC/driver support and measured payload throughput |
| Can the GLM runtime split the assumed state/weights across two nodes as modeled? | Balanced pipeline shards, no overlap speedup; bf16 boundary activations with equal-size feedback; no tensor collective | A supported split implementation and measurements for state layout, imbalance, synchronization and link latency |
| Does Muse also include reasoning inside output? | Run11 owner evidence verifies nesting for Codex 126/126 events and Claude Code 4577/4577 records (93% of calls); output-only base applies to Muse too, unverified. Explicit fraction 1 remains a labelled upper bound; historical bridge/legacy reproductions retain their dated sum | Muse usage accounting contract or a local log audit; do not add reasoning to verified Codex/Claude output |
| How well do measured curves extrapolate? | Run11 client prefill keeps last-point FLOP efficiency beyond230948; run12 server sensitivity extrapolates affine seconds/token beyond249k, held-out1.04M YaRN fill within15%; decode batching remains calibrated only at32k | More depths, small portions, multiple hardware configurations and sustained concurrent-stream benchmarks |
| Can BF16 27B be placed on L40S without changing the model? | It cannot fit on one 48 GB GPU; service-bf16-academic raises a capacity alarm. No multi-GPU sharding or CPU offload is assumed | An explicitly qualified alternative placement/runtime, if this option is needed |
| Which form factor does the quoted Koyeb H100 tariff provide? | Service calculations use the explicit SXM envelope estimate | Provider-specific hardware confirmation and measured sustained prefill MFU |
| Are the new purchase budgets and quantized kernels available? | H100/L40S/H200 capex is explicitly hypothetical; Q4/Q6/Q8 use INT8/FP8 tensor envelopes, NVFP4 needs Blackwell and engine support; sharded replicas have declared efficiency estimates | Procurement quotes and end-to-end serving/kernel/communication qualification |
| Does the requested 30–37% decode bandwidth fraction use the same denominator? | Measured native 16k decode is 7.48–8.82 tok/s; actual GGUF-byte traffic implies ~40.96%. The owner efficiency setting is an explicitly calibrated coordinate | Agree on physical traffic/dequantization denominator; do not silently call the measured GGUF bound 30–37% |
| Does the measured RTX server envelope transfer to B300, Server Edition RTX or GLM? | Run12 measures only one Vast600W workstation with Qwen Q4_K_M/q8_0 KV. RTX server hosts reuse the curve; B300 inherits its depth-dependent dense-FP8 fraction; GLM divides its own FLOPs by that estimated envelope. FP16 normalization gives the same ratio. Small512-token portions and compatible client/server kernels are not qualified | Same-weights long-depth bulk/small-portion benchmarks on the named hardware/models; native1M quality and compatible state export/import |
| Can a real pool enforce the assumed drain guarantee? | The pool does not exist; bounded tenant jobs plus owner model/state restoration, admission cutoff and disjoint owner windows are analytical assumptions. Continuous autopilot reservations leave no guaranteed idle window | Runtime admission control, job/restore-bound enforcement, schedule/eviction tests and measured handback; no provider availability is claimed |
| What do small colocated hosts actually cost? | One/two Server Edition GPU host budgets $36k/$62k; space fee max($100/host-month, kW*$190), power 0.9/1.8 kW; all dated/explicit estimates | A dated small-host purchase and colocation quote; confirmation of multi-GPU topology |
| Can the new paper client envelopes be treated as measured? | Only M3 timing/slot/parallel anchors are measured. M4 compute and replacement budgets, cross-device equal FLOP-efficiency, deep batching interpolation and GLM kernels are estimates | Device-specific long-context and concurrent-stream benchmarks; purchase quotes |
| Are synthetic growing GLM sessions real chronology? | They replay measured sampled increments from depth zero with a declared two-session/day plan; counter semantics and chronology are not reconstructed | A complete long GLM session trace and caller accounting contract |
| How do 64k/128k decode rates scale at K=1/2/4/8? | Run-6 `decode_scaling` contains raw bandwidth bounds for K=1/2/4/8/16 and memory fit, with no efficiency projection; only two M3 32k rows are measured | The owner's pending Mac parallel-depth run; separate observed throughput from theoretical bounds |
| What extra costs does a closed internal rack require? | Run-6 small hosts reuse R4 purchase/power estimates and an explicit sunk internal rack-space fee; no outside fallback; target-load fleet sizing excludes queues | Organization-specific secure facilities, connectivity, support and serving/scheduling measurements; no security qualification is claimed |
| What is the actual imported-delta/last-token cost on the hybrid path? | R7 assumes one serial copy at 10% nominal client bandwidth, zero fixed overhead and one final-depth decode-equivalent token; full slot restore includes filesystem work and is not a delta-import measurement | Measure compatible delta import, recurrent bf16 conversion/quality and first-token evaluation separately; no runtime compatibility is qualified |
| Can decode improve threefold on unchanged M3 byte traffic? | R7 shows the requested algebraic rate but alarms capacity above the raw bandwidth bound; factors up to 2 are hypothetical, not measurements | A qualified engine benchmark or explicit changed-traffic model; do not silently multiply the measured four-stream gain |
| What is the actual server-session residency policy and budget? | R9 design estimates append-only KV, expected deferred catch-up, four retained copies, active-window RAM/off-window NVMe and 50GB/s PCIe; conservative is append-only per-call/month-long RAM | Measure finite-session pending runs, retention, hot-cache residency, pool costs, day-end flush and background promotion/overlap; no storage tariff or implementation is claimed |
| Does the all-agent aggregate sampler recover real tails and correlation? | R8 fits measured token-mass shares and conditional means, global means and depth quantiles; remaining within-bin distribution and chronology are synthetic | A deidentified joint trace; do not substitute Claude-only means for pooled targets |
| Does the M5 Air transcript fit a developer workload? | The estimated appliance example uses 8GB OS/app reserve; 12GB alarms for 70k+3k at Q4 | A measured Air memory/prefill/decode/import run and a real OS/app budget |
| Do all target Python/platform combinations run identically? | Python 3.9 grammar and standard-library API compatibility; validated execution on Linux Python 3.14.4 | Native Python 3.9/macOS execution; no tools were installed |

Full05 call dates have partial time coverage and a different corpus boundary
from full04. This is a known data limit, not a license to splice their counts.
See `calc/ENGINE-REPORT-261030.md` and the preserved measurement package reports.

Run13 qualification update (2026-11-01): M5 Max64 steps40/50/55 and Vast
checkpoints-off/on runs are now archived and hash-verified. Earlier rows above
that describe all M5 clients or server timing as unmeasured refer to the
historical scenarios. The new base uses these measurements; other M5 variants,
B300/GLM portability, small portions, deep extrapolation and sustained loads
remain estimates. Step57's M5 rates are excluded for swap. vLLM 0.32 FP8 remains
server-only until a compatible client-state bridge exists. Three-stream M5
throughput interpolates measured two/four-stream aggregate rates; >4 streams
are outside the economic model's common depth coverage. A paper numeric update
is pending against ENGINE-QUOTES-R13-261101.csv. The requested paper/style.ru.md
was absent from the checkout and public main c04a99d; it needs owner restoration
before a later prose-editing run can apply it.


## Paper v2 qualification (2026-11-01)

The paper snapshot and prose now use run13. The style source used for this task is
`/home/agent/src/swarma-docs/editorial/style.ru.md`; the prior note about absent project-local style is historical.
The map and command evidence are in `calc/PAPER-V2-GAPS-261101.md`.

The orchestrator authorized the run13 checker migration in hybrid-c-r8-261101. The obsolete direction, constant-rate
and old-publication byte/line gates have been migrated with negative controls, not waived. Historical exports and
producer ledgers retain their original contracts. Current v2 bytes and numeric sites are guarded separately; see the
nine-test migration table and command evidence in the gap map. Review and publication remain with the owner; no
push or tag is authorized in this task.

Current pending measurements (paper v3, superseding the original FACTS section 5 schedule):

| Pending item | Evidence needed | Public location |
| --- | --- | --- |
| Growing session, CUDA-to-Metal on the owner's M3 Max | Actual call/transfer/import/fidelity/recovery observations; one-GPU rehearsal is functional only | Prototype appendix, visible pending block |
| CUDA-to-Metal calibration against BF16 | Honest-noise and attack-separation distributions on the named configurations | Security and prototype appendix |
| Optimized 5G rerun | Full path with final-only state, bypass and import changes | Prototype appendix |
| Sergey's M5 Max kit 1.6.6 sweep | Measurement archive; no inferred M5 update from M3 sweep | Evidence gap only |
| Bonsai 2 ladder and larger task evaluation | New measured results | Outlook |
| Post-PR15 CUDA import timings | Missing in the supplied FACTS revision; source requested | v3 gap map; historical PR9/CPU figures stay labelled |

KL stage2, heterogeneous eval5-eval7, GPU SWA qualification, kit 1.6.5 GPU/Mac ladders,
B300 measurements, vLLM bridge/node smoke and the cooled M3 kit 1.6.6 sweep are now measured.
Stopped KL stage3 is excluded. Earlier dated paragraphs below describe prior states.

External-review text response (2026-11-02): the publication now treats audit as proposed, with an open threat model
and a commitment chain rooted in empty state under the weights hash or a client-computed checkpoint. Cross-platform
honest-noise distributions, KL calibration, attack controls, challenge coverage and audit costs remain unmeasured.
The growing-session experiment (dev-b) must cover local/remote turns, catch-up and disconnect recovery at100–250k.
Engine run14 (dev-e) must include client import, match predictions to the measured5G setup, and equalize storage,
eviction and latency conditions without the artificial PRO6000 team cap. R13 numbers stay unchanged until that evidence
arrives. The corpus totals are reconciled as two bounded snapshots with identical filter parameters, not as an open
filter discrepancy. Details: `calc/PAPER-V2-GAPS-261101.md`, external-review response.

Overnight qualification update (hybrid-c-r10-261102): measured M3 parallel sweeps at64k/128k/260k and step57
realistic-agent calls are now in the paper, alongside both32k client anchors. The128k restored control and the
post34-minute-prefill lower bound are distinct. These observations do not update the run13 decode/economics model;
run14 owns that change. B300 llama.cpp and vLLM FP8 measurements replace the absence of server data, while the
published run13 B300 calculations retain their peak-scaling assumption explicitly pending run14. The first vLLM
bridge comparison is heterogeneous and uncalibrated,64 positions at784 tokens, with no full-path speed qualification.
PR9 CUDA imports and the single M3/5G point predate import-speed-v2. The source/evidence map and bounded controls are
in the r10 section of the gap map; older rows above describe historical engine assumptions.

Run14 qualification update (2026-11-02): M3 measured parallel depth/count
anchors, M5 Max128 using the same measured SoC, and B300 llama.cpp/FP8 rates
are now admitted in separate opt-in scenarios. Historical rows above remain
historical. Still missing: M3 three-stream measurements, >260016 depth at
four/six/eight streams, >131088 at twelve and >65552 at sixteen. These gaps
block numeric full-mix four-plus-agent days; conditional depth subsets remain
explicit. B300 step70 supplied no tuning run because pinned and comparison
builds are identical dde879bc. A separate-build tuning measurement is needed
before claiming any uplift. B300 vLLM transfer through the bridge remains in
qualification; FP8 rates are server-only. M5 Ultra hardware and GLM portability
are estimates. No new human product decision is needed for this engine run.

## Run14 r5 measurement and modelling limits

- Import-speed-v2 has no admitted Mac rate yet. Its sensitivity is explicitly
  pending; CPU speedups cannot fill the Mac cell. The old M3 rate is one point
  (39,504 tokens, 42.4 s), so a separate fixed intercept is unidentified and
  assumed zero. Other Apple/GLM import portability is not measured.
- The 5G component sum leaves 25.5 s of the measured 201.7 s unallocated.
  R5 reports that residual and does not fit it away.
- Step57 is a held-out check of the steady-throughput model; finite-batch drain,
  scheduling, prefill/decode interference and tool chronology are not modelled.
  The analytical batch32 server resource bound is not a server elapsed-time
  prediction. See the signed r5 report for quantified errors.
- Symmetric owned fleets use a shared explicit local-M3 mean/p90 prefill budget
  and separately budgeted session storage. Queue latency, storage contention
  and measured HBM/RAM/NVMe migration rates remain unqualified. Fixed-hardware
  reference/GLM tables are not optimized architecture comparisons.

- R5 prefill-price thresholds are conditional on the current routing, measured-fit
  server envelopes, rental tariffs and client budgets. They do not re-optimize
  routing for each hypothetical provider. vLLM costs remain server-only, and
  beyond-depth portions remain estimates. Strix/Spark power and extra-device
  cost reuse declared per-node budgets, not new measurements. A blended storage
  ceiling below the inactive NVMe floor requires changes to both storage tiers;
  reducing active RAM alone cannot meet it.

## Current run14 publication qualification (2026-11-02)

This update supersedes the earlier pending-run14 and pending31k-bridge/pilot entries.
Measured import is charged, M5 Max128 uses the measured same SoC, B300 uses its measured llama.cpp curve, and both
own-server routes optimize hardware/storage at every team size under identical retention and latency budgets.
The full-mix depth law now supplies explicitly modelled rows instead of R4 full-mix gaps:16agents models77.7%of calls
in depth and99.7%carry at least one flag. Symmetric latency rejects0/2106candidates; equal-retention costs drive selection.
The5G prediction is179.5s versus201.7s observed, preserving25.5s unallocated. Step57 local time is underpredicted
by8/22/37/33%; this limits extrapolated daily throughput. Queues, scheduling and storage-hardware timings remain unqualified.

The31,360-token bridge is heterogeneous and uncalibrated (checker exit5),64positions per client; the48-case homogeneous
pilot is partial at128k and does not establish task equivalence. The node-adapter functional smoke is now measured on the B300 through proxy/bench (7936196c):
8k KL0.0055/top1 63/64/noise ratio0.87;32k KL0.0256/top1 60/64/ratio2.38, free-run divergence at9.
All imports passed, checker5 heterogeneous/uncalibrated; same-GPU timing does not qualify speed. Also open: cooled kit1.6.6, Mac import-speed-v2, heterogeneous task evaluation,
KL study, sliding-window GPU qualification, growing-session acceptance, CUDA/Metal calibration and5G optimized rerun.
The no-break-even conclusion is scoped: measured clients at20% have a zero-prefill overhead floor above cheapest API;
M5 Max64 at50% and estimated Ultra256 have finite thresholds. No universal impossibility is claimed.

Independent paper review of the integrated head and engine r5i ACCEPTS exact2d457aed; no delta requested. Integrated-paper review remains with the orchestrator. Local signed delivery
is requested without push or tag. Evidence and exact control outcomes: `calc/PAPER-V2-GAPS-261101.md`, run14 section.
## Run15 cooled parallel qualification (2026-11-02)

The cooled kit1.6.6 sweep supersedes the old step55/restored128k-control base
anchors. It measures1/2/4/8/12/16/24/32 streams at32784 and65552 tokens, and
1/2/4/8/12/16 at131088, after the16-token suffix. The base uses np32/32/16;
np4 at128k is a separate server-shape sensitivity. Step56's260016-token
1/2/4/6/8 observations remain deepest;1.04M YaRN is historical only.

Still unmeasured: more than260016 tokens at1/2/4/6/8 streams, more than131088
at12/16, more than65552 at24/32, and count holes such as3/5/7/10. Six streams
have only the260k point, so shallower calls use its conservative held rate.
R14 r5's explicitly modelled depth law supplies numeric full-mix estimates;
the earlier R14 strict-gap paragraph is historical, not the current admission
policy. No count above32 is extrapolated. Of the full16-agent row,44.7524% of
calls and25.7257% of decode-device time are in the measured zone. All other
zones remain explicit and can overlap. This is not a fully measured day.

The260k points use the older build and np8, not a cooled kit1.6.6 measurement.
A same-build cooled260k sweep, additional counts, sustained realistic-agent
timings and Mac import-speed-v2 evidence would narrow the remaining limits.
These are measurement gaps; no new owner decision is required for this run.

## Current paper v3 qualification

See `calc/PAPER-V3-GAPS-261102.md`. Run15 updates all current embedded CSVs and derived figures.
At 16 agents, 44.7524% of calls and 25.7257% of decode-device time use the measured zone; the remaining
qualifications overlap. Six agents have 0% measured calls and 90.67% shallow-held calls at the 260k rate;
the row stays printed with a dagger, outside capacity ratios. No fully measured day is claimed.
Prototype main is `9348ecd6`; landed status does not qualify CUDA-to-Metal calibration or growing-session performance.
The full-refresh alternative restores the node's state, not equality with a separate local prefill.
