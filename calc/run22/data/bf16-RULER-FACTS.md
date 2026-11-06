- **Paired RULER, the bf16 state arm at 8k and 32k (RTX PRO 6000, node A; candidate `m3-state-bf16` `8d876c71`, Muse
  r7ah/r7ai2/r7ai4 ACCEPT; 2026-11-03 14:23-18:41Z).** Archives `bf16-8192-complete.tar.gz`, sha256 c0348572..., and
  `bf16-32768-complete.tar.gz`, 5efae77a..., with their analyses, in `.temp/ruler-results-261103/bf16-8d876c71/`.
  - Only the bf16 offload arm ran. Local, f32 offload and partition are the frozen rows of the 8k and 32k runs on the
    same node, examples and seed.
  - Score disagreements against local: 0 of 390 at 8k and 0 of 390 at 32k. Against the f32 offload arm also 0 and 0.
  - Answer text changed against local: bf16 28 and f32 34 at 8k (McNemar exact p 0.109); bf16 33 and f32 33 at 32k
    (p 1).
  - After the arm, the stage could not restore the original services: the port was still busy, and the shared build
    record no longer matched. The 64k depth therefore runs on freshly built services at the same commit (next block,
    when it lands). The bf16 results are complete and unaffected.

