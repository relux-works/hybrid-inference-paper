- **Apple M3 Max 128 GB, Glimmer 30B at normal priority (PRI 31), kit 1.6.7 step 40, llama.cpp `dde879bc` (incident
  lane, started 2026-11-03 15:42Z; root review ACCEPT 16:10Z).** Strict archive 10,953 B, sha256 8f817b23...a5d2 (raw
  sha256 5b81708e...0012), with the incident lane; its copy on agents1 is pending. Internal model SHA 4cc57c0f...3f60e.
  This run replaces the background-priority block above.
  - Admission: 120.04 s fresh memory window with 60 samples, then 152 runtime samples with zero pageout and swapout
    growth. Four depths, 12 delta turns, four exact saves and restores, no re-reads.
  - Values per depth: Δ512 / Δ2000 / Δ10000 prefill tok/s, then decode tok/s after each delta, then save and restore
    seconds.

    | Depth | Prefill tok/s | Decode tok/s | Save / restore s |
    |---|---|---|---|
    | 16k | 167.7 / 173.5 / 158.4 | 13.77 / 16.3 / 15.33 | 0.152 / 0.018 |
    | 50k | 120.2 / 107.3 / 99.0 | 10.37 / 10.34 / 9.51 | 0.392 / 0.064 |
    | 100k | 80.9 / 71.2 / 66.2 | 9.57 / 9.04 / 8.36 | 0.742 / 0.145 |
    | 118k | 66.9 / 67.4 / 65.8 | 9.01 / 8.82 / 10.0 | 0.868 / 0.176 |

  - The deltas within a depth are successive turns: each later turn starts after the preceding delta plus 128 generated
    tokens, not after a reset. Save and restore ran on the external LaCie disk, so those seconds are not comparable with
    the internal-disk slot timings.
  - Decode against the background-priority run, which reported one decode value per depth: 16k 10.48 against
    13.77-16.3; 118k 7.21 against 8.82-10.0.
- **Apple M5 Max 64 GB at recorded normal priority, kit 1.6.7, llama.cpp `dde879bc`, Qwen3.8-27B and Glimmer 30B
  (Sergey, via Ivan, 2026-11-03; launched from Terminal).** Archives in `.temp/m5max64-results-261103/`:
  - `qwen27b-mac-bench-results-20261103T171250Z.tar.gz`, sha256 1d0d04a3...704c, model 31629f53...;
  - `glimmer30-mac-bench-results-20261103T183326Z.tar.gz`, 89211edd...9f9f, model 4cc57c0f...;
  - Both manifests: `normal_priority: true`, `priority_override_used: false`, ctx checkpoints 0. The readiness records
    show llama-server and its ancestry at PRI 31, nice 0 in every sample (Qwen 36, Glimmer 31). Both runs together took
    3 h 31 min (Sergey).
  - **Qwen, step 40, depth ladder** (prefill tok/s for the segment / Δ512 / Δ2000 / Δ10000, then decode tok/s):

    | Depth | Prefill | Decode |
    |---|---|---|
    | 16k | 662.9 / 550.3 / 475.9 / 447.9 | 23.26 |
    | 50k | 417.0 / 415.9 / 368.3 / 352.1 | 19.93 |
    | 100k | 281.2 / 265.6 / 234.6 / 232.7 | 15.54 |
    | 150k | 203.7 / 196.4 / 177.2 / 173.9 | 12.96 |
    | 200k | 156.1 / 155.3 / 139.5 / 137.7 | 11.11 |
    | 249k | 127.8 / 130.5 / 117.6 / 116.2 | 9.78 |

    Slot saves: 714 MB at 16k (43.6 KiB/token, 62 ms) to 8,833 MB at 249k (34.6 KiB/token, 702 ms). Four streams at 32k:
    40.08 tok/s aggregate, single 19.64, x2.04.
  - **Qwen, step 55, parallel decode by depth** (median aggregate tok/s by stream count; gain against one stream):
    - 32k, np 16: 23.108, 32.834, 46.87, 60.964, 57.089, 62.727 at 1/2/4/8/12/16 streams; x2.71 at 16.
    - 64k, np 8: 20.163, 26.257, 33.09, 40.816 at 1/2/4/8; x2.02 at 8.
    - 128k, np 4: 16.186, 18.825, 20.778 at 1/2/4; x1.28 at 4. A second np-4 server gave 24.351 at 4 streams (rounds
      22.80-26.29).
    - Against the kit 1.6.6 sweep of 2026-11-02, whose priority was not recorded: -2.2% to +3.0% at every point except
      12 and 16 streams on 32k, -9.1% and -4.3%.
  - **Qwen, step 56, 260k:** one-time prefill of 260,000 tokens at 199.2 tok/s; decode 9.711 tok/s with one stream and
    10.643 with two (x1.10). 1.04M was skipped: no slot file on this Mac.
  - **Qwen, step 57, agent sessions at 128k:** aggregate decode 12.373 / 11.159 / 12.576 tok/s with 1 / 2 / 4 sessions;
    mean prefill 89-92 tok/s; call p50 49.5 / 18.2 / 87.6 s, p90 150.9 / 107.4 / 357.8 s.
  - **Glimmer, step 40** (native context 131,072; prefill segment / Δ512 / Δ2000 / Δ10000, then decode):

    | Depth | Prefill | Decode |
    |---|---|---|
    | 16k | 662.2 / 630.9 / 541.0 / 516.1 | 27.08 |
    | 50k | 446.7 / 421.7 / 377.4 / 383.4 | 22.65 |
    | 100k | 347.9 / 323.6 / 304.3 / 308.0 | 20.83 |
    | 118k | 296.8 / 302.2 / 281.6 / 285.5 | 20.09 |

    Slot saves: 7.3-9.6 KiB/token. Four streams at 32k: 48.6 tok/s aggregate, single 23.72, x2.05.
  - **Glimmer, step 55:**
    - 32k, np 32: 29.045, 39.291, 59.22, 91.628, 90.835, 94.004, 75.543, 92.291 at 1/2/4/8/12/16/24/32; x3.24 at 16.
    - 64k, np 32: 27.122, 35.397, 50.784, 70.949, 64.977, 72.154, 60.715, 70.45; x2.66 at 16.
    - The 128k series was skipped: no stream count fits the native context.
  - **Glimmer, step 56, 129k, np 8:** 19.863, 24.397, 34.727, 42.214, 46.938 at 1/2/4/6/8 streams; x2.36 at 8.
  - **Glimmer, step 57, agent sessions at 64k:** aggregate decode 20.688 / 19.827 / 23.21 / 28.45 tok/s with 1 / 2 / 4 /
    8 sessions; mean prefill 169-190 tok/s.
  - **Decode batching against depth on the same Mac:** Qwen (34.6-43.6 KiB/token) keeps x2.71 at 32k, x2.02 at 64k and
    x1.28 at 128k. Glimmer (7.3-9.6 KiB/token) keeps x3.24, x2.66 and x2.36 at 129k.
  - **Against the M3 Max at PRI 31, Glimmer:** decode at 118k 20.09 against 8.82-10.0; Δ2000 prefill at 118k 281.6
    against 67.4.

- **512k and 1.04M slots for the Mac, the GPU fill (kit 1.6.8 `ee3da64e`, Muse r7am ACCEPT; Vast node E, RTX PRO 6000
  Blackwell Server Edition; 2026-11-03 15:35-16:07Z).** llama.cpp `dde879bc`, Qwen3.8-27B Q4_K_M (sha256 31629f53...3d34),
  q8_0 K/V, flash attention, one sequence, batch and ubatch 512, context 1,042,432, YaRN factor 4 (original 262,144). The
  manifest `handoff.json` (sha256 234c5b05...ad41) stays on node E in `/root/rental/work168/slots-handoff/`.
  - One continuous fill:
    - 0 to 524,288 tokens: prefill 518.29 s, so 524,288 / 518.29 = 1,011.6 tok/s on average; save 2.09 s; slot
      18,425,185,848 B (sha256 e1c89210...86e9).
    - 524,288 to 1,040,000 (515,712 new tokens): prefill 1,295.48 s, 515,712 / 1,295.48 = 398.1 tok/s; save 4.08 s; slot
      36,394,654,776 B (sha256 20c6b40a...4c64).
    - From empty to 1,040,000: 518.29 + 1,295.48 = 1,813.77 s, 30.2 min.
  - Restoring a slot on the same GPU, in a separate process: 1.83 s at 524,288 and 3.14 s at 1,040,000. Probes of 64
    teacher-forced positions: 2.81 s and 4.58 s. The reference logits (64 x 248,320 float32 per depth) are in the
    manifest for the Mac's comparison.
  - The Mac's measured download, import, logit gate and decode are pending (incident lane, after Gemma).

- **KL study of the recurrent state in bf16 (prototype `m3-state-bf16` `8d876c71`, Muse r7ah/r7ai ACCEPT; Vast node C,
  RTX PRO 6000 Workstation; new-study mode, 2026-11-03 14:01-17:15Z).** Report `report.{md,json,csv}` (sha256
  752e413c..., c0613c34..., 69b8d463...) and the provenance lock, in `.temp/kl-study/c-complete-261103/`.
  - Design: 20 pinned Gutenberg documents, 2,048 scored positions each (40,960 in total), context 32,768 + 2,048, seed
    42, score batch 32. The client is Qwen3.8-27B Q4_K_M on CUDA. The KL is to the full-precision BF16 model's
    distribution, so it measures the client's own error. Three arms: local prefill; the state imported in f32; the
    recurrent state imported in bf16.
  - Mean KL to the reference, in nats, with the 95% interval over documents:
    - local: 0.054253 (0.030386-0.081082); top-1 agreement with the reference 91.152% (89.24-92.86%);
    - f32 import: identical to local in every document, paired difference exactly 0 for both KL and top-1;
    - bf16 import: 0.053955 (0.030349-0.080441); top-1 91.218% (89.38-92.90%).
  - Paired, bf16 minus local, over the 20 documents: KL -0.000298 nats (95% interval -0.001076 to +0.000390); top-1
    +0.066 pp (-0.100 to +0.249 pp). Both intervals contain 0. The bf16 effect is about 1/180 of the client's own mean
    KL: 0.000298 / 0.054253 = 0.0055.
  - Schedule probes, 60 per arm: mean KL 0.0039 local, 0.0045 f32, 0.0021 bf16; top-1 1.000, 0.983, 1.000.
  - Incident: the GPU of node C failed at 16:38Z, when 17 of the 20 bf16 documents were committed, and the host
    rebooted at about 17:00Z. The tool resumed from its committed per-document receipts on the same GPU, build and
    models, and redid the failed document pg36 in a new attempt. The failed attempt and the logs from before the resume
    are kept in `.temp/kl-study/c-failed-261103/`.

