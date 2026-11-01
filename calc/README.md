# Hybrid calculation engine

> Run11 supersedes earlier numerical base examples: current nonlegacy bases use output alone; fraction1 is the labelled reasoning-on-top upper bound. See [Run11](#run-11-output-already-includes-reasoning) and the regenerated publication CSVs. Historical bridge/legacy reproductions retain their dated inputs.

`hybridcalc/` consolidates the paper's calculations. It uses only the Python 3.9+
standard library. No installation, API access or network is needed. The current
paper defaults and paired conservative CSVs are described in the run-9 section;
its append-only hosting supersedes the historical run-8 equations below. Run from the
repository root (the small `hybridcalc.py` entry point locates the package), or
from `calc/` with the same module commands.

```bash
python3 -m hybridcalc list
python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper
python3 -m hybridcalc run paper-tables-r6 --format md
python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper
python3 -m hybridcalc run paper-tables --format md
python3 -m hybridcalc export paper-tables --output calc/out/paper
python3 -m hybridcalc run paper-base
python3 -m hybridcalc run paper-base --set hardware.links.wan.bandwidth=2500000000
python3 -m hybridcalc run paper-base --set prices.egress=0 economics.regions=3 --format csv
python3 -m hybridcalc run glm-tier2 --format json
python3 -m hybridcalc sources paper-base
python3 -m hybridcalc sources paper-base --set prices.egress=0 --format json
python3 -m hybridcalc run glm-tier2 --format tex > .temp/glm-tables.tex
```

`--set` accepts repeated flags or several `path=value` arguments. Numeric values
are JSON numbers; precision enums also accept unquoted names such as `Q4`, `Q6`, `Q8`,
`FP8`, `NVFP4` and academic `BF16`; client quantization is `Q3` or `Q4`.
Overrides retain their unit and record original provenance. Unknown paths,
non-quantity targets and malformed numeric JSON are command errors (exit 2).
Known canonical inputs set to null, invalid units/types/ranges, NaN or infinity
become metric alarms when read. Nothing substitutes zero or an assumed value.
The strict `Inputs` API used for legacy execution still rejects invalid
quantities/overrides atomically.

```bash
python3 -m hybridcalc run paper-base --set prices.rental_gpu_hour=null
python3 -m hybridcalc run paper-base --set prices.rental_gpu_hour=null --strict
python3 -m hybridcalc run service-fp8 --strict --format csv
python3 -m hybridcalc run service-fp8 --set service.precision=BF16 --format json
```

## Declared metrics, gaps and strict mode

Every canonical output cell declares direct requirements and transitive input
paths in `tables[].dependencies["row.column"]`. A cached dependency graph reads
and validates those inputs before evaluating the metric. A failed dependency
propagates its original input path/reason; independent nodes still evaluate.
For example, a missing `prices.rental_gpu_hour` alarms rental costs while owned
costs, APIs, workload, calibration, fleet and edge metrics remain computable.

JSON alarm cells have the shape
`{"alarm": [{"input": "prices.rental_gpu_hour", "reason": "missing input"}]}`.
Markdown, CSV and TeX show `ALARM: input: reason` in the cell. Each table also
carries/draws its deduplicated alarm list immediately after its rows. The result
has a deduplicated `alarms` list. The engine never uses a number built on a gap,
even where another factor is zero. Provenance-bearing estimates are valid data;
alarms indicate absence, contract failure or an infeasible declared calculation.

Without `--strict`, partial canonical results exit **0**, with alarms visible.
With `--strict`, any alarm exits **1**, after printing the same results. If no
numeric metric is computable, either mode exits **1**. Presentation labels and
constant mathematical identities do not count as computed numeric evidence.
Invalid CLI/scenario syntax exits **2**, with a clear error and no traceback.
The same strict gate applies to `sources`.

A zero/missing link alarms that offload is impossible; no instant or infinite
transfer time is emitted. Local/API metrics remain available. Empty call mixes
have count zero, but means and per-call costs alarm; a single call is valid.
Zero prices compute zero on complete data. Zero utilization alarms, one is
valid. Missing, corrupt or nonfinite measured inputs alarm at their source.

**Legacy exception:** calc2–9 and sensitivity wrappers run on their complete
historical data and keep byte-identical output. Partial-result alarms apply to
canonical `paper`, `glm`, `service` and `ownership` scenarios; legacy output is not rewritten
to insert alarms.

## Scenarios

| Scenario | Calculation |
|---|---|
| `paper-base` | Qwen3.8-27B, B300 prefill, measured M3 Max curve, six Apple client configurations, call-mix costs, rented/owned GPU alternatives, integer fleets, team equilibrium and edge devices |
| `service-fp8` | Integer warm pools for 10/100/1,000 users, four daily profiles, five GPU tariffs and API/egress comparison, FP8 server |
| `service-quantized` | Default production service, Q4 server weights and INT8/FP8 tensor throughput; Q6/Q8/FP8/NVFP4 overrides |
| `service-bf16-academic` | Labelled academic BF16 reference; L40S placement alarms instead of inventing sharding |
| `owners-economics` | Reviewed r3 reference: team summary, client cap, ownership/residuals, buy/rent, fit, small teams and selling price; retains its historical sparse grid and output-shadow overcharge |
| `crossover-bridge` | calc5 → r3 attribution one assumption at a time, then integer-grid sensitivity and paper corrections |
| `paper-tables-r7` | Four R7 charts: large turns, cold ingestion, hypothetical decode improvements and exact attached architecture formulas; explicit import/evaluation and f32/bf16 state |
| `paper-tables-r6` | Run-6 closed-perimeter integer fleets and turbo overflow, shared Studio utilization, raw decode bandwidth bounds and measured anchors; six additional CSVs |
| `paper-tables` | Run-5 paper charts: measured parallel/pre-fill scaling, full-demand overflow, explicit clients/purchase bases, remote fleets, GLM and deterministic CSVs |
| `owners-paper` | Paper candidate: corrected all-server input-only prefill, dense per-GPU replicas, 8h operator, colocated remote-team ownership, deep client fit, autopilot and hypothetical drain-safe pool |
| `glm-tier2` | Cloud prefill and GLM-5.3-Flash decode on M5 Ultra 256 GB, M3 Ultra 256 GB, two Spark 128 GB machines or two Strix Halo 128 GB machines |
| `hybrid_calc2` | Original v2 performance and economics |
| `hybrid_calc3` | v3 sessions, bandwidth decode, devices, API and company economics |
| `hybrid_calc4` | v4 fleet economics, scale, precision, long contexts, rental and GLM tier 2 |
| `hybrid_calc5_equilibrium` | Both original office-unit policies, team grid and 1–3 regions |
| `hybrid_calc6_edge` | Latest lane version, including section D: phone chips and receive-versus-compute energy |
| `hybrid_calc7_realcalls` | Original full04 call-mix recalibration |
| `hybrid_calc8_business` | Original provider, user-class, subscription and speed calculations |
| `hybrid_calc9_m3max_measured` | Original M3 Max slot fit, prefill curve and offload break-even |
| `sensitivity_host_sample` | Original agents1 host-sample sensitivity |

Historical entry points remain thin wrappers, including the newly imported
calc8 and calc9. They print the exact historical text, including its assumptions:

```bash
python3 calc/hybrid_calc9_m3max_measured.py > .temp/calc9.out
python3 -m hybridcalc run hybrid_calc9_m3max_measured --format legacy > .temp/calc9-cli.out
cmp calc/hybrid_calc9_m3max_measured.out .temp/calc9.out
```

Use `.out` files as independent historical references. Golden tests pin their
SHA-256 identities, so accidentally regenerating a changed reference cannot
silently bless a regression. The old calc3 CSV is a historical snapshot; wrappers
no longer overwrite `equilibrium.csv` as an import/report side effect.

## Input files and units

`hybridcalc/data/` contains `hardware.json`, `models.json`, `prices.json`,
`workload.json`, `sampler.json`, `economics.json`, `service.json`, `measurements.json` and
`scenarios/*.json`. Models describe FLOPs, growing KV, fixed state, weights and
server decode assumptions; hardware describes clients, server units and links.
The independent `contract.json` defines units, numerical types, ranges and the
precision enum. `file-contract.json` declares standard input-file namespaces.

Every numeric input is a quantity, for example:

```json
{
  "bandwidth": {
    "value": 1000000000,
    "unit": "bit/s",
    "provenance": {
      "kind": "estimate",
      "reason": "Nominal 1 Gbit/s WAN; the link's separate goodput factor accounts for overhead."
    }
  }
}
```

Provenance kinds are `fact` (`url`, `access_date` in ISO date format), `measured`
(`package`, 64-character `sha256`) and `estimate` (`reason`, with formula or
rationale). A fact's access date may refer to the repository's historical
research snapshot; it does not imply this offline run fetched that URL.
Results carry a `sources` ledger of quantity paths, values, units and provenance,
and a `files` ledger with actual checked file hashes. `sources` executes the
scenario so the ledger includes inputs used along its calculation branches.
Graph nodes declare exact fields rather than eagerly validating whole sections.
Raw measurement packages are retained verbatim; the reader supplies numeric
units and provenance without rewriting the delivered files.

Model names, device lists, API choices and the fleet's reference client are
scenario data. To add a device, copy a `hardware.clients` or
`hardware.glm_family` entry, set its quantities and provenance, and add its key to
`client_keys` or `family_keys` in a scenario. Existing field contracts apply to
new entry names. `cost_basis` explicitly chooses `owned`, `laptop_premium` or
`full`; renaming a device key does not change its accounting. No Python edit is needed. A new analytical architecture or a
new kind of physical input can require a model/contract extension.

A scenario JSON has `name`, `description`, `kind` (`paper`, `glm`, `service` or `legacy`),
`inputs` (data files merged in order), `model`, `server`, `link`, `api_keys`,
`client_keys`, `family_keys` and `fleet_client` as applicable. Optional
`overrides` contains nested quantity records. A scenario can be supplied as a
file path. Bundled scenarios resolve inputs within bundled data. Custom scenarios
resolve relative files only against their own directory: **no missing local file
falls back to a bundled copy**. Use an explicit `bundle:prices.json` reference
when bundled inputs are intended. A custom input can declare its namespaces:
`{"file": "local-prices.json", "provides": ["prices"]}`. Known standard filenames
have those scopes in `file-contract.json`. Missing/unreadable/malformed scoped
files invalidate earlier values in those namespaces, so a failed override file
cannot revive an earlier price. An unreadable file of unknown scope invalidates
all earlier data conservatively. Later explicitly supplied values can restore
known fields. Other scoped datasets still compute. Reuse bundled scenarios as
examples, prefixing their input references with `bundle:` when copying them. For another measured calibration,
provide matching measurement paths, file SHA-256 hashes and package provenance.

`legacy.json` and `legacy-contract.json` retain historical numerical operands,
with paths such as `legacy.fleet.PEAK16_L61_75`. Keys include the original
symbol, line and column; source expressions and inherited assumptions are in
the provenance reason. `1` denotes a dimensionless mathematical coefficient.
Historical unsupported `[fact]` comments are preserved as documentary context,
but the data ledger conservatively labels inherited values as estimates unless
supported by a measurement record. Historical source hashes are recorded in
`legacy-inventory.json`.

## Calculation semantics

The base prefill roofline uses effective compute calibrated to the measured
M3 Max marginal segment midpoints. It linearly interpolates measured rates,
clamps below the first midpoint and retains the last point's FLOP efficiency
above the last midpoint. The memory roof is bandwidth divided by
`weights / prefill_batch + KV`. Other Apple prefill multipliers are estimates.
Decode calibrates a bandwidth efficiency and batching penalty to the normalized
single/four-stream 32k result, then extrapolates to other depths and hardware.
Neither extrapolation is an additional measurement.

The sampler fits independent calls to full04 aggregates with a fixed seed.
Its sample size, caps, tail approximation and tool delays are data. It keeps the
partial final group. `chunk_calls=116` defines a session **normalization group**,
not an observed sequence of 116 related calls. Output and reasoning fields are
nested for verified Codex/Claude usage: `reasoning_extra_fraction=0` is the paper default;
`1` recreates the historical conservative sum. Capped sampling changes fitted
means; output tables report the actual sampled means.

API billing in the paper scenarios prices cached prefix, uncached delta and
output once. Historical tiered/cache-write bookkeeping is preserved in legacy
scenarios. GPU accounting separately charges prefill, decode and memory
residency, without overlap credit. Hybrid clients include cloud shadow prefill,
egress, device or laptop premium net of residual, estimated active electricity
and amortized DRAM/NVMe session storage. Rental comparisons replace the owned
GPU price at the declared rental utilization. Server power includes PUE, load,
colocation and support. All-server GLM uses calc4's FP8 TP2 memory reservation.

Capacity is constrained by both device time and occupied stream time. Streams
are selected at the declared rate and capacity depths, then reduced for memory
at each sampled call. A below-floor fallback is explicitly marked. If even one
stream cannot fit a call, the row reports its fit share and prices only that
supported subset; its API/own references use exactly the same subset. Default
64 GB Apple rows exclude 0.55% of sampled calls. No unsupported call is counted
as free or silently sent to another provider. Fleet tables size integer server
units and enough pooled decode boxes/pairs for the requested calls/day; grid
crossings are claims about that finite grid only.

For GLM pairs, weights and state are evenly sharded. Sequential pipeline stages
receive no speculative overlap credit, so memory capacity adds while per-token
memory bandwidth does not. Communication seconds per batched step are:

```
2 * (nodes - 1) *
    (latency + streams * hidden_width * activation_bytes * 8 / (link_bit_s * goodput))
```

This estimates one boundary activation and an equal-size feedback message per
stream. Spark assumes 200 Gbit/s ConnectX-7; Strix assumes direct 10GbE with
suitable NICs/PCIe expansion. NIC/driver compatibility, runtime split support,
shard balance and power are unverified estimates. This is a calculation, not an
implemented multi-node inference engine. Hidden width and message precision
are data. Cloud transfer sends each growing delta plus recurrent state to its
owning shards once, with no extra full-state copy on every decode step.

The full05 call-date package is a later corpus snapshot with partial timestamp
coverage. Its dates and counts are displayed separately and never used as the
denominator for full04 costs. See the preserved package reports and
[`ENGINE-REPORT-261030.md`](ENGINE-REPORT-261030.md) for limits.

## Service sizing

With explicit `--set workload.reasoning_extra_fraction=1`, `service-quantized`, `service-fp8` and `service-bf16-academic` recover the historical 196.6926 TFLOP and 66.6704 MB per-call calc8 reference. The current base counts output alone. These are calculated,
not hard-coded constants. The explicit historical profile retains 39,904 calls,
output-only generation and calc8's cache-write/group billing convention (fraction 1 restores the historical upper bound).
It is distinct from the `paper-base` output-only default. Full source custody,
prices and hardware assumptions are in [`SERVICE-SOURCES-261030.md`](SERVICE-SOURCES-261030.md).

Users are 10, 100 or 1,000. Profiles are light 200, medium 800, heavy 2,500 and
measured power user 6,500 calls per active day. Default window: 10 h × 21 days,
target load 70%, independent MFU 30%.

```
GPU_seconds_per_call = derived_FLOPs / (precision_peak_FLOP_s * MFU)
GPUs = max(1, ceil(N * calls_day * GPU_seconds_per_call /
                   (active_hours * 3600 * target_load)))
TB_month = N * calls_day * active_days * derived_download_bytes / 1e12
```

Each per-second option is a **warm pool billed for the whole active window**,
including idle integer headroom. Billing quantum is data; no scale-to-zero or
per-inference-only discount is invented. Monthly Hetzner reservations are paid
for the calendar month. The recurring charge, upfront setup, setup amortization
and first-month cash are shown separately, with the declared EUR→USD rate and
setup horizon. Egress is shown at declared $0/$5/$50 per TB sensitivities and a
separate selected price. API comparisons price precisely the same calls.

`service.precision` selects Q4/Q6/Q8/FP8/NVFP4 (academic BF16 only),
independently of the client transfer format. Q4/Q6/Q8/FP8 use INT8/FP8 tensor
throughput with format-specific weight bytes. NVFP4 uses Blackwell FP4 and is
engine-dependent; unsupported GPUs alarm. Dequantization overhead is absorbed
in the declared MFU. BF16 requires 54 GB for weights alone, so a
48 GB L40S is infeasible in the declared single-GPU model. GPU-seconds arithmetic,
egress and API comparisons still compute; placement counts and costs alarm.
Thus `service-bf16-academic --strict` intentionally exits 1. No sharding or CPU offload
is assumed. The weights/workspace check is a lower bound, not full KV/context
admission or runtime qualification. Koyeb's form factor and several performance
rates remain explicit offline estimates; no state-conversion equivalence is
claimed.

## Owners' economics (run 3)

```bash
python3 -m hybridcalc run owners-economics --format md
python3 -m hybridcalc run owners-economics --format csv > .temp/owner-tables.csv
python3 -m hybridcalc run owners-economics --set owners.client_quant=Q3 owners.client_efficiency=0.37
python3 -m hybridcalc run owners-economics --set owners.server_precision=NVFP4 --format json
python3 -m hybridcalc run owners-economics --set owners.teams.0=1 owners.residuals.0=1
python3 -m hybridcalc sources owners-economics --format json
```

`ownership.json` and `scenarios/owners-economics.json` hold the new assumptions
and selected catalogue keys. Every quantity has unit, provenance and a contract.
Required model/option/benchmark keys are declared by the scenario: deleting an
input cannot silently remove a row. Costs use the full04 calc8 sample (39,904
calls with output-only generation; fraction 1 recovers the historical upper bound), and 116 calls per normalized session.
Legacy scenarios and the earlier `paper-base`/`glm-tier2` calibration analyses
keep their historical model conventions; the owners' new quant/cap decisions
are parameterized in this scenario and quantized service scenarios.

The nine tables expose their input dependencies and preserve independent cells
on gaps, just like the run-2 scenarios:

- Paper summary: team sizes 5–20,000; open shares 20%, 50%, and a labelled 100%
  academic bound. It compares the same open calls; closed-model calls are a
  common excluded cost. Overflow from the Mac goes to the cheapest same-model
  API and is included in the hybrid bill.
- Client capacity: the lesser of device compute/decode capacity and occupied
  stream capacity, using measured prefill, local/remote policy, parallel agents
  and memory at the maximum sampled depth. `served=min(requested,capacity)`;
  excess is always shown. Each Mac retains the client's daily window when a
  server pool spans a global 24-hour window.
- Full ownership: independent server and Mac residual grids at 20% (cheaper
  hardware), 50% (wear) and 80% (scarcity), after four years. The summary charges
  an explicit zero fraction of a new Mac's purchase (existing Mac); this grid
  charges the entire new Studio price and a dedicated office RTX 5090 fleet
  (`owned_hybrid_option` in the scenario). Energy is charged in both.
- Derived equilibrium: first sustained crossover on the supplied finite team
  grid. It does not encode a 500-person answer. Quantization, workload and
  precision can move the crossover or remove it against the cheapest API.
- Selling price: `(GPU + egress + front) / (1-target_margin)` per 1,000 served
  calls, compared with the owner references MiMo $0.83, Chutes $1.61 and Flash
  $3.42. It excludes customer hardware and overflow API calls. The front is an
  explicit $5/person-month estimate; margin 1 alarms.
- Client fit: Macs 36/64/96/128 GB, Q3/Q4, contexts 32k/64k/128k, weights + KV +
  recurrent state + explicit OS/app reserve. Flash-Next shows both RAM and SSD
  n-gram placement (125B total, 6B active, 51B n-gram); SSD lookup latency is an
  estimate, not qualified performance. Non-fit means an alarm, never zero usable
  sessions presented as successful placement.
- Small teams: 5/10/50 people, Qwen27 and GLM, all supplied rental/office options;
  shows resident sessions per Studio, active streams, tok/s/stream and costs per
  normalized session against API and a separately sized owned all-server fleet.
- Buy/rent: all team/share/option combinations, 10h and 24h windows, three
  residual values, integer dedicated warm pools. Net capex divided by positive
  monthly rental-minus-opex gives the crossover in months. Nonpositive saving
  alarms as no recovery. The horizon comparison remains computable.
- Measured anchor: native 16k decode min/mean/max from the pinned normalized
  benchmark. The requested 30–37% parameter is a **calibrated efficiency
  coordinate**, with 0.34 anchored to 8.2555 tok/s. Actual GGUF-byte roofline
  efficiency is 40.96%, shown separately; it must not be called 30–37%. Scaling
  by quant traffic, bandwidth and efficiency is an estimate on other clients.

The summary buys fractional capacity from a **shared prefill service** at its
load target; this makes per-person costs independent of the team size. Dedicated
warm-pool rentals pay for the whole integer reservation in the other tables.
They are different purchasing arrangements, both explicit. New Macs and small
private GPU pools need not beat cheap APIs. The report shows negative savings
as well as positive savings.

Weights use separate precision bytes/parameter; Q4 client sizes reuse actual
GGUF measurements/snapshots, and Q3 scales by the explicit format ratio. Server
Q4/Q6/Q8 use INT8/FP8 arithmetic at the declared MFU; NVFP4 FP4 is Blackwell-only
and engine-dependent. Model fit checks apply to weights plus workspace, with
all-server KV occupancy counted separately. Multi-GPU units assume balanced
sharding with an explicit efficiency estimate. GPU count, price, bandwidth,
MFU, load, front, margin, residual, reserve, agent count and client efficiency
are overridable quantities. Missing or nonfinite values never turn into defaults.

New offline price/source qualifications are recorded in
[`SERVICE-SOURCES-261030.md`](SERVICE-SOURCES-261030.md). H100/L40S/H200 purchase
budgets are new estimates, not quotes. B300 is the calc4 tariff estimate: the
serverless note quotes B200, which is not substituted for B300. Office rent
comparisons use labelled counterfactual proxy tariffs. Canonical Chutes cached
input is corrected from $0.003 to $0.0039/Mtoken per the supplied API note;
legacy golden inputs remain untouched.

The full scenario deliberately requests non-fitting GLM laptops/GPUs, so its
`--strict` exit is **1** even with complete data. Use normal mode to inspect all
tables and alarms. Zero load, invalid quantization and unknown override paths
remain rejection cases. The focused tests delete every new numeric/enum owner
input in an activated configuration and check every previously dependent cell;
other tests cover null/nonfinite/unit/provenance failures, endpoint residuals,
a single person, zero prices, format admission, calibrated capacity and planted
gaps. See the report for exact validation commands and expected-red controls.

## Crossover attribution and late addenda (run 4)

```bash
python3 -m hybridcalc run crossover-bridge --strict --format md
python3 -m hybridcalc sources crossover-bridge --format json
python3 -m hybridcalc run owners-paper --format md
python3 -m hybridcalc run owners-paper --set operations.autopilot_share=1 operations.pool_fill=1
python3 -m hybridcalc run owners-paper --set operations.pool_price=0.75 operations.pool_fill=0.8
python3 -m hybridcalc run owners-paper --set owners.options.colo1.colo_min_month=250
python3 -m hybridcalc run owners-paper --set workload.reasoning_extra_fraction=1 --format json
```

`crossover.py` uses `bridge.json` sufficient statistics extracted from the
frozen calc3/calc5 workload (80 sizing sessions, 200 API sessions), with the
legacy parameter-file checksum and each moment's formula in provenance.
It recomputes costs and fleet ceilings rather than replaying a transcript.
Each ordered step changes one assumption; the effects are nonlinear and
order-dependent at integer fleet thresholds. Both old and new endpoints are
executable tests. Mac incremental cost does not enter an own-cluster/API
comparison. Calc5 already uses FP8 weights/throughput; it does not start at
BF16. Median API token prices are unchanged. The full result and paper
recommendations are in [`ENGINE-REPORT-261030.md`](ENGINE-REPORT-261030.md).

The reviewed r3 sparse-grid 200/200/100 crossovers correspond to integer-sweep
306/123/62 through 20,000 people. Missing intermediate failures matter.
R3 also prefills output **and** charges output decode in all-server mode.
`owners-paper` removes that duplicate prefill; the hybrid still shadows
output so its server copy stays current. Dense server weights/workspace are
reserved separately on every GPU. With an 8h operator day, 70% load target,
measured 34,844 B/token KV and the same conservative calc8 accounting, the
corrected integer thresholds are **612/245/123** at 20%/50%/academic100%.
The paper scenario tests every integer through the largest displayed team;
the table of example team costs still uses the compact team grid.

`operations.json` supplies all new quantities, including the pool price/fill,
autopilot share, drain/job/owner-restore bounds, idle-power fraction, context envelopes and
small-team policy boundary. Colocated 96 GB Server Edition hosts have one or
two GPUs, estimated purchase budgets $36k/$62k and power 0.9/1.8 kW. Space
fees are `max(host minimum, kW * prices.colo)`: the new $100/host-month minimum
is explicitly an estimate; the inherited $190/kW-month comes from the dated
calc4 source. Energy and support are separate. The counterfactual rental
comparison uses $2.20/GPU-hour; it does not guarantee a colocated dual-GPU
provider instance. These are inputs, not quotes or silent zero office fees.
The paper's small-team options exclude offices; the new operating table
allows office boxes only above 100 people. Colocation remains available above
that threshold too. GLM does not fit these small GPU configurations at the
assumed Q4 size/workspace; their costs alarm while API/Mac metrics survive.

The deep-fit table reports raw memory-limited depth for one session, the
separate supported-depth envelope, and resident sessions at 256k, 500k and
1M for every 36/64/96/128 GB Mac, Q3/Q4 and both Flash-Next n-gram placements.
For 27B it uses the measured affine slot geometry: 34,844 B/token plus
156,894,784 B state (156.9 MB rounded). OS/apps remain a declared reserve.
Non-fitting weights/state or requested depths produce alarms, not usable
zero-session results. Memory fit is not runtime/latency qualification.

Autopilot share is a fraction of **fixed total monthly open-model work**:
`(1-a)` runs in the 8h × 21-day operator windows, `a` is uniform across the
730h average calendar month. The table compares a=0 with the selected a
(default 0.5); 0 and 1 are valid. It shows actual owner GPU-hours, peak load,
integer servers, calendar utilisation and warm-rental billing. Automatic
arrivals require a warm lease for the whole calendar month. This is a prefill
service workload comparison; do not add its cost again to the hybrid summary
or infer additional Mac capacity from its change in time distribution.

The pool **does not exist**. Its owner net price and fill rate are estimates.
With no autopilot, guaranteed idle windows are the nights between operator
days and the trailing inactive portion of the average month. Jobs stop being
admitted one guard interval before the next owner window and must finish
within the declared job limit, followed by owner model/state restoration.
Defaults allocate the 15-minute guard to a 12-minute tenant-job bound and
a 3-minute owner-restoration bound. If guard < job limit + restore bound,
the pool calculation alarms; known idle hours, normal ownership/rental and
fit still compute. Admission/sold hours
exclude the entire guard. Incremental drain energy conservatively reserves
the full guard whenever fill > 0; fractional fill is not a bound on the last
job's runtime. Sold plus draining capacity never exceeds owner-idle hours.
Under continuous automatic reservations there are **no guaranteed idle
windows**, so pool revenue is zero even at fill 1. No user fallback or owner
queueing discount is assumed. The zero conflict-hours result is a property
of this analytical schedule, not a deployed-pool availability claim.

The operating study uses linear power accounting: idle power over the calendar
plus incremental owner activity. The summary/residual/small-team tables retain
calc4's fixed 70% energy-duty budget; the crossover bridge holds unit opex
fixed while attributing fleet changes. These are separate sensitivities, so
their costs must not be added or averaged. Pool credit is sale revenue minus incremental work/drain
energy. Effective cost is `(depreciation+owner_opex-net_pool_credit) /
owner_used_GPU_hours`; its denominator is explicitly owner-used hours.
Buy-versus-rent months are net capex divided by rental-minus-opex, with or
without the credit. They are residual-adjusted equivalent recovery months,
not cash-payback dates; values beyond 48 months mean no advantage within the
planned four-year horizon. Terminal resale is not immediate cash. Nonpositive saving alarms as no recovery. Zero prices,
fill and residual endpoints remain valid; negative prices, invalid shares,
nonfinite values, bad schedules and missing quantities do not make numbers
appear. All new quantities have activated missing-data and contract tests.

Source custody and finite evidence are documented in
[`CROSSOVER-SOURCES-261030.md`](CROSSOVER-SOURCES-261030.md). Native Python 3.9,
serving topology and pool implementation remain unqualified. Run 11 uses output alone in current base cases. Muse counter semantics remain unverified; `reasoning_extra_fraction=1` is the explicitly labelled reasoning-on-top upper bound, retaining historical numbers.

## Tables and tests

The calculation API `hybridcalc.engine.run(name, overrides=())` returns tables
with column units, row dictionaries, notes and provenance ledgers. Markdown,
rectangular CSV, JSON and LaTeX booktabs formatters consume these data. Legacy
scenarios additionally expose their exact text and a structured transcript table;
they do not reinterpret every historical prose line as a numeric table.
[`examples/glm-family.tex`](examples/glm-family.tex) is a compact booktabs example;
include it in a document that loads `\usepackage{booktabs}`.

```bash
python3 -m unittest discover -s calc/tests
python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py
```

Tests cover all nine hash-pinned golden outputs, a matching-golden input plant,
roofline and transfer monotonicity, linear pricing, calibration anchors and
normalized batching, pipeline communication, fleet sizing, finite-grid
crossings, data-only device additions, formatters, CLI errors, provenance,
units, ranges, strict legacy overrides, checksum rejection and copied-package
integrity, per-cell alarms, depth/call-count boundaries, source-file isolation,
strict exit codes, precision/memory placement, warm-pool sizing and tariff math.
Each test/group states its claim. Python 3.9 grammar is checked, but native 3.9
and macOS execution were not available in this run. No TeX/PDF build is required
for this calculation-only change. Logs belong in `.temp/`.

| Tool | Purpose | Command | Outputs |
|---|---|---|---|
| Python 3.9+ | Scenario CLI and provenance ledger | `python3 -m hybridcalc list`, `run`, `sources` | stdout; redirect into `.temp/` |
| `unittest` | Golden, invariant, rejection and control tests | `python3 -m unittest discover -s calc/tests` | test report; logs in `.temp/` |
| `compileall` | Syntax/bytecode validation | command above | ignored `__pycache__/`; logs in `.temp/` |
| Legacy wrappers | Exact historical `.out` regeneration | `python3 calc/hybrid_calc4.py` | stdout |
| `sha256sum` | Repository artifact integrity | `sha256sum -c MANIFEST.sha256` | verification report |

## Paper charts (run 5)

Commands below run from the repository root; `--output` is relative to the
current working directory. From `calc/`, use `--output out/paper`.

```bash
python3 -m hybridcalc run paper-tables --format json > .temp/paper-tables.json
python3 -m hybridcalc export paper-tables --output calc/out/paper
python3 -m hybridcalc sources paper-tables --format json
python3 -m hybridcalc run paper-tables --set paper_tables.streams=1 prices.egress=90
python3 -m hybridcalc export paper-tables --output .temp/paper-sensitivity --set workload.reasoning_extra_fraction=1
```

The committed chart inputs are under `out/paper/`. The exporter creates one
CSV per named table, with units/provenance/generation/alarm sidecars. It only
replaces its generated filenames. `--strict` still exits 1 after writing all
outputs when any cell alarms. The default has intentional nonfit/office-policy
alarms; it does not suppress them to manufacture a green strict gate.

| Table ID / CSV basename | Content |
|---|---|
| `person_cost_s20` | Six explicit Macs, existing/purchased premium, five team sizes; all 20% open calls billed |
| `person_cost_s50` | The same at 50% |
| `person_cost_academic_s100` | Separate 100% academic bound |
| `crossover_explanation` | Short independent r4 assumption/crossover/reference-choice table |
| `remote_rent_buy` | H100/L40S/RTX hourly, owned one/two-GPU colo, office exclusions; residual 20/50/80%, 10/24h |
| `client_sessions_day` | Eight clients × 100/300/1000 Mbit/s, local/hybrid sessions per eight-hour day and gain |
| `offload_by_link` | State 32/16 × 100/300/1000/2500 Mbit/s; share and unconditional/conditional time saving |
| `traffic_user_month` | Light/medium/heavy offered and Mac-capped traffic, zero/five/fifty/ninety dollars per TB |
| `glm_long_sessions` | GLM sessions growing to 200k through 1M, six teams, full bought Studio/server costs, spill and ingest |
| `client_fit_deep` | All r4 models, Q4/Q3, 36/64/96/128 GB, one-session reach and 256k/500k/1M residency |

Each CSV includes `status` and `alarm_inputs`. Noncomputable cells are `nan`,
not zero or empty. `alarms.json` gives every table/row/column and root reason;
`schema.json` provides names/units; `sources.json` provides quantity provenance
and measured-file hashes; `manifest.json` hashes the generation and outputs.
Do not substitute `run --format csv` for `export`: the former remains the
human-auditable multi-table formatter with explicit alarm rows. The chart
export keeps numeric columns readable by pgfplots. Filter client/basis rows
for cost series and team rows for GLM series. For example:

```latex
\addplot[restrict expr to domain={\thisrow{team}}{500:500}]
  table[x=context, y=hybrid_session, col sep=comma]
  {calc/out/paper/glm_long_sessions.csv};
```

No paper source is edited by the exporter. IDs and column names are stable;
CSV labels use safe display punctuation; exact originals are in
`schema.json` under `csv_labels`, and ambiguous display-label collisions are
rejected. All CSV rows remain flat/rectangular for pgfplots. Numeric values
retain full precision. Actual `share`, paired depth and tariff columns remain authoritative under
overrides. Verify the generated manifest hashes before consuming results.

The price columns `hybrid_median` and `hybrid_cheapest` both include all
requested calls: shared rental prefill, actual downloads, client energy/front,
selected purchase basis and the respectively priced API spill. Their explicit
`overflow_median`/`overflow_cheapest` columns allow the bill to be checked.
Per-call cache charges are calculated before splitting the mix; expensive
memory-ineligible calls retain their own API prices. `streams` is the anchor
selection; `min_streams`/`max_streams` report actual per-call memory-limited
counts. Existing-Mac acquisition is zero; a bought Studio is full additional
hardware, whereas a bought laptop credits the declared baseline.

The original `owners-economics.hybrid_user` already charged cheapest spill.
It remains unchanged, with new explicit spill/median/cheapest aliases. The
paper tables use the measured 32k single/four-stream anchor instead of the
old ideal-weight-sharing client law. Aggregate gain interpolates the measured
1.665 value, is capped by calibrated bandwidth, and is monotone in available
streams. No fifth stream is extrapolated. Other clients scale decode by
bandwidth, and measured prefill by declared compute/reference compute plus
roofline. M4 compute/purchase price and cross-device efficiency are estimates.

The historical crossover reference keeps its own r4 workload/inputs and
prefixes its ledger with `r4_reference.`; current client overrides do not
rewrite it. It is not a new crossover claim about these measured client rows.
The paper uses output alone for generation, timing and output billing. The explicit reasoning-on-top upper bound retains the old calc8 sum; reasoning is informational in the base.

Remote rent/buy prices full warm windows before a Mac cap, including median
API spill for a server-context nonfit. GLM grows sessions from depth zero by
replaying measured sampled increments; demand defaults to two full sessions
per active day. Every overflow session is priced. Its bought whole-node
server basis can be much more expensive for small teams than APIs. Cold
1M ingest is reported separately and uses one server replica plus one full
KV/state transfer. These are analytical estimates, not a runtime qualification.

See [PAPER-TABLES-SOURCES-261030.md](PAPER-TABLES-SOURCES-261030.md) for exact
provenance, formula choices, unit conventions and limits. New tests in
`tests/test_paper_tables.py` cover each table, every new quantity's gap/contract,
selective spill pricing, measured gain, memory/load monotonicity, ingest
refinement, invalid model/streams and safe deterministic CSV generation.

Optional native CSV/pgfplots smoke (existing cached TeX resources only):

```bash
mkdir -p .temp/pgfplots-smoke
(cd calc/tests && tectonic --only-cached --keep-logs --outdir ../../.temp/pgfplots-smoke paper_tables_smoke.tex)
```

This fixture reads all ten default CSVs, checks row counts and plots the GLM
team filter shown above. It writes only `.temp/`; Python tests/package usage
still require only the standard library. No network resource is fetched.

## Paper charts (run 6)

```bash
python3 -m hybridcalc run paper-tables-r6 --format json
python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper
python3 -m hybridcalc sources paper-tables-r6 --format json
python3 -m hybridcalc run paper-tables-r6 --set owners.residual=0.5 economics.client_residual=0.5
python3 -m hybridcalc export paper-tables-r6 --output .temp/r6-sensitivity --set r6.utilization.users_per_studio.1=3
python3 -m unittest discover -s calc/tests -p test_paper_r6.py
```

| Table / CSV in `calc/out/paper/` | Default rows | Meaning |
| --- | ---: | --- |
| `perimeter_cost.csv` | 918 | All routes, profiles, team sizes, clients and purchase bases; integer candidate fleets and selected eligible option |
| `perimeter_cost_light.csv` | 306 | Exact light-profile subset, 200 calls/person-day |
| `perimeter_cost_medium.csv` | 306 | Exact medium-profile subset, 800 calls/person-day |
| `perimeter_cost_heavy.csv` | 306 | Exact heavy-profile subset, 2,500 calls/person-day |
| `glm_utilization.csv` | 48 | 200k/1M, teams 50/500/5000, 1/2 users per Studio, 1/2/4 sessions or full Studio utilization |
| `decode_scaling.csv` | 42 | 40 raw bandwidth bounds and two separately labelled measured M3 Max 32k anchors |

`r6_schema.json`, `r6_sources.json`, `r6_alarms.json` and `r6_manifest.json`
are the run-6 audit sidecars. Run-5 sidecars and all ten prior CSVs coexist and
are preserved by the run-6 export. Verify `r6_manifest.json.files` and generator
hashes before plotting. Alarm cells use `nan`, `status=alarm`, `alarm_inputs`;
full reasons live in `r6_alarms.json`. The default has six expected alarms in
`decode_scaling.aggregate_tok_s`: 64 GB cannot fit K=16 at 64k, or K=8/16 at
128k, for either bandwidth family. The raw theoretical bound is still numeric.
Ordinary runs exit 0; `--strict` exits 1 after producing the same outputs.

The input layer is `hybridcalc/data/paper-tables-r6.json`; it uses the same
quantity/unit/provenance format and contracts as every other canonical scenario.
The scenario composes previous measured workload/hardware/economics layers,
sets `owners.hours=8`, and adds owner chart grids and rack-policy inputs. Arrays
are overrideable by index; unknown paths are errors. A missing input alarms
only its declared dependent cells. Legacy wrappers still use complete historical
data and retain their exact output.

**Closed perimeter.** Share 100% is real here. No call reaches an API or external
prefill service. `client_served_day + turbo_day + unserved_day = requested_day`;
Mac-only unserved calls stay unserved. All-server and hybrid routes serve the
whole request on owned infrastructure. `client_served_share` and
`client_capacity_day` refer specifically to the client, so all-server rows use
zero for them. Mean waits include the declared internal RTT for server routes and exclude
queues. The
`p90_scope` column distinguishes all-server all-call p90 from the client-served
subset. Local prefill scales the measured M3 curve by each client's compute
ratio and applies the memory roofline. Capacity retains R5's explicitly estimated
measured-anchor decode interpolation; it is not a new parallel measurement.

Small `rack1`/`rack2` 1/2-GPU RTX PRO 6000 hosts are inside an owned rack, with
an explicit `closed_perimeter_own_rack` office-policy exception. Space is a
provenance-bearing sunk zero (`owners.office_colo`), with office energy/support.
B300 uses internal datacenter budget inputs. Small hosts are eligible through
100 users, B300 from the declared overlap of 50; comparison-only rows remain
visible. For a cost chart filter `selected=1`, route, client and basis. This
chooses the cheapest eligible **whole fleet**, including overlap candidates.
Mac-only rows do not guarantee service of all calls; plot their served share too.

Hybrid overflow is benchmarked at `all_server_call`; `turbo_reference_month`
is overflow/day × active days × that cost. Prefill and turbo share an actual
integer fleet. `fleet_adjustment_month` reconciles that fleet's budget with the
prefill and turbo reference allocations, and may be negative when sharing saves
a node. `person_month` always pays the actual owned fleet, client energy,
frontend and residual-adjusted premium (or zero acquisition on already-owned
Macs), using the owners-paper 20% residual for both servers and premiums.
It never prices overflow at zero or at an outside API. See
[PAPER-R6-SOURCES-261030.md](PAPER-R6-SOURCES-261030.md) for custody and limits.

**Studio occupancy.** `studios=ceil(team/users_per_studio)` and total client
capacity is Studios × capacity per Studio. Fixed demand remains per person;
capacity mode saturates that exact fleet, including odd team sizes. Prices
are per **requested** session and include API overflow beyond Studio capacity,
retaining run 5; this table is separate from the perimeter case. Increased
sharing never multiplies a physical Studio's aggregate capacity. Frontend is
per user, hardware amortization is per purchased Studio. The 1M default remains
6.732123 sessions/Studio-day and $148.756458/device-month.

**Decode bounds.** Q4 is fixed in this chart by `r6.decode.client_quant`, while
other tables retain adjustable client quantization. q8_0 uses serialized KV
34,816 B/token in the bandwidth formula, and measured resident slot geometry
34,844 B/token + 156,894,784 B/session for fit:

```text
aggregate_bound = K * bandwidth / (weights + K * (depth * wire_KV + 2 * state))
fits = weights + reserve + K * (depth * resident_KV + state) <= memory
```

There is no efficiency calibration for the 64k/128k or new-K bounds. Measured
rows are only M3 Max 32k single 8.440947 tok/s and four-stream aggregate
14.054306 tok/s (maximum-decode-interval convention, not request wall throughput).
Do not treat a bound as a speed prediction; actual 64k/128k 1/2/4/8-stream
measurements are pending. Native optional import smoke uses the cached tool,
without making it an engine dependency:

```bash
cd calc/tests
tectonic --only-cached --outdir ../../.temp/hybrid-calc-r6-261030/pgfplots paper_r6_smoke.tex
```

## Paper charts (run 7)

```bash
python3 -m hybridcalc run paper-tables-r7 --format json
python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper
python3 -m hybridcalc sources paper-tables-r7 --format json
python3 -m hybridcalc run paper-tables-r7 --set r7.import_fixed_s=0.5 r7.goodput=0.9 r7.latency=0.02
python3 -m hybridcalc run paper-tables-r7 --set r7.decode.scales.3=2.2
python3 -m unittest discover -s calc/tests -p test_paper_r7.py
```

| Table / CSV under `calc/out/paper/` | Rows | Meaning |
| --- | ---: | --- |
| `turn_speedup.csv` | 48 | 2k/10k portions, 100k/200k depths, six links, f32/bf16 state |
| `oneshot_ingest.csv` | 36 | 100k/200k/262k cold loads from zero, six links, both states |
| `decode_sensitivity.csv` | 32 | Two clients, two links, four requested decode factors, both states |
| `arch_compare.csv` | 8 | Four models, exact attached-script f32 formulas and labelled bf16 extension |

Exactly these four tables are new. `r7_schema.json`, `r7_sources.json`,
`r7_alarms.json` and `r7_manifest.json` coexist with prior CSVs and sidecars.
The input layer/scenario use the existing quantity/unit/provenance format;
unknown override paths are errors, missing/invalid values alarm their dependent
cells. Dependencies are explicit in structured results. CSV `nan` is an alarm,
never zero; `alarm_inputs` and the alarm sidecar identify its source.

**Turn and one-shot timing:** measured M3 marginal prefill curve integrated over
the complete token span; one B300 at the existing default 1.35 PFLOP/s effective
compute. Full memory/context admission applies. Q4/q8_0 uses measured resident
34,844 B/token and 156,894,784 B f32 state; bf16 is an estimate at half the state
bytes. No KV halving is assumed. Components are exposed:

```text
hybrid = server_prefill + transfer + import + last_token_evaluation
transfer = RTT + (portion * measured_KV + state) * 8 / (bandwidth * goodput)
import = copies * payload / (client_bandwidth * import_efficiency) + fixed_s
```

For one-shot load, portion is the full context. Default line-rate goodput 1 and
RTT 0 are explicit inputs. Import is unmeasured: one serial copy at 10% nominal
memory bandwidth (40 GB/s on M3), fixed overhead zero. Filesystem slot restore
measurements do not establish delta import. One final-depth single-stream
decode-equivalent token is charged after import as an estimate, conservatively
in addition to the full payload. No model cold-start or queue cost is measured.
The local curve is clamped below its first midpoint and extrapolated at constant
FLOP efficiency beyond the last; the integration step is a refinement-tested
256 tokens. Timing spans cannot exceed the measured 262,144 context limit.
Speedup is local/hybrid: values below one favor local prefill.

**Decode:** factor 1 is anchored to the M3 single/four-stream measurement at 32k;
factors 1.5/2/3 are hypothetical engine improvements. M5 Max 64 GB and bf16 state
speed effects are estimates. The four-stream anchor gain stays 1.665015442.
Requested algebraic rates are shown, but capacity alarms if the implied
unchanged-traffic bandwidth efficiency exceeds one: default factor 3 is not
physically admissible. Factors 1–2 compute; nothing is silently clipped. The
sampled supported mix uses R5 marginal per-call prefill, adding import/evaluation
to remote steps and retaining the estimated 1M modeling envelope beyond measured
262k. `fit_share`, actual stream range, hours and group length are explicit;
sessions/day is calls/day divided by the 116-call normalization group, not a
measured calendar session count. This does not alter the R6 bounds-only table.

**Architecture reproduction:** every original numeric f32 field matches the
attached script, executed independently from a test fixture. It uses config
q8_0 layout (Qwen 34,816 B/token), not the measured slot slope. The approximate
131k reference is the hash-checked 41.2 tok/s segment, actual midpoint 131,448.
It retains the script's rounded 27.8B Qwen FLOP reference. Savings omit server,
import and last-token cost exactly as attached; this is a different accounting
basis from the timing charts. Config inputs identify HF URLs and the offline
owner snapshot, with no new web validation. Original field names retain nominal
1k/10k/131k/262k labels; coordinate/link columns expose actual override values.

The original Qwen3-32B 131k extrapolation stays numeric with
`within_context_131k=0`. Unsupported 262k values are alarms where the script wrote
None. Bf16 rows halve only recurrent state; sliding-window KV is unchanged.
Default has **28 alarm cells**: 24 capacity/gain cells in eight factor 3 rows,
and four unsupported 262k architecture cells. Ordinary run/export exits 0;
`--strict` exits 1 after the same outputs. Full reasons are in `r7_alarms.json`.
See [PAPER-R7-SOURCES-261030.md](PAPER-R7-SOURCES-261030.md) for custody and limits.

Optional native cached-only CSV smoke (after creating the output directory):

```bash
cd calc/tests
tectonic --only-cached --outdir ../../.temp/hybrid-calc-r7-261030/pgfplots paper_r7_smoke.tex
```


## Paper charts, run 8

Run 8 supersedes the sample-based numbers in the run-5/6/7 publication CSVs.
Regenerate all four families together; their audit manifests record exact
Python/data hashes and payload hashes. No network or installation is needed.

```bash
python3 -m hybridcalc export paper-tables --output calc/out/paper
python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper
python3 -m hybridcalc sources paper-tables-r8 --format json
python3 -m hybridcalc run paper-tables-r8 --set hosting.tiers.RAM.price=null --strict
python3 -m unittest discover -s calc/tests
python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py
```

| Table | CSV under `calc/out/paper/` | Basis |
| --- | --- | --- |
| reasoning_on_top_sensitivity | `reasoning_on_top_sensitivity.csv` | M3 Max/M5 Max 64, shares 20/50%, both purchase bases, team 50; fractions0/1 in separate dependency/source scopes |
| people_per_gpu | `people_per_gpu.csv` | One RTX PRO 6000 or B300, heavy offered demand at 20/50/100%, integer people rounded down; compute-only and paid migration bounds |
| transcript_example | `transcript_example.csv` | Cold 70k ingest, one 3k summary, M3/M5 Max 64/M5 Air 32 at 200M/1G; one stream, explicit reserve and all TTFT components |
| flop_per_byte | `flop_per_byte.csv` | Six models,110k/1M where configured,1k portions, three client peak envelopes and three links |

The four new tables have `r8_schema.json`, `r8_sources.json`, `r8_alarms.json`
and `r8_manifest.json`. Ordinary export is 0; strict is 1 because unsupported
architecture depths deliberately alarm. CSV alarms are `nan`, never zero.
The report links the complete old/new publication-cell ledger.

**Sampler.** `sampler.mode=measured_tail` is explicitly selected in current
paper-table scenarios. A stratified aggregate fit matches all-agent token-mass
tails at 2k/5k/10k/30k and depth-conditioned new-token means, rather than treating
a clipped lognormal as measured. The global depth/new/output/reasoning means
and six depth quantiles are retained on the full 39,904-call sample. The stated
1984/690 depth-bin means are Claude-only; pooled means are 1864/729. Low
quantiles, tail shares and bin means are read from hash-checked `stats.json`.
Fit controls/support/quantile coordinates are inputs with provenance; infeasible
fits alarm. Samples below the declared 4096-call calibration threshold are
finite-sample approximations; they are useful tests, not publication estimates.
This is still a synthetic marginal mix, not a recovered chronology or proof of
unmeasured correlations. `legacy_lognormal` remains explicitly available for
frozen historical comparisons, including crossover references; legacy wrappers
still run complete data and reproduce their original bytes.

**Server copies.** Every client-served input and decoded output is shadowed,
including locally read portions. `hosting.json` declares a storage tier
(HBM/RAM/NVMe), USD/decimal-GB-month, retained sessions/person, month fraction
and effective PCIe/tier bandwidth per replica. The default estimate retains
four sessions/person for a full month in RAM at$0.50/GB-month,50GB/s PCIe and
100GB/s RAM. It is an incremental pool budget, not a quoted RAM rental tariff.
Each cold-tier call reloads `(depth*KV+state)/min(PCIe,tier bandwidth)` and
spills `((depth+new+output)*KV+state)/min(...)`. Empty prefixes have no reload.
Both foreground and background shadow migrations are conservatively billed as
occupied GPU time; only offloaded reload is on the foreground critical path.
Background shadow is assumed ready by the next call. HBM has no PCIe migration,
but has its explicitly priced residency budget. Storage scales from mean
end-of-call bytes times retained sessions, not from 116-call normalization groups.

Person charts expose `compute_month`, `hosting_month`, `storage_month`,
`migration_month`, `compute_per_call` and `hosting_per_call`;
`gpu_month=compute_month+hosting_month`. Migration time is reserved in owned
perimeter/GLM/remote fleets and storage is paid separately. Remote rent/buy
shows per-call compute/migration plus storage/team-month. No external API is
introduced into the perimeter path. Standalone existing-prefix turns expose
`server_reload_s`; cold one-shot/transcript loads have no prefix to reload.

**Sensitivity and examples.** `reasoning_extra_fraction=0` is the output-only base; fraction 1 is the labelled reasoning-on-top upper bound. Codex/Claude usage includes reasoning inside output; Muse follows that convention unverified. The transcript decodes exactly 3000 requested summary tokens once,
without adding a second reasoning allowance. M5 curves scale the measured M3
curve by declared compute and decode by bandwidth; estimates are labelled.
The Air example uses an explicit 8GB appliance reserve: changing it to the
standard 12GB developer reserve raises a fit alarm. No Air benchmark is claimed.
FLOP/byte includes fixed delta overhead at 1k; a ratio above 1 compares transfer
with an ideal client peak compute bound only. Server work/import, memory
placement, scheduling and engine quality remain outside that bound. Unsupported
model contexts alarm; the existing Qwen1M engine envelope remains unqualified.

Inputs are ordinary quantity objects, for example:

```json
{"value": 0.5, "unit": "USD/GB/month", "provenance": {
  "kind": "estimate", "reason": "Incremental RAM pool budget; replace with a provider or owned-storage quote."}}
```

Missing/invalid quantities propagate only to declared consumers. A missing
hosting price leaves client capacity, compute-only costs and unrelated example
tables unchanged. A missing PCIe input alarms cold-tier consumers; HBM does not
read it. Every new quantity has deletion and contract/corner tests. Review
regressions were observed red on the original implementation before the fixes;
bounded controls live in `tests/r8_controls.py` (an intended AssertionError exits 1).
Optional native reader check, after creating the output directory:

```bash
cd calc/tests
tectonic --only-cached --outdir ../../.temp/hybrid-calc-r8-261030/pgfplots paper_r8_smoke.tex
```

Source custody and the new estimate boundaries are recorded in [PAPER-R8-SOURCES-261030.md](PAPER-R8-SOURCES-261030.md). The signed local R8 review candidate passed 210 tests (including all nine legacy goldens); exact commands, diagnostic failures and narrowing controls are in the report.

In `people_per_gpu`, share 1 is the academic full-open bound; the closed-perimeter family separately treats 100% as its real policy case.


## Protocol hosting, run 9

Run 9 supersedes the run-8 hosting equations and costs above. The accepted
measured-tail sampler, full input/output shadow, output-only sensitivity,
transcript timing and compute-only users/GPU remain. KV for old positions is
immutable: every flush appends only `(new+decoded)*KV` and overwrites recurrent
state. Reload still reads `depth*KV+state`. The old full-slot spill exists only
in the regression control, never as a published input policy.

Two cases use the same row coordinates and complete demand bills:

| Case | `hosting.catch_up` | `hosting.retention` | CSV convention |
| --- | --- | --- | --- |
| design (paper default) | `at_offload` | `tiered` | Existing table filenames |
| conservative | `per_call` | `ram_month` | Parallel `*_conservative.csv` files |

The policies are enum quantities with provenance in `hosting.json` and
`hosting-conservative.json`. They are ordinary override inputs, for example:

```bash
python3 -m hybridcalc run paper-tables --set hosting.catch_up=per_call hosting.retention=ram_month
python3 -m hybridcalc export paper-tables --output calc/out/paper
python3 -m hybridcalc export paper-tables-conservative --output calc/out/paper
python3 -m hybridcalc export paper-tables-r6 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r6-conservative --output calc/out/paper
python3 -m hybridcalc export paper-tables-r7 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r7-conservative --output calc/out/paper
python3 -m hybridcalc export paper-tables-r8 --output calc/out/paper
python3 -m hybridcalc export paper-tables-r8-conservative --output calc/out/paper
```

Conservative scenarios export only tables with a hosting dependency. Independent
transcript, architecture, fit, historical crossover and raw decode-bound tables
are shared. Case-specific schema/source/alarm/manifest sidecars use
`conservative_`, `r6_conservative_`, `r7_conservative_` and `r8_conservative_`
prefixes. Existing sidecars continue to describe the design case. An unknown
policy or missing input alarms its actual consumers; it cannot select a free
fallback. Enum overrides retain their original provenance and audit trail.

**Catch-up.** Offload opportunities are an exchangeable-call estimate, not a
reconstructed session trace. Given offload fraction `p`, expected consecutive
local calls before offload is `(1-p)/p`. Expected pending seconds per offload is
`(sum(local input+output work) + sum(previous offloaded output work))/offload_count`.
This pending compute is added to foreground server time before comparing local
and remote prefill. Starting from the optimistic zero-pending offload set, calls
that no longer win are removed until stable. Removal only increases pending
work; the process terminates after at most the finite number of candidate calls.
No offloads means no foreground pending cost or division by zero: all journal
work is caught up at day end. Every input/output token is still charged exactly
once in the full-shadow compute bill; pending is a latency placement, not an
additional compute charge. This stationary mean-run latency approximation does
not recover finite-day/session order or a latency distribution.

Each active session-day reserves one extra terminal reload/state overwrite.
Thus design reloads/day = offloaded calls/day + active session-days, versus
one reload per call in the conservative case. For Qwen planning, calls are
spread across up to the retained four sessions/person (`min(calls_day,4)`). GLM
uses the actual served long sessions/day, capped by retained slots. The one
terminal catch-up budget also covers the last decoded output. Spill KV bytes
sum over every new/decoded position exactly once; recurrent overwrites occur
only at catch-up flushes. Foreground and tail I/O are conservatively occupied
GPU time. Hot-cache/overlap savings are not invented. People/GPU uses the named
`people_reference_client` M5 Max 64 and the declared WAN link for routing, with
uncapped offered demand; its accepted compute-only columns remain independent.

**Retention.** Design storage/person-month is mean retained bytes times copies,
month fraction and `[active*RAM_price+(1-active)*NVMe_price]`, where
`active=hours*workdays/month_hours`. Default is 8*21/730; remote rent/buy uses each
row's10h or 24h, not the 8h paper default. Active windows exceeding calendar hours
alarm. Four retained copies/person and tier prices remain explicit estimates,
not protocol requirements. One NVMe-to-RAM promotion per retained session-day is
background I/O at the declared storage bandwidth; it consumes no GPU time and
is exposed separately. Missing promotion bandwidth can alarm that diagnostic
without corrupting storage cost, GPU bills or client capacity. RAM-only does
not read unused NVMe price/bandwidth.

Person tables expose compute/storage/migration month costs, foreground/background
reload, variable spill, terminal-flush seconds/day, reload count/day, promotion
seconds/day and expected pending calls/compute. `gpu_month` still reconciles
compute+storage+migration. Owned fleets reserve variable I/O plus the daily-tail
budget; no external route was added to the perimeter.

**Intensity.** `flop_per_byte.csv` has four portion/format combinations from
`r8.portion`, `r9.large_portion` and `r9.state_bits`. Qwen fixed f32 state is
156894784B and bf16 estimate 78447392B; KV remains q8_0. Flash-Next/GLM inherited
run-8 wire states were already bf16: their new f32 rows explicitly double/use
the resident f32 state, and their 16-bit rows preserve the old wire geometry.
Nonrecurrent models retain zero fixed state in both formats. Unsupported
contexts still alarm; a ratio is only an ideal peak/link bound, not full latency.

Run `python3 -m unittest discover -s calc/tests` and
`python3 -m compileall -q calc/hybridcalc calc/tests hybridcalc.py`.
`tests/test_run9.py` states protocol, accounting, policy-gap, window and chart
claims; `tests/r9_controls.py` contains bounded full-slot/free-pending/no-tail/
RAM-forever mutants (expected AssertionError exit 1, setup error 2, survivor 0).
The updated report records exact commands, statuses, old/design/conservative
headlines and the unchanged nine legacy goldens. All publication payloads have
auditable generation hashes. No network or installation is needed.

Run-9 source custody: [PAPER-R9-SOURCES-261030.md](PAPER-R9-SOURCES-261030.md). Final validation passed 226 tests, retaining all nine byte-identical legacy goldens. Full comparisons and exact exits are in the report. Optional cached-only all 42-table reader: from `calc/tests`, run `tectonic --only-cached --outdir ../../.temp/hybrid-calc-r9-261030/pgfplots paper_r9_smoke.tex` after creating the output directory.


## Paper team grid, run 10

The paper grid is now 5, 10, **20**, 50, 500, 5000 people; the new point is an
estimate requested by the owner on 2026-10-31 for the small-team own-server case.
Re-export with the same eight default/conservative commands in the run-9 section.
All previous CSV record bytes and their relative order are preserved. Audit offline
against pinned R9 commit `e9db8129887126ca6a5d27066dd4f4519d223c2d`:

```bash
python3 calc/tests/r10_controls.py --diff calc/ENGINE-DIFF-R10-261031.csv --added calc/ENGINE-CHANGES-R10-261031.csv
python3 -m unittest discover -s calc/tests
python3 -m unittest discover -s calc/tests -p test_golden.py
```

The Python audit reads the baseline with local `git ls-tree` / `git show` when that
commit is present. The public repository starts from a single publication commit, so
the R9 and R10 paper CSVs are also kept in `calc/tests/data/history/paper-csv-history.tar.gz`,
recorded file by file in `paper-csv-history.json` (git blob id, SHA-256, size); without the
commits the audit reads that archive and refuses any byte that does not match the record.
Git reads run with `GIT_NO_LAZY_FETCH=1` and an empty `GIT_ALLOW_PROTOCOL`, and git is used only
when the commit and every paper CSV blob are already local, so a partial clone never fetches.
It performs no network operation. `ENGINE-DIFF-R10-261031.csv` counts removed,
changed and added records for every published CSV. `ENGINE-CHANGES-R10-261031.csv`
contains only added records, with file, identity key and exact CSV record bytes
encoded in a CSV cell (including its trailing newline). The team-5 planted-cost
control in `test_run10.py` exercises the same byte gate on a real published row.
Logs live under `.temp/hybrid-calc-r10-261031/`. No build is required for this run;
optional TeX smoke fixtures have updated row counts but were not compiled.
See the [R10 report](ENGINE-REPORT-261030.md#run-10-small-team-own-server-grid)
for side-by-side selected all-server and B300 costs and alarm bounds.

## Run 11: output already includes reasoning

Current nonlegacy base scenarios count `output_per_call` alone for client and server decode, API output billing and timing. Reasoning remains informational. Owner-supplied logs establish nesting for Codex (126/126 events) and Claude Code (4,577/4,577 records), 93% of 1,528,194 calls; Muse is treated the same way, unverified. Provenance records the evidence, without claiming a new log audit. The sampler preserves its joint depth/new-token fit and all random draws.

`reasoning_on_top_sensitivity.csv` and its conservative counterpart replace `output_only_sensitivity*.csv`. `accounting_case=base_output` is fraction 0; `reasoning_on_top_upper_bound` is fraction 1, which recovers run-10 numbers. Conservative here describes hosting, independently of output accounting. Regenerate all eight cases using the commands above.

Run `python3 -m unittest discover -s calc/tests -p test_run11.py`; `python3 calc/tests/r11_controls.py output_sum` must exit **1**, with the named output-mean assertion. The ordinary suite must exit **0**. Run `python3 calc/tests/r11_audit.py` for the complete run-10-to-run-11 publication-cell ledger and headline replacements; outputs are `ENGINE-CHANGES-R11-261101.csv` and `ENGINE-QUOTES-R11-261101.csv`. No TeX/build command is needed.
