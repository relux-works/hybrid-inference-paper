# Paper sources

Title: «Hybrid Inference with Client–Server Prefill–Decode Disaggregation: Architecture and Economics for Unified-Memory
Clients». Russian title: «Гибридный инференс с клиент-серверным разнесением prefill и decode: архитектура и экономика
для клиентов с унифицированной памятью».
Authors: Ivan Oparin, Alexey Grigoriev, Timur Kackan and Sergei Shchepetkov (Relux Works).

| File | What |
|---|---|
| `hybrid-inference.ru.tex` | The Russian version, written first. The English version will be `hybrid-inference.en.tex` |
| `preamble.tex` | Layout shared by both versions: A4, 10 pt, PT fonts, booktabs tables, TikZ styles, the version line |
| `fonts/` | PT Serif, PT Sans and PT Mono, each with its licence (SIL Open Font License 1.1) |
| `version.tex` | Written by `make pdf` from git; not tracked |

Build from the repository root with `make pdf`. Versions and releases are described in the root `README.md`.

The v4b follow-up preserves the title, thesis and all non-superseded results. The abstract is limited to 1920
characters; the whole-paper no-growth target is revoked. See `../calc/PAPER-V4B-GAPS-261103.md` for restoration,
counting, every pending site and validation evidence. The owner PDF is
`../.temp/hybrid-c-r20b-261103/hybrid-inference-v4b-draft.ru.pdf`.

The v4c source/gap map is `../calc/PAPER-V4C-GAPS-261103.md`. The owner PDF is
`../.temp/hybrid-c-r20c-261103/hybrid-inference-v4c-draft.ru.pdf`. Six pending sites distinguish
FACTS5 waits from the two explicit r20c measurement requests.


Paper v5a keeps the title, four Cyrillic author names and release version. The opening/closing thesis is the
shared prefill server and per-session client decode. Current cost numbers are `% R20:` pending sites; the entire
previous economics and its figures are preserved in `sections/91-calculation-history.tex` as a historical calculation.
Accepted data, all pending sites and review-note resolutions are mapped in `../calc/PAPER-V5A-GAPS-261103.md`.
The owner draft is `.temp/hybrid-c-r21-261103/hybrid-inference-v5a-draft.ru.pdf` from the repository root.
