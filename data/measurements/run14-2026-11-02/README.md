# Run14 measured inputs (2026-11-02)

The three archives in this directory are unmodified owner-supplied data. The
fourth input is the existing M5 Max64 archive under `../m5max64-2026-11-01/`.
Full SHA-256 pins and relative paths live in
`calc/hybridcalc/data/run14-measurements.json`. The consumer validates the outer
hash, all manifest hashes/sizes, unsafe paths, links and unexpected members
before admitting data. Archive contents are never executed.

Mac steps55/56/57: `9b7019cd71a2d3df221768b77a91d37babe2fa6c0584d9618b0ead7f4c233ac2`.
Restored-context control: `409bd7efeca11ec4697b940b6f83d4e4055d3894f49de32bf723d876a235d73e`.
M5 Max64 kit1.4.1: `c7ceab57f8d61b9bd166daf96cae1e8f389d296c0f9789ccb8cc32536d9f6b05`.
B300 kit1.6.5: `1325ae41717945a2c8e14cf2ad5588c7375dd7511361879510fbc4d3523011bc`.

Mac aggregate decode is recomputed as the sum of `predicted_n - 1` divided by
the longest request's `predicted_ms / 1000`, matching the sweep's timed decode
interval convention. Actual depth includes the 16-token suffix. The restored
128k control supersedes hot-prefill 1/2/4/8 rows; step55's twelve-stream point
remains labelled "after a long prefill, lower bound". The 1.04M observations
use YaRN scale4 and do not qualify model quality at that context. Rates can
decrease with more streams or depth; no monotonicity correction is applied.

The complete seeded call mix reaches 1,000,557.676 tokens before decode. At
four requested streams it also admits three on some calls: no three-stream
Mac sweep exists. Strict full-mix capacity therefore has a measurement gap.
Depth-bounded exports are conditional supported subsets, never replacements
for the full-mix result. Memory remains checked after each call's output.

B300 step70 is explicitly **skipped** in the delivered `sweep-status.json`:
the pinned and comparison build are both
`dde879bc4f954b809892fd0d660515f42536394a`. There are no tuning observations
to turn into an uplift. Step40 is the admitted llama.cpp depth/decode run.
Step71 contains FP8 default KV, FP8 KV and large-batch controls. NVFP4 is a
different precision and is not an FP8 option. Cached rates must use each
row's own block size (784 default, 1568 FP8 KV), useful delta and actual TTFT.
These are server-only rates; hybrid transfer through the vLLM bridge is in
qualification.

Task: `hybrid-e-r4-261102`, tracked in the existing `.temp/tasks.md`.
Scratch extracts/logs are under `.temp/hybrid-e-r4-261102/`; extracts are
removed at handoff. Reproduce with `python3 -I calc/tests/r14_audit.py` and
`python3 -I -m unittest discover -s calc/tests -p test_run14.py -v`.

## R5 use

R5 retains the measured lookup and bounded tables, and explicitly models the
full-mix depth/count gaps using the owner-approved rule in the r5 report.
Step57's `agents-loop` payload is held out for a prediction check, never used
to fit parallel rates. `pr9/` preserves the owner-supplied CUDA 27B JSONL bytes;
its SHA-256 and the single-point Mac import/5G measurements are recorded in
`calc/hybridcalc/data/run14-r5.json`. CUDA imports are localhost measurements,
not WAN rates. Mac import-speed-v2 remains pending until its Mac gate lands.
