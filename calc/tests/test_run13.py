"""Run13 input custody, independent recomputation and historical preservation."""
import copy
from contextlib import contextmanager
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load,run
from hybridcalc.inputs import InputGap,ROOT,DATA
from hybridcalc.measurements_r13 import (package,matching,verified_archive,no_swap,cold_fit,vllm_rates,MeasuredM5)
from hybridcalc.server_prefill import fit,compute_at
from hybridcalc.paper_tables import Context
from hybridcalc.economics import api_cost
from history_fixtures import snapshot_read
from r13_audit import frozen
import hybridcalc.measurements_r13 as measurements

GOLD={
 'phase_a':('fd0bc08cd310718fadbe10f9badb081abcceb15d8bdb24d0e108305340d76040',125,.00022964337804155598,3.3616439930993272e-9),
 'off':('e80d4240b6e35d384e29a31c14269716b430728472a1253220e2235bbd1ab3c2',14,.0002297773785621298,3.3644085058344844e-9),
 'on':('92828a6c8e5796042fd7175d2b9281d71de3e9a9522af2d1833b8ddaa48c5d38',14,.000270547375634954,3.0818086763884095e-9),
 'm5':('c7ceab57f8d61b9bd166daf96cae1e8f389d296c0f9789ccb8cc32536d9f6b05',26,.0012052888319020894,7.466651934758962e-8)}


class Run13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={k:package(k) for k in GOLD}
        cls.config=json.loads((DATA/'run13-measurements.json').read_text())
        cls.m5=MeasuredM5()
        cls.vllm=[d for d in json.loads(next(c for n,c in cls.packages['phase_a'][1].items() if n.endswith('/vllm.json'))) if 'A' in d]

    @staticmethod
    def archive(path, members):
        with tarfile.open(path,'w:gz') as archive:
            for name,content in members:
                member=tarfile.TarInfo(name) if isinstance(name,str) else name
                member.size=len(content)
                archive.addfile(member,io.BytesIO(content))
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @contextmanager
    def m5_archive(self, review=None):
        # Use the real package verifier and imported-byte check, with only its
        # filesystem root/config pins redirected to an isolated, rehashed copy.
        manifest,payload=copy.deepcopy(self.packages['m5'])
        if review is not None:
            content=json.dumps(review).encode()
            payload['results/measurement-review.json']=content
            manifest['files']['measurement-review.json']=dict(bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
            payload['results/MANIFEST.json']=json.dumps(manifest).encode()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);directory=root/'data/measurements/m5'
            directory.mkdir(parents=True)
            for name,content in payload.items():
                path=directory/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
            digest=self.archive(directory/'copy.tar.gz',payload.items())
            config=root/'config/measurements_r13.py';config.parent.mkdir()
            (config.parent/'data').mkdir()
            (config.parent/'data/run13-measurements.json').write_text(json.dumps(dict(m5=dict(
                directory=str(directory.relative_to(root)),archive='copy.tar.gz',sha256=digest))))
            with patch.object(measurements,'ROOT',root),patch.object(measurements,'__file__',str(config)):
                yield payload

    # All four full hashes, manifest sizes/hashes and extracted-member sets match
    # independent delivery pins; AppleDouble files are never admitted.
    def test_archive_goldens_and_manifest(self):
        for key,(digest,count,_,_) in GOLD.items():
            config=self.config[key];root=ROOT/config['directory'];manifest,payload=self.packages[key]
            self.assertEqual(hashlib.sha256((root/config['archive']).read_bytes()).hexdigest(),digest)
            self.assertEqual(config['sha256'],digest);self.assertEqual(len(manifest['files']),count)
            self.assertEqual({str(p.relative_to(root)) for p in (root/'results').rglob('*') if p.is_file()},set(payload))
            self.assertFalse(any(Path(n).name.startswith('._') for n in payload))
        self.assertEqual(self.packages['phase_a'][0]['results_kit_version'],'1.6.1')
        self.assertEqual(self.packages['phase_a'][0]['kit_version'],'1.6.3')

    # Wrong outer hashes reject before parsing; an archive with a correct outer
    # hash but a false inner hash also rejects without writing any payload.
    def test_wrong_hash_and_manifest_rejected(self):
        info=self.config['m5'];path=ROOT/info['directory']/info['archive']
        with self.assertRaisesRegex(InputGap,'archive sha256 mismatch'):verified_archive(path,'0'*64)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bad.tar.gz'
            manifest=json.dumps({'files':{'sample.json':{'bytes':2,'sha256':'0'*64}}}).encode()
            with tarfile.open(path,'w:gz') as t:
                for n,c in [('results/MANIFEST.json',manifest),('results/sample.json',b'{}')]:
                    m=tarfile.TarInfo(n);m.size=len(c);t.addfile(m,io.BytesIO(c))
            with self.assertRaisesRegex(InputGap,'manifest mismatch: sample.json'):
                verified_archive(path,hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual([p.name for p in Path(tmp).iterdir()],['bad.tar.gz'])

    # Repacked real archives are admitted, but unsafe names, either link type,
    # duplicates and unmanifested files refuse before returning any payload.
    # The verifier never writes archive paths, including on rejection.
    def test_archive_custody_refusals(self):
        members=list(self.packages['off'][1].items())
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'copy.tar.gz'
            digest=self.archive(path,members)
            self.assertEqual(verified_archive(path,digest),self.packages['off'])
            plants=[('../escape.json',b'{}','unsafe archive member'),
                    ('/absolute.json',b'{}','unsafe archive member'),
                    # Without the path guard, AppleDouble's transport-only
                    # exemption would admit these: no later guard masks it.
                    ('../._escape',b'{}','unsafe archive member'),
                    ('/._absolute',b'{}','unsafe archive member'),
                    (members[-1][0],members[-1][1],'duplicate archive member'),
                    ('results/extra.jsonl',b'{}','unmanifested payload')]
            for kind in (tarfile.SYMTYPE,tarfile.LNKTYPE):
                link=tarfile.TarInfo('results/link');link.type=kind;link.linkname=members[-1][0]
                plants.append((link,b'','unsafe archive member'))
            for name,content,reason in plants:
                with self.subTest(member=name):
                    digest=self.archive(path,members+[(name,content)])
                    with self.assertRaisesRegex(InputGap,reason):verified_archive(path,digest)
                    self.assertEqual(list(Path(tmp).rglob('*')),[path])

    # Twelve independent raw seconds/token observations reproduce each golden fit.
    # Residual limits describe these runs, not unmeasured deltas or repeatability.
    def test_bulk_fit_goldens_and_recomputation(self):
        for key in GOLD:
            raw=matching(self.packages[key][1],'-q27b-q4km-');a,b,points=fit(raw)
            self.assertAlmostEqual(a,GOLD[key][2],places=16);self.assertAlmostEqual(b,GOLD[key][3],places=18)
            xy=sum(p['depth']*p['seconds_token'] for p in points);xs=sum(p['depth'] for p in points);ys=sum(p['seconds_token'] for p in points)
            expected_b=(12*xy-xs*ys)/(12*sum(p['depth']**2 for p in points)-xs**2)
            self.assertAlmostEqual(b,expected_b,places=18)
            self.assertLess(max(abs((a+b*p['depth'])/p['seconds_token']-1) for p in points),{'phase_a':.038,'off':.037,'on':.081,'m5':.107}[key])

    # Reproduction compares all twelve matched rates, not just fitted coefficients.
    def test_reproduction_within_one_percent(self):
        a=fit(matching(self.packages['phase_a'][1],'-q27b-q4km-'))[2]
        b=fit(matching(self.packages['off'][1],'-q27b-q4km-'))[2]
        for x,y in zip(a,b):
            self.assertEqual((x['depth'],x['delta']),(y['depth'],y['delta']))
            self.assertLess(abs(x['seconds_token']/y['seconds_token']-1),.01)

    # Actual Context consumers select the requested measured curve for RTX/B300;
    # the earlier-run case retains its independently pinned run12 coefficients.
    def test_server_case_consumers(self):
        for case,a,b in [('',GOLD['phase_a'][2],GOLD['phase_a'][3]),('-checkpoints-on',GOLD['on'][2],GOLD['on'][3]),('-earlier-run',.0003687230031301119,6.065719692011435e-9)]:
            s,i=load('paper-tables-r13'+case);c=Context(s,i)
            rate=c.g.resolve(c.server('b300',c.model('qwen27'))['compute']).value
            for d in (16000,110000,249000,1000000):
                expected=(54e9+393216*d)/(a+b*d)*i.get('owners.options.b300.fp8_peak')/i.get('hardware.servers.rtx1.peak')
                self.assertAlmostEqual(compute_at(rate,d)/expected,1,places=12)

    # The raw cold-fit normal equations reproduce both kit fits and observed TTFT.
    # FP8 large batch has a larger 6.3% residual; no blanket 2% claim is made.
    def test_vllm_cold_fit_goldens(self):
        expected=[(9.342839036996133e-5,1.4140563102468149e-9,.017),(9.216062614839821e-5,1.500578537687494e-9,.063)]
        for doc,(aa,bb,limit) in zip(self.vllm,expected):
            a,b=cold_fit(doc);self.assertAlmostEqual(a,aa,places=16);self.assertAlmostEqual(b,bb,places=18)
            for r in doc['A']:
                n=r['length'];self.assertLess(abs((a*n+b*n*n/2)/r['ttft_s']-1),limit)

    # All 16 cached probes count the 784-token-block remainder as processed work;
    # useful-delta rates omit it. The mislabeled status is not used as a rate.
    def test_vllm_cached_recomputation_and_goldens(self):
        self.assertEqual(sum(len(d['B']) for d in self.vllm),16)
        for doc in self.vllm:
            for raw,out in zip(doc['B'],vllm_rates(doc)):
                r=raw['measurement'];n=raw['depth']+raw['delta']-r['cached_tokens']
                self.assertEqual(out['processed'],n);self.assertEqual(out['cached'],(raw['depth']//784)*784)
                self.assertAlmostEqual(out['processed_tok_s'],n/r['ttft_s'])
                self.assertAlmostEqual(out['delta_tok_s'],raw['delta']/r['ttft_s'])
                self.assertGreater(out['processed_tok_s'],out['delta_tok_s'])
        first=vllm_rates(self.vllm[0])[0]
        self.assertEqual(first['processed'],2704);self.assertAlmostEqual(first['processed_tok_s'],7260.615129358147)
        self.assertAlmostEqual(first['delta_tok_s'],5370.2774625430075)

    # Malformed cache/TTFT cannot become a supported cached-rate observation;
    # nearby valid probes still produce positive useful throughput.
    def test_vllm_invalid_cached_rejected(self):
        for key,value in [('cached_tokens',15681),('cached_tokens',20000),('ttft_s',0),('ttft_s',float('nan'))]:
            d=copy.deepcopy(self.vllm[0]);d['B'][0]['measurement'][key]=value
            with self.assertRaisesRegex(InputGap,'invalid cached-delta'):vllm_rates(d)
        self.assertGreater(vllm_rates(self.vllm[0])[0]['delta_tok_s'],0)

    # Admission requires zero sampled swap and no sampler errors; step57 and a
    # contaminated otherwise-valid phase reject without altering the raw review.
    def test_swap_affected_rows_rejected(self):
        review=json.loads(self.packages['m5'][1]['results/measurement-review.json'])
        for phase in ('40-run-depth','50-run-parallel','55-run-scaling'):no_swap(review,phase)
        self.assertEqual(review['phase_summary']['57-run-agents']['max_swap_used_bytes'],5095754301)
        with self.assertRaisesRegex(InputGap,'swap-affected'):no_swap(review,'57-run-agents')
        for key in ('max_swap_used_bytes','swapins_counter_delta_sum','swapouts_counter_delta_sum','sampler_error_samples'):
            bad=copy.deepcopy(review);bad['phase_summary']['40-run-depth'][key]=1
            with self.assertRaisesRegex(InputGap,'swap-affected'):no_swap(bad,'40-run-depth')

    # The production consumer admits the real archive despite step57 swap, but
    # uses exactly steps40/50/55, never agents-loop observations, for speeds.
    def test_measured_m5_excludes_step57_archive_rows(self):
        with self.m5_archive() as payload:
            client=MeasuredM5()
            review=json.loads(payload['results/measurement-review.json'])
            self.assertEqual(review['phase_summary']['57-run-agents']['max_swap_used_bytes'],5095754301)
            self.assertEqual(client.depth,matching(payload,'-q27b-q4km-'))
            self.assertEqual(client.parallel,matching(payload,'-q27b-par4-'))
            expected=[json.loads(line) for name,content in payload.items()
                      if 'parallel-depth-' in name and name.endswith('.jsonl')
                      for line in content.splitlines() if json.loads(line)['kind']=='round']
            self.assertEqual(client.scaling,expected)
            self.assertEqual(len(client.scaling),7)
            for depth in (65536,131072):
                self.assertGreater(client.prefill(depth),0)
                self.assertGreater(client.decode(4,depth),0)

    # Swap in each otherwise valid phase must prevent construction of the
    # machine-speed consumer, through archive custody and package(), not a
    # direct no_swap() call or generator-source identity assertion.
    def test_measured_m5_rejects_swap_in_admitted_archive_phases(self):
        original=json.loads(self.packages['m5'][1]['results/measurement-review.json'])
        for phase in ('40-run-depth','50-run-parallel','55-run-scaling'):
            with self.subTest(phase=phase):
                review=copy.deepcopy(original)
                review['phase_summary'][phase]['max_swap_used_bytes']=1
                with self.m5_archive(review):
                    with self.assertRaisesRegex(InputGap,'swap-affected or unqualified phase: '+phase):
                        MeasuredM5()
        self.assertEqual(json.loads(self.packages['m5'][1]['results/measurement-review.json']),original)

    # M5 prefill uses the harmonic mean of exact 2k/10k rates at each depth;
    # decode uses exact output counters at the measured final depths.
    def test_client_depth_recomputation(self):
        pts=fit(self.m5.depth)[2]
        for d in sorted({p['depth'] for p in pts}):
            expected=2/sum(p['seconds_token'] for p in pts if p['depth']==d)
            self.assertAlmostEqual(self.m5.prefill(d),expected)
        for r in self.m5.depth:
            if r.get('kind')=='turn' and r['delta']==2000:
                self.assertAlmostEqual(self.m5.decode(1,r['depth']+r['prompt_n']),r['predicted_n']/(r['predicted_ms']/1000))
        self.assertEqual(len(self.m5.scaling),7)
        self.assertEqual(self.m5.decode(1,32000),18.29)
        self.assertEqual(4*self.m5.decode(4,32000),33.37)
        self.assertEqual(next(r for r in self.m5.parallel if r['kind']=='parallel')['aggregate_decode_tok_s'],33.37)

    # Three-stream gain is explicitly interpolated; unmeasured >4 streams and
    # incompatible quantization reject. Actual M5 graph consumers use the curve.
    def test_client_consumers_and_bounds(self):
        s,i=load('paper-tables-r13');c=Context(s,i);m=c.model('qwen27')
        local=c.g.resolve(c.local_rate('m5max64',m)).value
        for d in (16000,100000,249000):self.assertEqual(local(d),self.m5.prefill(d))
        for d in (32000,65536,131072,249000):
            self.assertAlmostEqual(3*self.m5.decode(3,d),(2*self.m5.decode(2,d)+4*self.m5.decode(4,d))/2)
        with self.assertRaisesRegex(InputGap,'outside common measured'):self.m5.decode(8,65536)
        with self.assertRaisesRegex(InputGap,'requires Q4'):c.m5_decoder('Q3')

    # New measured M5 efficiency governs its hypothetical rate guard: an old
    # M3 efficiency cannot admit a twofold M5 rate above the bandwidth bound.
    def test_m5_hypothetical_rate_cannot_exceed_bandwidth(self):
        result=run('paper-tables-r7-r13',['workload.sample_calls=1'])
        table=next(t for t in result['tables'] if t['id']=='decode_sensitivity')
        rows=[r for r in table['rows'] if r['client']=='M5 Max 64 GB']
        self.assertTrue(rows)
        for row in rows:
            if row['decode_scale']==1:
                self.assertIsInstance(row['hybrid_sessions_day'],float)
            elif row['decode_scale']==2:
                self.assertIn('alarm',row['hybrid_sessions_day'])
                self.assertTrue(any('raw bandwidth bound' in a['reason'] for a in row['hybrid_sessions_day']['alarm']))

    # The current Sonnet bill falls by exactly 0.10 USD per million cached input
    # tokens; output and uncached inputs are unchanged. Zero-prefix is a control.
    def test_sonnet_price_recomputation(self):
        _,i=load('paper-base');p=i.section('prices.apis.sonnet');self.assertEqual(p['cache_read'],.1)
        old=dict(p,cache_read=.2)
        for calls in ([(100000,2000,512,0)],[(0,2000,512,0)]):
            delta=api_cost(calls,old)-api_cost(calls,p)
            self.assertAlmostEqual(delta,sum(d for d,n,o,t in calls)/len(calls)*.1/1e6)

    # Accounting sensitivity must preserve the parent's measured M5 curve.
    # Its output-only row equals the ordinary R13 row at the same coordinates;
    # changing only reasoning may change generation, never client calibration.
    def test_accounting_child_retains_measured_m5(self):
        parent=run('paper-tables-r13',['workload.sample_calls=1'])
        child=run('paper-tables-r8-r13',['workload.sample_calls=1'])
        sensitivity=next(t for t in child['tables'] if t['id']=='reasoning_on_top_sensitivity')
        for share in ('s20','s50'):
            ordinary=next(t for t in parent['tables'] if t['id']=='person_cost_'+share)
            a=next(r for r in ordinary['rows'] if r['client']=='M5 Max 64 GB' and r['team']==50 and r['basis']=='Mac already owned')
            b=next(r for r in sensitivity['rows'] if r['client']==a['client'] and r['share']==a['share'] and r['basis']==a['basis'] and r['accounting_case']=='base_output')
            for key in ('capacity_day','hybrid_cheapest','hybrid_median','offload_share'):
                self.assertEqual(a[key],b[key],key+': accounting child must retain measured M5 calibration')

    # Separate K and V double Gemma full KV; the sliding component is unchanged.
    # R13 retains its original partial-window formula; current paper geometry
    # uses the complete live R17 window. Both keep separate K and V.
    def test_gemma_geometry_recomputation(self):
        result=run('paper-tables-r7-r13',['workload.sample_calls=1'])
        gemma=[r for t in result['tables'] if t['id']=='arch_compare' for r in t['rows'] if r['model']=='Gemma 4 31B']
        native=next(r for r in csv.DictReader(io.StringIO((ROOT/'paper/data/arch-compare.csv').read_text())) if r['model']=='Gemma 4 31B')
        self.assertEqual(len(gemma),2)
        for r in gemma:
            self.assertEqual(r['kv_full_bytes_token'],10*4*512*2*34/32)
            for k,n in [('delta_1k_mb',1000),('delta_10k_mb',10000)]:
                expected=round((n*43520+min(n,1024)*435200)/1e6,1)
                self.assertEqual(r[k],expected)
                self.assertEqual(float(native[k]),(n*43520+1024*435200)/1e6)
        self.assertEqual(float(native['kv_full_bytes_token']),43520)

    # Execute today's actual native script in isolation; every emitted CSV byte
    # must agree with its checked-in data, including Gemma's separate K and V.
    def test_live_architecture_generator_matches_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            script=Path(tmp)/'arch_compare.py'
            script.write_bytes((ROOT/'paper/data/arch_compare.py').read_bytes())
            (Path(tmp)/'engine').mkdir()
            (Path(tmp)/'engine/arch_compare.csv').write_bytes((ROOT/'paper/data/engine/arch_compare.csv').read_bytes())
            (Path(tmp)/'engine17').mkdir()
            (Path(tmp)/'engine17/sliding_geometry.csv').write_bytes((ROOT/'paper/data/engine17/sliding_geometry.csv').read_bytes())
            result=subprocess.run([sys.executable,str(script)],cwd=tmp,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual((Path(tmp)/'arch-compare.csv').read_bytes(),(ROOT/'paper/data/arch-compare.csv').read_bytes())

    # Current v2 paper bytes/sites and recomputed claims are strict; the new
    # native range is required. Historical dependency coverage is tested below.
    def test_paper_ledger_covers_changed_exports_and_printed_numbers(self):
        from publication_v2 import check_publication,records
        summary=check_publication()
        self.assertTrue(any(r['file']=='paper/sections/05b-models.tex' and r['token']=='13--14' for r in records()))
        self.assertGreater(summary['scanned_numbers'],0)

    # Removing a current coordinate, moving its file/line, or adding an old
    # publication value fails the exact site guard. A clean v2 control passes.
    # The retained891.6-second transcript now lives in the methods appendix.
    def test_paper_ledger_omission_controls(self):
        from publication_v2 import check_publication,records,read_texts
        check_publication()
        sites=records()
        for file,token in (('paper/sections/05b-models.tex','13--14'),
                           ('paper/sections/91-calculation-history.tex','5.6'),
                           ('paper/sections/90-appendix.tex','891.6')):
            target=next(r for r in sites if r['file']==file and r['token']==token)
            with self.subTest(file=file,token=token):
                with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
                    check_publication([r for r in sites if r is not target])
        texts=read_texts()
        for token in ('19--22','457'):
            with self.subTest(token=token):
                with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
                    check_publication(texts=dict(texts, **{'paper/sections/copied.tex':token}))

    # Historical R11/R12 exports remain pinned byte-for-byte; all current v2
    # publication bytes and numeric sites are pinned independently of history.
    def test_historical_exports_and_paper_text_unchanged(self):
        from publication_v2 import check_publication
        self.assertGreater(frozen(),100)
        self.assertGreater(check_publication()['publication_files'],50)

    # The original producer ledger and its line-specific exceptions remain
    # executable at their source revision; v2 does not rewrite their provenance.
    def test_historical_quote_ledger_provenance(self):
        from publication_history import historical_fixture
        with historical_fixture() as root:
            result=subprocess.run([sys.executable,str(root/'calc/tests/r13_ledger.py')],cwd=root,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            # Keep the original numeric scope, waiver and omitted-dependency
            # regression tests at their historical target, without edits.
            names = ['test_r13_reverse',
                     'test_run13.Run13Tests.test_paper_ledger_covers_changed_exports_and_printed_numbers',
                     'test_run13.Run13Tests.test_paper_ledger_omission_controls']
            script = ('import sys,unittest; sys.path.insert(0,' + repr(str(root/'calc/tests')) + '); '
                      'unittest.main(module=None,argv=' + repr(['historical', '-v', *names]) + ')')
            result=subprocess.run([sys.executable,'-c',script],cwd=root,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    # Run13 manifests pin their immutable generator, while all payload hashes
    # still validate. Later runs must not rewrite these historical sidecars.
    def test_new_manifests_and_server_only_flags(self):
        identity=json.loads(snapshot_read('r13-exports', 'calc/out/run13/base/r13_base_base_manifest.json'))['generator']
        paths=list((ROOT/'calc/out/run13').rglob('*manifest.json'));self.assertEqual(len(paths),25)
        for p in paths:
            m=json.loads(p.read_text());self.assertEqual(m['generator'],identity)
            for n,h in m['files'].items():self.assertEqual(hashlib.sha256((p.parent/n).read_bytes()).hexdigest(),h)
        for name in ('vllm_cold','vllm_cached'):
            rows=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run13/measurements'/(name+'.csv')).read_text())))
            self.assertTrue(rows);self.assertTrue(all(r['server_only']=='1' and r['client_bridge']=='0' for r in rows))


if __name__=='__main__':unittest.main()
