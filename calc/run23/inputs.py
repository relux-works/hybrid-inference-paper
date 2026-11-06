"""Accepted night measurements and the unchanged provenance CSV contracts."""
import csv
import hashlib
import json
from pathlib import Path

from hybridcalc.inputs import InputGap
from run22 import api, interfaces as old

DATA=Path(__file__).parent/'data'


def rows(name):
    with (DATA/(name+'.csv')).open(newline='') as f:
        return list(csv.DictReader(f))


def evidence():
    info=json.loads((DATA/'evidence.json').read_text())
    # These receipts preserve the accepted source independently of later pending
    # CSV updates. A data-only replacement updates its provenance digest too.
    for name,digest in info['files'].items():
        if hashlib.sha256((DATA/name).read_bytes()).hexdigest()!=digest:
            raise InputGap('run23.evidence','accepted source SHA256 mismatch: '+name)
    return info


def mac_rows(records=None):
    out={}
    for raw in rows('mac_direct') if records is None else records:
        old.provenance(raw)
        row=dict(raw)
        for key in ('depth','delta'):
            value=old.number(row[key],key)
            if not value.is_integer():
                raise InputGap('run23.mac','integer measured shape required')
            row[key]=int(value)
        key=(row['depth'],row['delta'])
        if row.get('client')!='m3max' or key in out or row['depth'] not in (524288,1040000) or row['delta'] not in (690,2000,10000):
            raise InputGap('run23.mac','unique supported M3 Max measured shape required')
        if row.get('priority')!='normal_priority' or row.get('cache_state')!='warm_no_purge' or 'LaCie' not in row.get('storage',''):
            raise InputGap('run23.mac','normal-priority warm/no-purge LaCie provenance required')
        if row.get('recovery_kind')!='full_slot_restore' or row.get('extension')!='yarn_factor4':
            raise InputGap('run23.mac','full-slot restore and model-card YaRN required; not delta import')
        if float(row.get('raw_logit_bound',0))!=4 or float(row.get('earlier_bound',0))!=1 or not row.get('earlier_refusal'):
            raise InputGap('run23.mac','both the earlier bound1 refusal and uncalibrated bound4 must remain disclosed')
        fits=sum(key)<=1048576
        if not fits:
            if row.get('status')!='refused_context' or row.get('prefill_s') not in ('',None):
                raise InputGap('run23.mac','context refusal cannot become a measured prefill')
        elif row.get('status')!='measured':
            raise InputGap('run23.mac','measured status required for supported shape')
        else:
            row['prefill_s']=old.number(row.get('prefill_s'),'prefill_s')
        for key2 in ('restore_first_s','restore_warm_s','decode_tok_s'):
            row[key2]=old.number(row.get(key2),key2)
        out[key]=row
    return out


def pending_inputs(physical_servers):
    evidence()
    known={(api.MODEL,r['tag'])for r in api.providers()}
    availability,window=old.availability_rows(rows('provider_availability'),known)
    return dict(cache=old.cache_rows(rows('provider_cache'),known),availability=availability,window=window,
        decode=old.server_rows(rows('server_decode'),physical_servers,'decode'),
        prefill=old.server_rows(rows('server_prefill'),physical_servers,'prefill'),
        mac=old.mac_rows(rows('mac_million')))


def bridge_rows():
    doc=json.loads((DATA/'bridge-receipt.json').read_text())
    return [dict(depth=r['depth'],delta=r['delta'],**r['median'],client=doc['client_backend'],link=doc['transport'],
        use='context only; no separate non-overlapping export/conversion term; CUDA import is not Mac recovery; retain reviewed aggregate bridge envelope')for r in doc['rows']]
