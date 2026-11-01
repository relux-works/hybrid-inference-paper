"""Scenario loading and isolated compatibility execution."""
import contextlib
import importlib
import io
import sys
import threading
import types
import uuid
from pathlib import Path

from .inputs import DATA, ROOT, Inputs, InputError, _ACTIVE, merge, read_json

_LOCK = threading.RLock()


def scenarios():
    return [read_json(path) for path in sorted((DATA / 'scenarios').glob('*.json'))]


def load(name, overrides=()):
    candidate = Path(name)
    path = candidate if candidate.is_file() else DATA / 'scenarios' / (name + '.json')
    scenario = read_json(path)
    if scenario.get('kind') not in ('legacy', 'paper', 'glm', 'service', 'ownership', 'bridge', 'paper_tables', 'paper_tables_r6', 'paper_tables_r7', 'paper_tables_r8'):
        raise InputError('unknown scenario kind: {}'.format(scenario.get('kind')))
    canonical = scenario['kind'] != 'legacy'
    data, failures = {}, {}
    file_contract = read_json(DATA / 'file-contract.json')
    bundled = path.resolve().parent == (DATA / 'scenarios').resolve()
    def read_input(filename, provides):
        try:
            document = read_json(filename)
            if not isinstance(document, dict):
                raise InputError('input file must contain a JSON object')
            if provides and set(document) - set(provides):
                raise InputError('input file writes outside its declared namespaces: ' + ', '.join(sorted(set(document) - set(provides))))
            merge(data, document)
        except InputError as exc:
            if not canonical:
                raise
            # A failed later layer cannot silently fall back to values it might have overridden.
            if provides:
                for namespace in provides:
                    data.pop(namespace, None)
                    failures[namespace] = str(exc)
            else:
                data.clear()
                failures[''] = str(exc)
    read_input(DATA / 'measurements.json', ['measurements'])
    for entry in scenario['inputs']:
        if isinstance(entry, dict):
            filename, provides = entry['file'], entry['provides']
            if not isinstance(provides, list) or not provides or any(not isinstance(p, str) or not p or '.' in p for p in provides):
                raise InputError('input file provides must list top-level namespaces')
        else:
            filename = entry
            provides = file_contract.get(Path(filename[len('bundle:'):] if filename.startswith('bundle:') else filename).name)
        if filename.startswith('bundle:'):
            filename = DATA / filename[len('bundle:'):]
        else:
            filename = (DATA if bundled else path.parent) / filename
        read_input(filename, provides)
    merge(data, scenario.get('overrides', {}))
    inputs = Inputs(data, tolerant=canonical)
    inputs.unavailable = failures
    for override in overrides:
        inputs.override(override)
    return scenario, inputs


def compatibility(scenario, inputs):
    """Fresh module namespace per run; no import-order leaks or CSV writes."""
    with _LOCK:
        prefix = 'hybridcalc._legacy_' + uuid.uuid4().hex
        package = types.ModuleType(prefix)
        package.__path__ = [str(Path(__file__).parent / 'legacy')]
        package.__package__ = prefix
        sys.modules[prefix] = package
        token = _ACTIVE.set(inputs)
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                module = importlib.import_module(prefix + '.' + scenario['module'])
                module.main()
            return output.getvalue()
        finally:
            _ACTIVE.reset(token)
            for name in list(sys.modules):
                if name == prefix or name.startswith(prefix + '.'):
                    del sys.modules[name]


def run(name, overrides=()):
    scenario, inputs = load(name, overrides)
    if scenario['kind'] == 'legacy':
        transcript = compatibility(scenario, inputs)
        result = {'scenario': scenario['name'], 'tables': [
            {'name': 'legacy transcript', 'columns': {'line': 'text'},
             'rows': [{'line': line} for line in transcript.splitlines()]}],
            'legacy_text': transcript}
    elif scenario['kind'] == 'paper_tables_r8':
        from .paper_tables_r8 import calculate
        result = calculate(scenario, inputs)
    elif scenario['kind'] == 'paper_tables_r7':
        from .paper_tables_r7 import calculate
        result = calculate(scenario, inputs)
    elif scenario['kind'] == 'paper_tables_r6':
        from .paper_tables_r6 import calculate
        result = calculate(scenario, inputs)
    elif scenario['kind'] == 'paper_tables':
        from .paper_tables import calculate
        result = calculate(scenario, inputs)
    elif scenario['kind'] == 'bridge':
        from .crossover import calculate
        result = calculate(scenario, inputs)
    elif scenario['kind'] == 'ownership':
        from .ownership import calculate
        result = calculate(scenario, inputs)
    elif scenario['kind'] == 'service':
        from .service import calculate
        result = calculate(scenario, inputs)
    else:
        from .paper import calculate
        result = calculate(scenario, inputs)
    if scenario.get('export_suffix') == 'conservative':
        from .metrics import unique
        result['tables'] = [t for t in result['tables'] if any(any(p.startswith('hosting.') or '.hosting.' in p for p in d['inputs']) for d in t.get('dependencies', {}).values())]
        for table in result['tables']:
            table['id'] += '_conservative'
            table['name'] += ' / conservative append-only hosting'
        result['alarms'] = unique(a for t in result['tables'] for a in t.get('alarms', []))
        result['computed_metrics'] = sum(type(v) in (int, float) for t in result['tables'] for row in t['rows'] for v in row.values())
        result['export_namespace'] = scenario['export_namespace']
    result['sources'] = [{'path': path, **quantity} for path, quantity in sorted(inputs.used.items())]
    result['files'] = list(inputs.files.values())
    return result
