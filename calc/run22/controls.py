"""Bounded process-local contract faults; every mutant must fail its named test."""
import argparse
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
sys.path.insert(0,str(ROOT/'calc/tests'))
from run22 import measurements as m,interfaces as i,sentences,economics as e
from test_run22 import Run22Policy

FAULTS={
    'force_f32':'test_bf16_default_refuses_unknown_and_preserves_f32_residency',
    'three_call_cache':'test_low_cache_is_priced_not_excluded_and_three_call_probe_refused',
    'mixed_window':'test_availability_refuses_mixed_windows_with_same_window_control',
    'infer_link':'test_words_ready_refuses_missing_link_with_long_and_short_controls',
    'flat_server_decode':'test_server_decode_refuses_flat_gain_with_capacity_control',
    'copy_16k_to_deep':'test_pro16k_measurement_refuses_deep_reuse_and_capacity_overrun',
}


def fault(name):
    if name=='force_f32':
        original=m.state_bytes
        return patch.object(m,'state_bytes',lambda transport='bf16':original('f32'))
    if name=='three_call_cache':
        original=i.cache_rows
        def cache(rows,known):
            rows=[dict(row,series_calls='4',warm_calls='3') if row.get('series_calls')=='3' else row for row in rows]
            return original(rows,known)
        return patch.object(i,'cache_rows',cache)
    if name=='mixed_window':
        original=i.availability_rows
        def availability(rows,known):
            rows=[dict(row,window_start=rows[0]['window_start'],window_end=rows[0]['window_end']) for row in rows]
            return original(rows,known)
        return patch.object(i,'availability_rows',availability)
    if name=='infer_link':
        original=sentences.validate
        def validate(text,row):
            if 'link=' not in text:
                text+='; link='+sentences.LINKS[row['billing']]
            return original(text,row)
        return patch.object(sentences,'validate',validate)
    if name=='flat_server_decode':
        original=e.Server.decode
        return patch.object(e.Server,'decode',lambda self,depth,streams=32,measurements=None:original(self,16000,streams,measurements))
    if name=='copy_16k_to_deep':
        original=e.Server.decode
        return patch.object(e.Server,'decode',lambda self,depth,streams=32,measurements=None:original(self,16384 if measurements else depth,streams,measurements))
    raise ValueError(name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['control']+list(FAULTS))
    mode=parser.parse_args().mode
    suite=(unittest.defaultTestLoader.loadTestsFromTestCase(Run22Policy) if mode=='control' else
        unittest.TestSuite([Run22Policy(FAULTS[mode])]))
    if mode=='control':
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        with fault(mode):
            result=unittest.TextTestRunner(verbosity=2).run(suite)
    # A mutant failure is an expected-red exit1, never reported as a green gate.
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':main()
