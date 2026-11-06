- **Apple M3 Max 128 GB, Qwen client decode batching by depth, capped step 55 (Mac kit 1.6.13 `4555ba33`, Muse r7aw
  ACCEPT; owner's Mac at normal priority, warm; incident lane, started 2026-11-04 01:59:38Z, completed about 03:50Z; root
  review ACCEPT).** Strict archive 1,460,215 B, sha256 6b0296ae...e436, with the incident lane. It was collected with
  two path redactions approved at 04:02Z; the raw data are retained unredacted.
  - **Design.**
    - Capped grid: 32k up to 32 streams, 64k up to 24, 128k up to 12, plus a fresh np4 control. 21 shapes, 63 rounds,
      591 fresh restores.
    - It is not the original 23-shape grid: the earlier 64k/np32 startup was refused at +262 pages under the strict
      guard, and that refusal is disclosed.
    - q8_0 KV, flash attention, 128 generated tokens, 3 rounds, a 300 s cooldown before each series.
    - Aggregate = the sum of 127 decode tokens over the longest predicted decode duration. Prompt and restore are
      excluded, so this is not end-to-end.
  - **Aggregate decode tok/s, median of 3 rounds;** the gain is against N = 1 on the same server:

    | Depth | N = 1 | Peak | At the largest N |
    |---|---|---|---|
    | 32,768 | 15.282 | 54.838 at N = 16, x3.588 | 47.974 at N = 32, x3.139 |
    | 65,536 | 13.157 | 33.647 at N = 8, x2.557 | 29.932 at N = 24, x2.275 |
    | 131,072 | 11.202 | 17.732 at N = 4, x1.583 | 17.047 at N = 12, x1.522 |

    - The other points:
      - 32k: N 2 / 4 / 8 / 12 / 24 give 22.561 / 34.104 / 48.708 / 49.096 / 44.767;
      - 64k: N 2 / 4 / 12 / 16 give 17.652 / 26.913 / 31.696 / 29.314;
      - 128k: N 2 / 8 give 13.766 / 17.674.
    - Fresh 128k np4 control: 17.694, against 17.732 in the grid (-0.21%).
  - **Memory.**
    - Swapouts were 0 in every child.
    - Pageouts per child: 64k/np24 2,455 pages (38.36 MiB) and 128k/np12 2,313 (36.14 MiB), both within the 64 MiB
      bound; the five other children 0.
    - Rounds with pageout growth carry it in the results: 14 at 64k and 10 at 128k, from 2 to 265 pages each.
  - **For comparison,** the M5 Max 64 GB client (Sergey) gave x2.71 / x2.02 / x1.28 at 32k / 64k / 128k, and the PRO 6000
    vLLM server x15.15 / x5.07 / x2.21 at 16k / 64k / 164k.
