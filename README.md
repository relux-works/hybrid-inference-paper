# Hybrid inference: architecture and economics (working repository)

The `0.1.0-rc.4` source candidate contains reviewed paper `v5d12` and accepted engine runs through 26. Measurements and declared scenarios bound applicability. Qwen RULER scores are equivalent at 8k/32k/64k; at 128k the frozen guard withholds equivalence. The forty-turn CUDA/Metal run showed no long-session speedup. See [the current gap and correction map](calc/PAPER-V5D11-GAPS-261106.md). Owner-signed publication remains with the incident lane.

Working repository for the paper «Hybrid Inference with Client–Server Prefill–Decode Disaggregation: Architecture and
Economics for Unified-Memory Clients». Authors: Ivan Oparin, Alexey Grigoriev, Timur Kackan and Sergei Shchepetkov (Relux Works).

The idea: a GPU server prefills an agent session and ships the model state (attention KV of the new positions plus the
fixed recurrent state) to a unified-memory client such as a Mac, which decodes locally.

Status: a draft heading for version 0.1.0 (versions `0.y.z` are drafts; see below). The Russian text, the calculation
engine (`calc/`, runs 1–26) and the data behind every number of the paper are in place. Version 0.1.0 is released
after the scheme has been checked on GPU hardware. The prototype lives in a separate repository,
[`relux-works/hybrid-inference`](https://github.com/relux-works/hybrid-inference).

The `0.1.0-rc.4` candidate supersedes published rc.3; see
[`CHANGELOG.md`](CHANGELOG.md#010-rc4---2026-11-06). Data cut-off: 2026-11-06 06:00 UTC.
Clean end-to-end replay, long-session vLLM qualification, the unexplained 1.04M Mac tolerance, B300 decode, an admitted Qwen 1M API provider, Mac bf16, timing-only calibration and the declared model/hardware follow-ups remain pending. The source lane creates no public commit or tag. The incident lane verifies the streamed git bundle, creates the owner commit, lands the reviewed PR, signs the tag and rebuilds the assets.

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
| `calc/` | Data-driven calculation engine and exact legacy wrappers, Python standard library only; reference CPython 3.14.4; see [`calc/README.md`](calc/README.md) |
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
| Run12 publication audit (Python + local Git) | Export all 42 sensitivity charts, paired payback tables, fit/fill residuals and every quoted comparison; assert run11 preservation | `python3 calc/tests/r12_audit.py` (`--audit-only` rechecks existing exports) | `calc/out/paper/*_measured_server.csv`, namespaced JSON sidecars; `calc/ENGINE-{CHANGES,DIFF,QUOTES,FLIPS}-R12-261101.csv`, `calc/SERVER-FIT-R12-261101.csv`; audit log in `.temp/hybrid-calc-r12-261101/` |
| Measured-server engine (Python) | Run/export one labelled sensitivity | `python3 -m hybridcalc export paper-tables-measured-server --output calc/out/paper` (also `paper-tables-r6-measured-server`, `paper-tables-r7-measured-server`, `paper-tables-r8-measured-server`; insert `-conservative` before `-measured-server` for the other policy) | Measured-server siblings only |
| Run12 tests/control (Python) | Rate fidelity, immutable design CSVs and intended old-MFU rejection | `python3 -m unittest discover -s calc/tests -p test_run12.py`; `python3 calc/tests/r12_controls.py old_mfu` | stdout/stderr; old-MFU plant must exit 1 with the named timing assertion; logs under `.temp/hybrid-calc-r12-261101/` |

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
| Run13 child-calibration control | Proves the accounting sensitivity cannot revert to estimated M5 rates | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-b-r32-261101/tmp" python3 calc/tests/r13_controls.py unmeasured_child` | Expected exit 1 with `test_accounting_child_retains_measured_m5`; `.temp/hybrid-b-r32-261101/child-mutant-01.log` |
| Run13 historical dependency coverage | Original all-export, formula and reverse-coordinate coverage remains bound to producer source `49a1c1d3`; current CLI validates v2 separately | `PYTHONPATH=calc/tests python3 -m unittest test_run13.Run13Tests.test_historical_quote_ledger_provenance -v` | Read-only verdict from an isolated original-source fixture; historical ledger and waivers unchanged |
| Run13 review-r5d controls | Exercise deleted/narrowed swap guards, unsafe paths, links, duplicate/unmanifested members and reverted native Gemma geometry through named behavioral tests | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-e-r1-261101/tmp" python3 calc/tests/r13fix_controls.py M3` (also `M9`, `M5`, `M6`, `M8`, `link`, `duplicate`, `M10`) | Each fault must exit 1 with the named assertion; comment-only M10 must exit 0. No production file is edited; task-scoped logs |
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
The engine snapshot remains run13; the cooled kit 1.6.6 sweep, deep bridge/adapter runs and run14 economics remain pending.
Source hashes, evidence paths and finite coverage are in the r10 section of the gap map.

| Tool | Purpose | Exact entry point | Outputs |
| --- | --- | --- | --- |
| Measurement/publication guard | Named source-transcribed rate rows, denominator/version boundaries and pending qualifiers, with an applied violation and clean control at every site | `python3 paper/data/offload_bound.py`; `python3 paper/data/offload_bound.py --self-test` | Verdict and named controls; `.temp/hybrid-c-r10-261102/offload-*.log` |
| Publication drift controls | Exact-byte and numeric plants in all 13 changed sections across r9/r10 | `PYTHONPATH=calc/tests python3 -m unittest test_paper_review -v` | `.temp/hybrid-c-r10-261102/review-controls-01.log`; also in the engine suite |

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
The current paper embeds all 61 run14 base CSVs, charges client import, uses the measured M5 Max family and B300
llama.cpp curves, and displays optimized symmetric own fleets at all six team sizes. The fixed-B300/API tables remain
explicit hardware references. The 16-agent row is mostly modelled; vLLM unit costs stay server-only.
The 31,360-token uncalibrated bridge, 48-case task pilot and functional B300 node smoke are added;
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
| Range checker | `python3 paper/data/check_ranges.py`; `python3 paper/data/check_ranges.py --self-test` | Retained 156 site plants, table and engine controls; task logs |
| Offload / measurement checker | `python3 paper/data/offload_bound.py`; `python3 paper/data/offload_bound.py --self-test` | Measured B300 bound, all 55 retained named sites and new table/qualification controls |
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

## Release validation tools and historical fixtures

Release tests use immutable in-tree inputs in `calc/tests/data/history-fixtures/`.
`manifest.json` records named snapshots, original full commit IDs as provenance,
file sizes and SHA-256 object names. `history_fixtures.py` pins the manifest's own
SHA-256 and verifies content before any comparison or extraction. A public clone
plus the release patch needs no author branches, tags, private objects or fetches.
The historical regression tests retain their original assertions; the separately
recorded I/O adapters replace only git content reads. See the
[private-history gap map](calc/PAPER-V2-GAPS-261101.md#public-clone-history-independence-hybrid-c-r14-261102).

| Tool / purpose | Command | Output |
| --- | --- | --- |
| Historical fixture integrity | `python3 calc/tests/history_fixtures.py` | Verification counts on stdout; no writes |
| Engine and publication regression suite | `python3 -m unittest discover -s calc/tests` | Test results; temporary fixtures under disk-backed `TMPDIR` |
| Measurement kit suite | `make test-bench` | Test results; temporary fixtures under `TMPDIR` |
| Numeric range checker and controls | `python3 paper/data/check_ranges.py` and `python3 paper/data/check_ranges.py --self-test` | Verdicts on stdout |
| Offload checker and controls | `python3 paper/data/offload_bound.py` and `python3 paper/data/offload_bound.py --self-test` | Verdicts on stdout |
| Current publication guards | `python3 calc/tests/publication_v2.py` and `python3 calc/tests/r13_ledger.py` | Verdicts on stdout |
| Release script fixtures | `.scripts/test-release.sh` | Includes independent signer fixtures; all repositories/keys are throwaway `TMPDIR` data |
| Repository manifest | `make manifest` then `sha256sum -c MANIFEST.sha256` | `MANIFEST.sha256` |
| Optional local-history audit, **dev only** | `python3 tools/dev/history_audit.py --repo /path/to/author/checkout` | R9/R10 CSV equality verdicts; requires original local objects, never fetches |

For offline validation, set `TMPDIR` to a disk directory and
`PYTHONDONTWRITEBYTECODE=1`. The PDF build, compiler installation and real signed
release-tag check remain documented above. The dev-only audit is excluded from
release acceptance; the suite tests its no-fetch transport guard only against
repositories and object IDs that the test itself creates. `r11_audit.py` through
`r14_audit.py` can compare/regenerate content from the verified snapshots; they
must be run in a disposable copy when preserving the checked-in outputs.

## Paper v3 draft validation

Paper v3 starts at rc.2 tree `71616b82` and incorporates exact engine r15 `04755721`.
The [v3 gap map](calc/PAPER-V3-GAPS-261102.md) compares every FACTS group with rc.2,
records supplemental evidence and preserves unresolved measurement limits. The rc.3 package versions this reviewed v3 text.
The six-agent row remains visible with its held-rate qualification and is excluded from capacity trends.

| Tool | Command | Output |
| --- | --- | --- |
| Publication prose spacing | `python3 .scripts/publication_spacing.py`; optionally `--release-notes PATH` | Checks README, changelog and each release-note section; prints exact failing lines |
| Spacing and v3 controls | `PYTHONPATH=calc/tests python3 -m unittest test_publication_spacing test_paper_v3 -v` | Named negative plants, valid technical-token controls and finite measurement boundaries |
| Current exact publication | `python3 calc/tests/publication_v2.py`; authorized migration: `--refresh` | Run-15 snapshot identity, byte and numeric-site pins; retained historical filename |
| CPU engine and kit | `python3 -B -m unittest discover -s calc/tests -v`; `python3 -B -m unittest discover -s bench/tests -v` | Actual exits and complete logs under task `.temp/` |
| Numeric publication checks | `python3 paper/data/check_ranges.py`; `python3 paper/data/offload_bound.py`; each with `--self-test` | Retained sites plus v3 measurements, source-bound traffic and clean/planted controls |
| Offline PDF | `make pdf TECTONIC="$PWD/.temp/hybrid-c-r15-261102/tectonic-cached"` | `build/`, `dist/`; owner copy `.temp/hybrid-c-r15-261102/hybrid-inference-v3-draft.ru.pdf` |
| File manifest | `make manifest`; `sha256sum -c MANIFEST.sha256` | Tracked-file hashes in `MANIFEST.sha256` |

Set `PYTHONDONTWRITEBYTECODE=1` and a disk-backed `TMPDIR` before these commands.
The task-local Tectonic wrapper passes `--only-cached`; it performs no download.
Spacing checks apply to prose; Markdown code spans/fences and link destinations contain identifiers.
Known model, unit, revision and digest tokens must match as whole tokens, so an accepted substring cannot hide glued prose.

The r16 spacing guard also rejects a percent sign attached to a word and prose colons/commas attached to a digit.
Whole numeric times (`10:12Z`), ratios (`1:1`), versions and thousands separators (`8,301`) pass.
`PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-c-r16-261102/tmp" PYTHONPATH=calc/tests python3 -B -m unittest test_publication_spacing test_paper_v3 -v`
runs the named punctuation, transcript-minute and direct-CSV rounding controls after creating that TMPDIR.
Measured table values are rounded once from the engine CSV to the printed precision.
Use the existing cache-only wrapper with `make pdf TECTONIC="$PWD/.temp/hybrid-c-r16-261102/tectonic-cached"`;
the owner PDF is `.temp/hybrid-c-r16-261102/hybrid-inference-v3-draft.ru.pdf`.
The [r16 gap map](calc/PAPER-V3-GAPS-261102.md#r16-review-corrections-hybrid-c-r16-261102)
records the whole-text r14-to-r15 sweep, finite controls and gate exits.

The rc.3 amendment adds EXO Labs' DGX Spark/M3 Ultra single-request 10GbE prior art,
four-author Cyrillic PDF metadata and explicit session-protocol/audit/economics framing.
Run `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=calc/tests python3 -B -m unittest test_paper_rc3_amendment -v`
for author-surface plants, seven named new checker sites and the comparison-table contract;
the same controls run in the engine suite. Logs belong under `.temp/`.

The second rc.3 amendment adds verified cache-compression, hybrid-prefix, device-cloud and on-device persistence
prior art and bounded quality summaries. The LMCache reference distinguishes legacy in-process support from
the pending multiprocess implementation. No compression speedup is measured by this amendment.
Run `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=calc/tests python3 -B -m unittest test_paper_rc3_review2 -v`
for named claim-removal, source/cell corruption and quality-overclaim controls; the engine suite includes them.
`python3 paper/data/offload_bound.py --self-test` includes the new source-transcribed and measurement-summary sites.
The source-verification record and CPU-only package receipts are under `.temp/hybrid-c-r19-261102/delivery/`.
## Engine run 16

The opt-in run16 calibration replaces M3 Max single-stream anchors with the
recorded PRI 31 step40 run, adds Sergey's cooled M5 sweep (priority
not recorded; the launching process was PRI 31 when checked afterwards), and models the prototype's depth-dependent
client import. Existing M3 parallel results remain explicitly interim because
they were measured in a background-priority context. Both the fitted prototype
and unimplemented bounded-undo sensitivity are exported; earlier exports stay
frozen.

Tool: Python 3 standard library with local Git. From the repository root:

```bash
mkdir -p .temp/hybrid-e-r8-261103/tmp
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-e-r8-261103/tmp" python3 -B -I calc/tests/r16_audit.py
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-e-r8-261103/tmp" python3 -B -I -m unittest discover -s calc/tests -p test_run16.py -v
```

Outputs: `calc/out/run16/{base,bounded_undo}/`, `INDEX.json`, the old/new
`calc/ENGINE-QUOTES-R16-261103.csv`, and
[`calc/ENGINE-REPORT-R16-261103.md`](calc/ENGINE-REPORT-R16-261103.md).
`r16_audit.py --audit-only` checks source/output identities, all 608 frozen
files, priority qualification and quote coverage. See
[`calc/README.md`](calc/README.md#run-16-priority-qualified-single-streams-and-prototype-depth-import)
for the data-only R16b sweep interface, threshold semantics and validation.

## Paper v4 validation and counts

Run the CPU-only engine suite with `python3 -B -m unittest discover -s calc/tests`,
the kit suite with `python3 -B -m unittest discover -s bench/tests`, and the two
publication checkers with `python3 paper/data/check_ranges.py` and
`python3 paper/data/offload_bound.py`, each also with `--self-test`.
Run `python3 calc/tests/publication_v2.py`, `python3 calc/tests/r13_ledger.py`,
`python3 .scripts/publication_spacing.py`, `bash .scripts/test-release.sh` and
`bash .scripts/test-release-signatures.sh`. The v4 regression tests are in
`calc/tests/test_paper_v4.py`; old reviewer test names remain present.

The exact engine snapshot is `calc/out/run16/base/`; `paper/data/arch_compare.py`
projects its f32 architecture rows into the existing native CSV format, while
`python3 paper/data/derive_charts.py` rebuilds the five chart inputs. The bounded
undo case stays in `calc/out/run16/bounded_undo/` as future-work sensitivity.
Source facts are pinned in `data/measurements/paper-v4-2026-11-03/FACTS.md`.
The gap map and complete numeric delta inventory are
`calc/PAPER-V4-GAPS-261103.md` and `calc/PAPER-V4-NUMBERS-261103.csv`.

Use disk-backed `TMPDIR` and `PYTHONDONTWRITEBYTECODE=1`; logs, gate receipts,
the before/after lexical counter and its counting definition are under
`.temp/hybrid-c-r20-261103/`. The cache-only build is
`make pdf TECTONIC="$PWD/.temp/paper-v2-261101/tectonic-cached"`, followed by
`make manifest`. Build outputs stay in `build/` and `dist/`; the owner copy is
`.temp/hybrid-c-r20-261103/hybrid-inference-v4-draft.ru.pdf`.

## Paper v4b owner follow-up

The owner revoked the length/no-growth target; title, thesis, authors and release version stay unchanged.
Every non-superseded result is retained. The restoration audit, four pending sites, character-count definition,
source-row arithmetic and validation receipts are in `calc/PAPER-V4B-GAPS-261103.md`.
Current FACTS (including Sergey's priority answer) and the independently recomputed prefill distribution are in
`data/measurements/paper-v4b-2026-11-03/`. Accepted R16 exports, quotes and historical fixtures remain unchanged;
the newer priority answer supersedes their owner-reported-priority label in current paper prose.

Tool: `python3 -B -m unittest discover -s calc/tests -p test_paper_v4b.py` checks the 1920/1921 character boundary,
source-selected per-team light-load directions, geometry/time accounting, priority qualifications and every pending site.
The same full v4 gates listed above apply. Logs, the unchanged lexical counter, counting receipts and the cache-only
owner PDF are under `.temp/hybrid-c-r20b-261103/`; PDF filename: `hybrid-inference-v4b-draft.ru.pdf`.
The abstract character count includes spaces in the plain body, excluding the typeset label; a separate conservative
TeX-body count includes source escapes. Both must stay within 1920.

Engine run17 adds measured sliding-window geometry for Glimmer 30B and Gemma 4
31B, finite link thresholds, a labelled architecture extrapolation and paired
Qwen bf16 wire economics. See [the R17 report](calc/ENGINE-REPORT-R17-261103.md)
and [Run17 tools](calc/README.md#run17-tools). CPU exporter:
`python3 -B -I calc/tests/r17_audit.py`; outputs stay under `calc/out/run17/`.
Use an on-disk `TMPDIR` and `PYTHONDONTWRITEBYTECODE=1`. Prior exports remain
frozen. Mac SWA rates remain `background_priority_interim`. The accepted dev-a r38 CPU bf16
transport evidence is archived below; GPU/Mac quality and speed remain pending.

## Paper v4c validation and source boundaries

Accepted engine 17 `714fe72135819ededd7c270dd661c1359acfa6c3` is merged with signing.
Main R16 diagnostic/economic snapshots keep their named calibration; five byte-exact architecture inputs from
`calc/out/run17/architectures/` are also pinned in `paper/data/engine17/`. The paired economics sensitivity uses
the frozen `calc/out/run17/{f32,bf16}/` cases. SWA thresholds remain background-priority interim with the named
Qwen-import portability estimate. The architecture S/K table is an extrapolation, not a real-model claim.
`python3 paper/data/arch_compare.py` now carries the complete live window and writes `paper/data/arch-compare.csv`;
its operation-scaled rates remain explicit estimates, separate from measured-rate thresholds.

Tool: `python3 -B -m unittest discover -s calc/tests -p test_paper_v4c.py` verifies raw accounting/chunk sums,
full-window geometry, depth-dependent comparisons, loss/measurement boundaries and the six pending sites.
The required full engine/kit/checker/self-test/publication/release/PDF/manifest commands remain listed above.
No prototype model/native build is run: accepted CPU evidence at `64dc3c69` is archived with the precise
time-accounting report, its raw local inputs and current FACTS in `data/measurements/paper-v4c-2026-11-03/`.
Pending GPU/Mac bf16 measurements and timing-only runs are explicitly owner-requested additions to FACTS 5 waits.

The word counter is corrected to retain escaped currency signs: the older regex treated `\$` as math delimiters.
Both r20b base and v4c are recounted with the same corrected definition; legacy counts are disclosed separately.
Counts, old/new/source numbers, gates, pending map and finite limitations: `calc/PAPER-V4C-GAPS-261103.md`.
Logs/counters/receipts are in `.temp/hybrid-c-r20c-261103/`; the owner PDF is
`.temp/hybrid-c-r20c-261103/hybrid-inference-v4c-draft.ru.pdf`. Title, thesis, authors and release version stay unchanged;
no whole-paper length target, push or tag.


## Paper v5a validation and deferred costs

The accepted base is `paper-v4` at `4ee9a9a52a39b29d084a5c384d5f6445ec33adfd`.
R16/R17 exports, historical fixtures and kit code remain unchanged. R20 `b6ac5abc` is read-only;
`calc/tests/data/paper-v5a-r20-sites.json` binds every `% R20:` amount to its future export and scope.
No R20 output is merged or presented as an accepted result. RTX 5090 is a client only.

Tool: `python3 -B -m unittest discover -s calc/tests -p 'test_paper_v5a*.py'` checks raw RULER analyses,
FACTS client rows, rate/cache arithmetic, current pending/deferred sites, semantic TTFT labels and the six r5u notes, the r5y finding/notes and accepted second-pass data. The technology guard now includes only the current `[Unreleased]` changelog section; new negative controls plant each forbidden label there while retaining released history.
`python3 -B paper/data/check_ranges.py --self-test` keeps the 156 numeric/direction controls at their moved historical sites;
`python3 -B paper/data/offload_bound.py --self-test` checks old and new named measurement/qualification sites.
`python3 -B calc/tests/publication_v2.py` pins the exact current paper and `paper-v5a4-migration.json` binds authorized
historical deltas without modifying original fixtures. All full gates are rerun at one frozen signed head; older receipts are not reused.

Current inputs and source identities: `data/measurements/paper-v5a3-2026-11-03/` and retained `paper-v5a2-2026-11-03/`, extending the retained `paper-v5a-2026-11-03/` snapshot. `test_paper_v5a2.py` recomputes primary-result cells from accepted producer JSON, reads paired document KL intervals, checks literal PRI 31 cells, interpolation and server rebuild arithmetic. Every new semantic site has an applied omission control. The current finite pending inventory is `calc/tests/data/paper-v5a4-pending.json`; the 26 R20 bindings are unchanged.
Gap, relocation, six-note and pending maps: `calc/PAPER-V5A-GAPS-261103.md`.
Run receipts, PID/exit logs, disk `df` probes, counters and addressed-summary readback:
`.temp/hybrid-c-r21d-261103/`. Requested owner PDF:
`.temp/hybrid-c-r21d-261103/hybrid-inference-v5a3-draft.ru.pdf`.
CPU only, no downloads/native builds/push/tag; disk TMPDIR and `PYTHONDONTWRITEBYTECODE=1`.
The third-pass guard records `df -BG` and exact bytes, waits up to 20 minutes below 28.5 GiB (30,601,641,984 bytes), checks every two minutes, and keeps a 28 GiB floor; no foreign scratch is deleted.

The third-pass `test_paper_v5a3.py` checks the exact `18d3f114` runbook, full M5 FACTS ladders/batching and source arithmetic, post-result margin scope, exploratory Glimmer, lossy-bf16 boundaries and excluded cache-probe controls. Current M5 measurements record PRI 31; the retained run16 daily-capacity/economics still use their original M5 inputs and are explicitly historical, awaiting accepted engine run 22. No new engine output is merged. Outputs and negative-control receipts stay in the task directory above.

## Paper `v5a4` owner review

Current evidence and current semantic views: `data/measurements/paper-v5a4-2026-11-03/`.
Tool: `python3 -B -m unittest discover -s calc/tests -p test_paper_v5a4.py` checks
completed bf16/Glimmer RULER scope, warm restore, useful download arithmetic,
RTX 5090 boundaries, M4 archival scope, finite-depth measured server batching,
abstract budgets, raw R20 custody and consolidated rendered notices. Each new
finite claim has a named applied negative control. Earlier test names remain.
English arXiv text: `paper/abstract.en.txt` (at most 1650 characters); rendered
Russian abstract at most 1670 characters, leaving at least 250 under arXiv 1920.
The full required gate commands above are rerun against one frozen signed head.
All command exits and disk preflights: `.temp/hybrid-c-r21e-261103/`;
owner PDF: `.temp/hybrid-c-r21e-261103/hybrid-inference-v5a4-draft.ru.pdf`.
Raw inventory contains 40 macro sites, including 20 inactive repeated amount hooks;
20 sites remain visible. All 26 R20 export/body signatures are unchanged.
One central notice replaces four repeated applicability paragraphs; no deferred
engine run 22 amount is filled. The counted abstract/words skip the explicit inactive
hook blocks. Complete run14 million-token modelling is preserved in appendix C.

Engine run18 adds RTX 3090/5090 Qwen/Glimmer clients, hard context limits,
link thresholds and one ephemeral Qwen rental comparator. See the
[R18 report](calc/ENGINE-REPORT-R18-261103.md) and
[Run18 tools](calc/README.md#run18-tools-and-outputs). Exporter:
`python3 -B -I calc/tests/r18_audit.py`, with disk `TMPDIR` and
`PYTHONDONTWRITEBYTECODE=1`. Outputs stay in `calc/out/run18/`; prior exports
remain frozen. Conditional workload coverage and repeated fetch/cold costs are
explicit; no persistence or current market-rate claim is assumed. CUDA import
now uses a joint PR 9 delta/depth fit with a refitted intercept; native full-slot
file timings remain diagnostics. The report explains that fallback and the
changed link thresholds.

Run18 CUDA rework validation: 404 engine tests, 26 focused tests and 24 kit tests
pass; the reviewer’s original two-test reproduction passes. All 907 historical
export files and the rental comparator retain exact bytes. Resource-floor
breaches and interrupted attempts remain disclosed in the R18 report; the
successful rework retry sampled at least 29.533 GB free, while the overall
rework minimum was 27.867 GB.


Engine run19 adds an RTX 5090 prefill node for office and rental scenarios,
measured-rate thresholds versus PRO6000, bounded residency/swapping, and
same-mix backend costs for 5/50/500 staff. See the
[R19 report](calc/ENGINE-REPORT-R19-261103.md) and
[Run19 tools](calc/README.md#run19-tools-and-outputs). The r10c base review
was pending at branching. Prices distinguish a sold-out card listing from an
estimated host allowance. Costs cover the explicitly conditioned measured
workload, not an unsupported full-mix closed perimeter. Export with
`python3 -B -I calc/tests/r19_audit.py`, using disk TMPDIR and
PYTHONDONTWRITEBYTECODE=1; prior exports stay frozen.

Run19 validation passes 420 engine tests, 16 focused tests and 24 kit tests.
All 917 historical export files remain byte-identical; live recomputation
matches 13 published payloads. The observed run19 disk minimum is 28.856 GB.

Engine run20 adds measured vLLM server economics, memory-limited decode
batching, small teams and admitted API snapshot baselines. See the
[report](calc/ENGINE-REPORT-R20-261103.md),
[standalone batching figure](calc/out/run20/batching_gain.svg), and
[tools/data-only interfaces](calc/README.md#run20-tools-and-data-only-interfaces).
Historical runs 13–19 are frozen. Costs are conditional on the shared measured
workload; provider cache behaviour, bridge portability and future decode
measurements remain explicit qualifications. The run's shared-disk 28 GB-floor
breach is preserved in its report.

Engine run21 adds a Claude-only deep workload reconstruction alongside the
unchanged combined profile, and a million-token scenario on the run20 vLLM
bases. See the [R21 report](calc/ENGINE-REPORT-R21-261103.md) and
[commands and data interfaces](calc/README.md#run21-tools-and-data-only-interfaces).
Only PRO6000 and B300 servers enter the new comparisons; historical run20
5090 server rows are not used in the paper. Runs 13–19 remain immutable; R14 authorizes label-only R20 republication. The
run19 rental coverage correction is published as a successor view under run21
and in the generator source, with every numeric cell preserved.

The r5x publication rework adds scoped, 5090-free paper projections for both
[R20](calc/out/run20/paper/) and [R21](calc/out/run21/paper/).
Use those for quotations; full R20 numerical cells are preserved, with archival
5090 server rows labelled not used in the paper. See the reports for PRO
small-team costs, per-load crossings and separately named shared/dedicated
multiples, and [publication commands](calc/README.md#r14-publication-tools).

The `r5x2` sentence rework makes all paper conclusions self-contained: billing,
server link/rate/RTT/location, client, s, cache allowance, load and coverage
travel with each sentence. The [R15 cell diff](calc/ENGINE-SENTENCE-DIFF-R15-261103.csv)
contains only sentence changes; numerical cells are preserved.
[Commands and checks](calc/README.md#r15-sentence-tools) use the 28 GiB disk floor.

Run22 RC 4 economics use the [CPU-only run22 exporter](calc/run22/README.md):
`python3 -B -I calc/run22/export.py` writes `calc/out/run22/` and its paper
projections; `--audit-only` verifies sources, historical bytes and quotations.
It keeps bf16 transport as the default and the dedicated team server as the
primary economic basis. See `calc/ENGINE-REPORT-R22-261103.md` for results.

## Paper v5b economics

Accepted engine run 22 `9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0` is integrated by a signed local merge,
including unchanged run 18 through 21 dependencies and historical exports. Current quotations use
`calc/out/run22/paper/`; the accepted exporter, report and complete ledger remain byte-identical.
Tool: `python3 -B -m unittest discover -s calc/tests -p test_paper_v5b.py` checks row selection,
dedicated costs and both occupancy denominators, sustained finite crossings, API cache points/windows,
1M client-specific estimates, the empty direct-Mac interface, and all 26 deferred-site dispositions.
Narrowing controls and finite limits: `calc/PAPER-V5B-GAPS-261103.md`.
Current pending inventory: `calc/tests/data/paper-v5b-pending.json`; former R20 bindings remain immutable
historical evidence, with every accepted successor in `data/measurements/paper-v5b-2026-11-03/r20-migration.json`.
The publication guard pins accepted engine source/output identity in addition to every current paper byte/number.
Russian abstract limit 1920 characters, English `paper/abstract.en.txt` limit 1800; the earlier temporary
250-character reserve is superseded by the accepted economic sentences.
Fresh exact-head gate exits, disk probes, counters and delivery receipts: `.temp/hybrid-c-r21f-261103/`.
Owner PDF: `.temp/hybrid-c-r21f-261103/hybrid-inference-v5b-draft.ru.pdf`.
Historical v5b whitespace evidence used three exact verbatim FACTS excerpts. The current `v5d8`/`v5d9`
check covers the entire paper/provenance content delta after accepted engine merges. A raw whole-base
`git diff --check` exits 2 on five byte-identical accepted run26 vendor/source snapshots; the failed
receipt is retained. Native-byte audits verify those snapshots against accepted engine 26; no engine
input, computation or output is reformatted to satisfy a whitespace check.

No downloads, native builds, push or tag. Disk TMPDIR and `PYTHONDONTWRITEBYTECODE=1`; every gate checks
`df -BG` and exact bytes, waiting up to 20 minutes below 28.5 GiB, with a 28 GiB hard floor.
Run23 replaces the deep Mac timing and PRO6000 decode estimates with the
[accepted night inputs](calc/run23/README.md). `python3 -B -I calc/run23/export.py`
writes `calc/out/run23/` and its paper projections;
`python3 -B -I calc/r23_report.py` publishes the report and quotation audit.
All run13–22 exports remain byte-identical.


## Paper v5c measurements and run 23

Signed integration of accepted `9064701a9a07bd2726f76cefb6a05aa6aa428c0d` preserves prior engine exports.
Current paper quotes `calc/out/run23/paper/` and the named FACTS blocks archived in
`data/measurements/paper-v5c-2026-11-04/`. Direct Mac native timings, finite same-GPU depth quality,
measured PRO decode/interpolation and model/proxy limits are checked with
`python3 -B -m unittest discover -s calc/tests -p test_paper_v5c.py`.
The publication guard additionally pins the accepted run 23 source/output identity; earlier source pins remain.
Current wait inventory: `calc/tests/data/paper-v5c-pending.json`.
Source/coverage/mutation boundaries: `calc/PAPER-V5C-GAPS-261104.md`.
Fresh gate logs and source/count receipts: `.temp/hybrid-c-r21g-261104/`.
Owner PDF: `.temp/hybrid-c-r21g-261104/hybrid-inference-v5c-draft.ru.pdf`.
The Russian/English abstract budgets remain 1920/1800 characters; no length cuts.
CPU only, cache-only build, checkout TMPDIR, no downloads/native builds/push/tag; disk launch threshold 28.5 GiB.


## Paper v5d part 1 measurement update

Current source archive and wording contracts: `data/measurements/paper-v5d1-2026-11-05/`.
The capped ordinary-priority M3 grid, fixed-journal bf16 rehearsal and descriptive final API study are checked with
`python3 -B -m unittest discover -s calc/tests -p test_paper_v5d1.py`.
Native accepted engine run 23 source/outputs remain exact; run 24 and measured-cache economics are deferred to part 2.
Scope, stopped RULER reason and narrowing controls: `calc/PAPER-V5D1-GAPS-261105.md`.
Current macro inventory: `calc/tests/data/paper-v5d1-pending.json`.
Fresh exact-head gate/disk/count receipts: `.temp/hybrid-c-r21h-261105/`.
Owner PDF: `.temp/hybrid-c-r21h-261105/hybrid-inference-v5d1-draft.ru.pdf`.
Russian/English abstract limits remain 1920/1800 characters. No length cuts, downloads, native builds, push or tag.

## Paper v5d part 2: partial RULER and nonadmitted measured API

Current evidence and successor wording contracts: `data/measurements/paper-v5d2-2026-11-05/`.
Saved Qwen RULER serial prefixes (368/390 and 225/390) stay separate from registered analysis; both depths entered as pending at p=1 in that superseded snapshot. All measured Qwen 1M providers fail the 95% whole-window rule; descriptive prices are not admitted economic figures. Engine run24 economic use is deferred.
The existing private repository is `relux-works/hybrid-inference-data`; the full evidence snapshot will be uploaded after RC 4.

Tool: `python3 -B -m unittest discover -s calc/tests -p 'test_paper_v5d2.py'` checks source custody, incomplete-depth fences, task gaps, availability admission and snapshot status.
Current pending inventory: `calc/tests/data/paper-v5d2-pending.json`; gap/negative-control map: `calc/PAPER-V5D2-GAPS-261105.md`.
All earlier data archives, native engine outputs and reviewer test names are retained. Exact-head receipts, counts and owner PDF are under `.temp/hybrid-c-r21i-261105/`.

Run24 adds the [final measured API cache/availability points](calc/run24/README.md)
on the accepted run23 costs. `python3 -B -I calc/run24/export.py` writes
`calc/out/run24/`; `python3 -B -I calc/r24_report.py` publishes the report and
quotes. Historical run13–23 exports stay byte-identical.

## Paper v5d part 3: RC 4 measured-cache economics

Accepted engine run 24 is integrated without rewriting any previous export. Three API cache points stay separate by cadence and priceable cohort. Qwen core remains unavailable; the descriptive Ionstream minimum has one warm observation. Source hit fractions are transferred to the paper workload by assumption. All ten attempted endpoints below 95% whole-window availability are excluded.

Current source/wording contracts: `data/measurements/paper-v5d3-2026-11-05/`.
Tool: `python3 -B -m unittest discover -s calc/tests -p 'test_paper_v5d3.py'` checks exported prices/crossings, cadence/cohort scope, availability and current completion status. Existing native `calc/run24/export.py` and `calc/r24_report.py` tools are documented above and in `calc/run24/README.md`. Publication guard now pins accepted run 24 while retaining all prior authority checks.
Current pending inventory: `calc/tests/data/paper-v5d3-pending.json`; gap/mutation map: `calc/PAPER-V5D3-GAPS-261105.md`. Exact-head gates, counts and owner PDF are under `.temp/hybrid-c-r21j-261105/`. The original owner-set data cut-off was 2026-11-05 12:00Z; the RULER waits in this historical section are superseded by the completed analysis below. Remaining headline items include B300 decode and an admitted measured Qwen 1M point. Private `relux-works/hybrid-inference-data` exists; full evidence snapshot follows RC 4. No push or tag.

### RC 4 review precision pass

The v5d part-4 scope and pending map are in `calc/PAPER-V5D4-GAPS-261105.md`.
Run its publication regressions with `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s calc/tests -p test_paper_v5d4.py`.
The existing checkers also enforce explicit claim relocations from `data/measurements/paper-v5d4-2026-11-05/`;
older evidence snapshots stay immutable. Run logs, disk preflights, counts and the owner PDF go to
`.temp/hybrid-c-r21k-261105/`; no provider or device remeasurement is implied by these CPU checks.

### RC 4 analyst abstract and workload-class pass

Current scope: `calc/PAPER-V5D5-GAPS-261105.md`. Sources and exact abstract successors:
`data/measurements/paper-v5d5-2026-11-05/`. Run the focused checks with
`PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s calc/tests -p test_paper_v5d5.py`.
Logs, counts and the owner PDF go to `.temp/hybrid-c-r21l-261105/`.
These CPU publication checks preserve the accepted native engine and earlier measurement archives.


## Public release provenance tools

The public owner recommits each release as one commit. Private engine/paper
commits are therefore evidence identifiers rather than public ancestors.
`calc/history_evidence.py` authenticates the in-tree historical content and
SHA256/blob/mode/path inventory in `calc/tests/data/history-evidence/`.
When original objects exist, every requested value is checked against Git;
otherwise the checker explicitly prints fixture mode. No fetch or skip is used.
Historical producer identities remain distinct from the nine exact pinned
verification adapters; numerical functions and accepted exports are unchanged.

- `python3 -B calc/tests/check_history_evidence.py` verifies the complete archive
  and cross-checks all available original revisions.
- `python3 -B .scripts/generate-history-evidence.py --check` reproduces the
  fixture from local private history; omit `--check` to regenerate it.
- `python3 -B calc/tests/public_history_guard.py` rejects unreviewed direct Git
  accesses in test/checker scopes. The regression suite plants a private
  `git show` and requires this same guard to reject the plant.
- `python3 -B .scripts/generate-public-git-catalog.py` updates the explicit
  reviewed Git-access catalogue after a deliberate provenance-tool review.
- `python3 -B .scripts/simulate-public-layout.py .temp/public-layout` builds
  isolated public ancestry/tree/index metadata, reusing this physical worktree.
  It copies no blobs, uses no alternates and excludes all private commits;
  the resulting `environment.json` selects this metadata for source-repo Git
  operations while temporary test repositories retain their own real Git.
- `python3 -B -m unittest discover -s calc/tests -p test_history_evidence.py`
  checks fixture corruption, original-object comparisons, adapter boundaries
  and the private-lookup negative. Full engine and kit commands stay unchanged.

Generators require original objects only when explicitly rebuilding fixtures.
Runtime tests and release proof require Python's standard library and Git;
release-signature fixtures also require Bash, OpenSSH `ssh-keygen` and SHA256
utilities. No Python dependency installation is needed. Logs and transport
proof artifacts belong in the task's `.temp/` delivery directory.

### RC 4 analyst and external-review corrections

Sources and exact publication successors: `data/measurements/paper-v5d6-2026-11-05/`.
Pending scope: `calc/PAPER-V5D6-GAPS-261105.md`.
Run `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s calc/tests -p test_paper_v5d6.py`.
Full CPU gates, counts and owner PDF are recorded in `.temp/hybrid-c-r21m-261105/`.
No native engine output or historical measurement fixture changes in this pass.

The finite overlapping checker-control ledger is regenerated explicitly with
`PYTHONDONTWRITEBYTECODE=1 python3 -B .scripts/generate-paper-self-test-couplings.py`.
It writes the current `data/measurements/paper-v5d8-2026-11-05/self-test-couplings.json` and its checker hash pin.
The generator uses declared literal paragraphs, never the checker verdicts; `offload_bound.py --self-test`
still requires every exact diagnostic and rejects missing or additional ones.

### Conditional closed-perimeter model map

Source decisions and finite successors: `data/measurements/paper-v5d7-2026-11-05/`.
Run `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s calc/tests -p test_paper_v5d7.py`.
Full CPU gates and PDF/count artifacts: `.temp/hybrid-c-r21n-261105/`.
Current pending and old/new scope map: `calc/PAPER-V5D7-GAPS-261105.md`.

### Accepted engines and lifecycle methods

Current sources, explicit claim successors and pending scope: `data/measurements/paper-v5d8-2026-11-05/`
and `calc/PAPER-V5D8-GAPS-261105.md`. Run
`PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s calc/tests -p test_paper_v5d8.py`.
Fresh CPU gates, the owner PDF and counts live in `.temp/hybrid-c-r21o-261105/`.

New engine parent audits authenticate original snapshots plus exact intentional paper migrations.
`python3 -B .scripts/generate-engine-parent-migrations.py` rebuilds
`calc/tests/data/history-evidence/engine-parent-migrations.json` and its gateway pin.
Run this explicit authoring step after an authorized paper or release-version change, before
`make manifest`; the current manifest independently verifies every tracked path and content hash.
It cannot authorize changes to calculation code. Original run-25/26 audit code is retained in the
history fixture; three live provenance adapters have their own exact hash pins.

## Paper `v5d9` post-review evidence and arithmetic

Current evidence: `data/measurements/paper-v5d9-2026-11-05/`, with content custody, finite successors,
architecture/start-capacity arithmetic and the partial Mac calibration. `python3 -B -m unittest discover -s calc/tests -p test_paper_v5d9.py` checks these contracts. Current pending inventory:
`calc/tests/data/paper-v5d9-pending.json`; limits/corrections: `calc/PAPER-V5D9-GAPS-261105.md`.
Export/codec/append controls exclude the earlier vLLM append localization; long sessions remain
unqualified, with a one-document natural-text diagnostic measured. The pre-probe stage 1 prediction is committed,
not an inference result; a second commitment follows the qualified actual probe before inference.
Glimmer save-size ratios include SWA; traffic separates global KV and a live window for every exchange.
At 0.9 GB the ideal 125 MB/s daily link budget is 12,000 contexts, not 11,000; 11,000 uses the conservative 1 GB point.
CPU/cache-only gates, exact argv/head/exit codes, owner PDF and counts: `.temp/hybrid-c-r21p-261105/`.

## Paper `v5d10` near-ties, dates and natural-text attempt

Current evidence and arithmetic: `data/measurements/paper-v5d10-2026-11-06/`. Current pending
inventory: `calc/tests/data/paper-v5d10-pending.json`; scope and review notes:
`calc/PAPER-V5D10-GAPS-261106.md`. Run `python3 -B -m unittest discover -s calc/tests -p test_paper_v5d10.py`.
Run-16 scratch-path portability: `python3 -B -m unittest discover -s calc/tests -p test_r16_audit_paths.py`.
The logical changed-cell sources stay identical, including when exports are outside the stand-in root.
Greedy near-ties explain numerical answer changes; the verified content-flip rule only gives a lower bound.
The natural-text workload amendment preceded attempt 5; its fourth turn refuses the unchanged top-1
criterion. The same-format llama.cpp path remains qualified. Pending softcap tests require exact
prompt reconstruction or a separately declared new dataset. All 128k passages remain unchanged.
Fresh CPU/cache-only receipts and owner PDF: `.temp/hybrid-c-r21q-261106/`.

## Paper `v5d11`: completed RULER

Current RULER evidence is `data/measurements/paper-v5d11-2026-11-06/`; current pending inventory
is `calc/tests/data/paper-v5d11-pending.json`, with scope in `calc/PAPER-V5D11-GAPS-261106.md`.
Earlier dated RULER pending/registration statements are historical snapshots superseded here.
The release data cut-off is 2026-11-06 06:00 UTC, after both deep completions and natural-text
vLLM attempt 5. Score equivalence at the frozen two-point margin is supported at 8k/32k/64k;
the 128k claim is withheld by the conservative guard. Text equivalence fails at every measured depth.
bf16 score claims cover 8k/32k only; 64k/128k bf16 was never measured.
Run `python3 -B -m unittest discover -s calc/tests -p test_paper_v5d11.py`.
Exact-head CPU/cache-only gates, PDF and counts: `.temp/hybrid-c-r21r-261106/`.

### Interpreter and reproduction contract

The reference interpreter for published calculation bytes is **CPython 3.14.4**,
which uses exact `bytes` regeneration mode. Other CPython versions use declared
`ulp` mode with at most two `binary64` steps in reference-typed finite float cells.
The signal-test child resets SIGINT and SIGTERM before Bash starts, retaining
exit 130/143 and cleanup assertions under inherited ignored signals.
A release candidate is proven from fresh public clones in three launch shapes:
reference CPython 3.14.4 with default signals, CPython 3.12.3 with default signals,
and reference CPython 3.14.4 with SIGINT and SIGTERM ignored. The proof clears `PYTHONOPTIMIZE` and requires 42 distinct automatic
filenames in announcements of the resolved mode and none of the opposite mode in the engine log.
Python 3.9 syntax is checked; native 3.9–3.11 and 3.13 are unqualified.
No third-party Python package is required by the paper suites.

Fresh CSV regeneration compares every byte on the reference interpreter. Other
interpreters use an announced comparison with at most **two `binary64` steps** in
canonically spelled finite float fields from the pinned reference schema. Every other field byte,
header, order, delimiter and newline remains exact. Published export hashes,
provenance fixtures, same-interpreter serialization round trips and historical
formatted transcripts remain byte-exact on every interpreter. See
[`calc/README.md`](calc/README.md#portable-regeneration) for commands and limits.

## Compressed accepted quote ledgers

Only the two quote ledgers for engine runs 22 and 23 use deterministic single-member
gzip (level 9, no filename, timestamp zero). Their accepted decompressed sizes and
SHA256 values, original revision/blob provenance and committed gzip SHA256 values
are pinned in `calc/ledger-storage.json`. Every reader uses `calc/ledger_storage.py`;
`python3 -B .scripts/generate-ledger-storage.py --check` checks the transform and
cross-checks accepted Git originals when available. Without `--check`, the generator
rebuilds gzip from local accepted Git objects; no fetch is performed. Regeneration
compares accepted decompressed bytes, retaining an existing authenticated gzip to
avoid interpreter/zlib-dependent compressed-byte comparisons. Other CSVs keep their
existing representation. The release proof checks every introduced blob, including
intermediate commits: at least 100 MiB fails; over 50 MiB prints a warning.

Historical custody and the current manifest authenticate the exact committed gzip.
Exporter text reads and fresh regeneration compare accepted decompressed content,
including when no prior gzip exists; valid compressor-byte differences never
relax the independent committed-blob custody check.

## RC 4 incident-lane rebuild

Release source follows accepted `v5d12`, including the corrected 128k departure identities.
The public-parent signed transport contains only the release tree and the public rc.3 ancestry; no private producer commits are transported. The git bundle is streamed twice for repeatable digest/size and never stored on `agents1`. Verified in-tree evidence retains private provenance without runtime access to private history; `.scripts/generate-history-evidence.py --check` authenticates available originals, and `.scripts/simulate-public-layout.py DIR` exercises public-only metadata with no blob copies or alternates.

Native `.scripts/version.sh` and the owner signer/ancestry checks are unchanged. The untagged source PDF is diagnostic; the correctly labelled release PDF and SHA256SUMS must be rebuilt after the owner recommit and signed tag. No source-lane push or tag is performed.
