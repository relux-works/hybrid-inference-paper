"""Declared queue/storage sensitivity; accepted run24 calculations are controls."""
import bisect
import json
import math
from pathlib import Path

from hybridcalc.inputs import InputGap

DATA = Path(__file__).parent


def config():
    return json.loads((DATA / 'config.json').read_text())


def storage(server, depth, team, nodes, case, sessions=4):
    # Integer complete-copy packing per node; GPU slots are transient, not storage.
    size = server.session_bytes(depth)
    capacity = case['ram_bytes'] if case['tier'] == 'RAM' else case['nvme_bytes']
    per_node = math.floor(capacity / size)
    required = math.ceil(team * sessions)
    fit = per_node * nodes
    return dict(copy_bytes=size, retained_copies=required, copies_per_node=per_node,
                storage_capacity_copies=fit, storage_shortfall_copies=max(0, required-fit),
                storage_min_nodes=math.ceil(required/per_node) if per_node else None,
                ram_bytes_node=case['ram_bytes'], nvme_bytes_node=case['nvme_bytes'],
                feasible=fit >= required)


def mg1(arrivals_s, first, second, nodes):
    """Exact mean for the DECLARED independent randomly split M/G/1 proxy."""
    if nodes < 1 or arrivals_s < 0 or first < 0 or second < first*first-1e-8:
        raise InputGap('run25.queue', 'invalid queue moments or fleet')
    rate = arrivals_s / nodes
    rho = rate*first
    return rho, rate*second/(2*(1-rho)) if rho < 1 else math.inf


def intervals(values):
    result = []; start = None
    for team, valid in enumerate(list(values)+[False], 1):
        if valid and start is None:
            start = team
        if not valid and start is not None:
            result.append([start, team-1]); start = None
    return result


def reweight(calls, targets):
    """Maximum-entropy delta/output moment fit; no deep-context reconstruction."""
    # Scaling keeps a simple two-dimensional Newton solve numerically stable.
    means = [sum(x[j] for x in calls)/len(calls) for j in (1, 2)]
    features = [(x[1]/means[0], x[2]/means[1]) for x in calls]
    target = [targets[i]/means[i] for i in range(2)]
    beta = [0., 0.]
    def at(b):
        scores = [b[0]*a+b[1]*c for a,c in features]; offset = max(scores)
        w = [math.exp(v-offset) for v in scores]; total = sum(w)
        w = [v/total for v in w]
        m = [sum(p*x[j] for p,x in zip(w,features)) for j in range(2)]
        error = sum((a-b)**2 for a,b in zip(m,target))
        return w, m, error
    for _ in range(100):
        w, m, err = at(beta)
        if err < 1e-16:
            return w
        a = sum(p*(x[0]-m[0])**2 for p,x in zip(w,features))
        b = sum(p*(x[0]-m[0])*(x[1]-m[1]) for p,x in zip(w,features))
        d = sum(p*(x[1]-m[1])**2 for p,x in zip(w,features))
        determinant = a*d-b*b
        if determinant <= 1e-20:
            break
        u,v = target[0]-m[0], target[1]-m[1]
        step = [(d*u-b*v)/determinant, (a*v-b*u)/determinant]
        scale = 1.
        while scale > 1e-8:
            candidate = [beta[i]+scale*step[i] for i in range(2)]
            if at(candidate)[2] < err:
                beta = candidate; break
            scale /= 2
        else:
            break
    raise InputGap('run25.coverage', 'full marginal delta/output targets cannot be matched inside the measured subset')


class Fleet:
    def __init__(self, econ, weights, case, speed, billing, cfg=None):
        if billing != 'bought':
            raise InputGap('run25.billing', 'fleet sensitivity is bought-office only; rental control remains the accepted run24 calculation')
        self.cfg = cfg or config(); self.econ = econ; self.server = econ.servers['pro6000_fp8']
        self.prepared = econ.prepared['pro6000_fp8','m5max64','measured_envelope']
        self.weights = weights; self.case = case; self.speed = speed; self.billing = billing
        self.depth = econ.cfg['reservation_depth']; self.slot = self.server.session_bytes(self.depth)
        self.link = self.prepared.profiles['office_gigabit' if billing == 'bought' else 'engine_wan']
        self.read = []; self.save = []; self.remote = []; self.base_service = []
        self.p = self.prepared
        for i,(d,n,o,t) in enumerate(self.p.calls):
            # Server format is65,536B/token and f32 resident state. Client wire is bf16.
            read = self.server.session_bytes(d)*speed/case['read_bytes_s']
            save = self.server.session_bytes(d+n+o)*speed/case['write_bytes_s']
            transfer = self.p.wire[i]/self.link['bytes_s']
            self.read.append(read); self.save.append(save)
            self.remote.append(read+self.p.pre[i]+transfer+self.link['rtt_s']+self.p.imports[i])
            self.base_service.append(read+self.p.pre[i]+save+transfer)
        # Sorting budget margins makes every subsequent fleet/team evaluation O(log N).
        order = sorted(range(len(weights)), key=lambda i: self.p.own[i]-self.remote[i], reverse=True)
        self.margins = [-(self.p.own[i]-self.remote[i]) for i in order]
        self.order = order
        self.total_shadow = sum(w*x for w,x in zip(weights,self.p.shadow))
        self.base_wait = sum(w*x for w,x in zip(weights,self.p.own))
        self.base_device = sum(w*(a+b) for w,a,b in zip(weights,self.p.own,self.p.decode_device))
        self.base_occupied = sum(w*(a*k+b) for w,a,k,b in zip(weights,self.p.own,self.p.wait_weight,self.p.decode_occupied))
        self.cold_journal_bound = sum(w*x for w,x in zip(weights,self.p.rebuild))
        self.overflow_prefill_ttft = sum(w*(r+p+self.link['rtt_s']) for w,r,p in zip(weights,self.read,self.p.pre))
        fields = {k:[] for k in ('mass','pending','service','service2','wait_delta','device_delta','occupied_delta','waitweight','read','save','wire','local_selected','remote_selected')}
        for i in order:
            s = self.base_service[i]; p = self.p
            vals = (1, p.output[i]-p.shadow[i], s, s*s,
                    self.remote[i]-p.own[i], p.imports[i]-p.own[i],
                    (self.remote[i]-p.own[i])*p.wait_weight[i], p.wait_weight[i],
                    self.read[i], self.save[i], p.wire[i], p.own[i], self.remote[i])
            for key,v in zip(fields,vals):
                fields[key].append(v*weights[i]+(fields[key][-1] if fields[key] else 0))
        self.prefix = {k:[0.]+v for k,v in fields.items()}
        self.overflow_cache = {}

    def route(self, queue):
        k = bisect.bisect_left(self.margins, -queue)
        while k:
            mass = self.prefix['mass'][k]
            pending = (self.total_shadow+self.prefix['pending'][k])/mass
            new = min(k, bisect.bisect_left(self.margins, -(queue+pending)))
            if new == k:
                return k, max(0.,pending)
            k = new
        return 0, 0.

    def overflow(self, team, nodes):
        # Same finite4T team concurrency and measured depth-batch surface as R23.
        active = min(nodes, int(team*self.econ.concurrency))
        streams = min(32, max(1, int(team*self.econ.concurrency)//active))
        if streams not in self.overflow_cache:
            first = second = 0.
            for w,(d,n,o,t),read,save,pre in zip(self.weights,self.p.calls,self.read,self.save,self.p.pre):
                dec = self.server.decode(d+n, streams)
                k = dec['batch']; rate = dec['aggregate_tok_s']
                work = max(pre+o/rate, (pre+o/(rate/k)+t)/k)
                # Equivalent batching occupancy is a workload proxy, not per-request decode latency.
                work += read+save
                first += w*work; second += w*work*work
            self.overflow_cache[streams] = first, second
        return active, self.overflow_cache[streams]

    def trial(self, team, demand, nodes, queue, local_prefill=False):
        k,pending = (0,0.) if local_prefill else self.route(queue)
        f = self.prefix; mass = f['mass'][k]
        wait = self.base_wait+f['wait_delta'][k]+mass*(queue+pending)
        device = self.base_device+f['device_delta'][k]
        occupied = self.base_occupied+f['occupied_delta'][k]+(queue+pending)*f['waitweight'][k]
        capacity = self.econ.hours*3600/max(device,occupied)
        served = min(demand, capacity); overflow = max(0., demand-served)
        active, (over_first,over_second) = self.overflow(team,nodes) if overflow else (nodes,(0.,0.))
        # Overflow is also a checkpoint catch-up. Do not treat an all-local
        # history as an already fresh server slot. With no prefill offloads,
        # use exchangeable local work per overflow refresh, capped by the full
        # existing-prefix cold-work upper bound. This is deferred journal work,
        # not an additional full resync performed on a current checkpoint.
        journal = pending if mass else min(self.cold_journal_bound,served*self.total_shadow/overflow) if overflow else 0.
        if overflow:
            over_second += 2*journal*over_first+journal*journal
            over_first += journal
        off_first = f['service'][k]+mass*pending
        off_second = f['service2'][k]+2*pending*f['service'][k]+mass*pending*pending
        jobs_day = team*(served*mass+overflow)
        first_day = team*(served*off_first+overflow*over_first)
        second_day = team*(served*off_second+overflow*over_second)
        first = first_day/jobs_day if jobs_day else 0.
        second = second_day/jobs_day if jobs_day else 0.
        rho, actual_queue = mg1(jobs_day/(self.econ.hours*3600),first,second,active)
        overflow_ttft = self.overflow_prefill_ttft+journal+queue if overflow else 0.
        return dict(offload_share=mass, pending_s_offload=pending,pending_s_overflow=journal if overflow else 0.,mean_ttft_s=wait,
                    mean_server_decode_overflow_ttft_s=overflow_ttft,
                    mean_all_call_ttft_s=(served*wait+overflow*overflow_ttft)/demand,
                    mean_offload_ttft_s=(f['remote_selected'][k]/mass+pending+queue) if mass else 0.,
                    mean_local_selected_s=f['local_selected'][k]/mass if mass else 0.,
                    client_capacity_day=capacity,served_day=served,server_decode_overflow_day=overflow,
                    service_utilization=rho,calendar_utilization=rho*self.econ.hours*self.econ.days/730,
                    actual_mean_queue_s=actual_queue,charged_mean_queue_s=queue,
                    read_s_offload=f['read'][k]/mass if mass else 0.,
                    write_s_offload=f['save'][k]/mass if mass else 0.,
                    wire_bytes_call=f['wire'][k], jobs_day=jobs_day,
                    mean_node_service_s=first, second_node_service_s2=second,
                    offload_count_shapes=k,active_nodes=active)

    def evaluate(self, team, demand, nodes):
        cap = storage(self.server,self.depth,team,nodes,self.case,self.econ.sessions)
        row = dict(cap,nodes=nodes,team=team,status='storage_shortfall',reason='off-GPU complete copies exceed declared tier capacity',
                   person_month='', mean_ttft_s='', service_utilization='')
        row['feasible'] = False
        if not cap['feasible']:
            return row
        candidate = None
        for local_prefill in (False,True):
            # If the largest tested queue already selected no offloads, forcing
            # local prefill is identical and cannot cure its failed queue/load.
            if local_prefill and candidate is not None and candidate['offload_share']==0:
                continue
            for queue in self.cfg['queue_budgets_s']:
                if queue > self.cfg['max_mean_queue_s']:
                    continue
                stat = self.trial(team,demand,nodes,queue,local_prefill); candidate = stat
                if (stat['actual_mean_queue_s'] <= queue+1e-12 and
                        stat['service_utilization'] <= self.cfg['max_service_occupancy']):
                    break
            else:
                continue
            if (stat['actual_mean_queue_s'] <= queue+1e-12 and
                    stat['service_utilization'] <= self.cfg['max_service_occupancy']):
                stat['prefill_route'] = ('local_after_remote_queue_refusal' if local_prefill else
                    'profitable_offload' if stat['offload_share'] else 'local_no_profitable_offload')
                row.update(stat,feasible=True,status='feasible',reason='storage, <=70% occupancy and declared mean-queue budget certified; not a tail guarantee')
                month,_ = self.econ.units['pro6000_fp8',self.billing]
                inputs = self.econ.inputs; extra = self.case['extra_capex_usd']
                # Added storage is explicitly owned even on a rented GPU scenario.
                uplift = extra*(1-inputs.get('owners.residual'))/(12*inputs.get('owners.years'))+extra*inputs.get('owners.office_support')/12
                energy = inputs.get('hardware.clients.m5max64.power')*self.econ.hours*self.econ.days*inputs.get('prices.energy_client')
                row.update(unit_month=month,extra_storage_node_month=uplift,client_energy_month=energy,
                           front_month=inputs.get('owners.front_month'),
                           person_month=nodes*(month+uplift)/team+energy+inputs.get('owners.front_month'))
                return row
        row.update(status='latency_or_compute_shortfall',reason='no certified queue-budget point at <=70% occupancy and <=5s mean queue; demand not silently dropped',
                   reported_mean_queue_s=candidate['actual_mean_queue_s'] if candidate else '',
                   service_utilization=candidate['service_utilization'] if candidate else '')
        return row

    def minimum(self, team, demand):
        low = storage(self.server,self.depth,team,1,self.case,self.econ.sessions)['storage_min_nodes']
        if low is None:
            raise InputGap('run25.storage','one complete copy cannot fit any node')
        # Enumerate integers: routing changes prevent assuming monotone performance.
        for nodes in range(low,max(low,4*team)+1):
            row = self.evaluate(team,demand,nodes)
            if row['status'] == 'feasible':
                return row
        return dict(team=team,nodes='',person_month='',feasible=False,status='finite_concurrency_shortfall',reason='no certified fleet through4T nodes')
