# v13 LLM Peer Candidate Menu

日期：2026-05-31

## Purpose

The current peer-validity gate has evaluated CSMAR scope peers, annual-report
text peers, and industry placebo peers. A strict LLM-generated peer system is not
yet available. This file makes that step executable without allowing the LLM to
hallucinate stock codes.

## Outputs

```text
data/peer_validity_llm_20260531/llm_peer_candidate_menu_200_20260531.csv
data/peer_validity_llm_20260531/LLM_PEER_RERANKING_TASK.md
```

## Candidate Sources

For each of 200 focal firms, candidates are drawn from:

```text
annual same-industry text Top10;
CSMAR business-scope text Top10;
annual global AI-word-stripped text Top10;
random same-industry Top10.
```

The intended LLM task is to re-rank/select Top5 direct product-market peers from
this candidate menu. The resulting selected rows can then be evaluated using the
same return-comovement and fundamentals-comovement scripts.

## Status

This prepares the LLM-peer construction gate. It is not yet a completed
LLM-generated peer network until the candidate menu is coded.
