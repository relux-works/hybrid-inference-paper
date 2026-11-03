#!/usr/bin/env python3
"""Reject missing letter/number and punctuation spaces in publication prose.

Markdown code spans/fences and link targets contain identifiers, not prose.
Known model, unit, revision and digest tokens are accepted as whole tokens;
accepting a technical substring never exempts an attached ordinary word.
Release-note sections are scanned separately using the release extractor's
section boundaries; --release-notes also checks an actual generated artifact.
"""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORD = re.compile(r'\w+', re.UNICODE)
GLUED = re.compile(r'[^\W\d_]\d|\d[^\W\d_]', re.UNICODE)
PUNCTUATION = re.compile(r'%[^\W\d_]\w*|[:,]\d+(?:\.\d+)?', re.UNICODE)
# Only whole numeric forms are exempt: times, ratios and grouped thousands.
# The final boundary prevents an attached prose word from gaining an exemption.
NUMERIC_FORM = re.compile(
    r'(?<![\w.,:])(?:\d+(?:\.\d+)?(?::\d+(?:\.\d+)?)+(?:Z)?|'
    r'\d{1,3}(?:,\d{3})+(?:\.\d+)?)(?!\w|[,:]\d|\.\d)')
TECHNICAL = re.compile(
    r'(?:[0-9a-f]{7,64}|[rRvV]\d+[a-z]?|(?:run|Run|RUN|step|Step)\d+|'
    r'[Mm]\d+|B\d+|H\d+|L\d+S|N\d+X|DS\d+|PRO\d+|Max(?:64|128)|Ultra(?:96|256)|'
    r'Qwen3|Q\d+(?:_K_M)?|[qQ]\d+_\d+|(?:bf|BF|fp|FP|f)\d+|p\d+|'
    r'\d+(?:k|M|B|G|GbE)|(?:SHA|sha)\d+(?:SUMS|sum)?|NVFP\d+|'
    r'x\d+|arm\d+|full\d+|Full\d+|tier\d+|calc\d+|top\d+)\Z')


def prose(text):
    # Keep line counts stable so a failure points at the original document.
    blank = lambda m: re.sub(r'[^\n]', ' ', m[0])
    text = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', blank, text, flags=re.M | re.S)
    text = re.sub(r'`[^`\n]*`', blank, text)
    text = re.sub(r'\]\([^\n)]*\)', blank, text)
    text = re.sub(r'https?://\S+', blank, text)
    return text


def violations(text):
    clean = prose(text)
    clean = NUMERIC_FORM.sub(lambda m: ' '*len(m[0]), clean)
    bad = [m for m in WORD.finditer(clean)
           if GLUED.search(m[0]) and not TECHNICAL.fullmatch(m[0])]
    bad.extend(PUNCTUATION.finditer(clean))
    return [(clean.count('\n', 0, m.start()) + 1, m[0])
            for m in sorted(bad, key=lambda m: m.start())]


def release_sections(changelog):
    """Same ## [version] boundary as release-check.sh, without a tag or git I/O."""
    pieces = re.split(r'^## \[([^\]]+)\][^\n]*\n', changelog, flags=re.M)
    return {pieces[i]: pieces[i+1] for i in range(1, len(pieces), 2)
            if pieces[i] != 'Unreleased'}


def check_documents(documents):
    return [(name, line, token) for name, text in documents.items()
            for line, token in violations(text)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-notes', type=Path)
    args = parser.parse_args()
    documents = {name: (ROOT/name).read_text() for name in ('CHANGELOG.md', 'README.md')}
    documents.update({'release notes ['+v+']': body
                      for v, body in release_sections(documents['CHANGELOG.md']).items()})
    if args.release_notes:
        documents[str(args.release_notes)] = args.release_notes.read_text()
    bad = check_documents(documents)
    for name, line, token in bad:
        kind = 'punctuation' if PUNCTUATION.search(token) else 'letter/number'
        print(f'{name}:{line}: missing {kind} space: {token}')
    print(f'publication spacing: {len(documents)} documents/sections; {len(bad)} violations')
    return bool(bad)


if __name__ == '__main__':
    raise SystemExit(main())
