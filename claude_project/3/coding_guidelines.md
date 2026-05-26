# Specificity Validation — Coding Guidelines (for Claude Code continuation)

Date started: 2026-05-26
Coder identity in output: `claude_opus_coder`
Status: SV0001–SV0160 coded (rows 1–160). SV0161–SV0300 still to do.

These are the operational decision rules an independent coder applied on top of
`10_specificity_validation_codebook_20260525.md`. The purpose is to keep the
remaining 140 rows consistent with the first 160. Read this BEFORE coding more rows.

## 0. Non-negotiable method rule

DO NOT keyword-match or regex to assign codes. The entire point of this validation
is to produce a human-judgment label that is INDEPENDENT of the machine
`Specificity_z` measure (which is itself a text/keyword statistic). Read each
`sample_answer` and judge it. Use the keyword/`specificity_z`/`specificity_bin`
columns only as context, never as the basis for a code. Do not look at `agent1`
codes before coding a row — code independently, then comparison is computed after.

## 1. The construct is GENERATIVE-AI specificity, not AI specificity

Code only GenAI / large-model / AIGC content in the company ANSWER. The investor
question alone never counts. Critically, **substantive but non-GenAI AI content
scores 0 on the GenAI components even when it is concrete and impressive.** This is
the single most important rule and the main source of human↔machine disagreement.

Treat as OFF-CONSTRUCT (→ all components 0, score 0 unless a GenAI element is also present):
- computer vision / image recognition / 3D perception (e.g. SV0007, SV0075)
- traditional ML / 智能分析系统 / 大数据模型 (medical-test analytics SV0053)
- RPA, OCR, 活体识别, 知识图谱, NLP-only systems (when not LLM/generative)
- AI chips / signal-processing chips (SV0048), GNSS chips (SV0121)
- HVAC/energy-control AI (SV0103), smart-factory automation / MES/SCADA (SV0148)
- medical-imaging AI platforms not described as generative/大模型 (SV0092)
- enterprise AI/ML platforms with no named GenAI element (SV0035)
- hardware whose only GenAI link is being a component in the AI supply chain:
  servers/液冷/散热 (SV0079, SV0094, SV0147), display panels (SV0091, SV0095),
  optics/光波导 (SV0089, SV0120), structural parts for AIPC (SV0065), memory/封装

When the answer is non-GenAI AI that is genuinely rich (named platform, deployed,
customers), set `uncertain_flag=1` and explain in notes, but keep GenAI components 0.
Examples flagged this way: SV0007, SV0075, SV0092, SV0101, SV0116, SV0118, SV0120.

## 2. Denials and pure attention → score 0, all components 0

- "暂未涉及 / 尚未开展 / 没有 / 不涉及 / 未接入 / 没有计划引入 ChatGPT/AIGC/大模型/DeepSeek"
  → all 0, score 0. (Vast majority of `bin=low` 2023 rows and many DeepSeek-era rows.)
- "持续关注 / 高度重视 / 密切跟踪 / 紧跟趋势 / 保持开放态度" with no concrete activity
  → all 0, score 0.
- A model named only inside a denial ("暂未涉及 Kimi 大模型", SV0127) does NOT earn C2.

## 3. The exploration ladder (how to score "doing something")

Order from weakest to strongest. Score reflects where the GenAI activity sits:

- score 0: denial / pure attention / industry commentary with no own activity
  (incl. expert explanations of what ChatGPT is — SV0100, SV0140).
- score 1: ONE weak concrete detail. Typically:
  - exploring/researching GenAI in NAMED concrete scenarios but not deployed
    (SV0096 bank 办公/风控/客服; SV0122 medical; SV0150 tourism; SV0154; SV0156 论证研究)
  - a launched/planned project or internal platform not yet in use (SV0066 拟建 AIGC平台)
  - employee training / encouraged office use (SV0158)
  - a future plan naming a model + concrete use but not deployed (SV0144)
  - GenAI in development inside an otherwise-deployed non-GenAI system (SV0128, SV0129)
- score 2: SEVERAL concrete details (e.g. named model + concrete use case, or named
  partner + concrete tech) but no clear full deployment/commercial path
  (SV0033 ChatGPT used internally, vague use; SV0057 LLM for code/ops; SV0064 DS deploying;
   SV0119 智源 partner + CPU-LLM adaptation; SV0123 讯飞+星火 lab; SV0139 DeepSeek API接入)
- score 3: concrete GenAI product/use case PLUS deployment, OR plus a named partner.
  (SV0011, SV0015, SV0056, SV0067, SV0068, SV0083, SV0098, SV0104, SV0111, SV0141)
- score 4: highly concrete — product/use case + deployment + (customer segment, OR
  multiple deployed GenAI uses, OR named foundation model in production).
  (SV0044 自研营销垂类大模型已部署+广告主; SV0082 大语音模型 used in 中高考;
   SV0085 多款AIGC教育产品已推出; SV0093 虚拟人直播已落地+AIGC中台; SV0160 自研系统接DeepSeek-R1)

The 0–4 score is a holistic judgment and need NOT equal the component sum.

## 4. Component-by-component rules as actually applied

- C1 has_specific_product_service: a concrete GenAI product/platform/system/solution/
  chatbot/数字人. Internal-only use of a model with no product = 0. Planned/拟建 = 0.
- C2 has_model_platform_name: named model OR named GenAI platform — ChatGPT, GPT,
  DeepSeek(-R1), Kimi, 星火大模型, 文心, 自研垂类/大语音/配方/电力大模型, named AIGC platform.
  Generic "大模型技术 / 生成式AI / 大语言模型" with NO name = 0. Named-in-denial = 0.
- C3 has_specific_use_case: a concrete function/scenario (智能客服, 文案/视频生成, 代码生成,
  风控, 投研, 配方设计, 智能打分, 电网运维...). "赋能业务 / 提升效率 / 内部业务及对客业务" = 0.
  A concrete scenario that is only aspirational/explored can still earn C3=1; deployment
  is captured separately by C6.
- C4 has_customer_or_industry: a named customer type / downstream sector / user group
  (广告主, 中考高考/学校/学生, 电网, 港口行业, 全球客户, 轨道交通). Own generic sector = 0.
- C5 has_partner_or_org: a NAMED external org / partner / investee / research institute /
  named subsidiary-as-distinct-org (智源研究院 SV0119; 科大讯飞 SV0123; K-Scale Labs SV0097;
  芊熹洛杉矶 subsidiary SV0102). Unnamed "外部技术伙伴 / 头部大模型公司" = 0. Partner tied
  only to NON-GenAI business (阿里/华为 for 互联网电视 SV0026) = 0.
- C6 has_deployment_status: concrete stage — 已上线/已发布/已接入/已部署/已落地/已商用/正式接入/
  已完成接入/正在使用. "计划/拟/未来将/积极探索/论证研究/正在规划" = 0. If the platform is
  live but the GenAI piece is still 建设/训练/推进中, judge the GenAI piece (usually 0 or borderline).
- C7 has_commercialization_or_timeline: revenue/订单/收费/上线日期/项目周期/明确里程碑 tied to
  GenAI. Generic "商业空间广阔 / 为客户创造价值" = 0. (Rarely 1 in this sample.)
- C8 has_quantitative_commitment: a NUMBER tied to GenAI (投入金额/团队人数/参数/客户数/收入/
  成本下降%/上线日期). Numbers about non-GenAI things (chip specs, robot 身高体重, 数据湖个数,
  收入占比) do NOT count. (Rarely 1 in this sample.)

## 5. Recurring tricky patterns (resolved decisions)

- Mixed answer: deployed non-GenAI NLP/CV product + GenAI only "研究/探索"
  → GenAI components 0, score 1, uncertain_flag=1. (SV0041, SV0109, SV0116)
- Cognitive/NLP language-AI deployed at scale but pre-generative (科大讯飞 SV0101)
  → keep components conservative, score ≤2, uncertain_flag=1, note the construct boundary.
- Company merely SUPPLIES the AI boom (data/算力/storage/components) → off-construct,
  score 0–1, not a GenAI deployer. (SV0112 data-resource library = score 1, the rest 0.)
- Industry-commentary / "what ChatGPT is" with no own activity → score 0–1, often uncertain=1.

## 6. uncertain_flag usage

Set `uncertain_flag=1` (and explain) when: the activity is substantive AI but its
generative/大模型 nature is genuinely unclear (SV0007, SV0092, SV0101, SV0118), or the
answer is truncated / mixes deployed-NLP with explored-GenAI (SV0041, SV0100, SV0109,
SV0116). Keep it sparing — clear denials and clear deployments are NOT uncertain.
Use component value `9` only if a single component is truly indeterminate; in 160 rows
it was never needed (binary judgment was always reachable).

## 7. Output

Fill the template columns: coder_id, coding_date, the 8 `has_*` components,
specificity_score_0_4, uncertain_flag, evidence_snippet (a short verbatim GenAI phrase
from the answer, <15 words), coder_notes (brief Chinese rationale). Preserve all
pre-filled metadata columns and the SV id order. After all 300 rows, compute
agreement vs agent1 (per-component Cohen's κ + agreement rate; Spearman on component
sum; correlation on the 0–4 score) per codebook §"Agreement Statistics".
