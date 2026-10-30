# Hybrid inference: architecture and economics (working repository)

Working repository for the paper «Hybrid Inference with Client–Server Prefill–Decode Disaggregation: Architecture and
Economics for Unified-Memory Clients». Authors: Ivan Oparin and Alexey Grigoriev (Relux Works).

The idea: a GPU server prefills an agent session and ships the model state (attention KV of the new positions plus the
fixed recurrent state) to a unified-memory client such as a Mac, which decodes locally.

Status: private draft, 2026-10-30. The paper text is not written yet; the calculations, sources and the prototype
specification are. Everything here is open-source material in preparation. Choose the licences before the repository
is made public; the proposal is CC BY 4.0 for text and Apache-2.0 for code.

## Layout

| Path | What |
|---|---|
| `paper/` | Paper text, Russian first |
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
