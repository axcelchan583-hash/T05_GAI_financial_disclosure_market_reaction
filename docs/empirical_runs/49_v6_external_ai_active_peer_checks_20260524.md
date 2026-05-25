# v6 外部 pre-event AIActivePeer 检验（2026-05-24）

## 这轮做了什么

本轮处理当前主设计最后一个核心短板：

```text
AIActivePeer 是否过度依赖历史 GenAI 披露文本？
能否用更外部、更事前、可观察的行动证据来定义竞品 AI-active 状态？
```

新增两步：

```text
1. 整理外部 AI 证据：
   CAC 生成式 AI 服务备案 / 登记；
   AI/GenAI 专利授权；
   上市公司本身及子公司的 AI 招聘；
   历史 GenAI 披露。

2. 把外部 AIActivePeer 接入 v6 公告清洗后的 peer CAR 面板，
   重跑 Top5 / Top10 / 低相似度同行 placebo。
```

脚本：

```text
scripts/build_v6_external_ai_evidence_dates_20260524.py
scripts/run_v6_external_ai_active_checks_20260524.py
```

结果目录：

```text
results/v6_external_ai_active_20260524
results/v6_external_ai_active_checks_20260524
```

## 外部证据数据规模

| 证据源 | 公司数 / 记录数 | 时间范围 | 说明 |
|---|---:|---|---|
| CAC A 股 lower-bound 匹配 | 106 家 | 2023-09-04 至 2026-04-30 | 来自既有 CAC 备案 / 登记匹配结果 |
| AI 专利标题匹配 | 101 家 | 授权日口径 | 专利名含 AI 相关关键词 |
| GenAI 专利标题匹配 | 28 家 | 授权日口径 | 专利名含大模型 / AIGC / 生成式等关键词 |
| broad AI 招聘 | 2,814 家 | 2016-04-03 至 2026-03-09 | 上市公司本身 + 子公司；按招聘发布日期 |
| GenAI 招聘 | 1,657 家 | 2016-04-03 至 2026-03-09 | 关键词更窄，但早年误报风险更高 |
| post-ChatGPT 历史 GenAI 披露 | 2,771 家 | 2022-11-30 后 | 来自完整 CSMAR GenAI 事件库 |

招聘流式扫描结果：

```text
招聘记录扫描：8,996,146
AI 候选招聘记录：98,445
AI 招聘 firm-day 行数：57,805
```

## AIActivePeer 口径

本轮跑了多个口径。最重要的是：

```text
current_text_history:
    旧口径，即 peer 在事件日前 5 天之前是否已有 GenAI 披露。

ext_any:
    prior CAC
 OR prior broad-AI patent grant
 OR >=1 broad-AI job posting in prior 365 days

ext_strict:
    prior CAC
 OR prior broad-AI patent grant
 OR >=3 broad-AI job postings in prior 365 days

ext_genai_strict:
    prior CAC
 OR prior GenAI patent grant
 OR >=1 GenAI job posting in prior 365 days

ext_plus_history:
    ext_strict
 OR post-ChatGPT prior GenAI disclosure
```

说明：

```text
ext_any 是当前最合理的“纯外部行为证据”主口径。
ext_plus_history 最稳，但它重新引入历史披露文本，因此只能算扩展口径。
ext_genai_strict 太窄，目前样本信号不足。
```

## 样本中 AIActivePeer 覆盖率

公告清洗后：

| peer group | N | events | current text history | prior AI patent | prior AI hiring365>=1 | ext_any | ext_strict | ext_plus_history |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| true Top5 | 8,683 | 2,416 | 0.256 | 0.018 | 0.197 | 0.208 | 0.105 | 0.324 |
| true Top10 | 17,285 | 2,432 | 0.259 | 0.017 | 0.199 | 0.209 | 0.106 | 0.327 |
| low-similarity | 14,753 | 2,382 | 0.251 | 0.011 | 0.169 | 0.175 | 0.086 | 0.306 |

## 主结果：CAR[0,+1]

公告清洗样本，`Y = market-model CAR[0,+1]`。

### 真实 Top5

| AIActivePeer 口径 | FE | coef | p |
|---|---|---:|---:|
| current_text_history | event FE | -0.002298 | 0.008 |
| current_text_history | event FE + peer industry-week FE | -0.002298 | 0.020 |
| ext_any | event FE | -0.001897 | 0.028 |
| ext_any | event FE + peer industry-week FE | -0.001800 | 0.058 |
| ext_plus_history | event FE | -0.002382 | 0.004 |
| ext_plus_history | event FE + peer industry-week FE | -0.002405 | 0.008 |

读法：

```text
纯外部 ext_any 方向和经济量级与旧口径一致；
Top5 在 event FE 下显著，在更强的 peer industry-week FE 下为边际显著。
加入历史披露后的 ext_plus_history 非常稳，但不应包装成纯外部证据。
```

### 真实 Top10

| AIActivePeer 口径 | FE | coef | p |
|---|---|---:|---:|
| current_text_history | event FE | -0.001190 | 0.056 |
| current_text_history | event FE + peer industry-week FE | -0.001408 | 0.034 |
| ext_any | event FE | -0.001654 | 0.004 |
| ext_any | event FE + peer industry-week FE | -0.001493 | 0.014 |
| ext_plus_history | event FE | -0.001420 | 0.013 |
| ext_plus_history | event FE + peer industry-week FE | -0.001548 | 0.011 |

Top10 下，纯外部 ext_any 比 Top5 更稳。

### 低相似度同行 placebo

| AIActivePeer 口径 | FE | coef | p |
|---|---|---:|---:|
| current_text_history | event FE | 0.000061 | 0.917 |
| ext_any | event FE | -0.000095 | 0.888 |
| ext_plus_history | event FE | 0.000114 | 0.830 |

低相似度同行没有复制主结果。

## 单项证据口径

单项证据的结论更复杂：

```text
prior AI patent grant:
    true Top5 / Top10 负向显著；
    但 low-similarity placebo 也有边际负向，不能单独当主口径。

prior broad-AI hiring in prior 365 days:
    true Top10 显著；
    true Top5 方向一致但强 FE 下不显著；
    low-similarity placebo 不显著。

prior CAC:
    样本覆盖太低，单独不显著。

ext_genai_strict:
    GenAI-only 外部证据太窄，当前不显著。
```

## 当前判断

这轮结果没有推翻主线，反而补强了一个重要点：

```text
主结果不是完全依赖历史 GenAI 披露文本定义 AIActivePeer；
用 CAC + AI 专利授权 + 过去 365 天 AI 招聘构造的外部 AIActivePeer，
仍然得到方向一致的竞品负向市场重估。
```

但要保守：

```text
纯外部 ext_any 在 Top5 + 强 FE 下是 p = 0.058，
不能说“完全强稳健”；
更准确的说法是“方向、经济量级和 placebo 均支持，统计强度略弱于历史披露口径”。
```

当前最适合写入论文的结构是：

```text
Main:
    current_text_history AIActivePeer，Top5，CAR[0,+1]。

External validation:
    ext_any = CAC + AI patent grant + AI hiring365>=1。
    Top5 方向一致、event FE 显著、强 FE 边际；
    Top10 更稳；
    low-similarity placebo 为零。

Expanded validation:
    ext_plus_history 很稳，但明确说明其包含历史披露文本。
```

下一步如果继续加强：

```text
1. 改进 CAC A 股匹配，不只用 lower-bound 的 106 家。
2. 改进 AI 专利分类，减少“低相似度同行也有边际负向”的问题。
3. 对 AI 招聘关键词做人工抽样复核，并尝试岗位标题-only / title+description 两种版本。
4. 将 ext_any 接到 AI-word-stripped peer network 上再跑一次。
```
