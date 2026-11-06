"""Strict current v3 publication guard, separate from immutable historical exports.

The owner-authorized v3 baseline pins every tracked paper byte and every TeX
numeric occurrence (file, line, spelling, unit, source-line hash). Range and
server claims are also recomputed by the live publication checkers. Historical
quote ledgers retain their original coordinates and are tested in their source
revision, rather than reinterpreted as a current-publication waiver list.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from r13_audit import ROOT, module
from r13_reverse import tokens

PIN = ROOT / 'calc/tests/data/paper-v2-publication.json'
SITES = ROOT / 'calc/tests/data/paper-v2-sites.csv'
FIELDS = ('file', 'line', 'token', 'unit', 'line_sha256', 'occurrence')
# Snapshot authority and pre-migration publication head are pinned separately.
REVIEW_BASE = '5f9846f319c8f5f222979bcb017ad9ae65d6206e'
SOURCE_REVISION = 'e51942d331e274833f97f934a750d780c9bea9b0'
SNAPSHOT = 'run16/base'
SOURCE_REVISION_RUN24 = 'ca7f228acd789380bf46016fd87acc33e1b07aef'
SOURCE_REVISION_RUN23 = '9064701a9a07bd2726f76cefb6a05aa6aa428c0d'
SOURCE_REVISION_RUN22 = '9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0'
SOURCE_REVISION_RUN17 = '714fe72135819ededd7c270dd661c1359acfa6c3'
EXTRA_RUN17 = ('architecture_link_threshold.csv','architecture_extrapolation.csv','sliding_geometry.csv','measured_model_rates.csv','bf16_transfer_egress.csv')


MIGRATION_SHA256 = '9135699c504ae069f5784cbf4022a36eb59d6c8cf96961a995390af5ce72ab7d'


import history_evidence as history

def historical_delta(snapshot):
    """Exact authorized v4 differences from a preserved historical snapshot."""
    payload = (ROOT/'calc/tests/data/paper-rc4-migration.json').read_bytes()
    assert hashlib.sha256(payload).hexdigest() == MIGRATION_SHA256, 'v4 migration record changed'
    return json.loads(payload)['historical_deltas'][snapshot]


def tracked_files():
    return subprocess.check_output(['git', 'ls-files', 'paper'], cwd=ROOT, text=True).splitlines()


def read_texts():
    return {str(path.relative_to(ROOT)): path.read_text()
            for path in sorted((ROOT/'paper').rglob('*.tex')) if path != ROOT/'paper/version.tex'}


def numeric_sites(texts):
    counts = {}
    result = []
    for name, line, token, unit in tokens(texts):
        key = (name, line, token, unit)
        counts[key] = counts.get(key, 0) + 1
        result.append(dict(zip(FIELDS, (name, str(line), token, unit,
                      hashlib.sha256(texts[name].splitlines()[line-1].encode()).hexdigest(), str(counts[key])))))
    return result



def records():
    with SITES.open(newline='') as stream:
        return list(csv.DictReader(stream))


def check_publication(site_records=None, texts=None):
    """No extra/missing sites or files, no byte drift, no weakened numeric tolerances."""
    site_records = records() if site_records is None else site_records
    texts = read_texts() if texts is None else texts
    actual = {tuple(r[k] for k in FIELDS) for r in numeric_sites(texts)}
    supplied = [tuple(r[k] for k in FIELDS) for r in site_records]
    assert len(set(supplied)) == len(supplied), 'duplicate v2 numeric site'
    assert not actual - set(supplied), 'unregistered v2 numeric site: ' + repr(sorted(actual-set(supplied))[:3])
    assert not set(supplied) - actual, 'unused v2 numeric site: ' + repr(sorted(set(supplied)-actual)[:3])
    pin = json.loads(PIN.read_text())
    assert pin['snapshot'] == SNAPSHOT and pin['source_revision'] == SOURCE_REVISION
    assert pin['review_base'] == REVIEW_BASE, 'external-review migration base changed'
    assert pin['additional_source_revision'] == SOURCE_REVISION_RUN17 and pin['additional_architecture_files']==list(EXTRA_RUN17), 'run17 source binding changed'
    assert pin['economics_revision']==SOURCE_REVISION_RUN24, 'run24 authority changed'
    assert hashlib.sha256((ROOT/'calc/out/run24/r24_manifest.json').read_bytes()).hexdigest()==pin['run24_manifest_sha256'], 'run24 numerical manifest changed'
    assert not history.unchanged(SOURCE_REVISION_RUN24,'calc/out/run24','calc/run24',allow_ports=True), 'accepted run24 source/output changed'
    assert hashlib.sha256((ROOT/'calc/out/run23/r23_manifest.json').read_bytes()).hexdigest()==pin['run23_manifest_sha256'], 'run23 numerical manifest changed'
    assert not history.unchanged(SOURCE_REVISION_RUN23,'calc/out/run23','calc/run23',allow_ports=True), 'accepted run23 source/output changed'
    assert hashlib.sha256((ROOT/'calc/out/run22/r22_manifest.json').read_bytes()).hexdigest()==pin['run22_manifest_sha256'], 'run22 numerical manifest changed'
    assert not history.unchanged(SOURCE_REVISION_RUN22,'calc/out/run22','calc/run22',allow_ports=True), 'accepted run22 source/output changed'
    assert set(tracked_files()) == set(pin['files']), 'v2 publication file set changed'
    assert set(texts) == {n for n in pin['files'] if n.endswith('.tex')}, 'v2 TeX file set changed'
    for name, digest in pin['files'].items():
        payload = texts[name].encode() if name in texts else (ROOT/name).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == digest, 'v2 publication bytes changed: ' + name
    # Exact snapshot payloads and regenerated figure inputs stay tied to R14.
    for path in (ROOT/'paper/data/engine').glob('*.csv'):
        assert path.read_bytes() == (ROOT/'calc/out/run16/base'/path.name).read_bytes(), 'v2 snapshot mismatch: '+path.name
    # New measured-rate architecture inputs are an additional frozen snapshot;
    # the existing R16 economics/diagnostics retain their explicitly named base.
    assert {p.name for p in (ROOT/'paper/data/engine17').glob('*.csv')} == set(EXTRA_RUN17)
    for name in EXTRA_RUN17:
        assert (ROOT/'paper/data/engine17'/name).read_bytes() == (ROOT/'calc/out/run17/architectures'/name).read_bytes(), 'run17 architecture snapshot mismatch: '+name
    projection=module('v4c_arch_projection',ROOT/'paper/data/arch_compare.py')
    with (ROOT/'paper/data/arch-compare.csv').open(newline='') as stream:
        actual_chart=list(csv.DictReader(stream))
    calculated=projection.calculated_rows()
    assert actual_chart==[{k:str(v) for k,v in row.items()} for row in calculated], 'corrected live-window projection changed'
    # Recompute all five figure inputs in a disk-backed temporary directory;
    # archived R13 derived inputs retain their original bytes.
    derived = module('v14_derived', ROOT/'paper/data/derive_charts.py')
    with tempfile.TemporaryDirectory(prefix='paper-r14-derived-') as directory:
        derived.HERE = directory
        derived.ENGINE = str(ROOT/'paper/data/engine')
        derived.main()
        for name in ('glm-1m-cost.csv', 'payback.csv', 'team-cost-s20.csv', 'team-cost-s50.csv', 'team-perimeter.csv'):
            assert (ROOT/'paper/data'/name).read_bytes() == (Path(directory)/name).read_bytes(), 'v2 figure mismatch: '+name
    ranges = module('v2_ranges', ROOT/'paper/data/check_ranges.py')
    section_texts = {Path(name).name: text for name, text in texts.items() if name.startswith('paper/sections/')}
    assert not ranges.check(section_texts), 'v2 range claims: '+repr(ranges.check(section_texts))
    offload = module('v2_offload', ROOT/'paper/data/offload_bound.py')
    assert not offload.missing(section_texts), 'v2 server claims: '+repr(offload.missing(section_texts))
    return dict(scanned_numbers=len(actual), publication_files=len(pin['files']))


def refresh():
    """Explicit migration operation; never invoked by a test or normal validation."""
    pin = dict(snapshot=SNAPSHOT, source_revision=SOURCE_REVISION, additional_source_revision=SOURCE_REVISION_RUN17, additional_architecture_files=list(EXTRA_RUN17),
               review_base=REVIEW_BASE, economics_revision=SOURCE_REVISION_RUN24,
               run24_manifest_sha256=hashlib.sha256((ROOT/'calc/out/run24/r24_manifest.json').read_bytes()).hexdigest(),
               run23_manifest_sha256=hashlib.sha256((ROOT/'calc/out/run23/r23_manifest.json').read_bytes()).hexdigest(),
               run22_manifest_sha256=hashlib.sha256((ROOT/'calc/out/run22/r22_manifest.json').read_bytes()).hexdigest(),
               files={name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in tracked_files()})
    PIN.write_text(json.dumps(pin, indent=2, ensure_ascii=False)+'\n')
    with SITES.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(numeric_sites(read_texts()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--refresh']:
        refresh()
    elif sys.argv[1:]:
        raise SystemExit('usage: publication_v2.py [--refresh]')
    else:
        print(check_publication())
