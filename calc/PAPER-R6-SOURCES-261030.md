# Run 6 source custody and model boundaries

> Run11 accounting correction: current nonlegacy base scenarios use output alone (mean511.9); reasoning is informational. Provider evidence and Muse's unverified treatment are recorded in workload provenance and [the Run11 report](ENGINE-REPORT-261030.md#run-11-output-includes-reasoning). Earlier summed numerical examples below are historical and recoverable with explicit fraction1; the separately historical crossover bridge and legacy transcripts remain unchanged.

This extends reviewed run 5 (`892da662`) without network research. All input
quantities retain their own unit/provenance in JSON. No new hardware or
performance measurement was acquired. The engine verifies the existing package
files against `hybridcalc/data/measurements.json`. Package custody is recorded
in `data/measurements/ivmbp-2026-10-30/ENGINE-PACKAGES.json`; the input registry,
rather than this prose, controls the file reads.

- `paper-tables-r6.json`: owner-requested chart grids, true closed-perimeter
  share 1, explicit small-rack policy exception, zero incremental local frontend
  budget, shared-device occupancy convention and two state traffic passes.
- `owners.options.rack1/rack2`: exact R4 `colo1/colo2` hardware, purchase and
  power envelopes, now placed in an **owned internal rack**. Server Edition
  96 GB/GPU, 1/2 GPUs and $36,000/$62,000 host estimates retain their original
  provenance. Space uses the explicit sunk-rack `owners.office_colo=0` input;
  office electricity/support and PUE assumptions are reused. This is not a new
  vendor quote and does not include a new secure-facility construction budget.
  Add a rack fee through `owners.office_colo` if the organization has one.
- B300: existing eight-replica 288 GB/GPU node from `ownership.json`; internal
  facility uses existing datacenter energy/support/rack budgeting. Candidate
  fleet paths overlap from 50 to 100 people. Whole-fleet costs, not a fractional
  GPU allocation, choose the recommended eligible path.
- Perimeter defaults: 8 hours/day, 21 days/month, 70% target server load,
  4 years, residual 20% for both servers and bought Mac premiums, as in
  owners-paper. The separate Studio utilization chart retains R5 client
  residual 35%. Zero local frontend cost is a sunk
  software baseline; hybrid uses existing `owners.front_month`.
- `paper-tables.json`, `hardware.json`: six explicit Apple clients and M3
  compute-scaled local-prefill curves, including the memory roofline. M4/M5/
  Ultra portability and four-stream scaling away from the 32k M3 anchor remain
  estimates. No 64k/128k parallel measurement is invented.
- Hash-checked benchmark: M3 Max single native 8.440946539830035 tok/s and
  four-stream aggregate maximum-decode-interval 14.054306337676012 tok/s at the
  frozen 32k coordinate in `normalized-results.json`. These differ from actual
  request wall throughput (13.1596888121 tok/s for four streams). The benchmark
  archive SHA256 is
  `5c393bdf40052eb582b5c17aac6176a9273a866c4fadde999ee19afa30924439`.
- Decode memory geometry: Q4 GGUF 18,973,870,432 B, resident slot slope
  34,844 B/token and intercept 156,894,784 B read from measured depth slots;
  serialized q8_0 KV is the existing 34,816 B/token input. The raw bound uses
  serialized KV and two recurrent-state passes; fit uses resident slope and
  one state allocation/session. The OS/apps reserve is 12 decimal GB.
- GLM: same R5 growing session, 181.4 GB Q4 weights, sparse expert byte-traffic
  estimate, Ultra 256 purchase price and residual, API tariff and integer owned
  B300 pool. Replayed measured call increments determine calls/session; final
  contexts are clipped at 200k/1M. Sharing buys ceil(team/users_per_Studio)
  devices; aggregate device capacity is never multiplied by sharing.

Every exported JSON result includes direct/transitive dependencies per cell.
The global sources sidecar includes GLM's API inputs because it covers all six
R6 tables. The perimeter dependency test independently forbids API tariffs,
hourly rental and outside egress prices on every perimeter cell.

The closed-perimeter case is a performance/economics estimate, not a security
or product qualification. It assumes compatible state export, an internal
organization-controlled path with the stated WAN envelope, and graceful local
scheduling. Waits exclude queues; no fallback outside the perimeter exists.
