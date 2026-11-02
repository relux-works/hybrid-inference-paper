#!/usr/bin/env python3
"""Checks the published figures and the stated directions of the paper against the engine snapshot in engine/.

Scope: the sites listed in SITES and DIRECTION_SITES, the client table, and a guard over all of paper/sections/*.tex.

Values: each figure in SITES is recomputed from engine/*.csv (run 11), payback.csv and the engine inputs named below,
rounded the way the text prints it, and must appear at each site SITES lists for it (a paragraph or one sentence, white
space normalised). The rows of the client table (tab:econ) are checked cell by cell.

Directions: directions() evaluates each comparison in DIRECTION_SITES on the engine rows (which option is cheaper, what
grows or falls), and each is bound to the wording that states it at each listed site. A comparison the engine no longer
supports, or a listed site whose wording is missing or flipped, is reported. Storage of a session copy under the
protocol policy follows the engine's tiered formula (session_hosting.py) with the same inputs: hosting.json tier
prices, paper_tables.hours (paper-tables.json), owners.days (ownership.json) and economics.hours_month
(economics.json).

Guard: every distinctive printed form of a checked figure (ranges, dollar amounts, decimals with three or more digits,
and the word forms in CORE_FORMS) is searched in every section. An occurrence outside the sites registered for a figure
with that form, outside the client table and outside ALLOW (each entry with its reason) is reported, so a figure printed
in the checker's form in a new place is reported; other spellings and values already stale when written are not.

Run: python3 check_ranges.py            (exit 0 when the text matches)
     python3 check_ranges.py --self-test (a planted stale value or flipped wording at each site must be reported)
"""
import csv, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = os.path.join(HERE, '..', 'sections')
RULE_FILE = os.path.join(HERE, '..', '..', 'calc', 'hybridcalc', 'data', 'paper-tables-r6.json')
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


def rule():
    """(small_team_max, overlap_min) of the engine's closed-perimeter eligibility rule."""
    with open(RULE_FILE, encoding='utf-8') as f:
        p = json.load(f)['r6']['perimeter']
    return int(p['small_team_max']['value']), int(p['overlap_min']['value'])


def money(v):
    return '\\$' + f'{v:,.0f}'.replace(',', '\\,')


def span(values, digits=1):
    return f'{min(values):.{digits}f}--{max(values):.{digits}f}'


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
        key = (r['profile'], int(r['team']), route, r['server'])
        opt[key] = dict(cost=float(r['person_month']), eligible=r['eligible'] == '1', selected=r['selected'] == '1',
                        units=int(float(r['units'])) if r['units'] not in ('', 'nan') else 0)
        if r['selected'] == '1':
            kind = 'own' if route == 'all server' else 'hybrid'
            sel[(r['profile'], int(r['team']), kind)] = float(r['person_month'])
            sel[(r['profile'], int(r['team']), kind + '_server')] = r['server']
            sel[(r['profile'], int(r['team']), kind + '_units')] = opt[key]['units']
    return sel, opt


def rule_holds(opt, small, overlap):
    """The snapshot's eligible column follows the stated rule for every option."""
    for (profile, team, route, server), o in opt.items():
        want = team >= overlap if server == B300 else team <= small
        if o['eligible'] != want:
            return False
    return True


def perimeter_rows(design, cons):
    calls = {'light': '200', 'medium': '800', 'heavy': '2\\,500'}
    return [f'{calls[p]} & {t} & \\${design[(p, t, "own")]:.0f} & \\${design[(p, t, "hybrid")]:.0f} & '
            f'\\${cons[(p, t, "hybrid")]:.0f} & {design[(p, t, "served")]:.0f}\\% \\\\'
            for p in ('light', 'medium', 'heavy') for t in TEAMS]


TWO_CARD = '2x RTX PRO 6000 Server; own perimeter rack'


def outside_rule(dopt, copt):
    """Light load at 500 people on two-card RTX PRO 6000 servers (ineligible under the rule): the hybrid under both
    policies, the own cluster on the same servers, and the own cluster on its selected B300 node."""
    hyb, hyb_c = dopt[('light', 500, 'hybrid', TWO_CARD)]['cost'], copt[('light', 500, 'hybrid', TWO_CARD)]['cost']
    own_two = dopt[('light', 500, 'all server', TWO_CARD)]['cost']
    own_b300 = dopt[('light', 500, 'all server', B300)]
    assert own_b300['selected'], 'the own cluster at 500 people, light load, is no longer the B300 node'
    return hyb, hyb_c, own_two, own_b300['cost']


# ---------------------------------------------------------------- own servers for 5 and 20 people

def own_servers():
    selected, b300 = {}, {}
    for r in rows('perimeter_cost.csv'):
        if r['route'] != 'all server':
            continue
        if r['selected'] == '1':
            selected[(r['profile'], int(r['team']))] = r
        if r['server'] == B300:
            b300.setdefault(int(r['team']), set()).add(float(r['person_month']))
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
    phrase = {1: 'по одной в сервере', 2: 'по две в сервере'}[per]
    return f'{need_cards(light, such)} при лёгкой нагрузке и {WORDS.get(heavy, str(heavy))}, {phrase}, при тяжёлой'


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
    text = open(os.path.join(SECTIONS, '02-workload.tex'), encoding='utf-8').read()
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
        out[(int(start / 1e3), int(mids[-1] / 1e3))] = sum(tok(n + 500, slope) * 1000
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
    m = dict(design=d, cons=c, dopt=dopt, copt=copt, rule=rule(),
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
    small, overlap = m['rule']
    hyb2, hyb2_c, own2, own_b300 = outside_rule(m['dopt'], m['copt'])
    s20, s50, s20c, s50c, b20, b50 = (m[k] for k in ('s20', 's50', 's20c', 's50c', 'b20', 'b50'))
    cheaper = lambda x, keys: [x[k]['api_median'] / x[k]['hybrid_cheapest'] for k in keys]
    dearer = lambda x, keys: [x[k]['hybrid_cheapest'] / x[k]['api_cheapest'] for k in keys]
    served = [100 * s50[k]['served_day'] / s50[k]['requested_day'] for k in MAX]
    a20, a50 = s20[CLIENT], s50[CLIENT]
    up = m['upper']
    base50, top50, base20, top20 = up[(False, 50)], up[(True, 50)], up[(False, 20)], up[(True, 20)]
    selected, b300 = own_servers()
    for team in (5, 20):
        assert len(b300[team]) == 1, ('B300 person_month varies across profiles', team, b300[team])
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
        'light at 500, outside the rule': f'около \\${hyb2:.0f} (при осторожной политике \\${hyb2_c:.0f}) против '
                                          f'\\${own2:.0f} у своего кластера на тех же серверах и \\${own_b300:.0f} на узле B300',
        'heavy saving, design': span([saving(d, 'heavy', t) for t in TEAMS], 0),
        'heavy saving, conservative': span([saving(c, 'heavy', t) for t in TEAMS], 0),
        'rule, RTX PRO 6000 limit': f'для команд до {small} человек',
        'rule, B300 from (paragraph)': f'узлы B300 начиная с {overlap}',
        'rule, B300 from (caption)': f'узлы B300 для команд от {overlap}',
        # own servers for 5 and 20 people
        'own server for five people': '\\$' + span(own_team(5), 0),
        'own server for twenty people': '\\$' + span(own_team(20), 0),
        'own server for five people, light load': f'от \\${float(selected[("light", 5)]["person_month"]):.0f} на '
                                                  f'человека в месяц при лёгкой нагрузке',
        'cards for five people': cards_sentence(selected, 5, True),
        'cards for twenty people': cards_sentence(selected, 20, False),
        'B300 node per person, five people': money(next(iter(b300[5]))),
        'B300 node per person, twenty people': money(next(iter(b300[20]))),
        # per-person economics
        'API per 1000 calls': f'стоят \\${a20["api_median"] / 10.5:.2f}, у самого дешёвого \\${a20["api_cheapest"] / 10.5:.2f}',
        'upper bound, capacity': f'с {base50["capacity_day"]:.0f} до {top50["capacity_day"]:.0f} вызовов в день',
        'upper bound, API rise': span([100 * (top50[k] / base50[k] - 1) for k in ('api_median', 'api_cheapest')], 0),
        'upper bound, s50 against median': f'\\${top50["hybrid_cheapest"]:.0f} против \\${top50["api_median"]:.0f}',
        'upper bound, s50 against cheapest': f'\\${top50["hybrid_cheapest"]:.0f} против \\${top50["api_cheapest"]:.0f} при',
        'upper bound, s20 against cheapest': f'в {top20["hybrid_cheapest"] / top20["api_cheapest"]:.1f} раза при доле 20',
        'storage against prefill': f'хранение стоит \\${s20[CLIENT]["hosting_month"]:.1f} в месяц, больше, чем сам prefill '
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
        'GLM 50 people': f'(\\${g[50]["own_cluster_session"]:.2f}) немного дешевле API (\\${g[50]["api_session"]:.2f}), а '
                         f'гибрид с отдельной Studio на каждого дороже обоих (\\${g[50]["hybrid_session"]:.2f})',
        'GLM Studio utilization at two sessions': ('меньше чем на треть' if max(v['utilization'] for v in two) < 1 / 3
                                                   else f'на {100 * max(v["utilization"] for v in two):.0f}\\%'),
        'GLM Studio capacity': f'почти {WORDS[math.ceil(two[0]["capacity_studio_day"])]} сессий',
        'GLM full load, Studio share': f'до \\${full[0]["studio_session"]:.2f} на сессию',
        'GLM full load, hybrid session': '\\$' + span([v['hybrid_session'] for v in full]),
        'GLM full load, below API': span([v['api_session'] / v['hybrid_session'] for v in full]),
        'GLM full load, below own cluster': span([v['own_cluster_session'] / v['hybrid_session'] for v in full]),
        'GLM four sessions, hybrid': '\\$' + span([v['hybrid_session'] for v in four]) + ', в '
                                     + f'{max(v["own_cluster_session"] / v["hybrid_session"] for v in four):.1f}'
                                     + ' раза дешевле своего кластера',
        'GLM four sessions, below own cluster': f'в {max(v["own_cluster_session"] / v["hybrid_session"] for v in four):.1f}'
                                                f' раза дешевле своего кластера и',
        'GLM shared Studio': 'двое и каждый проводит по две сессии в день, \\$' + span([v['hybrid_session'] for v in shared]),
        'GLM two sessions, dearer percent': f'гибрид дороже своего кластера на '
                                            f'{span([100 * (v["hybrid_session"] / v["own_cluster_session"] - 1) for v in two], 0)}\\%',
        'GLM one session, dearer factor': f'при одной в {span([v["hybrid_session"] / v["own_cluster_session"] for v in one])} раза',
        'refill, both slopes': ' или '.join(f'от {a} до {b} тысячи ({rf[(a, b)]:.1f} часа)' for a, b in rf),
        'refill, range': f'заново {round(min(rf.values()))}--{round(max(rf.values()))} часов',
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
    small, overlap = m['rule']
    hyb2, hyb2_c, own2, own_b300 = outside_rule(dopt, copt)
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
        # The 500-person reversal holds under the rule and only because of it: the snapshot follows the rule, RTX PRO
        # servers are excluded at 500, both routes get one B300 node, the own cluster is cheaper; outside the rule the
        # hybrid on two-card RTX PRO servers is cheaper than the own cluster.
        'closed: light at 500, own cluster cheaper under the rule':
            small < 500 and overlap <= 500 and rule_holds(dopt, small, overlap) and rule_holds(copt, small, overlap)
            and all(x[('light', 500, 'own')] < x[('light', 500, 'hybrid')]
                    and x[('light', 500, 'own_server')] == B300 == x[('light', 500, 'hybrid_server')]
                    and x[('light', 500, 'own_units')] == 1 == x[('light', 500, 'hybrid_units')] for x in both),
        'closed: light at 500, hybrid cheaper outside the rule': max(hyb2, hyb2_c) < min(own_b300, own2),
        'closed: the selected option is the cheapest eligible one':
            all(min((o['cost'] for (p2, t2, r2, _), o in opt.items() if (p2, t2, r2) == (p, t, r) and o['eligible']),
                    default=None) == o_sel['cost']
                for opt in (dopt, copt) for (p, t, r, _), o_sel in opt.items() if o_sel['selected']),
        'closed: light-load saving is not monotone over 50, 500 and 5000':
            not any(monotone(s) for s in light_saving),
        'cheapest API cheaper than the hybrid on every client, both shares and policies': cheap_everywhere,
        'at 50% Ultra clients dearer than the cheapest API':
            all(m['s50'][k]['hybrid_cheapest'] > m['s50'][k]['api_cheapest'] for k in ULTRA),
        'teams: own cluster below the median API at 500, above it at 50, above the cheapest at every size':
            all(m[t][CLIENT]['own_cluster'] < m[t][CLIENT]['api_median'] for t in ('t20', 't50'))
            and all(m[k][50]['own_cluster'] > m[k][50]['api_median'] for k in ('t20all', 't50all'))
            and all(r['own_cluster'] > r['api_cheapest'] for k in ('t20all', 't50all') for r in m[k].values()),
        'upper bound: capacity falls, API rises, the gap to the cheapest API narrows':
            up[(True, 50)]['capacity_day'] < up[(False, 50)]['capacity_day']
            and all(up[(True, s)][k] > up[(False, s)][k] for s in (20, 50) for k in ('api_median', 'api_cheapest'))
            and all(up[(True, s)]['hybrid_cheapest'] / up[(True, s)]['api_cheapest']
                    < up[(False, s)]['hybrid_cheapest'] / up[(False, s)]['api_cheapest'] for s in (20, 50)),
        'storage dearer than prefill (M5 Max, 20%)': m['s20'][CLIENT]['hosting_month'] > m['s20'][CLIENT]['compute_month'],
        '1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)':
            all(util[(p, t, 1, f'{s}/day')]['own_cluster_session'] < util[(p, t, 1, f'{s}/day')]['hybrid_session']
                for p in ('design', 'conservative') for t in big for s in (1, 2)),
        '1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)':
            all(util[(p, t, 1, k)]['hybrid_session'] < util[(p, t, 1, k)]['own_cluster_session']
                for p in ('design', 'conservative') for t in big for k in ('4/day', 'full')),
        '1M: four sessions a day almost four times below the API':
            all(3.5 <= util[('design', t, 1, '4/day')]['api_session'] / util[('design', t, 1, '4/day')]['hybrid_session']
                < 4 for t in big),
        '1M: API cheapest for 10 people and fewer; at 50 own below API below hybrid':
            all(m['glm_long'][t]['api_session'] < min(m['glm_long'][t]['own_cluster_session'],
                                                      m['glm_long'][t]['hybrid_session']) for t in (5, 10))
            and m['glm_long'][50]['own_cluster_session'] < m['glm_long'][50]['api_session']
            < m['glm_long'][50]['hybrid_session'],
        '1M: refill of a million tokens on M3 Max takes longer than a day': min(m['refill'].values()) > 24,
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
P_CLOSED = ('07-economics.tex', 'Закрытый контур.}')
P_OPEN = ('07-economics.tex', 'Все числа этого раздела')
P_S20 = ('07-economics.tex', 'При доле 20\\% пользователь')
P_S50 = ('07-economics.tex', 'При доле 50\\% на открытую')
P_BUY = ('07-economics.tex', 'Покупка клиента')
P_HOST = ('07-economics.tex', 'Мак уже есть')
M_DEEP = ('07-economics.tex', 'Глубокий контекст.}')
M_OPEN = ('07-economics.tex', 'У поставщика GLM-5.3-Flash', 'sentence')
M_COST2 = ('07-economics.tex', '500 человек гибрид обходится в', 'sentence')
ABSTRACT = ('00-abstract.tex', 'Аннотация')
K14 = ('14-conclusion.tex', 'При доле открытой модели 20')
SITES = {
    'medium, design': [P_CLOSED],
    'medium, conservative': [P_CLOSED],
    'medium, both cases': [K14],
    'heavy saving, design': [P_CLOSED],
    'heavy saving, conservative': [P_CLOSED],
    'API per 1000 calls': [P_OPEN],
    'storage against prefill': [P_HOST],
    'conservative storage': [P_HOST],
    'hosting prices': [P_HOST],
    's20 hybrid dollars': [P_S20],
    's20 API dollars': [P_S20],
    's20 API median dollars': [P_S20],
    's20 below median, all clients, both cases': [ABSTRACT, K14],
    's20 above cheapest, all clients, both cases': [ABSTRACT, K14],
    's20 below median, all clients, design': [P_S20],
    's20 above cheapest, all clients, design': [P_S20],
    's20 below median, all clients, conservative': [P_S20],
    's20 above cheapest, all clients, conservative': [P_S20],
    's50 M5 Max capacity': [P_S50],
    's50 Max dollars': [P_S50],
    's50 API dollars': [P_S50],
    's50 API median dollars': [P_S50],
    's50 below median, Max clients': [P_S50],
    's50 above cheapest, Max clients, percent': [P_S50],
    's50 below median, Max clients, overflow at median': [P_S50],
    's50 Ultra dollars': [P_S50],
    's50 Ultra conservative dollars': [P_S50],
    's50 above cheapest, Ultra clients, percent': [P_S50],
    'purchase at 50%': [P_BUY],
    'purchase against cheapest': [P_BUY],
    'payback s50, overflow to cheapest': [P_BUY],
    'GLM API session to 1M': [M_OPEN, M_COST2],
    'GLM API session to 200k': [M_OPEN],
    'GLM growth of the session cost': [M_OPEN],
    'GLM two sessions, hybrid': [M_COST2],
    'GLM two sessions, own cluster': [M_COST2],
    'GLM full load, hybrid session': [M_DEEP],
    'GLM full load, below API': [M_DEEP, K14],
    'GLM full load, below own cluster': [M_DEEP, K14],
}

# The wording that states each direction, per site. Flipping it (cheaper/dearer, falls/rises, ...) must be reported.
DIRECTION_SITES = {
    'closed: medium, hybrid cheaper at every team size': [
        (P_CLOSED, 'раза дешевле своего серверного кластера на 50, 500 и 5000 человек'),
        (K14, 'раза дешевле своего серверного кластера')],
    'closed: heavy, hybrid cheaper at every team size': [(P_CLOSED, 'на сервере, и гибрид дешевле кластера на')],
    'cheapest API cheaper than the hybrid on every client, both shares and policies': [
        (P_S20, 'раза дороже, чем у самого дешёвого поставщика API'), (P_S20, 'раза дороже самого дешёвого поставщика'),
        (P_S50, '\\% дороже самого дешёвого API ('), (K14, 'раза дороже самого дешёвого'),
        (ABSTRACT, 'раза дороже самого дешёвого')],
    'at 50% Ultra clients dearer than the cheapest API': [
        (P_S50, 'дороже самого дешёвого API при хранении по политике протокола')],
    'storage dearer than prefill (M5 Max, 20%)': [(P_HOST, 'в месяц, больше, чем сам prefill')],
    '1M: own cluster cheaper at one and two sessions a day (500, 5000, both policies)': [
        (M_COST2, 'свой кластер стоит'), (M_COST2, 'и дешевле гибрида')],
    '1M: hybrid cheaper at four sessions a day and at full load (500, 5000, both policies)': [
        (M_DEEP, 'раза дешевле API и в'), (M_DEEP, 'раза дешевле своего кластера.'),
        (K14, 'раза дешевле своего кластера.')],
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


def check(texts, m=None):
    """Return (item, file) pairs for values, table rows and direction wording that the text does not carry, and the
    names of directions the engine rows no longer support, as (name, 'engine')."""
    m = m or model()
    expected = values(m)
    missing = []
    for k, sites in SITES.items():
        for site in sites:
            if norm(expected[k]) not in norm(scope(texts, site)):
                missing.append((k, site[0]))
    for row in econ_rows(m['s20'], m['s50'], m['b50']):
        if norm(row) not in norm(texts['07-economics.tex']):
            missing.append((f'client table row: {row}', '07-economics.tex'))
    holds = directions(m)
    for k, sites in DIRECTION_SITES.items():
        if not holds[k]:
            missing.append((k, 'engine'))
        for site, wording in sites:
            if norm(wording) not in norm(scope(texts, site)):
                missing.append((f'direction wording: {k}', site[0]))
    return missing + guard(texts, m, expected)


def read():
    """Every section; SITES and DIRECTION_SITES name some of them, the guard scans all."""
    return {n: open(os.path.join(SECTIONS, n), encoding='utf-8').read() for n in sorted(os.listdir(SECTIONS))
            if n.endswith('.tex')}


# Word forms of checked figures that the number patterns below do not catch.
CORE_FORMS = {
    'GLM growth of the session cost': ('в 21 раз',),
}
# Occurrences of a checked figure's printed form that publish a different quantity, each with its reason. An entry is
# (file, form, a substring of the source line that holds it, reason); an entry that matches nothing is reported.
ALLOW = ()


def guard_forms(k, v):
    """Distinctive printed forms of a value: ranges, dollar amounts, decimals with three or more digits, word forms."""
    forms = set(CORE_FORMS.get(k, ()))
    for m in re.finditer(r'\\\$\d[\d\\,.]*\d(?:--\d[\d.]*\d)?|\\\$\d|\d+(?:\.\d+)?--\d+(?:\.\d+)?|\d+\.\d{2,}|\d{2,}\.\d', v):
        forms.add(m.group(0))
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
    table_rows = econ_rows(m['s20'], m['s50'], m['b50'])
    used, found = set(), []
    forms = sorted({f for k in SITES for f in guard_forms(k, expected[k])})
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
    m = model()
    expected = values(m)
    controls, failed = 0, []
    # One negative control per value site: a stale value planted at that site alone must be reported there.
    for k, sites in SITES.items():
        for site in sites:
            got = check(plant(texts, site, expected[k], perturb(expected[k])), m)
            if (k, site[0]) not in got:
                failed.append(('stale value not reported', k, site))
            controls += 1
    # One negative control per direction site: the flipped wording must be reported there.
    for k, sites in DIRECTION_SITES.items():
        for site, wording in sites:
            got = check(plant(texts, site, wording, flip(wording)), m)
            if (f'direction wording: {k}', site[0]) not in got:
                failed.append(('flipped wording not reported', k, site))
            controls += 1
    assert not failed, failed
    # Guard: a checked figure printed in a section that no list names must be reported.
    related = texts['12-related.tex'] + '\nСессия гибрида стоит \\$4.2--4.6.\n'
    assert ('unregistered occurrence of \\$4.2--4.6', '12-related.tex') in check(dict(texts, **{'12-related.tex': related}), m)
    limits = texts['11-limitations.tex'] + '\nСессия до миллиона стоит в 21 раз дороже.\n'
    assert ('unregistered occurrence of в 21 раз', '11-limitations.tex') in check(dict(texts, **{'11-limitations.tex': limits}), m)
    # Table rows: a stale cell in the client table must be reported.
    row = econ_rows(m['s20'], m['s50'], m['b50'])[2]
    assert any(k.startswith('client table row') for k, _ in check(dict(texts, **{'07-economics.tex': texts[
        '07-economics.tex'].replace(row, row.replace('883', '637'), 1)}), m)), 'stale client row'
    # Engine directions: rows changed so that a stated direction no longer holds must be reported.
    def flipped(**changes):
        return check(texts, dict(m, **changes))
    d = m['design']
    assert ('closed: medium, hybrid cheaper at every team size', 'engine') in flipped(
        design={**d, ('medium', 500, 'hybrid'): d[('medium', 500, 'own')] + 1})
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
