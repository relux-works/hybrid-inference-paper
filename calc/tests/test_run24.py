"""Final-study admission, cadence, price normalization and frozen cost contracts."""
import copy,csv,gzip,hashlib,io,json
from pathlib import Path
import sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'calc'))
from hybridcalc.inputs import InputGap
from run24 import inputs,api,curves,engine,sentences
from run22 import interfaces as legacy


class Run24Policy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.study=inputs.load()

    # Every actually attempted endpoint below95% fails at all cache points;
    # exactly95% and a known0-hit endpoint are nearby valid controls.
    def test_under95_whole_window_endpoint_is_never_admitted(self):
        rows=api.prices(self.study);bad={k for k,v in self.study['availability'].items()if v<95}
        self.assertEqual(len(bad),10)
        selected=[r for r in rows if (r['model'],r['provider'])in bad]
        self.assertTrue(selected);self.assertTrue(all(not r['admitted']and r['effective_usd_per_1000_calls']==''for r in selected))
        endpoint=dict(context_length=1000000,supports_implicit_caching=True,pricing={})
        self.assertEqual(api.admission(endpoint,262144,95),[])
        self.assertIn('common_window_availability_below_95',api.admission(endpoint,262144,94.999))
        zero=next(r for r in rows if r['provider']=='cloudflare'and r['profile']=='existing_combined'and r['scope_tier']=='measured_ladder'and r['cadence']=='v1_long_pause'and r['cache_point']=='measured')
        self.assertTrue(zero['admitted']);self.assertEqual(zero['cache_hit_fraction'],0);self.assertGreater(zero['effective_usd_per_1000_calls'],0)

    # A study inventory's context lower bound is not an exact upper limit. It
    # cannot establish a larger-window qualified price; an actual snapshot cap
    # still rejects an impossible request at the ordinary admission gate.
    def test_context_certificate_cannot_become_an_invented_upper_limit(self):
        row=dict(context_length=262144,context_basis='final-study selected inventory minimum',supports_implicit_caching=True,pricing={})
        self.assertEqual(api.admission(row,1000000,100),[])
        self.assertFalse(api.context_verified(row,1000000));self.assertTrue(api.context_verified(row,262144))
        row['context_basis']='2026-10-29 endpoint snapshot'
        self.assertIn('context_below_1000000',api.admission(row,1000000,100))

    # Price-only old research summaries do not establish a cache declaration.
    # The accepted final-study inventory independently qualifies real GLM rows.
    def test_unretained_cache_declaration_cannot_be_invented_from_prices(self):
        row=dict(context_length=1000000,pricing={'input_cache_read':.000000012})
        self.assertIn('caching_not_declared',api.admission(row,262144,100))
        actual=api.inventory(self.study)[inputs.GLM,'coreweave/nvfp4']
        self.assertEqual(api.admission(actual,262144,100),[])
        self.assertNotIn((inputs.GLM,'darkbloom/fp4'),api.inventory(self.study))

    # V1 and core are different observed points, even for the same endpoint;
    # the final-phase aggregate includes disclosed resumed calls, not a TTL claim.
    def test_core_cadence_cannot_be_replaced_by_v1_with_raw_controls(self):
        rows=api.prices(self.study)
        selected=[r for r in rows if r['model']==inputs.GLM and r['provider']=='coreweave/nvfp4'and r['profile']=='existing_combined'and r['scope_tier']=='measured_ladder'and r['cache_point']=='measured']
        lookup={r['cadence']:r for r in selected}
        self.assertEqual(set(lookup),{'v1_long_pause','amendment_core'})
        self.assertAlmostEqual(lookup['v1_long_pause']['cache_hit_fraction'],.24250831474973794)
        self.assertAlmostEqual(lookup['amendment_core']['cache_hit_fraction'],.8524690828555279)
        self.assertEqual(int(lookup['amendment_core']['interrupted_cell_warm_calls']),9)
        self.assertEqual(int(lookup['amendment_core']['continuation_flagged_warm_calls']),6)
        self.assertIn('resumed',lookup['amendment_core']['cadence_basis'])

    # Native source prices use a different depth mix/output convention. The
    # paper point must apply the recorded hit fraction to identical paper means.
    def test_study_mix_price_cannot_replace_paper_profile_price(self):
        row=next(r for r in api.prices(self.study)if r['model']==inputs.QWEN and r['provider']=='ionstream/fp8'and r['profile']=='existing_combined'and r['scope_tier']=='measured_ladder'and r['cadence']=='v1_long_pause'and r['cache_point']=='measured')
        hit=.9589762280808326
        expected=1000*(row['mean_input_tokens']*(hit*.00000002+(1-hit)*.00000004)+row['mean_output_tokens']*.00000195)
        self.assertAlmostEqual(row['effective_usd_per_1000_calls'],expected)
        self.assertAlmostEqual(float(row['study_usd_per_1000']),1.6754078993795638)
        self.assertNotAlmostEqual(row['effective_usd_per_1000_calls'],float(row['study_usd_per_1000']))

    # A never-attempted endpoint retains snapshot availability without becoming
    # a measured cache observation; partial-cohort rankings state their limit.
    def test_unattempted_endpoint_cannot_acquire_measured_cache_or_uptime(self):
        rows=api.prices(self.study)
        row=next(r for r in rows if r['model']==inputs.QWEN and r['provider']=='chutes/fp8'and r['profile']=='existing_combined'and r['scope_tier']=='measured_ladder'and r['cadence']=='v1_long_pause'and r['cache_point']=='measured')
        self.assertEqual(row['availability_source'],'snapshot_unattempted');self.assertTrue(row['admitted'])
        self.assertEqual(row['cache_hit_fraction'],'');self.assertEqual(row['effective_usd_per_1000_calls'],'')
        rank=next(r for r in api.ranked(rows)if r['model']==inputs.QWEN and r['profile']=='existing_combined'and r['scope_tier']=='measured_ladder'and r['cadence']=='v1_long_pause'and r['cache_point']=='measured'and r['role']=='cheapest')
        self.assertEqual(rank['provider'],'ionstream/fp8');self.assertFalse(rank['complete_admitted_cohort'])
        self.assertIn('not the global',rank['ranking_basis'])

    # The final accepted study's thin observation remains labelled/descriptive;
    # fabricated Chutes smoke promotion fails the real raw-to-CSV interface.
    def test_chutes_smoke_cannot_be_promoted_with_final_thin_point_control(self):
        key=(inputs.QWEN,'ionstream/fp8','existing_combined','v1_long_pause')
        self.assertEqual(int(self.study['cache'][key]['warm_calls']),1)
        self.assertIn('thin descriptive',self.study['cache'][key]['sample_basis'])
        original=inputs.read;before=hashlib.sha256((inputs.DATA/'provider_cache.csv').read_bytes()).hexdigest()
        def planted(name):
            rows=original(name)
            if name=='provider_cache':
                row=dict(next(r for r in rows if r['profile']=='existing_combined'and int(r['series_calls'])>3));row['model']=inputs.QWEN;row['tag']='chutes/fp8';rows.append(row)
            return rows
        with patch.object(inputs,'read',planted),self.assertRaisesRegex(AssertionError,'CSV adapter differs'):
            inputs.load()
        self.assertEqual(hashlib.sha256((inputs.DATA/'provider_cache.csv').read_bytes()).hexdigest(),before)

    # The same real observation interval is required across all own availability
    # rows; a single shifted interval is rejected, while the full actual CSV passes.
    def test_whole_window_cannot_be_mixed_with_another_interval(self):
        rows=inputs.read('provider_availability');known={(r['model'],r['tag'])for r in rows}
        self.assertEqual(len(legacy.availability_rows(rows,known)[0]),len(rows))
        bad=copy.deepcopy(rows);bad[0]['window_end']='2026-11-04T07:22:23+00:00'
        with self.assertRaisesRegex(InputGap,'same stated window'):legacy.availability_rows(bad,known)

    # A failed seed still counts as a series attempt/availability event, but is
    # never added to the accepted cache token sums to satisfy the old CSV guard.
    def test_failed_seed_cannot_be_fabricated_as_cache_hit(self):
        row=self.study['cache'][inputs.GLM,'morph/fp8','million','v1_long_pause']
        self.assertEqual(int(row['warm_calls']),7);self.assertGreater(int(row['series_calls']),7)
        raw=inputs.warm_rows(inputs.GLM,'morph/fp8','v1','v1','million')
        self.assertEqual(int(row['input_tokens']),sum(r['prompt_tokens']for r in raw))
        self.assertTrue(all(r['call_index']>0 for r in raw))

    # The pooled1M result is equal-provider weighted, not the cheapest endpoint;
    # a low-availability provider cannot be smuggled into that accepted cohort.
    def test_million_pool_refuses_under95_provider_with_fifteen_control(self):
        rows=api.million(self.study);glm=[r for r in rows if r['model']==inputs.GLM]
        self.assertEqual([r['qualified_providers']for r in glm],[15,15])
        self.assertEqual(glm[0]['usd_per_1000_calls'],glm[1]['usd_per_1000_calls'])
        self.assertAlmostEqual(glm[0]['usd_per_1000_calls'],60.35482127067251)
        self.assertTrue(all(r['qualified_providers']==0 and r['usd_per_1000_calls']==''for r in rows if r['model']==inputs.QWEN))
        bad=copy.deepcopy(self.study);bad['doc']['million_token_comparison'][inputs.GLM]['with_alibaba']['priced_providers'].append(inputs.GLM+' / morph/fp8')
        with self.assertRaisesRegex(AssertionError,'under95 provider'):api.million(bad)

    # Cached team curves must keep every published hardware-cost control; a
    # changed team3 sample refuses rather than becoming an interpolated crossing.
    def test_team_curve_refuses_changed_hardware_sample_with_full_grid_control(self):
        doc=curves.load();self.assertEqual(doc['sample_controls'],5184);self.assertEqual(len(doc['curves']),864)
        bad=copy.deepcopy(doc);bad['curves'][0]['prices'][2]+=1
        with patch.object(gzip,'decompress',return_value=json.dumps(bad).encode()),self.assertRaisesRegex(AssertionError,'cache sample changed'):
            curves.load()

    # A capacity alarm at a sampled load cannot turn fixed client capital into
    # NaN for another team; the additive purchase amount matches real controls.
    def test_new_client_capital_cannot_inherit_capacity_alarm(self):
        capitals=engine.capital_costs();self.assertAlmostEqual(capitals['m5max64'],69.04895833333333)
        self.assertTrue(all(value>0 for value in capitals.values()))
        known={(curves.key(row),int(row['team'])):row for name in ('main_economics.csv','small_team_cost.csv')for row in engine.read(name)if row['basis']=='new'}
        for curve in curves.load()['curves']:
            for team in (3,5,10,20,50,500):
                price=curve['prices'][team-1];old=known[curves.key(curve),team]['person_month']
                if price is None:self.assertEqual(old,'nan')
                else:self.assertEqual(price+capitals[curve['client']],float(old))

    # Missing core observations produce an unknown comparison, never a zero API
    # price or a fabricated finite crossing. Real v1 price points remain finite.
    def test_unqualified_qwen_core_cannot_become_a_finite_crossing(self):
        table=engine.calculate();core=[r for r in table['measured_crossings']if r['api_model']==inputs.QWEN and r['cadence']=='amendment_core']
        self.assertTrue(core);self.assertTrue(all(r['from_people']==''and r['api_person_month']==''and 'unknown'in r['statement']for r in core))
        self.assertTrue(any(r['api_person_month']!=''for r in table['measured_crossings']if r['api_model']==inputs.QWEN and r['cadence']=='v1_long_pause'))

    # Every new quote carries cadence/cache point alongside all inherited link,
    # billing/client/share/load/coverage conditions; removing cadence must fail.
    def test_words_ready_refuses_missing_cadence_with_both_form_controls(self):
        row=next(r for r in engine.calculate()['measured_crossings']if r['api_model']==inputs.QWEN and r['cadence']=='v1_long_pause'and r['scope_tier']=='measured_ladder')
        for column,short in [('sentence',False),('short_sentence',True)]:
            text=row[column];sentences.validate(text,row,short)
            with self.assertRaisesRegex(AssertionError,'cadence/cache-point/model'):
                sentences.validate(text.replace('Cadence=v1_long_pause','Cadence=unknown'),row,short)


class Run24Exports(unittest.TestCase):
    # The actual publication read path must detect missing quote coordinates,
    # while preserving all1046 historical artifacts byte for byte.
    def test_published_audit_refuses_missing_quote_with_control(self):
        from run24 import export
        self.assertEqual(export.verify()['historical_files'],1046)
        original=export.read
        def missing(path):
            rows=original(path);return rows[:-1]if path==export.LEDGER else rows
        with patch.object(export,'read',missing),self.assertRaisesRegex(AssertionError,'quote coordinate'):export.verify()

    # Text-valued paper sentences also carry abstract-bound numbers. Removing
    # such a real source coordinate must fail the explicit coverage checker.
    def test_published_abstract_sentence_coordinate_cannot_be_omitted(self):
        from run24 import export
        self.assertEqual(export.verify()['historical_files'],1046)
        original=export.read
        def missing(path):
            rows=original(path)
            if path==export.OUT/'abstract_bound_changes.csv':
                i=next(i for i,r in enumerate(rows)if r['column']=='short_sentence'and r['old_source'].startswith('calc/out/run23/'))
                return rows[:i]+rows[i+1:]
            return rows
        with patch.object(export,'read',missing),self.assertRaisesRegex(AssertionError,'missing abstract-bound'):
            export.verify()

    # A planted admission in the real CSV read path is rejected by the concrete
    # under95 rule, independently of input-adapter and ranking unit tests.
    def test_published_under95_admission_is_rejected(self):
        from run24 import export
        self.assertEqual(export.verify()['historical_files'],1046)
        original=export.read
        def planted(path):
            rows=original(path)
            if path==export.OUT/'api_prices.csv':
                row=next(r for r in rows if r['availability_source']=='measured_whole_window'and float(r['availability_percent'])<95);row['admitted']='True'
            return rows
        with patch.object(export,'read',planted),self.assertRaisesRegex(AssertionError,'under95 endpoint'):export.verify()


if __name__=='__main__':unittest.main()
