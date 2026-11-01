# Hybrid inference: architecture and economics (working repository)

Working repository for the paper «Hybrid Inference with Client–Server Prefill–Decode Disaggregation: Architecture and
Economics for Unified-Memory Clients». Authors: Ivan Oparin and Alexey Grigoriev (Relux Works).

The idea: a GPU server prefills an agent session and ships the model state (attention KV of the new positions plus the
fixed recurrent state) to a unified-memory client such as a Mac, which decodes locally.

Status: a draft heading for version 0.1.0 (versions `0.y.z` are drafts; see below). The Russian text, the calculation
engine (`calc/`, runs 1–10) and the data behind every number of the paper are in place. Version 0.1.0 is released
after the scheme has been checked on GPU hardware. The prototype lives in a separate repository,
[`relux-works/hybrid-inference`](https://github.com/relux-works/hybrid-inference).

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
Run `python3 calc/tests/r10_controls.py` to check against the pinned R9 git
baseline; `--diff PATH --added PATH` writes per-file counts and added rows.

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
| R10 CSV byte audit (Python + local Git) | Verifies R9 rows are unchanged and only team 20 is added | `python3 calc/tests/r10_controls.py --diff calc/ENGINE-DIFF-R10-261031.csv --added calc/ENGINE-CHANGES-R10-261031.csv` | `calc/ENGINE-{DIFF,CHANGES}-R10-261031.csv`; logs in `.temp/hybrid-calc-r10-261031/` |
| `unittest`, `compileall` | Engine tests and syntax validation | `python3 -m unittest discover -s calc/tests`; `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | `.temp/` logs; ignored bytecode |
| Tectonic (optional cached CSV smoke) | Checks pgfplots can read all 42 design/conservative chart CSVs | From `calc/tests`: `tectonic --only-cached --outdir ../../.temp/hybrid-calc-r9-261030/pgfplots paper_r9_smoke.tex` after creating the directory; `paper_tables_smoke.tex` covers R5 | `.temp/` PDF and captured command log |
| `paper/data/*.py` | Rebuild the paper's chart inputs, architecture table and the owner's API bill; check, against the engine snapshot in `paper/data/engine/`, the figures and stated directions at the sites listed in `SITES` and `DIRECTION_SITES` of `check_ranges.py` (abstract, economics and million-token sections, conclusion, appendix), the client and closed-perimeter table rows, and with a guard over all sections any occurrence of a checked figure's printed form outside those sites; `check_ranges.py` also reads the engine inputs it names from `calc/hybridcalc/data/` (eligibility rule, storage prices and hours). `offload_bound.py` checks the offload-bound example | `python3 paper/data/derive_charts.py`; `python3 paper/data/arch_compare.py`; `python3 paper/data/year_bill.py paper/data/owner-model-usage-2026-10-30.json > paper/data/year-bill-summary.json`; `python3 paper/data/check_ranges.py`; `python3 paper/data/offload_bound.py`; the last three also take `--self-test` | `paper/data/*.csv`, `paper/data/year-bill-summary.json`; stdout |
| `sha256sum` | Checks every tracked file against `MANIFEST.sha256`; after any change, `make manifest` rewrites the list | `sha256sum -c MANIFEST.sha256` | stdout |
| Run 11 audit (Python, local Git history) | Compare every publication numeric cell and all requested headline derivations against signed run 10 | `python3 calc/tests/r11_audit.py` | `calc/ENGINE-{CHANGES,DIFF,QUOTES}-R11-261101.csv` |
| Run 11 negative control (Python) | Plant the forbidden output-plus-reasoning base generation; expected exit 1 is the named output-mean assertion | `python3 calc/tests/r11_controls.py output_sum` | stdout/stderr; capture in `.temp/hybrid-calc-r11-261101/` |
