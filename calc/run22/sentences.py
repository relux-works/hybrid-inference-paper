"""Self-contained RC4 quotations, with parsable long and compact forms."""
import re

SERVERS = {'pro6000_fp8':'RTX PRO 6000 vLLM FP8', 'b300_fp8':'B300 vLLM FP8',
           'b300_fp8_kv':'B300 vLLM FP8/FP8-KV'}
LINKS = {'bought':'office 125 MB/s RTT 1 ms assumed',
         'rented':'rented WAN 112.5 MB/s RTT 400 ms estimated',
         'shared_work':'shared engine WAN 112.5 MB/s RTT 400 ms estimated',
         'shared_office':'office 125 MB/s RTT 1 ms assumed'}
FIELDS = ('server','billing','link','client','s','cache allowance','load','coverage','transport','API availability')


def clauses(row):
    return dict(server=SERVERS[row['server']],billing=row['billing'],link=LINKS[row['billing']],
        client=('M5 Max 64 GB' if row['client']=='m5max64' else 'M5 Max 128 GB same-SoC portability estimate')+' '+row['basis'],
        s=str(row['share']), **{'cache allowance':row['cache_basis'],
        'load':row['load']+' '+str(row['full_calls_day'])+' calls/day '+row['intensity_basis'],
        'coverage':row['workload_scope'],'transport':row['transport']+(' default' if row['transport']=='bf16' else ' control'),
        'API availability':row.get('api_window_basis','snapshot last1d availability,95% threshold')})


def sentence(row,claim,short=False):
    c=clauses(row)
    conditions='; '.join(k+'='+c[k] for k in FIELDS)
    # The compact form retains every numerical condition; neither form relies
    # on a report footnote for the server, billing, link or coverage meaning.
    return (claim+' ('+conditions+').' if short else conditions+'; '+claim+'.')


def parse(text):
    out={}
    for name in FIELDS:
        match=re.search(r'(?:^|[;(] ?)' + re.escape(name)+r'=([^;]+)',text)
        if not match:
            raise AssertionError('missing sentence condition: '+name)
        out[name]=match[1].rstrip(').') if name=='transport' else match[1]
    assert out['server'] in SERVERS.values(),'sentence server'
    assert out['billing'] in LINKS,'sentence billing'
    assert out['link']==LINKS[out['billing']],'sentence link/rate/RTT/location'
    assert 0<float(out['s'])<=1,'sentence s'
    assert 'calls/day' in out['load'] and ('typical' in out['load'] or 'owner intensity' in out['load']),'sentence intensity'
    assert 'share of calls whose shapes lie inside the common measured ladder' in out['coverage'],'sentence coverage meaning'
    # Coverage has semicolons, so check normalization in the entire sentence.
    assert re.search(r'normalized to [0-9.]+ calls/person-month',text),'sentence normalization'
    assert re.search(r'\d+/\d+ \([\d.]+%\)',out['coverage']),'sentence coverage counts'
    assert out['transport'] in ('bf16 default','f32 control'),'sentence transport'
    assert any(word in out['cache allowance'] for word in ('98.1%','no cache','measured','pending')),'sentence cache allowance'
    return out


def validate(text,row):
    out=parse(text); expected=clauses(row)
    # Coverage includes multiple semicolon clauses. Its complete row value must
    # be present, beyond the parser's first clause.
    for name in FIELDS:
        assert name+'='+expected[name] in text,'sentence disagrees with row: '+name
    validate_numbers(text,row)
    return out


def validate_numbers(text,row):
    if row.get('person_month') not in (None,'','nan'):
        cost=float(row['person_month'])
        assert '${:.2f}/person-month'.format(cost) in text,'sentence price disagrees with row'
        if row['billing'] in ('bought','rented'):
            assert 'service utilization {:.2%}'.format(float(row['service_utilization'])) in text,'sentence utilization disagrees with row'
    if row.get('from_people') not in (None,'','nan') and not isinstance(row['from_people'],dict):
        assert 'from '+str(int(float(row['from_people'])))+' people' in text,'sentence crossing disagrees with row'
    if row.get('api_median_over_hybrid') not in (None,'','nan'):
        assert 'API/hybrid {:.3f}'.format(float(row['api_median_over_hybrid'])) in text,'sentence median multiple disagrees with row'
    if row.get('api_cheapest_over_hybrid') not in (None,'','nan'):
        assert 'and {:.3f} cheapest({})'.format(float(row['api_cheapest_over_hybrid']),row['api_cheapest_provider']) in text,'sentence cheapest multiple/provider disagrees with row'


def short_sentence(row,claim):
    """r5x3's human profile/result header followed by complete prose conditions."""
    human='Combined-agent' if row['profile']=='existing_combined' else 'Claude Code reconstructed'
    human+=' measured-shape subset' if row['scope_tier']=='measured_ladder' else ' physical-envelope sensitivity'
    where={'bought':'Bought office','rented':'Rented WAN','shared_work':'Shared engine-WAN resident-work limit','shared_office':'Shared office resident-work limit'}[row['billing']]
    rate,rtt=(125,1) if row['billing'] in ('bought','shared_office') else (112.5,400)
    c=clauses(row)
    return ('{}, {} load: {} hybrid: {}. {} server ({} MB/s, RTT {} ms); {}; s={}; {}; '.format(
        human,row['load'],c['server'],claim,where,rate,rtt,c['client'],row['share'],short_cache(row))+
        '{} calls/day ({}); {}; {} transport; {}.'.format(row['full_calls_day'],row['intensity_basis'],short_scope(row),
        c['transport'],'shared resident-work lower bound, zero residency misses' if row['billing'].startswith('shared') else 'dedicated fleet sufficient, not minimal')+
        ' API: '+short_api_window(row)+'. PRI31 Mac anchors, interpolation; deep rates/import estimated; server decode modelled unless measured CSV overrides.')


def short_api_window(row):
    basis=row.get('api_window_basis','snapshot last1d availability,95% threshold')
    if basis.startswith('measured common window'):
        return basis
    return 'snapshot29 Oct last1d, >=95% (exact window endpoints unknown)'


def short_scope(row):
    scope=row['workload_scope']
    measured=re.search(r'measured ladder (\d+/\d+ \([0-9.]+%\))',scope)
    monthly=re.search(r'normalized to ([0-9.]+) calls/person-month',scope)
    assert measured and monthly,'short form requires scoped measured-shape counts and normalization'
    text='call shapes inside measured ladder '+measured[1]
    if row['scope_tier']!='measured_ladder':
        selected=re.search(r'physical_extended envelope (\d+/\d+ \([0-9.]+%\))',scope)
        assert selected,'physical sensitivity requires selected-envelope counts'
        text+=', physical envelope '+selected[1]+' uses deep estimates'
    return text+' at '+monthly[1]+' calls/person-month, full unconditioned mix unsupported'


def short_cache(row):
    text=row['cache_basis']
    if text.startswith('98.1%'):
        return '98.1% cache allowance (1.9% misses billed, provider unverified)'
    if text.startswith('no cache'):
        return 'no cache allowance (all input billed)'
    return text+' cache allowance'


def validate_short(text,row):
    """Parse the prose conditions independently; exact row fragments bind values."""
    c=clauses(row)
    where={'bought':'Bought office','rented':'Rented WAN','shared_work':'Shared engine-WAN resident-work limit','shared_office':'Shared office resident-work limit'}[row['billing']]
    rate,rtt=(125,1) if row['billing'] in ('bought','shared_office') else (112.5,400)
    patterns={'server':c['server']+' hybrid:','billing':where+' server',
              'link':'server ({} MB/s, RTT {} ms)'.format(rate,rtt),'client':c['client']+';',
              's':'s='+str(row['share'])+';','cache allowance':short_cache(row)+';',
              'load':str(row['full_calls_day'])+' calls/day ('+row['intensity_basis']+')',
              'coverage':short_scope(row),'transport':c['transport']+' transport',
              'API availability':'API: '+short_api_window(row)}
    for name,fragment in patterns.items():
        assert fragment in text,'missing or changed short sentence condition: '+name
    assert row['load']+' load:' in text,'short sentence load'
    assert 'calls/person-month' in text,'short sentence normalization'
    validate_numbers(text,row)
    return True
