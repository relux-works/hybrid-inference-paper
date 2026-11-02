# vLLM cold prefill (method A)

T(L)=aL+bL²/2, seconds; derivative rate=1/(a+bD); fitted Δ10000 rate=10000/(T(D+10000)-T(D)). Loopback TTFT includes request overhead and first token. Server metric deltas and raw SSE are in JSON; residuals above 10% or nonphysical fits are not usable.

| Configuration | a (s/token) | b (s/token²) | Max relative residual | Usable | Error |
|---|---:|---:|---:|---|---|
| fp8-default | 9.342839036996133e-05 | 1.4140563102468149e-09 | 0.016588609751198902 | True |  |

fp8-default residuals: `[{"length": 16384, "observed_s": 1.7444739318452775, "fitted_s": 1.7205221730468372, "residual_s": 0.02395175879844047, "relative": 0.013730075503681886}, {"length": 16384, "observed_s": 1.74954468710348, "fitted_s": 1.7205221730468372, "residual_s": 0.029022514056643023, "relative": 0.016588609751198902}, {"length": 65536, "observed_s": 9.095657782629132, "fitted_s": 9.159585794892035, "residual_s": -0.06392801226290334, "relative": -0.0070284100161500055}, {"length": 65536, "observed_s": 9.171468214131892, "fitted_s": 9.159585794892035, "residual_s": 0.011882419239856112, "relative": 0.0012955852827955115}, {"length": 131072, "observed_s": 24.198836372233927, "fitted_s": 24.392497196996572, "residual_s": -0.19366082476264346, "relative": -0.008002898229637708}, {"length": 131072, "observed_s": 24.613580800127238, "fitted_s": 24.392497196996572, "residual_s": 0.22108360313066733, "relative": 0.008982179591257378}, {"length": 249000, "observed_s": 67.046332558617, "fitted_s": 67.10012184792676, "residual_s": -0.05378928930976201, "relative": -0.0008022704189335835}, {"length": 249000, "observed_s": 67.14968853117898, "fitted_s": 67.10012184792676, "residual_s": 0.04956668325222324, "relative": 0.0007381520947667302}]`

| Depth | Fitted marginal tok/s | Fitted Δ10000 tok/s | llama.cpp Δ10000 tok/s |
|---:|---:|---:|---:|
| 16000 | 8616.731059550772 | 8121.921550577871 | 2141 |
| 50000 | 6092.6866077928935 | 5841.070746468953 | 1476 |
| 100000 | 4258.326770802439 | 4133.8661107807475 | 1018 |
| 150000 | 3272.927775659457 | 3198.9034828509757 | 780 |
| 200000 | 2657.8804056662434 | 2608.854901414605 | 631 |
| 249000 | 2244.5257674155614 | 2209.462853262219 | 532 |

Method B fp8-default

| D | Δ | cached_tokens | Status | tok/s |
|---:|---:|---:|---|---:|
| 16384 | 2000 | 15680 | not supported | None |
| 16384 | 10000 | 15680 | not supported | None |
| 65536 | 2000 | 65072 | not supported | None |
| 65536 | 10000 | 65072 | not supported | None |
| 131072 | 2000 | 130928 | not supported | None |
| 131072 | 10000 | 130928 | not supported | None |
| 249000 | 2000 | 248528 | not supported | None |
| 249000 | 10000 | 248528 | not supported | None |
| fp8-kv | None | None | None | False | vllm startup exit 1 |

Method B fp8-kv

| D | Δ | cached_tokens | Status | tok/s |
|---:|---:|---:|---|---:|

not supported: vllm startup exit 1
| nvfp4-default | None | None | None | False | vllm startup exit 1 |

Method B nvfp4-default

| D | Δ | cached_tokens | Status | tok/s |
|---:|---:|---:|---|---:|

not supported: vllm startup exit 1
| fp8-large-batch | 9.216062614839821e-05 | 1.500578537687494e-09 | 0.06280198521417361 | True |  |

fp8-large-batch residuals: `[{"length": 16384, "observed_s": 1.8235951201058924, "fitted_s": 1.7113639408293342, "residual_s": 0.11223117927655829, "relative": 0.061543912921877775}, {"length": 16384, "observed_s": 1.8260430707596242, "fitted_s": 1.7113639408293342, "residual_s": 0.11467912993029011, "relative": 0.06280198521417361}, {"length": 65536, "observed_s": 9.355489731300622, "fitted_s": 9.26230666748507, "residual_s": 0.09318306381555175, "relative": 0.009960255047236017}, {"length": 65536, "observed_s": 9.419485350139439, "fitted_s": 9.26230666748507, "residual_s": 0.15717868265436863, "relative": 0.016686546749822364}, {"length": 131072, "observed_s": 24.6629576170817, "fitted_s": 24.969549079417433, "residual_s": -0.30659146233572976, "relative": -0.012431252856850502}, {"length": 131072, "observed_s": 25.025444737635553, "fitted_s": 24.969549079417433, "residual_s": 0.05589565821812137, "relative": 0.002233553041879027}, {"length": 249000, "observed_s": 69.43859886005521, "fitted_s": 69.46668086853231, "residual_s": -0.028082008477099407, "relative": -0.00040441496427217916}, {"length": 249000, "observed_s": 69.54590261401609, "fitted_s": 69.46668086853231, "residual_s": 0.07922174548377825, "relative": 0.0011391288703730493}]`

| Depth | Fitted marginal tok/s | Fitted Δ10000 tok/s | llama.cpp Δ10000 tok/s |
|---:|---:|---:|---:|
| 16000 | 8608.083061768992 | 8085.8539516361125 | 2141 |
| 50000 | 5981.234962713116 | 5724.345983431294 | 1476 |
| 100000 | 4128.5041518799735 | 4004.4630123806814 | 1018 |
| 150000 | 3152.114023821239 | 3079.288923122045 | 780 |
| 200000 | 2549.223376806409 | 2501.3805971590104 | 631 |
| 249000 | 2146.8225601262793 | 2112.791033588302 | 532 |

Method B fp8-large-batch

| D | Δ | cached_tokens | Status | tok/s |
|---:|---:|---:|---|---:|
| 16384 | 2000 | 15680 | not supported | None |
| 16384 | 10000 | 15680 | not supported | None |
| 65536 | 2000 | 65072 | not supported | None |
| 65536 | 10000 | 65072 | not supported | None |
| 131072 | 2000 | 130928 | not supported | None |
| 131072 | 10000 | 130928 | not supported | None |
| 249000 | 2000 | 248528 | not supported | None |
| 249000 | 10000 | 248528 | not supported | None |
