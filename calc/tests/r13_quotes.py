"""Explicit paper timing, server, geometry and capacity quote coordinates for R13."""
from history_fixtures import snapshot_read
import csv
import io
import json
from pathlib import Path
from hybridcalc.engine import load
from hybridcalc.inputs import ROOT
from hybridcalc.paper_tables import Context
from hybridcalc.server_prefill import mean_seconds,compute_at
from hybridcalc.performance import flop


def supplement(add, out):
    def read(path):return list(csv.DictReader(io.StringIO(path.read_text())))
    old=ROOT/'paper/data/engine';new=out/'base'
    # Numeric table rows printed directly in TeX (not pgfplots CSV imports).
    specs={
      'turn_speedup':('04-channel.tex :: tab:turn',lambda r:r['state_format']=='f32' and float(r['link_mbit']) in (100,300,1000,10000),('local_prefill_s','hybrid_s','speedup')),
      'oneshot_ingest':('04-channel.tex :: tab:oneshot',lambda r:r['state_format']=='f32' and float(r['link_mbit']) in (100,300,1000,10000),('local_s','hybrid_ttft_s')),
      'transcript_example':('04-channel.tex :: tab:transcript',lambda r:True,('local_ttft_s','hybrid_ttft_s','local_total_s','hybrid_total_s')),
      'offload_by_link':('04-channel.tex :: tab:offload',lambda r:True,('share_calls','saved_seconds_call')),
      'client_sessions_day':('05-clients.tex :: tab:clients',lambda r:float(r['link_mbit'])==1000,('single_tok_s_32k','local_sessions_day','hybrid_sessions_day','gain')),
      'arch_compare':('05b-models.tex :: tab:arch',lambda r:r['state_format']=='f32',('kv_full_bytes_token','delta_1k_mb','transfer_1k_300mbit_s','saving_1k_131k_300mbit_s','saving_1k_131k_1000mbit_s')),
      'remote_rent_buy':('07-economics.tex :: tab:rentbuy',lambda r:r['option'] in ('RTX PRO 6000 hourly','1x RTX PRO 6000 Server; colocation') and int(r['team']) in (5,10,50),('per_user_month','units')),
    }
    for name,(site,select,columns) in specs.items():
        for i,(a,b) in enumerate(zip(read(old/(name+'.csv')),read(new/(name+'.csv')))):
            if not select(b):continue
            for key in columns:add('paper/sections/'+site,'printed-table-cell',f'{name}.row[{i}].{key}',a[key],b[key],'see run13 schema','calc/out/run13/base/'+name+'.csv')
    def pair(name,select):
        a=[r for r in read(old/(name+'.csv')) if select(r)]
        b=[r for r in read(new/(name+'.csv')) if select(r)]
        assert len(a)==len(b)==1,(name,len(a),len(b))
        return a[0],b[0]
    def metric(site,name,select,key,format=lambda v:f'{v:.2f}'):
        a,b=pair(name,select)
        add('paper/sections/'+site,'sentence',name+'.'+key,format(float(a[key])),format(float(b[key])),'as printed','calc/out/run13/base/'+name+'.csv')
    metric('04-channel.tex :: Один ход (10k at 200k; gigabit)','turn_speedup',lambda r:r['state_format']=='f32' and r['depth']=='200000' and r['portion']=='10000' and float(r['link_mbit'])==1000,'hybrid_s',lambda v:f'{v:.0f} s')
    metric('04-channel.tex :: Разовая загрузка (200k; gigabit)','oneshot_ingest',lambda r:r['state_format']=='f32' and r['context']=='200000' and float(r['link_mbit'])==1000,'hybrid_ttft_s',lambda v:f'{v:.0f} s')
    metric('04-channel.tex :: Разовая загрузка (server 200k)','oneshot_ingest',lambda r:r['state_format']=='f32' and r['context']=='200000' and float(r['link_mbit'])==1000,'server_prefill_s',lambda v:f'{v:.0f} s')
    for key,unit in [('hybrid_ttft_s','s'),('hybrid_total_s','min')]:
        metric('04-channel.tex :: Пример вне программирования; M3 gigabit','transcript_example',lambda r:r['client'].startswith('M3') and float(r['link_mbit'])==1000,key,lambda v:f'{v:.0f} s' if unit=='s' else f'{v/60:.1f} min')
    metric('04-channel.tex :: tab:transcript caption; server 70k','transcript_example',lambda r:r['client'].startswith('M3') and float(r['link_mbit'])==1000,'server_prefill_s',lambda v:f'{v:.1f} s')
    metric('05-clients.tex :: Сколько успевает клиент за день; M3','client_sessions_day',lambda r:r['client'].startswith('M3') and float(r['link_mbit'])==1000,'gain',lambda v:f'{v:.1f}')
    for bits in (32,16):
        for policy,suffix in [('design',''),('conservative','_conservative')]:
            for i,(a,b) in enumerate(zip(read(old/('people_per_gpu'+suffix+'.csv')),read(new/('people_per_gpu'+suffix+'.csv')))):
                if bits==16:continue
                for key in ('people_compute_only','people_with_hosting'):
                    add('paper/sections/06-server.tex :: Сколько людей держит одна карта','sentence',f'people_per_gpu{suffix}.row[{i}].{key}',a[key],b[key],'people','calc/out/run13/base/people_per_gpu'+suffix+'.csv')
    # Paragraphs reuse a range, so retain the exact range calculation as the key.
    def gains(directory):
        return [100*(float(r['gain'])-1) for r in read(directory/'client_sessions_day.csv') if r['client'].startswith('M5') and float(r['link_mbit'])==1000]
    def span(values):return f'{min(values):.0f}--{max(values):.0f}'
    for site in ('05-clients.tex :: Сколько успевает клиент за день; M5','14-conclusion.tex :: на M5 на 11--17'):
        add('paper/sections/'+site,'sentence','client_sessions_day[M5,1G].100*(gain-1) range',span(gains(old)),span(gains(new)),'percent','calc/out/run13/base/client_sessions_day.csv')
    a,b=pair('person_cost_s20',lambda r:r['client']=='M5 Max 64 GB' and r['basis']=='Mac already owned' and r['team']=='5')
    def capacities(r):return f"{round(3*float(r['capacity_day']),-1):.0f} / {round(float(r['capacity_day']),-1):.0f}"
    add('paper/sections/11-limitations.tex :: около 2650 вместо 880','sentence','person_cost_s20[M5 Max64,owned].capacity_day * [3,1]',capacities(a),capacities(b),'call/day; 24h / 8h','calc/out/run13/base/person_cost_s20.csv')
    # Traffic paragraph uses the heavy, capacity-limited M3 row and its actual bill.
    for key in ('bytes_per_served_call','served_day','hybrid_tb_month','egress_1','egress_2','egress_3'):
        a,b=pair('traffic_user_month',lambda r:r['profile']=='heavy')
        add('paper/sections/04-channel.tex :: Трафик как статья расходов','sentence','traffic_user_month[heavy].'+key,a[key],b[key],'see schema','calc/out/run13/base/traffic_user_month.csv')
    # Same printed server example, recomputed through the real Context consumer.
    server=[]
    for name in ('paper-tables','paper-tables-r13'):
        s,i=load(name);c=Context(s,i);m=c.model('qwen27');srv=c.server('b300',m)
        calls=c.g.resolve(c.valid).value;fm=c.g.resolve(m['flop']).value;compute=c.g.resolve(srv['compute']).value
        own=c.g.resolve(c.own_seconds('quote.server',c.valid,m,srv)).value
        server.append(dict(own=own,input=mean_seconds(calls,fm,compute,False),shadow=mean_seconds(calls,fm,compute,True)))
    for key in ('own','input','shadow'):
        add('paper/sections/06-server.tex :: По нашей модели','sentence','Context.b300.'+key,f"{server[0][key]:.2f}",f"{server[1][key]:.2f}",'GPU s/call','Context.own_seconds / server_prefill.mean_seconds, full sampled mix')
    add('paper/sections/06-server.tex :: в 9 раз меньше','sentence','Context.b300.own / shadow',f"{server[0]['own']/server[0]['shadow']:.0f}",f"{server[1]['own']/server[1]['shadow']:.0f}",'ratio','same Context consumers')
    for suffix in ('','_conservative'):
        a,b=pair('people_per_gpu'+suffix,lambda r:r['gpu'].startswith('B300') and float(r['share'])==.2)
        add('paper/sections/06-server.tex :: подъём и запись копии'+suffix,'sentence','people_per_gpu'+suffix+'[B300,s20].migration_gpu_s_call',f"{float(a['migration_gpu_s_call']):.2f}",f"{float(b['migration_gpu_s_call']):.2f}",'GPU s/call','calc/out/run13/base/people_per_gpu'+suffix+'.csv')
    # Medium-load closed-perimeter wait and unmet local demand precede the
    # economic paragraph's registered cost ranges.
    a,b=pair('perimeter_cost',lambda r:r['route']=='Macs only' and r['client']=='M5 Max 64 GB' and r['basis']=='Mac already owned' and r['profile']=='medium' and r['team']=='50')
    add('paper/sections/07-economics.tex :: не успевают ответить на 5%','sentence','perimeter_cost[medium,M5,Macs only].unserved_day/requested_day',f"{100*float(a['unserved_day'])/float(a['requested_day']):.0f}",f"{100*float(b['unserved_day'])/float(b['requested_day']):.0f}",'percent','calc/out/run13/base/perimeter_cost.csv')
    add('paper/sections/07-economics.tex :: prefill в среднем 6.5 секунды','sentence','perimeter_cost[medium,M5,Macs only].prefill_mean_s',f"{float(a['prefill_mean_s']):.1f}",f"{float(b['prefill_mean_s']):.1f}",'s','calc/out/run13/base/perimeter_cost.csv')
    def wait(directory):return [float(r['prefill_mean_s']) for r in read(directory/'perimeter_cost.csv') if r['profile']=='medium' and r['route']=='hybrid' and r['client']=='M5 Max 64 GB' and r['basis']=='Mac already owned' and r['selected']=='1' and r['team'] in ('50','500','5000')]
    add('paper/sections/07-economics.tex :: prefill от 0.8 до 1.9','sentence','perimeter_cost[medium,selected hybrid].prefill_mean_s range',f'{min(wait(old)):.1f}--{max(wait(old)):.1f}',f'{min(wait(new)):.1f}--{max(wait(new)):.1f}','s','calc/out/run13/base/perimeter_cost.csv')
    # The million-token cold-ingest column includes transfer; subtract the
    # identical explicit wire component to recover the printed pure prefill.
    from hybridcalc.performance import transfer
    _,ii=load('paper-tables-r13')
    wire=transfer(1e6,ii.get('owners.models.glm.kv'),ii.get('models.glm.wire_state'),ii.section('hardware.links.wan'))
    a,b=pair('glm_long_sessions',lambda r:r['context']=='1000000' and r['team']=='5')
    for label,offset in [('with transfer',0),('prefill only',wire)]:
        add('paper/sections/08-million.tex :: Клиент для миллиона токенов','sentence','glm_long_sessions.ingest_1m_server_s '+label,f"{float(a['ingest_1m_server_s'])-offset:.0f}",f"{float(b['ingest_1m_server_s'])-offset:.0f}",'s','calc/out/run13/base/glm_long_sessions.csv')
    # Hybrid bill in the yearly-account paragraph is the M5 owned-client
    # s20 bill per requested open-model call, under both hosting policies.
    def hybrid_cents(directory):
        return [100*float(r['hybrid_cheapest'])/(float(r['requested_day'])*21) for suffix in ('','_conservative') for r in read(directory/('person_cost_s20'+suffix+'.csv')) if r['client']=='M5 Max 64 GB' and r['basis']=='Mac already owned' and r['team']=='5']
    a,b=hybrid_cents(old),hybrid_cents(new)
    add('paper/sections/07-economics.tex :: Годовой счёт; вызов в гибриде','sentence','person_cost_s20[M5,owned,both hosting].hybrid_cheapest/(requested_day*21)',f'{min(a):.2f}--{max(a):.2f}',f'{min(b):.2f}--{max(b):.2f}','cents/call','calc/out/run13/base/person_cost_s20*.csv')
    add('paper/sections/11-limitations.tex :: Замеры на клиенте пока сделаны на одной машине','sentence','admitted measured client machine count','1 (M3 Max)','2 (M3 Max and M5 Max64)','machines','calc/out/run13/measurements/client_depth.csv')
    # Architecture prose uses the native CSV's rounded values, not a new timing model.
    before=list(csv.DictReader(io.StringIO(snapshot_read('r12-architecture', 'paper/data/arch-compare.csv').decode())))
    after=read(ROOT/'paper/data/arch-compare.csv')
    a=next(r for r in before if r['model']=='Gemma 4 31B');b=next(r for r in after if r['model']=='Gemma 4 31B')
    for site,key,fmt in [('Вес дельты','delta_1k_mb',lambda v:f'{v:.0f} MB'),('На гигабите больше всех экономит','saving_1k_131k_1000mbit_s',lambda v:f'{v:.0f} s')]:
        add('paper/sections/05b-models.tex :: '+site,'sentence','arch_compare[Gemma4].'+key,fmt(float(a[key])),fmt(float(b[key])),'as printed','paper/data/arch-compare.csv')
    # The paper's ideal-client offload example uses start-depth marginal FLOPs,
    # as its own offload_bound.py does; this is not a full latency prediction.
    intensity=next(r for r in read(old/'flop_per_byte.csv') if r['model']=='Qwen3.8-27B' and r['client']=='M5 Max 128 GB' and r['state_bits']=='32' and r['depth']=='110000' and r['portion_tokens']=='10000' and float(r['link_mbit'])==1000)
    s,i=load('paper-tables-r13');c=Context(s,i);m=c.model('qwen27');srv=c.server('b300',m)
    rate=compute_at(c.g.resolve(srv['compute']).value,110000)
    oldrate=float(read(old/'turn_speedup.csv')[0]['server_compute'])
    work=float(intensity['portion_tokens'])*float(intensity['flop_new_token']);local=work/float(intensity['client_peak_flop_s'])
    for link in (1000,10000):
        transfer=float(intensity['delta_bytes'])/(link*1e6/8)
        a,b=(local/(work/p+transfer) for p in (oldrate,rate))
        add('paper/sections/05b-models.tex :: Физика выигрыша','sentence',f'offload_bound[110k,10k,{link}Mbit].local/(server+transfer)',f'{a:.1f}',f'{b:.1f}','ratio (ideal upper bound)','Context.b300.compute(110000) + flop_per_byte.csv')
    add('paper/sections/05b-models.tex :: Выше 22.5 раза','sentence','offload_bound.server_compute/client_peak',f'{oldrate/60e12:.1f}',f'{rate/60e12:.1f}','ratio','Context.b300.compute(110000)')
    add('paper/sections/05b-models.tex :: tab:intensity caption','caption','server_compute depth 110000',f'{oldrate/1e15:.2f}',f'{rate/1e15:.2f}','PFLOP/s; depth-dependent','Context.b300.compute(110000)')
    # Rent/buy narrative: comparison at 50 people and10h under each residual.
    for residual in (.2,.5,.8):
        select=lambda r:r['team']=='50' and float(r['hours'])==10 and r['option']=='1x RTX PRO 6000 Server; colocation' and float(r['residual'])==residual
        a,b=pair('remote_rent_buy',select)
        add('paper/sections/07-economics.tex :: Аренда или покупка сервера','sentence',f'remote_rent_buy[team50,10h,residual{residual}].owned/rent',float(a['owned_month'])/float(a['rent_month']),float(b['owned_month'])/float(b['rent_month']),'ratio','calc/out/run13/base/remote_rent_buy.csv')

    # Introduction's B300 example uses the integrated 10k span at the stated
    # 131k..181k depths, preserving the original model FLOP convention.
    a,b=0.00022964337804155598,3.3616439930993272e-9
    ratio=ii.get('hardware.servers.rtx1.peak')/ii.get('owners.options.b300.fp8_peak')
    values=[(a*10000+b*(d*10000+10000**2/2))*ratio for d in (131000,181000)]
    add('paper/sections/01-introduction.tex :: одна B300 читает такую порцию','sentence','B300.integral_seconds(131k..181k,10k)','about 1',f'{min(values):.1f}--{max(values):.1f}','s','server_fits[phase_a].a,b and dense peak ratio')
    fractions=[float(r['fp8_fraction'])*100 for r in read(out/'measurements/server_bulk.csv') if r['case']=='phase_a']
    add('paper/sections/01-introduction.tex :: загрузке вычислителей 30%','sentence','server_bulk[phase_a].fp8_fraction range','30',f'{min(fractions):.1f}--{max(fractions):.1f}','percent; measured envelope','calc/out/run13/measurements/server_bulk.csv')
    add('paper/sections/05b-models.tex :: tab:intensity caption; 30%','caption','server_bulk[phase_a].fp8_fraction range','30',f'{min(fractions):.1f}--{max(fractions):.1f}','percent; depth-dependent','calc/out/run13/measurements/server_bulk.csv')
    # Only the 64GB M5 is newly measured; do not generalize its curve to the
    # 128GB Max, Ultra or Air estimates when updating the four-times sentence.
    client_rows=read(out/'measurements/client_depth.csv')
    speeds=[]
    for d in (16000,50000,100000,150000,200000,249000):
        means=[]
        for client in ('M3 Max 128 GB','M5 Max 64 GB'):
            subset=[r for r in client_rows if r['client']==client and int(r['depth'])==d and int(r['delta']) in (2000,10000)]
            means.append(2/sum(1/float(r['prefill_tok_s']) for r in subset))
        speeds.append(means[1]/means[0])
    add('paper/sections/05-clients.tex :: читают контекст в четыре раза быстрее','sentence','client_depth[M5 Max64/M3,2k+10k harmonic rates].ratio range','4 (estimate)',f'{min(speeds):.2f}--{max(speeds):.2f} (M5 Max64 measured only)','ratio','calc/out/run13/measurements/client_depth.csv')


def traffic_changes(add,out):
    """Additional r2 prose derivations, appended after all reviewed r1 rows."""
    def pair(name,select):
        before=list(csv.DictReader(io.StringIO((ROOT/'paper/data/engine'/(name+'.csv')).read_text())))
        after=list(csv.DictReader(io.StringIO((out/'base'/(name+'.csv')).read_text())))
        a=[r for r in before if select(r)];b=[r for r in after if select(r)]
        assert len(a)==len(b)==1
        return a[0],b[0]
    # The traffic paragraph compares the same capacity-limited M3 user with
    # compute + hosting at s50. Its rounded USD15 denominator also changes.
    a,b=pair('person_cost_s50',lambda r:r['client'].startswith('M3') and r['basis']=='Mac already owned' and r['team']=='5')
    old_host=sum(float(a[k]) for k in ('compute_month','hosting_month'))
    new_host=sum(float(b[k]) for k in ('compute_month','hosting_month'))
    add('paper/sections/04-channel.tex :: Трафик как статья расходов','sentence','traffic.M3.s50.compute_month+hosting_month',f'{old_host:.0f}',f'{new_host:.0f}','USD/month','calc/out/run13/base/person_cost_s50.csv')
    a,b=pair('traffic_user_month',lambda r:r['profile']=='heavy')
    span=lambda row,host:f"{float(row['egress_2'])/host:.0f}--{float(row['egress_3'])/host:.0f}"
    add('paper/sections/04-channel.tex :: Трафик как статья расходов','sentence','traffic.M3.egress[50,90]/(compute_month+hosting_month)',span(a,old_host),span(b,new_host),'ratio','calc/out/run13/base/traffic_user_month.csv + person_cost_s50.csv')
