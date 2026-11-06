# Run23: night measurements on the accepted run22 policy

Run from the repository root, CPU only, with a disk-backed temporary directory:

```bash
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/.temp/hybrid-e-r17-261104/tmp"
python3 -B -I calc/run23/export.py
python3 -B -I calc/run23/export.py --audit-only
python3 -B -I calc/r23_report.py
python3 -B -I calc/r23_report.py --audit-only
python3 -B -I -m unittest discover -s calc/tests
python3 -B -I -m unittest discover -s bench/tests
python3 -B -I calc/run23/controls.py control
```

`export.py` writes `calc/out/run23/`, PRO6000/B300-only `paper/` projections,
its own source/row schema and manifest, and the coordinate quote ledger
`calc/ENGINE-QUOTES-R23-261104.csv.gz`. The report publisher adds
`calc/ENGINE-REPORT-R23-261104.md`, its source-coordinate ledger and a separate
publication manifest. Git and `sha256sum` verify the signed local commit and
tracked-file `MANIFEST.sha256`; `make manifest` refreshes that inventory after
staging. Logs and process/disk receipts stay in the task's `.temp/` directory.
Historical numerical functions and accepted producer identities remain exact;
only the declared ledger I/O and provenance adapters are migrated. Every historical `calc/out/` file is compared recursively with the
accepted `9053089e` base, not merely numerically or at the top directory level.

## Measurements and interpolation

`data/server_decode.csv` contains the accepted kit 1.6.11 PRO6000 default-KV
observations at actual depths 16384/65536/164000/256000. The retained compact
receipt preserves exact medians, three-round aggregate values and the capacity
search, with the full raw JSON SHA256. The full local GPU archive SHA256 was
verified against FACTS; no archive or model was downloaded. Each stream has
its own private context. Timing is SSE chunk receipt, with exact token IDs per
chunk; it is not per-token GPU-event timing.

At an observed depth/count, decode returns that observation exactly. For other
counts at that depth, interpolate **seconds per sequence-token** between observed
counts. Between depths, use equal fractions `(N-1)/(resident_limit-1)` of the
admitted batch, interpolate that service time between depths, then compute
aggregate throughput as `N / seconds`. Capacity interpolates **reciprocal**
resident count (space per session), rounds down, and also respects physical
memory. Intermediate points are interpolation assumptions, not measurements.
The surface is used automatically by fleet accounting even if the caller has no
exact-count sparse curve; run22's inert-single-depth limitation is removed.
Below 16384 and above 256000 retain the labelled bandwidth model. B300 decode
remains modelled after its rental failed to start at 2026-11-04 00:36Z.

PRO vLLM default-KV 1M cannot be admitted: 61.97 GiB was needed versus 56.62 GiB
available, and FP8 KV is unavailable on SM 12.0. No feasible routing, decode or
server cost can be derived by switching that row to a model. The old llama.cpp
Q4/q8 slot-builder timings remain historical artifact-construction context,
explicitly not a feasible current vLLM1M server scenario.

## Mac recovery: measured full slot, not measured delta import

`data/mac_direct.csv` transcribes the accepted FACTS medians from kit 1.6.12
step 56 on the owner's M3 Max 128 GB, normal priority, **warm/no purge**, restoring
from an external **LaCie SSD**. The strict archive is with the incident lane;
this checkout does not claim to have reverified its abbreviated SHA256.
The gate was raised from 1.0 after a refused attempt (max raw-logit difference
1.08298) to 4.0, which is **not calibrated**. Both attempts stay disclosed.
Prefill excludes restore; each shape has an excluded warm-up and three timed
rounds. The 1040000+10000 shape is refused by the 1048576 context limit.

Per the run23 instruction, the measured **full-slot restore** is charged once
per offload as a conservative recovery proxy while wire bytes remain the bf16
(default) or f32 (control) delta payload. This is not a measurement of delta
import or end-to-end hybrid latency. Timed warm medians are 2.965s at 524288 and
40.479s at 1040000; first-probe restores 20.523/40.465s are separate sensitivities,
not purged/cold numbers. Actual 1040000 rows remain at that depth. The retained
1000000 comparison uses the 1040000 observation as an explicitly labelled proxy;
it is not called a direct 1000000 measurement. The analyst's earlier 120s local
turn remains a separate sensitivity. M5 deep rates/recovery remain estimated.

Bridge medians are exported as **context only**: there are no separate,
non-overlapping export/conversion terms, and a loopback CUDA import cannot
replace a Metal recovery. The reviewed aggregate bridge envelope stays intact;
components are not added to it a second time.

## Policy, provenance interfaces and comparisons

bf16 transport, f32 resident state, dedicated bought/rented primary basis,
utilization, shared-provider lower bounds, API admission/common availability
window, heavy owner-intensity and measured-call-shape coverage remain run22's
policy. Economics clients remain M5 Max 64/128 GB (128GB same-SoC portability),
not the owner's M3. Zero-prefill-offload cost/crossing families say so in both
sentence forms; local work plus residency/overflow must not be described as an
offload gain. Hybrid fleets remain sufficient, not proved minimal.

Provider cache/availability, server prefill and future Mac delta-import CSV
interfaces retain run22's validators and provenance fields, now in this data
folder. Empty rows remain pending; low cache hits are priced, not excluded.
The exploratory three-call probe is never an input. Accepted receipt replacements
also update `data/evidence.json`; this is a data-only change. Old R16b and
Glimmer/Gemma PRI31 interfaces remain unchanged at their historical entry points.

`changed_against_run22.csv` lists every common-coordinate numeric/verdict change,
including fleet counts, capacities, costs and crossings. `change_summary.csv`
counts changed/additional/removed rows per table. `abstract_bound_changes.csv`
accounts for every numeric coordinate quoted by the accepted run22 report,
plus its prose timings and primary crossing/fleet figures, including unchanged
values. Comparisons use semantic row keys and exact cell values; duplicates
refuse instead of silently overwriting a coordinate. Protocol/depth changes
are stated in the reason column. The report prints this abstract-bound ledger.

The quote ledger uses the named `accepted-csv-to-single-gzip-v1` transform.
`calc/ledger-storage.json` pins accepted CSV size/SHA256 and the committed gzip
SHA256 separately. `calc/ledger_storage.py` is the sole read/write gateway.
Regeneration verifies decompressed content and retains an existing authenticated
gzip; compressed bytes are not compared across interpreter/zlib builds.

Historical custody and the current manifest authenticate the exact committed gzip.
Exporter text reads and fresh regeneration compare accepted decompressed content,
including when no prior gzip exists; valid compressor-byte differences never
relax the independent committed-blob custody check.
