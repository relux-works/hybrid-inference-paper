"""Shared declared inputs for canonical workloads, FLOPs and measurement fits."""
import math
import statistics
from .inputs import InputGap
from .metrics import field, nonempty
from .performance import flop, Curve
from .workload import sampled_calls

FLOP_FIELDS = ('base_flop', 'attention_slope', 'sparse_slope', 'sparse_cap', 'context_limit')
WORKLOAD_FIELDS = ('sample_calls', 'seed', 'input_cap', 'output_cap', 'tail_cap',
                   'tool_median', 'tool_sigma', 'reasoning_extra_fraction')
SAMPLER_FIELDS = ('depth_50k', 'depth_100k', 'depth_200k', 'above_p90', 'above_p99',
                  'minimum_mean_ratio', 'minimum_median', 'mode')


def calls_graph(g):
    cfg = g.bundle('workload.settings', 'workload', WORKLOAD_FIELDS)
    cut = g.bundle('workload.sampler', 'sampler', SAMPLER_FIELDS)
    mode=g.resolve('sampler.mode')
    if not mode.alarms and mode.value=='measured_tail':
        controls=g.bundle('workload.fit.controls','sampler.fit',('iterations','tolerance','minimum_calls'))
        arrays=[]
        for name in ('thresholds','representatives','low_probabilities','depth_probabilities'):
            arrays.append(g.add('workload.fit.'+name,g.positions('sampler.fit.'+name),lambda *values:list(values)))
        fit=g.add('workload.fit',[controls]+arrays,lambda controls,t,r,p,d:dict(controls,thresholds=t,representatives=r,low_probabilities=p,depth_probabilities=d))
    else:fit=g.constant('workload.historical_fit',None)
    stats = g.measurement('stats')
    def sample(settings, sampler, document, fit):
        agent = field(document, 'agents.all', 'measurements.stats')
        try:
            return sampled_calls(g.inputs, settings, agent=agent, cut=sampler, fit=fit)
        except InputGap:
            raise
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            raise InputGap('measurements.stats', 'invalid call-mix measurement: ' + str(exc)) from exc
    requested = g.resolve('workload.sample_calls')
    if not requested.alarms and requested.value == 0:
        calls = g.add('calls', ['workload.sample_calls'], lambda count: [])
    else:
        calls = g.add('calls', [cfg, cut, stats, fit], sample)
    usable = g.add('calls.nonempty', [calls], nonempty)
    return calls, usable


def mean_field(g, name, calls, index):
    return g.add(name, [calls], lambda rows: sum(row[index] for row in rows) / len(nonempty(rows)))


def mean_flops(calls, model, shadow=True):
    return sum((delta + output if shadow else delta) * flop(model, depth)
               for depth, delta, output, tool in nonempty(calls)) / len(calls)


def curve_data(rows, model, inputs):
    curve = []
    for index, row in enumerate(rows):
        if field(row, 'kind', 'measurements.depth') != 'segment':
            continue
        values = [field(row, key, 'measurements.depth') for key in ('depth_from', 'depth', 'prefill_tok_s')]
        start, end, rate = values
        if not all(type(v) in (int, float) and math.isfinite(v) for v in values) or not (0 <= start < end and rate > 0):
            raise InputGap('measurements.depth', 'invalid prefill segment bounds or rate')
        for key, value, unit in zip(('depth_from', 'depth', 'prefill_tok_s'), values, ('token', 'token', 'token/s')):
            inputs.measured_value('depth', 'segment.{}.{}'.format(index, key), value, unit)
        curve.append(((start + end) / 2, rate))
    if len(curve) < 2 or any(b[0] <= a[0] for a,b in zip(curve, curve[1:])):
        raise InputGap('measurements.depth', 'at least two increasing segment midpoints are required')
    return Curve(model, curve)


def slot_data(rows, inputs):
    xs, ys = [], []
    for index,row in enumerate(rows):
        if field(row, 'kind', 'measurements.depth') == 'slot_save':
            for key,values,unit in [('depth',xs,'token'),('bytes',ys,'B')]:
                value = field(row, key, 'measurements.depth')
                if type(value) not in (int,float) or not math.isfinite(value) or value < 0:
                    raise InputGap('measurements.depth','invalid slot depth/bytes')
                values.append(inputs.measured_value('depth','slot.{}.{}'.format(index,key),value,unit))
    if len(xs) < 2 or len(set(xs)) < 2:
        raise InputGap('measurements.depth', 'slot fit needs at least two distinct depths')
    mx,my=statistics.mean(xs),statistics.mean(ys)
    slope=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
    fixed=my-slope*mx
    if slope <= 0 or fixed <= 0:
        raise InputGap('measurements.depth', 'slot fit needs positive per-token and fixed bytes')
    return slope,fixed


def decode_calibration(document, weights, kv, bandwidth, passes, state, inputs):
    values={}
    for path,unit in [('baseline_native_decode_tok_s','token/s'),('normalized_decode_interval_gain','1'),
                      ('frozen_v11_row.depth','token'),('frozen_v11_row.streams','stream')]:
        value=field(document,'parallel.'+path,'measurements.normalized')
        if type(value) not in (int,float) or not math.isfinite(value) or value <= 0:
            raise InputGap('measurements.normalized','invalid decode calibration '+path)
        values[path]=inputs.measured_value('normalized','parallel.'+path,value,unit)
    k=values['frozen_v11_row.streams']
    if k <= 1:
        raise InputGap('measurements.normalized','parallel calibration needs more than one stream')
    traffic=values['frozen_v11_row.depth']*kv+passes*state
    efficiency=values['baseline_native_decode_tok_s']*(weights+traffic)/bandwidth
    ideal=k*(weights+traffic)/(weights+k*traffic)
    penalty=math.log(ideal/values['normalized_decode_interval_gain'])/math.log(k)
    return efficiency,penalty
