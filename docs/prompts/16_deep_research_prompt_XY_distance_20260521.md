# Deep Research Prompt: GenAI 披露研究中 X/Y 距离、测度锚点与选题价值审计

我正在设计一篇关于中国上市公司 GenAI/生成式人工智能/大模型披露的实证论文。现在已有两个重要判断：

1. 如果把 X 设为“公司发布 GenAI 披露/声明”，把 Y 设为“后续 AI hiring / AI capability building”，虽然 Y 可以锚定 Babina et al. (2024, JFE) 的 AI hiring 测度，但 X 和 Y 可能太接近，容易变成“公司说要做 AI，所以后来招 AI 人”，学术价值不足。
2. 我希望 X 和 Y 的测度尽量来自 AJG 4 / AJG 4* 期刊的原始测度或成熟做法，不能主要依赖我自己构造的 claim-matching 或 future public evidence。

请你做一项深度研究，核心目标不是帮我润色题目，而是回答：

> 在 GenAI 披露研究中，怎样选择 X 和 Y，才能同时满足“X/Y 不过度接近”“测度有 AJG 4/4* 文献锚点”“有会计/金融/管理学发表价值”？

## 一、我的数据环境

我可能拥有或可获取的数据包括：

- 中国 A 股上市公司年报文本，2023、2024、2025。
- 巨潮资讯所有公告文本。
- 投资者关系活动记录文本。
- 深交所互动易 / 上证 e 互动问答文本。
- CAC 生成式 AI 服务备案清单。
- 上市公司招聘大数据，2014-2026.3。
- 上市公司专利明细数据。
- AI 投资水平 / AI 词频等第三方数据。
- 常规公司财务、股价、分析师、问询函、股权质押、高管持股等数据，可能可获取。

## 二、请重点审计以下三个研究方向

### 方向 A：披露可信度 / 市场识别路线

候选研究问题：

> 上市公司发布 GenAI 披露时，市场是否会根据披露具体性和既有 AI 能力基础作出差异化反应？

候选变量：

- X: GenAI disclosure specificity / level of detail。
- Moderator: prior AI capability, 例如披露前 AI hiring、AI patents、CAC 备案、AI investment。
- Y: CAR、abnormal trading volume、bid-ask spread、analyst forecast dispersion、analyst forecast revision、后续回撤、问询函。

请重点判断：

1. 这个方向是否比“GenAI 披露 -> 后续 AI hiring”更有发表价值？
2. X 和 Y 是否足够远？
3. 哪些 Y 最适合做主 Y？
4. 哪些 AJG 4/4* 文献可以支撑：
   - disclosure specificity / level of detail；
   - event-study market reaction；
   - analyst information environment；
   - disclosure credibility；
   - speculative vs existing technology disclosure。

### 方向 B：外部 GenAI 冲击 / 真实能力建设路线

候选研究问题：

> 外部 GenAI 需求冲击或行业暴露是否推动企业真实 AI 能力建设？

候选变量：

- X: industry/customer/supply-chain GenAI exposure、同行 GenAI adoption、客户 GenAI adoption、政策/技术冲击暴露。
- Y: AI hiring share、AI patents、AI investment、GenAI-related job postings。
- Disclosure: 作为机制或信息渠道，不作为主 X。

请重点判断：

1. 如果主 Y 继续使用 Babina et al. (2024, JFE) 风格的 AI hiring，主 X 应该如何设计才能避免 X/Y 太近？
2. 是否有 AJG 4/4* 文献支持 industry exposure / customer exposure / peer exposure / technology diffusion 的 X 测度？
3. 这个方向是否会偏离“披露研究”，变成技术采用/组织调整研究？
4. 它适合会计金融期刊，还是更适合管理学/创新经济学期刊？

### 方向 C：AI washing / 披露-行动差距路线

候选研究问题：

> 当企业 GenAI 披露强度高于其可观察 AI 行动基础时，是否会受到市场、分析师或监管惩罚？

候选变量：

- X: disclosure-action gap，例如 GenAI disclosure percentile - AI action percentile。
- Y: 后续市场回撤、长期异常收益、问询函、分析师分歧上升、机构投资者撤出、声誉惩罚。
- Action benchmark: prior AI hiring、AI patents、CAC 备案、AI investment。

请重点判断：

1. Baker et al. (2024, JAR) diversity washing 的“disclosure-action gap”逻辑是否可以迁移到 GenAI？
2. 如果迁移，哪些部分是成熟测度，哪些部分仍然是我自己构造？
3. 这个方向是否比方向 A 更有创新性？
4. 它的数据构造风险是否过高？

## 三、必须评估的文献锚点

请至少核查并评价以下文献能否作为 X 或 Y 的测度锚点：

1. Babina, Fedyk, He, and Hodson (2024), *Journal of Financial Economics*, “Artificial Intelligence, Firm Growth, and Product Innovation.”
   - 用于 AI hiring / AI investment / AI capability building。

2. Hope, Hu, and Lu (2016), *Review of Accounting Studies*, “The Benefits of Specific Risk-Factor Disclosures.”
   - 用于 disclosure specificity / level of detail。

3. Cheng, De Franco, Jiang, and Lin (2019), *Management Science*, “Riding the Blockchain Mania: Public Firms' Speculative 8-K Disclosures.”
   - 用于 speculative vs existing technology disclosure。

4. Baker, Larcker, McClure, Saraph, and Watts (2024), *Journal of Accounting Research*, “Diversity Washing.”
   - 用于 disclosure-action gap / washing logic。

5. Kogan, Papanikolaou, Seru, and Stoffman (2017), *Quarterly Journal of Economics*, “Technological Innovation, Resource Allocation, and Growth.”
   - 用于 patent-based innovation。

6. Rogers and Stocken (2005), *The Accounting Review*, “Credibility of Management Forecasts.”
   - 用于 disclosure credibility 理论。

7. Hutton, Miller, and Skinner (2003), *Journal of Accounting Research*, “The Role of Supplementary Statements with Management Earnings Forecasts.”
   - 用于 verifiable supplementary disclosure / soft talk。

8. Allee, DeAngelis, and Moon (2018), *Journal of Accounting Research*, “Disclosure Scriptability.”
   - 用于 disclosure machine-readability / structured specificity robustness。

9. 任何已发表在 AJG 4/4* 的 AI disclosure、GenAI disclosure、AI adoption、technology disclosure、analyst reaction、market reaction 文献。

请明确区分：

- A 类：可以作为主 X 或主 Y 的原始测度锚点。
- B 类：只能作为理论、机制或稳健性支撑。
- C 类：工作论文、低级别期刊或测度不可迁移，不建议作为主锚。

## 四、请重点回答的判断问题

### 1. X/Y 距离审计

请对以下组合逐一判断“是否太近、是否有发表价值”：

| 组合 | X | Y |
|---|---|---|
| 组合 1 | GenAI disclosure event | future AI hiring |
| 组合 2 | GenAI disclosure specificity | market reaction |
| 组合 3 | GenAI disclosure specificity × prior AI capability | market reaction / analyst reaction |
| 组合 4 | GenAI disclosure-action gap | market penalty / regulator attention |
| 组合 5 | external GenAI exposure | AI hiring |
| 组合 6 | speculative GenAI disclosure | future market reversal / analyst disagreement |
| 组合 7 | existing GenAI disclosure | short-window positive CAR / lower uncertainty |

每个组合请给出：

- X/Y 距离是否足够；
- 主变量是否有 AJG 4/4* 测度锚；
- 最大内生性问题；
- 最大数据问题；
- 是否推荐做主线。

### 2. 最推荐主线

请最终给出一个明确主线，格式如下：

```text
Recommended main design:
X = ...
Y = ...
Moderator = ...
Measurement anchor for X = ...
Measurement anchor for Y = ...
Why X and Y are not too close = ...
Why this is not self-constructed = ...
Biggest threat = ...
Data requirement = ...
Target journal fit = ...
```

### 3. 不推荐主线

请明确指出哪些设计应该放弃或降级，尤其包括：

- GenAI disclosure event -> future AI hiring。
- unsupported specific GenAI claim -> claim-matched realization。
- FutureMatchedPublicEvidence as main Y。
- GenAI-only hiring as main Y。
- patent-based GenAI realization as main Y。

如果这些不能做主线，请说明它们可以放在哪个位置：机制、稳健性、validation、case evidence，或完全放弃。

## 五、输出格式

请按以下结构输出：

1. Executive conclusion
   - 最推荐哪条方向，为什么；
   - 明确说明“GenAI 披露 -> 后续 AI hiring”是否太近；
   - 明确说明最推荐的 X 和 Y。

2. Literature-anchored measurement table
   表格列包括：
   - Variable role；
   - Construct；
   - Original measurement；
   - Original paper；
   - Journal and AJG rating；
   - How to adapt to China A-share GenAI setting；
   - X/Y distance concern；
   - Recommendation: main / moderator / robustness / validation / avoid。

3. X/Y distance audit table
   对上面 7 个组合逐一评分。

4. Top 3 feasible designs
   每个设计必须包括：
   - X；
   - Y；
   - Moderator；
   - Measurement anchor；
   - Identification concern；
   - Data concern；
   - Publication value；
   - Whether it is better than disclosure -> hiring。

5. Final recommended design
   请给出一个保守、可执行、不神秘的版本。

6. Measurement risk audit
   请专门说明哪些变量是研究者自构造风险较高，不能作为主变量。

## 六、重要约束

- 不要只列文献，必须做判断。
- 不要把工作论文或低级别期刊包装成 AJG 4/4* 主锚。
- 不要把“GenAI disclosure event”说成顶刊已有成熟测度，除非确有已发表 AJG 4/4* 直接证据。
- 如果某个变量只是透明事件定义，而不是成熟测度，请明确说明。
- 如果 X/Y 太近，请直接说太近，不要为了保留原设计而迁就。
- 请优先推荐一个“X/Y 距离足够、测度锚点清楚、能写成正常论文”的设计。
