# T05: GAI-assisted Disclosure Writing and Risk Disclosure Specificity

## Core Question

This project studies whether generative-AI-assisted financial disclosure writing changes the specificity and verifiability of corporate risk disclosure.

The focal treatment is not corporate AI capability, AI disclosure, or AI washing. It is the use of generative AI in preparing financial disclosure text.

## Current Preferred Branch

After the 2026-05-13 redesign, the preferred branch is no longer a same-firm
GenAI-adoption design. Same-firm adoption is too correlated with the focal
firm's own digital capability and organizational quality. The updated design
uses external network exposure:

```text
Customer / peer GenAI adoption
-> focal-firm follow-on GenAI adoption, capability upgrading, product/software outcomes
-> supply-chain disclosure and information-environment consequences
```

Main updated design note:

```text
docs/supply_chain_peer_design_update_20260513.md
```

The current preferred treatment is customer GenAI exposure:

```text
CustomerGenAIExposure_it
= sum_j w_ij,pre * PostFirstSpecificGenAIAdoption_jt
```

where customers are fixed using pre-event supply-chain links. The primary
outcome family is no longer one fragile Y. The pre-specified outcome hierarchy is:

1. focal firm's follow-on validated GenAI adoption;
2. AI-complementary hiring and knowledge-work upgrading;
3. GenAI-related software copyright, product launch, or patent outcomes;
4. supply-chain risk disclosure and analyst information-environment outcomes;
5. customer relationship and operating-resilience outcomes;
6. CAR and trading outcomes only as auxiliary validation.

## Older Same-firm DID Branch

After the 2026-05-11 design discussion, the preferred route is to learn from the GenAI-announcement event-sample construction in:

```text
/Users/mac/computerscience/23选题探索/bib/AI文本文献/The Impact of Generative AI Announcements on Suppliers_ Evidence From the Stock Market.pdf
```

The key idea is to construct a firm-level event library of first specific GenAI initiatives, then use the firm's first GenAI announcement as the treatment timing.

```text
RiskDisclosureSpecificity_it
= beta * TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
+ controls + firm FE + industry-year FE + eps_it
```

The treatment should be based on specific GenAI adoption, integration, deployment, or workflow-use announcements, not generic AI slogans or broad digital-transformation language.

As of the 2026-05-13 update, this branch is retained as a mechanism or robustness branch, not the main identification story.

The older public-shock exposure design remains a fallback or robustness branch:

```text
RiskDisclosureSpecificity_it
= beta * PostGenAI_t * PreRiskWritingBurden_i
+ controls + firm FE + year FE / industry-year FE + eps_it
```

Pre-period AI technical capability is not the main treatment. It is reserved for moderation or heterogeneity tests because old AI patents or AI technology foundations are not the same as GenAI-assisted disclosure writing.

## Current Folder Layout

- `docs/`: design notes, variable definitions, search plans, and pilot logs.
- `bib/`: paper records and citation files.
- `data/`: raw or interim data notes. Large raw data should be referenced by path rather than duplicated.
- `scripts/`: pilot scripts.
- `results/`: pilot tables and diagnostics.

## Immediate Gates

1. Build a first-version A-share `FirstSpecificGenAIAdoption` event library for all listed firms that can serve as customers, suppliers, peers, and focal firms.
2. Match pre-event customer-supplier links, keeping the first pass to traceable major customer/supplier names and fixed pre-GenAI links.
3. Construct `CustomerGenAIExposure_it` from customers' first specific GenAI adoption events and pre-event customer weights.
4. Test the primary diffusion outcome family: focal firms' follow-on validated GenAI adoption and adoption timing.
5. If the diffusion family is credible, test capability-upgrade outcomes: AI-complementary hiring, knowledge-work upgrading, software copyrights, and AI product launches.
6. Use disclosure, analyst, customer-relationship, and market-reaction outcomes as downstream consequences or validation, not as the first identification gate.
