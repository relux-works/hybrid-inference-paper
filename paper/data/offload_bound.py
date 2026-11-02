#!/usr/bin/env python3
"""Checks the worked example of the offload bound in the channel section against the engine snapshot.

The channel bound is: the time an ideal local engine at the client's peak needs to read a
portion, divided by the time the link needs to carry its delta. The text adds the server's prefill time to the
transfer for one example (Qwen3.8-27B, 10 000-token portion, depth 110 000, 32-bit state, M5 Max at its 60 TFLOPS
peak, the B300 server at the engine's effective prefill rate) and states the ceiling that server speed sets on any
link. Session reload, delta import and the last token are excluded, so the example values are upper bounds.
Run: python3 offload_bound.py            (exit 0 when the text matches)
     python3 offload_bound.py --self-test (a planted wrong value must fail)
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTION = os.path.join(HERE, '..', 'sections', '04-channel.tex')
ENGINE = os.path.join(HERE, 'engine')
EXAMPLE = ('Qwen3.8-27B', '32', 'M5 Max 128 GB', '10000', '110000')


def server_rate():
    """The B300 effective prefill rate the engine used for the end-to-end turn table."""
    with open(os.path.join(ENGINE, 'turn_speedup.csv'), newline='') as f:
        rates = {float(r['server_compute']) for r in csv.DictReader(f)}
    assert len(rates) == 1, rates
    return rates.pop()


def values():
    rows = {}
    with open(os.path.join(ENGINE, 'flop_per_byte.csv'), newline='') as f:
        for r in csv.DictReader(f):
            if (r['model'], r['state_bits'], r['client'], r['portion_tokens'], r['depth']) == EXAMPLE:
                rows[float(r['link_mbit'])] = r
    server = server_rate()
    out = {}
    for link in (1000.0, 10000.0):
        r = rows[link]
        work = float(r['portion_tokens']) * float(r['flop_new_token'])
        local = work / float(r['client_peak_flop_s'])
        transfer = float(r['delta_bytes']) / (link * 1e6 / 8)
        bound = local / transfer
        # The recomputed bound must equal the engine's own ratio column.
        assert abs(bound - float(r['ratio'])) <= 1e-9 * bound, (bound, r['ratio'])
        out[link] = (bound, local / (work / server + transfer))
    ceiling = server / float(rows[1000.0]['client_peak_flop_s'])
    return out, ceiling


def expected():
    out, ceiling = values()
    return [f'граница равна {out[1000.0][0]:.1f};', f'не больше {out[1000.0][1]:.1f} раза',
            f'граница вырастает до {out[10000.0][0]:.0f},', f'выигрыш не больше {out[10000.0][1]:.0f} раз.',
            f'Выше {ceiling:.1f} раза', f'со скоростью {server_rate() / 1e15:.2f}~PFLOPS']


def missing(text):
    flat = ' '.join(text.split())
    return [s for s in expected() if s not in flat]


def main():
    text = open(SECTION, encoding='utf-8').read()
    if '--self-test' in sys.argv:
        # Negative control: the channel bound written where the end-to-end value belongs must be reported.
        flat = ' '.join(text.split())
        bad = flat.replace(expected()[1], 'не больше 4.0 раза')
        assert bad != flat and missing(bad) == [expected()[1]], missing(bad)
        # Positive control: the current text passes.
        assert not missing(text), missing(text)
        print('self-test ok')
        return 0
    gaps = missing(text)
    for s in expected():
        print(s + ('  MISSING' if s in gaps else ''))
    return 1 if gaps else 0


if __name__ == '__main__':
    sys.exit(main())
