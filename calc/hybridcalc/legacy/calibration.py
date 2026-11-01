from ..inputs import read_json
from ..inputs import legacy_values, measurement_path
V = legacy_values('calibration')

"""calc9: recalibrate the local Mac side with Ivan's measured M3 Max run (2026-10-30).

Source: validated package ivmbp-qwen27b-bench-20261030 (sha256 5c393bdf...), from the incident lane.
Qwen3.8-27B Q4_K_M, llama.cpp b11087 Metal, flash attention on, KV q8_0, M3 Max 40-core GPU, 128 GiB.

Prints:
  A. slot bytes: KV per token and the fixed (recurrent) part, by linear fit;
  B. prefill rate and model FLOP utilisation (MFU) by depth, against calc3's old assumption;
  C. local prefill time per call for Ivan's real call mix, measured curve vs the old one;
  D. offload break-even: link speed above which server prefill + transfer beats local prefill,
     with the recurrent state on the wire as f32 (today) or bf16 (an M1 option).
"""
import contextlib
import io
import json
import math
import os
import statistics
import sys

with contextlib.redirect_stdout(io.StringIO()):
    from . import sessions as c3
    from . import fleet as c4
    from . import workload as c7

PKG = measurement_path("benchmark")

M = c3.MODELS["dense"]
PEAK = c4.PEAK16["m3max"]          # 14 TFLOP/s, calc4's figure for the 40-core M3 Max GPU
flop = M["flop"]                   # FLOP per prefill token at depth L (2 x 27e9 + attention)


def rows(name):
    with open(os.path.join(PKG, name), encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def main():
    depth = rows("depth.jsonl")
    seg = [r for r in depth if r["kind"] == "segment"]
    saves = [r for r in depth if r["kind"] == "slot_save"]
    turns = [r for r in depth if r["kind"] == "turn"]

    print("A. Slot bytes (llama-server slot save, q8_0 KV + recurrent state + token ids)")
    xs, ys = [r["depth"] for r in saves], [r["bytes"] for r in saves]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    per_tok = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    fixed = my - per_tok * mx
    worst = max(abs(y - (fixed + per_tok * x)) for x, y in zip(xs, ys))
    print(f"   per token {per_tok:,.1f} B (q8_0 K+V: 16 layers x 2 x 4 heads x 256 x 34/32 = {V['main_L55_94']*2*V['main_L55_99']*V['main_L55_101']*V['main_L55_105']/V['main_L55_108']:,.0f} B,"
          f" plus ids and cell metadata)")
    print(f"   fixed {fixed/1e6:,.1f} MB; calc3 recurrent state {M['state']/1e6:.1f} MB (bf16) -> ratio {fixed/M['state']:.3f}"
          f"  => the engine keeps the recurrent state in f32")
    print(f"   linear fit residual at most {worst:,.0f} B over {len(xs)} depths")

    print("\nB. Prefill by depth: marginal segment rate, MFU at the segment midpoint, calc3 assumption")
    print("   segment            mid     tok/s   TFLOP/s  MFU    calc3 tok/s  measured/calc3")
    curve = []
    for r in seg:
        mid = (r["depth_from"] + r["depth"]) / 2
        rate = r["prefill_tok_s"]
        eff = rate * flop(mid)
        old = c3.p_local_m3("dense", mid)
        curve.append((mid, rate))
        print(f"   {int(r['depth_from']):>7,}-{int(r['depth']):<7,} {mid/1e3:6.1f}k {rate:7.1f}  {eff/1e12:7.2f}  {eff/PEAK:5.0%}"
              f"  {old:9.1f}    {rate/old:5.2f}")
    print("   turn deltas (prefill tok/s at each level, 512 / 2k / 10k):")
    lv = {}
    for r in turns:
        lv.setdefault(r["level"], {})[r["delta"]] = r.get("prefill_tok_s")
    for L in sorted(lv):
        print(f"     {L/1e3:5.0f}k  " + "  ".join(f"{lv[L].get(d, float('nan')):6.1f}" for d in sorted(lv[L])))

    def rate_measured(L):
        if L <= curve[0][0]:
            return curve[0][1]
        for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
            if L <= x1:
                return y0 + (y1 - y0) * (L - x0) / (x1 - x0)
        x, y = curve[-1]
        return y * flop(x) / flop(L)      # beyond the last point: same efficiency, more FLOPs

    print("\nC. Local prefill time per call, Ivan's real call mix (calc7 sampler, 40k calls)")
    a = read_json(c7.STATS)["agents"]["all"]
    calls = [c for chunk in c7.make_real_calls(a) for c in chunk]
    t_new = [d / rate_measured(L) for (L, d, _o, _t) in calls]
    t_old = [d / c3.p_local_m3("dense", L) for (L, d, _o, _t) in calls]
    for name, t in (("measured", t_new), ("calc3 old", t_old)):
        s = sorted(t)
        print(f"   {name:<10} mean {statistics.mean(t):6.1f} s   p50 {s[len(s)//2]:5.1f} s   p90 {s[int(len(s)*V['main_L95_111'])]:6.1f} s")
    print(f"   measured / old mean: {statistics.mean(t_new)/statistics.mean(t_old):.2f}")

    print("\nD. Offload break-even per call: server prefill + transfer < local prefill")
    print("   (server: calc3 fixed overhead T_FIX and calc4 B300 effective FLOP/s; link in Mbit/s, payload = d x KV + state)")
    kv_wire = V['kv_wire_L100_14'] * 2 * V['kv_wire_L100_23'] * V['kv_wire_L100_27'] * V['kv_wire_L100_33'] / V['kv_wire_L100_38']
    for label, state in (("state f32 (today)", fixed), ("state bf16 (M1 option)", fixed / 2)):
        print(f"   {label}:")
        for mbit in (V['main_L103_21'], V['main_L103_26'], 1000, V['main_L103_37']):
            bw = mbit * 1e6 / 8
            off, saved = 0, 0.0
            for (L, d, _o, _t), tl in zip(calls, t_new):
                th = c3.T_FIX + d * flop(L) / c4.B300_EFF + (d * kv_wire + state) / bw
                if th < tl:
                    off += 1
                    saved += tl - th
            print(f"     {mbit:5d} Mbit/s: offload wins on {off/len(calls):5.1%} of calls,"
                  f" saves {saved/len(calls):5.1f} s per call on average")

    par = [r for r in rows("parallel.jsonl") if r["kind"] == "parallel"]
    if par:
        r = par[0]
        print(f"\nE. Parallel decode at {r.get('depth', 0)/1e3:.0f}k: single {r.get('single_decode_tok_s')} tok/s,"
              f" {r.get('streams')} streams aggregate {r.get('aggregate_tok_s', r.get('aggregate_decode_tok_s'))} tok/s"
              " (raw v1.1 row; normalized 8.441 / 14.054 / 1.665x in the package report)")


if __name__ == "__main__":
    main()
