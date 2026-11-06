# WAN hybrid-call time accounting: hybrid-d-r13-261103

Observed on 2026-11-03 UTC. CPU-only, local evidence analysis; no downloads, model execution, production changes, or push. All seconds below are wall seconds unless stated otherwise. Six decimals are for reproducible arithmetic, not timer accuracy.

## Findings

| Call | Measured TTFT | Snapshot download inside TTFT | TTFT minus snapshot | Prefill + body transfer + all import requests | Remainder before mapping sync | Mapped sync | Still not split into individual phases |
|---|---:|---:|---:|---:|---:|---:|---:|
| First 39,504-token call | 201.655099 | 0 | 201.655099 | 176.285151 | 25.369948 | Not separately recorded | 25.369948 |
| Growing base | 2896.763843 | 2413.468032 | 483.295812 | 442.127596 | 41.168216 | 0.437346 | 40.730869 |
| Turn 7 | 468.664485 | 425.589585 | 43.074901 | 33.215839 | 9.859062 | 3.927141 | 5.931921 |
| Turn 31 | 490.518778 | 455.201414 | 35.317364 | 27.531847 | 7.785517 | 0.311989 | 7.473529 |

The first-call 201.7 s is TTFT, not full stream duration: total is 202.088738 s. Its exact missing time is 25.369948 s. The supplied rounded components do not support an exact 25.5 s claim.

The growing base's 2.907521 s import field is the sum of all ten requests: nine stages total 2.508157 s and the final save plus import request is 0.399364 s. It is not a separate 2.9 s final import on top of ten stages. Adding stages again understates the remainder. Turn 7/31 each have one chunk, whose import_ms duplicates the call import_seconds.

Most remaining growing-session time is localized inside the synchronous extend wrappers: 40.165351 / 5.272069 / 6.636849 s. These wrappers include request upload, node queue/state load/export/save/checksums, and evidence-file writes and hashes. Available fields cannot separate these operations. Old-slot recovery save cannot be added to these gaps: it is inside import_ms. SHA-256 is a real unmetered contributor on the node and evidence-capture paths, but its elapsed cost is not independently recorded.

## Evidence and time boundaries

Sources, all local:

- First call: /home/agent/lanes/hybrid/.temp/e2e-results-261101/x/40k/hybrid-bench-mac-metal-40k-20261101T122140494707Z.jsonl, line 12; accompanying MD, client-info.json and node-info.json. The local dl/mac-40k.tar.gz contains the archived bundle; analysis used the already extracted files.
- Growing session: /home/agent/lanes/hybrid/.temp/growing-mac-261102/TIMING-EXTRACT.json.gz (T) and INSTRUMENTATION-TIMING-EXTRACT.json.gz (I), both bound to trace SHA-256 e38da6db2905aba36f2c0921f30de67e3d660012f2d4b3cb69101cce05beb784. The original Mac trace/state archive is not locally supplied; it was not retrieved.
- Both preflight route plans were read. They describe predictions, not phase measurements. The older plan refuses its route mix; the accepted 5G plan predicts turn 7 offload at 31.839249 s. Neither fills a measured gap.
- /home/agent/lanes/hybrid/.temp/paper-v2/FACTS.md, section 3, used as the summary to reconcile, not as a replacement for raw fields.
- tools/hybrid/RESULTS-hybrid-d-r12-261102.md and the recovery-size formulas in tools/hybrid/RESULTS-hybrid-a-r24-261101.md.

Code: prototype fca0fe31d2d0dc4ec6b6568c531b935af8a05d5a; driver 72566bca9158bc758f499caf458b91e74e69b1c8. The driver was read in the task's own detached worktree, driver-worktree/, using objects fetched only from the existing local hybrid-b checkout. Current workbench production files were checked byte-identical to fca0fe31 for the relevant proxy/state/node paths.

The first call predates this code. Its recorded client is 7e1a477b2e8dfc8146744f4f81d73abca25e7d4a and node is 0124e89a933872b54bd445921b9ac2e1c9c43a09. Their actual proxy/import/hash/node paths were inspected from local git objects; source extracts are retained here. This matters: that client imports each chunk immediately and has no proxy old-slot save. Current code stages chunks and applies them at the end.

Definitions:

- stream_chat starts its clock just before urllib opens the request, after bench JSON encoding. TTFT ends at first nonempty content/reasoning SSE delta at the bench. It does not independently timestamp first sampling or first raw token. Synthetic prompt construction, bench request JSON encoding, preflight token counting/health checks, base restore and later pre_stage are outside this clock.
- Proxy chat rendering/tokenization, slot checks, critical sync, import and held-final-prompt-token evaluation are inside TTFT. Their individual start/end clocks are not all retained.
- Node.request.transfer_ms starts AFTER urlopen has received response headers. It times response.read only. Upload, response-header wait, queueing, full node load_state, prefill, range export/checksums and full save_state happen before or outside this body-read interval.
- X-Hybrid-Prefill-Ms times hybrid::prefill only. Node load_state precedes it; export_range/encode_delta and save_state follow it. All extend traffic goes through node scheduler admission; there is no queue-time field.
- I.node_snapshot_capture_events duration_seconds is the MeasuredNode.download wrapper. It includes HTTP open/header wait, snapshot generation, streaming writes, flush/fsync. Do not add these costs again. The separate post-download delta.write_bytes and snapshot/delta sha256 calls are OUTSIDE that download timer and INSIDE the parent extend timer.
- R = remote_prepare_seconds; E = sum(parent_extend_duration_seconds_including_snapshot); S = sum(snapshot duration); P = server_prefill_seconds; D = transfer_seconds; M = import_seconds. The disjoint accounting is:
  TTFT = S + P + D + M + (E-S-P-D) + (R-E-M) + (TTFT-R).
  Sync spans are a further split of R-E-M, not an addition to it.
- Sync attribution uses matching time/depth and the proxy's synchronous sync-before-extend control flow. T's sync rows omit critical/background origin and exact call-start clocks, so this is a reconstructed association, not a new independently tagged span. Unmapped residuals are preserved below.

## First call: fresh 39,504-token prompt, UK CUDA to M3 Max Metal

All rows labelled unknown are contained in a numbered aggregate row and are not additional time.

| Phase, in execution order | Seconds | Source field / interpretation |
|---|---:|---|
| Proxy rendering/tokenization, slot allocation/info and client request handling | Unknown, part of 5.711228 below | No phase clock in first JSONL |
| Initial health/session/prefix synchronization; node upload and queue | Unknown, part of 19.658720 below | No upload/queue/sync clock; replayed_prefix=0, remote_replay_acknowledged=0, server_shadow_ms=0 |
| Node prefill, four chunks | 10.642512 | server_prefill_ms / 1000; sum chunks |
| Node full-state restore, range serialization, XXH3/SHA-256, envelope copies, full-state save; upload/header wait and per-chunk readback/journal work | Unknown individually | Located in remote_prepare remainder below |
| Delta response-body transfer | 123.219428 | transfer_ms / 1000; 2,004,023,525 envelope bytes |
| Four immediate chunk imports, including decoder checksum/native apply | 42.423212 | import_ms / 1000 = sum chunks[].import_ms / 1000 |
| Other work inside remote preparation | 19.658720 | remote_prepare_ms/1000 - prefill - transfer - import |
| Other TTFT work outside remote preparation, including rendering/tokenization and final prompt-token compute/sample/SSE receipt | 5.711228 | ttft_seconds - remote_prepare_ms/1000 |
| TTFT endpoint: first nonempty decoded text/reasoning at bench | 201.655099 | ttft_seconds; cumulative endpoint, not an additive phase |
| Remaining stream/finish after first text | 0.433639 | total_seconds - ttft_seconds |
| Complete stream | 202.088738 | total_seconds; cumulative endpoint |

remote_prepare_ms = 195943.871416. The two residual intervals sum to 25.369948 s. Neither can be split further from this JSONL. local_evaluated=1 establishes that the client evaluates the withheld prompt token; there is no per-call prompt_ms here. decode_ms=215.894 is the generation meter for the call, not a timer for that held token or the first sampled token. Do not subtract it from TTFT.

Chronological chunk chain: request/upload/queue -> node restore/prefill/export/hash/save -> body read -> client_delta parse -> immediate import -> /info exact token/hash verification and journal save; repeat four times; then client completion evaluates prompt token 39,504 and streams the response. There are no absolute per-chunk timestamps in the archived JSONL.

| Imported range [n0,n1) | Node prefill s | Body transfer s | Immediate import s | Envelope bytes |
|---|---:|---:|---:|---:|
| 0-10876 | 2.597060 | 33.449370 | 12.804780 | 535858600 |
| 10876-21752 | 2.836815 | 34.053650 | 9.868252 | 535858585 |
| 21752-32628 | 3.098263 | 31.515257 | 11.341299 | 535858585 |
| 32628-39503 | 2.110374 | 24.201151 | 8.408880 | 396447755 |

All four chunks contain recurrent state in this old protocol. There is no separate staged/final transaction import and no proxy action=save to explain a missing first-call interval.

## Growing base: fresh 99,999-token prompt, one output token

Source abbreviations: I.base_and_offload_call_components[turn=0] = C0; T.calls[hybrid,turn=0] = T0. The prefix exported to the client ends at 99,998; one final prompt token is evaluated locally, then one output token is sampled/reconciled, giving depth_after=100000.

| Phase, in execution order | Seconds | Source field |
|---|---:|---|
| Proxy rendering/tokenization, slot checks and held-token compute/first sample/SSE | Unknown separately; inside 0.492071 below | T0 omits original local_tail_seconds / meter.local_prompt_ms |
| Initial synchronous health/create/info, no catch-up tokens | 0.437346 | T.outage_and_resync_events: sync ending at 13.661352, seconds |
| Node queue/upload, full-state restore, range serialization/hash/chunk envelope, full-state save and capture-file write/hash | 40.165351 aggregate | Sum I.parent_extend_duration_seconds_including_snapshot - S - C0.server_prefill_seconds - C0.transfer_seconds |
| Node prefill across ten extends | 41.865963 | C0.server_prefill_seconds |
| Delta body reads | 397.354113 | C0.transfer_seconds; C0.wire_bytes=3641234956 |
| Synchronous full-node snapshot download/write/fsync | 2413.468032 | C0.snapshot_download_seconds_sum; 22106628552 bytes |
| Nine staged import requests | 2.508157 | Sum C0.chunks[status=staged].import_ms / 1000 |
| Empty old-slot save plus final import/apply request | 0.399364 | C0.chunks[-1].import_ms / 1000 |
| Other remote preparation, outside extend/import/sync | 0.073447 | C0.remote_prepare_seconds - E - M - sync |
| TTFT work outside remote preparation | 0.492071 | C0.ttft_seconds - C0.remote_prepare_seconds |
| TTFT endpoint | 2896.763843 | C0.ttft_seconds |
| Remaining stream/finish after first text | 0.167510 | C0.total_seconds - C0.ttft_seconds |
| Complete stream | 2896.931353 | C0.total_seconds |

E=2892.853458 s; R=2896.271772 s. Before mapping sync, the unassigned remainder is 41.168216 s; after mapping it, 40.730869 s remains, partitioned as 40.165351 inside extend + 0.073447 other remote preparation + 0.492071 outside remote preparation.

T0.catchup_tokens=0, catchup_seconds=0. Later pre_stage save at at_seconds=2913.568454 takes 3.609770 s / 3,641,294,792 bytes. It occurs AFTER this call and is not another import, nor part of the residual.

Chronological per chunk: node response body is read; the wrapper then synchronously captures a full node snapshot, writes the delta to disk, hashes both files; only then does it return the delta for staging/import and readback. Nine stages do not change the committed client prefix. The tenth request saves the still-empty old slot and applies all staged state. There is no evidence supporting overlap between these ten critical chunks.

## Growing turn 7

C7 = I component turn 7. Local old depth=104507; node critical export [104507,106849), 2,342 tokens, followed by one local prompt token. The call has 2,343 new prompt tokens and 17 output tokens; depth_after=106867.

| Phase, in execution order | Seconds | Source field |
|---|---:|---|
| Client rendering/tokenization, slot checks, held prompt token and first decoded text | Unknown separately; inside 0.601220 below | T.calls[turn=7] omits local_tail_seconds |
| Critical sync/catch-up wrapper | 3.616348 | T sync at 4216.995315: seconds; acknowledged 103821->103821, journal=104507 |
| Second sync confirms catch-up boundary | 0.310794 | T sync at 4217.306136: seconds; acknowledged 103821->104507 |
| Upload/queue/node state load-export-hash-save and evidence delta write/snapshot+delta hashing | 5.272069 aggregate | E-S-P-D |
| Node prefill of new exported range | 1.420419 | C7.server_prefill_seconds |
| Delta body read | 27.761830 | C7.transfer_seconds; wire_bytes=238500055 |
| Synchronous full-node snapshot download/write/fsync | 425.589585 | C7.snapshot_download_seconds_sum; bytes=3879941332 |
| Full old-slot recovery save plus final import | 4.033590 | C7.import_seconds = sole chunk import_ms/1000 |
| Other remote preparation outside extend/import/sync | 0.058632 | R-E-M-3.927141417 |
| TTFT work outside remote preparation | 0.601220 | TTFT-R |
| TTFT endpoint | 468.664485 | C7.ttft_seconds |
| Remaining stream/finish | 1.496112 | C7.total_seconds - C7.ttft_seconds |
| Complete stream | 470.160597 | C7.total_seconds |

E=460.043902 s; R=468.063265 s. After removing the capture, 43.074901 s remains. After prefill/transfer/import, 9.859062 s remains; mapping the two sync spans reduces this to 5.931921 s (5.272069 + 0.058632 + 0.601220).

The call's catch-up summary is 686 tokens, 3.275573 s, 0.383303 s native node prefill, 3,479 upload-body bytes. That request is nested in sync work above; its node prefill is nested again. Neither is additive to the sync rows. The summary spans all events since the prior call cursor, so its field alone would not establish TTFT membership. Here the two critical sync intervals and exact depth progression support the association.

T.per_call_resync reports 4,507 tokens / 458.301750 protocol seconds / 12.260779 catch-up seconds since reconnect. This is a multi-call event-window aggregate that also includes the critical turn-7 extend and its capture. It is not another phase to add to turn-7 TTFT.

## Growing turn 31

C31 = I component turn 31. Old local depth=134015; export [134015,136357), 2,342 tokens; one prompt token evaluated locally, then three output tokens; depth_after=136361.

| Phase, in execution order | Seconds | Source field |
|---|---:|---|
| Client rendering/tokenization, slot checks, held prompt token and first decoded text | Unknown separately; inside 0.767030 below | T.calls[turn=31] omits local_tail_seconds |
| Critical sync, already caught up | 0.311989 | T sync ending 7270.520368, seconds; acknowledged 134015->134015 |
| Upload/queue/node state load-export-hash-save and evidence delta write/snapshot+delta hashing | 6.636849 aggregate | E-S-P-D |
| Node prefill | 1.633869 | C31.server_prefill_seconds |
| Delta body read | 20.266240 | C31.transfer_seconds; wire_bytes=238500055 |
| Synchronous full-node snapshot download/write/fsync | 455.201414 | C31.snapshot_download_seconds_sum; bytes=4908118084 |
| Full old-slot recovery save plus final import | 5.631738 | C31.import_seconds = sole chunk import_ms/1000 |
| Other remote preparation outside extend/import/sync | 0.069649 | R-E-M-0.311988792 |
| TTFT work outside remote preparation | 0.767030 | TTFT-R |
| TTFT endpoint | 490.518778 | C31.ttft_seconds |
| Remaining stream/finish | 0.387109 | C31.total_seconds - C31.ttft_seconds |
| Complete stream | 490.905887 | C31.total_seconds |

E=483.738371 s; R=489.751748 s. TTFT minus capture=35.317364 s. Prefill+transfer+import=27.531847 s; remaining=7.785517 s, reduced to 7.473529 s after the critical sync association (6.636849 + 0.069649 + 0.767030).

The per-call cursor summary contains 226 catch-up tokens, 3.812165 s, 0.152570 s node prefill and 1,162 upload bytes. The depth-advancing sync is recorded earlier, at 7249.586482-7253.765436, followed by acknowledgement at 7254.805609-7255.149094 and repeated no-change syncs. The critical sync at 7270.208380-7270.520368 has no missing prefix. Adding the entire 3.812165 s would exceed the 0.381638 s available outside the critical extend/import even before the critical sync is counted. It is an earlier cursor-window catch-up, not an extra synchronous TTFT phase.

## Recorded timeline anchors

Growing at_seconds uses the driver's monotonic Events origin. Snapshot start/end below are the supplied I anchors. No cross-machine wall-clock subtraction was used.

| Call / export range | Snapshot start | Snapshot end | Snapshot s | Parent extend s (inclusive) | Prefill s | Delta body s | Import request s | Other extend s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 / 0-10876 | 59.277403 | 133.601819 | 74.324416 | 120.662376 | 3.102903 | 41.157493 | 0.341862 | 2.077564 |
| 0 / 10876-21752 | 187.904656 | 308.443715 | 120.539059 | 174.634637 | 3.332928 | 48.200189 | 0.267514 | 2.562460 |
| 0 / 21752-32628 | 366.277673 | 514.145483 | 147.867810 | 205.591134 | 3.575317 | 50.933712 | 0.270528 | 3.214294 |
| 0 / 32628-43504 | 560.954111 | 745.529260 | 184.575150 | 231.245921 | 3.981128 | 39.331299 | 0.270208 | 3.358344 |
| 0 / 43504-54380 | 788.755844 | 1038.791980 | 250.036136 | 293.138514 | 4.598327 | 34.424229 | 0.266925 | 4.079822 |
| 0 / 54380-65256 | 1085.838300 | 1356.277592 | 270.439292 | 317.374712 | 4.972183 | 37.795869 | 0.277236 | 4.167368 |
| 0 / 65256-76132 | 1410.123235 | 1694.018582 | 283.895348 | 337.593700 | 5.333512 | 43.057932 | 0.268874 | 5.306909 |
| 0 / 76132-87008 | 1737.642654 | 2104.136825 | 366.494171 | 409.981680 | 5.686559 | 32.728978 | 0.280105 | 5.071973 |
| 0 / 87008-97884 | 2164.094538 | 2541.371473 | 377.276934 | 437.104954 | 6.049026 | 48.375599 | 0.264905 | 5.403394 |
| 0 / 97884-99998 | 2569.328306 | 2907.348022 | 338.019715 | 365.525830 | 1.234079 | 21.348813 | 0.399364 | 4.923223 |
| 7 / 104507-106849 | 4249.941241 | 4675.530825 | 425.589585 | 460.043902 | 1.420419 | 27.761830 | 4.033590 | 5.272069 |
| 31 / 134015-136357 | 7296.837699 | 7752.039113 | 455.201414 | 483.738371 | 1.633869 | 20.266240 | 5.631738 | 6.636849 |

Import follows its parent extend, so that column is not part of the parent. Prefill, body transfer, snapshot and other-extend columns partition the parent. Snapshot/delta file hashes are in other-extend. The base final import is 0.399364 s; earlier rows are stages.

The supplied call at_seconds is appended AFTER stream completion and journal/slot verification. It cannot be used as the exact stream-end clock. Subtracting total yields only an upper bound on call start; adding TTFT to that bound yields only an upper bound on first-text receipt:

| Call | Call row at_seconds | Call start no later than | First text no later than | Known preceding/in-call anchors |
|---|---:|---:|---:|---|
| Base | 2909.954236 | 13.022883 | 2909.786726 | Initial sync 13.224005-13.661352; ten captures above |
| 7 | 4683.243659 | 4213.083062 | 4681.747547 | Sync 4213.378967-4216.995315 then 4216.995342-4217.306136; capture above |
| 31 | 7760.675622 | 7269.769735 | 7760.288513 | Critical sync 7270.208380-7270.520368; capture above |

The first-call JSONL has no comparable per-call absolute/monotonic start/end anchors. Its run-name timestamp is not its first hybrid-call start: local calls execute first. The chronological phase chain and durations are recoverable; exact absolute placement is not.

## Known suspect 1: full old-slot save

The r12 mechanism is real but is counted inside the growing-session import interval. At fca0fe31, proxy.py:829 starts import_started, lines 832-833 issue action=save for the final chunk, lines 835-836 issue import_delta, and line 837 stops the timer. Staged chunk timers contain no old-slot save. Current transaction cleanup (/abort_delta and backup unlink), readback and SQLite save happen outside import_ms.

| Call | Existing prefix at final save | Meter containing the save | Maximum save wall time allowed by that meter | Consequence for the unexplained remainder |
|---|---:|---|---:|---|
| First | Not applicable to old proxy | No proxy recovery save in 7e1a477b | No such operation | Cannot explain the 25.369948 s gap |
| Base | 0 | Final chunk save+import | Less than or equal to 0.399364 s | Already counted; no large old prefix |
| 7 | 104507 | Sole save+import | Less than or equal to 4.033590 s | Could dominate recorded import, cannot be added to the missing 9.859062 s |
| 31 | 134015 | Sole save+import | Less than or equal to 5.631738 s | Could dominate recorded import, cannot be added to the missing 7.785517 s |

For occupied Qwen slots, r24's no-checkpoint recovery-file formula is 156,894,792 + 34,844 * P bytes for one stream. It predicts 3,798,336,700 bytes at turn 7 and 4,826,513,452 bytes at turn 31. Attention tensors alone are 3,638,515,712 / 4,665,866,240 bytes. These are geometry estimates, not measured Mac save-file sizes; extra streams/checkpoints alter them. The formula is not an empty-slot size formula.

The r12 Mac fit for the whole fixed-539-token proxy interval, 0.281770 + 0.0000346993 * P seconds, gives 3.908090 / 4.931997 s at these depths. That supports the scale of the observed 4.033590 / 5.631738 s imports, but is not a stage estimate for these different 2,342-token imports. r12's CPU replay attributed 94.2% of its fitted depth slope to save. It does not measure Metal save time in the current calls.

Do not confuse client old-slot save with the NODE's full-state load/save on every extend. The latter are outside node prefill/body-transfer and remain in the extend residual.

## Known suspect 2: SHA-256

There are distinct hashing paths with different accounting:

1. Node delta body checksum during encode_delta. It occurs after range export and before response headers. Its cost is outside both node prefill and body-transfer meters and can explain part of the extend remainder.
2. Decoder delta checksum during read_delta_view/staging (old first-call code uses read_delta). This is INSIDE the import request meter. It cannot be added again to explain the residual. Both protocols also compute XXH3; timing the combined checksum function would not isolate SHA-256.
3. Driver evidence hashes of the complete downloaded node_snapshot and copied node_delta files, one pass each per chunk. These execute synchronously after the snapshot download timer stops, inside MeasuredNode.request. bench_common.sha256 reads files in 1 MiB blocks using hashlib. Thus subtracting snapshot_download_seconds_sum DOES NOT subtract this hashing or delta.write_bytes.
4. Prefix hashes cover token IDs, not GB of state. Model/binary identity hashes occur during setup before calls. Checkpoint/pre-stage file hashes after a call are not its TTFT.

The first node/client delta checksum code uses portable sha256_hash on the entire body. The newer state codec dispatches to CommonCrypto on Apple and SHA-NI on supported x86, unless forced portable; the supplied extracts do not record the actual runtime dispatch. Python evidence-file hashlib is a separate implementation. Do not assign it the portable C++ rate.

| Call | Node checksum body bytes, approximately | Decoder checksum body bytes, approximately, inside import | Exact synchronous evidence-file SHA-256 bytes outside download timer | Extend residual available for hashing AND other work |
|---|---:|---:|---:|---:|
| First | At most 2,004,023,525 | At most 2,004,023,525 | No growing-driver capture path | At most 19.658720 s, also contains sync/readback/journal work |
| Base | At most 3,641,234,956 | At most 3,641,234,956 | 25,747,863,508 = 22,106,628,552 snapshot + 3,641,234,956 delta | 40.165351 s |
| 7 | At most 238,500,055 | At most 238,500,055 | 4,118,441,387 = 3,879,941,332 + 238,500,055 | 5.272069 s |
| 31 | At most 238,500,055 | At most 238,500,055 | 5,146,618,139 = 4,908,118,084 + 238,500,055 | 6.636849 s |

Native checksum body counts are slightly below envelope bytes because headers and checksum trailers are excluded. Exact capture-file counts above include the complete envelopes. Those passes are established by code and successful capture fields; their elapsed times are not recorded.

A numerical consistency check, not a measurement: spending the ENTIRE growing extend remainder on evidence-file hashing alone would imply effective file-read-plus-SHA rates of 641.047 / 781.181 / 775.461 MB/s for base / turn 7 / turn 31. At a hypothetical 1 GB/s those hashes take 25.748 / 4.118 / 5.147 s; at 2 GB/s, 12.874 / 2.059 / 2.573 s. These are material fractions of the observed remainder. Node serialization, node hashing, upload/queue and delta writes also consume the same interval, so those rates are not measured Mac rates or a unique allocation of the gap.

For the first call, one node pass over at most 2.004 GB would consume the entire 19.658720 s remote remainder only at roughly 101.941 MB/s. At hypothetical 0.5 / 1 GB/s it takes about 4.008 / 2.004 s. This makes a partial contribution possible, while proving no actual duration. Client-side portable hashing is already inside the 42.423212 s import meter.

The base's per-chunk other-extend residual rises from 2.077564 s to roughly 5 s as full snapshot sizes grow; turn 7/31 residuals rise from 5.272069 to 6.636849 s despite identical 238.500 MB deltas. Evidence-file hash volume grows from 4.118 to 5.147 GB in those two calls, while the NODE full-prefix load/save also grows. These observations are consistent with full-prefix I/O/hash work and cannot distinguish it from node-state serialization. No standalone CPU hash benchmark was substituted for the missing Mac measurements.

## Instrumentation for the next timing-only Mac runs

Sent to agents1_hybrid_orch in #hybrid, topic prototype-go BEFORE this report, with a correction and addendum:

- Initial list: $usRbtrZccIbcE1eTCeAJNTgZEjkDCqJ6cIsSvE8ZPCY
- Base import/accounting correction: $9EUyIBB5XPsdm955roAgfCfZ-E3oOz1427UqcTycxPs
- Explicit node full-state load/save and retained local-tail fields: $IJPVHH3q2OGoRSRGQBJELcxNmyfgYJjgi1SaVg39IKM

Keep the same instrumentation for Qwen and Glimmer, with actual native/cache layout and backend identity recorded:

1. **Common span schema.** Record monotonic_ns start/end and duration with host/process/clock domain, call/session/transfer/chunk ID, n0/n1, byte counts, critical/background origin, and parent span. Record UTC only as an anchor. Do not subtract clocks from different hosts. Retain source, binary, model, driver/config hashes, priority, batch/ubatch and link identity.
2. **Client boundary.** Record bench request encode start/end separately; exact stream-call start, first response byte, first raw sampled token, first nonempty content/reasoning SSE delta, stream end, finish/reconciliation end, and post-call verification end. Token sampling, text availability and bench receipt are different boundaries.
3. **Proxy preparation.** Time rendering/template/layout/tokenization, token-prefix hashing, slot acquisition/queue/info, sync health/session/info/acknowledgement, JSON encoding and client-to-node upload. Retain critical versus background spans and exact overlap; emit catch-up tokens/upload bytes/node prefill under their parent sync.
4. **Node extend.** Record HTTP receipt/body complete, scheduler queue entry/acquisition, full load_state bytes/time, prefill start/end and backend synchronization, range sizing/export/allocation/tensor-to-host read, SHA-256 and XXH3 separately with bytes and actual backend, envelope encoding/copies, full save_state bytes/time, headers/first/last body write. Return these timings per chunk without including them again as additive parents.
5. **Import.** Time client_delta header parse/heterogeneous rewrite, loopback request upload/queue, checksum algorithms, cumulative-prefix hash, native parse/validation, staging and final apply, KV metadata backup and backend tensor copies. Separately time action=save request and actual bytes, tensor-to-host read, file write/flush, and the import_delta request. Preserve import_total plus each stage and final-request value, with their aggregation defined.
6. **Outside-import work.** Time /info and exact token/hash readback, SQLite journal save/commit, abort_delta, backup unlink, allocations/copies and any checkpoint save. Keep reconciliation after generation separate from last PROMPT-token evaluation before the first sample.
7. **Decoder tail.** Preserve existing local_tail_seconds, meter.local_prompt_ms and reconciliation_seconds in the extract. Record completion dispatch/queue, held prompt-token evaluation start/end, first sample/detokenization, SSE flush and bench receipt. A zero local_prefill_seconds on an offload must not be read as zero local compute.
8. **Evidence overhead.** Timing-only measured calls should omit --state-probes/checkpoint state capture. If captures are retained in another arm, meter snapshot HTTP/open/generation/stream/write/flush/fsync, delta.write_bytes, snapshot SHA-256, delta SHA-256, header checks/chmod and checkpoint/pre-stage save/hash as explicitly labelled instrumentation spans. Removing snapshot downloads alone does not remove instrumentation.
9. **Reconciliation.** Emit disjoint leaf-time totals and an explicit residual per call; verify that all leaves lie within their parent, avoid sums of parents and children, and retain unrounded original values. A bounded delay control in a chosen upload/export/hash/save stage should move that named stage and TTFT once, not transfer_ms or two additive buckets. This is a next-run instrumentation control, not a control executed here.

## Limits, verification and recovery notes

The supplied extracts can locate time in enclosing phases, not produce separate historical timings for every phase. Unknowns remain explicit: node queue versus upload/header wait, full-prefix load/save versus range export/checksums, capture file I/O versus hashing, individual proxy bookkeeping, held-token native compute, first sample versus first nonempty text. local_tail_seconds is present in the driver's original output contract but omitted from these extracts; it is unavailable here, not proof it was never measured.

Growing checkpoint10/fidelity is unmeasured because the backend label guard refused. Both timing arms are observational evidence from an aborted scenario. No inference correctness, full scenario acceptance, or production speedup is established here. TTFT minus snapshot is an arithmetic residual, not a measured timing-only counterfactual.

Reproducible arithmetic is in arithmetic.json. inputs.json records byte sizes and SHA-256 of the exact local evidence and diagnosis used. Source snapshots and the pinned driver worktree permit checking timer nesting. No analysis script file was added; calculations ran as task-local inline Python with PYTHONDONTWRITEBYTECODE=1 and on-disk TMPDIR.

Validation checks: per-call prefill/transfer/import totals match the per-chunk sums; snapshot durations match component totals; every residual partition reconciles to TTFT; nine stages plus the final request equal the base import total. Positive checks retain valid totals; negative accounting checks reject adding staged imports twice, adding turn-31 cursor catch-up as critical time, and treating post-verification call at_seconds as an exact stream endpoint. These check arithmetic/interpretation, not unrecorded runtime phases.

Operational probes: the requested driver object was absent from this checkout, then found in the existing hybrid-b object database. An initial local fetch used an incorrect full object name and exited 128; the corrected exact local-object fetch and detached-worktree creation exited 0. Optional-path searches and an exploratory dict-slice probe failed (exit 2 and exit 1 respectively) before analysis; corrected scoped reads succeeded. No network fetch/download or production code change was used. No shared process was stopped. Readiness and final validation/space logs are retained in this directory. Free disk remained above 28 GB; the observed post-worktree free space was 33,580,875,776 bytes, also above 28 GiB.

Final arithmetic validation: validation-03.log exited 0, including all four rounded report tables, exact per-chunk totals/nested partitions, input hashes and the three bounded negative accounting checks. Earlier validation-01.log exited 1 because its Markdown reader skipped a numeric cell suffixed with 'aggregate'; validation-02.log exited 1 because its source check matched an unrelated earlier at_seconds assignment outside call(). The corrected reader/scope passes; neither failure required changing measured values or accounting. No model/build tests were run because no executable behavior changed.
