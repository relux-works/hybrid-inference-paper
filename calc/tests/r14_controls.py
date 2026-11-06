"""Process-only narrowing faults; each must fail a named publication test."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r14_publication as p
from test_r14_publication import PublicationContracts
from test_r15_sentences import SentenceContracts
import r15_sentences as sentences

mode=sys.argv[1];patches=[]
names={
    'omit_api_scope':'test_r5x_repeat_api_scope_refuses_missing_counts_with_price_control',
    'hide_windows':'test_r5x_partial_availability_refuses_hidden_novita_cloudflare_windows',
    'native_bridge':'test_native_llama_duplicate_bridge_rows_cannot_claim_a_measured_effect',
    'admit_5090':'test_paper_exports_refuse_5090_server_with_pro_b300_positive_controls',
    'numeric_change':'test_label_only_diff_refuses_a_numeric_change_and_accepts_new_labels',
    'missing_basis':'test_paper_projection_refuses_empty_or_unscoped_costs',
    'drop_quote':'test_paper_quote_ledger_refuses_a_missing_cell_with_full_control',
    'infer_missing_link':'test_words_ready_missing_link_refuses_implicit_office_with_positive_control',
}
if mode=='control':suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(c)for c in(PublicationContracts,SentenceContracts)])
else:
    assert mode in names,'unknown control'
    if mode in('omit_api_scope','native_bridge','hide_windows','drop_quote'):
        old=p.read
        def changed(path):
            rows=old(path)
            if mode=='omit_api_scope'and path.name=='api_admission.csv':rows[0]['workload_scope']=''
            if mode=='hide_windows'and path.name=='api_admission.csv':
                for row in rows:row['availability_basis']='minimum of every recorded window'
            if mode=='native_bridge'and path.name in('server_prefill.csv','engine_sensitivity.csv'):
                for row in rows:
                    if row['engine']=='llama_cpp':row['basis']=row['basis'].replace('; '+p.LLAMA,'')
            if mode=='drop_quote'and path.name.startswith('ENGINE-QUOTES-R')and'-PAPER-'in path.name:rows=rows[:-1]
            return rows
        patches.append(patch.object(p,'read',side_effect=changed))
    elif mode=='admit_5090':patches.append(patch.object(p,'SERVERS',p.SERVERS|{'rtx5090'}))
    elif mode=='numeric_change':patches.append(patch.object(p,'ALLOWED',p.ALLOWED|{'effective_usd_per_1000_calls'}))
    elif mode=='missing_basis':
        old=p.require_paper
        patches.append(patch.object(p,'require_paper',side_effect=lambda rows:old([dict(r,cost_basis='dedicated',workload_scope='fixture')for r in rows])))
    elif mode=='infer_missing_link':
        original=sentences.condition_field
        def inferred(text,name):
            if name=='link'and'; link='not in text:
                billing=original(text,'billing')
                return next(value[1]for value in sentences.LINKS.values()if value[0]==billing)
            return original(text,name)
        patches.append(patch.object(sentences,'condition_field',side_effect=inferred))
    suite=unittest.TestSuite([(SentenceContracts if mode=='infer_missing_link'else PublicationContracts)(names[mode])])
for item in patches:item.start()
result=unittest.TextTestRunner(verbosity=2).run(suite)
for item in reversed(patches):item.stop()
raise SystemExit(not result.wasSuccessful())
