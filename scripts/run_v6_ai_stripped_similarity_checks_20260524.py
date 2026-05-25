#!/usr/bin/env python3
"""AI-word-stripped product-similarity checks for v6.

Rebuilds product-market peers after removing generic AI / GenAI terms from
company product text, then reruns the v6 market-model CAR tests with the same
announcement-cleaning filters.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_announcement_clean_checks_20260524 import (
    OUTCOMES,
    ROOT,
    attach_announcement_flags,
    base_clean_sample,
    build_announcement_stock_day_flags,
    code6,
    fit_absorbed_model,
)


BASE_DIR = ROOT / "results" / "v6_announcement_clean_checks_20260524"
MM_DIR = ROOT / "results" / "v6_supplement_market_model_placebo_20260524"
OUT_DIR = ROOT / "results" / "v6_ai_stripped_similarity_checks_20260524"

TRUE_PANEL = BASE_DIR / "true_peer_market_model_car_panel_with_ann_flags.csv.gz"
COMPANY_TEXT = ROOT / "results" / "v4_peer_spillover_x_pilot" / "v4_company_product_text_latest.csv"
STOCK_MODEL = MM_DIR / "stock_returns_with_market_model_params.csv"

AI_TERMS = [
    "生成式人工智能",
    "生成式AI",
    "生成式ai",
    "人工智能",
    "AI大模型",
    "人工智能大模型",
    "大模型",
    "大语言模型",
    "语言大模型",
    "基础模型",
    "预训练模型",
    "多模态",
    "多模态大模型",
    "AIGC",
    "GenAI",
    "ChatGPT",
    "DeepSeek",
    "GPT",
    "LLM",
    "RAG",
    "MaaS",
    "文生图",
    "文生视频",
    "Sora",
    "Kimi",
    "通义千问",
    "通义",
    "文心一言",
    "文心",
    "讯飞星火",
    "星火大模型",
    "智谱",
    "豆包",
    "盘古大模型",
    "混元大模型",
    "百川大模型",
    "商汤日日新",
    "日日新大模型",
    "机器学习",
    "深度学习",
    "自然语言处理",
    "计算机视觉",
    "算法",
    "智能",
    "智慧",
]


def clean_text(value: object) -> str:
    text = str(value or "")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9%％（）()、，。；;：:＋+./-]", "", text)
    return text


def strip_ai_terms(value: object) -> str:
    text = clean_text(value)
    for term in sorted(AI_TERMS, key=len, reverse=True):
        text = re.sub(re.escape(term), "", text, flags=re.IGNORECASE)
    return text


def char_ngrams(text: str, min_n: int = 2, max_n: int = 4) -> Counter[str]:
    text = clean_text(text)
    out: Counter[str] = Counter()
    for n in range(min_n, max_n + 1):
        if len(text) < n:
            continue
        for i in range(len(text) - n + 1):
            out[text[i : i + n]] += 1
    return out


def build_sparse_tfidf(companies: pd.DataFrame) -> tuple[list[dict[str, float]], dict[str, list[tuple[int, float]]]]:
    counts = [char_ngrams(t) for t in companies["product_text_stripped"].fillna("")]
    n_docs = len(counts)
    df: Counter[str] = Counter()
    for c in counts:
        df.update(c.keys())
    vocab = {term for term, d in df.items() if d >= 2 and d <= 0.85 * n_docs}
    idf = {term: math.log((1 + n_docs) / (1 + df[term])) + 1 for term in vocab}

    vectors: list[dict[str, float]] = []
    postings: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for idx, c in enumerate(counts):
        weights = {
            term: (1 + math.log(freq)) * idf[term]
            for term, freq in c.items()
            if term in vocab and freq > 0
        }
        norm = math.sqrt(sum(v * v for v in weights.values()))
        if norm > 0:
            weights = {term: val / norm for term, val in weights.items()}
        vectors.append(weights)
        for term, val in weights.items():
            postings[term].append((idx, val))
    return vectors, postings


def load_event_meta() -> pd.DataFrame:
    cols = [
        "event_id",
        "focal_code",
        "event_date",
        "specificity",
        "focal_name",
        "focal_industry_d",
        "date_m1",
        "date_0",
        "date_p1",
        "is_first_focal_event",
        "specificity_w",
        "specificity_z",
    ]
    df = pd.read_csv(TRUE_PANEL, usecols=cols, dtype={"event_id": str, "focal_code": str})
    df = df.drop_duplicates("event_id").copy()
    df["focal_code"] = df["focal_code"].map(code6)
    for col in ["event_date", "date_m1", "date_0", "date_p1"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def load_companies() -> pd.DataFrame:
    df = pd.read_csv(COMPANY_TEXT, dtype={"stock_code": str})
    df["stock_code"] = df["stock_code"].map(code6)
    df["product_text"] = df["product_text"].fillna("").map(clean_text)
    df["product_text_stripped"] = df["product_text"].map(strip_ai_terms)
    df["stripped_text_len"] = df["product_text_stripped"].str.len()
    df = df[df["stock_code"].ne("") & df["stripped_text_len"].ge(20)].copy()
    return df.drop_duplicates("stock_code").reset_index(drop=True)


def build_ai_stripped_peers(events: pd.DataFrame, companies: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / "ai_stripped_product_peer_network_top10.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype={"focal_code": str, "peer_code": str})

    vectors, postings = build_sparse_tfidf(companies)
    code_to_idx = {code: idx for idx, code in enumerate(companies["stock_code"])}
    focal_codes = sorted(set(events["focal_code"]) & set(code_to_idx))
    rows: list[dict[str, object]] = []
    for k, focal_code in enumerate(focal_codes, start=1):
        focal_idx = code_to_idx[focal_code]
        scores: defaultdict[int, float] = defaultdict(float)
        for term, focal_val in vectors[focal_idx].items():
            for doc_idx, doc_val in postings.get(term, []):
                if doc_idx != focal_idx:
                    scores[doc_idx] += focal_val * doc_val
        if not scores:
            continue
        focal_row = companies.iloc[focal_idx]
        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
        for rank, (peer_idx, sim) in enumerate(top, start=1):
            peer_row = companies.iloc[int(peer_idx)]
            rows.append(
                {
                    "focal_code": focal_code,
                    "focal_name": focal_row["company_name"],
                    "focal_industry_d": focal_row["industry_d"],
                    "peer_rank": rank,
                    "peer_code": peer_row["stock_code"],
                    "peer_name": peer_row["company_name"],
                    "peer_industry_d": peer_row["industry_d"],
                    "product_similarity_stripped": float(sim),
                    "same_industry_d": int(str(focal_row["industry_d"]) == str(peer_row["industry_d"])),
                }
            )
        if k % 250 == 0:
            print(f"built AI-stripped peers for {k}/{len(focal_codes)} focal firms", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(cache, index=False)
    return out


def attach_returns(panel: pd.DataFrame) -> pd.DataFrame:
    stock = pd.read_csv(STOCK_MODEL, dtype={"peer_code": str})
    stock["peer_code"] = stock["peer_code"].map(code6)
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
    idx_stock = stock.set_index(["peer_code", "date"]).sort_index()
    out = panel.copy()
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        idx = pd.MultiIndex.from_arrays([out["peer_code"], out[date_col]])
        vals = idx_stock[["ret", "mkt_ret", "trdsta", "limit_status"]].reindex(idx).reset_index(drop=True)
        for col in ["ret", "mkt_ret", "trdsta", "limit_status"]:
            out[f"{col}_{suffix}"] = vals[col].to_numpy()
    idx0 = pd.MultiIndex.from_arrays([out["peer_code"], out["date_0"]])
    params = idx_stock[["alpha_mm", "beta_mm"]].reindex(idx0).reset_index(drop=True)
    out["alpha_mm"] = params["alpha_mm"].to_numpy()
    out["beta_mm"] = params["beta_mm"].to_numpy()
    for suffix in ["m1", "0", "p1"]:
        out[f"abret_{suffix}_mm"] = out[f"ret_{suffix}"] - (
            out["alpha_mm"] + out["beta_mm"] * out[f"mkt_ret_{suffix}"]
        )
    out["peer_car_0_p1_mm"] = out[["abret_0_mm", "abret_p1_mm"]].sum(axis=1, min_count=2)
    out["peer_car_m1_p1_mm"] = out[["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]].sum(axis=1, min_count=3)
    out["obs_peer_car_m1_p1_mm"] = out[["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]].notna().sum(axis=1)
    out["normal_trading_m1_p1"] = (
        out[["trdsta_m1", "trdsta_0", "trdsta_p1"]].fillna(-999).astype(int).eq(1).all(axis=1)
    ).astype(int)
    out["no_limit_m1_p1"] = (
        out[["limit_status_m1", "limit_status_0", "limit_status_p1"]].fillna(0).astype(int).eq(0).all(axis=1)
    ).astype(int)
    return out


def add_ai_active(panel: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    event_dates_by_code = {
        code: np.array(sorted(sub["event_date"].dropna().unique()), dtype="datetime64[ns]")
        for code, sub in events[["focal_code", "event_date"]].drop_duplicates().groupby("focal_code")
    }
    flags = []
    for peer, event_date in zip(panel["peer_code"], panel["event_date"]):
        dates = event_dates_by_code.get(peer)
        if dates is None or len(dates) == 0 or pd.isna(event_date):
            flags.append(0)
            continue
        cutoff = np.datetime64((pd.Timestamp(event_date) - pd.Timedelta(days=5)).normalize())
        flags.append(int(np.searchsorted(dates, cutoff, side="right") > 0))
    out = panel.copy()
    out["ai_active_peer_tminus5"] = flags
    out["specz_ai_active"] = out["specificity_z"] * out["ai_active_peer_tminus5"]
    return out


def build_panel(events: pd.DataFrame, peers: pd.DataFrame) -> pd.DataFrame:
    panel = events.merge(peers, on="focal_code", how="inner")
    panel = panel[panel["peer_code"].ne(panel["focal_code"])].copy()
    panel = attach_returns(panel)
    panel = add_ai_active(panel, events)
    flags = build_announcement_stock_day_flags()
    panel = attach_announcement_flags(panel, flags)
    panel["event_week"] = panel["date_0"].dt.strftime("%Y-%U")
    panel["peer_industry_d"] = panel["peer_industry_d"].fillna("UNKNOWN").astype(str)
    panel["peer_industry_week"] = panel["peer_industry_d"] + "|" + panel["event_week"].fillna("")
    return panel


def run_models(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    samples = [
        ("base_no_announcement_filter", base_clean_sample(panel)),
        ("drop_either_cleaning_ann", base_clean_sample(panel)[lambda d: d["either_cleaning_ann"].eq(0)].copy()),
    ]
    fe_specs = [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]
    for top_n in [5, 10]:
        top_panel = panel[panel["peer_rank"].le(top_n)].copy()
        samples = [
            ("base_no_announcement_filter", base_clean_sample(top_panel)),
            (
                "drop_either_cleaning_ann",
                base_clean_sample(top_panel)[lambda d: d["either_cleaning_ann"].eq(0)].copy(),
            ),
        ]
        for sample_name, sample in samples:
            summaries.append(
                {
                    "top_n": top_n,
                    "sample": sample_name,
                    "obs": len(sample),
                    "events": sample["event_id"].nunique(),
                    "focal_firms": sample["focal_code"].nunique(),
                    "peer_firms": sample["peer_code"].nunique(),
                    "mean_ai_active": sample["ai_active_peer_tminus5"].mean(),
                    "mean_similarity_stripped": sample["product_similarity_stripped"].mean(),
                    "mean_car_0_p1_mm": sample["peer_car_0_p1_mm"].mean(),
                    "mean_car_m1_p1_mm": sample["peer_car_m1_p1_mm"].mean(),
                }
            )
            for fe_name, fe_cols in fe_specs:
                for outcome in OUTCOMES:
                    for row in fit_absorbed_model(
                        sample,
                        outcome,
                        ["ai_active_peer_tminus5", "specz_ai_active"],
                        fe_cols,
                    ):
                        row.update(
                            {
                                "peer_group": "ai_stripped_top_peers",
                                "top_n": top_n,
                                "sample": sample_name,
                                "fe_spec": fe_name,
                                "model": "M1_specz_x_ai_active",
                            }
                        )
                        rows.append(row)
    return pd.DataFrame(summaries), pd.DataFrame(rows)


def overlap_with_original(peers: pd.DataFrame) -> pd.DataFrame:
    original = pd.read_csv(
        ROOT / "results" / "csmar_v5_1_response_smoke_20260523" / "csmar_product_peer_network_top10.csv",
        dtype={"focal_code": str, "peer_code": str},
    )
    original["focal_code"] = original["focal_code"].map(code6)
    original["peer_code"] = original["peer_code"].map(code6)
    rows = []
    for top_n in [5, 10]:
        orig_sets = (
            original[original["peer_rank"].le(top_n)]
            .groupby("focal_code")["peer_code"]
            .apply(set)
        )
        strip_sets = (
            peers[peers["peer_rank"].le(top_n)]
            .groupby("focal_code")["peer_code"]
            .apply(set)
        )
        common = sorted(set(orig_sets.index) & set(strip_sets.index))
        shares = []
        for code in common:
            denom = max(1, min(len(orig_sets[code]), len(strip_sets[code])))
            shares.append(len(orig_sets[code] & strip_sets[code]) / denom)
        rows.append(
            {
                "top_n": top_n,
                "focal_firms": len(common),
                "mean_overlap_share": float(np.mean(shares)) if shares else np.nan,
                "median_overlap_share": float(np.median(shares)) if shares else np.nan,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_event_meta()
    companies = load_companies()
    peers = build_ai_stripped_peers(events, companies)
    panel = build_panel(events, peers)
    panel.to_csv(OUT_DIR / "ai_stripped_peer_market_model_car_panel_with_ann_flags.csv.gz", index=False, compression="gzip")
    summary, regs = run_models(panel)
    summary.to_csv(OUT_DIR / "v6_ai_stripped_similarity_sample_summary.csv", index=False)
    regs.to_csv(OUT_DIR / "v6_ai_stripped_similarity_regressions.csv", index=False)
    overlap = overlap_with_original(peers)
    overlap.to_csv(OUT_DIR / "ai_stripped_vs_original_peer_overlap.csv", index=False)
    key = regs[regs["term"].eq("specz_ai_active")].copy()
    print(overlap.to_string(index=False), flush=True)
    print(summary.to_string(index=False), flush=True)
    print(key.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
