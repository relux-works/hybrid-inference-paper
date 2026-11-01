"""Offline run-10 -> run-11 full publication-cell and quoted-claim audit (Python + local Git)."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load
from hybridcalc.export import generator_identity

ROOT=Path(__file__).resolve().parents[2]
BASELINE='1e8f897c4f82092c632507b520515cefa7eecab5'
PUBLISHED=ROOT/'calc/out/paper'
CASES=[('paper-tables',''),('paper-tables-conservative','conservative_'),
       ('paper-tables-r6','r6_'),('paper-tables-r6-conservative','r6_conservative_'),
       ('paper-tables-r7','r7_'),('paper-tables-r7-conservative','r7_conservative_'),
       ('paper-tables-r8','r8_'),('paper-tables-r8-conservative','r8_conservative_')]


OLD={}


def old_bytes(name):
    # Signed run 10 from local git history when present, else from the recorded archive (see r10_controls).
    if not OLD:
        from r10_controls import revision_csv
        OLD.update(revision_csv(BASELINE))
    return OLD[name]


def read_rows(data):
    return list(csv.DictReader(io.StringIO(data.decode())))


def number(value):
    try:return float(value)
    except (ValueError,TypeError):return None


def write_csv(path,rows,columns):
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns,lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def audit():
    expected=set();files={};identity=generator_identity()
    for scenario,prefix in CASES:
        manifest=json.loads((PUBLISHED/(prefix+'manifest.json')).read_text())
        assert manifest['scenario']==scenario
        assert manifest['generator']==identity,scenario+' generator identity'
        for name,sha in manifest['files'].items():
            assert hashlib.sha256((PUBLISHED/name).read_bytes()).hexdigest()==sha,name
        expected.update(manifest['tables'].values())
    assert expected=={p.name for p in PUBLISHED.glob('*.csv')}
    assert len(expected)==42
    ledger=[];summary=[]
    coordinates=('team','profile','route','client','basis','server','option','share','state_bits',
                 'state_format','depth','context','portion','portion_tokens','link_mbit',
                 'users_per_studio','demand_mode','reasoning_extra_fraction')
    for name in sorted(expected):
        prior=name.replace('reasoning_on_top_sensitivity','output_only_sensitivity')
        before=read_rows(old_bytes(prior));after=read_rows((PUBLISHED/name).read_bytes())
        assert len(before)==len(after),(name,len(before),len(after))
        changed=numeric=0
        for index,(a,b) in enumerate(zip(before,after)):
            for key in coordinates:
                if key in a:assert a[key]==b[key],(name,index,key)
            for column in sorted(set(a)|set(b)):
                x,y=a.get(column,'<absent>'),b.get(column,'<absent>')
                is_numeric=number(x) is not None or number(y) is not None
                numeric+=int(is_numeric)
                changed+=int(x!=y)
                # Every numeric cell, even unchanged or an explicit nan alarm, plus all changed text/labels.
                if is_numeric or x!=y:
                    ledger.append(dict(csv=name,policy='conservative' if name.endswith('_conservative.csv') else 'default',
                                       row=index,column=column,r10=x,r11=y,change='unchanged' if x==y else 'added' if x=='<absent>' else 'changed'))
        files[name]=(before,after)
        summary.append(dict(csv=name,rows=len(after),numeric_cells=numeric,changed_cells=changed,
                            r10_sha256=hashlib.sha256(old_bytes(prior)).hexdigest(),
                            r11_sha256=hashlib.sha256((PUBLISHED/name).read_bytes()).hexdigest()))
    # Both old sensitivity numeric cases remain exact; the fraction0 rows now equal the published base.
    for suffix in ('','_conservative'):
        prior,current=files['reasoning_on_top_sensitivity'+suffix+'.csv']
        for a,b in zip(prior,current):
            assert all(b[k]==v for k,v in a.items()),'old sensitivity number changed'
            assert b['accounting_case']==('base_output' if b['reasoning_extra_fraction']=='0' else 'reasoning_on_top_upper_bound')
            if b['reasoning_extra_fraction']=='0':
                source='person_cost_s'+str(round(float(b['share'])*100))+suffix+'.csv'
                base=next(r for r in files[source][1] if r['team']=='50' and r['client']==b['client'] and r['basis']==b['basis'])
                assert all(b[k]==v for k,v in base.items()),'fraction0 does not equal new base'
    write_csv(ROOT/'calc/ENGINE-CHANGES-R11-261101.csv',ledger,
              ['csv','policy','row','column','r10','r11','change'])
    write_csv(ROOT/'calc/ENGINE-DIFF-R11-261101.csv',summary,
              ['csv','rows','numeric_cells','changed_cells','r10_sha256','r11_sha256'])
    return files,summary


def quotes(files):
    rows=[]
    def add(policy,category,coordinates,metric,old,new,unit,source):
        rows.append(dict(policy=policy,category=category,coordinates=coordinates,metric=metric,
                         r10=old,r11=new,unit=unit,source=source))
    _,inputs=load('paper-tables')
    chunk=inputs.get('workload.chunk_calls')
    clients={inputs.locate('hardware.clients.'+key+'.label'):key for key in
             ('m3max','m4max','m5max64','m5max','ultra96','ultra256')}
    for policy,suffix in [('default',''),('conservative','_conservative')]:
        for share in ('s20','s50'):
            name='person_cost_'+share+suffix+'.csv';before,after=files[name]
            pairs=[(a,b) for a,b in zip(before,after) if b['team']=='50']
            for a,b in pairs:
                coords='; '.join(k+'='+b[k] for k in ('share','client','basis'))
                for column in ('hybrid_median','hybrid_cheapest','api_median','api_cheapest','capacity_day','served_day','overflow_day'):
                    add(policy,'person_cost',coords,column,a[column],b[column],
                        'call/day' if column.endswith('_day') else 'USD/person-month',name+' team=50')
                if share=='s50':
                    for denominator,label in [('requested_day','served_open_share'),(None,'served_all_calls_share')]:
                        values=[float(r['served_day'])/(float(r[denominator]) if denominator else 2500) for r in (a,b)]
                        add(policy,'served_s50',coords,label,*values,'1',name)
                if b['basis']=='Mac already owned':
                    key=clients[b['client']];prefix='hardware.clients.'+key
                    capital=max(0,inputs.get(prefix+'.purchase_price')-inputs.get(prefix+'.premium_credit'))
                    for api in ('median','cheapest'):
                        values=[]
                        for r in (a,b):
                            saving=float(r['api_'+api])-float(r['hybrid_'+api])
                            values.append(capital/saving if saving>0 else 'no payback')
                        add(policy,'payback',coords,'cash_payback_'+api,*values,'month',name+' incremental cash / (API - owned-client hybrid including same-API overflow)')
                        residual=inputs.get('economics.client_residual')
                        values=[v*(1-residual) if isinstance(v,float) else v for v in values]
                        add(policy,'payback',coords,'residual_adjusted_'+api,*values,'month',name+' net acquisition / monthly saving; not cash payback')
            for basis in ('Mac already owned','Mac premium bought'):
                subset=[(a,b) for a,b in pairs if b['basis']==basis]
                for api in ('median','cheapest'):
                    for label,formula,unit in (
                        ('saving_pct',lambda r:100*(1-float(r['hybrid_'+api])/float(r['api_'+api])),'%'),
                        ('api_over_hybrid',lambda r:float(r['api_'+api])/float(r['hybrid_'+api]),'ratio')):
                        values=[[formula(pair[i]) for pair in subset] for i in (0,1)]
                        for aggregate,fn in [('min',min),('max',max)]:
                            add(policy,'economics_range','share='+share+'; basis='+basis,
                                api+'_'+label+'_'+aggregate,fn(values[0]),fn(values[1]),unit,name+' six clients')
        name='client_sessions_day'+suffix+'.csv'
        for a,b in zip(*files[name]):
            if b['link_mbit']!='1000.0':continue
            coords=b['client']+'; link_mbit=1000'
            for column in ('local_sessions_day','hybrid_sessions_day'):
                add(policy,'client_capacity',coords,column.replace('sessions','calls'),
                    float(a[column])*chunk,float(b[column])*chunk,'call/day',name+' * chunk='+str(chunk))
        name='perimeter_cost'+suffix+'.csv';before,after=files[name]
        for profile in ('light','medium','heavy'):
            for team in ('5','10','20','50','500','5000'):
                for route,basis in sorted({(r['route'],r['basis']) for r in after}):
                    candidates=[]
                    for data in (before,after):
                        candidates.append([r for r in data if r['profile']==profile and r['team']==team and
                                           r['route']==route and r['basis']==basis and r['eligible']=='1' and
                                           r['status']=='ok' and float(r['unserved_day'])==0])
                    if all(candidates):
                        for label,fn in [('min',min),('max',max)]:
                            values=[fn(float(r['person_month']) for r in group) for group in candidates]
                            add(policy,'closed_perimeter_range',f'profile={profile}; team={team}; route={route}; basis={basis}',
                                'person_month_'+label,*values,'USD/person-month',name+' eligible complete service rows')
                if team not in ('5','20'):continue
                selected=[]
                for data in (before,after):
                    selected.append(next(r for r in data if r['profile']==profile and r['team']==team and
                                         r['route']=='all server' and r['selected']=='1'))
                a,b=selected;coords='profile='+profile+'; team='+team
                for col in ('server','units','person_month'):
                    add(policy,'own_server',coords,col,a[col],b[col],
                        'USD/person-month' if col=='person_month' else 'server unit' if col=='units' else 'text',name)
                for data,label in ((before,'old'),(after,'new')):
                    r=next(r for r in data if r['profile']==profile and r['team']==team and r['route']=='all server' and r['server'].startswith('Owned HGX'))
                    if label=='old':old=r
                    else:
                        for col in ('person_month','units','eligible'):
                            add(policy,'own_server_B300',coords,col,old[col],r[col],
                                'USD/person-month' if col=='person_month' else '1',name)
        name='offload_by_link'+suffix+'.csv'
        for a,b in zip(*files[name]):
            coords='state_bits='+b['state_bits']+'; link_mbit='+b['link_mbit']
            for col in ('share_calls','saved_seconds_call','saved_seconds_offloaded'):
                add(policy,'offload_example',coords,col,a[col],b[col],'1' if col=='share_calls' else 's/call',name)
    # These output-independent bounds have no distinct conservative export; both policies use identical values.
    for name in ('flop_per_byte.csv','transcript_example.csv','arch_compare.csv','decode_scaling.csv'):
        before,after=files[name]
        for index,(a,b) in enumerate(zip(before,after)):
            if name=='flop_per_byte.csv' and not (b['client'].startswith('M3 Max') and b['model']=='Qwen3.8-27B' and b['depth']=='110000' and b['state_bits']=='32' and b['portion_tokens']=='1000'):continue
            for col in b:
                if number(b[col]) is not None:
                    add('both','offload_bound' if name=='flop_per_byte.csv' else 'output_independent_example',
                        'row='+str(index),col,a[col],b[col],'see source schema',name)
    write_csv(ROOT/'calc/ENGINE-QUOTES-R11-261101.csv',rows,
              ['policy','category','coordinates','metric','r10','r11','unit','source'])
    return rows


def check_upper(directory):
    paths=list(Path(directory).glob('*.csv'))
    assert len(paths)==42,'upper-bound exports must cover all42 tables'
    cells=0
    for path in paths:
        prior=path.name.replace('reasoning_on_top_sensitivity','output_only_sensitivity')
        before=read_rows(old_bytes(prior));after=read_rows(path.read_bytes())
        assert len(before)==len(after),path
        for a,b in zip(before,after):
            for k,v in a.items():
                assert b[k]==v,(path,k,v,b[k])
                cells+=1
    print('Explicit fraction1 recovers all '+str(cells)+' run10 cells in42 CSVs exactly.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upper',type=Path,help='Check complete explicit fraction1 exports against run10')
    args=parser.parse_args()
    files,summary=audit();rows=quotes(files)
    if args.upper:check_upper(args.upper)
    print(json.dumps(dict(publication_files=len(summary),numeric_cells=sum(r['numeric_cells'] for r in summary),
                          changed_cells=sum(r['changed_cells'] for r in summary),quote_records=len(rows)),indent=2))


if __name__=='__main__':main()
