# Engine run23 — the night’s measured inputs

Base: accepted run22 `9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0` (Muse r5x4 ACCEPT). Historical run13–22 exports and their generators remain byte-identical. This successor retains bf16 transport by default, f32 control/resident state, dedicated bought/rented primary economics, the API cache/window bounds and the same workload shapes.

The r5x4 notes are carried forward: M3 Max threshold results are explicitly named; economics clients remain M5 Max, not the owner’s M3; zero-prefill-offload crossings disclose local work plus residency/overflow rather than claim an offload gain. Bought-server assumptions are restated below. The old brief’s idleness example is superseded by the measured-basis tables, not reused as a target.

## Direct Mac measurements and their gate

Owner’s **M3 Max 128 GB, normal priority**, kit 1.6.12 step 56, model internal, slots/references on an **external LaCie SSD**, **warm/no purge**. Each shape has one excluded warm-up and three timed rounds; prefill medians exclude restore. Decode is 255 steps after the seed. These are native measurements, not end-to-end hybrid TTFT.

The first attempt at 524288 refused at raw-logit bound 1.0 (max difference 1.08298), before any decode/delta/1040000 child. The later accepted timing run used bound 4.0; it was raised after that refusal and is **not calibrated**. At 524288 max KL/mean KL=0.0017539/0.00032912, top1=64/64; at 1040000=0.0021309/0.00032571, top1=63/64 and max raw difference 3.01402. All 30 native children stayed inside the pageout guard; swapouts 0. Neither attempt is hidden.

| Actual depth | Delta | Prefill s, restore excluded | First-probe restore s | Timed warm restore median s | Decode tok/s | Status |
|---:|---:|---:|---:|---:|---:|---|
| 524288 | 690 | 48.255 | 20.523 | 2.965 | 3.841 | measured |
| 524288 | 2000 | 161.768 | 20.523 | 2.965 | 3.841 | measured |
| 524288 | 10000 | 843.260 | 20.523 | 2.965 | 3.841 | measured |
| 1040000 | 690 | 72.408 | 40.465 | 40.479 | 1.664 | measured |
| 1040000 | 2000 | 296.966 | 40.465 | 40.479 | 1.664 | measured |
| 1040000 | 10000 | — | 40.465 | 40.479 | 1.664 | refused_context |

At 524288 the later 18.4 GB restores benefit from OS caching; at 1040000 the 36.4 GB file does not remain cached beside wired model/KV. “First” is not a purged cold measurement. The 1040000+10000 shape stays refused: 1050000 exceeds 1048576. FACTS is the accepted source for the rounded Mac medians; the strict archive (1069117 B, abbreviated SHA 90723f8c…be43) remains with the incident lane, and this checkout does not claim full archive re-verification.

## M3 Max million-context routing

Qwen, Delta 690, B300 FP8 with FP8 KV, historical home Wi-Fi 5.19 MB/s, RTT 126 ms. The main rows use the measured 1040000 local prefill and timed warm full-slot restore. As instructed, the restore is charged **once per offload as a conservative recovery proxy**, while wire bytes remain the modelled bf16/f32 delta payload. This is **not a measured delta import or a measured complete hybrid path**. B300 prefill and its deep bridge envelope remain extrapolated. The 1000000 comparison explicitly uses the 1040000 observation as a proxy; the direct observation is never renamed a measured 1000000 turn.

Recovery uses the supplied restore-before-decode median for each delta shape; per-delta restore medians are not available in this checkout. This is a charged recovery proxy, not a measured delta import. The Delta690 headline is accompanied by the measured Delta2000 case and the Delta10000 context refusal.

| Scenario depth / delta / local basis | Transport | Actual Mac observation depth | Local prefill s | Recovery charged s | Threshold MB/s | Offload |
|---|---|---:|---:|---:|---:|---|
| 1040000 / 690 / direct | bf16 | 1040000 | 72.408 | 40.479 | 3.356 | True |
| 1040000 / 690 / direct | f32 | 1040000 | 72.408 | 40.479 | 5.925 | False |
| 1040000 / 2000 / direct | bf16 | 1040000 | 296.966 | 40.479 | 0.581 | True |
| 1040000 / 2000 / direct | f32 | 1040000 | 296.966 | 40.479 | 0.889 | True |
| 1040000 / 10000 / context refusal | bf16 | 1040000 | — | 40.479 | — | False |
| 1040000 / 10000 / context refusal | f32 | 1040000 | — | 40.479 | — | False |
| 1000000 / 690 / explicit 1.04M proxy | bf16 | 1040000 | 72.408 | 40.479 | 3.351 | True |
| 1000000 / 690 / explicit 1.04M proxy | f32 | 1040000 | 72.408 | 40.479 | 5.916 | False |
| 1000000 / 690 / earlier 120s sensitivity | bf16 | 1040000 | 120.000 | 40.479 | 1.311 | True |
| 1000000 / 690 / earlier 120s sensitivity | f32 | 1040000 | 120.000 | 40.479 | 2.314 | True |

| Link profile at actual 1040000 / Delta690 | MB/s | RTT s | bf16 remote s / offload | f32 remote s / offload |
|---|---:|---:|---:|---:|
| historical_home_wifi | 5.19 | 0.126 | 61.619 / True | 76.734 / False |
| historical_5g | 9.75 | 0.126 | 52.385 / True | 60.430 / True |
| today_wifi | 0.80 | 0.126 | 169.962 / False | 268.020 / False |
| today_wan | 2.80 | 0.126 | 78.471 / False | 106.488 / False |
| fullslot_e2e | 5.18 | 0.126 | 61.657 / True | 76.801 / False |

The analyst’s earlier 120s local turn remains a sensitivity beside the measured basis, using the same newly charged recovery. At 512k, first versus timed-warm restores have separate routing rows. All measured-link profiles and both transport arms are exported. M5 Max deep local/import estimates remain explicitly estimated; no M3 measurement is ported into M5 economics. The normal-priority M3 decode 1.6638 tok/s replaces the earlier background-priority 1.67 in the ceiling comparison; the actual measurement depth stays 1040000.

## PRO6000 vLLM decode now drives the economics

Kit 1.6.11 `cd85a194`, Muse r7at ACCEPT; private independent contexts, 256 generated tokens, three-round medians over the common decode interval. Timing granularity is SSE chunk receipt with exact token IDs in each chunk. The local GPU archive SHA256 8a58f122af021136721e720232a6cc4c081ed3674391bdf13714e6d63d24efe0 was verified. Raw-source hashes, round aggregates and capacity searches are retained in the compact receipt.

| Actual depth | Streams | Largest resident | Aggregate tok/s | Gain |
|---:|---:|---:|---:|---:|---:|
| 16384 | 1 | 39 | 48.705 | 1.000 |
| 16384 | 8 | 39 | 302.600 | 6.213 |
| 16384 | 32 | 39 | 686.817 | 14.102 |
| 16384 | 39 | 39 | 737.934 | 15.151 |
| 65536 | 1 | 12 | 44.464 | 1.000 |
| 65536 | 8 | 12 | 190.289 | 4.280 |
| 65536 | 12 | 12 | 225.350 | 5.068 |
| 164000 | 1 | 5 | 38.105 | 1.000 |
| 164000 | 5 | 5 | 84.222 | 2.210 |
| 256000 | 1 | 3 | 33.067 | 1.000 |
| 256000 | 3 | 3 | 57.730 | 1.746 |

Exact observed depth/count points return the measured value. Other batches interpolate seconds per sequence-token. Between depths the same fraction of the admitted resident batch is used, with linear service-time interpolation. Capacity interpolates reciprocal resident count (space/session), rounds down, and is also bounded by physical memory. Those intermediate points are assumptions calibrated to measurements, not additional measurements. Unlike run22’s lone 16k point, the surface applies automatically to every supported workload shape. Below 16384 / above 256000 remain modelled; B300 decode remains modelled because its rental failed to start at 2026-11-04 00:36Z.

**PRO vLLM at 1M is impossible:** default KV required 61.97 GiB versus 56.62 GiB available; FP8 KV is unavailable on SM 12.0. Routing rows have no finite remote time/threshold; decode rows are capacity refusals. The historical llama.cpp Q4/q8 slot builder remains artifact-construction context only, explicitly not a feasible current vLLM 1M server scenario.

Bridge component medians are exported as context: the source is loopback with a CUDA client. There is no separate non-overlapping export/conversion term, and its CUDA import cannot replace Metal recovery. The reviewed aggregate bridge envelope is retained; phases are not added twice.

## Dedicated PRO6000 costs and fleet changes

Selection: bought PRO6000 vLLM FP8, office 125 MB/s RTT 1 ms assumed; owned PRI31 M5 Max 64 GB, s=20%, bf16; owner 98.1% aggregate cache allowance (1.9% misses billed, provider behaviour unverified). Economics compare the same selected measured call shapes, normalized per person-month; this is the open-model cost component, not the full unconditioned source workload. Light/medium are typical; heavy 2500 calls/day is the owner’s intensity.

Inherited cost assumptions, not new price observations: bought PRO box capex $30000, 20% residual over 4 years, 2% annual support; 0.9 kW x PUE 1.3 x730h x office load 0.5 x $0.15/kWh, no office colo, giving $614.0575/box-month. Rental remains the engine’s $2.20/h x730=$1606/month, WAN 112.5 MB/s RTT 400 ms, egress $5/decimal TB and separate storage. Owned client energy $2.52/month plus $5 front; buying an M5 Max 64 instead adds $69.05/month. Fleets are sufficient, not proved minimal. Service utilization includes allocated-GPU tool/concurrency occupancy, not hardware SM telemetry.

| Profile / load, 50 people | Own cluster old $ / new $ | Own boxes old / new | Own service/calendar old to new | Hybrid new $ | Hybrid service / calendar | Median API / hybrid old / new |
|---|---:|---:|---:|---:|---:|---:|
| existing_combined / light | 49.12 / 49.12 | 4 / 4 | 50.07% / 11.52% → 50.07% / 11.52% | 56.64 | 3.61% / 0.83% | 0.088 / 0.088 |
| existing_combined / medium | 135.09 / 135.09 | 11 / 11 | 66.47% / 15.30% → 66.46% / 15.29% | 56.64 | 14.46% / 3.33% | 0.351 / 0.351 |
| existing_combined / heavy | 331.59 / 331.59 | 27 / 27 | 66.87% / 15.39% → 66.61% / 15.33% | 56.64 | 45.17% / 10.40% | 1.097 / 1.097 |
| claude_deep / light | 61.41 / 61.41 | 5 / 5 | 56.06% / 12.90% → 57.56% / 13.25% | 56.64 | 0.00% / 0.00% | 0.099 / 0.099 |
| claude_deep / medium | 184.22 / 184.22 | 15 / 15 | 66.98% / 15.41% → 68.95% / 15.87% | 56.64 | 0.00% / 0.00% | 0.397 / 0.397 |
| claude_deep / heavy | 454.40 / 454.40 | 37 / 37 | 68.05% / 15.66% → 69.17% / 15.92% | 56.64 | 0.00% / 0.00% | 1.242 / 1.242 |

The Claude measured-shape rows with zero prefill offload price local client work plus residency/any generation overflow. Their crossings are not evidence of an offload gain. The sentence forms state that explicitly. API admission, workload profiles and measured-shape coverage exports are byte-identical to run22. Coverage means the share of calls whose shapes lie inside the measured ladder, normalized to the row’s calls/person-month; it is not a fraction of total work. Physical-envelope fractions use deep estimates. No provider cache measurement has arrived; no-cache, owner 98.1% and measured/pending remain separate.

| Heavy sensitivity: generation on own PRO server, 50 people | Old $/person-month | New $/person-month | Old service/calendar | New service/calendar |
|---|---:|---:|---:|---:|
| existing_combined | 331.59 | 331.59 | 66.87% / 15.39% | 66.61% / 15.33% |
| claude_deep | 454.40 | 454.40 | 68.05% / 15.66% | 69.17% / 15.92% |

All small-team/share/load/billing/client rows and shared-provider bounds are exported. The shared resident-work allocation remains a supplementary utilization limit; it is not substituted for a dedicated comparator. Night agents may raise utilization. The withdrawn universal heavy-load claim was lost after recalculation on vLLM; it held only for the owner-excluded 5090 hybrid, not because of a second Mac.

## Words-ready conclusions

These are generated short forms; each has its canonical, row-bound counterpart in the paper exports. Cache allowance, link, billing, client, s, load, coverage, transport and measured/modelled decode basis travel with every sentence.

- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 5 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 2 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 45 people through 500 scanned people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled.
- Claude Code reconstructed measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 554/1000 (55.40%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 554/1000 (55.40%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 554/1000 (55.40%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 4 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 554/1000 (55.40%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 554/1000 (55.40%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 554/1000 (55.40%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 2 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 554/1000 (55.40%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 30 people through 500 scanned people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 554/1000 (55.40%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.
- Claude Code reconstructed measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 554/1000 (55.40%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.

The measured-shape rental crossing changes; the zero-prefill-offload condition is material:

- Claude Code reconstructed measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 73 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 554/1000 (55.40%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; PRO decode measured/interpolated 16384–256000, beyond modelled. Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.

## Changed against run22: every abstract-bound coordinate

The table below includes unchanged numbers too. It covers every numeric coordinate quoted by the accepted run22 report, its prose local/recovery/decode inputs, primary fleet counts and sustained crossing statements. Full semantic row keys, both row indices, exact unrounded values, absolute/percentage deltas and reasons are in `abstract_bound_changes.csv`. These audit addresses are not standalone paper quotations; use the condition-complete sentences above. Every common-coordinate numeric/verdict change across the full matrices is separately in `changed_against_run22.csv`; added/removed rows are counted in `change_summary.csv`.

| Table: old row to new row / column | Old | New | Why |
|---|---|---|---|
| quality_evidence:1→1 / value | 390 | 390 | unchanged on the same coordinate/basis |
| quality_evidence:1→1 / answer_changes | 28 | 28 | unchanged on the same coordinate/basis |
| quality_evidence:2→2 / value | 390 | 390 | unchanged on the same coordinate/basis |
| quality_evidence:2→2 / answer_changes | 33 | 33 | unchanged on the same coordinate/basis |
| link_thresholds:970→1410 / wire_bytes | 102469632 | 102469632 | unchanged on the same coordinate/basis |
| link_thresholds:970→1410 / transfer_s | 19.74366705202312 | 19.74366705202312 | unchanged on the same coordinate/basis |
| link_thresholds:970→1410 / threshold_MB_s | 2.9923562566180237 | 3.3508235827379265 | M3 deep local time measured at1.04M; full-slot warm LaCie recovery charged as explicit proxy, not delta-import measurement; PRO1M impossible |
| link_thresholds:970→1410 / offload | True | True | unchanged on the same coordinate/basis |
| link_thresholds:980→1420 / wire_bytes | 102469632 | 102469632 | unchanged on the same coordinate/basis |
| link_thresholds:980→1420 / transfer_s | 19.74366705202312 | 19.74366705202312 | unchanged on the same coordinate/basis |
| link_thresholds:980→1420 / threshold_MB_s | 1.2240350447215587 | 1.3108154583198801 | M3 deep local time measured at1.04M; full-slot warm LaCie recovery charged as explicit proxy, not delta-import measurement; PRO1M impossible |
| link_thresholds:980→1420 / offload | True | True | unchanged on the same coordinate/basis |
| link_thresholds:1080→1520 / wire_bytes | 180916224 | 180916224 | unchanged on the same coordinate/basis |
| link_thresholds:1080→1520 / transfer_s | 34.858617341040464 | 34.858617341040464 | unchanged on the same coordinate/basis |
| link_thresholds:1080→1520 / threshold_MB_s | 5.283182775655014 | 5.9160781399029245 | M3 deep local time measured at1.04M; full-slot warm LaCie recovery charged as explicit proxy, not delta-import measurement; PRO1M impossible |
| link_thresholds:1080→1520 / offload | False | False | unchanged on the same coordinate/basis |
| link_thresholds:1090→1530 / wire_bytes | 180916224 | 180916224 | unchanged on the same coordinate/basis |
| link_thresholds:1090→1530 / transfer_s | 34.858617341040464 | 34.858617341040464 | unchanged on the same coordinate/basis |
| link_thresholds:1090→1530 / threshold_MB_s | 2.1611066031221378 | 2.3143225797869764 | M3 deep local time measured at1.04M; full-slot warm LaCie recovery charged as explicit proxy, not delta-import measurement; PRO1M impossible |
| link_thresholds:1090→1530 / offload | True | True | unchanged on the same coordinate/basis |
| workload_coverage:0→0 / measured_shape_calls | 10885 | 10885 | unchanged on the same coordinate/basis |
| workload_coverage:0→0 / source_calls | 39904 | 39904 | unchanged on the same coordinate/basis |
| workload_coverage:0→0 / measured_shape_fraction | 0.2727796712109062 | 0.2727796712109062 | unchanged on the same coordinate/basis |
| workload_coverage:0→0 / selected_calls | 10885 | 10885 | unchanged on the same coordinate/basis |
| workload_coverage:0→0 / selected_fraction | 0.2727796712109062 | 0.2727796712109062 | unchanged on the same coordinate/basis |
| workload_coverage:1→1 / measured_shape_calls | 10885 | 10885 | unchanged on the same coordinate/basis |
| workload_coverage:1→1 / source_calls | 39904 | 39904 | unchanged on the same coordinate/basis |
| workload_coverage:1→1 / measured_shape_fraction | 0.2727796712109062 | 0.2727796712109062 | unchanged on the same coordinate/basis |
| workload_coverage:1→1 / selected_calls | 39788 | 39788 | unchanged on the same coordinate/basis |
| workload_coverage:1→1 / selected_fraction | 0.997093023255814 | 0.997093023255814 | unchanged on the same coordinate/basis |
| workload_coverage:2→2 / measured_shape_calls | 554 | 554 | unchanged on the same coordinate/basis |
| workload_coverage:2→2 / source_calls | 1000 | 1000 | unchanged on the same coordinate/basis |
| workload_coverage:2→2 / measured_shape_fraction | 0.554 | 0.554 | unchanged on the same coordinate/basis |
| workload_coverage:2→2 / selected_calls | 554 | 554 | unchanged on the same coordinate/basis |
| workload_coverage:2→2 / selected_fraction | 0.554 | 0.554 | unchanged on the same coordinate/basis |
| workload_coverage:3→3 / measured_shape_calls | 554 | 554 | unchanged on the same coordinate/basis |
| workload_coverage:3→3 / source_calls | 1000 | 1000 | unchanged on the same coordinate/basis |
| workload_coverage:3→3 / measured_shape_fraction | 0.554 | 0.554 | unchanged on the same coordinate/basis |
| workload_coverage:3→3 / selected_calls | 985 | 985 | unchanged on the same coordinate/basis |
| workload_coverage:3→3 / selected_fraction | 0.985 | 0.985 | unchanged on the same coordinate/basis |
| small_team_cost:0→0 / person_month | 212.20583333333335 | 212.20583333333335 | unchanged on the same coordinate/basis |
| small_team_cost:0→0 / service_utilization | 0.00977081682601338 | 0.00977081682601338 | unchanged on the same coordinate/basis |
| small_team_cost:0→0 / calendar_utilization | 0.0022486263380414357 | 0.0022486263380414357 | unchanged on the same coordinate/basis |
| small_team_cost:0→0 / own_cluster_person_month | 204.68583333333333 | 204.68583333333333 | unchanged on the same coordinate/basis |
| small_team_cost:0→0 / own_service_utilization | 0.10132144835987375 | 0.10123165492577184 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:0→0 / own_calendar_utilization | 0.023317812773231222 | 0.023297147982917352 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:2→2 / person_month | 130.3315 | 130.3315 | unchanged on the same coordinate/basis |
| small_team_cost:2→2 / service_utilization | 0.015469427748311244 | 0.015469427748311244 | unchanged on the same coordinate/basis |
| small_team_cost:2→2 / calendar_utilization | 0.0035600874818031356 | 0.0035600874818031356 | unchanged on the same coordinate/basis |
| small_team_cost:2→2 / own_cluster_person_month | 122.8115 | 122.8115 | unchanged on the same coordinate/basis |
| small_team_cost:2→2 / own_service_utilization | 0.18527868748121845 | 0.18525364921198129 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:2→2 / own_calendar_utilization | 0.042639478762800956 | 0.042633716530976515 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:4→4 / person_month | 68.92575 | 68.92575 | unchanged on the same coordinate/basis |
| small_team_cost:4→4 / service_utilization | 0.029319732533488702 | 0.029319732533488702 | unchanged on the same coordinate/basis |
| small_team_cost:4→4 / calendar_utilization | 0.006747554884419318 | 0.006747554884419318 | unchanged on the same coordinate/basis |
| small_team_cost:4→4 / own_cluster_person_month | 61.40575 | 61.40575 | unchanged on the same coordinate/basis |
| small_team_cost:4→4 / own_service_utilization | 0.39553450486382286 | 0.3955372888851754 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:4→4 / own_calendar_utilization | 0.09102711892756471 | 0.09102775963384858 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:6→6 / person_month | 68.92575 | 68.92575 | unchanged on the same coordinate/basis |
| small_team_cost:6→6 / service_utilization | 0.029319732533488702 | 0.029319732533488702 | unchanged on the same coordinate/basis |
| small_team_cost:6→6 / calendar_utilization | 0.006747554884419318 | 0.006747554884419318 | unchanged on the same coordinate/basis |
| small_team_cost:6→6 / own_cluster_person_month | 61.40575 | 61.40575 | unchanged on the same coordinate/basis |
| small_team_cost:6→6 / own_service_utilization | 0.39553450486382286 | 0.3955372888851754 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:6→6 / own_calendar_utilization | 0.09102711892756471 | 0.09102775963384858 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:288→288 / person_month | 212.20583333333335 | 212.20583333333335 | unchanged on the same coordinate/basis |
| small_team_cost:288→288 / service_utilization | 0.03908326730405352 | 0.03908326730405352 | unchanged on the same coordinate/basis |
| small_team_cost:288→288 / calendar_utilization | 0.008994505352165743 | 0.008994505352165743 | unchanged on the same coordinate/basis |
| small_team_cost:288→288 / own_cluster_person_month | 204.68583333333333 | 204.68583333333333 | unchanged on the same coordinate/basis |
| small_team_cost:288→288 / own_service_utilization | 0.405285793439495 | 0.40492661970308735 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:288→288 / own_calendar_utilization | 0.09327125109292489 | 0.09318859193166941 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:290→290 / person_month | 130.3315 | 130.3315 | unchanged on the same coordinate/basis |
| small_team_cost:290→290 / service_utilization | 0.061877710993244975 | 0.061877710993244975 | unchanged on the same coordinate/basis |
| small_team_cost:290→290 / calendar_utilization | 0.014240349927212542 | 0.014240349927212542 | unchanged on the same coordinate/basis |
| small_team_cost:290→290 / own_cluster_person_month | 245.623 | 245.623 | unchanged on the same coordinate/basis |
| small_team_cost:290→290 / own_service_utilization | 0.3217008618488369 | 0.3212011823959272 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:290→290 / own_calendar_utilization | 0.07403526683644465 | 0.0739202721130353 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:292→292 / person_month | 68.92575 | 68.92575 | unchanged on the same coordinate/basis |
| small_team_cost:292→292 / service_utilization | 0.11727893013395481 | 0.11727893013395481 | unchanged on the same coordinate/basis |
| small_team_cost:292→292 / calendar_utilization | 0.026990219537677274 | 0.026990219537677274 | unchanged on the same coordinate/basis |
| small_team_cost:292→292 / own_cluster_person_month | 184.21725 | 184.21725 | unchanged on the same coordinate/basis |
| small_team_cost:292→292 / own_service_utilization | 0.4611329189802121 | 0.46087739542139816 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:292→292 / own_calendar_utilization | 0.10612374025845978 | 0.10606493483670533 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:294→294 / person_month | 68.92575 | 68.92575 | unchanged on the same coordinate/basis |
| small_team_cost:294→294 / service_utilization | 0.11727893013395481 | 0.11727893013395481 | unchanged on the same coordinate/basis |
| small_team_cost:294→294 / calendar_utilization | 0.026990219537677274 | 0.026990219537677274 | unchanged on the same coordinate/basis |
| small_team_cost:294→294 / own_cluster_person_month | 153.514375 | 153.514375 | unchanged on the same coordinate/basis |
| small_team_cost:294→294 / own_service_utilization | 0.5730381315062181 | 0.5728941771994857 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:294→294 / own_calendar_utilization | 0.13187726862060908 | 0.13184413941029258 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:576→576 / person_month | 212.20583333333335 | 212.20583333333335 | unchanged on the same coordinate/basis |
| small_team_cost:576→576 / service_utilization | 0.12213521032516726 | 0.12213521032516726 | unchanged on the same coordinate/basis |
| small_team_cost:576→576 / calendar_utilization | 0.028107829225517945 | 0.028107829225517945 | unchanged on the same coordinate/basis |
| small_team_cost:576→576 / own_cluster_person_month | 409.37166666666667 | 409.37166666666667 | unchanged on the same coordinate/basis |
| small_team_cost:576→576 / own_service_utilization | 0.4877948780992937 | 0.4843480540539637 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:576→576 / own_calendar_utilization | 0.11225964317901554 | 0.11146640148091219 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:578→578 / person_month | 130.3315 | 130.3315 | unchanged on the same coordinate/basis |
| small_team_cost:578→578 / service_utilization | 0.19336784685389052 | 0.19336784685389052 | unchanged on the same coordinate/basis |
| small_team_cost:578→578 / calendar_utilization | 0.04450109352253919 | 0.04450109352253919 | unchanged on the same coordinate/basis |
| small_team_cost:578→578 / own_cluster_person_month | 368.4345 | 368.4345 | unchanged on the same coordinate/basis |
| small_team_cost:578→578 / own_service_utilization | 0.5733639443236279 | 0.5702883547514748 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:578→578 / own_calendar_utilization | 0.13195225020050616 | 0.1312444432852709 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:580→580 / person_month | 68.92575 | 68.92575 | unchanged on the same coordinate/basis |
| small_team_cost:580→580 / service_utilization | 0.3664966566686088 | 0.3664966566686088 | unchanged on the same coordinate/basis |
| small_team_cost:580→580 / calendar_utilization | 0.08434443605524149 | 0.08434443605524149 | unchanged on the same coordinate/basis |
| small_team_cost:580→580 / own_cluster_person_month | 368.4345 | 368.4345 | unchanged on the same coordinate/basis |
| small_team_cost:580→580 / own_service_utilization | 0.5733639443236279 | 0.5702883547514748 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:580→580 / own_calendar_utilization | 0.13195225020050616 | 0.1312444432852709 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:582→582 / person_month | 68.92575 | 68.92575 | unchanged on the same coordinate/basis |
| small_team_cost:582→582 / service_utilization | 0.3664966566686088 | 0.3664966566686088 | unchanged on the same coordinate/basis |
| small_team_cost:582→582 / calendar_utilization | 0.08434443605524149 | 0.08434443605524149 | unchanged on the same coordinate/basis |
| small_team_cost:582→582 / own_cluster_person_month | 337.731625 | 337.731625 | unchanged on the same coordinate/basis |
| small_team_cost:582→582 / own_service_utilization | 0.6512914738781933 | 0.6486127379929402 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| small_team_cost:582→582 / own_calendar_utilization | 0.14988625700210476 | 0.14926978079837527 | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| dedicated_multiples:0→0 / person_month | 56.644600000000004 | 56.644600000000004 | unchanged on the same coordinate/basis |
| dedicated_multiples:0→0 / service_utilization | 0.036139896849339874 | 0.036139896849339874 | unchanged on the same coordinate/basis |
| dedicated_multiples:0→0 / calendar_utilization | 0.00831712694614945 | 0.00831712694614945 | unchanged on the same coordinate/basis |
| dedicated_multiples:0→0 / api_median_over_hybrid | 0.08775148201614674 | 0.08775148201614674 | unchanged on the same coordinate/basis |
| shared_multiples:0→0 / person_month | 15.903889624105993 | 15.903889624105993 | unchanged on the same coordinate/basis |
| shared_multiples:0→0 / api_median_over_hybrid | 0.31254288829304183 | 0.31254288829304183 | unchanged on the same coordinate/basis |
| dedicated_multiples:144→144 / person_month | 56.644600000000004 | 56.644600000000004 | unchanged on the same coordinate/basis |
| dedicated_multiples:144→144 / service_utilization | 0.1445595873973595 | 0.1445595873973595 | unchanged on the same coordinate/basis |
| dedicated_multiples:144→144 / calendar_utilization | 0.0332685077845978 | 0.0332685077845978 | unchanged on the same coordinate/basis |
| dedicated_multiples:144→144 / api_median_over_hybrid | 0.35100592806458697 | 0.35100592806458697 | unchanged on the same coordinate/basis |
| shared_multiples:36→36 / person_month | 21.285129875623976 | 21.285129875623976 | unchanged on the same coordinate/basis |
| shared_multiples:36→36 / api_median_over_hybrid | 0.9341070742357612 | 0.9341070742357612 | unchanged on the same coordinate/basis |
| dedicated_multiples:288→288 / person_month | 56.644600000000004 | 56.644600000000004 | unchanged on the same coordinate/basis |
| dedicated_multiples:288→288 / service_utilization | 0.45174871061674843 | 0.45174871061674843 | unchanged on the same coordinate/basis |
| dedicated_multiples:288→288 / calendar_utilization | 0.10396408682686811 | 0.10396408682686811 | unchanged on the same coordinate/basis |
| dedicated_multiples:288→288 / api_median_over_hybrid | 1.0968935252018344 | 1.0968935252018344 | unchanged on the same coordinate/basis |
| shared_multiples:72→72 / person_month | 36.531977254924925 | 36.531977254924925 | unchanged on the same coordinate/basis |
| shared_multiples:72→72 / api_median_over_hybrid | 1.7007865340568606 | 1.7007865340568606 | unchanged on the same coordinate/basis |
| dedicated_multiples:1728→1728 / person_month | 56.644600000000004 | 56.644600000000004 | unchanged on the same coordinate/basis |
| dedicated_multiples:1728→1728 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| dedicated_multiples:1728→1728 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| dedicated_multiples:1728→1728 / api_median_over_hybrid | 0.09932548534106023 | 0.09932548534106023 | unchanged on the same coordinate/basis |
| shared_multiples:432→432 / person_month | 14.110142873600001 | 14.110142873600001 | unchanged on the same coordinate/basis |
| shared_multiples:432→432 / api_median_over_hybrid | 0.3987381585963178 | 0.3987381585963178 | unchanged on the same coordinate/basis |
| dedicated_multiples:1872→1872 / person_month | 56.644600000000004 | 56.644600000000004 | unchanged on the same coordinate/basis |
| dedicated_multiples:1872→1872 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| dedicated_multiples:1872→1872 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| dedicated_multiples:1872→1872 / api_median_over_hybrid | 0.3973019413642409 | 0.3973019413642409 | unchanged on the same coordinate/basis |
| shared_multiples:468→468 / person_month | 14.110142873600001 | 14.110142873600001 | unchanged on the same coordinate/basis |
| shared_multiples:468→468 / api_median_over_hybrid | 1.5949526343852711 | 1.5949526343852711 | unchanged on the same coordinate/basis |
| dedicated_multiples:2016→2016 / person_month | 56.644600000000004 | 56.644600000000004 | unchanged on the same coordinate/basis |
| dedicated_multiples:2016→2016 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| dedicated_multiples:2016→2016 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| dedicated_multiples:2016→2016 / api_median_over_hybrid | 1.2415685667632528 | 1.2415685667632528 | unchanged on the same coordinate/basis |
| shared_multiples:504→504 / person_month | 14.110142873600001 | 14.110142873600001 | unchanged on the same coordinate/basis |
| shared_multiples:504→504 / api_median_over_hybrid | 4.984226982453973 | 4.984226982453973 | unchanged on the same coordinate/basis |
| api_admission:0→0 / effective_usd_per_1000_calls | 5.504775253207224 | 5.504775253207224 | unchanged on the same coordinate/basis |
| api_admission:24→24 / effective_usd_per_1000_calls | 19.51867419204954 | 19.51867419204954 | unchanged on the same coordinate/basis |
| api_admission:4→4 / effective_usd_per_1000_calls | 1.2129778734675853 | 1.2129778734675853 | unchanged on the same coordinate/basis |
| api_admission:28→28 / effective_usd_per_1000_calls | 5.917437616918841 | 5.917437616918841 | unchanged on the same coordinate/basis |
| api_admission:289→289 / effective_usd_per_1000_calls | 54.7147283 | 54.7147283 | unchanged on the same coordinate/basis |
| api_admission:301→301 / effective_usd_per_1000_calls | 93.58137986999999 | 93.58137986999999 | unchanged on the same coordinate/basis |
| api_admission:364→364 / effective_usd_per_1000_calls | 93.58137986999999 | 93.58137986999999 | unchanged on the same coordinate/basis |
| api_admission:367→367 / effective_usd_per_1000_calls | 95.3506191925 | 95.3506191925 | unchanged on the same coordinate/basis |
| api_admission:427→427 / effective_usd_per_1000_calls | 93.58137986999999 | 93.58137986999999 | unchanged on the same coordinate/basis |
| server_decode_measured:0→0 / streams | 1 | 1 | unchanged on the same coordinate/basis |
| server_decode_measured:0→0 / aggregate_tok_s | 48.7166723842491 | 48.70453006338683 | PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled |
| server_decode_measured:0→0 / gain | 1.0 | 1.0 | unchanged on the same coordinate/basis |
| server_decode_measured:1→1 / streams | 8 | 8 | unchanged on the same coordinate/basis |
| server_decode_measured:1→1 / aggregate_tok_s | 302.9805555126111 | 302.59977133502423 | PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled |
| server_decode_measured:1→1 / gain | 6.21923749477129 | 6.212969736925986 | PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled |
| server_decode_measured:2→2 / streams | 32 | 32 | unchanged on the same coordinate/basis |
| server_decode_measured:2→2 / aggregate_tok_s | 686.7991215323314 | 686.816953541619 | PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled |
| server_decode_measured:2→2 / gain | 14.097824993366846 | 14.101705788922645 | PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled |
| server_decode_measured:3→3 / streams | 39 | 39 | unchanged on the same coordinate/basis |
| server_decode_measured:3→3 / aggregate_tok_s | 738.101276255454 | 737.9342485617974 | PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled |
| server_decode_measured:3→3 / gain | 15.150896810720885 | 15.151244609103262 | PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled |
| link_thresholds:970→1410 / local_prefill_s | 70.52917150992289 | 72.408 | M3 deep local time measured at1.04M; full-slot warm LaCie recovery charged as explicit proxy, not delta-import measurement; PRO1M impossible |
| link_thresholds:970→1410 / import_s | 34.93680903769063 | 40.479 | M3 deep local time measured at1.04M; full-slot warm LaCie recovery charged as explicit proxy, not delta-import measurement; PRO1M impossible |
| decode_ceiling:0→0 / measured_decode_tok_s | 1.67 | 1.6638 | normal-priority1.04M decode replaces background-priority1.67; actual measured depth retained |
| decode_ceiling:0→0 / ceiling_tok_s | 7.415249282896157 | 7.415249282896157 | unchanged on the same coordinate/basis |
| team_break_even:0→0 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:1→1 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:2→2 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:3→3 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4→4 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:10→10 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:11→11 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:12→12 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:13→13 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:14→14 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:360→360 / statement | cheaper from 5 people through 500 scanned people | cheaper from 5 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:361→361 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:362→362 / statement | cheaper from 32 people through 500 scanned people | cheaper from 32 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:363→363 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:364→364 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:370→370 / statement | cheaper from 5 people through 500 scanned people | cheaper from 5 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:371→371 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:372→372 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:373→373 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:374→374 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:720→720 / statement | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:721→721 / statement | cheaper from 74 people through 500 scanned people | cheaper from 74 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:722→722 / statement | cheaper from 4 people through 500 scanned people | cheaper from 4 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:723→723 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:724→724 / statement | cheaper from 45 people through 500 scanned people | cheaper from 45 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:730→730 / statement | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:731→731 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:732→732 / statement | cheaper from 17 people through 500 scanned people | cheaper from 17 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:733→733 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:734→734 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4320→4320 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4321→4321 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4322→4322 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4323→4323 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4324→4324 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4330→4330 / statement | cheaper from 87 people through 500 scanned people | cheaper from 73 people through 500 scanned people | measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged |
| team_break_even:4331→4331 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4332→4332 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4333→4333 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4334→4334 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4680→4680 / statement | cheaper from 4 people through 500 scanned people | cheaper from 4 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:4681→4681 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4682→4682 / statement | cheaper from 19 people through 500 scanned people | cheaper from 19 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:4683→4683 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4684→4684 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4690→4690 / statement | cheaper from 4 people through 500 scanned people | cheaper from 4 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:4691→4691 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4692→4692 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4693→4693 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:4694→4694 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:5040→5040 / statement | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:5041→5041 / statement | cheaper from 32 people through 500 scanned people | cheaper from 32 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:5042→5042 / statement | cheaper from 3 people through 500 scanned people | cheaper from 3 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:5043→5043 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:5044→5044 / statement | cheaper from 30 people through 500 scanned people | cheaper from 30 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:5050→5050 / statement | cheaper from 2 people through 500 scanned people | cheaper from 2 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:5051→5051 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:5052→5052 / statement | cheaper from 8 people through 500 scanned people | cheaper from 8 people through 500 scanned people | unchanged on the same coordinate/basis |
| team_break_even:5053→5053 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| team_break_even:5054→5054 / statement | no sustained crossing through 500 people | no sustained crossing through 500 people | unchanged on the same coordinate/basis |
| quality_evidence:0→0 / ci_high | 0.00039 | 0.00039 | unchanged on the same coordinate/basis |
| quality_evidence:0→0 / ci_low | -0.001076 | -0.001076 | unchanged on the same coordinate/basis |
| quality_evidence:0→0 / local_own_KL | 0.054253 | 0.054253 | unchanged on the same coordinate/basis |
| quality_evidence:0→0 / value | -0.000298 | -0.000298 | unchanged on the same coordinate/basis |
| workload_profiles:0→0 / value | 57744.0 | 57744.0 | unchanged on the same coordinate/basis |
| workload_profiles:1→1 / value | 89042.0 | 89042.0 | unchanged on the same coordinate/basis |
| workload_profiles:2→2 / value | 135362.0 | 135362.0 | unchanged on the same coordinate/basis |
| workload_profiles:3→3 / value | 190258.0 | 190258.0 | unchanged on the same coordinate/basis |
| workload_profiles:4→4 / value | 250202.0 | 250202.0 | unchanged on the same coordinate/basis |
| workload_profiles:5→5 / value | 826234.9 | 826234.9 | unchanged on the same coordinate/basis |
| workload_profiles:6→6 / value | 164437.3 | 164437.3 | unchanged on the same coordinate/basis |
| workload_profiles:7→7 / value | 1524671 | 1524671 | unchanged on the same coordinate/basis |
| workload_profiles:8→8 / value | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| workload_profiles:9→9 / value | 32.0 | 32.0 | unchanged on the same coordinate/basis |
| workload_profiles:10→10 / value | 158.0 | 158.0 | unchanged on the same coordinate/basis |
| workload_profiles:11→11 / value | 805.0 | 805.0 | unchanged on the same coordinate/basis |
| workload_profiles:12→12 / value | 3052.0 | 3052.0 | unchanged on the same coordinate/basis |
| workload_profiles:13→13 / value | 10879.0 | 10879.0 | unchanged on the same coordinate/basis |
| workload_profiles:14→14 / value | 1066.4 | 1066.4 | unchanged on the same coordinate/basis |
| workload_profiles:15→15 / value | 1505761 | 1505761 | unchanged on the same coordinate/basis |
| workload_profiles:16→16 / value | 54.0 | 54.0 | unchanged on the same coordinate/basis |
| workload_profiles:17→17 / value | 113.0 | 113.0 | unchanged on the same coordinate/basis |
| workload_profiles:18→18 / value | 229.0 | 229.0 | unchanged on the same coordinate/basis |
| workload_profiles:19→19 / value | 530.0 | 530.0 | unchanged on the same coordinate/basis |
| workload_profiles:20→20 / value | 1135.0 | 1135.0 | unchanged on the same coordinate/basis |
| workload_profiles:21→21 / value | 4506.0 | 4506.0 | unchanged on the same coordinate/basis |
| workload_profiles:22→22 / value | 511.9 | 511.9 | unchanged on the same coordinate/basis |
| workload_profiles:23→23 / value | 1524671 | 1524671 | unchanged on the same coordinate/basis |
| workload_profiles:24→24 / value | 0.2 | 0.2 | unchanged on the same coordinate/basis |
| workload_profiles:25→25 / value | 3.8 | 3.8 | unchanged on the same coordinate/basis |
| workload_profiles:26→26 / value | 7.8 | 7.8 | unchanged on the same coordinate/basis |
| workload_profiles:27→27 / value | 17.9 | 17.9 | unchanged on the same coordinate/basis |
| workload_profiles:28→28 / value | 34.8 | 34.8 | unchanged on the same coordinate/basis |
| workload_profiles:29→29 / value | 340.0 | 340.0 | unchanged on the same coordinate/basis |
| workload_profiles:30→30 / value | 129.7 | 129.7 | unchanged on the same coordinate/basis |
| workload_profiles:31→31 / value | 1511502 | 1511502 | unchanged on the same coordinate/basis |
| workload_profiles:32→32 / value | 0.21535887833460954 | 0.21535887833460954 | unchanged on the same coordinate/basis |
| workload_profiles:32→32 / value_unit | 1 | 1 | unchanged on the same coordinate/basis |
| workload_profiles:33→33 / value | 84022.0 | 84022.0 | unchanged on the same coordinate/basis |
| workload_profiles:34→34 / value | 124893.0 | 124893.0 | unchanged on the same coordinate/basis |
| workload_profiles:35→35 / value | 212311.0 | 212311.0 | unchanged on the same coordinate/basis |
| workload_profiles:36→36 / value | 431845.0 | 431845.0 | unchanged on the same coordinate/basis |
| workload_profiles:37→37 / value | 720173.2 | 720173.2 | unchanged on the same coordinate/basis |
| workload_profiles:38→38 / value | 940754.7 | 940754.7 | unchanged on the same coordinate/basis |
| workload_profiles:39→39 / value | 307858.2 | 307858.2 | unchanged on the same coordinate/basis |
| workload_profiles:40→40 / value | 285129 | 285129 | unchanged on the same coordinate/basis |
| workload_profiles:41→41 / value | 73.0 | 73.0 | unchanged on the same coordinate/basis |
| workload_profiles:42→42 / value | 154.0 | 154.0 | unchanged on the same coordinate/basis |
| workload_profiles:43→43 / value | 380.0 | 380.0 | unchanged on the same coordinate/basis |
| workload_profiles:44→44 / value | 927.0 | 927.0 | unchanged on the same coordinate/basis |
| workload_profiles:45→45 / value | 2420.0 | 2420.0 | unchanged on the same coordinate/basis |
| workload_profiles:46→46 / value | 10038.0 | 10038.0 | unchanged on the same coordinate/basis |
| workload_profiles:47→47 / value | 1022.3 | 1022.3 | unchanged on the same coordinate/basis |
| workload_profiles:48→48 / value | 281976 | 281976 | unchanged on the same coordinate/basis |
| workload_profiles:49→49 / value | 141.0 | 141.0 | unchanged on the same coordinate/basis |
| workload_profiles:50→50 / value | 211.0 | 211.0 | unchanged on the same coordinate/basis |
| workload_profiles:51→51 / value | 382.0 | 382.0 | unchanged on the same coordinate/basis |
| workload_profiles:52→52 / value | 770.0 | 770.0 | unchanged on the same coordinate/basis |
| workload_profiles:53→53 / value | 1562.0 | 1562.0 | unchanged on the same coordinate/basis |
| workload_profiles:54→54 / value | 6372.9 | 6372.9 | unchanged on the same coordinate/basis |
| workload_profiles:55→55 / value | 762.0 | 762.0 | unchanged on the same coordinate/basis |
| workload_profiles:56→56 / value | 285129 | 285129 | unchanged on the same coordinate/basis |
| workload_profiles:57→57 / value | 3.0 | 3.0 | unchanged on the same coordinate/basis |
| workload_profiles:58→58 / value | 4.5 | 4.5 | unchanged on the same coordinate/basis |
| workload_profiles:59→59 / value | 8.1 | 8.1 | unchanged on the same coordinate/basis |
| workload_profiles:60→60 / value | 18.3 | 18.3 | unchanged on the same coordinate/basis |
| workload_profiles:61→61 / value | 60.6 | 60.6 | unchanged on the same coordinate/basis |
| workload_profiles:62→62 / value | 2177.6 | 2177.6 | unchanged on the same coordinate/basis |
| workload_profiles:63→63 / value | 333.0 | 333.0 | unchanged on the same coordinate/basis |
| workload_profiles:64→64 / value | 282262 | 282262 | unchanged on the same coordinate/basis |
| workload_profiles:65→65 / value | 0.5331836752064005 | 0.5331836752064005 | unchanged on the same coordinate/basis |
| workload_profiles:65→65 / value_unit | 1 | 1 | unchanged on the same coordinate/basis |
| main_economics:0→0 / unit_month | 614.0575 | 614.0575 | unchanged on the same coordinate/basis |
| main_economics:0→0 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:0→0 / own_cluster_boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:0→0 / own_cluster_person_month | 49.1246 | 49.1246 | unchanged on the same coordinate/basis |
| main_economics:0→0 / service_utilization | 0.036139896849339874 | 0.036139896849339874 | unchanged on the same coordinate/basis |
| main_economics:0→0 / calendar_utilization | 0.00831712694614945 | 0.00831712694614945 | unchanged on the same coordinate/basis |
| main_economics:4→4 / unit_month | 1606.0000000000002 | 1606.0000000000002 | unchanged on the same coordinate/basis |
| main_economics:4→4 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:4→4 / own_cluster_boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:4→4 / own_cluster_person_month | 134.67473430118403 | 134.67473430118403 | unchanged on the same coordinate/basis |
| main_economics:4→4 / service_utilization | 0.03377092630959133 | 0.03377092630959133 | unchanged on the same coordinate/basis |
| main_economics:4→4 / calendar_utilization | 0.007771939205494991 | 0.007771939205494991 | unchanged on the same coordinate/basis |
| main_economics:144→144 / unit_month | 614.0575 | 614.0575 | unchanged on the same coordinate/basis |
| main_economics:144→144 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:144→144 / own_cluster_boxes | 11 | 11 | unchanged on the same coordinate/basis |
| main_economics:144→144 / own_cluster_person_month | 135.09265 | 135.09265 | unchanged on the same coordinate/basis |
| main_economics:144→144 / service_utilization | 0.1445595873973595 | 0.1445595873973595 | unchanged on the same coordinate/basis |
| main_economics:144→144 / calendar_utilization | 0.0332685077845978 | 0.0332685077845978 | unchanged on the same coordinate/basis |
| main_economics:148→148 / unit_month | 1606.0000000000002 | 1606.0000000000002 | unchanged on the same coordinate/basis |
| main_economics:148→148 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:148→148 / own_cluster_boxes | 11 | 11 | unchanged on the same coordinate/basis |
| main_economics:148→148 / own_cluster_person_month | 358.82276929945607 | 358.82276929945607 | unchanged on the same coordinate/basis |
| main_economics:148→148 / service_utilization | 0.13508370523836533 | 0.13508370523836533 | unchanged on the same coordinate/basis |
| main_economics:148→148 / calendar_utilization | 0.031087756821979964 | 0.031087756821979964 | unchanged on the same coordinate/basis |
| main_economics:288→288 / unit_month | 614.0575 | 614.0575 | unchanged on the same coordinate/basis |
| main_economics:288→288 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:288→288 / own_cluster_boxes | 27 | 27 | unchanged on the same coordinate/basis |
| main_economics:288→288 / own_cluster_person_month | 331.59105000000005 | 331.59105000000005 | unchanged on the same coordinate/basis |
| main_economics:288→288 / service_utilization | 0.45174871061674843 | 0.45174871061674843 | unchanged on the same coordinate/basis |
| main_economics:288→288 / calendar_utilization | 0.10396408682686811 | 0.10396408682686811 | unchanged on the same coordinate/basis |
| main_economics:292→292 / unit_month | 1606.0000000000002 | 1606.0000000000002 | unchanged on the same coordinate/basis |
| main_economics:292→292 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:292→292 / own_cluster_boxes | 27 | 27 | unchanged on the same coordinate/basis |
| main_economics:292→292 / own_cluster_person_month | 871.1611350097921 | 871.1611350097921 | unchanged on the same coordinate/basis |
| main_economics:292→292 / service_utilization | 0.42213657886989164 | 0.42213657886989164 | unchanged on the same coordinate/basis |
| main_economics:292→292 / calendar_utilization | 0.0971492400686874 | 0.0971492400686874 | unchanged on the same coordinate/basis |
| main_economics:1728→1728 / unit_month | 614.0575 | 614.0575 | unchanged on the same coordinate/basis |
| main_economics:1728→1728 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:1728→1728 / own_cluster_boxes | 5 | 5 | unchanged on the same coordinate/basis |
| main_economics:1728→1728 / own_cluster_person_month | 61.40575 | 61.40575 | unchanged on the same coordinate/basis |
| main_economics:1728→1728 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:1728→1728 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:1732→1732 / unit_month | 1606.0000000000002 | 1606.0000000000002 | unchanged on the same coordinate/basis |
| main_economics:1732→1732 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:1732→1732 / own_cluster_boxes | 5 | 5 | unchanged on the same coordinate/basis |
| main_economics:1732→1732 / own_cluster_person_month | 166.69588215808002 | 166.69588215808002 | unchanged on the same coordinate/basis |
| main_economics:1732→1732 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:1732→1732 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:1872→1872 / unit_month | 614.0575 | 614.0575 | unchanged on the same coordinate/basis |
| main_economics:1872→1872 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:1872→1872 / own_cluster_boxes | 15 | 15 | unchanged on the same coordinate/basis |
| main_economics:1872→1872 / own_cluster_person_month | 184.21724999999998 | 184.21724999999998 | unchanged on the same coordinate/basis |
| main_economics:1872→1872 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:1872→1872 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:1876→1876 / unit_month | 1606.0000000000002 | 1606.0000000000002 | unchanged on the same coordinate/basis |
| main_economics:1876→1876 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:1876→1876 / own_cluster_boxes | 15 | 15 | unchanged on the same coordinate/basis |
| main_economics:1876→1876 / own_cluster_person_month | 486.90736072704004 | 486.90736072704004 | unchanged on the same coordinate/basis |
| main_economics:1876→1876 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:1876→1876 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:2016→2016 / unit_month | 614.0575 | 614.0575 | unchanged on the same coordinate/basis |
| main_economics:2016→2016 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:2016→2016 / own_cluster_boxes | 37 | 37 | unchanged on the same coordinate/basis |
| main_economics:2016→2016 / own_cluster_person_month | 454.40254999999996 | 454.40254999999996 | unchanged on the same coordinate/basis |
| main_economics:2016→2016 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:2016→2016 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:2020→2020 / unit_month | 1606.0000000000002 | 1606.0000000000002 | unchanged on the same coordinate/basis |
| main_economics:2020→2020 / boxes | 4 | 4 | unchanged on the same coordinate/basis |
| main_economics:2020→2020 / own_cluster_boxes | 37 | 37 | unchanged on the same coordinate/basis |
| main_economics:2020→2020 / own_cluster_person_month | 1191.372613578752 | 1191.372613578752 | unchanged on the same coordinate/basis |
| main_economics:2020→2020 / service_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |
| main_economics:2020→2020 / calendar_utilization | 0.0 | 0.0 | unchanged on the same coordinate/basis |

## Validation and limits

Full engine discovery: 543 tests across disjoint 523+20 native-unittest shards, both exit0, no skips; kit:24 tests, exit0; policy controls:15 tests, exit0; artifact and owned-process guard controls:exit0. All 523 prior tests remain present and green; 1014 historical output files are byte-identical. Four narrowing mutants fail their named assertions, each exit1; the mutation audit exits0, with no survivors. CPU only; no downloads/native builds. Numerical and report manifests bind their separate source/test identities.

| Mutant | Bound established | Named failing test |
|---|---|---|
| use_model_at_measurement | exact PRO depth/stream observations override the bandwidth model | `test_measured_pro_point_never_replaced_by_model` |
| admit_pro_million | PRO default-KV1M cannot acquire a feasible resident slot or finite service cost | `test_pro_million_server_cannot_be_feasible` |
| double_restore | measured prefill excludes recovery; the charged full-slot restore enters the remote path exactly once | `test_mac_prefill_refuses_double_restore_with_measured_threshold_control` |
| hide_zero_offload | both sentence forms disclose zero-prefill-offload economics rather than claim an offload gain | `test_zero_offload_sentence_refuses_missing_disclosure_with_control` |

Attempt history is retained: the first 50-person preflight (smoke01) failed on a structured capacity-alarm fraction being converted to float; corrected before publication, with a named alarm-versus-zero regression. Policy controls01 through05 all exited0 on their successive recorded source identities; mutation witnesses were rerun on the frozen production identity. The 50-person smoke02 and its rendered reports are preflight only, superseded by the 500-person production export01; they cannot establish sustained crossings through500. A later report-smoke04 exited2 because its scratch runner path used an underscore instead of the existing hyphen; the corrected report-smoke05 exited0. A final self-review found that generic export-health status hid native Mac benchmark disposition; a bounded metadata re-export adds measurement_status and removes its duplicate health header. It preserves every original Mac cell and every other calculation payload byte, retaining the completed calculation identity separately. The mathematical sources/data are unchanged; the new published-read-path regression refuses a fabricated measured status at the context-refused shape. The first draft validation receipt exited1 because a temporary discovery typo left its case-ID file absent; discovery01 and the next validation draft corrected that setup failure. The unrestricted staged style check initially exited2 for nine report sentence trailing spaces; publication now trims only their rendered whitespace while preserving exact source values in the quote ledger. No failed attempt is counted as passing evidence.

Observed minimum free disk 31114674176 bytes (28.977798GiB), above the28GiB floor. Gate launches require28.5GiB; task-owned PID/start-identity guards pause only their own process trees and stop after a20-minute hold. Disk samples and gate/environment receipts are retained; only own superseded 50-person preflight CSV payloads were removed after preserving their byte hashes; no foreign process or data cleanup was performed.

No new GPU/Mac run, model download or native build was performed. Unmeasured B300 decode/deep prefill, deeper PRO decode, delta-import portability, workload reconstruction/correlations and shared-provider assumptions remain open. Raw/cold LaCie performance and an end-to-end bf16 hybrid at 1M are not established by these measurements. Original R16b and Glimmer/Gemma PRI31 interfaces remain intact. No attack-surface table was supplied (brief gap); new measurements/API cache certification and a proof of minimal fleets are out of contract.
