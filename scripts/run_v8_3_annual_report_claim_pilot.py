#!/usr/bin/env python3
"""Annual-report sentence pilot for v8.3 claim-level design.

This scans 2024 A-share annual-report TXT files for GenAI-specific, forward-looking
sentences, assigns a rough specificity score, and joins coarse AI-investment support
plus one-year-ahead 2025 annual-report textual evidence.
It is a feasibility pilot, not the final claim-matched realization dataset.
"""

from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源")
TXT_ZIP = (
    DATA_ROOT
    / "上市公司年报信息/年报文本/2001~2024年年报/2001-2024年A股年报TXT格式/2024_5405份.zip"
)
TXT_DIR_2025 = ROOT / "data" / "raw" / "annual_reports_2025_txt" / "年报txt"
INVEST_ZIP = DATA_ROOT / "上市公司数据相关信息/人工智能投资水平131920031(仅供沪江大学使用).zip"
OUT_DIR = ROOT / "results" / "v8_3_claim_text_pilot"
DOC_OUT = ROOT / "docs" / "选题" / "14_v8_3_claim_text_pilot_20260517.md"


GENAI_TERMS = [
    "生成式人工智能",
    "生成式AI",
    "生成式 AI",
    "AIGC",
    "大模型",
    "大语言模型",
    "语言大模型",
    "基础模型",
    "ChatGPT",
    "GPT",
    "DeepSeek",
    "文心一言",
    "通义千问",
    "通义",
    "千问",
    "盘古大模型",
    "混元",
    "豆包",
    "智能体",
]

FORWARD_TERMS = [
    "将",
    "拟",
    "计划",
    "规划",
    "未来",
    "持续",
    "进一步",
    "加快",
    "推进",
    "推动",
    "建设",
    "打造",
    "开发",
    "研发",
    "探索",
    "布局",
    "升级",
    "优化",
    "引入",
    "接入",
    "应用",
    "赋能",
    "投入",
]

SCENARIO_TERMS = [
    "客服",
    "研发",
    "生产",
    "制造",
    "营销",
    "销售",
    "办公",
    "财务",
    "风控",
    "合规",
    "供应链",
    "设计",
    "运营",
    "知识库",
    "问答",
    "质检",
    "投研",
    "医疗",
    "教育",
    "金融",
]

ENTITY_TERMS = [
    "平台",
    "系统",
    "产品",
    "模型",
    "大模型",
    "智能体",
    "助手",
    "知识库",
    "客服",
    "算法",
    "应用",
]

PARTNER_TERMS = [
    "合作",
    "联合",
    "生态伙伴",
    "阿里",
    "腾讯",
    "百度",
    "华为",
    "科大讯飞",
    "商汤",
    "字节",
    "OpenAI",
    "DeepSeek",
    "通义",
    "文心",
]

SUBJECT_TERMS = [
    "公司",
    "本公司",
    "子公司",
    "事业部",
    "部门",
    "团队",
    "客户",
    "业务线",
]

REALIZATION_TERMS = [
    "已",
    "完成",
    "建成",
    "上线",
    "发布",
    "推出",
    "落地",
    "部署",
    "投产",
    "投入使用",
    "取得",
    "获得",
    "备案",
    "专利",
    "软著",
    "著作权",
    "注册",
    "商业化",
    "客户应用",
    "实现",
    "形成",
    "服务于",
    "应用于",
    "收入",
]


def read_first_xlsx_from_zip(path: Path) -> pd.DataFrame:
    with ZipFile(path) as zf:
        xlsx_names = [name for name in zf.namelist() if name.lower().endswith(".xlsx")]
        if not xlsx_names:
            raise FileNotFoundError(f"No .xlsx found in {path}")
        with zf.open(xlsx_names[0]) as f:
            return pd.read_excel(f)


def clean_investment() -> pd.DataFrame:
    invest = read_first_xlsx_from_zip(INVEST_ZIP)
    invest = invest[pd.to_datetime(invest["EndDate"], errors="coerce").notna()].copy()
    invest["EndDate"] = pd.to_datetime(invest["EndDate"])
    invest["year"] = invest["EndDate"].dt.year
    invest["Symbol"] = invest["Symbol"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    for col in ["AIInvestTotal", "AIInvestTotalValueAdd", "AIInvestLevel"]:
        invest[col] = pd.to_numeric(invest[col], errors="coerce")
    by_year = (
        invest.groupby(["Symbol", "year"], as_index=False)
        .agg(
            AIInvestTotal=("AIInvestTotal", "max"),
            AIInvestTotalValueAdd=("AIInvestTotalValueAdd", "max"),
            AIInvestLevel=("AIInvestLevel", "max"),
        )
    )
    by_year["HasAISupport"] = (by_year["AIInvestTotal"].fillna(0) > 0) | (
        by_year["AIInvestTotalValueAdd"].fillna(0) > 0
    )
    current = by_year[by_year["year"] == 2024].copy()
    current = current.rename(
        columns={
            "HasAISupport": "HasCurrentAISupport_2024",
            "AIInvestTotal": "AIInvestTotal_2024",
            "AIInvestTotalValueAdd": "AIInvestTotalValueAdd_2024",
            "AIInvestLevel": "AIInvestLevel_2024",
        }
    ).drop(columns=["year"])
    future = by_year[by_year["year"] == 2025].copy()
    future = future.rename(
        columns={
            "HasAISupport": "FutureAISupport_2025",
            "AIInvestTotal": "AIInvestTotal_2025",
            "AIInvestTotalValueAdd": "AIInvestTotalValueAdd_2025",
            "AIInvestLevel": "AIInvestLevel_2025",
        }
    ).drop(columns=["year"])
    return current.merge(future, on="Symbol", how="outer")


def decode_report_bytes(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gb18030", errors="ignore")


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", "", text)
    text = re.sub(r"\n+", "\n", text)
    return text


def split_sentences(text: str) -> list[str]:
    text = normalize_text(text)
    pieces = re.split(r"(?<=[。！？；;])|\n", text)
    out = []
    for piece in pieces:
        piece = piece.strip()
        if 18 <= len(piece) <= 280:
            out.append(piece)
    return out


def contains_any(sentence: str, terms: list[str]) -> bool:
    return any(term in sentence for term in terms)


def matched_terms(sentence: str, terms: list[str]) -> str:
    return ";".join([term for term in terms if term in sentence])


def specificity_score(sentence: str) -> tuple[int, dict[str, int]]:
    product_or_model = int(
        contains_any(sentence, ENTITY_TERMS)
        or bool(re.search(r"[\u4e00-\u9fa5A-Za-z0-9]{2,18}(?:大模型|模型|平台|系统|产品|助手|智能体)", sentence))
    )
    scenario = int(contains_any(sentence, SCENARIO_TERMS))
    timeline = int(bool(re.search(r"20[2-9][0-9]年|[一二三四1234]季度|Q[1-4]|年内|年底|未来[一二三四五\d]年|[一二三四五六七八九十\d]+月", sentence)))
    partner = int(contains_any(sentence, PARTNER_TERMS))
    subject = int(contains_any(sentence, SUBJECT_TERMS))
    features = {
        "specific_product_model_platform": product_or_model,
        "specific_business_scenario": scenario,
        "specific_timeline": timeline,
        "specific_partner": partner,
        "specific_subject": subject,
    }
    return sum(features.values()), features


def claim_type(sentence: str) -> str:
    if any(term in sentence for term in ["基础模型", "大模型", "大语言模型", "语言大模型", "LLM"]):
        return "foundation_model"
    if any(term in sentence for term in ["接入", "集成", "融合", "嵌入", "赋能"]):
        return "application_integration"
    if any(term in sentence for term in ["产品", "平台", "系统", "助手", "智能体", "知识库", "客服"]):
        return "specific_product_application"
    if any(term in sentence for term in ["内部", "办公", "研发", "生产", "运营", "财务", "供应链"]):
        return "internal_workflow"
    return "generic_or_unclear"


def parse_filename(name: str) -> tuple[str, str]:
    parts = Path(name).name.split("_")
    symbol = parts[0] if parts else ""
    short_name = ""
    if len(parts) >= 3 and re.fullmatch(r"20\d{2}", parts[1]):
        short_name = parts[2]
    elif len(parts) >= 2:
        short_name = parts[1]
    return symbol, short_name


def scan_2025_text_evidence() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int]]:
    if not TXT_DIR_2025.exists():
        raise FileNotFoundError(
            f"2025 annual-report TXT cache not found: {TXT_DIR_2025}. "
            "Extract 年报txt.rar into data/raw/annual_reports_2025_txt first."
        )

    firm_rows: list[dict[str, object]] = []
    type_rows: list[dict[str, object]] = []
    sentence_rows: list[dict[str, object]] = []
    total_docs = 0
    docs_with_genai = 0
    docs_with_text_evidence = 0

    for path in sorted(TXT_DIR_2025.rglob("*.txt")):
        total_docs += 1
        text = decode_report_bytes(path.read_bytes())
        symbol, short_name = parse_filename(path.name)
        has_genai = contains_any(text, GENAI_TERMS)
        if has_genai:
            docs_with_genai += 1

        type_counts: dict[str, int] = {}
        type_examples: dict[str, list[str]] = {}
        evidence_count = 0
        if has_genai:
            for idx, sent in enumerate(split_sentences(text)):
                if not contains_any(sent, GENAI_TERMS):
                    continue
                if not contains_any(sent, REALIZATION_TERMS):
                    continue
                ctype = claim_type(sent)
                evidence_count += 1
                type_counts[ctype] = type_counts.get(ctype, 0) + 1
                type_examples.setdefault(ctype, [])
                if len(type_examples[ctype]) < 3:
                    type_examples[ctype].append(sent)
                sentence_rows.append(
                    {
                        "Symbol": symbol,
                        "ShortName_from_filename": short_name,
                        "year": 2025,
                        "source_file": str(path.relative_to(TXT_DIR_2025.parent)),
                        "sentence_index_in_filtered_doc": idx,
                        "sentence": sent,
                        "matched_genai_terms": matched_terms(sent, GENAI_TERMS),
                        "matched_realization_terms": matched_terms(sent, REALIZATION_TERMS),
                        "claim_type": ctype,
                    }
                )

        if evidence_count:
            docs_with_text_evidence += 1

        firm_rows.append(
            {
                "Symbol": symbol,
                "FutureReportHasGenAI_2025": has_genai,
                "FutureReportTextEvidenceSentenceCount_2025": evidence_count,
                "FutureReportHasTextEvidence_2025": evidence_count > 0,
                "FutureReportEvidenceTypes_2025": ";".join(sorted(type_counts)),
            }
        )
        for ctype, count in type_counts.items():
            type_rows.append(
                {
                    "Symbol": symbol,
                    "claim_type": ctype,
                    "FutureTypeMatchedTextEvidence_2025": True,
                    "FutureTypeMatchedTextEvidenceSentenceCount_2025": count,
                    "FutureTypeMatchedTextEvidenceExamples_2025": " || ".join(type_examples.get(ctype, [])),
                }
            )

    firm_future = pd.DataFrame(firm_rows)
    if type_rows:
        type_future = pd.DataFrame(type_rows)
    else:
        type_future = pd.DataFrame(
            columns=[
                "Symbol",
                "claim_type",
                "FutureTypeMatchedTextEvidence_2025",
                "FutureTypeMatchedTextEvidenceSentenceCount_2025",
                "FutureTypeMatchedTextEvidenceExamples_2025",
            ]
        )
    sentence_future = pd.DataFrame(sentence_rows)
    stats = {
        "future_2025_total_docs": total_docs,
        "future_2025_docs_with_genai": docs_with_genai,
        "future_2025_docs_with_text_evidence": docs_with_text_evidence,
        "future_2025_text_evidence_sentences": len(sentence_rows),
    }
    return firm_future, type_future, sentence_future, stats


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)

    support = clean_investment()
    firm_future_text, type_future_text, future_sentence_evidence, future_stats = scan_2025_text_evidence()
    rows: list[dict[str, object]] = []
    docs_with_genai = 0
    docs_with_forward_candidates = 0
    total_docs = 0

    with ZipFile(TXT_ZIP) as zf:
        names = [name for name in zf.namelist() if name.lower().endswith(".txt")]
        total_docs = len(names)
        for name in names:
            text = decode_report_bytes(zf.read(name))
            if not contains_any(text, GENAI_TERMS):
                continue
            docs_with_genai += 1
            symbol, short_name = parse_filename(name)
            candidates_in_doc = 0
            for idx, sent in enumerate(split_sentences(text)):
                if not contains_any(sent, GENAI_TERMS):
                    continue
                is_forward = contains_any(sent, FORWARD_TERMS)
                if not is_forward:
                    continue
                score, features = specificity_score(sent)
                ctype = claim_type(sent)
                candidates_in_doc += 1
                rows.append(
                    {
                        "Symbol": symbol,
                        "ShortName_from_filename": short_name,
                        "year": 2024,
                        "source_file": name,
                        "sentence_index_in_filtered_doc": idx,
                        "sentence": sent,
                        "matched_genai_terms": matched_terms(sent, GENAI_TERMS),
                        "matched_forward_terms": matched_terms(sent, FORWARD_TERMS),
                        "claim_type": ctype,
                        "SpecificityScore": score,
                        "HighSpecificity": score >= 3,
                        **features,
                    }
                )
            if candidates_in_doc:
                docs_with_forward_candidates += 1

    claims = pd.DataFrame(rows)
    if claims.empty:
        raise RuntimeError("No GenAI forward-looking candidate sentences found.")

    claims = claims.merge(support, on="Symbol", how="left")
    claims = claims.merge(firm_future_text, on="Symbol", how="left")
    claims = claims.merge(type_future_text, on=["Symbol", "claim_type"], how="left")
    claims["HasCurrentAISupport_2024"] = claims["HasCurrentAISupport_2024"].fillna(False)
    claims["NoCurrentAISupport_2024"] = ~claims["HasCurrentAISupport_2024"].astype(bool)
    claims["FutureAISupport_2025_available"] = claims["FutureAISupport_2025"].notna()
    claims["FutureAISupport_2025"] = claims["FutureAISupport_2025"].fillna(False)
    claims["FutureReportHasGenAI_2025"] = claims["FutureReportHasGenAI_2025"].fillna(False)
    claims["FutureReportHasTextEvidence_2025"] = claims["FutureReportHasTextEvidence_2025"].fillna(False)
    claims["FutureTypeMatchedTextEvidence_2025"] = claims["FutureTypeMatchedTextEvidence_2025"].fillna(False)
    claims["FutureTypeMatchedTextEvidenceSentenceCount_2025"] = claims[
        "FutureTypeMatchedTextEvidenceSentenceCount_2025"
    ].fillna(0)
    claims["FutureAnyEvidence_2025"] = claims["FutureAISupport_2025"].astype(bool) | claims[
        "FutureTypeMatchedTextEvidence_2025"
    ].astype(bool)

    grid = (
        claims.groupby(["HighSpecificity", "NoCurrentAISupport_2024"], dropna=False)
        .agg(
            n_sentences=("sentence", "size"),
            n_firms=("Symbol", "nunique"),
            future_2025_invest_support_available=("FutureAISupport_2025_available", "mean"),
            future_2025_invest_support_rate=("FutureAISupport_2025", "mean"),
            future_2025_text_type_evidence_rate=("FutureTypeMatchedTextEvidence_2025", "mean"),
            future_2025_any_evidence_rate=("FutureAnyEvidence_2025", "mean"),
            mean_specificity=("SpecificityScore", "mean"),
        )
        .reset_index()
        .sort_values(["HighSpecificity", "NoCurrentAISupport_2024"])
    )

    by_type = (
        claims.groupby("claim_type")
        .agg(
            n_sentences=("sentence", "size"),
            n_firms=("Symbol", "nunique"),
            mean_specificity=("SpecificityScore", "mean"),
            high_specificity_share=("HighSpecificity", "mean"),
            no_current_support_share=("NoCurrentAISupport_2024", "mean"),
            future_text_type_evidence_rate=("FutureTypeMatchedTextEvidence_2025", "mean"),
            future_any_evidence_rate=("FutureAnyEvidence_2025", "mean"),
        )
        .reset_index()
        .sort_values("n_sentences", ascending=False)
    )

    top_examples = claims.sort_values(["SpecificityScore", "NoCurrentAISupport_2024"], ascending=[False, False]).head(80)

    claims.to_csv(OUT_DIR / "annual_report_genai_forward_candidates_2024.csv", index=False)
    grid.to_csv(OUT_DIR / "annual_report_genai_2x2_grid_2024.csv", index=False)
    by_type.to_csv(OUT_DIR / "annual_report_genai_by_claim_type_2024.csv", index=False)
    top_examples.to_csv(OUT_DIR / "annual_report_genai_top_examples_2024.csv", index=False)
    future_sentence_evidence.to_csv(OUT_DIR / "annual_report_future_text_evidence_sentences_2025.csv", index=False)
    type_future_text.to_csv(OUT_DIR / "annual_report_future_text_evidence_by_type_2025.csv", index=False)

    grid_md = grid.copy()
    for col in [
        "future_2025_invest_support_available",
        "future_2025_invest_support_rate",
        "future_2025_text_type_evidence_rate",
        "future_2025_any_evidence_rate",
        "mean_specificity",
    ]:
        grid_md[col] = grid_md[col].map(lambda v: "" if pd.isna(v) else f"{v:.4f}")
    by_type_md = by_type.copy()
    for col in [
        "mean_specificity",
        "high_specificity_share",
        "no_current_support_share",
        "future_text_type_evidence_rate",
        "future_any_evidence_rate",
    ]:
        by_type_md[col] = by_type_md[col].map(lambda v: "" if pd.isna(v) else f"{v:.4f}")

    core = claims[(claims["HighSpecificity"]) & (claims["NoCurrentAISupport_2024"])]

    report = f"""# v8.3 年报文本 pilot：GenAI forward-looking claim 抽取

**日期**：2026-05-17

## 1. 这次跑了什么

数据源：

```text
2024 年 A 股年报 TXT，共 {total_docs} 份：用于抽取 forward-looking GenAI claim
2025 年 A 股年报 TXT，共 {future_stats['future_2025_total_docs']} 份：用于扫描一年后的 textual realization clues
```

抽取规则：

```text
句子包含 GenAI-specific 关键词
且包含前瞻性动词 / 计划性动词
```

这比上一版 firm-year 粗 pilot 更接近 v8.3，但仍不是最终主实验。原因是：

```text
current support 仍用年度 AI 投资表近似
future realization 使用 2025 AI 投资表 + 2025 年报同 claim type 文本线索近似
还没有做 claim-type matched hard evidence
```

## 2. 抽取结果

```text
含 GenAI 关键词的年报数：{docs_with_genai}
含 forward-looking GenAI candidate 的年报数：{docs_with_forward_candidates}
candidate sentence 数：{len(claims)}
candidate firm 数：{claims['Symbol'].nunique()}
2025 年报含 GenAI 关键词公司数：{future_stats['future_2025_docs_with_genai']}
2025 年报含 GenAI 落地线索公司数：{future_stats['future_2025_docs_with_text_evidence']}
2025 年报 GenAI 落地线索句子数：{future_stats['future_2025_text_evidence_sentences']}
```

## 3. 粗 2x2

```text
HighSpecificity = SpecificityScore >= 3
NoCurrentAISupport_2024 = 2024 年 AI 投资表无支撑
FutureAISupport_2025 = 2025 年 AI 投资表有支撑
FutureTypeMatchedTextEvidence_2025 = 2025 年报中出现同公司、同 claim type 的 GenAI 落地线索
FutureAnyEvidence_2025 = FutureAISupport_2025 或 FutureTypeMatchedTextEvidence_2025
```

{grid_md.to_markdown(index=False)}

核心格：

```text
HighSpecificity = 1 且 NoCurrentAISupport_2024 = 1
```

样本量：

```text
{len(core)} sentences
{core['Symbol'].nunique()} firms
```

## 4. Claim type 分布

{by_type_md.to_markdown(index=False)}

## 5. 输出文件

```text
{OUT_DIR / "annual_report_genai_forward_candidates_2024.csv"}
{OUT_DIR / "annual_report_genai_2x2_grid_2024.csv"}
{OUT_DIR / "annual_report_genai_by_claim_type_2024.csv"}
{OUT_DIR / "annual_report_genai_top_examples_2024.csv"}
{OUT_DIR / "annual_report_future_text_evidence_sentences_2025.csv"}
{OUT_DIR / "annual_report_future_text_evidence_by_type_2025.csv"}
```

## 6. 硬判断

这个 pilot 支持继续推进 v8.3 的原因：

```text
1. 2024 年报中能抽到 GenAI-specific forward-looking candidate
2. 能形成 HighSpecificity × NoCurrentSupport 的核心格
3. 可以做人工复核样本，检查 specificity rubric 是否可用
```

它还不能证明主效应，原因：

```text
1. 年报句子不是所有 GenAI claim 来源，只覆盖 formal annual report
2. current support 目前是 broad AI investment，不是 GenAI claim-type matched support
3. future realization 目前是 2025 broad AI investment support + 2025 annual-report textual clues，不是 matched hard evidence
4. 句子抽取仍是规则法，需要人工标注 valid / weak / invalid
```

下一步应该人工复核：

```text
{OUT_DIR / "annual_report_genai_top_examples_2024.csv"}
```

重点看三件事：

```text
句子是否真的是 GenAI-specific
句子是否真的是 forward-looking claim
SpecificityScore >= 3 是否符合人类直觉
```
"""

    DOC_OUT.write_text(report, encoding="utf-8")

    print(f"total_docs={total_docs}")
    print(f"docs_with_genai={docs_with_genai}")
    print(f"docs_with_forward_candidates={docs_with_forward_candidates}")
    print(f"candidate_sentences={len(claims)}")
    print(f"candidate_firms={claims['Symbol'].nunique()}")
    print(f"core_cell_sentences={len(core)}")
    print(f"core_cell_firms={core['Symbol'].nunique()}")
    print(f"future_2025_total_docs={future_stats['future_2025_total_docs']}")
    print(f"future_2025_docs_with_genai={future_stats['future_2025_docs_with_genai']}")
    print(f"future_2025_docs_with_text_evidence={future_stats['future_2025_docs_with_text_evidence']}")
    print(f"future_2025_text_evidence_sentences={future_stats['future_2025_text_evidence_sentences']}")
    print(f"wrote={OUT_DIR}")
    print(f"report={DOC_OUT}")


if __name__ == "__main__":
    main()
