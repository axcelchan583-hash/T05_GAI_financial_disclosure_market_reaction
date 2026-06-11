# v49/v50 DeepSeek V4-Pro GenAI announcement coding audit

Date: 2026-06-10

## Purpose

Use DeepSeek V4-Pro via SiliconFlow as a first-pass audit for the v3.1 GenAI announcement coding rules. The model outputs are not final human codes. They are used to prioritize manual review and to test whether the v3.1 `A / B / C / D-fw / D` rules are operational.

## Inputs

- Machine workbench CSV: `/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_machine.csv`
- v49 pilot output directory: `results/v49_deepseek_v3_1_pilot_20260610/`
- v50 batch output directory: `results/v50_deepseek_v3_1_batch100_20260610/`
- Provider/model: SiliconFlow `deepseek-ai/DeepSeek-V4-Pro`

The `results/` directories are ignored by git. This note records the lightweight audit summary needed for repo history.

## v49 pilot

Cases: 18

Final parsed status after retry:

- Parsed success: 18
- Parse errors: 0
- API errors after retry: 0

Model verdict counts:

- `A`: 6
- `C`: 1
- `D`: 4
- `D-fw`: 7

Important conflict:

- `POM3_00040` 中文在线 was machine/human-draft `A`, but V4-Pro classified it as `D-fw` because the announcement was a strategic framework agreement with no specific amount and future cooperation terms to be separately negotiated.

## v50 batch100

Cases: 100

Final parsed status:

- Parsed success: 100
- Parse errors: 0
- API errors after retry: 0
- Machine/V4-Pro conflicts: 38
- V4-Pro `must_review`: 6

Model verdict counts:

- `A`: 40
- `B`: 2
- `C`: 11
- `D`: 19
- `D-fw`: 28

Machine versus V4-Pro cross tab:

| machine | A | B | C | D-fw | D | total | A-retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 35 | 0 | 8 | 13 | 4 | 60 | 58.3% |
| D-fw | 2 | 0 | 0 | 15 | 3 | 20 | 10.0% |
| B | 3 | 2 | 3 | 0 | 2 | 10 | 30.0% |
| D | 0 | 0 | 0 | 0 | 10 | 10 | 0.0% |

Category by V4-Pro verdict:

| category | A | B | C | D-fw | D | total |
|---|---:|---:|---:|---:|---:|---:|
| 产品/平台/模型发布、上线、成果发布 | 7 | 0 | 4 | 0 | 0 | 11 |
| 投资/建设/增资/收购/智算中心/大模型项目 | 25 | 2 | 7 | 3 | 19 | 56 |
| 签署战略合作/合作协议 | 8 | 0 | 0 | 25 | 0 | 33 |

## Combined 118-case summary

Across the v49 pilot and v50 batch:

| machine | A | B | C | D-fw | D | total | A-retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 41 | 0 | 8 | 14 | 4 | 67 | 61.2% |
| D-fw | 2 | 0 | 0 | 20 | 3 | 25 | 8.0% |
| B | 3 | 2 | 4 | 1 | 3 | 13 | 23.1% |
| D | 0 | 0 | 0 | 0 | 13 | 13 | 0.0% |

Main interpretation:

- The initial machine `A` queue is too broad. V4-Pro keeps only 41/67 machine-`A` cases as `A`.
- Most machine-`A` downgrades are `D-fw` strategic/framework agreements or `C` duplicate/progress announcements.
- The `D` queue is clean in this audit: 13/13 sampled machine-`D` cases remain `D`.
- `B` is unstable and should remain a manual backfill queue, not an automatic sample class.

## Obsidian review handoff

The 118 reviewed cases were written to:

`/Users/mac/Documents/Obsidian Vault/23-5/T05_DS_V4Pro_复核工作台_118_20260610.md`

The Obsidian note orders cases as:

1. `P0-冲突`: machine and V4-Pro disagree;
2. `P1-must_review`: V4-Pro self-flags for review;
3. `P2-一致`: machine and V4-Pro agree.

Human review syntax:

```text
复核: 通过
复核: 不通过
人工改判: A | OUT=1 | M=ext | R=- | 证=...
人工理由: ...
```

## Implications for design

The audit supports the v3.1 decision to keep `D-fw` as a cheap-talk/framework-agreement pool rather than dropping it as plain noise. The next empirical rerun should not use the old 1055/1066 event treatment directly. It should wait for the manually reviewed `A` sample and then rerun:

1. `A` competitor CAR;
2. `D-fw` competitor CAR;
3. `A` versus `D-fw` stacked contrast;
4. `Credible × AIActivePeer` with event fixed effects;
5. `Spec × AIActivePeer` on the cleaned sample.
