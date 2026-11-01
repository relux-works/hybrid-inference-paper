# Run 9 protocol hosting: source custody and limits

No new network research, installation or measurement package was used. The
owner's `hybrid-calc-r9-261030` protocol brief supplies the immutable-prefix,
catch-up, retention and intensity-variant requirements. New policy enums and
coordinates carry `estimate` provenance describing the formulas/decision basis;
they are not presented as measured runtime behavior.

## Inputs retained from accepted runs

- Measured pooled call mix and fitted-tail sampler are unchanged. Root stats
  SHA256 is `8c5f1f2c44e344b78d32d0b4c216d0ebdf2ecdae3cde0f1a983cb329e488e2a7`.
- M3 benchmark archive SHA256 remains
  `5c393bdf40052eb582b5c17aac6176a9273a866c4fadde999ee19afa30924439`.
  Measured Qwen resident geometry is 34844B/token and 156894784B fixed f32 state.
- API, hardware and compute envelopes retain their dated offline provenance.
  Server weights remain quantized. No tariff, MFU, client efficiency or accepted
  full-shadow token count was changed to improve the result.
- RAM$0.50 and NVMe$0.10 per decimalGB-month,50GB/s effective PCIe, storage
  bandwidths, four retained copies and the month fraction remain explicit R8
  budget estimates. They are not protocol requirements or provider quotes.

## New input layers and publication cases

`hosting.json` adds provenance-bearing `hosting.catch_up=at_offload` and
`hosting.retention=tiered`. `hosting-conservative.json` overrides these to
`per_call` and `ram_month`, retaining corrected append-only spill in both cases.
Four conservative scenario JSON files compose the same source layers and
export parallel hosting-dependent `*_conservative.csv` files with matching row
coordinates. Missing input layers invalidate their declared namespace; they do
not fall back to the previous layer's policy.

`paper-tables-r9.json` supplies 10000-token portions and 32/16-bit recurrent-state
coordinates. Existing `r8.portion` supplies 1000 tokens. Only Qwen f32 state is
measured; its 16-bit half is an estimate. Flash-Next's58834944B and GLM's76300000B
R8 wire state were already bf16. New f32 rows explicitly use 117669888B and
152600000B; 16-bit rows preserve the old native wire geometry. Dense models
without recurrent state retain zero fixed bytes in both variants. Config URLs
and unsupported context boundaries are inherited from the accepted R7 inputs.

## Protocol model

Past-position KV is immutable. A flush appends `(new+decoded)*KV` and overwrites
one fixed recurrent state. Reload reads the full sampled prefix. The original
R8 full-slot rewrite appears only as a historical control/test, not a selectable
published case.

The sampled calls are exchangeable offload opportunities. At offload fraction
`p`, expected local run is `(1-p)/p`; mean pending compute per offload is the
local full input/output work plus preceding offloaded output work, divided by
sample offload count. Pending enters the offloaded call's critical path and the
routing decision. The optimistic winner set is pruned monotonically until
stable. Full server compute still prefills every input/output token once.
Stationary mean runs ignore finite-day resets/order, so these are expected
latencies, not a measured trace or a queueing simulation.

Daily reload/state-overwrite budgets add one terminal catch-up per active
session-day. Qwen uses up to four active retained sessions; GLM uses actual
served long sessions capped by retained copies. This flush adds migration I/O,
not duplicated compute. All append KV bytes are charged once. The routing-aware
people/GPU hosting columns use the named M5 Max 64 reference client in the
scenario and its declared WAN path; compute-only columns remain independent of
this selection and of storage prices.

Tiered storage uses each scenario row's actual hours and workdays divided by
`economics.hours_month`:8h paper/owned rows and 10h/24h remote rows. Mean retained
bytes and copy count set the budget. One NVMe-to-RAM promotion per retained
session-day is background storage I/O, never GPU compute. It is a separately
reported diagnostic; no GPU overlap/hot-cache saving or transfer implementation
is claimed. Promotion throughput, journal bytes, scheduling and real retention
populations still need measurement. Alternative HBM/NVMe diagnostic overrides
remain outside the two default RAM-based publication cases.

## Evidence and artifacts

- [ENGINE-REPORT-261030.md](ENGINE-REPORT-261030.md): old/design/conservative
  person bills and splits, users/GPU, per-profile fleets, each link, client
  capacities, GLM headlines, exact tests and limits.
- [ENGINE-CHANGES-R9-261030.csv](ENGINE-CHANGES-R9-261030.csv): full-precision
  R8-to-both-case changed/new numeric or alarm cells.
- [PERIMETER-NODES-R9-261030.csv](PERIMETER-NODES-R9-261030.csv): all six
  clients × three profiles × five teams × three server paths.
- Eight source/schema/alarm/manifest sidecar groups in `out/paper/` bind every
  published payload to its input provenance and exact generator file hashes.
- `tests/test_run9.py` states finite protocol/table/gap claims;
  `tests/r9_controls.py` plants four bounded historical/forbidden behaviors.
  The full-slot witness was observed red before modifying production code.
