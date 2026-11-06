# Paper v5d part4: independent-review precision

Base signed70733c416e8508ebbc4a9f5e945d359693e48e15. Accepted native engine24 ca7f228acd789380bf46016fd87acc33e1b07aef unchanged. RC4 cutoff2026-11-05 12:00Z unchanged. Title/authors/VERSION unchanged; no push/tag/native build or measurement collection.

## Results, calculations and conflicts resolved

- Fresh39504-token CUDA/Metal call:201.655s against271.5s, (271.5-201.655)/271.5=25.7%, about26%. Background-priority M3,16.0MB/s/110ms; single call only. Full named FACTS block archived.
- Forty turns at9.75MB/s/140.6ms:3646.4s against2736.8s, excluding base preparation. Only2offloads; outage and resync completed. No long-session speedup established. Subtraction3646.4-425.6-455.2=2765.6s retains hashing/instrumentation and is not measured production time. Base2896.8/884.0 separately. Hashing25.748GB belongs to base preparation, not the two offloads.
- Analyst134.9s is the sum of catchup_seconds across32 calls. Accepted receipts give7.0877s in the two offload summary fields; time-accounting spans distinguish current blocking work from earlier journal work. The text does not assign134.9s solely to two offloads or assert every enclosing interval is on their critical path.
- Server14x is16k/Delta10000 prefill;10.1-10.8x is the interpolated profile-depth prefill ratio. Model1.38 daily capacity is archived,125MB/s/1Gbit/s with background multistream anchors. No figure is promoted to measured autonomous-task speedup.
- Run24 primary dedicated cheapest measured Qwen comparison is unchanged. Free-prefill floor2.52+5=7.52 exceeds3.604082737*840/1000=3.03 at light load only; a universal free-prefill impossibility at every intensity is not established by that floor. The archived free-prefill table remains archived.
- Accepted paper/data/year-bill-summary.json supports (21935+238266)/1530739=17.0% model-index-class calls and about5% of billing. These are classification/billing statistics, not completed-task rates. The1.5million-call workload does not establish Qwen task substitution.
- Archived run16 medium owned-M5 row served0.975934718:800-780.7478=19.2522 calls,2.41% unserved,97.59% rounds98% served. The prior19% came from an older basis and contradicted its table. Current run24 medium ownedM5 row is a different cohort; no archival98% is relabelled current.

## Scope and preservation

The three contributions are internet long-lived session design, measured offload boundaries, and transport exactness in measured cases. EXO1.0 undated primary page reports2.8x end-to-end on8192-token Llama3.1-8B;4x is device compute. PPD arXiv2603.13358v1 was submitted2026-03-09 and reports68% lower subsequent-turn TTFT. Both are cited in related work and novelty paragraphs. Auditing is future work; production has no reference-state reconciliation.

Client priority/build history, old/new imports, server bridge history and archived day-capacity results move to appendices. Their measured tables and original conditions are retained. New moves/revisions ledgers explicitly name each publication locus; no search-anywhere checker fallback or frozen-source edit. Quality inventory separates Metal checkpoint109591, warm Mac524288/1040000 gates, five same-device exact deep cases, fixed-journal CUDA bf16 rehearsal and interim RULER. No long alternating Metal100k-200k task-quality study is claimed.

No surface table supplied (brief gap), no acceptance clause outside scope. Rework stays in paper, publication controls/tests and documentation. No engine/model/export changes. All predecessor reviewer test names remain and their actual appendix loci are updated deliberately. Fresh16 gates at the signed candidate are required; earlier receipts are not reused.

## Named negative controls

| Mutant | Boundary | Named failing test |
|---|---|---|
| Turn snapshot residual into production time | Arithmetic is not a measured diagnostic-free run | test_all_review_sites_reject_applied_named_omission |
| Replace2.41% with19% | Frozen row determines served/unserved share | test_archived_19_calls_and_98_percent_use_same_row |
| Promote model-index classes to task success | Calls and bill do not establish completed work | test_free_prefill_and_workload_class_bounds_are_finite |
| Put auditing on production path | Audit remains separate future research | test_predecessors_and_future_audit_are_explicit |

Applied control receipts and any diagnostic failures are retained task-locally; no surviving plant is called killed. These are publication-contract tests, not unseen device or provider measurements.

## Pending sites

All10 raw macros are bound in calc/tests/data/paper-v5d4-pending.json. No pending measurement was fabricated or removed by the framing change.

1. `01-introduction.tex`: ожидает измерения: аренда не запустила контейнер

2. `05b-models.tex`: Gemma при нормальном приоритете ожидает свободного Mac.

3. `08-million.tex`: ожидает допущенного поставщика с доступностью не ниже 95\%.

4. `11-limitations.tex`: запуск Mac для качества и скорости передачи bf16.

5. `11-limitations.tex`: полные 390 пар и первичный анализ на 64 и 128 тысячах; узлы остановлены по решению владельца 2026-11-04, строки сохранены до остановки; исходные узлы поставлены в очередь на перезапуск. Граница приёма данных 2026-11-05 12:00 UTC.

6. `90-appendix.tex`: калибровка гетерогенного допуска CUDA и Metal на M3 Max, включая сравнение с эталоном BF16.

7. `90-appendix.tex`: RULER Qwen на 64 и 128 тысячах: сохранены неполные строки, полные 390 пар и первичный анализ ожидаются. Узлы остановлены по решению владельца 2026-11-04, исходные узлы поставлены в очередь на перезапуск; граница приёма данных 2026-11-05 12:00 UTC.

8. `90-appendix.tex`: перенос измеренной ограниченной кривой M3 в новые опоры движка и прогон 16b; Gemma при обычном приоритете; пакетная генерация B300, аренда не запустила контейнер; калибровка моста vLLM на GPU после переработки; лестница Bonsai 2 2B/4B/9B позднее.

9. `90-appendix.tex`: замеры времени без снимков и хэширования свидетельств, с отдельными интервалами этапов на Mac и узле.

10. `90-appendix.tex`: запуск Mac для качества и скорости передачи bf16.

## Pre-signature verification and delivery receipts

Corrected diagnostic failures from stale main-text loci, obsolete abstract expectations and overlapping marker scopes are retained in `.temp/hybrid-c-r21k-261105/`. Both checker self-tests and the focused correction controls passed. The four narrowing plants each applied once and exited1 at the named assertion; the initial audit plant was not credited until its clean control and corrected rerun. No survivor is credited. CRLF CSV whitespace is checked with core.whitespace=cr-at-eol over the full introduced diff, without path exclusions.

The pre-signature lexical count is17731 main words, against22323 before; material moved to appendices instead of being cut. RU abstract1835, EN1662 characters. Final pages/counts, every exact-head gate argv/exit, signature/source custody and addressed message readback are recorded in task-local delivery.json/final-gates.json after the signed candidate is frozen. The private evidence snapshot still followsRC4.

## Full-suite coordinate correction

The first signed candidate39c7cf9 ran all715 engine tests: exit1 with exactly one error in test_run13.Run13Tests.test_paper_ledger_omission_controls. Its891.6-second omission witness still named04-channel instead of90-appendix. The witness remains required at the actual appendix coordinate; no assertion, source value or scientific result is removed. All other15 first-candidate gates exited0 and remain recorded, but are not reused. The correction changes this legacy publication test and the delivery manifest/documentation only. Fresh all16 gates use final-r2 receipts at the corrected signed head.
