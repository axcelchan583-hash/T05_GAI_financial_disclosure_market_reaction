# v35 focal-peer two-component probe

## Scope

- Input: v33 supplement panel.
- Goal: evaluate Claude's two-component interpretation: common/contagion level effect plus competitive exposure gradient.
- `FocalCAR` is standardized focal firm CAR[0,+1] for PeerCAR models and standardized focal AR[0] for PeerAR models.
- `FocalCAR x Prox < 0` is the key competitive-gradient prediction.
- Peer-level Prox variables are also run with event FE; `Spec` is event-level, so its focal-CAR interaction is not identified under event FE.
- In event-FE rows, the focal-firm return level is omitted because it is event-level and absorbed by event FE.

## Headline Read

1. Claude's two-component interpretation is conceptually right: a GenAI disclosure can contain both a common/contagion signal and a peer-level competitive signal. The raw v33 focal-peer mirror and the v35 PeerAR[0] no-event-FE models support the existence of a positive common component.
2. The controlled PeerCAR[0,+1] level relation is only positive in direction, not statistically sharp after peer-industry-week FE and controls. Do not overstate the common-component test as a main result.
3. The desired competitive-gradient sign is not supported in this pass. `FocalMove x PeerSimilarity`, `FocalMove x Top3Peer`, and `FocalMove x AIActivePeer` are near zero or positive and insignificant.
4. `FocalMove x peer_industry_hhi_z` is the only negative lead in some PeerCAR specifications, but it is weak and not stable under event FE / pollution cleaning. Treat it as exploratory.
5. `FocalMove x Spec` is positive but insignificant. Since Spec is event-level, it is better interpreted as a possible common-signal moderator, not peer-level competition exposure.
6. Bottom line: keep Claude's decomposition as the framing for why raw focal-peer positive correlation does not kill the competition story, but do not use `FocalMove x Prox` as a finished mechanism table yet. The stronger current evidence remains: pollution cleaning, CAR[0,+1] persistence, long-window non-reversal, analyst forecast revision, and the existing event-FE `Spec x AIActivePeer` result.

## Main PeerCAR Results: All Sample

| sample   | outcome       | prox                | fe                             | FocalMove   |   FocalMove x Prox |   interaction_p |   nobs |   events |   peer_firms |
|:---------|:--------------|:--------------------|:-------------------------------|:------------|-------------------:|----------------:|-------:|---------:|-------------:|
| all      | PeerCAR[0,+1] | peer_similarity_z   | no_event_fe_peer_industry_week | 0.0035      |             0.0003 |          0.8257 |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | peer_similarity_z   | event_fe                       |             |            -0.0004 |          0.7514 |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | top3_peer           | no_event_fe_peer_industry_week | 0.0035      |             0.0006 |          0.7457 |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | top3_peer           | event_fe                       |             |             0.0006 |          0.7246 |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | ai                  | no_event_fe_peer_industry_week | 0.0022      |             0.0019 |          0.2725 |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | ai                  | event_fe                       |             |             0.0008 |          0.6329 |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | peer_industry_hhi_z | no_event_fe_peer_industry_week | -0.0099     |            -0.022  |          0.1777 |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | peer_industry_hhi_z | event_fe                       |             |            -0.003  |          0.797  |   2421 |      270 |         1250 |
| all      | PeerCAR[0,+1] | spec_z              | no_event_fe_peer_industry_week | 0.0038      |             0.0024 |          0.6243 |   2421 |      270 |         1250 |

## Main PeerCAR Results: Drop Peer GenAI Or Major Announcement

| sample              | outcome       | prox                | fe                             | FocalMove   |   FocalMove x Prox |   interaction_p |   nobs |   events |   peer_firms |
|:--------------------|:--------------|:--------------------|:-------------------------------|:------------|-------------------:|----------------:|-------:|---------:|-------------:|
| drop_genai_or_major | PeerCAR[0,+1] | peer_similarity_z   | no_event_fe_peer_industry_week | 0.0033      |             0.0017 |          0.2792 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | peer_similarity_z   | event_fe                       |             |             0.0016 |          0.3183 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | top3_peer           | no_event_fe_peer_industry_week | 0.0037      |             0.001  |          0.6165 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | top3_peer           | event_fe                       |             |             0.0005 |          0.7903 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | ai                  | no_event_fe_peer_industry_week | 0.0026      |             0.0018 |          0.3601 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | ai                  | event_fe                       |             |             0.0015 |          0.4519 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | peer_industry_hhi_z | no_event_fe_peer_industry_week | -0.0171     |            -0.0334 |          0.1561 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | peer_industry_hhi_z | event_fe                       |             |             0.0343 |          0.1992 |   1617 |      264 |          933 |
| drop_genai_or_major | PeerCAR[0,+1] | spec_z              | no_event_fe_peer_industry_week | 0.0041      |             0.0027 |          0.6658 |   1617 |      264 |          933 |

## Main PeerAR Results: All Sample

| sample   | outcome   | prox                | fe                             | FocalMove   |   FocalMove x Prox |   interaction_p |   nobs |   events |   peer_firms |
|:---------|:----------|:--------------------|:-------------------------------|:------------|-------------------:|----------------:|-------:|---------:|-------------:|
| all      | PeerAR[0] | peer_similarity_z   | no_event_fe_peer_industry_week | 0.0065***   |            -0.0001 |          0.9114 |   2473 |      278 |         1268 |
| all      | PeerAR[0] | peer_similarity_z   | event_fe                       |             |            -0.0001 |          0.95   |   2473 |      278 |         1268 |
| all      | PeerAR[0] | top3_peer           | no_event_fe_peer_industry_week | 0.0065***   |            -0.0004 |          0.7589 |   2473 |      278 |         1268 |
| all      | PeerAR[0] | top3_peer           | event_fe                       |             |            -0.0004 |          0.7612 |   2473 |      278 |         1268 |
| all      | PeerAR[0] | ai                  | no_event_fe_peer_industry_week | 0.0056**    |             0.0012 |          0.2072 |   2473 |      278 |         1268 |
| all      | PeerAR[0] | ai                  | event_fe                       |             |             0.0009 |          0.3003 |   2473 |      278 |         1268 |
| all      | PeerAR[0] | peer_industry_hhi_z | no_event_fe_peer_industry_week | 0.0072***   |             0.0013 |          0.6935 |   2473 |      278 |         1268 |
| all      | PeerAR[0] | peer_industry_hhi_z | event_fe                       |             |            -0.0081 |          0.1329 |   2473 |      278 |         1268 |
| all      | PeerAR[0] | spec_z              | no_event_fe_peer_industry_week | 0.0063***   |             0.0006 |          0.8236 |   2473 |      278 |         1268 |

## Main PeerAR Results: Drop Peer GenAI Or Major Announcement

| sample              | outcome   | prox                | fe                             | FocalMove   |   FocalMove x Prox |   interaction_p |   nobs |   events |   peer_firms |
|:--------------------|:----------|:--------------------|:-------------------------------|:------------|-------------------:|----------------:|-------:|---------:|-------------:|
| drop_genai_or_major | PeerAR[0] | peer_similarity_z   | no_event_fe_peer_industry_week | 0.0065**    |             0.0018 |          0.2249 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | peer_similarity_z   | event_fe                       |             |             0.0027 |          0.1174 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | top3_peer           | no_event_fe_peer_industry_week | 0.0069**    |             0.0011 |          0.3846 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | top3_peer           | event_fe                       |             |             0.0015 |          0.2766 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | ai                  | no_event_fe_peer_industry_week | 0.0061**    |             0.0018 |          0.1431 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | ai                  | event_fe                       |             |             0.0014 |          0.2085 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | peer_industry_hhi_z | no_event_fe_peer_industry_week | 0.0106***   |             0.0053 |          0.4285 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | peer_industry_hhi_z | event_fe                       |             |             0.0005 |          0.9656 |   1654 |      272 |          948 |
| drop_genai_or_major | PeerAR[0] | spec_z              | no_event_fe_peer_industry_week | 0.0074***   |             0.0001 |          0.9673 |   1654 |      272 |          948 |

## Output Files

- `results/v35_focal_peer_two_component_probe_20260605/focal_peer_two_component_regressions.csv`
- `results/v35_focal_peer_two_component_probe_20260605/focal_peer_two_component_compact.csv`