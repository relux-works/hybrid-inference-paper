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
CONV = 10240 * 3   # conv state per DeltaNet layer: channels x (kernel - 1)


def state_bytes(n_linear, nbytes):
    return (n_linear * 48 * 128 * 128 + n_linear * CONV) * nbytes


MODELS = {
    "flash": dict(name="Flash-Next", kv=12 * 2 * 2 * 256 + 12 * 128 / 4,   # 8-bit bytes/token
                  state=state_bytes(36, 2), flop=lambda L: 13.2e9 + 3072 * L,
                  weights=55e9,      # ~3.5-bit main weights; n-gram table offloaded to SSD
                  w_srv=125e9,       # fp8 server copy
                  dec1=35.0),        # [measured] M3 Max, one stream, 30-40 tok/s
    "dense": dict(name="Qwen3.8-27B", kv=16 * 2 * 4 * 256,
                  state=state_bytes(48, 2), flop=lambda L: 54e9 + 16 * 24 * 256 * 4 * L,
                  weights=11.8e9,    # ~3.5-bit (tuned profile)
                  w_srv=27e9),
}

# Dense decode profiles on the client: weight bytes, KV bytes/token, bandwidth efficiency.
# "measured": Q4_K_M with f16 KV, efficiency solved so that M3 Max gives 5 tok/s at 200k.
# "tuned": 3.5-bit weights, 8-bit KV, 65% of peak bandwidth (Ivan's 15-20 tok/s target).
_W_M, _KV_M = 16.5e9, 16 * 2 * 4 * 256 * 2
EFF_MEASURED = 5.0 * (_W_M + 200e3 * _KV_M + 2 * state_bytes(48, 2)) / 400e9
DENSE_PROFILES = {"measured": (_W_M, _KV_M, EFF_MEASURED), "tuned": (11.8e9, 16 * 2 * 4 * 256, 0.65)}


def p_local_m3(model, L, flash_mode="measured"):
    """M3 Max prefill tok/s at depth L (marginal)."""
    if model == "flash":
        if flash_mode == "sparse" or L <= 150e3:
            # flat measured region; beyond it "sparse" assumes QSA keeps cost ~linear
            return 500.0 * MODELS["flash"]["flop"](min(L, 150e3)) / MODELS["flash"]["flop"](L) \
                if flash_mode == "sparse" else 500.0
        f = (min(L, 260e3) - 150e3) / 110e3
        return math.exp(math.log(500) + f * (math.log(150) - math.log(500)))
    m = MODELS["dense"]
    return 50.0 * m["flop"](200e3) / m["flop"](L)


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
    Dev("m5pro", "M5 Pro 64 GB (MBP 14)", 64, 307, 1.0, 1.5, (3000, 3500), "est.: $2,499 base [fact] + RAM"),
    Dev("strix", "Ryzen AI Max+ 395 128 GB", 128, 256, 1.0, 1.3, (2500, 3449), "Framework $3,449 [listing, 09.2026]"),
    Dev("spark", "DGX Spark 128 GB", 128, 273, 1.0, 4.0, (4699, 6950), "$4,699 [fact, 02.2026]; $6,950 [report, 10.2026]"),
    Dev("m3max", "M3 Max 128 GB", 128, 400, 1.0, 1.0, None, "Ivan's, reference"),
    Dev("m5max", "M5 Max 128 GB (MBP)", 128, 614, 1.0, 3.0, (5100, 6400), "est."),
    Dev("ultra96", "M5 Ultra 96 GB (Studio)", 96, 1228, 0.75, 6.0, (5499, 5499), "$5,499 [fact]"),
    Dev("ultra256", "M5 Ultra 256 GB (Studio)", 256, 1228, 0.75, 8.0, (9499, 9499), "$9,499 [fact]"),
]
DEV = {d.key: d for d in DEVICES}
MEM_USABLE = 0.85      # share of RAM the GPU may wire (macOS limit raised; Linux GTT)
MEM_BUFFERS = 4e9

NETS = [("local", 0), ("100M", 100), ("200M", 200), ("1G", 1000)]
EFF_NET = 0.9
T_FIX = 0.4            # s per offload: scheduling, session load into HBM, RTT
EFF_PF = 4.5e15 * 0.30  # B300 FP8 dense x MFU, FLOP/s per GPU (FP4 would roughly double)
HBM_BW = 8e12 * 0.7
HBM_KV = 240e9          # usable HBM for KV per B300 after weights and workspace


def bw(mbit):
    return mbit * 1e6 / 8 * EFF_NET


def p_local(model, dev, L, flash_mode="measured"):
    return p_local_m3(model, L, flash_mode) * dev.pf


def dec_rates(model, dev, K, L, profile="tuned", g4=1.26):
    """(per-stream tok/s, aggregate tok/s) for K agents decoding at depth ~L."""
    if model == "dense":
        W, kvb, eff = DENSE_PROFILES[profile]
        step = W + K * (L * kvb + 2 * MODELS["dense"]["state"])
        r = dev.bw_eff_factor * eff / step
        return r, K * r
    r1 = MODELS["flash"]["dec1"] * (dev.bw * dev.ultra) / 400.0   # [assumption] scales with bandwidth
    agg = r1 * K ** math.log(g4, 4)                                 # g4: 4-stream batching gain
    return agg / K, agg


def k_mem(model, dev, L, profile="tuned"):
    m = MODELS[model]
    W = DENSE_PROFILES[profile][0] if model == "dense" else m["weights"]
    kvb = DENSE_PROFILES[profile][1] if model == "dense" else m["kv"]
    free = dev.mem * 1e9 * MEM_USABLE - MEM_BUFFERS - W
    return max(0, int(free // (L * kvb + m["state"])))


def k_max(model, dev, floor=10.0, L_avg=110e3, L_cap=200e3, profile="tuned"):
    km = k_mem(model, dev, L_cap, profile)
    best = 0
    for K in range(1, km + 1):
        if dec_rates(model, dev, K, L_avg, profile)[0] >= floor:
            best = K
    return best


# ---------------------------------------------------------------- sessions
def make_sessions(n=200, L0=20e3, L1=200e3, seed=7, tool_med=2.0):
    """Turn sequences (L at turn start, delta in, output, tool seconds); same draws for all scenarios."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        L, turns = L0, []
        while L < L1:
            d = min(60e3, rnd.lognormvariate(math.log(1200), 1.2))
            o = min(4e3, rnd.lognormvariate(math.log(350), 0.8))
            tau = rnd.lognormvariate(math.log(tool_med), 1.0)
            turns.append((L, d, o, tau))
            L += d + o
        out.append(turns)
    return out


def run(model, dev, mbit, K, sessions, profile="tuned", flash_mode="measured", g4=1.26):
    m = MODELS[model]
    acc = dict(dev_time=0.0, wall=0.0, pre_local=0.0, dec_dev=0.0, srv_gpu=0.0, srv_gpu_offl=0.0,
               bytes=0.0, offl=0.0, new=0.0, out=0.0, turns=0)
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
    "Haiku 5.5": dict(tiers=[(100e3, (0.10, 0.50, 0.01, 0.125)), (math.inf, (0.50, 2.50, 0.05, 0.625))]),
    "Sonnet 5.5": dict(tiers=[(math.inf, (2.0, 10.0, 0.20, 2.5))]),
    "Opus 5.5": dict(tiers=[(math.inf, (4.0, 20.0, 0.20, 5.0))]),
    "Fable 5.1": dict(tiers=[(math.inf, (10.0, 50.0, 0.25, 12.5))]),
    # [quoted] OpenRouter 2026-10-29; Flash: only Alibaba serves qwen3.8-flash (API sibling of Flash-Next [?])
    "Flash API (Alibaba)": dict(tiers=[(math.inf, (0.15, 0.47, 0.016, 0.20))]),
    # 27B: median over 21 OpenRouter providers; cheapest well-known (DeepInfra bf16); Alibaba
    "27B API median": dict(tiers=[(math.inf, (0.18, 2.30, 0.05, 0.18))]),
    "27B API DeepInfra": dict(tiers=[(math.inf, (0.15, 1.875, 0.0375, 0.15))]),
    "27B API Alibaba": dict(tiers=[(math.inf, (0.425, 2.55, 0.085, 0.531))]),
}


def api_cost(name, sessions):
    tiers = API[name]["tiers"]
    tot = 0.0
    for turns in sessions:
        o_prev = 0.0
        for (L, d, o, tau) in turns:
            prompt = L + d
            pi, po, pr, pw = next(p for lim, p in tiers if prompt <= lim)
            tot += (L * pr + (d + o_prev) * pw + o * po) / 1e6
            o_prev = o
    return tot / len(sessions)


NODE_CAPEX = 650e3 * 1.2           # B300 HGX node + 20% infrastructure (book price) [estimate]
NODE_OPEX_Y = 54e3                 # power, colo, support per node-year [estimate]
NODE_MONTH = NODE_CAPEX / 48 + NODE_OPEX_Y / 12
GPU_S = NODE_MONTH / (8 * 730 * 3600)   # $ per GPU-second at 100% use

PEAK = 2.0                          # GPUs at the working-hour peak / average, incl. latency headroom
SRV_DEC_BATCH = {"flash": 128, "dense": 32}   # active decode streams per GPU
SRV_STREAM_TPS = {"flash": 60.0, "dense": 25.0}


def own_cluster_gpu_s(model, sessions, ideal):
    """All-server: prefill + decode bandwidth + KV residency in HBM, GPU-seconds per session."""
    m = MODELS[model]
    pre = dec = res = 0.0
    for turns in sessions:
        for (L, d, o, tau) in turns:
            pre += d * m["flop"](L) / EFF_PF
            if model == "dense":
                per_tok = (m["w_srv"] / SRV_DEC_BATCH[model] + (L + d) * m["kv"] + 2 * m["state"]) / HBM_BW
            else:
                B = SRV_DEC_BATCH[model]
                touched = 1 - (1 - 10 / 512) ** B
                w_step = 5e9 + touched * (m["w_srv"] - 5e9)
                per_tok = (w_step / B + 2048 * m["kv"] + 384 * (L + d) + 4 * m["state"]) / HBM_BW
            dec += o * per_tok
            busy = o / SRV_STREAM_TPS[model] + (0 if ideal else tau)
            res += (L + d) * m["kv"] * busy / HBM_KV
    n = len(sessions)
    return pre / n, dec / n, res / n


def fmt_t(s):
    if s >= 3600:
        return f"{s/3600:.1f}h"
    return f"{s/60:.1f}m" if s >= 100 else f"{s:.0f}s" if s >= 10 else f"{s:.1f}s"


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
        for K in (1, 4, 8):
            for L in (20e3, 110e3, 200e3, 1e6):
                if k_mem("dense", dev, L) < K:
                    cells.append(f"K{K}@{int(L/1e3)}k: -")
                    continue
                r, a = dec_rates("dense", dev, K, L)
                cells.append(f"K{K}@{int(L/1e3)}k: {r:.1f}/{a:.0f}")
        p(f"  {dev.label:<26} " + "  ".join(cells))
    p("  measured profile on M3 Max: " + ", ".join(
        f"K1@{int(L/1e3)}k {dec_rates('dense', DEV['m3max'], 1, L, 'measured')[0]:.1f}" for L in (20e3, 110e3, 200e3)))
    p("")

    p("== Memory: max parallel 200k sessions (KV 8-bit) / agents with >=10 tok/s per stream at 110k")
    for dev in DEVICES:
        p(f"  {dev.label:<26} 27B: mem {k_mem('dense', dev, 200e3):>2}, >=10 tok/s {k_max('dense', dev):>2};"
          f"  Flash: mem {k_mem('flash', dev, 200e3):>2}, 1M-token sessions 27B: {k_mem('dense', dev, 1e6)}")
    p("")

    rows = []
    for model, profiles in (("dense", ("tuned", "measured")), ("flash", ("-",))):
        for prof in profiles:
            p(f"== Sessions 20k->200k per 8 h, {MODELS[model]['name']}" + (f", decode profile {prof}" if model == "dense" else ", g4=1.26"))
            p("   device                     K    local     100M      200M      1G     | 1G gain | dev-bound/wall-bound @1G")
            for dev in DEVICES:
                km = k_mem(model, dev, 200e3, prof if model == "dense" else "tuned")
                if km == 0:
                    p(f"   {dev.label:<26} does not fit")
                    continue
                for K in sorted({min(4, km), max(1, k_max(model, dev, profile=prof if model == 'dense' else 'tuned'))}):
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
                                         offloaded_share=round(r["offl"] / r["new"], 3) if r["new"] else 0))
            p("")

    # night: more agents, slower streams acceptable (>= 5 tok/s), prefill on idle server
    p("== 24 h: day (8 h, K as interactive) + night (16 h, K up to memory with >=5 tok/s/stream), hybrid 1G")
    for model in ("dense", "flash"):
        for dev in DEVICES:
            km = k_mem(model, dev, 200e3)
            if km == 0:
                continue
            k_day = min(4, km)
            k_night = max(k_day, k_max(model, dev, floor=5.0) if model == "dense" else min(km, 8))
            day = run(model, dev, 1000, k_day, S_short)["per8h"]
            night = 2 * run(model, dev, 1000, k_night, S_short)["per8h"]
            p(f"  {MODELS[model]['name']:<11} {dev.label:<26} day {day:5.0f} (K{k_day}) + night {night:5.0f} (K{k_night})"
              f" -> 24h {day+night:5.0f}; laptop at 40% night availability {day+0.4*night:5.0f}")
    p("")

    # ---------------------------------------------------------------- economics
    p("== API price per session 20k->200k and per heavy developer-month (840 sessions)")
    api_ps = {}
    for name in API:
        c = api_cost(name, S)
        api_ps[name] = c
        p(f"  {name:<20} ${c:6.3f}/session  ${840*c:8,.0f}/month")
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
              f" per dev-month at 50%/25% use: ${840*gs*GPU_S/0.5:,.0f} / ${840*gs*GPU_S/0.25:,.0f}")
    p("")

    p("== Hybrid server part per session (M3 Max client): GPU (shadow prefill of all tokens), download")
    hyb = {}
    for model in MODELS:
        for mb in (200, 1000):
            r = run(model, DEV["m3max"], mb, 4, S)
            hyb[(model, mb)] = r
            p(f"  {MODELS[model]['name']:<11} @{mb}M: {r['srv_gpu']:5.1f} GPU-s (latency-critical part {r['srv_gpu_offl']:.1f}),"
              f" download {r['bytes']/1e9:.1f} GB, offloaded {100*r['offl']/r['new']:.0f}% of new tokens;"
              f" GPU $/dev-month at 40%/16% use: ${840*r['srv_gpu']*GPU_S/0.4:,.0f} / ${840*r['srv_gpu']*GPU_S/0.16:,.0f}")
    p("  egress per dev-month (download x 840): transit $2-9/TB (colo, 95th pct, working hours) vs cloud $50-90/TB")
    for model in MODELS:
        gb = hyb[(model, 200)]["bytes"] / 1e9 * 840
        p(f"    {MODELS[model]['name']:<11} {gb/1e3:.1f} TB/month -> colo ${gb/1e3*2:,.0f}-{gb/1e3*9:,.0f}, cloud ${gb/1e3*50:,.0f}-{gb/1e3*90:,.0f}")
    p("")

    # ---------------------------------------------------------------- company TCO
    p("== Company of N heavy developers (40 sessions/day each), 1 and 4 years, $M")
    p(f"   capex sized for the working-hour peak: GPUs = N x 5 sessions/h x GPU-s / 3600 x {PEAK} (peak + headroom)")
    p("   residual value: servers 65% after 1 y, 20% after 4 y; Mac RAM/chip delta 75% / 35% [estimates]")
    for model in MODELS:
        for N in (1000, 5000):
            lines_tco = []
            # API
            for name in (["Flash API (Alibaba)"] if model == "flash" else ["27B API median", "27B API Alibaba"]):
                for Y in (1, 4):
                    lines_tco.append((f"API {name}", Y, N * 840 * api_ps[name] * 12 * Y / 1e6, 0.0))
            # own all-server
            for ideal in (True, False):
                gpus = N * 5 * own[(model, ideal)] / 3600 * PEAK
                nodes = math.ceil(gpus / 8)
                for Y in (1, 4):
                    cash = nodes * (NODE_CAPEX + NODE_OPEX_Y * Y)
                    resid = nodes * NODE_CAPEX * (0.65 if Y == 1 else 0.20)
                    lines_tco.append((f"own all-server {'ideal' if ideal else 'realistic'} ({nodes} nodes)", Y, cash / 1e6, resid / 1e6))
            # hybrid
            gs = hyb[(model, 200)]["srv_gpu"]
            gpus = N * 5 * gs / 3600 * PEAK
            nodes = max(1, math.ceil(gpus / 8))
            kv_gb = 4 * 110e3 * MODELS[model]["kv"] / 1e9
            storage = N * kv_gb * 12.0 + N * kv_gb * 4 * 0.15     # hot DRAM $12/GB + 4x on NVMe
            tb_month = hyb[(model, 200)]["bytes"] / 1e12 * 840 * N
            for delta in (2600, 3900):
                for Y in (1, 4):
                    egress = tb_month * 12 * Y * 5.0      # $5/TB colo transit, remote staff
                    cash = nodes * (NODE_CAPEX + NODE_OPEX_Y * Y) + storage + egress + N * delta
                    resid = nodes * NODE_CAPEX * (0.65 if Y == 1 else 0.20) + N * delta * (0.75 if Y == 1 else 0.35)
                    lines_tco.append((f"hybrid ({nodes} nodes, Mac delta ${delta:,})", Y, cash / 1e6, resid / 1e6))
            p(f"  {MODELS[model]['name']}, N={N}:")
            for name, Y, cash, resid in lines_tco:
                p(f"    {name:<48} {Y}y: cash {cash:8.2f}  residual {resid:6.2f}  net {cash-resid:8.2f}")
    p("")

    # ---------------------------------------------------------------- 1M context
    p("== 1M-token context, Qwen3.8-27B (native 262k; 1M via YaRN). Session 200k->1M and 20k->1M")
    S1 = make_sessions(n=12, L0=200e3, L1=1e6, seed=11)
    S2 = make_sessions(n=12, L0=20e3, L1=1e6, seed=12)
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
              f" residency {res/3600:.2f}) -> ${gs*GPU_S:.2f} at 100% use, ${gs*GPU_S/0.25:.2f} at 25%")
        for dev in (DEV["m3max"], DEV["m5max"], DEV["ultra96"]):
            if k_mem("dense", dev, 1e6) < 1:
                continue
            loc = run("dense", dev, 0, 1, SS)
            cells = [f"local {fmt_t(loc['wall'])} (prefill {100*loc['pre_local']/loc['wall']:.0f}%)"]
            for mb in (100, 200, 1000):
                r = run("dense", dev, mb, 1, SS)
                cells.append(f"{mb}M {fmt_t(r['wall'])} x{loc['wall']/r['wall']:.1f}")
            r = run("dense", dev, 200, 1, SS)
            p(f"    {dev.label:<24} one agent: " + ", ".join(cells)
              + f"; server {r['srv_gpu']/3600:.2f} GPU-h = ${r['srv_gpu']*GPU_S:.2f}, download {r['bytes']/1e9:.0f} GB")
    p("  Ingest 1M tokens at once (27B): local full prefill vs server (1 GPU / 8 GPUs) + download of KV 8-bit + state")
    full = sum(1e3 * MODELS["dense"]["flop"](L) for L in range(0, int(1e6), 1000))
    kv_b = 1e6 * MODELS["dense"]["kv"] + MODELS["dense"]["state"]
    p(f"    FLOP {full:.2e}; KV {kv_b/2**30:.1f} GiB; server {fmt_t(full/EFF_PF)} on 1 GPU (${full/EFF_PF*GPU_S:.2f}), ~{fmt_t(full/EFF_PF/7)} on 8")
    for dev in (DEV["m3max"], DEV["m5max"], DEV["ultra96"], DEV["spark"], DEV["strix"]):
        tl = sum(1e3 / p_local("dense", dev, L) for L in range(0, int(1e6), 1000))
        p(f"    {dev.label:<26} local {fmt_t(tl)}")
    p("    download: " + ", ".join(f"{lab} {fmt_t(kv_b/bw(mb))}" for lab, mb in (("100M", 100), ("200M", 200), ("1G", 1000), ("10G", 10000))))
    p("  Prefill cost per token vs depth (FLOP): " + ", ".join(
        f"{int(L/1e3)}k 27B {MODELS['dense']['flop'](L)/1e9:.0f}G / Flash {MODELS['flash']['flop'](L)/1e9:.1f}G"
        for L in (8e3, 200e3, 1e6)))
    p("")

    # ---------------------------------------------------------------- equilibrium
    # $/session = device price / (48 months x 21 days x sessions per 8 h) + server GPU at 25% use + egress.
    # Break-even device price: the price at which hybrid cost per session equals the reference.
    own_ps = {m: own[(m, False)] * GPU_S / 0.25 for m in MODELS}
    p("== Equilibrium: cost per session and break-even device price over 4 years, 8 h/day (remote: egress $5/TB)")
    p(f"   references per session: 27B API median ${api_ps['27B API median']:.3f}, Haiku 5.5 ${api_ps['Haiku 5.5']:.3f},"
      f" Flash API ${api_ps['Flash API (Alibaba)']:.3f}; own all-server at 25% use: 27B ${own_ps['dense']:.3f}, Flash ${own_ps['flash']:.3f}")
    for row in rows:
        model = "dense" if row["model"] == "Qwen3.8-27B" else "flash"
        dev = next(d for d in DEVICES if d.label == row["device"])
        srv = row["srv_gpu_s"] * GPU_S / 0.25 + row["download_gb"] * 5.0 / 1e3
        api_ref = api_ps["27B API median"] if model == "dense" else api_ps["Flash API (Alibaba)"]
        days = 48 * 21 * row["sessions_8h"]
        row["server_usd_per_session"] = round(srv, 4)
        row["device_usd_per_session_low"] = round(dev.price[0] / days, 4) if dev.price else ""
        row["device_usd_per_session_high"] = round(dev.price[1] / days, 4) if dev.price else ""
        row["api_ref_usd_per_session"] = round(api_ref, 4)
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
        be_api = row["breakeven_device_price_vs_api"] if row["net"] != "local" else round(row["api_ref_usd_per_session"] * 48 * 21 * row["sessions_8h"])
        be_own = row["breakeven_device_price_vs_own"] if row["net"] != "local" else round(own_ps["dense" if row["model"] == "Qwen3.8-27B" else "flash"] * 48 * 21 * row["sessions_8h"])
        p(f"   {row['model'][:5]} {row['device']:<26} {row['K']:>2} {row['net']:<5} {row['sessions_8h']:7.1f}  {dev_s:>13}  {tot:>13}   ${be_api:>7,} / ${be_own:>7,}")
    p("")

    with open(os.path.join(OUT_DIR, "equilibrium.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
