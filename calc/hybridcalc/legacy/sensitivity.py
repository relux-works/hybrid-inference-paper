from ..inputs import legacy_values, measurement_path
V = legacy_values('sensitivity')

#!/usr/bin/env python3
"""Capacity under the turn distribution measured on agents1 sessions (2026-10-29, local-02.json):
new input per call p50 ~330 (p50 ~1.4k below 50k depth, ~300-450 deeper), output p50 ~320 / mean ~700,
first prompt p50 ~44k. Compared with the v3 default (delta p50 1.2k everywhere, output p50 350)."""
import math, random, sys, os
from . import sessions as c

def host_sessions(n=V['host_sessions_L9_20'], L0=V['host_sessions_L9_27'], L1=V['host_sessions_L9_36'], seed=V['host_sessions_L9_48']):
    rnd = random.Random(seed); out = []
    for _ in range(n):
        L, turns = L0, []
        while L < L1:
            med = V['med_L14_18'] if L < V['med_L14_30'] else V['med_L14_40']
            d = min(V['d_L15_20'], rnd.lognormvariate(math.log(med), V['d_L15_60']))
            o = min(V['o_L16_20'], rnd.lognormvariate(math.log(V['o_L16_53']), V['o_L16_59']))
            tau = rnd.lognormvariate(math.log(2.0), 1.0)
            turns.append((L, d, o, tau)); L += d + o
        out.append(turns)
    return out

def main():
    S0, S1 = c.make_sessions(n=V['_S0__S1__L22_27']), host_sessions()
    print(f"turns per session: v3 default {sum(map(len,S0))/len(S0):.0f}, host sample {sum(map(len,S1))/len(S1):.0f}")
    for model, prof in (("dense", "tuned"), ("flash", "tuned")):
        for key, K in (("m5pro", V['module_L25_29']), ("m3max", V['module_L25_43']), ("m5max", V['module_L25_57']), ("ultra96", V['module_L25_73'])):
            dev = c.DEV[key]
            if c.k_mem(model, dev, V['module_L27_31']) < K:
                continue
            cells = []
            for lab, SS in (("default", S0), ("host", S1)):
                v = [c.run(model, dev, mb, K, SS, profile=prof)["per8h"] for mb in (0, V['v_L31_83'], 1000)]
                cells.append(f"{lab}: {v[0]:.1f} -> {v[1]:.1f} / {v[2]:.1f} (x{v[2]/v[0]:.2f})")
            print(f"  {c.MODELS[model]['name']:<11} {dev.label:<24} K{K}  " + " | ".join(cells))
    for name in ("27B API median", "Flash API (Alibaba)", "Haiku 5.5", "Sonnet 5.5"):
        print(f"  API {name:<20} per session: default ${c.api_cost(name, S0):.3f}, host ${c.api_cost(name, S1):.3f}")
    for model in ("dense", "flash"):
        r0, r1 = c.run(model, c.DEV["m3max"], V['_r0__r1__L37_42'], V['_r0__r1__L37_47'], S0), c.run(model, c.DEV["m3max"], V['_r0__r1__L37_84'], V['_r0__r1__L37_89'], S1)
        print(f"  hybrid server {c.MODELS[model]['name']}: GPU-s {r0['srv_gpu']:.1f} vs {r1['srv_gpu']:.1f}; download GB {r0['bytes']/1e9:.1f} vs {r1['bytes']/1e9:.1f}")
