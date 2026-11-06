"""Measured server prefill: rate fidelity, dependency boundaries and immutable run11."""
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load,run
from regeneration import compare_csv,reference_float_cells
from hybridcalc.export import write_tables
from hybridcalc.inputs import InputGap
from hybridcalc.paper_tables import Context
from hybridcalc.server_prefill import fit,compute_at,mean_seconds
from hybridcalc.performance import flop
from r11_audit import CASES
from r12_audit import check_frozen,ROOT,PUBLISHED


def scratch_directory():
    # The standalone test may be the first command in a fresh checkout. Keep its
    # repository output root available, but put temporary CSVs in the chosen TMPDIR.
    (ROOT/'.temp').mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory()


class Run12ScratchTests(unittest.TestCase):
    # Claim: standalone regeneration creates a missing repository scratch root;
    # temporary data use TMPDIR and are cleaned without removing that output root.
    def test_standalone_creates_missing_temp_root(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertFalse((root/'.temp').exists())
            with patch.dict(scratch_directory.__globals__, ROOT=root):
                with scratch_directory() as scratch:
                    self.assertTrue((root/'.temp').is_dir())
                    self.assertEqual(Path(scratch).parent, Path(tempfile.gettempdir()))
                self.assertFalse(Path(scratch).exists())
            self.assertTrue((root/'.temp').is_dir())


class Run12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario,cls.inputs=load('paper-tables-r6-measured-server')
        cls.raw=[json.loads(s) for s in cls.inputs.measured('gpu_server').decode().splitlines()]

    # Twelve held-in bulk turns meet2%; the three independent fills meet15%.
    # These are residual bounds on one device/run, not uncertainty estimates or small-delta guarantees.
    def test_fit_bulk_and_held_out_fills(self):
        a,b,points=fit(self.raw)
        self.assertGreater(a,0);self.assertGreater(b,0)
        self.assertEqual(len(points),12)
        for p in points:
            self.assertLess(abs((a+b*p['depth'])/p['seconds_token']-1),.02)
        directory=ROOT/'data/measurements/vast-2026-11-01/qwen27b-gpu-bench/results'
        fills=[]
        for path in directory.glob('*-slot*.jsonl'):
            p=next(r for r in map(json.loads,path.read_text().splitlines()) if r['kind']=='prefill')
            n=p['depth'];prediction=a*n+b*n*n/2;actual=p['prompt_ms']/1000
            self.assertLess(abs(prediction/actual-1),.15);fills.append(n)
        self.assertEqual(sorted(fills),[131072,260000,1040000])
        self.assertGreater(a+b*1040000,a+b*249000)

    # This independent observed-time oracle exercises the actual owned-server prefill consumer.
    # Zero output/tool wait isolates prefill; it cannot qualify server decode or GPU concurrency.
    def test_measured_server_timing_replaces_mfu(self):
        s,i=load('paper-tables-r6-measured-server');c=Context(s,i);m=c.model('qwen27')
        for key in ('rack1','rack2','b300_node'):
            server=c.server(key,m);h=c.g.resolve(server['hardware']).value
            peak=i.get(server['prefix']+'.fp8_peak');reference=i.get('hardware.servers.rtx1.peak')
            for row in self.raw:
                if row.get('kind')!='turn' or row.get('delta') not in (2000,10000):continue
                depth=row['level'];tokens=row['prompt_n']
                calls=c.label('oracle.'+key+'.'+str(depth)+'.'+str(tokens),[(depth,tokens,0,0)])
                seconds=c.g.resolve(c.own_seconds('oracle_seconds.'+key+'.'+str(depth)+'.'+str(tokens),calls,m,server)).value
                expected=row['prompt_ms']/1000*reference/peak/h['gpus']/h['shard_efficiency']
                self.assertLess(abs(seconds/expected-1),.02,
                                'measured server prefill must match observed bulk time within2%; old MFU0.3 is forbidden')

    # Both dense-peak bases yield identical B300 scaling; node replicas keep existing GPU/shard factors.
    # GLM uses the same inferred envelope and its own FLOPs, not a claimed GLM measurement.
    def test_b300_transfer_and_glm_envelope(self):
        s,i=load('paper-tables-r6-measured-server');c=Context(s,i)
        a,b,_=fit(self.raw)
        for model in ('qwen27','glm'):
            m=c.model(model)
            for key in ('rack1','rack2','b300','b300_node','colo1','colo2','office4','rtx6000'):
                server=c.server(key,m);rate=c.g.resolve(server['compute']).value
                total_out=c.g.resolve(server['total_compute']);total=total_out.value
                for depth in (0,16000,249000,1000000):
                    expected=(54e9+393216*depth)/(a+b*depth)*i.get(server['prefix']+'.fp8_peak')/i.get('hardware.servers.rtx1.peak')
                    self.assertAlmostEqual(compute_at(rate,depth)/expected,1,places=12)
                    h=c.g.resolve(server['hardware']).value
                    if total_out.alarms:
                        self.assertEqual(model,'glm')
                        self.assertTrue(any('weights plus workspace do not fit' in alarm['reason'] for alarm in total_out.alarms))
                    else:
                        self.assertAlmostEqual(compute_at(total,depth)/expected,h['gpus']*h['shard_efficiency'],places=12)
                self.assertEqual(i.get(server['prefix']+'.fp8_peak')/i.get('owners.options.rtx6000.fp8_peak'),
                                 i.get(server['prefix']+'.bf16_peak')/i.get('owners.options.rtx6000.bf16_peak'))
        # Other GPU models retain their unmeasured design assumptions.
        rate=c.g.resolve(c.server('h100',c.model('qwen27'))['compute']).value
        self.assertEqual(rate,i.get('owners.options.h100.fp8_peak')*i.get('service.mfu'))

    # Missing, duplicated, invalid and inexact observations cannot produce a fitted curve.
    def test_fit_rejects_invalid_observations(self):
        rows=[r for r in self.raw if r.get('kind')=='turn' and r.get('delta') in (2000,10000)]
        variants=[rows[:-1],rows+[rows[0]]]
        for field,value in [('prompt_ms',0),('prompt_ms',float('nan')),('prompt_n',-1),('truncated',True),('gen_tokens_exact',False)]:
            bad=copy.deepcopy(rows);bad[0][field]=value;variants.append(bad)
        for bad in variants:
            with self.assertRaises(InputGap):fit(bad)
        self.assertEqual(len(fit(rows)[2]),12)

    # Tampering/missing measured data and incompatible precision alarm the rate instead of using old MFU.
    def test_measurement_and_precision_fail_closed(self):
        for mode in ('hash','missing','precision'):
            s,i=load('paper-tables-measured-server')
            if mode=='hash':i.data['measurements']['gpu_server']['sha256']='0'*64
            if mode=='missing':i.data['measurements'].pop('gpu_server')
            if mode=='precision':i.override('owners.server_precision=BF16')
            c=Context(s,i);out=c.g.resolve(c.server('b300',c.model('qwen27'))['compute'])
            self.assertTrue(out.alarms,mode)
            self.assertTrue(any(('sha256' if mode=='hash' else 'unavailable' if mode=='missing' else 'same-weights Q4') in a['reason'] for a in out.alarms),out.alarms)

    # All original measurement members exactly match the kit manifest; only provenance README is added.
    def test_archive_members_and_manifest(self):
        root=ROOT/'data/measurements/vast-2026-11-01/qwen27b-gpu-bench';m=json.loads((root/'results/MANIFEST.json').read_text())
        self.assertEqual({str(p.relative_to(root/'results')) for p in (root/'results').rglob('*') if p.is_file()},set(m['files'])|{'MANIFEST.json'})
        self.assertEqual({p.name for p in root.iterdir()},{'results','README.md'})
        for name,info in m['files'].items():
            p=root/'results'/name;self.assertEqual(p.stat().st_size,info['bytes']);self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),info['sha256'])

    # Sensitivity changes only the scenario marker, measurement layer, names and export namespace.
    # Workload, decoding, prices, policies and hosting input bytes remain identical.
    def test_sensitivity_inputs_preserve_design(self):
        for name,_ in CASES:
            original,a=load(name);sensitive,b=load(name+'-measured-server')
            data=copy.deepcopy(b.data);data['measurements'].pop('gpu_server')
            self.assertEqual(a.data,data,name)
            for key in original:
                if key not in ('name','description','inputs','export_namespace'):self.assertEqual(original[key],sensitive[key])

    # Claim: all42 design CSVs retain reference bytes on CPython3.14.4; other
    # interpreters retain every non-float byte and floats within two binary64 steps.
    # Run11 artifacts retain a57db67; every current v2 publication byte is independently pinned.
    def test_all_design_csv_bytes_unchanged(self):
        check_frozen();count=0
        with scratch_directory() as directory:
            for name,_ in CASES:
                manifest=write_tables(run(name),directory)
                for table,file in manifest['tables'].items():
                    expected=(PUBLISHED/file).read_bytes()
                    compare_csv((Path(directory)/file).read_bytes(),expected,reference_float_cells(expected,file),file);count+=1
        self.assertEqual(count,42);check_frozen()

    # Exporting sensitivity into a directory containing every original artifact preserves their bytes.
    # Published measured sibling hashes and comparison coverage are verified separately by r12_audit.
    def test_measured_export_cannot_overwrite_run11(self):
        before=check_frozen()
        with scratch_directory() as directory:
            target=Path(directory)
            for p in PUBLISHED.iterdir():
                if p.is_file() and '_measured_server' not in p.name:(target/p.name).write_bytes(p.read_bytes())
            saved={p.name:p.read_bytes() for p in target.iterdir()}
            result=run('paper-tables-r8-conservative-measured-server');manifest=write_tables(result,target)
            self.assertTrue(all('_measured_server' in file for file in manifest['files']))
            for name,data in saved.items():self.assertEqual((target/name).read_bytes(),data,name)
        self.assertEqual(check_frozen(),before)

    # The same timing test passes normally and rejects an MFU0.3 plant with its intended assertion.
    def test_old_mfu_negative_control(self):
        result=subprocess.run([sys.executable,str(Path(__file__).with_name('r12_controls.py')),'old_mfu'],capture_output=True,text=True)
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        self.assertIn('test_measured_server_timing_replaces_mfu',result.stderr)
        self.assertIn('old MFU0.3 is forbidden',result.stderr)
        self.assertIn('AssertionError',result.stderr);self.assertNotIn('ERROR:',result.stderr)


if __name__=='__main__':unittest.main()
