# Paper v4b: owner follow-up and finite gap map, 2026-11-03

Authorized base: `paper-v4` at `b9ee9c8c5ae103bf07ae111e4610cf2ee46bca9f`.
This is the r20b follow-up to `PAPER-V4-GAPS-261103.md`; its numeric ledger and
validation history remain historical evidence. The owner revoked r20's no-growth
target. Title, thesis, four Cyrillic author names and release version stay unchanged.
No cut is justified by whole-paper length. Abstract length is a separate arXiv constraint.

Authority: unchanged accepted engine R16 `e51942d331e274833f97f934a750d780c9bea9b0`,
`calc/out/run16/base/` and `bounded_undo/`; current FACTS snapshot in
`data/measurements/paper-v4b-2026-11-03/FACTS.md` (including Sergey's 09:11 UTC answer).
The pending source calls its update 08:25 UTC and explicitly notes the brief's 08:40 label.
No report/export/measurement is silently promoted from historical priority conditions.

## Content restoration audit

Compared every changed section against rc.3 `5f9846f` and the delivered r20 tree.
Scratch diffs: `.temp/hybrid-c-r20b-261103/*-r20.diff`. Non-superseded content is
retained at least once; the short abstract relocates detailed claims into the body.

| rc.3 content affected by r20 | v4b disposition and reason |
|---|---|
| Introduction roadmap | Restored, same section references and team range |
| Old M3 singleton ladder and introductory timing | Replaced by PRI31 R16 values; background anchors are superseded, not restored as current measurements |
| Workload mean, median and p90 waiting | Restored with current values: 19.9, 2.8, 54.3 seconds. Derived from all 39,904 normalized calls, including zero-input calls; old 28/4/77 values superseded |
| First historical 5G call, setup, three timing modes and components | Restored in channel section, explicitly PRI4 and pre-import-speed-v2; 271.5/201.7/211.7 seconds, 110 ms RTT, 16.0/9.78 MB/s |
| First-call savings and delivery/import sum | Restored with shown arithmetic: 25.7% (about26%); 165.6 seconds of transfer/import; measured component sum176.2 |
| 25.5 seconds unattributed | Restored explicitly; time-accounting analysis running; no invented attribution |
| First-call wire explanation | Restored 2,004,023,525 B, 39,504*34,840 B KV and four156.9 MB state copies, chunks up to512 MiB; distinct from one-copy model tables |
| First-call model validation | Restored with R16 prediction139.2 vs201.7; components11.7/125.4/2.2 vs10.6/123.2/42.4; local241.1 vs271.5. Old179.5 is superseded. Different implementation/priority conditions stated; no fitted residual |
| CPU optimization and cross-backend qualification reference | Restored reference to prototype appendix; optimization details already retained there |
| Network placement | Restored office, corporate/VPN, colocation and rented-provider distinctions, including both traffic tariffs |
| Old channel concluding paragraph | Content retained in current link-threshold, offload-table and traffic discussion. Blanket100Mbit/s applicability is superseded by per-call thresholds; no duplicate concluding paragraph required |
| M3 control after34-minute fill vs restored context | Restored with historical PRI4 label and lower-bound meaning |
| Decode headroom discussion | Restored; engine speedup remains conditional on measurements, no projected improvement claimed |
| M5/M3 prefill ratio | Restored using all six current segment pairs: minimum95.1/52.5=1.81, maximum586.4/191.5=3.06. Old2.00--2.86 is superseded |
| First-call summary removed from conclusion | Full experiment/calculation restored in channel section; conclusion retains newer growing-session results |
| Superseded placeholders for timing arms and RULER8k | Removed; measured results retained. Mac checkpoint and deeper RULER remain pending |
| Long abstract's prior art, detailed KL/task-pilot claims, server/storage/autonomy scope | Prior art and scope remain in introduction; detailed KL and task bounds retained in limitations and prototype appendix. Original named reviewer checks follow the relocated body sites |
| Economics, million-token results and appendix formulas | No unsuperseded result removed; R16 replacements and source qualifications retained |

The full changed-numeric-spelling inventory is `PAPER-V4B-NUMBERS-261103.csv`.
It pairs changed subsequences inside each file, not necessarily identical quantities.
Every current numeric occurrence is separately pinned by the publication guard.

## Abstract and applicability

Plain abstract: **1,336 characters**, including spaces, excluding the typeset label.
Conservative normalized TeX body: **1,344 characters**, including escape syntax.
Both counts are below1,920. The exact definition is `offload_bound.abstract_text`;
the independent scratch receipt is `.temp/hybrid-c-r20b-261103/abstract-count.json`.
The checker admits a1920-character body and rejects1921 with the named length verdict.

The contribution and three measured results remain: same-partition CUDA identity,
40-turn CUDA/Metal5G run to143,439 with10.0--12.3 tok/s decode at PRI31, and RULER8k
97.01%/390 with zero score disagreements. One limits sentence includes unestablished
2pp equivalence, audit/Mac calibration, synchronous TTFT instrumentation, the home
Wi-Fi5.19 MB/s all-local result and the R16 f32 threshold8.05 MB/s for2343 tokens at100k.
The same link boundary now appears in limitations. These are per-call equal-cost
thresholds; catch-up and queues are excluded. The old8.45 MB/s policy-preflight
calculation remains explicitly historical in related work.

Abstract, introduction and conclusion state the same applicability conditions:
20% open-model share, already-owned Max/Ultra, **1.2--1.5x cheaper than median
same-model API, 4.8--6.0x dearer than the cheapest**, across clients/retention cases.
These figures do not assert universal savings or measure task quality.

## Closed-perimeter light load: all teams, two policies

Scope: 200 calls/day/person, Qwen, already-owned M5 Max64GB; selected eligible
hybrid and all-server fleets with identical retention and latency constraints.
Every selected route must have exactly one row; no unselected or other-client row supplies a quote.
Source files: `calc/out/run16/base/perimeter_cost_light.csv` and
`perimeter_cost_light_conservative.csv`. Formula: `100*(1-hybrid/person_server)`;
negative savings mean dearer. Percentages are rounded once to one decimal.

| Team | Protocol: own / hybrid USD per person-month | Hybrid relative to own | Cautious: own / hybrid USD | Hybrid relative to own |
|---|---|---|---|---|
|5|147.188159 /154.708159|5.1% dearer|147.188159 /154.708159|5.1% dearer|
|10|74.782409 /82.302409|10.1% dearer|74.782409 /82.302409|10.1% dearer|
|20|38.579534 /46.099534|19.5% dearer|38.579534 /46.099534|19.5% dearer|
|50|33.526788 /24.377809|27.3% cheaper|40.845595 /33.884445|17.0% cheaper|
|500|32.389684 /20.014912|38.2% cheaper|35.260982 /25.074039|28.9% cheaper|
|5000|32.136728 /19.761956|38.5% cheaper|35.008026 /24.568126|29.8% cheaper|

The conclusion states every team result. Registry: `v4b light team <N>`.
Scratch full-precision source-row proofs: `perimeter_cost_light*-proof.json`.
The old conclusion's broken sentence is removed; the economics summary's duplicated
"cheaper" wording is also repaired without changing its conclusion or site counts.

## Source qualifications and geometry

M5 priority: **not recorded; launching process was PRI31 when checked afterwards**.
The observation is Sergey's answer via Ivan,09:11 UTC; it does not record llama-server
QoS during the sweep. Captions and conclusion use this caveat. Historical1.4.1
measurements separately say priority was unrecorded. Original accepted R16 data
keeps its historical `owner_reported_normal_priority_not_recorded` field; current
paper prose follows the later answer. No accepted export/report/quote is rewritten.

Gemma uses only owner-provided kit1.6.5 geometry and FACTS4 for the new link claim:
`1024*435200=445644800 B =445.6448 MB`, about445.6 MB, versus Qwen156.9 MB fixed
state. Full-attention KV adds43,520 B/new token. A larger fixed part needs a faster
link to transmit that part. No Gemma/Glimmer calibrated speed or link threshold is
invented; those engine results follow later. The pre-existing analytical architecture
comparison remains an estimate; its min(delta,window) projection for a1000-token
portion is distinct from transferring the complete1024-position window here.

## Every remaining pending macro

Only four macro sites remain. `calc/tests/data/paper-v4b-pending.json` stores every
body and its FACTS5 wait. `offload_bound.pending_gaps` rejects added, removed or
changed placeholders. No RULER8k, timing-arm, KL or completed pilot placeholder remains.
Exact line references: `paper/sections/04-channel.tex:117`, `paper/sections/11-limitations.tex:76`, `paper/sections/90-appendix.tex:132`, `paper/sections/90-appendix.tex:134`.

| File/site | Waiting for, from current FACTS section5 |
|---|---|
|`04-channel.tex`, repaired backend-label paragraph|Mac checkpoint10 recheck; first retry refused RAM before checker launch|
|`11-limitations.tex`, RULER depths|RULER32k run started07:32 UTC, expected about6h;64k/128k after owner budget decision|
|`90-appendix.tex`, growing-session checkpoint|Same Mac checkpoint10 recheck and RAM investigation; timing arms are measured|
|`90-appendix.tex`, grouped remaining measurements|RULER32k/64k/128k; full PRI31 M3 intermediate-count curve and PRI31 Gemma/Glimmer after idle Mac window; then engine16b; CUDA/Metal BF16 calibration needs Mac; GPU vLLM bridge after rework; Bonsai2 2B/4B/9B later|

The source's time estimates are quoted as its recorded state, not refreshed live job status.
Bounded undo and bf16 bridge qualification remain future-work limits, not fabricated
FACTS5 pending macro sites. M5 priority rerun and first-call time accounting are
explicit qualifications without new pending macros.

## Size and validation protocol

| Quantity | r20 base | v4b | Difference |
|---|---:|---:|---:|
|PDF pages|30|31|+1|
|Main-text lexical words|13,729|14,285|+556|

For comparison, rc.3 was30 pages/13,845 words. Owner expressly authorized growth.
Same parser before/after: sections00--14 including05b, headings/captions/prose
footnotes, excluding appendix/bibliography/table bodies/TikZ/math/comments/command
names and label/reference arguments; numeric prose tokens count. Scripts and
receipts: `.temp/hybrid-c-r20b-261103/{count_size.py,baseline-counts.json,after-counts.json}`.
PDF page nodes and the page-tree count agree; no external dependency was installed.

Required standalone gates: full engine and kit suites; both publication checkers
and each self-test; publication_v2, r13_ledger, spacing, release46/signature12 fixtures;
cache-only `make pdf`; `make manifest`, then checksum verification sequentially.
Every actual command, PID, exit, elapsed time, head and sampled free disk is recorded
in `.temp/hybrid-c-r20b-261103/<gate>.json` with its log. No native build/download/GPU.
Keep free disk above28,000,000,000 bytes; disk TMPDIR and PYTHONDONTWRITEBYTECODE=1.

Finite controls:1920/1921 length boundary, each light-team amount, duplicate selected
rows and inverted source directions, erased novelty/link/priority/accounting/geometry
qualification, pending additions/removals, and all-call distribution vs dropping zero
inputs. Tests name each claim and limitation. All old reviewer test names remain;
original range site cardinalities156 remain, with three explicit collision entries
independently checked by the new source-bound registry/distribution tests.
Historical fixtures and accepted R16 source/data stay unchanged. Current publication
byte/numeric pins and a new `paper-v4b-migration.json` record only authorized changes
against frozen fixtures. Brief contains no attack-surface table (declared brief gap);
no requirement is treated as out of contract. Self-review precedes signed local
handoff; independent acceptance remains with the owner/orchestrator.

Diagnostic failures are kept: first offload/range gates exit1 while prose bindings
were being migrated; the initial edit-helper assertion concerned the tuple syntax of
ALLOW, and its applied subset was inspected before completing the remaining edit.
The preliminary broad paper-test selection finished before an attempted owned-PID stop; the PID had already exited, so no signal was sent. The actual receipt, not an inferred stop, records its verdict. No failed/incomplete command is counted as a green gate. Preliminary cached PDF
build exited0 with underfull spacing warnings; full visual review is not claimed.
Final gate receipts and exact source/artifact custody follow below after execution.

The first frozen-source offload self-test exited1: a plant inside the old growing-session pending body
correctly reported both `v4b pending inventory` and `run15 growing pending`, while the old CLI harness
expected only the latter. The corrected harness derives whether its plant changed a pending body and
requires both exact named diagnostics. A named regression independently asserts the two verdicts;
no diagnostic is suppressed. Source-e16f55d engine attempt was stopped by its recorded owned PID
(exit-15) before editing. Corrected checker/pins and a fresh full engine run are required.

## Green frozen-source receipt

Source `c2064579f6437d823ed69a7f875b267aaf4e2144`: engine **415 tests**, kit **24 tests**, all final required gates exit **0**.
All 2,414 tracked source files still equal the suite-input hashes. Full per-command receipts:
`.temp/hybrid-c-r20b-261103/final-gates.json`; each has a separate complete log.

| Gate / receipt basename | Actual exit |
|---|---:|
|`engine-02`|0|
|`kit-01`|0|
|`ranges-final`|0|
|`ranges-self-final`|0|
|`offload-source-final`|0|
|`offload-self-source-final`|0|
|`publication-source-final`|0|
|`ledger-final`|0|
|`spacing-final`|0|
|`release-final`|0|
|`release-signatures-final`|0|
|`pdf-corrected`|0|
|`manifest-source-final`|0|
|`manifest-check-source`|0|
|`signature-corrected`|0|

Kit/range/release evidence from e16f55d is reused only for unchanged source/test/configuration and the same disk-TMPDIR/environment.
`unchanged-gate-dependencies.json` enumerates the seven intervening paths; all bench dependencies, range checker and paper prose are byte-identical.
The corrected offload self-test and final publication guard additionally ran at frozen c206457; the fresh full engine suite used that complete source.
Earlier stopped engine process returned -15 (its Python driver exited241); this is not green evidence.
The first offload self-test exited1 on the coupled diagnostic; the corrected exact-diagnostic harness and named regression pass.

Cache-only PDF:31 pages,14,285 lexical main-text words; abstract1,336 plain characters (1,344 conservative TeX characters).
No overfull box, undefined reference/control or missing-glyph warning was observed; underfull spacing warnings remain.
No full visual review is claimed. Disk samples stayed above28GB; no native build, GPU, download, push or tag.

The final evidence-only commit changes this gap map and the root manifest. All other tracked bytes must equal the green-suite source.
The owner PDF is rebuilt at the delivered head and copied to `.temp/hybrid-c-r20b-261103/hybrid-inference-v4b-draft.ru.pdf`.
Exact head, PDF SHA256, signature readbacks, final counts and the authorized Matrix event/readback are stored in
`.temp/hybrid-c-r20b-261103/delivery.json`. Independent acceptance remains with the owner/orchestrator; source package ready for review.
