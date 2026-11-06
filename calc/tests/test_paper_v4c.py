"""R17 publication and trace-accounting regressions; no runtime qualification."""
import csv
import gzip
import hashlib
import json
import re
import unittest
from r13_audit import ROOT, module

SOURCE=ROOT/'data/measurements/paper-v4c-2026-11-03'


def read(name):
    with (ROOT/'paper/data/engine17'/name).open(newline='') as stream:
        return list(csv.DictReader(stream))


class PaperV4cTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v4c_guard',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    def plant(self,key,replacement):
        file,marker,phrase=self.off.expected()[key]
        part=next(p for p in self.texts[file].split('\n\n') if marker in p)
        changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),lambda _:replacement,part,count=1)
        self.assertEqual(n,1,key);self.assertNotEqual(changed,part,key)
        return dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})

    # Each displayed threshold follows exact tensor bytes divided by its
    # source budget. Priority and Qwen-import portability are independent limits.
    def test_threshold_cells_recompute_payload_and_budget(self):
        params={'qwen27':(34816,156893184),'glimmer30':(7072,43450368),'gemma31':(43520,445644800)}
        for r in read('architecture_link_threshold.csv'):
            k,s=params[r['model']]
            if r['state_format']=='bf16':s//=2
            payload=k*int(r['delta'])+s
            self.assertEqual(int(r['wire_bytes']),payload)
            budget=float(r['local_prefill_s'])-sum(float(r[f]) for f in ('server_prefill_s','import_s','rtt_s'))
            self.assertGreater(budget,0)
            self.assertAlmostEqual(payload/budget/1e6,float(r['break_even_downstream_mb_s']),places=10)
            self.assertEqual(r['background_priority_interim']=='True',r['model']!='qwen27')
            if r['model']!='qwen27':
                self.assertTrue(r['import_assumption'].startswith('r16_qwen_token_depth_portability:'))
                self.assertIn('not measured',r['import_assumption'])

    # Actual source rows supply the counterexample to a universal larger-S
    # threshold claim: Gemma is below Qwen at100k, above at32k, both interim.
    def test_gemma_comparison_is_depth_dependent(self):
        rows={(r['model'],int(r['depth'])):r for r in read('architecture_link_threshold.csv') if r['state_format']=='f32' and r['delta']=='2343'}
        for depth in (32000,64000,100000):
            g,q=rows['gemma31',depth],rows['qwen27',depth]
            self.assertGreater(int(g['wire_bytes']),int(q['wire_bytes']))
            self.assertGreater(float(g['local_prefill_s']),float(q['local_prefill_s']))
            self.assertEqual(float(g['break_even_downstream_mb_s'])>float(q['break_even_downstream_mb_s']),depth==32000)
        key='v4b Gemma link scope';file,_,phrase=self.off.expected()[key]
        changed=self.texts[file].replace(phrase,'Большая фиксированная часть всегда требует более быстрого канала.',1)
        self.assertNotEqual(changed,self.texts[file]);self.assertIn(key,self.off.missing(dict(self.texts,**{file:changed})))

    # The extrapolation fixes one timing budget, varies only bytes, and keeps
    # a strictly positive threshold atS=0 because new KV still transfers.
    def test_extrapolation_is_bytes_only_and_not_a_model_measurement(self):
        rows=read('architecture_extrapolation.csv')
        budgets=set()
        for r in rows:
            payload=float(r['fixed_mb'])*1e6+float(r['kv_kib_token'])*1024*2343
            budget=float(r['local_prefill_s'])-sum(float(r[k]) for k in ('server_prefill_s','import_s','rtt_s'))
            self.assertEqual(float(r['wire_bytes']),payload);budgets.add(budget)
            self.assertAlmostEqual(payload/budget/1e6,float(r['break_even_downstream_mb_s']),places=10)
            self.assertIn('not a model claim',r['basis'])
        self.assertEqual(len(budgets),1)
        self.assertTrue(all(float(r['break_even_downstream_mb_s'])>0 for r in rows))
        self.assertEqual(len(rows),15)

    # The live-window regression independently requires allW positions in
    # today's native projection; delta-only windows cannot satisfy either size.
    def test_architecture_projection_keeps_complete_live_window(self):
        arch=module('v4c_arch',ROOT/'paper/data/arch_compare.py')
        rows={r['model']:r for r in arch.calculated_rows()}
        with (ROOT/'paper/data/arch-compare.csv').open(newline='') as stream:
            native={r['model']:r for r in csv.DictReader(stream)}
        for model,key in ((arch.MODELS[1],'glimmer30'),(arch.MODELS[2],'gemma31')):
            geo=next(r for r in read('sliding_geometry.csv') if r['model']==key)
            full=int(geo['full_kv_bytes_token']);window=int(geo['window_bytes']);per=int(geo['window_bytes_position'])
            for n,field in ((1000,'delta_1k_mb'),(10000,'delta_10k_mb')):
                expected=n*full+window
                self.assertEqual(arch.delta(model,n,prefix=100000),expected)
                self.assertEqual(float(rows[model[0]][field]),expected/1e6)
                self.assertEqual(float(native[model[0]][field]),expected/1e6)
            self.assertNotEqual(1000*full+1000*per,1000*full+window)
        self.assertEqual(f'{float(rows[arch.MODELS[1][0]]["delta_1k_mb"]):.0f}','51')

    # First-call residuals use the raw JSONL, not subtraction of the older
    # one-decimal summaries. Rounded25.5 is an explicit rejected alternative.
    def test_first_call_raw_precision_and_enclosing_preparation(self):
        first_path=next(SOURCE.glob('hybrid-bench-*.jsonl'))
        r=json.loads(first_path.read_text().splitlines()[11]);self.assertEqual((r['stage'],r['mode']),('call','hybrid'))
        measured=sum(r[k]/1000 for k in ('server_prefill_ms','transfer_ms','import_ms'))
        remainder=r['ttft_seconds']-measured
        remote=r['remote_prepare_ms']/1000-measured
        client=r['ttft_seconds']-r['remote_prepare_ms']/1000
        self.assertAlmostEqual(remainder,remote+client)
        self.assertEqual([f'{v:.3f}' for v in (r['ttft_seconds'],remainder,remote,client)],['201.655','25.370','19.659','5.711'])
        self.assertNotEqual(f'{remainder:.3f}','25.500')
        self.assertGreater(r['total_seconds'],r['ttft_seconds'])
        key='v4b first call unattributed';file,marker,phrase=self.off.expected()[key]
        changed=self.plant(key,'25.5 секунды пока не атрибутированы.')
        self.assertIn(key,self.off.missing(changed))

    # Base import is exactly the sum of all ten chunks. Double-counting staged
    # requests changes the residual and must fail the actual publication binding.
    def test_growing_base_import_sum_rejects_double_counting(self):
        trace=json.loads(gzip.decompress((SOURCE/'INSTRUMENTATION-TIMING-EXTRACT.json.gz').read_bytes()))
        base=next(r for r in trace['base_and_offload_call_components'] if r['turn']==0)
        chunks=base['chunks'];self.assertEqual(len(chunks),10)
        imported=sum(r['import_ms']/1000 for r in chunks)
        staged=sum(r['import_ms']/1000 for r in chunks if r['status']=='staged')
        self.assertAlmostEqual(imported,base['import_seconds']);self.assertEqual(sum(r['status']=='staged' for r in chunks),9)
        self.assertEqual(f'{imported:.3f}','2.908')
        remainder=base['ttft_seconds']-base['snapshot_download_seconds_sum']-base['server_prefill_seconds']-base['transfer_seconds']-imported
        self.assertEqual(f'{remainder:.3f}','41.168');self.assertNotEqual(f'{remainder-staged:.3f}','41.168')
        key='run17 base import total';file,_,phrase=self.off.expected()[key]
        changed=self.texts[file].replace(phrase,phrase.replace('2.908',f'{imported+staged:.3f}'),1)
        self.assertIn(key,self.off.missing(dict(self.texts,**{file:changed})))

    # Hash bytes include snapshots plus deltas and remain outside the download
    # timer. No duration is inferred from bytes or from an unrelated CPU rate.
    def test_growing_accounting_keeps_hashing_inside_upper_bound(self):
        a=json.loads((SOURCE/'time-accounting-arithmetic.json').read_text())
        t=json.loads(gzip.decompress((SOURCE/'INSTRUMENTATION-TIMING-EXTRACT.json.gz').read_bytes()))
        for row in a['growing']:
            c=next(c for c in t['base_and_offload_call_components'] if c['turn']==row['turn'])
            self.assertEqual(row['hash_bytes'],c['wire_bytes']+c['snapshot_download_bytes_sum'])
            self.assertAlmostEqual(row['residual_ttft'],c['ttft_seconds']-c['snapshot_download_seconds_sum'])
            self.assertGreater(row['unattributed'],row['inside_extend_gap'])
        for key in ('run16 residual limit','run17 hashing remains','run17 arithmetic upper bound'):
            file,marker,phrase=self.off.expected()[key]
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),'После вычитания снимков получен производственный TTFT.',part,count=1)
            self.assertEqual(n,1,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})))

    # CPU evidence is a16-token0.8B state and classifies bf16 as lossy. It
    # cannot establish GPU/Mac quality, latency or lossless control success.
    def test_bf16_cpu_rounding_and_measurement_boundary(self):
        report=(SOURCE/'RESULTS-hybrid-a-r38-261103.md').read_text()
        self.assertIn('maximum observed 0.00389105',report)
        self.assertIn('lossy/exit5',report)
        self.assertIn('16-token Qwen3.5-0.8B',report)
        self.assertLess(0.00389105,2**-8)
        for r in read('bf16_transfer_egress.csv'):
            matches=[f for f in read('bf16_transfer_egress.csv') if f['depth']==r['depth'] and f['delta']==r['delta'] and f['downstream_mb_s']==r['downstream_mb_s'] and f['state_format']=='f32']
            if r['state_format']=='bf16':
                self.assertEqual(int(matches[0]['wire_bytes'])-int(r['wire_bytes']),78446592)
                self.assertNotEqual(int(r['wire_bytes']),int(matches[0]['wire_bytes'])//2)
        key='run17 bf16 CPU loss';file,_,phrase=self.off.expected()[key]
        changed=self.plant(key,'bf16 не имеет потерь и прошёл точный контроль.')
        self.assertIn(key,self.off.missing(changed))

    # Every new named row and qualification has an actual checker omission
    # control; a matching scientific table cannot hide a removed limitation.
    def test_run17_publication_sites_reject_omissions(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for key,(file,marker,phrase) in self.off.v4c_expected().items():
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),'УДАЛЕНО',part,count=1)
            self.assertEqual(n,1,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})))

    # Source additions are byte-exact accepted exports; the two new waits are
    # explicitly owner-required, while measured CPU implementation is not pending.
    def test_snapshot_custody_and_six_real_pending_sites(self):
        for path in (ROOT/'paper/data/engine17').glob('*.csv'):
            self.assertEqual(path.read_bytes(),(ROOT/'calc/out/run17/architectures'/path.name).read_bytes())
        inventory=json.loads((ROOT/'calc/tests/data/paper-v4c-pending.json').read_text())
        self.assertEqual(len(inventory),6);self.assertEqual(self.off.pending_gaps(self.texts),[])
        self.assertEqual(sum('Owner r20c' in r['source'] for r in inventory),2)
        changed=dict(self.texts,**{'90-appendix.tex':self.texts['90-appendix.tex']+'\n\\pending{реализация передачи bf16 на CPU}\n'})
        self.assertEqual(self.off.pending_gaps(changed),['v4b pending inventory'])
