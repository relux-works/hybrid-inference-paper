# Crossover and operations source custody — 2026-10-30

> Run11 accounting correction: current nonlegacy base scenarios use output alone (mean511.9); reasoning is informational. Provider evidence and Muse's unverified treatment are recorded in workload provenance and [the Run11 report](ENGINE-REPORT-261030.md#run-11-output-includes-reasoning). Earlier summed numerical examples below are historical and recoverable with explicit fraction1; the separately historical crossover bridge and legacy transcripts remain unchanged.

No online source was fetched. The legacy modules and lane sources were read
only. All numerical assumptions are quantities with units and provenance in
`bridge.json`, `operations.json`, the `owners-paper` scenario or reused data.

| Evidence | Identity / interpretation |
|---|---|
| Reviewed r3 | Signed `46e0ee9b2562b79f5b150ef876aaff9f2fa84d85` |
| Frozen legacy inputs | `legacy.json` SHA-256 `a74753d4deaf8e0d6334770059a2e030a7c1f1b214888f486e4a1b82cfde94ca` |
| Legacy code | `legacy/sessions.py`, `legacy/fleet.py`, `legacy/equilibrium.py`; unchanged, with nine original output goldens |
| Calc5 synthetic workload | `make_sessions(n=200,L0=20000,L1=200000,seed=7)`; sizing uses first 80 sessions, API uses all 200 |
| Measured workload | Repository full04 `stats.json`, original pinned measurement registry; calc8 sample prefix 39,904 calls, seed 5, explicit reasoning sum |
| KV/state fit | Original `ivmbp-qwen27b-bench-20261030`, archive SHA-256 `5c393bdf40052eb582b5c17aac6176a9273a866c4fadde999ee19afa30924439`; affine slope 34,844 B/token and intercept 156,894,784 B |
| Prior ownership data | `ownership.json` SHA-256 `f7b4e0808812e459dfcc030710e095f708078a14118e9ada9d4ea4f4e2234543`; unchanged |

The bridge stores sufficient per-call moments: depth, delta, output, tool delay,
output×context, tool×context, input-prefill FLOPs, output-prefill FLOPs and prior
output (reset per session). Their provenance states the formula and frozen
legacy parameter-file digest. The old sizing/API populations also retain their
own calls/session means, 62.975 versus 62.7. Thus 40 sessions/day normalizes to
2,519 sizing calls versus 2,508 API calls. Those sample differences are exposed,
then aligned as one explicit step before moving to 2,500 measured-mix calls/day.
The engine does not import legacy execution into the canonical graph or replay
stored cost/crossover answers. It recomputes demand, integer fleets and prices.

For dense per-call moments m and a server unit with G GPUs:

```
prefill = (m.input_flop + shadow*m.output_flop) / (G*effective_FLOP_s)
decode = (m.output*(weight_bytes/batch + state_passes*state_bytes)
          + KV_bytes_per_token*m.output_context) / (G*effective_bandwidth)
residency = (KV_bytes_per_token*(m.output_context/stream_rate + m.tool_context)
             + include_state*state_bytes*(m.output/stream_rate + m.tool)) / free_HBM
units = max(1, ceil(N*calls_day*share*(prefill+decode+residency)
                    *peak_factor/(operator_hours*3600)))
```

Each bridge step changes one assumption; effects at integer fleet boundaries
are order-dependent. Legacy already uses 27 GB FP8 weights and 4.5 PFLOP/s FP8
×30% MFU, not BF16. Median token tariffs are identical to r3. The calc5 Rule A
**code** is office-only through 10 people, mixed office/DC through 50, DC-only
afterward. Its heading/comment says office through 50; that label is inaccurate.
The engine reproduces the actual code and keeps its historical text unchanged.

Two paper corrections are explicit. All-server output tokens already produce
KV during decode, so charging their shadow-prefill again overstates own-cluster
work. Only the hybrid needs a shadow server copy. Dense 27B fits on one GPU;
the paper candidate therefore reserves weights/workspace on every replica
instead of assuming one model copy pooled across eight GPUs. Neither change
establishes a serving-runtime SLA. Sparse grids retain their literal meaning;
the paper candidate now checks every integer team through 20,000.

## Remote small-host inputs

| Quantity | Declared value | Provenance and limit |
|---|---:|---|
| Server Edition GPU acquisition | $23,000/GPU | Existing calc4 hardware snapshot; a dated estimate, not a fresh quote |
| One-GPU host budget | $36,000 | 1×$23k GPU + $13k host allowance, new estimate |
| Two-GPU host budget | $62,000 | 2×$23k GPUs + $16k host allowance, new estimate |
| Full-load power | 0.9 / 1.8 kW | Calc4 single-GPU host envelope, scaled; estimate |
| Colo space rate | $190/kW-month | Inherited calc4 CBRE-based snapshot; small-host minimum added separately |
| Colo host minimum | $100/host-month | New estimate, no supplier quote; charged as max(minimum,kW×rate) |
| Counterfactual rental | $2.20/GPU-hour | Supplied offline Koyeb price note; same-memory comparison, not proof of paired placement |
| Idle power | 15% of full-load | New estimate; linear energy model, not a measurement |
| Office availability | Team >100 | Owner's run-4 policy; small remote teams use colocation |

The dated source URLs are inherited from
[`SERVICE-SOURCES-261030.md`](SERVICE-SOURCES-261030.md) and the unchanged
hardware inputs: [Koyeb pricing](https://www.koyeb.com/pricing),
[NVIDIA architecture whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf)
and the repository's original CBRE/EIA snapshot references. No price or memory
number was refreshed from the network. Server performance and sharding loss
remain explicitly estimated. Under the declared 184.5 GB Q4 GLM weights +8 GB
workspace, even 2×96 GB is insufficient; the two-GPU small-host option alarms
for GLM instead of silently using a smaller format or pooling incompatible memory.

## Autopilot and pool definitions

Autopilot share is a fraction of the **same total monthly open-model requests**,
not an additional demand multiplier. The operator fraction runs in 8h×21-day
windows; automatic work is uniform over the 730h average month. Both profiles
price the same workload. The prefill operating study is distinct from per-Mac
capacity/overflow; it does not give a free device-capacity increase or a cost
to add a second time to the hybrid summary.

The hypothetical pool price defaults to $0.50/GPU-hour received net of any pool
fee, with tenant network/storage billed separately as an explicit estimate.
Fill is 50% of guaranteed idle-window admission capacity. The pool does not
exist and no fee, price, demand or implementation is observed evidence.

Operator-only guaranteed idle intervals are the nights between active days
and the trailing inactive part of an average month. Admission stops 0.25h
before each owner return. Each tenant job is bounded to 0.20h and owner
model/state restoration to 0.05h; both are unqualified estimates. If their
sum exceeds the guard, pool metrics alarm while known idle geometry and
normal ownership remain available. Fill cannot consume owner windows.
Any positive fill reserves the full guard as a conservative incremental drain
energy bound, since fractional occupancy cannot bound the final job's runtime.
Continuous automatic reservations leave no guaranteed idle window, so their
pool revenue is zero. No owner fallback or scheduling/queueing discount is
assumed. A reported zero conflict interval is an analytical schedule property,
not a deployed-system availability measurement.

Operating-study owner opex charges full-calendar idle power, incremental owner
work, colo and support. Summary/residual/small-team tables retain calc4's
fixed 70% energy-duty budget; attribution holds unit opex fixed. These are
separate sensitivities, not costs to add or average. Pool revenue is reduced by incremental work/drain energy. Effective
cost divides depreciation+opex−net pool credit by **owner-used GPU-hours**.
Negative net credits and effective costs are not clamped: they represent a
loss or net revenue under the selected estimates. Buy/rent recovery uses the
same net operating credit and stationary price/residual assumptions. It is not
a discounted-cash-flow forecast or a resale guarantee. These are equivalent
residual-adjusted recovery months; a value beyond 48 months indicates no
advantage within the planned four-year horizon, not a claim that the GPU lasts
for decades. Terminal residual credit does not eliminate the initial cash outlay.
