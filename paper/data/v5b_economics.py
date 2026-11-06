"""Finite economic publication contracts, with R23 current views and R22 migration custody.

This guard checks text and exact legacy-site disposition. It does not certify
provider caching or delta-import portability; native measurements have separate R23 controls.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'data/measurements/paper-v5d4-2026-11-05'
HISTORICAL_SOURCE=ROOT/'data/measurements/paper-v5b-2026-11-03'
ENGINE='9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0'


def expected():
    return {'v5b '+r['name']:(r['file'],r['marker'],r['phrase'])
            for r in json.loads((SOURCE/'economic-sites.json').read_text())}


def migration_gaps(texts):
    """All26 prior sites need an explicit accepted successor or measured wait."""
    old=json.loads((ROOT/'calc/tests/data/paper-v5a-r20-sites.json').read_text())
    rows=json.loads((HISTORICAL_SOURCE/'r20-migration.json').read_text())
    known={k.removeprefix('v5b ') for k in expected()}
    valid=(len(rows)==26 and [r['id'] for r in rows]==list(range(1,27))
           and [r['old'] for r in rows]==old
           and all(r['accepted_engine']==ENGINE and r['status']=='filled from accepted run22'
                   and r['source_exports'] and r['successor_sites']
                   and set(r['successor_sites'])<=known for r in rows)
           and not any('% R20:' in text for text in texts.values()))
    return [] if valid else ['v5a R20 deferred inventory']
