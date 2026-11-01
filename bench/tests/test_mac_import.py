"""Mac step control-flow tests with isolated server/benchmark doubles, no model or GPU."""
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest

from test_restream import fixture, large_fixture, wait_for_copy
from test_kitlib import kitlib

ROOT = Path(__file__).resolve().parents[2]
COMMON = ROOT/'bench/mac/scripts/common.sh'


class MacImport(unittest.TestCase):
    def exercise(self, step, mode='fallback', streams='1,2,4,8', external=False):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            work, results = d/'work', d/'results'
            imported = d/'external imports' if external else work/'slots-import'
            imported.mkdir(parents=True)
            original, _ = fixture()
            src = imported/'parallel-depth-4.bin'
            src.write_bytes(original)
            if mode in ('term-copy', 'int-copy'):
                large_fixture(src)
            original_hash = kitlib.sha256_file(src)
            bin_dir = d/'bin'
            bin_dir.mkdir()
            (bin_dir/'caffeinate').write_text('#!/bin/sh\nexit 0\n')
            (bin_dir/'caffeinate').chmod(0o755)
            harness = d/'common.sh'
            harness.write_text('''source "$REAL_COMMON"
file_bytes() { wc -c < "$1" | tr -d " \t"; }
mac_fit_streams() { echo "$TEST_STREAMS"; }
mac_usable_bytes() { echo 100000000000; }
sha256_of() {
  echo "$1" >> "$RESULTS/hash-events"
  python3 -c 'import hashlib,sys; h=hashlib.sha256(); f=open(sys.argv[1],"rb"); [h.update(b) for b in iter(lambda: f.read(1 << 20), b"")]; print(h.hexdigest())' "$1"
}
device_label() { echo test; }
snapshot() { echo before; }
new_records() { echo "$RESULTS/record.jsonl"; }
check_records() { :; }
try_start_server() {
  local attempt_np=$np
  echo "attempt $np $slot_dir" >> "$RESULTS/events"
  python3 - "$KITLIB" "$slot_dir/parallel-depth-$depth.bin" "$np" <<'EOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location('kitlib', sys.argv[1])
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
with open(sys.argv[2], 'rb') as f:
    assert k.parse_slot(f)['streams'] == int(sys.argv[3])
EOF
  [ "$?" -eq 0 ] || exit 99
  # Every prior attempt's directory must have been cleaned before another attempt.
  [ "$(find "$WORK/slots-restream" -name '*.bin' 2>/dev/null | wc -l)" -le 1 ] || exit 98
  if [ "$TEST_MODE" = startup ]; then return 1; fi
  if [ "$TEST_MODE" = fallback ] && [ "$np" -eq 8 ]; then return 1; fi
  return 0
}
# Keep the real run_child for the restream helper, stub only the benchmark invocation.
run_benchmark_child=$(declare -f run_child)
eval "${run_benchmark_child/run_child ()/real_run_child ()}"
run_child() {
  case "$2" in
    */kitlib.py)
       if [ "$TEST_MODE" = disk-race ]; then
         real_run_child python3 -c 'import importlib.util,sys; from unittest.mock import patch; spec=importlib.util.spec_from_file_location("kitlib",sys.argv[1]); k=importlib.util.module_from_spec(spec); spec.loader.exec_module(k); sys.argv=sys.argv[1:]; disk=type("Disk",(),{"free":0})(); p=patch.object(k.shutil,"disk_usage",return_value=disk); p.start(); sys.exit(k.main())' "${@:2}"
       else real_run_child "$@"; fi ;;
    *) echo benchmark >> "$RESULTS/events"
       case "$TEST_MODE" in error) return 1 ;; signal) kill -TERM $$ ;; esac ;;
  esac
}
''')
            # Only the common-source path changes in this private copy. The actual
            # common.sh and step bodies are exercised, including their EXIT trap.
            script = (ROOT/'bench/mac/scripts'/step).read_text()
            script = script.replace('source "$(dirname "$0")/common.sh"', 'source "$TEST_COMMON"')
            if mode == 'disk':
                with harness.open('a') as f:
                    f.write("df() { printf 'Filesystem 1K-blocks Used Available Capacity Mounted\\nmock 100 100 0 100%% /\\n'; }\n")
            if step.startswith('57') and streams == '1':
                with harness.open('a') as f:
                    f.write('mac_usable_bytes() { echo 2000000000; }\n')
            path = d/'step.sh'
            path.write_text(script)
            env = dict(os.environ, WORK=str(work), RESULTS=str(results), TEST_COMMON=str(harness),
                       REAL_COMMON=str(COMMON), TEST_STREAMS=streams, TEST_MODE=mode,
                       MAXCTX_DEPTHS='4', AGENTS_DEPTH='4', AGENT_TURNS='1',
                       PATH=str(bin_dir)+os.pathsep+os.environ['PATH'], PYTHONDONTWRITEBYTECODE='1')
            if external:
                env['SLOT_FROM'] = str(imported)
            if mode in ('term-copy', 'int-copy'):
                p = subprocess.Popen(['bash', str(path)], env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)
                try:
                    partial = wait_for_copy(p, work/'slots-restream')
                    self.assertLess(partial.stat().st_size, src.stat().st_size)
                    p.send_signal(signal.SIGTERM if mode == 'term-copy' else signal.SIGINT)
                    out, err = p.communicate(timeout=20)
                    r = subprocess.CompletedProcess(p.args, p.returncode, out, err)
                finally:
                    if p.poll() is None:
                        p.terminate()
                    p.communicate(timeout=20)
            else:
                r = subprocess.run(['bash', str(path)], env=env, capture_output=True, text=True)
            events = (results/'events').read_text() if (results/'events').exists() else ''
            log = (results/'kit.log').read_text()
            self.assertEqual(kitlib.sha256_file(src), original_hash)
            self.assertEqual(list((work/'slots-restream').glob('**/*')), [])
            self.assertFalse((work/'.step.lock').exists())
            self.assertEqual((results/'hash-events').read_text().splitlines(), [str(src)])
            return r, events, log, str(imported)

    # Claim: both steps restream each attempted np (8 then 4), pass a matching slot
    # directory to the server, log both hashes, preserve imports, and clean up.
    # This checks shell integration with doubles; real llama.cpp is a separate check.
    def test_fallback(self):
        for step in ('56-run-maxctx.sh', '57-run-agents.sh'):
            for external in (False, True):
                with self.subTest(step=step, external=external):
                    r, events, log, _ = self.exercise(step, external=external)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertIn('attempt 8 ', events)
                    self.assertIn('attempt 4 ', events)
                    self.assertEqual(events.count('benchmark'), 1)
                    self.assertIn('IN  sha256', log)
                    self.assertIn('OUT sha256', log)
                    self.assertIn('restreamed to 4 streams', log)

    # Claim: no-space (preflight or Python's second disk check) uses the import at
    # np=1 and still benchmarks; exhausted startup fallbacks, benchmark failure and TERM
    # remove temporary imports through the real EXIT trap, retaining originals.
    def test_disk_error_signal(self):
        for step in ('56-run-maxctx.sh', '57-run-agents.sh'):
            for mode, code in (('disk', 0), ('disk-race', 0), ('startup', 0), ('error', 1), ('signal', 143)):
                with self.subTest(step=step, mode=mode):
                    r, events, log, imported = self.exercise(step, mode=mode)
                    self.assertEqual(r.returncode, code, r.stderr)
                    if mode in ('disk', 'disk-race'):
                        self.assertIn('attempt 1 '+imported, events)
                        self.assertEqual(events.count('attempt'), 1)
                        self.assertEqual(events.count('benchmark'), 1)
                        self.assertIn('falling back to one stream using the import directly', log)
                        self.assertNotIn('OUT sha256', log)

    # Claim: TERM and INT to either real step during an observed partial 1.56 GiB
    # restream remove the entire owned directory (including hidden files/logs),
    # stop the child, free the step lock and preserve the import's SHA-256.
    def test_signal_during_restream(self):
        for step in ('56-run-maxctx.sh', '57-run-agents.sh'):
            for mode, code in (('term-copy', 143), ('int-copy', 130)):
                with self.subTest(step=step, signal=mode):
                    r, events, _, _ = self.exercise(step, mode=mode)
                    self.assertEqual(r.returncode, code, r.stderr)
                    self.assertEqual(events, '')

    # Claim: one-stream servers use the original import directory directly and do
    # not produce restream output or require disk for a second copy.
    def test_single_stream(self):
        for step in ('56-run-maxctx.sh', '57-run-agents.sh'):
            with self.subTest(step=step):
                r, events, log, imported = self.exercise(step, mode='direct', streams='1')
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn('attempt 1 '+imported, events)
                self.assertNotIn('OUT sha256', log)


class MacPowerCheck(unittest.TestCase):
    # Claim: step 00 records low_power_mode as 1 or 0 only from a known pmset value, records an unknown state as
    # null with status "unknown" and the raw pmset lines, and puts the warning into results/kit.log, without failing
    # the step, also when pmset -g itself fails; high power stays off with no warning. macOS commands are
    # doubles; no live Mac check is claimed.
    def test_system_json(self):
        import json
        for sample, expected, raw, warning in (
                ('pmset-legacy.txt', 1, 'lowpowermode 1', 'Low Power Mode is on'),
                ('pmset-26.txt', 1, 'powermode 1', 'Low Power Mode is on'),
                ('pmset-absent.txt', None, None, 'Low Power Mode state is unknown'),
                ('high', 0, 'powermode 2', None),
                ('unknown', None, 'powermode 3', 'Low Power Mode state is unknown'),
                ('fail', None, None, 'Low Power Mode state is unknown')):
            with self.subTest(sample=sample), tempfile.TemporaryDirectory() as d:
                d = Path(d)
                work, results = d/'work', d/'results'
                sample_path = d/'pmset.txt'
                text = (' powermode 3\n' if sample == 'unknown' else ' powermode 2\n' if sample == 'high' else
                        '' if sample == 'fail' else (Path(__file__).parent/'fixtures'/sample).read_text())
                sample_path.write_text(text)
                common = d/'common.sh'
                common.write_text('''source "$REAL_COMMON"
uname() { case "$1" in -s) echo Darwin ;; -m) echo arm64 ;; esac; }
sysctl() { case "$2" in hw.memsize) echo 137438953472 ;; machdep.cpu.brand_string) echo 'Apple M3 Max' ;; hw.model) echo Mac15,9 ;; esac; }
sw_vers() { echo 26.0; }
system_profiler() { echo ' Total Number of Cores: 40'; }
pmset() { if [ "${2:-}" = batt ]; then echo "Now drawing from 'AC Power'"; elif [ -n "${PMSET_FAIL:-}" ]; then return 1; else cat "$PMSET_SAMPLE"; fi; }
free_gb() { echo 60; }
xcode-select() { return 0; }
cmake() { return 0; }
lsof() { return 0; }
caffeinate() { return 0; }
sha256_of() { echo "$BENCH_SHA256"; }
''')
                script = (ROOT/'bench/mac/scripts/00-check.sh').read_text()
                script = script.replace('source "$(dirname "$0")/common.sh"', 'source "$TEST_COMMON"')
                path = d/'00-check.sh'
                path.write_text(script)
                env = dict(os.environ, WORK=str(work), RESULTS=str(results), TEST_COMMON=str(common),
                           REAL_COMMON=str(COMMON), PMSET_SAMPLE=str(sample_path), PYTHONDONTWRITEBYTECODE='1',
                           PMSET_FAIL='1' if sample == 'fail' else '')
                r = subprocess.run(['bash', str(path)], env=env, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                info = json.loads((results/'system.json').read_text())
                self.assertEqual(info['low_power_mode'], expected)
                self.assertEqual(info['low_power_mode_status'], 'unknown' if expected is None else 'measured')
                self.assertEqual(info['low_power_mode_raw'], raw)
                kit_log = (results/'kit.log').read_text()
                if warning:
                    self.assertIn(warning, kit_log)
                else:
                    self.assertNotIn('Low Power Mode', kit_log)


if __name__ == '__main__':
    unittest.main()
