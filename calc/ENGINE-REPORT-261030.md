# Calculation engine — run 11, hybrid-calc-r11-261101

> Current delivery: see [Run 11](#run-11-output-includes-reasoning). Earlier run sections below are historical evidence; run11 output-only base and regenerated CSVs supersede their numerical claims.

Continues signed `82bb1e52d9a9414d964c8d9665dbf652c91510df` on `calc-engine`.
Ready for review as a signed local delivery, no push, network research or installs.
No changes under `paper/`, `.github/`, `.scripts/`, `tools/` or `data/research/`.
The R9 section supersedes run-8 hosting equations/numbers below. Accepted full
shadow, its two-node witness, measured-tail sampler, output-only sensitivity,
transcript and compute-only users/GPU are retained. Publication cases are the
protocol design and an append-only conservative bound, never the defective
full-slot rewrite.

## Protocol correction and assumptions

**Immutable prefix.** Correct spill is `(new+decoded)*KV+state`. Qwen at depth
150000, new 1000, decoded 700, measured KV34844B/token and state 156894784B writes
**216129584B**, versus run8's5442729584B. Reload remains 5383494784B for this
prefix. `test_append_only_spill` was added first and failed on unmodified R8
with the full-slot value; the exact original defect is retained only as the
`full_slot` historical control. No published spill-mode switch can select it.
The test compares seconds with bytes/bandwidth directly to avoid a floating
round-trip byte-equality artifact; the mathematical byte witness is unchanged.

**Catch-up.** `hosting.catch_up` is a provenance-bearing enum:

- `per_call`: each client-served call reloads and shadows input/output; it spills
  only appended KV and the overwritten recurrent state.
- `at_offload`: client-served tokens are journaled; the next offload carries
  pending local input/output and previous offloaded output under one reload.
  Every token is prefilled exactly once in either policy. Pending is foreground
  compute placement, not additional compute in the bill.

Calls are exchangeable opportunities, not reconstructed chronology. For sample
offload fraction `p`, expected consecutive local calls per offload is `(1-p)/p`.
Expected pending compute seconds per offload are
`(sum(local input+output work)+sum(previous offloaded output work))/offload_count`.
That work is added to the current offload's server time **before** comparing
with local time. Starting from zero-pending winners, nonwinning calls are
removed until the set is stable. Removal increases pending work, so this finds
the greatest stable winner set and terminates over a finite sample. Zero
winners means no foreground pending path; it does not divide by zero or make
end-of-day background work free. The model uses stationary mean runs rather
than finite-session ordering; it does not predict tail latency or queues.

For each active session-day, one terminal reload/state overwrite is reserved:
`reloads/day=offloaded_calls/day+active_session_days`, with all accumulated KV
appended once. Qwen plans use `min(served_calls_day,retained_sessions)` active
session-days/person. GLM uses the actual served long sessions/day, capped by
retained slots. The default retained population remains the explicit four-copy
estimate; it is not imposed by the protocol or inferred from 116-call groups.
The terminal flush redistributes already-budgeted compute and adds only its
extra reload/state I/O. Prefix bytes use the sampled depth as a conservative
snapshot proxy; no unmeasured hot cache or GPU/I/O overlap saving is assumed.

**Retention.** `hosting.retention` is a second provenance-bearing enum:

- `ram_month`: selected active RAM tier for the whole declared month fraction.
- `tiered`: active-window RAM and NVMe otherwise. Storage uses
  `active=hours*workdays/month_hours` and
  `copies*mean_end_bytes/1e9*month_fraction*(active*RAM_price+(1-active)*NVMe_price)`.

Default active fraction is 8*21/730. Remote rent/buy uses the actual 10h or 24h
row, not the 8h paper window. Windows exceeding calendar hours alarm. Existing
RAM$0.50/GB-month, NVMe$0.10/GB-month,50GB/s effective PCIe and storage bandwidths
remain estimates. One NVMe-to-RAM promotion per retained session-day is
background I/O, explicitly **not GPU time**. Its seconds/day are exposed;
changing NVMe promotion bandwidth cannot change GPU cost or client capacity.
RAM-only does not read unused NVMe inputs. Advanced HBM/NVMe diagnostic tier
overrides remain available; publication cases use the declared RAM active tier.

The server keeps the full logical session copy eventually in both cases;
deferred catch-up may lag the client between offloads. Full-shadow compute is
unchanged per served call. Calls actually served can differ slightly because
pending compute changes client wait/capacity; overflow remains fully priced.
Owned perimeter/GLM/remote fleets include variable migration plus terminal I/O.
Journal bytes, compute, append bytes, state overwrite and promotion are separate
operations; no full-prefix write or duplicated pending compute is hidden.

## Published cases and files

Parallel `*_conservative.csv` files have the **same row keys and columns** as
their design counterparts. Existing filenames are design defaults. Export the
four primary families and four matching conservative scenarios:

```bash
python3 -m hybridcalc export paper-tables --output calc/out/paper
python3 -m hybridcalc export paper-tables-conservative --output calc/out/paper
python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r6-conservative --output calc/out/paper
python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r7-conservative --output calc/out/paper
python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r8-conservative --output calc/out/paper
```

All files are under `calc/out/paper/`. Independent historical crossover,
architecture/fit/raw decode bounds and the accepted transcript are shared.
Conservative scenarios export only hosting-dependent tables, including traffic
and the R7 decode sensitivity. Standalone large-turn/one-shot cases start with
an available server prefix/empty prefix and no unknown journal, so their
numeric timing components remain shared in both cases. Eight sets of
schema/source/alarm/manifest sidecars record exact generation and payload hashes.
The selectors are data; `hosting-conservative.json` overrides only catch-up and
retention, keeping the corrected append-only protocol in both cases.

| Table | Design CSV | Conservative CSV |
| --- | --- | --- |
| person_cost_s20 | [CSV](out/paper/person_cost_s20.csv) | [CSV](out/paper/person_cost_s20_conservative.csv) |
| person_cost_s50 | [CSV](out/paper/person_cost_s50.csv) | [CSV](out/paper/person_cost_s50_conservative.csv) |
| person_cost_academic_s100 | [CSV](out/paper/person_cost_academic_s100.csv) | [CSV](out/paper/person_cost_academic_s100_conservative.csv) |
| remote_rent_buy | [CSV](out/paper/remote_rent_buy.csv) | [CSV](out/paper/remote_rent_buy_conservative.csv) |
| client_sessions_day | [CSV](out/paper/client_sessions_day.csv) | [CSV](out/paper/client_sessions_day_conservative.csv) |
| offload_by_link | [CSV](out/paper/offload_by_link.csv) | [CSV](out/paper/offload_by_link_conservative.csv) |
| traffic_user_month | [CSV](out/paper/traffic_user_month.csv) | [CSV](out/paper/traffic_user_month_conservative.csv) |
| glm_long_sessions | [CSV](out/paper/glm_long_sessions.csv) | [CSV](out/paper/glm_long_sessions_conservative.csv) |
| perimeter_cost | [CSV](out/paper/perimeter_cost.csv) | [CSV](out/paper/perimeter_cost_conservative.csv) |
| perimeter_cost_light | [CSV](out/paper/perimeter_cost_light.csv) | [CSV](out/paper/perimeter_cost_light_conservative.csv) |
| perimeter_cost_medium | [CSV](out/paper/perimeter_cost_medium.csv) | [CSV](out/paper/perimeter_cost_medium_conservative.csv) |
| perimeter_cost_heavy | [CSV](out/paper/perimeter_cost_heavy.csv) | [CSV](out/paper/perimeter_cost_heavy_conservative.csv) |
| glm_utilization | [CSV](out/paper/glm_utilization.csv) | [CSV](out/paper/glm_utilization_conservative.csv) |
| turn_speedup | [CSV](out/paper/turn_speedup.csv) | [CSV](out/paper/turn_speedup_conservative.csv) |
| oneshot_ingest | [CSV](out/paper/oneshot_ingest.csv) | [CSV](out/paper/oneshot_ingest_conservative.csv) |
| decode_sensitivity | [CSV](out/paper/decode_sensitivity.csv) | [CSV](out/paper/decode_sensitivity_conservative.csv) |
| output_only_sensitivity | [CSV](out/paper/output_only_sensitivity.csv) | [CSV](out/paper/output_only_sensitivity_conservative.csv) |
| people_per_gpu | [CSV](out/paper/people_per_gpu.csv) | [CSV](out/paper/people_per_gpu_conservative.csv) |

The remaining shared tables are `crossover_explanation.csv`,
`client_fit_deep.csv`, `decode_scaling.csv`, `arch_compare.csv`,
`transcript_example.csv` and expanded `flop_per_byte.csv` (432rows). Thus 42 CSVs
are published. Design alarm cells are 329 R5,6 R6,28 R7 and 576 R8; conservative
alarm cells are 252 R5,0 R6,24 R7 and 0 R8. They are inherited policy/fit/physical
bounds and unsupported contexts, not new hosting gaps. No person, perimeter,
client, offload, GLM or people/GPU rows alarm on complete default inputs.
Ordinary partial export exits 0, strict alarm export exits 1; unknown overrides
exit 2. An all-supported-depth positive strict control exits 0 before the planted
catch-up gap changes it to 1. Alarms are `nan` cells with explicit reasons and
never numeric zero.

## R8 → design → conservative headlines

All amounts are USD/person-month unless stated otherwise. Open share applies to
requested calls, not just calls the Mac manages to serve. Median and cheapest
API overflow remain included. Common closed-model spending is excluded as in
run8. API prices and all-server physics are unchanged.

### M5 Max 64: full bills and compute/storage/migration split

At the economics WAN link, team 5 (hybrid shared-service totals are flat across
team sizes); each cell is **R8 → new case**. Both purchase bases and both
whole-demand API overflow bills are listed. Compute per served call is identical
across policies; only actual served volume can alter compute/month.

| Share | Mac basis | Case | Median total | Cheapest total | Compute | Storage | Migration |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s20 | Mac already owned | design | 40.48 → 25.86 | 39.37 → 24.75 | 5.83 → 5.83 | 11.77 → 4.52 | 9.25 → 1.99 |
| s20 | Mac already owned | conservative | 40.48 → 36.00 | 39.37 → 34.89 | 5.83 → 5.83 | 11.77 → 11.77 | 9.25 → 4.77 |
| s20 | Mac premium bought | design | 75.69 → 61.06 | 74.58 → 59.96 | 5.83 → 5.83 | 11.77 → 4.52 | 9.25 → 1.99 |
| s20 | Mac premium bought | conservative | 75.69 → 71.21 | 74.58 → 70.10 | 5.83 → 5.83 | 11.77 → 11.77 | 9.25 → 4.77 |
| s50 | Mac already owned | design | 177.26 → 160.64 | 65.61 → 48.94 | 7.45 → 7.44 | 11.77 → 4.52 | 11.81 → 2.53 |
| s50 | Mac already owned | conservative | 177.26 → 171.54 | 65.61 → 59.89 | 7.45 → 7.45 | 11.77 → 11.77 | 11.81 → 6.10 |
| s50 | Mac premium bought | design | 212.46 → 195.84 | 100.82 → 84.14 | 7.45 → 7.44 | 11.77 → 4.52 | 11.81 → 2.53 |
| s50 | Mac premium bought | conservative | 212.46 → 206.75 | 100.82 → 95.10 | 7.45 → 7.45 | 11.77 → 11.77 | 11.81 → 6.10 |

At 20% share the design hosting bill is$6.51/month (storage 4.52+migration 1.99)
versus compute 5.83, replacing R8's$21.01 hosting. Conservative is$16.54 hosting.
The fixed correction does not establish a general win over the cheapest API;
cheapest whole-demand API costs remain below these hybrid totals. Stored-copy
population and tier prices remain visible economic assumptions.

### Heavy people per GPU

Before per-Mac admission/caps,8h window and 70% target load. Routing-dependent
hosting uses the named M5 Max 64 reference client and declared WAN link.100% is
the academic open-share bound outside the closed perimeter. Integer people
round down, preserving the accepted compute-only column exactly.

| GPU | Share | Compute-only (unchanged) | R8 with hosting | Design | Conservative |
| --- | --- | --- | --- | --- | --- |
| RTX PRO 6000 hourly | 0.2 | 60 | 44 | 56 | 51 |
| RTX PRO 6000 hourly | 0.5 | 24 | 17 | 22 | 20 |
| RTX PRO 6000 hourly | 1 | 12 | 8 | 11 | 10 |
| B300 288 GB hourly | 0.2 | 271 | 104 | 201 | 148 |
| B300 288 GB hourly | 0.5 | 108 | 41 | 80 | 59 |
| B300 288 GB hourly | 1 | 54 | 20 | 40 | 29 |

### Perimeter integer fleets, every profile/team

M5 Max 64, Mac already owned (purchase basis does not change units). All-server
units are unchanged; hybrid uses the full-shadow compute plus corrected I/O.
Each candidate path is visible; `eligible=0` indicates a physically sized path
outside the perimeter small-host/large-node policy, not a recommendation.
The separate [full node grid](PERIMETER-NODES-R9-261030.csv) gives **all six
clients**, both cases and the all-server reference, at all profiles/team sizes.
All node-count changes at every published location also appear in the numeric
change ledger.

| Profile | Team | Candidate | Eligible | All-server | R8 hybrid | Design | Conservative |
| --- | --- | --- | --- | --- | --- | --- | --- |
| light | 5 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 1 | 1 | 1 | 1 |
| light | 5 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 1 | 1 | 1 | 1 |
| light | 5 | Owned HGX B300 8-GPU | 0 | 1 | 1 | 1 | 1 |
| medium | 5 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 2 | 1 | 1 | 1 |
| medium | 5 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 1 | 1 | 1 | 1 |
| medium | 5 | Owned HGX B300 8-GPU | 0 | 1 | 1 | 1 | 1 |
| heavy | 5 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 5 | 4 | 4 | 4 |
| heavy | 5 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 3 | 2 | 2 | 2 |
| heavy | 5 | Owned HGX B300 8-GPU | 0 | 1 | 1 | 1 | 1 |
| light | 10 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 1 | 1 | 1 | 1 |
| light | 10 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 1 | 1 | 1 | 1 |
| light | 10 | Owned HGX B300 8-GPU | 0 | 1 | 1 | 1 | 1 |
| medium | 10 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 3 | 1 | 1 | 1 |
| medium | 10 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 2 | 1 | 1 | 1 |
| medium | 10 | Owned HGX B300 8-GPU | 0 | 1 | 1 | 1 | 1 |
| heavy | 10 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 9 | 7 | 7 | 7 |
| heavy | 10 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 5 | 4 | 4 | 4 |
| heavy | 10 | Owned HGX B300 8-GPU | 0 | 1 | 1 | 1 | 1 |
| light | 50 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 4 | 1 | 1 | 1 |
| light | 50 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 2 | 1 | 1 | 1 |
| light | 50 | Owned HGX B300 8-GPU | 1 | 1 | 1 | 1 | 1 |
| medium | 50 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 14 | 5 | 5 | 5 |
| medium | 50 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 8 | 3 | 3 | 3 |
| medium | 50 | Owned HGX B300 8-GPU | 1 | 1 | 1 | 1 | 1 |
| heavy | 50 | 1x RTX PRO 6000 Server; own perimeter rack | 1 | 42 | 33 | 33 | 33 |
| heavy | 50 | 2x RTX PRO 6000 Server; own perimeter rack | 1 | 23 | 18 | 18 | 18 |
| heavy | 50 | Owned HGX B300 8-GPU | 1 | 2 | 2 | 1 | 2 |
| light | 500 | 1x RTX PRO 6000 Server; own perimeter rack | 0 | 34 | 5 | 4 | 5 |
| light | 500 | 2x RTX PRO 6000 Server; own perimeter rack | 0 | 18 | 3 | 3 | 3 |
| light | 500 | Owned HGX B300 8-GPU | 1 | 2 | 1 | 1 | 1 |
| medium | 500 | 1x RTX PRO 6000 Server; own perimeter rack | 0 | 135 | 43 | 41 | 42 |
| medium | 500 | 2x RTX PRO 6000 Server; own perimeter rack | 0 | 72 | 23 | 22 | 23 |
| medium | 500 | Owned HGX B300 8-GPU | 1 | 5 | 2 | 2 | 2 |
| heavy | 500 | 1x RTX PRO 6000 Server; own perimeter rack | 0 | 419 | 328 | 325 | 326 |
| heavy | 500 | 2x RTX PRO 6000 Server; own perimeter rack | 0 | 224 | 176 | 174 | 175 |
| heavy | 500 | Owned HGX B300 8-GPU | 1 | 13 | 11 | 10 | 11 |
| light | 5000 | 1x RTX PRO 6000 Server; own perimeter rack | 0 | 336 | 49 | 40 | 44 |
| light | 5000 | 2x RTX PRO 6000 Server; own perimeter rack | 0 | 180 | 27 | 22 | 24 |
| light | 5000 | Owned HGX B300 8-GPU | 1 | 11 | 3 | 2 | 2 |
| medium | 5000 | 1x RTX PRO 6000 Server; own perimeter rack | 0 | 1341 | 429 | 401 | 411 |
| medium | 5000 | 2x RTX PRO 6000 Server; own perimeter rack | 0 | 717 | 230 | 216 | 221 |
| medium | 5000 | Owned HGX B300 8-GPU | 1 | 41 | 17 | 13 | 14 |
| heavy | 5000 | 1x RTX PRO 6000 Server; own perimeter rack | 0 | 4190 | 3278 | 3250 | 3260 |
| heavy | 5000 | 2x RTX PRO 6000 Server; own perimeter rack | 0 | 2238 | 1752 | 1738 | 1743 |
| heavy | 5000 | Owned HGX B300 8-GPU | 1 | 128 | 103 | 100 | 101 |

The 5000-person light/B300 hybrid row is 3→2→2. The accepted isolated original
sample/HBM full-shadow regression still needs two nodes. The correction removes
the extra migration node without dropping any shadow compute or externalizing
perimeter calls.

### Offload share and saving per ALL calls

Line-rate chart, with fixed state f32 or estimated bf16, including foreground
reload and pending catch-up in the decision. Conservative foreground share and
saving equal R8; append-only spill changes background bills, not its wait.

| Bits | Mbit/s | R8 share% | Design share% | Conservative share% | R8 saved s | Design saved s | Conservative saved s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32 | 100.0 | 29.776 | 29.568 | 29.776 | 19.384 | 19.314 | 19.384 |
| 32 | 300.0 | 45.970 | 45.482 | 45.970 | 24.293 | 24.227 | 24.293 |
| 32 | 1000.0 | 61.377 | 60.548 | 61.377 | 26.520 | 26.455 | 26.520 |
| 32 | 2500.0 | 69.492 | 68.349 | 69.492 | 27.187 | 27.123 | 27.187 |
| 16 | 100.0 | 38.974 | 38.575 | 38.974 | 21.504 | 21.437 | 21.504 |
| 16 | 300.0 | 55.418 | 54.829 | 55.418 | 25.347 | 25.282 | 25.347 |
| 16 | 1000.0 | 67.855 | 66.617 | 67.855 | 26.923 | 26.859 | 26.923 |
| 16 | 2500.0 | 73.496 | 71.857 | 73.496 | 27.366 | 27.302 | 27.366 |

### Client capacity at 300Mbit/s and 1Gbit/s

Calls per 8h day, obtained by multiplying the published 116-call group capacity
by 116. Local capacities remain unchanged; conservative foreground capacity is
identical to R8. Design pays pending compute before choosing each offload, so
its wait/capacity comparison includes the deferred shadow work.

| Client | Mbit/s | R8 calls/8h | Design | Conservative |
| --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 300.0 | 438.847 | 438.735 | 438.847 |
| M3 Max 128 GB (measured) | 1000.0 | 442.989 | 442.878 | 442.989 |
| M4 Max 128 GB (estimate) | 300.0 | 594.483 | 594.267 | 594.483 |
| M4 Max 128 GB (estimate) | 1000.0 | 600.877 | 600.668 | 600.877 |
| M5 Max 64 GB | 300.0 | 630.414 | 630.048 | 630.414 |
| M5 Max 64 GB | 1000.0 | 637.252 | 636.944 | 637.252 |
| M5 Max 128 GB | 300.0 | 668.103 | 667.790 | 668.103 |
| M5 Max 128 GB | 1000.0 | 674.402 | 674.125 | 674.402 |
| M5 Ultra 96 GB | 300.0 | 1280.984 | 1279.327 | 1280.984 |
| M5 Ultra 96 GB | 1000.0 | 1298.787 | 1297.596 | 1298.787 |
| M5 Ultra 256 GB | 300.0 | 1306.436 | 1304.563 | 1306.436 |
| M5 Ultra 256 GB | 1000.0 | 1321.193 | 1319.986 | 1321.193 |
| Strix Halo 128 GB | 300.0 | 284.363 | 284.312 | 284.363 |
| Strix Halo 128 GB | 1000.0 | 285.706 | 285.659 | 285.706 |
| DGX Spark 128 GB | 300.0 | 303.663 | 303.585 | 303.663 |
| DGX Spark 128 GB | 1000.0 | 304.673 | 304.613 | 304.673 |

### GLM Studio utilization headlines

Rows at 2 sessions/user/day and full Studio capacity,200k/1M, teams 50/500/5000,
and one/two users sharing a Studio. Costs are per requested session, including
API overflow. Studio capacity is per box, not per sharing user. API/all-server
columns retain their accepted basis; corrected storage and I/O affect hybrid.
The CSV also contains the 1/4-session demand rows.

| Team | Depth | Users/Studio | Demand | R8 hybrid | Design | Conservative | API | All-server R8→design→conservative | Studio capacity R8→design |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50 | 200000 | 1 | 2/day | 11.7425 | 11.7177 | 11.7425 | 0.4616 | 8.0242 → 8.0242 → 8.0242 | 26.779 → 26.760 |
| 50 | 200000 | 1 | capacity | 0.8929 | 0.8917 | 0.8929 | 0.4616 | 0.5993 → 0.5997 → 0.5993 | 26.779 → 26.760 |
| 50 | 200000 | 2 | 2/day | 9.9716 | 9.9468 | 9.9716 | 0.4616 | 8.0242 → 8.0242 → 8.0242 | 26.779 → 26.760 |
| 50 | 200000 | 2 | capacity | 1.5041 | 1.5014 | 1.5041 | 0.4616 | 1.1986 → 1.1994 → 1.1986 | 26.779 → 26.760 |
| 500 | 200000 | 1 | 2/day | 4.5207 | 4.4959 | 4.5207 | 0.4616 | 0.8024 → 0.8024 → 0.8024 | 26.779 → 26.760 |
| 500 | 200000 | 1 | capacity | 0.3535 | 0.3519 | 0.3535 | 0.4616 | 0.4195 → 0.4198 → 0.4195 | 26.779 → 26.760 |
| 500 | 200000 | 2 | 2/day | 2.7498 | 2.7250 | 2.7498 | 0.4616 | 0.8024 → 0.8024 → 0.8024 | 26.779 → 26.760 |
| 500 | 200000 | 2 | capacity | 0.4254 | 0.4219 | 0.4254 | 0.4616 | 0.4794 → 0.4798 → 0.4794 | 26.779 → 26.760 |
| 5000 | 200000 | 1 | 2/day | 3.7986 | 3.7738 | 3.7986 | 0.4616 | 0.4815 → 0.4815 → 0.4815 | 26.779 → 26.760 |
| 5000 | 200000 | 1 | capacity | 0.3535 | 0.3339 | 0.3415 | 0.4616 | 0.4195 → 0.4138 → 0.4195 | 26.779 → 26.760 |
| 5000 | 200000 | 2 | 2/day | 2.0277 | 2.0029 | 2.0277 | 0.4616 | 0.4815 → 0.4815 → 0.4815 | 26.779 → 26.760 |
| 5000 | 200000 | 2 | capacity | 0.3654 | 0.3500 | 0.3534 | 0.4616 | 0.4195 → 0.4198 → 0.4195 | 26.779 → 26.760 |
| 50 | 1000000 | 1 | 2/day | 11.9391 | 11.8464 | 11.9391 | 8.9221 | 8.0242 → 8.0242 → 8.0242 | 5.359 → 5.355 |
| 50 | 1000000 | 1 | capacity | 4.5225 | 4.4903 | 4.5225 | 8.9221 | 5.9893 → 5.9942 → 5.9893 | 5.359 → 5.355 |
| 50 | 1000000 | 2 | 2/day | 10.1682 | 10.0755 | 10.1682 | 8.9221 | 8.0242 → 8.0242 → 8.0242 | 5.359 → 5.355 |
| 50 | 1000000 | 2 | capacity | 7.6166 | 7.5530 | 7.6166 | 8.9221 | 5.9893 → 5.9942 → 5.9893 | 5.359 → 5.355 |
| 500 | 1000000 | 1 | 2/day | 4.7173 | 4.6246 | 4.7173 | 8.9221 | 4.8145 → 4.8145 → 4.8145 | 5.359 → 5.355 |
| 500 | 1000000 | 1 | capacity | 2.1268 | 1.7929 | 2.1268 | 8.9221 | 4.1925 → 4.1959 → 4.1925 | 5.359 → 5.355 |
| 500 | 1000000 | 2 | 2/day | 2.9464 | 2.8537 | 2.9464 | 8.9221 | 4.8145 → 4.8145 → 4.8145 | 5.359 → 5.355 |
| 500 | 1000000 | 2 | capacity | 2.2263 | 2.1582 | 2.2263 | 8.9221 | 4.1925 → 4.1959 → 4.1925 | 5.359 → 5.355 |
| 5000 | 1000000 | 1 | 2/day | 4.5568 | 4.1431 | 4.3964 | 8.9221 | 4.1726 → 4.1726 → 4.1726 | 5.359 → 5.355 |
| 5000 | 1000000 | 1 | capacity | 2.1268 | 1.7929 | 1.9471 | 8.9221 | 4.1326 → 4.1360 → 4.1326 | 5.359 → 5.355 |
| 5000 | 1000000 | 2 | 2/day | 2.7859 | 2.3722 | 2.6254 | 8.9221 | 4.1726 → 4.1726 → 4.1726 | 5.359 → 5.355 |
| 5000 | 1000000 | 2 | capacity | 2.2263 | 1.8585 | 2.0466 | 8.9221 | 4.1326 → 4.1360 → 4.1326 | 5.359 → 5.355 |

GLM growing-session default (two requested sessions/day, purchased Studio and
server) at the endpoint depths is also published in both cases:

| Team | Depth | R8 $/session | Design | Conservative |
| --- | --- | --- | --- | --- |
| 5 | 200000 | 83.9603 | 83.9355 | 83.9603 |
| 10 | 200000 | 43.8393 | 43.8145 | 43.8393 |
| 50 | 200000 | 11.7425 | 11.7177 | 11.7425 |
| 500 | 200000 | 4.5207 | 4.4959 | 4.5207 |
| 5000 | 200000 | 3.7986 | 3.7738 | 3.7986 |
| 5 | 1000000 | 84.1568 | 84.0641 | 84.1568 |
| 10 | 1000000 | 44.0359 | 43.9432 | 44.0359 |
| 50 | 1000000 | 11.9391 | 11.8464 | 11.9391 |
| 500 | 1000000 | 4.7173 | 4.6246 | 4.7173 |
| 5000 | 1000000 | 4.5568 | 4.1431 | 4.3964 |

## Expanded arithmetic intensity

`flop_per_byte.csv` now has 432 rows: six models × two depths × three clients ×
three links × two portions × two recurrent formats. Portion coordinates are
`r8.portion=1000` and `r9.large_portion=10000`; `r9.state_bits` supplies 32/16.
Qwen f32 state is measured 156894784B and bf16 is an estimate at 78447392B.
Only fixed recurrent state changes format; q8_0 KV is unchanged. Muse/Gemma/Qwen3
have zero recurrent state, so those format pairs share byte counts; their window
KV still follows `min(portion,window)`.

The review describes all R8 state as f32, but its Flash-Next and GLM rows used
inherited bf16 wire state (58834944B and 76300000B). R9 labels the distinction:
the new f32 rows expand/use117669888B and 152600000B, and 16-bit rows preserve
the old native wire values. Qwen R8 matches the 32-bit/1k subset. Unsupported
contexts alarm in all variants; that explains 576 intensity alarm cells rather
than R8's144. This remains a compute/byte necessary bound, excluding full server
latency, placement qualification, import and scheduling.

## Complete publication change audit

[ENGINE-CHANGES-R9-261030.csv](ENGINE-CHANGES-R9-261030.csv) lists all 24031 changed
or added numeric/alarm cells for **R8 → each published case**, with row coordinates
and full-precision values. New intensity combinations use `<absent>` for a new
row/column; native 16-bit Flash/GLM rows are matched to their real R8 counterpart.
All 24 old CSV bytes were checked against signed 82bb1e52 before comparison.
All 42 new CSVs were checked against structured engine results; all eight
schema/source/alarm/payload manifests and independent strict export bytes were
audited. Historical geometry/reference/accepted transcript values are unchanged.
[PERIMETER-NODES-R9-261030.csv](PERIMETER-NODES-R9-261030.csv) is a compact full
270-row node grid, independent of acquisition-basis duplicates. The report's
headline tables are views of those exact CSV values, not manually asserted
crossovers or substituted defaults.

Source/assumption custody: [PAPER-R9-SOURCES-261030.md](PAPER-R9-SOURCES-261030.md).

## Modules, gaps and validation

| Scope | Implementation |
| --- | --- |
| Immutable-KV migration, expected pending routing, daily flush and retention | `session_hosting.py` |
| Person/remote/GLM/capacity/offload bills | `paper_tables.py` |
| Combined perimeter fleets and shared GLM Studios | `paper_tables_r6.py` |
| Sampled R7 foreground pending-work integration | `paper_tables_r7.py` |
| Routing-aware people/GPU and expanded intensity | `paper_tables_r8.py` |
| Data-composed conservative cases and safe filtered IDs | `engine.py`, four conservative scenario files, `hosting-conservative.json` |
| New enum/format/portion inputs and provenance | `hosting.json`, `paper-tables-r9.json`, additive input contracts |
| Old-red witness, policy/retention/case contracts and bounded mutants | `tests/test_run9.py`, `tests/r9_controls.py` |

A missing/invalid policy alarms only its declared consumers. Retention gaps
leave routing, compute/migration and independent transcript/intensity available;
catch-up gaps leave local-only perimeter capacity and compute-only users/GPU
available. Promotion bandwidth is a background-I/O diagnostic and cannot corrupt
GPU costs. Retained-price and bandwidth quantities remain estimates, with no
silent replacement. Legacy wrappers continue on complete historical data.

Final suite: **226/226 pass**, exit 0,306.803s, including all 210 retained tests
and 16 new R9 tests. All nine legacy outputs are byte-identical. Engine Python,
Python tests and input JSON were frozen at identity
`3ecd77b50563148e5b72fa9c807a6b36d788e0e917743869ec5e24dd0cb538f4`; the final audit rechecks every file.
No such source/data/test changes followed final validation. Earlier successful
full runs preceded a named selector cleanup and corrected result notes; the
final run below binds the delivered source, not those earlier candidates.

| Exact command (repository root unless stated) | Actual exit | Evidence |
| --- | --- | --- |
| `TMPDIR="$PWD/.temp/hybrid-calc-r9-261030/tmp" python3 -m unittest discover -s calc/tests` | 0 | `unittest-final-03.log`,226 tests,306.803s |
| `TMPDIR="$PWD/.temp/hybrid-calc-r9-261030/tmp" python3 -m unittest discover -s calc/tests -p test_run9.py` | 0 | `focused-r9-02.log`,16 tests,11.719s; final suite includes the same claims |
| `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | 0 | `compile-01.log` |
| `python3 -m hybridcalc list` | 0 | `list-01.log` |
| `python3 -m hybridcalc sources paper-tables-r8 --set workload.sample_calls=1 --format json` | 0 | `sources-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --set workload.sample_calls=1 r8.depths.0=10000 r8.depths.1=20000 --strict --format json` | 0 | `clean-strict-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --set workload.sample_calls=1 r8.depths.0=10000 r8.depths.1=20000 --set hosting.catch_up=null --format json` | 0 | `gap-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --set workload.sample_calls=1 r8.depths.0=10000 r8.depths.1=20000 --set hosting.catch_up=null --strict --format json` | 1 | `gap-strict-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --set hosting.typo=1` | 2 | `unknown-01.log` |
| `python3 -m hybridcalc export paper-tables --output calc/out/paper` | 0 | `export-paper-tables.log` |
| `python3 -m hybridcalc export paper-tables-conservative --output calc/out/paper` | 0 | `export-paper-tables-conservative.log` |
| `python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper` | 0 | `export-paper-tables-r6.log` |
| `python3 -m hybridcalc export paper-tables-r6-conservative --output calc/out/paper` | 0 | `export-paper-tables-r6-conservative.log` |
| `python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper` | 0 | `export-paper-tables-r7.log` |
| `python3 -m hybridcalc export paper-tables-r7-conservative --output calc/out/paper` | 0 | `export-paper-tables-r7-conservative.log` |
| `python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper` | 0 | `export-paper-tables-r8.log` |
| `python3 -m hybridcalc export paper-tables-r8-conservative --output calc/out/paper` | 0 | `export-paper-tables-r8-conservative.log` |
| `python3 -m hybridcalc export paper-tables-r8 --strict --output .temp/hybrid-calc-r9-261030/independent` | 1 | `independent-strict-01.log` |
| `python3 calc/tests/r9_controls.py full_slot` | 1 | `control-full_slot.log` |
| `python3 calc/tests/r9_controls.py free_pending` | 1 | `control-free_pending.log` |
| `python3 calc/tests/r9_controls.py no_tail` | 1 | `control-no_tail.log` |
| `python3 calc/tests/r9_controls.py ram_forever` | 1 | `control-ram_forever.log` |
| `python3 .temp/hybrid-calc-r9-261030/audit.py` | 0 | `audit-final.log`,42 structured CSVs, eight manifests, strict byte reproduction, signed baseline custody and 24031 numeric/alarm change records |
| From `calc/tests`: `tectonic --only-cached --outdir ../../.temp/hybrid-calc-r9-261030/pgfplots paper_r9_smoke.tex` | 0 | `pgfplots-02.log`, all 42 CSVs parse at declared row counts, both cases plotted |

Logs, standalone process PIDs, durations, actual and expected exits are recorded
in `.temp/hybrid-calc-r9-261030/validation.json` and adjacent logs. No pipeline
masks a gate's exit. Default alarm/strict failures are reported as 1, unknown
input as 2; they are not called green checks. The all-supported-context strict
positive control returns 0, so a pre-existing context alarm does not explain the
planted-gap strict failure. Final checksum, staged-whitespace, scope and
signature verification are local delivery gates; no remote CI was invoked.

The initial immutable-prefix regression was observed **red on unmodified R8**:
`test_append_only_spill`, same unittest discovery command while that file held
its first single test, exit 1,0.005s,5442729584B !=216129584B. The first positive
fixture used a seconds-to-bytes round trip and exposed a floating equality
artifact; comparison now uses exact expected bytes/bandwidth in seconds.
Initial focused policy tests also exposed fixture arithmetic and a day-range
contract expectation, corrected before the final suite. A first native-smoke
setup ran its file-generation snippet from the wrong cwd and exited 1; corrected
root generation and the explicit native command above exited 0. These diagnostic
failures are preserved, not counted as passing evidence.

### Finite protocol/table/gap claims

| Claim | Named test |
| --- | --- |
| Immutable past KV; exact 216129584B spill and full-prefix reload | `test_append_only_spill` |
| Pending input/output moves onto foreground and can reject a marginal offload; unchanged total compute | `test_pending_compute_enters_decision` |
| Zero/all-offload boundaries are finite and preceding output is accounted | `test_zero_and_all_offload` |
| Offloaded calls+one daily-tail reload per active session; appended KV once and state per flush | `test_daily_reload_spill_conservation` |
|8h/24h retention fractions, calendar-window alarm, promotion excluded from GPU time | `test_retention_windows_and_promotion` |
| Parallel cases preserve row coordinates and complete person bills; compute per call invariant | `test_person_and_parallel_cases` |
| Client capacities/offload savings include pending; conservative foreground matches old policy | `test_offload_and_client_capacity` |
| Remote rent/buy prices each 10h/24h storage window | `test_remote_windows` |
| Perimeter combined fleets, no outside route and reconciled GLM cases | `test_perimeter_and_glm_cases` |
| People/GPU downward integer bound including actual routing/day-tail I/O | `test_people_per_gpu` |
| All four portion/format combinations; bf16 fixed half, unchanged KV, context alarms | `test_intensity_variants` |
| Every new enum/portion/format quantity deletion alarms each declared consumer | `test_every_new_input_gap` |
| Null/NaN/inf/negative/wrong units/missing provenance, unknown enums/format24 and zero portion | `test_new_contracts_and_corners` |
| Retention gap leaves waits/compute/I/O intact; RAM-only ignores unused NVMe | `test_retention_gap_control` |
| Accepted exact compute-only headline grid 60/24/12 and 271/108/54 | `test_accepted_compute_only_headline` |
| Catch-up gap leaves local-only perimeter and compute-only bounds available | `test_catchup_gap_control` |

Retained tests continue to cover the accepted measured-tail/global/depth fit,
full-shadow two-node regression, output-only and transcript tables, all prior
quantity contracts, missing/corrupt measured packages, cost/transfer invariants,
load/residual/context boundaries, client fit and independent architecture oracle.
The old calc9 reproduction test explicitly selects its historical sampler,
resident copy and per-call policy; none of its numeric assertions were dropped.
RAM-price linearity/zero-price tests now price **both** paid tiers when testing
the aggregate storage bill. Removing RAM price alone correctly leaves NVMe cost.

### Narrowing mutants

| Mutant | What it narrows the gate to | Named failing test | Actual exit |
| --- | --- | --- | --- |
| `full_slot` | Exact R8 forbidden full-prefix rewrite, rather than append-only KV | `test_append_only_spill` | 1 |
| `free_pending` | Foreground pending must change wait and offload selection | `test_pending_compute_enters_decision` | 1 |
| `no_tail` | The terminal reload/state overwrite is paid, including no-offload days | `test_daily_reload_spill_conservation` | 1 |
| `ram_forever` | Tiered cost uses actual active-window fraction, rather than month-long RAM | `test_retention_windows_and_promotion` | 1 |

All four are bounded in-memory plants; each has its named AssertionError and no
setup error. No selected mutant survived. The initial exact old-source spill
failure supplements these controls. Unplanted serving/scheduling behavior is
outside this finite evidence, not implicitly covered.


## Limits

- Four retained copies, active-session allocation, mean retained depth, stationary
  local runs, daily-tail snapshot depth, storage prices/bandwidth and occupied
  GPU I/O time are estimates. Day-boundary run truncation, realistic retention,
  engine journal behavior, overlap, reload scheduling and queues need measurement.
- Mean pending work on critical paths is an aggregate model, not an event-level
  session replay. The compute bill remains one prefill per input/output token;
  no physical implementation or zero-latency background readiness is claimed.
- Existing alternative HBM/NVMe diagnostic overrides do not redefine the two
  published RAM-based cases. Own all-server accounting is inherited from the
  accepted engine and is not silently reparameterized by hybrid storage.
- Measurements, source prices, compute-only bounds and no-outside-fallback
  perimeter policy remain accepted inputs; no live URL/price verification,
  new hardware measurement or tool installation occurred.
- Linux Python execution and retained Python3.9 grammar checks are available;
  no native macOS/Python3.9 run. Self-review only, ready for review; no hosted CI,
  independent acceptance or landing claimed. The brief supplied no acceptance
  surface table; coverage is the named finite protocol/table/input contracts.
- No requested case/table is out of contract or omitted. Cross-file changes are
  limited to the calculation engine/data/tests, generated outputs and required
  documentation. No runtime/infrastructure, publication branch or forbidden path
  was modified.

---

# Historical run 8 and earlier evidence (hosting numbers superseded above)

# Calculation engine — run 8, hybrid-calc-r8-261030

Continues signed `574f427bd00a7eeadf9eb313c9003a7191585383` on `calc-engine`.
Ready for review; local signed delivery only, no push, installs or network
research. The two cited review reports and their probes were read before edits:
`/home/agent/Werkstatt/hybrid-review/paper/.temp/REVIEW-paper-v010.md`
(M01/M02/M12), `REVIEW-paper-v010-claude.md` (B3/M1/M2/M3),
`review-claude/probe_perimeter_allshadow.py` and `probe_server_seconds.py`.
This report's R8 section supersedes the publication numbers in the historical
reports below. The exact baseline is the preserved R7 workbench, not an assertion
that upstream paper commit `c95f6cb` is the same Git object.

## Corrections and accounting design

1. **Full server shadow.** Every client-served input AND output is prefilled on
   the server, whether that input portion was read locally or offloaded.
   The previous perimeter graph charged new-input shadow only on offloaded
   calls. That was a defect, unlike the already-correct `person_tables` path.
   All-server requests prefill input and decode output once; they do not get a
   redundant output-prefill charge.
2. **Measured sampler.** Current `paper-tables`, `paper-tables-r6`,
   `paper-tables-r7` and new `paper-tables-r8` explicitly select `measured_tail`.
   The old clipped lognormal was an estimate with a badly oversized token tail.
   The fitted joint depth-bin/token-band distribution matches pooled all-agent
   token-mass tails and conditional means, with a maximum-entropy tilt and
   stratified draws. Low quantiles shape the sub-2k band. At the full 39,904-call
   size, band token masses and depth/new/output/reasoning global means are
   normalized; six depth quantile anchors and sampled bin counts are retained.
   Within-bin means differ by less than 20 tokens due to sampled bin counts and
   integer strata. Fit support/tolerance/iterations/minimum size and quantile
   coordinates are provenance-bearing inputs. Inconsistent fits alarm.
3. **Session hosting.** The prior server-copy residency/migration budget was
   absent. New `hosting.json` makes it explicit: HBM/RAM/NVMe, retained sessions
   per person, full-month fraction, incremental USD/decimal-GB-month, and
   effective PCIe/tier bandwidth per GPU replica. Default RAM is **an estimate**:
   four sessions/person, fraction 1, $0.50/GB-month, PCIe50GB/s and RAM100GB/s.
   It represents a separately provisioned storage pool budget, not a RAM tariff
   hidden inside the GPU price. Mean retained end-of-call bytes × sessions ×
   month fraction × tier price gives storage/person-month. No session chronology
   or retention duration has been measured.
4. **Cold-tier work.** Prefix reload is `(depth*KV+state)/min(PCIe,tier BW)`;
   updated-slot spill is `((depth+new+decoded)*KV+state)/min(...)`. Empty fresh
   prefixes have zero reload. Both are conservatively billed as occupied GPU
   time, including background shadow for locally read calls: cold full server
   copies cannot update without old KV. Only offloaded reload blocks the client;
   spill/background work is asynchronous and assumed ready for the next turn.
   HBM residency has zero PCIe migration and its own explicit storage price.
   GPU overlap, hot caches or longer retained histories can change this budget;
   no such saving is silently assumed.
5. **Complete bills.** Person tables expose compute, hosting, storage and
   migration month costs, plus compute/hosting USD per served call;
   `gpu_month=compute_month+hosting_month`. Reload/spill time enters integer
   perimeter/GLM/remote prefill fleets; retained storage is paid separately.
   API overflow remains fully costed. Remote buy/rent adds the same storage
   budget to both choices and sizes migration work before comparing them.
   R7 existing-prefix timings expose `server_reload_s`; cold one-shot inputs
   have no old prefix. No outside fallback was added to the perimeter path.
6. **Output sensitivity.** Fraction 1 remains the conservative default; pooled
   output 511.9 plus reasoning 207.7 gives 719.6 decoded tokens/call after fitting.
   Fraction 0 counts output 511.9 alone. The prior finite lognormal sample had
   about 703 decoded tokens. Counter overlap is unresolved, not a claimed bug
   in the measured counters. Both policies now have published capacity, API and
   whole-demand hybrid costs in separate auditable input scopes.

All new quantities carry units/provenance and contracts. Cached metric graphs
propagate missing/null/invalid inputs to dependent cells, with no numeric
fallback. A hosting-price gap leaves capacities and compute-only bills intact;
PCIe gaps affect cold tiers while HBM remains independent. Ordinary partial
runs exit 0; strict alarm runs exit 1. Unknown overrides remain exit 2. Legacy
wrappers operate on complete historical inputs and keep byte-identical output;
canonical gaps never rewrite their old text.

### Sampler targets and corpus distinction

The brief's1984/690 depth-bin endpoints are Claude-only (1983.8/689.7).
The consistent pooled corpus used by the paper has 1864.2/729.2. Mixing those
Claude conditional means with pooled tails/overall means would be incorrect.
Hash-checked `stats.json` is the source of every target. Measured package/file
SHA256 values remain in `*_sources.json`; no measurement package was edited.

| Token threshold | Old token-mass share (review, approximate) | Measured/fitted target |
| --- | --- | --- |
| >=2k | 73% | 75.6% |
| >=5k | 55% | 51.1% |
| >=10k | 41% | 21.3% |
| >=30k | 20% | 4.2% |

The fit preserves the **measured** global means, correcting finite clipped-draw
bias in the old sample rather than retaining that bias:

| Per-call quantity | Old 39,904-call sample | New sample / measured target |
| --- | --- | --- |
| Depth, tokens | 171641.0751 | 164437.3 |
| New input, tokens | 1004.7169 | 1066.4 |
| Output+reasoning, tokens | 703.3651 | 719.6 |
| Full input/output shadow, TFLOP | 196.6926 | 200.6414 (derived, not a separately measured target) |

Measured pooled means are depth 164437.3 and new 1066.4. Six depth anchors
p10/p25/p50/p75/p90/p99 are 57744/89042/135362/190258/250202/826234.9;
the fitted sample preserves their ranks within the stated stratification error.
A first development fit matched the mean by contracting whole bins; self-review
replaced it before publication because it distorted the p90/p99 memory tail.
Samples below the explicit 4096-call full-calibration threshold are finite-sample
approximations, not publication replacements. Marginal aggregates cannot recover
real session chronology, all joint correlations or scheduler behavior.

### Shadow regression: isolate the fix, then add the new hosting assumption

| 5000 light users, M5 Max 64, B300 owned node | B300 nodes | Basis |
| --- | --- | --- |
| Baseline perimeter chart | 1 | Defective selected-only new-input shadow |
| Full-shadow regression on the original sample | 2 | Original sampler, HBM/resident copy isolates migration; reviewed boundary |
| Final R8 perimeter chart | 3 | Calibrated depth/tail/output mix AND full cold-RAM reload/spill |

The exact two-node witness is `test_full_shadow_two_node_boundary`; it failed
with 1 on the unmodified implementation. Three in the regenerated default row
is a new explicitly costed migration assumption, not failure of that witness.

## New named tables and CSVs

| Table | Rows | CSV | Alarm cells |
| --- | --- | --- | --- |
| output_only_sensitivity | 16 | [CSV](out/paper/output_only_sensitivity.csv) | 0 |
| people_per_gpu | 6 | [CSV](out/paper/people_per_gpu.csv) | 0 |
| transcript_example | 6 | [CSV](out/paper/transcript_example.csv) | 0 |
| flop_per_byte | 108 | [CSV](out/paper/flop_per_byte.csv) | 144 |

Run `python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper`.
The four `r8_*.json` sidecars record schema/label mappings, sources, exact
alarms and generation/payload hashes. All four families were regenerated.
There are 144 new alarm cells:36 unsupported model/depth rows × four dependent
intensity columns. Muse/Gemma at 1M and Qwen3-32B at 110k/1M exceed their config
contexts. Their byte geometry and client peak/link bounds remain available.
No people/GPU, transcript, output-sensitivity or perimeter cells alarm.
Existing families retain 329 R5,6 R6 and 28 R7 expected alarm cells.

### People per GPU

Full input/output shadow at Q4, 8h/day,70% target load,2500 heavy calls/day before
Mac admission/caps. Integer people round DOWN; storage is separately shown in
USD/person-month. This is an offered-demand bound, not a per-Mac throughput claim.

| GPU | Open share | Compute-only people | Including cold migration |
| --- | --- | --- | --- |
| RTX PRO 6000 hourly | 0.2 | 60 | 44 |
| RTX PRO 6000 hourly | 0.5 | 24 | 17 |
| RTX PRO 6000 hourly | 1 (academic bound) | 12 | 8 |
| B300 288 GB hourly | 0.2 | 271 | 104 |
| B300 288 GB hourly | 0.5 | 108 | 41 |
| B300 288 GB hourly | 1 (academic bound) | 54 | 20 |

Default full-copy compute is 0.663760s/call on RTX PRO6000 and 0.148623s on
B300, with 0.236707s/call reload+spill on either at the stated bandwidth; storage
is$11.8976/person-month on the pooled full mix. These storage/migration numbers
are explicitly estimated inputs applied to measured geometry, not measurements.

### Transcript and arithmetic-intensity examples

Transcript:70k fresh input and exactly 3k summary tokens, one stream. Local TTFT
integrates the measured M3 curve (M5 scaled by declared compute); hybrid TTFT
pays integrated B300 prefill, full KV/state transfer, estimated import and final
client evaluation. Both totals add the same depth-dependent single-stream
summary decode. Fresh input uses API cache-write prices; no cache-read or extra
reasoning charge is invented. M5 Max 64 and M5 Air 32 are unmeasured estimates.
The Air requires an explicit 8GB OS/app appliance reserve; the standard 12GB
reserve raises a nonfit alarm. This is exposed in the row and tested, not hidden
as a fallback. No hardware purchase is implied by a timing estimate.

FLOP/byte: six model architectures,110k and 1M where allowed,1k portions including
fixed state and sliding-window `min(portion,window)` bytes. Qwen uses measured
34844B/token+156894784B state; Flash-Next uses the inherited sparse active-parameter
approximation, GLM the inherited prefill model and declared bf16 wire state;
Muse/Gemma/Qwen3 use R7 config formulas and URLs. For each M3 Max/M5 Max/M5 Ultra
peak envelope and 200M/1G/10G link, ratio is model FLOP/byte divided by client
peak FLOP/s per link byte/s. Ratio>1 beats an ideal compute-only local bound on
transfer alone. It is not end-to-end speedup or a memory/engine qualification;
server/import cost is excluded. Qwen1M remains an estimated engine extension.

## Every changed publication number

[ENGINE-CHANGES-R8-261030.csv](ENGINE-CHANGES-R8-261030.csv) enumerates **18272**
changed or newly added cells across the previous 20 chart CSVs:14660 existing
cells and 3612 new numeric-column cells. Each record includes filename,
zero-based row, column, row coordinates, full-precision old/new values and
reason. `<absent>` marks a new explicit accounting column. The R7 baseline
copies were preserved before edits; chart ordering/coordinates are checked.
New charts have no historical counterpart; their complete numbers are their
own CSVs. The ledger includes repeated values in profile-specific perimeter
charts, so every published location is accounted for.

| Prior chart | Changed/new cells | Final alarms |
| --- | --- | --- |
| person_cost_s20 | 1110 | 0 |
| person_cost_s50 | 1214 | 0 |
| person_cost_academic_s100 | 1294 | 0 |
| crossover_explanation | 0 | 0 |
| remote_rent_buy | 822 | 252 |
| client_sessions_day | 75 | 0 |
| offload_by_link | 24 | 0 |
| traffic_user_month | 31 | 0 |
| glm_long_sessions | 193 | 0 |
| client_fit_deep | 0 | 77 |
| perimeter_cost | 6444 | 0 |
| perimeter_cost_light | 1596 | 0 |
| perimeter_cost_medium | 2207 | 0 |
| perimeter_cost_heavy | 2641 | 0 |
| glm_utilization | 353 | 0 |
| decode_scaling | 0 | 6 |
| turn_speedup | 144 | 0 |
| oneshot_ingest | 36 | 0 |
| decode_sensitivity | 88 | 24 |
| arch_compare | 0 | 4 |

Historical crossover, deep fit, decode bounds and attached architecture
numbers remain unchanged. One-shot previous numeric fields are unchanged;
its added reload column is explicitly zero. The architecture still reproduces
all 58 original f32 numeric values, with the same None-to-context-alarm treatment.

### Offload headline, old → new

Raw-line-rate chart, saving averaged over ALL calls, including zero savings on
local calls. New policy includes the declared cold-prefix reload. State 16 is
an estimated wire representation, not measured engine compatibility.

| State bits | Mbit/s | Old share % | New share % | Old saved s/call | New saved s/call |
| --- | --- | --- | --- | --- | --- |
| 32 | 100.0 | 27.253 | 29.776 | 19.257 | 19.384 |
| 32 | 300.0 | 48.153 | 45.970 | 23.973 | 24.293 |
| 32 | 1000.0 | 67.702 | 61.377 | 26.266 | 26.520 |
| 32 | 2500.0 | 77.316 | 69.492 | 26.977 | 27.187 |
| 16 | 100.0 | 39.021 | 38.974 | 21.289 | 21.504 |
| 16 | 300.0 | 59.788 | 55.418 | 25.090 | 25.347 |
| 16 | 1000.0 | 75.383 | 67.855 | 26.714 | 26.923 |
| 16 | 2500.0 | 81.543 | 73.496 | 27.176 | 27.366 |

### Client capacity, old → new

At 300Mbit/s, supported mix, measured four-stream law with per-call memory limits;
counts are 116-call normalization groups/day, not reconstructed sessions.
The change includes the fitted output mean and paid prefix reload. All other
links and local capacities are fully enumerated in the ledger.

| Client | Old groups/8h | New groups/8h |
| --- | --- | --- |
| M3 Max 128 GB (measured) | 3.838 | 3.783 |
| M4 Max 128 GB (estimate) | 5.201 | 5.125 |
| M5 Max 64 GB | 5.501 | 5.435 |
| M5 Max 128 GB | 5.849 | 5.760 |
| M5 Ultra 96 GB | 11.219 | 11.043 |
| M5 Ultra 256 GB | 11.445 | 11.262 |
| Strix Halo 128 GB | 2.489 | 2.451 |
| DGX Spark 128 GB | 2.659 | 2.618 |

### M5 Max 64 per-person costs, old → new

Economics uses the declared 1Gbit/s WAN path (separate goodput), not the 300Mbit/s
capacity slice above. Its capacity is 645.062→637.252 calls/day. All requested
open calls are paid, including median/cheapest-priced API overflow; common
closed-model spending remains excluded. Hybrid costs are flat over team sizes
because this is a shared prefill service. Values below apply to team 5 and are
the same at the other listed team sizes for the same client/basis.

| Share | Client basis | Old median-total $ | New median-total $ | Old cheapest-total $ | New cheapest-total $ |
| --- | --- | --- | --- | --- | --- |
| s20 | Mac already owned | 19.66 | 40.48 | 18.18 | 39.37 |
| s20 | Mac premium bought | 54.87 | 75.69 | 53.38 | 74.58 |
| s50 | Mac already owned | 156.26 | 177.26 | 41.76 | 65.61 |
| s50 | Mac premium bought | 191.47 | 212.46 | 76.97 | 100.82 |

The added hosting budget materially changes conclusions: hybrid is cheaper
than the median API on these rows, but the cheapest API alone remains cheaper
than the hybrid total. A general claim of beating the cheapest API is unsupported.

### Output-only sensitivity, conservative 1 → output-only 0

Team 50, Mac already owned. Capacity is calls/8h; all costs are USD/person-month.
Both purchase bases are in the CSV; the premium is unchanged across policies.

| Client | Share | Capacity | Hybrid median | API median | Hybrid cheapest | API cheapest |
| --- | --- | --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 0.2 | 442.99 → 616.17 | 51.25 → 40.83 | 107.07 → 101.67 | 40.97 → 40.83 | 16.91 → 14.10 |
| M5 Max 64 GB | 0.2 | 637.25 → 883.06 | 40.48 → 39.74 | 107.07 → 101.67 | 39.37 → 38.63 | 16.91 → 14.10 |
| M3 Max 128 GB (measured) | 0.5 | 442.99 → 616.17 | 211.86 → 174.69 | 267.68 → 254.17 | 66.33 → 63.68 | 42.27 → 35.24 |
| M5 Max 64 GB | 0.5 | 637.25 → 883.06 | 177.26 → 129.70 | 267.68 → 254.17 | 65.61 → 63.83 | 42.27 → 35.24 |

## Module map

| Scope | Implementation |
| --- | --- |
| Historical calc2–9/sensitivity | Existing legacy modules/wrappers unchanged |
| Current measured aggregate fit | `workload.py`, `sampler_fit.py`, declarations in `analysis_graph.py` |
| Retained copy storage/reload/spill | `session_hosting.py`, provenance-bearing `hosting.json` |
| Person/remote/GLM/capacity/traffic/offload charts | `paper_tables.py` |
| Full perimeter shadow and combined fleets / Studio utilization | `paper_tables_r6.py` |
| Existing-prefix turn timing and sensitivity reload | `paper_tables_r7.py`; architecture oracle unchanged |
| Four new named examples/sensitivity | `paper_tables_r8.py`, `paper-tables-r8.json` and composed scenario |
| Regression/gap/corner/export claims | `tests/test_run8.py`; prior tests retained under original names |

## Validation and narrowing controls

Final full suite: **210/210 passed**, exit 0,266.931s, retaining all 190 previous
tests under their original names plus 20 R8 tests. All nine legacy wrappers
remain byte-identical. The Python3.9 grammar/standard-library compatibility check
is included in the retained suite; execution used the existing Linux Python.
Final Python/test/data identity is
`c95b9693ec7004fb1f0d338508189ef4b9f8fc21fc410b189074e2092e19caa0`.
No Python/data/test changes followed that final run. Audit-03 verifies this
identity, all 24 CSVs against structured results, every payload/generator hash,
old chart bytes against signed 574f427b, and independent strict R8 export bytes.
CLI/export/control evidence is bound to the same generator and affected test
sources; the sole later test change was the explicit historical calc9 selector.

| Exact command (from repository root unless stated) | Actual exit | Evidence / claim |
| --- | --- | --- |
| `TMPDIR="$PWD/.temp/hybrid-calc-r8-261030/tmp" python3 -m unittest discover -s calc/tests` | 0 | `unittest-final-02.log`,210 tests,266.931s |
| `python3 -m unittest discover -s calc/tests -p test_run8.py` | 0 | `focused-r8-05.log`,20 tests,20.549s |
| `TMPDIR="$PWD/.temp/hybrid-calc-r8-261030/tmp" PYTHONPATH=calc:calc/tests python3 -m unittest test_paper_tables.PaperAdditionalCorners.test_offload_legacy_d` | 0 | Historical selector/oracle preserved,6.135s |
| `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | 0 | `compile-01.log` |
| `python3 -m hybridcalc list` | 0 | `list-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --format json` | 0 | `run-01.log` |
| `python3 -m hybridcalc sources paper-tables-r8 --set workload.sample_calls=1 --format json` | 0 | `sources-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --set workload.sample_calls=1 hosting.tiers.RAM.price=null --format json` | 0 | `gap-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --set workload.sample_calls=1 hosting.tiers.RAM.price=null --format json --strict` | 1 | `gap-strict-01.log` |
| `python3 -m hybridcalc run paper-tables-r8 --set r8.unknown=1` | 2 | `unknown-01.log` |
| `python3 -m hybridcalc export paper-tables --output calc/out/paper` | 0 | `export-r5-02.log` |
| `python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper` | 0 | `export-r6-02.log` |
| `python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper` | 0 | `export-r7-01.log` |
| `python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper` | 0 | `export-r8-01.log` |
| `python3 -m hybridcalc export paper-tables-r8 --strict --output .temp/hybrid-calc-r8-261030/independent` | 1 | `export-strict-01.log` |
| `python3 calc/tests/r8_controls.py shadow` | 1 | `control-shadow-01.log` |
| `python3 calc/tests/r8_controls.py tail` | 1 | `control-tail-01.log` |
| `python3 calc/tests/r8_controls.py hosting` | 1 | `control-hosting-01.log` |
| `python3 calc/tests/r8_controls.py output` | 1 | `control-output-01.log` |
| `python3 .temp/hybrid-calc-r8-261030/audit.py` | 0 | `audit-03.log`,24 structured CSVs, hashes, independent strict bytes and baseline custody |
| From `calc/tests`: `tectonic --only-cached --outdir ../../.temp/hybrid-calc-r8-261030/pgfplots paper_r8_smoke.tex` | 0 | Preinstalled tool; all four R8 files parse and row counts agree; `pgfplots-01.log` |

All logs and process statuses are under `.temp/hybrid-calc-r8-261030/`;
`validation.json` records the 16 CLI/compile/export/control processes with exact
arguments, cwd, duration and real exit. Strict/nonfinite/context failures are
reported failures, not green statuses. Final compile replay (`python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py`)
exited 0 (`compile-final-01.log`). The 226-entry tracked-file SHA256 manifest
and scoped staged checks are local delivery gates. The first whitespace check
exited 2 because the audit CSV writer used CRLF; the ledger was normalized to LF
without changing any parsed values, and its writer corrected. No engine or
chart numbers changed in this formatting correction. Signature verification
uses `git verify-commit HEAD` and `%G?` after signed local commit creation.

### Diagnostic failures retained honestly

- Before implementation, `python3 -m unittest discover -s calc/tests -p test_run8.py`
  ran the first three review tests on original source: exit 1, three intended
  AssertionErrors,4.199s, `regressions-old-red-01.log`; no setup errors.
- The first focused R6/R7 run exited 1 with two reconciliation tests still
  omitting the newly paid storage/reload terms. Their assertions now include
  those explicit components; names and prior physical claims remain.
- Early R8 gap tests exposed double-scoped sweep alarm labels. The mapping was
  corrected before final validation; the same tests now demand the exact root
  input on every affected cell, including a missing entire sweep.
- The first 210-test full run exited 1 (271.963s), with only
  `test_offload_legacy_d` expecting the historical calc9 values from the newly
  calibrated default. It now explicitly selects `legacy_lognormal` and HBM.
  The original name and all frozen numeric assertions remain. The final suite
  above supersedes that failed diagnostic candidate; it is not counted green.

### Corner/gap coverage

| Claim / boundary | Named tests |
| --- | --- |
| Four named charts, declared cells, exact export values / deterministic bytes | `test_named_tables`, `test_csv_export` |
| Every one of 56 new quantities is consumed and deletion alarms declared consumers; null/NaN/inf/negative/wrong unit/missing provenance and permitted zero | `test_every_new_input_gap`, `test_new_input_contracts` |
| Measured token tails, conditional/global means and depth quantile tail | `test_measured_token_tail`, `test_conditional_means_and_global_means` |
| Original full-shadow 2-node boundary / explicit GPU-month split | `test_full_shadow_two_node_boundary`, `test_hosting_is_in_gpu_month` |
| Missing hosting price leaves unrelated tables and capacity/compute unchanged | `test_hosting_price_gap_control` |
| HBM no-PCIe versus RAM/NVMe read+spill; zero tier price/fraction and invalid PCIe/load/link | `test_tier_reload_and_pcie_gap`, `test_zero_and_nonfinite` |
| Downward-rounded people/GPU, complete transcript bills/tariffs, fixed-part intensity/context guards | `test_people_per_gpu`, `test_transcript_example`, `test_flop_per_byte` |
| Output-only policies remain distinct and change decode, compute and API bills | `test_output_only_sensitivity` |
| Air 12GB nonfit, valid 8GB neighbor, zero summary and zero-depth intensity | `test_transcript_fit_and_zero_summary` |
| Team 1, missing/invalid sweep shape, unsupported fit/support/nonconvergence, empty/single call | `test_sensitivity_corners`, `test_sampler_corners` |
| Missing/hash-corrupt measured packages, missing whole layers and unknown override | `test_measurement_and_layer_gaps` |
| Storage price linearity and larger PCIe monotonicity | `test_hosting_monotonic_and_linear` |

Existing tests retain transfer/compute/cost invariants, context/depth boundaries,
load 0/1, residual 0/1, complete overflow costs, per-call memory admission, frozen
architecture oracle and legacy control plants. These tests establish the stated
finite contracts, not unmeasured scheduling/kernel performance.

### Narrowing mutant evidence

| Mutant | What it narrows the gate to | Named failing test | Actual exit |
| --- | --- | --- | --- |
| `shadow`: drop new-input shadow, keep output shadow | Original-mix large-team boundary pays new-input work too | `test_full_shadow_two_node_boundary` (1 !=2) | 1 |
| `tail`: return uncalibrated lognormal calls | Calibration actually constrains measured token-mass tails | `test_measured_token_tail` | 1 |
| `hosting`: erase storage and migration budgets | Hosting must be positive and explicit in GPU/month | `test_hosting_is_in_gpu_month` | 1 |
| `output`: collapse both policies onto fraction 1 | The output-only sweep cannot silently duplicate the default | `test_output_only_sensitivity` | 1 |

All four controls are bounded in-memory changes, with named AssertionErrors and
no setup errors. No selected mutant survived. The original three-test old-red
run additionally exercises the exact pre-fix implementation rather than just
an approximation of its defects. No claim is made about unplanted mutants.


## Limits and review status

- All pricing, storage retention, copy/import/PCIe occupation, equal-FLOP
  portability and unmeasured hardware/GLM kernels remain estimates with explicit
  inputs. These tables do not establish a working hybrid runtime or memory tier.
- Full04 pooled measurements and Full05 call dates remain separate snapshots.
  Synthetic sample groups are not calendar sessions. Output/reasoning overlap,
  background readiness, transfer overlap, queue delay and state compatibility
  require measurement; see `UNRESOLVED_QUESTIONS.md`.
- Historical `owners-economics`, `owners-paper`, service/crossover references
  and legacy scripts retain their dated sampler/accounting, labelled references;
  new corrected publication claims use the regenerated `paper-tables*` families.
  No previous crossover threshold is promoted to a new hosting-aware crossover.
- Linux system Python execution and Python3.9 grammar checks are available;
  native macOS/Python3.9 execution was not performed. No tools were installed.
- Self-review only; no hosted CI, independent acceptance or landing is claimed.
  No acceptance surface table was supplied; finite coverage is the stated
  regressions/table/gap contracts, not a universal proof of every serving model.
  No out-of-contract requested chart was omitted. Cross-file changes are limited
  to the engine/data/tests, generated publication artifacts and required docs.

---

# Historical run 7 and earlier evidence (publication numbers superseded above)

# Calculation engine — run 7, hybrid-calc-r7-261030

Continues reviewed signed `f01f32ad` on `calc-engine`. Ready for review; signed local delivery, no push, network research, installs or changes under the forbidden directories. Scope is exactly four new scenario tables and their provenance, tests and documentation. Existing R5/R6 CSVs are byte-identical; only their generation-audit manifests are refreshed.

## Four named tables

| Table | Rows | CSV | Default alarm cells |
| --- | --- | --- | --- |
| turn_speedup | 48 | [CSV](out/paper/turn_speedup.csv) | 0 |
| oneshot_ingest | 36 | [CSV](out/paper/oneshot_ingest.csv) | 0 |
| decode_sensitivity | 32 | [CSV](out/paper/decode_sensitivity.csv) | 24 |
| arch_compare | 8 | [CSV](out/paper/arch_compare.csv) | 4 |

```bash
python3 -m hybridcalc run paper-tables-r7 --format json
python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper
python3 -m hybridcalc sources paper-tables-r7 --format json
```

`r7_schema.json`, `r7_sources.json`, `r7_alarms.json` and `r7_manifest.json` coexist with the earlier artifacts. Every canonical cell declares its dependencies. CSV noncomputable cells are `nan`, with `status=alarm` and input paths; detailed reasons are in the alarm sidecar. Ordinary default export exits 0. Strict export exits 1 after identical bytes because the default deliberately includes impossible/unsupported cases.

## Timing basis and assumptions

Large turns and one-shot loads use Qwen3.8-27B Q4, measured q8_0 slot slope **34,844 B/token**, M3 Max measured marginal prefill curve and one B300 at the existing **1.35 PFLOP/s effective compute** (quantized tensor envelope × MFU). Local seconds/token and server FLOPs are integrated across the same token span with a refinement-tested 256-token midpoint step. The local curve uses actual segment midpoints, holds its first rate below the first midpoint and holds FLOP efficiency beyond the last. This is a curve-derived estimate, not a measured cold-ingest/remote-turn time.

Both recurrent-state variants are present: f32 **156,894,784 B**, measured affine fixed part; bf16 **78,447,392 B**, estimated half. KV remains q8_0 in both. Client/server weight, reserve/workspace and full-context admission checks apply; standalone spans cannot exceed the benchmark’s 262,144-token limit.

`hybrid = server_prefill + transfer + import + last_token_evaluation`.

- Transfer includes the payload for the delta (whole context for one-shot) and one fixed state: `RTT + (tokens × KV + state) × 8 / (link × goodput)`. Default goodput 1 and RTT 0 are explicit line-rate inputs.
- No isolated delta-import measurement exists. Full slot restores include filesystem/cache effects. The explicit import estimate is one serial copy at 10% nominal client bandwidth, **40 GB/s on M3**, plus zero fixed overhead. It can be overridden without code edits; parsing/conversion/runtime overhead may be higher.
- Last-token work is one final-depth single-stream decode-equivalent evaluation after import, conservatively charged in addition to the full payload. Its deep-context rate is estimated from the measured M3 anchor. No extra resident token is allocated by this bookkeeping step.
- No compute/transfer/import overlap, model cold start, extra upload, queueing or runtime compatibility is inferred. Bf16 state equivalence and quality remain unqualified.

Full turn results (both state formats), with speeds at each requested link:

| State | Depth | Portion | Local s | 50 Mbit/s × | 100 × | 200 × | 300 × | 1000 × | 10000 × |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f32 | 100000 | 2000 | 43.013 | 1.18 | 2.34 | 4.61 | 6.81 | 20.58 | 93.83 |
| f32 | 100000 | 10000 | 218.358 | 2.67 | 5.29 | 10.37 | 15.24 | 44.60 | 173.71 |
| f32 | 200000 | 2000 | 78.347 | 2.14 | 4.24 | 8.32 | 12.25 | 36.13 | 145.93 |
| f32 | 200000 | 10000 | 398.740 | 4.86 | 9.59 | 18.65 | 27.24 | 76.58 | 254.22 |
| bf16 | 100000 | 2000 | 43.013 | 1.79 | 3.55 | 6.94 | 10.18 | 29.47 | 109.51 |
| bf16 | 100000 | 10000 | 218.358 | 3.16 | 6.24 | 12.18 | 17.85 | 51.20 | 183.28 |
| bf16 | 200000 | 2000 | 78.347 | 3.26 | 6.42 | 12.48 | 18.21 | 50.95 | 166.25 |
| bf16 | 200000 | 10000 | 398.740 | 5.74 | 11.29 | 21.86 | 31.78 | 87.13 | 265.32 |

The ratio is always local/hybrid; below one favors local prefill. The tested slower-link positive control produces a losing offload without hiding the numeric ratio. Default grid outcomes follow the declared optimistic line-rate/import assumptions.

One-shot f32 examples (bf16 and all links are in the CSV):

| Context | Mbit/s | Local s | Server s | Transfer s | Import s | Last token s | Hybrid TTFT s | Speedup × |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100000 | 100 | 1,277.330 | 5.456 | 291.304 | 0.091 | 0.132 | 296.983 | 4.30 |
| 100000 | 1000 | 1,277.330 | 5.456 | 29.130 | 0.091 | 0.132 | 34.810 | 36.69 |
| 200000 | 100 | 4,160.395 | 13.825 | 570.056 | 0.178 | 0.152 | 584.212 | 7.12 |
| 200000 | 1000 | 4,160.395 | 13.825 | 57.006 | 0.178 | 0.152 | 71.162 | 58.46 |
| 262000 | 100 | 6,914.186 | 20.477 | 742.882 | 0.232 | 0.165 | 763.756 | 9.05 |
| 262000 | 1000 | 6,914.186 | 20.477 | 74.288 | 0.232 | 0.165 | 95.162 | 72.66 |

## Decode sensitivity: hypothetical improvements, retained gain

Two clients (measured M3 Max 128 GB anchors and estimated M5 Max 64 GB portability), two links, both states and factors 1/1.5/2/3. The observed 32k gain is **1.665015442445748**; multiplying the requested single-stream rate does not multiply that gain. The existing measured-anchor interpolation and depth roofline are retained; no new parallel measurements are invented. Bf16 state-rate changes are estimates.

Capacity uses the supported real call mix, 8-hour day and 116-call normalization group. `fit_share`, group length, hours and actual stream range are explicit. As in R5, per-call local prefill is marginal at its sampled starting depth; remote policy adds R7 import/evaluation, measured slot KV and state variant. The sensitivity retains the existing estimated 1M model envelope beyond the actual benchmark’s 262k limit, unlike standalone timing spans. These session counts do not reconstruct original chronology.

The numeric rate columns show algebraic requested targets. Physical capacity requires the calibrated single-stream bandwidth efficiency × scale <=1 at unchanged Q4/q8_0 byte traffic. The default factor 3 violates this bound, so its local/hybrid capacity and gain alarm. No rate is silently clipped. Factors 1, 1.5 and 2 compute. Achieving a larger multiplier requires evidence for a changed traffic/model assumption or a different bandwidth envelope.

F32 real-mix session/day results (capacity cells at 3× are intentionally alarms):

| Client | Mbit/s | Requested scale | Local sessions/day | Hybrid sessions/day | Gain |
| --- | --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 300.0 | 1 | 2.737 | 3.845 | 1.405 |
| M3 Max 128 GB (measured) | 1000.0 | 1 | 2.737 | 3.881 | 1.418 |
| M3 Max 128 GB (measured) | 300.0 | 1.5 | 3.557 | 5.689 | 1.599 |
| M3 Max 128 GB (measured) | 1000.0 | 1.5 | 3.557 | 5.768 | 1.621 |
| M3 Max 128 GB (measured) | 300.0 | 2 | 4.184 | 7.482 | 1.788 |
| M3 Max 128 GB (measured) | 1000.0 | 2 | 4.184 | 7.620 | 1.821 |
| M3 Max 128 GB (measured) | 300.0 | 3 | ALARM | ALARM | ALARM |
| M3 Max 128 GB (measured) | 1000.0 | 3 | ALARM | ALARM | ALARM |
| M5 Max 64 GB | 300.0 | 1 | 4.995 | 5.510 | 1.103 |
| M5 Max 64 GB | 1000.0 | 1 | 4.995 | 5.569 | 1.115 |
| M5 Max 64 GB | 300.0 | 1.5 | 7.033 | 8.101 | 1.152 |
| M5 Max 64 GB | 1000.0 | 1.5 | 7.033 | 8.229 | 1.170 |
| M5 Max 64 GB | 300.0 | 2 | 8.836 | 10.589 | 1.198 |
| M5 Max 64 GB | 1000.0 | 2 | 8.836 | 10.811 | 1.224 |
| M5 Max 64 GB | 300.0 | 3 | ALARM | ALARM | ALARM |
| M5 Max 64 GB | 1000.0 | 3 | ALARM | ALARM | ALARM |

## Architecture script reproduction and every difference

Independent oracle: [tests/fixtures/arch_compare_r7.py](tests/fixtures/arch_compare_r7.py), the owner-attached text, executed as a copy in an isolated temporary directory. All **58 original numeric f32 fields match exactly** after the script’s own rounding. Numeric differences on the original f32 basis: **none**.

Intentional representation changes: the two original `None` values (`client_prefill_1k_262k_s` for Muse Glimmer and Qwen3-32B) become source-named context alarms, in both state variants. Original Russian kind labels are English metadata. Original nominal field names remain; actual coordinate/link columns identify override values. Qwen3-32B’s 131k hypothetical extrapolation is reproduced numerically and explicitly flagged `within_context_131k=0`; it is not a qualified in-context prediction.

The script’s Qwen config q8_0 formula yields **34,816 B/token**, distinct from the measured resident slot slope **34,844** used in the other R7 tables. Its approximate 131k reference is **41.2 tok/s** from the hash-checked segment 112,896–150,000 (actual midpoint 131,448), not a direct point measurement at 131,072. It uses 27.8B text parameters, while the existing timing engine FLOP envelope uses 27B. Savings retain the exact architecture-only definition: client prefill minus line-rate delta transfer, excluding B300/import/evaluation.

Architecture f32 values (complete original fields remain in CSV):

| Model | Full KV B/token | SWA B/token | Fixed MB | Delta 1k MB | Delta 10k MB | Prefill 1k s | Saving 100 s | Saving 300 s | Saving 1000 s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.8-27B | 34816 | 0 | 156.9 | 191.7 | 505.1 | 24.3 | 8.9 | 19.2 | 22.7 |
| Muse Glimmer 30B | 7072 | 21216 | 43.5 | 28.3 | 114.2 | 19.3 | 17.0 | 18.6 | 19.1 |
| Gemma 4 31B | 21760 | 435200 | 445.6 | 457.0 | 663.2 | 33.7 | -2.8 | 21.6 | 30.1 |
| Qwen3-32B | 139264 | 0 | 0.0 | 139.3 | 1392.6 | 77.1 | 66.0 | 73.4 | 76.0 |

Bf16 is an additional estimated row, not a claim that the supplied script used bf16. Only Qwen has recurrent state here; all seven changed numeric fields relative to its f32 script row are listed below. Other models’ numeric bf16 rows are unchanged because they have no recurrent state; sliding-window q8_0 KV, where present, is unchanged.

| Field (Qwen only) | Attached f32 | Engine bf16 |
| --- | --- | --- |
| fixed_mb | 156.9 | 78.4 |
| delta_1k_mb | 191.7 | 113.3 |
| delta_10k_mb | 505.1 | 426.6 |
| transfer_1k_300mbit_s | 5.1 | 3.0 |
| saving_1k_131k_100mbit_s | 8.9 | 15.2 |
| saving_1k_131k_300mbit_s | 19.2 | 21.3 |
| saving_1k_131k_1000mbit_s | 22.7 | 23.4 |

Config quantities retain their HF URLs, units and provenance. Access dates identify reading the owner’s supplied offline snapshot, not a new live HF access. Rounded text parameter counts remain estimates. [PAPER-R7-SOURCES-261030.md](PAPER-R7-SOURCES-261030.md) records URLs, measurement custody, import assumptions and limits.

## Alarms and validation

Default: **28 alarm cells, three roots**. Eight factor-3 sensitivity rows × three capacity/gain cells =24; two unsupported architecture contexts × two state rows =4. Timing tables have no default alarms. Rows remain visible; ordinary output exits 0, strict exits 1.

| Root input | Reason |
| --- | --- |
| r7.arch.models.glimmer.context | attached script uses None: comparison depth exceeds configured context |
| r7.arch.models.qwen3.context | attached script uses None: comparison depth exceeds configured context |
| r7.decode.scales.3 | requested decode scale exceeds raw bandwidth bound at unchanged Q4/q8_0 byte traffic; capacity not physically computable |

Final suite: **190 tests, exit 0, 205.740 s**. Includes all 170 retained tests, the nine byte-identical legacy goldens, Python 3.9 grammar validation and 20 new stated-claim tests. All 91 new quantities are deleted and every declared dependent cell checked for its exact source alarm. Contract checks reject null/NaN/infinity/negative/wrong-unit/missing-provenance values with valid controls. Native execution is Linux Python 3.14.4, not a macOS/Python 3.9 runtime qualification.

```bash
TMPDIR="$PWD/.temp/hybrid-calc-r7-261030/tmp" python3 -m unittest discover -s calc/tests
```

| Claim/corner | Named tests |
| --- | --- |
| Four chart grids and source/state variants | test_named_tables |
| Each serial timing component, full one-shot payload | test_turn_components; test_oneshot_components |
| Exact independent script numeric reproduction | test_attached_script_numbers |
| Sliding-window saturation/K=V/state variants | test_architecture_state_geometry |
| Same measured four-stream gain, hypothetical factors | test_decode_sensitivity; test_actual_four_stream_gain |
| Import-gap isolation and every new input | test_import_gap_control; test_every_new_input_gap; test_architecture_independent_geometry |
| Missing/zero links, losing valid offload | test_link_corner |
| Depth 0, exact context limit, overflow and nonfit | test_context_and_memory |
| Empty/single call, missing/hash-corrupt package | test_mix_and_measurements |
| Integration refinement, bandwidth/compute monotonicity | test_invariants_and_integration; test_bandwidth_and_compute_limits |
| Explicit zero overhead/evaluation, nonfinite, unknown override | test_overrides_and_zero; test_quantity_contracts |
| Malformed grids/config relations; independent metrics survive | test_container_gaps; test_architecture_gap_and_relation |
| Namespaced export preserves prior artifacts and exact numbers | test_export |

Other standalone commands and actual exits:

| Exact command | Exit | Log |
| --- | --- | --- |
| python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py | 0 | compile-01.log |
| python3 -m hybridcalc list | 0 | list-01.log |
| python3 -m hybridcalc run paper-tables-r7 --format json | 0 | run-01.log |
| python3 -m hybridcalc sources paper-tables-r7 --set workload.sample_calls=1 --format json | 0 | sources-01.log |
| python3 -m hybridcalc run paper-tables-r7 --set workload.sample_calls=1 r7.import_efficiency=null --format json | 0 | gap-01.log |
| python3 -m hybridcalc run paper-tables-r7 --set workload.sample_calls=1 r7.import_efficiency=null --format json --strict | 1 (expected alarm gate) | gap-strict-01.log |
| python3 -m hybridcalc run paper-tables-r7 --set r7.unknown=1 | 2 (expected command error) | unknown-01.log |
| python3 -m hybridcalc export paper-tables --output calc/out/paper | 0 | export-r5-01.log |
| python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper | 0 | export-r6-01.log |
| python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper | 0 | export-r7-01.log |
| python3 -m hybridcalc export paper-tables-r7 --strict --output .temp/hybrid-calc-r7-261030/independent | 1 (expected alarm gate) | export-strict-01.log |
| python3 calc/tests/r7_controls.py free_import | 1 (intended AssertionError) | control-import-01.log |
| python3 calc/tests/r7_controls.py drop_sliding | 1 (intended AssertionError) | control-sliding-01.log |
| python3 calc/tests/r7_controls.py scale_gain | 1 (intended AssertionError) | control-gain-01.log |
| tectonic --only-cached --outdir ../../.temp/hybrid-calc-r7-261030/pgfplots paper_r7_smoke.tex | 0 | pgfplots-01.log |

Commands run at repository root except Tectonic from `calc/tests`; cached-only native pgfplots parses all four CSV row counts and plots a turn series. The engine itself remains standard-library-only. Logs, actual command exits and environment/source fingerprints are under `.temp/hybrid-calc-r7-261030/` (`validation.json`, `validation-identity.json`, `unittest-01.log`).

`python3 .temp/hybrid-calc-r7-261030/audit.py`: exit 0. It verifies every new CSV numeric/alarm cell against structured output, independent strict-export byte identity, all generation/payload hashes, exact script comparison and identical R5/R6 result hashes/payloads. Strict gap output is byte-identical to ordinary gap output. All sixteen previous CSVs and their source/schema/alarm sidecars are byte-identical to `f01f32ad`; only the two old generator manifests identify the expanded engine.

Three bounded controls all fail their intended named assertion (exit 1), with no setup failures or survivors in this selected set:

| Mutant | Narrowed property | Named failing test | Finite bound |
| --- | --- | --- | --- |
| free_import | Import must be included in hybrid turn cost | test_turn_components | Killed; does not measure real import speed |
| drop_sliding | Delta must include min(portion,W) sliding KV | test_attached_script_numbers | Killed; numeric formula fidelity, not model execution |
| scale_gain | Single-stream improvement must retain measured four-stream anchor gain | test_actual_four_stream_gain | Killed; does not validate deep concurrent runtime scaling |

## Review scope and limits

- New `paper_tables_r7.py` composes the existing Context/dependency DAG, measured curve and performance helpers. Shared changes are loader dispatch and additive input/file contracts; no old physics or legacy wrapper is edited. Only four new table IDs/CSVs.
- Root README, calc README, source custody, report, unresolved-evidence register and required MANIFEST are updated. No files under `paper/`, `.github/`, `.scripts/`, `tools/` or `data/research/` changed.
- Timing curves, import/evaluation estimates, deep decode portability, bf16 equivalence, FLOP approximations and offline config transcriptions are finite assumptions. No live price/config validation, new hardware benchmark, state-transfer implementation or quality/security qualification is claimed.
- Self-review only; no independent acceptance, hosted CI or landing. The brief has no attack-surface-catalog table; table/negative/control coverage is explicit above. Signed local branch is ready for review; no push.
- `sha256sum -c MANIFEST.sha256`: exit 0, all 207 tracked-file entries pass, excluding the manifest itself, `./path` format in C-locale order. Staged whitespace and frozen-source/forbidden-path checks gate signing. Explicit `git commit -S` and `git verify-commit` provide local signed delivery; the summary records the signed object.

---

# Prior run 6 evidence
# Calculation engine — run 6, hybrid-calc-r6-261030

Continues reviewed signed `892da662` on `calc-engine`. Ready for review; signed local delivery, no push, network research, installation or paper-source edits. Run 5 and the nine legacy transcripts remain unchanged; its generation manifest is refreshed to identify the extended engine.

## Named paper tables

One scenario, `paper-tables-r6`, uses the hash-checked full04 call-mix marginals and benchmark package. It exports six CSVs, including the three profile chart subsets. Every cell declares its input paths; quantities retain units/provenance, gaps propagate root alarms and unaffected cells compute.

| Table ID | Rows | CSV | Root alarms |
| --- | --- | --- | --- |
| perimeter_cost | 765 | [CSV](out/paper/perimeter_cost.csv) | 0 |
| perimeter_cost_light | 255 | [CSV](out/paper/perimeter_cost_light.csv) | 0 |
| perimeter_cost_medium | 255 | [CSV](out/paper/perimeter_cost_medium.csv) | 0 |
| perimeter_cost_heavy | 255 | [CSV](out/paper/perimeter_cost_heavy.csv) | 0 |
| glm_utilization | 48 | [CSV](out/paper/glm_utilization.csv) | 0 |
| decode_scaling | 42 | [CSV](out/paper/decode_scaling.csv) | 1 |

```bash
python3 -m hybridcalc run paper-tables-r6 --format json
python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper
python3 -m hybridcalc sources paper-tables-r6 --format json
```

Audit files are `r6_schema.json`, `r6_sources.json`, `r6_alarms.json` and `r6_manifest.json`. They coexist with R5 sidecars. Export preserves foreign files, stages all bytes, installs the manifest last and records generator/payload hashes. CSV alarms are `nan`, `status=alarm`, `alarm_inputs`; full reasons remain in the alarm sidecar. Default ordinary export exits 0; strict export exits 1 with the same bytes.

## Closed perimeter: routing, waits and integer budgets

Here s=100% is the real organizational requirement, not an academic bound. Every requested call is client-served, turbo-served or explicitly unserved. Local-only unserved requests receive no invented API bill. All-server and hybrid routes stay entirely on owned hardware, with zero external calls. Executable dependency and deletion controls prove that API tariffs, rental rates and external egress prices cannot affect any perimeter cell.

Defaults match `owners-paper`: 8 h/day, 21 active days/month, target server load 70%, four-year ownership and 20% residual on servers and bought Mac premiums. Already-owned Macs have zero acquisition allocation but retain energy. Bought laptop rows subtract the explicit baseline-laptop credit; additional Studios have no such credit. The separate Studio-utilization experiment retains the R5 client residual 35%.

The small-host path uses one/two RTX PRO 6000 Server GPUs (96 GB each) per host in an owned rack. `r6.perimeter.policy=closed_perimeter_own_rack` explicitly overrides the ordinary small-office exclusion. It reuses R4 hardware/capex estimates ($36k/$62k), internal rack-space cost `owners.office_colo=0`, office electricity/support and declared PUE. Add an internal rack fee if it is incremental. B300 uses the existing eight-GPU internal-datacenter budget. Small hosts are eligible through 100 people, B300 from the declared 50-person overlap. All three candidate fleets remain visible; `selected=1` picks the cheapest eligible whole fleet per route/client/basis. `ceil(work / (8h × target_load))`, minimum one host/node, sizes each candidate.

Local prefill scales the measured M3 curve by client compute / M3 compute, then applies the memory roofline. Client decode capacity retains R5 measured 32k single/four-stream interpolation with explicitly estimated depth/device portability. Unsupported/capacity-excess calls use turbo. The empirical mix is uniformly thinned within eligible calls; no priority scheduler or original chronology is reconstructed.

For requested calls n and client-served calls a, owned-node daily work is `n × full_mix_all_server_seconds − a × eligible_mix_all_server_seconds + a × selected_shadow_prefill_seconds`. Selected remote prefill includes output shadow; all-server work prefills inputs and decodes outputs once. Turbo cost is separately benchmarked at full all-server USD/call. Prefill and turbo share the actual integer fleet; the signed `fleet_adjustment_month` reconciles reference allocations with fleet sharing/rounding. Thus the final bill pays a whole viable owned fleet, rather than a fractional overflow node.

`person_month = actual_fleet/person + Mac_premium_amortization + client_energy + front`. Local-only frontend has explicit zero incremental budget; hybrid uses the existing $5/person-month support/front estimate. Means include the declared internal RTT for server routes and exclude queues. `p90_scope` labels all-call all-server versus client-served-subset local/hybrid p90. Means on hybrid rows cover all requests, including turbo.

Illustrative per-person monthly chart rows for the measured M3 Max 128 GB (the CSVs contain all six clients and both bases):

| Profile | Team | Mac-only bought $ | Local served | Own all-server $ | Hybrid owned-Mac $ | Hybrid bought-premium $ | Turbo calls/day | Hybrid mean prefill s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| light | 5 | 60.87 | 100.0% | 144.81 | 152.33 | 210.68 | 0.0 | 2.096 |
| light | 10 | 60.87 | 100.0% | 72.41 | 79.93 | 138.28 | 0.0 | 2.096 |
| light | 50 | 60.87 | 100.0% | 50.59 | 22.00 | 80.35 | 0.0 | 2.096 |
| light | 500 | 60.87 | 100.0% | 67.40 | 41.22 | 99.57 | 0.0 | 1.812 |
| light | 5000 | 60.87 | 100.0% | 37.07 | 10.89 | 69.24 | 0.0 | 1.812 |
| medium | 5 | 60.87 | 39.7% | 252.96 | 152.33 | 210.68 | 350.9 | 1.514 |
| medium | 10 | 60.87 | 39.7% | 217.22 | 134.00 | 192.35 | 350.9 | 1.514 |
| medium | 50 | 60.87 | 39.7% | 202.37 | 108.70 | 167.05 | 350.9 | 1.514 |
| medium | 500 | 60.87 | 39.7% | 168.51 | 74.92 | 133.27 | 350.4 | 1.230 |
| medium | 5000 | 60.87 | 39.7% | 141.55 | 74.92 | 133.27 | 350.4 | 1.230 |
| heavy | 5 | 60.87 | 12.7% | 724.06 | 513.43 | 571.78 | 2,050.9 | 1.008 |
| heavy | 10 | 60.87 | 12.7% | 632.39 | 513.43 | 571.78 | 2,050.9 | 1.008 |
| heavy | 50 | 60.87 | 12.7% | 581.80 | 488.14 | 546.49 | 2,050.9 | 1.008 |
| heavy | 500 | 60.87 | 12.7% | 438.12 | 378.24 | 436.59 | 2,050.4 | 0.722 |
| heavy | 5000 | 60.87 | 12.7% | 434.75 | 371.50 | 429.85 | 2,050.4 | 0.722 |

Mac-only prices above are not whole-demand service prices: their served share is shown explicitly. No outside fallback is assumed. Integer minimums can make a small-team owned hybrid more expensive than expected; this is not suppressed.

Heavy-profile client geometry at 50 people (selected hybrid path; estimates except the original M3 anchors):

| Client | Stream cap | Local calls/day | Local mean s | Local p90 s | Hybrid client calls/day | Turbo calls/day | Hybrid all-call mean s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 4 | 317.5 | 27.95 | 54.79 | 449.1 | 2,050.9 | 1.008 |
| M4 Max 128 GB (estimate) | 4 | 480.3 | 13.98 | 27.39 | 609.9 | 1,890.1 | 0.762 |
| M5 Max 64 GB | 4 | 579.4 | 6.49 | 12.65 | 645.1 | 1,854.9 | 0.715 |
| M5 Max 128 GB | 4 | 607.4 | 6.52 | 12.78 | 684.6 | 1,815.4 | 0.730 |
| M5 Ultra 96 GB | 4 | 1,191.7 | 3.49 | 6.85 | 1,314.2 | 1,185.8 | 1.110 |
| M5 Ultra 256 GB | 4 | 1,242.8 | 2.80 | 5.48 | 1,337.8 | 1,162.2 | 1.067 |

## GLM Studio utilization

Growing GLM sessions retain R5 replay/clipping, Q4 sparse decode, purchased Ultra 256 and owned integer B300 prefill/all-server pools. `studios=ceil(team/users_per_studio)`; aggregate client capacity is Studio count × per-Studio capacity. Sharing never multiplies a physical device’s throughput. Fixed demand 1/2/4 is per person-day. The fourth mode fills the actual integer fleet, so its per-user demand is capacity × Studios/team (6.732123 with one Studio per user, 3.366062 with two users/Studio at 1M for even teams).

Every USD/session denominator is all requested sessions. Client excess is GLM-API-priced as in R5; this table is separate from closed perimeter. Hardware is per Studio, frontend per user; client-side throughput and energy are not duplicated by sharing. One-Studio-per-person, two-session/day rows match R5 on the same workload. At 1M the purchased Studio cost remains $148.756458/month and estimated capacity 6.732123 sessions/day.

| Final depth k | Team | Users/Studio | Sessions/user-day | Studio utilization | Hybrid $/session | API $/session | Own cluster $/session |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 200 | 50 | 1 | 1 | 5.3% | 23.39 | 0.63 | 16.05 |
| 200 | 50 | 1 | 2 | 10.6% | 11.70 | 0.63 | 8.02 |
| 200 | 50 | 1 | 4 | 21.2% | 5.86 | 0.63 | 4.01 |
| 200 | 50 | 1 | capacity | 100.0% | 1.25 | 0.63 | 0.85 |
| 200 | 50 | 2 | 1 | 10.6% | 19.84 | 0.63 | 16.05 |
| 200 | 50 | 2 | 2 | 21.2% | 9.93 | 0.63 | 8.02 |
| 200 | 50 | 2 | 4 | 42.3% | 4.97 | 0.63 | 4.01 |
| 200 | 50 | 2 | capacity | 100.0% | 2.11 | 0.63 | 1.70 |
| 200 | 500 | 1 | 1 | 5.3% | 8.94 | 0.63 | 1.60 |
| 200 | 500 | 1 | 2 | 10.6% | 4.48 | 0.63 | 0.80 |
| 200 | 500 | 1 | 4 | 21.2% | 2.25 | 0.63 | 0.80 |
| 200 | 500 | 1 | capacity | 100.0% | 0.49 | 0.63 | 0.59 |
| 200 | 500 | 2 | 1 | 10.6% | 5.40 | 0.63 | 1.60 |
| 200 | 500 | 2 | 2 | 21.2% | 2.71 | 0.63 | 0.80 |
| 200 | 500 | 2 | 4 | 42.3% | 1.36 | 0.63 | 0.80 |
| 200 | 500 | 2 | capacity | 100.0% | 0.58 | 0.63 | 0.68 |
| 200 | 5000 | 1 | 1 | 5.3% | 7.50 | 0.63 | 0.64 |
| 200 | 5000 | 1 | 2 | 10.6% | 3.76 | 0.63 | 0.64 |
| 200 | 5000 | 1 | 4 | 21.2% | 1.89 | 0.63 | 0.60 |
| 200 | 5000 | 1 | capacity | 100.0% | 0.44 | 0.63 | 0.57 |
| 200 | 5000 | 2 | 1 | 10.6% | 3.96 | 0.63 | 0.64 |
| 200 | 5000 | 2 | 2 | 21.2% | 1.99 | 0.63 | 0.64 |
| 200 | 5000 | 2 | 4 | 42.3% | 1.00 | 0.63 | 0.60 |
| 200 | 5000 | 2 | capacity | 100.0% | 0.47 | 0.63 | 0.58 |
| 1000 | 50 | 1 | 1 | 14.9% | 23.45 | 6.47 | 16.05 |
| 1000 | 50 | 1 | 2 | 29.7% | 11.76 | 6.47 | 8.02 |
| 1000 | 50 | 1 | 4 | 59.4% | 5.92 | 6.47 | 4.01 |
| 1000 | 50 | 1 | capacity | 100.0% | 3.55 | 6.47 | 4.77 |
| 1000 | 50 | 2 | 1 | 29.7% | 19.90 | 6.47 | 16.05 |
| 1000 | 50 | 2 | 2 | 59.4% | 9.99 | 6.47 | 8.02 |
| 1000 | 50 | 2 | 4 | 100.0% | 6.05 | 6.47 | 4.01 |
| 1000 | 50 | 2 | capacity | 100.0% | 5.97 | 6.47 | 4.77 |
| 1000 | 500 | 1 | 1 | 14.9% | 9.00 | 6.47 | 3.21 |
| 1000 | 500 | 1 | 2 | 29.7% | 4.54 | 6.47 | 3.21 |
| 1000 | 500 | 1 | 4 | 59.4% | 2.31 | 6.47 | 3.21 |
| 1000 | 500 | 1 | capacity | 100.0% | 1.40 | 6.47 | 3.10 |
| 1000 | 500 | 2 | 1 | 29.7% | 5.46 | 6.47 | 3.21 |
| 1000 | 500 | 2 | 2 | 59.4% | 2.77 | 6.47 | 3.21 |
| 1000 | 500 | 2 | 4 | 100.0% | 2.44 | 6.47 | 3.21 |
| 1000 | 500 | 2 | capacity | 100.0% | 1.68 | 6.47 | 3.34 |
| 1000 | 5000 | 1 | 1 | 14.9% | 7.72 | 6.47 | 3.21 |
| 1000 | 5000 | 1 | 2 | 29.7% | 3.98 | 6.47 | 3.13 |
| 1000 | 5000 | 1 | 4 | 59.4% | 2.15 | 6.47 | 3.09 |
| 1000 | 5000 | 1 | capacity | 100.0% | 1.38 | 6.47 | 3.08 |
| 1000 | 5000 | 2 | 1 | 29.7% | 4.18 | 6.47 | 3.21 |
| 1000 | 5000 | 2 | 2 | 59.4% | 2.21 | 6.47 | 3.13 |
| 1000 | 5000 | 2 | 4 | 100.0% | 2.23 | 6.47 | 3.09 |
| 1000 | 5000 | 2 | capacity | 100.0% | 1.44 | 6.47 | 3.10 |

## Decode scaling: bounds only, measured rows separate

Qwen3.8-27B Q4/q8_0, 64/128 decimal GB, 12 GB reserve, K=1/2/4/8/16, depth 64k/128k. M3 nominal bandwidth 400 GB/s, M5 614 GB/s. No measured efficiency is projected onto a new K or depth. The raw aggregate formula is `K × bandwidth / (weights + K × (depth × wire_KV + 2 × state))`. Fit separately checks `weights + reserve + K × (depth × resident_KV + state) <= memory`.

Weights are the 18,973,870,432-byte Q4 artifact. Wire KV is 34,816 B/token; measured resident slot slope is 34,844 B/token and fixed allocation 156,894,784 B/session. Two state passes describe traffic; fit reserves state once per session. `bandwidth_bound_aggregate` remains a labelled theoretical number when memory fails, while `aggregate_tok_s` alarms on nonfit. No practical speed claim follows from either raw number.

| Depth k | K | Fits 64 GB | Fits 128 GB | M3 raw aggregate tok/s | M5 raw aggregate tok/s |
| --- | --- | --- | --- | --- | --- |
| 64 | 1 | yes | yes | 18.59 | 28.54 |
| 64 | 2 | yes | yes | 33.25 | 51.04 |
| 64 | 4 | yes | yes | 54.90 | 84.28 |
| 64 | 8 | yes | yes | 81.40 | 124.96 |
| 64 | 16 | ALARM | yes | 107.30 | 164.70 |
| 128 | 1 | yes | yes | 16.85 | 25.86 |
| 128 | 2 | yes | yes | 28.06 | 43.07 |
| 128 | 4 | yes | yes | 42.04 | 64.54 |
| 128 | 8 | ALARM | yes | 56.01 | 85.97 |
| 128 | 16 | ALARM | yes | 67.16 | 103.09 |

Measured anchor rows (not fitted projections):

| Client | Depth | K | Measured aggregate tok/s |
| --- | --- | --- | --- |
| M3 Max | 32000 | 1 | 8.440946540 |
| M3 Max | 32000 | 4 | 14.054306338 |

The four-stream value uses maximum decode interval, not full request wall time. Default has exactly six nonfit usable-rate cells, one deduplicated root `r6.decode.memories.0`: K=16 at 64k, K=8/16 at 128k on both bandwidth families. No perimeter or Studio table alarms. The pending Mac 64k/128k stream run will replace this bounds-only view.

## Tests, controls and exact commands

Each new table has a stated-claim test. All 46 new data quantities are deleted in their active precision and checked against every declared dependent cell. Contract tests reject null/nonfinite/negative/wrong-unit/missing-provenance values with positive/zero controls. Existing reviewer tests and all nine byte-identical legacy golden tests are retained.

| Corner/control | Named test | Expected result |
| --- | --- | --- |
| Closed perimeter, no external price dependency | test_perimeter_conservation; test_no_external_price_dependency | All calls conserved; every perimeter table unchanged after external tariffs are deleted |
| Gap isolation | test_gap_control; test_every_new_input_gap | Exactly the planted root alarm; unrelated tables/cells unchanged |
| Integer fleet and turbo | test_perimeter_fleet_budget; test_turbo_pool_work; test_integer_fleet_threshold | Whole fleet billed, turbo work retained, threshold ceiling verified |
| Policy overlap | test_perimeter_selection_and_overlap | Own-rack exception explicit; all three paths eligible at 50, cheapest whole fleet selected |
| Window/latency | test_window_and_local_wait; test_weighted_prefill_wait | Capacity halves at 4h; own-server wait increases by added RTT; local rows unchanged |
| Shared Studio, odd team | test_studio_sharing; test_shared_capacity_modes | ceil count, one capacity budget/device, conserved overflow |
| Legacy GLM reference | test_glm_r5_reference | One Studio/person and two/day equal R5 capacities and costs |
| Residual 0/1 and team 1 | test_team_load_residual; test_perimeter_owner_residual | Finite valid budgets; declared residual basis |
| Empty/single call and depth 0 | test_empty_single_depth_zero | Empty per-call alarms, independent geometry retained; valid single call/depth-zero bound |
| Load/window/link zero or missing | test_team_load_residual; test_nonfit_and_link; test_window_and_local_wait | Exact source alarms, no division-by-zero or instant offload |
| Missing/hash-corrupt measurement | test_measurements_and_bounds_independence | Affected measurements alarm, independent factual anchors/bounds survive when their own sources remain valid |
| Nonfit | test_nonfit_and_link; test_decode_bound | No usable-rate/price built on impossible memory placement |
| NaN/infinity, unknown path | test_new_input_contracts; test_invalid_override | Nonfinite alarms; unknown override command error |
| Export coexistence | test_export_coexistence; test_export_namespace_rejection | R5 files preserved; deterministic CSVs; unsafe namespace rejected before writes |

Final frozen-source suite: **170 tests, exit 0, 199.390 s**. Linux Python 3.14.4. The golden syntax test parses all calc Python with Python 3.9 grammar; this is not native Python 3.9/macOS runtime validation. Earlier candidate logs are preserved as superseded; they are not final-head evidence.

```bash
python3 -m unittest discover -s calc/tests
```

Other standalone processes (real exits, including expected failures):

| Exact command | Exit | Evidence log |
| --- | --- | --- |
| python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py | 0 | compile-01.log |
| python3 -m hybridcalc list | 0 | list-01.log |
| python3 -m hybridcalc run paper-tables-r6 --format json | 0 | run-01.log |
| python3 -m hybridcalc sources paper-tables-r6 --set workload.sample_calls=1 --format json | 0 | sources-01.log |
| python3 -m hybridcalc run paper-tables-r6 --set workload.sample_calls=1 r6.perimeter.local_front_month=null --format json | 0 | gap-01.log |
| python3 -m hybridcalc run paper-tables-r6 --set workload.sample_calls=1 r6.perimeter.local_front_month=null --format json --strict | 1 (expected alarm gate) | gap-strict-01.log |
| python3 -m hybridcalc run paper-tables-r6 --set r6.unknown=1 | 2 (expected command error) | unknown-01.log |
| python3 -m hybridcalc export paper-tables --output calc/out/paper | 0 | export-r5-01.log |
| python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper | 0 | export-r6-01.log |
| python3 -m hybridcalc export paper-tables-r6 --strict --output .temp/hybrid-calc-r6-261030/independent | 1 (expected alarm gate) | export-strict-01.log |
| python3 calc/tests/r6_controls.py free_turbo | 1 (expected AssertionError) | control-turbo-01.log |
| python3 calc/tests/r6_controls.py double_shared_capacity | 1 (expected AssertionError) | control-sharing-01.log |
| python3 calc/tests/r6_controls.py project_efficiency | 1 (expected AssertionError) | control-efficiency-01.log |
| tectonic --only-cached --outdir ../../.temp/hybrid-calc-r6-261030/pgfplots paper_r6_smoke.tex | 0 | pgfplots-01.log |

Commands run at repository root except cached Tectonic, run from `calc/tests`. Logs and machine-readable command/exit records are in `.temp/hybrid-calc-r6-261030/validation.json`; source/test/data fingerprints are in `validation-identity.json`. Native cached-only pgfplots parses all six default CSVs at exact row counts and plots the Studio-load sweep; it adds no runtime dependency or network access.

`python3 .temp/hybrid-calc-r6-261030/audit.py` exited 0 (`audit-02.log`): all CSV numeric/alarm cells match structured output, independent strict export is byte-identical, both generator/payload hash sets are current, all ten R5 CSVs and its schema/sources/alarms are byte-identical to reviewed HEAD, and its result hash is unchanged. Only R5 generation metadata identifies the added engine/data.

Three bounded fault controls all produce their intended named AssertionError, exit 1; no setup-error failures or survivors in this selected set:

| Mutant | Narrowed claim | Named failing test | Survival bound |
| --- | --- | --- | --- |
| free_turbo | Turbo decode cannot be omitted from combined fleet work | test_turbo_pool_work | Killed; does not claim exhaustive scheduling coverage |
| double_shared_capacity | Two users cannot multiply one physical Studio capacity | test_shared_capacity_modes | Killed; does not establish runtime multiuser fairness |
| project_efficiency | New K/depth rows must be the exact raw bandwidth formula | test_decode_bound | Killed; does not validate hardware performance |

## Review scope and limits

- New module `paper_tables_r6.py` composes the R5 `Context`, performance/workload helpers and lazy metric DAG. Loader dispatch and safe export-sidecar namespacing are the bounded shared-code changes. The other physics/scenarios and legacy wrappers are preserved.
- Inputs: new R6 layer/scenario and contracts/file namespace. Root edits are README, unresolved-evidence register and the required MANIFEST; all other delivery edits are under calc. Forbidden paper/workflow/scripts/tools/research directories are unchanged.
- Source custody and formulas: [PAPER-R6-SOURCES-261030.md](PAPER-R6-SOURCES-261030.md). Same historical conservative output+reasoning workload basis; full04 marginals do not reconstruct chronology. GLM sessions replay sampled increments and are not new measurements.
- Estimates include hardware envelopes, prices, MFU, four-year residual, client depth/compute portability, sparse GLM decode, internally controlled compatible state transfer and sunk rack facilities. No secure-perimeter implementation, kernel/state compatibility, queueing latency, fairness, load-trace adequacy or procurement quote is qualified.
- Studio capacity beyond measured Qwen M3 anchors remains estimated. Raw Qwen decode bounds deliberately contain no projected efficiency. Owner’s 64k/128k concurrent-stream measurements remain pending.
- Self-review only; brief provides no attack-surface-catalog table. Table/negative/control coverage is explicit above, with finite limits. No independent acceptance, hosted CI or landing is claimed. Local signed delivery is ready for review; no push.
- `sha256sum -c MANIFEST.sha256`: exit 0, all 191 tracked-file entries pass (manifest excluded from itself), `./path` format in C-locale order. Staged whitespace and forbidden-path checks gate signing. Explicit `git commit -S` and `git verify-commit` provide local signed delivery; the delivery summary records the resulting object.

---

# Prior run 5 evidence
# Calculation engine — run 5, hybrid-calc-r5-261030

Continues reviewed signed `2c4ca6f` on `calc-engine`. Ready for review; local
signed delivery only, no push, network research, installation or paper-source
edit. This section supplies the paper's named outputs. Historical evidence
below retains its original models and does not silently become new evidence.

## Delivered paper tables and CSV paths

One scenario: `paper-tables`. It uses the measured prefill curve, measured
single/four-stream decode anchor and the full04 call-mix marginals. Each chart
has its own committed CSV under `calc/out/paper/`. Decision shares and the
academic bound have separate tables/files. All inputs retain units/provenance;
metadata sidecars retain generation hashes, units, exact display labels, used
sources and cell-level alarms.

| Table ID | Named table | Rows | CSV | Root alarms |
| --- | --- | --- | --- | --- |
| person_cost_s20 | Per-person cost / s20 (all requested calls, explicit overflow) | 60 | [CSV](out/paper/person_cost_s20.csv) | 0 |
| person_cost_s50 | Per-person cost / s50 (all requested calls, explicit overflow) | 60 | [CSV](out/paper/person_cost_s50.csv) | 0 |
| person_cost_academic_s100 | Per-person cost / academic_s100 (all requested calls, explicit overflow) | 60 | [CSV](out/paper/person_cost_academic_s100.csv) | 0 |
| crossover_explanation | Crossover explanation (unchanged r4 reference, 20%/50%/academic100%) | 9 | [CSV](out/paper/crossover_explanation.csv) | 0 |
| remote_rent_buy | Remote prefill rent or buy (whole warm windows, residual grid; office restricted) | 126 | [CSV](out/paper/remote_rent_buy.csv) | 1 |
| client_sessions_day | Client sessions per eight-hour day (measured prefill/parallel anchor, scaled estimates) | 24 | [CSV](out/paper/client_sessions_day.csv) | 0 |
| offload_by_link | Offload by link (calc9 D line-rate convention; state conversion estimated) | 8 | [CSV](out/paper/offload_by_link.csv) | 0 |
| traffic_user_month | Traffic per user-month (offered demand and Mac-capped hybrid) | 3 | [CSV](out/paper/traffic_user_month.csv) | 0 |
| glm_long_sessions | GLM growing sessions 200k to 1M (purchased Studio and owned cluster; overflow costed) | 25 | [CSV](out/paper/glm_long_sessions.csv) | 0 |
| client_fit_deep | Deep client fit (complete sessions, measured 27B affine slot geometry) | 32 | [CSV](out/paper/client_fit_deep.csv) | 8 |

Regenerate with:

```bash
python3 -m hybridcalc run paper-tables --format json
python3 -m hybridcalc export paper-tables --output calc/out/paper
python3 -m hybridcalc sources paper-tables --format json
```

The ordinary multi-table CSV formatter remains available, while `export`
creates chart-shaped separate files. Full-precision numeric cells are preserved.
For pgfplots, every record is flat/rectangular; commas, quotes and newlines in
display labels use safe punctuation, with exact originals in
`schema.json.csv_labels`. Ambiguous display-label collisions are rejected.
No unrelated destination file is deleted. Output files are staged first and
the checksum manifest is replaced last; readers verify hashes to reject stale
or interrupted generations.

`nan` denotes a noncomputable cell, with `status=alarm` and `alarm_inputs`.
It is never a blank/zero substitute. `alarms.json` gives table, zero-based row,
column and full root reasons. Standard Markdown/TeX/JSON still show detailed
alarms. The default intentionally alarms small-team office exclusions and
non-fitting client configurations. Other chart tables remain computable.

The default export has **329 alarm cells**. Deduplicated root alarms:

| Input | Reason |
| --- | --- |
| operations.small_team_max | office boxes are reserved for large companies; small remote teams use colocation |
| owners.memories.0 | model does not fit: weights + KV + recurrent state + OS/app reserve exceed memory |
| owners.memories.0 | model weights + state + reserve do not fit even at depth zero |
| owners.memories.1 | model does not fit: weights + KV + recurrent state + OS/app reserve exceed memory |
| owners.memories.1 | model weights + state + reserve do not fit even at depth zero |
| owners.memories.2 | model does not fit: weights + KV + recurrent state + OS/app reserve exceed memory |
| owners.memories.2 | model weights + state + reserve do not fit even at depth zero |
| owners.memories.3 | model does not fit: weights + KV + recurrent state + OS/app reserve exceed memory |
| owners.memories.3 | model weights + state + reserve do not fit even at depth zero |

Strict run/export therefore correctly exit 1 after producing results;
ordinary run/export exit 0. It is not appropriate to suppress those rows to
claim an alarm-free strict gate. Expected exclusions occupy the remote office
rows and deep-fit rows; the economics/client/offload/traffic/GLM charts have no
input-gap alarms on their default inputs.

## Overflow: both price bases cover the whole request

Audit finding: at the reviewed head, `owners-economics` **already** added
cheapest-API spill internally. The short summary hid the bill and omitted a
median-API counterpart. Run 5 exposes both and retains `hybrid_user` as the
original cheapest-total alias, rather than add an existing charge twice.

| Historical witness at s=50%, N=5 | Value |
| --- | --- |
| served_day | 901.564 |
| excess_day | 348.436 |
| overflow_cheapest_user | 11.817 |
| overflow_median_user | 76.875 |
| hybrid_cheapest_user | 35.269 |
| hybrid_median_user | 100.327 |

The new paper rows are intentionally different from that old single-Ultra,
L40S service model: clients are explicit, capacity uses measured parallel
scaling, prefill uses the measured curve with compute scaling, and the shared
rental prefill reference is B300. Both spill alternatives price **all** requested
open-model calls. Remaining closed-model calls are common excluded costs.

For each client, `requested=served+overflow`. Per-call API bills are formed
before routing, preserving 116-call cache boundaries. Memory-ineligible tail
calls retain their own, often higher, prices; eligible overload is a proportional
workload estimate. Each hybrid total equals its non-overflow budget plus the
respectively priced spill. GPU/egress apply only to served calls. Device
energy/front and purchase assumptions stay explicit.

Below is s=50%, N=5, eight client hours/day; purchased totals use the Mac premium
basis. The CSVs also contain all requested team sizes and the separate shares.

| Client | Anchor streams | Minimum active | Served/day | API spill/day | Median spill $/mo | Cheap spill $/mo | Owned Mac hybrid, median spill | Owned Mac hybrid, cheap spill | Bought premium hybrid, cheap spill | Full median API | Full cheap API |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M3 Max 128 GB (measured) | 4 | 2 | 449.635 | 800.365 | 176.583 | 27.144 | 195.834 | 46.395 | 93.805 | 275.785 | 42.393 |
| M4 Max 128 GB (estimate) | 4 | 2 | 609.875 | 640.125 | 141.229 | 21.709 | 163.290 | 43.770 | 91.166 | 275.785 | 42.393 |
| M5 Max 64 GB | 4 | 1 | 645.062 | 604.938 | 135.146 | 20.645 | 156.258 | 41.757 | 76.966 | 275.785 | 42.393 |
| M5 Max 128 GB | 4 | 2 | 684.586 | 565.414 | 124.746 | 19.176 | 146.745 | 41.175 | 98.050 | 275.785 | 42.393 |
| M5 Ultra 96 GB | 4 | 1 | 1,250.000 | 0.000 | 0.000 | 0.000 | 31.178 | 31.178 | 105.644 | 275.785 | 42.393 |
| M5 Ultra 256 GB | 4 | 4 | 1,250.000 | 0.000 | 0.000 | 0.000 | 30.221 | 30.221 | 176.458 | 275.785 | 42.393 |

The shared-service hybrid cost is independent of team size under its explicit
fractional-capacity purchase assumption. The all-server comparator buys integer
nodes, so its per-person cost changes with team size. Existing Macs can be
competitive while new device acquisition can erase savings, especially against
the cheapest API. The tables do not assert universal superiority.

## Measured scaling, client fit and offload

Dense single-stream efficiency is calibrated to 8.44094654 tok/s at 32k.
Four-stream interval gain is 1.665015442, not the ideal fourfold gain. With
`gamma=log(gain)/log(4)`, aggregate decode is the smaller of the measured
power interpolation and the calibrated memory-bandwidth roofline. This
matches one/four streams at 32k and is monotone in available stream capacity.
The old fixed-penalty depth extrapolation could reverse that monotonicity;
only the new paper law changes. No fifth stream is extrapolated. Per-call
memory includes output growth, and reported min/max counts expose reductions.

Other clients scale decode by bandwidth. Local prefill uses measured M3
segment interpolation, multiplies effective compute by the declared device /
M3 compute ratio, and applies the memory roofline. Beyond the last measured
midpoint, constant FLOP efficiency is an explicit estimate. M4 compute and
replacement valuation are new estimates. None is presented as a measured
non-M3 benchmark. The eight-client sessions table reports local/hybrid
supported-call equivalents per eight-hour day and their gain at three links.
`fit_share` must accompany comparisons: a 64 GB supported subset is not an
entire recovered chronology or an API-latency-inclusive wall-session result.

The offload chart exactly matches the independently frozen calc9 D **rounded**
percentages/savings on the default mix. It uses that table's line-rate goodput=1;
client economics separately uses declared WAN goodput=0.9. Both unconditional
saving per offered call and conditional saving per offloaded call are shown.
State 16 changes only serialized state size; conversion correctness is unproven.

| State bits | Mbit/s | Offload share | Saved s/all calls | Saved s/offloaded call |
| --- | --- | --- | --- | --- |
| 32 | 100.000 | 0.273 | 19.257 | 70.662 |
| 32 | 300.000 | 0.482 | 23.973 | 49.786 |
| 32 | 1,000.000 | 0.677 | 26.266 | 38.796 |
| 32 | 2,500.000 | 0.773 | 26.977 | 34.892 |
| 16 | 100.000 | 0.390 | 21.289 | 54.557 |
| 16 | 300.000 | 0.598 | 25.090 | 41.965 |
| 16 | 1,000.000 | 0.754 | 26.714 | 35.437 |
| 16 | 2,500.000 | 0.815 | 27.176 | 33.327 |

Deep fit retains all r4 model/placement cases at Q4/Q3 and every requested
Mac size/depth, including failures. 27B uses the measured 34,844 B/token plus
156,894,784 B affine state/intercept. Raw one-session reach and a separately
clipped context envelope are both supplied. A failed fit is an alarm, not a
valid zero-session machine. RAM labels retain the conservative decimal-GB
normalization; runtime at million-token depths remains unqualified.

## Remote rent/buy and traffic

The remote table has all three teams, three residuals and 10/24h active windows:
hourly H100/L40S/RTX PRO 6000, owned one/two-GPU colocation and visibly excluded
small-team offices. It sizes a dedicated prefill service for offered open calls
before the client cap. Nonfitting server contexts spill to median API in both
cost alternatives. Rental pays whole warm windows; ownership includes energy,
colo/support and residual-adjusted depreciation. `buy_beats_rent` is a numeric
monthly-cost comparison over four years, not initial-cash payback. R4's small
host minimum and office policy remain explicit. Quantized replicas reserve
weights/workspace separately; Q6 sensitivity and academic-BF16 nonfit are tested.

Traffic includes both offered-demand and actual Mac-capped downloads. Light,
medium and heavy are the declared 200/800/2500-call profiles. There is no free
hybrid traffic attributed to API spill. Prices at zero/five/fifty/ninety dollars
per decimal TB are explicit input columns.

| Profile | Calls/day | Served/day | Spill/day | Offered TB/mo | Hybrid TB/mo | $0/TB | $5/TB | $50/TB | $90/TB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| light | 200 | 200.000 | 0.000 | 0.582 | 0.582 | 0.000 | 2.911 | 29.114 | 52.405 |
| medium | 800 | 449.635 | 350.365 | 2.329 | 1.309 | 0.000 | 6.545 | 65.453 | 117.816 |
| heavy | 2500 | 449.635 | 2,050.365 | 7.279 | 1.309 | 0.000 | 6.545 | 65.453 | 117.816 |

## GLM growing sessions and one-million-token ingest

A session starts at depth zero and replays sampled measured delta/output/tool
increments until the chosen final context, clipping the last call. It does
not claim reconstructed GLM chronology. Demand is an explicit two full growing
sessions/person/active day. Each row buys the full Studio Ultra 256 and integer
owned B300 nodes; depreciation, energy/colo/support, front, egress and API spill
are included. Costs divide by requested sessions. The purchased minimum node
makes small teams expensive. High-demand tests actually exercise priced spill.

At one million final tokens:

| Team | API $/session | Own all-server $/session | Bought hybrid $/requested session | Studio resident sessions | Streams | Decode tok/s/stream | Local ingest s | Via one server replica s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 6.467 | 80.242 | 83.979 | 10 | 4 | 19.126 | 3,425.133 | 97.411 |
| 10 | 6.467 | 40.121 | 43.858 | 10 | 4 | 19.126 | 3,425.133 | 97.411 |
| 50 | 6.467 | 8.024 | 11.762 | 10 | 4 | 19.126 | 3,425.133 | 97.411 |
| 500 | 6.467 | 3.210 | 4.540 | 10 | 4 | 19.126 | 3,425.133 | 97.411 |
| 5000 | 6.467 | 3.129 | 3.978 | 10 | 4 | 19.126 | 3,425.133 | 97.411 |

The CSV contains all five depths from 200k to 1M. The cold-ingest comparison
integrates the depth-dependent prefill rate with declared midpoint resolution,
then transfers KV/state once. It uses one B300 replica's compute, not an
unqualified eight-GPU per-stream speedup. GLM local prefill uses a declared MoE
factor and decode uses the calc4 expert-union estimate; no Qwen batching gain is
mislabelled as a GLM measurement. Memory fit is distinct from speed or semantic
state-interchange qualification.

## Short crossover explanation

The named short table recomputes r4's independent historical bridge, with
sources/dependencies under `r4_reference.`. Client/traffic/current-sampler
overrides do not rewrite that reference. The complete one-assumption table and
its defect analysis remain in the historical r4 section below. Its integer
thresholds are bounded at 20,000, not a universal law or a newly measured SLA.

| Assumption | 20% crossover | 50% crossover | Academic 100% crossover | Paper treatment |
| --- | --- | --- | --- | --- |
| calc5 Rule A / one time zone | 3000 | 1000 | 500 | Historical baseline |
| Server weight traffic: FP8 27 GB to Q4 15.1875 GB | 1000 | 200 | 100 | Quantized server weights |
| Replace synthetic calls with measured calc8 calls | none through 20000 | none through 20000 | none through 20000 | Measured call mix |
| Daily work window: 8 hours to 10 hours | 800 | 400 | 200 | Use eight-hour client/operator baseline instead |
| Peak/headroom: 2 to 1/0.70 | 400 | 150 | 75 | Target-load planning |
| R3 sparse team grid (reviewed endpoint) | 200 | 200 | 100 | Historical sampled grid only |
| Integer sweep 1..20000 (grid sensitivity) | 306 | 123 | 62 | Every-integer crossover |
| Correct all-server output double counting for paper | 306 | 123 | 62 | Input-only prefill, output decoded once |
| Paper: measured KV 34844 B/token | 612 | 245 | 123 | Corrected r4 paper reference; new client tables use measured scaling |

## Tests, controls and exact validation

Every requested table has a named claim test. Every new quantity is exercised,
then deleted to check every dependent cell. Contracts cover provenance, units,
null/nonfinite/negative values, all zero/one boundaries and bounded fractions.
Whole containers, corrupt/missing measurements, unknown paths, one-person teams,
zero/unit load, nonfit replicas, invalid expert geometry and stream bounds are
covered. Unrelated API/capacity/fit results remain available under planted gaps.

| Claim | Named tests |
|---|---|
| Named chart coverage and all-call pricing | `test_named_tables`, `test_overflow_cost_conservation`, `test_mac_purchase_basis`, `test_existing_overflow_witness` |
| Actual per-call spill prices/cache boundaries | `test_selective_overflow_price`, `test_gap_control` |
| Measured parallel anchor and safe depth envelope | `test_measured_stream_anchor`, `test_parallel_depth_envelope`, `test_memory_capacity_monotonic` |
| Historical r4 reference | `test_crossover_reference` |
| Remote deployment, residual and load/window rules | `test_remote_rent_buy`, `test_load_one_and_windows`, `test_boundaries` |
| Clients and offload | `test_client_sessions_day`, `test_offload_links`, `test_offload_legacy_d`, `test_no_offload_corner` |
| Traffic units/prices/cap | `test_traffic_user_month` |
| GLM cost/fit/ingest/spill | `test_glm_long_sessions`, `test_glm_overflow_priced`, `test_growth_and_integration`, `test_prefill_and_ingest_refinement`, `test_glm_server_fit_and_experts` |
| Deep memory geometry | `test_client_fit_deep` |
| Every new input gap/contract and independent results | `test_every_new_input_gap`, `test_new_quantity_contracts`, `test_price_gap_independence`, `test_container_gaps`, `test_measurement_gaps` |
| Corners and missing/invalid inputs | `test_empty_and_single`, `test_invalid_overrides`, `test_nonfit_and_stream_bound`, `test_zero_api_and_single_stream` |
| Deterministic safe CSVs and original label custody | `test_csv_export`, `test_export_rejects_ids_before_write`, `test_csv_label_source` |
| Retained legacy/prior behavior and Python 3.9 grammar | All 108 prior tests retain their names and nine byte-identical output goldens |

The final full suite ran **144 tests, exit 0**, in 143.712 seconds. Code/data/test identity: `3cc55b2ec86d5f2ff506e79b3364d04d3b67e31b947551d96a08c80c1bb4127b`. Direct-process PIDs, stdout/stderr and actual exits are in `.temp/hybrid-calc-r5-261030/validation.json`.

| Exact command | Actual exit |
| --- | --- |
| `python3 -m unittest discover -s calc/tests` | 0 |
| `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | 0 |
| `python3 -m hybridcalc list` | 0 |
| `python3 -m hybridcalc run paper-tables --format json` | 0 |
| `python3 -m hybridcalc run paper-tables --format md` | 0 |
| `python3 -m hybridcalc run paper-tables --format tex` | 0 |
| `python3 -m hybridcalc sources paper-tables --format json` | 0 |
| `python3 -m hybridcalc run paper-tables --strict --format json` | 1 |
| `python3 -m hybridcalc export paper-tables --output calc/out/paper` | 0 |
| `python3 -m hybridcalc export paper-tables --output .temp/hybrid-calc-r5-261030/strict-export --strict` | 1 |
| `python3 -m hybridcalc run paper-tables --set prices.apis.qwen_median.output=null --strict --format json` | 1 |
| `python3 -m hybridcalc run paper-tables --set paper_tables.links.0=0 --format csv` | 0 |
| `python3 -m hybridcalc run paper-tables --set paper_tables.glm.sessions_day=100 --format json` | 0 |
| `python3 -m hybridcalc run paper-tables --set owners.server_precision=Q6 --format json` | 0 |
| `python3 -m hybridcalc run paper-tables --set workload.reasoning_extra_fraction=0 --format json` | 0 |
| `python3 -m hybridcalc run paper-tables --set paper_tables.typo=1` | 2 |
| `python3 -m hybridcalc export paper-base --output .temp/hybrid-calc-r5-261030/unsupported-export` | 2 |
| `python3 calc/tests/paper_controls.py overflow` | 1 |
| `python3 calc/tests/paper_controls.py parallel` | 1 |
| `python3 calc/tests/paper_controls.py selection` | 1 |

Expected-red strict commands print known alarms and exit 1. Invalid command/
unknown override/unsupported unnamed-table export exit 2 without a traceback.
Fault-control commands are intentionally failing (exit 1), not green checks:

| Mutant | Narrows the gate to | Named failing test | Bound |
|---|---|---|---|
| Make API spill free | Positive-priced capacity overflow must carry a bill | `PaperTablesTests.test_overflow_cost_conservation` | Dropped overflow only; not every possible cost error |
| Four ideal single streams | Measured aggregate gain must constrain parallel decode | `PaperTablesTests.test_measured_stream_anchor` | One/four-stream 32k anchor; not a non-M3/GLM runtime qualification |
| Price spill at whole-mix average | Unsupported calls retain their actual cache/output prices | `PaperInputTests.test_selective_overflow_price` | Routing/cache-price partition, not reconstructed real chronology |

All three controls fail their intended AssertionError with no import/setup
error; no survivor is claimed. Their reproducible runner is committed as
`calc/tests/paper_controls.py` and mutates only its own process. The initial
feature-red unknown-scenario run and the corrected null-versus-missing test
expectation are diagnostic failures, not fault-control evidence. The first
143-test full run passed but is superseded because its snapshot predates the
CSV-safety and final test changes; no earlier identity is promoted to this head.

The committed CSV generation was compared with an independent default strict
export. All 9,316 exported cells, 329 alarm cells, CSV/sidecar hashes and generator
hashes match the final structured result. Native pgfplots also read all ten
CSVs with exact expected row counts and plotted the documented GLM team filter.
The committed optional fixture is `calc/tests/paper_tables_smoke.tex`. Tectonic
0.17.0 used `--only-cached`; no resource download or paper PDF build occurred.

| Additional exact audit command | Working directory | Exit |
|---|---|---|
| `diff -r calc/out/paper .temp/hybrid-calc-r5-261030/strict-export` | repository root | 0 |
| `python3 .temp/hybrid-calc-r5-261030/verify_export.py` | repository root | 0 |
| `sha256sum -c MANIFEST.sha256` (174 tracked files, excluding itself) | repository root | 0 |
| `git diff --cached --check` | repository root | 0 |
| `tectonic --only-cached --keep-logs --outdir ../../.temp/hybrid-calc-r5-261030/pgfplots-final paper_tables_smoke.tex` | `calc/tests` | 0 |

The numeric/alarm/hash audit script is task-local; native import and its fixture
are reproducible from the committed tree. Audit logs are `export-diff-01.log`,
`export-verify-01.log`, `pgfplots-final-01.log` and the retained TeX log under
`.temp/hybrid-calc-r5-261030/`. Fixture SHA-256: `29060a7cab4e54e756a0f9aa2fd889a1f5153d7b5e55c186043e9d1329b7e014`.

## Limits and review handoff

- Full04 marginal sampling and the conservative output+reasoning sum remain
  explicit. Counter disjointness, original session chronology and arrivals/SLA
  are unresolved. Output-only sensitivity is executed and remains overridable.
- Non-M3 kernel efficiency, M4 compute/purchase valuation, GLM parallel traffic,
  precision quality/state interchange and 1M extrapolation are estimates.
  Fits do not prove runtime speed or correctness. No live quote was obtained.
- Remote and GLM tables reserve whole warm/owned units. They do not claim
  scale-to-zero billing or a fractional hardware purchase for a small team.
  Bought Studio/laptop costs are not hidden in an existing-Mac basis.
- CSV labels have documented display encoding; exact originals and units remain
  in sidecars. A strict alarm is an intentional CI gate, not suppressed success.
- Local Linux Python 3.14.4 ran the checks; Python 3.9 grammar/API suitability
  is covered, but native macOS/Python 3.9 execution was not installed or claimed.
  No online CI/review acceptance/landing or push is claimed.
- No explicit surface table was supplied. The test/claim and killed-mutant maps
  state finite coverage. Outside `calc/`, only required root README/manifest
  and the existing unresolved-assumptions register change. Forbidden paths and
  original measurement packages remain untouched. Ready for review.

# Prior run 4 evidence

# Calculation engine — run 4, hybrid-calc-r4-261030

Continues reviewed signed `46e0ee9b` on `calc-engine`. Local signed delivery,
no push, fetch, installs or network research. Forbidden directories and original
measurement packages are unchanged. Historical reports below retain their
original assumptions; this section supersedes their paper recommendations.

## Own-cluster crossover: findings first

Calc5 **already uses FP8**: 27 GB server weights and FP8 tensor throughput.
Its median API token prices equal r3's. Mac purchase accounting is absent from
both the all-server and API paths. Those candidates therefore do not explain
the discrepancy as a BF16 speedup, changed median tariffs or a free Mac.

At the requested academic 100% share and 500 people, both reviewed snapshots
actually cost **$370.718/person-month for the owned cluster** (11 B300 nodes).
The API comparison changes from **$371.574 to $551.569/person-month**, because
the workload/accounting distribution changes. Server demand also changes:
the measured mix increases decode/KV occupancy, while the 8→10h window and
peak factor 2→1/0.7 reduce the required fleet. Integer node thresholds amplify
small changes; contributions cannot be added as linear percentages.

The sparse r3 grid's 200/200/100 is literal **on-grid** evidence, not a guarantee
at every intervening size. Rechecking every integer through 20,000 produces
**306/123/62** at 20%/50%/academic100%. At 305 people and 20% share, the cluster
still loses; the old table omitted that counterexample. Sparse sampling can
understate or overstate the sustained crossover, depending on share.

An r3 accounting defect is also isolated: it charges output shadow-prefill
and output decode in the **all-server** path. Generated output already creates
server KV during decode. The correction removes that extra prefill only for
the owned all-server calculation. A hybrid still needs output shadow work to
maintain its separate server copy. This overcharge made r3's owned estimate
conservative; it was not the reason its crossover appeared earlier.

## calc5 to r3 step by step

Each row changes only the named assumption from the preceding row (audit/no-op
rows explicitly change none). The initial point reproduces actual calc5 Rule A,
one time zone. The reviewed r3 endpoint is marked before integer sensitivity and
paper corrections. Crossover columns are the first tested team from which all
later tested sizes through 20,000 pass. Except the explicitly integer rows,
the search uses the selected finite grid. “none” is a valid no-crossover result.
Server time is B300 **node-seconds per call**, with eight GPUs per node.

| One changed assumption | N at 20% | N at 50% | N at academic 100% | Own $/person-mo at 500, academic 100 | API $/person-mo, academic 100 | Node-s/call |
| --- | --- | --- | --- | --- | --- | --- |
| calc5 Rule A / one time zone | 3000 | 1000 | 500 | 370.718 | 371.574 | 0.114 |
| Precision audit: calc5 already FP8 (not BF16) | 3000 | 1000 | 500 | 370.718 | 371.574 | 0.114 |
| Existing-Mac incremental basis: irrelevant to own/API | 3000 | 1000 | 500 | 370.718 | 371.574 | 0.114 |
| Median API token prices: unchanged | 3000 | 1000 | 500 | 370.718 | 371.574 | 0.114 |
| Fleet eligibility: fixed B300 nodes | 3000 | 1000 | 500 | 370.718 | 371.574 | 0.114 |
| Server weight traffic: FP8 27 GB to Q4 15.1875 GB | 1000 | 200 | 100 | 337.016 | 371.574 | 0.111 |
| Align API sample: first 80 synthetic sessions like server | 1000 | 200 | 100 | 337.016 | 375.075 | 0.111 |
| Activity normalization: 2500 calls/day for both paths | 1000 | 200 | 100 | 337.016 | 372.246 | 0.111 |
| Replace synthetic calls with measured calc8 calls | none through 20000 | none through 20000 | none through 20000 | 606.629 | 551.569 | 0.200 |
| KV geometry: 32768 to r3 34816 B/token | none through 20000 | none through 20000 | none through 20000 | 640.331 | 551.569 | 0.211 |
| Recurrent state: bf16 78.45 MB to r3 156.89 MB | none through 20000 | none through 20000 | none through 20000 | 640.331 | 551.569 | 0.214 |
| Count recurrent state in resident occupancy | none through 20000 | none through 20000 | none through 20000 | 640.331 | 551.569 | 0.216 |
| HBM geometry: replica reserves to r3 pooled free HBM | none through 20000 | none through 20000 | none through 20000 | 606.629 | 551.569 | 0.201 |
| Add r3 redundant output shadow-prefill (defect) | none through 20000 | none through 20000 | none through 20000 | 640.331 | 551.569 | 0.208 |
| Daily work window: 8 hours to 10 hours | 800 | 400 | 200 | 505.524 | 551.569 | 0.208 |
| Peak/headroom: 2 to 1/0.70 | 400 | 150 | 75 | 370.718 | 551.569 | 0.208 |
| R3 sparse team grid (reviewed endpoint) | 200 | 200 | 100 | 370.718 | 551.569 | 0.208 |
| Integer sweep 1..20000 (grid sensitivity) | 306 | 123 | 62 | 370.718 | 551.569 | 0.208 |
| Correct all-server output double counting for paper | 306 | 123 | 62 | 337.016 | 551.569 | 0.201 |
| Paper: retain requested 8-hour operator day | 612 | 245 | 123 | 438.121 | 551.569 | 0.201 |
| Paper: dense replicas reserve weights/workspace per GPU | 612 | 245 | 123 | 438.121 | 551.569 | 0.207 |
| Paper: measured KV 34844 B/token | 612 | 245 | 123 | 438.121 | 551.569 | 0.207 |

The Q4 traffic change reduces the old synthetic unit-time estimate by only
about 3.45%, yet moves some finite-grid thresholds sharply because the old
asymptotic saving was small. Replacing the synthetic workload alone temporarily
eliminates crossover within 20,000 under the old peak/window assumptions. The
later window and peak changes restore it. Thus attributing the entire result
to quantization would be incorrect. The order-dependent bridge gives a
reproducible explanation, not a Shapley or variance attribution.

The normalized source populations are exposed: calc5 sizes from 80 synthetic
sessions but bills the API from 200, with 62.975 versus 62.7 calls/session.
Forty sessions/day means 2,519 versus 2,508 normalized calls/day. The bridge
first aligns populations, then compares 2,500 calls/day, then switches both
paths to the same full04 measured mix. It does not splice full05 dates/counts.

A second old defect is a **label/comment discrepancy**: calc4's actual rule is
office-only through 10 people, mixed office/DC through 50, DC-only thereafter;
the heading says office through 50. The bridge follows the code. This does not
explain the reported large-team parity points. Frozen scripts/output text
remain untouched for the byte-identical legacy contract.

## Assumptions to use in the paper

Use `owners-paper` as the corrected candidate; retain `owners-economics` as the
reviewed r3 reference, and publish the bridge alongside any crossover claim.
Its **612/245/123** integer thresholds are conditional on the listed inputs,
with the search bounded at 20,000, not a universal team-size law. The compact
team-cost table still shows selected example sizes; the crossover calculation
now checks every integer through its largest displayed size.

| Assumption | Recommendation and provenance |
|---|---|
| Workload | Same full04 measured mix for both alternatives. Keep calc8's conservative output+reasoning sum explicitly labelled for revision-to-revision comparability, and display output-only sensitivity until provider counter semantics are resolved. Registry package/checksums and sampler settings are preserved. |
| Activity | 2,500 calls/day ×21 days/month, open shares 20%/50%; 100% labelled academic. These are owner/calc8 profile estimates, not a guaranteed measured arrival process. |
| Precision | Q4 server weights, INT8/FP8 tensor class at 30% MFU, per owner decision. Q4 memory/throughput is an estimate until runtime-qualified. FP8 is the actual legacy baseline. BF16 remains academic only. |
| All-server accounting | Input-only prefill plus one output decode charge and residency. Remove r3's redundant output shadow. Hybrid prefill still shadows generated tokens. |
| Dense HBM placement | Separate weight/workspace reserves per GPU for 27B replicas. Do not credit an unqualified pooled eight-GPU model copy. GLM sharding remains an explicit estimate with memory alarms. |
| Window/load | Requested 8h operator window; 70% target peak-window load, inherited from the owner's service-sizing decision. It is a planning estimate, separate from MFU/energy duty. Preserve calc5 peak=2 as a conservative sensitivity; neither factor is a measured SLA. |
| KV/state | Measured affine 27B slot geometry: 34,844 B/token +156,894,784 B fixed state/intercept (156.9 MB rounded), original benchmark package SHA pinned. |
| Ownership | Remote teams of 5–100 use colocated Server Edition hosts with nonzero space/energy/support charges. Office boxes are an option only above 100. Purchase/colo budgets are estimates pending quotes. |
| Mac basis | Existing versus full new-Mac purchase matters to hybrid economics, not own-cluster/API parity. State the basis whenever publishing hybrid savings. |
| Grid | Every integer through maximum displayed team (20,000 by default). Label finite bounds; do not call a sampled-grid threshold a universal minimum. |
| Autopilot/pool | Separate fixed-volume sensitivities. Pool price, fill, job/owner-restore bounds and drain are estimates; pool does not exist. Continuous automatic reservations get zero guaranteed-idle credit. |

Output-only usage is a material accounting sensitivity, not an input silently
selected to obtain a desired answer. The command is
`python3 -m hybridcalc run owners-paper --set workload.reasoning_extra_fraction=0 --format json`.
Its computed integer thresholds and API prices are:

| Share | Case | Output-only integer crossover | API $/person-month | Own at 500 $/person-month |
| --- | --- | --- | --- | --- |
| 0.200 | decision case | 321 | 105.201 | 67.403 |
| 0.500 | decision case | 129 | 263.004 | 168.508 |
| 1 | academic bound | 65 | 526.007 | 337.016 |

The unresolved usage-count contract limits what can be asserted about billing
or quality; these are explicitly conditional economic comparisons. No runtime
or provider contract was invented to close that evidence gap.

## Small remote teams: owned colocation

The paper candidate adds 1×/2× RTX PRO 6000 **Server Edition** 96 GB hosts at
estimated $36k/$62k, including host allowances. Power is 0.9/1.8 kW.
Space is `max($100/host-month minimum, kW*$190/kW-month)`; energy and support
are separate. The minimum is a new explicit estimate, not an office-space zero
or a supplier quote. Rental uses the counterfactual $2.20/GPU-hour snapshot.
Buying two single-GPU tariffs does not guarantee a connected dual-GPU instance.
Office choices at 5/10/50/100 people alarm on `operations.small_team_max`;
only the 1,000-person office comparison is admitted in the operating table.

The earlier small-team and residual tables in `owners-paper` use colocated
ownership and omit office rentals. The one-GPU colo option remains available
above 100 too; the policy does not require every large company to choose an
office. Under the declared Q4 GLM estimate, 184.5 GB weights +8 GB workspace
exceed even the dual host's 192 GB. GLM placement/cost therefore alarms there;
Mac sessions and API references still compute. No precision is silently lowered.
Full source custody and input formulas are in
[`CROSSOVER-SOURCES-261030.md`](CROSSOVER-SOURCES-261030.md).

## Deep client fit

All 36/64/96/128 GB Macs, Q3/Q4 and both Flash-Next n-gram placements have one
raw memory-depth bound, a separate supported-envelope bound, and sessions at
256k/500k/1M. Reserve is 12 GB by default. “ALARM” means no complete session
fits, or weights/state do not fit even at depth zero. It is not a valid zero.
The full 32-row result is below; no model was omitted because it failed.

| Model | Quant | Placement | Mac GB | Weights GB | Raw one-session depth | Supported depth | Sessions 256k | Sessions 500k | Sessions 1M |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.8-27B | Q3 | all weights in RAM | 36.000 | 14.757 | 260752 | 260752 | 1 | ALARM | ALARM |
| Qwen3.8-27B | Q3 | all weights in RAM | 64.000 | 14.757 | 1064333 | 1000000 | 4 | 2 | 1 |
| Qwen3.8-27B | Q3 | all weights in RAM | 96.000 | 14.757 | 1982712 | 1000000 | 7 | 3 | 1 |
| Qwen3.8-27B | Q3 | all weights in RAM | 128.000 | 14.757 | 2901092 | 1000000 | 11 | 5 | 2 |
| Qwen3.8-27B | Q4 | all weights in RAM | 36.000 | 18.974 | 139743 | 139743 | ALARM | ALARM | ALARM |
| Qwen3.8-27B | Q4 | all weights in RAM | 64.000 | 18.974 | 943325 | 943325 | 3 | 1 | ALARM |
| Qwen3.8-27B | Q4 | all weights in RAM | 96.000 | 18.974 | 1861704 | 1000000 | 7 | 3 | 1 |
| Qwen3.8-27B | Q4 | all weights in RAM | 128.000 | 18.974 | 2780083 | 1000000 | 10 | 5 | 2 |
| Qwen3.8-Flash-Next | Q3 | all weights in RAM | 36.000 | 54.688 | ALARM | ALARM | ALARM | ALARM | ALARM |
| Qwen3.8-Flash-Next | Q3 | all weights in RAM | 64.000 | 54.688 | ALARM | ALARM | ALARM | ALARM | ALARM |
| Qwen3.8-Flash-Next | Q3 | all weights in RAM | 96.000 | 54.688 | 2308527 | 1048576 | 8 | 4 | 2 |
| Qwen3.8-Flash-Next | Q3 | all weights in RAM | 128.000 | 54.688 | 4833780 | 1048576 | 18 | 9 | 4 |
| Qwen3.8-Flash-Next | Q3 | n-gram on SSD | 36.000 | 32.375 | ALARM | ALARM | ALARM | ALARM | ALARM |
| Qwen3.8-Flash-Next | Q3 | n-gram on SSD | 64.000 | 32.375 | 1544047 | 1048576 | 5 | 3 | 1 |
| Qwen3.8-Flash-Next | Q3 | n-gram on SSD | 96.000 | 32.375 | 4069299 | 1048576 | 15 | 8 | 4 |
| Qwen3.8-Flash-Next | Q3 | n-gram on SSD | 128.000 | 32.375 | 6594552 | 1048576 | 25 | 13 | 6 |
| Qwen3.8-Flash-Next | Q4 | all weights in RAM | 36.000 | 70.312 | ALARM | ALARM | ALARM | ALARM | ALARM |
| Qwen3.8-Flash-Next | Q4 | all weights in RAM | 64.000 | 70.312 | ALARM | ALARM | ALARM | ALARM | ALARM |
| Qwen3.8-Flash-Next | Q4 | all weights in RAM | 96.000 | 70.312 | 1075494 | 1048576 | 4 | 2 | 1 |
| Qwen3.8-Flash-Next | Q4 | all weights in RAM | 128.000 | 70.312 | 3600746 | 1048576 | 13 | 7 | 3 |
| Qwen3.8-Flash-Next | Q4 | n-gram on SSD | 36.000 | 41.625 | ALARM | ALARM | ALARM | ALARM | ALARM |
| Qwen3.8-Flash-Next | Q4 | n-gram on SSD | 64.000 | 41.625 | 814091 | 814091 | 3 | 1 | ALARM |
| Qwen3.8-Flash-Next | Q4 | n-gram on SSD | 96.000 | 41.625 | 3339343 | 1048576 | 12 | 6 | 3 |
| Qwen3.8-Flash-Next | Q4 | n-gram on SSD | 128.000 | 41.625 | 5864596 | 1048576 | 22 | 11 | 5 |
| GLM-5.3-Flash | Q3 | all weights in RAM | 36.000 | 141.089 | ALARM | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q3 | all weights in RAM | 64.000 | 141.089 | ALARM | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q3 | all weights in RAM | 96.000 | 141.089 | ALARM | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q3 | all weights in RAM | 128.000 | 141.089 | ALARM | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q4 | all weights in RAM | 36.000 | 181.400 | ALARM | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q4 | all weights in RAM | 64.000 | 181.400 | ALARM | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q4 | all weights in RAM | 96.000 | 181.400 | ALARM | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q4 | all weights in RAM | 128.000 | 181.400 | ALARM | ALARM | ALARM | ALARM | ALARM |

Fit alarms identify the corresponding `owners.memories.<index>` input with
weights+KV+state+reserve failure; supported-envelope violations instead identify
`operations.context_limits.<model>`. Static geometry is a persisted measured/
architectural input, not a guarantee of decode speed at these depths. All GLM
laptop configurations still fail. Runtime state format and extrapolation beyond
the measured trace are not qualified by this table.

## Autopilot utilisation and warm billing

The automatic share is a fraction of the **same total monthly open calls**:
operator-only a=0 versus selected a=0.5 by default. Automatic work is uniform
across the 730h average month; remaining work stays within 8h×21 operator
windows. More automatic work can reduce the peak fleet, but any continuous
reservation requires a whole-calendar warm rental. No scale-to-zero discount
is assumed. These are prefill-service workloads; do not add their costs again
to the hybrid table or infer unmodelled overnight Mac capacity.

The table includes all admitted remote/large-office cases. The sixteen
small-company office rows remain policy alarms in CLI output rather than
being priced as valid alternatives.

| Team | Option | Profile / auto share | Units | Owner GPU-h/mo | Calendar use | Peak-window load | Warm h/unit-mo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 1x RTX PRO 6000 Server, colocation | operator / 0 | 1 | 9.489 | 0.013 | 0.056 | 168 |
| 5 | 1x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 9.489 | 0.013 | 0.035 | 730 |
| 10 | 1x RTX PRO 6000 Server, colocation | operator / 0 | 1 | 18.979 | 0.026 | 0.113 | 168 |
| 10 | 1x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 18.979 | 0.026 | 0.069 | 730 |
| 50 | 1x RTX PRO 6000 Server, colocation | operator / 0 | 1 | 94.893 | 0.130 | 0.565 | 168 |
| 50 | 1x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 94.893 | 0.130 | 0.347 | 730 |
| 100 | 1x RTX PRO 6000 Server, colocation | operator / 0 | 2 | 189.787 | 0.130 | 0.565 | 168 |
| 100 | 1x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 189.787 | 0.260 | 0.695 | 730 |
| 1000 | 1x RTX PRO 6000 Server, colocation | operator / 0 | 17 | 1,897.865 | 0.153 | 0.665 | 168 |
| 1000 | 1x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 10 | 1,897.865 | 0.260 | 0.695 | 730 |
| 5 | 2x RTX PRO 6000 Server, colocation | operator / 0 | 1 | 10.544 | 0.007 | 0.031 | 168 |
| 5 | 2x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 10.544 | 0.007 | 0.019 | 730 |
| 10 | 2x RTX PRO 6000 Server, colocation | operator / 0 | 1 | 21.087 | 0.014 | 0.063 | 168 |
| 10 | 2x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 21.087 | 0.014 | 0.039 | 730 |
| 50 | 2x RTX PRO 6000 Server, colocation | operator / 0 | 1 | 105.437 | 0.072 | 0.314 | 168 |
| 50 | 2x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 105.437 | 0.072 | 0.193 | 730 |
| 100 | 2x RTX PRO 6000 Server, colocation | operator / 0 | 1 | 210.874 | 0.144 | 0.628 | 168 |
| 100 | 2x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 1 | 210.874 | 0.144 | 0.386 | 730 |
| 1000 | 2x RTX PRO 6000 Server, colocation | operator / 0 | 9 | 2,108.739 | 0.160 | 0.697 | 168 |
| 1000 | 2x RTX PRO 6000 Server, colocation | autopilot / 0.5 | 6 | 2,108.739 | 0.241 | 0.643 | 730 |
| 1000 | Office RTX PRO 6000 | operator / 0 | 17 | 1,897.865 | 0.153 | 0.665 | 168 |
| 1000 | Office RTX PRO 6000 | autopilot / 0.5 | 10 | 1,897.865 | 0.260 | 0.695 | 730 |
| 1000 | Office 4x RTX PRO 6000 | operator / 0 | 5 | 2,108.739 | 0.144 | 0.628 | 168 |
| 1000 | Office 4x RTX PRO 6000 | autopilot / 0.5 | 3 | 2,108.739 | 0.241 | 0.643 | 730 |

For 100 people on the one-GPU colo design, the 50% automatic profile reduces
required hosts from two to one and doubles calendar utilisation for the same
owner work. At ten people both profiles remain at one host, so calendar use
is unchanged even though the peak falls. Buying becomes more attractive
against a full-calendar warm lease; this is not a claim that utilisation rises
for every small team or that demand magically increases.

## Hypothetical idle-capacity pool and drain

**Estimate: the pool does not exist.** Price is $0.50/GPU-hour received net of
any platform fee; tenant network/storage are assumed billed separately. Fill
is 50% of **guaranteed idle-window admission hours**, not of unused GPU
utilisation. The owner-only profile has 562 idle hours/unit-month: nights
between active days plus the trailing inactive part of the average month.
Stopping admissions 0.25h before each owner return leaves 556.75 eligible
hours/unit-month. Tenant job duration is bounded by 0.20h (12 minutes),
followed by owner model/state restoration bounded by 0.05h (3 minutes).
Both bounds are estimates requiring qualification. If their sum exceeds the
guard, pool metrics alarm; known idle hours and normal ownership/rent survive.

Jobs and drain cannot consume owner windows. Admission/sale hours exclude the
guard; any positive fill reserves the entire guard as a conservative incremental
energy bound, because fill does not bound the final job's runtime. Sold plus
draining hours never exceed owner-idle capacity. Zero fill gives zero credit.
Continuous automatic owner reservations leave **zero guaranteed idle windows**,
so those profiles receive zero pool revenue even with fill 1. No user fallback
or owner queueing discount is assumed. Zero reported conflict-hours is a property
of this bounded analytical schedule, not a real availability measurement.

The operating study charges idle baseline over the calendar plus incremental
owner work. Summary/residual/small-team tables retain calc4's fixed 70%
energy-duty budget; the bridge holds unit opex fixed to attribute fleet
changes. These are separate sensitivities; do not add or average their costs.
Pool credit is revenue less incremental tenant work/drain energy. Effective
cost is net monthly depreciation+opex divided by **owner-used GPU-hours**.
Buy/rent months are net capex divided by positive rent−opex, with or without
pool credit. A nonpositive saving alarms as no recovery. Residuals and prices
remain overridable; no cost or credit is silently clamped to zero.

| Team | Option | Profile | Sold GPU-h | Net pool credit $/mo | $/owner-used GPU-h no pool | $/owner-used GPU-h with pool | Buy months no pool | Buy months with pool |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 1x RTX PRO 6000 Server, colocation | operator | 278.375 | 112.955 | 95.243 | 83.340 | 437.639 | 161.107 |
| 5 | 1x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 95.243 | 95.243 | 22.116 | 22.116 |
| 10 | 1x RTX PRO 6000 Server, colocation | operator | 278.375 | 112.955 | 47.668 | 41.716 | 443.555 | 161.902 |
| 10 | 1x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 47.668 | 47.668 | 22.131 | 22.131 |
| 50 | 1x RTX PRO 6000 Server, colocation | operator | 278.375 | 112.955 | 9.608 | 8.417 | 497.334 | 168.555 |
| 50 | 1x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 9.608 | 9.608 | 22.251 | 22.251 |
| 100 | 1x RTX PRO 6000 Server, colocation | operator | 556.750 | 225.911 | 9.608 | 8.417 | 497.334 | 168.555 |
| 100 | 1x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 4.850 | 4.850 | 22.403 | 22.403 |
| 1000 | 1x RTX PRO 6000 Server, colocation | operator | 4,732.375 | 1,920.243 | 8.180 | 7.168 | 511.001 | 170.097 |
| 1000 | 1x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 4.850 | 4.850 | 22.403 | 22.403 |
| 5 | 2x RTX PRO 6000 Server, colocation | operator | 556.750 | 225.911 | 152.395 | 130.969 | 299.284 | 126.647 |
| 5 | 2x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 152.395 | 152.395 | 18.798 | 18.798 |
| 10 | 2x RTX PRO 6000 Server, colocation | operator | 556.750 | 225.911 | 76.244 | 65.531 | 301.056 | 126.963 |
| 10 | 2x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 76.244 | 76.244 | 18.805 | 18.805 |
| 50 | 2x RTX PRO 6000 Server, colocation | operator | 556.750 | 225.911 | 15.323 | 13.180 | 316.020 | 129.550 |
| 50 | 2x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 15.323 | 15.323 | 18.861 | 18.861 |
| 100 | 2x RTX PRO 6000 Server, colocation | operator | 556.750 | 225.911 | 7.708 | 6.636 | 336.955 | 132.936 |
| 100 | 2x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 7.708 | 7.708 | 18.931 | 18.931 |
| 1000 | 2x RTX PRO 6000 Server, colocation | operator | 5,010.750 | 2,033.198 | 6.946 | 5.982 | 341.990 | 133.713 |
| 1000 | 2x RTX PRO 6000 Server, colocation | autopilot | 0.000 | 0.000 | 4.662 | 4.662 | 19.026 | 19.026 |
| 1000 | Office RTX PRO 6000 | operator | 4,732.375 | 1,646.922 | 5.248 | 4.380 | 84.588 | 63.057 |
| 1000 | Office RTX PRO 6000 | autopilot | 0.000 | 0.000 | 3.148 | 3.148 | 15.910 | 15.910 |
| 1000 | Office 4x RTX PRO 6000 | operator | 5,567.500 | 2,031.576 | 4.772 | 3.809 | 69.684 | 51.863 |
| 1000 | Office 4x RTX PRO 6000 | autopilot | 0.000 | 0.000 | 2.916 | 2.916 | 13.529 | 13.529 |

For ten people with one colocated GPU, the illustrative operator-only pool
reduces effective cost from $47.668 to $41.716 per owner-used GPU-hour and
buy/rent recovery from 443.555 to 161.902 months. This still does not recover
the purchase within four years. The same-work automatic profile has no pool
credit but a full-calendar rental comparator and about 22.131-month recovery.
These results expose the cost of a small dedicated warm pool; they do not
assert that buying small hardware beats cheap APIs.

The recovery values are **equivalent residual-adjusted months**, not literal
cash-payback dates: terminal four-year resale is credited in net capex for this
comparison. A result beyond 48 months means no advantage within the planned
four-year horizon under these assumptions, not a forecast that one GPU lasts
37 years. Residual 1 gives zero net capex, not zero initial cash outlay.

## Design, tests and bounds

`crossover.py` composes sufficient workload moments, per-unit physics, cost,
API and crossover nodes. API price and B300 time stay computable when fleet
capex is absent; a missing diagnostic team cannot mask crossover results.
Unknown changed assumptions alarm the uncertain current/later states and
preserve earlier rows. Ordered step/reference metadata is data, not executed
Python. No legacy module was edited or embedded into canonical printing. Final review
found and corrected the inherited datacenter-rental branch in small-team rows:
colocated keys now explicitly select owned cost. Its named regression compares
the exact owned budget with an otherwise matching rental counterfactual.
Deployment policy and energy price follow the location input, not catalogue ID
prefixes. A data-only office host under a new ID first exposed that omission
(expected-red `deployment-red-01.log`, exit 1); its regression now passes
(`deployment-green-01.log`, exit 0). No failing setup was counted as a control.

`operations.py` composes deep fit, scheduling, eligibility, pool admission,
power accounting, costs and recovery. Every output cell has direct/transitive
requirements. Missing pool price adds exactly its root alarm, while all other
tables and normal owner costs remain unchanged. Missing/null/empty containers
retain partial output. No zero multiplier hides a missing required input.

| New contract / corner | Named tests |
|---|---|
| Exact calc5 and reviewed r3 endpoints; Mac/tariff no-ops | `test_calc5_endpoint`, `test_r3_endpoint`, `test_irrelevant_assumptions` |
| Shadow overcharge correction and independent paper endpoint | `test_shadow_defect_correction`, `test_corrected_all_server_has_one_decode`, `test_paper_endpoint_and_integer_grid` |
| Omitted sparse-grid counterexample at N=305 | `test_omitted_team_counterexample` |
| Colocated fees, deployment-driven office threshold, owned budgets and independent rental/fit | `test_small_team_colocation_policy`, `test_colocation_minimum_price`, `test_small_colocation_is_ownership`, `test_office_policy_uses_deployment_metadata` |
| Measured affine deep-fit accounting, all 256k/500k/1M depths | `test_deep_fit_affine_bound` |
| Fixed-work conservation, integer fleet/load and calendar lease | `test_autopilot_work_and_load` |
| Pool temporal conservation, cost/recovery and zero overlap | `test_pool_conservation_and_economics` |
| Share/fill 0 and 1, zero price, guard failure preserves non-pool metrics | `test_pool_and_autopilot_boundaries` |
| Guard covers tenant job plus owner restoration; decimal boundary is stable | `test_owner_restore_is_in_guard`, `test_guard_decimal_boundary` |
| Drain energy bound cannot be scaled down by fractional fill | `test_drain_bound_not_scaled_by_fill` |
| Every new quantity missing in an activated branch; invalid/null/nonfinite/unit/provenance controls | `test_every_new_input_missing`, `test_new_input_contracts` |
| Independent API/compute and crossover under capex/probe gaps | `test_bridge_price_and_probe_gaps` |
| Exactly one pool-price root alarm; unrelated data identical | `test_pool_gap_control` |
| Missing/null/empty new containers, one person, residual 0/1, zero fees, invalid load/share/calendar/depth | `test_container_gaps`, `test_boundary_matrix` |
| Unknown bridge assumption retains earlier rows, alarms uncertain later values | `test_unknown_assumption_partial_alarm` |
| Free rental remains valid and its non-recovery alarm names the rental input | `test_zero_rental_names_comparison_input` |
| All prior tests, nine byte-identical legacy outputs and Python 3.9 grammar | Full suite retains every prior test name |

The full suite ran **108 tests, exit 0**, in 138.324 seconds. Source/test/data identity: `c7e570ae1f4308bfa94091dfab2dd58741d15010e276d58d79820efa9c447852`. Direct standalone-process PIDs, stdout/stderr and real exit codes are recorded in `.temp/hybrid-calc-r4-261030/validation.json`.

| Exact command | Actual exit |
| --- | --- |
| `python3 -m unittest discover -s calc/tests` | 0 |
| `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | 0 |
| `python3 -m hybridcalc list` | 0 |
| `python3 -m hybridcalc run crossover-bridge --strict --format json` | 0 |
| `python3 -m hybridcalc run crossover-bridge --format md` | 0 |
| `python3 -m hybridcalc sources crossover-bridge --strict --format json` | 0 |
| `python3 -m hybridcalc run crossover-bridge --set bridge.units.b300.capex=null --format csv` | 0 |
| `python3 -m hybridcalc run crossover-bridge --set bridge.weight_fp8=null --strict --format json` | 1 |
| `python3 -m hybridcalc run owners-paper --format json` | 0 |
| `python3 -m hybridcalc run owners-paper --strict --format md` | 1 |
| `python3 -m hybridcalc run owners-paper --set operations.autopilot_share=1 operations.pool_fill=1 --format csv` | 0 |
| `python3 -m hybridcalc run owners-paper --set operations.drain_hours=0 --format tex` | 0 |
| `python3 -m hybridcalc run owners-paper --set operations.pool_price=null --strict --format json` | 1 |
| `python3 -m hybridcalc run owners-paper --set workload.reasoning_extra_fraction=0 --format json` | 0 |
| `python3 -m hybridcalc sources owners-paper --format json` | 0 |
| `python3 -m hybridcalc run owners-paper --set operations.typo=1` | 2 |
| `python3 -m hybridcalc run owners-economics --format json` | 0 |
| `python3 -m hybridcalc run paper-base --strict --format json` | 0 |
| `python3 -m hybridcalc run glm-tier2 --strict --format json` | 0 |
| `python3 -m hybridcalc run service-quantized --strict --format json` | 0 |
| `python3 .temp/hybrid-calc-r4-261030/grid-control.py` | 1 |
| `python3 .temp/hybrid-calc-r4-261030/pool-control.py` | 1 |
| `python3 .temp/hybrid-calc-r4-261030/ownership-control.py` | 1 |

Expected-red strict commands print deliberate fit/policy/gap alarms before
exit 1. Unknown override exits 2 without a traceback. All three narrowing mutants
fail their named assertions (exit 1), with no import/setup error:

| Mutant | Narrows the gate to | Named failing test | Limit |
|---|---|---|---|
| Replace integer sweep with r3's sparse grid | Intermediate team failures cannot disappear | `RecommendedPaperTests.test_omitted_team_counterexample` | Detects 306→200 substitution, not every possible equilibrium defect |
| Sell operator idle windows despite continuous autopilot reservations | Pool cannot lease owner-reserved windows | `OperationsTests.test_pool_conservation_and_economics` | Temporal analytical model only; no real pool or job enforcement qualification |
| Classify colocated small hosts as rentals | Colocated owned rows must include depreciation/opex, not inherit the datacenter-rental rule | `ColocationOwnershipTests.test_small_colocation_is_ownership` | Small-team ownership calculation only, not supplier price qualification |

No surviving mutant is claimed. The old golden-input and gap controls also
remain in the full suite. No production files or external owner data were
changed by the mutations; each lives only in its isolated test process.

## Limits and handoff scope

- Paper figures are conditional estimates, not a universal “500-person” law.
  The report decomposes the difference and names the actual accounting and
  labelling defects. Integer results remain bounded at 20,000.
- Output/reasoning counter disjointness, synthetic session grouping, price/
  quality equivalence, MFU, queueing/SLA, quantized state interchange, multi-GPU
  topology and forecast arrivals remain unqualified. Output-only sensitivity
  is displayed; no evidence gate was pretended resolved.
- Deep fit is memory geometry with a declared context envelope, not proof of
  runtime performance at 1M. The persisted measured affine inputs have their
  package/hash provenance; performance curves still use hash-checked files.
- Small-host capex/minimum fees, idle power, pool price/fill and job/drain/owner-restore
  bounds are estimates. No real pool exists. Any positive continuous automatic
  reservation receives zero guaranteed-idle credit; a different interruptible
  schedule requires explicit new data/model assumptions.
- The pool owner price is assumed net of fees, with tenant storage/egress paid
  separately. No financing, time value of money, resale guarantee or unmeasured
  operational overhead is represented as an observed cost.
- Validation ran on local Linux Python 3.14.4; Python 3.9 grammar/API suitability
  is checked, but no native macOS/Python 3.9 runtime was installed or tested.
  No PDF build, online CI, push or landing was run or claimed.
- No explicit surface table was supplied in the brief; the test/claim map above
  states finite coverage. Local self-review supports review handoff, not owner
  acceptance. Outside `calc/`, only required root README/manifest and the
  existing unresolved-assumptions register change. Forbidden paths are untouched.

# Prior run 3 evidence

# Calculation engine — run 3, hybrid-calc-r3-261030

Continues signed `1ecd141d` on `calc-engine`. Local signed handoff only. No
push, fetch, installations, network research, or changes under `paper/`,
`.github/`, `.scripts/`, `tools/` or `data/research/`. The explicitly requested
a2a summary is the sole outward messaging action. Earlier run reports below
are historical evidence; this section describes the current code and numbers.

## Decisions and module map

`ownership.py` composes the existing declared-input DAG, measured sampling,
prefill curve, transfer policy and throughput bound. Data is in
`ownership.json` and `scenarios/owners-economics.json`; no dependencies were
added. `service.py` now selects Q4/Q6/Q8/FP8/NVFP4 tensor envelopes and memory.
`engine.py` dispatches the new scenario. Contracts, CLI formatters and the
no-fallback alarm mechanism remain shared. All legacy modules/wrappers and
outputs are unchanged; the old-script module map remains in the run-1 section.

| Old calculation / new requirement | Module / data |
|---|---|
| calc3/4/5 hardware, fleet and team economics | Existing `economics.py`, `paper.py`; new residual, buy/rent and summary graph in `ownership.py` |
| calc7/8 measured calls, API billing and per-call prefill | Existing `analysis_graph.py`, `workload.py`, `service.py`; reused by `ownership.py` |
| calc9 measured prefill and native decode | Existing `curve_data` and pinned benchmark; `ownership.py` native 16k anchor and client capacity |
| Owners' model-fit grids and quantization | `ownership.json`, `contract.json`, `ownership.py`; quantized service formats in `service.json` |

Open shares are 20% and 50%; 100% is explicitly labelled **academic bound** in
every share-sensitive table. Production server precision is Q4 by default.
Q4/Q6/Q8/FP8 weights use INT8/FP8 tensor arithmetic at declared MFU. NVFP4 uses
Blackwell FP4 and is explicitly engine-dependent; other GPUs alarm. BF16 is
labelled academic in output and renamed `service-bf16-academic` (the old name
is removed). `service-quantized` is the default service scenario; `service-fp8`
remains a named quantized sensitivity. Weight bytes drive admission, independent
of arithmetic throughput. The server/client state-format and quality
compatibility have not been proven by this cost model.

Client quantization Q3/Q4 changes both memory and decode/prefill estimates.
Native M3 Max 16k decode is read from the hash-pinned normalized package:
7.48084–8.82004 tok/s, mean 8.25547. With actual GGUF bytes and the declared
KV/state traffic this is **40.9569%** of nominal bandwidth, rather than 30–37%.
The owner efficiency parameter therefore uses an explicit calibrated coordinate
(0.34 at the measured anchor), with its correction derived from measured rate,
traffic and bandwidth. Both fractions are printed. It would be incorrect to
claim the actual GGUF-byte efficiency is 30–37%. Other-Mac/Q3/GLM scaling is an
estimate. GLM parallel agents read a union of routed experts, not a shared
single-agent active-weight set.

## Gap design and negative evidence

Every new cell declares direct/transitive inputs. Missing/null inputs,
nonfinite numbers, wrong units, missing provenance, invalid ranges and infeasible
fits propagate alarms. Required catalogue keys are scenario data: removing an
API benchmark keeps its row and raises an alarm. No deleted input becomes a
zero, default or omitted result. Each array shape (including a failed-shape
placeholder) is registered once and reused across models/options; missing
entire catalogues cannot cause duplicate graph-node exceptions. Known-good unrelated tables stay identical.
Normal partial runs exit 0, strict runs exit 1, and unknown overrides exit 2.
The full owners' grid intentionally contains non-fitting models, so its strict
exit is 1 on complete data. Earlier `paper-base`/`glm-tier2` calibration analyses
retain their conventions; the new decisions are parameterized in the owners'
and quantized-service scenarios. Legacy wrappers remain the complete-data
exception and reproduce their frozen output byte for byte.

The named missing-input test activates every new owner quantity, including
nondefault format/precision branches, removes it (array holes are null), and
checks **every previously dependent cell** for the same root alarm. Another
test rejects null/NaN/infinity, wrong units and missing provenance for each
quantity with positive controls. New service precision coefficients and FP4
fields have selected-branch missing/invalid tests as well.

An initial test run detected benchmark rows disappearing when their prices were
deleted. Required scenario keys fixed this; `test_missing_benchmark_keeps_row`
and the all-input deletion test retain the witness. Initial test-only errors
(an incorrect 144-row expectation, and `.37` instead of JSON `0.37`) were
corrected; they are not reported as successful controls. Logs are in
`.temp/hybrid-calc-r3-261030/`.

## Paper summary: cost per person-month

These are costs for the same **open-model calls**. Remaining closed-model calls
are a common excluded expense. Demand is 2,500 calls/day × 21 days, multiplied
by share. Hybrid summary uses an existing Studio (explicit zero incremental
purchase fraction, with energy charged), shared L40S prefill capacity at 70%
load, egress, $5/person-month front cost, and cheapest same-model API overflow.
It buys fractional service capacity; it does not reserve a minimum GPU for each
team. This purchasing assumption explains its flat per-person cost. Dedicated
warm rentals and full new hardware are evaluated separately below.

The all-server comparator owns integer eight-GPU B300 nodes, Q4 weights, 32-stream
analytical batching, 25 tok/s per-stream target and 70% bandwidth efficiency. It
sums prefill, decode bandwidth and KV/state residency demand without overlap
credit. This is a sizing estimate without a latency SLA/queueing qualification.
API cost follows calc8's cached-prefix/previous-output cache-write convention.
Canonical Chutes cached input was corrected from $0.003 to **$0.0039/Mtoken**
per the supplied API note, yielding $1.61497/1,000 calls; legacy data is unchanged.

| Team | Open share | Case | Hybrid $/person-mo | Own all-server $/person-mo | API median | API cheapest | B300 nodes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.200 | decision case | 17.338 | 3,370.162 | 110.314 | 16.957 | 1 |
| 10 | 0.200 | decision case | 17.338 | 1,685.081 | 110.314 | 16.957 | 1 |
| 20 | 0.200 | decision case | 17.338 | 842.540 | 110.314 | 16.957 | 1 |
| 50 | 0.200 | decision case | 17.338 | 337.016 | 110.314 | 16.957 | 1 |
| 100 | 0.200 | decision case | 17.338 | 168.508 | 110.314 | 16.957 | 1 |
| 200 | 0.200 | decision case | 17.338 | 84.254 | 110.314 | 16.957 | 1 |
| 500 | 0.200 | decision case | 17.338 | 101.105 | 110.314 | 16.957 | 3 |
| 1000 | 0.200 | decision case | 17.338 | 84.254 | 110.314 | 16.957 | 5 |
| 5000 | 0.200 | decision case | 17.338 | 70.773 | 110.314 | 16.957 | 21 |
| 20000 | 0.200 | decision case | 17.338 | 69.931 | 110.314 | 16.957 | 83 |
| 5 | 0.500 | decision case | 35.269 | 3,370.162 | 275.785 | 42.393 | 1 |
| 10 | 0.500 | decision case | 35.269 | 1,685.081 | 275.785 | 42.393 | 1 |
| 20 | 0.500 | decision case | 35.269 | 842.540 | 275.785 | 42.393 | 1 |
| 50 | 0.500 | decision case | 35.269 | 337.016 | 275.785 | 42.393 | 1 |
| 100 | 0.500 | decision case | 35.269 | 337.016 | 275.785 | 42.393 | 2 |
| 200 | 0.500 | decision case | 35.269 | 252.762 | 275.785 | 42.393 | 3 |
| 500 | 0.500 | decision case | 35.269 | 202.210 | 275.785 | 42.393 | 6 |
| 1000 | 0.500 | decision case | 35.269 | 185.359 | 275.785 | 42.393 | 11 |
| 5000 | 0.500 | decision case | 35.269 | 175.248 | 275.785 | 42.393 | 52 |
| 20000 | 0.500 | decision case | 35.269 | 174.406 | 275.785 | 42.393 | 207 |
| 5 | 1 | academic bound | 77.662 | 3,370.162 | 551.569 | 84.786 | 1 |
| 10 | 1 | academic bound | 77.662 | 1,685.081 | 551.569 | 84.786 | 1 |
| 20 | 1 | academic bound | 77.662 | 842.540 | 551.569 | 84.786 | 1 |
| 50 | 1 | academic bound | 77.662 | 674.032 | 551.569 | 84.786 | 2 |
| 100 | 1 | academic bound | 77.662 | 505.524 | 551.569 | 84.786 | 3 |
| 200 | 1 | academic bound | 77.662 | 421.270 | 551.569 | 84.786 | 5 |
| 500 | 1 | academic bound | 77.662 | 370.718 | 551.569 | 84.786 | 11 |
| 1000 | 1 | academic bound | 77.662 | 353.867 | 551.569 | 84.786 | 21 |
| 5000 | 1 | academic bound | 77.662 | 350.497 | 551.569 | 84.786 | 104 |
| 20000 | 1 | academic bound | 77.662 | 348.812 | 551.569 | 84.786 | 414 |

Hybrid beats the median API at every displayed team size. At 20% share it is
slightly **more expensive** than the cheapest same-model host; at 50% it is
cheaper under this purchasing/capacity model. The owned cluster crosses the
median at 200 people (20%/50%) and 100 (academic 100%) on the supplied grid;
it never crosses the cheapest host on that grid. **The requested “about 500”
is not reproduced under these new assumptions.** The old notes' ~500 was the
academic 100% case under older economics/workload/weight/batching conventions.
These new thresholds come from the table, not a hard-coded target. They are
finite-grid results, not exact continuous/team-size thresholds.

| Share | Case | API | First sustained own-cluster crossover |
| --- | --- | --- | --- |
| 0.200 | decision case | api_median_user | 200 |
| 0.200 | decision case | api_cheapest_user | none on supplied grid |
| 0.500 | decision case | api_median_user | 200 |
| 0.500 | decision case | api_cheapest_user | none on supplied grid |
| 1 | academic bound | api_median_user | 100 |
| 1 | academic bound | api_cheapest_user | none on supplied grid |

## Client capacity and excess

Capacity combines device prefill/decode work with occupied-stream time, limited
by memory at the largest sampled context. `served=min(share*daily_calls,capacity)`;
overflow is reported and charged to the cheapest same-model API in the summary.
The conservative maximum-depth admission limits this dense Studio to one stream
on this workload despite the four-agent input. No calls disappear from demand.

| Share | Case | Requested/day | Mac capacity/day | Served/day | Excess/day | Active streams | tok/s per stream at 16k |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.200 | decision case | 500.000 | 901.564 | 500.000 | 0.000 | 1 | 25.344 |
| 0.500 | decision case | 1,250.000 | 901.564 | 901.564 | 348.436 | 1 | 25.344 |
| 1 | academic bound | 2500 | 901.564 | 901.564 | 1,598.436 | 1 | 25.344 |

## Four-year residual value: owned servers and full new Macs

The owned hybrid buys dedicated office RTX 5090 prefill boxes and full $5,499
Studios. Server and Mac residuals vary **independently**, not as one combined
parameter. 20% = cheaper hardware, 50% = wear, 80% = scarcity. Depreciation is
`purchase*(1-residual)/48`; energy/support are still paid at residual 1.
Positive savings mean cheaper than API; negative values mean more expensive.
The full CLI table has all 270 team/share/server-residual/client-residual rows.
The following 50-person, 50%-share slice shows all nine residual combinations.

| Server residual | Mac residual | Hybrid $/person-mo | Median API | Cheapest API | Savings vs median | Savings vs cheapest |
| --- | --- | --- | --- | --- | --- | --- |
| 0.200 | 0.200 | 135.570 | 275.785 | 42.393 | 0.508 | -2.198 |
| 0.200 | 0.500 | 101.201 | 275.785 | 42.393 | 0.633 | -1.387 |
| 0.200 | 0.800 | 66.832 | 275.785 | 42.393 | 0.758 | -0.576 |
| 0.500 | 0.200 | 131.257 | 275.785 | 42.393 | 0.524 | -2.096 |
| 0.500 | 0.500 | 96.888 | 275.785 | 42.393 | 0.649 | -1.285 |
| 0.500 | 0.800 | 62.520 | 275.785 | 42.393 | 0.773 | -0.475 |
| 0.800 | 0.200 | 126.945 | 275.785 | 42.393 | 0.540 | -1.994 |
| 0.800 | 0.500 | 92.576 | 275.785 | 42.393 | 0.664 | -1.184 |
| 0.800 | 0.800 | 58.207 | 275.785 | 42.393 | 0.789 | -0.373 |

The full-purchase result must not be substituted for the summary's existing-Mac
case. A new Mac and a private prefill pool can cost more than cheap APIs, even
at high residual values. The grid reports that result rather than declaring
positive savings in advance.

## Buying versus renting

For each team, open share and option, size a whole warm prefill pool (minimum
one unit). The server window is 10 h for one time zone or 24 h for global use,
with fixed daily calls. Macs keep their individual 10-hour day. Rental is paid
for the entire active window, not just busy GPU seconds. Net capex is total
purchase × (1-residual). Crossover months are
`net_capex/(monthly_rental-monthly_ownership_opex)` when that denominator is
positive; otherwise an alarm states buying never recovers costs at this load.
The four-year cash comparison also prints independently. No discount rate,
price drift or resale guarantee is assumed.

Below: 50 people, 50% share. Full CLI output has 1,620 team/share/option/window/
residual rows. Office rentals are counterfactual proxy tariffs, **not offers**.

| Option | Residual | Units 10h | Units 24h | Months 10h | Months 24h | Buy by 4y 10h | Buy by 4y 24h |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H100 SXM on demand | 0.200 | 1 | 1 | 66.951 | 19.382 | False | True |
| H100 SXM on demand | 0.500 | 1 | 1 | 41.844 | 12.114 | True | True |
| H100 SXM on demand | 0.800 | 1 | 1 | 16.738 | 4.845 | True | True |
| L40S on demand | 0.200 | 2 | 1 | 182.929 | 31.083 | False | True |
| L40S on demand | 0.500 | 2 | 1 | 114.331 | 19.427 | False | True |
| L40S on demand | 0.800 | 2 | 1 | 45.732 | 7.771 | True | True |
| RTX PRO 6000 hourly | 0.200 | 2 | 1 | 177.255 | 30.683 | False | True |
| RTX PRO 6000 hourly | 0.500 | 2 | 1 | 110.784 | 19.177 | False | True |
| RTX PRO 6000 hourly | 0.800 | 2 | 1 | 44.314 | 7.671 | True | True |
| B300 288 GB hourly | 0.200 | 1 | 1 | 52.230 | 16.270 | False | True |
| B300 288 GB hourly | 0.500 | 1 | 1 | 32.644 | 10.168 | True | True |
| B300 288 GB hourly | 0.800 | 1 | 1 | 13.057 | 4.067 | True | True |
| 2x H200 hourly | 0.200 | 1 | 1 | 118.490 | 27.776 | False | True |
| 2x H200 hourly | 0.500 | 1 | 1 | 74.056 | 17.360 | False | True |
| 2x H200 hourly | 0.800 | 1 | 1 | 29.623 | 6.944 | True | True |
| Office RTX 5090 | 0.200 | 3 | 2 | 60.212 | 19.440 | False | True |
| Office RTX 5090 | 0.500 | 3 | 2 | 37.633 | 12.150 | True | True |
| Office RTX 5090 | 0.800 | 3 | 2 | 15.053 | 4.860 | True | True |
| Office RTX PRO 6000 | 0.200 | 2 | 1 | 68.977 | 24.127 | False | True |
| Office RTX PRO 6000 | 0.500 | 2 | 1 | 43.111 | 15.079 | True | True |
| Office RTX PRO 6000 | 0.800 | 2 | 1 | 17.244 | 6.032 | True | True |
| Office 4x RTX PRO 6000 | 0.200 | 1 | 1 | 56.884 | 20.417 | False | True |
| Office 4x RTX PRO 6000 | 0.500 | 1 | 1 | 35.552 | 12.761 | True | True |
| Office 4x RTX PRO 6000 | 0.800 | 1 | 1 | 14.221 | 5.104 | True | True |
| Owned HGX B300 8-GPU | 0.200 | 1 | 1 | 52.230 | 16.270 | False | True |
| Owned HGX B300 8-GPU | 0.500 | 1 | 1 | 32.644 | 10.168 | True | True |
| Owned HGX B300 8-GPU | 0.800 | 1 | 1 | 13.057 | 4.067 | True | True |

Purchase budgets for H100 $40k, L40S $15k and H200 pair $80k are new explicit
hypothetical estimates including host, not supplier quotes. B300 standalone
capex/power allocates 1/8 of the calc4 node. Rental B300 is calc4's $9.50/GPU-h
estimate; the supplied serverless note quotes B200, not B300. H100/L40S tariffs
come from RunPod; RTX PRO 6000 and H200 from Koyeb. The pair assumes connected,
co-located H200s; buying two single-GPU tariffs does not guarantee that placement.
Office energy/support/space assumptions are explicit provenance-bearing inputs.
Source custody and URLs are in `SERVICE-SOURCES-261030.md`.

## Client fit

Each row accounts for Q3/Q4 weights, KV at the stated context, recurrent state
and 12 GB OS/app reserve. Qwen27/GLM Q4 uses the supplied GGUF size; Q3 scales
by the declared format ratio. Flash-Next is 125B total / 6B active, with 51B
n-gram parameters shown both in RAM and on SSD. Its weights are format-size
estimates; removing the table assumes runtime support and reports 0.2 ms/token
unmeasured lookup latency. This is a memory-fit table, not proof of SSD decode
performance. Full output has 96 configurations. Counts below are resident
sessions; **ALARM** means weights+KV+state+reserve do not fit, never a valid zero.

| Model | Quant | Placement | Context | Weights GB | KV GB | State GB | Total incl reserve GB | 36 GB | 64 GB | 96 GB | 128 GB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.8-27B | Q3 | all weights in RAM | 32000 | 14.757 | 1.114 | 0.157 | 28.028 | 7 | 29 | 54 | 79 |
| Qwen3.8-27B | Q3 | all weights in RAM | 64000 | 14.757 | 2.228 | 0.157 | 29.143 | 3 | 15 | 29 | 42 |
| Qwen3.8-27B | Q3 | all weights in RAM | 128000 | 14.757 | 4.456 | 0.157 | 31.371 | 2 | 8 | 15 | 21 |
| Qwen3.8-27B | Q4 | all weights in RAM | 32000 | 18.974 | 1.114 | 0.157 | 32.245 | 3 | 25 | 51 | 76 |
| Qwen3.8-27B | Q4 | all weights in RAM | 64000 | 18.974 | 2.228 | 0.157 | 33.359 | 2 | 13 | 27 | 40 |
| Qwen3.8-27B | Q4 | all weights in RAM | 128000 | 18.974 | 4.456 | 0.157 | 35.587 | 1 | 7 | 14 | 21 |
| Qwen3.8-Flash-Next | Q3 | all weights in RAM | 32000 | 54.688 | 0.406 | 0.059 | 67.152 | ALARM | ALARM | 63 | 132 |
| Qwen3.8-Flash-Next | Q3 | all weights in RAM | 64000 | 54.688 | 0.811 | 0.059 | 67.557 | ALARM | ALARM | 33 | 70 |
| Qwen3.8-Flash-Next | Q3 | all weights in RAM | 128000 | 54.688 | 1.622 | 0.059 | 68.368 | ALARM | ALARM | 17 | 36 |
| Qwen3.8-Flash-Next | Q3 | ngram on SSD | 32000 | 32.375 | 0.406 | 0.059 | 44.839 | ALARM | 42 | 111 | 180 |
| Qwen3.8-Flash-Next | Q3 | ngram on SSD | 64000 | 32.375 | 0.811 | 0.059 | 45.245 | ALARM | 22 | 59 | 96 |
| Qwen3.8-Flash-Next | Q3 | ngram on SSD | 128000 | 32.375 | 1.622 | 0.059 | 46.056 | ALARM | 11 | 30 | 49 |
| Qwen3.8-Flash-Next | Q4 | all weights in RAM | 32000 | 70.312 | 0.406 | 0.059 | 82.777 | ALARM | ALARM | 29 | 98 |
| Qwen3.8-Flash-Next | Q4 | all weights in RAM | 64000 | 70.312 | 0.811 | 0.059 | 83.182 | ALARM | ALARM | 15 | 52 |
| Qwen3.8-Flash-Next | Q4 | all weights in RAM | 128000 | 70.312 | 1.622 | 0.059 | 83.993 | ALARM | ALARM | 8 | 27 |
| Qwen3.8-Flash-Next | Q4 | ngram on SSD | 32000 | 41.625 | 0.406 | 0.059 | 54.089 | ALARM | 22 | 91 | 160 |
| Qwen3.8-Flash-Next | Q4 | ngram on SSD | 64000 | 41.625 | 0.811 | 0.059 | 54.495 | ALARM | 11 | 48 | 85 |
| Qwen3.8-Flash-Next | Q4 | ngram on SSD | 128000 | 41.625 | 1.622 | 0.059 | 55.306 | ALARM | 6 | 25 | 44 |
| GLM-5.3-Flash | Q3 | all weights in RAM | 32000 | 141.089 | 0.191 | 0.153 | 153.433 | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q3 | all weights in RAM | 64000 | 141.089 | 0.383 | 0.153 | 153.624 | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q3 | all weights in RAM | 128000 | 141.089 | 0.766 | 0.153 | 154.007 | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q4 | all weights in RAM | 32000 | 181.400 | 0.191 | 0.153 | 193.744 | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q4 | all weights in RAM | 64000 | 181.400 | 0.383 | 0.153 | 193.936 | ALARM | ALARM | ALARM | ALARM |
| GLM-5.3-Flash | Q4 | all weights in RAM | 128000 | 181.400 | 0.766 | 0.153 | 194.319 | ALARM | ALARM | ALARM | ALARM |

Fit alarm roots are `owners.memories.0` through `.3`: model does not fit,
weights + KV + recurrent state + OS/app reserve exceed memory. GLM fails all
requested laptop configurations, while 256 GB Studios are sized separately.

## Small teams and GLM Studios

The 20% production share applies to 5/10/50 heavy users, with whole warm rentals
or office ownership and full Studio depreciation/energy. Each session is a
116-call normalization group. Cost per served session includes GPU, egress,
front and full Mac cost; excess calls are reported separately and are not in
this session denominator. The API and separately owned all-server comparator
price the same call mix. They exclude Mac purchase. Thus this is a deliberately
stricter procurement comparison than the existing-Mac pooled-service summary.

| Model | Team | Option | Units | Resident sessions/Mac | Active streams | tok/s/stream 16k | Served/day | Excess/day | Hybrid $/session | API $/session | Own server $/session |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.8-27B | 5 | H100 SXM on demand | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 3.010 | 1.219 | 2.268 |
| Qwen3.8-27B | 10 | H100 SXM on demand | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 2.084 | 1.219 | 2.268 |
| Qwen3.8-27B | 50 | H100 SXM on demand | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.344 | 1.219 | 1.361 |
| Qwen3.8-27B | 5 | L40S on demand | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.664 | 1.219 | 1.826 |
| Qwen3.8-27B | 10 | L40S on demand | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.412 | 1.219 | 1.826 |
| Qwen3.8-27B | 50 | L40S on demand | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.209 | 1.219 | 1.552 |
| Qwen3.8-27B | 5 | RTX PRO 6000 hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 2.179 | 1.219 | 1.826 |
| Qwen3.8-27B | 10 | RTX PRO 6000 hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.669 | 1.219 | 1.826 |
| Qwen3.8-27B | 50 | RTX PRO 6000 hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.261 | 1.219 | 1.461 |
| Qwen3.8-27B | 5 | B300 288 GB hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 5.567 | 1.219 | 4.654 |
| Qwen3.8-27B | 10 | B300 288 GB hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 3.363 | 1.219 | 2.327 |
| Qwen3.8-27B | 50 | B300 288 GB hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.599 | 1.219 | 0.931 |
| Qwen3.8-27B | 5 | 2x H200 hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 3.943 | 1.219 | 4.537 |
| Qwen3.8-27B | 10 | 2x H200 hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 2.551 | 1.219 | 2.268 |
| Qwen3.8-27B | 50 | 2x H200 hourly | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.437 | 1.219 | 0.907 |
| Qwen3.8-27B | 5 | Office RTX 5090 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.750 | 1.219 | 1.775 |
| Qwen3.8-27B | 10 | Office RTX 5090 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.454 | 1.219 | 1.775 |
| Qwen3.8-27B | 50 | Office RTX 5090 | 2 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.277 | 1.219 | 1.597 |
| Qwen3.8-27B | 5 | Office RTX PRO 6000 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 2.515 | 1.219 | 1.357 |
| Qwen3.8-27B | 10 | Office RTX PRO 6000 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.837 | 1.219 | 1.357 |
| Qwen3.8-27B | 50 | Office RTX PRO 6000 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.294 | 1.219 | 1.085 |
| Qwen3.8-27B | 5 | Office 4x RTX PRO 6000 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 5.834 | 1.219 | 4.676 |
| Qwen3.8-27B | 10 | Office 4x RTX PRO 6000 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 3.496 | 1.219 | 2.338 |
| Qwen3.8-27B | 50 | Office 4x RTX PRO 6000 | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 1.626 | 1.219 | 0.935 |
| Qwen3.8-27B | 5 | Owned HGX B300 8-GPU | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 36.423 | 1.219 | 37.232 |
| Qwen3.8-27B | 10 | Owned HGX B300 8-GPU | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 18.791 | 1.219 | 18.616 |
| Qwen3.8-27B | 50 | Owned HGX B300 8-GPU | 1 | 1 | 1 | 25.344 | 500.000 | 0.000 | 4.685 | 1.219 | 3.723 |
| GLM-5.3-Flash | 5 | H100 SXM on demand | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 10 | H100 SXM on demand | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 50 | H100 SXM on demand | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 5 | L40S on demand | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 10 | L40S on demand | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 50 | L40S on demand | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 5 | RTX PRO 6000 hourly | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 10 | RTX PRO 6000 hourly | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 50 | RTX PRO 6000 hourly | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 5 | B300 288 GB hourly | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 6.526 | 0.668 | 4.654 |
| GLM-5.3-Flash | 10 | B300 288 GB hourly | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 4.322 | 0.668 | 2.327 |
| GLM-5.3-Flash | 50 | B300 288 GB hourly | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 2.559 | 0.668 | 0.931 |
| GLM-5.3-Flash | 5 | 2x H200 hourly | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 4.902 | 0.668 | 4.537 |
| GLM-5.3-Flash | 10 | 2x H200 hourly | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 3.510 | 0.668 | 2.268 |
| GLM-5.3-Flash | 50 | 2x H200 hourly | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 2.396 | 0.668 | 0.907 |
| GLM-5.3-Flash | 5 | Office RTX 5090 | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 10 | Office RTX 5090 | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 50 | Office RTX 5090 | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 5 | Office RTX PRO 6000 | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 10 | Office RTX PRO 6000 | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 50 | Office RTX PRO 6000 | ALARM | 10 | 4 | 13.474 | 500.000 | 0.000 | ALARM | 0.668 | ALARM |
| GLM-5.3-Flash | 5 | Office 4x RTX PRO 6000 | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 6.794 | 0.668 | 4.676 |
| GLM-5.3-Flash | 10 | Office 4x RTX PRO 6000 | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 4.456 | 0.668 | 2.338 |
| GLM-5.3-Flash | 50 | Office 4x RTX PRO 6000 | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 2.586 | 0.668 | 0.935 |
| GLM-5.3-Flash | 5 | Owned HGX B300 8-GPU | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 37.382 | 0.668 | 37.232 |
| GLM-5.3-Flash | 10 | Owned HGX B300 8-GPU | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 19.750 | 0.668 | 18.616 |
| GLM-5.3-Flash | 50 | Owned HGX B300 8-GPU | 1 | 10 | 4 | 13.474 | 500.000 | 0.000 | 5.644 | 0.668 | 3.723 |

GLM Q4 server weights are 328B × 0.5625 = 184.5 GB plus 8 GB workspace.
H100 80 GB, L40S 48 GB, single RTX PRO 6000 96 GB and office 5090 32 GB alarm
at their `owners.options.<option>.memory` inputs. B300 288 GB, paired H200
282 GB and four-RTX 384 GB fit under the explicit balanced-shard assumption.
At Q8, weights are 348.5 GB, so the single B300 also alarms. Pooling memory
requires a qualified sharded runtime; it is not proven by adding memory sizes.
Model and placement failures do not remove Mac session or API cells.

## Break-even selling price

This is the pooled prefill service cost to cover GPU, egress and the front at
20% target gross margin, excluding customer Mac purchase and API overflow.
Front cost is allocated over served open calls; margin 1 or zero served calls
alarms instead of dividing by zero. MiMo/Chutes/Flash references are $0.83/
$1.61/$3.42 per 1,000 calls, from the supplied calc8/API research. They are not
claims of equivalent model quality. The rounded Chutes reference differs
slightly from recomputing its token tariff on the sampled mix.

| Share | Case | GPU $/1k | Egress $/1k | Front $/1k | Target margin | Price $/1k |
| --- | --- | --- | --- | --- | --- | --- |
| 0.200 | decision case | 0.392 | 0.333 | 0.476 | 0.200 | 1.502 |
| 0.500 | decision case | 0.392 | 0.333 | 0.264 | 0.200 | 1.236 |
| 1 | academic bound | 0.392 | 0.333 | 0.264 | 0.200 | 1.236 |

At the default costs, the service price exceeds MiMo's reference; it is below
Chutes and Flash. That is a calculation result, not an assertion that running
the service beats every API. A lower/higher front or egress price changes it
through the declared inputs.

## Tests and bounded controls

| Claim / corner | Named executable coverage |
|---|---|
| Same open-call denominator and capped excess; summary labels 100% academic | `test_summary_shares_and_capacity` |
| Derived sustained crossover from summary, no target-team constant | `test_derived_equilibrium` |
| Independent residual endpoints 0/1; one person; correct relative savings | `test_residual_endpoints_and_team_one` |
| Integer buy/rent pool and net-capex crossover formula | `test_buy_rent_formula` |
| Complete fit byte accounting, GLM laptop rejection, SSD n-gram subtraction | `test_fit_components_and_rejection`, `test_flash_ngram_both_placements` |
| Small-team GLM server memory alarm preserves Mac/API metrics | `test_small_teams_memory_alarm` |
| GPU+egress+front gross-margin formula; margin 1 alarm | `test_break_even_margin` |
| Every owner quantity missing; null/nonfinite/unit/provenance rejection | `test_every_owner_input_missing`, `test_every_owner_quantity_contract` |
| Zero prices/reserve/front/margin; valid unity utilization/efficiency; invalid domains | `test_nonnegative_zero_controls`, `test_domain_boundaries` |
| Zero load alarms costs, not static fit; empty/single workloads | `test_zero_load_independence`, `test_empty_call_mix`, single-call fixtures throughout |
| Missing front creates exactly one new root alarm, unrelated tables identical | `test_planted_front_gap_control` |
| Measured anchor, efficiency/quant/prefill/agent capacity controls; MoE expert union | `test_client_calibration_and_capacity_inputs`, `test_glm_parallel_expert_union` |
| Quantized service default, BF16 academic rename, selected format memory checks | `test_quantized_default_and_precision_memory`, `test_server_quantization_and_blackwell` |
| New service format coefficients/FP4 fields missing, nonfinite/invalid | `test_new_service_inputs_missing` |
| Corrupted benchmark checksum leaves static fit available | `test_measurement_gap_independence` |
| Active > total parameters or oversized SSD table alarms | `test_inconsistent_model_parameters` |
| Missing benchmark cannot delete its comparison rows | `test_missing_benchmark_keeps_row` |
| Missing/null/empty whole arrays and catalogues retain partial tables | `test_missing_owner_catalogues_preserve_partial_results` |
| Existing nine golden outputs, planted original input, Python 3.9 syntax, all run-2 gap/corner tests | All prior test names retained; nine hash-pinned golden comparisons |

The source/test/data identity for the exact delivery validation is
`d5ed7115d0f6bd46683b277f1a48da95f37b8ae6977dbd01bea14fabd1141662`. Logs and direct standalone-process PIDs/exits are in
`.temp/hybrid-calc-r3-261030/validation.json`. Python/platform execution is the
local Linux Python 3.14.4 environment; Python 3.9 compatibility is grammar/API
checked, not a native macOS/Python 3.9 run. No PDF build was needed or run;
no paper/build files changed.

| Exact command | Actual exit |
| --- | --- |
| `python3 -m unittest discover -s calc/tests` | 0 |
| `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | 0 |
| `python3 -m hybridcalc list` | 0 |
| `python3 -m hybridcalc run paper-base --strict --format json` | 0 |
| `python3 -m hybridcalc run glm-tier2 --strict --format json` | 0 |
| `python3 -m hybridcalc run service-quantized --strict --format json` | 0 |
| `python3 -m hybridcalc run service-fp8 --strict --format json` | 0 |
| `python3 -m hybridcalc run service-bf16-academic --format md` | 0 |
| `python3 -m hybridcalc run service-bf16-academic --strict --format json` | 1 |
| `python3 -m hybridcalc run owners-economics --format json` | 0 |
| `python3 -m hybridcalc run owners-economics --strict --format md` | 1 |
| `python3 -m hybridcalc run owners-economics --set owners.server_precision=NVFP4 --format csv` | 0 |
| `python3 -m hybridcalc run owners-economics --set owners.server_precision=BF16 --format md` | 0 |
| `python3 -m hybridcalc run owners-economics --set owners.client_quant=Q3 owners.client_efficiency=0.37 --format tex` | 0 |
| `python3 -m hybridcalc sources owners-economics --format json` | 0 |
| `python3 -m hybridcalc run owners-economics --set owners.typo=1` | 2 |
| `python3 -m hybridcalc run owners-economics --set owners.front_month=null --format json` | 0 |
| `python3 -m hybridcalc run owners-economics --set owners.front_month=null --strict --format json` | 1 |
| `python3 -m hybridcalc run paper-base --set prices.rental_gpu_hour=null --format json` | 0 |
| `python3 -m hybridcalc run paper-base --set prices.rental_gpu_hour=null --strict --format json` | 1 |
| `python3 .temp/hybrid-calc-r3-261030/front-control.py` | 1 |
| `python3 .temp/hybrid-calc-r3-261030/cap-control.py` | 1 |


The full suite ran **82 tests, exit 0** (105.995 seconds). Both bounded controls
first failed to import the package from their scratch directory; those exits
are explicitly **not mutation evidence** (`*-control-01.stderr`). After fixing
the helper import path, `*-control-03.stderr` records the named intended
assertion failure with no test error. The report-generation helper had the
same scratch import error and was corrected before producing this report.

Expected-red strict commands print the requested fit/gap alarms before exit 1.
The unknown override is a command error (2), with no traceback. Two bounded
mutants verify the new tests detect forbidden numbers; neither mutant modifies
the working tree or persists outside its test process:

| Mutant | Gate narrowed to | Named failing test | Actual exit / limit |
|---|---|---|---|
| Missing `owners.front_month` returns 0 | Missing front cannot become a numeric fallback | `OwnershipInputTests.test_planted_front_gap_control` | 1, intended assertion failure (missing expected root alarm) |
| `served=requested` bypasses Mac cap | Demand cannot exceed measured/modelled per-Mac capacity | `OwnershipTests.test_summary_shares_and_capacity` | 1, intended cap assertion failure |

No surviving mutant is claimed. These two controls do not qualify other
unstaged mutations or prove all model/physical assumptions. Original golden
input-plant coverage also runs in the full suite.

## Limits and scope

- The requested universal “hybrid beats API” and “own cluster about 500” are not
  forced into the results. They depend on API host, open share, purchase model,
  workload accounting, quantization, capacity, memory and batching assumptions.
- The summary assumes access to a shared service at its declared occupancy.
  Dedicated-team rentals have integer idle costs. Capacity overflow assumes the
  same call distribution and uses a priced API fallback; no overflow is hidden.
- Actual runtime kernel support, state conversion, quality equivalence,
  quantized MFU, cross-node/shard efficiency, queueing, latency SLA and Flash
  SSD lookup performance remain unqualified. M5 Ultra is still an estimate.
- New H100/L40S/H200 acquisition budgets and office proxy rentals are estimates.
  Tariffs remain dated offline observations; tax, provider extras, financing,
  time value of money and unmeasured operational overhead are not silently
  represented as measured costs. The explicit front is an estimate allocation.
- Full04 workload retains calc8's conservative reasoning sum and synthetic
  116-call grouping, not reconstructed real sessions. Full05 dates/counts are
  never spliced into its denominator. One sampled maximum depth conservatively
  limits client concurrency; more advanced scheduling needs a different model.
- The owner's efficiency coordinate differs from actual GGUF-byte roofline
  efficiency; both are printed and the discrepancy is unresolved physical
  denominator evidence, not a hidden calibration change.
- No explicit surface table was supplied in the brief; the test/claim table
  above is the finite coverage map. No owner-facing review or CI acceptance is
  claimed. No push or landing is authorized; this is local signed review handoff.
- Files outside `calc/`: required root README, manifest and the existing
  `UNRESOLVED_QUESTIONS.md` assumption register only. They document this same
  scope. Measurement packages and forbidden directories remain unchanged.

# Prior run 2 evidence

# Calculation engine — run 2, hybrid-calc-r2-261030

Continues `calc-engine` from independently reviewed signed commit `aaec23c3`.
Local signed delivery only; no fetch, push, install, online research or edits to
`paper/`, `.github/`, `.scripts/`, `tools/` or `data/research/`. The requested
team summary is the sole messaging exception to offline work.

## Gap and alarm design

Canonical `paper`, `glm` and new `service` scenarios use a dependency DAG in
`metrics.py`. Every output cell declares direct requirements and transitive
input paths in `tables[].dependencies["row.column"]`. `analysis_graph.py` shares
the measured workload and calibration definitions. `paper.py` separates units,
prices, memory, call filtering, transfer policy, decode capacity and individual
cost components. `service.py` composes precise workload/precision/tariff nodes.

Input contracts are read lazily by dependency. Missing/null fields, bad units,
missing provenance, invalid types/ranges, NaN/infinity and failed measured-file
checks produce an input-path/reason alarm. No fallback number or fabricated
measurement is introduced. Failed nodes preserve their root causes through all
dependents; independent nodes still compute. This also separates pair-only GLM
communication inputs from single-machine decode, and laptop premiums from
owned/full-price device accounting.

A JSON cell is `{"alarm": [{"input": "prices.rental_gpu_hour", "reason": "missing input"}]}`.
Markdown, CSV and TeX render `ALARM: input: reason` in the cell and list unique
alarms after each table. JSON stores table-level and global deduplicated alarms.
A zero multiplier does not erase a missing dependency. A valid zero price is
allowed. An infeasible declared placement is an alarm, not an invented runtime.
A finite-grid comparison with no crossover is a valid textual result, not a gap.

Exit contract:

| Mode / condition | Exit | Output |
|---|---:|---|
| Normal, any numeric metrics available | 0 | Computable cells plus all alarms |
| `--strict`, any alarm | 1 | Same partial output, then nonzero exit |
| Either mode, no numeric metric computable | 1 | Alarm output; labels/constant identities do not count as numeric evidence |
| Unknown override, malformed CLI/scenario syntax | 2 | Clear command error, no traceback |

`--strict` also applies to `sources`. Known canonical overrides with invalid
values become alarms; unknown override paths remain errors. Legacy wrappers
retain the strict complete-data path and their exact output. No legacy transcript
has alarm text inserted, and no legacy algorithm, wrapper or `.out` was changed.
All nine golden outputs still pass. All 29 existing test names are kept; the
strict override test still exercises the strict Inputs API. The old sampler
claim that fewer than 116 calls was invalid was revised for the explicitly
requested empty/single-call contract, without dropping or renaming the test.

There are no implicit local-file fallbacks. Custom scenarios use local paths
relative to their own directory, or explicit `bundle:...` references. Standard
file namespaces are declared in `file-contract.json`; custom files may state
`{"file":"prices-local.json","provides":["prices"]}`. A failed scoped file
invalidates earlier data it could have overridden, preserving other namespaces.
An unreadable file with unknown scope conservatively invalidates all earlier
data. Later explicitly supplied quantities can restore known fields. Missing or
corrupt measurement packages alarm at `measurements.<name>`; no unchecked
original or lane copy is searched for. Invalid measured numeric fields cannot
be transformed into apparently valid samples by a cap.

## Corner-case evidence

Every test/group has an adjacent claim comment. The relevant cases are:

| Case | Correct value or alarm asserted | Named test |
|---|---|---|
| Prefill depth 0 | 54e9 FLOP/token for the Qwen reference | `BoundaryTests.test_depth_zero_and_context_limit` |
| Declared context boundary | 54e9 + 393216 × limit; limit+1 alarms | same test |
| One call at depth 0 / context boundary | Exact cached-prefix/output API arithmetic; unsupported client memory alarms rather than charging zero | `BoundaryTests.test_one_call_at_both_depth_boundaries` |
| Empty / single call mix | Empty count=0 with mean/cost alarms; one call valid | `GapTests.test_empty_and_single_call` |
| Link bandwidth zero or missing | Offload-impossible alarm, no instant/infinite transfer; API/local values remain | `GapTests.test_zero_and_missing_link` |
| Service transfer gap | GPU counts/tariffs and API rows identical; byte/egress/total cells alarm | `ServiceTests.test_transfer_gap_preserves_gpu_and_api` |
| Zero price | Exact zero rent and egress on complete inputs | `GapTests.test_utilization_and_zero_price`, `ServiceTests.test_load_and_mfu_alarms` |
| Utilization 0 / 1 | Zero alarms; one has independently calculated nonzero rental cost and exact capacity ceiling | `PrecisionControlTests.test_full_utilization_and_missing_depth_package`, plus the two tests above |
| Missing measurement file | Scoped unavailable alarm; unrelated workload/API or calibration tables unchanged | `GapTests.test_measurement_missing_or_corrupt`, `PrecisionControlTests.test_full_utilization_and_missing_depth_package` |
| SHA-256 mismatch | Source alarm, all dependent prices blocked, independent measurement tables unchanged | `BoundaryTests.test_corrupted_workload_preserves_measurement_tables` |
| Nonfinite measured field with repinned file hash | Finite-number alarm, never a sampled cap standing in for NaN | `BoundaryTests.test_nonfinite_measured_field_is_not_capped_to_a_number` |
| Input null, wrong unit/provenance, NaN, infinity | Input-specific alarm; calibration unchanged; JSON contains no nonfinite numeric value | `GapTests.test_invalid_values_are_alarms` |
| Unknown override path | Hard error remains, exit 2 without traceback | `GapTests.test_cli_exit_contract`, existing `EndToEndTests.test_cli_and_wrapper` |
| Missing local / malformed source file | No bundled or earlier-value fallback; unrelated datasets compute | `SourceFileTests.test_failed_scoped_layer_has_no_earlier_fallback`, `test_missing_or_malformed_local_file` |
| Invalid array entry / null catalogue | Other cohort rows and independent tables preserved | `SourceFileTests.test_invalid_user_entry_preserves_other_cohorts`, `CatalogueTests.test_null_catalogues_preserve_unrelated_results` |
| Missing laptop baseline / pair-only input | Owned/full-price devices and single-machine GLM rows identical | `BoundaryTests.test_missing_baseline_has_only_laptop_dependents`, `TopologyTests.test_pair_only_input_does_not_taint_single_machine` |
| Invalid full05 count | Only the invalid count alarms; other date fields and full04 API cells remain valid | `SnapshotContractTests.test_invalid_date_count_is_scoped_to_its_metric` |
| Malformed scenario shape | Clear command error, exit 2, no numeric output or traceback | `ScenarioErrorTests.test_malformed_scenario_shape_has_no_traceback` |
| Nothing computable | Printed alarms, exit 1, no traceback | `BoundaryTests.test_nothing_computable_exits_one` |

The planted-gap control removes just `prices.rental_gpu_hour` from `paper-base`.
It asserts exactly one global root alarm, checks every affected cell against
that alarm and its declared dependency, and checks every unaffected cell plus
all unrelated tables for exact equality. No approximate comparison is used in
that isolation control.

| Mutant / plant | Gate narrowed to | Named failing test | Survival bound |
|---|---|---|---|
| Missing rental price silently replaced with zero | Detecting a forbidden numeric default for this input while independent tables survive | `test_gaps.GapTests.test_planted_gap_preserves_independent_tables` | Killed: actual standalone control exits 1 with `[]` versus the required alarm. No claim about all possible default mutations. |

The normal missing-input control passes; the deliberately broken implementation
above is expected red. It never edits product data or source files.

## Service inputs, sources and formulas

The read-only ad-hoc script's observed SHA-256 is `c901134c6435c9bb487e1f1d91500bcb18ce69e74b05f78736dce647486ebb5c`.
The provider research note's observed SHA-256 is
`c6f80c99361ef7d849e2fad857b6e93011c2166381aa2b620ba50862dd9bccbc`.
[`SERVICE-SOURCES-261030.md`](SERVICE-SOURCES-261030.md) preserves the relevant
§2/§5 tariffs, source IDs/URLs/access dates, precision envelopes and assumptions;
`hybridcalc/data/service.json` records provenance for every value. No URL was fetched.

The engine derives the reference from the same seeded 39,904-call prefix as
calc8, with its explicit conservative reasoning sum and cache-write grouping:

* FLOPs/call = **196.692560974 TFLOP**.
* Download/call = **66.670378361 MB**.
* These round to the ad-hoc 196.69 TFLOP and 67 MB. Neither is hard-coded.
* The Flash and 27B API estimates are derived from precisely the same calls and
  their historical tariff convention (about $3.42 and $10.51 per 1000 calls).

The transfer reference declares calc8's tuned M5 Max, 1 Gbit/s link and B300
admission policy; it stays fixed while the compared server SKU/precision changes.
Every new and generated token is shadow-prefilled. The reference is distinct
from `paper-base`'s measured-curve/output-only default. The sampler's explicit
minimum median is a provenance-bearing fit assumption, never a missing-value
substitute. Empty data produce no fitted mean.

Default users are 10, 100 and 1000. Daily profiles: light 200, medium 800,
heavy 2500, measured power user 6500. The last is an explicit rounded profile
estimate, not an instantaneous-arrival guarantee. Window: 10 h × 21 days;
target load 70%; independent prefill MFU 30%.

```
GPU_s_call = derived_FLOP_call / (selected_precision_peak_FLOP_s * MFU)
GPUs = max(1, ceil(N * calls_day * GPU_s_call /
                   (active_hours * 3600 * target_load)))
TB_month = N * calls_day * active_days * derived_download_bytes / 1e12
```

Per-second options bill the whole warm-pool active window, including integer
idle headroom. No busy-seconds-only discount or invented scale-to-zero benefit
is assumed. Hetzner bills the full calendar month. It converts €999 recurring
and €999 setup separately at 1.1130 USD/EUR; setup is shown upfront, amortized
over the explicit 12-month input, and charged once in first-month cash. Egress
has declared $0/$5/$50 sensitivity inputs and a separate selected price.

FP8/BF16 is a scenario parameter (`service.precision`, also overridable). Dense
server weight bytes change independently of the quantized client state format.
Weights/workspace memory is checked before deployment costs: BF16's 54 GB
weights plus declared 8 GB workspace exceed a 48 GB L40S. No sharding, CPU
offload or fictitious extra memory is assumed. Theoretical GPU-seconds and API/
egress arithmetic still compute; L40S deployment counts and costs alarm.

## Sizing results

All values below are estimates. GPU dollars/month include amortized setup where
applicable. Per-user totals include the selected $5/TB egress. Monthly prices
exclude tax. `ALARM*` is the single BF16 L40S capacity alarm stated above. FP8
has no alarms. BF16 without `--strict` exits 0 with partial results; with
`--strict` it exits 1 as intended.

| Profile | N | Option | FP8 GPUs | BF16 GPUs | FP8 GPU $/mo | BF16 GPU $/mo | FP8 total $/user-mo | BF16 total $/user-mo | Flash / 27B API $/user-mo |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| light | 10 | H100 SXM $3.99/h | 1 | 1 | 837.90 | 837.90 | 85.19 | 85.19 | 14.35 / 44.13 |
| light | 10 | H100 PCIe $2.89/h | 1 | 1 | 606.90 | 606.90 | 62.09 | 62.09 | 14.35 / 44.13 |
| light | 10 | L40S $1.09/h | 1 | ALARM* | 228.90 | ALARM* | 24.29 | ALARM* | 14.35 / 44.13 |
| light | 10 | Koyeb H100 $2.50/h | 1 | 1 | 525.00 | 525.00 | 53.90 | 53.90 | 14.35 / 44.13 |
| light | 10 | Hetzner RTX PRO 6000 | 1 | 1 | 1,204.54 | 1,204.54 | 121.85 | 121.85 | 14.35 / 44.13 |
| light | 100 | H100 SXM $3.99/h | 1 | 1 | 837.90 | 837.90 | 9.78 | 9.78 | 14.35 / 44.13 |
| light | 100 | H100 PCIe $2.89/h | 1 | 1 | 606.90 | 606.90 | 7.47 | 7.47 | 14.35 / 44.13 |
| light | 100 | L40S $1.09/h | 1 | ALARM* | 228.90 | ALARM* | 3.69 | ALARM* | 14.35 / 44.13 |
| light | 100 | Koyeb H100 $2.50/h | 1 | 1 | 525.00 | 525.00 | 6.65 | 6.65 | 14.35 / 44.13 |
| light | 100 | Hetzner RTX PRO 6000 | 1 | 2 | 1,204.54 | 2,409.09 | 13.45 | 25.49 | 14.35 / 44.13 |
| light | 1000 | H100 SXM $3.99/h | 3 | 6 | 2,513.70 | 5,027.40 | 3.91 | 6.43 | 14.35 / 44.13 |
| light | 1000 | H100 PCIe $2.89/h | 4 | 7 | 2,427.60 | 4,248.30 | 3.83 | 5.65 | 14.35 / 44.13 |
| light | 1000 | L40S $1.09/h | 8 | ALARM* | 1,831.20 | ALARM* | 3.23 | ALARM* | 14.35 / 44.13 |
| light | 1000 | Koyeb H100 $2.50/h | 3 | 6 | 1,575.00 | 3,150.00 | 2.98 | 4.55 | 14.35 / 44.13 |
| light | 1000 | Hetzner RTX PRO 6000 | 6 | 12 | 7,227.27 | 14,454.53 | 8.63 | 15.85 | 14.35 / 44.13 |
| medium | 10 | H100 SXM $3.99/h | 1 | 1 | 837.90 | 837.90 | 89.39 | 89.39 | 57.41 / 176.50 |
| medium | 10 | H100 PCIe $2.89/h | 1 | 1 | 606.90 | 606.90 | 66.29 | 66.29 | 57.41 / 176.50 |
| medium | 10 | L40S $1.09/h | 1 | ALARM* | 228.90 | ALARM* | 28.49 | ALARM* | 57.41 / 176.50 |
| medium | 10 | Koyeb H100 $2.50/h | 1 | 1 | 525.00 | 525.00 | 58.10 | 58.10 | 57.41 / 176.50 |
| medium | 10 | Hetzner RTX PRO 6000 | 1 | 1 | 1,204.54 | 1,204.54 | 126.05 | 126.05 | 57.41 / 176.50 |
| medium | 100 | H100 SXM $3.99/h | 2 | 3 | 1,675.80 | 2,513.70 | 22.36 | 30.74 | 57.41 / 176.50 |
| medium | 100 | H100 PCIe $2.89/h | 2 | 3 | 1,213.80 | 1,820.70 | 17.74 | 23.81 | 57.41 / 176.50 |
| medium | 100 | L40S $1.09/h | 3 | ALARM* | 686.70 | ALARM* | 12.47 | ALARM* | 57.41 / 176.50 |
| medium | 100 | Koyeb H100 $2.50/h | 2 | 3 | 1,050.00 | 1,575.00 | 16.10 | 21.35 | 57.41 / 176.50 |
| medium | 100 | Hetzner RTX PRO 6000 | 3 | 5 | 3,613.63 | 6,022.72 | 41.74 | 65.83 | 57.41 / 176.50 |
| medium | 1000 | H100 SXM $3.99/h | 11 | 22 | 9,216.90 | 18,433.80 | 14.82 | 24.03 | 57.41 / 176.50 |
| medium | 1000 | H100 PCIe $2.89/h | 14 | 28 | 8,496.60 | 16,993.20 | 14.10 | 22.59 | 57.41 / 176.50 |
| medium | 1000 | L40S $1.09/h | 29 | ALARM* | 6,638.10 | ALARM* | 12.24 | ALARM* | 57.41 / 176.50 |
| medium | 1000 | Koyeb H100 $2.50/h | 11 | 22 | 5,775.00 | 11,550.00 | 11.38 | 17.15 | 57.41 / 176.50 |
| medium | 1000 | Hetzner RTX PRO 6000 | 24 | 48 | 28,909.06 | 57,818.12 | 34.51 | 63.42 | 57.41 / 176.50 |
| heavy | 10 | H100 SXM $3.99/h | 1 | 1 | 837.90 | 837.90 | 101.29 | 101.29 | 179.40 / 551.57 |
| heavy | 10 | H100 PCIe $2.89/h | 1 | 1 | 606.90 | 606.90 | 78.19 | 78.19 | 179.40 / 551.57 |
| heavy | 10 | L40S $1.09/h | 1 | ALARM* | 228.90 | ALARM* | 40.39 | ALARM* | 179.40 / 551.57 |
| heavy | 10 | Koyeb H100 $2.50/h | 1 | 1 | 525.00 | 525.00 | 70.00 | 70.00 | 179.40 / 551.57 |
| heavy | 10 | Hetzner RTX PRO 6000 | 1 | 2 | 1,204.54 | 2,409.09 | 137.96 | 258.41 | 179.40 / 551.57 |
| heavy | 100 | H100 SXM $3.99/h | 4 | 7 | 3,351.60 | 5,865.30 | 51.02 | 76.15 | 179.40 / 551.57 |
| heavy | 100 | H100 PCIe $2.89/h | 5 | 9 | 3,034.50 | 5,462.10 | 47.85 | 72.12 | 179.40 / 551.57 |
| heavy | 100 | L40S $1.09/h | 9 | ALARM* | 2,060.10 | ALARM* | 38.10 | ALARM* | 179.40 / 551.57 |
| heavy | 100 | Koyeb H100 $2.50/h | 4 | 7 | 2,100.00 | 3,675.00 | 38.50 | 54.25 | 179.40 / 551.57 |
| heavy | 100 | Hetzner RTX PRO 6000 | 8 | 15 | 9,636.35 | 18,068.16 | 113.86 | 198.18 | 179.40 / 551.57 |
| heavy | 1000 | H100 SXM $3.99/h | 33 | 66 | 27,650.70 | 55,301.40 | 45.15 | 72.80 | 179.40 / 551.57 |
| heavy | 1000 | H100 PCIe $2.89/h | 43 | 86 | 26,096.70 | 52,193.40 | 43.60 | 69.69 | 179.40 / 551.57 |
| heavy | 1000 | L40S $1.09/h | 90 | ALARM* | 20,601.00 | ALARM* | 38.10 | ALARM* | 179.40 / 551.57 |
| heavy | 1000 | Koyeb H100 $2.50/h | 33 | 66 | 17,325.00 | 34,650.00 | 34.83 | 52.15 | 179.40 / 551.57 |
| heavy | 1000 | Hetzner RTX PRO 6000 | 75 | 149 | 90,340.82 | 179,477.09 | 107.84 | 196.98 | 179.40 / 551.57 |
| measured power user | 10 | H100 SXM $3.99/h | 1 | 2 | 837.90 | 1,675.80 | 129.29 | 213.08 | 466.44 / 1,434.08 |
| measured power user | 10 | H100 PCIe $2.89/h | 2 | 3 | 1,213.80 | 1,820.70 | 166.88 | 227.57 | 466.44 / 1,434.08 |
| measured power user | 10 | L40S $1.09/h | 3 | ALARM* | 686.70 | ALARM* | 114.17 | ALARM* | 466.44 / 1,434.08 |
| measured power user | 10 | Koyeb H100 $2.50/h | 1 | 2 | 525.00 | 1,050.00 | 98.00 | 150.50 | 466.44 / 1,434.08 |
| measured power user | 10 | Hetzner RTX PRO 6000 | 2 | 4 | 2,409.09 | 4,818.18 | 286.41 | 527.32 | 466.44 / 1,434.08 |
| measured power user | 100 | H100 SXM $3.99/h | 9 | 18 | 7,541.10 | 15,082.20 | 120.91 | 196.32 | 466.44 / 1,434.08 |
| measured power user | 100 | H100 PCIe $2.89/h | 12 | 23 | 7,282.80 | 13,958.70 | 118.33 | 185.09 | 466.44 / 1,434.08 |
| measured power user | 100 | L40S $1.09/h | 24 | ALARM* | 5,493.60 | ALARM* | 100.44 | ALARM* | 466.44 / 1,434.08 |
| measured power user | 100 | Koyeb H100 $2.50/h | 9 | 18 | 4,725.00 | 9,450.00 | 92.75 | 140.00 | 466.44 / 1,434.08 |
| measured power user | 100 | Hetzner RTX PRO 6000 | 20 | 39 | 24,090.89 | 46,977.23 | 286.41 | 515.27 | 466.44 / 1,434.08 |
| measured power user | 1000 | H100 SXM $3.99/h | 86 | 171 | 72,059.40 | 143,280.90 | 117.56 | 188.78 | 466.44 / 1,434.08 |
| measured power user | 1000 | H100 PCIe $2.89/h | 112 | 224 | 67,972.80 | 135,945.60 | 113.48 | 181.45 | 466.44 / 1,434.08 |
| measured power user | 1000 | L40S $1.09/h | 234 | ALARM* | 53,562.60 | ALARM* | 99.07 | ALARM* | 466.44 / 1,434.08 |
| measured power user | 1000 | Koyeb H100 $2.50/h | 86 | 171 | 45,150.00 | 89,775.00 | 90.65 | 135.28 | 466.44 / 1,434.08 |
| measured power user | 1000 | Hetzner RTX PRO 6000 | 193 | 386 | 232,477.04 | 464,954.08 | 277.98 | 510.46 | 466.44 / 1,434.08 |

Egress volume and cost are precision-independent because the client wire profile
and reference admission mix are separately fixed. The table lists every cohort:

| Profile | N | TB/month | Egress at $0/TB | Egress at $5/TB | Egress at $50/TB |
|---|---:|---:|---:|---:|---:|
| light | 10 | 2.800 | 0.00 | 14.00 | 140.01 |
| light | 100 | 28.002 | 0.00 | 140.01 | 1,400.08 |
| light | 1000 | 280.016 | 0.00 | 1,400.08 | 14,000.78 |
| medium | 10 | 11.201 | 0.00 | 56.00 | 560.03 |
| medium | 100 | 112.006 | 0.00 | 560.03 | 5,600.31 |
| medium | 1000 | 1120.062 | 0.00 | 5,600.31 | 56,003.12 |
| heavy | 10 | 35.002 | 0.00 | 175.01 | 1,750.10 |
| heavy | 100 | 350.019 | 0.00 | 1,750.10 | 17,500.97 |
| heavy | 1000 | 3500.195 | 0.00 | 17,500.97 | 175,009.74 |
| measured power user | 10 | 91.005 | 0.00 | 455.03 | 4,550.25 |
| measured power user | 100 | 910.051 | 0.00 | 4,550.25 | 45,502.53 |
| measured power user | 1000 | 9100.507 | 0.00 | 45,502.53 | 455,025.33 |

Complete structured outputs additionally show GPU-seconds/call, recurring cost,
setup upfront, selected egress and first-month cash. Per-second granularity does
not mean the shared warm pool is only billed while computing.

## Validation and limits

**58 tests pass**, including every original named test and all nine byte-identical
goldens. Standard-library compilation and CLI checks pass. Python 3.9 grammar
checks pass; execution was on Linux x86_64 Python 3.14.4. Native macOS/3.9,
actual GPU throughput/placement, cache reloads, queueing/latency SLAs, cold starts,
state conversion and output quality were not tested. The weights/workspace
admission is a lower bound; it does not qualify full-context KV residency.
H100 PCIe performance, Koyeb's unspecified form factor and other explicit
hardware assumptions remain estimates, not freshly verified specifications.

A comparison of 263 normal `paper-base` numeric cells against the preserved run 1
output found no differences at relative/absolute tolerance 1e-12; maximum observed
relative difference was 6.17e-15 from arithmetic regrouping. This does not replace
the exact planted-gap equality or legacy byte checks. The old valid null
finite-grid outcome is now explicit `no crossover on this grid`, not an alarm.

All gate commands below ran as standalone processes, without `tee`. Exit 1
rows are **expected red**, never reported as green: strict modes gate their
visible alarms, and the fallback mutant must fail its named test.

| Exact command | Actual exit | Evidence under `.temp/hybrid-calc-r2-261030/` |
|---|---:|---|
| `python3 -m unittest discover -s calc/tests` | 0 | `unittest-10.stderr` |
| `python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | 0 | `compile-02.stdout` |
| `python3 -m hybridcalc list` | 0 | `list-01.stdout` |
| `python3 -m hybridcalc run paper-base --strict --format json` | 0 | `paper-strict-01.stdout` |
| `python3 -m hybridcalc run glm-tier2 --strict --format json` | 0 | `glm-strict-01.stdout` |
| `python3 -m hybridcalc run service-fp8 --strict --format json` | 0 | `service-fp8-01.stdout` |
| `python3 -m hybridcalc run service-bf16 --format json` | 0 | `service-bf16-01.stdout` |
| `python3 -m hybridcalc run service-bf16 --strict --format json` | 1 | `service-bf16-strict-02.stdout` |
| `python3 -m hybridcalc run service-fp8 --set service.precision=BF16 --format json` | 0 | `service-enum-01.stdout` |
| `python3 -m hybridcalc run paper-base --set prices.rental_gpu_hour=null --format json` | 0 | `rental-null-01.stdout` |
| `python3 -m hybridcalc run paper-base --set prices.rental_gpu_hour=null --strict --format json` | 1 | `rental-null-strict-01.stdout` |
| `python3 -m hybridcalc sources service-fp8 --strict --format json` | 0 | `sources-01.stdout` |
| `python3 -m hybridcalc run paper-base --set hardware.links.wan.bandwidth=0 --format csv` | 0 | `alarm-csv-01.stdout` |
| `python3 -m hybridcalc run service-fp8 --format md` | 0 | `service-markdown-01.stdout` |
| `python3 -m hybridcalc run service-bf16 --format tex` | 0 | `alarm-booktabs-01.stdout` |
| `python3 .temp/hybrid-calc-r2-261030/gap-control.py` | 1 | `gap-control-02.stderr` |

Initial expected-red gap/service tests established the old failures before
implementation. Intermediate tests caught two test-assertion type mistakes and
the old single-call restriction; the final suite is green. File-resolution and
pair-only dependency checks were added before signing. The full log/CLI outputs
are local scratch evidence, not required to run the committed tests.

Validated source/test/config identity (same sorted-file-hash definition as run 1):

`7e715d08373cfc0cfc8f082292202f4063a14f57ff0ddac6b9d14d02e642e6a8`

`MANIFEST.sha256` is regenerated at delivery from every tracked file except
itself, with `./path` records in C-locale byte order; `sha256sum -c MANIFEST.sha256`
and `git diff --cached --check` both exited 0 before signing (139 manifest entries;
local evidence `.temp/hybrid-calc-r2-261030/manifest-02.log`). The signed commit is
local for Ivan's lane to review and publish. No push/PR/landing is claimed.

The brief has no attack-surface table or external landing property suite; that
remains an explicit brief gap. No prior reviewer test name was dropped. The
review is local self-review of the authorized calculation/documentation scope;
independent acceptance remains in Ivan's lane. Unresolved measurement/platform
questions are listed in `UNRESOLVED_QUESTIONS.md`; the BF16 L40S constraint is
reported as an alarm rather than hidden by an unapproved placement assumption.

---

# Historical run 1 report (signed aaec23c3; retained as prior evidence)

The following section describes run 1's source identity, test count and manifest
at that commit. The run 2 results and validation above supersede current behavior.

# Calculation engine delivery — hybrid-calc-r1-261030

Local delivery on `calc-engine`, based on main `7e3d54ee5b4bb7cd0f2f7655cde7282e9c1cf47b`.
No push, fetch, installation, external research lookup or PDF/source-paper change.
The separately requested team summary is sent through a2a after signing.

## Design

`calc/hybridcalc/` is a Python 3.9+ standard-library package. The repository-root
`hybridcalc.py` entry point also supports `python3 -m hybridcalc` without an
installation or environment setup. JSON scenarios compose hardware, models,
prices, workload, sampler and economic data. Every numerical input has a unit
and fact/measured/estimate provenance; independent field contracts reject
incorrect units, missing provenance, nonfinite values, invalid ranges and types.
Numeric overrides are strict, atomic and retain their original provenance.

Canonical calculations return typed-by-column table dictionaries and source
ledgers. Markdown, rectangular CSV, JSON and booktabs render the same rows.
`calc/examples/glm-family.tex` is the compact booktabs example. Legacy rendering
preserves the exact text and additionally exposes its transcript as structured
lines. It does not claim to parse every old prose table into numeric cells.

Historical formulas remain versioned inside one package, with 1,181 numeric
operands externalized to `legacy.json`. Stable compatibility keys retain the
original symbol, line and column. Scalar formula coefficients have unit `1`;
physical/pricing operands have their contextual units. Original source hashes
and source-expression provenance are retained. Original comments are historical
data: an unsupported inherited `[fact]` is conservatively an estimate in the
input ledger. This preserves historical arithmetic and random draw order instead
of quietly substituting modern equations. The nine scripts are now thin engine
wrappers. Fresh isolated module namespaces prevent import-order/global-state
leaks. Closed file reads and an in-memory legacy CSV writer remove incidental
file handle and working-directory output effects without changing transcripts.

## Module map

| Old script | Preserved algorithm module | Canonical responsibilities |
|---|---|---|
| calc2 | `legacy/v2.py` | `performance.py`: prefill, decode and transfer primitives |
| calc3 | `legacy/sessions.py` | `performance.py`, `paper.py`: calibrated decode, sessions and API comparison |
| calc4 | `legacy/fleet.py` | `economics.py`, `glm.py`, `paper.py`: fleet capex/opex, rental, storage and GLM |
| calc5_equilibrium | `legacy/equilibrium.py` | `economics.py`: finite-grid crossover and integer fleet sizing |
| calc6_edge | `legacy/edge.py` | `paper.py`: edge ingestion/decode bounds; full historical phone/energy detail remains versioned |
| calc7_realcalls | `legacy/workload.py` | `workload.py`: seeded real-call aggregate sampler |
| calc8_business | `legacy/business.py` | `economics.py`, `paper.py`: call/session pricing; original subscription/user-class calculations remain versioned |
| calc9_m3max_measured | `legacy/calibration.py` | `performance.py`: measured prefill interpolation, slot fit and normalized decode calibration |
| sensitivity_host_sample | `legacy/sensitivity.py` | Historical host distribution retained as its own data-driven scenario |

`inputs.py` owns units, provenance, data composition, overrides and verified file
reads; `engine.py` owns scenario execution; `formatters.py` owns presentation;
`__main__.py` owns the CLI. See `calc/README.md` for the input format and commands.

## Golden reproduction

All nine outputs are **byte-identical to the newest lane references**. No lane
file was edited. The pre-existing main checkout's calc6 was older: the newest
lane version appends section D (phone chips, Apple's on-device model and radio
versus prefill energy), 14 lines. That import is the only existing `.out` change;
there is no difference against the requested lane calc6 reference. Calc8 and
calc9 outputs and algorithms were imported from the lane before wrapper conversion.

| Reference | Bytes | Result |
|---|---:|---|
| `hybrid_calc2.out` | 15751 | identical |
| `hybrid_calc3.out` | 26282 | identical |
| `hybrid_calc4.out` | 28285 | identical |
| `hybrid_calc5_equilibrium.out` | 33252 | identical |
| `hybrid_calc6_edge.out` | 9799 | identical |
| `hybrid_calc7_realcalls.out` | 4942 | identical |
| `hybrid_calc8_business.out` | 8752 | identical |
| `hybrid_calc9_m3max_measured.out` | 2530 | identical |
| `sensitivity_host_sample.out` | 1155 | identical |

Full output hashes are pinned in `calc/tests/golden.json`; original source hashes
are in `calc/hybridcalc/data/legacy-inventory.json`. Positive goldens exercise all
nine scenarios; the public calc9 wrapper is also tested as a separate process.

## Measurement custody

Both delivered archive SHA-256 values were checked before copying. Every internal
manifest entry was checked; the complete extracted directories were copied
verbatim, including their original manifests and reports:

| Package / destination | Archive SHA-256 |
|---|---|
| `ivmbp-qwen27b-bench-20261030` → `data/measurements/ivmbp-2026-10-30/qwen27b-bench/` | `5c393bdf40052eb582b5c17aac6176a9273a866c4fadde999ee19afa30924439` |
| `ivmbp-session-call-dates-20261030` → `data/measurements/ivmbp-2026-10-30/session-call-dates/` | `164be0dbe0a294ef12bd209207582421164e049a7b8bec9d8d4d2a1e85c1d190` |

`ENGINE-PACKAGES.json` records archive identities and all copied file hashes.
`measurements.json` pins the files actually read by the engine. Package-integrity
and corruption-rejection tests pass. Archives themselves were not duplicated;
all extracted package files were retained. The original full04 `stats.json`
remains unchanged. Full05 call dates are read and displayed as a later snapshot
with partial time coverage; full05 counts never normalize full04 costs.

## GLM family

Default `glm-tier2`: full04-fitted 40,000-call sample; 116 calls per normalized
session; 8 working hours/day; 4-year device amortization net of 35% residual;
B300 owned fleet demand pricing; 1 Gbit/s WAN at 90% goodput; $5/TB egress;
active electricity and amortized DRAM/NVMe session storage included. The own
cluster uses calc4's FP8 TP2 reservation, leaving 114 GB KV memory per B300 GPU.

| Decode configuration | Memory sessions at 200k | Active streams | tok/s per stream at 110k | Sessions/8h per box or pair | Hybrid $/session | API $/session | Own cluster $/session |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mac Studio M5 Ultra 256 GB | 23 | 8 | 11.61 | 41.07 | 0.276 | 0.644 | 0.494 |
| M3 Ultra 256 GB | 23 | 5 | 11.27 | 25.05 | 0.315 | 0.644 | 0.494 |
| 2 x DGX Spark 128 GB | 20 | 1 | 11.17 | 4.98 | 2.019 | 0.644 | 0.494 |
| 2 x Strix Halo 128 GB | 20 | 1 | 10.47 | 4.69 | 1.210 | 0.644 | 0.494 |

These are estimates, not hardware benchmarks. All four fit the complete default
sample. K is chosen to meet 10 tok/s at 110k, capped at eight; concurrency is
reduced per call if a deeper context requires it. The API and own references
use the same calls. Session prices differ from calc4's synthetic 20k→200k
sessions: the denominator here is a 116-call normalization group on the real mix.

Pair decode uses a conservative sequential **pipeline** split, with balanced
weight/state shards. It combines memory capacity without adding memory bandwidth
or claiming unmeasured pipeline overlap. The estimate is:

```
inter_node_seconds_per_step = 2 * (nodes - 1) *
    (latency + K * hidden_width * activation_bytes * 8 / (link_bit_s * goodput))

step_seconds = total_model_batch_bytes / (per_node_bandwidth * efficiency)
             + inter_node_seconds_per_step
per_stream_tok_s = 1 / step_seconds
```

Hidden width 6,144 and bf16 boundary/feedback messages are explicit new
assumptions. Spark uses nominal 200 Gbit/s ConnectX-7, 80% goodput and 50 µs per
message: 0.101229 ms per step at chosen K=1. Strix assumes direct 10GbE with
compatible external NICs/PCIe expansion, 80% goodput and 100 µs per message:
0.224576 ms at K=1. No tensor all-reduce or per-token full-KV copy is assumed.
These settings and the communication formula are in data provenance.

M5 Ultra uses calc4's 80-core $10,799 configuration and 1,228 GB/s working
assumption. M3 Ultra uses new **estimates** of $8,000 and 819.2 GB/s. Spark costs
2 × $6,950; Strix costs 2 × $3,449 plus a new $600 NIC/cabling allowance. Active
whole-device power assumptions are 150 W for each Ultra, 480 W for the Spark
pair and 300 W for the Strix pair. These are explicit assumptions, not the M3
Max package's all-process power-domain measurements. Runtime split support,
NIC compatibility, balanced sharding and message synchronization remain unverified.

## Canonical assumptions and differences from historical scenarios

* Measured prefill interpolates calc9 segment midpoints and extrapolates the tail
  at constant final-point FLOP efficiency; other Apple scaling is estimated.
* Dense decode calibrates normalized 8.44094654 tok/s single-stream and 1.66501544×
  four-stream gain at 32k. It does not mix those with raw v1.1 8.51/14.16 values.
* Modern `reasoning_extra_fraction=0` avoids assuming output/reasoning fields are
  disjoint. Legacy sum behavior is untouched. Setting it to 1 is an explicit
  sensitivity; this does not prove the underlying usage fields are additive.
* The capped sampler's realized means differ from raw aggregate means; the
  actual sample statistics are shown. All 40,000 sampled calls are retained;
  legacy calc7 keeps 39,904 because it drops the final incomplete chunk.
* Modern API billing charges cached prefix, uncached delta and output once.
  Legacy tier/cache-write/previous-output bookkeeping remains byte-identical.
* Default 64 GB Apple clients cannot fit 0.55% of sampled calls even at K=1.
  Their supported-subset results and fit shares are explicit, and API/own
  references are recomputed on that same subset. Unsupported calls are never
  treated as zero-cost successes. Below-floor K=1 fallbacks are marked.
* Fleets size integer server units and pooled client boxes for declared calls/day;
  they do not assume a slow single client serves 2,500 calls/day. Crossovers are
  finite-grid results. Client prices/power and hybrid DRAM/NVMe costs are visible.

## Validation

Observed environment: Linux x86_64, Python 3.14.4. Every command below ran as its
own process with real exit status retained, without a pipeline through `tee`.
All 29 tests passed; compile validation passed. Test comments state their claims.

| Exact command | Exit | Evidence |
|---|---:|---|
| `/usr/bin/python3 -m unittest discover -s calc/tests` | 0 | `.temp/hybrid-calc-r1-261030/unittest-05.stderr.log` |
| `/usr/bin/python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py` | 0 | `.temp/hybrid-calc-r1-261030/compile-02.log` |
| `/usr/bin/python3 -m hybridcalc list` | 0 | `.temp/hybrid-calc-r1-261030/list-02.log` |
| `/usr/bin/python3 -m hybridcalc run paper-base --format json` | 0 | `.temp/hybrid-calc-r1-261030/paper-base-04.log` |
| `/usr/bin/python3 -m hybridcalc run glm-tier2 --format json` | 0 | `.temp/hybrid-calc-r1-261030/glm-tier2-04.log` |
| `/usr/bin/python3 -m hybridcalc sources paper-base --format json` | 0 | `.temp/hybrid-calc-r1-261030/sources-02.log` |
| `/usr/bin/python3 -m hybridcalc run paper-base --set hardware.links.wan.bandwidth=2500000000 prices.egress=0 --format csv` | 0 | `.temp/hybrid-calc-r1-261030/override-02.log` |
| `/usr/bin/python3 -m hybridcalc run glm-tier2 --format tex` | 0 | `.temp/hybrid-calc-r1-261030/booktabs-02.log` |
| `/usr/bin/python3 /home/agent/Werkstatt/hybrid-calc/paper/.temp/hybrid-calc-r1-261030/planted-control.py` | 1 | `.temp/hybrid-calc-r1-261030/planted-control-02.stderr.log` |

The planted-control command is **expected red**, not a passing test command:
it changes the M3 Max peak from 14 to 28 TFLOP/s in an isolated run and executes
the actual named golden test, which exits 1 with the intended byte mismatch.
The regular suite also includes the corresponding positive/negative control.
Earlier validation found a strict floating-point anchor equality discrepancy
(27.699999999999996 vs 27.7); returning the exact measured anchor at a curve knot
corrected it. An initial migration smoke failed on an indented absolute dependency import;
converting that import to package-relative fixed it. Initial import also stopped
on the main/lane calc6 equality assertion; inspection established the newer
14-line section D and selected the requested lane reference. No golden
differences or validation failures remain.

| Mutant | What the gate is narrowed to | Named failing test | Survival bound |
|---|---|---|---|
| M3 Max `PEAK16` 14→28 TFLOP/s | Sensitivity of calc9's printed MFU to this one hardware input | `test_golden.GoldenTests.test_hybrid_calc9_m3max_measured` | Killed; no survivor. This control does not prove every possible input mutation is detected. |

No broader mutation campaign was run. Known physical invariants and rejection
paths are exercised independently of the goldens. Source/test/configuration
identity for the validated calculation files (SHA-256 of sorted per-file hash
records, excluding docs and measurement files whose identities are separately
pinned):

`e09b7dec0504f481d81e2048eb3072231d28f69b5489e52c61f142acc5cfadc3`

Validation logs and full CLI outputs are local `.temp/hybrid-calc-r1-261030/`
artifacts. The commands, status codes, normalized results and references needed
to reproduce them are persisted in this report and tests; scratch logs are not
part of the signed repository delivery. `MANIFEST.sha256` is rebuilt from every
tracked regular file except itself, using `./path` names in C-locale order, then
checked with `sha256sum -c MANIFEST.sha256` (observed exit 0 for 129 files).
`git diff --cached --check` also exited 0; no forbidden paths changed.

## Limits and review scope

No native macOS or Python 3.9 execution was available; Python 3.9 grammar parsing
passed and runtime APIs are standard-library 3.9-compatible. The booktabs fragment
was generated and escaping tested, but no TeX/PDF build was run because the change
does not touch the paper/build system and installs/network are prohibited.
Prices and model claims are dated inputs, with no live revalidation. No real
multi-node GLM inference, transport/serialization benchmark, output-quality test,
thermal or wall-power measurement was performed. Residency and decode throughput
remain model estimates, not runtime scheduler simulations.

No surface table, attack-surface catalogue or externally specified landing-gate
property suite was provided in the brief: this is a brief gap. No reviewer tests
were removed or renamed; there were no pre-existing calculation tests. The
review is local self-review for this reversible calculation/documentation delta;
independent acceptance remains with Ivan's delivery lane. There is no board run
or active board configuration in this workbench, so progress uses the existing
`.temp/tasks.md` convention. No out-of-contract code rows were silently waived.

All requested calculation scope is included. Excluded by the user's limits:
`paper/`, `.github/`, `.scripts/`, `tools/`, `data/research/`, remote fetch/push,
PR/review/landing operations and online research. The final a2a summary is the
explicitly requested messaging exception. See `UNRESOLVED_QUESTIONS.md` for the
finite follow-up measurement questions. Signed commits are handed to Ivan's
lane for review and publication; no remote delivery is claimed here.


## Run 10: small-team own-server grid

Run `hybrid-calc-r10-261031` starts from signed
`e9db8129887126ca6a5d27066dd4f4519d223c2d` on `calc-engine`. The only engine
input change adds 20, in order, to `paper_tables.teams` (5, 10, 20, 50, 500,
5000), with estimate provenance: "owner request 2026-10-31, small-team own-server
case". All eight run-9 export commands above were rerun, each exit **0**;
all 42 published CSVs and eight audit manifests are current. No formula or
hosting policy changed. Manifest/schema/source changes reflect the new grid,
record counts, label mappings and generator hash.

Closed perimeter means all calls use the open model on owned infrastructure.
Costs below are USD/person-month, rounded to four decimals; exact values are in
the CSVs. One unit means one server of the named configuration (a `2x` unit
contains two RTX PRO 6000 GPUs). All B300 rows below have **one 8-GPU node**.
B300 is **ineligible** (`eligible=0`) for both team sizes under the existing
minimum-50-person policy; its numeric price is a comparison, not the selected
option or an alarm. Default and conservative all-server values coincide because
this route has no client hosting policy dependency.

| Policy | Traffic | 5 people: selected option; units; person_month | 20 people: selected option; units; person_month | B300 person_month: 5 / 20 | Alarms (5 / 20) |
| --- | --- | --- | --- | --- | --- |
| default | light | 1x RTX PRO 6000 Server; 1; $144.8115 | 2x RTX PRO 6000 Server; 1; $63.2391 | $3370.1617 / $842.5404 | none / none |
| default | medium | 2x RTX PRO 6000 Server; 1; $252.9563 | 2x RTX PRO 6000 Server; 3; $189.7172 | $3370.1617 / $842.5404 | none / none |
| default | heavy | 1x RTX PRO 6000 Server; 5; $724.0575 | 2x RTX PRO 6000 Server; 9; $569.1517 | $3370.1617 / $842.5404 | none / none |
| conservative | light | 1x RTX PRO 6000 Server; 1; $144.8115 | 2x RTX PRO 6000 Server; 1; $63.2391 | $3370.1617 / $842.5404 | none / none |
| conservative | medium | 2x RTX PRO 6000 Server; 1; $252.9563 | 2x RTX PRO 6000 Server; 3; $189.7172 | $3370.1617 / $842.5404 | none / none |
| conservative | heavy | 1x RTX PRO 6000 Server; 5; $724.0575 | 2x RTX PRO 6000 Server; 9; $569.1517 | $3370.1617 / $842.5404 | none / none |

**Byte-identity proof.** [ENGINE-DIFF-R10-261031.csv](ENGINE-DIFF-R10-261031.csv)
lists removed/changed/added counts separately for every one of the 42 CSVs:
**0 removed, 0 changed, 694 added**, all team 20. Existing header/record bytes,
including quoting, numeric spelling and line endings, and relative record order
are preserved. Sixteen files gain records: each policy adds 36 person-cost rows
(12 per share), five GLM long-session rows, 153 aggregate perimeter rows and
51 rows in each of its three profile subsets: 347/policy. The other 26 CSVs,
including remote rent/buy, are byte-identical in full. Subset rows are intentionally
counted again in the aggregate table. [ENGINE-CHANGES-R10-261031.csv](ENGINE-CHANGES-R10-261031.csv)
contains added rows only, with source file, identity key and the exact CSV record
in a quoted cell; the per-file count table includes unaffected files too.

`python3 calc/tests/r10_controls.py --diff calc/ENGINE-DIFF-R10-261031.csv --added calc/ENGINE-CHANGES-R10-261031.csv`
reads the pinned baseline from local git history, compares stable record keys
and exact bytes, rejects old-row deletion/change/reordering and additions outside
team 20, and exits **0**. The baseline signature was verified (exit **0**).
All eight manifests' payload hashes match (exit **0**).

| Negative control | Gate narrowed to | Named test that detects it | Observed result / surviving bound |
| --- | --- | --- | --- |
| Change actual team-5 all-server `person_month` to `0.123456789` in an isolated export copy | Old-record bytes, independently of inserted team-20 rows | `Run10Tests.test_planted_team5_change_fails_byte_identity` | The same CLI audit exits **1** as expected: `perimeter_cost_light.csv`, changed=1, removed=0, added=51. No survivor. |

The unchanged published file passes the same gate first. Additional negative
fixtures cover numeric reformatting, deletion, reordering and a team-30 insertion.
Existing tests keep their names; changed person/GLM counts and optional TeX smoke
counts carry explicit claims beside the checks. No brief surface table was
supplied. No engine behavior outside the team grid is in scope; previous reviewer
tests remain present. No rework outside a named implementation module applies.

Validation logs and exact command/exit records live under
`.temp/hybrid-calc-r10-261031/`: `export-results.json`, `csv-byte-audit-01.log`,
`planted-team5-01.log`, `manifest-check-01.log`, `legacy-results.json`,
`unittest-full-01.log` and `full-suite-result.json`. Source/data/Python-test
identity is frozen in `validated-source-identity.json` (aggregate SHA256
`8981f272895d7f8f4bdf13bdb04572b055cdaa1c27b6b10abb28cfdf9c4d918d`).

| Command | Exit | Evidence |
| --- | --- | --- |
| `TMPDIR="$PWD/.temp/hybrid-calc-r10-261031/tmp" python3 -m unittest discover -s calc/tests` | **0** | 230 tests, 306.861s; `unittest-full-01.log` |
| `python3 -m unittest discover -s calc/tests -p test_golden.py` | **0** | 11 tests, including all nine pinned legacy goldens and the legacy negative control; `legacy-golden-01.log` |
| `python3 calc/<stem>.py` for all nine stems in `calc/tests/golden.json` | **0 each** | Actual wrapper stdout matches pinned `.out` bytes/hash for all nine; `legacy-results.json` |
| `python3 calc/tests/r10_controls.py --diff calc/ENGINE-DIFF-R10-261031.csv --added calc/ENGINE-CHANGES-R10-261031.csv` | **0** | 42 files, 694 additions, zero deletions/changes; `csv-byte-audit-01.log` |
| `python3 calc/tests/r10_controls.py --directory .temp/hybrid-calc-r10-261031/planted-team5 --diff .temp/hybrid-calc-r10-261031/planted-team5-diff.csv` | **1 expected** | Exactly the planted old team-5 cost is detected; `planted-team5-01.log` |

The full suite retains all 226 prior tests and adds four R10 tests. Python also
validated all 66 row-count assertions in the optional TeX fixtures (exit **0**,
`smoke-counts-python-01.log`); TeX itself was not executed. The existing legacy
suite includes the Python 3.9 grammar check; no build was run.

No build, download, network, push or hosted review was attempted, as requested.
The message addressed to `agents1_hybrid_orch` in `#hybrid`, topic `prototype-go`,
is prepared in `.temp/hybrid-calc-r10-261031/prototype-go-summary.md`; it was
**not sent**, because sending it would violate this run's explicit no-network
limit. Delivery is local signed commits on `calc-engine`, ready for review.

## Run 11: output includes reasoning

Run `hybrid-calc-r11-261101` starts from signed `1e8f897c4f82092c632507b520515cefa7eecab5` on `calc-engine`. This section supersedes the generation accounting and numerical base cases in the historical run sections below. Delivery remains local signed commits, ready for review; no push or hosted review is claimed.

**Accounting.** Generated tokens per call are `output_per_call` alone: **511.9**, used consistently for client decode, server-only decode, output billing, generated-token shadow and timing. Reasoning is an informational subset. The owner supplied Codex evidence for 126/126 `token_count` events (`total=input+output`, reasoning≤output; example output 94/reasoning 15), and Claude Code evidence for 4,577/4,577 usage records (`thinking_tokens≤output`). Those clients account for 93% of 1,528,194 calls. `tools/agent_session_stats.py:81–84` stores both fields separately and its line 658 note says reasoning is not added to output; that code was inspected locally. Private logs were not re-audited in this run. **Muse follows the same convention, unverified.** All current nonlegacy base scenarios select fraction 0. The explicitly historical `crossover-bridge` and legacy byte reproductions retain their old sum.

The pinned full04 pooled means are output 511.9 and reasoning 207.7 (the request rounded the latter to about 207.5), so the exact old fitted upper bound is 719.6. No raw measurements were rewritten. The sampler still draws the same output distribution, fits the same global output mean and caps, and preserves every depth/new-token/tool draw and joint depth/new-token constraint. The field used by all downstream calculations is now that output alone.

**Sensitivity.** The old “without reasoning” case is now the base. `reasoning_on_top_sensitivity.csv` and `reasoning_on_top_sensitivity_conservative.csv` replace the two `output_only_sensitivity` filenames. The new `accounting_case` column labels `base_output` (fraction 0) and `reasoning_on_top_upper_bound` (fraction 1). All pre-existing sensitivity numeric cells are unchanged. This recovers the old 637→883 M5 Max 64 statement as approximately 883 base versus 637 upper-bound calls/day; API reductions relative to the old sum are 5.05% median and 16.62% cheapest. “Conservative” in filenames means the independent hosting policy, not summed output accounting. To recover any old table, add `--set workload.reasoning_extra_fraction=1` to its export command.

**Coverage of quoted claims.** [ENGINE-QUOTES-R11-261101.csv](ENGINE-QUOTES-R11-261101.csv) contains exact old/new costs for every client/share/basis, both API spill references, savings and ratio ranges, local/hybrid call capacity, both definitions of served share, closed-perimeter ranges, 5/20-person servers, cash and residual-adjusted payback, offload examples and output-independent bounds. [ENGINE-CHANGES-R11-261101.csv](ENGINE-CHANGES-R11-261101.csv) records **every numeric cell including unchanged and nan alarms**, plus changed text, across all 42 CSVs, with zero-based row index, old/new values and policy. [ENGINE-DIFF-R11-261101.csv](ENGINE-DIFF-R11-261101.csv) gives per-file coverage counts and baseline/current SHA256. The baseline is read directly from immutable local git history.

The checked-out `paper/hybrid-inference.ru.tex` is a 1,250-byte placeholder with no abstract/economics/conclusion body, and **`paper/data/` does not exist**. There are no such files to re-export or absent sentences to edit. The full replacement values below and in the two ledgers are the handoff for the paper-owning lane; no narrative or paper/data update is claimed. No build, download, network or push was run.

### Per-person economics: run10 → run11

USD/person-month, economics WAN 1 Gbit/s, 8 h/day, 21 days/month. Hybrid shared-service amounts are flat over team size; table uses team 50. Both overflow routes are included. Acquisition bases are already-owned client or bought premium; Studios are additional devices. Common closed-model spending is excluded as before. API costs cover the same offered open demand. All figures below are rounded; ledgers retain exact strings.

**default, s20.** Full median API: 107.07 → 101.67; full cheapest API: 16.91 → 14.10.

| Client | Owned, median spill | Owned, cheapest spill | Bought, median spill | Bought, cheapest spill |
| --- | --- | --- | --- | --- |
| M3 Max 128 | 38.39 → 27.26 | 28.09 → 27.26 | 85.80 → 74.67 | 75.50 → 74.67 |
| M4 Max 128 est. | 26.51 → 25.82 | 26.51 → 25.82 | 73.90 → 73.22 | 73.90 → 73.22 |
| M5 Max 64 | 25.86 → 25.18 | 24.75 → 24.07 | 61.06 → 60.38 | 59.96 → 59.28 |
| M5 Max 128 | 24.78 → 24.10 | 24.78 → 24.10 | 81.65 → 80.97 | 81.65 → 80.97 |
| M5 Ultra 96 | 23.25 → 22.60 | 23.25 → 22.60 | 97.71 → 97.07 | 97.71 → 97.07 |
| M5 Ultra 256 | 22.64 → 21.99 | 22.64 → 21.99 | 168.87 → 168.23 | 168.87 → 168.23 |

**default, s50.** Full median API: 267.68 → 254.17; full cheapest API: 42.27 → 35.24.

| Client | Owned, median spill | Owned, cheapest spill | Bought, median spill | Bought, cheapest spill |
| --- | --- | --- | --- | --- |
| M3 Max 128 | 198.99 → 159.68 | 53.45 → 48.65 | 246.40 → 207.09 | 100.86 → 96.06 |
| M4 Max 128 est. | 168.45 → 119.66 | 51.36 → 46.70 | 215.85 → 167.05 | 98.76 → 94.10 |
| M5 Max 64 | 160.64 → 109.54 | 48.94 → 43.60 | 195.84 → 144.75 | 84.14 → 78.81 |
| M5 Max 128 | 152.50 → 98.63 | 48.66 → 43.40 | 209.38 → 155.50 | 105.53 → 100.28 |
| M5 Ultra 96 | 39.92 → 38.31 | 39.92 → 38.31 | 114.39 → 112.78 | 114.39 → 112.78 |
| M5 Ultra 256 | 38.40 → 36.80 | 38.40 → 36.80 | 184.63 → 183.04 | 184.63 → 183.04 |

**conservative, s20.** Full median API: 107.07 → 101.67; full cheapest API: 16.91 → 14.10.

| Client | Owned, median spill | Owned, cheapest spill | Bought, median spill | Bought, cheapest spill |
| --- | --- | --- | --- | --- |
| M3 Max 128 | 47.23 → 36.30 | 36.95 → 36.30 | 94.64 → 83.70 | 84.36 → 83.70 |
| M4 Max 128 est. | 36.12 → 35.39 | 36.12 → 35.39 | 83.52 → 82.78 | 83.52 → 82.78 |
| M5 Max 64 | 36.00 → 35.27 | 34.89 → 34.16 | 71.21 → 70.47 | 70.10 → 69.37 |
| M5 Max 128 | 35.04 → 34.30 | 35.04 → 34.30 | 91.91 → 91.18 | 91.91 → 91.18 |
| M5 Ultra 96 | 34.13 → 33.40 | 34.13 → 33.40 | 108.60 → 107.86 | 108.60 → 107.86 |
| M5 Ultra 256 | 33.72 → 32.98 | 33.72 → 32.98 | 179.96 → 179.22 | 179.96 → 179.22 |

**conservative, s50.** Full median API: 267.68 → 254.17; full cheapest API: 42.27 → 35.24.

| Client | Owned, median spill | Owned, cheapest spill | Bought, median spill | Bought, cheapest spill |
| --- | --- | --- | --- | --- |
| M3 Max 128 | 207.84 → 169.10 | 62.31 → 58.09 | 255.25 → 216.51 | 109.72 → 105.50 |
| M4 Max 128 est. | 178.50 → 130.70 | 61.44 → 57.79 | 225.89 → 178.09 | 108.84 → 105.19 |
| M5 Max 64 | 171.54 → 121.78 | 59.89 → 55.91 | 206.75 → 156.99 | 95.10 → 91.12 |
| M5 Max 128 | 163.74 → 111.30 | 59.95 → 56.14 | 220.62 → 168.18 | 116.82 → 113.02 |
| M5 Ultra 96 | 56.20 → 54.39 | 56.20 → 54.39 | 130.67 → 128.85 | 130.67 → 128.85 |
| M5 Ultra 256 | 55.17 → 53.36 | 55.17 → 53.36 | 201.41 → 199.59 | 201.41 → 199.59 |

### Ranges against median and cheapest API

Savings percent is `100*(1-hybrid/API)`; negative means hybrid costs more. The API/hybrid ratio gives the same comparison as a factor. Each range spans all six clients under the stated acquisition basis.

| Policy / share / basis | Median saving % range | Cheapest saving % range | Median API/hybrid range | Cheapest API/hybrid range |
| --- | --- | --- | --- | --- |
| default / s20 / Mac already owned | 64.15–78.86 → 73.18–78.37 | -66.12–-33.88 → -93.39–-56.02 | 2.79–4.73 → 3.73–4.62 | 0.60–0.75 → 0.52–0.64 |
| default / s20 / Mac premium bought | -57.72–42.97 → -65.47–40.61 | -898.82–-254.62 → -1093.39–-320.51 | 0.63–1.75 → 0.60–1.68 | 0.10–0.28 → 0.08–0.24 |
| default / s50 / Mac already owned | 25.66–85.66 → 37.17–85.52 | -26.45–9.16 → -38.04–-4.42 | 1.35–6.97 → 1.59–6.91 | 0.79–1.10 → 0.72–0.96 |
| default / s50 / Mac premium bought | 7.95–57.27 → 18.52–55.63 | -336.81–-99.08 → -419.37–-123.62 | 1.09–2.34 → 1.23–2.25 | 0.23–0.50 → 0.19–0.45 |
| conservative / s20 / Mac already owned | 55.89–68.51 → 64.30–67.56 | -118.55–-99.44 → -157.47–-133.98 | 2.27–3.18 → 2.80–3.08 | 0.46–0.50 → 0.39–0.43 |
| conservative / s20 / Mac premium bought | -68.07–33.49 → -76.28–30.68 | -964.38–-314.64 → -1171.36–-392.08 | 0.59–1.50 → 0.57–1.44 | 0.09–0.24 → 0.08–0.20 |
| conservative / s50 / Mac already owned | 22.36–79.39 → 33.47–79.01 | -47.42–-30.53 → -64.83–-51.40 | 1.29–4.85 → 1.50–4.76 | 0.68–0.77 → 0.61–0.66 |
| conservative / s50 / Mac premium bought | 4.64–51.18 → 14.82–49.30 | -376.50–-125.00 → -466.35–-158.56 | 1.05–2.05 → 1.17–1.97 | 0.21–0.44 → 0.18–0.39 |

### Client capacity and served share

At 1 Gbit/s, supported mix, 8 h/day. Calls/day equals published normalized sessions/day times 116; these are synthetic normalization groups, not calendar session observations. Share at s50 uses served/requested 1250 open calls. The second share uses the complete 2500-call workday. Studios may exceed demand capacity, so served demand is capped.

| Policy | Client | Local calls/day | Hybrid calls/day | Served open demand at s50 % | Served whole workday % |
| --- | --- | --- | --- | --- | --- |
| default | M3 Max 128 | 313.3 → 391.1 | 442.9 → 616.0 | 35.43 → 49.28 | 17.72 → 24.64 |
| default | M4 Max 128 est. | 473.8 → 607.6 | 600.7 → 833.4 | 48.05 → 66.68 | 24.03 → 33.34 |
| default | M5 Max 64 | 572.6 → 763.6 | 636.9 → 882.6 | 50.96 → 70.61 | 25.48 → 35.31 |
| default | M5 Max 128 | 598.8 → 795.7 | 674.1 → 934.7 | 53.93 → 74.77 | 26.97 → 37.39 |
| default | M5 Ultra 96 | 1174.8 → 1556.1 | 1297.6 → 1779.8 | 100.00 → 100.00 | 50.00 → 50.00 |
| default | M5 Ultra 256 | 1224.9 → 1638.7 | 1320.0 → 1814.0 | 100.00 → 100.00 | 50.00 → 50.00 |
| default | Strix Halo 128 | 261.2 → 352.5 | 285.7 → 398.5 | not in economics client set | not in economics client set |
| default | DGX Spark 128 | 295.9 → 408.1 | 304.6 → 425.0 | not in economics client set | not in economics client set |
| conservative | M3 Max 128 | 313.3 → 391.1 | 443.0 → 616.2 | 35.44 → 49.29 | 17.72 → 24.65 |
| conservative | M4 Max 128 est. | 473.8 → 607.6 | 600.9 → 833.7 | 48.07 → 66.70 | 24.04 → 33.35 |
| conservative | M5 Max 64 | 572.6 → 763.6 | 637.3 → 883.1 | 50.98 → 70.64 | 25.49 → 35.32 |
| conservative | M5 Max 128 | 598.8 → 795.7 | 674.4 → 935.0 | 53.95 → 74.80 | 26.98 → 37.40 |
| conservative | M5 Ultra 96 | 1174.8 → 1556.1 | 1298.8 → 1781.4 | 100.00 → 100.00 | 50.00 → 50.00 |
| conservative | M5 Ultra 256 | 1224.9 → 1638.7 | 1321.2 → 1815.7 | 100.00 → 100.00 | 50.00 → 50.00 |
| conservative | Strix Halo 128 | 261.2 → 352.5 | 285.7 → 398.6 | not in economics client set | not in economics client set |
| conservative | DGX Spark 128 | 295.9 → 408.1 | 304.7 → 425.1 | not in economics client set | not in economics client set |

### Closed perimeter and own servers

All calls use owned infrastructure/open models, with no API fallback. The quote ledger lists min/max over eligible complete-service rows for every profile, team 5/10/20/50/500/5000, route and acquisition basis. Rows with any unserved calls or a fit/policy alarm are excluded from those ranges. The following whole-grid ranges span eligible complete-service hybrid rows over all six team sizes and six clients, separately by basis. Ranges are comparisons of heterogeneous team sizes; use the coordinate-specific CSV rows for a particular team.

| Policy | Profile | Basis | Closed hybrid USD/person-month range, run10 → run11 |
| --- | --- | --- | --- |
| default | light | Mac already owned | 18.78–349.11 → 18.77–349.10 |
| default | light | Mac premium bought | 62.11–529.09 → 62.11–529.08 |
| default | medium | Mac already owned | 28.94–349.11 → 28.89–349.10 |
| default | medium | Mac premium bought | 99.19–529.09 → 72.22–529.08 |
| default | heavy | Mac already owned | 241.26–686.12 → 133.41–518.00 |
| default | heavy | Mac premium bought | 336.28–744.47 → 228.43–588.00 |
| conservative | light | Mac already owned | 26.03–356.43 → 26.01–356.42 |
| conservative | light | Mac premium bought | 69.36–536.42 → 69.35–536.40 |
| conservative | medium | Mac already owned | 43.01–356.43 → 42.86–356.42 |
| conservative | medium | Mac premium bought | 109.80–536.42 → 86.20–536.40 |
| conservative | heavy | Mac already owned | 262.07–693.45 → 157.58–525.32 |
| conservative | heavy | Mac premium bought | 357.09–751.80 → 252.60–595.32 |

Selected own-server rows for 5 and 20 people are identical under both hosting policies, because the all-server route has no client hosting dependency. One 2× unit contains two GPUs. B300 remains one 8-GPU node, ineligible at these team sizes; $3370.16171/person-month at 5 and $842.5404275 at 20 are unchanged.

| Profile | People | Selected server, run10 → run11 | Units | USD/person-month |
| --- | --- | --- | --- | --- |
| light | 5 | 1x RTX PRO 6000 Server; own perimeter rack → 1x RTX PRO 6000 Server; own perimeter rack | 1 → 1 | 144.8115 → 144.8115 |
| light | 20 | 2x RTX PRO 6000 Server; own perimeter rack → 1x RTX PRO 6000 Server; own perimeter rack | 1 → 1 | 63.2391 → 36.2029 |
| medium | 5 | 2x RTX PRO 6000 Server; own perimeter rack → 1x RTX PRO 6000 Server; own perimeter rack | 1 → 1 | 252.9563 → 144.8115 |
| medium | 20 | 2x RTX PRO 6000 Server; own perimeter rack → 1x RTX PRO 6000 Server; own perimeter rack | 3 → 4 | 189.7172 → 144.8115 |
| heavy | 5 | 1x RTX PRO 6000 Server; own perimeter rack → 2x RTX PRO 6000 Server; own perimeter rack | 5 → 2 | 724.0575 → 505.9127 |
| heavy | 20 | 2x RTX PRO 6000 Server; own perimeter rack → 2x RTX PRO 6000 Server; own perimeter rack | 9 → 7 | 569.1517 → 442.6736 |

### Payback months, including overflow

Cash payback uses incremental acquisition cash `max(0,purchase_price-premium_credit)/(full_API-owned_client_hybrid)`. The denominator includes overflow to the same named API, energy, front, server and hosting costs, and excludes device amortization. A nonpositive saving is **no payback**. Bought laptop capital subtracts the declared ordinary-laptop credit; Studio capital is its full purchase cost. For an alternative four-year resale-adjusted capital convention, the exact quote ledger also lists payback multiplied by `(1-client_residual)`; that quantity is not cash payback. The placeholder paper does not establish which convention its missing prose used, so both are explicit.

| Policy | Share | Client | Overflow to median API | Overflow to cheapest API |
| --- | --- | --- | --- | --- |
| default | .2 | M3 Max 128 | 50.97 → 47.05 | no payback → no payback |
| default | .2 | M4 Max 128 est. | 43.44 → 46.15 | no payback → no payback |
| default | .2 | M5 Max 64 | 32.01 → 33.99 | no payback → no payback |
| default | .2 | M5 Max 128 | 51.04 → 54.15 | no payback → no payback |
| default | .2 | M5 Ultra 96 | 65.60 → 69.55 | no payback → no payback |
| default | .2 | M5 Ultra 256 | 127.90 → 135.54 | no payback → no payback |
| default | .5 | M3 Max 128 | 50.97 → 37.05 | no payback → no payback |
| default | .5 | M4 Max 128 est. | 35.27 → 26.02 | no payback → no payback |
| default | .5 | M5 Max 64 | 24.29 → 17.98 | no payback → no payback |
| default | .5 | M5 Max 128 | 36.47 → 27.00 | no payback → no payback |
| default | .5 | M5 Ultra 96 | 24.14 → 25.48 | 2347.11 → no payback |
| default | .5 | M5 Ultra 256 | 47.10 → 49.68 | 2788.63 → no payback |
| conservative | .2 | M3 Max 128 | 58.51 → 53.56 | no payback → no payback |
| conservative | .2 | M4 Max 128 est. | 49.33 → 52.81 | no payback → no payback |
| conservative | .2 | M5 Max 64 | 36.58 → 39.16 | no payback → no payback |
| conservative | .2 | M5 Max 128 | 58.30 → 62.35 | no payback → no payback |
| conservative | .2 | M5 Ultra 96 | 75.39 → 80.55 | no payback → no payback |
| conservative | .2 | M5 Ultra 256 | 147.22 → 157.23 | no payback → no payback |
| conservative | .5 | M3 Max 128 | 58.51 → 41.16 | no payback → no payback |
| conservative | .5 | M4 Max 128 est. | 39.25 → 28.35 | no payback → no payback |
| conservative | .5 | M5 Max 64 | 27.04 → 19.64 | no payback → no payback |
| conservative | .5 | M5 Max 128 | 40.41 → 29.40 | no payback → no payback |
| conservative | .5 | M5 Ultra 96 | 26.00 → 27.53 | no payback → no payback |
| conservative | .5 | M5 Ultra 256 | 50.82 → 53.78 | no payback → no payback |

### Offload-bound example and unchanged examples

For the sampled M3 reference with f32 state, the 1 Gbit/s economics-link offload opportunity fraction and saving are below; the complete 0.1/0.3/1/2.5/10 Gbit/s, f32/bf16 grid is in the quote ledger. This includes output-dependent shadow/catch-up and storage effects. The arithmetic-intensity bound `flop_per_byte` itself compares input work and delta bytes and is output-independent. Its Qwen 27B/M3/110k/1k/f32 link examples are retained exactly for both policies, as are explicitly requested transcript 3000-token summary, turn/ingest fixed-output examples, raw decode bounds and architecture/fit geometry; the full cell ledger records unchanged values as well.

| Policy | Metric, f32 / 1Gbit/s | Run10 → run11 |
| --- | --- | --- |
| default | share_calls | 0.605478 → 0.608109 |
| default | saved_seconds_call | 26.455181 → 26.473487 |
| default | saved_seconds_offloaded | 43.693040 → 43.534082 |
| conservative | share_calls | 0.613773 → 0.613773 |
| conservative | saved_seconds_call | 26.519565 → 26.519565 |
| conservative | saved_seconds_offloaded | 43.207443 → 43.207443 |

### Validation and delivery limits

Final full suite: **234 tests, exit 0, 523.414s**, retaining all 230 prior cases and adding four R11 cases. Frozen source/data/Python-test identity: `603c3e3ba4ac85c485b3c376fdff35250f83ad0ea64deb7106c76d4fa1236f30`. All 221 directly declared prior test method names are retained (plus inherited cases). The nine legacy golden transcripts remain byte-identical under the retained golden tests. Source identity was checked unchanged after validation.

| Command | Actual exit | Evidence |
| --- | ---: | --- |
| `TMPDIR="$PWD/.temp/hybrid-calc-r11-261101/tmp" python3 -m unittest discover -s calc/tests` | **0** | `unittest-full-02.log`, `full-suite-result.json` |
| Eight default/conservative export commands listed earlier in this report | **0 each** | `export-results.json`, `export-*-01.log` |
| The same eight exports with `--set workload.reasoning_extra_fraction=1` into the task temp upper-bound directory | **0 each** | `upper-results.json`; every one of 195,021 old run10 cells recovered exactly |
| `python3 calc/tests/r11_audit.py --upper .temp/hybrid-calc-r11-261101/upper-bound` | **0** | `publication-audit-final-01.log`; 42 files, 140,350 numeric cells, 38,754 changed cells, 1,883 quote records; eight generator/payload manifest sets verified |
| `python3 -m unittest discover -s calc/tests -p test_run11.py` | **0** | `unittest-r11-02.log`; four tests |
| `python3 calc/tests/r11_controls.py output_sum` | **1 expected red** | `planted-output-sum-01.log`; named assertion `719.6 != 511.9`, no setup error |
| `python3 -m hybridcalc export paper-tables-r8 --strict --output .temp/hybrid-calc-r11-261101/strict` | **1 expected alarm gate** | `strict-result.json`, `export-strict-01.log`; payload bytes exactly equal ordinary export; inherited physical/context alarms remain |
| `python3 calc/tests/r10_controls.py` | **0** | `r10-history-audit-01.log`; immutable signed run10 vs R9 byte-preservation history |
| Python `ast.parse(..., feature_version=(3,9))` over frozen source/tests | **0** | `python-grammar-final-01.log`; syntax validation only, no build |
| `git verify-commit 1e8f897c4f82092c632507b520515cefa7eecab5` | **0** | `baseline-signature-01.log` |

The first new focused run exited 1 because its API tariff fixture used `input/cached` instead of this path's `cache_write/cache_read`; that fixture was corrected. The first R8 focused run exited 1 on the historical two-node witness under the newly output-only default; its historical fraction1 is now explicit. The first 234-test full run exited **1** with exactly two obsolete expectations: historical API overflow 348.435693 versus output-only53.901182 calls/day, and old compute-only people/GPU60/24/12/271/108/54 versus new69/27/13/308/123/61. The overflow history now selects fraction1; the current headline pins the new output-only values. The final full run above supersedes those red candidates. Exact commands and real exit codes are retained in `.temp/hybrid-calc-r11-261101/validation.json`.

| Mutant | Gate narrowed to | Named failing test | Surviving bound |
| --- | --- | --- | --- |
| Plant actual base sampled output as output plus reasoning, leaving declared base configuration unchanged | Base generated mean consumed by decode/billing/timing must equal independently measured output, not the summed counters | `test_run11.Run11Tests.test_base_generated_tokens_are_output` | Killed with intended AssertionError; no survivor. This control does not claim exhaustive detection of every billing/timing defect or verification of Muse semantics. |

The paired unmodified path passes the same oracle and actual API-vector output billing check. The joint-input control proves depth/new/tool draws are identical between base and upper bound. Whole-publication recovery proves that the old values remain reachable; it does not establish summed accounting as a provider fact. Alarm counts remain R5 default329/conservative252, R6 6/0, R7 28/24, R8 576/0. No alarm was converted to zero or ignored.

No surface table or separate landing-gate property suite was provided: this remains an explicit brief gap. No reviewer test name was removed. Historical pinned two-node, calc8 service and r3/r4 bridge oracles select their original fraction 1 explicitly; current base-generation tests independently require fraction 0. Run10 byte-preservation validation now checks the immutable signed run10 publication rather than imposing its one-run-only no-change contract on later runs. No physical device inference, Muse semantics audit, new private-log scan, price refresh, network, hosted review, push or build was performed. Review is local self-review only; signed local commits are ready for review. The addressed #hybrid/prototype-go message is prepared locally under `.temp/hybrid-calc-r11-261101/prototype-go-summary.md`; without a network exception it remains unsent.
