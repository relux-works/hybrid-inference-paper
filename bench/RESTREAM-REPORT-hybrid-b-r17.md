# Restream check: hybrid-b-r17-261101

Validated on Linux x86_64, 2026-11-01 UTC. Implementation: signed commit
`6d946879c72ec40e44dd2717024e794f2e304ab4`, branch `bench-kit-restream`, based on
requested `e5f64d2` after `git fetch origin bench-kit`. No pushes.
Mac **1.4.0**, GPU **1.2.1**. GPU measurement/slot-generation commands are unchanged.

Source verification at **c21284cdf5fd833b90ac1f824cdf8065e2700dc4**, read from the
existing local upstream checkout (no upstream fetch/download):

- `include/llama.h:44-49`, `src/llama-context.cpp:3226-3300`: GGSQ magic
  `0x67677371`, version 3, u32 token-word count and token words, then memory state.
- `src/llama-kv-cache.cpp:2053-2333`: u32 stream count; per-stream cell count,
  optional 12-byte cell extension (`src/llama-kv-cells.h:13`), metadata, all K rows,
  then V rows or transposed V elements. `state_read_sinfo:2150-2177` checks equal
  stream counts, skips empty entries and maps a sequence restore to its destination
  stream. Therefore inserted empty entries belong after stream 0's V data.
- `src/llama-memory-hybrid.cpp:190-201`: attention precedes recurrent state.
  Its default complementary layer filters establish the recurrent tensor count.
  `src/llama-memory-recurrent.cpp:766-990` writes no stream count: cells/meta,
  s_trans, total layer count, R rows then S rows (plus PLE history where enabled).
- `tools/server/server-context.cpp:2565-2590` and `server-common.cpp:570-638`:
  the server packs a token wrapper. This test's header has **3076 words** for
  **3072 logical tokens**; the restreamer preserves all these bytes.

The parser checks the entire supported hybrid layout, dimensions' type alignment,
section lengths and EOF; it requires a unique interpretation of the cell extension.
OUT is published exclusively after validation; IN is opened read-only. It changes
only n_stream and adds N−1 zero cell counts, checks length growth and prints both
SHA-256 values. Model dimensions/masks are absent from the file, so matching-model
compatibility still belongs to llama.cpp. Unsupported PLE/missing-V/nonuniform
layouts are refused, as documented in the Mac README.

Build/check commands (repository root; `B=$PWD/.temp/hybrid-b-r17`):

```bash
mkdir -p "$B/llama-src"
git -C ../llama.cpp archive c21284cd -o "$B/source.tar"
tar -xf "$B/source.tar" -C "$B/llama-src"
# Existing local tool, no install:
CMAKE=/home/agent/Werkstatt/hybrid-a/llama.cpp/.temp/hybrid-a-r1-261030/cmake-tool/cmake/data/bin/cmake
flock /home/agent/Werkstatt/hybrid-models/.build.lock bash "$B/build.sh"
# build.sh ran these two commands under that lock:
"$CMAKE" -S "$B/llama-src" -B "$B/build" -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=OFF -DGGML_METAL=OFF -DGGML_VULKAN=OFF -DGGML_OPENCL=OFF -DGGML_SYCL=OFF -DGGML_RPC=OFF -DGGML_BLAS=OFF -DGGML_NATIVE=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_APP=OFF -DLLAMA_OPENSSL=OFF -DLLAMA_BUILD_COMMIT=c21284cd -DLLAMA_BUILD_NUMBER=11087
"$CMAKE" --build "$B/build" --target llama-server -j2
PYTHONDONTWRITEBYTECODE=1 python3 bench/tests/check_restream_cpu.py --server "$B/build/bin/llama-server" --model /home/agent/Werkstatt/hybrid-models/Qwen3.5-0.8B-Q4_0.gguf --out "$B/cpu-03"
TMPDIR="$B/tmp" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bench/tests -v
(cd bench/mac && sha256sum -c CHECKSUMS.sha256)
(cd bench/gpu && sha256sum -c CHECKSUMS.sha256)
```

| Check | Exit | Evidence under `.temp/hybrid-b-r17/` |
|---|---:|---|
| Configure / single CPU build / server version | 0 / 0 / 0 | `configure-01.log`, `build-01.log`, `build-run-01.log`, `server-readiness.log` |
| Real CPU check | 0 | `cpu-03.log`, `cpu-03/result.json`, `cpu-03/http.json`, server logs |
| Existing + new unit/shell tests: **20 tests** | 0 | `tests-08.log` |
| Shell syntax, Python 3.8 syntax, diff whitespace | 0 | `shell-syntax-01.log`, `python-syntax-01.log`; `diff-check-02.log` |
| Mac / GPU checksums | 0 / 0 | `mac-checksums-02.log`, `gpu-checksums-01.log` |
| Shared-file identity audit | 0 | `shared-audit-03.json`: all six originally identical file pairs remain identical |

CPU: CMake 4.4.4, GCC 15.2.0, build 11087/c21284cd; UI build and prebuilt UI both
OFF, zero embedded UI assets. All GPU backends OFF. Observed free disk was above
36 GiB (25 GiB stop threshold); guarded before configure/build and CPU requests,
and observed throughout the build. The build and extracted source were deleted;
logs, CMake cache, binary hash and test slots remain in `.temp/hybrid-b-r17/`.

The requested Qwen3.5-0.8B-Q4_0.gguf **is hybrid**: architecture `qwen35`, six
attention layers, recurrent F32 R/S state with 18 tensor pairs, no PLE history.
Model SHA-256: `444406ddd926550c724ec18d5120a9d40ded44908a063b0e66e9a7e5464c652c`.
Servers used `-ngl 0 -t 2 -tb 2 --no-kv-unified -fa on -ctk q8_0 -ctv q8_0`,
`--offline -lv 4 --no-warmup`; np=1/ctx=8192 then np=4/ctx=32768.

| Real-server assertion | Observed |
|---|---|
| Saved on np=1 / restored on np=1 | 3072 / 3072 tokens |
| Original restored into np=4 slot 2: negative control | HTTP **400**, **n_stream mismatch** in server log |
| Restreamed restored into np=4 slot 2 | **3072 tokens** |
| Greedy continuation after each own restore | **16 identical token IDs and identical content** |
| Prompt evaluation for those continuations | **7 tokens on each**, so no full reread |
| File length | 40,342,144 → 40,342,156 bytes: exactly +12 |
| IN unchanged | SHA-256 unchanged after both restores |

IN SHA-256: `5d295b40d6cfba495326494972a54ed29339ba672ed7666c4d74cbe52afb6663`.
OUT SHA-256: `7c38efca7a7ea36e7324e49509ae71c3b8c99ae1f42fb76ab6d4a0f50874bf67`.
Continuation: ` The river flows past the old stone bridge.  The river flows past the old`.
Token IDs: `[561,14367,26565,3162,279,2235,9506,13759,13,220,561,14367,26565,3162,279,2235]`.
All owned server PIDs stopped with exit 0 and were verified absent:
2165918, 2167153, 2167535, 2167727.

Coverage: claims are beside tests. `Restream.test_expansion` checks 2/4/8 streams,
both cell-extension forms, both known V layouts, q8_0 and exact byte preservation.
`test_refusals` rejects malformed fields, every byte truncation, extra streams,
size mismatches, trailing bytes and unknown V layouts; `test_path_disk_and_publish_refusals`
checks aliases, existing outputs, disk and failed publication. `test_server_token_words`
retains the real-check wrapper regression witness. `MacImport` exercises both import
locations, startup fallback/exhaustion, no-space skipping, errors, TERM cleanup and
one-stream direct use. `PowerMode`/`MacPowerCheck` cover stored representative pmset
fixtures for both formats, absent keys, values 0/1/2, integer JSON and warnings.

Corrected failures are retained in `step-notes.txt`: initial unit runs exited 1
for an unflushed temporary fixture and an incorrect mock memory bound; CPU attempts
01/02 exited 1 for hidden INFO diagnostics and the header-word/logical-token
assumption. Their servers were stopped; assertions were corrected from source,
not weakened to accept the failed behavior. An initial checksum command did not
run due to its log redirection path; corrected standalone commands above passed.

Bounds: no live Mac/Metal/GPU or 260k/1M run was performed. CPU evidence covers this
hybrid model, 3072 tokens and destination slot 2 at np=4; shell tests cover larger
stream counts/fallback mechanics. Brief gap: no attack-surface table was supplied;
coverage is the requested contract above. No requested row was treated as out of
contract. Self-review found no outstanding blocker; publication is intentionally
excluded by the user's no-push limit.

## r18: fixes for review r4k (hybrid-b-r18-261101)

Validated on Linux x86_64, 2026-11-01 UTC; verification and implementation signature
observed by **06:40:47 UTC**. Base: requested `c3ef976e`; signed implementation:
`7db6d636b5568e312ca285182585cb871207f97f` (`G`, Relux Nexus).
Branch remains `bench-kit-restream`. No pushes. Mac 1.4.0 / GPU 1.2.1 retained.
Read the complete r4k report at
`/home/agent/Werkstatt/hybrid-review/paper/.temp/REVIEW-bench-restream-claude.md`.

- **M1:** the step removes its entire owned `mktemp` directory, including hidden
  `.restream-*` files and its per-attempt log. Python converts TERM to exit 143,
  allowing its `finally` to unlink the temporary file. Existing EXIT handling
  stops/waits for the child before directory removal. TERM and INT to each of
  steps 56/57 during an observed partial **1.56 GiB sparse synthetic import**
  leave no scratch entries or step lock and preserve IN's SHA-256. A separate
  direct CLI TERM test proves Python cleanup without the shell's directory cleanup.
- **m1:** unknown numeric/text pmset values warn, contribute integer 0 and allow
  step 00 to write `system.json` and continue. Known 0/1/2 and missing-key controls
  remain covered; no traceback is accepted for the unknown-value case.
- **m2:** insufficient disk falls back to a one-stream server using the import
  directly, with an explicit log message. Tests exercise both the shell preflight
  and Python's second capacity check. ENOSPC (including a write/publication error)
  returns 3 from the CLI; other refused inputs still return 1. No disk is actually
  filled to test this condition: capacity is mocked in isolated fixtures.
- **m3:** EN/RU READMEs and prompts include the copy: about **73 GB** with 260k
  alone (55 + 9 + 9), or **136 GB** with both imports (55 + 45 + 36). The step-00
  disk warning distinguishes the existing 28 GB slot budget from imported files
  and their extra copy. Only one copy is kept at a time.
- **m4:** hash each import once per depth, pass its cached digest with
  `--input-sha256`, hash each OUT once, then reuse the helper's OUT digest in the
  shell log. Existing IN/OUT hash values and stdout format are preserved. This
  cache assumes the owner leaves the import unchanged while the step runs.
- **Notes:** N1 now has ambiguity and duplicate/decreasing-position regressions;
  N4 puts the optional command first; N5 documents the fresh-position limitation.
  N2's optional JSON source field is deferred: warnings still distinguish unknown
  from measured-off only in the log, not in `system.json` alone. N3 needs no code
  change: r4k already qualified the kit flags without `--no-kv-unified`; the r17
  CPU harness and its recorded flags remain unchanged.

All r18 logs are under `.temp/hybrid-b-r18-261101/`. Commands ran as standalone
processes; no validation output was piped through `tee`.

| Check | Actual exit | Evidence |
|---|---:|---|
| `TMPDIR="$PWD/.temp/hybrid-b-r18-261101/tmp" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bench/tests -v` | 0 | `tests-02.log`: **24 tests**, 45.376 s; all original 20 names retained |
| Bash `-n` for both kits; Python 3.8 AST syntax | 0 | `syntax-01.log` |
| `sha256sum -c CHECKSUMS.sha256` in each kit | 0 / 0 | `mac-checksums-01.log`, `gpu-checksums-01.log` |
| Manifest, shared files, output-format source audit | 0 | `manifest-shared-01.log`: 54 bench entries, other lines unchanged, six shared pairs identical |
| `git diff --check`; staged diff check | 0 / 0 | `diff-check-01.log`, `staged-check-01.log` |
| `git verify-commit` on implementation | 0 | `implementation-signature-01.log` |
| Isolated negative-control runner | 0 | `controls-run-01.log`, `controls.json`; each planted defect below exited **1**, as intended |

Bounded controls copy only kit/test files under `.temp/controls` within the r18
artifact directory; no source checkout is mutated. Each failure was inspected for
the intended assertion. These are discrimination controls, not passing product tests.

| Mutant | Gate property narrowed | Named failing test | Actual exit / surviving bound |
|---|---|---|---|
| Default TERM action restored | Python removes hidden partial copy | `Restream.test_term_during_copy` | 1; hidden file remains |
| Old partial shell cleanup restored | Entire owned directory removed | `MacImport.test_fallback` | 1; directories/logs remain |
| Unknown pmset abort restored | Step 00 continues on unknown value | `MacPowerCheck.test_system_json` | 1; unknown sample aborts |
| Low-disk loop breaks | One-stream measurement retained | `MacImport.test_disk_error_signal` | 1; direct attempt absent |
| IN rehashed despite cache | Only OUT hashed per attempt | `Restream.test_cached_hash` | 1; extra IN hash call |
| First valid interpretation wins | Ambiguous layouts refused | `Restream.test_ambiguous_layout` | 1; refusal absent |
| Only nonnegative positions required | Strict position order enforced | `Restream.test_refusals` | 1; duplicate/decreasing cases accepted |

No control survived. Bounds remain finite: Linux process/shell tests, synthetic
files and mocked macOS/server/capacity calls; no live Mac/Metal, 260k/1M, GPU or
new real-engine run. The parser, copy operations, byte output validation and
exclusive publication region are identical to c3ef976e (`manifest-shared-01.log`),
and exact-byte/hash unit checks pass. The r17/r4k real-engine qualification is
therefore reused under the requested exception. No build, model download or
server was started. Free disk observed at 36–37 GiB, above the 25 GiB floor;
large test fixtures and partial copies were removed. No tools installed.

Brief gap: no attack-surface table supplied; coverage follows the requested
review findings and the named tests above. No requested fix is out of contract.
Rework stays in `bench/`; root `MANIFEST.sha256` changes are its matching bench
hashes only. Self-review and local verification pass; ready for re-review.
