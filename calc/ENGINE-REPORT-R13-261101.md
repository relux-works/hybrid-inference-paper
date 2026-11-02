# Engine run 13: reproduced server base, measured M5 and corrected inputs

Run `hybrid-b-r32-261101`. Local branch `engine-r13` starts at public main
`c04a99dd06a9cf97f57baeb856e471b7b987c611`. Run12 `1da488a` was replayed as signed
commit `7c2e9b1e8e87835f474ae45a4454bda74f4af6d3`, with the requested coauthor.
The only replay conflicts were README and MANIFEST: public-main documentation
was retained, run12 documentation appended, and the manifest recomputed. No
calculator conflict required a mathematical choice. Nothing is pushed.

The run13 base uses the reproduced checkpoints-off llama.cpp curve and measured
M5 Max64. Earlier-run and checkpoints-on sensitivities use identical current
client, price, geometry, workload and hosting inputs. vLLM is a separate measured
server-only prefill option. It is never selected for a hybrid route: a compatible
state bridge to the client does not exist. No GPU computation, download, install,
native build or paper rendering was performed.

All **150 historical exports** in `calc/out/paper/`, including every run12 chart
and sidecar, remain byte for byte. Published TeX and the embedded run11 engine
snapshot in `paper/data/engine/` remain unchanged. The requested native Gemma
formula and `paper/data/arch-compare.csv` are corrected. Their pending printed
replacements, other table cells, plot data and prose are inventoried in
[ENGINE-QUOTES-R13-261101.csv](ENGINE-QUOTES-R13-261101.csv).
`paper/style.ru.md` was absent from both this checkout and public main; no new
Russian paper prose was authored. Existing Russian quote fragments identify
unchanged publication sites.

## Archive custody

All full hashes below were computed locally before import. Every manifest-listed
payload has its size and SHA-256 checked before use; imported copies are checked
again against their archived bytes. Four original archives, four provenance
READMEs, four manifests and 179 verified payload files are retained. AppleDouble
transport metadata from the Mac archive is excluded from extracted payloads.
The verifier never extracts tar paths and rejects wrong hashes, unsafe paths,
links, duplicate members, unmanifested payloads and manifest mismatches.

| Package | Archive SHA-256 | Verified payloads | Imported directory |
| --- | --- | ---: | --- |
| phase_a | `fd0bc08cd310718fadbe10f9badb081abcceb15d8bdb24d0e108305340d76040` | 125 | `data/measurements/vast-2026-11-01/r13-phase_a` |
| off | `e80d4240b6e35d384e29a31c14269716b430728472a1253220e2235bbd1ab3c2` | 14 | `data/measurements/vast-2026-11-01/r13-off` |
| on | `92828a6c8e5796042fd7175d2b9281d71de3e9a9522af2d1833b8ddaa48c5d38` | 14 | `data/measurements/vast-2026-11-01/r13-on` |
| m5 | `c7ceab57f8d61b9bd166daf96cae1e8f389d296c0f9789ccb8cc32536d9f6b05` | 26 | `data/measurements/m5max64-2026-11-01` |

Archive filenames and original local paths are recorded in each provenance
README and `calc/hybridcalc/data/run13-measurements.json`. The owner identifies
the GPU delivery as Vast 58647134, RTX PRO 6000 Blackwell Workstation Edition.
Phase A's manifest says results kit 1.6.1, packing kit 1.6.3, checkpoints0; the A/B
arms say kit 1.6.3 and checkpoints0/server-default. The Mac manifest says kit 1.4.1.
Model hashes, llama.cpp c21284cdf, commands, conditions, sweep/server-load outputs,
startup errors and telemetry remain available in the verified payloads.

## Server fit and FP8 envelope

The base is an unweighted twelve-point OLS fit of exact
`prompt_ms / 1000 / prompt_n = a + b * nominal_depth`, using Δ2000 and Δ10000 at
16k,50k,100k,150k,200k,249k. Phase A supplies the base; A/B off is an independent
reproduction check. The maximum matched seconds/token difference is
**0.354654%**, below 1%; reciprocal rate differences are also below 1%.
Actual starts, including the +640/+2768 offsets, remain explicit in raw data and
the bulk table. Fills and Δ512 are excluded from the fit.

| Curve | a (s/token) | b (s/token/depth-token) | Maximum bulk residual |
| --- | ---: | ---: | ---: |
| phase_a | 0.000229643378041556 | 3.361643993099327e-09 | 3.7131% |
| off | 0.0002297773785621298 | 3.364408505834484e-09 | 3.6513% |
| on | 0.000270547375634954 | 3.08180867638841e-09 | 8.0220% |
| earlier run | 0.0003687230031301119 | 6.065719692011435e-09 | 1.0585% |

The checkpoints-on case means the A/B server-default arm; it is not assumed
uniformly slower at every depth. The earlier run is the unchanged9accab80 archive
curve, retained through its original hash-checked measurement input. The new fit
has larger bulk residuals than the earlier fit; reproducibility does not imply
a 2% affine-fit bound. Held-out phase-A cold fills are56.758s at 131072 and21.733s at
65536; the fitted integral predicts58.976s and22.269s, errors+3.91% and+2.47%.
The earlier run's1.04M YaRN fill does not qualify the new fit at native1M.

Per-call work retains the engine's marginal-depth convention. Cold spans use
`a*N + b*(D*N + N*N/2)`. Beyond249k this law extrapolates; below16k it also extends
the affine server law. There is no small-delta, quality, queueing or concurrency
qualification. B300 uses the same depth-dependent fraction of dense FP8 peak;
GLM applies its own FLOPs to that inferred envelope. Neither is a measurement of
B300 or GLM. Other GPU families retain their declared historical envelopes.

The former8–13% earlier-run statement becomes **14.1339–21.1117%** on the new
fitted base across the six measured depths. Recompute every point as
`(54e9 + 393216*depth)/(a+b*depth)/hardware.servers.rtx1.peak`, or read
`measurements/server_bulk.csv: fp8_fraction`. This is an effective model-FLOP
fraction of the dense FP8 peak, not sampled GPU utilization or a claim that the
Q4 llama.cpp kernels execute in FP8. The public paper currently says30% in the
introduction and intensity caption; those sites are in the quote ledger. Its
ideal M5/B300 ceiling at 110k changes22.5→12.1; server compute there changes
1.35→0.72PFLOP/s. No depth-independent replacement peak fraction is implied.

## vLLM 0.32 FP8

`server-options-r13` exposes both usable FP8 options: default8192 and large-batch
32768 batched tokens, automatic KV dtype. Method A is cold TTFT, including request
and first-token overhead. Independent normal equations reproduce the kit's fit
`TTFT(N)=a*N+b*N*N/2` over eight observations/four lengths:

| Option | a (s/token) | b (s/token/depth-token) | Maximum TTFT residual |
| --- | ---: | ---: | ---: |
| fp8-default | 9.342839036996133e-5 | 1.4140563102468149e-9 | 1.6589% |
| fp8-large-batch | 9.216062614839821e-5 | 1.500578537687494e-9 | 6.2802% |

All16 method-B probes are recomputed from archived raw TTFT and cached-token
counters. Processed work is `depth+delta-cached`; useful work is `delta`. Both
rates are exported. At depth16384, delta2000, cached15680, the default option
processes2704 tokens in0.372420236s: **7260.615 processed tok/s**, **5370.277 useful
delta tok/s**. The704-token remainder is real processed work. Cached counters
align to784-token blocks; the kit's “not supported” label is not used as a rate.
The original raw label remains unchanged. FP8-KV and NVFP4 startup failures stay
unsupported, without invented rates. Cold fits and cached deltas are distinct
experiments and precision differs from llama.cpp Q4. No decoder, quality,
end-to-end server bill or client bridge is inferred from these prefill timings.

## Measured M5 Max64 client

Step40 supplies prefill and decode by depth; steps50/55 supply parallel/scaling
results alongside the original measured M3. The new depth table retains all
three portions and both clients. Economic M5 prefill interpolates six bulk-rate
anchors, each the harmonic mean of exact Δ2000/Δ10000 rates. Single decode uses
exact step40 output counters plus the measured32k/64k/128k controls. Parallel
curves reproduce the measured32k/64k/128k anchors, with three-stream aggregate
throughput interpolated between two and four streams. Common economic coverage
ends at four streams; the observed64k/eight-stream row remains in the measurement
table, without extrapolating eight streams to128k. Outside anchors, curve/depth
extrapolation remains an estimate. The64decimal-GB admission budget is retained;
the Mac system report gives68719476736 bytes. Other M5 configurations retain
estimates and do not inherit the64GB machine's measurements.

| Nominal depth | Δ2000 prefill tok/s | Δ10000 prefill tok/s | Δ2000 decode tok/s |
| --- | ---: | ---: | ---: |
| 16000 | 394.207 | 372.395 | 23.443 |
| 50000 | 211.991 | 206.057 | 19.261 |
| 100000 | 119.415 | 114.820 | 14.720 |
| 150000 | 81.992 | 79.363 | 12.312 |
| 200000 | 62.748 | 60.975 | 10.623 |
| 249000 | 50.755 | 50.021 | 9.228 |

At32k, native single decode is18.29tok/s and four-stream aggregate33.37tok/s;
the engine reproduces both anchors. Step55's kit-reported rate counts127 timed
decode steps for128 output tokens; the separately counter-recomputed interval
column uses128/predicted_ms. Wall rates are separate. Step50 preserves its rounded
summary because raw per-request timing counters are absent from that row.

The post-run review reports zero sampled swap and swap-counter increments in
steps40/50/55. Step57 reached **5095754301 bytes** sampled swap, and its rates are
excluded from all calibration and rate tables. The original step57 artifacts
remain archived. Whole-system60s telemetry cannot attribute paging to a particular
process or quantify a correction; no adjusted step57 speed is invented. Desktop
apps remained open; temperature and GPU utilization were not measured.

Self-review found and corrected an accounting-child propagation bug: output-only
and reasoning-on-top scopes now both inherit the measured-M5 marker. A named
regression requires the output-only sensitivity row to equal its ordinary R13
parent at the same coordinates. A bounded omission mutant fails that exact
assertion. Hypothetical M5 decode improvements are now checked against the new
measured curve's bandwidth fraction; an inherited M3 efficiency cannot admit an
unphysical twofold M5 rate.

## Price, geometry and selected consequences

Current `prices.apis.sonnet.cache_read` is **$0.10/MTok**,0.05×$2 input, using the
owner's 2026-11-01 verification of the supplied [Claude pricing page](https://platform.claude.com/docs/en/about-claude/pricing). Its supplied
quote says cache hits/refreshes on Opus5.5 and Sonnet5.5 cost0.05×base input.
No network verification is claimed in this offline run. The actual `paper-base`
Sonnet API baseline changes **$41.403701→$24.239643 per1000 calls**, and
**$4.802829→$2.811799 per116-call group**. Every current canonical API scenario
is re-exported under `api-baselines/`; Qwen/GLM tariffs are unchanged. The paper's
current model-price CSV already says$0.10 for Sonnet5.5; its$0.20 historical-period
row remains explicitly historical. The year-bill baseline therefore needs no
new correction. Frozen R11/R12 scenarios explicitly read the old price snapshot.

Gemma full-attention KV is `10*4*512*2*(34/32)=43520 B/token`. Sliding KV remains
435200B/token with 1024-position window. Native architecture values change:

| Gemma quantity | Published old | Run13 |
| --- | ---: | ---: |
| Full KV B/token | 21760 | 43520 |
| 1k delta MB | 457.0 | 478.7 |
| 10k delta MB | 663.2 | 880.8 |
| 1k transfer at300Mbit/s | 12.2s | 12.8s |
| Saving at100/300/1000Mbit/s | -2.8/21.6/30.1s | -4.5/21.0/29.9s |

The corresponding new R7 architecture and R8 intensity rows recompute from the
corrected geometry. Their historical export sets remain immutable.

Selected heavy-profile, already-owned client costs, with overflow to cheapest
API; old values are the public R11 paper, not the R12 sensitivity:

| Client | s20 old → R13 USD/person-month | s50 old → R13 USD/person-month |
| --- | ---: | ---: |
| M3 Max 128 GB (measured) | 27.26 → 32.13 | 48.65 → 54.65 |
| M4 Max 128 GB (estimate) | 25.82 → 30.65 | 46.70 → 54.74 |
| M5 Max 64 GB | 24.07 → 30.07 | 43.60 → 53.87 |
| M5 Max 128 GB | 24.10 → 28.88 | 43.40 → 52.34 |
| M5 Ultra 96 GB | 22.60 → 27.23 | 38.31 → 49.90 |
| M5 Ultra 256 GB | 21.99 → 26.58 | 36.80 → 48.27 |

M5 Max64 capacity changes882.63→837.65calls/day, local/hybrid conditional
sessions5.61/7.22 per8h, gain1.286, versus the published estimated hybrid gain1.16.
At s50 its R13 base/earlier-run/checkpoints-on owned-client costs are
$53.8706/$65.9422/$53.8839 per month. These sensitivities share measured client
rates, so “earlier run” isolates server timing rather than restoring the former
estimated M5. On the public s20 claim, the median-API advantage changes
2.8–4.6×→2.5–3.8× and the premium over cheapest API1.6–2.6×→1.9–2.9×.
Medium closed-perimeter ratios change2.4–3.9×→2.1–2.9×. Full-load GLM1M API
advantage changes5.4–6.0×→4.8–5.1×; cold1M GLM ingest plus transfer97.41→150.56s
(estimated pure server prefill43→96s). Integer fleet selections are recomputed,
not interpolated. The corrected M5 accounting sensitivity is tied to the same
base capacity as the ordinary candidate.

## Export and paper number inventory

The reproducible entry point is `calc/tests/r13_audit.py`. Twenty-four paper
scenarios generate **42 chart CSVs for each of three server cases** under
`calc/out/run13/{base,earlier-run,checkpoints-on}/`, with 8 manifest/schema/source/
alarm sets per case. Seven measurement CSVs have their own sidecars. Eight
current API scenario results, six complete payback-comparison CSVs and four derived
paper-figure CSVs are separate. There are 143 CSVs total; INDEX hashes 251 payloads.
`INDEX.json` hashes the complete export set and records generator identity.
No historical sidecar is rebound to the new generator.

The quote ledger deliberately includes every changed embedded-engine numeric
cell as supporting evidence, plus exact printed table cells/rows, figure inputs,
registered economics/million-token sentences and supplemental narrative keys.
Old printed values come from public main c04a99d/R11. It does not claim that
every supporting engine cell appears verbatim in the PDF. `kind`, `paper_site`,
`engine_key`, `old`, `new`, `unit`, `source` distinguish those scopes. Existing
reviewed `check_ranges.py` formulae supply the economics sentence definitions;
`r13_quotes.py` supplies explicit timing/server/client/geometry coordinates.

Affected published plots: **fig:payback**, both panels of **fig:teams**, and
**fig:million**. Affected printed numeric tables: **tab:turn**, **tab:oneshot**,
**tab:transcript**, **tab:offload**, **tab:clients**, **tab:arch**, **tab:econ**,
**tab:rentbuy**, **tab:perimeter**. The intensity caption/server bound changes;
its printed Qwen/Flash/GLM channel-only ratios are unchanged. The architecture
schematic, progress figure, owner-price/year bill, original M3 measurements,
memory-fit geometry and prototype correctness numbers are unchanged.

Affected prose/captions are located in00-abstract,01-introduction,04-channel,
05-clients,05b-models,06-server,07-economics,08-million,11-limitations and
14-conclusion. In addition to numbers, a later authorized prose run must update
the “only M3 measured” qualifications in abstract/client/transcript/limitations
text, without extending the M5 result to other configurations. No published
sentence has been silently rewritten in this run.

## Validation, review and bounds

The full engine suite passes **264 tests, exit0, 518.261s**, including all nine
legacy goldens and retained Run12 export-regeneration/byte-identity checks.
Focused R13 passes **17 tests, exit0**; the kit suite passes **24 tests, exit0**.
All 235 methods directly declared at Run12 remain present under their original
names (255 now, with inherited cases accounting for the larger executed count).
The validation host is Linux x86_64, Python3.14.4. Every Python gate below used
`PYTHONDONTWRITEBYTECODE=1` and an on-disk ext4 TMPDIR under
`.temp/hybrid-b-r32-261101/tmp`; no bytecode/native build is needed.

| Standalone command/check | Actual exit | Evidence under `.temp/hybrid-b-r32-261101/` |
| --- | ---: | --- |
| `python3 -m unittest discover -s calc/tests -v` | 0 | `unittest-full-03.log` |
| `python3 -m unittest discover -s calc/tests -p test_run13.py -v` | 0 | `focused-04.log` |
| `python3 -m unittest discover -s calc/tests -p test_r13_reverse.py -v` | 0 | `reverse-tests-final.log`, matching result JSON; six tests after independent fixture-data edit; `final-test-identity.json` binds unchanged implementation and fixture values |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `bench-tests-01.log` |
| `python3 calc/tests/r13_audit.py` | 0 | `publication-export-03.log` |
| `python3 calc/tests/r13_audit.py --quotes-only` after complete payback export support | 0 | `quotes-audit-04.log`;31774 ledger records |
| Complete current manifests, root INDEX, six full-sample accounting scopes, payback reconciliation, old bytes, unchanged TeX and Python3.9 grammar | 0 | `artifact-verification-04.log` |
| `python3 paper/data/check_ranges.py --self-test` | 0 | `paper-ranges-01.log`;152 site controls plus table/direction controls against preserved published data |
| `python3 paper/data/year_bill.py --self-test` | 0 | `year-bill-tests-01.log` |
| `python3 paper/data/offload_bound.py --self-test` | 0 | `offload-bound-tests-01.log` |
| `python3 -m unittest discover -s calc/tests -p test_run13.py -k accounting_child -v` | 0 | `child-regression-01.log` |
| `python3 calc/tests/r13_controls.py unmeasured_child` | **1, expected red** | `child-mutant-01.log`; named calibration AssertionError, no setup error |
| `python3 calc/tests/r12_controls.py old_mfu` | **1, expected red** | `old-mfu-control-01.log`; named measured-time AssertionError |
| Authored staged whitespace check with `core.whitespace=cr-at-eol` | 0 | `staged-authored-whitespace-01.log`; archived raw payloads excluded |
| Repository manifest verification | 0 | `manifest-check-01.log` |

The first full suite exited1 (262 tests, one error): the existing Run11 test
assumed every nonlegacy scenario had a workload. Its original method name and
assertions remain; its scope now explicitly excludes the new measurement-only
scenario. The second full run was stopped by its recorded PID (exit143) when
self-review found the accounting-child marker omission. No interrupted run is
reported green. After the propagation fix and named regression/control, final
exports and the complete third suite passed. An intermediate focused check
correctly rejected stale manifests after that source change; current manifests
are bound to the final engine. An early export was stopped during calibration
refinement; another completed the chart calculations but exited1 because the
quote reader still targeted the old `HERE/engine` layout. The final quote reader
uses an explicit new-table reader and passes. No failed/partial generation is
used as delivery evidence. One extended scratch-verification attempt exited1
with a missing ROOT import; a scratch inspect.py also shadowed the standard
library error hook. The import and scratch filename were corrected; the complete
artifact verifier then exited0 in artifact-verification-03.log.

The default whitespace check exits2 for the native CSV's preserved CRLF line
ending, and raw imported logs may contain original whitespace. These bytes are
retained to honor archive/CSV identity; the separate authored check treats CRLF
as an end-of-line convention and exits0. The tested engine/input identity and
retained test-name audit are recorded in `validation-final.json` and
`test-name-retention-01.json`; export drivers were also exercised directly after
the full table generation. Generator hashes in every current manifest and the
root INDEX match the delivered source; historical manifests keep their original
identities. No hosted status is synthesized or claimed.

No surface table or separate landing-gate property suite was supplied in the
brief; that is an explicit brief gap. Coverage below maps the actual requested
contracts. All historical test method names remain present. No requested input
or table is treated as silently out of contract. Deliberate exclusions follow
the brief: step57 swap rates, vLLM hybrid bridging, native builds/downloads and
published prose edits. Non-fitting configurations retain explicit alarm cells.

| Requirement | Named evidence |
| --- | --- |
| Verified imports and wrong-hash/manifest rejection | test_archive_goldens_and_manifest; test_wrong_hash_and_manifest_rejected |
| Base/reproduction/on/earlier fits | test_bulk_fit_goldens_and_recomputation; test_reproduction_within_one_percent; test_server_case_consumers |
| vLLM cold/cached/server-only | test_vllm_cold_fit_goldens; test_vllm_cached_recomputation_and_goldens; test_vllm_invalid_cached_rejected; test_new_manifests_and_server_only_flags |
| M5 depth/parallel/swap/physical bounds | test_client_depth_recomputation; test_client_consumers_and_bounds; test_swap_affected_rows_rejected; test_m5_hypothetical_rate_cannot_exceed_bandwidth |
| M5 accounting propagation | test_accounting_child_retains_measured_m5 |
| Sonnet and Gemma | test_sonnet_price_recomputation; test_gemma_geometry_recomputation |
| Old bytes, original tests and current exports | test_historical_exports_and_paper_text_unchanged; retained Run12 byte-identity tests; test_new_manifests_and_server_only_flags |

| Mutant | Narrows the gate to | Named failing test | Survivor bound |
| --- | --- | --- | --- |
| Omit measured-M5 marker from the accounting child | Actual sensitivity consumers must use the parent's measured client calibration | test_accounting_child_retains_measured_m5 | Killed, expected exit1; no survivor. This does not establish unmeasured device/precision equivalence. |
| Run12 old-MFU control | Actual server consumer must use the retained measured curve | test_measured_server_timing_replaces_mfu | Killed by the retained control test; bounds remain those of Run12. |

Self-review covered imported bytes, fit objectives and residuals, exact cached
work, measured anchors and interpolation, accounting-child propagation, physical
bounds, current/frozen price and geometry scopes, manifests, quote derivations
and the complete scoped diff. Independent review, hosted CI and landing are not
claimed. Local signed delivery is **ready for review**, under the explicit no-push
instruction. The addressed a2a summary records the delivered head separately.


## r13fix: review r5d rework (hybrid-e-r1-261101)

This rework continues `engine-r13` at reviewed producer head
`00ca9bd3df138186b61dafad996d062d9db0d6c3`. The complete Claude review,
including M1–M12 and the comment-only control, was read from
`/home/agent/Werkstatt/hybrid-review/paper/.temp/REVIEW-engine-r13-claude.md`.
The review requested changes to ledger coverage and tests; all of its independent
numeric recomputations matched. Engine implementation, inputs, original
archives, native architecture script/CSV and published TeX remain unchanged.

### F1: publication ledger coverage

The missing sentence at `paper/sections/05b-models.tex:54` is now recorded as
**19--22 → 19--21 seconds**. Its key names the three models and
`saving_1k_131k_300mbit_s:minmax(round0)`: the rounded range of
19.2/18.6/21.6 becomes that of 19.2/18.6/21.0.

`r13_ledger.py` independently compares old and new exported numeric cells,
recomputes the existing publication prose formulas against both snapshots,
and scans all **1409 numeric TeX tokens** under `paper/`, including scalar
values and ranges. Native architecture dependencies are discovered from changed
CSV columns and the precision printed at the site, without a sentence-site
list. Range endpoints select the old model rows; the same rows supply the new
range. Decimal KB/token is checked as bytes/token divided by 1000. The existing
publication formula guard scans every section for unregistered formula forms.
Equal-looking unrelated quantities have exact, reasoned lexical collision
entries; an unused entry fails. No whole file or section is exempted.

The checker requires exact site/kind/key/old/new ledger records for **31781
changed dependencies**. The original **31774 rows** remain in their original
order and content. Seven discovered native printed-number records are appended:
the missing range and six scalar occurrences in tab:arch and the delta prose.
These include the actual printed **21.8 → 43.5 KB/token**, resolving review N7's
byte-versus-printed-form ambiguity. The scalar records repeat existing raw-key
coverage intentionally, at exact source-line and printed precision.

`test_paper_ledger_omission_controls` removes the range, a changed exported cell
and a scalar ledger record separately; each fails the coverage checker. Copying
the range or the Gemma delta scalar into another unregistered paper site also
fails. A nearby unchanged range needs no ledger record; changing only its new
CSV endpoint recomputes a different required replacement. This checks behavior,
not a ledger count/hash. Bounds: the catalog defines nontrivial prose arithmetic;
a new arithmetic/rounding convention needs a catalog formula. Numeric scanning
does not infer arbitrary natural-language dependencies or validate new prose.

### F2–F4: production consumers and custody

The original direct `no_swap()` test is retained. New tests repack the real M5
archive, recompute its manifest and outer hash, write identical imported payloads
in a temporary root, and drive the real `package()` and `MeasuredM5()` paths.
The real archive is a positive control: step57 has 5095754301 bytes of swap, but
the consumer's exact depth, parallel and scaling records equal only steps40/50/55
and yield positive rates. Separately adding swap to each admitted phase causes
the production consumer to refuse construction with that phase's `swap-affected`
InputGap. No test substitutes a direct helper call for consumer admission.

Custody plants use repacked copies of the real off archive and correct outer
hashes. They require the specific refusal for `../`, absolute paths, symlinks,
hardlinks, duplicate members and unmanifested payloads. A valid repack is
accepted. Unsafe AppleDouble-named paths are also planted: deleting the path
guard then actually admits them, so a later unmanifested-file refusal cannot
mask the missing guard. All refusals leave only the input archive on disk;
no tar member is extracted. No production custody behavior is changed.

`test_live_architecture_generator_matches_csv` copies the actual live
`paper/data/arch_compare.py` into an isolated temporary directory, executes it
with the current Python, and compares every output CSV byte with the checked-in
CSV. It does not execute the historical fixture script. Reverting Gemma's
separate K/V geometry now fails this behavioral test.

### Mutant evidence

`r13fix_controls.py` compiles bounded mutations of the actual production
functions and executes the named tests; it never edits production files or
runs the generator-hash assertion. Every plant is required to apply exactly
once. Native-script M8 changes only the source bytes copied into the test's
isolated execution directory. Logs are under `.temp/hybrid-e-r1-261101/`.

| Mutant | What it narrows the gate to | Named failing test | Actual exit / survivor bound |
| --- | --- | --- | --- |
| M3 / M12: delete consumer swap guard | Swap in each admitted archive phase prevents a machine-speed consumer | `test_measured_m5_rejects_swap_in_admitted_archive_phases` | 1; killed for phases40/50/55 |
| M9: guard only step40 | Parallel and scaling admission must also inspect their own swap telemetry | `test_measured_m5_rejects_swap_in_admitted_archive_phases` | 1; killed for phases50/55 |
| M5: delete unsafe path predicates | Unsafe archive paths refuse before metadata exemptions; AppleDouble paths otherwise become admitted | `test_archive_custody_refusals` | 1; killed, including two `InputGap not raised` witnesses |
| M6: delete unmanifested check | An unmanifested payload prevents archive admission | `test_archive_custody_refusals` | 1; killed |
| Delete link guard | Both symlink and hardlink members prevent archive admission | `test_archive_custody_refusals` | 1; killed |
| Delete duplicate guard | Even identical repeated members prevent archive admission | `test_archive_custody_refusals` | 1; killed |
| M8 / M11: revert Gemma in live generator | Script output and checked-in CSV agree byte for byte | `test_live_architecture_generator_matches_csv` | 1; killed |
| M10: comment-only control | Behavioral checks do not reject source-byte changes without changed behavior | No failing behavioral test; `test_measured_m5_rejects_swap_in_admitted_archive_phases` stays green | 0; intentional survivor, limited to behavior-neutral comments |

Logs: `mutant-{M3,M9,M5,M6,M8,link,duplicate,M10}-02.log`; the aggregate
`mutants-02.json` records every real process exit. The no-error expected-red
faults exit1, rather than a setup error or the generator-hash failure. Review
M1/M2/M4/M7 were already behaviorally killed at the unchanged producer engine;
this rework targets the reported survivors. M11 and M12 are the review's
full-suite aliases of M8 and M3, not distinct faults.

### r13fix validation and preservation

The full engine suite passes **270 tests, exit0, 533.167s**; the kit suite passes
**24 tests, exit0, 25.253s**. All23 R13 tests pass within the complete engine
run. The pre-existing
17 R13 test methods remain under their original names; six named regression
tests are added. The rework has no supplied surface table or separate landing
property suite (the original brief gap remains explicit). No requested finding
is treated as out of contract. Production engine/input identity and all export
bytes are preserved; the only generated artifact change is the intended ledger
append. README documents the two new audit/control entry points, and the root
manifest is refreshed for the reviewed task scope. Those documentation/manifest
paths are the only changes outside `calc/`.


Engine, kit, ledger, artifact and mutant commands used
`PYTHONDONTWRITEBYTECODE=1` and on-disk
`TMPDIR="$PWD/.temp/hybrid-e-r1-261101/tmp"`, on Linux x86_64 / Python3.14.4.
No GPU, download, native build, PDF rendering or push was performed.

| Standalone command/check | Actual exit | Evidence under `.temp/hybrid-e-r1-261101/` |
| --- | ---: | --- |
| `python3 -m unittest discover -s calc/tests -v` | 0 | `engine-suite-02.log`;270 tests |
| `python3 -m unittest discover -s calc/tests -p test_r13_reverse.py -v` | 0 | `reverse-tests-final.log`, matching result JSON; six tests after independent fixture-data edit; `final-test-identity.json` binds unchanged implementation and fixture values |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `kit-suite-01.log`;24 tests |
| `python3 calc/tests/r13_audit.py --quotes-only` | 0 | `quotes-audit-02.log`;31781 rows |
| `python3 calc/tests/r13_ledger.py` | 0 | `ledger-coverage-01.log`;1409 scanned TeX numbers,31781 dependencies |
| `python3 .temp/hybrid-e-r1-261101/verify_artifacts.py` | 0 | `artifact-verification-02.log` and `.json` |
| `git diff --exit-code 00ca9bd3 -- calc/out/paper calc/out/run13 calc/hybridcalc paper` | 0 | `unchanged-exports-engine-paper-01.log` |
| Each `python3 calc/tests/r13fix_controls.py MUTANT` | **1, expected red**, except M10 **0** | Per-mutant `*-02.log` and `mutants-02.json`; named assertion failures, no setup errors |

Artifact verification compares every file and file-set membership against the
reviewed head: **150 historical + 252 run13 files remain byte-identical**.
All25 run13 manifests retain the current unchanged engine generator identity
and correct payload hashes. The root INDEX still names exactly251 payloads;
its own bytes are preserved too. The old ledger is an exact byte prefix, with
only the seven intended rows appended. Python3.9 grammar accepts all four
changed/added Python files. Final test edits preceded the full-suite launch. Source/test/config identity
was snapshotted during that run and verified unchanged afterwards. Full engine regeneration was
not repeated: engine, inputs and all252 current exports are unchanged; the
quote driver regenerated only its derived audit/ledger outputs, preserving all
export bytes and the original INDEX.

Initial focused checks exited1 while refining the new checker: the first
mistook an equal-looking table value for an unregistered prose dependency; the
existing publication guard now resolves its own table/quantity collisions. A
second had an arbitrary numeric-token count assertion, replaced by an actual
known-site assertion. Focused run03 passed23 tests before final scalar/path
controls were added. Full engine run01 was deliberately stopped by its recorded
PID, exit143, to add the unsafe AppleDouble acceptance witnesses. It is not
passing evidence. Full run02 exercises the final tests and is green. Reused
`check_ranges.py` emits ResourceWarning for its existing unclosed read; no test
failure is suppressed.

Disk sampling and the task scratch footprint are recorded in
`disk-watch-01.log`. Samples are in bytes to avoid unit ambiguity: the supplied
28 GB floor is 28000000000 bytes. The monitor captured a transient breach of the28 GB floor;
the exact minimum is reported below. No claim of a passing disk-floor gate
is made.
No other session's files or processes were removed to reclaim disk space.
Final sampled minimum and local delivery evidence are recorded below.

Minimum sampled free space was **27059757056 bytes (27.060 GB;
25.201 GiB)** at 2026-11-01T20:49:37.242152+00:00, over 92 five-second samples.
The requested28 GB floor **was not maintained** across all samples. The
post-suite spot check was 30993956864 bytes (30.994 GB). Task scratch
occupied 251635 bytes at this summary; no attribution to another process is
claimed. The resource assertion `minimum > 28000000000` exited1; it is a
failed control, not passing validation. No other session's data or processes
were touched. No further full generation or heavy validation is needed.

Self-review covers the complete rework diff, changed-key and printed-form
ledger completeness, consumer-level refusal behavior, every mutant verdict,
original test retention and all402 preserved export files. Root-manifest and
staged-whitespace command logs are `manifest-check-*.log` and
`staged-whitespace-*.log` in the same scratch directory. The local signed
rework is ready for review with the resource exception above, and no push;
its head and addressed Matrix receipt are recorded separately in the task
notes and requested handoff.


## r2: reverse quote ledger guard (hybrid-e-r2-261101)

This revision continues `engine-r13` from signed r1 head `bc15b96f`, after
Claude re-review r5e requested changes. The review and its `.temp/r13e/`
evidence were read at
`/home/agent/Werkstatt/hybrid-review/paper/.temp/REVIEW-engine-r13-rework-claude.md`.
The orchestrator is the writer and lane owner; the numeric scope below is its
explicit instruction, also recorded in `calc/tests/r13_reverse.py`. F2–F4
production code, source inputs, archives and printed TeX are unchanged.

### Writer-owned scope and independent reverse check

In scope: decimal points and decimal commas; thin/narrow spaces, commas,
`{,}` and `\,` as thousands separators; ranges with `--`, `–` and `-`;
percentages and currency signs `$`/`₽`; signs compared as written (a sign flip
is a change, including a rounded negative zero); byte values in B, KB, MB, GB,
KiB, MiB and GiB, converted before comparison at the printed precision, with
or without spacing before the unit; prose rounded to its printed significant
digits. Ambiguous comma groupings and integer trailing-zero precision are
checked conservatively in both interpretations. The Cyrillic byte-unit
spellings used by the paper are included.

The guard scans **every `.tex` file recursively under `paper/`**, including
captions, macros, comments and layout constants. The current tokenizer finds
**1435 numeric tokens**. It compares them with **177754 changed
numeric export keys**, rather than only the native architecture CSV or the
hand-kept quote sites. Every numeric column of all 42 charts, both policies,
and each R13 server case is compared with both references retained by R12:
its unchanged design tables and its measured-server sensitivity. The derived
paper CSVs, all payback columns and numeric JSON leaves are included. Removed
numeric keys are changes too: the old long-form payback `delta` column is
inventoried as removed, and acquisition/residual inputs for the normalized
payback columns come from the exact R12 engine, not copied R13 inputs. The eight
old API results are recomputed from exact local R12 source/inputs at
`7c2e9b1e8e87835f474ae45a4454bda74f4af6d3`, using the unchanged local measurement
files; this needs no download or build. The inventory records **1620 export
comparisons/accounting entries**, including the 11 new-only measurement files
and new INDEX, which have no pre-R13 value. New-only is recorded explicitly,
not treated as an unchanged pair. Existing prose formulas add arithmetic
results independently of the ledger's presence. Cached raw pairs are copied
before formula expansion, so repeated checks cannot mutate the raw inventory.

An occurrence of any changed old value must have an exact `(file:line, old
numeric token)` ledger coordinate or an exact `(file, line, token, reason)`
waiver. No token, section or file receives a blanket waiver. The guard compares
both old and new at the site's precision; a source change that rounds to the
same printed value needs no replacement. A sign is never discarded to make a
match. Byte conversion uses source-schema units and decimal/binary scale factors.
The independent inventory does not disappear when a ledger row is removed.

Numeric matching establishes possible dependency, not the meaning of a prose
sentence. **891 new exact collision waivers** in
`calc/tests/data/r13_numeric_waivers.csv`, plus the **13 retained native
waivers**, record unchanged inputs, independent observations and layout
constants. Each has a one-line reason. A moved/deleted new waiver fails closed;
the native checker separately validates its retained waiver sites using its
historical tokenizer. This distinction preserves the original signed-coordinate
collision rather than treating a negative TikZ coordinate as a positive value.
The r1 sentence about 1409 tokens described comparison with native architecture
values; this r2 inventory and guard replace that narrower coverage claim.

Numbers written as words are **out of the automated numeric guard's scope by
the writer's decision**. The complete lexical sweep below contains **406
occurrences at 279 file/line sites**, including scale words, fractions,
ordinals and ambiguous singular uses. Checkboxes are intentionally open for the
writer. The automated tests do not claim these words have been reconciled.

### Ledger additions and discovered changes

The **31781 reviewed r1 rows remain an exact byte prefix**. This revision appends
**261 rows**: two additional traffic-formula records and **259 exact printed
coordinates. The ledger now contains **32042 rows**. Table/paragraph labels
remain as supporting source bindings; the new exact rows give the writer the
actual printed token and replacement at each source line. Repeated equal tokens
on a line retain their distinct source-key records in the CSV; the table below
groups identical old/new pairs for readability.

The reverse sweep exposed additional work-list detail, including the repeated 50-person rent/buy prices at `07-economics.tex:200–201`,
M5 transcript
local/total times at `04-channel.tex:78`, the copied full-load GLM ranges at
`08-million.tex:70–71`, the rounded 24-hour capacity at
`11-limitations.tex:7`, and traffic at `04-channel.tex:127`. In that traffic
paragraph, the same capacity-limited M3 user's compute plus hosting changes
14.815693 → 20.864249 USD/month, printed **15 → 21**. Cloud egress at the two
tariffs changes 84.389533/151.901159 → 83.762966/150.773339, printed
**84/152 → 84/151**. Their ratio to compute plus hosting becomes **6--10 → 4--7**.
These two arithmetic bindings are the new supporting formula rows.

The prose latency range at `07-economics.tex:235` also needs explicit endpoints: **0.8 → 1.7** and **1.9 → 2.7 seconds**. Its printed lower bound 0.8 was already stale against the R12 selected-hybrid source range 1.5--1.9; the existing supporting row records that source range, while the new exact rows preserve what the paper actually says. The repeated rental/purchase figures become **24 → 33** and **25 → 35 USD/person-month**, respectively.

Published old cells are read as printed. The historical one-shot 100-Mbit/s
cell says 5.0 minutes although its old raw export rounds 4.949720 to 4.9 at one
decimal; R13 rounds to the already printed 5.0, so no replacement is invented.
The cell binding permits one printed rounding unit of historical discrepancy
and computes the replacement from the exact new source. Other unchanged
roundings, including Gemma's prose 30 seconds, remain explicit collisions.

| Exact printed site | Newly recorded old → new |
| --- | --- |
| `paper/sections/00-abstract.tex:9` | `2.8--4.6 → 2.5--3.8` |
| `paper/sections/00-abstract.tex:10` | `1.6--2.6 → 1.9--2.9` |
| `paper/sections/01-introduction.tex:12` | `30 → 14.1--21.1` |
| `paper/sections/04-channel.tex:12` | `42 → 43`; `5 → 6` |
| `paper/sections/04-channel.tex:26` | `18 → 19`; `6.4 → 6.5`; `6.7 → 6.6`; `2.2 → 2.3`; `20 → 19`; `0.5 → 0.6`; `81 → 66` |
| `paper/sections/04-channel.tex:27` | `41 → 42`; `5.3 → 5.2`; `14 → 15`; `5.0 → 5.6`; `44 → 39`; `1.3 → 1.9`; `164 → 113` |
| `paper/sections/04-channel.tex:28` | `6.5 → 6.7`; `2.3 → 2.5`; `34 → 31`; `0.7 → 0.9`; `115 → 88` |
| `paper/sections/04-channel.tex:29` | `42 → 43`; `9.6 → 9.3`; `15 → 16`; `27 → 25`; `5.3 → 6.4`; `75 → 62`; `1.7 → 2.8`; `233 → 144` |
| `paper/sections/04-channel.tex:37` | `71 → 83`; `14 → 25` |
| `paper/sections/04-channel.tex:49` | `1.7 → 1.8`; `35 → 38`; `8.6 → 12.0` |
| `paper/sections/04-channel.tex:50` | `9.7 → 9.9`; `3.4 → 3.6`; `71 → 83`; `20 → 31` |
| `paper/sections/04-channel.tex:51` | `12.7 → 13.0`; `4.5 → 4.8`; `95 → 114`; `28 → 47` |
| `paper/sections/04-channel.tex:58` | `24 → 26`; `6.7 → 6.8` |
| `paper/sections/04-channel.tex:67` | `3.5 → 5.4` |
| `paper/sections/04-channel.tex:77` | `24 → 26`; `6.7 → 6.8` |
| `paper/sections/04-channel.tex:78` | `2.7 → 4.4`; `24 → 26`; `6.8 → 7.5`; `5.9 → 4.9`; `4.5 → 3.5` |
| `paper/sections/04-channel.tex:79` | `25 → 27`; `18.3 → 18.4`; `16.9 → 17.0` |
| `paper/sections/04-channel.tex:99` | `29.6 → 29.4`; `45.6 → 45.2`; `60.8 → 60.2`; `68.7 → 67.8` |
| `paper/sections/04-channel.tex:100` | `19.3 → 19.2`; `24.2 → 24.1`; `26.5 → 26.3`; `27.1 → 27.0` |
| `paper/sections/04-channel.tex:101` | `38.7 → 38.3`; `55.0 → 54.6`; `67.0 → 66.1`; `72.3 → 71.2` |
| `paper/sections/04-channel.tex:102` | `21.5 → 21.3`; `25.3 → 25.2`; `26.9 → 26.8`; `27.3 → 27.2` |
| `paper/sections/04-channel.tex:127` | `15 → 21`; `6--10 → 4--7`; `152 → 151` |
| `paper/sections/05-clients.tex:75` | `11--17 → 10--29` |
| `paper/sections/05-clients.tex:93` | `1.58 → 1.57` |
| `paper/sections/05-clients.tex:95` | `13.0 → 18.3`; `6.58 → 5.61`; `7.61 → 7.22`; `1.16 → 1.29` |
| `paper/sections/05-clients.tex:96` | `8.06 → 8.05` |
| `paper/sections/05-clients.tex:97` | `15.34 → 15.31` |
| `paper/sections/05-clients.tex:98` | `15.64 → 15.60`; `1.11 → 1.10` |
| `paper/sections/05-clients.tex:99` | `3.44 → 3.43` |
| `paper/sections/05b-models.tex:70` | `3.4 → 3.0` |
| `paper/sections/05b-models.tex:71` | `22.5 → 12.1`; `14 → 9` |
| `paper/sections/05b-models.tex:85` | `1.35 → 0.72`; `30 → 14.1--21.1` |
| `paper/sections/06-server.tex:6` | `9 → 5`; `1.22 → 1.30`; `0.09 → 0.17`; `0.13 → 0.26` |
| `paper/sections/06-server.tex:9` | `0.05 → 0.06` |
| `paper/sections/06-server.tex:26` | `64 → 33`; `25 → 13`; `12 → 6` |
| `paper/sections/06-server.tex:27` | `221 → 127`; `88 → 50`; `44 → 25` |
| `paper/sections/06-server.tex:28` | `69 → 35`; `27 → 14`; `13 → 7`; `308 → 157`; `123 → 63`; `61 → 31` |
| `paper/sections/06-server.tex:29` | `57 → 31`; `22 → 12`; `11 → 6`; `159 → 106`; `63 → 42`; `31 → 21` |
| `paper/sections/07-economics.tex:11` | `883 → 838`; `637 → 605` |
| `paper/sections/07-economics.tex:12` | `49 → 57` |
| `paper/sections/07-economics.tex:13` | `1.5 → 1.9` |
| `paper/sections/07-economics.tex:18` | `0.23--0.33 → 0.29--0.38` |
| `paper/sections/07-economics.tex:55` | `6.5 → 6.9` |
| `paper/sections/07-economics.tex:56` | `5.1 → 10.0` |
| `paper/sections/07-economics.tex:60` | `22--27 → 27--32`; `1.6--1.9 → 1.9--2.3` |
| `paper/sections/07-economics.tex:61` | `3.7--4.6 → 3.2--3.8` |
| `paper/sections/07-economics.tex:62` | `2.8--3.1 → 2.5--2.7`; `2.3--2.6 → 2.7--2.9` |
| `paper/sections/07-economics.tex:65` | `880 → 840` |
| `paper/sections/07-economics.tex:66` | `43--49 → 52--55`; `23--38 → 49--55` |
| `paper/sections/07-economics.tex:67` | `5.2--5.9 → 4.6--4.9` |
| `paper/sections/07-economics.tex:69` | `1.6--2.6 → 1.5--2.4` |
| `paper/sections/07-economics.tex:70` | `37--38 → 48--50`; `53--54 → 66--67`; `4--9 → 37--42` |
| `paper/sections/07-economics.tex:86` | `27.3 → 32.1`; `48.6 → 54.6`; `96.1 → 102.1` |
| `paper/sections/07-economics.tex:87` | `25.8 → 30.7`; `46.7 → 54.7`; `94.1 → 102.1` |
| `paper/sections/07-economics.tex:88` | `883 → 838`; `24.1 → 30.1`; `43.6 → 53.9`; `78.8 → 89.1` |
| `paper/sections/07-economics.tex:89` | `935 → 934`; `24.1 → 28.9`; `43.4 → 52.3`; `100.3 → 109.2` |
| `paper/sections/07-economics.tex:90` | `1\,780 → 1\,776`; `22.6 → 27.2`; `38.3 → 49.9`; `112.8 → 124.4` |
| `paper/sections/07-economics.tex:91` | `1\,814 → 1\,810`; `22.0 → 26.6`; `36.8 → 48.3`; `183.0 → 194.5` |
| `paper/sections/07-economics.tex:105` | `79 → 89` |
| `paper/sections/07-economics.tex:106` | `59 → 65` |
| `paper/sections/07-economics.tex:108` | `12 → 13` |
| `paper/sections/07-economics.tex:109` | `24 → 25`; `34 → 36`; `66 → 71` |
| `paper/sections/07-economics.tex:110` | `18 → 21`; `35 → 40` |
| `paper/sections/07-economics.tex:115` | `44 → 54` |
| `paper/sections/07-economics.tex:137` | `18 → 21`; `35 → 40` |
| `paper/sections/07-economics.tex:138` | `8--10 → 16--19` |
| `paper/sections/07-economics.tex:145` | `67 → 101`; `169 → 202` |
| `paper/sections/07-economics.tex:153` | `36--443 → 63--506` |
| `paper/sections/07-economics.tex:200` | `24 → 33` |
| `paper/sections/07-economics.tex:201` | `25 → 35` |
| `paper/sections/07-economics.tex:221` | `24 → 33`; `2 → 3`; `43 → 62`; `34 → 48`; `25 → 35` |
| `paper/sections/07-economics.tex:222` | `31 → 53`; `1 → 2`; `28 → 47`; `23 → 38`; `19 → 29` |
| `paper/sections/07-economics.tex:233` | `5 → 19` |
| `paper/sections/07-economics.tex:234` | `6.5 → 11.4` |
| `paper/sections/07-economics.tex:235` | `2.9--3.9 → 2.6--2.9`; `0.8 → 1.7`; `1.9 → 2.7` |
| `paper/sections/07-economics.tex:236` | `2.4--3.2 → 2.1--2.5` |
| `paper/sections/07-economics.tex:237` | `30--39 → 27--39`; `4--22 → 3--22` |
| `paper/sections/07-economics.tex:242` | `17 → 22`; `27 → 29`; `35 → 38` |
| `paper/sections/07-economics.tex:245` | `6--26 → 22--24`; `4--24 → 18--22` |
| `paper/sections/07-economics.tex:264` | `27 → 30`; `19 → 22`; `26 → 29` |
| `paper/sections/07-economics.tex:265` | `145 → 152`; `37 → 55`; `45 → 63`; `95 → 81` |
| `paper/sections/07-economics.tex:266` | `95 → 81` |
| `paper/sections/07-economics.tex:267` | `104 → 111`; `29 → 42`; `43 → 53`; `95 → 81` |
| `paper/sections/07-economics.tex:268` | `337 → 455`; `316 → 349`; `323 → 356`; `31 → 26` |
| `paper/sections/07-economics.tex:269` | `337 → 371`; `248 → 282`; `255 → 289`; `31 → 26` |
| `paper/sections/07-economics.tex:270` | `320 → 344`; `238 → 268`; `252 → 282`; `31 → 26` |
| `paper/sections/07-economics.tex:315` | `2.8--4.2 → 2.5--3.5` |
| `paper/sections/07-economics.tex:316` | `4.7--6.9 → 3.8--5.3` |
| `paper/sections/07-economics.tex:317` | `5.2--5.9 → 4.6--4.9` |
| `paper/sections/07-economics.tex:320` | `2.4--3.9 → 2.1--2.9` |
| `paper/sections/07-economics.tex:321` | `6--26 → 22--24`; `4--24 → 18--22` |
| `paper/sections/08-million.tex:13` | `97 → 151`; `43 → 96` |
| `paper/sections/08-million.tex:32` | `4.2--4.6 → 4.4--4.6`; `3.21 → 4.01` |
| `paper/sections/08-million.tex:39` | `1.04 → 1.05` |
| `paper/sections/08-million.tex:40` | `1.5--1.7 → 1.8--1.9`; `5.4--6.0 → 4.8--5.1`; `2.0--2.1 → 1.9--1.9` |
| `paper/sections/08-million.tex:41` | `2.3--2.4 → 2.5--2.8`; `1.4 → 1.3` |
| `paper/sections/08-million.tex:42` | `2.4--2.9 → 2.6--2.9` |
| `paper/sections/08-million.tex:70` | `2.0--2.1 → 1.9--1.9`; `1.4 → 1.3` |
| `paper/sections/08-million.tex:71` | `5.4--6.0 → 4.8--5.1`; `29--44 → 15--30`; `2.5--2.9 → 1.9--2.4` |
| `paper/sections/11-limitations.tex:7` | `2\,650 → 2510`; `880 → 840` |
| `paper/sections/14-conclusion.tex:11` | `11--17 → 10--29` |
| `paper/sections/14-conclusion.tex:14` | `2.8--4.6 → 2.5--3.8` |
| `paper/sections/14-conclusion.tex:15` | `1.6--2.6 → 1.9--2.9` |
| `paper/sections/14-conclusion.tex:16` | `5.4--6.0 → 4.8--5.1` |
| `paper/sections/14-conclusion.tex:17` | `2.0--2.1 → 1.9--1.9` |
| `paper/sections/14-conclusion.tex:19` | `2.4--3.9 → 2.1--2.9` |

### Named regressions, controls and validation

`test_reverse_guard_rejects_copied_non_arch_changed_values` plants the reviewer's
883, `\$24.1`, “около 880”, 1.16, 221, `11--17\%`, `30\%` and 22.5 separately
at a fresh TeX coordinate, through `check_ledger(texts=...)`. Each must produce
the named unregistered-value assertion; an unchanged text control passes.
`test_paper_ledger_waivers_are_site_bound` plants 21.6 at another coordinate and
also exercises `native_changes` directly, so a later guard cannot mask a widened
native waiver. A second plant copies 11.5 from the new exact-waiver file. `test_writer_numeric_scope_and_unchanged_controls` uses independent
old/new fixtures for every declared lexical form and all byte units, including
attached units, unchanged rounded controls and sign flips. The exact printed-site
omission test removes the M5 transcript's 2.7-minute coordinate. The inventory
and manual-word tests cover the other declared contracts. All 270 prior engine
cases and all 24 kit cases remain present; six named engine tests are added.

| Mutant | What it narrows the gate to | Named failing test | Survivor bound |
| --- | --- | --- | --- |
| `arch_only` | Only architecture values reach the new reverse guard | `test_reverse_guard_rejects_copied_non_arch_changed_values`, all eight plant subtests (including 883) | Killed, expected exit 1; no survivor |
| `token_waiver` (review L3) | Native collision waivers apply to a token at any site | `test_paper_ledger_waivers_are_site_bound` | Killed, expected exit 1; no survivor |
| Comment-only control | Unmodified behavior | Same site-bound waiver test remains green | Exit 0 is intentional; source-function fault controls prove behavior, not generator hashing |

The control harness compiles the actual source functions with the single
narrowing edit in memory and drives the named test. It does not edit production
files, synthesize hosted checks or rely on a source hash for the verdict.

Validation host: agents1 Linux x86_64, Python 3.14.4, CPU only. Every engine, kit, quote and fault-control Python gate
uses `PYTHONDONTWRITEBYTECODE=1` and on-disk
`TMPDIR=.temp/hybrid-e-r2-261101/tmp`. No GPU, downloads, native builds or paper
rendering. One scratch import probe omitted the bytecode flag and created seven
ignored cache files (115320 bytes); those exact task-owned files were removed,
with paths/times retained in `bytecode-probe-cleanup.json`. All engine/kit/quote/control gates
used the required flag. Readiness and all standalone gate logs are under
`.temp/hybrid-e-r2-261101/`; durable `*.result.json` files record the actual
command, PID, times and exit code. The existing `.temp/tasks.md` is the tracker;
`task-board goal get` reported no board, so no parallel board was created.

<!-- r2-validation-results -->
The complete engine suite is **276 tests, OK, exit 0**, including the 270
retained cases and six new regressions. Its unittest time is **532.968 s**.
After that full run, the byte-unit fixture data in one new test was made
independent of the implementation registry, using literal physical scales.
This changes no production source or executed fixture values. All six new
tests were then rerun on the final test file (`reverse-tests-final.log`, exit 0);
the 270 original tests and their inputs are unchanged.
The kit suite is **24 tests, OK, exit 0**. The standalone ledger reports 32042
required dependencies and 1207 reverse occurrences, all accounted for. Artifact
verification confirms all 150 historical and 252 R13 export bytes, and the
31781-row ledger byte prefix. All 261 originally declared test names remain.

| Standalone command / gate | Actual exit | Evidence under `.temp/hybrid-e-r2-261101/` |
| --- | ---: | --- |
| `python3 -m unittest discover -s calc/tests -v` | 0 | `engine-suite-08.log`, `engine-suite-08.result.json`; 276 tests |
| `python3 -m unittest discover -s calc/tests -p test_r13_reverse.py -v` | 0 | `reverse-tests-final.log`, matching result JSON; six tests after independent fixture-data edit; `final-test-identity.json` binds unchanged implementation and fixture values |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `kit-suite-01.log`, `kit-suite-01.result.json`; 24 tests; kit source unchanged throughout this rework |
| `python3 calc/tests/r13_ledger.py` | 0 | `ledger-07.log`, `ledger-07.result.json` |
| `python3 calc/tests/r13_reverse.py --inventory .temp/hybrid-e-r2-261101/export-inventory-final.json` | 0 | `inventory-05.log`, `inventory-05.result.json`; 177754 changed keys, 1620 comparisons/accounting entries, 406 manual words |
| `python3 calc/tests/r13_audit.py --quotes-only` | 0 | `quotes-audit-05.log`; 32042 ledger rows; byte preservation verified separately |
| `python3 calc/tests/r13reverse_controls.py arch_only` | **1, expected red** | `mutant-arch-only-06.log`, matching result JSON; eight named plant failures |
| `python3 calc/tests/r13reverse_controls.py token_waiver` | **1, expected red** | `mutant-token-waiver-05.log`, matching result JSON; named waiver failure |
| `python3 calc/tests/r13reverse_controls.py comment` | 0 | `comment-control-05.log`, matching result JSON |
| Exact export-byte/prefix audit and Python 3.9 syntax parse | 0 | `artifact-verification-04.log`, `artifact-verification.json`; runtime validation is Python 3.14 |
| Original test-name retention | 0 | `test-retention.json`; 261 names, none missing |
| Signed delivery / authored whitespace / repository manifest | 0 | `signing-final-01.log`, `staged-whitespace-final.log`, `manifest-check-final.log` |
| Required >28 GB disk floor | **1, failed** | `disk-floor-01.log`, `resource-exception-final.json`; observed minimum 27747139584 bytes |

The disk floor was **not maintained**: the one-second monitor sampled
**27747139584 bytes (27.747140 GB)** free after task-owned validation had stopped.
The monitor first stopped this task's processes above the floor; it cannot
reserve shared free space. No cause is attributed to another actor, and no
foreign files/processes were deleted/stopped. Space later recovered above 36 GB
and the complete engine run resumed. The minimum is a sampled observation,
not a claim of continuous visibility between samples. This incident remains
an explicit resource exception; recovery does not turn the failed gate green.
<!-- /r2-validation-results -->

Early evidence is not promoted to green: the first quote-audit attempt exited 1
because its in-memory records contained numeric floats rather than the strings
read from CSV; the site renderer now normalizes both representations. Early
focused execution exposed unclosed readers in the new code; those readers were
closed. The first exact-R12 acquisition-input probe used the numeric accessor
for a text label and exited 1 (`ledger-05.log`); it now uses `locate` for that
label. Inventorying removed payback keys exposed four additional unchanged
11.5 collisions, now separately waived at the font/M3/M4 sites. The unchanged paper formula helper still emits its pre-existing
`ResourceWarning`. Engine-suite attempts 01–03, 05 and 07 were stopped by their recorded
own PIDs (signal 15) as source review corrected cached-inventory mutation,
manual-word false matches, attached/leading-fraction byte-unit coverage, and
removed payback keys/acquisition-input bindings in the complete export inventory.
Attempts 04 and 06 were stopped by the task-owned disk headroom guard. The first
stop was at 28,158,042,112 bytes free, above the 28 GB floor. Subsequent samples
fell below 28 GB after task-owned validation had stopped. This is an explicit
resource exception, not a passing floor gate; exact minimum and failure evidence
are recorded with the final validation results. No other session process or file
was touched. They are partial,
not passing suite evidence. The complete run is recorded above separately.

No surface table or separate landing-property suite was supplied (retained brief
gap). The exact requested contracts are mapped to the named tests above. There
are no silently excluded numeric forms; only number-words are manual under the
explicit scope clause. Existing reviewer tests retain their original names.
Self-review covers the complete scoped diff, exact source bindings, static
waivers, old-byte preservation and controls. Independent acceptance, hosted CI,
push and landing are not claimed; the owner's instruction is local signed
commits only. Code and tests are **ready for review**. The disk-floor failure remains a
declared resource exception and is not claimed as satisfied.

### Manual writer checklist: every number-word found under paper/

Each item lists occurrences in source order on that line. Scale words and their
`тыс.` abbreviation, references containing an English scale word, fractions,
ordinals and ambiguous singular uses are retained for manual adjudication.
The writer must decide which denote a changing engine result; none is waived
by the automated guard. A second vocabulary sweep checked numeral roots and
inflections against the corpus to retain such forms as «Четвёртый», «одном»
and «триллион» without treating «сотрудник» or «одинаковых» as numerals.

- [ ] `paper/hybrid-inference.ru.tex:46`: «million».
- [ ] `paper/sections/00-abstract.tex:2`: «тысячи», «одному».
- [ ] `paper/sections/00-abstract.tex:3`: «сотни», «тысяч».
- [ ] `paper/sections/00-abstract.tex:4`: «тысяч», «тысяч».
- [ ] `paper/sections/00-abstract.tex:5`: «четырёх», «шести».
- [ ] `paper/sections/00-abstract.tex:8`: «миллиона».
- [ ] `paper/sections/01-introduction.tex:7`: «сотни», «тысяч».
- [ ] `paper/sections/01-introduction.tex:9`: «тысячи».
- [ ] `paper/sections/01-introduction.tex:10`: «тысяч», «четырёх», «шести».
- [ ] `paper/sections/01-introduction.tex:12`: «одна».
- [ ] `paper/sections/01-introduction.tex:14`: «тысячи», «тысячи».
- [ ] `paper/sections/01-introduction.tex:15`: «миллион».
- [ ] `paper/sections/01-introduction.tex:16`: «миллион», «миллион».
- [ ] `paper/sections/01-introduction.tex:20`: «две».
- [ ] `paper/sections/01-introduction.tex:21`: «Третью».
- [ ] `paper/sections/01-introduction.tex:29`: «четыре», «тысячи», «один».
- [ ] `paper/sections/01-introduction.tex:35`: «миллион».
- [ ] `paper/sections/01-introduction.tex:36`: «million».
- [ ] `paper/sections/01-introduction.tex:42`: «нескольких», «одной».
- [ ] `paper/sections/01-introduction.tex:43`: «одной».
- [ ] `paper/sections/01-introduction.tex:47`: «двух».
- [ ] `paper/sections/01-introduction.tex:50`: «миллиона».
- [ ] `paper/sections/01-introduction.tex:53`: «миллиона».
- [ ] `paper/sections/02-workload.tex:1`: «единица».
- [ ] `paper/sections/02-workload.tex:7`: «тысячи», «тысяч».
- [ ] `paper/sections/02-workload.tex:8`: «тысяч».
- [ ] `paper/sections/02-workload.tex:10`: «тысяч».
- [ ] `paper/sections/02-workload.tex:12`: «тысяч», «тысяч».
- [ ] `paper/sections/02-workload.tex:15`: «один».
- [ ] `paper/sections/02-workload.tex:16`: «одного».
- [ ] `paper/sections/02-workload.tex:20`: «одной».
- [ ] `paper/sections/02-workload.tex:25`: «одному».
- [ ] `paper/sections/02-workload.tex:27`: «один».
- [ ] `paper/sections/02-workload.tex:36`: «тысяч».
- [ ] `paper/sections/02-workload.tex:37`: «тысяч», «четыре», «тысячи».
- [ ] `paper/sections/02-workload.tex:38`: «одного».
- [ ] `paper/sections/02-workload.tex:43`: «тыс».
- [ ] `paper/sections/02-workload.tex:49`: «тысяч», «тысячи».
- [ ] `paper/sections/02-workload.tex:50`: «тысяч», «половины», «десятой».
- [ ] `paper/sections/03-architecture.tex:8`: «два», «Шестнадцать».
- [ ] `paper/sections/03-architecture.tex:10`: «одну».
- [ ] `paper/sections/03-architecture.tex:11`: «обе».
- [ ] `paper/sections/03-architecture.tex:13`: «один».
- [ ] `paper/sections/03-architecture.tex:38`: «два».
- [ ] `paper/sections/03-architecture.tex:44`: «тысяч».
- [ ] `paper/sections/03-architecture.tex:45`: «тысяч».
- [ ] `paper/sections/03-architecture.tex:68`: «Два».
- [ ] `paper/sections/03-architecture.tex:75`: «тысячи», «тысячи».
- [ ] `paper/sections/03-architecture.tex:81`: «одно».
- [ ] `paper/sections/03-architecture.tex:89`: «одними».
- [ ] `paper/sections/03-architecture.tex:90`: «одних».
- [ ] `paper/sections/03-architecture.tex:95`: «двух».
- [ ] `paper/sections/03-architecture.tex:130`: «обоих».
- [ ] `paper/sections/04-channel.tex:5`: «тысячу».
- [ ] `paper/sections/04-channel.tex:6`: «полутора», «пятнадцати».
- [ ] `paper/sections/04-channel.tex:7`: «вдвое», «оба».
- [ ] `paper/sections/04-channel.tex:10`: «Один», «одной».
- [ ] `paper/sections/04-channel.tex:11`: «тысяч», «тысяч».
- [ ] `paper/sections/04-channel.tex:12`: «тысячи».
- [ ] `paper/sections/04-channel.tex:17`: «одной», «одной».
- [ ] `paper/sections/04-channel.tex:26`: «тыс», «тыс».
- [ ] `paper/sections/04-channel.tex:27`: «тыс», «тыс».
- [ ] `paper/sections/04-channel.tex:28`: «тыс», «тыс».
- [ ] `paper/sections/04-channel.tex:29`: «тыс», «тыс».
- [ ] `paper/sections/04-channel.tex:35`: «нуля».
- [ ] `paper/sections/04-channel.tex:36`: «тысяч».
- [ ] `paper/sections/04-channel.tex:41`: «первого».
- [ ] `paper/sections/04-channel.tex:49`: «тыс».
- [ ] `paper/sections/04-channel.tex:50`: «тыс».
- [ ] `paper/sections/04-channel.tex:51`: «тыс».
- [ ] `paper/sections/04-channel.tex:56`: «тысяч».
- [ ] `paper/sections/04-channel.tex:57`: «тысячи».
- [ ] `paper/sections/04-channel.tex:60`: «вдвое».
- [ ] `paper/sections/04-channel.tex:65`: «тысяч», «тысячи», «первого».
- [ ] `paper/sections/04-channel.tex:73`: «первого».
- [ ] `paper/sections/04-channel.tex:86`: «одной».
- [ ] `paper/sections/04-channel.tex:92`: «одной».
- [ ] `paper/sections/04-channel.tex:109`: «семь».
- [ ] `paper/sections/04-channel.tex:115`: «три».
- [ ] `paper/sections/04-channel.tex:120`: «третий», «три», «пяти».
- [ ] `paper/sections/04-channel.tex:124`: «восьмичасовой».
- [ ] `paper/sections/04-channel.tex:137`: «десятки».
- [ ] `paper/sections/05-clients.tex:4`: «нескольких».
- [ ] `paper/sections/05-clients.tex:5`: «триллион».
- [ ] `paper/sections/05-clients.tex:6`: «три».
- [ ] `paper/sections/05-clients.tex:8`: «миллиардов», «миллиардов», «миллиардов».
- [ ] `paper/sections/05-clients.tex:15`: «миллион».
- [ ] `paper/sections/05-clients.tex:20`: «тыс», «тыс».
- [ ] `paper/sections/05-clients.tex:35`: «тысяча».
- [ ] `paper/sections/05-clients.tex:37`: «одна», «тысяч», «семь», «одна».
- [ ] `paper/sections/05-clients.tex:38`: «полмиллиона», «две», «миллион», «тысяч», «миллион».
- [ ] `paper/sections/05-clients.tex:39`: «тысячи».
- [ ] `paper/sections/05-clients.tex:50`: «тыс», «тыс», «тыс», «тыс», «тыс».
- [ ] `paper/sections/05-clients.tex:62`: «тысяч».
- [ ] `paper/sections/05-clients.tex:63`: «Несколько», «один».
- [ ] `paper/sections/05-clients.tex:64`: «четырёх», «тысячи», «одного».
- [ ] `paper/sections/05-clients.tex:71`: «восьмичасовой», «четырьмя», «нескольких».
- [ ] `paper/sections/05-clients.tex:72`: «четырёх», «двух», «половиной», «тысячи».
- [ ] `paper/sections/05-clients.tex:75`: «четыре».
- [ ] `paper/sections/05-clients.tex:76`: «вдвое».
- [ ] `paper/sections/05-clients.tex:77`: «треть».
- [ ] `paper/sections/05-clients.tex:78`: «миллиардами».
- [ ] `paper/sections/05-clients.tex:83`: «восьмичасовой», «четырьмя».
- [ ] `paper/sections/05-clients.tex:85`: «одного», «тысячи».
- [ ] `paper/sections/05-clients.tex:105`: «несколькими», «первую».
- [ ] `paper/sections/05-clients.tex:107`: «десятки», «million».
- [ ] `paper/sections/05-clients.tex:108`: «обоих».
- [ ] `paper/sections/05b-models.tex:4`: «две».
- [ ] `paper/sections/05b-models.tex:5`: «четыре».
- [ ] `paper/sections/05b-models.tex:6`: «одной».
- [ ] `paper/sections/05b-models.tex:11`: «миллиардов».
- [ ] `paper/sections/05b-models.tex:13`: «тысяча».
- [ ] `paper/sections/05b-models.tex:15`: «тысячи».
- [ ] `paper/sections/05b-models.tex:25`: «тыс».
- [ ] `paper/sections/05b-models.tex:41`: «тысяча», «тысяча», «втрое».
- [ ] `paper/sections/05b-models.tex:47`: «две», «тысячу».
- [ ] `paper/sections/05b-models.tex:50`: «million».
- [ ] `paper/sections/05b-models.tex:54`: «три».
- [ ] `paper/sections/05b-models.tex:56`: «тысячи», «тысячи», «тысячи».
- [ ] `paper/sections/05b-models.tex:58`: «тысячи», «четырёх».
- [ ] `paper/sections/05b-models.tex:61`: «одно».
- [ ] `paper/sections/05b-models.tex:63`: «один», «первое», «второго».
- [ ] `paper/sections/05b-models.tex:64`: «первое».
- [ ] `paper/sections/05b-models.tex:65`: «двух».
- [ ] `paper/sections/05b-models.tex:67`: «трёх», «тысячу».
- [ ] `paper/sections/05b-models.tex:68`: «тысяч», «единице», «тысяч».
- [ ] `paper/sections/05b-models.tex:72`: «миллиардами».
- [ ] `paper/sections/05b-models.tex:73`: «единицы».
- [ ] `paper/sections/05b-models.tex:74`: «единицы».
- [ ] `paper/sections/05b-models.tex:75`: «единицы».
- [ ] `paper/sections/05b-models.tex:82`: «тысяч», «миллион», «единицы».
- [ ] `paper/sections/05b-models.tex:83`: «единицы».
- [ ] `paper/sections/05b-models.tex:85`: «десять».
- [ ] `paper/sections/05b-models.tex:86`: «миллион».
- [ ] `paper/sections/05b-models.tex:93`: «тыс».
- [ ] `paper/sections/05b-models.tex:94`: «тыс».
- [ ] `paper/sections/05b-models.tex:95`: «тыс».
- [ ] `paper/sections/05b-models.tex:96`: «тыс».
- [ ] `paper/sections/05b-models.tex:97`: «тыс».
- [ ] `paper/sections/05b-models.tex:98`: «тыс».
- [ ] `paper/sections/05b-models.tex:107`: «одна», «две».
- [ ] `paper/sections/05b-models.tex:109`: «десятки».
- [ ] `paper/sections/05b-models.tex:110`: «тысяч», «миллиона».
- [ ] `paper/sections/05b-models.tex:111`: «нескольких».
- [ ] `paper/sections/05b-models.tex:115`: «тысячу».
- [ ] `paper/sections/05b-models.tex:118`: «двух», «тысячи».
- [ ] `paper/sections/05b-models.tex:119`: «тысячу», «Первое», «второе».
- [ ] `paper/sections/06-server.tex:6`: «одна».
- [ ] `paper/sections/06-server.tex:12`: «одном».
- [ ] `paper/sections/06-server.tex:13`: «одной».
- [ ] `paper/sections/06-server.tex:19`: «тысяч».
- [ ] `paper/sections/06-server.tex:22`: «тысячи», «тысячи».
- [ ] `paper/sections/06-server.tex:25`: «одна», «одна».
- [ ] `paper/sections/06-server.tex:27`: «Одна».
- [ ] `paper/sections/06-server.tex:28`: «одни».
- [ ] `paper/sections/06-server.tex:29`: «одной», «несколько».
- [ ] `paper/sections/06-server.tex:30`: «десятков», «двум», «десяткам».
- [ ] `paper/sections/07-economics.tex:6`: «восьмичасовой».
- [ ] `paper/sections/07-economics.tex:16`: «миллиона».
- [ ] `paper/sections/07-economics.tex:17`: «тысячи».
- [ ] `paper/sections/07-economics.tex:23`: «тысячи».
- [ ] `paper/sections/07-economics.tex:29`: «нулевой».
- [ ] `paper/sections/07-economics.tex:38`: «тыс».
- [ ] `paper/sections/07-economics.tex:39`: «тыс».
- [ ] `paper/sections/07-economics.tex:40`: «тыс».
- [ ] `paper/sections/07-economics.tex:41`: «тыс».
- [ ] `paper/sections/07-economics.tex:45`: «тыс».
- [ ] `paper/sections/07-economics.tex:65`: «восьмичасовой», «четырьмя».
- [ ] `paper/sections/07-economics.tex:67`: «два».
- [ ] `paper/sections/07-economics.tex:77`: «четырёх», «восьмичасовой».
- [ ] `paper/sections/07-economics.tex:101`: «три», «четырёх», «полутора».
- [ ] `paper/sections/07-economics.tex:104`: «четыре».
- [ ] `paper/sections/07-economics.tex:113`: «несколько».
- [ ] `paper/sections/07-economics.tex:132`: «четыре».
- [ ] `paper/sections/07-economics.tex:143`: «пять».
- [ ] `paper/sections/07-economics.tex:150`: «пяти», «одна», «четыре».
- [ ] `paper/sections/07-economics.tex:151`: «две».
- [ ] `paper/sections/07-economics.tex:152`: «двадцати», «одна», «четырнадцать», «две».
- [ ] `paper/sections/07-economics.tex:191`: «восемь».
- [ ] `paper/sections/07-economics.tex:208`: «одной», «четыре».
- [ ] `paper/sections/07-economics.tex:210`: «обе».
- [ ] `paper/sections/07-economics.tex:228`: «три».
- [ ] `paper/sections/07-economics.tex:229`: «одни».
- [ ] `paper/sections/07-economics.tex:231`: «трёх».
- [ ] `paper/sections/07-economics.tex:233`: «Одни».
- [ ] `paper/sections/07-economics.tex:239`: «оба», «одному».
- [ ] `paper/sections/07-economics.tex:241`: «двумя».
- [ ] `paper/sections/07-economics.tex:246`: «пяти», «обоих».
- [ ] `paper/sections/07-economics.tex:251`: «одних», «восьмичасовой».
- [ ] `paper/sections/07-economics.tex:252`: «одна», «две».
- [ ] `paper/sections/07-economics.tex:260`: «Одни».
- [ ] `paper/sections/07-economics.tex:278`: «полгода».
- [ ] `paper/sections/07-economics.tex:284`: «million».
- [ ] `paper/sections/07-economics.tex:309`: «одну».
- [ ] `paper/sections/07-economics.tex:319`: «сотнях».
- [ ] `paper/sections/07-economics.tex:323`: «оба», «одному».
- [ ] `paper/sections/07-economics.tex:325`: «полтора».
- [ ] `paper/sections/08-million.tex:1`: «миллиона».
- [ ] `paper/sections/08-million.tex:2`: «million».
- [ ] `paper/sections/08-million.tex:6`: «тысяч», «миллиона».
- [ ] `paper/sections/08-million.tex:7`: «пять».
- [ ] `paper/sections/08-million.tex:9`: «миллиона», «миллиардов».
- [ ] `paper/sections/08-million.tex:10`: «шесть».
- [ ] `paper/sections/08-million.tex:11`: «миллиону», «тысяч».
- [ ] `paper/sections/08-million.tex:12`: «четырёх», «миллион», «одна».
- [ ] `paper/sections/08-million.tex:14`: «две», «миллиону».
- [ ] `paper/sections/08-million.tex:17`: «миллион».
- [ ] `paper/sections/08-million.tex:19`: «тысячу».
- [ ] `paper/sections/08-million.tex:20`: «тысячи», «тысячи».
- [ ] `paper/sections/08-million.tex:21`: «миллионе».
- [ ] `paper/sections/08-million.tex:22`: «пяти».
- [ ] `paper/sections/08-million.tex:24`: «Пять».
- [ ] `paper/sections/08-million.tex:29`: «million», «миллиона».
- [ ] `paper/sections/08-million.tex:30`: «четыре».
- [ ] `paper/sections/08-million.tex:31`: «двух».
- [ ] `paper/sections/08-million.tex:35`: «обоих».
- [ ] `paper/sections/08-million.tex:38`: «двух», «треть», «семь».
- [ ] `paper/sections/08-million.tex:39`: «миллиону».
- [ ] `paper/sections/08-million.tex:41`: «Четыре», «двое», «две».
- [ ] `paper/sections/08-million.tex:63`: «миллиона», «Две».
- [ ] `paper/sections/08-million.tex:66`: «million».
- [ ] `paper/sections/08-million.tex:69`: «миллиона», «четырёх».
- [ ] `paper/sections/08-million.tex:70`: «четыре».
- [ ] `paper/sections/08-million.tex:71`: «двух», «одной».
- [ ] `paper/sections/09-security.tex:19`: «одна».
- [ ] `paper/sections/09-security.tex:22`: «несколько», «десятков».
- [ ] `paper/sections/09-security.tex:24`: «один».
- [ ] `paper/sections/09-security.tex:28`: «тысяча», «тысяч».
- [ ] `paper/sections/09-security.tex:29`: «полуминуты».
- [ ] `paper/sections/09-security.tex:34`: «одни», «одной».
- [ ] `paper/sections/09-security.tex:35`: «одной».
- [ ] `paper/sections/09-security.tex:44`: «обоих».
- [ ] `paper/sections/09-security.tex:45`: «первую».
- [ ] `paper/sections/09-security.tex:52`: «два».
- [ ] `paper/sections/09-security.tex:55`: «первый».
- [ ] `paper/sections/09-security.tex:66`: «первую».
- [ ] `paper/sections/10-resilience.tex:11`: «одного».
- [ ] `paper/sections/10-resilience.tex:12`: «одной».
- [ ] `paper/sections/11-limitations.tex:4`: «восьмичасовой».
- [ ] `paper/sections/11-limitations.tex:6`: «втрое».
- [ ] `paper/sections/11-limitations.tex:14`: «нескольких».
- [ ] `paper/sections/11-limitations.tex:31`: «одной».
- [ ] `paper/sections/11-limitations.tex:38`: «восемь».
- [ ] `paper/sections/11-limitations.tex:39`: «одна».
- [ ] `paper/sections/12-related.tex:6`: «обе».
- [ ] `paper/sections/12-related.tex:9`: «обе».
- [ ] `paper/sections/12-related.tex:13`: «двух».
- [ ] `paper/sections/12-related.tex:15`: «несколькими», «одной».
- [ ] `paper/sections/12-related.tex:17`: «две».
- [ ] `paper/sections/12-related.tex:23`: «одного», «одной».
- [ ] `paper/sections/12-related.tex:24`: «одной».
- [ ] `paper/sections/12-related.tex:26`: «две», «одной», «один».
- [ ] `paper/sections/12-related.tex:28`: «одна».
- [ ] `paper/sections/13-outlook.tex:4`: «Четыре», «Первый».
- [ ] `paper/sections/13-outlook.tex:5`: «тысяч».
- [ ] `paper/sections/13-outlook.tex:6`: «Второй», «Третий».
- [ ] `paper/sections/13-outlook.tex:7`: «нескольких», «Четвёртый».
- [ ] `paper/sections/13-outlook.tex:12`: «одна», «одном».
- [ ] `paper/sections/13-outlook.tex:13`: «четверти».
- [ ] `paper/sections/13-outlook.tex:24`: «двух».
- [ ] `paper/sections/13-outlook.tex:27`: «вдвое».
- [ ] `paper/sections/14-conclusion.tex:6`: «десятки».
- [ ] `paper/sections/14-conclusion.tex:8`: «обоих».
- [ ] `paper/sections/14-conclusion.tex:9`: «три».
- [ ] `paper/sections/14-conclusion.tex:15`: «миллиона».
- [ ] `paper/sections/14-conclusion.tex:18`: «миллион», «пять».
- [ ] `paper/sections/14-conclusion.tex:20`: «оба».
- [ ] `paper/sections/14-conclusion.tex:21`: «одному».
- [ ] `paper/sections/14-conclusion.tex:30`: «Первая».
- [ ] `paper/sections/90-appendix.tex:19`: «Первое», «второе».
- [ ] `paper/sections/90-appendix.tex:29`: «оба».
- [ ] `paper/sections/90-appendix.tex:30`: «нулю».
- [ ] `paper/sections/90-appendix.tex:32`: «одного».
- [ ] `paper/sections/90-appendix.tex:42`: «один».
- [ ] `paper/sections/90-appendix.tex:45`: «четыре».
- [ ] `paper/sections/90-appendix.tex:52`: «сотен», «тысяч».
- [ ] `paper/sections/90-appendix.tex:56`: «одним».
- [ ] `paper/sections/90-appendix.tex:61`: «Пятнадцать».
- [ ] `paper/sections/90-appendix.tex:62`: «трёх».

## r3: reverse guard percent rendering and line binding (hybrid-e-r3-261101)

This revision addresses the two blocking r5f findings at reviewed head
`02f4b6fde9d5691951a6a19d8596b22d016bedd1`: `ledger-reverse-percent-unscaled`
and `ledger-site-line-binding-unpinned`. Review and exact MW1/MW2/MW3
definitions: `/home/agent/Werkstatt/hybrid-review/paper/.temp/REVIEW-ledger-guard-claude.md`
and its `.temp/r5f/scripts/mutants.sh`. The existing `.temp/tasks.md` tracks
this rework; `task-board goal get` exited 1 because no `.task-board` exists.

### Percent rendering and site regressions

`r13_reverse.tokens()` recognizes `\%`, literal `%` and Russian `процент…`
suffixes. `witnesses()` retains the as-written comparison and also scales
dimensionless fraction values by 100 before rounding at the token's printed
precision. Fractions here mean old values of magnitude at most one with
schema unit `1` or absent unit; byte-unit conversion is preserved. Already
percent-valued quantities still match as written. Independent fixtures check
45.6 → 45.2, all three suffix forms, unchanged printed precision, unchanged
20%/70% inputs, and the absence of percent scaling on an unmarked scalar.

Each of 45.6%, 72.3%, 95.4% and 30.5% has a separately named regression
through the real `check_ledger(texts=...)`. The plants append an in-memory
line to the real 04-channel text, with all other paper texts preserved. Before
the fix, all four tests failed with “AssertionError not raised” (expected red,
exit 1); after the fix all four pass. Same-file plants also exercise 883 in
07-economics and 30% in 05-clients through `check_ledger()`. The 21.6 plant
in 04-channel inspects `native_changes()` directly, so the reverse guard
cannot mask a widened native collision. The untouched paper is the positive
control; its existing rows and waivers still pass.

### Narrowing mutants

Each fault control in `r13reverse_controls.py` asserts exactly one source replacement,
compiles that consumer function in memory, and runs the named behavioral test.
No production file is edited. All required faults fail by assertion, with no
setup error. The native MW3 control includes the reviewer's matching used-waiver
update, so a stale-waiver assertion cannot masquerade as its kill.

| Mutant | What it narrows the gate to | Named failing test | Result / survivor bound |
| --- | --- | --- | --- |
| `percent_unscaled` | As-written numeric values and byte conversions; omits fraction ×100 | `test_reverse_guard_rejects_percent_45_6_same_file`, `test_reverse_guard_rejects_percent_72_3_same_file`, `test_reverse_guard_rejects_percent_95_4_same_file`, `test_reverse_guard_rejects_percent_30_5_same_file` | Killed by all four; actual exit 1, expected red; no survivor |
| `file_token_waiver` (r5f MW1) | Reverse waiver admits any line of its file/token | `test_reverse_waiver_rejects_same_file_30_percent_at_new_line` | Killed; actual exit 1, expected red; no survivor |
| `file_token_ledger` (r5f MW2) | Ledger coverage admits any line of its file/token | `test_reverse_ledger_rejects_same_file_883_at_new_line` | Killed; actual exit 1, expected red; no survivor |
| `file_token_native_collision` (r5f MW3) | Native collision admits any line of its file/token | `test_native_collision_rejects_same_file_21_6_at_new_line` | Killed directly; actual exit 1, expected red; no survivor |

Evidence: `.temp/hybrid-e-r3-261101/required-mutants.json` and
`mutant-{percent-unscaled,file-token-waiver,file-token-ledger,file-token-native-collision}-01.log`
with matching process-result JSON files. The existing `arch_only` and
`token_waiver` controls were rerun: both exit 1 as expected, killed by
`test_reverse_guard_rejects_copied_non_arch_changed_values` (eight subtests)
and `test_paper_ledger_waivers_are_site_bound`, respectively. Their logs are
`mutant-arch-only-01.log` and `mutant-token-waiver-01.log`. The unmutated
`comment` control exits 0 (`comment-control-01.log`). No fault survives.

### Regression evidence and delivery scope

All gate commands run as standalone processes, without pipelines. CPU only,
Python 3.14.4 on agents1 Linux; `PYTHONDONTWRITEBYTECODE=1` and disk-backed
`TMPDIR=.temp/hybrid-e-r3-261101/tmp` throughout. No downloads, GPU or native
builds. Logs, command arrays, actual PIDs, times and exit codes are under
`.temp/hybrid-e-r3-261101/`.

| Standalone command / gate | Actual exit | Evidence |
| --- | ---: | --- |
| `python3 -m unittest discover -s calc/tests -v` | 0 | `engine-suite-01.log`, matching result JSON; **285 tests, 762.219 s** |
| `python3 -m unittest discover -s bench/tests -v` | 0 | `kit-suite-01.log`, matching result JSON; **24 tests, 23.700 s** |
| `python3 -m unittest discover -s calc/tests -p test_r13_reverse.py -v` | 0 | `reverse-tests-01.log`; 15 tests |
| `python3 calc/tests/r13_ledger.py` | 0 | `ledger-01.log`, matching result JSON |
| Four pre-fix percent regressions / all six fault controls | **1, expected red** | `percent-regression-before-01.log`, `mutant-*-01.log`, matching result JSON; named assertions above |
| `python3 calc/tests/r13reverse_controls.py comment` | 0 | `comment-control-01.log`, matching result JSON |
| Exact export/ledger byte audit, test-name retention and Python 3.9 syntax parse | 0 | `artifact-verification-final.log`, `artifact-verification.json` |
| Unit-aware percent-site audit | 0 | `percent-site-audit-01.log`, `percent-site-audit.json` |
| >28 GB disk sample gate | 0 | `disk-floor-01.log`, `validation-disk-snapshot.json` |

The ledger is byte-identical to r2: **32042 rows**, SHA-256
`cefebfec62576644829f4195f22e58cffc52090b8ea1e3636145c1fd2589c92c`.
The new rendering discovers **no missing site** and needs **no new row or waiver**.
An additional unit-aware percent-site audit also finds no unaccounted site
(`percent-site-audit-01.log`, exit 0). Its grouped-token count differs from
the reviewer's 119 endpoint hits, which also scale seconds/dollar collisions;
`percent-count-conventions.json` records that distinction.
The real checker reports 1409 scanned numbers, 32042 dependencies, 1210 reverse
occurrences and 904 site waivers; r2 had 1207 reverse occurrences. The three
additional detected occurrences were already accounted for. All **150 historical
and 252 run-13 export files** remain byte-identical to `02f4b6fd`; engine, inputs
and paper sources are unchanged. Every previously committed test name remains.
The unchanged paper formula helper emits its existing unclosed-reader
`ResourceWarning`; it is retained in the logs.
Runtime source/test identity is frozen before the full suite and verified against
`candidate-source-identity.json` afterwards. No export regeneration is needed
for this checker/test change; every committed export is compared byte for byte.

The one-second disk monitor's sampled minimum through **2026-11-01T23:04:24.753219+00:00** is
**33332596736 bytes (33.332597 GB)**, above the
28,000,000,000-byte floor. These are samples, not continuous visibility between
samples. Monitoring continues through delivery; `disk-summary.json` retains the
full-run minimum and last sample. No resource abort occurred. No foreign
process or file was stopped or removed.

No surface table or separate landing-property suite was supplied (retained brief
gap). Both requested contracts are mapped to named tests and killed mutants
above; no requested row is treated as out of contract. Previously committed
reviewer tests are retained. Scope is limited to the reverse checker, its tests
and control driver, tool documentation, this report and the root manifest.
The pre-existing number-word checklist remains manual under its original scope.
Self-review covers the scoped diff, named control failures and byte identity.
Independent acceptance is pending: **ready for review**. The owner explicitly
requires a signed local commit with the Codex coauthor trailer and no push;
push, hosted CI and landing are not claimed.
