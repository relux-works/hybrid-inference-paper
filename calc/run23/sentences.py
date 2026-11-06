"""Run22 row-bound quotations, with measured decode and zero-offload disclosure."""
from run22 import sentences as old

SERVERS=old.SERVERS
LINKS=old.LINKS
FIELDS=old.FIELDS
clauses=old.clauses
parse=old.parse


def decode_basis(row):
    return ('PRO decode measured/interpolated 16384–256000, beyond modelled' if row['server']=='pro6000_fp8' else
        'B300 decode modelled; rental measurement pending')


def zero_offload(row):
    value=row.get('offload_share_max',row.get('offload_share'))
    if isinstance(value,dict):return ''  # capacity alarm, not a zero observation
    if value not in (None,'','nan') and float(value)==0:
        return 'Zero prefill offload; local-client work plus idle residency and any stated server generation overflow; not a prefill-offload gain.'
    return ''


def sentence(row,claim,short=False):
    return old.sentence(row,claim,short)+' '+decode_basis(row)+'. '+zero_offload(row)


def short_sentence(row,claim):
    text=old.short_sentence(row,claim)
    text=text.replace('server decode modelled unless measured CSV overrides.',decode_basis(row)+'.')
    return text+' '+zero_offload(row)


def validate(text,row):
    result=old.validate(text,row)
    assert decode_basis(row) in text,'missing measured/modelled decode basis'
    if zero_offload(row):
        assert zero_offload(row) in text,'zero-offload result cannot be claimed as offload gain'
    return result


def validate_short(text,row):
    result=old.validate_short(text,row)
    assert decode_basis(row) in text,'missing short decode basis'
    if zero_offload(row):
        assert zero_offload(row) in text,'zero-offload short form lacks disclosure'
    return result
