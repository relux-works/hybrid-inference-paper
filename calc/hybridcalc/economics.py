"""Linear token and running costs; integer server fleets and finite-grid equilibrium."""
import math
from .performance import flop
from .inputs import InputError


def api_cost(calls, prices):
    """Flat call-mix billing: prefix cached, delta uncached, output charged once."""
    from .metrics import nonempty
    nonempty(calls)
    return sum(depth * prices['cache_read'] + delta * prices['input'] + output * prices['output']
               for depth, delta, output, _ in calls) / len(calls) / 1e6


def unit_opex(server, prices, econ):
    energy = server['power'] * econ['pue'] * 12 * econ['hours_month'] * econ['load'] * prices['energy_dc']
    colo = server['power'] * prices['colo'] * 12
    support = server['capex'] * econ['support']
    return energy, colo, support


def unit_month(server, prices, econ):
    return (server['capex'] * (1 - econ['server_residual']) / (12 * econ['years'])
            + sum(unit_opex(server, prices, econ)) / 12)


def demand_price(server, prices, econ):
    """USD/GPU-s of demand; regions reuse a fleet across nonoverlapping working days."""
    utilization = econ['days_month'] * econ['hours_day'] * econ['regions'] / (econ['hours_month'] * econ['peak'])
    if utilization > 1:
        raise InputError('regional utilization exceeds 1; reduce regions/hours_day')
    return unit_month(server, prices, econ) / (server['gpus'] * econ['hours_month'] * 3600 * utilization)


def fleet(people, gpu_seconds_call, server, prices, econ):
    peak_gpus = (people / econ['regions'] * econ['calls_day'] * gpu_seconds_call
                 / (econ['hours_day'] * 3600) * econ['peak'])
    units = max(1, math.ceil(peak_gpus / server['gpus']))
    return {'people': people, 'units': units, 'peak_gpus': peak_gpus,
            'capex': units * server['capex'],
            'opex_year': units * sum(unit_opex(server, prices, econ)),
            'monthly': units * unit_month(server, prices, econ)}


def own_gpu_seconds(calls, model, server, decode, state_passes):
    """No overlap credit: sum prefill, decode bandwidth and KV residency, as calc4."""
    pre = dec = residence = 0.0
    for depth, delta, output, tool in calls:
        pre += delta * flop(model, depth) / (server['peak'] * server['mfu'])
        at = depth + delta
        step = decode['step'](decode['batch'], at, server=True)
        dec += output * step / decode['batch'] / (server['bandwidth'] * decode['efficiency'])
        busy = output / decode['stream_rate'] + tool
        residence += (at * model['kv'] + model['state']) * busy / (server['memory'] - server['reserved'])
    n = len(calls)
    return pre / n, dec / n, residence / n


def first_stays(rows, left, right):
    """First point after the last failure on this finite grid only."""
    hit = None
    for row in rows:
        if row[left] <= row[right]:
            if hit is None:
                hit = row['people']
        else:
            hit = None
    return hit
