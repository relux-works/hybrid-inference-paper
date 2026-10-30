"""Recalibration on Ivan's measured agent-session usage (ivmbp, 2026-10-30).

Source: .temp/a2a-in/ivmbp-stats-20261030/x/ivmbp-session-stats-20261030/stats.json (agent_session_stats v1.4-local-audit,
1,524,671 unique calls in 13,169 contexts: Claude Code, Codex, Muse). These are frontier-model sessions; we use them as
the call mix the open model would face in the same harnesses.

Sampler (per call, independent draws; session structure is not needed for per-call costs):
  * depth L: bin chosen with the measured call counts (<50k, 50-100k, 100-200k, 200k+); uniform inside a bin,
    the 200k+ bin follows the measured tail (p90 250k, p99 826k of all calls);
  * new tokens d: lognormal per depth bin, fitted to the bin's measured median and mean (mean is preserved);
  * output o and reasoning r: lognormal fitted to the measured median and mean; decode load = o + r;
    the server shadow-prefills o + r as well (conservative: some harnesses drop reasoning from the context);
  * tool time tau: as in hybrid_calc3 (lognormal, median 2 s).
Outputs: the hybrid_calc4 section-6 costing per 1000 calls, synthetic 20k->200k next to the measured call mix.
Run: python3 hybrid_calc7_realcalls.py > hybrid_calc7_realcalls.out
"""
import json
import math
import os
import random

import hybrid_calc3 as c3
import hybrid_calc4 as c4

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [
    os.path.join(_HERE, "..", "data", "measurements", "ivmbp-2026-10-30", "stats.json"),          # paper repository layout
    os.path.join(_HERE, "..", ".temp", "a2a-in", "ivmbp-stats-20261030", "x",
                 "ivmbp-session-stats-20261030", "stats.json"),                                    # lane working copy
]
STATS = next((c for c in _CANDIDATES if os.path.exists(c)), _CANDIDATES[0])


def lognorm_mean_median(rnd, median, mean, cap):
    if median <= 0:
        median = 1.0
    sigma = math.sqrt(2 * math.log(max(mean / median, 1.0001)))
    return min(cap, rnd.lognormvariate(math.log(median), sigma))


def make_real_calls(a, n_calls=40000, chunk=116, seed=5):
    rnd = random.Random(seed)
    bins = a["new_in_by_depth"]
    names = ["<50k", "50-100k", "100-200k", "200k+"]
    weights = [bins[b]["n"] for b in names]
    ranges = {"<50k": (a["first_call_prompt"]["p25"], 50e3), "50-100k": (50e3, 100e3), "100-200k": (100e3, 200e3)}
    out, cur = [], []
    o_med, o_mean = a["output_per_call"]["p50"], a["output_per_call"]["mean"]
    r_med, r_mean = max(1.0, a["reasoning_per_call"]["p50"]), a["reasoning_per_call"]["mean"]
    tail_p90, tail_p99 = a["depth_per_call"]["p90"], a["depth_per_call"]["p99"]
    share_200 = bins["200k+"]["n"] / sum(weights)
    for _ in range(n_calls):
        b = rnd.choices(names, weights)[0]
        if b == "200k+":
            u = rnd.random()
            above90 = 0.10 / share_200            # share of the 200k+ bin above the overall p90
            above99 = 0.01 / share_200
            if u < 1 - above90:
                L = rnd.uniform(200e3, tail_p90)
            elif u < 1 - above99:
                L = math.exp(rnd.uniform(math.log(tail_p90), math.log(tail_p99)))
            else:
                L = rnd.uniform(tail_p99, 1.0e6)
        else:
            L = rnd.uniform(*ranges[b])
        d = lognorm_mean_median(rnd, bins[b]["p50"], bins[b]["mean"], 120e3)
        o = lognorm_mean_median(rnd, o_med, o_mean, 16e3)
        r = lognorm_mean_median(rnd, r_med, r_mean, 16e3)
        tau = rnd.lognormvariate(math.log(2.0), 1.0)
        cur.append((L, d, o + r, tau))
        if len(cur) == chunk:
            out.append(cur)
            cur = []
    return out


def describe(p, label, sessions):
    calls = [t for s in sessions for t in s]
    ds = sorted(t[1] for t in calls)
    Ls = sorted(t[0] for t in calls)
    os_ = sorted(t[2] for t in calls)
    tot = sum(ds)
    q = lambda xs, f: xs[min(len(xs) - 1, int(f * len(xs)))]
    shares = {th: sum(x for x in ds if x >= th) / tot for th in (2e3, 5e3, 10e3, 30e3)}
    p(f"  {label}: {len(calls)} calls; d p50/p90/mean {q(ds,.5):.0f}/{q(ds,.9):.0f}/{tot/len(ds):.0f}; "
      f"depth p50/p90/p99/mean {q(Ls,.5)/1e3:.0f}k/{q(Ls,.9)/1e3:.0f}k/{q(Ls,.99)/1e3:.0f}k/{sum(Ls)/len(Ls)/1e3:.0f}k; "
      f"decoded (o+r) p50/mean {q(os_,.5):.0f}/{sum(os_)/len(os_):.0f}; "
      f"share of new tokens in calls >=2k/5k/10k/30k: " + "/".join(f"{100*v:.0f}%" for v in shares.values()))


def costing(p, label, SS, gpx, Lk=250e3):
    nt = sum(map(len, SS)) / len(SS)
    p(f"  {label}:")
    for model in ("dense", "flash"):
        m = c3.MODELS[model]
        api_names = ("27B API median", "Haiku 5.5", "Sonnet 5.5", "Opus 5.5") if model == "dense" else ("Flash API (Alibaba)",)
        api_t = ", ".join(f"{a.replace(' API median', '')} ${c3.api_cost(a, SS)/nt*1000:.1f}" for a in api_names)
        own = c4.own_gpu_s(model, SS, False, c4.UNIT["b300"])
        own_r = sum(own) / nt
        p(f"    {m['name']}: API {api_t} | own ${own_r*1000*gpx:.1f} per 1000 calls"
          f" (GPU-s/call prefill {own[0]/nt:.3f} + decode {own[1]/nt:.3f} + KV residency {own[2]/nt:.3f})")
        for key in ("m5max64", "m5max", "ultra96"):
            dev = c4.DEV[key]
            K = min(c3.k_mem(model, dev, Lk), 8)
            if K == 0:
                p(f"      {dev.label}: does not fit at {Lk/1e3:.0f}k"); continue
            cells = []
            for mb in (100, 200, 1000):
                rr = c3.run(model, dev, mb, K, SS)
                calls8 = rr["per8h"] * nt
                prem = dev.price[1] - (c4.BASELINE_LAPTOP if key.startswith("m5max") else 0)
                dev_t = prem * (1 - c4.MAC_RESID[4]) / (48 * c4.DAYS_MONTH) / calls8 * 1000
                srv_t = rr["srv_gpu"] / nt * 1000 * gpx
                eg_t = rr["bytes"] / nt * 1000 / 1e12 * c4.EGRESS_TB
                cells.append(f"{mb}M: {calls8:,.0f} calls/8h, offloaded {100*rr['offl']/max(rr['new'],1):.0f}% of new tokens,"
                             f" {rr['bytes']/nt*1000/1e9:.1f} GB/1000 calls, ${srv_t:.1f}+{eg_t:.1f}+{dev_t:.1f}=${srv_t+eg_t+dev_t:.1f}")
            loc = c3.run(model, dev, 0, K, SS)
            p(f"      {dev.label} K{K} (local only {loc['per8h']*nt:,.0f} calls/8h): " + " | ".join(cells))


def main():
    out = []
    p = out.append
    stats = json.load(open(STATS))
    a = stats["agents"]["all"]
    gpx = c4.demand_gpu_s_price(c4.UNIT["b300"])
    S80 = c3.make_sessions()[:80]
    R = make_real_calls(a)
    p("== 1. Call mix: synthetic sessions (hybrid_calc3) vs the sampler fitted to Ivan's measured calls")
    p(f"  measured (all agents): d p50/p90/mean {a['new_in_per_call']['p50']:.0f}/{a['new_in_per_call']['p90']:.0f}/"
      f"{a['new_in_per_call']['mean']:.0f}; depth p50/p90/p99/mean {a['depth_per_call']['p50']/1e3:.0f}k/"
      f"{a['depth_per_call']['p90']/1e3:.0f}k/{a['depth_per_call']['p99']/1e3:.0f}k/{a['depth_per_call']['mean']/1e3:.0f}k;"
      f" output+reasoning mean {a['output_per_call']['mean']+a['reasoning_per_call']['mean']:.0f};"
      f" share of new tokens in calls >=2k/5k/10k/30k: " + "/".join(f"{100*v:.0f}%" for v in a["share_of_new_tokens_in_calls"].values()))
    describe(p, "synthetic 20k->200k", S80)
    describe(p, "sampled from measurements", R)
    p("")
    p(f"== 2. Cost per 1000 agent calls (B300 priced per GPU-s of demand ${gpx*3600:.2f}/GPU-h; egress $5/TB;"
      " Mac premium or Ultra price over 4 years at 8 h/day); K chosen for 250k depth")
    costing(p, "synthetic 20k->200k", S80, gpx)
    costing(p, "measured call mix", R, gpx)
    print("\n".join(out))


if __name__ == "__main__":
    main()
