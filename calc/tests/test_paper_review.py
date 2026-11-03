"""Finite controls for the external-review text migration; no new runtime claim."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hybridcalc.session_hosting import route
from publication_v2 import ROOT, check_publication, read_texts

CHANGED_TEX = (
    '00-abstract', '01-introduction', '02-workload', '04-channel', '05-clients', '05b-models',
    '06-server', '07-economics', '09-security', '11-limitations', '12-related',
    '14-conclusion', '90-appendix', '08-million', '13-outlook',
)


class PaperReviewTests(unittest.TestCase):
    # Each changed TeX file reaches both the exact-byte and numeric-site guard.
    # These are publication-drift controls, not proof of the prose's semantics.
    def test_review_sites_reject_prose_drift(self):
        texts = read_texts()
        check_publication()
        for stem in CHANGED_TEX:
            name = 'paper/sections/' + stem + '.tex'
            with self.subTest(file=name):
                with self.assertRaisesRegex(AssertionError, 'v2 publication bytes changed: ' + name):
                    check_publication(texts=dict(texts, **{name: texts[name] + '\n% planted prose drift\n'}))

    def test_review_sites_reject_unregistered_numbers(self):
        texts = read_texts()
        check_publication()
        for stem in CHANGED_TEX:
            name = 'paper/sections/' + stem + '.tex'
            with self.subTest(file=name):
                with self.assertRaisesRegex(AssertionError, 'unregistered v2 numeric site'):
                    check_publication(texts=dict(texts, **{name: texts[name] + '\n% planted 883\n'}))

    # The independent aggregate deltas locate the entire difference in Codex;
    # identical export filters and billing's all-row sum exclude a price filter.
    def test_corpus_difference_is_snapshot_not_billing_filter(self):
        old = json.loads((ROOT/'data/measurements/ivmbp-2026-10-30/session-call-dates/stats.json').read_text())
        new = json.loads((ROOT/'paper/data/owner-model-usage-2026-10-30.json').read_text())
        self.assertEqual(old['params'], new['params'])
        self.assertEqual(old['params'], dict(sample=0, min_calls=1, max_mb=0, chars_per_token=3.6))
        self.assertLess(old['generated'], new['generated_utc'])
        self.assertEqual((old['agents']['all']['calls'], new['agents']['all']['calls']), (1528194, 1530739))
        for agent, delta in (('claude', (0, 0)), ('codex', (2545, 1)), ('muse', (0, 0))):
            with self.subTest(agent=agent):
                self.assertEqual(tuple(new['agents'][agent][k] - old['agents'][agent][k]
                                       for k in ('calls', 'streams')), delta)
        spec = importlib.util.spec_from_file_location('review_bill', ROOT/'paper/data/year_bill.py')
        bill = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bill)
        recs = bill.bill(new['model_usage'], bill.load_prices(ROOT/'paper/data/model-prices-2026-10.csv'))
        total = bill.summary(recs)
        self.assertEqual(total['calls'], 1530739)
        self.assertLess(total['priced_calls'], total['calls'])
        self.assertEqual(sum(r['calls'] for r in new['model_usage']), total['calls'])
        for agent, date in (('codex', '2025-11-18'), ('claude', '2026-05-07'), ('muse', '2026-08-06')):
            self.assertEqual(new['agents'][agent]['call_time']['first_utc'][:10], date)

    # A mixed finite fixture independently checks the appendix numerator:
    # local input+output plus previous remote output, divided by remote calls.
    # Pending work changes compute time without retransmitting the local tail.
    def test_appendix_deferred_tail_and_unchanged_wire(self):
        steps = route([50, 1, 40], [10, 2, 5], [6, 4, 8], [2, 1, 3], [100, 200, 300], [0, 0, 0], 'at_offload')
        self.assertEqual(steps.pending_seconds, (2 + 4 + 3) / 2)
        self.assertEqual(steps.pending_calls, 0.5)
        self.assertEqual(list(steps), [(14.5, 0, 100, True), (1, 1, 0, False), (9.5, 0, 300, True)])
        # Removing a marginal offload must increase the survivor's catch-up;
        # a model that uses current delta alone would keep the first call.
        narrowed = route([12, 1, 40], [10, 2, 5], [6, 4, 8], [2, 1, 3], [100, 200, 300], [0, 0, 0], 'at_offload')
        self.assertEqual(narrowed.pending_seconds, 13)
        self.assertEqual(list(narrowed), [(12, 12, 0, False), (1, 1, 0, False), (18, 0, 300, True)])
        # No profitable remote call must mean no remote effects and no tail charge.
        rejected = route([1, 1], [2, 2], [6, 4], [2, 1], [100, 200], [0, 0], 'at_offload')
        self.assertEqual(rejected.pending_seconds, 0)
        self.assertEqual(list(rejected), [(1, 1, 0, False), (1, 1, 0, False)])


if __name__ == '__main__':
    unittest.main()
