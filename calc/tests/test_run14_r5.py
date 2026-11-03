"""Run14 r5 contracts: named refusals beside accepted controls."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load
from hybridcalc.inputs import InputGap
from hybridcalc.paper_tables import Context,measured_rate
from hybridcalc.session_hosting import Migration,policy_with_reload
from hybridcalc.run14_r5 import import_seconds,first_call_check,step57_check,full_server_stats,choose_candidate,cuda_import_rows,evidence
from hybridcalc.measurements_r14 import day_bounds,package,one_file,rows


class Run14R5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,i=load('paper-tables-r14');cls.c=Context(s,i);cls.a=cls.c.parallel

    # Exact same-count deepest anchors are continuous; using32k or a different
    # count's depth law cannot reproduce the required anchored Run13 ratio.
    def test_depth_law_rejects_32k_reanchor_and_flat_clamp(self):
        c=self.c;a=self.a
        for k in (4,6,8,12,16):
            deepest=max(p['depth'] for p in a.points if p['streams']==k)
            exact=a.measured_lookup(k,deepest)['aggregate_tok_s']
            self.assertEqual(a.lookup(k,deepest)['aggregate_tok_s'],exact)
            expected=exact*c.m3_depth_law(k,1000000)/c.m3_depth_law(k,deepest)
            self.assertAlmostEqual(a.lookup(k,1000000)['aggregate_tok_s'],expected)
            self.assertNotEqual(expected,exact)
            self.assertTrue(a.lookup(k,1000000)['zones']['depth_modelled'])

    # A hole must preserve lower-count aggregate and actual occupancy; it
    # cannot borrow the upper count's faster aggregate or admit count25.
    def test_count_hole_rejects_upper_neighbor_and_above_max(self):
        a=self.a
        self.assertEqual(a.lookup(3,131088)['aggregate_tok_s'],a.lookup(2,131088)['aggregate_tok_s'])
        self.assertNotEqual(a.lookup(3,131088)['aggregate_tok_s'],a.lookup(4,131088)['aggregate_tok_s'])
        self.assertGreater(a.decode(24,1000000),0)
        for d in (0,65552,1000000):
            with self.assertRaisesRegex(InputGap,'above largest measured count'):a.decode(25,d)

    # Flag shares use all calls and actual aggregate decode seconds, not an
    # unweighted average or a silently depth-filtered workload.
    def test_zone_shares_reject_call_weighting_for_decode_time(self):
        calls=[(32000,0,10,0),(500000,0,1000,0)]
        s=[(1,1,0,False)]*2
        r=day_bounds(calls,s,4,lambda d:4,self.a,8)
        expected=(1000/self.a.lookup(4,500000)['aggregate_tok_s'])/sum(o/self.a.lookup(4,d)['aggregate_tok_s'] for d,n,o,t in calls)
        self.assertEqual(r['zones']['depth_modelled']['calls'],.5)
        self.assertAlmostEqual(r['zones']['depth_modelled']['decode_time'],expected)
        self.assertNotEqual(expected,.5)
        with self.assertRaisesRegex(InputGap,'depth exceeds deepest'):day_bounds(calls,s,4,lambda d:4,self.a,8,True)

    # A selected offload pays import once in both wall wait and device time;
    # adding import can reject a formerly winning offload without partial wire.
    def test_import_rejects_zero_device_time_and_nonwinning_offload(self):
        calls=[(0,100,0,0)];model=dict(base_flop=1,attention_slope=0,sparse_slope=0,sparse_cap=0,context_limit=1000,kv=1,wire_state=100)
        link=dict(bandwidth=1e12,goodput=1,latency=0)
        v=Migration([(0,0)]);v.catch_up='per_call'
        old=policy_with_reload(calls,model,1e9,link,lambda d:10,v)
        new=policy_with_reload(calls,model,1e9,link,lambda d:10,v,lambda b:2)
        self.assertTrue(new[0][3]);self.assertEqual(new[0][1],2)
        self.assertAlmostEqual(new[0][0]-old[0][0],2)
        denied=policy_with_reload(calls,model,1e9,link,lambda d:10,v,lambda b:11)
        self.assertEqual(denied[0],(10,10,0,False))

    # Baseline reproduces the measured token/time point; CPU-only v2 evidence
    # and invalid token counts cannot become an admitted Mac import rate.
    def test_import_v2_refuses_ungated_rate_and_negative_bytes(self):
        self.assertEqual(import_seconds(39504),42.4)
        self.assertGreater(import_seconds(1),0)
        with self.assertRaisesRegex(InputGap,'Mac gate pending'):import_seconds(100,'import_speed_v2')
        for size in (-1,float('nan')):
            with self.assertRaisesRegex(InputGap,'nonnegative'):import_seconds(size)

    # The independent PR9 data reproduces the fitted CUDA intercept/slope;
    # neither a checksum mismatch nor the M3 one-point rate may replace it.
    def test_cuda_import_refuses_unverified_bytes_or_mac_rate(self):
        data=cuda_import_rows();xs=[r['remote_applied'] for r in data];ys=[r['import_ms']/1000 for r in data]
        mx=sum(xs)/len(xs);my=sum(ys)/len(ys)
        slope=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
        fixed=my-slope*mx
        self.assertAlmostEqual(import_seconds(0,'cuda_pr9'),fixed)
        self.assertAlmostEqual(import_seconds(40000,'cuda_pr9'),fixed+40000*slope)
        self.assertNotEqual(import_seconds(40000,'cuda_pr9'),import_seconds(40000))
        bad=copy.deepcopy(evidence());bad['cuda_pr9']['sha256']='0'*64
        with patch('hybridcalc.run14_r5.evidence',return_value=bad):
            with self.assertRaisesRegex(InputGap,'byte identity mismatch'):cuda_import_rows()

    # All first-call components share the old wire configuration; the25.5s
    # measured residual stays visible instead of being fitted into import.
    def test_first_call_rejects_silent_residual_fit_or_b300_node(self):
        values={r['component']:r for r in first_call_check(self.c)}
        self.assertAlmostEqual(values['unallocated']['measured_s'],25.5)
        self.assertEqual(values['unallocated']['predicted_s'],0)
        self.assertAlmostEqual(values['total']['predicted_s'],sum(values[k]['predicted_s'] for k in ('server_prefill','transfer','client_import')))
        self.assertLess(values['server_prefill']['predicted_s'],15)

    # Trace corruption/rereads refuse rather than qualifying as a clean
    # held-out check. The actual trace has exactly4 calls per session.
    def test_step57_refuses_rereads_and_missing_calls(self):
        _,content=one_file(package('mac')[1],'agents-loop');trace=rows(content)
        actual=step57_check(self.c,trace)
        self.assertEqual([r['calls'] for r in actual[::2]],[4,8,16,32])
        bad=copy.deepcopy(trace);next(r for r in bad if r['kind']=='call')['reread']=True
        with self.assertRaisesRegex(InputGap,'invalid held-out trace'):step57_check(self.c,bad)
        bad=[r for r in trace if not (r['kind']=='call' and r['agents']==1 and r['turn']==0)]
        with self.assertRaisesRegex(InputGap,'invalid held-out trace'):step57_check(self.c,bad)

    # Evicted full-server state pays read+append on every call and does not
    # charge tool-idle GPU residency. Memory nonfit never becomes cheap service.
    def test_symmetric_reload_rejects_free_eviction_and_nonfit(self):
        c=self.c;s=c.server('rtx6000',c.model('qwen27'));calls=[(131072,2000,100,1)]
        hbm=full_server_stats(c,calls,s,'HBM');ram=full_server_stats(c,calls,s,'RAM');nvme=full_server_stats(c,calls,s,'NVMe')
        self.assertEqual(hbm['migration_s'],0)
        self.assertGreater(ram['seconds'],hbm['seconds']);self.assertGreater(nvme['seconds'],ram['seconds'])
        self.assertGreater(nvme['wait'][0],ram['wait'][0])
        self.assertEqual(ram,full_server_stats(c,[(131072,2000,100,9999)],s,'RAM'))
        with self.assertRaisesRegex(InputGap,'does not fit'):full_server_stats(c,[(4000000,1,1,0)],s,'RAM')

    # Cost minimization has the same latency limits for both routes; a cheap
    # but slow candidate and an empty admissible set cannot win.
    def test_cheapest_admission_rejects_latency_violation(self):
        good=dict(person_month=2,server='PRO6000',storage_tier='RAM',prefill_mean_s=1,prefill_p90_s=2,team=500)
        slow=dict(good,person_month=1,prefill_p90_s=20)
        self.assertIs(choose_candidate([good,slow],2,3),good)
        with self.assertRaisesRegex(InputGap,'no configuration'):choose_candidate([slow],2,3)


class Run14R5ExportTests(unittest.TestCase):
    # The isolated sensitivity uses the same R5 depth law and workload: local
    # capacity is invariant while real import reduces hybrid capacity/savings.
    def test_import_effect_rejects_changed_local_baseline_or_free_import(self):
        import csv,io
        from hybridcalc.inputs import ROOT
        data=list(csv.DictReader(io.StringIO((ROOT/'calc/R14-R5-IMPORT-EFFECT-261102.csv').read_text())))
        self.assertTrue(data)
        for row in data:
            if row['metric'] in ('local_sessions_day','local_agent_s'):self.assertEqual(float(row['delta']),0)
            elif row['metric']=='hybrid_sessions_day':self.assertLessEqual(float(row['delta']),0)
            elif row['metric']=='saved_seconds_call':self.assertLess(float(row['delta']),0)
        self.assertTrue(any(r['metric']=='hybrid_sessions_day' and float(r['delta'])<0 for r in data))

    # Large teams keep PRO6000 candidates. Each chosen tier minimizes cost
    # among real same-route candidates under the identical latency/retention
    # requirements; no zero-storage/full-server exception is admitted.
    def test_symmetric_export_rejects_team_cap_and_unequal_limits(self):
        import csv,io
        from hybridcalc.inputs import ROOT
        path=ROOT/'calc/out/run14/base'
        read=lambda name:list(csv.DictReader(io.StringIO((path/name).read_text())))
        choices=read('symmetric_storage_candidates.csv')
        self.assertEqual({r['storage_tier'] for r in choices},{'HBM','RAM','NVMe'})
        large=[r for r in choices if float(r['team'])>=500 and 'RTX PRO 6000' in r['server']]
        self.assertTrue(large);self.assertTrue(all(r['eligible']=='1' for r in large))
        groups={}
        for row in choices:
            key=tuple(row[k] for k in ('profile','team','route','client','basis','server'))
            groups.setdefault(key,[]).append(row)
            self.assertGreater(float(row['hosting_storage_month']),0)
        for rows_ in groups.values():
            self.assertEqual(len({tuple(r[k] for k in ('latency_mean_limit_s','latency_p90_limit_s','retention','retained_sessions')) for r in rows_}),1)
            admitted=[r for r in rows_ if float(r['prefill_mean_s'])<=float(r['latency_mean_limit_s']) and float(r['prefill_p90_s'])<=float(r['latency_p90_limit_s'])]
            chosen=next(r for r in rows_ if r['tier_selected']=='1')
            self.assertEqual(float(chosen['person_month']),min(float(r['person_month']) for r in admitted))
        main=read('perimeter_cost.csv')
        groups={}
        for row in main:
            if row['route']=='Macs only':continue
            groups.setdefault(tuple(row[k] for k in ('profile','team','route','client','basis')),[]).append(row)
        for rows_ in groups.values():
            chosen=next(r for r in rows_ if r['selected']=='1')
            self.assertEqual(float(chosen['person_month']),min(float(r['person_month']) for r in rows_))


if __name__=='__main__':unittest.main()
