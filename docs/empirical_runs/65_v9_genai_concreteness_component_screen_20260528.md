# V9 GenAI Concreteness Component Screen

Date: 2026-05-28

## Purpose

The full Hope/Cheng-style continuous density X did not reproduce the legacy `specificity_z x AIActivePeer` result. This screen checks whether a specific component of the new measurement has signal.

Specification for continuous components:

`PeerCAR[0,+1] ~ AIActive + Component_z x AIActive + PeerCAR[-10,-2] + PeerCAR[-20,-2] + event FE + peer industry-week FE`

SE: two-way clustered by `event_id + peer_code`.

## Top Continuous Component Results

| ai_def               | x_col                                       | coef_se              |      p |   nobs |   events |   peer_firms |
|:---------------------|:--------------------------------------------|:---------------------|-------:|-------:|---------:|-------------:|
| current_text_history | ai_keyword_count_z_event                    | -0.001579 (0.000997) | 0.1134 |   7805 |     2177 |         3345 |
| current_text_history | quant_concrete_count_z_event                | -0.001119 (0.000851) | 0.1883 |   7805 |     2177 |         3345 |
| ext_any              | log1p_operational_concrete_count_z_event    | -0.000986 (0.001167) | 0.3979 |   7805 |     2177 |         3345 |
| current_text_history | log1p_quant_concrete_count_z_event          | -0.000795 (0.000988) | 0.4209 |   7805 |     2177 |         3345 |
| ext_any              | genai_concreteness_char_density_z_event     | -0.000927 (0.001174) | 0.4296 |   7805 |     2177 |         3345 |
| ext_any              | genai_concreteness_raw_z_event              | -0.000903 (0.001209) | 0.4549 |   7805 |     2177 |         3345 |
| ext_any              | ai_keyword_count_z_event                    | 0.000778 (0.001180)  | 0.5095 |   7805 |     2177 |         3345 |
| ext_any              | operational_concrete_count_z_event          | -0.000645 (0.001026) | 0.5295 |   7805 |     2177 |         3345 |
| current_text_history | log1p_operational_concrete_count_z_event    | -0.000586 (0.001078) | 0.587  |   7805 |     2177 |         3345 |
| ext_any              | log1p_total_concrete_count_z_event          | -0.000609 (0.001151) | 0.5967 |   7805 |     2177 |         3345 |
| current_text_history | operational_concrete_count_z_event          | -0.000502 (0.000979) | 0.6085 |   7805 |     2177 |         3345 |
| current_text_history | log1p_total_concrete_count_z_event          | -0.000542 (0.001071) | 0.613  |   7805 |     2177 |         3345 |
| current_text_history | total_concrete_count_z_event                | -0.000398 (0.000945) | 0.6738 |   7805 |     2177 |         3345 |
| ext_any              | log1p_positive_genai_sentence_count_z_event | -0.000392 (0.001139) | 0.7309 |   7805 |     2177 |         3345 |
| ext_any              | genai_token_count_z_event                   | 0.000355 (0.001130)  | 0.7536 |   7805 |     2177 |         3345 |
| ext_any              | log1p_entity_concrete_count_z_event         | -0.000342 (0.001141) | 0.7645 |   7805 |     2177 |         3345 |
| ext_any              | positive_genai_sentence_count_z_event       | -0.000285 (0.001100) | 0.7954 |   7805 |     2177 |         3345 |
| current_text_history | log1p_entity_concrete_count_z_event         | -0.000260 (0.001051) | 0.8046 |   7805 |     2177 |         3345 |
| ext_any              | total_concrete_count_z_event                | -0.000237 (0.001039) | 0.8197 |   7805 |     2177 |         3345 |
| ext_any              | entity_concrete_count_z_event               | 0.000175 (0.001093)  | 0.8725 |   7805 |     2177 |         3345 |
| current_text_history | genai_concreteness_char_density_z_event     | -0.000164 (0.001074) | 0.8788 |   7805 |     2177 |         3345 |
| current_text_history | log1p_positive_genai_sentence_count_z_event | -0.000118 (0.001086) | 0.9132 |   7805 |     2177 |         3345 |
| current_text_history | genai_concreteness_raw_z_event              | -0.000108 (0.001048) | 0.9182 |   7805 |     2177 |         3345 |
| current_text_history | positive_genai_sentence_count_z_event       | 0.000102 (0.001035)  | 0.9215 |   7805 |     2177 |         3345 |
| current_text_history | genai_token_count_z_event                   | 0.000111 (0.001133)  | 0.9219 |   7805 |     2177 |         3345 |
| current_text_history | entity_concrete_count_z_event               | -0.000091 (0.000959) | 0.9248 |   7805 |     2177 |         3345 |
| ext_any              | log1p_quant_concrete_count_z_event          | -0.000065 (0.000993) | 0.9482 |   7805 |     2177 |         3345 |
| ext_any              | quant_concrete_count_z_event                | -0.000055 (0.001143) | 0.9618 |   7805 |     2177 |         3345 |

## Binary Cheng-Style Content Flags

Each row is the coefficient on `content_flag x AIActive`, estimated jointly with the other content flags.

| ai_def               | x_col                              | coef_se               |      p |   nobs |   events |   peer_firms |
|:---------------------|:-----------------------------------|:----------------------|-------:|-------:|---------:|-------------:|
| ext_any              | competitive_risk_content_ai        | -0.015718* (0.008496) | 0.0643 |   7805 |     2177 |         3345 |
| ext_any              | speculative_or_generic_content_ai  | 0.004875 (0.004722)   | 0.3019 |   7805 |     2177 |         3345 |
| current_text_history | category_validation_content_ai     | 0.004006 (0.004602)   | 0.384  |   7805 |     2177 |         3345 |
| ext_any              | substantive_or_existing_content_ai | 0.009937 (0.013843)   | 0.4729 |   7805 |     2177 |         3345 |
| ext_any              | category_validation_content_ai     | 0.002724 (0.004117)   | 0.5083 |   7805 |     2177 |         3345 |
| current_text_history | speculative_or_generic_content_ai  | 0.002519 (0.003978)   | 0.5266 |   7805 |     2177 |         3345 |
| ext_any              | positive_genai_claim_content_ai    | 0.006320 (0.011056)   | 0.5676 |   7805 |     2177 |         3345 |
| current_text_history | positive_genai_claim_content_ai    | 0.004253 (0.012619)   | 0.7361 |   7805 |     2177 |         3345 |
| current_text_history | substantive_or_existing_content_ai | -0.004690 (0.016618)  | 0.7778 |   7805 |     2177 |         3345 |
| current_text_history | denial_or_no_exposure_content_ai   | 0.000667 (0.003149)   | 0.8323 |   7805 |     2177 |         3345 |
| current_text_history | competitive_risk_content_ai        | 0.001598 (0.010197)   | 0.8755 |   7805 |     2177 |         3345 |
| ext_any              | denial_or_no_exposure_content_ai   | -0.000354 (0.003090)  | 0.9089 |   7805 |     2177 |         3345 |

## Interpretation

This is a diagnostic screen, not a final table. Its purpose is to decide whether the new X should be refined around a specific component, kept only as validation, or abandoned as the headline X.

