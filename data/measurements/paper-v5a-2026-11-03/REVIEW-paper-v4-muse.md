# Review: paper v4, three passes (Muse reviewer, run hybrid-rev-r5u-paper-v4-261103)

Candidate bound: `paper-v4` at `4ee9a9a52a39b29d084a5c384d5f6445ec33adfd`, base `release-0.1.0-rc.3` at `5f9846f3` (tree `5b2e4caae48e79861ed70b03246ed4790ca6a467`, re-verified). Range `5f9846f3..4ee9a9a5`, 16 commits, all signed (`%G?` = G) with the Codex co-author trailer; engine merges `fff1480` (run 16, parent `e51942d`) and `dd7a7e2` (run 17, parent `714fe72`) carry the exact accepted parents. Producer runs hybrid-c-r20, r20b, r20c. Reviewed in an isolated detached worktree at the candidate head; all gates rerun there at `4ee9a9a5`.

## Verdict

**ACCEPT** — bound to `4ee9a9a52a39b29d084a5c384d5f6445ec33adfd`. No blocking findings; six notes below. Full engine suite at this head: 443 tests, OK, exit 0 (923.9 s, this review's rerun; the first attempt lost its exit code to a `/bin/sh` substitution error in the reviewer's own harness and was rerun cleanly).

## Findings array

```json
{
  "findings": [],
  "notes": [
    {
      "id": "checker-direction-label-stale",
      "row": "gates",
      "text": "paper/data/check_ranges.py:526 names a direction '1M: refill of a million tokens on M3 Max takes longer than a day' but predicates max(refill) < 24. The paper correctly prints about 20 h (08-million, conclusion) and the wording site at line 705 binds 'заново около 20 часов'. The checker label contradicts its own predicate and the text; the gate passes for the right numeric reason under a wrong name. Rename the direction at the next checker edit."
    },
    {
      "id": "limitations-ttft-label-bytepin-only",
      "row": "labels",
      "text": "Relabelling the limitations sentence 'Вычитание снимков даёт арифметическую верхнюю оценку...' to 'даёт производственный TTFT' survives check_ranges and offload_bound (both exit 0) and is killed only by the publication_v2 byte pin (exit 1, 'v2 publication bytes changed'). The composed gate set holds, but this one label has no semantic site registration; an authorized --refresh migration would launder it. Register the limitations wording as a named site."
    },
    {
      "id": "bare-eto-inherited",
      "row": "style",
      "text": "Strict reading of 'pronoun only with its noun': 'Это в 4.8--5.2 раза дороже...' (07-economics) refers to the $67--73 price of the previous sentence without a noun. The sentence is inherited from rc.3 with renumbered ratios; all other new demonstratives carry their noun ('Эти оценки', 'Это соотношение') or name the referent in the same sentence ('Это сопоставление разных условий'). One-word fix if the owner wants strict compliance."
    },
    {
      "id": "abstract-measured-modelled-split-dropped",
      "row": "owner-direction",
      "text": "The abstract rewrite (char limit) drops rc.3's explicit measured-vs-modelled split sentence and the 'growth is moderate' sentence from the abstract. Both remain in the body (clients/economics captions, conclusion). Abstract-only compression under the 1,920-char requirement, not a paper content cut."
    },
    {
      "id": "decode-headroom-percent-dropped",
      "row": "owner-direction",
      "text": "05-clients drops the old derived 'about 40% of the bandwidth limit' for single-stream decode when replacing the throttled 7.5--8.8 tok/s with PRI 31 14.99 tok/s; no PRI 31 percentage is computed. The 37% four-stream figure is retained with its PRI 4 label. One derived percentage lost with its superseded input."
    },
    {
      "id": "producer-gate-reuse",
      "row": "gates",
      "text": "Producer final-gates.json reuses kit/range/offload/ledger receipts from 54c7562 at frozen source 6112860 (intervening: README/CHANGELOG/gap map/publication_v2.py one-line path fix) and the PDF receipt from 664a404. The reuse argument is documented with finite path lists. This review reran every gate at 4ee9a9a5, so acceptance does not depend on the reuse."
    }
  ]
}
```

No blocking findings. Every attacked surface below either held under a narrowing mutant or was verified against an independent source.

## 1. Numbers (74 independent checks, all pass)

Independent sampler `/tmp/rev-r5u-sample.py` (74 checks against engine CSVs, FACTS literals, the time-accounting report, and recomputed arithmetic; 5 first-pass mismatches were formatting only and verified by hand: printed 25.370/19.659/2.908 are roundings of report values 25.369948/19.658720/2.907521; RULER percentages carry TeX `\%`). Prioritised sites:

- M3 Max PRI 31: segment/Δ/decode anchors (191.5…30.1; 174.2/65.3/28.7; decode 14.99/10.36/6.93) match FACTS PRIORITY A/B and run 16; intro 44.37 tok/s and 225 s = 10000/44.37 recomputed; parallel anchor counts 57.375/37.862/18.705/18.77 match FACTS kit 1.6.7.
- 5G growing session: residuals 483.3/43.1/35.3 vs local 884.0/33.7/38.9, depth 143,439, decode 10.0–12.3, resync 106,849 > 103,024 — all in FACTS and the text.
- Time accounting: 10.643+123.219+42.423+25.370 = 201.655; 2.508157+0.399364 = 2.907521 (2.908 printed); 41.168/40.165/25.748 GB in report and text; (271.5−201.655)/271.5 = 25.7%.
- Link thresholds (run 17 CSV `architecture_link_threshold.csv`): Qwen f32/bf16, Glimmer, Gemma at 32k/64k/100k × Δ512/2343/10000 sampled at 11 cells, all within 0.001 of printed. Retained run 16 B300-case values 8.05/7.20/5.40/4.83 printed as a separate basis, not substituted.
- Extrapolation cells S0/K2 0.159, S10/K2 0.491, S78.5/K34 5.307, S157/K34 7.909 match `architecture_extrapolation.csv`.
- bf16: saving 78,446,592 B; transfer 24.458→16.412 s at 9.75 MB/s and 45.947→30.832 at 5.19 recomputed from wire bytes 238,467,072/160,020,480; egress $0.00476934/$0.00320041 at $0.02/GB recomputed; 0.00389 < 2^-8 = 0.00390625.
- Gemma/Glimmer geometry: 1024×435200 = 445,644,800 B; Δ1000 payloads 50,522,368 / 489,164,800 B; 50.522368/37.5 = 1.35 s; hypothetical 84.590592 MB and 11.8 s recomputed.
- RULER 8k: 97.01%, 0/390 score disagreements, 34/390 (8.72%) vs 32/390 (8.21%), McNemar p = 0.727, interval −2.13…+3.12 pp — FACTS and limitations agree.
- Import law: intercept 0.28530138 − 539×0.0000487 = 0.25905208; appendix 0.2591 + 48.7 µs/token + 34.64 µs/depth; 94.2% slope share from FACTS.
- Clients/economics cells recomputed from `calc/out/run16/base/`: tab:clients M3 14.266→14.3, 3.973→3.97, 5.469→5.47, gain 1.377→1.38 (M4/M5/Ultra/Strix/Spark rows likewise); M5 hosting $5.57→$5.6 vs compute $54.88→$54.9 (`person_cost_s20.csv`, team 50).
- 1M refill: piecewise integration of the printed PRI 31 segment reciprocals with the stated linear extrapolation gives 19.9 h (printed 19.9 / about 20 h).

## 2. Labels (none overstated)

- Capture-subtracted residual is called an arithmetic upper bound containing evidence hashing at every surface (abstract, tab:growing-5g caption, channel prose, tab:time-accounting caption, limitations, conclusion); production TTFT is stated as not measured. A relabelling mutant is killed by the composed gates (see notes).
- Mac checkpoint fidelity is pending (4 sites: channel, outlook, conclusion, appendix `\pending`); GPU rehearsal 4/4 is stated CUDA-only.
- RULER equivalence at 2 pp is stated not established (abstract and limitations).
- M5 priority: not recorded, launcher at PRI 31 on later check (clients table caption, economics captions, conclusion, clients prose).
- SWA thresholds and comparisons carry both the PRI 4 interim label with PRI 31 rerun queued and the named Qwen import-law transfer estimate without SWA calibration (tab:model-link caption and following paragraph, tab:swa-measured caption, Gemma paragraph in 05b-models, tab:arch caption).
- Architecture table and S/K grid are labelled extrapolations, not model claims (captions and prose); bf16 rows carry CPU-lossy implementation with GPU/Mac quality and speed pending (channel opening, tab:model-link caption, bf16 paragraph with `\pending`, related-work row).
- All M3 multi-stream derived values (tab:clients, tab:agents-day, traffic volumes, economics tables) carry the ‡ interim PRI 4 mark.

## 3. The reviewer's rc.3 points

- Abstract: 1,425 raw TeX chars; 1,383 by this review's plain stripping (producer: 1,364 plain / 1,372 conservative). Under 1,920 by every count. Contains the link boundary (5.19 MB/s all-local; 7.905 MB/s f32 threshold at Δ2343/100k from run 17, replacing run 16's 8.05, which stays in the body as the separate B300-basis estimate).
- Link boundary also in limitations (Граница канала paragraph) and channel Порог канала section.
- Economics as applicability boundaries with both comparators (median API ×(1.2–1.5) cheaper, cheapest API ×(4.8–6.0) dearer) in abstract, introduction, and conclusion, worded as conditions, no promotional adjectives.
- Conclusion team-size sentence rebuilt and independently recomputed from `calc/out/run16/base/perimeter_cost_light{,_conservative}.csv` (selected rows, M5 Max 64 GB, Mac already owned vs selected all-server): 5 people +5.1%, 10 +10.1%, 20 +19.5% (identical under both policies), 50 −27.3%/−17.0%, 500 −38.2%/−28.9%, 5000 −38.5%/−29.8%. Exact match to the printed sentence. An applied 27.3→37.3 mutant is rejected by `offload_bound.py` (exit 1) and `publication_v2.py` (exit 1, unregistered numeric site); `check_ranges.py` alone does not bind it.
- Novelty sentence present (conclusion line 5): internet link with client-side decode, two growing copies with journal and resync, client-side audit, immediately after the predecessors sentence.
- 25.5 s explained and replaced: traced 25.370 s = 19.659 s inside node request preparation (upload, first-byte wait, node load/export/save, checksums; not separately timed) + 5.711 s client; full stream 202.089 s distinguished from TTFT 201.655 s.

## 4. Owner direction (no significant cuts for length)

Section word counts (rc.3 → v4, `wc -w`): abstract 391→201, introduction 918→956, workload 706→648, architecture 1395→1395, channel 1716→3080, clients 2114→2377, models 1759→1953, server 1534→1534, economics 3513→3853, million 823→823, security 692→692, resilience 217→217, limitations 873→1027, related 1290→1324, outlook 337→338, conclusion 558→610, appendix 1347→1498. PDF 33 pages (decompressed page count), producer main-text count 17,264 words.

Removed passages not superseded by newer data — complete list:

1. Abstract measured-vs-modelled split sentence and moderate-growth sentence (abstract only; body retains both). See notes.
2. Single-stream decode headroom "about 40% of limit" derived percentage (05-clients). See notes.
3. Channel closing rule-of-thumb paragraph ("Гибриду нужен канал от 100 Мбит/с…") replaced by per-call run 17 thresholds; qualitative content survives in quantified form (15.8%/31.8% offload shares, threshold table). Superseded in substance, listed for completeness.

Everything else removed is superseded: throttled PRI 4 Mac numbers (kept only as labelled interim/historical rows), planned-RULER sentences, the broken team-size sentence, the 25.5 s unattributed wording, the growing-session placeholders and TODOs, the old 42.4/39504 import coefficient, and the first-call-only conclusion paragraph (full first-call accounting retained and expanded in channel; KL/pilot abstract sentences relocated to appendix lines 141–144, marked `v4b-relocated-quality`). Commit `e16f55d` documents the r20 restoration pass; spot checks confirm the restored material is present.

## 5. Gemma correction

The r20b sentence claiming Gemma needs a faster link than Qwen is absent (grep: no match). Replacement (05b-models): fixed part larger (445.6 MB arithmetic retained: 1024×435,200 = 445,644,800 B > Qwen 156.9 MB; full-attention KV 43,520 B/token), local Mac prefill slower; thresholds Δ2343: 100k 6.588 vs Qwen 7.905, 32k 21.851 vs 17.606, 64k 10.984 vs 12.342 — all match run 17 CSV and the depth-dependent direction was recomputed from the CSV. All three comparisons carry the interim + import-estimate labels in the same paragraph.

## 6. Style (Russian editorial rules)

- No «» quotes anywhere in `paper/sections/` (grep clean).
- No «не X, а Y» / «X, а не Y» in changed lines; the three `, а ` hits are plain additive conjunctions with measured contrasts, not antithesis.
- No dash connectors in new prose; `---` occurrences are pre-existing empty-cell placeholders in tables, `--` are numeric ranges (permitted).
- ё present throughout new prose (трёх, ещё, четырёх, всём, дешёвого); no `еще/трех` without ё in changed lines.
- Pronouns: new demonstratives carry their noun, with one inherited exception (see notes).
- Measurements only: comparatives in new text (медленнее, быстрее порога, выгоднее) restate adjacent printed numbers; the retained heading "Какая модель удобнее гибриду" is rc.3 wording now fenced as an operations-scaled extrapolation. No promotional adjectives, no empty openers in changed lines.

## 7. Gates (rerun by this reviewer at 4ee9a9a5)

Environment: detached worktree of `4ee9a9a5`, `TMPDIR` on disk, `PYTHONDONTWRITEBYTECODE=1`, Python `-B`. First cached-PDF attempt failed (exit 2) because this session's `XDG_CACHE_HOME` points at an empty curator cache; with `XDG_CACHE_HOME=/home/agent/.cache` the same cache-only command exits 0. That failure is environmental, retained here for honesty.

| Gate | Command | Exit |
|---|---|---|
| Engine suite | `python3 -B -m unittest discover -s calc/tests` (443 tests, 923.9 s, OK) | 0 |
| Kit suite | `python3 -B -m unittest discover -s bench/tests` (24 tests) | 0 |
| Range checker | `python3 -B paper/data/check_ranges.py` | 0 |
| Range self-test | `python3 -B paper/data/check_ranges.py --self-test` (156 site controls) | 0 |
| Offload checker | `python3 -B paper/data/offload_bound.py` | 0 |
| Offload self-test | `python3 -B paper/data/offload_bound.py --self-test` | 0 |
| Publication guard | `python3 -B calc/tests/publication_v2.py` | 0 |
| Ledger guard | `python3 -B calc/tests/r13_ledger.py` | 0 |
| Spacing guard | `python3 -B .scripts/publication_spacing.py` | 0 |
| Release guards | `bash .scripts/test-release.sh`; `bash .scripts/test-release-signatures.sh` (12 passed) | 0 |
| Cached PDF | `make pdf TECTONIC=.../tectonic-cached` (adds `--only-cached`) | 0 |
| Manifest | `make manifest`; `sha256sum --check --quiet MANIFEST.sha256` | 0 |
| Signature | `git verify-commit HEAD`; `%G?`=G for all 16 commits | 0 |

The reviewer's own cached build is byte-identical to the producer PDF `.temp/hybrid-c-r20c-261103/hybrid-inference-v4c-draft.ru.pdf` (319,521 B, sha256 `2b44f479…379e88`, 33 pages, no Overfull/undefined-reference hits in the log).

Adversarial mutants (applied to candidate blobs, restored after each; clean controls re-pass):

| Mutant | Result |
|---|---|
| Abstract threshold 7.905→7.005 | `offload_bound` exit 1 (killed) |
| Conclusion 27.3%→37.3% | `offload_bound` exit 1, `publication_v2` exit 1 (killed); an earlier unapplied sed attempt was discarded, not counted |
| tab:model-link interim wording removed | `offload_bound` exit 1 (killed) |
| Limitations residual relabelled production TTFT | `publication_v2` exit 1 byte pin (killed); semantic checkers exit 0 — see notes |

## Pending inventory

Exactly six `\pending` sites, byte-identical to the gap map list: `04-channel.tex:128` (timing-only runs), `:159` (checkpoint 10), `:332` (bf16 GPU/Mac), `11-limitations.tex:76` (RULER depths), `90-appendix.tex:132` (checkpoint 10/RAM), `:134` (grouped FACTS §5 waits). Each maps to FACTS §5 or an explicit r20c owner input. No pending site has data in FACTS (RULER 8k, both 5G timing arms, CPU bf16 are all reported as results, not pending).

Free disk was 31 GB at start, 30 GB through the main gates, and 27 GB at engine-suite completion (floor 28 GB; this review's own footprint was the 436 MB worktree, now deleted; the shared host was also written by other sessions). No downloads, no native builds. Review worktree and logs under `.temp/rev-r5u/` deleted after handoff.
