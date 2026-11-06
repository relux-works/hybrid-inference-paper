# Paper v5d6: analyst and external candidate review

Base: signed provenance-port head d909764 on paper-v5, fast-forwarded from accepted f33c5df3. No release commit, version change, push or tag. Native engine 24 and all earlier measurement archives remain unchanged. Full documentary sources and exact finite successor tuples are in data/measurements/paper-v5d6-2026-11-05/.

## Resolved corrections

- **Measured median inversion.** calc/out/run24/api_prices.csv and calc/run24/api.py prices()/ranked() use identical paper-shape means and per-provider tariffs for no-cache and measured prices. The overall no-cache cohort has15 priceable admitted providers and upper-middle median8.68082670435457 (Wafer). The measured v1 cohort has11 and median12.549870329346795 (DeepInfra). On those exact11 providers the no-cache median is19.711326477535152 (also DeepInfra). Thus12.55 versus8.68 compares different cohorts;19.71 versus12.55 is like-for-like. Every measured cost is no larger than the same provider's no-cache cost. No cache-write premium is needed to explain the inversion. Full provider names, sorted costs and source SHA are in arithmetic.json.
- **Cadence bias.** Accepted reconstructed Claude aggregate gaps have median8.1s/p90 60.6s, not measured tool time. The v1 long-pause cohort is less favourable to caching; no qualified measured short-interval Qwen price point exists. Ionstream3.604 has one warm observation. Both abstracts remove the median-API gain. The body retains the conditional heavy-load crossing at5 with the v1 caveat, against45 at the unverified owner98.1% allowance.
- **Closed perimeter.** Current5-medium/2-heavy crossings apply to the20% open-model segment; the other80% runs on a stronger cloud model. This is not a closed perimeter. Abstracts and introductory block defer a100% recalculation; all retained thresholds state their segment scope. Archived Q4 closed-perimeter tables remain explicitly historical and supply no current guarantee.
- **Mac logit bound.** The524288 attempt refused max1.08298 against1.0; the next attempt used4.0 with the same KL/top-1 metrics. No prose calls this a passed acceptance. Same-depth local-versus-local partition calibration is newly pending. KL/top-1/max metrics remain in the measured table.
- **Million-token boundary.** At1040000, ordinary-priority decode1.6638 tok/s means512/1.6638=307.7293s,5.1288min. Published400e9B/s divided by measured model18973870432B plus34816*1040000=36208640000B KV plus156893184B recurrent state gives7.2281227094tok/s; ratio to measurement4.3443459006. These are a peak-bandwidth estimate, not a measured kernel limit or causal explanation. Apple Support117737 supplies400GB/s for the16-coreCPU/40-coreGPU M3 Max; accepted normalized-results.json supplies model_bytes. All three measured1M APIs fail95%; PRO vLLM holds3*256000=768000 resident cache tokens and fails the61.97GiB need against56.62GiB available. B300 remains unmeasured. The operational conclusion is technical feasibility with slow interactive generation on M3.
- **Quality and reading.** Complete64k390/390 replaces the368-row interim publication;97.18% every arm, text-change28/32, exact McNemar.5716 and excess[-5.51,+3.49]pp. It resumes on the same original node with a whole-manifest check and unchanged369 rows. Completion arrived after the12:00Z cutoff and is included by this explicit owner brief.128k remains225/390 interim, with completion moved B to A using B's exact binaries/libraries and within-example pairing. Full Holm waits for128k; no score interval is invented. Results precede Limitations in the document, with existing source-file identity retained for custody.
- **Replay.** Published prereg dfffda35, amendment7ab1dedd, implementationc2df294e and draft PR18 are planned, not run. Server components and CUDA bridge checks do not establish full-path Metal time or task success. The accepted40-turn no-speedup statement is unchanged; Swarm Inference comes last.
- **Duplication.** Seven identical appendix table bodies were removed in favour of the sole main-text tables. Unique methods captions remain as prose. Prior interim rows are a labelled historical slice, distinct from the current complete64k table. Repeated introduction/conclusion economics becomes five short applicability points and five differently worded closing statements; full scenario arithmetic moves once to the supplement.

## Analyst block: number corrections and conditions

-5 medium/2 heavy are removed from the closed-perimeter bullet and replaced by a100%-share pending calculation; they survive only as20%-segment scenario crossings elsewhere.
-20% is the declared open-model segment; remaining80% executes in the stronger cloud model. The scope covers10885/39904=27.28% call shapes normalized to200/800/2500 calls/day; none establishes covered tokens or work.
-The approximate1.7tok/s is printed1.66, rounded from1.6638. The262k RTX5090 boundary is retained;32GB fits one session. The owned M5/officePRO basis stays.
-The median bullet retains45 people at the owner98.1% allowance and5 at measured long-pause v1, with cadence bias and no short-interval point stated. The cheapest measured API boundary is retained, limited to priceable measured Qwen cohorts.
-The analyst's approximately4.5x memory-ceiling shortfall becomes4.34x from the explicit arithmetic above; a512-token answer is5.13min. The fleet estimate20 instead of57 remains an analyst estimate conditional on one node sufficing, not an accepted replacement for table18.

## Pending

1. Engine25 A: minimal sufficient fleet of one/two nodes, RAM/NVMe session copies and on-demand restore. Table18 remains byte-identical.
2. Engine25 B: closed perimeter at100% open-model share.
3. Engine25 C: shares of tokens and work covered by the admitted call shapes.
4. Mac calibration of maximum absolute logit difference between local runs with different partitions at524288 and1040000.
5. Full128k RULER and registered four-depth/Holm analysis after completion on A with B's exact build.
6. Clean paired preregistered Metal end-to-end replay without diagnostics/hashing on the critical path, with cold start separate; no long-task speedup or task-quality conclusion yet.
7. Existing B300 decode, admitted Qwen1M provider, Macbf16, timing-only/heterogeneous calibration and declared model/engine follow-ups remain pending. Exact macros are bound by calc/tests/data/paper-v5d6-pending.json.

## Validation and scope

The brief has no surface table (declared brief gap). No acceptance clause is excluded. Scope: paper content, documentation, finite publication/checker successors and regression tests. Native engine code/exports, kit, historical fixtures and measurement archives are preserved. Every previous test name remains; changed expectations explicitly follow the new owner-authorized publication locus or the retained historical slice. Exact-byte publication pins and private-history guard catalogue are refreshed explicitly; fixture gateway guarantees are unchanged.

Fresh signed-head gate receipts, source retention, PDF/counts and addressed report live in .temp/hybrid-c-r21m-261105/. Diagnostic nonzero receipts remain diagnostics, never reused as green gates. Named omission controls cover all finite successors; narrowing controls and their named failing tests are recorded there. No remote inference, package download, native build, push, tag or release commit.

The publication receipt also corrects a pre-existing local-variable shadow: architecture chart rows no longer overwrite the numeric-site set used for the reported count. A dedicated assertion compares the receipt with the full registry; all original content assertions are retained.

The analyst's office-only median wording is scoped to the primary basis: the measured long-pause v1 rented-PRO crossing at443 people remains a separate scenario and is now explicit in the introductory bullet. The original cutoff status is corrected to distinguish owner-authorized complete64k after12:00Z from the remaining128k/Holm wait.

The exact self-test diagnostic ledger declares31 overlapping plants among697 named sites. The authoring generator predicts couplings from literal finite paragraphs without calling missing(); runtime requires every exact named diagnostic, including independent pending-inventory failures. No predicate is skipped or suppressed. A bounded test plants a real overlap and proves both omitted and unrelated diagnostics fail the same assertion. The first superseded-head self-test failure is retained as diagnostic evidence.
