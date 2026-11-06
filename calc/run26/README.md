# Run26 closed-contour sensitivity

Separate added files on run25 ec28e37c; run24/run25 bytes frozen. CPU-only Python standard library, no model runtimes/builds. Root README/manifest remain unchanged to honor the frozen parent; this README documents the new tools.

```bash
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/.temp/hybrid-e-r21b-261105/tmp"
python3 -B -I calc/run26/export.py
python3 -B -I calc/run26/finish.py
python3 -B -I calc/run26/finish.py --audit-only
python3 -B -I -m unittest discover -s calc/tests -p 'test_run26*.py'
python3 -B -I -m unittest discover -s calc/tests
python3 -B -I -m unittest discover -s bench/tests
```

`model.py` defines client admission, prefill-only service, GLM architecture-derived KV, expert union, Ultra two-die scaling, common internal large-model cost, and cloud capacity floors. `engine.py` scans every integer team1..500 for both profiles, light/medium/heavy, s20/50/100%, owned/new64/128GB Max and256/512GB Ultra clients, bought/rented same-model servers. GLM x1/x2 prefill portability is UNMEASURED. Fleet1/2/4/min variants at team50 reuse run25 PRO-only IO/queue proxies; they are not GLM measurements or globally optimal fleet proofs.

`export.py` writes compact tables under `calc/out/run26/`, paper selections under `paper/`, and `calc/ENGINE-REPORT-R26-261105.md`. Before/after each write it checks exact bytes and df-BG; refusal leaves accepted files untouched. All CSVs together must stay under50MB. The new manifest binds sources, report, exports and ALL parent-tracked bytes. Logs/real exit receipts live under `.temp/hybrid-e-r21b-261105/`; validation is `calc/R26-VALIDATION-261105.json`.

Public model-card/config and Apple captures with hashes are under `data/`; no weights downloaded. Apple512GB configuration exists; US reported list prices are sourced purchase-cost proxies. Prior failed403 is disclosed. GLM/Ultra/large-model service and task-success share remain pending inputs. Primary hybrid server generation overflow refuses; it is never silently priced as prefill-only service. Mixed totals contain an identical common large-model capacity FLOOR plus unknown service/storage, not a cloud API and not a full service-price claim. No push.

`export.py` checkpoints completed stages under the task TMPDIR parent, bound to source/data identity and the fully verified parent tree. Resource retries preserve completed stages. `finish.py` adds compact quote coordinates, conditional MoE verdicts and publication metadata audit. An owned-capital blank on refused rows is normalized to0.0; every other cell is asserted identical. This changes no feasible price, crossing or model rate.
