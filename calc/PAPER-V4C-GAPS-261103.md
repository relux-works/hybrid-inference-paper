# Paper v4c: engine17, time accounting and Gemma correction

Owner run `hybrid-c-r20c-261103`; base `paper-v4` at
`4a0890efe73f154f75f70ba7e474520a1f7164a9`. Title, thesis, four Cyrillic author
names and release version stay unchanged. No whole-paper length target and no
unsuperseded content cut for space. Earlier gap maps/number ledgers remain historical.

## Input custody and integration

Signed merge `dd7a7e2254210e08798a3abab6765355d4270c5f` has the exact accepted
engine-r17 parent `714fe72135819ededd7c270dd661c1359acfa6c3` (Muse r5t ACCEPT per owner).
Objects came only from the requested local calculator checkout. Append conflicts
in README/UNRESOLVED retained both sides; root manifest was regenerated.
Engine17 code, configuration, accepted report/quotes/outputs are unchanged.
Older exports, historical fixtures and kit source remain unchanged.

Authority:

- `calc/ENGINE-REPORT-R17-261103.md`, `calc/ENGINE-QUOTES-R17-261103.csv`, `calc/out/run17/`.
- Five exact architecture exports also in `paper/data/engine17/`.
- Current FACTS, precise time-accounting report, producer arithmetic/input hashes
  and three raw local evidence files in `data/measurements/paper-v4c-2026-11-03/`.
- Prototype `64dc3c699d2885f49146a0536f98c4fb06555692` CPU bf16 report and format
  document copied via local Git; Muse r7ah acceptance is owner-supplied.

No producer native/model test was rerun here. CPU evidence and long-context GPU/Mac
measurement are distinct. Source SHA256 inventory is in the data README.

The main R16 diagnostic/economic snapshot remains explicitly named. R17's new
threshold table uses exact tensor bytes and same-build PRO6000 rates. R16's
B300/rounded-state threshold and bounded-undo sensitivities are retained as separate
calculations; this is not a silent substitution of one hardware basis for another.
The paired R17 f32/bf16 economics case is separately displayed and source-bound.

## Thresholds and Gemma

Minimum downstream MB/s at100k, ordered delta512 /2343 /10000:

|Model / state|512|2343|10000|
|---|---:|---:|---:|
|Qwen f32|47.686|7.905|3.416|
|Qwen bf16|26.276|5.305|2.885|
|Glimmer interim|26.647|2.090|0.972|
|Gemma interim|28.853|6.588|2.351|

All32k/64k rows are also printed; labels mean32000/64000 prefix tokens.
Qwen uses recorded PRI31. Every SWA threshold/comparison surface states both:
Mac rates PRI4/interim with PRI31 repeat queued, and the named Qwen-import
portability estimate without an SWA import calibration. The engine identifier is
`r16_qwen_token_depth_portability`; visible Russian name: transfer of Qwen's import law.
Window bytes affect wire only in this estimate; additional SWA import work is unmeasured.
Catch-up, framing/chunk overhead and queues are excluded from the serial threshold budget.

The universal r20b inference from Gemma's larger fixed part is removed. The445.6MB
window arithmetic remains:1024*435200=445644800B. Gemma prefill is slower locally;
at100k/delta2343 its threshold6.588 is below Qwen7.905, at32k21.851 is above17.606,
at64k10.984 is below12.342. All comparisons remain interim with the explicit import estimate.
Abstract and limitations replace the R16 boundary8.05 with R17's7.905; measured
home-Wi-Fi5.19MB/s all-local and5G9.75MB/s preflights remain historical measurements.
The old8.45MB/s policy-entry threshold remains explicitly a different policy calculation.

## Complete live-window geometry and operation-scaled sensitivity

The earlier native comparison used `min(delta,W)` window positions. An offload
at depth L transfers all live positions, `min(W,L+delta)`. This supersedes the
partial-window assumption rather than hiding it under a label. No engine export is edited.
`paper/data/arch_compare.py` applies accepted R17 geometry and retains the clearly
labelled R16 Qwen/FLOP-scaled prefill sensitivity, not a calibrated SWA speed claim.
The generated native CSV is independently checked and every changed table cell bound.

|Quantity|Old|New|Source/arithmetic|
|---|---:|---:|---|
|Glimmer 1k delta, MB|28.3|50.522368|7072*1000+43450368B|
|Gemma 1k delta, MB|479.0|489.164800|43520*1000+445644800B|
|Glimmer table integer MB|28|51|round exact50.522368 once, not rounded50.5 again|
|Gemma table integer MB|479|489|exact489.1648|
|Glimmer transfer300Mbit/s, s|0.8|1.3|50.522368/37.5|
|Gemma transfer300Mbit/s, s|12.8|13.0|489.1648/37.5|
|Glimmer saving100/300/1000Mbit/s, s|12.5/14.0/14.6|10.8/13.5/14.4|same unrounded operation-scaled local time minus complete-window transfer|
|Gemma saving300Mbit/s, s|13.1|12.8|same operation-scaled sensitivity;100Mbit/s still routes local|
|Hypothetical6KiB/bf16 Qwen bytes|about84MB|84.590592MB|78.446592+1000*6144/1e6|
|Hypothetical100Mbit/s reading-minus-wire saving|18s vs9s|11.8s vs3.3s|18.6069-84.590592/12.5, PRI31 local rate|

The hypothetical byte example explicitly excludes server/import and makes no real-model
or measured bf16-speed claim. SWA rates in the operation-scaled table are estimates
from Qwen; actual interim measured-rate comparisons use the separate R17 threshold table.
At the native-context boundary, the large-depth Glimmer/Qwen3-32B examples are explicitly extrapolations.
Two printed GPU cells follow R17 raw-once rounding: Qwen50k decode57.3->57.2,
Gemma249k delta2000 prefill511->510. Four other declared rounding corrections concern
metrics not printed in that current measurement table; the accepted ledger preserves all six.

## Architecture extrapolation and bf16 calculations

All15 S/K cells are shown, with Qwen rates/import/RTT fixed atdelta2343/depth100k.
`D=S*10^6+K*1024*2343` B, decimal MB/binary KiB. Examples: S0/K2=0.159MB/s,
S10/K2=0.491, S157/K34=7.909. The rounded78.5/157MB grid differs from exact
78.446592/156.893184MB tensors. Both caption and prose say extrapolation, not a real-model claim.

Only recurrent wire tensors halve. Saving is78,446,592B/offload; attention KV,
resident f32 state, decode, storage migration and import coefficients do not halve.
Atdelta2343 transfer alone is24.458->16.412s at9.75MB/s,45.947->30.832s at5.19MB/s.
Illustrative$0.02/decimal-GB egress: $0.00476934->$0.00320041, saving$0.00156893.
The paired economics table displays all report observables (duplicate capacity/served
fields share one row), with six-decimal calculation values and explicit scope:
M3 Max four streams,1Gbit/s,8h; heavy traffic; costs team5/share20%/already-owned Mac.
M3 multi-stream outputs remain PRI4/interim. The$5/TB baseline and$50/TB traffic
illustration are separate. Changing policy means monthly bytes need not halve;
hosting/migration cost rises with more offloads. These are calculations, not bf16 runtime measurements.

CPU transport is implemented and reviewed, intentionally lossy. Exact controls
classify bf16 as lossy even if argmax agrees. Real-state rounding0.00389<2^-8
is scoped to checked normal values of a16-token Qwen3.5-0.8B state (source maximum0.00389105),
not a27B quality result or a bound on overflow/subnormal edge cases. GPU/Mac
quality and speed remain a real pending measurement, as explicitly required by owner r20c.

## Precise time accounting

|First call|Old rounded account|Current traced account|
|---|---|---|
|TTFT|201.7|201.655s (raw201.655099)|
|Outside prefill/transfer/import|25.5, called unattributed|25.370s|
|Enclosing attribution|pending|19.659s request preparation +5.711s client outside preparation|
|Known components|10.6+123.2+42.4=176.2|10.643+123.219+42.423=176.285|
|Complete stream|TTFT sometimes called full time|202.089s; TTFT ends at first nonempty text|

The19.659s interval includes upload, first-byte wait, node full-state load/export/save
and checksums, not separate measured durations of those operations. Older request
bookkeeping/readback is also inside its enclosing span; it is not all GPU compute.
The unrounded raw JSONL rejects the25.5-second interpretation; rounded old summaries
are retained only as rounded values in the original model-comparison case.

The growing base's2.908s import already sums all ten requests:
2.508157+0.399364=2.907521s (nine stages plus final request). It must not be added twice.
After snapshots/prefill/transfer/import,41.168s remain;40.165s are inside ten node extend
requests, including full-state load/save/checksums and synchronous evidence hashing25.748GB.
That hashing is outside snapshot-download timers. Capture subtraction is therefore an
arithmetic upper bound containing instrumentation, not a measured production TTFT.

The additional accounting table also retains turns7/31: remainders9.859/7.786s,
inside-extend5.272/6.637s, hash volumes4.118/5.147GB. No hash duration is inferred
from bytes or an unrelated CPU benchmark. Turn31's3.812s cursor catch-up is earlier
than its critical TTFT path; its critical sync is0.312s. Turn7 critical sync totals3.927s.
Original R16 prediction rows remain source-identified coarse comparisons using their
original summary fields; refined timer boundaries do not manufacture a new calibrated prediction.

## Every pending macro

Exact sites: `paper/sections/04-channel.tex:128`, `paper/sections/04-channel.tex:159`, `paper/sections/04-channel.tex:332`, `paper/sections/11-limitations.tex:76`, `paper/sections/90-appendix.tex:132`, `paper/sections/90-appendix.tex:134`.
Six sites, enumerated byte-for-byte in `calc/tests/data/paper-v4c-pending.json`.
The earlier requirement to source waits only from FACTS5 is extended by the two
explicit new owner requests, not by an invented FACTS edit.

|Site|Wait and authority|
|---|---|
|04-channel, time-accounting paragraph|Timing-only Mac/node calls without capture/evidence hashing, separate stage spans; owner r20c input3 and accounting report instrumentation section|
|04-channel, checkpoint paragraph|Mac checkpoint10 recheck and RAM investigation; FACTS5|
|04-channel, bf16 paragraph|GPU/Mac bf16 quality and speed; owner r20c input1 and accepted CPU report|
|11-limitations, RULER paragraph|32k run expected about6h from07:32UTC;64k/128k owner budget decision; FACTS5|
|90-appendix, growing-session paragraph|Same Mac checkpoint10/RAM recheck; FACTS5|
|90-appendix, grouped waits|RULER32/64/128k; full PRI31 M3 curve/Gemma/Glimmer after idle Mac, then16b; CUDA/Metal BF16 calibration needs Mac; GPU vLLM bridge after rework; Bonsai2 ladder later; FACTS5|

Source time estimates are reported as provided input state, not a live job-status poll.
CPU bf16 implementation, RULER8k and both timing arms have data and are not pending.

## Counts and validation

Initial cached build:33 pages. Corrected lexical counts: r20b base16,132 words,
v4c17,264 (+1,132), pages31->33. Exact final source/head counts are recorded in the delivery receipt.
No whole-paper length target. Original r20b count14,285 used a regex that mistakenly
paired escaped currency signs as math delimiters and undercounted prose. Both versions
are recounted with the corrected parser; the legacy count is disclosed for continuity.
Same definition: sections00--14, headings/captions/prose footnotes and numeric prose tokens;
exclude appendix/bibliography/table bodies/TikZ/math/comments/command names and reference arguments.
Control fixture keeps escaped$10/$50 and removes actual$x=3$ math. PDF page nodes/tree count agree.
Scripts/receipts: `.temp/hybrid-c-r20c-261103/{count_size.py,baseline-counts-corrected.json,after-counts.json,counter-control.json}`.

All430 pre-existing reviewer test names retained. New controls independently check
raw/chunk arithmetic, complete live-window geometry, per-row threshold budgets and
interim labels, depth-dependent Gemma comparison, extrapolation limits, CPU loss and
six real pending sites. Both checker self-tests retain exact named verdicts, including
coupled pending-inventory diagnostics. Current publication pins add five exact R17
inputs and regenerate the corrected architecture projection; frozen historical fixtures
are unchanged. The new migration ledger records exact authorized historical deltas.

Required gates: full engine/kit; range/offload checkers and each self-test; publication_v2,
r13_ledger, spacing, release/signature fixtures; cache-only make pdf; make manifest,
then checksum verification sequentially. Every command has PID/exit/time/head/disk
receipts under `.temp/hybrid-c-r20c-261103/`; no tee. Disk TMPDIR,
PYTHONDONTWRITEBYTECODE=1, CPU only, no downloads/native builds/push/tag, disk>28GB.
No attack-surface table supplied (brief gap); no requested clause out of contract.
Self-review and source custody precede local handoff; independent acceptance remains orchestrator-owned.

Diagnostics retained: merge-engine exit1 for expected append/manifest conflicts,
resolved without dropping either document side. First offload checker exit1 on an
incorrect exact import-assumption string; second exit1 exposed a double-rounding tie
in the new Glimmer integer cell, corrected by retaining exact byte arithmetic before
printing. First PDF exit2 because cmr9.pfb was not cached; equivalent plain-text table
labels removed the uncached-font requirement, subsequent cache-only build exit0.
Initial new-control suite exit1 because two literal multiline plants were not applied;
scoped whitespace-normalized plants now assert application and reject their intended
violations, all10 focused controls pass. No setup error or unapplied plant is counted
as successful negative evidence. Original architecture controls and31 review compatibility
checks pass; final full gates and custody receipts follow after execution.

The first publication-spacing gate exited1 on nine joined prose words/numbers in README/CHANGELOG.
Those spaces and a stale merged CPU-status sentence are corrected. The initial owned engine process
was stopped with SIGTERM (-15) before editing; its partial log is diagnostic, not green evidence.
A fresh full suite runs against the signed corrected source.

The second partial full-engine log contained a failure in the preserved
`HistoryFixtureTests.test_reviewed_paper_bytes_preserved`: the new migration hash was paired
with the old v4b migration filename. The one-path correction reads the new exact v4c ledger;
all seven historical-store tests now pass, with original assertions/fixtures unchanged.
The second owned partial suite was stopped with SIGTERM (-15), not counted as passing;
its focused diagnostic exited1 on the intended hash rejection. Fresh full-suite evidence follows.

## Green frozen-source receipt

Source `611286027958c4d0899aa0920134244ea5784709`: engine **443 tests**, kit **24 tests**, all final required gates exit **0**.
All 2,541 tracked files equal the full-suite input hashes. Command/PID/head/environment/disk/exit receipts:
`.temp/hybrid-c-r20c-261103/final-gates.json`; every receipt has a separate complete log.

| Gate / receipt basename | Actual exit |
|---|---:|
|`engine-03`|0|
|`kit-01`|0|
|`ranges-final`|0|
|`ranges-self-final`|0|
|`offload-final`|0|
|`offload-self-final`|0|
|`publication-frozen`|0|
|`ledger-final`|0|
|`spacing-source-final`|0|
|`release-final`|0|
|`release-signatures-final`|0|
|`pdf-source-final`|0|
|`manifest-frozen`|0|
|`manifest-check-frozen`|0|
|`signature-frozen`|0|

Unchanged kit, range/offload, ledger and release evidence is reused on exact unchanged
source/test/input bytes in the same environment. The finite intervening-path lists are
in `unchanged-gate-dependencies.json`: only root documentation, gap/manifest and the
publication guard changed; the corrected publication guard and full engine suite ran
at the frozen source above. Spacing/release receipts already use the corrected README/CHANGELOG.
The PDF scientific source is unchanged; a fresh cache-only PDF is built at the delivered head.
No partial or stopped suite is used as green evidence. Both stopped processes returned
-15 (driver exit241); the focused historical diagnostic returned1, then the preserved
historical-store/producer tests passed after the exact filename correction.

| Negative plant | Gate narrowed to | Named test / observed rejection | Survivor bound |
|---|---|---|---|
|Universal faster-link claim for Gemma|Depth-dependent measured-rate budget|`test_gemma_comparison_is_depth_dependent`, `v4b Gemma link scope` rejects|No survivor in these controls|
|Delta-only SWA window|All live positions at a hot prefix|`test_architecture_projection_keeps_complete_live_window` rejects the partial-window sizes|Other architectures remain outside this geometry check|
|Double-count the nine staged imports|Exactly ten imports, 2.908s total|`test_growing_base_import_sum_rejects_double_counting`, `run17 base import total` rejects|No claim about separately untimed subphases|
|Capture subtraction called production TTFT|Hashing remains in the upper bound|`test_growing_accounting_keeps_hashing_inside_upper_bound`, three named checker sites reject|No instrumentation-free timing measurement|
|CPU bf16 called lossless|Lossy CPU result and GPU/Mac boundary|`test_bf16_cpu_rounding_and_measurement_boundary`, `run17 bf16 CPU loss` rejects|No GPU/Mac quality or speed qualification|
|Remove any new row/qualification|Every registered R17 publication site|`test_run17_publication_sites_reject_omissions`, each named site rejects|Finite registered prose/table scope|
|Re-add pending CPU implementation|Only six genuine pending sites|`test_snapshot_custody_and_six_real_pending_sites`, pending inventory rejects|Pending job status is source state, not a live poll|
|Read v4b ledger with v4c hash|Exact historical migration payload|`HistoryFixtureTests.test_reviewed_paper_bytes_preserved` actually failed; corrected seven-test store suite passes|Frozen fixture bytes/assertions remain unchanged|

The isolated in-memory delta-only-window code mutant actually exits1 in
`test_architecture_projection_keeps_complete_live_window` (28,288,000 vs50,522,368B);
its unmodified one-test positive control exits0. Receipts: `window-mutant`/`window-clean`.
This expected-red mutant is not a required production gate and is never reported as green.
No product file or frozen fixture was modified by that control.

Both checker self-tests include clean positive controls and applied known violations;
unapplied plants and setup errors are diagnostic failures, never successful controls.
No unchecked survivor is presented as verified coverage.

Cache-only PDF:33 pages,17,264 corrected lexical main-text words; abstract1,364 plain
characters (1,372 conservative TeX characters). Comparable corrected r20b baseline:
31 pages,16,132 words; the legacy14,285 count is separately disclosed above.
No overfull box, undefined reference/control or missing-glyph warning was observed;
underfull spacing warnings remain. No full visual review is claimed.
CPU only, disk TMPDIR, no downloads/native builds/push/tag; disk samples remain above28GB.

The evidence-only commit changes this gap map and the root manifest. All other tracked
bytes must equal the green-suite source. Owner PDF:
`.temp/hybrid-c-r20c-261103/hybrid-inference-v4c-draft.ru.pdf`.
Exact delivered head, signatures, final PDF/count/hash and addressed Matrix readback:
`.temp/hybrid-c-r20c-261103/delivery.json`. Independent acceptance remains orchestrator-owned;
source package ready for review. No brief clause is out of contract; no surface table was supplied.
