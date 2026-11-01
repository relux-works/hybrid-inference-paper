"""Offline R10 audit: compare raw CSV records with the immutable R9 git baseline."""
import argparse
import csv
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASELINE = 'e9db8129887126ca6a5d27066dd4f4519d223c2d'
KEYS = {
    'person_cost': ('team', 'client', 'basis'),
    'remote_rent_buy': ('team', 'option', 'deployment', 'mode', 'share', 'hours', 'residual'),
    'glm_long_sessions': ('context', 'team'),
    'perimeter_cost': ('profile', 'team', 'route', 'client', 'basis', 'server'),
}


def records(data, name):
    """Retain exact header/record bytes, including quoting and line endings."""
    lines = data.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(data.decode('utf-8'), newline=''))
    columns = next(reader)
    header = b''.join(lines[:reader.line_num])
    previous = reader.line_num
    fields = next((v for k, v in KEYS.items() if name.startswith(k)), None)
    result = {}
    for index, values in enumerate(reader):
        if len(values) != len(columns):
            raise AssertionError('malformed record: ' + name)
        row = dict(zip(columns, values))
        key = tuple(row[k] for k in fields) if fields else (str(index),)
        if key in result:
            raise AssertionError('duplicate record key: ' + name)
        raw = b''.join(lines[previous:reader.line_num])
        previous = reader.line_num
        result[key] = (row, raw)
    return header, result


def compare(name, old, new):
    before_header, before = records(old, name)
    after_header, after = records(new, name)
    if before_header != after_header:
        raise AssertionError('header bytes changed: ' + name)
    removed = [k for k in before if k not in after]
    changed = [k for k in before if k in after and before[k][1] != after[k][1]]
    added = [k for k in after if k not in before]
    # Existing rows must also retain their relative order.
    reordered = [k for k in before if k in after] != [k for k in after if k in before]
    forbidden = [k for k in added if after[k][0].get('team') != '20']
    summary = dict(file=name, removed=len(removed), changed=len(changed),
                   added=len(added), reordered=reordered, forbidden_added=len(forbidden))
    additions = [(name, json.dumps(k), after[k][1].decode('utf-8')) for k in added]
    return summary, additions


def require_additions_only(summary):
    if any(summary[k] for k in ('removed', 'changed', 'reordered', 'forbidden_added')):
        raise AssertionError('existing-row byte identity / team-20-only contract: ' + json.dumps(summary))


def audit(directory, baseline=BASELINE):
    paths = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', baseline, 'calc/out/paper'], cwd=ROOT,
        text=True).splitlines()
    paths = [p for p in paths if p.endswith('.csv')]
    expected = {Path(p).name for p in paths}
    if {p.name for p in directory.glob('*.csv')} != expected:
        raise AssertionError('published CSV file set changed')
    summaries, additions = [], []
    for path in paths:
        old = subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT)
        summary, rows = compare(Path(path).name, old, (directory / Path(path).name).read_bytes())
        summaries.append(summary)
        additions.extend(rows)
    return summaries, additions


def audit_revision(revision):
    """Audit immutable historical publication after later engine runs supersede it."""
    import tempfile
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision,
                                     'calc/out/paper'], cwd=ROOT, text=True).splitlines()
    with tempfile.TemporaryDirectory() as directory:
        for path in paths:
            if path.endswith('.csv'):
                (Path(directory) / Path(path).name).write_bytes(subprocess.check_output(
                    ['git', 'show', revision + ':' + path], cwd=ROOT))
        return audit(Path(directory))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, help='Audit an explicit R10 export directory instead of immutable history')
    parser.add_argument('--revision', default='1e8f897c4f82092c632507b520515cefa7eecab5', help='Historical publication commit (default: signed R10)')
    parser.add_argument('--diff', type=Path)
    parser.add_argument('--added', type=Path)
    args = parser.parse_args()
    summaries, additions = audit(args.directory) if args.directory else audit_revision(args.revision)
    if args.diff:
        with args.diff.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(summaries[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(summaries)
    if args.added:
        with args.added.open('w', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(('file', 'row_key', 'row_csv'))
            writer.writerows(additions)
    for summary in summaries:
        print(json.dumps(summary, sort_keys=True))
    for summary in summaries:
        require_additions_only(summary)
    print('PASS: {} files; {} added rows; zero removed/changed rows'.format(len(summaries), len(additions)))


if __name__ == '__main__':
    main()
