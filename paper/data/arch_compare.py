#!/usr/bin/env python3
"""Architecture comparison for the hybrid (paper section "Архитектура модели и выгода гибрида").

Estimates from published config.json files and the formulas of appendix A; no measurement except where noted.
- KV cache in 8 bits uses the llama.cpp q8_0 layout: 34 bytes per 32 values (factor 1.0625).
- Sliding-window layers keep the last W positions, so a delta carries their KV for min(d, W) new positions.
- Prefill FLOPs per token at depth L: 2N + 4 * L * q * e over full-attention layers, plus 4 * min(L, W) * q * e over
  sliding-window layers (global layers with their own head size where the config gives one).
- Client prefill time scales the measured Qwen3.8-27B rate on the M3 Max at 131k (41.2 tok/s) by FLOPs per token;
  this assumes the same compute efficiency for every dense model.
Saving per call = client prefill time minus delta transfer time; server prefill time (well under a second on B300)
is left out.
Run: python3 arch_compare.py  (writes arch-compare.csv next to this script)
"""
import csv, os

Q8 = 34 / 32
LINK = 300e6 / 8          # 300 Mbit/s in bytes per second
DEPTH = 131072
QWEN_RATE_131K = 41.2     # measured, M3 Max, Qwen3.8-27B Q4_K_M

# name, params N (billions, text), context, full layers (count, kv heads, head dim, q heads, k=v shared),
# sliding layers (count, kv heads, head dim, q heads, window), fixed state bytes, kind
MODELS = [
    ("Qwen3.8-27B", 27.8, 262144, (16, 4, 256, 24, False), None, 156_894_784, "плотная, линейное внимание 3:1"),
    ("Muse Glimmer 30B", 28.0, 131072, (13, 2, 128, 32, False), (39, 2, 128, 32, 2048), 0, "плотная, скользящее окно 3:1"),
    ("Gemma 4 31B", 30.7, 262144, (10, 4, 512, 32, True), (50, 16, 256, 32, 1024), 0, "плотная, скользящее окно 5:1"),
    ("Qwen3-32B", 32.8, 40960, (64, 8, 128, 64, False), None, 0, "плотная, полное внимание"),
]


def kv_full(full):
    layers, kvh, dim, _, shared = full
    return layers * kvh * dim * (1 if shared else 2) * Q8


def kv_swa(swa):
    if not swa:
        return 0.0, 0
    layers, kvh, dim, _, window = swa
    return layers * kvh * dim * 2 * Q8, window


def delta(model, d):
    _, _, _, full, swa, state, _ = model
    per_swa, window = kv_swa(swa)
    return d * kv_full(full) + min(d, window) * per_swa + state


def flops_per_token(model, depth):
    _, n, _, full, swa, _, _ = model
    layers, _, dim, q, _ = full
    f = 2 * n * 1e9 + 4 * layers * depth * q * dim
    if swa:
        sl, _, sdim, sq, window = swa
        f += 4 * sl * min(depth, window) * sq * sdim
    return f


def main():
    ref = flops_per_token(MODELS[0], DEPTH)
    rows = []
    for m in MODELS:
        name, _, ctx, full, swa, state, kind = m
        per_swa, window = kv_swa(swa)
        d1k, d10k = delta(m, 1000), delta(m, 10000)
        prefill_s = 1000 / (QWEN_RATE_131K * ref / flops_per_token(m, DEPTH))
        rows.append(dict(model=name, kind=kind, context=ctx, full_layers=full[0],
                         kv_full_bytes_token=round(kv_full(full)), swa_bytes_token=round(per_swa), swa_window=window,
                         fixed_mb=round((state + (window * per_swa if swa else 0)) / 1e6, 1),
                         delta_1k_mb=round(d1k / 1e6, 1), delta_10k_mb=round(d10k / 1e6, 1),
                         transfer_1k_300mbit_s=round(d1k / LINK, 1),
                         gflop_token_131k=round(flops_per_token(m, DEPTH) / 1e9),
                         client_prefill_1k_131k_s=round(prefill_s, 1),
                         **{f"saving_1k_131k_{mbit}mbit_s": round(prefill_s - d1k / (mbit * 1e6 / 8), 1) for mbit in (100, 300, 1000)},
                         client_prefill_1k_262k_s=round(1000 / (QWEN_RATE_131K * ref / flops_per_token(m, 262144)), 1)
                         if ctx >= 262144 else None))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arch-compare.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
