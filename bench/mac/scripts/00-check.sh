#!/usr/bin/env bash
# Step 0: checks the machine and tools and writes results/system.json.
# Records only hardware and software versions: no host name, user name or serial number.
source "$(dirname "$0")/common.sh"

[ "$(uname -s)" = "Darwin" ] || die "this kit needs macOS"
[ "$(uname -m)" = "arm64" ] || die "this kit needs Apple Silicon (arm64)"

mem_gb=$(( $(sysctl -n hw.memsize) / 1073741824 ))
chip=$(sysctl -n machdep.cpu.brand_string)
model_id=$(sysctl -n hw.model)
macos="$(sw_vers -productVersion) ($(sw_vers -buildVersion))"
gpu_cores=$(system_profiler SPDisplaysDataType 2>/dev/null | awk -F': ' '/Total Number of Cores/ {print $2; exit}')
power=$(pmset -g batt 2>/dev/null | head -1 | sed -E "s/.*'([^']*)'.*/\1/")
pmset_all=$(pmset -g 2>/dev/null || true)
low_power=$(printf '%s\n' "$pmset_all" | python3 "$KITLIB" low-power-mode)
low_power_raw=$(printf '%s\n' "$pmset_all" | awk '$1 == "lowpowermode" || $1 == "powermode" {printf "%s%s %s", sep, $1, $2; sep = "; "}')
disk_free=$(free_gb "$KIT_DIR")

problems=""
add_problem() { problems="$problems
- $*"; }

[ "$mem_gb" -ge 48 ] || add_problem "memory: $mem_gb GB; at least 48 GB is needed (64 GB is the target)"
for tool in git cmake python3 curl shasum lsof caffeinate; do
  command -v "$tool" >/dev/null 2>&1 || add_problem "missing tool: $tool"
done
xcode-select -p >/dev/null 2>&1 || add_problem "Xcode Command Line Tools are missing: the user runs 'xcode-select --install'"
if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || add_problem "python3 is older than 3.8"
fi
[ "$(sha256_of "$BENCH")" = "$BENCH_SHA256" ] || add_problem "tools/hybrid_bench.py does not match its pinned SHA-256"

need_gb=25
[ -f "$MODEL_PATH" ] && need_gb=6
[ "$disk_free" -ge "$need_gb" ] || add_problem "free disk: $disk_free GB; at least $need_gb GB is needed (about 55 GB with slot save/restore)"

warnings=""
[ "$power" = "AC Power" ] || warnings="$warnings
- not on AC power ($power): connect the charger before the long steps"
case "$low_power" in
  0) ;;
  1) warnings="$warnings
- Low Power Mode is on: turn it off for the measurement" ;;
  *) warnings="$warnings
- Low Power Mode state is unknown (pmset: ${low_power_raw:-no lowpowermode or powermode line}): check Battery settings before the long steps" ;;
esac
[ "$mem_gb" -ge 64 ] || warnings="$warnings
- $mem_gb GB of memory: the 260k depth needs about 32 GB for the model and cache"
[ "$disk_free" -ge 55 ] || warnings="$warnings
- $disk_free GB free: the depth step will skip slot save/restore (up to 28 GB); GPU imports additionally need 9/36 GB per 260k/1M original and another 9/36 GB for a restream copy, or fall back to one stream"

KIT_VERSION="$KIT_VERSION" CHIP="$chip" MODEL_ID="$model_id" MEM_GB="$mem_gb" MACOS="$macos" GPU_CORES="$gpu_cores" \
POWER="$power" LOW_POWER="$low_power" LOW_POWER_RAW="$low_power_raw" DISK_FREE="$disk_free" \
python3 - "$RESULTS/system.json" <<'EOF'
import json, os, platform, sys
info = {
    "kit_version": os.environ["KIT_VERSION"],
    "chip": os.environ["CHIP"],
    "model_identifier": os.environ["MODEL_ID"],
    "memory_gb": int(os.environ["MEM_GB"]),
    "gpu_cores": os.environ["GPU_CORES"] or None,
    "macos": os.environ["MACOS"],
    "python": platform.python_version(),
    "power_source": os.environ["POWER"],
    "low_power_mode": int(os.environ["LOW_POWER"]) if os.environ["LOW_POWER"] in ("0", "1") else None,
    "low_power_mode_status": "measured" if os.environ["LOW_POWER"] in ("0", "1") else "unknown",
    "low_power_mode_raw": os.environ["LOW_POWER_RAW"] or None,
    "disk_free_gb_at_check": int(os.environ["DISK_FREE"]),
}
with open(sys.argv[1], "w") as f:
    json.dump(info, f, indent=2)
EOF

log "machine: $chip, $mem_gb GB, GPU cores ${gpu_cores:-unknown}, macOS $macos, power: $power, free disk: $disk_free GB"
if [ -n "$warnings" ]; then log "warnings:$warnings"; fi
if [ -n "$problems" ]; then die "fix these before continuing:$problems"; fi
log "check passed; results/system.json written"
