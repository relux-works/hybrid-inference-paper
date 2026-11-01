#!/usr/bin/env bash
# Step 0: checks the machine, the GPU and the tools, and writes results/system.json.
# Records only hardware and software versions: no host name, user name, IP address or serial number.
source "$(dirname "$0")/common.sh"

[ "$(uname -s)" = "Linux" ] || die "this kit needs Linux with an NVIDIA GPU; on a Mac use bench/mac"
command -v nvidia-smi >/dev/null 2>&1 || die "nvidia-smi not found: this kit needs an NVIDIA GPU with its driver installed"
gpu_name=$(gpu_query name)
[ -n "$gpu_name" ] || die "no NVIDIA GPU with index $GPU_INDEX; list them with 'nvidia-smi -L' and set GPU_INDEX"

gpu_mem_mib=$(gpu_mib memory.total)
gpu_free_mib=$(gpu_mib memory.free)
driver=$(gpu_query driver_version)
cc=$(gpu_query compute_cap)
pcie="gen $(gpu_query pcie.link.gen.max) x$(gpu_query pcie.link.width.max)"
power_limit=$(gpu_query power.limit)
gpu_count=$(nvidia-smi -L 2>/dev/null | grep -c '^GPU ' || true)
gpu_uuid=$(gpu_query uuid)
others=0
if [ -n "$gpu_uuid" ]; then
  others=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader 2>/dev/null | grep -c -F "$gpu_uuid" || true)
fi
cuda=""
if command -v nvcc >/dev/null 2>&1; then cuda=$(nvcc --version | sed -nE 's/.*release ([0-9.]+).*/\1/p' | head -1); fi
cpu=$(awk -F': ' '/^model name/ {print $2; exit}' /proc/cpuinfo)
cores=$(nproc)
ram_gb=$(awk '/^MemTotal/ {printf "%d", $2 / 1048576}' /proc/meminfo)
os=$( (. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME") || uname -sr)
disk_free=$(free_gb "$KIT_DIR")
ctx1=$(fit_ctx 1)

problems=""
add_problem() { problems="$problems
- $*"; }

for tool in git cmake python3 curl sha256sum c++; do
  command -v "$tool" >/dev/null 2>&1 || add_problem "missing tool: $tool"
done
if [ ! -x "$SERVER_BIN" ] && [ -z "$cuda" ]; then
  add_problem "nvcc (the CUDA toolkit) is missing, so llama.cpp cannot be built with CUDA; install the CUDA toolkit or use an image with it (a '-devel' CUDA image)"
fi
if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || add_problem "python3 is older than 3.8"
fi
[ "$(sha256_of "$BENCH")" = "$BENCH_SHA256" ] || add_problem "tools/hybrid_bench.py does not match its pinned SHA-256"
[ "$ctx1" -ge 32768 ] || add_problem "GPU $GPU_INDEX has $gpu_free_mib MiB free: too little for the 19 GB model plus a 32k context"

# The model takes 19 GB and the build about 1 GB; the depth step then wants 35 GB more for slot save/restore.
need_gb=25
[ -f "$MODEL_PATH" ] && need_gb=6
[ "$disk_free" -ge "$need_gb" ] || add_problem "free disk: $disk_free GB; at least $need_gb GB is needed (about 55 GB with slot save/restore)"
after_model=$disk_free
[ -f "$MODEL_PATH" ] || after_model=$((after_model - 19))
[ -x "$SERVER_BIN" ] || after_model=$((after_model - 1))

warnings=""
add_warning() { warnings="$warnings
- $*"; }
[ "$others" = "0" ] || add_warning "$others other process(es) use GPU $GPU_INDEX: the numbers will be lower; ask the owner to stop them"
if [ "${cc%%.*}" -ge 10 ] 2>/dev/null && [ -n "$cuda" ]; then
  python3 -c "import sys; v=tuple(int(x) for x in '$cuda'.split('.')[:2]); sys.exit(0 if v >= (12, 8) else 1)" \
    || add_warning "compute capability $cc (Blackwell) needs CUDA 12.8 or newer; nvcc reports $cuda"
fi
[ "$ctx1" -ge 262144 ] || [ "$ctx1" -lt 32768 ] || add_warning "the card fits a context of $ctx1 tokens: the depth ladder stops below 249k (expected on 24 GB cards)"
[ -n "$gpu_uuid" ] || add_warning "nvidia-smi gives no UUID for GPU $GPU_INDEX, so other processes on it cannot be counted"
[ "$after_model" -ge 35 ] || add_warning "about $after_model GB will be free after the model and the build: the depth step will skip slot save/restore (it needs 35 GB then)"

KIT_VERSION="$KIT_VERSION" GPU_NAME="$gpu_name" GPU_MEM="$gpu_mem_mib" GPU_FREE="$gpu_free_mib" DRIVER="$driver" CC="$cc" \
PCIE="$pcie" POWER_LIMIT="$power_limit" GPU_COUNT="$gpu_count" GPU_INDEX="$GPU_INDEX" OTHERS="$others" CUDA="$cuda" \
CPU="$cpu" CORES="$cores" RAM_GB="$ram_gb" OS="$os" DISK_FREE="$disk_free" CTX1="$ctx1" \
python3 - "$RESULTS/system.json" <<'EOF'
import json, os, platform, sys
e = os.environ
info = {
    "kit_version": e["KIT_VERSION"],
    "gpu": e["GPU_NAME"],
    "gpu_memory_mib": int(e["GPU_MEM"]),
    "gpu_memory_free_mib_at_check": int(e["GPU_FREE"]),
    "gpu_compute_capability": e["CC"],
    "gpu_pcie_max": e["PCIE"],
    "gpu_power_limit_w": e["POWER_LIMIT"],
    "gpu_index": int(e["GPU_INDEX"]),
    "gpus_on_host": int(e["GPU_COUNT"] or 0),
    "other_processes_on_gpu_at_check": int(e["OTHERS"] or 0),
    "nvidia_driver": e["DRIVER"],
    "cuda_toolkit": e["CUDA"] or None,
    "cpu": e["CPU"],
    "cpu_threads": int(e["CORES"]),
    "ram_gb": int(e["RAM_GB"]),
    "os": e["OS"],
    "kernel": platform.release(),
    "python": platform.python_version(),
    "disk_free_gb_at_check": int(e["DISK_FREE"]),
    "max_context_one_slot": int(e["CTX1"]),
}
with open(sys.argv[1], "w") as f:
    json.dump(info, f, indent=2)
EOF

log "GPU $GPU_INDEX: $gpu_name, $gpu_mem_mib MiB ($gpu_free_mib free), compute $cc, driver $driver, CUDA ${cuda:-none}, PCIe $pcie"
log "host: $cpu, $cores threads, $ram_gb GB RAM, $os, free disk $disk_free GB; one slot fits $ctx1 tokens"
if [ -n "$warnings" ]; then log "warnings:$warnings"; fi
if [ -n "$problems" ]; then die "fix these before continuing:$problems"; fi
log "check passed; results/system.json written"
