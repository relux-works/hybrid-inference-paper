# Engine run12: server at the measured llama.cpp rate

Run `hybrid-calc-r12-261101`; immutable design baseline `a57db67` (run11). This is a labelled sensitivity, not a replacement for run11. All 42 original chart CSVs, 32 sidecars and 15 files under `paper/` (89 files total) are preserved byte for byte. No paper text is edited.

With existing Macs, the design hosting policy costs $33.41–39.52/person-month at 20% open share and $65.33–174.94 with median-API overflow at 50%. The median API is still more expensive; the cheapest API is still cheaper. Two bought-device cases reverse against the median API. At 20 people, the selected light-load all-server perimeter rises $36.20→$63.24/person-month. M3 cash payback against median API grows 47.05→56.33 months at 20% share and 37.05→44.19 at 50%. GLM 1M cold ingest plus transfer grows 97.41→225.02 s; integer fleet costs can stay flat.

## Input, fit and transfer basis

Only the hash-verified kit archive is imported under `data/measurements/vast-2026-11-01/qwen27b-gpu-bench/results/`, plus its provenance README. The archive SHA-256 is `9accab80ed21dfa24714d5e11b16d31e0106419cd13c3fd27123528949673661`; all 37 manifest-listed payload files verify, plus the manifest itself. Vast rented RTX PRO 6000 Blackwell Workstation Edition, 600 W; Ryzen 9 9950X; driver 595.71.05; CUDA 12.8; GPU kit 1.2.0, bench e5f64d2; llama.cpp c21284cdf / b11087; Qwen3.8-27B Q4_K_M, q8_0 KV, flash attention. This run executes no inference or builds.

Twelve equally weighted observations fit **seconds/token = a + b × nominal depth**, using exact `prompt_ms/1000/prompt_n` from both Δ2000 and Δ10000. `a=0.0003687230031301119` s/token; `b=6.065719692011435e-09` s/token/depth-token. The six labelled depths are the fit coordinates. Actual starts are 640 tokens later for Δ2000 and 2768 later for Δ10000, preserved in `SERVER-FIT-R12-261101.csv`. Fills and 512-token turns are excluded from fitting. The fit does not model the 512-turn overhead and may be optimistic for small portions.

Per-call prefill retains the engine’s marginal-depth convention: `n × (a+bD)`; all-call shadow uses `(n+output) × (a+bD)`. Cold fills/large spans integrate: `aN + b(DN+N²/2)`. Beyond 249k and below 16k the same affine seconds/token curve continues without clamping, so fills grow quadratically and effective FLOP efficiency falls with depth. This is extrapolation, not a measured native 1M incremental curve or a quality check. In the unchanged fitted call sample, 10.18% of calls (8.10% of input+output tokens) start beyond 249k; 87.27% of calls have input portions below 2k (those calls carry 44.77% of input+output tokens). The bulk curve therefore does not qualify short-call overhead for much of the call count. The 1040000 fill uses YaRN x4.

Bulk residual below is 100 ×(predicted seconds/observed seconds−1); the named test requires absolute residual<2% for each of 12 points. Independent held-out fill tolerance is15%; these are validation bounds on this run, not statistical confidence intervals.

| Nominal depth | ObservedΔ2k tok/s | ObservedΔ10k tok/s | Fit tok/s | ResidualΔ2k | ResidualΔ10k |
| --- | --- | --- | --- | --- | --- |
| 16000 | 2147.31 | 2140.86 | 2146.96 | 0.02% | -0.28% |
| 50000 | 1503.83 | 1476.13 | 1488.08 | 1.06% | -0.80% |
| 100000 | 1032.39 | 1017.79 | 1025.33 | 0.69% | -0.74% |
| 150000 | 785.39 | 780.15 | 782.12 | 0.42% | -0.25% |
| 200000 | 631.84 | 631.24 | 632.16 | -0.05% | -0.15% |
| 249000 | 533.03 | 531.66 | 532.17 | 0.16% | -0.10% |


| Held-out fill tokens | Observed prompt seconds | Predicted seconds | Residual |
| --- | --- | --- | --- |
| 1040000 | 3633.85 | 3663.81 | 0.82% |
| 131072 | 88.95 | 100.43 | 12.91% |
| 260000 | 286.99 | 300.89 | 4.84% |


The raw archive records 88.954 s at 131072, 286.993 s at 260000 and 3633.845 s at 1040000. These take precedence over the brief’s rounded ≈90/294 s/61 min; slot-save time is excluded. The fit overpredicts the131k held-out fill time by 12.91%, a material limit of this simple bulk-turn curve.

All owned RTX PRO 6000 variants (rack, colocation, office, hourly reference) use this curve per GPU and keep their existing GPU counts and shard efficiencies. Applying a workstation observation to Server Edition hosts is a portability estimate, not another measurement. B300 shared service and owned 8-GPU nodes use `C_B300(D) = C_RTX(D) × (4.5e15/1.0076e15)`, where `C_RTX(D)=F_Qwen(D)/(a+bD)`. Thus each depth inherits the observed fraction of FP8 dense peak. For GLM, its own FLOPs are divided by this inferred envelope: both cross-device and cross-model portability are explicit estimates; GLM was not benchmarked.

FP16 comparison: the engine’s RTX dense peak is 503.8 TFLOP/s and B300 is 2250 TFLOP/s, exactly half their FP8 peaks. Measured utilization doubles if expressed on the FP16 basis, but transferring the same FP16 fraction gives exactly the same B300 rate. FP8 is used to retain the engine’s existing denominator. Keeping the *FP8* fraction but multiplying only by the FP16 B300 peak would mix denominators; it is not the alternative estimate used here. No claim is made that Q4 kernels execute at FP8 precision. The measured same-weights llama.cpp path is the available Q4 server evidence. Run11 retains its design throughput assumption; reaching FP8-class rates needs faster same-weights kernels or the heterogeneous-precision mode that remains awaiting verification.

Decode kernels/rates, hosting equations and parameters, prices, capacity/memory geometry, and decision policies remain unchanged. Decisions, pending-work amounts, transferred bytes, host migration charges, API overflow and integer fleets are recomputed from the slower prefill; these consequences can change. H100/L40S and historical bridge/legacy paths keep their original assumptions.

| Depth | RTX fraction of FP8 peak, observedΔ2k/Δ10k | Same fraction on FP16 basis | B300 estimateΔ2k/Δ10k tok/s |
| --- | --- | --- | --- |
| 16000 | 12.85% / 12.81% | 25.70% / 25.62% | 9590.02 / 9561.22 |
| 50000 | 10.99% / 10.79% | 21.99% / 21.58% | 6716.18 / 6592.49 |
| 100000 | 9.56% / 9.43% | 19.12% / 18.85% | 4610.73 / 4545.51 |
| 150000 | 8.81% / 8.75% | 17.61% / 17.50% | 3507.58 / 3484.20 |
| 200000 | 8.32% / 8.31% | 16.64% / 16.62% | 2821.84 / 2819.17 |
| 249000 | 8.04% / 8.02% | 16.07% / 16.03% | 2380.56 / 2374.42 |


## Per-client economics and share

USD/person-month for 2500 calls/day, 21 days, team 50 (the shared-service person cost is team-independent). s20 requests 500 open calls/day; s50 requests 1250. API baselines are unchanged: median 101.66586/254.16465, cheapest 14.09675/35.24187 at s20/s50. Each cell is run11→measured-server. Hybrid includes overflow to the named API. Studios use full purchase cost in the bought basis; laptop premium subtracts the baseline laptop credit.

| Hosting | Share | Client | Owned vs median | Owned vs cheapest | Bought vs median | Bought vs cheapest |
| --- | --- | --- | --- | --- | --- | --- |
| design | s20 | M3 Max 128 GB (measured) | 27.26 → 39.52 | 27.26 → 39.52 | 74.67 → 86.93 | 74.67 → 86.93 |
| design | s20 | M4 Max 128 GB (estimate) | 25.82 → 37.95 | 25.82 → 37.95 | 73.22 → 85.35 | 73.22 → 85.35 |
| design | s20 | M5 Max 64 GB | 25.18 → 37.03 | 24.07 → 35.93 | 60.38 → 72.24 | 59.28 → 71.14 |
| design | s20 | M5 Max 128 GB | 24.10 → 36.12 | 24.10 → 36.12 | 80.97 → 93.00 | 80.97 → 93.00 |
| design | s20 | M5 Ultra 96 GB | 22.60 → 34.25 | 22.60 → 34.25 | 97.07 → 108.71 | 97.07 → 108.71 |
| design | s20 | M5 Ultra 256 GB | 21.99 → 33.41 | 21.99 → 33.41 | 168.23 → 179.64 | 168.23 → 179.64 |
| design | s50 | M3 Max 128 GB (measured) | 159.68 → 174.94 | 48.65 → 63.72 | 207.09 → 222.35 | 96.06 → 111.13 |
| design | s50 | M4 Max 128 GB (estimate) | 119.66 → 140.18 | 46.70 → 66.88 | 167.05 → 187.58 | 94.10 → 114.28 |
| design | s50 | M5 Max 64 GB | 109.54 → 130.99 | 43.60 → 64.52 | 144.75 → 166.20 | 78.81 → 99.73 |
| design | s50 | M5 Max 128 GB | 98.63 → 121.50 | 43.40 → 65.83 | 155.50 → 178.38 | 100.28 → 122.70 |
| design | s50 | M5 Ultra 96 GB | 38.31 → 67.44 | 38.31 → 67.44 | 112.78 → 141.90 | 112.78 → 141.90 |
| design | s50 | M5 Ultra 256 GB | 36.80 → 65.33 | 36.80 → 65.33 | 183.04 → 211.57 | 183.04 → 211.57 |
| conservative | s20 | M3 Max 128 GB (measured) | 36.30 → 48.72 | 36.30 → 48.72 | 83.70 → 96.13 | 83.70 → 96.13 |
| conservative | s20 | M4 Max 128 GB (estimate) | 35.39 → 47.80 | 35.39 → 47.80 | 82.78 → 95.20 | 82.78 → 95.20 |
| conservative | s20 | M5 Max 64 GB | 35.27 → 47.49 | 34.16 → 46.38 | 70.47 → 82.70 | 69.37 → 81.59 |
| conservative | s20 | M5 Max 128 GB | 34.30 → 46.69 | 34.30 → 46.69 | 91.18 → 103.57 | 91.18 → 103.57 |
| conservative | s20 | M5 Ultra 96 GB | 33.40 → 45.71 | 33.40 → 45.71 | 107.86 → 120.18 | 107.86 → 120.18 |
| conservative | s20 | M5 Ultra 256 GB | 32.98 → 45.30 | 32.98 → 45.30 | 179.22 → 191.54 | 179.22 → 191.54 |
| conservative | s50 | M3 Max 128 GB (measured) | 169.10 → 184.51 | 58.09 → 73.39 | 216.51 → 231.92 | 105.50 → 120.80 |
| conservative | s50 | M4 Max 128 GB (estimate) | 130.70 → 151.58 | 57.79 → 78.46 | 178.09 → 198.98 | 105.19 → 125.85 |
| conservative | s50 | M5 Max 64 GB | 121.78 → 143.70 | 55.91 → 77.50 | 156.99 → 178.91 | 91.12 → 112.71 |
| conservative | s50 | M5 Max 128 GB | 111.30 → 134.71 | 56.14 → 79.28 | 168.18 → 191.58 | 113.02 → 136.16 |
| conservative | s50 | M5 Ultra 96 GB | 54.39 → 85.18 | 54.39 → 85.18 | 128.85 → 159.64 | 128.85 → 159.64 |
| conservative | s50 | M5 Ultra 256 GB | 53.36 → 84.15 | 53.36 → 84.15 | 199.59 → 230.39 | 199.59 → 230.39 |


Across all six clients with already-owned devices, both policies and both shares still beat the median API and lose to the cheapest API. At s20, bought Ultra 96 under design hosting flips from $97.07<$101.67 to $108.71>$101.67; under conservative hosting, bought M5 Max 128 flips from $91.18 to $103.57. Both are reversals against the median API. Costs are flat by team in these shared-service rows, so each flip repeats over all six teams. Cheapest-API direction stays unchanged.

Exact savings percentages, API/hybrid ratios and all per-client served/overflow/capacity values are in `ENGINE-QUOTES-R12-261101.csv`; the complete numeric cell comparison is `ENGINE-CHANGES-R12-261101.csv`. The quote inventory reuses run11’s named claim definitions and adds every numeric GLM, people/GPU and timing cell. The checked-in manuscript is still a placeholder with no abstract/economics/million-token/conclusion body, so quote coverage is tied to that persisted run11 inventory plus all 42 chart tables, rather than an unavailable newer manuscript.

## Closed perimeter: load and team

All calls stay inside the owned perimeter, without API fallback. The all-server column shows the selected integer fleet. Hybrid ranges span all eligible, fully served rows over six clients, separately by existing/bought device basis. Rows with unserved calls or alarms do not enter a range. Unit means a purchasable server; rack2 has two GPUs and B300_node eight. Each cell is run11→sensitivity.

| Hosting | Load | People | Selected all-server$/person-month | Units | Hybrid owned range | Hybrid bought range |
| --- | --- | --- | --- | --- | --- | --- |
| design | light | 5 | 144.81 → 144.81 | 1 → 1 | 156.85–265.04 → 156.85–265.04 | 200.18–445.02 → 200.18–445.02 |
| design | light | 10 | 72.41 → 72.41 | 1 → 1 | 84.44–138.56 → 84.44–138.56 | 127.77–318.55 → 127.77–318.55 |
| design | light | 20 | 36.20 → 63.24 | 1 → 1 | 48.24–75.32 → 48.24–75.32 | 91.57–255.31 → 91.57–255.31 |
| design | light | 50 | 43.44 → 43.44 | 3 → 3 | 26.52–349.10 → 26.57–349.10 | 69.85–529.08 → 80.66–529.08 |
| design | light | 500 | 33.70 → 33.70 | 1 → 1 | 45.74–45.79 → 45.74–45.79 | 89.07–225.77 → 89.07–225.77 |
| design | light | 5000 | 26.96 → 30.33 | 8 → 9 | 18.77–18.82 → 22.19–25.57 | 62.11–198.81 → 68.85–202.18 |
| design | medium | 5 | 144.81 → 252.96 | 1 → 1 | 156.85–265.04 → 156.85–265.04 | 200.18–445.02 → 200.18–445.02 |
| design | medium | 10 | 144.81 → 217.22 | 2 → 3 | 84.44–138.56 → 84.44–156.90 | 127.77–318.55 → 127.77–318.55 |
| design | medium | 20 | 144.81 → 181.01 | 4 → 5 | 48.24–84.49 → 75.27–138.56 | 91.57–255.31 → 118.61–264.47 |
| design | medium | 50 | 144.81 → 173.77 | 10 → 12 | 37.33–349.10 → 70.01–349.10 | 80.66–529.08 → 127.77–529.08 |
| design | medium | 500 | 134.81 → 134.81 | 4 → 4 | 45.74–79.49 → 79.44–79.49 | 89.07–225.77 → 122.77–259.47 |
| design | medium | 5000 | 104.48 → 121.33 | 31 → 36 | 28.89–52.53 → 52.53–76.12 | 72.22–208.92 → 99.18–232.51 |
| design | heavy | 5 | 505.91 → 505.91 | 2 → 2 | 265.04–518.00 → 446.47–591.33 | 356.69–588.00 → 489.80–697.98 |
| design | heavy | 10 | 505.91 → 505.91 | 4 → 4 | 229.30–391.52 → 374.11–518.92 | 320.95–461.52 → 465.76–588.00 |
| design | heavy | 20 | 442.67 → 505.91 | 7 → 8 | 193.10–391.52 → 328.28–482.72 | 284.75–449.87 → 419.93–541.07 |
| design | heavy | 50 | 337.02 → 505.91 | 1 → 20 | 185.86–374.11 → 315.63–461.00 | 277.51–529.08 → 392.38–529.08 |
| design | heavy | 500 | 337.02 → 404.42 | 10 → 12 | 146.89–281.70 → 214.29–349.10 | 238.54–340.05 → 305.94–407.45 |
| design | heavy | 5000 | 320.17 → 374.09 | 95 → 111 | 133.41–268.22 → 207.55–328.88 | 228.43–326.57 → 302.57–387.54 |
| conservative | light | 5 | 144.81 → 144.81 | 1 → 1 | 164.08–272.36 → 164.08–272.36 | 207.42–452.34 → 207.42–452.34 |
| conservative | light | 10 | 72.41 → 72.41 | 1 → 1 | 91.68–145.88 → 91.68–145.88 | 135.01–325.86 → 135.01–325.86 |
| conservative | light | 20 | 36.20 → 63.24 | 1 → 1 | 55.48–82.64 → 55.48–82.64 | 98.81–262.63 → 98.81–262.63 |
| conservative | light | 50 | 43.44 → 43.44 | 3 → 3 | 33.75–356.42 → 44.57–356.42 | 77.09–536.40 → 87.90–536.40 |
| conservative | light | 500 | 33.70 → 33.70 | 1 → 1 | 52.98–53.10 → 52.98–53.10 | 96.31–233.09 → 96.31–233.09 |
| conservative | light | 5000 | 26.96 → 30.33 | 8 → 9 | 26.01–26.14 → 32.75–32.88 | 69.35–206.13 → 76.09–212.87 |
| conservative | medium | 5 | 144.81 → 252.96 | 1 → 1 | 164.08–272.36 → 164.08–272.36 | 207.42–452.34 → 207.42–452.34 |
| conservative | medium | 10 | 144.81 → 217.22 | 2 → 3 | 91.68–145.88 → 91.68–164.21 | 135.01–325.86 → 135.01–325.86 |
| conservative | medium | 20 | 144.81 → 181.01 | 4 → 5 | 55.48–91.81 → 82.51–145.88 | 98.81–262.63 → 125.85–271.79 |
| conservative | medium | 50 | 144.81 → 173.77 | 10 → 12 | 44.57–356.42 → 91.68–356.42 | 87.90–536.40 → 135.01–536.40 |
| conservative | medium | 500 | 134.81 → 134.81 | 4 → 4 | 52.98–86.81 → 86.68–86.81 | 96.31–233.09 → 130.01–266.79 |
| conservative | medium | 5000 | 104.48 → 121.33 | 31 → 36 | 42.86–59.85 → 69.83–83.44 | 86.20–222.98 → 113.16–249.94 |
| conservative | heavy | 5 | 505.91 → 505.91 | 2 → 2 | 272.36–525.32 → 309.03–598.65 | 364.01–595.32 → 489.01–705.30 |
| conservative | heavy | 10 | 505.91 → 505.91 | 4 → 4 | 236.62–398.84 → 309.03–526.24 | 328.27–468.84 → 473.08–595.32 |
| conservative | heavy | 20 | 442.67 → 505.91 | 7 → 8 | 200.42–398.84 → 309.03–490.04 | 292.07–457.19 → 427.25–548.39 |
| conservative | heavy | 50 | 337.02 → 505.91 | 1 → 20 | 193.18–381.43 → 297.66–468.32 | 288.12–536.40 → 389.31–536.40 |
| conservative | heavy | 500 | 337.02 → 404.42 | 10 → 12 | 187.91–289.02 → 255.31–356.42 | 279.56–367.89 → 346.96–435.30 |
| conservative | heavy | 5000 | 320.17 → 374.09 | 95 → 111 | 157.58–278.91 → 231.72–339.57 | 252.60–337.56 → 326.74–411.71 |


At 5 people, medium all-server changes from one single-RTX server($144.81/person-month) to one dual-RTX server($252.96); heavy stays one pair of dual-RTX servers($505.91). At 20 people, light changes single→dual($36.20→$63.24), medium grows to five single-RTX servers($144.81→$181.01), and heavy grows from seven to eight dual-RTX units($442.67→$505.91). The complete selection reversals, including hybrid fleet choices, are in `ENGINE-FLIPS-R12-261101.csv`. B300 eligibility policy is unchanged.

## Cash payback

Months = incremental acquisition cash / (full API bill − owned-device hybrid bill including overflow to the same API). Nonpositive saving means no payback. This is cash payback; the separate resale-adjusted convention multiplies by1−client_residual and is exported too. Purchased-device amortization is excluded from this denominator.

| Hosting | Share/client/basis | Median API cash payback, months |
| --- | --- | --- |
| default | share=0.2; client=M3 Max 128 GB (measured); basis=Mac already owned | 47.05 → 56.33 |
| default | share=0.2; client=M4 Max 128 GB (estimate); basis=Mac already owned | 46.15 → 54.94 |
| default | share=0.2; client=M5 Max 64 GB; basis=Mac already owned | 33.99 → 40.23 |
| default | share=0.2; client=M5 Max 128 GB; basis=Mac already owned | 54.15 → 64.08 |
| default | share=0.2; client=M5 Ultra 96 GB; basis=Mac already owned | 69.55 → 81.57 |
| default | share=0.2; client=M5 Ultra 256 GB; basis=Mac already owned | 135.54 → 158.21 |
| default | share=0.5; client=M3 Max 128 GB (measured); basis=Mac already owned | 37.05 → 44.19 |
| default | share=0.5; client=M4 Max 128 GB (estimate); basis=Mac already owned | 26.02 → 30.71 |
| default | share=0.5; client=M5 Max 64 GB; basis=Mac already owned | 17.98 → 21.11 |
| default | share=0.5; client=M5 Max 128 GB; basis=Mac already owned | 27.00 → 31.66 |
| default | share=0.5; client=M5 Ultra 96 GB; basis=Mac already owned | 25.48 → 29.45 |
| default | share=0.5; client=M5 Ultra 256 GB; basis=Mac already owned | 49.68 → 57.19 |
| conservative | share=0.2; client=M3 Max 128 GB (measured); basis=Mac already owned | 53.56 → 66.13 |
| conservative | share=0.2; client=M4 Max 128 GB (estimate); basis=Mac already owned | 52.81 → 64.98 |
| conservative | share=0.2; client=M5 Max 64 GB; basis=Mac already owned | 39.16 → 47.99 |
| conservative | share=0.2; client=M5 Max 128 GB; basis=Mac already owned | 62.35 → 76.40 |
| conservative | share=0.2; client=M5 Ultra 96 GB; basis=Mac already owned | 80.55 → 98.28 |
| conservative | share=0.2; client=M5 Ultra 256 GB; basis=Mac already owned | 157.23 → 191.60 |
| conservative | share=0.5; client=M3 Max 128 GB (measured); basis=Mac already owned | 41.16 → 50.26 |
| conservative | share=0.5; client=M4 Max 128 GB (estimate); basis=Mac already owned | 28.35 → 34.12 |
| conservative | share=0.5; client=M5 Max 64 GB; basis=Mac already owned | 19.64 → 23.54 |
| conservative | share=0.5; client=M5 Max 128 GB; basis=Mac already owned | 29.40 → 35.16 |
| conservative | share=0.5; client=M5 Ultra 96 GB; basis=Mac already owned | 27.53 → 32.54 |
| conservative | share=0.5; client=M5 Ultra 256 GB; basis=Mac already owned | 53.78 → 63.52 |


Every cheapest-API cash-payback case remains “no payback”. Separate `payback_measured_server.csv` and `payback_conservative_measured_server.csv` preserve all cash and resale-adjusted comparisons.

## Million-token sessions

GLM growing sessions retain the two-sessions/user-day plan and full Studio amortization. These costs depend on estimated B300 prefill, so both long-session and Studio-utilization tables are re-exported. Per-session USD at context 1000000:

| Hosting | Team | API $/session | All-server$/session | Hybrid$/session | Owned units | Hybrid units |
| --- | --- | --- | --- | --- | --- | --- |
| design | 5 | 9.15 | 80.24 → 80.24 | 84.07 → 84.07 | 1→1 | 1→1 |
| design | 10 | 9.15 | 40.12 → 40.12 | 43.95 → 43.95 | 1→1 | 1→1 |
| design | 20 | 9.15 | 20.06 → 20.06 | 23.89 → 23.89 | 1→1 | 1→1 |
| design | 50 | 9.15 | 8.02 → 8.02 | 11.85 → 11.85 | 1→1 | 1→1 |
| design | 500 | 9.15 | 3.21 → 4.01 | 4.63 → 5.43 | 4→5 | 1→2 |
| design | 5000 | 9.15 | 3.21 → 3.69 | 4.15 → 4.79 | 40→46 | 4→12 |
| conservative | 5 | 9.15 | 80.24 → 80.24 | 84.16 → 84.16 | 1→1 | 1→1 |
| conservative | 10 | 9.15 | 40.12 → 40.12 | 44.04 → 44.04 | 1→1 | 1→1 |
| conservative | 20 | 9.15 | 20.06 → 20.06 | 23.98 → 23.98 | 1→1 | 1→1 |
| conservative | 50 | 9.15 | 8.02 → 8.02 | 11.94 → 11.94 | 1→1 | 1→1 |
| conservative | 500 | 9.15 | 3.21 → 4.01 | 4.72 → 5.52 | 4→5 | 1→2 |
| conservative | 5000 | 9.15 | 3.21 → 3.69 | 4.40 → 4.96 | 40→46 | 6→13 |


GLM 1M cold ingest plus transfer rises from97.41 to225.02s; hybrid capacity changes from6.79 to6.74sessions/Studio-day. Local capacity and decode remain unchanged. This is not the measured Qwen1.04M fill; they are different models and input paths. The utilization CSVs retain all1/2-user sharing and fixed/saturated demand cases; the full comparison ledger records every one of their numeric cells.

## Capacity and offload example

Heavy-user GPU capacity at 20/50/100% open share; 8 h/day and 70% target load. These are uncapped offered-demand bounds, not observed concurrency or per-client capacity:

| Hosting | GPU | Share | People compute only | People with hosting |
| --- | --- | --- | --- | --- |
| design | RTX PRO 6000 hourly | 0.2 | 69.00 → 20.00 | 64.00 → 20.00 |
| design | RTX PRO 6000 hourly | 0.5 | 27.00 → 8.00 | 25.00 → 8.00 |
| design | RTX PRO 6000 hourly | 1 | 13.00 → 4.00 | 12.00 → 4.00 |
| design | B300 288 GB hourly | 0.2 | 308.00 → 90.00 | 221.00 → 81.00 |
| design | B300 288 GB hourly | 0.5 | 123.00 → 36.00 | 88.00 → 32.00 |
| design | B300 288 GB hourly | 1 | 61.00 → 18.00 | 44.00 → 16.00 |
| conservative | RTX PRO 6000 hourly | 0.2 | 69.00 → 20.00 | 57.00 → 19.00 |
| conservative | RTX PRO 6000 hourly | 0.5 | 27.00 → 8.00 | 22.00 → 7.00 |
| conservative | RTX PRO 6000 hourly | 1 | 13.00 → 4.00 | 11.00 → 3.00 |
| conservative | B300 288 GB hourly | 0.2 | 308.00 → 90.00 | 159.00 → 71.00 |
| conservative | B300 288 GB hourly | 0.5 | 123.00 → 36.00 | 63.00 → 28.00 |
| conservative | B300 288 GB hourly | 1 | 61.00 → 18.00 | 31.00 → 14.00 |


| Hosting; f32,1Gbit/s | Offloaded share | Saved s/all calls | Saved s/offloaded call |
| --- | --- | --- | --- |
| design | 0.608109 → 0.593023 | 26.47 → 26.16 | 43.53 → 44.11 |
| conservative | 0.613773 → 0.612746 | 26.52 → 26.32 | 43.21 → 42.95 |


The Qwen 27B/M3/110k/1k/f32 arithmetic-intensity offload bound is unchanged byte for byte: it compares client compute with transferred delta bytes and excludes server time. It remains a necessary bound, not end-to-end speedup. Its measured-server sibling is exported unchanged; offload policy, turn/ingest and transcript timing siblings account for slower server work.

## Direction changes

| Comparison whose direction/selection changes | Coordinate records (profile extracts included) |
| --- | --- |
| API minus hybrid cheapest | 12 |
| API minus hybrid median | 12 |
| API minus hybrid session | 1 |
| API minus owned session | 4 |
| owned minus hybrid median | 33 |
| owned minus hybrid session | 3 |
| selected owned fleet | 528 |


The extra academic 100%-open case also reverses the cheapest-API advantage of already-owned Ultra 96/Ultra 256 under design hosting: API−hybrid changes+$0.76245→−$40.53081 and+$3.20916→−$38.04410/person-month. This does not change the s20/s50 verdict above.

One GLM 1M utilization row reverses by less than half a cent/session: team 500, one user/Studio, one session/user-day, design hosting changes hybrid $9.149894→$9.145163 against API $9.146792. Fewer optimal offloads reduce migration overhead while the owned fleet stays one node; this is an integer-fleet/hosting consequence, not improved measured compute. The sign is numerically real and too small to support a robust economic claim. At GLM 200k, team 5000 and fixed one-session/day demand, the owned route flips from below to above API for both 1/2-user Studio sharing cases and both hosting policies. Three saturated-demand GLM rows flip hybrid versus owned; their offered demand is recomputed from changed capacity, so those are not equal-workload comparisons. The 33 owned-cluster versus median-hybrid reversals are all listed at their exact client/share/team coordinates.

`ENGINE-FLIPS-R12-261101.csv` gives exact before/after values and coordinates for every entry above. Positive API−hybrid means hybrid is cheaper; positive owned−hybrid means hybrid is cheaper than all-server. Selection flags list both the deselected and selected alternative and appear in both the master perimeter table and its profile extract. These are record counts, not distinct deployment counts. No direction change is hidden by averaging or by rounding the report tables.

## Validation and delivery evidence

The full suite passes: **244 tests, exit 0, 566.471 s**, including all 234 prior cases and 10 run12 tests. All 225 directly declared prior test method names are retained (235 now; inherited cases make the executed count larger). The nine legacy golden transcripts pass. Frozen source/input/Python-test/environment identity: `b8f9ca1b3ea1d8dbdb92ad08f3b8a382bd8a505a7fec35d0e88fa43c40f5fd80`; its component hashes are checked unchanged after validation in `.temp/hybrid-calc-r12-261101/validation-identity.json`.

| Command/check | Actual exit | Evidence in `.temp/hybrid-calc-r12-261101/` |
| --- | --- | --- |
| `python3 -m unittest discover -s calc/tests -v` with task-local TMPDIR | 0 | `unittest-full-01.log`, `unittest-full-result-01.json` |
| `python3 calc/tests/r12_audit.py` | 0 | `publication-export-02.log`, `publication-export-result-02.json`, `publication-audit.json`; 42 charts + 2 payback CSVs; 140350 numeric cells, 31870 changed cells; 7997 quote records |
| All eight measured-server generator/payload manifest sets | 0 | `manifest-verification-01.json`; original manifests untouched |
| All 42 design CSVs regenerated in scratch and compared byte for byte; sensitivity export preserves all original artifacts | 0, within full suite | `test_all_design_csv_bytes_unchanged`, `test_measured_export_cannot_overwrite_run11` |
| `python3 calc/tests/r12_controls.py old_mfu` | **1, expected red** | `old-mfu-control-01.log`; intended named timing AssertionError, not a setup error |
| Python3.9 `ast.parse` grammar validation, no build | 0 | `python-grammar-01.log` |
| `python3 -m hybridcalc list` | 0 | `engine-list-01.log` |
| `git verify-commit a57db67` | 0 | `baseline-signature-01.log` |
| Prior test-method-name retention and unchanged source/test identity | 0 | `test-name-retention-01.json`, `validation-identity.json` |
| Python SHA256 verification of all 416 repository manifest entries | 0 | `manifest-check-01.log` |
| `git diff --cached --check` | **2, preserved archive whitespace** | `staged-diff-check-01.log`; ten existing trailing-whitespace lines in the imported build-configure/kit logs |
| Staged whitespace check excluding only the raw archive members | 0 | `staged-code-diff-check-01.log`; source, docs, inputs and generated tables are clean |

The first focused run exited 1: its GLM envelope fixture tried to divide an alarmed non-fitting RTX placement's absent total compute. Production correctly retained the placement alarm. The fixture now explicitly checks that rejection and checks total compute only on admitted configurations; the isolated corrected regression exits 0 and the complete suite above is green. The first export run was superseded after a source-only cleanup of a redundant conditional; all eight final sidecars match the same unchanged validated generator. No red candidate is presented as final green evidence. The whole staged whitespace check exits 2 solely for ten lines already present in two archive log files; those bytes are deliberately preserved to satisfy the archive-integrity requirement. The separate check of every authored/generated file exits 0. No archive content was trimmed or silently changed.

| Mutant | What the gate is narrowed to | Named failing test | Surviving bound |
| --- | --- | --- | --- |
| Replace the measured prefill node with old `target_fp8_peak × 0.3` | The actual owned-server prefill consumer must reproduce independent raw 2k/10k prompt timings within 2%, with the existing GPU/shard factors | `test_run12.Run12Tests.test_measured_server_timing_replaces_mfu` | Killed, exit 1: error 57.17% exceeds 2%. No survivor. This does not test every possible curve defect, small-portion overhead, device portability, GLM portability or concurrency. |

The paired positive path passes the same observed-time assertion. Bulk-point tolerance is 2%; held-out fills use 15%. Hash mismatch, missing measurement, malformed/inexact observations and incompatible BF16 precision reject rather than falling back to MFU. The all-call input sample, decoding inputs, tariffs and hosting-policy inputs are equal across paired scenarios. Existing alarm-cell counts remain R5 329/252, R6 6/0, R7 28/24 and R8 576/0 (design/conservative). No requested table is treated as out of contract; non-fitting or policy-excluded rows retain explicit alarm cells and the report's cost ranges exclude them with their stated criteria.

No surface table or separate landing-gate property suite is supplied in this brief: this remains an explicit brief gap. Review is local self-review, including the entire scoped diff, archive member hashes, manifests, quote definitions, sign reversals and preserved historical artifacts. No independent review, hosted CI, landing, build, download, install, network research or push is claimed. No file under `paper/` is changed. Local signed delivery is ready for review. The addressed summary is prepared at `.temp/hybrid-calc-r12-261101/prototype-go-summary.md`; the explicit no-network limit remains in force and no a2a post has been sent without the requested exception.
