#!/usr/bin/env bash
# Step 4: the main run with the reference settings: one slot, KV cache q8_0, flash attention on, turn deltas
# 512/2k/10k with 128 decoded tokens each. The context is the reference 262,144 tokens when the card fits it,
# otherwise the largest that fits. The depths are 16k, 50k, 100k, 150k and 200k where they fit, then the deepest
# level that leaves room for the deltas: 249k at 262,144, as in the reference run.
# Slot save/restore runs when the disk has room (the slot files of all levels take up to about 28 GB);
# SLOT_SAVE=1 forces it, SLOT_SAVE=0 skips it.
source "$(dirname "$0")/common.sh"
require_gpu_memory

ctx=$(fit_ctx 1)
[ "$ctx" -ge 32768 ] || die "GPU $GPU_INDEX fits only $ctx tokens next to the model"
log "context planned for the depth run: $ctx tokens"

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

# The context comes from a memory model. If the server still cannot allocate it, retry with 16k less: four attempts
# in all, each with its own server log.
attempt=1
until try_start_server "depth-$attempt" -c "$ctx" -np 1 ${server_slot_args[@]+"${server_slot_args[@]}"}; do
  [ "$attempt" -lt 4 ] || die "llama-server did not start in four attempts, the last with $ctx tokens; see results/server-depth-*.log"
  ctx=$((ctx - 16384))
  [ "$ctx" -ge 32768 ] || die "the context fell below 32k; see results/server-depth-*.log"
  attempt=$((attempt + 1))
  log "retrying the depth run with a context of $ctx tokens"
done

depths=$(python3 "$KITLIB" depth-list "$ctx")
log "depth run started at context $ctx, depths $depths; expect 20 to 60 minutes on a recent GPU"
bench --label "$(device_label)-q27b-q4km-q8kv" --notes "Qwen3.8-27B Q4_K_M, fa on, q8_0 KV, ctx $ctx, np 1" \
  --depths "$depths" ${bench_slot_args[@]+"${bench_slot_args[@]}"}
log "depth run finished"

# Remove only the slot files this run wrote.
rm -f "$slot_dir"/hybrid-bench-*.bin
