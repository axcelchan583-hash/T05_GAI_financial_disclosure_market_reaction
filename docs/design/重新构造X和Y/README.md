# 重新构造 X 和 Y：设计文件索引

当前 source of truth：

- `11_experiment_design_v4_20260611.md`：**实验设计定稿**（假设、表序 T1–T9、识别防守、执行顺序）；
- `08_genai_announcement_experiment_design_v3_1_20260610.md`：判定树与编码主规则；
- `10_genai_coding_amendment_v3_2_20260611.md`：v3.2 增补，X 定为 GenAI 产业链宽口径（model/app/compute/data 四层链内即可进 A，泛 AI 判 D），`L=` 层标签、`D` 与 `D-fw` 的 2×2 边界澄清、宽口径三件实证防守。编码时 08+10 并读。
- `12_genai_coding_amendment_v3_3_20260612.md`：v3.3 小补丁，补充 AI 算力高速互联光模块/光芯片的 `L=compute` 专用性 gate，并规定控股子公司少数股东权益收购默认判 `C`。全量 LLM 预编码按 08+10+12 执行。

理论备忘：

- `09_深度研究与重构方案.md`：signed detector 理论框架与引用栈（Farrell-Gibbons、Chakraborty-Harbaugh、contagion vs competitive 符号分离），v4 设计的承重理论从此取。

LLM 审核记录：

- `../../empirical_runs/113_v49_v50_deepseek_v4pro_coding_audit_20260610.md`
- `../../empirical_runs/114_v51_deepseek_v3_2_reaudit_20260611.md`

当前人工编码入口：

- `/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告PDF人工审核_v3_1_20260610.md`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_DS_V4Pro_v3_2_复核工作台_118_20260611.md`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_coding.csv`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_machine.csv`

归档文件：

- `archive/20260612_prior_versions/02_wide_collaborator_competitor_experiment_design_20260607.md`：早期 wide-collaborator/competitor 设计草稿，已被 v4 主线替代。
- `archive/20260612_prior_versions/03_disclosure_text_feature_design_20260608.md`：早期文本特征设计备忘，保留作历史参考。
- `archive/20260612_prior_versions/04_genai_announcement_taxonomy_experiment_design_20260609.md`：v1，taxonomy 过重，已弃用。
- `archive/20260612_prior_versions/05_genai_announcement_manual_coding_template_20260609.md`：v1 编码模板，已弃用。
- `archive/20260612_prior_versions/06_genai_announcement_taxonomy_experiment_design_v2_20260609.md`：v2.1，保留了清洗层和 product/process 对照，但已被 v3.1 判定树替代。
- `archive/20260612_prior_versions/07_genai_announcement_manual_coding_template_v2_20260609.md`：v2.1 多字段模板，已被 v3.1 一行人工码替代。

Obsidian 旧入口归档在：

- `/Users/mac/Documents/Obsidian Vault/23-5/archive/T05_20260612_prior_versions/`

当前主线：

1. 先用 v3.1 重构可信、首次、事件日可用的 GenAI disclosure 样本；
2. 主结果仍是 product-market competitors 的短窗负反应；
3. 主机制仍是 `Specificity × AIActivePeer`；
4. `D-fw` 框架协议/cheap talk 样本保留公告日，作为 placebo / contrast group；
5. `OUT/M/L/R` 只做辅助异质性和稳健性，不替代 `Specificity`。
