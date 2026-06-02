# 在中国数据里逼近 Qian (2025) 事件口径的构建方案

日期：2026-06-02

目标：把 v23 那个"问答关键词命中"的事件群，重建成 Qian 口径——
**每家公司首次、公司作为行动方、具体的 GenAI initiative；剔除否认 / 套话 / 纯投资者提问触发。**
AR/CAR 机器（v23 脚本 §A 已审为正确）不动，只换事件侧输入。

---

## 0. Qian 事件口径回顾（要逼近的目标）

Qian §4.1 + 第6页：
- 事件 = 公司**首次**"具体 GenAI initiative"：投资 GenAI / 采用 GenAI 工具 / 把 GenAI 集成进产品 / 把 GenAI 纳入工作流；
- 来源 = 新闻通讯社（PR Newswire 等）+ **人工核验**；
- **剔除** 1,397 条只泛泛提"GenAI and other IT"的；
- 公司是行动方（不是被问到才回应）；
- 产品导向 vs 流程导向人工分类（H6）。

---

## 1. 源表替换：用什么替代"新闻通讯社"

按"公司是行动方 + 真 initiative"的纯度从高到低，分三层。建议**主样本用 Tier 1，Tier 2 做扩样稳健性**。

| Tier | 中国数据源 | 对应 Qian 的什么 | 纯度 | 量级 |
| --- | --- | --- | --- | --- |
| **T1a** | **CAC 生成式AI服务备案 / 深度合成算法备案**（`extract_cac_genai_service_filing_tables.py`，字段 `company / model_name / filing_date / status=已备案`） | 最接近"真上线的 GenAI 产品/服务" | 最高 | 小（百级公司） |
| **T1b** | **正式公告**（CSMAR `公告基本信息表 + 公告分类关联表(ClassifyName) + 公告证券关联表(Title)`），按类别 + GenAI 关键词筛 | 最接近 Qian 的"公司主动披露的 initiative" | 高 | 中小 |
| **T2** | **互动易 IIP（ReplyContent）+ 调研问答 IR_QA（Answer）** 事件库，**经 initiative 分类器过滤** | 扩样，但必须重筛 | 中（过滤后） | 大 |

理由：
- CAC 备案是**监管登记**，等于"公司真的部署了 GenAI 服务"——比任何文本都硬，是 Qian "specific initiative" 在中国最干净的对应物。
- 正式公告里公司是行动方；问答里公司常是被动应答。
- v23 的错就在于直接用了 T2 的**未过滤**版本（含否认/套话）。

---

## 2. initiative 分类：两遍法（先规则、后 LLM）

对每条候选事件文本（CAC：model_name+status；公告：Title；问答：answer_text）打一个 4 分类标签：
`genuine_initiative / denial / boilerplate_attention / question_only`。

### 2.1 第一遍：规则（先扔掉明显的否认/套话/纯提问）

直接可用的正则（基于 v23 实际文本归纳）：

```python
import re

# A. 否认 —— 直接剔除
DENIAL = re.compile(
    r"(暂无|尚无|暂未|尚未|目前没有|目前无|未涉及|不涉及|暂不涉及|不直接涉及|"
    r"无(相关|该项|此类)?(业务|产品|技术|应用|布局|储备)|没有(相关)?(业务|产品|布局)|"
    r"不存在|与公司无关|未开展|未应用|未部署|无生成式|无大模型|无ChatGPT|无chatGPT)"
)

# B. 套话/泛泛关注 —— 无具体交付时剔除（Qian 剔的就是这类）
BOILERPLATE = re.compile(
    r"(持续关注|密切关注|保持关注|积极关注|将关注|会关注|正在(研究|探索|论证|评估)|"
    r"积极探索|有所(关注|了解)|前沿(技术|领域)|顺应趋势|不断学习)"
)

# C. 行动/落地动词 —— 命中才可能是 genuine（公司作为行动方）
INITIATIVE_ACTION = re.compile(
    r"(已(推出|上线|发布|落地|应用|部署|实现|完成|投产|量产|交付|集成|搭载)|"
    r"推出了|正式发布|已上线|已量产|已应用于|已部署|已集成|已搭载|"
    r"完成(备案|登记)|通过(备案|登记)|已(中标|签约|中选)|"
    r"自主研发的(大模型|模型|平台)|发布(了)?(.{0,8})?(大模型|模型|平台|产品)|"
    r"投资(建设|设立)|设立(合资|子)公司|战略合作(协议)?(已)?签署)"
)

def first_pass_label(text: str) -> str:
    t = str(text or "")
    if DENIAL.search(t):
        return "denial"
    if INITIATIVE_ACTION.search(t):
        return "genuine_initiative"      # 仍需第二遍 LLM 复核
    if BOILERPLATE.search(t):
        return "boilerplate_attention"
    return "uncertain"                   # 交给 LLM
```

注意顺序：**否认优先**（"已关注但暂无业务"要判否认，不能被 action 词误命中）。

### 2.2 actor / 触发源过滤（解决 v23 "触发词在提问里"的问题）

- 问答类必须满足：**GenAI 触发词出现在 `answer_terms`（公司回答），而不是只在 `question_terms`（投资者提问）里**。
  事件库已分列 `answer_terms` / `question_terms`，直接用：`require len(answer_terms)>0`。
- 进一步：initiative 动词必须出现在**公司回答/公告正文**，不是复述投资者的话。

### 2.3 第二遍：复用现有 LLM 机器编码器

项目已有 `specificity_validation_machine_coding`（脚本 `run_specificity_machine_coding_20260525.py`），
输出字段直接就是 Qian initiative 判据。定义 **initiative gate**：

```text
is_genuine_initiative =
    (machine_uncertain_flag == 0)
AND first_pass_label != "denial"
AND (
        has_deployment_status == 1            # 已部署/上线
     OR has_specific_product_service == 1     # 具体产品/服务
     OR has_commercialization_or_timeline==1  # 商业化/时间表
     OR (has_model_platform_name==1 AND INITIATIVE_ACTION 命中)  # 自研模型/平台 + 行动
    )
AND NOT (只命中 has_specific_use_case 且整体是 BOILERPLATE)
```

即：**至少有一个"硬交付"维度（部署/产品/商业化/自研模型+行动）**，才算 initiative。
这正是 Qian "specific initiatives" 与"broadly reference GenAI"的分界，用结构化字段落地。

CAC 备案行天然满足（status=已备案 → 视为 has_deployment_status=1），可跳过 LLM。

---

## 3. Qian 对齐的样本过滤（事件确定后）

照搬 Qian §4.1 清洗，项目已有设施：

1. **每公司首次**：按 focal_code 取最早 `is_genuine_initiative` 事件日。
2. **混杂事件清洗 [-2,+1]**：用 `announcement_stock_day_flags`（已建，含重大资产/重组/收购/对外投资/重大合同/担保/关联交易/诉讼/股权激励/质押/减持增持/回购/破产清算/重大事项等类别 `MAJOR_PAT`）。
   - 焦点公司侧：剔除事件 [-2,+1] 内有上述重大公告的（Qian 对 announcing firm 的稳健性）。
   - 供应商侧：剔除供应商在 [-2,+1] 有重大公告/业绩/并购的（Qian 主清洗）。
3. **penny / size**：剔除事件日股价过低（A 股可用 < 2 元 或 ST 标记）、剔除估计期 < 120 交易日（市场模型 min_obs）。
4. **多客户重叠**：一个供应商对应多个客户且事件日重叠时剔除（Qian 做法）。
5. **供应商自身先披露**：剔除供应商在客户事件日前/当天已有 genuine GenAI initiative（v23 已有 `drop_affected_prior_genai`，但要把判定从"任意 GenAI 文本"收紧为"genuine_initiative"）。

---

## 4. 产品 vs 流程导向（Qian H6）

用 LLM 字段直接派生：

```text
product_oriented = 1 if (
    has_specific_product_service==1            # AI 增强/新 AI 产品
 OR has_model_platform_name==1                 # 自研模型/平台对外
) and 不是纯内部效率场景
else 0  (流程导向：内部运营/客服自动化/供应链优化/办公提效)
```

辅助关键词：流程导向命中 `内部(管理|办公|流程)|降本增效|客服(自动化)?|运营效率|供应链优化|质检|风控自动化`。

---

## 5. 输出 schema（喂回 v23 AR 机器）

事件表（每行一个 genuine initiative 事件）：

```text
event_id, focal_code(=customer), event_date,
event_source (cac_filing / formal_announcement / iip_answer / ir_qa_answer),
init_label (genuine_initiative), product_oriented (0/1),
is_first_focal_initiative (0/1),
machine_specificity_score_0_4, has_deployment_status, ... (留作 X / 稳健性),
trigger_in_answer (0/1)
```

然后**直接接 v23 的 `normalize_chain_panel → attach_event_returns`**（那套 AR/CAR/检验是对的），
把 `strict_genai_event` 替换为 `is_genuine_initiative & is_first_focal_initiative`。

---

## 6. 现实预期与判读

- T1a+T1b（CAC + 正式公告）样本会小（几十到一二百客户事件 × 上市供应商），但**干净**——这才是真正能和 Qian 比较的样本。
- T2（过滤后问答）能扩样，但要把"genuine_initiative 占比"报出来（v23 现在只有约 7%）。
- 判读分三种：
  1. 干净 T1 样本下供应商 AR0 **显著正** → 复刻成功（中美一致）。
  2. 显著 **负/零** → 在排除事件污染后，才是可写的"中美供应链溢出差异"。
  3. 样本太小无法判 → 老实写"中国正式披露 + 上市供应链数据不足以支撑 Qian 式供应商溢出检验"，回到 T05 横向竞争主线。

> 关键纪律：**先把事件筛成 genuine_initiative，再谈符号。** 否则永远在 Qian 扔掉的样本上打转。

---

## 7. 落地顺序（建议）

1. 写 `build_v24_qian_aligned_genai_initiative_events_YYYYMMDD.py`：
   读 CAC + 公告 + 事件库 → 第一遍规则标签 → （问答类）调 LLM 机器编码器 → initiative gate → 每公司首次 → 产品/流程。
2. 复用 v23 供应链匹配 + AR 机器，换事件输入，跑 AR0/CAR + 方向 placebo。
3. 报告：genuine_initiative 占比、样本流失、AR0 三种判读、与 v23（未过滤）对照表。
