# Hybrid prefill/decode prototype: plan

Status: plan for estimation (2026-10-30). Owner: Ivan Aparin. Author: agents1 hybrid lane.
The detailed specification follows after the estimate and Ivan's go-ahead. No work has started.

## Goal

Show, on existing engines and hardware, that a server can prefill an agent session and hand the
model state to a Mac, which then continues decoding. The model is Qwen3.8-27B: 64 layers, of which 16
are full attention and 48 are Gated DeltaNet. The decode after the hand-off must match the decode
after a local prefill, and the hand-off must be fast enough over a 100 Mbit/s – 1 Gbit/s link to beat
the Mac's local prefill on large turns.

What crosses the network per hand-off:
- up: token ids of the new turn (kilobytes);
- down: the attention KV of the new positions (8-bit: about 32 KiB per token) plus the full recurrent
  state of the DeltaNet layers (about 78 MB in bf16, 157 MB in fp32), a fixed cost per hand-off.

## Components

1. **Prefill node.** A fork of llama.cpp's `llama-server` on a GPU server.
   - Holds every session (tokens, KV, recurrent state) as the system of record.
   - `extend(session, token_ids)`: prefills the new tokens and returns a state delta, that is the KV of
     the new positions plus the recurrent state at the new end.
   - Shadow prefill: tokens that the client generated locally are appended in the background, so the
     server copy stays identical to the client's.
   - Storage tiers: VRAM, then host RAM, then NVMe, with a time-to-live of hours to days.
2. **Decode node.** A fork of `llama-server` on the Mac (Metal).
   - Imports a state delta into a slot: appends the KV positions and replaces the recurrent state.
   - Decodes and reports the generated token ids back to the prefill node.
3. **Client proxy.** An OpenAI- and Anthropic-compatible endpoint for agent harnesses.
   - Per turn it decides between local prefill and offload, from the delta size, the measured link
     bandwidth and the local prefill rate at the current depth.
   - It falls back to local prefill when the server is unreachable.
4. **Transport.** HTTP/2 or gRPC streaming with per-layer chunks.
   - KV in q8_0 (optionally 4-bit V); recurrent state in bf16 (fp8 is a later experiment).
   - Hashes of the token prefix on both sides; resumable downloads.

## llama.cpp base

- `llama-server` slot save and restore (`/slots/{id}?action=save|restore`) moves a whole sequence
  state today. Milestones M0–M1 need no engine changes.
- `llama_state_seq_get_data` / `set_data` and their `_ext` variants with partial-state flags, used by
  context checkpoints for SWA and recurrent models. Verify the current names in llama.cpp.
- Missing piece: export of a position range of the attention KV together with the recurrent state,
  and import of that as an append.
- Recurrent memory cannot drop a suffix, so the protocol is strictly append-only. On divergence the
  client re-syncs from a server snapshot.

## Milestones

| | What | Done when |
|---|---|---|
| M0 | Two `llama-server` processes on one machine, one GGUF. A prefills and saves the slot; B restores it and decodes. | B's greedy tokens match A's for 64+ tokens on 95% of test prompts, or the logit KL is below a set bound (batching is not bit-deterministic). |
| M1 | Whole-session transfer over HTTP: a CUDA (or CPU) server node, the Mac as the client. | M0's criterion across backends. Measured bytes per token and seconds per hand-off. |
| M2 | Incremental delta: export KV positions [n0, n1) plus state; import as an append. | Decode after an M2 import equals decode after a local prefill. The delta size matches the formula. |
| M3 | Proxy, offload policy and network emulation: `dnctl`/`pfctl` on macOS, `tc netem` on Linux; 100 Mbit/s, 200 Mbit/s and 1 Gbit/s; RTT 20–80 ms. | Real agent traces show wall-clock gains within ±25% of the model's prediction. |
| M4 | Compression and precision: fp8 state, 4-bit V, logit drift over N turns. GPU prefill node with storage tiers. | Bytes saved and drift measured. The server holds 100+ parked sessions. |

The cleanest proof uses one and the same GGUF on the server (CUDA) and on the client (Metal), so that
mixed weight precision is not a question.

## Resources and constraints

- Client: Ivan's MacBook Pro M3 Max 128 GB, or another Mac with 64 GB or more.
- Server: one CUDA GPU with 48 GB or more is enough for the prototype (RTX PRO 6000, L40S, A100,
  H100). M0–M2 can also run with the Mac as both server and client.
- agents1 has no GPU and shared CPU. Builds and benchmarks there only with the keeper's yes. Most
  work belongs on the Mac or a GPU host.
- Code lives in a new repository, which needs the owner's confirmation. The fork follows llama.cpp
  upstream; patches should stay small enough to propose upstream.

## Risks

- llama.cpp's memory internals (the hybrid and recurrent caches) change often, so a fork can drift.
- Partial export of hybrid memory may need patches inside `llama_memory_hybrid` and the recurrent cache.
- CUDA and Metal give numerically different results, so equivalence is statistical, not bitwise.
- Qwen3.8 support details in llama.cpp, for example DeltaNet kernels on Metal, are to be verified.
