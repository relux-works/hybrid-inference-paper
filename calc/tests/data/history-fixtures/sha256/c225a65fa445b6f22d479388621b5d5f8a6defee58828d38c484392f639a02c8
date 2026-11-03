"""Validated quantities, strict overrides and auditable measured-file access."""
import contextvars
import copy
import datetime
import hashlib
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent / 'data'
ROOT = Path(__file__).resolve().parents[2]
_ACTIVE = contextvars.ContextVar('hybridcalc_inputs')


class InputError(ValueError):
    """A data error suitable for reporting without a Python traceback."""


class InputGap(InputError):
    """One root cause; graph propagation preserves the input path and reason."""
    def __init__(self, path, reason):
        if (path.startswith('hardware.links.') or path == 'service.transfer.bandwidth') and path.endswith('.bandwidth') and 'offload impossible' not in reason:
            reason += '; offload impossible'
        self.path, self.reason = path, reason
        super().__init__(path + ': ' + reason)

    def alarm(self):
        return {'input': self.path, 'reason': self.reason}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise InputError('{}: {}'.format(path, exc)) from exc


def leaves(value, prefix=''):
    if isinstance(value, dict) and 'value' in value:
        yield prefix, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, prefix + '.' + key if prefix else key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from leaves(child, '{}.{}'.format(prefix, index))
    elif type(value) in (float, int):
        raise InputError('{}: every number requires value, unit and provenance'.format(prefix))


def provenance(path, source):
    if not isinstance(source, dict):
        raise InputError('{}: missing provenance'.format(path))
    kind = source.get('kind')
    required = {'fact': ('url', 'access_date'), 'measured': ('package', 'sha256'),
                'estimate': ('reason',)}
    if kind not in required or any(not source.get(k) for k in required[kind]):
        raise InputError('{}: incomplete {} provenance'.format(path, kind))
    if kind == 'fact':
        if not isinstance(source['url'], str) or not source['url'].startswith(('https://', 'http://')):
            raise InputError('{}: fact requires an HTTP URL'.format(path))
        try:
            datetime.date.fromisoformat(source['access_date'])
        except (TypeError, ValueError) as exc:
            raise InputError('{}: invalid access_date'.format(path)) from exc
    if kind == 'measured':
        digest = source['sha256']
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise InputError('{}: invalid measured sha256'.format(path))


def merge(target, incoming):
    for key, value in incoming.items():
        if isinstance(value, dict) and 'value' not in value and isinstance(target.get(key), dict):
            merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)


class Inputs:
    def __init__(self, data, tolerant=False):
        self.data = copy.deepcopy(data)
        self.used = {}
        self.files = {}
        self.unavailable = {}
        self.tolerant = tolerant
        self._contracts = read_json(DATA / 'contract.json')
        self._legacy_contract = None
        if not tolerant:
            self.validate()

    def validate(self):
        for path, quantity in leaves(self.data):
            self.validate_quantity(path, quantity)

    def validate_quantity(self, path, quantity):
        if not isinstance(quantity, dict):
            raise InputError('{}: expected value, unit and provenance'.format(path))
        provenance(path, quantity.get('provenance'))
        if path.startswith('legacy.'):
            if self._legacy_contract is None:
                self._legacy_contract = read_json(DATA / 'legacy-contract.json')
            _, module, key = path.split('.', 2)
            try:
                rule = self._legacy_contract[module][key]
            except KeyError as exc:
                raise InputError('{}: unknown legacy parameter'.format(path)) from exc
        else:
            # Device/model entries share field contracts; adding another entry needs data only.
            normalized = '.'.join('*' if part.isdigit() else part for part in path.split('.'))
            rules = [rule for pattern, rule in self._contracts.items() if match(pattern, normalized)]
            if len(rules) != 1:
                raise InputError('{}: missing or ambiguous input contract'.format(path))
            rule = rules[0]
        if quantity.get('unit') != rule['unit']:
            raise InputError('{}: wrong unit {!r}; expected {}'.format(path, quantity.get('unit'), rule['unit']))
        value = quantity.get('value')
        if 'enum' in rule:
            if not isinstance(value, str) or value not in rule['enum']:
                raise InputError('{}: expected one of {}'.format(path, ', '.join(rule['enum'])))
            return
        if type(value) not in (int, float) or not math.isfinite(value):
            raise InputError('{}: value must be a finite number'.format(path))
        if rule.get('integer') and type(value) is not int:
            raise InputError('{}: value must be an integer'.format(path))
        minimum = rule.get('minimum', 0)
        if value < minimum or (rule.get('exclusive_minimum') and value == minimum):
            raise InputError('{}: value must be {} {}'.format(path, 'greater than' if rule.get('exclusive_minimum') else 'at least', minimum))
        if 'maximum' in rule and value > rule['maximum']:
            raise InputError('{}: value must be at most {}'.format(path, rule['maximum']))

    def locate(self, path):
        cur = self.data
        try:
            for part in path.split('.'):
                cur = cur[int(part)] if isinstance(cur, list) else cur[part]
            return cur
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise InputError('unknown override/input path: {}'.format(path)) from exc

    def override(self, expression):
        if '=' not in expression:
            raise InputError('override must be path=value: {}'.format(expression))
        path, raw = expression.split('=', 1)
        quantity = self.locate(path)
        if not isinstance(quantity, dict) or 'value' not in quantity:
            raise InputError('{}: override must address a numeric quantity'.format(path))
        try:
            value = json.loads(raw)
        except ValueError as exc:
            if isinstance(quantity.get('value'), str):
                value = raw
            else:
                raise InputError('{}: override value must be JSON'.format(path)) from exc
        old = copy.deepcopy(quantity)
        quantity['value'] = value
        quantity['provenance'] = {'kind': 'estimate', 'reason': 'CLI override {}; original provenance: {}'.format(expression, json.dumps(old.get('provenance'), sort_keys=True))}
        if not self.tolerant:
            try:
                self.validate()
            except InputError:
                quantity.clear()
                quantity.update(old)
                raise

    def get(self, path):
        try:
            quantity = self.locate(path)
        except InputError as exc:
            raise InputGap(path, self.missing_reason(path)) from exc
        try:
            self.validate_quantity(path, quantity)
        except InputError as exc:
            reason = str(exc)
            prefix = path + ': '
            raise InputGap(path, reason[len(prefix):] if reason.startswith(prefix) else reason) from exc
        self.used[path] = copy.deepcopy(quantity)
        return quantity['value']

    def missing_reason(self, path):
        namespace = path.split('.')[0]
        reason = self.unavailable.get(namespace, self.unavailable.get(''))
        return 'missing input; source file unavailable: ' + reason if reason else 'missing input'

    def require(self, path):
        """Lazy graph input: validate a quantity, or explicitly read nonnumeric metadata."""
        try:
            value = self.locate(path)
        except InputError as exc:
            reason = self.missing_reason(path)
            if path.endswith('.bandwidth') and path.startswith('hardware.links.'):
                reason += '; offload impossible'
            raise InputGap(path, reason) from exc
        if value is None:
            raise InputGap(path, 'null input')
        if isinstance(value, dict) or type(value) in (int, float):
            return self.get(path)
        if isinstance(value, list):
            return [self.require(path + '.' + str(i)) for i in range(len(value))]
        if not isinstance(value, str):
            raise InputGap(path, 'expected input metadata string or numeric quantity')
        return value

    def section(self, path):
        def unwrap(value, prefix):
            if isinstance(value, dict) and 'value' in value:
                return self.get(prefix)
            if isinstance(value, dict):
                return {k: unwrap(v, prefix + '.' + k) for k, v in value.items()}
            if isinstance(value, list):
                return [unwrap(v, prefix + '.' + str(i)) for i, v in enumerate(value)]
            return value
        return unwrap(self.locate(path), path)

    def measured(self, name):
        input_path = 'measurements.' + name
        try:
            info = self.locate(input_path)
            if not isinstance(info, dict):
                raise InputError('expected measured-file record')
            provenance(input_path, info.get('provenance'))
            for field in ('path', 'sha256'):
                if not isinstance(info.get(field), str) or not info[field]:
                    raise InputError('missing or invalid ' + field)
            path = ROOT / info['path']
            content = path.read_bytes()
        except (InputError, OSError, TypeError) as exc:
            raise InputGap(input_path, 'measurement unavailable: ' + str(exc)) from exc
        actual = hashlib.sha256(content).hexdigest()
        if actual != info['sha256']:
            raise InputGap(input_path, 'measurement sha256 mismatch')
        self.files[info['path']] = {'path': info['path'], 'sha256': actual, 'provenance': info['provenance']}
        return content

    def measured_json(self, name):
        try:
            return json.loads(self.measured(name))
        except (ValueError, UnicodeError) as exc:
            if isinstance(exc, InputGap):
                raise
            raise InputGap('measurements.' + name, 'invalid measurement JSON: ' + str(exc)) from exc

    def measured_value(self, name, path, value, unit):
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise InputGap('measurements.' + name, 'invalid measured value {}: expected finite nonnegative number'.format(path))
        info = self.data['measurements'][name]
        self.used['measured.' + name + '.' + path] = {'value': value, 'unit': unit, 'provenance': info['provenance']}
        return value


def match(pattern, path):
    left, right = pattern.split('.'), path.split('.')
    return len(left) == len(right) and all(a == '*' or a == b for a, b in zip(left, right))


def legacy_values(module):
    inputs = _ACTIVE.get()
    class Values(dict):
        def __missing__(self, key):
            value = inputs.get('legacy.' + module + '.' + key)
            self[key] = value
            return value
    return Values()


def measurement_path(name):
    inputs = _ACTIVE.get()
    if name == 'benchmark':
        inputs.measured('depth')
        inputs.measured('parallel')
        return str((ROOT / inputs.data['measurements']['depth']['path']).parent)
    inputs.measured(name)
    return str(ROOT / inputs.data['measurements'][name]['path'])
