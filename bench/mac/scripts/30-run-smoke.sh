#!/usr/bin/env bash
# Step 3: a two-minute smoke test of the server and the benchmark script.
source "$(dirname "$0")/common.sh"

start_server smoke -c 32768 -np 1
bench --label "$(device_label)-smoke" --smoke
log "smoke test finished; check results/hybrid-bench-*smoke*.md"
