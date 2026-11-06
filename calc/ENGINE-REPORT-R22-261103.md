# Engine run22 — RC4 bounds and accepted measurements

Base: `b6316e8a12c47526c9815cc08ebc6de78eec162b`, independently accepted by Muse r5x3. No findings remained. Run22 adopts its generated, humanized short-form advice; the canonical and short quotations share row-bound validators. Runs13–21 and their generators are unchanged.

The headline basis is a dedicated team server, bought in the office or rented for 730 calendar hours/month. Shared resident work is a supplementary provider/full-utilization limit. The authors operate a shared prefill service, so its allocation is not the headline. Costs below are the open-model component per person-month, with the stated client/front costs; all alternatives use the same selected call shapes.

## bf16 default and measured quality

Qwen transports 78,446,592 recurrent bytes by default; 156,893,184 bytes remains the adjacent f32 control. Resident state remains f32: capacity and decode traffic do not halve. Measured f32 Mac import seconds are reused in both transport arms; bf16 import acceleration is not assumed.

The accepted KL study gives bf16 minus local −0.000298 nats, 95% interval [−0.001076,+0.000390], against the client’s own 0.054253 nats. The interval contains zero; this is not a universal equivalence claim. The archived paired RULER analyses report:

| Arm | Equal paired scores | Changed answers against local |
|---|---:|---:|
| bf16 RULER8192 | 390/390 | 28 |
| bf16 RULER32768 | 390/390 | 33 |

The RULER block arrived in FACTS during this run; primary analyses are now source-bound in `calc/run22/data/`. Equality of scores does not mean answer identity or 100% accuracy. These homogeneous CUDA results do not close the heterogeneous vLLM-to-Metal calibration item.

## 1M routing: anchored primary value, 120-second sensitivity

At 1M, Δ690, B300 FP8 with FP8 KV and the measured historical 5.19 MB/s home Wi-Fi profile:

| Transport / local basis | Wire MB | Transfer s | Threshold MB/s | Offload |
|---|---:|---:|---:|---|
| bf16 / anchored extension | 102.470 | 19.744 | 2.992 | True |
| bf16 / 120s estimate | 102.470 | 19.744 | 1.224 | True |
| f32 / anchored extension | 180.916 | 34.859 | 5.283 | False |
| f32 / 120s estimate | 180.916 | 34.859 | 2.161 | True |

The primary local delta time is a FLOP-efficiency extension of measured M3 PRI31 anchors, not a direct 1M measurement. The original f32 anchored threshold 5.283 MB/s survives; only transport changes its bf16 counterpart. Both the local 1M rate and the Mac import-depth slope remain estimates. The analyst 120s local turn is separate. PRO6000 default-KV 1M capacity refuses; B300 variants are capacity-checked.

All office/WAN/Wi-Fi rows, including 0.798/2.805 MB/s today, 5.19/9.75 MB/s historically and 5.18 MB/s end-to-end slot acquisition, are in `link_thresholds.csv`. The 5.18 MB/s observation included hashing/assembly, not pure wire throughput. Direct restored 1.04M Δ690/2000/10000 observations have their own pending table and CSV interface; they are never renamed measured 1M rates. A slot restore is never substituted for delta import.

## Coverage is about call shapes

| Profile / selected envelope | Measured-shape calls / source calls | Selected calls / source calls |
|---|---:|---:|
| existing_combined / measured_ladder | 10885/39904 (27.28%) | 10885/39904 (27.28%) |
| existing_combined / physical_extended | 10885/39904 (27.28%) | 39788/39904 (99.71%) |
| claude_deep / measured_ladder | 554/1000 (55.40%) | 554/1000 (55.40%) |
| claude_deep / physical_extended | 554/1000 (55.40%) | 985/1000 (98.50%) |

Measured coverage means the share of calls whose depth/delta/end shapes lie inside the common measured ladder, normalized to each stated calls/person-month. It is not a share of the total workload or token mass. The combined measured subset retains the same 10,885/39,904 call shapes as R20; the explicit 16k lower bound excludes none of them. Physical-envelope fractions include extrapolated deep rates and must not be called measured coverage. Neither table prices the full unconditioned source mix.

The original seeded combined workload is unchanged. The Claude profile remains a quantile/mean reconstruction with conditional mean deltas and independently permuted output/pause ranks, not raw replay. Published Claude pauses are median 8.1 s / p90 60.6 s; the combined p90 is 34.8 s. The active 300 s gap cap and lost correlations remain assumptions.

## Dedicated PRO6000 small teams — primary selection

Bought office PRO6000 vLLM FP8, 125 MB/s and 1 ms assumed; owned M5 Max 64 GB at recorded PRI31; s=20%; bf16; owner 98.1% cache allowance with 1.9% billed misses. Combined measured-shape subset 10,885/39,904 (27.28%), normalized separately per demanded person-month. Light/medium are typical; heavy 2500 calls/day is the owner’s own intensity.

| Load | People | Hybrid $/person-month | Service occupancy | Calendar occupancy | Same-server own cluster $/person-month | Own-cluster service / calendar occupancy |
|---|---:|---:|---:|---:|---:|---:|
| light | 3 | 212.21 | 0.98% | 0.22% | 204.69 | 10.13% / 2.33% |
| light | 5 | 130.33 | 1.55% | 0.36% | 122.81 | 18.53% / 4.26% |
| light | 10 | 68.93 | 2.93% | 0.67% | 61.41 | 39.55% / 9.10% |
| light | 20 | 68.93 | 2.93% | 0.67% | 61.41 | 39.55% / 9.10% |
| medium | 3 | 212.21 | 3.91% | 0.90% | 204.69 | 40.53% / 9.33% |
| medium | 5 | 130.33 | 6.19% | 1.42% | 245.62 | 32.17% / 7.40% |
| medium | 10 | 68.93 | 11.73% | 2.70% | 184.22 | 46.11% / 10.61% |
| medium | 20 | 68.93 | 11.73% | 2.70% | 153.51 | 57.30% / 13.19% |
| heavy | 3 | 212.21 | 12.21% | 2.81% | 409.37 | 48.78% / 11.23% |
| heavy | 5 | 130.33 | 19.34% | 4.45% | 368.43 | 57.34% / 13.20% |
| heavy | 10 | 68.93 | 36.65% | 8.43% | 368.43 | 57.34% / 13.20% |
| heavy | 20 | 68.93 | 36.65% | 8.43% | 337.73 | 65.13% / 14.99% |

Service occupancy divides modelled allocated-GPU work by installed 8h/day GPU time; calendar occupancy uses 730h/month. Decode’s tool/concurrency bound is included, so neither is hardware SM utilization. Hybrid integer fleets are sufficient, not proved minimal. Every dedicated cost row carries utilization, including the own-cluster comparator. Rented nodes pay the full calendar, office nodes the whole bought chassis. Rented hybrid egress uses the retained USD per decimal TB tariff; office egress is zero.

## Price of idleness and conditional multiples

| Profile / load, team50 | Dedicated cost | Service / calendar occupancy | Median API / dedicated hybrid | Shared-work cost | Median API / shared hybrid |
|---|---:|---:|---:|---:|---:|
| existing_combined / light | 56.64 | 3.61% / 0.83% | 0.088 | 15.90 | 0.313 |
| existing_combined / medium | 56.64 | 14.46% / 3.33% | 0.351 | 21.29 | 0.934 |
| existing_combined / heavy | 56.64 | 45.17% / 10.40% | 1.097 | 36.53 | 1.701 |
| claude_deep / light | 56.64 | 0.00% / 0.00% | 0.099 | 14.11 | 0.399 |
| claude_deep / medium | 56.64 | 0.00% / 0.00% | 0.397 | 14.11 | 1.595 |
| claude_deep / heavy | 56.64 | 0.00% / 0.00% | 1.242 | 14.11 | 4.984 |

The dedicated office link is 125 MB/s / 1 ms; the shared provider limit uses engine WAN 112.5 MB/s / 400 ms. `idleness.csv` additionally aligns both sides to the office link and shows the dedicated-minus-shared cost difference against 70%-allocation and 100%-utilization limits. That contrast also changes bought versus rental tariffs, residency, storage and pooled batching: it is not a pure causal measurement of idle cost. Paying the full idle calendar/chassis is explicit. Night agents on autopilot can raise utilization, but their sustained demand is an assumption.

## API bounds, no cache verdict

Admission excludes context impossibility, no declared cache, or availability below 95% in the chosen common window. Low/zero measured cache hit rates are priced, never excluded. Missing tariff data makes an admitted endpoint unpriceable, not impossible. The exploratory Chutes three-call probe is not an input; series warm-up includes a first miss.

| Main measured-shape API point | Cheapest admitted provider | $/1000 calls | Median admitted provider | $/1000 calls |
|---|---|---:|---|---:|
| no_cache | darkbloom/fp4 | 5.505 | tenstorrent/fp4 | 19.519 |
| owner_981 | chutes/fp8 | 1.213 | deepinfra/bf16 | 5.917 |
| Measured cache rate | Pending | Pending | Pending | Pending |

No-cache means zero cached input tokens; misses use declared cache-write or base-input tariffs, including Alibaba’s explicit write tariff. The 98.1% point is the hash-bound owner commercial aggregate, not a Chutes/provider measurement. API input billing preserves previous generated output at the original call-group boundaries before subsetting. Partial cache observations price individual endpoints but cannot establish the cheapest/median over an incompletely measured cohort.

Availability uses the snapshot’s last1d field uniformly, rather than a minimum over 5m/30m/1d. Exact snapshot interval endpoints were not retained. A measured common-window CSV replaces this comparison cohort; no snapshot backfill is mixed into its missing provider observations.

| 1M owner 98.1% allowance / availability cohort | Cheapest | $/1000 calls | Median | $/1000 calls |
|---|---|---:|---|---:|
| snapshot_1d | phala | 54.715 | novita | 93.581 |
| analyst_72h_with_alibaba | novita | 93.581 | alibaba | 95.351 |
| analyst_72h_without_alibaba | novita | 93.581 | novita | 93.581 |

The fixed 1M API task reserves 690 new and 762 generated tokens inside its advertised 1,000,000 total window, as R21 did; mean billed input is 999,238 tokens. The owner-reported analyst 72h scenario has Phala 86% and Alibaba 96%; other providers and exact endpoints are unverified. Snapshot last1d Alibaba is 87.464%, so the window changes admission. The separate without-Alibaba cohort is an explicit sensitivity, not an additional impossibility rule. Hybrid Qwen uses model-card YaRN factor 4; API extension methods are unknown, and identical YaRN is not claimed. Historical GLM/Ultra projections remain unmeasured; this run does not promote them to new measurements.

## Words-ready conclusions

The following are generated short forms, with the canonical row in the same table. Own-cluster crossings compare the same server/engine/billing; no claim substitutes an expensive cluster for a cheaper one without naming that basis. All crosses are sustained strict improvements through 500 scanned people, not the first favourable fleet step.

- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 5 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 2 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 45 people through 500 scanned people versus median admitted API (deepinfra/bf16). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Bought office server (125 MB/s, RTT 1 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus own vLLM cluster on the same server and billing basis. Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, light load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 200 calls/day (typical light load); call shapes inside measured ladder 10885/39904 (27.28%) at 840 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 5 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, medium load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 800 calls/day (typical medium load); call shapes inside measured ladder 10885/39904 (27.28%) at 3360 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: cheaper from 2 people through 500 scanned people versus own vLLM cluster on the same server and billing basis. Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus median admitted API (deepinfra/bf16). Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.
- Combined-agent measured-shape subset, heavy load: RTX PRO 6000 vLLM FP8 hybrid: no sustained crossing through 500 people versus cheapest admitted API (chutes/fp8). Rented WAN server (112.5 MB/s, RTT 400 ms); M5 Max 64 GB owned; s=0.2; 98.1% cache allowance (1.9% misses billed, provider unverified); 2500 calls/day (owner intensity2500 calls/day, atypical; light/medium are typical); call shapes inside measured ladder 10885/39904 (27.28%) at 10500 calls/person-month, full unconditioned mix unsupported; bf16 default transport; dedicated fleet sufficient, not minimal. API: snapshot29 Oct last1d, >=95% (exact window endpoints unknown). PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.

The old “heavy is cheaper at any team size” claim was withdrawn because the own cluster was recalculated on vLLM; under vLLM prices it held only for a 5090 hybrid, which the owner excluded. A second Mac is not the explanation. `heavy_sensitivity.csv` gives one alternative: move generation to the team’s own vLLM server, using its matched own-cluster cost/occupancy bound. Heavy 2500 calls/day is the owner’s intensity; light and medium are typical.

## Accepted Mac measurements and resync

The new M5 Max 64 GB kit 1.6.7 archives match full SHA256s 1d0d04a372d56ef553565292d12ae10dd58357fad71d53f9f7ccd28e0d44704c and 89211edd6348d026724769bc0de46933f582856b6c36bf33a04d4454b2709f9f. Recorded server samples are PRI31 / nice 0, with no overrides. Readiness arrays contain 35 Qwen and 30 Glimmer samples, versus 36/31 in FACTS; the archived counts govern. M5 Max 128 GB uses the 64 GB same-SoC curves as a labelled portability estimate.

Qwen’s measured best batching gains are 2.715/2.024/1.284 at 32768/65536/131072; Glimmer’s 3.236/2.660/2.363 at 32768/65536/129024. Raw depth-specific ladders, 260k Qwen 1/2-stream decode, 129k Glimmer and agent-loop medians/tails are published in `client_measurements.csv`. Agent-loop 8h call counts are projections of those small measured rounds, not a substitute for the economics’ differently shaped workload. Pure parallel decode and agent-loop scheduling are separate protocols. Server decode is measured only at 16384 on the PRO6000; deeper points and the B300 remain modelled until their CSV data arrive.

## Accepted PRO 6000 server decode point

The accepted kit 1.6.9 observation is at the actual depth of 16,384 tokens, with default KV. Values below are three-round medians of the common decode interval, using private prefixes and salts per session. The measured resident limit is 39 sessions; 40 did not fit. This limit applies at the observed depth. Deeper points remain modelled pending kit 1.6.11; the separate model grid at 16,000 tokens is not relabelled as measured.

| Streams | Aggregate tok/s | Gain against one stream |
|---|---:|---:|
| 1 | 48.72 | 1.00 |
| 8 | 302.98 | 6.22 |
| 32 | 686.80 | 14.10 |
| 39 | 738.10 | 15.15 |

The measured point enters through `server_decode.csv`, with its retained receipt and source SHA256. Own-cluster economics use it only where depth and stream count are supported. Continuous workload depths elsewhere retain the bandwidth model; this one anchor does not make the whole cost table measured.

M3 Max Glimmer now uses the accepted PRI31 FACTS transcription, including actual successive-turn start offsets; the incident archive is still unavailable on this host. Its rounded values are not claimed archive-verified. SWA reuses the Qwen Mac import-cost fit as an unmeasured portability assumption.

The PRO6000 ServerEdition llama.cpp cold fill to 1,040,000 was 518.29+1295.48=1813.77 s (30.2 min), with a measured f32 slot 36,394,654,776 bytes. `full_resync.csv` uses these values. The bf16 full-slot payload is a labelled casting/container estimate; server restore 3.14 s is not Mac import. This does not become a measured vLLM cold rebuild. The M3 Max 1M bandwidth ceiling remains 7.415 tok/s against 1.67 at 1.04M measured at background priority; the gap is open.

## Interfaces and limits

The provenance CSV carries the accepted PRO 6000 default-KV point at 16,384 tokens. Interfaces remain open for deeper/B300 decode, 512k/1M prefill, provider cache/availability, and restored-slot Mac prefill/import/logits/decode. Empty cells mean pending, never zero. The R16b and Glimmer/Gemma PRI31 JSON interfaces remain unchanged. No 5090 server rows enter paper exports; the historical 5090 client remains supported. The complete commands and CSV contracts are in `calc/run22/README.md`.

No new GPU/Mac measurements, downloads or native builds were run. Hardware service rates beyond measured ladders, uniform session retention/miss modelling, deep Mac import, and vLLM decode traffic/efficiency remain assumptions. Physical-extension and shared-provider rows bound applicability rather than establish deployable service offers. No supplied attack-surface table was present (brief gap); out of contract are new measurements, API cache/availability certification and heterogeneous quality calibration.

## Validation

Full engine discovery: 523 tests across disjoint 495+28 native-unittest shards, both exit0; kit:24 tests, exit0; policy controls:24 tests, exit0; artifact and guard controls:exit0. All 495 prior tests remain present and green; 987 historical output files are byte-identical. CPU only; no downloads/native builds. Numerical and report manifests bind their separate source/test identities.

Six process-local narrowing faults were killed by named assertion failures; controls passed. Expected-red mutant exits are 1, never labelled green:

| Mutant | Gate narrowed to | Named failing test |
|---|---|---|
| force_f32 | bf16 is the default wire tensor; resident state remains f32 | `test_bf16_default_refuses_unknown_and_preserves_f32_residency` |
| three_call_cache | an exploratory three-call series cannot establish provider cache performance | `test_low_cache_is_priced_not_excluded_and_three_call_probe_refused` |
| mixed_window | all provider availability observations share the same stated interval | `test_availability_refuses_mixed_windows_with_same_window_control` |
| infer_link | each sentence carries its own server location, rate and RTT | `test_words_ready_refuses_missing_link_with_long_and_short_controls` |
| flat_server_decode | modelled server batching falls with per-session KV traffic at depth | `test_server_decode_refuses_flat_gain_with_capacity_control` |
| copy_16k_to_deep | the measured16384 point does not become a64k observation | `test_pro16k_measurement_refuses_deep_reuse_and_capacity_overrun` |

No surviving mutants. Report-only publication adds this report, a coordinate/rendering ledger and a separate manifest; numerical CSV payloads remain the exact exporter output. The main quote ledger covers sentence surfaces and declared quantitative/cost columns; this report ledger additionally covers every quoted API/cost/coverage coordinate. Both are verified against source cells.

Earlier attempts remain disclosed: focused01/policy02 had draft-fixture or not-yet-exported-artifact failures, corrected against primary evidence; resumed controls-positive02 used an invalid expected failure at a memory-clamped unmeasured batch, corrected to the supported 8-stream witness. Report-smoke01 found a string/float link selector, corrected before publication. Export01/02/03/04 were explicitly stopped by own recorded PIDs (actual exit−15) for newly accepted quality evidence, API context/billing self-review, CSV boundary validation, and an egress USD/TB correction respectively; none is green. Egress-unit-red01 reproduced the 1000x overcharge before correction; its paired dedicated/shared control now passes. Boundary-negative-red01 had the two intended assertion failures before the fixes. Export05 is the sole accepted production generation. Unrestricted git diff --cached --check exits2 solely for trailing blank lines in three verbatim FACTS excerpts; those source-bound bytes are intentionally retained, and the code/output-scope whitespace check exits0. Old receipts are retained separately from passing evidence.

Observed minimum free disk: 32384802816 bytes (30.161 GiB), above the 28 GiB floor; launch hold 28.5 GiB, task-owned PID/start-identity guards, disk-backed TMPDIR and PYTHONDONTWRITEBYTECODE=1. No foreign cleanup or process control. Observer samples do not claim continuous telemetry across the model-capacity interruption.
