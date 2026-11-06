- **End to end over 5G.**
  - Setup: node on CUDA in the UK, client the M3 Max on Metal, iPhone 5G by USB; RTT 110 ms, 16.0 MB/s down,
    9.78 MB/s up.
  - First call, fresh 39,504-token context:

    | Mode | TTFT | Breakdown |
    |---|---|---|
    | local | 271.5 s | |
    | hybrid | 201.7 s | server prefill 10.6 s + transfer 123.2 s + import 42.4 s |
    | offload | 211.7 s | |

    Hybrid is 26% faster than local.
  - Wire: 2,004,023,525 B. That is KV 39,504 × 34,840 B plus 4 copies of the 156.9 MB state, one per 512 MiB chunk.
  - Time accounting (dev-d r13, 2026-11-03; report `.temp/research/time-accounting-r13-261103.md`): measured TTFT
    201.655 s, stream total 202.089 s. The 25.370 s outside server prefill, transfer and import split into 19.659 s
    inside the node request preparation (upload, time to first byte, node state load, export and save, checksums; not
    separately timed) and 5.711 s on the client after it. That older proxy has no full old-slot save.
  - The cross-backend equivalence check is labelled uncalibrated (calibration pending).
