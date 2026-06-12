# v67 Registry Firm-Product Master

## Scope

- Implements the first execution step for `15_registry_verified_adoption_experiment_design_v2_20260612.md`.
- Builds stable `registry_product_id = sha1(registry_source + filing_no)`.
- Adds `batch_public_date` and its precision/source flag.
- Keeps GenAI `已登记` as adoption verification, not self-developed model verification.

## Outputs

- `results/v67_registry_firm_product_master_20260612/registry_products_all.csv`
- `results/v67_registry_firm_product_master_20260612/registry_status_history.csv`
- `results/v67_registry_firm_product_master_20260612/registry_firm_product_candidates_all.csv`
- `results/v67_registry_firm_product_master_20260612/registry_firm_product_master.csv`
- `results/v67_registry_firm_product_master_20260612/registry_product_match_review_queue.csv`

## Counts

- Registry source rows: 8504
- Unique registry products: 8503
- Candidate firm-product pairs, all recall: 1418
- Preliminary high/medium firm-product master rows: 457
- Preliminary listed firms: 210

## Product Counts By Source

| registry_source | registry_status | verification_type | products | entities |
|---|---|---|---|---|
| cac_algorithm_filing | 备案清单 | ordinary_algorithm_genai_keyword | 87 | 82 |
| cac_deep_synthesis_filing | 备案清单 | deep_synthesis | 7058 | 4947 |
| cac_genai_service | 已备案 | self_filing | 847 | 784 |
| cac_genai_service | 已登记 | app_registration | 511 | 450 |

## Preliminary Listed Firm-Product Counts

| registry_source | registry_status | verification_type | firm_product_rows | products | firms |
|---|---|---|---|---|---|
| cac_algorithm_filing | 备案清单 | ordinary_algorithm_genai_keyword | 6 | 6 | 5 |
| cac_deep_synthesis_filing | 备案清单 | deep_synthesis | 316 | 315 | 170 |
| cac_genai_service | 已备案 | self_filing | 95 | 95 | 80 |
| cac_genai_service | 已登记 | app_registration | 40 | 40 | 33 |

## Batch Public Date Precision

| registry_source | batch_public_date_precision | products |
|---|---|---|
| cac_algorithm_filing | source_batch_month_end_proxy | 87 |
| cac_deep_synthesis_filing | official_notice_create_time | 7058 |
| cac_genai_service | official_page_date | 1169 |
| cac_genai_service | pdf_metadata_proxy | 189 |

## Candidate Match Counts

| match_confidence | match_scope | match_method | candidate_pairs | products | firms |
|---|---|---|---|---|---|
| high | entity_name | full_name_exact | 308 | 308 | 153 |
| low | entity_name | short_name_contained_len2 | 303 | 294 | 101 |
| low | entity_name | short_name_contained_len3 | 73 | 73 | 30 |
| low | entity_name | short_name_prefix_len2 | 61 | 60 | 28 |
| low | entity_name | short_name_prefix_risky_next_char | 1 | 1 | 1 |
| medium | entity_name | short_name_prefix_len4plus | 207 | 207 | 85 |
| medium | entity_name | short_name_contained_len4plus | 130 | 130 | 67 |
| medium | entity_name | short_name_prefix_len3 | 54 | 54 | 26 |
| medium | entity_name | full_name_contained | 8 | 8 | 5 |
| medium | entity_name | short_name_exact_entity | 1 | 1 | 1 |
| text_only_low | item_product_text | stock_short_in_item_text_len3 | 143 | 140 | 39 |
| text_only_low | item_product_text | stock_short_in_item_text_len4plus | 129 | 127 | 63 |

## Caveat

For GenAI service attachments 2024-08 and 2024-11, no separate CAC article page was found in the local archive; the first-public date uses PDF metadata proxy and is flagged accordingly. Ordinary algorithm filing dates use source-batch month-end proxy.
