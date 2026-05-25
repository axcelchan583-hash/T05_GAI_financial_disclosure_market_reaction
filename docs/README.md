# Docs Index

更新时间：2026-05-24

这个目录已经按用途整理。后续默认先看 `current/`；旧设计、降级路线和早期版本都放进 `archive/` 或保留为历史诊断，避免继续混在当前主线里。

## 先看这里

当前主线已经从 v5.1 调整为 v6：

```text
主问题：
    GenAI 披露是否引发产品市场竞品的资本市场重估？

主 Y：
    peer signed CAR / abnormal turnover / abnormal volume

机制 Y：
    peer GenAI disclosure response within 60 / 90 / 180 days

验证 Y：
    CAC 生成式 AI 服务备案 / 深度合成算法备案
```

最重要的当前文件：

- `current/41_v6_market_reaction_main_peer_diffusion_mechanism_20260523.md`
- `empirical_runs/38_csmar_genai_event_library_smoke_20260523.md`
- `empirical_runs/39_csmar_v5_1_response_smoke_20260523.md`
- `empirical_runs/40_csmar_peer_diffusion_main_effect_20260523.md`
- `empirical_runs/42_v6_csmar_peer_market_reaction_smoke_20260523.md`
- `empirical_runs/43_v6_simple_main_effect_20260523.md`
- `empirical_runs/44_v6_market_model_and_placebo_20260524.md`
- `empirical_runs/45_v6_main_effect_full_checks_20260524.md`
- `current/31_v4_experimental_design_ai_active_peer_20260522.md`
- `current/32_v4_go_no_go_diagnostics_20260522.md`

如果只给网页版 / Claude 上传材料，优先上传：

1. `current/41_v6_market_reaction_main_peer_diffusion_mechanism_20260523.md`
2. `empirical_runs/38_csmar_genai_event_library_smoke_20260523.md`
3. `empirical_runs/44_v6_market_model_and_placebo_20260524.md`
4. `empirical_runs/45_v6_main_effect_full_checks_20260524.md`
5. `empirical_runs/43_v6_simple_main_effect_20260523.md`
6. `empirical_runs/42_v6_csmar_peer_market_reaction_smoke_20260523.md`
7. `empirical_runs/40_csmar_peer_diffusion_main_effect_20260523.md`
8. `current/32_v4_go_no_go_diagnostics_20260522.md`
9. `empirical_runs/39_csmar_v5_1_response_smoke_20260523.md`

## 目录结构

- `current/`: 当前仍在推进的研究设计、数据执行计划、go/no-go 诊断和文献锚点。
- `empirical_runs/`: 已完成的试跑记录。保留结果与失败路径，但不作为当前主线入口。
- `prompts/`: 给 ChatGPT Pro / Claude / 深度研究模式使用的 prompt。
- `archive/design_history/`: v0-v3、v8-v10 以及已经降级的历史路线。
- `archive/annual_report/`: 2025 年报跟踪计划和早期年报路线。
- `archive/assets/`: 历史图片或临时素材。
- `选题/`: 旧路径兼容入口，只保留 README 指向新目录。

## Current

- `41_v6_market_reaction_main_peer_diffusion_mechanism_20260523.md`: 当前主线；主 Y 回到竞品资本市场反应，竞品 GenAI 披露扩散降级为机制，CAC 备案作为外部验证。
- `37_v5_1_layered_iip_cac_disclosure_response_smoke_20260523.md`: v5.1 历史设计；原本以 IIP->IIP 竞品披露响应为主 Y。现在已降级为机制思路。
- `34_v5_long_term_rival_ai_investment_design_20260522.md`: rival AI hiring 设计；因招聘是慢变量，当前不再作为主入口。
- `36_recruitment_data_and_v5_y_risk_audit_20260522.md`: 招聘数据覆盖与 v5 主 Y 风险审计；结论是招聘数据更适合增强 pre-event AIActivePeer。
- `31_v4_experimental_design_ai_active_peer_20260522.md`: v4 短窗市场反应设计；v6 的直接前身。
- `32_v4_go_no_go_diagnostics_20260522.md`: v4 双向聚类后的 go/no-go 诊断。
- `30_v4_theory_interaction_screen_20260522.md`: 三重交互方向筛选记录。
- `29_v4_controls_and_ai_capability_heterogeneity_20260522.md`: 控制变量和 AI capability 异质性试跑。
- `28_v4_csmar_main_effect_rerun_20260522.md`: CSMAR 日收益重跑后的主效应记录。
- `27_v4_csmar_return_coverage_diagnostic_20260522.md`: 日收益覆盖诊断。
- `26_v4_data_processing_execution_plan_20260522.md`: 数据处理执行计划。
- `22_v4_product_market_peer_spillover_research_plan_20260522.md`: v4 初始计划；用于理解路线演化。
- `measurement_literature_anchor_after_meeting.md`: X/Y 测度文献锚点。
- `data_fit_audit_20260518.md`: 当前数据适配审计。

## Empirical Runs

- `38_csmar_genai_event_library_smoke_20260523.md`: CSMAR 投资者互动 + 调研问答 GenAI 事件库构造记录；合并后 40,691 条 answer-level、23,454 个 firm-day 事件。
- `39_csmar_v5_1_response_smoke_20260523.md`: v5.1 的 `Specificity × Similarity -> peer disclosure response` 试跑；核心交互不显著，支持降级。
- `40_csmar_peer_diffusion_main_effect_20260523.md`: 产品市场同伴 GenAI 披露扩散试跑；Top10 60/90/180 天有正向信号，适合作为机制。
- `42_v6_csmar_peer_market_reaction_smoke_20260523.md`: v6 主 Y 试跑；完整 CSMAR 事件库下，首次 GenAI 披露样本的 `Specificity × ProductSimilarity × AIActivePeer` 对竞品短窗 CAR 有负向初步信号。
- `43_v6_simple_main_effect_20260523.md`: v6 简化主效应；把 ProductSimilarity 改为 Top5/Top10 样本定义，主交互只保留 `Specificity × AIActivePeer`，首次披露样本显著为负。
- `44_v6_market_model_and_placebo_20260524.md`: v6 补充检验；market-model CAR 下 Top5 主结果保留，低相似度同行 placebo 不成立，随机同行 placebo 仍需进一步处理。
- `45_v6_main_effect_full_checks_20260524.md`: v6 主效应完整复核；加入 peer industry-week FE 与 100 次随机同行 placebo，确认 `CAR[0,+1]` 的 Top5 负向结果不是随机同业伪相关。
- `15_v8_3_external_evidence_link_pilot_20260519.md`: 外部证据连接旧试跑。
- `18_v3_genai_specificity_car_pilot_20260522.md`: v3 自身 CAR 最小试跑。
- `19_v3_event_library_expansion_diagnostic_20260522.md`: v3 事件库扩容诊断。
- `20_v3_supplier_spillover_sample_diagnostic_20260522.md`: 供应链溢出样本诊断。
- `21_plan_A_irqa_multichannel_event_study_20260522.md`: 互动平台多渠道事件研究计划。
- `23_v4_x_peer_similarity_pilot_20260522.md`: 产品相似度 X 构造试跑。
- `24_v4_peer_spillover_main_effect_pilot_20260522.md`: v4 平均竞品效应试跑。

## Prompts

- `16_deep_research_prompt_XY_distance_20260521.md`: 早期 X/Y 距离审计 prompt。
- `17_deep_research_prompt_force_one_X_one_Y_20260521.md`: 强制锁定一个主 X 和主 Y 的 prompt。
- `25_deep_research_prompt_significance_and_reference_design_20260522.md`: v4 显著性与范文处理 prompt。
- `25_deep_research_prompt_significance_and_reference_design_EN_20260522.md`: 上一条的英文版。
- `33_deep_research_prompt_independent_go_no_go_EN_20260522.md`: v4 独立 go/no-go prompt。
- `35_claude_brief_v5_rival_ai_hiring_EN_20260522.md`: v5 给 Claude 网页版的简洁英文介绍。

## Archive

`archive/design_history/` 保留早期题目探索、v1-v3、v8-v10 和被降级的路线。除非需要复盘“为什么不做某条线”，后续不建议从这里开始读。

`archive/annual_report/` 保留年报路线的计划和待披露跟踪文件。年报 GenAI 披露仍可作为补充数据源，但不再是当前主线入口。
