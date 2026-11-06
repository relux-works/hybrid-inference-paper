"""Report/quote publication for the final-study API overlay."""
import argparse,csv,hashlib,io,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'calc'))
from run24 import export,inputs,api
OUT=export.OUT;REPORT=ROOT/'calc/ENGINE-REPORT-R24-261105.md';QUOTES=ROOT/'calc/ENGINE-REPORT-QUOTES-R24-261105.csv'
VALIDATION=ROOT/'calc/R24-VALIDATION-261105.json';MANIFEST=ROOT/'calc/R24-REPORT-MANIFEST-261105.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def build():
    cache={};records=[]
    def rows(name):
        if name not in cache:cache[name]=export.read(OUT/name)
        return cache[name]
    def match(name,**conditions):
        found=[(i,r)for i,r in enumerate(rows(name))if all(r.get(k)==str(v)for k,v in conditions.items())]
        assert len(found)==1,(name,conditions,len(found));return found[0]
    def q(name,index,column,fmt=None):
        raw=rows(name)[index][column];rendered=raw.rstrip()if column.endswith('sentence')else raw
        if raw=='':rendered='unknown'
        elif fmt:rendered=fmt(float(raw))
        records.append(dict(site='report quote '+str(len(records)+1),source='calc/out/run24/'+name,row=index,column=column,source_value=raw,rendered=rendered))
        return rendered
    money=lambda v:format(v,'.3f');pct=lambda v:format(100*v,'.2f')+'%'
    lines=['# Engine run24 — measured API cache and availability for RC4','',
        'Base: accepted run23 `9064701a9a07bd2726f76cefb6a05aa6aa428c0d`, Muse r5x5 ACCEPT. RC4 data cutoff: 2026-11-05 12:00Z. API-only successor: hardware/client costs, bf16 default/f32 control, PRO decode, 1M routing, dedicated-primary policy and the historical bought-office headlines retain their run23 bases. No server/client performance has been re-estimated.','',
        '## Final evidence and cadence','',
        'Whole study window: **2026-11-03 14:39:44.389926Z to 2026-11-04 07:22:22.114713Z**. Availability is request-sampled over that same whole window, including seeds, errors and timeouts; it is not continuous uptime. Every attempted endpoint below 95% is excluded, including endpoints whose core cache rate is high. Never-attempted Qwen endpoints retain the labelled October29 snapshot last1d basis; missing availability remains unverified. The old GLM research summary retained neither cache declarations nor uptime and cannot qualify a provider from tariff alone; it is not used as a GLM fallback. Final-study inventory/live evidence establish GLM points, with unattempted availability/prices unverified. No rolling window is substituted for a measured endpoint.','',
        'Copied read-only inputs and full SHA256s are in `calc/run24/data/evidence.json`: final API report **2485e7f2dd8c961deeeca95a36eac88a95b71b2c56f9760e40e99a129160d9f6**, `analysis.json`, `accepted-rows.json` and `call-rows.json`. The adapter checks exact integer token sums against the final aggregates. Failed seeds count as attempts; their tokens never become cache evidence. The entire Chutes smoke and every first call are excluded from cache inference.','',
        '**v1_long_pause** is the multi-depth v1 cadence with long/late pauses. **amendment_core** is the short-gap amendment, with interrupted cells retained and labelled. Both remain separate. The core phase aggregate is not silently replaced by its better uninterrupted subset. `api_cadence_subsets.csv` retains uninterrupted, interrupted-cell and continuation-only source values; continuation flags and full interrupted-cell counts are separately retained in the CoreWeave core arm. No long stop gap is called an 8s/35s TTL result.','',
        'The final study includes thin observations with only one or two accepted warm calls. They remain descriptive points, with their sample size in tables and sentences; no provider-wide confidence claim follows. Low measured hits are priced, never excluded. Missing hits stay unknown. Cheapest and upper-middle median mean the admitted **PRICEABLE cohort at the stated cadence**; unmeasured admitted providers remain in the inventory, so the measured ranking does not establish a global cheapest API.','',
        '## API points on the same paper workload','',
        'The following prices use the combined-agent measured-shape subset: 10885/39904 calls (27.28%) whose shapes lie inside the measured ladder, normalized to 1000 calls. This covers call shapes, not a quarter of work or tokens; the full unconditioned mix is unsupported. Both models use those same input/output means for this price comparison. GLM prices are an API reference, not a claim that the Qwen hybrid runs GLM. The Claude profile and physical-envelope sensitivity are separately exported.','',
        'Paper normalization follows the run22 expected aggregate-token tariff formula, using the measured cadence-specific cached fraction and arithmetic mean of that warm cohort’s per-call live tariffs. Transferring a measured fraction across depth/workload mixes is an assumption. The source study’s USD/1000 is retained separately: its own depth mix, 1065 new input/512 output projection and conservative write-surcharge convention differ from the paper profile. Neither is presented as a raw sixteen-output-token bill.','',
        '| Model | Cadence | Cache point | Cheapest admitted priceable endpoint / USD per1000 | Upper-middle endpoint / USD per1000 | Priceable / admitted |',
        '|---|---|---|---|---|---|']
    for model in (inputs.QWEN,inputs.GLM):
        for cadence in ('v1_long_pause','amendment_core'):
            for point in ('no_cache','owner_981','measured'):
                args=dict(model=model,profile='existing_combined',scope_tier='measured_ladder',cadence=cadence,cache_point=point)
                ci,c=match('api_rankings.csv',**args,role='cheapest');mi,m=match('api_rankings.csv',**args,role='median')
                lines.append('| '+model+' | '+cadence+' | '+point+' | '+q('api_rankings.csv',ci,'provider')+' / '+q('api_rankings.csv',ci,'usd_per_1000_calls',money)+' | '+q('api_rankings.csv',mi,'provider')+' / '+q('api_rankings.csv',mi,'usd_per_1000_calls',money)+' | '+q('api_rankings.csv',ci,'cohort_size')+' / '+q('api_rankings.csv',ci,'admitted_count')+' |')
    lines+=['', 'Qwen’s core Phala observation is excluded by whole-window availability, so no qualified measured Qwen core point or finite core crossing exists. It is never backfilled with v1 or snapshot cache data. The measured Qwen v1 minimum is explicitly thin; the endpoint source table below supplies its warm-call count. The no-cache and owner98.1% rows are scenarios rather than provider cache verdicts. They use same-cohort live tariffs when available; retained Qwen snapshot tariffs are labelled otherwise. GLM has no qualified research-summary tariff fallback, so its side points use the same live-price cohort as its measured point. Inventory/cohort/tariff bases are stated in every export.','',
        '## Source endpoint prices and sample sizes','',
        'These are source-native projections at each endpoint’s measured depth mix. They must not replace the normalized same-shape prices above. Different native depth mixes prevent reading this table as a like-for-like provider ranking. Whole-window exclusions remain visible alongside their observed cache measurements.','',
        '| Model / endpoint | Cadence | Warm calls | Cached input fraction | Source USD per1000 | Admission |', '|---|---|---:|---:|---:|---|']
    for i,r in enumerate(rows('api_native_study.csv')):
        lines.append('| '+r['model']+' / '+r['tag']+' | '+r['cadence']+' | '+q('api_native_study.csv',i,'warm_calls')+' | '+q('api_native_study.csv',i,'cache_hit_fraction',pct)+' | '+q('api_native_study.csv',i,'study_usd_per_1000',money)+' | '+q('api_native_study.csv',i,'admitted')+' |')
    lines+=['', '## Million-token measured API point','',
        'The pooled source figure combines restarted-v1 multi-pause and amendment core cadence, excludes independent probe/long substudy, and gives each qualified provider equal weight. Its 1065-new/512-output projection is distinct from the fixed-depth paper normalization in `api_rankings.csv`. Snapshot Qwen1M references remain historical labelled controls, not measured providers. Hybrid/client model-card YaRN stays required; provider context extension is unknown and is not claimed identical.','',
        '| Model | Alibaba variant | Cadence | Qualified measured providers | Pooled source USD per1000 | Verdict |', '|---|---|---|---:|---:|---|']
    for i,r in enumerate(rows('million_measured.csv')):
        lines.append('| '+r['model']+' | '+r['variant']+' | '+r['cadence']+' | '+q('million_measured.csv',i,'qualified_providers')+' | '+q('million_measured.csv',i,'usd_per_1000_calls',lambda v:format(v,'.2f'))+' | '+r['verdict']+' |')
    lines+=['', '## Dedicated and shared comparisons at the measured point','',
        'Primary selection below: bought RTX PRO6000 vLLM FP8 office server, 125 MB/s RTT1 ms assumed; owned PRI31 M5 Max64 GB; s=20%; bf16; identical combined-agent measured call shapes, normalized to840/3360/10500 calls per person-month at light/medium/heavy load. Light200/day and medium800/day are typical; heavy2500/day is the owner’s intensity. Dedicated hardware costs and utilization are inherited from run23. Fleets remain sufficient, not proved minimal.','',
        'The old owner98.1%/snapshot headline is a frozen control. The new measured point changes cache, availability, price evidence and the priceable cohort together; the crossing difference is not a causal cache-only effect. GLM API-versus-Qwen hybrid price-reference rows are separately labelled in root exports and excluded from paper hybrid-claim tables. No GLM hybrid performance is invented.','',
        '| Load / API role | Historical owner98.1% snapshot control | Measured v1 long-pause comparison | At50: API/hybrid | Dedicated service / calendar utilization |', '|---|---|---|---:|---:|']
    common=dict(profile='existing_combined',scope_tier='measured_ladder',transport='bf16',share=.2,client='m5max64',basis='owned',server='pro6000_fp8',billing='bought',api_model=inputs.QWEN,cadence='v1_long_pause')
    for load in ('light','medium','heavy'):
        for role in ('cheapest','median'):
            args=dict(common,load=load,api_role=role);ci,c=match('measured_crossings.csv',**args);mi,m=match('measured_multiples.csv',**args)
            lines.append('| '+load+' / '+role+' | '+q('measured_crossings.csv',ci,'historical_owner_981_statement')+' | '+q('measured_crossings.csv',ci,'statement')+' | '+q('measured_multiples.csv',mi,'api_over_hybrid',money)+' | '+q('measured_multiples.csv',mi,'service_utilization',pct)+' / '+q('measured_multiples.csv',mi,'calendar_utilization',pct)+' |')
    lines+=['', 'The shared resident-work comparison is a supplementary allocation limit on the shared engine WAN112.5 MB/s RTT400 ms estimated, at the inherited70% continuous occupancy. It is a constant per-person allocation, not a dedicated-team fleet promise. Night agents may raise real utilization; the dedicated bought/rented basis remains primary.','',
        '| Load / API role | Shared allocation comparison, v1 | API/hybrid |', '|---|---|---:|']
    for load in ('light','medium','heavy'):
        for role in ('cheapest','median'):
            i,r=match('shared_measured_crossings.csv',**dict(common,billing='shared_work',load=load,api_role=role))
            lines.append('| '+load+' / '+role+' | '+q('shared_measured_crossings.csv',i,'statement')+' | '+q('shared_measured_crossings.csv',i,'api_over_hybrid',money)+' |')
    lines+=['', '## Words-ready measured-point conclusions','',
        'Each sentence carries its billing/link/rate/RTT/location, client, share, cadence, cache point/fraction, load, coverage, transport, API admission window, measured-cohort limit and sample size. The canonical form is beside the short form in the paper CSVs.','']
    for profile in ('existing_combined','claude_deep'):
        for load in ('light','medium','heavy'):
            for role in ('cheapest','median'):
                i,r=match('paper/measured_crossings.csv',**dict(common,profile=profile,load=load,api_role=role))
                lines.append('- '+q('paper/measured_crossings.csv',i,'short_sentence'))
        i,r=match('paper/measured_crossings.csv',**dict(common,profile=profile,cadence='amendment_core',load='medium',api_role='median'))
        lines.append('- '+q('paper/measured_crossings.csv',i,'short_sentence'))
    lines+=['', '## Changed against run23 — every abstract-bound coordinate','',
        'All source coordinates quoted in the accepted run23 report are listed, including text-valued sentences that carry numbers, including its historical audit coordinates. They remain inherited controls byte-for-byte. Newly available measured ranks and primary crossing comparisons are added with their distinct cadence/cache/admission/cohort basis; an unknown old measured point is never made numeric. Full source addresses and why are in `abstract_bound_changes.csv`. These audit addresses are not standalone paper sentences.','',
        '| Old source:row / column | Old | New | Why |','|---|---|---|---|']
    for i,r in enumerate(rows('abstract_bound_changes.csv')):
        lines.append('| '+r['old_source']+':'+r['old_row']+' / '+r['column']+' | '+q('abstract_bound_changes.csv',i,'old')+' | '+q('abstract_bound_changes.csv',i,'new')+' | '+r['why']+' |')
    lines+=['', '## Gates and limits','']
    if VALIDATION.exists():
        v=json.loads(VALIDATION.read_text());lines += [v['summary'],'','| Mutant | Bound | Named failing test |','|---|---|---|']
        for m in v['mutants']:lines.append('| '+m['name']+' | '+m['bound']+' | `'+m['test']+'` |')
        lines+=['',v['attempts'],'',v['resources']]
    else:lines+=['Validation pending; this draft is not a review handoff.']
    lines+=['', 'No new API request, GPU/Mac benchmark, download or native build was performed. Thin cache samples, transferred depth-mix fractions, partial measured cohorts, request-sampled availability, unknown API context extension, unmeasured GLM hybrid performance and the inherited deep server/recovery assumptions remain explicit limits. No supplied attack-surface table (brief gap). New performance/quality certification and continuous-uptime inference are outside this API-data-only task.']
    return '\n'.join(lines)+'\n',records


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audit-only',action='store_true');args=p.parse_args()
    export.verify();text,records=build()
    if not args.audit_only:
        REPORT.write_text(text);QUOTES.write_bytes(export.csv_bytes(records))
        MANIFEST.write_bytes(export.encoded(dict(policy_sha256=sha(Path(__file__)),test_sha256=sha(ROOT/'calc/tests/test_r24_report.py'),
            numerical_manifest_sha256=sha(OUT/'r24_manifest.json'),files={str(p.relative_to(ROOT)):sha(p)for p in (REPORT,QUOTES,VALIDATION)if p.exists()})))
    assert REPORT.read_text()==text,'changed report quotation'
    assert export.read(QUOTES)==[{k:str(v)for k,v in r.items()}for r in records],'missing/changed report quote'
    m=json.loads(MANIFEST.read_text());assert m['policy_sha256']==sha(Path(__file__))and m['test_sha256']==sha(ROOT/'calc/tests/test_r24_report.py'),'stale report policy/test'
    assert m['numerical_manifest_sha256']==sha(OUT/'r24_manifest.json'),'changed numerical manifest'
    assert set(m['files'])=={str(p.relative_to(ROOT))for p in (REPORT,QUOTES,VALIDATION)if p.exists()},'report manifest file set'
    assert all(sha(ROOT/n)==h for n,h in m['files'].items()),'changed report artifact'
    print('report quotes',len(records),'exit0')


if __name__=='__main__':main()
