"""Reviewer reproduction for finding r18-cuda-import-depth-double-count (candidate 12f0c042).

Claim: the candidate's CUDA import model (PR9 marginal fit + R16 Mac recovery-depth slope) is
contradicted by the PR9 CUDA import records it is fitted from, and that contradiction flips
threshold verdicts from "never" to finite.

Retained reviewer regression: both tests fail at12f0c042 and must pass after rework.
Run with the normal engine unittest discovery; no external checkout is required.
"""
import csv, json, os, sys, unittest

from pathlib import Path
WT = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, os.path.join(WT, 'calc'))
from hybridcalc import measurements_r18 as r18  # noqa: E402

PR9 = os.path.join(WT, 'data/measurements/run14-2026-11-02/pr9/hybrid-bench-r13-27b-cuda-20261101T132757015879Z.jsonl')


def pr9_calls():
    rows = [json.loads(l) for l in Path(PR9).read_text().splitlines() if l.strip()]
    return [r for r in rows if r.get('stage') == 'call' and r.get('import_ms', 0) > 0]


def ols3(rows):
    # import_s = a + b*tokens + c*depth_before, by normal equations
    X = [[1.0, r['remote_applied'], r['depth_before']] for r in rows]
    y = [r['import_ms'] / 1000 for r in rows]
    A = [[sum(x[i] * x[j] for x in X) for j in range(3)] for i in range(3)]
    b = [sum(x[i] * t for x, t in zip(X, y)) for i in range(3)]
    for i in range(3):
        for j in range(i + 1, 3):
            f = A[j][i] / A[i][i]
            A[j] = [p - f * q for p, q in zip(A[j], A[i])]
            b[j] -= f * b[i]
    out = [0.0] * 3
    for i in reversed(range(3)):
        out[i] = (b[i] - sum(A[i][k] * out[k] for k in range(i + 1, 3))) / A[i][i]
    return out


class CudaImportDepth(unittest.TestCase):
    # Claim: the admitted CUDA import model must not over-predict its own CUDA source
    # measurements by more than 25% at any measured depth. Positive control: depth ~0 rows pass.
    def test_model_matches_pr9_cuda_measurements_at_depth(self):
        worst = 0
        for r in pr9_calls():
            model = r18.cuda_import(r['remote_applied'], r['depth_before'], 'qwen27')
            measured = r['import_ms'] / 1000
            if r['depth_before'] < 1000:
                self.assertLess(abs(model / measured - 1), 0.25)  # positive control
            worst = max(worst, model / measured)
        self.assertLess(worst, 1.25, 'model/measured import ratio %.2f at PR9 depth' % worst)

    # Claim: "never (budget<=0)" must be robust to replacing the ported Mac depth slope with the
    # depth slope measured on CUDA in the same PR9 file; otherwise "never" is an artefact.
    def test_never_status_survives_cuda_measured_depth_slope(self):
        a, b, c = ols3(pr9_calls())
        flips = []
        for row in csv.DictReader(Path(WT, 'calc/out/run18/gpu_link_threshold.csv').read_text().splitlines()):
            if row['threshold_status'] != 'never_pays_nonpositive_budget':
                continue
            d, n = int(row['depth']), int(row['delta'])
            budget = float(row['local_prefill_s']) - float(row['server_prefill_s']) - (a + b * n + c * d) - float(row['rtt_s'])
            if budget > 0:
                flips.append((row['client'], row['state_format'], d, n, round(float(row['wire_bytes']) / budget / 1e6, 3)))
        self.assertEqual(flips, [], 'never cells finite under PR9 CUDA depth fit: %s' % flips)


if __name__ == '__main__':
    unittest.main()
