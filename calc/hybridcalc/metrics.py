"""Declared dependency DAG. Failed inputs propagate alarms, never substitute numbers."""
import math
from dataclasses import dataclass
from .inputs import InputError, InputGap


def unique(alarms):
    return [dict(input=path, reason=reason) for path, reason in
            sorted({(a['input'], a['reason']) for a in alarms})]


@dataclass
class Outcome:
    value: object = None
    alarms: tuple = ()


class Graph:
    def __init__(self, inputs):
        self.inputs = inputs
        self.inputs.used.clear()
        self.inputs.files.clear()
        self.readers = {}
        self.nodes = {}
        self._roots = {}
        self.cache = {}
        self.tables = []
        self.numeric_count = 0

    def add(self, name, requires, function):
        key = '@' + name
        if key in self.nodes:
            raise ValueError('duplicate metric ' + name)
        self.nodes[key] = (tuple(requires), function)
        return key

    def constant(self, name, value):
        """Presentation labels and mathematical identities, never assumed physical inputs."""
        return self.add(name, (), lambda: value)

    def bundle(self, name, prefix, fields):
        return self.add(name, [prefix + '.' + field for field in fields],
                        lambda *values: dict(zip(fields, values)))

    def measurement(self, name, json_lines=False):
        def read():
            if json_lines:
                import json
                try:
                    return [json.loads(line) for line in self.inputs.measured(name).splitlines()]
                except (ValueError, UnicodeError) as exc:
                    if isinstance(exc, InputGap):
                        raise
                    raise InputGap('measurements.' + name, 'invalid JSON lines: ' + str(exc)) from exc
            return self.inputs.measured_json(name)
        # File readers validate the structured input at this declared path.
        path = 'measurements.' + name
        self.readers[path] = read
        return self.add('measurement.' + name, [path], lambda document: document)

    def positions(self, path):
        """Array shape is independent of the validity of its individual quantities."""
        try:
            raw = self.inputs.locate(path)
        except InputError:
            raw = None
        if isinstance(raw, list) and raw:
            return [path + '.' + str(index) for index in range(len(raw))]
        def invalid(value):
            raise InputGap(path, 'expected a nonempty list')
        return [self.add(path + '.shape', [path], invalid)]

    def mapping(self, path):
        """Enumerate known record keys without validating unrelated leaf values."""
        try:
            raw = self.inputs.locate(path)
        except InputError:
            raw = None
        if isinstance(raw, dict) and raw and 'value' not in raw:
            return [(key, path + '.' + key) for key in raw]
        def invalid(value):
            raise InputGap(path, 'expected a nonempty record')
        return [(None, self.add(path + '.shape', [path], invalid))]

    def roots(self, key):
        if key in self._roots:
            return self._roots[key]
        if not key.startswith('@'):
            result = {key}
        else:
            dependencies, _ = self.nodes[key]
            result = set().union(*(self.roots(child) for child in dependencies)) if dependencies else set()
        self._roots[key] = result
        return result

    def resolve(self, key):
        if key in self.cache:
            return self.cache[key]
        if not key.startswith('@'):
            try:
                result = Outcome(self.readers[key]() if key in self.readers else self.inputs.require(key))
            except InputGap as exc:
                result = Outcome(alarms=(exc.alarm(),))
        else:
            dependencies, function = self.nodes[key]
            arguments = [self.resolve(child) for child in dependencies]
            errors = unique(a for argument in arguments for a in argument.alarms)
            if errors:
                result = Outcome(alarms=tuple(errors))
            else:
                try:
                    value = function(*(argument.value for argument in arguments))
                    if isinstance(value, float) and not math.isfinite(value):
                        raise InputGap(key, 'calculated value is not finite')
                    result = Outcome(value)
                except InputGap as exc:
                    roots = self.roots(key)
                    matches = [root for root in roots if root.rsplit('.', 1)[-1] == exc.path.rsplit('.', 1)[-1]]
                    alarm = exc.alarm()
                    if exc.path not in roots and len(matches) == 1:
                        alarm['input'] = matches[0]
                    result = Outcome(alarms=(alarm,))
                except (InputError, KeyError, TypeError, ArithmeticError, ValueError, IndexError) as exc:
                    # Per-node containment keeps the rest of the graph available for malformed structured data.
                    roots = sorted(self.roots(key))
                    source = roots[0] if len(roots) == 1 else key
                    result = Outcome(alarms=({'input': source, 'reason': 'not computable: ' + str(exc)},))
        self.cache[key] = result
        return result

    def table(self, name, columns, references):
        rows, declarations, alarms = [], {}, []
        for index, reference in enumerate(references):
            row = {}
            for column in columns:
                key = reference[column]
                outcome = self.resolve(key)
                row[column] = {'alarm': list(outcome.alarms)} if outcome.alarms else outcome.value
                alarms.extend(outcome.alarms)
                if not outcome.alarms and type(outcome.value) in (int, float) and self.roots(key):
                    self.numeric_count += 1
                declarations['{}.{}'.format(index, column)] = {
                    'requires': list(self.nodes[key][0]) if key.startswith('@') else [key],
                    'inputs': sorted(self.roots(key))}
            rows.append(row)
        result = {'name': name, 'columns': columns, 'rows': rows,
                  'alarms': unique(alarms), 'dependencies': declarations}
        self.tables.append(result)
        return result

    def result(self, name, notes=()):
        return {'scenario': name, 'tables': self.tables,
                'alarms': unique(a for table in self.tables for a in table['alarms']),
                'computed_metrics': self.numeric_count, 'notes': list(notes)}


def nonempty(calls):
    if not calls:
        raise InputGap('workload.sample_calls', 'empty call mix; per-call metrics are not computable')
    return calls


def field(value, path, source):
    """Read measured structured fields without losing the measured input's identity."""
    try:
        for key in path.split('.'):
            value = value[int(key)] if isinstance(value, list) else value[key]
        if value is None:
            raise TypeError('null field')
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('nonfinite field')
        return value
    except (KeyError, TypeError, IndexError, ValueError) as exc:
        raise InputGap(source, 'invalid measured field {}: {}'.format(path, exc)) from exc
