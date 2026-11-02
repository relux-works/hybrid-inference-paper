"""Generate isolated run13 exports, current API baselines and published claim replacements."""
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import run,load
from hybridcalc.export import write_tables,generator_identity
from r11_audit import CASES
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calc/out/run13'
BASELINE='7c2e9b1e8e87835f474ae45a4454bda74f4af6d3'


def frozen():
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASELINE,'calc/out/paper'],cwd=ROOT,text=True).splitlines()
    for name in names:
        old=subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)
        assert (ROOT/name).read_bytes()==old,name
    return len(names)


def export():
    frozen()
    write_tables(run('server-options-r13'),OUT/'measurements')
    for case in ('base','earlier-run','checkpoints-on'):
        for name,_ in CASES:
            scenario=name+'-r13'+('' if case=='base' else '-'+case)
            manifest=write_tables(run(scenario),OUT/case)
            print(scenario,len(manifest['tables']),manifest['alarm_cells'],flush=True)
    # Recompute every current canonical API comparison that consumes prices.json.
    for name in ('paper-base','glm-tier2','service-quantized','service-fp8','service-bf16-academic','owners-economics','owners-paper','crossover-bridge'):
        result=run(name)
        (OUT/'api-baselines').mkdir(exist_ok=True)
        (OUT/'api-baselines'/(name+'.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
        print(name,'API baseline recomputed',flush=True)
    assert frozen()>0


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def derived():
    # Run the paper's unchanged derivation against new tables in a new directory.
    dest=OUT/'paper-derived';dest.mkdir(exist_ok=True)
    m=module('r13_derive',ROOT/'paper/data/derive_charts.py');m.HERE=str(dest);m.rows=lambda name:list(csv.DictReader(io.StringIO((OUT/'base'/name).read_text())));m.main()
    # Preserve the full R12 payback-comparison scope as new, case-local
    # tables; paper-derived/payback.csv separately uses cheapest overflow.
    _, inputs=load('paper-tables-r13')
    labels={inputs.locate('hardware.clients.'+k+'.label'):k for k in ('m3max','m4max','m5max64','m5max','ultra96','ultra256')}
    for case in ('base','earlier-run','checkpoints-on'):
        for suffix in ('','_conservative'):
            records=[]
            for share in ('s20','s50'):
                path=OUT/case/('person_cost_'+share+suffix+'.csv')
                for row in csv.DictReader(io.StringIO(path.read_text())):
                    if row['team']!='50' or row['basis']!='Mac already owned':continue
                    key=labels[row['client']];prefix='hardware.clients.'+key
                    capital=max(0,inputs.get(prefix+'.purchase_price')-inputs.get(prefix+'.premium_credit'))
                    for api in ('median','cheapest'):
                        saving=float(row['api_'+api])-float(row['hybrid_'+api])
                        cash=capital/saving if saving>0 else 'no payback'
                        adjusted=cash*(1-inputs.get('economics.client_residual')) if isinstance(cash,float) else cash
                        records.append(dict(client=row['client'],share=row['share'],overflow_api=api,capital=capital,saving_month=saving,cash_months=cash,residual_adjusted_months=adjusted,source=path.name))
            write(OUT/case/('payback'+suffix+'.csv'),records)
    return dest


def write(path,records):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)


def quoted():
    dest=derived();records=[]
    def add(site,kind,key,old,new,unit,source):
        if str(old)!=str(new):records.append(dict(paper_site=site,kind=kind,engine_key=key,old=old,new=new,unit=unit,source=source))
    # Capture every changed numeric cell of any table consumed by paper figures
    # or printed numeric tables, with stable row and column coordinates.
    sections={p.name:p.read_text() for p in (ROOT/'paper/sections').glob('*.tex')}
    for old in sorted((ROOT/'paper/data/engine').glob('*.csv')):
        new=OUT/'base'/old.name
        if not new.exists():continue
        before=list(csv.DictReader(old.open()));after=list(csv.DictReader(new.open()))
        assert len(before)==len(after),(old.name,'row identity changed')
        for i,(a,b) in enumerate(zip(before,after)):
            for k,v in a.items():
                try:float(v)
                except (ValueError,TypeError):continue
                if v==b[k]:continue
                # These data are consumed by printed tables too; the sentence
                # registry below identifies exact prose/caption sites.
                add('paper/data/engine/'+old.name,'table-cell',f'{old.name}[row={i}].{k}',v,b[k],'see schema','calc/out/run13/base/'+new.name)
    for old in sorted((ROOT/'paper/data').glob('*.csv')):
        new=dest/old.name
        if old.name=='arch-compare.csv':
            before=subprocess.check_output(['git','show','c04a99d:paper/data/arch-compare.csv'],cwd=ROOT,text=True)
            a=list(csv.DictReader(before.splitlines()));b=list(csv.DictReader(old.open()));new=old
        elif new.exists():a=list(csv.DictReader(old.open()));b=list(csv.DictReader(new.open()))
        else:continue
        for i,(x,y) in enumerate(zip(a,b)):
            for key in x:
                try:float(x[key])
                except (ValueError,TypeError):continue
                sites=[name for name,s in sections.items() if 'data/'+old.name in s] or ['05b-models.tex' if old.name=='arch-compare.csv' else '07-economics.tex']
                for site in sites:add('paper/sections/'+site,'figure-cell',f'{old.name}[row={i}].{key}',x[key],y[key],'as printed','calc/out/run13/paper-derived/'+new.name if new.parent==dest else str(new.relative_to(ROOT)))
    # Reuse the reviewed paper's complete economics/million-token sentence registry.
    m=module('r13_ranges',ROOT/'paper/data/check_ranges.py');old_values=m.values(m.model());m.HERE=str(dest);m.rows=lambda name:list(csv.DictReader(io.StringIO((OUT/'base'/name).read_text())))
    new_model=m.model();new_values=m.values(new_model)
    for key,sites in m.SITES.items():
        for site in sites:
            add('paper/sections/'+site[0]+' :: '+site[1],'sentence',key,old_values[key],new_values[key],'paper printed form','paper/data/check_ranges.py values() -> calc/out/run13/base')
    # Printed client and perimeter tables are generated by the same reviewed helpers.
    old_m=module('r13_old_ranges',ROOT/'paper/data/check_ranges.py');om=old_m.model()
    for key,oldrows,newrows in [('tab:econ',old_m.econ_rows(om['s20'],om['s50'],om['b50']),m.econ_rows(new_model['s20'],new_model['s50'],new_model['b50'])),('tab:perimeter',old_m.perimeter_rows(om['design'],om['cons']),m.perimeter_rows(new_model['design'],new_model['cons']))]:
        for i,(a,b) in enumerate(zip(oldrows,newrows)):add('paper/sections/07-economics.tex :: '+key,'printed-table-row',key+'[row='+str(i)+']',a,b,'USD/person-month and call/day','calc/out/run13/base')
    from r13_quotes import supplement
    supplement(add,OUT)
    # Discover native-CSV numbers/ranges by scanning every TeX numeric token,
    # independently of the hand-maintained sentence registry (19--22 at :54).
    from r13_ledger import native_changes,paper_numbers
    records.extend(native_changes(paper_numbers()))
    from r13_quotes import traffic_changes
    traffic_changes(add,OUT)
    from r13_sites import printed_sites
    records.extend(printed_sites(records,OUT))
    write(ROOT/'calc/ENGINE-QUOTES-R13-261101.csv',records)
    return records


if __name__=='__main__':
    if '--quotes-only' not in sys.argv:export()
    records=quoted()
    index=dict(generator=generator_identity(),files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='INDEX.json'})
    (OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print('frozen historical files',frozen(),'quote records',len(records),flush=True)
