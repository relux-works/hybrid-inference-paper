#!/usr/bin/env python3
"""Real c21284cd CPU integration check (no build, downloads or GPU).

Run: python3 bench/tests/check_restream_cpu.py --server PATH --model PATH --out DIR
Outputs HTTP evidence, server logs, owned PIDs and result.json under DIR.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--server', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('kitlib', Path(__file__).resolve().parents[1]/'mac/scripts/kitlib.py')
    kitlib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kitlib)
    evidence = []
    # Local connections bypass proxy environment variables; the check makes no external requests.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def disk():
        free = shutil.disk_usage(args.out).free
        if free < 25 * 1024**3:
            raise RuntimeError('less than 25 GiB free; stopping CPU check')
    def http(port, path, body=None, expected=200):
        disk()
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request('http://127.0.0.1:%d%s' % (port, path), data,
                                         {'Content-Type': 'application/json'})
        try:
            with opener.open(request, timeout=600) as r:
                status, result = r.status, json.load(r)
        except urllib.error.HTTPError as e:
            status, result = e.code, json.load(e)
        evidence.append(dict(path=path, body=body, status=status, result=result))
        (args.out/'http.json').write_text(json.dumps(evidence, indent=2))
        assert status == expected, (path, status, result)
        return result
    processes = []
    def start(np):
        disk()
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        command = [str(args.server.resolve()), '-m', str(args.model.resolve()), '--host', '127.0.0.1',
                   '--port', str(port), '-ngl', '0', '-t', '2', '-tb', '2', '-c', str(8192*np),
                   '-np', str(np), '--no-kv-unified', '-fa', 'on', '-ctk', 'q8_0', '-ctv', 'q8_0',
                   '--slot-save-path', str(args.out.resolve()), '--no-warmup', '-lv', '4', '--offline']
        log = (args.out/('server-np%d.log' % np)).open('w')
        p = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        log.close()
        processes.append(p)
        with (args.out/'processes.jsonl').open('a') as f:
            f.write(json.dumps(dict(pid=p.pid, command=command))+'\n')
        for _ in range(180):
            disk()
            assert p.poll() is None, 'server exited during startup'
            try:
                with opener.open('http://127.0.0.1:%d/health' % port, timeout=1) as r:
                    if r.status == 200:
                        return p, port
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(1)
        raise RuntimeError('server startup timeout')
    def stop(p):
        if p.poll() is None:
            p.terminate()  # exact PID of our Popen child
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        with (args.out/'processes.jsonl').open('a') as f:
            f.write(json.dumps(dict(stopped_pid=p.pid, exit=p.returncode))+'\n')
    def complete(port, slot, prompt, count):
        return http(port, '/completion', dict(id_slot=slot, prompt=prompt, n_predict=count,
                    temperature=0, seed=42, cache_prompt=True, ignore_eos=True, return_tokens=True))
    try:
        p, one = start(1)
        # Claim: the test model actually has both dense attention and recurrent state;
        # merely testing a transformer-only model cannot qualify this parser.
        log = (args.out/'server-np1.log').read_text()
        assert 'general.architecture' in log and 'qwen35' in log.lower(), 'not the requested Qwen3.5 model'
        assert 'llama_memory_recurrent' in log, 'model has no observed recurrent cache'
        tokens = http(one, '/tokenize', dict(content='The river flows past the old stone bridge. ', add_special=False))['tokens']
        prompt = (tokens * (3072//len(tokens)+1))[:3072]
        complete(one, 0, prompt, 1)
        saved = http(one, '/slots/0?action=save', dict(filename='original.bin'))
        count = saved['n_saved']
        assert count == len(prompt), (count, len(prompt))
        original = args.out/'original.bin'
        original_sha = kitlib.sha256_file(original)
        with original.open('rb') as f:
            parsed = kitlib.parse_slot(f)
        # Server tokens.serialize() packs a versioned header/padding into the
        # sequence file's token words; HTTP n_saved is the logical token count.
        assert parsed['streams'] == 1 and parsed['counts'] == [count]
        # Claim: continuation from its own restored single-stream state is the
        # positive reference for the identical prompt/sampling after restreaming.
        restored_one = http(one, '/slots/0?action=restore', dict(filename='original.bin'))
        assert restored_one['n_restored'] == count
        suffix = http(one, '/tokenize', dict(content=' Describe the river in one sentence:', add_special=False))['tokens']
        reference = complete(one, 0, prompt+suffix, 16)
        stop(p)
        kitlib.restream_slot(str(original), str(args.out/'restreamed.bin'), 4)
        p, four = start(4)
        # Claim: the ORIGINAL fails at the real n_stream guard (HTTP 400 AND named
        # server diagnostic); an unrelated restore/setup failure is insufficient.
        rejected = http(four, '/slots/2?action=restore', dict(filename='original.bin'), expected=400)
        assert 'Unable to restore slot' in json.dumps(rejected)
        assert 'n_stream mismatch' in (args.out/'server-np4.log').read_text()
        # Claim: slot 2 accepts the expanded file and reports exactly the saved
        # token count. Greedy decoded token IDs AND content equal the np=1 control.
        restored_four = http(four, '/slots/2?action=restore', dict(filename='restreamed.bin'))
        assert restored_four['n_restored'] == count
        actual = complete(four, 2, prompt+suffix, 16)
        assert actual['tokens_predicted'] == reference['tokens_predicted'] == 16
        assert actual['tokens'] == reference['tokens'] and len(actual['tokens']) == 16
        assert actual['content'] == reference['content']
        assert kitlib.sha256_file(original) == original_sha
        # A full reread would evade the recurrent restore claim; require reuse on
        # both sides (at most suffix + the final restored token was reevaluated).
        for result in (reference, actual):
            assert result['timings']['prompt_n'] <= len(suffix)+1, result['timings']
        summary = dict(commit='c21284cdf5fd833b90ac1f824cdf8065e2700dc4', model=str(args.model),
                       model_sha256=kitlib.sha256_file(args.model), saved_tokens=count,
                       header_token_words=parsed['token_words'],
                       restored_np1=restored_one['n_restored'], original_np4_http=400,
                       original_np4_diagnostic='n_stream mismatch', restored_np4_slot=2,
                       restored_np4_tokens=restored_four['n_restored'], greedy_equal=True,
                       continuation_tokens=actual['tokens'], continuation=actual['content'],
                       prompt_n_np1=reference['timings']['prompt_n'], prompt_n_np4=actual['timings']['prompt_n'],
                       original_sha256=original_sha, restreamed_sha256=kitlib.sha256_file(args.out/'restreamed.bin'),
                       original_bytes=original.stat().st_size, restreamed_bytes=(args.out/'restreamed.bin').stat().st_size,
                       model_has_recurrent_layers=True)
        (args.out/'result.json').write_text(json.dumps(summary, indent=2)+'\n')
        print(json.dumps(summary, indent=2))
    finally:
        for p in processes:
            if p.poll() is None:
                stop(p)


if __name__ == '__main__':
    main()
