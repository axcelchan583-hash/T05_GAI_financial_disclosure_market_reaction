# Deep Research Prompt: 强制确定一个主 X 和一个主 Y

我正在设计一篇关于中国上市公司 GenAI/生成式人工智能/大模型披露的实证论文。前期讨论已经变得过于发散，现在需要强制收口。

请你不要再给我并列列出很多可能方向。你的任务是：

> 在所有可行方案中，最终必须确定一个唯一的主 X 和一个唯一的主 Y，并说明为什么其他方案应该降级或放弃。

## 一、背景

我原来考虑过很多变量：

- GenAI disclosure event；
- GenAI disclosure specificity；
- speculative vs existing GenAI disclosure；
- unsupported specific GenAI claim；
- future AI hiring；
- AI patents；
- CAC GenAI filing；
- claim-matched realization；
- FutureMatchedPublicEvidence；
- CAR / abnormal volume；
- analyst forecast dispersion / forecast revision；
- regulatory inquiry letters。

现在最大问题是：

1. 如果 X = GenAI disclosure event，Y = future AI hiring，那么 X 和 Y 太接近，像“公司说要做 AI，所以后来招 AI 人”，学术价值可能不足。
2. 如果 Y = claim-matched realization / FutureMatchedPublicEvidence，又太像研究者自己构造的文本匹配变量。
3. 如果同时保留 CAR、分析师、问询函、招聘、专利、CAC，又会变成三篇论文混在一起。

所以请你强制帮我做一个清晰选择。

## 二、我的硬性要求

最终输出必须满足：

1. **只能推荐一个主 X。**
2. **只能推荐一个主 Y。**
3. 主 X 和主 Y 不能太近，必须能解释为什么不是同一件事。
4. 主 X 或主 Y 至少有一个必须能直接锚定 AJG 4 / AJG 4* 文献中的原始测度。
5. 如果另一个变量不是成熟测度，也必须是透明、可复核、非任意的定义。
6. 必须明确说明哪些变量只能做 moderator、mechanism、robustness、validation，不能做主变量。

## 三、候选方案

请在以下候选方案中强制选择一个最优主线，也可以提出一个更优但必须仍然只有一个主 X 和一个主 Y。

### 方案 A：披露具体性 -> 短窗市场反应

```text
Main X = GenAI disclosure specificity / Level of Detail
Main Y = short-window market reaction, e.g. |CAR[-1,+1]| or ABVOL[-1,+1]
Moderator = prior AI capability
```

直觉：

> 市场是否认为更具体的 GenAI 披露更有信息含量？这种信息含量是否取决于企业披露前是否已有真实 AI 能力基础？

潜在锚点：

- X: Hope, Hu, and Lu (2016, Review of Accounting Studies), disclosure specificity / level of detail。
- Y: classic event study / market reaction literature, e.g. Beaver (1968), Hope et al. (2016) 的 |CAR| / abnormal volume。
- Theory: Rogers and Stocken (2005, TAR), disclosure credibility。

### 方案 B：speculative GenAI disclosure -> 后续市场回撤或分析师分歧

```text
Main X = speculative GenAI disclosure
Main Y = future return reversal / analyst forecast dispersion
Moderator = prior AI capability
```

直觉：

> 投机性 GenAI 披露是否会在后续被市场或分析师重新定价？

潜在锚点：

- X: Cheng, De Franco, Jiang, and Lin (2019, Management Science), speculative vs existing blockchain 8-K disclosures。
- Y: analyst forecast dispersion / market reversal literature。

### 方案 C：GenAI disclosure-action gap -> 监管或市场惩罚

```text
Main X = GenAI disclosure-action gap
Main Y = regulatory inquiry / market penalty
Moderator = governance or incentive pressure
```

直觉：

> 说得多但做得少的 GenAI 披露是否会受到惩罚？

潜在锚点：

- X: Baker et al. (2024, Journal of Accounting Research), diversity washing / disclosure-action gap。
- Y: inquiry letters / market penalty / analyst skepticism。

### 方案 D：外部 GenAI 暴露 -> AI hiring

```text
Main X = external GenAI exposure
Main Y = future AI hiring share
Moderator = prior digital capability
```

直觉：

> 外部 GenAI 冲击是否推动企业真实 AI 能力建设？

潜在锚点：

- Y: Babina et al. (2024, Journal of Financial Economics), AI hiring / AI investment。
- X: technology exposure / industry exposure / customer exposure literature。

问题：

> 这可能偏离披露研究。

### 方案 E：GenAI disclosure event -> future AI hiring

```text
Main X = GenAI disclosure event
Main Y = future AI hiring share
```

直觉：

> 公司披露 GenAI 后是否真的建设 AI 能力？

问题：

> X/Y 可能太近，像项目进度条。

## 四、必须评估的文献

请至少核查并使用以下文献作为判断基础：

1. Hope, Hu, and Lu (2016), Review of Accounting Studies, “The Benefits of Specific Risk-Factor Disclosures.”
2. Cheng, De Franco, Jiang, and Lin (2019), Management Science, “Riding the Blockchain Mania: Public Firms' Speculative 8-K Disclosures.”
3. Baker, Larcker, McClure, Saraph, and Watts (2024), Journal of Accounting Research, “Diversity Washing.”
4. Babina, Fedyk, He, and Hodson (2024), Journal of Financial Economics, “Artificial Intelligence, Firm Growth, and Product Innovation.”
5. Rogers and Stocken (2005), The Accounting Review, “Credibility of Management Forecasts.”
6. Hutton, Miller, and Skinner (2003), Journal of Accounting Research, “The Role of Supplementary Statements with Management Earnings Forecasts.”
7. Beaver (1968), Journal of Accounting Research, “The Information Content of Annual Earnings Announcements.”
8. Analyst information environment / forecast dispersion literature in AJG 4 / 4* accounting and finance journals, if relevant.
9. Regulatory inquiry letter literature in China or international accounting journals, if relevant.

## 五、请你必须回答的问题

### 1. 唯一主线选择

请直接回答：

```text
I recommend:
Main X = ...
Main Y = ...
Moderator = ...
Main sample = ...
Main empirical design = ...
```

不允许回答“取决于研究目标”。你必须替我选。

### 2. 为什么 X 和 Y 不太近

请专门说明：

- X 衡量的是什么；
- Y 衡量的是什么；
- 为什么它们不是同一件事；
- 为什么这个关系有理论价值。

### 3. 测度锚点

请说明：

- 主 X 的 AJG 4 / 4* 测度锚点是什么；
- 主 Y 的 AJG 4 / 4* 测度锚点是什么；
- 如果某个变量只是透明事件定义而不是成熟测度，请直接说明。

### 4. 放弃或降级项

请明确说明以下变量应该放在什么位置：

| 变量 | main / moderator / mechanism / robustness / validation / avoid |
|---|---|
| future AI hiring |
| AI patents |
| CAC GenAI filing |
| prior AI capability |
| GenAI disclosure event |
| GenAI disclosure specificity |
| speculative vs existing |
| unsupported specific GenAI claim |
| claim-matched realization |
| FutureMatchedPublicEvidence |
| CAR / ABVOL |
| analyst forecast dispersion |
| inquiry letters |

### 5. 最小可执行版本

请给出一个最小可执行版本：

```text
Data required:
Step 1:
Step 2:
Step 3:
Baseline regression:
Key table 1:
Key table 2:
```

要求这个版本能在现有数据条件下尽快试跑，不要依赖太多未来才能拿到的数据。

### 6. 最强反对意见

请从审稿人角度提出最强三条反对意见，并说明怎么防御。

## 六、输出格式

请按以下结构输出：

1. Final choice in one paragraph。
2. Main X and main Y table。
3. Why rejected alternatives are worse。
4. Measurement anchor table。
5. Minimal empirical design。
6. Reviewer objections and defenses。
7. Final one-sentence paper idea。

## 七、重要约束

- 不要再生成多个并列主线。
- 不要说“都可以”。
- 不要把 future AI hiring 同时当主 Y，又说它只是能力基础。
- 不要把 claim-matched realization 包装成成熟测度。
- 不要把 GenAI disclosure event 包装成 AJG 4/4* 现成测度，除非找到直接已发表证据。
- 最后必须只留下一个主 X 和一个主 Y。
