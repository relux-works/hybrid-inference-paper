"""Condition-complete measured-cache quotations with explicit cadence/model scope."""
from run23 import sentences as inherited
from .api import CADENCE_TEXT


def suffix(row):
    return ('Cadence='+row['cadence']+' ('+CADENCE_TEXT[row['cadence']]+'); API cache point=measured; API model='+row['api_model']+
        '; hybrid model=qwen/qwen3.8-27b; comparison='+row['comparison_kind']+'; observed warm calls='+str(row['api_warm_calls']or'unknown')+'; evidence='+row['api_sample_basis']+'; price basis=run22 aggregate-token tariff projection on the stated paper shapes, using mean warm-cohort live tariffs, with measured hit fraction transferred across depths.')


def make(row,claim):
    return inherited.sentence(row,claim).rstrip()+' '+suffix(row),inherited.short_sentence(row,claim).rstrip()+' '+suffix(row)


def validate(text,row,short=False):
    (inherited.validate_short if short else inherited.validate)(text,row)
    assert suffix(row)in text,'missing cadence/cache-point/model condition'
    assert 'PRICEABLE measured cohort' in text,'measured partial cohort must stay disclosed'
    if row.get('api_over_hybrid')not in (None,''):
        assert 'API/hybrid {:.3f}'.format(float(row['api_over_hybrid']))in text,'measured multiple disagrees with row'
    return True
