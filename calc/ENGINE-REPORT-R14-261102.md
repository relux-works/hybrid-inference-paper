# Engine run 14: measured parallel anchors, M5 family and B300

Task `hybrid-e-r4-261102`; branch `engine-r14`, based on the explicitly
requested `49a1c1d38233f8edbbc1150c3e28dd69adb72997`. R13 Muse re-review remains
an orchestrator-owned prerequisite; no acceptance is inferred here. CPU only,
no downloads, GPU execution or native builds. All archive consumers and final
validation entry points run under `python3 -I`, with
`PYTHONDONTWRITEBYTECODE=1` and disk-backed
`TMPDIR=.temp/hybrid-e-r4-261102/tmp`. The signed core commit is `bced3b31`.
Local signed commits only; no push, hosted checks, review acceptance or landing
is claimed. Delivery state: **ready for review**.

## Input custody and method

All four owner-supplied archives were checked against their full SHA-256 pins
before any read. Every payload also passed its internal manifest size/hash and
member-safety checks. Each was extracted into its own new task-scratch
directory; the data were never executed. The three new archives are retained
unmodified under `data/measurements/run14-2026-11-02/`; M5 reuses its existing
archive. `calc/hybridcalc/data/run14-measurements.json` pins paths and hashes.
Export sources record archive and payload-member hashes. All four scratch
extracts were removed, preserving original inputs and logs.

M3 anchors contain the frozen 32k single/four interval observations plus the
64k sweep, restored 128k control, twelve-stream post-prefill lower bound,
260k and 1.04M observations. Aggregate sweep throughput is recomputed from
`sum(predicted_n - 1) / max(predicted_ms / 1000)`, matching the timed decode
interval convention. Anchor depth is actual depth including the 16-token
suffix. The 1.04M point records YaRN scale4 explicitly; no model-quality
qualification is implied. Step 57's realistic-agent observations remain in the
verified archive as a cross-check, never a substitute for pure decode anchors.

Lookup interpolates in depth only within an identical measured count. Below
the first depth it keeps that count's first rate and marks it conservative.
Above the last depth it raises `InputGap`; missing counts also raise
`InputGap`, including interior holes such as three. No monotonicity correction
hides the 260k slowdown. Memory admission still occurs per call after output
growth, through the existing `end_memory` contract. Every requested row is
retained; gap capacities/latencies are `nan` with `status=alarm` and an explicit
reason, never an invented zero or a numeric estimate.

## client_agents_day: full supported-memory workload

39904 seeded calls,116 calls per normalized session, eight-hour day. Agent
seconds include prefill wait, per-stream decode and tool time. Device and
agent-cycle bounds use the existing engine equations; the larger seconds/call
is binding. Admitted streams are a per-call range, not a global cap.

| Mbit/s | Agents | Local sessions/day | Hybrid sessions/day | Gain | Local bound | Hybrid bound | Local agent s/call | Hybrid agent s/call | Admitted streams | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1 | 2.324 | 3.037 | 1.307 | agent cycle | agent cycle | 106.818 | 81.756 | 1..1 | ok |
| 1000 | 2 | 3.071 | 4.444 | 1.447 | device | agent cycle | 136.788 | 111.725 | 2..2 | ok |
| 1000 | 4 | gap | gap | gap | gap | gap | gap | gap | 2..4 | alarm |
| 1000 | 6 | gap | gap | gap | gap | gap | gap | gap | 2..6 | alarm |
| 1000 | 8 | gap | gap | gap | gap | gap | gap | gap | 2..8 | alarm |
| 1000 | 12 | gap | gap | gap | gap | gap | gap | gap | 2..12 | alarm |
| 1000 | 16 | gap | gap | gap | gap | gap | gap | gap | 2..16 | alarm |
| 300 | 1 | 2.324 | 2.949 | 1.269 | agent cycle | agent cycle | 106.818 | 84.184 | 1..1 | ok |
| 300 | 2 | 3.071 | 4.350 | 1.416 | device | agent cycle | 136.788 | 114.154 | 2..2 | ok |
| 300 | 4 | gap | gap | gap | gap | gap | gap | gap | 2..4 | alarm |
| 300 | 6 | gap | gap | gap | gap | gap | gap | gap | 2..6 | alarm |
| 300 | 8 | gap | gap | gap | gap | gap | gap | gap | 2..8 | alarm |
| 300 | 12 | gap | gap | gap | gap | gap | gap | gap | 2..12 | alarm |
| 300 | 16 | gap | gap | gap | gap | gap | gap | gap | 2..16 | alarm |

The full mix reaches1,000,557.676 tokens before decode. At four requested
streams,831 calls admit three and 125 admit two;3723 calls exceed260016
tokens before decode. No three-stream anchor exists, and four/six/eight-stream
coverage stops at 260016. Twelve-stream coverage stops at 131088 and
sixteen at 65552. Larger requests can also admit unmeasured intermediate
counts. The CSV's `coverage` names the first encountered gap; this paragraph
records the additional finite coverage limits. All 1/2-agent requests fit the
measured depth envelope; shallow uses are conservatively flagged.

## Existing four-agent table: old and new

At 1 Gbit/s, using the full current profile in each run:

| Client | R13 local | R14 local | R13 hybrid | R14 hybrid | R13 gain | R14 gain |
| --- | --- | --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 3.371 | gap | 5.307 | gap | 1.574 | gap |
| M4 Max 128 GB (estimate) | 5.238 | 5.238 | 7.178 | 7.115 | 1.370 | 1.358 |
| M5 Max 64 GB | 5.614 | 5.614 | 7.221 | 7.141 | 1.286 | 1.272 |
| M5 Max 128 GB | 6.860 | 5.782 | 8.049 | 7.512 | 1.173 | 1.299 |
| M5 Ultra 96 GB | 13.415 | 11.220 | 15.307 | 14.070 | 1.141 | 1.254 |
| M5 Ultra 256 GB | 14.126 | 12.091 | 15.604 | 12.091 | 1.105 | 1 |
| Strix Halo 128 GB | 3.039 | 3.039 | 3.434 | 3.419 | 1.130 | 1.125 |
| DGX Spark 128 GB | 3.519 | 3.519 | 3.662 | 3.519 | 1.041 | 1 |

M3's32k rate is byte-for-byte the same numeric anchor. Four-stream rates at
profile depths change as follows (aggregate tok/s):

| Actual depth | R13 model | R14 measured/interpolated |
| --- | --- | --- |
| 32000 | 14.054 | 14.054 |
| 65552 | 13.293 | 13.893 |
| 131088 | 12.020 | 12.966 |
| 260016 | 10.115 | 7.026 |

Thus M3's existing day result cannot be retained as a currently supported
number: its old full-mix1 Gbit/s gain was an extrapolated model, whereas the
new strict lookup exposes the missing counts/depths. The old exports remain
unchanged. At 100/300/1000 Mbit/s all three new full-mix four-agent M3 rows are
gaps, rather than altered numeric claims. New B300 prefill also changes hybrid
routing and capacities for the remaining clients; the ledger records both
changed cells and numeric-to-gap transitions.

## M5 family and old sensitivity

M5 Max 128 uses exactly the measured Max 64 prefill/decode curves, including
18.29 tok/s single at 32k and 33.37 tok/s aggregate at four streams (gain
1.824494, displayed as1.82). Only memory admission differs. The existing
Max 64 consumer's bulk-turn marginal curve is preserved; the separate
`client_prefill_segments.csv` exposes the measured fill segments rather than
confusing segment rates with bulk-turn rates.

Ultra 96 uses compute112/60=1.866667 and bandwidth1228/614=2 relative to the
measured Max. Ultra 256 uses140/60=2.333333 and the same2x bandwidth. Prefill
keeps the engine's memory roofline; these Ultra rates are estimates. The
hardware-only `prefill_compute_scale` column still denotes compute/M3, not a
measured prefill speedup. Actual admitted curves are in `m5_family_rates.csv`.

`client_m5_m3_sensitivity.csv` retains the former M3-derived Max 128/Ultra curves
with an explicit sensitivity label and the same new B300/workload. Its local
rates/capacities reproduce the old client estimate; its hybrid results are
recomputed with the new server and are not claimed byte-identical to R13.
M5 retains R13's three-stream interpolation and deep extrapolation estimates;
strict M3 measurement bounds are not silently claimed as M5 coverage.

## Measured B300 and server-only options

B300 kit 1.6.5, llama.cpp `dde879bc`: twelve bulk observations give
`a=0.0005673505018699517 s/token`,
`b=2.1666191870109614e-9 s/token/depth-token`. The B300 compute envelope is
`Qwen FLOPs(depth)/(a+b*depth)`, with **no 4.466 peak multiplier**. Its
single-stream decode curve runs from 80.549 tok/s at 18641 to 35.631 tok/s at
251641. Owned Qwen B300 fleets consume this decode curve and its residency
time; they claim no unmeasured batching uplift. Linear prefill fit beyond
249k and FLOP-scaled decode beyond the final point remain estimates; GLM
portability remains an explicit compute-envelope estimate.

Fitted marginal rate comparison (tok/s), derived from the actual engine
consumers and the cold-fit coefficients exported with the FP8 options:

| Depth | PRO6000 Q4 measured fit | R13 B300 peak-scaled estimate | R14 B300 Q4 measured fit | B300 FP8 auto KV | B300 FP8 KV |
| --- | --- | --- | --- | --- | --- |
| 16000 | 3528.212 | 15757.199 | 1661.084 | 24030.978 | 24841.424 |
| 100000 | 1767.385 | 7893.242 | 1275.490 | 14667.344 | 18555.013 |
| 249000 | 937.477 | 4186.827 | 903.474 | 8672.938 | 12806.425 |


FP8 uses different weights/serving precision and remains a server-only rate.
The observed B300 llama.cpp bulk-fit residual is below 1.3%; the static
comparison labels inside the vLLM document are not used as measurements.

Step 70's `sweep-status.json` says **skipped**, because the pinned and comparison
builds are both `dde879bc4f954b809892fd0d660515f42536394a`. The archive supplies
no independent tuning observations. `b300_tuning.csv` retains this reason in
`tuning_status`, separate from the CSV exporter's generic row status. There is
no tuning speedup to report or apply.

`server-options-r14` exposes B300 in the same cold/cached form as the PRO6000
R13 controls. It includes FP8 weights with auto KV and FP8 KV, plus the
large-batch FP8 control. NVFP4 is not relabelled FP8. Cold fits are recomputed
from raw TTFT; useful cached rates are delta/TTFT, processed rates also count
the uncached prefix remainder. The observed block sizes are 784 and 1568
respectively. Each B300 record says:
**server-only rate; hybrid transfer through the vLLM bridge is in qualification**.
All have `server_only=1`, `client_bridge=0`; no hybrid table routes via vLLM.

## Why the day gain is modest, and where it is multiple

A day contains reading, generation and tool time. Hybrid offload shortens
reading; generation stays on the client. The engine must satisfy both the
amount of device work and the number of available agent cycles. Removing a
large part of reading therefore does not remove the same part of the day.

For M5 Max 128 at 1 Gbit/s, mean prefill wait falls from 11.468 s to 2.959 s, while
mean decode remains122.575 s per call. Device seconds/call fall from 42.941 to
32.029, and the hybrid agent-cycle bound is 33.052 s/call. Day gain is 1.299x.
Ultra 96 gives1.254x. Ultra 256's recomputed full-mix policy chooses no offload
with this measured llama.cpp B300 and migration/transfer budget, so its day
gain is 1.000x. A faster server-only vLLM result does not qualify the bridge.

More agents can keep the device busy and expose greater aggregate decode.
The following is the explicitly conditional <=65552-token subset:6132 calls,
1 Gbit/s, same call definition and eight-hour normalization. It is not a
forecast for the full workload:

| Agents | Local sessions/day | Hybrid sessions/day | Gain | Local bound | Hybrid bound | Hybrid agent s/call |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 3.146 | 3.553 | 1.129 | agent cycle | agent cycle | 69.869 |
| 2 | 4.631 | 5.528 | 1.194 | device | agent cycle | 89.818 |
| 4 | 5.255 | 6.695 | 1.274 | device | agent cycle | 148.328 |
| 6 | 5.077 | 6.491 | 1.278 | device | agent cycle | 229.513 |
| 8 | 5.708 | 7.616 | 1.334 | device | agent cycle | 260.801 |
| 12 | 5.223 | 6.822 | 1.306 | device | agent cycle | 436.714 |
| 16 | 8.291 | 13.238 | 1.597 | device | device | 298.947 |

The measured 64k aggregate continues from 15.613 tok/s at 8 streams to 27.162
at 16 and 31.926 at 24. This does not guarantee monotone gains elsewhere: the
restored 128k control is 13.348 at 6 streams and 12.670 at 8. In the bounded day
above, sixteen agents improve throughput but wait longer per call than four.
Twelve streams use the explicitly conservative post-prefill lower bound. The
full-mix table refuses an unsupported extrapolation to these agent counts.

Prefill wait itself can improve by multiples. These engine examples use the
measured B300 llama.cpp fit, M3 local curve and 1 Gbit/s with 0.9 goodput. They
include state/KV transfer, exclude decode/tool time and cold-tier reload, and
are not whole-call or whole-day speedups. Large deltas use the engine's
start-depth marginal approximation. First fill integrates local prefill in
512-token steps and the measured server fit from zero:

| Case | Start depth | New tokens | Local wait s | Hybrid wait s | Wait gain |
| --- | --- | --- | --- | --- | --- |
| per-call | 16000 | 2000 | 13.048 | 3.618 | 3.607 |
| per-call | 131072 | 2000 | 48.467 | 4.116 | 11.775 |
| per-call | 249000 | 2000 | 94.506 | 4.627 | 20.424 |
| large tool output | 131072 | 10000 | 242.334 | 13.403 | 18.081 |
| large tool output | 249000 | 10000 | 472.530 | 15.958 | 29.611 |
| first fill | 0 | 131072 | 1984.901 | 135.333 | 14.667 |
| first fill | 0 | 249000 | 6289.557 | 287.291 | 21.893 |

## Refusal tests and bounded fault controls

Each refusal test includes a nearby accepted measured input. Fault plants
operate in memory in a separate process; they never edit production files.
Every listed faulty gate produces an assertion failure in its named test,
with no setup error. No fault survives.

| Mutant | What it narrows the gate to | Named failing test | Result / survivor bound |
| --- | --- | --- | --- |
| deep-clamp | Clamps above the last measured depth | test_refuses_optimistic_depth_extrapolation | Killed; actual exit 1 expected red; no survivor |
| count-extrapolation | Uses a lower-count rate for an unmeasured count | test_refuses_stream_count_above_anchor_and_unmeasured_holes | Killed; actual exit 1 expected red; no survivor |
| unchecked-archive | Parses archives without the outer checksum | test_refuses_archive_checksum_mismatch | Killed; actual exit 1 expected red; no survivor |
| b300-fallback | Substitutes a cached rate when measured B300 input is missing | test_refuses_b300_option_without_measured_inputs | Killed; actual exit 1 expected red; no survivor |

Logs and real exit metadata are under `.temp/hybrid-e-r4-261102/`:
`mutant-*-01.log` and matching result JSON. These four commands really exited1
(expected red); they are not recorded as passing commands. The unchanged
consumer/test controls pass in the focused and full suites.

## Validation, preservation and limits

| Standalone command | Actual exit | Seconds | Log |
| --- | --- | --- | --- |
| python3 -I calc/tests/r14_audit.py | 0 | 109.765 | export-03.log |
| python3 -I -m unittest discover -s calc/tests -p test_run14.py -v | 0 | 0.839 | focused-tests-final.log |
| python3 -I -m unittest discover -s calc/tests -v | 0 | 589.835 | engine-suite-02.log |
| python3 -I -m unittest discover -s bench/tests -v | 0 | 20.701 | kit-suite-01.log |

engine-suite-02: **302 tests, exit 0**.

kit-suite-01: **24 tests, exit 0**.

focused-tests-final: **17 tests, exit 0**.

Every gate runs directly as its own process without tee/pipeline status masking.
`candidate-source-identity.json` freezes 234 engine/input/test/kit files before
the full suite; final verification checks they did not change. Prior reviewer
test names remain present. R13's existing manifest test keeps its original
name and checks the immutable 49a1c1d3 generator instead of requiring R14's
new generator to match old sidecars. R14 sidecars independently require the
current generator and every real output hash.

The final audit verifies 103 new files/nine manifests and all 150 historical and 252 R13 files byte for byte,
all new manifest/INDEX hashes, Python3.9 syntax, and reviewed diff whitespace.
`r14_audit.py` produces 29030 replacement rows with `paper_site`, `old`, `new`,
`paper_current` and source. The ledger compares R13 against R14; the
`paper_current` field distinguishes still-published values. Exact table
coordinates and TeX CSV consumers are included; tab:clients headlines are
explicit. Paper sources and previous quote ledgers remain unchanged. This
run does not claim the R13 reverse-prose guard has been extended to R14 prose
or that the paper has been updated. A later writer must apply the replacements
and review surrounding prose, including the M5 compute-ratio explanation.

No surface table or separate landing-property suite was supplied (brief gap,
not a coverage waiver). Requested contracts are mapped to named tests above;
no requested row is treated as out of contract. Step 70's lack of tuning data
is explicitly retained rather than filled with an assumption. Independent
review is still pending. All source changes stay in the calculation engine,
its data/tests and documentation; original paper/bench source is unchanged.

### Corrected diagnostics

The first full engine run exposed a legacy workload-inventory test that did
not exclude the new measurement-only scenario. Its original test name and
accounting assertions are preserved; the measurement-only exclusion now
includes R14. The recorded engine PID668259 was stopped (return-15), that
focused accounting suite passed, and full engine-suite-02 reran against the
updated 234-file identity. No engine or export source changed for this fix.
The first task1 export exited2 because `local_steps` was not exposed in the
client record; the existing node was exposed and the corrected export exited0.
That diagnostic invocation omitted `-I`; every subsequent export and all final
validation use isolated Python. A same-SoC equality test caught an avoidable
floating operation-order difference; precomputing the unit bandwidth factor
makes the two SoCs exactly equal. The first audit script exited1 because
isolated Python excludes sibling imports; its explicit test-module path was
added. An intermediate export was stopped by recorded PID664427 (actual
return-15) while completing the separate server-option consumer, never counted
as green. A draft README patch failed to match before writing and was corrected.
Logs preserve these attempts. Final export03 and all required suites run on
the unchanged candidate; no failed or partial attempt is promoted to passing.

### Resource custody

The one-second disk monitor sampled a minimum of **33884123136 bytes** through 2026-11-02T00:37:09.524141+00:00, above 28,000,000,000 bytes. This is sampled visibility, not continuous proof between samples. All four task extracts were removed; `extracts-cleaned.json` records their exact paths and byte counts. Final delivery records the last disk sample. No foreign process or file was stopped or removed.

## r5: depth law, measured import, symmetric fleets and held-out checks

Task `hybrid-e-r5-261102`, continuing the explicitly requested `785334ab` on
`engine-r14`. This section supersedes the R4 full-mix gaps and the affected
R4 capacities/costs. All changes are local; no push or session links.

### Rules and limits

Within each measured count, the original measured depth interpolation remains.
Beyond that count's deepest point, aggregate rate is the deepest observed
aggregate multiplied by `R13_rate(k, depth) / R13_rate(k, deepest)`. It is flagged
**modelled beyond measured depth**. A count hole uses the nearest lower measured
count's aggregate, preserving the actual admitted count when computing per-agent
speed. Counts above 24 always refuse. The bounded tables retain R4 measured-only
admission, including its existing shallow clamps and measured lower-bound flags;
they never invoke the new depth or count fallback.

Zone call shares use the complete supported-memory mix. Decode-time shares use
`generated_tokens / aggregate_tok_s`, the shared device's decode seconds. Flag
zones can overlap; the unflagged measured zone excludes all flags. No calls are
dropped to obtain the full-mix rows. Depth admission includes output growth.

### Full-mix client_agents_day

Eight hours, 39,904 calls, normalized to 116 calls/session. Agent seconds include
tool time. These are throughput estimates, not measured daily sessions.


| Mbit/s | Agents | Local/day | Hybrid/day | Gain | Local bound | Hybrid bound | Local s/call | Hybrid s/call | Streams |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1 | 2.324 | 2.995 | 1.289 | agent cycle | agent cycle | 106.818 | 82.890 | 1..1 |
| 1000 | 2 | 3.071 | 4.400 | 1.433 | device | agent cycle | 136.788 | 112.860 | 2..2 |
| 1000 | 4 | 3.212 | 4.867 | 1.515 | device | agent cycle | 222.919 | 198.991 | 2..4 |
| 1000 | 6 | 3.195 | 4.866 | 1.523 | device | device | 310.617 | 286.689 | 2..6 |
| 1000 | 8 | 3.211 | 4.902 | 1.527 | device | device | 389.487 | 365.559 | 2..8 |
| 1000 | 12 | 3.326 | 5.176 | 1.556 | device | device | 508.067 | 484.139 | 2..12 |
| 1000 | 16 | 3.933 | 6.811 | 1.732 | device | device | 434.275 | 410.347 | 2..16 |
| 300 | 1 | 2.324 | 2.911 | 1.252 | agent cycle | agent cycle | 106.818 | 85.292 | 1..1 |
| 300 | 2 | 3.071 | 4.308 | 1.403 | device | agent cycle | 136.788 | 115.261 | 2..2 |
| 300 | 4 | 3.212 | 4.810 | 1.497 | device | agent cycle | 222.919 | 201.392 | 2..4 |
| 300 | 6 | 3.195 | 4.805 | 1.504 | device | device | 310.617 | 289.090 | 2..6 |
| 300 | 8 | 3.211 | 4.840 | 1.508 | device | device | 389.487 | 367.961 | 2..8 |
| 300 | 12 | 3.326 | 5.107 | 1.535 | device | device | 508.067 | 486.540 | 2..12 |
| 300 | 16 | 3.933 | 6.692 | 1.702 | device | device | 434.275 | 412.748 | 2..16 |


Zone percentages (calls / shared decode device time):

| Mbit/s | Agents | Shallow % | Modelled depth % | Lower count % | Measured lower bound % |
| --- | --- | --- | --- | --- | --- |
| 1000 | 1 | 3.18 / 2.38 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| 1000 | 2 | 15.37 / 12.25 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| 1000 | 4 | 3.18 / 2.19 | 6.93 / 13.12 | 2.08 / 6.36 | 0.00 / 0.00 |
| 1000 | 6 | 48.08 / 37.11 | 6.93 / 13.43 | 3.32 / 8.84 | 0.00 / 0.00 |
| 1000 | 8 | 15.37 / 9.97 | 6.93 / 13.68 | 4.20 / 10.44 | 0.00 / 0.00 |
| 1000 | 12 | 48.08 / 38.09 | 44.97 / 46.25 | 10.11 / 20.31 | 38.04 / 31.78 |
| 1000 | 16 | 15.37 / 8.06 | 77.68 / 71.12 | 24.09 / 43.32 | 18.02 / 21.31 |
| 300 | 1 | 3.18 / 2.38 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| 300 | 2 | 15.37 / 12.25 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| 300 | 4 | 3.18 / 2.19 | 6.93 / 13.12 | 2.08 / 6.36 | 0.00 / 0.00 |
| 300 | 6 | 48.08 / 37.11 | 6.93 / 13.43 | 3.32 / 8.84 | 0.00 / 0.00 |
| 300 | 8 | 15.37 / 9.97 | 6.93 / 13.68 | 4.20 / 10.44 | 0.00 / 0.00 |
| 300 | 12 | 48.08 / 38.09 | 44.97 / 46.25 | 10.11 / 20.31 | 38.04 / 31.78 |
| 300 | 16 | 15.37 / 8.06 | 77.68 / 71.12 | 24.09 / 43.32 | 18.02 / 21.31 |


### Client import and its isolated effect

The measured M3 Max point is 39,504 tokens in 42.4 s before import-speed-v2:
1.073309 ms/token. One point cannot identify both intercept and slope; the
fixed term is explicitly assumed zero, not measured zero. Other Apple clients
and GLM reuse this token coefficient as an uncalibrated portability estimate.
Import is charged once to client device time and once to agent wait, before
routing. A formerly winning offload can now remain local.

PR9's preserved 27B CUDA JSONL is admitted by SHA-256. Across its 18 positive
imports, OLS gives **1.618657 s + 0.4953084 ms/token**. The CUDA model and each
raw call/prediction are separate from the Mac calibration; localhost transfer
is not a WAN measurement. The file is stored under
`data/measurements/run14-2026-11-02/pr9/`. Both fixed and per-token terms are
checked against the independent raw observations.

The Mac import-speed-v2 sensitivity is explicitly pending in
`client_import_sensitivity.csv`. CPU review/speedup does not fill that Mac gate.

The table below isolates import with the same R5 depth law and identical calls.
Every isolated cell is in `R14-R5-IMPORT-EFFECT-261102.csv`; it is not a mixed
R4-to-R5 attribution.


| tab:clients; 1 Gbit/s | Hybrid/day; no import | Hybrid/day; with import | Change |
| --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 4.894 | 4.867 | -0.027 |
| M4 Max 128 GB (estimate) | 7.115 | 7.058 | -0.057 |
| M5 Max 64 GB | 7.141 | 7.075 | -0.066 |
| M5 Max 128 GB | 7.512 | 7.447 | -0.064 |
| M5 Ultra 96 GB | 14.070 | 11.220 | -2.850 |
| M5 Ultra 256 GB | 12.091 | 12.091 | 0.000 |
| Strix Halo 128 GB | 3.419 | 3.406 | -0.013 |
| DGX Spark 128 GB | 3.519 | 3.519 | 0.000 |


Full-mix four-agent day attribution:

| Mbit/s | No import/day | With import/day | Change |
| --- | --- | --- | --- |
| 1000 | 4.894 | 4.867 | -0.027 |
| 300 | 4.836 | 4.810 | -0.026 |


tab:offload, R4 → R5 (same B300/server assumptions; import changes routing):

| State bits | Mbit/s | Offloaded share old % | New % | Saved s/all calls old | New |
| --- | --- | --- | --- | --- | --- |
| 32 | 100.0 | 26.96 | 25.94 | 18.024 | 16.982 |
| 32 | 300.0 | 41.84 | 40.97 | 22.950 | 21.838 |
| 32 | 1000.0 | 55.16 | 54.36 | 25.179 | 24.043 |
| 32 | 2500.0 | 60.69 | 59.84 | 25.840 | 24.699 |
| 16 | 100.0 | 35.54 | 34.51 | 20.158 | 19.066 |
| 16 | 300.0 | 49.78 | 48.79 | 24.002 | 22.872 |
| 16 | 1000.0 | 59.49 | 58.68 | 25.578 | 24.438 |
| 16 | 2500.0 | 63.16 | 62.32 | 26.017 | 24.874 |


### Same-configuration 5G first call

PRO 6000, M3 Max, fresh 39,504-token context, 110 ms RTT, 16.0 MB/s down,
9.78 MB/s up. Predict the old protocol: four recurrent-state copies, q8 KV
34,840 B/token, plus a token-ID upload estimate of 4 B/token. The measured wire
includes framing; model payload is not set equal to measured bytes. Server and
local prefill integrate their existing curves from zero. Import uses its
single calibration point, so agreement there is calibration, not independent
validation. No component is fitted to the total.


| Component | Predicted s | Measured s | Error s | Error % |
| --- | --- | --- | --- | --- |
| server_prefill | 11.695 | 10.600 | 1.095 | 10.33 |
| transfer | 125.370 | 123.200 | 2.170 | 1.76 |
| client_import | 42.400 | 42.400 | 0.000 | 0.00 |
| total | 179.465 | 201.700 | -22.235 | -11.02 |
| local | 289.388 | 271.500 | 17.888 | 6.59 |
| unallocated | 0.000 | 25.500 | -25.500 | -100.00 |


The three reported measured components sum to 176.2 s, leaving **25.5 s** of
the 201.7 s wall total unallocated. The table preserves that residual. The
actual local/hybrid gain is 271.5/201.7 = **1.346×**; it is not the large-turn
modelled speedup on a different link/server.

### Step 57: the model is optimistic

The held-out Mac archive is the verified `9b7019cd...3ac2` input, using each
call's `new`, `gen` and `depth_before`. The Mac prediction applies the existing
device/agent-cycle bounds to the full finite workload. It omits finite-batch
drain, scheduling, actual overlap and prefill/decode interference. The PRO 6000
column is the existing analytical batch of 32 prefill/decode resource bound, not a
server scheduler prediction; no parallel server measurement was substituted.
No Step 57 row is used to calibrate a rate.


| Device | Sessions | Calls | Predicted s | Measured s | Error s | Error % |
| --- | --- | --- | --- | --- | --- | --- |
| M3 Max | 1 | 4 | 372.476 | 405.100 | -32.624 | -8.05 |
| PRO 6000 | 1 | 4 | 12.210 | 84.300 | -72.090 | -85.52 |
| M3 Max | 2 | 8 | 319.287 | 408.800 | -89.513 | -21.90 |
| PRO 6000 | 2 | 8 | 12.909 | 68.600 | -55.691 | -81.18 |
| M3 Max | 4 | 16 | 1752.908 | 2775.500 | -1022.592 | -36.84 |
| PRO 6000 | 4 | 16 | 80.107 | 441.000 | -360.893 | -81.84 |
| M3 Max | 8 | 32 | 1941.429 | 2914.300 | -972.871 | -33.38 |
| PRO 6000 | 8 | 32 | 88.867 | 486.700 | -397.833 | -81.74 |


The Mac model underestimates elapsed time by about **8%, 22%, 37%, 33%** for
1/2/4/8 sessions. The analytical server bound is about **81–86% below** the
measured elapsed times and must not be quoted as a validated server latency
model. The larger Mac session-count errors also limit confidence in extrapolated
daily-capacity claims. Later cooled sweeps can extend the anchor table without
turning this held-out trace into a fit.

### Symmetric own-server comparison and changed conclusions

The primary closed-perimeter table now allows every hardware option at every
team size. Both architectures choose the cheapest admissible hardware/tier
under identical retention, retained-session count, 70% target load and prefill
latency requirements. The shared mean/p90 prefill limits are the local-M3
workload's mean/p90; queueing is excluded. This is an explicit modelled service
budget, not a measured queue guarantee. The max of client/turbo p90 bounds the
hybrid mixture's p90, rather than comparing a client-only tail with all calls.

Both architectures pay the same incremental retained-session pool. HBM retention
has no migration; RAM/NVMe all-server variants reload their prefix each call,
append new input/output KV and overwrite the endpoint state. Only active decode
residency is charged as GPU occupancy: tool-idle retention already has its
separate pool charge. This removes the former asymmetric free/held-storage
assumption. Every tested storage candidate, price, latency and selected tier is
in `symmetric_storage_candidates.csv` and its cautious-policy counterpart.

Other explicitly fixed-hardware/GLM reference tables keep their named scope;
the optimized architecture conclusions must use the symmetric perimeter table.

Every changed selected owned-fleet conclusion across all profiles, teams,
clients and purchase bases is enumerated in `R14-R5-CONCLUSIONS-261102.csv`
(with exact old/new hardware, storage, monthly price, waits and integer fleet).
The paper's M5 Max 64 already-owned rows change as follows; costs are
USD/person-month. R4 is the numerical predecessor, distinct from older
still-embedded paper text.


| Profile | Team | Own R4 | Own R5 | Hybrid R4 | Hybrid R5 | Cautious hybrid R4 | R5 | Hybrid tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| light | 50 | 43.44 | 33.53 | 26.52 | 24.38 | 33.75 | 33.88 | NVMe |
| light | 500 | 269.61 | 32.39 | 45.74 | 21.48 | 86.68 | 25.07 | NVMe |
| light | 5000 | 269.61 | 32.14 | 45.74 | 20.77 | 56.35 | 24.57 | NVMe |
| medium | 50 | 151.77 | 120.41 | 55.48 | 55.53 | 62.72 | 62.85 | RAM |
| medium | 500 | 1078.45 | 115.87 | 146.84 | 47.50 | 187.78 | 57.35 | RAM |
| medium | 5000 | 1075.08 | 114.35 | 146.84 | 47.25 | 160.82 | 56.59 | RAM |
| heavy | 50 | 455.32 | 358.70 | 366.17 | 287.23 | 373.41 | 297.66 | RAM |
| heavy | 500 | 3370.16 | 348.59 | 2404.85 | 277.69 | 2412.09 | 287.54 | RAM |
| heavy | 5000 | 3356.68 | 347.07 | 2394.74 | 277.69 | 2401.98 | 286.78 | RAM |


Changed prose conclusions at `paper/sections/07-economics.tex:234–246` and `:317–324`:


- medium: old published claim 2.9–3.9×; cautious 2.4–3.2×. New own/hybrid cost ratios at 50/500/5000 range **2.169–2.439×**, cautious **2.032–2.150×**. Exact per-team values are in the table/CSV; ratio below 1 means hybrid is dearer.

- light: old published claim 30–39% cheaper at 50/5000 but dearer at 500; cautious 4–22% cheaper at 50/5000. New own/hybrid cost ratios at 50/500/5000 range **1.375–1.547×**, cautious **1.205–1.425×**. Exact per-team values are in the table/CSV; ratio below 1 means hybrid is dearer.

- heavy: old published claim 6–26% cheaper; cautious 4–24%. New own/hybrid cost ratios at 50/500/5000 range **1.249–1.255×**, cautious **1.230–1.238×**. Exact per-team values are in the table/CSV; ratio below 1 means hybrid is dearer.


- The PRO 6000 “only through 100 people” and B300 “from 50” policy/caption is
  removed from the optimized comparison. The old 500-person light-load
  B300 discontinuity is no longer a policy-imposed conclusion. Hardware and
  storage selection now follow real modelled costs and common requirements.
- The “same RTX hardware outside the policy” counterfactual becomes an ordinary
  candidate. The 234-row conclusion ledger records all selected configurations,
  including route changes and former M3 gap rows; it does not hide them in a
  single headline range.
- tab:clients and tab:offload require the replacements listed above. All other
  changed numeric cells (including person/API comparisons, GLM and transcript
  estimates) and engine table coordinates are in the quote ledger. Existing
  paper sources are not edited by this engine task.

### Why the day gain is modest, and where it is multiple

Four agents do not make four independent GPUs. They share prefill, import and
decode time, and long contexts reduce how many streams fit. Hybrid removes
some prefill work, while decode still consumes most device time. Once device
time is the limiting bound, shorter individual waits do not turn into a
proportional day-capacity gain. The measured aggregate curve is also nearly
flat between four and eight streams at 128k and is not forced monotone: six
agents can have slightly lower modelled local capacity than four.

At 1Gbit/s four agents improve **3.212→4.867 sessions/day (1.515×)**; sixteen
improve **3.933→6.811 (1.732×)**. More agents can hide waits and sometimes use
higher measured aggregate rates, but memory and the shared device still bind.
The 16-agent full mix models beyond measured depth for 77.68% of calls and
71.12% of decode device time; count fallback covers 24.09% of calls and 43.32%
of decode time (overlapping flags). At four agents those depth shares are
6.93%/13.12%, and count fallback 2.08%/6.36%. These are not additional measurements. Agent latency improvements and day throughput are different
claims, and Step 57 shows that the steady-capacity model can be optimistic.

The multiple gain is in the individual deep prefill wait: modelled B300 at 1Gbit/s
for a 2k delta is **7.74× at 131k and 13.95× at 249k**; a 10k tool delta is **10.04×
and 17.70×**. Those examples now include import. They exclude decode/tool time
and are not the measured 5G first call, whose gain is 1.346×. The first-fill
modelled examples are 7.19× at 131k and 11.34× at 249k; deeper extrapolation is
labelled and does not establish model quality.

### New negative tests and fault controls

Every new rejection is paired with an accepted control in `test_run14_r5.py`:
anchored depth versus flat/re-anchored depth, lower count versus upper/above-max,
weighted zone shares versus count weighting, nonzero foreground import versus
free/nonwinning offload, baseline import versus ungated v2/invalid size, verified
CUDA bytes versus a wrong hash/Mac rate, complete clean Step 57 trace versus
rereads/missing calls, real reload versus free eviction/nonfit, and cheapest
admissible selection versus a cheap latency violation. Export tests verify
uncapped large-team choices, equal budgets and isolated-import invariants.

Fault controls mutate only process-local functions; candidate files and
measurement bytes are untouched. Each listed mutant actually exits 1 with its
named failing assertion; these are expected-red failures, not passing gates.


| Mutant | Narrows gate to | Named failing test | Survival bound |
| --- | --- | --- | --- |
| flat-depth | deepest same-count Run13 depth ratio | test_depth_law_rejects_32k_reanchor_and_flat_clamp | killed; no survivor |
| upper-count | lower measured aggregate, no count 25 | test_count_hole_rejects_upper_neighbor_and_above_max | killed; no survivor |
| zero-foreground | client import consumes device time | test_import_rejects_zero_device_time_and_nonwinning_offload | killed; no survivor |
| free-reload | cold full-server prefix read and append are charged | test_symmetric_reload_rejects_free_eviction_and_nonfit | killed; no survivor |
| ignore-latency | cost minimum only over admissible candidates | test_cheapest_admission_rejects_latency_violation | killed; no survivor |
| unchecked-cuda | recorded CUDA import bytes are hash bound | test_cuda_import_refuses_unverified_bytes_or_mac_rate | killed; no survivor |
| erase-reread | held-out trace rereads cannot be sanitized into evidence | test_step57_refuses_rereads_and_missing_calls | killed; no survivor |


The unchanged control exits 0. Scope is finite: these controls do not qualify a
GPU scheduler, Mac v2 speed, storage hardware rates or cross-backend equivalence.
No surface table/separate landing-property suite was supplied (brief gap); no
requested row is silently treated as out of contract. Prior test method names
remain present, with R4 refusal expectations updated to the explicit R5 rule.

### Exports, checks and delivery evidence

All 150 historical and 252 Run13 files remain byte-identical. Every changed/new
R4 output is listed by path and old/new SHA-256 in
`R14-R5-CHANGED-OUTPUTS-261102.csv`. The quote ledger retains R13→current mapping
and adds a separate `r14_r4_to_r14_r5` comparison for every changed existing
cell, including R4-only tables. New measured checks and storage candidates have
explicit schemas/manifests. No old export tree is regenerated.

CPU only, no downloads/native builds; disk TMPDIR and PYTHONDONTWRITEBYTECODE=1.
Logs, PIDs, command exits and source identity are in `.temp/hybrid-e-r5-261102/`.


| Standalone gate | Actual exit | Seconds | Log |
| --- | --- | --- | --- |
| export-final-01 | 0 | 261.681 | export-final-01.log |
| import-effect-01 | 0 | 18.274 | import-effect-01.log |
| focused-final-02 | 0 | 1.330 | focused-final-02.log |
| engine-suite-01 | 0 | 546.071 | engine-suite-01.log |
| kit-suite-01 | 0 | 21.729 | kit-suite-01.log |


Corrected diagnostics: the initial isolated `python -I -m hybridcalc` probe could not find the package; the corrected probes explicitly add calc to sys.path. A temporary indentation error and a wrong self/c reference were fixed before the final exports. One early nonfit test hit the context limit before the memory gate; admission now checks memory before compute integration. An obsolete slow smoke process was stopped by its recorded PID (actual signal exit, not success) after hoisting invariant input reads. These failed/superseded logs are retained.


Tasks 1–6 checkpoint: engine **314 tests, exit 0**; kit **24 tests, exit 0**;
focused **29 tests, exit 0**. Seven named mutants each fail with actual exit 1;
the unchanged control exits 0. Python 3.9 syntax passes for 77 source/test files.
The sampled disk minimum is 30.889 GB. No archive was extracted to disk.

The orchestrator's additional task 7 follows this validated checkpoint in the
same r5 section below.

### Task 7: break-even prefill price

Added by the orchestrator after the validated tasks 1–6 checkpoint `8840cc10`.
`breakeven_prefill_price.csv` has **192 rows** covering all eight tab:clients
classes, default/cautious storage,20%/50%/100% open shares, already-owned/extra
purchase budgets and cheapest/median API targets. The 100% case retains its
academic label in the parent paper scenarios. All non-open calls are a common
excluded cost, exactly as in the earlier economics.

For each row, `M = served_calls_day * workdays * mean(delta + output) / 1e6`.
Every client-served input/output token is eventually prefilled once, including
catch-up after local calls. Existing-prefix reload and migration are not new
prefill tokens. For target API bill A and fixed monthly cost F, the threshold
is `(A - F) / M` when F≤A. A negative price is forbidden. If F>A, the result is
**no break-even**, even with free prefill compute. Overflow uses the target API
in each comparison, so supplier-switch savings cannot masquerade as a hybrid
advantage. Routing and all non-prefill budgets are held fixed; this is a tariff
threshold for the current performance/routing case, not a new provider route.

The row separately reports storage, transfer/egress, client power, device,
front/service, migration and overflow costs. Storage price is an effective
blended USD/GB-month ceiling at zero prefill price. Its companion column solves
for active RAM while inactive NVMe stays at its modelled price. A negative
required price is reported as impossible, not as a negative tariff.

Strix/Spark previously had capacity-only single-client entries. Their power and
extra-device budgets reuse the existing two-node family's declared whole-device
budget per node: 150 W/240 W; Strix keeps its NIC allocation and neither device
receives a laptop credit. This is explicitly an estimate, not a new measurement.
Missing that source power refuses, rather than creating a free client.

Base 20%, already-owned clients, default storage (all prices USD/MToken
prefilled; storage columns USD/GB-month):


| Client | Cheapest API threshold | Median API threshold | Current blended storage | Storage ceiling vs cheapest at free prefill | Blocker |
| --- | --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | no break-even | 4.8485 | 0.1921 | no nonnegative storage price | non-storage floor exceeds API; largest component: transfer |
| M4 Max 128 GB (estimate) | no break-even | 4.9722 | 0.1921 | no nonnegative storage price | non-storage floor exceeds API; largest component: transfer |
| M5 Max 64 GB | no break-even | 4.9597 | 0.1921 | 0.001606 | storage at its current price |
| M5 Max 128 GB | no break-even | 5.0155 | 0.1921 | 0.004725 | storage at its current price |
| M5 Ultra 96 GB | 0.1165 | 5.4006 | 0.1921 | 0.273286 | none at zero prefill price |
| M5 Ultra 256 GB | 0.1165 | 5.4006 | 0.1921 | 0.273286 | none at zero prefill price |
| Strix Halo 128 GB | no break-even | 4.7386 | 0.1921 | no nonnegative storage price | non-storage floor exceeds API; largest component: service_front |
| DGX Spark 128 GB | no break-even | 4.9752 | 0.1921 | 0.016215 | storage at its current price |


For the base 20% already-owned case, M3/M4 and Strix already exceed the cheapest
API through their non-storage floor even at zero prefill/storage price. M5 Max
and Spark need sharply lower blended storage prices; their ceilings lie below
the current inactive-NVMe floor of about **$0.077/GB-month**, so lowering active
RAM alone cannot close the gap. The Ultras admit about **$0.116/MToken** for
prefill against the cheapest API, below every compared measured-fit server
cost. The median-API thresholds are about **$4.74–$5.40/MToken**. Thus faster or
cheaper prefill alone does not make the hybrid beat the cheapest API in this
base case; storage, paid egress and the other fixed budgets matter independently.
All other policies, shares and purchase cases are retained in the 192-row table,
including explicit no-break-even cases against the median API.

Every threshold has these four server-cost columns beside it, weighted by that
client's delta/output tokens and depth. For the M3 full mix:


| Option/basis | Engine rental USD/GPU-hour | USD/MToken prefilled at 70% load | Token share beyond measured depth % |
| --- | --- | --- | --- |
| llama.cpp PRO 6000; measured run13 base | 2.20 | 0.6310 | 8.10 |
| vLLM FP8 PRO 6000; measured; server-only | 2.20 | 0.2627 | 8.10 |
| vLLM FP8 B300 auto KV; measured; server-only | 9.50 | 0.3127 | 8.10 |
| vLLM FP8 B300 FP8 KV; measured; server-only | 9.50 | 0.2318 | 8.10 |


The llama.cpp price uses the Run13-base bulk marginal fit. vLLM prices use
measured cold marginal fits (not a cache-hit price or a single favourable
delta), with each table's rental tariff: PRO 6000 $2.20/GPU-hour, B300 $9.50/GPU-hour,
all at 70% target load. Beyond-measured-depth token shares are explicit; those
parts are estimated. Server-only costs do not qualify a vLLM client bridge or
claim its latency/transfer equivalence to the current hybrid route. Client
purchase/power and storage assumptions retain their existing estimate status.

Named positive/negative tests in `test_prefill_price_r14.py` establish exact
parity and opposite cost ordering around the root, the valid zero boundary,
no nonnegative root/storage price, fixed inactive-NVMe floors, delta/output
catch-up once without charging prefix, negative price/component refusal,
missing option and missing power refusal, plus all192 row reconciliations.
The initial export correctly exposed missing single-client Strix power; the
final implementation explicitly reuses the already-declared physical-node
budget. Two superseded in-flight exports were stopped by their own recorded
PIDs; their signal exits are retained, never called green evidence.


| Task 7 mutant | Narrows gate to | Named failing test | Survival bound |
| --- | --- | --- | --- |
| negative-price | nonnegative provider prices | test_price_parity_and_negative_price_refusal | killed; no survivor |
| missing-option | only admitted measured server options | test_measured_option_missing_and_negative_rental_refuse | killed; no survivor |
| zero-price-floor | no invented root when fixed costs already exceed API | test_zero_price_floor_and_storage_counterfactual | killed; no survivor |
| double-catchup | each generated token shadowed once; no duplicated compute charge | test_prefilled_volume_rejects_prefix_and_duplicate_output_charge | killed; no survivor |


All eleven final-candidate faults (seven original plus four pricing faults)
are expected-red actual exit1 with named assertions; the unchanged control
exits 0. CPU-only/no downloads/native builds and the disk floor continue to
apply. All 150 historical and 252 Run13 exports remain frozen. Task 7 adds one
CSV; every tasks 1–6 CSV is checked byte-identical to checkpoint 8840cc10. The
updated generator manifests/INDEX, sources, correction inventory and report
bind the final candidate. No paper source or benchmark implementation changed.


| Final gate | Actual exit | Seconds | Log |
| --- | --- | --- | --- |
| export-task7-final-02 | 0 | 272.537 | export-task7-final-02.log |
| price-focused-final-02 | 0 | 0.135 | price-focused-final-02.log |
| focused-final-03 | 0 | 0.952 | focused-final-03.log |
| engine-suite-02 | 0 | 476.175 | engine-suite-02.log |
| kit-suite-01 | 0 | 21.729 | kit-suite-01.log |


The 24-test kit evidence is reused from the tasks 1–6 checkpoint because every
tracked `bench/` byte and all tool/environment identities are unchanged; task7
changes only calculation/report code. The full engine suite is rerun for the
new calculation source identity. Final custody checks and signed local delivery
are recorded after that suite; independent acceptance remains the orchestrator's
review gate, with no push/tag requested.

Final r5 evidence: engine **321 tests, exit 0**; correction focus **29 tests,
exit 0**; pricing focus **7 tests, exit 0**; unchanged kit **24 tests, exit 0**.
All eleven final-candidate fault controls have actual exit 1 with named failing
assertions; the unchanged control has actual exit 0. The read-only custody gate
exits 0: **150 historical + 252 Run13 files frozen, 72 tasks1–6 CSVs unchanged,
110 Run14 files, 71 changed/new R4 exports, 89,163 quote rows**, and all nine
manifests/INDEX hashes match the current source. Python 3.9 syntax passes for
79 files; 186 source/input/test identities remain unchanged from final gating.
The sampled minimum free disk is **30.889 GB**. No archive extracts were created.

A trailing report blank line made the first whitespace gate exit 2; trimming
it produced exit 0. Pre-existing ResourceWarnings in the paper checker remain
in the complete passing engine log. No native build, download, push or tag was
performed. Import-speed-v2 still lacks a Mac gate/rate; the pending sensitivity
is retained. Independent acceptance remains open; this signed local result is
ready for review.
