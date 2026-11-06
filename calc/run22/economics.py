"""Dedicated team economics with measured PRI31 clients and bf16 transport."""
import copy
import functools
import math

from hybridcalc.inputs import InputGap
from hybridcalc import deep_r21 as deep, measurements_r21 as r21
from hybridcalc import measurements_r20 as old, measurements_r16 as r16
from hybridcalc import measurements_r19 as r19
from .measurements import Mac, wire


class Server(deep.Server):
    def __init__(self,key,cfg=None,observations=(),decode_observations=()):
        super().__init__(key,cfg)
        self.decode_capacity={r['depth']:r['resident_limit'] for r in decode_observations if r['server']==key and r.get('resident_limit')}
        self.observations = {(r['depth'],r['delta']):r['prefill_s'] for r in observations if r['server']==key}
        self.observed_points={}
        for (depth,delta),seconds in self.observations.items():
            self.observed_points.setdefault(delta,[]).append((depth,seconds))
        for delta,points in self.observed_points.items():
            self.observed_points[delta]=sorted(dict(self.points.get(delta,[])+points).items())

    def slots(self,depth):
        model=super().slots(depth)
        return min(model,getattr(self,'decode_capacity',{}).get(depth,model))

    def observed_surface(self,depth,delta):
        # Cached timing has a launch/bridge intercept. A lone throughput point
        # cannot identify it; require both2k and10k elapsed-time curves before
        # updating other deltas. Sub2k extension remains explicitly estimated.
        points=self.observed_points
        if all(n in points and points[n][0][0]<=depth<=points[n][-1][0] for n in (2000,10000)) and 0<delta<=10000:
            from hybridcalc.measurements_r18 import interpolate
            a=interpolate(points[2000],depth);b=interpolate(points[10000],depth)
            value=a+(delta-2000)*(b-a)/8000
            if value<=0:
                raise InputGap('run22.prefill','nonpositive measured elapsed-time delta extension')
            return value
        return None

    def cached(self,depth,delta,bridge='none'):
        if bridge not in ('none','measured_envelope'):
            raise InputGap('run22.bridge','unknown bridge assumption')
        # Exact measured shapes override extrapolation; do not silently interpolate
        # a sparse512k/1M observation onto other shapes or claim a bridge speedup.
        if (depth,delta) in self.observations:
            seconds = self.observations[depth,delta]
            return max(seconds,delta*self.bridge['seconds_token']) if bridge=='measured_envelope' else seconds
        seconds=self.observed_surface(depth,delta)
        if seconds is not None:
            return max(seconds,delta*self.bridge['seconds_token']) if bridge=='measured_envelope' else seconds
        return super().cached(depth,delta,bridge)


class M5Rates:
    def __init__(self):
        self.mac = Mac()

    def prefill(self,depth):
        return 2000/self.mac.prefill(depth,2000)

    def decode(self,streams,depth):
        return self.mac.decode(streams,depth)


def mac_prefill(context,client,depth,delta):
    if client == 'm3max':
        return deep.mac_prefill(context,client,depth,delta)
    return context.measured_m5.mac.prefill(depth,delta)


class Prepared(old.Prepared):
    def __init__(self,calls,server,client,context,bridge,measurements,transport):
        self.calls=calls; self.server=server; self.client=client; self.context=context
        self.bridge=bridge; self.measurements=measurements
        self.own=[]; self.pre=[]; self.shadow=[]; self.output=[]
        self.wire=[]; self.imports=[]; self.rebuild=[]
        cl=context.client(client,'hardware.links.wan.bandwidth','r22')
        self.streams=context.g.resolve(cl['streams']).value
        self.memory=context.g.resolve(cl['memory']).value
        self.decoder=context.g.resolve(cl['decoder']).value
        self.profiles={x['key']:x for x in r19.links(context.inputs)}
        self.decode_device=[]; self.decode_occupied=[]; self.wait_weight=[]
        importer=r16.ClientImport()
        for depth,n,o,tool in calls:
            server.slots(depth+n+o)
            self.own.append(mac_prefill(context,client,depth,n))
            self.pre.append(server.cached(depth,n,bridge))
            base=server.cached(depth,n)
            self.shadow.append(base*(n+o)/n if n else server.cached(depth,o))
            self.output.append(base*o/n if n else server.cached(depth,o))
            self.wire.append(wire(n,transport) if n else 0)
            # bf16 transport does not prove a faster import. Keep the same
            # measured-depth Mac fit (extrapolated at1M) in both transport arms.
            self.imports.append(importer.at_depth(n,depth))
            self.rebuild.append(server.cold(depth))
            admissible=min(self.streams,self.memory(depth+n+o))
            k=max((k for k in (1,2,4) if k<=admissible),default=0)
            if k<1:
                raise InputGap('run22.client','complete end-of-call session does not fit')
            rate=self.decoder(k,depth+n)
            self.decode_device.append(o/(k*rate))
            self.decode_occupied.append((o/rate+tool)/k)
            self.wait_weight.append(1/k)


class Economics(old.Economics):
    def __init__(self,context,calls,servers,cfg,transport='bf16',measurements=(),reuse=None):
        plain=copy.deepcopy(cfg); plain['server_decode']={'measurements':[]}
        super().__init__(context,calls,servers,plain,{})
        self.measurements=list(measurements)
        self.transport=transport
        if reuse is not None:
            self.own_cache=reuse.own_cache; self.fleet_cache=reuse.fleet_cache; self.decode_vectors=reuse.decode_vectors
        for key,server in servers.items():
            for client in ('m5max64','m5max'):
                self.prepared[key,client,'measured_envelope']=Prepared(calls,server,client,context,'measured_envelope',self.measurements,transport)

    @functools.lru_cache(maxsize=None)
    def hybrid(self,key,team,demand,client,basis,billing,bridge):
        result=dict(super().hybrid(key,team,demand,client,basis,billing,bridge))
        if isinstance(result['person_month'],(int,float)):
            link='office_gigabit' if billing=='bought' else 'engine_wan'
            prepared=self.prepared[key,client,bridge]
            stat=prepared.stats(result['spill_share'],link)
            size=stat['wire_bytes_call']
            egress=result['served_day']*self.days*size/1e12*self.inputs.get('prices.egress') if billing=='rented' else 0
            result.update(wire_bytes_call=size,wire_transfer_s_call=size/prepared.profiles[link]['bytes_s'],egress_person_month=egress)
            result['person_month']+=egress
        else:
            result.update(wire_bytes_call='',wire_transfer_s_call='',egress_person_month='')
        return result

    def utilization(self,key,team,demand,result,kind):
        """Service occupancy bound, not hardware/SM utilization or active FLOPs."""
        if not isinstance(result['boxes'],(int,float)):
            return dict(service_utilization='',calendar_utilization='',utilization_basis='capacity-refused; utilization undefined')
        _,gpus=self.units[key,'bought']
        if kind=='hybrid':
            seconds=team*(result['prefill_gpu_s_day']+result['decode_overflow_gpu_s_day'])
        else:
            seconds=team*demand*result['gpu_s_call']
        calendar=seconds*self.days/(result['boxes']*gpus*730*3600)
        service=seconds/(result['boxes']*gpus*self.hours*3600)
        return dict(service_utilization=service,calendar_utilization=calendar,
            utilization_basis='modelled allocated-GPU service occupancy / installed GPU time; includes tool/concurrency bound in server decode, not nvidia-smi; service denominator8h/day, calendar730h/month; target<=70% service; sufficient hybrid fleet, not minimal')

    def shared(self,key,demand,client,basis,link='engine_wan'):
        """Resident-work limit on a named link; reserved state/storage separate."""
        server=self.servers[key]; prepared=self.prepared[key,client,'measured_envelope']
        stat=prepared.stats(0,link)
        served=min(demand,stat['client_capacity_day']); overflow=demand-served
        # Full shared-provider batching is a limit, not a promise of32 independent
        # streams on a dedicated small team.
        dec=self.own_stats(server,32)
        work=served*stat['gpu_s_call']+overflow*dec['seconds']
        unit,gpus=self.units[key,'rented']
        server_month=work*self.days*(unit/730/gpus)/(3600*self.load)
        p='hardware.clients.'+client
        device=0 if basis=='owned' else self.inputs.get(p+'.purchase_price')*(1-self.inputs.get('economics.client_residual'))/(12*self.inputs.get('owners.years'))
        energy=self.inputs.get(p+'.power')*self.hours*self.days*self.inputs.get('prices.energy_client')
        storage=server.session_bytes(self.cfg['reservation_depth'])*self.sessions/1e9*self.inputs.get('hosting.tiers.NVMe.price')
        egress=served*self.days*stat['wire_bytes_call']/1e12*self.inputs.get('prices.egress')
        return dict(person_month=server_month+storage+device+energy+self.inputs.get('owners.front_month')+egress,
            server_person_month=server_month,storage_person_month=storage,egress_person_month=egress,
            service_utilization=self.load,calendar_utilization=self.load,
            utilization_basis='resident shared-work/provider limit billed at70% utilization continuously; full-utilization lower bound also exported; not a dedicated-node offer',
            full_utilization_person_month=server_month*self.load+storage+device+energy+self.inputs.get('owners.front_month')+egress,
            offload_share=stat['offload_share'],served_day=served,server_decode_overflow_day=overflow)


def coverage(calls,indices,measured,profile,monthly,tier):
    inside=sum(1 for depth,n,o,t in calls if 16000<=depth and depth+n+o<=249000 and 512<=n<=10000)
    return ('{}: share of calls whose shapes lie inside the common measured ladder {}/{} ({:.2f}%); '.format(profile,inside,len(calls),100*inside/len(calls))+
        'selected {} envelope {}/{} ({:.2f}%), {}; normalized to {:g} calls/person-month; full unconditioned mix unsupported'.format(
            tier,len(indices),len(calls),100*len(indices)/len(calls),
            'all selected shapes within measured ladder, interpolation still modelled' if tier=='measured_ladder' else 'physical capacity envelope, deep rates extrapolated; this fraction is NOT measured-ladder coverage',monthly))


def intensity(load):
    return 'owner intensity2500 calls/day, atypical; light/medium are typical' if load=='heavy' else 'typical '+load+' load'
