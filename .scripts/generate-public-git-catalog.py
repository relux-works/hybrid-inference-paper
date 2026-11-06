from pathlib import Path
import hashlib,importlib.util,json,re,sys
import argparse
root=Path(__file__).resolve().parents[1];sys.path[:0]=[str(root/'calc'),str(root/'calc/tests')]
import public_history_guard as guard
files={};rows=[]
for name,text in sorted(guard.sources().items()):
 calls=guard.git_calls(text)if name.endswith('.py')else[(i,t,None)for i,t in enumerate(text.splitlines(),1)if re.search(r'\bgit\s',t)and not t.lstrip().startswith('#')]
 if not calls and name!='.scripts/simulate-public-layout.py':continue
 if name in ('calc/history_evidence.py','.scripts/generate-history-evidence.py'):reason='verified evidence gateway; private object reads only cross-check pinned in-tree evidence'
 elif name in ('calc/hybridcalc/history.py','calc/tests/test_run10.py'):reason='explicit local/temporary Git fixture and existing public snapshot mode; no private producer revision'
 elif name=='calc/tests/publication_v2.py':reason='tracked working-tree file enumeration only, no revision lookup'
 elif name=='.scripts/simulate-public-layout.py':reason='isolated real Git metadata: only public ancestor commits and current trees; no private producer objects'
 elif name.startswith('.scripts/'):reason='HEAD/public release refs, or isolated synthetic release fixture'
 else:reason='MANUAL REVIEW REQUIRED'
 assert reason!='MANUAL REVIEW REQUIRED',(name,[(n,c)for n,c,_ in calls])
 files[name]={'sha256':hashlib.sha256(text.encode()).hexdigest(),'reason':reason}
 for line,call,_ in calls:rows.append({'file':name,'line':line,'classification':'evidence gateway'if name in ('calc/history_evidence.py','.scripts/generate-history-evidence.py')else'public-safe','reason':reason,'call':call})
raw=(json.dumps({'schema':1,'scope':'explicitly reviewed Git-bearing modules; unknown or changed Git access fails closed','files':files},indent=2)+'\n').encode();p=guard.CATALOG;p.write_bytes(raw)
p=root/'calc/tests/public_history_guard.py';s=p.read_text();s=re.sub(r"CATALOG_SHA256='[^']+'",f"CATALOG_SHA256='{hashlib.sha256(raw).hexdigest()}'",s);p.write_text(s)
print(json.dumps({'reviewed_git_modules':len(files),'sites':rows},indent=2))
