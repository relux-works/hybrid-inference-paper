"""R15 admission, boundary, provenance and export regression witnesses."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc.engine import load
from hybridcalc.inputs import InputGap, ROOT
from hybridcalc.measurements_r13 import rows, verified_archive
from hybridcalc.measurements_r14 import day_bounds, one_file, package as previous_package
from hybridcalc.measurements_r15 import cooled_points, package
from hybridcalc.paper_tables import Context, end_memory


class Run15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,i=load('paper-tables-r15');cls.c=Context(s,i);cls.a=cls.c.parallel
        cls.payload=package()[1]

    # Independent interval arithmetic reproduces all22 medians and each of
    # their66 rounds; an average or a picked round cannot pass this witness.
    def test_medians_reject_mean_or_single_round_replacement(self):
        self.assertEqual(len(self.a.points),27)
        for p in (p for p in self.a.points if p['rounds']==3):
            rs=[r for r in rows(self.payload[p['source']]) if r.get('kind')=='round' and r['streams']==p['streams']]
            values=[sum(q['predicted_n']-1 for q in r['requests'])/max(q['predicted_ms']/1000 for q in r['requests']) for r in rs]
            self.assertEqual([r['round'] for r in rs],[1,2,3])
            self.assertAlmostEqual(p['aggregate_tok_s'],sorted(values)[1])
            self.assertEqual([float(x) for x in p['round_aggregate_tok_s'].split('; ')],values)
            self.assertEqual(p['payload_sha256'],hashlib.sha256(self.payload[p['source']]).hexdigest())
        p=next(p for p in self.a.points if p['depth']==131088 and p['streams']==1)
        self.assertAlmostEqual(p['aggregate_tok_s'],5.378,places=3)
        self.assertNotAlmostEqual(p['aggregate_tok_s'],sum(float(v) for v in p['round_aggregate_tok_s'].split('; '))/3,places=2)

    def reduce(self, mutate):
        fragment='-scale131072-largest-np16-'
        name,content=one_file(self.payload,fragment)
        records=copy.deepcopy(rows(content));mutate(records)
        payload=dict(self.payload);payload[name]='\n'.join(json.dumps(r) for r in records).encode()
        return cooled_points(payload,fragment,131088,16,(1,2,4,8,12,16))

    # A valid three-round grid is accepted; missing/duplicate/invalid rounds
    # refuse instead of quietly computing a median from surviving samples.
    def test_incomplete_or_invalid_rounds_refuse_partial_median(self):
        self.assertEqual(len(self.reduce(lambda rs:None)),6)
        for kind in ('missing','duplicate','invalid'):
            def mutate(rs):
                index=next(i for i,r in enumerate(rs) if r.get('kind')=='round')
                if kind=='missing':rs.pop(index)
                elif kind=='duplicate':rs.append(copy.deepcopy(rs[index]))
                else:rs[index]['valid']=False
            with self.subTest(kind=kind),self.assertRaises(InputGap):self.reduce(mutate)

    # Restored16-token suffixes are the protocol. A reread or a changed server
    # shape cannot be admitted as one of the largest-np observations.
    def test_reread_unrestored_or_wrong_np_refuses_base_admission(self):
        for key in ('prompt_n','restore_reused','server_np'):
            def mutate(rs):
                r=next(r for r in rs if r.get('kind')=='round')
                if key=='prompt_n':r['requests'][0]['prompt_n']=131088
                elif key=='restore_reused':r[key]=False
                else:r[key]=4
            with self.subTest(key=key),self.assertRaises(InputGap):self.reduce(mutate)

    # The three physical grids use np32/32/16, with np4 recorded only as a
    # shape control. The faster control cannot silently replace the base.
    def test_np4_control_refuses_faster_base_substitution(self):
        grid={1,2,4,8,12,16,24,32}
        for depth,np,counts in ((32784,32,grid),(65552,32,grid),(131088,16,{1,2,4,8,12,16})):
            ps=[p for p in self.a.points if p['depth']==depth]
            self.assertEqual({p['streams'] for p in ps},counts)
            self.assertEqual({p['server_np'] for p in ps},{np})
        r=self.a.shape_sensitivity[0]
        self.assertAlmostEqual(r['control_aggregate_tok_s'],16.026,places=3)
        self.assertAlmostEqual(r['base_aggregate_tok_s'],14.351,places=3)
        self.assertGreater(r['ratio'],1.11)
        self.assertEqual(self.a.lookup(4,131088)['aggregate_tok_s'],r['base_aggregate_tok_s'])

    # The old hot/control points and1.04M observations remain discoverable,
    # but cannot extend R15's base measured envelope or choose its rates.
    def test_historical_step55_control_and_yarn_refuse_base_reentry(self):
        self.assertTrue(any('step55' in p['condition'] for p in self.a.historical))
        self.assertTrue(any('restored-context control' in p['condition'] for p in self.a.historical))
        self.assertTrue(any(p['depth']==1040016 for p in self.a.historical))
        for p in self.a.historical:self.assertIn('excluded',p['sensitivity'])
        self.assertEqual(max(p['depth'] for p in self.a.points),260016)
        self.assertNotIn('control',self.a.lookup(4,131088)['sources'])
        with self.assertRaisesRegex(InputGap,'depth exceeds deepest'):self.a.measured_lookup(1,1040016)
        self.assertTrue(self.a.lookup(1,1040016)['zones']['depth_modelled'])

    # Each260k raw observation is retained exactly, including six streams
    # and the measured nonmonotonic single-stream point; no smoothing.
    def test_step56_deepest_points_reject_replacement_or_smoothing(self):
        _,content=one_file(previous_package('mac')[1],'-maxctx260k-')
        rs=[r for r in rows(content) if r.get('kind')=='round']
        self.assertEqual({r['streams'] for r in rs},{1,2,4,6,8})
        for r in rs:
            expected=sum(q['predicted_n']-1 for q in r['requests'])/(max(q['predicted_ms'] for q in r['requests'])/1000)
            self.assertEqual(self.a.measured_lookup(r['streams'],260016)['aggregate_tok_s'],expected)
        self.assertGreater(self.a.decode(1,260016),self.a.decode(1,131088))

    # Interior depths interpolate only the same count. Beyond its own last
    # point, every count uses the unchanged R13 law ratio at that exact point.
    def test_lookup_rejects_flat_depth_or_wrong_deepest_anchor(self):
        for count in sorted({p['streams'] for p in self.a.points}):
            ps=[p for p in self.a.points if p['streams']==count]
            for a,b in zip(ps,ps[1:]):
                d=(a['depth']+b['depth'])/2
                self.assertAlmostEqual(self.a.lookup(count,d)['aggregate_tok_s'],(a['aggregate_tok_s']+b['aggregate_tok_s'])/2)
            last=ps[-1];probe=last['depth']+100000
            expected=last['aggregate_tok_s']*self.c.m3_depth_law(count,probe)/self.c.m3_depth_law(count,last['depth'])
            self.assertAlmostEqual(self.a.lookup(count,probe)['aggregate_tok_s'],expected)
            self.assertLess(expected,last['aggregate_tok_s'])
            self.assertFalse(self.a.lookup(count,last['depth'])['zones']['depth_modelled'])
            with self.assertRaisesRegex(InputGap,'depth exceeds deepest'):self.a.measured_lookup(count,last['depth']+1)

    # Count32 has real shallow anchors; count33 refuses at every depth.
    # Interior holes keep the lower measured aggregate with actual occupancy.
    def test_stream_count_extrapolation_and_upper_neighbor_refuse(self):
        for d in (0,65552,1000000):
            self.assertGreater(self.a.decode(32,d),0)
            with self.assertRaisesRegex(InputGap,'above largest measured count'):self.a.decode(33,d)
        for k,lower in ((3,2),(5,4),(7,6),(10,8)):
            p=self.a.lookup(k,131088)
            self.assertEqual(p['aggregate_tok_s'],self.a.lookup(lower,131088)['aggregate_tok_s'])
            self.assertTrue(p['zones']['count_conservative']);self.assertFalse(p['zones']['measured'])

    # Shares use all calls, count actual decode-device seconds, and exclude
    # shallow/modelled/count-hole calls from measured. Flags may overlap.
    def test_zone_shares_reject_dropped_calls_or_unweighted_decode(self):
        calls=[(10000,0,10,0),(65552,0,20,0),(131088,0,30,0),(500000,0,1000,0),(131088,1,100,0)]
        mem=lambda d:10 if d==131089 else 16
        r=day_bounds(calls,[(1,1,0,False)]*5,16,mem,self.a,8)
        probes=[self.a.lookup(min(16,mem(d+n)),d+n) for d,n,o,t in calls]
        times=[o/p['aggregate_tok_s'] for (d,n,o,t),p in zip(calls,probes)]
        self.assertEqual(r['zones']['measured']['calls'],2/5)
        self.assertAlmostEqual(r['zones']['measured']['decode_time'],sum(times[i] for i in (1,2))/sum(times))
        self.assertNotEqual(r['zones']['measured']['calls'],r['zones']['measured']['decode_time'])
        with self.assertRaisesRegex(InputGap,'depth exceeds deepest'):day_bounds(calls,[(1,1,0,False)]*5,16,mem,self.a,8,True)

    # The full16-agent row keeps all39904 calls. Direct per-call admission and
    # decode-time weighting reproduce its partial measurement qualification.
    def test_16_agent_row_refuses_full_measurement_or_filtered_denominator(self):
        cl=self.c.client('m3max',self.c.label('r15.test.link',1e9),'r15.test')
        calls=self.c.g.resolve(cl['matched']).value
        memory=end_memory(calls,self.c.g.resolve(cl['memory']).value)
        measured=0;seconds=total=0.0
        for d,n,o,t in calls:
            p=self.a.lookup(min(16,memory(d+n)),d+n)
            decode=o/p['aggregate_tok_s'];total+=decode
            if p['zones']['measured']:measured+=1;seconds+=decode
        data=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run15/base/client_agents_day.csv').read_text())))
        r=next(r for r in data if r['agents']=='16' and r['link_mbit']=='1000')
        self.assertEqual(len(calls),39904);self.assertEqual(int(r['calls']),len(calls))
        self.assertEqual(measured,17858)
        self.assertAlmostEqual(float(r['measured_call_share']),measured/len(calls))
        self.assertAlmostEqual(float(r['measured_decode_time_share']),seconds/total)
        self.assertLess(float(r['measured_call_share']),.5)

    # Pinned archive custody is reused; a digest mismatch cannot be parsed as
    # measurement input. Successful decoding of the real package is the control.
    def test_wrong_archive_hash_refuses_before_admission(self):
        info=json.loads((ROOT/'calc/hybridcalc/data/run15-measurements.json').read_text())
        self.assertEqual(package()[0]['kit_version'],'1.6.6')
        with self.assertRaisesRegex(InputGap,'archive sha256 mismatch'):verified_archive(ROOT/info['path'],'0'*64)


class Run15ExportTests(unittest.TestCase):
    # Prior runs include every sidecar as well as CSVs. The fresh index binds
    # new bytes; neither changed history nor an incomplete R15 file set passes.
    def test_frozen_history_and_new_export_hashes(self):
        from r15_audit import frozen, verify_tables
        self.assertEqual(frozen(),{'calc/out/paper':150,'calc/out/run13':252,'calc/out/run14':110})
        out=ROOT/'calc/out/run15';index=json.loads((out/'INDEX.json').read_text())
        self.assertEqual(verify_tables(),len(index['files']))
        self.assertEqual(set(index['files']),{str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p.name!='INDEX.json'})
        for name,digest in index['files'].items():self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),digest)

    # Every changed cell (including alarms and labels) has an old/new ledger
    # row. Spot claims also bind the actual table and handwritten prose sites.
    def test_quote_ledger_rejects_missing_changed_cells(self):
        from r15_audit import cell_key, changed_cells, verify_quote_coverage
        ledger=list(csv.DictReader(io.StringIO((ROOT/'calc/ENGINE-QUOTES-R15-261102.csv').read_text())))
        actual={(r['source'],r['engine_key'],r['old'],r['new']) for r in ledger}
        expected={(r['source'],cell_key(r),r['old'],r['new']) for r in changed_cells()}
        self.assertTrue(expected);self.assertFalse(expected-actual)
        self.assertEqual(verify_quote_coverage(ledger),len(expected))
        removed=next(iter(expected))
        reduced=[r for r in ledger if (r['source'],r['engine_key'],r['old'],r['new'])!=removed]
        with self.assertRaisesRegex(AssertionError,'unreported changed cells'):verify_quote_coverage(reduced)
        self.assertTrue(any('tab:clients' in r['paper_site'] for r in ledger))
        self.assertTrue(any(r['comparison']=='r14_to_r15_prose' for r in ledger))
        prose={r['engine_key'] for r in ledger if r['comparison']=='r14_to_r15_prose'}
        self.assertTrue({'M3 s50 compute_month+hosting_month','2500/M3 capacity_day',
                         'traffic egress_2/(compute_month+hosting_month)',
                         'traffic egress_3/(compute_month+hosting_month)'}<=prose)

    # The complete ledger is the positive control: all 8301 counterpart-table
    # cells survive set keying, including five distinct expired R14 anchor rows.
    def test_quote_coverage_clean_control_has_8301_unique_cells(self):
        from r15_audit import changed_cells, verify_quote_coverage
        ledger=list(csv.DictReader(io.StringIO((ROOT/'calc/ENGINE-QUOTES-R15-261102.csv').read_text())))
        cells=changed_cells()
        self.assertEqual(len(cells),8301)
        self.assertEqual(verify_quote_coverage(ledger),8301)
        expired=[r for r in cells if r['table']=='parallel_anchors.csv' and r['new']=='<absent>']
        self.assertEqual(len(expired),40)
        old=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run14/base/parallel_anchors.csv').read_text())))
        expected={('r14:'+str(i),'streams='+r['streams']+'; depth='+r['depth'])
                  for i,r in enumerate(old) if (r['streams'],r['depth']) in
                  {('1','32000'),('4','32000'),('1','1040016'),('2','1040016'),('6','131088')}}
        self.assertEqual({(r['row'],r['coordinates']) for r in expired},expected)
        sites=[r['paper_site'] for r in ledger if r['comparison']=='r14_to_r15'
               and r['source'].endswith('/parallel_anchors.csv') and r['new']=='<absent>']
        self.assertEqual(len(sites),40)
        self.assertEqual(len(set(sites)),40)
        self.assertTrue(all('row=-1' not in s and '; streams=' in s and '; depth=' in s for s in sites))

    # F1 regression plant: remove exactly one duplicate-valued expired cell.
    # Other anchors with the same old/new condition remain; they cannot cover it.
    def test_expired_anchor_duplicate_cell_deletion_is_rejected(self):
        from r15_audit import verify_quote_coverage
        ledger=list(csv.DictReader(io.StringIO((ROOT/'calc/ENGINE-QUOTES-R15-261102.csv').read_text())))
        victims=[i for i,r in enumerate(ledger) if r['source'].endswith('/parallel_anchors.csv')
                 and r['engine_key'].endswith('.condition; streams=4; depth=32000')
                 and r['new']=='<absent>']
        self.assertEqual(len(victims),1)
        victim=ledger[victims[0]]
        self.assertTrue(any(r['engine_key']!=victim['engine_key'] and r['old']==victim['old']
                            and r['new']==victim['new'] and r['source']==victim['source'] for r in ledger))
        reduced=ledger[:victims[0]]+ledger[victims[0]+1:]
        self.assertEqual(len(reduced),len(ledger)-1)
        with self.assertRaisesRegex(AssertionError,'unreported changed cells'):
            verify_quote_coverage(reduced)

    # A row index and matching values do not excuse absent/wrong coordinates.
    # Tampering is in memory and cannot modify the committed ledger or exports.
    def test_quote_coverage_rejects_lost_or_wrong_coordinates(self):
        from r15_audit import verify_quote_coverage
        ledger=list(csv.DictReader(io.StringIO((ROOT/'calc/ENGINE-QUOTES-R15-261102.csv').read_text())))
        victim=next(i for i,r in enumerate(ledger) if r['engine_key'].startswith('client_agents_day.csv[row=3].gain; '))
        for coordinates in ('','client=wrong; link_mbit=1000; agents=6'):
            reduced=copy.deepcopy(ledger)
            reduced[victim]['engine_key']=ledger[victim]['engine_key'].split('; ',1)[0]+'; '+coordinates
            with self.subTest(coordinates=coordinates),self.assertRaisesRegex(AssertionError,'unreported changed cells'):
                verify_quote_coverage(reduced)

    # Existing CSV metadata flags the six-agent hold at both links; adjacent
    # measured rows are valid controls. No numeric export or column is changed.
    def test_six_agent_row_retains_machine_readable_measurement_gap(self):
        data=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run15/base/client_agents_day.csv').read_text())))
        six=[r for r in data if r['agents']=='6']
        self.assertEqual({r['link_mbit'] for r in six},{'1000','300'})
        self.assertEqual(len(six),2)
        for r in six:
            self.assertEqual(set(r['coverage'].split('; ')),{'shallow','depth_modelled','count_conservative'})
            self.assertEqual(float(r['measured_call_share']),0)
            self.assertEqual(float(r['measured_decode_time_share']),0)
            self.assertAlmostEqual(float(r['shallow_call_share']),36181/39904)
        for r in (r for r in data if r['agents'] in ('4','8')):
            self.assertIn('measured',r['coverage'].split('; '))
            self.assertGreater(float(r['measured_call_share']),0)

    # Diagnostic32k single/four rows and R7 anchor_gain must consume the new
    # medians; obsolete normalized anchors cannot leak through these tables.
    def test_diagnostic_tables_reject_stale_parallel_metadata(self):
        read=lambda n:list(csv.DictReader(io.StringIO((ROOT/'calc/out/run15/base'/n).read_text())))
        for row in (r for r in read('decode_scaling.csv') if r['kind']=='measured'):
            self.assertEqual(row['depth'],'32784')
            expected=8.77 if row['streams']=='1' else 24.030
            self.assertAlmostEqual(float(row['aggregate_tok_s']),expected,places=3)
        for row in (r for r in read('decode_sensitivity.csv') if r['client'].startswith('M3 Max') and r['status']=='ok'):
            self.assertAlmostEqual(float(row['anchor_gain']),float(row['four_aggregate_tok_s_32k'])/float(row['single_tok_s_32k']))


if __name__=='__main__':unittest.main()
