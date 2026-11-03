"""Cooled kit1.6.6 medians; largest-np base and explicit sensitivities."""
import hashlib
import json
from pathlib import Path
from statistics import median

from .inputs import InputGap, ROOT
from .measurements_r13 import rows, verified_archive
from .measurements_r14 import ParallelAnchors as PreviousAnchors
from .measurements_r14 import aggregate_round, one_file, package as previous_package, raw_table


CONFIG = Path(__file__).parent/'data/run15-measurements.json'


def package():
    info = json.loads(CONFIG.read_text())
    return verified_archive(ROOT/info['path'], info['sha256'])


def record_package(inputs):
    info = json.loads(CONFIG.read_text())
    manifest, payload = package()
    provenance = dict(kind='measured', package=manifest['kit']+' '+manifest['kit_version'],
                      sha256=info['sha256'], protocol=info['protocol'])
    for name, content in [(info['path'], (ROOT/info['path']).read_bytes()),
                          (str(CONFIG.relative_to(ROOT)), CONFIG.read_bytes())]:
        inputs.files[name] = dict(path=name, sha256=hashlib.sha256(content).hexdigest(), provenance=provenance)
    for name, content in payload.items():
        source = info['path']+'::'+name
        inputs.files[source] = dict(path=source, sha256=hashlib.sha256(content).hexdigest(), provenance=provenance)


def cooled_points(payload, fragment, depth, server_np, counts):
    """Require all three restored rounds; never reduce a subset or a summary."""
    name, content = one_file(payload, fragment)
    records = rows(content)
    rounds = [r for r in records if r.get('kind') == 'round']
    if {r['streams'] for r in rounds} != set(counts):
        raise InputGap('measurements.parallel', 'incomplete cooled stream grid')
    points = []
    for count in counts:
        group = sorted((r for r in rounds if r['streams'] == count), key=lambda r:r['round'])
        if (len(group) != 3 or [r['round'] for r in group] != [1,2,3] or
                any(r['depth'] != depth or r['server_np'] != server_np or
                    any(q.get('prompt_n') != 16 for q in r['requests']) for r in group)):
            raise InputGap('measurements.parallel', 'three restored rounds at the required largest-np shape required')
        rates = [aggregate_round(r) for r in group]
        points.append(dict(depth=depth, streams=count, aggregate_tok_s=median(rates), source=name,
                           condition='kit1.6.6; cooled 300s; restored every round; largest-np base; q8_0 KV; FA on',
                           conservative=False, server_np=server_np, rounds=3,
                           round_aggregate_tok_s='; '.join(format(v,'.17g') for v in rates),
                           payload_sha256=hashlib.sha256(content).hexdigest()))
    return points


class ParallelAnchors(PreviousAnchors):
    """Reuse R14 lookup rules, replacing only the admitted measurement set."""
    def __init__(self, normalized, depth_law=None):
        super().__init__(normalized, depth_law)
        old = self.points
        # Step56's actual 260k observations are the deepest base anchors.
        self.points = [dict(p) for p in old if p['depth'] == 260016]
        self.historical = [dict(p, sensitivity='historical; excluded from R15 base')
                           for p in old if p['depth'] != 260016]
        # R14 preferred the restored control; retain *all* old step55 128k
        # observations, including those it did not select for its own base.
        name, content = one_file(previous_package('mac')[1], '-depth128k-')
        for r in rows(content):
            if r.get('kind') == 'round' and r['streams'] != 12:
                self.historical.append(dict(depth=r['depth'], streams=r['streams'],
                    aggregate_tok_s=aggregate_round(r), source=name, conservative=True,
                    condition='step55; old build; immediately after long prefill',
                    sensitivity='historical; excluded from R15 base'))
        _, payload = package()
        grid = (1,2,4,8,12,16,24,32)
        for prefix, depth, np, counts in (('32768-largest-np32-',32784,32,grid),
                                        ('65536-largest-np32-',65552,32,grid),
                                        ('131072-largest-np16-',131088,16,grid[:6])):
            self.points.extend(cooled_points(payload, '-scale'+prefix, depth, np, counts))
        for p in self.points:
            p.setdefault('server_np', 8)
            p.setdefault('rounds', 1)
            p.setdefault('round_aggregate_tok_s', format(p['aggregate_tok_s'],'.17g'))
            if 'payload_sha256' not in p:
                content = previous_package('mac')[1][p['source']]
                p['payload_sha256'] = hashlib.sha256(content).hexdigest()
        control = cooled_points(payload, '-scale131072-np4-control-np4-',131088,4,(4,))[0]
        base = next(p for p in self.points if p['depth']==131088 and p['streams']==4)
        self.shape_sensitivity = [dict(depth=131088, streams=4, base_np=16, control_np=4,
            base_aggregate_tok_s=base['aggregate_tok_s'], control_aggregate_tok_s=control['aggregate_tok_s'],
            ratio=control['aggregate_tok_s']/base['aggregate_tok_s'],
            condition='server-shape sensitivity only; base uses largest-np shape',
            source=control['source'], round_aggregate_tok_s=control['round_aggregate_tok_s'],
            payload_sha256=control['payload_sha256'])]
        self.points.sort(key=lambda p:(p['streams'],p['depth']))


def append_sensitivities(result, c):
    raw_table(result, 'parallel_historical_sensitivity', c.parallel.historical,
              dict(depth='token',streams='stream',aggregate_tok_s='token/s',source='text',
                   condition='text',conservative='bool',sensitivity='text'))
    raw_table(result, 'parallel_server_shape_sensitivity', c.parallel.shape_sensitivity,
              dict(depth='token',streams='stream',base_np='slot',control_np='slot',
                   base_aggregate_tok_s='token/s',control_aggregate_tok_s='token/s',ratio='1',
                   condition='text',source='text',round_aggregate_tok_s='token/s by round',payload_sha256='sha256'))
