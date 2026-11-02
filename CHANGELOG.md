# Changelog

Every paper version is a GitHub Release with the PDF. Versions follow [Semantic Versioning](https://semver.org) as
README.md defines it for the paper, in the section "Versions and releases".

## [Unreleased]

### Changed
- The paper is cut from 22 pages to 9 (7 of text) and keeps what states and tests the core idea: the server copies
  the model memory of new positions to the client, and what that copy costs and saves. The protocol section takes
  the delta and offload-rule formulas from the appendix; the channel section takes the offload bound; the prototype
  results, the trust model and the limitations share one section; economics keeps the client table, the purchase,
  the closed perimeter and the million-token context, each reduced to a paragraph.

### Removed
- Sections on clients and weight classes, model architectures, the million-token context, security, resilience and
  outlook, the appendix, and the figures and tables for teams, renting against buying, payback, model progress,
  the owner's yearly bill, one-shot ingestion and the transcript example. Heterogeneous quantisation, the patchwork
  cache and provider routing are dropped from the protocol.
- `paper/data/check_ranges.py` and `paper/data/offload_bound.py` follow the shorter text: the sites of removed
  figures and the closed-perimeter table are no longer checked.

## [0.1.0-rc.1] - 2026-11-01

A draft snapshot of the current text for review, published as a GitHub pre-release.

### Added
- Timur Kackan joins the authors.
- The Russian text of the paper: the client–server split of prefill and decode for long agent sessions, the channel it
  needs, clients and model architectures, the server side, economics against APIs and own clusters for teams of 5 to
  5000 people and an own RTX PRO 6000 server for teams of 5 and 20, contexts up to one million tokens, the trust
  model, resilience, limitations and related work.
- The calculation engine `calc/` (runs 1–11): provenance-bearing inputs, the measured call profile and the published
  tables. Generated tokens per call are the logged output, which already contains the reasoning; reasoning counted on
  top is kept only as a labelled upper bound. The paper's numbers come from its snapshot in `paper/data/engine/`.
- Scripts in `paper/data/` that rebuild the charts, the architecture table and the owner's per-model API bill, and
  that check, against the engine snapshot, the figures and stated directions at the sites the checker lists, the
  table rows, and any occurrence of a checked figure's printed form outside those sites, and the offload-bound
  example.
- Per-model usage export in `tools/agent_session_stats.py` 1.6.
- Licences: CC BY 4.0 for the paper, its data and the documents in `data/` and `docs/`; MIT for the code and everything
  else.
- Measurement kits in `bench/` for contributors, with one prompt for an agent (`bench/AGENT_PROMPT.md`): the
  Qwen3.8-27B long-context benchmark on Apple Silicon Macs (`bench/mac`) and on NVIDIA GPUs with the context sized
  to the card (`bench/gpu`), both pinned to the reference run's llama.cpp commit, model file and benchmark script;
  and agent-session statistics computed locally, only with the owner's consent (`bench/sessions`).

## [0.0.1] - 2026-10-30

### Added
- The release pipeline. A tag `vX.Y.Z` on `main` builds the PDF in CI and publishes it as a GitHub Release with
  `SHA256SUMS`.
- The title page of the Russian version. The paper text is not written yet.
