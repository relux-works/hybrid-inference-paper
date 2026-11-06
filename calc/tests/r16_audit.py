"""CPU-only run16 exports, frozen history and coordinate-qualified quote ledger."""
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

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calc/out/run16'
BASE='04755721'
COORDINATES=('client','link_mbit','agents','streams','depth','actual_depth','delta','profile','team','route','basis','state_format','import_variant','variant','component','kind','server','option','storage_tier','precision','scale','context')


import history_evidence as history

def read(path):
    return list(csv.DictReader(io.StringIO(path.read_text())))


def write(path,records):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(records)


def frozen():
    counts={}
    for directory,count in (('paper',150),('run13',252),('run14',110),('run15',96)):
        prefix='calc/out/'+directory
        names=history.snapshot_paths(BASE,prefix)
        assert len(names)==count,(prefix,len(names))
        assert set(names)=={str(p.relative_to(ROOT)) for p in (ROOT/prefix).rglob('*') if p.is_file()},prefix+' file set'
        for name in names:
            assert history.digest((ROOT/name).read_bytes())==history.snapshot_hash(BASE,name),name+' changed historical bytes'
        counts[prefix]=len(names)
    return counts


def changed_cells():
    records=[]
    for variant in ('base','bounded_undo'):
        for current in sorted((OUT/variant).glob('*.csv')):
            previous=ROOT/'calc/out/run15/base'/current.name
            after=read(current);before=read(previous) if previous.exists() else []
            if current.name=='parallel_anchors.csv':
                old={(r['streams'],r['depth']):(i,r) for i,r in enumerate(before)}
                new={(r['streams'],r['depth']):r for r in after}
                assert len(old)==len(before) and len(new)==len(after),'duplicate anchor coordinates'
                pairs=[(i,old.get((r['streams'],r['depth']),(-1,{}))[1],r) for i,r in enumerate(after)]
                pairs += [('r15:'+str(i),r,{}) for i,r in enumerate(before) if (r['streams'],r['depth']) not in new]
            else:
                assert not before or len(before)==len(after) or current.name in ('parallel_historical_sensitivity.csv','parallel_server_shape_sensitivity.csv'),(current.name,'row count')
                pairs=[(i if i<len(after) else 'r15:'+str(i),
                        before[i] if i<len(before) else {},after[i] if i<len(after) else {})
                       for i in range(max(len(before),len(after)))]
            for i,a,b in pairs:
                for col in sorted(set(a)|set(b)):
                    if a.get(col,'<absent>')!=b.get(col,'<absent>'):
                        records.append(dict(table=current.name,row=i,column=col,
                            coordinates='; '.join(k+'='+str(b.get(k,a.get(k,''))) for k in COORDINATES if k in a or k in b),
                            old=a.get(col,'<absent>'),new=b.get(col,'<absent>'),source="calc/out/run16/"+variant+"/"+current.name))
    return records


def cell_key(r):
    return r['table']+'[row={}].{}'.format(r['row'],r['column'])+'; '+r['coordinates']


def verify_quote_coverage(records):
    actual={(r['source'],r['engine_key'],str(r['old']),str(r['new'])) for r in records}
    cells=changed_cells()
    expected={(r['source'],cell_key(r),r['old'],r['new']) for r in cells}
    assert len(expected)==len(cells),'changed-cell key collision'
    assert not expected-actual,'unreported changed cells: '+repr(sorted(expected-actual)[:3])
    return len(expected)


def prose_quotes():
    old=ROOT/'calc/out/run15/base';new=OUT/'base';records=[]
    def derive(site,key,table,selector,formula):
        prior=[r for r in read(old/table) if selector(r)];current=[r for r in read(new/table) if selector(r)]
        assert len(prior)==len(current)==1,(key,'ambiguous quote')
        a,b=formula(prior[0]),formula(current[0])
        records.append(dict(paper_site=site,engine_key=key,old=a,new=b,source=str((new/table).relative_to(ROOT)),comparison='r15_to_r16_prose'))
        return a,b
    m3=lambda r:r['client'].startswith('M3') and float(r.get('link_mbit',1000))==1000
    a,b=derive('paper/sections/05-clients.tex:72; 14-conclusion.tex:11','M3 four-agent gain','client_sessions_day.csv',m3,lambda r:float(r['gain']))
    derive('paper/sections/05-clients.tex:64','32k four-stream aggregate','parallel_anchors.csv',
           lambda r:r['streams']=='4' and r['depth']=='32784',lambda r:float(r['aggregate_tok_s']))
    derive('paper/sections/05-clients.tex:72','512-token answer seconds at four streams','parallel_anchors.csv',
           lambda r:r['streams']=='4' and r['depth']=='32784',lambda r:512/(float(r['aggregate_tok_s'])/4))
    derive('paper/sections/05-clients.tex:65','four-stream measured share of bandwidth bound','decode_scaling.csv',
           lambda r:r['kind']=='measured' and r['streams']=='4',lambda r:float(r['aggregate_tok_s'])/float(r['bandwidth_bound_aggregate']))
    # The single anchor's physical grid changed, so compare actual32k lookups,
    # rather than silently matching a new16k row to an old32k coordinate.
    from hybridcalc.engine import load
    from hybridcalc.paper_tables import Context
    s,i=load('paper-tables-r16');c=Context(s,i)
    p=next(r for r in read(old/'parallel_anchors.csv') if r['streams']=='1' and r['depth']=='32784')
    records.append(dict(paper_site='paper/sections/05-clients.tex:65',engine_key='32k single-stream rate; interpolated in R16',old=float(p['aggregate_tok_s']),new=c.parallel.decode(1,32784),source='calc/out/run16/base/parallel_anchors.csv',comparison='r15_to_r16_prose'))
    for table,basis,key in (('person_cost_s20.csv','Mac already owned','capacity_day'),('person_cost_s20.csv','Mac already owned','hybrid_cheapest'),('person_cost_s50.csv','Mac already owned','hybrid_cheapest'),('person_cost_s50.csv','Mac premium bought','hybrid_cheapest')):
        derive('paper/sections/07-economics.tex:86','tab:econ M3 '+table+' '+basis+' '+key,table,
               lambda r,basis=basis:r['client'].startswith('M3') and r['team']=='5' and r['basis']==basis,lambda r,key=key:float(r[key]))
    own=lambda r:r['client'].startswith('M3') and r['team']=='5' and r['basis']=='Mac already owned'
    host=derive('paper/sections/04-channel.tex:127','compute_month+hosting_month','person_cost_s50.csv',own,lambda r:float(r['compute_month'])+float(r['hosting_month']))
    for key in ('served_day','hybrid_tb_month','egress_1','egress_2','egress_3'):
        values=derive('paper/sections/04-channel.tex:125-127','traffic heavy '+key,'traffic_user_month.csv',lambda r:r['profile']=='heavy',lambda r,key=key:float(r[key]))
        if key in ('egress_2','egress_3'):
            records.append(dict(paper_site='paper/sections/04-channel.tex:127',engine_key=key+'/(compute_month+hosting_month)',old=values[0]/host[0],new=values[1]/host[1],source='calc/out/run16/base/traffic_user_month.csv',comparison='r15_to_r16_prose'))
    derive('paper/sections/07-economics.tex:101','about four M3 Max; manual number-word; 2500/capacity_day','person_cost_academic_s100.csv',own,lambda r:2500/float(r['capacity_day']))
    return records


def quotes():
    cells=changed_cells();records=[]
    tex={str(p.relative_to(ROOT)):p.read_text().splitlines() for p in (ROOT/'paper').rglob('*.tex')}
    for r in cells:
        sites=['engine replacement']
        sites += [path+':'+str(n) for path,lines in tex.items() for n,line in enumerate(lines,1) if r['table'] in line]
        if (ROOT/'paper/data/engine'/r['table']).exists():sites.append('paper/data/engine/'+r['table'])
        # One cell retains every consumer site in a single field. Repeating
        # its full coordinate key per site adds no coverage and bloats custody.
        records.append(dict(paper_site='; '.join(sites),engine_key=cell_key(r),old=r['old'],new=r['new'],source=r['source'],comparison='r15_to_r16'))
    records+=prose_quotes()
    # FACTS' same-build background step40 is a historical A/B quote source,
    # separate from accepted R15. Never admit these rates as canonical data.
    old_rates=((175.1,149.0,159.8,143.1,7.85),(81.5,75.8,89.0,57.7,6.59),
               (47.3,37.8,45.8,40.4,5.52),(38.6,37.8,41.9,39.5,5.16),
               (27.1,27.2,28.5,24.5,5.34),(22.3,21.0,26.2,21.0,5.27))
    from hybridcalc.measurements_r16 import SingleStream,DEPTHS,DELTAS
    single=SingleStream()
    for depth,values in zip(DEPTHS,old_rates):
        segment=next(r for r in single.records if r['kind']=='segment' and r['level']==depth)
        pairs=[('segment prefill',values[0],segment['prompt_n']*1000/segment['prompt_ms'])]
        pairs += [('delta'+str(n)+' prefill',v,single.for_delta(depth,n)) for n,v in zip(DELTAS,values[1:4])]
        pairs.append(('single decode mean',values[4],dict(single.decode_points)[depth]))
        for key,old,new in pairs:
            records.append(dict(paper_site='FACTS-261103.md section2 PRIORITY A/B; historical background throttled step40',
                engine_key=key+'; depth='+str(depth),old=old,new=new,source='calc/out/run16/base/m3_pri31_depth.csv',comparison='background_dde879bc_to_pri31'))
    write(ROOT/'calc/ENGINE-QUOTES-R16-261103.csv',records)
    return len(records)


def accepted_generator_identity():
    # Accepted R16 exports stay frozen while later opt-in sources evolve.
    accepted='e51942d3'
    paths=history.snapshot_paths(accepted,'hybridcalc.py','calc/hybridcalc')
    paths=[p for p in paths if p.endswith('.py') or p.startswith('calc/hybridcalc/data/') and p.endswith('.json')]
    return {p:hashlib.sha256(history.snapshot_object(accepted+':'+p)).hexdigest() for p in paths}


def accepted_config():
    return json.loads(history.snapshot_object('e51942d3:calc/hybridcalc/data/run16-measurements.json'))


def verify_tables():
    identity=accepted_generator_identity()
    files=set()
    for variant in ('base','bounded_undo'):
        suffix='-bounded-undo' if variant=='bounded_undo' else ''
        for name,_ in CASES:
            scenario=name+'-r16'+suffix
            manifests=[p for p in (OUT/variant).glob('*manifest.json') if json.loads(p.read_text())['scenario']==scenario]
            assert len(manifests)==1,(scenario,'missing manifest')
            m=json.loads(manifests[0].read_text());assert m['generator']==identity,scenario+' stale generator'
            for name,digest in m['files'].items():
                assert hashlib.sha256((OUT/variant/name).read_bytes()).hexdigest()==digest,(variant,name)
                files.add(variant+'/'+name)
            files.add(str(manifests[0].relative_to(OUT)))
    assert files=={str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file() and p.name!='INDEX.json'},'new file set mismatch'
    return len(files)


def verify_qualification():
    interim=accepted_config()['m3_parallel']['background_priority_interim']
    count=0
    for variant in ('base','bounded_undo'):
        for p in (OUT/variant).glob('*.csv'):
            for r in read(p):
                assert 'background_priority_interim' in r and 'capacity_status' in r,(str(p),'missing priority qualifier')
                if p.name in ('client_agents_day.csv','client_sessions_day.csv'):
                    assert r['background_priority_interim']==str(interim),(str(p),'wrong interim qualifier')
                    if interim:assert r['capacity_status'].startswith('interim;'),(str(p),'falsely final capacity')
                count+=1
    assert count>0,'no qualified output rows'
    return count


def main():
    assert sys.argv[1:] in ([],['--audit-only'])
    print('frozen before',frozen(),flush=True)
    if not sys.argv[1:]:
        for variant in ('base','bounded_undo'):
            suffix='-bounded-undo' if variant=='bounded_undo' else ''
            for name,_ in CASES:
                scenario=name+'-r16'+suffix
                m=write_tables(run(scenario),OUT/variant)
                print(scenario,len(m['tables']),'tables',m['alarm_cells'],'explicit alarm cells',flush=True)
    print('verified files',verify_tables(),flush=True)
    print('qualified rows',verify_qualification(),flush=True)
    print('quote rows',quotes(),flush=True)
    print('changed-cell coverage',verify_quote_coverage(read(ROOT/'calc/ENGINE-QUOTES-R16-261103.csv')),flush=True)
    index=dict(baseline=BASE,generator=generator_identity(),frozen=frozen(),
        files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='INDEX.json'})
    (OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print('frozen after',index['frozen'],flush=True)


if __name__=='__main__':main()
