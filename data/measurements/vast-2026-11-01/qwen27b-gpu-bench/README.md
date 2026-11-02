# Vast RTX PRO 6000 server measurements (2026-11-01)

Rented NVIDIA RTX PRO 6000 Blackwell Workstation Edition on Vast, 600 W, one GPU;
Ryzen 9 9950X host, driver 595.71.05, CUDA 12.8. GPU kit **1.2.0**, bench
commit **e5f64d2** (owner-supplied provenance), llama.cpp
**c21284cdf5fd833b90ac1f824cdf8065e2700dc4**, build b11087.
Qwen3.8-27B Q4_K_M, KV q8_0, flash attention.

Source: owner-delivered `qwen27b-gpu-bench-results-20261101T024637Z.tar.gz`,
SHA-256 `9accab80ed21dfa24714d5e11b16d31e0106419cd13c3fd27123528949673661`.
The archive was read locally, verified before extraction, and extracted without
changing member bytes or importing any sibling files. Only this README is added
to the extracted `results/`. `results/MANIFEST.json` identifies the model and
individual file hashes; the archive is kit-scrubbed. No new benchmark was run.

Run12 fits prompt_ms / prompt_n at the six nominal `level` values using both
2k and10k new portions (12 equally weighted observations). Actual starting depths
are slightly later than those nominal labels because turns run sequentially.
The512-token points are retained as raw evidence but excluded from this bulk
prefill fit; short-portion overhead is not measured by the fit.
Independent zero-to-context fill observations are held out of fitting.
The1040000-token fill uses YaRN x4; neither native1M context quality nor GLM
performance is measured. Existing decode, memory, hosting and prices are retained.
See `calc/ENGINE-REPORT-R12-261101.md` and the separate measured-server exports.
