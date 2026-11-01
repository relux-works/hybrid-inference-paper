#!/usr/bin/env bash
# Shared settings and helpers for the Qwen3.8-27B long-context benchmark kit, NVIDIA GPU edition (Linux).
# The model, the llama.cpp commit, the server flags and the benchmark script are the same as in the Mac kit and in
# the reference run (Apple M3 Max 128 GB, 2026-10-30), so GPU and Mac results compare directly.
set -euo pipefail

KIT_VERSION="1.2.1"
KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${WORK:-$KIT_DIR/work}"
RESULTS="${RESULTS:-$KIT_DIR/results}"
KITLIB="$KIT_DIR/scripts/kitlib.py"

LLAMA_REPO="https://github.com/ggml-org/llama.cpp"
LLAMA_COMMIT="${LLAMA_COMMIT:-c21284cdf5fd833b90ac1f824cdf8065e2700dc4}"   # llama.cpp build 11087
MODEL_URL="https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF/resolve/0669b98607d47046c7c2b3f801011d54a08cfccf/Qwen3.8-27B-Q4_K_M.gguf"
MODEL_SHA256="31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34"
MODEL_BYTES=18973870432
MODEL_PATH="${MODEL_PATH:-$WORK/models/Qwen3.8-27B-Q4_K_M.gguf}"
BENCH="$KIT_DIR/tools/hybrid_bench.py"
BENCH_SHA256="c9f1b4966b080ba81c2b0df3d001b73fd1732fd67a8891a14c04ef81f106b095"   # hybrid_bench 1.1, frozen

# One GPU per run, so a multi-GPU host measures a single card. GPU_INDEX picks it. nvidia-smi numbers GPUs in PCI
# bus order; CUDA is told to use the same order, so the index means the same card to both.
GPU_INDEX="${GPU_INDEX:-0}"
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES="$GPU_INDEX"

# Memory model of the 27B model with a q8_0 KV cache, for sizing the context to the card:
# 34,816 bytes of attention KV per token (34 bytes per 32 values; a saved slot measures 34,844 with metadata) and a
# fixed 156,894,784-byte recurrent state per slot. RESERVE_MIB covers the CUDA context and compute buffers; raise it
# if the server still fails to allocate.
KV_BYTES_PER_TOKEN=34816
STATE_BYTES=156894784
RESERVE_MIB="${RESERVE_MIB:-2560}"
MAX_CTX=262144

# Depths above the model's native 262,144 tokens use YaRN rope scaling with factor 4 (up to 1,048,576 tokens). A slot
# made with these settings must be restored with the same settings.
ROPE_LONG=(--rope-scaling yarn --rope-scale 4 --yarn-orig-ctx 262144)
NATIVE_CTX=262144

PORT="${PORT:-8080}"
SERVER_BIN="$WORK/llama.cpp/build/bin/llama-server"
PID_FILE="$WORK/server.pid"
SERVER_PID=""

mkdir -p "$WORK" "$RESULTS"

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$RESULTS/kit.log" >&2; }
die() { log "ERROR: $*"; exit 1; }

sha256_of() { sha256sum "$1" | awk '{print $1}'; }
file_bytes() { stat -L -c %s "$1"; }
free_gb() { df -Pk "$1" | awk 'NR==2 {printf "%d", $4 / 1048576}'; }
is_int() { case "$1" in ''|*[!0-9]*) return 1 ;; *) return 0 ;; esac; }

# gpu_query <field>: one nvidia-smi field of the selected GPU, without units; empty when unavailable.
gpu_query() {
  { nvidia-smi -i "$GPU_INDEX" --query-gpu="$1" --format=csv,noheader,nounits 2>/dev/null || true; } | head -1 | sed -E 's/^ +| +$//g'
}

# gpu_mib <field>: a memory field in MiB; stops the step when nvidia-smi does not report a number (MIG, some vGPUs).
gpu_mib() {
  local v
  v=$(gpu_query "$1")
  is_int "$v" || die "nvidia-smi reports '$v' for $1 on GPU $GPU_INDEX; this kit needs a whole GPU (no MIG slice)"
  echo "$v"
}

# require_gpu_memory: stops the step when nvidia-smi does not report free memory as a number. Called at the top level of
# a step, where a failure ends the step (inside $(...) it would end only the subshell).
require_gpu_memory() {
  local v
  local f
  for f in memory.free memory.total; do
    v=$(gpu_query "$f")
    is_int "$v" || die "nvidia-smi reports '$v' for $f on GPU $GPU_INDEX; this kit needs a whole GPU (no MIG slice)"
  done
}

# Device label for result file names, for example nvidia-geforce-rtx-3090-24g.
device_label() {
  local name
  name=$(gpu_query name | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')
  printf '%s-%sg%s' "$name" "$(( ($(gpu_mib memory.total) + 512) / 1024 ))" "${LABEL_SUFFIX:-}"
}

# Bytes the kit may plan with: free GPU memory now, minus the weights and RESERVE_MIB.
usable_bytes() { echo $(( $(gpu_mib memory.free) * 1048576 - MODEL_BYTES - RESERVE_MIB * 1048576 )); }

# fit_ctx <slots>: the largest per-slot context, a multiple of 1024 and at most MAX_CTX, such that <slots> slots fit.
# Prints 0 when not even 1024 tokens per slot fit.
fit_ctx() {
  local slots=$1 usable per_slot
  usable=$(usable_bytes)
  per_slot=$(( usable / slots - STATE_BYTES ))
  if [ "$per_slot" -le 0 ]; then echo 0; return; fi
  per_slot=$(( per_slot / KV_BYTES_PER_TOKEN / 1024 * 1024 ))
  [ "$per_slot" -le "$MAX_CTX" ] || per_slot=$MAX_CTX
  echo "$per_slot"
}

# fit_streams <depth> <candidates...>: prints the candidates, in order, whose slots of depth+1024 tokens all fit.
fit_streams() {
  local depth=$1; shift
  local usable per out="" n
  usable=$(usable_bytes)
  per=$(( (depth + 1024) * KV_BYTES_PER_TOKEN + STATE_BYTES ))
  for n in "$@"; do
    if [ $(( n * per )) -le "$usable" ]; then out="${out:+$out,}$n"; fi
  done
  echo "$out"
}

port_busy() { (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; }

# is_kit_server <pid>: true when the process runs this kit's llama-server binary (its absolute path is in the command).
is_kit_server() {
  local cmd
  cmd=$(ps -p "$1" -o command= 2>/dev/null || true)
  case "$cmd" in *"$SERVER_BIN "*|*"$SERVER_BIN") return 0 ;; *) return 1 ;; esac
}

# A PID file left by an earlier run that ended without cleanup (reboot, kill, agent timeout). The process is stopped
# only if it is still this kit's llama-server; any other process with that PID is left alone.
clear_stale_server() {
  [ -f "$PID_FILE" ] || return 0
  local pid
  pid=$(head -1 "$PID_FILE" 2>/dev/null || true)
  rm -f "$PID_FILE"
  if is_int "$pid" && is_kit_server "$pid"; then
    log "stopping a llama-server left over from an earlier run of this kit (pid $pid)"
    SERVER_PID=$pid
    stop_server
  else
    log "removed a stale work/server.pid ($pid); that process is not this kit's server and was not touched"
  fi
}

# try_start_server <log name> <extra llama-server arguments...>: returns 1, with the server stopped, if it does not
# come up (for example when the context does not fit in GPU memory). Flags shared with the reference run: all layers
# on the GPU, flash attention on, KV cache q8_0.
try_start_server() {
  local name=$1; shift
  [ -x "$SERVER_BIN" ] || die "llama-server not built yet: run scripts/10-build-llama.sh"
  [ -f "$MODEL_PATH" ] || die "model not found at $MODEL_PATH: run scripts/20-fetch-model.sh"
  clear_stale_server
  if port_busy; then die "port $PORT is already in use by another program; free it or rerun with PORT=<other port>"; fi
  "$SERVER_BIN" -m "$MODEL_PATH" --host 127.0.0.1 --port "$PORT" -ngl 999 -fa on -ctk q8_0 -ctv q8_0 "$@" \
    > "$RESULTS/server-$name.log" 2>&1 &
  SERVER_PID=$!
  echo "$SERVER_PID" > "$PID_FILE"
  log "llama-server ($name) started with pid $SERVER_PID on GPU $GPU_INDEX; arguments: $*"
  local i=0
  while [ $i -lt 900 ]; do
    if kill -0 "$SERVER_PID" 2>/dev/null && curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
      log "llama-server ready after ${i}s; GPU memory used: $(gpu_query memory.used) MiB"
      return 0
    fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      SERVER_PID=""
      rm -f "$PID_FILE"
      log "llama-server exited during start; see results/server-$name.log"
      return 1
    fi
    sleep 1
    i=$((i + 1))
  done
  stop_server
  log "llama-server did not become ready in 900 s"
  return 1
}

# start_server <log name> <extra llama-server arguments...>: like try_start_server, but stops the step on failure.
start_server() {
  try_start_server "$@" || die "llama-server ($1) did not start; see results/server-$1.log"
}

# Stops the server that this shell started, and only that one: the PID is kept in SERVER_PID and checked against
# the kit's binary before any signal.
stop_server() {
  [ -n "$SERVER_PID" ] || return 0
  local pid=$SERVER_PID i=0
  SERVER_PID=""
  if kill -0 "$pid" 2>/dev/null && is_kit_server "$pid"; then
    kill "$pid" 2>/dev/null || true
    while kill -0 "$pid" 2>/dev/null && [ $i -lt 60 ]; do sleep 1; i=$((i + 1)); done
    if kill -0 "$pid" 2>/dev/null && is_kit_server "$pid"; then kill -9 "$pid" 2>/dev/null || true; fi
    log "llama-server pid $pid stopped"
  fi
  rm -f "$PID_FILE"
}

# snapshot <prefix>: the existing result records with that prefix, as one "|"-separated string (paths may hold spaces).
snapshot() {
  local f out="|"
  for f in "$RESULTS"/"$1"*.jsonl; do [ -f "$f" ] && out="$out$f|"; done
  printf '%s' "$out"
}

# new_records <prefix> <snapshot>: the records with that prefix that are not in the snapshot, one per line.
new_records() {
  local f
  for f in "$RESULTS"/"$1"*.jsonl; do
    [ -f "$f" ] || continue
    case "$2" in *"|$f|"*) ;; *) printf '%s\n' "$f" ;; esac
  done
}

# check_records <files...>: stops the step if a benchmark record says error or interrupted, or a round is invalid.
check_records() {
  [ $# -gt 0 ] || die "the benchmark wrote no records; see results/kit.log"
  python3 "$KITLIB" check-jsonl "$@" | tee -a "$RESULTS/kit.log" >&2 \
    || die "the benchmark recorded errors (listed above); pack what exists with scripts/90-collect.sh and report"
}

# Runs the pinned benchmark script against the local server and checks its records.
bench() {
  [ "$(sha256_of "$BENCH")" = "$BENCH_SHA256" ] || die "tools/hybrid_bench.py was modified; restore the original file"
  local before f files=()
  before=$(snapshot hybrid-bench-)
  run_child python3 "$BENCH" --url "http://127.0.0.1:$PORT" --outdir "$RESULTS" "$@" || die "hybrid_bench.py failed"
  while IFS= read -r f; do files+=("$f"); done < <(new_records hybrid-bench- "$before")
  check_records ${files[@]+"${files[@]}"}
}

# proc_start <pid>: the process start time as ps prints it (the same on Linux and macOS), or nothing.
proc_start() { ps -o lstart= -p "$1" 2>/dev/null | sed -E 's/^ +| +$//g'; }

# One step at a time per kit folder. The lock holds the step's PID and its start time, so a live step is recognised
# however it was started, and a PID that a new process has since taken counts as stale. A step started while another
# one runs refuses; a stale lock is taken over. SIGTERM and SIGINT end the step through the EXIT trap, which stops the
# step's benchmark and server and frees the lock at once, because long commands run through run_child. (A step
# started with "nohup ... &" ignores SIGINT: stop it with a plain "kill <pid>".)
STEP_LOCK="$WORK/.step.lock"
STEP_LOCK_HELD=0
MY_START=""
acquire_step_lock() {
  local line other other_start
  if ! mkdir "$STEP_LOCK" 2>/dev/null; then
    line=$(cat "$STEP_LOCK/pid" 2>/dev/null || true)
    if [ -z "$line" ]; then sleep 1; line=$(cat "$STEP_LOCK/pid" 2>/dev/null || true); fi
    other=${line%% *}
    other_start=${line#* }
    if is_int "$other" && [ "$other_start" != "$line" ] && kill -0 "$other" 2>/dev/null \
       && [ "$(proc_start "$other")" = "$other_start" ]; then
      log "another step of this kit is still running as pid $other; wait for it to finish, or stop it with: kill $other"
      exit 1
    fi
    rm -f "$STEP_LOCK/pid"
    rmdir "$STEP_LOCK" 2>/dev/null || true
    mkdir "$STEP_LOCK" 2>/dev/null || { log "ERROR: cannot take the step lock $STEP_LOCK"; exit 1; }
  fi
  MY_START=$(proc_start $$)
  echo "$$ $MY_START" > "$STEP_LOCK/pid"
  STEP_LOCK_HELD=1
}
# Frees the lock only while it still names this step.
release_step_lock() {
  [ "$STEP_LOCK_HELD" = "1" ] || return 0
  STEP_LOCK_HELD=0
  [ "$(cat "$STEP_LOCK/pid" 2>/dev/null || true)" = "$$ $MY_START" ] || return 0
  rm -f "$STEP_LOCK/pid"
  rmdir "$STEP_LOCK" 2>/dev/null || true
}

# run_child <command...>: runs a long command in the background and waits for it. A signal sent to the step is then
# handled at once (bash defers traps while a foreground command runs), and the EXIT trap stops this child, whose PID
# the step recorded itself.
CHILD_PID=""
run_child() {
  local rc=0
  "$@" &
  CHILD_PID=$!
  wait "$CHILD_PID" || rc=$?
  CHILD_PID=""
  return "$rc"
}
stop_child() {
  [ -n "$CHILD_PID" ] || return 0
  local pid=$CHILD_PID
  CHILD_PID=""
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}
on_exit() { trap '' TERM INT; stop_child; stop_server; release_step_lock; }
trap on_exit EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
acquire_step_lock
