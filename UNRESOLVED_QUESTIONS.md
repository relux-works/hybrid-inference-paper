# Calculation assumptions requiring later evidence

## Resolved source question, analyst pass r21l

The accepted owner model-class export resolves the 17% / 5% provenance question: 260,201 of 1,530,739 calls and 4.6-4.8% of spending, plus the frontier-call and same-token price reference. Arithmetic and source hashes are in `calc/PAPER-V5D5-GAPS-261105.md`. The actual fraction of frontier tasks Qwen can complete remains unmeasured. Neither engine choice nor API admission changes this workload-class arithmetic. The current RULER status and revised RC 4 cutoff are recorded in the completed-analysis map.

## Historical RC 4 measurement boundaries (2026-11-05, r21k)

This historical section is superseded by the completed RULER status at the end of this file. Accepted engine24 economics and descriptive cache measurements are incorporated. At that original 2026-11-05 12:00 UTC cutoff, full RULER64k/128k, B300 decode and an admitted measured Qwen1M API point remain open. Saved RULER prefixes are interim and do not fill the registered analysis. Mac bf16, heterogeneous tolerance, timing-only runs and declared model follow-ups remain qualified waits; all10 raw sites are in `calc/tests/data/paper-v5d4-pending.json` and `calc/PAPER-V5D4-GAPS-261105.md`.

The40-turn CUDA/Metal run showed no long-session speedup. An identical task sequence without diagnostic critical-path work, separate cold start and task success at100k-200k on Metal is still required. Cost per call is not cost per completed task. Auditing remains research outside production reconciliation. A free-prefill overhead floor exceeds the measured cheapest API at the stated light load only; a universal all-load impossibility is not inferred. All earlier measurement records and calculations remain preserved.

## Historical v5a third-pass snapshot (superseded below by the current v5d map)

This section supersedes the historical measurement-status entries below. The original data boundary was 2026-11-05 12:00 UTC; the completed RULER pass below supersedes this historical cutoff.

Checkpoint 10 on Metal is measured with exit 5, top-1 64/64 and the reported controls; heterogeneous tolerance
and BF16-reference calibration remain pending. Qwen RULER 8k/32k score equivalence is supported (8k by post-review sidecars); Glimmer 8k is not equivalent. Text equivalence is not established at these depths. Qwen 8k/32k preceded registration; Glimmer was not named, straddled registration and uses the rules by extension.
Qwen 64k/128k, bf16 8k/32k and Glimmer 32k/64k/122880 remain input-state waits.

Normal-priority full M3 intermediate curves/Gemma need an idle Mac; Glimmer PRI31 is measured, with successive deltas and external-disk saves; its frozen engine thresholds still use interim PRI4 anchors;
16b follows the full curve. The GPU vLLM rework, Bonsai 2 ladder, timing-only instrument-free runs,
The server-side Qwen rebuild to1.04M is measured in30.2min; Mac download/import/logit/decode remains pending. Quality at depth, measured vLLM decode batching, bf16 RULER/GPU rehearsal/Mac work and the OpenRouter cache test remain pending. The20-document CUDA bf16 KL study is measured and does not close those other items.
The owner's commercial 98.1% aggregate is a scenario, not a measured Chutes rate.

Current applicability amounts await accepted R20/R21 results; every placeholder has an exact `% R20:` export comment.
R20 is read without merging; 5090 server rows are excluded by owner direction. Previous Q4 economics survives only
as a named historical calculation. New sources/maps: `calc/PAPER-V5A-GAPS-261103.md`,
`calc/tests/data/paper-v5a-pending.json` and `calc/tests/data/paper-v5a-r20-sites.json`.

## Historical assumptions and earlier status snapshots


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

## Historical paper v3 qualification

See `calc/PAPER-V3-GAPS-261102.md`. Run15 updates all current embedded CSVs and derived figures.
At 16 agents, 44.7524% of calls and 25.7257% of decode-device time use the measured zone; the remaining
qualifications overlap. Six agents have 0% measured calls and 90.67% shallow-held calls at the 260k rate;
the row stays printed with a dagger, outside capacity ratios. No fully measured day is claimed.
Prototype main is `9348ecd6`; landed status does not qualify CUDA-to-Metal calibration or growing-session performance.
The full-refresh alternative restores the node's state, not equality with a separate local prefill.
## Run16 qualification limits (2026-11-03)

| Question | Current declared behaviour | Needed evidence |
| --- | --- | --- |
| PRI31 M3 parallel capacity | All inherited mixed outputs carry `background_priority_interim`; cooled background measurements remain interim, including the six-stream260k-only gap | The new hash-verified normal-priority sweep via the data-only R16b interface; no final agents/day claim yet |
| M5 process priority | Priority not recorded; Sergey reports that the launching process showed PRI 31 when checked afterwards (2026-11-03 09:11 UTC) | Recorded process-priority samples for a later sweep, to qualify priority during the measured run |
| Separating token and depth import costs | Conditional depth OLS at delta539;48.7us/token retained from the weak original marginal fit; measured depth range2k–100k | A joint delta/depth sweep and repeated timings, especially beyond100k |
| Bounded undo and bf16 state | Unimplemented depth-free sensitivity; bf16 halves recurrent state bytes only | Transaction, rollback/lost-ack and cross-engine state-equivalence qualification before any production claim |
| 5G timing versus production behaviour | Capture-subtracted arithmetic residuals only; main-run checkpoint/fidelity unmeasured; turn7 and base retain sizeable prediction errors | A qualified checkpoint and an uninstrumented repeat; finer accounting of unallocated time and link variation |

The quoted8.45MB/s is reconciled: it is the old prototype's entry threshold
with15% saving required by margin+hysteresis, rather than equal-cost break-even.
The source base `fca0fe31` and the two preserved preflight plans support that
calculation. The exact driver `5be993f2` Git object was unavailable locally;
no fetch/download was attempted. This does not replace the recorded source
hashes in the original extracts.

## Current paper v4 gaps (2026-11-03 08:40 UTC source)

See `calc/PAPER-V4-GAPS-261103.md`. Both 5G timing arms completed 40 turns to 143,439 tokens at PRI 31. The Mac checkpoint 10 remains unmeasured after the fixed backend-label bug; the first recheck refused RAM before checker launch. The 4/4 GPU-rehearsal checkpoints are CUDA-only. Synchronous snapshots are inside measured TTFT; subtraction yields arithmetic residuals, not production timings.

RULER 8k: 390 paired examples on CUDA, identical 97.01% scores in all arms, zero per-example score disagreements. Text changes are 8.72%/8.21%; McNemar p=0.727, excess interval -2.13 to +3.12 pp. Equivalence at 2 pp is not established. 32k is running (about six hours from 07:32 UTC); 64k/128k await the owner budget decision.

Full normal-priority M3 parallel/Gemma/Glimmer measurements need an idle Mac; then R16b replaces interim capacity data. CUDA-to-Metal BF16 calibration needs the Mac. GPU vLLM state bridge awaits rework. Bonsai 2 2B/4B/9B ladder is later. Bounded undo requires implementation and transaction/lost-ack qualification; bf16 thresholds do not qualify its bridge.

## Paper v4b follow-up boundaries

Current pending-site inventory: `calc/tests/data/paper-v4b-pending.json`, explained in `calc/PAPER-V4B-GAPS-261103.md`.
The four TeX sites reference only FACTS section 5 waits; RULER8k, the timing arms, KL and the small task pilots are measured.
The r20c accounting supersedes the old25.5-second rounded subtraction: the first call has25.370 seconds outside three meters,19.659 inside request preparation and5.711 on the client outside preparation. Individual subphases remain untimed.
M5 priority was not recorded during measurement; a later PRI31 launcher check does not establish the measured process QoS.
Gemma's445.6 MB window follows geometry. R17 now supplies interim measured-rate thresholds; larger fixed bytes alone do not order them against Qwen. Normal-priority SWA and actual SWA import calibration remain pending.
The restored model-geometry table retains its prior analytical estimates; those estimates are not measured Gemma/Glimmer link thresholds.

## Engine run17 (2026-11-03)

- PRI31 Glimmer/Gemma Mac rates are pending; current kit1.6.5 background-priority
  data is interim. Data-only source/priority interfaces are documented in
  `calc/README.md`. R16b parallel replacement remains available for Run17.
- The SWA import assumption `r16_qwen_token_depth_portability` has no SWA import
  measurements. The window may add import work that this estimate excludes.
- Ideal tensor payload geometry is reconciled with full sequence-save geometry;
  actual prototype framing, chunking and SWA hybrid timings are unmeasured here.
  No new Gemma/Glimmer native hybrid runs were performed by this task.
- bf16 recurrent tensor wire economics assume half the f32 tensor bytes with
  unchanged resident memory/import/decode; measured quality of dev-a r38 is
  pending. This task makes no quality or production-readiness claim.
- Architecture extrapolation holds Qwen rates/import fixed and is not a claim
  about a real model. Lower fixed bytes alone do not establish model quality.

## Paper v4c current measurement boundaries

See `calc/PAPER-V4C-GAPS-261103.md` and `calc/tests/data/paper-v4c-pending.json` for all six macro sites.
Two additions are required by the owner's r20c inputs: timing-only Mac/node calls with separate spans, and
GPU/Mac quality and speed of the implemented lossy bf16 transport. The earlier four sites remain FACTS5 waits.
The base import2.908 seconds already sums all ten chunks. Subtracting snapshot downloads still retains
synchronous evidence-file hashing25.748GB inside node extend wrappers; residuals remain arithmetic upper bounds.
R17 thresholds at32k/64k/100k use same-build PRO6000 rates and exact tensor bytes, distinct from the retained
R16 B300/rounded-state sensitivity. Glimmer/Gemma Mac rates are interim PRI4; import reuses Qwen as a named estimate.
CPU bf16 implementation and normal-value rounding are measured; these facts do not qualify long-context27B quality
or GPU/Mac speed. Only recurrent wire tensors halve; resident memory and import/decode assumptions stay fixed.

## Analyst pass r21d

All26 legacy R20 sites remain pending for accepted engine22. Recorded PRI31 M5 Qwen/Glimmer data close the priority-recording caveat for the new measurements; older model outputs keep their original inputs as a historical calculation. RULER 8k/32k scores are post-result analyses with a margin fixed at14:36UTC; Qwen64k/128k are the strictly preregistered depths. Glimmer is exploratory. Paired BF16-wire KL does not qualify lossless transport, GPU rehearsal, Mac or bf16 RULER. No excluded cache-probe result is used.

## Owner pass r21e: current measurement boundary

Accepted bf16 RULER8k/32k and exploratory Glimmer32k replace the earlier waits;
Glimmer stops at32k by owner decision. Main 1M economics await engine22; Mac
slot download is measured, import/logit gate/decode/delta prefill remain pending.
Server restore is warm (newly written file, no OS-cache drop); cold restore is
unmeasured. vLLM decode batching is measured only at16k on PRO6000Workstation;
deeper PRO6000 and B300 batches still wait. GPU rehearsal and Mac bf16 quality
and speed remain pending despite the bounded CUDA KL and RULER observations.
The engine must revisit unmeasured M4 prefill:8.38 local sessions/day versus
6.73 for M5 on measured anchors. No current M4 row is presented.
Raw26 R20 source hooks remain unchanged; one visible applicability pending
notice supersedes their four repeated renderings. Exact current waits and
closed-scope authority are in paper-v5a4-pending.json and the gap map.


## Engine run18 (2026-11-03)

- Resolved source custody: canonical FACTS corrected5090 Qwen suffix to...e3e8
  on2026-11-03; the supplied full digest/manifest now matches. Original...16b
  discrepancy and corrected full digest remain in the report/quote ledger.
- Optional task boundary: default116-call normalization group per rental. The
  fitted call mix is not a chronological session trace. Actual task boundaries
  and trace/cold-start measurements would tighten economics. Whole-hour rounding
  is a sensitivity, not an assertion of Vast billing granularity.
- GPU import portability remains unmeasured: the CUDA-only PR9 joint delta/depth
  fit replaces the rejected Mac slope composition. Host full-slot file timings
  cannot separately identify the imported-delta endpoint/recovery cost. Measure
  that endpoint on each card/model; Glimmer import and bf16 quality remain pending.
- Full fitted workload exceeds GPU context caps. Conditional common-subset
  costs are not full-workload/persistent-machine quotes; aggregate GPU hours can
  require concurrent independent rentals. No Glimmer fetch/API price is supplied.

- R18 historical resource exception: free disk27754147840 B at2026-11-03
  11:45:52Z was below28GB. Own engine02 stopped by recorded PID (return-15); no
  foreign cleanup/control. After recovery, exact-current engine03 passed399
  tests with observed free space above28GB. The earlier breach remains recorded
  and is not converted into a successful resource-control claim.

- R10c resource exception: observer recorded 27867369472 B at
  2026-11-03T12:46:20.733004Z after the owned engine02 process was stopped
  (return -15). This violated the 28GB rule. The report preserves the earlier
  exit reading, later lower observation and monitoring gap. A retry uses a
  29GB intervention threshold; a later green suite cannot erase the breach.


## Run19 qualification boundaries

- R10c producer headf7aeef95 was still pending independent acceptance at
  branching; R19 uses that explicitly permitted parent, not an invented review.
- The 5090 client-kit path is reused for a hybrid prefill node by assumption.
  Measure that binary and concurrent service before calling the node qualified.
- About13GB usable KV/state is an owner-provided estimate. Physical368885,
  configured262144 and measured249000 token bounds differ. Full fitted calls
  exceed these limits; the10885-call conditional quote is not full-workload cost.
- Same-card file save/restore timings support full-session migration; RAM
  direct-copy speed and storage provenance are not isolated. Uniform session
  popularity and249k reservations give sufficient fleets, not optimal packing.
- The sourced1999.99USD card listing is sold out. Host1500USD, cache sizes and
  power are unpriced estimates. A current available box quote may change the
  narrow larger-team comparison with the cheapest API.
- Rented GPU-work cost is a utilization allocation, distinct from a full warm
  calendar lease. Startup/model fetch, independent retention provisioning,
  provider host resources and persistence across terminated leases are not
  qualified. Client demand throughput is not established by server sizing.

## Run20 qualification boundaries

- Run19 exact-head review was pending at branching from3a1eed0d. No independent
  acceptance is invented. R10c f7aeef95 acceptance was subsequently observed.
- vLLM decode1/8/32-stream measurements are pending. BF16 KV prevents some
  planned deep parallel cells from fitting; missing measurements cannot
  override physical capacity.1M rates are extrapolated bandwidth bounds only.
- PR16 bridge server timings are measured smoke envelopes, not isolated
  conversion cost or production latency. FP8-KV bridge portability, deeper
  geometry, GPU concurrency, CPU occupancy and task quality need measurement.
  Heterogeneous checker exit5 remains uncalibrated.
- vLLM state restore is unmeasured here. Uniform residency misses rebuild the
  cold prefix; that prefix already includes pending history, which must not
  be charged again. Retention/workspace/weight budgets are estimates.
- API admission is snapshot-based.98.1% is the owner's aggregate commercial
  cache share, not a measured hit rate at each OpenRouter endpoint. The
  provider-specific data-only interface is empty. Snapshot availability is
  historical, and unknown availability is disclosed rather than measured.
- The common measured-envelope subset covers27.28% of the fitted workload.
  Full-workload economics and universal team-size claims are not established.
  Costs/multiples omit the equal non-open commercial share. Client purchase
  prices and non-5090 rental prices are inherited estimates, not new offers.
- Dedicated server calendar costs differ from shared work-price allocations.
  Hybrid fleets are sufficient under the R19 provision policy, not proven
  minimum fleets. Break-even scans stop at500, so no infinite-team theorem.
- The shared filesystem briefly fell below28GB during this run. The observer
  minimum/resource-exception and gate logs preserve this failure; subsequent
  passing tests cannot retroactively satisfy the throughout-run floor.

- Run20 budgets one recurrent state/session. Additional vLLM prefix-checkpoint
  and allocator overhead is unmeasured; modelled residency/batching capacities
  are conditional on that idealization, not deployment guarantees.

- Later R19 review CHANGES REQUESTED at3a1eed0d is a rental coverage-label
  finding only. R20 inherits that producer base and preserves R19 exports as
  required; the historical R19 finding remains for its own rework. New R20
  price/threshold rows explicitly carry coverage and normalization, covered
  by a named regression and narrowing mutant.

- The R20 bridge coefficient is a token-weighted smoke average projected
  through zero, not a short-turn latency fit or a conservative upper bound.
  Fixed overhead is visible in the54-token increment; geometry portability
  remains an economic sensitivity until measured at workload deltas/depths.

## Run21 qualifications

- The delivered session package contains aggregates, not raw calls. Claude
  pauses are median8.1/p9060.6s, versus7.8/34.8s combined. No raw recomputation
  or per-model depth averages is possible from the counts-only model list.
  Deep quantile+mean reconstruction, conditional delta means, rank pairing,
  tail endpoints and a300s active-gap cap are modelling assumptions. Published
  source statistics and actual model marginals are both exported.
- No measured1M delta-prefill or normal-priority1M decode is available here.
  The1.67tok/s at1.04M is background priority; the~7.42tok/s raw M3 ceiling
  is not achievable-throughput evidence. Deep Mac imports extend the R16
  recovery-depth law. Fresh0.8/2.8MB/s observations have no raw trace supplied;
  full-slot5.18MB/s is a delta-path portability sensitivity.
- vLLM deep cached/cold rates and session admission beyond249k remain
  extrapolated; planned512k/1M decode data uses a guarded data-only interface.
  Hybrid Qwen must use model-card YaRN factor4 on client and server. API
  providers' extension method and equivalent task quality are unknown.
- GLM/M5Ultra, Studio1M57min and GLM B300 prefill carried from Qwen are
  unmeasured. FP8 GLM328GB requires at least2B300 GPUs; ideal summed
  bandwidth omits replica communication. Expert-union batching includes
  complete per-session KV/state, rather than treating KV as shared weights.
- The local GLM research note omits cache declarations and exact metadata for
  the grouped endpoints. Its individually listed candidates fail closed;
  cheapest/median admitted GLM prices remain noncomputable until data arrives.
- 5090 server choices are excluded from run21 by owner decision. Their frozen
  run20 rows are not used in the paper; measured5090 client interfaces remain.
  The historical R19 F1 basis is fixed in source and a run21 successor view,
  preserving all R13–20 bytes. Historical office zero boxes mean local bypass;
  the R19 report's share table is NVMe; hybrid fleet sizing stays sufficient,
  not proven minimal. PRO6000 rate-basis relabelling now refuses.
- Initial run21 inspection observed27.821GB free before writes, below28GB.
  Writes were held until recovery. Shared-disk floor compliance throughout the
  task cannot be claimed; subsequent green tests do not erase that observation.

- The growing-task companion also keeps the projected GLM two-GPU replica,
  whole eight-GPU node prices and finite concurrency. Studio250W/$8000 and its
 57min cold integral remain estimates, not new hardware measurements. It
  grows by conditional mean input plus mean generated output and median gaps;
  correlations and task quality are unqualified. At50 staff/two1M tasks/day,
  projected GLM hybrid can undercut its own cluster while Qwen hybrid does not;
  unavailable GLM API admission prevents a qualified API multiple.

R14/r5x publication status: R20 API population and partial availability labels
are corrected; native llama bridge duplicates are labelled not applicable.
Independent re-review remains pending. Paper projections exclude5090 servers;
measured5090 clients remain in scope. R20 full numerical cells and R21 full
CSVs are preserved. The review's nonblocking sample-size/plausibility guards
for future measured cache/decode rows and the single-source discount reading
remain open; published measurement replacement lists are empty.

R15/r5x2: words-ready billing and link conditions are now embedded and parsed
in every paper sentence and report quotation; no numerical cells change.
Independent re-review remains pending. Snapshot-bound parser/link choices
state the office and engine-WAN assumptions; this adds no measured link rate
or measured deep-model result. Existing capacity alarms stay nonfinite and
are explicitly disclosed in sentence text.

## Paper v5b current boundaries

The accepted run 22 closes model/economics deferrals, not physical measurement waits.
All 26 historical R20 sites have explicit accepted successors. Current economics cover the owned M5 Max
and selected call shapes, not M3 money claims or the full unconditional source workload. Server decode
remains modelled for every selected economic call; the 16384 measurement is a distinct coordinate.
The deep Claude profile is local-only with zero offload and zero occupancy. Provider cache rates and a
measured common availability window remain pending; zero cache is priced rather than excluded.
1M M3 thresholds use extended local-rate/import estimates; M5 has no positive anchored budget.
Warm server restore is never treated as direct Mac delta import. The direct Mac interface remains empty.
Remaining physical waits are enumerated in paper-v5b-pending.json and PAPER-V5B-GAPS-261103.md.


## Paper v5c measurement status

Accepted direct Mac 512k/1.04M local timings and five same-device depth-quality cases close their former waits.
PRO vLLM decode is measured at four depths, interpolated between them, modelled outside; B300 still modelled.
Warm full-slot LaCie recovery is a proxy, not a delta-import measurement; the raised raw-logit bound is uncalibrated.
Remaining sites and authorities: `calc/tests/data/paper-v5c-pending.json` and `calc/PAPER-V5C-GAPS-261104.md`.


## Paper v5d part 1 remaining waits

The capped M3 grid, bf16 GPU rehearsal and descriptive API cache/availability study are measured.
Measured-cache economic use awaits engine run 24; no new cost/crossing is inferred in part 1.
Saved interim RULER64k/128k rows now cover368/390 and225/390 after the owner stopped the nodes on2026-11-04; complete registered analyses remain pending;
the cut-off stays 2026-11-05 12:00Z. B300 decode remains modelled because no rental container started.
All current sites and other unchanged hardware/calibration waits: `calc/tests/data/paper-v5d1-pending.json`.

## v5d part2: current status

Saved Qwen RULER64k/128k rows are descriptive serial prefixes, not completed registered depths. Missing22 qa_2 and165 examples respectively; original nodes queued to restart with frozen per-depth identities. Both depths remain p1 in Holm. All three measured Qwen1M providers are excluded below95% availability; no admitted measured Qwen1M price exists. Engine24 measured-cache economics pending. Private hybrid-inference-data exists, evidence snapshot after RC4. Current finite waits: calc/tests/data/paper-v5d2-pending.json. Older entries above record their historical observation dates.

## v5d part3: RC4 close

Accepted engine24 closes the measured-cache economic-model wait. Qwen v1 and GLM v1/core have cadence-labelled partial priceable cohorts; Qwen core remains unavailable. Full RULER64k/128k, B300 decode and an admitted Qwen1M provider remain pending at the owner-set2026-11-05 12:00Z cut-off. Other calibration/model/future-work qualifications remain mapped in calc/tests/data/paper-v5d3-pending.json. Earlier engine24 pending statements above are historical. Private evidence repository snapshot followsRC4.

## RC 4 candidate review, r21m

Pending engine 25: Part A verifies fleet minimality with one or two nodes and RAM/NVMe/on-demand restore; Part B recalculates a true closed perimeter at 100% model share; Part C measures covered token/work shares. The analyst's approximately $20 instead of $57 light-load figure is conditional on one node sufficing, not a replacement for table 18. Mac logit calibration needs paired local runs with different partitions at the same depths. Registered RULER/Holm still awaits 128k completion on node A with node B's build; 64k is now complete. Clean paired end-to-end replay is preregistered, not run. Native engine 24 prices remain unchanged; long-pause measured-cache cohorts do not establish a short-interval recommendation.

## Current closed-perimeter scope, r21n

The20% Qwen component admits5-medium/2-heavy crossings inside a closed perimeter only with an internal larger model handling the other80% at the same cost in both alternatives. This supersedes r21m's assumption of an external cloud remainder. Full100% and mixed-scheme conclusions wait for engine26; no accepted engine25 revision is available at writing. Existing fleet/coverage waits remain. New unmeasured inputs: GLM decode/prefill on Studio; GLM prefill on B300; M5Ultra extrapolated from M5Max by owner decision; Studio512GB price/configuration; middle-class task share as an input scenario. Exact pending macros: calc/tests/data/paper-v5d7-pending.json.

## Current status after accepted engines 25 and 26

Fleet alternatives, fitted coverage, full-Qwen and internal mixed-scheme comparisons are calculated;
they do not qualify restore proxies, real arrivals or task-success substitution. Studio/GLM speeds,
GLM import/quality and cloud-class throughput/interconnect/storage remain unmeasured. Reported
Studio list-price proxies and the owner-directed Ultra projection replace former missing numeric
inputs, without becoming measured hardware rates. Remaining physical waits include RULER128k/Holm,
long-session vLLM handoff/quality qualification, the planned clean lifecycle replay, Mac calibration
and the existing B300 decode/Mac-bf16/model follow-ups. Exact macros: calc/tests/data/paper-v5d10-pending.json (current inventory).
The corrected FACTS now supplies the0/112 export control and exact codec/append diagnostics. Quantile packet8432f75d is a frozen planned artifact
under review, not inference or a dev-e numeric prediction.

## Current post-review status, v5d9

524288 Metal partition/repeat noise is0 and the historical1.08298 is reproduced cross-device;
1040000 calibration was cancelled,3.01402 unexplained. This is partial, not calibrated acceptance.
The vLLM export, codec and append are exact; even full-server N-1 handoff refuses the unchanged
quality gate. One natural-text document is measured; long-session qualification remains pending, not impossible.
The pre-probe forecast exists; the second signed numeric commitment and inference remain pending.
Architecture traffic and GPU/link start capacity are shown arithmetic, with assumed starts/uniform
arrivals and no full-path/queue claim. RULER128k/Holm and near-tie scope unchanged by this pass.
Exact macro inventory: calc/tests/data/paper-v5d9-pending.json.

## Current v5d10 waits

The near-tie softcap hypothesis has no GPU result: reconstruct exact pinned prompts with hash checks,
or predeclare a separate new dataset. Attempt 5 on predeclared natural text refused top-1 at turn 4,
so vLLM long sessions remain unqualified. A near-tie-aware criterion needs advance specification
and unseen documents. N6 remains a phrase-checker limitation: appended token-preserving contradictions
need full prose review; finite omission and semantic narrowing controls are retained.
RULER completion/Holm and all existing 128k mentions are unchanged for the separate pass.
Mac calibration at 1.04M, the clean paired lifecycle experiment, B300 decode, Mac bf16/current-build
and declared model follow-ups retain their physical waits. Exact macro inventory:
`calc/tests/data/paper-v5d10-pending.json`.

## Current completed RULER status, `v5d11`

This section supersedes every earlier RULER wait and registration-timing summary in this historical log.
All four Qwen f32 depths have 390 pairs; Holm is complete. The 128k registered interval passes, but
the frozen supplementary guard withholds score equivalence. Scores at 8k/32k/64k meet the stated
bound, without a simultaneous four-depth or text-equivalence claim. The margin followed 8k/32k;
128k straddled registration (zero or one row before it), then changed hosts using the original binaries.
bf16 8k/32k analysis is reported; higher bf16 depths were never measured and enter as absent p=1.
The release measurement cut-off is 2026-11-06 06:00 UTC. Both deep RULER completions and vLLM
attempt 5 followed the original cut-off. Every unrelated pending macro is retained byte-for-byte;
Mac calibration/bf16, vLLM qualification, clean paired end-to-end replay and the other declared
physical/model waits remain. Current inventory: `calc/tests/data/paper-v5d11-pending.json`.

## RC 4 publication prerequisites, 2026-11-06

The owner-signed tag and fresh-node bundle proof remain incident-lane steps. No private-history runtime blocker remains; the production tag gate is expected 1 until the owner tags. The diagnostic source PDF must be rebuilt as release assets after the owner recommit/tag. The completed RULER results and F1 correction above remain current.
