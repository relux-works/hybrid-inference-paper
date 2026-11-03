"""Offline R10 audit: compare raw CSV records with the immutable R9 baseline."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASELINE = 'e9db8129887126ca6a5d27066dd4f4519d223c2d'
# The public repository starts from one publication commit, so these historical commits exist only in the authors'
# history. Their paper CSVs are kept here, recorded by git blob id and SHA-256.
HISTORY = ROOT / 'calc/tests/data/history'
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


def git_blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


# Historical reads stay local: in a partial clone git would otherwise fetch missing objects from its promisor remote.
# GIT_NO_LAZY_FETCH stops the lazy fetch, and an empty GIT_ALLOW_PROTOCOL refuses every transport if one is tried.
LOCAL_GIT_ENV = dict(GIT_NO_LAZY_FETCH='1', GIT_ALLOW_PROTOCOL='', GIT_TERMINAL_PROMPT='0')


def local_git(args, repo=ROOT, check=True, text=False, data=None):
    result = subprocess.run(['git'] + args, cwd=repo, env=dict(os.environ, **LOCAL_GIT_ENV), input=data,
                            capture_output=True, text=text)
    if check and result.returncode:
        raise subprocess.CalledProcessError(result.returncode, ['git'] + args, result.stdout, result.stderr)
    return result


def history_present(revision, repo=ROOT):
    """True only when the commit, its tree and every paper CSV blob are already in the local object store."""
    if local_git(['cat-file', '-e', revision + '^{commit}'], repo, check=False).returncode:
        return False
    listing = local_git(['ls-tree', '-r', revision, 'calc/out/paper'], repo, check=False, text=True)
    if listing.returncode:
        return False
    blobs = [meta.split()[2] for meta, _, path in (line.partition('\t') for line in listing.stdout.splitlines())
             if path.endswith('.csv') and meta.split()[1] == 'blob']
    if not blobs:
        return False
    check = local_git(['cat-file', '--batch-check'], repo, check=False, text=True, data='\n'.join(blobs) + '\n')
    return check.returncode == 0 and not any(line.endswith(' missing') for line in check.stdout.splitlines())


def revision_csv(revision, source='auto', archive=None, record=None, repo=ROOT):
    """Paper CSV bytes of a historical publication, by file name. They come from local git when the commit and all its
    paper CSV blobs are present (source 'auto' or 'git'), otherwise from the archived copy; nothing is ever fetched,
    and either way every file must match the record."""
    recorded = json.loads(Path(record or HISTORY / 'paper-csv-history.json').read_text())
    if revision not in recorded:
        raise AssertionError('no recorded history for revision ' + revision)
    expected = recorded[revision]['files']
    present = history_present(revision, repo)
    if source == 'git' and not present:
        raise AssertionError('historical commit is not fully present in local git: ' + revision)
    files = {}
    if source == 'git' or (source == 'auto' and present):
        paths = local_git(['ls-tree', '-r', '--name-only', revision, 'calc/out/paper'], repo, text=True).stdout
        for path in paths.splitlines():
            if path.endswith('.csv'):
                files[Path(path).name] = local_git(['show', revision + ':' + path], repo).stdout
    else:
        with tarfile.open(archive or HISTORY / 'paper-csv-history.tar.gz') as stored:
            for member in stored.getmembers():
                folder, _, name = member.name.partition('/')
                if folder == revision:
                    if not member.isfile() or '/' in name or name in files:
                        raise AssertionError('unexpected archive member: ' + member.name)
                    files[name] = stored.extractfile(member).read()
    if set(files) != set(expected):
        raise AssertionError('historical CSV file set differs from the record: ' + revision)
    for name, data in files.items():
        want = expected[name]
        if (git_blob_id(data), hashlib.sha256(data).hexdigest(), len(data)) != (want['git_blob'], want['sha256'], want['bytes']):
            raise AssertionError('historical CSV bytes differ from the record: ' + revision + ' ' + name)
    return files


def audit(directory, baseline=BASELINE):
    old_files = revision_csv(baseline)
    if {p.name for p in directory.glob('*.csv')} != set(old_files):
        raise AssertionError('published CSV file set changed')
    summaries, additions = [], []
    for name in sorted(old_files):
        summary, rows = compare(name, old_files[name], (directory / name).read_bytes())
        summaries.append(summary)
        additions.extend(rows)
    return summaries, additions


def audit_revision(revision):
    """Audit immutable historical publication after later engine runs supersede it."""
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        for name, data in revision_csv(revision).items():
            (Path(directory) / name).write_bytes(data)
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
