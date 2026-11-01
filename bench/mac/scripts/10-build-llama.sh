#!/usr/bin/env bash
# Step 1: builds llama-server with Metal from the pinned llama.cpp commit (build 11087, as in the reference run).
# The clone keeps full commit history (only file contents are fetched lazily), so the build number matches.
source "$(dirname "$0")/common.sh"

src="$WORK/llama.cpp"
if [ ! -d "$src/.git" ]; then
  log "cloning $LLAMA_REPO"
  git clone --filter=blob:none --no-checkout "$LLAMA_REPO" "$src"
fi
git -C "$src" cat-file -e "$LLAMA_COMMIT^{commit}" 2>/dev/null || git -C "$src" fetch origin
git -C "$src" checkout --quiet --detach "$LLAMA_COMMIT"
[ "$(git -C "$src" rev-parse HEAD)" = "$LLAMA_COMMIT" ] || die "llama.cpp is not at $LLAMA_COMMIT"

log "configuring llama.cpp $LLAMA_COMMIT with Metal"
cmake -S "$src" -B "$src/build" -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=ON \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF > "$RESULTS/build-configure.log" 2>&1 \
  || die "cmake configure failed; see results/build-configure.log"
log "building llama-server"
run_child cmake --build "$src/build" --config Release -j "$(sysctl -n hw.ncpu)" --target llama-server \
  > "$RESULTS/build.log" 2>&1 || die "build failed; see results/build.log"

"$SERVER_BIN" --version > "$RESULTS/llama-server-version.txt" 2>&1 || true
log "built: $(tr '\n' ' ' < "$RESULTS/llama-server-version.txt")"
