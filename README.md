# Hybrid inference: architecture and economics (working repository)

Working repository for the paper «Hybrid Inference with Client–Server Prefill–Decode Disaggregation: Architecture and
Economics for Unified-Memory Clients». Authors: Ivan Oparin and Alexey Grigoriev (Relux Works).

The idea: a GPU server prefills an agent session and ships the model state (attention KV of the new positions plus the
fixed recurrent state) to a unified-memory client such as a Mac, which decodes locally.

Status: private draft, 2026-10-30. The paper text is not written yet; the calculations, sources and the prototype
specification are. Everything here is open-source material in preparation. Choose the licences before the repository
is made public; the proposal is CC BY 4.0 for text and Apache-2.0 for code.

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
| `calc/` | Cost and capacity models. Python 3 standard library only; each `*.py` writes the matching `*.out` |
| `data/research/` | Source notes from October 2026, each item tagged [fact] with URL and quote, [estimate] or [unverified] |
| `data/measurements/ivmbp-2026-10-30/` | Aggregate statistics of the author's agent sessions (Claude Code, Codex, Muse), as delivered: no transcripts |
| `docs/prototype/` | Prototype plan and technical specification (v0.3) |
| `tools/` | Mac measurement scripts: prefill and decode benchmark by depth, and session statistics |

## Calculations

| Script | What it computes |
|---|---|
| `calc/hybrid_calc3.py` | Session model, Mac decode model, API prices, device × channel equilibrium |
| `calc/hybrid_calc4.py` | Own all-server cluster vs hybrid vs API: fleets, capex and opex, payback, scale, long contexts, devices, GLM tier |
| `calc/hybrid_calc5_equilibrium.py` | Team-size equilibrium for 1–3 regions |
| `calc/hybrid_calc6_edge.py` | FLOP per transferred byte, light laptops, phones |
| `calc/hybrid_calc7_realcalls.py` | Recalibration on the measured call mix (reads `data/measurements/.../stats.json`) |

Run, for example: `cd calc && python3 hybrid_calc4.py > hybrid_calc4.out`. Numbers marked as estimates in the outputs
are model results, not measurements.

## Measurement tools

Use Python 3 for local numeric session analysis and inference benchmarking; see
[`tools/README.md`](tools/README.md) for exact commands, private source coverage,
usage-event UTC date semantics and benchmark interpretation. For example:
`mkdir -p .temp/session-stats && python3 tools/agent_session_stats.py --auto --out .temp/session-stats/stats.json --coverage .temp/session-stats/coverage.json`.
Outputs belong under `.temp/`; coverage and per-call CSV stay private. Run the
Swift 6/Swift Testing fixtures with
`swift test --package-path tools/tests --scratch-path .temp/session-stats-build`.
The original delivered measurements remain under `data/measurements/`.

## Building the PDF

`make pdf` writes `dist/hybrid-inference-<version>.ru.pdf` and `dist/SHA256SUMS`. Intermediate files and the TeX log go
to `build/`. `make clean` removes `build/`, `dist/` and the generated `paper/version.tex`.

The build needs [tectonic](https://tectonic-typesetting.github.io) 0.17.0, the version CI uses. On Linux x86-64 or
macOS arm64, `PATH="$(.scripts/install-tectonic.sh):$PATH" make pdf` installs that build into a cache directory, after
checking its SHA-256 digest. The fonts come from `paper/fonts/`, so every machine sets the same glyphs.

| Tool | What it does | How to run |
|---|---|---|
| `Makefile` | Builds the PDF | `make pdf`, `make clean` |
| `.scripts/version.sh` | Version label from git tags; with `--tex`, the title-page version | Called by `make pdf` |
| `.scripts/release-check.sh` | Verifies the tag signature and release criteria, then extracts its changelog section | `.scripts/release-check.sh vX.Y.Z`; notes go to `build/release-notes.md` |
| `.scripts/install-tectonic.sh` | Installs the pinned tectonic and prints its directory | See above |
| `.scripts/test-release.sh` | Version, changelog, ancestry and SSH authorization tests; needs Bash, Git and OpenSSH `ssh-keygen` | `.scripts/test-release.sh`; disposable repositories and keys are removed on exit |
| `.scripts/test-release-signatures.sh` | Authorized signature control plus rejection fixtures for unsigned, lightweight, foreign-key, tampered-pin and related trust failures | `.scripts/test-release-signatures.sh`; disposable repositories and keys are removed on exit |
| Git / OpenSSH | Checks SSH tag signatures using the reviewed public pin | Called by `.scripts/release-check.sh`; temporary verification files are removed on exit |
| `.github/workflows/paper.yml` | Hosted `ubuntu-24.04` builds for pull requests and `main`; verified tags build and publish a draft-first GitHub Release | Automatic; PDF and `SHA256SUMS` go directly to the Release |
