"""CSV-only pending measurements; missing evidence never becomes an observation."""
import csv
import datetime
import math

from hybridcalc.inputs import InputGap
from hybridcalc import deep_r21 as d
from .measurements import DATA


def number(value, name, zero=False):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise InputGap('run22.'+name, 'finite numeric measurement required')
    if not math.isfinite(result) or result < 0 or (not zero and result == 0):
        raise InputGap('run22.'+name, 'positive finite measurement required')
    return result


def date(value):
    try:
        result = datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    except (TypeError, ValueError, AttributeError):
        raise InputGap('run22.provenance', 'ISO8601 timestamp required')
    if result.tzinfo is None:
        raise InputGap('run22.provenance', 'timezone required')
    return result


def rows(name, directory=DATA):
    with (directory/(name+'.csv')).open(newline='') as f:
        return list(csv.DictReader(f))


def provenance(row):
    if not row.get('source'):
        raise InputGap('run22.provenance', 'measurement source required')
    date(row.get('observed_at'))


def cache_rows(records, known):
    out = {}
    for row in records:
        provenance(row)
        key = (row.get('model'),row.get('tag'),row.get('profile'))
        if key[:2] not in known or key in out or key[2] not in ('existing_combined','claude_deep','million'):
            raise InputGap('run22.cache', 'unknown or duplicate provider/profile')
        total = number(row.get('input_tokens'),'input_tokens')
        cached = number(row.get('cached_tokens'),'cached_tokens',True)
        count = number(row.get('series_calls'),'series_calls')
        warm = number(row.get('warm_calls'),'warm_calls')
        # Explicit policy: do not promote the exploratory three-call probe to a
        # provider-wide cache rate. A dated repeated series must include warm calls.
        if count <= 3 or not count.is_integer() or not warm.is_integer() or warm >= count or cached > total or not total.is_integer() or not cached.is_integer():
            raise InputGap('run22.cache', 'repeated series beyond three-call probe, warm calls and valid token counts required')
        out[key] = cached/total
    return out


def availability_rows(records, known):
    out = {}
    windows = set()
    for row in records:
        if not row.get('source'):
            raise InputGap('run22.availability', 'window source required')
        start,end = date(row.get('window_start')),date(row.get('window_end'))
        if end <= start:
            raise InputGap('run22.availability', 'positive common window required')
        windows.add((start,end))
        key = (row.get('model'),row.get('tag'))
        value = number(row.get('availability_percent'),'availability',True)
        if key not in known or key in out or value > 100:
            raise InputGap('run22.availability', 'unknown, duplicate or invalid provider availability')
        out[key] = value
    if len(windows) > 1:
        raise InputGap('run22.availability', 'same stated window required for every provider; no mixed-window minima')
    return out, next(iter(windows),None)


def server_rows(records, servers, kind):
    out = []; seen = set()
    for raw in records:
        provenance(raw)
        row = dict(raw)
        for name in ('depth','streams' if kind=='decode' else 'delta'):
            value = number(row.get(name),name)
            if not value.is_integer():
                raise InputGap('run22.server', 'integer depth/shape required')
            row[name] = int(value)
        key = (row.get('server'),row['depth'],row.get('streams',row.get('delta')))
        if key in seen or key[0] not in servers or row.get('engine') != 'vllm':
            raise InputGap('run22.server', 'unique PRO6000/B300 vLLM observations required')
        seen.add(key)
        if row['depth'] > 1048576:
            raise InputGap('run22.server', 'YaRN analysis envelope exceeded')
        if row['depth'] > 262144 and row.get('extension') != 'yarn_factor4':
            raise InputGap('run22.server', 'deep measurement requires recorded YaRN factor4')
        if kind == 'decode':
            row['aggregate_tok_s'] = number(row.get('aggregate_tok_s'),'aggregate_tok_s')
        else:
            if row['depth']+row['delta'] > 1048576:
                raise InputGap('run22.server', 'prefill context exceeded')
            servers[key[0]].slots(row['depth']+row['delta'])
            row['prefill_s'] = number(row.get('prefill_s'),'prefill_s')
        out.append(row)
    if kind == 'decode':
        limits={}
        for row in out:
            physical=servers[row['server']].slots(row['depth'])
            limit=row.get('resident_limit')
            if limit not in ('',None):
                limit=number(limit,'resident_limit')
                if not limit.is_integer() or limit>physical:
                    raise InputGap('run22.decode','measured resident limit exceeds physical capacity')
                row['resident_limit']=int(limit)
                key=(row['server'],row['depth'])
                if key in limits and limits[key]!=int(limit):
                    raise InputGap('run22.decode','conflicting measured resident limits at one depth')
                limits[key]=int(limit)
                physical=min(physical,int(limit))
            if row['streams']>physical:
                raise InputGap('run22.decode','measured streams exceed resident capacity')
            ones=[r['depth'] for r in out if r['server']==row['server'] and r['streams']==1]
            if not ones or not min(ones)<=row['depth']<=max(ones):
                raise InputGap('run22.decode','single-stream reference must span parallel observations')
        for row in out:
            if row['streams'] > limits.get((row['server'],row['depth']),row['streams']):
                raise InputGap('run22.decode','measured streams exceed resident capacity')
        return out
    return out


def mac_rows(records):
    out = {}; seen = set()
    for raw in records:
        provenance(raw)
        row = dict(raw)
        for name in ('depth','delta'):
            value = number(row.get(name),name)
            if not value.is_integer():
                raise InputGap('run22.mac', 'integer restored depth/delta required')
            row[name] = int(value)
        key = (row.get('client'),row['depth'],row['delta'])
        if key in seen or key[0] not in ('m3max','m5max64','m5max') or key[1] != 1040000 or key[2] not in (690,2000,10000):
            raise InputGap('run22.mac', 'unique supported Mac1.04M delta required')
        if row.get('priority') != 'normal_priority' or row.get('slot_restored') != 'true':
            raise InputGap('run22.mac', 'recorded normal priority and restored1,040,000 slot required')
        if row.get('extension') != 'yarn_factor4':
            raise InputGap('run22.mac','direct1.04M measurement requires recorded model-card YaRN factor4')
        for name in ('prefill_s','import_s','decode_tok_s','logits_kl'):
            if row.get(name) != '':
                row[name] = number(row.get(name),name,name in ('import_s','logits_kl'))
        if isinstance(row.get('import_s'),(int,float)):
            if row.get('import_kind') not in ('delta_import','slot_restore') or row.get('transport') not in ('bf16','f32'):
                raise InputGap('run22.mac','import kind and recurrent transport must be recorded; slot restore is not delta import')
        if row.get('prefill_s') == '' and row.get('import_s') == '' and row.get('decode_tok_s') == '' and row.get('logits_kl') == '':
            raise InputGap('run22.mac', 'at least one observed metric required')
        seen.add(key); out[key] = row
    return out
