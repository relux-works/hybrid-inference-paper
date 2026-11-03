#!/usr/bin/env python3
"""What the owner's preserved agent calls would have cost at API list prices, per model (paper section on economics).

Inputs:
- the `model_usage` rows of `tools/agent_session_stats.py` 1.6 (per agent and model: deduplicated calls and raw token
  counters, with `<counter>_reported_sum` and `unknown_counter_calls`);
- `model-prices-2026-10.csv`: list prices per 1M tokens and the AA Intelligence Index class against Qwen3.8-27B, from
  the research note `model-prices-capability-2026-10.md` (all prices read 2026-10-30, sources per row).

Every bill is a range [low, high]. The range covers what the logs do not say:
- Anthropic cache writes without a logged TTL split cost 1.25x input (5-minute write, low) to 2x input (1-hour write,
  high); logged 5-minute and 1-hour writes are priced as logged. Duplicate records keep independent maxima per
  counter, so a row's TTL split can exceed its total write; the excess is priced as logged and reported per row.
- OpenAI GPT-5.6 and GPT-6.x bill a cache write at 1.25x input. A Codex row that logs its cache write on every call is
  priced as logged; the owner's Codex logs report a zero write on every call. Without a logged write, uncached input
  costs 1x (low) to 1.25x (high). Older OpenAI models have no write price.
- Muse cache semantics are unverified: input is treated as including cache reads (low) or excluding them (high).
- Models whose price changed during the year use the cheaper period (low) and the dearer one (high).
Not applied, and reported separately: OpenAI's long-context rate (2x input and cache, 1.5x output for prompts above
272K tokens on GPT-5.4 and later) and the early-2026 Claude 4.6 surcharge above 200K, because the export has no
per-call depth by model. Reasoning tokens are never added to output: providers bill them inside output_tokens.

Run: python3 year_bill.py model-usage.json [--prices model-prices-2026-10.csv] [--out year-bill.csv]
     python3 year_bill.py --self-test
"""
import argparse, csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
M = 1e6

# Class against Qwen3.8-27B by the AA Intelligence Index on the same index version (research note, table 1 and 3).
# at_or_below: every scored variant at or below; above: the headline variant and the provider's default effort above;
# effort: above only at high reasoning effort, at or below at the provider's default effort; unclassified: no AA score.
CLASS = {
    **dict.fromkeys(['gpt-5.2', 'gpt-5.3-codex', 'gpt-5-codex', 'gpt-5.1-codex', 'gpt-5.2-codex', 'gpt-5.1',
                     'claude-sonnet-4-6', 'claude-opus-4-5', 'claude-opus-4-6'], 'at_or_below'),
    **dict.fromkeys(['gpt-6.1-sol', 'gpt-6-astra', 'gpt-6-sol', 'gpt-5.6-sol', 'claude-opus-5-5', 'claude-opus-5',
                     'claude-fable-5', 'claude-fable-5-1', 'claude-sonnet-5-5', 'claude-opus-4-8', 'muse-spark-1.3',
                     'muse-spark-1.3-contributor', 'muse-wonder-full-1.0', 'muse-wonder-full-1.0-contributor',
                     'muse-wonder-1.0', 'muse-wonder-1.0-contributor'], 'above'),
    **dict.fromkeys(['gpt-5.4', 'gpt-5.5', 'gpt-5.6-luna', 'gpt-5.6-terra', 'gpt-6-luna', 'claude-sonnet-5',
                     'claude-opus-4-7'], 'effort'),
    **dict.fromkeys(['gpt-5.3-codex-spark', 'gpt-5.1-codex-max'], 'unclassified'),
}
# Models without their own per-token price, priced with a labelled proxy (research note, gaps 1 and 3). Muse Wonder
# has no Contributor-mode price; its API sibling's standard price stands in.
PROXY = {'gpt-5.3-codex-spark': 'gpt-5.3-codex', 'muse-wonder-full-1.0': 'muse-wonder-1.0',
         'muse-wonder-full-1.0-contributor': 'muse-wonder-1.0', 'muse-wonder-1.0-contributor': 'muse-wonder-1.0'}
# Logged labels that name a priced variant differently.
ALIAS = {'muse-spark-1.3-contributor-free': 'muse-spark-1.3-contributor'}
# Labels of open models served on the owner's own machine (LM Studio, Ollama, llama-server, MLX), inferred from the
# label. They have no API bill and are reported apart.
LOCAL = {'qwen3.6-27b', 'qwen3.8-27b-q4km', 'gpt-oss-20b-high-131k', 'gpt-oss-20b-high-131k:latest', 'gpt-oss-120b',
         'gpt-oss-120b-high-131k', 'openai/gpt-oss-20b', 'gpt-oss:20b', 'gpt-oss-safeguard-120b-mlx',
         'google/gemma-4-26b-a4b', 'qwen/qwen3-coder-next'}
QWEN = 'qwen3.8-27b'
# Muse Spark 1.3 calls from a Muse Code subscription may be Contributor mode (research note, gap 4): low bound.
LOW_VARIANT = {'muse-spark-1.3': 'muse-spark-1.3-contributor'}
OPENAI_WRITE_BILLED = re.compile(r'^gpt-(5\.6|6)')


def number(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_prices(path):
    """Return {model: [price rows]}; a model with a price change has one row per period."""
    prices = {}
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            name = re.sub(r'\s*\(.*\)$', '', r['model'].strip())
            row = {k: number(r[k]) for k in ('input_per_m', 'cache_read_per_m', 'cache_write_per_m', 'output_per_m')}
            if row['input_per_m'] is None:
                continue
            row['label'] = r['model'].strip()
            prices.setdefault(name, []).append(row)
    return prices


def normalise(label):
    """Map a logged model label to a price-table name: lower case, no [1m]-style suffix, no -YYYYMMDD snapshot."""
    if not isinstance(label, str):
        return None
    x = label.strip().lower()
    x = re.sub(r'\[[^\]]*\]$', '', x)
    x = re.sub(r'-20\d{6}$', '', x)
    return ALIAS.get(x, x) or None


def counter(row, key):
    """Sum over the calls that report the counter, and the number of calls that do not."""
    total = row.get(key + '_reported_sum')
    if total is None:
        total = row.get(key) or 0
    missing = (row.get('unknown_counter_calls') or {}).get(key, 0)
    return total, missing


def price_row(agent, name, usage, p, low):
    """Cost in dollars of one usage row at one price row; low selects the cheaper reading of each unknown."""
    inp, read, out = p['input_per_m'], p['cache_read_per_m'] or 0.0, p['output_per_m']
    output, _ = counter(usage, 'raw_output')
    if agent == 'claude':
        uncached, _ = counter(usage, 'uncached_input')
        write, _ = counter(usage, 'cache_write')
        w5, _ = counter(usage, 'cache_write_5m')
        w1, _ = counter(usage, 'cache_write_1h')
        cached, _ = counter(usage, 'cache_read')
        unknown_ttl = max(write - w5 - w1, 0)
        write_cost = w5 * 1.25 * inp + w1 * 2 * inp + unknown_ttl * (1.25 if low else 2) * inp
        return (uncached * inp + write_cost + cached * read + output * out) / M
    if agent == 'codex':
        # Legacy prompt is the inclusive input and legacy cached is the logged cache read (0 when absent), so a call
        # without a cache counter counts as uncached: the dearer reading.
        prompt, cached = usage.get('prompt') or 0, usage.get('cached') or 0
        uncached = max(prompt - cached, 0)
        write, write_missing = counter(usage, 'cache_write')
        if usage.get('cache_write') is not None and not write_missing:
            # Every call logs its cache write, so the write fee is measured, not a range.
            write_price = p['cache_write_per_m'] if p['cache_write_per_m'] is not None else inp
            first = max(uncached - write, 0) * inp + write * write_price
        else:
            first = uncached * inp * (1.25 if (not low and OPENAI_WRITE_BILLED.match(name)) else 1.0)
        return (first + cached * read + output * out) / M
    # muse: input as logged; cache semantics unverified.
    prompt, cached = usage.get('prompt') or 0, usage.get('cached') or 0
    uncached = max(prompt - cached, 0) if low else prompt
    return (uncached * inp + cached * read + output * out) / M


def bill(rows, prices):
    out = []
    for u in rows:
        agent, label = u['agent'], u.get('model')
        name = normalise(label)
        priced_as = PROXY.get(name, name)
        cls = 'local' if name in LOCAL else CLASS.get(name, 'unknown')
        rec = dict(agent=agent, model=label, price_name=name, priced_as=priced_as if priced_as != name else '',
                   cls=cls, calls=u.get('calls', 0), prompt=u.get('prompt', 0), cached=u.get('cached', 0),
                   output=u.get('output', 0), reasoning=u.get('reasoning', 0), low=None, high=None, note='',
                   qwen_low=None, qwen_high=None)
        if cls == 'local':
            rec['note'] = 'own machine, no API bill'
            out.append(rec)
            continue
        qwen = prices.get(QWEN, [])
        if qwen:
            rec['qwen_low'] = min(price_row(agent, QWEN, u, p, True) for p in qwen)
            rec['qwen_high'] = max(price_row(agent, QWEN, u, p, False) for p in qwen)
        periods = prices.get(priced_as)
        if not periods:
            rec['note'] = 'no list price'
            out.append(rec)
            continue
        lows = [price_row(agent, name, u, p, True) for p in prices.get(LOW_VARIANT.get(name), []) + periods]
        highs = [price_row(agent, name, u, p, False) for p in periods]
        rec['low'], rec['high'] = min(lows), max(highs)
        notes = []
        if priced_as != name:
            notes.append(f'proxy price {priced_as}')
        if label and normalise(label) != re.sub(r'-20\d{6}$', '', label.strip().lower()):
            notes.append(f'label read as {name}')
        if len(periods) > 1:
            notes.append('price changed during the year')
        if name in LOW_VARIANT:
            notes.append('low bound at Contributor-mode price')
        missing = {k: v for k, v in (u.get('unknown_counter_calls') or {}).items()
                   if k in ('uncached_input', 'cache_write', 'cache_read', 'raw_output') and v}
        if agent == 'claude' and missing:
            notes.append('calls missing counters: ' + ', '.join(f'{k} {v}' for k, v in sorted(missing.items())))
        if agent == 'claude':
            excess = counter(u, 'cache_write_5m')[0] + counter(u, 'cache_write_1h')[0] - counter(u, 'cache_write')[0]
            rec['ttl_excess'] = max(excess, 0)
            if excess > 0:
                notes.append(f'TTL split exceeds total write by {excess:.0f} tokens (independent maxima), priced as logged')
        rec['note'] = '; '.join(notes)
        out.append(rec)
    return out


def summary(recs):
    priced = [r for r in recs if r['low'] is not None]
    calls = sum(r['calls'] for r in recs)
    s = dict(calls=calls, priced_calls=sum(r['calls'] for r in priced),
             low=sum(r['low'] for r in priced), high=sum(r['high'] for r in priced),
             claude_ttl_excess_tokens=sum(r.get('ttl_excess', 0) for r in recs), by_class={})
    for cls in ('at_or_below', 'effort', 'above', 'unclassified', 'unknown', 'local'):
        rs = [r for r in recs if r['cls'] == cls]
        ps = [r for r in rs if r['low'] is not None]
        s['by_class'][cls] = dict(calls=sum(r['calls'] for r in rs), priced_calls=sum(r['calls'] for r in ps),
                                  low=sum(r['low'] for r in ps), high=sum(r['high'] for r in ps),
                                  qwen_low=sum(r['qwen_low'] for r in ps), qwen_high=sum(r['qwen_high'] for r in ps))
    return s


def write_csv(recs, path):
    keys = ['agent', 'model', 'price_name', 'priced_as', 'cls', 'calls', 'prompt', 'cached', 'output', 'reasoning',
            'low', 'high', 'qwen_low', 'qwen_high', 'note']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in sorted(recs, key=lambda r: -(r['high'] or 0)):
            w.writerow({k: (round(r[k], 2) if k in ('low', 'high', 'qwen_low', 'qwen_high') and r[k] is not None
                            else r[k]) for k in keys})


def selftest():
    prices = load_prices(os.path.join(HERE, 'model-prices-2026-10.csv'))

    def row(agent, model, **kw):
        base = dict(agent=agent, model=model, calls=1, prompt=0, cached=0, output=0, reasoning=0,
                    unknown_counter_calls={})
        for k, v in kw.items():
            if k in ('prompt', 'cached', 'output', 'reasoning', 'unknown_counter_calls'):
                base[k] = v
            else:
                # A raw counter reported by every call: strict total and reported sum agree, as in the export.
                base[k] = base[k + '_reported_sum'] = v
        return base
    # Claude: 1M uncached, 1M write without TTL, 1M read, 1M output on Opus 4.5 ($5 / $0.50 / 1.25x-2x / $25):
    # low 5 + 6.25 + 0.5 + 25 = 36.75, high 5 + 10 + 0.5 + 25 = 40.5. The snapshot suffix maps to the base name.
    r = bill([row('claude', 'claude-opus-4-5-20251101', uncached_input=M, cache_write=M, cache_read=M, raw_output=M)],
             prices)[0]
    assert (round(r['low'], 2), round(r['high'], 2), r['cls']) == (36.75, 40.5, 'at_or_below'), r
    # A logged TTL split is priced exactly, with no range: 5-minute 0.5M and 1-hour 0.5M on the same row.
    r = bill([row('claude', 'claude-opus-4-5', cache_write=M, cache_write_5m=M / 2, cache_write_1h=M / 2)], prices)[0]
    assert round(r['low'], 4) == round(r['high'], 4) == round((0.5 * 1.25 + 0.5 * 2) * 5, 4), r
    # Codex GPT-6.1 Sol: 2M inclusive input with 1M cached, 1M output: uncached 1M at $2 (low) or $2.50 (high),
    # read $0.10, output $10.
    r = bill([row('codex', 'gpt-6.1-sol', prompt=2 * M, cached=M, output=M, raw_output=M)], prices)[0]
    assert (round(r['low'], 2), round(r['high'], 2)) == (12.1, 12.6), r
    # Negative: reasoning never adds to the bill; the same row with 1M reasoning costs the same.
    r2 = bill([row('codex', 'gpt-6.1-sol', prompt=2 * M, cached=M, output=M, raw_output=M, reasoning=M)], prices)[0]
    assert (r2['low'], r2['high']) == (r['low'], r['high']), r2
    # Negative: an unknown label is reported, unpriced and outside the bill, but its calls still count.
    recs = bill([row('claude', 'claude-test', uncached_input=M), row('codex', 'gpt-5.1', prompt=M, raw_output=0)],
                prices)
    s = summary(recs)
    assert recs[0]['low'] is None and recs[0]['note'] == 'no list price' and s['calls'] == 2 and s['priced_calls'] == 1
    assert round(s['low'], 2) == 1.25 and s['by_class']['unknown']['calls'] == 1, s
    # A price change yields the range of the periods: GPT-5.6 Sol 1M output costs $20 now and $30 before 2026-08-21.
    r = bill([row('codex', 'gpt-5.6-sol', output=M, raw_output=M)], prices)[0]
    assert (r['low'], r['high']) == (20.0, 30.0), r
    # Proxy pricing is labelled: Codex Spark has no API price and is priced as GPT-5.3 Codex.
    r = bill([row('codex', 'gpt-5.3-codex-spark', output=M, raw_output=M)], prices)[0]
    assert r['priced_as'] == 'gpt-5.3-codex' and r['low'] == 14.0 and 'proxy' in r['note'], r
    # A Codex row that logs its cache writes for every call is priced exactly: a measured zero write leaves no range
    # even on GPT-6.x, whose write fee is 1.25x input.
    r = bill([row('codex', 'gpt-6.1-sol', prompt=2 * M, cached=M, output=M, raw_output=M, cache_write=0)], prices)[0]
    assert (round(r['low'], 2), round(r['high'], 2)) == (12.1, 12.1), r
    # Negative: a label of a model on the owner's machine never enters the API bill, but its calls are counted.
    recs = bill([row('codex', 'Qwen3.6-27B', prompt=M, cached=0, output=M, raw_output=M)], prices)
    s = summary(recs)
    assert recs[0]['cls'] == 'local' and recs[0]['low'] is None and s['low'] == 0 and s['calls'] == 1, recs
    # An alias is read as the priced variant and labelled: Contributor-free is priced as Contributor mode.
    r = bill([row('codex', 'muse-spark-1.3-contributor-free', prompt=M, cached=0, output=0, raw_output=0,
                  cache_write=0)], prices)[0]
    assert r['price_name'] == 'muse-spark-1.3-contributor' and r['low'] == 0.1 and 'label read as' in r['note'], r
    # Negative: a TTL split larger than the total write is not normalized away; it is priced as logged and reported.
    r = bill([row('claude', 'claude-opus-4-5', cache_write=100, cache_write_5m=60, cache_write_1h=50)], prices)[0]
    assert r['ttl_excess'] == 10 and 'exceeds total write by 10' in r['note'], r
    assert abs(r['low'] - (60 * 1.25 * 5 + 50 * 2 * 5) / M) < 1e-12 and r['low'] == r['high'], r
    # The Qwen3.8-27B reference prices the same tokens: 1M uncached Claude input costs $0.50 there.
    r = bill([row('claude', 'claude-opus-4-5', uncached_input=M)], prices)[0]
    assert (r['qwen_low'], r['qwen_high']) == (0.5, 0.5), r
    print('self-test ok')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('usage', nargs='?')
    ap.add_argument('--prices', default=os.path.join(HERE, 'model-prices-2026-10.csv'))
    ap.add_argument('--out', default=os.path.join(HERE, 'year-bill.csv'))
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return selftest()
    if not a.usage:
        ap.error('usage JSON required')
    data = json.load(open(a.usage))
    rows = data['model_usage'] if isinstance(data, dict) else data
    recs = bill(rows, load_prices(a.prices))
    write_csv(recs, a.out)
    print(json.dumps(summary(recs), indent=1))


if __name__ == '__main__':
    sys.exit(main())
