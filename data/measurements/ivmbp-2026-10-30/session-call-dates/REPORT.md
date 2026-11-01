# Local saved session usage-event dates, full05

The complete configured inventory scan exited 0. Source reading is
`complete_for_discovered_sources`; **time coverage is `partial`** because valid
projection timestamps disagree for some deduplicated calls. No calls have missing
or invalid retained timestamps. This completes the requested aggregate date scan,
with those conflicts explicitly retained rather than resolved by guesswork.

| Agent | Calls | Contexts | First retained UTC event | Last retained UTC event | Distinct UTC dates | Calls with conflicting valid timestamps |
|---|---:|---:|---|---|---:|---:|
| claude | 285,129 | 2,867 | 2026-05-07T14:11:48.637000Z | 2026-10-28T14:26:26.469000Z | 119 | 169,887 |
| codex | 1,126,620 | 7,664 | 2025-11-18T22:58:13.635000Z | 2026-10-30T10:20:58.812000Z | 214 | 172,383 |
| muse | 116,445 | 2,644 | 2026-08-06T18:09:56.868201Z | 2026-10-30T04:02:31.931557Z | 42 | 6 |
| all | 1,528,194 | 13,175 | 2025-11-18T22:58:13.635000Z | 2026-10-30T10:20:58.812000Z | 233 | 342,276 |

Claude/Codex use envelope `timestamp`; Muse uses runtime.session `recorded_at`.
The first valid timestamp in discovery/reader order is retained; later duplicate
records can fill missing/invalid time. Other valid times flag the same call but
never add calls or dates. Naive ISO values assume UTC. Numeric values retain the
prior magnitude heuristic for positive seconds/ms/us/ns. The report does not
retain conflict spans, so it cannot establish that all conflicting projections
stay within one UTC day. These are **retained logged-event dates**, not verified
exact inference-start dates or a conflict-free accounting ledger.

Combined distinct days are a UTC set union: 233, not the sum of provider days
(375), nor the inclusive calendar span (347). Only dates containing retained calls
are counted. This is an active logging-day denominator, not uptime, wall time or
a billing period. Do not infer zero usage on uncovered dates.

## Source and run audit

- Same original source-manifest bytes as full04; no sampling, size cutoff or
  min-call exclusion. The root-presence inventory is unchanged: 98 present,
  9 optional absent, 8 present with no matching journals.
- 68,868 files/members / 138,372,855,715 observed uncompressed bytes;
  42,765 members across the same five ZIPs. 15,999 unique-content files parsed;
  52,869 full-content copies removed. All three providers have recorded usage.
- No root/read/parse/count/source-truncation/filter errors. One active Codex
  source appended after its observed boundary; input is bounded per file,
  not an atomic cross-session snapshot. Files created later are outside this run.
- 2,198 distinct parsed journals have no usage: consumption is unknown, not zero.
  81 zero-usage calls and 106 unknown-model labels remain explicit. The previously
  audited 890 Claude web chats without per-call usage are outside CLI telemetry.
- All source/manifest hashes match; 13 files in the immutable full04 evidence
  manifest were verified unchanged. Source time coverage is independent from
  source reading completeness. Conflicts are flags on unique calls, not errors
  suppressed by the parser.
- Process: 2026-10-30T10:20:58Z–10:52:56Z, actual wall 1,917.28s; tool timer
  1,911.0s. Data reflect per-file read boundaries within this run, not its finish.

## Keep snapshot denominators aligned

This is a later local inventory than full04, including six additional Codex backup
files and six additional Muse files. Claude counts/totals are unchanged. The
following deltas must not be attributed solely to a software speed or parser gain.

| Agent | full04 calls | full05 calls | Delta |
|---|---:|---:|---:|
| claude | 285,129 | 285,129 | +0 |
| codex | 1,123,109 | 1,126,620 | +3,511 |
| muse | 116,433 | 116,445 | +12 |
| all | 1,524,671 | 1,528,194 | +3,523 |

Use this package's `stats.json` together with its `call-dates.json` when updating
the study; do not silently combine full04 totals with full05 date denominators.
No need to replace the historical evidence. `new_in` remains a context-growth
heuristic, not billed uncached input or measured prefill. Muse cache accounting
is unverified, and reasoning is not added to output.

## Source delivery and privacy

Source: https://github.com/relux-works/hybrid-inference-paper/pull/3

Exact author-signed/main commit:
`ec7fd1a03fcfc6a0f3948d6d6e0df8f0e41d82ce`.
Script SHA256:
`99dce8012210a4ec961c82d0193255aa81ace74a0eda848428157ff74dcef37b`.
Sixteen Swift Testing fixture groups pass; six date groups fail on frozen1.4
specifically because `call_time` is absent. Actual author COMMENT review and
exact-head non-rewriting landing are complete. No hosted-CI execution is claimed.

This package contains only aggregate stats/date summaries, this interpretation
and a hash manifest. It excludes transcripts, per-call CSV, private coverage,
source paths/inventory, native session IDs, raw power logs and credentials.
