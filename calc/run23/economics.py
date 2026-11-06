"""Measured PRO decode surface; reviewed accounting and other hosts unchanged."""
from functools import lru_cache
import math

from hybridcalc.inputs import InputGap
from hybridcalc import deep_r21 as deep, measurements_r18 as r18
from run22 import economics as base, interfaces
from . import inputs

Economics=base.Economics
M5Rates=base.M5Rates
mac_prefill=base.mac_prefill
coverage=base.coverage
intensity=base.intensity


class Server(base.Server):
    def __init__(self,key,cfg=None,observations=(),decode_observations=None):
        if decode_observations is None:
            physical={k:base.Server(k,cfg)for k in deep.SERVERS}
            decode_observations=interfaces.server_rows(inputs.rows('server_decode'),physical,'decode')
        super().__init__(key,cfg,observations,decode_observations)
        self.surface={}
        for row in decode_observations:
            if row['server']==key:
                self.surface.setdefault(row['depth'],{})[row['streams']]=row['aggregate_tok_s']
        self.depths=sorted(self.surface)
        self.limits={d:self.decode_capacity.get(d)for d in self.depths}
        if key=='pro6000_fp8':
            if not self.depths or any(1 not in points or self.limits[d] not in points for d,points in self.surface.items()):
                raise InputGap('run23.decode','PRO surface requires single and largest-resident measurements at each depth')

    def require_capacity(self,depth):
        if self.key=='pro6000_fp8' and depth>=1000000:
            raise InputGap('run23.capacity','one complete session does not fit: measured PRO default-KV1M refusal,61.97GiB needed >56.62GiB available; FP8 KV unavailable on SM12.0')

    @lru_cache(maxsize=None)
    def slots(self,depth):
        self.require_capacity(depth)
        physical=super().slots(depth)
        if self.key!='pro6000_fp8' or not self.depths[0]<=depth<=self.depths[-1]:
            return physical
        if depth in self.limits:
            return min(physical,self.limits[depth])
        # KV space is approximately linear in depth. Interpolate reciprocal
        # resident count (space/session), then round down; never interpolate N
        # arithmetically and invent additional deep resident sessions.
        reciprocal=r18.interpolate([(d,1/self.limits[d])for d in self.depths],depth)
        return min(physical,max(1,math.floor(1/reciprocal+1e-12)))

    def cached(self,depth,delta,bridge='none'):
        self.require_capacity(depth+delta)
        return super().cached(depth,delta,bridge)

    def cold(self,depth):
        self.require_capacity(depth)
        return super().cold(depth)

    @lru_cache(maxsize=None)
    def _measured_decode(self,depth,streams):
        k=min(streams,self.slots(depth))
        cap=self.slots(depth)
        if depth in self.surface and k in self.surface[depth]:
            aggregate=self.surface[depth][k];single=self.surface[depth][1]
            basis='measured PRO depth/streams point; private independent contexts, three-round SSE common-window median'
        else:
            # At each bracketing depth interpolate seconds/sequence-token across
            # measured N. Between depths use equal fractions of admitted batch
            # capacity. This stays inside both measured batch ranges even when
            # the deeper endpoint cannot hold the shallower requested N.
            fraction=0 if cap==1 else (k-1)/(cap-1)
            seconds=[];single_seconds=[]
            for d in self.depths:
                target=1+fraction*(self.limits[d]-1)
                points=self.surface[d]
                seconds.append((d,r18.interpolate(sorted((n,n/rate)for n,rate in points.items()),target)))
                single_seconds.append((d,1/points[1]))
            aggregate=k/r18.interpolate(seconds,depth)
            single=1/r18.interpolate(single_seconds,depth)
            basis='interpolated PRO measured surface: seconds/sequence-token in batch and depth at equal resident-batch fraction; reciprocal residency interpolation; not a direct measurement'
        return dict(batch=k,single_tok_s=single,aggregate_tok_s=aggregate,gain=aggregate/single,basis=basis)

    def decode(self,depth,streams=32,measurements=None):
        from hybridcalc.measurements_r19 import integer
        integer(streams,'streams')
        self.require_capacity(depth)
        if self.key=='pro6000_fp8' and self.depths[0]<=depth<=self.depths[-1]:
            # Always consume the bound measured surface. The old caller's
            # exact-N sparse-anchor selection must not silently restore a model.
            return dict(self._measured_decode(depth,streams))
        result=super().decode(depth,streams,measurements)
        if self.key=='pro6000_fp8':
            result['basis']+='; outside PRO16384–256000 measured surface'
        else:
            result['basis']+='; B300 decode pending: rental failed to start2026-11-04T00:36Z'
        return result
