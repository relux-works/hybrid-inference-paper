# Paper v5c (RC4 pass): inputs collected after v5b

Base: paper v5b `241a8616`, Muse r5y4 ACCEPT (2026-11-03 ~22:28Z), PDF sha256 09a49e29..., 45 pages, abstracts RU 1,763
and EN 1,601 characters.

## From the r5y4 review notes

1. **07-economics, the claude_deep paragraph.** There is a capital letter after a semicolon: «…резидентности; Эти
   пересечения…».
2. **CHANGELOG.** Two stale «Unreleased» bullets about engine 22 still pending and about the abstract budgets. Collapse
   them.
3. **Conclusion.** «сравнение с самым дешёвым API требует нового расчёта…» predates run 22. Replace it with the run-22
   statement:
   - never crossed at 98.1%;
   - crossed at heavy load from 74 without cache;
   - each cheapest-API sentence names its cache point.
4. **04-channel.** «Формат намеренно вносит потери…» is correct and bounded. Align its wording with the abstract's
   rounding sentence, if needed.

5. **Cache test (Muse r7au6).** The live code (`ce8649ca`) counts provider-mismatch rows that carry usable usage as
   availability successes, and excludes them from cache metrics. Give this one line in the paper's availability
   definition.
   - The study had six study-wide stops before 23:01Z. Their causes and fixes are in the r15d-r15j summaries.
   - Methods mention the restarts in one sentence. The data are continuous, with no replay.

## Data expected before RC4 (2026-11-05 12:00Z)

- vLLM decode batching by depth:
  - PRO 6000, kit 1.6.11, node G, running;
  - then the B300.
- vLLM 512k and 1M on the PRO 6000, step 74, in the same stage.
- The Mac step 56:
  - import, logit gate, decode and Δ690 / 2000 / 10000 prefill at 524,288 and 1,040,000;
  - the first attempt was refused at 524,288 on max |Δlogit| 1.083 against a bound of 1.0;
  - the rerun uses a bound of 4.0, and the text states both.
- The Mac step 55: the full parallel-decode curve.
- RULER Qwen 64k (node A, about 11-04 08:30Z) and 128k (node B, about 11-04 22:30Z), through `ruler_equivalence.py`.
- The OpenRouter cache test.
  - The measured hit rates and the full-window availability.
  - Use the r15g/r15h filtered end report, with the pooled 1M label and the per-phase figures.
- The Qwen bf16 rehearsal: the f32 run is done; the bf16 replay is running on node E.
- Depth quality at 512k / 1.04M: 4 of 5 done on node F.
- Engine run 23 folds in the measured server decode, the cache rates and the Mac 1M numbers.
