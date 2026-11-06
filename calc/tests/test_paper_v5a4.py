"""Owner v5a4 publication contracts; CPU-readable accepted receipts only."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from r13_audit import ROOT,module

SOURCE=ROOT/'data/measurements/paper-v5a4-2026-11-03'
BASE='b543c026b859850bbd53b2af352b9a3514ff1539'


import history_evidence as history

class PaperV5a4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5a4_guard',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # Omission at each added finite site must lose that named verdict. The full
    # checker self-test separately proves single-digit mutation attribution.
    def test_owner_sites_have_applied_named_omission_controls(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for name,(file,marker,phrase) in self.off.v5a4_expected().items():
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),lambda _:'УДАЛЕНО',part,count=1)
            self.assertEqual(n,1,name)
            self.assertIn(name,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})))

    # Original26 hooks remain in the accepted baseline and migration evidence;
    # the current article has accepted successors, never inactive pending bodies.
    def test_deferred_economic_sites_keep_raw_custody_and_one_visible_notice(self):
        base={f:history.snapshot_object(BASE+':paper/sections/'+f).decode() for f in self.texts}
        original=self.off.r20_signatures(base)
        mapping=json.loads((ROOT/'data/measurements/paper-v5b-2026-11-03/r20-migration.json').read_text())
        self.assertEqual(len(original),26);self.assertEqual([r['old'] for r in mapping],original)
        self.assertEqual(self.off.r20_signatures(self.texts),[])
        self.assertEqual(self.off.r20_gaps(self.texts),[])
        self.assertEqual('\n'.join(self.texts.values()).count('Кому подходит схема.'),1)
        self.assertIn('Границы применимости.',self.texts['14-conclusion.tex'])
        key='00-abstract.tex';old=original[0]
        bad=dict(self.texts,**{key:self.texts[key]+'\n'+r'\pending{размеры} % R20: '+old['export']})
        self.assertIn('v5a R20 deferred inventory',self.off.missing(bad))
        self.assertIn('v4b pending inventory',self.off.missing(bad))

    # Abstracts have separate publication budgets; hidden source hooks must not
    # inflate rendered counts. KL-neutral observation cannot become lossless.
    def test_abstract_budgets_rounding_and_empirical_kl_boundary(self):
        text=self.texts['00-abstract.tex'];plain=self.off.abstract_text(text)
        self.assertLessEqual(len(plain),1920)
        english=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLessEqual(len(english),1800)
        # The analyst removes laboratory numbers from both abstracts; retain their body evidence.
        for x in ('-0.000298','-0.001076','+0.000390','1/180','7.905'):self.assertIn(x,self.texts['11-limitations.tex'])
        self.assertIn('без измеримого эффекта на KL',plain);self.assertIn('no measurable KL effect',english)
        self.assertAlmostEqual(.000298/.054253,.0055,places=4)
        self.assertAlmostEqual(.054253/.000298,180,delta=3)
        self.assertNotIn('без потерь',plain)
        bad=dict(self.texts,**{'00-abstract.tex':text.replace('bf16 округляет','bf16 передаёт без потерь',1)})
        self.assertIn('v5a3 abstract bf16',self.off.missing(bad))
        for word in ('PRI','код выхода','инструментирован'):self.assertNotIn(word,plain)
        huge=dict(self.texts,**{'00-abstract.tex':text.replace(r'\end{quote}','Я '*1000+r'\end{quote}')})
        self.assertIn('v4b abstract arXiv length',self.off.missing(huge))

    # The 1M main section contains measurements, not run14 price conclusions;
    # every historical paragraph except the superseded Mac wait remains in C.
    def test_million_archive_custody_and_warm_restore_download_arithmetic(self):
        main=self.texts['08-million.tex'];archived=self.texts['91-calculation-history.tex']
        old=history.snapshot_object(BASE+':paper/sections/08-million.tex').decode()
        for paragraph in old.split('\n\n'):
            if not paragraph.strip() or any(x in paragraph for x in (r'\section{', 'Для Qwen за пределами',r'\textbf{Измеренное восстановление на сервере.}')):continue
            self.assertIn(' '.join(paragraph.split()),' '.join(archived.split()))
        self.assertNotIn('2.6--2.7',main);self.assertIn('2.6--2.7',archived)
        # Current excluded-provider price is measured; archived gains stay outside the section.
        self.assertIn('421.54',main);self.assertNotIn('2.6--2.7 раза дешевле',main)
        self.assertIn('Прямой замер Mac.',main)
        self.assertNotIn(r'\pending{импорт, проверка логитов, генерация и добавочный prefill Mac',main)
        for numerator,denominator,result in ((36394654776,3.14*1e9,11.6),(18425185848,1026.042*1e6,17.96),(36394654776,1365.377*1e6,26.66),(54819840624,2391.419*1e6,22.92)):
            self.assertAlmostEqual(numerator/denominator,result,places=1 if result==11.6 else 2)
        self.assertAlmostEqual(2391.419/60,39.9,places=1)
        for old,new,key in [('Тёплое восстановление','Холодное восстановление','v5a2 server rebuild'),('полезной скорости','скорости провода','v5a4 download useful throughput')]:
            file,marker,_=self.off.expected()[key];source=self.texts[file]
            part=next(p for p in source.split('\n\n') if marker in p)
            self.assertIn(old,part);bad=source.replace(part,part.replace(old,new,1),1);self.assertNotEqual(bad,source)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))

    # RTX5090 comparisons use actual M3 PRI31 anchors; full-depth single-stream
    # fit is not a two-stream 260k result. M4 estimate leaves the client table.
    def test_consumer_boundary_and_m4_estimate_scope(self):
        text=self.texts['05-clients.tex'];facts=(SOURCE/'FACTS-rtx5090.md').read_text()
        for a,b,ratio in ((65.68,14.99,4.38),(57.95,13.52,4.29),(48.64,10.36,4.69),(41.66,8.99,4.63),(36.43,7.82,4.66),(32.42,6.93,4.68)):
            self.assertIn(str(a),facts);self.assertAlmostEqual(a/b,ratio,places=2)
            self.assertIn(f'{a:.2f}/{b:.2f}={ratio:.2f}',text)
        self.assertAlmostEqual(59.7/2.6,23,places=1)
        self.assertNotIn('M4 Max 128 ГБ &',text)
        self.assertIn('M4 Max 128 ГБ & 19.5 & 8.38',self.texts['91-calculation-history.tex'])
        key='v5a4 RTX5090 boundary';bad=text.replace('на 260 тысячах только один','на 260 тысячах два',1)
        self.assertIn(key,self.off.missing(dict(self.texts,**{'05-clients.tex':bad})))
        self.assertIn('с незаписанным приоритетом к M3 Max при обычном приоритете',self.texts['91-calculation-history.tex'])

    # Completed bf16 depths and exploratory Glimmer32 cannot remain queued;
    # measured text variation cannot imply bit identity or deeper equivalence.
    def test_completed_bf16_and_glimmer_scope(self):
        text=self.texts['11-limitations.tex']
        for x in ('28 случаях против 34','33 против 33','87.26 / 87.12 / 87.18','111/390','114/390','[-4.37,+2.86]','остановлена на 32 тысячах'):self.assertIn(x,text)
        self.assertIn('Glimmer stops at 32k',(SOURCE/'FACTS-glimmer32.md').read_text())
        inventory=json.loads((ROOT/'calc/tests/data/paper-v5a4-pending.json').read_text())
        for item in inventory:self.assertNotRegex(item['body'],r'RULER.*(?:bf16|Glimmer)')
        key='v5a4 Glimmer32 exploratory'
        # Scope the negative plant to the newly measured Glimmer32 paragraph.
        marker=self.off.expected()[key][1];part=next(p for p in text.split('\n\n') if marker in p)
        changed=part.replace('эквивалентность текста при границе 2 п.п. не установлена.','эквивалентность текста при границе 2 п.п. установлена.',1)
        self.assertNotEqual(changed,part);self.assertIn(key,self.off.missing(dict(self.texts,**{'11-limitations.tex':text.replace(part,changed,1)})))

    # The earlier16k series remains historical evidence; accepted kit1.6.11
    # adds four depths, without promoting out-of-surface points to measurements.
    def test_measured_server_batching_has_finite_depth_boundary(self):
        text=self.texts['90-appendix.tex'];facts=(SOURCE/'FACTS-server-decode16k.md').read_text()
        self.assertAlmostEqual(738.10/48.72,15.15,places=2)
        self.assertIn('39',facts);self.assertIn('15.15',facts)
        for x in ('собственные 16'+r'\,384','медиана трёх повторов','комплект 1.6.11 считает точные идентификаторы токенов'):self.assertIn(x,text)
        old='комплект 1.6.11 считает точные идентификаторы токенов';bad=text.replace(old,'комплект 1.6.11 не считает токены',1)
        self.assertNotEqual(bad,text)
        self.assertIn('v5a4 vLLM deeper scope',self.off.missing(dict(self.texts,**{'90-appendix.tex':bad})))

    # Local source archive and current semantic views have explicit SHA custody;
    # accepted original exports and reviewer tests are checked separately.
    def test_v5a4_evidence_identity_and_readability(self):
        readme=(SOURCE/'README.md').read_text()
        for p in SOURCE.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
        for name in ('11-limitations.tex','14-conclusion.tex'):
            text=self.off.rendered_tex(self.texts[name])
            for word in ('PRI~31','Код выхода 5','код 5','хэширование свидетельств','Синхронные снимки узла'):self.assertNotIn(word,text)
        self.assertIn('хэширование свидетельств',self.texts['90-appendix.tex'])
