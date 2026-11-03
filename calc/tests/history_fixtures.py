"""Verified, content-addressed snapshots; commit IDs are provenance, never lookups."""
import hashlib
import json
from pathlib import Path, PurePosixPath

STORE = Path(__file__).resolve().parent / 'data/history-fixtures'
MANIFEST_SHA256 = '7ab60d3062219d2cf7c257ebb2455f2f4be6b4769f50812feea52c6306154aff'


def manifest(store=None):
    store = Path(store) if store is not None else STORE
    payload = (store / 'manifest.json').read_bytes()
    assert hashlib.sha256(payload).hexdigest() == MANIFEST_SHA256, 'fixture manifest hash mismatch'
    return json.loads(payload)['snapshots']


def snapshot_files(snapshot, prefix='', store=None):
    """Read and verify every selected byte before making it available to a check."""
    store = Path(store) if store is not None else STORE
    snapshots = manifest(store)
    assert snapshot in snapshots, 'unknown historical fixture: ' + snapshot
    result = {}
    for name, entry in snapshots[snapshot]['files'].items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts, 'unsafe fixture path: ' + name
        if prefix and name != prefix and not name.startswith(prefix.rstrip('/') + '/'):
            continue
        digest = entry['sha256']
        assert len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), 'invalid fixture digest'
        data = (store / 'sha256' / digest).read_bytes()
        assert len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == digest, 'fixture hash mismatch: ' + name
        result[name] = data
    assert result, 'empty historical fixture selection: ' + snapshot + ' ' + prefix
    return result


def snapshot_read(snapshot, name, store=None):
    return snapshot_files(snapshot, name, store)[name]


def extract_snapshot(snapshot, destination):
    # Verify all bytes first: a corrupt snapshot must never leave a partial extraction.
    files = snapshot_files(snapshot)
    for name, data in files.items():
        path = Path(destination) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def verify_store(store=None):
    store = Path(store) if store is not None else STORE
    snapshots = manifest(store)
    expected = {entry['sha256'] for snapshot in snapshots.values() for entry in snapshot['files'].values()}
    assert expected == {p.name for p in (store / 'sha256').iterdir() if p.is_file()}, 'fixture object set mismatch'
    for name in snapshots:
        snapshot_files(name, store=store)
    return len(snapshots), len(expected)


if __name__ == '__main__':
    print('verified historical snapshots / objects:', *verify_store())
