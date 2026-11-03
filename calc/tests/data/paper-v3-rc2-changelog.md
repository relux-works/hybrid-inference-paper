# Changelog

Every paper version is a GitHub Release with the PDF. Versions follow [Semantic Versioning](https://semver.org) as
README.md defines it for the paper, in the section "Versions and releases".

## [Unreleased]

## [0.1.0-rc.2] - 2026-11-02

A reviewed draft of paper v2 for publication as a GitHub pre-release. Compared with rc.1, this candidate adds
engine runs 13 and 14, measured client/server and bridge sections, and answers to the external review. Paper v2
at `1a45cd22` was accepted by Muse r5k with no findings; engine run 14 was accepted by r5i.

### Changed
- Integrated accepted engine run14 `2d457aed` with a signed merge; all110run14 exports plus report/quote/R14-R5
  payloads arrive unchanged and regenerate byte-identically. The current embedded snapshot changes42→61CSVs.
- Changed medium-load own-cluster savings from2.6–2.9→2.2–2.4times (cautious2.1–2.5→2.0–2.2).
  Removed the artificial500-person light-load jump; all team sizes optimize hardware/storage with equal retention
  and mean/p90budgets. The latency limit rejects0/2106candidates, so the comparison is cost-driven under equal retention.
- Changed the main team-size chart from fixed B300 versus shared prefill/API to the symmetric own/hybrid minimum
  at5/10/20/50/500/5000people; the separately labelled B300/API reference remains available.
- Changed M3 day gain1.57→1.52; M5 Max64 1.29→1.26, Max128 1.17→1.29, Ultra96 1.14→1.00 and Ultra256 1.10→1.00.
  M5 rows now use measured M5 Max curves and client import. Max128 decode13.0→18.3tok/s; Ultra25.9→36.6is an estimate.
- Added the seven-row full-mix agent-count table. Sixteen-agent gain1.732is modelled:77.7%of calls modelled in depth,
  and99.7%have at least one flag. Call/decode-time shares for all overlapping flags are printed adjacent to the row.
- Replaced peak-scaled B300 economics with measured llama.cpp rates. B300 prefill capacity127/50/25→27/11/5people
  at20/50/100%open share; ideal-client ceiling12.1→2.0times at110k. vLLM rates/costs remain server-only.
- Changed20%open-share hybrid/median savings2.5–3.8→1.2–1.5times and cheapest-API premium1.9–2.9→4.8–6.1times.
  Changed four-session GLM/API savings3.3–3.6→2.1–2.3times; full-load4.8–5.1→2.7–2.8times.
- Added the zero-prefill-price cost floor: measured clients at20%have no break-even against cheapest API because
  overheads alone exceed its bill. Preserved exceptions (M5 Max64 at50%:0.01558USD/MTok; estimated Ultra256 at20%:0.11649).
  Added median-API thresholds4.7–5.4USD/MTok and measured server-only unit costs; no universal impossibility claim.
- Replaced5G-prediction TODO with179.5s predicted versus201.7s observed and25.5s unallocated; Step57 model time
  under measured local time by8/22/37/33%is now stated in validation.
- Replaced31,360-token bridge TODO with heterogeneous uncalibrated KL0.0031BF16/0.0061Q4and64/64top1each.
  Replaced task-pilot TODO with35/48correct in every treatment,4/48offload and partition disagreements,0/48repeat,
  and partial128kcoverage; these observations do not establish task equivalence.
- Replaced node-adapter TODO after the orchestrator supplied the B300 smoke:8k KL0.0055/top1 63/64/noise ratio0.87;
  32k KL0.0256/top1 60/64/ratio2.38. Same-GPU timing is functional only, heterogeneous and uncalibrated.
- Fixed the four r5h style sentences and repinned their guards. Retained all156range sites and55old offload names,
  added snapshot/qualification controls, and migrated exact publication/numeric pins. The r11 B300 check replaced
  cross-profile uniqueness with a minimum, weakening its scope; r12 restores unique-row checks for the explicitly
  light-load, one-node reference. Numeric rounding is unchanged.
- Fixed the r5j traffic pronoun, qualified all three B300 $3,373/$845 sites as light-load one-node costs, and
  corrected the economics caption to measured M5 Max curves, same-SoC transfer to 128 GB and Ultra scaling.
  Added named regression, scope and planted-violation controls and repinned the authorized publication delta.

### Earlier candidate changes (run 13, before the run-14 updates above)

- Added measured parallel decode by depth and stream count, separating the restored 128k control, the post-prefill
  lower bound and request-time versus generation-interval rates. Added step57 realistic-agent speed, p90, prefill
  shares and long tool-output waits. Cooled kit1.6.6 and run14 gain-by-agent-count results remain pending.
- Replaced the B300 measurement placeholder with the llama.cpp depth ladder and vLLM FP8 cold marginal/cached rates,
  including cache-block sizes. Measured B300 rates remain server-only; run13 peak-scaled economics await run14.
- Added the first heterogeneous, uncalibrated vLLM state export at784 tokens with BF16/Q4 client comparisons;
  retained TODOs for the31,360-token run and node-adapter smoke.
- Added pre-import-speed-v2 CUDA per-call fixed and token import costs beside the5G breakdown, including the39,146-token
  case and the single M3 Max rate. Extended named publication controls and refreshed exact byte/numeric-site pins.
- Narrowed the novelty claim to the design and applicability limits of prefill as a service for an autonomous local
  agent. Added a source-bound DS4 PR 401 / PPD / SparKV / PrfaaS mechanism table, including prior catch-up, rebuild,
  routing and recurrent-state mechanisms; tied the measured claims to their finite configurations.
- Reframed verifiability as a proposed audit with an open threat model, trusted-start dependency chain and uncalibrated
  cross-platform tolerance. A history hash binds declared tokens without proving state computation.
- Restored the one-user corpus caveat and per-tool retained-history dates. Reconciled the call totals as two snapshots
  with identical filter parameters: the later export adds 2,545 Codex calls and one context, rather than a billing filter.
- Derived the deferred-tail routing equation from the engine, retained its zero-import limitation pending run 14,
  and separated the measured 165.6-second transfer/import from the 10.6-second server prefill in the 5G first call.
- Storage versus prefill changes direction: run 11 had storage $6.5 > prefill $5.1 per month; run 13 has
  storage $6.9 < prefill $10.0 for M5 Max64 at 20%, so storing is cheaper. The paper states the comparison and snapshot keys.
- Four daily GLM million-token sessions were described as almost four times cheaper than API; run 13 gives
  3.3–3.6 times cheaper. The four-session saving against the own cluster changes from 1.4 to 1.3 times.
- At full GLM load, savings change from 5.4–6.0 to 4.8–5.1 times against API and from 2.0–2.1 to 1.9 times
  against the own cluster. At two sessions the hybrid premium falls from 29–44% to 15–30%; at one, from 2.5–2.9 to 1.9–2.4 times.
- The ideal-client offload example changes from a constant 1.35 PFLOP/s B300 estimate and 22.5-times ceiling
  to a depth-specific 0.72 PFLOP/s at 110k and 12.1-times ceiling; 1G/10G bounds change from 3.4/14 to 3.0/9 times.
- vLLM's 8,122/2,209 token/s figures, previously labelled cold prefill rates, are now explicitly rates of a
  10,000-token portion computed from the cold fit. Server-only qualification and the pending client bridge remain explicit.
- Migrate both publication checkers and nine current-publication guards to run 13. Preserve the historical export
  pins, original quote ledger and site exceptions; pin all v2 paper bytes and numeric coordinates separately.
- The Russian paper now uses the reviewed run-13 engine snapshot. Rebuilt chart inputs and tables include the reproduced
  checkpoints-off server base, measured M5 Max 64 GB, corrected Gemma full-attention KV and current API pricing.
- Updated every run-13 ledger site and manually reviewed the 406 inventoried number-word occurrences; corrected GPU counts,
  payback wording and cost comparisons whose direction changed. The gap map records the original sites and evidence.
- Added measured 27B CUDA equivalence, the first 5G CUDA-to-Metal call with TTFT breakdown and wire bytes, stock deep-slot
  transfer, canonical M3 Max and measured M5 Max results, checkpoint sensitivity and server-only vLLM FP8.
- Updated limitations, supported abstract/conclusion claims and the research outlook. Pending quality, GPU/Mac qualification,
  B300, calibration, bridge and end-to-end measurements remain explicit with `TODO(data)` comments and no placeholder values.

### Validation limits
- The r7 failures from obsolete run-11 checker directions and nine old-publication guards are resolved by the
  owner-authorized run-13 migration. Full command results and clean/planted controls are recorded in the gap map.
- The growing-session CUDA-to-Metal run, the KL study, CUDA-to-Metal calibration and cooled kit 1.6.6 measurements
  remain pending. The finite bridge and task-pilot observations above do not establish general task equivalence.
- The incident lane owns the publication commit, pull request, landing and owner-signed release tag. This package
  creates no release tag and does not itself authorize GitHub publication.

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
