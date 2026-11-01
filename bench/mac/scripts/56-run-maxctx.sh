#!/usr/bin/env bash
# Step 6b: aggregate decode of several sessions at the longest contexts this Mac holds. For each depth in
# MAXCTX_DEPTHS (default "260000 1040000"):
#   - if parallel-depth-<depth>.bin is in SLOT_FROM (a folder) or in work/slots-import, the slot made on a GPU with the
#     GPU kit's scripts/60-make-slots.sh is restored into every stream; its SHA-256 is logged for comparison with the
#     GPU's log, and the restore must bring back exactly the depth's tokens;
#   - otherwise the Mac fills the slot itself, which takes about two hours at 260k on an M3 Max; a depth above 262,144
#     tokens without a slot file is skipped (filling a million tokens would take about a day).
# Stream counts: 1, 2, 4, 6 and 8 where all slots fit in about three quarters of the memory next to the 19 GB model;
# if the server still cannot start, the largest count is dropped and the server is started again. Depths above
# 262,144 use the same YaRN rope settings as the GPU that made the slot. SKIP_MAXCTX=1 skips the step.
# GPU imports carry one stream. For np > 1, prepare_import_slot validates and
# restreams into work/slots-restream; fallbacks recreate it, and EXIT removes it.
source "$(dirname "$0")/common.sh"
if [ "${SKIP_MAXCTX:-0}" = "1" ]; then log "max-context step skipped"; exit 0; fi

for depth in ${MAXCTX_DEPTHS:-260000 1040000}; do
  is_int "$depth" || die "MAXCTX_DEPTHS: '$depth' is not a number"
  per_slot=$(( (depth + 2048 + 1023) / 1024 * 1024 ))
  rope=()
  [ "$per_slot" -le "$NATIVE_CTX" ] || rope=("${ROPE_LONG[@]}")
  slot_dir="$WORK/slots"
  mode=()
  import_dir="${SLOT_FROM:-$WORK/slots-import}"
  if [ -f "$import_dir/parallel-depth-$depth.bin" ]; then
    slot_dir="$import_dir"; mode=(--from-slot)
    import_sha256=$(sha256_of "$import_dir/parallel-depth-$depth.bin")
    log "depth $depth: restoring the slot file from $import_dir, sha256 $import_sha256"
  elif [ "$per_slot" -gt "$NATIVE_CTX" ]; then
    log "depth $depth: no slot file in SLOT_FROM or work/slots-import; skipped (make it on a GPU with the GPU kit's step 8)"; continue
  else
    mkdir -p "$slot_dir"
    need_gb=$(( depth * 34844 / 1000000000 + 5 ))
    if [ "$(free_gb "$WORK")" -lt "$need_gb" ]; then log "depth $depth needs $need_gb GB of free disk for its slot; skipped"; continue; fi
    log "depth $depth: no slot file, so this Mac fills it (about two hours at 260k on an M3 Max)"
  fi
  streams=$(mac_fit_streams "$depth" 1 2 4 6 8)
  if [ -z "$streams" ]; then log "depth $depth does not fit in this Mac's memory; skipped"; continue; fi
  started=0
  while [ -n "$streams" ]; do
    np=${streams##*,}
    if [ ${#mode[@]} -gt 0 ]; then
      if ! prepare_import_slot "$import_dir/parallel-depth-$depth.bin" "$np" "$import_sha256"; then
        streams=1
        continue
      fi
    fi
    if try_start_server "maxctx-$((depth / 1000))k-np$np" -c $((np * per_slot)) -np "$np" --slot-save-path "$slot_dir" \
         ${rope[@]+"${rope[@]}"}; then
      started=1
      break
    fi
    cleanup_restream
    case "$streams" in *,*) streams=${streams%,*} ;; *) streams="" ;; esac
    log "dropping $np streams at $((depth / 1000))k"
  done
  if [ "$started" = "0" ]; then log "depth $depth: no server started (startup failure or insufficient restream disk); skipped"; continue; fi
  before=$(snapshot parallel-depth-)
  run_child python3 "$KIT_DIR/tools/parallel_depth.py" --url "http://127.0.0.1:$PORT" --outdir "$RESULTS" \
    --label "$(device_label)-q27b-maxctx$((depth / 1000))k" --depth "$depth" --streams "$streams" ${mode[@]+"${mode[@]}"} \
    --notes "np $np, ctx $((np * per_slot)), q8_0 KV, fa on${rope[*]:+, ${rope[*]}}${mode[*]:+, slot made elsewhere}" \
    || die "parallel_depth.py failed at depth $depth"
  files=()
  while IFS= read -r f; do files+=("$f"); done < <(new_records parallel-depth- "$before")
  check_records ${files[@]+"${files[@]}"}
  stop_server
  cleanup_restream
  # Remove only the slot file this step wrote itself; imported slot files stay where they are.
  if [ ${#mode[@]} -eq 0 ]; then rm -f "$WORK/slots/parallel-depth-$depth.bin"; fi
done
log "max-context run finished"
