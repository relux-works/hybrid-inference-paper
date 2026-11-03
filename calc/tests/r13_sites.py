"""Exact printed coordinates for the ledger; the reverse guard is independent.

Rows are generated from paired source columns and the precision actually used
by each printed cell. Formula phrases are located literally in their declared
publication scopes, never inferred from an equal number elsewhere.
"""
import csv
import re
from r13_audit import ROOT, OUT, module
from r13_reverse import NUMBER, decimal, spellings, rounded, tokens, read_csv


def printed_sites(records,out=OUT):
    records=[{k:str(v) for k,v in r.items()} for r in records]
    texts={str(p.relative_to(ROOT)):p.read_text() for p in (ROOT/'paper').rglob('*.tex')}
    found=[]
    coordinates={(name,line,token) for name,line,token,unit in tokens(texts)}
    ranges=module('r13_site_ranges',ROOT/'paper/data/check_ranges.py')
    def add(name,line,token,new,key,source):
        if (name,line,token) in coordinates and token!=str(new):found.append(dict(paper_site=name+':'+str(line),kind='reverse-number',engine_key=key,old=token,new=str(new),unit='as printed',source=source))
    def cell(name,line,cell_index,values):
        text=texts[name].splitlines()[line-1].split('&')[cell_index]
        matches=list(NUMBER.finditer(text))
        assert len(matches)==len(values),(name,line,cell_index,text,values)
        for match,(old,new,key,source,scale) in zip(matches,values):
            token=match.group();spelling=next(iter(spellings(token)))
            exponent=-len(spelling.partition('.')[2])
            a=rounded(decimal(old)/decimal(scale),exponent)
            b=rounded(decimal(new)/decimal(scale),exponent)
            assert abs(decimal(a)-decimal(spelling))<=decimal(1).scaleb(exponent),(name,line,token,a,key)
            add(name,line,token,b,key,source)
    def paired(table):
        a=read_csv(ROOT/'paper/data/engine'/table)
        b=read_csv(out/'base'/table)
        return [(i,x,y) for i,(x,y) in enumerate(zip(a,b))]
    def value(table,row,key,scale=1):
        i,a,b=row
        return (a[key],b[key],f'{table}[row={i}].{key}',f'calc/out/run13/base/{table}',scale)
    channel='paper/sections/04-channel.tex'
    table='turn_speedup.csv'
    rows=paired(table)
    for line,(depth,portion) in zip(range(26,30),((100000,2000),(100000,10000),(200000,2000),(200000,10000))):
        for col,link in enumerate((100,300,1000,10000),2):
            row=next(r for r in rows if r[1]['state_format']=='f32' and int(r[1]['depth'])==depth and int(r[1]['portion'])==portion and float(r[1]['link_mbit'])==link)
            cell(channel,line,col,[value(table,row,'hybrid_s'),value(table,row,'speedup')])
    table='oneshot_ingest.csv';rows=paired(table)
    for line,context in zip(range(49,52),(100000,200000,262000)):
        for col,link in enumerate((100,300,1000,10000),2):
            row=next(r for r in rows if r[1]['state_format']=='f32' and int(r[1]['context'])==context and float(r[1]['link_mbit'])==link)
            cell(channel,line,col,[value(table,row,'hybrid_ttft_s',60 if col<4 else 1)])
    table='transcript_example.csv';rows=paired(table)
    for line,client in zip(range(77,80),('M3 Max','M5 Max','M5 Air')):
        for col,(link,key) in enumerate(((200,'local_ttft_s'),(200,'hybrid_ttft_s'),(1000,'hybrid_ttft_s'),(200,'local_total_s'),(200,'hybrid_total_s'),(1000,'hybrid_total_s')),1):
            row=next(r for r in rows if r[1]['client'].startswith(client) and float(r[1]['link_mbit'])==link)
            cell(channel,line,col,[value(table,row,key,1 if col==3 else 60)])
    table='offload_by_link.csv';rows=paired(table)
    for shareline,savedline,bits in ((99,100,32),(101,102,16)):
        for col,link in enumerate((100,300,1000,2500),1):
            row=next(r for r in rows if r[1]['state_bits']==str(bits) and float(r[1]['link_mbit'])==link)
            cell(channel,shareline,col,[value(table,row,'share_calls',.01)])
            cell(channel,savedline,col,[value(table,row,'saved_seconds_call')])
    table='client_sessions_day.csv'
    for line,row in zip(range(93,101),(r for r in paired(table) if float(r[1]['link_mbit'])==1000)):
        for col,key in enumerate(('single_tok_s_32k','local_sessions_day','hybrid_sessions_day','gain'),1):
            cell('paper/sections/05-clients.tex',line,col,[value(table,row,key)])
    table='remote_rent_buy.csv';rows=paired(table)
    for line,(team,hours) in zip(range(217,223),((5,10),(5,24),(10,10),(10,24),(50,10),(50,24))):
        for col,residual in enumerate((None,.2,.5,.8),1):
            row=next(r for r in rows if int(r[1]['team'])==team and float(r[1]['hours'])==hours and
                     r[1]['option']==('RTX PRO 6000 hourly' if residual is None else '1x RTX PRO 6000 Server; colocation') and
                     (residual is None or float(r[1]['residual'])==residual))
            cell('paper/sections/07-economics.tex',line,col,[value(table,row,'per_user_month'),value(table,row,'units')])
    # The literal formula strings already carry both the unchanged context and
    # every changed printed number. Locate that exact phrase, not every equal
    # scalar in the surrounding paragraph/table.
    for record in records:
        site=record['paper_site']
        if ' :: ' not in site or record['kind']=='printed-table-cell':continue
        name=site.split(' :: ')[0]
        if name not in texts:continue
        text=texts[name]
        marker=site.split(' :: ')[1]
        entry=next((s for s in ranges.SITES.get(record['engine_key'],[]) if 'paper/sections/'+s[0]==name and s[1]==marker),None)
        if entry:
            scope=ranges.scope({path_name.rsplit('/',1)[-1]:content for path_name,content in texts.items()},entry)
        elif record['kind']=='printed-table-row':
            scope=text
        elif record['engine_key'].startswith('people_per_gpu'):
            continue
        else:
            marker=re.split(r'[;(]',marker)[0].strip().replace('%',r'\%')
            pos=text.find(marker)
            if pos<0:continue
            start=text.rfind('\n\n',0,pos)+2;end=text.find('\n\n',pos)
            scope=text[start:end if end>=0 else len(text)]
        if not scope:continue
        base=text.find(scope)
        old=list(tokens({'value':record['old']}));new=list(tokens({'value':str(record['new'])}))
        if len(old)!=len(new):continue
        pattern=re.escape(record['old']);pattern=re.sub(r'(?:\\\s)+',r'\\s+',pattern)
        # Whitespace in reviewed prose formulas may span TeX source lines.
        pattern=r'\s+'.join(re.escape(part) for part in record['old'].split())
        if not pattern:continue
        for match in re.finditer(pattern,scope):
            for a,b in zip(old,new):
                if a[2]==b[2]:continue
                # A unique old token offset within the matched phrase keeps
                # repeated values at their actual printed source lines.
                offset=record['old'].find(a[2])
                prefix=record['old'][:offset]
                prefix_pattern=r'\s+'.join(re.escape(part) for part in prefix.split())
                partial=re.match(prefix_pattern,scope[match.start():]) if prefix_pattern else None
                pos=base+match.start()+(partial.end() if partial else 0)
                line=text.count('\n',0,pos)+1
                if a[2] not in text.splitlines()[line-1]:
                    line=next(n for n in range(line,line+record['old'].count('\n')+4) if n<=len(text.splitlines()) and a[2] in text.splitlines()[n-1])
                add(name,line,a[2],b[2],record['engine_key'],record['source'])
    def scalar(line_name,line,token,key,scale=1):
        record=next((r for r in records if r['engine_key']==key and r['kind'] in ('sentence','caption')),None)
        if record is None:return
        new=record['new']
        # Supplemental scalar records include display units, not a second value.
        numeric=next(iter(tokens({'value':new})))[2]
        spelling=next(iter(spellings(token)))
        result=rounded(decimal(numeric)/decimal(scale),-len(spelling.partition('.')[2]))
        add(line_name,line,token,result,key,record['source'])
    server='paper/sections/06-server.tex'
    for token,key in (('1.22','own'),('0.09','input'),('0.13','shadow')):
        scalar(server,6,token,'Context.b300.'+key)
    row=next(r for r in paired('turn_speedup.csv') if r[1]['state_format']=='f32' and r[1]['depth']=='200000' and r[1]['portion']=='10000' and float(r[1]['link_mbit'])==100)
    val=value('turn_speedup.csv',row,'hybrid_s')
    add(channel,12,'42',rounded(decimal(val[1]),0),val[2],val[3])
    for line,token,key in ((9,'0.05','people_per_gpu[B300,s20].migration_gpu_s_call'),(10,'0.12','people_per_gpu_conservative[B300,s20].migration_gpu_s_call')):
        scalar(server,line,token,key)
    for line,gpu,key,oldtokens,policy in (
            (26,'RTX','people_with_hosting',('64','25','12'),''),
            (27,'B300','people_with_hosting',('221','88','44'),''),
            (28,'RTX','people_compute_only',('69','27','13'),''),
            (28,'B300','people_compute_only',('308','123','61'),''),
            (29,'RTX','people_with_hosting',('57','22','11'),'_conservative'),
            (29,'B300','people_with_hosting',('159','63','31'),'_conservative')):
        table='people_per_gpu'+policy+'.csv'
        for token,share in zip(oldtokens,(.2,.5,1)):
            row=next(r for r in paired(table) if r[1]['gpu'].startswith(gpu) and float(r[1]['share'])==share)
            val=value(table,row,key)
            add(server,line,token,rounded(decimal(val[1]),0),val[2],val[3])
    # Supplemental units/rounding whose Russian text is not a literal copy of
    # the English display unit in the supporting ledger record.
    for name,line,token,key,scale in (
        (channel,12,'5','turn_speedup.hybrid_s',1),
        (channel,37,'71','oneshot_ingest.hybrid_ttft_s',1),
        (channel,37,'14','oneshot_ingest.server_prefill_s',1),
        (channel,58,'24','transcript_example.hybrid_ttft_s',1),
        (channel,58,'6.7','transcript_example.hybrid_total_s',1),
        (channel,127,'152','traffic_user_month[heavy].egress_3',1),
        (channel,67,'3.5','transcript_example.server_prefill_s',1),
        ('paper/sections/05-clients.tex',72,'1.6','client_sessions_day.gain',1),
        ('paper/sections/05b-models.tex',85,'1.35','server_compute depth 110000',1),
        ('paper/sections/05b-models.tex',70,'3.4','offload_bound[110k,10k,1000Mbit].local/(server+transfer)',1),
        ('paper/sections/05b-models.tex',71,'14','offload_bound[110k,10k,10000Mbit].local/(server+transfer)',1),
        ('paper/sections/05b-models.tex',71,'22.5','offload_bound.server_compute/client_peak',1),
        ('paper/sections/08-million.tex',13,'43','glm_long_sessions.ingest_1m_server_s prefill only',1),
        ('paper/sections/08-million.tex',13,'97','glm_long_sessions.ingest_1m_server_s with transfer',1)):
        scalar(name,line,token,key,scale)
    # The rent/buy paragraph repeats the 50-person table cells at new sites.
    for line,token,option,residual in ((200,'24','RTX PRO 6000 hourly',None),(201,'25','1x RTX PRO 6000 Server; colocation',.8)):
        row=next(r for r in paired('remote_rent_buy.csv') if r[1]['team']=='50' and float(r[1]['hours'])==10 and
                 r[1]['option']==option and (residual is None or float(r[1]['residual'])==residual))
        val=value('remote_rent_buy.csv',row,'per_user_month')
        add('paper/sections/07-economics.tex',line,token,rounded(decimal(val[1]),0),val[2],val[3])
    # The published lower endpoint 0.8 is already stale against R12's 1.5.
    # Preserve the actual printed token in the writer's work list and use the
    # independently catalogued selected-hybrid range for its R13 replacement.
    record=next(r for r in records if r['engine_key']=='perimeter_cost[medium,selected hybrid].prefill_mean_s range')
    for token,new in zip(('0.8','1.9'),record['new'].split('--')):
        add('paper/sections/07-economics.tex',235,token,new,record['engine_key'],record['source'])
    # Written old ranges, including the rounded 24-hour capacity example.
    for name,line,oldtokens,key in (
        ('paper/sections/01-introduction.tex',12,('30',),'server_bulk[phase_a].fp8_fraction range'),
        ('paper/sections/05b-models.tex',85,('30',),'server_bulk[phase_a].fp8_fraction range'),
        ('paper/sections/11-limitations.tex',7,(r'2\,650','880'),'person_cost_s20[M5 Max64,owned].capacity_day * [3,1]')):
        record=next(r for r in records if r['engine_key']==key)
        newparts=list(tokens({'value':record['new']}))
        for token,new in zip(oldtokens,newparts):add(name,line,token,new[2],key,record['source'])
    return list({(r['paper_site'],r['old'],r['engine_key']):r for r in found}.values())
