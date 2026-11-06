# Engine report R17 — 2026-11-03

Task `hybrid-e-r9-261103`. Local branch `engine-r17`, requested accepted base
`e51942d331e274833f97f934a750d780c9bea9b0`. No push, downloads, model loads,
native builds or accelerator use. Sources and calculations are English.

## Scope and evidence

Five local kit1.6.5 archives were copied, hash/manifest verified, and extracted
under `.temp/hybrid-e-r9-261103/<source>/results/`. Full archive hashes are in
`data/measurements/run17-2026-11-03/README.md` and the data config; export source
sidecars also hash each admitted payload. Qwen PRI31 step40 remains the Run16
archive. Server rates use FACTS1a, same build `dde879bc` on the PRO6000; SWA Mac
rates use FACTS2 and remain `background_priority_interim`.

The raw-timing audit checks130 segment/delta/decode cells:124 match the printed
precision, and six differ only by a second rounding of kit display values. All
130 stay within the bounded two-stage rounding interval. Calculations use raw
`prompt_n/prompt_ms`, not displayed rates. Six explicit corrections are in the
quote ledger (`facts_double_round_to_raw_once`):

| Model / server depth | Metric | FACTS | Raw tok/s |
|---|---|---:|---:|
| qwen27 / 50000 | decode | 57.3 | 57.247735 |
| qwen27 / 150000 | delta512 | 1,382 | 1381.453980 |
| gemma31 / 150000 | delta512 | 746 | 745.479801 |
| gemma31 / 249000 | delta2000 | 511 | 510.469081 |
| glimmer30 / 16000 | segment | 4,468 | 4467.459306 |
| glimmer30 / 118000 | delta10000 | 2,936 | 2935.456356 |

Mac cells all match their printed precision. The small FACTS discrepancies
do not change any source admission or the raw-based threshold calculation.
`facts-verification-04.log` is green, with all six differences declared.

## Sliding-window payload and full-save reconciliation

For prefix depth `d` and new token count `Δ`, estimate one ideal offload as
`D(Δ,d) = Kfull·Δ + Kwindow·min(W,d+Δ) + Srecurrent`. The client keeps full
attention KV for its old prefix; the transfer contains all currently live
window positions. At all requested depths, windows are saturated. Protocol
framing, token lists and cache bookkeeping are excluded. This is a tensor
payload estimate, not a measurement of prototype SWA transport.

| Model | Native context | Full KV B/token | Window B/position | W | Saturated window B | Recurrent tensor B |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.8-27B | 262144 | 34816 | 0 | 0 | 0 | 156893184 |
| Glimmer30B | 131072 | 7072 | 21216 | 2048 | 43450368 | 0 |
| Gemma4 31B | 262144 | 43520 | 435200 | 1024 | 445644800 | 0 |

Thus Glimmer exports `7072·Δ + 43450368` B, Gemma
`43520·Δ + 445644800` B, and Qwen f32 `34816·Δ + 156893184` B. AtΔ2343 this
is60.020064 MB,547.612160 MB and238.467072 MB respectively. Qwen bf16 is
`34816·Δ + 78446592` B,160.020480 MB atΔ2343. MB is decimal.

The files named `delta-geometry` explicitly contain complete sequence saves,
not exported prototype deltas. Both measured three-point ladders reconcile
exactly with tensor geometry plus observed serialization overhead:

- Glimmer: `7088·depth + 43476268` B = tensor bytes + `16·depth + 25900`.
- Gemma: `43536·depth + 445658604` B = tensor bytes + `16·depth + 13804`.

The constant residuals are inferred from the measured affine intercepts; they
are not claimed protocol-header sizes. At16k/40k/64k, Glimmer saves are
156884268 /326996268 /497108268 B, and Gemma saves are
1142234604 /2187098604 /3231962604 B. All six residuals are0 B. Allocated
`slot_fixed_bytes` (54312960 and668467200 B) include reserved capacity and are
not substituted for live window tensors. Qwen geometry also has1600 B of
non-tensor state metadata; the requested exact recurrent tensor quantity is
used for ideal wire economics.

## Link thresholds

Depth labels32k/64k mean32000/64000 prefix tokens;100k means100000. Every
prefix+delta is inside native context. Server and SWA Mac prefill rates use
bilinear interpolation of raw nominal-depth,512/2000/10000 probes. Qwen Mac
uses the PRI31 Run16 surface; no rate is inferred from a peak ratio.

The serial budget is `Tlocal - Tserver - Timport - RTT`; threshold in B/s is
`D / budget`. Strictly faster links win; equality ties; nonpositive budgets
have no finite winning link. RTT is0.14058910400490277 s. Rates are delivered
application bytes/s, with MB/s multiplied by8 for Mbit/s; no second goodput
factor is applied. Catch-up, framing, chunk overhead and queueing are excluded.

Import uses Run16 `prototype_depth`:
`0.25905207981118364 + 0.0000487·Δ + 0.00003464415395787945·d` seconds.
For SWA this is the named estimate `r16_qwen_token_depth_portability`: reuse
Qwen token/depth coefficients unchanged, with window bytes affecting transfer
only. No SWA import fit exists. In particular the large Gemma window may have
additional import cost. The weak original token fit remains an assumption;
bf16 does not receive an unmeasured import speedup.

Minimum downstream **MB/s**, orderedΔ512 /Δ2343 /Δ10000:

| Model / state | Depth | Δ512 | Δ2343 | Δ10000 |
|---|---:|---:|---:|---:|
| qwen27 / f32 | 32000 | 100.615 | 17.606 | 7.199 |
| qwen27 / f32 | 64000 | 88.260 | 12.342 | 5.126 |
| qwen27 / f32 | 100000 | 47.686 | 7.905 | 3.416 |
| qwen27 / bf16 | 32000 | 55.440 | 11.814 | 6.081 |
| qwen27 / bf16 | 64000 | 48.632 | 8.282 | 4.330 |
| qwen27 / bf16 | 100000 | 26.276 | 5.305 | 2.885 |
| glimmer30 / f32 | 32000 | 23.959 | 4.209 | 1.706 |
| glimmer30 / f32 | 64000 | 20.192 | 2.846 | 1.152 |
| glimmer30 / f32 | 100000 | 26.647 | 2.090 | 0.972 |
| gemma31 / f32 | 32000 | 116.114 | 21.851 | 7.017 |
| gemma31 / f32 | 64000 | 63.464 | 10.984 | 3.438 |
| gemma31 / f32 | 100000 | 28.853 | 6.588 | 2.351 |

SWA rows remain `background_priority_interim`; these cross-model rankings
are interim. Qwen bf16 rows are pending measured quality of dev-a r38. At
100k andΔ2343 the thresholds are7.905 MB/s (Qwen f32),5.305 (Qwen bf16),
2.090 (Glimmer interim),6.588 (Gemma interim). Full precision, timing
components and Mbit/s values are in `architecture_link_threshold.csv`.

## Architecture extrapolation — not a model claim

Hold Qwen PRI31 local rates, kit1.6.5 PRO6000 server rates, RTT and import time
fixed atΔ2343,depth100000. Let `D = S·1000000 + K·1024·2343`; `S` is
decimal MB and `K` is binary KiB/token. Varying bytes does not assert that a
real architecture retains Qwen speed or quality. The fixed latency budget is
30.165156 s. Minimum downstream MB/s:

| Fixed S, MB | K=2 KiB/token | K=7 KiB/token | K=34 KiB/token |
|---:|---:|---:|---:|
| 0 | 0.159 | 0.557 | 2.704 |
| 10 | 0.491 | 0.888 | 3.036 |
| 50 | 1.817 | 2.214 | 4.362 |
| 78.5 | 2.761 | 3.159 | 5.307 |
| 157 | 5.364 | 5.761 | 7.909 |

AtS=10 MB,K=2 KiB/token the extrapolated threshold is0.491 MB/s. EvenS=0
still transfers all new KV; its threshold is positive. The requested78.5/157 MB
grid is deliberately rounded and differs from Qwen’s exact78.446592/156.893184 MB.

## bf16 wire economics — pending measured quality of dev-a r38

Only recurrent tensors on the wire halve. Each ideal offload saves78446592 B;
full-attention KV, resident f32 state, decode, storage migration and import
coefficients retain Run16 assumptions. No second resident stream or speedup
is credited. OnΔ2343, transfer alone falls from24.458 s to16.412 s at9.75 MB/s
(8.046 s saved), or45.947 s to30.832 s at5.19 MB/s (15.115 s saved). At the
illustrative$0.02/decimal GB tariff, per-offload egress falls from$0.00476934
to$0.00320041, saving$0.00156893. `bf16_transfer_egress.csv` covers all54
depth/delta/state/link combinations; RTT/import are separate from transfer.

The paired `f32/` and `bf16/` economics exports recompute routing, foreground
wait, catch-up, capacity, egress and costs. Their server portfolio remains
Run16’s measured B300/PRO6000 economics case, so the pair isolates wire state;
the link-threshold table separately uses the requested same-build PRO6000
server rates. They retain the historical157 MB resident-state approximation
and its decode calibration in both cases; only wire uses the exact tensors.
Default economics egress is$5/TB, distinct from the illustrative$20/TB above.

| Observable / scenario | f32 | bf16 |
|---|---:|---:|
| client_sessions_day.csv / local_sessions_day | 3.972504 | 3.972504 |
| client_sessions_day.csv / hybrid_sessions_day | 5.469343 | 5.475793 |
| client_sessions_day.csv / gain | 1.376800 | 1.378424 |
| traffic_user_month.csv / served_day | 634.443780 | 635.191961 |
| traffic_user_month.csv / hybrid_tb_month | 1.118012 | 0.808498 |
| traffic_user_month.csv / egress_2 | 55.900580 | 40.424900 |
| person_cost_s20.csv / capacity_day | 634.443780 | 635.191961 |
| person_cost_s20.csv / offload_share | 0.314480 | 0.328463 |
| person_cost_s20.csv / egress_month | 4.405479 | 3.182101 |
| person_cost_s20.csv / hosting_month | 6.182218 | 6.232401 |
| person_cost_s20.csv / hybrid_cheapest | 73.409243 | 72.236048 |

Client rows are M3 Max four streams at1Gbit/s,8h; economics is five-person
teams,20% share,Mac already owned; traffic is the heavy profile. The slightly
higher offload share adds storage migration and raises hosting cost despite
lower wire cost. Monthly bytes need not halve when more calls offload. Every
mixed client/economics table keeps the interim parallel qualifier. The inherited
diagnostic tables retain their dated rates/rounded state cases; the added
`wire_state_format` describes the paired economics scenario. Those diagnostics
are controls, not measurements of a bf16 prototype.

Each paired manifest retains334 explicit inherited alarm cells:252 office
placement exclusions,49 context-memory fit refusals,28 depth-zero fit refusals,
and5 pending Mac-import gates. They are not converted to zeros or passing
evidence. The architecture export has0 alarm cells.

## Data-only interfaces and custody

- R16b remains `run16-measurements.json -> m3_parallel`, read unchanged by
  Run17 contexts. Recorded-priority, complete restored/cooled-grid, hash and
  device checks still apply. The Run17 test exercises both unrecorded rejection
  and recorded synthetic acceptance. Frozen Run16 generator/qualification audits
  bind to accepted `e51942d3` instead of future mutable input selection.
- New `run17-measurements.json -> mac.glimmer30/mac.gemma31` entries select
  hash-verified `sources` keys. `mode=verified_pri31`, recorded normal priority
  and no override,PRI31 readiness samples,M3 Max identity and complete exact
  reused grids are required to remove the interim flag. Background evidence
  cannot simply be relabelled. Both interfaces have synthetic controls only;
  actual PRI31 replacement measurements remain pending.
- All new outputs are under `calc/out/run17/`:91 files plusINDEX, with hashes
  and generator identities. All815 existing export files, including runs13–16,
  remain byte-identical to the accepted base. Paper prose/figures remain unchanged.
  The ledger contains12205 coordinate-qualified records:12199 changed/new
  export cells and6 FACTS rounding corrections.

## Validation and bounded fault controls

All gates run as standalone subprocesses with real exit status, no `tee`.
Environment: Python3.14.4/Linux x86_64, standard library only,
`PYTHONDONTWRITEBYTECODE=1`, on-disk
`TMPDIR=$PWD/.temp/hybrid-e-r9-261103/tmp`. Tools and exact commands are in
`calc/README.md`; logs/PIDs/exit timestamps are task-local.

| Gate | Exit / result |
|---|---|
| Run17 exporter | 0; `export-01.log` |
| Focused Run17 positive/negative suite | 0; `focused-final-06.log` |
| Kit suite | 0; `kit-suite-01.log` |
| Full engine suite | 0; `engine-suite-01.log` |
| 130-cell FACTS bounded comparison | 0; `facts-verification-04.log` |
| Current-index / frozen-byte / quote audit | 0; `audit-01.log` |
| Five bounded fault controls | 0; `mutants-01.log` |

Each mutant below exits1 with the named assertion failure; no setup errors or
survivors. `mutants.json` records commands and actual statuses.

| Mutant | Gate narrowed to | Named failing test |
|---|---|---|
| omit_window | Complete live window, not delta-only/full-prefix substitution | test_offload_rejects_delta_only_window_and_full_prefix_charge |
| halve_entire_wire | Recurrent tensors only; KV unchanged | test_bf16_rejects_halving_whole_wire_and_rounded_state |
| omit_import_depth | Exactly one conditional depth term | test_import_depth_rule_rejects_omitted_or_double_counted_term |
| launder_priority | Recorded PRI31 readiness required | test_mac_data_only_interface_rejects_unrecorded_priority |
| label_only_bf16 | Actual policy wire dependency changes | test_economics_rejects_resident_halving_and_wire_label_only |

The suite also plants bounded in-memory corruption of a frozen export and a
current export, and deletes/forges quote coordinates. Every previously named
reviewer test is retained; no requested task row is excluded. No surface table
or separate landing-property suite was supplied (explicit brief gap).

Diagnostic failures are preserved: smoke01 hit Gemma’s extra smokeJSONL; the
loader now selects the model-specific file. Smoke02 lacked the raw-table metric
counter, corrected before export. Focused01 exposed two fixture errors (missing
client API arguments and duplicate readiness filenames); focused02 and later
passed. FACTS audit01 could not parse thousands separators;02 revealed the
rounding discrepancy;03 inventoried all cells;04 bounds and declares all six
rather than presenting them as exact matches. These failed commands are not
green gates. No calculator source/input change occurred after the green export. The quote
auditor was extended during full-suite execution, before its Run17 artifact
tests loaded it, to include the six FACTS corrections; final focused/audit gates
exercise that exact auditor.

The first detached disk watcher retained only one sample and did not remain
live. It was restarted in a foreground tool session at09:28:31Z. There is no
continuous-monitor claim for the earlier interval; spot observations were above
28GB. Later one-second observations are in `disk-samples.jsonl`; the final
observed minimum and delivery evidence are recorded below. No foreign files
or processes were removed or stopped.

## Review boundary

Ready for review. Required final validation gates passed. SWA import/transport,
PRI31 SWA and parallel remeasurement, and bf16 quality remain explicit
measurement/qualification limits. The architecture extrapolation is not a real
model claim. No push or hosted landing is authorized.

Full engine:378/378 tests,765.983s,exit0; kit:24/24 tests,44.396s,exit0; final
focused Run17:18/18 tests,exit0. All360 previous engine tests are retained.
The source/config/test delta was self-reviewed, with no foreign edits present.
Final observed disk audit at2026-11-03T09:44:51.244200+00:00:
minimum30879817728 B (>28,000,000,000 B) during the monitored
interval; earlier observer gap remains declared above. Post-commit signature,
clean-scope and addressed a2a receipt are kept in the task log and scratch
delivery evidence.
