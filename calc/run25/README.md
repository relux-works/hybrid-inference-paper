# Run25: separate dedicated-fleet sensitivity

Accepted parent: `ca7f228acd789380bf46016fd87acc33e1b07aef` (run24,
Muse r5x6 ACCEPT). This run adds new files only. The root README and root
manifest remain frozen with all other accepted parent bytes; this README
documents the new tools without changing an accepted file.

Run from the paper checkout, CPU only:

```bash
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/.temp/hybrid-e-r20-261105/tmp"
python3 -B -I calc/run25/export.py
python3 -B -I calc/run25/finish.py
python3 -B -I calc/run25/finish.py --audit-only
python3 -B -I -m unittest discover -s calc/tests -p 'test_run25*.py'
```

`config.json` declares storage capacity, unmeasured restore/price/arrival
proxies and mean-latency admission limits. `model.py` implements complete-copy
packing, expected pending catch-up and per-node randomly split Poisson/M/G/1
queue means. `engine.py` reuses the accepted PRI31 client, measured PRO decode
surface, prefill, billing and workload profiles; it scans integer teams1..500
for fixed1/2/4-node and first-certified-minimum policies. `export.py` writes
small CSVs under `calc/out/run25/` and the R25 report, checking free bytes and
`df -BG` before/after each write. It refuses writes that would cross28GiB.
`finish.py` publishes the compact changed-crossing ledger, latency tables and
final source-bound audit. Re-running `finish.py` requires a fresh base export
to avoid appending the report supplement twice.

`manifest.json` binds new outputs and source hashes and verifies every
parent-tracked file byte-for-byte without extracting large historical trees.
All CSVs together must stay below50,000,000 bytes. There is no full quote dump.
Task logs/real exit receipts and failed resource stops are under
`.temp/hybrid-e-r20-261105/`; `calc/R25-VALIDATION-261105.json` records delivery
gates. No inference, API request, download, native build or push is needed.

The new sensitivity is bought PRO6000, office125MB/s/1ms and owned M5Max64,
bf16 transport. Rented-GPU rows in the closed-contour CONTROL retain the accepted
estimated WAN112.5MB/s/400ms and original billing/egress; new office-proxy rental
billing refuses. Rental must be approved inside the team's trust boundary before
it represents a closed contour; no physical-office or external-provider privacy
assurance is inferred.
s=.2 covers only the open-model segment;80% still goes to a stronger cloud
model. Only s=1 removes external model APIs.

All storage/restore/queue/expansion-price proxies are **unmeasured**. The large
warm-RAM case is a hypothetical3.6TB usable RAM pool, not a256GB cache magically
holding200 full slots. Full read and write are charged. A fixed fleet can have
a finite winning interval and later refuse storage; the first win is not a
sustained crossing through500. Queue budgets certify modelled means, not
measured p95 latency or real vLLM scheduler performance.

See [unresolved input](UNRESOLVED_QUESTIONS.md) for the exact log-coverage gap.
Fitted token/work fractions and delta/output reweighting are explicitly
conditional estimates. Per-cadence API comparisons retain run24's priceable
cohort and missing-Qwen-core rules; no provider cache verdict is added.

When the remote queue cannot certify, the policy tries local prefill and still
charges all server generation exceeding client capacity. `prefill_route` makes
this explicit; zero offload is never called an offload speedup. Server overflow
replays the expected deferred local journal (bounded by full-prefix work), rather
than assuming its restored checkpoint is already current. Client-only TTFT and
an unmeasured all-call TTFT surrogate are separate fields. The certified minimum
is within this declared policy and storage class, not a proof of global fleet
optimality.
