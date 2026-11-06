# Review: engine run 23 — Muse reviewer (run hybrid-rev-r5x5-engine-r23-261104)

- Candidate: `engine-r23` head `9064701a9a07bd2726f76cefb6a05aa6aa428c0d`, parent `9053089e` (run 22, accepted r5x4). Range reviewed: `9053089e..9064701a`.
- Producer run: hybrid-e-r17. Producer checkout read-only: `~/Werkstatt/hybrid-calc/paper`. Review clone at exact head, deleted after review.
- Commit signature: `G` (good ED25519, reluxbot), trailer `Co-authored-by: Codex gpt-6.1-sol <noreply@openai.com>` present.
- Brief read in full; FACTS blocks «Mac direct 512k/1.04M», «vLLM decode batching PRO 6000», «Engine run 22» read in full.

## Verdict: ACCEPT (bound to `9064701a`)

## Findings

```json
[]
```

No blocking finding reproduced. Every row below was attacked through the engine's public entry points or recomputed independently from the published CSVs; `held` means only that the named attacks did not reproduce.

| Row | Result | Evidence |
|---|---|---|
| Mac 1M inputs & labels | held | §1 |
| PRO 6000 measured decode & interpolation | held | §2 |
| PRO 1M impossibility | held | §3 |
| Changed/unchanged vs run 22 | held | §4 |
| Gates (suites, audits, byte-identity, mutants) | held | §5 |

### Notes (non-blocking)

- `note` — The review prompt §2 lists the 16k aggregate as 37.93; FACTS, the receipt and the engine all carry 737.93 at N=39. The engine matches FACTS; the prompt figure is a dropped digit.
- `note` — `link_thresholds.import_s` carries the 40.479 s proxy value; the proxy nature is in `recovery_kind=full_slot_restore_proxy`, `rate_basis` («NOT measured delta import») and the report. A consumer reading only the `import_s` column name could still mislabel it downstream; the paper text must keep the proxy wording (report does).
- `note` — PRO decode between 256k and the physical capacity limit returns the labelled bandwidth model (e.g. 512k/900k, 1 slot); 999,999 already refuses physically (`run20.capacity`), ≥1,000,000 refuses with the measured 61.97 > 56.62 GiB reason. This matches the brief («beyond 256k modelled», «1M impossible»); no export presents a ≥1M PRO row as feasible.
- `note` — Two of the four mutants (`admit_pro_million`, `hide_zero_offload`) are gate deletions; acceptance does not rest on them — §2/§3 attacks exercised the real gates directly.

## §1 Mac 1M inputs

- Measured Δ690 72.408 s at 1,040,000 replaces the 70.529 s estimate; Δ2000 296.966 s; Δ10000 refused (1,050,000 > 1,048,576), 60 threshold rows for that shape: 0 feasible, 0 with a local prefill. 512k rows match FACTS exactly (48.255 / 161.768 / 843.260 s, decode 3.8409; 1.04M decode 1.6638).
- The 40.479 s warm full-slot LaCie restore is charged once as `full_slot_restore_proxy`, never as a measured delta import: `rate_basis` states «NOT measured delta import or end-to-end hybrid» on all 780 proxy rows; report §«M3 Max million-context routing» and `run23/README.md` say the same. M5 rows keep the `delta_import_fit` estimate (34.937 s) and estimated local time — no M3 value leaked into M5 economics.
- Labels present on every direct row: `warm_no_purge`, external LaCie SSD, normal priority, raw-logit bound 4.0 with earlier bound 1.0 and the 524,288 refusal (max |Δlogit| 1.08298) disclosed; bound 4.0 marked not calibrated. `inputs.mac_rows()` refuses rows lacking any of these.
- Thresholds recomputed independently (`wire = Δ·34816 + state`, bf16 78,446,592 B / f32 156,893,184 B; `budget = local − server_prefill − recovery − RTT`; `threshold = wire/budget`), B300 FP8-KV server as the report states:
  - nominal 1M (explicit 1.04M proxy, `measurement_depth=1040000`, never renamed): bf16 102,469,632 B / 30.580 s = **3.351**; f32 180,916,224 B / 30.580 s = **5.916**.
  - at 1,040,000: bf16 **3.356**; f32 **5.925**.
  - 120 s sensitivity (`primary=False` on all 120 such rows): bf16 **1.311**; f32 **2.314**.
  All match the report to the printed digits; all 1,690 finite threshold rows in the CSV recompute with 0 mismatches. Offload verdicts at 5.19 MB/s follow (bf16 remote 61.62 s < 72.408 s → offload; f32 76.73 s → local).

## §2 PRO 6000 server decode

- All 11 receipt medians are the middle of their three rounds and equal `server_decode.csv` digit-for-digit: 16k 48.705/302.600/686.817/737.934 (N=1/8/32/39), 64k 44.464/190.289/225.350 (1/8/12), 164k 38.105/84.222 (1/5), 256k 33.067/57.730 (1/3), resident limits 39/12/5/3.
- Named negative attacked through `Server.decode()`: every exact depth/stream point returns the measured aggregate (0 mismatches), basis «measured PRO depth/streams point». Over-request (16k, N=1000) caps at batch 39 with the measured aggregate — batch disclosed, no invented throughput.
- Interpolation stated in report, README and code: seconds per sequence-token across batch, equal resident-batch fraction `(N−1)/(limit−1)` across depths, reciprocal resident-count capacity rounded down and bounded by physical memory. Probes: 100k/N=4 → 107.15 tok/s, 8 slots, basis «interpolated … not a direct measurement»; slots monotone 39/18/12/8/5/3/3 at 16k/40k/64k/100k/164k/200k/256k.
- Beyond 256k basis is «modelled bandwidth … outside PRO 16384–256000 measured surface»; B300 basis «modelled bandwidth … B300 decode pending: rental failed to start 2026-11-04T00:36Z» at every depth probed. B300 never reuses the PRO curve.

## §3 PRO 1M row

Impossible and never feasible: `require_capacity()` raises `InputGap` (61.97 GiB needed > 56.62 GiB available, FP8 KV unavailable on SM 12.0) from `decode`, `slots`, `cold`, and `cached` (999,310+690 refused via depth+delta). In `link_thresholds.csv` all 180 PRO rows at depth 1,000,000/1,040,000 have `feasible=False`, 0 slots, no finite remote time or threshold. `full_resync` llama.cpp rows are renamed `historical_llama_pro6000_slot_builder` with `feasible_server_scenario=False`.

## §4 What changed

- Abstract-bound ledger: 377 coordinates, 39 changed — verified cell-by-cell against the actual run22/run23 CSVs (377/377 match, including every «unchanged»).
- Crossings: independently diffing run22 vs run23 `team_break_even.csv` on semantic keys gives exactly 14 changed statements (28 cells), matching `change_summary.csv`. The claude_deep rented-WAN light own-cluster crossing is 87 → 73 in all four transport/client arms; the remaining 10 are physical-extended light rows (20 → 13, 493 → 485).
- Bought-office headlines unchanged, verified in both runs' files: existing_combined own cluster never (light) / 5 (medium) / 2 (heavy); median API (owner 98.1%) heavy 45; cheapest API never at every load.
- Spot-checks beyond the crossings: one changed cell in each of 11 tables (small_team_cost, main_economics, dedicated/shared multiples, idleness, link_thresholds, decode_scaling, server_decode_measured, decode_ceiling, heavy_sensitivity) matched the ledger against both files; all 19,359 changed cells are ledgered with reasons.

## §5 Gates (rerun in the review clone, `TMPDIR` inside the clone, CPU only)

- Engine suite: **543 tests, OK** (609.5 s). Kit suite (`bench/tests`): **24 tests, OK**.
- `calc/run23/export.py --audit-only` exit 0 (`historical_files: 1014, new_files: 32, quote_cells: 576093`); `calc/r23_report.py --audit-only` exit 0 (1,417 report quotes); audits left the tree clean.
- Byte-identity: `git ls-tree 9053089e calc/out` = 1,014 files; `git diff 9053089e..9064701a -- calc/out` touches nothing outside `calc/out/run23/`; only modified (not added) files are `MANIFEST.sha256`, `README.md`, `calc/README.md`. `sha256sum -c MANIFEST.sha256` exit 0 (1,919 entries).
- Mutants via `calc/run23/controls.py`: control exit 0; `use_model_at_measurement`, `admit_pro_million`, `double_restore`, `hide_zero_offload` each exit 1 on their named assertion (`model used at measured point`; `InputGap not raised`; `112.887 != 72.408`; zero-offload disclosure) — no survivors, no setup errors.
- Free disk stayed ≥29 GiB throughout (floor 28 GiB).
