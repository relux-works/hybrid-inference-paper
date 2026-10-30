# Market and literature check for the hybrid prefill/decode paper

Date: 2026-10-30. Author: research helper agent (Claude Opus 5.5) for the `hybrid` lane.

Labels used below:
- **[fact]**: stated by the cited source; the quote is copied exactly.
- **[computed]**: arithmetic on the cited numbers.
- **[estimate]**: my inference; not stated by any source.
- **[not found]**: searched for and not located.
- **[secondary]**: from press or blog coverage, not the primary source.

Method: web search, then direct fetch of the primary pages (arXiv abstract and HTML pages, the arXiv API, official docs, Census and Eurostat data files).
- A script checked every double-quoted source string in this file against the fetched texts, after whitespace normalisation.
- Two quotes could not be checked that way. The OECD sentence comes from a search snippet, because oecd.org returned 403. The Microsoft Research venue line "ISCA | June 2024" shows on the page as "ISCA" and "June 2024" in two cells.
- A negative control with fabricated quotes was correctly flagged MISS.
- Pages that refused direct fetch (HTTP 403): usenix.org, oecd.org and openai.com/index. Where those matter, this file says so.

---

## 1. How many companies employ 5,000+ people?

### 1a. US Census SUSB, reference year 2022 (latest available)

- Latest year [fact]. The SUSB table index lists **2022** as the newest annual release, with "Page Last Revised - October 8, 2026". The 2023 table page returns 404. Index: https://www.census.gov/programs-surveys/susb/data/tables.html
- Table used [fact]: "U.S., NAICS sectors, larger employment sizes up to 20,000+". File: https://www2.census.gov/programs-surveys/susb/tables/2022/us_naicssector_large_emplsize_2022.xlsx. The file header says "Release Date: 4/10/2025" and "SOURCE: 2022 County Business Patterns and Economic Census."

All industries, by enterprise employment size [fact, from the xlsx]:

| Enterprise size | Firms | Employment |
|---|---:|---:|
| 5,000–9,999 | 1,124 | 7,786,231 |
| 10,000–19,999 | 592 | 8,139,580 |
| 20,000+ | 546 | 33,384,317 |
| **5,000+ (sum)** [computed] | **2,262** | **49,310,128** |
| All firms | 6,395,635 | 135,748,407 |

- [computed] Firms with 5,000+ employees are 0.035% of firms and hold **36.3%** of SUSB employment. Firms with 10,000+: 1,138 firms, 41.5M employees, 30.6%. Firms with 500+: 21,041 firms, 54.1%.
- Coverage caveats [fact]:
  - "SUSB provides annual statistics for U.S. business establishments with paid employees by geography, industry, and enterprise size." Government, farms, rail and some other sectors are excluded. https://www.census.gov/programs-surveys/susb/about.html
  - Size counts **US domestic employment only**: "An enterprise (or "company") is a business organization consisting of one or more domestic establishments that were specified under common ownership or control." Also: "Enterprise size designations are determined by the summed employment of all associated establishments." https://www.census.gov/programs-surveys/susb/about/glossary.html
  - [estimate] A foreign multinational with fewer than 5,000 US employees therefore falls below this class.

### 1b. EU (Eurostat)

**Large enterprises (250+ persons employed).** Eurostat SBS dataset `sbs_sc_ovw`, "Enterprise statistics by size class and NACE Rev. 2 activity (from 2021 onwards)", updated 2026-09-30. Scope: EU27_2020, NACE `B-S_X_O_S94` (industry, construction and market services, excluding public administration and membership organisations). API query: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_sc_ovw?format=JSON&lang=EN&geo=EU27_2020&nace_r2=B-S_X_O_S94&indic_sbs=ENT_NR&indic_sbs=EMP_NR

| Year | Enterprises 250+ | Persons employed 250+ | All persons employed | Share [computed] |
|---|---:|---:|---:|---:|
| 2023 | 54,256 | 59,135,669 | 162,195,544 | 36.5% |
| 2024 | 54,762 | 60,000,000 (flag `e`, estimated) | 164,521,796 | 36.5% |

- Caveat [estimate]: SBS counts national *enterprises*, not enterprise groups. One multinational appears once per country, so this is not a count of companies with 250+ staff worldwide.

**Finer than 250+: the EuroGroups Register (EGR), experimental statistics, 2024.** Dataset `egr_mne_n2sc`: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/egr_mne_n2sc?format=JSON&lang=EN&time=2024
- Definition [fact]: "The multinational enterprise group size class is based on the multinational enterprise groups worldwide employment". The top class is 1,000+. No 5,000+ class exists. Metadata: https://ec.europa.eu/eurostat/cache/metadata/en/egr_esms.htm
- Counts [fact]: multinational groups with at least one unit in EU-EFTA and **1,000+ worldwide employees**: **8,778**, all controlling countries. Of these, 5,306 are EU27-controlled and 5,817 are EU27+EFTA-controlled. All such groups, any size: 149,678.
- Employment [fact, `egr_emp`, 2024]: groups with 1,000+ employees employ 41.3M persons. All multinational groups: 49.3M, "30" % of SBS employment (flag `p`). [estimate] My reading is that the geography is the country of work.

### 1c. Global estimates

- **OECD** [fact, via search snippet; direct fetch returned 403]: "Large enterprises employ 250 or more people." This is the top OECD size class, so there is no 5,000+ count. https://www.oecd.org/en/data/indicators/enterprises-by-business-size.html
- **LinkedIn** [fact]: size codes "H | 5001-10,000 employees" and "I | 10,001+ employees". https://learn.microsoft.com/en-us/linkedin/shared/references/reference-tables/company-size-codes. **[not found]** No public count of company pages per band.
- **Orbis (Moody's/BvD) and Dun & Bradstreet:** **[not found]** No public count of 5,000+ companies.
- **CompanyData.com** [fact, commercial vendor, register-based]: "Only 7,886 companies on earth employ 10,000 people or more." The 1,000–9,999 band has 124,214 companies. Basis: "375,880,144 companies indexed · Data counted on 22 October 2026". https://companydata.com/world/
- **Global 5000 database, via BIIA, 23 Jun 2021** [fact, old, vendor]: "3,756 companies have more than 5,000 employees as we would expect with all the largest firms in the world." This counts only the 5,000 largest firms by revenue. https://www.biia.com/news-from-the-smallest-database-on-the-5000-largest-companies/
- **[estimate]** Worldwide companies with 5,000+ employees: **about 15,000**, plausible range 10,000–20,000.
  - Derivation: the US SUSB ratio of 5,000+ firms to 10,000+ firms is 2,262 / 1,138 ≈ 2.0. Applied to CompanyData's 7,886 firms with 10,000+, this gives about 15,700.
  - Uncertainties: vendor registers may count subsidiaries separately, and the US ratio may not hold abroad.

### 1d. Share of knowledge or office workers

**[not found]** None of these sources reports occupational mix (SUSB, Eurostat SBS and EGR, OECD, LinkedIn codes, CompanyData, Global 5000).

---

## 2. Apple "Minions" (idle Macs), and the Stanford "Minions"

### 2a. Apple: it exists, published October 2026

- **Title** [fact]: "Minions: A Dynamic and Distributed Virtual GPU Cloud Built on Idle Apple Silicon Devices".
- **Authors** [fact]: Jianhua Li, Yun Xing, Girisha De Silva, Ryan Flint, Kai Yuan, Sean Suchter. All are listed as "Apple, USA".
- **Sources:**
  - Apple ML Research page, "published October 2026": https://machinelearning.apple.com/research/distributed-gpu-cloud
  - Its "View publication" link points to arXiv:2610.12970: https://arxiv.org/abs/2610.12970 ("[Submitted on 9 Oct 2026]"; comments "3 pages, 1 figure, 1 table"; cs.DC, cs.LG).
- **What it does** [fact]: "a dynamic and distributed virtual GPU cloud that aggregates idle Apple Silicon GPUs across macOS devices to execute large-scale machine learning inference workloads".
  - Scheduling: "Minions adopts a pull-based execution model and intentionally avoids a centralized scheduler." Also: "This pull-based execution model accommodates the inherently intermittent availability of personal devices while enabling elastic parallelism."
  - Workloads: embeddings run through HuggingFace transformers. "For large language model (LLM) completion workloads, Minions integrates with Ollama". Inputs and outputs live in S3, metadata in PostgreSQL, and a Watchdog tracks heartbeats.
  - Results, qualitative only: "Prior to its adoption, some inference jobs experienced queue times exceeding ten hours due to limited centralized GPU availability." Also: "With Minions, tasks can often begin execution within minutes by leveraging idle macOS devices."
  - In practice: "team members may send Slack messages requesting others to temporarily run the Minion Executor".
  - Scope: inference only. "Future work will extend Minions to support distributed model training in addition to inference."
- [estimate] The paper says "personal devices", "device owners" and "team members" rather than "employees". It reports no throughput or cost numbers; Table 1 is qualitative.
- [secondary] The Register covered it on 13 Oct 2026: https://www.theregister.com/ai-and-ml/2026/10/13/apple-unleashes-a-swarm-of-mac-minions-to-share-gpu-resources-for-large-ai-tasks/5302891

### 2b. Stanford Hazy Research Minions: citation confirmed

- arXiv: **2502.15964**, "Minions: Cost-efficient Collaboration Between On-device and Cloud Language Models" ("[Submitted on 21 Feb 2025]"). Authors: Avanika Narayan, Dan Biderman, Sabri Eyuboglu, Avner May, Scott Linderman, James Zou, Christopher Ré. https://arxiv.org/abs/2502.15964
- Venue: **ICML 2025** [fact]: "Proceedings of the 42nd International Conference on Machine Learning, PMLR 267:45682-45719, 2025." The PMLR title drops the prefix: "Cost-efficient Collaboration between On-device and Cloud Language Models". https://proceedings.mlr.press/v267/narayan25a.html
- Relevance [fact]: the collaboration is via text, not KV. "Because only the local model reads the full context, this protocol achieves a 30.4x reduction in remote costs".

---

## 3. Prompt-cache retention and prices

### 3a. OpenAI extended retention (24 h, KV offloaded to GPU-local storage)

- **Date and quote** [fact]: OpenAI API changelog, entry under the headings `## November, 2025` and `### Nov 13` (Feature). The entry text starts with `Released [extended prompt cache retention](…)`. Quote: "Extended Prompt Caching works by offloading the key/value tensors to GPU-local storage when memory is full, significantly increasing the storage capacity available for caching." https://developers.openai.com/api/docs/changelog (markdown at `.md`)
- **Guide as of Dec 2025** (Wayback snapshot 2025-12-20: https://web.archive.org/web/20251220013538/https://platform.openai.com/docs/guides/prompt-caching) [fact]:
  - "Extended prompt cache retention keeps cached prefixes active for longer, up to a maximum of 24 hours."
  - "In-memory cached prefixes are only held within volatile GPU memory."
  - "Only the key/value tensors may be persisted in local storage; the original customer content, such as prompt text, is only retained in memory."
  - "Prompt cache pricing is the same for both retention policies."
- **Later changes** [fact, changelog]:
  - May 29, 2026: "For organizations without ZDR enabled, `prompt_cache_retention` now defaults to `24h` instead of `in_memory`".
  - Oct 20, 2026: "You can now choose 12-hour prompt caching in the API." Also: "12-hour cache writes cost 2.5x the input token price."
- **Current guide**, fetched 2026-10-30, https://developers.openai.com/api/docs/guides/prompt-caching [fact]:
  - Earlier models: "`in_memory`: Entries typically remain active for around 5 to 10 minutes of inactivity, up to one hour." and "`24h`: Extended retention typically keeps entries available for around 30 minutes and can retain them for up to 24 hours."
  - GPT-5.5 and 5.5 Pro: `24h` only, with no cache-write charge.
  - GPT-5.6 and later use `prompt_cache_options.ttl`: "For GPT-5.6 and later, cache writes cost 1.25× the standard, uncached input-token rate for the default 30-minute lifetime." The `"12h"` option is "2.5× the uncached input-token rate" (Responses API).
  - Reads cost 0.1× uncached input (0.05× for GPT-6.1 Sol and Terra).
  - Storage wording is now: "Prompt caching may store encrypted key/value tensors in GPU-local storage as application state." [fact] The phrase "when memory is full" no longer appears in the current guide.

### 3b. Anthropic

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching (fetched 2026-10-30) [fact].

- Lifetime: "By default, the cache has a 5-minute lifetime. The cache is refreshed for no additional cost each time the cached content is used." 1 h is optional via `"ttl": "1h"`.
- Prices:
  - "Cache write tokens with a 5-minute TTL are 1.25 times the base input tokens price."
  - "Cache write tokens with a 1-hour TTL are 2 times the base input tokens price."
  - "Cache read tokens are 0.1 times the base input tokens price (see the table footnote for per-model exceptions)."
  - Exceptions: "Cache hits and refreshes on Claude Opus 5.5 and Claude Sonnet 5.5 are priced at 0.05x the base input price." Fable 5.1 and Mythos 5.1: 0.025x.
- Examples per MTok (base / 5m write / 1h write / hit):
  - Opus 5.5: $4 / $5 / $8 / $0.20
  - Sonnet 5.5: $2 / $2.50 / $4 / $0.10
  - Haiku 4.5: $1 / $1.25 / $2 / $0.10
  - Fable 5.1: $10 / $12.50 / $20 / $0.25
- Storage: "KV cache representations and cryptographic hashes are held in memory for the cache TTL and promptly deleted after expiry." [estimate] There is no per-hour storage fee; the cost sits in the write multiplier.

### 3c. Google Gemini API

Sources [fact]: caching doc https://ai.google.dev/gemini-api/docs/generate-content/caching ("Last updated 2026-10-23 UTC") and pricing https://ai.google.dev/gemini-api/docs/pricing ("Last updated 2026-10-28 UTC").

- Implicit: "Implicit caching (automatically enabled on Gemini 2.5 and newer models, no cost saving guarantee)". Minimum prompt is 2,048 tokens for 2.5 Flash/Pro and 4,096 for Gemini 3.x and 4 Argon.
- Explicit: "Explicit caching (can be manually enabled on Gemini 3 and 2.5 models, cost saving guarantee; not supported for Gemini 4 Argon and onward)". "If not set, the TTL defaults to 1 hour." "There are no minimum or maximum bounds on the TTL."
- Paid tier, per 1M tokens:

| Model | Input | Cached input | Storage per 1M tokens per hour |
|---|---|---|---|
| Gemini 4 Argon | $2.00 (to Nov 30, 2026), then $4.00 | $0.10, then $0.20 | none: "Implicit caching only (explicit caching is not supported)." |
| Gemini 3.8 Flash | $0.75 (to Dec 31, 2026), then $1.50 | $0.075, then $0.15 | "$0.50 / 1,000,000 tokens per hour (storage price) through December 31, 2026."; $1.00 from Jan 1, 2027 |
| Gemini 3.1 Pro Preview | $2.00 (≤200k) | $0.20 (≤200k), $0.40 (>200k) | $4.50 |
| Gemini 2.5 Pro | $1.25 (≤200k) | $0.125 | $4.50 |
| Gemini 2.5 Flash | $0.30 | $0.03 | $1.00 |

- [computed] A cached read costs 10% of the input price in every row above.

---

## 4. "Мостик" (Mostik) and academic analogs

**Who, when, where** [fact unless marked]:
- Company: Mostik (https://mostik.ai). Name [fact]: "Mostik—the Russian word for bridge" (WIRED). The company's own gloss: "It is also the company's name: Mostik means “little bridge”."
- Launch post at https://mostik.ai/read-more (undated page): "Today we are coming out of stealth to say what we have been doing about that."
- WIRED, Will Knight (AI Lab newsletter), "These Russian Mathematicians Taught AI Models How to Talk to Each Other Without Using Words", datePublished **2026-09-02**: https://www.wired.com/story/russian-startup-mostik-ai-models-communication/
- People [fact, WIRED]: "Sasha Malysheva, Mostik’s CEO, told me over coffee." Also: "Stanislav Smirnov, a professor at the University of Geneva and a 2010 Fields Medalist, is Mostik’s chief scientist."
- Team [fact, site]: "There are 15 of us: 12 PhDs and a Fields Medalist." "We started four months ago." "We are backed by General Catalyst, Foundation Capital, and others."
- CEO's X post: https://x.com/aimalysheva/status/2095232794792255848. [estimate] Posted 2026-09-02 19:30 UTC, decoded from the status ID.
- Russian coverage [secondary]: dataist.ai, published 2026-09-02, "Российские математики из стартапа Mostik разработали способ связывать ИИ-модели напрямую". https://dataist.ai/news/rossiiskie-matematiki-nauchili-ii-modeli-obshchatsia-drug-s-drugom-bez-slov/

**Technical details** [fact, mostik.ai/read-more]:
- Mechanism: "One model hands its hidden states to another through a small trained bridge, and the receiving model works with them directly." Also: "No output-type text passes between them, and neither model's weights are touched."
- Models: "Our sender and receiver are GLM-5.2 (753B) and Qwen-3.5 (4B)". "So, in these experiments the large model never writes. It reads the problem, its hidden states cross the bridge, and it stops. The small model does all the generation."
- Results:
  - "With the bridge attached, the small model closes 50% of that distance, which lifts its own accuracy by 25%."
  - "Running the bridged pair costs 2.5x less compute than running such a model."
  - Against text hand-off: "improving performance by as much as 10 percentage points".
- Deployment, the mode closest to our idea: "A stronger model contributes prefill state at selected points in the workload, while a smaller model handles decoding." Also: "This allows the smaller model to run wherever suitable capacity exists, including on older or otherwise underused GPUs."
- Inconsistency in the press: WIRED says the method "allows different models to interact using the mathematical values found in their weights". The company says weights are untouched and hidden states are passed. WIRED also says: "The resulting hybrid system costs one-twentieth of the full GLM model, and its performance is exactly halfway between the two." WIRED reports an ARC-AGI 3 lead, but "They wouldn’t tell me more because they want to win the contest."
- No benchmark names, no code, and no sizes for the bridge or the transferred state appear on the site.

**Paper** **[not found]**:
- The arXiv API returned 0 hits for `all:mostik`. No ML paper by Malysheva appears, and Smirnov's 2026 arXiv paper is pure mathematics.
- The site cites only others' papers (arXiv:2604.12493, arXiv:2507.11473).

**Academic analogs** (arXiv metadata checked via the arXiv API; venue as stated in the arXiv comment unless noted):

| Work | arXiv | Venue | What it does (exact quote) |
|---|---|---|---|
| Fu, Min, Zhang, Yan, Dai, Ouyang, Wang. "Cache-to-Cache: Direct Semantic Communication Between Large Language Models" | 2510.03215 | "Published in ICLR'26" | "C2C uses a neural network to project and fuse the source model's KV-cache with that of the target model" |
| Zou, Qiu, Li, Yang, Tieu, Lu, Shen, Tong, Choi, He, Zou, Wang, Yang. "Latent Collaboration in Multi-Agent Systems" (LatentMAS) | 2511.20639 | "ICML2026 Spotlight" | "a shared latent working memory preserves and transfers each agent's internal representations and latent thoughts" |
| Dery, Yahav, Prior, Feng, Shen, Szlam. "Latent Space Communication via K-V Cache Alignment" | 2601.06123 | none stated | "we propose learning a shared representation space that aligns the k-v caches of multiple models" |
| Liu et al. "DroidSpeak: KV Cache Sharing for Cross-LLM Communication and Multi-LLM Serving" | 2411.02820 | NSDI 2026 per NVIDIA 2608.03893's references (there titled "DroidSpeak: KV cache sharing across fine-tuned model variants"); not verified on usenix.org (403) | "so long as the LLMs have the same architecture" |
| Shi, Chiesa, Maguire, Kostic. "KVComm: Enabling Efficient LLM Communication through Selective KV Sharing" | 2510.03346 | "ICLR 2026" | "enables efficient communication between LLMs through selective sharing of KV pairs" |
| Ye et al. "KVCOMM: Online Cross-context KV-cache Communication for Efficient LLM-based Multi-agent Systems" | 2510.12872 | "NeurIPS2025" | KV reuse across agents with diverging prefixes |
| Ramesh, Li. "Communicating Activations Between Language Model Agents" | 2501.14082 | "ICML 2025" | "we propose a simple technique whereby LMs communicate via activations" |
| Pham et al. "Let Models Speak Ciphers: Multiagent Debate through Embeddings" (CIPHER) | 2310.06272 | "Accepted to ICLR 2024" | communicate "through the expectation of the raw transformer output embeddings" |
| Zheng et al. "Thought Communication in Multiagent Collaboration" | 2510.20733 | "NeurIPS 2025 Spotlight" | "enables agents to interact directly mind-to-mind, akin to telepathy" |
| Du et al. "Enabling Agents to Communicate Entirely in Latent Space" (Interlat) | 2511.09149 | "Accepted to ACL 2026" | uses "the continuous last hidden states of an LLM as a representation of its thought for direct communication" |
| Liu, Pfeiffer, Wu, Xie, Szlam. "Deliberation in Latent Space via Differentiable Cache Augmentation" | 2412.17747 | none stated | "a frozen LLM can be augmented with an offline coprocessor that operates on the model's key-value (kv) cache" |
| Zhao, Li, Zhao. "IAM: Efficient Inference through Attention Mapping between Different-scale LLMs" | 2507.11953 | "ACL 2025" | "performing attention mapping between small and large LLMs" |
| Woo et al. "ICaRus: Identical Cache Reuse for Efficient Multi Model Inference" | 2603.13281 | ICLR 2026 per NVIDIA's references | "allows multiple models to share identical KV caches across all layers" |
| Woo et al. "PrefillShare: A Shared Prefill Module for KV Reuse in Multi-LLM Disaggregated Serving" | 2602.12029 | preprint | "enables sharing the prefill stage across multiple fine-tuned models in a disaggregated setting" |
| Heo et al. (NVIDIA). Cross-model KV cache transfer (see section 5) | 2608.03893 | none stated | closed-form, within-family |

---

## 5. NVIDIA arXiv:2608.03893: confirmed

- **Exact title** [fact]: "Cross-Model KV Cache Transfer in LLM Families: A Closed-Form Linear Mapping for Prefill Reuse". The short title used in the notes omits the subtitle.
- **Authors** [fact]: Taekyung Heo, Rasoul Shafipour, Ritchie Zhao, Maximilian Golub, Mohammad Mahdi Kamani, Ritika Borkar, Makesh Tarun Chandran, Pantea Zardoshti, Bita Darvish Rouhani. The HTML shows "Affiliation: NVIDIA".
- **Date and version** [fact]: "[Submitted on 4 Aug 2026]", v1, cs.LG; no venue listed. https://arxiv.org/abs/2608.03893 ; HTML: https://arxiv.org/html/2608.03893v1
- **Headline results** [fact, abstract]: "this linear mapper retains 73-98% of the receiver's standalone-prefill accuracy on four pairs, while two degrade sharply". Also: "The mapper runs 2.7-25x faster than re-prefill and remains stable across multi-turn handoff". The pairs are Qwen3 8B/14B→32B, Llama 3.1 8B→70B and Ministral 3; all are matched-KV with 8 KV heads and head dimension 128.
- **Architectures** [fact, §4.1]: "All families use dense full-attention, so every target layer receives mapped KV."
- **Limitations section** [fact, §5]:
  - "(1) Single-domain calibration. Calibration uses only FineWeb-Edu."
  - (2) The source-layer count k is selected on the reported benchmarks, with an effect of at most 2.49 pp.
  - "(3) Matched-KV is empirical." … "We do not test mismatched-KV pairs."
  - "(4) Scope. Within-family transfer over dense full-attention models. Hybrid attention and attention-recurrent architectures are out of scope."
  - Future work (5): extending to "attention-recurrent hybrids such as Nemotron 3 (Blakeman et al., 2025) that carry SSM state alongside KV is a natural next step."
- **DeltaNet:** the words DeltaNet, Mamba and "linear attention" do not occur in the HTML text. [estimate] Gated DeltaNet hybrids (e.g. Qwen3-Next/3.5-style) fall under the excluded "attention-recurrent" class. The paper excludes them by category, not by name. The secondary-source claim that the paper covers only dense full attention is **confirmed**.

---

## 6. Disaggregation citations and the closest prior work

### 6a. Server-side prefill/decode disaggregation

- **DistServe** [fact]: Zhong, Liu, Chen, Hu, Zhu, Liu, Jin, Zhang. "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving". arXiv:2401.09670; the arXiv comment reads "OSDI 2024". https://arxiv.org/abs/2401.09670
  - The USENIX PDF https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf returns HTTP 200; the HTML page returned 403.
  - Quote: "DistServe assigns prefill and decoding computation to different GPUs, hence eliminating prefill-decoding interferences."
- **Splitwise** [fact]: Patel, Choukse, Zhang, Shah, Goiri, Maleki, Bianchini. "Splitwise: Efficient generative LLM inference using phase splitting". arXiv:2311.18677.
  - Venue: **ISCA 2024** (51st), pp. 118–132, DOI 10.1109/ISCA59077.2024.00019 (Crossref). Microsoft Research page: "ISCA | June 2024", https://www.microsoft.com/en-us/research/publication/splitwise-efficient-generative-llm-inference-using-phase-splitting/
  - Quote: "With Splitwise, we propose splitting the two phases of a LLM inference request on to separate machines."
- **Mooncake** [fact]: Qin, Li, He, Zhang, Wu, Zheng, Xu. arXiv:2407.00079. v1 is dated 24 Jun 2024; v5 (8 Oct 2026) carries the title "Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving".
  - FAST '25 version: "Mooncake: Trading More Storage for Less Computation — A KVCache-centric Architecture for Serving LLM Chatbot". PDF: https://www.usenix.org/system/files/fast25-qin.pdf
  - **Best paper: confirmed.** Tsinghua says it "won the Erik Riedel Best Paper Award": https://www.tsinghua.edu.cn/en/info/1245/14138.htm. The GitHub README says: "Mooncake receives the **Best Paper Award** at **FAST 2025**!"
  - Quote: "It features a KVCache-centric disaggregated architecture that separates the prefill and decoding clusters."

### 6b. Server or cloud prefill → KV to client or edge → client decode: closest prior work

| Work | Setting | KV goes to the client? | Quote |
|---|---|---|---|
| **P/D-Device** (Jin et al., 30 authors, Huawei), arXiv:2508.09035, Aug 2025, no venue | cloud prefill and first token; device decodes | **No.** It rejects raw KV over the WAN and sends tokens and a refined prompt; the device prefills a shortened prompt | "raw KVCache is unsuitable to be transferred between cloud and devices." / "the volume of the KVCache to be transferred is considerable (often GB sizes [35, 36])." |
| **SparKV** (Liu et al., CityU Hong Kong), arXiv:2604.21231, comment "IoTJ" | cloud streams **precomputed** KV chunks to an edge device (Jetson-class) over Wi-Fi; the device computes the rest and decodes | **Yes**, but for reusable contexts, not per-turn session prefill | "We present SparKV, an adaptive KV loading framework that combines cloud-based KV streaming with on-device computation." / "fetching precomputed KV caches from Aliyun [31] over a wireless last-hop connection" |
| **CacheGen** (Liu et al.), arXiv:2310.07240, SIGCOMM'24 | KV compression and streaming over the network to the serving GPU | server side | "fetching the KV cache, which contains large tensors, over the network can cause high extra network delays" |
| **Cake** (Jin, Liu, Zhang, Mao), arXiv:2410.03065 | overlaps KV load and compute | server side | "Cake employs a bidirectional scheduling strategy that dynamically balances KV cache computation and loading" |
| **PrfaaS** (Qin et al., Moonshot AI + Tsinghua), arXiv:2604.15039, Apr 2026 | cross-datacenter remote prefill; KV over Ethernet; enabled by hybrid attention | datacenter decode, not a client | "transfers the resulting KVCache over commodity Ethernet to local PD clusters for decode" / "the KVCache transfer of a hybrid model consumes only 13% of a 100 Gbps Ethernet link." |
| **EXO Labs** blog (dated 16 Oct 2025 via Simon Willison's link post) | DGX Spark prefill → M3 Ultra Mac decode, layer-wise KV streaming, LAN | **Yes**, LAN only | "If you prefill on one device and decode on another, you must send the KV cache across the network." / "delivering 2.8× overall speedup compared to M3 Ultra alone." / "streaming the KV cache to the Mac over 10Gb Ethernet." |
| **muser** (GitHub High-Performance-AI-Lab/muser, Apache-2.0, created 2026-08-27, 1 star) | GB10 NVFP4 prefill → Mac Metal decode; authenticated KV packs; delta handoff | **Yes**, wired 10GbE LAN | "an NVIDIA GB10-class node prefills in NVFP4 and hands the KV cache to your Mac over an authenticated transport." / "Disaggregated prefill cuts time-to-first-token 3.75–4.26× versus prefilling locally on the Mac." / "a delta handoff moves **54.2851%** of the bytes" |
| **DiSCo** (Sun, Wang, Lai), arXiv:2502.11417, Findings of ACL 2025 | device–server dispatch and migration | **No**, token IDs only | "When endpoints share the same vocabulary, we transmit token IDs rather than complete token representations." |
| **EdgeFlow** (Zhang et al.), arXiv:2610.22172, "Accepted by ICDCS 2026" | KV migration between geo-distributed edge servers | server to server | "making it essential to migrate stateful KV cache to other servers for ensuring continuous service" |
| **Mostik** (section 4) | big-model prefill state → small-model decode | latent state, cross-model; no paper | see section 4 |

Links:
- P/D-Device: https://arxiv.org/abs/2508.09035
- SparKV: https://arxiv.org/abs/2604.21231
- CacheGen: https://arxiv.org/abs/2310.07240
- Cake: https://arxiv.org/abs/2410.03065
- PrfaaS: https://arxiv.org/abs/2604.15039
- EXO Labs: https://blog.exolabs.net/nvidia-dgx-spark/ (date: https://simonwillison.net/2025/Oct/16/nvidia-dgx-spark-apple-mac-studio/)
- muser: https://github.com/High-Performance-AI-Lab/muser
- DiSCo: https://aclanthology.org/2025.findings-acl.734/
- EdgeFlow: https://arxiv.org/abs/2610.22172

**Novelty assessment [estimate]:** I found no paper that does same-model server prefill with per-turn KV/state deltas shipped over a WAN to a unified-memory client that decodes, with economics by configuration. The closest neighbours are:
- P/D-Device: the same split, but it argues KV transfer is infeasible. That is a good foil, given small hybrid-model state and incremental deltas.
- SparKV: the same KV-to-device mechanism, but for precomputed reusable contexts.
- EXO and muser: Mac-decoder demos, LAN only; not peer-reviewed.
- PrfaaS: the hybrid-attention-makes-KV-transfer-cheap argument, inside datacenters.

Re-check before publication: arXiv moves fast, and the searches were bounded.

---

## Could not confirm / not found

- Worldwide count of 5,000+ companies from LinkedIn, Orbis, D&B or OECD: **not found**. Only vendor figures (CompanyData, Global 5000) and my estimate (~15k).
- Share of knowledge or office workers in any of the item-1 sources: **not found**.
- Eurostat breakdown above 1,000 employees (e.g. 5,000+): **not found**. EGR's top class is 1,000+ worldwide employees.
- A Mostik paper, benchmark names, bridge size or code: **not found**. The exact time of the X post is derived from its ID, not read from the page.
- USENIX pages (OSDI'24 DistServe, FAST'25 Mooncake) and the OECD indicator page returned HTTP 403. Venues are confirmed instead via arXiv comments, Crossref, the PDF URLs, Tsinghua and the GitHub README; the OECD quote comes from a search snippet.
- DroidSpeak's NSDI 2026 venue and ICaRus's ICLR 2026 venue come only from NVIDIA 2608.03893's reference list. Venues for 2412.17747 and 2601.06123 are not stated on arXiv.
- The Apple Minions paper gives no quantitative throughput or cost results, and its wording does not say "employees".
