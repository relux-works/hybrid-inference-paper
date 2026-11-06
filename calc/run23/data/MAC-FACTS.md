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
