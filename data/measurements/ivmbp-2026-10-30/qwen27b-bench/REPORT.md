# Qwen3.8-27B measurement — validated depth, parallel and reported power

Frozen hybrid_bench1.1; depth process actual exit0,6segments/18turns/6save+restore pairs. Synthetic prompts, no user session contents.

| Depth | Marginal prefill | Turn prefill512/2k/10k | Native decode512/2k/10k | Slot size | Save / restore |
|---|---:|---:|---:|---:|---:|
| 16k | 173.6tok/s | 132.1 / 163.4 / 144.1tok/s | 7.48 / 8.47 / 8.82tok/s | 0.714GB | 2.437s / 2.635s |
| 50k | 93.7tok/s | 71.5 / 75.6 / 70.6tok/s | 7.54 / 7.78 / 7.54tok/s | 1.899GB | 5.737s / 2.218s |
| 100k | 49.9tok/s | 40.0 / 46.5 / 41.9tok/s | 6.98 / 6.59 / 5.30tok/s | 3.641GB | 8.825s / 4.316s |
| 150k | 41.2tok/s | 37.2 / 42.4 / 38.5tok/s | 6.79 / 5.43 / 6.18tok/s | 5.383GB | 16.274s / 4.956s |
| 200k | 27.7tok/s | 28.9 / 34.8 / 26.7tok/s | 4.34 / 6.00 / 5.34tok/s | 7.126GB | 24.921s / 7.393s |
| 249k | 22.2tok/s | 22.8 / 24.5 / 20.8tok/s | 5.44 / 5.25 / 4.82tok/s | 8.833GB | 28.271s / 8.033s |

All segment/turn prefix reuse is independently bounded to <=1extra prompt token. No truncated/error/skipped/interrupted row. Final requested prompt261768 plus128predicted tokens=261896, below actual262144context. Checkpoints have matching reported saved/restored token counts and byte sizes; next requests retain prefix reuse. No output-quality or cross-engine cache-transfer claim.

Primary decode is the server timings.predicted_per_second=(n_gen-1)/predicted_seconds. Frozen1.1 raw rows retain their original n_gen/predicted_seconds convention, about0.787%higher at128tokens; do not mix them silently. Generated ID arrays are exact according to the frozen result flag; later sequence lengths corroborate128IDs except the final turn, whose raw array length was not separately retained. Parallel trace adds response array counts without changing requests.

All slotfiles belong to this workbench, not shared Strata paths. Save/restore timings include the observed local filesystem/cache state; they are not cold-disk or network-transfer throughput.

## Environment and limits

Apple M3 Max/Mac15,9/128GiB/macOS27.2build26B123/AC. Qwen3.8-27B Q4_K_M, actual GGUF18,973,870,432bytes; model context262144, qwen35architecture. Engine llama.cpp0.4.1-dev/build11087/c21284cdf, engine sourcec21284cdf5fd833b90ac1f824cdf8065e2700dc4. Metal allGPUlayers, flash-attentionon, K/Vq8_0. Single phase context262144,np1. Parallel requested totalcontext140000,np4; actual observed35072tokens/slot (140288total after engine rounding).

Shared Strata stayed resident and unmodified; its memory compression/reclamation changed during the experiment. The machine was not exclusively idle. Lightweight root/a2a/GitHub/security-watch network/CLI activity occurred; no corpus scan or Swift build during measured GPU phases. No restart, stop, request or slot deletion against shared Strata.

Power capture is owner-started CPU/GPU/ANE estimates for all processes. It is neither AC wall power nor exclusive model energy. Whole-second sample headers introduce <=1sboundary uncertainty; turn request windows combine prefill/decode. Do not subtract a nonstationary background into a falsely precise exclusive model result.

## Four-stream32k result

Four independent32kcontexts were filled sequentially before the baseline/parallel generation measurements. Actual runtime17.2minutes including setup/prefill; each of the five generation requests returns128token IDs. All four parallel requests overlap for38.869s, no error/truncation, each reprocesses only16/17new prompt tokens.

| Metric | Value | Convention |
|---|---:|---|
| Single-stream decode |8.441tok/s|native server127timed decode steps|
| Per concurrent stream |3.514tok/s|native server|
| Aggregate decode interval |14.054tok/s|508timed decode steps / maximum server decode interval|
| Batching gain |1.665x|same decode-interval convention|
| Actual end-to-end joint throughput |13.160tok/s|512generated IDs /38.907s client wall including prefill/HTTP/scheduling|

Raw frozen1.1parallel row reports14.16tok/s aggregate,8.51single,1.67gain from its n_gen formula. Keep raw and normalized conventions distinct. Client overlap alone is not exact GPU-kernel timing. n_predict0prefill requests return one initial token with zero timed decode iterations; that is retained, not counted as a128-token trial.

## CPU/GPU/ANE estimates

17,904complete samples, zero invalid complete samples; one final in-flight sample excluded. The two GPU sections were kept separate; their phase averages agree within0.001W. They must not be added. Combined is the field reported alongside CPU/GPU/ANE in the CPU-power section.

| Window | CPU | GPU | Combined | Integrated reported-domain energy |
|---|---:|---:|---:|---:|
|ladder-01/whole_phase|1.728W|17.194W|18.922W|38.531Wh|
|parallel4_joint_wall|1.394W|25.199W|26.592W|0.286Wh|
|parallel-01/whole_phase|1.970W|29.745W|31.715W|9.074Wh|

These are all-process CPU/GPU/ANE estimates, not AC wall power, whole-machine total energy or exclusive model energy. ANE reports0throughout these windows. Per-request summaries mix prefill and decode for generation turns. Sample headings have whole-second resolution; up to1sselection uncertainty at each boundary. Pre-smoke background is descriptive, not a valid stationary baseline to subtract. Overlapping windows must not be summed.

Source-prefix hash and byte bound in power-summary.json permit a private raw-log audit; raw powermetrics is retained locally. Original benchmark file-name stamps use local+04time; trace timestamps are explicit UTC and row ts fields are Unix time. Both measured servers were stopped by their exact verified own PID; shared Strata and owner-started powermetrics remain outside our process custody.

Actual-call-date aggregates are a separate queued result; this package does not claim that task or the broader Memori objective is complete.
