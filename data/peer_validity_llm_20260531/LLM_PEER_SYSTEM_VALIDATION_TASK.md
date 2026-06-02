# Peer-System Validation Coding Task

Input: `data/peer_validity_llm_20260531/peer_system_validation_template_150_pairs_20260531.csv`

For each focal-peer pair, judge whether the peer is a direct product-market
competitor of the focal firm.

Score:
- 3 = close direct competitor: similar product/service and similar customer/use case.
- 2 = related product-market peer: same broad market, but products or customers differ.
- 1 = weakly related: same industry label or supply-chain relation, but not a direct competitor.
- 0 = not a product-market competitor.

Do not reward generic words such as "technology", "platform", "service", "digital",
"AI", or "intelligent" unless the actual products or customers overlap.

Fill:
- `human_competitor_score_0_to_3`
- `human_is_direct_product_market_peer_0_1` (1 if score is 2 or 3)
- `human_reason`

Output with the same rows:
`data/peer_validity_llm_20260531/peer_system_validation_coded_150_pairs_YYYYMMDD.csv`
