# Agent-session statistics

The paper's workload model comes from a year of agent sessions: how deep the context is at each model call, how
many new tokens each call brings (tool output, user text), how long the answers and the reasoning are, how much time
passes between calls, and how large tool results are. More people's statistics make that model better. This step
computes the same statistics on your machine.

## What it reads
Only on this machine, and only session logs of Claude Code, Codex CLI and Muse. The script looks in these places
(missing ones are skipped):
- Claude Code: `projects/` and `.agent-environment-backup/` under `~/.claude`, `~/.config/claude`, other `~/.claude*`
  folders that have `projects/`, the Xcode Claude agent folder
  (`~/Library/Developer/Xcode/CodingAssistant/ClaudeAgentConfig`) and `$CLAUDE_CONFIG_DIR`; plus
  `~/Library/Application Support/Claude/local-agent-mode-sessions` and `~/Library/Application Support/ClaudeUsageArchive`;
- Codex CLI: `sessions/`, `archived_sessions/` and `.agent-environment-backup/` under `~/.codex`, other `~/.codex*`
  folders that have sessions, and `$CODEX_HOME`;
- Muse: `muse/sessions` under `~/.local/share`, `~/Library/Application Support` and `$XDG_DATA_HOME`;
- the per-agent homes of the Curator tool, `~/.curator/environments/*`, if you use it;
- session backups in `~/Backups/AgentSessions` and `/Volumes/LaCie/Archives/AgentSessions`, ZIP archives included
  (read in place, never unpacked).

It never sends them anywhere.

## What it writes
One file, `results/session-stats-<UTC>.json`, with aggregate numbers only:
- call counts per agent and per model, and the logged token totals (prompt, cache, output, reasoning);
- distributions (percentiles) of context depth, new input per call, output and reasoning tokens, and time between
  calls;
- tool-result sizes, estimated from their character length.

It contains no message text, no tool output, no file paths, no project or repository names and no session ids. The
model names it lists are the ones your agents used.

## How to run
Only after the owner of the machine agrees:

```bash
CONSENT=yes bash bench/sessions/run.sh
```

It takes about 15 seconds per 600 MB of logs. Without `CONSENT=yes` the script stops and explains what it would do.
`SESSION_ARGS` accepts only `--sample N` (read at most N session files per agent), `--seed N`, `--min-calls N` and
`--max-mb X` (skip files larger than X MB); everything else is refused, including the tool's `--coverage` (a private
inventory of local paths) and `--csv` options. `SESSIONS_OUT=<folder>` writes the file somewhere other than
`bench/sessions/results/`. There is no option to limit the period: the statistics cover all logs found.

Look at the file before sending it. Send it only if you agree; nothing is sent automatically.
