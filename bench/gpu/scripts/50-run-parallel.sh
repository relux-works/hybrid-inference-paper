#!/usr/bin/env bash
# Step 5: parallel decode streams at 32k, as in the reference run (-np 4, 35,000 tokens per slot). A card that cannot
# hold four such slots next to the model runs two; one that cannot hold two skips the step. SKIP_PARALLEL=1 skips it.
source "$(dirname "$0")/common.sh"
if [ "${SKIP_PARALLEL:-0}" = "1" ]; then log "parallel step skipped (SKIP_PARALLEL=1)"; exit 0; fi
require_gpu_memory

per_slot=35000
fits=$(fit_streams $((per_slot - 1024)) 2 4)
if [ -z "$fits" ]; then
  log "parallel step skipped: GPU $GPU_INDEX cannot hold two slots of $per_slot tokens next to the model"
  exit 0
fi
for np in 4 2; do
  case ",$fits," in *",$np,"*) ;; *) continue ;; esac
  if try_start_server "par$np" -c $((np * per_slot)) -np "$np"; then
    bench --label "$(device_label)-q27b-par$np" --notes "$np streams at 32k, np $np, ctx $((np * per_slot))" \
      --only-parallel --parallel "$np" --parallel-depth 32k
    log "parallel run finished with $np streams"
    exit 0
  fi
  log "the server did not start with $np slots"
done
log "parallel step skipped: the server did not start with two or four slots; see results/server-par*.log"
