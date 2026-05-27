#!/usr/bin/env python3
"""Machine pre-coding for the specificity validation sample.

This is a reproducible first pass, not final human validation.
It follows docs/design/06_specificity_validation_codebook_20260525.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "data" / "specificity_validation" / "specificity_validation_sample_300_20260525.csv"
OUT_DIR = ROOT / "data" / "specificity_validation"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "56_specificity_machine_coding_20260525.md"

GENAI_TERMS = [
    "ChatGPT",
    "GPT",
    "GenAI",
    "AIGC",
    "大模型",
    "生成式AI",
    "生成式人工智能",
    "通义",
    "文心",
    "Kimi",
    "智谱",
    "星火",
    "盘古",
    "混元",
    "DeepSeek",
    "多模态",
    "自然语言处理",
    "机器学习",
    "人工智能生成",
]
GENAI_PAT = re.compile("|".join(re.escape(x) for x in GENAI_TERMS), re.I)
NEGATIVE_PAT = re.compile(
    r"(?:暂不|暂未|尚未|未|无|没有|不|暂无|尚无).{0,18}(?:涉及|开展|布局|接入|应用|使用|推出|发布|相关业务|相关产品|相关技术|合作)|"
    r"(?:不涉及|未涉及|暂无涉及|暂不涉及|暂未涉及|尚未涉及|没有涉及).{0,20}(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能)|"
    r"(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能).{0,30}(?:暂不涉及|暂未涉及|不涉及|未涉及|暂无|尚无|没有|未应用|尚未应用)|"
    r"(?:没有将|尚未将|暂未将).{0,30}(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能|该技术).{0,30}(?:应用|接入|用于)|"
    r"(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能|该技术).{0,30}(?:没有|暂无|尚无|尚未|暂未|无).{0,30}(?:应用场景|应用|接入|合作|业务往来)|"
    r"(?:与|和).{0,12}(?:DeepSeek|ChatGPT|GPT|通义|文心|Kimi|智谱).{0,12}(?:没有|暂无|尚无|无).{0,12}(?:合作|业务往来)",
    re.I,
)
NEG_WORD_PAT = re.compile(r"(?:暂不|暂未|尚未|未|无|没有|不涉及|暂无|尚无|没有将|尚未将|暂未将)", re.I)
NEG_TARGET_PAT = re.compile(
    r"(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能|DeepSeek|通义|文心|Kimi|智谱|星火|盘古|混元|多模态|该技术|相关技术|相关业务|相关产品)",
    re.I,
)
NEG_ACTION_PAT = re.compile(
    r"(?:涉及|开展|布局|接入|应用|使用|推出|发布|合作|业务往来|适用的应用场景|应用场景|落地|部署|商业化)",
    re.I,
)

PATTERNS = {
    "has_specific_product_service": re.compile(
        r"(?:产品|服务|平台|系统|软件|APP|应用|方案|工具|机器人|助手|模块|解决方案|智能体|Agent|座舱|客服|模型平台|大模型平台)",
        re.I,
    ),
    "has_model_platform_name": re.compile(
        r"(?:ChatGPT|GPT-?\d*|DeepSeek|通义千问|通义|文心一言|文心|Kimi|智谱|ChatGLM|星火|盘古|混元|豆包|百川|MiniMax|月之暗面|LLaMA|Gemini|Claude|自研大模型|行业大模型|垂直大模型|多模态大模型)",
        re.I,
    ),
    "has_specific_use_case": re.compile(
        r"(?:客服|营销|文案|研发|生产|办公|教育|医疗|诊断|金融|投研|汽车|智能座舱|风控|质检|设计|代码|编程|问答|搜索|推荐|训练|翻译|数字人|语音|图像|视频|绘画|内容生成|数据分析|知识库|政务|运维|供应链|招聘|法律|审计)",
        re.I,
    ),
    "has_customer_or_industry": re.compile(
        r"(?:客户|用户|行业|企业|医院|银行|学校|政府|政务|汽车|金融|医疗|教育|制造|电力|能源|运营商|B端|C端|ToB|ToC|场景|业务线|下游)",
        re.I,
    ),
    "has_partner_or_org": re.compile(
        r"(?:合作|伙伴|联合|共建|生态|阿里|百度|腾讯|华为|微软|OpenAI|英伟达|商汤|讯飞|京东|字节|火山|智谱|清华|北大|大学|研究院|实验室|银行|客户)",
        re.I,
    ),
    "has_deployment_status": re.compile(
        r"(?:已上线|已经上线|已发布|已经发布|已推出|已经推出|已备案|备案通过|已通过|已落地|已经落地|已部署|已经部署|已接入|已经接入|已应用|已经应用|应用于|试点|内测|公测|完成训练|正在训练|签署|签订|已签约|商业化|量产|交付|升级)",
        re.I,
    ),
    "has_commercialization_or_timeline": re.compile(
        r"(?:收入|订单|合同|商业化|付费|收费|销售|降本|增效|推广|市场化|规模化|预计.{0,12}上线|预计.{0,12}推出|将于.{0,12}上线|将于.{0,12}发布|年内.{0,12}上线|上半年.{0,12}上线|下半年.{0,12}上线|20[2-9]\d年.{0,12}(?:上线|推出|发布|交付|商业化)|Q[1-4].{0,12}(?:上线|推出|发布|交付|商业化))",
        re.I,
    ),
    "has_quantitative_commitment": re.compile(
        r"(?:\d+(?:\.\d+)?(?:亿元|万元|元|万美元|美元|人民币|%|％|个|项|款|台|套|人|家|年|月|日|亿|万|次|小时|天|倍|G|GB|TB|亿参数|参数))|(?:Q[1-4]|[一二三四1234]季度)",
        re.I,
    ),
}

COMPANY_ACTION_PAT = re.compile(
    r"(?:公司|本公司|我司|我们|集团).{0,60}"
    r"(?:已|已经|正在|推出|发布|接入|应用|使用|部署|落地|研发|开发|训练|测试|内测|试点|合作|签署|签订|商业化|上线|升级|打造|建设|形成)",
    re.I,
)
GENAI_ACTION_PAT = re.compile(
    r"(?:接入|应用|使用|部署|落地|研发|开发|训练|测试|内测|试点|合作|签署|签订|商业化|上线|升级|打造|建设|推出|发布).{0,35}"
    r"(?:ChatGPT|GPT|AIGC|大模型|DeepSeek|通义|文心|Kimi|智谱|星火|盘古|混元|生成式|多模态|自然语言处理)|"
    r"(?:ChatGPT|GPT|AIGC|大模型|DeepSeek|通义|文心|Kimi|智谱|星火|盘古|混元|生成式|多模态|自然语言处理).{0,35}"
    r"(?:接入|应用|使用|部署|落地|研发|开发|训练|测试|内测|试点|合作|签署|签订|商业化|上线|升级|打造|建设|推出|发布)",
    re.I,
)
WEAK_ATTENTION_PAT = re.compile(r"(?:关注|密切关注|积极关注|探索|研究|储备|跟踪|研判|学习|考察|考虑)", re.I)
PURE_EXPLANATION_PAT = re.compile(
    r"(?:ChatGPT由OpenAI|OpenAI实验室推出|广泛应用必然|带来内容创作|存储需求也会增加|请问|建议公司|是否有|有没有|可能存在广泛应用场景|可以应用于|主要体现在|应用前景|未来会有较多应用)",
    re.I,
)


def clean_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？；;])", text)
    return [p.strip() for p in parts if len(p.strip()) >= 4]


def genai_context(text: str) -> str:
    sentences = split_sentences(text)
    selected: list[str] = []
    for idx, sent in enumerate(sentences):
        if GENAI_PAT.search(sent):
            # Include the direct sentence and one adjacent sentence when short enough;
            # this captures answers where the concrete product appears right before the GenAI term.
            if idx > 0 and len(sentences[idx - 1]) <= 180:
                selected.append(sentences[idx - 1])
            selected.append(sent)
            if idx + 1 < len(sentences) and len(sentences[idx + 1]) <= 180:
                selected.append(sentences[idx + 1])
    if not selected:
        return text[:1200]
    seen = []
    for item in selected:
        if item not in seen:
            seen.append(item)
    return " ".join(seen)[:1800]


def sentence_is_negative(sent: str) -> bool:
    if NEGATIVE_PAT.search(sent):
        return True
    if not (NEG_TARGET_PAT.search(sent) or GENAI_PAT.search(sent)):
        return False
    return bool(NEG_WORD_PAT.search(sent) and NEG_ACTION_PAT.search(sent))


def sentence_is_positive_action(sent: str) -> bool:
    if sentence_is_negative(sent):
        return False
    if GENAI_ACTION_PAT.search(sent):
        return True
    if COMPANY_ACTION_PAT.search(sent) and GENAI_PAT.search(sent):
        return True
    return False


def is_negative_disclosure(context: str) -> bool:
    if not GENAI_PAT.search(context):
        return False
    sentences = split_sentences(context)
    neg_sentences = [sent for sent in sentences if sentence_is_negative(sent)]
    if not neg_sentences:
        return False
    positive_sentences = [sent for sent in sentences if sentence_is_positive_action(sent)]
    # If the only concrete GenAI implementation statement is denial, treat as zero.
    return len(positive_sentences) == 0


def has_company_genai_action(context: str) -> bool:
    for sent in split_sentences(context):
        if sentence_is_positive_action(sent):
            return True
    return False


def is_pure_general_comment(context: str) -> bool:
    if has_company_genai_action(context):
        return False
    if PURE_EXPLANATION_PAT.search(context):
        return True
    # Pure attention / exploration without a concrete company action is not specificity.
    if WEAK_ATTENTION_PAT.search(context) and not PATTERNS["has_deployment_status"].search(context):
        if not re.search(r"(?:产品|平台|系统|客户|订单|收入|部署|上线|应用于|试点|商业化)", context):
            return True
    return False


def snippet_for(context: str, pattern: re.Pattern[str] | None = None) -> str:
    sentences = split_sentences(context)
    if pattern is not None:
        for sent in sentences:
            if pattern.search(sent):
                return sent[:160]
    for sent in sentences:
        if GENAI_PAT.search(sent):
            return sent[:160]
    return context[:160]


def score_from_components(values: dict[str, int]) -> int:
    s = int(sum(values.values()))
    implementation = values.get("has_deployment_status", 0) or values.get("has_commercialization_or_timeline", 0)
    quantitative = values.get("has_quantitative_commitment", 0)
    if s <= 0:
        return 0
    if s == 1:
        return 1
    if s <= 3 and not implementation:
        return 2
    if s <= 5 and (implementation or quantitative):
        return 3
    if s >= 6 or (s >= 4 and implementation and quantitative):
        return 4
    return min(3, s)


def code_one(row: pd.Series) -> dict[str, object]:
    answer = clean_text(row.get("sample_answer", ""))
    context = genai_context(answer)
    neg = is_negative_disclosure(context)

    component_cols = list(PATTERNS.keys())
    values: dict[str, int] = {}
    if neg:
        values = {k: 0 for k in component_cols}
        evidence = snippet_for(context)
        notes = "Machine pre-code: negative/no-current-involvement disclosure; concrete non-GenAI business details ignored."
        score = 0
    elif is_pure_general_comment(context):
        values = {k: 0 for k in component_cols}
        evidence = snippet_for(context)
        notes = "Machine pre-code: general industry comment or weak attention statement; no company-specific GenAI implementation detail."
        score = 0
    else:
        company_action = has_company_genai_action(context)
        for col, pat in PATTERNS.items():
            values[col] = int(bool(pat.search(context)))
        # Restrict broad component hits to company-specific GenAI contexts.
        if not company_action:
            for col in [
                "has_specific_product_service",
                "has_specific_use_case",
                "has_customer_or_industry",
                "has_partner_or_org",
                "has_deployment_status",
                "has_commercialization_or_timeline",
                "has_quantitative_commitment",
            ]:
                values[col] = 0
        # If a public external model is merely named with no company implementation detail,
        # do not count it as a company-specific model/platform claim.
        if values["has_model_platform_name"] and not company_action:
            values["has_model_platform_name"] = 0
        # Partner/org needs an actual relation, not only an outside model/company name.
        if values["has_partner_or_org"] and not re.search(r"(?:合作|伙伴|联合|共建|接入|签署|签订|生态)", context):
            values["has_partner_or_org"] = 0
        # Generic future consideration is not deployment/commercialization.
        if re.search(r"(?:是否接入|考虑是否|后续.*根据|暂无.*计划|尚处于.*探索)", context):
            values["has_deployment_status"] = 0
            values["has_commercialization_or_timeline"] = 0
        score = score_from_components(values)
        positive_patterns = [PATTERNS[k] for k, v in values.items() if v]
        evidence = snippet_for(context, positive_patterns[0] if positive_patterns else None)
        notes = "Machine pre-code using codebook-aligned regex over GenAI context."

    uncertain = int(len(context) < 15 or "?" in context[:20])
    component_sum = int(sum(values.values()))
    return {
        "validation_id": row["validation_id"],
        "event_id": row["event_id"],
        "machine_context": context,
        **values,
        "machine_component_sum": component_sum,
        "machine_specificity_score_0_4": score,
        "machine_uncertain_flag": uncertain,
        "machine_evidence_snippet": evidence,
        "machine_coder_notes": notes,
    }


def corr_row(df: pd.DataFrame, y: str, x: str) -> dict[str, object]:
    a = pd.to_numeric(df[y], errors="coerce")
    b = pd.to_numeric(df[x], errors="coerce")
    valid = a.notna() & b.notna()
    if valid.sum() < 3:
        return {"y": y, "x": x, "n": int(valid.sum()), "pearson": np.nan, "spearman": np.nan}
    return {
        "y": y,
        "x": x,
        "n": int(valid.sum()),
        "pearson": float(a[valid].corr(b[valid], method="pearson")),
        "spearman": float(a[valid].corr(b[valid], method="spearman")),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    sample = pd.read_csv(IN_PATH)
    coded = pd.DataFrame([code_one(row) for _, row in sample.iterrows()])
    out = sample.merge(coded, on=["validation_id", "event_id"], how="left")

    out_path = OUT_DIR / "specificity_validation_machine_coding_300_20260525.csv"
    jsonl_path = OUT_DIR / "specificity_validation_machine_coding_300_20260525.jsonl"
    summary_path = OUT_DIR / "specificity_validation_machine_coding_summary_20260525.csv"
    corr_path = OUT_DIR / "specificity_validation_machine_coding_correlations_20260525.csv"

    out.to_csv(out_path, index=False)
    with jsonl_path.open("w", encoding="utf-8") as f:
        for _, row in out.iterrows():
            rec = {
                "validation_id": row["validation_id"],
                "event_id": row["event_id"],
                "has_specific_product_service": int(row["has_specific_product_service"]),
                "has_model_platform_name": int(row["has_model_platform_name"]),
                "has_specific_use_case": int(row["has_specific_use_case"]),
                "has_customer_or_industry": int(row["has_customer_or_industry"]),
                "has_partner_or_org": int(row["has_partner_or_org"]),
                "has_deployment_status": int(row["has_deployment_status"]),
                "has_commercialization_or_timeline": int(row["has_commercialization_or_timeline"]),
                "has_quantitative_commitment": int(row["has_quantitative_commitment"]),
                "machine_specificity_score_0_4": int(row["machine_specificity_score_0_4"]),
                "machine_uncertain_flag": int(row["machine_uncertain_flag"]),
                "machine_evidence_snippet": row["machine_evidence_snippet"],
                "machine_coder_notes": row["machine_coder_notes"],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    component_cols = list(PATTERNS.keys())
    summary_rows: list[dict[str, object]] = []
    for col in component_cols:
        summary_rows.append(
            {
                "metric": col,
                "mean": float(out[col].mean()),
                "sum": int(out[col].sum()),
                "n": int(out[col].notna().sum()),
            }
        )
    summary_rows.extend(
        [
            {
                "metric": "machine_component_sum",
                "mean": float(out["machine_component_sum"].mean()),
                "sum": int(out["machine_component_sum"].sum()),
                "n": int(out["machine_component_sum"].notna().sum()),
            },
            {
                "metric": "machine_specificity_score_0_4",
                "mean": float(out["machine_specificity_score_0_4"].mean()),
                "sum": int(out["machine_specificity_score_0_4"].sum()),
                "n": int(out["machine_specificity_score_0_4"].notna().sum()),
            },
        ]
    )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(summary_path, index=False)

    corr = pd.DataFrame(
        [
            corr_row(out, "machine_component_sum", "specificity_z"),
            corr_row(out, "machine_specificity_score_0_4", "specificity_z"),
            corr_row(out, "machine_component_sum", "specificity"),
            corr_row(out, "machine_specificity_score_0_4", "specificity"),
            corr_row(out, "machine_component_sum", "total_specific_items"),
            corr_row(out, "machine_specificity_score_0_4", "total_specific_items"),
        ]
    )
    corr.to_csv(corr_path, index=False)

    by_bin = (
        out.groupby("specificity_bin", dropna=False)[["machine_component_sum", "machine_specificity_score_0_4"]]
        .agg(["mean", "count"])
        .round(3)
    )
    score_dist = out["machine_specificity_score_0_4"].value_counts().sort_index().to_dict()
    neg_count = int(out["machine_coder_notes"].str.contains("negative/no-current", regex=False).sum())

    doc = f"""# Specificity Machine Pre-Coding

Date: 2026-05-25

This is a reproducible machine pre-code for the 300-event specificity validation sample. It is not a substitute for human coding or API-based LLM coding; use it as a first pass for review and error correction.

## Inputs

- `data/specificity_validation/specificity_validation_sample_300_20260525.csv`
- `docs/design/06_specificity_validation_codebook_20260525.md`

## Outputs

- `data/specificity_validation/specificity_validation_machine_coding_300_20260525.csv`
- `data/specificity_validation/specificity_validation_machine_coding_300_20260525.jsonl`
- `data/specificity_validation/specificity_validation_machine_coding_summary_20260525.csv`
- `data/specificity_validation/specificity_validation_machine_coding_correlations_20260525.csv`

## Coding Logic

The script extracts GenAI-context sentences, handles explicit negative/no-current-involvement statements, and codes eight codebook components:

```text
{component_cols}
```

Explicit negative/no-current-involvement statements coded as zero-component disclosures:

```text
{neg_count}
```

## Score Distribution

```text
{score_dist}
```

## Means by Specificity Tercile

```text
{by_bin.to_string()}
```

## Correlations with Existing Specificity Proxy

```text
{corr.to_string(index=False)}
```

## Next Step

Human review should focus first on:

1. rows where machine score is high but `specificity_bin` is low;
2. rows where machine score is low but `specificity_bin` is high;
3. rows with negative/no-current-involvement notes;
4. rows with `machine_uncertain_flag = 1`.

After human or API-LLM coding is available, compute kappa / agreement against this machine pre-code only as a diagnostic. The publishable validation should use human and LLM/human overlap, not this deterministic pre-code alone.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"wrote {out_path}")
    print(f"wrote {jsonl_path}")
    print(f"wrote {summary_path}")
    print(f"wrote {corr_path}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
