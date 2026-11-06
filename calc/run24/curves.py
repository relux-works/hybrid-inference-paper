"""Replay unchanged run23 costs once; cache full1..500 series for API repricing."""
import copy,csv,gzip,hashlib,json,math,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
from run23 import engine as r23,economics as e,inputs
from run23.export import source_identity as baseline_identity
import history_evidence as history
from hybridcalc import deep_r21 as deep,measurements_r21 as r21,server_economics_r20 as s

CACHE=Path(__file__).parent/'data/cost-curves.json.gz'
KEYS=('profile','scope_tier','transport','load','share','client','server','billing')


def read(name):
    with (ROOT/'calc/out/run23'/name).open(newline='')as f:return list(csv.DictReader(f))


def key(row):return tuple(str(row[k])for k in KEYS)


def published():
    return {(key(row),int(row['team'])):row for name in ('small_team_cost.csv','main_economics.csv')for row in read(name)if row['basis']=='owned'}


def assert_sample(base,team,result,known):
    row=known[key(base),team]
    for field in ('person_month','boxes','spill_share','served_day','offload_share','client_capacity_day','server_decode_overflow_day'):
        actual=result[field];old=row[field]
        if isinstance(actual,dict):assert old=='nan',('capacity differs',base,team,field)
        else:assert float(old)==actual,('run23 sample changed',base,team,field,old,actual)


def build():
    identity=baseline_identity();source=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    c=r23.context();cfg=deep.config();stats=deep.checked_stats(cfg)
    original=c.g.resolve(c.valid).value;bc=s.config();bc['servers']={k:bc['servers'][k]for k in deep.SERVERS}
    servers={k:e.Server(k,bc)for k in deep.SERVERS};known=published();curves=[];samples=0
    profiles=(('existing_combined',original),('claude_deep',deep.reconstruct(stats['agents']['claude'],cfg['quadrature_points'],cfg['active_gap_cap_s'])))
    for profile,calls in profiles:
        measured=[i for i,(d,n,o,t)in enumerate(calls)if 16000<=d and d+n+o<=249000 and 512<=n<=10000]
        for tier in ('measured_ladder','physical_extended'):
            end=min(deep.LIMIT,min((sv.free-sv.state)/sv.kv for sv in servers.values()))
            indices=measured if tier=='measured_ladder'else[i for i,(d,n,o,t)in enumerate(calls)if d+n+o<=end]
            selected=[calls[i]for i in indices];pc=copy.deepcopy(bc)
            pc['reservation_depth']=r21.profile_reservation(selected,249000 if tier=='measured_ladder'else cfg['reservation_depth'],servers)
            reuse=None
            for transport in ('bf16','f32'):
                econ=e.Economics(c,selected,servers,pc,transport,(),reuse);reuse=econ
                for load in ('light','medium','heavy'):
                    for share in (.2,.5,1.):
                        demand=c.inputs.get('service.profiles.'+load)*share
                        for client in ('m5max64','m5max'):
                            for server in deep.SERVERS:
                                for billing in ('bought','rented'):
                                    base=dict(profile=profile,scope_tier=tier,transport=transport,load=load,share=share,client=client,server=server,billing=billing)
                                    prices=[];fractions=[]
                                    for team in range(1,501):
                                        result=econ.hybrid(server,team,demand,client,'owned',billing,'measured_envelope')
                                        price=result['person_month'];prices.append(price if isinstance(price,(int,float))else None)
                                        fraction=result.get('offload_share')
                                        if isinstance(fraction,(int,float)):fractions.append(fraction)
                                        if team in (3,5,10,20,50,500):assert_sample(base,team,result,known);samples+=1
                                    curves.append(dict(base,prices=prices,offload_share_min=min(fractions,default=None),offload_share_max=max(fractions,default=None)))
                print('cached unchanged run23 cost series',profile,tier,transport,flush=True)
    assert baseline_identity()==identity and hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==source,'calculation source changed'
    document=dict(base='9064701a9a07bd2726f76cefb6a05aa6aa428c0d',calculation=identity,curve_source_sha256=source,scan_max=500,
        sample_controls=samples,curves=curves,basis='unchanged run23 Qwen hybrid costs; API-only overlays use these exact native full1..500 series; no interpolation of team costs')
    raw=(json.dumps(document,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    with CACHE.open('wb')as f:
        with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(raw)
    print('cache curves',len(curves),'sample controls',samples,'compressed bytes',CACHE.stat().st_size,flush=True)


def load():
    document=json.loads(gzip.decompress(CACHE.read_bytes()))
    assert document['calculation']==history.accepted_identity('ca7f228acd789380bf46016fd87acc33e1b07aef',baseline_identity()),'stale cost calculation inputs'
    assert document['curve_source_sha256']==history.historical_code_hash('calc/run24/curves.py'),'changed curve replay policy'
    assert document['scan_max']==500 and len(document['curves'])==864,'incomplete team grid'
    known=published();samples=0
    for curve in document['curves']:
        assert len(curve['prices'])==500
        for team in (3,5,10,20,50,500):
            old=known[key(curve),team]['person_month'];new=curve['prices'][team-1]
            assert (old=='nan'and new is None)or(float(old)==new),'cache sample changed'
            samples+=1
    assert samples==document['sample_controls']
    return document


if __name__=='__main__':build()
