"""Published CSV regeneration: reference bytes, otherwise at most two binary64 steps.

This comparator is only for fresh computations, never immutable evidence hashes.
The caller supplies float coordinates from the reference schema. CSV structure and
all other field bytes remain exact, including headers, quoting and line endings.
"""
import hashlib
import json
from pathlib import Path
import math
import platform
import re
import struct
import sys

SCHEMA_SHA256 = 'dd867aad009099f11f279795c28cc384fdc492459e21eeef258eeca9e0335c8f'
REFERENCE = (3, 14, 4)
MAX_ULP = 2
_TOKEN = re.compile(rb'("(?:[^"]|"")*"|[^,\r\n]*)(,|\r\n|\n|$)')
_FLOAT = re.compile(rb'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?')


def selected_mode():
    # No untested interpreter is silently declared byte-equivalent.
    return 'bytes' if platform.python_implementation() == 'CPython' and sys.version_info[:3] == REFERENCE else 'ulp'


def _tokens(raw):
    result = []
    end = 0
    for match in _TOKEN.finditer(raw):
        if match.start() != end:
            raise AssertionError('malformed CSV structure')
        if match.start() == len(raw):
            break
        field, delimiter = match.groups()
        result.append((field, delimiter))
        end = match.end()
    if end != len(raw):
        raise AssertionError('malformed CSV structure')
    return result


def _ordered(value):
    bits = struct.unpack('>Q', struct.pack('>d', value))[0]
    return (~bits & ((1 << 64)-1)) if bits >> 63 else bits | (1 << 63)


def compare_csv(actual, expected, float_cells, name='', mode=None):
    automatic = mode is None
    mode = selected_mode() if mode is None else mode
    if mode not in ('bytes', 'ulp'):
        raise ValueError('unknown regeneration mode')
    detail = 'exact CSV bytes' if mode == 'bytes' else 'maximum 2 ulp in canonical finite float fields only'
    print('CSV regeneration [' + name + ']: ' + ('automatic ' if automatic else 'explicit control ')
          + mode + '; Python ' + platform.python_version()
          + '; reference CPython 3.14.4; ' + detail, flush=True)
    if mode == 'bytes':
        assert actual == expected, name + ': reference CSV bytes differ'
        return
    a, b = _tokens(actual), _tokens(expected)
    assert len(a) == len(b), name + ': CSV field count differs'
    row = col = 0
    for (x, dx), (y, dy) in zip(a, b):
        site = name + '[%d,%d]' % (row, col)
        assert dx == dy, site + ': CSV delimiter bytes differ'
        if (row, col) in float_cells:
            assert (b'.' in y or b'e' in y.lower()) and _FLOAT.fullmatch(x) and _FLOAT.fullmatch(y), site + ': float encoding differs'
            u, v = float(x), float(y)
            assert math.isfinite(u) and math.isfinite(v), site + ': nonfinite float differs'
            assert repr(u).encode() == x and repr(v).encode() == y, site + ': noncanonical float spelling'
            assert u != 0 and v != 0 or x == y, site + ': zero spelling/sign differs'
            assert abs(_ordered(u)-_ordered(v)) <= MAX_ULP, site + ': exceeds 2 ulp'
        else:
            assert x == y, site + ': non-float bytes differ'
        if dy in (b'\n', b'\r\n'):
            row += 1
            col = 0
        else:
            col += 1


def reference_float_cells(expected, name):
    raw = (Path(__file__).with_name('data')/'regeneration-floats.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SCHEMA_SHA256, 'float schema pin changed'
    schema = json.loads(raw)['files'][name]
    tokens = _tokens(expected)
    header = []
    for field, delimiter in tokens:
        header.append(field.decode())
        if delimiter in (b'\n', b'\r\n'): break
    assert set(schema) <= set(header), 'float schema column missing'
    allowed = {j for j,key in enumerate(header) if key in schema}
    result = set()
    row = col = 0
    for field, delimiter in tokens:
        if row and col in allowed and (b'.' in field or b'e' in field.lower()) and _FLOAT.fullmatch(field):
            result.add((row,col))
        if delimiter in (b'\n', b'\r\n'): row += 1; col = 0
        else: col += 1
    return result
