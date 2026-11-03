# Cooled M3 parallel sweep (kit1.6.6)

Original owner-supplied archive, retained byte for byte:
`qwen27-kit166-scaling.tar.gz`, SHA-256
`916891bdcf32112bdba069140ef86eb35bf4fbaec8b1f342b2ffd2baa637d618`.
Source: `/home/agent/lanes/hybrid/.temp/mac-results-261102/`.
The copied FACTS protocol and clock-label discrepancy are in [PROTOCOL.md](PROTOCOL.md).

M3 Max128GB, Qwen3.8-27B Q4_K_M, q8_0 KV, FA on, llama.cpp
`dde879bc4f954b809892fd0d660515f42536394a`. Fill once, cool300s, restore before
every round; median of three. Largest-np32/32/16 shapes at32k/64k/128k are
base; np4/four-stream128k is sensitivity only. Every raw request/round remains
in the manifest-backed archive. Step56's260k observations are reused from the
R14 archive; historical step55/control/1.04M points stay outside the R15 base.

| Tool | Exact command from repository root | Output |
| --- | --- | --- |
| SHA-256 | `sha256sum data/measurements/run15-2026-11-02/qwen27-kit166-scaling.tar.gz` | Full digest on stdout |
| Python standard-library archive/export audit | `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.temp/hybrid-e-r6-261102/tmp" python3 -B -I calc/tests/r15_audit.py` after creating TMPDIR | Verified eight-family `calc/out/run15/`, index and quote ledger; no persistent extraction |

The admission reader verifies the full archive pin and every manifest payload
size/hash and rejects unsafe paths, links, duplicates and unmanifested data.
The engine consumes the archive directly. Task-local verification extracts
are removed before handoff; the original archive is retained.
