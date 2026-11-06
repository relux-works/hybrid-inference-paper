# Run17 measurement custody

Verified local copies of kit1.6.5 archives. Source host inputs were read from
`/home/agent/lanes/hybrid/.temp/{kit165-host2,mac-results-261102}/`.
No downloads, model loads or native builds were used. Full archive and every
manifest payload digest/length were verified before use. Task scratch extracts
are under `.temp/hybrid-e-r9-261103/<source>/results/`.

| Source | Archive | SHA256 |
|---|---|---|
| qwen27_server | qwen27b-gpu-bench-results-20261102T030926Z.tar.gz | 3364b8a1ceb5a2a7521f73b051da01075ddd6d2e322f625e02abe99b1b8b2fe5 |
| glimmer30_server | glimmer30-gpu-bench-results-20261102T024947Z.tar.gz | a9c8887e1e5b24347802ca8049439aa04313d0a397f6e0ea1200aaf542f9606c |
| glimmer30_mac | glimmer30-mac-bench-results-20261102T102823Z.tar.gz | 188f97901325c464a8054d02dd305afb1d7622b33ff5df4f4686361e1a76a065 |
| gemma31_server | gemma31-gpu-bench-results-20261102T030127Z.tar.gz | a8b38efbeff4f26aa9f5215345c9791f100a7939ef59ba39eff240c0c9edc602 |
| gemma31_mac | gemma31-mac-bench-results-20261102T035935Z.tar.gz | c9ad47e8142ed8a8fc66ad3171329815dcd1a3c36761e1a558e1cf9ef6985272 |

Geometry and GPU rates correspond to FACTS section1a, q8_0 KV, Q4_K_M,
llama.cpp `dde879bc4f954b809892fd0d660515f42536394a`. Mac rates correspond
to FACTS section2 and remain `background_priority_interim`. The report explains
the distinction between tensor wire estimates and full sequence-save metadata.
Qwen PRI31 input custody remains in the frozen Run16 measurement package.

Provenance selection: `calc/hybridcalc/data/run17-measurements.json`.
Data-only future PRI31 replacement instructions: `calc/README.md`, Run17.
