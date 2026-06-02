# LLM Peer Coding Task

Input: `data/peer_validity_llm_20260531/llm_peer_request_template_200_20260531.csv`

For each focal Chinese A-share firm, identify up to five product-market competitors
from Chinese listed firms using only information that would be observable from
public business descriptions. Rank peers from closest to less close.

Coding rule:
- Product-market competitor means a firm selling similar products/services to similar customer groups.
- Do not choose supply-chain complements unless they directly compete in end products.
- Prefer A-share listed firms and fill stock code when known.
- If uncertain, leave the code blank but write the name and note uncertainty.

Output:
`data/peer_validity_llm_20260531/llm_peer_coded_200_YYYYMMDD.csv`
with the same columns filled.

This is for validating text-based peer systems, following the spirit of
Cao, Chen, Tucker, and Wan (2025, Review of Accounting Studies), not for
constructing the main variable by hand.
