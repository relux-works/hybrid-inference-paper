# RULER saved rows: interim paired analysis and completion path

Run: hybrid-d-r16d-261105. Observed/analyzed on agents1 at 2026-11-05 09:01:13Z. Workbench: accepted `e46e5623b5138c5212b23bb427510b9b14acb1c9`.

**Every result below is interim, n of 390, not the pre-registered verdict.** The snapshots precede the owner-directed rental-node stops on 2026-11-04. The RC4 data cut-off is 2026-11-05 12:00Z. Neither depth is complete; 64k and 128k remain pending with p=1 in the preregistered Holm family. No committed equivalence tables or source code were changed.

## Inputs and verification

- Bundle SHA-256: `fe2195aaae4e098a3a206a0e60fe925fa19293d59c62c8103fbb6160c7e7d48b` (matches supplied fe2195aa...d48b).
- Original: `/home/agent/lanes/hybrid/.temp/ruler-results-261105/download/ruler-main-results-before-stop.tar.gz`; unpacked source under `.../x/` is read-only.
- Selected verified bundle contents copied to this report directory under `input/`; every copied byte also matches the supplied unpacked source. The copied scope is 6,987,623 bytes, including 593 row files, manifests/events/pending-session files, logs and RECOVERY.json. No generated specs or model/data files are in the bundle.
- `input-hashes.json` records the SHA-256 and size of every copied file; full manifest differences are in `manifest-differences.json`.
- Manifest identity: Qwen model `31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34`, seed 261102, native commit `18d3f114e46c4f801c4a09e2c6cf8ba2303ae42d` in client/node/partition, Q4_K_M, CUDA; client batch/ubatch 64, node and partition 256, context 135168, threads/threads_batch 2.
- Data lock SHA-256: `f42a48cc9d2ca4a0e6ab0bb986fb7b87990dee3c61cc821da53d4147ed80594b`. The raw lock bytes were reconstructed from embedded provenance using the accepted writer order, and their SHA-256 matches. The embedded download-manifest SHA also matches reconstructed original serialization. Actual model/dataset/native-binary bytes are not in this selected bundle and were not independently rehashed here.
- All 50 Python source fingerprints in each manifest match the local git objects at 18d3f114. Accepted `ruler_analysis.py` SHA-256 is `f0fa95fdf3890b0a485a6f9ae1a0be96c8177ffd46312664a6857ad370990635`; evaluator SHA-256 is `f37651d47907885f09f25ace654b8ac962a8359faa3db7e06a316cf397289ee0`.

**The premise that the two manifests differ only by depth is false.** All fields other than depth and native-binary fingerprints agree exactly. There are 64 differing `clients/*/binaries/*` hash leaves (including soname aliases), plus depth. In particular `llama-server` is `c6f07f4b84b6ab18cd89da04398f73b68e7defc849b9096636d3306b1a310958` at 64k and `a4e8396c5fda877cf7c96c3b45218c1fc2c4c28335362b57be4bbf37d2be50ca` at 128k. Each depth is checked against its own saved manifest; rows are not pooled or relabelled as one exact native identity.

| Depth | Saved complete pairs / target | Manifest SHA-256 | State |
|---:|---:|---|---|
| 65536 | 368/390 | `8d7cf9041ca798d96fe6212334991cb429fe07095665b593e8748f14ee4bf1f7` | interim, not the pre-registered verdict |
| 131072 | 225/390 | `b8fdacf3af8ef20ffbd5cd14f83013c90bb3bb4f4d194e4ac9d4fad22349ceea` | interim, not the pre-registered verdict |

All 593 row_sha256 values match the accepted canonical `digest` of the entire row without that checksum. All rows have all three arms, shared prompt identity, declared depth, seed 261102, unique planned task/index and valid scores/answers; none were excluded. Rows do not independently embed model/data-lock/commit: those identities are bound by their verified archive/manifest context. This is integrity/provenance checking, not fresh attestation of remote execution.

Named controls in `analysis-verification-01.log`, `verification-controls.json` and `report-build-01.log` reject changed row seed even after recomputing its checksum; corrupted row SHA; foreign model, data lock or commit manifests; and cross-node binary identity with depth normalized. Accepted exact-manifest positives pass. Changed native binaries at the same commit refuse in the real resume_manifest both with and without the cleanup flag. These are CPU-only inline checks, with no evaluator code change. The manifest-only-depth equality check records the actual failed premise, not a passing assertion.

## Method

Imported the accepted, unchanged `ruler_analysis.analyze` and passed each depth's complete rows directly. It accepts incomplete depths for descriptive calculations; no replacement statistic or resampling was added. Scores use its per-example mean, fully-correct means score==1, changed answers use outer-whitespace equality, Wilson limits are its 95% limits, and the paired text excess interval is its conservative Bonferroni exact-binomial-cell interval. All McNemar p-values below are exact, two-sided, unadjusted. JSON preserves the accepted tables under an explicit interim wrapper in `interim-65536.json` and `interim-131072.json`; no interim result is promoted into the registered score-equivalence analysis.

These are task-order prefixes, not random subsamples of all 390 planned cases. At 128k, vt/cwe/fwe/qa_1/qa_2 have no saved rows. The 100% observed score is therefore not a full-depth RULER score. At 64k, 22 qa_2 examples remain. Its row snapshot contains qa_2 indices 0-7 (8 rows), although the separately copied progress log ends at 7/30. RECOVERY.json explicitly warns collection is not atomic; the report uses verified saved rows rather than inferring the denominator from the log.

## Interim summary: 368/390 at 64k, 225/390 at 128k; not the pre-registered verdict

| Depth | n/390 | Local score % | Offload score % | Partition score % | Fully correct local / offload / partition |
|---:|---:|---:|---:|---:|---|
| 65536 | 368/390 | 98.9130 | 98.9130 | 98.9130 | 364 / 364 / 364 |
| 131072 | 225/390 | 100.0000 | 100.0000 | 100.0000 | 225 / 225 / 225 |

| Depth | Fully-correct pair against local | Both correct | Arm correct, local not | Local correct, arm not | Neither correct | Exact McNemar p |
|---:|---|---:|---:|---:|---:|---:|
| 65536 | local_partition-local | 364 | 0 | 0 | 4 | 1 |
| 65536 | offload-local | 364 | 0 | 0 | 4 | 1 |
| 131072 | local_partition-local | 225 | 0 | 0 | 0 | 1 |
| 131072 | offload-local | 225 | 0 | 0 | 0 | 1 |

| Depth | Text arm vs local | Changed / n | Changed % | Wilson 95% (%) |
|---:|---|---:|---:|---|
| 65536 | offload | 28/368 | 7.6087 | [5.3164, 10.7769] |
| 65536 | partition | 32/368 | 8.6957 | [6.2268, 12.0179] |
| 131072 | offload | 12/225 | 5.3333 | [3.0769, 9.0894] |
| 131072 | partition | 12/225 | 5.3333 | [3.0769, 9.0894] |

| Depth | Offload only | Partition only | Both changed | Neither changed | Text McNemar p | Excess pp (O-P) | Excess conservative 95% (pp) |
|---:|---:|---:|---:|---:|---:|---:|---|
| 65536 | 12 | 16 | 16 | 324 | 0.571588 | -1.0870 | [-5.8349, +3.6932] |
| 131072 | 7 | 7 | 5 | 206 | 1 | +0.0000 | [-5.7205, +5.7205] |

## Per-task interim tables: depth 65536, 368/390; not the pre-registered verdict

| Task | n/30 | Score % local / offload / partition | Fully correct local / offload / partition | Changed text O / P | O-only / P-only | Text p | Excess 95% pp |
|---|---:|---|---|---|---|---:|---|
| cwe | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 10 / 14 | 1 / 5 | 0.21875 | [-37.254, +14.732] |
| fwe | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 2 / 4 | 2 / 4 | 0.6875 | [-32.692, +21.409] |
| niah_multikey_1 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_multikey_2 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 5 / 8 | 2 / 5 | 0.453125 | [-36.731, +19.726] |
| niah_multikey_3 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_multiquery | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_multivalue | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 6 / 3 | 5 / 2 | 0.453125 | [-19.726, +36.731] |
| niah_single_1 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_single_2 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_single_3 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 4 / 2 | 2 / 0 | 0.5 | [-13.025, +24.453] |
| qa_1 | 30/30 | 96.67 / 96.67 / 96.67 | 29 / 29 / 29 | 1 / 1 | 0 / 0 | 1 | [-13.590, +13.590] |
| qa_2 | 8/30 | 62.50 / 62.50 / 62.50 | 5 / 5 / 5 | 0 / 0 | 0 / 0 | 1 | [-42.175, +42.175] |
| vt | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |

| Task | Offload gain / loss vs local | Exact accuracy p | Partition gain / loss vs local | Exact accuracy p |
|---|---|---:|---|---:|
| cwe | 0 / 0 | 1 | 0 / 0 | 1 |
| fwe | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multikey_1 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multikey_2 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multikey_3 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multiquery | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multivalue | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_single_1 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_single_2 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_single_3 | 0 / 0 | 1 | 0 / 0 | 1 |
| qa_1 | 0 / 0 | 1 | 0 / 0 | 1 |
| qa_2 | 0 / 0 | 1 | 0 / 0 | 1 |
| vt | 0 / 0 | 1 | 0 / 0 | 1 |

## Per-task interim tables: depth 131072, 225/390; not the pre-registered verdict

| Task | n/30 | Score % local / offload / partition | Fully correct local / offload / partition | Changed text O / P | O-only / P-only | Text p | Excess 95% pp |
|---|---:|---|---|---|---|---:|---|
| cwe | 0/30 | not measured | not measured | - | - | - | - |
| fwe | 0/30 | not measured | not measured | - | - | - | - |
| niah_multikey_1 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_multikey_2 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 4 / 4 | 3 / 3 | 1 | [-27.379, +27.379] |
| niah_multikey_3 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 2 / 2 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_multiquery | 15/30 | 100.00 / 100.00 / 100.00 | 15 / 15 / 15 | 0 / 0 | 0 / 0 | 1 | [-25.333, +25.333] |
| niah_multivalue | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 3 / 3 | 2 / 2 | 1 | [-23.888, +23.888] |
| niah_single_1 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_single_2 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 0 / 0 | 0 / 0 | 1 | [-13.590, +13.590] |
| niah_single_3 | 30/30 | 100.00 / 100.00 / 100.00 | 30 / 30 / 30 | 3 / 3 | 2 / 2 | 1 | [-23.888, +23.888] |
| qa_1 | 0/30 | not measured | not measured | - | - | - | - |
| qa_2 | 0/30 | not measured | not measured | - | - | - | - |
| vt | 0/30 | not measured | not measured | - | - | - | - |

| Task | Offload gain / loss vs local | Exact accuracy p | Partition gain / loss vs local | Exact accuracy p |
|---|---|---:|---|---:|
| niah_multikey_1 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multikey_2 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multikey_3 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multiquery | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_multivalue | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_single_1 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_single_2 | 0 / 0 | 1 | 0 / 0 | 1 |
| niah_single_3 | 0 / 0 | 1 | 0 / 0 | 1 |

## Completion path at evaluator 18d3f114

**A new host and fresh services are not inherently prohibited, but the four named identities alone are insufficient, and this rows-only bundle cannot automatically resume unchanged.**

1. `ruler_eval.py:54-81` admits a resume only when the entire new manifest equals the saved manifest. Hostname, service URLs, ports, PIDs and session IDs are not stored in that manifest, so they may change. All stored source fingerprints, Python 3.12.3, dependency/wordlist identities, data/download provenance, model, layout/template, CUDA backend, context/batch/ubatch/threads and native executable/library hashes must still match. Rebuilding the same commit is not proof of the same hashes. The two depths require their respective original native binary sets, not one shared replacement build. The accepted equivalence branch also has extra/changed Python source files, so it is not the source inventory for resuming this evaluator; use the exact saved 18d3f114 inventory.
2. `--resume-slot-cleanup` is only the b63d9019 predecessor-source migration. It requires all non-source fields equal and the precise allowlisted prior source hashes. It cannot waive fresh-build, package, model, data or host-migration identity changes. Inline controls against the actual 18d3f114 function confirm changed-binary manifests refuse with both flag settings.
3. More importantly, the loop at lines 282-302 checks/recreates `specs/<task>-<index>.json` before skipping a saved row. It then requires the saved spec_sha256 to equal digest(spec). This selected bundle has zero specs; generated input bodies are omitted from rows, and regenerated specs contain a newly measured generation_seconds in their digest. Recreating only the same seed/model/data therefore does not produce the same frozen spec bytes/digest automatically. There is no unchanged evaluator option to skip existing rows without validating those specs.
4. Restore the original frozen specs and exact per-depth runtime/build/data identity from the preserved full archives or provider volumes, then verify them before continuation. RECOVERY.json says those originals are retained; their contents/access are not independently verified in this local bundle. Alternatively an explicitly reviewed recovery/migration procedure would have to reconstruct and verify every original spec digest, account for any changed runtime identity, and qualify the change; that is future work, not a reason to rewrite manifests or bypass hashes. Without this recovery, start a fresh 390-example depth under its honest new identity.
5. Both snapshots have pending-sessions.json. After manifest admission, the evaluator tries to release all three old session IDs before progressing. The accepted release retry treats HTTP 404 as already released, so a healthy fresh proxy with absent old IDs can clean them up. Other release failures block continuation. Every example uses fresh independent sessions, so completed rows need no live cache carried between examples. This is a code-path conclusion; no service, network or provider action was performed.

### Remaining time from measured saved-row rates

Rate below is mean(generator generation_seconds + sum of the three stored arm seconds) on complete saved examples. It omits unrecorded release/hash/control overhead and setup; it is not a new benchmark or a guaranteed finish time. Estimates assume comparable native services and hardware. Unmeasured task types make the 128k extrapolation uncertain.

| Depth | Remaining examples | Measured basis | Seconds / example | Remaining compute estimate |
|---:|---:|---|---:|---|
| 65536 | 22 | all saved complete rows | 134.190 | 49.20 min (0.820 h) |
| 131072 | 165 | all saved complete rows | 297.718 | 818.72 min (13.645 h) |
| 65536 | 22 | matching remaining task qa_2, 8 saved examples | 152.595 | 55.95 min |
| 131072 | 165 | latest partly measured task niah_multiquery, 15 saved examples | 321.455 | 14.733 h |

64k remainder: qa_2 indices 8-29. 128k remainder: niah_multiquery indices 15-29, then vt/cwe/fwe/qa_1/qa_2, 30 each. At approximately 09:00Z on 2026-11-05, a recovered 64k continuation might fit before 12:00Z with roughly 56 minutes of compute plus recovery/setup. The 128k remainder is roughly 13.65-14.73 hours on observed-rate extrapolations, so it cannot fit in the remaining approximately three-hour window at those rates, even before recovery/setup. No node launch or completion is authorized or claimed here. A wholly fresh rerun costs about 14.54 h at 64k and 32.25 h at 128k using their overall observed rates, with the same task-mix caveat.

## FACTS-ready block (English)

```text
Interim paired RULER snapshots recovered before the owner-directed rental-node stops on 2026-11-04; interim, n of 390, not the pre-registered verdict. Accepted descriptive analysis on checksum-verified complete three-arm rows:
64k: 368/390 saved pairs. Local/offload/partition RULER scores 98.91%/98.91%/98.91%; fully correct 364/368 in every arm. Both offload-local and partition-local fully-correct McNemar p=1 (0 gains, 0 losses). Changed text: offload 28/368=7.61% (Wilson 95% 5.32-10.78%), partition 32/368=8.70% (6.23-12.02%). Offload-only 12, partition-only 16; exact text McNemar p=0.5716. Text excess -1.09 pp, conservative 95% [-5.83,+3.69] pp. Remaining: 22 qa_2 examples.
128k: 225/390 saved pairs, restricted to the early needle tasks. All arms score 100.00%, with 225/225 fully correct; both accuracy McNemar p=1 (0 gains, 0 losses). Changed text 12/225=5.33% in each comparison (Wilson 95% 3.08-9.09%); offload-only 7, partition-only 7, text McNemar p=1. Excess 0.00 pp, conservative 95% [-5.72,+5.72] pp. Remaining: 165 examples, including all vt/cwe/fwe/QA cases.
Neither depth is complete: both remain pending at p=1 in the preregistered Holm analysis. These serial task prefixes do not establish the registered equivalence verdict. Model/data-lock/seed/source commit agree across nodes, but 64 native-binary hash leaves also differ between manifests. A fresh host is not forbidden by the manifest contract; rows alone cannot auto-resume: exact runtime/build identity and frozen specs must be recovered. At measured rates, remaining compute is about 56 min at 64k and 13.65-14.73 h at 128k, excluding recovery and setup.
```

## Evidence and execution scope

`analysis-verification-01.log`, `report-build-01.log`, `verification-controls.json`, `input-hashes.json`, `manifest-differences.json`, and both `interim-*.json` persist beside this report. The real command exit for verification/analysis was 0; expected refusal cases were caught and checked, while the false manifest-equality premise is reported explicitly. All calculations were inline Python standard-library calls reusing accepted functions. No script or tracked file was added, no commits were created, and no original result or supervisor output was modified. The only requested external action is the separately logged orchestrator summary; no measurement/service/provider network requests were made.
