"""Constant design compute or a measured depth-dependent prefill envelope."""
import math
from .analysis_graph import mean_flops
from .inputs import InputGap
from .metrics import field, nonempty
from .performance import flop


def compute_at(compute, depth):
    return compute(depth) if callable(compute) else compute


def scale_compute(compute, factor):
    return (lambda depth: compute(depth) * factor) if callable(compute) else compute * factor


def mean_seconds(calls, model, compute, shadow=True):
    # Preserve the design case's operation order and exact serialized floats.
    if not callable(compute):
        return mean_flops(calls, model, shadow=shadow) / compute
    return sum((n + o if shadow else n) * flop(model, d) / compute_at(compute, d)
               for d, n, o, t in nonempty(calls)) / len(calls)


def fit(rows):
    """Unweighted OLS of seconds/token against the six nominal depth labels.

    Twelve bulk-turn observations (2k and10k); fills and512 turns held out.
    Sequential actual start depths are preserved in the raw data/residual ledger.
    """
    points=[]
    for row in rows:
        if row.get('kind') != 'turn' or row.get('delta') not in (2000, 10000):
            continue
        keys=('level', 'depth', 'delta', 'prompt_n', 'prompt_ms')
        values=[field(row, k, 'measurements.gpu_server') for k in keys]
        if not all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in values):
            raise InputGap('measurements.gpu_server', 'positive finite bulk-turn fields required')
        if row.get('truncated') is not False or row.get('gen_tokens_exact') is not True:
            raise InputGap('measurements.gpu_server', 'truncated or inexact bulk-turn measurement')
        d, actual, delta, n, ms=values
        points.append(dict(depth=d, actual_depth=actual, delta=delta, seconds_token=ms/1000/n))
    expected={(d,n) for d in (16000,50000,100000,150000,200000,249000) for n in (2000,10000)}
    if len(points)!=12 or {(p['depth'],p['delta']) for p in points}!=expected:
        raise InputGap('measurements.gpu_server', 'exactly twelve distinct bulk observations at six depths required')
    x=sum(p['depth'] for p in points)/len(points)
    y=sum(p['seconds_token'] for p in points)/len(points)
    b=sum((p['depth']-x)*(p['seconds_token']-y) for p in points)/sum((p['depth']-x)**2 for p in points)
    a=y-b*x
    if a<=0 or b<0:
        raise InputGap('measurements.gpu_server', 'fit must have positive intercept and nonnegative depth slope')
    return a,b,points


def measured_compute(rows, reference_model, reference_peak, target_peak, precision):
    if precision!='Q4':
        raise InputGap('owners.server_precision', 'measured-server sensitivity requires same-weights Q4')
    if reference_peak<=0 or target_peak<=0:
        raise InputGap('hardware.servers.rtx1.peak', 'positive dense peaks required')
    a,b,_=fit(rows)
    # Constant peak ratio transfers the depth-dependent RTX utilization to B300.
    # Other model FLOPs (e.g. GLM) use this envelope as an explicit estimate.
    return lambda depth: flop(reference_model, depth)/(a+b*depth)*target_peak/reference_peak
