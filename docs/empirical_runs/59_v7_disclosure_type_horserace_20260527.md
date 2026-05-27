# V7 Disclosure-Type Horse-Race

Date: 2026-05-27

## Purpose

This run splits focal GenAI disclosures into rough disclosure types and reruns the current Top5 peer-CAR framework.

Types:

- `own_impl`: focal firm describes its own GenAI implementation, deployment, product, model, or application.
- `supply_chain`: focal firm frames itself as exposed to AI/large-model demand through compute, data centers, semiconductors, optical modules, cooling, terminals, or data resources.
- `generic_attention`: focal firm gives generic AI/GenAI attention language without own implementation or supply-chain exposure.
- `denial_no_current`: focal firm denies current involvement or says it has no current GenAI business/cooperation.

Main interpretation target is not the average event effect, but `type × AIActivePeer` inside the existing peer-revaluation design.

## Sample and Type Counts

Top5 first focal GenAI event, announcement-cleaned, market-model `PeerCAR[0,+1]`.

| type              |   events |   event_share |   obs |   obs_share |   mean_specificity_z_events |
|:------------------|---------:|--------------:|------:|------------:|----------------------------:|
| own_impl          |     1526 |        0.701  |  5547 |      0.7107 |                      0.2376 |
| supply_chain      |      301 |        0.1383 |  1044 |      0.1338 |                     -0.1359 |
| generic_attention |      214 |        0.0983 |   751 |      0.0962 |                      0.0227 |
| denial_no_current |      251 |        0.1153 |   872 |      0.1117 |                      0.057  |

## Type x AIActive Only

Outcome: `PeerCAR[0,+1]`. FE: `event_id + peer_industry_week`. SE: two-way clustered by `event_id + peer_code`. Controls: `PeerCAR[-10,-2] + PeerCAR[-20,-2]`.

| ai_def               | model          | term                 | coef_se               |      p |   nobs |   events |   peer_firms |
|:---------------------|:---------------|:---------------------|:----------------------|-------:|-------:|---------:|-------------:|
| ext_any              | type_x_ai_only | own_impl_ai          | -0.000105 (0.001533)  | 0.9455 |   7805 |     2177 |         3345 |
| ext_any              | type_x_ai_only | supply_chain_ai      | -0.000401 (0.003761)  | 0.915  |   7805 |     2177 |         3345 |
| ext_any              | type_x_ai_only | generic_attention_ai | 0.007788** (0.003875) | 0.0445 |   7805 |     2177 |         3345 |
| ext_any              | type_x_ai_only | denial_no_current_ai | 0.002026 (0.003534)   | 0.5664 |   7805 |     2177 |         3345 |
| current_text_history | type_x_ai_only | own_impl_ai          | -0.001837 (0.001402)  | 0.19   |   7805 |     2177 |         3345 |
| current_text_history | type_x_ai_only | supply_chain_ai      | -0.000233 (0.003699)  | 0.9498 |   7805 |     2177 |         3345 |
| current_text_history | type_x_ai_only | generic_attention_ai | -0.002011 (0.004539)  | 0.6577 |   7805 |     2177 |         3345 |
| current_text_history | type_x_ai_only | denial_no_current_ai | -0.006600 (0.004254)  | 0.1208 |   7805 |     2177 |         3345 |

## Specificity plus Type x AIActive Horse-Race

This table asks whether disclosure-type interactions absorb the original `Specificity_z × AIActivePeer` effect.

| ai_def               | model                      | term                 | coef_se                |      p |   nobs |   events |   peer_firms |
|:---------------------|:---------------------------|:---------------------|:-----------------------|-------:|-------:|---------:|-------------:|
| ext_any              | specificity_plus_type_x_ai | spec_ai              | -0.002394** (0.000986) | 0.0152 |   7805 |     2177 |         3345 |
| ext_any              | specificity_plus_type_x_ai | own_impl_ai          | 0.003174 (0.005590)    | 0.5701 |   7805 |     2177 |         3345 |
| ext_any              | specificity_plus_type_x_ai | supply_chain_ai      | -0.000669 (0.003813)   | 0.8607 |   7805 |     2177 |         3345 |
| ext_any              | specificity_plus_type_x_ai | generic_attention_ai | 0.010812 (0.006664)    | 0.1047 |   7805 |     2177 |         3345 |
| ext_any              | specificity_plus_type_x_ai | denial_no_current_ai | 0.005374 (0.006350)    | 0.3973 |   7805 |     2177 |         3345 |
| current_text_history | specificity_plus_type_x_ai | spec_ai              | -0.002107** (0.001050) | 0.0448 |   7805 |     2177 |         3345 |
| current_text_history | specificity_plus_type_x_ai | own_impl_ai          | -0.005657 (0.004951)   | 0.2532 |   7805 |     2177 |         3345 |
| current_text_history | specificity_plus_type_x_ai | supply_chain_ai      | -0.001965 (0.003713)   | 0.5967 |   7805 |     2177 |         3345 |
| current_text_history | specificity_plus_type_x_ai | generic_attention_ai | -0.006430 (0.006478)   | 0.3209 |   7805 |     2177 |         3345 |
| current_text_history | specificity_plus_type_x_ai | denial_no_current_ai | -0.009805 (0.006541)   | 0.1339 |   7805 |     2177 |         3345 |

## Type-Specific Specificity x AIActive

This table asks whether specificity matters more inside a particular disclosure type.

| ai_def               | model                          | term                      | coef_se                 |      p |   nobs |   events |   peer_firms |
|:---------------------|:-------------------------------|:--------------------------|:------------------------|-------:|-------:|---------:|-------------:|
| ext_any              | type_specific_specificity_x_ai | own_impl_spec_ai          | -0.002194* (0.001233)   | 0.0753 |   7805 |     2177 |         3345 |
| ext_any              | type_specific_specificity_x_ai | supply_chain_spec_ai      | 0.000393 (0.003695)     | 0.9153 |   7805 |     2177 |         3345 |
| ext_any              | type_specific_specificity_x_ai | generic_attention_spec_ai | 0.000305 (0.003690)     | 0.9341 |   7805 |     2177 |         3345 |
| ext_any              | type_specific_specificity_x_ai | denial_no_current_spec_ai | -0.003792 (0.002333)    | 0.104  |   7805 |     2177 |         3345 |
| current_text_history | type_specific_specificity_x_ai | own_impl_spec_ai          | 0.000252 (0.001227)     | 0.8372 |   7805 |     2177 |         3345 |
| current_text_history | type_specific_specificity_x_ai | supply_chain_spec_ai      | -0.001295 (0.003257)    | 0.691  |   7805 |     2177 |         3345 |
| current_text_history | type_specific_specificity_x_ai | generic_attention_spec_ai | -0.009524*** (0.003195) | 0.0029 |   7805 |     2177 |         3345 |
| current_text_history | type_specific_specificity_x_ai | denial_no_current_spec_ai | -0.004849** (0.002332)  | 0.0376 |   7805 |     2177 |         3345 |

## Average Peer Effect without Event FE

This is descriptive only. It uses `focal_industry_week + peer_industry_week` FE, not event FE, because event FE would absorb focal-event type flags.

| term                           | coef_se               |      p |   nobs |   events |   peer_firms |
|:-------------------------------|:----------------------|-------:|-------:|---------:|-------------:|
| own_genai_implementation_regex | -0.000741 (0.002718)  | 0.7852 |   7805 |     2177 |         3345 |
| ai_supply_chain_exposure       | 0.004225** (0.001899) | 0.0261 |   7805 |     2177 |         3345 |
| generic_ai_attention_regex     | 0.001109 (0.003352)   | 0.7408 |   7805 |     2177 |         3345 |
| denial_no_current_regex        | 0.000416 (0.003196)   | 0.8964 |   7805 |     2177 |         3345 |

## Reading Rule

- If `own_impl_ai` is negative and stronger than `supply_chain_ai`, the evidence supports the competitive-risk interpretation.
- If `supply_chain` is positive in the no-event-FE table but not negative in `type × AIActive`, it supports category validation rather than competitive threat.
- If `spec_ai` remains negative after adding type interactions, the original specificity signal is not merely a disguised disclosure-type dummy.
