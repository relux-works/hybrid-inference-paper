from ..inputs import legacy_values, measurement_path
V = legacy_values('v2')

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
CONV = V['CONV_L13_7'] * V['CONV_L13_15']  # conv state per DeltaNet layer: (2*16*128 + 48*128) channels x (kernel-1)


def state_bytes(n_linear, nbytes):
    return (n_linear * V['state_bytes_L17_23'] * V['state_bytes_L17_28'] * V['state_bytes_L17_34'] + n_linear * CONV) * nbytes


MODELS = {
    "flash": dict(
        name="Flash-Next",
        kv=V['MODELS_L23_11'] * 2 * 2 * V['MODELS_L23_24'] + V['MODELS_L23_30'] * V['MODELS_L23_35'] / V['MODELS_L23_41'],          # fp8 bytes/token: 12 QSA layers + indexer keys
        state={"bf16": state_bytes(V['MODELS_L24_35'], 2), "fp32": state_bytes(V['MODELS_L24_63'], V['MODELS_L24_67'])},
        srv_rate=V['MODELS_L25_17'],                                # server prefill tok/s for one request
        flop=lambda L: V['MODELS_L26_23'] + V['MODELS_L26_32'] * L,            # FLOP/token at depth L (sparse attention)
        dec=V['MODELS_L27_12'],                                     # M3 Max decode tok/s, one stream
    ),
    "dense": dict(
        name="Qwen3.8-27B",
        kv=V['MODELS_L31_11'] * 2 * V['MODELS_L31_20'] * V['MODELS_L31_24'],                          # fp8 bytes/token: 16 full-attention layers
        state={"bf16": state_bytes(V['MODELS_L32_35'], 2), "fp32": state_bytes(V['MODELS_L32_63'], V['MODELS_L32_67'])},
        srv_rate=V['MODELS_L33_17'],
        flop=lambda L: V['MODELS_L34_23'] + V['MODELS_L34_30'] * V['MODELS_L34_35'] * V['MODELS_L34_40'] * V['MODELS_L34_46'] * L,  # dense attention in 16 layers
        dec=V['MODELS_L35_12'],
    ),
}


def p_local_m3(model, L):
    """M3 Max prefill tok/s at context depth L."""
    if model == "flash":
        # Sparse attention: ~flat until the measured cliff (assumption below 150k).
        if L <= V['p_local_m3_L44_16']:
            return V['p_local_m3_L45_19']
        f = (min(L, V['f_L46_20']) - V['f_L46_29']) / V['f_L46_38']
        return math.exp(math.log(V['p_local_m3_L47_33']) + f * (math.log(V['p_local_m3_L47_54']) - math.log(V['p_local_m3_L47_70'])))
    # dense: constant efficiency calibrated to 50 tok/s at 200k
    m = MODELS["dense"]
    return V['p_local_m3_L50_11'] * m["flop"](V['p_local_m3_L50_28']) / m["flop"](L)


TIERS = {  # (prefill multiplier, decode multiplier) vs M3 Max; estimates
    "slow~200GB/s": (V['TIERS_L54_21'], V['TIERS_L54_26']),
    "M3 Max": (1.0, 1.0),
    "M5 Max(2x)": (2.0, V['TIERS_L56_24']),   # if long-context attention kernels don't use the neural accelerators
    "M5 Max(4x)": (V['TIERS_L57_19'], V['TIERS_L57_24']),   # Apple MLX: up to ~4x TTFT vs M4 (base chip, 4k prompt)
    "M5 Ultra": (8.0, V['TIERS_L58_22']),
}

NETS = [  # downlink, Mbit/s
    ("50M", V['NETS_L62_12']), ("100M", V['NETS_L62_26']), ("200M", V['NETS_L62_41']), ("300M", V['NETS_L62_56']), ("500M", V['NETS_L62_71']),
    ("1G", 1000), ("2.5G", V['NETS_L63_27']), ("10G", V['NETS_L63_42']),
]
EFF = V['EFF_L65_6']      # goodput / nominal
T_FIX = V['T_FIX_L66_8']    # s: scheduling, session load into HBM, RTT


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
def sim_sessions(model, tier, mbit, L0=V['sim_sessions_L92_39'], L1=V['sim_sessions_L92_48'], n=V['sim_sessions_L92_57'], st="bf16", seed=V['sim_sessions_L92_78'], dec_mult=V['sim_sessions_L92_90']):
    rnd = random.Random(seed)
    m = MODELS[model]
    acc = dict(pre_local=V['acc_L95_25'], pre_hyb=V['acc_L95_36'], dec=V['acc_L95_43'], bytes=V['acc_L95_52'], offl_tok=V['acc_L95_64'], new_tok=V['acc_L95_75'], out_tok=V['acc_L95_86'],
               turns=V['acc_L96_21'], cache_read=V['acc_L96_35'], pre_on_mac=V['acc_L96_49'], state_bytes=V['acc_L96_64'])
    for _ in range(n):
        L = L0
        while L < L1:
            d = min(V['d_L100_20'], rnd.lognormvariate(math.log(V['d_L100_54']), V['d_L100_61']))   # tool output / file / user input
            o = min(V['o_L101_20'], rnd.lognormvariate(math.log(V['o_L101_53']), V['o_L101_59']))     # thinking + tool call
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
    return f"{s/60:.1f}m" if s >= V['fmt_t_L124_34'] else f"{s:.0f}s" if s >= V['fmt_t_L124_63'] else f"{s:.1f}s"


def main():
    out = []
    p = out.append
    for k, m in MODELS.items():
        p(f"{m['name']}: KV fp8 {m['kv']/1024:.1f} KiB/tok; state bf16 {m['state']['bf16']/1e6:.1f} MB, "
          f"fp32 {m['state']['fp32']/1e6:.1f} MB; M3 Max prefill at 50/100/150/200/260k: "
          + "/".join(f"{p_local_m3(k, L*1e3):.0f}" for L in (V['main_L133_61'], V['main_L133_65'], V['main_L133_70'], V['main_L133_75'], V['main_L133_80'])))
    p("")

    # ---- Table 1: one turn, delta 10k, M3 Max, speedup by depth and network
    for model in MODELS:
        for d in (V['main_L138_18'], V['main_L138_23'], V['main_L138_29']):
            p(f"== {MODELS[model]['name']}, M3 Max, delta {d/1e3:.0f}k: prefill speedup (local time in header)")
            depths = (V['depths_L140_22'], V['depths_L140_28'], V['depths_L140_35'], V['depths_L140_42'], V['depths_L140_49'])
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
            for L in (V['main_L154_22'], V['main_L154_29']):
                cells = []
                for d in (V['main_L156_26'], V['main_L156_31'], V['main_L156_36'], V['main_L156_42']):
                    v = [bw_needed(model, tier, d, L, g) for g in (1, 2, V['v_L157_73'])]
                    cells.append(f"{d/1e3:.0f}k:" + "/".join("-" if x == float('inf') else f"{x:.0f}" for x in v))
                asym = MODELS[model]["kv"] * p_local_m3(model, L) * TIERS[tier][0] * 8 / 1e6 / EFF
                p(f"  {tier:<13} @{int(L/1e3)}k  " + "  ".join(cells) + f"   asymptote {asym:.0f}")
        p("")

    # ---- Table 3: full session 20k -> 200k (and 150k -> 260k), adaptive per-turn policy
    for model in MODELS:
        for (L0, L1) in ((V['main_L165_26'], V['main_L165_32']), (V['main_L165_41'], V['main_L165_48'])):
            p(f"== {MODELS[model]['name']}: session {int(L0/1e3)}k->{int(L1/1e3)}k, adaptive offload; "
              f"time = prefill + decode (wall, one agent)")
            for tier in TIERS:
                base = sim_sessions(model, tier, 0, L0, L1)
                tot0 = base["pre_local"] + base["dec"]
                line = (f"  {tier:<13} local {fmt_t(base['pre_local'])}+{fmt_t(base['dec'])}={fmt_t(tot0)}"
                        f" (prefill {V['line_L172_37']*base['pre_local']/tot0:.0f}%) |")
                for lab, mb in NETS:
                    if lab in ("50M", "500M", "2.5G"):
                        continue
                    r = sim_sessions(model, tier, mb, L0, L1)
                    tot = r["pre_hyb"] + r["dec"]
                    line += f" {lab}:{tot0/tot:.2f}x"
                p(line)
            r = sim_sessions(model, "M3 Max", 1000, L0, L1)
            p(f"  per session: turns {r['turns']:.0f}, new tokens {r['new_tok']/1e3:.0f}k, output {r['out_tok']/1e3:.0f}k, "
              f"cloud cache reads {r['cache_read']/1e6:.1f}M; @1G M3 offloaded {V['main_L182_80']*r['offl_tok']/r['new_tok']:.0f}% of new tokens, "
              f"download {r['bytes']/1e9:.1f} GB")
            r = sim_sessions(model, "M3 Max", V['r_L184_46'], L0, L1)
            p(f"  @100M M3: offloaded {V['main_L185_39']*r['offl_tok']/r['new_tok']:.0f}% of new tokens, download {r['bytes']/1e9:.1f} GB")
            p("")

    # ---- decode-speed sensitivity for the dense model (Ivan: 5 now, 10-15 reachable)
    p("== Qwen3.8-27B, M3 Max, session 20k->200k, decode 5 vs 10 vs 15 tok/s")
    for dm in (1.0, 2.0, V['main_L190_25']):
        base = sim_sessions("dense", "M3 Max", 0, dec_mult=dm)
        tot0 = base["pre_local"] + base["dec"]
        line = f"  decode {V['line_L193_27']*dm:.0f} tok/s: local {fmt_t(tot0)} |"
        for lab, mb in (("100M", V['main_L194_33']), ("200M", V['main_L194_48']), ("1G", 1000), ("10G", V['main_L194_76'])):
            r = sim_sessions("dense", "M3 Max", mb, dec_mult=dm)
            line += f" {lab}: {fmt_t(r['pre_hyb'] + r['dec'])} ({tot0/(r['pre_hyb']+r['dec']):.1f}x)"
        p(line)
    p("")

    # ---- big ingestion: load d tokens at once on top of a cached 20k harness prefix
    p("== Big ingestion (repo/doc/log dump) on top of cached 20k prefix: time to first token")
    for model in MODELS:
        for tier, pm in (("slow~200GB/s", None), ("M3 Max", None), ("M5 Max(2x)", None), ("M5 Max(4x)", None)):
            cells = []
            for d in (V['main_L205_22'], V['main_L205_28'], V['main_L205_35']):
                tl, L = 0.0, V['_tl__L__L206_29']
                while L < V['main_L207_26'] + d:
                    tl += 1e3 / (p_local_m3(model, L) * TIERS[tier][0])
                    L += 1e3
                hy = [t_hybrid(model, d, V['hy_L210_41'] + d, mb) for mb in (V['hy_L210_66'], V['hy_L210_71'], 1000, V['hy_L210_82'])]
                cells.append(f"{int(d/1e3)}k: local {fmt_t(tl)} | 100M {fmt_t(hy[0])} 200M {fmt_t(hy[1])} "
                             f"1G {fmt_t(hy[2])} 10G {fmt_t(hy[3])}")
            p(f"  {MODELS[model]['name']:<11} {tier:<13} " + " ;; ".join(cells))
    p("")

    # ---- multi-agent Mac capacity: 4 agents share the GPU; decode batches, prefill does not
    BATCH4 = {"flash": V['BATCH4_L217_23'], "dense": 2.0}  # aggregate decode gain of 4 streams vs 1 (estimate)
    p("== Sessions (20k->200k) per 8 h of GPU time, 4 parallel agents: local-only -> hybrid @1G / @200M")
    for model in MODELS:
        for tier in TIERS:
            for dm in ((1.0, V['main_L221_29']) if model == "dense" else (1.0,)):
                res = []
                for mb in (0, 1000, V['main_L223_36']):
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
            for mb in (V['main_L236_23'], V['main_L236_28'], 1000):
                r = sim_sessions(model, "M3 Max", mb, st=st)
                p(f"  {MODELS[model]['name']:<11} state {st} @{mb}M: {r['bytes']/1e9:.1f} GB, "
                  f"state {V['main_L239_27']*r['state_bytes']/max(r['bytes'],1):.0f}%, offloaded {V['main_L239_84']*r['offl_tok']/r['new_tok']:.0f}% of new tokens")
    p("")
    print("\n".join(out))
    econ()


# ---------------------------------------------------------------- economics
PRICES = {  # $/M tokens: input, output, cache read, cache write
    "Sonnet 5.5": (2.0, V['PRICES_L247_24'], V['PRICES_L247_30'], V['PRICES_L247_36']),     # write = 1.25 x input (assumed standard multiplier)
    "Opus 5.5": (V['PRICES_L248_17'], V['PRICES_L248_22'], V['PRICES_L248_28'], V['PRICES_L248_34']),
    "Fable 5.1": (V['PRICES_L249_18'], V['PRICES_L249_24'], V['PRICES_L249_30'], V['PRICES_L249_36']),
    "Flash-Next API": (V['PRICES_L250_23'], V['PRICES_L250_29'], V['PRICES_L250_35'], V['PRICES_L250_42']),  # QwenCloud list via aggregators; write assumed = input
    "27B API": (V['PRICES_L251_16'], V['PRICES_L251_22'], V['PRICES_L251_28'], V['PRICES_L251_34']),          # Alibaba intl list via aggregator (Oct 2026)
}
NODE_MONTH = V['NODE_MONTH_L253_13'] * V['NODE_MONTH_L253_21'] / V['NODE_MONTH_L253_27'] + V['NODE_MONTH_L253_32'] / V['NODE_MONTH_L253_39']   # B300 node: book price + 20% infra, 4 y, opex $54k/y
GPU_H = NODE_MONTH / (8 * V['GPU_H_L254_26'])               # $/GPU-hour at 100% use
EFF_PF = V['EFF_PF_L255_9'] * V['EFF_PF_L255_18']                       # FP8 dense x MFU, FLOP/s per GPU


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
        c_miss = c + V['c_miss_L268_21'] * r["turns"] * (cr / r["turns"]) / 1e6 * (pw - pr)  # 10% turns re-write prefix
        per[k] = c
        p(f"   {k:<15} ${c:6.2f}/session (with 10% cache misses ${c_miss:6.2f}); x840/month = ${V['econ_L270_96']*c:,.0f}")
    for model in MODELS:
        m = MODELS[model]
        avg_L = V['avg_L_L273_16']
        gpu_s = (tok_in + tok_out) * m["flop"](avg_L) / EFF_PF
        for util in (1.0, V['econ_L275_26']):
            c = gpu_s / 3600 * GPU_H / util
            p(f"   hybrid prefill {m['name']:<11} {gpu_s:5.1f} GPU-s/session, util {util:.0%}: ${c:.3f}/session, x840 = ${V['econ_L277_122']*c:,.0f}/month")
    # own all-server cluster: prefill + decode + KV residency in HBM (estimate)
    life = V['life_L279_11']                  # s, wall lifetime of a 20k->200k session served from the DC
    hbm_gpu = V['hbm_gpu_L280_14']                # usable HBM per B300 for KV after weights/workspace
    dec_gpu = {"flash": V['dec_gpu_L281_24'], "dense": V['dec_gpu_L281_41']}   # tok/s per GPU at the batch HBM allows (estimate)
    for model in MODELS:
        m = MODELS[model]
        pre = (tok_in + tok_out) * m["flop"](V['pre_L284_45']) / EFF_PF
        dec = tok_out / dec_gpu[model]
        res = V['res_L286_14'] * m["kv"] * life / hbm_gpu
        gs = pre + dec + res
        cells = ", ".join(f"util {u:.0%}: ${V['cells_L288_44']*gs/3600*GPU_H/u:,.0f}/month" for u in (V['cells_L288_87'], V['cells_L288_92']))
        p(f"   own cluster {m['name']:<11} prefill {pre:.0f} + decode {dec:.0f} + KV residency {res:.0f} = {gs:.0f} GPU-s/session; {cells}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
