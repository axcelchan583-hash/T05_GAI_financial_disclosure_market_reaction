# 重新构造 X 和 Y：设计文件索引

当前 source of truth：

- `08_genai_announcement_experiment_design_v3_1_20260610.md`：判定树与编码主规则；
- `10_genai_coding_amendment_v3_2_20260611.md`：v3.2 增补，GenAI 认定亮线（产出/标的描述需明确指向大模型/AIGC，背景段提 ChatGPT 不算）、`INFRA` 标签、`D` 与 `D-fw` 的 2×2 边界澄清。编码时两份并读。

理论重构备忘：

- `09_深度研究与重构方案.md`：将 v3.1 的 `A` vs `D-fw` 样本重构接到 credible disclosure vs cheap talk 的理论框架；可作为 v4 设计候选，但尚未替代 v3.1 编码口径。

LLM 审核记录：

- `../../empirical_runs/113_v49_v50_deepseek_v4pro_coding_audit_20260610.md`

当前人工编码入口：

- `/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告PDF人工审核_v3_1_20260610.md`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_DS_V4Pro_复核工作台_118_20260610.md`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_coding.csv`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_machine.csv`

历史文件：

- `04_genai_announcement_taxonomy_experiment_design_20260609.md`：v1，taxonomy 过重，已弃用。
- `05_genai_announcement_manual_coding_template_20260609.md`：v1 编码模板，已弃用。
- `06_genai_announcement_taxonomy_experiment_design_v2_20260609.md`：v2.1，保留了清洗层和 product/process 对照，但已被 v3.1 判定树替代。
- `07_genai_announcement_manual_coding_template_v2_20260609.md`：v2.1 多字段模板，已被 v3.1 一行人工码替代。

当前主线：

1. 先用 v3.1 重构可信、首次、事件日可用的 GenAI disclosure 样本；
2. 主结果仍是 product-market competitors 的短窗负反应；
3. 主机制仍是 `Specificity × AIActivePeer`；
4. `D-fw` 框架协议/cheap talk 样本保留公告日，作为 placebo / contrast group；
5. `OUT/M/R` 只做辅助异质性和稳健性，不替代 `Specificity`。
