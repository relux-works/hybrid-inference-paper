from ..inputs import legacy_values, measurement_path
V = legacy_values('sessions')

import io
#!/usr/bin/env python3
"""Hybrid inference (server prefill, client decode), model v3.

New in v3 (v2 is hybrid_calc2.py in this directory):
  * device table with prices (Apple M5 Pro/Max/Ultra, Ryzen AI Max+ 395, DGX Spark);
  * decode of several parallel agents from memory bandwidth (weights read once per
    step, KV of every stream read every step), so device capacity follows physics
    instead of fixed multipliers;
  * the server is the system of record: it prefills every session token in the
    background, offloaded or not, and only the latency of an offloaded turn waits;
  * own all-server cluster vs hybrid vs API per session, per developer-month, and
    for a company of N developers over 1 and 4 years with residual values;
  * a 1M-token scenario; an equilibrium table (device price x channel x sessions).

Every number is an estimate unless marked as a measurement or a quoted price.
Measurements (Ivan, M3 Max 128 GB, 400 GB/s):
  Flash-Next: prefill ~500 tok/s at ~150k, ~150 tok/s near 260k; decode 30-40 tok/s.
  Qwen3.8-27B: prefill ~50 tok/s at 200k+; decode ~5 tok/s (Ivan expects 15-20 with
  3-bit weights, 8-bit KV and a better engine).
Prices quoted 2026-10-29: OpenRouter API snapshots in prices-2026-10-29/, Anthropic list
prices from the Claude API reference bundled with Claude Code.
"""
import csv
import math
import os
import random

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- models
CONV = V['CONV_L31_7'] * V['CONV_L31_15']   # conv state per DeltaNet layer: channels x (kernel - 1)


def state_bytes(n_linear, nbytes):
    return (n_linear * V['state_bytes_L35_23'] * V['state_bytes_L35_28'] * V['state_bytes_L35_34'] + n_linear * CONV) * nbytes


MODELS = {
    "flash": dict(name="Flash-Next", kv=V['MODELS_L39_40'] * 2 * 2 * V['MODELS_L39_53'] + V['MODELS_L39_59'] * V['MODELS_L39_64'] / V['MODELS_L39_70'],   # 8-bit bytes/token
                  state=state_bytes(V['MODELS_L40_36'], 2), flop=lambda L: V['MODELS_L40_59'] + V['MODELS_L40_68'] * L,
                  weights=V['MODELS_L41_26'],      # ~3.5-bit main weights; n-gram table offloaded to SSD
                  w_srv=V['MODELS_L42_24'],       # fp8 server copy
                  dec1=V['MODELS_L43_23']),        # [measured] M3 Max, one stream, 30-40 tok/s
    "dense": dict(name="Qwen3.8-27B", kv=V['MODELS_L44_41'] * 2 * V['MODELS_L44_50'] * V['MODELS_L44_54'],
                  state=state_bytes(V['MODELS_L45_36'], 2), flop=lambda L: V['MODELS_L45_59'] + V['MODELS_L45_66'] * V['MODELS_L45_71'] * V['MODELS_L45_76'] * V['MODELS_L45_82'] * L,
                  weights=V['MODELS_L46_26'],    # ~3.5-bit (tuned profile)
                  w_srv=V['MODELS_L47_24']),
}

# Dense decode profiles on the client: weight bytes, KV bytes/token, bandwidth efficiency.
# "measured": Q4_K_M with f16 KV, efficiency solved so that M3 Max gives 5 tok/s at 200k.
# "tuned": 3.5-bit weights, 8-bit KV, 65% of peak bandwidth (Ivan's 15-20 tok/s target).
_W_M, _KV_M = V['__W_M___KV_M__L53_14'], V['__W_M___KV_M__L53_22'] * 2 * V['__W_M___KV_M__L53_31'] * V['__W_M___KV_M__L53_35'] * 2
EFF_MEASURED = V['EFF_MEASURED_L54_15'] * (_W_M + V['EFF_MEASURED_L54_29'] * _KV_M + 2 * state_bytes(V['EFF_MEASURED_L54_61'], 2)) / V['EFF_MEASURED_L54_71']
DENSE_PROFILES = {"measured": (_W_M, _KV_M, EFF_MEASURED), "tuned": (V['DENSE_PROFILES_L55_69'], V['DENSE_PROFILES_L55_77'] * 2 * V['DENSE_PROFILES_L55_86'] * V['DENSE_PROFILES_L55_90'], V['DENSE_PROFILES_L55_95'])}


def p_local_m3(model, L, flash_mode="measured"):
    """M3 Max prefill tok/s at depth L (marginal)."""
    if model == "flash":
        if flash_mode == "sparse" or L <= V['p_local_m3_L61_42']:
            # flat measured region; beyond it "sparse" assumes QSA keeps cost ~linear
            return V['p_local_m3_L63_19'] * MODELS["flash"]["flop"](min(L, V['p_local_m3_L63_58'])) / MODELS["flash"]["flop"](L) \
                if flash_mode == "sparse" else V['p_local_m3_L64_47']
        f = (min(L, V['f_L65_20']) - V['f_L65_29']) / V['f_L65_38']
        return math.exp(math.log(V['p_local_m3_L66_33']) + f * (math.log(V['p_local_m3_L66_54']) - math.log(V['p_local_m3_L66_70'])))
    m = MODELS["dense"]
    return V['p_local_m3_L68_11'] * m["flop"](V['p_local_m3_L68_28']) / m["flop"](L)


# ---------------------------------------------------------------- devices
class Dev:
    def __init__(self, key, label, mem, bw, ultra, pf, price, note):
        self.key, self.label, self.mem, self.bw, self.ultra, self.pf = key, label, mem, bw, ultra, pf
        self.price, self.note = price, note

    @property
    def bw_eff_factor(self):
        return self.bw * 1e9 * self.ultra


# bandwidth GB/s; "ultra": share of peak bandwidth a two-die Ultra delivers to decode
# relative to a Max (M2/M3 Ultra decoded ~1.4-1.5x a Max at 2x bandwidth);
# pf: long-context prefill multiplier vs M3 Max (estimates, see notes).
DEVICES = [
    Dev("m5pro", "M5 Pro 64 GB (MBP 14)", V['DEVICES_L86_42'], V['DEVICES_L86_46'], 1.0, V['DEVICES_L86_56'], (V['DEVICES_L86_62'], V['DEVICES_L86_68']), "est.: $2,499 base [fact] + RAM"),
    Dev("strix", "Ryzen AI Max+ 395 128 GB", V['DEVICES_L87_45'], V['DEVICES_L87_50'], 1.0, V['DEVICES_L87_60'], (V['DEVICES_L87_66'], V['DEVICES_L87_72']), "Framework $3,449 [listing, 09.2026]"),
    Dev("spark", "DGX Spark 128 GB", V['DEVICES_L88_37'], V['DEVICES_L88_42'], 1.0, V['DEVICES_L88_52'], (V['DEVICES_L88_58'], V['DEVICES_L88_64']), "$4,699 [fact, 02.2026]; $6,950 [report, 10.2026]"),
    Dev("m3max", "M3 Max 128 GB", V['DEVICES_L89_34'], V['DEVICES_L89_39'], 1.0, 1.0, None, "Ivan's, reference"),
    Dev("m5max", "M5 Max 128 GB (MBP)", V['DEVICES_L90_40'], V['DEVICES_L90_45'], 1.0, V['DEVICES_L90_55'], (V['DEVICES_L90_61'], V['DEVICES_L90_67']), "est."),
    Dev("ultra96", "M5 Ultra 96 GB (Studio)", V['DEVICES_L91_46'], V['DEVICES_L91_50'], V['DEVICES_L91_56'], V['DEVICES_L91_62'], (V['DEVICES_L91_68'], V['DEVICES_L91_74']), "$5,499 [fact]"),
    Dev("ultra256", "M5 Ultra 256 GB (Studio)", V['DEVICES_L92_48'], V['DEVICES_L92_53'], V['DEVICES_L92_59'], 8.0, (V['DEVICES_L92_71'], V['DEVICES_L92_77']), "$9,499 [fact]"),
]
DEV = {d.key: d for d in DEVICES}
MEM_USABLE = V['MEM_USABLE_L95_13']      # share of RAM the GPU may wire (macOS limit raised; Linux GTT)
MEM_BUFFERS = V['MEM_BUFFERS_L96_14']

NETS = [("local", 0), ("100M", V['NETS_L98_31']), ("200M", V['NETS_L98_46']), ("1G", 1000)]
EFF_NET = V['EFF_NET_L99_10']
T_FIX = V['T_FIX_L100_8']            # s per offload: scheduling, session load into HBM, RTT
EFF_PF = V['EFF_PF_L101_9'] * V['EFF_PF_L101_18']  # B300 FP8 dense x MFU, FLOP/s per GPU (FP4 would roughly double)
HBM_BW = V['HBM_BW_L102_9'] * V['HBM_BW_L102_16']
HBM_KV = V['HBM_KV_L103_9']          # usable HBM for KV per B300 after weights and workspace


def bw(mbit):
    return mbit * 1e6 / 8 * EFF_NET


def p_local(model, dev, L, flash_mode="measured"):
    return p_local_m3(model, L, flash_mode) * dev.pf


def dec_rates(model, dev, K, L, profile="tuned", g4=V['dec_rates_L114_52']):
    """(per-stream tok/s, aggregate tok/s) for K agents decoding at depth ~L."""
    if model == "dense":
        W, kvb, eff = DENSE_PROFILES[profile]
        step = W + K * (L * kvb + 2 * MODELS["dense"]["state"])
        r = dev.bw_eff_factor * eff / step
        return r, K * r
    r1 = MODELS["flash"]["dec1"] * (dev.bw * dev.ultra) / V['r1_L121_58']   # [assumption] scales with bandwidth
    agg = r1 * K ** math.log(g4, V['agg_L122_33'])                                 # g4: 4-stream batching gain
    return agg / K, agg


def k_mem(model, dev, L, profile="tuned"):
    m = MODELS[model]
    W = DENSE_PROFILES[profile][0] if model == "dense" else m["weights"]
    kvb = DENSE_PROFILES[profile][1] if model == "dense" else m["kv"]
    free = dev.mem * 1e9 * MEM_USABLE - MEM_BUFFERS - W
    return max(0, int(free // (L * kvb + m["state"])))


def k_max(model, dev, floor=V['k_max_L134_28'], L_avg=V['k_max_L134_40'], L_cap=V['k_max_L134_53'], profile="tuned"):
    km = k_mem(model, dev, L_cap, profile)
    best = V['best_L136_11']
    for K in range(1, km + 1):
        if dec_rates(model, dev, K, L_avg, profile)[0] >= floor:
            best = K
    return best


# ---------------------------------------------------------------- sessions
def make_sessions(n=V['make_sessions_L144_20'], L0=V['make_sessions_L144_28'], L1=V['make_sessions_L144_37'], seed=V['make_sessions_L144_49'], tool_med=V['make_sessions_L144_61']):
    """Turn sequences (L at turn start, delta in, output, tool seconds); same draws for all scenarios."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        L, turns = L0, []
        while L < L1:
            d = min(V['d_L151_20'], rnd.lognormvariate(math.log(V['d_L151_54']), V['d_L151_61']))
            o = min(V['o_L152_20'], rnd.lognormvariate(math.log(V['o_L152_53']), V['o_L152_59']))
            tau = rnd.lognormvariate(math.log(tool_med), 1.0)
            turns.append((L, d, o, tau))
            L += d + o
        out.append(turns)
    return out


def run(model, dev, mbit, K, sessions, profile="tuned", flash_mode="measured", g4=V['run_L160_82']):
    m = MODELS[model]
    acc = dict(dev_time=V['acc_L162_24'], wall=V['acc_L162_34'], pre_local=V['acc_L162_49'], dec_dev=V['acc_L162_62'], srv_gpu=V['acc_L162_75'], srv_gpu_offl=V['acc_L162_93'],
               bytes=V['acc_L163_21'], offl=V['acc_L163_31'], new=V['acc_L163_40'], out=V['acc_L163_49'], turns=V['acc_L163_60'])
    for turns in sessions:
        for (L, d, o, tau) in turns:
            tl = d / p_local(model, dev, L, flash_mode)
            th = float("inf")
            if mbit:
                th = T_FIX + d * m["flop"](L) / EFF_PF + (d * m["kv"] + m["state"]) / bw(mbit)
            if th < tl:
                acc["wall"] += th
                acc["bytes"] += d * m["kv"] + m["state"]
                acc["offl"] += d
                acc["srv_gpu_offl"] += d * m["flop"](L) / EFF_PF
            else:
                acc["dev_time"] += tl
                acc["pre_local"] += tl
                acc["wall"] += tl
            if mbit:   # server shadows every token as system of record
                acc["srv_gpu"] += (d + o) * m["flop"](L) / EFF_PF
            r, agg = dec_rates(model, dev, K, L + d, profile, g4)
            acc["dev_time"] += o / agg
            acc["dec_dev"] += o / agg
            acc["wall"] += o / r + tau
            acc["new"] += d
            acc["out"] += o
            acc["turns"] += 1
    n = len(sessions)
    res = {k: v / n for k, v in acc.items()}
    res["per8h"] = min(8 * 3600 / res["dev_time"], K * 8 * 3600 / res["wall"])
    res["dev_bound"] = 8 * 3600 / res["dev_time"]
    res["wall_bound"] = K * 8 * 3600 / res["wall"]
    return res


# ---------------------------------------------------------------- prices
# $/M tokens. API: input, output, cache read, cache write (write = price of tokens added to cache).
API = {
    # [quoted] Anthropic list prices; cache write = 1.25 x input (5-minute TTL)
    "Haiku 5.5": dict(tiers=[(V['API_L200_30'], (V['API_L200_38'], V['API_L200_44'], V['API_L200_50'], V['API_L200_56'])), (math.inf, (V['API_L200_77'], V['API_L200_83'], V['API_L200_89'], V['API_L200_95']))]),
    "Sonnet 5.5": dict(tiers=[(math.inf, (2.0, V['API_L201_47'], V['API_L201_53'], V['API_L201_59']))]),
    "Opus 5.5": dict(tiers=[(math.inf, (V['API_L202_40'], V['API_L202_45'], V['API_L202_51'], V['API_L202_57']))]),
    "Fable 5.1": dict(tiers=[(math.inf, (V['API_L203_41'], V['API_L203_47'], V['API_L203_53'], V['API_L203_59']))]),
    # [quoted] OpenRouter 2026-10-29; Flash: only Alibaba serves qwen3.8-flash (API sibling of Flash-Next [?])
    "Flash API (Alibaba)": dict(tiers=[(math.inf, (V['API_L205_51'], V['API_L205_57'], V['API_L205_63'], V['API_L205_70']))]),
    # 27B: median over 21 OpenRouter providers; cheapest well-known (DeepInfra bf16); Alibaba
    "27B API median": dict(tiers=[(math.inf, (V['API_L207_46'], V['API_L207_52'], V['API_L207_58'], V['API_L207_64']))]),
    "27B API DeepInfra": dict(tiers=[(math.inf, (V['API_L208_49'], V['API_L208_55'], V['API_L208_62'], V['API_L208_70']))]),
    "27B API Alibaba": dict(tiers=[(math.inf, (V['API_L209_47'], V['API_L209_54'], V['API_L209_60'], V['API_L209_67']))]),
}


def api_cost(name, sessions):
    tiers = API[name]["tiers"]
    tot = V['tot_L215_10']
    for turns in sessions:
        o_prev = V['o_prev_L217_17']
        for (L, d, o, tau) in turns:
            prompt = L + d
            pi, po, pr, pw = next(p for lim, p in tiers if prompt <= lim)
            tot += (L * pr + (d + o_prev) * pw + o * po) / 1e6
            o_prev = o
    return tot / len(sessions)


NODE_CAPEX = V['NODE_CAPEX_L226_13'] * V['NODE_CAPEX_L226_21']           # B300 HGX node + 20% infrastructure (book price) [estimate]
NODE_OPEX_Y = V['NODE_OPEX_Y_L227_14']                 # power, colo, support per node-year [estimate]
NODE_MONTH = NODE_CAPEX / V['NODE_MONTH_L228_26'] + NODE_OPEX_Y / V['NODE_MONTH_L228_45']
GPU_S = NODE_MONTH / (8 * V['GPU_S_L229_26'] * 3600)   # $ per GPU-second at 100% use

PEAK = V['PEAK_L231_7']                          # GPUs at the working-hour peak / average, incl. latency headroom
SRV_DEC_BATCH = {"flash": V['SRV_DEC_BATCH_L232_26'], "dense": V['SRV_DEC_BATCH_L232_40']}   # active decode streams per GPU
SRV_STREAM_TPS = {"flash": 60.0, "dense": V['SRV_STREAM_TPS_L233_42']}


def own_cluster_gpu_s(model, sessions, ideal):
    """All-server: prefill + decode bandwidth + KV residency in HBM, GPU-seconds per session."""
    m = MODELS[model]
    pre = dec = res = V['pre_L239_22']
    for turns in sessions:
        for (L, d, o, tau) in turns:
            pre += d * m["flop"](L) / EFF_PF
            if model == "dense":
                per_tok = (m["w_srv"] / SRV_DEC_BATCH[model] + (L + d) * m["kv"] + 2 * m["state"]) / HBM_BW
            else:
                B = SRV_DEC_BATCH[model]
                touched = 1 - (1 - V['touched_L247_35'] / V['touched_L247_40']) ** B
                w_step = V['w_step_L248_25'] + touched * (m["w_srv"] - V['w_step_L248_55'])
                per_tok = (w_step / B + V['per_tok_L249_40'] * m["kv"] + V['per_tok_L249_57'] * (L + d) + V['per_tok_L249_73'] * m["state"]) / HBM_BW
            dec += o * per_tok
            busy = o / SRV_STREAM_TPS[model] + (0 if ideal else tau)
            res += (L + d) * m["kv"] * busy / HBM_KV
    n = len(sessions)
    return pre / n, dec / n, res / n


def fmt_t(s):
    if s >= 3600:
        return f"{s/3600:.1f}h"
    return f"{s/60:.1f}m" if s >= V['fmt_t_L260_34'] else f"{s:.0f}s" if s >= V['fmt_t_L260_63'] else f"{s:.1f}s"


# ---------------------------------------------------------------- report
def main():
    lines = []
    p = lines.append
    S = make_sessions()
    S_short = S[:80]

    p("== Inputs")
    for k, m in MODELS.items():
        p(f"  {m['name']}: KV 8-bit {m['kv']/1024:.1f} KiB/tok, state bf16 {m['state']/1e6:.0f} MB")
    p(f"  dense 'measured' bandwidth efficiency solved from 5 tok/s @200k on M3 Max: {EFF_MEASURED:.2f}")
    p(f"  own B300 node ${NODE_MONTH:,.0f}/month -> ${GPU_S*3600:.2f}/GPU-h at 100% use")
    t0 = sum(len(t) for t in S) / len(S)
    p(f"  session 20k->200k: {t0:.0f} turns on average")
    p("")

    p("== Decode per stream / aggregate (tok/s), Qwen3.8-27B tuned (3.5-bit, 8-bit KV); K agents at depth L")
    for dev in DEVICES:
        cells = []
        for K in (1, V['main_L282_21'], 8):
            for L in (V['main_L283_22'], V['main_L283_28'], V['main_L283_35'], 1e6):
                if k_mem("dense", dev, L) < K:
                    cells.append(f"K{K}@{int(L/1e3)}k: -")
                    continue
                r, a = dec_rates("dense", dev, K, L)
                cells.append(f"K{K}@{int(L/1e3)}k: {r:.1f}/{a:.0f}")
        p(f"  {dev.label:<26} " + "  ".join(cells))
    p("  measured profile on M3 Max: " + ", ".join(
        f"K1@{int(L/1e3)}k {dec_rates('dense', DEV['m3max'], 1, L, 'measured')[0]:.1f}" for L in (V['main_L291_98'], V['main_L291_104'], V['main_L291_111'])))
    p("")

    p("== Memory: max parallel 200k sessions (KV 8-bit) / agents with >=10 tok/s per stream at 110k")
    for dev in DEVICES:
        p(f"  {dev.label:<26} 27B: mem {k_mem('dense', dev, V['main_L296_60']):>2}, >=10 tok/s {k_max('dense', dev):>2};"
          f"  Flash: mem {k_mem('flash', dev, V['main_L297_46']):>2}, 1M-token sessions 27B: {k_mem('dense', dev, 1e6)}")
    p("")

    rows = []
    for model, profiles in (("dense", ("tuned", "measured")), ("flash", ("-",))):
        for prof in profiles:
            p(f"== Sessions 20k->200k per 8 h, {MODELS[model]['name']}" + (f", decode profile {prof}" if model == "dense" else ", g4=1.26"))
            p("   device                     K    local     100M      200M      1G     | 1G gain | dev-bound/wall-bound @1G")
            for dev in DEVICES:
                km = k_mem(model, dev, V['km_L306_39'], prof if model == "dense" else "tuned")
                if km == 0:
                    p(f"   {dev.label:<26} does not fit")
                    continue
                for K in sorted({min(V['main_L310_37'], km), max(1, k_max(model, dev, profile=prof if model == 'dense' else 'tuned'))}):
                    if K > km:
                        continue
                    res = [run(model, dev, mb, K, S_short, profile=prof if model == "dense" else "tuned") for _, mb in NETS]
                    v = [r["per8h"] for r in res]
                    p(f"   {dev.label:<26} {K:>2} " + " ".join(f"{x:>8.1f}" for x in v)
                      + f"   | x{v[3]/v[0]:.2f}  | {res[3]['dev_bound']:.0f}/{res[3]['wall_bound']:.0f}")
                    for (lab, mb), r in zip(NETS, res):
                        rows.append(dict(model=MODELS[model]["name"], profile=prof, device=dev.label, K=K, net=lab,
                                         sessions_8h=round(r["per8h"], 2),
                                         price_low=dev.price[0] if dev.price else "", price_high=dev.price[1] if dev.price else "",
                                         srv_gpu_s=round(r["srv_gpu"], 2), download_gb=round(r["bytes"] / 1e9, 2),
                                         offloaded_share=round(r["offl"] / r["new"], V['main_L322_85']) if r["new"] else 0))
            p("")

    # night: more agents, slower streams acceptable (>= 5 tok/s), prefill on idle server
    p("== 24 h: day (8 h, K as interactive) + night (16 h, K up to memory with >=5 tok/s/stream), hybrid 1G")
    for model in ("dense", "flash"):
        for dev in DEVICES:
            km = k_mem(model, dev, V['km_L329_35'])
            if km == 0:
                continue
            k_day = min(V['k_day_L332_24'], km)
            k_night = max(k_day, k_max(model, dev, floor=V['k_night_L333_57']) if model == "dense" else min(km, 8))
            day = run(model, dev, 1000, k_day, S_short)["per8h"]
            night = 2 * run(model, dev, 1000, k_night, S_short)["per8h"]
            p(f"  {MODELS[model]['name']:<11} {dev.label:<26} day {day:5.0f} (K{k_day}) + night {night:5.0f} (K{k_night})"
              f" -> 24h {day+night:5.0f}; laptop at 40% night availability {day+V['main_L337_80']*night:5.0f}")
    p("")

    # ---------------------------------------------------------------- economics
    p("== API price per session 20k->200k and per heavy developer-month (840 sessions)")
    api_ps = {}
    for name in API:
        c = api_cost(name, S)
        api_ps[name] = c
        p(f"  {name:<20} ${c:6.3f}/session  ${V['main_L346_46']*c:8,.0f}/month")
    p("")

    p("== Own all-server cluster, GPU-seconds per session (prefill + decode + KV residency)")
    own = {}
    for model in MODELS:
        for ideal in (True, False):
            pre, dec, res = own_cluster_gpu_s(model, S, ideal)
            gs = pre + dec + res
            own[(model, ideal)] = gs
            p(f"  {MODELS[model]['name']:<11} {'ideal (KV leaves HBM in tool gaps)' if ideal else 'realistic (KV stays in HBM)':<36}"
              f" {pre:5.1f} + {dec:5.1f} + {res:5.1f} = {gs:5.1f} GPU-s;"
              f" per dev-month at 50%/25% use: ${V['main_L358_49']*gs*GPU_S/V['main_L358_62']:,.0f} / ${V['main_L358_76']*gs*GPU_S/V['main_L358_89']:,.0f}")
    p("")

    p("== Hybrid server part per session (M3 Max client): GPU (shadow prefill of all tokens), download")
    hyb = {}
    for model in MODELS:
        for mb in (V['main_L364_19'], 1000):
            r = run(model, DEV["m3max"], mb, V['r_L365_45'], S)
            hyb[(model, mb)] = r
            p(f"  {MODELS[model]['name']:<11} @{mb}M: {r['srv_gpu']:5.1f} GPU-s (latency-critical part {r['srv_gpu_offl']:.1f}),"
              f" download {r['bytes']/1e9:.1f} GB, offloaded {V['main_L368_62']*r['offl']/r['new']:.0f}% of new tokens;"
              f" GPU $/dev-month at 40%/16% use: ${V['main_L369_51']*r['srv_gpu']*GPU_S/V['main_L369_74']:,.0f} / ${V['main_L369_88']*r['srv_gpu']*GPU_S/V['main_L369_111']:,.0f}")
    p("  egress per dev-month (download x 840): transit $2-9/TB (colo, 95th pct, working hours) vs cloud $50-90/TB")
    for model in MODELS:
        gb = hyb[(model, V['gb_L372_25'])]["bytes"] / 1e9 * V['gb_L372_48']
        p(f"    {MODELS[model]['name']:<11} {gb/1e3:.1f} TB/month -> colo ${gb/1e3*2:,.0f}-{gb/1e3*V['main_L373_99']:,.0f}, cloud ${gb/1e3*V['main_L373_123']:,.0f}-{gb/1e3*V['main_L373_140']:,.0f}")
    p("")

    # ---------------------------------------------------------------- company TCO
    p("== Company of N heavy developers (40 sessions/day each), 1 and 4 years, $M")
    p(f"   capex sized for the working-hour peak: GPUs = N x 5 sessions/h x GPU-s / 3600 x {PEAK} (peak + headroom)")
    p("   residual value: servers 65% after 1 y, 20% after 4 y; Mac RAM/chip delta 75% / 35% [estimates]")
    for model in MODELS:
        for N in (1000, V['main_L381_24']):
            lines_tco = []
            # API
            for name in (["Flash API (Alibaba)"] if model == "flash" else ["27B API median", "27B API Alibaba"]):
                for Y in (1, V['main_L385_29']):
                    lines_tco.append((f"API {name}", Y, N * V['main_L386_60'] * api_ps[name] * V['main_L386_81'] * Y / 1e6, 0.0))
            # own all-server
            for ideal in (True, False):
                gpus = N * V['gpus_L389_27'] * own[(model, ideal)] / 3600 * PEAK
                nodes = math.ceil(gpus / 8)
                for Y in (1, V['main_L391_29']):
                    cash = nodes * (NODE_CAPEX + NODE_OPEX_Y * Y)
                    resid = nodes * NODE_CAPEX * (V['resid_L393_50'] if Y == 1 else V['resid_L393_70'])
                    lines_tco.append((f"own all-server {'ideal' if ideal else 'realistic'} ({nodes} nodes)", Y, cash / 1e6, resid / 1e6))
            # hybrid
            gs = hyb[(model, V['gs_L396_29'])]["srv_gpu"]
            gpus = N * V['gpus_L397_23'] * gs / 3600 * PEAK
            nodes = max(1, math.ceil(gpus / 8))
            kv_gb = V['kv_gb_L399_20'] * V['kv_gb_L399_24'] * MODELS[model]["kv"] / 1e9
            storage = N * kv_gb * V['storage_L400_34'] + N * kv_gb * V['storage_L400_53'] * V['storage_L400_57']     # hot DRAM $12/GB + 4x on NVMe
            tb_month = hyb[(model, V['tb_month_L401_35'])]["bytes"] / 1e12 * V['tb_month_L401_59'] * N
            for delta in (V['main_L402_26'], V['main_L402_32']):
                for Y in (1, V['main_L403_29']):
                    egress = tb_month * V['egress_L404_40'] * Y * V['egress_L404_49']      # $5/TB colo transit, remote staff
                    cash = nodes * (NODE_CAPEX + NODE_OPEX_Y * Y) + storage + egress + N * delta
                    resid = nodes * NODE_CAPEX * (V['resid_L406_50'] if Y == 1 else V['resid_L406_70']) + N * delta * (V['resid_L406_91'] if Y == 1 else V['resid_L406_111'])
                    lines_tco.append((f"hybrid ({nodes} nodes, Mac delta ${delta:,})", Y, cash / 1e6, resid / 1e6))
            p(f"  {MODELS[model]['name']}, N={N}:")
            for name, Y, cash, resid in lines_tco:
                p(f"    {name:<48} {Y}y: cash {cash:8.2f}  residual {resid:6.2f}  net {cash-resid:8.2f}")
    p("")

    # ---------------------------------------------------------------- 1M context
    p("== 1M-token context, Qwen3.8-27B (native 262k; 1M via YaRN). Session 200k->1M and 20k->1M")
    S1 = make_sessions(n=V['S1_L415_25'], L0=V['S1_L415_32'], L1=V['S1_L415_42'], seed=V['S1_L415_52'])
    S2 = make_sessions(n=V['S2_L416_25'], L0=V['S2_L416_32'], L1=V['S2_L416_41'], seed=V['S2_L416_51'])
    for lab, SS in (("200k->1M", S1), ("20k->1M", S2)):
        turns = sum(len(t) for t in SS) / len(SS)
        cr = sum(L for t in SS for (L, d, o, tau) in t) / len(SS)
        p(f"  {lab}: {turns:.0f} turns, cache reads {cr/1e6:.0f}M tokens per session")
        for name in ("27B API median", "Haiku 5.5", "Sonnet 5.5", "Opus 5.5"):
            p(f"    API {name:<16} ${api_cost(name, SS):7.2f}/session")
        for ideal in (True, False):
            pre, dec, res = own_cluster_gpu_s("dense", SS, ideal)
            gs = pre + dec + res
            p(f"    own all-server {'ideal' if ideal else 'realistic':<9} {gs/3600:5.2f} GPU-h (prefill {pre/3600:.2f}, decode {dec/3600:.2f},"
              f" residency {res/3600:.2f}) -> ${gs*GPU_S:.2f} at 100% use, ${gs*GPU_S/V['main_L427_86']:.2f} at 25%")
        for dev in (DEV["m3max"], DEV["m5max"], DEV["ultra96"]):
            if k_mem("dense", dev, 1e6) < 1:
                continue
            loc = run("dense", dev, 0, 1, SS)
            cells = [f"local {fmt_t(loc['wall'])} (prefill {V['cells_L432_60']*loc['pre_local']/loc['wall']:.0f}%)"]
            for mb in (V['main_L433_23'], V['main_L433_28'], 1000):
                r = run("dense", dev, mb, 1, SS)
                cells.append(f"{mb}M {fmt_t(r['wall'])} x{loc['wall']/r['wall']:.1f}")
            r = run("dense", dev, V['r_L436_34'], 1, SS)
            p(f"    {dev.label:<24} one agent: " + ", ".join(cells)
              + f"; server {r['srv_gpu']/3600:.2f} GPU-h = ${r['srv_gpu']*GPU_S:.2f}, download {r['bytes']/1e9:.0f} GB")
    p("  Ingest 1M tokens at once (27B): local full prefill vs server (1 GPU / 8 GPUs) + download of KV 8-bit + state")
    full = sum(1e3 * MODELS["dense"]["flop"](L) for L in range(0, int(1e6), 1000))
    kv_b = 1e6 * MODELS["dense"]["kv"] + MODELS["dense"]["state"]
    p(f"    FLOP {full:.2e}; KV {kv_b/2**V['main_L442_41']:.1f} GiB; server {fmt_t(full/EFF_PF)} on 1 GPU (${full/EFF_PF*GPU_S:.2f}), ~{fmt_t(full/EFF_PF/V['main_L442_139'])} on 8")
    for dev in (DEV["m3max"], DEV["m5max"], DEV["ultra96"], DEV["spark"], DEV["strix"]):
        tl = sum(1e3 / p_local("dense", dev, L) for L in range(0, int(1e6), 1000))
        p(f"    {dev.label:<26} local {fmt_t(tl)}")
    p("    download: " + ", ".join(f"{lab} {fmt_t(kv_b/bw(mb))}" for lab, mb in (("100M", V['main_L446_90']), ("200M", V['main_L446_105']), ("1G", 1000), ("10G", V['main_L446_133']))))
    p("  Prefill cost per token vs depth (FLOP): " + ", ".join(
        f"{int(L/1e3)}k 27B {MODELS['dense']['flop'](L)/1e9:.0f}G / Flash {MODELS['flash']['flop'](L)/1e9:.1f}G"
        for L in (V['main_L449_18'], V['main_L449_23'], 1e6)))
    p("")

    # ---------------------------------------------------------------- equilibrium
    # $/session = device price / (48 months x 21 days x sessions per 8 h) + server GPU at 25% use + egress.
    # Break-even device price: the price at which hybrid cost per session equals the reference.
    own_ps = {m: own[(m, False)] * GPU_S / V['own_ps_L455_43'] for m in MODELS}
    p("== Equilibrium: cost per session and break-even device price over 4 years, 8 h/day (remote: egress $5/TB)")
    p(f"   references per session: 27B API median ${api_ps['27B API median']:.3f}, Haiku 5.5 ${api_ps['Haiku 5.5']:.3f},"
      f" Flash API ${api_ps['Flash API (Alibaba)']:.3f}; own all-server at 25% use: 27B ${own_ps['dense']:.3f}, Flash ${own_ps['flash']:.3f}")
    for row in rows:
        model = "dense" if row["model"] == "Qwen3.8-27B" else "flash"
        dev = next(d for d in DEVICES if d.label == row["device"])
        srv = row["srv_gpu_s"] * GPU_S / V['srv_L462_41'] + row["download_gb"] * V['srv_L462_69'] / 1e3
        api_ref = api_ps["27B API median"] if model == "dense" else api_ps["Flash API (Alibaba)"]
        days = V['days_L464_15'] * V['days_L464_20'] * row["sessions_8h"]
        row["server_usd_per_session"] = round(srv, V['row__server_usd_per_session___L465_51'])
        row["device_usd_per_session_low"] = round(dev.price[0] / days, V['row__device_usd_per_session_low___L466_71']) if dev.price else ""
        row["device_usd_per_session_high"] = round(dev.price[1] / days, V['row__device_usd_per_session_high___L467_72']) if dev.price else ""
        row["api_ref_usd_per_session"] = round(api_ref, V['row__api_ref_usd_per_session___L468_56'])
        row["breakeven_device_price_vs_api"] = round((api_ref - srv) * days) if api_ref > srv else 0
        row["breakeven_device_price_vs_own"] = round((own_ps[model] - srv) * days) if own_ps[model] > srv else 0
    p("   device                     K  net   sess/8h  device $/sess   total $/sess   break-even price vs API / vs own")
    for row in rows:
        if row["profile"] == "measured" or row["net"] not in ("local", "200M", "1G"):
            continue
        dl, dh = row["device_usd_per_session_low"], row["device_usd_per_session_high"]
        srv = row["server_usd_per_session"] if row["net"] != "local" else 0.0
        tot = f"{dl+srv:.3f}-{dh+srv:.3f}" if dl != "" else f"{srv:.3f}+owned"
        dev_s = f"{dl:.3f}-{dh:.3f}" if dl != "" else "owned"
        be_api = row["breakeven_device_price_vs_api"] if row["net"] != "local" else round(row["api_ref_usd_per_session"] * V['be_api_L479_123'] * V['be_api_L479_128'] * row["sessions_8h"])
        be_own = row["breakeven_device_price_vs_own"] if row["net"] != "local" else round(own_ps["dense" if row["model"] == "Qwen3.8-27B" else "flash"] * V['be_own_L480_154'] * V['be_own_L480_159'] * row["sessions_8h"])
        p(f"   {row['model'][:5]} {row['device']:<26} {row['K']:>2} {row['net']:<5} {row['sessions_8h']:7.1f}  {dev_s:>13}  {tot:>13}   ${be_api:>7,} / ${be_own:>7,}")
    p("")

    with io.StringIO(newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
