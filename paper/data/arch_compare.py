#!/usr/bin/env python3
"""Architecture comparison for the hybrid (paper section "Архитектура модели и выгода гибрида").

Estimates from published config.json files and the formulas of appendix A; no measurement except where noted.
- KV cache in 8 bits uses the llama.cpp q8_0 layout: 34 bytes per 32 values (factor 1.0625).
- Sliding-window layers keep the last W positions, so an offload carries every live window position, min(prefix + delta, W).
- Prefill FLOPs per token at depth L: 2N + 4 * L * q * e over full-attention layers, plus 4 * min(L, W) * q * e over
  sliding-window layers (global layers with their own head size where the config gives one).
- Client prefill time scales the PRI31 Qwen3.8-27B rate on the M3 Max at 131k, from the engine snapshot by FLOPs per token;
  this assumes the same compute efficiency for every dense model.
Saving per call = client prefill time minus delta transfer time; server prefill time (well under a second on B300)
is left out.
Run: python3 arch_compare.py  (writes arch-compare.csv next to this script)
"""
import csv, os

Q8 = 34 / 32
LINK = 300e6 / 8          # 300 Mbit/s in bytes per second
DEPTH = 131072

# name, params N (billions, text), context, full layers (count, kv heads, head dim, q heads, k=v shared),
# sliding layers (count, kv heads, head dim, q heads, window), fixed state bytes, kind
MODELS = [
    ("Qwen3.8-27B", 27.8, 262144, (16, 4, 256, 24, False), None, 156_894_784, "плотная, линейное внимание 3:1"),
    ("Muse Glimmer 30B", 28.0, 131072, (13, 2, 128, 32, False), (39, 2, 128, 32, 2048), 0, "плотная, скользящее окно 3:1"),
    ("Gemma 4 31B", 30.7, 262144, (10, 4, 512, 32, False), (50, 16, 256, 32, 1024), 0, "плотная, скользящее окно 5:1"),
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


def delta(model, d, prefix=DEPTH):
    _, _, _, full, swa, state, _ = model
    per_swa, window = kv_swa(swa)
    return d * kv_full(full) + min(prefix + d, window) * per_swa + state


def flops_per_token(model, depth):
    _, n, _, full, swa, _, _ = model
    layers, _, dim, q, _ = full
    f = 2 * n * 1e9 + 4 * layers * depth * q * dim
    if swa:
        sl, _, sdim, sq, window = swa
        f += 4 * sl * min(depth, window) * sq * sdim
    return f


def calculated_rows():
    # Preserve the R16 operation-scaled sensitivity; correct live-window wire
    # geometry from R17 without changing any accepted engine export.
    source = os.path.join(os.path.dirname(__file__), 'engine', 'arch_compare.csv')
    with open(source, newline='') as stream:
        calibrated = {r['model']: r for r in csv.DictReader(stream) if r['state_format'] == 'f32'}
    fields = ['model', 'kind', 'context', 'full_layers', 'kv_full_bytes_token', 'swa_bytes_token', 'swa_window', 'fixed_mb', 'delta_1k_mb', 'delta_10k_mb', 'transfer_1k_300mbit_s', 'gflop_token_131k', 'client_prefill_1k_131k_s', 'saving_1k_131k_100mbit_s', 'saving_1k_131k_300mbit_s', 'saving_1k_131k_1000mbit_s', 'client_prefill_1k_262k_s']
    rows = []
    for m in MODELS:
        name, _, ctx, full, swa, state, kind = m
        row = {key: calibrated[name][key] for key in fields}
        row['kind'] = kind
        if swa:
            geometry_path = os.path.join(os.path.dirname(__file__), 'engine17', 'sliding_geometry.csv')
            with open(geometry_path, newline='') as stream:
                key = 'glimmer30' if name == 'Muse Glimmer 30B' else 'gemma31'
                g = next(r for r in csv.DictReader(stream) if r['model'] == key)
            small = 1000 * int(g['full_kv_bytes_token']) + int(g['window_bytes'])
            large = 10000 * int(g['full_kv_bytes_token']) + int(g['window_bytes'])
            reference = float(calibrated['Qwen3.8-27B']['reference_rate_tok_s'])
            local = 1000 / reference * flops_per_token(m, DEPTH) / flops_per_token(MODELS[0], DEPTH)
            row.update(delta_1k_mb=small/1e6,delta_10k_mb=large/1e6,transfer_1k_300mbit_s=round(small/LINK,1))
            for link in (100,300,1000):
                row['saving_1k_131k_'+str(link)+'mbit_s'] = round(local-small/(link*1e6/8),1)
        rows.append(row)
    return rows


def main():
    rows = calculated_rows()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arch-compare.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
