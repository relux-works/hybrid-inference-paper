# Paper v5a gap and pending map

## v5a: owner thesis, structure and accepted measurements

Run hybrid-c-r21b-261103 resumes the unchanged hybrid-c-r21-paper-v5a brief after the initial disk stop.
Base: accepted paper-v4 `4ee9a9a52a39b29d084a5c384d5f6445ec33adfd` (Muse r5u ACCEPT).
Branch paper-v5. Title, four Cyrillic authors and release version remain unchanged.
No cut for length; condensation PR9 stays shelved. RC4 takes data through2026-11-05 12:00UTC;
later measurements keep pending markers, with no release-date move.

### Data custody and admitted scope

- Complete current FACTS is archived in data/measurements/paper-v5a-2026-11-03/;
  its section5 RULER update is15:40Z. Hash inventory and raw producer analyses are in that directory.
- Checkpoint10 recheck is measured, heterogeneous exit5, not calibrated acceptance:
  depth109591, top1 64/64, KL7.7296e-5, p95 1.7031e-4, maximum0.2097. Local identities and CUDA-node findings
  are all retained; unpersisted free-running sequences cannot independently prove that reported field.
- Qwen32k scores97.44/97.44/97.18%, changes33/29 of390; Glimmer8k scores87.91/89.13/89.08%, changes130/125.
  Full task details, Wilson intervals, McNemar and text-excess intervals remain descriptive.
  Exact pre-registration7556f461 sets paired score difference, ±2pp, Newcombe10 / paired bootstrap,
  Holm across depths; Qwen8k/32k preceded registration. Primary implementation is pending.
- RTX5090 and3090 client tables retain every FACTS rate and parallel anchor. Capacity262144/99328;
  3090 Qwen ladder ends86k. Both normal priority;5090 is client only. No licence rationale is introduced.
- YaRN beyond262144 uses model-card static factor4/original262144; API extension settings are unknown.
- R16/R17 engines, exports, embedded snapshots, historical fixtures and bench source remain byte-identical.
  R20 at exact b6ac5abcdf60b72582be87c7ad075ee460e7cc78 was read through local Git only, never merged.
  Deferred-source metadata binds six export hashes/headers; no unaccepted R20 number is printed as a result.
  Future selectors explicitly exclude5090 server rows per owner direction.

### Thesis and calculations

The abstract, first introduction paragraph and conclusion start with shared server prefill and client decode.
Each session reads its own KV/recurrent state per token; batching shares weights. Decode-gain numbers remain pending.
B300 finite-delta comparison23151/1663=13.92. Deep anchors14667/1284=11.42 and8673/915=9.48.
Shown reciprocal-rate interpolation gives10.82/10.34/10.13 at131k/164k/181k.
These are mixed-engine/weight-format calculations, not new measurements. About10x is limited to this calculated scale.

The applicability table uses exact accepted R17 link thresholds with strict-above/equality/local rules.
SWA rates remain PRI4 interim; Qwen import-law portability is a named estimate, without SWA import calibration.
GPU/Mac bf16 quality and speed remain pending. Cost columns are deferred.
The prior appendix's delta-only SWA formula is corrected to min(L+d,W), consistent with the accepted full live-window
geometry already used by R17/native CSVs. No engine payload changes.

Chutes snapshot2026-10-29 is same id/family, FP8 weights; hybrid client Q4_K_M/server vLLM FP8.
No API quality comparison is claimed. Context, declared caching, measured cache hits and availability>=95% where
recorded bound admission; missing availability is disclosed. Owner98.1% is a commercial aggregate, not provider data.
Effective input(1-h)*0.039+h*0.0039 gives0.039 without reuse and0.0045669 at h=.981; measured-provider point pending.

### Preservation and wording migrations

The complete former economics body, tables and figures now lives in91-calculation-history.tex as a labelled
historical Q4/API scenario. Old conclusion amounts, abstract ratios and economic summary are preserved there too.
Current main economics and audience paragraphs do not claim those superseded applicability bounds.
Every old range/table comparison remains checked at its moved site. No numeric or direction assertion is removed.
Normal-priority M3 decode headroom is restored with shown arithmetic:14.99*(18.9739+.5571+.1569)/400=.738,
about73.8% of the estimated bandwidth roof. The labelled historical four-stream37% is retained.

All typeset link-technology names are replaced by parameters, including the nominal10Gbit/s prior-art link.
First call16.0MB/s,110ms; growing session9.75MB/s,140.6ms; all-local preflight5.19MB/s,125.8ms.
The later check records0.798MB/s,71.2ms and2.805MB/s,50.6ms, full RTT ranges and the49.0MB/s node control.
Protocol difference and unknown cause are retained; no performance is inferred from a technology name.

Guard migrations: offload_bound's old link strings/markers, current checkpoint/RULER status sites, moved economics
sites and new semantic registry; check_ranges' moved file sites/ALLOW collisions and corrected direction label;
publication_v2 exact TeX/numeric/history pins. Native test names are retained, with explicit renamed-direction and
moved-site adapters; no historical fixture or export is rewritten. New R20 annotation and pending inventories reject
missing comments, promoted numbers, absent waits and unregistered additions independently of byte pins.

### Six r5u notes

| Note | Resolution and control |
|---|---|
|checker-direction-label-stale|Rename to takes less than a day; predicate remains max(refill)<24. Named day/day+1 negative controls in test_r5u_refill_direction_rejects_day_or_more.|
|limitations-ttft-label-bytepin-only|Named v5a limitations residual semantics site; production-TTFT relabelling fails before publication refresh. Regression test test_r5u_limitations_residual_label_has_semantic_rejection.|
|bare-eto-inherited|Historical monthly cost says Эта месячная цена, with its named semantic site.|
|abstract-measured-modelled-split-dropped|Explicit measured/modelled split and throughput-limit mechanism restored in abstract, bound by v5a abstract measured modelled.|
|decode-headroom-percent-dropped|Shown PRI31 arithmetic gives73.8% of the stated estimated roof, without a measured-memory-bandwidth claim.|
|producer-gate-reuse|All required gates will run freshly at the one signed delivered source head. No old receipts reused; no evidence-only follow-up changes the tested head. Actual per-command exits and source hashes live in delivery.json.|

### Negative controls and finite limits

| Plant | Narrows the gate to | Named failing/rejection control | Bound |
|---|---|---|---|
|Production TTFT in limitations|Instrumentation upper bound|test_r5u_limitations_residual_label_has_semantic_rejection|No timing-only production measurement|
|Refill24/25hours|Name and <24 predicate agree|test_r5u_refill_direction_rejects_day_or_more|This R16 refill sensitivity only|
|Delete R20 comment or insert number|Deferred-export custody|test_r20_annotations_and_numbers_cannot_be_silently_promoted|No accepted R20 price claim|
|5090 server claim|Consumer client-only scope|test_consumer_rows_and_client_only_boundary_follow_facts|No licence or server-capacity claim|
|Calibrated exit5 or provider98.1%|Fidelity/cache measurement boundaries|test_fidelity_measured_but_uncalibrated_with_unpersisted_sequence_limit; test_cache_cost_and_admission_are_bounded_scenarios|No GPU/Mac bf16 or provider cache qualification|
|Remove new semantic site|Every registered new row/qualification|test_every_new_semantic_site_has_an_applied_omission_control|Finite named sites; no universal coverage claim|

All controls retain nearby positive cases. Both checker self-tests require each plant to apply and report the
intended named verdict; unapplied plants/setup failures are not negative evidence. No surface table supplied
(brief gap), no requested clause is out of contract. Independent acceptance remains orchestrator-owned.

### Required gates and evidence

Fresh standalone commands: full calc/tests engine suite; full bench/tests kit suite; both paper checkers and each
self-test; publication_v2, r13_ledger, publication_spacing, release and signature fixtures; cache-only make pdf;
make manifest then checksum verification. Every exact command/PID/exit/head/environment/disk sample is recorded
under .temp/hybrid-c-r21b-261103. Gate exits are not claimed before their final receipts exist.
Disk TMPDIR/PYTHONDONTWRITEBYTECODE=1; CPU only, no downloads/native builds/push/tag.
Every gate starts with df -B1. Below28.2GB, wait up to20minutes with2minute checks; no foreign cleanup.
The initial r21 stopped at27.82GB. Resume preflight29.09GB. Brief dips from concurrent lanes are not hidden.

Development diagnostics retained: first offload/range migration checks exited1 for changed wording/unmoved ALLOW;
corrected checks exit0. Compatibility diagnostics caught exact old site/direction references and stale publication
pins; adapters preserve the original assertions at moved sites. The final full suite is the completion gate.

Baseline accepted v4c:33pages,17264 corrected main-text words. The same counter excludes appendices/table bodies,
includes headings/captions/prose. Main-text count decreases when old economics moves to the appendix; this is a
relocation, with every calculation/figure retained, not condensation or a removed point. Final pages/words and
plain/conservative abstract lengths are bound to the delivered head in .temp/hybrid-c-r21b-261103/delivery.json.
Requested owner PDF: .temp/hybrid-c-r21-261103/hybrid-inference-v5a-draft.ru.pdf.

### Every pending and R20 site

Snapshot-derived waits plus the owner's explicit new R20/analysis/OpenRouter/tonight measurement requirements
are enumerated below. Qwen32k and checkpoint10 are measured and no longer pending; heterogeneous tolerance remains pending.
Input-state estimates do not poll jobs or change the fixed data cut-off.

38 pending macro sites; 26 carry an adjacent R20 export annotation.

| File:line | Wait |
|---|---|
|paper/sections/00-abstract.tex:6|размеры|
|paper/sections/00-abstract.tex:7|вызовов в день|
|paper/sections/00-abstract.tex:8|соотношение цен|
|paper/sections/00-abstract.tex:9|соотношение цен|
|paper/sections/00-abstract.tex:10|соотношение цен|
|paper/sections/01-introduction.tex:8|расчёт ожидается|
|paper/sections/01-introduction.tex:9|ожидаются|
|paper/sections/01-introduction.tex:11|размеры|
|paper/sections/01-introduction.tex:12|вызовов в день|
|paper/sections/01-introduction.tex:13|соотношение цен|
|paper/sections/01-introduction.tex:14|соотношение цен|
|paper/sections/01-introduction.tex:15|соотношение цен|
|paper/sections/04-channel.tex:128|замеры времени без снимков и хэширования свидетельств, с отдельными интервалами этапов на Mac и узле.|
|paper/sections/04-channel.tex:334|влияние передачи bf16 на качество и скорость на GPU и Mac.|
|paper/sections/05b-models.tex:181|нормальный приоритет Mac для Glimmer выполняется; Gemma ожидает свободного Mac.|
|paper/sections/06-server.tex:13|ожидается|
|paper/sections/07-economics.tex:4|размеры|
|paper/sections/07-economics.tex:5|вызовов в день|
|paper/sections/07-economics.tex:6|соотношение цен|
|paper/sections/07-economics.tex:7|соотношение цен|
|paper/sections/07-economics.tex:8|соотношение цен|
|paper/sections/07-economics.tex:10|пересчитываются|
|paper/sections/07-economics.tex:20|измеренная доля попаданий OpenRouter и окончательный допуск поставщиков.|
|paper/sections/07-economics.tex:34|доля|
|paper/sections/07-economics.tex:34|цена|
|paper/sections/07-economics.tex:45|ожидается|
|paper/sections/07-economics.tex:75|ожидаются|
|paper/sections/07-economics.tex:79|ожидается|
|paper/sections/11-limitations.tex:115|первичный парный анализ оценок по зарегистрированному критерию.|
|paper/sections/11-limitations.tex:117|ожидаются до среза данных 2026-11-05 12:00 UTC.|
|paper/sections/14-conclusion.tex:24|размеры|
|paper/sections/14-conclusion.tex:25|вызовов в день|
|paper/sections/14-conclusion.tex:26|соотношение цен|
|paper/sections/14-conclusion.tex:27|соотношение цен|
|paper/sections/14-conclusion.tex:28|соотношение цен|
|paper/sections/90-appendix.tex:145|калибровка гетерогенного допуска CUDA и Metal на M3 Max, включая сравнение с эталоном BF16.|
|paper/sections/90-appendix.tex:147|RULER Qwen на 64 и 128 тысячах, варианты bf16 на 8 и 32 тысячах; Glimmer на 32, 64 и 122\,880 токенах. Первичный парный анализ по зарегистрированному критерию реализуется. Состояние на 2026-11-03 15:40 UTC: bf16 на 8 и 32 тысячах начат в 14:24, затем идёт глубина 64 тысячи; Qwen на 128 тысячах начат в 14:29, оценка 32--36 часов, до 2026-11-05 00:00--02:00 UTC. Программа Glimmer на четырёх глубинах оценена в 33--50 часов. Данные принимаются до 2026-11-05 12:00 UTC; неизмеренные пункты остаются помеченными, срок выпуска сохраняется.|
|paper/sections/90-appendix.tex:153|полная параллельная кривая M3 при PRI~31 и нормальный приоритет Gemma требуют свободного Mac; Glimmer при PRI~31 выполняется, затем обновление движка 16b. Измерения пакетной генерации vLLM на PRO 6000 и B300, Mac на миллионе, качества на глубине и проверка кэша OpenRouter выполняются по отдельной программе. Мост vLLM на GPU после переработки; лестница Bonsai 2 2B/4B/9B позднее.|

| R20 file:line | Exact future export and selector |
|---|---|
|paper/sections/00-abstract.tex:6|calc/out/run20/team_break_even.csv; PRO6000 only; owned/new64/128; load/share; sustained finite scan|
|paper/sections/00-abstract.tex:7|calc/out/run20/small_team_cost.csv; PRO6000 only; profile/share/client/basis; requested_day|
|paper/sections/00-abstract.tex:8|calc/out/run20/small_team_cost.csv; PRO6000 only; median_over_hybrid|
|paper/sections/00-abstract.tex:9|calc/out/run20/small_team_cost.csv; PRO6000 only; cheapest_over_hybrid; measured cache admission pending|
|paper/sections/00-abstract.tex:10|calc/out/run20/small_team_cost.csv; PRO6000 only; own_cluster_person_month/person_month|
|paper/sections/01-introduction.tex:8|calc/out/run20/decode_scaling.csv; PRO6000/B300; modelled depth/batch gain, not measured|
|paper/sections/01-introduction.tex:11|calc/out/run20/team_break_even.csv; PRO6000 only; owned/new64/128; load/share; sustained finite scan|
|paper/sections/01-introduction.tex:12|calc/out/run20/small_team_cost.csv; PRO6000 only; profile/share/client/basis; requested_day|
|paper/sections/01-introduction.tex:13|calc/out/run20/small_team_cost.csv; PRO6000 only; median_over_hybrid|
|paper/sections/01-introduction.tex:14|calc/out/run20/small_team_cost.csv; PRO6000 only; cheapest_over_hybrid; measured cache admission pending|
|paper/sections/01-introduction.tex:15|calc/out/run20/small_team_cost.csv; PRO6000 only; own_cluster_person_month/person_month|
|paper/sections/06-server.tex:13|calc/out/run20/decode_scaling.csv; PRO6000/B300; modelled gain; measured batching pending|
|paper/sections/07-economics.tex:4|calc/out/run20/team_break_even.csv; PRO6000 only; owned/new64/128; load/share; sustained finite scan|
|paper/sections/07-economics.tex:5|calc/out/run20/small_team_cost.csv; PRO6000 only; profile/share/client/basis; requested_day|
|paper/sections/07-economics.tex:6|calc/out/run20/small_team_cost.csv; PRO6000 only; median_over_hybrid|
|paper/sections/07-economics.tex:7|calc/out/run20/small_team_cost.csv; PRO6000 only; cheapest_over_hybrid; measured cache admission pending|
|paper/sections/07-economics.tex:8|calc/out/run20/small_team_cost.csv; PRO6000 only; own_cluster_person_month/person_month|
|paper/sections/07-economics.tex:10|calc/out/run20/paper_claims.csv; light/medium/heavy; unconditional_claim; no5090-server rows|
|paper/sections/07-economics.tex:45|calc/out/run20/small_team_cost.csv; server/profile/share/client/basis; cost columns after accepted merge|
|paper/sections/07-economics.tex:75|calc/out/run20/team_break_even.csv; PRO6000 only; each profile; reference=own_cluster; sustained finite scan|
|paper/sections/07-economics.tex:79|calc/out/run20/paper_claims.csv; PRO6000 only; compare own_cluster/API; full-workload alarm retained|
|paper/sections/14-conclusion.tex:24|calc/out/run20/team_break_even.csv; PRO6000 only; owned/new64/128; load/share; sustained finite scan|
|paper/sections/14-conclusion.tex:25|calc/out/run20/small_team_cost.csv; PRO6000 only; profile/share/client/basis; requested_day|
|paper/sections/14-conclusion.tex:26|calc/out/run20/small_team_cost.csv; PRO6000 only; median_over_hybrid|
|paper/sections/14-conclusion.tex:27|calc/out/run20/small_team_cost.csv; PRO6000 only; cheapest_over_hybrid; measured cache admission pending|
|paper/sections/14-conclusion.tex:28|calc/out/run20/small_team_cost.csv; PRO6000 only; own_cluster_person_month/person_month|

Pending labels are generic (Ожидается) because waits include model results and analysis. The abstract counter expands that visible label and ignores source comments. Initial compatibility diagnostics1 retained; explicit moved-site/direction adapters and refreshed pins pass focused controls. Spacing diagnostic1 on RC4 was corrected in prose, without changing the guard. Final same-head gates remain required.

### Full-suite migration correction

The first full suite at a11635f ran455tests in559.55s, exit1, with one StopIteration in
Run13Tests.test_paper_ledger_omission_controls. Its exact5.6-dollar omission selector still named07-economics;
the calculation had moved unchanged to91-calculation-history. The one-path adapter follows that same scalar
at its new registered site; original missing-site assertions and reviewer test name remain unchanged.
Focused diagnostic exit1 is retained. All final gates, including the entire engine/kit suites and cached PDF,
are rerun at the corrected signed head; no first-head receipt is reused as final evidence.


## V5a second pass: r21c, r5y rework and accepted measurements

Continues signed `ee4401ce28003e70ae388d38d64dd02275786a32` on `paper-v5`; no engine20/21 merge.
All26 R20 bodies/export selectors are unchanged. The first model-capacity interruption left12 tracked edits and a new evidence directory. Every edit was inspected against the base: valid manuscript/registry/test changes were retained; stale related-work/current README status, nested pending reference and current RULER-bound wording were corrected deliberately. No foreign edit was discarded.

### Review disposition

| Finding/note | Correction and bound |
|---|---|
| link-tech-names-in-unreleased-changelog | Four current bullets now use16.0MB/s110ms or9.75MB/s140.6ms. Existing v5a guard includes Unreleased; released notes, exports and historical fixtures remain exact. |
| million-section-basis-fence-reach | Entire GLM/Studio economics fenced at entry; figure caption and conclusion each independently identify run14, llama.cppQ4 and previousAPI tariffs. All old amounts/calculations retained, no current-vLLM assertion. |
| glimmer-outside-preregistration-unstated | Not named in registration;13:59–15:35UTC straddles14:36UTC, not confirmatory; same rules applied by extension. Qwen collection05:52–07:32/07:32–14:21 precedes registration. |
| intro-llama-9-10s-inherited | Replaced9–10s with8.44s at131k and9.50s at181k. Reciprocal-rate interpolation and weights0.38/0.62 shown in91-calculation-history. |
| checker-files-duplicate-dead-constant | FILES contains each path once and restores14-conclusion. Range/direction coverage and predicates retained. C08 follows the explicitly archival conclusion marker. |
| link-tech-names-internal-residue | Live site IDs renamed to16.0MB/s prediction,9.75MB/s preflight and5.19MB/s all-local; live regression selector migrated. Frozen growing_5g_validation.csv, offload_at_5g_9_75_mb_s fields, old fixtures and released prose retain their identifiers for byte custody. No current typeset or Unreleased label uses technology. |

### Accepted measurements and superseded sites

- Primary RULER: exact e46e5623 report/JSON copied to data/measurements/paper-v5a2-2026-11-03. Qwen32k score intervals0.0000[-1.0519,+1.0519] and-0.2564[-1.4704,+0.8517]pp meet±2pp. Qwen8k point bootstrap explicitly cannot certify; two post-review sidecars[-0.9414,+0.9414] and[-1.0387,+1.0387] support the score claim. The binarised sidecar has its own fully-correct-rate estimand. Glimmer8k+1.2179[-0.1410,+2.6923] and+1.1667[-0.1923,+2.6410]pp do not meet the margin. Pendingp=1 Holm results are upper bounds within each model/pair; observed equivalence cannot reverse with later depths. Text equivalence remains unestablished at all three measured depths. The old generic primary-analysis pending is removed.
- BF16 recurrent transport: accepted20-document/40960-position CUDA KL study only. f32-local exact0; bf16-local KL-0.000298[-0.001076,+0.000390]nats, top1+0.066[-0.100,+0.249]pp. Source report/provenance/receipts archived; GPU failure and same-identity resume stated. Does not close bf16RULER, GPU rehearsal, Mac or speed qualification. Lossy controls remain.
- Glimmer PRI31: four measured depths and all12delta-prefill/decode cells, four saves/restores. M3 Glimmer2000-token cells old→new:16k174.7/10.48→173.5/16.3;50k105.8/9.29→107.3/10.34;100k69.6/7.61→71.2/9.04;118k54.0/7.21→67.4/8.82. Source FACTS2 PRI31 block. Successive deltas+128generated tokens and external LaCie saves constrain interpretation. Strict archive not yet copied to agents1, so literal FACTS is the local raw-cell authority. Engine thresholds retain frozen PRI4/Qwen-import-estimate labels until accepted engine pass.
- Qwen server rebuild: FACTS3 GPU-fill block, PRO6000 Server Edition,518.29+1295.48=1813.77s=30.2min empty→1040000;524288/515712 newtokens,18.4/36.4GB savedslots. Restores/probes are same-GPU controls; Mac download/import/logit/decode remains pending. No end-to-end Mac resync time is inferred.

New input snapshot includes full FACTS and r5y verdict, exact accepted RULER report/JSON, BF16 producer report/provenance, literal PRI31 cells and source-reviewed semantic sites; README hashes every archived file. Original engine inputs/exports, bench, history-fixtures and previous v5a evidence remain byte-identical. All prior test method names remain. Title, Cyrillic authors and release version are unchanged; no cuts for length.

### Narrowing controls

| Mutant | Gate narrowed to | Named failing test |
|---|---|---|
| Plant each technology name in Unreleased | Current release prose, with released-history positive control | test_r5y_unreleased_link_technology_regression |
| Remove each new semantic phrase | Its exact named publication site (15sites) | test_every_r5y_data_site_has_named_omission_control |
| Remove entry/caption/conclusion historical label separately | Each reachable1M economics surface | test_r5y_million_basis_reaches_caption_and_conclusion |
| Change primary/sidecar numbers or equivalence basis | Accepted primary JSON plus source-bound semantic contract | test_ruler_primary_cells_and_sidecar_basis_follow_accepted_json; test_every_r5y_data_site_has_named_omission_control |
| Promote Glimmer registration/timing | Witnessed accepted model/timing scope | test_r5y_glimmer_registration_scope_and_timing; named omission control |
| Remove bf16 KL scope or future waits | Document-paired CUDA result only, independent CPU-lossy qualification | test_bf16_kl_accepted_rows_and_remaining_scope; named omission control |
| Substitute old PRI4 Glimmer cells or remove engine-interim label | Raw PRI31 measurement distinct from frozen threshold inputs | test_glimmer_pri31_cells_and_interim_engine_boundary; named omission control |

No surviving planted omission is claimed as coverage. Bounds: finite authored sites and accepted small JSON/FACTS recomputations; no GPU/Mac execution, statistical-method requalification or transport validation here. The brief supplies no surface table (declared brief gap); no requested row treated as out of contract. Independent acceptance remains orchestrator-owned.

### Counts, gates and custody

Comparable baseline37pages/15968main-text lexical words; diagnostic current39pages/16844words; abstract1725plain characters including rendered pending labels, below1920. Same lexical counter excludes appendices/table/math bodies. Final exact-head counts and SHA256 are written to .temp/hybrid-c-r21c-261103/delivery.json after the fresh build; no evidence-only commit after final gates.

All gates must run freshly at the delivered signed head: engine/kit, checkers+self-tests, publication/ledger/spacing, release/signature fixtures, cache-onlyPDF, manifest/check, git signature/whitespace. Per-command argv/PID/head/environment/disk/exit logs live under .temp/hybrid-c-r21c-261103; final-gates.json is created only after every required exit0. Disk guard28.2GB waits20min/rechecks2min, never deletes foreign scratch. CPU only; no downloads/native builds/push/tag.

Diagnostics: initial offload/range checks exit1 on the moved deeper-RULER paragraph and archival conclusion marker, respectively; both were retargeted without changing the bound or predicate. Focused21tests exit0, checkers self-tests and cached PDF exit0. All actual later exits, including failures, remain in task receipts.

### Current pending inventory

39 macro sites, including26 unchanged R20 sites. `calc/tests/data/paper-v5a2-pending.json` enumerates every body and exact wait authority. Deep RULER/bf16 timing remains the FACTS5 snapshot updated15:40UTC; accepted newer blocks remove only completed waits. Fixed data cut-off2026-11-05 12:00UTC stays.

| Site | Wait |
|---|---|
|paper/sections/00-abstract.tex:6|размеры|
|paper/sections/00-abstract.tex:7|вызовов в день|
|paper/sections/00-abstract.tex:8|соотношение цен|
|paper/sections/00-abstract.tex:9|соотношение цен|
|paper/sections/00-abstract.tex:10|соотношение цен|
|paper/sections/01-introduction.tex:8|расчёт ожидается|
|paper/sections/01-introduction.tex:9|ожидаются|
|paper/sections/01-introduction.tex:11|размеры|
|paper/sections/01-introduction.tex:12|вызовов в день|
|paper/sections/01-introduction.tex:13|соотношение цен|
|paper/sections/01-introduction.tex:14|соотношение цен|
|paper/sections/01-introduction.tex:15|соотношение цен|
|paper/sections/04-channel.tex:128|замеры времени без снимков и хэширования свидетельств, с отдельными интервалами этапов на Mac и узле.|
|paper/sections/04-channel.tex:335|RULER для bf16, репетиция GPU и запуск Mac для качества и скорости передачи bf16.|
|paper/sections/05b-models.tex:208|Gemma при нормальном приоритете ожидает свободного Mac.|
|paper/sections/06-server.tex:13|ожидается|
|paper/sections/07-economics.tex:4|размеры|
|paper/sections/07-economics.tex:5|вызовов в день|
|paper/sections/07-economics.tex:6|соотношение цен|
|paper/sections/07-economics.tex:7|соотношение цен|
|paper/sections/07-economics.tex:8|соотношение цен|
|paper/sections/07-economics.tex:10|пересчитываются|
|paper/sections/07-economics.tex:20|измеренная доля попаданий OpenRouter и окончательный допуск поставщиков.|
|paper/sections/07-economics.tex:34|доля|
|paper/sections/07-economics.tex:34|цена|
|paper/sections/07-economics.tex:45|ожидается|
|paper/sections/07-economics.tex:75|ожидаются|
|paper/sections/07-economics.tex:79|ожидается|
|paper/sections/08-million.tex:45|загрузка, импорт, проверка логитов и генерация Mac на 524\,288 и 1\,040\,000 токенов.|
|paper/sections/11-limitations.tex:72|RULER для bf16, репетиция GPU и запуск Mac для качества и скорости передачи bf16.|
|paper/sections/11-limitations.tex:169|ожидаются до среза данных 2026-11-05 12:00 UTC.|
|paper/sections/14-conclusion.tex:24|размеры|
|paper/sections/14-conclusion.tex:25|вызовов в день|
|paper/sections/14-conclusion.tex:26|соотношение цен|
|paper/sections/14-conclusion.tex:27|соотношение цен|
|paper/sections/14-conclusion.tex:28|соотношение цен|
|paper/sections/90-appendix.tex:145|калибровка гетерогенного допуска CUDA и Metal на M3 Max, включая сравнение с эталоном BF16.|
|paper/sections/90-appendix.tex:148|RULER Qwen на 64 и 128 тысячах, варианты bf16 на 8 и 32 тысячах; Glimmer на 32, 64 и 122\,880 токенах. Для новых глубин анализ ожидает данных. Состояние на 2026-11-03 15:40 UTC: bf16 на 8 и 32 тысячах начат в 14:24, затем идёт глубина 64 тысячи; Qwen на 128 тысячах начат в 14:29, оценка 32--36 часов, до 2026-11-05 00:00--02:00 UTC. Программа Glimmer на четырёх глубинах оценена в 33--50 часов. Данные принимаются до 2026-11-05 12:00 UTC; неизмеренные пункты остаются помеченными, срок выпуска сохраняется.|
|paper/sections/90-appendix.tex:153|полная параллельная кривая M3 при PRI~31 и нормальный приоритет Gemma требуют свободного Mac; Glimmer при PRI~31 измерен; обновление опор движка и многопоточный прогон 16b ожидаются. Измерения пакетной генерации vLLM на PRO 6000 и B300, Mac на миллионе, качества на глубине и проверка кэша OpenRouter выполняются по отдельной программе. Мост vLLM на GPU после переработки; лестница Bonsai 2 2B/4B/9B позднее.|

Compatibility rework: the152-test paper-only diagnostic exited1 on two inherited score/text negative selectors. Explicit text-only non-equivalence wording preserves both original controls at their original names; score equivalence has its separate current evidence. No historical fixture or prior test name was removed. Threshold captions now distinguish completed GlimmerPRI31 measurement awaiting engine ingestion from GemmaPRI31 still queued; the frozen PRI4/Qwen-import estimates and all thresholds remain exact. README spacing diagnostic1 was fixed in prose; corrected guard0. All final receipts will be fresh at the signed source.


## V5a third pass: r21d, analyst corrections independent of engine22

Base accepted605ba51ab22aefebd94f5e9ddf1bbb12735f3075, paper-v5. All26 legacy R20 bodies/export selectors stay pending, awaiting accepted engine22; no new engine output read as an accepted result or merged. No cuts for length.

### Scientific and measurement changes

| Scope | Previous statement / basis | Current statement and source |
|---|---|---|
| Abstract prefill | Shallow16k, delta10000, about14x | Profile-depth131k/164k/181k ratios10.82/10.34/10.13, rounded range10.1–10.8. Existing reciprocal-rate arithmetic in06-server and archived pref ill-ratios.json; shallow23151/1663=13.92 remains in body. FP8/Q4 and marginal/finite-portion limits remain. |
| Exactness headline | Broad same-partition CUDA statement | f32 KL study paired KL/top1 exactly0 in all20documents; functional CUDA bit identity remains only with its measured depth/partition qualifications in methods. RULER answer identity never follows from scores. |
| RULER paths | Short batch-only description | Read exact18d3f114 RULER-RUNBOOK. Node prefills with own batching, imports into client and samples locally. Local batch/ubatch64, partition256. Different prefill paths, without an inferred narrower mechanism. |
| Scores versus text | Measured scores and separate answer counts | Offload/local scores identical390/390 at each8k/32k; text34/33changes against partition32/29, nonsignificant paired comparisons retained. Score sidecars/intervals preserved; no bit-equal RULER answer claim. |
| Registration | Before/straddling timing labels | Margin±2pp fixed2026-11-03 14:36UTC after known Qwen8k/32k. Strictly preregistered Qwen64k/128k. Glimmer unnamed and exploratory; extended analysis unchanged. |
| Glimmer | Not equivalent | Equivalence not established within±2pp; local differs from offload+1.22pp and partition+1.17pp. Measured model/engine property; no assignment of extra causality or clearance to offload. Full intervals unchanged. |
| Bandwidth thesis | Shared prefill / individual decode | Added client bandwidth/KV condition to abstract, thesis paragraph and conclusion. Actual M5 ratios source FACTS2; only two observed model/engine configurations, no claim that KV alone explains model differences. Server vLLM batching remains modelled pending measurement. |
| Abstract procedure | PRI31, synchronous snapshots/hashing | Laboratory conditions removed from abstract and retained explicitly in methods/limitations. Actual code5 calibration limit, arithmetic residual/instrumentation boundary and PRI31 decode remain bound. Economic sentences pending unchanged. |
| Heavy-load general claim | Withdrawn without stated implementation cause | CHANGELOG names own-cluster recalculation on vLLM as the cause. No replacement economic amount invented. |
| Excluded cache probe | Not used | No result or description introduced; full current-prose negative control plus valid price/pending controls. New FACTS snapshot is restricted to the named M5 block. Existing immutable evidence is untouched. |

### M5 accepted data and unchanged engine inputs

Full FACTS2 block Apple M5 Max64GB at recorded normal priority archived verbatim in data/measurements/paper-v5a3-2026-11-03/FACTS-M5.md. Qwen/Glimmer readiness records show PRI31/nice0 for process and ancestry in all36/31samples, normal_priority true, no override. Current measured1.6.7 rows replace owner-reported-priority1.6.6 rows; current caveat lifted. All10ladder rows and parallel/260k/129k/agent-session points, slot-save sizes/times and missing-series limits are present.

| Qwen parallel depth | Old1.6.6 aggregate by streams | New1.6.7 aggregate by streams |
|---|---|---|
|32k,1/2/4/8/12/16|22.62/31.89/47.78/62.32/62.78/65.54|23.108/32.834/46.870/60.964/57.089/62.727|
|64k,1/2/4/8|19.88/26.00/32.55/40.23|20.163/26.257/33.090/40.816|
|128k,1/2/4|15.73/18.35/20.69|16.186/18.825/20.778|

Source arithmetic explicitly shows100(57.089/62.78−1)=−9.1% at12streams and100(62.727/65.54−1)=−4.3% at16streams,32k. Other points−2.2…+3.0% as FACTS. Separate np4 control24.351 does not replace20.778.
Qwen footprint34.6–43.6KiB/token and maximum aggregate/single gains2.71/2.02/1.28 at32k/64k/128k; Glimmer7.3–9.6KiB/token and3.24/2.66/2.36 at32k/64k/129k. Gains are recomputed from each series' own single-stream rate, not pooled across steps.

No unreviewed engine rescaling: retained run16 daily capacity and economic results explicitly keep their historical input basis, including old M5 priority uncertainty. The current M5 measurement table has recorded priority. Old1.4.1 ladder prose, all1.6.6 M5 sweep rows and former conclusion capacity paragraph are retained in91-calculation-history with the original qualifiers; old guard sites follow them. This boundary prevents new measurements from silently laundering old model outputs as recalculated values.

### Negative controls and limits

| Mutant | Scope narrowed | Named failing test |
|---|---|---|
| Omit any of28new authored sites | Own named publication contract | test_each_analyst_site_rejects_named_omission |
| Promote RULER answer equality | Score/answer distinction | test_ruler_paths_and_score_identity_do_not_imply_bit_identity |
| Change margin timing to before known results | Preregistration timeline | test_registration_and_glimmer_exploratory_scope |
| Promote14x into headline or bf16 to lossless | Profile-depth and codec boundaries | test_abstract_profile_gap_lab_details_and_lossy_bf16_boundary |
| Insert excluded three-call probe | Current prose/release text; ordinary API list-price positive | test_excluded_three_call_cache_probe_is_absent |

No survivor claimed as coverage. Positive source/arithmetic tests cover all M5 ladders and gain/regression scalars; full source-bound phrases cover remaining accepted block values. These CPU publication tests do not reproduce hardware or requalify statistics. No surface table supplied (declared brief gap); no acceptance clause out of contract. All prior test names and reviewer tests remain. Independent acceptance belongs to orchestrator/reviewer.

Diagnostics retained: contracts helper1 stopped on a not-yet-authored source inventory, resumed only its unfinished suffix. Focused29tests first1 on preserved wording and an overbroad test token conflating agent tools with instrumentation; corrected29tests0. Offload self-tests1 caught duplicate migrated RULER contracts, then overlapping conclusion novelty/endpoints; individual sites separated without weakening exact named-rejection checks, subsequent self-test0. Range156controls0, cachedPDF0. All final gates must be freshly rerun at the signed delivered head; no earlier receipt reuse and no evidence-only source commit afterwards.

### Counts and gates

Baseline39pages/16844main-text lexical words. Diagnostic current40pages/17476words. Interim abstract1832characters including rendered pending labels, below1920. Main-text counter and current page count in .temp/hybrid-c-r21d-261103/counts-delivery.json after exact-head cached build. Version/title/Cyrillic authors unchanged; all prior measured/modelled content preserved with basis labels.

All required engine/kit/checker+self-test/publication/release/cache-onlyPDF/manifest gates must exit0. Exact argv, signed source head, PID, environment, df-BG plus exact-byte samples and every exit are recorded in .temp/hybrid-c-r21d-261103/*.json and logs. Final-gates.json/delivery.json are produced only after all16required receipts are0at the delivered head. Disk threshold28.5GiB=30601641984bytes, floor28GiB, wait20min/recheck2min; no foreign deletion. CPU only, no downloads/native builds/push/tag.

### Pending map

39macro sites including26 unchanged R20 annotations. Every current body and authority is in calc/tests/data/paper-v5a3-pending.json; later accepted engine22 fills the economics/abstract in a separate pass. No new measurement completion inferred.

| Site | Wait |
|---|---|
|paper/sections/00-abstract.tex:7|размеры|
|paper/sections/00-abstract.tex:8|вызовов в день|
|paper/sections/00-abstract.tex:9|соотношение цен|
|paper/sections/00-abstract.tex:10|соотношение цен|
|paper/sections/00-abstract.tex:11|соотношение цен|
|paper/sections/01-introduction.tex:10|расчёт ожидается|
|paper/sections/01-introduction.tex:11|ожидаются|
|paper/sections/01-introduction.tex:13|размеры|
|paper/sections/01-introduction.tex:14|вызовов в день|
|paper/sections/01-introduction.tex:15|соотношение цен|
|paper/sections/01-introduction.tex:16|соотношение цен|
|paper/sections/01-introduction.tex:17|соотношение цен|
|paper/sections/04-channel.tex:128|замеры времени без снимков и хэширования свидетельств, с отдельными интервалами этапов на Mac и узле.|
|paper/sections/04-channel.tex:335|RULER для bf16, репетиция GPU и запуск Mac для качества и скорости передачи bf16.|
|paper/sections/05b-models.tex:208|Gemma при нормальном приоритете ожидает свободного Mac.|
|paper/sections/06-server.tex:13|ожидается|
|paper/sections/07-economics.tex:4|размеры|
|paper/sections/07-economics.tex:5|вызовов в день|
|paper/sections/07-economics.tex:6|соотношение цен|
|paper/sections/07-economics.tex:7|соотношение цен|
|paper/sections/07-economics.tex:8|соотношение цен|
|paper/sections/07-economics.tex:10|пересчитываются|
|paper/sections/07-economics.tex:20|измеренная доля попаданий OpenRouter и окончательный допуск поставщиков.|
|paper/sections/07-economics.tex:34|доля|
|paper/sections/07-economics.tex:34|цена|
|paper/sections/07-economics.tex:45|ожидается|
|paper/sections/07-economics.tex:75|ожидаются|
|paper/sections/07-economics.tex:79|ожидается|
|paper/sections/08-million.tex:45|загрузка, импорт, проверка логитов и генерация Mac на 524\,288 и 1\,040\,000 токенов.|
|paper/sections/11-limitations.tex:72|RULER для bf16, репетиция GPU и запуск Mac для качества и скорости передачи bf16.|
|paper/sections/11-limitations.tex:176|ожидаются до среза данных 2026-11-05 12:00 UTC.|
|paper/sections/14-conclusion.tex:25|размеры|
|paper/sections/14-conclusion.tex:26|вызовов в день|
|paper/sections/14-conclusion.tex:27|соотношение цен|
|paper/sections/14-conclusion.tex:28|соотношение цен|
|paper/sections/14-conclusion.tex:29|соотношение цен|
|paper/sections/90-appendix.tex:146|калибровка гетерогенного допуска CUDA и Metal на M3 Max, включая сравнение с эталоном BF16.|
|paper/sections/90-appendix.tex:149|RULER Qwen на 64 и 128 тысячах, варианты bf16 на 8 и 32 тысячах; Glimmer на 32, 64 и 122\,880 токенах. Для новых глубин анализ ожидает данных. Состояние на 2026-11-03 15:40 UTC: bf16 на 8 и 32 тысячах начат в 14:24, затем идёт глубина 64 тысячи; Qwen на 128 тысячах начат в 14:29, оценка 32--36 часов, до 2026-11-05 00:00--02:00 UTC. Программа Glimmer на четырёх глубинах оценена в 33--50 часов. Данные принимаются до 2026-11-05 12:00 UTC; неизмеренные пункты остаются помеченными, срок выпуска сохраняется.|
|paper/sections/90-appendix.tex:154|полная параллельная кривая M3 при PRI~31 и нормальный приоритет Gemma требуют свободного Mac; Glimmer при PRI~31 измерен; обновление опор движка и многопоточный прогон 16b ожидаются. Измерения пакетной генерации vLLM на PRO 6000 и B300, Mac на миллионе, качества на глубине и проверка кэша OpenRouter выполняются по отдельной программе. Мост vLLM на GPU после переработки; лестница Bonsai 2 2B/4B/9B позднее.|


## v5a4: owner review, run hybrid-c-r21e-261103

Base b543c026b859850bbd53b2af352b9a3514ff1539 (Muse r5y3 ACCEPT), branch paper-v5.
Title, thesis, Cyrillic authors and version unchanged. No cuts for length.
No engine20/21/22 merge; all26 R20 body/export signatures remain byte-identical.
The brief contains no surface table (declared brief gap); no acceptance clause
is treated as out of contract. All original reviewer test methods remain.

### Owner-item old/new/source map

| Item | Old | New | Source and finite limit |
| --- | --- | --- | --- |
| A1 abstract bf16 | Format incurs loss, potentially read as observed quality loss | Rounds state; no detected KL effect, -0.000298 nats,95%[-0.001076,+0.000390];0.000298/0.054253=0.0055,about1/180 | Accepted20-document40960-position CUDA paired study; no lossless claim |
| A1 bf16 RULER | Pending8k/32k | Equal local scores390/390 each; text28 vs34 f32 at8k,33 vs33 at32k | Full new FACTS bf16-arm block; frozen comparison arms, no general quality clearance |
| A2 1M | Run14 GLM economics and2.6--2.7 API ratio in main text | Entire archived calculation/figure/conclusions in appendix C; main section only settings, measured rebuild, warm restore, download, remaining waits | Run14 exact exports and archive labels retained; current economics engine22 |
| A2 download | Pending | useful17.96/26.66MB/s,39.9min both; total22.92MB/s | FACTS download spans1026.042/1365.377s,54819840624B; includes retries/write/hash, not wire-only rate |
| A3 median | Generic median provider | Median of each price item in2026-10-29 snapshot | Old0.05/0.18/2.30,85% and48% unchanged pending engine22 basis |
| A4 5090 | Implicit client boundary | Cumulative prefill59.7/2.6=23.0; decode65.68/14.99=4.38 through32.42/6.93=4.68 (range4.3--4.7) | Full FACTS5090 and M3 PRI31 ladder;48.64/10.36=4.69 before one-decimal range rounding |
| A4 fit | Tabulated capacity | One Qwen at262144 in32GB; measured2streams128k,1at260k; little benefit for27B<=262k owner-PC | FACTS5090;1M/multisession audience boundary; largeMoE expectation without measurement |
| B5 M4 | Main table19.5/8.38/11.01/1.31 | Row removed to appendix C, declared unmeasured once | Engine gap: estimated8.38 local sessions/day vs measured-anchor M5 estimate6.73 suggests overestimated M4 prefill; engine must revisit |
| B6 restore | Restore3.14s unqualified | Warm;36394654776/3.14/1e9=11.6GB/s; file just written, OS cache not dropped; cold not measured | Full slot-fill FACTS block |
| B7 readability | Code5, PRI31, snapshot/hash journal in conclusion/limits | Checkpoint10 top1 64/64, meanKL7.7296e-5; ordinary priority; methods in appendix A | Full checkpoint10 facts; heterogeneous acceptance still requires calibration |
| B7 notice | Four repeated audience amount paragraphs | One visible applicability pending notice;20 inactive amount hooks plus6 active hooks retain all26 signatures | Owner instruction consolidation; no economic amount filled or export selector changed |
| B8 rounding | Cache display0.0045669 |0.0046 in table; exact shown arithmetic unchanged |0.019*0.039+0.981*0.0039=0.0045669 |
| B8 abstract |1832 Russian characters, no English artifact | Russian<=1670 (>=250room); English<=1650 in paper/abstract.en.txt | Counts use rendered text, excluding inactive hook blocks; receipts contain exact counts |
| B9 duplicate | Same-partition CUDA identity repeated | Duplicate removed, original measured-depth identity retained and guarded | Existing CUDA functional paragraph; exactness scoped to measured controls |
| B9 M5 ratio | PRI31 attached to old M5 anchors | M5kit1.4.1 priority explicitly unrecorded, ordinary-priority label attached only M3 | Preserved95.1/52.5 through586.4/191.5; no reassignment to recorded-run numbers |
| C Glimmer32 | Pending deeper Glimmer |87.26/87.12/87.18%;111/114of390; excess-.77pp[-4.37,+2.86], text not equivalent2pp; stopped32k | Full FACTS exploratory block; no unprovided primary score interval inferred |
| C server batching | All depths unmeasured |16k PRO6000Workstation15.15 at39resident;738.10/48.72 | Full FACTS block; deeper batches modelled until kit1.6.11, B300 pending |

### Guard migrations and negative controls

- check_ranges.py follows all moved million-token run14 amounts/directions into
  appendix C; FILES remains unique and retains both live08 and conclusion14.
  Every original numeric bound/direction remains checked.
- offload_bound.py follows moved claims and completed waits via new current
  semantic views; original frozen exports/evidence/fixtures remain unchanged.
  Distinct claim wording keeps each checker self-test plant attributable.
- publication_v2.py pins the new exact paper bytes and numeric occurrences with
  paper-v5a4-migration.json; no historical fixture waiver or byte rewrite.
- The raw pending inventory retains all40 sites;26 R20 signatures remain exact.
  rendered_tex skips only the explicit inactive hook blocks; budgets/counts
  and one-notice tests verify visible text separately from source custody.
- test_paper_v5a4.py provides applied omission controls for every new named
  measurement/qualification site, plus targeted cold-restore, wire-rate,
  lossless-bf16, deeper-batch, 260k-double-stream and altered-R20 plants.
  Each is rejected by its named contract; the full checker self-test proves
  independent attribution. Existing review-test names are retained with
  superseded assertions updated explicitly to completed measurement scope.

| Mutant | Gate narrows to | Named rejecting test | Surviving bound |
| --- | --- | --- | --- |
| Omit each new owner claim | Finite current source site | test_owner_sites_have_applied_named_omission_controls | None |
| Change deferred R20 amount | Exact body/export custody | test_deferred_economic_sites_keep_raw_custody_and_one_visible_notice | None |
| bf16 lossless; abstract over budget | Rounding observation and publication budget | test_abstract_budgets_rounding_and_empirical_kl_boundary | None |
| Warm becomes cold; useful becomes wire rate | Measurement conditions, not inferred link speed | test_million_archive_custody_and_warm_restore_download_arithmetic | None |
| Two streams at260k | Measured resident-session boundary | test_consumer_boundary_and_m4_estimate_scope | None |
| Glimmer32 text becomes equivalent | Explicit interval and exploratory stop | test_completed_bf16_and_glimmer_scope | None |
| Deeper batches become measured | Accepted16k depth only | test_measured_server_batching_has_finite_depth_boundary | None |

These are publication contracts, not new hardware, statistical-method or
provider-quality tests. Physical cold restore, deeper batching and actual
unmeasured Mac execution remain outside the measurement evidence.

### Current pending scope and delivery receipts

Closed since v5a3: bf16 RULER8k/32k, Glimmer32k (deeper program cancelled),
Mac slot download, shallow PRO6000 decode batching. Current waits:
accepted engine22 economics and deeper server gain; Qwen64k/128k RULER and
primary analysis; Mac512k/1.04M import/logit/decode/delta prefill; GPU rehearsal
and Mac bf16 quality/speed; heterogeneous calibration; full M3 normal-priority
parallel curve/Gemma and engine ingestion; timing-only runs; provider-cache
admission test; quality at depth; remaining vLLM bridge and Bonsai2 data.
Each exact raw macro body/site is calc/tests/data/paper-v5a4-pending.json.
Twenty repeated hook sites are inactive;20 pending sites remain visible.

All gates run directly with real exits, disk TMPDIR, PYTHONDONTWRITEBYTECODE=1,
CPU/cache only. Before each gate: df -BG plus exact bytes; wait up to20min
below28.5GiB, no foreign cleanup. No push/tag/native build/download.
Fresh exact-head receipts, all diagnostic failures and corrections, complete
argv/environment/disk samples: .temp/hybrid-c-r21e-261103/*.json and *.log.
Final source identity and actual exits: final-gates.json/delivery.json;
PDF: .temp/hybrid-c-r21e-261103/hybrid-inference-v5a4-draft.ru.pdf.
Counts before and after use the same lexical parser (sections00--14, excluding
appendices/table bodies/math/TikZ/comments and inactive blocks). Baseline40pages,
17476 main-text words; exact candidate counts and both abstract lengths in
counts-delivery.json and abstract-delivery.json. This tracked map identifies
the receipt paths; green status is asserted only after actual execution.

Pre-signature rendered draft: 41 pages, 17186 main-text words; Russian abstract 1337 characters (583 reserve), English 1328. Final exact-head counts are separately verified in the delivery receipts; word change includes the owner-requested archive move and repeated-notice consolidation.


## v5b successor

Owner run hybrid-c-r21f-261103 integrates accepted engine22 and resolves the26 economic/model hooks.
The original v5a inventories and evidence stay immutable. Current old/new/source and pending map:
`calc/PAPER-V5B-GAPS-261103.md`, with every legacy ID in `data/measurements/paper-v5b-2026-11-03/r20-migration.json`.
The temporary abstract reserve and inactive repeated hooks are superseded by current conditional prose.

## v5d7 successor

Owner r21n specifies the internal equal-cost80% remainder; current scope and new model-class waits are in `calc/PAPER-V5D7-GAPS-261105.md`. Earlier closed-contour assumptions above remain historical. Native economics stay unchanged pending engine26.

## v5d8 successor

Accepted engines25/26 and lifecycle methods supersede the former model deferrals. Current map: `calc/PAPER-V5D8-GAPS-261105.md`; physical/protocol waits remain explicit.

Current post-review factual successors and architecture/start-capacity limits: PAPER-V5D9-GAPS-261105.md.
