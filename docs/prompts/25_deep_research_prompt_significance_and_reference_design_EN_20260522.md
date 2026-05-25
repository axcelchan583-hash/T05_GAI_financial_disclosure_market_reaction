# Deep Research Prompt: Can the Product-Market Peer Spillover Design Be Strengthened Legitimately?

Date: 2026-05-22

## How to Use

Copy the full prompt below into ChatGPT Pro, Claude, or another deep-research tool.

The goal is not to ask the model to p-hack. The goal is to ask whether, under defensible theory and prior literature, our current GenAI disclosure peer-spillover design can be made sharper and more likely to detect the true effect if one exists.

---

## Prompt

You are a top-journal empirical reviewer and research-design advisor working at the intersection of accounting, finance, information systems, operations management, and strategic management.

Please independently evaluate a China A-share empirical research design on GenAI disclosure and product-market peer spillovers. The central question is:

```text
Is there a theoretically legitimate, literature-grounded, and empirically feasible way to make the main effect clearer or more statistically detectable, without p-hacking?
```

Do not recommend mechanical sample deletion, ex post window shopping, or any form of p-hacking. Every recommendation must satisfy all three criteria:

1. **Ex ante theoretical justification**: why this sample split, outcome, event window, or variable definition should capture a stronger effect.
2. **Literature anchor**: how it connects to event-study, disclosure informativeness, product-market competition, supply-chain spillovers, peer effects, technology announcements, or GenAI announcement literature.
3. **Data feasibility**: whether it can be implemented using China A-share public data or the data already available in the project.

## 1. Current Research Question

The project has gone through multiple versions. The current version is:

```text
When a listed firm gives a more specific public reply about its GenAI / LLM / AIGC applications on an exchange-run investor-interaction platform,
does the stock market revalue its product-market competitors?
```

The current design is:

```text
Main X:
    Specificity_it x ProductSimilarity_ij

Where:
    Specificity_it = the specificity of focal firm i's GenAI disclosure on event date t
    ProductSimilarity_ij = product-market text similarity between focal firm i and peer firm j

Main Y:
    PeerCAR_jt = short-window stock-market reaction of peer firm j around focal firm i's GenAI disclosure event

Unit:
    focal GenAI disclosure event i,t x peer firm j
```

The current economic logic is:

```text
If a focal firm's GenAI disclosure is more specific, it may signal that its GenAI use is closer to real product or business implementation.
For product-market peers, this signal may represent either a competitive threat or an industry opportunity.
```

Therefore, the average main effect may mix two channels:

```text
Competitive threat: more similar peers experience lower CAR.
Industry opportunity: more similar peers experience higher CAR.
```

## 2. Current Pilot Data and Results

The event sample comes from Chinese exchange-run investor-interaction platforms. The strict event definition is:

```text
The company's reply text itself contains GenAI / large model / AIGC / ChatGPT / DeepSeek related content.
Investor questions are used only as context or controls; they are not treated as company disclosure.
```

Current event sample:

```text
590 answer-level events
402 firm-day events
222 focal firms
```

Product-market peer network:

```text
Uses CSMAR/STK_LISTEDCOINFOANL fields MAINBUSSINESS + BusinessScope.
Computes Chinese character 2-4 gram TF-IDF cosine similarity.
Peers are selected within the same IndustryNameD category.
Top 5 and Top 10 product-market peers are retained.
```

Explanatory-side X pilot:

```text
Top 10 peer definition:
    399 events matched to peer network
    2,178 focal-peer links
    3,978 event x peer X observations

Top 5 peer definition:
    1,993 event x peer X observations
```

Main-effect pilot:

```text
Daily return source: Sina Finance daily K-line feed, only for pilot
Market return: Shanghai Composite Index sh000001
Window: PeerCAR[-1,+1]
Expected return: market model
Peer sample: Top 5 peers
CAR-linked observations: 1,906
Events: 399
Peer firms: 681
```

Current main specification:

```text
PeerCAR_jt =
    beta1 ProductSimilarity_ij
  + beta2 Specificity_it x ProductSimilarity_ij
  + Event FE
  + error_ijt
```

Current result:

```text
coef(Specificity x ProductSimilarity) = -0.0167
clustered SE by focal event = 0.0121
p = 0.168
```

With peer fixed effects:

```text
coef = -0.0165
p = 0.213
```

Portfolio-spread sanity check:

```text
Top-rank peer portfolio CAR - low-rank peer portfolio CAR
coef on Specificity = -0.0015
p = 0.355
```

Alternative outcome quick checks:

```text
|CAR| is also insignificant.
Raw return gives a negative coefficient but remains insignificant.
```

Current interpretation:

```text
The direction is more consistent with a competitive-threat story, but the evidence is statistically weak.
```

## 3. Reference Paper to Benchmark Against

Please benchmark our design against:

```text
Qian, Peng, and Li (2025),
"The Impact of Generative AI Announcements on Suppliers: Evidence From the Stock Market",
Production and Operations Management, OnlineFirst.
DOI: 10.1177/10591478251398333
```

Key features of the reference paper:

1. The event source is not exchange Q&A. It uses LexisNexis and leading newswire agencies such as PR Newswire, Business Wire, and GlobeNewswire.
2. It starts from 14,941 potential GenAI announcements and then narrows to 2,084 announcements by publicly traded North American firms.
3. It excludes 1,397 broad mentions that discuss GenAI together with other IT topics and keeps only specific GenAI initiatives.
4. The final initial GenAI announcement sample contains 254 announcing firms.
5. After matching listed suppliers, the final sample is:

```text
117 announcing firms
277 suppliers
515 supplier-announcement observations
```

6. The main event-study result is not based on a broad CAR window. It reports:

```text
AR on day -1
AR on day 0
AR on day +1
```

The main effect is concentrated on announcement day `AR[0]`:

```text
mean AR[0] = 0.27%, significant at 1%
median AR[0] = 0.13%, significant at 1%
positive AR proportion = 54.56%, significant at 5%
```

7. Expected returns are estimated using a Fama-French four-factor model over:

```text
[-210, -11] trading days
```

8. If an announcement is made on a weekend, holiday, or after market hours, the next trading day is treated as the announcement date.
9. It excludes suppliers that made their own GenAI announcements before the customer's announcement date.
10. It excludes suppliers linked to multiple announcing customers with overlapping announcement dates.
11. It excludes suppliers with confounding events such as board changes, earnings announcements, and M&A within the event window [-2,+1].
12. Much of its inferential power comes from theoretically motivated cross-sectional heterogeneity:

```text
Higher supplier R&D intensity
Higher supplier sales growth
Shorter geographic distance between customer and supplier
Less competitive supplier industries / higher industry concentration
Product-oriented GenAI announcement rather than process-oriented announcement
```

13. It reports PSM, IV, Heckman selection, DID, long-horizon CAR, exclusion of major LLM release / government AI policy days, and alternative Fama-French three-factor/five-factor expected-return models.

## 4. Your Tasks

Based on the information above, independently assess whether our product-market peer-spillover design still has a legitimate chance of producing a clearer effect.

Please answer in the structure below.

### Task 1: Overall Judgment

Give one of the following judgments:

```text
A. Worth continuing, with a clear legitimate path to improve signal-to-noise.
B. Worth one more strengthened pilot, but should not yet be treated as the main paper.
C. Not recommended as the main design; pivot to another design.
```

Explain why.

### Task 2: Compare Our Design With the Reference Paper

Compare the two designs along the following dimensions:

```text
event-source strength
specificity of event definition
event window
AR[0] versus CAR[-1,+1]
strength of the peer/supplier relationship
confounding-event cleanup
strength of theoretical heterogeneity
whether the unit of analysis amplifies sample size without adding noise
whether the expected sign is mixed
```

Identify which differences are most likely responsible for our current weak result.

### Task 3: Propose Legitimate Signal-to-Noise Improvements

Propose at least 8 candidate improvements. For each one, provide a table with:

```text
proposal name
how to change X / Y / sample / model
theoretical justification
literature or reference-paper logic
expected sign
whether it may increase statistical detectability
p-hacking risk
implementation difficulty
priority
```

Please consider, but do not limit yourself to, the following possibilities:

1. Change Y from `CAR[-1,+1]` to `AR[0]` or `CAR[0,+1]`.
2. Treat pre-market, intraday, after-market, weekend, and holiday replies differently.
3. Keep only firm replies with concrete product, scenario, customer, timing, monetary, partner, or deployment details.
4. Classify GenAI disclosures into product-oriented versus process-oriented / internal-efficiency-oriented disclosures.
5. Split peers by prior AI capability:

```text
High Specificity x ProductSimilarity x Low Peer AI Capability -> more negative PeerCAR
High Specificity x ProductSimilarity x High Peer AI Capability -> less negative or positive PeerCAR
```

6. Tighten the peer relationship from same-industry Top5 to product-text Top3 / high-similarity peers.
7. Replace `BusinessScope + MAINBUSSINESS` with annual-report business-description sections.
8. Exclude confounding events such as same-day major announcements, earnings releases, M&A, regulatory inquiries, limit-up/limit-down days, ST stocks, and Beijing Stock Exchange stocks.
9. Use ABVOL, investor attention, or future investor questions as alternative outcomes.
10. Reframe the main hypothesis as heterogeneity rather than average main effect.
11. Use stronger event sources such as formal announcements, investor-relations activity records, press releases, or newswire announcements.
12. Use same-event high-versus-low peer portfolio spread instead of observation-level regression.
13. Use the correct fixed-effect structure, such as event fixed effects, peer fixed effects, industry-date fixed effects, or portfolio-level event regressions.
14. First test whether there is any average peer reaction using AR[0] t-tests, Wilcoxon signed-rank tests, and sign tests, then run cross-sectional regressions.

### Task 4: Recommend the Top 3 Versions to Try Next

Do not list too many. Give the three most important versions to run next.

For each version, specify:

```text
main X
main Y
sample restriction
regression or test
expected direction
why it is more likely to work than the current pilot
main risk
```

### Task 5: Should the Paper Story Change?

Rank the following possible stories:

```text
A. Product-market competitive threat
B. Industry-opportunity revaluation
C. Investor attention / attention spillover
D. Heterogeneity story: low-AI-capability peers face competitive threat, high-AI-capability peers benefit or are less harmed
E. Abandon product-market peers and return to supplier spillover or own-firm disclosure informativeness
```

Explain the ranking.

### Task 6: Give a Clear Execution Rule

Answer directly:

```text
What is the next table we should run?
What result, if still insignificant, should make us stop this line?
What result, if significant, would justify continued investment?
```

Do not give a generic literature review. Focus on the current pilot results and the reference paper's research design. The output should be critical, direct, and operational.

## Required Output Format

Please answer in English using the following structure:

```text
1. Overall Judgment
2. What the Reference Paper Does to Increase Signal-to-Noise
3. Why Our Current Pilot Is Weak
4. Legitimate Improvement Options
5. Top 3 Versions to Run Next
6. Whether the Story Should Change
7. Stop / Continue Criteria
```
