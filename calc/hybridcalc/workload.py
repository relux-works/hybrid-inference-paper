"""Seeded sampler fitted to the delivered aggregate call mix, not a reconstructed trace."""
import math
import random
from .inputs import InputError


def sampled_calls(inputs, settings, agent=None, cut=None, fit=None):
    if agent is None:
        agent = inputs.measured_json('stats')['agents']['all']
    from .metrics import field
    from .inputs import InputGap
    def scalar(path, unit):
        value = field(agent, path, 'measurements.stats')
        return inputs.measured_value('stats', 'agents.all.' + path, value, unit)
    # Validate exactly the measured fields that define the fitted distribution.
    original=agent
    bins = {name: {key: scalar('new_in_by_depth.' + name + '.' + key, 'call' if key == 'n' else 'token')
                   for key in ('n', 'p50', 'mean')}
            for name in ('<50k', '50-100k', '100-200k', '200k+')}
    packed = {'new_in_by_depth': bins,
             'first_call_prompt': {'p25': scalar('first_call_prompt.p25', 'token')},
             **{section: {key: scalar(section + '.' + key, 'token') for key in keys}
                for section, keys in [('depth_per_call', ('p90', 'p99')), ('output_per_call', ('p50', 'mean')), ('reasoning_per_call', ('p50', 'mean'))]}}
    agent=original
    bins = packed['new_in_by_depth']
    names = ['<50k', '50-100k', '100-200k', '200k+']
    weights = [bins[b]['n'] for b in names]
    if any(w <= 0 for w in weights):
        raise InputError('all workload depth bins must have positive call counts')
    # Bin boundaries and quantile probabilities are declared in sampler.json.
    if cut is None:
        cut = inputs.section('sampler')
    ranges = {names[0]: (packed['first_call_prompt']['p25'], cut['depth_50k']),
              names[1]: (cut['depth_50k'], cut['depth_100k']),
              names[2]: (cut['depth_100k'], cut['depth_200k'])}
    if not (packed['first_call_prompt']['p25'] <= cut['depth_50k'] < cut['depth_100k'] < cut['depth_200k']):
        raise InputGap('sampler.depth_50k', 'depth bins must be ordered after first-call p25')
    if not (0 < cut['above_p99'] <= cut['above_p90'] < 1):
        raise InputGap('sampler.above_p99', 'tail probabilities must satisfy 0 < p99 tail <= p90 tail < 1')
    p90, p99 = packed['depth_per_call']['p90'], packed['depth_per_call']['p99']
    share = weights[-1] / sum(weights)
    if not (cut['depth_200k'] <= p90 <= p99 <= settings['tail_cap']):
        raise InputError('workload tail must satisfy 200k <= p90 <= p99 <= tail_cap')
    if share < cut['above_p90']:
        raise InputError('200k+ bin is too small for the specified tail probabilities')
    rnd = random.Random(settings['seed'])
    def draw(median, mean, cap):
        if mean == 0:
            if median != 0:
                raise InputGap('measurements.stats', 'zero mean with positive median is inconsistent')
            return 0.0
        sigma = math.sqrt(2 * math.log(max(mean / max(median, cut['minimum_median']), cut['minimum_mean_ratio'])))
        return min(cap, rnd.lognormvariate(math.log(max(median, cut['minimum_median'])), sigma))
    calls = [];groups=[];components=[]
    for _ in range(settings['sample_calls']):
        name = rnd.choices(names, weights)[0]
        if name == names[-1]:
            u = rnd.random()
            if u < 1 - cut['above_p90'] / share:
                depth = rnd.uniform(cut['depth_200k'], p90)
            elif u < 1 - cut['above_p99'] / share:
                depth = math.exp(rnd.uniform(math.log(p90), math.log(p99)))
            else:
                depth = rnd.uniform(p99, settings['tail_cap'])
        else:
            depth = rnd.uniform(*ranges[name])
        delta = draw(bins[name]['p50'], bins[name]['mean'], settings['input_cap'])
        output = draw(packed['output_per_call']['p50'], packed['output_per_call']['mean'], settings['output_cap'])
        reasoning = draw(packed['reasoning_per_call']['p50'], packed['reasoning_per_call']['mean'], settings['output_cap'])
        tool = rnd.lognormvariate(math.log(settings['tool_median']), settings['tool_sigma'])
        calls.append((depth, delta, output + settings['reasoning_extra_fraction'] * reasoning, tool))
        groups.append(name);components.append((output,reasoning))
    if cut['mode']=='measured_tail':
        from .sampler_fit import calibrate
        if fit is None:fit=inputs.section('sampler.fit')
        data=dict(depth_quantiles=[scalar('depth_per_call.'+label,'token') for label in ('p10','p25','p50','p75','p90','p99')],first_depth=packed['first_call_prompt']['p25'],depth_cuts=[cut['depth_50k'],cut['depth_100k'],cut['depth_200k']],bins=bins,new_mean=scalar('new_in_per_call.mean','token'),depth_mean=scalar('depth_per_call.mean','token'),
                  output_mean=scalar('output_per_call.mean','token'),reasoning_mean=scalar('reasoning_per_call.mean','token'),
                  shares=[scalar('share_of_new_tokens_in_calls.'+label,'1') for label in ('>=2k','>=5k','>=10k','>=30k')],
                  low_quantiles=[scalar('new_in_per_call.'+label,'token') for label in ('p10','p25','p50','p75')])
        calls=calibrate(calls,groups,components,data,settings,fit,rnd)
    return calls


def summary(calls, chunk):
    from .metrics import nonempty
    nonempty(calls)
    return {'calls': len(calls), 'calls_per_session': chunk,
            'mean_depth': sum(c[0] for c in calls) / len(calls),
            'mean_new': sum(c[1] for c in calls) / len(calls),
            'mean_output': sum(c[2] for c in calls) / len(calls)}
