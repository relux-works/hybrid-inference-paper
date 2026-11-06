"""Bounded process-only faults; control exits0, each named mutant exits1."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_run19
from hybridcalc import measurements_r19 as r

mode=sys.argv[1]
if mode=='omit_state':
    r.Node.session_bytes=lambda self,d,delta=0,output=0:(d+delta+output)*r.KV
    names=['NodeContracts.test_resident_overflow_must_swap_or_refuse']
elif mode=='free_swap':
    r.Node.swap_seconds=lambda *args:0
    names=['NodeContracts.test_swap_rejects_free_reload_double_count_and_depth_extrapolation']
elif mode=='ignore_capacity':
    r.Node.admit=lambda self,d,delta=0,output=0:self.session_bytes(d,delta,output)
    names=['NodeContracts.test_capacity_estimate_cannot_extend_configured_or_measured_limits']
elif mode=='ignore_catchup':
    original=r.route
    r.route=lambda own,remote,shadow,output,wire,foreground,mode:original(own,remote,shadow,output,wire,foreground,'per_call')
    names=['NodeContracts.test_routing_rejects_ignored_catchup_and_bills_only_selected_work']
elif mode=='unpriced_box':
    r.checked_price=lambda cfg:json.loads((r.ROOT/cfg['price_evidence']['path']).read_text())
    names=['NodeContracts.test_prices_reject_card_only_box_market_relabelling_and_bad_digest']
elif mode=='pool_retention':
    original=r.fleet
    def wrong(p,link,tier,team,calls_day,hours,load,sessions,cfg):
        import copy
        cfg=copy.deepcopy(cfg);cfg['tiers']['RAM']['capacity_bytes']=1e15
        return original(p,link,tier,team,calls_day,hours,load,sessions,cfg)
    r.fleet=wrong
    names=['NodeContracts.test_fleet_rejects_pooled_vram_fragmentation_and_free_retention']
elif mode=='time_units':
    original=r.calculate
    def wrong_units(s,i):
        result=original(s,i)
        for table in result['tables']:
            for key in table['columns']:
                if key.endswith('_mb_s') or key.endswith('_mbit_s') or key=='bytes_s':table['columns'][key]='s'
        return result
    r.calculate=wrong_units
    names=['Run19Outputs.test_export_units_reject_bandwidth_labelled_as_time']
else:
    assert mode=='control','unknown mode'
    names=['NodeContracts']
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_run19.'+n for n in names])
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
