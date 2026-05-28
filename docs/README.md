# Docs Index

更新时间：2026-05-28

这个目录已经按用途整理。后续默认先看 `design/`；旧设计、降级路线和早期版本都放进 `archive/` 或保留为历史诊断，避免继续混在当前主线里。

## 先看这里

当前主线是 v6 capital-market peer revaluation：

```text
主问题：
    更具体的 GenAI 披露是否被市场解读为竞争威胁信号，
    从而使 AI-active 的 Top5 产品市场竞品出现更负短窗重估？

主 Y：
    peer signed market-model CAR[0,+1]

机制 Y：
    peer GenAI disclosure response within 60 / 90 / 180 days
    但严格口径下不显著，只能做描述性后续反应

验证 Y：
    CAC 生成式 AI 服务备案 / 深度合成算法备案
    当前不作为主 Y
```

最重要的当前文件：

- `design/09_project_outline_v8_after_measurement_checks_20260528.md`
- `design/00_REVIEW_PACKAGE_README_20260525.md`
- `design/01_current_research_design_20260525.md`
- `design/02_paper_outline_20260525.md`
- `design/03_chatgpt_pro_review_prompt_20260525.md`
- `design/04_chatgpt_pro_feedback_digest_20260525.md`
- `design/05_design_freeze_20260525.md`
- `design/06_specificity_validation_codebook_20260525.md`
- `design/07_specificity_validation_execution_plan_20260525.md`
- `design/08_paper_outline_current_20260527.md`
- `empirical_runs/53_v6_final_review_checks_20260525.md`
- `empirical_runs/54_v6_focal_good_news_pretrend_checks_20260525.md`
- `empirical_runs/55_specificity_validation_sample_20260525.md`
- `empirical_runs/57_v7_ai_supply_chain_disclosure_diagnostic_20260527.md`
- `empirical_runs/58_v7_ai_supply_chain_stacked_did_20260527.md`
- `empirical_runs/59_v7_disclosure_type_horserace_20260527.md`
- `empirical_runs/60_v7_event_time_peer_validity_20260527.md`
- `empirical_runs/61_v8_measurement_final_checks_20260527.md`
- `empirical_runs/52_v6_identification_strengthening_checks_20260524.md`
- `empirical_runs/50_v6_external_ai_active_on_ai_stripped_similarity_20260524.md`

2026-05-28 最新收口判断：

```text
主市场反应结果仍成立：
    final sample N = 7,805
    events = 2,177
    ext_any coef = -0.002303, p = 0.020
    + AI-theme abnormal return × AIActive 后 coef = -0.002112, p = 0.032

人工编码分支暂时不进入主线：
    该结果只作为内部测度边界检查，不作为主线否定证据。

当前主文仍使用 Specificity_z 作为 objective text-detail / disclosure concreteness proxy，
但不把它写成“真实 GenAI 落地具体性”的人工金标准测度。
```

如果只给网页版 / Claude 上传材料，优先上传 clean package：

```text
../claude_project/4/T05_review_package_4_20260528_clean.zip
```

如果对方不能上传 zip，再按以下顺序传：

1. `../claude_project/4/01_PROJECT_BRIEF_EN.md`
2. `../claude_project/4/prompts/01_CLAUDE_REVIEW_PROMPT_EN.md`
3. `../claude_project/4/prompts/02_CHATGPT_PRO_REVIEW_PROMPT_EN.md`
4. `../claude_project/4/source_docs/01_current_paper_outline_20260527.md`
5. `../claude_project/4/source_docs/02_final_review_checks_20260525.md`
6. `../claude_project/4/source_docs/03_focal_good_news_pretrend_checks_20260525.md`
7. `../claude_project/4/source_docs/04_disclosure_type_horserace_20260527.md`
8. `../claude_project/4/source_docs/05_event_time_peer_validity_20260527.md`
9. `../claude_project/4/results_csv/headline.csv`

也可以直接上传：

```text
../claude_project/4/T05_review_package_4_20260528_clean.zip
```

## 目录结构

- `current/`: 当前仍在推进的研究设计、数据执行计划、go/no-go 诊断和文献锚点。
- `design/`: 2026-05-25 成稿审阅包，当前最推荐从这里开始看。
- `empirical_runs/`: 已完成的试跑记录。保留结果与失败路径，但不作为当前主线入口。
- `prompts/`: 给 ChatGPT Pro / Claude / 深度研究模式使用的 prompt。
- `archive/design_history/`: v0-v3、v8-v10 以及已经降级的历史路线。
- `archive/annual_report/`: 2025 年报跟踪计划和早期年报路线。
- `archive/assets/`: 历史图片或临时素材。
- `选题/`: 旧路径兼容入口，只保留 README 指向新目录。

## Current

当前主线入口已移到 `design/`。`current/` 中的文件主要用于复盘路线演化。

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

- `60_v7_event_time_peer_validity_20260527.md`: task 4/5 输出；包含 daily event-time 图、window lead-lag 图、Top1-3/Top4-5/Top6-10/low-sim/random 的产品市场近邻有效性表和系数图。
- `61_v8_measurement_final_checks_20260527.md`: 最新收口检查；冻结 final headline sample，报告 AI-theme date-shock controls、external AIActive 组件审计、经济量级换算和 placebo 摘要。300 条双编码结果暂作内部测度边界检查，不进入当前主线。
- `59_v7_disclosure_type_horserace_20260527.md`: 披露类型 horse-race。四类 Type × AIActive 不能吃掉 `Specificity_z × AIActive`；supply-chain 披露只有平均 peer effect 为正，更像 category validation。
- `58_v7_ai_supply_chain_stacked_did_20260527.md`: AI 供应链披露分支的 stacked event-DID。结论是 Top5 `Supply × Post[0,+1]` 不显著，low-sim DDD 也不显著；不能作为当前主线 DID。
- `57_v7_ai_supply_chain_disclosure_diagnostic_20260527.md`: AI 供应链披露文本诊断。横截面事件窗中供应链披露对应正向 Top5 peer CAR，更像 category validation，但与原主线 `Specificity_z × AIActivePeer` 是不同分支。
- `53_v6_final_review_checks_20260525.md`: 当前最重要的最终复核；包括 headline 主结果、specificity validation、产品市场距离梯度、lead/lag、external AIActive breakdown、严格机制检验。
- `54_v6_focal_good_news_pretrend_checks_20260525.md`: 最新核心稳健性；加入 FocalCAR 与 FocalCAR × AIActive，并用 PeerCAR[-10,-2] 净化 Y 后重跑。
- `55_specificity_validation_sample_20260525.md`: 300 条 specificity validation 样本构造记录，来自当前 headline Top5 事件宇宙，按 specificity 高中低分层。
- `52_v6_identification_strengthening_checks_20260524.md`: 识别强化；formal DDD、pre-window placebo、focal CAR sign、question-triggered subsample、non-GenAI pseudo-event。
- `51_v6_peer_firm_fe_identification_check_20260524.md`: peer firm FE 检查。
- `50_v6_external_ai_active_on_ai_stripped_similarity_20260524.md`: external AIActive 接到 AI-word-stripped 产品相似度后的稳健性。
- `49_v6_external_ai_active_peer_checks_20260524.md`: external AIActivePeer 第一轮检查。
- `48_v6_announcement_clean_random_placebo_20260524.md`: 公告清洗后的随机同业 placebo。
- `47_v6_ai_stripped_similarity_checks_20260524.md`: 剔除 AI 词后的产品相似度稳健性。
- `46_v6_announcement_clean_and_trading_response_20260524.md`: 公告清洗与交易反应检查。
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
