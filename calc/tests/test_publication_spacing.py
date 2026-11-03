"""Finite positive/negative witnesses for the publication spacing contract."""
from pathlib import Path
import unittest
from r13_audit import module, ROOT

spacing = module('publication_spacing_guard', ROOT/'.scripts/publication_spacing.py')


class PublicationSpacingTests(unittest.TestCase):
    # Punctuation plants fail through the real release-note CLI with the named
    # reason and no file mutation; each repaired counterpart passes.
    def test_punctuation_glue_cli_plants_and_clean_control(self):
        import subprocess
        import sys
        import tempfile
        legitimate = '10:12Z 10:12:34Z 1:1 1.5:2.5 v1.2.3 0.1.0-rc.2 8,301 12,345,678.90'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'release-notes.md'
            for name, plant, repaired in (
                ('percent_letter_33_is', '33%is', '33% is'),
                ('comma_digit_treatment', 'treatment,4/48', 'treatment, 4/48'),
                ('colon_digit_modelled', 'modelled:77.7%', 'modelled: 77.7%'),
                ('percent_colon_digit', 'at 50%:0.01558', 'at 50%: 0.01558'),
                ('comma_list', 'counts 1,2', 'counts 1, 2'),
                ('percent_cyrillic', '33%вызовов', '33% вызовов'),
            ):
                with self.subTest(named_negative_plant=name):
                    path.write_text(legitimate+' '+plant+'\n')
                    original = path.read_bytes()
                    bad = subprocess.run([sys.executable, '-B', str(ROOT/'.scripts/publication_spacing.py'),
                                          '--release-notes', str(path)], capture_output=True, text=True)
                    self.assertEqual(bad.returncode, 1, bad.stdout+bad.stderr)
                    self.assertIn(str(path)+':1: missing punctuation space:', bad.stdout)
                    self.assertEqual(path.read_bytes(), original)
                    path.write_text(legitimate+' '+repaired+'\n')
                    clean = subprocess.run([sys.executable, '-B', str(ROOT/'.scripts/publication_spacing.py'),
                                            '--release-notes', str(path)], capture_output=True, text=True)
                    self.assertEqual(clean.returncode, 0, clean.stdout+clean.stderr)
                    print(f'named negative plant {name}: exit 1; clean control: exit 0')

    # Numeric punctuation is exempt only as a whole form; a time, ratio or
    # thousands separator cannot hide prose glued to its final digit.
    def test_legitimate_punctuation_and_attached_word_boundary(self):
        self.assertEqual(spacing.violations('10:12Z 1:1 v1.2.3 8,301'), [])
        for plant in ('10:12Zshows', '1:1gain', '8,301calls'):
            with self.subTest(plant=plant):
                self.assertTrue(spacing.violations(plant))

    # Named plants must fail in each publication surface while the nearby
    # spaced controls and whole technical identifiers remain accepted.
    def test_glued_letter_number_plant_and_clean_control(self):
        clean = 'M3 B300 Q4_K_M r5k 8k 32k 27B BF16 Q8_0 p90 run14 SHA256SUMS'
        self.assertEqual(spacing.violations(clean), [])
        for document in ('CHANGELOG.md', 'README.md', 'release-notes.md'):
            for plant, repaired in (
                ('from2.6', 'from 2.6'), ('2.4times', '2.4 times'),
                ('gain1.57', 'gain 1.57'), ('Ultra25.9', 'Ultra 25.9'),
                ('36.6is', '36.6 is'), ('all110run14', 'all 110 run14'),
                ('0.0061Q4and64', '0.0061 Q4 and 64'), ('число16', 'число 16'),
            ):
                with self.subTest(document=document, named_negative_plant=plant):
                    self.assertTrue(spacing.check_documents({document: clean+' '+plant}))
                    self.assertEqual(spacing.check_documents({document: clean+' '+repaired}), [])

    # A valid model substring cannot hide an attached word or an extra count.
    def test_technical_substring_does_not_exempt_glued_prose(self):
        for plant in ('B300shows', 'Q4and64', '8kcalls', 'M3gain1'):
            with self.subTest(plant=plant):
                self.assertTrue(spacing.violations(plant))
        self.assertEqual(spacing.violations('B300 shows Q4 and 64 8k calls M3 gain 1'), [])

    # Release-note extraction checks the same section text, including older
    # releases; a clean README cannot mask a broken generated artifact.
    def test_release_note_sections_and_actual_artifact_are_guarded(self):
        source = '## [Unreleased]\nnew\n## [0.1.0-rc.2] - date\nfrom2.6\n## [0.1.0-rc.1]\nM3\n'
        sections = spacing.release_sections(source)
        self.assertEqual(set(sections), {'0.1.0-rc.2', '0.1.0-rc.1'})
        self.assertTrue(spacing.violations(sections['0.1.0-rc.2']))
        self.assertFalse(spacing.violations(sections['0.1.0-rc.1']))

    # The rc.3 release permits exactly one supersession notice in the rc.2
    # section; all earlier text remains identical apart from whitespace repairs.
    def test_rc2_changelog_repairs_change_only_whitespace(self):
        import hashlib
        payload = (ROOT/'calc/tests/data/paper-v3-rc2-changelog.md').read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
                         '3c090703c0bae3403eb8371f24cd6329985f2d3abcaa909c4d0b07b364822657')
        original = payload.decode()
        before = spacing.release_sections(original)['0.1.0-rc.2']
        after = spacing.release_sections((ROOT/'CHANGELOG.md').read_text())['0.1.0-rc.2']
        notice = 'Prepared but not published as a GitHub release; rc.3 supersedes this candidate.'
        self.assertEqual(after.count(notice), 1)
        historical = after.replace(notice, '', 1)
        self.assertEqual(''.join(before.split()), ''.join(historical.split()))
        self.assertFalse(spacing.violations(after))

    # Real publication documents and every release-note section use the same
    # guard as generated notes; fixture examples alone cannot satisfy the gate.
    def test_existing_publication_documents_are_clean(self):
        documents = {n: (ROOT/n).read_text() for n in ('CHANGELOG.md', 'README.md')}
        documents.update(spacing.release_sections(documents['CHANGELOG.md']))
        self.assertEqual(spacing.check_documents(documents), [])

    # The real CLI rejects a broken generated release-note file with exit 1
    # and the named reason; repairing that same file restores exit 0.
    def test_actual_release_note_cli_plant_and_clean_control(self):
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'release-notes.md'
            path.write_text('M3 B300 Q4_K_M r5k 8k from2.6\n')
            bad = subprocess.run([sys.executable, '-B', str(ROOT/'.scripts/publication_spacing.py'),
                                  '--release-notes', str(path)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1, bad.stdout+bad.stderr)
            self.assertIn('missing letter/number space: from2', bad.stdout)
            self.assertEqual(path.read_text(), 'M3 B300 Q4_K_M r5k 8k from2.6\n')
            path.write_text('M3 B300 Q4_K_M r5k 8k from 2.6\n')
            clean = subprocess.run([sys.executable, '-B', str(ROOT/'.scripts/publication_spacing.py'),
                                    '--release-notes', str(path)], capture_output=True, text=True)
            self.assertEqual(clean.returncode, 0, clean.stdout+clean.stderr)
            print('named negative plant generated_release_notes_from2: exit 1; clean control: exit 0')
