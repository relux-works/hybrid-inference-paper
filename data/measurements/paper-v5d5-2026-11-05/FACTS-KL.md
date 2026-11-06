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
