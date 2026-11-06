- **OpenRouter cache and availability test, final (prototype `m3-api-cache-test`, final code `65620748`, public branch
  fast-forwarded; dev-d r15-r15m, Muse r7au-r7au8 ACCEPT).** Whole window 2026-11-03 14:39:44Z to 2026-11-04 07:22:22Z;
  both bounded phases ended normally (v1 on its $22 ceiling at 01:28:49Z, the amendment at 07:21:58Z).
  - Spend: known $29.3068, committed upper $44.9799, within the $45 cap.
  - Calls: 743 accepted; generation cross-check 742 agree, 0 mismatch, 1 unverified; largest difference $9e-10.
    Identity-refused accepted rows: 0.
  - Final report `.../hybrid-d-r15m-261104/audit-end/API-CACHE-REPORT.md`, sha256 2485e7f2...; `analysis.json`,
    2b15799b...; per-row data in `accepted-rows.json` and `call-rows.json`.
  - The study had nine study-wide stops before it ran unattended. The data are continuous, with no replay, and the
    resumed amendment cells are labelled.
  - **Measured cached fraction depends on the call cadence:**
    - v1 (multi-depth, long pauses): Qwen3.8-27B endpoints 0 to 0.757:
      - alibaba 0;
      - modelrun 0.286;
      - parasail 0.429;
      - dekallm 0.451;
      - deepinfra/bf16 0.509;
      - streamlake 0.517;
      - coreweave 0.757;
      - cloudflare 0;
      - darkbloom 0.014;
      - tenstorrent 0.141.
    - The amendment core cadence (short gaps) for GLM-5.3-flash: up to 0.998 for morph 0.997, relace 0.997,
      sail-research 0.998, gmicloud 0.998, novita/fp8 0.998 and digitalocean 0.998, but 0.094 for atlas-cloud and 0.55
      for phala/nvfp4.
    - Qwen phala, core cadence: 0.987.
  - **Availability over the whole window** (attempts include seeds and timeouts); excluded under 95%:
    - Qwen: alibaba 0.846, streamlake 0.80, phala 0.875, novita 0.452;
    - GLM: morph 0.932, relace 0.780, reka 0.474;
    - all other measured endpoints 0.969-1.
  - **1M, pooled cadence:**
    - GLM-5.3-flash 60.35 USD per 1,000 calls over 15 qualified providers, the same with or without Alibaba;
    - Qwen 1M: no qualified measured provider (unknown).
  - The report gives USD per 1,000 calls at the measured depth mix per endpoint and phase. The engine converts these to
    the paper's measured-cache API point.
