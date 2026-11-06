- **Engine run 24 (dev-e r18, `engine-r24` `ca7f228a`, parent `9064701a`; Muse r5x6 ACCEPT, 2026-11-05 ~10:21Z).**
  Report `calc/ENGINE-REPORT-R24-261105.md`. Suites: engine 562, kit 24, audits and manifest exit 0. The 1,046 historical
  files are byte-identical.
  - **Measured-cache API point,** USD per 1,000 calls on the paper's combined call-shape means:
    - Qwen v1 (long pauses): cheapest Ionstream 3.604, one warm observation, labelled descriptive; median DeepInfra 12.550;
    - Qwen amendment core: no qualified measured point;
    - GLM v1: cheapest OpenInference 3.008, median Phala 7.830;
    - GLM core: cheapest GMICloud 2.021, median CoreWeave 4.539.
    - These are partial priceable cohorts (Qwen v1 11 priceable of 15 admitted; GLM v1 15 of 33; GLM core 10 of 33), not
      global cheapest claims. Measured hit fractions are transferred to the paper's workload as an assumption.
  - **Admission:** whole-window availability under 95% excludes every attempted endpoint. Endpoints the test never
    attempted keep the labelled snapshot basis.
  - **Crossings at the measured point** (bought office PRO 6000, owned M5 Max, bf16, s = 20%, the combined profile):
    - median API, Qwen v1, heavy load: from 5 people (45 at the 98.1% point);
    - light and medium: none;
    - cheapest API: never at any load.
    - Rented PRO, heavy: from 443 (combined) and 60 (Claude), where before there was none.
    - Bought, Claude profile: 30 becomes 5, with the zero-offload caveat.
  - **1M:** GLM 60.354821 USD per 1,000 calls over 15 qualified providers, with or without Alibaba. Qwen 1M has no
    qualified measured provider; measured but not admitted per the OpenRouter block.
  - The no-cache and 98.1% points and run 23's headlines are unchanged.
