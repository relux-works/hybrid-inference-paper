#!/usr/bin/env bash
# Step 6c: realistic agent sessions. Several sessions start at 128k (the median depth of the measured calls is
# about 135k), and each goes through AGENT_TURNS turns (default 4) of a tool result and an answer, with sizes drawn
# from the measured call mix (tools/agents_loop.py). All sessions run at once, so one session's tool result is read
# while the others generate, as on a real client. Session counts 1, 2, 4, 8 as far as memory allows; each slot holds
# the depth plus 48k tokens of room. The start context is restored from work/slots-import/parallel-depth-<depth>.bin
# (or SLOT_FROM) when that file exists, otherwise it is filled once here and removed at the end. AGENTS_DEPTH changes
# the depth; SKIP_AGENTS=1 skips the step.
# GPU imports carry one stream. For np > 1, prepare_import_slot validates and
# restreams into work/slots-restream; fallbacks recreate it, and EXIT removes it.
source "$(dirname "$0")/common.sh"
if [ "${SKIP_AGENTS:-0}" = "1" ]; then log "agents step skipped"; exit 0; fi

depth=${AGENTS_DEPTH:-131072}
turns=${AGENT_TURNS:-4}
is_int "$depth" && is_int "$turns" || die "AGENTS_DEPTH and AGENT_TURNS must be numbers"
room=49152
per_slot=$(( (depth + room + 1023) / 1024 * 1024 ))
rope=()
[ "$per_slot" -le "$NATIVE_CTX" ] || rope=("${ROPE_LONG[@]}")
import_dir="${SLOT_FROM:-$WORK/slots-import}"
mode=()
slot_dir="$WORK/slots"
if [ -f "$import_dir/parallel-depth-$depth.bin" ]; then
  slot_dir="$import_dir"; mode=(--from-slot)
  import_sha256=$(sha256_of "$import_dir/parallel-depth-$depth.bin")
  log "restoring the start context from $import_dir, sha256 $import_sha256"
else
  mkdir -p "$slot_dir"
  [ "$(free_gb "$WORK")" -ge $(( depth * 34844 / 1000000000 + 5 )) ] || die "not enough free disk for the start context's slot file"
fi
usable=$(mac_usable_bytes)
per=$(( per_slot * KV_BYTES_PER_TOKEN + STATE_BYTES ))
agents=""
for n in 1 2 4 8; do [ $(( n * per )) -le "$usable" ] && agents="${agents:+$agents,}$n"; done
[ -n "$agents" ] || { log "the start context of $depth tokens plus room does not fit; agents step skipped"; exit 0; }
started=0
while [ -n "$agents" ]; do
  np=${agents##*,}
  if [ ${#mode[@]} -gt 0 ]; then
    if ! prepare_import_slot "$import_dir/parallel-depth-$depth.bin" "$np" "$import_sha256"; then
      agents=1
      continue
    fi
  fi
  if try_start_server "agents-$((depth / 1024))k-np$np" -c $((np * per_slot)) -np "$np" --slot-save-path "$slot_dir" \
       ${rope[@]+"${rope[@]}"}; then
    started=1
    break
  fi
  cleanup_restream
  case "$agents" in *,*) agents=${agents%,*} ;; *) agents="" ;; esac
  log "dropping $np sessions"
done
[ "$started" = "1" ] || { log "no server started (startup failure or insufficient restream disk); agents step skipped"; exit 0; }
before=$(snapshot agents-loop-)
log "agents step started: depth $depth, sessions $agents, $turns turns each"
run_child python3 "$KIT_DIR/tools/agents_loop.py" --url "http://127.0.0.1:$PORT" --outdir "$RESULTS" \
  --label "$(device_label)-q27b-agents$((depth / 1024))k" --depth "$depth" --agents "$agents" --turns "$turns" \
  --room "$room" ${mode[@]+"${mode[@]}"} --notes "np $np, ctx $((np * per_slot)), q8_0 KV, fa on" \
  || die "agents_loop.py failed"
files=()
while IFS= read -r f; do files+=("$f"); done < <(new_records agents-loop- "$before")
check_records ${files[@]+"${files[@]}"}
stop_server
cleanup_restream
# Remove only the start-context file this step wrote itself.
if [ ${#mode[@]} -eq 0 ]; then rm -f "$WORK/slots/agents-loop-$depth.bin"; fi
log "agents step finished"
