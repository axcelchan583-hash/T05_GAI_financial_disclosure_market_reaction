# T05 External Review Handoff: Current Blockers and Evidence

Date: 2026-06-12

This note is for an independent review by Claude / ChatGPT Pro. The project is not being archived. Please assume the topic must be rescued, and focus on data processing, sample construction, treatment selection, and the most defensible empirical framing.

## Repository

- Main repo: `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction`
- Remote: `git@github-ac:axcelchan583-hash/T05_GAI_financial_disclosure_market_reaction.git`

## Core Question We Are Stuck On

We are trying to study capital-market reactions to listed firms' GenAI-related disclosures in China. The strongest empirical pattern so far is negative abnormal returns for product-market peers after focal-firm GenAI disclosures. But the treatment definition is unstable:

- If we use a broad credible GenAI disclosure sample, we get enough observations and negative peer returns.
- If we require strict GenAI product/model launch announcements, the sample collapses.
- If we use model/app-layer announcements, sample size improves but many events are noisy financing, board, investment, feasibility, or IR/periodic-report disclosures.

The core design question is whether the paper should be about `GenAI-related disclosure`, `credible GenAI corporate action disclosure`, or `GenAI product/model launch`.

## Key Empirical Runs

### v56 Expanded LLM Sample

Files:

- `docs/empirical_runs/117_v56_v55_expanded_llm_empirical_tables_20260612.md`
- `results/v56_v55_expanded_llm_empirical_tables_20260612/`

Main sample:

- `A_all`: 203 events / 160 firms
- `A_first_firm`: 160 events / 160 firms

Preferred product-market peer CAR[0,+1]:

- `A_all`: -0.005859, p=0.008432, events=178
- `A_first_firm`: -0.006558, p=0.010464, events=138
- old-363 reaudited first-firm subset: -0.009614, p=0.002424, events=106

Interpretation problem: the broad A sample is empirically useful but conceptually mixed. It includes credible GenAI-related disclosures, not only product launches or actual deployment events.

### v58 FactSet Supplier/Customer Benchmark

Files:

- `docs/empirical_runs/119_v58_v56_factset_supplier_benchmark_20260612.md`
- `results/v58_v56_factset_supplier_benchmark_20260612/`

Main FactSet findings on `A_all`:

- downstream customer CAR[0,+1]: -0.003330, p=0.020226
- upstream supplier CAR[0,+1]: +0.003938, p=0.234277

Interpretation problem: downstream customer results weakly align with negative spillovers, but the supplier/customer pattern is not as clean or stable as product-peer returns.

### v59 Focal-Firm Own Return Check

Files:

- `results/v59_focal_own_return_check_20260612/`

Strict next trading day focal CAR[0,+1]:

- `A_all`: -0.012378, p=0.01095
- `A_first`: -0.013877, p=0.001234
- old-363 subset: -0.016563, p=0.000719

Interpretation problem: if the focal firm itself also has negative abnormal returns, the story cannot simply be "focal GenAI good news hurts rivals." It may instead be market skepticism, expected investment cost, disclosure hype correction, implementation risk, or broader GenAI competition pressure.

### v60 Strict Core Launch Sample

Files:

- `docs/empirical_runs/120_v60_core_clean_launch_event_study_20260612.md`
- `scripts/run_v60_core_clean_launch_event_study_20260612.py`
- `results/v60_core_clean_launch_event_study_20260612/`

Definition:

- v56 A event
- `out=1`
- `mode=own`
- `layer in {model, app}`
- has explicit launch/release/filing/new-product wording
- excludes noisy title forms such as board resolutions, investment, M&A, financing, framework agreements, annual reports, investor minutes, patents, compute/capex projects

Sample:

- `Core_clean_launch`: 10 events / 9 firms
- `Core_realized_plus`: 7 events / 6 firms

Preferred product-peer CAR[0,+1]:

- `Core_clean_launch_all`: +0.003731, p=0.510399
- `Core_clean_launch_first_firm`: +0.006546, p=0.233935
- `Core_realized_plus_first_firm`: +0.011306, p=0.080963

Interpretation problem: the strict launch sample is too small to be the main sample. It also removes the negative peer result, suggesting that the broad-sample peer effect is not driven by pure launch announcements.

### v61 Model/App-Layer Sample

Files:

- `docs/empirical_runs/121_v61_modelapp_layer_event_study_20260612.md`
- `scripts/run_v61_modelapp_layer_event_study_20260612.py`
- `results/v61_modelapp_layer_event_study_20260612/`

Definition:

- v56 A event
- `out=1`
- `mode=own`
- `layer in {model, app}`
- no requirement for launch/release/filing wording

Sample:

- `ModelApp_own_out_all`: 61 events / 55 firms
- `ModelApp_own_out_first_firm`: 55 events / 55 firms
- `ModelApp_clean_title_all`: 14 events / 12 firms
- `ModelApp_realized_plus_all`: 14 events / 12 firms
- `Model_only_own_out_all`: 35 events / 32 firms
- `App_only_own_out_all`: 26 events / 25 firms

Preferred product-peer CAR[0,+1]:

- `ModelApp_own_out_all`: -0.005166, p=0.173407
- `ModelApp_own_out_first_firm`: -0.005643, p=0.166180
- `ModelApp_clean_title_all`: -0.004356, p=0.455436
- `ModelApp_realized_plus_all`: +0.001856, p=0.837476
- `Model_only_own_out_all`: -0.003430, p=0.472625
- `App_only_own_out_all`: -0.007634, p=0.214835

Focal strict-next CAR[0,+1]:

- `ModelApp_own_out_all`: -0.010768, p=0.144537
- `ModelApp_own_out_first_firm`: -0.012520, p=0.095255
- `ModelApp_realized_plus_all`: -0.017658, p=0.015690

Interpretation problem: model/app layer is not enough. It includes board resolutions, issuance plans, feasibility reports, action plans, contracts, investments, and IR records. Clean-title filtering removes too much and still leaves odd cases.

## Main Current Blockers

1. Treatment definition is not stable.
   - `GenAI product/model launch` is too narrow.
   - `GenAI-related disclosure` is feasible but conceptually broad.
   - `model/app layer` sounds precise but still contains many disclosure-form noises.

2. Sample-size tradeoff is severe.
   - Broad A sample: 203 events / 160 firms.
   - Model/app layer: 61 events / 55 firms.
   - Strict launch: 10 events / 9 firms.
   - A publishable design probably needs a middle layer, not the current extremes.

3. Main effect interpretation is ambiguous.
   - Product peers show negative returns in the broad sample.
   - Focal firms also show negative returns under strict next-trading-day timing.
   - This undermines a simple "GenAI adoption is good news for focal firms and bad news for rivals" mechanism.

4. Supply-chain evidence is not decisive.
   - CSMAR listed supplier coverage is too small.
   - FactSet downstream customer returns are sometimes negative, but not as robust as product-peer results.
   - Upstream suppliers are mostly weak or unstable.

5. The POM benchmark likely uses a broader announcement/disclosure definition.
   - Our strict launch sample is too small, so if POM has a few hundred observations, it probably does not require pure GenAI launch events.
   - The right comparison may be announcement/disclosure events, not actual product releases.

6. Old sample continuity is confusing.
   - Old 363 first-candidate events do not map cleanly into the new v52/v56 candidate pool.
   - Only part of the old 363 survives under the new candidate-generation and LLM recoding pipeline.
   - This suggests the retrieval/candidate pipeline itself is a major source of sample instability.

## Possible Rescue Direction

The likely viable route is to stop treating "launch" as the main treatment and instead define:

`credible GenAI corporate action disclosure`

Then classify the v56 A sample into disclosure types:

- `product_launch`: release, launch, filing, new product/model
- `project_investment`: GenAI/AI project construction, smart-computing, model development investment, subsidiary setup
- `business_contract`: customer contract, order, tender, deployment for customer
- `strategic_cooperation`: cooperation agreement or partnership with credible GenAI content
- `financing_or_capex_plan`: issuance plan, fundraising use, feasibility report
- `periodic_or_ir`: annual report, action plan, investor minutes, earnings exchange
- `weak_or_noise`: weak keyword hit or announcement topic not truly GenAI

Potential main sample:

`A_core_disclosure = product_launch + project_investment + business_contract + strategic_cooperation`

Potential exclusions:

`financing_or_capex_plan`, `periodic_or_ir`, `weak_or_noise`

Expected benefit: this may retain a usable sample size, likely larger than 61 but cleaner than 203, while matching POM-style announcement/disclosure design better than strict launch.

## Data-Processing Decisions To Prioritize

Independent reviewers should focus on the data pipeline, not on abandoning the idea:

1. Retrieval universe:
   - Should we start from the current v56 A sample, the older 363 events, or rebuild from the 111k CNINFO announcement universe?
   - What recall keywords or title/body search rules should define the candidate pool before LLM coding?

2. Event de-duplication:
   - Should the main sample be every credible event, first event per firm, first event per disclosure type per firm, or strongest event per firm-year?
   - How should repeated follow-up disclosures be handled?

3. Disclosure-form exclusions:
   - Which forms should always be excluded from the main sample: annual reports, semiannual reports, board resolutions, issuance plans, feasibility reports, investor minutes, action plans, patents, routine contracts, M&A documents?
   - Which forms should stay if the GenAI action is concrete enough?

4. Disclosure-type coding:
   - Which types should form the main treatment?
   - Which types should be mechanism or robustness groups only?
   - Should `realized=+` be a main-sample requirement or only a credibility/mechanism split?

5. Outcome hierarchy:
   - Should the main Y be product-market peer CAR, focal-firm CAR, peer-minus-focal, downstream-customer CAR, or a family of spillover outcomes?
   - If focal and peer are both negative, what comparison best identifies a competitive or revaluation mechanism?

6. First rerun:
   - Propose one exact sample construction rule that is neither the broad 203-event A sample nor the 10-event strict launch sample.
   - Specify the first empirical table to rerun and what result would count as diagnostic.

## Questions For Independent Reviewers

1. Should the paper's X be `credible GenAI disclosure`, `credible GenAI corporate action disclosure`, or `GenAI launch/adoption announcement`?
2. Given focal returns are also negative, what mechanism is most defensible?
   - market skepticism / hype correction
   - costly investment / implementation risk
   - competition-intensity shock
   - investor reassessment of AI capability gap
   - disclosure-quality / cheap-talk contrast
3. Should product-peer CAR remain the main Y, or should focal-firm CAR / peer-minus-focal / downstream-customer CAR become the main Y?
4. Is the broad A sample defensible if we explicitly frame the paper as disclosure-driven market reassessment rather than actual technology adoption?
5. What exact filtering rule would best approximate POM's announcement sample while avoiding our strict-launch sample collapse?
6. Under the assumption that the topic must be rescued, what is the minimum viable data reconstruction plan, including retrieval scope, exclusion rules, disclosure-type coding, main sample, robustness samples, and the first table that should be rerun?

## Recommended Files To Read First

1. `docs/empirical_runs/117_v56_v55_expanded_llm_empirical_tables_20260612.md`
2. `docs/empirical_runs/119_v58_v56_factset_supplier_benchmark_20260612.md`
3. `docs/empirical_runs/120_v60_core_clean_launch_event_study_20260612.md`
4. `docs/empirical_runs/121_v61_modelapp_layer_event_study_20260612.md`
5. `docs/design/重新构造X和Y/12_genai_coding_amendment_v3_3_20260612.md`
6. `docs/prompts/57_genai_announcement_llm_precoding_prompt_v3_3_20260612.md`
