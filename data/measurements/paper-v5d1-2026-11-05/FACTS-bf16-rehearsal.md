- **The Qwen growing-session rehearsal with bf16 state transport (prototype `m3-growing-r46` r46d `7d512238`, Muse
  r7ao ACCEPT; Vast node E, RTX PRO 6000 Server Edition, Japan; 2026-11-03 16:13Z to 2026-11-04 02:38:22Z).**
  Evidence: `.temp/evidence/rehearsal-r46d-e-261104/` (r46d.tar.gz, sha256 c9aa3533...0bf0). Node E was destroyed at
  02:41Z.
  - **Design.**
    - 40 sampled turns from a 100k start; the CUDA client and the CUDA node are on one card. It is a functional and
      numerical check, not a timing comparison.
    - The f32 rehearsal routes by its policy.
    - The bf16 replay then reuses the same captured token journal and the same f32 routing boundaries, rounding every
      critical recurrent envelope to bf16 once. Node states remain f32.
    - So the replay isolates the accumulated client-side effect of bf16. It does not test bf16 routing decisions or a
      changed free-running history.
  - **Checkpoints** at turns 10 / 20 / 30 / 40 (depth 109,591 / 123,135 / 134,015 / 143,439), 64 teacher-forced
    positions each:

    | Comparison | Mean KL, nats, at turns 10 / 20 / 30 / 40 | Top-1 | Max |Δlogit| |
    |---|---|---|---|
    | f32 rehearsal, hybrid against local | 1.567e-4 / 3.62e-5 / 2.572e-4 / 1.276e-4 | 64/64 at each | 0.53-0.82 |
    | local partition noise (the same checker) | 6.12e-4 / 3.48e-5 / 1.60e-4 / 1.80e-4 | | |
    | bf16 replay, local against bf16 | 6.92e-5 / 1.212e-4 / 1.53e-4 / 1.025e-4 | 64/64 at each | 0.76-1.06 |
    | bf16 replay, f32 against bf16 | 7.39e-5 / 1.80e-4 / 1.602e-4 / 5.29e-5 | 64/64 at each | 0.51-1.12 |

    - Maximum KL in the bf16 replay: 0.00329 (local) and 0.004457 (f32), both at turn 30.
    - No free-running divergence within 64 tokens in any comparison.
    - Imports up to the checkpoint: 5 / 9 / 12 / 18.
  - The replay exits with code 5, «lossy», as expected for bf16: exactness is not claimed, and the quality gate passes.
