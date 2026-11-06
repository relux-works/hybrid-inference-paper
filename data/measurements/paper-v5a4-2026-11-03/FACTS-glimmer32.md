- **Paired RULER for Glimmer, 32k depth (same node D, prototype `715c81a4`, examples and seed as 8k; 2026-11-03
  15:35-19:55:58Z including the pilot).** Archives `results-32768.tar.gz`, sha256 e39acffc...0533, and
  `pilot-32768.tar.gz`, b62ae48a...ae21, with `analysis-32768.json` and `.md`, in
  `.temp/ruler-results-261103/glimmer-715c81a4/`. Both
  archives verified against their sha256 files on agents1. Owner decision 19:05Z: Glimmer stops at 32k. The stage was
  stopped by PID after the 32k archive, and node D was destroyed at 19:58:16Z.
  - RULER score: local 87.26%, offload 87.12%, partition 87.18%.
    - Fully correct examples against local: 4 and 4 for offload, McNemar exact p = 1. Partition has the same counts.
    - Per task, local / offload / partition: cwe 2.67 / 3.33 / 3.33; niah_multiquery 96.67 in all three;
      niah_multivalue 91.67 / 92.50 / 93.33; qa_1 80.00 / 76.67 / 76.67; qa_2 63.33 in all three; 100% in all three
      arms in the other 8 tasks.
  - Answer text changed against local:
    - offload 111/390 = 28.46% (95% Wilson 24.21-33.13%);
    - partition 114/390 = 29.23% (24.94-33.93%);
    - offload only 7, partition only 10; McNemar exact p = 0.629.
  - Excess, offload minus partition: -0.77 pp, 95% interval -4.37 to +2.86 pp. Equivalence at the 2 pp margin is not
    established: the interval is wider than the margin.
  - Changes by task, offload / partition, of 30: niah_single_2 21 / 20, niah_multivalue 17 / 17, niah_single_3 17 / 17,
    niah_multikey_2 13 / 12, niah_multikey_1 12 / 13, niah_multiquery 10 / 11, niah_multikey_3 7 / 9,
    niah_single_1 7 / 7, cwe 3 / 3, qa_1 3 / 3, qa_2 1 / 1, fwe 0 / 0, vt 0 / 1.
  - Score differences against local, offload / partition: at 8k +1.22 / +1.17 pp; at 32k -0.14 / -0.08 pp.
