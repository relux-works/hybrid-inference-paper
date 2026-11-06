"""Owner v5a: source-derived descriptive results and finite publication controls."""
from test_paper_v5a2 import current_changelog
import csv
import hashlib
import json
import re
import unittest
from pathlib import Path
from r13_audit import ROOT,module
SOURCE=ROOT/'data/measurements/paper-v5a-2026-11-03'


class PaperV5aTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5a_offload',ROOT/'paper/data/offload_bound.py')
        cls.ranges=module('v5a_ranges',ROOT/'paper/data/check_ranges.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # A production-TTFT relabelling must fail the semantic site before byte pins.
    # The same numeric content with the correct label is the positive control.
    def test_r5u_limitations_residual_label_has_semantic_rejection(self):
        key='v5a limitations residual semantics';file,marker,phrase=self.off.expected()[key]
        self.assertEqual(self.off.missing(self.texts),[])
        part=next(p for p in self.texts[file].split('\n\n') if marker in p)
        bad=part.replace('арифметическую верхнюю оценку','производственный TTFT')
        self.assertNotEqual(bad,part)
        self.assertIn(key,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,bad,1)})))

    # The direction name and predicate agree at either side of a day; the
    # historical >=24h control must fail the named engine-direction gate.
    def test_r5u_refill_direction_rejects_day_or_more(self):
        m=self.ranges.model();key='1M: refill of a million tokens on M3 Max takes less than a day'
        self.assertTrue(self.ranges.directions(m)[key])
        for hours in (24,25):
            bad=dict(m,refill={k:hours for k in m['refill']})
            self.assertFalse(self.ranges.directions(bad)[key])
        self.assertNotIn('takes longer than a day',self.ranges.directions(m))

    # The original26 deferrals remain immutable historical evidence. Current
    # promotion requires an accepted22 mapping; resurrecting any old hook fails.
    def test_r20_annotations_and_numbers_cannot_be_silently_promoted(self):
        expected=json.loads((ROOT/'calc/tests/data/paper-v5a-r20-sites.json').read_text())
        source=json.loads((SOURCE/'run20-deferred-sources.json').read_text())
        self.assertEqual(source['source_revision'],'b6ac5abcdf60b72582be87c7ad075ee460e7cc78')
        self.assertFalse(source['merge_authorized'])  # Historical v5a authorization.
        migrated=json.loads((ROOT/'data/measurements/paper-v5b-2026-11-03/r20-migration.json').read_text())
        self.assertEqual([r['old'] for r in migrated],expected)
        self.assertEqual(len(migrated),26)
        self.assertEqual(self.off.r20_signatures(self.texts),[])
        self.assertEqual(self.off.r20_gaps(self.texts),[])
        for row in expected:
            line=r'\pending{'+row['body']+'} % R20: '+row['export']
            bad=dict(self.texts,**{row['file']:self.texts[row['file']]+'\n'+line})
            self.assertIn('v5a R20 deferred inventory',self.off.missing(bad))
        self.assertTrue((ROOT/'calc/out/run22/paper').is_dir())

    # Full consumer rows come from literal FACTS tables, with both memory
    # boundaries and normal priority retained; 5090 is never a server scenario.
    def test_consumer_rows_and_client_only_boundary_follow_facts(self):
        facts=(SOURCE/'FACTS.md').read_text()
        with (SOURCE/'consumer-gpu.csv').open(newline='') as stream:rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),17)
        for r in rows:
            values=' / '.join(r[k] for k in ('segment','delta512','delta2000','delta10000','decode'))
            self.assertIn(values,facts)
            phrase=' & '.join([r['model'],str(int(r['depth'])//1000)]+[r[k] for k in ('segment','delta512','delta2000','delta10000','decode')])+r' \\'
            self.assertIn(phrase,self.texts['05-clients.tex'])
        for bad in ('RTX 5090 рассматривается как сервер.','RTX 5090 рассматривается и как клиент, и как сервер.'):
            file,_,phrase=self.off.expected()['v5a consumer only']
            text=self.texts[file].replace(phrase,bad,1)
            self.assertNotEqual(text,self.texts[file]);self.assertIn('v5a consumer only',self.off.missing(dict(self.texts,**{file:text})))

    # Raw producer analyses supply every aggregate score/change/interval.
    # Non-significant McNemar and equal scores cannot become equivalence claims.
    def test_ruler_descriptives_and_preregistration_keep_distinct_endpoints(self):
        for name,scores,changes,pvalue,bounds in (
            ('qwen-32768',[97.44,97.44,97.18],[33,29],.618,[-4.02,6.05]),
            ('glimmer-8192',[87.91,89.13,89.08],[130,125],.383,[-2.69,5.21]),
        ):
            rows=json.loads((SOURCE/('ruler-'+name+'.json')).read_text());r=next(r for r in rows if r['task']=='ALL')
            self.assertEqual([round(100*r['score_means'][k],2) for k in ('local','offload','local_partition')],scores)
            self.assertEqual([r['offload_changed'],r['partition_changed']],changes)
            self.assertAlmostEqual(r['mcnemar_p'],pvalue,places=3)
            self.assertEqual([round(100*v,2) for v in r['excess_conservative95']],bounds)
            for score in scores:self.assertIn(f'{score:.2f}'+r'\%',self.texts['11-limitations.tex'])
        prereg=(SOURCE/'RULER-EQUIVALENCE-PREREGISTRATION.md').read_text()
        for literal in ('Primary endpoint: task score','±2 percentage points','observed before registration','Holm','10,000'):
            self.assertIn(literal,prereg)
        self.assertIn('Qwen на 8 и 32 тысячах наблюдались до регистрации.',self.texts['11-limitations.tex'])
        self.assertNotIn(r'\pending{первичный парный анализ оценок по зарегистрированному критерию.}',self.texts['11-limitations.tex'])
        self.assertIn('На 32 и 64 тысячах эквивалентность оценок установлена',self.texts['11-limitations.tex'])
        self.assertIn('Доля изменившихся текстов служит вторичным показателем;',self.texts['11-limitations.tex'])

    # The new checkpoint is measured, while heterogeneous exit5 never becomes
    # calibrated acceptance and unpersisted sequences cannot prove divergence.
    def test_fidelity_measured_but_uncalibrated_with_unpersisted_sequence_limit(self):
        text=self.texts['90-appendix.tex']
        for literal in ('Код выхода 5',r'$7.7296\cdot10^{-5}$',r'$1.7031\cdot10^{-4}$','0.2097','последовательности не сохранены','90.2 и не служит порогом'):
            self.assertIn(literal,text)
        self.assertAlmostEqual(7.7296e-5/8.5664e-7,90.2,places=1)
        bad=text.replace('без калиброванной приёмки.','с калиброванной приёмкой.')
        self.assertIn('v5a fidelity detail 0',self.off.missing(dict(self.texts,**{'90-appendix.tex':bad})))
        pending=' '.join(r['body'] for r in json.loads((ROOT/'calc/tests/data/paper-v5a2-pending.json').read_text()))
        self.assertNotIn('повторная проверка checkpoint 10',pending)
        self.assertNotIn('RULER 32 тысячи: запуск',pending)

    # Reciprocal-rate interpolation is recomputed from FACTS anchors. It is
    # an explicit mixed-format estimate, with no measured batching-gain claim.
    def test_prefill_profile_ratios_are_shown_estimates(self):
        record=json.loads((SOURCE/'prefill-ratios.json').read_text())
        def interp(points,d):
            a=max(k for k in points if k<=d);b=min(k for k in points if k>=d)
            return points[a] if a==b else 1/((b-d)/(b-a)/points[a]+(d-a)/(b-a)/points[b])
        for r in record['rows']:
            v=interp({100000:14667,249000:8673},r['depth']);l=interp({100000:1284,150000:1131,200000:1010},r['depth'])
            self.assertAlmostEqual(v/l,r['ratio'],places=10)
            self.assertTrue(10<=r['ratio']<11)
        self.assertAlmostEqual(23151/1663,13.92,places=2)
        self.assertIn('промежуточные отношения рассчитаны, отдельными замерами не являются.',self.texts['06-server.tex'])

    # Cache effective price includes the1.9% misses; commercial aggregate is
    # not a measured Chutes hit rate. A free-miss or provider-rate label fails.
    def test_cache_cost_and_admission_are_bounded_scenarios(self):
        self.assertAlmostEqual(.019*.039+.981*.0039,.0045669,places=10)
        text=self.texts['07-economics.tex']
        self.assertIn('Без повторного использования & 0'+r'\% & 0.039',text)
        self.assertIn(r'\label{tab:r24-api-points}',text)
        key='v5a cache owner aggregate';file,marker,phrase=self.off.expected()[key]
        bad=text.replace(phrase,'98.1'+r'\% измерено у Chutes.')
        self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))

    # New semantic sites reject an applied omission, independently of byte pins.
    # Each plant is checked against its own named verdict; coupled diagnostics remain.
    def test_every_new_semantic_site_has_an_applied_omission_control(self):
        for name,(file,marker,phrase) in self.off.v5a_expected().items():
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),'УДАЛЕНО',part,count=1)
            self.assertEqual(n,1,name)
            self.assertIn(name,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})))

    # Technology labels cannot survive in any typeset section; measured
    # rates/RTTs and the old numerical observations remain in their replacement.
    def test_link_labels_are_parameters_and_old_rates_are_retained(self):
        unreleased=current_changelog((ROOT/'CHANGELOG.md').read_text())
        all_text='\n'.join(self.texts.values())+'\n'+unreleased
        from test_paper_v5a2 import link_technology_hits
        self.assertEqual(link_technology_hits(self.texts,(ROOT/'CHANGELOG.md').read_text()),[])
        for number in ('16.0~МБ/с','110~мс','9.75~МБ/с','140.6~мс','5.19~МБ/с','125.8~мс','0.798','2.805','71.2','50.6'):
            self.assertIn(number,all_text)

    # The new six-note fixes do not erase an old test name or prior export.
    def test_r5u_notes_and_history_are_explicit(self):
        self.assertNotIn('Это в 4.8--5.2',self.texts['91-calculation-history.tex'])
        self.assertIn('Расчёт задаёт сценарии для команды',self.texts['01-introduction.tex'])
        self.assertIn('На одной GPU',self.texts['11-limitations.tex'])
        self.assertIn('73.8'+r'\%',self.texts['90-appendix.tex'])
        self.assertIn('прежнюю тарификацию API',self.texts['91-calculation-history.tex'])
        self.assertLessEqual(len(self.off.abstract_text(self.texts['00-abstract.tex'])),1920)

    # Abstract length includes the visible generic pending label. Cost/model
    # deferrals cannot masquerade as measured results or evade the arXiv limit.
    def test_abstract_counter_includes_rendered_pending_labels(self):
        self.assertIn(r'\newcommand{\pending}[1]{\textbf{Ожидается: #1}}',(ROOT/'paper/preamble.tex').read_text())
        sample=r'\begin{quote}\textbf{Аннотация.} A \pending{B} C\end{quote}'
        self.assertEqual(self.off.abstract_text(sample),'A Ожидается: B C')
        self.assertLessEqual(len(self.off.abstract_text(self.texts['00-abstract.tex'])),1920)
