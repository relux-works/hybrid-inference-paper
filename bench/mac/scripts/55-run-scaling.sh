#!/usr/bin/env bash
# Step 6 (new, not in the reference): how aggregate decode grows with the number of parallel agents at
# realistic depths. One prefill per depth; the saved slot is restored into every stream (tools/parallel_depth.py).
# The stream counts are the candidates 1, 2, 4, 8, 16, 24 at 64k and 1, 2, 4, 8, 12 at 128k whose slots fit in about
# three quarters of the memory next to the 19 GB model (up to 24 and 12 on 128 GB, 8 and 4 on 64 GB).
# If the server cannot start with the largest count, that count is dropped and the server is started again.
# SKIP_SCALING=1 skips the step.
source "$(dirname "$0")/common.sh"
if [ "${SKIP_SCALING:-0}" = "1" ]; then log "scaling step skipped"; exit 0; fi

plans=""
s64=$(mac_fit_streams 65536 1 2 4 8 16 24); [ -z "$s64" ] || plans="65536:$s64"
s128=$(mac_fit_streams 131072 1 2 4 8 12); [ -z "$s128" ] || plans="$plans 131072:$s128"
[ -n "$plans" ] || { log "no depth fits in this Mac's memory; scaling step skipped"; exit 0; }

slot_dir="$WORK/slots"
mkdir -p "$slot_dir"
if [ "$(free_gb "$WORK")" -lt 12 ]; then log "scaling step skipped: it needs 12 GB of free disk for the saved slot"; exit 0; fi

for plan in $plans; do
  depth=${plan%%:*}
  streams=${plan#*:}
  per_slot=$((depth + 1024))
  started=0
  while [ -n "$streams" ]; do
    np=${streams##*,}
    if try_start_server "scale-$((depth / 1024))k-np$np" -c $((np * per_slot)) -np "$np" --slot-save-path "$slot_dir"; then
      started=1
      break
    fi
    case "$streams" in *,*) streams=${streams%,*} ;; *) streams="" ;; esac
    log "dropping $np streams at $((depth / 1024))k"
  done
  if [ "$started" = "0" ]; then log "depth $((depth / 1024))k does not fit on this Mac; skipped"; continue; fi
  before=$(snapshot parallel-depth-)
  run_child python3 "$KIT_DIR/tools/parallel_depth.py" --url "http://127.0.0.1:$PORT" --outdir "$RESULTS" \
    --label "$(device_label)-q27b-depth$((depth / 1024))k" --depth "$depth" --streams "$streams" \
    --notes "np $np, ctx $((np * per_slot)), q8_0 KV, fa on" || die "parallel_depth.py failed at $((depth / 1024))k"
  files=()
  while IFS= read -r f; do files+=("$f"); done < <(new_records parallel-depth- "$before")
  check_records ${files[@]+"${files[@]}"}
  stop_server
  rm -f "$slot_dir/parallel-depth-$depth.bin"
done
log "scaling run finished"
