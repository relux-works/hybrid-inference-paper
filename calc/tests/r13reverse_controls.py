"""Bounded source-function mutants for the repeated r5e/r5f ledger findings."""
import inspect
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r13_ledger as ledger
import r13_reverse as reverse

mode=sys.argv[1]
names=None
if mode=='arch_only':
    source=inspect.getsource(reverse.changed_values)
    needle='return pairs,accounting'
    assert source.count(needle)==1
    source=source.replace(needle,"return [p for p in pairs if 'arch' in p['engine_key']],accounting")
    exec(compile(source,'<arch-only reverse guard>','exec'),reverse.__dict__)
    name='test_reverse_guard_rejects_copied_non_arch_changed_values'
elif mode=='token_waiver':
    source=inspect.getsource(ledger.native_changes)
    needle='if collision in NATIVE_COLLISIONS:'
    assert source.count(needle)==1
    source=source.replace(needle,'if token in {c[2] for c in NATIVE_COLLISIONS}:')
    exec(compile(source,'<token-only native waiver>','exec'),ledger.__dict__)
    name='test_paper_ledger_waivers_are_site_bound'
elif mode=='percent_unscaled':
    source=inspect.getsource(reverse.witnesses)
    needle='scales+=(Decimal(100),)'
    assert source.count(needle)==1
    source=source.replace(needle,'pass # omit fraction-to-percent rendering')
    exec(compile(source,'<unscaled percent reverse guard>','exec'),reverse.__dict__)
    names=['test_reverse_guard_rejects_percent_'+value+'_same_file' for value in ('45_6','72_3','95_4','30_5')]
elif mode in ('file_token_waiver','file_token_ledger'):
    source=inspect.getsource(reverse.check_reverse)
    if mode=='file_token_waiver':
        needle="(r['paper_site'].rsplit(':',1)[0],int(r['paper_site'].rsplit(':',1)[1]),r['old']) not in waivers"
        replacement="(r['paper_site'].rsplit(':',1)[0],r['old']) not in {(s[0],s[2]) for s in waivers}"
        name='test_reverse_waiver_rejects_same_file_30_percent_at_new_line'
    else:
        needle="(r['paper_site'],r['old']) not in exact and"
        replacement="(r['paper_site'].rsplit(':',1)[0],r['old']) not in {(s.rsplit(':',1)[0],o) for s,o in exact} and"
        name='test_reverse_ledger_rejects_same_file_883_at_new_line'
    assert source.count(needle)==1
    source=source.replace(needle,replacement)
    exec(compile(source,'<'+mode+' reverse guard>','exec'),reverse.__dict__)
elif mode=='file_token_native_collision':
    source=inspect.getsource(ledger.native_changes)
    needle='if collision in NATIVE_COLLISIONS:'
    assert source.count(needle)==1
    source=source.replace(needle,'if (name,token) in {(c[0],c[2]) for c in NATIVE_COLLISIONS}:\n                        used.update(c for c in NATIVE_COLLISIONS if (c[0],c[2])==(name,token))')
    exec(compile(source,'<file-token native collision>','exec'),ledger.__dict__)
    name='test_native_collision_rejects_same_file_21_6_at_new_line'
elif mode=='comment':
    name='test_paper_ledger_waivers_are_site_bound'
else:
    raise SystemExit('choose arch_only, token_waiver, percent_unscaled, file_token_waiver, file_token_ledger, file_token_native_collision or comment')
# Import after replacing the function, so the test's native_changes reference
# reaches the actual narrowed consumer. No repository file is modified.
from test_r13_reverse import ReverseLedgerTests
result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(ReverseLedgerTests(n) for n in (names or [name])))
raise SystemExit(0 if result.wasSuccessful() else 1)
