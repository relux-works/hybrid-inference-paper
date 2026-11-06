- **Engine run 22 (dev-e r16 with capacity retries, `engine-r22` `9053089e`, parent `b6316e8a`; Muse r5x4 ACCEPT,
  2026-11-03 ~21:15Z).** Report `calc/ENGINE-REPORT-R22-261103.md`, outputs `calc/out/run22/paper/`. Suites: engine 523,
  kit 24, report, manifest and audits exit 0; 987 historical files byte-identical. The reviewer recomputed every
  abstract-bound number.
  - **Policy.**
    - bf16 recurrent transport is the default: 78,446,592 B. f32 is the control.
    - **The primary basis is a dedicated team server:** a bought office RTX PRO 6000 with vLLM FP8, 125 MB/s at
      RTT 1 ms.
      - Bought-server inputs: capex $30k, 4 years, 20% residual, 2% support, 0.9 kW.
      - The client is an owned M5 Max 64 GB at PRI 31; s = 20%.
      - Cache: the owner's 98.1% allowance, with 1.9% of misses billed; per provider it is unverified.
    - The combined measured-shape subset is 10,885 / 39,904 calls (27.28%), normalized to 840 / 3,360 / 10,500 calls per
      person-month. Light and medium are typical; heavy, 2,500 calls a day, is the owner's own intensity.
    - **The M3 Max has no economics rows.** Run 22's economics use the owned M5 Max.
  - **Team of 50, existing combined profile.** Columns: dedicated hybrid $/person-month; service / calendar occupancy;
    median API / dedicated hybrid; shared-work hybrid; median API / shared hybrid.

    | Load | Values |
    |---|---|
    | light | 56.64 / 3.61% / 0.83% / 0.088 / 15.90 / 0.313 |
    | medium | 56.64 / 14.46% / 3.33% / 0.351 / 21.29 / 0.934 |
    | heavy | 56.64 / 45.17% / 10.40% / 1.097 / 36.53 / 1.701 |

    - The $56.64 is 4 x 614.0575 / 50 + 2.52 + 5.
    - The run-21 idleness example (1.462 shared against 0.526 dedicated) is superseded: heavy is now 1.701 against
      1.097.
    - The claude_deep profile never offloads: occupancy 0.00%. Its crossings are local-only results, and the paper
      must say so.
  - **Crossings through 500 people,** sustained, combined profile; the same for the bought office server and the rented
    WAN server (112.5 MB/s, 400 ms), except where noted:
    - **Own vLLM cluster** on the same server and billing basis:
      - light: never;
      - medium: from 5 people (at 3 people the own cluster is cheaper, 204.69 against 212.21);
      - heavy: from 2 people.
    - **Median admitted API** (deepinfra/bf16 at the 98.1% point): light and medium never; heavy from 45 people on the
      office server, never on the rented WAN server.
    - **Cheapest admitted API** (chutes/fp8 at the 98.1% point): never.
      - At team 50 its cost relative to the hybrid is 0.018 / 0.072 / 0.225 dedicated, so the hybrid costs 55 / 14 / 4.4
        times more.
      - On the shared basis it is 0.064 / 0.191 / 0.349.
      - At the no-cache point the cheapest is darkbloom/fp4, and the hybrid is cheaper at heavy load from 74 people.
        Every cheapest-API sentence must name its cache point.
  - **Small dedicated teams,** hybrid against own cluster in $ per person-month:
    - light: 3 people 212.21 / 204.69; 5 people 130.33 / 122.81; 10 and 20 people 68.93 / 61.41;
    - medium: 5 people 130.33 / 245.62;
    - heavy: 3 people 212.21 / 409.37.
    The light-load gap of 7.52 at every size is the per-person part of the hybrid (2.52 + 5).
  - **A bought Mac** (a new M5 Max 64 GB) adds $69.05 per person-month, so team 50 costs $125.69.
    - Own-cluster medium crossing: 5 becomes 34 people. Heavy stays at 2.
    - Median-API heavy crossing: 45 becomes never.
    - The case depends on already owning suitable Macs.
  - **API points, main measured shape,** $ per 1,000 calls:
    - no cache: cheapest darkbloom/fp4 5.505, median tenstorrent/fp4 19.519;
    - owner 98.1%: cheapest chutes/fp8 1.213, median deepinfra/bf16 5.917;
    - measured cache rate: pending (OpenRouter test).
    - Admission excludes only context impossibility, no declared cache, or availability under 95% in the chosen window.
  - **1M APIs at the 98.1% allowance:**
    - snapshot 1d: cheapest Phala 54.715, median Novita 93.581;
    - the analyst's 72 h window with Alibaba: Novita 93.581, Alibaba 95.351;
    - without Alibaba: Novita 93.581.
  - **1M routing,** M3 Max (the M5 Max's anchored budget is non-positive), Δ690, B300 FP8 with FP8 KV, home Wi-Fi
    5.19 MB/s:
    - bf16 anchored threshold 2.992 MB/s (wire 102.470 MB, 19.744 s);
    - bf16 with the 120 s estimate: 1.224;
    - f32 control: 5.283 anchored, 2.161 with 120 s.
    The local 1M rate and the Mac import-depth slope remain estimates until the direct Mac measurement.
  - **Thresholds at 100k, Δ2343, office RTT 1 ms, bf16:**
    - PRO 6000: M3 Max 5.305 MB/s, M5 Max 34.475 MB/s;
    - B300, both KV variants: M3 Max 5.227 MB/s, M5 Max 31.423 MB/s.
  - **The measured PRO 6000 decode at 16k** (x15.15 at 39) changes no economics row. Decode stays modelled.
