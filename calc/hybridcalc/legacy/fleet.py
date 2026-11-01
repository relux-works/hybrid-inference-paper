from ..inputs import legacy_values, measurement_path
V = legacy_values('fleet')

#!/usr/bin/env python3
"""Hybrid inference (server prefill, client decode), model v4.

Builds on hybrid_calc3.py (imported; its session model, decode model and API prices are reused).
New in v4:
  * local share s: only part of a developer's agent work goes to the open model (20% now, 50% as
    a hypothesis for the end of 2027); the rest stays on frontier APIs in every option;
  * payback of the Mac premium and of the whole device, and the device that fits each share;
  * server units other than B300 nodes (RTX PRO 6000 workstations, RTX 5090 for prefill only),
    with power, colocation and support spelled out, and integer fleets for N = 5 ... 5000;
  * API price decline sensitivity;
  * 500k and 1M contexts for both models: cost per turn, fleet for 5000, client capacity;
  * precision of the transferred state and KV;
  * theoretical bounds: decode and prefill at 100% of the hardware peak vs the link;
  * one-shot ingest (meeting transcript) scenario.
Every number is an estimate unless marked [fact] or [Ivan].
"""
import contextlib
import math
import os
import sys

from . import sessions as c3                      # noqa: E402
import random                                  # noqa: E402


def host_sessions(n=V['host_sessions_L28_20'], L0=V['host_sessions_L28_27'], L1=V['host_sessions_L28_36'], seed=V['host_sessions_L28_48']):
    """Turn distribution measured on agents1 sessions (same as sensitivity_host_sample.py)."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        L, turns = L0, []
        while L < L1:
            med = V['med_L35_18'] if L < V['med_L35_30'] else V['med_L35_40']
            d = min(V['d_L36_20'], rnd.lognormvariate(math.log(med), V['d_L36_60']))
            o = min(V['o_L37_20'], rnd.lognormvariate(math.log(V['o_L37_53']), V['o_L37_59']))
            tau = rnd.lognormvariate(math.log(2.0), 1.0)
            turns.append((L, d, o, tau))
            L += d + o
        out.append(turns)
    return out


MODELS, API = c3.MODELS, c3.API
Dev = c3.Dev

# ---------------------------------------------------------------- client devices (prices 2026-10-30)
BASELINE_LAPTOP = V['BASELINE_LAPTOP_L49_18']           # [fact] MacBook Pro 14" M5 Pro base, what a developer gets anyway
DEVICES = [
    Dev("m5pro", "M5 Pro 64 GB (MBP 14)", V['DEVICES_L51_42'], V['DEVICES_L51_46'], 1.0, V['DEVICES_L51_56'], (V['DEVICES_L51_62'], V['DEVICES_L51_68']), "[fact] Apple store, 18C/20C, 1 TB"),
    Dev("strix", "Ryzen AI Max+ 395 128 GB", V['DEVICES_L52_45'], V['DEVICES_L52_50'], 1.0, V['DEVICES_L52_60'], (V['DEVICES_L52_66'], V['DEVICES_L52_72']), "[fact] Framework $3,449, GMKtec $3,500-3,650"),
    Dev("spark", "DGX Spark 128 GB", V['DEVICES_L53_37'], V['DEVICES_L53_42'], 1.0, V['DEVICES_L53_52'], (V['DEVICES_L53_58'], V['DEVICES_L53_64']), "[fact] $6,950 since 2026-10-02"),
    Dev("m3max", "M3 Max 128 GB", V['DEVICES_L54_34'], V['DEVICES_L54_39'], 1.0, 1.0, None, "owned"),
    Dev("m5max64", "M5 Max 64 GB (MBP 14)", V['DEVICES_L55_44'], V['DEVICES_L55_48'], 1.0, V['DEVICES_L55_58'], (V['DEVICES_L55_64'], V['DEVICES_L55_70']), "[fact] Apple store, 40C GPU, 2 TB"),
    Dev("m5max", "M5 Max 128 GB (MBP 14)", V['DEVICES_L56_43'], V['DEVICES_L56_48'], 1.0, V['DEVICES_L56_58'], (V['DEVICES_L56_64'], V['DEVICES_L56_70']), "[fact] Apple store, 40C GPU, 2 TB"),
    Dev("ultra96", "M5 Ultra 96 GB (Studio)", V['DEVICES_L57_46'], V['DEVICES_L57_50'], V['DEVICES_L57_56'], V['DEVICES_L57_62'], (V['DEVICES_L57_68'], V['DEVICES_L57_74']), "[fact] 64C GPU"),
    Dev("ultra256", "M5 Ultra 256 GB (Studio)", V['DEVICES_L58_48'], V['DEVICES_L58_53'], V['DEVICES_L58_59'], V['DEVICES_L58_65'], (V['DEVICES_L58_71'], V['DEVICES_L58_78']), "[fact] 80C GPU; 64C GPU $9,499"),
]
# peak dense FP16/BF16 matmul, FLOP/s [research 2026-10-30: measured where available, else estimate]
PEAK16 = {"m5pro": V['PEAK16_L61_19'], "strix": V['PEAK16_L61_37'], "spark": V['PEAK16_L61_53'], "m3max": V['PEAK16_L61_70'], "m5max64": V['PEAK16_L61_88'], "m5max": V['PEAK16_L61_104'],
          "ultra96": V['PEAK16_L62_21'], "ultra256": V['PEAK16_L62_41']}
DEV = {d.key: d for d in DEVICES}
MAC_RESID = {1: V['MAC_RESID_L64_16'], V['MAC_RESID_L64_22']: V['MAC_RESID_L64_25']}   # residual share of the device price after 1 and 4 years


# ---------------------------------------------------------------- server units
class Unit:
    """A purchasable server unit: GPUs, capex, yearly opex split into energy, colocation, support."""

    def __init__(self, key, label, gpus, pf8, mfu, hbm_bw, mem, w_res, capex, kw, where, stream_tps, batch, note):
        self.key, self.label, self.gpus, self.note = key, label, gpus, note
        self.eff_pf = pf8 * mfu                 # FLOP/s per GPU for prefill
        self.bw = hbm_bw * V['self_bw_L74_27']                  # bytes/s per GPU for decode
        self.kv_mem = mem - w_res               # bytes per GPU left for KV after weights and workspace
        self.capex, self.kw, self.where = capex, kw, where
        self.stream_tps, self.batch = stream_tps, batch    # stream_tps: {model: tok/s per decode stream}

    def opex_y(self):
        if self.where == "dc":     # energy at average load 70%, PUE 1.3; colo space+cooling per kW; support 4%/y
            energy = self.kw * V['energy_L81_31'] * V['energy_L81_37'] * V['energy_L81_44'] * PRICE_KWH_DC
            colo = self.kw * COLO_KW_MONTH * V['colo_L82_45']
            support = V['support_L83_22'] * self.capex
        else:                      # office: energy at 50% load plus 30% for air conditioning; no colo
            energy = self.kw * V['energy_L85_31'] * V['energy_L85_38'] * PRICE_KWH_OFFICE * V['energy_L85_63']
            colo = V['colo_L86_19']
            support = V['support_L87_22'] * self.capex
        return energy, colo, support

    def gpu_s_price(self):
        """$ per GPU-second at 100% use over 4 years (straight line, no residual)."""
        return (self.capex / V['gpu_s_price_L92_29'] + sum(self.opex_y()) / V['gpu_s_price_L92_55']) / (self.gpus * V['gpu_s_price_L92_74'] * 3600)


PRICE_KWH_DC = V['PRICE_KWH_DC_L95_15']             # [fact] US industrial 9.09-9.64 c/kWh in 2026 (EIA)
PRICE_KWH_OFFICE = V['PRICE_KWH_OFFICE_L96_19']
COLO_KW_MONTH = V['COLO_KW_MONTH_L97_16']            # [fact-based] CBRE $196/kW-month avg H2 2025, large deals $145-185; energy on top
RTX6000 = V['RTX6000_L98_10']                  # [fact] US Workstation Edition $16,000-18,600 (NVIDIA $16,000); Server Edition ~$23,000
RTX_PF8 = V['RTX_PF8_L99_10']              # [fact] RTX PRO 6000 dense FP8, FP16 or FP32 accumulate (whitepaper)
R5090_PF8 = V['R5090_PF8_L100_12']             # [fact] RTX 5090 dense FP8 with FP32 accumulate (838 with FP16 accumulate)
RTX5090 = V['RTX5090_L101_10']                   # [fact] street $5,000-7,000 in October 2026 (MSRP $1,999)
B300_NODE = V['B300_NODE_L102_12'] * V['B300_NODE_L102_20']          # [fact] ~$550k per 8-GPU node in the US (Reuters 2026-04); +20% fabric, racks, install
UNITS = [
    # key, label, gpus, FP8 dense, MFU, HBM bw, memory, weights+workspace, capex, kW, where, stream tok/s, batch
    Unit("b300", "HGX B300 node (8 GPU), DC", 8, V['UNITS_L105_49'], V['UNITS_L105_57'], V['UNITS_L105_63'], V['UNITS_L105_69'], V['UNITS_L105_76'], B300_NODE, V['UNITS_L105_93'], "dc",
         {"dense": V['UNITS_L106_19'], "flash": 60.0}, V['UNITS_L106_41'], "book price"),
    Unit("rtx8", "8x RTX PRO 6000 Server, DC", 8, RTX_PF8, V['UNITS_L107_59'], V['UNITS_L107_65'], V['UNITS_L107_75'], V['UNITS_L107_81'], 8 * V['UNITS_L107_91'] + V['UNITS_L107_99'], V['UNITS_L107_106'], "dc",
         {"dense": V['UNITS_L108_19'], "flash": V['UNITS_L108_34']}, 8, "Server Edition ~$23k each, host with 1 TB RAM"),
    Unit("rtx4", "4x RTX PRO 6000 server, office", V['UNITS_L109_51'], RTX_PF8, V['UNITS_L109_63'], V['UNITS_L109_69'], V['UNITS_L109_78'], V['UNITS_L109_84'], V['UNITS_L109_90'] * RTX6000 + V['UNITS_L109_104'], V['UNITS_L109_111'], "office",
         {"dense": V['UNITS_L110_19'], "flash": V['UNITS_L110_34']}, 8, "GPUs + host with 512 GB RAM"),
    Unit("rtx1", "1x RTX PRO 6000 workstation, office", 1, RTX_PF8, V['UNITS_L111_68'], V['UNITS_L111_74'], V['UNITS_L111_83'], V['UNITS_L111_89'], RTX6000 + V['UNITS_L111_105'], V['UNITS_L111_112'], "office",
         {"dense": V['UNITS_L112_19'], "flash": V['UNITS_L112_34']}, 8, "GPU + host with 128 GB RAM, 8 TB NVMe"),
    Unit("r5090", "1x RTX 5090 box, office (prefill only)", 1, R5090_PF8, V['UNITS_L113_74'], V['UNITS_L113_80'], V['UNITS_L113_89'], V['UNITS_L113_95'], RTX5090 + V['UNITS_L113_111'], V['UNITS_L113_117'], "office",
         None, 0, "4-bit weights; one session's KV at a time; GeForce licence: not for datacenters"),
]
OFFICE_UNITS = ("r5090", "rtx1", "rtx4")
DC_UNITS = ("rtx8", "b300")
UNIT = {u.key: u for u in UNITS}
B300_EFF = UNIT["b300"].eff_pf
SRV_RESID = {1: V['SRV_RESID_L120_16'], V['SRV_RESID_L120_22']: V['SRV_RESID_L120_25']}
PEAK = V['PEAK_L121_7']
SESS_PER_H = V['SESS_PER_H_L122_13']                 # heavy developer: 40 sessions per 8 h day
DAYS_MONTH = V['DAYS_MONTH_L123_13']
EGRESS_TB = V['EGRESS_TB_L124_12']                  # $/TB colo transit, remote staff (office: 0)


# ---------------------------------------------------------------- helpers
@contextlib.contextmanager
def patched(model, **kw):
    old = {k: MODELS[model][k] for k in kw}
    MODELS[model].update(kw)
    try:
        yield
    finally:
        MODELS[model].update(old)


def own_gpu_s(model, sessions, ideal, u):
    """All-server on unit u: prefill + decode bandwidth + KV residency, GPU-seconds per session."""
    m = MODELS[model]
    pre = dec = res = V['pre_L141_22']
    for turns in sessions:
        for (L, d, o, tau) in turns:
            pre += d * m["flop"](L) / u.eff_pf
            if model == "dense":
                per_tok = (m["w_srv"] / u.batch + (L + d) * m["kv"] + 2 * m["state"]) / u.bw
            else:
                B = u.batch * V['B_L148_30']
                touched = 1 - (1 - V['touched_L149_35'] / V['touched_L149_40']) ** B
                w_step = V['w_step_L150_25'] + touched * (m["w_srv"] - V['w_step_L150_55'])
                per_tok = (w_step / B + V['per_tok_L151_40'] * m["kv"] + V['per_tok_L151_57'] * (L + d) + V['per_tok_L151_73'] * m["state"]) / u.bw
            dec += o * per_tok
            busy = o / u.stream_tps[model] + (0 if ideal else tau)
            res += (L + d) * m["kv"] * busy / u.kv_mem
    n = len(sessions)
    return pre / n, dec / n, res / n


def fleet_cost(units_needed_gpus, u, years):
    n = max(1, math.ceil(units_needed_gpus / u.gpus))
    cash = n * (u.capex + sum(u.opex_y()) * years)
    resid = n * u.capex * SRV_RESID[years]
    return n, cash, resid


def best_fleet(gpu_s_b300_eq, sessions_per_h, years, keys, own_model=None, sessions=None, ideal=False):
    """Cheapest fleet among unit types. For the hybrid, GPU-s are FLOP-bound and rescale by eff_pf;
    for the all-server cluster they are recomputed per unit type (bandwidth and memory differ)."""
    best = None
    for k in keys:
        u = UNIT[k]
        if own_model:
            if not u.stream_tps:
                continue
            gs = sum(own_gpu_s(own_model, sessions, ideal, u))
        else:
            gs = gpu_s_b300_eq * B300_EFF / u.eff_pf
        gpus = sessions_per_h * gs / 3600 * PEAK
        n, cash, resid = fleet_cost(gpus, u, years)
        if best is None or cash - resid < best[3] - best[4]:
            best = (k, n, gpus, cash, resid)
    return best


def kv_store_cost(n_people, model, parked=V['kv_store_cost_L185_42'], active=V['kv_store_cost_L185_53'], L_avg=V['kv_store_cost_L185_62']):
    """Server KV store for the hybrid: active sessions in DRAM, parked ones on NVMe (x1.5 redundancy)."""
    per = L_avg * MODELS[model]["kv"] + MODELS[model]["state"]
    dram = n_people * active * per / 1e9 * DRAM_GB
    nvme = n_people * parked * per / 1e12 * V['nvme_L189_44'] * NVME_TB
    return dram + nvme


DRAM_GB = V['DRAM_GB_L193_10']                   # [fact-based] DDR5 RDIMM contract ~$25-35/GB, retail $42-64/GB (Oct 2026)
NVME_TB = V['NVME_TB_L194_10']                  # [fact] in-stock 15-61 TB enterprise NVMe $450-1,197/TB (median ~$920) in Oct 2026


def fmt(x):
    return f"{x:,.0f}"


def demand_gpu_s_price(u):
    """$ per GPU-second of demand on unit u: the fleet is sized for the working-hour peak and idles
    off-hours (8 h x 21 days), 4-year straight line net of the 20% residual."""
    per_gpu_month = (u.capex * (1 - SRV_RESID[4]) / V['per_gpu_month_L204_52'] + sum(u.opex_y()) / V['per_gpu_month_L204_75']) / u.gpus
    util = DAYS_MONTH * 8 / (V['util_L205_29'] * PEAK)
    return per_gpu_month / (V['demand_gpu_s_price_L206_28'] * 3600) / util


def device_k(model, key):
    dev = DEV[key]
    km = c3.k_mem(model, dev, V['km_L211_30'])
    return min(km, max(V['device_k_L212_23'], c3.k_max(model, dev))) if km else 0


def pick_device(model, s, cap):
    need = SESS_PER_H * 8 * s
    order = ("m5pro", "m5max64", "m5max", "ultra96") if model == "dense" else ("m5max", "ultra256")
    return next((k for k in order if k in cap and cap[k][1] >= V['pick_device_L218_63'] * need), order[-1])


def units_for(N, own):
    if N <= V['units_for_L222_12']:
        return ("rtx1", "rtx4") if own else OFFICE_UNITS
    if N <= V['units_for_L224_12']:
        return ("rtx1", "rtx4") + DC_UNITS if own else OFFICE_UNITS + DC_UNITS
    return DC_UNITS


# ---------------------------------------------------------------- report
def main():
    out = []
    p = out.append
    S = c3.make_sessions()
    S80 = S[:80]
    SH = host_sessions()
    T0 = sum(map(len, S)) / len(S)
    api_ps = {n: c3.api_cost(n, S) for n in API}
    util = DAYS_MONTH * 8 / (V['util_L238_29'] * PEAK)

    p("== 0. Inputs")
    p(f"  heavy developer: {SESS_PER_H*8:.0f} sessions/day of 20k->200k ({T0:.0f} turns each), {DAYS_MONTH} days/month;"
      f" fleets sized for the working-hour peak x{PEAK}, idle off-hours -> effective utilization {V['main_L242_98']*util:.1f}%")
    p(f"  Mac premium = device price - ${BASELINE_LAPTOP:,} (MBP 14 M5 Pro base); residual 75% after 1 y, 35% after 4 y;"
      f" servers 65% / 20%; remote egress ${EGRESS_TB}/TB")
    p("  server units: capex, opex per year = energy + colocation + support; $/GPU-h at 100% use, and per GPU-h of demand")
    for u in UNITS:
        e, c, s_ = u.opex_y()
        p(f"    {u.label:<40} ${fmt(u.capex):>8}  opex ${fmt(e)} + {fmt(c)} + {fmt(s_)} = ${fmt(e+c+s_)}/y"
          f"  ${u.gpu_s_price()*3600:.2f} / ${demand_gpu_s_price(u)*3600:.2f} per GPU-h  {u.eff_pf/1e12:.0f} TFLOP/s ({u.note})")
    p("")

    cap = {}
    for model in MODELS:
        for key in ("m5pro", "m5max64", "m5max", "ultra96", "ultra256"):
            K = device_k(model, key)
            if K:
                cap[(model, key)] = (K, c3.run(model, DEV[key], 1000, K, S80)["per8h"])

    # ------------------------------------------------ 1. the chain: own all-server vs hybrid, s = 100%
    N = V['N_L260_8']
    p(f"== 1. Own all-server vs hybrid, step by step: {N} heavy developers, all their agent work on the open model, B300 nodes, 4 years")
    chain = {}
    for model in ("dense", "flash"):
        m = MODELS[model]
        u = UNIT["b300"]
        p(f"  {m['name']}:")
        for ideal in (False, True):
            pre, dec, res = own_gpu_s(model, S, ideal, u)
            gs = pre + dec + res
            gpus = N * SESS_PER_H * gs / 3600 * PEAK
            n, cash, resid = fleet_cost(gpus, u, V['_n__cash__resid__L271_49'])
            per = (cash - resid) / (N * V['per_L272_40'])
            chain[(model, "own", ideal)] = per
            p(f"    own {'ideal    ' if ideal else 'realistic'}: GPU-s per session = prefill {pre:.1f} + decode {dec:.1f} + KV residency {res:.1f}"
              f" = {gs:.1f}; GPUs at peak = {N} x {SESS_PER_H:.0f}/h x {gs:.1f} / 3600 x {PEAK} = {gpus:.0f} -> {n} nodes;"
              f" capex ${cash-sum(u.opex_y())*V['main_L276_46']*n:,.0f}, opex ${sum(u.opex_y())*n:,.0f}/y, residual ${resid:,.0f} -> ${per:.0f}/dev-month")
        key = "m5max"
        K = cap[(model, key)][0]
        r = c3.run(model, DEV[key], 1000, K, S)
        gpus = N * SESS_PER_H * r["srv_gpu"] / 3600 * PEAK
        n, cash, resid = fleet_cost(gpus, u, V['_n__cash__resid__L281_45'])
        srv = (cash - resid) / (N * V['srv_L282_36'])
        store = kv_store_cost(N, model) / (N * V['store_L283_47'])
        egress = r["bytes"] / 1e12 * V['egress_L284_37'] * EGRESS_TB
        premium = DEV[key].price[1] - BASELINE_LAPTOP
        mac = premium * (1 - MAC_RESID[4]) / V['mac_L286_45']
        chain[(model, "hyb")] = (srv, store, egress, mac)
        p(f"    hybrid: server GPU-s per session = {r['srv_gpu']:.1f} (prefill of every new and generated token);"
          f" GPUs at peak {gpus:.0f} -> {n} nodes -> ${srv:.0f}; KV store ${store:.0f}; egress ${egress:.0f} (remote only);"
          f" Mac premium ${premium:,} x 65% / 48 = ${mac:.0f} -> ${srv+store+mac:.0f} office / ${srv+store+mac+egress:.0f} remote per dev-month")
        api_names = ("27B API median", "27B API Alibaba", "27B API DeepInfra") if model == "dense" else ("Flash API (Alibaba)",)
        p("    API: " + ", ".join(f"{a} ${V['main_L292_42']*api_ps[a]:.0f}" for a in api_names) + " per dev-month")
    p("")

    # ------------------------------------------------ 2. share s, device that fits, payback
    p(f"== 2. Local share s of the agent work, device that fits it, payback ({N} developers, B300 server)")
    p("   device fits when its 1G capacity >= 1.25 x daily local sessions; savings = reference - hybrid running cost")
    p("   (server fleet + KV store, + egress for remote staff); payback = premium (or the whole price) / savings")
    for model, shares in (("dense", (V['main_L299_37'], V['main_L299_42'], 1.0)), ("flash", (V['main_L299_65'], V['main_L299_70'], 1.0))):
        for s in shares:
            key = pick_device(model, s, {k: v for (mm, k), v in cap.items() if mm == model})
            dev = DEV[key]
            K = cap[(model, key)][0]
            r = c3.run(model, dev, 1000, K, S80)
            sess_m = V['sess_m_L305_21'] * s
            k, n, gpus, cash, resid = best_fleet(r["srv_gpu"], N * SESS_PER_H * s, V['_k__n__gpus__cash__resid__L306_83'], DC_UNITS)
            run_m = (cash - resid) / (N * V['run_m_L307_42']) + kv_store_cost(N, model) / (N * V['run_m_L307_79'])
            egress_m = r["bytes"] / 1e12 * sess_m * EGRESS_TB
            premium = dev.price[1] - BASELINE_LAPTOP
            p(f"  {MODELS[model]['name']} s={int(s*V['main_L310_51'])}%: {sess_m:.0f} local sessions/month -> {dev.label} (K{K},"
              f" {cap[(model, key)][1]:.0f}/8h at 1G), premium ${premium:,}; running cost ${run_m:.0f} office / ${run_m+egress_m:.0f} remote"
              f" ({n}x {k})")
            refs = ("27B API median", "27B API Alibaba", "27B API DeepInfra", "own") if model == "dense" else ("Flash API (Alibaba)", "own")
            for ref in refs:
                if ref == "own":
                    kk, nn, g2, c2, r2 = best_fleet(0, N * SESS_PER_H * s, V['_kk__nn__g2__c2__r2__L316_75'], DC_UNITS, own_model=model, sessions=S80)
                    ref_m, lab = (c2 - r2) / (N * V['_ref_m__lab__L317_50']), f"own all-server ({nn}x {kk})"
                else:
                    ref_m, lab = sess_m * api_ps[ref], ref
                cells = []
                for where, extra in (("office", 0.0), ("remote", egress_m)):
                    sav = ref_m - run_m - extra
                    if sav <= 0:
                        cells.append(f"{where}: no saving")
                        continue
                    net4 = V['net4_L326_27'] * sav - premium * (1 - MAC_RESID[4])
                    cells.append(f"{where}: saves ${sav:.0f}/mo, premium back in {premium/sav:.0f} mo, whole device in"
                                 f" {dev.price[1]/sav:.0f} mo, 4-y net ${fmt(net4)}")
                p(f"     vs {lab:<30} ${ref_m:6.0f}/mo | " + " | ".join(cells))
    p("")

    # ------------------------------------------------ 3. frontier shift, for scale
    p("== 3. For scale: moving work from frontier APIs to the open model (any deployment), per heavy developer-month")
    for fr in ("Opus 5.5", "Sonnet 5.5"):
        cells = [f"s={int(s*V['cells_L335_28'])}%: frontier part ${V['cells_L335_52']*(1-s)*api_ps[fr]:,.0f}" for s in (V['cells_L335_90'], V['cells_L335_95'])]
        shift = V['shift_L336_16'] * V['shift_L336_22'] * (api_ps[fr] - api_ps["27B API median"])
        p(f"  {fr:<10} ${api_ps[fr]:.2f}/session; " + ", ".join(cells) + f"; 20%->50% saves ${shift:,.0f}/month at 27B API prices")
    p("")

    # ------------------------------------------------ 4. scale curve
    p("== 4. Scale curve, Qwen3.8-27B, 4 years, $ per developer-month net of residual")
    p("   office units up to 50 people (RTX 5090 only in the office: GeForce licence), datacenter units from 50")
    p("   N      s   | API median | own all-server: fleet, capex, $/mo | hybrid: server fleet, capex, $/mo office/remote | up-front hybrid (server + store + Macs)")
    scale = {}
    for s in (V['main_L345_14'], V['main_L345_19'], 1.0):
        key = pick_device("dense", s, {k: v for (mm, k), v in cap.items() if mm == "dense"})
        dev = DEV[key]
        r = c3.run("dense", dev, 1000, cap[("dense", key)][0], S80)
        premium = dev.price[1] - BASELINE_LAPTOP
        for Nn in (V['main_L350_19'], V['main_L350_22'], V['main_L350_26'], V['main_L350_30'], V['main_L350_35']):
            api_m = V['api_m_L351_20'] * s * api_ps["27B API median"]
            ko, no, go, co, ro = best_fleet(0, Nn * SESS_PER_H * s, V['_ko__no__go__co__ro__L352_68'], units_for(Nn, True), own_model="dense", sessions=S80)
            own_m = (co - ro) / (Nn * V['own_m_L353_38'])
            kh, nh, gh, ch, rh = best_fleet(r["srv_gpu"], Nn * SESS_PER_H * s, V['_kh__nh__gh__ch__rh__L354_79'], units_for(Nn, False))
            store = kv_store_cost(Nn, "dense")
            mac_net = Nn * premium * (1 - MAC_RESID[4])
            hyb_m = (ch - rh + store + mac_net) / (Nn * V['hyb_m_L357_56'])
            egress_m = r["bytes"] / 1e12 * V['egress_m_L358_43'] * s * EGRESS_TB
            capex_srv = nh * UNIT[kh].capex
            scale[(Nn, s)] = (api_m, own_m, hyb_m, hyb_m + egress_m)
            p(f"  {Nn:>5} {int(s*V['main_L361_33']):>3}% | ${api_m:7.0f}   | {no}x {ko:<5} ${fmt(no*UNIT[ko].capex):>11} ${own_m:6.0f} |"
              f" {nh}x {kh:<5} ${fmt(capex_srv):>11} ${hyb_m:6.0f}/{hyb_m+egress_m:.0f} | ${fmt(capex_srv + store + Nn*premium)}"
              f" ({key}, premium ${premium:,})")
    p("")

    # ------------------------------------------------ 4b. what one server unit carries
    p("== 4b. What one server unit carries (27B, 20k->200k sessions): heavy developers at s = 100% / 50% / 20%, and agents")
    r = c3.run("dense", DEV["m5max"], 1000, cap[("dense", "m5max")][0], S80)
    for u in UNITS:
        gs_h = r["srv_gpu"] * B300_EFF / u.eff_pf
        devs_h = u.gpus * 3600 / (SESS_PER_H * gs_h * PEAK)
        line = (f"  {u.label:<40} ${fmt(u.capex):>8}: hybrid prefill {gs_h:5.0f} GPU-s/session -> {devs_h:6.1f} / {2*devs_h:6.1f} / {V['line_L372_133']*devs_h:6.1f}"
                f" developers, ~{devs_h*V['line_L373_40']:.0f} agents at K7")
        if u.stream_tps:
            gs_o = sum(own_gpu_s("dense", S80, False, u))
            devs_o = u.gpus * 3600 / (SESS_PER_H * gs_o * PEAK)
            sess_fit = u.gpus * u.kv_mem / (V['sess_fit_L377_44'] * MODELS["dense"]["kv"])
            line += f" | all-server {gs_o:5.0f} GPU-s/session -> {devs_o:5.1f} / {2*devs_o:5.1f} / {V['main_L378_100']*devs_o:5.1f}; KV of {sess_fit:.0f} sessions at 110k fits in VRAM"
        p(line)
    p("")

    # ------------------------------------------------ 4c. startup of 10 heavy developers, server choices side by side
    p("== 4c. Startup of 10 heavy developers, 27B, 4 years: each server choice side by side ($ per developer-month, office)")
    for s in (V['main_L384_14'], V['main_L384_19'], 1.0):
        key = pick_device("dense", s, {k: v for (mm, k), v in cap.items() if mm == "dense"})
        dev = DEV[key]
        r = c3.run("dense", dev, 1000, cap[("dense", key)][0], S80)
        premium = dev.price[1] - BASELINE_LAPTOP
        mac_m = premium * (1 - MAC_RESID[4]) / V['mac_m_L389_47']
        cells = [f"API median ${V['cells_L390_32']*s*api_ps['27B API median']:.0f}"]
        for k in ("r5090", "rtx1", "rtx4"):
            kk, n, g, c, rr = best_fleet(r["srv_gpu"], V['_kk__n__g__c__rr__L392_55'] * SESS_PER_H * s, V['_kk__n__g__c__rr__L392_76'], (k,))
            srv_m = (c - rr) / (V['srv_m_L393_32'] * V['srv_m_L393_37'])
            cells.append(f"hybrid {n}x {k} (${fmt(n*UNIT[k].capex)}) ${srv_m + mac_m + kv_store_cost(V['main_L394_101'], 'dense')/(V['main_L394_115']):.0f}")
        for k in ("rtx1", "rtx4"):
            kk, n, g, c, rr = best_fleet(0, V['_kk__n__g__c__rr__L396_44'] * SESS_PER_H * s, V['_kk__n__g__c__rr__L396_65'], (k,), own_model="dense", sessions=S80)
            cells.append(f"own {n}x {k} (${fmt(n*UNIT[k].capex)}) ${(c - rr)/V['main_L397_77']:.0f}")
        p(f"  s={int(s*V['main_L398_23']):>3}% ({dev.label.split(' (')[0]}, premium ${premium:,} = ${mac_m:.0f}/mo): " + "; ".join(cells))
    p("")

    # ------------------------------------------------ 5. API price decline
    p("== 5. If API prices for this model class fall: 4-year average API price vs the hybrid (N=5000, office/remote)")
    for r_ in (0.0, V['main_L403_20'], V['main_L403_25']):
        mult = sum((1 - r_) ** y for y in range(V['mult_L404_48'])) / V['mult_L404_54']
        cells = [f"s={int(s*V['cells_L405_28'])}%: API ${scale[(V['cells_L405_49'], s)][0]*mult:.0f} vs hybrid ${scale[(V['cells_L405_91'], s)][2]:.0f}/{scale[(V['cells_L405_117'], s)][3]:.0f}"
                 for s in (V['cells_L406_27'], V['cells_L406_32'], 1.0)]
        p(f"  decline {int(r_*V['main_L407_30']):>2}%/year (x{mult:.2f}): " + "; ".join(cells))
    p("")

    # ------------------------------------------------ 6. long contexts
    gpx = demand_gpu_s_price(UNIT["b300"])
    p("== 6. Long contexts, per 1000 agent turns (B300 fleet priced per GPU-s of demand; egress $5/TB; device at 8 h/day over 4 years)")
    profiles = [("20k->200k", S80), ("20k->500k", c3.make_sessions(n=V['profiles_L413_69'], L0=V['profiles_L413_76'], L1=V['profiles_L413_85'], seed=V['profiles_L413_97'])),
                ("20k->1M", c3.make_sessions(n=V['profiles_L414_47'], L0=V['profiles_L414_54'], L1=V['profiles_L414_63'], seed=V['profiles_L414_73'])),
                ("200k->1M", c3.make_sessions(n=V['profiles_L415_48'], L0=V['profiles_L415_55'], L1=V['profiles_L415_65'], seed=V['profiles_L415_75']))]
    for model in ("dense", "flash"):
        m = MODELS[model]
        p(f"  {m['name']}:")
        base = None
        for lab, SS in profiles:
            nt = sum(map(len, SS)) / len(SS)
            api_names = ("27B API median", "Haiku 5.5", "Sonnet 5.5", "Opus 5.5") if model == "dense" else ("Flash API (Alibaba)",)
            api_t = ", ".join(f"{a.replace(' API median', '')} ${c3.api_cost(a, SS)/nt*1000:.1f}" for a in api_names)
            own_r = sum(own_gpu_s(model, SS, False, UNIT["b300"])) / nt
            own_i = sum(own_gpu_s(model, SS, True, UNIT["b300"])) / nt
            Lend = V['Lend_L426_19'] if lab == "20k->200k" else V['Lend_L426_52'] if lab == "20k->500k" else 1e6
            cells = []
            for key in ("m5max", "ultra256"):
                K = min(c3.k_mem(model, DEV[key], Lend), 8)
                if K == 0:
                    cells.append(f"{DEV[key].label.split(' (')[0]}: does not fit")
                    continue
                rr = c3.run(model, DEV[key], 1000, K, SS)
                turns8 = rr["per8h"] * nt
                prem = DEV[key].price[1] - (BASELINE_LAPTOP if key == "m5max" else 0)
                dev_t = prem * (1 - MAC_RESID[4]) / (V['dev_t_L436_53'] * DAYS_MONTH) / turns8 * 1000
                srv_t = rr["srv_gpu"] / nt * 1000 * gpx
                eg_t = rr["bytes"] / nt * 1000 / 1e12 * EGRESS_TB
                cells.append(f"{DEV[key].label.split(' (')[0]} K{K} {turns8:,.0f} turns/8h: server ${srv_t:.1f} + egress ${eg_t:.1f}"
                             f" + device ${dev_t:.1f} = ${srv_t+eg_t+dev_t:.1f}")
                if key == "m5max":
                    hyb_gs = rr["srv_gpu"] / nt
            if base is None:
                base = (own_r, hyb_gs)
            p(f"    {lab:<9} {nt:4.0f} turns/session | API {api_t} | own ${own_i*1000*gpx:.1f}-{own_r*1000*gpx:.1f}"
              f" (GPU-s/turn x{own_r/base[0]:.1f} vs 200k) | hybrid server GPU-s/turn x{hyb_gs/base[1]:.1f}")
            p("              hybrid: " + " | ".join(cells))
    p("")

    # ------------------------------------------------ 7. precision of the transferred state and KV
    p("== 7. Precision of what crosses the network (27B): sessions per 8 h and GB downloaded per session")
    st = c3.state_bytes(V['st_L452_24'], 1)
    variants = [("state fp32, KV 8-bit", V['variants_L453_41'] * st, V['variants_L453_49'] * 2 * V['variants_L453_58'] * V['variants_L453_62']), ("state bf16, KV 8-bit", 2 * st, V['variants_L453_101'] * 2 * V['variants_L453_110'] * V['variants_L453_114']),
                ("state fp8,  KV 8-bit", st, V['variants_L454_45'] * 2 * V['variants_L454_54'] * V['variants_L454_58']), ("state bf16, K8 V4", 2 * st, V['variants_L454_94'] * V['variants_L454_99'] * V['variants_L454_103'] * V['variants_L454_109']),
                ("state fp8,  K8 V4", st, V['variants_L455_42'] * V['variants_L455_47'] * V['variants_L455_51'] * V['variants_L455_57'])]
    for dist, SS in (("synthetic", S80), ("agents1 sample", SH)):
        p(f"  turn distribution: {dist}")
        for key, K in (("m3max", V['main_L458_33']), ("m5max", V['main_L458_47'])):
            for lab, sb, kvb in variants:
                with patched("dense", state=sb, kv=kvb):
                    cells = []
                    for mb in (V['main_L462_31'], V['main_L462_36'], 1000):
                        rr = c3.run("dense", DEV[key], mb, K, SS)
                        cells.append(f"{mb}M {rr['per8h']:5.1f} ({rr['bytes']/1e9:4.1f} GB)")
                p(f"    {DEV[key].label:<22} K{K} {lab:<22} " + "  ".join(cells))
    p("")

    # ------------------------------------------------ 8. bounds
    p("== 8. Bounds: link rate in tokens/s (what offload delivers) vs local prefill")
    for model in ("dense", "flash"):
        kvb = MODELS[model]["kv"]
        p(f"  {MODELS[model]['name']}: KV {kvb/1024:.1f} KiB/token -> link delivers "
          + ", ".join(f"{lab} {c3.bw(mb)/kvb:,.0f} tok/s" for lab, mb in (("100M", V['main_L473_83']), ("200M", V['main_L473_98']), ("1G", 1000), ("10G", V['main_L473_126'])))
          + f"; plus {MODELS[model]['state']/1e6:.0f} MB of state per offload")
    p("  27B prefill FLOP per token: " + ", ".join(f"{int(L/1e3)}k {MODELS['dense']['flop'](L)/1e9:.0f} G" for L in (V['main_L475_117'], V['main_L475_123'], V['main_L475_130'], V['main_L475_137'], 1e6)))
    p("  prefill at depth: our working rate | bound at 100% of peak FP16 (tok/s) -- vs what the link delivers above")
    for model, Ls in (("dense", (V['main_L477_33'], 1e6)), ("flash", (V['main_L477_58'], 1e6))):
        p(f"   {MODELS[model]['name']} at {int(Ls[0]/1e3)}k / {int(Ls[1]/1e3)}k:")
        for dev in DEVICES:
            pk = PEAK16[dev.key]
            cur = [c3.p_local(model, dev, L) for L in Ls]
            bnd = [pk / MODELS[model]["flop"](L) for L in Ls]
            p(f"    {dev.label:<26} working {cur[0]:6.0f} / {cur[1]:6.0f} | bound {bnd[0]:6.0f} / {bnd[1]:6.0f}"
              f"  (working = {V['main_L484_30']*cur[0]/bnd[0]:.0f}% of peak; peak {pk/1e12:.0f} TFLOP/s)")
    p("  27B decode bound at 100% bandwidth, one stream (3.5-bit weights, 8-bit KV), tok/s at 20k / 200k / 1M:")
    for dev in DEVICES:
        cells = [f"{dev.bw*1e9/(V['cells_L487_32'] + L*V['cells_L487_43'] + 2*MODELS['dense']['state']):.0f}" for L in (V['cells_L487_95'], V['cells_L487_101'], 1e6)]
        p(f"    {dev.label:<26} {' / '.join(cells)}")
    p("")

    # ------------------------------------------------ 9. one-shot ingest: meeting transcript
    p("== 9. One-shot ingest: a 1-3 h meeting transcript (70k tokens), a 3k-token summary, then 10 questions (100 in / 700 out)")
    d0, o0 = V['_d0__o0__L493_13'], V['_d0__o0__L493_19']
    flops = sum(1e3 * MODELS["dense"]["flop"](L) for L in range(0, int(d0), 1000))
    air = Dev("m5", "M5 32 GB (MacBook Air)", V['air_L495_46'], V['air_L495_50'], 1.0, V['air_L495_60'], None, "estimate: half an M5 Pro's GPU")
    for dev in (air, DEV["m3max"], DEV["m5pro"], DEV["m5max"]):
        tl = sum(1e3 / c3.p_local("dense", dev, L) for L in range(0, int(d0), 1000))
        r1, _ = c3.dec_rates("dense", dev, 1, d0)
        cells = [f"local TTFT {c3.fmt_t(tl)}"]
        for mb in (V['main_L500_19'], V['main_L500_24'], 1000):
            th = c3.T_FIX + flops / B300_EFF + (d0 * MODELS["dense"]["kv"] + MODELS["dense"]["state"]) / c3.bw(mb)
            cells.append(f"{mb}M {c3.fmt_t(th)}")
        p(f"  {dev.label:<24} " + ", ".join(cells) + f"; then the summary takes {c3.fmt_t(o0/r1)} at {r1:.0f} tok/s")
    sess = [[(0.0, d0, o0, 0.0)] + [(d0 + o0 + i * V['sess_L504_51'], V['sess_L504_56'], V['sess_L504_63'], 0.0) for i in range(V['sess_L504_90'])]]
    for a in ("27B API median", "Haiku 5.5", "Sonnet 5.5"):
        p(f"  API {a:<16} ${c3.api_cost(a, sess):.3f} per transcript with 10 questions")
    pre, dec, res = own_gpu_s("dense", sess, True, UNIT["b300"])
    p(f"  own all-server {pre+dec+res:.1f} GPU-s = ${(pre+dec+res)*gpx:.3f}; hybrid server {flops/B300_EFF:.1f} GPU-s = ${flops/B300_EFF*gpx:.3f};"
      f" Mac memory for one transcript {(V['main_L509_41'] + d0*V['main_L509_53'] + MODELS['dense']['state'])/1e9:.0f} GB + OS")
    p("")
    # ------------------------------------------------ 10. devices at v4 prices
    srv_ps = gpx                                   # $ per GPU-s of demand, B300 fleet
    own_ps = sum(own_gpu_s("dense", S, False, UNIT["b300"])) * gpx
    api_ref = api_ps["27B API median"]
    p("== 10. Devices at v4 prices, Qwen3.8-27B, 4 years at 8 h/day: $ per session = device price / (1008 days x sessions/day)"
      " + server + egress (remote)")
    p(f"   references per session: API median ${api_ref:.3f}, own all-server ${own_ps:.3f} (B300 fleet, demand-priced)")
    p("   device                     price      K   local  200M   1G  | $/session at 1G | break-even device price vs API / vs own")
    for dev in DEVICES:
        if not dev.price:
            continue
        for K in sorted({min(V['main_L522_29'], c3.k_mem("dense", dev, V['main_L522_55'])), max(1, c3.k_max("dense", dev))}):
            if K == 0 or K > c3.k_mem("dense", dev, V['main_L523_52']):
                continue
            v = [c3.run("dense", dev, mb, K, S80) for mb in (0, V['v_L525_64'], 1000)]
            r1 = v[2]
            srv = r1["srv_gpu"] * srv_ps + r1["bytes"] / 1e12 * EGRESS_TB
            days = V['days_L528_19'] * DAYS_MONTH * r1["per8h"]
            lo, hi = dev.price[0] / days + srv, dev.price[1] / days + srv
            p(f"   {dev.label:<26} ${dev.price[0]:>6,}-{dev.price[1]:<6,} {K:>2} {v[0]['per8h']:6.1f} {v[1]['per8h']:5.1f} {v[2]['per8h']:5.1f}"
              f" | ${lo:.3f}-{hi:.3f}     | ${fmt(max(0, (api_ref - srv) * days)):>7} / ${fmt(max(0, (own_ps - srv) * days)):>7}")
    p("")

    # ------------------------------------------------ 11. break-even share
    p("== 11. Break-even local share: the smallest s at which the device premium returns within 4 years (office, N=5000)")
    for key in ("m5pro", "m5max64", "m5max", "ultra96"):
        dev = DEV[key]
        K, c8 = cap[("dense", key)]
        prem = dev.price[1] - BASELINE_LAPTOP if key != "ultra96" else dev.price[1]
        r = c3.run("dense", dev, 1000, K, S80)
        cells = []
        for ref in ("27B API median", "27B API DeepInfra", "own"):
            s_be = None
            for i in range(1, V['main_L544_30']):
                s_ = i / V['s__L545_25']
                if SESS_PER_H * 8 * s_ * V['main_L546_41'] > c8:
                    break
                k_, n_, g_, c_, r_ = best_fleet(r["srv_gpu"], N * SESS_PER_H * s_, V['_k___n___g___c___r___L548_83'], DC_UNITS)
                run_m = (c_ - r_) / (N * V['run_m_L549_41']) + kv_store_cost(N, "dense") / (N * V['run_m_L549_80'])
                if ref == "own":
                    kk, nn, g2, c2, r2 = best_fleet(0, N * SESS_PER_H * s_, V['_kk__nn__g2__c2__r2__L551_76'], DC_UNITS, own_model="dense", sessions=S80)
                    ref_m = (c2 - r2) / (N * V['ref_m_L552_45'])
                else:
                    ref_m = V['ref_m_L554_28'] * s_ * api_ps[ref]
                if V['main_L555_19'] * (ref_m - run_m) >= prem * (1 - MAC_RESID[4]):
                    s_be = s_
                    break
            cells.append(f"vs {ref.replace('27B API ', 'API ')}: {'s >= ' + str(int(s_be*V['main_L558_89'])) + '%' if s_be else 'not within capacity'}")
        p(f"  {dev.label:<26} {'premium' if key != 'ultra96' else 'whole price'} ${prem:,}, capacity {c8:.0f}/8h (s up to"
          f" {min(V['main_L560_18'], c8/V['main_L560_26']/(SESS_PER_H*8)*V['main_L560_46']):.0f}%): " + "; ".join(cells))
    p("")
    # ------------------------------------------------ 13. server utilization and renting
    p("== 13. Server utilization and renting (N=5000, s=100%, M5 Max 128 clients, $ per developer-month, office/remote)")
    p("   regions: the same fleet serves 1, 2 or 3 regions' working days in turn; rent: on-demand GPU-hours x1.5 autoscaling overhead")
    for model in ("dense", "flash"):
        u = UNIT["b300"]
        own_gs = sum(own_gpu_s(model, S, False, u))
        K = cap[(model, "m5max")][0]
        r = c3.run(model, DEV["m5max"], 1000, K, S)
        mac = (DEV["m5max"].price[1] - BASELINE_LAPTOP) * (1 - MAC_RESID[4]) / V['mac_L570_79']
        store = kv_store_cost(N, model) / (N * V['store_L571_47'])
        egress = r["bytes"] / 1e12 * V['egress_L572_37'] * EGRESS_TB
        cells = []
        for regions in (1, 2, V['main_L574_30']):
            n1, c1, r1 = fleet_cost(N / regions * SESS_PER_H * own_gs / 3600 * PEAK, u, V['_n1__c1__r1__L575_88'])
            n2, c2, r2 = fleet_cost(N / regions * SESS_PER_H * r["srv_gpu"] / 3600 * PEAK, u, V['_n2__c2__r2__L576_94'])
            hm = (c2 - r2) / (N * V['hm_L577_34']) + store + mac
            cells.append(f"{regions} region{'s' if regions > 1 else ''}: own ${(c1-r1)/(N*V['main_L578_90']):.0f} ({n1} nodes) vs hybrid ${hm:.0f}/{hm+egress:.0f} ({n2})")
        for lab, price in (("neocloud B300 $9.50", V['main_L579_51']), ("AWS B300 $17.80", V['main_L579_78'])):
            om = V['om_L580_17'] * own_gs / 3600 * V['om_L580_39'] * price
            hm = V['hm_L581_17'] * r["srv_gpu"] / 3600 * V['hm_L581_45'] * price + mac + store
            cells.append(f"rent {lab}: own ${om:.0f} vs hybrid ${hm:.0f}/{hm+egress:.0f}")
        p(f"  {MODELS[model]['name']} (API: {'27B median $' + format(V['main_L583_69']*api_ps['27B API median'], '.0f') if model == 'dense' else 'Alibaba $' + format(V['main_L583_152']*api_ps['Flash API (Alibaba)'], '.0f')}):")
        for c_ in cells:
            p(f"    {c_}")
    p("")

    # ------------------------------------------------ 12. tier 2: GLM-5.3-Flash on M5 Ultra 256 GB
    glm_section(p, gpx)
    print("\n".join(out))


# ---------------------------------------------------------------- tier 2: GLM-5.3-Flash
# [fact] HF config.json zai-org/GLM-5.3-Flash: 45 layers = 34 KDA (64 heads x 128 x 128 state) + 11 MLA/DSA (latent 512,
# NoPE; indexer 32 heads x 128, top-2048 pooled groups, 4:1 key pooling); 288 routed experts, 8 active, 18B active.
# [estimate] KV 8-bit 11 x (512 + 128/4) = 5,984 B/token; KDA state 142.6 MB fp32 / 71.3 MB bf16 + conv ~5 MB.
GLM = dict(name="GLM-5.3-Flash", kv=V['GLM_L597_36'], state_fp32=V['GLM_L597_53'] + V['GLM_L597_63'], state_x=V['GLM_L597_77'] + V['GLM_L597_86'],
           w4=V['GLM_L598_14'],                      # [fact] ggml-org Q4_K 181.4 GB; mlx 4-bit 204 GB
           w_fp8=V['GLM_L599_17'], always=V['GLM_L599_31'] * V['GLM_L599_39'], routed=V['GLM_L599_54'] * V['GLM_L599_63'], n_exp=V['GLM_L599_77'], k_exp=V['GLM_L599_88'])
GLM_API = dict(tiers=[(math.inf, (V['GLM_API_L600_34'], V['GLM_API_L600_40'], V['GLM_API_L600_46'], V['GLM_API_L600_52']))])   # [fact] Z.ai list price per 1M tokens


def glm_flop(L):
    sel = min(L, V['sel_L604_17'] * V['sel_L604_24'])                  # top-2048 pooled groups of 4 tokens
    return 2 * V['glm_flop_L605_15'] + V['glm_flop_L605_24'] * V['glm_flop_L605_29'] * sel * V['glm_flop_L605_40'] + V['glm_flop_L605_47'] * V['glm_flop_L605_52'] * V['glm_flop_L605_57'] * 2 * L / V['glm_flop_L605_71'] + V['glm_flop_L605_75'] * V['glm_flop_L605_80'] * V['glm_flop_L605_85'] * V['glm_flop_L605_91'] * V['glm_flop_L605_97']


def glm_dec(K, L, eff=V['glm_dec_L608_22'], bw=V['glm_dec_L608_31']):
    """Per-stream and aggregate tok/s on an M5 Ultra; eff = share of peak bandwidth MoE decode reaches on a Mac
    (Qwen3-235B-A22B on an M3 Ultra reaches ~0.45; Strata's Flash-Next on an M3 Max ~0.23)."""
    e_k = GLM["n_exp"] * (1 - (1 - GLM["k_exp"] / GLM["n_exp"]) ** K)
    per_stream = V['per_stream_L612_17'] * L + V['per_stream_L612_27'] * V['per_stream_L612_32'] * V['per_stream_L612_39'] + 2 * GLM["state_fp32"]
    step = GLM["always"] + GLM["routed"] * e_k / GLM["k_exp"] + K * per_stream
    r = bw * eff / step
    return r, K * r


def glm_p_local(L, moe=V['glm_p_local_L618_23'], pf=V['glm_p_local_L618_31']):
    """Ultra 256 prefill: the M3 Max effective 6.6 TFLOP/s x pf, x a MoE penalty on Mac."""
    return V['glm_p_local_L620_11'] * pf * moe / glm_flop(L)


def glm_run(mbit, K, sessions, state_x=None, eff=V['glm_run_L623_49'], moe=V['glm_run_L623_59']):
    sx = GLM["state_x"] if state_x is None else state_x
    acc = dict(dev_time=V['acc_L625_24'], wall=V['acc_L625_34'], srv=V['acc_L625_43'], bytes=V['acc_L625_54'], offl=V['acc_L625_64'], new=V['acc_L625_73'])
    for turns in sessions:
        for (L, d, o, tau) in turns:
            tl = d / glm_p_local(L, moe)
            th = float("inf")
            if mbit:
                th = c3.T_FIX + d * glm_flop(L) / B300_EFF + (d * GLM["kv"] + sx) / c3.bw(mbit)
                acc["srv"] += (d + o) * glm_flop(L) / B300_EFF
            if th < tl:
                acc["wall"] += th
                acc["bytes"] += d * GLM["kv"] + sx
                acc["offl"] += d
            else:
                acc["dev_time"] += tl
                acc["wall"] += tl
            r, agg = glm_dec(K, L + d, eff)
            acc["dev_time"] += o / agg
            acc["wall"] += o / r + tau
            acc["new"] += d
    n = len(sessions)
    res = {k: v / n for k, v in acc.items()}
    res["per8h"] = min(8 * 3600 / res["dev_time"], K * 8 * 3600 / res["wall"])
    return res


def glm_own_gpu_s(sessions, ideal=False, batch=V['glm_own_gpu_s_L650_47'], stream_tps=V['glm_own_gpu_s_L650_62']):
    """All-server GLM on B300 (FP8, TP2: 164 GB of weights per GPU leaves ~114 GB for KV)."""
    hbm_kv, bw = V['_hbm_kv__bw__L652_17'], V['_hbm_kv__bw__L652_24'] * V['_hbm_kv__bw__L652_31']
    e_b = GLM["n_exp"] * (1 - (1 - GLM["k_exp"] / GLM["n_exp"]) ** batch)
    w_step = (V['w_step_L654_14'] + V['w_step_L654_22'] * e_b / GLM["k_exp"]) / batch            # FP8 bytes per token-step
    pre = dec = res = V['pre_L655_22']
    for turns in sessions:
        for (L, d, o, tau) in turns:
            pre += d * glm_flop(L) / B300_EFF
            dec += o * (w_step + V['glm_own_gpu_s_L659_33'] * (L + d) + V['glm_own_gpu_s_L659_49'] * V['glm_own_gpu_s_L659_54'] * V['glm_own_gpu_s_L659_61'] + 2 * GLM["state_fp32"]) / bw
            busy = o / stream_tps + (0 if ideal else tau)
            res += ((L + d) * GLM["kv"] + GLM["state_fp32"]) * busy / hbm_kv
    n = len(sessions)
    return pre / n, dec / n, res / n


def glm_section(p, gpx):
    p("== 12. Tier 2: GLM-5.3-Flash (320B / 18B active, 1M native) on an M5 Ultra 256 GB, B300 server")
    for lab, usable in (("85% of RAM for the GPU", V['glm_section_L668_51'] * V['glm_section_L668_59']), ("Ivan's 236 GB (20 GB left to macOS)", V['glm_section_L668_106'])):
        free = usable - V['free_L669_24'] - GLM["w4"]
        p(f"  memory, {lab}: Q4_K weights {GLM['w4']/1e9:.0f} GB -> {free/1e9:.0f} GB free -> sessions at 200k:"
          f" {int(free // (V['glm_section_L671_27']*GLM['kv'] + GLM['state_fp32']))}, at 1M: {int(free // (1e6*GLM['kv'] + GLM['state_fp32']))}")
    p(f"  KV {GLM['kv']} B/token (8-bit) vs Qwen3.8-27B 32,768: x{V['glm_section_L672_66']/GLM['kv']:.1f} smaller; fixed KDA state per offload"
      f" {GLM['state_x']/1e6:.0f} MB bf16 ({GLM['state_fp32']/1e6:.0f} MB fp32)")
    p("  prefill FLOP/token: " + ", ".join(f"{int(L/1e3)}k {glm_flop(L)/1e9:.0f} G" for L in (V['glm_section_L674_94'], V['glm_section_L674_100'], 1e6)))
    for eff in (V['glm_section_L675_16'], V['glm_section_L675_22']):
        cells = []
        for K in (1, V['glm_section_L677_21'], 8):
            for L in (V['glm_section_L678_22'], 1e6):
                r, a = glm_dec(K, L, eff)
                cells.append(f"K{K}@{int(L/1e3)}k {r:.0f}/{a:.0f}")
        p(f"  decode per stream / aggregate tok/s, bandwidth efficiency {eff}: " + "  ".join(cells))
    for moe in (V['glm_section_L682_16'], 1.0):
        p(f"  local prefill (MoE factor {moe}): " + ", ".join(f"{int(L/1e3)}k {glm_p_local(L, moe):.0f} tok/s" for L in (V['glm_section_L683_121'], V['glm_section_L683_127'], 1e6)))
    full = sum(1e3 * glm_flop(L) for L in range(0, int(1e6), 1000))
    kvb = 1e6 * GLM["kv"] + GLM["state_x"]
    loc = [sum(1e3 / glm_p_local(L, moe) for L in range(0, int(1e6), 1000)) for moe in (V['loc_L686_88'], 1.0)]
    p(f"  ingest 1M tokens: local {c3.fmt_t(loc[0])} (MoE factor 0.5) / {c3.fmt_t(loc[1])} (1.0); server {c3.fmt_t(full/B300_EFF)}"
      f" on one B300; download {kvb/1e9:.1f} GB: " + ", ".join(f"{lab} {c3.fmt_t(kvb/c3.bw(mb))}" for lab, mb in
                                                            (("100M", V['glm_section_L689_70']), ("200M", V['glm_section_L689_85']), ("1G", 1000))))
    p("  smallest turn delta worth offloading (offload faster than local prefill at 200k, MoE factor 0.5):")
    for sl, sx in (("state bf16", GLM["state_x"]), ("state fp8", GLM["state_x"] / 2)):
        cells = []
        for lab, mb in (("100M", V['glm_section_L693_33']), ("200M", V['glm_section_L693_48']), ("1G", 1000)):
            L = V['L_L694_16']
            a = 1 / glm_p_local(L) - glm_flop(L) / B300_EFF - GLM["kv"] / c3.bw(mb)
            cells.append(f"{lab} {(c3.T_FIX + sx / c3.bw(mb)) / a:,.0f} tokens" if a > 0 else f"{lab} never")
        p(f"    {sl}: " + ", ".join(cells))
    p("  sessions per 8 h, K=4 agents (local / 100M / 200M / 1G):")
    profiles = (("20k->200k", c3.make_sessions(n=V['profiles_L699_49'])), ("200k->1M", c3.make_sessions(n=V['profiles_L699_87'], L0=V['profiles_L699_94'], L1=V['profiles_L699_104'], seed=V['profiles_L699_114'])))
    srv_cost = {}
    for lab, SS in profiles:
        res = [glm_run(mb, V['res_L702_27'], SS) for mb in (0, V['res_L702_48'], V['res_L702_53'], 1000)]
        srv_cost[lab] = (res[3]["srv"], res[3]["bytes"], res[3]["per8h"])
        p(f"    {lab}: " + " / ".join(f"{r['per8h']:.1f}" for r in res)
          + f"; at 1G offloaded {V['glm_section_L705_33']*res[3]['offl']/max(res[3]['new'], 1):.0f}% of new tokens, download {res[3]['bytes']/1e9:.1f} GB per session")
    p("  $ per session (B300 fleet priced per GPU-s of demand; Ultra 256 $9,499-10,799 over 4 years at 8 h/day; egress $5/TB):")
    for lab, SS in profiles:
        api = c3.api_cost.__wrapped__(GLM_API, SS) if hasattr(c3.api_cost, "__wrapped__") else glm_api_cost(SS)
        pre, dec, res_ = glm_own_gpu_s(SS)
        own = (pre + dec + res_) * gpx
        gs, by, per8 = srv_cost[lab]
        srv = gs * gpx + by / 1e12 * EGRESS_TB
        dev = [price / (V['dev_L713_24'] * DAYS_MONTH * per8) for price in (V['dev_L713_62'], V['dev_L713_68'])]
        p(f"    {lab}: API ${api:.2f}; own all-server ${own:.2f} (prefill {pre:.0f} + decode {dec:.0f} + residency {res_:.0f} GPU-s);"
          f" hybrid server ${srv:.2f} + Ultra ${dev[0]:.2f}-{dev[1]:.2f} = ${srv+dev[0]:.2f}-{srv+dev[1]:.2f}"
          f" (24 h use: ${srv+dev[0]/V['glm_section_L716_37']:.2f}-{srv+dev[1]/V['glm_section_L716_56']:.2f})")
    p("")


def glm_api_cost(sessions):
    tot = V['tot_L721_10']
    pi, po, pr, pw = GLM_API["tiers"][0][1]
    for turns in sessions:
        o_prev = V['o_prev_L724_17']
        for (L, d, o, tau) in turns:
            tot += (L * pr + (d + o_prev) * pw + o * po) / 1e6
            o_prev = o
    return tot / len(sessions)


if __name__ == "__main__":
    main()
