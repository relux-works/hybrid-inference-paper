# Paper v5c: accepted run 23 and completed night measurements

Base: signed paper `241a8616515ff880c1da81c9a9810279f370ae0d`, accepted by Muse r5y4.
Accepted engine: `9064701a9a07bd2726f76cefb6a05aa6aa428c0d`, Muse r5x5 ACCEPT.
A signed local merge preserves every accepted engine source/output byte and every earlier result.
No cut for length, title/authors/version unchanged. The original 26 R20 sites remain resolved in the
immutable v5b migration map; current quotations use run 23. No new hardware run is performed here.

## Changed coordinates and sources

The complete 377-coordinate old/new/source inventory, including all 39 changed cells, is
`calc/out/run23/abstract_bound_changes.csv`; its conditions and report address are in
`calc/ENGINE-REPORT-R23-261104.md`, section "Changed against run22".
`changed_against_run22.csv` covers the full matrices; `change_summary.csv` distinguishes additions/removals.
The full ledger is retained without cherry-picking the unchanged bought-office headlines.

| Paper coordinate | Old | New | Source |
|---|---|---|---|
| M3 nominal 1M Δ690 bf16 threshold | 2.992 MB/s | 3.351 MB/s | run23 link_thresholds, nominal depth 1000000, actual observation 1040000 |
| Same f32 control | 5.283 | 5.916 | same coordinate, f32 |
| Actual depth 1040000 bf16 / f32 | estimated anchors | 3.356 / 5.925 | run23 link_thresholds, measured local time with full-slot recovery proxy |
| 120-second sensitivity bf16 / f32 | 1.224 / 2.161 | 1.311 / 2.314 | run23 link_thresholds, primary=False |
| M3 local Δ690 prefill | 70.529 s estimate at nominal 1M | 72.408 s measured at 1040000 | mac_direct_measurements, 2.7% rounded difference; depths explicitly distinct |
| M3 recovery charge | 34.937 s extrapolated delta import | 40.479 s warm full-slot LaCie proxy | recovery_kind=full_slot_restore_proxy; never measured delta import |
| M3 deep decode | 1.67 background | 1.6638 normal priority at 1040000 | decode_ceiling and direct Mac rows |
| PRO at 64000/request32 | batch14, gain4.99 | batch12, gain5.06 | decode_scaling; interpolated, not measured at64000 |
| PRO at164000/request32 | gain2.32 | gain2.21, batch5 | decode_scaling, exact measured depth/batch |
| Own-cluster medium50 service/calendar | 66.47/15.30% | 66.46/15.29% | paper/main_economics, existing_combined, measured_ladder, bf16, s=.2, owned M5, bought PRO |
| Own-cluster heavy50 and generation sensitivity | 66.87/15.39% | 66.61/15.33% | same primary row and heavy_sensitivity |
| Own-cluster light3 service/calendar | 10.13/2.33% | 10.12/2.33% | paper/small_team_cost, same selection |
| Own-cluster medium5 service/calendar | 32.17/7.40% | 32.12/7.39% | paper/small_team_cost, same selection |
| Claude light rented-WAN own-cluster crossing | 87 | 73 through500 | paper/team_break_even, local-only zero offload, owned M5, s=.2, bf16 |

Costs and bought-office headline crossings are unchanged on their selected coordinates. Capacity refusal at
PRO vLLM 1M is explicit:61.97 GiB required,56.62 available. The historical llama.cpp slot builder is a
separate engine/format. No M3 timing is transplanted into M5 economics. API admission and cache points are
unchanged, provider measured cache and common-window availability still pending.

## Completed measurement scope

The full named FACTS blocks and evidence pointers are archived in
`data/measurements/paper-v5c-2026-11-04/FACTS-excerpts.md` with SHA custody.
- Direct Mac: full two-depth restore/gate/decode/Δ690/2000/10000 table. Warm external LaCie, no purge;
  first restore is not cold. One warm-up excluded, three timed rounds; restore excluded from prefill.
  Initial bound1 refusal at max raw difference1.08298 retained. Raised bound4 accepted later, not calibrated;
  1040000+10000 is refused_context, not a fabricated measured zero. Full hybrid TTFT and delta import unmeasured.
- Same-GPU descriptive depth quality: five cases, each4096 teacher-forced positions and16 needles;
  offload/local meanKL0, top1=1, max raw difference0. All five partition controls remain printed.
  No network/cross-device/all-depth equivalence claim; full f32 document logits were not retained.
- PRO vLLM kit1.6.11: private independent contexts, median3 common decode spans, SSE chunk receipt timing.
  Gain15.15/5.07/2.21/1.75 at16384/65536/164000/256000, resident39/12/5/3.
  Equal resident-fraction and seconds/token interpolation are assumptions, outside range modelled.
  B300 remains modelled after failed rental. Earlier kit1.6.9 rows remain labelled historical measured results.
- Bridge16k components: loopback CUDA client; medians need not sum to the full TTFT median.
  CUDA import does not substitute for Metal recovery; aggregate bridge envelope is not added twice.
- Existing server fill, warm restore and useful Mac download results retained intact.

## Pending inventory

Every remaining macro and its authority is in `calc/tests/data/paper-v5c-pending.json`;
current line addresses are generated into the task delivery receipt. Named active waits:
Qwen RULER64k/128k plus their primary analysis (expected2026-11-04 around08:30/22:30Z), measured OpenRouter cache
and common availability window/mismatch handling, M3 step55 parallel curve and engine anchor replacement,
Gemma ordinary priority, Qwen bf16 GPU rehearsal and Mac bf16 follow-up, heterogeneous CUDA/Metal/BF16 calibration,
timing-only spans without synchronous evidence instrumentation, B300 decode, vLLM bridge calibration and Bonsai ladder.
The release data cut-off stays2026-11-05 12:00Z. No completed Mac/PRO/depth-quality result remains inside a pending macro.
The cache-study methods/restarts and mismatch accounting wait for its accepted result, as authorized in this brief.

## Controls and finite coverage

All previous reviewer test method names remain. Native engine sources and tests are unmodified.
Current semantic views are successors; previous measurement archives and all original exports stay byte-identical.
No attack-surface table was supplied (brief gap); no acceptance clause is treated as out of contract.
Paper wording is checked through the actual offload checker; applied omission plants cover every new site,
with a clean positive control and exact first-digit/word attribution in its CLI self-test.

| Mutant | Bound | Named failing test |
|---|---|---|
| delete a new site | each registered Mac/depth/server/thesis quotation must appear | test_all_new_sites_have_applied_named_omission_controls |
| call raised4 bound calibrated or hide initial1 refusal | measured gate history and uncalibrated scope | test_mac_cells_and_both_gate_attempts_keep_their_scope |
| call B300 measured | finite PRO surface does not certify B300 | test_server_surface_and_model_boundaries_are_not_interchanged |
| replace61.97 with51.97 | no-fit cannot acquire a feasible PRO1M path | test_pro_million_refusal_is_not_hidden_by_the_slot_builder |
| replace same-GPU cases with cross-device/all-depth claim | descriptive exactness stays finite | test_depth_quality_retains_five_exact_cases_and_partition_controls |
| change any first digit/word at a current site | exact named numeric/qualifier registry | offload_bound.py --self-test |

No surviving mutant is claimed. These controls establish the named publication invariants; they do not certify
provider behavior, hardware generalization or calibrated heterogeneous tolerance.

## Delivery evidence

Fresh gate commands, actual exits, head, environment and disk samples are in `.temp/hybrid-c-r21g-261104/`.
All required suites/checkers/guards/PDF/manifest/signature/whitespace gates are rerun at the delivered signed head;
no previous green receipt is reused. Character counts use the printed Russian abstract and trimmed English text;
main words use the unchanged lexical counter for sections00–14. Base45pages/19499words, RU1763/EN1601characters.
Current counts, PDF SHA, source-retention proof and addressed orchestration summary are in the delivery receipt.
CPU only, cache-only PDF, no downloads/native builds/push/tag. Before every gate:df-BG plus exact bytes;
launch at>=28.5 GiB, wait up20minutes below this threshold, hard floor28GiB. No foreign cleanup.

Pre-signature diagnostics: focused01 exit1 caught three inherited current-wording assertions, corrected explicitly;
newtests01 exit1 included a missing not-yet-created evidence README and an incorrect sensitivity selector prefix,
focused02 exit1 retained only that selector error; focused03 and newtests02 exit0.
PDF diagnostic01 exit2 requested uncached cmsy8.pfb from a new table heading; using a plain-text heading fixed
PDF diagnostic02 to exit0 without a download. The four isolated in-memory mutants each exit1 on their
named invariant assertion (no setup errors); clean newtests02 exit0. No survivor.
Whitespace diagnostic01 exit0 scans the full introduced diff, CRLF-aware, without path exclusions.
Cache-only diagnostic PDF47pages, main text20482words before the final deep-client cross-reference, Russian abstract1844characters, English1737.
The final counters and all gates are freshly rerun after signing; these diagnostic receipts do not stand in for them.
