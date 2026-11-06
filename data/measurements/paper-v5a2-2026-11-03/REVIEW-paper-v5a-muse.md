# Review: paper v5a, the owner's theses and structure (Muse reviewer, run hybrid-rev-r5y-paper-v5a-261103)

Candidate bound: `paper-v5` at `ee4401ce28003e70ae388d38d64dd02275786a32`, base `paper-v4` `4ee9a9a5` (accepted in r5u). Range `4ee9a9a5..ee4401ce`, 2 commits (`a11635f`, `ee4401c`), both signed (`%G?` = G, `git verify-commit HEAD` exit 0 in this review). Producer runs hybrid-c-r21 and r21b. Reviewed in a local clone of the producer repo at the candidate head; every gate rerun there. Run-20 numbers are out of scope for this pass by the brief; no run-20 result is asked for or accepted here.

## Verdict

**CHANGES REQUESTED** — bound to `ee4401ce28003e70ae388d38d64dd02275786a32`. One blocking finding: link-technology names survive in the ship-facing `[Unreleased]` changelog, which review item 6 explicitly puts in scope. Everything else in items 1–5 and 7–11 held under independent recomputation and narrowing mutants. The requested fix is confined to four changelog bullets; no other rework is requested. If the orchestrator reads item 6 as typeset-only (the producer brief's scope, which the candidate meets in full), this verdict converts to ACCEPT with the finding demoted to a note, without further review.

## Findings array

```json
{
  "findings": [
    {
      "id": "link-tech-names-in-unreleased-changelog",
      "row": "links",
      "invariant": "No 5G, Wi-Fi or iPhone wording remains anywhere: text, tables, captions, figures, alt text, the changelog, guards (review item 6). Each link is described by its measured rate and RTT.",
      "mechanism": "The producer migration and its guard (calc/tests/test_paper_v5a.py:143) scan only paper/sections/*.tex. The typeset paper is clean, but CHANGELOG.md lines 16, 20, 24, 25 in the current [Unreleased] section still name the same runs 'the first 5G call', 'CUDA-to-Metal 5G timing arms' and 'engine-versus-5G validation'. [Unreleased] is unpublished RC4 release-note prose, so the residue is current ship-facing text, not released history.",
      "reproductions": [
        {
          "test": "reviewer grep against exact candidate blobs",
          "command": "awk '/^## \\[Unreleased\\]/{u=1} /^## \\[0\\./{u=0} u && /5G|Wi-Fi|iPhone/' CHANGELOG.md at ee4401ce",
          "expected_failure": "4 bullets match (lines 16, 20, 24, 25); observed exactly those 4. Control: the same sweep over paper/sections/ returns no match, and calc/tests/test_paper_v5a.py::test_link_labels_are_parameters_and_old_rates_are_retained passes, so the failure is confined to the changelog scope the producer guard does not scan."
        }
      ],
      "severity": "bypass",
      "repeat-of": "none"
    }
  ],
  "notes": [
    {
      "id": "link-tech-names-internal-residue",
      "row": "links",
      "text": "Examined and not counted as typeset residue: offload_bound.py internal site names ('5G prediction' line 271, 'preflight 5G' line 569, 'Wi-Fi all local' line 621) and a 'home-Wi-Fi preflight' comment (line 606); frozen accepted exports (growing_5g_validation.csv, offload_at_5g_9_75_mb_s columns) which must stay byte-identical; historical test fixtures (test_paper_v4b pending body, test_paper_rc3_review2 site name); released CHANGELOG sections (rc.3 and below), README.md:464 historical rc.3 description, and UNRESOLVED_QUESTIONS.md historical entries below the new superseding v5a section. No guard still pins old typeset wording: migrated markers bind the new parameter wording, verified by the clean gate run and mutants M1-M7. Rename internal site names only if the orchestrator wants literal guard-text compliance; it forces historical-fixture migration for no reader benefit."
    },
    {
      "id": "million-section-basis-fence-reach",
      "row": "superseded-claims",
      "text": "08-million keeps the GLM 1M-session economics in the main text, including 10/50/500-person comparisons (lines 33-37) and a Вывод (lines 67-70). The pass adds an old-basis fence at the head of the Стоимость сессии paragraph ('Следующий расчёт сохраняет базу llama.cpp Q4 и прежние тарифы API; текущие цены vLLM ожидают пересчёта'), which covers lines 33-37 in the same paragraph. The fence does not reach fig:million's caption (lines 61-63) or the Вывод paragraph, which restate the ratios without the basis. This is a distinct GLM/Studio scenario (run 14 snapshot, footnoted), not the run-20 Qwen perimeter thresholds, which are correctly pending; accepted here as fenced, with the ask that the second pass extend the basis label to the caption and Вывод or move the block with the rest of the old economics."
    },
    {
      "id": "glimmer-outside-preregistration-unstated",
      "row": "data-ruler",
      "text": "FACTS states Glimmer was not named in the registration and its 8k run straddles the 14:36Z registration. The paper states the criterion and that Qwen 8k/32k preceded registration, reports Glimmer 8k descriptively with text-equivalence not established, and makes no claim that Glimmer is pre-registered. The appendix pending block bundles Glimmer depths next to 'Первичный парный анализ по зарегистрированному критерию реализуется', which a reader could scope to Glimmer. No false statement; ask the second pass to state Glimmer's registration status explicitly."
    },
    {
      "id": "intro-llama-9-10s-inherited",
      "row": "thesis",
      "text": "Introduction: 'порции 10 тысяч токенов около 9--10 секунд на глубине 131--181 тысячи' for llama.cpp on B300. Reciprocal-rate interpolation of FACTS 1b anchors (1284@100k, 1131@150k, 1010@200k), recomputed by this review, gives 8.44 s at 131k and 9.50 s at 181k, so the printed range overstates the low end by about 0.6 s. The sentence is inherited unchanged from accepted v4 (e16f55d), not introduced by this pass; correct opportunistically in the second pass."
    },
    {
      "id": "checker-files-duplicate-dead-constant",
      "row": "gates",
      "text": "check_ranges.py:30 FILES now lists 91-calculation-history.tex twice and drops 14-conclusion.tex. FILES is never referenced (the loader at line 792 reads every file in sections/), and the conclusion's retained gains remain semantically bound in offload_bound.py ('conclusion M3 gain', 'M5 gains conclusion'), so no coverage is lost. Cosmetic; fix the tuple at the next checker edit."
    }
  ]
}
```

## Surface results

| Row | Result | Evidence |
|---|---|---|
| 1 thesis | held | Ratios and interpolation recomputed (below); decode gain pending/modelled at every site; mutant M7 killed |
| 2 who-it-is-for / R20 | held | 38 pending sites, 26 `% R20:` bindings verified against `b6ac5abc` exports and one blob hash; mutants M1, M2 killed |
| 3 when-pays table | held | All 8 cells match run 17 CSV within 0.0015; interim flags match export; mutant M4 killed |
| 4 vendor requests | held | Three requests read in full; no vendor-plan claim (grep clean) |
| 5 cheapest API | held | Price arithmetic recomputed exactly; 98.1% labelled aggregate; mutant M6 killed |
| 6 links | broken | Finding above. Typeset paper clean; numbers unchanged |
| 7 data | held | Checkpoint 10, RULER descriptives, clients-only, YaRN, interim labels verified against FACTS; mutant M5 killed |
| 8 six r5u notes | held | Each verified at its site (below); mutant M3 confirms the semantic TTFT site |
| 9 length/content | held | No numeric token lost in any touched file; appendix judgement below |
| 10 style | held | Sweeps clean (below) |
| 11 gates | held | Full rerun table below; PDF byte-identical |

## 1. Thesis

Abstract sentence 1, introduction paragraph 1 and conclusion paragraph 1 all state the division of labour (shared server prefill; per-session KV/recurrent reads at decode; batching shares weight reads, gain falls with depth). Prefill numbers are FACTS 1c's: 23,151 vs 1,663 tok/s. Independent recomputation (`/tmp/rev-r5y-probe.py`, all PASS): 23151/1663 = 13.92; 14667/1284 = 11.42; 8673/915 = 9.48; reciprocal-rate interpolation exactly as printed in 06-server gives 10.82/10.34/10.13 at 131k/164k/181k (reviewer values 10.8245/10.3352/10.1267). "About 10x" is used only for that calculated scale and fenced in the same sentences: mixed engine and weight precision (FP8 vs Q4), marginal-cold vs finite-delta rates, "промежуточные отношения рассчитаны, отдельными замерами не являются". Decode batching is never stated as measured: introduction line 8 and 06-server line 13 carry `\pending{}` with `decode_scaling.csv; modelled … not measured` bindings; tonight's PRO 6000/B300 measurement is pending. One inherited rounding note above.

## 2. Who it is for

Identical applicability paragraphs in abstract, introduction, economics and conclusion: team sizes, load, and price ratios against median API, cheapest admitted API and own cluster are all `\pending{}`. Inventory by this review: 38 pending macro sites (37 lines; economics line 34 carries two), 26 with `% R20:` comments, matching the gap map and `paper-v5a-r20-sites.json` exactly. Every named export exists at the pinned read-only revision `b6ac5abc` in `~/Werkstatt/hybrid-calc/paper` with the named selector columns (`team_break_even.csv`, `small_team_cost.csv` incl. `requested_day`, `median_over_hybrid`, `cheapest_over_hybrid`, `own_cluster_person_month`; `decode_scaling.csv` incl. `gain`; `paper_claims.csv` incl. `unconditional_claim`); `small_team_cost.csv` blob sha256 `f7df2c64…174a` and 576 rows match `run20-deferred-sources.json`. Run 20 is not merged (`calc/out/run20` absent; suite asserts it). Superseded claims do not survive as current claims: economics states "Утверждение о выигрыше при любом размере команды не принято", the conclusion states the paper does not claim a hybrid win against the cheapest API at the owner's cache share, closed-perimeter light/medium/heavy bounds are pending, and no 5090-server conclusion exists anywhere (grep; §7). The 08-million GLM scenario is the one fenced exception (note above).

## 3. When the hybrid pays

`tab:when-pays` cells recomputed from `calc/out/run17/architectures/architecture_link_threshold.csv`: Qwen f32 100k 47.686/7.905/3.416 (Δ512/2343/10000), bf16 5.305, 32k 17.606, 64k 12.342, Glimmer 2.090, Gemma 6.588 — all PASS within 0.0015 MB/s. Caption carries the interim labels the export itself carries (`background_priority_interim=True` and the named Qwen import-law portability estimate for both SWA models; bf16 CPU-lossy with GPU/Mac pending). Strict-above/equality/local reading is stated; the two applied rows (5.19 local, 9.75 remote against the 7.905 threshold) follow from it. Cost columns are pending with an R20 binding, as briefed.

## 4. Vendor requests

«Перспективы» carries the three briefed requests as requests ("Просим…"): versioned state export (KV, recurrent state, positions, model/tokenizer hashes, RoPE/YaRN) grounded in the prototype's own manifest; documented recurrent-state layout grounded in the prototype's reconstruction and the bf16 codec; cross-engine KV format grounded in the accepted vLLM bridge's conversion. Closing sentence: "Запросы задают необходимые контракты и не описывают планы поставщиков." No vendor-plan claim found.

## 5. Cheapest API

Snapshot 2026-10-29, `qwen/qwen3.8-27b`, Chutes $0.039/$1.25/$0.0039, 262,144 context. Same model id and family stated; FP8 declared by the provider; hybrid client Q4_K_M, vLLM server FP8; quality comparisons explicitly confined to the hybrid's own arms. Admission criteria printed: context at least the needed depth, declared caching, measured cache hits, availability at least 95% in each recorded window, missing availability records disclosed as unchecked. Three cache points in `tab:cache-price` with shown arithmetic: $0.039 at h=0; $0.0045669 at h=0.981 (reviewer: 0.019·0.039+0.981·0.0039 = 0.0045669 exactly), labelled in caption and test-pinned as the owner's commercial aggregate across several APIs, a scenario without a measured Chutes hit; measured provider share and price `\pending{}`, as is final admission.

## 6. Links

Typeset paper (all sections, tables, captions, figure labels, the renamed `tab:growing-link`, EXO prior-art link): no 5G, Wi-Fi, iPhone, Ethernet, 10GbE or mobile/wired technology wording (reviewer grep clean; producer test asserts the same regex). Each measured link is described by rate and RTT with numbers unchanged from FACTS: first call 16.0 MB/s, RTT 110 ms (up 9.78 retained); growing session 9.75 MB/s, 140.6 ms; all-local preflight 5.19 MB/s, 125.8 ms; new link-check paragraph 0.798 MB/s / 71.2 ms (45.4–120.2) and 2.805 MB/s / 50.6 ms (45.6–57.0) with the 49.0 MB/s node control, different-protocol note and unknown cause. Scenario rates (100 Mbit/s, gigabit classes in channel/outlook) are engine scenarios and future work, not measured links. Broken only outside the typeset paper: see the finding (changelog) and the internal-residue note.

## 7. Data

Checkpoint 10 (FACTS r45) reported in channel and appendix with full fidelity limits: depth 109,591, top-1 64/64, KL 7.7296e-5, p95 1.7031e-4, max logit difference 0.2097, exit 5 heterogeneous without calibrated acceptance, exact local identities, CUDA-node control findings, partition ratio 90.2 stated as not an acceptance threshold, and the unpersisted free-running sequences stated as unable to prove that field. Heterogeneous calibration remains pending; the old checkpoint pending sites are gone. RULER Qwen 32k (97.44/97.44/97.18%, 33/29 text changes, McNemar p=0.618, excess −4.02…+6.05 pp) and Glimmer 8k (87.91/89.13/89.08%, 130/125, p=0.383, −2.69…+5.21 pp) are descriptive, match FACTS, and carry "эквивалентность текста при 2 п.п. не установлена"; producer tests recompute them from the committed raw analysis JSONs. No provisional primary-analysis number or equivalence verdict from FACTS's pending r16 block leaks into the text (grep for its distinctive values clean). The pre-registered criterion is stated in full (paired score difference, ±2 pp, whole 95% interval inside (−2,+2), Newcombe 10 / paired bootstrap 10,000 seed 261102, TOST α=0.025, Holm across four depths, registered 2026-11-03 14:36 UTC, Qwen 8k/32k observed before registration) and its analysis is `\pending{}`. RTX 3090/5090 appear as clients only, with every FACTS ladder and parallel anchor (producer test rebuilds each table row from FACTS literally; reviewer recomputed the four parallel ratios 1.97/1.81/1.56/1.98 and the 86%/78% PRO 6000 comparisons), capacities 262,144/99,328 with the 3090 Qwen ladder ending at 86k, normal priority, 5090 client-only stated twice, no licence rationale. YaRN: static model-card factor 4, original 262,144 beyond 262k; API extension method stated unknown. Glimmer and Gemma keep PRI 4 interim labels with PRI 31 reruns pending; Glimmer's normal-priority Mac run is pending-in-progress.

## 8. The six notes of r5u

All six addressed and verified at their sites: (1) `check_ranges.py:526` direction renamed to "takes less than a day", predicate `max(refill) < 24` unchanged, with 24/25 h negative controls in `test_r5u_refill_direction_rejects_day_or_more`; (2) limitations residual now has the named semantic site `v5a limitations residual semantics` — reviewer mutant M3 (production-TTFT relabel) is killed by `offload_bound.py` exit 1, where r5u found only the byte pin; (3) bare «Это» replaced by "Эта месячная цена" at its moved site in 91-calculation-history; (4) abstract restores the measured/modelled split ("Скорости и перенос измерены; экономика и рост ёмкости дня остаются расчётами") and the growth limit sentence; (5) decode headroom restored with shown arithmetic, 14.99·(18.9739+0.5571+0.1569)/400 = 0.738 (reviewer 0.7378; KV term = 16,000×34,816 B = 0.5571 GB), fenced as an estimated roof without a measured-bandwidth claim; (6) producer receipts in delivery.json are all bound to the delivered head `ee4401ce` with no reuse (`older_receipts_reused: false`, first-head failure retained as diagnostic), and this review reran every gate independently, so acceptance does not depend on producer receipts in any case.

## 9. Length and content

No cuts. Producer main-text count 17,264 → 15,968 words is the economics relocation (07-economics 3,853 words in v4 → 609 now; new 91-calculation-history 4,312 words by `wc -w`), PDF 33 → 37 pages. No measured point lost: reviewer token audit found every numeric token of old 07-economics present at equal or higher count in new economics+history (766 → 925 tokens), all 10 old economics labels present, and no reduced numeric token in abstract, introduction or conclusion either; checker sites were migrated to the moved locations with predicates unchanged. Judgement on the appendix: keeping the superseded economics is acceptable in this pass and does not mislead a reader who reads linearly, because the appendix opens with two explicit old-basis fences (llama.cpp Q4 server, prior API pricing, run 16 storage; "текущие границы применимости … ожидают пересчёта"; 5090-server excluded), the current economics section states its bounds are pending and points to the appendix as a different-basis calculation, and the abstract/conclusion carry no old ratio. Residual risk is a reader landing directly on an appendix table via search; the second pass replaces the appendix content with run 20 in any case. The one place the fence is thin is 08-million (note above), not the appendix.

## 10. Style

Changed and new prose checked against `style.ru.md`: no «» quotes anywhere in `paper/sections/` (grep clean); no «не X, а Y» / «X, а не Y» in added lines (the single `, а ` hit is an additive conjunction in inherited text); no dash connectors in added lines (`--` occurrences are numeric ranges); ё used in new prose (added-lines sweep for `еще/трех/четырех` clean); new demonstratives carry their noun (the r5u exception fixed, §8). Numbers in new text trace to FACTS, the run 17 export, or shown arithmetic (spot-recomputed in §§1, 3, 5, 7, 8). Comparatives restate adjacent printed numbers; no promotional adjectives or quality judgements introduced. The pending macro's visible label changed to "Ожидается:"; the abstract counter includes rendered labels (reviewer count 1,600 plain chars, limit 1,920).

## 11. Gates (rerun by this reviewer at `ee4401ce`)

Environment: local clone at the candidate head, `TMPDIR` on disk, `PYTHONDONTWRITEBYTECODE=1`, Python `-B`, `XDG_CACHE_HOME=/home/agent/.cache`. Free disk 29.12 GB at start, 28.66 GB before the gate runs, 28.56 GB at the end (floor 28.2 GB; no gate started below it). Logs under `.temp/rev-r5y/logs/` in the review workbench.

TMPDIR note, retained for honesty: this review's first engine-suite run used `TMPDIR=/tmp/rev-r5y-tmp` outside the clone and exited 1 with one error in the pre-existing, untouched `test_run16.Run16Anchors.test_data_only_replacement_rejects_unrecorded_sweep`: `r16_audit.changed_cells()` calls `Path.relative_to(ROOT)` on a temp file, which raises `ValueError` when TMPDIR is outside the repository. The producer convention (and delivery receipts) place TMPDIR inside the repo. The single test passes with repo-local TMPDIR (Ran 1 test, OK), and the full suite was rerun clean at the same head with `TMPDIR` inside the clone: 455 tests, OK, exit 0 (603.1 s). The first failure is this reviewer's harness placement against a pre-existing test assumption, not a candidate defect; both logs (`engine.log`, `engine2.log`) are retained.

| Gate | Command | Exit |
|---|---|---|
| Engine suite | `python3 -B -m unittest discover -s calc/tests` (455 tests, 603.1 s, OK; see TMPDIR note below) | 0 |
| Kit suite | `python3 -B -m unittest discover -s bench/tests` (24 tests, OK) | 0 |
| Range checker | `python3 -B paper/data/check_ranges.py` | 0 |
| Range self-test | `python3 -B paper/data/check_ranges.py --self-test` (156 site controls) | 0 |
| Offload checker | `python3 -B paper/data/offload_bound.py` | 0 |
| Offload self-test | `python3 -B paper/data/offload_bound.py --self-test` | 0 |
| Publication guard | `python3 -B calc/tests/publication_v2.py` | 0 |
| Ledger guard | `python3 -B calc/tests/r13_ledger.py` | 0 |
| Spacing guard | `python3 -B .scripts/publication_spacing.py` | 0 |
| Release guards | `bash .scripts/test-release.sh`; `bash .scripts/test-release-signatures.sh` (12 passed) | 0 |
| Cached PDF | `make pdf TECTONIC=…/tectonic-cached` (`--only-cached`) | 0 |
| Manifest | `make manifest`; `sha256sum --check --quiet MANIFEST.sha256` | 0 |
| Signature | `git verify-commit HEAD`; `%G?`=G for both commits | 0 |

This review's cached build is byte-identical to the producer PDF `.temp/hybrid-c-r21-261103/hybrid-inference-v5a-draft.ru.pdf` (343,332 B, sha256 `b4c06377…e69b59`, 37 pages by the build log, no Overfull/undefined-reference hits).

Reviewer narrowing mutants (applied to candidate blobs in the clone, restored after each; clean controls re-pass, tree clean):

| Mutant | Result |
|---|---|
| M1 delete one `% R20:` comment (abstract) | `offload_bound` exit 1 (killed) |
| M2 promote abstract median pending to "в 1.4 раза дешевле" | `offload_bound` exit 1, `publication_v2` exit 1 (killed) |
| M3 limitations residual relabelled production TTFT | `offload_bound` exit 1 semantic (killed; was byte-pin-only in r5u) |
| M4 when-pays threshold 7.905 → 7.005 | `offload_bound` exit 1, `publication_v2` exit 1 (killed) |
| M5 "RTX 5090 рассматривается как сервер" | `offload_bound` exit 1 (killed) |
| M6 "98.1% измерено у Chutes" | `offload_bound` exit 1 (killed) |
| M7 decode-batching gain stated as measured 2.0x | `offload_bound` exit 1 (killed) |
| M8 conclusion M3 gain 1.38 → 2.38 | `offload_bound` exit 1 (killed) |

Producer's new `test_paper_v5a.py` (12 tests) was read in full: its controls are narrowing mutants and source recomputations (RULER aggregates from raw JSON, consumer rows rebuilt from FACTS, R20 comment deletion and number insertion per site, applied-omission control per new semantic site), not positive-path only.

Free disk during review: 29.12 GB → 28.56 GB (shared host). CPU only, no downloads, no native builds. Review clone under `.temp/rev-r5y/clone` deleted after handoff; gate logs retained under `.temp/rev-r5y/logs/` and probe scripts at `/tmp/rev-r5y-probe.py`, `/tmp/rev-r5y-gates-fast.sh`, `/tmp/rev-r5y-mutants.sh`.
