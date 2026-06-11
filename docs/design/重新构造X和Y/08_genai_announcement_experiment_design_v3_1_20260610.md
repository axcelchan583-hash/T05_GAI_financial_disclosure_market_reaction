# T05 GenAI 公告样本重构与实验设计 v3.1（20260610）

## 1. 当前定位

本项目不再把公告 taxonomy 当成主贡献。当前设计的核心是先重构干净的 X：

> 中国 A 股上市公司首次披露可信、可定位事件日的 GenAI initiative。

主研究问题仍然是：

> 资本市场是否把可信 GenAI disclosure 定价为对 product-market competitors 的横向竞争威胁？

与 POM/Qian 的关系：

- POM/Qian 看的是 GenAI announcements 对 suppliers 的正向纵向溢出；
- 本项目看的是 GenAI disclosure 对 product-market competitors 的负向横向重估；
- POM 的 product/process 二分不作为本项目主 X，只作为后续可比对照或附录。

当前 v3.1 的新增点是把“真实承诺”和“概念性框架/cheap talk”分开。`D-fw` 样本保留公告日，可作为 placebo / cheap-talk event pool，用来检验市场是否区分 credible claim 与 non-committal GenAI talk。

## 2. 当前人工编码入口

Obsidian 最新工作台：

`/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告PDF人工审核_v3_1_20260610.md`

配套输出：

```text
/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_machine.csv
/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_coding.csv
```

生成脚本：

`/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/scripts/build_v3_obsidian_coding_workbench_20260610.py`

当前候选池：

```text
三类宽口径公告：1,601 条
机器预判：A=202, B=29, D-fw=52, D=1318
```

这些机器预判只是分流，不是最终人工码。

## 3. v3.1 判定码

人工只填写一行 `人工码:`。

```text
A     主样本：首次、可信、公告日可用的 GenAI initiative
B     真 GenAI，但当前公告日不能用，需要回填更早首次日期
C     真 GenAI 相关，但非首次，或重复/进展披露
D-fw  GenAI 话题/框架协议/无实质承诺；保留公告日作 placebo，不进主样本
D     剔除：非有效 GenAI 行动、泛AI、否认、估值模型、非公司行动等
U     待定，需要二次核验
```

主样本只使用：

```text
verdict = A
genai_validity = yes
source_event_type = direct_event
event_date_usable = yes
first_event = yes
```

`B` 样本不直接进入事件研究，先用于寻找更早首次事件日。`D-fw` 样本不进入主 treatment，但保留公告日进入 cheap-talk placebo 检验。

## 4. A 类附加字段

仅 `A` 类需要继续填写：

```text
OUT=1/0
M=own/ext
证=一句原文
R=+/-   可选
```

解释：

- `OUT=1`：GenAI 相关产出面向外部客户收费、销售或提供服务；
- `OUT=0`：纯内部提效、自用算力储备、生态接入、能力储备等，不直接面对外部客户；
- `CT=1/0` 可写，但解析时统一并入 `OUT`；
- `M=own`：自己发布、上线、备案、部署；
- `M=ext`：合作、投资、收购、算力承诺等借外力；
- `R=+`：已经发布、上线、交付或商业化；
- `R=-`：计划、意向、框架或尚未落地。

示例：

```text
人工码: A | OUT=1 | M=own | 证=公司发布讯飞星火认知大模型并同步发布商业应用成果 | R=+
人工码: A | OUT=1 | M=ext | 证=鑫煜科技3亿元增资星临科技获10%股权，标的为国产大模型研发训练提供算力服务 | R=-
人工码: D-fw
人工码: B | 线索=年报追溯，查2023年3月新闻
```

## 5. 合作/框架协议规则

合作类公告的判定视角永远站在公告方，也就是 focal listed firm。

关键问题：

> 协议里有没有 focal firm 可指认的 GenAI 动作或交付物？

判定：

```text
有，且为该公司首次             -> A，M=ext
有，但该公司此前已有首次有效事件 -> C
没有，只写战略合作/生态/探索AI   -> D 或 D-fw
写了方向但模糊                 -> U
```

三条原则：

1. 合作方有没有技术不影响判定，判的是焦点公司自己的承诺；
2. `C` 只看焦点公司自己的时间线，与合作方无关；
3. 不为合作类新开主样本类别，能力来自外部由 `M=ext` 承载。

### 5.1 框架协议亮线

公告特别提示或正文中出现以下三类标志中两类及以上，通常判 `D-fw`：

1. 自称框架性协议、框架协议或意向性文件；
2. 不涉及具体金额、无需董事会或股东大会审议；
3. 具体合作、费用、知识产权等另行签约、另行协商或另行确定。

逻辑：

> 公司用法律语言自我声明承诺水平很低，当前公告日更接近 GenAI cheap talk，而不是可信 initiative。

例外：

若同一公告同时披露已经上线、交付、签署具体合同、明确金额订单或商业化收入，可以 override 为 `A`。

`D-fw` 与普通 `D` 不同：

- `D-fw`：有 GenAI 话题但无实质承诺，保留公告日；
- `D`：不是有效 GenAI 事件，不保留事件日。

## 6. 投资/增资/收购规则

投资类只问两个 gate：

1. 承诺是否真实：正式协议、真金白银、支付安排；业绩对赌/补偿条款是强信号；
2. 标的是否明确 GenAI 相关：大模型训练/推理、AIGC 服务、或服务具体大模型公司。

两者都成立且为首次：

```text
verdict = A
M = ext
OUT = 按标的产出归宿判断
```

不构成否决的因素：

- 参股比例低或不并表；
- 焦点公司主业与 AI 不同；
- 协议签署日早于公告日。

信息事件日一律先取公告日。威胁大小由后续 `Specificity`、`OUT`、`M`、`AIActivePeer` 和稳健性检验处理。

## 7. DeepSeek / LLM 预编码方案

可以把约 1,000 条未编码公告交给 DeepSeek 做第一轮预编码，但只能作为分流，不作为最终人工码。

DeepSeek 输入不建议直接整份 PDF。推荐给它：

```text
公司、代码、日期
标题
公告类别
命中词
机器证据提示
特别提示/风险提示/协议主要内容/投资协议/合同条款附近文本
v3.1 判定规则
```

DeepSeek 输出 JSON：

```json
{
  "id": "POM3_00079",
  "verdict": "D-fw",
  "out": "",
  "mode": "",
  "realized": "",
  "event_date": "2023-03-28",
  "evidence": "一句原文",
  "reason": "命中框架协议三标志中的两项",
  "uncertainty": "low"
}
```

人工复核优先级：

1. 所有 `A`；
2. 所有 `B`；
3. 所有 `D-fw`；
4. 所有 `U`；
5. `D` 中抽样 5%-10% 做漏保审计。

因此 LLM 的作用是把人工工作从 1,601 条逐条精填降为“高风险类别复核 + D 类抽样审计”。

## 8. 实证设计

### 8.1 主样本

```text
ValidAEvents = verdict=A
             & event_date_usable=yes
             & first_event=yes
```

用 `event_date` 作为事件日；若人工码内写 `日=YYYY-MM-DD`，则覆盖公告日。

### 8.2 主结果：competitor CAR

主表仍然报告 product-market competitors 的短窗反应：

```text
CompetitorCAR_{e,p,[0,+1]} = α + β ValidAEvent_e + controls + ε
```

当前旧的 competitor-negative 结果来自未完成 v3.1 清洗前的事件口径，只能作为 provisional。v3.1 清洗完成后必须重跑。

### 8.3 机制：Specificity × AIActivePeer

```text
PeerCAR_{e,p,[0,+1]} = α_e
                      + β1 Specificity_e × AIActivePeer_p
                      + β2 AIActivePeer_p
                      + PeerControls_p
                      + ε_{e,p}
```

解释边界：

- `Specificity` 仍是主机制变量；
- `OUT/M/R` 不替代 `Specificity`，只做辅助异质性或稳健性；
- event FE 识别来自同一公告内 AI-active 与 non-AI-active peers 的相对反应；
- peer FE 下会弱化或消失，必须披露识别边界。

### 8.4 Cheap-talk placebo：D-fw

`D-fw` 是新增 placebo / contrast group：

```text
CAR around D-fw announcement date
```

预期不是主方向假设，而是检验市场是否区分：

```text
credible GenAI claim (A)
vs
non-committal GenAI framework / cheap talk (D-fw)
```

推荐报告：

1. A 事件 competitor CAR；
2. D-fw 事件 competitor CAR；
3. A - D-fw stacked contrast；
4. 对后续 A 事件加入 `pre_fw`，检查同公司此前 D-fw 是否预释放信息。

### 8.5 A 类内部异质性

仅在样本量允许时做：

```text
OUT=1 vs OUT=0
M=own vs M=ext
R=+ vs R=-
```

这些不作为主贡献。尤其 `OUT` 不是“是否有竞争威胁”，只是是否直接面向外部客户或服务。

必要稳健性：

- 只保留 `M=own` 的发布/上线/备案/部署类事件；
- 剔除投资/算力类 `M=ext` 事件；
- 分别报告 `OUT=1` 与 `OUT=0`；
- 检查 `OUT` 与 `Specificity` 的相关性，避免把 `OUT` 误写成独立机制。

## 9. 清洗后必须重跑

v3.1 清洗会改变：

1. 事件是否进入主样本；
2. 每家公司首次事件日；
3. 回填事件日；
4. cheap-talk placebo 池；
5. A 类内部 `OUT/M/R` 分布。

清洗完成后必须重跑：

- competitor CAR `[0,+1]`；
- `Spec × AIActivePeer`；
- peer-characteristic guard；
- `A` vs `D-fw` cheap-talk contrast；
- `OUT/M/R` 辅助异质性；
- investment-linked partner 探索性结果。

论文中不能把旧事件口径的 v44/v45/v46 结果写成最终估计。

## 10. 当前执行优先级

1. 用 v3.1 工作台继续人工编码；
2. 若调用 DeepSeek，先作为预编码分流，不直接定稿；
3. 优先复核 `A/B/D-fw/U`；
4. 每完成约 100 条，更新 `coding.csv` 并看 `verdict/out/mode/realized` 分布；
5. 主样本 A 稳定后，再重跑市场反应。
