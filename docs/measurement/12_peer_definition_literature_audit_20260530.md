# Product-Market Peer Definition Literature Audit

日期：2026-05-30

## 结论先行

当前项目不能再把 peer 口径写成“我们基于文本相似度自构造竞品”。更安全的写法是：

```text
We follow established peer-identification systems in the finance/accounting literature.
```

可选 peer 系统分为四类：

1. **传统行业同业**：SIC / NAICS / CSRC 行业。
2. **文本产品市场同业**：Hoberg-Phillips TNIC / annual-report business-description similarity。
3. **投资者或中介识别的同业**：EDGAR co-search peers、common analyst peers、compensation peers。
4. **技术相似同业**：patent/R&D/technological peer pressure。

对本项目最可用的是第 1 和第 2 类；第 3、4 类更适合外部验证或机制，不适合当前主口径。

## 1. 行业同业

### 文献逻辑

最传统 peer 定义是同一行业分类下的 firms，例如 SIC、NAICS、Fama-French industry 或中国 CSRC 行业。
它的优势是可复现、低争议；劣势是太粗，不能刻画 firm-specific competitors。

### 在本项目中的角色

```text
Use as baseline / placebo:
    same CSRC IndustryNameD peers
    random same-industry peers
```

它不能单独支撑“产品市场近邻竞争威胁”，但可以作为最朴素的对照组。

## 2. Hoberg-Phillips / TNIC-style 文本产品市场同业

### 核心文献

Hoberg and Phillips (2016, Journal of Political Economy), "Text-Based Network Industries and Endogenous Product Differentiation."

核心做法：

```text
10-K business description
-> product-word vector
-> firm-pair textual similarity
-> each firm has its own firm-centric competitor set
```

Hoberg-Phillips Data Library 对 TNIC 的描述是：竞争者是在 product space 中距离 focal firm 较近的 firms，
每个 firm 有自己的 distinct set of competitors，并且 annually updated。

### 可迁移到中国 A 股的版本

中国没有现成 TNIC。最接近的可迁移版本是：

```text
A-share annual report business / MD&A / main business text
-> Chinese text vector
-> firm-pair cosine similarity
-> TopK product-market peers
```

本项目 v12 已实现：

```text
scripts/build_v12_annual_report_product_peers_20260530.py
```

但主回归替换检验失败：

```text
annual same IndustryNameD Top5:
    ext_any              coef =  0.001020, p = 0.144
    current_text_history coef =  0.000392, p = 0.570

annual global AI-word-stripped Top5:
    ext_any              coef = -0.000490, p = 0.551
    current_text_history coef = -0.001366, p = 0.124
```

因此，年报文本 peer 网络可以作为文献锚定的替换检验，但目前不能支撑主结果。

## 3. Annual-report business-description similarity and LLM peers

### 核心文献

Cao, Chen, Tucker, and Wan (2025, Review of Accounting Studies), "Can generative AI help identify peer firms?"

该文比较了：

- LLM-generated peers；
- TNIC peers；
- analyst-mentioning peers；
- compensation-benchmarking peers；
- annual-report business-description similarity；
- SIC industry members。

该文结论之一是：LLM peers 与专家识别、既有 peer systems 有较高 overlap，并在后续 stock returns、sales growth、gross margin 等维度有更强相关性。

### 在本项目中的角色

这篇不能直接让我们用“自己算的旧 CSMAR scope similarity”当主口径，但它给了一个清楚方向：

```text
If product-market peer validity is attacked,
add LLM-peer validation / annual-report similarity / SIC industry as benchmarking systems.
```

可执行方案：

1. 抽取 focal firm 的 Top5 old-CSMAR peers；
2. 抽取 annual-report peers；
3. 让 LLM 在指定年份、指定 A 股公司池中列出 Top5 product-market competitors；
4. 比较 overlap；
5. 用 return comovement / sales growth comovement 验证哪套 peer 更像真实同业。

这一步是 peer measurement validation，不是新的主效应。

## 4. Search-based peers

### 核心文献

Lee, Ma, and Wang (2015, Journal of Financial Economics), "Search-Based Peer Firms: Aggregating Investor Perceptions Through Internet Co-Searches."

核心做法：

```text
EDGAR user search logs
-> firms searched close together by same user
-> search-based peer firms
```

它捕捉的是投资者 revealed perception of related firms，而不是纯产品文本。

### 在本项目中的角色

中国 A 股没有直接可用的 EDGAR search log 对应物。互动平台同日/同问题共同出现不能等同于 search-based peers。

可作为讨论，不建议当前实现为主 peer 口径。

## 5. Common analyst peers

### 核心文献

Kaustia and Rantala (2021, Journal of Financial and Quantitative Analysis), "Common Analysts: Method for Defining Peer Firms."

核心做法：

```text
joint analyst coverage
-> common analyst peer groups
```

逻辑是分析师覆盖选择不仅反映行业，还反映 business model 和可比性。

### 在本项目中的角色

如果能拿到分析师覆盖公司-年份数据，可以做 robustness：

```text
peer is covered by at least one same analyst / same brokerage team as focal firm
```

但这测的是 equity-market comparability，不是纯产品市场竞争。适合作为外部 peer-validity 检验，不适合作为主 competitor 口径。

## 6. Technological peers

### 核心文献

Cao, Ma, Tucker, and Wan (2018, The Accounting Review), "Technological Peer Pressure and Product Disclosure."

核心做法是构造 firm-specific technological peer pressure，用技术接近度加权 peers 的 R&D stock，
解释产品开发相关披露。

### 在本项目中的角色

这类 peer 更适合回答：

```text
GenAI 披露是否影响技术相近企业？
```

而不是：

```text
产品市场竞品是否被资本市场重估？
```

可以作为 heterogeneity：

```text
product-market close peers × technological close peers
```

但不宜直接替代 product-market peers。

## 7. Compensation peers and valuation peers

### 文献逻辑

补偿 peer、估值可比公司 peer 都是成熟 peer systems：

- compensation benchmarking peers：公司自己在 proxy 中披露；
- valuation peers：根据估值理论或可比倍数选择 comparable firms。

### 在本项目中的角色

这些 peer 的经济含义不是产品市场竞争，而是高管劳动力市场或估值可比性。当前项目不建议使用。

## 推荐的当前处理

### 不建议继续的写法

```text
我们用 CSMAR MAINBUSSINESS + BusinessScope 自己构造 Top5 竞品，
发现 Specificity_z × AIActivePeer 显著。
```

这个写法太像 data mining。

### 更安全的写法

```text
We use a text-based product-market peer approach inspired by Hoberg and Phillips (2016).
Because China does not have off-the-shelf TNIC data, we construct Chinese A-share
peer networks from two observable business-description sources:

(1) CSMAR business-scope / main-business text;
(2) annual-report business-section text.

The headline pattern is concentrated in the CSMAR business-scope network and does
not reproduce in the broader annual-report network. Therefore, peer definition is a
central limitation and must be treated transparently.
```

### 论文层面的选择

如果坚持当前 peer-CAR 主线，主表可以继续用旧 CSMAR scope Top5，但必须新增一个
peer-validity section：

1. CSMAR scope Top5 vs annual-report Top5 overlap；
2. CSMAR scope Top5 vs same CSRC industry random peers；
3. CSMAR scope Top5 vs LLM-generated peers for a manually checked subsample；
4. return comovement validation；
5. revenue / gross margin comovement validation if data are available。

如果这些 peer-validity 检验不过，当前主线应降级或换 Y。

## References

- Hoberg, G., and Phillips, G. (2016). "Text-Based Network Industries and Endogenous Product Differentiation." *Journal of Political Economy*, 124(5), 1423-1465.
- Hoberg, G., Phillips, G., and Prabhala, N. (2014). "Product Market Threats, Payouts, and Financial Flexibility." *Journal of Finance*, 69(1), 293-324.
- Lee, C. M. C., Ma, P., and Wang, C. C. Y. (2015). "Search-Based Peer Firms: Aggregating Investor Perceptions Through Internet Co-Searches." *Journal of Financial Economics*, 116(2), 410-431.
- Kaustia, M., and Rantala, V. (2021). "Common Analysts: Method for Defining Peer Firms." *Journal of Financial and Quantitative Analysis*, 56(5), 1505-1536.
- Cao, S. S., Ma, G., Tucker, J. W., and Wan, C. (2018). "Technological Peer Pressure and Product Disclosure." *The Accounting Review*, 93(6), 95-126.
- Cao, Y., Chen, L., Tucker, J. W., and Wan, C. (2025). "Can Generative AI Help Identify Peer Firms?" *Review of Accounting Studies*, 30, 3344-3386.
