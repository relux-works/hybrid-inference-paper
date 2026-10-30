# Fanless Macs, base Apple chips, small models, office GPU boxes, licences and TEEs (research note, 2026-10-30)

Scope: eight questions for the hybrid paper (server prefill, then the model state goes to an Apple Silicon laptop, which decodes). All pages read on 2026-10-30 (UTC).

Labels:
- **[fact]**: URL plus a short verbatim quote. Quotes from the Apple store and the AA/HF APIs are JSON fields.
- **[estimate]**: my own arithmetic or inference. The basis is stated.
- **[unverified]**: secondary source, forum or blog, or the method is unclear.
- **Not found**: I searched and found no primary statement.

Related notes in this folder:
- `hardware-2026-10.md`: M5 Pro/Max/Ultra, RTX PRO 6000 and RTX 5090 specs and prices.
- `models-apis-2026-10.md`: AA index history, Qwen timeline.

## Key numbers at a glance

| Topic | Number | Label |
|---|---|---|
| Fanless Air, sustained GPU loss in the 20-loop 3DMark stress test (worst loop vs best, or end vs start) | M1 −28%; M2 13" −23%, 15" −17%; M3 13" −25%; M4 13" −20%, 15" −22%; M5 13" −18% | fact (UL medians for M1/M2; Notebookcheck for M3-M5) |
| Same chip with a fan | MBP 13 M2: −2% (WLE), −4% (Steel Nomad Light) | fact (UL) |
| Air SoC power under load | bursts of 26-33 W, then about 8-9 W "within a few minutes". MBP 14 M5: 44 W, then 30 W | fact (Notebookcheck) |
| LLM run over many minutes on an Air | **not found** | – |
| Fanless analogues (iPhone running MLX) | −38% to −42% after 3 iterations (a few minutes) | fact (paper, GitHub) |
| MBP 14 M3 Max, llama.cpp decode | 8.68 → 2.37 tok/s over repeated runs (−73%); the cause was not thermal | fact (GitHub) |
| Prefill vs decode power, NVIDIA | Decode does draw much less. H200 decode: 137-300 W on a 700 W GPU. H100: a 50% power cap barely affects decode; prefill power rises with batch size | fact |
| Prefill vs decode power, Apple | **No measurement of both phases side by side found**. Decode alone: M2 Max GPU 28 W, settling to 17.4 W; M4 Max package about 24.7 W | fact / not found |
| Base-chip bandwidth | M1 68 / M2 100 / M3 100 / M4 120 / M5 153 / M6 170 GB/s | fact |
| MacBook Air M5: max RAM and US prices (512 GB) | 32 GB max.<br>13": $1,299 (16 GB, 8-core GPU), $1,399 (16 GB, 10-core), $1,499 (24 GB), $1,699 (32 GB).<br>15": $1,499 / $1,699 / $1,899 | fact (Apple store API) |
| Best open models for 24-32 GB (MLX 4-bit size; AA v4.1.1 index) | Qwen3.8-27B (16.05 GB; 52.0 xhigh / 44.5 medium)<br>Muse Glimmer 30B (19.41 GB; 35.1)<br>Qwen3.6-35B-A3B (20.40 GB; 32.1)<br>Gemma 4 26B-A4B (15.34 GB; 26.1) | fact |
| Best open model for 16 GB | Qwen3.5-9B (5.95 GB; 21.8) | fact |
| GeForce licence | "(v. February 25, 2025)", §2.8: "(ii) is not licensed for datacenter deployment". No wording about offices or workstations. The 2024 blockchain exception is gone | fact |
| US/EU circuits | 15 A/120 V: 1,440 W continuous. 20 A/120 V: 1,920 W. EU 16 A/230 V: 3,680 W nameplate | estimate (NEC 125% rule) |
| Box power at full load | 2× RTX 5090: 1.0-1.45 kW. 4× RTX 5090: 2.7-3.7 kW. 4× RTX PRO 6000 Max-Q: 1.65 kW peak | fact (vendor pages) |
| GPUs with confidential computing | H100, H200, B200, HGX B300, RTX Pro 6000 Blackwell Server Edition | fact (NVIDIA docs) |
| CPU TEEs for confidential computing | AMD SEV-SNP (Genoa/Milan) or Intel TDX (Emerald/Granite Rapids) | fact (NVIDIA docs) |
| Apple PCC | stateless computation, enforceable guarantees, no privileged runtime access, non-targetability, verifiable transparency | fact |

---

## 1. Fanless MacBook Air under sustained load

3DMark stress tests run a benchmark loop 20 times.
- [fact] Macworld: "a Stress Test mode that runs through the minute-long benchmark 20 times in a row" (https://www.macworld.com/article/3586152/3dmark-wild-life-is-a-much-need-modern-3d-graphics-benchmark-for-ios.html). So one stress test lasts about 20 minutes.
- [fact] UL defines "Frame Rate Stability = fpsLow / fpsHigh * 100" (https://support.benchmarks.ul.com/support/solutions/articles/44002134931-stress-test-result-screen).
- UL device pages show "the median of all the results submitted by users for this device". These are crowd medians, not lab runs (https://benchmarks.ul.com/hardware/tablet/MacBook+Air+(M2,+2022)+review).

### 1.1 Measured drops

| Device | What was measured | Result | Over what time | Source |
|---|---|---|---|---|
| MBA M1 (2020) | 3DMark stress, user median | Wild Life Extreme (WLE) "stability 72%"; Steel Nomad Light (SNL) "stability 80 %" | 20 loops | [fact] https://benchmarks.ul.com/hardware/tablet/MacBook+Air+(M1,+2020)+review |
| MBA 13 M2 (2022) | same | WLE "stability 77%"; SNL "stability 78 %" | 20 loops | [fact] https://benchmarks.ul.com/hardware/tablet/MacBook+Air+(M2,+2022)+review |
| MBA 15 M2 (2023) | same | WLE "stability 83%"; SNL "stability 83 %" | 20 loops | [fact] https://benchmarks.ul.com/hardware/tablet/MacBook+Air+15%E2%80%9D+(M2,+2023)+review |
| **MBP 13 M2 (fan)** | same | WLE "stability 98%"; SNL "stability 96 %" | 20 loops | [fact] https://benchmarks.ul.com/hardware/tablet/MacBook+Pro+13%E2%80%9D+(M2,+2022)+review |
| MBA 13 M2, 10-core GPU | package power | "briefly consume about 33 watts", then "a slightly lower package power of less than 9 watts" | "rapidly" | [fact] https://www.notebookcheck.net/Apple-MacBook-Air-M2-review-The-faster-10-core-GPU-isn-t-worth-it.640427.0.html (2022-08) |
| MBA 13 M3, 10-core GPU | WLE stress | "its result fell by about 25 % after 20 runs" | about 20 min | [fact] https://www.notebookcheck.net/Apple-MacBook-Air-13-M3-review-A-lot-faster-and-with-Wi-Fi-6E.811129.0.html (2024-03) |
| MBA 13 M3 | CPU | "~21 watts for a short while", then "balanced out at 10.5 watts during 12 minutes of continuous load (R23 Multi: 8,237 points, so ~19 % less)" | 12 min | same |
| MBA 13 M4, 8-core GPU | SNL stress | GPU "can consume a maximum of 15.5 watts, but this quickly levels out at around 8 watts"; "a drop in performance of around 20% under constant load" | minutes | [fact] https://www.notebookcheck.net/The-passively-cooled-M4-SoC-makes-the-competition-look-old-Apple-MacBook-Air-13-M4-entry-review.1002534.0.html (2025-04) |
| MBA 13 M4 | Cinebench loop | "Even after half an hour, its CB Multi score only dropped by 13% to 710 points" | 30 min | same |
| MBA 15 M4, 10-core GPU | GPU and CPU | "Under longer load, the GPU's performance dropped by around 22%"<br>CPU: "settled at 9 watts after 20 minutes of continuous load (~15.5 watts after 1 minute; 12 watts after 5 minutes)"<br>CB24: "After 30 minutes ... 776 points was only 11% lower" | 1 / 5 / 20 / 30 min | [fact] https://www.notebookcheck.net/Apple-MacBook-Air-15-M4-review.976933.0.html (2025-03) |
| **MBA 13 M5, 8-core GPU, 16 GB** | SNL stress | "The performance drops by around 18 percent in the synthetic 3DMark stress test (Steel Nomad Light)" | 20 loops | [fact] https://www.notebookcheck.net/Insane-performance-and-efficiency-without-fans-Apple-MacBook-Air-13-M5-Entry-Review.1242707.0.html (2026-03-07) |
| MBA 13 M5 | SoC, combined CPU+GPU | "consumes up to 26 Watts and then quickly levels off at around 8 Watts" | "quickly" | same |
| MBA 13 M5 | CB24 Multi | "After the stress test of CB24 Multi (30 minutes), the result is still 820 points at 9 Watts". The single run scored 957, so the drop is −14% [estimate, arithmetic] | 30 min | same |
| MBA 13 M5 | games | "SoC consumption was sitting between 7-8 Watts ... there is no throttling"<br>Cyberpunk 2077 "for one hour ... rock solid" | 60 min | same |

### 1.2 Same chip in a MacBook Pro (with a fan)

- **M2** [fact]: UL's WLE stability is 77% on the Air and 98% on the MBP 13 M2 (URLs above).
- **M3** [fact]: Notebookcheck compares the Air with "the MacBook Pro 14 M3, whose performance remains stable, however, thanks to its active cooling", and says "the Air has to slow down under permanent load" (M3 Air URL above).
- **M4 Air 13** [fact]: "After a brief load peak of around 27 watts, the M4 SoC's power consumption dropped to around 8 watts over the following few minutes" (M4 Air 13 URL above).
- **M4** [fact]: "M4 in the MBP 14 was 21% faster here" in the long Cinebench run (M4 Air 13 URL above).
- **M5** [fact]:
  - Air: "The deficit compared to the MacBook Pro 14 M5 with active cooling is still only 18 % during the Cinebench 2024 Multi test".
  - MBP 14 M5: "briefly consumed up to 44 watts ... finally settled at 30 watts"; "its gaming performance remains absolutely consistent"; fan noise in the stress test "48 dB(A)", measured at 15 cm (https://www.notebookcheck.net/Apple-MacBook-Pro-M5-2025-review-The-fastest-single-core-performance-in-the-world.1144391.0.html, 2025-10-21).
  - Average GPU power in Notebookcheck's combined test (Cinebench R23 + WLE stress): Air M5 "Ø4.56" W, MBP 14 M5 "Ø15.2" W.
- **Fans are not a guarantee** [fact], MBP 14 M5 Max: "Sustained workloads will result in some throttling, even in High Power mode with 92.6 % (74.99 % in Automatic mode)". Also: "During the 30-minute stress test of Cinebench 2024 Multi, the performance dropped by 24 %" (https://www.notebookcheck.net/M5-Max-with-inconsistent-performance-and-throttling-issues-Apple-MacBook-Pro-14-Review.1246064.0.html).

### 1.3 LLM-specific sustained runs

- **MacBook Air (any chip): no controlled llama.cpp or MLX run over many minutes found.**
  - Blogs claim the Air throttles "after ~6 minutes" or loses "15-25%", without a stated method [unverified] (https://modelfit.io/blog/best-llm-macbook-air-m4-16gb/, https://bestllmfor.com/best/macbook-air-m4-16gb/).
  - The "40% throttle" figures for the M5 Air come from low-quality sites [unverified].
- [fact] **iPhone 16 Pro, fanless, MLX, Qwen 2.5 1.5B, 20 back-to-back iterations.**
  - "loses roughly 40% of its peak throughput within three iterations".
  - Warm state "24.96 tok/s (38.4% from peak)" against a peak of 40.49 tok/s; the hot plateau is "41.5% from peak".
  - Source: arXiv 2603.23640v2, 2026-06 (https://arxiv.org/html/2603.23640v2).
  - [estimate] At roughly 30 s per iteration, the drop sets in within 1-2 minutes.
- [fact] **iPhone 17 Pro, Gemma 4 E2B.** "the GPU runtimes (MLX, LiteRT-LM) heat up and shed ~50–60% of their throughput under sustained load"; "MLX crosses the 50%-lost line within ~60 s" (https://github.com/john-rocky/apple-silicon-llm-bench, README, 600 s runs).
- [fact] **MBP 14 M3 Max 128 GB (with fan), llama.cpp decode, Qwen2.5-72B Q4_0.**
  - tg32 runs repeated with `sleep 10` between them gave 8.68, 8.60, 8.51, 5.40, 2.67, 2.37 tok/s.
  - "The max core temperature during throttling ... hovered between 60-70°C".
  - Not reproduced on M1 Pro, M2 Ultra or an M4 Mac mini (ggerganov). A maintainer: "the issue is entirely within the OS or hardware".
  - Source: https://github.com/ggml-org/llama.cpp/issues/10444 (2024-11).
- [fact] **MBP M2 Max, llama.cpp decode, Llama 3.1 8B Q4_0, `powermetrics`.**
  - "GPU HW active frequency: 1385 MHz ... <<< Initial burst", then "GPU Power: 28022 mW" (the peak sample, at 1227 MHz).
  - It "settles around" 873 MHz at "GPU Power: 17409 mW".
  - Source: the same issue, comment of 2024-11-23.
- [estimate] **What to expect for client decode on an M5 Air.**
  - After 1-5 minutes of continuous load the SoC sits at about 8-9 W.
  - Compute-bound prefill should lose roughly what the GPU stress tests lose (−18% to −25%).
  - Bandwidth-bound decode should lose less if memory clocks hold. This is not measured.
  - The iPhone data shows that fanless Apple SoCs can lose more under LLM load than 3DMark suggests.
  - Plausible sustained loss on an Air: **20-40%, starting within 1-5 minutes**. Short chat turns (bursty) mostly stay in the boost window. Confidence is low. A sustained `llama-bench` loop on an Air should be measured.

## 2. Power during prefill vs decode

### 2.1 NVIDIA (clean primary sources)

- [fact] **Splitwise** (Patel et al., ISCA 2024; DGX-A100/H100; https://arxiv.org/html/2311.18677v2):
  - "Since the the prompt phase is compute intensive, its power draw increases with batch size."
  - "the token phase is memory bound and its power draw does not vary when increasing the number of tokens to process."
  - "the token generation phase incurs almost no latency impact when power capping by over 50% (i.e., 700 to 350W)."
  - "Insight VI: While the prompt phase utilizes the power budget of the GPU efficiently, the token phase does not."
- [fact] **H200 decode** (Ma et al., arXiv 2605.11999, 2026-05-12; https://arxiv.org/html/2605.11999v1):
  - "decode draws only 137–300 W on a 700 W GPU; no cap ever triggers, because memory-bound decode saturates HBM bandwidth".
  - "Power capping ... is structurally ineffective for memory-bound LLM decode."
- **Answer for NVIDIA: yes. Decode draws clearly less than prefill**, roughly 20-43% of TDP at small batch on an H200, while prefill power rises toward TDP with batch size.
- RTX 5090 or RTX PRO 6000: no phase-split power measurement found.

### 2.2 Apple Silicon

- [fact] Apple ML Research, 2025-11-19 (https://machinelearning.apple.com/research/exploring-llms-mlx-m5):
  - "TTFT is compute-bound, while generation is memory-bandwidth-bound."
  - M5 vs M4 with MLX: "up to 4x speedup ... for time-to-first-token". Table 1 range is 3.33x-4.06x, with a 4096-token prompt on a 24 GB MBP.
  - "the M5 provides 19-27% performance boost compared to the M4, thanks to its greater memory bandwidth (120GB/s for the M4, 153GB/s for the M5, which is 28% higher)".
- **Not found:** a powermetrics, asitop or macmon measurement of the same model in prefill and in decode on any M-series chip. I checked:
  - llama.cpp discussions #4167 (280 comments) and #4297 (charts only, no numbers);
  - MLX and mlx-lm issues;
  - GitHub repos (actop, macmon, apple-silicon-llm-bench);
  - arXiv;
  - Creative Strategies;
  - Notebookcheck.
- Decode-only measurements:
  - [fact] M2 Max GPU: 28.0 W at the peak sample, settling at 17.4 W (llama.cpp issue #10444, above).
  - [fact] M4 Max, whole-system `powermetrics` over the decode window: "The ANE path draws ~half the GPU path's package power at full decode (12.7 W vs ~24.7 W)". In the table, MLX-Swift is 24.7 W and llama.cpp 24.5 W, for Gemma 4 E2B 4-bit (https://github.com/john-rocky/apple-silicon-llm-bench).
- Whole-request averages, not split by phase:
  - [fact] M4 Pro, whole system, SMC: "The system drew 21 W against 48 W with GPU 8-bit" (ANE vs GPU MLX) (https://research.macpaw.com/projects/neural-engine).
- Not used:
  - [unverified] GreenBench (arXiv 2608.28667) reports "0.47 W of CPU+GPU package power during sustained inference" on an M4 Pro. That is implausibly low.
- [estimate] **Physics argument for Apple.**
  - Prefill on the GPU is dense matmul, like a 3D stress test, so GPU power should reach its cap. Measured caps: M4 Air GPU 15.5 W peak / 8 W sustained; M5 Max GPU 72 W peak / 44 W sustained (Notebookcheck).
  - Decode at batch 1 mostly streams weights from DRAM. GPU ALU power should drop and DRAM power rise, so package power is likely lower than in prefill on actively cooled Macs.
  - On a fanless Air both phases converge to the about 8-9 W sustained SoC cap within minutes, so the difference is probably smaller there.
  - Confidence is medium for the direction and low for the size.
  - Suggested check: run `sudo powermetrics --samplers gpu_power,cpu_power -i 500` during `llama-bench -p 4096 -n 0` and then during `-p 0 -n 512`.

## 3. Base Apple chips (non-Pro) and MacBook Air M5

### 3.1 Base chips

| Chip (announced) | GPU cores | Memory bandwidth | Max RAM | GPU / AI throughput |
|---|---|---|---|---|
| M1 (2020-11-10) | 7 or 8 | 68.25 GB/s<br>[fact] Wikipedia: "the M1 SoC has 68.25 GB/s memory bandwidth"<br>[fact] Apple: M2's 100 GB/s is "50 percent more than M1" | 16 GB<br>[fact] MBA M1 specs: "8GB unified memory, Configurable to 16GB" (https://support.apple.com/en-us/111883) | [fact] "2.6 teraflops of throughput" (FP32) (https://www.apple.com/newsroom/2020/11/apple-unleashes-m1/) |
| M2 (2022-06-06) | 8 or 10 | [fact] "100GB/s of unified memory bandwidth" | [fact] "up to 24GB" (https://www.apple.com/newsroom/2022/06/apple-unveils-m2-with-breakthrough-performance-and-capabilities/) | [fact] Notebookcheck: "theoretical performance is rated at 3.6 Teraflops" (https://www.notebookcheck.net/Apple-M2-10-Core-GPU-Benchmarks-and-Specs.632306.0.html) |
| M3 (2023-10-30) | 8 or 10 | [fact] "100GB/s memory bandwidth" (https://support.apple.com/en-us/118551) | 24 GB (same page) | Apple publishes none.<br>[estimate] about 3.5-4.5 TFLOPS FP32 (10 cores × 128 ALUs × 2 × 1.4-1.75 GHz) |
| M4 (2024-05-07) | 8 or 10 | [fact] "120GB/s memory bandwidth" (https://support.apple.com/en-us/122209) | 32 GB, "24GB or 32GB" (same page) | Apple publishes no GPU figure.<br>Neural Engine: [fact] "up to 38 trillion operations per second" (https://www.apple.com/newsroom/2024/05/apple-introduces-m4-chip/) |
| **M5** (2025-10-15) | 8 or 10, "a Neural Accelerator in each core" | [fact] "153GB/s" | [fact] "32GB of memory capacity" | [fact] "over 4x peak GPU compute compared to M4, and over 6x peak GPU compute for AI performance compared to M1" (https://www.apple.com/newsroom/2025/10/apple-unleashes-m5-the-next-big-leap-in-ai-performance-for-apple-silicon/)<br>[estimate] about 15-18 TFLOPS dense FP16 matmul (see below) |
| M6 (2026-08-25, Mac mini; MBP 14 in Oct 2026; **not in MacBook Air yet**) | 12 with Neural Accelerators | [fact] "up to 170GB/s" | [fact] "up to 32GB" | [fact] "a nearly 30 percent increase in peak GPU compute for AI compared to M5, and more than 8x compared to M1" (https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/)<br>[estimate] about 19-23 TFLOPS FP16 |

- [fact] Zakharko, 2025-10-15 (https://tzakharko.github.io/apple-neural-accelerators-benchmark/):
  - Per-core rate: "1024 FLOPS per GPU core per cycle for FP16 matrix-multiply accumulate".
  - Measured on A19: "approximately 7.4 TFLOPS for the 5-core A19", at about 1460 MHz.
- [estimate] Base M5 FP16 matmul is 10 cores × 1024 × 1.46-1.75 GHz ≈ 15-18 TFLOPS. That is about 4x a pre-M5 10-core GPU, consistent with Apple's ">4x". No direct measurement on the base M5 was found.
- Apple publishes no FP16 figures for M1-M4. On those GPUs FP16 runs at about the FP32 rate; see `hardware-2026-10.md` §1.3.
- [fact] Measured PyTorch MPS matmul in FP32: M1 GPU 1.4 TFLOPS, M2 GPU 2 TFLOPS, with measured bandwidth of 56 and 90 GB/s (https://github.com/chsasank/device-benchmarks). This shows low efficiency.
- [fact] Community measurement on an M6 Mac mini 24 GB, Qwen3.8-27B Q4, MLX 0.32.2: "around 270 tok/s average prefill, 9.8 tok/s ordinary decoding" (https://github.com/ml-explore/mlx-lm/discussions/1932, 2026-09-29).
- [fact] MacBook Air M5 press release, 2026-03-03: "up to 4x faster performance for AI tasks than MacBook Air with M4, and up to 9.5x faster than MacBook Air with M1". The footnote says only "Testing was conducted by Apple in February 2026" (https://www.apple.com/newsroom/2026/03/apple-introduces-the-new-macbook-air-with-m5/).

### 3.2 MacBook Air M5: configurations and current US prices

Source: [fact] Apple store configurator API, read 2026-10-30. The API is `https://www.apple.com/shop/api/cto/update-config?collection=MBA_2026_COLLECTION&...`; `"amount"` is the configured price. The store page reads "Choose from 16GB, 24GB, or 32GB" and "Selection of 24GB memory or higher includes upgrade to M5 chip with 10-core GPU on 13-inch models."

| Model (512 GB SSD, pre-tax) | 16 GB | 24 GB | 32 GB |
|---|---|---|---|
| 13", 8-core GPU | **$1,299** (MDHE4LL/A) | n/a (24 GB forces the 10-core GPU) | n/a |
| 13", 10-core GPU | $1,399 (CTO) | **$1,499** (MGP84LL/A) | **$1,699** (CTO) |
| 15", 10-core GPU | **$1,499** (MDVH4LL/A) | **$1,699** (MGPD4LL/A) | **$1,899** (CTO) |

- SSD upgrades [fact]: 1 TB "+ $300.00", 2 TB "+ $800.00", 4 TB "+ $1,800.00".
- Maximum RAM is **32 GB** [fact].
- All configurations: "10-core CPU with 4 super cores and 6 efficiency cores", "153GB/s memory bandwidth" [fact] (https://www.apple.com/macbook-air/specs/).
- Price history [fact]:
  - Launch, 2026-03-03: "The 13-inch MacBook Air with M5 starts at $1,099"; the 15-inch started at $1,299 (Apple press release, above).
  - Late June 2026: "MacBook Air: $1,299, up from $1,099 (+$200)". Apple's statement: "The rapid expansion of AI data centers has created an extraordinary surge in demand for memory and storage" (https://www.macrumors.com/2026/06/29/apple-raised-prices-on-14-products/).

## 4. Small open models for a 16-32 GB Mac (late October 2026)

Sources:
- Release dates and sizes: HF model cards and the HF API (`createdAt`, file sizes), the Qwen GitHub news, and AA `releaseDate`.
- Index values: [fact] AA Intelligence Index **v4.1.1**, read from the JSON embedded in the Wayback snapshot of 2026-08-30 (http://web.archive.org/web/20260830213601/https://artificialanalysis.ai/models/qwen3-8-27b), field `"intelligenceIndex"`. "est" means `"intelligenceIndexIsEstimated":true`.
- The live AA index is now v5.0, which is harder. Most small models are not scored on it: Qwen3.5 9B is `null`, Qwen3.8 27B is 20.1.
- 4-bit size: sum of `.safetensors` in the `mlx-community/*-4bit` repo (HF API, 2026-10-30). Vision or audio towers are included where they ship.

| Model (release) | Type and parameters | Licence | MLX 4-bit size | AA v4.1.1 (reasoning / non-reasoning) |
|---|---|---|---|---|
| Qwen3.5-4B (2026-03-02) | dense 4.66B | Apache 2.0 | 3.03 GB | 20.4 est / 16.1 est |
| **Qwen3.5-9B** (2026-03-02) | dense 9.65B | Apache 2.0 | 5.95 GB | **21.8** / 20.6 est |
| Gemma 4 E4B (2026-04-02; AA lists 04-03) | dense, 4.5B effective, 8B with embeddings | Apache 2.0 | 5.15 GB | 12.2 est / 8.7 est |
| Gemma 4 12B (2026-06-03, AA) | dense 11.95B | Apache 2.0 | 10.99 GB | 22.2 est / 13.2 est |
| **Gemma 4 26B-A4B** (2026-04-02) | MoE 25.2B, 3.8B active | Apache 2.0 | 15.34 GB | 26.1 / 20.4 est |
| Gemma 4 31B (2026-04-02) | dense 30.7B | Apache 2.0 | 18.41 GB | 29.7 / 22.3 |
| GLM-4.7-Flash (2026-01-19) | MoE 31.2B, 3B active | MIT | 16.85 GB | 23.3 est / 15.6 est |
| Qwen3.5-35B-A3B (2026-02-24) | MoE 36B, 3B active | Apache 2.0 | 20.39 GB | 29.9 est / 24.3 |
| **Qwen3.6-35B-A3B** (2026-04-16) | MoE 36B, 3B active | Apache 2.0 | 20.40 GB | **32.1** / 24.6 |
| Qwen3.6-27B (2026-04-22) | dense 27.8B | Apache 2.0 | 16.05 GB | 37.7 / 31.3 |
| **Qwen3.8-27B** (2026-08-14) | dense 27B | Apache 2.0 | 16.05 GB | **52.0** xhigh, 44.5 medium, 42.9 low / 34.7 |
| **Muse Glimmer 30B** (Meta, 2026-08-10) | dense 29.6B, including a 1.8B vision encoder | Apache 2.0 | 19.41 GB | **35.1** (high) |
| Nemotron 3.5 Lightning 30B-A3B (2026-08-11) | MoE 30B, 3B active (AA: 31.6B / 3.6B) | OpenMDW-1.1 | 17.78 GB | 23.6 |
| gpt-oss-20b (2025-08-05) | MoE 21B, 3.6B active | Apache 2.0 | 11.18 GB (MXFP4-Q4) | 15.2 (high) |
| Nemotron 3.5 Bolt 74B-A9B-24GB (2026-10-15) | MoE 74B, 9B active, native 2-bit QAT | OpenMDW-1.1 | "24GB packed model" | not found |

Release facts [fact]:
- Qwen GitHub news (https://github.com/QwenLM/Qwen3.8):
  - "2026-03-02: Qwen3.5-9B, Qwen3.5-4B, Qwen3.5-2B, and Qwen3.5-0.8B are now available"
  - "2026-04-16: Qwen3.6-35B-A3B is now available"
  - "2026-08-14: Qwen3.8-27B is now available"
- **No Qwen3.6, 3.7 or 3.8 small dense models (<27B) exist.** The HF API for author=Qwen lists only Qwen3.6-35B-A3B and 27B, and for Qwen3.8 only 27B, 2.4T-A95B and Flash-Next. Qwen 4 is "in training" (see `models-apis-2026-10.md`).
- Gemma 4: Simon Willison, 2026-04-02: "Four new vision-capable Apache 2.0 licensed reasoning LLMs from Google DeepMind ... sized at 2B, 4B, 31B, plus a 26B-A4B Mixture-of-Experts" (https://simonwillison.net/2026/Apr/2/). The 12B came later; its card says "audio supported on E2B, E4B, and 12B" (https://huggingface.co/google/gemma-4-12B-it).
- Muse Glimmer: the HF org `meta-models` is verified, `"fullname":"Meta Inc."`. The card says "Model Release Date: August 2026", "Dense Causal Transformer", "shrinking the language model to under 20 GB ... within a 24 GB or 32 GB envelope" (https://huggingface.co/meta-models/Muse-Glimmer-30B).
- Nemotron 3.5 Bolt: "native 2-bit quantization to fit in 24GB of memory", "Hugging Face 10/15/2026" (https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB).
- Nemotron 3.5 Lightning: "Release Date | August 11, 2026" (https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16).

Which models fit [estimate]:
- macOS caps GPU-wired memory below physical RAM. [fact] mlx-lm #1932, 24 GB M6: "With the macOS GPU wired-memory limit raised to 20GB, I could use roughly 30K context".
- Rule of thumb for weights, leaving room for KV cache and the OS:
  - 16 GB Mac: up to about 9-10 GB of weights (Qwen3.5-9B, Gemma 4 E4B).
  - 24 GB: up to about 16-17 GB (Qwen3.8-27B, Gemma 4 26B-A4B).
  - 32 GB: up to about 22-24 GB (Qwen3.6-35B-A3B, Muse Glimmer, Gemma 4 31B).
- Decode ceiling on an M5 Air (153 GB/s) is about 0.8 × 153 / GB read per token:
  - dense 27B at 4-bit (about 15 GB): about 8 tok/s. This matches the 9.8 tok/s measured at 170 GB/s on the M6.
  - 3B-active MoE (about 2 GB per token): about 50-60 tok/s.
  - 9B dense (about 5.5 GB): about 20 tok/s.
  - These are before any thermal loss (§1).

## 5. NVIDIA GeForce driver licence: the datacenter clause

- [fact] **Current text.** https://www.nvidia.com/en-us/drivers/geforce-license/ (title "NVIDIA Driver License Agreement", footer "(v. February 25, 2025)", read 2026-10-30):
  - §2.8: "You agree that GeForce or Titan SOFTWARE: (i) is licensed for use only on GeForce or Titan hardware products you own, and (ii) is not licensed for datacenter deployment."
  - The generic page https://www.nvidia.com/en-us/drivers/nvidia-license/ now serves the same agreement and the same §2.8.
- [fact] **Other relevant clauses:**
  - §1.1(c): "Deploy, for your own use, the SOFTWARE on infrastructure you own or lease"
  - §2.7: "you may not ... provide commercial hosting services with the SOFTWARE"
  - §3: "You may allow employees and contractors of your entity or of your subsidiary(ies) to access and use the SOFTWARE from your secure network"
- **Offices or workstations: not mentioned.** [fact] by full-text search of the agreement text:
  - "workstation" and "personal" do not appear.
  - "office" appears only in the arbitration clause ("the nearest JAMS office").
  - "datacenter" appears once, in §2.8, and is not defined.
- **The clause covers only GeForce/Titan software.** RTX PRO drivers are not under §2.8 [fact, from its wording]. Whether an on-prem server room counts as a "datacenter" is undefined [estimate: a legal grey zone; needs counsel].
- [fact] **2025 change.** The pre-2025 "License For Customer Use of NVIDIA GeForce Software" (Wayback snapshot 2024-05-11, https://web.archive.org/web/20240511035433/https://www.nvidia.com/en-us/drivers/geforce-license/) read: "No Datacenter Deployment. The SOFTWARE is not licensed for datacenter deployment, except that blockchain processing in a datacenter is permitted." The Feb 2025 version drops the blockchain exception and adds "hardware products you own".
- **2026 change: none.** The live page is still v. February 25, 2025.

## 6. Multi-GPU workstation in an office: power, circuits, heat, noise

GPU board power [fact]:
- RTX 5090: "TGP (Total Graphics Power) ... 575 W" (https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf).
- RTX PRO 6000 Workstation Edition: 600 W; Max-Q: 300 W (https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1.0.pdf).
- See `hardware-2026-10.md` §4-5 for both.

Wall power and circuits:

| Configuration | Wall power | Circuit or PSU per the vendor | Source |
|---|---|---|---|
| 2× RTX 5090 (BIZON X5500, Threadripper) | "Idle: 200W Max Load (stress test): 1000W-1200W" | "two (2) 20 A /120V outlets (one circuit is enough)"; 2200 W PSU | [fact] https://bizon-tech.com/bizon-x5500.html |
| 2× RTX 5090 + Core Ultra 9 285K (BIZON V3000 G4) | "1300W-1450W (100% load for all the GPUs and CPUs)" | "one (1) 20 A /120V outlet with a dedicated circuit" | [fact] https://bizon-tech.com/bizon-v3000.html |
| 4× RTX 5090 + Threadripper 9995WX | "2700W-3000W" | – | [fact] BIZON X5500 page |
| 4× RTX 5090 + dual Xeon (liquid-cooled Z8000 G3) | "3200W-3700W" | up to 4500 W PSU, C19 cord | [fact] https://bizon-tech.com/bizon-z8000-g3.html |
| 4× RTX PRO 6000 Max-Q (BIZON) | – | "two (2) 20 A /120V outlets with a dedicated circuit each" | [fact] BIZON X5500 page |
| 4× RTX PRO 6000 Max-Q + TR PRO 7975WX (a16z build, 2025-08-22) | "pulls 1650W at peak" | "operable on a standard, dedicated 15A 120V outlet" | [fact] https://a16z.com/building-a16zs-personal-ai-workstation-with-four-nvidia-rtx-6000-pro-blackwell-max-q-gpus/ |
| 2× RTX 5090 or 2× RTX PRO 6000 WS, or up to 4× Max-Q (Puget T140-5U) | – | "requires a 200-240V circuit"; Super Flower 2800W PSU | [fact] https://www.pugetsystems.com/products/rackmount-workstations/amd-rackstations/t140-5u/ |
| Puget Quad GPU (4× RTX PRO 5000 or 6000 Max-Q) | – | "240V power supply ( requires 200-240V circuit )" | [fact] https://www.pugetsystems.com/solutions/ai/deploy/ |

Notes on the a16z build:
- 1650 W equals the PSU rating, so it is probably a cap, not a metered reading.
- [estimate] If 1650 W were sustained, it would exceed the 1,440 W continuous limit of a 15 A circuit.

Other vendors:
- Lambda no longer sells workstations [fact]: "Lambda has ended its on-premise hardware business ... as of August 29, 2025" (https://lambda.ai/legacy-hardware).

Circuit limits:
- [fact] NEC 210.20(A), quoted by IAEI (2016): "the rating of the overcurrent device shall not be less than the noncontinuous load plus 125 percent of the continuous load". A continuous load is "a load where the maximum current is expected to continue for 3 hours or more" (https://iaeimagazine.org/2016/may2016/100-vs-80-choosing-the-right-ocpd-solution/).
- [estimate] That gives 80% for continuous use:
  - 15 A × 120 V × 0.8 = **1,440 W** (1,800 W nameplate).
  - 20 A × 120 V × 0.8 = **1,920 W** (2,400 W nameplate).
  - 30 A/208-240 V × 0.8 ≈ 5.0-5.8 kW.
- EU: 16 A × 230 V = **3,680 W** nameplate [estimate, arithmetic].
  - A Schuko socket is commonly limited to about 10 A (2.3 kW) for multi-hour loads, per ADAC advice for EV charging [unverified] (https://v2charge.com/de/wallbox-oder-schukostecker/).
  - Not found: a primary IEC or VDE text for a continuous-load derating.

Which boxes need what [estimate]:
- 2× 600 W-class cards: about 1.4-1.8 kW at the wall. That exceeds a 15 A/120 V circuit's continuous limit and is borderline on a dedicated 20 A circuit, so a dedicated 20 A circuit or 240 V is needed. One EU 16 A circuit is fine.
- 4× 600 W-class cards: about 2.7-3.7 kW. That needs 240 V (US) or two dedicated 20 A circuits, with dual PSUs or a single 2.8-4.5 kW 200-240 V PSU. In the EU it needs a dedicated 16 A circuit, preferably with a CEE (blue industrial) socket, or two circuits.
- 4× Max-Q: about 1.6-1.9 kW. That fits one dedicated 20 A/120 V circuit only marginally; vendors specify 240 V (Puget) or two circuits (BIZON).

Heat [estimate, unit conversion]:
- 1 kW = 3,412 BTU/h.
- A 3 kW box gives about 10,200 BTU/h, close to a 1-ton (12,000 BTU/h) air conditioner's capacity, or about two 1.5 kW space heaters running continuously.

Noise [fact]:
- BIZON, measured at 1.8 m:
  - 2× RTX 5090, air-cooled GPUs: "Idle noise level: up to 43 dB ... Max load noise level (stress test): up to 55 dB"; the room was "Environment: 24 C / 75 F, 43 dB".
  - 4× RTX 5090, liquid-cooled: "up to 45 dB" idle, "up to 52 dB" under stress.
- Puget T140-5U, qualitative: "2 x RTX 5090 or 6000 Blackwell WS: Very High"; "4 x RTX PRO 6000 Blackwell Max-Q: High"; "2-3 x ... Max-Q: Moderate".
- For comparison, MBP 14 M5 under stress: 48 dB(A) at 15 cm (different distance, not comparable).

## 7. Confidential computing on NVIDIA GPUs

- [fact] NVIDIA Confidential Containers, "Supported Platforms" (version Dev, read 2026-10-30; https://docs.nvidia.com/confidential-computing/containers/dev/supported-platforms.md).
  - GPU table:
    - H100 and H200: Single-GPU.
    - H100 and H200 "Protected PCIe (PPCIe)": Multi-GPU.
    - B200 and HGX B300: Single-GPU and Multi-GPU.
    - "NVIDIA RTX Pro 6000 BSE": Single-GPU.
  - CPU table:
    - "AMD Genoa / Milan | AMD SEV-SNP".
    - "Intel Emerald Rapids (ER) / Granite Rapids (GR) | Intel TDX".
    - Host OS Ubuntu 25.10 or 26.04, kernel 6.17+.
- [fact] The NVIDIA solution page (https://www.nvidia.com/en-us/data-center/solutions/confidential-computing/) says "NVIDIA Confidential Computing on Hopper, Blackwell, and Rubin GPUs" and "at up to 98% of the performance of unsecured deployments".
- Not listed in NVIDIA's table [fact by omission]: GeForce cards, RTX PRO 6000 Workstation and Max-Q editions, GB200 and GB300. Superprotocol says TEE support for the RTX PRO 6000 Server Edition started with driver "R580 TRD1" [unverified] (https://superprotocol.com/resources/gpu-cpu-tee-requirements).

## 8. Apple Private Cloud Compute (for comparison)

[fact] Apple Security Research, "Private Cloud Compute: A new frontier for AI privacy in the cloud", June 10, 2024 (https://security.apple.com/blog/private-cloud-compute/):
- The listed requirements are "Stateless computation on personal user data", "Enforceable guarantees", "No privileged runtime access", "Non-targetability" and "Verifiable transparency".
- "personal user data sent to PCC isn't accessible to anyone other than the user — not even to Apple."
- "This data must never be available to anyone other than the user, not even to Apple staff, not even during active processing."
- "we'll take the extraordinary step of making software images of every production build of PCC publicly available for security research."

---

## Not found, and main uncertainties

1. **No measured LLM run over many minutes on any MacBook Air.**
   - The Air estimates rest on 3DMark and Cinebench loops, iPhone MLX data and one M3 Max llama.cpp issue.
   - UL stability values are medians of user submissions, not lab runs. There are no UL pages for the M3, M4 or M5 Air.
2. **No side-by-side prefill vs decode power measurement on Apple Silicon.** The NVIDIA answer is clean (Splitwise, H200 paper); the Apple direction is inferred.
3. **FP16 throughput of base chips.**
   - Apple gives only multipliers: M5 ">4x" M4; M6 "nearly 30 percent" over M5.
   - The base M5 estimate of about 15-18 TFLOPS relies on Zakharko's A19 per-core rate and an assumed clock.
   - M3 and M4 FP32 figures are not published.
4. **AA index.**
   - v4.1.1 (Aug 2026) is the last version that covers small models. v5.0 (live) mostly does not score them.
   - Several small-model values are AA estimates.
5. **Office power.**
   - Wall-power figures are vendor estimates (BIZON says "may vary +/-10%"), not independent measurements.
   - The EU continuous-load practice for Schuko sockets comes from secondary sources only.
6. **GeForce licence.** "Datacenter" is undefined. Whether an on-prem rack in an office breaches §2.8 is a legal question.
7. **Prices change.** Apple prices were read through the store API on 2026-10-30, after the June 2026 increase of $200.
