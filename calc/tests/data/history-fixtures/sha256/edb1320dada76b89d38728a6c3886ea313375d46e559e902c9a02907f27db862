"""In-memory protocol mutants: expected AssertionError exit1, setup error2, survivor0."""
import argparse,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc import session_hosting as hosting
from test_run9 import ProtocolTests


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mutant',choices=('full_slot','free_pending','no_tail','ram_forever'));kind=p.parse_args().mutant
    if kind=='full_slot':
        original=hosting.Hosting.vector
        def old(self,*args):
            node=original(self,*args);refs,fn=self.c.g.nodes[node]
            def rewrite(*values):
                result=fn(*values);rows,kv,state=values[:3]
                result[:]=[(a,b+d*kv*result.state_seconds/state) for (a,b),(d,n,o,t) in zip(result,rows)]
                return result
            self.c.g.nodes[node]=(refs,rewrite);return node
        hosting.Hosting.vector=old;name='test_append_only_spill'
    elif kind=='free_pending':
        original=hosting.route
        hosting.route=lambda *args:original(*args[:-1],'per_call');name='test_pending_compute_enters_decision'
    elif kind=='no_tail':
        original=hosting.Hosting.daily
        def free(self,*args,**kw):
            node=original(self,*args,**kw);refs,fn=self.c.g.nodes[node]
            self.c.g.nodes[node]=(refs,lambda *v:v[0]*v[2]);return node
        hosting.Hosting.daily=free;name='test_daily_reload_spill_conservation'
    else:
        original=hosting.Hosting.storage
        def resident(self,*args,**kw):
            node=original(self,*args,**kw);refs,fn=self.c.g.nodes[node]
            def price(*values):
                values=list(values);values[4]='ram_month';return fn(*values)
            self.c.g.nodes[node]=(refs,price);return node
        hosting.Hosting.storage=resident;name='test_retention_windows_and_promotion'
    r=unittest.TextTestRunner().run(unittest.TestSuite([ProtocolTests(name)]))
    return 0 if r.wasSuccessful() else 2 if r.errors else 1

if __name__=='__main__':sys.exit(main())
