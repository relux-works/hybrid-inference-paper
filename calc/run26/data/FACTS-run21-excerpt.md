- **Engine run 21 (dev-e r13, `engine-r21` `3bc58752`, parent run 20 `b6ac5abc`; Muse r5z ACCEPT).** Report
  `calc/ENGINE-REPORT-R21-261103.md`, outputs `calc/out/run21/`, in `~/Werkstatt/hybrid-calc/paper`.
  - The labelling fixes, the paper exports without the 5090 server (`calc/out/run{20,21}/paper/`) and the
    self-contained sentences are accepted at `b6316e8a` (dev-e r14 and r15; Muse r5x2, then r5x3 ACCEPT). Both
    `engine-r20` and `engine-r21` point to that head.
  - Every exported sentence names the server, its billing and link, the client, s, the cache allowance, the load and
    the coverage. The canonical sentences run 879-1,239 characters and suit tables. r5x3 proposes a generated 66-word
    short form for running text.
  - **Deep workload profile (Claude Code).** Context depth in tokens: median 212,311, p75 431,845, p90 720,173, p99
    940,755, mean 307,858. Pause between calls: median 8.1 s, p90 60.6 s. The logs hold aggregates, so the joint
    workload is a reconstruction with stated limits. The 39,904 seeded calls of the main profile are unchanged.
  - **1M scenario, a 690-token turn on a 1M context:** the offload payload is 180.916 MB.
    - Minimum link rate for the offload to pay, M3 Max client with a B300 FP8-KV server: 5.283 MB/s by extrapolation
      from measured anchors, 2.161 MB/s with the analyst's estimate of 120 s for the local turn. An M5 client needs
      44.888 MB/s.
    - At 5.19 MB/s the turn stays local in the first case and offloads in the second; 0.8 MB/s never pays; 2.8 MB/s pays
      only in the analyst case.
    - M3 Max decode at 1.04M: a bandwidth ceiling of 7.415 tok/s against the only measurement, 1.67 tok/s, taken at
      background priority. The gap is open until the Mac slot run.
  - **Office scenario**, 50 people, two 1M tasks a day each, in USD per person-month:
    - Qwen with FP8 KV: hybrid 1,692.60, own cluster 1,348.06.
    - GLM with a new Mac Studio: 456.65 against 674.03. This is a projection: GLM is unmeasured, needs two B300 per
      replica, and has no admitted API.
  - **1M APIs:** Phala is the cheapest admitted at 54.715 USD per 1,000 calls and Novita the median at 93.581. Alibaba
    is excluded for availability, 87.46%.
  - **Run-20 findings:** F1 (coverage provenance) and F2 (missing availability windows) are fixed in new publications,
    and the old bytes stay frozen. The 5090 server rows are excluded; the 5090 client rows remain.

