#!/usr/bin/env python3
"""Link v8.3 annual-report GenAI claims to IR and interactive-QA evidence.

This is a feasibility pilot. It checks whether the 2024 annual-report claim
sample can be connected to later public evidence from investor-relation records
and exchange interactive Q&A.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v8_3_external_evidence_link_pilot"
DOC_OUT = ROOT / "docs" / "选题" / "15_v8_3_external_evidence_link_pilot_20260519.md"

CLAIM_CSV = ROOT / "results" / "v8_3_claim_text_pilot" / "annual_report_genai_forward_candidates_2024.csv"
IR_ROOT = Path(
    "/Users/mac/computerscience/第三方资料/04_项目专用资料/T05_GAI_financial_disclosure_market_reaction/ir_interaction_data_20260519"
)
INTERACTIVE_CSV = IR_ROOT / "interactive_platforms" / "interim" / "genai_interactive_qa_answered_combined_2023_2026.csv"
IR_MATCH_CSV = IR_ROOT / "cninfo_ir_activity" / "interim" / "cninfo_ir_activity_full_genai_matches_2023_2026.csv"
IR_SNIPPET_CSV = IR_ROOT / "cninfo_ir_activity" / "interim" / "cninfo_ir_activity_full_genai_sentence_snippets_2023_2026.csv"


def z6(s: object) -> str:
    return re.sub(r"\.0$", "", str(s)).strip().zfill(6)


def bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def pct(x: object) -> str:
    if pd.isna(x):
        return ""
    return f"{100 * float(x):.2f}%"


def parse_report_date(source_file: str) -> pd.Timestamp:
    m = re.search(r"_(20\d{2}-\d{2}-\d{2})\.txt$", str(source_file))
    if not m:
        return pd.NaT
    return pd.to_datetime(m.group(1), errors="coerce")


def load_claims() -> pd.DataFrame:
    claims = pd.read_csv(CLAIM_CSV)
    claims["Symbol"] = claims["Symbol"].map(z6)
    claims["report_disclosure_date"] = claims["source_file"].map(parse_report_date)
    for col in [
        "HighSpecificity",
        "HasCurrentAISupport_2024",
        "NoCurrentAISupport_2024",
        "FutureTypeMatchedTextEvidence_2025",
        "FutureAnyEvidence_2025",
        "FutureReportHasTextEvidence_2025",
    ]:
        if col in claims.columns:
            claims[col] = bool_series(claims[col])
    return claims


def load_public_events() -> tuple[pd.DataFrame, pd.DataFrame]:
    qa = pd.read_csv(INTERACTIVE_CSV)
    qa["Symbol"] = qa["stock_code"].map(z6)
    qa["event_date_dt"] = pd.to_datetime(qa["event_date"], errors="coerce")
    qa["event_source"] = "interactive_qa_answer"
    qa["event_text"] = (qa["question_text"].fillna("") + " " + qa["answer_text"].fillna("")).str.slice(0, 1000)
    qa = qa[
        [
            "Symbol",
            "company_name",
            "event_date_dt",
            "event_source",
            "query_terms",
            "event_text",
            "source_url",
        ]
    ].rename(columns={"company_name": "company_or_short_name", "query_terms": "matched_terms"})

    ir = pd.read_csv(IR_MATCH_CSV)
    ir["Symbol"] = ir["sec_code"].map(z6)
    ir["event_date_dt"] = pd.to_datetime(ir["announcement_date"], errors="coerce")
    ir["event_source"] = "cninfo_ir_activity"
    ir["event_text"] = ir["announcement_title"].fillna("")
    ir = ir[
        [
            "Symbol",
            "sec_name",
            "event_date_dt",
            "event_source",
            "matched_terms",
            "event_text",
            "pdf_url",
        ]
    ].rename(columns={"sec_name": "company_or_short_name", "pdf_url": "source_url"})

    events = pd.concat([qa, ir], ignore_index=True)
    events = events[events["event_date_dt"].notna()].copy()
    events["event_date"] = events["event_date_dt"].dt.strftime("%Y-%m-%d")
    return events, qa


def event_counts_for_claims(claims: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    symbols = claims[["Symbol", "report_disclosure_date"]].drop_duplicates()
    merged = symbols.merge(events, on="Symbol", how="left")
    merged["is_prior_or_current"] = merged["event_date_dt"].notna() & (
        merged["event_date_dt"] <= merged["report_disclosure_date"]
    )
    merged["is_future"] = merged["event_date_dt"].notna() & (
        merged["event_date_dt"] > merged["report_disclosure_date"]
    )

    counts = (
        merged.groupby(["Symbol", "report_disclosure_date"], as_index=False)
        .agg(
            prior_public_irqa_events=("is_prior_or_current", "sum"),
            future_public_irqa_events=("is_future", "sum"),
            first_future_public_irqa_date=(
                "event_date_dt",
                lambda x: x[merged.loc[x.index, "is_future"]].min(),
            ),
        )
    )
    counts["HasPriorPublicIRQAEvidence"] = counts["prior_public_irqa_events"] > 0
    counts["FuturePublicIRQAEvidence"] = counts["future_public_irqa_events"] > 0
    counts["first_future_public_irqa_date"] = counts["first_future_public_irqa_date"].dt.strftime("%Y-%m-%d")
    return counts


def make_grids(claims_linked: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    claims_linked["NoPriorPublicEvidence_Strict"] = claims_linked["NoCurrentAISupport_2024"] & (
        ~claims_linked["HasPriorPublicIRQAEvidence"]
    )
    claims_linked["FutureAnyPublicEvidence_Extended"] = claims_linked["FutureTypeMatchedTextEvidence_2025"] | claims_linked[
        "FuturePublicIRQAEvidence"
    ]

    sentence_grid = (
        claims_linked.groupby(["HighSpecificity", "NoPriorPublicEvidence_Strict"], dropna=False)
        .agg(
            n_sentences=("Symbol", "size"),
            n_firms=("Symbol", "nunique"),
            future_type_matched_ar_rate=("FutureTypeMatchedTextEvidence_2025", "mean"),
            future_irqa_rate=("FuturePublicIRQAEvidence", "mean"),
            future_any_public_rate=("FutureAnyPublicEvidence_Extended", "mean"),
            mean_prior_irqa_events=("prior_public_irqa_events", "mean"),
            mean_future_irqa_events=("future_public_irqa_events", "mean"),
            mean_specificity=("SpecificityScore", "mean"),
        )
        .reset_index()
        .sort_values(["HighSpecificity", "NoPriorPublicEvidence_Strict"])
    )

    firm_panel = (
        claims_linked.groupby(["Symbol", "ShortName_from_filename", "report_disclosure_date"], as_index=False)
        .agg(
            n_claim_sentences=("sentence", "size"),
            n_high_specificity_sentences=("HighSpecificity", "sum"),
            HasHighSpecificityClaim=("HighSpecificity", "max"),
            NoCurrentAISupport_2024=("NoCurrentAISupport_2024", "max"),
            HasPriorPublicIRQAEvidence=("HasPriorPublicIRQAEvidence", "max"),
            NoPriorPublicEvidence_Strict=("NoPriorPublicEvidence_Strict", "max"),
            FutureTypeMatchedTextEvidence_2025=("FutureTypeMatchedTextEvidence_2025", "max"),
            FuturePublicIRQAEvidence=("FuturePublicIRQAEvidence", "max"),
            FutureAnyPublicEvidence_Extended=("FutureAnyPublicEvidence_Extended", "max"),
            prior_public_irqa_events=("prior_public_irqa_events", "max"),
            future_public_irqa_events=("future_public_irqa_events", "max"),
            first_future_public_irqa_date=("first_future_public_irqa_date", "first"),
            max_specificity=("SpecificityScore", "max"),
        )
    )
    firm_grid = (
        firm_panel.groupby(["HasHighSpecificityClaim", "NoPriorPublicEvidence_Strict"], dropna=False)
        .agg(
            n_firms=("Symbol", "nunique"),
            mean_claim_sentences=("n_claim_sentences", "mean"),
            future_type_matched_ar_rate=("FutureTypeMatchedTextEvidence_2025", "mean"),
            future_irqa_rate=("FuturePublicIRQAEvidence", "mean"),
            future_any_public_rate=("FutureAnyPublicEvidence_Extended", "mean"),
            mean_prior_irqa_events=("prior_public_irqa_events", "mean"),
            mean_future_irqa_events=("future_public_irqa_events", "mean"),
        )
        .reset_index()
        .sort_values(["HasHighSpecificityClaim", "NoPriorPublicEvidence_Strict"])
    )
    return sentence_grid, firm_panel, firm_grid


def run_simple_lpm(firm_panel: pd.DataFrame) -> pd.DataFrame:
    def lpm_numpy(data: pd.DataFrame, y_col: str, model_name: str) -> list[dict[str, object]]:
        import math
        import numpy as np

        a = data["HasHighSpecificityClaim"].astype(float).to_numpy()
        b = data["NoPriorPublicEvidence_Strict"].astype(float).to_numpy()
        y = data[y_col].astype(float).to_numpy()
        x = np.column_stack([np.ones(len(data)), a, b, a * b])
        terms = ["Intercept", "HasHighSpecificityClaim", "NoPriorPublicEvidence_Strict", "Interaction"]
        beta = np.linalg.lstsq(x, y, rcond=None)[0]
        resid = y - x @ beta
        n, k = x.shape
        sigma2 = float((resid @ resid) / max(n - k, 1))
        vcov = sigma2 * np.linalg.pinv(x.T @ x)
        se = np.sqrt(np.diag(vcov))
        tvals = beta / se
        ybar = y.mean()
        sst = float(((y - ybar) @ (y - ybar)))
        r2 = 1 - float((resid @ resid) / sst) if sst else 0.0
        rows = []
        for term, coef, stderr, tval in zip(terms, beta, se, tvals):
            p = math.erfc(abs(float(tval)) / math.sqrt(2))
            rows.append(
                {
                    "model": model_name,
                    "term": term,
                    "coef": float(coef),
                    "std_err": float(stderr),
                    "p_value": float(p),
                    "nobs": int(n),
                    "r2": float(r2),
                    "note": "numpy OLS, classical SE, no controls",
                }
            )
        return rows

    data = firm_panel.copy()
    for col in [
        "HasHighSpecificityClaim",
        "NoPriorPublicEvidence_Strict",
        "FutureAnyPublicEvidence_Extended",
        "FuturePublicIRQAEvidence",
        "FutureTypeMatchedTextEvidence_2025",
    ]:
        data[col] = data[col].astype(int)

    try:
        import statsmodels.formula.api as smf
    except Exception:
        rows = []
        rows.extend(lpm_numpy(data, "FutureAnyPublicEvidence_Extended", "Y_any_public_evidence"))
        rows.extend(lpm_numpy(data, "FuturePublicIRQAEvidence", "Y_future_irqa"))
        rows.extend(lpm_numpy(data, "FutureTypeMatchedTextEvidence_2025", "Y_2025_ar_type_matched"))
        return pd.DataFrame(rows)

    models = {
        "Y_any_public_evidence": "FutureAnyPublicEvidence_Extended ~ HasHighSpecificityClaim * NoPriorPublicEvidence_Strict",
        "Y_future_irqa": "FuturePublicIRQAEvidence ~ HasHighSpecificityClaim * NoPriorPublicEvidence_Strict",
        "Y_2025_ar_type_matched": "FutureTypeMatchedTextEvidence_2025 ~ HasHighSpecificityClaim * NoPriorPublicEvidence_Strict",
    }
    rows = []
    for name, formula in models.items():
        fit = smf.ols(formula, data=data).fit(cov_type="HC1")
        for term in fit.params.index:
            rows.append(
                {
                    "model": name,
                    "term": term,
                    "coef": fit.params[term],
                    "std_err": fit.bse[term],
                    "p_value": fit.pvalues[term],
                    "nobs": int(fit.nobs),
                    "r2": fit.rsquared,
                }
            )
    return pd.DataFrame(rows)


def sample_event_examples(firm_panel: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    core = firm_panel[
        firm_panel["HasHighSpecificityClaim"] & firm_panel["NoPriorPublicEvidence_Strict"] & firm_panel["FuturePublicIRQAEvidence"]
    ][["Symbol", "ShortName_from_filename", "report_disclosure_date"]].drop_duplicates()
    if core.empty:
        return pd.DataFrame()
    examples = core.merge(events, on="Symbol", how="left")
    examples = examples[examples["event_date_dt"] > examples["report_disclosure_date"]].copy()
    return (
        examples.sort_values(["Symbol", "event_date_dt"])
        .groupby("Symbol", as_index=False)
        .head(3)
        [
            [
                "Symbol",
                "ShortName_from_filename",
                "report_disclosure_date",
                "event_date",
                "event_source",
                "matched_terms",
                "event_text",
                "source_url",
            ]
        ]
    )


def write_report(
    claims_linked: pd.DataFrame,
    sentence_grid: pd.DataFrame,
    firm_panel: pd.DataFrame,
    firm_grid: pd.DataFrame,
    lpm: pd.DataFrame,
    examples: pd.DataFrame,
) -> None:
    def to_md(df: pd.DataFrame, max_rows: int | None = None) -> str:
        if df.empty:
            return "无"
        show = df if max_rows is None else df.head(max_rows)
        cols = list(show.columns)
        lines = [
            "| " + " | ".join(cols) + " |",
            "| " + " | ".join(["---"] * len(cols)) + " |",
        ]
        for _, row in show.iterrows():
            vals = [str(row.get(col, "")).replace("\n", " ").replace("|", "\\|") for col in cols]
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    sentence_md = sentence_grid.copy()
    firm_grid_md = firm_grid.copy()
    for df in [sentence_md, firm_grid_md]:
        for col in [
            "future_type_matched_ar_rate",
            "future_irqa_rate",
            "future_any_public_rate",
            "mean_prior_irqa_events",
            "mean_future_irqa_events",
            "mean_specificity",
            "mean_claim_sentences",
        ]:
            if col in df.columns:
                df[col] = df[col].map(lambda v: "" if pd.isna(v) else f"{float(v):.4f}")

    lpm_md = lpm.copy()
    for col in ["coef", "std_err", "p_value", "r2"]:
        if col in lpm_md.columns:
            lpm_md[col] = lpm_md[col].map(lambda v: "" if pd.isna(v) else f"{float(v):.4f}")

    core_firms = firm_panel[firm_panel["HasHighSpecificityClaim"] & firm_panel["NoPriorPublicEvidence_Strict"]]
    core_sentences = claims_linked[claims_linked["HighSpecificity"] & claims_linked["NoPriorPublicEvidence_Strict"]]
    report = f"""# v8.3 外部证据连接试跑

日期：2026-05-19

## 1. 目的

这次不是正式回归，而是检查当前数据能否支持一个更硬的测度闭环：

```text
2024 年报 GenAI 前瞻性声明
    -> 年报披露日前是否已有公开支撑
    -> 年报披露日后是否出现 IR / 互动问答 / 下一年年报证据
```

这里的外部公开证据来自两类渠道：

- 巨潮投资者关系活动记录表。
- 上证 e 互动与深交所互动易的公司回复。

## 2. 当前变量口径

```text
HasPriorPublicIRQAEvidence
    = 同一股票代码在 2024 年报披露日前，已有 GenAI 相关 IR 或互动问答公司回复。

NoPriorPublicEvidence_Strict
    = NoCurrentAISupport_2024 = 1 且 HasPriorPublicIRQAEvidence = 0。

FuturePublicIRQAEvidence
    = 同一股票代码在 2024 年报披露日后，出现 GenAI 相关 IR 或互动问答公司回复。

FutureAnyPublicEvidence_Extended
    = FutureTypeMatchedTextEvidence_2025 = 1 或 FuturePublicIRQAEvidence = 1。
```

注意：`NoCurrentAISupport_2024` 仍来自现有 AI 投资支撑表；IR/互动问答只是在“公开可核验支撑”上补一层。

## 3. 样本概况

- 年报 GenAI 前瞻性声明句子：{len(claims_linked)}
- 涉及公司：{claims_linked['Symbol'].nunique()}
- 有高具体性声明的公司：{int(firm_panel['HasHighSpecificityClaim'].sum())}
- 严格无先验公开支撑且有高具体性声明的公司：{len(core_firms)}
- 严格无先验公开支撑且高具体性声明句子：{len(core_sentences)}
- 这些核心公司中，后续出现任一公开证据的比例：{pct(core_firms['FutureAnyPublicEvidence_Extended'].mean())}
- 这些核心公司中，后续出现 IR/互动问答证据的比例：{pct(core_firms['FuturePublicIRQAEvidence'].mean())}

## 4. 句子层 2x2

{to_md(sentence_md)}

## 5. 公司层 2x2

{to_md(firm_grid_md)}

## 6. 极简 LPM

只用于看方向，不含行业、规模、公司基本面、固定效应，不作为正式结果。

{to_md(lpm_md)}

## 7. 核心格后续公开证据示例

样例文件：

`results/v8_3_external_evidence_link_pilot/core_cell_future_public_evidence_examples.csv`

前 10 条：

{to_md(examples, max_rows=10)}

## 8. 初步判断

可以继续跑，但目前适合定位为“测度闭环与样本量试验”，还不能直接当正式实证。

更稳的下一步是：

1. 对 `NoPriorPublicEvidence_Strict` 核心格抽样人工复核，确认年报句子是不是具体 GenAI 能力声明。
2. 对 `FuturePublicIRQAEvidence` 句子做类型匹配，不要只按同公司同关键词算兑现。
3. 将专利、招聘、CAC 的公司映射补上后，再把 outcome 从“文本证据”升级为更硬的行动证据。
"""
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    claims = load_claims()
    events, _qa = load_public_events()
    counts = event_counts_for_claims(claims, events)
    linked = claims.merge(counts, on=["Symbol", "report_disclosure_date"], how="left")
    for col in ["prior_public_irqa_events", "future_public_irqa_events"]:
        linked[col] = linked[col].fillna(0).astype(int)
    for col in ["HasPriorPublicIRQAEvidence", "FuturePublicIRQAEvidence"]:
        linked[col] = linked[col].fillna(False).astype(bool)
    linked["first_future_public_irqa_date"] = linked["first_future_public_irqa_date"].fillna("")

    sentence_grid, firm_panel, firm_grid = make_grids(linked)
    lpm = run_simple_lpm(firm_panel)
    examples = sample_event_examples(firm_panel, events)
    core_firms = firm_panel[firm_panel["HasHighSpecificityClaim"] & firm_panel["NoPriorPublicEvidence_Strict"]].copy()
    core_claims = linked[linked["HighSpecificity"] & linked["NoPriorPublicEvidence_Strict"]].copy()

    linked.to_csv(OUT_DIR / "claim_external_evidence_panel_2024.csv", index=False)
    firm_panel.to_csv(OUT_DIR / "firm_external_evidence_panel_2024.csv", index=False)
    core_firms.to_csv(OUT_DIR / "core_cell_firms_2024.csv", index=False)
    core_claims.to_csv(OUT_DIR / "core_cell_claim_sentences_2024.csv", index=False)
    sentence_grid.to_csv(OUT_DIR / "sentence_external_evidence_2x2_grid_2024.csv", index=False)
    firm_grid.to_csv(OUT_DIR / "firm_external_evidence_2x2_grid_2024.csv", index=False)
    lpm.to_csv(OUT_DIR / "firm_level_simple_lpm.csv", index=False)
    examples.to_csv(OUT_DIR / "core_cell_future_public_evidence_examples.csv", index=False)
    events.to_csv(OUT_DIR / "public_irqa_events_for_linking.csv", index=False)
    write_report(linked, sentence_grid, firm_panel, firm_grid, lpm, examples)

    print(f"claim_rows={len(linked)} firms={linked['Symbol'].nunique()}")
    print(f"firm_rows={len(firm_panel)} core_firms={len(firm_panel[firm_panel['HasHighSpecificityClaim'] & firm_panel['NoPriorPublicEvidence_Strict']])}")
    print(f"doc={DOC_OUT}")


if __name__ == "__main__":
    main()
