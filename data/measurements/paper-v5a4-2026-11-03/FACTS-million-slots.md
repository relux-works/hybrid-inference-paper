- **512k and 1.04M slots for the Mac, the GPU fill (kit 1.6.8 `ee3da64e`, Muse r7am ACCEPT; Vast node E, RTX PRO 6000
  Blackwell Server Edition; 2026-11-03 15:35-16:07Z).** llama.cpp `dde879bc`, Qwen3.8-27B Q4_K_M (sha256 31629f53...3d34),
  q8_0 K/V, flash attention, one sequence, batch and ubatch 512, context 1,042,432, YaRN factor 4 (original 262,144). The
  manifest `handoff.json` (sha256 234c5b05...ad41) stays on node E in `/root/rental/work168/slots-handoff/`.
  - One continuous fill:
    - 0 to 524,288 tokens: prefill 518.29 s, so 524,288 / 518.29 = 1,011.6 tok/s on average; save 2.09 s; slot
      18,425,185,848 B (sha256 e1c89210...86e9).
    - 524,288 to 1,040,000 (515,712 new tokens): prefill 1,295.48 s, 515,712 / 1,295.48 = 398.1 tok/s; save 4.08 s; slot
      36,394,654,776 B (sha256 20c6b40a...4c64).
    - From empty to 1,040,000: 518.29 + 1,295.48 = 1,813.77 s, 30.2 min.
  - Restoring a slot on the same GPU, in a separate process: 1.83 s at 524,288 and 3.14 s at 1,040,000.
    These are warm restores: each file had just been written and the kit did not drop the OS cache.
    36,394,654,776 B / 3.14 s = 11.6 GB/s. A cold restore was not measured. Probes of 64
    teacher-forced positions: 2.81 s and 4.58 s. The reference logits (64 x 248,320 float32 per depth) are in the
    manifest for the Mac's comparison.
  - **Download to the owner's M3 Max, measured** (incident lane, 2026-11-03 19:34:37Z to about 20:15Z). The published
    kit 1.6.8 fetcher pulled 1 GiB ranges over 8 parallel SSH streams from node E (Japan), with a full resync. The
    custody supervisor checked the size and whole-file sha256 of both slots and their references against the node's
    manifest.
    - 524,288: slot 18,425,185,848 B in 1,026.042 s, so 17.96 MB/s of useful throughput. The received payload was
      18,880,529,976 B (18.40 MB/s), including 455,344,128 B of retried ranges. The retry causes were not recorded.
    - 1,040,000: payload 36,394,654,776 B in 1,365.377 s, 26.66 MB/s.
    - Both slots: 54,819,840,624 B of slots in 2,391.419 s (39.9 min), so 22.92 MB/s useful.
    - Each wall interval includes the range-manifest fetch, retries, disk writes and hashing. It excludes the
      reference downloads and the gaps between files. This is not wire-only bandwidth: it is one owner link at one
      time of day, not a link model.
    - The incident lane's root custody review (2026-11-03 ~20:34Z) reread every byte, recomputed all 18 + 34 one-GiB
      ranges, both whole-file hashes, the manifest bytes and both 64 x 248,320 float32 references: ACCEPT. That
      review released the node-E retention hold.
  - The Mac's import, logit gate, decode and delta prefill are pending (kit 1.6.10, after a fresh admission).
