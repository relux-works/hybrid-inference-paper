#!/usr/bin/env bash
# Agent-session statistics for the hybrid-inference paper, run only with the machine owner's consent.
# Reads Claude Code, Codex and Muse session logs on this machine with tools/agent_session_stats.py and writes one file
# of aggregate numbers: call depths, new input per call, output and reasoning tokens, time between calls, tool-result
# sizes and per-model usage. No message text, file paths, project names or session ids. Nothing is uploaded.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
script="$repo/tools/agent_session_stats.py"
SCRIPT_SHA256="65adced2c7ee07d814a708f73d791703b12a4df62de53dc8f00ac133d5ae0b67"   # agent_session_stats 1.6-model-usage
out_dir="${SESSIONS_OUT:-$here/results}"

if [ "${CONSENT:-}" != "yes" ]; then
  cat >&2 <<'MSG'
This step reads the local agent session logs of this machine (Claude Code, Codex, Muse) and writes only aggregate
numbers. Ask the owner first and explain what it reads and writes (bench/sessions/README.md). If they agree, run:
  CONSENT=yes bash bench/sessions/run.sh
MSG
  exit 2
fi
command -v python3 >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }
have=$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$script")
if [ "$have" != "$SCRIPT_SHA256" ]; then
  echo "tools/agent_session_stats.py does not match its pinned SHA-256; restore the original file" >&2
  exit 1
fi
# SESSION_ARGS may hold only these options, each with a number: --sample N, --seed N, --min-calls N, --max-mb X.
# Anything else is refused, so the private coverage inventory (--coverage), the per-call CSV (--csv) and other
# output paths cannot be produced through this step.
set -- ${SESSION_ARGS:-}
extra=()
while [ $# -gt 0 ]; do
  case "$1" in
    --sample|--seed|--min-calls)
      [ $# -ge 2 ] && printf '%s' "$2" | grep -Eq '^[0-9]+$' || { echo "SESSION_ARGS: $1 needs a whole number" >&2; exit 1; }
      extra+=("$1" "$2"); shift 2 ;;
    --max-mb)
      [ $# -ge 2 ] && printf '%s' "$2" | grep -Eq '^[0-9]+(\.[0-9]+)?$' || { echo "SESSION_ARGS: $1 needs a number" >&2; exit 1; }
      extra+=("$1" "$2"); shift 2 ;;
    *) echo "SESSION_ARGS: '$1' is not allowed; allowed are --sample, --seed, --min-calls and --max-mb" >&2; exit 1 ;;
  esac
done
mkdir -p "$out_dir"
out="$out_dir/session-stats-$(date -u +%Y%m%dT%H%M%SZ).json"
# The script exits 0 for a complete scan of the discovered sources and 2 for a partial one (for example with --sample);
# anything else is a failure.
status=0
python3 "$script" --auto --out "$out" ${extra[@]+"${extra[@]}"} || status=$?
rm -f "${out%.json}.pid"
if [ "$status" = "2" ] && [ ! -s "$out" ]; then status=1; fi
case "$status" in
  0) echo "complete scan of the discovered sources" ;;
  2) echo "partial scan (sampling, failed files or no calls): the file is valid but marked partial" ;;
  *) rm -f "$out"; echo "agent_session_stats.py failed with exit $status" >&2; exit "$status" ;;
esac
python3 - "$out" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
keys = [k for k in r if not isinstance(r[k], (dict, list))]
print("wrote", sys.argv[1])
print("top-level fields:", ", ".join(sorted(r.keys())))
print("scalar fields:", {k: r[k] for k in keys})
PY
echo "Show this file to the owner. Send it only if they agree."
