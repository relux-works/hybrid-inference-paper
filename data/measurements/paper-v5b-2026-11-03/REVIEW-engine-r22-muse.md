# Review: engine run 22 — Muse reviewer (hybrid-rev-r5x4-engine-r22-261103)

- Candidate: branch `engine-r22`, head `9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0`, parent `b6316e8a` (accepted in r5x3).
- Producer: hybrid-e-r16. Reviewed in a local clone at the exact head; clone deleted after review.
- Method: brief + resume read in full; report, run22 code, FACTS excerpts read; headline numbers recomputed
  independently from the exported CSVs and the repo inputs (not by rerunning the exporter); all gates rerun in
  the clone with `TMPDIR` inside the clone and `PYTHONDONTWRITEBYTECODE=1`.

## Verdict

**ACCEPT** — bound to `9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0`.

No blocking findings. The findings array below contains only `note`-severity items: wording and disclosure
points for the paper text. Every abstract-bound number I recomputed holds exactly.

## Findings

```json
{
  "verdict": "accepted",
  "head": "9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0",
  "findings": [],
  "notes": [
    {
      "id": "claude-zero-offload-crossings",
      "row": "1/5 words-ready sentences",
      "severity": "note",
      "repeat-of": "none (inherited mechanism, present in accepted r20/r21)",
      "detail": "claude_deep measured-ladder dedicated rows (bought PRO, M5 Max 64, s=0.2) have offload_share=0.0, prefill_gpu_s_day=0 and service utilization 0.00% at every load: no Claude call offloads (spill 0.94 x cold rebuild makes remote lose for those shapes), so the $56.64 team-50 cost is local-only Mac work plus an idle residency fleet. Cost claims disclose 'service utilization 0.00%, calendar occupancy 0.00%', but claude crossing sentences (own cluster from 4 at medium, from 2 at heavy; median API from 30 at heavy) carry neither utilization nor offload share. Do not quote a claude crossing in the paper as a hybrid-offload result."
    },
    {
      "id": "measured-16k-decode-inert-in-economics",
      "row": "2 new inputs / 4 crossings",
      "severity": "note",
      "repeat-of": "none",
      "detail": "The measured PRO 6000 16k decode point (48.72/302.98/686.80/738.10 tok/s, x15.15 at 39) is correctly published in server_decode_measured.csv and fed through server_decode.csv, but it changes no economics row: measured anchors apply only at exact depth 16384, and zero of the 10,885 selected calls have depth+delta=16384 (measured ladder implies >=16512; verified by direct probe). Own-cluster and hybrid decode therefore remain fully modelled (model at 16000: 44.42 single / 611.45 at 32 streams vs measured 48.72 / 686.80 at 16384, i.e. the model is ~10% slower there, which if anything overstates own-cluster cost slightly). The report's 'use it only where depth and stream count are supported' and the sentences' 'modelled unless measured CSV overrides' are literally conditional, but the paper must not state that run-22 economics use the measured decode."
    },
    {
      "id": "report-1m-table-client-unlabelled",
      "row": "1 policy item 5",
      "severity": "note",
      "repeat-of": "none",
      "detail": "The report's 1M table (bf16 2.992 / f32 5.283 MB/s) does not name the client. Those values are the M3 Max rows (anchored local 70.529 s). For the M5 Max 64 the anchored budget is nonpositive (local 15.771 s < server prefill 1.223 + import 34.937 s), so there is no finite threshold and offload is False; only the 120 s sensitivity gives 1.224. CSV rows and sentences carry the client; the abstract must name M3 Max when quoting 2.992."
    },
    {
      "id": "idleness-example-superseded",
      "row": "1 policy item 2",
      "severity": "note",
      "repeat-of": "none",
      "detail": "The brief's example price of idleness (API/hybrid 1.462 shared vs 0.526 dedicated at PRO 50) is the R20 heavy-load pair (shared $42.510, dedicated $118.050). Run 22 recomputes it and does not reconcile the change: at heavy the pair is now 1.701 shared ($36.53) vs 1.097 dedicated ($56.64); at medium 0.934 vs 0.351; at light 0.313 vs 0.088. The paper must use the run-22 numbers, not the brief's example."
    },
    {
      "id": "bought-server-assumptions-not-restated",
      "row": "3 primary selection cost model",
      "severity": "note",
      "repeat-of": "none",
      "detail": "The bought PRO 6000 unit cost $614.0575/month recomputes exactly from inherited inputs (capex $30,000, residual 20%, 4 years = $500; support 2%/yr = $50; power 0.9 kW x PUE 1.3 x 730 h x office load 0.5 x $0.15/kWh = $64.0575; office hosting/colo $0), and the rented variant is $2.20/h x 730 = $1,606/month. These assumptions live in the repo input data and unit_month code but are not restated in the run-22 report or run22 README; the paper text must state them where it quotes $56.64."
    },
    {
      "id": "m3max-economics-absent",
      "row": "3 primary selection",
      "severity": "note",
      "repeat-of": "none (same scope as accepted r20/r21)",
      "detail": "The owner's own client, M3 Max 128 GB, has no economics rows in run 22 (main/small-team clients are m5max64 and the m5max same-SoC portability estimate only; grep m3max in paper/main_economics.csv = 0). M3 Max appears in link_thresholds (750 rows, incl. the 1M headline) and in Glimmer measurements. Whether M3 Max economics would change any crossing cannot be determined from run-22 outputs; the paper must not present the M5-based crossings as the owner's-machine result."
    },
    {
      "id": "facts-readiness-counts",
      "row": "2 new inputs",
      "severity": "note",
      "repeat-of": "none",
      "detail": "FACTS says readiness samples Qwen 36 / Glimmer 31; the archived OPERATOR-READINESS.json files contain 35 / 30 sample rows (verified). The producer discloses this and lets the archives govern; every archived llama-server sample is PRI 31 / nice 0, enforced in measurements.priority(). No action needed beyond keeping the disclosure."
    }
  ]
}
```

## Item 1 — the nine policy items

| # | Item | Result |
|---|---|---|
| 1 | bf16 default 78,446,592 B, f32 control | Held. `measurements.BF16/F32`; wire = delta*34816 + state (Δ690: 102,469,632 vs 180,916,224 B, recomputed). Resident state stays f32; f32 rows adjacent labelled control. KL −0.000298 [−0.001076,+0.000390] vs own 0.054253 and RULER 390/390 both depths, hash-bound analyses; answer changes 28/33 disclosed, no identity/accuracy claim. |
| 2 | Dedicated primary, utilization beside every cost, shared = full-utilization limit, price of idleness named | Held, with note `idleness-example-superseded`. Every dedicated CSV row carries service+calendar utilization, own-cluster comparator included; report tables show both. Shared rows at 70% allocation plus 100% lower bound. Reason (authors run a shared prefill service) and night-agent remark present in policy.csv/report. |
| 3 | API admission impossibility-only; cheapest at three points; no Chutes probe | Held. Admission reasons in `api_admission.csv` are exactly {context_below_N, caching_not_declared, common_window_availability_below_95}; zero admitted providers under 95%; cache never an admission input (`api.admission`). Three points: no_cache darkbloom/fp4 $5.505, owner_981 chutes/fp8 $1.213, measured pending (no verdict). `interfaces.cache_rows` refuses series of ≤3 calls / no warm calls. |
| 4 | Availability over one window; 1M with/without Alibaba | Held. Primary cohort uses snapshot `uptime_last_1d` uniformly (endpoints unretained, disclosed; no min over 5m/30m/1d). 1M owner-981: snapshot_1d phala 54.715 / novita 93.581; analyst_72h_with_alibaba novita 93.581 / alibaba 95.351; without_alibaba novita/novita — all recomputed from the CSV. Measured-window CSV interface refuses mixed windows (mutant killed). |
| 5 | 1M threshold bf16 main, 120 s sensitivity, Δ690/2000/10000 interface | Held, with note `report-1m-table-client-unlabelled`. bf16 anchored 2.992 vs f32 control 5.283 MB/s; shared budget 34.25 s; 120 s sensitivity 1.224 (bf16). `mac_million.csv` header-only interface + `direct_mac_pending.csv` 9 pending rows (3 clients x Δ690/2000/10000); slot restore never substituted for delta import. |
| 6 | Heavy: no second Mac, one sensitivity, 2,500/day = owner intensity | Held. `heavy_sensitivity.csv` has exactly one sensitivity (generation moved to team's own vLLM server; 2 rows = 2 profiles); Ultra explicitly unmeasured/unpriced. Every heavy row/sentence says owner intensity, light/medium typical. |
| 7 | Coverage wording for 27.28% | Held. CSV `workload_scope` and sentences: "share of calls whose shapes lie inside the common measured ladder 10885/39904 (27.28%) … normalized to N calls/person-month; full unconditioned mix unsupported"; report states it is not a share of workload/token mass. 10885/39904 = 27.278% recomputed. |
| 8 | Words-ready sentences + short form | Held. Long form = r15-style `field=value` conditions; short form = human header + full prose conditions; `sentences.validate` requires every field verbatim from the row plus cost/utilization/crossing numbers; missing-link mutant killed. |
| 9 | Reason for withdrawn heavy claim | Held. policy.csv + report: own cluster recalculated on vLLM; under vLLM prices the old claim held only for a 5090 hybrid, which the owner excluded; not a second-Mac explanation. |

## Item 2 — new inputs vs FACTS

- **Sergey M5 Max 64 GB PRI 31** — held. `engine.context()` installs `measured_m5` before any client graph
  resolves, replacing the owner-reported-priority family for run 22 only. Archives SHA256-checked per
  `evidence.json` (1d0d04a3…, 89211edd…), manifests require `normal_priority=true`, no override, every server
  sample PRI 31/nice 0. Client batching gains from `client_measurements.csv` (basis `measured`): Qwen
  2.715/2.024/1.284 at 32768/65536/131072, Glimmer 3.236/2.660/2.363 at 32768/65536/129024 — exactly the FACTS
  values. Sample-count discrepancy 35/30 vs FACTS 36/31 disclosed (note above).
- **Glimmer PRI 31 on M3 Max** — held. FACTS transcription hash-bound; successive-turn starts reconstructed
  (+delta+128: e.g. 16640 after 16000+512+128, rates 167.7/173.5/158.4 etc. match FACTS); replaces
  background-priority block; archive copy pending, labelled. SWA import-cost reuse labelled unmeasured
  portability assumption in threshold rows.
- **30.2 min slot fill** — held. `full_resync.csv`: 518.29 + 1295.48 = 1813.77 s to 1,040,000; measured f32
  slot 36,394,654,776 B; server restore 3.14 s explicitly not Mac import; bf16 slot payload labelled estimate.
- **Measured PRO 6000 decode 16k** — held as data, inert in economics (note above). Values 48.72/302.98/
  686.80/738.10, gains 1/6.22/14.10/15.15 recomputed; 39-session resident limit enforced at that depth only.
  `decode_scaling.csv` grid (16000/64000/164000/512000) is entirely `modelled bandwidth … not vLLM decode
  measurement`; deeper points modelled, B300 modelled.

## Item 3 — primary selection

Bought PRO 6000 vLLM FP8; office 125 MB/s, RTT 1 ms; owned M5 Max 64 GB PRI 31; s = 20%; owner 98.1% cache
allowance. Support: brief policy 2 (dedicated bought-or-rented today; PRO 6000 is the brief's example
server), brief policy 3 (98.1% point), brief new-inputs (Sergey PRI-31 rates replace owner-reported). The
125 MB/s / 1 ms office link and s ∈ {0.2, 0.5, 1.0} grid are inherited engine assumptions, labelled
"assumed" in every sentence; all three shares, both billings, both transports, both Mac bases are exported,
so the primary selection is one named row family, not a hidden filter.

- **M3 Max rows**: thresholds only, no economics (see note `m3max-economics-absent`). Effect on crossings:
  not determinable from run-22 outputs.
- **Bought-server cost model** (recomputed from inputs, exact): unit $614.0575/month = capex $30,000 ×
  (1 − residual 0.20) / (12 × 4 years) = $500 + support 2%/yr of capex = $50 + energy 0.9 kW × PUE 1.3 ×
  730 h × office-load 0.5 × $0.15/kWh = $64.0575. Office hosting/colo $0 (colo $190/kW applies to B300 only).
  Rented variant present everywhere: $2.20/h × 730 = $1,606.00/month, WAN 112.5 MB/s / 400 ms, egress at
  $5 per decimal TB, storage billed separately. Client: owned = $0 device; energy 0.1 kW × 8 h × 21 days ×
  $0.15 = $2.52; front $5. Assumptions not restated in the report (note above).

## Item 4 — independent recomputation (team 50, primary selection)

- **$56.64/person-month**: boxes 4 × $614.0575 / 50 = $49.1246 server + $0 device (owned) + $2.52 client
  energy + $5 front + $0 egress (office) = $56.6446. Identical at all loads because the hybrid fleet is
  residency-sized (4 boxes at team 50; 1/1/1/2/4/36 boxes at teams 3/5/10/20/50/500), not work-sized; own
  cluster is work-sized (4/11/27 boxes at light/medium/heavy team 50).
- **Utilization**: service = team × prefill_gpu_s_day / (boxes × 1 GPU × 8 h × 3600): light 50×83.266/115200
  = 3.61%, medium 50×333.065/115200 = 14.46%, heavy 50×1040.829/115200 = 45.17%. Calendar = service ×
  (21 days × 8 h / 730 h) = 0.83 / 3.33 / 10.40%. Decode overflow 0 (client capacity 916 calls/day > demand).
- **Median API / hybrid** (owner-981 median deepinfra/bf16 person-month 4.9706 / 19.8826 / 62.1331):
  0.088 / 0.351 / 1.097 — exact.
- **API unit costs** recomputed from snapshot tariffs and billed means (input 124,987.1, output 513.74
  tokens): chutes/fp8 owner-981 $1.2130/1000 calls, deepinfra/bf16 $5.9174/1000 — exact to 4 dp.
- **Crossings** (sustained through 500, from `team_break_even.csv`, spot-verified at teams 3/5/10/20/50/500
  against `small_team_cost`/`main_economics`): own cluster — light never (3: 212.21 vs 204.69; 50: 56.64 vs
  49.12; 500: 51.73 vs 44.21), medium from 5 (3: 212.21 vs 204.69; 5: 130.33 vs 245.62), heavy from 2
  (3: 212.21 vs 409.37). Median API (owner-981) — only heavy, from 45. Cheapest API (owner-981) — never.
  All match the producer's summary. Rented-WAN variant differs: median heavy never crosses when rented.

## Item 5 — for the plain-language text

1. **Bought Mac vs owned Mac.** Run 22 prices a newly bought M5 Max 64 GB at +$69.05/person-month
   ($5,099 × (1 − 0.35 residual) / 48 months), taking team-50 hybrid from $56.64 to $125.69. With a bought
   Mac: own-cluster crossing at medium moves 5 → 34 people; at heavy it stays at 2; the median-API crossing
   at heavy disappears (45 → never through 500); light and cheapest-API remain never. In plain words: the
   hybrid case at medium/heavy load depends on the team already owning suitable Macs; buying Macs for it
   removes the API advantage entirely and delays the own-cluster advantage to 34 people at medium load.
2. **Own cluster at 2–5 people, light/medium.** On the like-for-like dedicated basis: at light load the
   own cluster is not beaten at 2–5 people (nor through 500); at medium load it is beaten only at exactly
   5 people, not at 2–4. On the shared (full-utilization limit) basis the hybrid cost is team-independent,
   $15.90 (light) / $21.29 (medium) per person-month, which is below the dedicated own-cluster cost at 2–5
   people — but that compares a shared-limit hybrid against a dedicated cluster; run 22 computes no
   shared-basis own cluster, so that comparison mixes bases and should not be quoted as like-for-like.
3. **Cheapest API vs hybrid.** At the owner's 98.1% cache point the cheapest admitted API is chutes/fp8.
   Team-50 cheapest/hybrid multiples: dedicated 0.018 / 0.072 / 0.225 (light/medium/heavy), i.e. the hybrid
   costs 55× / 14× / 4.4× the cheapest API; shared basis 0.064 / 0.191 / 0.349 (16× / 5× / 2.9×). The
   cheapest API is never crossed on either basis through 500 people. Warning for wording: at the no-cache
   point the cheapest is a different provider (darkbloom/fp4) and IS crossed at heavy load from 74 people
   dedicated (multiple 1.020 at team 50) — every "cheapest API" sentence must name its cache point.

Also carry into the text: claude-profile crossings are zero-offload local-only results (note 1); the 1M
2.992 MB/s threshold is an M3 Max number (note 3); economics clients are M5, not the owner's M3 (note 6).

## Item 6 — gates rerun in the clone (TMPDIR inside clone, PYTHONDONTWRITEBYTECODE=1)

| Gate | Command | Exit |
|---|---|---|
| Engine suite | `python3 -B -I -m unittest discover -s calc/tests` — 523 tests, 560 s, OK | 0 |
| Kit suite | `python3 -B -I -m unittest discover -s bench/tests` — 24 tests, OK | 0 |
| Audit | `python3 -B -I calc/run22/export.py --audit-only` — `{"historical_files": 987, "new_files": 27, "quote_cells": 528021}` | 0 |
| Report | `python3 -B -I calc/r22_report.py` — 198 report quotes verified | 0 |
| Manifest | `sha256sum -c MANIFEST.sha256` — 1857 files, 0 non-OK | 0 |
| Historical byte-identity (independent) | `git diff --stat b6316e8a..9053089e -- calc/out/run13..run21 calc/out/paper` empty; `git ls-tree b6316e8a -- calc/out` = 987 files | 0 |
| Fault control | `python3 -B -I calc/run22/controls.py control` | 0 |
| Mutants (expected red) | `force_f32`, `three_call_cache`, `mixed_window`, `infer_link`, `flat_server_decode`, `copy_16k_to_deep` | 1 each |
| Egress USD/TB regression | test in suite (`test_egress_refuses_gigabyte_tariff_…`) green in the 523; independently recomputed rented medium team-50 egress: 160 served/day × 21 × 35,356,859 B / 1e12 × $5 = $0.5940 = CSV value | 0 |

Commit `9053089e` is signed (G, Relux Nexus) with the required Codex co-author trailer. Free disk stayed at
30–31 GiB, above the 28 GiB floor. Paper exports contain no 5090 server rows (servers: pro6000_fp8,
b300_fp8, b300_fp8_kv only).
