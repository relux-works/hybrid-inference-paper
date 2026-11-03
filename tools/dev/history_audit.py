"""DEV ONLY: optional local-author-history audit, outside release acceptance.

Run: python3 tools/dev/history_audit.py --repo /path/to/author/checkout
Requires the private original objects; never fetches them. Public acceptance
uses the immutable fixtures instead. The release suite also exercises this
transport guard against self-created throwaway repositories only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'calc/tests'))
from r10_controls import HISTORY, ROOT, git_blob_id

# Historical reads stay local: in a partial clone git would otherwise fetch missing objects from its promisor remote.
# GIT_NO_LAZY_FETCH stops the lazy fetch, and an empty GIT_ALLOW_PROTOCOL refuses every transport if one is tried.
LOCAL_GIT_ENV = dict(GIT_NO_LAZY_FETCH='1', GIT_ALLOW_PROTOCOL='', GIT_TERMINAL_PROMPT='0')


def local_git(args, repo=None, check=True, text=False, data=None):
    assert repo is not None, 'dev history audit requires an explicit repository'
    result = subprocess.run(['git'] + args, cwd=repo, env=dict(os.environ, **LOCAL_GIT_ENV), input=data,
                            capture_output=True, text=text)
    if check and result.returncode:
        raise subprocess.CalledProcessError(result.returncode, ['git'] + args, result.stdout, result.stderr)
    return result


def history_present(revision, repo=None):
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


def revision_csv(revision, source='auto', archive=None, record=None, repo=None):
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



def main():
    from history_fixtures import manifest, snapshot_files
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    args = parser.parse_args()
    for label in ('r9-paper', 'r10-paper'):
        revision = manifest()[label]['original_commit']
        assert history_present(revision, args.repo), 'missing dev-only local history: ' + revision
        stored = {Path(p).name: data for p, data in snapshot_files(label, 'calc/out/paper').items() if p.endswith('.csv')}
        paths = local_git(['ls-tree', '-r', '--name-only', revision, 'calc/out/paper'], args.repo, text=True).stdout.splitlines()
        actual = {Path(p).name: local_git(['show', revision + ':' + p], args.repo).stdout for p in paths if p.endswith('.csv')}
        assert actual == stored, label + ' differs from author history'
        print(label, len(actual), 'exact CSVs')


if __name__ == '__main__':
    main()
