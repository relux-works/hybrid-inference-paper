#!/usr/bin/env python3
"""Check run-14 bounds, tables and finite source-transcribed measurements.

The ideal-client example excludes reload, import and last token. B300 compute is
recomputed from twelve measured B300 bulk observations, at each stated depth.
vLLM's cold-fit and cached-delta rates are separate server-only observations;
they do not qualify full-call delivery through a client bridge. Inputs are the
reviewed run-14 CSV snapshot and original measurements. Overnight constants below are transcribed
from the orchestrator's FACTS.md (snapshot SHA256 and evidence paths in the
r10 section of calc/PAPER-V2-GAPS-261101.md), not fitted by this checker.
Every site has an independent wrong-rate/value or qualification plant.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
ENGINE = HERE / 'engine'
MEASUREMENTS = HERE.parents[1] / 'calc/out/run14/measurements'
SECTIONS = HERE.parent / 'sections'
EXAMPLE = ('Qwen3.8-27B', '32', 'M5 Max 128 GB', '10000', '110000')


def rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def server_rate(depth=110000):
    """Depth-specific B300 FLOP rate from its own measured bulk OLS fit."""
    points = rows(MEASUREMENTS / 'b300_bulk.csv')
    x = sum(float(r['depth']) for r in points) / len(points)
    y = sum(float(r['seconds_token']) for r in points) / len(points)
    b = sum((float(r['depth'])-x)*(float(r['seconds_token'])-y) for r in points) / sum((float(r['depth'])-x)**2 for r in points)
    a = y-b*x
    # The reference model's operation count is affine in depth. Recover both
    # coefficients from the snapshot, rather than repeating model geometry.
    intensity = {float(r['depth']): float(r['flop_new_token']) for r in rows(ENGINE / 'flop_per_byte.csv')
                 if r['model'] == EXAMPLE[0]}
    low, high = min(intensity), max(intensity)
    slope = (intensity[high] - intensity[low]) / (high - low)
    work = intensity[low] + slope * (depth - low)
    rate = work / (a + b * depth)
    # Retain every measured-envelope rate in the turn table, with the original
    # 1e-9 relative numerical agreement, instead of asserting one constant.
    for row in rows(ENGINE / 'turn_speedup.csv'):
        d = float(row['depth'])
        want = (intensity[low] + slope * (d - low)) / (a + b * d)
        assert abs(want - float(row['server_compute'])) <= 1e-9 * want, ('llama.cpp rate', d)
    return rate


def values():
    selected = {float(r['link_mbit']): r for r in rows(ENGINE / 'flop_per_byte.csv')
                if (r['model'], r['state_bits'], r['client'], r['portion_tokens'], r['depth']) == EXAMPLE}
    server = server_rate()
    out = {}
    for link in (1000.0, 10000.0):
        r = selected[link]
        work = float(r['portion_tokens']) * float(r['flop_new_token'])
        local = work / float(r['client_peak_flop_s'])
        transfer = float(r['delta_bytes']) / (link * 1e6 / 8)
        bound = local / transfer
        assert abs(bound - float(r['ratio'])) <= 1e-9 * bound, (bound, r['ratio'])
        out[link] = (bound, local / (work / server + transfer))
    return out, server / float(selected[1000.0]['client_peak_flop_s'])


def expected():
    """Named check -> (section, paragraph marker, exact computed wording)."""
    out, ceiling = values()
    physics = ('05b-models.tex', r'\textbf{Физика выигрыша.}')
    caption = ('05b-models.tex', r'\caption{Вычисления prefill')
    fp8 = ('06-server.tex', r'\textbf{Серверный FP8.}')
    result = {}
    def add(name, site, wording):
        result[name] = (*site, wording)
    add('channel 1G', physics, f'граница равна {out[1000.0][0]:.1f};')
    add('llama.cpp bound 1G', physics, f'не больше {out[1000.0][1]:.1f} раза')
    add('channel 10G', physics, f'граница вырастает до {out[10000.0][0]:.0f},')
    add('llama.cpp bound 10G', physics, f'выигрыш не больше {out[10000.0][1]:.0f} раз.')
    add('llama.cpp ceiling', physics, f'Выше {ceiling:.1f} раза')
    add('bound is possibility, actual gain includes overhead', physics,
        'Граница больше единицы оставляет возможность выигрыша даже против идеального клиентского движка. '
        'Фактический выигрыш зависит от времени сервера, подъёма копии, вставки и очередей.')
    add('llama.cpp rate at 110k', caption, f'со скоростью {server_rate() / 1e15:.2f}~PFLOPS на глубине 110 тысяч')
    cold = [r for r in rows(MEASUREMENTS / 'vllm_cold.csv') if r['option'] == 'fp8-default']
    assert cold and all(r['server_only'] == '1' and r['client_bridge'] == '0' for r in cold)
    fits = {(float(r['a']), float(r['b'])) for r in cold}
    assert len(fits) == 1, fits
    a, b = fits.pop()
    # Integrate the cold-fit marginal seconds over a 10k-token portion. These
    # are fitted portion rates, not observed whole-prompt cold token rates.
    rate = lambda d: 1 / (a + b * (d + 10000 / 2))
    add('vLLM cold-fit 16k', fp8, f'порции 10\\,000 токенов {rate(16000):.0f} токена/с на глубине 16 тысяч')
    add('vLLM cold-fit 249k', fp8, f'и {rate(249000):.0f} на глубине 249 тысяч')
    cached = [r for r in rows(MEASUREMENTS / 'vllm_cached.csv') if r['option'] == 'fp8-default']
    assert cached and all(r['server_only'] == '1' and r['client_bridge'] == '0' for r in cached)
    rates = {(int(r['depth']), int(r['delta'])): float(r['delta_tok_s']) for r in cached}
    for depth, label in ((16384, '16'), (65536, '65'), (131072, '131'), (249000, '249')):
        pair = f'{rates[depth, 2000]:.0f}/{rates[depth, 10000]:.0f}'
        suffix = 'токена/с на глубине 16 тысяч' if label == '16' else ('на 131 тысяче' if label == '131' else f'на {label} тысячах')
        add('vLLM cached ' + label + 'k', fp8, pair + ' ' + suffix)
    add('vLLM server-only qualification', fp8, 'Эти скорости FP8 относятся только к серверному исполнению.')
    result.update(overnight_expected())
    result.update(run14_expected())
    result.update(run15_expected())
    result.update(rc3_amendment_expected())
    result.update(rc3_review2_expected())
    result.update(run16_expected())
    result.update(v4b_expected())
    result.update(v4c_expected())
    result.update(v5a_expected())
    result.update(v5a3_expected())
    result.update(v5a4_expected())
    from v5b_economics import expected as v5b_expected
    result.update(v5b_expected())
    result.update({'v5c '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05/v5c-sites-current.json').read_text())})
    result.update({'v5d1 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05/v5d1-sites-current.json').read_text())})
    result.update({'v5d2 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05/v5d2-sites-current.json').read_text())})
    result.update({'v5d3 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05/v5d3-sites-current.json').read_text())})
    result.update({'v5d4 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05/sites.json').read_text())})
    result.update({'v5d5 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d5-2026-11-05/sites.json').read_text())})
    result.update({'v5d6 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d6-2026-11-05/sites.json').read_text())})
    result.update({'v5d7 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d7-2026-11-05/sites.json').read_text())})
    result.update({'v5d8 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d8-2026-11-05/sites.json').read_text())})
    result.update({'v5d9 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d9-2026-11-05/sites.json').read_text())})
    result.update({'v5d10 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d10-2026-11-06/sites.json').read_text())})
    result.update({'v5d11 '+r['name']:(r['file'],r['marker'],r['phrase']) for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d11-2026-11-06/sites.json').read_text())})
    return result


def overnight_expected():
    """Finite source-transcribed sites; no inferred run14 economics or calibration."""
    result = {}
    def add(name, file, marker, wording):
        result['overnight ' + name] = (file, marker, wording)
    clients = '05-clients.tex'
    parallel = r'\label{tab:parallel-decode}'
    # Each row fixes depth, stream columns and aggregate rates together.
    for name, row in (
        ('M3 32k', 'M3 Max & 32 & 8.44 & & 13.2 & & & & &'),
        ('M3 64k', 'M3 Max, шаг 55 & 64 & 7.2 & 11.9 & 13.9 & & 15.6 & & 27.2 & 31.9'),
        ('M3 restored 128k', 'M3 Max, восстановлен & 128 & 7.683 & 11.488 & 12.966 & 13.348 & 12.670 & & &'),
        ('M3 warm 128k', 'M3 Max, шаг 55 & 128 & & & & & & 13.9 & &'),
        ('M3 260k', 'M3 Max, шаг 56 & 260 & 5.98 & 7.63 & 7.03 & 6.68 & 6.42 & & &'),
        ('M5 32k', 'M5 Max & 32 & 18.29 & & 33.37 & & & & &'),
    ):
        add(name, clients, parallel, row)
    add('parallel denominators', clients, r'\textbf{Параллельная генерация.}',
        'Для M3 Max на глубине 32 тысячи скорости 8.44 и 13.2 токена/с рассчитаны по '
        'времени запросов, а четыре потока по интервалам генерации дают 14.05 токена/с.')
    add('warm lower bound', clients, r'\caption{Измеренная суммарная генерация',
        'Точка 12 потоков при 128 тысячах снята сразу после 34-минутного prefill и обозначает нижнюю границу.')
    agents = r'\textbf{Реалистичные агенты.}'
    add('agent stream speed', clients, agents,
        'При 1, 2, 4 и 8 сессиях средняя скорость одного потока Mac равна 7.00, 4.73, 2.97 и 1.63 токена/с,')
    add('agent p90', clients, agents, 'p90 времени вызова составляет 270.8, 262.5, 903.8 и 1142.0 секунды.')
    add('Mac prefill share', clients, agents, 'Доля prefill во времени вызовов Mac равна 3.9, 26.1, 14.4 и 9.6\\%;')
    add('PRO prefill share', clients, agents, 'у PRO 6000 на тех же вызовах доля prefill составляет 1.6, 8.7, 4.5 и 3.6\\%.')
    add('large tool output', clients, agents,
        'результат на 8193 токена при 4--8 сессиях Mac читает за 241--247 секунд, PRO 6000 за 9.8--10.2 секунды.')
    add('cooled sweep pending', clients, agents,
        'Охлаждённые медианы комплекта 1.6.6 при PRI~4 входят в промежуточный расчёт ёмкости дня прогона 16.')
    add('agent gain pending', clients, agents,
        'Модель времени шага 57 ниже измеренного локального времени на 8, 22, 37 и 33\\% при 1, 2, 4 и 8 сессиях.')
    server = '06-server.tex'
    for depth, cells in (
        (16, '1757 & 1658 & 1659 & 1663 & 79.6'), (50, '1580 & 1456 & 1475 & 1485 & 67.6'),
        (100, '1388 & 1232 & 1267 & 1284 & 54.8'), (150, '1212 & 1066 & 1110 & 1131 & 46.3'),
        (200, '1074 & 941 & 990 & 1010 & 40.1'), (249, '966 & 844 & 892 & 915 & 35.4'),
    ):
        add('B300 ladder ' + str(depth), server, r'\label{tab:b300-llama}', f'{depth} & {cells}')
    for depth, cells in ((16, '24031 & 24841'), (50, '19096 & 21846'),
                         (100, '14667 & 18555'), (249, '8673 & 12806')):
        add('B300 cold marginal ' + str(depth), server, r'\label{tab:b300-vllm}', f'{depth} & {cells}')
    b300 = r'\textbf{FP8 на B300.}'
    add('B300 portion comparison', server, b300,
        'Для порции 10\\,000 токенов на глубине 16 тысяч аппроксимация даёт 23\\,151 токен/с против 1663 у llama.cpp на той же B300.')
    add('B300 cached default', server, b300,
        'Кэшированные порции в 2000/10\\,000 токенов с обычным кэшем и блоками по 784 токена дали '
        '11\\,638/20\\,140 на глубине 16 тысяч, 8755/14\\,768 на 65 тысячах, 7251/11\\,185 на 131 тысяче '
        'и 4134/6987 токенов/с на 249 тысячах.')
    add('B300 cached FP8 KV', server, b300,
        'С кэшем FP8 и блоками по 1568 токенов на глубине 16 тысяч получено 13\\,761/20\\,961 токен/с.')
    add('B300 server only', server, b300, 'Все эти скорости относятся только к серверному исполнению.')
    bridge = r'\textbf{Первый запуск моста состояния.}'
    add('bridge export and probe', server, bridge,
        'B300 с vLLM 0.32.0 FP8 экспортировала состояние на 784 токенах; клиент llama.cpp на той же карте '
        'сравнивался со своим локальным prefill на 64 позициях.')
    add('bridge BF16', server, bridge, 'Клиент BF16 получил совпадение top-1 в 64/64 позициях и средний KL 0.00055 нат,')
    add('bridge Q4', server, bridge, 'клиент Q4\\_K\\_M совпал в 64/64 позициях при среднем KL 0.0027 нат.')
    add('bridge heterogeneous uncalibrated', server, bridge,
        'Это гетерогенная некалиброванная проверка: серверные веса FP8 отличаются от клиентских GGUF.')
    add('bridge finite qualification', server, bridge,
        'Проверка моста измеряет приближённую эквивалентность на этих позициях и не устанавливает побитовое совпадение или скорость полного гибридного вызова.')
    add('bridge depth pending', server, bridge,
        'На глубине 31\\,360 токенов средний KL равен 0.0031 нат у BF16 и 0.0061 нат у Q4\\_K\\_M, top-1 совпал в 64/64 позициях у обоих клиентов.')
    add('bridge adapter pending', server, r'\textbf{Сквозная проверка узла vLLM.}', 'стандартный прокси и клиент llama.cpp Q4\\_K\\_M на той же карте; все вставки завершились.')
    add('B300 economics pending', server, 'Экономические оценки B300 используют',
        'Экономические оценки B300 используют измеренную кривую llama.cpp; цены vLLM обозначены как серверные без квалификации полного гибридного вызова.')
    channel = '04-channel.tex'
    cost = r'\textbf{Стоимость вставки состояния.}'
    add('import fixed and token costs', channel, cost,
        'Каждый оффлоад несёт около 158~МБ фиксированных данных, преимущественно рекуррентного состояния, '
        'и требует около 1.6 секунды фиксированного времени вставки плюс около 0.52~мс на токен.')
    add('import long delta', channel, cost,
        'Для 39\\,146 новых токенов передано 1.99~ГБ; вставка заняла 20.2 секунды при серверном prefill 10.6--10.8 секунды.')
    add('import Mac single point', channel, cost,
        'У M3 Max при PRI~4 на канале 16.0~МБ/с с RTT 110~мс одна историческая точка вставки даёт 1.07~мс на токен: 42.4 секунды на 39\\,504 токена.')
    add('import version qualification', channel, cost,
        'Эти замеры обозначены \\texttt{pre-import-speed-v2};')
    return result


def run14_expected():
    """Snapshot-derived publication rows and finite measurement qualifications."""
    result = {}
    def add(name, file, marker, wording):
        result['run14 ' + name] = (file, marker, wording)
    def table(name, file, label, row):
        add(name, file, r'\label{' + label + '}', row + r' \\')
    client_labels = ['M3 Max 128 ГБ', 'M4 Max 128 ГБ', 'M5 Max 64 ГБ', 'M5 Max 128 ГБ',
                     'M5 Ultra 96 ГБ', 'M5 Ultra 256 ГБ', 'AMD Strix Halo 128 ГБ', 'NVIDIA DGX Spark']
    clients = [r for r in rows(ENGINE/'client_sessions_day.csv') if r['link_mbit'] == '1000.0']
    for label, r in zip(client_labels, clients):
        table('client '+r['client'], '91-calculation-history.tex' if label.startswith('M4 ') else '05-clients.tex', 'v5a4-m4-row' if label.startswith('M4 ') else 'tab:clients',
              label + ' & ' + ' & '.join(f'{float(r[k]):.{n}f}' for k,n in
              [('single_tok_s_32k',1),('local_sessions_day',2),('hybrid_sessions_day',2),('gain',2)]))
    for r in rows(ENGINE/'client_agents_day.csv'):
        if r['link_mbit'] != '1000': continue
        table('agents '+r['agents'], '05-clients.tex', 'tab:agents-day',
              (r['agents'] + (r'\textsuperscript{†}' if r['agents']=='6' else '')) + ' & ' + ' & '.join(f'{float(r[k]):.2f}' for k in
              ('local_sessions_day','hybrid_sessions_day','gain')) + ' & ' +
              ' & '.join(f'{100*float(r[k]):.1f}'+r'\%' for k in
              ('depth_modelled_call_share','depth_modelled_decode_time_share')))
    add('mostly modelled 16', '05-clients.tex', r'\textbf{Выигрыш по числу агентов.}',
        'Строка 16 агентов остаётся модельной: 47.4\\% вызовов и 63.9\\% времени генерации лежат глубже измеренных опорных точек.')
    add('import qualification', '05-clients.tex', r'\caption{Условных сессий',
        'Вставка состояния включена; коэффициент M3 Max перенесён на остальные клиенты как некалиброванная оценка.')
    add('M5 source', '05-clients.tex', r'\textbf{Сколько успевает клиент за день.}',
        'M5 Max с 128~ГБ использует измеренные кривые той же SoC M5 Max с 64~ГБ; M5 Ultra масштабирует эти кривые по вычислениям и полосе памяти.')
    channel = '04-channel.tex'
    turns = [r for r in rows(ENGINE/'turn_speedup.csv') if r['state_format']=='f32']
    for depth in (100000,200000):
        for portion in (2000,10000):
            selected = {int(float(r['link_mbit'])):r for r in turns if int(r['depth'])==depth and int(r['portion'])==portion}
            row = f'{portion//1000} тыс., {depth//1000} тыс. & {float(selected[1000]["local_prefill_s"]):.1f} с'
            for link in (100,300,1000,10000):
                r=selected[link];row+=f' & {float(r["hybrid_s"]):.1f} с ({float(r["speedup"]):.1f}×)'
            table(f'turn {depth}/{portion}', channel, 'tab:turn', row)
    shots=[r for r in rows(ENGINE/'oneshot_ingest.csv') if r['state_format']=='f32']
    for depth in (100000,200000,262000):
        selected={int(float(r['link_mbit'])):r for r in shots if int(r['context'])==depth}
        row=f'{depth//1000} тыс. токенов & {float(selected[1000]["local_s"])/60:.1f} мин'
        row+=''.join(f' & {float(selected[link]["hybrid_ttft_s"]):.0f} с' for link in (100,300,1000,10000))
        table('oneshot '+str(depth), channel, 'tab:oneshot', row)
    labels=['M3 Max, 128~ГБ','M5 Max, 64~ГБ, модель времени','MacBook Air M5, 32~ГБ, оценка']
    source=rows(ENGINE/'transcript_example.csv')
    for label,client in zip(labels,dict.fromkeys(r['client'] for r in source)):
        data={int(float(r['link_mbit'])):r for r in source if r['client']==client}
        a,b=data[200],data[1000]
        row=label+' & '+' & '.join(f'{float(r[k])/60:.1f} мин' for r,k in
             [(a,'local_ttft_s'),(a,'hybrid_ttft_s'),(b,'hybrid_ttft_s'),(a,'local_total_s'),(a,'hybrid_total_s'),(b,'hybrid_total_s')])
        table('transcript '+client,channel,'tab:transcript',row)
    for bits in (32,16):
        data={int(float(r['link_mbit'])):r for r in rows(ENGINE/'offload_by_link.csv') if int(r['state_bits'])==bits}
        table('offload share '+str(bits),channel,'tab:offload',f'Состояние в {bits} битах: доля вызовов & '+
              ' & '.join(f'{100*float(data[link]["share_calls"]):.1f}'+r'\%' for link in (100,300,1000,2500)))
        table('offload saved '+str(bits),channel,'tab:offload',r'\quad экономия на вызов, с & '+
              ' & '.join(f'{float(data[link]["saved_seconds_call"]):.1f}' for link in (100,300,1000,2500)))
    turn={int(float(r['link_mbit'])):r for r in turns if r['depth']=='200000' and r['portion']=='10000'}
    add('large turn narrative',channel,r'\textbf{Один ход.}',
        f'отдаёт её за {float(turn[100]["hybrid_s"]):.0f} секунд, через гигабит за {float(turn[1000]["hybrid_s"]):.0f} секунды.')
    shot=next(r for r in shots if r['context']=='200000' and r['link_mbit']=='1000.0')
    add('oneshot narrative',channel,r'\textbf{Разовая загрузка.}',
        f'за {float(shot["hybrid_ttft_s"]):.0f} секунды: {float(shot["server_prefill_s"]):.0f} секунд считает сервер, {float(shot["import_s"]):.0f} секунд занимает вставка,')
    cost=next(r for r in rows(ENGINE/'person_cost_s50.csv') if r['client']=='M3 Max 128 GB (measured)' and r['team']=='50' and r['basis']=='Mac already owned')
    add('traffic day client subject',channel,r'\textbf{Трафик как статья расходов.}',
        f'За восьмичасовой день клиент успевает обслужить около {float(cost["served_day"]):.0f} вызовов,')
    add('traffic compute storage narrative',channel,r'\textbf{Трафик как статья расходов.}',
        f'против примерно \\${float(cost["compute_month"])+float(cost["hosting_month"]):.0f} на серверное вычисление и хранение сессий для того же пользователя')
    validation = rows(ENGINE/'growing_5g_validation.csv')
    base = next(r for r in validation if r['turn']=='0' and r['import_variant']=='prototype_depth')
    add('16.0 MB/s prediction',channel,r'\textbf{Прогноз для измеренного запуска.}',
        f'локальный prefill базы {float(base["predicted_local_prefill_s"]):.1f} секунды против TTFT {float(base["measured_local_ttft_s"]):.1f};')
    econ = '91-calculation-history.tex'
    add('economics M5 measured basis', econ, r'\caption{Гибрид на человека в месяц',
        'по измеренным кривым M3 Max и M5 Max с 64~ГБ. M5 Max с 128~ГБ использует измеренные кривые той же SoC M5 Max с 64~ГБ; '
        'M5 Ultra масштабирует эти кривые по вычислениям и полосе памяти. Перенос на M5 Max с 128~ГБ и M5 Ultra '
        'не подтверждён отдельными измерениями. M4 Max оценён по вычислительной мощности и полосе памяти.')
    add('B300 light reference five', econ, 'B300 покупается целиком',
        'на пять человек при лёгкой нагрузке с одним узлом')
    for team, word in ((5, 'пяти'), (20, 'двадцати')):
        label = 'five' if team == 5 else 'twenty'
        reference = next(r for r in rows(ENGINE/'perimeter_cost.csv') if r['route'] == 'all server' and
                         r['server'] == 'Owned HGX B300 8-GPU' and r['profile'] == 'light' and r['team'] == str(team))
        amount = f'{float(reference["person_month"]):,.0f}'.replace(',', r'\,')
        add('B300 light reference ' + label + ' comparison', econ, 'Команде из ' + word + ' человек нужна',
            'против \\$' + amount + ' на человека при лёгкой нагрузке с одним узлом B300.')
    price=rows(ENGINE/'breakeven_prefill_price.csv')
    selected=[]
    for share in ('0.2','0.5'):
        for client in ('M3 Max 128 GB (measured)','M5 Max 64 GB'):
            selected.append(next(r for r in price if r['client']==client and r['share']==share and
                r['basis']=='owned' and r['storage_policy']=='default' and r['target']=='cheapest API'))
    for title,key in [('Передача','transfer_month'),('Хранение','storage_month'),('Обслуживание','front_month'),
                      ('Миграция','migration_month'),('Электричество клиента','client_power_month'),
                      ('Вызовы сверх ёмкости, API','overflow_api_month'),('Всего при бесплатном prefill','zero_prefill_price_month'),
                      ('Самый дешёвый API','api_month')]:
        table('zero-price '+key,'91-calculation-history.tex','tab:breakeven',title+' & '+
              ' & '.join(r'\$'+f'{float(r[key]):.2f}' for r in selected))
    verdict=lambda r: 'нет порога' if r['verdict']=='no break-even' else r'\$'+f'{float(r["price_usd_mtoken"]):.3f}'
    table('zero-price verdict','91-calculation-history.tex','tab:breakeven','Порог, долларов за млн токенов & '+ ' & '.join(map(verdict,selected)))
    median=[r for r in price if r['basis']=='owned' and r['storage_policy']=='default' and r['share']=='0.2' and r['target']=='median API']
    assert all(r['verdict']!='no break-even' for r in median)
    thresholds=[float(r['price_usd_mtoken']) for r in median]
    m5_threshold = next(r for r in selected if r['client']=='M5 Max 64 GB' and r['share']=='0.5')
    add('M5 cheapest threshold','91-calculation-history.tex',r'\textbf{Цена безубыточности prefill.}',
        f'У M5 Max при доле 50\\% остаётся порог \\${float(m5_threshold["price_usd_mtoken"]):.3f} за миллион токенов, ниже всех измеренных серверных затрат.')
    add('median threshold','91-calculation-history.tex',r'\textbf{Цена безубыточности prefill.}',
        f'Против медианного API при доле 20\\% порог равен \\${min(thresholds):.1f}--{max(thresholds):.1f} за миллион токенов для уже имеющегося клиента при хранении по политике протокола.')
    costs=[]
    for key,label in [('llamacpp_pro6000','llama.cpp PRO 6000'),('vllm_pro6000','vLLM PRO 6000'),
                      ('vllm_b300_auto','vLLM B300'),('vllm_b300_fp8kv','vLLM B300 с кэшем FP8')]:
        vals=[float(r[key+'_usd_mtoken']) for r in median]
        lo, hi = f'{min(vals):.2f}', f'{max(vals):.2f}'
        costs.append(f'{label} \\${lo}' + ('--'+hi if lo != hi else ''))
    add('measured server prices','91-calculation-history.tex',r'\textbf{Цена безубыточности prefill.}',
        'Серверная стоимость миллиона токенов prefill по измеренным кривым: '+', '.join(costs)+'.')
    budget=next(r for r in rows(ENGINE/'perimeter_cost.csv') if r['route']=='all server')
    add('common own budgets','91-calculation-history.tex','Одни клиентские машины почти',
        f'Обе схемы сохраняют четыре сессии на человека полный месяц; бюджет среднего prefill равен {float(budget["latency_mean_limit_s"]):.1f} секунды, p90 {float(budget["latency_p90_limit_s"]):.1f} секунды.')
    glm=next(r for r in rows(ENGINE/'glm_long_sessions.csv') if r['context']=='1000000')
    add('GLM cold load','91-calculation-history.tex',r'\textbf{Клиент для миллиона токенов.}',
        f'а серверная часть на B300 вместе с передачей по гигабитному каналу занимает по оценке {float(glm["ingest_1m_server_s"]):.0f} секунды.')
    add('GLM cold scope','91-calculation-history.tex',r'\textbf{Клиент для миллиона токенов.}',
        'Эта оценка холодной загрузки исключает вставку состояния; перенос скорости B300 на GLM оценочный.')
    sixteen=next(r for r in rows(ENGINE/'client_agents_day.csv') if r['agents']=='16' and r['link_mbit']=='1000')
    add('flag union 16','05-clients.tex',r'\label{tab:agents-day}',
        f'Строка 16 модельная: хотя бы один флаг имеют {100*(1-float(sixteen["measured_call_share"])):.1f}\\% вызовов и {100*(1-float(sixteen["measured_decode_time_share"])):.1f}\\% времени генерации.')
    for flag,label in [('depth_modelled','моделируемая глубина'),('count_conservative','подстановка числа потоков'),
                       ('measured_lower_bound','нижняя граница'),('shallow','ограничение малой глубины')]:
        add('flag share 16 '+flag,'05-clients.tex',r'\label{tab:agents-day}',
            f'{label} {100*float(sixteen[flag+"_call_share"]):.1f} / {100*float(sixteen[flag+"_decode_time_share"]):.1f}\\%')
    candidates=rows(ENGINE/'symmetric_storage_candidates.csv')
    rejected=sum(float(r['prefill_mean_s'])>float(r['latency_mean_limit_s']) or
                 float(r['prefill_p90_s'])>float(r['latency_p90_limit_s']) for r in candidates)
    assert rejected == 0, 'symmetric latency observation changed'
    add('symmetric nonbinding latency','91-calculation-history.tex','Одни клиентские машины почти',
        f'Ограничение задержки не отсекло ни одного из {len(candidates)} вариантов: сравнение определяется стоимостью при равном хранении.')
    smoke=r'\textbf{Сквозная проверка узла vLLM.}'
    add('node smoke8k','06-server.tex',smoke,
        'На глубине 8 тысяч гибрид дал KL 0.0055 нат, top-1 63/64, отношение к собственному шуму разбивки клиента 0.87.')
    add('node smoke32k','06-server.tex',smoke,
        'На глубине 32 тысячи получены KL 0.0256 нат, top-1 60/64 и отношение 2.38;')
    add('node smoke divergence','06-server.tex',smoke,'свободная генерация разошлась на девятом токене.')
    add('node smoke timing','06-server.tex',smoke,
        'равно 2.72 секунды локально и 4.15 секунды при оффлоаде. Одна GPU делает этот запуск функциональной проверкой.')
    add('node smoke qualification','06-server.tex',smoke,
        'Проверка гетерогенная и некалиброванная, FP8 на узле и Q4 на клиенте; код выхода 5 сохраняет этот статус.')
    add('price boundary','91-calculation-history.tex',r'\textbf{Цена безубыточности prefill.}',
        'На измеренных клиентах при доле 20\\% гибрид блокируют накладные расходы даже при бесплатном prefill.')
    add('vLLM price server only','91-calculation-history.tex',r'\textbf{Цена безубыточности prefill.}',
        'Цены vLLM относятся только к серверу (server-only); мост не квалифицирован по времени полного вызова.')
    add('pilot correct','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Во всех четырёх вариантах правильны 35 из 48 ответов.')
    add('pilot disagreement','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Оффлоад расходится с локальным ответом в 4/48 случаях; другая локальная разбивка prefill даёт те же 4/48, повтор при той же разбивке даёт 0/48.')
    add('pilot partial','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Глубина 128 тысяч покрыта частично: запуск прерван при заполнении диска.')
    add('pilot finite','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Этот пилот не устанавливает эквивалентность; разнородные кванты проверены отдельно.')
    return result



def run15_expected():
    """Current measured claims, with finite FACTS/owner evidence in the v3 gap map."""
    result = {}
    def add(name, file, marker, wording):
        result['run15 ' + name] = (file, marker, wording)
    def table(name, file, label, row):
        add(name, file, r'\label{' + label + '}', row + r' \\')
    client = '05-clients.tex'
    anchors = {(int(r['depth']), int(r['streams'])): float(r['aggregate_tok_s'])
               for r in rows(ENGINE/'parallel_anchors.csv')}
    anchors.update({(int(r['depth']), int(r['streams'])): float(r['aggregate_tok_s'])
                    for r in rows(ENGINE/'parallel_historical_sensitivity.csv') if 'kit1.6.6' in r['condition'] and r['streams']=='1'})
    for i, (depth, label) in enumerate(((32784,32),(65552,64),(131088,128))):
        cells = [f'{anchors[depth,s]:.2f}' if (depth,s) in anchors else ''
                 for s in (1,2,4,6,8,12,16,24,32)]
        table('cooled anchor '+str(i),client,'tab:parallel-decode',
              f'M3 Max, 1.6.6 & {label} & '+' & '.join(cells))
    transcript = next(r for r in rows(ENGINE/'transcript_example.csv')
                      if r['client']=='M3 Max 128 GB (measured)' and float(r['link_mbit'])==1000)
    marker = r'\textbf{Пример вне программирования.}'
    for name, key, prefix, suffix in (
        ('summary minutes','summary_decode_s','ещё ',' минуты'),
        ('hybrid total minutes','hybrid_total_s','задача занимает ',' минуты'),
        ('local total minutes','local_total_s','вместо ','.'),
    ):
        add('transcript prose '+name,'04-channel.tex',marker,
            prefix+f'{float(transcript[key])/60:.1f}'+suffix)
    add('cooled protocol',client,r'\textbf{Параллельная генерация.}',
        'После заполнения каждой глубины сервер ждёт 300 секунд и восстанавливает слот перед каждым из трёх повторов.')
    add('np4 sensitivity',client,r'\textbf{Параллельная генерация.}',
        'дал 16.03 токена/с на четырёх потоках против 14.35 при 16 слотах; контроль не подменяет базу.')
    add('six coverage',client,r'\noindent\footnotesize',
        'Для шести агентов измеренная зона покрывает 0\\% вызовов; 90.67\\% вызовов используют удержанную суммарную скорость 6.68 токена/с из точки при 260 тысячах.')
    add('six exclusion',client,r'\noindent\footnotesize',
        'Строка сохраняется в таблице и исключена из трендов и отношений роста ёмкости по числу агентов.')
    add('daily M3 prose',client,r'\textbf{Сколько успевает клиент за день.}',
        'равна 3.97 условной сессии, гибридная 5.47, выигрыш 1.38 раза.')
    add('cooled bandwidth share',client,r'\textbf{Скорость генерации и её запас.}',
        'Охлаждённый замер при PRI~4 дал 24.03 токена в секунду на четырёх потоках против 8.77 у одного, около 37\\% этого предела.')
    add('capacity gains',client,'Переход от одного к четырём,',
        'в 1.30, 1.46 и 1.57 раза, гибридную в 1.46, 1.72 и 1.92 раза.')
    add('capacity four sixteen',client,'Переход от одного к четырём,',
        'Переход от четырёх к шестнадцати даёт 1.21 и 1.31 раза соответственно.')
    add('measured zone16',client,r'\textbf{Выигрыш по числу агентов.}',
        'Измеренная зона покрывает 44.75\\% вызовов и 25.73\\% времени генерации.')
    add('depth zone4',client,r'\textbf{Выигрыш по числу агентов.}',
        'На четырёх агентах эти доли равны 9.3\\% и 22.4\\%.')
    traffic = rows(ENGINE/'traffic_user_month.csv')[-1]
    add('traffic volume','04-channel.tex',r'\textbf{Трафик как статья расходов.}',
        f'это около {float(traffic["hybrid_tb_month"]):.2f}~ТБ. По цене колокации около \\$5 за терабайт это \\${float(traffic["egress_1"]):.0f} в месяц,')
    add('traffic high egress','04-channel.tex',r'\textbf{Трафик как статья расходов.}',
        f'от \\${float(traffic["egress_2"]):.0f} до \\${float(traffic["egress_3"]):.0f} против')
    add('conclusion M3 gain','91-calculation-history.tex','результата. Ожидание prefill', 'на M3 Max в 1.38 раза')
    models = '05b-models.tex'
    add('SWA GPU exact',models,r'\textbf{Проверка скользящего окна.}',
        'подтвердила побитовое совпадение при одинаковой разбивке для Glimmer, Gemma 4 и Qwen с состоянием, передаваемым по частям;')
    for i,row in enumerate((
        '16 & 3909 / 63.8 & 2977 / 56.0 & 4171 / 73.4 & 116.0 / 9.04 & 173.5 / 16.3',
        '50 & 2716 / 57.2 & 1633 / 44.1 & 3616 / 68.1 & 50.2 / 6.58 & 107.3 / 10.34',
        '100 & 1767 / 49.6 & 1039 / 33.5 & 3015 / 61.6 & 26.2 / 5.01 & 71.2 / 9.04',
        '118 & & & 2823 / 59.4 & & 67.4 / 8.82',
        '150 & 1345 / 43.5 & 767 / 27.0 & & 20.3 / 4.20 &',
        '200 & 1097 / 38.4 & 613 / 22.6 & & 16.5 / 3.64 &',
        '249 & 925 / 34.5 & 510 / 19.5 & & 13.3 / 3.15 &',
    )): table('SWA measurements '+str(i),models,'tab:swa-measured',row)
    add('SWA no reread',models,'Комплект 1.6.5 на',
        'только новую порцию: на GPU выполнены 18 таких вызовов Qwen, 18 Gemma и 12 Glimmer; на Mac выполнены 18 вызовов Gemma и 12 Glimmer')
    add('hetero abstract measured','90-appendix.tex','% checker-site: v4b-relocated-quality',
        'Разнородный пилот задач дал одинаковые счётчики правильных ответов во всех вариантах')
    add('hetero conclusion measured','14-conclusion.tex','Однородный пилот задач дал',
        'разнородный пилот сохранил счётчики правильных ответов при измеренных глубинах.')
    limits='11-limitations.tex'
    for i,row in enumerate((
        r'BF16, локальный контроль & 1.6e-7 & 1.000',
        r'Q4\_K\_M, локально & 0.0543 & 0.912',
        'Mirai, локально & 0.382 & 0.749',
        'Mirai, импорт & 0.385 / 0.387 / 0.387 & 0.750',
        'Bonsai, локально & 0.672 & 0.665',
        'Bonsai, импорт & 0.718 / 0.719 / 0.719 & 0.649',
    )): table('KL stage2 '+str(i),limits,'tab:kl-stage2',row)
    add('KL scope',limits,r'\textbf{Квантизация и распределения.}',
        'BF16 как эталон: 20 документов Gutenberg, 40\\,960 оцениваемых позиций, пакет оценки 32, seed 42.')
    add('hetero correct',limits,'В разнородном прогоне узел',
        '12, 11 и 9 правильных ответов из 15 на глубинах 8, 32 и 64 тысячи во всех четырёх вариантах.')
    add('hetero disagreements',limits,'В разнородном прогоне узел',
        'Относительно локального Q4 оффлоад изменил ответ в 1/1/1 случаях, другая локальная разбивка в 2/1/1, повтор одинаковой разбивки в 0/0/0.')
    add('hetero limit',limits,'В разнородном прогоне узел',
        'Глубина 128 тысяч в разнородном прогоне не измерялась.')
    server='06-server.tex';smoke='Точная общая версия прототипа'
    for name,phrase in (
        ('landed head',r'\texttt{9348ecd6} после PR \#16 повторно проверена на RTX PRO 6000:'),
        ('PRO timing','по восьми вызовам составило 1.571 секунды локально и 4.497 секунды при оффлоаде,'),
        ('PRO 8k','При 8 тысячах получены KL 0.0202 нат, top-1 61/64 и первое расхождение на восьмом токене;'),
        ('PRO 8k cause','На B300 при 8 тысячах измерен KL 0.0055 нат; причина различия между картами не установлена.'),
        ('PRO 32k','При 32 тысячах PRO 6000 даёт KL 0.0233 нат, top-1 60/64 и расхождение на девятом токене;'),
        ('PRO chunk chain','Дельта пришла пятью частями; добавочная цепочка с концами 7840, 31\\,360 и 32\\,144 дала те же числа.'),
        ('PRO calibration','Код выхода 5 сохраняет статус гетерогенной некалиброванной проверки.'),
    ): add(name,server,smoke,phrase)
    appendix='90-appendix.tex'
    add('landed PRs',appendix,'После сквозного запуска прототип',
        r'PR \#14 с атомарной вставкой частей и раскладкой скользящего окна, PR \#15 с ускорением импорта и PR \#16 с узлом vLLM включены в общую версию \texttt{9348ecd6}.')
    add('growing mechanism',appendix,r'\textbf{Растущая сессия.}',
        'клиент сохраняет старые строки KV, вставляет новый диапазон узла и заменяет рекуррентное состояние.')
    add('CHAIN-H exact',appendix,r'\textbf{Растущая сессия.}',
        'Повтор фактической цепочки импортов CHAIN-H побитово воспроизводит живой гибрид;')
    add('full refresh',appendix,r'\textbf{Растущая сессия.}',
        r'34\,816 байт на токен: $34\,816\times100\,000=3\,481\,600\,000$ байт, или 3.48~ГБ')
    add('growing gate',appendix,'Приёмка однородного прогона',
        'сравнения локального и гибридного вариантов по ответу требует top-1 не ниже 63/64.')
    add('growing report only',appendix,'Приёмка однородного прогона',
        'KL, первое расхождение свободной генерации и флаги отклонений публикуются без влияния на код выхода.')
    add('GPU rehearsal functional',appendix,'Приёмка однородного прогона',
        'Репетиция на одной PRO 6000 прошла 4/4 контрольные точки на CUDA; эта функциональная проверка относится только к CUDA и не измеряет сверку CUDA и Metal.')
    add('growing calibration pending',appendix,r'\pending{',
        r'\pending{калибровка гетерогенного допуска CUDA и Metal на M3 Max, включая сравнение с эталоном BF16.}')
    return result


def run16_expected():
    """R16 exports and transcribed current FACTS; finite timing/quality bounds.

    Authority: data/measurements/paper-v4-2026-11-03/FACTS.md plus R16 archived
    measurements. Capture residuals are independently derived from trace by
    the engine tests; the checker only binds the published rounded values.
    """
    result = {}
    def add(name, file, marker, wording):
        result['run16 ' + name] = (file, marker, wording)
    client = '05-clients.tex';channel = '04-channel.tex'
    add('background ancestry',client,r'\textbf{Условия измерений.}',
        r'LaunchAgent с \texttt{ProcessType=Background} запускал сервер tmux; дочерние процессы M3 Max работали при PRI~4.')
    add('paired priority limit',client,r'\textbf{Условия измерений.}',
        r'Парный запуск той же сборки \texttt{dde879bc} и модели при PRI~31 дал на 9--85\% больше токенов/с добавочного prefill и на 28--203\% больше при генерации.')
    add('kit refuses background',client,r'\textbf{Условия измерений.}',
        'Комплект 1.6.7 записывает приоритет процесса и предков и отказывается измерять в фоновом диапазоне.')
    add('partial PRI31 parallel',client,r'\textbf{Параллельная генерация.}',
        'При PRI~31 на 32 тысячах и 32 потоках получено 57.375 против 47.83 токена/с при PRI~4; на 64 тысячах и 32 потоках 37.862 против 35.56; на 128 тысячах и 16 потоках 18.705 против 20.22, на четырёх потоках при 16 слотах 18.77 против 14.35.')
    add('intermediate counts pending',client,r'\textbf{Параллельная генерация.}',
        r'Ограниченная сетка промежуточных потоков при обычном приоритете измерена отдельно (таблица~\ref{tab:m3-capped-decode}); прежние контрольные точки сохраняют свои условия.')
    # A visible qualification follows every interim capacity/coverage surface.
    for name,file,marker,phrase in (
        ('clients capacity',client,r'\caption{Условных сессий', '‡ M3: промежуточные оценки с многопоточными опорами PRI~4, ограниченный повтор при обычном приоритете измерен; обновление архивной модели ожидается.'),
        ('agents capacity',client,r'\label{tab:agents-day}', r'M3 Max\textsuperscript{‡}, промежуточные оценки по многопоточным опорам PRI~4; ограниченный повтор при обычном приоритете измерен; обновление архивной модели ожидается.'),
        ('gains interim',client,'Переход от одного к четырём,','‡ Эти отношения промежуточные, многопоточные опоры PRI~4; ограниченный повтор при обычном приоритете измерен; обновление архивной модели ожидается.'),
        ('economic capacity','91-calculation-history.tex',r'\caption{Гибрид на человека', '‡ M3: промежуточные многопоточные опоры PRI~4, повтор при PRI~31 ожидается.'),
        ('free prefill capacity','91-calculation-history.tex',r'\caption{Месячные доллары', '‡ M3: промежуточные многопоточные опоры PRI~4, повтор при PRI~31 ожидается.'),
        ('traffic capacity',channel,r'\textbf{Трафик как статья расходов.}', '‡ Следующие объёмы на день промежуточные: многопоточные опоры M3 сняты при PRI~4; ограниченный повтор при обычном приоритете измерен; обновление архивной модели ожидается.'),
        ('SWA background','05b-models.tex',r'\caption{Измерения комплекта','Ячейки M3 Gemma сняты при PRI~4, повтор при PRI~31 ожидается. M3 Glimmer снят при PRI~31, дельты последовательны; сохранение на внешний диск.'),
    ): add(name,file,marker,phrase)
    for name,marker in (('client table',r'\caption{Условных сессий'),('sweep table',r'\caption{Измеренная суммарная')):
        phrase = ('Архивная модель M5 использует прежние опоры без записи приоритета; новые измерения M5 при PRI~31 приведены отдельно.' if name=='client table'
                  else 'M5 1.6.7: PRI~31 записан вместе с предками процесса; принудительный обход не использован.')
        add('M5 priority '+name,client,marker,phrase)
    daily={r['client']:r for r in rows(ENGINE/'client_sessions_day.csv') if r['link_mbit']=='1000.0'}
    gain64=100*(float(daily['M5 Max 64 GB']['gain'])-1)
    gain128=100*(float(daily['M5 Max 128 GB']['gain'])-1)
    add('M5 gains prose',client,r'\textbf{Сколько успевает клиент за день.}',
        f'В архивной модели run 16 на гигабите M5 Max получает {min(gain64,gain128):.0f}--{max(gain64,gain128):.0f}'+r'\% к ёмкости дня,')
    add('M5 gains conclusion','91-calculation-history.tex','результата. Ожидание prefill',
        f'на M5 Max с 64~ГБ на {gain64:.0f}'+r'\%, на M5 Max с 128~ГБ по переносу измерений на '+f'{gain128:.0f}'+r'\%;')
    capacity=float(daily['M5 Max 64 GB']['hybrid_sessions_day'])*116
    fmt=lambda x:f'{round(x,-1):,.0f}'.replace(',',r'\,')
    add('autopilot capacity','11-limitations.tex','Расчёты исходят',
        'около '+fmt(3*capacity)+' вместо '+fmt(capacity)+'.')
    glm=next(r for r in rows(ENGINE/'glm_long_sessions.csv') if r['context']=='1000000')
    add('GLM cold local','91-calculation-history.tex',r'\textbf{Клиент для миллиона токенов.}',
        f'примерно за {float(glm["ingest_1m_local_s"])/60:.0f} минуты,')
    m5=rows(ENGINE/'m5_cooled_parallel.csv')
    for depth,label in ((32784,32),(65552,64),(131088,128)):
        data={int(r['streams']):r for r in m5 if int(r['depth'])==depth}
        cells=[f'{float(data[s]["aggregate_tok_s"]):.2f}' if s in data else '' for s in (1,2,4,6,8,12,16,24,32)]
        add('M5 sweep '+str(label),'91-calculation-history.tex',r'\label{tab:m5-sweep-history}',
            f'M5 Max, 1.6.6 & {label} & '+' & '.join(cells)+r' \\')
    add('growing timing arms',channel,r'\textbf{Измеренный запуск при 9.75~МБ/с.}',
        r'и M3 Max на Metal при PRI~31 прошли по 40 ходов от 100 тысяч до 143\,439 токенов через канал 9.75~МБ/с с RTT 140.6~мс.')
    add('outage resync',channel,r'\textbf{Измеренный запуск при 9.75~МБ/с.}',
        r'Обрыв на ходах 2--4 завершился синхронизацией: граница импорта 106\,849 лежит после глубины обрыва 103\,024.')
    add('decode PRI31',channel,r'\textbf{Измеренный запуск при 9.75~МБ/с.}',
        'Генерация в обоих вариантах составила 10.0--12.3 токена/с на глубинах 100--143 тысячи.')
    validation=[r for r in rows(ENGINE/'growing_5g_validation.csv') if r['import_variant']=='prototype_depth']
    for r,label in zip(validation,('База 100 тыс.','Ход 7','Ход 31')):
        cells=[f'{float(r[k]):.1f}' for k in ('measured_ttft_s','instrumentation_capture_s','measured_residual_s','measured_local_ttft_s')]
        add('instrumentation row '+r['turn'],channel,r'\label{tab:growing-link}',label+' & '+' & '.join(cells)+r' \\')
    add('residual limit',channel,r'\caption{Канал 9.75',
        'Остаток служит арифметической верхней оценкой и содержит хэширование свидетельств; производственный TTFT без этой инструментальной работы не измерен.')
    add('captures synchronous',channel,'Проверяющая программа синхронно',
        r'Проверяющая программа синхронно сохраняла снимки узла внутри TTFT (таблица~\ref{tab:growing-link}).')
    add('validation local turns',channel,r'\textbf{Прогноз для измеренного запуска.}',
        'ходов 7 и 31: 36.4 и 44.2 против 33.7 и 38.9.')
    add('validation ideal',channel,r'\textbf{Прогноз для измеренного запуска.}',
        'Идеальный оффлоад даёт 418.1, 30.0 и 31.2 секунды;')
    add('validation conditioned',channel,r'\textbf{Прогноз для измеренного запуска.}',
        '418.4, 33.2 и 35.0 против остатков 483.3, 43.1 и 35.3.')
    add('Mac checkpoint measured',channel,r'\textbf{Прогноз для измеренного запуска.}',
        r'повтор на глубине 109\,591 при PRI~31 дал на 64 позициях top-1 64/64, средний KL $7.7296\cdot10^{-5}$ нат, p95 $1.7031\cdot10^{-4}$ и максимальную абсолютную разность логитов 0.2097.')
    add('Mac recheck uncalibrated',channel,r'\textbf{Прогноз для измеренного запуска.}',
        r'Код выхода 5 сохраняет гетерогенный статус; калиброванной приёмки нет.')
    add('import model','90-appendix.tex','Клиентское время вставки включено',
        r'$t_{\mathrm{ins}}(d,L)=0.2591+48.7\cdot10^{-6}d+34.64\cdot10^{-6}L$ секунд.')
    add('import cause','90-appendix.tex','Клиентское время вставки включено',
        r'Полное сохранение старого слота перед последней вставкой даёт 94.2\% наклона в CPU-диагностике.')
    add('bounded undo future','90-appendix.tex','Клиентское время вставки включено',
        'только в чувствительности: реализация, транзакционная проверка и проверка потери подтверждения относятся к будущей работе.')
    add('link thresholds',channel,'Для прежней базовой конфигурации',
        'порог 8.05~МБ/с с состоянием f32 и 7.20~МБ/с при ограниченном откате; для bf16 пороги равны 5.40 и 4.83~МБ/с.')
    add('preflight 9.75 MB/s',channel,r'\textbf{Порог канала.}',
        'при 9.75~МБ/с и RTT 140.6~мс политика выбрала ходы 7 и 31.')
    quality='11-limitations.tex';marker=r'\textbf{Пилот задач.}'
    add('RULER score',quality,marker,r'Оценка RULER равна 97.01\% во всех трёх вариантах; расхождений оценок отдельных примеров 0 из 390.')
    add('RULER CUDA design',quality,marker,
        r'оффлоад с prefill на узле по собственной разбивке и импортом состояния на клиент, где ответ генерируется локально; локальный вариант использует batch и ubatch 64, другая локальная разбивка 256.')
    add('RULER text changes',quality,marker,r'в 34/390 случаях (8.72\%) при оффлоаде и 32/390 (8.21\%) при другой разбивке.')
    add('RULER paired interval',quality,marker,r'Точный тест Макнемара даёт $p=0.727$, 95\%-й интервал избытка изменений при оффлоаде над другой разбивкой составляет от $-2.13$ до $+3.12$ п.п.')
    add('RULER deeper pending',quality,r'\textbf{Первичный анализ RULER.}',r'Глубины Qwen 64 и 128 тысяч: \pending{полные 390 пар и первичный анализ на 64 и 128 тысячах; узлы остановлены по решению владельца 2026-11-04, строки сохранены до остановки; исходные узлы поставлены в очередь на перезапуск. Граница приёма данных 2026-11-05 12:00 UTC.}')
    return result

def rc3_amendment_expected():
    """Owner's session framing and source-transcribed EXO single-request scope."""
    return {
        'rc3 prior art': ('01-introduction.tex', r'\textbf{Место работы.}',
            r'Разделение prefill и decode между машинами уже используют DistServe, Splitwise и Mooncake в дата-центрах \cite{zhong2024distserve,patel2023splitwise,qin2024mooncake}.'),
        'rc3 audit limits': ('01-introduction.tex', 'Модель угроз открыта;',
            'Модель угроз открыта; покрытие атак и межплатформенный допуск не измерены.'),
        'rc3 session protocol': ('01-introduction.tex', 'Схема задаёт протокол',
            'Вверх идут только идентификаторы токенов, вниз идут KV новых позиций и рекуррентное состояние линейных слоёв (вместе, память модели). Журнал токенов, догоняющий prefill и повторная синхронизация восстанавливают согласованный префикс.'),
        'rc3 EXO streaming': ('01-introduction.tex', r'\textbf{Место работы.}',
            'EXO Labs выполняет prefill на DGX Spark, decode на Mac Studio M3 Ultra и передаёт KV послойно во время prefill по каналу с заявленной полосой 10~Гбит/с;'),
        'rc3 EXO benchmark': ('01-introduction.tex', r'\textbf{Место работы.}',
            r'в опубликованном опыте одного запроса Llama-3.1 8B FP16 с промптом в 8\,192 токена и ответом в 32 токена ускорение относительно одного M3 Ultra составляет 2.8 раза \cite{exolabsSpark}.'),
        'rc3 verifiability': ('01-introduction.tex', 'представлениями между моделями',
            'Клиент может пересчитать выбранные дельты самостоятельно и сверить полученное состояние; облачная генерация без выдачи состояния такого аудита клиенту не даёт.'),
        'rc3 economics scope': ('01-introduction.tex', 'представлениями между моделями',
            'На реальном профиле из 1.5 миллиона вызовов оцениваем стоимость локальной генерации и удалённого prefill; основную статью расходов у медианного API составляет чтение кэша. Профиль относится к одному пользователю.'),
    }


def rc3_review2_expected():
    """Transcribed primary-source claims and bounded summaries, not new measurements.

    Source record: r19 delivery/sources/verification.md (CacheGen sec. 5.2,
    abstracts of Marconi/EdgeShard/PicoSpec, authorized-KV sec. 5.6,
    agent-memory sec. 3.2; LMCache legacy and MP pages). Link-policy figures
    come from the owner's FACTS, 5.19 MB/s preflight, not the engine snapshot.
    """
    result = {}
    def add(name, file, marker, wording):
        result['rc3 review2 ' + name] = (file, marker, wording)
    related = '12-related.tex'
    marker = '% checker-site: rc3-review2-compression'
    add('adaptive bitstream', related, marker,
        r'CacheGen (SIGCOMM 2024) кодирует KV-кэш в компактный битовый поток и подбирает степень сжатия к доступной полосе \cite{liu2024cachegen};')
    add('LMCache mode limit', related, marker,
        r'LMCache документирует CacheGen в прежнем внутрипроцессном режиме, для многопроцессного режима CacheGen ещё не реализован \cite{lmcacheCachegen}.')
    add('wire formats', related, marker,
        r'В нашем прототипе KV-дельта уже передаётся в q8\_0 с вращением Адамара, рекуррентное состояние в f32.')
    add('fixed recurrent cost', related, marker,
        'У Qwen3.8-27B около 157~МБ состояния составляют фиксированную часть передачи и определяют задержку малых дельт на медленном канале.')
    add('5.19 MB/s all local', related, marker,
        'На канале 5.19~МБ/с с RTT 125.8~мс политика оставила все 37 подключённых ходов локальными; предварительный запуск был отклонён без оффлоадов.')
    add('first offload threshold', related, marker,
        'Для первого оффлоада, хода 7, при тех же RTT и аппроксимации вставки нужно около 8.45~МБ/с.')
    add('preflight limit', related, marker,
        r'Это расчёт прежней политики по измеренной связи; растущая сессия через канал 9.75~МБ/с с RTT 140.6~мс измерена отдельно, сверка M3 Max дала top-1 64/64 и средний KL $7.7296\cdot10^{-5}$ нат; межплатформенный допуск требует калибровки.')
    add('compression future work', related, marker,
        'Репетиция bf16 на CUDA измерена при фиксированных журнале и границах f32; качество и скорость на Mac и энтропийное кодирование по примеру CacheGen остаются будущей работой; движок рассчитывает пороги bf16 при неизменных коэффициентах вставки.')
    add('Marconi recurrent prefix', related, '% checker-site: rc3-review2-prefix',
        r'Marconi (MLSys 2025) рассматривает кэширование префиксов гибридных моделей: обновление рекуррентного состояния на месте не позволяет откатить запись к частично совпавшему префиксу, поэтому попадание требует точного совпадения \cite{pan2025marconi}.')
    add('journal relation', related, '% checker-site: rc3-review2-prefix',
        'С тем же ограничением связаны наш журнал токенов и контрольные точки: они задают восстановление нужного согласованного префикса.')
    add('device cloud', related, '% checker-site: rc3-review2-prefix',
        r'Совместный инференс устройства и облака изучают EdgeShard с разбиением модели между устройствами \cite{zhang2024edgeshard}, PicoSpec со спекулятивной генерацией \cite{zhang2026picospec} и работа с разрешением клиента на использование KV-кэша \cite{li2026authorizedkv}.')
    add('agent persistence', '10-resilience.tex', 'Локальное хранение памяти агента',
        r'Agent Memory Below the Prompt сохраняет KV-кэш каждого агента на диске в 4-битном формате и загружает при возобновлении \cite{shkolnikov2026agentmemory}.')
    abstract = '00-abstract.tex'
    add('abstract CUDA identity', '90-appendix.tex', 'Прототип на llama.cpp',
        'При одинаковой разбивке prefill на пакеты перенос дельты на CUDA даёт побитовое совпадение с локальным расчётом')
    add('abstract KL scope', '90-appendix.tex', '% checker-site: v4b-relocated-quality',
        'В исследовании KL расхождение задают собственные веса клиента; точность узла Q4, Q8 или BF16 не даёт измеримого различия для импортированного состояния.')
    add('abstract task bound', '90-appendix.tex', '% checker-site: v4b-relocated-quality',
        'В пилотах оффлоад меняет ответы не чаще другой разбивки prefill: 48 случаев в однородном прогоне, по 15 на глубину в разнородном.')
    add('abstract paired plan', abstract, 'Протокол ведёт',
        'Граница выбрана после результатов; эквивалентность текста на этой выборке не установлена.')
    limits = '11-limitations.tex'
    add('limitations CUDA identity', limits, 'Qwen3.8-27B и GLM-5.3-Flash',
        'Измеренная эквивалентность состояния ограничена условиями опыта: перенос дельты Qwen3.8-27B на CUDA при одинаковой разбивке prefill даёт побитовое совпадение.')
    add('limitations KL scope', limits, r'\textbf{Квантизация и распределения.}',
        'В измеренных вариантах расхождение задают собственные веса клиента. Смена точности узла не даёт измеримого различия для импортированного состояния:')
    add('limitations task bound', limits, r'\textbf{Пилот задач.}',
        'В этих пилотах оффлоад меняет ответы не чаще другой разбивки prefill. Выборки малы: 48 случаев в однородном прогоне, по 15 на глубину в разнородном; тест эквивалентности не заявлен.')
    add('limitations paired plan', limits, r'\textbf{Пилот задач.}',
        r'Эквивалентность текста при границе 2 п.п. на этой выборке не установлена.')
    # Cells are registered independently, so a valid prose paragraph cannot
    # compensate for an incorrect table entry.
    for name, wording in (
        ('compression cells', r'Сжатие состояния & Битовый поток KV; CacheGen адаптирует сжатие к полосе & Кодирование передачи НО & KV в 4 битах на диске & KV q8\_0 с вращением Адамара; состояние f32; bf16 проверен на CPU с потерями; кодирование в плане \\'),
        ('reuse cells', r'Повторное использование & Повторная загрузка KV & Точное совпадение рекуррентного префикса; отбор записей & Загрузка отдельного KV агента с диска & Журнал и контрольные точки согласованного префикса \\'),
        ('storage cells', r'Место хранения & Загружаемый KV; у LMCache прежний внутрипроцессный режим & Кэш префиксов гибридной модели & Диск устройства, Q4 & Клиент и копия у поставщика; политика хранения рассчитана моделью \\'),
    ):
        add(name, related, r'\label{tab:cache-mechanisms}', wording)
    return result


def v4b_expected():
    """Owner r20b: current source qualifications and explicit arithmetic.

    Light-load statements use selected, admissible run16 rows for the already
    owned M5 Max 64 GB, separately in both retention policies. No other client,
    profile or unselected fleet can supply a printed amount or direction.
    """
    out = {}
    def add(name, file, marker, wording):
        out['v4b '+name] = (file, marker, wording)
    abstract='00-abstract.tex';intro='01-introduction.tex';conclusion='14-conclusion.tex'
    add('abstract link',abstract,'Протокол ведёт',
        'При 5.19~МБ/с и RTT 125.8~мс политика оставила все ходы локальными; для 2343 токенов на глубине 100 тысяч с f32 расчётный порог 7.905~МБ/с.')
    add('abstract RULER','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Парная RULER на глубине 8 тысяч проверила 13 задач по 30 примеров, всего 390, с seed 261102.')
    add('abstract growing',abstract,'Протокол ведёт',
        r'В растущей сессии CUDA и Metal оба варианта прошли 40 ходов до 143\,439 токенов при 9.75~МБ/с и RTT 140.6~мс; M3 Max генерировал 10.0--12.3 токена/с.')
    add('introduction economics','91-calculation-history.tex','% checker-site: v5a-old-introduction-economics',
        r'При доле открытой модели 20\% гибрид на уже купленной машине Max или Ultra в 1.2--1.5 раза дешевле медианного поставщика API той же модели и в 4.8--6.0 раза дороже самого дешёвого; диапазоны учитывают клиента и политику хранения.')
    add('conclusion novelty',conclusion,'Догоняющая синхронизация,',
        'Наш вклад объединяет интернет-канал с генерацией на клиенте, две растущие копии сессии с журналом и повторной синхронизацией и клиентский аудит состояния.')
    channel='04-channel.tex'
    add('first call accounting',channel,r'\textbf{Первый сквозной вызов при 16.0~МБ/с.}',
        r'Время до первого токена гибрида: $201.655=10.643+123.219+42.423+25.370$ секунды;')
    add('first call unattributed',channel,r'\textbf{Первый сквозной вызов при 16.0~МБ/с.}',
        'За пределами этих трёх компонентов 25.370 секунды: 19.659 внутри подготовки запросов к узлу и 5.711 на клиенте вне подготовки запросов.')
    add('first call historical priority',channel,r'\textbf{Первый сквозной вызов при 16.0~МБ/с.}',
        r'использовал CUDA-сервер в Великобритании, M3 Max на Metal при PRI~4 через канал 16.0~МБ/с с RTT 110~мс.')
    measured={r['component']:r for r in rows(ENGINE/'e2e_first_call_check.csv')}
    add('first call prediction',channel,r'\textbf{Прогноз первого вызова.}',
        f'{float(measured["total"]["predicted_s"]):.1f} секунды против измеренных 201.7: сервер 11.7 против 10.6, передача 125.4 против 123.2, вставка 2.2 против 42.4 секунды. Локальная оценка равна 241.1 секунды против 271.5.')
    add('limitations link','11-limitations.tex',r'\textbf{Граница канала.}',
        'На канале 5.19~МБ/с с RTT 125.8~мс политика оставила все ходы локальными. Для порции 2343 токена при глубине 100 тысяч расчётный порог с состоянием f32 равен 7.905~МБ/с;')
    fixed=1024*435200
    add('Gemma fixed geometry','05b-models.tex',r'\textbf{Gemma 4 и канал.}',
        r'окно в 1024 позиции по 435\,200 байт занимает $1024\times435200='+str(fixed)+r'$ байт, около '+f'{fixed/1e6:.1f}'+r'~МБ на каждый оффлоад.')
    add('Gemma full KV','05b-models.tex',r'\textbf{Gemma 4 и канал.}',
        r'KV слоёв полного внимания Gemma занимает ещё 43\,520 байт на новый токен.')
    add('Gemma link scope','05b-models.tex',r'\textbf{Gemma 4 и канал.}',
        'Фиксированная часть Gemma больше, но локальный prefill Gemma на Mac медленнее.')
    costs=[]
    for suffix in ('','_conservative'):
        selected={}
        for team in (5,10,20,50,500,5000):
            for route in ('all server','hybrid'):
                rr=[r for r in rows(ENGINE/('perimeter_cost_light'+suffix+'.csv'))
                    if r['team']==str(team) and r['profile']=='light' and r['selected']=='1' and r['route']==route
                    and (route=='all server' or (r['client']=='M5 Max 64 GB' and r['basis']=='Mac already owned'))]
                assert len(rr)==1 and rr[0]['eligible']=='1',('light-load selected row',suffix,team,route)
                selected[team,route]=float(rr[0]['person_month'])
        costs.append(selected)
    saving=lambda data,team:100*(1-data[team,'hybrid']/data[team,'all server'])
    conclusion='91-calculation-history.tex'
    marker='% checker-site: v5a-R16-conclusion'
    for team in (5,10,20):
        amounts=[saving(data,team) for data in costs]
        assert amounts[0]==amounts[1] and amounts[0]<0,('small-team light direction',team,amounts)
        wording=f'на {-amounts[0]:.1f}'+r'\% для '+str(team)
        if team==5:wording='дороже своего кластера '+wording+' человек'
        if team==20:wording+=' при обеих политиках хранения;'
        add('light team '+str(team),conclusion,marker,wording)
    for team in (50,500,5000):
        base,cautious=[saving(data,team) for data in costs]
        assert base>0 and cautious>0,('large-team light direction',team)
        wording=f'для {team} '+('человек гибрид ' if team==50 else '')+f'дешевле на {base:.1f}'+r'\% '+('по политике протокола ' if team==50 else '')+f'и на {cautious:.1f}'+r'\%'
        if team!=50:wording=wording.replace('и на ','и ')
        if team==50:wording+=' при осторожной,'
        add('light team '+str(team),conclusion,marker,wording)
    segments=rows(ENGINE/'client_prefill_segments.csv')
    m3=[float(r['prefill_tok_s']) for r in segments if r['client']=='M3 Max']
    m5=[float(r['prefill_tok_s']) for r in segments if r['client']=='M5 Max']
    pairs=list(zip(m3,m5));low=min(pairs,key=lambda p:p[1]/p[0]);high=max(pairs,key=lambda p:p[1]/p[0])
    add('restored prefill ratio','05-clients.tex',r'\textbf{Сколько успевает клиент за день.}',
        f'между ${low[1]:.1f}/{low[0]:.1f}={low[1]/low[0]:.2f}$ и ${high[1]:.1f}/{high[0]:.1f}={high[1]/high[0]:.2f}$;')
    distribution=json.loads((HERE.parents[1]/'data/measurements/paper-v4b-2026-11-03/derived-prefill.json').read_text())
    add('restored distribution','02-workload.tex','На глубине 150 тысяч порция',
        f'На всём профиле чтение на M3 Max занимает в среднем {distribution["mean"]:.1f} секунды на вызов; медиана {distribution["median"]:.1f} секунды, p90 {distribution["p90"]:.1f} секунды.')
    return out


ENGINE17 = HERE / 'engine17'
SOURCE_V4C = HERE.parents[1] / 'data/measurements/paper-v4c-2026-11-03'


def selected17(kind, file, **filters):
    data = rows(HERE.parents[1]/'calc/out/run17'/kind/file)
    found=[r for r in data if all(r[key]==value for key,value in filters.items())]
    assert len(found)==1,('run17 selected row',kind,file,filters,len(found))
    return found[0]


def v4c_expected():
    """R17 measured-rate thresholds, shown geometry, and traced accounting.

    R16 diagnostics and operation-scaled timing estimates retain their named
    scope; R17 adds the measured PRO6000 curve and exact live-window payload.
    Accounting is enclosing-span attribution, not a timing-only counterfactual.
    """
    out={}
    def add(name,file,marker,wording):out['run17 '+name]=(file,marker,wording)
    channel='04-channel.tex';models='05b-models.tex'
    data=rows(ENGINE17/'architecture_link_threshold.csv')
    for model,label,state in (('qwen27','Qwen','f32'),('qwen27','Qwen','bf16'),('glimmer30',r'Glimmer\textsuperscript{†}','f32'),('gemma31',r'Gemma\textsuperscript{†}','f32')):
        for depth in (32000,64000,100000):
            chosen={int(r['delta']):r for r in data if r['model']==model and r['state_format']==state and int(r['depth'])==depth}
            assert set(chosen)=={512,2343,10000}
            interim=model!='qwen27'
            assert all((r['background_priority_interim']=='True')==interim for r in chosen.values())
            if interim:assert all(r['import_assumption']=='r16_qwen_token_depth_portability: same conditional intercept; 48.7us per transferred full-KV token and prefix-depth slope; estimated for SWA; not measured; window bytes affect wire only' for r in chosen.values())
            phrase=f'{label} & {state} & {depth//1000} & '+' & '.join(f'{float(chosen[d]["break_even_downstream_mb_s"]):.3f}' for d in (512,2343,10000))+r' \\'
            add(f'threshold {model}/{state}/{depth}',channel,r'\label{tab:model-link}',phrase)
    add('SWA qualification',channel,r'\caption{Минимальная полезная',
        r'Строки Glimmer и Gemma\textsuperscript{†} промежуточные: скорости Mac сняты при PRI~4; новые опоры Glimmer при PRI~31 ожидают обновления движка, повтор Gemma в очереди; вставка задана именованной оценкой переноса закона Qwen, без собственной калибровки скользящего окна.')
    add('SWA import limit',channel,'Перенос закона вставки Qwen',
        'Собственного замера вставки Glimmer или Gemma нет, и большой объём окна Gemma может добавить работу вставки.')
    add('Gemma 100k',models,r'\textbf{Gemma 4 и канал.}',
        'При глубине 100 тысяч и порции 2343 токена порог Gemma равен 6.588~МБ/с против 7.905 у Qwen;')
    add('Gemma 32k64k',models,r'\textbf{Gemma 4 и канал.}',
        'при 32 тысячах 21.851 против 17.606, при 64 тысячах 10.984 против 12.342.')
    add('Gemma comparison qualification',models,r'\textbf{Gemma 4 и канал.}',
        r'Все три сравнения промежуточные: скорости Glimmer и Gemma на Mac сняты при PRI~4; новые опоры Glimmer при PRI~31 ожидают обновления движка, повтор Gemma в очереди. Вставка скользящего окна задана именованной оценкой переноса закона Qwen, без собственной калибровки Glimmer или Gemma.')
    extra=rows(ENGINE17/'architecture_extrapolation.csv')
    for fixed in ('0','10','50','78.5','157'):
        selected={int(r['kv_kib_token']):r for r in extra if r['fixed_mb']==fixed}
        phrase=fixed+' & '+' & '.join(f'{float(selected[k]["break_even_downstream_mb_s"]):.3f}' for k in (2,7,34))+r' \\'
        add('extrapolation S='+fixed,channel,r'\label{tab:architecture-extrapolation}',phrase)
    add('extrapolation limit',channel,r'\textbf{Экстраполяция устройства модели.}',
        'эта экстраполяция не описывает измеренную модель и не утверждает, что другая архитектура сохраняет скорости или качество Qwen.')
    add('extrapolation caption',channel,r'\caption{Экстраполяция при фиксированных',
        r'Значения 78.5 и 157 округлены для сетки; точное состояние Qwen составляет 78.446592 или 156.893184~МБ. Таблица не является утверждением о реальной модели.')
    add('hypothetical bytes example',models,'Например, при кэше новых токенов',
        r'$78.446592+1000\cdot6144/10^6=84.590592$~МБ вместо примерно 192~МБ с f32 и исходным KV.')
    add('hypothetical time example',models,'Например, при кэше новых токенов',
        r'$18.6069-84.590592/12.5=11.8$ секунды вместо 3.3 в исходной геометрии.')
    add('whole window',models,r'\textbf{Вес дельты.}',
        r'После заполнения окна Glimmer передаёт $7072\Delta+43450368$ байт, Gemma $43520\Delta+445644800$ байт; обрамление протокола не включено.')
    add('whole window example',models,r'\textbf{Вес дельты.}',
        r'Для тысячи новых токенов это 50\,522\,368 байт у Glimmer, около 50.5~МБ, и 489\,164\,800 байт у Gemma, около 489.2~МБ.')
    arch=rows(HERE/'arch-compare.csv')
    for label,key,precision in (('Дельта на 1000 токенов, МБ','delta_1k_mb',0),('Передача при 300 Мбит/с, с','transfer_1k_300mbit_s',1)):
        phrase=label+' & '+' & '.join(f'{float(r[key]):.{precision}f}' for r in arch)+r' \\'
        add('operation sensitivity '+key,models,r'\label{tab:arch}',phrase)
    for link in (100,300,1000):
        label='1 Гбит/с' if link==1000 else str(link)+' Мбит/с'
        phrase='Экономия на вызове при '+label+', с & '+' & '.join('0' if float(r[f'saving_1k_131k_{link}mbit_s'])<0 else f'{float(r[f"saving_1k_131k_{link}mbit_s"]):.1f}' for r in arch)+r' \\'
        add('operation sensitivity saving '+str(link),models,r'\label{tab:arch}',phrase)
    add('operation sensitivity limit',models,r'\caption{Дельта и чтение порции',
        'Скорости Glimmer и Gemma здесь получены переносом эффективности Qwen по операциям; это оценка, без собственной калибровки этих моделей. Передаётся всё живое окно.')
    marker=r'\textbf{Учёт времени растущей сессии.}'
    add('base import total',channel,marker,'Вставка базы 2.908 секунды включает все десять запросов:')
    add('base import arithmetic',channel,marker,r'По неокруглённым полям $2.508157+0.399364=2.907521$ секунды; заключительная вставка уже включена в сумму.')
    add('base gap',channel,marker,'После вычитания снимков, prefill, передачи и всех вставок у базы остаётся 41.168 секунды, из них 40.165 внутри десяти запросов расширения состояния на узле.')
    add('node full save',channel,marker,'В запросы входят загрузка полного состояния до prefill, сохранение после экспорта и контрольные суммы.')
    add('hashing remains',channel,marker,'Те же запросы синхронно хэшируют 25.748~ГБ файлов свидетельств: снимки и дельты. Таймер загрузки снимков не включает это хэширование, поэтому вычитание снимков хэширование не устраняет.')
    add('arithmetic upper bound',channel,marker,'Остаток после вычитания загрузки снимков служит арифметической верхней оценкой, содержащей инструментальное хэширование; производственный TTFT этим вычитанием не измерен.')
    add('timing-only pending',channel,marker,r'\pending{замеры времени без снимков и хэширования свидетельств, с отдельными интервалами этапов на Mac и узле.}')
    account=json.loads((SOURCE_V4C/'time-accounting-arithmetic.json').read_text())
    for r,label in zip(account['growing'],('База','Ход 7','Ход 31')):
        phrase=label+' & '+' & '.join(f'{r[k]:.3f}' for k in ('unattributed','inside_extend_gap'))+' & '+f'{r["hash_bytes"]/1e9:.3f}'+r' \\'
        add('accounting row '+str(r['turn']),channel,r'\label{tab:time-accounting}',phrase)
    add('first request unknown split',channel,r'\textbf{Первый сквозной вызов при 16.0~МБ/с.}',
        'Интервал 19.659 секунды включает отправку, ожидание первого байта, загрузку состояния на узле, экспорт, сохранение и контрольные суммы; отдельные времена этих операций не записаны.')
    add('turn31 cursor not critical',channel,'Для хода 7 два критических',
        'У хода 31 критическая синхронизация занимает 0.312 секунды; сводные 3.812 секунды догоняющего вычисления относятся к более раннему интервалу журнала и не прибавляются к TTFT.')
    marker=r'\textbf{Передача состояния в bf16.}'
    add('bf16 tensor bytes',channel,marker,r'Рекуррентные тензоры Qwen сокращаются с 156\,893\,184 до 78\,446\,592 байт; каждый идеальный оффлоад экономит 78\,446\,592 байта. Кэш полного внимания не меняется.')
    add('bf16 CPU loss',channel,marker,'Передача реализована и проверена на CPU. bf16 округляет состояние; точные контроли классифицируют перенос bf16 как передачу с потерями даже при совпадении ответов.')
    add('bf16 rounding',channel,marker,r'На реальном состоянии Qwen3.5-0.8B после 16 токенов максимальная относительная ошибка округления проверенных нормальных значений равна 0.00389, меньше $2^{-8}=0.00390625$.')
    add('bf16 pending',channel,marker,r'\pending{запуск Mac для качества и скорости передачи bf16.}')
    add('bf16 resident unchanged',channel,marker,'В модели резидентное состояние, генерация, миграция хранения и коэффициенты вставки сохраняются; вдвое уменьшаются только рекуррентные тензоры на проводе.')
    add('bf16 transfer estimate',channel,marker,'При порции 2343 токена передача без RTT и вставки меняется с 24.458 до 16.412 секунды на канале 9.75~МБ/с, с 45.947 до 30.832 секунды на 5.19~МБ/с.')
    client='M3 Max 128 GB (measured)'
    pairs={kind:{'day':selected17(kind,'client_sessions_day.csv',client=client,link_mbit='1000.0'), 'traffic':selected17(kind,'traffic_user_month.csv',client=client,profile='heavy'), 'cost':selected17(kind,'person_cost_s20.csv',client=client,team='5',basis='Mac already owned')} for kind in ('f32','bf16')}
    fields=[('Локальных сессий в день','day','local_sessions_day'),('Гибридных сессий в день','day','hybrid_sessions_day'),('Отношение ёмкости дня','day','gain'),('Ёмкость вызовов в день / обслужено в тяжёлом профиле','traffic','served_day'),('Трафик, ТБ в месяц','traffic','hybrid_tb_month'),('Трафик по тарифу \\$50/ТБ, долларов','traffic','egress_2'),('Доля оффлоадов','cost','offload_share'),('Трафик по базовому тарифу, долларов','cost','egress_month'),('Хранение и миграция, долларов','cost','hosting_month'),('Гибрид всего, долларов','cost','hybrid_cheapest')]
    for label,table,key in fields:
        phrase=label+' & '+' & '.join(f'{float(pairs[kind][table][key]):.6f}' for kind in ('f32','bf16'))+r' \\'
        add('bf16 economics '+key,'91-calculation-history.tex',r'\label{tab:bf16-economics}',phrase)
    add('bf16 economics caveat','91-calculation-history.tex',r'\caption{Чувствительность экономики',
        r'Все значения промежуточные: многопоточные опоры M3 сняты при PRI~4; повтор при PRI~31 ожидается.')
    return out



def v5a_expected():
    """Owner v5a: current accepted measurements, explicit estimates and review fixes."""
    out={}
    def add(name,file,marker,phrase):out['v5a '+name]=(file,marker,phrase)
    thesis='При decode каждая сессия на каждом токене читает собственный KV-кэш и рекуррентное состояние.'
    for file in ('01-introduction.tex','14-conclusion.tex'):
        add('division '+file,file,'Разделение труда между общим сервером',thesis)
    add('abstract division','00-abstract.tex',r'\textbf{Аннотация.}','Предлагаем разделение труда: общий сервер выполняет prefill, машина пользователя генерирует по собственному контексту.')
    add('abstract measured modelled','00-abstract.tex','Протокол ведёт','На одной GPU при 512 тысячах и 1.04 миллиона f32-оффлоад точно совпал с локальным по логитам в пяти случаях.')
    add('limitations residual semantics','90-appendix.tex',r'\textbf{Условия растущего запуска.}','вычитание загрузок снимков сохраняет хэширование и даёт арифметическую верхнюю оценку; производственное время без инструментирования не измерено.')
    add('monthly price noun','91-calculation-history.tex',r'При доле 20\% пользователь',r'Эта месячная цена в 4.8--5.2 раза дороже')
    add('normal decode headroom','05-clients.tex',r'\textbf{Измеренные клиенты.}',r'$14.99(18.9739+0.5571+0.1569)/400=0.738$, около 73.8\% границы полосы.')
    source=HERE.parents[1]/'data/measurements/paper-v5a-2026-11-03'
    for row in rows(source/'consumer-gpu.csv'):
        phrase=' & '.join([row['model'],str(int(row['depth'])//1000)]+[row[k] for k in ('segment','delta512','delta2000','delta10000','decode')])+r' \\'
        add('consumer '+row['card']+' '+row['model']+' '+row['depth'],'05-clients.tex',r'\label{tab:client-'+row['card']+'}',phrase)
    add('consumer capacity','05-clients.tex',r'\textbf{Потребительские GPU как клиенты.}',r'На 5090 один слот Qwen вмещает 262\,144 токена, на 3090 99\,328 токенов: лестница Qwen у 3090 заканчивается на 86 тысячах.')
    add('consumer only','05-clients.tex',r'\textbf{Потребительские GPU как клиенты.}','RTX 5090 рассматривается только как клиент; серверный вариант в модель статьи не входит.')
    add('consumer normal','05-clients.tex',r'\textbf{Потребительские GPU как клиенты.}',r'при нормальном приоритете.')
    # Parallel rows are independently frozen in the source-bound site inventory below.
    for name in ('consumer parallel','ruler detail','vendor request','fidelity detail'):
        for i,site in enumerate(json.loads((HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05/extra-sites.json').read_text()).get(name,[])):
            add(name+' '+str(i),site['file'],site['marker'],site['phrase'])
    add('cache snapshot','07-economics.tex',r'\textbf{Пример тарифа одного поставщика.}',r'в точке условного кэша 98.1\% даёт минимум у Chutes: вход \$0.039, выход \$1.25, чтение кэша \$0.0039 за миллион токенов, контекст 262\,144.')
    add('cache precision','07-economics.tex',r'\textbf{Пример тарифа одного поставщика.}',r'Совпадают идентификатор и семейство модели; поставщик заявляет веса FP8, клиент гибрида использует Q4\_K\_M, сервер vLLM FP8.')
    add('cache own arms','07-economics.tex',r'\textbf{Пример тарифа одного поставщика.}','Сравнения качества в статье относятся к собственным вариантам гибрида; сравнения качества с API не проводились.')
    add('cache admission','07-economics.tex',r'\textbf{Пример тарифа одного поставщика.}',r'Допуск исключает только недостаточный контекст, отсутствие заявленного кэширования и доступность ниже 95\% в общем выбранном окне.')
    add('cache owner aggregate','07-economics.tex',r'\caption{Цена миллиона',r'98.1\% взято из коммерческого агрегата владельца по нескольким API; это сценарий, без измеренного попадания у Chutes.')
    add('cache arithmetic','07-economics.tex','При доле $h$',r'$0.019\cdot0.039+0.981\cdot0.0039=0.0045669$ доллара за миллион токенов.')
    add('cache no reuse','07-economics.tex',r'\label{tab:cache-price}',r'Без повторного использования & 0\% & 0.039 \\')
    add('cache measured wait','07-economics.tex',r'\label{tab:cache-price}',r'Измерение Chutes & не измерено & не определена \\')
    for i,(model,fmt,depth,delta) in enumerate([('qwen27','f32',100000,512),('qwen27','f32',100000,2343),('qwen27','f32',100000,10000),('qwen27','bf16',100000,2343),('qwen27','f32',32000,2343),('qwen27','f32',64000,2343),('glimmer30','f32',100000,2343),('gemma31','f32',100000,2343)]):
        rr=[r for r in rows(ENGINE17/'architecture_link_threshold.csv') if (r['model'],r['state_format'],int(r['depth']),int(r['delta']))==(model,fmt,depth,delta)];assert len(rr)==1
        label={'qwen27':'Qwen '+fmt,'glimmer30':r'Glimmer\textsuperscript{†}','gemma31':r'Gemma\textsuperscript{†}'}[model]
        phrase=f'{label} & {depth} & {delta} & {float(rr[0]["break_even_downstream_mb_s"]):.3f} & выше порога'+r' \\'
        add('when pays '+str(i),'07-economics.tex',r'\label{tab:when-pays}',phrase)
    add('when pays interim','07-economics.tex',r'\caption{Условия окупаемости',r'Glimmer и Gemma\textsuperscript{†} промежуточные: Mac при PRI~4; новые опоры Glimmer при PRI~31 ожидают обновления движка, повтор Gemma в очереди; стоимость вставки задана именованной оценкой переноса закона Qwen, без собственной калибровки окна.')
    add('when pays policy','07-economics.tex','Таблица~\\ref{tab:when-pays}', 'Равенство порогу даёт равное время; выше порога перенос быстрее локального prefill.')
    add('YaRN','08-million.tex','Для Qwen за пределами',r'статический YaRN из карточки модели: коэффициент 4, исходное окно 262\,144.')
    add('API context unknown','08-million.tex','Для Qwen за пределами','Способ расширения контекста у поставщиков API неизвестен;')
    ratio=json.loads((source/'prefill-ratios.json').read_text())
    add('prefill profile ratios','06-server.tex',r'\textbf{Деление работы и глубина.}', 'При глубинах 131, 164 и 181 тысяча расчёт даёт отношения '+'/'.join(f'{r["ratio"]:.2f}' for r in ratio['rows'])+'.')
    add('prefill ratio limit','06-server.tex',r'\textbf{Деление работы и глубина.}','промежуточные отношения рассчитаны, отдельными замерами не являются.')
    add('prefill 14x','06-server.tex',r'\textbf{Деление работы и глубина.}',r'$23151/1663=13.92$, около 14 раз.')
    add('link check first','04-channel.tex',r'\textbf{Повторная проверка связи.}', 'на первом маршруте 0.798~МБ/с, RTT в среднем 71.2~мс (45.4--120.2);')
    add('link check second','04-channel.tex',r'\textbf{Повторная проверка связи.}', 'на втором 2.805~МБ/с, RTT 50.6~мс (45.6--57.0).')
    add('link check protocol','04-channel.tex',r'\textbf{Повторная проверка связи.}', 'Ночные 9.75 и 5.19~МБ/с получены проверкой драйвера с другим протоколом; причина снижения скорости не установлена.')

    out.update(v5a2_expected())
    add('appendix live window','90-appendix.tex',r'\textbf{Дельта.}',r'$D(d,L) = d \cdot K_f + \min(L+d, W) \cdot K_w + S$')
    return out


def v5a2_expected():
    """R5y and accepted data: finite sites, independently cross-checked by CPU tests."""
    source=HERE.parents[1]/'data/measurements/paper-v5a2-2026-11-03'
    return {'v5a2 '+r['name']:(r['file'],r['marker'],r['phrase'])
            for r in json.loads((HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05/v5a2-sites-current.json').read_text())}


def v5a3_expected():
    """Owner analyst corrections and recorded M5 data, with finite source contracts."""
    source=HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05'
    return {'v5a3 '+r['name']:(r['file'],r['marker'],r['phrase'])
            for r in json.loads((source/'semantic-sites.json').read_text())}


def v5a4_expected():
    """Owner v5a4 claims: finite source and readability contracts."""
    source=HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05'
    return {'v5a4 '+r['name']:(r['file'],r['marker'],r['phrase'])
            for r in json.loads((source/'owner-sites.json').read_text())}


def rendered_tex(source):
    """Skip the four explicit inactive hook blocks; raw custody checks keep them."""
    return re.sub(r'\\iffalse\b.*?\\fi\b','',source,flags=re.S)


def abstract_text(source):
    """Plain abstract body, including spaces; TeX escapes count as printed text."""
    body=rendered_tex(source).split(r'\textbf{Аннотация.}',1)[1].split(r'\end{quote}',1)[0]
    body=re.sub(r'(?<!\\)%[^\n]*','',body)
    body=re.sub(r'\\pending\{([^{}]*)\}',lambda m:'Ожидается: '+m[1],body)
    return ' '.join(body.replace(r'\,','').replace(r'\%','%').replace('~',' ').replace('--','–').split())


def pending_gaps(texts):
    """Each pending macro is enumerated against FACTS5 or the explicit owner r20c inputs.

    This finite inventory rejects new/unregistered placeholders and changes to
    an existing wait; it does not poll hardware jobs or predict completion.
    """
    inventory=json.loads((HERE.parents[1]/'calc/tests/data/paper-v5d11-pending.json').read_text())
    actual=[(file,' '.join(m[1].split())) for file,text in sorted(texts.items())
            for m in re.finditer(r'\\pending\{([^{}]*)\}',text,re.S)]
    wanted=[(r['file'],r['body']) for r in inventory]
    return [] if actual==wanted else ['v4b pending inventory']



def r20_signatures(texts):
    """Each deferral is tied to its exact unmerged export, without importing values."""
    return [{'file':file,'body':m[1],'export':m[2]}
            for file,text in sorted(texts.items()) for line in text.splitlines()
            for m in re.finditer(r'\\pending\{([^{}]*)\}[^%\n]*% R20:\s*(.*)',line)]


def r20_gaps(texts):
    """The26 legacy hooks must all migrate to accepted22 or an explicit measurement wait."""
    from v5b_economics import migration_gaps
    return migration_gaps(texts)


def missing(texts):
    gaps = pending_gaps(texts) + r20_gaps(texts)
    if len(abstract_text(texts["00-abstract.tex"]))>1920:
        gaps.append("v4b abstract arXiv length")
    for name, (file, marker, wording) in expected().items():
        part = next((p for p in texts[file].split('\n\n') if marker in p), '')
        if ' '.join(wording.split()) not in ' '.join(part.split()):
            gaps.append(name)
    return gaps


SELF_TEST_COUPLINGS_SHA256='d099cfcf461f0a2a00ee596b7a5fcf09079d2984eb252b083fb6b7f5ff3fd10e'

def assert_control_diagnostics(name, actual, wanted):
    """Every declared diagnostic is mandatory; extras also reject the control."""
    assert actual == wanted, (name, actual, wanted)


def main():
    texts = {p.name: p.read_text() for p in SECTIONS.glob('*.tex')}
    if '--self-test' in sys.argv:
        assert not missing(texts), missing(texts)  # Clean publication is the positive control.
        raw=(HERE.parents[1]/'data/measurements/paper-v5d11-2026-11-06/self-test-couplings.json').read_bytes()
        assert hashlib.sha256(raw).hexdigest()==SELF_TEST_COUPLINGS_SHA256, 'undeclared self-test couplings'
        coupled=json.loads(raw)
        assert all(k in expected() and k in r['diagnostics'] and set(r['diagnostics'])<=set(expected()) for k,r in coupled.items())
        for name, (file, marker, wording) in expected().items():
            match = re.search(r'\d', wording)
            bad = (wording[:match.start()] + str((int(match[0]) + 1) % 10) + wording[match.end():]
                   if match else 'ПОДМЕНА ' + wording.split(maxsplit=1)[-1])
            pattern = r'\s+'.join(map(re.escape, wording.split()))
            part = next(p for p in texts[file].split('\n\n') if marker in p)
            changed, count = re.subn(pattern, lambda _: bad, part, count=1)
            planted = texts[file].replace(part, changed, 1)
            assert count == 1 and planted != texts[file], ('plant not applied', name)
            gaps = missing(dict(texts, **{file: planted}))
            # A plant inside a pending body also violates the independently
            # enumerated FACTS5 inventory; require both exact named verdicts.
            pending_bodies=lambda text:re.findall(r'\\pending\{([^{}]*)\}',text,re.S)
            want=(['v4b pending inventory'] if pending_bodies(texts[file])!=pending_bodies(planted) else [])
            if r20_signatures(texts)!=r20_signatures(dict(texts,**{file:planted})):want+=['v5a R20 deferred inventory']
            want+=coupled[name]['diagnostics'] if name in coupled else [name]
            assert_control_diagnostics(name, gaps, want)
            print(f'negative control: {name}: rejected by {name}; clean control: pass')
        print('self-test ok')
        return 0
    gaps = missing(texts)
    for name, (_, _, wording) in expected().items():
        print(f'{name}: {wording}' + ('  MISSING' if name in gaps else ''))
    return 1 if gaps else 0




def _prior_publication_locus(items):
    """Apply the finite r21k move/rewrite ledger; never search another paragraph."""
    source=HERE.parents[1]/'data/measurements/paper-v5d4-2026-11-05'
    reloc=json.loads((source/'relocations.json').read_text())
    revised=json.loads((source/'revisions.json').read_text())
    successor=json.loads((HERE.parents[1]/'data/measurements/paper-v5d5-2026-11-05/abstract-successors.json').read_text())
    latest=json.loads((HERE.parents[1]/'data/measurements/paper-v5d6-2026-11-05/successors.json').read_text())
    result=dict(items)
    for name,value in items.items():
        if name in latest and list(value)==latest[name]['to']:
            continue
        if name in successor and list(value)==successor[name]['to']:
            result[name]=tuple(value)
            continue
        if name in revised:
            row=revised[name]
            # Nested expected() calls may already carry the declared successor.
            assert list(value) in (row['from'],row['to']), ('undeclared claim rewrite',name,value)
            result[name]=tuple(row['to'])
        elif name in reloc:
            row=reloc[name]
            assert value[0] in (row['from'],row['to']), ('undeclared claim move',name,value)
            result[name]=(row['to'],row['marker'],value[2])
    for name,row in successor.items():
        if name in latest and list(result.get(name,()))==latest[name]['to']:
            continue
        if name in result:
            assert list(result[name]) in (row['from'],row['to']), ('undeclared analyst successor',name,result[name])
            result[name]=tuple(row['to'])
    for name,row in latest.items():
        if name in result:
            assert list(result[name]) in (row['from'],row['to']), ('undeclared v5d6 successor',name)
            result[name]=tuple(row['to'])
    return result


def _v5d7_publication_locus(items):
    """Owner r21n successors are exact finite tuples, never a fallback search."""
    ledger=json.loads((HERE.parents[1]/'data/measurements/paper-v5d7-2026-11-05/successors.json').read_text())
    already={k:v for k,v in items.items()if k in ledger and list(v)==ledger[k]['to']}
    result=_prior_publication_locus({k:v for k,v in items.items()if k not in already})
    result.update(already)
    for name,row in ledger.items():
        if name in result:
            assert list(result[name]) in (row['from'],row['to']), ('undeclared v5d7 successor',name)
            result[name]=tuple(row['to'])
    return result


def _v5d8_publication_locus(items):
    """Accepted engine25/26 and planned-method successors, each one explicit."""
    ledger=json.loads((HERE.parents[1]/'data/measurements/paper-v5d8-2026-11-05/successors.json').read_text())
    already={k:v for k,v in items.items()if k in ledger and list(v)==ledger[k]['to']}
    result=_v5d7_publication_locus({k:v for k,v in items.items()if k not in already});result.update(already)
    for name,row in ledger.items():
        if name in result:
            assert list(result[name]) in (row['from'],row['to']),('undeclared v5d8 successor',name)
            result[name]=tuple(row['to'])
    return result


def _v5d9_publication_locus(items):
    """Post-review factual successors, each exact and independently tested."""
    ledger=json.loads((HERE.parents[1]/'data/measurements/paper-v5d9-2026-11-05/successors.json').read_text())
    already={k:v for k,v in items.items()if k in ledger and list(v)==ledger[k]['to']}
    result=_v5d8_publication_locus({k:v for k,v in items.items()if k not in already});result.update(already)
    for name,row in ledger.items():
        if name in result:
            assert list(result[name]) in (row['from'],row['to']),('undeclared v5d9 successor',name)
            result[name]=tuple(row['to'])
    return result


def _v5d10_publication_locus(items):
    """Post-review factual successors, each exact and independently tested."""
    ledger=json.loads((HERE.parents[1]/'data/measurements/paper-v5d10-2026-11-06/successors.json').read_text())
    already={k:v for k,v in items.items()if k in ledger and list(v)==ledger[k]['to']}
    result=_v5d9_publication_locus({k:v for k,v in items.items()if k not in already});result.update(already)
    for name,row in ledger.items():
        if name in result:
            assert list(result[name]) in (row['from'],row['to']),('undeclared v5d10 successor',name)
            result[name]=tuple(row['to'])
    return result


def _publication_locus(items):
    """Completed RULER successors preserve every finite historical obligation."""
    ledger=json.loads((HERE.parents[1]/'data/measurements/paper-v5d11-2026-11-06/successors.json').read_text())
    already={k:v for k,v in items.items()if k in ledger and list(v)==ledger[k]['to']}
    result=_v5d10_publication_locus({k:v for k,v in items.items()if k not in already});result.update(already)
    for name,row in ledger.items():
        if name in result:
            assert list(result[name]) in (row['from'],row['to']),('undeclared v5d11 successor',name)
            result[name]=tuple(row['to'])
    return result


def _at_declared_publication_locus(function):
    def checked():
        return _publication_locus(function())
    return checked

# Keep all historical named predicates; only the explicit publication locus changes.
for _name,_function in list(globals().items()):
    if callable(_function) and (_name=='expected' or _name.endswith('_expected')):
        globals()[_name]=_at_declared_publication_locus(_function)


if __name__ == '__main__':
    sys.exit(main())
