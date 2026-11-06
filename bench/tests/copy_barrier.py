"""Test-only barrier after a real partial restream write; no production hooks."""
import contextlib
import os
from pathlib import Path
import runpy
import select
import sys
import tempfile


@contextlib.contextmanager
def barrier():
    ready_read, ready_write = os.pipe()
    block_read, block_write = os.pipe()
    try:
        yield dict(COPY_READY_FD=str(ready_write), COPY_BLOCK_FD=str(block_read)), (ready_write, block_read), ready_read, block_write
    finally:
        for fd in (ready_read, ready_write, block_read, block_write):
            os.close(fd)


def wait_for_copy(process, ready):
    # The writer cannot complete until released or signalled, regardless of CPU speed.
    assert select.select([ready], [], [], 30)[0], 'copy did not reach barrier'
    message = os.read(ready, 4096).decode().strip()
    assert message and process.poll() is None, 'copy exited before barrier'
    path = Path(message)
    assert path.is_file() and path.stat().st_size > 0, 'no actual partial-copy bytes'
    return path


def main():
    original = tempfile.NamedTemporaryFile
    def blocked_file(*args, **kwargs):
        out = original(*args, **kwargs)
        write = out.write
        waiting = False
        def blocked_write(data):
            nonlocal waiting
            n = write(data)
            if not waiting and out.tell() >= 16:
                waiting = True
                out.flush()
                os.write(int(os.environ['COPY_READY_FD']), (out.name+'\n').encode())
                assert os.read(int(os.environ['COPY_BLOCK_FD']), 1) == b'R', 'copy barrier not released'
            return n
        out.write = blocked_write
        return out
    tempfile.NamedTemporaryFile = blocked_file
    sys.argv = sys.argv[1:]
    runpy.run_path(sys.argv[0], run_name='__main__')


if __name__ == '__main__':
    main()
