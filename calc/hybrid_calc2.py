#!/usr/bin/env python3
"""Hybrid inference (server prefill, client decode), recalibrated to Ivan's M3 Max numbers.

Everything here is an estimate unless marked as a measurement or a quoted price.
Measurements (Ivan, M3 Max 128 GB, 400 GB/s):
  Flash-Next: prefill ~500 tok/s at ~150k, ~150 tok/s near 260k; decode 30-40 tok/s.
  Qwen3.8-27B: prefill ~50 tok/s at 200k+; decode ~5 tok/s (10-15 reachable, per Ivan).
"""
import math
import random

# ---------------------------------------------------------------- models
CONV = 10240 * 3  # conv state per DeltaNet layer: (2*16*128 + 48*128) channels x (kernel-1)


def state_bytes(n_linear, nbytes):
    return (n_linear * 48 * 128 * 128 + n_linear * CONV) * nbytes


MODELS = {
    "flash": dict(
        name="Flash-Next",
        kv=12 * 2 * 2 * 256 + 12 * 128 / 4,          # fp8 bytes/token: 12 QSA layers + indexer keys
        state={"bf16": state_bytes(36, 2), "fp32": state_bytes(36, 4)},
        srv_rate=50e3,                                # server prefill tok/s for one request
        flop=lambda L: 13.2e9 + 3072 * L,            # FLOP/token at depth L (sparse attention)
        dec=35.0,                                     # M3 Max decode tok/s, one stream
    ),
    "dense": dict(
        name="Qwen3.8-27B",
        kv=16 * 2 * 4 * 256,                          # fp8 bytes/token: 16 full-attention layers
        state={"bf16": state_bytes(48, 2), "fp32": state_bytes(48, 4)},
        srv_rate=20e3,
        flop=lambda L: 54e9 + 16 * 24 * 256 * 4 * L,  # dense attention in 16 layers
        dec=5.0,
    ),
}


def p_local_m3(model, L):
    """M3 Max prefill tok/s at context depth L."""
    if model == "flash":
        # Sparse attention: ~flat until the measured cliff (assumption below 150k).
        if L <= 150e3:
            return 500.0
        f = (min(L, 260e3) - 150e3) / 110e3
        return math.exp(math.log(500) + f * (math.log(150) - math.log(500)))
    # dense: constant efficiency calibrated to 50 tok/s at 200k
    m = MODELS["dense"]
    return 50.0 * m["flop"](200e3) / m["flop"](L)


TIERS = {  # (prefill multiplier, decode multiplier) vs M3 Max; estimates
    "slow~200GB/s": (0.5, 0.55),
    "M3 Max": (1.0, 1.0),
    "M5 Max(2x)": (2.0, 1.5),   # if long-context attention kernels don't use the neural accelerators
    "M5 Max(4x)": (4.0, 1.5),   # Apple MLX: up to ~4x TTFT vs M4 (base chip, 4k prompt)
    "M5 Ultra": (8.0, 2.5),
}

NETS = [  # downlink, Mbit/s
    ("50M", 50), ("100M", 100), ("200M", 200), ("300M", 300), ("500M", 500),
    ("1G", 1000), ("2.5G", 2500), ("10G", 10000),
]
EFF = 0.9      # goodput / nominal
T_FIX = 0.4    # s: scheduling, session load into HBM, RTT


def bw(mbit):
    return mbit * 1e6 / 8 * EFF


def t_local(model, tier, d, L):
    return d / (p_local_m3(model, L) * TIERS[tier][0])


def t_hybrid(model, d, L, mbit, st="bf16"):
    m = MODELS[model]
    return T_FIX + d / m["srv_rate"] + (d * m["kv"] + m["state"][st]) / bw(mbit)


def bw_needed(model, tier, d, L, gain, st="bf16"):
    """Downlink Mbit/s for the hybrid to be `gain` times faster than local prefill."""
    m = MODELS[model]
    budget = t_local(model, tier, d, L) / gain - T_FIX - d / m["srv_rate"]
    if budget <= 0:
        return float("inf")
    return (d * m["kv"] + m["state"][st]) / budget * 8 / 1e6 / EFF


# ---------------------------------------------------------------- session simulation
def sim_sessions(model, tier, mbit, L0=20e3, L1=200e3, n=300, st="bf16", seed=7, dec_mult=1.0):
    rnd = random.Random(seed)
    m = MODELS[model]
    acc = dict(pre_local=0, pre_hyb=0, dec=0, bytes=0, offl_tok=0, new_tok=0, out_tok=0,
               turns=0, cache_read=0, pre_on_mac=0, state_bytes=0)
    for _ in range(n):
        L = L0
        while L < L1:
            d = min(60e3, rnd.lognormvariate(math.log(1200), 1.2))   # tool output / file / user input
            o = min(4e3, rnd.lognormvariate(math.log(350), 0.8))     # thinking + tool call
            acc["cache_read"] += L
            tl = t_local(model, tier, d, L)
            th = t_hybrid(model, d, L, mbit, st) if mbit else float("inf")
            acc["pre_local"] += tl
            if th < tl:
                acc["pre_hyb"] += th
                acc["bytes"] += d * m["kv"] + m["state"][st]
                acc["state_bytes"] += m["state"][st]
                acc["offl_tok"] += d
            else:
                acc["pre_hyb"] += tl
                acc["pre_on_mac"] += tl
            L += d
            acc["dec"] += o / (m["dec"] * TIERS[tier][1] * dec_mult)
            L += o
            acc["new_tok"] += d
            acc["out_tok"] += o
            acc["turns"] += 1
    return {k: v / n for k, v in acc.items()}


def fmt_t(s):
    return f"{s/60:.1f}m" if s >= 100 else f"{s:.0f}s" if s >= 10 else f"{s:.1f}s"


def main():
    out = []
    p = out.append
    for k, m in MODELS.items():
        p(f"{m['name']}: KV fp8 {m['kv']/1024:.1f} KiB/tok; state bf16 {m['state']['bf16']/1e6:.1f} MB, "
          f"fp32 {m['state']['fp32']/1e6:.1f} MB; M3 Max prefill at 50/100/150/200/260k: "
          + "/".join(f"{p_local_m3(k, L*1e3):.0f}" for L in (50, 100, 150, 200, 260)))
    p("")

    # ---- Table 1: one turn, delta 10k, M3 Max, speedup by depth and network
    for model in MODELS:
        for d in (2e3, 10e3, 30e3):
            p(f"== {MODELS[model]['name']}, M3 Max, delta {d/1e3:.0f}k: prefill speedup (local time in header)")
            depths = (50e3, 100e3, 150e3, 200e3, 260e3)
            p("net    " + "".join(f"{int(L/1e3):>5}k({fmt_t(t_local(model,'M3 Max',d,L)):>5})" for L in depths))
            for lab, mb in NETS:
                row = ""
                for L in depths:
                    s = t_local(model, "M3 Max", d, L) / t_hybrid(model, d, L, mb)
                    row += f"{s:>13.1f}x"
                p(f"{lab:<6}" + row)
            p("")

    # ---- Table 2: downlink needed for break-even and for 2x/4x, by tier
    for model in MODELS:
        p(f"== {MODELS[model]['name']}: downlink Mbit/s needed (break-even / 2x / 4x), state bf16")
        for tier in TIERS:
            for L in (100e3, 200e3):
                cells = []
                for d in (2e3, 5e3, 10e3, 30e3):
                    v = [bw_needed(model, tier, d, L, g) for g in (1, 2, 4)]
                    cells.append(f"{d/1e3:.0f}k:" + "/".join("-" if x == float('inf') else f"{x:.0f}" for x in v))
                asym = MODELS[model]["kv"] * p_local_m3(model, L) * TIERS[tier][0] * 8 / 1e6 / EFF
                p(f"  {tier:<13} @{int(L/1e3)}k  " + "  ".join(cells) + f"   asymptote {asym:.0f}")
        p("")

    # ---- Table 3: full session 20k -> 200k (and 150k -> 260k), adaptive per-turn policy
    for model in MODELS:
        for (L0, L1) in ((20e3, 200e3), (150e3, 260e3)):
            p(f"== {MODELS[model]['name']}: session {int(L0/1e3)}k->{int(L1/1e3)}k, adaptive offload; "
              f"time = prefill + decode (wall, one agent)")
            for tier in TIERS:
                base = sim_sessions(model, tier, 0, L0, L1)
                tot0 = base["pre_local"] + base["dec"]
                line = (f"  {tier:<13} local {fmt_t(base['pre_local'])}+{fmt_t(base['dec'])}={fmt_t(tot0)}"
                        f" (prefill {100*base['pre_local']/tot0:.0f}%) |")
                for lab, mb in NETS:
                    if lab in ("50M", "500M", "2.5G"):
                        continue
                    r = sim_sessions(model, tier, mb, L0, L1)
                    tot = r["pre_hyb"] + r["dec"]
                    line += f" {lab}:{tot0/tot:.2f}x"
                p(line)
            r = sim_sessions(model, "M3 Max", 1000, L0, L1)
            p(f"  per session: turns {r['turns']:.0f}, new tokens {r['new_tok']/1e3:.0f}k, output {r['out_tok']/1e3:.0f}k, "
              f"cloud cache reads {r['cache_read']/1e6:.1f}M; @1G M3 offloaded {100*r['offl_tok']/r['new_tok']:.0f}% of new tokens, "
              f"download {r['bytes']/1e9:.1f} GB")
            r = sim_sessions(model, "M3 Max", 100, L0, L1)
            p(f"  @100M M3: offloaded {100*r['offl_tok']/r['new_tok']:.0f}% of new tokens, download {r['bytes']/1e9:.1f} GB")
            p("")

    # ---- decode-speed sensitivity for the dense model (Ivan: 5 now, 10-15 reachable)
    p("== Qwen3.8-27B, M3 Max, session 20k->200k, decode 5 vs 10 vs 15 tok/s")
    for dm in (1.0, 2.0, 3.0):
        base = sim_sessions("dense", "M3 Max", 0, dec_mult=dm)
        tot0 = base["pre_local"] + base["dec"]
        line = f"  decode {5*dm:.0f} tok/s: local {fmt_t(tot0)} |"
        for lab, mb in (("100M", 100), ("200M", 200), ("1G", 1000), ("10G", 10000)):
            r = sim_sessions("dense", "M3 Max", mb, dec_mult=dm)
            line += f" {lab}: {fmt_t(r['pre_hyb'] + r['dec'])} ({tot0/(r['pre_hyb']+r['dec']):.1f}x)"
        p(line)
    p("")

    # ---- big ingestion: load d tokens at once on top of a cached 20k harness prefix
    p("== Big ingestion (repo/doc/log dump) on top of cached 20k prefix: time to first token")
    for model in MODELS:
        for tier, pm in (("slow~200GB/s", None), ("M3 Max", None), ("M5 Max(2x)", None), ("M5 Max(4x)", None)):
            cells = []
            for d in (50e3, 100e3, 200e3):
                tl, L = 0.0, 20e3
                while L < 20e3 + d:
                    tl += 1e3 / (p_local_m3(model, L) * TIERS[tier][0])
                    L += 1e3
                hy = [t_hybrid(model, d, 20e3 + d, mb) for mb in (100, 200, 1000, 10000)]
                cells.append(f"{int(d/1e3)}k: local {fmt_t(tl)} | 100M {fmt_t(hy[0])} 200M {fmt_t(hy[1])} "
                             f"1G {fmt_t(hy[2])} 10G {fmt_t(hy[3])}")
            p(f"  {MODELS[model]['name']:<11} {tier:<13} " + " ;; ".join(cells))
    p("")

    # ---- multi-agent Mac capacity: 4 agents share the GPU; decode batches, prefill does not
    BATCH4 = {"flash": 1.26, "dense": 2.0}  # aggregate decode gain of 4 streams vs 1 (estimate)
    p("== Sessions (20k->200k) per 8 h of GPU time, 4 parallel agents: local-only -> hybrid @1G / @200M")
    for model in MODELS:
        for tier in TIERS:
            for dm in ((1.0, 3.0) if model == "dense" else (1.0,)):
                res = []
                for mb in (0, 1000, 200):
                    r = sim_sessions(model, tier, mb, dec_mult=dm)
                    on_mac = r["pre_local"] if mb == 0 else r["pre_on_mac"]
                    gpu = on_mac + r["dec"] / BATCH4[model]
                    res.append(8 * 3600 / gpu)
                p(f"  {MODELS[model]['name']:<11} {tier:<13} decode x{dm:.0f}: {res[0]:.0f} -> {res[1]:.0f} / {res[2]:.0f}"
                  f"  (gain {res[1]/res[0]:.2f}x / {res[2]/res[0]:.2f}x)")
    p("")

    # ---- traffic per session, state share
    p("== Download per 200k session (adaptive), state share of bytes")
    for model in MODELS:
        for st in ("bf16", "fp32"):
            for mb in (100, 200, 1000):
                r = sim_sessions(model, "M3 Max", mb, st=st)
                p(f"  {MODELS[model]['name']:<11} state {st} @{mb}M: {r['bytes']/1e9:.1f} GB, "
                  f"state {100*r['state_bytes']/max(r['bytes'],1):.0f}%, offloaded {100*r['offl_tok']/r['new_tok']:.0f}% of new tokens")
    p("")
    print("\n".join(out))
    econ()


# ---------------------------------------------------------------- economics
PRICES = {  # $/M tokens: input, output, cache read, cache write
    "Sonnet 5.5": (2.0, 10.0, 0.20, 2.5),     # write = 1.25 x input (assumed standard multiplier)
    "Opus 5.5": (4.0, 20.0, 0.20, 5.0),
    "Fable 5.1": (10.0, 50.0, 0.25, 12.5),
    "Flash-Next API": (0.15, 0.47, 0.016, 0.15),  # QwenCloud list via aggregators; write assumed = input
    "27B API": (0.50, 3.00, 0.05, 0.50),          # Alibaba intl list via aggregator (Oct 2026)
}
NODE_MONTH = 650e3 * 1.2 / 48 + 54e3 / 12   # B300 node: book price + 20% infra, 4 y, opex $54k/y
GPU_H = NODE_MONTH / (8 * 730)               # $/GPU-hour at 100% use
EFF_PF = 4.5e15 * 0.30                       # FP8 dense x MFU, FLOP/s per GPU


def econ():
    out = []
    p = out.append
    r = sim_sessions("flash", "M3 Max", 1000)
    tok_in, tok_out, cr = r["new_tok"], r["out_tok"], r["cache_read"]
    p(f"== Economics per 200k-class session (new {tok_in/1e3:.0f}k, out {tok_out/1e3:.0f}k, cache reads {cr/1e6:.1f}M)")
    p(f"   own B300 node: ${NODE_MONTH:,.0f}/month -> ${GPU_H:.2f}/GPU-h at 100% use")
    per = {}
    for k, (pi, po, pr, pw) in PRICES.items():
        c = cr / 1e6 * pr + (tok_in + tok_out) / 1e6 * pw + tok_out / 1e6 * po
        c_miss = c + 0.10 * r["turns"] * (cr / r["turns"]) / 1e6 * (pw - pr)  # 10% turns re-write prefix
        per[k] = c
        p(f"   {k:<15} ${c:6.2f}/session (with 10% cache misses ${c_miss:6.2f}); x840/month = ${840*c:,.0f}")
    for model in MODELS:
        m = MODELS[model]
        avg_L = 110e3
        gpu_s = (tok_in + tok_out) * m["flop"](avg_L) / EFF_PF
        for util in (1.0, 0.16):
            c = gpu_s / 3600 * GPU_H / util
            p(f"   hybrid prefill {m['name']:<11} {gpu_s:5.1f} GPU-s/session, util {util:.0%}: ${c:.3f}/session, x840 = ${840*c:,.0f}/month")
    # own all-server cluster: prefill + decode + KV residency in HBM (estimate)
    life = 2700.0                  # s, wall lifetime of a 20k->200k session served from the DC
    hbm_gpu = 240e9                # usable HBM per B300 for KV after weights/workspace
    dec_gpu = {"flash": 13.7e3, "dense": 1.8e3}   # tok/s per GPU at the batch HBM allows (estimate)
    for model in MODELS:
        m = MODELS[model]
        pre = (tok_in + tok_out) * m["flop"](110e3) / EFF_PF
        dec = tok_out / dec_gpu[model]
        res = 110e3 * m["kv"] * life / hbm_gpu
        gs = pre + dec + res
        cells = ", ".join(f"util {u:.0%}: ${840*gs/3600*GPU_H/u:,.0f}/month" for u in (0.5, 0.25))
        p(f"   own cluster {m['name']:<11} prefill {pre:.0f} + decode {dec:.0f} + KV residency {res:.0f} = {gs:.0f} GPU-s/session; {cells}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
