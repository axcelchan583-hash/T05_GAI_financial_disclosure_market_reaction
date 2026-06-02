# v13 Peer-Validity Gate

日期：2026-05-31

## Purpose

This gate evaluates whether candidate peer systems behave like economically
meaningful peer systems before they are used in the GenAI event-study.

Primary validation follows the logic used in peer-identification papers:

```text
If j is a valid peer of i, returns of i and the equal-weighted peer portfolio of j
should comove more strongly than weak/random peers.
```

We report both raw-return comovement and market-model abnormal-return comovement.

## Literature-backed Peer Systems

- Industry peers: SIC/CSRC same-industry baseline.
- Text-based product-market peers: Hoberg and Phillips (2016, JPE) / TNIC-style.
- Search-based peers: Lee, Ma, and Wang (2015, JFE), not locally observable here.
- Common analyst peers: Kaustia and Rantala (2021, JFQA), requires analyst coverage data.
- Technological peers: Cao, Ma, Tucker, and Wan (2018, TAR), separate technology-space construct.
- LLM-generated peers: Cao, Chen, Tucker, and Wan (2025, RAST), prepared here as a validation template.

## Main Return-Comovement Gate, 2025-2026, Top5

Sorted by mean market-model abnormal-return correlation:

| peer_system                         |   pair_count |   focal_firms_with_returns |   mean_abret_corr |   median_abret_corr |   p_abret_corr |   mean_raw_corr |   median_raw_corr |   p_raw_corr |   mean_peer_similarity |
|:------------------------------------|-------------:|---------------------------:|------------------:|--------------------:|---------------:|----------------:|------------------:|-------------:|-----------------------:|
| annual_same_industry_2024_top5      |         5819 |                       1107 |            0.4352 |              0.4383 |              0 |          0.5814 |            0.5952 |            0 |                 0.3623 |
| annual_global_2024_top5             |         5845 |                       1108 |            0.4167 |              0.4273 |              0 |          0.5684 |            0.585  |            0 |                 0.3892 |
| annual_global_ai_stripped_2024_top5 |         5845 |                       1108 |            0.4144 |              0.4225 |              0 |          0.5669 |            0.5819 |            0 |                 0.3879 |
| csmar_scope_top5                    |        13260 |                       2450 |            0.3547 |              0.3494 |              0 |          0.5126 |            0.5164 |            0 |                 0.232  |
| csmar_scope_ai_stripped_top5        |        13255 |                       2449 |            0.3541 |              0.3486 |              0 |          0.5122 |            0.5158 |            0 |               nan      |
| random_same_industry_top5           |        13000 |                       2403 |            0.3007 |              0.2938 |              0 |          0.475  |            0.476  |            0 |                 0.0526 |
| low_similarity_same_industry_top5   |        13000 |                       2401 |            0.2459 |              0.24   |              0 |          0.4361 |            0.444  |            0 |                 0.0062 |

## Outputs

```text
results/v13_peer_validity_gate_20260531/peer_validity_return_comovement_summary.csv
results/v13_peer_validity_gate_20260531/peer_validity_focal_return_comovement.csv
results/v13_peer_validity_gate_20260531/peer_validity_paired_system_comparisons.csv
results/v13_peer_validity_gate_20260531/peer_system_pair_overlap.csv
results/v13_peer_validity_gate_20260531/peer_validity_decision_matrix.csv
data/peer_validity_llm_20260531/llm_peer_request_template_200_20260531.csv
data/peer_validity_llm_20260531/LLM_PEER_CODING_TASK.md
```

## Current Reading

This is a measurement gate, not the final paper table. A peer system should be
preferred only if it has both:

1. a published peer-identification literature anchor; and
2. stronger return comovement than random/low-similarity same-industry peers.

Revenue and gross-margin comovement will be added after confirming the local
financial-statement fields.

## Paired Comparison, 2025-2026, Top5, Abnormal-Return Correlation

Same focal firms only:

| system A | system B | mean corr A | mean corr B | mean diff | p |
|---|---|---:|---:|---:|---:|
| annual same-industry text | low-similarity same-industry | 0.4328 | 0.2506 | 0.1822 | <0.001 |
| annual same-industry text | random same-industry | 0.4330 | 0.3150 | 0.1180 | <0.001 |
| CSMAR scope text | low-similarity same-industry | 0.3532 | 0.2459 | 0.1073 | <0.001 |
| annual global text | random same-industry | 0.4175 | 0.3150 | 0.1024 | <0.001 |
| annual global AI-word-stripped text | random same-industry | 0.4151 | 0.3150 | 0.1001 | <0.001 |
| CSMAR scope text | random same-industry | 0.3534 | 0.3008 | 0.0527 | <0.001 |
| CSMAR scope text | annual global text | 0.3703 | 0.4167 | -0.0464 | <0.001 |
| CSMAR scope text | annual same-industry text | 0.3703 | 0.4352 | -0.0649 | <0.001 |

Interpretation:

- 旧 CSMAR scope peer 不是完全无效；它显著强于随机同业和低相似同业。
- 但年报文本 peer 的 return comovement 更强，更接近 Hoberg-Phillips / Cao et al. 风格的 peer-validity criterion。
- 因此当前主结果如果只在 CSMAR scope peer 中成立，而在年报 peer 中不成立，风险不是“peer 无效”，而是“主结果对 peer-identification system 敏感”。

## Current Decision Matrix

| peer system | literature support | return gate | fundamentals gate | proxy direct share | two-coder direct share | GenAI PeerCAR result | current role |
|---|---|---:|---:|---:|---:|---|---|
| annual same-industry text Top5 | strongest Hoberg-Phillips-style A-share analog | best | best | 0.8886 | 0.7167 | does not reproduce | benchmark / replacement test |
| annual global AI-word-stripped Top5 | strong but cross-industry false positives | strong | strong | 0.5422 | 0.6000 | does not reproduce | robustness / AI-word-stripped check |
| CSMAR scope Top5 | moderate Hoberg-Phillips-style business-description analog | passes | passes | 0.4545 | 0.6500 | preserves current result | possible headline, but limitation must be transparent |
| random same-industry Top5 | industry placebo | weaker | weaker | 0.0995 | 0.4667 | placebo | falsification |
| low-similarity same-industry Top5 | negative-control placebo | weakest | weak/noisy | 0.0008 | 0.2333 | placebo | falsification |

One-line verdict:

```text
The measurement-clean winner is annual same-industry annual-report text peers.
The result-preserving system is old CSMAR scope peers.
Therefore the peer-validity gate does not kill the old peer network, but it prevents
us from claiming that the main result is robust to the strongest available peer
definition.
```

Manual-coding note:

```text
Two independent LLM-assisted coding passes were completed on the same 150-pair
template. Direct-peer agreement is moderate, not perfect:

    overall direct agreement = 0.6533
    overall direct kappa     = 0.3240

The two-coder mean ranking is:

    annual same-industry text Top5       = 0.7167 direct-peer share
    CSMAR scope Top5                     = 0.6500
    annual global AI-word-stripped Top5  = 0.6000
    random same-industry Top5            = 0.4667
    low-similarity same-industry Top5    = 0.2333

This supports "CSMAR is inspectable and better than weak placebos," not "CSMAR is
unambiguously best."
```
