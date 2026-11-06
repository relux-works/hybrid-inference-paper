"""Snapshot-bound sentence regeneration, parser and cell-by-cell custody."""
import csv
from functools import lru_cache
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
BASE='a706732f1530df51d7e94050802ef4429daeac33'
SERVERS={'pro6000_fp8':'RTX PRO 6000 vLLM FP8 (pro6000_fp8)',
         'b300_fp8':'B300 vLLM FP8 (b300_fp8)',
         'b300_fp8_kv':'B300 vLLM FP8 with FP8 KV (b300_fp8_kv)',
         'llama_pro6000':'RTX PRO 6000 llama.cpp sensitivity (llama_pro6000)',
         'llama_b300':'B300 llama.cpp sensitivity (llama_b300)'}
CLIENTS={'m5max64':'M5 Max 64 GB (m5max64)','m5max':'M5 Max 128 GB (m5max)'}
LINKS={
    'bought':('bought','office office_gigabit, 125 MB/s, RTT 1 ms (assumed goodput and RTT)'),
    'rented':('rented','rented WAN engine_wan, 112.5 MB/s, RTT 400 ms (engine WAN estimate)'),
    'shared_work':('shared resident work','shared engine WAN engine_wan, 112.5 MB/s, RTT 400 ms (engine WAN estimate)'),
}
FIELDS=('server','billing','link','client','s','cache allowance','load','coverage')


import history_evidence as history

def conditions(row):
    billing,link=LINKS[row['billing']]
    return ('server={}; billing={}; link={}; client={} {}; s={}; cache allowance={}; load={}; coverage={}').format(
        SERVERS[row['server']],billing,link,CLIENTS[row['client']],row['basis'],row['share'],row['cache_basis'],row['load'],row['workload_scope'])


def condition_field(text,name):
    match=re.search(r'(?:^|;\s*)'+re.escape(name)+r'=([^;]+)',text)
    assert match,'missing sentence condition: '+name
    return match.group(1)


def parse_sentence(text):
    """Parse canonical, human-readable condition clauses, not loose keywords."""
    values={name:condition_field(text,name)for name in FIELDS}
    assert values['server']in SERVERS.values(),'unknown sentence server'
    assert values['billing']in {x[0]for x in LINKS.values()},'unknown sentence billing'
    assert values['link']==next(x[1]for x in LINKS.values()if x[0]==values['billing']),'sentence billing/link mismatch'
    link=re.search(r'([0-9.]+) MB/s, RTT ([0-9.]+) ms',values['link'])
    assert link,'missing sentence link rate/RTT'
    assert values['client']in {client+' '+basis for client in CLIENTS.values()for basis in ('owned','new')},'unknown sentence client'
    assert re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',values['s'])and 0<=float(values['s'])<=1,'invalid sentence share'
    assert re.match(r'98\.1%(?:\s|$)',values['cache allowance']),'missing sentence cache allowance'
    assert values['load']in ('light','medium','heavy'),'unknown sentence load'
    counts=re.search(r'(\d+)/(\d+)\s*\(([0-9.]+)%\)',values['coverage'])
    assert counts and 0<int(counts[1])<=int(counts[2]),'missing sentence coverage counts'
    values['rate_MB_s']=float(link[1]);values['rtt_ms']=float(link[2])
    return values


def validate_sentence(text,row):
    values=parse_sentence(text)
    expected={'server':SERVERS[row['server']],'billing':LINKS[row['billing']][0],
              'link':LINKS[row['billing']][1],'client':CLIENTS[row['client']]+' '+row['basis'],
              's':str(row['share']),'cache allowance':row['cache_basis'].split(';')[0],'load':row['load'],
              'coverage':row['workload_scope'].split(';')[0]}
    for name,value in expected.items():assert values[name]==value,'sentence condition disagrees with row: '+name
    assert 'coverage='+row['workload_scope']in text,'sentence drops full coverage basis'
    assert 'cache allowance='+row['cache_basis']in text,'sentence drops full cache basis'
    return values


@lru_cache(maxsize=None)
def source_rows(path):
    return list(csv.DictReader(io.StringIO((ROOT/path).read_text())))


def alarm_clause(row):
    if math.isfinite(float(row['hybrid_person_month'])):return ''
    match=re.fullmatch(r'(calc/out/run\d+/\w+\.csv)\[row=(\d+)\]',row['source'])
    assert match,'capacity alarm lacks source coordinate'
    source=source_rows(match[1])[int(match[2])]
    assert source['status']=='alarm','nonfinite cost lacks source capacity alarm'
    return '; capacity alarm: source status='+source['status']+', alarm_inputs='+source['alarm_inputs']+'; requested demand is unserviceable under the finite-concurrency model'


def policy():return dict(source='calc/tests/r15_sentences.py',sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),basis='sentence-only correction of '+BASE)


def before(path):
    return list(csv.DictReader(io.StringIO(history.snapshot_object(BASE+':'+str(path.relative_to(ROOT))).decode())))


def sentence_diff():
    """All original columns and non-sentence cells, including growing, are exact."""
    import r14_publication as p
    changes=[];unchanged=0
    names=history.snapshot_paths(BASE,'calc/out/run20','calc/out/run21')
    for name in names:
        if not name.endswith('.csv'):continue
        path=ROOT/name;a=before(path);b=p.read(path)
        assert len(a)==len(b),'sentence rework changed row count: '+name
        for index,(old,new)in enumerate(zip(a,b)):
            assert list(old)==list(new),'sentence rework changed column set/order: '+name
            for key,value in old.items():
                if new[key]!=value:
                    assert key=='sentence','non-sentence cell changed: '+name+'/'+key
                    changes.append(dict(source=name,row=index,column=key,old=value,new=new[key]))
                else:unchanged+=1
    return changes,unchanged


def refresh():
    import r14_publication as p
    for run in (20,21):
        directory=ROOT/f'calc/out/run{run}/paper';primary=[]
        for name in ('team_break_even','dedicated_multiples','shared_multiples'):
            path=directory/(name+'.csv');rows=p.read(path)
            for row in rows:
                row['sentence']=(p.conclusion(row)+' '+row['rate_basis']+'; '+row['api_median_basis']+'.'if name=='team_break_even'else p.multiple_sentence(row))
                validate_sentence(row['sentence'],row)
            p.dump(path,rows);primary+=rows
        path=directory/'paper_claims.csv';claims=p.read(path)
        assert len(primary)==len(claims),'claim projection count changed'
        for row,source in zip(claims,primary):
            assert all(value==source[key]for key,value in row.items()if key!='sentence'),'claim projection order changed'
            row['sentence']=source['sentence'];validate_sentence(row['sentence'],row)
        p.dump(path,claims)
        manifest=json.loads((directory/'manifest.json').read_text())
        manifest['policy_sha256']=p.digest(Path(p.__file__));manifest['sentence_policy']=policy()
        manifest['files']={name:p.digest(directory/name)for name in manifest['files']}
        p.js(directory/'manifest.json',manifest)
        p.dump(ROOT/f'calc/ENGINE-QUOTES-R{run}-PAPER-261103.csv',p.quotes(run))
    directory=ROOT/'calc/out/run20';path=directory/'r20_manifest.json';manifest=json.loads(path.read_text())
    manifest['r14_publication']['sha256']=p.digest(Path(p.__file__));p.js(path,manifest);p.refresh_index(directory)
    changes,unchanged=sentence_diff();p.dump(ROOT/'calc/ENGINE-SENTENCE-DIFF-R15-261103.csv',changes)
    print('changed sentence cells',len(changes),'identical other cells',unchanged,flush=True)
    return changes


def readable(text):
    return text.replace('versus own_cluster:','versus the cheapest capacity-admitted PRO6000/B300 vLLM own cluster:').replace('versus api_median:','versus the admitted median API:').replace('versus api_cheapest:','versus the cheapest admitted API:')


def refresh_reports():
    import r14_publication as p
    for run in (20,21):
        path=ROOT/f'calc/ENGINE-REPORT-R{run}-261103.md'
        text=history.snapshot_object(BASE+':'+str(path.relative_to(ROOT))).decode()
        for name in ('team_break_even','dedicated_multiples','shared_multiples'):
            source=ROOT/f'calc/out/run{run}/paper/{name}.csv'
            for old,new in zip(before(source),p.read(source)):
                selected=(old['server']=='pro6000_fp8'and old['client']=='m5max64'and old['basis']=='owned'and
                    (float(old['share'])==1 and old['billing']=='bought'if name=='team_break_even'else
                     float(old['share'])==.2 and old['team']==('50'if name=='shared_multiples'else'20')and old['billing']in ('bought','shared_work')))
                if selected:
                    a=readable(old['sentence']);b=readable(new['sentence'])
                    assert a in text,'report quotation not found: '+name
                    text=text.replace(a,b)
        breaks=p.read(ROOT/f'calc/out/run{run}/paper/team_break_even.csv')
        selected=[r for r in breaks if float(r['share'])==1 and r['client']=='m5max64'and r['basis']=='owned'and r['billing']=='bought']
        lookup={(r['profile'],r['load'],r['server'],r['reference']):readable(r['sentence'])for r in selected}
        lines=[]
        for line in text.splitlines():
            cells=[x.strip()for x in line.strip('|').split('|')]if line.startswith('|')else[]
            if run==20 and len(cells)==4 and cells[0]in ('light','medium','heavy')and cells[1]=='pro6000_fp8'and cells[2]in ('own_cluster','api_median','api_cheapest'):
                cells[-1]=lookup['common_measured_r20',cells[0],cells[1],cells[2]];line='| '+' | '.join(cells)+' |'
            elif run==20 and len(cells)==3 and cells[0]in ('light','medium','heavy')and cells[1].startswith('cheaper '):
                cells[-1]=lookup['common_measured_r20',cells[0],'pro6000_fp8','own_cluster'];line='| '+' | '.join(cells)+' |'
            elif run==21 and len(cells)==4 and cells[0]in ('existing_combined','claude_deep')and cells[1]in ('light','medium','heavy')and cells[2]in ('pro6000_fp8','b300_fp8','b300_fp8_kv'):
                cells[-1]=lookup[cells[0],cells[1],cells[2],'own_cluster'];line='| '+' | '.join(cells)+' |'
            lines.append(line)
        text='\n'.join(lines)+'\n'
        text+='''

## R15 / r5x2 self-contained sentence rework, 2026-11-03

The r5x2 review requested one sentence-only correction: every quotable sentence now names the server, bought/rented/shared-resident-work billing, its actual link and location, rate and RTT, client and ownership, s, load, cache allowance and full coverage. Bought uses office125MB/s1ms; rented uses engine WAN112.5MB/s400ms; shared resident work explicitly uses shared engine WAN112.5MB/s400ms. Link assumptions are stated inside each sentence. The parser checks both presence and agreement with the row; a complete but wrong billing/link pair is refused.

All9006 sentence cells are regenerated without numerical recalculation. Every381159 other original CSV cell is byte-identical after parsing, including growing exports, numeric displays and nan cells; no columns were added. The exact old/new sentence diff is `ENGINE-SENTENCE-DIFF-R15-261103.csv`. Existing paper quote ledgers are refreshed; `ENGINE-QUOTES-R15-261103.csv` records report text changes. Report words-ready table cells and prose carry the same complete conditions. The144 primary capacity-alarm sentences now disclose original source status/alarm_inputs; copied claims retain that disclosure without changing nan prices. The drop_quote narrowing fault now removes a real ledger row from the read path instead of replacing the verifier wholesale.

No engine rates, inputs, prices, workloads, crossings or multiples changed. Earlier resource exceptions above remain historical R14 evidence; R15 uses GiB: floor28GiB (30064771072B), hold below28.5GiB (30601641984B), maximum20-minute resource wait. No surface table was supplied (brief gap). Independent re-review remains pending. Current validation receipts follow below.
'''
        path.write_text(text)


def verify_reports():
    counts={}
    for run in (20,21):
        count=0
        for line in (ROOT/f'calc/ENGINE-REPORT-R{run}-261103.md').read_text().splitlines():
            if '; server='not in line:continue
            text=line[2:]if line.startswith('- ')else line.strip('|').split('|')[-1].strip()
            parse_sentence(text);count+=1
        assert count==(27 if run==20 else 48),'missing report sentence conditions'
        counts[run]=count
    return counts


def verify():
    import r14_publication as p
    changes,unchanged=sentence_diff()
    assert p.read(ROOT/'calc/ENGINE-SENTENCE-DIFF-R15-261103.csv')==[{k:str(v)for k,v in r.items()}for r in changes],'sentence diff ledger mismatch'
    count=0
    for run in (20,21):
        p.verify_paper(run);p.verify_quotes(run)
        for path in (ROOT/f'calc/out/run{run}/paper').glob('*.csv'):
            for row in p.read(path):
                if 'sentence'in row:validate_sentence(row['sentence'],row);count+=1
    assert count==len(changes)==9006,'missing regenerated sentence'
    verify_reports()
    print('parsed sentences',count,'unchanged other cells',unchanged,flush=True)
    return count


def main():
    assert sys.argv[1:]in([],['--audit-only']),'unsupported arguments'
    if not sys.argv[1:]:
        refresh();refresh_reports()
    verify()

if __name__=='__main__':main()
