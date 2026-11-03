#!/usr/bin/env python3
"""Chart inputs for the economics and million-token sections, derived from the engine snapshot in engine/.

Engine: hybrid-calc run 11 (commit in engine/SOURCE.txt). Files without a suffix are the design hosting case;
*_conservative.csv are the conservative case.
- team-cost-s20.csv, team-cost-s50.csv: USD per person-month for the M5 Max 64 GB client (Q4 server and client,
  decision case): own cluster, API at the median and the cheapest provider, and the hybrid with overflow to the
  cheapest API, for a Mac already owned and for a Mac bought at its laptop premium; *_cons columns give the
  conservative hosting case.
- payback.csv: months until the saving against the median API pays the laptop premium (PRICE - BASELINE) or the
  whole Mac (PRICE); hybrid with overflow to the cheapest API, Mac already owned; s=100% uses the academic bound.
  The *_median_overflow columns leave the calls above client capacity at the median API instead.
- glm-1m-cost.csv: USD per GLM-5.3-Flash session at a final depth of 1M tokens: API, own cluster, and the hybrid on an
  M5 Ultra 256 GB.
Run: python3 derive_charts.py
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, 'engine')
PRICE, BASELINE = 5099, 2499  # engine paper-tables.json: M5 Max 64 GB purchase_price and premium_credit (estimates)
CLIENT = 'M5 Max 64 GB'


def rows(name):
    with open(os.path.join(ENGINE, name), newline='') as f:
        return list(csv.DictReader(f))


def person(share, suffix=''):
    """{(team, basis): row} for the paper's client and decision case."""
    name = f'person_cost_academic_s100{suffix}.csv' if share == 100 else f'person_cost_s{share}{suffix}.csv'
    out = {}
    for r in rows(name):
        # The 100% table is the academic bound (all work on the open model, before overflow decisions).
        bound = 'academic bound' if share == 100 else 'decision case'
        if (r['client'] == CLIENT and r['server_precision'] == 'Q4' and r['client_quant'] == 'Q4'
                and r['bound'] == bound):
            out[(int(r['team']), r['basis'])] = r
    return out


def write(name, keys, data):
    with open(os.path.join(HERE, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(keys)
        w.writerows(data)


def main():
    owned, bought = 'Mac already owned', 'Mac premium bought'
    pay = []
    for share in (20, 50, 100):
        design, cons = person(share), person(share, '_conservative')
        teams = sorted({t for t, _ in design})
        if share in (20, 50):
            write(f'team-cost-s{share}.csv',
                  ['team', 'own', 'api_median', 'api_cheapest', 'hybrid_owned', 'hybrid_bought',
                   'hybrid_owned_cons', 'hybrid_bought_cons'],
                  [[t, *(round(float(design[(t, owned)][k]), 2) for k in ('own_cluster', 'api_median', 'api_cheapest',
                                                                          'hybrid_cheapest')),
                    round(float(design[(t, bought)]['hybrid_cheapest']), 2),
                    round(float(cons[(t, owned)]['hybrid_cheapest']), 2),
                    round(float(cons[(t, bought)]['hybrid_cheapest']), 2)] for t in teams])
        r, c = design[(teams[0], owned)], cons[(teams[0], owned)]
        hybrid, hybrid_c, hybrid_m = float(r['hybrid_cheapest']), float(c['hybrid_cheapest']), float(r['hybrid_median'])
        median, cheapest = float(r['api_median']), float(r['api_cheapest'])
        saving, saving_c, saving_m = median - hybrid, median - hybrid_c, median - hybrid_m
        pay.append([share, round(hybrid, 2), round(median, 2), round(cheapest, 2), round(saving, 2),
                    round((PRICE - BASELINE) / saving, 2), round(PRICE / saving, 2), round(cheapest - hybrid, 2),
                    round(hybrid_c, 2), round((PRICE - BASELINE) / saving_c, 2), round(PRICE / saving_c, 2),
                    round(hybrid_m, 2), round((PRICE - BASELINE) / saving_m, 2), round(PRICE / saving_m, 2)])
    write('payback.csv', ['share', 'hybrid', 'api_median', 'api_cheapest', 'saving_median', 'premium_months',
                          'whole_months', 'saving_cheapest', 'hybrid_cons', 'premium_months_cons',
                          'whole_months_cons', 'hybrid_median_overflow', 'premium_months_median_overflow',
                          'whole_months_median_overflow'], pay)
    glm = {}
    for suffix in ('', '_conservative'):
        for r in rows(f'glm_long_sessions{suffix}.csv'):
            if r['context'] == '1000000':
                glm.setdefault(int(r['team']), {})[suffix] = r
    write('glm-1m-cost.csv', ['team', 'api', 'own', 'hybrid', 'hybrid_cons'],
          [[t, round(float(v['']['api_session']), 2), round(float(v['']['own_cluster_session']), 2),
            round(float(v['']['hybrid_session']), 2), round(float(v['_conservative']['hybrid_session']), 2)]
           for t, v in sorted(glm.items())])


if __name__ == '__main__':
    main()
