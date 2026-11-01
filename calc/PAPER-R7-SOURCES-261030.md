# Run 7 source custody and assumptions

No network lookup was performed. `hybridcalc/data/paper-tables-r7.json` contains
all new quantities, units and provenance; `scenarios/paper-tables-r7.json`
composes the existing engine layers. Exactly four new chart IDs are exported.

## Measured timing basis

The engine verifies existing files with `hybridcalc/data/measurements.json`.
The benchmark archive SHA256 is
`5c393bdf40052eb582b5c17aac6176a9273a866c4fadde999ee19afa30924439`.

- Measured M3 Max Qwen Q4 marginal segment rates are interpolated at their
  actual midpoints; below the first midpoint the first rate is held constant,
  beyond the last midpoint FLOP efficiency is held constant. Local large turns
  and cold loads integrate seconds/token across the complete span, with the
  existing memory roofline. Midpoint step is an explicit 256-token estimate.
- Measured slot geometry is 34,844 B/token and 156,894,784 B fixed. The bf16
  recurrent representation is **estimated** at half the fixed bytes,
  78,447,392 B. It does not halve q8_0 KV. Compatibility and numerical quality
  are not established by these arithmetic variants.
- One B300 uses `owners.options.b300` and `service.mfu`, effective 1.35 PFLOP/s
  under the default Q4/INT8-FP8 throughput estimate. Server prefill integrates
  depth-dependent FLOPs; existing workspace/weight memory checks apply.
- The client evaluates one final-depth single-stream decode-equivalent token
  after import. This is a conservative estimate, in addition to the full delta
  payload, not a measured remote-to-local first-token path.
- Isolated delta import is unmeasured. Full slot restores in the package include
  local filesystem/cache state and are not a delta-import benchmark. The
  declared estimate is one serial memory copy at 10% nominal client bandwidth
  (M3 40 GB/s), plus an explicit zero fixed overhead. Parsing, conversion and
  runtime validation can add cost; override the inputs when measured.
- Link defaults are line rate, goodput 1 and RTT 0, both explicit inputs.
  Hybrid timing is a serial sum; upload/model-load and queue/scheduling cost
  beyond these declared components is not measured or added implicitly.

## Decode sensitivity

The hash-checked 32k M3 native baseline is 8.440946539830035 tok/s; four streams
have aggregate 14.054306337676012 tok/s, gain 1.665015442445748. R7 retains the
existing interpolation/roofline law and multiplies rates, preserving that
anchor gain. M5 compute/bandwidth portability and all deep/state-format
projections remain estimates. Factors above one are hypothetical improvements.

The numeric rate columns show requested algebraic targets. Capacity requires
unchanged-traffic bandwidth efficiency <=1. Factor 3 exceeds this bound under
the current calibration and has capacity alarms; it is not silently clipped or
reported as measured. Factors 1, 1.5 and 2 remain computable. Session counts are
supported sampled calls divided by the existing 116-call normalization group,
not reconstruction of session chronology. `fit_share`, hours and stream ranges
are explicit. This sensitivity retains R5's estimated 1M model envelope beyond
the benchmark's actual 262,144 context, while standalone timing spans use the
benchmark limit. Per-call local prefill retains the R5 marginal-depth convention.

## Architecture attachment

The verbatim owner-supplied script is retained only as an independent test
oracle at `tests/fixtures/arch_compare_r7.py`. Tests execute a copy in an isolated
temporary directory, compare every original numeric f32 field, and never read
or edit `paper/data/`. Config URLs recorded in the data are:

- [Qwen3.8-27B config](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/config.json)
- [Muse Glimmer 30B config](https://huggingface.co/meta-models/Muse-Glimmer-30B/blob/main/config.json)
- [Gemma 4 31B config](https://huggingface.co/google/gemma-4-31B-it/blob/main/config.json)
- [Qwen3-32B config](https://huggingface.co/Qwen/Qwen3-32B/blob/main/config.json)

Config quantities are offline owner-script transcriptions. Their access date
2026-10-30 records reading the supplied snapshot, **not** a live HF access or
independent URL/config validation. Parameter counts are rounded FLOP estimates,
with URLs in their reasoning/provenance, not newly counted checkpoint sizes.

The architecture f32 numeric outputs are identical to the attachment. Its
Qwen q8_0 layout is 34,816 B/token (34/32 packing), not the measured slot slope
34,844 used by R7 timing/sensitivity. Its 41.2 tok/s reference is read from the
measured segment 112,896–150,000, midpoint 131,448, labelled approximately 131k
in the script; it is not a direct point measurement at 131,072. Its Qwen FLOP
count uses 27.8B, while the prior engine envelope uses 27B. Architecture savings
intentionally exclude server prefill, import and evaluation exactly as attached.

Unsupported 262k values become alarms where the script wrote None; the original
131k Qwen3-32B extrapolation is reproduced and explicitly marked outside the
configured 40,960-token context. Bf16 adds a labelled extension: only Qwen's fixed
state, deltas and transfer/saving values change. Sliding-window state is still
q8_0; K=V sharing and window saturation follow the exact attachment formulas.
