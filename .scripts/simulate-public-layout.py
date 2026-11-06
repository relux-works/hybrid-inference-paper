#!/usr/bin/env python3
"""Create real public-only Git metadata reusing the existing physical worktree."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
PUBLIC='386a053be934b2ba362a1296d4b5e34bff70ac3c'
def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--tree');args=p.parse_args();dest=args.directory.resolve();dest.mkdir(exist_ok=False);meta=dest/'repo.git';real=shutil.which('git');assert real
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_TERMINAL_PROMPT='0')
 for key in ('GIT_DIR','GIT_WORK_TREE','GIT_COMMON_DIR','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'):env.pop(key,None)
 records=[]
 def run(argv,*,data=None,metadata=False):
  command=[real,*(('--git-dir='+str(meta),'--work-tree='+str(ROOT))if metadata else()),*argv]
  r=subprocess.run(command,cwd=ROOT,env=env,input=data,capture_output=True);records.append({'argv':command,'exit_code':r.returncode});assert r.returncode==0,(command,r.stderr.decode());return r.stdout
 run(['init','--bare','-q',str(meta)])
 tree=args.tree or run(['write-tree']).decode().strip()
 public_commits=run(['rev-list',PUBLIC]).decode().splitlines();trees=set()
 for commit in public_commits:
  trees.add(run(['rev-parse',commit+'^{tree}']).decode().strip())
  for row in run(['ls-tree','-rt',commit]).decode().splitlines():
   fields=row.split();
   if fields[1]=='tree':trees.add(fields[2])
 trees.add(tree)
 for row in run(['ls-tree','-rt',tree]).decode().splitlines():
  fields=row.split()
  if fields[1]=='tree':trees.add(fields[2])
 copied_bytes=0
 for kind,oids in (('commit',public_commits),('tree',sorted(trees))):
  for oid in oids:
   raw=run(['cat-file',kind,oid]);copied_bytes+=len(raw);new=run(['hash-object','-t',kind,'-w','--stdin'],data=raw,metadata=True).decode().strip();assert new==oid
 standin=run(['-c','user.name=Public layout fixture','-c','user.email=public-layout@example.invalid','-c','commit.gpgsign=false','commit-tree',tree,'-p',PUBLIC],data=b'Unsigned public one-commit stand-in for portability tests\n',metadata=True).decode().strip()
 run(['update-ref','refs/heads/main',standin],metadata=True);run(['update-ref','refs/remotes/origin/main',PUBLIC],metadata=True);run(['symbolic-ref','HEAD','refs/heads/main'],metadata=True)
 run(['read-tree',standin],metadata=True);run(['update-index','--refresh'],metadata=True)
 assert not (meta/'objects/info/alternates').exists()
 (dest/'bin').mkdir();shim=dest/'bin/git'
 code='''#!/usr/bin/env python3
import os,sys
from pathlib import Path
REAL=__REAL__;ROOT=Path(__ROOT__);META=__META__
a=sys.argv[1:];cwd=Path.cwd();i=0;explicit=bool(os.environ.get('GIT_DIR'))
while i<len(a) and a[i].startswith('-'):
 flag=a[i]
 if flag=='-C':cwd=(cwd/a[i+1]).resolve();i+=2
 elif flag in ('-c','--git-dir','--work-tree'):
  explicit=explicit or flag=='--git-dir';i+=2
 elif flag.startswith('--git-dir='):explicit=True;i+=1
 else:i+=1
operation=a[i]if i<len(a)else''
closest=None
for here in (cwd,*cwd.parents):
 if (here/'.git').exists():closest=here.resolve();break
route=not explicit and closest==ROOT and operation not in ('init','clone')
os.execv(REAL,[REAL,*(['--git-dir='+META,'--work-tree='+str(ROOT)]if route else[]),*a])
'''.replace('__REAL__',repr(real)).replace('__ROOT__',repr(str(ROOT))).replace('__META__',repr(str(meta)))
 shim.write_text(code);shim.chmod(0o755)
 record={'public_base':PUBLIC,'standin_commit':standin,'tree':tree,'metadata_git_dir':str(meta),'physical_worktree':str(ROOT),'environment':{'PATH':str(dest/'bin')+os.pathsep+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':os.environ.get('TMPDIR','')},'copied_public_commits':public_commits,'copied_trees':len(trees),'copied_blob_objects':0,'copied_metadata_raw_bytes':copied_bytes,'no_alternates':True,'extra_checkout':False,'commands':records}
 (dest/'environment.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items()if k not in ('commands','environment')},indent=2))
if __name__=='__main__':main()
