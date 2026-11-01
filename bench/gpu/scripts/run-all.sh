#!/usr/bin/env bash
# Runs steps 0-7 in order and stops at the first failure.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
# A kill or a Ctrl-C sent to run-all.sh is passed on to the step it is running, which then stops its server and
# frees the lock.
child=""
forward() { if [ -n "$child" ]; then kill "$child" 2>/dev/null; wait "$child" 2>/dev/null; fi; }
trap 'forward; exit 143' TERM
trap 'forward; exit 130' INT
for step in 00-check 10-build-llama 20-fetch-model 30-run-smoke 40-run-depth 50-run-parallel 55-run-scaling 57-run-agents 90-collect; do
  if [ "$step" = "50-run-parallel" ] && [ "${SKIP_PARALLEL:-0}" = "1" ]; then echo "=== $step skipped ==="; continue; fi
  echo "=== $step ==="
  bash "$here/$step.sh" &
  child=$!
  wait "$child"
  child=""
done
