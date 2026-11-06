- **The owner's call logs priced by model class (paper repository `paper/data/year-bill-summary.json`, computed by
  `paper/data/year_bill.py` from `paper/data/owner-model-usage-2026-10-30.json`; October 2026 provider prices; classes by
  the Artificial Analysis index; the table in appendix C).** Read from the paper checkout on 2026-11-05; the analyst's
  arithmetic was rechecked against the file.
  - Calls: 1,530,739 in total, 1,521,469 priced.
  - Qwen-tier calls (classes at_or_below and effort): 21,935 + 238,266 = 260,201, that is 17.0% of calls.
  - Their bill: $606.13 + $4,823.74-5,126.72 = $5,429.87-5,732.85, against a total of $112,543.74-124,462.94. That is
    4.6-4.8% of the bill.
  - Frontier models (class above): 1,248,111 calls (81.5%), billed $106,836.72-118,452.94. The same tokens at Qwen3.8-27B
    reference prices: $15,061.07-24,456.49.
  - Remaining: unclassified 13,157 calls ($277.15), unknown 3,092 and local 6,178 calls (unpriced).
  - Reading: most of the money is in frontier-model calls. Whether Qwen-27B can solve those tasks is not tested in the
    paper, so the price per call is not the price of completed work.
