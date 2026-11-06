"""Finite inventory gate for direct Git provenance access outside evidence mode."""
from pathlib import Path
import ast,hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'calc/tests/data/public-git-catalog.json'
CATALOG_SHA256='0724e94b5b5900648d4297f47a48e7a100e931780fcd8446d21563005b8d1cb2'
SCOPES=('calc/tests','calc/hybridcalc','calc/run22','calc/run23','calc/run24','calc/run25','calc/run26','paper/data','bench/tests')


def sources():
    result={str(p.relative_to(ROOT)):p.read_text()for folder in SCOPES for p in (ROOT/folder).glob('*.py')}
    result['calc/history_evidence.py']=(ROOT/'calc/history_evidence.py').read_text()
    result.update({str(p.relative_to(ROOT)):p.read_text()for p in (ROOT/'.scripts').glob('*')if p.suffix in ('.py','.sh')})
    return result

def git_calls(text):
    tree=ast.parse(text);result=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call):continue
        name=node.func.id if isinstance(node.func,ast.Name)else node.func.attr if isinstance(node.func,ast.Attribute)else ''
        wrapper=isinstance(node.func,ast.Name)and name in ('git','local_git','_git')
        process=isinstance(node.func,ast.Attribute)and isinstance(node.func.value,ast.Name)and node.func.value.id=='subprocess'
        if not(wrapper or process and any(isinstance(n,ast.Constant)and n.value=='git'for n in ast.walk(node))):continue
        result.append((node.lineno,ast.get_source_segment(text,node)or'',node))
    return result

def violations(documents=None,catalog=None):
    if catalog is None:
        raw=CATALOG.read_bytes();assert hashlib.sha256(raw).hexdigest()==CATALOG_SHA256,'Git catalogue SHA256 mismatch';catalog=json.loads(raw)['files']
    errors=[]
    for name,text in (documents if documents is not None else sources()).items():
        calls=git_calls(text)if name.endswith('.py')else[(i,line,None)for i,line in enumerate(text.splitlines(),1)if re.search(r'\bgit\s',line)and not line.lstrip().startswith('#')]
        if not calls:
            if name in catalog and catalog[name]['sha256']!=hashlib.sha256(text.encode()).hexdigest():errors.append({'file':name,'line':1,'kind':'changed reviewed metadata builder'})
            continue
        # The reviewed evidence gateway resolves private objects only to verify
        # pinned fixtures. Every other direct access has a public/fixture role.
        gateway=name in ('calc/history_evidence.py','.scripts/generate-history-evidence.py','.scripts/generate-ledger-storage.py')
        for line,call,node in calls:
            if not gateway and re.search(r'(?<![0-9a-f])[0-9a-f]{7,40}(?=:|[\'\"])(?![0-9a-f])',call):
                errors.append({'file':name,'line':line,'kind':'private revision outside evidence gateway','call':call})
        pin=catalog.get(name)
        if not pin or pin['sha256']!=hashlib.sha256(text.encode()).hexdigest():errors.append({'file':name,'line':calls[0][0],'kind':'unreviewed Git access outside declared public/evidence inventory'})
    return errors

if __name__=='__main__':
    found=violations()
    for row in found:print(json.dumps(row))
    print('public-history guard: '+str(len(found))+' violations')
    raise SystemExit(bool(found))
