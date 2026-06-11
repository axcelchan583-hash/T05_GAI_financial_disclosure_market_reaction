# v51 DeepSeek V4-Pro v3.2 GenAI announcement re-audit

Date: 2026-06-11

## Purpose

Re-run the 118 previously reviewed v49/v50 cases under the v3.2 coding standard. The key v3.2 change is that X is now a broad **GenAI value-chain initiative disclosure**: `model / app / compute / data` chain-in cases can qualify, while generic AI or chain-out disclosures are `D`. `A` and `D-fw` cases should carry a `L=` layer tag.

The model outputs are still pre-coding only. They are used to prioritize human review and to test how much the v3.2 standard changes the v3.1 judgments.

## Inputs

- v3.2 prompt: `docs/prompts/56_genai_announcement_llm_precoding_prompt_v3_2_20260611.md`
- Builder script: `scripts/build_v51_deepseek_v3_2_reaudit_20260611.py`
- API runner: `scripts/run_v50_siliconflow_batch_20260610.py`
- Output directory: `results/v51_deepseek_v3_2_reaudit118_20260611/`
- Provider/model: SiliconFlow `deepseek-ai/DeepSeek-V4-Pro`

The `results/` directory is ignored by git. This note records the run summary needed for repo history.

## Run Status

- Cases: 118
- Parsed success: 118
- Parse errors: 0
- API errors after retry: 0
- Prompt tokens: 404,806
- Completion tokens: 117,749
- Total tokens: 522,555
- Changed from v3.1 DS verdict: 26
- New `A` from previous non-`A`: 10
- Previous `A` downgraded/non-`A` under v3.2: 7
- `A` / `D-fw` missing layer: 0

v3.2 verdict counts:

- `A`: 49
- `C`: 8
- `D`: 30
- `D-fw`: 30
- `U`: 1

v3.2 layer counts:

- `model`: 27
- `app`: 26
- `compute`: 32
- `data`: 2
- missing: 31

The missing layer rows are `D` / `U`, where `L=` is not required.

## Main Transitions

New `A` from previous non-`A`:

- `POM3_00270` 弘信电子: `D -> A`, `L=compute`
- `POM3_00724` 恒信东方: `C -> A`, `L=compute`
- `POM3_01133` *ST宇顺: `D -> A`, `L=compute`
- `POM3_01153` 弘信电子: `D-fw -> A`, `L=compute`
- `POM3_01157` 达实智能: `C -> A`, `L=app`
- `POM3_00168` 众合科技: `D -> A`, `L=compute`
- `POM3_00607` 建设银行: `B -> A`, `L=model`
- `POM3_00761` 每日互动: `C -> A`, `L=app`
- `POM3_00918` 上海电影: `C -> A`, `L=app`
- `POM3_01519` 老百姓: `B -> A`, `L=app`

Previous `A` downgraded under v3.2:

- `POM3_00211` 昆仑万维: `A -> C`, non-first/progress disclosure
- `POM3_00300` 浩瀚深度: `A -> D`, chain-out deepfake detection system
- `POM3_01111` 神开股份: `A -> D`, chain-out intelligent drilling software
- `POM3_01357` 探路者: `A -> D`, signal/display IP with only background model mention
- `POM3_01426` 视觉中国: `A -> U`, target company's chain-in status unclear
- `POM3_01570` 申昊科技: `A -> D`, chain-out industrial robot / embodied-intelligence application
- `POM3_01242` 润建股份: `A -> D`, chain-out maintenance service

## Obsidian Review Handoff

The v3.2 review workbench was written to:

`/Users/mac/Documents/Obsidian Vault/23-5/T05_DS_V4Pro_v3_2_复核工作台_118_20260611.md`

Human review syntax:

```text
复核: 通过
复核: 不通过
人工改判: A | OUT=1 | M=own | L=compute | R=- | 证=...
人工理由: ...
```

Review order:

1. `P0-新旧迁移`
2. `P1-must_review/U`
3. `P2-一致`

## Implications

The v3.2 rule does not merely loosen the old sample. It moves compute-heavy announcements into the chain-in universe, but also pushes several old `A` cases out as chain-out or non-first events. Human review should therefore prioritize the 26 changed cases and the 5 must-review / `U` rows before expanding to the full 1,601-row workbench.
