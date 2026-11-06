"""Hash-checked PRI31 Mac evidence and explicitly bounded curve estimates."""
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from hybridcalc.inputs import InputGap
from hybridcalc import measurements_r18 as r18

DATA = Path(__file__).parent / 'data'
BF16 = 78446592
F32 = 156893184
KV = 34816


def state_bytes(transport='bf16'):
    if transport not in ('bf16', 'f32'):
        raise InputGap('run22.transport', 'bf16 default or explicit f32 control required')
    return BF16 if transport == 'bf16' else F32


def wire(delta, transport='bf16'):
    r18.positive(delta, 'delta')
    return delta * KV + state_bytes(transport)


def priority(manifest, readiness):
    if (manifest.get('normal_priority') is not True or
            manifest.get('priority_override_used') is not False or
            str(manifest.get('ctx_checkpoints')) != '0' or
            readiness.get('normal_priority') is not True or readiness.get('override_used') is not False):
        raise InputGap('run22.priority', 'recorded normal priority without overrides required')
    samples = readiness.get('samples', [])
    servers = [s for row in samples for s in row.get('servers', [])]
    # OS ancestors (Terminal/launchd) need not have the server scheduling PRI.
    if not servers or any(s.get('pri') != 31 or s.get('nice') != 0 or s.get('errors') for s in servers):
        raise InputGap('run22.priority', 'every recorded llama-server sample must be PRI31 nice0')
    if any(row.get('violations') or not row.get('normal_priority') for row in samples):
        raise InputGap('run22.priority', 'readiness violation or missing normal-priority sample')
    return len(samples)


@lru_cache(maxsize=2)
def evidence(model):
    info = json.loads((DATA / 'evidence.json').read_text())[model]
    for name, expected in info['files'].items():
        if hashlib.sha256((DATA / name).read_bytes()).hexdigest() != expected:
            raise InputGap('run22.evidence', 'Mac evidence SHA256 mismatch: ' + name)
    root = DATA / model
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    readiness = json.loads((root / 'OPERATOR-READINESS.json').read_text())
    priority(manifest, readiness)
    files = {}
    for name in info['files']:
        p = DATA / name
        if p.suffix == '.jsonl':
            raw = p.read_bytes()
            entry = manifest['files'].get(p.name)
            if not entry or entry['sha256'] != hashlib.sha256(raw).hexdigest() or entry['bytes'] != len(raw):
                raise InputGap('run22.evidence', 'kit manifest member mismatch')
            files[p.name] = [json.loads(line) for line in raw.splitlines()]
    return manifest, readiness, files


class Mac:
    def __init__(self, model='qwen', client='m5max64'):
        if model not in ('qwen', 'glimmer') or client not in ('m5max64', 'm5max', 'm3max'):
            raise InputGap('run22.mac', 'unknown Mac/model')
        if client == 'm3max' and model != 'glimmer':
            raise InputGap('run22.mac', 'M3 Qwen uses the existing PRI31 surface')
        self.model = model
        self.client = client
        self.limit = 1048576 if model == 'qwen' else 131072
        self.turns = {n: [] for n in (512, 2000, 10000)}
        self.parallel = {}
        if client == 'm3max':
            facts = json.loads((DATA / 'evidence.json').read_text())['facts']
            if hashlib.sha256((DATA / facts['path']).read_bytes()).hexdigest() != facts['sha256']:
                raise InputGap('run22.evidence', 'FACTS transcription source changed')
            # Accepted FACTS transcription; strict archive is not on agents1.
            for depth, rates in ((16000, (167.7,173.5,158.4)), (50000,(120.2,107.3,99.0)),
                                 (100000,(80.9,71.2,66.2)), (118000,(66.9,67.4,65.8))):
                start = depth
                for n, rate in zip(self.turns, rates):
                    self.turns[n].append((start, 1/rate))
                    start += n + 128
            self.basis = 'accepted FACTS PRI31 rounded transcription; incident archive copy pending; actual successive-turn start reconstructed'
            return
        _, _, files = evidence(model)
        for name, rows in files.items():
            if 'hybrid-bench' in name:
                for row in rows:
                    if row.get('kind') == 'turn':
                        if row.get('reread') or row.get('truncated') or row['prompt_n'] not in (row['delta'],row['delta']+1):
                            raise InputGap('run22.ladder', 'exact cached delta without reread required')
                        self.turns[row['delta']].append((row['depth'], row['prompt_ms']/1000/row['delta']))
            if 'largest' in name or 'maxctx' in name:
                for row in rows:
                    if row.get('kind') == 'summary' and row['valid']:
                        self.parallel.setdefault(row['streams'], []).append((row['depth'], row['median_aggregate_tok_s']))
        if any(not points for points in self.turns.values()) or not self.parallel:
            raise InputGap('run22.ladder', 'missing measured ladder or parallel curve')
        for points in list(self.turns.values()) + list(self.parallel.values()):
            points.sort()
        self.basis = 'kit1.6.7 recorded PRI31 nice0; elapsed-time interpolation at actual turn start; outside measured shapes estimated'
        if client == 'm5max':
            self.basis += '; same-SoC 128GB portability assumption, not a 128GB measurement'

    def prefill(self, depth, delta=2000):
        """Seconds; interpolation in elapsed time, FLOP-efficiency tail extension."""
        if depth < 0 or delta < 0 or depth + delta > self.limit:
            raise InputGap('run22.mac', 'Mac context envelope exceeded')
        if delta == 0:
            return 0.0
        if delta > 10000:
            n = min(delta, 10000)
            return self.prefill(depth,n) + self.prefill(depth+n,delta-n)
        seconds = []
        for n, points in self.turns.items():
            anchor = min(depth, points[-1][0])
            per_token = r18.interpolate(points, anchor)
            if depth > points[-1][0]:
                # Qwen only: Glimmer is capacity-bound at its native window.
                per_token *= (54e9+393216*depth)/(54e9+393216*points[-1][0])
            seconds.append((n, per_token*delta))
        # Endpoint per-token holds for sub512 deltas are an explicit estimate.
        return r18.interpolate(sorted(seconds), delta)

    def decode(self, streams, depth):
        """Per-stream tok/s; measured curves, labelled traffic-model tails."""
        if streams not in self.parallel or not 0 <= depth <= self.limit:
            raise InputGap('run22.decode', 'unmeasured client stream count or context envelope')
        points = self.parallel[streams]
        anchor = min(depth, points[-1][0])
        aggregate = r18.interpolate(points, anchor)
        if depth > points[-1][0]:
            kv = KV if self.model == 'qwen' else 7072
            fixed = F32 if self.model == 'qwen' else 21216*2048
            weights = 18.97e9 if self.model == 'qwen' else 17e9
            aggregate *= (weights+streams*(kv*anchor+fixed))/(weights+streams*(kv*depth+fixed))
        return aggregate/streams


def measurement_rows():
    out = []
    for model in ('qwen','glimmer'):
        manifest, readiness, files = evidence(model)
        for name, rows in files.items():
            for index, row in enumerate(rows):
                if row.get('kind') not in ('turn','segment','summary','round','prefill'):
                    continue
                # Summary rows, not their repeated rounds, feed pure decode curves.
                if row['kind'] == 'round' and 'agents-loop' not in name:
                    continue
                one=next((x['median_aggregate_tok_s'] for x in rows if x.get('kind')=='summary' and x['streams']==1),None)
                out.append(dict(model=model,client='m5max64',source=name,source_row=index,
                    protocol='agents_loop' if 'agents-loop' in name else 'step40' if 'hybrid-bench' in name else 'parallel_depth',
                    depth=row.get('depth',row.get('level',0)),delta=row.get('delta',0),
                    streams=row.get('streams',1),prefill_tok_s=row.get('prefill_tok_s',row.get('mean_prefill_tok_s','')),
                    aggregate_decode_tok_s=row.get('median_aggregate_tok_s',row.get('aggregate_decode_tok_s','')),
                    single_decode_tok_s=row.get('decode_tok_s',''),
                    calls=row.get('calls',''),elapsed_s=row.get('elapsed_s',''),
                    call_wall_p50_s=row.get('call_wall_p50_s',''),call_wall_p90_s=row.get('call_wall_p90_s',''),
                    projected_continuous_calls_8h=(row['calls']/row['elapsed_s']*28800 if row.get('calls') and row.get('elapsed_s') else ''),
                    gain=(row['median_aggregate_tok_s']/one if row['kind']=='summary' and one else ''),
                    normal_priority=True,priority_samples=len(readiness['samples']),model_sha256=manifest['model_sha256'],
                    basis='measured; step40 successive turn starts; step55 cooled medians; step56 one round; agents loop includes scheduling, not pure batching'))
    decode={16000:(13.77,16.3,15.33),50000:(10.37,10.34,9.51),100000:(9.57,9.04,8.36),118000:(9.01,8.82,10.0)}
    m3=Mac('glimmer','m3max')
    for j,n in enumerate((512,2000,10000)):
        for (depth,per_token),(nominal,rates) in zip(m3.turns[n],decode.items()):
            out.append(dict(model='glimmer',client='m3max',source='FACTS-excerpts.md',source_row='accepted nominal depth'+str(nominal),
                protocol='step40 successive turns, accepted transcription',depth=depth,delta=n,streams=1,prefill_tok_s=1/per_token,
                aggregate_decode_tok_s='',single_decode_tok_s=rates[j],calls='',elapsed_s='',call_wall_p50_s='',call_wall_p90_s='',
                projected_continuous_calls_8h='',gain='',normal_priority=True,priority_samples='',model_sha256='4cc57c0f...3f60e (FACTS)',
                basis='accepted PRI31 FACTS transcription replaces background interim; rounded rates, strict archive unavailable; no pure-decode parallel claim'))
    return out


def quality_rows():
    info=json.loads((DATA/'evidence.json').read_text())['bf16_ruler']
    out=[dict(evidence='bf16 KL study',value=-.000298,ci_low=-.001076,ci_high=.000390,unit='nats relative to local',
        local_own_KL=.054253,answer_changes='',source='FACTS KL study8d876c71;20 documents40960 positions',
        basis='accepted paired result;95% interval includes0, not universal equivalence')]
    for name,expected in info['analyses'].items():
        raw=(DATA/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:
            raise InputGap('run22.quality','BF16 RULER analysis SHA256 mismatch')
        total=next(r for r in json.loads(raw) if r['task']=='ALL')
        if total['n']!=390 or total['bf16_local_score_disagreements']!=0 or total['bf16_f32_score_disagreements']!=0:
            raise InputGap('run22.quality','accepted paired-score contract changed')
        out.append(dict(evidence='bf16 RULER'+str(total['depth']),value=390,ci_low='',ci_high='',unit='paired scores equal out of390',
            local_own_KL='',answer_changes=total['bf16_answer_changes'],source=name,
            basis='accepted primary analysis, same examples/seed and frozen local/f32 baselines; score equality does not mean identical answers or100% accuracy; homogeneous CUDA quality evidence, not a universal vLLM-to-Metal calibration'))
    return out
