"""Saved serial-prefix RULER and unavailable Qwen1M are descriptive, not admission."""
import hashlib,json,re,subprocess,unittest
from pathlib import Path
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d2-2026-11-05'
BASE='fcd44c26967c560b9ca3e179ab2e3d3c19509a19'

import history_evidence as history

class PaperV5d2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d2_off',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}
        cls.sites={'v5d2 '+r['name']:r for r in json.loads((ROOT/'data/measurements/paper-v5d4-2026-11-05/v5d2-sites-current.json').read_text())}
        # Finite complete64k successors retain exact current loci.
        for k,r in cls.sites.items():r.update(zip(('file','marker','phrase'),cls.off.expected()[k]))

    # A removed claim must fail its named checker, with clean prose as control.
    # This validates publication transcription, not hardware or endpoint replay.
    def test_new_sites_have_applied_named_omission_controls(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for k,r in self.sites.items():
            text=self.texts[r['file']];part=next(p for p in text.split('\n\n') if r['marker'] in p)
            bad,n=re.subn(r'\s+'.join(map(re.escape,r['phrase'].split())),lambda _:'УДАЛЕНО',part,count=1)
            self.assertEqual(n,1,k);self.assertNotEqual(bad,part,k)
            self.assertIn(k,self.off.missing(dict(self.texts,**{r['file']:text.replace(part,bad,1)})))

    # Rounded table values come from the independent accepted ALL-row JSON.
    # Serial prefixes cannot substitute for the planned390-example population.
    def test_interim_counts_intervals_and_percentages_match_saved_analysis(self):
        # Prove the old serial-prefix arithmetic in its labelled historical slice.
        text=self.texts['91-calculation-history.tex']
        table=next(p for p in text.split('\n\n') if r'\label{tab:ruler-interim-archive}' in p)
        self.assertIn('Сохранено пар из 390 & 368 & 225',table)
        for depth,n,correct in [(65536,368,364),(131072,225,225)]:
            a=next(r for r in json.loads((D/f'interim-{depth}.json').read_text())['analysis'] if r['task']=='ALL')
            self.assertEqual(a['n'],n);self.assertEqual(a['accuracy_pairs']['offload']['both_true'],correct)
            for key in ('offload','local_partition'):
                self.assertEqual(a['accuracy_pairs'][key]['mcnemar_p'],1)
                self.assertIn(f'{100*a["score_means"]["local"]:.2f}',table)
            for arm in ('offload','partition'):
                self.assertIn(f'{a[arm+"_changed"]} ({100*a[arm+"_rate"]:.2f}'+r'\%)',table)
                for value in a[arm+'_wilson95']:self.assertIn(f'{100*value:.2f}',text)
            for value in a['excess_conservative95']:self.assertIn(f'{100*value:+.2f}',table)
            self.assertIn(str(a['left_only'])+'/'+str(a['right_only']),table)
            self.assertFalse(a['equivalent_at_margin'])
        self.assertIn('0.5716',table);self.assertIn('364/368',table);self.assertIn('225/225',table)

    # The archived serial prefix stays nonrandom and never substitutes for the
    # completed analysis. Its former p1 entries are explicitly past-tense.
    def test_registered_analysis_is_not_filled_by_interim_prefixes(self):
        t=self.texts['91-calculation-history.tex']
        self.assertIn('полный сбор',self.texts['11-limitations.tex'])
        for phrase in ('без зарегистрированного вердикта','сохранённые строки не являются случайной подвыборкой','полный анализ заменяет этот снимок'):
            self.assertIn(phrase,t)
        self.assertIn('В прежнем первичном анализе обе глубины',t);self.assertIn('входили как ожидающие с $p=1$',t)
        self.assertIn('только ранние задачи поиска иголок',t)
        self.assertIn('22 примера',t);self.assertIn('165 примеров',t);self.assertIn(r'\texttt{vt/cwe/fwe/QA}',t)
        self.assertNotIn('результаты не собраны',t)
        self.assertEqual(history.unchanged(BASE,'data/measurements/paper-v5a2-2026-11-03','data/measurements/paper-v5a3-2026-11-03',allow_ports=True),'')

    # Resolved wait requires completed pairs, saved-prefix identity and host
    # custody; differing per-depth native builds remain explicitly disclosed.
    def test_pending_requires_full_pairs_and_frozen_runtime(self):
        t=self.texts['11-limitations.tex']
        self.assertIn('Получены 390/390 пар',t);self.assertNotIn('ждут 128 тысяч',t)
        self.assertIn('по решению владельца 2026-11-04',t)
        self.assertIn('узла B на узел A',t)
        self.assertIn('бинарные файлы и библиотеки с проверенными хэшами',t)
        self.assertIn('парность сохраняется внутри примера',t)
        self.assertIn('Проверка всего манифеста',t)
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        self.assertIn('Полные 390 пар на каждой из четырёх глубин Qwen',self.texts['90-appendix.tex'])

    # Availability, not cache fraction, admits an endpoint. Cost remains
    # unknown for Alibaba; all three rows are outside the admitted aggregate.
    def test_measured_qwen_million_is_excluded_by_unchanged_95_percent_rule(self):
        t=self.texts['08-million.tex'];table=next(p for p in t.split('\n\n') if r'\label{tab:qwen-million-measured-excluded}' in p)
        for row in ('Phala & 0.987 & 54.2087 & 0.875 & исключён','Novita & 0.731 & 421.536 & 0.452 & исключён','Alibaba & неизвестна & неизвестна & 0.846 & исключён'):
            self.assertIn(row,table)
        self.assertIn('не достигли правила доступности 95',t)
        self.assertIn('в минимум и медиану допущенных поставщиков эти строки не входят',t)
        self.assertIn('новые наблюдения их набор не расширяют',t)
        for value in (.875,.452,.846):self.assertLess(value,.95)
        self.assertGreater(.987,.95)
        for f in ('07-economics.tex','08-million.tex'):
            self.assertNotIn('ожидает прогона 24',self.texts[f])
        self.assertTrue((ROOT/'calc/out/run24').exists());self.assertEqual(history.unchanged('ca7f228acd789380bf46016fd87acc33e1b07aef','calc/out/run24','calc/run24',allow_ports=True),'')
        self.assertEqual(history.unchanged(BASE,'calc/out/run23','calc/hybridcalc','calc/run23',allow_ports=True),'')

    # Naming an existing private repository does not claim a public snapshot.
    def test_private_repository_snapshot_follows_rc4(self):
        t=self.texts['90-appendix.tex']
        self.assertIn('https://github.com/relux-works/hybrid-inference-data',t)
        self.assertIn('существующем закрытом репозитории',t)
        self.assertIn('будет размещён после RC4',t)
        self.assertIn('сейчас этот снимок ещё не опубликован',t)

    # Source copies and successor contracts have explicit SHA custody;
    # predecessor evidence is protected independently by source-retention audit.
    def test_new_source_files_have_sha_custody(self):
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
        report=(D/'RULER-INTERIM.md').read_text()
        for phrase in ('368','225','qa_2','fe2195aa'):self.assertIn(phrase,report)
