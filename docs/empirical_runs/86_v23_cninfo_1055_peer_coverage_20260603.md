# v23 CNINFO 1055 peer coverage audit

## Purpose

This run checks whether the 1055 CNINFO GenAI disclosure candidates can be connected to prior T05 product-market peer definitions. It is a coverage audit only; it does not estimate peer abnormal returns.

## Inputs

- Event source: `T05-qian-supplier-replication-cn/results/v27_cninfo_priority_pdf_audit_2023_2026_20260603/manual_review_priority_pdf_all.csv`.
- Event date: `manual_event_date_corrected` if available, otherwise `announcement_date`.
- Time-valid annual networks keep the latest `snapshot_report_year <= event_year - 1`.
- Static LLM/semantic networks are reported as coverage diagnostics only because they are not event-year rolling networks.

## Sample counts

| sample | events | focal firms |
|---|---:|---:|
| all_1055 | 1055 | 640 |
| likely_106 | 106 | 91 |
| possible_or_backfill_921 | 921 | 575 |

All-1055 automatic PDF labels:

| auto label | events | focal firms |
|---|---:|---:|
| review_denial_or_uncertain | 285 | 229 |
| review_possible_initiative | 285 | 219 |
| review_backfill_or_support_doc | 270 | 213 |
| likely_qian_initiative | 106 | 91 |
| review_action_context_unclear_actor | 81 | 73 |
| exclude_no_fulltext_genai | 20 | 20 |
| exclude_mention_without_initiative | 8 | 6 |

## Main coverage result

Strict prior-year peer networks on all 1055 events:

| method | linked events | event link rate | linked focal firms | peer-event obs | unique peers |
|---|---:|---:|---:|---:|---:|
| liu_product_tfidf_global_top20 | 870 | 0.825 | 513 | 17400 | 3013 |
| ren_wang_binary_global_top20 | 870 | 0.825 | 513 | 17400 | 2816 |
| liu_product_tfidf_same_industry_d_top20 | 870 | 0.825 | 513 | 16934 | 3016 |
| ren_wang_binary_same_industry_d_top20 | 870 | 0.825 | 513 | 16934 | 3029 |
| annual_report_global_ai_stripped_top10 | 870 | 0.825 | 513 | 8700 | 2111 |
| annual_report_global_top10 | 870 | 0.825 | 513 | 8700 | 2110 |
| liu_product_tfidf_global_top10 | 870 | 0.825 | 513 | 8700 | 2173 |
| ren_wang_binary_global_top10 | 870 | 0.825 | 513 | 8700 | 2033 |

Static/LLM coverage diagnostics on all 1055 events:

| method | linked events | event link rate | linked focal firms | peer-event obs | unique peers |
|---|---:|---:|---:|---:|---:|
| csmar_scope_product_text_top10 | 883 | 0.837 | 516 | 8830 | 2426 |
| full_semantic_reranked_top10 | 883 | 0.837 | 516 | 8830 | 2374 |
| csmar_scope_semantic_only_top10 | 883 | 0.837 | 516 | 8331 | 2339 |
| csmar_scope_product_text_top5 | 883 | 0.837 | 516 | 4415 | 1565 |
| full_semantic_reranked_top5 | 883 | 0.837 | 516 | 4415 | 1499 |
| placebo_low_similarity_top5 | 883 | 0.837 | 516 | 4415 | 1614 |
| placebo_random_top5 | 883 | 0.837 | 516 | 4415 | 1586 |
| csmar_scope_semantic_only_top5 | 883 | 0.837 | 516 | 4411 | 1531 |

Likely-Qian subset coverage:

| method | linked events | event link rate | linked focal firms | peer-event obs | unique peers |
|---|---:|---:|---:|---:|---:|
| csmar_scope_product_text_top10 | 91 | 0.858 | 78 | 910 | 638 |
| full_semantic_reranked_top10 | 91 | 0.858 | 78 | 910 | 627 |
| csmar_scope_semantic_only_top10 | 91 | 0.858 | 78 | 874 | 614 |
| csmar_scope_product_text_top5 | 91 | 0.858 | 78 | 455 | 349 |
| csmar_scope_semantic_only_top5 | 91 | 0.858 | 78 | 455 | 333 |
| full_semantic_reranked_top5 | 91 | 0.858 | 78 | 455 | 343 |
| placebo_low_similarity_top5 | 91 | 0.858 | 78 | 455 | 351 |
| placebo_random_top5 | 91 | 0.858 | 78 | 455 | 344 |

## Interpretation

- The best strict prior-year peer network links 870 of 1055 events (82.5%) and 513 focal firms.
- The best static diagnostic network links 883 of 1055 events (83.7%); this is useful for design triage but should not be used as a clean event-time design without rebuilding as rolling/as-of peers.
- Compared with listed-supplier links, product-market peers are expected to be much less sparse because every A-share focal firm can in principle have listed product peers.

## Output files

- `results/v23_cninfo_1055_peer_coverage_20260603/peer_coverage_summary.csv`
- `results/v23_cninfo_1055_peer_coverage_20260603/auto_label_peer_coverage_summary.csv`
- `results/v23_cninfo_1055_peer_coverage_20260603/year_peer_coverage_summary.csv`
- `results/v23_cninfo_1055_peer_coverage_20260603/event_peer_counts_by_method.csv`
- `results/v23_cninfo_1055_peer_coverage_20260603/peer_link_panel.csv.gz`
- `results/v23_cninfo_1055_peer_coverage_20260603/network_inventory.csv`
