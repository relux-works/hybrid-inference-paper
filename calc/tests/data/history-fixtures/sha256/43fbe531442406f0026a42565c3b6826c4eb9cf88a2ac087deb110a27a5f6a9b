"""Bounded in-memory review controls: 1 is an intended AssertionError, 2 a setup error."""
import argparse
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_run8 import ReviewRegressionTests,R8TablesTests


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mutant',choices=('shadow','tail','hosting','output'));mode=p.parse_args().mutant
    if mode=='shadow':
        # Narrows the boundary to keeping new-input shadow, beyond output-only shadow; the original unmodified code was separately old-red.
        import hybridcalc.paper_tables_r6 as r6
        r6.mean_flops=lambda rows,model:sum(o*r6.flop(model,d) for d,n,o,t in rows)/len(rows)
        test=ReviewRegressionTests('test_full_shadow_two_node_boundary')
    elif mode=='tail':
        # Returning the original lognormal calls must fail the measured tail witness.
        import hybridcalc.sampler_fit as fit
        fit.calibrate=lambda calls,*args:calls
        test=ReviewRegressionTests('test_measured_token_tail')
    elif mode=='hosting':
        # Erasing the two paid hosting components must fail explicit positive GPU/month accounting.
        from hybridcalc.session_hosting import Hosting
        original=Hosting.summary
        def free(self,*args):
            result=original(self,*args)
            result.update(flush_seconds=self.add('mutant.flush.'+str(len(self.c.g.nodes)),[],lambda:0),storage=self.add('mutant.storage.'+str(len(self.c.g.nodes)),[],lambda:0),seconds=self.add('mutant.migration.'+str(len(self.c.g.nodes)),[],lambda:0))
            return result
        Hosting.summary=free
        test=ReviewRegressionTests('test_hosting_is_in_gpu_month')
    else:
        # Collapsing output-only onto the conservative policy must lose the declared capacity/cost sensitivity.
        from hybridcalc import paper_tables_r8 as r8
        original=r8.output_sensitivity
        def collapse(context):
            for q in context.inputs.data['r8']['output_fractions']:q['value']=1
            return original(context)
        r8.output_sensitivity=collapse
        R8TablesTests.setUpClass()
        test=R8TablesTests('test_output_only_sensitivity')
    result=unittest.TextTestRunner().run(unittest.TestSuite([test]))
    return 0 if result.wasSuccessful() else 2 if result.errors else 1


if __name__=='__main__':sys.exit(main())
