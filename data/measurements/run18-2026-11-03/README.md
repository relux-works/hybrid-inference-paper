# Run18 measurement custody

All four local archives match the corrected canonical FACTS digest fragments
and full configured SHA256; every internal payload hash/length is verified.

| Source | Full SHA256 |
|---|---|
| rtx3090_glimmer30 | 7b90ef56035de389a57a13254335f7c77a2cad355bc008ffef86714e4e3971d8 |
| rtx3090_qwen27 | 3d8827833823eb03428ba281b77c563902c27486468fae237fa8cb0c7f4b6004 |
| rtx5090_qwen27 | b10541aa8957930e096a2316c5c74e28a87511d1fb5494fac002067cebf4e3e8 |
| rtx5090_glimmer30 | 3f3f0506882c9d4950e20fc664ce1926e293b41ea914c5d829d0e793f48bd16b |

Canonical FACTS corrected the5090 Qwen suffix from...16b to...e3e8 on
2026-11-03. The original strict refusal is preserved in signed checkpoint
7867b9cc; the corrected snapshot is `FACTS-261103.md`, hashed by the config.
No checksum override flag exists.

Inputs came from `/home/agent/lanes/hybrid/.temp/ckit-results-261103/{3090,5090}/`.
Task-local extracts remain under `.temp/hybrid-e-r10-261103/`. Kit1.6.7,
llama.cpp dde879bc, Q4_K_M, q8_0 KV, recorded Linux TS/nice0.

Prices/fetch times are owner-supplied observations dated2026-11-03:3090
search0.122–0.162USD/h/rented0.153;5090search0.448–0.522/rentedabout0.55.
Qwen18.97GB fetch took1029s/185s respectively. These are not market rates.
Glimmer fetch/API tariff is not supplied. No model download/native build was
performed here. Rental/task/billing and finite coverage limits are in the report.
