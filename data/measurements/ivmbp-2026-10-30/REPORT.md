# Full retained session-usage measurement — ivmbp, 2026-10-30 UTC

This is historical model-call usage, not an inference-speed benchmark. hybrid_bench.py was not run; no prefill/decode/KV-transfer rate was measured, and no model/provider request was made.

## Coverage and actual completion

Full04 completed exit0 in2582seconds (43m02s). No date/sample/size cap. Native live and Curator homes, alternate profiles and discovered project-isolated homes were included, along with current and older separate backups, retained divergent versions and5weekly ZIPs.68,856files/ZIPmembers (42,765ZIPmembers),138,319,544,913observed uncompressed bytes.52,863identical content copies removed;15,993distinct contents parsed.632,377duplicate call records removed.

1,524,671unique calls in13,169contexts with recorded usage. Zero read/JSON/usage/source-root errors and zero truncation or in-place source changes. Six active files appended after discovery; only their discovery-length prefixes were read. This is a bounded historical corpus view, not an atomic live snapshot.

| System | Contexts with usage | Calls | Input depth p50 | Input depth p90 | Estimated new_in p50 / p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Claude Code | 2,867 | 285,129 | 212,311 | 720,173 | 380 / 2,420 |
| Codex | 7,664 | 1,123,109 | 124,878 | 204,391 | 73 / 3,337 |
| Muse | 2,638 | 116,433 | 154,140 | 305,073 | 472 / 2,792 |

Token units. Combined input depth p50/p90:135,362/250,202. Combined estimated new_in p50/p90:158/3,052. Combined inter-call gap p50/p90:7.8/34.8seconds. See stats.json for all distributions, counts, depth bins, output/reasoning, tool estimates and per-model summaries.

Summed logged input250,712,809,698; cached245,888,959,316; output780,505,163; reasoning316,628,841. Inputs repeat context over successive calls; this is not unique corpus size or a bill. Reasoning is separate and must not be added to output.

## Corrections to the supplied v1.0 script

- Include backups, divergent versions, streamed ZIP members, native/Curator/alternate homes, and isolated homes from the audited explicit source inventory.
- Deduplicate physical paths/content and provider call/source-record identities across retained copies; preserve later usage maxima and distinguish actual unique calls from aliases.
- Preserve mixed modern/legacy Codex usage. Match cumulative aliases across different files in either discovery order, including optional zero-field format neighbors.
- Preserve Muse input_tokens as logged. The old value-dependent cache addition was removed because Muse cache semantics are unverified.
- Parse each file only to observed length; hash ZIP member bytes/CRC without extraction. Cache archive handles instead of reconstructing a ZIP central directory for every member.
- Retain one-call contexts, expose failures/empty sources/zero usage/unknown models, and fail with partial status instead of claiming clean results after malformed reads or explicit filters.

Validation:10Swift Testing groups passed on the producing Mac. Old-defect controls intentionally fail the relevant assertions for dropped legacy Codex usage, omitted ZIP-only calls, cross-file format duplicates, repeated ZIP-index loading and alternate-home omission. Independent aggregate readback checks file partitions, records minus duplicates, per-agent/all sums, model+unknown call counts and pinned candidate/source/original hashes. These are fixture/accounting checks, not runtime inference qualification.

## Interpretation limits for hybrid inference

- new_in is estimated context growth. It is not billed uncached input, actual network transfer, measured server prefill or a reconstruction of every prompt delta. Compaction, forks and reasoning retention affect it.
- Input/cache totals follow logged provider fields. Claude depth includes cache read/write; Codex input is its logged total; Muse input/cache semantics remain unverified and unmodified.
- Tool-result token estimates use3.6characters/token.
-2,198distinct parsed journals contain no usage; historical consumption is unknown.81calls record zero usage;106calls lack model labels.890Claude web-export chats have no per-call usage and are excluded.
- Context counts mean contexts with usage, not every failed/empty journal. Legacy cumulative fallback identities cannot prove equivalence across arbitrary forks.
- Deleted/unretained and remote-only journals cannot be reconstructed. No transcript, private coverage, source paths, native IDs, credentials, project/task details or per-call CSV is included in this package.
