# T05 组会后版本：测度文献锚定与研究计划

## 一句话结论

这条线现在不能写成“我们自己构造了能力支撑和兑现变量”。更稳的写法是：

> 既有 AJG 3/4 文献已经分别提供了披露具体性、热点技术披露是否有实质基础、AI 人力资本投入、AI/技术专利产出、以及披露内容预测未来真实结果的成熟测度模板；本文的增量是把这些测度迁移到中国 A 股 GenAI 能力声明场景，并把分析单元从 firm-year 下沉到单条 claim。

因此，当前论文的核心不是发明两个全新变量，而是回答：

> 具体的 GenAI 能力声明，只有在声明前已有可公开核验证据时，才更可能被后续真实行动跟随吗？

## 当前研究问题

传统披露理论认为，越具体的披露越可信，因为具体内容更容易被市场、监管者或投资者事后核查。但在 GenAI 场景中，产品名、模型名、合作方、业务场景和时间表这些“看起来可验证”的细节也可能被低成本制造。本文检验的是具体性的可信度边界：当企业在声明前没有可公开核验的能力支撑时，具体性是否仍然预测后续 AI 人力资本投入、AI 创新产出和 claim-level 后续公开证据。

分析单元为：

```text
claim c x firm i x quarter t
```

核心解释变量为：

```text
HighSpecificity_cit x NoPriorPublicEvidence_cit
```

核心预期是交互项为负：如果一条 GenAI 声明非常具体，但声明前没有公开证据支撑，那么这类具体性对后续行动的预测价值更弱。

## 变量与 AJG 文献锚定

| 构件 | 本文变量 | 不能说成“自造”的文献锚 | 本文迁移方式 | 写作边界 |
|---|---|---|---|---|
| 披露具体性 | `HighSpecificity_cit` | Hope, Hu, and Lu (2016, RAS) 构造 risk-factor disclosure specificity；Rogers and Stocken (2005, TAR) 提供管理层披露可信度理论 | 把“具体性”从风险因素披露迁移到 GenAI capability claim，编码产品/模型/平台名、业务场景、时间表、合作方、业务线或子公司 | 可以说“借鉴披露具体性文献”；不要说具体性是 GenAI 文献已有标准变量 |
| 是否有前置支撑 | `NoPriorPublicEvidence_cit` | Cheng, De Franco, Jiang, and Lin (2019, Management Science) 将区块链 8-K 披露区分为 speculative 和 existing，依据是否已有产品、承诺或 track record | 把 speculative/existing 的思想迁移为 claim 发布前是否存在公开可核验证据 | 这是本文的 claim-level 改造；不要说已有文献有完全相同变量名 |
| 后续 AI 人力资本投入 | `AIHiringShare_{i,t:t+4Q}` | Babina, Fedyk, He, and Hodson (2024, JFE) 用 AI 人力资本/AI 投资度量企业 AI 采用；Kalyani et al. (2025, QJE) 用 job postings 识别新技术扩散 | 用上市公司招聘数据中的岗位标题和职位描述识别 GenAI/AI 相关岗位扩张 | 这是主 Y，文献锚最强，适合放第一张主表 |
| 后续 AI/GenAI 专利产出 | `AIPatentFiling_{i,t:t+8Q}` | Kogan et al. (2017, QJE) 用专利衡量创新经济价值；Babina et al. (2024, JFE) 与 Kalyani et al. (2025, QJE) 均把 AI/新技术专利作为技术采用或创新证据 | 用专利名称、摘要或分类识别 AI/GenAI 相关专利申请，并以申请日进入后续窗口 | 这是主 Y，文献锚强，适合放第二张主表 |
| 披露内容是否预测未来结果 | 结果解释框架 | Chu, He, Hui, and Lehavy (2025, RAS) 检验新产品公告中的 innovation disclosure 是否预测未来销售增长和市场反应 | 用同一逻辑检验 GenAI 能力声明内容是否预测未来 AI hiring / AI patent / public evidence | 支撑本文“披露内容 -> 未来真实结果”的会计论文模板 |
| claim-level 后续公开证据 | `FutureMatchedPublicEvidence_cit` | 近邻来自 Cheng et al. (2019) 的 existing/speculative 分类与 Chu et al. (2025) 的 disclosure-to-future-performance 逻辑 | 声明后是否出现命名匹配专利、算法备案、产品上线、合作生效等公开证据 | 这是本文自己的 claim-level 特色测度，应作为第三张主表或验证表，不宜单独扛全部主结论 |

## 主结果顺序

组会后的版本建议调整主表顺序。先让 AJG 文献中最成熟的 Y 扛住论文，再把 claim-level 匹配证据作为本文的特色贡献。

1. **主表一：后续 AI/GenAI 招聘**

   ```text
   AIHiringShare_{i,t:t+4Q}
   = beta1 HighSpecificity_cit
   + beta2 NoPriorPublicEvidence_cit
   + beta3 HighSpecificity_cit x NoPriorPublicEvidence_cit
   + controls + firm FE + claim-type x quarter FE + industry x quarter FE + eps
   ```

   解释：如果 `beta3 < 0`，说明“具体但无前置支撑”的 GenAI 声明较少伴随后续 AI 人力资本投入。这个 Y 的好处是文献成熟、数据可得、经济含义清楚。

2. **主表二：后续 AI/GenAI 专利申请**

   ```text
   AIPatentFiling_{i,t:t+8Q}
   = beta1 HighSpecificity_cit
   + beta2 NoPriorPublicEvidence_cit
   + beta3 HighSpecificity_cit x NoPriorPublicEvidence_cit
   + controls + firm FE + claim-type x quarter FE + industry x quarter FE + eps
   ```

   解释：如果 `beta3 < 0`，说明“具体但无前置支撑”的声明较少转化为后续 AI 创新产出。专利窗口可以用 8Q 作为主设定，4Q 和 12Q 作为稳健性。

3. **主表三或验证表：claim-level 后续公开证据**

   ```text
   FutureMatchedPublicEvidence_cit
   = 1[声明后窗口内出现与该 claim 命名或类型匹配的公开证据]
   ```

   解释：这是本文最有特色的 claim-level 变量，但也是最容易被质疑“自己构造”的变量。它应该承担两个角色：第一，证明主结果不是只停留在 firm-level AI hiring / patent；第二，显示本文确实能在单条声明层面追踪“说了什么”和“后来有没有对应公开行动”。在样本量和编码一致性过关之前，不建议让它成为唯一主 Y。

## 为什么这不是“自己造测度”

可以在组会或论文里这样解释：

> 本文的每个关键构件都不是凭空定义。披露具体性来自 Hope, Hu, and Lu (2016) 的 specificity measurement tradition；“是否已有实质基础”的分类来自 Cheng et al. (2019) 对 blockchain speculative/existing disclosures 的划分；后续行动结果中的 AI hiring 与 AI patents 分别对应 Babina et al. (2024)、Kalyani et al. (2025) 和 Kogan et al. (2017) 等文献中成熟的 AI/技术采用和创新产出测度；披露内容预测未来真实结果的整体框架则与 Chu et al. (2025) 的 new product announcement 研究一致。本文的创新在于把这些成熟测度迁移到中国 GenAI 能力声明，并在 claim-level 构造可复核的 prior public evidence 和 future matched public evidence。

这段话的关键是承认：

- `HighSpecificity` 有成熟披露文献支撑；
- `AIHiringShare` 和 `AIPatentFiling` 是成熟 Y；
- `NoPriorPublicEvidence` 和 `FutureMatchedPublicEvidence` 是本文的 claim-level 改造，不是已有文献的现成变量名；
- 但这种改造有 Cheng et al. (2019) 的 speculative/existing 分类和 Chu et al. (2025) 的 disclosure-to-future-outcome 模板支撑。

## 建议写进引言的标准段落

近期关于企业 AI 披露的研究已经不再仅仅关注企业是否提及 AI，而是进一步追问这些 AI 叙事是否对应真实行动。既有研究通常将企业披露中的 AI 表述视为 “talk”，并以 AI 人力资本投入、AI 专利和后续经营结果等外部证据作为 “walk” 的验证。这一路径为识别 AI washing 提供了重要基础，但现有研究多停留在企业-年或企业-季层面，难以回答一个更细的问题：同一家企业在不同时间、不同渠道发布的多条 GenAI 能力声明，哪些更可能被后续行动跟随？本文由此将 AI talk-walk gap 从企业层面下沉到单条声明层面。具体而言，本文借鉴披露具体性文献、热点技术 speculative disclosure 文献以及 AI 采用和创新产出文献，构造声明前公开证据与声明后行动结果的匹配框架。本文检验：具体 GenAI 能力声明的预测价值是否条件于声明前已有可公开核验的能力支撑。

## 第一阶段可执行计划

第一阶段不先扩全渠道数据，而是先做小样本测度验证。

| 步骤 | 内容 | 通过标准 |
|---|---|---|
| 1 | 从 2024 年报 PDF 和 2025 年报 txt 中抽取 GenAI forward-looking claims | 得到 200-300 条可人工复核 claim |
| 2 | 编码 `HighSpecificity` | 人工/LLM 双编码 kappa 不低于 0.70 |
| 3 | 编码 `NoPriorPublicEvidence` | 至少形成有效 2x2 分布，尤其 `HighSpecificity=1 & NoPriorPublicEvidence=1` 不少于 30 条 |
| 4 | 匹配后续招聘 | 声明后 4Q 内能按上市公司代码和日期匹配招聘记录 |
| 5 | 匹配后续专利 | 声明后 8Q 内能按证券代码、申请日期、专利名识别 AI/GenAI 专利 |
| 6 | 构造 `FutureMatchedPublicEvidence` | 后续匹配证据发生率不能接近 0 |

如果这些门槛通过，就继续 claim-level 可信度主线。如果 `FutureMatchedPublicEvidence` 太稀疏，则不强行把它当主 Y，而是降级为测量验证表，主结论由 AI hiring 和 AI patents 承担。

## 当前数据口径

基于本地数据审计，当前最合适的第一版样本是：

```text
年报 GenAI forward-looking claim
+ 后续 AI/GenAI 招聘
+ 后续 AI/GenAI 专利
+ 算法备案/产品名/同名专利作为前置或后续公开证据补充
+ 股权质押、所有制、管理层持股薪酬作为机制或异质性
```

暂时不要在第一版里承诺已经覆盖互动易、上证 e 互动、投资者关系活动、临时公告、软著和 CAC 生成式 AI 服务备案。这些可以作为第二阶段扩展数据。

## 写作禁区

1. 不要说“本文构造真实能力变量”。应改成“声明前可公开核验的能力支撑证据”。
2. 不要说“兑现变量已经由文献成熟定义”。应区分 AI hiring / AI patent 是成熟 Y，`FutureMatchedPublicEvidence` 是本文的 claim-level 改造。
3. 不要把 `FutureMatchedPublicEvidence` 放成唯一主 Y。它有特色，但最容易被质疑测度主观。
4. 不要把 Barrios / Li / Song 这类 AI washing 工作论文当成唯一测度锚。它们可以放在前沿动机里，真正支撑测度的核心应是 Hope et al. (2016)、Cheng et al. (2019)、Babina et al. (2024)、Kalyani et al. (2025)、Kogan et al. (2017)、Chu et al. (2025)。

## 参考文献锚点

- Rogers, J. L., and Stocken, P. C. (2005). Credibility of Management Forecasts. *The Accounting Review*, 80(4), 1233-1260. https://doi.org/10.2308/accr.2005.80.4.1233
- Hope, O.-K., Hu, D., and Lu, H. (2016). The Benefits of Specific Risk-Factor Disclosures. *Review of Accounting Studies*, 21(4), 1005-1045. https://doi.org/10.1007/s11142-016-9371-1
- Cheng, S. F., De Franco, G., Jiang, H., and Lin, P. (2019). Riding the Blockchain Mania: Public Firms' Speculative 8-K Disclosures. *Management Science*, 65(12), 5901-5913. https://doi.org/10.1287/mnsc.2019.3357
- Babina, T., Fedyk, A., He, A., and Hodson, J. (2024). Artificial Intelligence, Firm Growth, and Product Innovation. *Journal of Financial Economics*, 151, 103745. https://doi.org/10.1016/j.jfineco.2023.103745
- Kalyani, A., Bloom, N., Carvalho, V. M., Hassan, T., Lerner, J., and Tahoun, A. (2025). The Diffusion of New Technologies. *Quarterly Journal of Economics*, 140(2), 1299-1365. https://doi.org/10.1093/qje/qjaf002
- Kogan, L., Papanikolaou, D., Seru, A., and Stoffman, N. (2017). Technological Innovation, Resource Allocation, and Growth. *Quarterly Journal of Economics*, 132(2), 665-712. https://doi.org/10.1093/qje/qjw040
- Chu, J., He, Y., Hui, K. W., and Lehavy, R. (2025). New Product Announcements, Innovation Disclosure, and Future Firm Performance. *Review of Accounting Studies*, 30(1), 352-383. https://link.springer.com/article/10.1007/s11142-024-09820-0
