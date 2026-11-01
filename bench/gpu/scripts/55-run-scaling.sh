#!/usr/bin/env bash
# Step 6: how aggregate decode grows with the number of parallel agents at realistic depths. One prefill per depth;
# the saved slot is restored into every stream (tools/parallel_depth.py). The stream counts are the candidates
# 1, 2, 4, 8, 16, 32 at 64k, 1, 2, 4, 8, 16 at 128k and 1, 2, 4, 8 at 260k (nearly the full native context) that
# fit in the card's memory next to the model. If the
# server cannot start with the largest count, that count is dropped and the server is started again.
# SKIP_SCALING=1 skips the step.
source "$(dirname "$0")/common.sh"
require_gpu_memory
if [ "${SKIP_SCALING:-0}" = "1" ]; then log "scaling step skipped"; exit 0; fi

slot_dir="$WORK/slots"
mkdir -p "$slot_dir"
if [ "$(free_gb "$WORK")" -lt 12 ]; then log "scaling step skipped: it needs 12 GB of free disk for the saved slot"; exit 0; fi

for depth in 65536 131072 260000; do
  case "$depth" in
    65536) streams=$(fit_streams "$depth" 1 2 4 8 16 32) ;;
    131072) streams=$(fit_streams "$depth" 1 2 4 8 16) ;;
    *) streams=$(fit_streams "$depth" 1 2 4 8) ;;
  esac
  per_slot=$((depth + 1024))
  case "$depth" in 65536|131072) dl="$((depth / 1024))k" ;; *) dl="$((depth / 1000))k" ;; esac
  started=0
  while [ -n "$streams" ]; do
    np=${streams##*,}
    if try_start_server "scale-$dl-np$np" -c $((np * per_slot)) -np "$np" --slot-save-path "$slot_dir"; then
      started=1
      break
    fi
    case "$streams" in *,*) streams=${streams%,*} ;; *) streams="" ;; esac
    log "dropping $np streams at $dl"
  done
  if [ "$started" = "0" ]; then log "depth $dl does not fit on this card; skipped"; continue; fi
  before=$(snapshot parallel-depth-)
  run_child python3 "$KIT_DIR/tools/parallel_depth.py" --url "http://127.0.0.1:$PORT" --outdir "$RESULTS" \
    --label "$(device_label)-q27b-depth$dl" --depth "$depth" --streams "$streams" \
    --notes "np $np, ctx $((np * per_slot)), q8_0 KV, fa on" || die "parallel_depth.py failed at $dl"
  files=()
  while IFS= read -r f; do files+=("$f"); done < <(new_records parallel-depth- "$before")
  check_records ${files[@]+"${files[@]}"}
  stop_server
  rm -f "$slot_dir/parallel-depth-$depth.bin"
done
log "scaling run finished"
