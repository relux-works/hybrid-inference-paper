# Ivan MacBook session-usage measurements

Delivered to the hybrid-inference lane on Ivan's explicit Matrix-sharing instruction.

- stats.json: unchanged full04 aggregate (agents and 49 model entries); numeric metrics/model names, no transcript text or native session identifiers.
- agent_session_stats.py: corrected standalone v1.4-local-audit, standard-library Python, no network or inference requests.
- REPORT.md: measurement coverage, corrections, validation and interpretation limits.
- MANIFEST.json: hashes and sizes of the four files above.

Read the supplied results directly; re-running is not required. For another host:

```sh
python3 -I -S -B agent_session_stats.py --auto --out stats.json --coverage private-coverage.json
```

Audit the actual host/backup layouts first. --auto covers recognized native/Curator/alternate-profile and supported backup layouts, not arbitrary unknown project-isolated homes. Additional roots require a JSON manifest and --sources sources.json:

```json
{"roots":{"claude":["/absolute/path/to/claude/projects"],"codex":["/absolute/path/to/codex/sessions"],"muse":["/absolute/path/to/muse/sessions"]},"zip_roots":["/absolute/path/to/backup/archives"]}
```

Keep source manifests and --coverage output private; this package intentionally excludes them. Exit0 means complete parsing for discovered sources, not universal discovery of every possible host path. Exit2 marks partial/empty results. Files without usage have unknown historical consumption.

The API differs from v1.0: no file-mtime --since filter; sample/min_calls/max_mb restrictions are explicit and report partial status. Default min_calls1 retains one-call contexts. CSV is optional and was not generated for this full run.

Original v1.0 attachment SHA256:0982d9641a18a2195d6cac3a3e0cc22c5509c2d2b4d2223353185af99325619d.
Corrected candidate SHA256:6774541d434448893ad5827a95c0c13e98fe5139aa8b7647c533d34138ce7c3d.
