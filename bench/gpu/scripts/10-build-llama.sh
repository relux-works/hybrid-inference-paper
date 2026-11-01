#!/usr/bin/env bash
# Step 1: builds llama-server with CUDA from the pinned llama.cpp commit (build 11087, as in the reference run).
# Only the selected GPU's architecture is compiled, which keeps the build to a few minutes.
source "$(dirname "$0")/common.sh"

command -v nvcc >/dev/null 2>&1 || die "nvcc not found: install the CUDA toolkit first (see scripts/00-check.sh)"
cc=$(gpu_query compute_cap)
[ -n "$cc" ] || die "cannot read the compute capability of GPU $GPU_INDEX"
arch="${CUDA_ARCH:-${cc//./}}"

src="$WORK/llama.cpp"
if [ ! -d "$src/.git" ]; then
  log "cloning $LLAMA_REPO"
  git clone --filter=blob:none --no-checkout "$LLAMA_REPO" "$src"
fi
git -C "$src" cat-file -e "$LLAMA_COMMIT^{commit}" 2>/dev/null || git -C "$src" fetch origin
git -C "$src" checkout --quiet --detach "$LLAMA_COMMIT"
[ "$(git -C "$src" rev-parse HEAD)" = "$LLAMA_COMMIT" ] || die "llama.cpp is not at $LLAMA_COMMIT"

log "configuring llama.cpp $LLAMA_COMMIT with CUDA for architecture $arch"
cmake -S "$src" -B "$src/build" -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="$arch" \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_CURL=OFF > "$RESULTS/build-configure.log" 2>&1 \
  || die "cmake configure failed; see results/build-configure.log"
log "building llama-server (several minutes)"
run_child cmake --build "$src/build" --config Release -j "$(nproc)" --target llama-server \
  > "$RESULTS/build.log" 2>&1 || die "build failed; see results/build.log"

"$SERVER_BIN" --version > "$RESULTS/llama-server-version.txt" 2>&1 || true
log "built: $(tr '\n' ' ' < "$RESULTS/llama-server-version.txt")"
