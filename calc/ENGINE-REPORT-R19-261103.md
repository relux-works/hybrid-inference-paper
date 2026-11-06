# Engine report R19 — 2026-11-03

Run `hybrid-e-r11-261103`, branch `engine-r19`, parent
`f7aeef958fc3e61a178ce345daa163c769545cbb` (r10c CUDA correction).
**R10c review was still pending at branching**: the local r18 review and latest
25 prototype-go messages contained no exact-head acceptance. The user
explicitly permits this base. This report does not promote producer tests to
independent acceptance. No push, native builds, accelerator use or model
fetches. Only the public price pages were fetched. All 917 run13–18 export
files remain byte-identical; new outputs are confined to `calc/out/run19/`.
Paper prose, including `04-channel.tex` and its “Где стоит сервер” paragraph,
is unchanged. This run supplies engine tables for that deployment discussion.

## What the comparison covers

All alternatives use exactly 10885 of the original 39904 fitted calls:
27.277967%, with prefix+delta+output at most 249000 and delta512–10000.
The original mix reaches roughly one million prefix tokens and includes
larger/smaller deltas. Its unqualified remainder is not silently truncated or
assigned free service. `workload_coverage.csv` retains an explicit alarm for
unconditioned closed-perimeter cost. A single oversized session cannot be
made feasible merely by swapping other sessions.

Every cost is normalized to **52500 calls per person-month from this same
conditional mix**, not the cost of serving 27% of a full requested month.
Routing shares also refer to that conditional mix. API prices are selected
from the original per-call price vectors at the same indices: cache-group
boundaries are not restarted by filtering. M3 Max128GB uses the PRI31 step40
single-stream delta surface. M5 Max64GB uses the existing clean measured M5
prefill depth curve (the pooled bulk2k/10k rate, not a newly measured
M5 delta surface). The M5 rates/priority qualifications are inherited from
R13/R16; no new M5 PRI31 qualification is claimed. Both clients fit every
included session. Client throughput at 2500 calls/day is not newly qualified;
this is server-side provisioning for the stated demand. Macs are already
owned; costs are incremental backend costs, excluding client purchase,
client electricity and common front-end fees for every alternative.

## Node and residency contracts

The RTX5090 node reuses the archived kit1.6.7 Qwen Q4_K_M/q8_0 prefill
surface from the same card measured as a client. **Same llama.cpp prefill
path in the hybrid-prefill binary is an assumption**, not a measured hybrid
node. The PRO6000 comparison uses the kit1.6.5 same-weight delta surface.
Both are serial single-GPU service-time estimates with 70% target load;
there is no new multi-client batching or network-contention measurement.
The 5090 retains the inherited measured slot configuration of 262144 tokens
and a rate ladder ending249000; the physical memory estimate is distinct.

```text
VRAM per resident Qwen session = 34816 * end_depth + 156893184 bytes
5090 session budget = 13e9 bytes (owner's approximate 32GB/model allowance)
physical one-session token bound = floor((13e9 - 156893184)/34816) = 368885
configured-context bound = 262144; measured-rate endpoint = 249000
```

The13GB budget is an approximate usable session budget, not a new allocation
measurement or proof that runtime workspace always fits. PRO6000 uses
96GB minus18.97GB model and8GB workspace:69.03GB for sessions. Per-box
resident counts include one recurrent state per session:

| Prefix | 5090 resident slots | PRO6000 resident slots |
|---|---:|---:|
| 32000 | 10 | 54 |
| 64000 | 5 | 28 |
| 100000 | 3 | 18 |
| 200000 | 1 | 9 |
| 249000 | 1 | 7 |

At100k, a fourth5090 session must spill or refuse; it cannot be resident for
free. Economics reserves249k for each of the four retained sessions per
person, so one5090 slot versus sevenPRO6000 slots per box. This conservative
reservation avoids relying on mean footprint or pooling fragmented free VRAM
across independent replicas. It is not the optimal heterogeneous packing.

Swapping uses the node's measured full-slot file save and restore rows,
with all six depths and successful matching byte/token counts required.
This is the full-session endpoint actually needed by a nonresident server;
it is distinct from client delta import. At100k the measured round trips are
1.394828s on5090 and2.029281s onPRO6000. The storage medium and hybrid-binary
portability remain assumptions; the file measurements are not an isolated
RAM/DMA benchmark. Each operation is `max(measured_file_time, tensor_bytes /
min(tier_bandwidth, PCIe_bandwidth))`, avoiding additive double counting of
file IO. Engine tier rates are estimated100GB/s RAM,7GB/s NVMe and50GB/s PCIe.
For this dataset the measured file times dominate both tiers, so RAM receives
no invented speedup. Shallow restores hold the16k endpoint; depth beyond249k
refuses. Routing conservatively prices both operations at the call's final
prefix. No loss/retry, persistence or transactional correctness is qualified.

The Mac import law remains the R16 conditional Mac depth law, including on
M5 as a portability estimate. The CUDA client fit from r10c is never used for
Mac import. Native server full-slot migration and Mac imported-delta work are
charged separately, once each.

## Links, thresholds and routing

Gigabit and10GbE use ideal application goodput125/1250MB/s and assumed1ms
RTT. Protocol overhead, shared uplink congestion and workstation NIC limits
are unmeasured; the host allowance assumes10GbE. The measured Wi-Fi profile
is the existing **Wi-Fi plus WAN/SSH path replay**, not an office-LAN Wi-Fi
measurement. Measured5G is the existing remote path. The generic WAN profile
reuses the engine's bandwidth/goodput/latency estimate. DecimalMB throughout.

| Link | MB/s | RTT seconds | Basis |
|---|---:|---:|---|
| office_gigabit | 125.000 | 0.001000 | ideal application goodput; 1ms RTT assumption |
| office_10gbe | 1250.000 | 0.001000 | ideal application goodput; 1ms RTT assumption |
| measured_wifi_wan | 5.186 | 0.125757 | measured Wi-Fi plus WAN/SSH path; replay; not office-LAN measurement |
| measured_5g_wan | 9.753 | 0.140589 | measured 5G WAN/SSH path replay |
| engine_wan | 112.500 | 0.400000 | existing engine WAN bandwidth/goodput/RTT estimate |

Isolated-turn threshold = `(156893184 + 34816*delta) /
(local_prefill - node_prefill - swap - Mac_import - RTT)`. The server prefix
is current; catch-up is excluded only from this isolated-turn table.
A nonpositive budget explicitly says no finite winning link. Equality ties;
a faster application link wins. The complete CSV has540 cells covering both
clients/nodes, resident/RAM/NVMe, five link RTTs, three depths and three deltas.
For the office1ms case, resident thresholds are:

| Client | Node | Prefix | Δ512 MB/s | Δ2343 MB/s | Δ10000 MB/s |
|---|---|---:|---:|---:|---:|
| m3max | rtx5090 | 32000 | 93.829 | 17.600 | 7.259 |
| m3max | rtx5090 | 64000 | 83.905 | 12.409 | 5.194 |
| m3max | rtx5090 | 100000 | 47.061 | 7.971 | 3.465 |
| m3max | pro6000 | 32000 | 93.128 | 17.426 | 7.185 |
| m3max | pro6000 | 64000 | 82.446 | 12.254 | 5.119 |
| m3max | pro6000 | 100000 | 45.936 | 7.869 | 3.413 |
| m5max64 | rtx5090 | 32000 | 1269.015 | 43.653 | 18.329 |
| m5max64 | rtx5090 | 64000 | 4056.066 | 26.513 | 10.958 |
| m5max64 | rtx5090 | 100000 | 699.755 | 16.485 | 6.857 |
| m5max64 | pro6000 | 32000 | 1151.848 | 42.600 | 17.860 |
| m5max64 | pro6000 | 64000 | 2186.589 | 25.813 | 10.630 |
| m5max64 | pro6000 | 100000 | 512.974 | 16.055 | 6.653 |

At100k/Δ2343, paying the full measured-file swap proxy changes the office
threshold as follows. RAM and NVMe coincide under the named proxy here.

| Client | Node | Resident MB/s | Swapped MB/s |
|---|---|---:|---:|
| m3max | rtx5090 | 7.971 | 8.360 |
| m3max | pro6000 | 7.869 | 8.434 |
| m5max64 | rtx5090 | 16.485 | 18.244 |
| m5max64 | pro6000 | 16.055 | 18.596 |

Routing uses the existing greatest-stable-offload-set calculation with
expected `at_offload` catch-up. Pending local prefill plus the previous
output is charged when the next offload occurs. Removing a call can enlarge
that pending work and veto more offloads; routing is not just the isolated
threshold check. Node GPU demand includes that work and expected swap cost.
Four sessions/person, uniform popularity and exchangeability are estimates,
not a recovered chronological workload or measured cache-hit rate.

## Office boxes and costs

The card basis is Best Buy's displayed **$1999.99, Sold Out** listing,
SKU6614151, checked2026-11-03. This is a list-price scenario, not an available
procurement offer. NVIDIA's2025-01-06 announcement independently gives a
historical launch price of$1999; it does not establish today's street price.
[Best Buy product page](https://www.bestbuy.com/product/nvidia-geforce-rtx-5090-32gb-gddr7-founders-edition-graphics-card/6614151),
[NVIDIA launch announcement](https://nvidianews.nvidia.com/news/nvidia-blackwell-geforce-rtx-50-series-opens-new-world-of-ai-computer-graphics).

Add an explicitly **unpriced $1500 host allowance** for CPU,128GB RAM,1TB
NVMe, PSU/chassis and10GbE: total box$3499.99. This is not a sourced complete
workstation quote. Usable cache budgets reserve model/OS space:96GB RAM or
900GB NVMe per box. Host cache hardware is included in capex, with no second
monthly storage rental charge. Taxes, price premium/availability and optional
switch/cabling upgrades are outside that allowance's qualification.

Office unit cost uses the existing4-year/20%-residual depreciation,2% annual
support, estimated0.75kW box power,1.3PUE,730calendar hours/month,50% office
power duty and$0.15/kWh. Provisioning uses8h/day,21days and70% target GPU
load, with2500 normalized calls/person/day. No API overflow is hidden in the
conditional closed-perimeter office rows.

Resident-only fleets take the maximum of GPU demand and retained-session
slot count. Swapping fleets also require finite host retention capacity;
the algorithm recomputes route demand whenever it increases the integer box
count. The result is sufficient under these assumptions, **not proved
minimal**. The resident-only5090 counts are20/200/2000 for5/50/500 people
at the declared four-session249k reservation.

Gigabit NVMe-cache results (backendUSD per person-month):

| Client | Staff | 5090 boxes | 5090 USD | PRO6000 boxes | PRO6000 USD | Same-mix cheapest API USD |
|---|---:|---:|---:|---:|---:|---:|
| m3max | 5 | 3 | 70.53 | 3 | 368.43 | 64.95 |
| m3max | 50 | 26 | 61.12 | 27 | 331.59 | 64.95 |
| m3max | 500 | 260 | 61.12 | 262 | 321.77 | 64.95 |
| m5max64 | 5 | 3 | 70.53 | 2 | 245.62 | 64.95 |
| m5max64 | 50 | 23 | 54.07 | 21 | 257.90 | 64.95 |
| m5max64 | 500 | 224 | 52.66 | 209 | 256.68 | 64.95 |

Corresponding offload shares, using each sized fleet's expected residency:

| Client | Staff | Link | 5090 share | PRO6000 share |
|---|---:|---|---:|---:|
| m3max | 5 | office_gigabit | 98.78% | 100.00% |
| m3max | 5 | office_10gbe | 100.00% | 100.00% |
| m3max | 5 | measured_wifi_wan | 14.45% | 17.11% |
| m3max | 5 | measured_5g_wan | 38.36% | 40.75% |
| m3max | 500 | office_gigabit | 98.72% | 100.00% |
| m3max | 500 | office_10gbe | 100.00% | 100.00% |
| m3max | 500 | measured_wifi_wan | 14.45% | 16.78% |
| m3max | 500 | measured_5g_wan | 38.36% | 40.39% |
| m5max64 | 5 | office_gigabit | 65.96% | 77.02% |
| m5max64 | 5 | office_10gbe | 81.42% | 97.68% |
| m5max64 | 5 | measured_wifi_wan | 0.00% | 0.00% |
| m5max64 | 5 | measured_5g_wan | 0.00% | 0.00% |
| m5max64 | 500 | office_gigabit | 65.07% | 77.68% |
| m5max64 | 500 | office_10gbe | 80.70% | 93.28% |
| m5max64 | 500 | measured_wifi_wan | 0.00% | 0.00% |
| m5max64 | 500 | measured_5g_wan | 0.00% | 0.00% |

The full CSV also contains10GbE, both measured WAN paths, generic WAN, RAM
and resident-only cases for all three staff sizes. The existing fully-local
PRO6000 and8-GPU HGXB300 owned references use their original
`own_seconds`/`unit_month` models on exactly the same selected calls, including
server decode/residence. They are a different placement from Mac-local decode
plus a prefill node. The B300 reference retains its existing datacenter
costs, not an imagined office B300 card. These values are exposed in
`same_mix_own_references.csv` and beside every office row. Their inherited
quantization, power and batching approximations are not new measurements.
At the sold-out card's list price, shared5090 costs can narrowly undercut the
cheapest API for larger teams; the small margin is conditional on the host,
price and workload assumptions and is not a procurement conclusion.

## Rented5090 prefill node

Observed Vast offers supplied by the owner on2026-11-03 are$0.448–0.522/h;
they are not market rates. This is a warm prefill service with Mac-local
decode, **not** R18's ephemeral fully-local task machine. First model fetch,
model-load/startup latency, disconnects and persistence after the lease ends
are not included or qualified. A full-calendar warm lease retains state
while rented; there is no claimed state across terminated rentals.

For each client/WAN/tier, the engine shows both utilization-priced GPU work
at70% load (a lower-bound allocation needing effective pooling/scheduling)
and an entire730-hour calendar node including idle time. The latter uses a
one-person service allocation, not an optimized many-user rental pool.
RAM/NVMe retention is a separate estimated provisioning allowance at the
existing engine tier prices, not an asserted Vast storage bill or guarantee
that those host capacities accompany the observed GPU offers. Egress uses
the existing$5/TB scenario. Network uploads and ancillary unquoted charges
are unmeasured. Each cost divides by the same52500 conditional calls/month.

NVMe-cache rental ranges (offer endpoints), including retention and egress:

| Client | WAN | Offload share | GPU-work USD/1000 | GPU-work USD/person-month | Warm whole-node USD/person-month |
|---|---|---:|---:|---:|---:|
| m3max | measured_wifi_wan | 14.63% | 0.80–0.88 | 42.02–46.20 | 343.76–397.78 |
| m3max | measured_5g_wan | 38.71% | 1.21–1.30 | 63.59–68.25 | 362.39–416.41 |
| m3max | engine_wan | 97.48% | 1.93–2.04 | 101.12–106.92 | 393.07–447.09 |
| m5max64 | measured_wifi_wan | 0.00% | 0.00–0.00 | 0.00–0.00 | 0.00–0.00 |
| m5max64 | measured_5g_wan | 0.00% | 0.00–0.00 | 0.00–0.00 | 0.00–0.00 |
| m5max64 | engine_wan | 62.77% | 1.53–1.63 | 80.21–85.33 | 376.28–430.30 |

Zero rental cost on the two slow M5 paths means the policy bypasses the
node and executes locally; it does not mean free AI computation. The full
rental CSV includes whole-nodeUSD/1000 and both RAM/NVMe cases. Warm whole
nodes cost substantially more than the work-allocation lower bound; the
engine does not equate those two billing scenarios.

## Exports, validation and boundary

Nine tables:10capacity rows,24native swap observations,5links,540isolated
threshold cells,60routing diagnostics,180office rows,48rental rows,6existing
own-server references and1coverage row. Thirteen generated payloads plus
INDEX retain all output hashes and the live generator/source identities.
The quote ledger has20175 coordinate-qualified records, including both
public price sources. No old paper quote was edited.

The R18 auditor now binds to the frozenf7aeef95 generator, rather than
requiring R19 source identity to equal the old generator. Its historical file
perimeter is limited to the actual parent roots. The run18 payloads/ledger
and all previously named tests are retained. R16b and Glimmer/Gemma PRI31
loader/calculation interfaces are unchanged; R19's Context reads the same
current data selection. No old export is regenerated to accommodate R19.

Commands use Python standard library/localGit, diskTMPDIR and
PYTHONDONTWRITEBYTECODE=1. Gate logs and research are under
`.temp/hybrid-e-r11-261103/`; commands are documented in `calc/README.md`.
Live recomputation matches every published payload byte; a corrupted
scratch threshold is refused by that checker. The first CLI probe failed
because isolated-mode execution of the root shim does not expose the local
package; documented exporter/test entry points set their package path and
work. The initial smoke also exposed a missing computed_metrics result key;
that failure is preserved and corrected, never presented as passing evidence.

| Mutant | Gate narrowed to | Named failing test | Real exit |
|---|---|---|---:|
| omit_state | One recurrent state per resident | test_resident_overflow_must_swap_or_refuse | 1 |
| free_swap | Measured full-slot migration charged once | test_swap_rejects_free_reload_double_count_and_depth_extrapolation | 1 |
| ignore_capacity | Configured per-session hard bound | test_capacity_estimate_cannot_extend_configured_or_measured_limits | 1 |
| ignore_catchup | Expected pending local work veto | test_routing_rejects_ignored_catchup_and_bills_only_selected_work | 1 |
| unpriced_box | Card/host and observed-price provenance | test_prices_reject_card_only_box_market_relabelling_and_bad_digest | 1 |
| pool_retention | Independent boxes, finite host retention | test_fleet_rejects_pooled_vram_fragmentation_and_free_retention | 1 |
| time_units | Bandwidth distinguished from seconds | test_export_units_reject_bandwidth_labelled_as_time | 1 |

All seven faults fail by named assertions, with no setup errors or survivors.
The unchanged positive control passes. Focused16 and retainedR18 tests26
pass, as do kit24. Final engine and artifact checks are recorded below. No surface table/separate landing property
suite was supplied (brief gap). Out of measured contract: full unconditioned
workload cost, hybrid-binary equivalence, RAM-specific direct import, runtime
concurrency/latency, heterogeneous optimal packing, actual host BOM/street
availability, provider startup/retention guarantees and quality qualification.
These limits are not silently converted to measured claims.


Final annotation correction: engine01 passed419 tests/475.395s before the
last schema correction. Review then found the generic `_s` suffix labelled
MB/s, Mbit/s and B/s fields as seconds. The new named regression first failed
(exit1 at the byte-bandwidth assertion), then passed after the specific unit
rules were moved before generic time. Time and currency columns remain
positive controls. All nine numeric CSVs are byte-identical across this fix;
only schema/generator/index metadata changed. Current focused16 passes; the
seventh narrowing fault fails at the named assertion. Final engine02 and a
new live-export comparison bind to `suite-source-identity-final.json`. The
prior419-test run is not substituted for the final source identity.


## Final validation and handoff

Ready for review. Final engine02 passes420 tests in471.192s, actual exit0,
from2026-11-03T13:43:56.753396Z to13:51:50.357130Z. Focused16 and kit24
pass (exit0). All396 previously declared test methods are retained; current
declared count is412 and discovery executes420 cases. Calculator, input and
test hashes are unchanged since the final full-suite snapshot. No numerical
or test edits followed this pass.

| Gate | Actual exit | Evidence under task scratch |
|---|---:|---|
| Full engine420 | 0 | engine-suite-02.log |
| Focused16 | 0 | focused-final-04.log |
| Kit24, unchanged bench identity | 0 | kit-suite-01.log |
| Final exporter /917 frozen files /20175 quotes | 0 | export-final-04.log |
| Live13-payload byte comparison and corruption control | 0 | live-export-final-02.log |
| Runtime identity, preserved test names,7 assertion-only faults | 0 | final-artifacts-01.log; final-evidence.json |
| Unit regression before correction | 1, intended assertion | units-regression-before-01.log |

All nine CSVs retain exact numeric bytes across the final unit-label fix.
No earlier failed smoke or pre-correction full run is presented as final-source
evidence.

Observed task free-disk minimum is28855939072 B (28.856GB), above the28GB
floor. A one-second observer records all samples; the owned-PID/start-identity
guard intervenes at29GB and was not triggered during either full suite. No
foreign cleanup or process control occurred. Scratch/artifact footprint is
small; the earlier R18/r10c resource exceptions remain in their original
reports and are not attributed to this run.

The signed local change contains only R19 implementation/configuration,
new R19 output/report/quotes, tests and the historical R18 auditor binding,
price evidence, documentation and the root manifest. No push or hosted
landing. Binary/quality/provider/procurement qualifications remain as stated;
ready for review does not claim independent acceptance.
