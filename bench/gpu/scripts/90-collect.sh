#!/usr/bin/env bash
# Step 7: packs the results for sending. A scrubbed copy of results/ is made in work/collect-stage: the kit, work,
# model, results and home directories become <kit>, <work>, <models>, <results> and ~, and the user and host names
# become <user> and <host>. If anything that looks like a personal path remains, no archive is made and the places are
# listed. Otherwise MANIFEST.json is written and the copy is packed into qwen27b-gpu-bench-results-<UTC>.tar.gz in the
# kit directory. The raw results stay as they are.
source "$(dirname "$0")/common.sh"

stage="$WORK/collect-stage/results"
host_full=$(hostname 2>/dev/null || true)
# SCRUB_ALLOW: comma-separated paths the owner has looked at and accepts (see the prompt); each becomes --allow.
allow_args=()
IFS=',' read -r -a allowed <<< "${SCRUB_ALLOW:-}"
for a in ${allowed[@]+"${allowed[@]}"}; do [ -n "$a" ] && allow_args+=(--allow "$a"); done
python3 "$KITLIB" scrub-pack --results "$RESULTS" --stage "$stage" \
  --replace "$KIT_DIR=<kit>" --replace "$WORK=<work>" --replace "$(dirname "$MODEL_PATH")=<models>" \
  --replace "$RESULTS=<results>" --replace "$HOME=~" --user "$(id -un)" \
  --host "$host_full" --host "${host_full%%.*}" \
  --meta kit=qwen27b-gpu-bench --meta "kit_version=$KIT_VERSION" --meta "llama_cpp_commit=$LLAMA_COMMIT" \
  --meta "model=ggml-org/Qwen3.8-27B-GGUF@0669b98607d4 Qwen3.8-27B-Q4_K_M.gguf" --meta "model_sha256=$MODEL_SHA256" \
  --meta "benchmark_sha256=$BENCH_SHA256" ${allow_args[@]+"${allow_args[@]}"} \
  || die "the results were not packed: see the list above, and ask the owner how to proceed"

archive="$KIT_DIR/qwen27b-gpu-bench-results${LABEL_SUFFIX:-}-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
tar -czf "$archive.part" -C "$(dirname "$stage")" "$(basename "$stage")" || { rm -f "$archive.part"; die "tar failed"; }
mv "$archive.part" "$archive"
log "archive ready: $(basename "$archive") in the kit folder ($(du -h "$archive" | awk '{print $1}'))"
echo "$archive"
