# Paper v4 gap map: hybrid-c-r20-261103

## Authority and scope

Base: owner-specified rc.3 branch `5f9846f319c8f5f222979bcb017ad9ae65d6206e`,
tree `5b2e4caae48e79861ed70b03246ed4790ca6a467`, equal to the public Ivan-signed
rc.3 tree. Branch `paper-v4`; signed merge `fff148083e08e1da47815c582481dd9022a8f0ad`
imports the exact accepted engine `e51942d331e274833f97f934a750d780c9bea9b0`.
No push, tag, release, hardware experiment, native build or download is authorized.
The local draft retains the existing git-derived version mechanism; its label
is not a newly published rc.3 asset. Authors stay Cyrillic in the Russian PDF.

No local task board is present (`task-board goal get`, exit 1); the existing
`.temp/tasks.md` tracks this work. No applicable installed/project skill exists.
No attack-surface table or separately named landing-property suite was supplied:
this is a brief gap, not a claim of complete attack coverage. No requested row
is treated as out of contract. Independent paper acceptance belongs to the
orchestrator; this local source package is ready for review only after its gates.

Numeric authority: `ENGINE-REPORT-R16-261103.md`, `ENGINE-QUOTES-R16-261103.csv`,
`out/run16/{base,bounded_undo}/`, and the full owner FACTS snapshot retained as
`data/measurements/paper-v4-2026-11-03/FACTS.md` (sections 2, 3 and 5 read in full
for the requested blocks). The LaunchAgent cause and kit refusal contract also
come from the owner's explicit brief. Earlier engine exports and historical
fixture bytes remain unchanged. Every CSV in the current embedded snapshot is
byte-identical to run16/base. Its SOURCE and manifest identify the new authority.

## Length

| Artifact | rc.3 baseline | v4 | Delta |
| --- | ---: | ---: | ---: |
| PDF pages | 30 | 30 | 0 |
| Main-text lexical words | 13,845 | 13,729 | -116 |

Counts use the same parser before and after: sections 00 through 14, including
05b, headings, captions and prose footnotes; excluding bibliography, appendix,
comments, tabular/TikZ/axis bodies, display/inline math, command names and
reference/label arguments. Numeric prose tokens count as lexical words. These
are source lexical counts, not a claim of compatibility with TeXcount's default
word categories. Counter and per-section JSON: task directory `count_size.py`,
`baseline-size.json`, `after-size.json`. PDF page-tree counts independently agree
with the number of Page objects after decompressing object streams. The baseline
cache-only build exited 0; its failed initial uncompressed-only page-count probe
was corrected to handle compressed object streams. No paper structure changed.

## Changes and qualifications

| Subject | v4 treatment | Source / limit |
| --- | --- | --- |
| M3 singleton anchors | PRI 31 cold segments and delta/decode ladder replace old anchors; transcript, turn, one-shot, architecture, cost, capacity and refill claims recomputed | R16 base; six nominal depths, three delta sizes; no new measurement beyond 249k |
| M3 parallel capacity | Visible background-priority/interim qualifications in client/agent tables, zone shares, gains, traffic, economics and conclusion | R16 `background_priority_interim`; full PRI 31 curve pending; six-agent row retains its separate 0% coverage dagger and trend exclusion |
| Old singleton sweep cells | Historical PRI 4 cells retained in labelled multi-stream measurement table, from `parallel_historical_sensitivity.csv` | They do not supply canonical singleton lookups; all 22 cooled table cells retain once-only rounding controls |
| PRI 31 parallel controls | 57.375/47.83 at 32k/32; 37.862/35.56 at 64k/32; 18.705/20.22 at 128k/16; 18.77/14.35 at 128k/4 | FACTS section 2; complete intermediate-count sweep unmeasured |
| M5 cooled sweep | Added all 13 measured medians; current capacity uses cooled M5 data | Normal priority owner-reported, not recorded; 128GB/Ultra portability remains estimated |
| Gemma/Glimmer Mac | Table visibly marks all M3 cells PRI 4; normal-priority repeat pending | FACTS section 2; no silent promotion to PRI 31 |
| Import | `0.2591 + 48.7e-6*d + 34.64e-6*L` seconds | Conditional four-probe depth fit; token slope retained from weak marginal fit; beyond 100k extrapolated |
| Import diagnosis | Full save of old slot is 94.2% of CPU-diagnosed depth slope | CPU diagnosis; Mac benefit from changing implementation unmeasured |
| Bounded undo | Separate future-work sensitivity without the depth term | Transaction and lost-ack qualification required; no implementation claim |
| f32/bf16 thresholds | At 100k/2343, 8.05/7.20 and 5.40/4.83 MB/s | Prototype/bounded undo; ideal equal-cost threshold excludes catch-up/queueing, bf16 bridge unqualified |
| Preflights | Wi-Fi 5.19 MB/s all local; 5G 9.75 MB/s offloads 7/31 | Old policy entry threshold near 8.45 MB/s remains separately identified in related work; distinct from new equal-cost threshold |
| 5G timing arms | Both 40 turns to 143,439; decode 10.0-12.3 tok/s at PRI 31; outage 2-4 and resync boundary reported | FACTS section 3; 40-turn totals exclude pre-staged base |
| Instrumentation | TTFT/capture/residual/local rows: base 2896.8/2413.5/483.3/884.0; turn 7 468.7/425.6/43.1/33.7; turn 31 490.5/455.2/35.3/38.9 | Synchronous checker node snapshots are inside TTFT. Subtraction is an arithmetic residual; production timing without snapshots is unmeasured; other instrumentation may remain |
| Engine validation | Base and turns 7/31 show local, ideal and observed-wire/catch-up predictions against observations | No fitting to held-out residuals; Workstation-to-Server-Edition portability estimated; base/turn 7 errors retained |
| Checkpoint 10 | Not measured on Mac: MTL/Metal label guard refused; bug fixed, recheck pending; first recheck refused RAM before launch | CUDA rehearsal's 4/4 checkpoints remain explicitly CUDA-only |
| RULER 8k | 97.01% in all three CUDA arms; 0 score disagreements/390 examples; text changed 34/390 (8.72%) and 32/390 (8.21%); McNemar p=0.727; excess interval -2.13 to +3.12 pp | Equivalence at the 2 pp margin is not established at this n; no Metal-quality claim |
| Publication | Unreleased changelog, version unchanged; refreshed current source/number pins with retained historical tests and fixtures | Current migrations are explicit hash deltas; historical assertions/tolerances remain |

## Remaining gaps (FACTS section 5, updated 2026-11-03 08:40 UTC)

- RULER 32k started at 07:32 UTC, expected about six hours; 64k/128k follow the owner's budget decision.
- Mac checkpoint 10 recheck and the RAM preflight refusal remain unresolved.
- Full normal-priority M3 parallel, Gemma and Glimmer measurements need an idle Mac window; engine R16b follows as a data-only update.
- CUDA-to-Metal calibration against BF16 needs the Mac; GPU vLLM state bridge awaits rework; Bonsai 2 2B/4B/9B ladder is later.
- Bounded undo remains future work; bf16 threshold sensitivity does not qualify a working bf16 bridge. Uninstrumented production timing, multi-user queues and sustained workload qualification remain unmeasured.

## Finite negative evidence and validation

All 372 pre-existing statically named engine tests remain, with their original
names. Current-snapshot expectations were migrated; the immutable historical
input archive and historical exports were not edited. Seven new v4 tests bind
source data, priority qualifiers, instrumentation arithmetic, bounded RULER
claims and payback-plot bounds. The exact byte guard covers every tracked paper
file and every TeX numeric occurrence; both live checkers retain prior site IDs.
One historical refill direction ID still names its original above-day claim;
its current predicate/wording and D5 plant now require the R16 below-day result.
That stable ID is not a current above-day claim.

| Plant / mutant | Narrows the gate to | Named rejecting test / gate | Surviving bound |
| --- | --- | --- | --- |
| Old cold ladder | Recorded PRI 31 cold source instead of old background curve | `test_pri31_cold_ladder_rejects_background_regression`; exact publication site guard | None for the enumerated ladder |
| Missing interim/M5 priority qualifier | Each named capacity, gains, economics, traffic and SWA surface carries its condition | `test_measurement_qualification_plants_are_detected`; offload self-test | None at enumerated sites; arbitrary prose outside registered sites needs review |
| Corrupt capture/residual cell | Arithmetic subtraction at base and turns 7/31 | `test_snapshot_residual_rows_follow_trace_derived_export`; R16 `test_instrumentation_rejects_wrong_trace_or_capture_accounting` | No claim that residual is a production measurement |
| Completed/equivalent RULER overclaim | Score agreement and finite paired interval remain distinct | `test_ruler_scores_text_changes_and_unestablished_equivalence`; retained `test_quality_and_source_overclaims_are_rejected` | Finite 390 CUDA examples; other depths/backends pending |
| Removed Mac-pending / future-undo qualifier | Neither unmeasured fidelity nor unimplemented undo becomes delivered | `test_measurement_qualification_plants_are_detected`; checker self-test | Real Mac recheck and rollback/lost-ack qualification pending |
| Doubled rounded parallel median | Once-only rounding from exact source cells | retained `test_measured_parallel_cells_round_csv_once` | No universal rounding proof outside enumerated table cells |
| Plot upper bound below updated repayment | All printed payback bars fit the figure | `test_payback_plot_does_not_clip_updated_months` | Numeric clipping only; full visual review not claimed |

Command/PID/time/free-space/real-exit receipts and complete stdout/stderr are in
`.temp/hybrid-c-r20-261103/<gate>.json` and `<gate>.log`. Preliminary migration
runs are kept honestly: focused tests failed before publication/migration pins
were refreshed; spacing failed on three imported README glues and was corrected;
the initial broad whitespace probe flags the repository's CRLF CSV format,
while the CR-aware authored-diff check exits 0. Two preliminary engine attempts were stopped by their recorded owned PIDs (each exit -15) while final prose corrections were still being made; neither incomplete attempt is passing evidence. A first manifest verification raced its writer and exited 1 on a temporary empty file; the corrected sequential verification exited 0. The final manual audit corrected M5 gain percentages, the autopilot illustration and GLM cold-ingest minutes and added source-bound named stale-value plants. The first completed full suite ran 409 tests and exited 1: the retained `test_paper_ledger_omission_controls` selected removed historical 5G token 179.5 and raised StopIteration before applying that plant. The same named test now selects current 891.6 and retains the exact omission/rejection assertion. Final gate results are appended below after execution. No native build or network download was used. The optional R16 `--audit-only` command exits 0 but unconditionally rewrites quote consumer-site annotations. Its generated local delta was preserved under the task directory, then that single path was restored byte-for-byte from accepted `e51942d`. Final source custody and the full suite use the accepted ledger. No engine export changed.

## Complete old / new / source numeric inventory

`PAPER-V4-NUMBERS-261103.csv` inventories every changed numeric spelling against
the rc.3 base, independent of the named checkers. The table below reproduces it.
Each block pairs differing numeric subsequences within one source file, in
source order; a block can describe replacement of a whole discussion rather
than equality of the old and new quantities. `<absent>`/`<removed>` are explicit.
Source CSV names refer to `calc/out/run16/base/`; FACTS refers to the retained
current snapshot above. Exact cell coordinates for all 218,146 engine changes
remain in the accepted R16 engine quote ledger. Captions, layout limits and
model identifiers also appear here; no whole-section numeric exemption is used.

Number-word changes were checked separately: the old four-to-six-minute Mac
example becomes 225 seconds at 150k; the old more-than-a-day refill claim becomes
about 20 hours. Approximate device counts (three M5, four M3, one-and-a-half
Ultra) remain rounded workload illustrations, with M3 interim qualification
in the section's table caption. The printed four-agent/gain and zone figures
are all computed from the new current snapshot, not copied from R15.

| Site (new lines) | Old | New | Source |
| --- | --- | --- | --- |
| `paper/sections/00-abstract.tex:5` | <absent> | 31; 225 | calc/out/run16/base/person_cost_s20*.csv; m3_pri31_depth.csv; FACTS sections 2-3 |
| `paper/sections/00-abstract.tex:15` | 4.8--6.1 | 4.8--6.0 | calc/out/run16/base/person_cost_s20*.csv; m3_pri31_depth.csv; FACTS sections 2-3 |
| `paper/sections/00-abstract.tex:19` | 271.5; 201.7; 26; 165.6; 10.6 | 143\,439; 31 | calc/out/run16/base/person_cost_s20*.csv; m3_pri31_depth.csv; FACTS sections 2-3 |
| `paper/sections/00-abstract.tex:27` | <absent> | 8; 97.01; 390; 2 | calc/out/run16/base/person_cost_s20*.csv; m3_pri31_depth.csv; FACTS sections 2-3 |
| `paper/sections/01-introduction.tex:9` | 131; 181; 41; 28 | 31 | calc/out/run16/base/m3_pri31_depth.csv; shown 10000/rate arithmetic; FACTS section 2 |
| `paper/sections/01-introduction.tex:9` | <absent> | 150; 44.37; 225 | calc/out/run16/base/m3_pri31_depth.csv; shown 10000/rate arithmetic; FACTS section 2 |
| `paper/sections/01-introduction.tex:32` | <absent> | 4 | calc/out/run16/base/m3_pri31_depth.csv; shown 10000/rate arithmetic; FACTS section 2 |
| `paper/sections/01-introduction.tex:32` | 5; 5000 | 31 | calc/out/run16/base/m3_pri31_depth.csv; shown 10000/rate arithmetic; FACTS section 2 |
| `paper/sections/02-workload.tex:42` | 7.5--8.8 | 31 | calc/out/run16/base/client_prefill_segments.csv; m3_pri31_depth.csv; shown 10000/44.37 and 512/8.993 arithmetic |
| `paper/sections/02-workload.tex:<none>` | 5 | <removed> | calc/out/run16/base/client_prefill_segments.csv; m3_pri31_depth.csv; shown 10000/44.37 and 512/8.993 arithmetic |
| `paper/sections/02-workload.tex:43,48,49,54` | 32; 13.2; 14.05; 8.44; 8; 39; 81; 131; 181; 231; 173.6; 93.7; 49.9; 41.2; 27.7; 22.2 | 14.99; 6.93; 8.0; 39.4; 81.4; 131.4; 181.4; 230.9; 191.5; 128.8; 81.4; 52.5; 38.2; 30.1; 150 | calc/out/run16/base/client_prefill_segments.csv; m3_pri31_depth.csv; shown 10000/44.37 and 512/8.993 arithmetic |
| `paper/sections/02-workload.tex:54` | 131--181; 4; 6 | 31; 10000; 44.37; 225.4 | calc/out/run16/base/client_prefill_segments.csv; m3_pri31_depth.csv; shown 10000/44.37 and 512/8.993 arithmetic |
| `paper/sections/02-workload.tex:55` | 75--93; 150; 5.5; 6.8; 28; 4; 77 | 512; 8.993; 56.9 | calc/out/run16/base/client_prefill_segments.csv; m3_pri31_depth.csv; shown 10000/44.37 and 512/8.993 arithmetic |
| `paper/sections/04-channel.tex:11` | 6.6 | 4.9 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:12` | 62; 25 | 58; 22 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:26` | 43.0; 22.1; 1.9; 10.0; 4.3; 5.8 | 30.4; 23.7; 1.3; 11.6; 2.6 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:26` | 10.4 | 5.7; 5.3 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:27` | 218.4; 59.4; 3.7; 32.4; 6.7; 23.0; 9.5; 19.3; 11.3 | 162.4; 52.8; 3.1; 25.8; 6.3; 16.4; 9.9; 12.7; 12.8 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:28` | 78.3; 22.6 | 54.5; 27.7; 2.0; 15.6 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:28` | 10.5; 7.5; 6.3; 12.5; 4.7; 16.8 | 11.4; 4.8; 9.7; 5.6 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:29` | 398.7; 61.6; 6.5; 34.6; 11.5; 25.2; 15.8; 21.6 | 295.8; 58.5; 5.1; 31.5; 9.4; 22.1; 13.4 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:29` | <absent> | 16.0 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:36,37` | 69; 429 | 50; 224 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:37` | 215 | 10 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:49` | 21.3; 466; 272; 204; 178 | 14.9; 364; 170; 102; 76 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:50` | 69.3; 942; 562; 429; 377 | 50.4; 737; 357; 224; 173 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:51` | 115.2; 1247; 752; 579; 512; 110; 16.0; 9.78; 39\,504; 271.5; 201.7; 211.7; 26; 10.6; 123.2; 42.4; 165.6; 201.7; 179.5; 201.7; 25.5 | 84.2; 979; 484; 310; 244 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:57,58,59,60,61,74,75,76,82,84,85,86,89,90,91,93` | 176.2 | 31; 40; 100; 143\,439; 9.75; 140.6; 38; 7; 31; 2--4; 106\,849; 103\,024; 10.0--12.3; 100--143; 100; 2896.8; 2413.5; 483.3; 884.0; 7; 468.7; 425.6; 43.1; 33.7; 31; 490.5; 455.2; 35.3; 38.9; 483.3; 43.1; 35.3; 40; 1158.7; 262.9; 3646.4; 2736.8; 477; 9.7; 134.9; 3.64; 238.5; 2343; 4.0; 5.6; 891.6; 884.0; 7; 31; 36.4; 44.2; 33.7; 38.9; 418.1; 30.0; 31.2; 418.4; 33.2; 35.0; 483.3; 43.1; 35.3; 6000; 10 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:101` | <absent> | 4 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:<none>` | 2\,004\,023\,525; 39\,504; 34\,840; 156.9; 512 | <removed> | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:106,107,108` | 11.5; 7.9; 2.4; 10.3; 19.4 | 8.6; 4.1; 1.2; 5.3; 12.7 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:109` | 20; 18.9 | 16.2; 10.9 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:115` | <absent> | 31 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:116` | 75.1 | 3.7 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:126` | 11.5; 3.7; 2.4; 19.4; 11.6; 10.3 | 8.6; 2.5; 1.2; 12.7; 6.7; 5.3 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:127` | <absent> | 2.5; 1.2; 7.0; 5.1 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:<none>` | 2.3; 7.5; 6.8; 5.4 | <removed> | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:128` | 21.6; 3.7; 2.4; 38.1; 20.3; 18.9 | 16.2; 2.5; 1.2; 26.0; 12.3; 10.9 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:148,149` | 25.9; 41.0; 54.4; 59.8; 17.0; 21.8; 24.0; 24.7 | 15.8; 26.1; 31.8; 33.4; 9.5; 13.3; 14.9; 15.3 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:150,151` | 34.5; 48.8; 58.7; 62.3; 19.1; 22.9; 24.4; 24.9 | 20.9; 29.2; 33.0; 34.0; 10.9; 13.9; 15.1; 15.4 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:157` | 17; 28 | 9.5; 14.9 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:164,167,168` | 121; 656 | 15.8; 31.8; 4; 31; 84; 634 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:168` | 1.66 | 1.12 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:168` | 8 | 6 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:169,178` | 83; 150; 81 | 56; 101; 77; 2343 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/04-channel.tex:179,180,181,182` | <absent> | 8.05; 7.20; 5.40; 4.83; 5.19; 9.75; 7; 31 | calc/out/run16/base/turn_speedup.csv; oneshot_ingest.csv; transcript_example.csv; offload_by_link.csv; traffic_user_month.csv; growing_5g_validation.csv; state_link_threshold.csv; FACTS section 3 |
| `paper/sections/05-clients.tex:61,62,65,66,67` | <absent> | 4; 31; 9--85; 28--203; 31; 4; 4; 31 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:71,72,73` | 162--176; 93--101; 47--60; 28--31; 21--26; 16.5--20.7; 128; 4.3--7.7 | 512--10; 000; 156.3--176.9; 106.7--121.7; 63.5--66.2; 44.4--47.1; 34.5--36.8; 27.8--29.7; 14.99; 13.52; 10.36; 8.99; 7.82; 6.93 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:85,86,87` | <absent> | 31; 32; 32; 57.375; 47.83; 4; 64; 32; 37.862; 35.56; 128; 16; 18.705; 20.22; 16; 18.77; 14.35; 31 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:91` | 128; 34 | 4 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:96` | 15 | 4; 31 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:114,115,116` | <absent> | 32; 22.62; 31.89; 47.78; 62.32; 62.78; 65.54; 64; 19.88; 26.00; 32.55; 40.23; 128; 15.73; 18.35; 20.69 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:121` | <absent> | 4 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:128` | 15 | 4; 16 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:134` | <absent> | 4 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:138` | 7.5--8.8 | 31; 14.99 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:<none>` | 40 | <removed> | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:139` | <absent> | 4 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:142,144` | 3.54; 5.66; 1.60; 17--25 | 4; 31; 3.97; 5.47; 1.38; 10--15 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:147` | 2.00--2.86; 26--29 | 28--29 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:161` | <absent> | 4; 31 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:168` | 8.8; 3.54; 5.66; 1.60 | 14.3; 3.97; 5.47; 1.38 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:169` | 11.5; 5.24; 7.06; 1.35 | 19.5; 8.38; 11.01; 1.31 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:170` | 18.3; 5.61; 7.07; 1.26 | 22.6; 6.73; 8.67; 1.29 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:171` | 18.3; 5.78; 7.45; 1.29 | 22.6; 6.58; 8.44; 1.28 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:172` | 36.6; 11.22; 11.22 | 45.2; 12.95; 12.95 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:173` | 36.6; 12.09; 12.09 | 45.2; 13.64; 13.64 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:174,175` | 5.4; 3.04; 3.41; 1.12; 5.8; 3.52; 3.52 | 9.1; 5.04; 5.57; 1.11; 9.7; 5.94; 5.94 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:192` | <absent> | 4; 31 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:201` | 2.06; 2.57; 1.25; 9.3; 12.4 | 3.06; 3.74; 1.22; 10.3; 18.0 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:202` | 2.89; 4.04; 1.40 | 3.18; 4.00; 1.26 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:203` | 3.54; 5.66; 1.60 | 3.97; 5.47; 1.38 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:204` | 2.32; 3.09; 1.33 | 2.50; 3.02; 1.21 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:205` | 3.91; 6.76; 1.73 | 4.45; 6.42; 1.44 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:206` | 4.12; 7.41; 1.80 | 4.73; 7.01; 1.48 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:207` | 4.18; 7.59; 1.82 | 4.80; 7.18; 1.49 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:219` | <absent> | 1.30; 1.46; 1.57; 1.46 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05-clients.tex:219,220` | 1.90; 2.03; 2.20; 2.62; 2.95; 1.18; 1.34 | 1.92; 1.21; 1.31; 4; 31 | calc/out/run16/base/m3_pri31_depth.csv; m5_cooled_parallel.csv; client_sessions_day.csv; client_agents_day.csv; decode_scaling.csv; FACTS section 2; shown capacity-ratio arithmetic |
| `paper/sections/05b-models.tex:13` | 41.2 | 31; 53.74; 1000 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:<none>` | 24 | <removed> | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:30` | 34; 77 | 15; 26; 59 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:32` | 8.9; 17.0 | 3.3; 12.5 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:32` | 66.0 | 48.0 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:33` | 19.2; 18.6; 21.0; 73.4 | 13.5; 14.0; 13.1; 55.4 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:34` | 22.7; 19.1; 29.9; 76.0 | 17.1; 14.6; 22.0; 58.0 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:53` | 17; 9 | 12.5; 3.3 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:54` | 19--21 | 13--14 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:55` | 30 | 22 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:57` | 36; 53 | 28; 41 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/05b-models.tex:80` | <absent> | 4; 31 | calc/out/run16/base/arch_compare.csv; FACTS section 2 |
| `paper/sections/07-economics.tex:55` | 6.4 | 5.6 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:55` | 14 | 16 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:59` | 67--77; 4.8--5.4 | 67--73; 4.8--5.2 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:60` | 1.3--1.5 | 1.4--1.5 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:61` | 5.9--6.1 | 5.8--6.0 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:64,65` | 820; 114--130; 222--268 | 1010; 107--160; 204--354 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:66` | 2.0--2.2 | 1.6--2.4 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:68` | 1.2--1.3 | 1.2--1.6 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:69` | 178--179 | 176--177 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:73` | <absent> | 4; 31 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:86` | 656; 76.6; 113.5; 160.9 | 634; 73.4; 107.2; 154.7 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:87` | 819; 74.6; 126.5; 173.9 | 1\,277; 71.3; 160.0; 207.4 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:88` | 821; 73.5; 125.1; 160.3 | 1\,006; 71.3; 138.4; 173.6 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:89` | 864; 73.9; 129.7; 186.5 | 979; 71.7; 136.5; 193.3 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:90` | 1\,302 | 1\,503 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:91` | 1\,403 | 1\,582 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:105` | 160 | 174 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:106` | 109 | 107 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:108` | <absent> | 22; 44 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:108` | 40; 20; 92; 181 | 86; 168 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:109` | <absent> | 36; 72 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:113` | 97; 50; 125 | 138 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:119` | 74 | 180 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:135,136` | 50; 97; 59--90 | 36; 72; 57--103 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:214` | 2.2--2.4 | 2.3--2.5 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:216` | 27--35 | 27--39 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:219` | 28.2; 77.1 | 19.9; 54.3 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:222` | 21 | 20 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:225,226` | 20; 19 | 25--26; 24--26 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:244` | 21 | 20 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:245` | 21 | 20 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:246` | 56 | 53 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:246` | 81 | 98 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:247` | 81 | 98 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:248` | 47 | 46 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:248` | 81 | 98 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:249` | 287; 298; 26 | 265; 272; 31 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:250` | 278; 288; 26 | 260; 270; 31 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:251` | 278; 287; 26 | 259; 270; 31 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:261` | 0.016 | 0.226 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:262` | 4.7--5.4 | 5.0--5.4 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:270` | <absent> | 4; 31 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:277` | 6.33; 4.50; 8.31; 7.40 | 4.41; 3.23; 5.59; 6.52 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:280` | 2.90; 1.92; 3.79; 3.14 | 1.62; 1.06; 2.04; 2.10 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:282,283` | 16.74; 12.24; 21.32; 18.57; 40.93; 34.82 | 17.35; 7.04; 18.11; 16.44; 37.07; 27.70 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:285` | 0.016 | 0.226 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:330,331` | 2.0--2.2; 52; 69 | 1.6--2.4; 51; 100 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/07-economics.tex:334,335` | 2.0--2.4; 20; 19 | 2.0--2.5; 25--26; 24--26 | calc/out/run16/base/person_cost*.csv; perimeter_cost*.csv; breakeven_prefill_price.csv; payback.csv derived from snapshot; symmetric_storage_candidates.csv |
| `paper/sections/08-million.tex:12` | 57 | 42 | calc/out/run16/base/glm_long_sessions*.csv; glm_utilization*.csv; shown integration from tab:m3max via check_ranges.refill_hours |
| `paper/sections/08-million.tex:18,19` | 26--28; 231; 181; 231; 25.9; 131; 231; 28.2 | 20; 230.9; 181.4; 230.9; 19.9; 131.4; 230.9; 19.9 | calc/out/run16/base/glm_long_sessions*.csv; glm_utilization*.csv; shown integration from tab:m3max via check_ranges.refill_hours |
| `paper/sections/08-million.tex:28` | 5.8--6.2 | 5.7--6.1 | calc/out/run16/base/glm_long_sessions*.csv; glm_utilization*.csv; shown integration from tab:m3max via check_ranges.refill_hours |
| `paper/sections/08-million.tex:31,34` | 11.78; 34; 1.19 | 11.74; 38; 1.33 | calc/out/run16/base/glm_long_sessions*.csv; glm_utilization*.csv; shown integration from tab:m3max via check_ranges.refill_hours |
| `paper/sections/08-million.tex:35` | 3.3--3.4; 2.7--2.8; 1.3--1.4; 3.9--4.3; 1.1; 2.1--2.3; 4.1--4.4 | 3.4--3.5; 2.6--2.7; 1.3; 3.9; 1.2; 2.4; 4.0--4.4 | calc/out/run16/base/glm_long_sessions*.csv; glm_utilization*.csv; shown integration from tab:m3max via check_ranges.refill_hours |
| `paper/sections/08-million.tex:63,64` | 1.1; 2.1--2.3; 1.3--1.4; 2.7--2.8 | 1.2; 2.4; 1.3; 2.6--2.7 | calc/out/run16/base/glm_long_sessions*.csv; glm_utilization*.csv; shown integration from tab:m3max via check_ranges.refill_hours |
| `paper/sections/08-million.tex:64` | 28--30 | 27 | calc/out/run16/base/glm_long_sessions*.csv; glm_utilization*.csv; shown integration from tab:m3max via check_ranges.refill_hours |
| `paper/sections/11-limitations.tex:7` | 2\,460; 820 | 3\,020; 1\,010 | calc/out/run16/base/FACTS section 3, paired RULER 8k; person_cost*.csv; latency_examples.csv |
| `paper/sections/11-limitations.tex:69,70,71,72,73,74,75,76` | <absent> | 8; 13; 30; 390; 261102; 64; 256; 97.01; 0; 390; 34; 390; 8.72; 32; 390; 8.21; 0.727; 95; -2.13; +3.12; 2; 32; 64; 128 | calc/out/run16/base/FACTS section 3, paired RULER 8k; person_cost*.csv; latency_examples.csv |
| `paper/sections/13-outlook.tex:4` | <absent> | 10 | calc/out/run16/base/unchanged source / layout |
| `paper/sections/14-conclusion.tex:12,13` | 17--25; 1.6 | 10--15; 1.38; 4; 31 | calc/out/run16/base/offload_by_link.csv; client_sessions_day.csv; person_cost*.csv; glm_utilization*.csv; FACTS sections 2-3; shown 1M refill integration |
| `paper/sections/14-conclusion.tex:13` | 26 | 29 | calc/out/run16/base/offload_by_link.csv; client_sessions_day.csv; person_cost*.csv; glm_utilization*.csv; FACTS sections 2-3; shown 1M refill integration |
| `paper/sections/14-conclusion.tex:13` | 29 | 28 | calc/out/run16/base/offload_by_link.csv; client_sessions_day.csv; person_cost*.csv; glm_utilization*.csv; FACTS sections 2-3; shown 1M refill integration |
| `paper/sections/14-conclusion.tex:17` | 4.8--6.1 | 4.8--6.0 | calc/out/run16/base/offload_by_link.csv; client_sessions_day.csv; person_cost*.csv; glm_utilization*.csv; FACTS sections 2-3; shown 1M refill integration |
| `paper/sections/14-conclusion.tex:18,19,20` | 2.7--2.8; 1.3--1.4; 2.0--2.4 | 2.6--2.7; 1.3; 20; 2.0--2.5 | calc/out/run16/base/offload_by_link.csv; client_sessions_day.csv; person_cost*.csv; glm_utilization*.csv; FACTS sections 2-3; shown 1M refill integration |
| `paper/sections/14-conclusion.tex:28,30` | 201.7; 271.5; 165.6; 201.7; 10.6; 179.5; 25.5 | 143\,439; 31; 10 | calc/out/run16/base/offload_by_link.csv; client_sessions_day.csv; person_cost*.csv; glm_utilization*.csv; FACTS sections 2-3; shown 1M refill integration |
| `paper/sections/90-appendix.tex:54,56,57,60` | 42.4; 39504 | 0.2591; 48.7; -6; 34.64; -6; 539; 94.2; 100 | calc/out/run16/base/import_depth_fit.csv; ENGINE-REPORT-R16-261103.md; FACTS sections 2, 3 and 5 |
| `paper/sections/90-appendix.tex:87` | <absent> | 4 | calc/out/run16/base/import_depth_fit.csv; ENGINE-REPORT-R16-261103.md; FACTS sections 2, 3 and 5 |
| `paper/sections/90-appendix.tex:108` | <absent> | 4 | calc/out/run16/base/import_depth_fit.csv; ENGINE-REPORT-R16-261103.md; FACTS sections 2, 3 and 5 |
| `paper/sections/90-appendix.tex:130,132,134,135,136,138` | <absent> | 4; 4; 10; 32; 2026; 11; 03; 07; 32; 64; 128; 31; 4; 31; 2 | calc/out/run16/base/import_depth_fit.csv; ENGINE-REPORT-R16-261103.md; FACTS sections 2, 3 and 5 |

## Validated source handoff

Scientific source and test head `e7e803f1f92836edaac4f9723e8110c041e8fd8d` ran the full engine suite: 409 tests, 510.599 seconds reported by unittest, exit 0. All 2,406 tracked source bytes were unchanged throughout that final run. Kit: 24 tests, exit 0. The earlier 409-test attempt exited 1 on the expired omission selector and remains a failed diagnostic, not green evidence.

| Required gate | Receipt | Exit |
| --- | --- | ---: |
| `engine-04` | `.temp/hybrid-c-r20-261103/engine-04.json` | 0 |
| `kit-final-02` | `.temp/hybrid-c-r20-261103/kit-final-02.json` | 0 |
| `ranges-final-02` | `.temp/hybrid-c-r20-261103/ranges-final-02.json` | 0 |
| `ranges-self-final-02` | `.temp/hybrid-c-r20-261103/ranges-self-final-02.json` | 0 |
| `offload-final-02` | `.temp/hybrid-c-r20-261103/offload-final-02.json` | 0 |
| `offload-self-final-02` | `.temp/hybrid-c-r20-261103/offload-self-final-02.json` | 0 |
| `publication-final-02` | `.temp/hybrid-c-r20-261103/publication-final-02.json` | 0 |
| `ledger-final-02` | `.temp/hybrid-c-r20-261103/ledger-final-02.json` | 0 |
| `spacing-final-02` | `.temp/hybrid-c-r20-261103/spacing-final-02.json` | 0 |
| `release-final-02` | `.temp/hybrid-c-r20-261103/release-final-02.json` | 0 |
| `signatures-final-02` | `.temp/hybrid-c-r20-261103/signatures-final-02.json` | 0 |
| `pdf-final-02` | `.temp/hybrid-c-r20-261103/pdf-final-02.json` | 0 |
| `manifest-05` | `.temp/hybrid-c-r20-261103/manifest-05.json` | 0 |
| `source-manifest-verify-final-03` | `.temp/hybrid-c-r20-261103/source-manifest-verify-final-03.json` | 0 |

The kit, checker, publication, spacing, release-fixture and cached-build source/test/configuration inputs are unchanged from their green receipts. The final test correction only moved the retained omission selector to the current scientific site. The accepted engine's 987 source/export/measurement files and quote ledger remain byte-identical; all 372 original static test names remain, with seven new v4 tests. No substantive code or paper delta follows this green source; this evidence note and root manifest are the only final tracked edits.

The owner PDF is `.temp/hybrid-c-r20-261103/hybrid-inference-v4-draft.ru.pdf`. The final artifact is rebuilt after the evidence commit to bind its git metadata to the delivered head; its SHA-256, exact head, final page/word readback and the authorized Matrix event are in `delivery.json` in the task directory. Counts remain 30 pages and 13,729 lexical main-text words (rc.3: 30 and 13,845). CPU-only, cached TeX; no push, tag or download. Minimum sampled free space stayed above 28,000,000,000 bytes. Underfull TeX spacing warnings remain; no overfull box, undefined reference/control or missing glyph was reported in the final source build. Full visual review is not claimed.

Source package is ready for independent review. Remaining measurement and future-work gaps above are not acceptance claims.
