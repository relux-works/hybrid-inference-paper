# Run22 RC4 extension

CPU-only standard-library extension of the reviewed R20/R21 accounting engine.
Historical generators and exports remain unchanged. This entry point has its
own source/input identity and manifest, so adding RC4 inputs cannot invalidate
the frozen run13–21 generator identities.

Run from the repository root with a disk-backed temporary directory:

```bash
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/.temp/hybrid-e-r16-261103/tmp"
python3 -B -I calc/run22/export.py
python3 -B -I calc/run22/export.py --audit-only
python3 -B -I -m unittest discover -s calc/tests -p test_run22.py
python3 -B -I -m unittest discover -s calc/tests
python3 -B -I -m unittest discover -s bench/tests
```

Python generates `calc/out/run22/`, its `paper/` projections and the coordinate
ledger `calc/ENGINE-QUOTES-R22-261103.csv.gz`. The ledger covers every long/short
sentence, the quantitative threshold/measurement tables, and the cost/utilization
columns quoted from small-team/main tables. Other cells are manifest-bound;
the ledger does not claim to duplicate every engine cell. Historical files are
compared recursively, byte for byte, against `b6316e8a`. `git`, `sha256sum` and
the repository Makefile provide signed delivery and tracked-file manifest checks.
Scratch logs and process/disk receipts belong under the task's `.temp/` folder.

The primary tables are **dedicated** bought/rented fleets. `shared_multiples`
is a resident-work/provider limit, with 70% allocation and a 100% utilization
lower bound. Utilization is modelled service occupancy divided by installed
GPU time, with an 8-hour service day and a 730-hour calendar month. Decode tool
occupancy is included; it is not hardware SM utilization. Hybrid fleets are
sufficient, not proved minimal. Amounts are the conditional open-model component
per person-month, including the stated client/front costs, not total household
spending. The same selected call shapes are used for all alternatives.

`measured_ladder` keeps complete end-of-call shapes at no more than 249k,
starting at least 16k deep, with delta512–10000. `physical_extended` includes
the common physical capacity envelope; its larger selected fraction is **not**
measured coverage. Both are normalized to the demanded calls/person-month.
The Claude profile is a reconstruction of published marginals, not raw replay.
This stricter lower bound differs from R20's historical endpoint-held subset.

bf16 changes recurrent **transport**, not resident f32 state or measured import
latency. f32 remains a control. Full-slot bf16 serialization is an encoding
estimate; actual full-slot bytes were measured in f32. The PRO6000 llama.cpp
1M fill was measured at 1813.77 seconds; this is not a vLLM rebuild measurement.

## Data-only interfaces

The CSVs in `data/` carry observations or header-only pending interfaces. The
accepted PRO6000 default-KV point is at the actual16384-token depth:1/8/32/39
streams,48.72/302.98/686.80/738.10 tok/s. It is not relabelled16000 or copied to
64k. The measured39-session resident bound applies at that observed coordinate;
other depths retain the model. Kit1.6.11 deeper reruns are pending. Add dated observations
and their source, then rerun the exporter; no code change is required. Missing
metrics remain blank/pending. A failed validator refuses generation.

| CSV | Contract and use |
|---|---|
| `server_decode.csv` | Qwen vLLM PRO6000/B300 variant key, actual integer depth and streams, aggregate tok/s, `engine=vllm`, UTC timestamp/source, and `extension=yarn_factor4` above262k, up to1,048,576. Complete resident batch must fit. Optional `resident_limit` must agree within a depth and applies to every row at that host/depth. A single-stream curve must span parallel measurements. Used in own-server economics where the depth/count is supported; outside observations remains modelled. |
| `server_prefill.csv` | Server variant, depth/delta, elapsed seconds and matching engine/extension/provenance. Exact observations override extrapolations. Both2k and10k depth curves allow elapsed-time interpolation and labelled sub2k extension. A lone point does not identify a delta intercept. |
| `provider_cache.csv` | Model/tag/profile, input and cached tokens, repeated-series call count and warm-call count, timezone-aware observation date/source. More than three calls, some warm calls and cached<=input required. A low/zero hit fraction is priced, never an admission criterion. The discarded Chutes three-call probe cannot enter. |
| `provider_availability.csv` | Model/tag, timezone-aware `window_start/window_end`, percentage and source. All supplied providers must use the exact same positive interval. Unobserved providers remain unverified; snapshot rates are not backfilled into a measured window. |
| `mac_million.csv` | Client, restored depth1040000, delta690/2000/10000, any observed prefill/import/decode/KL metrics, `priority=normal_priority`, `slot_restored=true`, `extension=yarn_factor4`, timestamp/source. An import additionally declares `import_kind=delta_import` or `slot_restore`, and `transport=bf16` or `f32`. A slot restore never replaces a delta import. Direct prefill feeds separate1.04M thresholds; it is never relabelled as a measured1M turn. Unsupported server context is refused. |

Server keys are `pro6000_fp8`, `b300_fp8`, `b300_fp8_kv`; no5090 server.
Mac keys are `m3max`, `m5max64`, `m5max` (128GB). API model is
`qwen/qwen3.8-27b`, snapshot provider tag and profile `existing_combined`,
`claude_deep` or `million`. The earlier JSON interfaces, including GLM and PRI31
R16b/Glimmer/Gemma, remain available unchanged through their historical entry points.

Availability uses one snapshot last1d field for the primary scenario; exact
snapshot interval endpoints were not retained. The analyst72h sensitivity has
Phala86% and Alibaba96%, with other observations unknown. It is shown both with
and without Alibaba; no other snapshot window is mixed into that cohort. The
future CSV window creates a measured-window scenario and replaces the snapshot
cohort in the economic comparisons. Partial cache observations price individual
providers; cheapest/median measured-cache claims wait for the full admitted cohort. Provider cache
rates are shown as no cache, owner98.1% allowance and measured/pending, without
a provider-cache verdict. API context-extension methods remain unknown; only
the hybrid is configured with model-card YaRN factor4.

The quote ledger uses the named `accepted-csv-to-single-gzip-v1` transform.
`calc/ledger-storage.json` pins accepted CSV size/SHA256 and the committed gzip
SHA256 separately. `calc/ledger_storage.py` is the sole read/write gateway.
Regeneration verifies decompressed content and retains an existing authenticated
gzip; compressed bytes are not compared across interpreter/zlib builds.

Historical custody and the current manifest authenticate the exact committed gzip.
Exporter text reads and fresh regeneration compare accepted decompressed content,
including when no prior gzip exists; valid compressor-byte differences never
relax the independent committed-blob custody check.
