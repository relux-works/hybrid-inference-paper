#!/usr/bin/env python3
"""Bind intentional paper changes; never authorize drift in engine computation."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'calc'));import history_evidence as h
BASE='04c3e8de';PARENTS=('ca7f228acd789380bf46016fd87acc33e1b07aef','ec28e37c')
MUTABLE={'calc/README.md','CHANGELOG.md','README.md','UNRESOLVED_QUESTIONS.md','paper/abstract.en.txt','paper/data/offload_bound.py','paper/data/check_ranges.py'}|{'paper/sections/'+n for n in ('00-abstract.tex','01-introduction.tex','02-workload.tex','04-channel.tex','06-server.tex','07-economics.tex','08-million.tex','11-limitations.tex','13-outlook.tex','14-conclusion.tex','90-appendix.tex','91-calculation-history.tex')}
rows={};basis=h.manifest()['revisions'][h.revision(BASE)]['files']
for parent in PARENTS:
 out={}
 for name in h.snapshot_paths(parent):
  old=h.snapshot_hash(parent,name)
  if name=='MANIFEST.sha256':continue
  live=h.digest(h.payload(ROOT/name))
  if name in h.port_hashes():
   assert live==h.port_hashes()[name],('unapproved adapter',name);continue
  if live==old:continue
  accepted=basis[name]['sha256']
  # N7 only changes canonical quote-path presentation; every audit assertion stays exact.
  audit_path_only=False
  if name=='calc/tests/r16_audit.py':
   prior=h.snapshot_object(BASE+':'+name)
   old_pattern=b'source=str(current.relative_to(ROOT))'
   assert prior.count(old_pattern)==1,'ambiguous run16 audit path migration'
   audit_path_only=live==h.digest(prior.replace(old_pattern,b'source="calc/out/run16/"+variant+"/"+current.name',1))
  assert live==accepted or name in MUTABLE or audit_path_only,('unreviewed nonpaper parent drift',name)
  out[name]={'original_sha256':old,'accepted_paper_sha256':accepted,'current_sha256':live,'basis':'Exact run16 canonical quote-path presentation; all audit assertions unchanged'if audit_path_only else('Existing accepted paper divergence'if live==accepted else'Explicit current paper/docs rewrite, bound by publication/checker gates')}
 rows[h.revision(parent)]=out
p=ROOT/'calc/tests/data/history-evidence/engine-parent-migrations.json';raw=(json.dumps({'accepted_paper_baseline':h.revision(BASE),'revisions':rows,'manifest_rule':'Original manifest authenticated in history; current manifest must enumerate and hash every tracked file except itself.'},indent=2)+'\n').encode();p.write_bytes(raw)
p=ROOT/'calc/history_evidence.py';p.write_text(re.sub(r"ENGINE_PARENT_MIGRATIONS_SHA256='[^']*'","ENGINE_PARENT_MIGRATIONS_SHA256='"+hashlib.sha256(raw).hexdigest()+"'",p.read_text()))
print('Explicit parent migrations', {k:len(v)for k,v in rows.items()})
