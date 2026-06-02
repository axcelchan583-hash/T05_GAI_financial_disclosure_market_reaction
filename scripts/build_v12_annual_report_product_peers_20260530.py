#!/usr/bin/env python3
"""Build Hoberg-Phillips-style product-market peers from annual-report text.

This replaces the earlier CSMAR business-scope pilot with a closer Chinese
adaptation of Hoberg and Phillips (2016): firm-pair cosine similarity is
computed from annual-report business-description text, not static company
profile text.  The original TNIC data are unavailable for A-shares, so this
script constructs a TNIC-style network from Chinese annual reports.
"""

from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源")
ANNUAL_TXT_ZIP_ROOT = (
    DATA_ROOT
    / "上市公司年报信息/年报文本/2001~2024年年报/2001-2024年A股年报TXT格式"
)
ANNUAL_TXT_2025_DIR = ROOT / "data/raw/annual_reports_2025_txt/年报txt"
COMPANY_INFO_PATH = DATA_ROOT / "上市公司财务信息/STK_LISTEDCOINFOANL.xlsx"
DEFAULT_EVENT_PATH = (
    ROOT
    / "results/csmar_v5_1_response_smoke_20260523/csmar_conservative_focal_events_2023_2026.csv"
)
OUT_DIR = ROOT / "results/v12_annual_report_product_peers_20260530"
DOC_PATH = ROOT / "docs/measurement/11_product_market_peer_network_hoberg_phillips_style_20260530.md"


AI_TERMS = [
    "人工智能",
    "生成式人工智能",
    "生成式AI",
    "AIGC",
    "大模型",
    "大语言模型",
    "LLM",
    "ChatGPT",
    "DeepSeek",
    "智能化",
    "智能",
    "算法",
    "机器学习",
    "深度学习",
    "自然语言处理",
    "多模态",
]

START_PATTERNS = [
    "报告期内公司从事的主要业务",
    "公司从事的主要业务",
    "主要业务及产品",
    "主要业务",
    "主营业务分析",
    "主营业务",
    "经营情况讨论与分析",
    "管理层讨论与分析",
    "业务概要",
]

END_PATTERNS = [
    "核心竞争力分析",
    "主营业务分析",
    "非主营业务分析",
    "资产及负债状况分析",
    "投资状况分析",
    "未来发展的展望",
    "公司未来发展的展望",
    "重要事项",
    "环境和社会责任",
    "公司治理",
    "财务报告",
    "第五节",
    "第六节",
    "第七节",
    "第八节",
    "第九节",
    "第十节",
]


@dataclass
class ReportRecord:
    stock_code: str
    report_year: int
    company_name_from_file: str
    report_date: str
    source_file: str
    business_text: str
    business_text_ai_stripped: str
    text_len: int
    extracted_start_pattern: str
    extracted_mode: str


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\D", "", text)
    return text.zfill(6) if text else ""


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\r", "\n")
    text = re.sub(r"[ \t]+", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9%％（）()、，。；;：:＋+./\n\\-]", "", text)
    return text.strip()


def compact_for_similarity(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"\s+", "", text)
    return text


def strip_ai_terms(text: str) -> str:
    out = text
    for term in sorted(AI_TERMS, key=len, reverse=True):
        out = out.replace(term, "")
    return out


def parse_report_filename(name: str) -> tuple[str, int | None, str, str]:
    base = Path(name).name
    stem = re.sub(r"\.txt$", "", base, flags=re.I)
    parts = stem.split("_")
    code = code6(parts[0]) if parts else ""
    year = None
    if len(parts) > 1 and re.fullmatch(r"\d{4}", parts[1]):
        year = int(parts[1])
    company_name = parts[2] if len(parts) > 2 else ""
    date_match = re.search(r"(20\d{2}-\d{2}-\d{2})", stem)
    report_date = date_match.group(1) if date_match else ""
    return code, year, company_name, report_date


def find_section_start(text: str) -> tuple[int | None, str]:
    candidates: list[tuple[int, str]] = []
    for pat in START_PATTERNS:
        for match in re.finditer(re.escape(pat), text):
            pos = match.start()
            if pos < 3000:
                continue
            context = text[max(0, pos - 120) : pos + 240]
            dot_count = context.count(".") + context.count("·") + context.count("…")
            if dot_count >= 15 and len(context) < 500:
                continue
            candidates.append((pos, pat))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0]
    return None, ""


def find_section_end(text: str, start: int, min_len: int = 2500, max_len: int = 10000) -> int:
    search_from = min(len(text), start + min_len)
    end_limit = min(len(text), start + max_len)
    endings: list[int] = []
    for pat in END_PATTERNS:
        for match in re.finditer(re.escape(pat), text[search_from:end_limit]):
            endings.append(search_from + match.start())
            break
    if endings:
        return max(start + min_len, min(endings))
    return end_limit


def extract_business_text(raw_text: str) -> tuple[str, str, str]:
    # Locate headings on the raw text first.  Cleaning a full annual report is
    # much slower than cleaning only the selected business-description section.
    text = str(raw_text).replace("\r", "\n")
    start, pat = find_section_start(text)
    if start is not None:
        end = find_section_end(text, start)
        extracted = text[start:end]
        mode = "section"
    else:
        # Fallback: use the early narrative portion after the table of contents.
        # This is deliberately conservative and marked in the output.
        start = min(len(text), 5000)
        end = min(len(text), start + 10000)
        extracted = text[start:end]
        pat = ""
        mode = "fallback_window"
    extracted = compact_for_similarity(extracted)
    return extracted, pat, mode


def iter_annual_report_records(year: int) -> list[ReportRecord]:
    records: list[ReportRecord] = []
    if year <= 2024:
        zips = sorted(ANNUAL_TXT_ZIP_ROOT.glob(f"{year}_*份.zip"))
        if not zips:
            raise FileNotFoundError(f"No annual-report TXT zip found for {year}: {ANNUAL_TXT_ZIP_ROOT}")
        zip_path = zips[0]
        with ZipFile(zip_path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".txt")]
            for name in names:
                code, file_year, company_name, report_date = parse_report_filename(name)
                if not code or file_year != year:
                    continue
                raw = zf.read(name).decode("utf-8", errors="ignore")
                business_text, start_pat, mode = extract_business_text(raw)
                if len(business_text) < 200:
                    continue
                records.append(
                    ReportRecord(
                        stock_code=code,
                        report_year=year,
                        company_name_from_file=company_name,
                        report_date=report_date,
                        source_file=name,
                        business_text=business_text,
                        business_text_ai_stripped=strip_ai_terms(business_text),
                        text_len=len(business_text),
                        extracted_start_pattern=start_pat,
                        extracted_mode=mode,
                    )
                )
    else:
        if not ANNUAL_TXT_2025_DIR.exists():
            raise FileNotFoundError(f"Missing 2025 annual-report TXT dir: {ANNUAL_TXT_2025_DIR}")
        for path in sorted(ANNUAL_TXT_2025_DIR.glob("*.txt")):
            code, file_year, company_name, report_date = parse_report_filename(path.name)
            file_year = file_year or year
            if not code or file_year != year:
                continue
            raw = path.read_text(encoding="utf-8", errors="ignore")
            business_text, start_pat, mode = extract_business_text(raw)
            if len(business_text) < 200:
                continue
            records.append(
                ReportRecord(
                    stock_code=code,
                    report_year=year,
                    company_name_from_file=company_name,
                    report_date=report_date or f"{year + 1}-05-01",
                    source_file=str(path),
                    business_text=business_text,
                    business_text_ai_stripped=strip_ai_terms(business_text),
                    text_len=len(business_text),
                    extracted_start_pattern=start_pat,
                    extracted_mode=mode,
                )
            )
    return records


def read_company_info() -> pd.DataFrame:
    raw = pd.read_excel(COMPANY_INFO_PATH, dtype=str)
    raw = raw[~raw["Symbol"].isin(["股票代码", "没有单位"])].copy()
    raw["stock_code"] = raw["Symbol"].map(code6)
    raw["info_date"] = pd.to_datetime(raw["EndDate"], errors="coerce")
    raw["info_year"] = raw["info_date"].dt.year
    raw = raw[raw["stock_code"].ne("")].copy()
    latest = raw.sort_values(["stock_code", "info_year"]).groupby("stock_code", as_index=False).tail(1)
    out = latest[
        ["stock_code", "ShortName", "IndustryNameC", "IndustryNameD", "MAINBUSSINESS", "BusinessScope"]
    ].copy()
    out = out.rename(
        columns={
            "ShortName": "company_name",
            "IndustryNameC": "industry_c",
            "IndustryNameD": "industry_d",
        }
    )
    for col in ["company_name", "industry_c", "industry_d"]:
        out[col] = out[col].fillna("")
    return out.reset_index(drop=True)


def read_events(path: Path) -> pd.DataFrame:
    events = pd.read_csv(path)
    if "focal_code" not in events.columns:
        if "stock_code" not in events.columns:
            raise ValueError(f"Cannot infer focal code from {path}")
        events["focal_code"] = events["stock_code"].map(code6)
    else:
        events["focal_code"] = events["focal_code"].map(code6)
    if "event_date" not in events.columns:
        if "event_date_str" not in events.columns:
            raise ValueError(f"Cannot infer event date from {path}")
        events["event_date"] = pd.to_datetime(events["event_date_str"], errors="coerce")
    else:
        events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    if "specificity" not in events.columns and "hope_style_specificity_proxy" in events.columns:
        events["specificity"] = pd.to_numeric(events["hope_style_specificity_proxy"], errors="coerce")
    if "event_id" not in events.columns:
        events = events.sort_values(["event_date", "focal_code"]).reset_index(drop=True)
        events["event_id"] = [
            f"E{idx + 1:05d}_{row.focal_code}_{row.event_date:%Y%m%d}"
            for idx, row in events.iterrows()
        ]
    events = events[events["focal_code"].ne("") & events["event_date"].notna()].copy()
    events["event_year"] = events["event_date"].dt.year
    events["event_month"] = events["event_date"].dt.month
    # Conservative reporting-season cutoff.  Annual reports for fiscal year y-1
    # are treated as broadly observable from May 1 of calendar year y.
    events["snapshot_report_year"] = np.where(
        events["event_month"].ge(5), events["event_year"] - 1, events["event_year"] - 2
    ).astype(int)
    return events.reset_index(drop=True)


def build_annual_report_texts(years: list[int], force: bool = False) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"annual_report_business_text_{min(years)}_{max(years)}.csv"
    if out_path.exists() and not force:
        return pd.read_csv(out_path, dtype={"stock_code": str})

    company = read_company_info()
    rows: list[dict[str, object]] = []
    for year in years:
        print(f"[extract] annual reports {year}", flush=True)
        records = iter_annual_report_records(year)
        print(f"[extract] {year}: {len(records):,} usable reports", flush=True)
        rows.extend([r.__dict__ for r in records])
    df = pd.DataFrame(rows)
    df["stock_code"] = df["stock_code"].map(code6)
    df = df.merge(company, on="stock_code", how="left")
    df["company_name"] = df["company_name"].fillna(df["company_name_from_file"]).fillna("")
    for col in ["industry_c", "industry_d"]:
        df[col] = df[col].fillna("")
    df = df.sort_values(["report_year", "stock_code"]).reset_index(drop=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return df


def choose_peer_indices(
    sims: np.ndarray,
    companies: pd.DataFrame,
    focal_idx: int,
    top_n: int,
    restrict_same_industry_d: bool,
) -> np.ndarray:
    focal_row = companies.iloc[focal_idx]
    candidate_pool = np.ones(len(sims), dtype=bool)
    candidate_pool[focal_idx] = False
    if restrict_same_industry_d and str(focal_row["industry_d"]).strip():
        candidate_pool &= companies["industry_d"].eq(focal_row["industry_d"]).to_numpy()
    candidate_indices = np.where(candidate_pool)[0]
    if len(candidate_indices) == 0:
        return np.array([], dtype=int)
    pool_sims = sims[candidate_indices]
    keep = min(top_n, len(candidate_indices))
    local_top = np.argpartition(-pool_sims, range(keep))[:keep]
    candidate_idx = candidate_indices[local_top]
    return candidate_idx[np.argsort(-sims[candidate_idx])]


def same_nonempty(a: object, b: object) -> int:
    aa = str(a).strip()
    bb = str(b).strip()
    return int(bool(aa) and aa == bb)


def build_peer_network_for_year(
    text_df: pd.DataFrame,
    focal_codes: set[str],
    report_year: int,
    text_col: str,
    top_n: int,
    restrict_same_industry_d: bool,
) -> pd.DataFrame:
    companies = text_df[text_df["report_year"].eq(report_year)].copy()
    companies = companies[companies[text_col].fillna("").str.len().ge(200)].copy()
    companies = companies.drop_duplicates("stock_code", keep="last").reset_index(drop=True)
    if companies.empty:
        return pd.DataFrame()

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 3),
        min_df=2,
        max_df=0.85,
        max_features=30000,
        sublinear_tf=True,
        norm="l2",
    )
    matrix = vectorizer.fit_transform(companies[text_col].fillna(""))
    matrix = normalize(matrix, norm="l2", copy=False)
    code_to_idx = {code: idx for idx, code in enumerate(companies["stock_code"])}

    valid_focal_codes = [code for code in sorted(focal_codes) if code in code_to_idx]
    if not valid_focal_codes:
        return pd.DataFrame()
    focal_indices = np.array([code_to_idx[code] for code in valid_focal_codes], dtype=int)
    sim_block = (matrix[focal_indices] @ matrix.T).toarray()

    rows: list[dict[str, object]] = []
    for row_pos, focal_code in enumerate(valid_focal_codes):
        focal_idx = code_to_idx[focal_code]
        sims = sim_block[row_pos].copy()
        sims[focal_idx] = -np.inf
        if not np.isfinite(sims).any():
            continue
        top_indices = choose_peer_indices(sims, companies, focal_idx, top_n, restrict_same_industry_d)
        focal_row = companies.iloc[focal_idx]
        for rank, peer_idx in enumerate(top_indices, start=1):
            peer_row = companies.iloc[int(peer_idx)]
            sim = float(sims[int(peer_idx)])
            if not math.isfinite(sim):
                continue
            rows.append(
                {
                    "snapshot_report_year": report_year,
                    "focal_code": focal_code,
                    "focal_name": focal_row["company_name"],
                    "focal_industry_c": focal_row["industry_c"],
                    "focal_industry_d": focal_row["industry_d"],
                    "focal_text_len": int(focal_row["text_len"]),
                    "focal_extracted_mode": focal_row["extracted_mode"],
                    "peer_rank": rank,
                    "peer_code": peer_row["stock_code"],
                    "peer_name": peer_row["company_name"],
                    "peer_industry_c": peer_row["industry_c"],
                    "peer_industry_d": peer_row["industry_d"],
                    "peer_text_len": int(peer_row["text_len"]),
                    "peer_extracted_mode": peer_row["extracted_mode"],
                    "product_similarity": sim,
                    "same_industry_c": same_nonempty(focal_row["industry_c"], peer_row["industry_c"]),
                    "same_industry_d": same_nonempty(focal_row["industry_d"], peer_row["industry_d"]),
                }
            )
    return pd.DataFrame(rows)


def build_peer_networks(
    events: pd.DataFrame,
    text_df: pd.DataFrame,
    top_n: int,
    restrict_same_industry_d: bool,
    text_col: str,
) -> pd.DataFrame:
    networks: list[pd.DataFrame] = []
    for year, group in events.groupby("snapshot_report_year"):
        print(
            f"[peers] year {year}: {group['event_id'].nunique():,} events, "
            f"{group['focal_code'].nunique():,} focal firms, text={text_col}, "
            f"same_industry={restrict_same_industry_d}",
            flush=True,
        )
        focal_codes = set(group["focal_code"].astype(str))
        network = build_peer_network_for_year(
            text_df=text_df,
            focal_codes=focal_codes,
            report_year=int(year),
            text_col=text_col,
            top_n=top_n,
            restrict_same_industry_d=restrict_same_industry_d,
        )
        if not network.empty:
            networks.append(network)
    return pd.concat(networks, ignore_index=True) if networks else pd.DataFrame()


def merge_events(events: pd.DataFrame, network: pd.DataFrame) -> pd.DataFrame:
    if network.empty:
        return pd.DataFrame()
    out = events.merge(network, on=["snapshot_report_year", "focal_code"], how="inner")
    if "specificity" in out.columns:
        out["x_specificity_similarity"] = pd.to_numeric(out["specificity"], errors="coerce") * out[
            "product_similarity"
        ]
    return out


def summarize(text_df: pd.DataFrame, events: pd.DataFrame, outputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rows.append(
        {
            "item": "annual_report_text_rows",
            "value": len(text_df),
        }
    )
    rows.append({"item": "event_rows", "value": len(events)})
    rows.append({"item": "event_firms", "value": events["focal_code"].nunique()})
    for name, df in outputs.items():
        rows.append({"item": f"{name}_rows", "value": len(df)})
        if "event_id" in df.columns:
            rows.append({"item": f"{name}_events", "value": df["event_id"].nunique()})
        if "focal_code" in df.columns:
            rows.append({"item": f"{name}_focal_firms", "value": df["focal_code"].nunique()})
        if "peer_code" in df.columns:
            rows.append({"item": f"{name}_peer_firms", "value": df["peer_code"].nunique()})
        if "product_similarity" in df.columns and len(df):
            rows.append({"item": f"{name}_mean_similarity", "value": df["product_similarity"].mean()})
            rows.append({"item": f"{name}_median_similarity", "value": df["product_similarity"].median()})
            rows.append({"item": f"{name}_same_industry_d_rate", "value": df["same_industry_d"].mean()})
    return pd.DataFrame(rows)


def write_doc(text_df: pd.DataFrame, events: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    coverage = (
        text_df.groupby("report_year", as_index=False)
        .agg(
            firms=("stock_code", "nunique"),
            mean_text_len=("text_len", "mean"),
            section_rate=("extracted_mode", lambda s: float((s == "section").mean())),
        )
        .to_markdown(index=False)
    )
    event_years = (
        events.groupby("snapshot_report_year", as_index=False)
        .agg(events=("event_id", "nunique"), focal_firms=("focal_code", "nunique"))
        .to_markdown(index=False)
    )
    doc = f"""# Annual-Report Product-Market Peer Network

日期：2026-05-30

## 目的

本轮把旧的 CSMAR `MAINBUSSINESS + BusinessScope` 竞品网络升级为更接近
Hoberg and Phillips (2016, JPE) 的文本产品市场网络。核心思想保持一致：

```text
年度报告业务描述文本 -> firm text vector -> firm-pair cosine similarity -> TopK product-market peers
```

本文不能直接使用美国 TNIC 数据，因此采用 **Hoberg-Phillips-style Chinese A-share product-market peer network**。

## 与 Hoberg-Phillips 的对应

| 维度 | Hoberg and Phillips (2016) | 本项目当前实现 |
|---|---|---|
| 文本来源 | 10-K business descriptions | A 股年报业务/经营章节 TXT |
| 相似度单元 | firm-pair product-word cosine | firm-pair Chinese char 2-3 gram TF-IDF cosine |
| 同行定义 | firm-specific product-market peers | event-specific Top5/Top10 product-market peers |
| 时间口径 | 年度更新 | 按事件日期映射到已完成年报披露季的 fiscal year |
| 防 look-ahead | 使用当年可见 10-K | 事件在 5 月前用 t-2 年报，5 月后用 t-1 年报 |

## 当前数据覆盖

年报业务文本覆盖：

{coverage}

事件映射到的年报快照：

{event_years}

## 输出

输出目录：

```text
{out_dir}
```

主要文件：

- `annual_report_business_text_YYYY_YYYY.csv`
- `annual_report_peer_network_global_top10.csv`
- `annual_report_peer_event_global_top10.csv`
- `annual_report_peer_network_same_industry_d_top10.csv`
- `annual_report_peer_event_same_industry_d_top10.csv`
- `annual_report_peer_network_global_ai_stripped_top10.csv`
- `annual_report_peer_event_global_ai_stripped_top10.csv`
- `sample_summary.csv`

## 当前限制

1. 中文文本不能逐字复刻英文 noun/proper noun 筛选，因此主口径使用 char 2-3 gram TF-IDF cosine。
2. 年报章节抽取是规则法；少数公司会退回到年报正文前段窗口，输出中用 `extracted_mode` 标记。
3. 2025 年报 TXT 文件名缺少实际披露日，当前只在保守 reporting-season cutoff 下使用。
4. 这一步只更新 peer network，还没有自动替换主回归表。

## Summary

{summary.to_markdown(index=False)}
"""
    DOC_PATH.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-path", type=Path, default=DEFAULT_EVENT_PATH)
    parser.add_argument("--years", type=int, nargs="+", default=[2021, 2022, 2023, 2024, 2025])
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--force-extract", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = read_events(args.event_path)
    needed_years = sorted(set(events["snapshot_report_year"]).intersection(set(args.years)))
    text_df = build_annual_report_texts(needed_years, force=args.force_extract)
    text_df = text_df[text_df["report_year"].isin(needed_years)].copy()

    outputs: dict[str, pd.DataFrame] = {}
    specs = [
        ("global", False, "business_text"),
        ("same_industry_d", True, "business_text"),
        ("global_ai_stripped", False, "business_text_ai_stripped"),
    ]
    for label, same_industry, text_col in specs:
        network = build_peer_networks(
            events=events,
            text_df=text_df,
            top_n=args.top_n,
            restrict_same_industry_d=same_industry,
            text_col=text_col,
        )
        event_panel = merge_events(events, network)
        network_path = OUT_DIR / f"annual_report_peer_network_{label}_top{args.top_n}.csv"
        event_path = OUT_DIR / f"annual_report_peer_event_{label}_top{args.top_n}.csv"
        network.to_csv(network_path, index=False, encoding="utf-8-sig")
        event_panel.to_csv(event_path, index=False, encoding="utf-8-sig")
        outputs[f"network_{label}"] = network
        outputs[f"event_{label}"] = event_panel

    summary = summarize(text_df, events, outputs)
    summary.to_csv(OUT_DIR / "sample_summary.csv", index=False, encoding="utf-8-sig")
    write_doc(text_df, events, summary, OUT_DIR)

    print(f"events: {len(events):,}")
    print(f"annual-report text rows: {len(text_df):,}")
    print(f"outputs: {OUT_DIR}")
    print(f"doc: {DOC_PATH}")


if __name__ == "__main__":
    main()
