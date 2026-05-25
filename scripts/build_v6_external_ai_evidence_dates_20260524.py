#!/usr/bin/env python3
"""Build external pre-event AI evidence tables for v6.

The output is intentionally simple:
1. first observable evidence dates by stock code;
2. AI hiring firm-day counts for rolling-window flags.

Run with the bundled Python runtime because it includes openpyxl.
"""

from __future__ import annotations

import io
import re
import subprocess
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v6_external_ai_active_20260524"

CAC_A_SHARE = (
    ROOT
    / "results"
    / "v5_1_disclosure_response_smoke"
    / "v5_1_cac_first_event_by_a_share_lower_bound.csv"
)
HIST_DISCLOSURE = ROOT / "results" / "csmar_genai_event_library_20260523" / "combined_firm_day_genai_events.csv"
PATENT_ZIP = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司数据相关信息/专利明细情况093018090(仅供哈佛大学使用).zip"
)
RECRUIT_RAR = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司其他/上市公司招聘大数据2014-2026.3.rar"
)

AI_PATENT_PAT = re.compile(
    r"人工智能|机器学习|深度学习|神经网络|自然语言|NLP|语音识别|图像识别|计算机视觉|"
    r"知识图谱|智能问答|智能客服|智能推荐|推荐算法|智能算法|算法模型|大模型|AIGC|"
    r"生成式|多模态|大语言|预训练|Transformer|RAG|智能体",
    re.IGNORECASE,
)
GENAI_PATENT_PAT = re.compile(
    r"生成式|大模型|AIGC|ChatGPT|DeepSeek|多模态|大语言|预训练|Transformer|RAG|"
    r"提示词|Prompt|智能体|扩散模型",
    re.IGNORECASE,
)

AI_HIRING_PAT = re.compile(
    r"人工智能|机器学习|深度学习|神经网络|自然语言|NLP|语音识别|图像识别|计算机视觉|"
    r"知识图谱|推荐算法|算法工程师|AI算法|AI工程师|算法模型|大模型|AIGC|生成式|"
    r"ChatGPT|DeepSeek|LLM|多模态|RAG|Prompt|Transformer|智能体",
    re.IGNORECASE,
)
GENAI_HIRING_PAT = re.compile(
    r"生成式|大模型|AIGC|ChatGPT|DeepSeek|LLM|多模态|RAG|Prompt|Transformer|"
    r"智能体|大语言模型|文生图|扩散模型|微调|Fine[- ]?tuning",
    re.IGNORECASE,
)


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def min_date(series: pd.Series) -> pd.Timestamp | pd.NaT:
    s = pd.to_datetime(series, errors="coerce").dropna()
    return s.min() if len(s) else pd.NaT


def build_cac_first_dates() -> pd.DataFrame:
    df = pd.read_csv(CAC_A_SHARE, dtype={"stock_code": str})
    df["stock_code"] = df["stock_code"].map(code6)
    df["cac_event_date"] = pd.to_datetime(df["cac_event_date"], errors="coerce")
    return (
        df[df["stock_code"].ne("") & df["cac_event_date"].notna()]
        .groupby("stock_code", as_index=False)
        .agg(cac_first_date=("cac_event_date", "min"))
    )


def build_history_first_dates() -> pd.DataFrame:
    df = pd.read_csv(HIST_DISCLOSURE, dtype={"stock_code": str})
    df["stock_code"] = df["stock_code"].map(code6)
    df["event_date"] = pd.to_datetime(df["event_date_str"], errors="coerce")
    # Avoid pre-ChatGPT false positives from terms such as RAG and MaaS.
    df = df[df["event_date"].ge(pd.Timestamp("2022-11-30"))].copy()
    return (
        df[df["stock_code"].ne("") & df["event_date"].notna()]
        .groupby("stock_code", as_index=False)
        .agg(history_genai_disclosure_first_date=("event_date", "min"))
    )


def build_patent_first_dates() -> pd.DataFrame:
    with zipfile.ZipFile(PATENT_ZIP) as zf:
        data = zf.read("PT_LCDETAIL.xlsx")
    df = pd.read_excel(io.BytesIO(data), skiprows=[1, 2])
    df["stock_code"] = df["Symbol"].map(code6)
    df["PatentName"] = df["PatentName"].fillna("").astype(str)
    df["GrantDate"] = pd.to_datetime(df["GrantDate"], errors="coerce")
    df["ApplicationDate"] = pd.to_datetime(df["ApplicationDate"], errors="coerce")
    df["is_ai_patent_title"] = df["PatentName"].str.contains(AI_PATENT_PAT, na=False)
    df["is_genai_patent_title"] = df["PatentName"].str.contains(GENAI_PATENT_PAT, na=False)
    valid = df[df["stock_code"].ne("")].copy()

    rows = []
    for code, sub in valid.groupby("stock_code", sort=False):
        ai = sub[sub["is_ai_patent_title"]]
        gen = sub[sub["is_genai_patent_title"]]
        rows.append(
            {
                "stock_code": code,
                "ai_patent_grant_first_date": min_date(ai["GrantDate"]),
                "ai_patent_application_first_date": min_date(ai["ApplicationDate"]),
                "genai_patent_grant_first_date": min_date(gen["GrantDate"]),
                "genai_patent_application_first_date": min_date(gen["ApplicationDate"]),
                "ai_patent_title_count_total": int(len(ai)),
                "genai_patent_title_count_total": int(len(gen)),
            }
        )
    return pd.DataFrame(rows)


def build_hiring_day_counts() -> pd.DataFrame:
    cache = OUT_DIR / "external_ai_hiring_firm_day_counts.csv.gz"
    if cache.exists():
        return pd.read_csv(cache, dtype={"stock_code": str}, parse_dates=["post_date"])

    usecols = ["关联股票代码", "与上市公司关系", "招聘岗位", "职位描述", "招聘发布日期"]
    proc = subprocess.Popen(
        ["unar", "-q", "-D", "-o", "-", str(RECRUIT_RAR)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.stdout is None:
        raise RuntimeError("Failed to open recruitment archive stream")

    pieces: list[pd.DataFrame] = []
    total_rows = 0
    ai_rows = 0
    for chunk in pd.read_csv(
        proc.stdout,
        usecols=usecols,
        dtype=str,
        chunksize=200_000,
        encoding="utf-8-sig",
        encoding_errors="replace",
        on_bad_lines="skip",
    ):
        total_rows += len(chunk)
        chunk["stock_code"] = chunk["关联股票代码"].map(code6)
        relation = chunk["与上市公司关系"].fillna("")
        chunk = chunk[chunk["stock_code"].ne("") & relation.str.contains("本身|子公司", regex=True)].copy()
        if chunk.empty:
            continue
        text = chunk["招聘岗位"].fillna("") + " " + chunk["职位描述"].fillna("")
        chunk["is_broad_ai_hiring"] = text.str.contains(AI_HIRING_PAT, na=False)
        chunk["is_genai_hiring"] = text.str.contains(GENAI_HIRING_PAT, na=False)
        chunk = chunk[chunk["is_broad_ai_hiring"] | chunk["is_genai_hiring"]].copy()
        if chunk.empty:
            continue
        chunk["post_date"] = pd.to_datetime(chunk["招聘发布日期"], errors="coerce")
        chunk = chunk[chunk["post_date"].notna()].copy()
        if chunk.empty:
            continue
        ai_rows += len(chunk)
        grouped = (
            chunk.groupby(["stock_code", "post_date"], as_index=False)
            .agg(
                broad_ai_hiring_count=("is_broad_ai_hiring", "sum"),
                genai_hiring_count=("is_genai_hiring", "sum"),
            )
        )
        pieces.append(grouped)
        if total_rows and total_rows % 1_000_000 < 200_000:
            print(f"scanned recruitment rows={total_rows:,}, ai_candidate_rows={ai_rows:,}", flush=True)

    _, stderr = proc.communicate()
    if proc.returncode not in (0, None):
        raise RuntimeError(stderr.decode("utf-8", errors="replace"))

    if not pieces:
        out = pd.DataFrame(columns=["stock_code", "post_date", "broad_ai_hiring_count", "genai_hiring_count"])
    else:
        out = (
            pd.concat(pieces, ignore_index=True)
            .groupby(["stock_code", "post_date"], as_index=False)
            .agg(
                broad_ai_hiring_count=("broad_ai_hiring_count", "sum"),
                genai_hiring_count=("genai_hiring_count", "sum"),
            )
            .sort_values(["stock_code", "post_date"])
        )
    out.to_csv(cache, index=False, compression="gzip")
    pd.DataFrame(
        [
            {
                "recruitment_rows_scanned": total_rows,
                "ai_candidate_rows_after_relation_filter": ai_rows,
                "firm_day_rows": len(out),
                "firms_with_broad_ai_hiring": out.loc[out["broad_ai_hiring_count"].gt(0), "stock_code"].nunique(),
                "firms_with_genai_hiring": out.loc[out["genai_hiring_count"].gt(0), "stock_code"].nunique(),
                "first_post_date": out["post_date"].min(),
                "last_post_date": out["post_date"].max(),
            }
        ]
    ).to_csv(OUT_DIR / "external_ai_hiring_scan_summary.csv", index=False)
    return out


def merge_first_dates(
    cac: pd.DataFrame,
    history: pd.DataFrame,
    patent: pd.DataFrame,
    hiring_day: pd.DataFrame,
) -> pd.DataFrame:
    hiring_first = (
        hiring_day.groupby("stock_code", as_index=False)
        .agg(
            broad_ai_hiring_first_date=("post_date", "min"),
            genai_hiring_first_date=("post_date", lambda s: min_date(hiring_day.loc[s.index, "post_date"][hiring_day.loc[s.index, "genai_hiring_count"].gt(0)])),
            broad_ai_hiring_firm_days=("post_date", "size"),
            broad_ai_hiring_total=("broad_ai_hiring_count", "sum"),
            genai_hiring_total=("genai_hiring_count", "sum"),
        )
    )
    all_codes = sorted(
        set(cac["stock_code"])
        | set(history["stock_code"])
        | set(patent["stock_code"])
        | set(hiring_first["stock_code"])
    )
    out = pd.DataFrame({"stock_code": all_codes})
    for df in [cac, patent, hiring_first, history]:
        out = out.merge(df, on="stock_code", how="left")
    date_cols = [c for c in out.columns if c.endswith("_date")]
    for col in date_cols:
        out[col] = pd.to_datetime(out[col], errors="coerce").dt.strftime("%Y-%m-%d")
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cac = build_cac_first_dates()
    history = build_history_first_dates()
    patent = build_patent_first_dates()
    hiring_day = build_hiring_day_counts()
    first_dates = merge_first_dates(cac, history, patent, hiring_day)
    first_dates.to_csv(OUT_DIR / "external_ai_evidence_first_dates_by_firm.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "cac_a_share_firms": cac["stock_code"].nunique(),
                "history_genai_disclosure_firms_post_chatgpt": history["stock_code"].nunique(),
                "ai_patent_title_firms": patent.loc[patent["ai_patent_title_count_total"].gt(0), "stock_code"].nunique(),
                "genai_patent_title_firms": patent.loc[patent["genai_patent_title_count_total"].gt(0), "stock_code"].nunique(),
                "broad_ai_hiring_firms": hiring_day.loc[hiring_day["broad_ai_hiring_count"].gt(0), "stock_code"].nunique(),
                "genai_hiring_firms": hiring_day.loc[hiring_day["genai_hiring_count"].gt(0), "stock_code"].nunique(),
                "evidence_union_firms": first_dates["stock_code"].nunique(),
            }
        ]
    )
    summary.to_csv(OUT_DIR / "external_ai_evidence_summary.csv", index=False)
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
