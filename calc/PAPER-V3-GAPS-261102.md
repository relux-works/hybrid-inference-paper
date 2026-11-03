# Paper v3 gap map: hybrid-c-r15-261102

## Authority, scope and base

Owner base: rc.2 `27c51feaa5dedbc3f94cc59ef33c433edd0e3bdd`, tree
`71616b82eec526627b49ee281b15095a7596f9d8`. `paper-v3` starts there,
not at a moving public branch. Signed merge imports exact engine r15
`04755721ca9f08141b8fcff792e74dfc52cd1fc6`. No push, tag, downloads,
native build or new hardware experiment is authorized. No local task board or
applicable installed technical skill exists; the task plan is `.temp/tasks.md`.
The brief supplies no attack-surface table; no coverage-map completeness is claimed.
No requested text row is treated as out of contract. Independent review belongs
to the orchestrator after this local handoff.

Numeric authority is `calc/ENGINE-QUOTES-R15-261102.csv`, `calc/out/run15/`
and the orchestrator's `/home/agent/lanes/hybrid/.temp/paper-v2/FACTS.md`.
The comparison below was made against rc.2 before prose edits. Earlier statements
in PAPER-V2-GAPS remain historical. FACTS sections 1-3 contain later results that
supersede several pending entries in FACTS section 5. Evidence below refers to
FACTS unless a supplemental source is explicitly identified.

## Complete FACTS comparison against rc.2

| Evidence / fact | rc.2 coverage or gap | v3 placement / action |
| --- | --- | --- |
| 1: PRO 6000 checkpoints-off/on, earlier-run sensitivity, effective FP8 fraction | Covered in server and engine; retain finite device/build limits | Retain |
| 1: newer build and ubatch sweep | Covered in server, including 9-20%, 2-5% and 3950/4793 tok/s | Retain; models adds the new-build ladder without replacing the engine base |
| 1: PRO 6000 vLLM cold/cached, 784-token blocks, unavailable NVFP4/FP8 KV | Covered; old bridge-pending status superseded by later smoke | Server retains measurements, refreshes prototype status |
| 1a: kit 1.6.5, Qwen/Gemma/Glimmer PRO 6000 depth ladders, no rereads | Missing, models says GPU measurement pending | Models adds endpoints, measured delta/decode and exact no-reread counts |
| 1b: B300 llama.cpp ladder and same-card comparison | Covered by server tables and r14 economics | Retain, no inferred cause or peak-ratio substitution |
| 1c: B300 vLLM marginal/cached/default/FP8-KV measurements | Covered; server-only limits remain | Retain |
| 2: M3 canonical repeated-delta, earlier parallel, 260k, step55/restored control/step57, YaRN | Covered; old sweeps are historical | Clients distinguishes cooled r15 base from historical sweeps |
| 2: cooled kit 1.6.6, three-round medians, shape control, no rereads | Missing; marked pending | Clients current table, r15 snapshot, source report and separate np4 control |
| 2: explanation of daily gains and historical M5 biases | r14 already supersedes r13 rates | Recompute all current r15 sites, avoid promoting historical rates |
| 2: M3 Gemma kit 1.6.5, six depths, no rereads, 18 deltas | Missing | Models measured table and no-reread statement |
| 2: M3 Glimmer kit 1.6.5, four depths, no rereads, 12 deltas and slot size | Missing | Models measured table, slot-size observation |
| 2: M5 Max64 depth/parallel, swap exclusion, tensor-use unknown | Covered | Retain; Sergey's M5 kit 1.6.6 sweep remains pending if mentioned |
| 3: 27B CUDA exact same partition, PR9 import costs | Covered | Retain historical pre-import-speed-v2 label |
| 3: first 5G call, components/wire, uncalibrated cross-backend | Covered | Retain exact observation; no optimization applied to that time |
| 3: stock CUDA-to-Metal deep slots / YaRN | Covered | Retain, separate from prototype and quality |
| 3: final-only fixed state, local bypass, CPU import, CommonCrypto | Measurements covered; merge status obsolete | Appendix names landed PR14/15/16 and main 9348ecd6 |
| 3: PR15 CUDA import costs | No post-PR15 CUDA numbers occur in the supplied FACTS revision | Explicit evidence gap; do not relabel PR9/CPU numbers; source requested |
| 3: 784/31,360-token bridge and B300 node smoke | Covered | Retain; B300 exact reviewed-head timing distinguished |
| 3: exact landed 9348ecd6 PRO 6000 vLLM re-smoke | Missing | Server adds 8k/32k, TTFT, chunk endpoints, exact-repeat and exit-5 qualifications |
| 3: stage-2 KL study, BF16 reference, 20 documents / 40,960 positions | Missing, KL study pending | Limitations table, client-weight conclusion, node-precision bound; stage3 omitted |
| 3: heterogeneous Q8-node/Q4-client eval5-eval7 | Missing, marked pending | Limitations correct/disagreement counts, finite coverage, no 128k claim |
| 3: homogeneous 48-case pilot / partial 128k | Covered | Retain; remove obsolete heterogeneous-pending sentence |
| 3: Mirai exact transfer / source-port match | Covered; KL pending obsolete | Appendix points to measured stage2 |
| 3: SWA reread causes / CPU fix | Covered; GPU pending obsolete | Models updates GPU exact same-partition result from swa7 supplement |
| 4: Sonnet cache price and Gemma full-KV geometry | Covered in engine/text | Retain dated inputs; no live price claim |
| 5: KL, task pilots, GPU/Mac SWA, B300, bridge pending list | Superseded by measurements above | Remove corresponding current pending statements |
| 5: CUDA-to-Metal calibration, optimized 5G rerun, Bonsai ladder | Still unmeasured | Retain bounded pending/future status |
| 6: split point, speculative decode, SSD experts, NVFP4, attestation, 300 cases, gigabit | Covered as future work | Retain, no claimed measurement |

## Supplemental owner evidence and growing-session gaps

`/home/agent/lanes/hybrid/NOTES.md`, 2026-11-02 entries, records swa7 at
`03f1b4ff`: Glimmer, Gemma and Qwen chunked transfer exact on the same
partition, and landed PR14 `683caeed`, PR15 `3ac1503d`, PR16 `9348ecd6`.
FACTS already contains the exact-head PRO 6000 smoke. These records describe
observations, not an independent reproduction by this writer.

Growing-session source: owner brief plus
`/home/agent/Werkstatt/hybrid-b/llama.cpp/.temp/hybrid-b-r36-261102/worktree/tools/hybrid-bench/RESULTS-hybrid-b-r36-261102.md`
(r39/r41/r42 sections), and the r41 owner gate brief. Append preserves old
client attention-KV rows, imports only the node's new range and recurrent state;
CHAIN-H replay is exact. Ten exact controls and state/token/hash/rollback
integrity are mandatory; L-H teacher-forced top-1 >=63/64 is the sanity gate;
KL, free-running divergence and fidelity flags are report-only. Full attention-KV
refresh costs 34,816 B/token, or 3,481,600,000 B at 100,000 tokens (3.48 GB,
decimal), before other state/framing. A one-PRO-6000 rehearsal is functional
only. CUDA-to-Metal growing-session latency, wire, import, correctness and
recovery results remain visibly pending, without fabricated numeric values.

## Implementation and validation record

Task-local logs: `.temp/hybrid-c-r15-261102/`. Every gate is a standalone
process, stdout/stderr redirected directly, with actual exit and timestamps in
its result record. Environment: CPU-only, disk TMPDIR, Python bytecode disabled.
Free disk must remain above 28 GB. Final commands, controls and limits follow.
## Gate migration and failed controls

- `range-01` and `range-02` exited 1. The first found unchanged M3-dependent s50 prose/table cells and traffic
  figures. The second found a new lexical collision: the source-derived egress amount $150 coincides with an
  economics figure. The wording was corrected from exact r15 rows; one exact line-bound collision is declared,
  and new offload traffic guards independently recompute volume and both egress endpoints. `range-03` exited 0.
- First spacing invocation exited 1 on the actual glued rc.2/README prose. Whitespace-only repair plus explicit
  whole technical tokens made `spacing-02`/`spacing-03` exit 0. The rc.2 section retains every non-whitespace byte.
- `pdf-01` exited 2 because the cached TeX bundle lacks cmsy5.pfb for the mathematical superscript dagger.
  The text dagger uses the existing PT Serif and keeps its explanation inside the floating table. No package download.
- `engine-suite-01` runs the prior r14 preservation contracts against the authorized changed v3 text/source.
  The original reviewed-paper and r14-producer snapshots remain byte-identical in the verified fixture store.
  Their finite before/after migrations are enumerated and pinned separately; original test names, assertions for
  every unchanged file, all historical exports and historical adapters remain. Current byte/numeric guards cover v3.
- The r15 historical-export adapter reads the existing r13/r14 verified fixtures instead of private git objects.
  R14 generator hashes likewise come from the existing r14-producer source fixture. No old fixture is re-blessed.
- The FACTS revision used has SHA-256 0e6d9d74652c12984851e0439c83e5e9e6b10651766b88a522acbdd218b91c79.
  It contains no post-PR15 CUDA import measurement. The source was requested; no value is invented.

## Finite negative evidence

| Named plant | Contract discriminated | Named failing assertion/test | Surviving bound |
| --- | --- | --- | --- |
| from2.6 / 2.4times / gain1.57 / Ultra25.9 / 36.6is / all110run14 | Prose needs letter/number spaces on all three publication surfaces | test_glued_letter_number_plant_and_clean_control | Finite tokens; legitimate whole technical tokens explicitly pass |
| B300shows / Q4and64 / 8kcalls / M3gain1 | A legitimate technical substring cannot excuse an attached ordinary word | test_technical_substring_does_not_exempt_glued_prose | Code/link syntax and model grammar remain explicit limits |
| six_row_removed / six_dagger_removed | The six-agent row stays visible and flagged | test_six_agent_row_is_retained_flagged_and_excluded | The test checks this row/marker, not statistical trend fitting software |
| six_false_measurement / six_trend_exclusion_removed | Held rate cannot be called measured or enter reported agent-count ratios | test_six_agent_row_is_retained_flagged_and_excluded | Printed ratios independently checked by test_capacity_ratio_and_zone_claims_match_engine |
| Each current offload phrase has its first digit changed, or wording replaced | Every retained and new named claim must stay at its named site | offload_bound.py --self-test | Literal finite sites, not arbitrary semantic equivalence |
| Every range/direction site is perturbed | Retained economics quantities and directions match source rows | check_ranges.py --self-test | Finite registered forms and explicitly declared lexical collisions |

These are executable negative plants, not a claim of exhaustive mutation coverage. No unexecuted mutant is credited.

The completed first engine suite ran 368 tests in 597.589 seconds, exit **1**:
54 subtest failures are confined to the two historical byte-preservation tests
(49 reviewed-paper files and five r14 engine-source files). No other test failed.
The explicit migration record is `calc/tests/data/paper-v3-migration.json`,
independently pinned in `publication_v2.py`; unchanged files still compare exact bytes.
The r15 generator/input/export bytes are untouched. Only test/audit content I/O
and current-publication gates change outside the paper/data/documentation scope.

`v3-focused-02` exited **1** because numeric-site pins had not yet been refreshed
following the typography/prose edits. Refreshing the authorized current pins,
without altering old fixtures, resolves this failure. `v3-focused-03` ran
25 tests, exit **0**, including actual release-note CLI plant exit **1** and
clean CLI control exit **0**. `pdf-02` exited **2** for a second uncached math font,
cmsy8.pfb in the KL floor cell. Plain scientific notation retains exactly 1.6e-7
without that font. `pdf-03` exits **0**; no overfull boxes, undefined references
or missing characters. Underfull-box warnings remain. No visual PDF renderer
is installed; the compiler log is the layout check, and the owner reads the PDF.

The subsequent final engine run and final gate records are appended after completion.

## Final accepted local gate evidence

The full second engine suite at signed source `27a420c299035476ec98e9a519731873d90c2021`
ran **369 tests in 481.965 seconds**, exit **0** (2026-11-02 11:39:06–11:47:10 UTC).
The matching kit run passed **24 tests**, exit **0**. All full-suite assertions,
reviewer tests and immutable fixtures are retained; the fixtures' manifest and 821
content objects are unchanged.

A subsequent editorial delta removes obsolete pending-heterogeneous-pilot sentences
from the abstract, introduction and conclusion, fixes outlook cross-references,
and explains client-backend gate identifiers. It changes no engine/input/export,
kit or derived CSV bytes. Current byte/site and explicit historical-delta pins are
refreshed. All affected current-publication consumers were identified by their
imports and paper reads: six publication/history/spacing regression modules and
three current-publication methods of Run13Tests. Their **47 tests** passed, exit
**0** in `publication-regressions-final-01.log`. This reuses the unchanged engine
and kit evidence instead of claiming a second full suite at the editorial successor.
The two old preservation test names stay; the exact final deltas enumerate 51
reviewed-paper files and five r14 producer source files. All other historical files
still compare byte-for-byte. No scientific tolerance or assertion is relaxed.

| Gate / exact standalone command | Actual exit | Evidence in task log directory |
| --- | ---: | --- |
| `python3 -B -m unittest discover -s calc/tests -v` | 0 | engine-suite-02.log/json; 369 tests at 27a420c |
| `python3 -B -m unittest discover -s bench/tests -v` | 0 | kit-suite-02.log/json; 24 tests |
| Affected publication regressions (exact unittest argv in JSON) | 0 | publication-regressions-final-01.log/json; 47 tests after editorial delta |
| `python3 -B paper/data/check_ranges.py` | 0 | range-final-02.log/json |
| `python3 -B paper/data/check_ranges.py --self-test` | 0 | range-self-final-02.log/json; 156 retained named sites plus table/direction controls |
| `python3 -B paper/data/offload_bound.py` | 0 | offload-final-02.log/json |
| `python3 -B paper/data/offload_bound.py --self-test` | 0 | offload-self-final-02.log/json; all retained names and new v3 controls |
| `python3 -B calc/tests/publication_v2.py` | 0 | publication-final-02.log/json; exact snapshot, byte/numeric pins and five recomputed figures |
| `python3 -B calc/tests/r13_ledger.py` | 0 | publication-ledger-final-02.log/json |
| `python3 -B .scripts/publication_spacing.py --release-notes .temp/hybrid-c-r15-261102/release-notes.rc2.md` | 0 | release-notes-spacing-final-01.log/json; six surfaces/sections |
| `bash .scripts/test-release.sh` | 0 | release-fixtures-final-01.log/json; 46 release/version fixtures and 12 signer controls |
| `python3 -B calc/tests/history_fixtures.py` | 0 | history-integrity-01.log/json; 13 snapshots / 821 objects |
| `make pdf TECTONIC="$PWD/.temp/hybrid-c-r15-261102/tectonic-cached"` | 0 | pdf-04.log/json; final successor build recorded as pdf-final-01 |
| `make manifest` and `sha256sum -c MANIFEST.sha256` | 0 / 0 | manifest-01 and manifest-verify-01; final documentation successor repeated below in final logs |
| `git -c core.whitespace=cr-at-eol diff --check 27c51fea..HEAD` | 0 | whitespace-base-01.log; covers the actual full delta, unlike the earlier empty unstaged check |
| `git verify-commit` for all five commits introduced above rc.2 | 0 each | signatures-01.json/log; final successor verified separately |

`producer-custody-01.json` compares 613 export/report/measurement files with exact
engine head 04755721: zero mismatches. The writer changes only the two historical
I/O adapters outside current publication gates; generator/input/output values stay
exact. The r15 ledger remains 8,804 rows / 8,301 changed cells with unique expired
coordinates and its retained single-cell-deletion witness. No audit command that
rewrites the producer ledger was run in the writer checkout.

One notes-extraction helper omitted the requested Python environment setting and
created `.scripts/__pycache__/publication_spacing.cpython-314.pyc`. The exact
owned file was hash-recorded and removed; `bytecode-correction-01.json` records
the correction. All gate environments set `PYTHONDONTWRITEBYTECODE=1`, disk TMPDIR,
and use `-B`. No download, native build, project tag or push occurred.
The smallest observed free-space sample across gate records is **31,901,827,072 B**
(first full engine run), above 28 GB. This is sampled evidence, not a claim about
other sessions' activity. Engine r15's own report separately retains its earlier
producer resource-control failure; this writer does not erase that history.

## Remaining gaps and handoff

- Growing-session CUDA-to-Metal on the owner's M3 Max: visible pending block, no measured result claimed.
- CUDA-to-Metal BF16 calibration, attack/noise separation and optimized 5G rerun: still pending.
- Sergey's M5 Max kit 1.6.6 sweep: no measurement imported; stays pending in the evidence ledger.
- Post-PR15 CUDA import timings: absent from FACTS SHA-256 0e6d9d74652c12984851e0439c83e5e9e6b10651766b88a522acbdd218b91c79;
  source requested, no number invented. PR9 and CPU observations remain explicitly historical.
- KL stage3 was stopped; no stage3 result is reported. Larger task evaluation and Bonsai ladder remain future work.
- Independent integrated-paper review and owner publication remain outside this local no-push/no-tag handoff.

Owner PDF: `.temp/hybrid-c-r15-261102/hybrid-inference-v3-draft.ru.pdf`.
The final signed successor changes only this validation narrative, manifest and
editorial/publication scope listed above; executable scientific inputs and outputs
retain the green engine/kit identities. Status: ready for review.

## R16 review corrections: hybrid-c-r16-261102

The complete Muse r5o review at
`/home/agent/Werkstatt/hybrid-review/paper/.temp/REVIEW-paper-v3-muse.md`
requests corrections to signed `cb07bea310b451129bd7aedafd5a0bbe3981f9f5`.
This task retains `paper-v3`, makes signed local commits only and creates no tag
or push. CPU only, no downloads or native builds. Python bytecode is disabled;
TMPDIR is `.temp/hybrid-c-r16-261102/tmp` on disk. The free-disk floor is 28 GB.
No project board exists (`goal-01.log`, exit 1); the existing `.temp/tasks.md`
tracks the work. No applicable installed/project skill was found. The brief has
no attack-surface table; the finite controls below do not claim complete surface
coverage. No requested correction is out of contract. All prior reviewer tests
and immutable historical fixtures remain under their original names.

### F1 and the whole-text sweep

The transcript paragraph now prints 7.9 minutes writing the summary, 10.3 minutes
for the hybrid task and 19.4 minutes locally. Three new source-derived sites are
`run15 transcript prose summary minutes`, `run15 transcript prose hybrid total minutes`
and `run15 transcript prose local total minutes`. They divide the full engine
seconds by 60 and round once to one decimal. The source is the M3 Max / 1000 Mbit/s
row of `paper/data/engine/transcript_example.csv`: 474.22071187316874,
615.3003731190606 and 1161.5050145788764 seconds. Existing table values are unchanged.

The sweep covers all 19 authored TeX files, including the abstract, captions,
conclusion and appendix. It compares all 8,440 changed finite numeric ledger rows
from the 8,804-row `ENGINE-QUOTES-R15-261102.csv` at fixed precisions 0–4; it also
checks seconds as minutes and fractions as percentages. TeX thousands separators
are normalized. Table cells and plotting environments are outside this prose
inventory and remain covered by their publication checkers. The task-local
`sweep.py` preserves the complete candidate records, source keys and context in
`sweep-candidates-before.json` and `sweep-candidates-after.json`. The before scan
is from exact cb07bea3 via read-only git object reads; the after scan is from the
corrected sources. Both scans see 1,302 numeric occurrences outside those environments.
There are 674 lexical old-value candidates before and 671 after. These are
collisions with any changed ledger row, not 674 stale scientific claims.

Semantic review of those candidates, the ledger's 19 explicit prose mappings,
and the number-word claims found **three stale numbers, all in F1; zero additional
stale prose claims; zero stale claims remaining after correction**. In particular:

| Candidate class / sites | Disposition and evidence |
| --- | --- |
| Transcript 6.9 / 9.2 / 18.3 minutes | Replaced with 7.9 / 10.3 / 19.4; three named sites and old-value plants |
| Historical M3 8.44 / 13.2 / 14.05, introduction 1.56 | Retained measured request-time/interval observations, not the cooled base. The workload caption names the initial measurement; clients explicitly labels the historical rows. The 1.56 uses request-time 13.1596888121 / 8.4409465398; it is not the new aggregate ratio |
| Transcript 11.5 and 2.4 minutes | Correct current rounding; not stale. The source table and its existing computed site verify them |
| Current day capacity, zone shares, traffic, cost ranges, agent ratios and conclusion gain | Already r15: 3.54 / 5.66 / 1.60; 656 calls / 1.66 TB / USD 8, 83, 150 / USD 81; 1.72 / 1.90 / 2.03 and 2.20 / 2.62 / 2.95. Retained checker sites recompute or pin these claims |
| M5/Ultra, GLM, symmetric fleets, measured server/bridge/SWA/KL observations | Retained own source rows or finite measurements. Sharing a spelling with another changed M3-dependent ledger cell does not change these values; range, offload and exact-publication guards remain active |
| Corpus, depths, rates' denominators, geometry, prices, dates, counts, versions and font/TeX settings | Unchanged independent inputs or technical tokens; common small-integer collisions are not changed-output claims |
| Ledger's derived 512-token answer time, old bandwidth-share wording, four-M3 number-word claim | Old answer-time wording is absent; bandwidth prose already says cooled 24.03 / 8.77 and about 37%; the academic-capacity statement already uses current source arithmetic |

This is a lexical inventory plus manual source/context review, with explicit
historical distinctions. It does not claim automated semantic equivalence for
arbitrary rewritten equations. No producer quote ledger is rewritten by the sweep.

### F2 punctuation and N1 rounding

Seven spaces were inserted in the rc.2 changelog section, including both price
thresholds. The rc.2 non-whitespace equality regression stays green. The expanded
spacing guard additionally found `bridge,48-case` in README; one space repairs it.
It rejects `%` followed by a letter (including Cyrillic), and prose `:`/`,`
followed by a digit. Whole numeric times, ratios and thousands groups are exempt;
attached prose cannot use a numeric prefix as an exemption. Version strings,
Markdown code/link syntax and the existing technical-token grammar remain valid.

Measured values are rounded once from the engine CSV to the printed precision.
The cooled 32k / 8- and 12-stream cells are 33.39 and 38.46. The three cooled row
sites keep their original names and now derive all 22 cells directly from full
`parallel_anchors.csv` values rather than FACTS transcriptions. The rounding rule
is stated in the table caption and README. The independent task-local
`rounding_audit.py` checks all **43 printed parallel-table cells** against current
or explicitly historical sources, using the request-time denominator for 13.2.
The baseline has exactly the two reported mismatches; the corrected table has
zero. `rounding-audit-02.log` exits 0; per-cell source values are in
`rounding-audit-01.json`. No other rounding-step correction was found. FACTS was
read only; its owner already corrected the two cells and states the same rule.
SWA and KL observations have no corresponding changed engine CSV and retain their
measured FACTS precision. Existing computed client/agent/channel table sites keep
their direct source rounding.

### Finite negative evidence and limits

| Named plant | What it narrows the gate to | Named failing test / site | Surviving bound |
| --- | --- | --- | --- |
| transcript_old_summary minutes (6.9) | Correct prose even when the table remains correct | test_transcript_prose_old_minutes_rejected / run15 transcript prose summary minutes | Literal paragraph site, one-decimal minutes |
| transcript_old_hybrid total minutes (9.2) | Same invariant for the whole hybrid task | test_transcript_prose_old_minutes_rejected / run15 transcript prose hybrid total minutes | Same finite source row |
| transcript_old_local total minutes (18.3) | Same invariant for the local total | test_transcript_prose_old_minutes_rejected / run15 transcript prose local total minutes | Same finite source row |
| double_round_33.40 / double_round_38.47 | Full CSV precision is rounded once | test_measured_parallel_cells_round_csv_once / run15 cooled anchor 0 | All 22 cooled cells checked; no claim about unprinted measurements |
| percent_letter_33_is (`33%is`) | Percent/word punctuation glue | test_punctuation_glue_cli_plants_and_clean_control | Real generated-note CLI exits 1 for the named punctuation reason; repaired file exits 0 |
| comma_digit_treatment (`treatment,4/48`) | Comma/digit punctuation glue | test_punctuation_glue_cli_plants_and_clean_control | Same CLI and no-file-mutation check |
| colon_digit_modelled (`modelled:77.7%`) | Colon/digit punctuation glue | test_punctuation_glue_cli_plants_and_clean_control | Same CLI and clean control |
| percent_colon_digit / comma_list / percent_cyrillic | Threshold colon, ungrouped numeric list and Cyrillic word variants | test_punctuation_glue_cli_plants_and_clean_control | Finite examples; code/link syntax remains excluded |
| 10:12Zshows / 1:1gain / 8,301calls | Numeric-form exemptions cannot hide an attached word | test_legitimate_punctuation_and_attached_word_boundary | Whole clean 10:12Z / 1:1 / versions / 8,301 pass |

All listed negative plants are applied and rejected by the intended assertion;
no survivor is credited as killed. `regression-after-02.log` runs all 13 spacing
and v3 tests, exit 0. The initial pre-fix run exited 1; its parallel-row parser
also had a setup error on an empty cell, which is not negative evidence and was
corrected to split/strip individual ampersand cells. The first post-fix run exited
1 on the real README glue; the final focused run passes after its whitespace repair.
The first supplementary rounding audit exited 1 because it also selected the daily
client table; restricting it to `tab:parallel-decode` gives the 43-cell green audit.
The first ledger exploration exited 1 on a prose key without a CSV-row separator;
the corrected sweep handles those 19 prose rows explicitly.

Publication byte/site pins and the exact historical-delta record are refreshed
only for the authorized changed current files. Historical `before` hashes,
fixtures, exports, measurements and quote-ledger bytes are preserved. Rework is
bounded to the paper and its publication guard/tests/docs; no engine or kit
implementation changes. The external spacing helper is used only by this repo,
so its source correction is in `.scripts/publication_spacing.py`.

### R16 gate record

Gate commands, actual exits, process IDs, timestamps, log digests and sampled
free disk are captured in `.temp/hybrid-c-r16-261102/<gate>.json` beside each
standalone log. Gate output is redirected directly without a pipe or tee.
Full engine, kit, checkers/self-tests, publication/spacing/release guards,
cache-only PDF and manifest results are recorded below.
The absence of a visual PDF renderer remains a limit; the compiler log and owner
PDF read are the available layout checks. Pending hardware/quality experiments
in the earlier gap map remain pending. Independent review is the next handoff.

The number-word inventory contains 496 occurrences across the same 19 files
(`number-word-inventory-01.json`); the gain/answer-time/capacity word claims are
included in the semantic review above. FACTS readback SHA-256 is
`82e52b44bdc494b27e885b550660c5faa6bf88e8cd89543177ae1972adf7e602`.
The auxiliary inventory first used a nonexistent helper name; the corrected
`r13_reverse.number_words` call succeeds without changing any source.


The full engine suite ran at clean signed source
`1814ad50a1a183b9cc2ed43dc41e362442ccc218`: **373 tests in 469.837 s, exit 0**,
2026-11-02 12:26:03–12:33:56 UTC (wrapper observation times). The kit passed
**24 tests in 18.620 s, exit 0**. All 13 spacing/v3 tests, including the three
old-minute plants, both double-rounding plants and six real punctuation CLI
plants, are included in that exact full suite. The corrected current-publication
consumer subset also passed 100 tests (`focused-01`, exit 0) before the commit.

| Standalone command | Actual exit | Task-local evidence |
| --- | ---: | --- |
| `python3 -B -m unittest discover -s calc/tests -v` | 0 | engine-01.log/json; 373 tests at 1814ad50 |
| `python3 -B -m unittest discover -s bench/tests -v` | 0 | kit-01.log/json; 24 tests |
| `python3 -B paper/data/check_ranges.py` | 0 | range-01.log/json |
| `python3 -B paper/data/check_ranges.py --self-test` | 0 | range-self-01.log/json; 156 site controls plus table/direction/collision controls |
| `python3 -B paper/data/offload_bound.py` | 0 | offload-01.log/json |
| `python3 -B paper/data/offload_bound.py --self-test` | 0 | offload-self-01.log/json; 182 named controls including the three new prose sites |
| `python3 -B calc/tests/publication_v2.py` | 0 | publication-01.log/json; 2240 numbers / 114 files |
| `python3 -B calc/tests/r13_ledger.py` | 0 | ledger-01.log/json |
| `python3 -B .scripts/publication_spacing.py` | 0 | spacing-01.log/json; five surfaces/sections, zero violations |
| `bash .scripts/test-release.sh` | 0 | release-01.log/json; 46 release and 12 signer controls |
| `python3 -B calc/tests/history_fixtures.py` | 0 | history-01.log/json; 13 snapshots / 821 objects |
| `make pdf TECTONIC="$PWD/.temp/hybrid-c-r16-261102/tectonic-cached"` | 0 | pdf-01.log/json at 1814ad50; XDG_CACHE_HOME=/home/agent/.cache; only cached resources |
| `make manifest` / `sha256sum -c MANIFEST.sha256` | 0 / 0 | manifest-01 and manifest-verify-01.log/json; final documentation successor refreshed separately |
| `git -c core.whitespace=cr-at-eol diff --check` | 0 | whitespace-01.log; final range check recorded with delivery |
| `git verify-commit HEAD` | 0 | signature-01.log; host identity, signature G and requested Codex trailer |

The PDF compiler reports **28 pages**, no overfull boxes, no undefined references
and no missing characters; existing underfull warnings remain. No visual renderer
is installed, as verified in `pdf-reader-readiness-01.log`; visual inspection is
not claimed. The final exact-head rebuild and requested owner copy
`.temp/hybrid-c-r16-261102/hybrid-inference-v3-draft.ru.pdf` are bound by SHA-256,
head and timestamp in `delivery-01.json`, with standalone `pdf-final-01` evidence.

The evidence-only successor changes this gap map and the repository manifest.
All executable source, tests, configuration, publication inputs and measured
payloads retain the green 1814ad50 identity; final diff and hash readback verify
that fact. The complete suite is not claimed as rerun at that documentation-only
successor. Its changed build version is covered by the exact-head PDF rebuild.
`custody-01.json` verifies all 1807 protected export, measurement, fixture, kit and
embedded CSV files remain unchanged; the producer quote ledger/report are intact.

The minimum sampled free disk in the required gate receipts is **32,456,613,888 bytes**,
above 28 GB. This is sampled evidence, not a claim about unrelated host activity.
No download, native build, project tag or push occurred. All requested corrections
are ready for independent review; the earlier hardware/quality and owner-visual
limits remain explicit.
