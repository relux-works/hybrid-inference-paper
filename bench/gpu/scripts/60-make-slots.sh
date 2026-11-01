#!/usr/bin/env bash
# Step 8 (optional): slot files for long contexts, made on the GPU for clients that would need hours or a day to fill
# them (a Mac reads 260k tokens in about two hours and a million in about a day). Each file holds one session filled to
# the depth with the kit's synthetic tokens; the client restores it with scripts/56-run-maxctx.sh of the Mac kit.
# Each file carries one KV stream (-np 1). The Mac kit restreams it for its server's -np,
# preserving the import and all attention/recurrent state bytes.
# Depths above 262,144 tokens use YaRN rope scaling (common.sh, ROPE_LONG), and the client uses the same.
# SLOT_DEPTHS lists the depths (default "260000 1040000"). The files go to work/slots-export, a folder no other step
# cleans; copy them into work/slots-import of the Mac kit.
source "$(dirname "$0")/common.sh"
require_gpu_memory

slot_dir="$WORK/slots-export"
mkdir -p "$slot_dir"
for depth in ${SLOT_DEPTHS:-260000 1040000}; do
  is_int "$depth" || die "SLOT_DEPTHS: '$depth' is not a number"
  ctx=$(( (depth + 2048 + 1023) / 1024 * 1024 ))
  rope=()
  [ "$ctx" -le "$NATIVE_CTX" ] || rope=("${ROPE_LONG[@]}")
  if [ "$(fit_ctx 1)" -lt "$ctx" ] && [ "$ctx" -le "$MAX_CTX" ]; then
    log "depth $depth does not fit on this card; skipped"; continue
  fi
  if [ "$ctx" -gt "$MAX_CTX" ] && [ $(( ctx * KV_BYTES_PER_TOKEN + STATE_BYTES )) -gt "$(usable_bytes)" ]; then
    log "depth $depth does not fit on this card; skipped"; continue
  fi
  need_gb=$(( depth * 34844 / 1000000000 + 5 ))
  if [ "$(free_gb "$WORK")" -lt "$need_gb" ]; then log "depth $depth needs $need_gb GB of free disk for its slot file; skipped"; continue; fi
  if ! try_start_server "slot-$((depth / 1000))k" -c "$ctx" -np 1 --slot-save-path "$slot_dir" ${rope[@]+"${rope[@]}"}; then
    log "the server did not start with a context of $ctx; depth $depth skipped"; continue
  fi
  before=$(snapshot parallel-depth-)
  run_child python3 "$KIT_DIR/tools/parallel_depth.py" --url "http://127.0.0.1:$PORT" --outdir "$RESULTS" \
    --label "$(device_label)-q27b-slot$((depth / 1000))k" --depth "$depth" --fill-only \
    --notes "slot file for clients; ctx $ctx${rope[*]:+, ${rope[*]}}" || die "parallel_depth.py failed at depth $depth"
  files=()
  while IFS= read -r f; do files+=("$f"); done < <(new_records parallel-depth- "$before")
  check_records ${files[@]+"${files[@]}"}
  stop_server
  f="$slot_dir/parallel-depth-$depth.bin"
  [ -f "$f" ] || die "the slot file $f was not written"
  log "slot file ready: work/slots-export/parallel-depth-$depth.bin, $(file_bytes "$f") bytes, sha256 $(sha256_of "$f")"
done
log "slot files done; copy them into work/slots-import of the Mac kit (see AGENT_PROMPT.md)"
