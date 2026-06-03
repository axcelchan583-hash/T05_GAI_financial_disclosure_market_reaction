# T05: 中国上市公司 GenAI 披露、竞品市场重估与同伴扩散机制

更新时间：2026-06-01

## Repository Split

本仓库现在只保留 T05 原主线：GenAI 披露具体性、竞品市场重估与同伴扩散机制。

已拆出的两个辅助仓库：

- Qian 供应商复刻：`/Users/mac/computerscience/23实证选题探索/23-T05-qian-supplier-replication-cn`
- GenAI 资本市场文献精读：`/Users/mac/computerscience/23实证选题探索/23-T05-genai-capital-markets-reading`

巨潮 PDF/text 缓存和 Qian 复刻结果不再放在本仓库内。

## 2026-06-01 最新识别风险审计

当前项目不能再被表述为“一个显著主效应已经自然成立”。更准确的状态是：

```text
有可写的核心现象：
    更具体的 GenAI 披露与 AI-active 的 LLM-screened direct product-market peers
    更负的 PeerCAR[0,+1] 相关。

但 peer definition 是最大风险：
    严格中文年报文本产品相似度 peer 不能复制当前主结果；
    当前有效 peer 是 LLM-screened direct competitors，而不是传统年报文本 peer。
```

### 需要解决的识别/测度问题

从 X 到 Y，目前至少有五层问题：

| 层级 | 关键攻击点 | 当前处理 | 风险等级 |
|---|---|---|---|
| X: GenAI 披露事件 | 是否只是普通“人工智能”泛泛提及 | 事件要求公司回复/披露文本含 GenAI/AIGC/大模型/ChatGPT/DeepSeek 等词 | 中 |
| X: 披露具体性 | `Specificity_z` 到底测什么 | 参考 Hope, Hu and Lu (2016) 的 disclosure specificity；强调“可观察文本具体性”，不是能力 | 中高 |
| X: 文本混杂 | 是否只是长度、AI 词频、IR 活跃度 | 控制 answer/question length、AI keyword、source、年份/月度、disclosure type | 中 |
| Peer definition | 谁是真正竞品 | 当前显著结果依赖 LLM-screened candidate-menu Top5；传统年报文本 peer 不支持主结果 | 高 |
| AIActivePeer | 是否同源、是否 look-ahead | 主口径倾向 `ext_any`；text-history 只并列/稳健性；所有证据需 t-5 前可观察 | 高 |
| Y: PeerCAR | 是否自造 Y | `PeerCAR[0,+1]` 是标准短窗 event-study / information-transfer outcome | 低 |
| 事件污染 | 同日公告/业绩/重大事项污染 | announcement-cleaned 样本；pre-window CAR controls | 中 |
| 模型识别 | 是否是 DID/强因果 | 不是 DID/IV；是 within-event cross-sectional revaluation design | 高 |
| 理论解释 | business stealing 是否过度 | 只能写 competitive-risk reassessment；不能写真实业务挤出 | 中高 |

### 当前 8 个硬门槛

1. **X 不是 generic AI**：GenAI 关键词与语境过滤要清楚。
2. **X 有 Hope-style 文献锚**：写成“参考 Hope 构造的生成式 AI 披露具体性”。
3. **X 不只是长度/AI 词频**：主表或测度表必须控制文本长度、AI 词频、问题长度。
4. **Peer 不能被说成纯自造**：需要候选集来源、LLM 筛选规则、validity tests。
5. **AIActive 用外部证据做 headline**：`ext_any` 优先，text-history 并列但不单独承担主结果。
6. **Y 是标准 CAR**：保留 market-model `PeerCAR[0,+1]`，并做公告污染清理。
7. **模型承认是相对重估**：event FE 下识别的是同一焦点事件内 AI-active vs non-AI-active peer 的相对差异。
8. **机制区分 competitive risk 和 category validation**：具体化披露负向重估；供应链/行业验证披露可正向。

## 2026-06-01 中文年报文本 peer 复刻结果

为回应“能否按任宏达、王琨（2019，《会计研究》）和刘昌阳、刘亚辉、尹玉刚（2020，《世界经济》）的中文年报文本产品市场竞争口径构造 peer”的问题，新增 v22：

```text
scripts/build_v22_chinese_literature_product_peers_20260601.py
scripts/run_v22_chinese_literature_peer_main_effect_20260601.py
docs/empirical_runs/85_v22_chinese_literature_product_peer_checks_20260601.md
results/v22_chinese_literature_product_peers_20260601/
results/v22_chinese_literature_peer_main_effect_20260601/
```

构造两套文献口径：

```text
Ren-Wang binary:
    年报业务文本 -> 中文分词 -> 去停用/非产品词 -> 0/1 产品业务词向量
    -> cosine similarity -> TopN peers

Liu-Liu-Yin product-TFIDF:
    CSMAR 主营业务/经营范围生成产品词库 -> 年报产品词 TF-IDF
    -> cosine similarity -> TopN peers
```

Top5 强 FE 主结果，系数均为 `Specificity_z × AIActivePeer`：

| peer 口径 | AIActive | coef | p |
|---|---|---:|---:|
| Ren-Wang binary global | ext_any | 0.000895 | 0.281 |
| Ren-Wang binary global | current_text_history | -0.001383 | 0.113 |
| Ren-Wang binary same-industry | ext_any | 0.001413 | 0.035 |
| Ren-Wang binary same-industry | current_text_history | 0.000472 | 0.502 |
| Liu product-TFIDF global | ext_any | -0.000826 | 0.354 |
| Liu product-TFIDF global | current_text_history | -0.000947 | 0.299 |
| Liu product-TFIDF same-industry | ext_any | -0.000797 | 0.273 |
| Liu product-TFIDF same-industry | current_text_history | -0.001585 | 0.039 |

解释：

```text
严格中文年报文本 peer 口径不支持当前 competitive-risk 主效应。
最干净的 external AIActive (`ext_any`) 没有稳定负向结果；
个别 text-history 结果显著，但依赖同源 AIActive，不能作为 headline。
```

因此后续写法必须区分：

```text
文献基础：
    Hoberg and Phillips / 任宏达-王琨 / 刘昌阳等提供“文本产品相似度”
    和“产品市场 peer”构造思想。

当前有效 peer：
    从年报文本、CSMAR 业务范围和 AI-word-stripped 年报文本生成候选集，
    再由 LLM 筛选 direct product-market competitors。

论文责任：
    证明 LLM-screened direct peers 在 GenAI 披露短窗重估场景下更贴近
    直接竞争关系，而不是宣称传统中文年报文本 peer 已经支持主结果。
```

## 当前可写故事

```text
主线 A：竞争风险重估
    更具体的 GenAI 披露
    -> AI-active LLM-screened direct peers 的 PeerCAR[0,+1] 更负
    -> 解释为资本市场识别 competitive-risk signal

边界 B：类别验证 / 供应链验证
    GenAI announcement / AI supply-chain exposure disclosure
    -> 相关 peers 平均反应可能为正
    -> 解释为 category validation，而不是竞争风险
```

当前最安全结论：

```text
本文识别的是资本市场短窗口相对重估：
    specific GenAI disclosure × pre-event AI activeness × direct product-market proximity

本文不声称：
    强因果、真实 business stealing、真实 GenAI 能力建设、
    或传统年报文本 peer 口径下主结果完全稳健。
```

## 2026-06-01 组会版冻结口径

新增组会版实验设计：

```text
docs/design/12_group_meeting_experimental_design_20260601.md
docs/design/13_framework_measurement_support_20260601.md
docs/design/figures/figure_framework_measurement_support_20260601.svg
docs/design/figures/figure_framework_measurement_support_20260601.png
docs/empirical_runs/81_v17_deepseek_flash_peer_network_20260531.md
docs/empirical_runs/82_v18_cao_style_open_ended_deepseek_peers_20260531.md
results/v17_deepseek_flash_peer_coding_20260531/
results/v18_cao_style_open_ended_deepseek_peers_20260531/
```

当前框架图把所有关键测度的支撑写进图里：

```text
X:
    Specificity_z
    支撑：Hope, Hu and Lu (2016); Cheng et al. (2019)

Y:
    PeerCAR[0,+1]
    支撑：Beaver (1968); MacKinlay (1997); Kothari and Warner (2007);
          Foster (1981); Lang and Stulz (1992)

Peer:
    DeepSeek Flash-selected Top5 product-market peers
    支撑：Hoberg and Phillips (2016); Cao et al. (2025);
          本文 v19/v20 peer-validity checks

AIActive:
    ext_any = prior CAC / AI patent / AI hiring evidence
    支撑：Babina et al. (2024); Kogan et al. (2017);
          CAC public registry evidence
```

当前主线更新为：

```text
Research question:
    更具体的 GenAI 披露是否使资本市场对 AI-active 的近产品市场同行
    进行更负面的短窗口相对重估？

Main X:
    Specificity_z
    Hope-style GenAI disclosure specificity / text-detail density.

Main Y:
    PeerCAR[0,+1]
    DeepSeek Flash-selected product-market peer 的 signed market-model CAR.

Main peer definition:
    DeepSeek Flash-selected Top5 product-market peers from a no-random,
    auditable candidate menu.

Candidate menu:
    CSMAR business-scope Top10
    annual-report same-industry business-text Top10
    annual-report global AI-word-stripped Top10

Main AIActive:
    ext_any =
        prior CAC GenAI filing / registration
     OR prior broad-AI patent grant
     OR prior broad-AI hiring in prior 365 days
```

DeepSeek Flash 全量 peer 编码：

```text
model: deepseek-v4-flash
focal firms coded: 2,652
selected focal-peer pairs: 11,864
prompt tokens: 2,237,821
completion tokens: 97,058
estimated cost: about RMB 2.4
API key: read from environment only; not stored in scripts or outputs
```

DeepSeek Flash-selected Top5 主结果：

```text
PeerCAR[0,+1] =
    beta * Specificity_z × AIActivePeer
  + AIActivePeer
  + PeerCAR[-10,-2] + PeerCAR[-20,-2]
  + event FE
  + peer industry-week FE

two-way clustered by event_id and peer_code
sample = first focal GenAI event, announcement-cleaned

AIActive = ext_any:
    coef = -0.002137
    p    = 0.0157
    N    = 7,813
    events = 2,311

AIActive = current_text_history:
    coef = -0.002283
    p    = 0.0108

AIActive = ext_plus_history:
    coef = -0.002252
    p    = 0.0116
```

### Cao-style open-ended DeepSeek peer diagnostic

为回应“能否完全按 Cao et al. (2025) 的 open-ended LLM peer
generation 来做”的问题，新增 v18 诊断：

```text
Peer definition:
    DeepSeek open-ended Cao-style Top5 A-share product-market peers.
    不提供候选池；只要求模型列出 A 股上市公司竞品代码和简称。

Coverage:
    input focal firms: 2,652
    focals with at least one matched peer: 2,585
    selected peer pairs: 12,099
    unmatched generated peers: 1

Overlap with v17 candidate-menu DeepSeek peers:
    pair overlap: 1,425
    share of v18 pairs overlapping v17: 11.8%
    focal-level median Jaccard overlap: 0.000

Main result, Top5, AIActive = ext_any:
    coef = -0.000828
    p    = 0.2228
    N    = 7,934
    events = 2,322

Same-industry filtered v18, Top5:
    ext_any:              coef = -0.000630, p = 0.4926
    current_text_history: coef = -0.002373, p = 0.0140
    ext_plus_history:     coef = -0.001883, p = 0.0229
```

解释：v18 更接近 Cao et al. 的 open-ended LLM peer generation，
但在中国 A 股中更 noisy，且在最干净的 external AIActive (`ext_any`)
下不复制 v17 主结果。当前不宜把 v18 作为 headline peer definition；
它应作为 conservative robustness / boundary check。主文仍以 v17
auditable candidate-menu DeepSeek peers 为主，并明确这是对 Cao et al.
思想的中国场景适配，而非完全复刻。

### DeepSeek-selected peer validity package

为回应“DeepSeek Flash-selected Top5 product-market peers 是否有效”的问题，
新增 v19 非人工验证包：

```text
docs/empirical_runs/83_v19_deepseek_peer_validity_checks_20260531.md
results/v19_deepseek_peer_validity_checks_20260531/
```

核心结论：

```text
Output stability, 100-focal rerun:
    mean Jaccard overlap = 0.8708
    median Jaccard overlap = 1.0000
    mean common peers     = 4.505 / 5
    top1 same share       = 84.5%

Overlap with non-random alternative peer systems:
    CSMAR business-scope Top5 overlap share of v17 = 44.3%
    annual same-industry text Top5 overlap share    = 33.9%
    annual AI-word-stripped text Top5 overlap share = 20.0%
    random same-industry overlap share              = 1.8%
    low-similarity overlap share                    = 0.8%

Return comovement, 2025-2026:
    v17 DeepSeek peers:
        mean abnormal-return beta = 0.6008
        mean abnormal-return corr = 0.4147
    random same-industry peers:
        beta = 0.4592, corr = 0.3007
    low-similarity peers:
        beta = 0.3780, corr = 0.2459

Fundamental comovement:
    v17 DeepSeek peers have the highest gross-margin residual correlation
    and highest sales-growth residual correlation among tested systems.
```

解释：跳过人工专家盲审后，当前能最快补强的是 Cao et al. 风格的
output stability、与既有文本 peer 系统的 overlap、收益共动、
基本面共动和同质性检验。v19 支持 v17 peer measure 不是随机或低相似
同行；但它仍不是“真实竞品”的金标准，论文中应写成 validated
product-market-neighbor proxy。

### DeepSeek-candidate-menu placebo peers

为避免旧 v6 placebo 与当前 DeepSeek peer 口径不完全一致，新增 v20：

```text
scripts/run_v20_deepseek_candidate_placebos_20260601.py
docs/empirical_runs/84_v20_deepseek_candidate_placebos_20260601.md
results/v20_deepseek_candidate_placebos_20260601/
```

构造逻辑：

```text
对每个 focal firm：
    1. 复原 v17 DeepSeek 使用的 no-random candidate menu，最多 15 个候选；
    2. 排除 DeepSeek Flash-selected Top5；
    3. 在剩余候选中构造：
        deepseek_candidate_low_similarity_top5:
            选择剩余候选中 product similarity 最低的 5 个；
        deepseek_candidate_random_top5:
            用固定 focal-code seed 随机抽取 5 个。
```

覆盖：

```text
focal firms with candidate menu: 2,652
focal firms with placebo Top5:   2,652
mean remaining candidates:       7.73
median remaining candidates:     8
```

主规格 placebo 结果，`Specificity_z × AIActivePeer`：

```text
DeepSeek-selected Top5 headline, ext_any:
    coef = -0.002137
    p    = 0.0157

DeepSeek-candidate low-similarity Top5, ext_any:
    coef =  0.000094
    p    = 0.9226

DeepSeek-candidate random Top5, ext_any:
    coef = -0.001639
    p    = 0.1067
```

解释：同一候选菜单内的 low-similarity placebo 很干净，说明主结果不是
“任意候选同行都会出现”。candidate-menu random placebo 有同方向负号但
不显著，因为剩余候选本身已经是从 CSMAR / 年报文本中筛出的 plausible
peers，不是普通随机公司。因此论文中应把 v20 random 写成 stress test，
而不是最强 placebo；最强 falsification 仍是 low-similarity、旧
same-industry random、non-GenAI pseudo-events 和 open-ended v18 的
external-AIActive 不复制。

当前组会表述：

```text
本文识别的是短窗口 peer-side relative revaluation，
不是强因果、不是真实 business stealing、不是真实 GenAI 能力。

最安全结论：
    更具体的焦点 GenAI 披露与 AI-active DeepSeek-selected Top5
    产品市场同行更负的两日异常收益相关。
```

最大风险仍然是 peer definition sensitivity：

```text
annual-only peer 不支持主结果；
patent peer 不支持主结果；
common-analyst peer 不支持主结果；
旧 CSMAR scope 和 DeepSeek-selected peer 支持主结果。

因此论文必须把 peer construction 和 peer validity 作为核心测度部分，
不能把 peer 当成无争议给定变量。
```

## 2026-05-31 X/Y 测度文献锚与 peer-validity gate

当前先把问题收束为一个 measurement-first goal：

```text
X 已基本确定：
    GenAI disclosure event
    或 GenAI disclosure specificity / concreteness

Y 的大类已确定：
    股票市场反应

关键不是再自造一个新 Y，
而是把 Y 写成已有文献中的标准资本市场反应变量：
    focal firm CAR
    或 product-market peer CAR
```

新增测度文献锚文档：

```text
docs/measurement/13_x_y_measurement_literature_anchor_20260531.md
```

当前最可防守的 X/Y 组合：

```text
Main X:
    生成式人工智能披露具体性
    GenAI_Disclosure_Specificity / Specificity_z

X 文献锚：
    Hope, Hu and Lu (2016, RAST)
        qualitative disclosure specificity as concrete/verifiable detail density

    Cheng, De Franco, Jiang and Lin (2019, Management Science)
        hot-technology disclosure should be separated into generic/speculative
        versus existing/substantive content

Main Y:
    PeerCAR[0,+1]
    focal GenAI disclosure date around close product-market peers' stock returns

Y 文献锚：
    Beaver (1968), MacKinlay (1997), Kothari and Warner (2007)
        standard disclosure/event-study abnormal return framework

    Foster (1981), Lang and Stulz (1992)
        intra-industry information transfer / competitive effects

    Hoberg and Phillips (2016, JPE)
        text-based product-market peer network
```

当前模型含义：

```text
PeerCAR[0,+1]_{j,t}
  = beta * Specificity_z_{i,t} * AIActivePeer_{j,t-1}
  + theta * AIActivePeer_{j,t-1}
  + controls
  + event FE
  + peer industry-week FE
  + error

由于 Specificity_z 是 event-level 变量，在 event FE 下被吸收；
真正识别的是同一个 focal GenAI 披露事件内，
AI-active peers 相对 non-AI-active peers 是否随 focal disclosure specificity
更高而出现更负的短窗相对重估。
```

新增 peer-validity gate：

```text
scripts/run_v13_peer_validity_gate_20260531.py
scripts/run_v13_peer_fundamental_validity_20260531.py
docs/empirical_runs/69_v13_peer_validity_gate_20260531.md
docs/empirical_runs/70_v13_peer_fundamental_validity_20260531.md
results/v13_peer_validity_gate_20260531/
data/peer_validity_llm_20260531/
```

Return-comovement gate, 2025-2026 Top5：

```text
annual same-industry text Top5:
    mean abnormal-return corr = 0.4352

annual global text Top5:
    mean abnormal-return corr = 0.4167

annual global AI-word-stripped text Top5:
    mean abnormal-return corr = 0.4144

old CSMAR scope Top5:
    mean abnormal-return corr = 0.3547

random same-industry Top5:
    mean abnormal-return corr = 0.3007

low-similarity same-industry Top5:
    mean abnormal-return corr = 0.2459
```

Fundamental-comovement gate, Top5：

```text
old CSMAR scope Top5:
    sales-growth corr = 0.1327
    gross-margin corr = 0.4413

random same-industry Top5:
    sales-growth corr = 0.0598
    gross-margin corr = 0.3106

annual same-industry text Top5:
    sales-growth corr = 0.2028
    gross-margin corr = 0.6139

annual global AI-word-stripped text Top5:
    sales-growth corr = 0.1880
    gross-margin corr = 0.5527
```

Manual / LLM inspectability gate：

```text
新增：
    scripts/run_v13_peer_manual_llm_gate_20260531.py
    docs/empirical_runs/71_v13_peer_manual_llm_gate_20260531.md
    results/v13_peer_validity_gate_20260531/peer_manual_proxy_pair_scores.csv
    results/v13_peer_validity_gate_20260531/peer_manual_proxy_summary.csv
    results/v13_peer_validity_gate_20260531/peer_validity_decision_matrix.csv
    data/peer_validity_llm_20260531/peer_system_validation_template_150_pairs_20260531.csv
    data/peer_validity_llm_20260531/LLM_PEER_SYSTEM_VALIDATION_TASK.md
    data/peer_validity_llm_20260531/peer_system_validation_coded_150_pairs_codex_20260531.csv
    results/v13_peer_validity_gate_20260531/peer_system_validation_coded_150_pairs_codex_summary.csv
    docs/empirical_runs/72_v13_peer_codex_manual_coding_20260531.md
    data/peer_validity_llm_20260531/peer_system_validation_coded_150_pairs_agent_20260531.csv
    results/v13_peer_validity_gate_20260531/peer_system_validation_coded_150_pairs_agent_summary.csv
    results/v13_peer_validity_gate_20260531/peer_system_manual_coding_two_coder_agreement.csv
    docs/empirical_runs/73_v13_peer_agent_manual_coding_20260531.md
    scripts/build_v13_llm_peer_candidate_menu_20260531.py
    data/peer_validity_llm_20260531/llm_peer_candidate_menu_200_20260531.csv
    data/peer_validity_llm_20260531/LLM_PEER_RERANKING_TASK.md
    docs/empirical_runs/74_v13_llm_peer_candidate_menu_20260531.md
    scripts/run_v13_llm_reranked_peer_gate_20260531.py
    results/v13_peer_validity_gate_20260531/llm_semantic_reranked_peer_network_top5_200.csv
    results/v13_peer_validity_gate_20260531/llm_semantic_reranked_return_gate_200.csv
    results/v13_peer_validity_gate_20260531/llm_semantic_reranked_fundamental_gate_200.csv
    docs/empirical_runs/76_v13_llm_reranked_peer_gate_20260531.md
    docs/empirical_runs/75_v13_peer_validity_completion_audit_20260531.md
```

人工抽查代理结果：

```text
annual same-industry text Top5:
    likely direct peer share = 0.8886
    weak review share        = 0.0053

annual global AI-word-stripped text Top5:
    likely direct peer share = 0.5422
    weak review share        = 0.0429

old CSMAR scope Top5:
    likely direct peer share = 0.4545
    weak review share        = 0.2167

random same-industry Top5:
    likely direct peer share = 0.0995
    weak review share        = 0.4608

low-similarity same-industry Top5:
    likely direct peer share = 0.0008
    weak review share        = 0.5778
```

Codex-assisted semantic coding，150 对抽查样本：

```text
old CSMAR scope Top5:
    direct peer share = 0.8000
    score 3 share     = 0.6000

annual same-industry text Top5:
    direct peer share = 0.7333
    score 3 share     = 0.5000

annual global AI-word-stripped text Top5:
    direct peer share = 0.7333
    score 3 share     = 0.5667

random same-industry Top5:
    direct peer share = 0.5333
    score 3 share     = 0.3333

low-similarity same-industry Top5:
    direct peer share = 0.3000
    score 3 share     = 0.2667
```

解释：

```text
这版语义抽查显示 CSMAR scope peers 在样本里略强，
但 random same-industry peers 也并非全是假 peer，
因为同业随机抽样本身会抽到真实竞品。

所以人工抽查支持：
    CSMAR scope peer 是可检查、可防守的竞品系统；
但它不支持：
    CSMAR scope peer 是无争议最优系统。

加入第二编码者后，排序更稳：
    年报同业文本 Top5 是人工可解释性最强口径；
    CSMAR scope Top5 通过人工 gate，但不是最强。
```

Agent second-coder semantic coding：

```text
annual same-industry text Top5:
    direct peer share = 0.7000
    score 3 share     = 0.4667

old CSMAR scope Top5:
    direct peer share = 0.5000
    score 3 share     = 0.1667

annual global AI-word-stripped text Top5:
    direct peer share = 0.4667
    score 3 share     = 0.2000

random same-industry Top5:
    direct peer share = 0.4000
    score 3 share     = 0.3000

low-similarity same-industry Top5:
    direct peer share = 0.1667
    score 3 share     = 0.1000
```

Two-coder mean direct-peer share：

```text
annual same-industry text Top5       = 0.7167
old CSMAR scope Top5                 = 0.6500
annual global AI-word-stripped Top5  = 0.6000
random same-industry Top5            = 0.4667
low-similarity same-industry Top5    = 0.2333

overall direct agreement = 0.6533
overall direct kappa     = 0.3240
```

三层 gate 的当前 decision matrix：

```text
1. annual same-industry annual-report text Top5
   文献口径最强；return / fundamentals / manual-proxy 都最好；
   但不复制当前 GenAI PeerCAR 负向主结果。

2. annual global AI-word-stripped text Top5
   文献口径强，能说明不是 AI 词驱动；
   但跨行业误配更多，也不复制当前主结果。

3. old CSMAR scope Top5
   不是最强 peer system，但通过了三层 validity gate：
       return comovement 强于 random / low-similarity；
       sales-growth / gross-margin comovement 强于 random / low-similarity；
       两编码者平均人工评分强于 random / low-similarity。
   它也是唯一保留当前显著 PeerCAR 结果的 peer system。
```

当前判断：

```text
1. X 的测度不是最大问题。
   生成式 AI 披露具体性可以明确写成：
   参考 Hope et al. (2016) 的披露具体性思想，
   并结合 Cheng et al. (2019) 的技术热潮披露分类逻辑。

2. Y 的测度也不是最大问题。
   PeerCAR[0,+1] 是标准 event-study / information-transfer Y，
   不是自造 Y。

3. 最大风险在 peer definition。
   old CSMAR scope peers 通过了 return 和 fundamentals validity gate，
   明显强于 random / low-similarity peers；
   但 annual-report text peers 的 return、sales-growth、gross-margin comovement
   都更强，且文献上更接近 Hoberg-Phillips / Cao et al. 的口径。

4. 旧 CSMAR scope Top5 可以继续作为当前显著结果的主 peer system，
   但必须透明写成：
       valid but not dominant text-based business-description peer system。

5. 如果严格追求最干净文献口径，
   annual-report text peers 更好；
   但它们没有复制当前 GenAI PeerCAR 主结果。

6. 因此下一步不是改 X/Y，
   而是决定：
       保留 CSMAR scope peer 并把 peer-validity section 做扎实；
       或转向 annual-report peers，重新寻找更稳的 Y/机制。

7. 人工抽查 gate 已经完成两版 LLM-assisted coding。
   但严格意义上的 Cao et al. 风格 LLM-generated peers 还没有构造成全量
   peer network；当前 LLM 证据是 peer-system validation coding，
   不是一个独立 LLM-peer network。

8. 已经为 LLM-generated / LLM-re-ranked peers 准备了 code-safe 候选菜单：
       200 focal firms
       5,094 candidate rows
   候选来源包括：
       annual same-industry text Top10
       CSMAR scope Top10
       annual global AI-word-stripped Top10
       random same-industry Top10

   当前已用 semantic re-ranking 构造出一版 LLM/semantic Top5 peer network，
   并完成 matched 200-focal return/fundamental gate。

9. LLM/semantic re-ranked peer gate：

   Matched 200-focal return comovement:

       annual same-industry text Top5       = 0.4359
       LLM/semantic re-ranked Top5          = 0.3998
       annual global AI-word-stripped Top5  = 0.3939
       CSMAR scope Top5                     = 0.3462
       random same-industry Top5            = 0.3118
       low-similarity same-industry Top5    = 0.2432

   Matched 200-focal fundamentals:

       LLM/semantic re-ranked Top5:
           sales-growth corr = 0.2169
           gross-margin corr = 0.4763

       CSMAR scope Top5:
           sales-growth corr = 0.2185
           gross-margin corr = 0.1955

       annual same-industry text Top5:
           sales-growth corr = -0.0373
           gross-margin corr = 0.5217

   解释：
       LLM/semantic re-ranked peers 在 return gate 中排第二，
       仅低于年报同业文本；在 fundamentals gate 中比 CSMAR 更均衡。
       这说明 LLM peer 不是摆设，可以作为非常有力的 measurement benchmark。
```

截至 2026-05-31 的 peer-validity gate 最终判断：

```text
最有文献支撑 / measurement-clean winner:
    annual same-industry annual-report text peers

最均衡的可解释替代:
    code-safe LLM/semantic re-ranked peers

能保留当前显著 GenAI PeerCAR 结果:
    old CSMAR scope peers

作为 placebo / falsification:
    random same-industry peers
    low-similarity same-industry peers

论文策略：
    若追求最干净测度，应改用 annual / LLM peers 并重跑主效应；
    若保留当前主结果，只能用 CSMAR scope peers，并把 annual / LLM peers
    作为 measurement benchmark，承认主结果对 peer definition 敏感。
```

## 2026-05-30 产品市场近邻测度升级与替换检验

已新增一套更接近 Hoberg and Phillips (2016, JPE) 的年报业务文本产品市场近邻构造。

```text
scripts/build_v12_annual_report_product_peers_20260530.py
scripts/run_v12_annual_report_peer_main_effect_20260530.py
docs/measurement/11_product_market_peer_network_hoberg_phillips_style_20260530.md
docs/measurement/12_peer_definition_literature_audit_20260530.md
docs/empirical_runs/67_v12_annual_report_peer_main_effect_20260530.md
docs/empirical_runs/68_v12_annual_peer_baseline_effect_20260530.md
results/v12_annual_report_product_peers_20260530/
results/v12_annual_report_peer_main_effect_20260530/
results/v12_annual_peer_baseline_effect_20260530/
```

核心变化：

```text
旧口径：
    CSMAR 公司基本资料中的 MAINBUSSINESS + BusinessScope

新口径：
    A 股年报 TXT 中的“报告期内公司从事的主要业务 / 主要业务 / 经营情况讨论与分析”等业务章节
    -> 中文 char 2-3 gram TF-IDF
    -> firm-pair cosine similarity
    -> Top5 / Top10 product-market peers
```

当前输出覆盖：

```text
event library:
    20,165 focal GenAI disclosure events

annual-report business text:
    26,312 firm-year rows, 2021-2025

event-peer panel:
    annual_report_peer_event_global_top10.csv              197,540 rows
    annual_report_peer_event_same_industry_d_top10.csv     196,369 rows
    annual_report_peer_event_global_ai_stripped_top10.csv  197,540 rows
```

替换主回归后的结果：

```text
规格：
    PeerCAR[0,+1]
    ~ AIActivePeer
    + Specificity_z × AIActivePeer
    + pre-window peer CAR controls
    + event FE
    + peer industry-week FE
    two-way clustered by event and peer firm

annual same IndustryNameD Top5:
    ext_any              coef =  0.001020, p = 0.144
    current_text_history coef =  0.000392, p = 0.570

annual global Top5:
    ext_any              coef = -0.000132, p = 0.875
    current_text_history coef = -0.001227, p = 0.168

annual global AI-word-stripped Top5:
    ext_any              coef = -0.000490, p = 0.551
    current_text_history coef = -0.001366, p = 0.124
```

GenAI 公告本身的平均 peer 反应：

```text
annual same IndustryNameD Top5:
    PeerCAR[0,+1] mean =  0.000209, p = 0.676

annual global Top5:
    PeerCAR[0,+1] mean =  0.000512, p = 0.325

annual global AI-word-stripped Top5:
    PeerCAR[0,+1] mean =  0.000580, p = 0.265

Top5 - ranks 6-10:
    annual same IndustryNameD:          coef = 0.000664, p = 0.137
    annual global:                      coef = 0.000786, p = 0.104
    annual global AI-word-stripped:     coef = 0.001172, p = 0.016
```

也就是说，年报 peer 网络下“GenAI 公告本身冲击竞品股价”的平均效应不是负向；
如果有差异，反而是 Top5 相对后排 peer 更正向。这不能支撑 competitive-threat 主故事。

当前判断：

```text
1. 这一步解决“产品市场近邻是不是我们自己提出”的文献锚问题：
   写法应为 Hoberg-Phillips-style Chinese A-share product-market peer network。

2. 但年报 peer 网络替换主回归后，旧 CSMAR 业务范围 Top5 的负向主效应没有复制。
   同细分行业年报 Top5 甚至为正向不显著；global / AI-word-stripped global Top5
   为负但远不显著。

3. 中文年报业务章节比美国 10-K Item 1 更嘈杂。
   全市场 Top10 偶有模板语言导致的跨行业误配；同 IndustryNameD 内 Top5 更可解释，
   但主效应也没有通过。

4. 因此不能把年报业务文本口径直接升为主 peer 定义。
   当前更诚实的处理是：

       主结果：旧 CSMAR business-scope / main-business text Top5
       方法锚：解释为 Hoberg-Phillips-style text-based product-market peers
       稳健性：年报业务文本 peer network 替换检验，但承认结果不复制

5. AI-word-stripped annual network 与原 annual-report global Top5 高度重合：
       mean overlap count = 4.74 / 5
       median overlap count = 5 / 5

   这说明产品市场相似度不是单纯由“AI / 智能 / 算法 / 大模型”等词驱动。

6. 新年报口径与旧 CSMAR 经营范围口径 Top5 重合度较低：
       mean overlap count ≈ 1.01 / 5

   这已经不是单纯“替代数据源”的问题，而是主结果对 peer network definition 敏感。
   论文如果继续写，必须把 product-market peer measurement 作为核心风险点处理。

7. 文献上可防守的 peer 系统包括：
       行业同业；
       Hoberg-Phillips / TNIC-style 文本产品市场同业；
       search-based peers；
       common analyst peers；
       technological peers；
       LLM-generated peers。

   当前项目最接近的是 Hoberg-Phillips-style 文本产品市场同业。
   但由于年报替换检验失败，旧 CSMAR scope Top5 不能再被无条件包装为“稳健竞品”。
   下一步若继续，必须先做 peer-validity validation，而不是继续堆主回归。
```

## 2026-05-28 最新判断

主线继续做，但需要把 claim 收紧到“短窗资本市场重估”。`Specificity_z` 暂时继续作为主文本细节指标使用；人工编码分支先从主线中拿掉。

最新收口检验：

```text
docs/empirical_runs/61_v8_measurement_final_checks_20260527.md
results/v8_measurement_final_checks_20260527
docs/design/09_project_outline_v8_after_measurement_checks_20260528.md
```

最新结论：

```text
1. 主市场反应结果仍成立。

   Final sample:
       first focal GenAI event × Top5 product-market peers
       N = 7,805
       events = 2,177
       peer firms = 3,345
       window = 2023-01-01 to 2026-05-20

   ext_any headline:
       coef = -0.002303
       p = 0.020

   加入 AI-theme abnormal return × AIActive 后：
       coef = -0.002112
       p = 0.032

   经济量级：
       median total market-cap effect ≈ RMB -21.85 million
       median float market-cap effect ≈ RMB -17.85 million

2. headline AIActive 继续用 ext_any。

   ext_any =
       prior CAC filing
    OR prior broad-AI patent grant
    OR prior broad-AI hiring in previous 365 days

   current_text_history 只能作为 robustness，
   因为它有显著 pre-window negative pattern。

3. 人工编码分支暂时不进入主线。

   当前处理：
       不把人工 score 当作推翻主测度的金标准；
       不在主文或外部评审包中突出该部分；
       只在内部记录中说明二者测的是不同概念。

   论文主线仍用 Specificity_z 表示 objective text-detail / disclosure concreteness proxy，
   但不把它写成“真实 GenAI 落地具体性”。
```

当前可安全写的主问题：

```text
更具体的 GenAI 披露是否被资本市场解读为竞争风险信号，
使事前 AI-active 的近产品市场同行出现更负的短窗相对重估？
```

当前不能写：

```text
GenAI 披露导致竞争对手价值损失；
GenAI 披露证明真实 business stealing；
Specificity_z 已经验证为“真实 GenAI 落地具体性”。
```

## 当前结论

当前主线继续保留，且比上一轮更稳。可执行版本是：

```text
Research question:
    具体化 GenAI 披露是否构成一种竞争威胁信号，
    使资本市场下调产品市场近邻中 AI-active 竞品的短窗估值？

Main X:
    焦点公司首次 GenAI 披露的 Specificity_z
    × 竞品事前 AIActivePeer
    × Top5 产品市场近邻样本定义

Main Y:
    竞品 market-model PeerCAR[0,+1]

Main sample:
    每家公司首次 GenAI 披露事件
    × Top5 产品市场近邻竞品

Main inference:
    event FE
    event FE + peer industry-week FE
    event × peer firm 双向聚类标准误
```

2026-05-25 网页版审阅后的执行口径：

```text
这不是平均 main effect，而是 conditional peer revaluation / heterogeneity effect。

主结论应写成：
    同一个焦点 GenAI 披露事件内，
    AI-active 的近产品市场竞品相对 non-AI-active 竞品出现更负的短窗 CAR，
    且这种相对负向重估随焦点披露 Specificity 更高而更强。

下一步不是继续堆新 Y，
而是补 specificity validation、pre-window controls、external AIActive 并列表、
    以及 Top1-3 / Top4-5 / Top6-10 的产品市场距离梯度。
```

2026-05-27 对“AI 供应链披露”分支做了单独诊断：

```text
docs/empirical_runs/57_v7_ai_supply_chain_disclosure_diagnostic_20260527.md
docs/empirical_runs/58_v7_ai_supply_chain_stacked_did_20260527.md
results/v7_ai_supply_chain_disclosure_diagnostic_20260527
results/v7_ai_supply_chain_stacked_did_20260527
```

结论：AI 供应链披露可以作为一个有趣的机制/边界分支，但不适合作为当前主线 DID。

```text
横截面事件窗：
    AI_supply_chain_exposure 对 Top5 peer CAR[0,+1] 为正，
    更像 category validation / AI 需求验证。

stacked event-DID:
    Top5 pair FE + event-time FE:
        Supply × Post[0,+1] coef = 0.000604, p = 0.485

    Top5 pair FE + event-time FE + calendar-date FE:
        coef = -0.000092, p = 0.901

    pretrend placebo:
        p = 0.631 / 0.772

    Top5 vs low-sim DDD:
        p = 0.964 / 0.974

判断：
    DID 没有打出可写主效应；横截面正向 peer revaluation
    不能升级为“有 AI 供应链披露 vs 无披露”的 DID 主线。
```

2026-05-27 又补了披露类型 horse-race：

```text
docs/empirical_runs/59_v7_disclosure_type_horserace_20260527.md
results/v7_disclosure_type_horserace_20260527
```

披露类型按粗规则拆为：

```text
own_impl:          自身 GenAI 实施 / 部署 / 产品 / 应用
supply_chain:      AI 算力、数据中心、半导体、光模块、液冷、终端、数据资源等供应链暴露
generic_attention: 泛泛关注 AI / GenAI
denial_no_current: 否认或暂无相关业务 / 合作
```

关键结论：

```text
1. 披露类型 dummy 本身不能替代原主结果。
   加入四类 Type × AIActive 后，
   Specificity_z × AIActive 仍显著为负：

   ext_any:
       coef = -0.002394, p = 0.015

   current_text_history:
       coef = -0.002107, p = 0.045

2. supply_chain 披露不产生 AI-active close peers 的负向重估。
   但在无 event FE 的描述性平均 peer effect 中为正：

   ai_supply_chain_exposure:
       coef = 0.004225, p = 0.026

   解释：供应链披露更像 category validation / AI 需求验证，
   不是 competitive-risk signal。

3. ext_any 口径下，own_impl 内部的
   Specificity_z × AIActive 为负且边际显著：

   own_impl_spec_ai:
       coef = -0.002194, p = 0.075

   这支持“具体化披露的竞争威胁含义更接近真实实施/部署承诺”，
   但不能单独把 own_impl dummy 升成主 X。
```

2026-05-27 已补 task 4/5：lead-lag 图和产品市场近邻有效性：

```text
docs/empirical_runs/60_v7_event_time_peer_validity_20260527.md
results/v7_event_time_peer_validity_20260527/event_time_spec_ai_daily.png
results/v7_event_time_peer_validity_20260527/window_lead_lag_coefficients.png
results/v7_event_time_peer_validity_20260527/proximity_gradient_coefficients.png
docs/design/08_paper_outline_current_20260527.md
```

判断：

```text
1. daily event-time 单日拆分后系数不强，适合作透明度检查，
   不适合作 headline estimator。

2. window lead-lag 更适合论文展示：
   ext_any 在 pre-window 不显著，
   [0,+1] 为负且边际显著；
   text-history 仍有长 pre-window concern，
   所以 headline 继续用 ext_any。

3. 产品市场近邻有效性更强：
   Top1-3 / ext_any:
       coef = -0.003252, p = 0.016

   Top6-10、low-similarity、random same-industry 均不显著。

4. peer-set 描述支持 Top5 不是普通行业同行：
   mean product similarity:
       Top1-3 = 0.255
       Top4-5 = 0.206
       Top6-10 = 0.180
       random same-industry = 0.055
       low-similarity = 0.006
```

2026-05-25 已补 design freeze 与 specificity validation 起步包：

```text
docs/design/05_design_freeze_20260525.md
docs/design/06_specificity_validation_codebook_20260525.md
docs/design/07_specificity_validation_execution_plan_20260525.md
docs/prompts/55_specificity_validation_llm_coding_prompt_20260525.md
docs/empirical_runs/55_specificity_validation_sample_20260525.md
data/specificity_validation/specificity_validation_sample_300_20260525.csv
data/specificity_validation/specificity_validation_coding_template_300_20260525.csv
data/specificity_validation/specificity_validation_llm_input_300_20260525.jsonl
```

冻结后的主表口径：

```text
Main AIActive = ext_any
Robustness AIActive = current_text_history
Headline spec = within-event FE heterogeneity
DDD = robustness / placebo
Main sample = first focal GenAI event × Top5 product-market peers
Main Y = signed market-model PeerCAR[0,+1]
```

Specificity validation 已生成 300 条事件样本：

```text
eligible focal events = 2,177
validation sample = 300
specificity terciles = low 100 / mid 100 / high 100
```

2026-05-25 一次性复核已完成：

```text
docs/empirical_runs/53_v6_final_review_checks_20260525.md
results/v6_final_review_checks_20260525
```

2026-05-25 又补了两项针对审稿人最可能质疑的核心稳健性：

```text
docs/empirical_runs/54_v6_focal_good_news_pretrend_checks_20260525.md
results/v6_focal_good_news_pretrend_checks_20260525
```

结论：排除“焦点公司自身利好程度”混杂、以及净化 peer pre-trend 后，`Specificity_z × AIActivePeer` 仍然稳定。

```text
Task 1: 加入焦点公司自身 FocalCAR[0,+1] 及 FocalCAR[0,+1] × AIActive。

Top5 / announcement clean / CAR[0,+1] /
event FE + peer industry-week FE /
PeerCAR[-10,-2] + PeerCAR[-20,-2] controls:

text-history AIActive:
    baseline coef = -0.002275, p = 0.027
    + FocalCAR coef = -0.002275, p = 0.027
    + FocalCAR × AIActive coef = -0.002283, p = 0.027

external ext_any:
    baseline coef = -0.002303, p = 0.020
    + FocalCAR coef = -0.002303, p = 0.020
    + FocalCAR × AIActive coef = -0.002307, p = 0.020

注意：FocalCAR[0,+1] 是 event-level 变量，在 event FE 下会被吸收；
真正有识别含义的是 FocalCAR[0,+1] × AIActive。
```

```text
Task 2: 用 PeerCAR[-10,-2] 净化 PeerCAR[0,+1] 后重跑。

text-history AIActive:
    residualized Y baseline coef = -0.002274, p = 0.027
    residualized Y + FocalCAR × AIActive coef = -0.002281, p = 0.026

external ext_any:
    residualized Y baseline coef = -0.002295, p = 0.021
    residualized Y + FocalCAR × AIActive coef = -0.002300, p = 0.020

样本量：
    N = 7,805
    events = 2,177
    peer firms = 3,345
    clustering = event_id × peer_code
```

结论很清楚：资本市场主效应通过当前 go/no-go 门槛，但披露扩散机制在更严格口径下不显著。

```text
Top5 / CAR[0,+1] / announcement clean /
event FE + peer industry-week FE /
pre-window CAR controls:

text-history AIActive:
    coef = -0.002025, p = 0.036

external ext_any:
    coef = -0.002109, p = 0.024

ext_plus_history:
    coef = -0.002265, p = 0.011

Top10 同口径：
    text-history p = 0.033
    ext_any p = 0.010
    ext_plus_history p = 0.011
```

新增几条关键判断：

```text
1. Specificity 不是简单 length / AI keyword count / source attention / numeric detail：
   加入这些 observable text controls 后，ext_any 口径仍 p = 0.021；
   text-history 口径全控后 p = 0.071，方向和量级稳定。

2. 产品市场距离梯度基本支持竞争接近度：
   Top1-3 ext_any coef = -0.003252, p = 0.016；
   Top6-10 不显著；
   low-similarity 和 random same-industry peer 均不显著。

3. pre-window concern 需要继续正面写：
   text-history AIActive 仍有较长 pre-window pattern；
   external ext_any 没有同样的 pre-window pattern。
   所以主文必须并列展示 text-history 与 ext_any。

4. peer disclosure diffusion 不能再当强机制：
   在 focal-event FE + baseline peer GenAI-disclosure-rate control 后，
   Top5 / Top10 的 60/90/180 天响应均不显著。
   它只能保留为描述性后续反应，不能承担论文机制主张。
```

目前最稳的结果是：

```text
Top5 first focal event, market-model CAR[0,+1],
同时剔除焦点公司与竞品的重大/定期/业绩/风险类公告：

event FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.008

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.020

低相似度同行 placebo:
coef ≈ 0, p > 0.90
```

AI 词剔除版产品相似度也保留同一方向：

```text
Top5 first focal event, AI-word-stripped product similarity,
market-model CAR[0,+1],
同时剔除焦点公司与竞品的重大/定期/业绩/风险类公告：

event FE:
Specificity_z × AIActivePeer
coef = -0.002124, p = 0.011

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002041, p = 0.033
```

公告清洗版 100 次随机同业 placebo 也支持 Top5 不是随机同业波动：

```text
真实 Top5, drop either cleaning announcement, CAR[0,+1]:
coef = -0.002298

100 次同一细行业随机非 Top10 peer:
random median coef = -0.000055
random p05 coef = -0.001483
share random <= true Top5 = 0.00
```

外部版 AIActivePeer 第一轮也支持主方向，但需要保守表述：

```text
ext_any = prior CAC
       OR prior broad-AI patent grant
       OR >=1 broad-AI job posting in prior 365 days

Top5, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001897, p = 0.028
event FE + peer industry-week FE coef = -0.001800, p = 0.058

Top10, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001654, p = 0.004
event FE + peer industry-week FE coef = -0.001493, p = 0.014

低相似度同行 placebo:
coef ≈ 0, p = 0.888
```

把外部 AIActivePeer 接到 AI 词剔除版产品相似度后，结果进一步变稳：

```text
AI-word-stripped Top5, ext_any,
drop either cleaning announcement, CAR[0,+1]:

event FE:
coef = -0.002118, p = 0.011

event FE + peer industry-week FE:
coef = -0.002321, p = 0.011
```

当前最安全的论文表述是：

```text
焦点公司首次 GenAI 披露越具体，
事前已经 AI-active 的 Top5 产品市场近邻竞品，
在 [0,+1] 窗口出现更负的 market-model CAR；
该结果在剔除焦点公司与竞品的重大/定期/业绩/风险类公告后仍成立，
低相似度同行没有类似反应；
同一细行业随机 peer 无法复制该负向强度；
剔除产品描述中的 AI / 大模型 / 智能等通用词后，结论仍保留；
用 CAC、AI 专利授权与事前 AI 招聘构造的外部 AIActivePeer 也得到方向一致的结果；
外部 AIActivePeer 与 AI 词剔除版产品相似度同时使用时，Top5 结果仍显著；
非 GenAI 互动平台 pseudo-event 不能复制该结果；
投资者 GenAI 问题触发样本仍支持主方向。
```

当前还不能过度声称：

```text
不能说“GenAI 披露导致竞品价值下降”；
更稳的说法是“市场把具体化 GenAI 披露解读为可信竞争威胁信号”。

不能把同伴披露扩散当主 Y；
它只能作为机制 / 后续反应表。

不能把交易活跃度当主 Y；
它只能作为辅助市场反应证据。

不能把机制写成纯粹 business stealing；
focal CAR sign 分解没有显示“焦点公司涨、竞品跌”的清晰模式。

不能忽略 pre-window concern；
text-history AIActivePeer 存在显著 pre-window pattern，
因此主表或稳健性表必须加入 pre-window peer CAR 控制。
```

2026-05-25 已把三张成稿级表的试跑版补完：

```text
1. 主表重跑版已完成：
   Top5 / CAR[0,+1] / announcement clean / strong FE /
   event × peer firm two-way clustering / pre-window CAR controls。
   text-history、ext_any、ext_plus_history 均保留显著。

2. Specificity validation 表已完成第一版：
   控制 length、AI keyword intensity、source attention、numeric/component proxy 后，
   主方向和量级保留；ext_any 口径最稳。

3. Product-market proximity gradient 表已完成：
   Top1-3、Top4-5、Top6-10、low-similarity、random peers，
   结果主要集中在 Top1-3；low-similarity 和 random peers 不显著。

下一步不是再找新主 Y，而是把这些表整理成论文主表和附录表。
```

## 当前主线 v6

当前不再把“竞品是否跟进 GenAI 披露”作为主 Y。这个设计的 X 和 Y 都来自互动平台 / 调研问答文本，距离太近，最多适合作为机制。

最新主线调整为：

```text
Main question:
    一家上市公司披露 GenAI / 大模型 / AIGC 信息后，
    资本市场是否会重新评估其产品市场竞品？

Main Y:
    竞品短窗资本市场反应
    signed PeerCAR[-1,+1] / PeerCAR[0,+1]
    abnormal turnover / abnormal volume

Mechanism Y:
    竞品随后是否在互动平台 / 调研问答 / 公告中跟进 GenAI 披露

Validation Y:
    竞品后续 CAC 生成式 AI 服务备案 / 深度合成算法备案
```

当前入口文档：

```text
docs/empirical_runs/53_v6_final_review_checks_20260525.md
docs/empirical_runs/50_v6_external_ai_active_on_ai_stripped_similarity_20260524.md
docs/empirical_runs/52_v6_identification_strengthening_checks_20260524.md
docs/empirical_runs/51_v6_peer_firm_fe_identification_check_20260524.md
docs/empirical_runs/49_v6_external_ai_active_peer_checks_20260524.md
docs/empirical_runs/48_v6_announcement_clean_random_placebo_20260524.md
docs/empirical_runs/47_v6_ai_stripped_similarity_checks_20260524.md
docs/empirical_runs/46_v6_announcement_clean_and_trading_response_20260524.md
docs/current/41_v6_market_reaction_main_peer_diffusion_mechanism_20260523.md
```

## 核心研究设计

### 观察单元

```text
focal GenAI disclosure event i,t × product-market peer firm j
```

### 主 X

主解释结构是：

```text
GenAI_Disclosure_Event_i,t
× ProductSimilarity_i,j
× AIActivePeer_j,t-1
```

其中：

- `GenAI_Disclosure_Event_i,t`: 焦点公司在公开投资者沟通中的 GenAI 披露；
- `ProductSimilarity_i,j`: 焦点公司与竞品的产品市场相似度；
- `AIActivePeer_j,t-1`: 竞品在事件前是否已经处于 AI / GenAI 竞争空间。

`Specificity_i,t` 仍然保留，但不再单独承担主设计：

```text
Specificity_i,t
× ProductSimilarity_i,j
× AIActivePeer_j,t-1
```

它的作用是检验“披露越具体，竞争性重估越强”，而不是把论文写成“文本具体性预测另一个文本事件”。

### 主 Y

主 Y 必须外部于披露文本系统：

```text
PeerCAR[-1,+1]
PeerCAR[0,+1]
Peer abnormal turnover
Peer abnormal volume
```

推荐主表先用 signed CAR，而不是 `|CAR|`：

```text
如果机制是竞争威胁，方向应当是 AI-active 近邻竞品出现更负面的重估；
如果只看 |CAR|，会把竞争性重估和一般信息含量混在一起。
```

## 当前识别与估计方式

当前不是 IV，也不是标准 DID。更准确地说，这是一个短窗事件研究下的横截面信息揭示设计：

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_e × AIActivePeer_{j,t-5}
  + event FE_e
  + peer industry × week FE
  + peer pre-window CAR controls
  + error_{e,j}
```

其中 `e` 是焦点公司首次 GenAI 披露事件，`j` 是其产品市场竞品。Top5 / Top10 产品相似度主要用于定义竞品样本，而不是在主回归中继续放一个连续相似度项。

估计方式：

```text
absorbed OLS
Y 和 X 先按固定效应去均值
再用 OLS 估计
标准误按 event_id × peer_code 双向聚类
```

`event FE` 吸收所有焦点事件层面的共同冲击，包括焦点公司当日信息、披露具体性本身、市场对该事件的平均反应。因此主系数不是在比较“高具体性事件的竞品平均跌不跌”，而是在比较：

```text
同一个焦点事件下，
AI-active peer 与 non-AI-active peer 的 CAR 差异；
并且这个差异是否随着焦点披露 Specificity 更高而更负。
```

加入 `peer industry × week FE` 后，进一步吸收同一周同一竞品行业的市场波动。最新又补了一版 `peer firm FE`，用来检验是否完全由某些竞品公司固定特征驱动；结果见：

```text
docs/empirical_runs/51_v6_peer_firm_fe_identification_check_20260524.md
```

识别假设必须保守表述：

```text
短窗内，在剔除焦点公司与竞品的重大/定期/业绩/风险类公告后，
没有其他与 Specificity × AIActivePeer 同步变化的竞品层面未观测冲击；
Top5 产品市场近邻确实代表竞争替代关系；
AIActivePeer 使用事件前可观察信息，避免 look-ahead。
```

因此论文不能写成“具体披露因果导致竞品下跌”。更稳的写法是：

```text
资本市场将具体化 GenAI 披露解读为可信竞争威胁信号，
并对事前处于 AI 竞争空间的产品市场近邻进行更负面的相对重估。
```

## 机制：产品市场同伴披露扩散

`focal GenAI disclosure -> rival GenAI disclosure` 现在降级为机制表。

机制问题：

```text
焦点公司 GenAI 披露后，
产品市场更接近的竞品是否更可能在 60 / 90 / 180 天内首次跟进 GenAI 披露？
```

早期 CSMAR smoke test 支持“同伴披露扩散”这个描述性现象：

```text
全部焦点事件 Top10：
30d coef = 0.0041, p = 0.012
60d coef = 0.0060, p = 0.003
90d coef = 0.0061, p = 0.006

每家公司首次焦点事件 Top10：
60d coef = 0.0112, p = 0.017
90d coef = 0.0131, p = 0.009
180d coef = 0.0173, p = 0.001

pre-window placebo:
30 / 60 / 90 / 180d 均不显著
```

但 2026-05-25 的更严格版本加入 focal-event FE 与 peer 事前 365 天 GenAI 披露频率控制后，`Specificity × Similarity` 不显著：

```text
Top5:
60d p = 0.935
90d p = 0.622
180d p = 0.886

Top10:
60d p = 0.317
90d p = 0.657
180d p = 0.555
```

解释边界：

```text
只能说早期描述性结果提示可能存在同伴披露扩散；
更严格口径下并不能证明“具体披露触发竞品跟进披露”。
因此它不能承担核心机制，只能作为补充描述或后续探索。
```

对应文档：

```text
docs/empirical_runs/40_csmar_peer_diffusion_main_effect_20260523.md
```

## v6 主结果初步试跑

已用完整 CSMAR 事件库跑了一版市场调整 CAR smoke test：

```text
docs/empirical_runs/42_v6_csmar_peer_market_reaction_smoke_20260523.md
results/v6_csmar_peer_market_reaction_smoke_20260523
```

同时已重跑一版更适合作为主表的简化主效应：

```text
docs/empirical_runs/43_v6_simple_main_effect_20260523.md
results/v6_simple_main_effect_20260523
```

当前读法：

```text
简化主效应：
    ProductSimilarity 用于定义 Top5 / Top10 peer sample；
    主交互只保留 Specificity × AIActivePeer。

每家公司首次 GenAI 披露样本，Top5 clean:
    Top5 clean CAR[0,+1],
    Specificity_z × AIActivePeer
    coef = -0.001669, p = 0.024

    Top5 clean CAR[-1,+1],
    Specificity_z × AIActivePeer
    coef = -0.002659, p = 0.014

    Top10 clean CAR[-1,+1],
    Specificity_z × AIActivePeer
    coef = -0.002113, p = 0.041
```

这说明 v6 主线目前有初步信号，但还不是正式结果。最合理的暂定表述是：

```text
焦点公司首次 GenAI 披露越具体，
产品市场近邻中事前 AI-active 的竞品，
短窗 CAR 越负。
```

下一步必须用 market-model CAR、低相似度 / 随机 peer placebo、外部 AIActivePeer 和竞品同日公告清洗来复核。

2026-05-24 已补第一轮复核：

```text
docs/empirical_runs/44_v6_market_model_and_placebo_20260524.md
results/v6_supplement_market_model_placebo_20260524
```

关键结果：

```text
market-model CAR，首次披露样本，true Top5 peers:

CAR[0,+1]:
Specificity_z × AIActivePeer
coef = -0.001825, p = 0.0166

CAR[-1,+1]:
Specificity_z × AIActivePeer
coef = -0.001921, p = 0.0496

低相似度同行 placebo:
CAR[0,+1] p = 0.828
CAR[-1,+1] p = 0.750

true Top5 vs 低相似度同行差异:
CAR[0,+1] p = 0.038
CAR[-1,+1] p = 0.037
```

目前最需要继续处理的是随机同行 placebo：`CAR[-1,+1]` 有边际负向，说明还需要 industry-week FE、多次随机抽样和同日公告清洗。

2026-05-24 已继续完成主效应完整复核：

```text
docs/empirical_runs/45_v6_main_effect_full_checks_20260524.md
results/v6_main_effect_full_checks_20260524
```

关键结果：

```text
market-model CAR，首次披露样本，true Top5 peers:

CAR[0,+1], event FE:
Specificity_z × AIActivePeer
coef = -0.001825, p = 0.0166

CAR[0,+1], event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.001513, p = 0.0839

低相似度同行 placebo:
CAR[0,+1] p = 0.828
CAR[-1,+1] p = 0.750

100 次随机同业 placebo:
CAR[0,+1] 下没有一次随机抽样比 true Top5 更负；
CAR[-1,+1] 下 event FE 没有一次更负，加入 peer industry-week FE 后只有 1% 更负。
```

当前更稳的主表述应收窄为：

```text
焦点公司首次 GenAI 披露越具体，
事前已经 AI-active 的 Top5 产品市场近邻竞品，
在 [0,+1] 窗口出现更负的 market-model CAR。
```

2026-05-24 已补公告污染清洗与交易活跃度检验：

```text
docs/empirical_runs/46_v6_announcement_clean_and_trading_response_20260524.md
results/v6_announcement_clean_checks_20260524
results/v6_trading_response_checks_20260524
```

公告补数来自 CSMAR 公告基本信息表、公告证券关联表、公告分类关联表，已整理为：

```text
announcement_stock_day_flags_2023_2026.csv.gz
覆盖 2023-01-01 至 2026-05-25
A 股证券关联行数 2,415,820
股票-日期公告标记 695,403 行
```

公告清洗后的关键结果：

```text
Top5 first focal event, market-model CAR[0,+1],
剔除焦点公司与竞品的重大/定期/业绩/风险类公告后：

event FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.008

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.020

低相似度同行 placebo:
coef ≈ 0, p > 0.90
```

Top5 vs 低相似度同行差异检验：

```text
Specificity_z × AIActivePeer × TrueTop5

同时剔除焦点与竞品清洗公告，event FE:
CAR[0,+1] coef = -0.001718, p = 0.018
CAR[-1,+1] coef = -0.002503, p = 0.009

但加入 peer industry-week FE 后差异项不再显著。
```

交易活跃度补充 Y：

```text
异常成交额 / 异常成交量方向也偏负；
Top5 清洗样本中 abnormal log trading value [0,+1],
event FE + peer industry-week FE:
coef = -0.0397, p = 0.027

但单次随机同业 placebo 在清洗样本中出现正向异常成交额，
因此交易活跃度只作为辅助事实，不升级为主 Y。
```

当前最稳主表述进一步收窄为：

```text
焦点公司首次 GenAI 披露越具体，
事前已经 AI-active 的 Top5 产品市场近邻竞品，
在 [0,+1] 窗口出现更负的 market-model CAR；
该结果在剔除焦点公司与竞品的重大/定期/业绩/风险类公告后仍成立，
低相似度同行没有类似反应。
```

`CAR[-1,+1]` 可以作为补充窗口，不宜作为唯一 headline。

2026-05-24 又补了 AI 词剔除版产品相似度检验：

```text
docs/empirical_runs/47_v6_ai_stripped_similarity_checks_20260524.md
results/v6_ai_stripped_similarity_checks_20260524
```

处理逻辑：

```text
从主营业务 / 产品描述文本中剔除：
AI / AIGC / GenAI / ChatGPT / DeepSeek / 大模型 / 生成式人工智能
机器学习 / 深度学习 / 自然语言处理 / 算法 / 智能 / 智慧 等词，
然后重新计算产品市场相似度与 Top5 / Top10 peer network。
```

关键结果：

```text
Top5 first focal event, AI-word-stripped product similarity,
同时剔除焦点与竞品清洗公告，CAR[0,+1]:

event FE:
Specificity_z × AIActivePeer
coef = -0.002124, p = 0.011

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002041, p = 0.033
```

与原始 peer network 的重合度：

```text
Top5 mean overlap = 0.956, median overlap = 1.000
Top10 mean overlap = 0.959, median overlap = 1.000
```

这说明当前主结果不是简单由产品描述中共同出现 AI 词造成的。

2026-05-24 进一步补了公告清洗版 100 次随机同业 placebo：

```text
docs/empirical_runs/48_v6_announcement_clean_random_placebo_20260524.md
results/v6_announcement_clean_random_placebo_20260524
```

关键结果：

```text
真实 Top5, drop either cleaning announcement, CAR[0,+1]:
coef = -0.002298

100 次同一细行业随机非 Top10 peer:
random mean coef = -0.000050
random median coef = -0.000055
random 5th percentile = -0.001483
share random <= true Top5 = 0.00
```

这说明同一细行业随机公司不能复制真实 Top5 产品市场近邻的负向强度。

2026-05-24 又补了外部 pre-event AIActivePeer 第一轮：

```text
docs/empirical_runs/49_v6_external_ai_active_peer_checks_20260524.md
results/v6_external_ai_active_20260524
results/v6_external_ai_active_checks_20260524
```

外部证据规模：

```text
CAC A 股 lower-bound 匹配：106 家
AI 专利标题匹配：101 家
GenAI 专利标题匹配：28 家
broad AI 招聘：2,814 家
GenAI 招聘：1,657 家
post-ChatGPT 历史 GenAI 披露：2,771 家
```

纯外部主口径：

```text
ext_any = prior CAC
       OR prior broad-AI patent grant
       OR >=1 broad-AI job posting in prior 365 days
```

关键结果：

```text
Top5, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001897, p = 0.028
event FE + peer industry-week FE coef = -0.001800, p = 0.058

Top10, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001654, p = 0.004
event FE + peer industry-week FE coef = -0.001493, p = 0.014

低相似度同行 placebo:
coef ≈ 0, p = 0.888
```

读法：

```text
纯外部 ext_any 没有推翻主结果；
它支持方向和经济量级，但 Top5 强 FE 下是边际显著。
加入历史披露文本的 ext_plus_history 更稳，但只能作为扩展口径。
```

2026-05-24 进一步补了外部 AIActivePeer × AI 词剔除产品相似度联合检验：

```text
docs/empirical_runs/50_v6_external_ai_active_on_ai_stripped_similarity_20260524.md
results/v6_external_ai_active_ai_stripped_checks_20260524
```

关键结果：

```text
AI-word-stripped Top5, ext_any,
drop either cleaning announcement, CAR[0,+1]:

event FE coef = -0.002118, p = 0.011
event FE + peer industry-week FE coef = -0.002321, p = 0.011

AI-word-stripped Top10, ext_any,
event FE coef = -0.001525, p = 0.009
event FE + peer industry-week FE coef = -0.001343, p = 0.029
```

这说明两个关键防御可以同时成立：

```text
不是 AI 词共同出现定义竞品；
也不是历史披露文本单独定义 AI-active peer。
```

2026-05-24 又补了 peer firm FE 识别检验：

```text
docs/empirical_runs/51_v6_peer_firm_fe_identification_check_20260524.md
results/v6_peer_firm_fe_checks_20260524
```

关键结果：

```text
Current text-history AIActivePeer, original Top5,
drop either cleaning announcement, CAR[0,+1]:

event FE + peer firm FE:
coef = -0.002152, p = 0.058

event FE + peer firm FE + peer industry-week FE:
coef = -0.002915, p = 0.053

Current text-history AIActivePeer, original Top10:
event FE + peer firm FE:
coef = -0.001800, p = 0.009

event FE + peer firm FE + peer industry-week FE:
coef = -0.001922, p = 0.012

low-similarity placebo:
coef = -0.000261, p = 0.683
```

纯外部 `ext_any` 在 peer firm FE 下变弱：

```text
Original Top5:
event FE + peer firm FE p = 0.157
event FE + peer firm FE + peer industry-week FE p = 0.847

AI-word-stripped Top5:
event FE + peer firm FE p = 0.230
event FE + peer firm FE + peer industry-week FE p = 0.449
```

因此当前经验判断是：

```text
主表仍以 text-history AIActivePeer 为核心；
外部 ext_any 作为验证层，说明方向不是纯文本同源造成；
peer firm FE 作为更严检验，结果支持主口径和 Top10，但不支持把 ext_any 直接升级为 headline。
```

2026-05-24 继续补了五类识别增强检验：

```text
docs/empirical_runs/52_v6_identification_strengthening_checks_20260524.md
results/v6_identification_strengthening_20260524
```

正式 DDD 结果方向正确，但强度不均匀：

```text
True Top5 vs random Top5, current text-history AIActive:
event FE coef = -0.002315, p = 0.027
event FE + peer industry-week FE coef = -0.001904, p = 0.094

True Top5 vs low-similarity Top5, current text-history AIActive:
event FE p = 0.132
event FE + peer industry-week FE p = 0.300

ext_plus_history 口径下，DDD 对 low/random peers 多数为 5%-10% 显著或边际显著。
```

pre-window placebo 暴露了一个真实风险：

```text
true Top5, current text-history AIActive:
CAR[-10,-2] p = 0.013 / 0.043
CAR[-20,-2] p = 0.009 / 0.003
```

但加入 pre-window peer CAR 控制后，事件窗主结果仍保留：

```text
current text-history AIActive,
control CAR[-10,-2] and CAR[-20,-2],
event FE + peer industry-week FE:
coef = -0.002025, p = 0.036

external ext_any,
control CAR[-10,-2] and CAR[-20,-2],
event FE + peer industry-week FE:
coef = -0.002109, p = 0.024

ext_plus_history,
control CAR[-10,-2] and CAR[-20,-2],
event FE + peer industry-week FE:
coef = -0.002265, p = 0.011
```

focal CAR sign 分解不支持简单 business stealing：

```text
focal CAR positive:
p = 0.144 / 0.230

focal CAR non-positive:
p = 0.024 / 0.048

interaction with focal positive:
p = 0.694 / 0.652
```

投资者问题触发样本支持主方向：

```text
Question contains GenAI terms:
event FE coef = -0.001837, p = 0.058
event FE + peer industry-week FE coef = -0.002123, p = 0.050

IIP quick question-triggered sample:
event FE coef = -0.002384, p = 0.056
event FE + peer industry-week FE coef = -0.002411, p = 0.091
```

Non-GenAI IIP pseudo-event placebo 不复制主结果：

```text
2,652 pseudo focal events
14,790 clean event-peer rows

event FE coef = +0.002349, p = 0.358
event FE + peer industry-week FE coef = +0.002284, p = 0.372
```

五类补强后的总体判断：

```text
题目仍然活着，但需要保守写。

可说：
    具体化 GenAI 披露被市场解读为 competitive-risk signal；
    负向重估集中在事前 AI-active 的产品市场近邻；
    该模式不能由普通 non-GenAI 互动文本、随机 peer、低相似度 peer 完整复制；
    并且在控制 pre-window peer CAR 后仍保留。

不可说：
    这是强因果；
    这是明确 business stealing；
    这是完全没有 pre-trend concern 的干净事件研究。
```

## 已完成的数据扩展

CSMAR 下载资料已整理到：

```text
/Users/mac/computerscience/第三方资料/04_项目专用资料/T05_GAI_financial_disclosure_market_reaction/csmar_downloads_20260523
```

完整 GenAI 事件库已经建好：

```text
results/csmar_genai_event_library_20260523
```

事件库规模：

```text
IIP:
    raw rows = 2,460,811
    answer-level GenAI events = 25,544
    firm-day GenAI events = 15,460
    firms = 2,587

IR_QA:
    raw rows = 1,773,908
    answer-level GenAI events = 15,147
    firm-day GenAI events = 8,268
    firms = 1,274

Combined:
    answer-level GenAI events = 40,691
    firm-day GenAI events = 23,454
    firms = 2,800
    post-2023 firm-day events = 22,701
```

对应脚本和记录：

```text
scripts/build_csmar_genai_event_library_20260523.py
docs/empirical_runs/38_csmar_genai_event_library_smoke_20260523.md
```

## 已降级路线

### v5.1：IIP -> IIP / CAC response

v5.1 的原始设想是：

```text
焦点公司 IIP GenAI 披露具体性
× 产品市场相似度
-> 竞品 30/60/90 天内是否跟进 IIP GenAI 披露
```

现在判断：

```text
同伴披露扩散可以做机制；
不适合作为主 Y。
```

原因：

- X 和 Y 都是 GenAI 披露文本，经济距离太近；
- 同源平台和同一分类器容易被质疑为共同方法偏误；
- 最新 CSMAR 试跑中，`Specificity × Similarity` 对竞品披露响应不显著；
- 真正有信号的是产品相似度的同伴扩散主效应，更像机制而不是终点。

对应文档：

```text
docs/current/37_v5_1_layered_iip_cac_disclosure_response_smoke_20260523.md
docs/empirical_runs/39_csmar_v5_1_response_smoke_20260523.md
```

### v5：rival hiring

v5 想把主 Y 改成竞品后续 AI-skilled hiring。现在仍不建议作为当前主线：

```text
招聘数据覆盖 2014-01-07 至 2026-03-10，约 899.6 万条；
但招聘是慢变量，难解释为焦点披露事件后的短期竞品响应；
更适合构造 pre-event AIActivePeer / prior AI capability。
```

对应文档：

```text
docs/current/34_v5_long_term_rival_ai_investment_design_20260522.md
docs/current/36_recruitment_data_and_v5_y_risk_audit_20260522.md
```

### v4：AI-active peer CAR

v4 是当前 v6 的直接前身：

```text
一家公司的 GenAI 披露越具体，
资本市场是否会对“产品越相似、且已经 AI-active 的竞品”作出更负面的短窗重估？
```

早期证据：

```text
Top5 clean CAR[-1,+1],
Specificity × ProductSimilarity × AIActivePeer:
coef = -0.0103, p = 0.005

加 peer controls:
coef = -0.0095, p = 0.011
```

更严格双向聚类后：

```text
Top5 clean CAR[-1,+1],
AIActivePeer = t-5 preobservable public or annual evidence:
coef = -0.0104, p = 0.055 without controls
coef = -0.0094, p = 0.084 with controls

Top10 不再稳健。
```

因此 v6 不是放弃 v4，而是用完整 CSMAR 事件库重新跑 v4 主问题，并把披露扩散放到机制表。

对应文档：

```text
docs/current/31_v4_experimental_design_ai_active_peer_20260522.md
docs/current/32_v4_go_no_go_diagnostics_20260522.md
```

## 下一步

v6 主市场反应已经通过第一轮公告污染清洗。下一步不是回退，也不是扩展新 Y，而是继续把主效应打硬：

```text
完整 CSMAR GenAI 事件库
× 产品市场 Top5 / Top10 竞品
× 日收益 / 成交量数据
-> peer CAR / abnormal turnover
```

最低 go/no-go 已部分通过：

1. AI-active 近邻竞品的 signed CAR 方向合理；
2. 双向聚类 by focal event and peer firm 后仍有信号；
3. Top5 经济含义更清楚，Top10 方向基本一致；
4. 低相似度 peer placebo 不成立；
5. 同伴披露扩散机制表方向一致。
6. 剔除焦点公司与竞品重大/定期/业绩/风险类公告后，Top5 `CAR[0,+1]` 仍成立。
7. 剔除产品描述中的 AI / 大模型 / 智能等通用词后，Top5 `CAR[0,+1]` 仍成立。
8. 公告清洗版 100 次随机同业 placebo 无法复制真实 Top5 的负向强度。
9. 外部 `AIActivePeer = CAC + AI专利授权 + 过去365天AI招聘` 支持方向和 placebo，但 Top5 强 FE 下为边际显著。
10. 外部 `AIActivePeer` 与 AI 词剔除版产品相似度同时使用时，Top5 `CAR[0,+1]` 仍显著。

下一轮优先做两件事：

1. **精修外部 `AIActivePeer`**
   现在已有第一版外部口径，但还应改进 CAC 公司匹配、AI 专利分类和招聘关键词人工复核。

2. **准备主表 / 稳健性表结构**
   主表用历史披露口径，外部 `ext_any` 放验证表；不要把 p=0.058 包装成完全强稳健。

已经完成、暂不再作为下一步重点：

```text
竞品自身同日重大公告清洗：已完成；
AI 词剔除版 ProductSimilarity：已完成；
公告清洗版 100 次随机同业 placebo：已完成；
外部 pre-event AIActivePeer 第一版：已完成；
外部 AIActivePeer × AI 词剔除版产品相似度：已完成；
abnormal trading value / shares：已完成，作为补充 Y；
同伴披露扩散：已降级为机制表。
```

如果外部口径精修后 `CAR[0,+1]` 的 Top5 结果仍能保留，这条主线可以进入正式论文框架。
