"""Bounded process-only narrowing faults, with named positive controls."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_run21
from hybridcalc import deep_r21 as d, measurements_r21 as r
from hybridcalc import measurements_r19 as r19, measurements_r16 as r16
from hybridcalc import server_economics_r20 as s

mode=sys.argv[1]
if mode=='rental_missing_scope':
    r19.rental_basis=lambda old:old
    names=['CustodyContracts.test_r19_rental_basis_missing_coverage_regression_and_numeric_control']
elif mode=='combined_pause':
    original=d.profile_rows
    def wrong(stats):
        rows=original(stats)
        for row in rows:
            if row['profile']=='claude_deep'and row['metric']=='gap_seconds'and row['statistic']=='p90':row['value']=34.8
        return rows
    d.profile_rows=wrong
    names=['ProfileContracts.test_profile_source_refuses_corruption_and_combined_pause_substitution']
elif mode=='api_same_yarn':
    original=d.extension_basis
    d.extension_basis=lambda model,side:original(model,'client'if side=='api'else side)
    names=['ProfileContracts.test_yarn_refuses_identical_api_extension_claim_with_hybrid_control']
elif mode=='shared_kv':
    original=s.Server.decode
    def wrong(*args,**kwargs):
        result=original(*args,**kwargs);result['gain']=result['batch'];return result
    s.Server.decode=wrong
    names=['ServerContracts.test_million_capacity_refuses_pro_and_depth_independent_batch_gain']
elif mode=='single_gpu_glm':
    original=r.glm_batch
    def wrong(*args):
        result=original(*args);result['replica_gpus']=1;return result
    r.glm_batch=wrong
    names=['ServerContracts.test_glm_batch_refuses_dense_weight_sharing_and_single_gpu_fit']
elif mode=='missing_state':
    r19.STATE=0
    names=['ServerContracts.test_million_links_refuse_missing_state_and_unlabelled_local_estimate']
elif mode=='free_import':
    r16.ClientImport.at_depth=lambda *args:0
    names=['ServerContracts.test_million_links_refuse_missing_state_and_unlabelled_local_estimate']
elif mode=='ungated_pro':
    original=r19.Node.__init__
    def wrong(self,key,cfg=None):
        cfg=cfg or r19.config()
        if key=='pro6000':cfg['nodes'][key]['rate_basis']=r19.config()['nodes'][key]['rate_basis']
        original(self,key,cfg)
    r19.Node.__init__=wrong
    names=['CustodyContracts.test_pro6000_refuses_fresh_hybrid_measurement_relabelling']
elif mode=='unvetted_api':
    s.admission=lambda *args:[]
    names=['ApiContracts.test_million_admission_refuses_alibaba_and_unverified_glm_cache']
elif mode=='free_cache_misses':
    original=s.api_cost;s.api_cost=lambda row,means,hit:original(row,means,1)
    names=['ApiContracts.test_provider_cache_data_changes_effective_price_with_positive_control']
elif mode=='duplicate_concurrency':
    original=r.million_own
    def wrong(*args,**kwargs):
        result=original(*args,**kwargs);result['total_streams']*=8;return result
    r.million_own=wrong
    names=['ServerContracts.test_million_fleet_refuses_duplicate_concurrency_and_invalid_team']
elif mode=='time_units':
    original=r.unit;r.unit=lambda key,value:'s'if key=='bytes_s'else original(key,value)
    names=['CustodyContracts.test_units_refuse_bandwidth_as_time_and_node_price_as_person_price']
elif mode=='restart_api_groups':
    r.old.billing_calls=lambda calls,indices,chunk:[calls[i]for i in indices]
    names=['ApiContracts.test_profile_api_refuses_cache_group_restart_after_filtering']
elif mode=='underreserve_tail':
    r.profile_reservation=lambda calls,minimum,servers:minimum
    names=['ServerContracts.test_profile_retention_refuses_shallower_than_end_depth_reservation']
elif mode=='omit_api_scope':
    import r21_export_labels as labels
    labels.scope=lambda *args:'no workload provenance'
    names=['ExportLabelContracts.test_r20_api_coverage_regression_refuses_missing_population_provenance']
elif mode=='hide_missing_windows':
    import r21_export_labels as labels
    labels.availability=lambda *args:'minimum recorded windows; missing unverified'
    names=['ExportLabelContracts.test_r20_missing_availability_regression_names_partial_windows']
else:
    assert mode=='control'
    names=['ProfileContracts','ServerContracts','ApiContracts',
        'ExportLabelContracts.test_r20_api_coverage_regression_refuses_missing_population_provenance',
        'ExportLabelContracts.test_r20_missing_availability_regression_names_partial_windows',
        'CustodyContracts.test_pro6000_refuses_fresh_hybrid_measurement_relabelling',
        'CustodyContracts.test_r19_rental_basis_missing_coverage_regression_and_numeric_control',
        'CustodyContracts.test_units_refuse_bandwidth_as_time_and_node_price_as_person_price']
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_run21.'+name for name in names])
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful()else 1)
