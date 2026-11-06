# Historical provenance fixtures

`revisions.json` lists the full original commit IDs, aliases and consumers.
`manifest.json.gz` records complete path/mode/blob-OID/size/SHA256 inventories.
Each content record either names an immutable in-tree export/measurement or
an authenticated gzip object in `objects/`. Canonical references are selected
against accepted paper `f33c5df3d650e2f09dd6c498d44711eb393331eb`, never the
mutable working tree. All content required by the original readers is retained.

The runtime module pins both the manifest and `port-code.json` by SHA256.
The latter identifies exactly six provenance-only adapters. Original producer
hashes remain unchanged in frozen manifests; current computation/input hashes
must still match them. AST regression checks preserve every other function.
The module compares fixtures to real Git whenever original commits are present,
and announces fixture mode when they are absent. It never fetches history.

Rebuild with `python3 -B .scripts/generate-history-evidence.py` from a checkout
holding all original revisions. `--check` performs deterministic reproduction;
`--code-only` refreshes adapter pins after explicit review. Runtime verification:
`python3 -B calc/tests/check_history_evidence.py`.

This is a content/provenance proof. It does not claim that private engine commits
are ancestors of the public owner's deliberately squashed release commit.
The separate Git-access guard and real public-layout tests enforce portability.

## Accepted engine-parent extension

The manifest now binds23 revisions and4124 unique original blobs, including accepted run25/run26
and the04c paper baseline. Nine exact live provenance adapters have separate hashes. The two new
whole-parent audits require original engine bytes or explicit finite paper successors, and a
fully enumerated current manifest; no computation/input/output migration is authorized.
