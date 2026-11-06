"""CPU-only R15 exports, immutable previous runs and complete changed-cell ledger."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc.engine import run
from hybridcalc.export import generator_identity, write_tables
from r11_audit import CASES

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'calc/out/run15'
BASE = '2d457aed87d415043a2c0566f7a185607f11487e'


from history_fixtures import snapshot_files


import history_evidence as history

def frozen():
    counts = {}
    for directory, expected in (('calc/out/paper',150),('calc/out/run13',252),('calc/out/run14',110)):
        files = snapshot_files('r14-producer' if directory == 'calc/out/run14' else 'r13-exports', directory)
        names = sorted(files)
        assert len(names) == expected, (directory,len(names))
        assert set(names) == {str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file()}
        for name in names:
            assert (ROOT/name).read_bytes() == files[name], name
        counts[directory] = len(names)
    return counts


def read(path):
    return list(csv.DictReader(io.StringIO(path.read_text())))


def write(path, records):
    with path.open('w',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(records[0]),lineterminator='\n')
        writer.writeheader(); writer.writerows(records)


def changed_cells():
    records = []
    for previous in sorted((ROOT/'calc/out/run14/base').glob('*.csv')):
        current = OUT/'base'/previous.name
        if not current.exists():
            raise AssertionError('missing R15 counterpart: '+previous.name)
        before, after = read(previous), read(current)
        # The anchor grid intentionally changed; compare by physical coordinate.
        if previous.name == 'parallel_anchors.csv':
            old = {(r['streams'],r['depth']):r for r in before}
            assert len(old)==len(before), 'duplicate R14 anchor coordinates'
            paired = [(i,old.get((b['streams'],b['depth']),{}),b) for i,b in enumerate(after)]
            new_keys = {(b['streams'],b['depth']) for b in after}
            assert len(new_keys)==len(after), 'duplicate R15 anchor coordinates'
            # Removed rows retain their original R14 index in a separate
            # namespace, so neither each other nor current R15 rows collide.
            paired += [('r14:'+str(i),a,{}) for i,a in enumerate(before)
                       if (a['streams'],a['depth']) not in new_keys]
        else:
            assert len(before)==len(after), (previous.name,'row coordinates changed')
            paired = [(i,a,b) for i,(a,b) in enumerate(zip(before,after))]
        for i,a,b in paired:
            for column in sorted(set(a)|set(b)):
                if a.get(column,'<absent>') != b.get(column,'<absent>'):
                    records.append(dict(table=previous.name,row=i,column=column,
                        coordinates='; '.join(k+'='+str(b.get(k,a.get(k,''))) for k in ('client','link_mbit','agents','streams','depth','profile','team','route','basis','state_format') if k in a or k in b),
                        old=a.get(column,'<absent>'),new=b.get(column,'<absent>'),
                        source=str(current.relative_to(ROOT))))
    return records


def cell_key(cell):
    return cell['table']+'[row={}].{}'.format(cell['row'],cell['column'])+'; '+cell['coordinates']


def quotes():
    records = []
    sections = {str(p.relative_to(ROOT)):p.read_text().splitlines() for p in (ROOT/'paper').rglob('*.tex')}
    for cell in changed_cells():
        name,i,column = cell['table'],cell['row'],cell['column']
        key=cell_key(cell)
        embedded=ROOT/'paper/data/engine'/name
        paper_rows=read(embedded) if embedded.exists() else []
        if name=='parallel_anchors.csv':
            # The embedded paper has a different grid; match physical
            # coordinates, never a current/expired export's positional index.
            coordinates=dict(part.split('=',1) for part in cell['coordinates'].split('; '))
            paper_row=next((r for r in paper_rows if all(r.get(k)==v for k,v in coordinates.items())),{})
            paper_value=paper_row.get(column,'')
        else:
            paper_value=paper_rows[i].get(column,'') if 0<=i<len(paper_rows) else ''
        sites=['paper/data/engine/'+key]
        sites += [path+':'+str(line_no) for path,lines in sections.items()
                  for line_no,line in enumerate(lines,1) if name in line]
        printed_sites={
            'client_sessions_day.csv':'05-clients.tex :: tab:clients',
            'turn_speedup.csv':'04-channel.tex :: tab:turn',
            'oneshot_ingest.csv':'04-channel.tex :: tab:oneshot',
            'transcript_example.csv':'04-channel.tex :: tab:transcript',
            'traffic_user_month.csv':'04-channel.tex:123-128 :: traffic costs',
            'person_cost_s20.csv':'07-economics.tex :: tab:econ',
            'person_cost_s50.csv':'07-economics.tex :: tab:econ',
        }
        if name in printed_sites:sites.append('paper/sections/'+printed_sites[name])
        for site in sites:
            records.append(dict(paper_site=site,engine_key=key,old=cell['old'],new=cell['new'],
                                paper_current=paper_value,source=cell['source'],comparison='r14_to_r15'))
    # Handwritten numbers are not CSV consumers. Bind the affected prose to
    # exact sites and formulas, including already-stale paper text.
    clients=read(OUT/'base/client_sessions_day.csv')
    old_clients=read(ROOT/'calc/out/run14/base/client_sessions_day.csv')
    m3=lambda rs:next(r for r in rs if r['client'].startswith('M3 Max') and float(r['link_mbit'])==1000)
    a,b=m3(old_clients),m3(clients)
    anchors=read(OUT/'base/parallel_anchors.csv')
    anchor=lambda k:next(float(r['aggregate_tok_s']) for r in anchors if r['streams']==str(k) and r['depth']=='32784')
    old_anchor=read(ROOT/'calc/out/run14/base/parallel_anchors.csv')
    old32=lambda k:next(float(r['aggregate_tok_s']) for r in old_anchor if r['streams']==str(k) and float(r['depth'])<40000)
    prose=[('05-clients.tex',64,'32k four-stream timed aggregate',old32(4),anchor(4),'14.05'),
           ('05-clients.tex',65,'32k single-stream timed rate',old32(1),anchor(1),'8.44'),
           ('05-clients.tex',72,'512-token answer seconds at four streams',512/(old32(4)/4),512/(anchor(4)/4),'about two and a half minutes'),
           ('05-clients.tex',72,'M3 four-agent gain',a['gain'],b['gain'],'1.6'),
           ('05-clients.tex',65,'four-stream measured share of bandwidth bound',None,None,'about20%')]
    for file,line,key,old,new,printed in prose:
        if old is None:
            prior=read(ROOT/'calc/out/run14/base/decode_scaling.csv');current=read(OUT/'base/decode_scaling.csv')
            pick=lambda rs:next(r for r in rs if r['kind']=='measured' and r['streams']=='4')
            x,y=pick(prior),pick(current)
            old=float(x['aggregate_tok_s'])/float(x['bandwidth_bound_aggregate']);new=float(y['aggregate_tok_s'])/float(y['bandwidth_bound_aggregate'])
        records.append(dict(paper_site='paper/sections/'+file+':'+str(line),engine_key=key,old=old,new=new,
                            paper_current=printed,source='calc/out/run15/base/',comparison='r14_to_r15_prose'))
    records.append(dict(paper_site='paper/sections/14-conclusion.tex:11',engine_key='M3 four-agent gain',
                        old=a['gain'],new=b['gain'],paper_current='1.6',
                        source='calc/out/run15/base/client_sessions_day.csv',comparison='r14_to_r15_prose'))
    def derived(site,key,table,select,formula,printed):
        before=[r for r in read(ROOT/'calc/out/run14/base'/table) if select(r)]
        after=[r for r in read(OUT/'base'/table) if select(r)]
        assert len(before)==len(after)==1, (key,'ambiguous paper quote')
        old,new=formula(before[0]),formula(after[0])
        records.append(dict(paper_site=site,engine_key=key,old=old,new=new,paper_current=printed,
                            source='calc/out/run15/base/'+table,comparison='r14_to_r15_prose'))
        return old,new
    m3_owned=lambda r:r['client'].startswith('M3') and r['basis']=='Mac already owned' and r['team']=='5'
    host=derived('paper/sections/04-channel.tex:127','M3 s50 compute_month+hosting_month','person_cost_s50.csv',
                 m3_owned,lambda r:float(r['compute_month'])+float(r['hosting_month']),'about USD15')
    for key,line,printed in (('served_day',125,'about620'),('hybrid_tb_month',125,'about1.7'),
                             ('egress_1',125,'8'),('egress_2',126,'84'),('egress_3',127,'152')):
        derived('paper/sections/04-channel.tex:'+str(line),'traffic heavy '+key,'traffic_user_month.csv',
                lambda r:r['profile']=='heavy',lambda r:float(r[key]),printed)
    for key in ('egress_2','egress_3'):
        old=next(r for r in read(ROOT/'calc/out/run14/base/traffic_user_month.csv') if r['profile']=='heavy')
        new=next(r for r in read(OUT/'base/traffic_user_month.csv') if r['profile']=='heavy')
        records.append(dict(paper_site='paper/sections/04-channel.tex:127',engine_key='traffic '+key+'/(compute_month+hosting_month)',
                            old=float(old[key])/host[0],new=float(new[key])/host[1],paper_current='6--10',
                            source='calc/out/run15/base/traffic_user_month.csv + person_cost_s50.csv',comparison='r14_to_r15_prose'))
    for table,basis,key,printed in (('person_cost_s20.csv','Mac already owned','capacity_day','616'),
                                  ('person_cost_s20.csv','Mac already owned','hybrid_cheapest','27.3'),
                                  ('person_cost_s50.csv','Mac already owned','hybrid_cheapest','48.6'),
                                  ('person_cost_s50.csv','Mac premium bought','hybrid_cheapest','96.1')):
        derived('paper/sections/07-economics.tex:86','tab:econ M3 '+table+' '+basis+' '+key,table,
                lambda r:r['client'].startswith('M3') and r['team']=='5' and r['basis']==basis,lambda r:float(r[key]),printed)
    derived('paper/sections/07-economics.tex:101','2500/M3 capacity_day','person_cost_academic_s100.csv',
            m3_owned,lambda r:2500/float(r['capacity_day']),'about four M3 Max (manual number-word)')
    write(ROOT/'calc/ENGINE-QUOTES-R15-261102.csv',records)
    return len(records)


def verify_quote_coverage(records):
    actual={(r['source'],r['engine_key'],str(r['old']),str(r['new'])) for r in records}
    cells=changed_cells()
    expected={(r['source'],cell_key(r),r['old'],r['new']) for r in cells}
    assert len(expected)==len(cells), 'changed-cell key collision'
    missing=expected-actual
    assert not missing, 'unreported changed cells: '+repr(sorted(missing)[:3])
    return len(expected)


def verify_tables():
    # R15 is immutable after acceptance. Bind its generator to the reviewed
    # source tree, independently of the manifest and later opt-in scenarios.
    accepted='04755721'
    paths=history.snapshot_paths(accepted,'hybridcalc.py','calc/hybridcalc')
    paths=[p for p in paths if p.endswith('.py') or p.startswith('calc/hybridcalc/data/') and p.endswith('.json')]
    identity={p:hashlib.sha256(history.snapshot_object(accepted+':'+p)).hexdigest() for p in paths}
    files=set()
    for name,_ in CASES:
        scenario=name+'-r15'
        manifests=[p for p in (OUT/'base').glob('*_manifest.json') if json.loads(p.read_text())['scenario']==scenario]
        assert len(manifests)==1, (scenario,'missing or duplicate manifest')
        manifest=json.loads(manifests[0].read_text())
        assert manifest['generator']==identity, scenario+' stale generator'
        for path,digest in manifest['files'].items():
            assert hashlib.sha256((OUT/'base'/path).read_bytes()).hexdigest()==digest, path
            files.add(path)
        files.add(manifests[0].name)
    assert files=={p.name for p in (OUT/'base').iterdir() if p.is_file()}, 'unexpected or missing export file'
    return len(files)


def main():
    print('frozen before',frozen(),flush=True)
    assert sys.argv[1:] in ([],['--audit-only']), 'usage: r15_audit.py [--audit-only]'
    if not sys.argv[1:]:
        for name,_ in CASES:
            scenario=name+'-r15'
            manifest=write_tables(run(scenario),OUT/'base')
            print(scenario,len(manifest['tables']),'tables',manifest['alarm_cells'],'explicit alarm cells',flush=True)
    print('verified export files',verify_tables(),flush=True)
    print('quote rows',quotes(),flush=True)
    print('changed-cell coverage',verify_quote_coverage(read(ROOT/'calc/ENGINE-QUOTES-R15-261102.csv')),flush=True)
    index=dict(baseline=BASE,generator=generator_identity(),frozen=frozen(),
               files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='INDEX.json'})
    (OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print('frozen after',index['frozen'],flush=True)


if __name__=='__main__':main()
