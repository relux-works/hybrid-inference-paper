# Engine run15: cooled kit1.6.6 parallel anchors

Task `hybrid-e-r6-261102`, branch `engine-r15`, exact owner-specified base `2d457aed87d415043a2c0566f7a185607f11487e` (R14 accepted by r5i per brief). Local signed delivery only, with the requested Codex coauthor; no push, PR, hosted review or landing is authorized. Status: ready for review. Paper prose and embedded paper data remain unchanged; this report and the quote ledger are the writer handoff.

## Measurement custody and admission

Archive `data/measurements/run15-2026-11-02/qwen27-kit166-scaling.tar.gz` has SHA-256 `916891bdcf32112bdba069140ef86eb35bf4fbaec8b1f342b2ffd2baa637d618`. The full digest, safe tar members and every internal manifest size/hash passed before extraction. All32 manifest-backed payloads were extracted under `.temp/hybrid-e-r6-261102/extracted/` for inspection; raw archive bytes are retained in the repository. No payload was executed. Every raw round remains in the archive and every three-round rate vector and payload SHA-256 is exported in `parallel_anchors.csv`; export sources also identify every archive payload.

Protocol: one fill per depth,300s pause, restore before every round; no rereads. Kit1.6.6, Qwen3.8-27B Q4_K_M, q8_0 KV, FA on, llama.cpp `dde879bc4f954b809892fd0d660515f42536394a`. The base uses the largest-np shape:32 slots at32k/64k,16 at128k. Each rate is the median of all three valid rounds recomputed as `sum(predicted_n - 1) / max(predicted_ms / 1000)`. No averaging, chosen round or summary-field substitution. The actual lookup depths include the16-token suffix:32784,65552,131088.

The owner FACTS block is retained in `data/measurements/run15-2026-11-02/PROTOCOL.md`. It labels approximately10:55–13:40Z; archive kit.log labels06:46–09:40Z, and JSONL filenames use10:46–13:38 labels. These source labels are preserved without silently reconciling their clock conventions. They are measurement labels, not this run’s verification timestamps.

| Actual decode depth | np | Streams | Median aggregate tok/s |
| --- | --- | --- | --- |
| 32784 | 32 | 1 / 2 / 4 / 8 / 12 / 16 / 24 / 32 | 8.770 / 14.658 / 24.030 / 33.395 / 38.465 / 44.410 / 43.502 / 47.829 |
| 65552 | 32 | 1 / 2 / 4 / 8 / 12 / 16 / 24 / 32 | 6.421 / 9.891 / 20.084 / 29.969 / 30.604 / 33.966 / 32.927 / 35.557 |
| 131088 | 16 | 1 / 2 / 4 / 8 / 12 / 16 | 5.378 / 9.371 / 14.351 / 18.934 / 19.767 / 20.218 |
| 260016 | 8 | 1 / 2 / 4 / 6 / 8 | 5.981 / 7.627 / 7.026 / 6.683 / 6.420 |

The five step56 points at260016 tokens (1/2/4/6/8 streams, np8, old build `c21284cd`) are kept exactly as the deepest base observations. The mixed build/shape at260k is explicit; this is not a new cooled/deeper measurement. Old step55 and restored128k-control points remain labelled historical sensitivities in `parallel_historical_sensitivity.csv`, together with the frozen32k interval points and1.04M YaRN observations. The1.04M points do not extend this base measured envelope. No monotonic smoothing removes the single-stream increase from128k to260k.

The server-shape sensitivity is separate: at128k/four streams, np4 gives16.026061 tok/s versus14.351284 at np16, a1.116699 ratio (+11.67%). All three control rounds are retained in the archive and `parallel_server_shape_sensitivity.csv`. The faster np4 observation never replaces the np16 base.

## Lookup and qualification

Rules are reused from R14 r5 without changing the Run13 depth law. Same-count measured anchors interpolate linearly within their depth interval; below the first anchor the first rate is held and flagged shallow. Beyond that count’s deepest point, rate is multiplied by the Run13 law ratio `law(k,depth)/law(k,last_depth)`. Holes use the nearest lower measured aggregate, divide by the actual admitted count, and flag count-conservative. Counts above32 refuse at every depth. Deepest depths are260016 for1/2/4/6/8,131088 for12/16,65552 for24/32. Measured-only subset exports still refuse depths beyond their envelope.

The only six-stream base observation is step56 at260k. Consequently shallow six-stream calls use that conservative6.683 tok/s anchor. The six-agent row drops instead of borrowing the now-historical128k control. This follows the unchanged lookup rule and must not be interpreted as a measured cooled six-stream regression.

## client_agents_day

Full supported-memory workload:39904 seeded calls,116 calls per normalized session, eight-hour day; memory admission includes output growth. All rows remain numeric estimates across their explicitly flagged zones. Sessions/day are local and hybrid throughput bounds, including tool time; both capacity bounds are still evaluated.

| Mbit/s | Agents | R14 local | R15 local | R14 hybrid | R15 hybrid | R14 gain | R15 gain | R15 local/hybrid bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1 | 2.324 | 2.062 | 2.995 | 2.573 | 1.289 | 1.248 | agent cycle / agent cycle |
| 1000 | 2 | 3.071 | 2.893 | 4.400 | 4.043 | 1.433 | 1.398 | device / agent cycle |
| 1000 | 4 | 3.212 | 3.538 | 4.867 | 5.657 | 1.515 | 1.599 | device / agent cycle |
| 1000 | 6† | 3.195 | 2.319 | 4.866 | 3.090 | 1.523 | 1.332 | device / device |
| 1000 | 8 | 3.211 | 3.914 | 4.902 | 6.755 | 1.527 | 1.726 | device / device |
| 1000 | 12 | 3.326 | 4.125 | 5.176 | 7.410 | 1.556 | 1.796 | device / device |
| 1000 | 16 | 3.933 | 4.181 | 6.811 | 7.594 | 1.732 | 1.816 | device / device |
| 300 | 1 | 2.324 | 2.062 | 2.911 | 2.511 | 1.252 | 1.218 | agent cycle / agent cycle |
| 300 | 2 | 3.071 | 2.893 | 4.308 | 3.966 | 1.403 | 1.371 | device / agent cycle |
| 300 | 4 | 3.212 | 3.538 | 4.810 | 5.579 | 1.497 | 1.577 | device / agent cycle |
| 300 | 6† | 3.195 | 2.319 | 4.805 | 3.065 | 1.504 | 1.321 | device / device |
| 300 | 8 | 3.211 | 3.914 | 4.840 | 6.638 | 1.508 | 1.696 | device / device |
| 300 | 12 | 3.326 | 4.125 | 5.107 | 7.269 | 1.535 | 1.762 | device / device |
| 300 | 16 | 3.933 | 4.181 | 6.692 | 7.446 | 1.702 | 1.781 | device / device |

† Six streams are measured only at 260k; shallower calls hold that 6.68 tok/s aggregate lower bound. **0% of calls are measured; 90.67% use the shallow-held rate.** Show this row with the same dagger/footnote in the paper, exclude it from fitted trends and agent-count capacity-gain ratios, and never drop it silently. If moved to a supplement, retain its flag and state the move in the main table note. The existing machine-readable `coverage` and share columns identify this gap; see the r7 addendum.

## tab:clients at1Gbit/s / four agents

| Client | R14 single32k | R15 single32k | R14 local | R15 local | R14 hybrid | R15 hybrid | R14 gain | R15 gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 8.441 | 8.770 | 3.212 | 3.538 | 4.867 | 5.657 | 1.515 | 1.599 |
| M4 Max 128 GB (estimate) | 11.522 | 11.522 | 5.238 | 5.238 | 7.058 | 7.058 | 1.347 | 1.347 |
| M5 Max 64 GB | 18.290 | 18.290 | 5.614 | 5.614 | 7.075 | 7.075 | 1.260 | 1.260 |
| M5 Max 128 GB | 18.290 | 18.290 | 5.782 | 5.782 | 7.447 | 7.447 | 1.288 | 1.288 |
| M5 Ultra 96 GB | 36.580 | 36.580 | 11.220 | 11.220 | 11.220 | 11.220 | 1.000 | 1.000 |
| M5 Ultra 256 GB | 36.580 | 36.580 | 12.091 | 12.091 | 12.091 | 12.091 | 1.000 | 1.000 |
| Strix Halo 128 GB | 5.402 | 5.402 | 3.039 | 3.039 | 3.406 | 3.406 | 1.121 | 1.121 |
| DGX Spark 128 GB | 5.761 | 5.761 | 3.519 | 3.519 | 3.519 | 3.519 | 1.000 | 1.000 |

M3 four-agent gain rises from1.515126 to1.598725 (+5.52% in the gain ratio; the hybrid advantage rises8.36 percentage points). Local sessions rise10.15%, hybrid16.23%. Single32k throughput is8.769772 tok/s; four-stream aggregate24.029933, per-stream6.007483. A512-token answer at that anchor takes85.227s, versus145.720s under the old14.054306 aggregate. Other tab:clients rows retain their R14 inputs and results. The theoretical bandwidth-bound diagnostic and R7 anchor_gain metadata also now consume cooled medians, preventing stale parallel metadata.

## How much of16 agents is measured?

Zone shares use all39904 calls and actual decode-device seconds `output/aggregate_rate`, not a mean of per-call shares. Flags overlap; do not sum their columns. "Measured" excludes shallow, depth-modelled and count-conservative calls; interpolation within a measured same-count interval qualifies. This is measurement-backed lookup, not an assertion that every call or the whole row was directly benchmarked. Shares are identical at300Mbit/s and1Gbit/s because decode/admission is independent of the link.

| Zone | R14 call share | R15 call share | R14 decode-time share | R15 decode-time share |
| --- | --- | --- | --- | --- |
| measured | 0.313% | 44.752% | 2.647% | 25.726% |
| shallow | 15.367% | 3.323% | 8.056% | 1.154% |
| depth_modelled | 77.681% | 47.369% | 71.117% | 63.882% |
| count_conservative | 24.093% | 24.093% | 43.325% | 39.729% |
| measured_lower_bound | 18.023% | 0.000% | 21.305% | 0.000% |

Exactly17858/39904 calls (44.7524%) now use the measured zone, versus125/39904 (0.3133%) in R14: +44.4392 percentage points. They account for25.7257% of decode device time, versus2.6468% before (the exact previous CSV is authoritative). The remaining55.2476% of calls are qualified by the other zones;47.3687% of all calls and63.8819% of decode time exceed their measured depth envelope. Count-conservative accounts for24.0928% of calls and39.7289% of decode time, overlapping the depth/shallow zones. Shallow is3.3230% of calls and1.1544% of decode time. At1Gbit/s the full row gives4.181433 local /7.593812 hybrid sessions/day, gain1.816079; at300Mbit/s,4.181433 /7.446306, gain1.780802. Neither is a fully measured day.

## Exports and paper quotes

`calc/out/run15/` contains96 files:95 generated family files plus `INDEX.json`. Eight default/cautious paper families were recomputed, including client counts, person costs, traffic, perimeter and storage candidate choices, one-shot/turn/transcript times, break-even prices and held-out step57 checks. Server-only measurements have no new parallel dependency and are reused from the preserved R14 inputs. Existing explicit nonfit/unsupported-rate alarms remain alarms, not zero. Bounded agent subsets retain their measured-only refusals.

`calc/ENGINE-QUOTES-R15-261102.csv` contains8804 rows covering all8301 changed cells in tables with Run14 counterparts, with old=accepted R14 and new=R15, plus named printed-table and handwritten prose sites. Printed paper values are separately recorded because the embedded paper still predates R14. Derived traffic compute+hosting denominators and egress ratios, tab:econ M3 cells, and the manual number-word "about four M3 Max" are explicit. Every changed cell in those counterpart tables is included even if its printed rounding does not change. The two new sensitivity tables have no Run14 counterpart and are documented separately above. No existing paper source or export is silently replaced.

All512 prior export files are byte-identical:150 historical `calc/out/paper`,252 R13,110 R14, including sidecars and indexes. The audit refuses missing/new historical files as well as byte changes. New manifests pin source generator/input identities and each output digest; `--audit-only` verifies those identities before producing a ledger/index and cannot bless stale tables.

## Validation and finite limits

The final engine/kit commands, actual exit codes, resource observations and extract cleanup are recorded in the validation addendum below. No surface table or separately named landing-property suite was supplied in the brief (declared brief gap); engine regression tests and all existing reviewer tests are retained. No requested row is out of contract. No tests/builds requiring network, model weights, GPU, PDF downloads or native compilation were run.

New named negative/positive witnesses:

- `test_medians_reject_mean_or_single_round_replacement`
- `test_incomplete_or_invalid_rounds_refuse_partial_median`
- `test_reread_unrestored_or_wrong_np_refuses_base_admission`
- `test_np4_control_refuses_faster_base_substitution`
- `test_historical_step55_control_and_yarn_refuse_base_reentry`
- `test_step56_deepest_points_reject_replacement_or_smoothing`
- `test_lookup_rejects_flat_depth_or_wrong_deepest_anchor`
- `test_stream_count_extrapolation_and_upper_neighbor_refuse`
- `test_zone_shares_reject_dropped_calls_or_unweighted_decode`
- `test_16_agent_row_refuses_full_measurement_or_filtered_denominator`
- `test_wrong_archive_hash_refuses_before_admission`
- `test_frozen_history_and_new_export_hashes`
- `test_quote_ledger_rejects_missing_changed_cells`
- `test_diagnostic_tables_reject_stale_parallel_metadata`

The ledger gate is calibrated with a bounded deletion plant: removing all records for one changed coordinate must produce the intended `unreported changed cells` assertion, while the full ledger passes. Corrupt-round fixtures preserve the valid controls and reject incomplete, invalid, unrestored, reread or wrong-shape input. Test failures are never treated as passing controls.

Initial diagnostics: `focused-01` exited1: all10 anchor tests passed, but three artifact tests ran before exports existed and failed with FileNotFoundError. The corrected focused run exited0 (14 tests). `export-01` generated all eight families but exited1 in quote generation because its already-loaded selector compared `1000` with CSV `1000.0`; the selector was corrected. `audit-02` then exited0. Expanding prose coverage exposed a wrong purchase-basis label in `audit-03` (exit1, intended unique-row assertion); it was corrected to the actual `Mac premium bought`. `audit-04` exited0 after verifying every generated table and all512 frozen files. No export regeneration was needed: source/input generator identities were unchanged, and all export manifest hashes were rechecked.

The first full engine run (`engine-suite-01`) exited1:334/335 tests passed;
`test_run14_manifest_hashes_and_all402_frozen_files` still required the R14
manifest to equal the current generator. That is incompatible with this
run's explicit frozen-R14 requirement. Its original name, nine-manifest
coverage, all payload hashes, index hashes and402 older-file byte comparisons
are retained. It now independently hashes the accepted R14 source tree at
`2d457aed` using local Git and compares all R14 generator records with that
identity. It does not trust its own manifest as the expected source identity.
The corrected R14 focused suite passed17 tests, exit0. R15 continues to require
the *current* source identity in all new manifests. The full engine suite is
rerun after this test-only historical migration; no engine/input/export bytes
changed during the correction.

## Bounded fault controls

Process-local faults changed no source or output files. The unchanged control ran all14 R15 tests, exit0. Each fault below produced a named assertion failure, actual exit1, with no setup error. No mutant in this six-case experiment survived. This is finite fixture evidence, not exhaustive fault coverage. Logs: `.temp/hybrid-e-r6-261102/fault-*-01.log`; definitions: task-local `anchor_fault_probe.py`; outcomes: `fault-results-01.json`.

| Mutant | What it narrows the gate to | Named failing test | Actual exit | Surviving bound |
| --- | --- | --- | --- | --- |
| mean | Median of all three rounds, not an arithmetic mean | `test_medians_reject_mean_or_single_round_replacement` | 1 | None; killed |
| np4 | Largest-np base cannot select the faster np4 control | `test_np4_control_refuses_faster_base_substitution` | 1 | None; killed |
| yarn | Historical1.04M cannot extend the260k measured envelope | `test_historical_step55_control_and_yarn_refuse_base_reentry` | 1 | None; killed |
| flat | Beyond-depth throughput follows the anchored Run13 ratio | `test_lookup_rejects_flat_depth_or_wrong_deepest_anchor` | 1 | None; killed |
| count33 | Counts above32 are rejected | `test_stream_count_extrapolation_and_upper_neighbor_refuse` | 1 | None; killed |
| all_measured | Measured shares exclude unqualified calls | `test_zone_shares_reject_dropped_calls_or_unweighted_decode` | 1 | None; killed |

The export identity guard also passed a real95-file control and rejected a planted stale source identity with the intended `stale generator` assertion inside the bounded control (control process exit0). The quote deletion plant is exercised by the named ledger test.

## Capacity gain from adding agents

At1Gbit/s, ratios below compare the full-workload sessions/day at different requested agent counts. They are throughput ratios, separate from each row’s hybrid/local gain. Memory admission and the same qualified/modelled zones still apply. Six agents are excluded because their only anchor is the260k observation and no calls in that row qualify as measured; retain the flagged six-agent row in the table above, outside trend fitting and these capacity comparisons.

| Requested agents | R14 local ratio | R15 local ratio | R14 hybrid ratio | R15 hybrid ratio |
| --- | --- | --- | --- | --- |
| 1 to 4 | 1.3820 | 1.7159 | 1.6249 | 2.1980 |
| 1 to 8 | 1.3813 | 1.8980 | 1.6365 | 2.6249 |
| 1 to 16 | 1.6920 | 2.0278 | 2.2741 | 2.9508 |
| 4 to 16 | 1.2243 | 1.1818 | 1.3996 | 1.3425 |

Execution-control correction: the requested `PYTHONDONTWRITEBYTECODE=1` was present in every validation environment, but Python `-I` ignores Python environment options and initially still wrote cache files. Reproduction commands now use `python3 -B -I`; a direct control confirms effective `dont_write_bytecode=True` with the variable still1 and disk TMPDIR. New R15 cache files are removed at handoff. This correction changes interpreter cache writes, not engine/input/export bytes or numeric results. Full-suite commands and exits below are reported exactly as executed.

## Validation addendum

Verified at 2026-11-02T10:13:06.003968+00:00. CPU-only Linux x86_64, Python3.14.4 standard library; disk-backed TMPDIR. All199 recorded source/input/test identities are unchanged from the corrected candidate; all312 statically named prior engine tests remain under their original names (335 total executed including inheritance and14 new tests). Bench source is unchanged. Python3.9 syntax validation passed for all80 engine/test Python files.

| Validation | Exact standalone command (requested environment set) | Tests | Actual exit | Evidence |
| --- | --- | --- | --- | --- |
| engine-suite-02 | `python3 -I -m unittest discover -s calc/tests -v` | 335 | 0 | `.temp/hybrid-e-r6-261102/engine-suite-02.log`, `.result.json` |
| kit-final-02 | `python3 -B -I -m unittest discover -s bench/tests -v` | 24 | 0 | `.temp/hybrid-e-r6-261102/kit-final-02.log`, `.result.json` |
| focused-final-03 | `python3 -B -I -m unittest discover -s calc/tests -p test_run15.py -v` | 14 | 0 | `.temp/hybrid-e-r6-261102/focused-final-03.log`, `.result.json` |
| historical-manifest-02 | `python3 -I -m unittest discover -s calc/tests -p test_run14.py -v` | 17 | 0 | `.temp/hybrid-e-r6-261102/historical-manifest-02.log`, `.result.json` |
| Final export/quote custody | `python3 -B -I calc/tests/r15_audit.py --audit-only` | 95 generated files +512 prior files;8804 quote rows /8301 actual changed cells (r6 gate reported8282; corrected in r7) | 0 | `.temp/hybrid-e-r6-261102/audit-final-05.log` |

Engine validation started: 2026-11-02T10:03:36.814240+00:00.

Engine validation finished: 2026-11-02T10:11:29.528985+00:00.

The sampled minimum free disk through this verification is **29124698112 bytes (29.124698GB)**, above28,000,000,000. The one-second task monitor stays active through local delivery and records actual observations; no attribution to other sessions and no foreign cleanup. Original task extracts were removed (1,518,497 bytes), TMPDIR was cleaned after all gates ended, and 3 task-created R15 cache files were removed: `calc/hybridcalc/__pycache__/measurements_r15.cpython-314.pyc`, `calc/tests/__pycache__/r15_audit.cpython-314.pyc`, `calc/tests/__pycache__/test_run15.cpython-314.pyc`. Original archive retained. No downloads, model/GPU execution, native builds, push, tag, or hosted review/landing.

Delivery evidence: `.temp/hybrid-e-r6-261102/delivery-verification-01.json`, `candidate-source-identity.json`, `archive-custody-01.json`, `fault-results-01.json`, `disk-summary.json`, and `extract-cleanup-01.json`. No requested requirement is excluded. Ready for review.

## r7: unique quote-cell identities (hybrid-e-r7-261102)

Rework base: reviewed signed head `0ef3fc285283906861eb4a6beb845905a9ec1479`, continuing `engine-r15`. Muse r5m finding F1 is confined to ledger completeness: the previous set key discarded coordinates and used `row=-1` for five expired anchors, collapsing 19 distinct changed cells. The ledger already contained their values. The corrected count is **8,301 changed cells**, not 8,282; **8,804 ledger rows** remain (8,785 cell-site rows plus 19 prose rows). Scope is the 34 changed tables with Run14 counterparts; the two new historical/shape sensitivity tables have no prior counterpart and are documented in their own sections, not counted as changed counterpart cells.

Expired anchors now use their original zero-based Run14 row identity, namespaced as `row=r14:<index>`; active rows retain their Run15 index. For example, the removed four-stream 32k condition is `parallel_anchors.csv[row=r14:9].condition; streams=4; depth=32000`. Coverage compares source, the complete row/column/coordinate key, old and new, and refuses an expected-key collision. All 40 expired-anchor paper sites are distinct and carry coordinates; embedded anchor values are located by physical coordinates. No shared sentinel remains. All ledger old/new values and all 19 prose rows are unchanged.

### Regression controls

The named clean control is `test_quote_coverage_clean_control_has_8301_unique_cells`. Next to it, `test_expired_anchor_duplicate_cell_deletion_is_rejected` deletes exactly one condition cell while retaining the duplicate-valued condition of another expired anchor. `test_quote_coverage_rejects_lost_or_wrong_coordinates` separately covers absent and forged coordinates. The original `test_quote_ledger_rejects_missing_changed_cells` name and its table/prose assertions are retained.

Before the fix, `expired-cell-regression-before-01.log` records actual exit1 because the expected rejection never happened. `coverage-regression-before-01.log` records actual exit1: the clean-count test saw 8282, and both coordinate plants were wrongly accepted. These are expected-red regression failures on r6, not passing gate evidence. After the fix, all 18 focused tests pass, exit0. The standalone in-memory clean control also exits0 and reports 8301.

Standalone plant commands use `python3 -B -I .temp/hybrid-e-r7-261102/quote_fault_probe.py <mode>` with the environment below; they write no ledger or export files. Each failing plant reaches the intended `unreported changed cells` assertion, not a setup error. This is finite single-cell/coordinate calibration, not a universal completeness proof.

| Mutant mode | What it narrows the gate to | Named regression test | Actual exit | Surviving bound |
| --- | --- | --- | --- | --- |
| `expired_anchor_cell` | One duplicate-valued expired cell cannot be covered by another original row | `test_expired_anchor_duplicate_cell_deletion_is_rejected` | 1, expected red | None; rejected |
| `missing_coordinates` | A matching index/value pair cannot replace the full coordinate key | `test_quote_coverage_rejects_lost_or_wrong_coordinates` | 1, expected red | None; rejected |
| `wrong_coordinates` | Forged coordinates cannot cover the real cell | `test_quote_coverage_rejects_lost_or_wrong_coordinates` | 1, expected red | None; rejected |

Definitions and logs: `.temp/hybrid-e-r7-261102/quote_fault_probe.py`, `fault-control-01.log`, `fault-expired_anchor_cell-01.log`, `fault-missing_coordinates-01.log`, `fault-wrong_coordinates-01.log`.

### Six-agent paper qualification

The paper must show the 6-agent row with a dagger and this footnote: “Six streams measured only at 260k; shallower calls hold the 6.68 tok/s aggregate lower bound: 0% of calls measured, 90.67% shallow-held; excluded from fitted trends and agent-count capacity-gain ratios.” Both links are daggered in this report. Keep this flagged row visible; if space requires moving it to a supplement, disclose the move in the main table note. The existing capacity table retains only 1→4, 1→8, 1→16 and 4→16, with the reason for excluding 6 now explicit.

The CSV already has machine-readable qualification metadata at both links: `coverage = shallow; depth_modelled; count_conservative`, `measured_call_share = 0.0`, `measured_decode_time_share = 0.0`, `shallow_call_share = 0.9067010825982358` (36,181/39,904 calls). These existing flags meet the conditional metadata requirement without changing frozen export bytes. `test_six_agent_row_retains_machine_readable_measurement_gap` checks both six-agent rows and adjacent 4/8-agent measured controls. No engine number, CSV column or generator source changes.

### Frozen bytes and validation

Before and after SHA-256 inventories match every file against reviewed Git head `0ef3fc28`: 96 R15 files (95 family files **and INDEX.json**), 150 historical, 252 Run13 and 110 Run14 files, 608 total. Individual hashes, file-set checks and observation times are persisted in `.temp/hybrid-e-r7-261102/exports-before.json` and `exports-after.json`; command logs are `custody-before-01.log` and `custody-after-01.log`, both exit0. The R15 sorted SHA-256 inventory digest is `85c83edc12520e971a6b90a8071b14ff6c627c3fdefa35d6d80acdc261568981`, identical before/after. Inventory bytes are sorted lines `<sha256>  <repository-relative path>\n`, including all 96 files. The repaired ledger has 40 changed engine keys, 8301 coordinate-qualified paper sites and zero changed old/new values or `paper_current` cells.

All commands below set `PYTHONDONTWRITEBYTECODE=1` and disk-backed `TMPDIR="$PWD/.temp/hybrid-e-r7-261102/tmp"`. Python 3.14.4, Linux CPU only; no downloads, model execution or native builds. `-B` also enforces no bytecode writes under isolated mode. All 350 previously declared class/test-method names in engine and kit files remain; four named tests are added. In-memory Python 3.9 grammar validation covers 94 Python files, exit0. Source/input/test custody records 251 file hashes, including bench sources, in `validation-source-identity.json`.

| Validation | Standalone command | Result / actual exit | Evidence under `.temp/hybrid-e-r7-261102/` |
| --- | --- | --- | --- |
| Ledger/export audit | `python3 -B -I calc/tests/r15_audit.py --audit-only` | 8804 rows /8301 cells; 95 family files and 512 prior files, exit0 | `audit-01.log` |
| Focused R15 suite | `python3 -B -I -m unittest discover -s calc/tests -p test_run15.py -v` | 18 tests, exit0 | `focused-01.log` |
| Kit suite | `python3 -B -I -m unittest discover -s bench/tests -v` | 24 tests, exit0 | `kit-suite-01.log` |
| Full engine suite | `python3 -B -I -m unittest discover -s calc/tests -v` | 339 tests in687.691s, exit0 | `engine-suite-01.log` |
| Source/test/grammar custody | `python3 -B -I .temp/hybrid-e-r7-261102/source_custody.py before` | 350 prior names retained; 94 files parse; all ledger values unchanged, exit0 | `source-custody-before-01.log` |

The initial background disk watcher did not survive its short tool cell; no continuous sampling is claimed between its 10:50:41Z sample and the 10:54:13Z snapshot. Both observations exceeded 33.6 GB. It was restarted as a persistent foreground tool session with its PID recorded; later samples and the minimum are in `disk-samples.jsonl` and `disk-summary.json`. No foreign processes or files were touched. Final sampled disk and delivery results are recorded below after validation.

No surface table or separate landing-property suite was supplied (brief gap). All existing reviewer tests are retained, and the engine/kit suites are the supplied regression gates. No requested requirement is excluded. The rework touches the R15 audit/test module, its ledger, writer report, README documentation and repository integrity manifest. No paper source, engine/generator input, benchmark source or export is in the rework diff. Signed local delivery only, with the requested coauthor; no push. Independent re-review remains pending.

Full-engine completion observed at2026-11-02T11:04:31Z: **339 tests in687.691s, exit0**, started at10:52:59Z. Final ledger audit (`audit-final-02.log`), post-audit608-file hash check (`custody-final-03.log`) and unchanged251-file source/test identity check (`source-custody-after-01.log`) all exit0. Engine and kit gates are green; independent re-review is pending.

At report finalization (2026-11-02T11:06:10.048995+00:00), the sampled minimum free disk was **28224045056 bytes**, above28,000,000,000. The watcher remains active through local delivery. No extracts were created; disk-backed TMPDIR is empty. Source review and whitespace validation passed; the repository manifest is refreshed for the reviewed scope. Ready for review.

**Resource-control failure after signing the implementation:** the persistent watcher recorded **27,722,223,616 free bytes at2026-11-02T11:06:21.982967Z**, below the28,000,000,000-byte floor, and exited1 with `disk floor violated`. The earlier above-floor minimum is a timestamped report-finalization observation, not a claim about the entire delivery window. No other sessions' files or processes were altered. All engine, kit, focused, hash and ledger gates had already passed, but the requested disk-floor constraint was **not maintained**. Evidence: `.temp/hybrid-e-r7-261102/disk-floor-failure.json`, `disk-samples.jsonl`, `disk-watch-02.log`. This control failure is included in the orchestrator handoff; no cause is attributed without evidence.
