# Offline service-sizing inputs — 2026-10-30

> Run11 accounting correction: current nonlegacy base scenarios use output alone (mean511.9); reasoning is informational. Provider evidence and Muse's unverified treatment are recorded in workload provenance and [the Run11 report](ENGINE-REPORT-261030.md#run-11-output-includes-reasoning). Earlier summed numerical examples below are historical and recoverable with explicit fraction1; the separately historical crossover bridge and legacy transcripts remain unchanged.

No URL was fetched in this run. Prices and citations below are transcribed from
the supplied lane research; every numerical engine input has its own provenance
in `hybridcalc/data/service.json` or the reused model/workload/price files.

| Read-only source | Observed SHA-256 |
|---|---|
| `/home/agent/lanes/hybrid/.temp/research/serverless-gpu-prefill-2026-10.md` | `c6f80c99361ef7d849e2fad857b6e93011c2166381aa2b620ba50862dd9bccbc` |
| `/home/agent/lanes/hybrid/.temp/research/service-sizing-2026-10.py` | `c901134c6435c9bb487e1f1d91500bcb18ce69e74b05f78736dce647486ebb5c` |

The research note records access on 2026-10-30, 14:30–15:00 UTC. These are
historical list prices excluding tax, not fresh quotes or capacity guarantees.

| Option | Tariff in note §2/§5 | Source IDs and URLs | Engine billing |
|---|---|---|---|
| RunPod Secure H100 SXM | $3.99/GPU-hour | R7 [RunPod pricing](https://www.runpod.io/pricing), R8 [Pod billing](https://docs.runpod.io/pods/pricing) | Per-second granularity; whole active window |
| RunPod Secure H100 PCIe | $2.89/GPU-hour | R7/R8, same URLs | Per-second granularity; whole active window |
| RunPod Secure L40S | $1.09/GPU-hour | R7/R8, same URLs | Per-second granularity; whole active window |
| Koyeb H100 | $2.50/instance-hour | K1 [Koyeb pricing](https://www.koyeb.com/pricing) | Includes host resources; warm for whole active window |
| Hetzner GEX63, RTX PRO 6000 Max-Q 96 GB | €999/month and €999 setup | H1 [Hetzner GPU matrix](https://www.hetzner.com/dedicated-rootserver/matrix-gpu/) | Whole calendar month; setup shown upfront and amortized over an explicit 12-month horizon |
| EUR conversion | 1 EUR = 1.1130 USD, 2026-10-29 | E1 [ECB daily rates](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml) | Convert monthly and setup charges separately |

Warm-pool billing is an explicit scenario assumption from the ad-hoc sizing
script. The engine does not multiply tariff by busy GPU seconds only. Integer
headroom remains paid during all 10 active hours × 21 days. On-demand setup is
explicitly zero **as an estimate input**, not an omitted/defaulted charge.

## Hardware and precision estimates

| GPU envelope | Dense FP8 TFLOP/s | Dense BF16 TFLOP/s | Memory | Qualification |
|---|---:|---:|---:|---|
| H100 SXM | 1,979 | 989.5 | 80 GB | Rates from supplied sizing note; [BW1 NVIDIA](https://www.nvidia.com/en-us/data-center/h100/) |
| H100 PCIe | 1,513 | 756.5 | 80 GB | Explicit nominal estimate, not numerically verified in the supplied note; half the sparse vendor tensor headline |
| L40S | 724 | 362 | 48 GB | Note §5 quotes 362 dense BF16 using [BW2 NVIDIA](https://www.nvidia.com/en-us/data-center/l40s/); FP8 is the explicit 2× estimate |
| Koyeb H100 | 1,979 | 989.5 | 80 GB | Explicit estimate using SXM envelope; provider form factor is unspecified in the supplied note |
| RTX PRO 6000 Max-Q | 877.9 | 438.9 | 96 GB | Existing `data/research/hardware-2026-10.md`, [NVIDIA whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |

MFU defaults to the declared 30% calc4/calc8 estimate. It is independent of the
70% active-window load target. FP8/BF16 changes server compute and server weight
memory; the client's q8 KV and bf16 recurrent transfer representation remain
separately declared. No state-format or output-quality equivalence is proven.

Weights are 27B × 1 or 2 bytes/parameter. The explicit 8 GB workspace input is a
weights/workspace lower bound, not a full KV/context admission model. BF16's
54 GB weights already exceed the L40S's 48 GB: its deployment-dependent GPU
counts/costs alarm. Arithmetic GPU-seconds and egress/API comparisons still
compute. No TP2, CPU offload, or fabricated effective memory is assumed.

## Workload and profiles

The engine samples the same 39,904-call prefix as calc8, with seed 5 and the
historical explicit output-plus-reasoning assumption. Its FLOP mean is derived
as `mean((new + decoded) * F(depth))`; there is no 196.69 TFLOP constant.
Download volume is derived with the declared calc8 M5 Max/1G/B300 admission
policy; there is no 67 MB constant. The results round to those ad-hoc values.

The reference uses calc3's 32,768 B/token KV, 78,446,592 B bf16 state,
19.89648 TFLOP/s effective client prefill, 1.35 PFLOP/s reference server, 90%
link goodput and 0.4 s fixed overhead. These are inherited estimates with
formulas in their quantity provenance. This admission policy fixes the call
mix while comparing SKU/precision compute costs; it is not reoptimized for
each GPU. All new and generated tokens are shadow-prefilled regardless of
whether the reference policy transfers a particular delta.

User counts are 10, 100 and 1,000. Daily profiles are calc8's light 200, medium
800 and heavy 2,500, plus the requested rounded measured power-user profile
6,500. Full05 aggregates imply approximately 6,559 calls per distinct UTC day;
6,500 is a profile estimate, not a guaranteed instantaneous arrival rate.

API references reuse calc3/calc8's Flash and 27B median tariffs, including
cache-write charges on prior output inside explicit 116-call groups. They use
the same sampled calls as service demand. Group order is a model convention,
not reconstructed measured session order. The conservative reasoning sum does
not prove usage fields are disjoint. Full05 counts never normalize full04 costs.

## Run 3: quantization and ownership extensions

`service-quantized` is the production default (Q4). `service-fp8` remains an
explicit quantized sensitivity. BF16 was renamed `service-bf16-academic`.
Q4/Q6/Q8 use INT8/FP8 tensor arithmetic; memory uses 0.5625/0.8125/1.0625
bytes per parameter, including estimated block metadata. FP8 uses one byte.
NVFP4 uses 0.5625 bytes and estimated 2× FP8 Blackwell throughput; support is
engine-dependent. It alarms on the non-Blackwell options. MFU includes unknown
dequantization costs; these are model envelopes, not achieved GPU benchmarks.

The owners' scenario has a separate `ownership.json` catalogue. Its tariff
transcriptions are $3.99 H100 SXM and $1.09 L40S (R7/R8 above), $2.20 RTX PRO
6000 and $3.00 per H200 (K1 above). The two-H200 unit costs 2×$3.00; it assumes
co-location and sharding, which that pair of single-GPU tariffs does **not**
guarantee. B300 is calc4's $9.50/GPU-hour estimate, not a tariff from the
serverless note (which quotes B200). Its eight-GPU node is $76/hour. Per-second
rentals are billed for the complete active window in dedicated-team tables.

Office 5090 / single RTX PRO 6000 / four RTX PRO 6000 capex is the calc4
$11,500 / $30,000 / $103,000, with 0.8 / 0.9 / 3.2 kW power envelopes.
The $660,000 B300 node and 14.5 kW are also calc4 estimates. Buying an
individual B300 allocates 1/8 of the node acquisition and power budgets;
this is not a standalone vendor quote. H100 $40,000, L40S $15,000 and the
H200 pair $80,000 are **new hypothetical acquisition budgets including host**;
the supplied note contains rental prices, not purchase quotes. Office rent
comparators are explicit proxy tariffs for the closest memory class, not
market offers for the named boxes. Their limitations are kept in provenance.

Multi-GPU service units use `GPUs * dense_peak * MFU * shard_efficiency`, with
0.9 sharding efficiency except the inherited eight-GPU B300 envelope at 1.
This is an estimate of communication/imbalance loss, not topology qualification.
Weight memory is checked against balanced pooled HBM. All-server costs also
sum batched decode bandwidth demand and KV/state occupancy in free HBM.
No overlap speedup is credited. Nominal HBM bandwidth, memory and power for
new options remain explicitly marked estimates, pending device/runtime checks.

The summary uses shared-service fractional rental capacity at 70% target load;
buy/rent and small-team tables instead provision whole warm GPUs/units. The
owned residual grid buys office 5090 prefill boxes and full Mac Studios; the
all-server comparator buys complete eight-GPU B300 nodes. All closed-model
traffic is excluded as a common cost. Capped local overflow is charged at the
cheapest same-model API, with the same workload distribution assumed for it.

The supplied API note and `NOTES.md` identify Chutes cached input at
$0.0039/Mtoken. The earlier canonical quantity was $0.003; run 3 corrects it.
This gives about $1.615/1,000 calls on the engine's calc8 mix, distinct from the
rounded $1.61 comparison input. Historical legacy quantities are untouched.
MiMo $0.83 and Qwen Flash $3.42 are owner-supplied rounded calc8/API references,
not claims of equal capability or new pricing observations.

| Additional read-only source | Observed SHA-256 |
|---|---|
| `/home/agent/lanes/hybrid/.temp/research/api-capability-2026-10.md` | `bb200c4b17ec591bba689ab94464d26523fd70ca3dcbb9d2a8b503d4cf9eaf47` |
| `/home/agent/lanes/hybrid/NOTES.md` | `c46e34e1fa51cfbde3f148b25332d76c777babea0861cb8eb4675a7a22c1d0ac` |

Native measured M3 Max rates at 16k are 7.48084 / 8.46553 / 8.82004 tok/s
(mean 8.25547), read from the pinned normalized benchmark. At the measured
GGUF size, KV and state, this implies **40.96%** of the nominal 400 GB/s bound.
The owner's 30–37% setting is therefore an explicitly calibrated coordinate:
`correction = measured_mean * reference_traffic / (reference_BW * 0.34)`;
`per_stream = BW * efficiency * correction / (active_weights + K*state_traffic)`.
The engine shows both the coordinate and raw fraction, avoiding an incorrect
physical claim. Applying that calibration to Q3, other Macs or GLM remains an
estimate. Qwen prefill uses the measured segment curve; GLM scales it by the
FLOP ratio and the declared client multiplier. Fit includes OS/apps, KV and
recurrent state; Flash-Next optionally leaves its 51B n-gram table on SSD and
reports an unmeasured 0.2 ms/token lookup latency. That fit is not a promise
of usable SSD decoding performance.
