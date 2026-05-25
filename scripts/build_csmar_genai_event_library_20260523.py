#!/usr/bin/env python3
"""Build a CSMAR-based GenAI disclosure event library.

This script uses the CSMAR downloads archived on 2026-05-23:
- CMS_InvestorInteraction: exchange investor-interaction Q&A.
- IRM_MEETINGMINUTES: investor-relation meeting Q&A minutes.

Strict disclosure events require the company's answer/reply text itself to
contain GenAI terms. Investor questions are retained as context but not treated
as firm disclosure.
"""

from __future__ import annotations

import re
import zipfile
from collections.abc import Iterable
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(
    "/Users/mac/computerscience/第三方资料/04_项目专用资料/"
    "T05_GAI_financial_disclosure_market_reaction/csmar_downloads_20260523"
)
OUT_DIR = ROOT / "results" / "csmar_genai_event_library_20260523"
DOC_OUT = ROOT / "docs" / "empirical_runs" / "38_csmar_genai_event_library_smoke_20260523.md"

IIP_ZIP = DATA_DIR / "CMS_InvestorInteraction_20210523_20260522_CSV_2460998rows.zip"
IRQA_ZIP = DATA_DIR / "IRM_QAMinutes_20110422_20260521_CSV_1774601rows.zip"
BASIC_ZIP = DATA_DIR / "IRM_BasicInfo_20120709_20260521_CSV_195525rows.zip"

A_SHARE_PAT = re.compile(r"^(000|001|002|003|300|301|600|601|603|605|688)\d{3}$")

GENAI_TERMS = [
    "生成式人工智能",
    "生成式AI",
    "生成式 AI",
    "GenAI",
    "AIGC",
    "ChatGPT",
    "DeepSeek",
    "大模型",
    "AI大模型",
    "人工智能大模型",
    "大语言模型",
    "语言大模型",
    "基础模型",
    "预训练模型",
    "多模态大模型",
    "多模态",
    "文生图",
    "文生视频",
    "Sora",
    "GPT",
    "Kimi",
    "通义千问",
    "通义",
    "文心一言",
    "讯飞星火",
    "星火大模型",
    "智谱",
    "豆包",
    "盘古大模型",
    "混元大模型",
    "百川大模型",
    "商汤日日新",
    "日日新大模型",
    "RAG",
    "Agent",
    "智能体",
    "模型备案",
    "MaaS",
]
GENAI_PAT = re.compile("|".join(re.escape(t) for t in sorted(GENAI_TERMS, key=len, reverse=True)), re.I)


def z6(x: object) -> str:
    s = re.sub(r"\.0$", "", str(x or "")).strip()
    return s.zfill(6) if s else ""


def clean_text(x: object) -> str:
    return re.sub(r"\s+", " ", str(x or "")).strip()


def is_a_share(code: object) -> bool:
    return bool(A_SHARE_PAT.match(z6(code)))


def hit_terms(text: object) -> str:
    s = clean_text(text)
    hits = [t for t in GENAI_TERMS if re.search(re.escape(t), s, re.I)]
    return ";".join(sorted(set(hits)))


def has_genai(text: object) -> bool:
    return bool(GENAI_PAT.search(clean_text(text)))


def split_sentences(text: object) -> list[str]:
    s = clean_text(text)
    parts = re.split(r"(?<=[。！？；;])", s)
    return [p.strip() for p in parts if len(p.strip()) >= 6]


def genai_span(text: object) -> str:
    parts = [s for s in split_sentences(text) if has_genai(s)]
    return " ".join(parts)[:6000]


def specificity_metrics(text: object) -> dict[str, float | int]:
    span = genai_span(text)
    compact = re.sub(r"\s+", "", span)
    token_count = max(1, len(re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9]+", compact)))
    patterns = {
        "dates": r"(?:20[2-9]\d年\d{0,2}月?\d{0,2}日?|20[2-9]\d[-/]\d{1,2}[-/]\d{1,2}|[一二三四1234]季度|Q[1-4])",
        "money": r"\d+(?:\.\d+)?(?:亿元|万元|元|万美元|美元|人民币)",
        "percent": r"\d+(?:\.\d+)?%",
        "numbers": r"\d+(?:\.\d+)?(?:个|项|款|台|套|人|家|年|月|日|亿|万)?",
        "quoted_names": r"[“《][^”》]{2,40}[”》]",
        "orgs": r"[\u4e00-\u9fa5A-Za-z0-9]{2,35}(?:公司|集团|大学|研究院|实验室|中心|平台|科技|智能|网络|银行)",
        "partners": r"(?:华为|百度|阿里|腾讯|科大讯飞|智谱|商汤|字节|DeepSeek|OpenAI|微软|英伟达|通义|文心|Kimi|月之暗面|百川|MiniMax)",
        "stage": r"(?:已上线|已发布|已备案|已通过|已落地|已部署|已接入|签署|合作|共建|推出|发布|升级|备案通过|内测|公测)",
    }
    counts = {k: len(re.findall(pat, compact, flags=re.I)) for k, pat in patterns.items()}
    specific_items = int(sum(counts.values()))
    return {
        **counts,
        "specific_items": specific_items,
        "genai_span_tokens": int(token_count),
        "specificity": 100 * specific_items / token_count,
        "genai_mentions": int(sum(compact.lower().count(t.lower()) for t in GENAI_TERMS)),
    }


def csv_members(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path) as zf:
        return [info.filename for info in zf.infolist() if info.filename.lower().endswith(".csv")]


def read_csv_chunks(zip_path: Path, members: Iterable[str], chunksize: int = 100_000) -> Iterable[pd.DataFrame]:
    with zipfile.ZipFile(zip_path) as zf:
        for member in members:
            with zf.open(member) as fh:
                for chunk in pd.read_csv(
                    fh,
                    dtype=str,
                    chunksize=chunksize,
                    encoding="utf-8-sig",
                    keep_default_na=False,
                    low_memory=False,
                    on_bad_lines="skip",
                ):
                    chunk["_zip_member"] = member
                    yield chunk


def aggregate_terms(values: pd.Series) -> str:
    out: set[str] = set()
    for v in values.dropna().astype(str):
        for item in re.split(r"[;,；]", v):
            item = item.strip()
            if item:
                out.add(item)
    return ";".join(sorted(out))


def first_nonempty(values: pd.Series) -> str:
    for v in values.astype(str):
        v = clean_text(v)
        if v:
            return v
    return ""


def load_basic_info() -> pd.DataFrame:
    if not BASIC_ZIP.exists():
        return pd.DataFrame(columns=["ReportID", "DeclareDate", "Title", "FileType", "FileSize"])
    member = csv_members(BASIC_ZIP)[0]
    with zipfile.ZipFile(BASIC_ZIP) as zf, zf.open(member) as fh:
        out = pd.read_csv(fh, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    keep = [c for c in ["ReportID", "DeclareDate", "Title", "FileType", "FileSize"] if c in out.columns]
    return out[keep].drop_duplicates("ReportID")


def build_iip_events() -> tuple[pd.DataFrame, dict[str, int]]:
    rows = []
    stats = {"rows_read": 0, "a_share_rows": 0, "answer_genai_rows": 0, "question_only_rows": 0}
    for chunk in read_csv_chunks(IIP_ZIP, csv_members(IIP_ZIP)):
        stats["rows_read"] += len(chunk)
        chunk["Symbol"] = chunk["Symbol"].map(z6)
        chunk = chunk[chunk["Symbol"].map(is_a_share)].copy()
        stats["a_share_rows"] += len(chunk)
        if chunk.empty:
            continue
        chunk["ReplyContent"] = chunk.get("ReplyContent", "").map(clean_text)
        chunk["QuestionContent"] = chunk.get("QuestionContent", "").map(clean_text)
        chunk["answer_has_genai"] = chunk["ReplyContent"].map(has_genai)
        chunk["question_has_genai"] = chunk["QuestionContent"].map(has_genai)
        strict = chunk[chunk["answer_has_genai"]].copy()
        stats["answer_genai_rows"] += len(strict)
        stats["question_only_rows"] += int(((~chunk["answer_has_genai"]) & chunk["question_has_genai"]).sum())
        if strict.empty:
            continue
        strict["event_source"] = "csmar_investor_interaction"
        strict["source_id"] = strict["Symbol"] + "_" + strict["Rank"].astype(str) + "_" + strict["QuestionDate"].astype(str)
        strict["stock_code"] = strict["Symbol"]
        strict["company_name"] = strict.get("ShortName", "")
        strict["event_date"] = pd.to_datetime(strict.get("ReplyDate", ""), errors="coerce")
        strict["question_date"] = pd.to_datetime(strict.get("QuestionDate", ""), errors="coerce")
        strict["answer_text"] = strict["ReplyContent"]
        strict["question_text"] = strict["QuestionContent"]
        strict["answer_terms"] = strict["answer_text"].map(hit_terms)
        strict["question_terms"] = strict["question_text"].map(hit_terms)
        strict["genai_span"] = strict["answer_text"].map(genai_span)
        metrics = pd.DataFrame([specificity_metrics(v) for v in strict["answer_text"]], index=strict.index)
        strict = pd.concat([strict, metrics], axis=1)
        keep = [
            "event_source",
            "source_id",
            "stock_code",
            "company_name",
            "event_date",
            "question_date",
            "answer_terms",
            "question_terms",
            "specificity",
            "specific_items",
            "genai_span_tokens",
            "genai_mentions",
            "question_text",
            "answer_text",
            "QuestionContent",
            "ReplyContent",
            "genai_span",
            "ProblemSource",
            "_zip_member",
        ]
        rows.append(strict[[c for c in keep if c in strict.columns]])
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    return out, stats


def build_irqa_events() -> tuple[pd.DataFrame, dict[str, int]]:
    basic = load_basic_info()
    rows = []
    stats = {"rows_read": 0, "a_share_rows": 0, "answer_genai_rows": 0, "question_only_rows": 0}
    for chunk in read_csv_chunks(IRQA_ZIP, csv_members(IRQA_ZIP)):
        stats["rows_read"] += len(chunk)
        chunk["Symbol"] = chunk["Symbol"].map(z6)
        chunk = chunk[chunk["Symbol"].map(is_a_share)].copy()
        stats["a_share_rows"] += len(chunk)
        if chunk.empty:
            continue
        chunk["Answer"] = chunk.get("Answer", "").map(clean_text)
        chunk["Question"] = chunk.get("Question", "").map(clean_text)
        chunk["answer_has_genai"] = chunk["Answer"].map(has_genai)
        chunk["question_has_genai"] = chunk["Question"].map(has_genai)
        strict = chunk[chunk["answer_has_genai"]].copy()
        stats["answer_genai_rows"] += len(strict)
        stats["question_only_rows"] += int(((~chunk["answer_has_genai"]) & chunk["question_has_genai"]).sum())
        if strict.empty:
            continue
        strict["event_source"] = "csmar_ir_meeting_qa"
        strict["source_id"] = strict["ReportID"].astype(str) + "_" + strict["Rank"].astype(str)
        strict["stock_code"] = strict["Symbol"]
        strict["event_date"] = pd.to_datetime(strict.get("ReportDate", ""), errors="coerce")
        strict["answer_text"] = strict["Answer"]
        strict["question_text"] = strict["Question"]
        strict["answer_terms"] = strict["answer_text"].map(hit_terms)
        strict["question_terms"] = strict["question_text"].map(hit_terms)
        strict["genai_span"] = strict["answer_text"].map(genai_span)
        metrics = pd.DataFrame([specificity_metrics(v) for v in strict["answer_text"]], index=strict.index)
        strict = pd.concat([strict, metrics], axis=1)
        if not basic.empty:
            strict = strict.merge(basic, on="ReportID", how="left")
        keep = [
            "event_source",
            "source_id",
            "ReportID",
            "stock_code",
            "event_date",
            "DeclareDate",
            "Title",
            "answer_terms",
            "question_terms",
            "specificity",
            "specific_items",
            "genai_span_tokens",
            "genai_mentions",
            "question_text",
            "answer_text",
            "Question",
            "Answer",
            "genai_span",
            "_zip_member",
        ]
        rows.append(strict[[c for c in keep if c in strict.columns]])
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    return out, stats


def firm_day(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()
    d = events.copy()
    d["event_date"] = pd.to_datetime(d["event_date"], errors="coerce")
    d = d[d["event_date"].notna()].copy()
    d["event_date_str"] = d["event_date"].dt.strftime("%Y-%m-%d")
    if "company_name" not in d.columns:
        d["company_name"] = ""
    group = d.groupby(["event_source", "stock_code", "event_date_str"], as_index=False)
    out = group.agg(
        answer_level_events=("source_id", "nunique"),
        company_name=("company_name", first_nonempty),
        answer_terms=("answer_terms", aggregate_terms),
        question_terms=("question_terms", aggregate_terms),
        mean_specificity=("specificity", "mean"),
        max_specificity=("specificity", "max"),
        total_specific_items=("specific_items", "sum"),
        total_genai_span_tokens=("genai_span_tokens", "sum"),
        total_genai_mentions=("genai_mentions", "sum"),
        sample_answer=("answer_text", lambda x: " || ".join(clean_text(v)[:260] for v in x.head(3))),
        sample_question=("question_text", lambda x: " || ".join(clean_text(v)[:180] for v in x.head(3))),
    )
    out["hope_style_specificity_proxy"] = 100 * out["total_specific_items"] / out["total_genai_span_tokens"].clip(lower=1)
    return out.sort_values(["event_date_str", "stock_code", "event_source"])


def combined_firm_day(iip_fd: pd.DataFrame, irqa_fd: pd.DataFrame) -> pd.DataFrame:
    combined = pd.concat([iip_fd, irqa_fd], ignore_index=True)
    if combined.empty:
        return combined
    group = combined.groupby(["stock_code", "event_date_str"], as_index=False)
    out = group.agg(
        source_count=("event_source", "nunique"),
        sources=("event_source", lambda x: ";".join(sorted(set(map(str, x))))),
        answer_level_events=("answer_level_events", "sum"),
        company_name=("company_name", first_nonempty),
        answer_terms=("answer_terms", aggregate_terms),
        question_terms=("question_terms", aggregate_terms),
        mean_specificity=("mean_specificity", "mean"),
        max_specificity=("max_specificity", "max"),
        total_specific_items=("total_specific_items", "sum"),
        total_genai_span_tokens=("total_genai_span_tokens", "sum"),
        total_genai_mentions=("total_genai_mentions", "sum"),
        sample_answer=("sample_answer", lambda x: " || ".join(clean_text(v)[:260] for v in x.head(3))),
        sample_question=("sample_question", lambda x: " || ".join(clean_text(v)[:180] for v in x.head(3))),
    )
    out["hope_style_specificity_proxy"] = 100 * out["total_specific_items"] / out["total_genai_span_tokens"].clip(lower=1)
    return out.sort_values(["event_date_str", "stock_code"])


def table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "无"
    show = df.head(max_rows).copy()
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in show.iterrows():
        vals = [str(row.get(c, "")).replace("\n", " ").replace("|", "\\|")[:180] for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)

    iip, iip_stats = build_iip_events()
    irqa, irqa_stats = build_irqa_events()
    for name, df in [("iip_answer_level", iip), ("irqa_answer_level", irqa)]:
        if not df.empty:
            df.to_csv(OUT_DIR / f"{name}_genai_events.csv", index=False, encoding="utf-8-sig")

    iip_fd = firm_day(iip)
    irqa_fd = firm_day(irqa)
    combo_fd = combined_firm_day(iip_fd, irqa_fd)
    iip_fd.to_csv(OUT_DIR / "iip_firm_day_genai_events.csv", index=False, encoding="utf-8-sig")
    irqa_fd.to_csv(OUT_DIR / "irqa_firm_day_genai_events.csv", index=False, encoding="utf-8-sig")
    combo_fd.to_csv(OUT_DIR / "combined_firm_day_genai_events.csv", index=False, encoding="utf-8-sig")

    summary_rows = []
    for source, answer, fd, stats in [
        ("IIP", iip, iip_fd, iip_stats),
        ("IR_QA", irqa, irqa_fd, irqa_stats),
        ("Combined", pd.concat([iip, irqa], ignore_index=True), combo_fd, {}),
    ]:
        summary_rows.append(
            {
                "source": source,
                "raw_rows_read": stats.get("rows_read", ""),
                "a_share_rows": stats.get("a_share_rows", ""),
                "question_only_genai_rows": stats.get("question_only_rows", ""),
                "answer_level_events": len(answer),
                "firm_day_events": len(fd),
                "firms": fd["stock_code"].nunique() if not fd.empty else 0,
                "first_event_date": fd["event_date_str"].min() if not fd.empty else "",
                "last_event_date": fd["event_date_str"].max() if not fd.empty else "",
                "mean_specificity": answer["specificity"].mean() if not answer.empty else "",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_DIR / "event_library_summary.csv", index=False, encoding="utf-8-sig")

    if not combo_fd.empty:
        tmp = combo_fd.copy()
        tmp["year"] = tmp["event_date_str"].str.slice(0, 4)
        tmp["month"] = tmp["event_date_str"].str.slice(0, 7)
        yearly = tmp.groupby("year", as_index=False).agg(firm_day_events=("stock_code", "size"), firms=("stock_code", "nunique"))
        monthly = tmp.groupby("month", as_index=False).agg(firm_day_events=("stock_code", "size"), firms=("stock_code", "nunique"))
        top_firms = (
            tmp.groupby(["stock_code", "company_name"], as_index=False)
            .size()
            .rename(columns={"size": "firm_day_events"})
            .sort_values("firm_day_events", ascending=False)
            .head(30)
        )
    else:
        yearly = pd.DataFrame()
        monthly = pd.DataFrame()
        top_firms = pd.DataFrame()
    yearly.to_csv(OUT_DIR / "combined_yearly_stats.csv", index=False, encoding="utf-8-sig")
    monthly.to_csv(OUT_DIR / "combined_monthly_stats.csv", index=False, encoding="utf-8-sig")
    top_firms.to_csv(OUT_DIR / "combined_top_firms.csv", index=False, encoding="utf-8-sig")

    report = f"""# CSMAR GenAI 事件库最小试跑

日期：2026-05-23

## 口径

本次只把公司侧文本本身包含 GenAI 关键词的记录视为披露事件：

- 互动平台：`ReplyContent` / 公司回复内容命中；
- 调研问答：`Answer` / 公司解答命中；
- 投资者问题命中但公司回答不命中的记录，只记入 `question_only_genai_rows`，不进入主事件库。

## 样本汇总

{table(summary)}

## 年度分布：合并 firm-day 事件

{table(yearly, max_rows=20)}

## 月度分布：合并 firm-day 事件

{table(monthly, max_rows=60)}

## 事件最多的公司

{table(top_firms)}

## 输出文件

目录：`{OUT_DIR.relative_to(ROOT)}`

- `iip_answer_level_genai_events.csv`
- `iip_firm_day_genai_events.csv`
- `irqa_answer_level_genai_events.csv`
- `irqa_firm_day_genai_events.csv`
- `combined_firm_day_genai_events.csv`
- `event_library_summary.csv`
- `combined_yearly_stats.csv`
- `combined_monthly_stats.csv`
- `combined_top_firms.csv`

## 读法

这批 CSMAR 全量表解决了此前互动平台样本过短的问题。下一步可以用
`combined_firm_day_genai_events.csv` 重跑 v5.1 的 rival disclosure response smoke test。
"""
    DOC_OUT.write_text(report, encoding="utf-8")
    print(summary.to_string(index=False))
    print(f"Wrote {OUT_DIR}")
    print(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
