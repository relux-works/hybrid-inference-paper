"""Prefill roofline, measured interpolation and batched decode bandwidth models."""
import json
import math
import statistics
from .inputs import InputError, InputGap


def positive(value, name, zero=False):
    if not math.isfinite(value) or value < 0 or (not zero and value == 0):
        raise InputError('{} must be {}'.format(name, 'nonnegative' if zero else 'positive'))
    return value


def flop(model, depth):
    positive(depth, 'depth', zero=True)
    if depth > model['context_limit']:
        from .inputs import InputGap
        raise InputGap('models.context_limit', 'depth exceeds declared context limit')
    return (model['base_flop'] + model['attention_slope'] * depth
            + model['sparse_slope'] * min(depth, model['sparse_cap']))


def roofline_prefill(model, depth, compute, bandwidth, bytes_per_token):
    """Seconds/token = max(compute traffic / FLOP/s, memory traffic / B/s)."""
    positive(compute, 'prefill FLOP/s')
    positive(bandwidth, 'memory bandwidth')
    positive(bytes_per_token, 'memory traffic', zero=True)
    return max(flop(model, depth) / compute, bytes_per_token / bandwidth)


def payload(delta, kv, state):
    positive(delta, 'delta', zero=True)
    positive(kv, 'KV bytes/token')
    positive(state, 'state bytes', zero=True)
    return delta * kv + state


def transfer(delta, kv, state, link):
    try:
        bandwidth = link['bandwidth']
    except KeyError as exc:
        raise InputGap('bandwidth', 'missing input; offload impossible') from exc
    if type(bandwidth) not in (int, float) or not math.isfinite(bandwidth) or bandwidth <= 0:
        raise InputGap('bandwidth', 'positive finite link bandwidth required; offload impossible')
    positive(link['goodput'], 'link goodput')
    if link['goodput'] > 1:
        raise InputError('link goodput must be at most 1')
    positive(link['latency'], 'link latency', zero=True)
    return link['latency'] + payload(delta, kv, state) * 8 / (link['bandwidth'] * link['goodput'])


class Curve:
    """Measured marginal segment curve with a declared FLOP extrapolation envelope."""
    def __init__(self, model, curve):
        self.model, self.curve = model, curve

    def rate(self, depth):
        positive(depth, 'depth', zero=True)
        if depth <= self.curve[0][0]:
            return self.curve[0][1]
        for (x0, y0), (x1, y1) in zip(self.curve, self.curve[1:]):
            if depth == x1:
                return y1
            if depth < x1:
                return y0 + (y1 - y0) * (depth - x0) / (x1 - x0)
        x, y = self.curve[-1]
        return y * flop(self.model, x) / flop(self.model, depth)


class Calibration(Curve):
    """calc9 midpoint interpolation; beyond the last point keep FLOP efficiency constant."""
    def __init__(self, inputs, model):
        self.model = model
        rows = [json.loads(line) for line in inputs.measured('depth').splitlines()]
        segments = [r for r in rows if r['kind'] == 'segment']
        saves = [r for r in rows if r['kind'] == 'slot_save']
        if len(segments) < 2 or len(saves) < 2:
            raise InputError('benchmark needs at least two segments and slot saves')
        self.curve = []
        for index, row in enumerate(segments):
            for field, unit in [('depth_from', 'token'), ('depth', 'token'), ('prefill_tok_s', 'token/s')]:
                inputs.measured_value('depth', 'segment.{}.{}'.format(index, field), row[field], unit)
            if row['depth'] <= row['depth_from'] or row['prefill_tok_s'] <= 0:
                raise InputError('invalid benchmark segment')
            self.curve.append(((row['depth_from'] + row['depth']) / 2, row['prefill_tok_s']))
        if any(b[0] <= a[0] for a, b in zip(self.curve, self.curve[1:])):
            raise InputError('benchmark segment midpoints must increase')
        xs, ys = [], []
        for index, row in enumerate(saves):
            xs.append(inputs.measured_value('depth', 'slot.{}.depth'.format(index), row['depth'], 'token'))
            ys.append(inputs.measured_value('depth', 'slot.{}.bytes'.format(index), row['bytes'], 'B'))
        mx, my = statistics.mean(xs), statistics.mean(ys)
        variance = sum((x - mx) ** 2 for x in xs)
        if variance == 0:
            raise InputError('slot-fit depths must vary')
        self.slot_per_token = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / variance
        self.slot_fixed = my - self.slot_per_token * mx
        positive(self.slot_fixed, 'fitted fixed state')
        normalized = inputs.measured_json('normalized')['parallel']
        self.single = inputs.measured_value('normalized', 'parallel.baseline_native_decode_tok_s', normalized['baseline_native_decode_tok_s'], 'token/s')
        self.gain = inputs.measured_value('normalized', 'parallel.normalized_decode_interval_gain', normalized['normalized_decode_interval_gain'], '1')
        self.parallel_depth = inputs.measured_value('normalized', 'parallel.frozen_v11_row.depth', normalized['frozen_v11_row']['depth'], 'token')
        self.parallel_streams = inputs.measured_value('normalized', 'parallel.frozen_v11_row.streams', normalized['frozen_v11_row']['streams'], 'stream')

    def decode_parameters(self, weights, kv, bandwidth, state_passes):
        traffic = self.parallel_depth * kv + state_passes * self.slot_fixed
        efficiency = self.single * (weights + traffic) / bandwidth
        k = self.parallel_streams
        ideal_gain = k * (weights + traffic) / (weights + k * traffic)
        penalty = math.log(ideal_gain / self.gain) / math.log(k)
        return efficiency, penalty


def dense_decode(model, device, streams, depth, efficiency, penalty, state_passes):
    positive(streams, 'streams')
    step = model['weights'] + streams * (depth * model['kv'] + state_passes * model['state'])
    return device['bandwidth'] * efficiency / (step * streams ** penalty)


def memory_streams(model, device, depth, usable, buffers):
    free = device['memory'] * usable - buffers - model['weights']
    return max(0, int(free // (depth * model['kv'] + model['state'])))
