- **Growing session CUDA to Metal over 5G, the main run: both timing arms complete, the checkpoint unmeasured
  (2026-11-02 22:56Z to 2026-11-03 02:44Z).**
  - Setup:
    - client M3 Max (Metal, prototype `fca0fe31` plus the r44 driver `5be993f2`), every process at PRI 31;
    - node RTX PRO 6000 Server in Bulgaria;
    - link through one SSH stream: 9.75 MB/s down, RTT 140.6 ms;
    - 100k pre-staged start, 40 turns (seed 1), outage at turns 2-4.
    - Timing extract `.temp/growing-mac-261102/TIMING-EXTRACT.json.gz` (d0d3f021...). Private archive on the owner's
      LaCie: 4.13 GB, sha256 93ab0d9b....
  - Hybrid arm: 40 turns, 38 local and 2 offloads (turns 7 and 31). Local arm: 40 turns, all local.

    | Arm | TTFT sum / mean / median | Total time | Local prefill | Decode |
    |---|---|---|---|---|
    | Hybrid | 1,158.7 / 28.97 / 2.35 s | 3,646.4 s | 173.3 s | 11.06 tok/s (10.00-12.16) |
    | Local | 262.9 / 6.57 / 2.24 s | 2,736.8 s | 246.0 s | 11.12 tok/s (10.03-12.29) |

    The hybrid arm also spent 9.7 s on imports and 134.9 s on catch-up, with 477 MB on the wire.
  - The two offloads, against the same turns run locally:

    | Turn | Delta | Hybrid TTFT | Wire | Import | Catch-up | Local TTFT |
    |---|---|---|---|---|---|---|
    | 7 | 2,343 tokens | 468.7 s | 238.5 MB | 4.0 s | 3.3 s | 33.7 s |
    | 31 | 2,343 tokens | 490.5 s | 238.5 MB | 5.6 s | 3.8 s | 38.9 s |

  - Instrumentation split (`.temp/growing-mac-261102/INSTRUMENTATION-TIMING-EXTRACT.json.gz`, trace e38da6db...).
    The checker's full node snapshot captures run synchronously inside the call's TTFT. TTFT minus capture is an
    arithmetic residual, not a production TTFT.

    | Call | TTFT | Captures | Capture time | Residual | Local, same call |
    |---|---|---|---|---|---|
    | Base 100k | 2,896.8 s | 10, 22.11 GB | 2,413.5 s | 483.3 s | 884.0 s |
    | Turn 7 | 468.7 s | 1, 3.88 GB | 425.6 s | 43.1 s | 33.7 s |
    | Turn 31 | 490.5 s | 1, 4.91 GB | 455.2 s | 35.3 s | 38.9 s |

    - Captures ran at 9.1-10.8 MB/s.
    - Base components: server prefill 41.9 s, transfer 397.4 s (3.64 GB in 10 chunks), final import 2.9 s, staged
      chunk imports 0.26-0.34 s each.
    - Correction and time accounting (dev-d r13): the 2.908 s import is the sum of all ten chunk imports (nine staged
      requests 2.508 s, then the final save and apply 0.399 s), not an extra final import. After snapshots, server
      prefill, transfer and imports, 41.168 s of the base remain; 40.165 s of them lie inside the ten node extend
      requests. Those requests include the node's full-state load before prefill and save after export, checksums,
      and the synchronous evidence hashing of 25.748 GB (snapshots plus delta), which the snapshot-download timer does
      not subtract. Turns 7 and 31: 9.859 s and 7.786 s remain, of them 5.272 s and 6.637 s inside the extend requests.
      The split between instrumentation hashing and node serialization is not measurable from these traces; the
      timing-only runs record separate spans.
    - Reading:
      - over this 5G link, the 100k base minus instrumentation took 483 s against 884 s local, about 1.8x faster;
      - the two per-turn offloads came out 9.4 s slower and 3.6 s faster than local. The policy predicted 31.8 s
        offload against 42.7 s local, but its local rates came from the background-root fixture, and the local Mac
        at PRI 31 was faster than that.
  - Base 100k:
    - hybrid pre-stage TTFT 2,896.8 s, with 3.64 GB on the wire and a 2.9 s import; that includes the snapshot
      captures (see the split above);
    - local prefill 884.0 s (880.2 s prefill).
  - Checkpoint 10, first attempt: not measured. The checker labelled the Metal backend `MTL` (ggml registry name), and
    `check.cpp:523` maps only `Metal`, so the guard refused.
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
