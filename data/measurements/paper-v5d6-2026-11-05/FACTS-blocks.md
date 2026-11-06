- **Paired RULER for Qwen at 128k: completion on node A with node B's exact build (IN PROGRESS from 2026-11-05 15:51Z).**
  - **Decision.** The analyst, via the owner on 11-05: finish the remainder on any free machine if the computed state
    can be brought out, otherwise wait at most a day for B.
  - **Hosts.**
    - Rows 1-226 ran on node B: Vast 58969419, RTX PRO 6000 WS, i7-11700F, Czechia.
    - The rest run on node A: Vast 58864154, RTX PRO 6000 Blackwell Server Edition, EPYC 9754, Bulgaria.
    - Same GPU chip, compute capability 12.0. Each example's three arms run on one host, so pairing is within the
      example.
  - **Transfer.** B was stopped and its GPU unavailable. Vast's instance copy moved B's run directory and its
    `build-ruler/bin` with the build stamp to A, at the same absolute paths. Checks:
    - all 225 rows saved off-node before the stop are byte-identical to the copy;
    - 226 rows and 227 frozen specs in total;
    - every binary sha256 equals B's saved 128k manifest;
    - the binaries' RUNPATH resolves only B's libraries.
    - A's own 8k/32k build was renamed to `build-ruler-a35`, unchanged.
  - **Fixes before admission**, recorded on the node:
    - The copy dropped one absolute symlink, `venv/bin/python3 -> /usr/bin/python3`. It was recreated, giving the same
      Python 3.12.3 with numpy 2.4.2 and scipy 1.17.1.
    - Services run B's binaries as built (`--skip-build`). Each started with the build stamp listing exactly the
      binaries B recorded for that service (node: libraries plus `llama-hybrid-prefill`; clients: libraries plus the
      three client targets). The lists were taken from B's manifest and each hash was checked against the file. B's
      original stamp is kept.
  - **Attempts.**
    - Attempt 1 stopped on the missing interpreter link.
    - Attempt 2 was refused by the evaluator's whole-manifest check, because of the per-service binary lists.
    - Both stopped before any example. The saved manifest, the 226 rows and the pending sessions were verified
      unchanged.
    - Attempt 3 was admitted. Row 227 (`niah_multiquery` 17/30) was written at about 15:58Z.
  - **Estimate.** About 300 s per example, so roughly 13.6 h for the remaining 163.
  - **Paper.** Disclose the host change, and that the registered analysis runs on the complete 390.

- **Paired RULER for Qwen at 64k, COMPLETE (node A, Vast 58864154, RTX PRO 6000 Server, 2026-11-05).**
  This supersedes the 64k rows of the INTERIM block below; 128k stays interim.
  - **Run.** 390/390 examples: 13 tasks × 30, seed 261102, evaluator `18d3f114`, input lock f42a48cc.
  - **Resume.**
    - 369 rows were saved before the owner-ordered stop of 11-04. The remaining 21 ran after a resume on the same node
      at 13:45-14:28Z: the same build-r64 binaries, model and flags, with services restarted into new state
      directories.
    - The evaluator admits a resume only if the whole manifest (binary hashes, model, flags, data, packages, sources)
      equals the saved one. It released the 3 pending sessions and validated every frozen spec digest.
    - The saved manifest and all 369 saved rows were verified byte-unchanged after completion.
    - Archive `complete.tar.gz` sha256 012c9308...; local download bundle `r64-complete.tgz` e8d8acfa...
  - **Scores.** The RULER score is 97.18% in all three arms (local, offload, partition), with accuracy McNemar p = 1.
    By task:
    - qa_2: 66.67%;
    - qa_1: 96.67%;
    - every other task: 100%.
  - **Changed answers against local** (outer-whitespace equality), per the pre-registered analysis:
    - offload 28/390 = 7.18%, Wilson [5.01, 10.18];
    - partition 32/390 = 8.21%, Wilson [5.87, 11.35];
    - offload only 12, partition only 16; McNemar p = 0.5716, two-sided exact, unadjusted.
  - **Excess of offload over partition:** −1.03 pp, conservative 95% interval [−5.51, +3.49] pp.
    - Strict «no more changes than partition» (upper bound ≤ 0): not established.
    - Equivalence at the ±2 pp margin: not established. That margin was fixed after the 8k/32k results; the paper
      discloses this.
  - **Holm across the four registered depths** stays pending until 128k completes. At p = 0.57, 64k cannot reject in
    any case.
  - **Statement:** at 64k, offload gives the same RULER score as local and the partition control. It changes answer
    text no more often than the partition control does, as a point estimate. n = 390 cannot establish equivalence
    within ±2 pp.

  - **The Mac's logit gate at 524,288, first canonical attempt** (kit 1.6.12 `7ca3c4f8`, incident lane, 2026-11-03
    22:14-22:15Z, warm, slots on LaCie).
    - Restore 20.506 s; 64-position probe 16.647 s.
    - Gate refused on one bound: max |Δlogit| 1.08298 at position 55, bound 1.0. The rest passed: max KL 0.0017539
      (bound 0.01), mean KL 0.00032912, top-1 64/64 (bound 0.95).
    - Memory: whole child +332 pageouts (5,439,488 B), 0 swapouts, within the 64 MiB bound.
    - No decode, delta or 1,040,000 child ran.
    - Lane decision (NOTES, ~22:20Z): the raw-logit bound becomes 4.0. KL and top-1 are unchanged, and the first
      attempt stays in the record.
    - For comparison, CUDA against Metal at 109,591: max |Δlogit| 0.2097.
  - **The Mac's direct 512k and 1.04M measurement, complete** (kit 1.6.12 `7ca3c4f8` step 56, verified handoff;
    owner's M3 Max 128 GB at normal priority, warm, no purge; slots and references read from LaCie, model internal;
    incident lane, started 22:33Z, completed about 00:39Z on 2026-11-04; root review ACCEPT).
    - Strict archive 1,069,117 B, sha256 90723f8c...be43, with the incident lane. All per-child restore times and raw VM
      snapshots are in `PAPER-NUMBERS-AND-PER-CHILD-MEMORY.json`.
    - The raw-logit bound was 4.0. It was raised from 1.0 after the first attempt refused at 524,288 (block above). Both
      attempts must be stated; 4.0 is not a calibrated bound.
    - Each delta shape is one excluded warm-up plus three timed rounds, with medians. Every round first restores the
      original slot. The prefill seconds exclude the restore. Decode is 255 steps after the seed. Server TTFT is not
      available on the native path.

    | Metric | 524,288 | 1,040,000 |
    |---|---|---|
    | Restore before the probe, s | 20.523 | 40.465 |
    | Restore before a timed decode round, median s | 2.965 | 40.479 |
    | Gate: max KL / mean KL, nats | 0.0017539 / 0.00032912 | 0.0021309 / 0.00032571 |
    | Gate: top-1 / max abs logit difference | 64/64 / 1.08298 | 63/64 / 3.01402 |
    | Decode, median tok/s | 3.8409 | 1.6638 |
    | Δ690 prefill, median | 48.255 s, 14.299 tok/s | 72.408 s, 9.5293 tok/s |
    | Δ2000 prefill, median | 161.768 s, 12.363 tok/s | 296.966 s, 6.7348 tok/s |
    | Δ10000 prefill, median | 843.260 s, 11.859 tok/s | refused: 1,050,000 > 1,048,576 |

    - At 524,288 the later restores are faster than the first (2.97 s against 20.5 s): the 18.4 GB file stays in the OS
      cache. At 1.04M every restore takes about 40.5 s: the 36.4 GB file does not stay cached next to the wired model
      and KV.
    - Memory: all 30 native children stayed within the bound, the largest at 1,064 pages. Total pageouts were 7,755
      pages (127,057,920 B). Swapouts were 0.
    - Against engine run 22's estimates for the M3 Max at 1M (`link_thresholds.csv`):
      - the local Δ690 prefill was 70.53 s by the anchored FLOP-efficiency extension, and 120 s in the analyst's
        sensitivity; measured 72.408 s at 1,040,000, 2.7% above the anchored value;
      - the Mac import was 34.94 s, an extrapolated depth slope; the measured restore is 40.47 s, from LaCie.
      - Engine run 23 replaces both estimates with these measurements.

- **Apple M3 Max 128 GB, Qwen client decode batching by depth, capped step 55 (Mac kit 1.6.13 `4555ba33`, Muse r7aw
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

- **The owner's call logs priced by model class (paper repository `paper/data/year-bill-summary.json`, computed by
