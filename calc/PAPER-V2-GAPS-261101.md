# Paper v2 gap map (2026-11-01)

The r7 evidence below is retained as history. Current migration status and controls are in the final section,
**Run-13 checker migration: hybrid-c-r8-261101**. Earlier blocking/unchanged-checker statements describe r7 only.

Read before prose edits at merge f651d545 (engine 02f4b6fd + public main 3a2ff4fe). Locations below are original source lines. Numeric authority: reviewed ENGINE-QUOTES-R13-261101.csv and calc/out/run13; new measured claims: /home/agent/lanes/hybrid/.temp/paper-v2/FACTS.md (2026-11-01). No new benchmarks are run. This map records planned replacements first; the completion column is updated after each group.

| File / original lines | Existing claim | Evidence / measured status | Change | Completion |
| --- | --- | --- | --- | --- |
| 00-abstract.tex:9-15 | Run11 cost ratios; only M3 measured, CPU 0.8B only, CUDA/Metal and 27B future | R13 ledger; FACTS 1-3: reproduced server, M5, CUDA 27B exact, measured 5G CUDA/Metal | Replace ratios; bounded measured feasibility and quality limits | updated; see final evidence below |
| 01-introduction.tex:12-13,56-58 | B300 at fixed 30% FP8 peak, one second; CPU-only prototype | R13 FP8 14.1-21.1%; B300 remains scaled estimate; FACTS 3 | State depth-dependent effective FLOP fraction, derived timing; update prototype contribution | updated; see final evidence below |
| 02-workload.tex:35-51 | Historical M3 segment run presented without canonical-run distinction | FACTS 2: canonical delta prefill 162-176 to 16.5-20.7, noisy decode | Preserve engine's historical segment anchors; distinguish canonical repeated-delta measurements in clients | updated; see final evidence below |
| 03-architecture.tex:7-14,88-99 | KV/state wire formula; heterogeneous quality unmeasured | FACTS 3: chunk state repetition measured, last-chunk fix CPU-only; KL/task studies pending | Retain analytical wire model and heterogeneous caution; explain actual chunk overhead in channel, pending quality in limitations | updated; see final evidence below |
| 04-channel.tex:11-102,125-128 | Run11 tables, latency and traffic; no real WAN result | R13 ledger; FACTS 3: 39,504 tokens, 5G TTFT and 2,004,023,525 B | Refresh all numeric sites and add measured setup/breakdown/wire accounting; improvement rerun pending | updated; see final evidence below |
| 04-channel.tex:66-79 | M5 Max64 is estimated | FACTS 2 and run13 measured M5 curve | Distinguish measured anchors from modeled task duration | updated; see final evidence below |
| 05-clients.tex:70-102 | All M5 prefill fourfold estimate; no M5 measurements | FACTS 2: M3 canonical and M5 Max64 depth/parallel data; swap exclusion; tensor-unit use unknown | Add measured ladders, provenance bounds; keep other clients estimated; refresh capacity table | updated; see final evidence below |
| 05-clients.tex:36-40 | Million-token Qwen only memory estimate | FACTS 3: stock slot transfer 8x260k and 2x1.04M YaRN | Distinguish operational transfer evidence from unmeasured extended-context quality | updated; see final evidence below |
| 05b-models.tex:26-31,48-55,70-85 | Gemma half-sized full KV; old B300 bound; no SWA qualification status | R13 Gemma 43,520 B/token; FACTS 3: two reread causes, kit pin and CPU compaction fix, GPU pending | Correct table/prose; document SWA status without GPU claim | updated; see final evidence below |
| 06-server.tex:4-10,25-30 | Fixed estimated server envelope and run11 capacity | FACTS 1: off/off reproduction, checkpoint sensitivity, earlier run unexplained; R13 | Refresh model costs/capacity; add measured Q4 curve, FP8 fraction definition and server-only vLLM | updated; see final evidence below |
| 07-economics.tex:7-18,54-153,200-270,314-325 | Run11 economics/capacity, all non-M3 clients estimated | R13 ledger including Sonnet cache correction and measured M5 | Apply all ledger, derived chart and number-word changes; label limits | updated; see final evidence below |
| 08-million.tex:12-14,31-43,69-72 | Run11 B300/GLM extrapolation, no CUDA-to-Metal transfer evidence | R13 ledger; FACTS 3 stock 1.04M transfer | Refresh derived values and retain explicit B300/GLM and quality extrapolation bounds; refer to measured transfer | updated; see final evidence below |
| 09-security.tex:33-38 | Exact comparison only CPU; cross-backend tolerance unmeasured | FACTS 3: CUDA same-partition logit difference 0; CUDA/Metal calibration pending | Add CUDA evidence; retain calibration/attack coverage limits | updated; see final evidence below |
| 10-resilience.tex:1-15 | General availability/switching design | FACTS adds no measured resilience qualification | No new result; preserve design status | reviewed, unchanged |
| 11-limitations.tex:7,19-24,31-33 | CPU-only 0.8B, one measured client, estimated server | FACTS 1-3,5: current evidence and pending studies | Replace stale boundaries; explicit pending study sentences with TODO(data); retain model/queue/quality limits | updated; see final evidence below |
| 12-related.tex:1-33 | Related-work comparisons, heterogeneous quality unconfirmed | FACTS 5: quality still pending | No new comparative conclusion | reviewed, unchanged |
| 13-outlook.tex:4-10,22-25 | M5 first measurements and CUDA/Metal still future; NVFP4 prospective | FACTS 5-6: complete pending and future-work lists | Replace stale next-version list; pending TODOs; list all future directions without claimed results | updated; see final evidence below |
| 14-conclusion.tex:10-19,30-31 | Run11 ratios, general M5 gain, no measured prototype result | R13 ledger; FACTS 3 5G and exact CUDA | Correct ratios/device scope and add bounded empirical conclusion | updated; see final evidence below |
| 90-appendix.tex:48-64 | Feasibility exclusively CPU 0.8B | FACTS 3: CUDA 27B exact at three depths, partition KL, 5G, stock transfer, Mirai and CPU improvements | Replace obsolete feasibility account with measurement boundaries and evidence references | updated; see final evidence below |
| paper/data/engine/SOURCE.txt and *.csv | Run11 snapshot | calc/out/run13/base, same filenames; paired sensitivities retained upstream | Copy exact run13 files and regenerate derived outputs; never alter a checker | updated; see final evidence below |
| README.md, paper/README.md, CHANGELOG.md, UNRESOLVED_QUESTIONS.md | Older tooling/status descriptions, paper README omits third author | Main author/release metadata; measured facts and delivery evidence | Preserve release section, append Unreleased changes and current qualification notes; manifest | updated; see final evidence below |

## Qualification gaps to preserve

- The brief contains no attack-surface table; no mutant coverage map is claimed. Existing checker self-tests and engine/kit negative tests are reused, without changing their contracts.
- All FACTS section 5 items must remain pending until the orchestrator supplies a newer evidence ledger. Expected dates belong to the evidence notes; public pending sentences carry no placeholder numbers.
- Independent review and owner publication occur after this local handoff. No push or tag is authorized.

## Numeric-step findings

The 259 reverse-number ledger rows cover 106 distinct original TeX lines. Applied all of those coordinates without cascading replacements, then applied the six native architecture-table/prose sites and the written-number changes. All 42 embedded CSVs are exact copies of the run13 base; regenerate the derived tables from that snapshot. The 406 number-word occurrences in the engine report were read in source context: changed twenty-person GPU counts (one/fourteen -> two/sixteen), M5 fourfold estimate -> measured 2.00-2.86 for Max64 only, payback year/one-and-a-half years -> 13/21 months, server two-dozen-user estimate -> thirteen. Unchanged words denote workload scale, model geometry, memory fit, historical measurements, explicit assumptions or reference/layout identifiers. The obsolete CPU-only and four-future-measurements passages are replaced in the prose groups, not promoted to new measurements. Existing quarter-calendar, half-million memory and million-token quality qualifications remain bounded estimates.

Two semantic errors in the supplied quote ledger were caught rather than copied: the replacement for storage versus compute retained "more" despite $6.9 < $10.0; the text now gives the two costs without that comparison. Four-session GLM/API savings now round to 3.3-3.6, so "almost four times" is removed. The 1.9-1.9 rounded interval is written as 1.9.

### Blocking checker contract conflict

Unchanged `paper/data/offload_bound.py`, `server_rate()`, line 24, asserts a single rate in turn_speedup.csv before examining any prose. Exact R13 data contains 656774382251202.1 and 736610013430563.9 FLOP/s; exit 1 is unavoidable by text editing. Choosing either constant, modifying the snapshot or changing the checker would violate this task. Log: `.temp/paper-v2-261101/offload-01.log`.

Unchanged `paper/data/check_ranges.py` computes the new values but requires the historical directions `storage dearer than prefill` and `four sessions a day almost four times below the API`; both return `NO LONGER HOLDS`. Its guard also uses literal old allowlist values and cannot distinguish new coincident rounded values. `check-ranges-01.log` exits 1. Initial payback mismatches in that run were because derived CSVs were still old; regenerated immediately afterward. The direction and constant-rate failures are structural and are not cured by regeneration.

Clean alternatives: keep checkers unchanged and hand off the corrected paper with these explicit blocking failures; or obtain explicit owner authorization for a separate run13 checker migration with negative controls. No checker is edited. Clarification requested while independent text work continues.


## Prose completion and evidence boundaries

All sections were read before editing; unchanged resilience and related-work claims received no new numeric conclusions.
The text now distinguishes CUDA same-partition bit equivalence, CUDA-to-Metal operational transfer with uncalibrated
quality, stock deep-slot restore, and CPU-only optimization deltas. The 5G call retains its original wire cost and
all three timing components; CPU optimizations are not applied to that measured WAN time. Public model estimates
retain their original historical M3 anchors; canonical M3 deltas are presented separately. Only M5 Max64 is newly
measured; other M5 variants remain estimates. Server FP8 is explicitly server-only, and B300/GLM portability remains
estimated. The complete pending list and expected dates are in UNRESOLVED_QUESTIONS.md, with one adjacent TODO(data)
for each public pending item. The original number-word checklist is adjudicated in PAPER-V2-NUMBER-WORDS-261101.md.

New measurement authority is FACTS.md sections 1-3: server raw archives fd0bc08c/e80d4240/92828a6c and earlier9accab80;
M5 c7ceab57; canonical M3 13bff62f; prototype landed CUDA proof f65c5948 (PR9), Mirai PR11, local-bypass PR12,
CommonCrypto PR7. Original archives/provenance for server and M5 are already retained under data/measurements/.
For canonical M3, WAN and prototype results, this task relies on the orchestrator's evidence ledger; no additional
raw archive is imported and no independent reproduction is claimed.

Additional test-boundary conflict found by source inspection: test_run13.py contains an explicit invariant that
all publication TeX remains byte-identical to c04a99d, plus line-bound tests requiring the old 19--22 text. These
engine-producer preservation guards are incompatible with this authorized paper-update task. They are retained
under their original names; the full engine suite is run and any resulting failures remain blocking.

First PDF invocation put -C before -X and failed with make exit2 before TeX. Corrected invocation uses a temporary
wrapper passing --only-cached to `tectonic -X compile`, as required by the compiler's help; no downloads occur.
The second make invocation exited0 and built the PDF. Initial whitespace check exited2 on generator-owned CRLF
CSV endings; `git -c core.whitespace=cr-at-eol diff --check` validates unchanged CSV convention without rewriting
snapshot bytes. First a2a progress attempt used unsupported kind=progress (exit2); corrected kind=notice succeeded,
event $j3YnJGn24Tc5sav3C8zcaFf7DVHUytJ-F7qBb6J25UY.


## Verification record

Commands below run with `PYTHONDONTWRITEBYTECODE=1` and disk-backed
`TMPDIR=$PWD/.temp/paper-v2-261101/tmp`. Logs are complete local artifacts; stdout/stderr are redirected directly,
without a pipe or `tee`. A nonzero result remains a failed gate even when its obsolete assumption is identified.

| Command / claim | Exit | Evidence |
| --- | ---: | --- |
| `python3 paper/data/derive_charts.py` | 0 | derive-02.log; all four produced tables equal calc/out/run13/paper-derived |
| `python3 paper/data/arch_compare.py` | 0 | arch-02.log; corrected native Gemma geometry/table |
| `python3 paper/data/year_bill.py paper/data/owner-model-usage-2026-10-30.json` | 0 | regenerated summary and year-bill.csv; historical/current Sonnet prices already present |
| `python3 paper/data/year_bill.py --self-test` | 0 | year-bill-self-01.log; current positive and forbidden-accounting controls pass |
| `python3 paper/data/check_ranges.py` | 1 | check-ranges-04.log; obsolete direction/wording/allowlist failures, not waived |
| `python3 paper/data/check_ranges.py --self-test` | 1 | check-ranges-self-02.log; cannot plant the now-false storage-direction phrase |
| `python3 paper/data/offload_bound.py` | 1 | offload-02.log; constant-rate assertion fails before TeX inspection |
| `python3 paper/data/offload_bound.py --self-test` | 1 | offload-self-01.log; same structural assertion, no successful control plant claimed |
| `python3 -m unittest discover -s bench/tests` | 0 | kit-tests-01.log; 24 tests in 26.029 s |
| `python3 -m unittest discover -s calc/tests` (initial diagnostic) | 1 | engine-tests-01.log; 276 tests, 7 failures and 2 missing-object errors; historical object restored before final rerun |
| `make pdf TECTONIC=$PWD/.temp/paper-v2-261101/tectonic-cached` | 0 | pdf-04.log; Tectonic 0.17.0, cache-only, 24-page PDF, underfull-box warnings; no overfull boxes, missing glyphs or undefined references |
| `sha256sum -c MANIFEST.sha256` (56555ce manifest) | 0 | manifest-verify-01.log; repeated after final manifest refresh |
| `git -c core.whitespace=cr-at-eol diff --check` | 0 | CRLF follows the existing CSV generator; no snapshot normalization |
| Style grep and manual sentence review | 0 | style-review-03.log; excludes TeX drawing operators, missing-data table markers and math subtraction |
| Exact snapshot and derived-output comparison | 0 | source-identity-01.json; 42 CSVs byte-identical; four derived tables cell-identical |
| Retained checker/engine/kit scope | 0 | `git diff --exit-code 02f4b6fd HEAD -- paper/data/check_ranges.py paper/data/offload_bound.py calc/tests calc/hybridcalc bench` |

The final engine rerun is recorded below. Manifest/signature readback follows the final documentation commit in the task-local logs. No property suite is
reported green while its required command fails. No attack-surface table was supplied; out-of-contract work includes
new GPU execution, downloads, native builds, new model-quality conclusions, queue/storage qualification, checker
migration, remote publication and tagging. These follow the task's CPU-only, evidence-only, no-checker-change,
no-push and no-tag clauses. There is no rework-module expansion; all authored changes are paper/data, paper/sections,
review documentation, README/changelog and manifest.


### Final engine suite, unchanged publication guards retained

Final source head for executable/text verification: `0b792352787d7082877c5f37ffefd47001f9980a`.
The complete second run of `python3 -m unittest discover -s calc/tests` exited **1**:
**276 tests in 346.354 s, 9 failures, no errors**. Complete output: `.temp/paper-v2-261101/engine-tests-02.log`.
The prior missing-object errors are resolved by fetching the already existing historical a57db67 object from the
local engine workbench. The workbench was not edited. No tests are deleted, renamed, skipped, patched or blessed.

| Failing test | Actual remaining contract |
| --- | --- |
| `test_exact_printed_site_omission_is_rejected` | Original line-bound native collision inventory must remain used after the prose is moved/updated |
| `test_paper_ledger_waivers_are_site_bound` | Original line-bound native collision inventory must remain used |
| `test_reverse_guard_rejects_copied_non_arch_changed_values` | Original line-bound native collision inventory must remain used |
| `test_reverse_inventory_spans_exports_and_keys` | Original line-bound native collision inventory must remain used |
| `test_all_design_csv_bytes_unchanged` | Run12's guard freezes the entire historical paper subtree as well as engine CSVs |
| `test_measured_export_cannot_overwrite_run11` | Same entire-paper freeze, reached before sensitivity export |
| `test_historical_exports_and_paper_text_unchanged` | TeX must remain byte-identical to c04a99d |
| `test_paper_ledger_covers_changed_exports_and_printed_numbers` | Reverse numeric waivers remain tied to old source lines and tokens |
| `test_paper_ledger_omission_controls` | The old changed range 19--22 must still be present, even after its requested replacement by 19--21 |

All inherited engine code, exports (including historical outputs and raw measurement inputs), tests and kit files
are unchanged relative to reviewed engine head 02f4b6fd. This independently distinguishes authorized paper edits
from calculator drift; it does not turn the nine failing tests into passing evidence. The checkers' obsolete
assumptions are the only unresolved acceptance decision. Current tests do not certify the updated paper.

Supplementary client-table inspection checked all eight capacity rows against exact run13 rounding
(`manual-table-review-02.log`, exit0). Its first attempt failed on the historical NVIDIA display-label difference,
not a numeric value; the corrected task-local label mapping is recorded in `.temp/tasks.md`. This inspection
supplements the failed existing paper gates and does not replace them.

The public paper contains no new timing from pending studies. Eleven bounded pending statements and adjacent
TODO(data) comments map to FACTS section5, verified in `pending-map-01.log`; future-work items follow FACTS section6.
The 42 exact snapshot files and four derived tables are verified in `source-identity-01.json`. Negative-test limits
remain explicit: year-bill's existing self-tests pass; offload/range control plants cannot run successfully against
the current contracts, and no mutation-control success is claimed for those failures.

Local tooling: Python 3.14.4, Tectonic 0.17.0, CPU only, disk-backed TMPDIR and bytecode disabled for all validation.
No downloads, installs, native builds, GPU jobs, push or release tag. Observed free space remained above 28 GB.
Only the requested team notices are sent. Independent acceptance, checker-contract resolution and publication
belong to the owner; the candidate is **validation-blocked**, not an accepted delivery.


## Run-13 checker migration: hybrid-c-r8-261101

Owner authorization: migrate the paper workflow to run 13 from r7 head
`a63565ebb0f9004ba2dab01ef26eafc087b08a86`, on `paper-v2`. This supersedes the r7 no-checker-change restriction;
it does not waive a claim, site, tolerance, historical export or provenance gate. CPU only, no downloads or native
builds, disk-backed TMPDIR, bytecode disabled, no push/tag. No attack-surface table was supplied; that remains a
brief gap rather than an implied coverage claim. New GPU execution, publication and all pending qualification
measurements remain out of contract under the user's explicit rules. No new measurement or quality claim is made.

### Changed conclusions and claim directions

| Text location | Before (run 11 / r7 omission) | Run 13 claim and authority | Flag |
| --- | --- | --- | --- |
| 07-economics, storage paragraph | Storage $6.5 > prefill $5.1; r7 omitted the direction | Storage $6.9 < prefill $10.0: storing is cheaper. `person_cost_s20.csv`, M5 Max64 / owned / team50, `hosting_month`, `compute_month`; keys cited in public footnote | conclusion changed |
| 08-million, four sessions, body and conclusion | Almost four times cheaper than API; own-cluster saving 1.4x | API saving 3.3–3.6x and own-cluster saving 1.3x; `glm_utilization.csv`, context1M / teams500,5000 / one user per Studio / 4/day, `api_session/hybrid_session` and `own_cluster_session/hybrid_session`; public key footnote | conclusion changed |
| 08-million and 14-conclusion, full load | API saving 5.4–6.0x, own cluster 2.0–2.1x | API saving 4.8–5.1x, own cluster 1.9x; same table at capacity demand; equal rounded endpoints print once at unchanged 0.1 precision | conclusion changed |
| 08-million, two sessions | Hybrid 29–44% dearer than own cluster | Hybrid 15–30% dearer; `glm_utilization.csv`, `2/day`, teams500,5000 | conclusion changed |
| 08-million, one session | Hybrid 2.5–2.9x dearer than own cluster | Hybrid 1.9–2.4x dearer; `glm_utilization.csv`, `1/day`, teams500,5000 | conclusion changed |
| 05b-models, ideal-client bound | Constant 1.35 PFLOP/s; 22.5x ceiling; 1G/10G bounds 3.4/14x | Depth-specific llama.cpp-derived B300 estimate: 0.72 PFLOP/s at110k; ceiling12.1x; bounds3.0/9x. `measurements/server_fits.csv[phase_a]`, `flop_per_byte.csv`, hardware B300/RTX dense-peak ratio | conclusion changed |
| 06-server, vLLM | 8122/2209 described as cold-prefill measurements | Same numbers explicitly denote fitted 10k-token portion rates at16k/249k, integrated from `vllm_cold.csv[fp8-default].a,b`; cached rates use `vllm_cached.csv.delta_tok_s`; server-only and pending bridge retained | conclusion changed (measurement interpretation) |

The two values in `turn_speedup.csv.server_compute` are depth samples (100k and200k) of the llama.cpp-derived
envelope, not a llama/vLLM pair. The checker verifies **both** against the fit with the original 1e-9 relative
arithmetic tolerance and computes the110k example at its stated depth. vLLM is checked separately in token/s at
all six published cold-fit/cached sites, with `server_only=1`, `client_bridge=0`. No vLLM rate substitutes for
the Q4 client's bound. The raw vLLM JSON's `fitted_delta10000_tok_s` also confirms the interpretation correction.

Range directions and numeric wording are computed from run13, including the exact rounded four-session API ratio.
The old loose verbal “almost four” interval is replaced by the exact computed 0.1-precision endpoints at both
sites; the cheaper-than predicate states the new direction. No numeric tolerance is widened. All previous
value/direction sites remain; the 500-person own-cluster sentence binding follows the sentence r7 split out, and
an additional 5000-person value check is added. Original collision sites stay mandatory: the rent/buy 50-person,
10h, 50%-residual cell changes $34→$48; the 10-person,24h,80%-residual $59 cell and client25.9 sites remain.
The occurrence scan includes those forms even when they cease to collide with a computed range. New collisions
have exact line markers and reasons, never file-wide exemptions. Bare ranges are additionally scanned inside
money forms. The self-test's 1.9x plant is bound to the actual comparison, so another equal scalar in its paragraph
cannot mask a stale claim.

### All nine engine-test targets

The public v2 baseline pins all92 tracked paper files and1619 numeric occurrences. Coordinates include file,
line, spelling, unit, occurrence index and full source-line SHA256; repeated equal numbers are distinct sites.
All TeX is scanned, including untracked new TeX; only generated `paper/version.tex` is excluded as build metadata.
Every current snapshot CSV and all four derived chart inputs are also compared byte-for-byte to run13. The live
range and offload guards are invoked after byte/site checks. Tests never regenerate their expected baseline.

| Test (original name retained) | Old target | New target | Why / retained provenance |
| --- | --- | --- | --- |
| `test_exact_printed_site_omission_is_rejected` | Run11 line78 / 2.7 and old reverse ledger coordinates | Actual v2 04-channel / 1.8 occurrence and all exact v2 coordinates | Reject missing current sites; original coordinate/replacement regression runs unchanged in historical source fixture |
| `test_paper_ledger_waivers_are_site_bound` | Run11 21.6-minute waiver and old line-bound collisions | Same copied 21.6/11.5 values rejected at any new v2 site | No equal number inherits authority; original native-change control retained, historical exceptions untouched |
| `test_reverse_guard_rejects_copied_non_arch_changed_values` | Reverse scan over old publication, including 883/$24.1/etc. | Same forbidden copied forms against current v2 byte/site guard | Current paper is positive control; all former planted forms retained; historical reverse-scope tests run unchanged |
| `test_reverse_inventory_spans_exports_and_keys` | All paired exports plus formula expansion over old publication | Same all-case/key export inventory, immutable old derived bytes, plus current v2 guard | Derived comparison now reads its original local Git object; historical formula-expansion regression also runs unchanged |
| `test_all_design_csv_bytes_unchanged` | 42 design CSVs and entire run11 publication | Same42 design CSVs pinned to a57db67; entire v2 publication pinned separately | Historical export bytes and generator identity are preserved, current publication follows authorized migration |
| `test_measured_export_cannot_overwrite_run11` | Sensitivity export plus run11 publication freeze | Same non-overwrite experiment and historical hashes, plus v2 publication freeze | Namespaced exports and untouched saved artifacts remain required |
| `test_historical_exports_and_paper_text_unchanged` | All R12 exports + TeX identical to c04a99d | Same historical export pin + exact v2 paper bytes/sites | Split the mixed guard; no historical export pin is retargeted |
| `test_paper_ledger_covers_changed_exports_and_printed_numbers` | Old19--22 at line54 and producer dependency ledger | Current19--21 native range and all v2 numeric sites/bytes/claims | Original all-export and formula coverage stays executable at producer source02f4b6fd |
| `test_paper_ledger_omission_controls` | Omit old sentence/table/number dependencies; old native range fixtures | Omit current19--21/6.9/1.8 sites and copy stale19--22/457 at a new site | Current omissions fail; original sentence/table/number omission tests and native fixtures run unchanged in historical source |

`calc/ENGINE-QUOTES-R13-261101.csv`, `r13_numeric_waivers.csv`, all historical exports, measurement inputs,
engine code and kit files remain unchanged. `test_historical_quote_ledger_provenance` uses a local `git archive`
of02f4b6fd, the original ledger and **eight original tests** (all six reverse tests plus two run13 ledger tests),
without rewriting their coordinates or expectations. This is a distinct historical target, not a substitute for
current-publication validation. `r13_ledger.py` now routes its ordinary check to v2; historical audit code remains
available and the source-revision fixture preserves its original entry point.

### Negative controls

Each row below has a clean control against the same source/model identity. Range controls invoke the real named
`check()` path and assert the indicated missing-item verdict; self-test exits0 only when every plant is applied
and rejected and the complete clean publication passes. The engine mutant subprocesses truthfully exit1 with the
named test failure, no setup errors. The outer control harness exits0 after verifying that expected-red result.
No surviving mutant is claimed as killed. These controls prove the listed bounds, not exhaustive mutation coverage.

| Mutant / site | What the gate is narrowed to | Named check that rejects it | Clean control / evidence |
| --- | --- | --- | --- |
| 07-economics.tex :: Одни клиентские машины почти; 2.6--2.9 → 2.6--2.0 | Exact printed value in this scope, unchanged precision | `medium, design` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; 2.1--2.5 → 2.1--2.6 | Exact printed value in this scope, unchanged precision | `medium, conservative` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; 2.1--2.9 → 2.1--2.0 | Exact printed value in this scope, unchanged precision | `medium, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: В закрытом; 2.1--2.9 → 2.1--2.0 | Exact printed value in this scope, unchanged precision | `medium, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; 27--39 → 27--30 | Exact printed value in this scope, unchanged precision | `light at 50 and 5000, design, percent` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; 3--22 → 3--23 | Exact printed value in this scope, unchanged precision | `light at 50 and 5000, conservative, percent` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: По этому правилу на 500 человек; \$34 на человека в месяц против \$46 → \$34 на человека в месяц против \$47 | Exact printed value in this scope, unchanged precision | `light at 500, own against hybrid` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вне этого правила; около \$22 (при осторожной политике \$29) против \$38 у своего кластера на тех же серверах и \$34 на узле B300 → около \$22 (при осторожной политике \$29) против \$38 у своего кластера на тех же серверах и \$34 на узле B301 | Exact printed value in this scope, unchanged precision | `light at 500, outside the rule` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; 22--24 → 22--25 | Exact printed value in this scope, unchanged precision | `heavy saving, design` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; 22--24 → 22--25 | Exact printed value in this scope, unchanged precision | `heavy saving, design` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; 18--22 → 18--23 | Exact printed value in this scope, unchanged precision | `heavy saving, conservative` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; 18--22 → 18--23 | Exact printed value in this scope, unchanged precision | `heavy saving, conservative` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; для команд до 100 человек → для команд до 101 человек | Exact printed value in this scope, unchanged precision | `rule, RTX PRO 6000 limit` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Закрытый контур: всё внутри периметра; для команд до 100 человек → для команд до 101 человек | Exact printed value in this scope, unchanged precision | `rule, RTX PRO 6000 limit` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; для команд до 100 человек → для команд до 101 человек | Exact printed value in this scope, unchanged precision | `rule, RTX PRO 6000 limit` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: В закрытом; для команд до 100 человек → для команд до 101 человек | Exact printed value in this scope, unchanged precision | `rule, RTX PRO 6000 limit` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; узлы B300 начиная с 50 → узлы B300 начиная с 51 | Exact printed value in this scope, unchanged precision | `rule, B300 from (paragraph)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Закрытый контур: всё внутри периметра; узлы B300 для команд от 50 → узлы B300 для команд от 51 | Exact printed value in this scope, unchanged precision | `rule, B300 from (caption)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команде из пяти человек нужн; \$145--506 → \$145--507 | Exact printed value in this scope, unchanged precision | `own server for five people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: пяти человек свой сервер обходится; от \$145 на человека в месяц при лёгкой нагрузке → от \$146 на человека в месяц при лёгкой нагрузке | Exact printed value in this scope, unchanged precision | `own server for five people, light load` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команде из пяти человек нужн; нужна одна такая карта при лёгкой нагрузке и четыре, по две в сервере, при тяжёлой → ПОДМЕНА | Exact printed value in this scope, unchanged precision | `cards for five people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: B300 покупается целиком; \$3\,370 → \$3\,371 | Exact printed value in this scope, unchanged precision | `B300 node per person, five people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команде из пяти человек нужн; \$3\,370 → \$3\,371 | Exact printed value in this scope, unchanged precision | `B300 node per person, five people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команде из двадцати человек нужн; \$63--506 → \$63--507 | Exact printed value in this scope, unchanged precision | `own server for twenty people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команде из двадцати человек нужн; нужны две карты при лёгкой нагрузке и шестнадцать, по две в сервере, при тяжёлой → ПОДМЕНА | Exact printed value in this scope, unchanged precision | `cards for twenty people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команде из двадцати человек нужн; \$843 → \$844 | Exact printed value in this scope, unchanged precision | `B300 node per person, twenty people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; стоят \$9.68, у самого дешёвого \$1.34 → стоят \$9.68, у самого дешёвого \$1.35 | Exact printed value in this scope, unchanged precision | `API per 1000 calls` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; с 838 до 605 вызовов в день → с 838 до 606 вызовов в день | Exact printed value in this scope, unchanged precision | `upper bound, capacity` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; 5--20 → 5--21 | Exact printed value in this scope, unchanged precision | `upper bound, API rise` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; \$57 против \$268 → \$57 против \$269 | Exact printed value in this scope, unchanged precision | `upper bound, s50 against median` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; \$57 против \$42 при → \$57 против \$43 при | Exact printed value in this scope, unchanged precision | `upper bound, s50 against cheapest` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; в 1.9 раза при доле 20 → в 1.9 раза при доле 21 | Exact printed value in this scope, unchanged precision | `upper bound, s20 against cheapest` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Мак уже есть; хранение стоит \$6.9 в месяц, меньше, чем сам prefill (\$10.0) → хранение стоит \$6.9 в месяц, меньше, чем сам prefill (\$10.1) | Exact printed value in this scope, unchanged precision | `storage against prefill` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Мак уже есть; обходится в \$16.5 → обходится в \$16.6 | Exact printed value in this scope, unchanged precision | `conservative storage` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; \$27--32 в месяц → \$27--33 в месяц | Exact printed value in this scope, unchanged precision | `s20 hybrid dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; (\$14), и в → (\$15), и в | Exact printed value in this scope, unchanged precision | `s20 API dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; (\$102) → (\$103) | Exact printed value in this scope, unchanged precision | `s20 API median dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 00-abstract.tex :: Аннотация; 2.5--3.8 → 2.5--3.9 | Exact printed value in this scope, unchanged precision | `s20 below median, all clients, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: При доле открытой модели 20; 2.5--3.8 → 2.5--3.9 | Exact printed value in this scope, unchanged precision | `s20 below median, all clients, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 00-abstract.tex :: Аннотация; 1.9--2.9 → 1.9--2.0 | Exact printed value in this scope, unchanged precision | `s20 above cheapest, all clients, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: При доле открытой модели 20; 1.9--2.9 → 1.9--2.0 | Exact printed value in this scope, unchanged precision | `s20 above cheapest, all clients, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; 2.5--3.5 → 2.5--3.6 | Exact printed value in this scope, unchanged precision | `s20 below median, Max clients, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; 3.2--3.8 → 3.2--3.9 | Exact printed value in this scope, unchanged precision | `s20 below median, all clients, design` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; 1.9--2.3 → 1.9--2.4 | Exact printed value in this scope, unchanged precision | `s20 above cheapest, all clients, design` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; 2.5--2.7 → 2.5--2.8 | Exact printed value in this scope, unchanged precision | `s20 below median, all clients, conservative` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; 2.7--2.9 → 2.7--2.0 | Exact printed value in this scope, unchanged precision | `s20 above cheapest, all clients, conservative` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; около 840 вызовов → около 841 вызовов | Exact printed value in this scope, unchanged precision | `s50 M5 Max capacity` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; \$52--55 в месяц → \$52--56 в месяц | Exact printed value in this scope, unchanged precision | `s50 Max dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; (\$35) и в → (\$36) и в | Exact printed value in this scope, unchanged precision | `s50 API dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; (\$254) → (\$255) | Exact printed value in this scope, unchanged precision | `s50 API median dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; 4.6--4.9 → 4.6--4.0 | Exact printed value in this scope, unchanged precision | `s50 below median, Max clients` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; 4.6--4.9 → 4.6--4.0 | Exact printed value in this scope, unchanged precision | `s50 below median, Max clients` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; 49--55 → 49--56 | Exact printed value in this scope, unchanged precision | `s50 above cheapest, Max clients, percent` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; 1.5--2.4 → 1.5--2.5 | Exact printed value in this scope, unchanged precision | `s50 below median, Max clients, overflow at median` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; от 49 до 75\% → от 49 до 76\% | Exact printed value in this scope, unchanged precision | `s50 share served by Max clients` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; обходятся в \$48--50 → обходятся в \$48--51 | Exact printed value in this scope, unchanged precision | `s50 Ultra dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; и в \$66--67 при осторожной политике → и в \$66--68 при осторожной политике | Exact printed value in this scope, unchanged precision | `s50 Ultra conservative dollars` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; 37--42 → 37--43 | Exact printed value in this scope, unchanged precision | `s50 above cheapest, Ultra clients, percent` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; 3.8--5.3 → 3.8--5.4 | Exact printed value in this scope, unchanged precision | `s50 below median, Ultra clients, both cases` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Покупка клиента; стоит \$89 против \$35 у самого дешёвого API и \$254 у медианного → стоит \$89 против \$35 у самого дешёвого API и \$255 у медианного | Exact printed value in this scope, unchanged precision | `purchase at 50%` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Покупка клиента; \$65 против \$102 → \$65 против \$103 | Exact printed value in this scope, unchanged precision | `purchase at 20%` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Покупка клиента; дороже его на \$54 в месяц → дороже его на \$55 в месяц | Exact printed value in this scope, unchanged precision | `purchase against cheapest` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команды от 5 до 5000 человек; (\$101 против \$102 при доле 20\% → (\$101 против \$102 при доле 21\% | Exact printed value in this scope, unchanged precision | `teams at 500, 20%` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команды от 5 до 5000 человек; \$202 против \$254 при доле 50\% → \$202 против \$254 при доле 51\% | Exact printed value in this scope, unchanged precision | `teams at 500, 50%` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Покупка клиента; за 13 месяцев, Мак целиком за 25 → за 13 месяцев, Мак целиком за 26 | Exact printed value in this scope, unchanged precision | `payback s50, overflow to cheapest` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Покупка клиента; за 36 и 71 месяц → за 36 и 72 месяц | Exact printed value in this scope, unchanged precision | `payback s20, overflow to cheapest` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Покупка клиента; за 21 месяц → за 22 месяц | Exact printed value in this scope, unchanged precision | `payback s50, overflow to median` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Окупаемость клиента против медианного; за 21 месяц → за 22 месяц | Exact printed value in this scope, unchanged precision | `payback s50, overflow to median` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Покупка клиента; целиком за 40 → целиком за 41 | Exact printed value in this scope, unchanged precision | `payback s50, overflow to median, whole` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Окупаемость клиента против медианного; целиком за 40 → целиком за 41 | Exact printed value in this scope, unchanged precision | `payback s50, overflow to median, whole` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Окупаемость клиента против медианного; 16--19 → 16--10 | Exact printed value in this scope, unchanged precision | `payback, dearer than cheapest` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Чем глубже контекст; \$9.15 → \$9.16 | Exact printed value in this scope, unchanged precision | `GLM API session to 1M` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: 500 человек гибрид обходится в; \$9.15 → \$9.16 | Exact printed value in this scope, unchanged precision | `GLM API session to 1M` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: На 50 человек свой кластер; \$9.15 → \$9.16 | Exact printed value in this scope, unchanged precision | `GLM API session to 1M` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Чем глубже контекст; стоит \$0.44 → стоит \$0.45 | Exact printed value in this scope, unchanged precision | `GLM API session to 200k` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Чем глубже контекст; сессия дороже в 21 раз → сессия дороже в 22 раз | Exact printed value in this scope, unchanged precision | `GLM growth of the session cost` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: 500 человек гибрид обходится в; гибрид обходится в \$4.4--4.6 за сессию → гибрид обходится в \$4.4--4.7 за сессию | Exact printed value in this scope, unchanged precision | `GLM two sessions, hybrid` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: На 500 человек свой кластер; свой кластер стоит \$4.01 → свой кластер стоит \$4.02 | Exact printed value in this scope, unchanged precision | `GLM two sessions, own cluster` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: На 500 человек свой кластер; на 5000 человек \$3.37 → на 5000 человек \$3.38 | Exact printed value in this scope, unchanged precision | `GLM two sessions, own cluster at 5000` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Стоимость сессии.; (\$8.02) немного дешевле API (\$9.15), а гибрид с отдельной Studio на каждого дороже обоих (\$11.85) → (\$8.02) немного дешевле API (\$9.15), а гибрид с отдельной Studio на каждого дороже обоих (\$11.86) | Exact printed value in this scope, unchanged precision | `GLM 50 people` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; меньше чем на треть → больше чем на треть | Exact printed value in this scope, unchanged precision | `GLM Studio utilization at two sessions` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; почти семь сессий → больше чем семь сессий | Exact printed value in this scope, unchanged precision | `GLM Studio capacity` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; до \$1.05 на сессию → до \$1.06 на сессию | Exact printed value in this scope, unchanged precision | `GLM full load, Studio share` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; \$1.8--1.9 → \$1.8--1.0 | Exact printed value in this scope, unchanged precision | `GLM full load, hybrid session` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; 4.8--5.1 → 4.8--5.2 | Exact printed value in this scope, unchanged precision | `GLM full load, below API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; 4.8--5.1 → 4.8--5.2 | Exact printed value in this scope, unchanged precision | `GLM full load, below API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: Его преимущество растёт; 4.8--5.1 → 4.8--5.2 | Exact printed value in this scope, unchanged precision | `GLM full load, below API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; в 1.9 раза дешевле своего кластера. → в 1.0 раза дешевле своего кластера. | Exact printed value in this scope, unchanged precision | `GLM full load, below own cluster` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; при полной загрузке в 1.9 и → при полной загрузке в 1.0 и | Exact printed value in this scope, unchanged precision | `GLM full load, below own cluster` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: Его преимущество растёт; в 1.9 раза дешевле своего кластера. → в 1.0 раза дешевле своего кластера. | Exact printed value in this scope, unchanged precision | `GLM full load, below own cluster` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; \$2.5--2.8, в 1.3 раза дешевле своего кластера → \$2.5--2.8, в 1.4 раза дешевле своего кластера | Exact printed value in this scope, unchanged precision | `GLM four sessions, hybrid` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; в 1.3 раза дешевле своего кластера и → в 1.4 раза дешевле своего кластера и | Exact printed value in this scope, unchanged precision | `GLM four sessions, below own cluster` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; 3.3--3.6 → 3.3--3.7 | Exact printed value in this scope, unchanged precision | `GLM four sessions, below API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; 3.3--3.6 → 3.3--3.7 | Exact printed value in this scope, unchanged precision | `GLM four sessions, below API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; двое и каждый проводит по две сессии в день, \$2.6--2.9 → двое и каждый проводит по две сессии в день, \$2.6--2.0 | Exact printed value in this scope, unchanged precision | `GLM shared Studio` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; гибрид дороже своего кластера на 15--30\% → гибрид дороже своего кластера на 15--31\% | Exact printed value in this scope, unchanged precision | `GLM two sessions, dearer percent` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; при одной в 1.9--2.4 раза → при одной в 1.9--2.5 раза | Exact printed value in this scope, unchanged precision | `GLM one session, dearer factor` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; от 181 до 231 тысячи (25.9 часа) или от 131 до 231 тысячи (28.2 часа) → от 181 до 231 тысячи (25.9 часа) или от 131 до 231 тысячи (28.3 часа) | Exact printed value in this scope, unchanged precision | `refill, both slopes` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; заново 26--28 часов → заново 26--29 часов | Exact printed value in this scope, unchanged precision | `refill, range` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; около 35~ГБ → около 36~ГБ | Exact printed value in this scope, unchanged precision | `restore, size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; около пяти минут → ПОДМЕНА | Exact printed value in this scope, unchanged precision | `restore, minutes` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: Клиенту, который потерял; примерно за пять минут и дольше → ПОДМЕНА | Exact printed value in this scope, unchanged precision | `restore, minutes (conclusion)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; около 18 центов → около 19 центов | Exact printed value in this scope, unchanged precision | `restore, traffic` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; Хранение копии на NVMe по \$0.10 за гигабайт стоит около \$3.5 в месяц → Хранение копии на NVMe по \$0.10 за гигабайт стоит около \$3.6 в месяц | Exact printed value in this scope, unchanged precision | `restore, storage on NVMe` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Мак уже есть; \$0.50 в оперативной памяти и \$0.10 на NVMe → \$0.50 в оперативной памяти и \$0.11 на NVMe | Exact printed value in this scope, unchanged precision | `hosting prices` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 90-appendix.tex :: В расчётах $n = 4$; $p_{\text{RAM}} = \$0.50$ и $p_{\text{NVMe}} = \$0.10$ → $p_{\text{RAM}} = \$0.50$ и $p_{\text{NVMe}} = \$0.11$ | Exact printed value in this scope, unchanged precision | `hosting prices (appendix)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; По политике протокола копия в рабочие часы лежит в оперативной памяти по \$0.50 за гигабайт, и хранение стоит около \$6.7 → По политике протокола копия в рабочие часы лежит в оперативной памяти по \$0.50 за гигабайт, и хранение стоит около \$6.8 | Exact printed value in this scope, unchanged precision | `restore, storage under the protocol policy` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; раза дешевле своего серверного кластера на 50, 500 и 5000 человек → раза дороже своего серверного кластера на 50, 500 и 5000 человек | Direction wording at this site | `direction wording: closed: medium, hybrid cheaper at every team size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; раза дешевле своего кластера, при тяжёлой на → раза дороже своего кластера, при тяжёлой на | Direction wording at this site | `direction wording: closed: medium, hybrid cheaper at every team size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: В закрытом; раза дешевле своего серверного кластера, а при лёгкой → раза дороже своего серверного кластера, а при лёгкой | Direction wording at this site | `direction wording: closed: medium, hybrid cheaper at every team size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; на сервере, и гибрид дешевле кластера на → на сервере, и гибрид дороже кластера на | Direction wording at this site | `direction wording: closed: heavy, hybrid cheaper at every team size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; Для лёгкой нагрузки на 50 и 5000 человек гибрид дешевле кластера на → Для лёгкой нагрузки на 50 и 5000 человек гибрид дороже кластера на | Direction wording at this site | `direction wording: closed: light, hybrid cheaper at 50 and 5000` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; а при лёгкой дешевле на 50 и 5000 человек → а при лёгкой дороже на 50 и 5000 человек | Direction wording at this site | `direction wording: closed: light, hybrid cheaper at 50 and 5000` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: В закрытом; а при лёгкой дешевле на 50 и 5000 человек → а при лёгкой дороже на 50 и 5000 человек | Direction wording at this site | `direction wording: closed: light, hybrid cheaper at 50 and 5000` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; По этому правилу на 500 человек при лёгкой нагрузке оба варианта получают по одному узлу B300, и свой кластер обходится в → По этому правилу на 500 человек при лёгкой нагрузке только гибрид получают по одному узлу B300, и свой кластер обходится в | Direction wording at this site | `direction wording: closed: light at 500, own cluster cheaper under the rule` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; и дороже на 500: серверы на RTX PRO 6000 мы рассматриваем только для команд до → и дешевле на 500: серверы на RTX PRO 6000 мы рассматриваем только для команд до | Direction wording at this site | `direction wording: closed: light at 500, own cluster cheaper under the rule` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; на 500 человек оба варианта получают по одному узлу B300 → на 500 человек только гибрид получают по одному узлу B300 | Direction wording at this site | `direction wording: closed: light at 500, own cluster cheaper under the rule` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: В закрытом; и дороже на 500: серверы на RTX PRO 6000 мы рассматриваем только для команд до → и дешевле на 500: серверы на RTX PRO 6000 мы рассматриваем только для команд до | Direction wording at this site | `direction wording: closed: light at 500, own cluster cheaper under the rule` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: В закрытом; на 500 человек оба варианта получают по одному узлу B300 → на 500 человек только гибрид получают по одному узлу B300 | Direction wording at this site | `direction wording: closed: light at 500, own cluster cheaper under the rule` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; движок выбирает самый дешёвый из допустимых → движок выбирает самый дорогой из допустимых | Direction wording at this site | `direction wording: closed: the selected option is the cheapest eligible one` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Закрытый контур: всё внутри периметра; из допустимых вариантов взят самый дешёвый → из допустимых вариантов взят самый дорогой | Direction wording at this site | `direction wording: closed: the selected option is the cheapest eligible one` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; Экономия немонотонна, потому что серверы и узлы добавляются целиком → Экономия монотонна, потому что серверы и узлы добавляются целиком | Direction wording at this site | `direction wording: closed: light-load saving is not monotone over 50, 500 and 5000` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Одни клиентские машины почти; Вне этого правила, на серверах с двумя RTX PRO 6000, гибрид на 500 человек стоил бы около → По этому правилу, на серверах с двумя RTX PRO 6000, гибрид на 500 человек стоил бы около | Direction wording at this site | `direction wording: closed: light at 500, hybrid cheaper outside the rule` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Вывод.} Против медианного; Самый дешёвый поставщик API дешевле гибрида на всех рассмотренных клиентах и при обеих долях → Самый дешёвый поставщик API дороже гибрида на всех рассмотренных клиентах и при обеих долях | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Как это будет меняться; самый дешёвый поставщик обходится дешевле гибрида на всех рассмотренных клиентах → самый дешёвый поставщик обходится дороже гибрида на всех рассмотренных клиентах | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; раза дороже, чем у самого дешёвого поставщика API → раза дешевле, чем у самого дешёвого поставщика API | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 20\% пользователь; раза дороже самого дешёвого поставщика → раза дешевле самого дешёвого поставщика | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; \% дороже самого дешёвого API ( → \% дешевле самого дешёвого API ( | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: При доле открытой модели 20; раза дороже самого дешёвого → раза дешевле самого дешёвого | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 00-abstract.tex :: Аннотация; раза дороже самого дешёвого → раза дешевле самого дешёвого | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Окупаемость клиента против медианного; Против самого дешёвого поставщика гибрид дороже → Против самого дешёвого поставщика гибрид дешевле | Direction wording at this site | `direction wording: cheapest API cheaper than the hybrid on every client, both shares and policies` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: При доле 50\% на открытую; дороже самого дешёвого API при хранении по политике протокола → дешевле самого дешёвого API при хранении по политике протокола | Direction wording at this site | `direction wording: at 50% Ultra clients dearer than the cheapest API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команды от 5 до 5000 человек; на 500 человек свой кластер уже дешевле медианного поставщика API при обеих долях → на 500 человек свой кластер уже дороже медианного поставщика API при обеих долях | Direction wording at this site | `direction wording: teams: own cluster below the median API at 500, above it at 50, above the cheapest at every size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команды от 5 до 5000 человек; на 50 человек ещё дороже → на 50 человек ещё дешевле | Direction wording at this site | `direction wording: teams: own cluster below the median API at 500, above it at 50, above the cheapest at every size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Команды от 5 до 5000 человек; Самого дешёвого поставщика API свой кластер не догоняет ни при каком размере команды до 5000 → Самого дешёвого поставщика API свой кластер догоняет ни при каком размере команды до 5000 | Direction wording at this site | `direction wording: teams: own cluster below the median API at 500, above it at 50, above the cheapest at every size` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; ёмкость M5 Max падает → ёмкость M5 Max растёт | Direction wording at this site | `direction wording: upper bound: capacity falls, API rises, the gap to the cheapest API narrows` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; API дорожает на → API дешевеет на | Direction wording at this site | `direction wording: upper bound: capacity falls, API rises, the gap to the cheapest API narrows` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Все числа этого раздела; разрыв с самым дешёвым сокращается → разрыв с самым дешёвым растёт | Direction wording at this site | `direction wording: upper bound: capacity falls, API rises, the gap to the cheapest API narrows` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Мак уже есть; в месяц, меньше, чем сам prefill → ПОДМЕНА | Direction wording at this site | `direction wording: storage cheaper than prefill (M5 Max, 20%)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: На 500 человек свой кластер; свой кластер стоит → гибрид стоит | Direction wording at this site | `direction wording: 1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: На 500 человек свой кластер; и дешевле гибрида → и дороже гибрида | Direction wording at this site | `direction wording: 1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; При двух сессиях в день гибрид дороже своего кластера на → При двух сессиях в день гибрид дешевле своего кластера на | Direction wording at this site | `direction wording: 1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; раза дешевле своего кластера и в → раза дороже своего кластера и в | Direction wording at this site | `direction wording: 1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; раза дешевле API и в → раза дороже API и в | Direction wording at this site | `direction wording: 1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; раза дешевле своего кластера. → раза дороже своего кластера. | Direction wording at this site | `direction wording: 1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; раза дешевле своего кластера и в → раза дороже своего кластера и в | Direction wording at this site | `direction wording: 1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: Его преимущество растёт; раза дешевле своего кластера. → раза дороже своего кластера. | Direction wording at this site | `direction wording: 1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; 3.3--3.6 раза дешевле API → 3.3--3.6 раза дороже API | Direction wording at this site | `direction wording: 1M: four sessions a day below the API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Вывод.} Контекст до миллиона; 3.3--3.6 раза дешевле API → 3.3--3.6 раза дороже API | Direction wording at this site | `direction wording: 1M: four sessions a day below the API` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Стоимость сессии.; Команде из 10 человек и меньше выделенный сервер не окупается, и дешевле всего остаётся API → Команде из 10 человек и меньше выделенный сервер не окупается, и дороже всего остаётся API | Direction wording at this site | `direction wording: 1M: API cheapest for 10 people and fewer; at 50 own below API below hybrid` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Стоимость сессии.; немного дешевле API → немного дороже API | Direction wording at this site | `direction wording: 1M: API cheapest for 10 people and fewer; at 50 own below API below hybrid` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Стоимость сессии.; дороже обоих → дешевле обоих | Direction wording at this site | `direction wording: 1M: API cheapest for 10 people and fewer; at 50 own below API below hybrid` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Studio при двух сессиях; При осторожной политике хранения сессии дороже не больше чем на 20 → При осторожной политике хранения сессии дешевле не больше чем на 20 | Direction wording at this site | `direction wording: 1M: conservative policy at most 20% dearer` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 14-conclusion.tex :: Клиенту, который потерял; заново больше суток → заново меньше суток | Direction wording at this site | `direction wording: 1M: refill of a million tokens on M3 Max takes longer than a day` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; Пять минут здесь нижняя граница: по политике протокола сервер дописывает в копию токены вызовов, прочитанных клиентом, только при следующем оффлоаде → Пять минут здесь верхняя граница: по политике протокола сервер дописывает в копию токены вызовов, прочитанных клиентом, только при следующем оффлоаде | Direction wording at this site | `direction wording: 1M: the server copy can lag behind the client under the protocol policy` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 08-million.tex :: Потеря кэша.; Если диск клиента уцелел, сессию быстрее поднять из локального снимка → Если диск клиента уцелел, сессию медленнее поднять из локального снимка | Direction wording at this site | `direction wording: 1M: a local NVMe snapshot restores faster than the 1 Gbit/s link` | Complete clean `check()` passes; `ranges-self-final-03.log` |
| 05-clients.tex :: & 25.9 &; 25.9 → 25.0 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry 25.9` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 07-economics.tex :: 50 человек, 10 ч в день &; \$48 → \$49 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry \$48` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 07-economics.tex :: 10 человек, 24 ч &; \$59 → \$50 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry \$59` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 07-economics.tex :: 50 человек, 10 ч в день &; \$35 → \$36 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry \$35` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 07-economics.tex :: 50 человек, 24 ч &; \$38 → \$39 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry \$38` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 07-economics.tex :: 50 человек, 24 ч &; \$29 → \$20 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry \$29` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 07-economics.tex :: остаточной стоимости 80\% (\$35); \$35 → \$36 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry \$35` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 07-economics.tex :: Не выше на стандартном усилии рассуждения &; 4.8--5.1 → 4.8--5.2 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry 4.8--5.1` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 06-server.tex :: генерация была на 15--30; 15--30 → 15--31 | Every matching occurrence of this reasoned collision remains mandatory | `unused ALLOW entry 15--30` | Clean collision inventory passes; `ranges-self-final-03.log` |
| 05b-models.tex :: channel 1G; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `channel 1G` | Same clean site passes; `offload-self-final-01.log` |
| 05b-models.tex :: llama.cpp bound 1G; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `llama.cpp bound 1G` | Same clean site passes; `offload-self-final-01.log` |
| 05b-models.tex :: channel 10G; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `channel 10G` | Same clean site passes; `offload-self-final-01.log` |
| 05b-models.tex :: llama.cpp bound 10G; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `llama.cpp bound 10G` | Same clean site passes; `offload-self-final-01.log` |
| 05b-models.tex :: llama.cpp ceiling; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `llama.cpp ceiling` | Same clean site passes; `offload-self-final-01.log` |
| 05b-models.tex :: llama.cpp rate at 110k; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `llama.cpp rate at 110k` | Same clean site passes; `offload-self-final-01.log` |
| 06-server.tex :: vLLM cold-fit 16k; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `vLLM cold-fit 16k` | Same clean site passes; `offload-self-final-01.log` |
| 06-server.tex :: vLLM cold-fit 249k; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `vLLM cold-fit 249k` | Same clean site passes; `offload-self-final-01.log` |
| 06-server.tex :: vLLM cached 16k; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `vLLM cached 16k` | Same clean site passes; `offload-self-final-01.log` |
| 06-server.tex :: vLLM cached 65k; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `vLLM cached 65k` | Same clean site passes; `offload-self-final-01.log` |
| 06-server.tex :: vLLM cached 131k; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `vLLM cached 131k` | Same clean site passes; `offload-self-final-01.log` |
| 06-server.tex :: vLLM cached 249k; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `vLLM cached 249k` | Same clean site passes; `offload-self-final-01.log` |
| 06-server.tex :: vLLM server-only qualification; wrong first printed numeral (qualification: server→client) | This exact rate/value or server-only qualification at this paragraph | `vLLM server-only qualification` | Same clean site passes; `offload-self-final-01.log` |
| Old storage “больше, чем сам prefill” | Obsolete direction cannot accompany corrected dollars | `direction wording: storage cheaper than prefill (M5 Max, 20%)` | Clean “меньше” passes; `ranges-self-final-03.log` |
| Old “почти в четыре раза дешевле API” | Old verbal bound cannot replace3.3–3.6 | `GLM four sessions, below API` | Clean computed ratio passes; `ranges-self-final-03.log` |
| Stale client/perimeter table cell | Exact complete row, not any equal scalar elsewhere | `client table row`, `closed-perimeter table row` | Both clean tables pass; `ranges-self-final-03.log` |
| Changed storage hours / engine comparison direction | Model dependency rather than hardcoded text blessing | `restore, storage under the protocol policy`, `storage cheaper than prefill (M5 Max, 20%)` | Original inputs/inequality pass; `ranges-self-final-03.log` |
| New unregistered five-minute/range occurrence; removed collision form | Whole-section occurrence scan and exact collision sites | `unregistered occurrence`, `unused ALLOW entry` | Complete clean publication passes; `ranges-self-final-03.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_exact_printed_site_omission_is_rejected` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_paper_ledger_waivers_are_site_bound` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_reverse_guard_rejects_copied_non_arch_changed_values` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_reverse_inventory_spans_exports_and_keys` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_all_design_csv_bytes_unchanged` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_measured_export_cannot_overwrite_run11` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_historical_exports_and_paper_text_unchanged` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_paper_ledger_covers_changed_exports_and_printed_numbers` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |
| Isolated abstract: append stale883; separately append nonnumeric prose | Current numeric registration **and** byte drift, including nonnumeric text | `test_paper_ledger_omission_controls` | All9 clean tests exit0; each mutant produces this named failure, exit1; `engine-controls-final-02.log`, `engine-byte-controls-red-01.log` |

No mutant survives the listed controls. The nine repeated publication plants establish that each migrated test
reaches the current guard; they do not claim nine independent semantic algorithms. Historical arithmetic/negative
scope is protected by the unchanged source-fixture tests, and the individual current claims have separate site
plants above. Rework extends into calc/tests because the user explicitly requires migration of those nine tests;
all other authored code is in the two requested paper checkers. Root documentation and manifest changes record
that scope. No shared runtime or skill is edited.

### Migration verification record

Final command outcomes are appended here after complete standalone runs. All logs are in
`.temp/hybrid-c-r8-261101/`; stdout/stderr are redirected directly, never through tee. Disk-backed TMPDIR and
`PYTHONDONTWRITEBYTECODE=1` are set on every Python/build gate. No pending result is called passing.

The static site audit (`site-audit-01.log`, exit0) verifies104→107 value sites,48→49 direction sites, all original
collision-site reasons, the one documented own-cluster sentence relocation, and Python3.9 grammar for all ten
changed Python files. Runtime validation is on Linux Python3.14.4; no macOS/Python3.9 execution is claimed.

Initial diagnostic gates were genuinely red: the first v2 baseline lacked an occurrence index for repeated equal
numbers on one line (`publication-01.log`, exit1); the first range self-test exposed an unscoped repeated1.9x scalar
and repeated API phrase (`ranges-self-01.log`, exit1). The later collision control changed only one of two matching
client rows and therefore did not remove the exception (`ranges-self-final-02.log`, exit1). Those plants were
corrected to bind the actual comparison and mutate every matching collision occurrence; final03 exits0. The first
offload run used the wrong Russian inflection at131k (`offload-01.log`, exit1); correcting the expected wording
preserved its numeric value. No failed or partially applied plant is counted as a successful negative control.

| Standalone gate | Exit | Evidence / scope |
| --- | ---: | --- |
| `python3 paper/data/check_ranges.py` | 0 | `ranges-final-03.log`; all current values, directions, tables and occurrence sites |
| `python3 paper/data/check_ranges.py --self-test` | 0 | `ranges-self-final-03.log`;156 individual site plants,9 collision-entry plants, original table/model/guard controls and explicit obsolete-phrase regressions |
| `python3 paper/data/offload_bound.py` | 0 | `offload-final-01.log`; depth-dependent base envelope and separate server-only vLLM rates |
| `python3 paper/data/offload_bound.py --self-test` | 0 | `offload-self-final-01.log`;13 independently named wrong-value/rate/qualification plants and clean control |
| `python3 calc/tests/r13_ledger.py` | 0 | `ledger-final-01.log`; current v2 guard,92 files and1619 numeric occurrences |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `kit-01.log`;24 tests /20.010s; source/tests/config/environment unchanged afterward |
| Nine isolated migrated tests, clean copy | 0 | `engine-controls-clean-01.log`; all9 pass on final source |
| Same9 tests with stale883 appended | 1 (expected red) | `engine-controls-red-01.log`; nine named assertion failures, no errors; outer harness `engine-controls-final-02.log` exits0 |
| Same9 tests with nonnumeric text appended | 1 (expected red) | `engine-byte-controls-red-01.log`; nine named byte assertions, no errors; outer harness `byte-controls-final-01.log` exits0 |
| `make pdf TECTONIC=$PWD/.temp/paper-v2-261101/tectonic-cached` | 0 | `pdf-01.log`; Tectonic0.17.0, only-cached; underfull boxes only; source TeX unchanged afterward; rebuilt after signing for exact version metadata |
| `make manifest`; `sha256sum -c MANIFEST.sha256` | 0 /0 | `manifest-01.log`, `manifest-verify-01.log`; refreshed again after this evidence note |
| Historical/engine/kit scope equality against r7 | 0 | `provenance-preserved-01.log`; no changes in calc/hybridcalc,calc/out,data,bench, original quote ledger or historical numeric waivers |
| Whitespace review | 0 | `diff-check-01.log`; existing CSV CRLF convention retained |

The first full engine run passed277 tests in431.952s (`engine-01.log`, exit0). The final full run is recorded
below because subsequent changes strengthened collision controls and restored the original historical negative
fixtures; the earlier green run is not substituted for final-source execution.

Final full-source engine gate: `python3 -m unittest discover -s calc/tests -v` exited **0** with
**277 tests in508.942s, no failures or errors**, including `test_historical_quote_ledger_provenance` and its eight
original source-revision tests. Complete log: `engine-final-01.log`. `gate-source-identity-01.json` pins the tested
source/configuration and environment; `source-identity-verify-01.log` (exit0) verifies those files did not change
across the final run. Self-review checked the complete migration diff, historical preservation, per-site negative
controls, baseline file/coordinate completeness and the explicit server-only boundary. No independent acceptance
or publication is claimed. The local signed candidate is **ready for review**; no push or tag is authorized.

Final manifest refresh and exact-head offline PDF readback are recorded in `manifest-final-01.log`,
`manifest-verify-final-01.log`, `pdf-head-01.log` and `signatures-final-01.log` under the same task log directory.

## External review response: hybrid-c-r9-261102

Base: local `paper-v2` at `d9c5e5f80489f5b33add7516909c684270bbcd71`. Scope is review items1,3,5,
plus the measured first-call breakdown. Engine run14 and the growing-session experiment are dependencies,
not results of this run. No engine input, historical export, measurement archive or kit is changed.
The brief contains no attack-surface table; that remains a brief gap. No attack-coverage map or audit implementation
is claimed. No out-of-contract row is silently treated as measured: queues, multi-client service operation,
retention implementation, attack detection, cross-platform tolerance, task quality and growing mixed sessions remain unqualified.

| Text / former claim | Source and disposition | Result / boundary |
| --- | --- | --- |
| Related work, introduction, abstract, conclusion: session life between turns is new | DS4 PR401 and pinned code already flush local decode and replay transcript; PPD routes append-prefill; PrfaaS separates recurrent state and full-attention KV | Claim narrowed to service design/applicability for an autonomous local agent; four questions point to measured, modelled or proposed evidence |
| Related-work mechanism table | Primary sources below; eight mechanism rows and five systems | Source silence is marked NO (Russian НО), never inferred absence or uniqueness; ours is explicitly design scope |
| Distinguishing combination and measured evidence | FACTS sections2/3: CUDA same-partition max logit difference0.0 through127,538; stock CUDA/Metal slot restore260k/1.04M; tool-output8193 tokens at241–247s versus9.8–10.2s | Exact continuation is finite/configuration-bound; slot restoration does not calibrate logits; tool-prefill gap excludes wire/import; combined multi-turn operation pending |
| Security and all summary verification claims | Access to intermediate state, trusted weights hash/journal/client checkpoints, provider substitutions/omissions; piecewise inputs reference prior committed states and activations back to trusted root | Proposed audit, open threat model; commitment is not correctness; no measured attack detection probability or price comparison |
| Security tolerance and API comparison | Same-partition experiment only; CUDA/Metal calibration and KL study pending | API users may own weights; remove cloud impossibility and orders-of-magnitude attack separation; specify honest/error distributions and attack controls needed |
| Models bound | FLOP/byte bound sets possibility; actual server/reload/import/queues remain | New exact wording added to offload guard with its own plant and clean control |
| AppendixA remote time | `calc/hybridcalc/session_hosting.py:route`, `policy_with_reload` | Current delta plus expected pending tail; full stationary numerator, fixed-point removal, zero-offload case, no tail wire duplication; import0 limitation explicit |
| Workload, limitations, owner-table caption | Two exact JSON exports plus `tools/agent_session_stats.py:analyse/model_usage` and `paper/data/year_bill.py:bill/summary/main` | Author's own sessions, one user, per-tool dates; totals differ by snapshot, not filtering |
| First call over5G, abstract and conclusion | FACTS3:123.2+42.4=165.6s of201.7s; server10.6s | Standalone delivery/import result; large predicted gains label a different configuration; matched prediction TODO(data) |
| Review2 and4, changing economic inputs | dev-b growing session; dev-e run14 | TODO(data): growing local/remote turns/catch-up/recovery; matched5G prediction/import; symmetric storage/eviction/no artificial PRO6000 cap; R13 values retained pending replacement |

### Primary-source readback

- [DS4 PR401](https://github.com/antirez/ds4/pull/401), Summary/User-Facing Behavior: layer-distributed prefill,
  slice KV handoff and coordinator-local decode. Read as a proposal, not upstream release qualification.
- [Pinned DS4 code](https://github.com/lobanov/ds4/blob/6399c23de955917a519cf08a67a24cb62945023e/ds4_distributed.c#L5772),
  `dist_session_flush_local_decode_remote`5772: bounded token chunks, positions, prefix/result hashes and ACK-only requests;
  `ds4_dist_session_sync`6500 calls it before continued distributed prefill. `dist_coordinator_rebuild_from_transcript`3415
  replays the transcript. Raw source SHA256 `1349bdfccb469fd91d6b99a3df23a93bc748a4101ae6e33d6fec6970e56a5ad4`,
  retained in `.temp/hybrid-c-r9-261102/ds4_distributed.c`. Browser code fetch failed (cache miss); the allowed raw-source fetch succeeded.
- [PPD v1](https://arxiv.org/html/2603.13358v1), sections1/2.2/2.3/5 and appendixB.1/B.2:
  server P/D roles, previous-response recomputation, dynamic append routing, KV transfer and session table.
  No autonomous personal client or recurrent-state contract is described.
- [SparKV v1](https://arxiv.org/html/2604.21231v1), sectionsII/III/IV:
  precomputed full-context KV; token/layer/head block scheduling, cloud/local computation, local decode.
  No two-copy session catch-up/rebuild or recurrent-state transfer contract is described.
- [PrfaaS v1](https://arxiv.org/html/2604.15039v1), sections3.1–3.4:
  remote/full prefill, local PD fallback, selective per-request placement, shared cache pools;
  section3.2 explicitly separates full-attention and linear-state groups. This is prior art, not our unique mechanism.
  Catch-up/rebuild for an autonomous personal decoder is not specified.

Only browser text views of the papers were read; no PDFs, models, packages, or datasets were downloaded.
The only fetched local source file was the expressly permitted DS4 code. No native build or accelerator job ran.

### Exact corpus reconciliation

Workload source: `data/measurements/ivmbp-2026-10-30/session-call-dates/stats.json`, generated
`2026-10-30T10:51:36.706920+00:00`. Billing source: `paper/data/owner-model-usage-2026-10-30.json`, generated
`2026-10-30T21:17:05.979961+00:00`. Both use `sample=0,min_calls=1,max_mb=0,chars_per_token=3.6`.

| Agent | Workload calls / contexts | Model-usage calls / contexts | Difference calls / contexts |
| --- | ---: | ---: | ---: |
| Claude | 285129 /2867 | 285129 /2867 | 0 /0 |
| Codex | 1126620 /7664 | 1129165 /7665 | 2545 /1 |
| Muse | 116445 /2644 | 116445 /2644 | 0 /0 |
| All | 1528194 /13175 | 1530739 /13176 | 2545 /1 |

`analyse` counts all retained calls in depth/output totals after min_calls; only new-input distribution excludes
first/reset observations. `model_usage` applies the same session threshold, groups all retained calls including null
model labels, and `year_bill.summary` sums calls across every record before selecting priced records. The exact price
summary and source digest are in `.temp/hybrid-c-r9-261102/source-readback-01.json`. The retained aggregates locate the
count delta, not every changed private call identity; no per-call trace or exact cause of each added record is claimed.
Retained first usage dates are Codex2025-11-18, Claude2026-05-07, Muse2026-08-06. Both exports are bounded reads, not atomic snapshots.

### Appendix derivation and verification scope

The engine's remote array is `reload + d*g + transfer(d)`, shadow is `(d+o)*g`, output is `o*g`.
`route(at_offload)` averages shadow for non-selected rows and output for selected rows over the selected count,
adds this expected tail to each selected remote time, and monotonically removes non-profitable calls until stable.
The synthetic opportunities are exchangeable; this is not the observed chronological tail of a real trace.
No current output is counted twice and no additional tail payload is sent. The current caller passes zero foreground
import; run14 must replace that assumption. Formula fixtures test a mixed selection, a marginal call removed after
catch-up, and all-local rejection, with exact independent expected times and unchanged selected wire bytes.

### R9 control map and diagnostic outcomes

| Mutant / control | What the guard is narrowed to | Named test/checker that rejects the plant | Survival bound |
| --- | --- | --- | --- |
| Append nonnumeric prose to each of the12 changed TeX files, one file at a time | Exact current-publication bytes at each changed file | `PaperReviewTests.test_review_sites_reject_prose_drift` (file-named subtests) | None survives; byte drift detection, not semantic truth or attack detection |
| Append stale883 to each of the same12 TeX files, one file at a time | Registration of every numeric occurrence, including new comment sites | `PaperReviewTests.test_review_sites_reject_unregistered_numbers` (file-named subtests) | None survives; the ledger does not independently validate arbitrary scientific claims |
| Replace the bound's possibility/overhead qualification | Correct bound interpretation at the physics paragraph | `offload_bound.py --self-test`: `bound is possibility, actual gain includes overhead` | Rejected; exact scope is this qualification, not a measured queue model |
| Existing numerical/rate/qualification plants | Each old offload claim retains its original value and finite server-only boundary | `offload_bound.py --self-test`, all13 original named checks plus the new qualification | None survives |
| Existing range/value/direction/collision/table/input plants | All original publication sites and numerical tolerances stay enforced | `check_ranges.py --self-test`,156 site controls plus collision/table/engine controls | None survives; no new source-truth algorithm is claimed |
| Finite independent route fixtures: mixed2-remote/1-local, marginal removal, no offload | Correct pending numerator, removal fixed point, zero-offload effects, no additional tail bytes | `PaperReviewTests.test_appendix_deferred_tail_and_unchanged_wire` | These finite cases do not qualify chronological multi-turn runtime or client import |
| Exact aggregate/model-row/billing readback | Snapshot delta is entirely Codex; filters match; unpriced calls remain in total | `PaperReviewTests.test_corpus_difference_is_snapshot_not_billing_filter` | Per-call private identities and atomic snapshot causality remain outside retained evidence |

The old workload `analyse` AST is identical at `ec7fd1a` (1.5-call-time) and `21d8151` (1.6-model-usage).
The version diff is retained as `stats-version-diff-01.patch`; legacy counting/deduplication paths remain,
and the later version adds raw counters/model grouping. The identity check also verifies unchanged engine,
exports, raw data and kits against r8. Evidence: `source-identity-01.log`.

`pdf-01.log` is a real failure (make exit2): the new summation glyph required uncached `cmex10.pfb`.
No font was fetched or installed. The same arithmetic was typeset using explicitly defined accumulated
local-work and remote-output terms; `pdf-02.log` and `pdf-final-01.log` exit0 with cache-only Tectonic0.17.0.
These builds show no undefined references, missing characters or overfull boxes; underfull-box warnings remain.
No PDF raster/text-inspection tool is installed (`pdf-tools-readiness-01.log`); no rendered-page inspection is claimed.
The first finite style probe exited1 because it incorrectly treated the grammatical phrase `все слои` as missing ё;
that probe was corrected without changing the phrase. `style-review-02.log` exits0 and is limited to the listed
added-line patterns; prose and pronoun antecedents were also read manually. The corrected billing paragraph names
calls in its own sentence rather than referring to journals through an unbound pronoun.

The brief's independently owned prerequisites remain open. A green local suite is not acceptance of the proposed
audit, proof of attack coverage, approval of pending measurements, or review/landing of this local candidate.

### R9 validation record

Every gate was a standalone process with real status preserved, direct log redirection, disk-backed
`TMPDIR=$PWD/.temp/hybrid-c-r9-261102/tmp` and `PYTHONDONTWRITEBYTECODE=1`. All logs below are under
`.temp/hybrid-c-r9-261102/`.

| Standalone command | Exit | Evidence |
| --- | ---: | --- |
| `python3 paper/data/check_ranges.py` | 0 | `ranges-final-02.log` |
| `python3 paper/data/check_ranges.py --self-test` | 0 | `ranges-self-final-02.log`;156 site controls and retained collision/table/model controls |
| `python3 paper/data/offload_bound.py` | 0 | `offload-final-01.log` |
| `python3 paper/data/offload_bound.py --self-test` | 0 | `offload-self-final-01.log`;14 named plants and clean publication |
| `python3 calc/tests/r13_ledger.py` | 0 | `ledger-final-02.log`;92 pinned files,1662 numeric occurrences |
| `PYTHONPATH=calc/tests python3 -m unittest test_paper_review -v` | 0 | `review-controls-final-02.log`;4 tests, final12-file plant list, after last prose change |
| `python3 -m unittest discover -s calc/tests -v` | 0 | `engine-01.log`;281 tests in663.932s, including historical-source tests; no failures/errors |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `kit-01.log`;24 tests in30.957s; kit source/config/environment unchanged |
| `make pdf TECTONIC=$PWD/.temp/paper-v2-261101/tectonic-cached` | 0 | `pdf-candidate-01.log`;final prose, only-cached Tectonic; exact-head rebuild follows signing |
| `make manifest`; `sha256sum -c MANIFEST.sha256` | 0 /0 | `manifest-01.log`, `manifest-verify-01.log`;refresh again after this evidence record |
| Exact source/data preservation and finite style/whitespace checks | 0 | `source-identity-01.log`, `source-identity-verify-01.log`, `style-review-02.log`, `diff-check-final-01.log` |

The full suite ran while the last typography/wording and changed-file list were finalized. The four review controls
were rerun afterward against the final pinned text and12-file list; all remaining engine/runtime/data/kit source and
original tests are unchanged. `gate-source-identity-01.json` binds317 source/test/configuration files for final readback.
Self-review covered every new mechanism-table cell against the named primary-source sections, the proposed/trusted
boundaries, exact corpus arithmetic and formula derivation. Independent acceptance and owner publication remain
outside this local handoff. This signed local candidate is ready for review; no push or tag is authorized.

## Overnight measurements: hybrid-c-r10-261102

Authorized base `eef577c66ab6ee74043b03f9dd32e1ea7ad02962` on `paper-v2`, initially clean.
This task imports measured facts into the prose; the engine, its inputs, historical exports and current run13
snapshot remain unchanged. No board exists in this checkout (`task-board goal get`, exit1); progress uses the
existing `.temp/tasks.md`. No attack-surface table was supplied. The finite measurement/guard map below states
what was checked and leaves hardware reproduction, pending runs and engine integration outside this handoff.

### Source and gap map

The orchestrator's source is `/home/agent/lanes/hybrid/.temp/paper-v2/FACTS.md`, SHA256
`f090441eaec3ec3a9bf170766e44329f281275c0d0fe99e147716e966ef4bdb9`. Its exact readback is retained at
`.temp/hybrid-c-r10-261102/FACTS-source.md`. The style source is
`/home/agent/src/swarma-docs/editorial/style.ru.md`, SHA256
`6ffdfa7efaa9ae29d907bc5f3f57808411851b585c7edeeae7c1e95fdaf287b6`.
Specific delivered measurements in FACTS1b/1c/3 supersede its older general pending list. Evidence paths below
are the source's references, not claims that this CPU-only paper task repeated remote GPU or Mac runs.

| Public site | Measurement/evidence | Applied change and remaining gap | Conclusion status |
| --- | --- | --- | --- |
| 05-clients, `tab:parallel-decode`,32k | Requested M3 anchor; existing `data/measurements/ivmbp-2026-10-30/qwen27b-bench/normalized-results.json` and `parallel.jsonl`; FACTS2 M5 archive `c7ceab57…` under `.temp/m5max64-results-261101/` | M3 single8.44 and four13.2 by request time, four14.05 by generation intervals; M5 single18.29/four33.37 | Denominator distinction explicit; no engine change |
| 05-clients,64k and128k | FACTS2 step55; restored128k archive `409bd7ef...d73e` | All requested64k points through24 streams, restored128k1/2/4/6/8 points, separate12-stream13.9 after34-minute prefill as lower bound | Aggregate rises past8 at64k; each agent is slower than the single-stream case. No monotone per-agent decline between every adjacent count is claimed |
| 05-clients,260k | FACTS2 step56 | Existing1/2/4/6/8 rates moved into the same table | Preserved measured rates; no stream extrapolation |
| 05-clients, realistic agents | FACTS2 step57 archive `9b7019cd...3ac2` | Same calls on Mac/PRO6000; mean Mac stream speeds, callp90 and both prefill-share vectors;8193-token tool output at4–8 sessions | Mac mostly generates on this mix; large tool results produce long input waits. No step57 M5 speed claim (swap exclusion retained) |
| 05-clients, pending | FACTS2 plus owner request | `TODO(data)` for cooled restored kit1.6.6,32k and up to32 streams; run14 gain by agent count and step57 validation | No pending result promoted to observation |
| 06-server, `tab:b300-llama` | FACTS1b; kit1.6.5, llama.cpp `dde879bc`, native103a-real, checkpoints0; `/root/kitb300/gpu/results/` on Vast58724229 | Complete16/50/100/150/200/249k ladder (segment,512/2000/10000 deltas,decode); Δ2000 1659/892 versus PRO6000 3547/905, with mixed-build caveat | Measured llama.cpp prefill does not support peak-ratio scaling; economics remains unchanged pending run14 |
| 06-server, `tab:b300-vllm` and cached paragraph | FACTS1c; `qwen27b-gpu-bench-results-b300-20261101T232533Z.tar.gz`, SHA256 `1325ae41…11bc`, `.temp/b300-results-261101/` | Cold marginal16/50/100/249k rates, ordinary/FP8 KV; cached2000/10000 with784/1568-token blocks; fitted16k Δ10000 23151 versus llama.cpp1663 | Explicitly server-only. Marginal rate distinguished from finite-portion integration; no measured hybrid speed/economics inferred |
| 06-server, bridge | FACTS3, branch `m3-vllm-bridge` `4a25d528`; `/root/bridge/run2/` on Vast58724229 | Export784;64-position BF16 top1 64/64,KL0.00055nats; Q4 top1 64/64,KL0.0027nats; no free-running divergence in64 tokens | Heterogeneous and uncalibrated; approximate equivalence, no bit-exact or full-path speed qualification.31,360-token run and node-adapter smoke remain TODO |
| 06-server and05b-models, engine boundary | Current run13 snapshot, unchanged | State that retained B300 economics/example use the old scaled assumption and add run14 TODOs | The new server observations replace the measurement placeholder, without presenting old economics as newly measured |
| 04-channel, import beside5G | FACTS3 PR9 CUDA: `.temp/pr9-results/hybrid-bench-r13-27b-cuda-*.jsonl`; M3/5G measured point | About158MB/1.6s fixed per offload, about0.52ms/token;39146tokens/1.99GB/import20.2s versus prefill10.6–10.8s; M3 one point1.07ms/token | Labelled pre-import-speed-v2. Delivery/application costs matter; these approximate rates are not an exact multi-point fitted latency law or a speedup measurement of the later optimization |
| CHANGELOG, README, unresolved rows | Same source and guards | Record imported results, source/tool entry points and remaining work; historical entries retained as history | Review/publication remain owner-owned; no push or tag |

No quality judgement or new quality result is added. The restored128k and post-prefill points retain their distinct
conditions, server-only rates remain separate from the uncalibrated bridge, and the request/generation denominators
are named. The real-mix observation concerns the measured calls and session counts; it does not prove a universal
queue or throughput model. Pending run14 client/import/B300 economics and kit1.6.6 measurements are explicit.

### Guard and control map

`offload_bound.py` retains the14 original run13 value/qualification checks and adds41 source-transcribed overnight
sites for each row and measurement boundary. It computes the original bounds/rates from the unchanged run13 CSVs;
it does not infer the overnight hardware measurements. The old pending-bridge wording is replaced by the actual
server-only boundary, with the first live bridge's finite qualification guarded separately. Self-test plants now
modify the matching paragraph, avoiding any same-spelling occurrence in an earlier paragraph.

`publication_v2.py` moves its authorized review base to the exact r9 head and explicitly refreshes all changed bytes
and numeric coordinates. All92 paper files remain registered;1847 numeric occurrences are pinned. The only paper
changes are04-channel,05-clients,05b-models (pending comment) and06-server. Historical exports/quote-ledger checks
retain their original source revisions. `test_paper_review.py` adds05-clients to its retained file list, so both
numeric and nonnumeric drift plants now cover all13 changed sections across r9/r10.

| Plant/control | What it narrows the gate to | Named rejecting test/check | Survival bound |
| --- | --- | --- | --- |
| First numeral changed in each aggregate/depth/ladder/cold row | Correct row, stream columns, depth and exact printed rates at their table marker | `offload_bound.py --self-test`: `overnight M3…`, `overnight M5…`, `overnight B300 ladder…`, `overnight B300 cold marginal…` | All applied plants rejected; source transcription is manually checked against the named facts, not independently reproduced on hardware |
| Changed request/generation denominator, warm lower bound, agent speed/p90/share or tool-output measurement | Exact finite observation and its stated conditions | `offload_bound.py --self-test`: `overnight parallel denominators`, `warm lower bound`, `agent stream speed`, `agent p90`, `Mac prefill share`, `PRO prefill share`, `large tool output` (each prefixed `overnight`) | All rejected; no chronological agent-model calibration is claimed |
| Changed cached B300 pair/block size or finite-portion comparison | Distinct cold marginal versus cached and finite-portion rates | `offload_bound.py --self-test`: `overnight B300 cached default`, `B300 cached FP8 KV`, `B300 portion comparison` | All rejected; no unmeasured FP8-KV depth row is supplied |
| Changed server-only/bridge values or heterogeneous/uncalibrated/finite qualification | Server-only throughput and finite approximate bridge evidence | `offload_bound.py --self-test`: `vLLM server-only qualification`, `overnight B300 server only`, `bridge export and probe`, `bridge BF16`, `bridge Q4`, `bridge heterogeneous uncalibrated`, `bridge finite qualification` (new names prefixed `overnight`) | All rejected; bit-exactness, calibration and full hybrid timing remain outside evidence |
| Changed fixed import amount/rate, long delta, Mac point or pre-optimization label | Fixed plus per-token/version/device boundaries | `offload_bound.py --self-test`: `overnight import fixed and token costs`, `import long delta`, `import Mac single point`, `import version qualification` | All rejected; approximate figures do not establish an exact import model or an optimized implementation's performance |
| Removed/changed cooled sweep, run14, depth or adapter TODO | Explicit non-delivery boundary | `offload_bound.py --self-test`: `overnight cooled sweep pending`, `agent gain pending`, `bridge depth pending`, `bridge adapter pending`, `B300 economics pending` | All rejected; pending results remain unqualified |
| Append nonnumeric prose to each of13 retained changed sections | Exact publication byte registry | `PaperReviewTests.test_review_sites_reject_prose_drift` | All rejected; byte integrity does not prove semantic truth |
| Append stale883 to each of the same13 sections | Complete numeric occurrence registry | `PaperReviewTests.test_review_sites_reject_unregistered_numbers` | All rejected; no scientific claim validation beyond the source-bound sites |
| Existing ranges/directions/tables/collisions and run13 offload plants | Unchanged numerical tolerances and old required claims | `check_ranges.py --self-test`;14 retained named `offload_bound.py --self-test` controls | Original controls retained; no waiver or relaxed tolerance |

Each guard first admits the unchanged text as its clean control, checks that its text plant was actually applied,
and requires the corresponding named rejection. These are text/control plants; no source-code mutation campaign or
new runtime attack-surface qualification is claimed.

### Build diagnostic

The first cache-only `make pdf` genuinely failed (exit2, `pdf-01.log`): the new math Delta table heading required
uncached `cmr9.pfb`. No download, installation or native build was attempted. Replacing the symbol with plain
`Порция` headers preserves every measured value and permits the same cache-only build (`pdf-02.log`, exit0).

Raw `git diff --check` exits2 on the generated site's CSV CRLF terminators. A diagnostic that assumed the previous
baseline used LF failed (exit1) before writing anything; the previous baseline actually contains1663 CRLF lines.
The CSV convention is preserved. `git -c core.whitespace=cr-at-eol diff --check` exits0, still rejecting added trailing
spaces while recognizing the established terminators. This diagnostic does not change a publication tolerance or site.

### R10 validation record

Standalone processes preserve their real exit statuses, with direct log redirection, disk-backed
`TMPDIR=$PWD/.temp/hybrid-c-r10-261102/tmp` and `PYTHONDONTWRITEBYTECODE=1`. All logs below are in
`.temp/hybrid-c-r10-261102/`. No GPU work, download or native build was performed.

| Standalone command | Exit | Evidence |
| --- | ---: | --- |
| `python3 paper/data/check_ranges.py` | 0 | `ranges-final-01.log` |
| `python3 paper/data/check_ranges.py --self-test` | 0 | `ranges-self-01.log`;156 site controls plus table/engine controls |
| `python3 paper/data/offload_bound.py` | 0 | `offload-final-01.log`;14 retained and41 new named claims |
| `python3 paper/data/offload_bound.py --self-test` | 0 | `offload-self-final-01.log`;all55 applied violations rejected, clean controls pass |
| `python3 calc/tests/r13_ledger.py`; `python3 calc/tests/publication_v2.py` | 0 /0 | `ledger-01.log`, `publication-final-02.log`;92files/1847numeric occurrences |
| `PYTHONPATH=calc/tests python3 -m unittest test_paper_review -v` | 0 | `review-controls-01.log`;4 tests including both13-file plant groups |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `kit-01.log`;24 tests in23.076s |
| `make pdf TECTONIC=$PWD/.temp/paper-v2-261101/tectonic-cached` | 0 | `pdf-02.log`;cache-only Tectonic0.17.0;initial exit2 preserved in `pdf-01.log` |
| Exact source/pin and finite style checks | 0 | `source-style-review-01.log`, `final-source-review-01.log`;875 engine/data/export/kit/snapshot files unchanged;320 gate files bound |
| `git -c core.whitespace=cr-at-eol diff --check` | 0 | `diff-check-crlf-01.log`;native CRLF diagnostic described above |

The corrected PDF has no overfull box, undefined reference or missing-character warning. Underfull-box warnings
remain. No PDF text/raster inspection tool is installed (`pdf-tools-readiness-01.log`); no rendered-page inspection
is claimed. Free disk observations remained above28GB; `disk-01.log` records33,506,865,152bytes (31.2GiB).
The scientific source and finite conditions were reviewed manually against the source map. This is a local review
candidate; no release, push, tag, independent acceptance or pending hardware qualification is claimed.

Full engine suite: `python3 -m unittest discover -s calc/tests -v`, **exit0**,281 tests in598.691s,
`engine-01.log`, including all retained historical provenance and reviewer/publication tests. The320 bound
source/test/configuration/publication files remain unchanged throughout this run. Signing and exact-head build
follow only after this green result. Required manifest generation/readback is recorded below before signing.

Manifest checkpoint: `make manifest` and `sha256sum -c MANIFEST.sha256` each exit0
(`manifest-01.log`, `manifest-verify-01.log`). The manifest is regenerated after this record and checked again
before signing, with final logs `manifest-final-01.log` and `manifest-verify-final-01.log`. This candidate is ready
for review; independent acceptance, hardware follow-ups and owner publication remain outside this local task.


## Run14 integration and publication migration (hybrid-c-r11-261102)

Authorized publication base `8a96246e0f280dd9866be0f5af9159eebd0dde75`; engine input `2d457aed87d415043a2c0566f7a185607f11487e`.
Signed merge `103cccfb41ef70d61b464a5af06d1d5dde9005c1` has those exact parents. No push/tag/download/native build.
The merge preserves engine implementation, all110 run14 files, report,89163-row quote ledger and three R14-R5 CSVs byte for byte.
`r14_audit.py` was rerun in `.temp/hybrid-c-r11-261102/engine-control` at the exact engine head: exit0, clean git status afterward.
All115 payload files match the integrated checkout, and all150 historical plus252 run13 exports remain frozen.
Evidence: `engine-export-02.log`, `engine-byte-identity.json`. An initial audit was started from the publication cwd by mistake;
own PID1029725 was stopped with SIGTERM (shell exit143) before prose-dependent ledger generation. The corrected exact-head run supersedes it.

The61 embedded CSVs copy run14 base exactly. Five figure inputs are regenerated, including the symmetric team chart
at5/10/20/50/500/5000 people. Fixed-B300/API tables are explicitly hardware references; optimized architecture claims
and the main team-size figure use the symmetric snapshot. Both routes may use HBM/RAM/NVMe, retain four sessions/person
for a full month, and share mean28.2s/p9077.1s prefill limits and70%load, excluding queues. The artificial500-person paragraph is removed.

### Changed values (old r10 publication to current R14)

Each row retains its publication scope; snapshot formulas compute the new direction. Rounded equal endpoints collapse
without changing precision. Legacy policy-site names map explicitly in `calc/tests/data/paper-r14-migration.json`.

| Claim | Old | New |
| --- | --- | --- |
| medium, design | `2.6--2.9` | `2.2--2.4` |
| medium, conservative | `2.1--2.5` | `2.0--2.2` |
| medium, both cases | `2.1--2.9` | `2.0--2.4` |
| light at 50 and 5000, design, percent | `27--39` | `27--35` |
| light at 50 and 5000, conservative, percent | `3--22` | `17--30` |
| light at 500, own against hybrid | `\$34 на человека в месяц против \$46` | `\$32 на человека в месяц против \$21` |
| light at 500, cautious symmetric comparison | `около \$22 (при осторожной политике \$29) против \$38 у своего кластера на тех же серверах и \$34 на узле B300` | `При осторожной политике на 500 человек гибрид стоит \$25 против \$35 у своего кластера` |
| heavy saving, design | `22--24` | `20` |
| heavy saving, conservative | `18--22` | `19` |
| symmetric hardware without team cap | `для команд до 100 человек` | `без ограничения размера команды` |
| symmetric retention budget | `узлы B300 начиная с 50` | `одинаковые сроки хранения и число сохраняемых сессий` |
| symmetric latency budget | `узлы B300 для команд от 50` | `одинаковые ограничения среднего и p90 времени prefill` |
| own server for five people | `\$145--506` | `\$147--437` |
| own server for twenty people | `\$63--506` | `\$39--367` |
| own server for five people, light load | `от \$145 на человека в месяц при лёгкой нагрузке` | `от \$147 на человека в месяц при лёгкой нагрузке` |
| cards for five people | `нужна одна такая карта при лёгкой нагрузке и четыре, по две в сервере, при тяжёлой` | `нужна одна такая карта при лёгкой нагрузке и три при тяжёлой` |
| cards for twenty people | `нужны две карты при лёгкой нагрузке и шестнадцать, по две в сервере, при тяжёлой` | `нужна одна карта при лёгкой нагрузке и десять при тяжёлой` |
| B300 node per person, five people | `\$3\,370` | `\$3\,373` |
| B300 node per person, twenty people | `\$843` | `\$845` |
| storage against prefill | `хранение стоит \$6.9 в месяц, меньше, чем сам prefill (\$10.0)` | `хранение стоит \$6.4 в месяц, меньше, чем сам prefill (\$54.9)` |
| s20 hybrid dollars | `\$27--32 в месяц` | `\$67--77 в месяц` |
| s20 below median, all clients, both cases | `2.5--3.8` | `1.2--1.5` |
| s20 above cheapest, all clients, both cases | `1.9--2.9` | `4.8--6.1` |
| s20 below median, Max clients, both cases | `2.5--3.5` | `1.2--1.4` |
| s20 below median, all clients, design | `3.2--3.8` | `1.3--1.5` |
| s20 above cheapest, all clients, design | `1.9--2.3` | `4.8--5.4` |
| s20 below median, all clients, conservative | `2.5--2.7` | `1.2` |
| s20 above cheapest, all clients, conservative | `2.7--2.9` | `5.9--6.1` |
| s50 M5 Max capacity | `около 840 вызовов` | `около 820 вызовов` |
| s50 Max dollars | `\$52--55 в месяц` | `\$104--130 в месяц` |
| s50 below median, Max clients | `4.6--4.9` | `2.0--2.4` |
| s50 above cheapest, Max clients, percent | `49--55` | `196--268` |
| s50 below median, Max clients, overflow at median | `1.5--2.4` | `1.1--1.3` |
| s50 share served by Max clients | `от 49 до 75\%` | `от 45 до 69\%` |
| s50 Ultra dollars | `обходятся в \$48--50` | `обходятся в \$150` |
| s50 Ultra conservative dollars | `и в \$66--67 при осторожной политике` | `и в \$178--179 при осторожной политике` |
| s50 above cheapest, Ultra clients, percent | `37--42` | `327` |
| s50 below median, Ultra clients, both cases | `3.8--5.3` | `1.4--1.7` |
| purchase at 50% | `стоит \$89 против \$35 у самого дешёвого API и \$254 у медианного` | `стоит \$160 против \$35 у самого дешёвого API и \$254 у медианного` |
| purchase at 20% | `\$65 против \$102` | `\$109 против \$102` |
| purchase against cheapest | `дороже его на \$54 в месяц` | `дороже его на \$125 в месяц` |
| teams at 500, 20% | `(\$101 против \$102 при доле 20\%` | `(\$674 против \$102 при доле 20\%` |
| teams at 500, 50% | `\$202 против \$254 при доле 50\%` | `\$1685 против \$254 при доле 50\%` |
| payback s50, overflow to cheapest | `за 13 месяцев, Мак целиком за 25` | `за 20 месяцев, Мак целиком за 40` |
| payback s20, overflow to cheapest | `за 36 и 71 месяц` | `за 92 и 181 месяц` |
| payback s50, overflow to median | `за 21 месяц` | `за 50 месяцев` |
| payback s50, overflow to median, whole | `целиком за 40` | `целиком за 97` |
| payback, dearer than cheapest | `16--19` | `59--90` |
| GLM two sessions, hybrid | `гибрид обходится в \$4.4--4.6 за сессию` | `гибрид обходится в \$5.8--6.2 за сессию` |
| GLM two sessions, own cluster | `свой кластер стоит \$4.01` | `свой кластер стоит \$4.81` |
| GLM two sessions, own cluster at 5000 | `на 5000 человек \$3.37` | `на 5000 человек \$4.49` |
| GLM 50 people | `(\$8.02) немного дешевле API (\$9.15), а гибрид с отдельной Studio на каждого дороже обоих (\$11.85)` | `(\$8.02) немного дешевле API (\$9.15), а гибрид с отдельной Studio на каждого дороже обоих (\$11.78)` |
| GLM Studio utilization at two sessions | `меньше чем на треть` | `на 34\%` |
| GLM Studio capacity | `почти семь сессий` | `почти шесть сессий` |
| GLM full load, Studio share | `до \$1.05 на сессию` | `до \$1.19 на сессию` |
| GLM full load, hybrid session | `\$1.8--1.9` | `\$3.3--3.4` |
| GLM full load, below API | `4.8--5.1` | `2.7--2.8` |
| GLM full load, below own cluster | `1.9` | `1.3--1.4` |
| GLM four sessions, below API | `3.3--3.6` | `2.1--2.3` |
| GLM four sessions, hybrid | `\$2.5--2.8, в 1.3 раза дешевле своего кластера` | `\$3.9--4.3, в 1.1 раза дешевле своего кластера` |
| GLM four sessions, below own cluster | `в 1.3 раза дешевле своего кластера и` | `в 1.1 раза дешевле своего кластера и` |
| GLM shared Studio | `двое и каждый проводит по две сессии в день, \$2.6--2.9` | `двое и каждый проводит по две сессии в день, \$4.1--4.4` |
| GLM two sessions, dearer percent | `гибрид дороже своего кластера на 15--30\%` | `гибрид дороже своего кластера на 28--30\%` |
| GLM one session, dearer factor | `при одной в 1.9--2.4 раза` | `при одной в 2.1--2.2 раза` |

Client rows below give local/day, hybrid/day and gain at1Gbit/s with four agents; single-stream rates are32k.

| Client | Old local / hybrid / gain / tok/s | New local / hybrid / gain / tok/s |
| --- | --- | --- |
| M3 Max 128 GB (measured) | 3.37 / 5.31 / 1.57 / 8.44 | 3.21 / 4.87 / 1.52 / 8.44 |
| M4 Max 128 GB (estimate) | 5.24 / 7.18 / 1.37 / 11.52 | 5.24 / 7.06 / 1.35 / 11.52 |
| M5 Max 64 GB | 5.61 / 7.22 / 1.29 / 18.29 | 5.61 / 7.07 / 1.26 / 18.29 |
| M5 Max 128 GB | 6.86 / 8.05 / 1.17 / 12.96 | 5.78 / 7.45 / 1.29 / 18.29 |
| M5 Ultra 96 GB | 13.41 / 15.31 / 1.14 / 25.91 | 11.22 / 11.22 / 1.00 / 36.58 |
| M5 Ultra 256 GB | 14.13 / 15.60 / 1.10 / 25.91 | 12.09 / 12.09 / 1.00 / 36.58 |
| Strix Halo 128 GB | 3.04 / 3.43 / 1.13 / 5.40 | 3.04 / 3.41 / 1.12 / 5.40 |
| DGX Spark 128 GB | 3.52 / 3.66 / 1.04 / 5.76 | 3.52 / 3.52 / 1.00 / 5.76 |

| Additional conclusion | Old | New |
| --- | --- | --- |
| Agent-count gain | Pending | Seven full-mix1G rows; four agents3.212→4.867/day,1.515x; sixteen3.933→6.811/day,1.732x |
| Sixteen-agent evidence zone | Unstated | Modelled-depth77.68%calls/71.12%decode-device time; overlapping count fallback24.09%/43.32%, lower-bound18.02%/21.31%, shallow15.37%/8.06% |
| M5 basis | Max128 scaled from M3; Ultra from M3 peaks | Same measured Max SoC for Max64/128, Ultra scales measured Max curves; uncalibrated import portability |
| B300 prefill capacity at20/50/100% |127/50/25people |27/11/5people, measured llama.cpp fit |
| Ideal-client B300 ceiling at110k |12.1x,0.72PFLOP/s |2.0x,0.12PFLOP/s; all original1e-9 agreements retained |
| Cheapest-API break-even | No prefill threshold analysis | Measured clients at20%: overhead floor alone exceeds API; no break-even. M5 Max64 at50% has0.01558USD/MTok; estimated Ultra256 at20%0.11649USD/MTok |
| Median-API threshold | Absent |4.7–5.4USD/MTok for already-owned clients,20%,protocol storage |
| Measured unit costs | Absent |llama.cpp PRO6000 0.62–0.63; vLLM PRO6000 0.26, B300 auto0.31, B300 FP8KV0.23USD/MTok; vLLM server-only |
| Same-config5G prediction | Pending |179.5s predicted vs201.7s measured;25.5s measured residual preserved; import agreement is calibration |
| Step57 validation | Pending |Local elapsed underprediction8/22/37/33%at1/2/4/8sessions; analytical server bound81–86%below observations |
| vLLM31,360-token bridge | Pending |BF16 KL0.0031/Q4_K_M0.0061nats; top1 64/64each; no64-token free-run divergence; checker5,heterogeneous/uncalibrated |
| Task pilot | Pending |35/48correct each treatment; offload4/48, different local partition4/48, same-partition repeat0/48;128kpartial, no equivalence claim |
| Node-adapter smoke | Pending | Functional B300 smoke supplied:8k KL0.0055/top1 63/64/ratio0.87;32k0.0256/60/64/2.38; free-run divergence9, checker5 heterogeneous/uncalibrated |

All changed channel tables (turn, cold ingestion, transcript, offload shares/saved time), client rows, new agent rows,
price components/verdicts and qualifications have snapshot-derived named controls in `offload_bound.py`.
The transcript M5 row intentionally retains the engine's M3-curve portability basis, explicitly labelled;
GLM cold-ingest454s excludes import, while GLM session economics includes the uncalibrated import coefficient.
Price floors hold routing and overflow supplier fixed; no negative prefill/storage price is invented.

### Guard migration and finite fault evidence

No prior range or offload site is removed. The range inventory retains156 value/direction sites; all55 old offload
names remain plus67new sites (122total). The exact inventory test fails if a prior site disappears.
The current publication pins112files and all numeric occurrences, recomputes five chart inputs, and copies61CSVs exactly.
Accepted R13 r3 reviewer tests run at49a1c1d3 in the historical fixture under their original names; current reverse
plants use the current publication baseline. No historical ledger, waiver or export is rewritten.

| Plant / mutant | Property narrowed to | Named failing guard / test | Survival bound |
| --- | --- | --- | --- |
| Stale value or flipped wording at each156old sites | Every original scope and computed direction, including replacement symmetric requirements | `check_ranges.self_test`, each named value/direction line in log | All rejected; finite listed sites only |
| Removed large-team RTX option | No artificial cap reintroduced | `closed: light at500, hybrid cheaper with uncapped hardware` | Rejected; other architecture search is not independently reimplemented |
| Changed retention, p90 budget, or cap policy in candidate rows | Shared budgets and uncapped options | `test_symmetric_budget_guard_rejects_each_asymmetry` | All three rejected; no hardware scheduler qualification |
| Wrong value/row/qualification at every offload site | Original55plusnew tables, import/zone/quality boundaries | `offload_bound.main --self-test`, each named line | All rejected, clean control passes; finite source transcriptions |
| Old/new same-rounded ranges swapped | Scalar bound to its own comparison clause | `check_ranges.value_at`, named156-site controls | Initial plants survived before clause binding; corrected controls reject all |
| New numbers/prose in every changed TeX section | Exact numeric occurrence and byte contracts | `test_review_sites_reject_unregistered_numbers`, `test_review_sites_reject_prose_drift` | Rejected; semantic correctness still requires source review |
| Overheads replaced by prefill-price cause, vLLM server-only erased, thresholdx10 | Price verdict and qualification remain explicit | `test_price_boundary_preserves_exception_and_no_break_even` | All rejected; finite20/50%controls |
| Wrong payload or stale embedded row | Exact producer bytes and snapshot identity | `test_engine_payloads_and_embedded_snapshot_keep_exact_bytes` | No drift admitted; fresh audit binds exact source head |

The first self-test exit1 exposed duplicate numeric phrases after migration. Binding both2.0–2.4claims to their own
clauses fixed the two survivors. Collapsing20–20/19–19then exposed two scalar collisions; heavy-load checks now bind
both the load and policy clause. Numeric rounding was unchanged, but r11 weakened the B300 check by replacing
cross-profile uniqueness with a minimum. The r12 correction below restores unique-row checks in the explicit
light-load, one-node scope. New incidental25.9offload-share and28.2latency-budget collisions are narrowly
registered by their exact rows and reasons; the original Ultra collision site remains mandatory at its new36.6rate.

The brief has no surface table or separate landing-property suite (brief gap). No requested row is treated as
out of contract. This is a local publication migration, not GPU or task-equivalence qualification. Integrated-paper independent review remains with the orchestrator.
Engine r5i ACCEPTS exact2d457aed (review file REVIEW-engine-r14-muse.md); producer-green checks do not close
the integrated-paper review. Pending Mac import-v2, cooled sweep, heterogeneous/KL/SWA/growing-session
and5G rerun gates remain explicit. No downloads/native builds/GPU work; measured archives were read, not rerun.

### Validation record

Logs below live under `.temp/hybrid-c-r11-261102/`; every gate ran standalone with disk-backed TMPDIR and
PYTHONDONTWRITEBYTECODE=1. Final statuses are appended after processes exit. Required available disk remains>28GB;
observed samples so far32–33GB. Initial cache-only PDF attempts exit2 on absentcmr5/cmmi6fonts; explicit numeric
tick labels preserve the graph data while using cached fonts. No cache or network fallback is authorized.

Orchestrator follow-up (inbox-05) is applied without an engine delta. The16-agent caption now prints the flag union
99.7%calls/97.4%decode time and all four overlapping flag shares adjacent to the row. The symmetric comparison is
explicitly cost-driven:0of2106default candidates (also0of2106cautious candidates) violate the common latency budget.
The node-smoke TODO is replaced by the newly supplied functional measurement; cross-quantization calibration and
full-path speed remain unqualified. FACTS-source-02.md preserves the updated source; no node hardware run was repeated.

The initial full engine suite ran331tests in672.348s and exited1 (12failures,1error). Eleven failures were the
unregistered28.2budget/refill collision during migration; the exact-row collision registration fixes them.
The remaining failure came from applying historical native-collision exceptions to current lines: that direct control
now uses its original49a1c1d3source for both its positive site and new-line plant. The error was an omission fixture
still searching for old6.9/1.8coordinates; the current storage/latency witnesses are6.4/179.5. Test names and rejection
assertions remain. Corrected five-regression rerun exits0 (174.617s), both fixture regressions exit0 (0.733s),
and the nine publication/review controls exit0 (3.829s). A new full stable-source suite is required below.

Current preliminary gates: range self-test156sites exit0 (`ranges-self-05.log`); offload self-test119sites exit0
(`offload-self-03.log`); publication guard112files/2023occurrences exit0 (`publication-03.log`); kit24tests exit0
(`kit-01.log`,41.813s); cache-only PDF exit0 (`pdf-04.log`, no overfull/undefined/missing-glyph warnings).
The exact source constants and generated latency observation were subsequently made explicit; final same-source
checks and the stable full engine suite follow. No passing initial full-suite claim is made.

Final source readback found three independently unbound channel-prose sums:61→62seconds for the100Mbit/s large turn,
432→429seconds and161→157seconds for the200k cold call, and71→70USD for monthly compute+hosting at the capped M3 load.
The tables already carried the correct snapshot values. Three new named guards bind these narrative sums directly
to `turn_speedup`, `oneshot_ingest` and `person_cost_s50`, with the same clean/planted controls (122offload sites total).
This bounded correction does not alter the engine or tables; final full-suite evidence must include this source.


### Final same-source validation

Final tested source is signed `e5b4fcddb3f14f0218fb76372f9a1a430030d93a`. All305source/test/publication files
in `final-source-identity.json` were rehashed after the suite and remained unchanged. The final evidence commit
changes this gap map and the repository manifest only. The engine implementation, inputs,115producer payloads,
61embedded CSVs, five derived CSVs and checker/test code keep the tested bytes.

| Standalone command | Actual exit | Evidence |
| --- | --- | --- |
| `python3 -I calc/tests/r14_audit.py` at exact producer head |0|`engine-export-02.log`;115files identical,110under run14, clean producer checkout |
| `python3 -m unittest discover -s calc/tests -v` |0|`engine-03.log`;331tests,499.008s, including retained historical reviewer tests |
| `python3 -m unittest discover -s bench/tests -v` |0|`kit-01.log`;24tests,41.813s; bench tree byte-unchanged from input publication |
| `python3 paper/data/check_ranges.py` |0|`ranges-final-01.log` |
| `python3 paper/data/check_ranges.py --self-test` |0|`ranges-self-06.log`;156retained site plants plus table/engine/collision controls |
| `python3 paper/data/offload_bound.py` |0|`offload-final-01.log` |
| `python3 paper/data/offload_bound.py --self-test` |0|`offload-self-05.log`;122named applied plants and clean control |
| `python3 calc/tests/publication_v2.py` |0|`publication-05.log`;112files,2023numeric occurrences, exact snapshot and derived tables |
| `make pdf TECTONIC="$PWD/.temp/paper-v2-261101/tectonic-cached"` |0|`pdf-06.log`;strictly cache-only, no overfull/undefined/missing-glyph warnings |
| `make manifest` |0|`manifest-03.log`;unchanged on tested source |
| `git verify-commit HEAD` |0|`numeric-signature-01.log`;merge and both implementation commits showG |

The final-source PDF SHA256 is `31bd217290a29ee6e7cdb75d22d86b3ce97887c24044f680980e02dfa896dbe9`.
A rebuild after the evidence-only commit updates the draft's git label; its receipt and final signature/status
are stored in task-scoped logs. Minimum sampled available space was29.395GiB, above28GiB; no downloads,
native builds, push or tag. FACTS source hashes: initial
`d70dc4acc99bf856ece9f81332c3436659e2a4f7fb23c3977b78009b95675527`, updated node-smoke source
`7607c11bf7ed1b655ed82a96264bf153741bc234e9dae43ec2cda1d36c6c2ccd`.

Superseded `engine-02.log` was stopped by its recorded own PID1057432after the three channel narrative corrections
made its source identity obsolete: actual shell exit143, never a passing gate. The original wrong-cwd audit likewise
returned143. Final331-test exit0above supersedes both incomplete/failed suite attempts. All negative-control families
now reject by the named assertion, with no surviving plant claimed as killed. The original claim of no tolerance
change was incorrect for B300 cross-profile uniqueness; the r12 correction below records the scoped replacement.
The local candidate is ready for integrated-paper review; engine r5i acceptance alone does not accept the paper.

## Three r5j minors (hybrid-c-r12-261102)

Base: `5fc78ed5d218dcf434ad36c17bc7e56d079c8e80`, existing `paper-v2` branch. Review authority:
`/home/agent/Werkstatt/hybrid-review/paper/.temp/REVIEW-paper-v2-run14-muse.md` (0 blockers, 0 majors, 3 minors).
The delta changes two TeX sections, their checker qualifications and publication pins, four regression tests,
and the related documentation/manifest. Engine implementation, inputs, exports, embedded CSVs and chart data
are outside this rework and retain their reviewed bytes. No separate surface table or landing-property suite
was supplied (brief gap); existing publication properties and all prior reviewer tests remain required.

The traffic day-capacity sentence names the client in the same sentence, fixing the r5h m2 repeat class.
The named `run14 traffic day client subject` guard binds that sentence to the snapshot's rounded 565 calls.

The B300 $3,373 (five people) and $845 (twenty people) references now explicitly mean **light load, one node**
at all three text sites. `own_servers()` requires exactly one all-server B300 row for each team in that profile,
including rejecting duplicate rows with equal prices, and asserts `units == 1`. It reads that row's
`person_month`, preserving the exact prior rounding. Other profiles are outside these two quoted amounts:
at twenty people, medium/heavy loads use two/four B300 nodes and cost $1,687/$3,375 per person.
The PRO 6000 ranges still span light through heavy load; the adjacent B300 amount is explicitly light-only.
This corrects r11's lost scope: cross-profile price uniqueness had been replaced by `min()` without a qualifier.
The earlier no-tolerance-change records above and in `CHANGELOG.md` are corrected; they were not evidence
that the original B300 invariant survived. Row uniqueness in the explicit light profile is stronger than
uniqueness of the price set in that profile. Cross-profile equality is no longer claimed.

The economics caption now names measured M3 Max and M5 Max 64 GB curves, the same-SoC transfer to M5 Max
128 GB, and Ultra scaling from measured M5 Max curves by compute and memory bandwidth. It explicitly denies
separate 128 GB/Ultra measurements and keeps M4 Max estimated. The economics table contains no Strix/Spark row.

| Plant / mutant | Property narrowed to | Named failing test / guard | Survival bound |
| --- | --- | --- | --- |
| Restore the day sentence's orphan pronoun | Noun in this sentence, the r5h m2 repeat class | `test_traffic_day_sentence_names_client_r5h_m2`; `run14 traffic day client subject` | Rejected; finite named sentence, no general Russian grammar checker |
| Duplicate equal/different B300 light row, remove light row, or set two nodes, at both team sizes | Unique scoped record and one node, rather than minimum or equal-price set | `test_b300_light_reference_requires_unique_one_node_row`; `B300 light profile: exactly one row/one node for team 5/20` | All eight rejected; fleet sizing for other profiles remains engine-owned |
| Replace medium/heavy B300 costs with $1 | Other profiles cannot select the light-only price | `test_b300_light_reference_ignores_other_profiles` | Valid out-of-scope variation passes and printed values remain unchanged; this is a positive scope control |
| Erase each B300 qualifier or restore stale M5 basis | All three price sites and the economics caption retain their basis | `test_r5j_economics_scope_and_m5_basis_reject_stale_wording`; four named `run14 B300 light reference` / `economics M5 measured basis` guards | All rejected; no hardware measurements rerun |

Regression-before-02 ran the first three tests against the prior implementation and exited 1 with ten intended
assertion failures and no setup errors. Regression-before-01 also exposed two test-fixture API mistakes; those
errors were corrected and are not claimed as property detections. Regression-after-01 ran all four new tests
and exited 0. Standalone full-gate exits and final candidate evidence are recorded after execution below.
Logs: `.temp/hybrid-c-r12-261102/`; CPU only, no downloads/native builds, disk-backed `TMPDIR`,
`PYTHONDONTWRITEBYTECODE=1`, available disk must stay above 28 GB. No push or tag is authorized.

Direct task-local plants (`python3 .temp/hybrid-c-r12-261102/planted_b300.py duplicate` / `two-nodes`)
each exit 1 by the intended `B300 light profile: exactly one row for team 20` / `one node for team 20`
assertion; `clean` exits 0 with unchanged printed amounts. These are expected-red controls, not passing gates.
The range and offload checkers and their self-tests exit 0 (`ranges-01.log`, `ranges-self-01.log`,
`offload-01.log`, `offload-self-01.log`); the range self-test retains 156 site controls plus the new B300 controls,
and all 127 offload controls reject by name with a clean control. Publication guard exit 0 pins 112 files and
2026 numeric occurrences. The baseline changes exactly the two edited sections and two checkers; three added
numeric tokens are the caption's explicit 128/64/128 GB transfer, with all other printed forms preserved.

The complete engine run passed at signed candidate `115db98e7d6aca3aa122775b368944d1c6f91bad`:
335 tests in 551.933 seconds, including all retained reviewer tests. All 1208 tracked files were rehashed
after the run and matched the recorded test identity. The evidence commit changes only this gap map and
`MANIFEST.sha256`; source, tests, configuration and publication pins retain the tested bytes.

| Standalone command | Actual exit | Evidence under `.temp/hybrid-c-r12-261102/` |
| --- | --- | --- |
| `PYTHONPATH=calc/tests python3 -m unittest test_paper_r14 -v` | 0 | `r14-controls-01.log`, 9 tests |
| `python3 -m unittest discover -s calc/tests -v` | 0 | `engine-01.log`, 335 tests |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `kit-01.log`, 24 tests in 19.816 seconds |
| `python3 paper/data/check_ranges.py` | 0 | `ranges-01.log` |
| `python3 paper/data/check_ranges.py --self-test` | 0 | `ranges-self-01.log`, 156 retained sites and scoped B300/table/engine/collision controls |
| `python3 paper/data/offload_bound.py` | 0 | `offload-01.log` |
| `python3 paper/data/offload_bound.py --self-test` | 0 | `offload-self-01.log`, 127 named plants with clean controls |
| `python3 calc/tests/publication_v2.py` | 0 | `publication-01.log`, 112 files / 2026 numeric occurrences |
| `python3 calc/tests/r13_ledger.py` | 0 | `ledger-guard-01.log`, current publication entry point |
| `make pdf TECTONIC="$PWD/.temp/paper-v2-261101/tectonic-cached"` | 0 | `pdf-01.log`, wrapper enforces `--only-cached` |
| `make manifest` | 0 | `manifest-01.log` |
| `sha256sum -c MANIFEST.sha256` | 0 | `manifest-check-01.log`, 1207 files |
| `git verify-commit HEAD` | 0 | `signature-01.log`, machine identity and requested Codex trailer, signature G |

The tested-candidate PDF SHA-256 is `374d311f7f2eb6464712ede78fb3f7e4ee6bc913d5a64770c456abbe03834382`.
No overfull, undefined-reference or missing-character warnings occurred; underfull warnings remain.
The post-evidence-commit rebuild changes the draft's git label; its exact-head PDF hash, signature and clean
status are persisted in the task receipt and sent to the orchestrator. Minimum sampled free space is
29,309,693,952 bytes (>28 GB), with subsequent samples above 35 GB (`disk-samples.jsonl`).

Out-of-contract surfaces: engine modelling, fleet optimization and raw measurement reproduction are unchanged
under task items 1–3 (paper/checker corrections only); GPU work, downloads and native builds are excluded by
the task's explicit CPU-only rule. No prior reviewer test was removed, no separate landing suite was supplied,
and no new measurement or independent paper acceptance is claimed. The local candidate is ready for review.

## Public-clone history independence (hybrid-c-r14-261102)

The incident lane correctly rejected the previous local-only 335-test evidence:
`historical_fixture()` required private `49a1c1d3`, and further content reads
also depended on author history. The owner-signed draft `b809942d` / tree
`218ccc453b9b13f6597c9b15c00ef449d9733c45` remains the superseded packet; its
passing local suite does not prove public-clone acceptance.

### Complete executable history-read inventory and replacement

The inventory covers tracked Python, shell, Makefiles and hosted workflows,
including the original source inside the historical fixture. Original source
bytes remain immutable data; only the explicitly recorded I/O adapters execute
in their place. No original test assertion, numeric tolerance, waiver or site
requirement changes. All existing test names are retained.

| Reader / operation before correction | Original reference(s) | Release replacement / retained bound |
| --- | --- | --- |
| `publication_history.historical_fixture`: `git archive`, `rev-parse --absolute-git-dir`, `.git` pointer | `49a1c1d38233f8edbbc1150c3e28dd69adb72997` | `r13-publication` exact source plus separately hashed `r13-io-adapters`; no git pointer. Original regression test files unchanged; four adapter modules preserve every assertion. |
| `r10_controls.revision_csv`, `history_present`, `local_git`: `cat-file`, `ls-tree`, `show`; optional original-history comparison in `test_history_archive_matches_record_and_git` | R9 `e9db8129887126ca6a5d27066dd4f4519d223c2d`, R10 `1e8f897c4f82092c632507b520515cefa7eecab5` | `r9-paper` / `r10-paper` content-addressed bytes, full hash/size/blob-ID validation, independent legacy archive equality. Actual private-history comparison moved to `tools/dev/history_audit.py`, **dev only**. Synthetic partial-clone/no-fetch controls remain, with self-created object IDs. |
| `r11_audit.old_bytes` and `audit`: R10 fallback and `git show` generator identity | R10 above; `a57db67fb1163f59487ac829c01730efdaa186fc` | R10 fixture plus exact `r11-paper` generator manifest; all cell/coordinate and 42-CSV assertions retained. |
| `r12_audit.frozen_files`: `ls-tree`, `show` | `a57db67fb1163f59487ac829c01730efdaa186fc` | Full `r11-paper` path set and verified bytes; unchanged hash comparisons. |
| `r13_audit.frozen`, `quoted`: `ls-tree`, `show` | `7c2e9b1e8e87835f474ae45a4454bda74f4af6d3`, `c04a99dd06a9cf97f57baeb856e471b7b987c611` | `r12-paper` exact exports, `r12-architecture` original CSV. |
| `r13_reverse.old_api_results`, `changed_pairs`: `git archive`, `git show` | `7c2e9b1e8e87835f474ae45a4454bda74f4af6d3`, `02f4b6fde9d5691951a6a19d8596b22d016bedd1` | Execute exact `r12-source` engine/inputs; compare exact four `r13-derived` predecessor CSVs. No canned API outputs or mocked comparisons. |
| `r13_ledger.native_ranges`, `native_changes`, native dependency check; `r13_quotes.supplement`: `git show` | `c04a99dd06a9cf97f57baeb856e471b7b987c611` | `r12-architecture`; unchanged row identity, formula, precision and site assertions. Same I/O substitutions in the archived historical modules. |
| `r14_audit.frozen`, `quotes`, `changed_outputs`, `conclusions`: `ls-tree`, `show` | `49a1c1d38233f8edbbc1150c3e28dd69adb72997`, R4 `785334ab5d3ad145ecd9f6d2621d34e9a6314c24` | `r13-exports` (150 paper + 252 run13 files), `r14-r4` (103 files); same counts, exact file sets, bytes and per-cell comparisons. |
| `test_run13.test_new_manifests_and_server_only_flags`: `git show` | `49a1c1d38233f8edbbc1150c3e28dd69adb72997` | Exact `r13-exports` generator manifest, all 25 sidecar checks retained. |
| `test_r13_reverse.test_native_collision_rejects_same_file_21_6_at_new_line`: `git show` | `49a1c1d38233f8edbbc1150c3e28dd69adb72997` | Exact `r13-publication` channel source; accepted original and rejected copied site unchanged. |
| `test_paper_r14.test_engine_payloads_and_embedded_snapshot_keep_exact_bytes`: `ls-tree`, `show` | `2d457aed87d415043a2c0566f7a185607f11487e` | All 252 selected `r14-producer` payloads, same exact-byte and embedded CSV set checks. |
| Reviewed paper custody (previously documentary, no runtime lookup) | `1a45cd2269fa8ea1a7027936a1f0bb35586460de` | `reviewed-paper` fixture; new positive control compares all 112 reviewed paper files byte-for-byte. |

All 13 snapshots share 821 SHA-256-addressed objects. The manifest records full
original commits only as provenance; release readers select named snapshots,
never a git ref. The loader pins the manifest independently and verifies hashes
and lengths before exposing bytes; extraction verifies the complete snapshot
before writing anything. An unknown snapshot, missing object, altered byte,
manifest rewrite or unrecorded object fails explicitly. There are no skips,
network fallbacks or replacement expected values. The legacy R9/R10 archive is
retained as an independent byte witness and parser-control input, with named
folders and the same original per-file SHA256/blob IDs.

### Git operations that remain, and explicit coverage gaps

- `publication_v2.tracked_files()` and `make manifest` read only the current
  checkout index (`git ls-files`). These require no historical object.
- `.scripts/version.sh` reads the current `HEAD`, date and available public tags;
  `make pdf` reads the current commit timestamp. Draft labels may differ after
  an owner recommit. They do not resolve private source refs.
- `.scripts/release-check.sh` intentionally resolves the actual release tag,
  `origin/main` (or explicit release branch), ancestry, annotated tag object,
  signer pin and changelog. This production authorization gate is unchanged;
  no fixture can replace its real owner signature and landed ancestry. The
  release script fixtures create every tested commit/tag/key in throwaway
  repositories. The real rc.2 tag gate remains incident-lane owned.
- `bench/{mac,gpu}/scripts/10-build-llama.sh` resolves `LLAMA_COMMIT` in its own
  clone of public `ggml-org/llama.cpp`, fetching if absent. This is an external
  measurement-kit/native-build dependency, not a paper-history dependency;
  these native builds are outside this CPU-only correction and were not run.
- `tools/dev/history_audit.py` is explicitly excluded from release acceptance.
  An audit of an author's live branch/object database is a developer custody
  check, not reproducibility evidence for patch-based public readers. Its
  original R9/R10 equality check passes locally; synthetic no-fetch controls
  retain the original positive, negative and trace-detector controls.
- No surface table was supplied. This correction claims the listed content
  custody and fixture integrity bounds, not new engine/hardware measurements.

### Negative controls and preliminary verification

| Plant | Property narrowed to | Named failing test / check | Bound |
| --- | --- | --- | --- |
| One changed fixture byte | SHA256 before comparison/extraction, no partial extraction | `test_altered_object_rejected_before_extraction` | The isolated selected snapshot; pristine bytes are the positive control. |
| Missing fixture object | No git fallback, regeneration or skip | `test_missing_object_rejected` | Explicit missing-file failure. |
| Manifest rewritten to authorize forged bytes | Manifest's independent code pin | `test_manifest_rewrite_rejected` | Updating fixture authority requires a reviewed code-pin change. |
| Extra object / unknown snapshot | Exact immutable object inventory / named snapshot authority | `test_unknown_snapshot_and_extra_object_rejected` | No directory-wide exemption. |
| Adapter removes/changes historical assertion or edits original test | Original assertion AST / exact test bytes | `test_historical_assertions_and_tests_are_preserved` | Structural check supplements execution of the original eight regression tests. |

The controls above assert the intended failure against real fixture reads; they
do not mock comparisons. Narrow gates: R10 7 tests exit0, reverse 15 tests exit0,
fixture controls 6 tests exit0 before the additional reviewed-paper positive
control, selected historical/source tests 4 tests/87.898s exit0. The dev-only
R9/R10 audit exits0 (42 exact CSVs each). One import cleanup introduced an
indentation error in `r13_quotes.py` (syntax probe exit1); the exact source was
restored and the precise I/O edit reapplied, syntax probe exit0. No failing
probe is counted as a passing gate. Final acceptance must come from the fresh
public-clone full gates recorded in the delivery packet below this run's
`.temp/hybrid-c-r14-261102/delivery/`, not these preliminary local results.

### Fresh public-clone acceptance and final source binding

A new HTTPS clone of GitHub `main` at
`3a2ff4fe32415887ed2c71e2022b259a8d6ad676`, without alternates,
HTTP alternates, promisor packs or inherited git-object configuration, accepted
the full binary patch. The three incident refs and six further snapshot commits
were absent (real `git cat-file -e <ref>^{commit}` exits128); only `c04a99d` was
already publicly present. Both missing-ref and present-ref observations are
retained. The initial probe harness wrongly expected exit1 for missing commits,
then wrongly assumed `c04a99d` absent; both harness failures are recorded and
corrected, not promoted to passing evidence.

| Gate run directly in the public clone plus patch | Real exit | Result |
| --- | --- | --- |
| Full engine suite | 0 | 342 tests / 500.725 seconds; original 335 plus 7 fixture controls, no skips |
| Kit suite | 0 | 24 tests |
| Both checkers and both self-tests | 0 each | Range and offload checks, including all 156 range sites |
| Both publication guard entry points | 0 each | Exact current bytes/sites and recomputed claims |
| Release script fixtures | 0 | 46 general + 12 independent signer fixtures |
| Fixture store | 0 | 13 snapshots, 821 exact objects |
| `make manifest`, checksum readback, unchanged-content check | 0 each | Manifest reproducible in the fresh checkout |
| `make pdf` with compiler `--only-cached`, PDF checksum readback | 0 each | Honest `0.1.0-rc.1-dirty` draft from public HEAD plus patch; not an rc.2 asset |
| Real `.scripts/release-check.sh v0.1.0-rc.2` | 1 | Expected missing real owner-signed tag; publication gate remains pending |

Gate traces contain no lookup of any original snapshot commit. The final source
adds this acceptance record and refreshes the repository manifest; all other
2,031 tested files remain byte-identical. Neither changed file is an engine,
kit, checker, fixture or release-script input. The final delivery proof applies
the final patch to a second independent GitHub clone, compares its complete tree
to the signed release source, and repeats the manifest/readback checks. The
packet binds every full-suite input by SHA256 and retains every command's real
exit, PID, observation time and free-disk sample. Both fresh clones are deleted
after proof; source evidence remains under
`.temp/hybrid-c-r14-261102/delivery/`.

This supersedes the prior history-dependent local acceptance evidence. It is a
source correction ready for incident-lane review and owner patch recommit, not
approval of the real release tag, hosted landing or pending measurements.
