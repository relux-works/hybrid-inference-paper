# Engine run16 — PRI31 anchors, depth import and state/link thresholds

Task `hybrid-e-r8-261103`; branch `engine-r16`, explicitly based on accepted `engine-r15` head `04755721`. Local signed delivery only, no push. Paper prose and all earlier exports remain unchanged. This is an engine result ready for review; the background-priority parallel sweep does not establish final agents/day capacity.

## Sources and custody

| Source | SHA-256 / qualification |
| --- | --- |
| data/measurements/run16-2026-11-03/m3/qwen27b-mac-bench-results-20261103T062853Z.tar.gz | c2e83fbd4f59a38181e48b17206783e91d6d5b6734624f46d4cede68d7bcace5; recorded PRI31, no override |
| data/measurements/run16-2026-11-03/m5/8d265ff6-qwen27b-mac-bench-results-20261102T174709Z.tar.gz | b17ef9d9304937bdc5e559dd28dd03c2ddd61393628c2ac192c8d4cb8acbb778; owner-reported normal priority, not recorded |

Both original archives were verified against the supplied abbreviated identity and their complete internal manifests, then safely extracted into `.temp/hybrid-e-r8-261103/extract/` (550,769 payload bytes total). Verification never trusts tar member paths for extraction. The exact source FACTS snapshot, four compressed route/timing extracts and `fca0fe31` policy source are retained in `data/measurements/run16-2026-11-03/`, with full hashes in `run16-measurements.json`. The policy source is read as AST data, not executed. The exact r44 driver `5be993f2` object was unavailable in two local stores; `fca0fe31` is the recorded prototype base. No fetch/download was attempted.

Historical background ancestry and throttling are the owner's A/B conclusion. Operator qualification explicitly limits that conclusion: no continuous historical server-priority proof, one paired run rather than a universal causal estimate. New server PRI31 samples are recorded even though older ancestors can still be PRI4. External-SSD save/restore timings are excluded.

## M3 single-stream anchors

| Nominal depth | Δ512 tok/s | Δ2000 tok/s | Δ10000 tok/s | Decode mean tok/s |
| --- | --- | --- | --- | --- |
| 16000 | 174.19 | 176.91 | 156.26 | 14.993 |
| 50000 | 121.72 | 116.15 | 106.68 | 13.520 |
| 100000 | 65.34 | 66.18 | 63.49 | 10.358 |
| 150000 | 46.24 | 47.07 | 44.37 | 8.993 |
| 200000 | 36.45 | 36.84 | 34.50 | 7.820 |
| 249000 | 28.68 | 29.68 | 27.79 | 6.928 |

At 100k, same-build background Δ512/decode 37.8/5.52 become 65.34/10.358 tok/s. The canonical kit 1.6.0 `c21284cd` prefill curve and old singleton parallel points are historical, measured at background priority and throttled. They remain discoverable in `historical_m3_prefill.csv` and `parallel_historical_sensitivity.csv`; they cannot serve the R16 canonical singleton path.

Prefill uses raw `prompt_n/prompt_seconds`, preserving framed2001/10001 prompts and actual sequential probe depths. Rates interpolate at the six nominal depth labels and between delta512/2000/10000; deltas outside that finite grid hold the endpoint rate. Decode is the arithmetic mean of the three raw `predicted_n/predicted_seconds` rates per nominal depth. This differs from the parallel sweep's `(n-1)` interval convention, which is retained. Cold ingest uses the new measured segment midpoints. Beyond 249k uses the labelled FLOP/depth law, not extra measurement. The architecture comparison now reads the PRI31 delta surface at its configured depth/portion instead of the old41.2 tok/s scalar. Other-model/device portability remains estimated.

## Interim M3 parallel and owner-reported M5 sweep

Every inherited mixed output table carries `background_priority_interim` and `capacity_status`; flags conservatively cover independent cells in those mixed tables too. Canonical PRI31 singleton anchor rows and independent new evidence tables retain their own qualification. All old multi-stream points, including 260k, remain interim. The two import variants are fully recomputed. These numbers are not final normal-priority agents/day results.

| Requested agents,1Gbit/s | Local groups/day | Prototype groups/day | Bounded-undo groups/day | Prototype/local gain | Qualified depth/count call share |
| --- | --- | --- | --- | --- | --- |
| 1 | 3.058 | 3.739 | 3.883 | 1.223 | 89.70% |
| 2 | 3.177 | 3.996 | 4.077 | 1.258 | 87.35% |
| 4 | 3.973 | 5.469 | 5.689 | 1.377 | 87.35% |
| 6 | 2.498 | 3.018 | 3.104 | 1.208 | 0.00% |
| 8 | 4.452 | 6.422 | 6.870 | 1.442 | 87.35% |
| 12 | 4.727 | 7.011 | 7.604 | 1.483 | 44.75% |
| 16 | 4.802 | 7.176 | 7.798 | 1.494 | 44.75% |

Groups normalize 116 calls; all 39,904 calls remain in the full-workload denominator. The six-agent row is measured only at 260k:0% of calls qualify as measured, with shallower calls held at its aggregate lower bound. Keep it flagged and exclude it from fitted agent-count trends. Measured-zone shares are finite depth/count coverage, not normal-priority qualification of the interim multi-stream observations.

The R16b interface is data-only: `m3_parallel.mode=verified_sweep`, new archive path/hash, `priority_basis=recorded_normal_priority_PRI31`, `background_priority_interim=false`, and data-defined depth/np/count grids. The existing loader requires recorded no-override PRI31 evidence, M3 device metadata,300 s cooling and all three restored rounds. Its notes and flags follow those data. A synthetic fixture exercises the contract without claiming that the pending real sweep has arrived. No source edits are needed for R16b; source-identical calculations naturally change where new data changes them.

| M5 depth | Server np | 1 stream | 2 | 4 | 8 | 12 | 16 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32784 | 16 | 22.62 | 31.89 | 47.78 | 62.32 | 62.78 | 65.54 |
| 65552 | 8 | 19.88 | 26.00 | 32.55 | 40.23 | — | — |
| 131088 | 4 | 15.73 | 18.35 | 20.69 | — | — | — |

These 13 aggregate rates are medians of all three valid rounds, using summed decoded intervals divided by the slowest completion interval. The128k np 4 repeat is 23.76 tok/s versus base 20.69: same configuration, run-to-run spread only. It does not replace the base. M5 Max64 uses these cooled decode anchors; same-SoC128 GB and Ultra portability remain labelled estimates. Existing M5 prefill measurements are retained. Larger counts/depths retain conservative lower-count lookup and explicit modelled/shallow zones; this does not invent new measured coverage.

## Depth-dependent prototype import

The supplied marginal fit is `1.498 s + 0.0000487 s*delta`, R² 0.12. The four fixed539-token probes independently fit `0.28530138 s + 0.000034644154 s*depth`, R² 0.99998449 over 2k–100k. The conditional model therefore is:

```text
I_prototype(delta,D) = 0.25905208 + 0.0000487*delta + 0.000034644154*D seconds
I_bounded_undo(delta) = 0.25905208 + 0.0000487*delta seconds
0.25905208 = 0.28530138 - 539*0.0000487
```

Keeping the marginal1.498 s intercept while adding the slope would overpredict every depth probe by1.239 s, counting depth already absorbed in that intercept twice. The token coefficient is retained as an assumption: four equal-delta points cannot identify it independently. Both the original fit and conditional fit remain visible in `import_depth_fit.csv`. Full save of the client's old slot as a recovery point explains the diagnosed depth dependence (dev-d r12); no mechanism is silently declared fixed.

| Prefix depth | Observed539-token import,s | Conditional prototype,s | Bounded undo,s | Original marginal fit,s |
| --- | --- | --- | --- | --- |
| 2000 | 0.360 | 0.355 | 0.285 | 1.524 |
| 20000 | 0.970 | 0.978 | 0.285 | 1.524 |
| 50000 | 2.020 | 2.018 | 0.285 | 1.524 |
| 100000 | 3.750 | 3.750 | 0.285 | 1.524 |

Bounded undo is an unimplemented sensitivity requiring transaction/lost-ack qualification. Depths140k/200k extrapolate beyond the100k probe envelope. Other Apple imports inherit this M3 law as an estimate. Missing conditioning depth, nonfinite/negative inputs and nonpositive fit slope refuse explicitly.

## State and downstream link thresholds

One ideal offload carries `B = state_bytes + 34816*delta`. f32 state is 157,000,000 B; bf16 is 78,500,000 B. Decimal MB/s is downstream payload goodput, with no additional efficiency discount. The B300 Q4 bulk-turn OLS supplies server time. RTT is 0.140589104 s. No catch-up, upload/framing overhead, final-token evaluation or queueing is hidden in these break-even numbers:

```text
local = delta / PRI31_rate(D,delta)
server = delta * (B300_a + B300_b*D)
R_equal = B / (local - server - I(delta,D) - RTT) bytes/s
```

A nonpositive denominator means no finite downstream rate can win; the gate rejects it. The table covers all 36 required cases. bf16 changes only recurrent transfer bytes and does not establish a qualified bridge or faster import.

| Depth | Delta | f32 prototype,MB/s | f32 bounded undo | bf16 prototype | bf16 bounded undo |
| --- | --- | --- | --- | --- | --- |
| 100000 | 512 | 49.304 | 24.938 | 27.165 | 13.741 |
| 100000 | 2343 | 8.046 | 7.204 | 5.399 | 4.834 |
| 100000 | 10000 | 3.476 | 3.395 | 2.936 | 2.868 |
| 140000 | 512 | 38.787 | 18.683 | 21.371 | 10.294 |
| 140000 | 2343 | 6.159 | 5.473 | 4.132 | 3.672 |
| 140000 | 10000 | 2.617 | 2.552 | 2.210 | 2.156 |
| 200000 | 512 | 28.292 | 13.337 | 15.589 | 7.349 |
| 200000 | 2343 | 4.419 | 3.916 | 2.965 | 2.628 |
| 200000 | 10000 | 1.857 | 1.811 | 1.568 | 1.529 |

At 100k/2343, f32 economic thresholds are 8.046 MB/s with depth and 7.204 MB/s without; bf16 gives5.399/4.834 MB/s. These use the new client surface and B300 estimate, not the old prototype policy's rates or entry margin.

| Preserved plan | Downstream,MB/s | Old local,s | Old offload,s | Recorded connected offloads | Equal-cost threshold,MB/s | Policy entry threshold,MB/s |
| --- | --- | --- | --- | --- | --- | --- |
| Wi-Fi | 5.186 | 42.659 | 57.155 | 0 | 7.0842 | 8.4497 |
| 5G | 9.753 | 42.659 | 31.839 | 2 | 7.0869 | 8.4535 |

The original policy has eta 0.85, margin 0.1 and hysteresis 0.05. After a local turn it requires `remote < 0.85*local`; entry is stricter than equal-cost break-even. Cancelling the two recorded plans' shared nontransfer cost, after removing their different RTTs, yields an effective wire numerator280,508,536 B and nontransfer cost2.93743197 s. Substituting the entry fraction recovers8.449743 MB/s on Wi-Fi, agreeing with FACTS' approximately8.45. The inferred numerator already includes policy goodput. It is not a second recurrent-state copy.

At the actual5.185832 MB/s Wi-Fi probe, the preserved policy offloads0 of 37 connected turns; the new PRI31 ideal economic replay also offloads0 with either import model. Over9.753010 MB/s 5G, the preserved policy has2 offloads; the ideal new economic replay has2 with depth and 7 without. This latter sensitivity excludes prototype eta/margins/catch-up, so it is not a reproduction of its routing implementation.

## 5G predicted versus measured calls

| Turn0=base | Import model | Predicted local prefill,s | Measured local TTFT,s | Ideal offload prediction,s | Measured-wire/catch-up prediction,s | Observed residual,s | Conditioned error,s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | prototype_depth | 891.6 | 884.0 | 418.1 | 418.4 | 483.3 | -64.9 |
| 0 | bounded_undo | 891.6 | 884.0 | 418.1 | 418.4 | 483.3 | -64.9 |
| 7 | prototype_depth | 36.4 | 33.7 | 30.0 | 33.2 | 43.1 | -9.8 |
| 7 | bounded_undo | 36.4 | 33.7 | 26.3 | 29.6 | 43.1 | -13.5 |
| 31 | prototype_depth | 44.2 | 38.9 | 31.2 | 35.0 | 35.3 | -0.3 |
| 31 | bounded_undo | 44.2 | 38.9 | 26.6 | 30.4 | 35.3 | -4.9 |

Depths/deltas are read from the preserved trace: turn 7 D104,507/2343; turn 31 D134,015/2343; base D0/99,999 prefill tokens plus the first generated token. The local predictor integrates PRI31 cold segments for the base. Remote server time uses the Run13 PRO6000 workstation bulk-fit as an explicit portability estimate for the measured Server Edition. No coefficient is fitted to these three held-out residuals.

Conditioned predictions use observed wire and catch-up, not their measured import/server/transfer timings. Ideal predictions retain one state plus delta KV. Turn wire238,500,055 B is within0.1 MB of ideal238,573,888 B because157 MB is rounded; base measured wire3,641,234,956 B includes ten staged chunks. Full component predictions and observations are retained in the CSV. The large base/turn 7 errors remain: link variability, chunk/import/protocol costs and unallocated synchronous overhead are not absorbed into a magic residual coefficient.

Capture removal is independently checked against the enclosing trace events: base 2896.763843−2413.468032=483.295812 s; turn 7 468.664485−425.589585=43.074901 s; turn 31 490.518778−455.201414=35.317364 s. Relative to local33.699844/38.870059 s, turn 7 is 9.375057 s slower and turn 31 is 3.552695 s faster. Base local883.968947 s divided by residual483.295812 s is 1.829x. These are arithmetic snapshot-download-subtracted residuals, not measured production TTFT or counterfactual speedups. Other instrumentation may remain. Checkpoint/numerical fidelity is unmeasured after the MTL/Metal guard failure.

## Exports, quotes and finite test evidence

The index binds 206 family files plus itself to the current generator and input configuration. Both import variants contain all eight paper/conservative families. Existing explicit alarms remain alarms, including memory/nonfit and pending legacy Mac-v2 diagnostics; they are not converted into zeros. The frozen audit compares every path and byte against accepted Git:150 historical +252 R13 +110 R14 +96 R15 =608 files, including sidecars and indexes.

The compact `ENGINE-QUOTES-R16-261103.csv` retains one coordinate-qualified row per changed cell, with every consumer site in one field, plus handwritten prose and the same-build priority A/B quotes. Actual counts: 218,194 rows covering218,146 changed cells,18 prose records and 30 same-build A/B records. Historical/expired anchor rows keep their original `r15:<index>` namespace. Deleting one record or forging its coordinates fails the coverage gate even when another cell has the same value. Metadata additions and both import variants are included; the paper itself is not rewritten.

The brief supplies no surface table or separately named landing-property suite; this is a declared brief gap, not an exemption. No requested row is out of contract. All 354 prior statically named engine/kit tests remain;21 new tests cover the new rules. The supplied regression gates are the full engine and kit suites. Self-review covers the source diff, data admission, source/byte custody, both economic branches, all 36 link cases, instrumentation subtraction and qualification metadata. Independent review is pending.

Named negative witnesses are in `calc/tests/test_run16.py`; executable fixtures cover bad priority/override, incomplete or reread grids, wrong device/np/cooling, control substitution, stale/background singleton rates, missing depth, doubled intercept, invalid budgets/state, capture accounting, omitted qualifier, stale generator, changed history and missing/forged quote coordinates. Adjacent positive controls remain executable. The data-only future-sweep control is synthetic and has no evidentiary status as a Mac measurement.

Nine process-local faults changed no source or export files. The unchanged calculation control passed 18 tests (`focused-calculation-08`, exit0). Every fault below reached a named assertion and exited1; none failed setup or survived. Driver `fault-controls-03` exited0 only after checking those real failures. This is finite narrowing evidence, not exhaustive mutation coverage.

| Mutant | Narrows the gate to | Named failing test | Actual exit | Surviving bound |
| --- | --- | --- | --- | --- |
| priority | Recorded PRI31/no-override admission | test_priority_gate_rejects_background_override_and_unrecorded | 1 | None; killed |
| flat_delta | Measured512/2000/10000 surface, not one bulk scalar | test_pri31_grid_rejects_background_single_rates | 1 | None; killed |
| lost_depth | Prefix depth contributes to prototype import | test_import_depth_rule_rejects_omitted_or_double_counted_term | 1 | None; killed |
| double_intercept | Conditional intercept, not marginal depth cost twice | test_import_depth_rule_rejects_omitted_or_double_counted_term | 1 | None; killed |
| half_wire | Full state+delta bytes and decimal bytes/s | test_threshold_rejects_state_omission_bits_and_import_omission | 1 | None; killed |
| m5_control | Base median rather than faster np 4 repeat | test_m5_cooled_sweep_rejects_wrong_np_mean_and_control_substitution | 1 | None; killed |
| final_interim | Background multi-stream outputs remain interim | test_parallel_interim_cannot_become_a_final_anchor | 1 | None; killed |
| raw_ttft | Capture-subtracted residual rather than instrumented TTFT | test_growing_validation_rejects_instrumented_ttft_as_residual | 1 | None; killed |
| entry_margin | Policy entry saving differs from equal-cost break-even | test_preflight_check_rejects_confusing_entry_and_break_even | 1 | None; killed |

Fault logs: `.temp/hybrid-e-r8-261103/fault-<mutant>-02.log`; definitions `fault_probe.py`; actual outcomes `fault-results-02.json`. Bounded byte/qualifier/coordinate plants also calibrate the real artifact checkers in the focused suite, without modifying real artifacts.

## Validation and resource record

Full engine:360 tests in523.606 s, exit0. Kit:24 tests in19.847 s, exit0. Final R16 focused suite:21 tests in12.641 s, exit0; it includes the bounded fixture-only corrections after the full run.

| Gate | Exact standalone command | Actual exit | Completion UTC |
| --- | --- | --- | --- |
| focused-calculation-08 | `python3 -B -I -m unittest discover -s calc/tests -p test_run16.py -k Run16Anchors -k Run16ImportAndLink -v` | 0 | 2026-11-03T06:57:56.252638+00:00 |
| kit-suite-01 | `python3 -B -I -m unittest discover -s bench/tests -v` | 0 | 2026-11-03T06:46:00.507031+00:00 |
| historical-r15-01 | `python3 -B -I -m unittest discover -s calc/tests -p test_run15.py -v` | 0 | 2026-11-03T06:45:46.872925+00:00 |
| audit-03 | `python3 -B -I calc/tests/r16_audit.py --audit-only` | 0 | 2026-11-03T07:24:19.583825+00:00 |
| focused-final-02 | `python3 -B -I -m unittest discover -s calc/tests -p test_run16.py -v` | 0 | 2026-11-03T07:23:19.184774+00:00 |
| engine-suite-04 | `python3 -B -I -m unittest discover -s calc/tests -v` | 0 | 2026-11-03T07:21:21.520999+00:00 |
| source-after-01 | `python3 -B -I .temp/hybrid-e-r8-261103/source_custody.py after` | 0 | 2026-11-03T07:27:11.157123+00:00 |
| delivery-verify-01 | `python3 -B -I .temp/hybrid-e-r8-261103/delivery_verify.py` | 0 | 2026-11-03T07:27:16.586412+00:00 |

All Python gates set `PYTHONDONTWRITEBYTECODE=1`, use `-B` (including isolated mode) and on-disk `TMPDIR=$PWD/.temp/hybrid-e-r8-261103/tmp`. 3.14.4 on Linux x86_64, standard library only. Each command runs as its own subprocess, with no tee/pipe hiding its return status; logs/PIDs/exit timestamps are task-local. Engine/kit execution is CPU only; no downloads, native builds, models or GPUs.

Earlier diagnostic failures are retained honestly. `smoke-01` exited1 because the loader initially required contiguous fill segments; the real kit inserts12896 probe tokens between fills. It now verifies those actual boundaries. `focused-import-01` exited1 because a test incorrectly assumed rounded157 MB payload must be smaller than the exact turn wire. `focused-calculation-03` had a test-label API error. `focused-anchors-import-05` selected artifact tests before exports existed and also used too-tight0.007 s OLS residual tolerance; the actual maximum residual is 0.008185 s, now bounded at 0.01 s. `focused-calculation-06` retained that residual assertion failure; `07` and`08` passed 18 calculation tests. No failed check is reported green.

Exports01–04 and full-engine01–02 were explicitly stopped by their recorded child PIDs (actual return−15/SIGTERM, shell equivalent143) as self-review corrected the architecture anchor, conditional import intercept and policy entry semantics. `export-05` generated all 16 families but exited1 in quote generation because its already-loaded auditor assumed the historical table could not grow. Current `r16_audit.py` keeps all 20 prior historical rows and four newly historical singleton rows. `audit-01` then exited0 on every generated byte. The ledger was compacted without losing any changed-cell or site coverage; audit02 passed and final audit03 independently rechecked it. The retired-shape witness failed as expected before the bounded auditor correction (future-shape-before-01 exit1), then passed after it (future-shape-after-01 exit0). Full engine03 exited1:358/360 tests passed, while two artifact tests reached the not-yet-written quote/index files. The corrected final full suite runs only after the artifact gate is green. ResourceWarning from a test's unclosed CSV handle was removed using an in-memory reader. Calculator source/input identity has not changed since final export05; only the auditor/test plumbing changed afterward. Full engine04 then passed 360 tests. After that pass, three R16 test bodies were made independent of the default interim fixture and the auditor was taught to retain a retired shape-control row for R16b. Calculator/input and all other source/test identities are unchanged (246 files; validation-fixture-delta.json). The final21-test R16 suite and audit were rerun on that bounded fixture-only delta, including an expected-red then green retired-row witness. Exact current export/index/quote bytes remain unchanged. Unaffected full-suite/kit evidence is reused rather than replaying the same calculations.

Sampled minimum free disk so far: **32113344512 B (32.113 GB)**, floor28,000,000,000 B. Continuous one-second samples and timestamps are in `disk-samples.jsonl`; `disk-summary.json` is the actual observation ledger. The watcher stays active through signed local delivery. No foreign files/processes were cleaned or stopped. Post-commit delivery/signature/A2A receipt is recorded in the task log and `.temp/` delivery evidence. No push or hosted landing is authorized.

Ready for review. PRI31 parallel remeasurement, bounded-undo/bf16 qualification and production/fidelity validation remain explicit limits; see `UNRESOLVED_QUESTIONS.md`.
