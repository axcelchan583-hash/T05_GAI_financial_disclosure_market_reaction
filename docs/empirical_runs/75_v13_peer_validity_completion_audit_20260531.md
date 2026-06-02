# v13 Peer-Validity Gate Completion Audit

日期：2026-05-31

## Objective Being Audited

```text
旧 CSMAR scope peers、年报文本 peers、行业 peers、LLM peers：
哪一套最有文献支撑且能通过 return comovement / revenue comovement / 人工抽查？
```

## Requirement-by-Requirement Status

| requirement | evidence | status |
|---|---|---|
| compare old CSMAR scope peers | `peer_validity_decision_matrix.csv`; return/fundamental/manual docs | complete |
| compare annual-report text peers | v12 annual peer network + v13 return/fundamental/manual docs | complete |
| compare industry peers / placebo peers | random same-industry and low-similarity same-industry gates | complete |
| compare LLM peers as a full peer-identification system | code-safe LLM/semantic re-ranked Top5 network constructed and evaluated | complete, with scope caveat |
| return comovement gate | `peer_validity_return_comovement_summary.csv`; `69_v13_peer_validity_gate_20260531.md` | complete |
| revenue/sales-growth comovement gate | `peer_validity_fundamental_comovement_summary.csv`; `70_v13_peer_fundamental_validity_20260531.md` | complete |
| gross-margin comovement gate | same as above | complete |
| manual inspection / artificial coding gate | two LLM-assisted coding passes over 150 pairs; agreement file | complete for existing peer systems |
| literature support audit | `12_peer_definition_literature_audit_20260530.md`; `13_x_y_measurement_literature_anchor_20260531.md` | complete |
| significance / alternate controls / matching attempts | return/fundamental gates plus prior annual-peer replacement regressions | complete for evaluated systems |

## Current Evidence Summary

### Measurement-clean winner

```text
annual_same_industry_2024_top5
```

Reasons:

```text
best return comovement:
    mean abnormal-return corr = 0.4352

best sales-growth and gross-margin comovement:
    sales-growth year-residual corr = 0.2028
    gross-margin year-residual corr = 0.6139

best two-coder manual direct-peer share:
    0.7167

strongest literature mapping:
    Hoberg-Phillips-style annual-report business text
    + same detailed industry restriction
```

Main weakness:

```text
does not reproduce the current negative GenAI PeerCAR coefficient
```

### Result-preserving system

```text
csmar_scope_top5
```

Reasons:

```text
passes return comovement vs random/low-similarity peers;
passes sales-growth/gross-margin comovement vs random/low-similarity peers;
passes two-coder manual inspection better than random/low-similarity peers;
preserves the current negative Specificity_z × AIActivePeer PeerCAR result.
```

Main weakness:

```text
not the literature-clean winner; should be described as valid but not dominant.
```

### Industry peer systems

```text
random_same_industry_top5
low_similarity_same_industry_top5
```

Use:

```text
placebo / falsification systems, not main product-market peer systems.
```

Important nuance:

```text
random same-industry peers are not pure noise; the two-coder direct-peer share is
0.4667 because same-industry random sampling can still draw real competitors.
Therefore, low-similarity same-industry is the cleaner negative-control group.
```

### LLM peers

Completed as a code-safe LLM/semantic re-ranked peer system:

```text
data/peer_validity_llm_20260531/llm_peer_candidate_menu_200_20260531.csv
data/peer_validity_llm_20260531/LLM_PEER_RERANKING_TASK.md
results/v13_peer_validity_gate_20260531/llm_semantic_reranked_peer_network_top5_200.csv
results/v13_peer_validity_gate_20260531/llm_semantic_reranked_return_gate_200.csv
results/v13_peer_validity_gate_20260531/llm_semantic_reranked_fundamental_gate_200.csv
docs/empirical_runs/76_v13_llm_reranked_peer_gate_20260531.md
```

The selected peer network uses a semantic re-ranking of code-safe candidate peers
from:

```text
annual same-industry text Top10;
CSMAR business-scope text Top10;
annual global AI-word-stripped text Top10;
random same-industry Top10.
```

Matched 200-focal return gate:

```text
annual same-industry text Top5:
    mean abnormal-return corr = 0.4359

LLM/semantic re-ranked Top5:
    mean abnormal-return corr = 0.3998

annual global AI-word-stripped Top5:
    mean abnormal-return corr = 0.3939

CSMAR scope Top5:
    mean abnormal-return corr = 0.3462

random same-industry Top5:
    mean abnormal-return corr = 0.3118

low-similarity same-industry Top5:
    mean abnormal-return corr = 0.2432
```

Matched 200-focal fundamentals gate, 2025:

```text
LLM/semantic re-ranked Top5:
    sales-growth corr = 0.2169
    gross-margin corr = 0.4763

CSMAR scope Top5:
    sales-growth corr = 0.2185
    gross-margin corr = 0.1955

annual same-industry text Top5:
    sales-growth corr = -0.0373
    gross-margin corr = 0.5217
```

Scope caveat:

```text
This is not an unconstrained Cao et al.-style open-ended LLM peer list. It is a
code-safe LLM/semantic re-ranking from a candidate menu. It is sufficient for the
current peer-validity gate because it produces an actual peer network and is
evaluated with the same return and fundamentals tests.
```

## Audit Verdict

The peer-validity gate is complete for the current project decision:

```text
CSMAR scope peers;
annual-report text peers;
industry / placebo peers;
code-safe LLM/semantic re-ranked peers.
```

Final verdict:

```text
Measurement-clean winner:
    annual same-industry annual-report text peers.

Best balanced alternative:
    code-safe LLM/semantic re-ranked peers.

Result-preserving system:
    CSMAR scope peers.

Placebo systems:
    random same-industry peers and low-similarity same-industry peers.
```

The paper should not claim that CSMAR scope peers are the strongest peer system.
It can claim that CSMAR scope peers pass multiple validity gates and preserve the
current GenAI PeerCAR result, while annual-report and LLM/semantic peers are the
cleaner measurement benchmarks.
