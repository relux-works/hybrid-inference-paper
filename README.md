# Hybrid inference: architecture and economics (working repository)

Engine run14 adds archive-backed M3 depth/stream anchors, the measured M5 Max
family and measured B300 llama.cpp/FP8 options. It preserves every historical
and run13 export. See [`calc/README.md`](calc/README.md#run-14-measured-parallel-m5-and-b300)
for CPU-only commands and output locations; the corrected full-mix table labels
modelled depth/count zones and preserves separate measured-depth subsets.

Working repository for the paper «Hybrid Inference with Client–Server Prefill–Decode Disaggregation: Architecture and
Economics for Unified-Memory Clients». Authors: Ivan Oparin, Alexey Grigoriev and Timur Kackan (Relux Works).

The idea: a GPU server prefills an agent session and ships the model state (attention KV of the new positions plus the
fixed recurrent state) to a unified-memory client such as a Mac, which decodes locally.

Status: a draft heading for version 0.1.0 (versions `0.y.z` are drafts; see below). The Russian text, the calculation
engine (`calc/`, runs 1–14) and the data behind every number of the paper are in place. Version 0.1.0 is released
after the scheme has been checked on GPU hardware. The prototype lives in a separate repository,
[`relux-works/hybrid-inference`](https://github.com/relux-works/hybrid-inference).

The `0.1.0-rc.2` candidate contains reviewed paper v2 and engine runs 13 and 14; see
[`CHANGELOG.md`](CHANGELOG.md#010-rc2---2026-11-02). The growing-session CUDA-to-Metal run, the KL study,
CUDA-to-Metal calibration and cooled kit 1.6.6 measurements remain pending. The incident lane publishes the
candidate under the owner's identity after its release gates pass.

Licences: everything in this repository is licensed under MIT (`LICENSE`), except the paper and its materials, which
are licensed under CC BY 4.0 (`paper/LICENSE`): the text, figures and data under `paper/` other than the scripts in
`paper/data/`, the source notes and measurements in `data/`, and the documents in `docs/`. The engine snapshot in
`paper/data/engine/` copies `calc/out/paper/`, so the same numbers are available under either licence. Quotations in
the source notes keep their authors' terms, and the PT fonts keep their own OFL licences.

To contribute measurements from a Mac or an NVIDIA GPU, or statistics of your agent sessions, see
[`bench/`](bench/README.md).

## Versions and releases

Every version of the paper is a [GitHub Release](https://github.com/relux-works/hybrid-inference-paper/releases). It
carries the PDF, `hybrid-inference-X.Y.Z.ru.pdf`, and `SHA256SUMS`. The English version will join the same release as
`.en.pdf`. To download one version: `gh release download vX.Y.Z -R relux-works/hybrid-inference-paper -p '*.pdf'`.

The title page states the version, so a forwarded or printed copy identifies itself. Any other build says «черновик»
with its `git describe` label. For pull requests and `main`, CI only checks that the PDF builds and keeps no copy: the
PDF never goes through Actions artifact storage. To share a draft, publish a pre-release such as `v0.2.0-rc.1`.

Versions follow [Semantic Versioning](https://semver.org), read for a paper:

| Part | Raised when |
|---|---|
| MAJOR | A conclusion changes, or a change of method moves the main results |
| MINOR | New or corrected numbers, sections, figures or appendices, with every conclusion still standing |
| PATCH | Wording, typos, layout and references only; no number changes |

Versions `0.y.z` are drafts; `1.0.0` is the first version for outside readers. A candidate such as `v1.0.0-rc.1` is
published as a GitHub pre-release and never marked latest.

To release version X.Y.Z:
1. In the pull request that completes the version, move the entries under `## [Unreleased]` in `CHANGELOG.md` into a new section `## [X.Y.Z] - YYYY-MM-DD`.
2. After it lands, tag that commit on `main` with a signed tag and push the tag: `git tag -s vX.Y.Z -m "Paper X.Y.Z" && git push origin vX.Y.Z`.
3. CI checks the tag, builds the PDF and publishes the release. Nothing is published unless all of these hold:
   - the tag is SemVer with a leading `v`;
   - the commit is on `main`;
   - the tag is annotated and has a valid SSH signature for `ivan@relux.works`, verified with
     `.github/allowed_signers` copied from the current reviewed `origin/main` commit;
   - the tagged tree carries exactly that same signer pin;
   - `CHANGELOG.md` at that commit has a non-empty section for the version.

The public signer pin is the `ssh-ed25519` key of GitHub user `ivanopcode`, key id `1245573`, titled
"ivmbp agents signing 2026-10-15". Its fingerprint is
`SHA256:rE/sRlfdFt/vT5y5yukDCsq4aFtC48pbWsq9z4hm8MA`. Source: the public
[`GET /users/ivanopcode/ssh_signing_keys`](https://api.github.com/users/ivanopcode/ssh_signing_keys) API;
pin supplied by the orchestrator and fingerprint checked on 2026-10-30. The committed allowed-signers entry
restricts the principal to `ivan@relux.works` and the namespace to `git`. CI verifies with `git verify-tag`,
`gpg.format=ssh` and `gpg.ssh.allowedSignersFile` pointing to a temporary copy extracted with `git show` from
the resolved default-branch commit. It never uses the tagged or working-tree pin as its trust source.
Signer-policy changes must land on the reviewed default branch before tagging. Historical tags with a
different or absent pin cannot be released by this gate. No private signing key or signing agent is provisioned
in CI; signature tests generate disposable fixture keys outside their throwaway repository trees.

A published release is never rebuilt or replaced: a correction is a new version. If a run fails before publishing, for
example on a network error, re-run it. If the tag itself is wrong, release the next version and leave the tag in place.

Both CI jobs use standard GitHub-hosted Linux x64 `ubuntu-24.04` runners. Pull requests use `pull_request`
with `contents: read`; no repository secrets, private-network connection, signing agent or production credentials
are configured. Only the tag release job has `contents: write`, used by the publication step after tag verification
and the PDF build. Checkout never persists credentials, and actions are pinned by full commit SHA. There is no
self-hosted fallback. Assets and `SHA256SUMS` are uploaded into a draft release before it is published, without
Actions artifact storage.

## Layout

| Path | What |
|---|---|
| `paper/` | Paper sources: the Russian version first, the shared layout and the fonts; see [`paper/README.md`](paper/README.md) |
| `CHANGELOG.md` | What changed in each released version of the paper |
| `.scripts/`, `Makefile` | PDF build and release scripts; see "Building the PDF" |
| `.github/workflows/paper.yml` | CI: builds the PDF and publishes releases |
| `calc/` | Data-driven calculation engine and exact legacy wrappers, Python 3.9+ standard library only; see [`calc/README.md`](calc/README.md) |
| `data/research/` | Source notes from October 2026, each item tagged [fact] with URL and quote, [estimate] or [unverified] |
| `data/measurements/ivmbp-2026-10-30/` | Aggregate statistics of the agent sessions behind the workload model (Claude Code, Codex, Muse), as delivered: no transcripts |
| `bench/` | Measurement kits for contributors: Mac and NVIDIA GPU long-context benchmarks, agent-session statistics with consent; start with [`bench/AGENT_PROMPT.md`](bench/AGENT_PROMPT.md) |
| `docs/prototype/` | Prototype plan and technical specification (v0.3) |
| `tools/` | Mac measurement scripts: prefill and decode benchmark by depth, and session statistics |

## Calculations

The calculation engine lives in [`calc/hybridcalc/`](calc/hybridcalc/). Hardware,
models, API/rental/device prices, workload and economics are JSON inputs with
units and provenance. New hardware and changed assumptions need a data file or
an override. It runs without installation or network access:

```bash
python3 -m hybridcalc list
python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper
python3 -m hybridcalc run paper-tables-r6 --format md
python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper
python3 -m hybridcalc run paper-tables --format md
python3 -m hybridcalc export paper-tables --output calc/out/paper
python3 -m hybridcalc run paper-base --strict --format md
python3 -m hybridcalc run paper-base --set hardware.links.wan.bandwidth=2500000000
python3 -m hybridcalc run glm-tier2 --format json
python3 -m hybridcalc run service-quantized --strict --format csv
python3 -m hybridcalc run service-bf16-academic --format md
python3 -m hybridcalc run crossover-bridge --strict --format md
python3 -m hybridcalc run owners-paper --format md
python3 -m hybridcalc run owners-paper --set owners.server_precision=Q6 owners.client_quant=Q3
python3 -m hybridcalc sources paper-base
python3 -m unittest discover -s calc/tests
```

`paper-base` uses the measured M3 Max prefill curve and full04 call mix, with
Apple client, API, fleet, equilibrium and edge tables. `glm-tier2` compares four
256 GB-class GLM decode configurations, including explicit split-pipeline
communication estimates for Spark and Strix pairs. Costs and extrapolated
performance are estimates. `service-quantized` (Q4 by default), `service-fp8` and the labelled
academic `service-bf16-academic` size warm prefill pools
for 10/100/1,000 users and four daily profiles against five GPU tariffs and APIs.
Missing or invalid inputs produce alarms in dependent cells while independent
metrics remain available. `--strict` exits nonzero after printing any alarms;
without it, partial results exit 0 unless nothing numeric is computable. BF16
L40S placement intentionally alarms because its weights exceed 48 GB. Full05
call dates remain a separate, partial snapshot.

`owners-economics` adds team costs at 20%/50% open share (100% is labelled
academic), residual and buy/rent grids, client fit and call capacity, small-team
GLM/27B sessions, and selling-price break-even. The fit grid intentionally includes
infeasible configurations, so `--strict` exits 1 after printing their alarms.
The report distinguishes shared rental service costs from dedicated warm pools
and existing Macs from new purchases. Crossovers are derived rather than assumed.

`crossover-bridge` explains calc5 → r3 one assumption at a time and checks
integer-grid sensitivity. `owners-paper` is the corrected paper candidate: an
8-hour operator day, colocated 1–2 GPU servers for remote teams, measured 27B
KV/state fit through 1M, autopilot load and an explicitly hypothetical idle pool
with bounded drain. Its own-cluster crossover checks every integer team through
20,000. `owners-economics` remains the reviewed r3 reference. The report explains
the output-prefill correction and why the old 500-person result is conditional.

Run 10 adds the owner-requested 20-person team to the ordered paper grid
(5, 10, 20, 50, 500, 5000). All R9 default/conservative exports are regenerated;
the [R10 report](calc/ENGINE-REPORT-261030.md#run-10-small-team-own-server-grid)
compares 5/20-person own-server costs and records the existing-row byte audit.
Run `python3 calc/tests/r10_controls.py` to check against the pinned R9
baseline; `--diff PATH --added PATH` writes per-file counts and added rows.
The R9 and R10 commits are not part of this repository's history, so their paper CSVs
are kept in `calc/tests/data/history/` with each file's git blob id and SHA-256;
the audits read local git when those commits are present and the verified archive otherwise.

Run 9 makes append-only KV spill, deferred catch-up and active-window RAM/NVMe
retention the default in the paper scenarios. Parallel `*_conservative.csv`
files use append-only spill with per-call shadow and month-long RAM; export the
matching `paper-tables[-r6|-r7|-r8]-conservative` scenarios. Run 8's full-slot
rewrite is retained only as a historical regression witness. The intensity CSV
now includes 1k/10k portions and f32/estimated bf16 recurrent state. See the
[run-9 guide](calc/README.md#protocol-hosting-run-9) and
[report](calc/ENGINE-REPORT-261030.md) for the old/design/conservative comparisons.

`paper-tables-r8` adds output-only accounting sensitivity, people per GPU,
a 70k transcript example and a FLOP/byte bound. Run 8 also regenerates the
run-5/6/7 charts with measured token-tail/depth calibration, full server shadow
and explicit session storage/reload costs. These corrections supersede their
previous published numbers; the report links every changed cell and the
headline comparisons. New CSVs and `r8_*.json` sidecars share `calc/out/paper/`.
See the [run-8 guide](calc/README.md#paper-charts-run-8) and
[report](calc/ENGINE-REPORT-261030.md). Historical crossover/legacy scenarios
retain their dated inputs.

`paper-tables-r7` adds four charts: large-turn speedup, one-shot ingestion,
hypothetical faster decode and an architecture comparison reproducing the
owner-supplied script. CSVs are `turn_speedup.csv`, `oneshot_ingest.csv`,
`decode_sensitivity.csv` and `arch_compare.csv` in `calc/out/paper/`, with
`r7_*.json` audit files. Import/last-token costs and f32/bf16 state assumptions
are explicit. Capacity at 3× decode and unsupported architecture contexts alarm;
see the [run-7 guide](calc/README.md#paper-charts-run-7) and report.

`paper-tables-r6` adds closed-perimeter costs (all calls open, no outside
fallback), one cost CSV per light/medium/heavy profile, shared Studio utilization
at 200k/1M, and Q4/q8_0 decode bandwidth bounds with separate measured 32k anchors.
The six CSVs share `calc/out/paper/` with run 5; `r6_*.json` audit sidecars keep each generation auditable. The default six alarms are non-fitting 64 GB decode
configurations; the perimeter and Studio tables compute. See the
[run-6 guide](calc/README.md#paper-charts-run-6) and
[report](calc/ENGINE-REPORT-261030.md).

`paper-tables` provides the paper's ten named chart tables and one CSV per chart
in `calc/out/paper/`. It exposes both overflow API bills and hybrid totals, six
Macs with explicit acquisition bases, the measured parallel anchor, remote
rent/buy, traffic, GLM and deep fit. Exported alarm cells are `nan` with row
status and detailed sidecars; no gap becomes a zero.

Historical calc2–9 and sensitivity scenarios reproduce their lane `.out` files
byte for byte. The original script names remain thin wrappers, for example
`python3 calc/hybrid_calc4.py > .temp/calc4.out`. Markdown, CSV, JSON, legacy text
and LaTeX booktabs output share the engine; one compact TeX example is included.
See [`calc/README.md`](calc/README.md) for scenarios, data format, overrides and
tests, and [`calc/ENGINE-REPORT-261030.md`](calc/ENGINE-REPORT-261030.md) for delivery
evidence and limitations. Assumptions needing further measurements are listed in
[`UNRESOLVED_QUESTIONS.md`](UNRESOLVED_QUESTIONS.md).

## Measurement tools

Use Python 3 for local numeric session analysis and inference benchmarking; see
[`tools/README.md`](tools/README.md) for exact commands, private source coverage,
usage-event UTC date semantics and benchmark interpretation. For example:
`mkdir -p .temp/session-stats && python3 tools/agent_session_stats.py --auto --out .temp/session-stats/stats.json --coverage .temp/session-stats/coverage.json`.
Outputs belong under `.temp/`; coverage and per-call CSV stay private. Run the
Swift 6/Swift Testing fixtures with
`swift test --package-path tools/tests --scratch-path .temp/session-stats-build`.
The original delivered measurements remain under `data/measurements/`.

Contributors' measurement kits live in `bench/` (Mac and NVIDIA GPU benchmarks, consent-gated session
statistics); an agent starts from `bench/AGENT_PROMPT.md`. Their shared helper `bench/*/scripts/kitlib.py` (the
depth ladder, the benchmark-record check and the scrubbing of result archives) has tests: `make test-bench`, which
runs `python3 -m unittest discover -s bench/tests`.

## Building the PDF

`make pdf` writes `dist/hybrid-inference-<version>.ru.pdf` and `dist/SHA256SUMS`. The `<version>` in the file name is
read back from `paper/version.tex`, the file the title page prints, so a shared PDF carries the label of its title page. Intermediate files and the TeX log go
to `build/`. `make clean` removes `build/`, `dist/` and the generated `paper/version.tex`.

The build needs [tectonic](https://tectonic-typesetting.github.io) 0.17.0, the version CI uses. On Linux x86-64 or
macOS arm64, `PATH="$(.scripts/install-tectonic.sh):$PATH" make pdf` installs that build into a cache directory, after
checking its SHA-256 digest. The fonts come from `paper/fonts/`, so every machine sets the same glyphs.

| Tool | What it does | How to run | Outputs |
|---|---|---|---|
| `Makefile` | Builds the PDF; refreshes `MANIFEST.sha256` | `make pdf`, `make clean`, `make manifest` | `build/`, `dist/`; `MANIFEST.sha256` |
| `.scripts/version.sh` | Version label from git tags; with `--tex`, the title-page version; with `--label-of FILE`, the label recorded in that file (used for the PDF name) | Called by `make pdf` | stdout / generated version label |
| `.scripts/release-check.sh` | Verifies the tag signature and release criteria, then extracts its changelog section | `.scripts/release-check.sh vX.Y.Z`; notes go to `build/release-notes.md` | `build/release-notes.md` on accepted tags |
| `.scripts/install-tectonic.sh` | Installs the pinned tectonic and prints its directory | See above | tool cache; stdout path |
| `.scripts/test-release.sh` | Version, changelog, ancestry and SSH authorization tests; needs Bash, Git and OpenSSH `ssh-keygen` | `.scripts/test-release.sh`; disposable repositories and keys are removed on exit | Disposable repositories and keys removed on exit |
| `.scripts/test-release-signatures.sh` | Authorized signature control plus rejection fixtures for unsigned, lightweight, foreign-key, tampered-pin and related trust failures | `.scripts/test-release-signatures.sh`; disposable repositories and keys are removed on exit | Disposable verification fixtures removed on exit |
| Git / OpenSSH | Checks SSH tag signatures using the reviewed public pin | Called by `.scripts/release-check.sh`; temporary verification files are removed on exit | Disposable verification fixtures removed on exit |
| `.github/workflows/paper.yml` | Hosted `ubuntu-24.04` builds for pull requests and `main`; verified tags build and publish a draft-first GitHub Release | Automatic; PDF and `SHA256SUMS` go directly to the Release | PDF and `SHA256SUMS` directly in accepted GitHub Releases |
| `hybridcalc` (Python 3.9+) | Calculation tables, metric alarms, service sizing, crossover attribution, ownership/pool estimates, closed-perimeter costs, shared Studios, decode bounds, turn/ingest timing, architecture comparison, protocol session hosting, paired conservative cases and paper examples | `python3 -m hybridcalc list`, `run`, `sources`; `python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper` (also regenerate `paper-tables`, `paper-tables-r6`, `paper-tables-r7`); see `calc/README.md` | stdout; chart CSVs/audit sidecars in `calc/out/paper/`, scratch in `.temp/` |
| R10 CSV byte audit (Python; recorded history or local Git) | Verifies R9 rows are unchanged and only team 20 is added | `python3 calc/tests/r10_controls.py --diff calc/ENGINE-DIFF-R10-261031.csv --added calc/ENGINE-CHANGES-R10-261031.csv` | `calc/ENGINE-{DIFF,CHANGES}-R10-261031.csv`; logs in `.temp/hybrid-calc-r10-261031/` |
| `unittest`, `compileall` | Engine tests and syntax validation | `python3 -m unittest discover -s calc/tests`; `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | `.temp/` logs; ignored bytecode |
| Tectonic (optional cached CSV smoke) | Checks pgfplots can read all 42 design/conservative chart CSVs | From `calc/tests`: `tectonic --only-cached --outdir ../../.temp/hybrid-calc-r9-261030/pgfplots paper_r9_smoke.tex` after creating the directory; `paper_tables_smoke.tex` covers R5 | `.temp/` PDF and captured command log |
| `paper/data/*.py` | Rebuild the paper's chart inputs, architecture table and the owner's API bill; check, against the engine snapshot in `paper/data/engine/`, the figures and stated directions at the sites listed in `SITES` and `DIRECTION_SITES` of `check_ranges.py` (abstract, economics and million-token sections, conclusion, appendix), the client and closed-perimeter table rows, and with a guard over all sections any occurrence of a checked figure's printed form outside those sites; `check_ranges.py` also reads the engine inputs it names from `calc/hybridcalc/data/` (eligibility rule, storage prices and hours). `offload_bound.py` checks the offload-bound example | `python3 paper/data/derive_charts.py`; `python3 paper/data/arch_compare.py`; `python3 paper/data/year_bill.py paper/data/owner-model-usage-2026-10-30.json > paper/data/year-bill-summary.json`; `python3 paper/data/check_ranges.py`; `python3 paper/data/offload_bound.py`; the last three also take `--self-test` | `paper/data/*.csv`, `paper/data/year-bill-summary.json`; stdout |
| `sha256sum` | Checks every tracked file against `MANIFEST.sha256`; after any change, `make manifest` rewrites the list | `sha256sum -c MANIFEST.sha256` | stdout |
| Run 11 audit (Python; recorded history or local Git) | Compare every publication numeric cell and all requested headline derivations against signed run 10 | `python3 calc/tests/r11_audit.py` | `calc/ENGINE-{CHANGES,DIFF,QUOTES}-R11-261101.csv` |
| Run 11 negative control (Python) | Plant the forbidden output-plus-reasoning base generation; expected exit 1 is the named output-mean assertion | `python3 calc/tests/r11_controls.py output_sum` | stdout/stderr; capture in `.temp/hybrid-calc-r11-261101/` |

## Engine run 12: measured-server sensitivity

Run11 remains the design case, with all existing publication files preserved byte
for byte. Separate `*_measured_server.csv` charts use the measured llama.cpp Q4
prefill curve from a rented Vast RTX PRO6000; B300 rates transfer the measured
depth-dependent fraction of FP8 peak as an explicit estimate. Decode, prices,
hosting and policy inputs are unchanged. GLM uses an inferred compute envelope,
not a GLM measurement. See the [run12 report](calc/ENGINE-REPORT-R12-261101.md),
[complete comparison](calc/ENGINE-CHANGES-R12-261101.csv),
[quoted values](calc/ENGINE-QUOTES-R12-261101.csv), and
[measurement provenance](data/measurements/vast-2026-11-01/qwen27b-gpu-bench/README.md).

| Tool | Purpose | Exact entry point | Outputs |
| --- | --- | --- | --- |
| Run12 publication audit (Python + local Git) | Export all42 sensitivity charts, paired payback tables, fit/fill residuals and every quoted comparison; assert run11 preservation | `python3 calc/tests/r12_audit.py` (`--audit-only` rechecks existing exports) | `calc/out/paper/*_measured_server.csv`, namespaced JSON sidecars; `calc/ENGINE-{CHANGES,DIFF,QUOTES,FLIPS}-R12-261101.csv`, `calc/SERVER-FIT-R12-261101.csv`; audit log in `.temp/hybrid-calc-r12-261101/` |
| Measured-server engine (Python) | Run/export one labelled sensitivity | `python3 -m hybridcalc export paper-tables-measured-server --output calc/out/paper` (also `paper-tables-r6-measured-server`, `paper-tables-r7-measured-server`, `paper-tables-r8-measured-server`; insert `-conservative` before `-measured-server` for the other policy) | Measured-server siblings only |
| Run12 tests/control (Python) | Rate fidelity, immutable design CSVs and intended old-MFU rejection | `python3 -m unittest discover -s calc/tests -p test_run12.py`; `python3 calc/tests/r12_controls.py old_mfu` | stdout/stderr; old-MFU plant must exit1 with the named timing assertion; logs under `.temp/hybrid-calc-r12-261101/` |

These commands need no build, download or network. Existing run11 manifests retain
their historical generator identity; they are not overwritten by the sensitivity.

## Engine run 13

The [run-13 report](calc/ENGINE-REPORT-R13-261101.md) and
[paper number ledger](calc/ENGINE-QUOTES-R13-261101.csv) cover the reproduced
checkpoints-off server base, earlier/checkpoints-on sensitivities, server-only
vLLM FP8, measured M5 Max64, Sonnet cache pricing and Gemma KV correction.
Historical publication quotes are retained in the ledger. The paper-v2 candidate applies them to the text. New exports live under `calc/out/run13/`;
all run-12 exports retain their original bytes.

| Tool | Purpose | Exact entry point | Outputs |
| --- | --- | --- | --- |
| Run13 audit (Python standard library, local Git) | Verify archives; generate three complete chart cases, current API baselines, derived figures and the paper number ledger | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-b-r32-261101/tmp" python3 calc/tests/r13_audit.py` after creating TMPDIR; `--quotes-only` rechecks quotes | `calc/out/run13/`, `calc/ENGINE-QUOTES-R13-261101.csv`; logs in `.temp/hybrid-b-r32-261101/` |
| Run13 measurement engine | Recompute server fits/reproduction, cold/cached vLLM and admitted client rates | `python3 -m hybridcalc export server-options-r13 --output .temp/hybrid-b-r32-261101/measurement-tables` | Seven CSVs with sources/schema/alarm/manifest sidecars |
| Run13 tests | Archive/manifest and swap rejection, golden inputs, recomputation, bandwidth limits and historical byte preservation | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-b-r32-261101/tmp" python3 -m unittest discover -s calc/tests -p test_run13.py -v` | stdout/stderr; task-scoped logs |
| Run13 child-calibration control | Proves the accounting sensitivity cannot revert to estimated M5 rates | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-b-r32-261101/tmp" python3 calc/tests/r13_controls.py unmeasured_child` | Expected exit1 with `test_accounting_child_retains_measured_m5`; `.temp/hybrid-b-r32-261101/child-mutant-01.log` |
| Run13 historical dependency coverage | Original all-export, formula and reverse-coordinate coverage remains bound to producer source `49a1c1d3`; current CLI validates v2 separately | `PYTHONPATH=calc/tests python3 -m unittest test_run13.Run13Tests.test_historical_quote_ledger_provenance -v` | Read-only verdict from an isolated original-source fixture; historical ledger and waivers unchanged |
| Run13 review-r5d controls | Exercise deleted/narrowed swap guards, unsafe paths, links, duplicate/unmanifested members and reverted native Gemma geometry through named behavioral tests | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-e-r1-261101/tmp" python3 calc/tests/r13fix_controls.py M3` (also `M9`, `M5`, `M6`, `M8`, `link`, `duplicate`, `M10`) | Each fault must exit1 with the named assertion; comment-only M10 must exit0. No production file is edited; task-scoped logs |
| R13 reverse inventory / manual number-word checklist (Python standard library; Python 3.14 validation host) | Audit all paired export keys, list new-only exports explicitly, and enumerate number-words for the writer's manual checklist in the r2 report | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-e-r2-261101/tmp" python3 calc/tests/r13_reverse.py --inventory .temp/hybrid-e-r2-261101/export-inventory-final.json` after creating TMPDIR | Task-scoped inventory JSON; [r2 report](calc/ENGINE-REPORT-R13-261101.md#r2-reverse-quote-ledger-guard-hybrid-e-r2-261101); exact waivers in `calc/tests/data/r13_numeric_waivers.csv` |
| R13 reverse-guard controls (Python) | Narrow to architecture-only changes or widen the native waiver to token-only, through named regression tests | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-e-r2-261101/tmp" python3 calc/tests/r13reverse_controls.py arch_only` (also `token_waiver`, `comment`) | Faults must exit 1 with their named assertion; comment control must exit 0; logs in `.temp/hybrid-e-r2-261101/` |

## Paper v2 candidate (run 13)

`paper/data/engine/` is the exact 42-CSV run13 base; `SOURCE.txt` pins the reviewed engine commit. Measured claims
and pending qualifications are mapped in [PAPER-V2-GAPS-261101.md](calc/PAPER-V2-GAPS-261101.md). Rebuild the chart
inputs with `python3 paper/data/derive_charts.py`, `python3 paper/data/arch_compare.py`, and
`python3 paper/data/year_bill.py paper/data/owner-model-usage-2026-10-30.json > paper/data/year-bill-summary.json`.
Outputs stay in `paper/data/`. Use disk-backed `TMPDIR` and `PYTHONDONTWRITEBYTECODE=1` for validation.

The publication checkers now encode run13: storage is cheaper than prefill, four-session GLM/API savings are
3.3–3.6 times, the llama.cpp envelope varies with depth, and vLLM rates remain server-only. The gap map records every
migrated test, changed conclusion and clean/planted control. Historical exports and producer quote ledgers keep their
original bytes and coordinates; the current v2 publication has a separate exact byte and numeric-site baseline.
The owner reviews and publishes this local candidate; no push or tag is made here.

| Tool | Purpose | Exact entry point | Outputs |
| --- | --- | --- | --- |
| Run13 range guard | All existing sites, computed comparisons, tables and unregistered-number guard | `python3 paper/data/check_ranges.py`; `python3 paper/data/check_ranges.py --self-test` | Named site controls on stdout; `.temp/hybrid-c-r8-261101/ranges-*.log` |
| Run13 offload/server guard | Depth-specific llama.cpp B300 bound; separate vLLM cold-fit and cached-delta rates and bridge boundary | `python3 paper/data/offload_bound.py`; `python3 paper/data/offload_bound.py --self-test` | Named wrong-rate controls on stdout; `.temp/hybrid-c-r8-261101/offload-*.log` |
| v2 publication guard | Pin all paper bytes, every numeric occurrence, exact snapshot and four chart inputs, plus live checker claims | `python3 calc/tests/publication_v2.py` (also `python3 calc/tests/r13_ledger.py`) | Read-only verdict; baselines in `calc/tests/data/paper-v2-publication.json` and `paper-v2-sites.csv` |
| Historical producer-ledger validation | Run the original ledger on its original local source objects at `02f4b6fd`; no downloads or history rewrites | `PYTHONPATH=calc/tests python3 -m unittest test_run13.Run13Tests.test_historical_quote_ledger_provenance -v` | Task-scoped temporary fixture and test output; invoked by full engine suite |
| Complete local suites | Engine and kit regressions | `python3 -m unittest discover -s calc/tests -v`; `python3 -m unittest discover -s bench/tests -v` | `.temp/hybrid-c-r8-261101/engine-01.log`, `kit-01.log` |
| Cache-only paper build | Use `make pdf` with Tectonic's no-download compile option, as in r7 | `make pdf TECTONIC="$PWD/.temp/paper-v2-261101/tectonic-cached"`; wrapper executes `tectonic -X compile --only-cached` | `build/`, `dist/`, `.temp/hybrid-c-r8-261101/pdf-01.log` |

The v2 baseline refresh, `python3 calc/tests/publication_v2.py --refresh`, is an explicit owner-authorized migration
operation. Tests and ordinary validation never refresh it. A later intentional publication edit must review its exact
baseline diff. The historical run13 ledger and reverse-control commands above describe the producer revision;
use the historical-fixture test for those contracts after the v2 text migration.

External-review text response (2026-11-02) narrows the service contribution, adds the primary-source mechanism table,
and treats audit as proposed. The one-user corpus and per-tool dates are explicit; the call-count difference comes
from two snapshots with identical filter parameters. Run14 economics and the growing-session measurement remain
`TODO(data)`. Source readback and finite verification boundaries are in the external-review section of the gap map.

| Tool | Purpose | Exact entry point | Outputs |
| --- | --- | --- | --- |
| External-review publication controls (Python standard library) | Clean publication plus prose/numeric plants in every changed TeX file; corpus reconciliation; finite deferred-tail routing fixtures | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-c-r9-261102/tmp" PYTHONPATH=calc/tests python3 -m unittest test_paper_review -v` after creating TMPDIR | `.temp/hybrid-c-r9-261102/review-controls-01.log`; also part of the complete engine suite |
| Updated offload guard | Numeric/server claims and possibility-versus-actual-gain wording, each with a plant and clean control | `python3 paper/data/offload_bound.py`; `python3 paper/data/offload_bound.py --self-test` | `.temp/hybrid-c-r9-261102/offload-*.log` |

R9 validation uses the same cache-only PDF wrapper and standalone suite commands listed above, with logs under
`.temp/hybrid-c-r9-261102/`, disk-backed `TMPDIR`, and `PYTHONDONTWRITEBYTECODE=1`. No push or tag is authorized.

Overnight measurements (hybrid-c-r10-261102) add the parallel/realistic-agent observations, measured server-only
B300 ladder and vLLM rates, the first heterogeneous uncalibrated bridge run, and pre-import-speed-v2 costs.
The engine snapshot remains run13; the cooled kit1.6.6 sweep, deep bridge/adapter runs and run14 economics remain pending.
Source hashes, evidence paths and finite coverage are in the r10 section of the gap map.

| Tool | Purpose | Exact entry point | Outputs |
| --- | --- | --- | --- |
| Measurement/publication guard | Named source-transcribed rate rows, denominator/version boundaries and pending qualifiers, with an applied violation and clean control at every site | `python3 paper/data/offload_bound.py`; `python3 paper/data/offload_bound.py --self-test` | Verdict and named controls; `.temp/hybrid-c-r10-261102/offload-*.log` |
| Publication drift controls | Exact-byte and numeric plants in all13 changed sections across r9/r10 | `PYTHONPATH=calc/tests python3 -m unittest test_paper_review -v` | `.temp/hybrid-c-r10-261102/review-controls-01.log`; also in the engine suite |

Use the standalone engine/kit/checker and cache-only PDF/manifest commands above with logs in
`.temp/hybrid-c-r10-261102/`, disk-backed `TMPDIR` and `PYTHONDONTWRITEBYTECODE=1`. The guard transcribes the
named measurements; it does not independently reproduce the hardware runs or turn server-only rates into hybrid economics.

Engine Run14 r5 corrects full-mix depth modelling, client import and the primary
owned-fleet comparison. See [the engine instructions](calc/README.md#run14-r5-corrected-full-mix-depth-import-and-owned-fleets)
for tools, exact commands and output paths; the report and quote ledger remain
under `calc/`. Historical and Run13 exports are frozen.

## Current paper v2 candidate: run 14 (2026-11-02)

This section supersedes the historical run13 candidate and pending-run14 notes above.
The signed local merge imports engine-r14 `2d457aed87d415043a2c0566f7a185607f11487e` intact.
The current paper embeds all61 run14 base CSVs, charges client import, uses the measured M5 Max family and B300
llama.cpp curves, and displays optimized symmetric own fleets at all six team sizes. The fixed-B300/API tables remain
explicit hardware references. The 16-agent row is mostly modelled; vLLM unit costs stay server-only.
The31,360-token uncalibrated bridge,48-case task pilot and functional B300 node smoke are added;
heterogeneous equivalence, Mac import-v2 and optimized end-to-end timing remain unqualified.
Exact old/new conclusions, controls and command exits are recorded in
[the run14 gap map](calc/PAPER-V2-GAPS-261101.md#run14-integration-and-publication-migration-hybrid-c-r11-261102).
No push or tag is authorized.

Use `PYTHONDONTWRITEBYTECODE=1` and disk-backed `TMPDIR="$PWD/.temp/hybrid-c-r11-261102/tmp"` after creating that path.
CPU only; no downloads or native builds. Logs belong in `.temp/hybrid-c-r11-261102/`.

| Tool | Purpose / exact command | Outputs |
| --- | --- | --- |
| Engine reproduction | In the task's detached exact engine-head checkout: `python3 -I calc/tests/r14_audit.py`; then `git status --short` must be empty, including ledger/report/R14-R5 CSVs | Existing run14 exports regenerated byte-identically; `engine-export-02.log` |
| Chart derivation | `python3 paper/data/derive_charts.py` | Five CSVs under `paper/data/`, including `team-perimeter.csv` |
| Range checker | `python3 paper/data/check_ranges.py`; `python3 paper/data/check_ranges.py --self-test` | Retained156 site plants, table and engine controls; task logs |
| Offload / measurement checker | `python3 paper/data/offload_bound.py`; `python3 paper/data/offload_bound.py --self-test` | Measured B300 bound, all55 retained named sites and new table/qualification controls |
| Current publication guard | `python3 calc/tests/publication_v2.py`; authorized migration only: `python3 calc/tests/publication_v2.py --refresh` | Exact file and numeric-site pins; five figure inputs recomputed in temporary storage |
| Migration regression tests | `PYTHONPATH=calc/tests python3 -m unittest test_paper_r14 -v` | Payload identity, retained sites, symmetric-budget rejection, all team sizes, no-break-even plus threshold controls |
| Engine / kit suites | `python3 -m unittest discover -s calc/tests -v`; `python3 -m unittest discover -s bench/tests -v` | Standalone logs and actual exits |
| Cache-only PDF | `make pdf TECTONIC="$PWD/.temp/paper-v2-261101/tectonic-cached"` | `build/`, `dist/`; wrapper adds `--only-cached`, never downloads |
| File manifest | `make manifest` | `MANIFEST.sha256` |

The historical producer fixture now uses accepted R13 r3 `49a1c1d3` so all later reviewer regressions remain executable
under their original names. Current reverse checks use the exact current publication baseline; producer ledgers keep
original bytes/coordinates. `calc/tests/data/paper-r14-migration.json` inventories every retained guard site.

The r5j correction (`hybrid-c-r12-261102`) names the traffic sentence's client, binds B300 $3,373/$845 to a unique
light-load one-node record, and aligns the economics caption with the measured M5 Max basis and stated transfers.
The earlier B300 cross-profile uniqueness check had been weakened to a minimum in r11; the correction and finite
controls are recorded in [the r12 gap map](calc/PAPER-V2-GAPS-261101.md#three-r5j-minors-hybrid-c-r12-261102).
Use the same gate commands above with disk-backed `TMPDIR="$PWD/.temp/hybrid-c-r12-261102/tmp"` and
`PYTHONDONTWRITEBYTECODE=1`; logs go in `.temp/hybrid-c-r12-261102/`.

| Tool | Purpose / exact command | Outputs |
| --- | --- | --- |
| r5j regression controls | `PYTHONPATH=calc/tests python3 -m unittest test_paper_r14 -v`; both checker self-tests above | Named pronoun, duplicate/missing/wrong-node B300, other-profile and caption controls; task logs |
