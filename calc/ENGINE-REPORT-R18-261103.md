# Engine report R18 — 2026-11-03

Run `hybrid-e-r10-261103`, reworked by `hybrid-e-r10c-261103` after review
`hybrid-rev-r5v`, branch `engine-r18`, accepted base
`714fe72135819ededd7c270dd661c1359acfa6c3` (Muse r5t ACCEPT). CPU only, no
downloads, model loads, native builds or push. All 907 prior exports remain
byte-identical. New exports are under `calc/out/run18/`; their index binds
generator/source identities and every output hash.

## Source custody and client classes

All four supplied archives pass full SHA256 and internal-manifest checks.
The original FACTS5090 Qwen suffix `b10541aa...16b` disagreed with the supplied
archive. The exporter refused before writing outputs (actual exit1). Canonical
FACTS was then corrected externally to `b10541aa...e3e8`, explicitly dated
2026-11-03. The corrected snapshot and expected suffix were imported; the
strict gate itself was retained, with no override flag. The full archive SHA is
`b10541aa8957930e096a2316c5c74e28a87511d1fb5494fac002067cebf4e3e8`.
The quote ledger preserves this correction. Signed checkpoint7867b9cc records
the earlier unresolved state; it is superseded by the completed calculation.

| Client/model | Hard one-slot context | Nominal rate ladder | Parallel measurements |
|---|---:|---|---|
| RTX3090 Qwen | 99328 | 16k/50k/86k | 32k:1/2 streams;65552:1 |
| RTX5090 Qwen | 262144 | 16k/50k/100k/150k/200k/249k | 32k:1/4;65552:1/2/4;131088:1/2;260016:1 |
| RTX3090 Glimmer | 131072 | 16k/50k/100k/118k | 32k:1/4;65552:1/2/4/8 |
| RTX5090 Glimmer | 131072 | 16k/50k/100k/118k | 32k:1/4;65552:1/2/4/8/16 |

Capacity checks `prefix+delta+output`. A 3090 Qwen session beyond99328 refuses,
including output growth; endpoint holds cannot extend capacity. Physically
fitting sessions above the last measured ladder depth remain rate-coverage gaps.
Raw prefill rates interpolate nominal depth and delta; shallow depths and
deltas outside512..10000 hold the nearest measured endpoint as an estimate.
Decode is the mean of the three raw `n/elapsed` turn rates at each depth.

All85 segment/delta/decode cells reconcile with FACTS using kit-display
reductions. Two raw-once differences are recorded:3090 Qwen86k decode
20.114818635 vs FACTS20.12 (mean rounded rows20.116666667), and5090 Glimmer100k
59.635795092 vs FACTS59.63 (mean rounded rows59.633333333). Calculations use
raw timings, not display values. Task extracts and `facts-verification-03.log`
preserve the check; full custody hashes are in the measurement README/config.

Parallel lookup preserves exact stream count, actual depth and server np.
Step50 at 32k is a single reported aggregate plus its single control; step55
uses raw `n-1` decode intervals from one restored round with zero cooldown.
These are not the cooled three-round Mac medians. Missing counts or whole
shape files refuse; no interpolation/fabrication across server configurations.
All24 parallel observations retain their protocol and slot context.

## Link thresholds

Same Run17 grid: prefix32000/64000/100000;delta512/2343/10000. Qwen f32/bf16
payloads use34816B/token plus156893184/78446592 recurrent tensor bytes. Glimmer
uses7072B/token plus43450368B of saturated window. No protocol framing or
catch-up is invented. Server rates are kit1.6.5 PRO6000, same build/weights;
RTT0.14058910400490277s. No new GPU hybrid run was performed.

Named import assumption: `cuda_pr9_joint_delta_depth_portability`. Unweighted
joint OLS on all 18 hash-verified PR9 CUDA call records refits the intercept
and both slopes together:

```text
import_s = 1.489389799537046 + 0.0004963026481723266*delta
           + 0.000002064768751033477*prefix_depth
```

The source is `data/measurements/run14-2026-11-02/pr9/` file
`hybrid-bench-r13-27b-cuda-20261101T132757015879Z.jsonl`, SHA256
`b88f8fb440db84abbd48b9d5a606e07ec672b3ed11f16b73fef4a66ece82a634`.
Its positive-import calls span delta 43–87787 and depth 0–127606. The joint
fit's largest relative residual is 13.0%; largest overprediction is 5.19%.
These are in-sample checks, not independent predictive validation. At
127494–127606, the six small imports are 1.686–1.760 s; predictions are
1.774–1.798 s. The rejected composition predicted about 6.06 s there.
The Mac slope is never read, accepted as provenance, or added to this fit.

The preferred host-specific route was evaluated first. Kit 1.6.7 records
full-slot file save/restore timings at every ladder depth (table below), via
`bench/gpu/tools/hybrid_bench.py` lines 217–224. They include full-prefix
serialization/filesystem work and do not measure the imported-delta endpoint.
PR9 `import_ms` does not separately identify recovery versus delta application.
Consequently neither replacing import by a slot round trip nor adding these
slot costs to PR9 is identified by the supplied evidence. The permitted
CUDA-only depth-aware fallback is used instead. Native timings remain direct
diagnostics; none is silently added to a marginal intercept. No evidence is
assumed that PR9 predates recovery saves.

| Client/model | Prefix | Slot save ms | Slot restore ms |
|---|---:|---:|---:|
| rtx3090_glimmer30 | 16000 | 84.362 | 49.698 |
| rtx3090_glimmer30 | 50000 | 206.286 | 124.403 |
| rtx3090_glimmer30 | 100000 | 523.637 | 250.024 |
| rtx3090_glimmer30 | 118000 | 442.234 | 286.21 |
| rtx3090_qwen27 | 16000 | 338.458 | 183.336 |
| rtx3090_qwen27 | 50000 | 915.499 | 520.845 |
| rtx3090_qwen27 | 86000 | 1508.899 | 908.192 |
| rtx5090_qwen27 | 16000 | 316.203 | 85.56 |
| rtx5090_qwen27 | 50000 | 519.758 | 282.731 |
| rtx5090_qwen27 | 100000 | 801.337 | 593.491 |
| rtx5090_qwen27 | 150000 | 1148.067 | 883.53 |
| rtx5090_qwen27 | 200000 | 1627.326 | 1181.814 |
| rtx5090_qwen27 | 249000 | 2054.961 | 1575.151 |
| rtx5090_glimmer30 | 16000 | 35.467 | 21.293 |
| rtx5090_glimmer30 | 50000 | 86.391 | 55.281 |
| rtx5090_glimmer30 | 100000 | 164.111 | 122.915 |
| rtx5090_glimmer30 | 118000 | 263.371 | 149.949 |

These paired rows reconcile saved/restored token counts and file bytes in the
four already verified archives. They are not hybrid import benchmarks.
`import-evidence.json` under the rework scratch retains all 17 pairs, source
paths/hashes, fitted coefficients and all 18 import residuals. The exported
sources now explicitly bind the PR9 digest as well as the kit archives.

Portability of the old PR9 Qwen CUDA endpoint to RTX3090/5090 and to Glimmer
remains an estimate. Large calls in PR9 used the old chunked protocol; these
coefficients are not a measurement of a new single-message GPU implementation.
No local GPU hybrid measurements or uncertainty intervals are claimed. bf16
changes wire bytes only; import speed is unchanged and quality remains pending
dev-a r38. These thresholds are conditional on this import estimate.

Budget=`local-server-import-RTT`; threshold=`wire/budget`. Nonpositive budget
means no finite winning link, represented by a named status and alarm, never0.
Capacity refusal and missing measured rates are separate statuses. MB is
decimal; Mbit/s equals8×MB/s. Equality ties; a faster application link wins.

| Client/state | Prefix | Δ512 MB/s | Δ2343 MB/s | Δ10000 MB/s |
|---|---:|---|---|---|
| rtx3090_glimmer30/f32 | 32000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx3090_glimmer30/f32 | 64000 | never (budget≤0) | never (budget≤0) | 169.427 |
| rtx3090_glimmer30/f32 | 100000 | never (budget≤0) | never (budget≤0) | 66.625 |
| rtx3090_qwen27/f32 | 32000 | never (budget≤0) | never (budget≤0) | 693.268 |
| rtx3090_qwen27/f32 | 64000 | never (budget≤0) | never (budget≤0) | 183.494 |
| rtx3090_qwen27/f32 | 100000 | capacity refusal | capacity refusal | capacity refusal |
| rtx3090_qwen27/bf16 | 32000 | never (budget≤0) | never (budget≤0) | 585.587 |
| rtx3090_qwen27/bf16 | 64000 | never (budget≤0) | never (budget≤0) | 154.993 |
| rtx3090_qwen27/bf16 | 100000 | capacity refusal | capacity refusal | capacity refusal |
| rtx5090_qwen27/f32 | 32000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_qwen27/f32 | 64000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_qwen27/f32 | 100000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_qwen27/bf16 | 32000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_qwen27/bf16 | 64000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_qwen27/bf16 | 100000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_glimmer30/f32 | 32000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_glimmer30/f32 | 64000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |
| rtx5090_glimmer30/f32 | 100000 | never (budget≤0) | never (budget≤0) | never (budget≤0) |

There are 42 nonpositive budgets, 6 capacity refusals (3090 Qwen 100k), and
6 finite thresholds. Four former “never” cells become finite: 3090 Glimmer
64k/10000 at 169.427 MB/s and 100k/10000 at 66.625 MB/s; 3090 Qwen
32k/10000 at 693.268 MB/s f32 and 585.587 MB/s bf16. The already-finite
3090 Qwen 64k/10000 values change from 921.609 to 183.494 MB/s f32 and
778.461 to 154.993 MB/s bf16. Every 5090 budget remains nonpositive under
this import estimate. This is not a universal GPU hybrid architecture claim.

## One ephemeral rented-task comparator

Qwen has the supplied fetch measurements:18.97GB,185s on5090 and1029s on3090.
Observed Vast offers on2026-11-03 are3090$0.122–0.162/h and5090$0.448–0.522/h;
rented prices are$0.153/h and about$0.55/h. These are dated observations, not
market rates. The rented5090 price exceeds the search range and is retained.
Glimmer fetch time/API tariff is not supplied; no Glimmer rental quote is invented.

Declared scenario: one116-call normalization group per independent rental,
using the engine’s existing grouping assumption. Every rental pays model fetch,
a cold prefix and local delta prefill/decode/tool-idle wall time, and loses
model/session on termination. A final partial rental pays too. Both prorated
hourly quotes and whole-hour rounding are shown; rounding is a sensitivity,
not an assertion of Vast billing granularity. Cold-prefix cost integrates the
measured segment-rate law analytically and averages every included prefix.

The fitted aggregate call mix is not a chronological task trace. One initial
cold prefix per116-call group and warm per-call rates are economic assumptions,
not a reconstructed growing session or proof that a continuous116-turn task
fits. Actual task boundaries/trajectories would tighten the estimate. Individual
calls are admitted through output growth. No persistent state is credited across
rentals, and no API fallback occurs inside the fully-local rental scenario.

The full39904-call fitted distribution exceeds every card’s context limit.
3090 Qwen physically fits11551 calls (28.94697%), while9324 calls (23.36608%)
are within measured rate coverage through output. All alternatives condition
on that same common measured-capacity distribution. Full-workload rental cost
is explicitly unavailable. No truncation or dropping of the unsupported fraction
is hidden inside a full-workload quote. Physical and measured shares are distinct.

Demand is52500 calls/person-month (2500/day,21days). The hybrid reference uses
an already-owned M3 Max plus API overflow, with its R16b parallel qualifier.
Owned-server cost is the inherited B300 eight-GPU node divided among five
people; it is not asserted to be the cheapest possible owned machine. API
tariffs are the inherited Qwen references; no API/local model-equivalence claim.

| Option / observed rented price | USD/1000 calls | USD/person-month |
|---|---:|---:|
| rtx3090_qwen27 / ceil_hour_assumption | 2.601000 | 138.465000 |
| rtx3090_qwen27 / prorated_hourly_quote | 1.493842 | 77.528757 |
| rtx5090_qwen27 / ceil_hour_assumption | 4.950000 | 249.150000 |
| rtx5090_qwen27 / prorated_hourly_quote | 2.190986 | 114.416588 |
| Cheapest API reference | 0.897700 | 47.129235 |
| Median API reference | 4.243098 | 222.762657 |
| Hybrid M3 + API overflow | 3.061813 | 160.745195 |
| Own B300 node allocation | 64.193556 | 3370.161710 |

At rented prices, the3090 is cheaper than5090 despite slower compute because
its hourly price is much lower. The cheapest API reference remains cheaper
than either rental case on this conditional distribution. Monthly GPU-machine
wall hours are506.724 for3090 and208.030 for5090; whole-hour billed totals are
905 and453. Both wall totals exceed21×8h. Costs therefore sum independent
task rentals and may require concurrency; they do not claim that one GPU
serves the month in an8h/day calendar. Offer availability, concurrent hosts and
unquoted storage/network charges are not inferred from the hourly observations.

## Exports, interfaces and validation

Five CSVs contain51 raw rate rows,24 parallel observations,54 thresholds,12
rental price/billing rows and4 capacity-coverage rows. There are9 generated
files plusINDEX; the quote ledger has 2700 complete coordinate-qualified records,
including the canonical checksum correction. No paper prose/figures or run13–17
exports were rewritten. Manifests retain 112 explicit alarm cells:84 for the 42
nonpositive thresholds,24 for6 capacity-refused rows,4 for unsupported full
workload costs. They are expected mathematical/coverage exclusions, not zeros.

R16b and Glimmer/Gemma PRI31 data-only interfaces are unchanged. Run18’s M3
comparison reads the current R16b selection and qualification flag; frozen
Run17 audits bind to accepted714fe721 independently of future data selections.

Python3.14.4/Linux x86_64, standard library only. All gate commands run as
standalone processes with actual exits/PIDs/timestamps, no `tee`.
`PYTHONDONTWRITEBYTECODE=1`, on-disk task `TMPDIR`; exact commands are in
`calc/README.md`. No downloads, native builds, accelerators or push.

Original run10 checks below predate the CUDA rework; current checks are
recorded in the rework section.

| Gate | Real exit / evidence |
|---|---|
| Complete exporter | 0; `export-01.log` |
| Canonical correction quote coverage | 0; `quote-update-01.log` |
| Original 21-test Run18 suite | 0; `focused-complete-06.log` |
| Original R18 full engine suite | 0; `engine-suite-03.log` |
| Kit24; unchanged bench identity | 0; `kit-suite-01.log` |
| Index/manifests/907 frozen files | 0; `audit-complete-01.log` |
| 85 FACTS cells | 0; `facts-verification-03.log` |
| Five bounded fault controls | 0; `mutants-complete-03.log` |

| Mutant | Narrows gate to | Named failing test |
|---|---|---|
| omit_output_capacity | Prefix+delta+output | test_3090_capacity_rejects_prefix_delta_and_output_overflow |
| extrapolate_decode | Coverage distinct from capacity | test_rate_coverage_rejects_extrapolation_inside_capacity |
| persist_between_rentals | Repeated fetch+cold per rental | test_rental_rejects_free_fetch_persistent_state_and_dropped_tail |
| floor_billed_hours | Explicit ceiling-hour sensitivity | test_rental_rejects_floor_hours_and_quote_billing_conflation |
| priority_manifest_only | Raw Linux TS/nice0 evidence | test_priority_rejects_override_and_background_server |

All five controls exit1 at the named assertion; parent gate exits0. No setup
errors or survivors. Output/history byte-corruption and missing/forged quote
plants also have valid positive controls. All378 prior engine tests retain
their names. No surface table/separate landing property suite was supplied
(brief gap). Out-of-contract rows are the unmeasured rate regions, unsupported
full-distribution contexts, Glimmer fetch/API price, actual task chronology,
unmeasured CUDA/SWA import portability and unqualified bf16 quality.

Historical diagnostics are preserved: initial source checksum refusal exit1
before writes; canonical correction then admitted the exact archive. An early
FACTS rounding-bound check failed; the corrected check reconciles the actual
mean of already-rounded kit rows and declares raw-once differences. A394-test
engine pass on earlier source preceded bounded self-review corrections; it is
superseded by engine03 for final-source validation. No failed/partial run is
presented as a passing gate.

Free disk is sampled each second. A task-owned guard checks the recorded PID
and process start identity before stopping its own long suite at28.1GB, above
the28GB floor. It never signals foreign processes. Resource logs preserve exact
observations and any intervention; task scratch is only about2.2MB.

## Review boundary

GPU import portability, bf16 quality and actual chronological rental tasks
remain explicit model limits. These are engine predictions on measured client
rates, not new end-to-end GPU hybrid measurements. No push or hosted landing.

## Original R18 verification and resource exception (before r10c)

Ready for review. Exact-current engine03 passed399 tests (exit0); focused06
passed21 (exit0); kit01 passed24 (exit0), with unchanged bench identity.
All 907 prior export files remain identical. Numeric source/config identity is
unchanged since complete export01; only documentation changed afterward.

The requested28GB floor was not maintained in the earlier attempt. At
2026-11-03T11:45:52.062071Z the observer recorded27,754,147,840 B. The guard had
sent SIGTERM to its own engine02 PID2702938 at28,010,504,192 B; actual gate
return-15 is not passing evidence. Free space continued downward afterward.
The writer was not identified; task scratch used about2.3MB and no foreign
files or processes were removed/stopped. The observer stopped on failure and
resumed after headroom recovered, preserving the original failure/minimum.
There is no continuous-observation claim for the intervening gap. Recovery and
a passing rerun do not erase the earlier resource violation.

The successful suite ran from2026-11-03T11:51:05.951901+00:00 to2026-11-03T12:00:26.786959+00:00,
558.198s measured by unittest. Its sampled free-disk minimum was
30391681024 B across560 observations
(all above28GB). Overall observed minimum remains
27754147840 B. `resource-final.json` preserves both intervals.

The conditional cost distribution is reweighted to a hypothetical52500-call
month; the quoted monthly figures are not merely the cost of23.37% of an
otherwise unsupported actual month. Baseline comparator custody can also be
traced through frozen `calc/out/run17/f32/r17_f32_sources.json`; its bytes are
pinned by the907-file history audit. No model/persistence/market claim is added.


## CUDA import review rework — hybrid-e-r10c-261103

Blocking finding `r18-cuda-import-depth-double-count` is addressed with the
joint CUDA fit above. Both reviewer reproduction tests retain their names in
`calc/tests/test_r18_cuda_import_depth.py`. Before the fix they exited 1 with
two assertion failures: deep ratio 3.5914 and the four false “never” cells.
The corrected 26-test Run18 suite exits 0 (`focused-03.log`). The synthetic
fit control independently recovers a known two-axis law; rank deficiency,
negative fitted costs, omitted depth and Mac slope provenance refuse.

The rental comparator never consumes `cuda_import`; it is byte-identical to
`12f0c042`, as are rates, parallel observations and capacity coverage. No
cost quote changed. Threshold, alarm and provenance sidecars were regenerated.
The ledger preserves all 2519 current table-cell coordinates and the prior
checksum correction, plus 180 exact old/new changed-cell records against
`12f0c042`. A missing rework record or forged old value fails a named test.
The 907 run13–17 export files remain byte-identical. R16b and both SWA PRI31
data-only interfaces and all previously named engine tests are retained.

| Mutant | Narrows gate to | Named failing test | Actual exit |
|---|---|---|---:|
| mac_slope | Deep CUDA observations rather than Mac recovery slope | test_model_matches_pr9_cuda_measurements_at_depth | 1 |
| allow_mac | Explicit CUDA provenance gate | test_cuda_import_refuses_mac_slope_on_cuda_host | 1 |
| marginal_intercept | Intercept refitted with both predictors | test_cuda_joint_fit_refuses_rank_deficiency_and_negative_costs | 1 |

All three faults fail by the named assertion; no setup errors or survivors.
The same four unmodified test methods pass in the positive control (exit 0).
Commands are documented in the Run18 README section. Logs and measured source
research are under `.temp/hybrid-e-r10c-261103/`; tools are Python standard
library, local Git and a2a. No new surface table was supplied (brief gap);
import portability, bf16 quality, unmeasured rate regions and chronological
rental reconstruction remain outside the measured contract. No push.

Self-review removed a permanent assertion that would have frozen future
R16b/PRI31 comparator data updates against the old input selection. Current
comparator byte identity is instead a task-specific evidence check. Engine01
was stopped by its recorded PID for this test refinement (SIGTERM, return -15);
it is not passing evidence. Numerical source remained unchanged. Engine02
uses the refined test identity. Kit01 passed all 24 tests, exit 0.

Current validation is recorded after the resource chronology below. Original
run10 green results do not stand in for rework validation.


R10c resource exception: engine02 was stopped by its recorded own PID2785325
at 2026-11-03T12:45:50.208315Z with 28042305536 B free; return was -15.
At its exit, 2026-11-03T12:45:50.417396Z, free space was 27994476544 B,
below the 28GB floor. The one-second observer missed this brief lower reading;
its higher minimum cannot supersede the exit observation. The rule was not
maintained. Task scratch was 253415 B in the preceding check. Writer is
unidentified; no foreign files or processes were removed/stopped. Evidence is
`resource-exception.json`, `disk-guard-engine02-stop.json` and the engine02 gate
record. Engine02 is incomplete, not passing evidence. A full retry waits for
at least 30GB headroom; recovery will not erase the breach.

The observer subsequently recorded 27867369472 B at
2026-11-03T12:46:20.733004Z and exited 1. This lower observation is the
current aggregate minimum. It is preserved in `disk-floor-failure-first.json`.
Monitoring resumes after recovery with the historical minimum retained; the
intervening observation gap is not described as continuous monitoring. The
new observer records every later breach and continues sampling instead of
losing subsequent observations. Its eventual normal stop is not a passing
resource-floor verdict.

Retry policy was revised after stable recovery to 29.5GB: task scratch is
below 300KB and the guard now intervenes at 29GB, a full 1GB above the floor
(rather than the earlier 28.3GB threshold). The initially proposed 30GB restart
target was precautionary, not a measurement requirement. `engine03-restart.json`
records the actual restart headroom; prior breaches remain failures.


## R10c validation and local handoff

Ready for review. Engine03 passes all 404 tests in 459.428s, exit 0, from
2026-11-03T12:51:06.673621Z to 12:58:48.668857Z. The captured calculator,
input and test identities remained unchanged throughout that run and the
artifact verification. All 391 previously declared test methods are retained;
five new methods bring the declared count to 396; discovery executes 404
cases. No source, input or test edits followed this pass.

| Gate | Actual exit | Rework evidence |
|---|---:|---|
| Engine 404 tests | 0 | engine-suite-03.log |
| Focused 26 tests | 0 | focused-03.log |
| Kit 24 tests | 0 | kit-suite-01.log |
| Original reviewer reproduction, both tests unchanged | 0 | reviewer-original-01.log |
| Export / immutable history / 2700 quote records | 0 | export-01.log; audit-01.log |
| Current runtime hashes, four unchanged CSVs, 180 exact corrections | 0 | final-artifact-01.log |
| Three narrowing faults | 1 each, intended assertions | mutant-mac-slope-01.log; mutant-allow-mac-01.log; mutant-intercept-01.log |
| Valid fault-driver control | 0 | controls-positive-01.log |
| Resource floor over the whole rework | 1, actual violation | resource-floor-01.log; resource-exception.json |

The successful retry interval sampled a minimum of 29533790208 B free.
Overall observed minimum remains 27867369472 B; the floor rule failed earlier.
The resource exception is disclosed rather than treated as a green gate.
No foreign cleanup/process control, downloads, native builds or push occurred.
Only the requested R18 implementation/tests, regenerated R18 artifacts,
quote ledger, documentation and root manifest enter the signed local change.
