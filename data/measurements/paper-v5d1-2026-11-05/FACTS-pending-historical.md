## 5. Pending: state as pending, with the expected date

Updated 2026-11-03 08:25Z (the v4 brief labels it 08:40Z).
- Paired RULER (updated 2026-11-03 15:40Z). Qwen 8k and 32k are complete (section 3). Running:
  - node A (Bulgaria): the bf16 arms at 8k and 32k from 14:24Z, then the three-arm 64k depth;
  - node B (Czechia): 128k from 14:29Z, about 32-36 h, so until about 00:00-02:00Z on 2026-11-05;
  - node D (Japan): Glimmer 8k is complete (section 3); 32k, 64k and 122,880 follow, 33-50 h for all four depths.
  - The pre-registered equivalence analysis (`m3-ruler-prereg` 7556f461) applies to the depths that finish before the
    RC4 data cut-off, 2026-11-05 12:00Z.
- Fidelity of the CUDA to Metal main run: measured on 2026-11-03 (checkpoint 10 recheck, section 3). Calibration of
  the heterogeneous tolerance is still pending, so its exit 5 is not a calibrated acceptance.
- The full parallel curve on the M3 Max at normal priority (the intermediate stream counts): needs an idle Mac window
  from the owner.
- Glimmer 30B and Gemma 4 31B on the M3 Max at normal priority: the same window. Their kit 1.6.5 Mac numbers were
  measured at background priority.
- Engine run 16b: the normal-priority multi-stream M3 anchors, after the full curve.
- CUDA to Metal calibration against the BF16 reference: needs the Mac.
- vLLM state bridge on GPU: after its rework.
- Bonsai 2 ladder 2B/4B/9B: later.
- Measured since the earlier pending list, so no longer pending: the KL study (stage 2; stage 3 stopped and not
  reported), the task-level evaluation (eval4-eval7), the sliding-window GPU qualification, GPU kit 1.6.5, the B300 runs,
  the Mac kit 1.6.5 runs of Gemma 4 and Glimmer (at background priority), and the end-to-end CUDA to Metal run over 5G.
