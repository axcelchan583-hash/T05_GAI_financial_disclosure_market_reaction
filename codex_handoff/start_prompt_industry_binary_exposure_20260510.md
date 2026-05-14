# Handoff: T05 行业级 0/1 暴露度（方案 A）

Date: 2026-05-10
Recipient: Codex
Owner: 主线 T05 GAI-assisted financial disclosure writing

## 一句话目标

为 T05 的 difference-in-exposure DID 构造一个**行业级 0/1 暴露度**变量 `HighRiskDiscIndustry_i`，作为现有连续 `PreRiskWritingBurden_i` 的稳健性对照。最终产出一个企业-年面板的暴露度变量 + 一个 validation memo。

## 必读上下文

进 T05 后按顺序读：

1. `T05_GAI_financial_disclosure_market_reaction/README.md`
2. `docs/research_design_v0.md`
3. `docs/variable_definitions_v0.md`
4. `docs/did_xy_design_update_20260511.md`（最新设计，主 X = Post × PreRiskWritingBurden）

不读 `annual_report_2025_*.md`，那是文本抓取计划，不影响本任务。

## 任务定位

当前主表用连续暴露 `PreRiskWritingBurden_i`（pre-2023 风险章节长度 / 复杂度等）。已知风险：

- 连续 exposure DID 的平行趋势假设比 0/1 DID 更强；
- 暴露度和公司规模、行业等基本面高度相关，可能被 `Size × Year FE` 类趋势污染；
- 审稿人一句"你这就是大公司效应"很难驳。

**方案 A**：构造行业级 0/1 暴露度，定义"哪些行业天然就要写大量风险披露"。逻辑：行业分类对单个公司外生，比公司层面连续暴露更难被 endogeneity 攻击。

**重要**：这个变量是稳健性对照，**不是替换主表**。主表保留连续 `PreRiskWritingBurden_i`。

## 数据源

A 股数据 parquet 在：

```
/Users/mac/computerscience/0暂时不做了/22数据要素与AI溢出/data/interim/
```

关键文件：

- `stk_listcoinfo.parquet`：上市公司基础信息，含 CSRC 行业代码（一级 / 二级）
- `controls_firm_year.parquet`：公司-年面板，可作为样本框
- `iar_rept.parquet`：年报披露元数据，确认年份范围

列名规范（项目级）见 `/Users/mac/computerscience/23选题探索/CLAUDE.md`：
`stkcd` 小写 zfill(6)，部分文件用 `report_year` 不是 `year`。

## 要做的事

### Step 1：行业级 0/1 分类规则

按 CSRC 一级行业分类，分三类：

**HighRiskDiscIndustry = 1**（监管/业务天然要求重风险披露）：

- 金融业（J）：货币金融、资本市场、保险、其他金融
- 房地产业（K）
- 采矿业（B）
- 电力、热力、燃气及水生产和供应业（D）
- 制造业（C）的子类：医药制造（C27）、化学原料和化学制品（C26）、石油加工（C25）
- 交通运输、仓储和邮政业（G）的航空运输、水上运输
- 信息传输、软件和信息技术服务业（I）

**HighRiskDiscIndustry = 0**（监管要求低 / 业务简单）：

- 农林牧渔业（A）
- 批发和零售业（F）
- 住宿和餐饮业（H）
- 居民服务、修理和其他服务业（O）
- 文化、体育和娱乐业（R）

**Excluded（中间样本，给主表保留但暴露度赋 NaN）**：

- 制造业（C）剩余子行业
- 建筑业（E）
- 租赁和商务服务业（L）
- 科学研究和技术服务业（M）
- 水利、环境和公共设施管理业（N）
- 教育（P）、卫生和社会工作（Q）

理由：制造业内部异质性极大，不强分；其他中间行业监管要求不清晰，剔除以保持处理组/对照组对比锐利。

### Step 2：数据驱动验证（关键，不可省）

用 pre-period（2018-2021）的风险披露长度数据，检验上述行业分类是否真的对应"风险披露负担"：

- 若 T05 已有文本数据，直接算行业层均值/中位数 `PreRiskWritingBurden_i`，看 HighRiskDiscIndustry=1 组是否显著高于 =0 组。
- 若**没有**文本数据（目前 `data/` 是空的），用 `iar_rept.parquet` 中的年报总字数或风险章节字节数作代理。如果连这都没有，**先在 handoff 里 flag 出来**，不要硬编。

输出一张行业级摘要表：

```
csrc_l1_code | csrc_l1_name | n_firms | mean_risk_length_pre | HighRiskDiscIndustry
```

让人能一眼看出分类是否合理。

### Step 3：构造公司-年面板变量

```
HighRiskDiscIndustry_i:  时不变，按 stkcd 标记
LowRiskDiscIndustry_i:   时不变，1 - HighRiskDiscIndustry_i（仅对非排除样本）
```

样本范围：

- 期间：2018-2025（视 `iar_rept.parquet` 实际覆盖）
- 公司：A 股全样本，剔除 ST/PT、金融业可保留（金融业本身就是 HighRiskDisc=1 的重要组成）

输出 parquet：

```
T05_GAI_financial_disclosure_market_reaction/data/interim/industry_binary_exposure_v0.parquet
```

字段：`stkcd, csrc_l1_code, csrc_l1_name, HighRiskDiscIndustry, in_sample`。

### Step 4：和主 X 的兼容性检查

把 `HighRiskDiscIndustry_i` 和现有（或将要构造的）`PreRiskWritingBurden_i` 做相关性表：

- 行业 0/1 vs 连续暴露度的相关系数
- 行业 0/1 = 1 内部，连续暴露度的分布
- 行业 0/1 = 0 内部，连续暴露度的分布

如果两者相关性极高（>0.7），说明行业 0/1 几乎就是连续版本的二分，价值有限——要在 memo 里如实报告，不要硬卖。

### Step 5：写 validation memo

输出：

```
T05_GAI_financial_disclosure_market_reaction/docs/industry_binary_exposure_v0_20260510.md
```

包含：

1. 分类规则（Step 1）+ 理由
2. 行业级摘要表（Step 2）
3. 主表（连续）vs 稳健性（0/1）的样本量对比
4. 已知 caveats：
   - 制造业被剔除会损失多少样本
   - 金融业作为 HighRiskDisc=1 会不会被审稿人质疑（金融业有自己的会计准则）
   - 2022 年报是否要排除（与现有设计一致）
5. 不写"识别成立"或"主结果稳健"等判断——本任务只构造变量，不跑 DID。

## 不要做

1. **不要跑 DID 回归**。本任务只到变量构造和描述统计。
2. **不要替换 `PreRiskWritingBurden_i` 作主 X**。主表保持连续。
3. **不要发明行业层文本指标**——如果没有文本数据，flag 出来等下一步，不要硬编。
4. **不要把制造业内部强行分类**。"制造业整体属于高风险披露"和"制造业整体属于低风险披露"都不成立。
5. **不要修改 `docs/research_design_v0.md` 或 `did_xy_design_update_20260511.md`**。如有设计层面建议，写在 memo 末尾的 "open questions" 段落。

## 输出清单

完成后应该有：

```
T05_GAI_financial_disclosure_market_reaction/
├── data/interim/industry_binary_exposure_v0.parquet           # Step 3 输出
├── docs/industry_binary_exposure_v0_20260510.md               # Step 5 memo
└── scripts/build_industry_binary_exposure.py                  # 构造脚本
```

脚本要可重跑，路径硬编为绝对路径，列名按项目规范。

## 期望符号 / 完成判据

- HighRiskDiscIndustry=1 组的 pre-period 风险披露长度均值应**显著高于** =0 组（验证分类合理）。
- 样本量：HighRiskDiscIndustry=1 应至少有几百家公司，=0 应至少有上百家，否则统计功效太弱。
- 行业 0/1 和连续 burden 的相关系数应在 0.3-0.6 之间——太低说明分类无效，太高说明二分没新增价值。

如果上述判据有任何一条不通过，**不要硬交**，在 memo 里报死因。
