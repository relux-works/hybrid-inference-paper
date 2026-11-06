# Run24: final API cache/availability overlay for RC4

Accepted parent: engine-r23 `9064701a`, Muse r5x5 ACCEPT. All run13–23 exports
remain byte-identical. Hardware rates, bf16-default/f32-control transport,
1M routing, PRO decode, workload shapes and dedicated-primary policy stay on
that parent. Historical bought-office API headlines are inherited controls
with their original snapshot/98.1% assumptions; new measured points are separate.

Run CPU-only from the checkout root:

```bash
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/.temp/hybrid-e-r18-261105/tmp"
python3 -B -I calc/run24/inputs.py
python3 -B -I calc/run24/curves.py
python3 -B -I calc/run24/export.py
python3 -B -I calc/run24/export.py --audit-only
python3 -B -I calc/r24_report.py
python3 -B -I calc/r24_report.py --audit-only
python3 -B -I calc/run24/controls.py control
python3 -B -I -m unittest discover -s calc/tests
python3 -B -I -m unittest discover -s bench/tests
make manifest
sha256sum --check MANIFEST.sha256
```

`inputs.py` regenerates the data-only cache, availability and tariff CSVs from
the copied final report/analysis/accepted/attempt rows in `data/`; `evidence.json`
binds their original hashes. No source tree owned by the measurement producer
is written. A new data-only intake replaces those input files/hashes and runs
the adapter. Cost curves do not need recomputation for an API-data-only update.
The original R16b, Glimmer/Gemma PRI31 and run22 pending interfaces stay intact.

`curves.py` caches all native1..500-person Qwen hybrid costs on the unchanged
run23 classes. Its deterministic compressed JSON binds the exact baseline
calculation inputs and replay source, and checks5184 owned cost/capacity samples
against accepted exports. New-client capital is additive, checked against all
published new-client samples. It never interpolates costs between team sizes.

`export.py` writes `calc/out/run24/` and `paper/`, a source/file manifest and
`calc/ENGINE-QUOTES-R24-261105.csv`. `baseline_inheritance.csv` references each
unchanged run23 CSV rather than duplicating those large controls. The report
publisher writes the report, its coordinate quotes and publication manifest.
Git verifies the signed local commit. Logs, actual exit-code receipts and
bounded owned-process/disk guards live in the task `.temp/` folder. No downloads,
native builds or push are part of this run.

## Cadence, price and admission

Every measured point names `v1_long_pause` or `amendment_core`; neither silently
substitutes for the other. Native study USD/1000 retains its measured depth mix,
1065 new input/512 output projection and conservative write-surcharge convention.
Paper-normalized points apply the observed aggregate token-hit fraction and
mean same-cohort live tariffs to the identical run23 call-shape means, using
run22's expected aggregate-token tariff formula. Porting a hit fraction across
depth/workload mixes is an assumption, not raw replay or a measured TTL guarantee.
The native, normalized and pooled1M results are distinct columns/tables.

Core phase aggregates retain resumed cells. `api_cadence_subsets.csv` separately
shows uninterrupted, interrupted-cell and continuation-only source aggregates.
Continuation flags do not count earlier pre-stop calls in the same interrupted
cell. No stop gap is represented as an8s/35s TTL result.

All actually attempted endpoints use the same whole observation window for
admission, including seeds, failures and timeouts. Any availability below95%
refuses. Never-attempted Qwen endpoints retain snapshot-last1d availability and are
labelled; missing availability remains unverified. The old GLM research summary
retained neither cache declarations nor uptime and is not a qualified fallback.
Final-study selected inventory and same-cadence live evidence establish the GLM
points; unattempted GLM availability and prices remain unverified. A context minimum is never called a precise upper limit.

Known zero hits are priced. Missing cache measurements are unknown, never zero.
The final study's thin1/2-warm-call points stay descriptive and visibly thin;
they do not certify provider-wide behaviour. The entire Chutes smoke and every
seed are excluded from cache inference. The adapter retains the old run22 CSV
validator for repeated series; thin final-study points require exact binding to
the accepted raw study, not a relaxed standalone three-call probe.

Cheapest and upper-middle median are ranked among **admitted priceable endpoints
at that cadence**. The measured cohort is partial: unmeasured admitted endpoints
remain in the inventory and are not silently excluded as providers. No global
cheapest-API claim or cache verdict is made over those unknown prices.

## Comparisons and limits

Dedicated crossings scan every integer team size through500 and require a
sustained strict advantage; capacity refusals remain unknown, not zero cost.
Shared comparisons are constant resident-work/provider allocation limits, not
dedicated-team batching promises. Every quoted cost retains utilization and
all link, billing, client, share, load and call-shape coverage conditions. Heavy
2500 calls/day remains the owner's intensity; light/medium are typical.

Qwen API versus Qwen hybrid rows are same-model comparisons. Additional root
rows show GLM API **price references versus Qwen hybrid**, explicitly different
models with no quality/performance equivalence claim. These are excluded from
paper hybrid-claim tables: this API-only run supplies no new GLM client/server
performance. Per-model API rankings remain in the paper exports.

GLM pooled1M is equal-provider weighted across15 qualified measured providers,
with the same mean with/without Alibaba. Qwen1M has no qualified measured provider.
Its historical snapshot scenarios remain labelled inherited controls. API context
extension is unknown; identical model-card YaRN to the hybrid is not established.

`abstract_bound_changes.csv` accounts for every unique source coordinate quoted
by the accepted run23 report, including text-valued paper sentences and earlier
audit coordinates. Those inherited controls remain unchanged; new measured
points and crossings state their different cache/admission/cohort basis.
