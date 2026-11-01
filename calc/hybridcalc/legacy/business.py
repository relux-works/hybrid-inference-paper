from ..inputs import read_json
from ..inputs import legacy_values, measurement_path
V = legacy_values('business')

"""Business view of the hybrid on the measured call mix (Qwen3.8-27B). Not for the paper: input for a separate note.

A. What one agent call costs the prefill provider, by GPU option (rent or own, utilisation), and the price per
   million prefilled tokens.
B. Prices per 1000 calls at break-even and with margin, against API alternatives.
C. Monthly cost to serve heavy / medium / light users at local shares 20/50/100%, and subscription break-evens.
D. A team of 10 heavy developers with an office box.
E. An individual on pay-as-you-go API: savings and Mac payback.
F. Speed: agent waiting time per day, local prefill vs hybrid, and the "always offload" mode for weak Macs.

Call mix: hybrid_calc7_realcalls sampler fitted to Ivan's measured sessions (1.52M calls).
Run: python3 hybrid_calc8_business.py > hybrid_calc8_business.out
"""
import json

from . import sessions as c3
from . import fleet as c4
from . import workload as c7

M = c3.MODELS["dense"]
MFU = V['MFU_L21_6']
# [fact] dense FP8 per GPU: B300 4.5 PF (HGX, as in hybrid_calc4), B200 4.5 PF, H100 SXM 1.979 PF, RTX PRO 6000 1.0076 PF
GPUS = {
    # label: (FP8 dense, $/GPU-h, note)
    "B300 own, 1 region (11.5% use)": (V['GPUS_L25_39'], c4.UNIT["b300"].gpu_s_price() * 3600 / V['GPUS_L25_86'], "hybrid_calc4 node incl. opex"),
    "B300 own, 3 regions (35% use)": (V['GPUS_L26_38'], c4.UNIT["b300"].gpu_s_price() * 3600 / V['GPUS_L26_85'], "same fleet, three working days"),
    "B300 rent $9.50, 70% use": (V['GPUS_L27_33'], V['GPUS_L27_41'] / V['GPUS_L27_48'], "[fact] neocloud on-demand $7.10-9.50"),
    "B200 rent $7.00, 70% use": (V['GPUS_L28_33'], V['GPUS_L28_41'] / V['GPUS_L28_48'], "[fact] neocloud $6.25-8.60"),
    "H100 rent $4.00, 70% use": (V['GPUS_L29_33'], V['GPUS_L29_43'] / V['GPUS_L29_50'], "[fact] neocloud $3.95-6.16"),
    "RTX PRO 6000 rent $2.50, 70% use": (V['GPUS_L30_41'], V['GPUS_L30_52'] / V['GPUS_L30_59'], "[fact] CoreWeave/RunPod $2.49-2.50"),
    "RTX PRO 6000 own DC, 35% use": (V['GPUS_L31_37'], c4.UNIT["rtx8"].gpu_s_price() * 3600 / V['GPUS_L31_87'], "hybrid_calc4 8-GPU server incl. colo"),
    "RTX PRO 6000 own office, 11.5% use": (V['GPUS_L32_43'], c4.UNIT["rtx1"].gpu_s_price() * 3600 / V['GPUS_L32_93'], "workstation, office power"),
}
EGRESS = (1.0, V['EGRESS_L34_15'])                       # $/TB: hyperscale volume vs colo transit
USERS = {"heavy": V['USERS_L35_18'], "medium": V['USERS_L35_34'], "light": V['USERS_L35_48']}   # agent calls per working day at s = 100% [assumption]
DAYS = V['DAYS_L36_7']
# parked + active sessions kept by the provider per user class, at the measured mean depth [assumption]
STORE = {"heavy": (V['STORE_L38_19'], V['STORE_L38_23']), "medium": (V['STORE_L38_38'], 2), "light": (V['STORE_L38_56'], 1)}


def call_stats(R, dev, K, mbit=V['call_stats_L41_31']):
    calls = [t for s in R for t in s]
    n = len(calls)
    flops = sum((d + o) * M["flop"](L) for (L, d, o, tau) in calls) / n        # server shadow-prefills new + decoded
    toks = sum(d + o for (L, d, o, tau) in calls) / n
    rr = c3.run("dense", dev, mbit, K, R)
    nt = sum(map(len, R)) / len(R)
    return dict(flops=flops, toks=toks, bytes=rr["bytes"] / nt, depth=sum(c[0] for c in calls) / n)


def api_per_1000(R, prices):
    """$ per 1000 calls for a flat price triple (input, output, cache read) per million tokens."""
    pi, po, pr = prices
    calls = [t for s in R for t in s]
    return sum(L * pr + d * pi + o * po for (L, d, o, tau) in calls) / len(calls) / 1e6 * 1000


def main():
    out = []
    p = out.append
    stats = read_json(c7.STATS)
    R = c7.make_real_calls(stats["agents"]["all"])
    dev = c4.DEV["m5max64"]
    cs = call_stats(R, dev, V['cs_L64_28'])
    p("== Inputs (measured call mix, Qwen3.8-27B)")
    p(f"  per call: mean depth {cs['depth']/1e3:.0f}k; server prefills {cs['toks']:.0f} tokens (new + client-decoded);"
      f" {cs['flops']/1e12:.2f} TFLOP; KV + state downloaded {cs['bytes']/1e6:.0f} MB at 1G (M5 Max 64 K4)")
    p("")

    p("== A. Provider cost per 1000 calls and per million prefilled tokens, by GPU option (MFU 30%)")
    costs = {}
    for lab, (pf, gph, note) in GPUS.items():
        gpu_s = cs["flops"] / (pf * MFU)
        srv = gpu_s * gph / 3600 * 1000
        per_m = srv / 1000 / cs["toks"] * 1e6
        eg = [cs["bytes"] / 1e12 * e * 1000 for e in EGRESS]
        costs[lab] = (srv, eg)
        p(f"  {lab:<38} ${gph:6.2f}/GPU-h effective: server ${srv:5.2f} + egress ${eg[0]:.2f}-{eg[1]:.2f} per 1000 calls;"
          f" ${per_m:.3f} per M prefilled tokens  ({note})")
    p("")

    p("== B. API alternatives per 1000 calls on the same mix (cache reads priced as listed)")
    apis = {n: c3.api_cost(n, R) / (sum(map(len, R)) / len(R)) * 1000 for n in ("27B API median", "Haiku 5.5", "Sonnet 5.5", "Opus 5.5")}
    apis["GLM-5.3-Flash API (Z.ai)"] = api_per_1000(R, (V['apis__GLM_5_3_Flash_API__Z_ai____L84_56'], V['apis__GLM_5_3_Flash_API__Z_ai____L84_62'], V['apis__GLM_5_3_Flash_API__Z_ai____L84_68']))
    apis["Qwen3.8-Flash API (Alibaba)"] = c3.api_cost("Flash API (Alibaba)", R) / (sum(map(len, R)) / len(R)) * 1000
    for k, v in apis.items():
        p(f"  {k:<30} ${v:6.2f}")
    p("  price the provider can ask, per 1000 calls (server + egress at $5/TB), at 0% / 40% / 70% gross margin:")
    for lab in ("B300 rent $9.50, 70% use", "RTX PRO 6000 rent $2.50, 70% use", "B300 own, 3 regions (35% use)", "H100 rent $4.00, 70% use"):
        c = costs[lab][0] + costs[lab][1][1]
        p(f"    {lab:<36} ${c:.2f} / ${c/V['main_L91_41']:.2f} / ${c/V['main_L91_56']:.2f}")
    p("")

    p("== C. Monthly cost to serve one user (provider: B300 rent $9.50 at 70% use, egress $5/TB, session store)")
    base = costs["B300 rent $9.50, 70% use"][0] + costs["B300 rent $9.50, 70% use"][1][1]
    per_sess = cs["depth"] * M["kv"] + M["state"]
    for u, calls_d in USERS.items():
        parked, active = STORE[u]
        store = (active * per_sess / 1e9 * c4.DRAM_GB + parked * per_sess * V['store_L99_76'] / 1e12 * c4.NVME_TB) / V['store_L99_103']
        cells = []
        for s in (V['main_L101_18'], V['main_L101_23'], 1.0):
            calls_m = calls_d * s * DAYS
            cost = calls_m / 1000 * base + store
            cells.append(f"s={int(s*V['main_L104_36'])}%: {calls_m/1e3:5.1f}k calls -> ${cost:6.1f}")
        p(f"  {u:<6} ({calls_d}/day at s=100%; store ${store:.1f}/mo): " + " | ".join(cells))
    p("")

    p("== D. Team of 10 heavy developers, half of their calls on the hybrid (s=50%), office box, 4 years")
    calls_m = V['calls_m_L109_14'] * USERS["heavy"] * V['calls_m_L109_36'] * DAYS
    for key in ("rtx1", "r5090"):
        u = c4.UNIT[key]
        gpu_s_day = V['gpu_s_day_L112_20'] * USERS["heavy"] * V['gpu_s_day_L112_42'] * cs["flops"] / u.eff_pf
        need = gpu_s_day / (8 * 3600) * c4.PEAK
        n = max(1, -(-need // u.gpus))
        box_m = n * (u.capex * (1 - c4.SRV_RESID[4]) / V['box_m_L115_55'] + sum(u.opex_y()) / V['box_m_L115_78'])
        p(f"  {u.label}: needs {need:.2f} GPUs at peak -> {int(n)} box(es); box ${box_m:,.0f}/month")
    macs = V['macs_L117_11'] * (c4.DEV["m5max"].price[1] - c4.BASELINE_LAPTOP) * (1 - c4.MAC_RESID[4]) / V['macs_L117_90']
    rtx = c4.UNIT["rtx1"]
    box = rtx.capex * (1 - c4.SRV_RESID[4]) / V['box_L119_46'] + sum(rtx.opex_y()) / V['box_L119_71']
    p(f"  hybrid part with 1 RTX PRO 6000 box + 10 x M5 Max 128 premium: ${box + macs:,.0f}/month for {calls_m/1e3:.0f}k calls"
      f" = ${(box + macs)/calls_m*1000:.2f} per 1000 calls")
    for k in ("Opus 5.5", "Sonnet 5.5", "Haiku 5.5", "27B API median", "GLM-5.3-Flash API (Z.ai)"):
        p(f"  the same calls via {k:<26}: ${apis[k]*calls_m/1000:9,.0f}/month")
    p(f"  for scale: all calls of the team (s=100%) via Opus 5.5 list prices: ${apis['Opus 5.5']*calls_m*2/1000:,.0f}/month;"
      f" 10 flat $200 subscriptions: $2,000/month")
    p("")

    p("== E. One developer on pay-as-you-go API who moves a share of calls to a hybrid subscription priced P")
    for u in ("heavy", "medium"):
        for s in (V['main_L130_18'], V['main_L130_23']):
            calls_m_u = USERS[u] * s * DAYS
            for P in (V['main_L132_22'], V['main_L132_28']):
                cells = []
                for k in ("Sonnet 5.5", "Haiku 5.5", "27B API median"):
                    save = apis[k] * calls_m_u / 1000 - P
                    pay = (c4.DEV["m5max64"].price[1] - c4.BASELINE_LAPTOP) / save if save > 0 else float("inf")
                    cells.append(f"vs {k.split(' API')[0]}: saves ${save:5.0f}/mo, M5 Max 64 premium back in {pay:4.0f} mo")
                p(f"  {u:<6} s={int(s*V['main_L138_38'])}% ({calls_m_u/1e3:4.1f}k calls/mo), P=${P:.0f}: " + "; ".join(cells))
    p("")

    p("== F. Speed: prefill wait per call (time to first token), local vs the hybrid policy, measured call mix")
    calls = [t for s in R for t in s]
    air = c3.Dev("air", "MacBook Air M5 32 GB", V['air_L143_48'], V['air_L143_52'], 1.0, V['air_L143_62'], None, "v4 working rate")
    air_cal = c3.Dev("air6", "MacBook Air M5 32 GB, M6-calibrated", V['air_cal_L144_68'], V['air_cal_L144_72'], 1.0, V['air_cal_L144_82'] * V['air_cal_L144_89'] / V['air_cal_L144_96'], None, "")
    devs = [air, air_cal, c4.DEV["m3max"], c4.DEV["m5pro"], c4.DEV["m5max64"]]
    for d in devs:
        cells = []
        for mb in (V['main_L148_19'], 1000):
            loc = hyb = always = V['loc_L149_33']
            stall_l = stall_h = V['stall_l_L150_32']
            for (L, dd, o, tau) in calls:
                tl = dd / c3.p_local("dense", d, L)
                th = c3.T_FIX + dd * M["flop"](L) / c3.EFF_PF + (dd * M["kv"] + M["state"]) / c3.bw(mb)
                loc += tl
                hyb += min(tl, th)
                always += th
                stall_l += tl > V['main_L157_32']
                stall_h += min(tl, th) > V['main_L158_41']
            n = len(calls)
            saved_h = (loc - hyb) / n * USERS["heavy"] / 3600
            cells.append(f"{mb}M: mean {loc/n:5.1f} s -> {hyb/n:4.1f} s (always-offload {always/n:4.1f} s); calls waiting >10 s"
                         f" {V['main_L162_29']*stall_l/n:4.1f}% -> {V['main_L162_54']*stall_h/n:4.1f}%; heavy user saves {saved_h:4.1f} agent-hours/day")
        p(f"  {d.label}:")
        for c_ in cells:
            p(f"    {c_}")
    p("")
    p("== G. B2C at break-even for a user whose Mac is already paid for (no margin; sessions parked on NVMe only)")
    p("   price per 1000 calls = server + egress; per month adds the NVMe session store; compared with the cheapest APIs")
    per_sess = cs["depth"] * M["kv"] + M["state"]
    store_nvme = {u: STORE[u][0] * per_sess * V['store_nvme_L170_46'] / 1e12 * c4.NVME_TB / V['store_nvme_L170_72'] for u in USERS}
    for lab in ("B200 rent $7.00, 70% use", "B300 own, 3 regions (35% use)", "B300 rent $9.50, 70% use"):
        srv, eg = costs[lab]
        lo, hi = srv + eg[0], srv + eg[1]
        p(f"  {lab}: ${lo:.2f}-{hi:.2f} per 1000 calls")
        for u, calls_d in USERS.items():
            cells = []
            for sh in (V['main_L177_23'], V['main_L177_28'], 1.0):
                k = calls_d * sh * DAYS / 1000
                cells.append(f"s={int(sh*V['main_L179_41'])}%: ${k*lo + store_nvme[u]:5.1f}-{k*hi + store_nvme[u]:5.1f}")
            p(f"    {u:<6} (store ${store_nvme[u]:.1f}/mo): " + " | ".join(cells))
    p("  the same calls via the cheapest APIs, $ per 1000 calls: MiMo-V2.6-Flash 0.83; GPT-6 Luna Flex 1.08;"
      " DeepSeek V4.1 Flash off-peak 1.10; Qwen3.8-27B at Chutes 1.61 (research api-capability-2026-10.md)")
    print("\n".join(out))


if __name__ == "__main__":
    main()
