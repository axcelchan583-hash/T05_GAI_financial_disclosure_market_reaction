# LLM Peer Re-Ranking Task

Input: `data/peer_validity_llm_20260531/llm_peer_candidate_menu_200_20260531.csv`

For each `focal_code`, review the candidate peer list. Select up to five direct
product-market peers from the candidates and fill:

- `llm_selected_rank_1_to_5`: 1 to 5 for selected peers, blank otherwise.
- `llm_is_direct_product_market_peer_0_1`: 1 if the candidate is a product-market
  competitor, 0 otherwise.
- `llm_reason`: one short reason.

Rules:
- Product-market peer means similar products/services sold to similar customers
  or use cases.
- Do not select supply-chain complements unless they directly compete in the end
  product market.
- Do not reward generic terms such as technology, platform, service, AI, digital,
  intelligent, or solution unless the product/customer overlap is concrete.
- Prefer candidates with observable product/customer overlap over candidates
  that merely share the same CSRC industry.

Output:
`data/peer_validity_llm_20260531/llm_peer_candidate_menu_coded_200_YYYYMMDD.csv`

After coding, the selected rows can be converted into an LLM-re-ranked peer
network and evaluated with the same return/fundamental gates.
