"""Edge clients for the hybrid: a general offload metric, light laptops, and phones.

A. FLOP per transferred byte. Offloading a turn delta beats even a perfect local engine when the model's
   prefill FLOP per token, divided by the bytes per token that cross the network, exceeds the client's
   peak FLOP/s divided by the link's bytes per second:
       speed-up over a perfect local engine = (F(L) / kv) / (P_peak / BW)
   (the fixed recurrent state per offload and the RTT are left out here; hybrid_calc3.run includes them).
B. Light laptops (fanless MacBook Air class): local prefill vs hybrid for one-shot ingests, decode bounds.
C. Phones: time to first token, downlink per prompt and per month, and server cost for 100M devices.

Inputs marked [fact] come from .temp/research/*.md; [estimate] are ours.
Run: python3 hybrid_calc6_edge.py > hybrid_calc6_edge.out
"""
import hybrid_calc3 as c3
import hybrid_calc4 as c4

M = c3.MODELS
LINK_EFF = 0.9


def link_bps(mbit):
    return mbit * 1e6 / 8 * LINK_EFF


# ---------------------------------------------------------------- models
def hybrid_qwen(name, layers_full, kv_heads, head_dim, layers_lin, v_heads, k_dim, v_dim, active, q_heads):
    """Qwen3.5-style hybrid: full-attention layers keep KV, Gated DeltaNet layers keep a fixed state.
    KV 8-bit; state bf16 (2 bytes) as sent; FLOP/token = 2 x active params + attention over L."""
    kv = layers_full * 2 * kv_heads * head_dim                       # bytes/token at 8 bits
    state = layers_lin * v_heads * k_dim * v_dim * 2                  # bf16
    att = layers_full * q_heads * head_dim * 4                        # QK^T and AV, 2 FLOP each
    return dict(name=name, kv=kv, state=state, flop=lambda L, a=active, t=att: 2 * a + t * L)


MODELS_EDGE = {
    "27B": dict(name=M["dense"]["name"], kv=M["dense"]["kv"], state=M["dense"]["state"], flop=M["dense"]["flop"]),
    "flash": dict(name=M["flash"]["name"], kv=M["flash"]["kv"], state=M["flash"]["state"], flop=M["flash"]["flop"]),
    "glm": dict(name="GLM-5.3-Flash", kv=c4.GLM["kv"], state=c4.GLM["state_x"], flop=c4.glm_flop),
    # [fact] HF config Qwen/Qwen3.5-35B-A3B: 40 layers = 10 full (16 q, 2 kv heads x 256) + 30 Gated DeltaNet
    # (32 v-heads x 128 x 128); 256 experts, 8 routed + shared; ~3B active [card]
    "a3b": hybrid_qwen("Qwen3.5-35B-A3B", 10, 2, 256, 30, 32, 128, 128, 3.0e9, 16),
}


def section_a(p):
    p("== A. FLOP per transferred byte, I(L) = F(L) / kv, MFLOP per byte")
    for k, m in MODELS_EDGE.items():
        p(f"  {m['name']:<18} kv {m['kv']:6.0f} B/token, state {m['state']/1e6:5.1f} MB: "
          + "  ".join(f"{int(L/1e3)}k {m['flop'](L)/m['kv']/1e6:5.2f}" for L in (8e3, 32e3, 110e3, 1e6)))
    devs = {"M5 Air (est.)": 16e12, "M5 Pro": c4.PEAK16["m5pro"], "M5 Max": c4.PEAK16["m5max"],
            "M5 Ultra 80C": c4.PEAK16["ultra256"]}
    p("  client ratio R = peak FLOP/s / link bytes/s, MFLOP per byte:")
    for d, pf in devs.items():
        p(f"    {d:<14} " + "  ".join(f"{mb}M {pf/link_bps(mb)/1e6:6.2f}" for mb in (100, 200, 1000, 10000)))
    p("  speed-up of offload over a perfect local engine at 110k / 1M (I / R):")
    for k, m in MODELS_EDGE.items():
        for d, pf in devs.items():
            p(f"    {m['name']:<18} {d:<14} " + "  ".join(
                f"{mb}M {m['flop'](110e3)/m['kv']/(pf/link_bps(mb)):6.1f}/{m['flop'](1e6)/m['kv']/(pf/link_bps(mb)):6.1f}"
                for mb in (100, 200, 1000, 10000)))
    p("")


# ---------------------------------------------------------------- B. light laptops
# [fact] mlx-lm discussion #1932 (2026-09-29): M6 Mac mini 24 GB, Qwen3.8-27B 4-bit, MLX 0.32.2: "around 270 tok/s
# average prefill, 9.8 tok/s ordinary decoding"; ~30K context with the GPU wired limit raised to 20 GB.
# [fact] Apple: M6 has "nearly 30 percent" more peak GPU AI compute than M5. [fact] M5 153 GB/s, M6 170 GB/s, M1 68 GB/s.
# [fact] Fanless Air under sustained GPU load: 3DMark stress -18% (M5) .. -28% (M1); SoC settles at 8-9 W within minutes;
# fanless Apple SoCs under LLM load (iPhone, MLX) lose 40-60%. [estimate] sustained factor 0.6-0.8 for prefill on an Air.
M6_EFF = 270 * (54e9 + 393216 * 15e3)        # effective FLOP/s implied by the M6 measurement (average depth ~15k assumed)
LAPTOPS = {
    "air_m5_32": dict(label="MacBook Air 13 M5 32 GB, $1,699", bw=153e9, eff=M6_EFF / 1.3, mem_gb=32,
                      note="burst rate scaled from the M6 measurement; sustained x0.6-0.8"),
    "air_m5_24": dict(label="MacBook Air 13 M5 24 GB, $1,499", bw=153e9, eff=M6_EFF / 1.3, mem_gb=24,
                      note="as above; 27B leaves room for ~30K context (measured on a 24 GB M6)"),
    "air_m1_16": dict(label="MacBook Air M1 16 GB (2020)", bw=68.25e9, eff=2.6e12 * 0.5, mem_gb=16,
                      note="2.6 TFLOP/s FP32 [fact], FP16 at about the same rate, 50% efficiency assumed"),
}
LIGHT_MODELS = {
    # active_gb: bytes read per decoded token at 4-bit (all weights for dense; active experts + shared for MoE)
    "q27": dict(name="Qwen3.8-27B (AA 52.0)", weights_gb=16.05, active_gb=15.0, kv=M["dense"]["kv"],
                state=M["dense"]["state"], flop=M["dense"]["flop"]),
    "a3b": dict(name="Qwen3.6-35B-A3B (AA 32.1)", weights_gb=20.40, active_gb=2.0, kv=MODELS_EDGE["a3b"]["kv"],
                state=MODELS_EDGE["a3b"]["state"], flop=MODELS_EDGE["a3b"]["flop"]),
}


def prefill_flops(m, L):
    n = 64
    return sum(m["flop"](L * (i + 0.5) / n) for i in range(n)) * L / n


def ttft_hybrid(m, L, mbit, rtt=0.04, srv_eff=c4.UNIT["b300"].eff_pf):
    """Seconds to first token with server prefill: RTT + server compute on one B300 GPU + download."""
    return rtt + prefill_flops(m, L) / srv_eff + (L * m["kv"] + m["state"]) / link_bps(mbit)


def decode_bound(m, L, bw, eff=0.85):        # 0.85 reproduces the 9.8 tok/s measured on the M6 within ~5%
    """Single-stream decode ceiling, tok/s: effective bandwidth / bytes read per token."""
    return bw * eff / (m["active_gb"] * 1e9 + L * m["kv"] + 2 * m["state"])


def section_b(p):
    p("== B. Light laptops: one-shot ingest, then a 3k-token answer (local prefill burst / sustained x0.6) vs hybrid")
    p(f"   calibration: M6 measurement implies {M6_EFF/1e12:.1f} TFLOP/s effective; earlier v4 assumed 4.8 for the M5 Air")
    for lk, lp in LAPTOPS.items():
        p(f"  {lp['label']} ({lp['bw']/1e9:.0f} GB/s, {lp['eff']/1e12:.1f} TFLOP/s effective burst): {lp['note']}")
        for mk, m in LIGHT_MODELS.items():
            # GPU-wired limit raised to RAM - 4 GB, minus weights and ~2 GB of compute buffers. Check: a 24 GB M6 with
            # Qwen3.8-27B gives ~30K context at fp16 KV (measured, mlx-lm #1932), i.e. ~60K at 8-bit KV.
            usable = lp["mem_gb"] - 4 - m["weights_gb"] - 2
            if usable < 1.0:
                p(f"    {m['name']:<26} does not fit ({m['weights_gb']:.1f} GB weights in {lp['mem_gb']} GB)"); continue
            max_ctx = usable * 1e9 / m["kv"]
            dec = decode_bound(m, 30e3, lp["bw"])
            p(f"    {m['name']:<26} context room ~{max_ctx/1e3:.0f}k; decode <= {dec:.0f} tok/s; 3k answer {3000/dec/60:.1f} min")
            for L in (8e3, 32e3, 70e3):
                if L > max_ctx:
                    p(f"      {int(L/1e3):>3}k: does not fit"); continue
                tl = prefill_flops(m, L) / lp["eff"]
                th = [ttft_hybrid(m, L, mb) for mb in (100, 200, 1000)]
                p(f"      {int(L/1e3):>3}k: local {tl/60:5.1f} / {tl/0.6/60:5.1f} min | hybrid 100M {th[0]/60:4.1f} min,"
                  f" 200M {th[1]:5.0f} s, 1G {th[2]:4.0f} s | download {(L*m['kv']+m['state'])/1e9:.2f} GB")
    p("")


# ---------------------------------------------------------------- C. phones
# Inputs: .temp/research/phones-2026-10.md.
# [fact] configs (HF config.json): growing KV per token at bf16 and fixed parts; we send KV at 8 bits (Apple already
#   uses an 8-bit KV cache) and recurrent state at bf16, so bf16 KV figures are halved here.
# [fact] iPhone 17 Pro, LiteRT-LM GPU, ~1K-token prompts: Gemma 4 E2B 2,878 tok/s, E4B 1,189 tok/s (cold); sustained
#   LLM load on phones keeps 38-67% of burst within minutes. [estimate] effective phone FLOP/s = rate x FLOP/token,
#   ~1.1-1.3e13; models without a phone measurement use 1.1e13; sustained factor 0.5.
# [fact] links: Ookla Sep 2026 global median mobile 110 Mbps / 24 ms, US mobile median 191 Mbps; US 5G 180-314 Mbps.
PHONE_EFF = 1.1e13
PHONE_SUSTAINED = 0.5


def phone_model(name, active, kv_bf16, fixed_bf16, att_flop_per_L=0.0, rate=None):
    m = dict(name=name, kv=kv_bf16 / 2, state=fixed_bf16 / 2, flop=lambda L, a=active, t=att_flop_per_L: 2 * a + t * L)
    m["eff"] = rate * m["flop"](1024) if rate else PHONE_EFF
    return m


PHONE_MODELS = {
    # Gemma 4 E2B: 2.3B effective; growing KV 6 KiB bf16; sliding cap 6 MiB (window 512) [fact/estimate]
    "e2b": phone_model("Gemma 4 E2B", 2.3e9, 6 * 1024, 6 * 2**20, rate=2878),
    # Gemma 4 E4B: 4.5B effective; growing KV 16 KiB; sliding cap 20 MiB
    "e4b": phone_model("Gemma 4 E4B", 4.5e9, 16 * 1024, 20 * 2**20, rate=1189),
    # Qwen3.5-2B: 6 full layers x 2 KV heads x 256 -> 12 KiB bf16; GDN state 18 MiB fp32 = 9 MiB bf16 (x2 below to undo /2)
    "q2b": phone_model("Qwen3.5-2B", 2.0e9, 12 * 1024, 18 * 2**20, att_flop_per_L=6 * 8 * 256 * 4),
    # Qwen3.5-9B: 8 full layers x 4 KV heads x 256 -> 32 KiB bf16; GDN state 48 MiB fp32 = 24 MiB bf16
    "q9b": phone_model("Qwen3.5-9B", 9.65e9, 32 * 1024, 48 * 2**20, att_flop_per_L=8 * 16 * 256 * 4),
    # Llama 3.2 3B: plain full attention, 112 KiB bf16 per token
    "l3b": phone_model("Llama 3.2 3B", 3.2e9, 112 * 1024, 0, att_flop_per_L=28 * 24 * 128 * 4),
}
# usage profile for the fleet estimate [assumption, to be argued in the text]: offloaded prompts per device-day
USAGE = dict(prompts_per_day=10, tokens=8e3)
EGRESS_TB_LOW, EGRESS_TB_HIGH = 1.0, 5.0      # $/TB: hyperscale CDN volume pricing vs our colo transit figure


def phone_ttft_hybrid(m, L, mbit, rtt=0.024):
    return rtt + prefill_flops(m, L) / c4.UNIT["b300"].eff_pf + (L * m["kv"] + m["state"]) / link_bps(mbit)


def section_c(p):
    p("== C. Phones: time to first token, local (burst / sustained x0.5) vs hybrid, and what crosses the network")
    p("   KV sent at 8 bits, recurrent state at bf16; links: 110 Mbps global mobile median, 190 US median, 300 good 5G")
    for k, m in PHONE_MODELS.items():
        p(f"  {m['name']:<13} KV {m['kv']/1024:5.1f} KiB/token + fixed {m['state']/2**20:4.1f} MiB;"
          f" FLOP/byte at 8k {m['flop'](8e3)/m['kv']/1e6:4.2f} M; local {m['eff']/1e12:4.1f} TFLOP/s effective")
        for L in (4096, 16384, 32768):
            tl = prefill_flops(m, L) / m["eff"]
            th = [phone_ttft_hybrid(m, L, mb) for mb in (110, 190, 300)]
            mb_ = (L * m["kv"] + m["state"]) / 2**20
            p(f"    {L//1024:>3}K: local {tl:5.1f} / {tl/PHONE_SUSTAINED:5.1f} s | hybrid 110M {th[0]:5.1f} s, 190M {th[1]:5.1f} s,"
              f" 300M {th[2]:5.1f} s | {mb_:6.0f} MiB per prompt")
    p("")
    p(f"  Fleet of 100M devices, {USAGE['prompts_per_day']} offloaded prompts of {USAGE['tokens']/1e3:.0f}k tokens per device-day:")
    gpu_h_price = c4.UNIT["b300"].gpu_s_price() * 3600 / 0.5     # 50% utilisation for a global consumer service
    for k, m in PHONE_MODELS.items():
        fl = USAGE["prompts_per_day"] * prefill_flops(m, USAGE["tokens"])
        gpu_s_day = fl / c4.UNIT["b300"].eff_pf
        gb_month = USAGE["prompts_per_day"] * (USAGE["tokens"] * m["kv"] + m["state"]) * 30 / 1e9
        srv_y = gpu_s_day * 365 / 3600 * gpu_h_price
        eg_lo, eg_hi = gb_month * 12 / 1e3 * EGRESS_TB_LOW, gb_month * 12 / 1e3 * EGRESS_TB_HIGH
        gpus = 100e6 * gpu_s_day / 86400 * c4.PEAK
        p(f"    {m['name']:<13} server {gpu_s_day:5.2f} GPU-s/day -> ${srv_y:5.2f}/device-year; downlink {gb_month:5.1f} GB/month"
          f" -> egress ${eg_lo:4.2f}-{eg_hi:4.2f}/device-year; B300 GPUs at 2x peak: {gpus:6,.0f} ({gpus/8:5,.0f} nodes)")
    p(f"   B300 GPU-hour priced at ${gpu_h_price:.2f} (100%-use price ${c4.UNIT['b300'].gpu_s_price()*3600:.2f} at 50% utilisation)")
    p("")


def main():
    out = []
    p = out.append
    section_a(p)
    section_b(p)
    section_c(p)
    print("\n".join(out))


if __name__ == "__main__":
    main()
