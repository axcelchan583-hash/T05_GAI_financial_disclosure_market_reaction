#!/usr/bin/env python3
"""Build Chinese-literature product-market peer networks from annual reports.

This script is a closer A-share adaptation of the product-market text methods
used in Ren and Wang (2019, Accounting Research), Wang, Zhao and Ren (2020,
China Accounting and Finance Review), and Liu, Liu and Yin (2020, The Journal
of World Economy).

The earlier v12 annual-report network used character n-gram TF-IDF.  That is a
reasonable smoke-test, but it is not the same measurement language as the
Chinese papers.  Here we build two auditable alternatives:

1. ren_wang_binary:
   Chinese segmentation -> stop/non-product word removal -> binary 0/1 word
   vector -> cosine similarity -> nearest product-market peers.

2. liu_product_tfidf:
   Product-word dictionary seeded from CSMAR main-business/business-scope text
   -> TF-IDF product-word vector -> cosine similarity -> nearest peers.

The script only constructs peer networks and event-peer mappings.  It does not
overwrite prior v12/v17 peer outputs.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Iterable

import jieba
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize

from build_v12_annual_report_product_peers_20260530 import (
    ROOT,
    OUT_DIR as V12_OUT_DIR,
    DEFAULT_EVENT_PATH,
    code6,
    read_events,
)


OUT_DIR = ROOT / "results" / "v22_chinese_literature_product_peers_20260601"
ANNUAL_TEXT_PATH = V12_OUT_DIR / "annual_report_business_text_2021_2025.csv"


AI_TERMS = {
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
    "机器人",
}

STOPWORDS = {
    "的",
    "了",
    "和",
    "与",
    "及",
    "等",
    "在",
    "对",
    "为",
    "是",
    "以",
    "或",
    "并",
    "而",
    "于",
    "将",
    "已",
    "也",
    "中",
    "从",
    "由",
    "向",
    "及其",
    "以及",
    "通过",
    "进行",
    "相关",
    "主要",
    "公司",
    "本公司",
    "报告期",
    "业务",
    "行业",
    "客户",
    "市场",
    "产品",
    "服务",
    "发展",
    "经营",
    "管理",
    "生产",
    "销售",
    "提供",
    "包括",
    "具有",
    "实现",
    "形成",
    "提升",
    "持续",
    "进一步",
    "方面",
    "领域",
    "能力",
    "情况",
}

NON_PRODUCT_TERMS = {
    "利润",
    "融资",
    "负债",
    "资产",
    "股东",
    "董事",
    "监事",
    "高管",
    "会计",
    "审计",
    "现金",
    "净利",
    "收入",
    "成本",
    "费用",
    "同比",
    "增长",
    "下降",
    "风险",
    "治理",
    "公告",
    "披露",
    "年度",
    "财务",
    "证券",
    "股票",
    "上市",
    "交易",
    "投资者",
    "募集",
    "权益",
    "股份",
    "分红",
    "报告",
    "章节",
    "同比增长",
    "净利润",
    "营业收入",
    "总资产",
    "董事会",
    "监事会",
    "独立董事",
    "会计师",
}

TOKEN_DROP_RE = re.compile(r"^[0-9０-９一二三四五六七八九十百千万亿年月日%％.．、，。；：:（）()]+$")


def strip_ai_terms(text: str) -> str:
    out = "" if pd.isna(text) else str(text)
    for term in sorted(AI_TERMS, key=len, reverse=True):
        out = out.replace(term, "")
    return out


def normalize_token(token: str) -> str:
    token = token.strip()
    token = re.sub(r"^[^\u4e00-\u9fa5A-Za-z0-9]+|[^\u4e00-\u9fa5A-Za-z0-9]+$", "", token)
    return token


def keep_token(token: str, product_vocab: set[str] | None = None) -> bool:
    if not token:
        return False
    if len(token) <= 1:
        return False
    if TOKEN_DROP_RE.match(token):
        return False
    if token in STOPWORDS or token in NON_PRODUCT_TERMS or token in AI_TERMS:
        return False
    if len(token) > 18:
        return False
    if product_vocab is not None and token not in product_vocab:
        return False
    return bool(re.search(r"[\u4e00-\u9fa5A-Za-z]", token))


def tokenize(text: object, product_vocab: set[str] | None = None) -> list[str]:
    raw = strip_ai_terms("" if pd.isna(text) else str(text))
    raw = re.sub(r"\s+", "", raw)
    toks: list[str] = []
    for tok in jieba.lcut(raw, cut_all=False):
        tok = normalize_token(tok)
        if keep_token(tok, product_vocab=product_vocab):
            toks.append(tok)
    return toks


def build_product_vocab(df: pd.DataFrame, min_doc_freq: int = 3, max_doc_share: float = 0.60) -> set[str]:
    """Seed a product dictionary from CSMAR main-business and business-scope text.

    Liu et al. (2020) use external product dictionaries and Wind product-composition
    nouns.  We do not have those exact dictionaries in the current repo, so this
    is a transparent local approximation from CSMAR business fields.
    """
    doc_freq: dict[str, int] = {}
    n_docs = 0
    fields = ["MAINBUSSINESS", "BusinessScope"]
    for _, row in df.drop_duplicates(["stock_code", "report_year"]).iterrows():
        text = "。".join(str(row.get(col, "") or "") for col in fields)
        toks = set(tokenize(text))
        if not toks:
            continue
        n_docs += 1
        for tok in toks:
            doc_freq[tok] = doc_freq.get(tok, 0) + 1
    upper = max(1, int(n_docs * max_doc_share))
    vocab = {
        tok
        for tok, dfreq in doc_freq.items()
        if dfreq >= min_doc_freq and dfreq <= upper and tok not in STOPWORDS and tok not in NON_PRODUCT_TERMS
    }
    return vocab


def choose_top_indices(
    sims: np.ndarray,
    companies: pd.DataFrame,
    focal_idx: int,
    top_n: int,
    restrict_same_industry_d: bool,
) -> np.ndarray:
    focal_row = companies.iloc[focal_idx]
    pool = np.ones(len(sims), dtype=bool)
    pool[focal_idx] = False
    if restrict_same_industry_d and str(focal_row["industry_d"]).strip():
        pool &= companies["industry_d"].astype(str).eq(str(focal_row["industry_d"]).strip()).to_numpy()
    idx = np.where(pool)[0]
    if len(idx) == 0:
        return np.array([], dtype=int)
    pool_sims = sims[idx]
    keep = min(top_n, len(idx))
    local = np.argpartition(-pool_sims, np.arange(keep))[:keep]
    out = idx[local]
    return out[np.argsort(-sims[out])]


def same_nonempty(a: object, b: object) -> int:
    aa = str(a).strip()
    bb = str(b).strip()
    return int(bool(aa) and aa == bb)


def vectorize_year(companies: pd.DataFrame, method: str, product_vocab: set[str]) -> sparse.csr_matrix:
    texts = companies["business_text"].fillna("").astype(str).map(strip_ai_terms).tolist()
    if method == "ren_wang_binary":
        vectorizer = CountVectorizer(
            tokenizer=lambda x: tokenize(x),
            token_pattern=None,
            lowercase=False,
            binary=True,
            min_df=3,
            max_df=0.50,
            max_features=12000,
            dtype=np.float32,
        )
    elif method == "liu_product_tfidf":
        vectorizer = TfidfVectorizer(
            tokenizer=lambda x: tokenize(x, product_vocab=product_vocab),
            token_pattern=None,
            lowercase=False,
            min_df=2,
            max_df=0.80,
            sublinear_tf=True,
            norm="l2",
            dtype=np.float32,
        )
    else:
        raise ValueError(f"Unknown method: {method}")
    mat = vectorizer.fit_transform(texts)
    return normalize(mat, norm="l2", copy=False).tocsr()


def build_network_for_year(
    text_df: pd.DataFrame,
    focal_codes: Iterable[str],
    report_year: int,
    method: str,
    product_vocab: set[str],
    top_n: int,
    restrict_same_industry_d: bool,
) -> pd.DataFrame:
    companies = text_df[text_df["report_year"].eq(report_year)].copy()
    companies = companies[companies["business_text"].fillna("").str.len().ge(500)].copy()
    companies = companies.drop_duplicates("stock_code", keep="last").reset_index(drop=True)
    if companies.empty:
        return pd.DataFrame()

    mat = vectorize_year(companies, method, product_vocab)
    if mat.shape[1] == 0:
        return pd.DataFrame()
    code_to_idx = {code: i for i, code in enumerate(companies["stock_code"].astype(str))}
    valid_codes = [c for c in sorted(set(map(code6, focal_codes))) if c in code_to_idx]
    if not valid_codes:
        return pd.DataFrame()

    focal_indices = np.array([code_to_idx[c] for c in valid_codes], dtype=int)
    sim_block = (mat[focal_indices] @ mat.T).toarray()

    rows: list[dict[str, object]] = []
    for row_pos, focal_code in enumerate(valid_codes):
        focal_idx = code_to_idx[focal_code]
        sims = sim_block[row_pos].copy()
        sims[focal_idx] = -np.inf
        top_idx = choose_top_indices(sims, companies, focal_idx, top_n, restrict_same_industry_d)
        focal = companies.iloc[focal_idx]
        for rank, peer_idx in enumerate(top_idx, start=1):
            peer = companies.iloc[int(peer_idx)]
            sim = float(sims[int(peer_idx)])
            if not math.isfinite(sim):
                continue
            rows.append(
                {
                    "snapshot_report_year": report_year,
                    "peer_method": method,
                    "peer_scope": "same_industry_d" if restrict_same_industry_d else "global",
                    "focal_code": focal_code,
                    "focal_name": focal["company_name"],
                    "focal_industry_c": focal["industry_c"],
                    "focal_industry_d": focal["industry_d"],
                    "peer_rank": rank,
                    "peer_code": peer["stock_code"],
                    "peer_name": peer["company_name"],
                    "peer_industry_c": peer["industry_c"],
                    "peer_industry_d": peer["industry_d"],
                    "product_similarity": sim,
                    "same_industry_c": same_nonempty(focal["industry_c"], peer["industry_c"]),
                    "same_industry_d": same_nonempty(focal["industry_d"], peer["industry_d"]),
                    "focal_text_len": int(focal["text_len"]),
                    "peer_text_len": int(peer["text_len"]),
                    "focal_extracted_mode": focal["extracted_mode"],
                    "peer_extracted_mode": peer["extracted_mode"],
                }
            )
    return pd.DataFrame(rows)


def merge_events(events: pd.DataFrame, network: pd.DataFrame) -> pd.DataFrame:
    if network.empty:
        return pd.DataFrame()
    return events.merge(network, on=["snapshot_report_year", "focal_code"], how="inner")


def build_all(args: argparse.Namespace) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = read_events(args.event_path)
    text_df = pd.read_csv(ANNUAL_TEXT_PATH, dtype={"stock_code": str})
    text_df["stock_code"] = text_df["stock_code"].map(code6)
    text_df = text_df[text_df["report_year"].isin(args.years)].copy()
    text_df["business_text"] = text_df["business_text"].fillna("")
    for col in ["company_name", "industry_c", "industry_d", "MAINBUSSINESS", "BusinessScope"]:
        if col not in text_df.columns:
            text_df[col] = ""
        text_df[col] = text_df[col].fillna("")

    product_vocab = build_product_vocab(text_df)
    (OUT_DIR / "product_vocab.txt").write_text("\n".join(sorted(product_vocab)), encoding="utf-8")

    summary_rows: list[dict[str, object]] = [
        {"item": "annual_text_rows", "value": len(text_df)},
        {"item": "events_rows", "value": len(events)},
        {"item": "product_vocab_size", "value": len(product_vocab)},
    ]
    spec_rows: list[pd.DataFrame] = []
    method_specs = [
        ("ren_wang_binary", False),
        ("ren_wang_binary", True),
        ("liu_product_tfidf", False),
        ("liu_product_tfidf", True),
    ]
    for method, same_industry in method_specs:
        label = f"{method}_{'same_industry_d' if same_industry else 'global'}"
        networks: list[pd.DataFrame] = []
        for year, group in events.groupby("snapshot_report_year"):
            if int(year) not in set(args.years):
                continue
            print(f"[v22] {label} year={year} events={group['event_id'].nunique():,}", flush=True)
            net = build_network_for_year(
                text_df=text_df,
                focal_codes=group["focal_code"],
                report_year=int(year),
                method=method,
                product_vocab=product_vocab,
                top_n=args.top_n,
                restrict_same_industry_d=same_industry,
            )
            if not net.empty:
                networks.append(net)
        network = pd.concat(networks, ignore_index=True) if networks else pd.DataFrame()
        event_peer = merge_events(events, network)
        network_path = OUT_DIR / f"{label}_peer_network_top{args.top_n}.csv"
        event_path = OUT_DIR / f"{label}_peer_event_top{args.top_n}.csv"
        network.to_csv(network_path, index=False, encoding="utf-8-sig")
        event_peer.to_csv(event_path, index=False, encoding="utf-8-sig")
        spec_rows.append(
            pd.DataFrame(
                [
                    {
                        "peer_source": label,
                        "network_rows": len(network),
                        "event_peer_rows": len(event_peer),
                        "events": event_peer["event_id"].nunique() if not event_peer.empty else 0,
                        "focal_firms": event_peer["focal_code"].nunique() if not event_peer.empty else 0,
                        "peer_firms": event_peer["peer_code"].nunique() if not event_peer.empty else 0,
                        "mean_similarity": event_peer["product_similarity"].mean()
                        if not event_peer.empty
                        else np.nan,
                        "median_similarity": event_peer["product_similarity"].median()
                        if not event_peer.empty
                        else np.nan,
                        "same_industry_d_rate": event_peer["same_industry_d"].mean()
                        if not event_peer.empty
                        else np.nan,
                    }
                ]
            )
        )
    spec_summary = pd.concat(spec_rows, ignore_index=True)
    spec_summary.to_csv(OUT_DIR / "network_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(summary_rows).to_csv(OUT_DIR / "sample_summary.csv", index=False, encoding="utf-8-sig")
    print(spec_summary.to_string(index=False), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-path", type=Path, default=DEFAULT_EVENT_PATH)
    parser.add_argument("--years", type=int, nargs="+", default=[2021, 2022, 2023, 2024, 2025])
    parser.add_argument("--top-n", type=int, default=20)
    args = parser.parse_args()
    build_all(args)


if __name__ == "__main__":
    main()
