#!/usr/bin/env bash
# Step 5: four parallel decode streams at 32k with the reference server settings (-np 4, -c 140000). If the server
# cannot start with them, the step is skipped and says so. SKIP_PARALLEL=1 skips it.
source "$(dirname "$0")/common.sh"
if [ "${SKIP_PARALLEL:-0}" = "1" ]; then log "parallel step skipped (SKIP_PARALLEL=1)"; exit 0; fi

if ! try_start_server par4 -c 140000 -np 4; then
  log "parallel step skipped: the server did not start with four slots; see results/server-par4.log"
  exit 0
fi
bench --label "$(device_label)-q27b-par4" --notes "4 streams at 32k, np 4, ctx 140000" \
  --only-parallel --parallel 4 --parallel-depth 32k
log "parallel run finished"
