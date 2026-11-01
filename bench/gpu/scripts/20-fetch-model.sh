#!/usr/bin/env bash
# Step 2: downloads the exact GGUF file of the reference run and verifies its size and SHA-256.
# With MODEL_PATH pointing at an existing copy, only the verification runs.
source "$(dirname "$0")/common.sh"

if [ ! -f "$MODEL_PATH" ]; then
  mkdir -p "$(dirname "$MODEL_PATH")"
  have=$(free_gb "$(dirname "$MODEL_PATH")")
  [ "$have" -ge 21 ] || die "only $have GB free for the 19 GB model"
  log "downloading the model (19 GB) from Hugging Face, pinned revision 0669b986; the download resumes if interrupted"
  run_child curl -L --fail --retry 5 --retry-delay 15 -C - -o "$MODEL_PATH.part" "$MODEL_URL" \
    || die "download failed; rerun this script to resume"
  mv "$MODEL_PATH.part" "$MODEL_PATH"
fi

size=$(file_bytes "$MODEL_PATH")
[ "$size" = "$MODEL_BYTES" ] || die "model size $size bytes, expected $MODEL_BYTES; the file is incomplete or a different revision"
log "verifying SHA-256 (about a minute)"
sum=$(sha256_of "$MODEL_PATH")
[ "$sum" = "$MODEL_SHA256" ] || die "model SHA-256 $sum does not match $MODEL_SHA256; do not use this file for the comparison"
log "model verified: $(basename "$MODEL_PATH"), $size bytes, sha256 $sum"
