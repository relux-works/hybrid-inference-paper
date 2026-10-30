# Hardware prices and specs for the inference-economics study (late October 2026)

Compiled 2026-10-30 (UTC). Every number has a source URL, the date of the data, and a short quote.
Labels used below:

- **[vendor-live]**: read directly from a vendor store, price file or API on 2026-10-30.
- **[vendor-spec]**: vendor datasheet, whitepaper or press release.
- **[press]**: news article or analyst note; date given.
- **[tracker]**: price aggregator; method and date given.
- **[measured]**: a benchmark result reported by a third party.
- **[estimate]**: my own arithmetic or inference. The basis is always stated.
- **[unverified]**: seen only in a search snippet or on a page whose method is unclear.

Currency conversions use ECB reference rates of 2026-10-29: EUR/USD 1.1130, USD/JPY 158.06, USD/SGD 1.2817, USD/INR 95.27
(https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml).

Method: items 1-6 were researched directly; items 7 (components and vendor systems), 8 and 9 were researched by two helper agents with the same rules (URL, date and quote for every number). Their full notes are appended as Appendix A and Appendix B; sections 7-9 condense them. DDR5 RDIMM (7.1) and the workstation totals (7.4) are mine.

## Key numbers at a glance

| Item | Key figure(s) | Status |
|---|---|---|
| MacBook Pro 14" M5 Max, 128 GB | **$6,699**, 2 TB SSD, 18C CPU / 40C GPU (owner's $6,700 confirmed) | Apple store API |
| M5 Max 64 GB (14", 2 TB) | $5,099 | Apple store API |
| MacBook Pro 14" M5 Pro: base / 64 GB | $2,499 (15C/16C, 24 GB, 1 TB) / $3,699 (18C/20C, 1 TB) | Apple store API |
| Mac Studio M5 Ultra 96 / 256 / 512 GB (1 TB) | $5,499 or $6,799 / $9,499 or $10,799 / **$22,299** (80-core only) | Apple store API |
| Memory bandwidth M5 Pro / M5 Max / M5 Ultra | 307 / 614 (460 on 32-core) / 1,200 GB/s | Apple |
| FP16 dense M5 Pro / M5 Max / M5 Ultra / M3 Max | ~30-35 est / ~60 measured, ~70 est / ~120-140 est / ~14 est (11.4 FP32 measured) TFLOPS | Apple publishes no TFLOPS |
| DGX Spark 128 GB | **$6,950** list since 2026-10-02 (was $3,999, then $4,699); 64 GB partner models from $4,999 | press; NVIDIA page not readable |
| GB10 | 273 GB/s; dense FP8 ~250 peak est / 208 measured; BF16 ~125 est / 99.8 measured TFLOPS | NVIDIA gives only 1 PFLOP FP4 sparse |
| Ryzen AI Max+ 395, 128 GB | Framework $3,449 (out of stock); GMKtec EVO-X2 $3,499.99 (1 TB) | vendor stores |
| Radeon 8060S | ~59 TFLOPS FP16 theoretical (WMMA); 256 GB/s theoretical, ~215 measured | AMD spec + community |
| RTX PRO 6000 (Workstation) | US $16,000 list, street ~$16.3-18.6k; EU ~€15.5-16.5k incl. VAT; Asia ~$16-28k | trackers, press |
| RTX PRO 6000 specs (WS / Max-Q / Server) | 1792 / 1792 / 1597 GB/s; dense FP8 1007.6 / 877.9 / ~1000; FP4 2015.2 / 1755.7 / ~2000; BF16 503.8 / 438.9 / ~500 TFLOPS; 600 / 300 / ≤600 W | NVIDIA whitepaper and pages |
| RTX 5090 | street ~$5-7k (Oct average of 3 cheapest listings $6,460; MSRP $1,999); 1792 GB/s; dense FP8 838 (FP16 acc) / 419 (FP32 acc) TFLOPS | tracker; NVIDIA whitepaper |
| HGX B300 node | ~$400-650k (Reuters: ~$550k, Apr 2026); 288 GB HBM3E and 8 TB/s per GPU; dense FP8 4.5 PFLOPS per GPU; ~14-15 kW | NVIDIA, Supermicro, press |
| Cloud $/GPU-h on-demand | B300: $7.10-9.50 neocloud, $15.00 Oracle, $17.80 AWS. B200: $6.25-8.60 neocloud, $14.00-14.24 Oracle/AWS. H100: $3.95-6.16 neocloud, $6.88 AWS, $10.00-12.29 Oracle/GCP/Azure | provider price files and pages |
| DDR5 RDIMM | retail $42-64/GB; contract/spot-derived $25-35/GB | store data, TrendForce, Citi |
| RTX PRO 6000 workstation | 1 GPU ≈ $25-28k (128 GB); 2 GPUs ≈ $46-52k (256 GB); System76 $27.3k (1 GPU), Puget $52.4k (2x Max-Q); 4-GPU servers ~$106-108k | estimate + vendor configurators |
| Enterprise NVMe | TLC 15.36 TB ~$700-1,200/TB (median ~$920); capacity TLC/QLC 30-61 TB ~$450-775/TB | in-stock listings |
| US colocation | CBRE 250-500 kW average $196.25/kW-mo (H2 2025), ~$205 H1 2026 est; large deals $145-185; retail ~$250-300; energy usually extra | CBRE, datacenterHawk, Digital Realty |
| US industrial electricity | 9.09 ¢/kWh 2026 YTD (9.64 ¢ in Aug 2026); Virginia ~10 ¢, Texas ~7 ¢ | EIA |

---

## 1. Apple

### 1.1 MacBook Pro and Mac Studio prices (US, pre-tax, Apple Store)

Source for all **[vendor-live]** prices: Apple's own store pages and the store's configurator price API, read 2026-10-30:

- https://www.apple.com/shop/buy-mac/macbook-pro/14-inch-m5-max (base prices for every model are embedded in the page)
- `https://www.apple.com/shop/api/cto/update-config?collection=MBP_2026_COLLECTION&fae=true&sv.chassis-dimensionScreensize=14inch&sv.chassis-dimensionColor=spaceblack&sv.processor-dimensionChip-cpuCoreCount-gpuCoreCount=m5max-18-40&sv.display-dimensionFinish=standard&sv.memory-dimensionMemory=48gb&sv.storage-dimensionCapacity=2tb&sections=memory-dimensionMemory,storage-dimensionCapacity`
  (the JSON the configurator uses for option prices; change the `sv.` values for other models)
- https://www.apple.com/shop/buy-mac/mac-studio and the same API with `collection=MACSTUDIO_2026_COLLECTION`

The API answer for the 14-inch M5 Max 18-core CPU / 40-core GPU, 48 GB, 2 TB was:
`"amount": 4699.0`; memory `"64gb": "+ $400.00"`, `"128gb": "+ $2,000.00"`; storage `"4tb": "+ $1,000.00"`, `"8tb": "+ $3,000.00"`;
footer text "Choose from 48GB, 64GB, or 128GB with your current chip selection".

| Configuration (US, pre-tax) | Price | How derived |
|---|---|---|
| **MacBook Pro 14" M5 Max 18C CPU / 40C GPU, 128 GB, 2 TB SSD** | **$6,699** | $4,699 base (48 GB, 2 TB) + $2,000 for 128 GB **[vendor-live]** |
| same, 128 GB, 4 TB / 8 TB | $7,699 / $9,699 | + $1,000 / + $3,000 storage **[vendor-live]** |
| MacBook Pro 14" M5 Max 40C GPU, 64 GB, 2 TB | $5,099 | $4,699 + $400 **[vendor-live]** |
| MacBook Pro 14" M5 Max 18C CPU / 32C GPU, 36 GB, 2 TB (cheapest M5 Max) | $4,099 | base; 36 GB is the only memory option on this chip **[vendor-live]** |
| MacBook Pro 16" M5 Max 40C GPU, 128 GB, 2 TB | $6,999 | $4,999 + $2,000 **[vendor-live]** |
| **MacBook Pro 14" M5 Pro base (15C CPU / 16C GPU, 24 GB, 1 TB)** | **$2,499** | base; footer "Choose from 24GB or 48GB" (no 64 GB on this chip) **[vendor-live]** |
| MacBook Pro 14" M5 Pro 18C CPU / 20C GPU, 24 GB, 1 TB | $2,699 | base **[vendor-live]** |
| **MacBook Pro 14" M5 Pro 18C/20C, 64 GB, 1 TB** | **$3,699** | $2,699 + $1,000 (48 GB is + $600) **[vendor-live]** |
| MacBook Pro 16" M5 Pro 18C/20C, 64 GB, 1 TB | $3,999 | $2,999 + $1,000 **[vendor-live]** |
| Nano-texture display option | + $150 | price keys in store page (e.g. 14" M5 Max 40C: $4,699 standard vs $4,849 nano-texture) **[vendor-live]** |
| **Mac Studio M5 Ultra 30C CPU / 64C GPU, 96 GB, 1 TB** | **$5,499** | base **[vendor-live]** |
| Mac Studio M5 Ultra 36C CPU / 80C GPU, 96 GB, 1 TB | $6,799 | base **[vendor-live]** |
| **Mac Studio M5 Ultra, 256 GB, 1 TB** | **$9,499** (30C/64C) or **$10,799** (36C/80C) | base + $4,000 **[vendor-live]** |
| **Mac Studio M5 Ultra 36C/80C, 512 GB, 1 TB** | **$22,299** | $6,799 + $15,500; 512 GB is offered only on the 36C/80C chip (the 30C/64C API answer lists only 96 GB and 256 GB) **[vendor-live]** |
| Mac Studio M5 Ultra SSD options | 2 TB + $500, 4 TB + $1,500, 8 TB + $3,500, 16 TB + $7,500 | **[vendor-live]** |
| Mac Studio M5 Max 18C/40C, 48 GB, 512 GB | $3,099 (64 GB + $400, 128 GB + $2,000) | **[vendor-live]** |
| Mac Studio M5 Max 18C/32C, 36 GB, 512 GB | $2,499 | **[vendor-live]** |

Verdicts on the owner's numbers:

- **$6,700 for the 14" M5 Max 128 GB is confirmed: $6,699 pre-tax, with a 2 TB SSD** (the smallest SSD offered with M5 Max), 18-core CPU / 40-core GPU, standard display. 128 GB requires the 40-core GPU chip.
- **Mac Studio M5 Ultra 256 GB "about $11k"**: close. $10,799 with the 80-core GPU and 1 TB ($11,299 with 2 TB); $9,499 with the 64-core GPU.
- **512 GB "about $23k"**: slightly high. **$22,299** with 1 TB; it went on sale on 2026-10-28.

Corroboration and history:

- MacRumors, 2026-10-28, https://www.macrumors.com/2026/10/28/mac-studio-m5-ultra-512gb-ram/ **[press]**:
  "This pushes the minimum cost for a configuration with 512GB of RAM to an eye-watering $22,299." and "which starts at $6,799 in the U.S., and then you have to select the 512GB of RAM option for an additional $15,500."
- Cult of Mac, 2026-10-28, https://www.cultofmac.com/news/512gb-mac-studio-arrives-with-a-jaw-dropping-price **[press]**:
  "configuring the machine with 256GB of memory costs an additional $4,000, bringing the total to $10,799." and "The jump from 256GB to 512GB of memory alone adds a whopping $11,500 to the price."
- Daring Fireball, 2026-08-25, https://daringfireball.net/2026/08/configurations_and_pricing_for_new_mac_minis_and_mac_studios **[press]**:
  M5 Ultra "30-core CPU, 64-core GPU: $5,500", "36-core CPU, 80-core GPU: $6,800"; RAM "96 GB $0", "256 GB $4000", "512 GB 'Coming late October'".
- June 2026 Apple price increase: Macworld, updated 2026-07-09, https://www.macworld.com/article/353690/upgrade-your-old-laptop-with-200-off-the-speedy-m1-macbook-pro.html **[press]**:
  14" M5 Max "Is now priced at a whopping $4,099. Previously it was $3,599." and "The base 14-inch M5 Pro MacBook was $2,199 prior to the June price hikes. Now that model costs $2,499."
- Daring Fireball, 2026-06-25, https://daringfireball.net/2026/06/spensive_thoughts **[press]**:
  "The 64 and 128 GB RAM upgrades for the M5 Max doubled in price." and "The nano-texture display upgrade remains +$150". Its example table (paraphrased) puts a 14-inch M5 Max 18/40, 128 GB, 8 TB, nano-texture at $7,050 before and $9,850 after the increase. (Today's API arithmetic gives $4,699 + $2,000 + $3,000 + $150 = $9,849, consistent.)
- Older 128 GB prices around $5,399 (e.g. AppleInsider price guides) predate the June 2026 increase and are stale.
- Note: Apple's store now also lists a 14" MacBook Pro with an **M6** chip (12C CPU / 12C GPU, from $1,999). Not researched further.

### 1.2 Memory bandwidth (Apple claims) **[vendor-spec]**

| Chip | Bandwidth | Source and quote |
|---|---|---|
| M5 Pro | up to 307 GB/s | Apple Newsroom, 2026-03-03, https://www.apple.com/newsroom/2026/03/apple-debuts-m5-pro-and-m5-max-to-supercharge-the-most-demanding-pro-workflows/ : "M5 Pro supports up to 64GB of unified memory with higher unified memory bandwidth up to 307GB/s." |
| M5 Max (40-core GPU) | 614 GB/s | same release: "M5 Max supports up to 128GB of unified memory with higher unified memory bandwidth up to 614GB/s." |
| M5 Max (32-core GPU) | 460 GB/s | Mac Studio specs, https://www.apple.com/mac-studio/specs/ (read 2026-10-30): "460GB/s memory bandwidth" (32-core) vs "614GB/s memory bandwidth" (40-core) |
| M5 Ultra | 1.2 TB/s (Wikipedia variant table: 1,228.8 GB/s, uncited) | Apple Newsroom, 2026-08-25, https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/ : "Combined with up to 512GB of unified memory and 1.2TB/s of memory bandwidth, 50 percent higher than before" |
| M3 Max (for reference) | 400 GB/s (40-core GPU), 300 GB/s (30-core) | Wikipedia, https://en.wikipedia.org/wiki/Apple_M3 : "the 16-core M3 Max has the same 400 GB/sec as the prior M1 and M2 Max models" |

### 1.3 Peak GPU matrix throughput (FP16, dense)

Apple publishes **no TFLOPS figures** for M5-generation GPUs; it gives only multipliers. The Neural Accelerators in each M5 GPU core are reached through the Metal 4 tensor APIs (MLX and llama.cpp use them only in recent builds).

Apple claims **[vendor-spec]**:

- M5 Pro / M5 Max (Apple Newsroom, 2026-03-03, URL above): "M5 Pro and M5 Max are over 4x the peak GPU compute for AI compared to the previous generation." Also "M5 Pro delivers over 4x the peak GPU compute compared to M4 Pro" and "over 6x the peak GPU compute than M1 Max for AI performance" (M5 Max).
- Mac Studio (Apple Newsroom, 2026-08-25, URL above): "M5 Max features phenomenal on-device AI compute with up to 3.9x faster AI performance than the prior generation"; "With M5 Ultra, Mac Studio achieves up to 4.3x the peak AI compute performance of M3 Ultra"; "Up to 9.8x faster LLM prompt processing in LM Studio when compared to Mac Studio with M1 Ultra" ("up to 4x faster than M3 Ultra"). Footnote: "Testing was conducted by Apple in July 2026."

Measured and microbenchmark data:

- **Per-core rate [measured, on A19]**: Taras Zakharko, "Investigating the GPU Neural Accelerators on Apple A19/M5", published 2025-10-15, https://tzakharko.github.io/apple-neural-accelerators-benchmark/ : about "1024 FLOPS per GPU core per cycle for FP16 matrix-multiply accumulate"; measured "approximately 7.4 TFLOPS" on the 5-core A19 (iPhone 17); "The performance remains the same for both accumulator types" (FP16 or FP32 accumulate). The article extrapolates about 70 TFLOPS FP16 for a 40-core M5 Max at about 1750 MHz. BF16 was not measured ("A notable omission").
- **M5 Max [measured]**: Draw Things engineering post, 2026-04-01, https://releases.drawthings.ai/p/metal-quantized-attention-pulling : "our most efficient FP16 matrix multiplication shader on the M5 Max delivers about 60 TFLOPs." (GPU core count not stated; probably the 40-core part.) The same post: "our shaders now regularly reach around 110 TFLOPs on M5 Max" in image/video generation, in the context of Int8 kernels (precision not stated in that sentence).
- **M3 Max [measured, FP32]**: chsasank/device-benchmarks (PyTorch MPS matmul), https://github.com/chsasank/device-benchmarks (read 2026-10-30, undated table): "Apple M3 Max GPU (40 Core)" 11.4 TFLOPS FP32; "Apple M4 Max GPU (16C,40C,128G)" 13.27 FP32 and 13.29 FP16. Apple GPUs before M5 run FP16 FMA at the same per-cycle rate as FP32 (Philip Turner, https://github.com/philipturner/metal-benchmarks : 256 F16 FMA ops and 256 F32 FMA ops per core-cycle on M1-class GPUs), so the M3 Max FP16 peak is about the FP32 peak. Spec databases that list 28.4 TFLOPS FP16 for M3 Max assume a 2:1 FP16 rate that Apple GPUs do not have (CPU-Monkey, seen only in a search snippet).
- Creative Strategies' "19.9 TFLOPS" M5 Max figure (2026-03-09, https://creativestrategies.com/research/m5-max-chiplets-thermals-and-performance-per-watt/) is the **Neural Engine**, not the GPU: "the measured wall-clock peak rose to about 19.9 TFLOPS, versus the project's older 15.8 TFLOPS M4 reference point."
- Higher community "FP16" figures for M5 (e.g. jdhodges.com: M5 Max ~33.2 / ~41.0 TFLOPS "+NA", M5 Ultra ~66.4 / ~82.0) are labelled there as estimates and assume 2x FP32; they are below the measured 60 TFLOPS and are not used here.

Summary table (dense FP16 matmul; BF16 on the M5 neural accelerators is not documented or measured):

| Chip | GPU cores | Measured | My estimate of peak | Basis of estimate |
|---|---|---|---|---|
| M5 Pro | 20 | not found | **~30-35 TFLOPS [estimate]** | half of M5 Max (20 vs 40 cores, similar clocks); consistent with Apple's ">4x M4 Pro" (M4 Pro FP16 ~8 TFLOPS, also an estimate) |
| M5 Max | 40 | **~60 TFLOPS** (Draw Things, best FP16 shader) | **~70 TFLOPS [estimate]** | 1024 FLOP/core/cycle x 40 cores x ~1.75 GHz (Zakharko) |
| M5 Ultra | 80 | not found | **~120-140 TFLOPS [estimate]** | 2x M5 Max; cross-check 4.3x an M3 Ultra FP16 peak of ~28 TFLOPS (2x M3 Max) gives ~120 |
| M3 Max | 40 (no neural accelerators) | 11.4 TFLOPS FP32 matmul (PyTorch MPS) | **~14 TFLOPS FP16 [estimate]** | FP16 rate = FP32 rate on pre-M5 Apple GPUs; ~14 TFLOPS FP32 listed by spec sites |

---

## 2. NVIDIA DGX Spark (GB10)

### 2.1 Price

| Item | Price | Date | Source and quote |
|---|---|---|---|
| DGX Spark 128 GB / 4 TB (Founders Edition), launch | $3,999 | Oct 2025 | StorageReview, 2025-10-14: "Founders Edition is available to order at $3,999 for the 4TB configuration" https://www.storagereview.com/review/nvidia-dgx-spark-review-the-ai-appliance-bringing-datacenter-capabilities-to-desktops |
| first increase | $4,699 | 2026-02-25 | NVIDIA Developer Forums announcement: MSRP "has been adjusted from $3,999 to $4,699 due to memory supply constraints." https://forums.developer.nvidia.com/t/2-23-2026-price-change-announcement/361713 |
| **current 128 GB price** | **$6,950** | 2026-10-02 | The Register (2026-10-02): Nvidia raised the price "to $6,950". https://www.theregister.com/systems/2026/10/02/nvidia-debuts-4999-dgx-spark-with-half-the-ram-and-storage-amid-memory-crunch/5300622 ; ServeTheHome (2026-10-03): "The new price is $6950 for that model." https://www.servethehome.com/nvidia-dgx-spark-64gb-launched-and-big-128gb-gb10-price-increases/ ; Hardware Busters (2026-10-02): "128GB at $3,999 at launch, $4,699 in early 2026 and $6,950 now" https://hwbusters.com/news/nvidia-dgx-spark-64gb-arrives-at-4999-as-the-128gb-model-jumps-to-6950/ |
| conflicting report | $6,000 | 2026-10-03 | heise: "The 128-GByte model now costs US$6000, 50 percent more than a year ago." https://www.heise.de/en/news/Nvidia-s-DGX-Spark-becomes-more-expensive-despite-halved-RAM-11475128.html (outlier; three other outlets say $6,950) |
| NVIDIA marketplace check | $6,950, out of stock | checked 2026-10-11 | GPUwerk: "$6,950 (US list)", "listed out of stock"; the marketplace page did not load on 2026-10-24. https://gpuwerk.com/dgx-spark/price/ **[tracker]** |
| new DGX Spark 64 GB (partners only) | from $4,999 | on sale 2026-10-23 | The Register: "expected to retail for around $4,999"; sold by Acer, ASUS, Dell, Gigabyte, HP and MSI. NVIDIA's page: 64 GB "available exclusively through participating OEM partners". |
| Germany, 128 GB Founders Edition | from €7,331.59 incl. VAT (≈ $6,857 ex-VAT) | 2026-10-24 | GPUwerk citing geizhals.de, "Cheapest of 21 offers" **[tracker]** |
| Saitech (US reseller), Founders Edition 940-54242-0000-000 | $4,825, **not available** | listing updated 2026-10-29 | https://esaitech.com/products/nvidia-940-54242-0000-000-dgx-spark-founders-ai-super-pc (Shopify data: `"price": 482500`, `"available": false`) **[vendor-live]**; an old-price listing that cannot be bought |

Partner GB10 systems with 128 GB (ASUS Ascent GX10, Dell Pro Max with GB10, HP ZGX Nano G1n, Lenovo ThinkStation PGX): no confirmed US price after the October increase. Search snippets only **[unverified]**: ASUS GX10 "U.S. starting price of $3,999 as of August 18, 2026" (starryhope.com, before the increase); HP ZGX Nano 128 GB about €7,339-8,239 at a German retailer; Lenovo PGX 1 TB €4,666 excl. VAT at Bechtle Belgium on 2026-10-24 (GPUwerk, above). ServeTheHome says OEMs charge "different amounts" around the $6,950 tier.

**Verdict:** the owner's "at least $7,000" is about right: **$6,950 list for 128 GB (since 2026-10-02)**, stock thin; the 64 GB partner model starts at $4,999. I could not read the NVIDIA marketplace or US retailer pages directly (timeouts / HTTP 403), so I found no live US retailer listing for late October.

### 2.2 GB10 specs

- **Memory bandwidth: 273 GB/s** [vendor-spec], NVIDIA DGX Spark page (read 2026-10-30) https://www.nvidia.com/en-us/products/workstations/dgx-spark/ : "273 GB/s"; same for the 64 GB model (The Register).
- NVIDIA's only tensor figure is sparse: "Up to 1 PFLOP FP4", footnote "Theoretical FP4 TOPS using the sparsity feature." GB10 TDP "140 W"; power supply "240 Watts".

| Precision | Dense peak | Measured dense |
|---|---|---|
| FP4 (NVFP4) | 500 TFLOPS [estimate: half of the 1 PFLOP sparse figure; the forum post below also uses "500 TFLOPS dense FP4 peak"] | 356 TFLOPS (CUTLASS) [measured] |
| FP8 | ~250 TFLOPS [estimate: half the FP4 rate, the usual Blackwell ratio] | **207.7 TFLOPS** (StorageReview) and 188 TFLOPS (forum) [measured] |
| BF16 | ~125 TFLOPS [estimate: half the FP8 rate; the measured 99.8 would be impossible if BF16 with FP32 accumulate ran at half rate] | **99.8 TFLOPS** (StorageReview) [measured] |

- StorageReview, 2025-10-14 (URL above): "At BF16 precision, we observe a MAMF of 99.8 TFLOPs, while FP8 (E4M3) demonstrates a MAMF of 207.7 TFLOPs."
- NVIDIA Developer Forums, 2026-02-10, https://forums.developer.nvidia.com/t/fp4-on-dgx-spark-why-it-doesnt-scale-like-youd-expect/360142 : "NVFP4 dense: 356 TFLOPS", "FP8 dense: 188 TFLOPS", "500 TFLOPS dense FP4 peak".

---

## 3. AMD Ryzen AI Max+ 395, 128 GB systems

### 3.1 Prices

| System | Config | Price | Date | Source and quote |
|---|---|---|---|---|
| **Framework Desktop DIY** | Ryzen AI Max+ 395, 128 GB | **$3,449**, out of stock (pre-order with deposit) | read 2026-10-30 | https://frame.work/products/desktop-diy-amd-aimax300/configuration/new : option "Max+ 395", "128GB non-upgradeable LPDDR5x", "$3,449", "Out of stock" (64 GB: $1,959; Max 385 32 GB: $1,269); "Ships within 5 business days" once in stock. DIY edition: storage and OS not included. **[vendor-live]** |
| **GMKtec EVO-X2** | 128 GB + 1 TB | **$3,499.99** (compare-at $3,999.99) | store data updated 2026-10-30 | https://www.gmktec.com/products.json (product "GMKtec EVO-X2 AMD Ryzen™ AI Max+ 395 AI Mini PC"): "128GB RAM + 1TB SSD / US", price "3499.99" **[vendor-live]** |
| GMKtec EVO-X2 | 128 GB + 2 TB | $3,649.99 | same | same source **[vendor-live]** |
| GMKtec EVO-X3 | 128 GB + 2 TB | $3,799.99 | same | same source **[vendor-live]** |
| GMKtec EVO-X5 Pro (Ryzen AI Max+ PRO 495) | 192 GB + 2 TB | $6,799 | same | same source; newer 192 GB part, for reference **[vendor-live]** |
| HP Z2 Mini G1a | AI Max+ PRO 395, 128 GB | **not confirmed** | — | No hp.com US price found (the US store timed out from this host). Search snippets only **[unverified]**: Staples $4,997.99 and Newegg $3,733.99 for C3XE0UT#ABA (128 GB / 1 TB), undated; hp.com UK 128 GB / 2 TB (8T219EA#ABU) "£6,623.99 SAVE £1,320.00 £5,303.99"; Bechtle (DE) about €5,113 excl. VAT for 128 GB / 2 TB. |

Price history: Framework's 128 GB board launched at $1,999 (Feb 2025); Tom's Hardware reported a rise to $2,459 in early 2026 (headline: "128GB up $450"; article not readable) https://www.tomshardware.com/desktops/gaming-pcs/diy-pc-maker-framework-finally-succumbs-to-ram-apocalypse-is-raising-prices-on-its-desktops-now-starts-at-usd1-139-with-32gb-128gb-up-usd450 . Typical 128 GB Strix Halo systems now cost **about $3,450-3,800**.

### 3.2 Radeon 8060S specs

- AMD spec page, read 2026-10-30, https://www.amd.com/en/products/processors/laptop/ryzen/ai-300-series/amd-ryzen-ai-max-plus-395.html **[vendor-spec]**: "System Memory Type 256-bit LPDDR5x", "Max Memory Speed LPDDR5x-8000", "Graphics Model Radeon 8060S Graphics", "Graphics Core Count 40", "Graphics Frequency 2900 MHz", "Overall TOPS Up to 126 TOPS", "NPU TOPS Up to 50 TOPS".
- **Memory bandwidth: 256 GB/s theoretical** (256-bit x 8000 MT/s / 8) [estimate from AMD's spec; matches the community figure], **~215 GB/s measured**. Source: lhl, Framework Community, 2025-07-22, https://community.frame.work/t/amd-strix-halo-ryzen-ai-max-395-gpu-llm-performance-tests/72521 : "256 GB/s theoretical (256-bit 8000 MT/s)", "~215 GB/s max GPU MBW" [measured].
- **FP16/BF16: ~59 TFLOPS theoretical dense** (40 CU x 2.9 GHz x 512 FLOP/CU/clk with WMMA) [estimate]; same post: "theoretical 59 FP16 TFLOPS (VPOD/WMMA) on RDNA 3.5 (gfx11); effective is _much_ lower." Measured GEMM results are far lower: 5.1 BF16 TFLOPS with plain rocBLAS and about 36.9 TFLOPS with hipBLASLt (r/LocalLLaMA, 2025; seen only in search snippets) **[unverified]**.

---

## 4. NVIDIA RTX PRO 6000 Blackwell (96 GB GDDR7)

### 4.1 Specs **[vendor-spec]**

Source: NVIDIA RTX Blackwell PRO GPU Architecture whitepaper v1.0, Table 4 (Appendix A),
https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1.0.pdf .
Values are dense/sparse; footnote 2: "Effective TOPS / TFLOPS using the Sparsity Feature"; footnote 1: "Peak rates are based on GPU Boost Clock."

| | Workstation Edition | Max-Q Workstation Edition | Server Edition |
|---|---|---|---|
| Boost clock | 2617 MHz | 2280 MHz | n/a |
| **Memory bandwidth** | **1792 GB/s** ("28 Gbps GDDR7", 512-bit) | **1792 GB/s** | **1597 GB/s** (NVIDIA server page; Lenovo: "Up to 1597 GB/s") |
| **FP4 dense** (FP32 accumulate) | **2015.2 TFLOPS** (sparse 4030.4) | **1755.7** (3511.4) | **~2 PFLOPS** [estimate: half of NVIDIA's "4 PFLOPS"] |
| **FP8 dense** (FP16 or FP32 accumulate, same rate) | **1007.6 TFLOPS** (2015.2) | **877.9** (1755.7) | **~1 PFLOPS** [estimate: half of "2 PFLOPS"] |
| **BF16 dense** (FP32 accumulate) | **503.8 TFLOPS** (1007.6) | **438.9** (877.9) | **~0.5 PFLOPS** [estimate: half of "1 PFLOP"] |
| **TDP / TGP** | **600 W** | **300 W** | **up to 600 W, configurable** |

- Server Edition sources: NVIDIA, https://www.nvidia.com/en-us/data-center/rtx-pro-6000-blackwell-server-edition/ (read 2026-10-30): "1597 GB/s", "FP4 Tensor Core 4 PFLOPS", "FP8 Tensor Core 2 PFLOPS", "FP16 | BF16 Tensor Core 1 PFLOP", "Up to 600W (configurable)" (no sparsity footnote; the 2:1 ratio to the workstation dense figures shows these are sparse numbers). Lenovo Press LP2263, updated 2026-07-28, https://lenovopress.lenovo.com/lp2263-thinksystem-nvidia-rtx-pro-6000-blackwell-server-edition-pcie-gen5-gpu : "600 W (can also be power capped to 450 W to support increased density)".

### 4.2 Street prices

US:

| Source | Price | Date |
|---|---|---|
| NVIDIA US marketplace, Workstation and Max-Q | **$16,000** (out of stock at times) | listed since Aug 2026. Wccftech, 2026-08-12: "As per the latest listing by NVIDIA, the RTX PRO 6000 Blackwell is officially listed at $16,000 US." and image text "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition for $16,000." https://wccftech.com/nvidia-96-gb-rtx-pro-6000-blackwell-now-costs-16000-usd-double-its-original-price/ |
| earlier marketplace price | $13,250 | June 2026. igor'sLAB, 2026-08-14: "As recently as June, the RTX PRO 6000 Blackwell was listed at 13,250 dollars in the NVIDIA marketplace." https://www.igorslab.de/en/nvidia-rtx-pro-6000-blackwell-16000-dollar-96-gb-workstation-gpu-price-increase/ ; launch-era retail was about $8,565 (2025). |
| Thunder Compute summary | NVIDIA marketplace $16,000; Newegg $15,999+; B&H $15,999+; used $14,980-18,850 | updated 2026-10-16, reviewed 2026-10-23, https://www.thundercompute.com/blog/nvidia-rtx-pro-6000-pricing **[tracker]** |
| GPU Poet, Workstation Edition | average of the 3 cheapest listings per day: **$17,317** for October 2026, range $16,325-$18,636 (eBay-based) | 2026-10, https://gpupoet.com/gpu/learn/price/october-2026/nvidia-rtx-pro-6000-blackwell-workstation **[tracker]** |
| GPU Poet, Max-Q | "lowest average price of $22,137" in October 2026 (best day $19,849, worst $23,502); only 3 deals tracked | 2026-10, https://gpupoet.com/gpu/learn/price/october-2026/nvidia-rtx-pro-6000-blackwell-max-q **[tracker]** |
| GPU Poet, Server Edition | "lowest average price of $23,034" in October 2026 (range $21,666-$23,332); 22 deals tracked | 2026-10, https://gpupoet.com/gpu/learn/price/october-2026/nvidia-rtx-pro-6000-blackwell-server **[tracker]** |

EU and Asia (gpuprix.com pages updated 2026-10-30; kakaku.com read 2026-10-30) **[tracker]**:

| Region | Lowest current listing | USD equivalent | Notes |
|---|---|---|---|
| Germany | **€16,505** (PNY Max-Q, Amazon.de); 3-month median €15,490; 12-month median €12,193 | $18,370 incl. 19% VAT; **$15,437 ex-VAT** | https://gpuprix.com/germany/gpus/rtx-pro-6000-blackwell |
| EU (all countries) | €11,054 (PNY Workstation, Amazon NL); 3-month median **€16,051** | $12,303 incl. VAT / $10,168 ex-VAT (low); median $17,865 incl. VAT / ~$14,900 ex-VAT | https://gpuprix.com/eu/gpus/rtx-pro-6000-blackwell ; the €11,054 listing is an outlier versus the medians |
| Japan | Max-Q product page "¥2,592,000〜" (8 shops); Workstation product page "¥3,433,148〜" (1 shop); individual shop listings ¥3.07-3.43M for both editions (e.g. "RTX PRO 6000 Blackwell W/E" ¥3,073,620, "Workstation Edition Bulk" ¥3,404,007); Server Edition ¥3,917,108 | Max-Q $16,399 incl. 10% tax ($14,908 ex-tax); Workstation ¥3.07-3.43M = **$19,400-21,700** incl. tax ($17,700-19,700 ex-tax); Server $24,783 incl. tax | https://search.kakaku.com/6000%20blackwell%20rtx%20pro/?act=Add (parsed 2026-10-30) |
| Singapore | S$22,123 (PNY Server Edition, Amazon.sg, out of stock) | $17,261 incl. 9% GST ($15,836 ex-GST) | https://gpuprix.com/singapore/gpus/rtx-pro-6000-blackwell?show=listings |
| India | ₹2,699,499 (PNY Workstation, Amazon.in; others out of stock at ₹1,585,000-2,260,172) | **$28,336** incl. 18% GST ($24,013 ex-GST); the 3-month median ₹1,585,000 = $16,637 | https://gpuprix.com/india/gpus/rtx-pro-6000-blackwell?show=listings |

**Verdict:** the owner's $15k-30k range holds. US: about **$16,000-18,600** for the Workstation Edition (NVIDIA list $16,000; street average ~$17,300); marketplace listings for Max-Q and Server Edition, where stock is thinner, average **$22,000-23,000**. EU: about **€15,500-16,500 incl. VAT** (~$15,000-15,500 ex-VAT). Asia: about **$16,000-28,000** depending on country and tax (Japan Max-Q ~$16,400 and Workstation ~$19,400-21,700 incl. tax; Singapore ~$17,300; India up to ~$28,300 incl. GST). The 2025 launch price was about $8,500.

---

## 5. GeForce RTX 5090 (32 GB GDDR7)

- **Specs [vendor-spec]**, NVIDIA RTX Blackwell GPU architecture whitepaper, Appendix A, https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf (dense/sparse):
  - "Memory Bandwidth ... 1792 GB/sec" (28 Gbps, 512-bit); "TGP (Total Graphics Power) ... 575 W".
  - **FP8 dense: 838 TFLOPS with FP16 accumulate, 419 TFLOPS with FP32 accumulate** ("Peak FP8 Tensor TFLOPS with FP16 Accumulate ... 838/1676"; "with FP32 Accumulate ... 419/838").
  - FP4 dense 1676 (sparse 3352); BF16 dense 209.5 with FP32 accumulate (419 sparse). GeForce runs FP32-accumulate tensor math at half rate; the RTX PRO 6000 does not.
- **Price**: MSRP $1,999. Street prices in October 2026 are about **$5,000-7,000**:
  - GPU Poet, October 2026, https://gpupoet.com/gpu/learn/price/october-2026/nvidia-geforce-rtx-5090 **[tracker]**: "lowest average price" $6,460 (average of the three cheapest listings each day, eBay-based), daily range $5,986-$6,932.
  - GPU Poet market report dated 2026-10-01 (September data), https://gpupoet.com/gpu/market-report/gpu-market-report-october-2026 : best resale $4,795; "New on Amazon" $5,258 (August: $4,262); "140% over MSRP (about 2.4x)".
  - Reports of $8,500-$10,000 asking prices at Amazon/Newegg (tech-insider.org, TechRadar headline "prices skyrocket to $9,000") are **[unverified]** and describe single listings, not typical prices.

---

## 6. NVIDIA HGX B300 (8 GPUs) and cloud rental

### 6.1 Specs **[vendor-spec]**

| Item | Value | Source and quote |
|---|---|---|
| HBM per GPU | **288 GB HBM3E** | NVIDIA Technical Blog, 2025-08-22, https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/ : "288 GB HBM3E". Supermicro's HGX B300 datasheet gives "up to 2.3TB of total HBM3e memory" (8 x 288 GB). NVIDIA's HGX and DGX B300 pages list "Total Memory 2.1 TB" for 8 GPUs (~270 GB per GPU); the discrepancy is unexplained. |
| HBM bandwidth per GPU | **8 TB/s** | same blog: "8 TB/s" |
| **Dense FP8 per GPU (HGX B300)** | **4.5 PFLOPS** [estimate from NVIDIA's table] | HGX page, https://www.nvidia.com/en-us/data-center/hgx/ (read 2026-10-30): "FP8/FP6 Tensor Core² 72 PFLOPS" for 8 GPUs; footnote 2 "Specification in Sparse. Dense is ½ sparse spec shown." → 36 PFLOPS dense / 8 = 4.5 |
| Dense FP8 per GPU (Blackwell Ultra, GB300 class) | 5 PFLOPS | same blog, Table 2: "5 \| 10 PetaFLOPS" (dense \| sparse); "Up to 1,400W" TDP. The HGX (air-cooled, lower power) figure above is lower. |
| Dense FP4 per GPU (HGX B300) | 13.5 PFLOPS | HGX page: "FP4 Tensor Core¹ 144 PFLOPS \| 108 PFLOPS", footnote 1 "Specification in Sparse \| Dense" → 108 / 8 |
| Dense BF16 per GPU (HGX B300) | 2.25 PFLOPS | HGX page "FP16/BF16 Tensor Core² 36 PFLOPS" (sparse) → 18 dense / 8 |
| **Node power** | **~14-15 kW** | DGX B300 page, https://www.nvidia.com/en-us/data-center/dgx-b300/ : system power "~14 kW". Supermicro HGX B300 datasheet, https://www.supermicro.com/datasheet/Datasheet_Supermicro_NVIDIA_AI_Factories_HGX_B300.pdf : "eight 1100W TDP NVIDIA HGX B300 GPUs with up to 2.3TB of total HBM3e memory" and "Power per Rack (4-node) 60kW" (= 15 kW per node). GPU Server Values uses 15.5 kW per server (managedgpus.com sizing). |

### 6.2 Server price (8-GPU HGX B300 node)

| Source | Price | Date |
|---|---|---|
| Reuters (via Yahoo Finance) | **about $550,000 in the US** ("up from around $500,000 late last year"); about 7 million yuan (~$1 million) in China | 2026-04-30, https://finance.yahoo.com/sectors/technology/articles/exclusive-prices-nvidias-b300-server-064521420.html : "A B300 server, which houses eight B300 GPUs, is priced at about $550,000 in the United States" **[press]** |
| GPU Server Values (amcompute) | **$400K-$450K per node, new** (no fabric, racks, installation or support) | page updated 2026-10-17, data through Aug 2026, https://www.amcompute.com/gpu-server-values/b300 : "$400K-$450K per 8-GPU node new in the October 2026 Rack Report" **[tracker]** |
| Thunder Compute | $550,000-650,000 per 8-GPU system; $50,000-60,000 per GPU | 2026-10-09, https://www.thundercompute.com/blog/nvidia-b300-pricing (no named sources) **[tracker]** |
| Reseller listings | $496,728 (BIZON X9000 G5) to $795,000 (Supermicro AS-8126GS-NB3RT), excl. VAT | 2026-09-02, search snippet only **[unverified]** |

Working range: **about $400k-650k per node in the US; ~$500-550k typical for a single node bought at list.**

For comparison, Thunder Compute (updated 2026-10-23, https://www.thundercompute.com/blog/nvidia-b200-pricing) puts an 8-GPU HGX B200 server at $450,000-550,000 ("NVIDIA does not publish list prices; ranges reflect reseller and system-implied estimates") and a single B200 at $45,000-55,000 street **[tracker]**.

### 6.3 Cloud rental, on-demand, $ per GPU-hour

Hyperscaler figures were read on 2026-10-30 from the providers' own price files/APIs/pages:
AWS EC2 on-demand price file for us-east-1 Linux (published 2026-10-29), https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json ;
Azure Retail Prices API, https://prices.azure.com/api/retail/prices (East US, Linux, consumption);
Google Cloud accelerator-optimized pricing page, https://cloud.google.com/products/compute/pricing/accelerator-optimized?hl=en (region selector preset to "Iowa (us-central1)");
Oracle Cloud price list API, https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD .
Per-GPU figures are instance price / GPU count [estimate arithmetic].

| GPU | AWS | Azure | Google Cloud | Oracle |
|---|---|---|---|---|
| **B300** | **$17.80** (p6-b300.48xlarge $142.416/h) | not listed in the retail price API | not listed | **$15.00** ("Compute - GPU - B300", "GPU Per Hour"); GB300 $18.00 |
| **B200** | **$14.24** (p6-b200.48xlarge $113.9328/h) | no HGX B200 VM listed; GB200: $27.04 (ND128isr_NDR_GB200_v6 $108.16/h, 4 GPUs) | a4-highgpu-8g: on-demand "N/A"; DWS Flex-start $64.44/h = **$8.05**; DWS Calendar $90.22/h = $11.28; Spot $4.95; 1-yr CUD $11.12; 3-yr CUD $7.09 | **$14.00**; GB200 $16.00 |
| **H100** | **$6.88** (p5.48xlarge $55.04/h; p5.4xlarge 1 GPU $6.88/h) | **$12.29** (ND96isr_H100_v5 $98.32/h); $11.06 (ND96is_H100_v5 $88.488/h) | **$11.06** (a3-highgpu-8g $88.49/h); 3-yr CUD $4.86 | **$10.00** |
| H200 (reference) | $7.91 (p5en.48xlarge $63.296/h) | $10.60 (ND96isr_H200_v5 $84.80/h) | $10.60 (a3-ultragpu-8g $84.81/h) | $10.00 |
| RTX PRO 6000 Server (reference) | $4.14 (g7e.48xlarge $33.144/h, 8 GPUs; g7e.2xlarge 1 GPU $3.363/h) | — | — | — |

Neoclouds, on-demand $/GPU-hour, read 2026-10-30 from each provider's pricing page:

| Provider | B300 | B200 | H100 | Source |
|---|---|---|---|---|
| Nebius | **$9.50** (HGX B300) | $8.50 | $4.50 | https://nebius.com/prices |
| Lambda | not offered | $6.69 (8x) to $6.99 (1x) | $3.99 (8x SXM) to $4.29 (1x); PCIe $3.29 | https://lambda.ai/pricing |
| CoreWeave | on-demand "Contact sales"; spot $35.84/h per 8 = $4.48 | $8.60 ($68.80/h per 8) | $6.16 ($49.24/h per 8) | https://www.coreweave.com/pricing (North America) |
| RunPod | $8.99 Secure Cloud ($6.94 Community) | $7.99 ($5.98) | $3.99 SXM ($2.69); PCIe $2.89 | https://www.runpod.io/pricing |
| Modal (serverless, per second) | $7.10 ("$0.001972 / sec") | $6.25 ("$0.001736 / sec") | $3.95 ("$0.001097 / sec", H100 SXM5) | https://modal.com/pricing (hourly = per-second x 3600, my arithmetic) |

Other rates on the same pages: CoreWeave RTX PRO 6000 $2.50/GPU-h ($20.00/h per 8), GB200 NVL72 $10.50/GPU-h ($42.00/h per 4); RunPod RTX PRO 6000 $2.49, RTX 5090 $1.19 (Secure Cloud).
A search summary (underlying source not identified) says Nebius raised on-demand B200 from $5.50 to $8.50 and B300 from $6.10 to $9.50 during 2026, the last step effective 2026-10-01 **[unverified]**.

Summary (on-demand, per GPU-hour): **H100** $3.95-4.50 at Lambda/RunPod/Modal/Nebius, $6.16 CoreWeave, $6.88 AWS, $10-12.29 Oracle/GCP/Azure. **B200** $6.25-8.60 neoclouds, $14.00-14.24 Oracle/AWS (GCP only via DWS: $8.05 Flex-start). **B300** $7.10-9.50 neoclouds (Modal/RunPod/Nebius), $15.00 Oracle, $17.80 AWS; not listed by Azure or GCP; CoreWeave on request.

---

## 7. Workstation with one or two RTX PRO 6000

### 7.1 DDR5 RDIMM price per GB (late October 2026)

| Source | Figure | $/GB | Date | Quote / note |
|---|---|---|---|---|
| TrendForce DRAM spot, DDR5 16Gb (2Gx8) 4800/5600 chip | session average $61.333 (daily high $73.00, low $47.30) | chip cost alone ≈ $30.7/GB [estimate: 64 GB = 32 chips; ECC chips extra] | "Last Update 2026-10-30 11:00 (GMT+8)" | https://www.trendforce.com/price/dram/dram_spot |
| memoryindex.io, 64 GB DDR5 RDIMM | $2,058 per module | $32.2 | 2026-10-30 | https://memoryindex.io/chart/ddr5-rdimm-64 : "Derived: 32 × DDR5 16Gb spot plus ~6% for RCD, PMIC, PCB and assembly. Not a traded module quote." **[tracker]** |
| Citi note (May 2026), via ServNet UK | 64 GB RDIMM $873 in Q1 2026 → $1,586 forecast for Q4 2026 | $13.6 → $24.8 | 2026-05 | https://www.servnetuk.com/research/ddr5-server-memory-price-tracker-2026 : "projecting the unit price of a DDR5 64GB RDIMM rising from $873 in Q1 2026 to $1,586 by Q4 2026" **[press]** |
| ITLDC (hosting provider) | 64 GB RDIMM "now costs roughly 2.5 to 3 times its January price" | — | 2026-08-21 | https://itldc.com/en/blog/server-ram-ssd-market-update-2026 **[press]** |
| A-Tech (US memory brand, Shopify store), DDR5-6400 RDIMM | 96 GB $4,062.55; 128 GB $5,431.33; 64 GB kit (2x32 GB) $2,930.38; all "available" | **$42.3 / $42.4 / $45.8** | store data updated 2026-10-29 | https://www.atechmemory.com/products.json **[vendor-live]** |
| Tecisoft (reseller), Samsung M321R8GA0PB2-CCP 64 GB DDR5-6400 RDIMM | $4,066.95, available | $63.5 | updated 2026-10-29 | https://www.tecisoft.com/products/samsung-m321r8ga0pb2-ccp-64gb-ddr5-rdimm **[vendor-live]** |
| Saitech (reseller), same Samsung part | $3,444.00, not available | $53.8 | updated 2026-10-29 | https://esaitech.com/products/samsung-64gb-ddr5-6400-rdimm-m321r8ga0pb2-ccp **[vendor-live]** |

**Estimate:** contract/spot-derived cost is about **$25-35/GB**; what a small buyer pays at retail for in-stock DDR5-6400 RDIMMs is about **$42-64/GB**. For a workstation budget I use **~$45/GB** (256 GB ≈ $11.5k; 512 GB ≈ $23k) [estimate]. Older listings at $5-12/GB (e.g. AvaDirect $338 for 64 GB) are 2025 prices and stale.

### 7.2 CPUs and motherboards

Component prices in 7.2-7.3 and the platform totals in 7.4 were collected by a helper agent on 2026-10-30 from retailer pages and store APIs (BuildCores and MaxMyBuild aggregators, esaitech.com and SabrePC store data, AMD.com, Corsair, Samsung); "available=False" means the listing exists but cannot be bought now.

| Part | Launch MSRP | Current US price (2026-10-30) | Source |
|---|---|---|---|
| Threadripper 9960X (24C) | $1,499 | **$1,395** (Amazon); Newegg/B&H $1,449.99 | https://www.buildcores.com/products/CPU/z77n6bd90/AMD-Ryzen-Threadripper-9960X ("$1,395.00 via Amazon") |
| Threadripper 9970X (32C) | $2,499 | no in-stock offer found; esaitech $2,496 (available=False); SabrePC $2,669.87 "Out of Stock"; Amazon deal $2,000 on 2026-07-03 | https://www.sabrepc.com/100-100001594WOF-AMD-S161530807 ; PC Guide deal post |
| Threadripper 9980X (64C) | $4,999 | **$4,819** (Newegg) | https://www.buildcores.com/products/CPU/wuuleew67/AMD-Ryzen-Threadripper-9980X |
| Threadripper PRO 9955WX (16C) | $1,649 | **$1,549** (Amazon, Walmart, B&H) | https://www.buildcores.com/products/CPU/873mwfjow/AMD-Ryzen-Threadripper-PRO-9955WX |
| Threadripper PRO 9965WX (24C) | $2,899 | scarce: MemoryC $3,760.37; esaitech $2,781 (available=False) | BuildCores |
| Threadripper PRO 9975WX (32C) | $4,099 | **$4,099.99** (Amazon) | https://www.buildcores.com/products/CPU/zldrztnms/AMD-Ryzen-Threadripper-PRO-9975WX |
| EPYC 9355P (32C) | $2,998 (Oct 2024) | AMD "1kU Pricing" now **$2,598**; street **$3,408.60 in stock** (SabrePC); esaitech $2,722 special order | https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9355p.html ; https://www.sabrepc.com/100-000001521-AMD-S184203267 |
| EPYC 9555P (64C) | $7,983 | AMD 1kU now **$6,130**; street $4,855 (esaitech, special order) to $5,427 (SabrePC, out of stock) | https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9555p.html |
| ASUS Pro WS TRX50-SAGE WIFI A (TRX50, 4-ch) | ~$999.99 MSRP | **$960** (esaitech, available) | esaitech store data |
| Gigabyte TRX50 AERO D / ASRock TRX50 WS | $599 / $799 (2023) | $626 / $747 (esaitech, both available=False) | esaitech store data |
| ASUS Pro WS WRX90E-SAGE SE (WRX90, 8-ch) | $1,299.99 | **$1,248** (esaitech, available) | esaitech store data |
| ASRock WRX90 WS EVO | — | $1,114 (available=False) | esaitech store data |
| Supermicro H14SSL-NT-O (SP5, 12-ch) | — | **$837** (esaitech, available) | esaitech store data |
| Supermicro H13SSL-N-O (SP5) | — | $638.79 (available=False) | esaitech store data |

Threadripper launch MSRPs: Phoronix, 2025-07-25, https://www.phoronix.com/news/AMD-Threadripper-9000-31-July : "The 24-core Threadripper 9960X is expected to go for $1499 USD, the 32-core Threadripper 9970X for $2499 USD, and the 64-core Threadripper 9980X for $4999 USD." CPU and board prices have not risen like memory and SSDs; EPYC list prices have fallen.

### 7.3 PSU, chassis, NVMe

| Part | Price (US, 2026-10-30) | Source / note |
|---|---|---|
| Corsair HX1500i (2025), ATX 3.1 (1 GPU) | $389.99 (previous HX1500i $319.99 at Amazon) | https://retail.corsair.com/products/hx1500i-fully-modular-ultra-low-noise-platinum-atx-1500-watt-pc-power-supply-cp-9020309-na ; https://www.maxmybuild.com/power-supplies/corsair-hx1500i |
| 1600 W ATX 3.1 on 115 V (2 GPUs): MSI MPG 1600W / Seasonic PRIME PX-1600 / TX-1600 | $499.99 / $505.99 / $559.99 | MaxMyBuild pages (Amazon / B&H / Amazon offers) |
| 2200 W units (need a 200-240 V circuit): Super Flower Leadex Titanium 2200W / ASUS Pro WS 2200W | $549.99 / $569.99 | MaxMyBuild; Seasonic PX-2200 is not sold in the US ("MSRP PRIME PX-2200 \| N/A (USA)", "AC Input Range: 200 - 240 Vac only", https://seasonic.com/news/sea-sonic-to-launch-the-new-prime-px-2200/) |
| Chassis: Phanteks Enthoo Pro 2 Server / Fractal Define 7 XL | $179.99 / $254.99 | https://www.buildcores.com/products/PCCase/bdv1wc9rj/Phanteks-Enthoo-Pro-2-Server-Edition-ATX-Full-Tower-Black ; https://www.buildcores.com/products/PCCase/mfjs8wut8/Fractal-Design-Define-7-XL-ATX-Full-Tower-Dark-Tinted-Tempered-Glass |
| NVMe 4 TB: Crucial T705 / WD_BLACK SN8100 / Samsung 9100 PRO | $629.99 / $768 / $987 (Samsung.com list $1,359.99) | https://www.maxmybuild.com/storage/nvme-ssds/samsung-9100-pro/4tb ("Samsung 9100 PRO 4TB costs $987.00 right now") and sibling pages |
| NVMe 8 TB: Samsung 9100 PRO / WD_BLACK SN8100 | $1,949.99 / $2,149.99 | MaxMyBuild |
| CPU cooler (Noctua NH-U14S TR5-SP6 / Arctic Freezer 4U-SP5) | ~$130-170 / ~$50-55 | 2023-2025 data only (stale) |

Consumer SSD prices rose sharply: Samsung 9100 PRO 4 TB was $349 in Oct 2025 (Notebookcheck, https://www.notebookcheck.net/Samsung-9100-Pro-SSD-with-8TB-and-14-800MB-s-drops-to-lowest-price-ever-on-Amazon.1133591.0.html) and is $987 now (+183%) [estimate arithmetic]. Notebookcheck, 2026-10-25, https://www.notebookcheck.net/SSD-prices-explode-by-303-in-a-year-as-AI-fuels-NAND-flash-shortage.1433261.0.html : "The contract price of a 256GB TLC SSD reached approximately $134.20 in the third quarter of 2026, up from $33.30 a year earlier."

### 7.4 Totals [estimate]

Platform parts only (CPU + board + PSU + case + one 4 TB NVMe + cooler; no GPU, no RAM), from the prices above:

| Build | Low (cheapest listed, some out of stock) | Typical (in stock / near MSRP) |
|---|---|---|
| TRX50, 1 GPU | $3,281 (9960X, AERO D, HX1500i, Enthoo Pro 2, T705) | $5,039 (9970X, TRX50-SAGE, HX1500i 2025, Define 7 XL, SN8100) |
| TRX50, 2 GPUs | $3,461 | $5,209 (1600 W PSU) |
| WRX90, 2 GPUs | $4,103 (9955WX) | $7,101 (9975WX, WRX90E-SAGE SE) |
| EPYC SP5, 2 GPUs | $4,721 (9355P special order) | $5,884 (9355P in stock, H14SSL-NT); $7,902 with 9555P |

Whole workstation, assuming RTX PRO 6000 Workstation Edition at $16,000 (NVIDIA list) to $17,300 (US street average, section 4) and DDR5-6400 RDIMM at $42-46/GB (A-Tech, section 7.1):

| Build | Platform | GPU(s) | RAM | **Total** |
|---|---|---|---|---|
| **1 GPU**, TRX50, 128 GB (4 x 32 GB) | $3.3-5.0k | $16.0-17.3k | $5.4-5.9k | **≈ $25-28k** |
| 1 GPU, TRX50, 256 GB (4 x 64 GB) | $3.3-5.0k | $16.0-17.3k | $10.8-11.7k | ≈ $30-34k |
| **2 GPUs**, TRX50, 256 GB | $3.5-5.2k | $32.0-34.6k | $10.8-11.7k | **≈ $46-52k** |
| 2 GPUs, WRX90 or EPYC, 256 GB (8 x 32 GB) | $4.1-7.9k | $32.0-34.6k | $10.8-11.7k | ≈ $47-54k |
| 2 GPUs, any platform, 512 GB | add ~$11-12k to the 256 GB row | | | ≈ $57-66k |

With RAM at the $25-35/GB contract/spot level instead of retail, subtract about $0.9-2.7k per 128 GB. The second GPU costs almost nothing beyond the card itself (+$170-180 for the bigger PSU).

### 7.5 Vendor-built systems with RTX PRO 6000 (US, read 2026-10-30)

| System | Configuration | Price | Source |
|---|---|---|---|
| **Puget Systems** Multi GPU Workstation | TR PRO 9975WX, **2x RTX PRO 6000 Max-Q**, 256 GB RDIMM, 2x2 TB, 3-yr parts | **$52,412.24** "Price as Configured"; Puget's per-GPU option delta is $15,184.16, so the non-GPU part is ~$22,044 [estimate] | https://www.pugetsystems.com/solutions/ai-and-hpc-workstations/machine-learning-ai/ |
| Puget Quad GPU Rackmount (as configured with 2 GPUs) | TR PRO 9975WX, 2x Max-Q, 512 GB, 240 V PSU | $63,861.73 | same |
| **Puget 4 GPU LLM Server** | EPYC 9375F, **4x RTX PRO 6000 Max-Q**, 768 GB, 2U | **$106,514.40** | Puget configurator buy-449, linked from https://www.pugetsystems.com/solutions/ai/deploy/ |
| Puget 8 GPU LLM Server | 8x RTX PRO 6000 Server Edition, 1.5 TB (summary card; CPU line inconsistent with the configurator) | $219,404.75 | https://www.pugetsystems.com/solutions/ai/enterprise-scale/ |
| **System76 Thelio Mega** | TR PRO 9955WX, 64 GB ECC, 1 TB; **1x RTX PRO 6000** / **2x Max-Q** / 3x Max-Q | **$27,338 / $45,978 / $64,624** (in stock per the store API) | https://system76.com/desktops/thelio-mega |
| ASUS ExpertCenter Pro ET900A X9 (via monitors.com, reseller) | TR PRO 9955WX, 256 GB, **2x RTX PRO 6000**, 2000 W PSU | $50,675.89 | monitors.com store data |
| HP Z6 G5 A (via monitors.com) | TR PRO 9955WX, 128 GB, 1x RTX PRO 6000 | $26,652.05 | monitors.com store data |
| HP Z8 Fury G5 / Dell Precision 7960 / Lenovo ThinkStation P5 (via monitors.com) | Xeon W, 64-128 GB, 1x RTX PRO 6000 | $23,430 / $27,924 / $24,349 | monitors.com store data |
| Dell Pro Max Tower T2 | Core Ultra 5 235, 8 GB, 256 GB, 1x RTX PRO 6000 (edition not stated) | $15,149 at Dell (not verified on dell.com) | TechRadar, 2026-10-20, https://www.techradar.com/pro/dells-pro-max-tower-t2-workstation-costs-less-than-the-nvidia-blackwell-gpu-inside-it : "Dell Pro Max Tower T2 workstation with Blackwell GPU for $15,149 at Dell" |
| **Supermicro SYS-422GA-NRT-01-G2** (via AVADirect) | 2x Xeon 6960P, **4x RTX PRO 6000 Server Edition**, 1 TB DDR5-6400, 4x 3200 W | **$108,039** "Configured price" | https://www.avadirect.com/Supermicro-GPU-SuperServer-SYS-422GA-NRT-01-G2-4U-Rackmount-Gold-Series-version-with-pre-configured-components-server/Configure/19917291 |
| BIZON X5500 G2 | from $9,076 base; RTX PRO 6000 option $19,321.50 each | 2-GPU lower bound ≈ $47.7k [estimate] | https://bizon-tech.com/bizon-x5500.html |
| Exxact Valence VWS-135223847 (TR PRO, up to 4 GPUs) / TensorEX TWS-198830577 (EPYC, up to 2 GPUs) | "Starting Price" only; the configuration behind it is not shown | $15,616.70 / $16,354.80 | https://www.exxactcorp.com/Exxact-VWS-135223847-E135223847 ; https://www.exxactcorp.com/Exxact-TWS-198830577-E198830577 |

Integrators charge $15,184 (Puget), ~$18,340-18,650 (System76) and $19,321.50 (BIZON) per RTX PRO 6000. Lambda no longer sells workstations: "Lambda has ended its on-premise hardware business ... as of August 29, 2025." (https://lambda.ai/legacy-hardware).
Not found: Lenovo ThinkStation PX, Dell PowerEdge and Gigabyte 4-GPU server prices with RTX PRO 6000 in the US; full configured BIZON and Exxact totals.

## 8. Enterprise NVMe SSD price per TB

Research for this item was done by a helper agent on 2026-10-30; its full notes, with every listing, are summarized here. $/TB = price ÷ nominal decimal capacity [estimate arithmetic].

### 8.1 Market context: TrendForce enterprise-SSD contract prices, quarter on quarter **[press]**

| Quarter | Change | Source |
|---|---|---|
| 1Q26 (revised) | "Above 70%" | TrendForce report, 2026-02-12, https://www.trendforce.com/research/download/RP260212NQ : "Enterprise SSD Experienced another ASP Hike to Above 70% in 1Q26" |
| 2Q26 | +48-53% | TrendForce, 2026-04-24, https://www.trendforce.com/research/download/RP260427NK : "Contract Prices of Enterprise SSD Continue to Surge by 48-53% in 2Q26" |
| 3Q26 | +20-25% | TrendForce, 2026-07-29, https://www.trendforce.com/research/download/RP260728RU : "Contract Price Hikes on Enterprise SSD Subsided to 20-25% in 3Q26" |
| 4Q26 forecast | +23-28% (all NAND +15-20%) | TrendForce, 2026-09-24, https://www.trendforce.com/research/download/RP260924PL : "4Q26 Contract Prices for Enterprise SSD Surge 23-28% QoQ Against Trend"; press release 2026-09-30, https://www.trendforce.com/presscenter/news/20260930-13258.html |

Compounded (with +25% for 4Q25): about **3.9x from 3Q25 to 3Q26**, ~4.9x to 4Q26 [estimate]. TrendForce's absolute $/GB contract levels are paywalled (not found).

VDURA Flash Volatility Index, Q3 2026 (StorageReview, 2026-08-18, https://www.storagereview.com/news/enterprise-ssd-prices-run-at-6-5x-last-year-vdura-pegs-a-30tb-tlc-drive-at-22600) **[press]**: "places the price of a 30TB TLC enterprise SSD at $22,600, compared with $3,460 in Q3 2025" and "A 30TB QLC SSD now costs $18,080, up from $2,768" → about **$736/TB TLC and $589/TB QLC** (VDURA sells hybrid flash+HDD systems, so it has an interest in high flash prices; basis — street, contract or list — not stated).

### 8.2 US listings, late October 2026

In stock, new, SabrePC (data from SabrePC's public product API, `"condition":"New"`, inventory > 0, read 2026-10-30; product pages checked where marked ✓) **[vendor-live]**:

| Drive | Capacity / NAND / form factor | Price | $/TB | URL |
|---|---|---|---|---|
| Kioxia CD8P-R KCD8XPJE15T3 ✓ | 15.36 TB TLC, E3.S Gen5 | $10,730.82 | 699 | https://www.sabrepc.com/KCD8XPJE15T3-Kioxia-S7964311 |
| Kioxia CD8-R KCD8XRUG15T3 | 15.36 TB TLC, U.2 Gen4 | $11,820 | 770 | https://www.sabrepc.com/KCD8XRUG15T3-Kioxia-S6942818 |
| Micron 7600 PRO ✓ | 15.36 TB TLC, E3.S Gen5 | $13,971.43 | 910 | https://www.sabrepc.com/MTFDLBQ15T3THG-1BP1DFCYYR-Micron-S9282341 |
| Solidigm D7-P5520 | 15.36 TB TLC, U.2 Gen4 | $14,250 | 928 | https://www.sabrepc.com/SSDPF2KX153T11Z-Solidigm-S8112628 |
| Solidigm D7-PS1010 ✓ | 15.36 TB TLC, U.2 Gen5 | $16,395 | 1,067 | https://www.sabrepc.com/SB5PH27X153T001-Solidigm-S8084130 |
| Micron 9550 PRO | 15.36 TB TLC, E3.S Gen5 | $18,286.26 | 1,191 | https://www.sabrepc.com/MTFDLBQ15T3THA-1BK1DABYYR-Micron-S161614233 |
| Micron 6550 ION ✓ | 30.72 TB TLC, E3.S Gen5 | $13,993.50 | 456 | https://www.sabrepc.com/MTFDLBQ30T7THL-1BK1DFCYYR-Micron-S8797287 |
| Micron 9550 PRO | 30.72 TB TLC, U.2 Gen5 | $35,109.62 | 1,143 | https://www.sabrepc.com/MTFDLAL30T7THA-1BK1DABYYR-Micron-S109173291 |
| Kioxia CD9P-R ✓ | 61.44 TB TLC, U.2 Gen5 | $36,480 | 594 | https://www.sabrepc.com/KCD9XPUG61T4-Kioxia-S10396073 |
| Micron 6550 ION | 61.44 TB TLC, U.2 Gen5 | $47,498.43 | 773 | https://www.sabrepc.com/MTFDLAL61T4THL-1BK1DFCYYR-Micron-S8797281 |
| Solidigm D5-P5336 ✓ | 61.44 TB **QLC**, U.2 Gen4 | $47,295 | 770 | https://www.sabrepc.com/SBFPF2BV614T001-Solidigm-S7402588 (SabrePC change log: $34,509 on 2026-06-17, so about +37% since) |

Other new-drive prices (special order or out of stock; **weaker evidence**):

- Saitech (special order "from the OEM", read 2026-10-30): Samsung PM9D3a 30.72 TB U.2 $16,516 ($538/TB); Micron 6600 ION 61.44 TB QLC $37,694 ($614/TB); Micron 6600 ION 30.72 TB QLC $20,276 ($660/TB); Solidigm D5-P5336 61.44 TB $33,107 ($539/TB); Kioxia CD8-R 15.36 TB SED $7,195 ($468/TB). URLs: https://esaitech.com/products/samsung-mzwl630thblf-00aw7-30-72tb-solid-state-drive , https://esaitech.com/products/micron-mtfdlal61t4qhf-1bq1dfcyyr-61-44tb-u-2-ssd , https://esaitech.com/products/solidigm-sbfpf2bv614t001-d5-p5336-61-44tb-2-5-inch-ssd .
- Zones: Solidigm D5-P5336 61.44 TB E1.L $36,098.99 ($588/TB), https://www.zones.com/site/product/index.html?id=114604807 .
- SabrePC out-of-stock list prices: Samsung PM1743 15.36 TB $9,666-10,313 ($629-671/TB); PM9D3a 15.36 TB E3.S $9,480 ($617/TB); D5-P5336 30.72 TB $13,670-17,987 ($445-586/TB); Samsung BM1743 30.72/61.44 TB QLC ~$509-512/TB.
- Search snippets only (CDW, ShopBLT, CompSource, Tech-America; pages blocked; undated) **[unverified]**: D5-P5336 61.44 TB at $25,528-28,949 ($416-471/TB).

### 8.3 Typical price per TB, late October 2026 [estimate]

- **TLC, 15.36 TB class (U.2/E3.S), new, in stock: about $700-1,200/TB, median ~$920/TB**; working figure **~$750-950/TB** (Gen5 high-performance drives sit at the top, read-intensive Gen4 at the bottom; special-order quotes go down to ~$470-540/TB).
- **High-capacity TLC (30.72-61.44 TB: Micron 6550 ION, Kioxia CD9P-R, Samsung PM9D3a 30.72): ~$450-775/TB.**
- **QLC, 30.72-122.88 TB: ~$550-650/TB working figure** (page-verified listings $512-770/TB). In the late-2026 channel QLC is not reliably cheaper per TB than capacity TLC.
- 2025 levels were about $100-113/TB TLC and $80-90/TB QLC (VDURA Q2-Q3 2025); 2025 prices understate late-2026 costs by roughly 5-8x.

---

## 9. US colocation and industrial electricity

Also researched by the helper agent on 2026-10-30; condensed here.

### 9.1 Colocation, $ per kW per month

Wholesale rates normally exclude energy, which is billed as a pass-through ("+E"): datacenterHawk, 2026-02-12, https://datacenterhawk.com/resources/fundamentals/colocation-data-center-pricing-a-2026-beginner-s-guide : "electricity costs are handled as pass-through charges, often referred to as + E". CBRE says only that its "Rental rates are quoted asking rates for 250+ kW at N+1/Tier III requirements" [inference: energy excluded].

| Metric | $/kW-month | Period | Source and quote |
|---|---|---|---|
| CBRE primary-market average, 250-500 kW | **$196.25** (+6.6% YoY) | H2 2025 | CBRE North America Data Center Trends H2 2025, published 2026-02-25, https://www.cbre.com/insights/books/north-america-data-center-trends-h2-2025 : "rose by 6.6% year-over-year to a record $196.25 per kW/month" **[press]** |
| same, H1 2026 | **~$205** [estimate: $196.25 x 1.043] | H1 2026 | CBRE H1 2026, published 2026-08-27, https://www.cbre.com/insights/books/north-america-data-center-trends-h1-2026 : "Average asking rates for 250-to-500-kW requirements across primary markets rose by 4.3% in H1" (no dollar level in the text); 10+ MW +6.7%; primary-market vacancy "a record low of 1.4%" |
| CBRE outlook | "above $215" (250-500 kW) | 2026 | https://www.cbre.com/insights/books/us-real-estate-market-outlook-midyear-review-2026/data-centers : "We expect average rental rates for 250-500kW requirements to be above $215 per kW per month." |
| Northern Virginia, 250-500 kW | $190-235 | Q1 2026 | CBRE Global Data Center Trends 2026, 2026-06-17, https://www.cbre.com/insights/reports/global-data-center-trends-2026 : "Northern Virginia with a broader price range of $190 to $235" |
| Northern Virginia, 10+ MW | $160-185 | H1 2026 | CBRE H1 2026 N. Virginia chapter: "asking rates for 10-plus-MW requirements rose to $160 to $185 per kW"; vacancy 0.24% |
| Chicago, 250-500 kW | $200-230 (+14.7% YoY) | Q1 2026 | CBRE press release 2026-06-24, https://www.cbre.com/press-releases/global-data-center-supply-cant-keep-up-with-demand-resulting-in-extreme-scarcity-of-available-space : "Chicago had the highest rental rates, ranging from $200 to $230 per kW/month for a 250-to-500-kW requirement" |
| Silicon Valley | $200-275 | H1 2026 | CBRE press release 2026-09-01, https://www.cbre.com/press-releases/silicon-valley-data-center-demand-continues-outpace-supply-causing-vacancy-fall-further-rents-rise : "Asking rental rates in Silicon Valley range from $200 to $275 per kW per month" |
| Large / hyperscale deals | $145-170 (NNN deals $15-25 lower) | early 2026 | datacenterHawk, 2026-03-16, https://datacenterhawk.com/resources/market-insights/2026-data-center-deal-trends : "At $145–$170/kW ..."; "Primary NA markets have moved $25–30/kW in a single calendar year." |
| Digital Realty, signed Americas leases (GAAP base rent) | 0-1 MW (retail): $256 / $293 / $284; >1 MW: $174 / $156 / $264 | Q1 / Q2 / Q3 2026 | DLR 8-K exhibits, e.g. Q3 2026 (2026-10-29), https://www.sec.gov/Archives/edgar/data/0001297996/000110465926120212/dlr-ex99d1.htm : "0-1 MW | $39,587 | 11.6 | $284"; "> 1 MW | 203,002 | 64.0 | 264". Utilities are reported separately as tenant reimbursements [inference: energy excluded]. |
| Retail rack, all-in (vendor blog) | ~$250 "all-in"; a 20 A/208 V rack at $1,000-1,500/month ≈ $300-450 per usable kW [estimate] | 2026-04-01 | Inflect (a colocation marketplace), https://inflect.com/blog/colocation-pricing-what-to-expect-for-racks-cabinets-and-cages-in-2026 : "Fixed all-in kW rate (~$250/kW/month, covering space, power delivery, and cooling)" |

Not found: 2026 dollar figures for Dallas, Phoenix and Atlanta (CBRE: Dallas asking rents "unchanged" in Q1 2026; Atlanta +2% YoY); any JLL, Cushman & Wakefield or Uptime $/kW figure (JLL: rents "increased nearly 70% since 2020", vacancy 1%, https://www.jll.com/en-us/newsroom/data-center-demand-exceeds-expectations-in-h1-2026).

**Working figures [estimate]:** wholesale 250-500 kW in primary markets **~$200-215/kW-month** (range $160-275 by market and size), large deals $145-185, retail 0-1 MW **~$250-300**, all excluding energy (retail rack quotes often bundle energy).

### 9.2 US electricity prices (EIA Electric Power Monthly, data for August 2026, released 2026-10-23) **[vendor-spec: government statistics]**

Table 5.3, https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_3 (cents/kWh; 2026 values are preliminary; averages are revenue ÷ sales, so demand charges are included):

| Period | Industrial | Commercial | Row quote (Residential, Commercial, Industrial, Transportation, All) |
|---|---|---|---|
| **August 2026** | **9.64** | 14.47 | "August 18.16 14.47 9.64 14.86 14.87" |
| **2026 year to date (Jan-Aug)** | **9.09** | 14.04 | "2026 18.19 14.04 9.09 15.64 14.37" |
| 2025 annual | 8.51 | 13.37 | "2025 17.23 13.37 8.51 13.87 13.56" |

State examples (Tables 5.6.A/B, https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a ), industrial / commercial, August 2026 (YTD in brackets): **Virginia 9.98 / 11.14 (10.07 / 11.20)**; **Texas 7.21 / 8.96 (6.77 / 8.60)**; Arizona 9.73 / 13.05; Oregon 8.75 / 10.72; Washington 7.43 / 11.81; Ohio 9.75 / 12.31; Illinois 11.33 / 14.67; California 24.12 / 30.02.

Outlook: EIA Short-Term Energy Outlook, 2026-10-06, https://www.eia.gov/outlooks/steo/report/elec_coal_renew.php : "We forecast wholesale prices in the PJM region this year will increase by 41% compared with 2025" (PJM includes Virginia).

**Typical US industrial electricity: ~9-10 ¢/kWh in 2026 (9.09 ¢ YTD, 9.64 ¢ in August).**

---

## Not confirmed or not found

- **Live US retailer or NVIDIA marketplace pages** for DGX Spark and RTX PRO 6000 could not be read from this host (timeouts or HTTP 403); their prices rest on dated press reports and trackers (dates given above).
- **DGX Spark**: heise reports $6,000 for the 128 GB model against $6,950 from The Register, ServeTheHome and Hardware Busters; partner 128 GB GB10 prices after the October increase not found. NVIDIA publishes no dense FP8/BF16 figures for GB10; the peaks above are estimates, the measured values are from StorageReview and the NVIDIA forum.
- **HP Z2 Mini G1a 128 GB**: no hp.com US price; only undated reseller snippets.
- **Apple TFLOPS**: Apple publishes none. No measured matmul figure for M5 Pro or M5 Ultra; the M5 Max 60 TFLOPS figure is from a single developer post (GPU core count not stated). BF16 support on the M5 neural accelerators is undocumented. M3 Max FP16 is an estimate.
- **Radeon 8060S** measured GEMM throughput (36.9 TFLOPS with hipBLASLt) seen only in search snippets.
- **RTX PRO 6000 Server Edition** dense figures are derived (NVIDIA lists 2:1 sparse-looking numbers without a footnote); EU listing at €11,054 is an outlier.
- **RTX 5090** asking prices of $8,500-10,000 reported by some outlets are unverified single listings.
- **HGX B300**: total memory 2.1 TB (NVIDIA pages) vs 2.3 TB (Supermicro, 8 x 288 GB) not reconciled; reseller server listings ($497k-795k) seen only in snippets; Reuters' $550k is from April 2026.
- **Cloud**: Azure and Google Cloud list no B300/GB300 on-demand price; CoreWeave B300 on-demand is "Contact sales"; Lambda does not offer B300. GCP offers B200 (A4) only via DWS, spot or commitments, not plain on-demand.
- **Workstation parts**: Threadripper 9970X in-stock price; 9965WX at a major retailer; in-stock prices for ASRock TRX50 WS, Gigabyte TRX50 AERO D, ASRock WRX90 WS EVO; Supermicro H14SSL-N (non-NT), ASRock Rack GENOAD8X-2T / TURIND8UD-2T; be quiet! Dark Power Pro 13 1600W, Meshify 2 XL, Lian Li V3000 Plus; current cooler prices; Lenovo ThinkStation PX, Dell PowerEdge and Gigabyte 4-GPU servers with RTX PRO 6000; full BIZON/Exxact totals; the Dell T2 $15,149 price on dell.com; which RTX PRO 6000 edition the reseller and Dell listings include.
- **DDR5 RDIMM**: no large US retailer (Newegg, CDW, B&H) price could be read; the retail range rests on A-Tech, Tecisoft and Saitech store data; TrendForce contract $/GB is paywalled.
- **Enterprise SSD**: TrendForce absolute $/TB (paywalled); in-stock new listings for Samsung PM9A3/PM1743/PM9D3a 15.36 TB, Solidigm D5-P5336 30.72 TB, Kioxia CM7-R, Samsung BM1743; VDURA's pricing basis.
- **Colocation**: CBRE H1 2026 dollar averages (text gives % changes only); 2026 $/kW for Dallas, Phoenix and Atlanta; any JLL, Cushman & Wakefield or Uptime $/kW figure; whether CBRE asking rates include energy (inferred: they do not).

---

## Appendix A: helper-agent notes for item 7 (workstation parts and vendor systems), 2026-10-30

Verbatim notes from the helper agent; "I" refers to that agent. Labels: LIVE = fetched 2026-10-30; SNIPPET = search snippet only; STALE = older than Aug 2026; ESTIMATE = its arithmetic.

### Item 7: workstation build prices around 1-2 x RTX PRO 6000 Blackwell (non-GPU, non-RAM parts)

Prepared 2026-10-30. All prices are US dollars before tax unless marked otherwise.

#### Labels

- **LIVE**: I fetched the page or the store's own price API on **2026-10-30** and read the number from it. The data date is 2026-10-30 unless stated otherwise.
- **SNIPPET**: the number comes only from a web-search result snippet. I could not open the page (HTTP 403, bot check, or rate limit). Treat it as unverified.
- **STALE**: the data is older than Aug 2026. Launch MSRPs are stale by definition, but they are given as reference points.
- **ESTIMATE**: my own arithmetic or inference. Nothing in an estimate is quoted from a source.

#### Sources that worked, and how

- **BuildCores** (buildcores.com): server-rendered "Best Price" and retailer rows showing Amazon, Newegg, Walmart, B&H and MemoryC prices. It is an affiliate aggregator, and the pages show no timestamp.
- **MaxMyBuild** (maxmybuild.com): US offers marked "Checked daily", with 30- and 60-day lows.
- **esaitech.com**: Shopify `search/suggest.json`, which returns price and an `available` flag. It is a USD reseller, and many items are special order.
- **SabrePC**: product pages with JSON-LD prices.
- **AMD.com**: product pages showing "1kU Pricing".
- **Corsair**: retail.corsair.com Shopify `.js` and suggest endpoints.
- **Samsung.com/us**: JSON-LD on the business store page.
- **Puget Systems**: configurator HTML.
- **System76**: BigCommerce price API (POST `/remote/v1/product-attributes/760`, read-only).
- **BIZON**: configurator JSON embedded in the page.
- **Exxact**: product pages.
- **monitors.com**: Shopify suggest JSON. It is a reseller with high markups.
- **AVADirect**: through WebFetch.

Blocked (403 or bot check): newegg.com, neweggbusiness.com, bhphotovideo.com, microcenter.com, centralcomputer.com, cdw.com, shi.com, tweaktown.com, dell.com, store.supermicro.com (curl), phanteks.store, camelcamelcamel.com and digitalcitizen.life. Esaitech returned HTTP 429 for a while and later recovered.

---

#### 1. CPUs

##### 1a. Threadripper 9000 (HEDT, sTR5, TRX50, 4-channel DDR5 RDIMM, 350 W)

**Launch MSRP** (STALE, July 2025). Phoronix, 25 Jul 2025, https://www.phoronix.com/news/AMD-Threadripper-9000-31-July (LIVE):
> "The 24-core Threadripper 9960X is expected to go for $1499 USD, the 32-core Threadripper 9970X for $2499 USD, and the 64-core Threadripper 9980X for $4999 USD."

| Model (box P/N) | Launch MSRP | Street price, 2026-10-30 (LIVE unless marked) |
|---|---|---|
| 9960X 24C (100-100001595WOF) | $1,499 | **Amazon $1,395.00**; Walmart $1,399.00; Newegg $1,449.99; B&H $1,449.99; MemoryC $1,836.20 (BuildCores, https://www.buildcores.com/products/CPU/z77n6bd90/AMD-Ryzen-Threadripper-9960X, quote "$1,395.00 via Amazon"). esaitech $1,487.00, available=True ("AMD 100-100001595WOF Ryzen Threadripper 9960X 24-Core 4.2GHz sTR5 Processor \| 1487.00"). |
| 9970X 32C (100-100001594WOF) | $2,499 | No in-stock price confirmed. esaitech $2,496.00, available=False. SabrePC **$2,669.87, "Out of Stock"** (https://www.sabrepc.com/100-100001594WOF-AMD-S161530807). Most recent deal (STALE-ish, 3 Jul 2026): PC Guide, https://www.pcguide.com/deals/amds-powerful-ryzen-threadripper-9970x-sinks-to-lowest-ever-price-at-amazon-a-workstation-gem/ : "it's now at its lowest price ever on Amazon, down to $2,000, with a saving of $500". |
| 9980X 64C (100-100001593WOF) | $4,999 | **Newegg $4,819.00**; Walmart $5,481.05; MemoryC $6,092.76; Amazon N/A (BuildCores, https://www.buildcores.com/products/CPU/wuuleew67/AMD-Ryzen-Threadripper-9980X). esaitech $4,842.00, available=True. SabrePC $5,340.88, "Out of Stock" (https://www.sabrepc.com/100-100001593WOF-AMD-S172670832). |

Street prices against MSRP (ESTIMATE): 9960X -6.9% (1,395/1,499); 9980X -3.6% (4,819/4,999).

##### 1b. Threadripper PRO 9000 WX (sTR5, WRX90, 8-channel, 350 W)

**Launch SEP** (STALE, 17 Jul 2025). Tom's Hardware table syndicated on Yahoo, https://tech.yahoo.com/computing/articles/amd-launches-threadripper-pro-9000-175008741.html (LIVE). Table rows: "Threadripper Pro 9975WX | $4,099", "Threadripper Pro 9965WX | $2,899", "Threadripper Pro 9955WX | $1,649". The same article: "The Threadripper Pro 9995WX has a SEP (Suggested Etail Price) of $11,699".

| Model | Launch SEP | Street price, 2026-10-30 (LIVE) |
|---|---|---|
| 9955WX 16C (100-100000725WOF) | $1,649 | **Amazon $1,549.00**; Walmart $1,549.00; B&H $1,549.00; Newegg $1,549.99; MemoryC $2,058.92 (BuildCores, https://www.buildcores.com/products/CPU/873mwfjow/AMD-Ryzen-Threadripper-PRO-9955WX). esaitech $1,625.00, available=True. |
| 9965WX 24C (100-100000724WOF) | $2,899 | Scarce. The only listing was **MemoryC $3,760.37** (BuildCores, https://www.buildcores.com/products/CPU/j9wavxsep/AMD-Ryzen-Threadripper-PRO-9965WX, "Best Price $3,760.37 via MemoryC"; Amazon "N/A"). esaitech $2,781.00, available=False. |
| 9975WX 32C (100-100000723WOF) | $4,099 | **Amazon $4,099.99**; Walmart $4,299.99; MemoryC $5,382.08 (BuildCores, https://www.buildcores.com/products/CPU/zldrztnms/AMD-Ryzen-Threadripper-PRO-9975WX). esaitech $4,089.00, available=False. |

Integrator CPU prices, for context (LIVE). The BIZON X5500 G2 configurator JSON (https://bizon-tech.com/bizon-x5500.html) lists `actual_price`: 9955WX 2015, 9965WX 3432, 9975WX 5070, 9985WX 9295, 9995WX 13910.

##### 1c. EPYC 9005 "P" single-socket parts (SP5, 12-channel DDR5-6400)

**Current AMD 1kU list price** (LIVE, AMD product pages, field "1kU Pricing"):
- 9355P 32C, 280 W: **2598 USD**. https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9355p.html
- 9455P 48C, 300 W: **4366 USD**. https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9455p.html
- 9555P 64C, 360 W: **6130 USD**. https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9555p.html
- 9655P 96C, 400 W: **7958 USD**. https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9655p.html
- Non-P parts for comparison (LIVE, same page pattern): 9355 $3,694; 9555 $7,973; 9375F $4,753; 9175F $3,703; 9135 $1,214; 9115 $726; 9015 $527.

**Launch prices, 10 Oct 2024** (STALE). Wikipedia Template:AMD EPYC 9000 Series, https://en.wikipedia.org/w/index.php?title=Template:AMD_EPYC_9000_Series&action=raw (LIVE): 9355P "US $2,998", 9455P "US $4,819", 9555P "US $7,983", 9655P "US $10,811".

AMD's current 1kU list prices are below launch (ESTIMATE): 9355P -13.3%, 9455P -9.4%, 9555P -23.2%, 9655P -26.4%. I did not find when AMD made the change.

**Street prices** (LIVE 2026-10-30):
- 9355P (100-000001521): SabrePC **$3,408.60, "In Stock", "Ships in 2-3 days"** (https://www.sabrepc.com/100-000001521-AMD-S184203267). esaitech **$2,722.00**, "In stock: No", "SPECIAL ORDER ITEM", "Availability 1-3 Weeks" (https://esaitech.com/products/amd-100-000001521-epyc-9355p-dotriaconta-core-32-core-3-55-ghz-processor). SNIPPET: CDW "$2,807.99" against "$2,998.00" suggested.
- 9555P (100-000001523): SabrePC **$5,427.00, "Out of Stock"** (https://www.sabrepc.com/100-000001523-AMD-S197169404). esaitech **$4,855.00**, special order (https://esaitech.com/products/amd-100-000001523-epyc-9555p-tetrahexaconta-core-64-core-3-20-ghz-processor).
- 9455P: esaitech $3,458.00, available=False. 9655P: esaitech $5,198.00, available=False. esaitech also lists the non-P 9555 at $5,835.00, available=True.

Context: Exxact's site banner reads "AMD EPYC 9006 Series Solutions Coming Soon!" (LIVE, https://www.exxactcorp.com/category/Deep-Learning-NVIDIA-GPU-Workstations), so Turin is still the current SP5 part.

---

#### 2. Motherboards

Unless marked, the source is esaitech `search/suggest.json` (LIVE 2026-10-30). The quote is the product title plus price.

##### TRX50 (sTR5, 4-channel)

The ASUS where-to-buy API confirms 4 channels: "4 x DIMM slots, DDR5, ECC Registered Memory ... 4 Channel Memory Architecture" (https://odinapi.asus.com/recent-data/apiv2/WhereToBuyList?SystemCode=ASUS&WebsiteCode=us&ProductWebPath=pro-ws-trx50-sage-wifi-a&siteID=www&sitelang=, LIVE).

| Board | Street price | Other data |
|---|---|---|
| ASUS Pro WS TRX50-SAGE WIFI **A** | **$960.00, available=True** ("ASUS Pro WS TRX50-SAGE WIFI A AMD TRX50 sTR5 DDR5 Workstation Motherboard \| 960.00") | SNIPPET: SHI $1,118.00; SHI Texas lists MSRP $999.99. |
| ASUS Pro WS TRX50-SAGE WIFI (original) | $899.00, available=True | SNIPPET, STALE (TweakTown, Nov 2023, https://www.tweaktown.com/news/94565/amd-trx50-motherboard-prices-asus-for-899-asrock-799-and-gigabyte-599/): "ASUS's PRO WS TRX50-SAGE WIFI sat at $899, while the ASRock TRX50 WS came in at $799, and the GIGABYTE TRX50 AERO D at $599." |
| ASRock TRX50 WS | $747.00, available=False | Launch $799 (TweakTown snippet). SNIPPET: CDW $1,012.00, "Item Backordered"; AvaDirect $771.48. |
| Gigabyte TRX50 AERO D | $626.00, available=False | Launch $599; SNIPPET: Channel Online MSRP $599.99; Zones $704.99; SHI $697/$738. |
| Gigabyte TRX50 AI TOP | $953.00, available=False | SNIPPET: BuildCores $968.00. |
| Supermicro H13SRA-TF (TRX50) | $690.15, available=False | |

##### WRX90 (sTR5 TR PRO, 8-channel)

The ASUS API for pro-ws-wrx90e-sage-se gives "8 x DIMM slots, DDR5, ECC Registered Memory ... 8 Channel Memory Architecture" (LIVE).

| Board | Street price | Other data |
|---|---|---|
| ASUS Pro WS WRX90E-SAGE SE | **$1,248.00, available=True** | SNIPPET: SHI $1,472.00 and $1,257.35, both with "MSRP $1,299.99". |
| ASRock WRX90 WS EVO | $1,114.00, available=False | SNIPPET: an esaitech listing at $1,099.99; SHI public sector $1,326.00. |

##### SP5 (EPYC 9004/9005, 12-channel)

| Board | Street price | Other data |
|---|---|---|
| Supermicro **H14SSL-NT-O** (2x10GbE) | **$837.00, available=True** ("Supermicro MBD-H14SSL-NT-O AMD EPYC 9005/9004 SP5 DDR5-6400 ATX Motherboard \| 837.00") | |
| Supermicro H14SSL-N (1GbE) | US price not found | SNIPPET: eBay.de business seller US $935; Future-X (DE) €760.49 incl. VAT. |
| Supermicro H13SSL-N-O | $638.79, available=False | H13SSL-N-B $603.48, available=False. STALE (Phoronix, 14 Nov 2024, https://www.phoronix.com/review/supermicro-h13ssln-epyc-turin/2, LIVE): "available from a number of Internet retailers for $669~690 USD or as high as $989 at Amazon ... I ended up buying the Supermicro H13SSL-N from Wiredzone for $632 USD." |
| Supermicro H13SSL-NT-O | $792.00, available=False | |
| ASRock Rack TURIND8-2L2T (CEB) | SNIPPET only: Newegg $729 (was $819), "Final Sale: Non-Refundable" | SNIPPET: SHI $984.00. |
| ASRock Rack TURIND8UD-2T/X550 (deep mATX) | USD price not found | SNIPPET: Scan UK £839.99. |
| ASRock Rack GENOAD8X-2T | not found | |
| esaitech "ASRock Rack TURIND8X-2T/500W AMD EPYC 9005/9004 SP5 DDR5-6400 Motherboard" | $1,069.00, available=False | Listing name as shown; the exact SKU is unclear. |

---

#### 3. PSUs for 1 or 2 x 600 W GPUs

**Electrical constraint** (sourced quotes, with my ESTIMATE of what follows): 2 x 600 W GPUs plus a 350 W Threadripper is about 1.55 kW before the platform. That is the reason for using either 1,500-1,600 W units on 115 V or 2,200 W+ units, which need 200-240 V circuits. Quotes:
- Seasonic PX-2200: "AC Input Range: 200 - 240 Vac only".
- Corsair WS3000: "Requires 220-240V AC high-line power".
- Puget's quad-GPU tower: "240V power supply (requires 200-240V circuit)".

| PSU | Price and source (LIVE 2026-10-30 unless marked) | Notes |
|---|---|---|
| Corsair **HX1500i (2025)** CP-9020309-NA, ATX 3.1 | **$389.99, available** (retail.corsair.com product JSON; Shopify `published_at` 2026-09-08) https://retail.corsair.com/products/hx1500i-fully-modular-ultra-low-noise-platinum-atx-1500-watt-pc-power-supply-cp-9020309-na | |
| Corsair HX1500i (previous) CP-9020261-NA, ATX 3.1, 100-240 V | **Amazon $319.99** (MaxMyBuild, https://www.maxmybuild.com/power-supplies/corsair-hx1500i, "Amazon \| In stock \| $319.99"); MSRP $399.99 per the same page. Corsair store $444.99, unavailable. | |
| Corsair AX1600i CP-9020087-NA | **Discontinued**. Corsair US page stock status "Discontinued"; Corsair retail store price 0.00, unavailable. | Not ATX 3.1. |
| Corsair WS3000 (3000 W, ATX 3.1, 4 x 12V-2x6) | $629.99, available (retail.corsair.com) | "Requires 220-240V AC high-line power". |
| Seasonic PRIME **PX-1600** (ATX 3.1, 100-240 V) | **B&H $505.99** (MaxMyBuild, /power-supplies/seasonic-prime-px-1600) | |
| Seasonic PRIME **TX-1600** (ATX 3.1, 100-240 V) | **Amazon $559.99** (MaxMyBuild, /power-supplies/seasonic-prime-tx-1600) | |
| Seasonic PRIME **PX-2200** (ATX 3.1) | Seasonic press release (https://seasonic.com/news/sea-sonic-to-launch-the-new-prime-px-2200/, published 2024-09-23, modified 2026-03-26): "MSRP PRIME PX-2200 \| N/A (USA) \| 579.90€ (Europe) \| $499.99 (ROW)" and "AC Input Range: 200 - 240 Vac only". US marketplace: Newegg $714.51, Amazon $748.90 (MaxMyBuild, /power-supplies/seasonic-prime-2200w). | Not sold in North America and not usable on 120 V. |
| MSI MPG 1600W (ATX 3.1, 100-240 V) | **Amazon $499.99** (MaxMyBuild, /power-supplies/msi-mpg-1600w) | |
| ASUS Pro WS 1600W Platinum (ATX 3.1) | Newegg $587.88 (MaxMyBuild) | |
| ASUS Pro WS 2200W Platinum (ATX 3.1) | B&H $569.99; Newegg $572.99 (MaxMyBuild) | Listings disagree on AC input; one says 200-240 V (SNIPPET). |
| Super Flower Leadex **Titanium 2200W** SF-2200F14HP (ATX 3.1) | Amazon $549.99; Newegg $549.99 (MaxMyBuild) | SNIPPET: retailer "MUST connect to 240V outlet"; Newegg "200-240Vac". |
| Super Flower Leadex Platinum 2000W (SF-2000F14HP) | Current US price not found. Older ATX 2.x unit; SNIPPET, STALE: launch about €369.90 / £349.99. | Superseded in practice by the Titanium 2200W above. |
| be quiet! Dark Power Pro 13 **1600W** | Current US price **not found**. SNIPPET, STALE (May 2023, tech-critter): "Dark Power Pro 13 (1600W) - USD$459.90". | DPP13 1300W: Amazon $379.90 (MaxMyBuild). |
| NZXT C1500 Platinum (ATX 3.1) | $329.99 at Amazon and Newegg (MaxMyBuild) | Budget option for 1 GPU. |
| SilverStone PS-ST1500-TI | Newegg $440.99; Amazon $481.70 (MaxMyBuild) | |
| ASRock PG-1600G (ATX 3.1, 80+ Gold) | Amazon $199.99 (MaxMyBuild) | Cheapest 1600 W option seen. |

Integrator PSU option prices (BIZON X5500 G2 JSON, LIVE): "2 GPU-Ready for 2x RTX 5090/40xx or 2x RTX 6000 Ada/Blackwell (2200W power supply)" $793.22; "4 GPU-Ready ... (advanced case, 3000W power supply)" $1,413.

---

#### 4. Chassis for 2 large GPUs

| Case | Price | Notes |
|---|---|---|
| Phanteks Enthoo Pro 2 Server Edition | **Amazon $179.99**; Newegg $179.99 (+$9.98 s/h); Walmart $257.14 (BuildCores, LIVE, https://www.buildcores.com/products/PCCase/bdv1wc9rj/Phanteks-Enthoo-Pro-2-Server-Edition-ATX-Full-Tower-Black) | Launch MSRP (STALE, July 2023, SNIPPET via Guru3D): TG "$169.99", closed "$159.99". SNIPPET: V2 at $199.99. |
| Fractal Design Define 7 XL (Dark TG) | **Newegg $254.99**; B&H $254.99; Walmart $367.79 (BuildCores, LIVE, https://www.buildcores.com/products/PCCase/mfjs8wut8/Fractal-Design-Define-7-XL-ATX-Full-Tower-Dark-Tinted-Tempered-Glass) | |
| Fractal Design Meshify 2 XL | Current US price **not confirmed**. SNIPPET: SHI $215.52; STALE launch (2020, bit-tech snippet) $179.99 for the TG versions. | |
| Lian Li V3000 Plus | Current price **not verified**. SNIPPETs disagree: Micro Center $349.99 (white) and $399.99 (black); launch $499.99 (Vortez snippet, 2022). | |

Typical price (ESTIMATE): $180-$255 for a full tower that fits two dual-slot GPUs and an EEB board.

---

#### 5. Consumer NVMe SSDs, 4 TB and 8 TB

The main source is MaxMyBuild US pages (LIVE 2026-10-30; "Prices update daily", offers "Checked daily").

| Drive | Lowest US offer now | Other offers |
|---|---|---|
| Samsung 9100 PRO **4TB** (MZ-VAP4T0B/AM) | **Amazon $987.00** ("Samsung 9100 PRO 4TB costs $987.00 right now") | Newegg $1,020.00; B&H $1,359.99; heatsink version $1,029.99 (Newegg). "Lowest in the last 30 days: $749.99" (Oct 7). Samsung.com list price **$1,359.99** (JSON-LD `"price":"1359.99"`, https://www.samsung.com/us/business/memory-storage/nvme-ssd/9100-pro-nvme-ssd-sku-mz-vap4t0b-am/). https://www.maxmybuild.com/storage/nvme-ssds/samsung-9100-pro/4tb |
| Samsung 9100 PRO **8TB** | **Newegg $1,949.99** (heatsink, MZ-VAP8T0CW) | Newegg $2,099.99; Amazon $2,340.60; B&H $2,769.99. Samsung.com "$2,719.99 Out of stock". https://www.maxmybuild.com/storage/nvme-ssds/samsung-9100-pro/8tb |
| WD_BLACK SN8100 **4TB** | **Newegg $768.00** | Amazon $859.99; B&H and Adorama $1,079.99 (listed under part SDSP82400TAN-000E0). https://www.maxmybuild.com/storage/nvme-ssds/wd-black-sn8100/4tb |
| WD_BLACK SN8100 **8TB** | **$2,149.99** at Amazon, Newegg and Adorama | "Lowest point $2,149.99 on Sep 19". https://www.maxmybuild.com/storage/nvme-ssds/wd-black-sn8100/8tb |
| Crucial T705 **4TB** | **Amazon $629.99** (heatsink) / $633.77 | Newegg $634.00. https://www.maxmybuild.com/storage/nvme-ssds/crucial-t705/4tb |
| Crucial T710 **4TB** | **Newegg $789.95** (heatsink) / $795.00 | Amazon $819.00; "Lowest in 60 days: $700.14". https://www.maxmybuild.com/storage/nvme-ssds/crucial-t710/4tb |
| Samsung 990 PRO 4TB (Gen4, reference) | Newegg $786.00 | |
| Crucial T705/T710 8TB | not found | |

##### How much SSD prices rose in 2026

All percentage calculations below are ESTIMATES. The inputs are sourced.

- **Samsung 9100 PRO 4TB.** Launch MSRP $549.99 (Samsung Newsroom, https://news.samsung.com/us/samsung-announces-9100-pro-series-ssds-with-breakthrough-pcie-5-0-performance/, "(MSRP: $549.99)"). 2025 lows were $385 (TechRadar, 9 Jul 2025, title "...shock 30% discount brings it to $385") and $349 (Notebookcheck, 8 Oct 2025: "can now be ordered for $349 instead of $549", https://www.notebookcheck.net/Samsung-9100-Pro-SSD-with-8TB-and-14-800MB-s-drops-to-lowest-price-ever-on-Amazon.1133591.0.html). Changes to now:
  - $987 street is **+79% over MSRP** and **+183% over the Oct 2025 low**.
  - Samsung's own list price ($1,359.99) is **+147% over the launch MSRP**.
- **Samsung 9100 PRO 8TB.** $749 in Oct 2025 (same Notebookcheck article: "the maxed-out 8TB Samsung 9100 Pro has dropped to $749"). Now $1,949.99, which is **+160%**. Samsung list $2,719.99 against the $999.99 pre-discount price is +172%. The $999.99 figure comes from a SNIPPET of the Tom's Hardware deal history.
- **WD SN8100.** 8TB launch $999.99 (SNIPPET, Android Headlines, Oct 2025). Now $2,149.99, **+115%**. 4TB launch MSRP $549.99 (SNIPPET citing Tom's Hardware, 13 May 2025). Now $768, +40%.
- **Market data.** Notebookcheck, 25 Oct 2026 (LIVE, https://www.notebookcheck.net/SSD-prices-explode-by-303-in-a-year-as-AI-fuels-NAND-flash-shortage.1433261.0.html):
  > "The contract price of a 256GB TLC SSD reached approximately $134.20 in the third quarter of 2026, up from $33.30 a year earlier. That represents a 303 % increase year over year"

  > "A 1TB Gen4 NVMe SSD reportedly cost an average of about $144 in mid-October, while a Samsung 990 Evo Plus 1TB drive was listed at $237, compared with a previous low of around $59."

  > "TrendForce forecasts that NAND flash contract prices will increase by another 15 % to 20 % quarter over quarter in the fourth quarter of 2026."
- **MaxMyBuild NVMe index** (LIVE, https://www.maxmybuild.com/storage/prices, through Oct 28, 2026): "NVMe SSD $0.190/GB up 5.1% over the past 3 months".
- **SNIPPET** (digitalcitizen.life, 403, date unclear): "The Crucial T710 4TB is currently $769, while its lowest recorded price was $379 ... The Samsung 990 Pro 4TB is currently listed at $994, compared with a previous low of $249."

Integrator SSD prices (LIVE). These show what system builders charge:
- **Puget** (buy-570 SecondHardDrive deltas from the "None [subtract $646.35]" baseline): 2TB Gen4 $646.35; 4TB Gen4 $1,089.30; 4TB Gen5 $1,333.87; 8TB Gen5 $2,629.46.
- **BIZON:** "4 TB PCI-E 4.0 NVMe SSD" $1,245.29; "4 TB PCI-E 5.0 NVMe SSD" $1,875.

---

#### 6. CPU coolers (needed for the estimate)

- **Noctua NH-U14S TR5-SP6** (sTR5). SNIPPET, STALE: launch "EUR 129.90 / USD 129.90" (Guru3D, 2023); an eBay listing at US $169.99. No current US retailer price was confirmed.
- **Arctic Freezer 4U-SP5** (SP5). SNIPPET, STALE: Phoronix, 12 Feb 2025: "listed for only $55 USD on Amazon.com ... The list price on this heatsink is ~$135"; Central Computers $49.99 (date unclear).

---

#### 7. Vendor-built systems with RTX PRO 6000

Context: integrator prices per RTX PRO 6000 (LIVE). These show how much of each system price is GPU:
- **Puget:** "None [subtract $15184.16]", so **$15,184.16 per Max-Q**.
- **System76:** the 1st, 2nd and 3rd GPU add **$18,339, $18,640 and $18,646**. The first increment is measured against the base configuration with its A400 card, so it is net of the A400.
- **BIZON:** `actual_price` **$19,321.50** for both the 600 W and the Max-Q card.

##### Puget Systems (LIVE 2026-10-30)

https://www.pugetsystems.com/solutions/ai-and-hpc-workstations/machine-learning-ai/ and /solutions/ai/deploy/, /solutions/ai/enterprise-scale/

**Multi GPU Workstation** (configurator buy-570):
- CPU "AMD Threadripper PRO 9975WX".
- GPUs "2 x NVIDIA RTX PRO 6000 Blackwell Max-Q" (configurator: VideoCard 1 + Accelerators 1).
- RAM "8x 32GB DDR5 RDIMM (256GB total)".
- Storage 2 x "2TB NVMe PCIe Gen4 M.2 SSD".
- Ubuntu 26.04; "Lifetime Labor and Tech Support, 3 Year Parts Warranty".
- **"Price as Configured" $52,412.24**; "Starting At" $13,140.19.
- Non-GPU part (ESTIMATE): 52,412.24 - 2 x 15,184.16 = **$22,043.92**. This includes the 256 GB RDIMM, labor and warranty.

**Quad GPU Rackmount** (buy-571):
- TR PRO 9975WX.
- As configured, 2 x RTX PRO 6000 Max-Q (VideoCard 1 + Accelerators 1). The chassis takes "4x RTX PRO 5000 Blackwell or 6000 Max-Q GPUs".
- "8x 64GB DDR5 RDIMM (512GB total)"; 2 x 4TB Gen4 NVMe.
- "5U rackmount / tower convertible chassis", "240V power supply (requires 200-240V circuit)".
- **$63,861.73**; starting at $32,736.46.

**4 GPU LLM Server** (buy-449):
- "AMD EPYC 9375F".
- **4 x "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition 96GB"** (quantity select "4x" SELECTED).
- "12x 64GB DDR5 RDIMM (768GB total)"; 1.92TB U.2.
- 2U.
- **$106,514.40**; starting at $23,986.92.
- Non-GPU part (ESTIMATE): 106,514.40 - 4 x 15,184.16 = $45,777.76.

**8 GPU LLM Server**, for reference:
- Summary card: "2x AMD EPYC 9354", "8x NVIDIA RTX PRO Blackwell Server 96GB", "24x 64GB DDR5 RDIMM (1.5TB total)", **$219,404.75**.
- The configurator page shows EPYC 9375F as the selected CPU, so the CPU line is inconsistent between the two pages.

##### System76 Thelio Mega (LIVE, BigCommerce price API, 2026-10-30)

https://system76.com/desktops/thelio-mega

Base configuration:
- "5.4 GHz Threadripper PRO 9955WX (16 Cores - 32 Threads)".
- "64 GB ECC DDR5 5600MHz (2x32)".
- "1 TB PCIe5 M.2 SSD".
- Pop!_OS.
- "1 Year Limited Parts and Labor Warranty".

API `price.without_tax` by GPU option:
- "4 GB NVIDIA A400": **$8,999.00**.
- "96 GB NVIDIA RTX PRO 6000 (non-refundable)": **$27,338.00**.
- "96 GB NVIDIA RTX PRO 6000 Max-Q": **$27,338.00**.
- "192 GB Dual NVIDIA RTX PRO 6000 Max-Q": **$45,978.00**.
- "288 GB Triple NVIDIA RTX PRO 6000 Max-Q": **$64,624.00**.

All were reported `purchasable: True` and `instock: True`.

##### BIZON X5500 G2 (LIVE, https://bizon-tech.com/bizon-x5500.html)

- "Starting at $9,076". Lead time "2–3 days", "Ship date: Nov 1 – Nov 2, 2026".
- "Up to 2× NVIDIA RTX 5090 or 4x RTX PRO 6000 Blackwell GPUs, AMD Threadripper PRO 9000WX up to 96 cores".
- A fully configured total is not in the static page. Option prices from the configurator JSON:
  - RTX PRO 6000 (600 W or Max-Q): $19,321.50 each.
  - 9975WX: $5,070.
  - "32 GB DDR5 ECC/REG": $1,768.50; "64 GB": $3,024; "128 GB": $6,331.50. Whether these are per module is not stated.
  - 2-GPU-ready 2,200 W PSU: $793.22.
  - 4 TB Gen5 SSD: $1,875.
- ESTIMATE, rough lower bound for 2 x RTX PRO 6000: base $9,076 + 2 x $19,321.50 = **about $47.7K**, before CPU, RAM and SSD upgrades. The GPU included in the base configuration is unknown, so this is not a quote.

##### Exxact (LIVE)

These are starting prices only. The configuration behind each starting price is not shown.
- Valence VWS-135223847, "1x AMD Ryzen Threadripper Pro 9000/7000 WX-Series", "Up to 4x Double-Wide cards": **"Starting Price: $15,616.70"**. https://www.exxactcorp.com/Exxact-VWS-135223847-E135223847
- TensorEX TWS-198830577, "1x AMD EPYC 9005/9004-Series", 4U, "Up to 2x PCI-E 5.0 x16 Double-Wide cards": **"Starting Price: $16,354.80"**. https://www.exxactcorp.com/Exxact-TWS-198830577-E198830577
- Both pages list RTX PRO 6000 Max-Q, Server and Workstation options.

##### Dell Pro Max Tower T2

TechRadar, published 2026-10-20, updated 2026-10-28 (LIVE HTML), https://www.techradar.com/pro/dells-pro-max-tower-t2-workstation-costs-less-than-the-nvidia-blackwell-gpu-inside-it:
> "Dell Pro Max Tower T2 workstation with Blackwell GPU for $15,149 at Dell"

> "This is the cheapest one with the Nvidia RTX Pro Blackwell 6000 GPU, running Windows 11 Pro on an Intel Core Ultra 5 235 CPU, 8GB DDR5, and 256GB SSD."

The RTX PRO 6000 edition is not stated. I could not verify this on dell.com (HTTP 403).

##### OEM workstations through reseller monitors.com (LIVE, Shopify suggest API, 2026-10-30; reseller prices, not OEM list)

All entries have one "RTX Pro 6000 Blackwell 96GB" (edition not stated) and a 512GB NVMe SSD unless noted. All were `available: True`.

- **HP Z6 G5 A**: TR PRO 9955WX, 128GB ECC DDR5: **$26,652.05**.
- HP Z6 G5 A: TR PRO 9965WX, 64GB: $25,235.43.
- HP Z6 G5 A: TR PRO 9995WX, 64GB: $36,234.09.
- **HP Z8 Fury G5**: Xeon W5-3433, 64GB: **$23,429.89**.
- HP Z8 Fury G5: Xeon w7-3555, 128GB: $27,582.10.
- **Dell Precision 7960**: Xeon W5-3423, 128GB: **$27,923.88**.
- **Dell Pro Max Tower T2**: Core Ultra 9 285, 64GB: **$20,937.93**.
- **Lenovo ThinkStation P5**: Xeon W5-2565X, 64GB: $24,348.91.
- Lenovo ThinkStation P3 Gen 2: Core Ultra 5 235, 32GB: $20,058.94.
- **ASUS ExpertCenter Pro ET900A X9**, 2 GPUs: TR PRO 9955WX, 256GB ECC DDR5, "2TB Samsung 9100 Pro Gen5 NVMe", "Dual 10GbE LAN", "2000W Palatinum PSU" (sic), "Dual (x2) NVIDIA RTX Pro 6000 Blackwell 96GB": **$50,675.89**.

Lenovo **ThinkStation PX** with RTX PRO 6000: **not found** on monitors.com. SNIPPET: monitors.com PX listings at about $16,969-$22,219, several "sold out".

##### 4-GPU servers

**Supermicro SYS-422GA-NRT-01-G2** ("4U GPU AI Gold Series") through **AVADirect** (WebFetch, 2026-10-30), https://www.avadirect.com/Supermicro-GPU-SuperServer-SYS-422GA-NRT-01-G2-4U-Rackmount-Gold-Series-version-with-pre-configured-components-server/Configure/19917291:
- **"Configured price $108039"**.
- 4 x RTX PRO 6000 Blackwell **Server Edition**.
- 2 x Xeon 6960P (72C).
- 1TB DDR5-6400.
- 2 x 3.84TB E3.S plus 960GB M.2.
- 4 x 3200 W Titanium PSUs.
- "AVA Basic (2-Year Labor / 1-Year Parts)".
- The page warns that the configuration "is missing an essential component".
- An older SNIPPET showed $84,639.
- The Supermicro eStore page (https://store.supermicro.com/us_en/4u-gpu-ai-gold-series-gpu-server-sys-422ga-nrt-01-g2.html, WebFetch) lists the same configuration but showed no price.

**Gigabyte 4-GPU servers**: no US price found. SNIPPET, EU reseller (probably servermall.com, unverified): G294-S42-AAP1 (2 x Xeon 6756E, 384GB) about €100,379 plus VAT.

**Dell PowerEdge with RTX PRO 6000**: no US configured price found (dell.com returned 403). SNIPPET: R7725 regional storefront prices without a GPU breakdown.

**Lambda**: no longer sells hardware (LIVE, https://lambda.ai/legacy-hardware):
> "Lambda has ended its on-premise hardware business (Vector, Vector One, and Vector Pro workstations and Scalar and Hyperplane servers) as of August 29, 2025."

---

#### 8. ESTIMATE: non-GPU, non-RAM component cost

Scope: CPU + motherboard + PSU + case + one 4 TB Gen5 SSD + CPU cooler. GPUs, DIMMs, OS, assembly, warranty and extra fans are excluded. "Low" uses the cheapest verified price, even if out of stock. "Typical" uses mainstream in-stock or near-MSRP picks. Prices are from sections 1-6.

**TRX50, 1 GPU**
- Low: 9960X 1,395.00 + AERO D 626.00 + HX1500i (prev.) 319.99 + Enthoo Pro 2 Server 179.99 + T705 4TB 629.99 + NH-U14S TR5-SP6 129.90 = **$3,280.87**.
- Typical: 9970X 2,496.00 + TRX50-SAGE WIFI A 960.00 + HX1500i (2025) 389.99 + Define 7 XL 254.99 + SN8100 4TB 768.00 + cooler 169.99 = **$5,038.97**.

**TRX50, 2 GPUs** (1,600 W PSU on 115 V)
- Low: 1,395.00 + 626.00 + MSI MPG 1600W 499.99 + 179.99 + 629.99 + 129.90 = **$3,460.87**.
- Typical: 2,496.00 + 960.00 + Seasonic TX-1600 559.99 + 254.99 + 768.00 + 169.99 = **$5,208.97**.
- For a 240 V circuit, a 2,200 W unit costs about the same: Super Flower Leadex Titanium 2200W $549.99; ASUS Pro WS 2200W $569.99.

**WRX90, 2 GPUs**
- Low: 9955WX 1,549.00 + ASRock WRX90 WS EVO 1,114.00 + 499.99 + 179.99 + 629.99 + 129.90 = **$4,102.87**.
- Typical: 9975WX 4,099.99 + ASUS WRX90E-SAGE SE 1,248.00 + 559.99 + 254.99 + 768.00 + 169.99 = **$7,100.96**.

**EPYC SP5, 2 GPUs**
- Low: 9355P (esaitech special order) 2,722.00 + H13SSL-N-O 638.79 + 499.99 + 179.99 + 629.99 + Arctic 4U-SP5 49.99 = **$4,720.75**.
- In stock: 9355P (SabrePC) 3,408.60 + H14SSL-NT-O 837.00 + 559.99 + 254.99 + 768.00 + 55.00 = **$5,883.58**.
- 64-core: 9555P 5,427.00 + 837.00 + 559.99 + 254.99 + 768.00 + 55.00 = **$7,901.98**.

**Storage add-on**: going to 8 TB adds about $1,320 (9100 PRO 8TB $1,949.99 - T705 4TB $629.99) or $1,382 (SN8100 8TB $2,149.99 - SN8100 4TB $768).

**Summary range**:
- TRX50 1-GPU: about $3.3-5.0K.
- TRX50 2-GPU: about $3.5-5.2K.
- WRX90 2-GPU: about $4.1-7.1K.
- EPYC SP5 2-GPU: about $4.7-7.9K.

The 2-GPU premium over 1 GPU in the CPU/board/PSU/case bucket is only about $170-180, the PSU difference ($499.99 - $319.99; $559.99 - $389.99). The real cost of a second GPU is the card itself.

**Sanity checks against integrators** (ESTIMATE, each figure includes RAM and service):
- System76's $8,999 base (9955WX, 64 GB RAM, 1 TB, A400 GPU, 1-year warranty) is consistent with about $4K of DIY non-GPU, non-RAM parts plus RAM, assembly and margin.
- Puget's 2-GPU TR PRO 9975WX machine implies $22,044 non-GPU. That includes 256 GB RDIMM, 2 x 2 TB SSDs, assembly, a 3-year parts warranty and lifetime support.

**What the estimate leaves out (RAM is covered elsewhere)**: the platforms differ in memory channels. TRX50 has 4, WRX90 has 8 and SP5 has 12. A WRX90 or SP5 build needs more DIMMs to use its bandwidth, so its total RAM spend will be higher.

---

#### 9. Not found or not confirmed

- Threadripper **9970X** current in-stock street price. The only data points are out-of-stock distributors ($2,496 and $2,669.87) and an Amazon $2,000 deal on 3 Jul 2026.
- Threadripper PRO **9965WX** at a major retailer. Only MemoryC $3,760.37 was found; esaitech $2,781 is out of stock.
- In-stock US prices for **ASRock TRX50 WS**, **Gigabyte TRX50 AERO D** and **ASRock WRX90 WS EVO**. The esaitech prices are for out-of-stock items; other figures are snippets.
- Supermicro **H14SSL-N** (non-NT) US price; ASRock Rack **GENOAD8X-2T** and **TURIND8UD-2T** USD prices. TURIND8-2L2T is a snippet only.
- be quiet! **Dark Power Pro 13 1600W** current US price. **Corsair AX1600i** is discontinued. **Seasonic PX-2200** is not sold in the US (MSRP "N/A (USA)", 200-240 V only). **Super Flower Leadex Platinum 2000W** current price not found.
- **Fractal Meshify 2 XL** and **Lian Li V3000 Plus** current US prices (snippets only, and they conflict).
- Current US prices for the **Noctua NH-U14S TR5-SP6** and **Arctic 4U-SP5** coolers (only 2023-2025 data).
- WD **SN8100 4TB** launch MSRP and **Crucial T705/T710 8TB** prices. The 2026 rise for T705/T710 4TB is only from snippets.
- Systems:
  - **Lenovo ThinkStation PX** with RTX PRO 6000: no current price.
  - **Dell PowerEdge** with RTX PRO 6000: no US price.
  - **Gigabyte 4-GPU server**: EU snippet only.
  - **Exxact** and **BIZON**: no full configured totals.
  - **HP and Lenovo**: only reseller prices, not OEM direct.
  - **Dell T2 $15,149**: from TechRadar, not verified on dell.com.
  - **Lambda**: exited hardware on 29 Aug 2025.
- GPU edition in the monitors.com and Dell T2 listings (Workstation or Max-Q) is not stated.

---

## Appendix B: helper-agent notes for items 8 and 9 (enterprise SSD, colocation, electricity), 2026-10-30

Verbatim notes from the helper agent; "I" refers to that agent.

### Items 8-9: enterprise NVMe SSD $/TB, US colocation $/kW-month, US electricity $/kWh

Research date: 2026-10-30 (retrievals 2026-10-29/30 UTC). Prices are US$, pre-tax.

#### Conventions and confidence

- **$/TB** is my own arithmetic: list price divided by the nominal decimal capacity (7.68, 15.36, 30.72, 61.44, 122.88 TB).
- **How each source was retrieved:**
  - `curl`: raw page or JSON. Quotes are exact.
  - `WebFetch`: the page was read by an extraction model. Quotes are near-verbatim but not byte-checked.
  - `snippet`: only a search-engine snippet was visible. These are unverified, often undated, and may be stale.
- **Inferences:** anything I inferred is labelled **ESTIMATE** or **INFERENCE**.
- **Stale data:** anything dated before 2026-08 is marked **STALE** (pre-2026 = strongly stale, because of the 2026 NAND price surge).
- **Blocked sites (HTTP 403 or bot wall, so not usable):** CDW, Connection, Insight, SHI, Provantage, ShopBLT, CompSource, Tech-America, ServerSupply, Central Computer, Mouser, DCD (datacenterdynamics.com) and BusinessWire. Shopify stores (esaitech, LTT Partners, Avendor) began bot-walling curl after a few requests, so later checks of them used WebFetch.

---

#### TASK A: enterprise NVMe SSD price per TB, late 2026

##### A1. Market context: TrendForce enterprise SSD contract prices (quarter on quarter)

| Quarter | Enterprise SSD contract price change | Source (date) | Quote |
|---|---|---|---|
| 4Q25 (STALE, baseline) | ~+25% average; >20%, ~40% on some small capacities | TrendForce report "Enterprise SSD Contract Price 4Q25", last modified 2025-10-28, https://www.trendforce.com/research/download/RP251029UJ (WebFetch) | "Suppliers are aggressively raising 4Q25 contract prices over twenty percent" |
| 1Q26, forecast | "Over 50%" | TrendForce report "Enterprise SSD Contract Price 1Q26", last modified 2026-01-27, https://www.trendforce.com/research/download/RP260128FF (WebFetch) | "Enterprise SSD to Rise by Over 50% in 1Q26 as Surge of AI Agent Applications Triggered Shortages" |
| 1Q26, forecast | +53-58% | TrendForce press release, 2026-02-02, https://www.trendforce.com/presscenter/news/20260202-12911.html (WebFetch) | "...enterprise SSD prices are expected to rise by 53–58% QoQ in 1Q26, marking a new record for quarterly price increases." |
| 1Q26, revised | ASP increase "Above 70%" | TrendForce report "(Revised) Enterprise SSD Contract Price 1Q26", last modified 2026-02-12, https://www.trendforce.com/research/download/RP260212NQ (WebFetch) | "Enterprise SSD Experienced another ASP Hike to Above 70% in 1Q26" |
| 2Q26 | +48-53% | TrendForce report "Enterprise SSD Contract Price 2Q26", last modified 2026-04-24, https://www.trendforce.com/research/download/RP260427NK (WebFetch) | "Contract Prices of Enterprise SSD Continue to Surge by 48-53% in 2Q26" |
| 3Q26 | +20-25% | TrendForce report "Enterprise SSD Contract Price 3Q26", last modified 2026-07-29, https://www.trendforce.com/research/download/RP260728RU (WebFetch) | "Contract Price Hikes on Enterprise SSD Subsided to 20-25% in 3Q26" |
| 4Q26, forecast | +23-28% (all NAND +15-20%) | TrendForce report "4Q26 Memory Price Forecast", last modified 2026-09-24, https://www.trendforce.com/research/download/RP260924PL (WebFetch) | "4Q26 Contract Prices for Enterprise SSD Surge 23-28% QoQ Against Trend"; "Hyperscalers Raise QLC Enterprise SSD Orders to Accommodate KV Cache"; "Overall NAND Flash Up 15-20% QoQ" |
| 4Q26, forecast | Enterprise SSD is the only category accelerating | TrendForce press release, 2026-09-30, https://www.trendforce.com/presscenter/news/20260930-13258.html (WebFetch, plus the table image read directly) | "Enterprise SSD price growth is therefore expected to accelerate in 4Q26". The table image "DRAM and NAND Flash Contract Price Projections, 3Q26-4Q26" (Source: TrendForce, Sept. 2026) reads "Total NAND Flash: 3Q26E up 18~23%; 4Q26F up 15~20%". |

**Compounding the TrendForce steps (ESTIMATE, my arithmetic using range mid-points and 70% for 1Q26):**
- 3Q25 to 3Q26: about 3.9x (1.25 × 1.70 × 1.505 × 1.225).
- 4Q25 to 4Q26F: about 3.9x.
- 3Q25 to 4Q26F: about 4.9x.

**Other context:**
- **Demand (TrendForce release, 2026-09-21, https://www.trendforce.com/presscenter/news/20260921-13246.html, WebFetch):**
  - "U.S. CSPs have recently upgraded their enterprise SSD demand forecasts over the past two weeks"
  - "total enterprise SSD orders in the fourth quarter could surpass the already elevated levels seen in 3Q26"
  - QLC is called "a significant growth catalyst"
  - No % or $/GB figures in this release.
- **Revenue (TrendForce release, 2026-09-01, https://www.trendforce.com/presscenter/news/20260901-13210.html, WebFetch):** top-5 enterprise SSD revenue "double quarter-over-quarter, reaching $37.59 billion in 2Q26", which it calls "a staggering 103.6% increase".

**Reported per-drive / $-per-TB figures: the VDURA Flash Volatility Index.**
- VDURA sells hybrid flash+HDD systems, so it has a commercial interest in showing high flash prices. The index does not say whether its prices are street, contract or list.

| Quarter | 30TB TLC | 30TB QLC | $/TB TLC / QLC (ESTIMATE, ÷30.72) | Source |
|---|---|---|---|---|
| Q2 2025 (STALE) | $3,062 | $2,450 | $100 / $80 | Blocks & Files, 2026-04-08, https://www.blocksandfiles.com/flash/2026/04/08/vdura-says-30-tb-qlc-ssd-capacity-now-costs-226x-more-than-hdd/5214761 (WebFetch): "Pricing for 30 TB TLC enterprise SSDs increased by 472 percent between Q2 2025 and Q1 2026, rising from $3,062 to $17,500." / "Over the same period, 30 TB QLC SSD pricing increased from $2,450 to $15,121." |
| Q3 2025 (STALE) | $3,460 | $2,768 | $113 / $90 | StorageReview (Harold Fritts), 2026-08-18, https://www.storagereview.com/news/enterprise-ssd-prices-run-at-6-5x-last-year-vdura-pegs-a-30tb-tlc-drive-at-22600 (WebFetch) |
| Q1 2026 | $17,500 | $15,121 | $570 / $492 | Blocks & Files, 2026-04-08 (above) |
| Q3 2026 (index update 2026-08-11) | $22,600 | $18,080 | **$736 / $589** (if the drive is exactly 30.0 TB: $753 / $603) | StorageReview, 2026-08-18: "places the price of a 30TB TLC enterprise SSD at $22,600, compared with $3,460 in Q3 2025." / "A 30TB QLC SSD now costs $18,080, up from $2,768 during the same period." Blocks & Files (Chris Mellor), 2026-08-11, https://www.blocksandfiles.com/flash/2026/08/11/ssd-prices-still-rocketing-up-faster-than-disk/5286189 (WebFetch) has the same figures. |

- **Contract $/GB or $/TB from TrendForce:** not found. TrendForce's absolute contract price levels are subscriber-only.
- **Contract vs retail (INFERENCE):** VDURA shows about 6.5x year on year, against TrendForce's compounded contract increases of about 3.9x for 3Q25 to 3Q26. Street and channel prices therefore appear to have risen faster than hyperscaler contract prices.

##### A2. Listings: new drives, US retailers, late October 2026

###### A2.1 SabrePC: in-stock new drives (strongest evidence)

- **Source:** SabrePC's public product API, the same data that renders each product page. Retrieved via curl on 2026-10-30 at 03:32 UTC.
- **Query used:** `https://www.sabrepc.com/api/products/find?filters={"sites.spc.displayInStore":true,"mpn":"<MPN>"}&limit=1`
- **Fields:** every row is `"condition":"New"` with `"inventory"` > 0. The "Record date" column is SabrePC's `updatedAt` record timestamp. A row marked "WebFetch ✓" means the product page itself was also checked and showed the price and "In Stock".

| Model (MPN) | Cap. | NAND | Form factor | Price | $/TB | Inventory | Record date | URL | Quote |
|---|---|---|---|---|---|---|---|---|---|
| Kioxia CD8P-R (KCD8XPJE15T3) | 15.36 TB | TLC | E3.S, PCIe 5.0 | $10,730.82 | 698.6 | 28 | 2026-10-29 | https://www.sabrepc.com/KCD8XPJE15T3-Kioxia-S7964311 | WebFetch ✓: "$10,730.82", "In Stock" |
| Kioxia CD8P-R SED (KCD8DPJE15T3) | 15.36 TB | TLC | E3.S, PCIe 5.0 | $10,730.82 | 698.6 | 4 | 2026-10-17 | https://www.sabrepc.com/KCD8DPJE15T3-Kioxia-S8304719 | `"inventory":4` `"price":10730.82` |
| Kioxia CD8-R (KCD8XRUG15T3) | 15.36 TB | TLC | U.2, PCIe 4.0 | $11,820 | 769.5 | 127 | 2026-10-27 | https://www.sabrepc.com/KCD8XRUG15T3-Kioxia-S6942818 | `"inventory":127` `"price":11820` |
| Micron 7600 PRO (MTFDLBQ15T3THG-1BP1DFCYYR) | 15.36 TB | TLC | E3.S, PCIe 5.0 | $13,971.43 | 909.6 | 48 | 2026-10-12 | https://www.sabrepc.com/MTFDLBQ15T3THG-1BP1DFCYYR-Micron-S9282341 | WebFetch ✓: "$13,971.43", "In Stock" |
| Solidigm D7-P5520 (SSDPF2KX153T11Z) | 15.36 TB | TLC | U.2, PCIe 4.0 | $14,250 | 927.7 | 9 | 2026-10-27 | https://www.sabrepc.com/SSDPF2KX153T11Z-Solidigm-S8112628 | `"inventory":9` `"price":14250` |
| Solidigm D7-PS1010 (SB5PH27X153T001) | 15.36 TB | TLC | U.2, PCIe 5.0 | $16,395 | 1,067.4 | 5 | 2026-10-27 | https://www.sabrepc.com/SB5PH27X153T001-Solidigm-S8084130 | WebFetch ✓: "$16,395.00", "In Stock" |
| Micron 9550 PRO (MTFDLBQ15T3THA-1BK1DABYYR) | 15.36 TB | TLC | E3.S, PCIe 5.0 | $18,286.26 | 1,190.5 | 43 | 2026-10-25 | https://www.sabrepc.com/MTFDLBQ15T3THA-1BK1DABYYR-Micron-S161614233 | `"inventory":43` `"price":18286.26` |
| Micron 7600 PRO (MTFDLCE15T3THG-1BP1DFCYYR) | 15.36 TB | TLC | E1.S 15 mm | $18,383.46 | 1,196.8 | 8 | 2026-10-07 | https://www.sabrepc.com/MTFDLCE15T3THG-1BP1DFCYYR-Micron-S9282313 | `"inventory":8` `"price":18383.46` |
| Micron 6550 ION (MTFDLBQ30T7THL-1BK1DFCYYR) | 30.72 TB | TLC | E3.S, PCIe 5.0 | $13,993.50 | 455.5 | 6 | 2026-10-17 | https://www.sabrepc.com/MTFDLBQ30T7THL-1BK1DFCYYR-Micron-S8797287 | WebFetch ✓: "$13,993.50", "In Stock" (listed as "30.70 TB") |
| Micron 9550 PRO (MTFDLAL30T7THA-1BK1DABYYR) | 30.72 TB | TLC | U.2, PCIe 5.0 | $35,109.62 | 1,142.9 | 118 | 2026-10-25 | https://www.sabrepc.com/MTFDLAL30T7THA-1BK1DABYYR-Micron-S109173291 | `"inventory":118` `"price":35109.62` |
| Micron 6550 ION (MTFDLAL61T4THL-1BK1DFCYYR) | 61.44 TB | TLC | U.2, PCIe 5.0 | $47,498.43 | 773.1 | 8 | 2026-10-27 | https://www.sabrepc.com/MTFDLAL61T4THL-1BK1DFCYYR-Micron-S8797281 | `"inventory":8` `"price":47498.43` |
| Kioxia CD9P-R (KCD9XPUG61T4) | 61.44 TB | TLC | U.2, PCIe 5.0 | $36,480 | 593.8 | 6 | 2026-10-28 | https://www.sabrepc.com/KCD9XPUG61T4-Kioxia-S10396073 | WebFetch ✓: "$36,480.00", "In Stock" |
| **Solidigm D5-P5336 (SBFPF2BV614T001)** | 61.44 TB | **QLC** | U.2, PCIe 4.0 | $47,295 | **769.8** | 2 | 2026-10-28 | https://www.sabrepc.com/SBFPF2BV614T001-Solidigm-S7402588 | WebFetch ✓: "$47,295.00", "In Stock" |

**7.68 TB TLC in stock at SabrePC (same API pull, `$/TB` = price ÷ 7.68):**

| Model | Form factor | Price | $/TB | Inventory | URL |
|---|---|---|---|---|---|
| Kioxia CD8P-R KCD8XPUG7T68 | U.2 Gen5 | $5,370 | 699.2 | 51 | https://www.sabrepc.com/KCD8XPUG7T68-Kioxia-S7466403 |
| Solidigm D7-P5520 SSDPF2KX076T11Z | U.2 Gen4 | $5,340 | 695.3 | 13 | https://www.sabrepc.com/SSDPF2KX076T11Z-Solidigm-S8112501 |
| Solidigm D7-PS1010 SB5PH27X076T001 | U.2 Gen5 | $6,300 | 820.3 | 16 | https://www.sabrepc.com/SB5PH27X076T001-Solidigm-S8084161 |
| Kioxia CD9P-R KCD9XPUG7T68 | U.2 Gen5 | $5,686.32 | 740.4 | 50 | https://www.sabrepc.com/KCD9XPUG7T68-Kioxia-S10853641 |
| Kioxia CD8P-R KCD8DPJE7T68 | E3.S | $5,483.40 | 714.0 | 13 | https://www.sabrepc.com/KCD8DPJE7T68-Kioxia-S8304628 |
| Micron 7450 PRO MTFDKCB7T6TFR-1BC1ZABYYR | U.3 7 mm | $5,124 | 667.2 | 12 | https://www.sabrepc.com/MTFDKCB7T6TFR-1BC1ZABYYR-Micron-S5568003 |
| Micron 7450 PRO MTFDKCC7T6TFR-1BC1ZABYYR | U.3 15 mm | $7,020 | 914.1 | 9 | https://www.sabrepc.com/MTFDKCC7T6TFR-1BC1ZABYYR-Micron-S5469323 |
| Micron 7500 PRO MTFDKCC7T6TGP-1BK1DABYYR | U.3 Gen4 | $8,053.31 | 1,048.6 | 62 | https://www.sabrepc.com/MTFDKCC7T6TGP-1BK1DABYYR-Micron-S7634707 |
| Micron 7600 PRO MTFDLBQ7T6THG-1BP1DFCYYR | E3.S | $8,053.31 | 1,048.6 | 48 | https://www.sabrepc.com/MTFDLBQ7T6THG-1BP1DFCYYR-Micron-S9279576 |
| Micron 9550 PRO MTFDLBQ7T6THA-1BK1DABYYR | E3.S | $10,536.31 | 1,371.9 | 13 | https://www.sabrepc.com/MTFDLBQ7T6THA-1BK1DABYYR-Micron-S101601186 |
| Micron 7600 PRO MTFDLAL7T6THG-1BP1DFCYYR | U.2 | $10,596.47 | 1,379.7 | 81 | https://www.sabrepc.com/MTFDLAL7T6THG-1BP1DFCYYR-Micron-S9279651 |

**Price trend from SabrePC's change log.** The log is embedded in the API, is partial, and also records reversals:
- D5-P5336 61.44 TB:
  - 2026-06-17: `"from":34509,"to":39000`
  - 2026-08-20: 44,182.5 → 47,190
  - 2026-08-21: back to 44,182.5
  - Now $47,295, so about +37% versus the June 17 starting price.
- D7-PS1010 15.36 TB:
  - 2026-07-01: 12,931.67 → 13,083
  - 2026-07-31: 13,658.06 → 15,450
  - Now $16,395
- Kioxia CD8-R 15.36 TB:
  - 2026-07-01: 13,245 → 9,898.5
  - Now $11,820
  - This one is volatile, not monotonic.

**NAND type sources:**
- Micron 6550 ION is TLC: Blocks & Files 2024-11-12 (snippet: "Micron's Gen5 G8 TLC").
- Kioxia CD9P is TLC (BiCS8): Kioxia America release 2025-06-19 via search.
- Micron 6600 ION is QLC: "G9 QLC NAND", Blocks & Files 2025-07-30 (snippet).
- Solidigm D5-P5336 is QLC: listed as "3D5, QLC" in retailer titles.

###### A2.2 SabrePC: list prices on out-of-stock new drives (weaker; inventory 0)

- Same API pull, 2026-10-30.
- `"inventory":0` on all of these, so the price may be stale or an estimate.

| Model (MPN) | Cap. | NAND | FF | Price | $/TB | Note |
|---|---|---|---|---|---|---|
| Solidigm D5-P5336 SBFPF2BV307T001 | 30.72 | QLC | U.2 | $17,987.06 | 585.5 | https://www.sabrepc.com/SBFPF2BV307T001-Solidigm-S7402370 |
| Solidigm D5-P5336 SBFPFABV307T001 | 30.72 | QLC | E3.S | $13,670.06 | 445.0 | https://www.sabrepc.com/SBFPFABV307T001-Solidigm-S8018705; page shows "Out of Stock" (curl) |
| Solidigm D5-P5336 SBFPF2BV153T001 | 15.36 | QLC | U.2 | $9,291.72 | 604.9 | https://www.sabrepc.com/SBFPF2BV153T001-Solidigm-S7402373 |
| Solidigm D5-P5336 SBFPF2BV0P12001 | 122.88 | QLC | U.2 | $69,548.60 | 566.0 | https://www.sabrepc.com/SBFPF2BV0P12001-Solidigm-S8752002 |
| Samsung BM1743 MZWMO30THCLF-00AW7 | 30.72 | QLC | U.2 | $15,633.33 | 508.9 | https://www.sabrepc.com/MZWMO30THCLF-00AW7-Samsung-S8977623 |
| Samsung BM1743 MZWMO61THCLF-00AW7 | 61.44 | QLC | U.2 | $31,446.66 | 511.8 | https://www.sabrepc.com/MZWMO61THCLF-00AW7-Samsung-S8977581 |
| Samsung PM1743 MZWLO15THBLA-00A07 | 15.36 | TLC | U.2 Gen5 | $10,313.34 | 671.4 | https://www.sabrepc.com/MZWLO15THBLA-00A07-Samsung-S7066067 |
| Samsung PM1743 MZ3LO15THBLA-00A07 | 15.36 | TLC | E3.S | $9,666.66 | 629.3 | https://www.sabrepc.com/MZ3LO15THBLA-00A07-Samsung-S7428385 |
| Samsung PM9D3a MZ3L615THBLF-00AW7 | 15.36 | TLC | E3.S | $9,480 | 617.2 | https://www.sabrepc.com/MZ3L615THBLF-00AW7-Samsung-S8690871 |
| Samsung PM9D3a MZWL615THBLF-00AW7 | 15.36 | TLC | U.2 | $2,341.50 | 152.4 | **STALE / implausible** for 2026. https://www.sabrepc.com/MZWL615THBLF-00AW7-Samsung-S8685306 |
| Samsung PM9A3 MZQL215THBLA-00A07 | 15.36 | TLC | U.2 Gen4 | $3,300 | 214.8 | **STALE**. The latest logged price change is 2024-09-10 (2,087.91 → 2,466.99). https://www.sabrepc.com/MZQL215THBLA-00A07-Samsung-S5438135 |
| Micron 7500 PRO MTFDKCC15T3TGP-1BK1DABYYR | 15.36 | TLC | U.3 Gen4 | $10,115.22 | 658.5 | https://www.sabrepc.com/MTFDKCC15T3TGP-1BK1DABYYR-Micron-S7642546 |
| Kioxia CD8P-R KCD8XPUG30T7 | 30.72 | TLC | U.2 Gen5 | $18,750 | 610.4 | https://www.sabrepc.com/KCD8XPUG30T7-Kioxia-S7467278 |
| Kioxia CM7-R KCM7XRJE15T3 | 15.36 | TLC | E3.S | $12,095.27 | 787.5 | https://www.sabrepc.com/KCM7XRJE15T3-Kioxia-S6942833 |

###### A2.3 Saitech (esaitech.com, California)

- **Condition:** new.
- **Availability caveat:** every page says "In stock: Yes" but also "This product is available for special order and may take longer to ship" and "We source this item directly from the OEM as a special order". Treat these as quote-able prices, not shelf stock.
- **Retrieval:** WebFetch on 2026-10-30 unless noted.

| Model (MPN) | Cap. | NAND | FF | Price | $/TB | URL | Quote |
|---|---|---|---|---|---|---|---|
| Samsung PM9D3a MZWL630THBLF-00AW7 | 30.72 | TLC | U.2 Gen5 | $16,516 | 537.6 | https://esaitech.com/products/samsung-mzwl630thblf-00aw7-30-72tb-solid-state-drive | "Sale price $16,516.00; regular price $41,991.71"; "Condition: New" |
| Micron 6550 ION MTFDLAL61T4THL-1BK1DFCYYR | 61.44 | TLC | U.2 | $43,749 | 712.1 | https://esaitech.com/products/micron-6550-ion-mtfdlal61t4thl-1bk1dfcyyr-61-44tb-ssd | "Sale price $43,749.00" (regular $51,359.99) |
| Micron 6600 ION MTFDLAL61T4QHF-1BQ1DFCYYR | 61.44 | QLC | U.2 Gen5 | $37,694 | 613.5 | https://esaitech.com/products/micron-mtfdlal61t4qhf-1bq1dfcyyr-61-44tb-u-2-ssd | "$37,694.00"; "Regular price$43,063.99"; "Condition: New" |
| Micron 6600 ION MTFDLAL30T7QHF-1BQ1DFCYYR | 30.72 | QLC | U.2 Gen5 | $20,276 | 660.0 | https://esaitech.com/products/micron-mtfdlal30t7qhf-1bq1dfcyyr-30-72tb-u-2-ssd | "$20,276.00"; "SPECIAL ORDER ITEM" |
| Solidigm D5-P5336 SBFPF2BV614T001 | 61.44 | QLC | U.2 | $33,107 | 538.9 | https://esaitech.com/products/solidigm-sbfpf2bv614t001-d5-p5336-61-44tb-2-5-inch-ssd | "$33,107.00"; "Condition: New" |
| Kioxia CD8-R KCD8DRUG15T3 (SED) | 15.36 | TLC | U.2 Gen4 | $7,195 | 468.4 | https://esaitech.com/products/kioxia-kcd8drug15t3-cd8-r-series-15-36tb-sed-pcie-ssd | "Sale price$7,195.00"; "Condition: New" |
| Micron 7600 PRO MTFDLAL15T3THG-1BP1DFCYYR | 15.36 | TLC | U.2 Gen5 | $13,224 | 860.9 | https://esaitech.com/products/micron-7600-pro-mtfdlal15t3thg-1bp1dfcyyr-15-36tb-ssd | "$13,224.00" (regular $15,106.99) |

**More Saitech prices, catalog JSON only (curl of `products.json` on 2026-10-30; individual pages not checked):**
- Micron 6600 ION 122.88 TB U.2 (QLC): $70,309 → $572.2/TB
- Micron 9550 PRO 15.36 TB E3.S: $16,843 → $1,096.5/TB
- Micron 6550 ION 30.72 TB E3.S: $12,889 → $419.6/TB
- Samsung PM9D3a 15.36 TB E1.S: $8,196 → $533.6/TB

###### A2.4 Other retailers

| Model | Cap. | FF | Price | $/TB | Retailer / status | Date | URL | Quote / basis |
|---|---|---|---|---|---|---|---|---|
| Solidigm D5-P5336 SBFPFWBV614T001 (QLC) | 61.44 | E1.L | $36,098.99 | 587.5 | Zones; availability field blank | retrieved 2026-10-30 | https://www.zones.com/site/product/index.html?id=114604807 | WebFetch: "SOLIDIGM D5-P5336 SERIES (61.44TB, E1.L 9.5MM PCIE 4.0 X4, 3D5, QLC) S", price $36,098.99 |
| Solidigm D5-P5336 SBFPF2BV614T001 (QLC) | 61.44 | U.2 | $31,467.99 | 512.2 | Avendor; "Only 0 units left" | retrieved 2026-10-30 | https://www.avendor.com/products/solidigm-d5-p5336-series-61-44tb-2-5in-pcie-4-0-x4-3d5-qlc-single-pack | WebFetch: "Sale price$31,467.99" |
| Kioxia CD8P-V KCD8XPUG12T8 (TLC, 3 DWPD) | 12.8 | U.3 Gen5 | $4,599 | 359.3 | ServerPartDeals; available; **new with seller (not OEM) warranty** | record updated 2026-10-29 | https://serverpartdeals.com/products/kioxia-cd8p-v-kcd8xpug12t8-12-8tb-3-dwpd-pcie-gen-5-0-x4-128-gt-s-3d-tlc-u-3-nvme-2-5in-ssd | curl JSON: `"price":"4599.00"`, tags `condition:New`, body "Condition: New - 3 Year Seller Limited Period Warranty". **Outlier:** SabrePC lists the same MPN at $14,823 with 6 in stock ($1,158/TB). |
| D5-P5336 SBFPF2BV614T001 | 61.44 | U.2 | $28,085.10 | 457.1 | ShopBLT | undated | https://www.shopblt.com/item/solidigm-d5-p5336-61.44tb-2.5in-pcie/750y_sbfpf2bv614t001.html | **snippet only**: "...61.44tb 2.5in Pcie 4.0 Generic Opal Mm#Aa001770l for $28,085.10." (page returned 403) |
| D5-P5336 SBFPF2BV614T001 | 61.44 | U.2 | $25,527.86 | 415.5 | CompSource; out of stock | "as of September 4, 2026" (per snippet) | https://www.compsource.com/buy/SBFPF2BV614T001/Solidigm-6455/Solidigm-D5p5336-6144-Tb-Solid-State-Drive--25inch-Internal--U2-pci-Express-Nvme-40-X4--Serve/ | **snippet only** (403) |
| D5-P5336 SBFPF2BV614T001 | 61.44 | U.2 | $28,949 | 471.2 | Tech-America; out of stock | undated | https://www.tech-america.com/item/solidigm-d5-p5336-61-44-tb-solid-state-drive/sbfpf2bv614t001 | **snippet only** (403) |
| D5-P5336 SBFPF2BV614T001 | 61.44 | U.2 | $25,950.95 | 422.4 | CDW | undated | https://www.cdw.com/product/solidigm-d5-p5336-61.44-tb-solid-state-drive-2.5-internal-u.2-pci-exp/7785193 | **snippet only** (403) |
| D5-P5336 30.72 TB OPAL | 30.72 | U.2 | $16,195.80 | 527.2 | Walmart; out of stock | undated | https://www.walmart.com/ip/Solidigm-Solid-State-Drive-D5-P5336-Series-61-44TB-2-5in-PCIe-4-0-x4-3D5-QLC-Generic-OPAL-Single-Pack-Data-Center-Server-Internal-SSD-SBFPF2BV614T001/5407714229 (search result) | **snippet only** |
| Solidigm D7-PS1010 SB5PH27X153T001 | 15.36 | U.2 Gen5 | $6,181.71 | 402.5 | Mouser US; "3 in stock" | undated cached page; likely STALE | https://www.mouser.com/c/?m=Solidigm | **snippet only**: "US$6,181.71 for quantity 1 ... A tariff of 16 % may be applied if shipping to the United States." Live page blocked. |

**Searched for but not found as in-stock new US listings with a verifiable 2026 price:**
- Samsung PM9A3, PM1743 and PM9D3a at 15.36 TB (only out-of-stock or special order)
- Solidigm D5-P5336 30.72 TB (only out of stock)
- Kioxia CM7-R (only out of stock)
- Samsung BM1743 (only out of stock)
- Micron 7500 PRO 15.36 TB (only out of stock)
- Any listing at B&H, Newegg, CDW, Provantage or ShopBLT: those sites were blocked, so no page-level check was possible.

##### A3. Typical $/TB, late October 2026 (ESTIMATES, my synthesis)

- **TLC, 15.36 TB class, new, US retail, in stock:**
  - **$700-1,200/TB.** Median about **$920/TB** across 8 SabrePC listings (range $699-$1,197/TB).
    - Gen4 read-intensive and Kioxia CD8P-R: about $700-930/TB.
    - Gen5 high-performance (D7-PS1010, 9550 PRO, 7600 PRO E1.S): about $1,070-1,200/TB.
  - Special-order quotes run lower: Saitech Kioxia CD8-R at $468/TB, Samsung PM9D3a at $534-538/TB.
  - VDURA's Q3 2026 30 TB TLC figure is about $736/TB.
  - **Working figure: about $750-950/TB.**
- **TLC, high capacity (30.72-61.44 TB "capacity TLC": Micron 6550 ION, Kioxia CD9P-R, PM9D3a 30.72):** about **$420-775/TB**, for example $456/TB (6550 ION 30.72 E3.S, in stock) and $594/TB (CD9P-R 61.44, in stock).
- **QLC, 30.72-122.88 TB:**
  - Page-verified listings: **$512-770/TB**. The only one in stock is SabrePC D5-P5336 61.44 TB at $770/TB. Special orders are $539-660/TB; Zones is $588/TB.
  - Snippet-only listings: $415-471/TB.
  - VDURA's Q3 2026 30 TB QLC figure is about $589/TB.
  - **Working figure: about $550-650/TB.** In the late-2026 channel, QLC is not reliably cheaper per TB than capacity-optimized TLC.
- **Hyperscaler contract prices:** these should sit below the retail figures (INFERENCE) but are not public. TrendForce's quarter-on-quarter steps compound to about 3.9x over 3Q25-3Q26, and another +23-28% is forecast for 4Q26.
- **For comparison (STALE):** the 2025 level was about **$100-113/TB TLC and $80-90/TB QLC** (VDURA, Q2-Q3 2025). 2025 prices understate late-2026 costs by roughly 5-8x.

---

#### TASK B: US data center colocation and electricity

##### B1. Wholesale colocation, $/kW per month

**Power treatment:**
- CBRE's text says only that its "Rental rates are quoted asking rates for 250+ kW at N+1/Tier III requirements". It does not say whether power is included.
- datacenterHawk (2026-02-12, https://datacenterhawk.com/resources/fundamentals/colocation-data-center-pricing-a-2026-beginner-s-guide, WebFetch) says wholesale electricity is a pass-through: "electricity costs are handled as pass-through charges, often referred to as + E".
- INFERENCE: the wholesale $/kW figures below exclude metered energy.

| Metric | Value | Period | Source (date) | Quote |
|---|---|---|---|---|
| Primary-market average asking rate, 250-500 kW | **$196.25/kW-mo** (+6.6% YoY); the same page elsewhere gives **$195.94** (+6.5% YoY) | H2 2025 (somewhat STALE) | CBRE, North America Data Center Trends H2 2025, published 2026-02-25, https://www.cbre.com/insights/books/north-america-data-center-trends-h2-2025 (WebFetch) | "rose by 6.6% year-over-year to a record $196.25 per kW/month"; "rose by 6.5% year-over-year to $195.94 per kW/month"; "Pricing for 3-to-10-MW requirements jumped by 12.5% year-over-year" |
| Change in average asking rate by tier | 250-500 kW **+4.3%**; 500 kW-3 MW **+7.9%** (paraphrase); 3-10 MW **+8.3%**; 10+ MW **+6.7%**. **No dollar level published in the text.** | H1 2026 | CBRE, North America Data Center Trends H1 2026, published 2026-08-27, https://www.cbre.com/insights/books/north-america-data-center-trends-h1-2026 (WebFetch) | "Average asking rates for 250-to-500-kW requirements across primary markets rose by 4.3% in H1"; "Average rental rates for 3-to-10-MW deployments rose by 8.3% in H1."; "Asking rates for 10-plus-MW deployments across primary markets rose by 6.7% in H1." Vacancy: "primary market vacancy fell to a record low of 1.4% in H1 from 1.6% in H1 2025"; absorption 1,456.2 MW. |
| Implied H1 2026 average, 250-500 kW | **about $204-205/kW-mo** | H1 2026 | **ESTIMATE:** $196.25 × 1.043 = $204.69 ($195.94 × 1.043 = $204.37). One aggregator quotes "$204.69", which is exactly this computation, so it is not an independent CBRE figure. | n/a |
| CBRE forecast | **above $215/kW-mo** for 250-500 kW (no time frame given) | 2026 outlook; figures cite "CBRE Research, Q2 2026" | CBRE U.S. Real Estate Market Outlook Midyear Review 2026, Data Centers chapter (page undated), https://www.cbre.com/insights/books/us-real-estate-market-outlook-midyear-review-2026/data-centers (WebFetch) | "We expect average rental rates for 250-500kW requirements to be above $215 per kW per month." |
| Northern Virginia, 250-500 kW | **$190-235/kW-mo** | Q1 2026 | CBRE Global Data Center Trends 2026, 2026-06-17, https://www.cbre.com/insights/reports/global-data-center-trends-2026 (WebFetch) | "followed by Northern Virginia with a broader price range of $190 to $235" |
| Northern Virginia, 10+ MW | **$160-185/kW-mo** | H1 2026 | CBRE H1 2026, Northern Virginia chapter, https://www.cbre.com/insights/books/north-america-data-center-trends-h1-2026/northern-virginia-data-center-market (WebFetch); also Data Center Frontier (Matt Vincent), 2026-08-28, https://www.datacenterfrontier.com/site-selection/news/55401462/cbre-record-data-center-construction-fails-to-ease-capacity-crunch | "asking rates for 10-plus-MW requirements rose to $160 to $185 per kW"; "Overall rental rates held steady in H1."; vacancy "fell to 0.24%"; 10+ MW rates up "just 1.5%" |
| Chicago, 250-500 kW | **$200-230/kW-mo**, +14.7% YoY | Q1 2026 | CBRE press release, 2026-06-24, https://www.cbre.com/press-releases/global-data-center-supply-cant-keep-up-with-demand-resulting-in-extreme-scarcity-of-available-space ; and the 2026-06-17 report above | "Chicago had the highest rental rates, ranging from $200 to $230 per kW/month for a 250-to-500-kW requirement"; "Chicago had the highest increase of 14.7% and Atlanta rose by 2%, while Dallas-Ft. Worth asking rents were unchanged." H1 2026: Chicago 10+ MW +9.7%. |
| Silicon Valley | **$200-275/kW-mo** (deployment size not stated) | H1 2026 | CBRE press release, 2026-09-01, https://www.cbre.com/press-releases/silicon-valley-data-center-demand-continues-outpace-supply-causing-vacancy-fall-further-rents-rise (WebFetch) | "Asking rental rates in Silicon Valley range from $200 to $275 per kW per month"; vacancy 4.2%. H1 2026 10+ MW: "Silicon Valley and Hillsboro asking rates were unchanged in H1". |
| Dallas-Fort Worth | **No 2026 dollar figure found.** Q1 2026 asking rents were unchanged YoY. | Q1 2026 | CBRE 2026-06-17 / 2026-06-24 (above) | "Dallas-Ft. Worth asking rents were unchanged" |
| Atlanta | **No 2026 dollar figure found.** +2% YoY (Q1 2026); 10+ MW +14.5% (H1 2026); increases in all four tiers. | Q1-H1 2026 | CBRE (above) | "Atlanta had the broadest pricing gains of any market, with rates rising across all four deployment tiers." |
| Phoenix | **No 2026 dollar figure found.** The last CBRE figure found is $170-210 (H1 2024, **STALE**, secondary). | n/a | CBRE H1 2026 Phoenix chapter has no rates in its text (Figure 5 is an image) | n/a |
| Large-deal market level (datacenterHawk) | **$145-170/kW-mo** for current large and hyperscale deals; triple-net (NNN) deals are $15-25/kW lower; primary markets "moved $25–30/kW in a single calendar year" | early 2026 | datacenterHawk "2026 Data Center Deal Trends", 2026-03-16, https://datacenterhawk.com/resources/market-insights/2026-data-center-deal-trends (WebFetch) | "At $145–$170/kW with volatile construction and uncertain operating costs at GW scale"; "Primary NA markets have moved $25–30/kW in a single calendar year." Renewals of 2015-2019 leases signed at "$70–85/kW". |
| Signed wholesale leases, Digital Realty Americas, >1 MW | **Q1 2026 $174; Q2 2026 $156; Q3 2026 $264** per kW-mo (GAAP base rent). Monthly basis confirmed by my arithmetic, e.g. Q3: $203,002k ÷ 64.0 MW ÷ 12 = $264.3. | Q1-Q3 2026 | DLR 8-K Ex. 99.1: Q1 (2026-04-23) https://www.sec.gov/Archives/edgar/data/0001297996/000110465926047702/dlr-20260423xex99d1.htm ; Q2 (2026-07-23) https://www.sec.gov/Archives/edgar/data/0001297996/000110465926086270/dlr-20260723xex99d1.htm ; Q3 (2026-10-29) https://www.sec.gov/Archives/edgar/data/0001297996/000110465926120212/dlr-ex99d1.htm (WebFetch) | Q1: "> 1 MW 280,082 134.5 174". Q2: "> 1 MW | 82,706 | 44.2 | 156". Q3: "> 1 MW | 203,002 | 64.0 | 264". **Note:** the Q3 jump probably reflects deal mix (e.g. high-density AI deployments). INFERENCE, not stated by DLR. |
| Rent growth context (JLL) | about +70% since 2020, about 9%/year; vacancy 1% | H1 2026 | JLL news release, 2026-08-11, https://www.jll.com/en-us/newsroom/data-center-demand-exceeds-expectations-in-h1-2026 (WebFetch) | "Data center rental rates have increased nearly 70% since 2020"; "With vacancy sustained at 1% for the third consecutive year". No $/kW published. |

**National average:** no single published 2026 national figure. The CBRE primary-market 250-500 kW average is the usual proxy: $196.25 (H2 2025), about $205 implied for H1 2026 (ESTIMATE), and above $215 expected by CBRE.

**Data-quality warning:** several 2026 aggregator pages put wholesale Northern Virginia and Dallas at $155-175 and Phoenix at $105-120 (datacentres.com "Research", 2026-08-31). These were not reproducible: the page now shows no $/kW figures when fetched on 2026-10-30, and it gives no primary source. I have excluded them.

##### B2. Retail colocation (0-1 MW, cabinets)

| Metric | Value | Source (date) | Quote | Power? |
|---|---|---|---|---|
| Digital Realty Americas, new 0-1 MW leases, GAAP base rent | **Q1 2026 $256; Q2 2026 $293; Q3 2026 $284** per kW-mo | DLR 8-K Ex. 99.1 (same three links as above) | Q1: "0-1 MW $40,444 13.2 $256"; Q2: "0-1 MW | $37,131 | 10.6 | $293"; Q3: "0-1 MW | $39,587 | 11.6 | $284" | Likely **excluded** (INFERENCE). The leasing table does not define it, but DLR reports "Tenant reimbursements - Utilities" ($423,919k in Q3 2026) separately from "Rental revenues" ($1,224,802k). |
| Vendor blog, retail all-in | about **$250/kW-mo** "all-in" | Inflect (colocation marketplace, not independent), page date 2026-04-01, https://inflect.com/blog/colocation-pricing-what-to-expect-for-racks-cabinets-and-cages-in-2026 (WebFetch) | "Fixed all-in kW rate (~$250/kW/month, covering space, power delivery, and cooling)"; "A full rack in a centrally located Tier III facility with dual 20-amp 208V circuits typically costs 1,000 to 1,500 dollars per month." | "power delivery" covers circuits; energy is included in many retail rack quotes, but this is not stated. **ESTIMATE:** a 20 A / 208 V circuit gives 3.33 kW at 80%, so $1,000-1,500 per rack is about **$300-450 per usable kW-month**. |

- **Uptime Institute 2026:** the survey (2026-07-29) has no colocation price figures that I could find.
- **Cushman & Wakefield 2026:** the Global Data Center Market Comparison (2026-05-20) has no rent figures in its press materials.
- **JLL:** publishes no $/kW figures.

##### B3. US electricity prices: EIA Electric Power Monthly

- **Edition:** Data for August 2026, released 2026-10-23 (next release 2026-11-24).
- **Retrieval:** curl, so values are exact.
- **Caveat:** EIA's 2026 values are "preliminary estimates based on a cutoff model sample". The averages are revenue divided by sales, so they include demand charges.

**Table 5.3 (U.S. total), cents/kWh.** https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_3

| Period | Commercial | Industrial | All sectors | Exact row quote (Res, Com, Ind, Transp, All) |
|---|---|---|---|---|
| **August 2026 (latest month)** | **14.47** | **9.64** | 14.87 | "August 18.16 14.47 9.64 14.86 14.87" |
| **2026 YTD (Jan-Aug)** | **14.04** | **9.09** | 14.37 | "Year to Date ... 2026 18.19 14.04 9.09 15.64 14.37" |
| Rolling 12 months to Aug 2026 | 13.87 | 8.91 | 14.15 | "2026 18.04 13.87 8.91 15.16 14.15" |
| 2025 annual | 13.37 | 8.51 | 13.56 | "2025 17.23 13.37 8.51 13.87 13.56" |
| 2024 annual (STALE) | 12.75 | 8.13 | 12.94 | "2024 16.48 12.75 8.13 12.75 12.94" |

2026 monthly industrial prices: Jan 9.29, Feb 8.94, Mar 8.56, Apr 8.60, May 8.68, Jun 9.16, Jul 9.77, Aug 9.64.

**Tables 5.6.A (August 2026) and 5.6.B (year to date through August 2026), selected states, cents/kWh.**
- https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a
- https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_b

| State | Com. Aug-26 | Ind. Aug-26 | Com. YTD-26 | Ind. YTD-26 | (Aug-25 Com / Ind) |
|---|---|---|---|---|---|
| **Virginia** | 11.14 | 9.98 | 11.20 | 10.07 | 9.85 / 9.40 |
| **Texas** | 8.96 | 7.21 | 8.60 | 6.77 | 8.76 / 6.42 |
| Arizona | 13.05 | 9.73 | 12.28 | 7.94 | 12.98 / 8.88 |
| Georgia | 13.81 | 13.05 (monthly outlier vs 8.20 a year earlier; YTD 8.67) | 12.01 | 8.67 | 11.16 / 8.20 |
| Illinois | 14.67 | 11.33 | 14.05 | 10.42 | 13.94 / 10.18 |
| Ohio | 12.31 | 9.75 | 13.61 | 10.23 | 11.42 / 8.47 |
| Oregon | 10.72 | 8.75 | 10.59 | 8.38 | 9.84 / 8.44 |
| Washington | 11.81 | 7.43 | 11.86 | 7.17 | 11.02 / 7.06 |
| Nevada | 9.80 | 10.20 | 9.36 | 8.69 | 10.05 / 9.69 |
| North Carolina | 10.73 | 8.23 | 10.61 | 7.95 | 10.02 / 7.80 |
| Pennsylvania | 13.93 | 10.47 | 13.90 | 10.82 | 12.68 / 9.66 |
| Iowa | 14.15 | 9.31 | 11.66 | 7.66 | 12.87 / 8.94 |
| New York | 23.06 | 10.54 | 22.93 | 10.33 | 22.33 / 10.20 |
| California | 30.02 | 24.12 | 26.96 | 21.11 | 29.24 / 23.84 |
| U.S. total | 14.47 | 9.64 | 14.04 | 9.09 | 13.87 / 8.98 |

- Exact row quotes from Table 5.6.A:
  - "Virginia| 17.64| 15.85| 11.14| 9.85| 9.98| 9.40|..."
  - "Texas| 15.91| 15.40| 8.96| 8.76| 7.21| 6.42|..."
- Exact row quotes from Table 5.6.B:
  - "Virginia|16.95|15.00|11.20|9.67|10.07|9.31|..."
  - "Texas|16.03|15.18|8.60|8.59|6.77|6.31|..."
- **Wholesale outlook:** EIA's Short-Term Energy Outlook, released 2026-10-06 (https://www.eia.gov/outlooks/steo/report/elec_coal_renew.php, curl), says "We forecast wholesale prices in the PJM region this year will increase by 41% compared with 2025, the largest increase across all regions." PJM covers Virginia and Ohio.

---

#### Not found or could not confirm

1. TrendForce absolute enterprise SSD contract levels ($/GB or $/TB). The reports are paywalled; only quarter-on-quarter % changes are public.
2. A primary-source in-stock new listing (Aug-Oct 2026) for:
   - Samsung PM9A3, PM1743 or PM9D3a at 15.36 TB
   - Solidigm D5-P5336 at 30.72 TB
   - Kioxia CM7-R
   - Samsung BM1743
   - Micron 7500 PRO 15.36 TB
   - Only out-of-stock list prices or special-order quotes were found.
3. B&H, Newegg, CDW, Provantage, ShopBLT, Connection, Insight, SHI, Mouser and CompSource could not be checked at page level (403 or bot wall). Prices from them above are search snippets only.
4. The CBRE H1 2026 dollar averages: the text gives only % changes, and Figure 3 and the market Figure 5 are images not exposed to the fetcher.
5. 2026 $/kW-month figures for Dallas, Phoenix and Atlanta from CBRE, JLL, Cushman & Wakefield or datacenterHawk.
6. Any JLL, Cushman & Wakefield or Uptime 2026 $/kW figure.
7. A primary-source national average for retail all-in colocation per kW (with energy included).
8. Whether CBRE asking rates include power. INFERENCE: they do not, per the "+E" convention described by datacenterHawk.
9. VDURA's pricing basis (street, contract or list) is not documented in the coverage.
10. The SabrePC price change logs are partial: some logged reversals do not match the current price.
