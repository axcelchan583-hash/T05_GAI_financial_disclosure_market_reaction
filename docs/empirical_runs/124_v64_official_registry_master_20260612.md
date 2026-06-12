# v64 official CAC registry master through 2026-06-12

## Purpose

Build a complete local registry list for the new sample-construction path based on official CAC filing sources, refreshed on 2026-06-12.

The registry has three public official components:

1. CAC GenAI service filing / registration list.
2. CAC domestic internet information service algorithm filing list.
3. CAC domestic deep-synthesis service algorithm filing list.

The local CSMAR `AI_AlgorithmInfo.xlsx` workbook is used only as a validation and system-snapshot supplement. The proprietary workbook is not copied into the repo.

## Source Coverage

| source | local rows | latest official batch found on 2026-06-12 | note |
|---|---:|---|---|
| CAC GenAI service filing / registration | 1,358 | 2026-04 | Official GenAI service page still had 11 attachments; no 2026-06 attachment. |
| CAC ordinary algorithm filing | 938 | 2026-05 | Official algorithm page had 18 attachments; no 2026-06 / attachment 19. |
| CAC deep-synthesis algorithm filing | 7,059 | 2026-05 | Beian notice list had 17 deep-synthesis batches; no 2026-06 notice. |
| Local CSMAR algorithm system snapshot | 7,311 | 2026-03 | Used as a cross-check and full system snapshot through 2026-03. |

Official ordinary algorithm + deep-synthesis algorithm rows through 2026-03 equal the CSMAR snapshot row count:

| comparison | rows |
|---|---:|
| official ordinary algorithm + deep-synthesis through 2026-03 | 7,311 |
| CSMAR algorithm system snapshot through 2026-03 | 7,311 |
| official post-CSMAR batch added from 2026-05 | 686 |

## Outputs

Main output directory:

`results/v64_official_registry_master_20260612/`

Key files:

| file | rows | use |
|---|---:|---|
| `official_registry_master.csv` | 9,355 | Public official registry master: GenAI service + ordinary algorithm + deep-synthesis algorithm. |
| `official_registry_master_genai_relevant_subset.csv` | 8,504 | Public official GenAI-relevant subset: all GenAI service, all deep-synthesis, and keyword/type hits from ordinary algorithm filings. |
| `expanded_registry_master_with_csmar.csv` | 9,355 | Uses CSMAR system snapshot through 2026-03, then adds official 2026-05 ordinary/deep-synthesis batches; same row count as official master after the extraction fix. |
| `expanded_registry_master_with_csmar_genai_relevant_subset.csv` | 8,505 | Same expanded logic, but with GenAI-relevant filter. |
| `coverage_manifest.csv` | 4 | Source-level coverage and caveats. |
| `summary_by_source_batch.csv` | 49 | Source x batch x GenAI-relevant counts. |

## Repro Commands

Use the bundled Python for scripts that read Office documents:

```bash
python3 scripts/download_cac_genai_service_filing.py
python3 scripts/extract_cac_genai_service_filing_tables.py
python3 scripts/download_cac_algorithm_filing.py
/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/extract_cac_algorithm_filing_tables.py
python3 scripts/download_cac_deep_synthesis_filing.py
/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/extract_cac_deep_synthesis_filing_tables.py
/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/extract_csmar_algorithm_info_20260612.py
python3 scripts/build_v64_official_registry_master_20260612.py
```

## Design Note

For the rescue path, use `official_registry_master.csv` as the auditable registry universe. For listed-firm matching, the strictest first pass should start from:

- `registry_source == cac_genai_service`, because it is explicitly GenAI service filing / registration;
- `registry_source == cac_deep_synthesis_filing`, because it is the official deep-synthesis algorithm registry and captures most model/app generation records;
- the 87 GenAI-relevant ordinary algorithm rows only as an auxiliary recall channel.

This gives a much larger and more defensible registry-side universe than CNINFO disclosure keywords alone, while preserving source labels and filing numbers for exact matching.
