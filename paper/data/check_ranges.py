#!/usr/bin/env python3
"""Checks the published figures and the stated directions of the paper against the engine snapshot in engine/.

Scope: the sites listed in SITES and DIRECTION_SITES, the two tables, and a guard over all of paper/sections/*.tex.

Values: each figure in SITES is recomputed from engine/*.csv (run 16, historical Q4 scenario), payback.csv and the engine inputs named below,
rounded the way the text prints it, and must appear at each site SITES lists for it (a paragraph or one sentence, white
space normalised). The rows of the client table (tab:econ) and the closed-perimeter table (tab:perimeter) are checked
cell by cell.

Directions: directions() evaluates each comparison in DIRECTION_SITES on the engine rows (which option is cheaper, what
grows or falls), and each is bound to the wording that states it at each listed site. A comparison the engine no longer
supports, or a listed site whose wording is missing or flipped, is reported. Both routes use all hardware
at every team size and identical retention and mean/p90 prefill budgets. The former artificial team-cap sites
now bind those shared constraints; no publication site is dropped. Every storage-tier candidate is checked in
symmetric_storage_candidates*.csv. Tiered hosting follows the unchanged engine-input formula.

Guard: every distinctive printed form of a checked figure (ranges, dollar amounts, decimals with three or more digits,
and the word forms in CORE_FORMS) is searched in every section. An occurrence outside the sites registered for a figure
with that form, outside the two tables and outside ALLOW (each entry with its reason) is reported, so a figure printed
in the checker's form in a new place is reported; other spellings and values already stale when written are not.

Run: python3 check_ranges.py            (exit 0 when the text matches)
     python3 check_ranges.py --self-test (a planted stale value or flipped wording at each site must be reported)
"""
import csv, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = os.path.join(HERE, '..', 'sections')
FILES = ('00-abstract.tex', '02-workload.tex', '91-calculation-history.tex', '08-million.tex', '14-conclusion.tex')
TEAMS = (50, 500, 5000)
LIGHT_ENDS = (TEAMS[0], TEAMS[-1])  # light load: the hybrid is cheaper at these team sizes
CLIENT, OWNED, BOUGHT = 'M5 Max 64 GB', 'Mac already owned', 'Mac premium bought'
MAX = ('M3 Max 128 GB (measured)', 'M4 Max 128 GB (estimate)', 'M5 Max 64 GB', 'M5 Max 128 GB')
CLIENTS = MAX + ('M5 Ultra 96 GB', 'M5 Ultra 256 GB')
ULTRA = CLIENTS[len(MAX):]
B300 = 'Owned HGX B300 8-GPU'
ENGINE_DATA = os.path.join(HERE, '..', '..', 'calc', 'hybridcalc', 'data')
# Stated inputs of the economics section used by the million-token restore arithmetic.
TRAFFIC_USD_TB, LINK_BIT_S = 5.0, 1e9


def rows(name):
    with open(os.path.join(HERE, 'engine', name), newline='') as f:
        return list(csv.DictReader(f))


def money(v):
    return '\\$' + f'{v:,.0f}'.replace(',', '\\,')


def compact_span(values, digits=1):
    """Identical rounded endpoints print once; precision is unchanged."""
    low, high = (f'{fn(values):.{digits}f}' for fn in (min, max))
    return low if low == high else low + '--' + high


def span(values, digits=1):
    return compact_span(values, digits)


WORDS = {1: 'одна', 2: 'две', 3: 'три', 4: 'четыре', 5: 'пять', 6: 'шесть', 7: 'семь', 8: 'восемь', 9: 'девять',
         10: 'десять', 11: 'одиннадцать', 12: 'двенадцать', 13: 'тринадцать', 14: 'четырнадцать', 15: 'пятнадцать',
         16: 'шестнадцать', 17: 'семнадцать', 18: 'восемнадцать', 19: 'девятнадцать', 20: 'двадцать'}
GENITIVE = {4: 'четырёх', 5: 'пяти', 6: 'шести', 7: 'семи'}


def need_cards(n, such=False):
    """'нужна одна карта', 'нужны две карты', 'нужно пять карт': verb and noun agree with n (Russian number agreement)."""
    word = WORDS.get(n, str(n))
    if n % 10 == 1 and n % 100 != 11:
        return f'нужна {word} {"такая " if such else ""}карта'
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f'нужны {word} {"такие " if such else ""}карты'
    return f'нужно {word} {"таких " if such else ""}карт'


def minutes(n):
    """'одну минуту', 'две минуты', 'пять минут': accusative of a whole number of minutes."""
    if n % 10 == 1 and n % 100 != 11:
        return f'{"одну" if n == 1 else n} минуту'
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f'{WORDS.get(n, n)} минуты'
    return f'{WORDS.get(n, n)} минут'


def months(n):
    """Russian agreement of 'месяц' with a whole number."""
    if n % 10 == 1 and n % 100 != 11:
        return 'месяц'
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return 'месяца'
    return 'месяцев'


# ---------------------------------------------------------------- closed perimeter

def perimeter(name):
    """Selected costs by (profile, team, kind) and every option by (profile, team, route, server)."""
    sel, opt = {}, {}
    for r in rows(name):
        route = r['route']
        if route == 'hybrid' and not (r['client'] == CLIENT and r['basis'] == OWNED):
            continue
        if route == 'Macs only':
            if r['client'] == CLIENT and r['basis'] == OWNED and r['selected'] == '1':
                sel[(r['profile'], int(r['team']), 'served')] = 100 * float(r['client_served_share'])
            continue
        key = (r['profile'], int(r['team']), route, r['server'], r['storage_tier'])
        opt[key] = dict(cost=float(r['person_month']), eligible=r['eligible'] == '1', selected=r['selected'] == '1',
                        units=int(float(r['units'])) if r['units'] not in ('', 'nan') else 0)
        if r['selected'] == '1':
            kind = 'own' if route == 'all server' else 'hybrid'
            sel[(r['profile'], int(r['team']), kind)] = float(r['person_month'])
            sel[(r['profile'], int(r['team']), kind + '_server')] = r['server']
            sel[(r['profile'], int(r['team']), kind + '_units')] = opt[key]['units']
    return sel, opt


def perimeter_rows(design, cons):
    calls = {'light': '200', 'medium': '800', 'heavy': '2\\,500'}
    return [f'{calls[p]} & {t} & \\${design[(p, t, "own")]:.0f} & \\${design[(p, t, "hybrid")]:.0f} & '
            f'\\${cons[(p, t, "hybrid")]:.0f} & {design[(p, t, "served")]:.0f}\\% \\\\'
            for p in ('light', 'medium', 'heavy') for t in TEAMS]


TWO_CARD = '2x RTX PRO 6000 Server; own perimeter rack'


def symmetric_budgets():
    """Both routes share budgets; every hardware/tier remains an exported candidate."""
    for name in ('symmetric_storage_candidates.csv', 'symmetric_storage_candidates_conservative.csv'):
        data = [r for r in rows(name) if r['route'] == 'all server' or
                (r['route'] == 'hybrid' and r['client'] == CLIENT and r['basis'] == OWNED)]
        for profile in ('light', 'medium', 'heavy'):
            for team in (5, 10, 20, 50, 500, 5000):
                group = [r for r in data if r['profile'] == profile and int(r['team']) == team]
                for key in ('retention', 'retained_sessions', 'latency_mean_limit_s', 'latency_p90_limit_s'):
                    if len({r[key] for r in group}) != 1:
                        return False
                for route in ('all server', 'hybrid'):
                    rs = [r for r in group if r['route'] == route]
                    if {r['storage_tier'] for r in rs} != {'HBM', 'RAM', 'NVMe'}:
                        return False
                    if any(r['office_policy'] != 'uncapped cheapest admissible fleet' for r in rs):
                        return False
                    for r in rs:
                        want = (float(r['prefill_mean_s']) <= float(r['latency_mean_limit_s']) and
                                float(r['prefill_p90_s']) <= float(r['latency_p90_limit_s']))
                        if (r['eligible'] == '1') != want:
                            return False
    return True


# ---------------------------------------------------------------- own servers for 5 and 20 people

def own_servers():
    """Selected fleets plus the unique light-load, one-node B300 reference.

    Run 14 sizes other profiles independently; their costs cannot supply the
    printed $3,373/$845 amounts. Require row uniqueness, including equal prices.
    """
    selected, b300 = {}, {}
    for r in rows('perimeter_cost.csv'):
        if r['route'] != 'all server':
            continue
        if r['selected'] == '1':
            selected[(r['profile'], int(r['team']))] = r
        if r['server'] == B300 and r['profile'] == 'light' and int(r['team']) in (5, 20):
            b300.setdefault(int(r['team']), []).append(r)
    for team in (5, 20):
        candidates = b300.get(team, [])
        assert len(candidates) == 1, f'B300 light profile: exactly one row for team {team}'
        row = candidates[0]
        assert float(row['units']) == 1, f'B300 light profile: one node for team {team}'
        b300[team] = float(row['person_month'])
    return selected, b300


def cards_sentence(selected, team, such):
    """'нужна одна карта при лёгкой нагрузке и четырнадцать, по две в сервере, при тяжёлой', from the selected rows."""
    def count(profile):
        r = selected[(profile, team)]
        assert 'RTX PRO 6000' in r['server'], ('own server is not RTX PRO 6000', profile, team)
        per = int(r['server'].split('x', 1)[0])
        return int(float(r['units'])) * per, per
    light, _ = count('light')
    heavy, per = count('heavy')
    return f'{need_cards(light, such)} при лёгкой нагрузке и {WORDS.get(heavy, str(heavy))} при тяжёлой'


# ---------------------------------------------------------------- per-person economics

def person(name, basis=OWNED, team=None):
    """Per-person monthly figures by client; for team=None they must not depend on team size."""
    out, seen = {}, {}
    for r in rows(name):
        if r['basis'] != basis or (team is not None and int(r['team']) != team):
            continue
        row = {k: float(r[k]) for k in r if k not in ('team', 'client', 'basis', 'server_precision', 'client_quant',
                                                        'bound', 'status', 'alarm_inputs', 'accounting_case')
               and r[k] not in ('', 'nan') and re.fullmatch(r'-?[0-9.e+-]+', r[k])}
        if team is None:
            keep = {k: row[k] for k in ('hybrid_cheapest', 'hybrid_median', 'api_median', 'api_cheapest',
                                        'served_day', 'requested_day', 'capacity_day')}
            assert seen.setdefault(r['client'], keep) == keep, ('team-dependent per-person cost', name, r['client'])
            out[r['client']] = dict(row, **keep)
        else:
            out[r['client']] = row
    return out


def econ_rows(s20, s50, b50):
    label = lambda k: k.split(' (')[0].replace(' GB', ' ГБ')
    cap = lambda v: f'{v:,.0f}'.replace(',', '\\,')
    out = [f'{label(k)} & {cap(s20[k]["capacity_day"])} & \\${s20[k]["hybrid_cheapest"]:.1f} & '
           f'\\${s50[k]["hybrid_cheapest"]:.1f} & \\${b50[k]["hybrid_cheapest"]:.1f} \\\\' for k in CLIENTS]
    a20, a50 = s20[CLIENTS[0]], s50[CLIENTS[0]]
    out.append(f'API, медианный поставщик & & \\${a20["api_median"]:.1f} & \\${a50["api_median"]:.1f} & '
               f'\\${a50["api_median"]:.1f} \\\\')
    out.append(f'API, самый дешёвый поставщик & & \\${a20["api_cheapest"]:.1f} & \\${a50["api_cheapest"]:.1f} & '
               f'\\${a50["api_cheapest"]:.1f} \\\\')
    return out


def upper_bound():
    """Base (output) and upper bound (reasoning on top) for M5 Max 64 GB already owned, team 50."""
    out = {}
    for r in rows('reasoning_on_top_sensitivity.csv'):
        if r['client'] == CLIENT and r['basis'] == OWNED:
            out[(r['accounting_case'].startswith('reasoning'), round(float(r['share']) * 100))] = {
                k: float(r[k]) for k in ('capacity_day', 'hybrid_cheapest', 'api_median', 'api_cheapest')}
    return out


# ---------------------------------------------------------------- million tokens

def glm():
    """GLM-5.3-Flash at a final depth of 1M: per-team rows, two sessions a day, and the Studio utilization rows."""
    long_rows = {int(r['team']): {k: float(r[k]) for k in ('api_session', 'own_cluster_session', 'hybrid_session')}
                 for r in rows('glm_long_sessions.csv') if r['context'] == '1000000'}
    short = [r for r in rows('glm_long_sessions.csv') if r['context'] == '200000']
    util = {}
    for name, policy in (('glm_utilization.csv', 'design'), ('glm_utilization_conservative.csv', 'conservative')):
        for r in rows(name):
            if r['context'] != '1000000' or r['users_per_studio'] not in ('1', '2'):
                continue
            demand = 'full' if r['demand_mode'] == 'capacity' else f'{float(r["requested_user_day"]):g}/day'
            util[(policy, int(r['team']), int(r['users_per_studio']), demand)] = {
                k: float(r[k]) for k in ('api_session', 'own_cluster_session', 'hybrid_session', 'studio_session',
                                         'capacity_studio_day', 'utilization')}
    return long_rows, float(short[0]['api_session']), util


def refill_hours():
    """M3 Max refill of 1M tokens from the tab:m3max segments (02-workload.tex), linear beyond the last midpoint."""
    with open(os.path.join(SECTIONS, '02-workload.tex'), encoding='utf-8') as stream:
        text = stream.read()
    nums = lambda prefix: [float(x) for x in re.search(re.escape(prefix) + r'(.*?)\\\\', text).group(1).split('&')[1:]]
    mids = [m * 1e3 for m in nums('Глубина контекста, тыс. токенов')]
    t = [1 / r for r in nums('Prefill, токенов/с')]
    def tok(n, slope):
        if n <= mids[0]:
            return t[0]
        for i in range(len(mids) - 1):
            if n <= mids[i + 1]:
                return t[i] + (t[i + 1] - t[i]) * (n - mids[i]) / (mids[i + 1] - mids[i])
        return t[-1] + slope * (n - mids[-1])
    out = {}
    for start in (mids[-2], mids[-3]):  # slopes over the last segment and over the last two
        slope = (t[-1] - t[mids.index(start)]) / (mids[-1] - start)
        out[(start / 1e3, mids[-1] / 1e3)] = sum(tok(n + 500, slope) * 1000
                                                           for n in range(0, 1_000_000, 1000)) / 3600
    return out


def engine_input(name, *path):
    with open(os.path.join(ENGINE_DATA, name), encoding='utf-8') as f:
        node = json.load(f)
    for key in path:
        node = node[key]
    return float(node['value'])


def restore(hours=None, days=None):
    """Size, transfer time, traffic and storage cost of a 1M-token Qwen3.8-27B session copy. Storage under the protocol
    policy follows the engine's tiered price (Hosting.storage in session_hosting.py): RAM for paper_tables.hours x
    owners.days of economics.hours_month, NVMe otherwise; hours and days can be overridden for the self-test."""
    r = next(x for x in rows('oneshot_ingest.csv') if x['state_format'] == 'f32')
    size = float(r['kv_bytes_token']) * 1e6 + float(r['state_bytes'])
    ram = engine_input('hosting.json', 'hosting', 'tiers', 'RAM', 'price')
    nvme = engine_input('hosting.json', 'hosting', 'tiers', 'NVMe', 'price')
    hours = engine_input('paper-tables.json', 'paper_tables', 'hours') if hours is None else hours
    days = engine_input('ownership.json', 'owners', 'days') if days is None else days
    active = hours * days / engine_input('economics.json', 'economics', 'hours_month')
    return dict(gb=size / 1e9, minutes=size * 8 / LINK_BIT_S / 60, cents=size / 1e12 * TRAFFIC_USD_TB * 100,
                nvme=size / 1e9 * nvme, tiered=size / 1e9 * (active * ram + (1 - active) * nvme),
                nvme_price=nvme, ram_price=ram, nvme_read=engine_input('hosting.json', 'hosting', 'tiers', 'NVMe', 'bandwidth'))


# ---------------------------------------------------------------- payback

def payback():
    with open(os.path.join(HERE, 'payback.csv'), newline='') as f:
        return {int(r['share']): {k: float(v) for k, v in r.items()} for r in csv.DictReader(f)}


# ---------------------------------------------------------------- expected values and directions

def model():
    """Everything the checks need, computed once."""
    d, dopt = perimeter('perimeter_cost.csv')
    c, copt = perimeter('perimeter_cost_conservative.csv')
    m = dict(design=d, cons=c, dopt=dopt, copt=copt,
             s20=person('person_cost_s20.csv'), s50=person('person_cost_s50.csv'),
             s20c=person('person_cost_s20_conservative.csv'), s50c=person('person_cost_s50_conservative.csv'),
             b20=person('person_cost_s20.csv', BOUGHT), b50=person('person_cost_s50.csv', BOUGHT),
             t20=person('person_cost_s20.csv', team=500), t50=person('person_cost_s50.csv', team=500),
             t20all={t: person('person_cost_s20.csv', team=t)[CLIENT] for t in (5, 10, 20, 50, 500, 5000)},
             t50all={t: person('person_cost_s50.csv', team=t)[CLIENT] for t in (5, 10, 20, 50, 500, 5000)},
             upper=upper_bound(), pay=payback(), refill=refill_hours(), restore=restore())
    m['glm_long'], m['glm_200k'], m['glm_util'] = glm()
    return m


def values(m):
    d, c = m['design'], m['cons']
    ratio = lambda x, p, t: x[(p, t, 'own')] / x[(p, t, 'hybrid')]
    saving = lambda x, p, t: 100 * (1 - x[(p, t, 'hybrid')] / x[(p, t, 'own')])
    med_d, med_c = [ratio(d, 'medium', t) for t in TEAMS], [ratio(c, 'medium', t) for t in TEAMS]

    s20, s50, s20c, s50c, b20, b50 = (m[k] for k in ('s20', 's50', 's20c', 's50c', 'b20', 'b50'))
    cheaper = lambda x, keys: [x[k]['api_median'] / x[k]['hybrid_cheapest'] for k in keys]
    dearer = lambda x, keys: [x[k]['hybrid_cheapest'] / x[k]['api_cheapest'] for k in keys]
    served = [100 * s50[k]['served_day'] / s50[k]['requested_day'] for k in MAX]
    a20, a50 = s20[CLIENT], s50[CLIENT]
    up = m['upper']
    base50, top50, base20, top20 = up[(False, 50)], up[(True, 50)], up[(False, 20)], up[(True, 20)]
    selected, b300 = own_servers()
    own_team = lambda t: [float(r['person_month']) for (p, tt), r in selected.items() if tt == t]
    pay = m['pay']; p20, p50 = pay[20], pay[50]
    n = lambda v: round(v)
    g, util = m['glm_long'], m['glm_util']
    big = (500, 5000)
    full = [util[('design', t, 1, 'full')] for t in big]
    two = [util[('design', t, 1, '2/day')] for t in big]
    one = [util[('design', t, 1, '1/day')] for t in big]
    four = [util[('design', t, 1, '4/day')] for t in big]
    shared = [util[('design', t, 2, '2/day')] for t in big]
    api1m = g[500]['api_session']
    rf, rs = m['refill'], m['restore']
    return {
        # closed perimeter
        'medium, design': span(med_d),
        'medium, conservative': span(med_c),
        'medium, both cases': span(med_d + med_c),
        'light at 50 and 5000, design, percent': span([saving(d, 'light', t) for t in LIGHT_ENDS], 0),
        'light at 50 and 5000, conservative, percent': span([saving(c, 'light', t) for t in LIGHT_ENDS], 0),
        'light at 500, own against hybrid': f'\\${d[("light", 500, "own")]:.0f} на человека в месяц против '
                                            f'\\${d[("light", 500, "hybrid")]:.0f}',
        'light at 500, cautious symmetric comparison': f'При осторожной политике на 500 человек гибрид стоит \\${c[("light", 500, "hybrid")]:.0f} против \\${c[("light", 500, "own")]:.0f} у своего кластера',
        'heavy saving, design': span([saving(d, 'heavy', t) for t in TEAMS], 0),
        'heavy saving, conservative': span([saving(c, 'heavy', t) for t in TEAMS], 0),
        'symmetric hardware without team cap': 'без ограничения размера команды',
        'symmetric retention budget': 'одинаковые сроки хранения и число сохраняемых сессий',
        'symmetric latency budget': 'одинаковые ограничения среднего и p90 времени prefill',
        # own servers for 5 and 20 people
        'own server for five people': '\\$' + span(own_team(5), 0),
        'own server for twenty people': '\\$' + span(own_team(20), 0),
        'own server for five people, light load': f'от \\${float(selected[("light", 5)]["person_month"]):.0f} на '
                                                  f'человека в месяц при лёгкой нагрузке',
        'cards for five people': cards_sentence(selected, 5, True),
        'cards for twenty people': cards_sentence(selected, 20, False),
        'B300 node per person, five people': money(b300[5]),
        'B300 node per person, twenty people': money(b300[20]),
        # per-person economics
        'API per 1000 calls': f'стоят \\${a20["api_median"] / 10.5:.2f}, у самого дешёвого \\${a20["api_cheapest"] / 10.5:.2f}',
        'upper bound, capacity': f'с {base50["capacity_day"]:.0f} до {top50["capacity_day"]:.0f} вызовов в день',
        'upper bound, API rise': span([100 * (top50[k] / base50[k] - 1) for k in ('api_median', 'api_cheapest')], 0),
        'upper bound, s50 against median': f'\\${top50["hybrid_cheapest"]:.0f} против \\${top50["api_median"]:.0f}',
        'upper bound, s50 against cheapest': f'\\${top50["hybrid_cheapest"]:.0f} против \\${top50["api_cheapest"]:.0f} при',
        'upper bound, s20 against cheapest': f'в {top20["hybrid_cheapest"] / top20["api_cheapest"]:.1f} раза при доле 20',
        'storage against prefill': f'хранение стоит \\${s20[CLIENT]["hosting_month"]:.1f} в месяц, {"меньше" if s20[CLIENT]["hosting_month"] < s20[CLIENT]["compute_month"] else "больше"}, чем сам prefill '
                                   f'(\\${s20[CLIENT]["compute_month"]:.1f})',
        'conservative storage': f'обходится в \\${s20c[CLIENT]["hosting_month"]:.1f}',
        's20 hybrid dollars': '\\$' + span([s20[k]['hybrid_cheapest'] for k in CLIENTS], 0) + ' в месяц',
        's20 API dollars': f'(\\${a20["api_cheapest"]:.0f}), и в',
        's20 API median dollars': f'(\\${a20["api_median"]:.0f})',
        's20 below median, all clients, both cases': span(cheaper(s20, CLIENTS) + cheaper(s20c, CLIENTS)),
        's20 above cheapest, all clients, both cases': span(dearer(s20, CLIENTS) + dearer(s20c, CLIENTS)),
        's20 below median, Max clients, both cases': span(cheaper(s20, MAX) + cheaper(s20c, MAX)),
        's20 below median, all clients, design': span(cheaper(s20, CLIENTS)),
        's20 above cheapest, all clients, design': span(dearer(s20, CLIENTS)),
        's20 below median, all clients, conservative': span(cheaper(s20c, CLIENTS)),
        's20 above cheapest, all clients, conservative': span(dearer(s20c, CLIENTS)),
        's50 M5 Max capacity': f'около {round(s50[CLIENT]["capacity_day"], -1):.0f} вызовов',
        's50 Max dollars': '\\$' + span([s50[k]['hybrid_cheapest'] for k in MAX], 0) + ' в месяц',
        's50 API dollars': f'(\\${a50["api_cheapest"]:.0f}) и в',
        's50 API median dollars': f'(\\${a50["api_median"]:.0f})',
        's50 below median, Max clients': span(cheaper(s50, MAX)),
        's50 above cheapest, Max clients, percent': span([100 * (x - 1) for x in dearer(s50, MAX)], 0),
        's50 below median, Max clients, overflow at median': span([s50[k]['api_median'] / s50[k]['hybrid_median']
                                                                    for k in MAX]),
        's50 share served by Max clients': f'от {min(served):.0f} до {max(served):.0f}\\%',
        's50 Ultra dollars': 'обходятся в \\$' + span([s50[k]['hybrid_cheapest'] for k in ULTRA], 0),
        's50 Ultra conservative dollars': 'и в \\$' + span([s50c[k]['hybrid_cheapest'] for k in ULTRA], 0)
                                          + ' при осторожной политике',
        's50 above cheapest, Ultra clients, percent': span([100 * (x - 1) for x in dearer(s50, ULTRA)], 0),
        's50 below median, Ultra clients, both cases': span(cheaper(s50, ULTRA) + cheaper(s50c, ULTRA)),
        'purchase at 50%': f'стоит \\${b50[CLIENT]["hybrid_cheapest"]:.0f} против \\${a50["api_cheapest"]:.0f} у самого '
                           f'дешёвого API и \\${a50["api_median"]:.0f} у медианного',
        'purchase at 20%': f'\\${b20[CLIENT]["hybrid_cheapest"]:.0f} против \\${a20["api_median"]:.0f}',
        'purchase against cheapest': f'дороже его на \\${b50[CLIENT]["hybrid_cheapest"] - a50["api_cheapest"]:.0f} в месяц',
        'teams at 500, 20%': f'(\\${m["t20"][CLIENT]["own_cluster"]:.0f} против \\${a20["api_median"]:.0f} при доле 20\\%',
        'teams at 500, 50%': f'\\${m["t50"][CLIENT]["own_cluster"]:.0f} против \\${a50["api_median"]:.0f} при доле 50\\%',
        'payback s50, overflow to cheapest': f'за {n(p50["premium_months"])} {months(n(p50["premium_months"]))}, Мак '
                                             f'целиком за {n(p50["whole_months"])}',
        'payback s20, overflow to cheapest': f'за {n(p20["premium_months"])} и {n(p20["whole_months"])} '
                                             f'{months(n(p20["whole_months"]))}',
        'payback s50, overflow to median': f'за {n(p50["premium_months_median_overflow"])} '
                                           f'{months(n(p50["premium_months_median_overflow"]))}',
        'payback s50, overflow to median, whole': f'целиком за {n(p50["whole_months_median_overflow"])}',
        'payback, dearer than cheapest': span([-p['saving_cheapest'] for p in (p20, p50)], 0),
        # million tokens
        'GLM API session to 1M': f'\\${api1m:.2f}',
        'GLM API session to 200k': f'стоит \\${m["glm_200k"]:.2f}',
        'GLM growth of the session cost': f'сессия дороже в {api1m / m["glm_200k"]:.0f} раз',
        'GLM two sessions, hybrid': f'гибрид обходится в \\${span([g[t]["hybrid_session"] for t in big])} за сессию',
        'GLM two sessions, own cluster': f'свой кластер стоит \\${g[500]["own_cluster_session"]:.2f}',
        'GLM two sessions, own cluster at 5000': f'на 5000 человек \\${g[5000]["own_cluster_session"]:.2f}',
        'GLM 50 people': f'(\\${g[50]["own_cluster_session"]:.2f}) немного дешевле API (\\${g[50]["api_session"]:.2f}), а '
                         f'гибрид с отдельной Studio на каждого дороже обоих (\\${g[50]["hybrid_session"]:.2f})',
        'GLM Studio utilization at two sessions': ('меньше чем на треть' if max(v['utilization'] for v in two) < 1 / 3
                                                   else f'на {100 * max(v["utilization"] for v in two):.0f}\\%'),
        'GLM Studio capacity': f'почти {WORDS[math.ceil(two[0]["capacity_studio_day"])]} сессий',
        'GLM full load, Studio share': f'до \\${full[0]["studio_session"]:.2f} на сессию',
        'GLM full load, hybrid session': '\\$' + span([v['hybrid_session'] for v in full]),
        'GLM full load, below API': span([v['api_session'] / v['hybrid_session'] for v in full]),
        'GLM full load, below own cluster': compact_span([v['own_cluster_session'] / v['hybrid_session'] for v in full]),
        'GLM four sessions, below API': span([v['api_session'] / v['hybrid_session'] for v in four]),
        'GLM four sessions, hybrid': '\\$' + span([v['hybrid_session'] for v in four]) + ', в '
                                     + f'{max(v["own_cluster_session"] / v["hybrid_session"] for v in four):.1f}'
                                     + ' раза дешевле своего кластера',
        'GLM four sessions, below own cluster': f'в {max(v["own_cluster_session"] / v["hybrid_session"] for v in four):.1f}'
                                                f' раза дешевле своего кластера и',
        'GLM shared Studio': 'двое и каждый проводит по две сессии в день, \\$' + span([v['hybrid_session'] for v in shared]),
        'GLM two sessions, dearer percent': f'гибрид дороже своего кластера на '
                                            f'{span([100 * (v["hybrid_session"] / v["own_cluster_session"] - 1) for v in two], 0)}\\%',
        'GLM one session, dearer factor': f'при одной в {span([v["hybrid_session"] / v["own_cluster_session"] for v in one])} раза',
        'refill, both slopes': ' или '.join(f'от {a:g} до {b:g} тысячи ({rf[(a, b)]:.1f} часа)' for a, b in rf),
        'refill, range': f'заново {compact_span(list(rf.values()), 0)} часов',
        'restore, size': f'около {rs["gb"]:.0f}~ГБ',
        'restore, minutes': f'около {GENITIVE[round(rs["minutes"])]} минут',
        'restore, minutes (conclusion)': f'примерно за {minutes(round(rs["minutes"]))} и дольше',
        'restore, traffic': f'около {rs["cents"]:.0f} центов',
        'hosting prices': f'\\${rs["ram_price"]:.2f} в оперативной памяти и \\${rs["nvme_price"]:.2f} на NVMe',
        'hosting prices (appendix)': f'$p_{{\\text{{RAM}}}} = \\${rs["ram_price"]:.2f}$ и '
                                     f'$p_{{\\text{{NVMe}}}} = \\${rs["nvme_price"]:.2f}$',
        'restore, storage on NVMe': f'Хранение копии на NVMe по \\${rs["nvme_price"]:.2f} за гигабайт стоит около '
                                    f'\\${rs["nvme"]:.1f} в месяц',
        'restore, storage under the protocol policy': f'По политике протокола копия в рабочие часы лежит в оперативной '
                                                      f'памяти по \\${rs["ram_price"]:.2f} за гигабайт, и хранение стоит около '
                                                      f'\\${rs["tiered"]:.1f}',
    }


def directions(m):
    """Each comparison the text states, evaluated on the engine rows: name -> True when the rows support it."""
    d, c, dopt, copt = m['design'], m['cons'], m['dopt'], m['copt']

    light_saving = [[100 * (1 - x[('light', t, 'hybrid')] / x[('light', t, 'own')]) for t in TEAMS] for x in (d, c)]
    monotone = lambda s: all(a <= b for a, b in zip(s, s[1:])) or all(a >= b for a, b in zip(s, s[1:]))
    both = (d, c)
    util = m['glm_util']
    big = (500, 5000)
    up = m['upper']
    cheap_everywhere = all(x[k]['hybrid_cheapest'] > x[k]['api_cheapest']
                           for x in (m['s20'], m['s50'], m['s20c'], m['s50c']) for k in CLIENTS)
    return {
        'closed: medium, hybrid cheaper at every team size':
            all(x[('medium', t, 'hybrid')] < x[('medium', t, 'own')] for x in both for t in TEAMS),
        'closed: heavy, hybrid cheaper at every team size':
            all(x[('heavy', t, 'hybrid')] < x[('heavy', t, 'own')] for x in both for t in TEAMS),
        'closed: light, hybrid cheaper at 50 and 5000':
            all(x[('light', t, 'hybrid')] < x[('light', t, 'own')] for x in both for t in LIGHT_ENDS),
        # Legacy site names are retained for audit continuity; the new claims
        # explicitly replace the removed artificial team-cap conclusions.
        'closed: light at 500, hybrid cheaper with uncapped hardware':
            all(x[('light', 500, 'hybrid')] < x[('light', 500, 'own')] for x in both)
            and all(any(t == 500 and 'RTX PRO 6000' in server and o['eligible']
                        for (p, t, route, server, tier), o in opt.items()) for opt in (dopt, copt)),
        'closed: both routes have equal retention and latency budgets': symmetric_budgets(),
        'closed: the selected option is the cheapest eligible one':
            all(min((o['cost'] for (p2, t2, r2, _, _), o in opt.items() if (p2, t2, r2) == (p, t, r) and o['eligible']),
                    default=None) == o_sel['cost']
                for opt in (dopt, copt) for (p, t, r, _, _), o_sel in opt.items() if o_sel['selected']),
        'closed: light-load saving grows over 50, 500 and 5000':
            all(all(a <= b for a,b in zip(s,s[1:])) for s in light_saving),
        'cheapest API cheaper than the hybrid on every client, both shares and policies': cheap_everywhere,
        'at 50% Ultra clients dearer than the cheapest API':
            all(m['s50'][k]['hybrid_cheapest'] > m['s50'][k]['api_cheapest'] for k in ULTRA),
        'teams: fixed B300 above both APIs at 500 and50, above cheapest at every size':
            all(m[t][CLIENT]['own_cluster'] > m[t][CLIENT]['api_median'] for t in ('t20', 't50'))
            and all(m[k][50]['own_cluster'] > m[k][50]['api_median'] for k in ('t20all', 't50all'))
            and all(r['own_cluster'] > r['api_cheapest'] for k in ('t20all', 't50all') for r in m[k].values()),
        'upper bound: capacity falls, API rises, the gap to the cheapest API narrows':
            up[(True, 50)]['capacity_day'] < up[(False, 50)]['capacity_day']
            and all(up[(True, s)][k] > up[(False, s)][k] for s in (20, 50) for k in ('api_median', 'api_cheapest'))
            and all(up[(True, s)]['hybrid_cheapest'] / up[(True, s)]['api_cheapest']
                    < up[(False, s)]['hybrid_cheapest'] / up[(False, s)]['api_cheapest'] for s in (20, 50)),
        'storage cheaper than prefill (M5 Max, 20%)': m['s20'][CLIENT]['hosting_month'] < m['s20'][CLIENT]['compute_month'],
        '1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)':
            all(util[(p, t, 1, f'{s}/day')]['own_cluster_session'] < util[(p, t, 1, f'{s}/day')]['hybrid_session']
                for p in ('design', 'conservative') for t in big for s in (1, 2)),
        '1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)':
            all(util[(p, t, 1, k)]['hybrid_session'] < util[(p, t, 1, k)]['own_cluster_session']
                for p in ('design', 'conservative') for t in big for k in ('4/day', 'full')),
        '1M: four sessions a day below the API':
            all(1 < util[('design', t, 1, '4/day')]['api_session'] / util[('design', t, 1, '4/day')]['hybrid_session']
                for t in big),
        '1M: API cheapest for 10 people and fewer; at 50 own below API below hybrid':
            all(m['glm_long'][t]['api_session'] < min(m['glm_long'][t]['own_cluster_session'],
                                                      m['glm_long'][t]['hybrid_session']) for t in (5, 10))
            and m['glm_long'][50]['own_cluster_session'] < m['glm_long'][50]['api_session']
            < m['glm_long'][50]['hybrid_session'],
        '1M: refill of a million tokens on M3 Max takes less than a day': max(m['refill'].values()) < 24,
        '1M: the server copy can lag behind the client under the protocol policy':
            m['s20'][CLIENT]['pending_calls_per_offload'] > 0,
        # The engine has no client SSD figure; its server NVMe tier bandwidth (hosting.json) stands in for it.
        '1M: a local NVMe snapshot restores faster than the 1 Gbit/s link':
            m['restore']['nvme_read'] * 8 > LINK_BIT_S,
        '1M: conservative policy at most 20% dearer':
            all(util[('conservative',) + k[1:]]['hybrid_session'] <= 1.2 * v['hybrid_session']
                for k, v in util.items() if k[0] == 'design' and k[1] in big),
    }


# Each value must appear at every site that publishes it. A site is (file, marker) for the paragraph that contains the
# marker, or (file, marker, 'sentence') for the sentence that starts at it.
C07 = ('91-calculation-history.tex', 'Вывод.} Против медианного')
C08 = ('91-calculation-history.tex', 'Вывод архивного сценария.}')
P_CLOSED = ('91-calculation-history.tex', 'Одни клиентские машины почти')
P_TEAMS = ('91-calculation-history.tex', 'Команды от 5 до 5000 человек')
P_OPEN = ('91-calculation-history.tex', 'Все числа этого раздела')
P_S20 = ('91-calculation-history.tex', 'При доле 20\\% пользователь')
P_S50 = ('91-calculation-history.tex', 'При доле 50\\% на открытую')
P_BUY = ('91-calculation-history.tex', 'Покупка клиента')
P_HOST = ('91-calculation-history.tex', 'Мак уже есть')
CAP_PAY = ('91-calculation-history.tex', 'Окупаемость клиента против медианного')
CAP_PER = ('91-calculation-history.tex', 'Закрытый контур: всё внутри периметра')
M_OPEN = ('91-calculation-history.tex', 'Чем глубже контекст')
M_LOSS = ('91-calculation-history.tex', 'Потеря кэша.')
M_COST = ('91-calculation-history.tex', 'Стоимость сессии.')
M_COST2 = ('91-calculation-history.tex', '500 человек гибрид обходится в', 'sentence')
M_LOAD = ('91-calculation-history.tex', 'Studio при двух сессиях')
K14 = ('91-calculation-history.tex', 'При доле открытой модели 20')
K14C = ('91-calculation-history.tex', 'В закрытом')
K14R = ('91-calculation-history.tex', 'Клиенту, который потерял', 'sentence')
SITES = {
    'medium, design': [P_CLOSED],
    'medium, conservative': [P_CLOSED],
    'medium, both cases': [C07, K14C],
    'light at 50 and 5000, design, percent': [P_CLOSED],
    'light at 50 and 5000, conservative, percent': [P_CLOSED],
    'light at 500, own against hybrid': [('91-calculation-history.tex', 'На 500 человек при лёгкой нагрузке', 'sentence')],
    'light at 500, cautious symmetric comparison': [('91-calculation-history.tex', 'При осторожной политике на 500 человек', 'sentence')],
    'heavy saving, design': [P_CLOSED, C07],
    'heavy saving, conservative': [P_CLOSED, C07],
    'symmetric hardware without team cap': [P_CLOSED, CAP_PER, C07, K14C],
    'symmetric retention budget': [P_CLOSED],
    'symmetric latency budget': [CAP_PER],
    # The own-server sentences are checked one by one: the paragraph mentions $3,370 twice.
    'own server for five people': [('91-calculation-history.tex', 'Команде из пяти человек нужн', 'sentence')],
    'own server for five people, light load': [('91-calculation-history.tex', 'пяти человек свой сервер обходится', 'sentence')],
    'cards for five people': [('91-calculation-history.tex', 'Команде из пяти человек нужн', 'sentence')],
    'B300 node per person, five people': [('91-calculation-history.tex', 'B300 покупается целиком', 'sentence'),
                                          ('91-calculation-history.tex', 'Команде из пяти человек нужн', 'sentence')],
    'own server for twenty people': [('91-calculation-history.tex', 'Команде из двадцати человек нужн', 'sentence')],
    'cards for twenty people': [('91-calculation-history.tex', 'Команде из двадцати человек нужн', 'sentence')],
    'B300 node per person, twenty people': [('91-calculation-history.tex', 'Команде из двадцати человек нужн', 'sentence')],
    'API per 1000 calls': [P_OPEN],
    'upper bound, capacity': [P_OPEN],
    'upper bound, API rise': [P_OPEN],
    'upper bound, s50 against median': [P_OPEN],
    'upper bound, s50 against cheapest': [P_OPEN],
    'upper bound, s20 against cheapest': [P_OPEN],
    'storage against prefill': [P_HOST],
    'conservative storage': [P_HOST],
    's20 hybrid dollars': [P_S20],
    's20 API dollars': [P_S20],
    's20 API median dollars': [P_S20],
    's20 below median, all clients, both cases': [('91-calculation-history.tex', '% checker-site: v5a-old-abstract-economics'), K14],
    's20 above cheapest, all clients, both cases': [('91-calculation-history.tex', '% checker-site: v5a-old-abstract-economics'), K14],
    's20 below median, Max clients, both cases': [C07],
    's20 below median, all clients, design': [P_S20],
    's20 above cheapest, all clients, design': [P_S20],
    's20 below median, all clients, conservative': [P_S20],
    's20 above cheapest, all clients, conservative': [P_S20],
    's50 M5 Max capacity': [P_S50],
    's50 Max dollars': [P_S50],
    's50 API dollars': [P_S50],
    's50 API median dollars': [P_S50],
    's50 below median, Max clients': [P_S50, C07],
    's50 above cheapest, Max clients, percent': [P_S50],
    's50 below median, Max clients, overflow at median': [P_S50],
    's50 share served by Max clients': [C07],
    's50 Ultra dollars': [P_S50],
    's50 Ultra conservative dollars': [P_S50],
    's50 above cheapest, Ultra clients, percent': [P_S50],
    's50 below median, Ultra clients, both cases': [C07],
    'purchase at 50%': [P_BUY],
    'purchase at 20%': [P_BUY],
    'purchase against cheapest': [P_BUY],
    'teams at 500, 20%': [P_TEAMS],
    'teams at 500, 50%': [P_TEAMS],
    'payback s50, overflow to cheapest': [P_BUY],
    'payback s20, overflow to cheapest': [P_BUY],
    'payback s50, overflow to median': [P_BUY, CAP_PAY],
    'payback s50, overflow to median, whole': [P_BUY, CAP_PAY],
    'payback, dearer than cheapest': [CAP_PAY],
    'GLM API session to 1M': [M_OPEN, M_COST2, ('91-calculation-history.tex', 'На 50 человек свой кластер', 'sentence')],
    'GLM API session to 200k': [M_OPEN],
    'GLM growth of the session cost': [M_OPEN],
    'GLM two sessions, hybrid': [M_COST2],
    'GLM two sessions, own cluster': [('91-calculation-history.tex', 'На 500 человек свой кластер', 'sentence')],
    'GLM two sessions, own cluster at 5000': [('91-calculation-history.tex', 'На 500 человек свой кластер', 'sentence')],
    'GLM 50 people': [M_COST],
    'GLM Studio utilization at two sessions': [M_LOAD],
    'GLM Studio capacity': [M_LOAD],
    'GLM full load, Studio share': [M_LOAD],
    'GLM full load, hybrid session': [M_LOAD],
    'GLM full load, below API': [M_LOAD, C08, ('91-calculation-history.tex', 'На глубоком контексте:')],
    'GLM full load, below own cluster': [M_LOAD, C08, ('91-calculation-history.tex', 'На глубоком контексте:')],
    'GLM four sessions, hybrid': [M_LOAD],
    'GLM four sessions, below own cluster': [C08],
    'GLM four sessions, below API': [M_LOAD, C08],
    'GLM shared Studio': [M_LOAD],
    'GLM two sessions, dearer percent': [C08],
    'GLM one session, dearer factor': [C08],
    'refill, both slopes': [M_LOSS],
    'refill, range': [M_LOSS],
    'restore, size': [M_LOSS],
    'restore, minutes': [M_LOSS],
    'restore, minutes (conclusion)': [K14R],
    'restore, traffic': [M_LOSS],
    'restore, storage on NVMe': [M_LOSS],
    'hosting prices': [P_HOST],
    'hosting prices (appendix)': [('90-appendix.tex', 'В расчётах $n = 4$', 'sentence')],
    'restore, storage under the protocol policy': [M_LOSS],
}

# The wording that states each direction, per site. Flipping it (cheaper/dearer, falls/rises, ...) must be reported.
DIRECTION_SITES = {
    'closed: medium, hybrid cheaper at every team size': [
        (P_CLOSED, 'раза дешевле своего серверного кластера на 50, 500 и 5000 человек'),
        (C07, 'раза дешевле своего кластера, при тяжёлой на'),
        (K14C, 'раза дешевле своего серверного кластера. При лёгкой')],
    'closed: heavy, hybrid cheaper at every team size': [(P_CLOSED, 'на сервере, и гибрид дешевле кластера на')],
    'closed: light, hybrid cheaper at 50 and 5000': [
        (P_CLOSED, 'Для лёгкой нагрузки на 50 и 5000 человек гибрид дешевле кластера на'),
        (C07, 'при лёгкой на 50 и 5000 человек гибрид дешевле своего кластера'), (K14C, 'для 50 человек гибрид дешевле')],
    'closed: light at 500, hybrid cheaper with uncapped hardware': [
        (P_CLOSED, 'На 500 человек при лёгкой нагрузке гибрид дешевле своего кластера'),
        (C07, 'на 500 человек гибрид тоже дешевле: серверы на RTX PRO 6000 допустимы без ограничения размера команды'),
        (C07, 'обе схемы имеют одинаковые требования хранения и задержки'),
        (K14C, 'для 500 дешевле'),
        (K14C, 'обе схемы имеют одинаковые требования хранения и задержки')],
    'closed: the selected option is the cheapest eligible one': [
        (P_CLOSED, 'движок выбирает самый дешёвый из допустимых'), (CAP_PER, 'из допустимых вариантов взят самый дешёвый')],
    'closed: light-load saving grows over 50, 500 and 5000': [
        (P_CLOSED, 'Экономия на лёгкой нагрузке растёт с размером команды')],
    'closed: both routes have equal retention and latency budgets': [
        (P_CLOSED, 'Обе схемы имеют одинаковые сроки хранения и число сохраняемых сессий')],
    'cheapest API cheaper than the hybrid on every client, both shares and policies': [
        (C07, 'Самый дешёвый поставщик API дешевле гибрида на всех рассмотренных клиентах и при обеих долях'),
        (('91-calculation-history.tex', 'Как это будет меняться'), 'самый дешёвый поставщик обходится дешевле гибрида на всех '
                                                          'рассмотренных клиентах'),
        (P_S20, 'раза дороже, чем у самого дешёвого поставщика API'), (P_S20, 'раза дороже самого дешёвого поставщика'),
        (P_S50, '\\% дороже самого дешёвого API ('), (K14, 'раза дороже самого дешёвого'),
        (('91-calculation-history.tex', '% checker-site: v5a-old-abstract-economics'), 'раза дороже самого дешёвого'),
        (CAP_PAY, 'Против самого дешёвого поставщика гибрид дороже')],
    'at 50% Ultra clients dearer than the cheapest API': [
        (P_S50, 'дороже самого дешёвого API при хранении по политике протокола')],
    'teams: fixed B300 above both APIs at 500 and50, above cheapest at every size': [
        (P_TEAMS, 'на 500 человек фиксированный кластер B300 дороже медианного поставщика API при обеих долях'),
        (P_TEAMS, 'на 50 человек кластер B300 тоже дороже'),
        (P_TEAMS, 'Самого дешёвого поставщика API свой кластер не догоняет ни при каком размере команды до 5000')],
    'upper bound: capacity falls, API rises, the gap to the cheapest API narrows': [
        (P_OPEN, 'ёмкость M5 Max падает'), (P_OPEN, 'API дорожает на'), (P_OPEN, 'разрыв с самым дешёвым сокращается')],
    'storage cheaper than prefill (M5 Max, 20%)': [(P_HOST, 'в месяц, меньше, чем сам prefill')],
    '1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)': [
        (('91-calculation-history.tex', 'На 500 человек свой кластер', 'sentence'), 'свой кластер стоит'),
        (('91-calculation-history.tex', 'На 500 человек свой кластер', 'sentence'), 'и дешевле гибрида'),
        (C08, 'При двух сессиях в день гибрид дороже своего кластера на')],
    '1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)': [
        (M_LOAD, 'раза дешевле своего кластера и в'),
        (M_LOAD, 'раза дешевле API и в'), (M_LOAD, 'раза дешевле своего кластера.'),
        (C08, 'раза дешевле своего кластера и в'),
        (('91-calculation-history.tex', 'На глубоком контексте:'), 'раза дешевле своего кластера.')],
    '1M: four sessions a day below the API': [(site, 'раза дешевле API') for site in (M_LOAD, C08)],
    '1M: API cheapest for 10 people and fewer; at 50 own below API below hybrid': [
        (M_COST, 'Команде из 10 человек и меньше выделенный сервер не окупается, и дешевле всего остаётся API'),
        (M_COST, 'немного дешевле API'), (M_COST, 'дороже обоих')],
    '1M: conservative policy at most 20% dearer': [(M_LOAD, 'При осторожной политике хранения сессии дороже не больше чем на 20')],
    '1M: refill of a million tokens on M3 Max takes less than a day': [(K14R, 'заново около 20 часов')],
    '1M: the server copy can lag behind the client under the protocol policy': [
        (M_LOSS, 'Пять минут здесь нижняя граница: по политике протокола сервер дописывает в копию токены вызовов, '
                 'прочитанных клиентом, только при следующем оффлоаде')],
    '1M: a local NVMe snapshot restores faster than the 1 Gbit/s link': [
        (M_LOSS, 'Если диск клиента уцелел, сессию быстрее поднять из локального снимка')],
}


def paragraph(text, marker):
    """The paragraph of text that contains marker, or '' when the marker is absent."""
    for part in text.split('\n\n'):
        if marker in part:
            return part
    return ''


def sentence(text, marker):
    """The sentence of text that starts at marker (up to a full stop followed by white space), or ''."""
    i = text.find(marker)
    if i < 0:
        return ''
    m = re.search(r'\.(\s|$)', text[i:])
    return text[i:i + m.start() + 1] if m else text[i:]


def scope(texts, site):
    name, marker = site[0], site[1]
    return sentence(texts[name], marker) if len(site) > 2 else paragraph(texts[name], marker)


def norm(t):
    return ' '.join(t.split())


def value_at(key, site, expected):
    """Bind a scalar repeated within a paragraph to its own comparison."""
    value = expected[key]
    if key == 'heavy saving, design':
        return ('при тяжёлой на ' if site == C07 else 'гибрид дешевле кластера на ') + value + '\\%'
    if key == 'heavy saving, conservative':
        return ('при осторожной политике на ' if site == C07 else 'при осторожной политике хранения на ') + value + '\\%'
    if key == 'medium, both cases' and site == C07:
        return 'при средней нагрузке гибрид в ' + value + ' раза'
    if key == 's50 below median, Max clients' and site == C07:
        return 'при доле 50\\% в ' + value + ' раза'
    if key == 'payback s50, overflow to median, whole':
        return ('Мак ' + value + '. Против' if site == P_BUY else 'машина ' + value + '.')
    if key == 'GLM full load, below own cluster':
        return ('при полной загрузке в ' + value + ' и' if site == C08
                else 'в ' + value + ' раза дешевле своего кластера.')
    return value


def direction_wording(key, wording, expected):
    if key == '1M: four sessions a day below the API':
        return expected['GLM four sessions, below API'] + ' ' + wording
    return wording


def check(texts, m=None):
    """Return (item, file) pairs for values, table rows and direction wording that the text does not carry, and the
    names of directions the engine rows no longer support, as (name, 'engine')."""
    m = m or model()
    expected = values(m)
    missing = []
    for k, sites in SITES.items():
        for site in sites:
            if norm(value_at(k, site, expected)) not in norm(scope(texts, site)):
                missing.append((k, site[0]))
    for kind, rws in (('client table row', econ_rows(m['s20'], m['s50'], m['b50'])),
                      ('closed-perimeter table row', perimeter_rows(m['design'], m['cons']))):
        for row in rws:
            if norm(row) not in norm(texts['91-calculation-history.tex']):
                missing.append((f'{kind}: {row}', '91-calculation-history.tex'))
    holds = directions(m)
    for k, sites in DIRECTION_SITES.items():
        if not holds[k]:
            missing.append((k, 'engine'))
        for site, wording in sites:
            if norm(direction_wording(k, wording, expected)) not in norm(scope(texts, site)):
                missing.append((f'direction wording: {k}', site[0]))
    return missing + guard(texts, m, expected)


def read():
    """Every section; SITES and DIRECTION_SITES name some of them, the guard scans all."""
    return {n: open(os.path.join(SECTIONS, n), encoding='utf-8').read() for n in sorted(os.listdir(SECTIONS))
            if n.endswith('.tex')}


# Word forms of checked figures that the number patterns below do not catch.
CORE_FORMS = {
    'restore, minutes': ('пяти минут', 'пять минут'),
    'restore, minutes (conclusion)': ('пяти минут', 'пять минут'),
    'restore, size': ('35~ГБ', '35 ГБ'),
    'restore, traffic': ('18 центов',),
    'GLM growth of the session cost': ('в 21 раз',),
    'GLM Studio capacity': ('семь сессий',),
    'GLM four sessions, below own cluster': (),
    'GLM four sessions, hybrid': (),
    'upper bound, s20 against cheapest': (),
}
# Occurrences of a checked figure's printed form that publish a different quantity, each with its reason. An entry is
# (file, form, a substring of the source line that holds it, reason); an entry that matches nothing is reported.
ALLOW = (
    ('90-appendix.tex', '19.9', 'На всём профиле чтение', 'Original M3 methodology retains mean wait, source-bound to the same run16 normalized calls'),
    ('91-calculation-history.tex', '1.2--1.5', '1.2--1.5', 'v4b introduction economics bound by offload registry'),
    ('91-calculation-history.tex', '4.8--6.0', '4.8--6.0', 'v4b introduction economics bound by offload registry'),
    ('02-workload.tex', '19.9', 'в среднем 19.9 секунды', 'v4b restored distribution, recomputed against all R16 normalized calls'),
    ('02-workload.tex', '131.4', 'Глубина контекста, тыс. токенов', 'PRI31 measured segment midpoint'),
    ('02-workload.tex', '181.4', 'Глубина контекста, тыс. токенов', 'PRI31 measured segment midpoint'),
    ('02-workload.tex', '230.9', 'Глубина контекста, тыс. токенов', 'PRI31 measured segment midpoint'),
    ('90-appendix.tex', '15.8', 'при 100~Мбит/с на сервер уходит', 'R16 f32 offload call share, source-bound table'),
    ('91-calculation-history.tex', 'в 1.2 раза', 'хранения гибрид в 5.8--6.0 раза', 'M5 price-bound comparison; source-bound by the breakeven guard'),
    ('90-appendix.tex', '\\$101', '\\$101 против', 'R15 egress at 90 USD/TB; separately snapshot-bound by offload traffic guard'),
    ('91-calculation-history.tex', '19.9', 'бюджет среднего prefill равен 19.9', 'shared snapshot mean-latency budget; unrelated to28.2-hour refill'),
    ('90-appendix.tex', '15.8', 'Состояние в 32 битах: доля вызовов', 'R14 offload share at100Mbit/s; unrelated to25.9-hour refill'),
    ('91-calculation-history.tex', '45.2', '& 45.2 &', 'tab:clients: generation rate of the M5 Ultra in tokens per second'),
    ('91-calculation-history.tex', '\\$48', '50 человек, 10 ч в день &', 'tab:rentbuy: buying at 50% residual for 50 people, 10 h a day'),
    ('91-calculation-history.tex', '\\$59', '10 человек, 24 ч &', 'tab:rentbuy: buying at 80% residual for 10 people, 24 h'),
    ('91-calculation-history.tex', '\\$35', '50 человек, 10 ч в день &', 'tab:rentbuy: buying at 80% residual for 50 people, 10 h a day'),
    ('91-calculation-history.tex', '\\$38', '50 человек, 24 ч &', 'tab:rentbuy: buying at 50% residual for 50 people, 24 h'),
    ('91-calculation-history.tex', '\\$29', '50 человек, 24 ч &', 'tab:rentbuy: buying at 80% residual for 50 people, 24 h'),
    ('91-calculation-history.tex', '\\$35', 'остаточной стоимости 80\\% (\\$35)', 'rent/buy prose, 50 people, 80% residual'),
    ('91-calculation-history.tex', '4.8--5.1', 'Не выше на стандартном усилии рассуждения &', 'historical owner API bill in thousands of USD'),
    ('90-appendix.tex', '15--30', 'генерация была на 15--30', 'earlier-run measured decode slowdown, not GLM cost'),
)


def guard_forms(k, v):
    """Distinctive printed forms of a value: ranges, dollar amounts, decimals with three or more digits, word forms."""
    forms = set(CORE_FORMS.get(k, ()))
    if k in ('GLM four sessions, hybrid', 'GLM four sessions, below own cluster', 'upper bound, s20 against cheapest'):
        match = re.search(r'в [0-9.]+ раза', v)
        if match:
            forms.add(match.group())
    if k == 'GLM full load, below own cluster':
        forms.add('в ' + v + ' раза')
    for m in re.finditer(r'\\\$\d[\d\\,.]*\d(?:--\d[\d.]*\d)?|\\\$\d|\d+(?:\.\d+)?--\d+(?:\.\d+)?|\d+\.\d{2,}|\d{2,}\.\d', v):
        forms.add(m.group(0))
    forms.update(re.findall(r'\d+(?:\.\d+)?--\d+(?:\.\d+)?', v))
    return forms


def occurrences(text, form):
    """Start offsets of form in text, with the boundaries of a whole printed figure."""
    pattern = r'\s+'.join(map(re.escape, form.split()))
    if form[0].isdigit():
        pattern = r'(?<![\d.\-])' + pattern
    if form[-1].isdigit():
        pattern += r'(?![\d]|\.\d|--|\\,\d)'
    if form[0].isalpha():
        pattern = r'(?<![а-яёА-ЯЁa-zA-Z])' + pattern
    return [m.start() for m in re.finditer(pattern, text)]


def guard(texts, m, expected):
    """Occurrences of checked figures outside their registered sites, the tables and ALLOW."""
    spans = {}
    def span_of(site):
        text, part = texts[site[0]], scope(texts, site)
        i = text.find(part) if part else -1
        return (i, i + len(part)) if i >= 0 else None
    for k, sites in SITES.items():
        for form in guard_forms(k, expected[k]):
            for site in sites:
                s = span_of(site)
                if s:
                    spans.setdefault((site[0], form), []).append(s)
    table_rows = econ_rows(m['s20'], m['s50'], m['b50']) + perimeter_rows(m['design'], m['cons'])
    used, found = set(), []
    forms = sorted({f for k in SITES for f in guard_forms(k, expected[k])} | {a[1] for a in ALLOW})
    for name, text in texts.items():
        for form in forms:
            for pos in occurrences(text, form):
                if any(a <= pos < b for a, b in spans.get((name, form), ())):
                    continue
                line = text[text.rfind('\n', 0, pos) + 1:text.find('\n', pos) if text.find('\n', pos) >= 0 else len(text)]
                if any(norm(row) in norm(line) and form in row for row in table_rows):
                    continue
                allowed = [a for a in ALLOW if a[0] == name and a[1] == form and a[2] in line]
                if allowed:
                    used.update(allowed)
                    continue
                found.append((f'unregistered occurrence of {form}', name))
    for a in ALLOW:
        if a not in used:
            found.append((f'unused ALLOW entry {a[1]} ({a[3]})', a[0]))
    return found


FLIPS = (('немонотонна', 'монотонна'), ('нижняя', 'верхняя'), ('быстрее', 'медленнее'), ('больше суток', 'меньше суток'),
         ('дешевле', 'дороже'), ('дороже', 'дешевле'), ('падает', 'растёт'), ('дорожает', 'дешевеет'),
         ('сокращается', 'растёт'), ('больше', 'меньше'), ('не догоняет', 'догоняет'), ('не окупается', 'окупается'),
         ('не больше', 'больше'), ('оба варианта', 'только гибрид'), ('самый дешёвый', 'самый дорогой'),
         ('почти', 'больше чем'), ('Вне этого правила', 'По этому правилу'), ('меньше чем', 'больше чем'),
         ('свой кластер стоит', 'гибрид стоит'))


def perturb(s):
    """A stale variant of a value: the last digit changed; for text without digits, its first flip."""
    digits = [i for i, ch in enumerate(s) if ch.isdigit()]
    if digits:
        i = digits[-1]
        return s[:i] + str((int(s[i]) + 1) % 10) + s[i + 1:]
    return flip(s)


def flip(s):
    for old, new in FLIPS:
        if old in s:
            return s.replace(old, new, 1)
    return 'ПОДМЕНА'  # contains nothing of s, so the planted site loses the expected text


def plant(texts, site, old, new):
    """texts with the first occurrence of old (white space as in the source) inside the site's scope replaced."""
    text, part = texts[site[0]], scope(texts, site)
    match = re.compile(r'\s+'.join(map(re.escape, old.split()))).search(part)
    assert match, ('control target missing', site, old)
    return dict(texts, **{site[0]: text.replace(part, part[:match.start()] + new + part[match.end():], 1)})


def self_test(texts):
    from unittest.mock import patch
    m = model()
    expected = values(m)
    controls, failed = 0, []
    # Duplicate scoped rows (even equal prices) and non-single-node fleets must
    # reject by the intended assertion; the untouched rows remain valid.
    original_rows = rows
    clean = rows('perimeter_cost.csv')
    for team in (5, 20):
        row = next(r for r in clean if r['route'] == 'all server' and r['server'] == B300 and
                   r['profile'] == 'light' and r['team'] == str(team))
        for data, reason in ((clean + [dict(row)], 'exactly one row'),
                             ([dict(r, units='2') if r is row else r for r in clean], 'one node')):
            message = f'B300 light profile: {reason} for team {team}'
            with patch.dict(globals(), rows=lambda name: data if name == 'perimeter_cost.csv' else original_rows(name)):
                try:
                    own_servers()
                except AssertionError as error:
                    assert str(error) == message, (message, str(error))
                else:
                    raise AssertionError('plant survived: ' + message)
            assert own_servers()[1][team] == float(row['person_month'])
            print(f'negative engine control: {message}: rejected; clean control: pass')
    # One negative control per value site: a stale value planted at that site alone must be reported there.
    for k, sites in SITES.items():
        for site in sites:
            value = value_at(k, site, expected)
            got = check(plant(texts, site, value, perturb(value)), m)
            if (k, site[0]) not in got:
                failed.append(('stale value not reported', k, site))
            print(f'negative value control: {k} at {site}: rejected by {k}')
            controls += 1
    # One negative control per direction site: the flipped wording must be reported there.
    for k, sites in DIRECTION_SITES.items():
        for site, wording in sites:
            wording = direction_wording(k, wording, expected)
            got = check(plant(texts, site, wording, flip(wording)), m)
            if (f'direction wording: {k}', site[0]) not in got:
                failed.append(('flipped wording not reported', k, site))
            print(f'negative direction control: {k} at {site}: rejected by direction wording: {k}')
            controls += 1
    assert not failed, failed
    for key, site, old, new in (
        ('storage cheaper than prefill (M5 Max, 20%)', P_HOST,
         'в месяц, меньше, чем сам prefill', 'в месяц, больше, чем сам prefill'),
        ('1M: four sessions a day below the API', C08,
         expected['GLM four sessions, below API'] + ' раза дешевле API', 'почти в четыре раза дешевле API'),
    ):
        bad = plant(texts, site, old, new)
        assert bad != texts
        # The obsolete phrase must lose its named numeric/direction check.
        name = ('direction wording: ' + key if site == P_HOST else 'GLM four sessions, below API')
        assert (name, site[0]) in check(bad, m), (key, 'old direction survived')
        print(f'old-claim regression: {key}: rejected by {name}')
    storage = m['s20'][CLIENT]
    bad_storage = dict(m['s20'], **{CLIENT: dict(storage, hosting_month=storage['compute_month'] + 1)})
    assert ('storage cheaper than prefill (M5 Max, 20%)', 'engine') in check(texts, dict(m, s20=bad_storage))
    # Named regression controls for review r5b: N3 (restore minutes in the conclusion) and D5 (refill longer than a day).
    n3 = check(plant(texts, K14R, 'примерно за пять минут и дольше', 'примерно за две минуты и дольше'), m)
    assert ('restore, minutes (conclusion)', '91-calculation-history.tex') in n3, 'r5b N3 not reported'
    d5 = check(plant(texts, K14R, 'заново около 20 часов', 'заново больше суток'), m)
    assert ('direction wording: 1M: refill of a million tokens on M3 Max takes less than a day',
            '91-calculation-history.tex') in d5, 'r5b D5 not reported'
    # r5c: the storage figure follows paper_tables.hours, the engine's input for it (10 h instead of 8 changes it).
    assert ('restore, storage under the protocol policy', '91-calculation-history.tex') in check(
        texts, dict(m, restore=restore(hours=engine_input('paper-tables.json', 'paper_tables', 'hours') + 2))), \
        'changed paper_tables.hours not reported'
    # Guard: a checked figure printed in a section that no list names must be reported, and so must an ALLOW entry
    # whose occurrence is gone.
    outlook = texts['13-outlook.tex'] + '\nСервер возвращает сессию за пять минут.\n'
    assert ('unregistered occurrence of пять минут', '13-outlook.tex') in check(dict(texts, **{'13-outlook.tex': outlook}), m)
    form = next(f for f in guard_forms('GLM two sessions, hybrid', expected['GLM two sessions, hybrid']) if f.startswith('\\$'))
    related = texts['12-related.tex'] + '\nСессия гибрида стоит ' + form + '.\n'
    assert ('unregistered occurrence of ' + form, '12-related.tex') in check(dict(texts, **{'12-related.tex': related}), m)
    economics = texts['91-calculation-history.tex'].replace('\\$38 (2)', '\\$39 (2)', 1)
    assert any(k.startswith('unused ALLOW entry \\$38') for k, _ in check(dict(texts, **{'91-calculation-history.tex': economics}), m))
    # Every original collision site remains mandatory even when its new value
    # no longer coincides with a checked formula. No ALLOW entry can go unused.
    for file, form, marker, reason in ALLOW:
        lines = texts[file].splitlines(keepends=True)
        changed = ''.join(line.replace(form, perturb(form)) if marker in line and form in line else line
                          for line in lines)
        bad = dict(texts, **{file: changed})
        assert bad != texts
        assert any(k.startswith('unused ALLOW entry ' + form) for k, _ in check(bad, m)), reason
        print(f'negative collision control: {reason}: rejected by unused ALLOW entry {form}')
    # Table rows: a stale cell in each table must be reported.
    row = econ_rows(m['s20'], m['s50'], m['b50'])[2]
    assert any(k.startswith('client table row') for k, _ in check(dict(texts, **{'91-calculation-history.tex': texts[
        '91-calculation-history.tex'].replace(row, perturb(row), 1)}), m)), 'stale client row'
    row = perimeter_rows(m['design'], m['cons'])[1]
    assert any(k.startswith('closed-perimeter table row') for k, _ in check(dict(texts, **{'91-calculation-history.tex': texts[
        '91-calculation-history.tex'].replace(row, perturb(row), 1)}), m)), 'stale perimeter row'
    # Engine directions: rows changed so that a stated direction no longer holds must be reported.
    def flipped(**changes):
        return check(texts, dict(m, **changes))
    d = m['design']
    assert ('closed: light, hybrid cheaper at 50 and 5000', 'engine') in flipped(
        design={**d, ('light', 50, 'hybrid'): d[('light', 50, 'own')] + 1})
    dopt = dict(m['dopt'])
    for key, option in list(dopt.items()):
        if key[1] == 500 and 'RTX PRO 6000' in key[3]:
            dopt[key] = dict(option, eligible=False)
    assert ('closed: light at 500, hybrid cheaper with uncapped hardware', 'engine') in flipped(dopt=dopt), \
        'artificial large-team RTX exclusion not reported'
    s50 = m['s50']
    ultra = dict(s50, **{ULTRA[1]: dict(s50[ULTRA[1]], hybrid_cheapest=s50[ULTRA[1]]['api_cheapest'] - 1)})
    assert ('cheapest API cheaper than the hybrid on every client, both shares and policies', 'engine') in flipped(s50=ultra)
    util = dict(m['glm_util'])
    two = ('design', 500, 1, '2/day')
    util[two] = dict(util[two], hybrid_session=util[two]['own_cluster_session'] - 0.5)
    assert ('1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)', 'engine') in flipped(
        glm_util=util)
    util = dict(m['glm_util'])
    full = ('conservative', 5000, 1, 'full')
    util[full] = dict(util[full], hybrid_session=util[full]['own_cluster_session'] + 0.5)
    assert ('1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)', 'engine') in flipped(
        glm_util=util)
    # Agreement helpers: one, few and many.
    assert need_cards(1) == 'нужна одна карта' and need_cards(1, True) == 'нужна одна такая карта'
    assert need_cards(2) == 'нужны две карты' and need_cards(4, True) == 'нужны четыре такие карты'
    assert need_cards(5) == 'нужно пять карт' and need_cards(14) == 'нужно четырнадцать карт'
    assert months(12) == 'месяцев' and months(24) == 'месяца' and months(21) == 'месяц' and months(35) == 'месяцев'
    # Positive control: the current text and the engine rows pass.
    assert not check(texts, m), check(texts, m)
    print('positive control: all values, directions, occurrences and table rows: pass')
    print(f'self-test ok: {controls} site controls, table and engine-direction controls passed')
    return 0


def main():
    texts = read()
    if '--self-test' in sys.argv:
        return self_test(texts)
    m = model()
    missing = check(texts, m)
    for k, v in values(m).items():
        bad = [name for key, name in missing if key == k]
        print(f'{k}: {v}' + (f'  MISSING in {", ".join(bad)}' if bad else ''))
    holds = directions(m)
    for k in DIRECTION_SITES:
        bad = [name for key, name in missing if key == f'direction wording: {k}']
        print(f'direction: {k}: ' + ('holds' if holds[k] else 'NO LONGER HOLDS')
              + (f'; wording MISSING in {", ".join(bad)}' if bad else ''))
    for key, name in missing:
        if key not in SITES and not key.startswith('direction wording: ') and name != 'engine':
            print(f'{key}  MISSING in {name}')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
