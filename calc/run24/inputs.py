"""Final-study CSV adapter; cadence is part of each measurement's identity."""
import csv,hashlib,json,math
from functools import lru_cache
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'calc'))
from run22 import interfaces as old
from hybridcalc.inputs import InputGap

DATA=Path(__file__).parent/'data'
QWEN='qwen/qwen3.8-27b';GLM='z-ai/glm-5.3-flash'
CADENCES={('v1','v1'):'v1_long_pause',('amendment','core'):'amendment_core',('amendment','long'):'amendment_long'}


def read(name):
    with (DATA/(name+'.csv')).open(newline='')as f:return list(csv.DictReader(f))


def checked():
    info=json.loads((DATA/'evidence.json').read_text())
    for name,record in info['files'].items():
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==record['sha256'],'changed API source '+name
    doc=json.loads((DATA/'analysis.json').read_text())
    assert doc['window_final']is True and not doc['smoke_used_for_cache']and not doc['seed_calls_used_for_cache'],'final no-smoke/no-seed study required'
    assert old.date(doc['window_start'])<old.date(doc['window_observed_through'])<old.date('2026-11-05T12:00:00Z'),'invalid RC4 observation window'
    return doc


@lru_cache(maxsize=1)
def raw():return json.loads((DATA/'accepted-rows.json').read_text())


@lru_cache(maxsize=1)
def attempts():return json.loads((DATA/'call-rows.json').read_text())


def native_key(provider):return provider['model'],provider['provider'].split(' / ')[1]


def warm_rows(model,tag,phase,cohort,profile):
    return [r for r in raw()if r.get('model')==model and r.get('endpoint_tag')==tag and r.get('phase')==phase and r.get('cohort')==cohort
        and r.get('call_index',0)>0 and isinstance(r.get('cached_tokens'),(int,float))and isinstance(r.get('prompt_tokens'),(int,float))
        and (profile!='million'or r.get('depth')==1000000)]


def materialized(doc=None):
    doc=checked()if doc is None else doc;cache=[];availability=[];prices=[]
    for provider in doc['providers']:
        model,tag=native_key(provider);window=provider['whole_window_availability']
        if window['attempts']:
            availability.append(dict(model=model,tag=tag,availability_percent=100*window['successes']/window['attempts'],
                attempts=window['attempts'],successes=window['successes'],errors=window['errors'],timeouts=window['timeouts'],
                window_start=doc['window_start'],window_end=doc['window_observed_through'],source='analysis.json:whole_window_availability'))
        for (phase,cohort),cadence in CADENCES.items():
            summary=provider['phases'].get(phase,{}).get(cohort)
            if not summary:continue
            for profile in ('existing_combined','claude_deep','million'):
                rows=warm_rows(model,tag,phase,cohort,profile)
                if not rows:continue
                total=sum(r['prompt_tokens']for r in rows);cached=sum(r['cached_tokens']for r in rows)
                target=summary if profile!='million'else provider['million_by_phase'][phase]
                assert len(rows)==target['accepted']and math.isclose(cached/total,target['token_hit_rate'],rel_tol=0,abs_tol=1e-12),'raw accepted rows disagree with final cache aggregate'
                series=[r for r in attempts()if r.get('model')==model and r.get('endpoint_tag')==tag and r.get('phase')==phase and r.get('cohort')==cohort and (profile!='million'or r.get('depth')==1000000)]
                # All final-study warm points remain descriptive, including the
                # explicitly thin1/2-warm-call observations. This is not Chutes'
                # excluded exploratory three-call smoke or a broad certification.
                record=dict(model=model,tag=tag,profile=profile,cadence=cadence,input_tokens=total,cached_tokens=cached,
                    series_calls=len(series),warm_calls=len(rows),observed_at=doc['window_observed_through'],
                    source='accepted-rows.json + analysis.json final accepted study, phase='+phase+', cohort='+cohort,
                    study_usd_per_1000=target['effective_usd_per_1000_measured_depth_mix'],
                    study_depth_mix=json.dumps(target['measured_depth_mix_counts'],sort_keys=True,separators=(',',':')),
                    sample_basis='thin descriptive final-study point; no provider-wide confidence claim'if len(rows)<=2 else'final repeated study series',
                    continuation_flagged_warm_calls=sum(bool(r.get('resumed_cell'))for r in rows),
                    interrupted_cell_warm_calls=(target.get('cadence_subsets',{}).get('resumed_cells')or{}).get('accepted',''),
                    resume_boundaries=sum(bool(r.get('resume_boundary'))for r in rows))
                cache.append(record)
                price_rows=[r['pricing']for r in rows if r.get('pricing')]
                assert len(price_rows)==len(rows),'missing live-price evidence for normalized cache point'
                # Match the run22 aggregate-token tariff model. Study-native
                # prices retain their own1065-new/512-output conservative formula.
                prices.append(dict(model=model,tag=tag,profile=profile,cadence=cadence,
                    prompt=sum(float(p['prompt'])for p in price_rows)/len(rows),
                    completion=sum(float(p['completion'])for p in price_rows)/len(rows),
                    input_cache_read=sum(float(p['input_cache_read'])for p in price_rows)/len(rows),
                    input_cache_write=sum(float(p.get('input_cache_write',p['prompt']))for p in price_rows)/len(rows),
                    source='arithmetic mean of per-call live tariffs in the same final warm cohort; run22 expected aggregate-token tariff model'))
    return cache,availability,prices


def write_csv(name,rows):
    with (DATA/(name+'.csv')).open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def materialize():
    cache,availability,prices=materialized()
    for name,rs in [('provider_cache',cache),('provider_availability',availability),('provider_prices',prices)]:write_csv(name,rs)
    print('final data-only CSVs',len(cache),len(availability),len(prices))


def load():
    doc=checked();known={native_key(p)for p in doc['providers']}
    avail,window=old.availability_rows(read('provider_availability'),known)
    cache={};prices={};records=read('provider_cache')
    for row in records:
        old.provenance(row);key=(row['model'],row['tag'],row['profile'],row['cadence'])
        if key in cache or row['cadence']not in CADENCES.values():raise InputGap('run24.cache','unique explicit final cadence required')
        total=old.number(row['input_tokens'],'input_tokens');hits=old.number(row['cached_tokens'],'cached_tokens',True)
        assert hits<=total and float(row['warm_calls'])>=1,'invalid accepted token evidence'
        if int(row['series_calls'])>3:
            fraction=old.cache_rows([row],known)[key[:3]]
        else:
            assert row['sample_basis'].startswith('thin descriptive final-study'),'thin point must remain labelled'
            fraction=hits/total
        cache[key]=dict(row,hit=fraction)
    for row in read('provider_prices'):
        key=(row['model'],row['tag'],row['profile'],row['cadence']);assert key in cache and key not in prices
        prices[key]={k:old.number(row[k],k,True)for k in ('prompt','completion','input_cache_read','input_cache_write')}
    expected=materialized(doc)
    for actual,native in zip((records,read('provider_availability'),read('provider_prices')),expected):
        assert actual==[{k:str(v)for k,v in row.items()}for row in native],'CSV adapter differs from final accepted raw study'
    return dict(doc=doc,cache=cache,availability=avail,window=window,prices=prices)


if __name__=='__main__':materialize()
