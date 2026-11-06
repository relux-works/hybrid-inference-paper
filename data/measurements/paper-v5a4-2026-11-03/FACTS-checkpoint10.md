  - **Checkpoint 10 recheck (r45, code `72566bca`, Muse r7ae ACCEPT; on the M3 Max at PRI 31, 2026-11-03
    08:32:30-12:42:57Z, checker wall 4 h 10 min 28 s; incident lane, independent root review).** Archive
    `r45-checkpoint10-recheck-20261103.tar`, 1,042,503,680 B, sha256 aecde1ed...5e1f (transfer to the Bulgaria node
    in progress).
    - Exit 5: heterogeneous CUDA node against Metal client. This is not a calibrated acceptance.
    - Depth 109,591, 64 positions. L-H: top-1 64/64; mean KL 7.7296e-5 nats, p95 1.7031e-4; maximum absolute logit
      difference 0.2097. The checker reports no free-running divergence within 64 tokens; the free-running sequences
      were not persisted, so the raw logits cannot prove that field independently.
    - Local identities, all exact (gate true, raw logits exact): CHAIN-H, A-L, OWN_NATIVE-A, OWN_RANGE-A, and
      CHAIN_RECURRENT-H.
    - Controls against the CUDA node's values, not exact (findings): NODE-B, NODE_RANGE-B and CHAIN_ATTENTION-B with
      directional KL(B || probe) 5.0115e-5 nats; RESTORE-B and BSTATE-B with exact raw logits but unequal snapshot
      bytes at 106,849.
    - The Metal client's own partition noise: mean KL 8.5664e-7. The L-H to partition ratio is 90.2; this is not an
      acceptance threshold.
    - For comparison, the CUDA-to-CUDA GPU rehearsal: KL 1.06e-4 / 1.54e-4 / 2.45e-4 / 6.2e-5 at checkpoints
      10/20/30/40, top-1 64/64 at each.
  - Resync: the last import boundary before checkpoint 10 (106,849) lies past the outage depth (103,024).
  - Decode at PRI 31 was 10.0-12.3 tok/s from 100k to 143k in both arms. The background-root kit runs gave 5.2-7.5 tok/s
    at those depths on stock `dde879bc`. The kit 1.6.7 A/B on stock `dde879bc` at PRI 31 (section 2, PRIORITY A/B)
    gave 10.36 tok/s at 100k and 8.99 at 150k.
