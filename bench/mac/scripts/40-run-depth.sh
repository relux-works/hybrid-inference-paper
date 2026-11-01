#!/usr/bin/env bash
# Step 4: the main run with the reference settings. One slot, context 262,144, KV cache q8_0, flash attention on.
# Depths 16k, 50k, 100k, 150k, 200k and 249k, as in the reference run; turn deltas 512/2k/10k with 128 decoded tokens each. Slot save/restore runs when the disk
# has room for the slot files (up to about 28 GB at all depths); SLOT_SAVE=1 forces it, SLOT_SAVE=0 skips it.
source "$(dirname "$0")/common.sh"

slot_dir="$WORK/slots"
server_slot_args=()
bench_slot_args=()
mode="${SLOT_SAVE:-auto}"
room=$(free_gb "$WORK")
if [ "$mode" = "1" ] || { [ "$mode" = "auto" ] && [ "$room" -ge 35 ]; }; then
  mkdir -p "$slot_dir"
  server_slot_args=(--slot-save-path "$slot_dir")
  bench_slot_args=(--slot-save)
  log "slot save/restore on ($room GB free)"
else
  log "slot save/restore off ($room GB free, SLOT_SAVE=$mode)"
fi

start_server depth -c 262144 -np 1 ${server_slot_args[@]+"${server_slot_args[@]}"}
depths=$(python3 "$KITLIB" depth-list 262144)
log "depth run started; expect one to three hours"
bench --label "$(device_label)-q27b-q4km-q8kv" --notes "Qwen3.8-27B Q4_K_M, fa on, q8_0 KV, ctx 262144, np 1" \
  --depths "$depths" ${bench_slot_args[@]+"${bench_slot_args[@]}"}
log "depth run finished"

# Remove only the slot files this run wrote.
rm -f "$slot_dir"/hybrid-bench-*.bin
