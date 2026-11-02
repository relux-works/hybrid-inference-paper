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
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
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
        '% TODO(data): kit 1.6.6 remeasurement: cooled restored context, 32k point, up to 32 streams.')
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
        'У M3 Max через 5G одна точка вставки даёт 1.07~мс на токен: 42.4 секунды на 39\\,504 токена.')
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
        table('client '+r['client'], '05-clients.tex', 'tab:clients',
              label + ' & ' + ' & '.join(f'{float(r[k]):.{n}f}' for k,n in
              [('single_tok_s_32k',1),('local_sessions_day',2),('hybrid_sessions_day',2),('gain',2)]))
    for r in rows(ENGINE/'client_agents_day.csv'):
        if r['link_mbit'] != '1000': continue
        table('agents '+r['agents'], '05-clients.tex', 'tab:agents-day',
              r['agents'] + ' & ' + ' & '.join(f'{float(r[k]):.2f}' for k in
              ('local_sessions_day','hybrid_sessions_day','gain')) + ' & ' +
              ' & '.join(f'{100*float(r[k]):.1f}'+r'\%' for k in
              ('depth_modelled_call_share','depth_modelled_decode_time_share')))
    add('mostly modelled 16', '05-clients.tex', r'\textbf{Выигрыш по числу агентов.}',
        'Строка 16 агентов преимущественно модельная: 77.7\\% вызовов и 71.1\\% времени генерации лежат глубже измеренных опорных точек.')
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
        f'отдаёт её за {float(turn[100]["hybrid_s"]):.0f} секунды, через гигабит за {float(turn[1000]["hybrid_s"]):.0f} секунд.')
    shot=next(r for r in shots if r['context']=='200000' and r['link_mbit']=='1000.0')
    add('oneshot narrative',channel,r'\textbf{Разовая загрузка.}',
        f'за {float(shot["hybrid_ttft_s"]):.0f} секунд: {float(shot["server_prefill_s"]):.0f} секунд считает сервер, {float(shot["import_s"]):.0f} секунд занимает вставка,')
    cost=next(r for r in rows(ENGINE/'person_cost_s50.csv') if r['client']=='M3 Max 128 GB (measured)' and r['team']=='50' and r['basis']=='Mac already owned')
    add('traffic day client subject',channel,r'\textbf{Трафик как статья расходов.}',
        f'За восьмичасовой день клиент успевает обслужить около {float(cost["served_day"]):.0f} вызовов,')
    add('traffic compute storage narrative',channel,r'\textbf{Трафик как статья расходов.}',
        f'против примерно \\${float(cost["compute_month"])+float(cost["hosting_month"]):.0f} на серверное вычисление и хранение сессий для того же пользователя')
    e2e={r['component']:r for r in rows(ENGINE/'e2e_first_call_check.csv')}
    add('5G prediction',channel,r'\textbf{Прогноз для измеренного запуска.}',
        f'Для той же конфигурации модель даёт {float(e2e["total"]["predicted_s"]):.1f} секунды против измеренных {float(e2e["total"]["measured_s"]):.1f} секунды; '+
        f'{float(e2e["unallocated"]["measured_s"]):.1f} секунды полного времени остаются нераспределёнными по измеренным компонентам.')
    econ = '07-economics.tex'
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
        table('zero-price '+key,'07-economics.tex','tab:breakeven',title+' & '+
              ' & '.join(r'\$'+f'{float(r[key]):.2f}' for r in selected))
    verdict=lambda r: 'нет порога' if r['verdict']=='no break-even' else r'\$'+f'{float(r["price_usd_mtoken"]):.3f}'
    table('zero-price verdict','07-economics.tex','tab:breakeven','Порог, долларов за млн токенов & '+ ' & '.join(map(verdict,selected)))
    median=[r for r in price if r['basis']=='owned' and r['storage_policy']=='default' and r['share']=='0.2' and r['target']=='median API']
    assert all(r['verdict']!='no break-even' for r in median)
    thresholds=[float(r['price_usd_mtoken']) for r in median]
    add('median threshold','07-economics.tex',r'\textbf{Цена безубыточности prefill.}',
        f'Против медианного API при доле 20\\% порог равен \\${min(thresholds):.1f}--{max(thresholds):.1f} за миллион токенов для уже имеющегося клиента при хранении по политике протокола.')
    costs=[]
    for key,label in [('llamacpp_pro6000','llama.cpp PRO 6000'),('vllm_pro6000','vLLM PRO 6000'),
                      ('vllm_b300_auto','vLLM B300'),('vllm_b300_fp8kv','vLLM B300 с кэшем FP8')]:
        vals=[float(r[key+'_usd_mtoken']) for r in median]
        lo, hi = f'{min(vals):.2f}', f'{max(vals):.2f}'
        costs.append(f'{label} \\${lo}' + ('--'+hi if lo != hi else ''))
    add('measured server prices','07-economics.tex',r'\textbf{Цена безубыточности prefill.}',
        'Серверная стоимость миллиона токенов prefill по измеренным кривым: '+', '.join(costs)+'.')
    budget=next(r for r in rows(ENGINE/'perimeter_cost.csv') if r['route']=='all server')
    add('common own budgets','07-economics.tex','Одни клиентские машины почти',
        f'Обе схемы сохраняют четыре сессии на человека полный месяц; бюджет среднего prefill равен {float(budget["latency_mean_limit_s"]):.1f} секунды, p90 {float(budget["latency_p90_limit_s"]):.1f} секунды.')
    glm=next(r for r in rows(ENGINE/'glm_long_sessions.csv') if r['context']=='1000000')
    add('GLM cold load','08-million.tex',r'\textbf{Клиент для миллиона токенов.}',
        f'а серверная часть на B300 вместе с передачей по гигабитному каналу занимает по оценке {float(glm["ingest_1m_server_s"]):.0f} секунды.')
    add('GLM cold scope','08-million.tex',r'\textbf{Клиент для миллиона токенов.}',
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
    add('symmetric nonbinding latency','07-economics.tex','Одни клиентские машины почти',
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
    add('price boundary','07-economics.tex',r'\textbf{Цена безубыточности prefill.}',
        'На измеренных клиентах при доле 20\\% гибрид блокируют накладные расходы даже при бесплатном prefill.')
    add('vLLM price server only','07-economics.tex',r'\textbf{Цена безубыточности prefill.}',
        'Цены vLLM относятся только к серверу (server-only); мост не квалифицирован по времени полного вызова.')
    add('pilot correct','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Во всех четырёх вариантах правильны 35 из 48 ответов.')
    add('pilot disagreement','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Оффлоад расходится с локальным ответом в 4/48 случаях; другая локальная разбивка prefill даёт те же 4/48, повтор при той же разбивке даёт 0/48.')
    add('pilot partial','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Глубина 128 тысяч покрыта частично: запуск прерван при заполнении диска.')
    add('pilot finite','11-limitations.tex',r'\textbf{Пилот задач.}',
        'Этот пилот не устанавливает эквивалентность; разнородные кванты требуют отдельной проверки.')
    return result


def missing(texts):
    gaps = []
    for name, (file, marker, wording) in expected().items():
        part = next((p for p in texts[file].split('\n\n') if marker in p), '')
        if ' '.join(wording.split()) not in ' '.join(part.split()):
            gaps.append(name)
    return gaps


def main():
    texts = {p.name: p.read_text() for p in SECTIONS.glob('*.tex')}
    if '--self-test' in sys.argv:
        assert not missing(texts), missing(texts)  # Clean publication is the positive control.
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
            assert gaps == [name], (name, gaps)
            print(f'negative control: {name}: rejected by {name}; clean control: pass')
        print('self-test ok')
        return 0
    gaps = missing(texts)
    for name, (_, _, wording) in expected().items():
        print(f'{name}: {wording}' + ('  MISSING' if name in gaps else ''))
    return 1 if gaps else 0


if __name__ == '__main__':
    sys.exit(main())
