# Paper v4b source record

FACTS.md is the owner's live source copied for r20b; SHA-256 `e6c2d46b84ae721770543b4bec2bd98a5a779c3e981dc5d8ebaa14ed4ce2d5ca`.
Includes Sergey's M5 priority answer via Ivan, 2026-11-03 09:11 UTC. Section 5 calls its update08:25 UTC,
with the brief's08:40 label noted explicitly. This is a source snapshot, not a live job-status poll.

`derived-prefill.json` recomputes the R16 local-prefill distribution over all39,904 normalized calls, including
zero-input calls. Formula `new_tokens / local_rate(depth)` follows the perimeter reference in
`hybridcalc.run14_r5.perimeter_table`. Mean/median/p90 are calculated before display rounding.
Reproduction and negative zero-drop control: `python3 -B -m unittest discover -s calc/tests -p test_paper_v4b.py`.

Gemma window geometry is supplied directly in the owner's r20b brief (kit1.6.5 notes):
1024 positions *435200 B =445644800 B. FACTS4 supplies43520 B/new-token full-attention KV.
No new measurement or calibrated Gemma/Glimmer threshold is inferred. Frozen R16 architecture projections
retain their original min(delta,window) geometry; a complete window transfer is distinguished in the gap map.
