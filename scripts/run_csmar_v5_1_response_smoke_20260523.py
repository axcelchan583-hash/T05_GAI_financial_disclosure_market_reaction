#!/usr/bin/env python3
"""Smoke test for v5.1 using the CSMAR GenAI event library.

Question:
    Does a focal firm's GenAI disclosure make close product-market peers more
    likely to issue their own GenAI disclosure within 30/60/90 days?

This is intentionally lightweight:
- Uses latest CSMAR company business text already prepared by the v4 pilot.
- Builds global Top10 product-market peers with a local char n-gram TF-IDF
  implementation, avoiding external sklearn dependency.
- Runs within-focal-event demeaned OLS as a quick event-FE diagnostic.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVENT_PATH = ROOT / "results" / "csmar_genai_event_library_20260523" / "combined_firm_day_genai_events.csv"
COMPANY_TEXT_PATH = ROOT / "results" / "v4_peer_spillover_x_pilot" / "v4_company_product_text_latest.csv"
OUT_DIR = ROOT / "results" / "csmar_v5_1_response_smoke_20260523"
DOC_OUT = ROOT / "docs" / "empirical_runs" / "39_csmar_v5_1_response_smoke_20260523.md"

DATA_END = pd.Timestamp("2026-05-22")

CONSERVATIVE_TERMS = [
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
    "文生图",
    "文生视频",
    "Sora",
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
    "模型备案",
    "MaaS",
]


def z6(x: object) -> str:
    s = re.sub(r"\.0$", "", str(x or "")).strip()
    s = re.sub(r"\D", "", s)
    return s.zfill(6) if s else ""


def clean_text(x: object) -> str:
    s = str(x or "")
    s = re.sub(r"\s+", "", s)
    return re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9%％（）()、，。；;：:＋+./-]", "", s)


def has_conservative_term(s: object) -> bool:
    text = str(s or "")
    return any(t in text for t in CONSERVATIVE_TERMS)


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
    counts = [char_ngrams(t) for t in companies["product_text"].fillna("")]
    n_docs = len(counts)
    df: Counter[str] = Counter()
    for c in counts:
        df.update(c.keys())

    # Approximate sklearn defaults: remove one-off ngrams and very common ngrams.
    vocab = {term for term, d in df.items() if d >= 2 and d <= 0.85 * n_docs}
    idf = {term: math.log((1 + n_docs) / (1 + df[term])) + 1 for term in vocab}

    vectors: list[dict[str, float]] = []
    postings: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for idx, c in enumerate(counts):
        weights = {term: (1 + math.log(freq)) * idf[term] for term, freq in c.items() if term in vocab and freq > 0}
        norm = math.sqrt(sum(v * v for v in weights.values()))
        if norm > 0:
            weights = {term: val / norm for term, val in weights.items()}
        vectors.append(weights)
        for term, val in weights.items():
            postings[term].append((idx, val))
    return vectors, postings


def build_peer_network(events: pd.DataFrame, companies: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    vectors, postings = build_sparse_tfidf(companies)
    code_to_idx = {code: i for i, code in enumerate(companies["stock_code"])}
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
        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
        focal_row = companies.iloc[focal_idx]
        for rank, (peer_idx, sim) in enumerate(top, start=1):
            peer_row = companies.iloc[peer_idx]
            rows.append(
                {
                    "focal_code": focal_code,
                    "focal_name": focal_row["company_name"],
                    "focal_industry_d": focal_row["industry_d"],
                    "peer_rank": rank,
                    "peer_code": peer_row["stock_code"],
                    "peer_name": peer_row["company_name"],
                    "peer_industry_d": peer_row["industry_d"],
                    "product_similarity": float(sim),
                    "same_industry_d": int(str(focal_row["industry_d"]) == str(peer_row["industry_d"])),
                }
            )
        if k % 250 == 0:
            print(f"built peers for {k}/{len(focal_codes)} focal firms", flush=True)
    return pd.DataFrame(rows)


def load_events() -> pd.DataFrame:
    df = pd.read_csv(EVENT_PATH, dtype={"stock_code": str})
    df["stock_code"] = df["stock_code"].map(z6)
    df["event_date"] = pd.to_datetime(df["event_date_str"], errors="coerce")
    df["specificity"] = pd.to_numeric(df["hope_style_specificity_proxy"], errors="coerce")
    df = df[df["event_date"].notna() & df["stock_code"].ne("")].copy()
    df = df[df["event_date"].ge(pd.Timestamp("2023-01-01"))].copy()
    df = df[df["answer_terms"].map(has_conservative_term)].copy()
    df = df.sort_values(["event_date", "stock_code"]).reset_index(drop=True)
    df["focal_code"] = df["stock_code"]
    df["event_id"] = [
        f"CSMAR{idx + 1:05d}_{row.stock_code}_{row.event_date:%Y%m%d}"
        for idx, row in df.iterrows()
    ]
    return df


def load_companies() -> pd.DataFrame:
    df = pd.read_csv(COMPANY_TEXT_PATH, dtype={"stock_code": str})
    df["stock_code"] = df["stock_code"].map(z6)
    df["product_text"] = df["product_text"].fillna("").map(clean_text)
    df = df[df["stock_code"].ne("") & df["product_text"].str.len().ge(20)].copy()
    return df.drop_duplicates("stock_code").reset_index(drop=True)


def next_event_dates(events: pd.DataFrame) -> dict[str, np.ndarray]:
    out = {}
    for code, g in events.groupby("stock_code"):
        dates = np.array(sorted(pd.to_datetime(g["event_date"]).dt.normalize().unique()), dtype="datetime64[D]")
        out[code] = dates
    return out


def next_after(dates: np.ndarray, event_date: pd.Timestamp) -> pd.Timestamp | pd.NaT:
    if dates.size == 0:
        return pd.NaT
    target = np.datetime64((event_date + pd.Timedelta(days=1)).date())
    pos = np.searchsorted(dates, target, side="left")
    if pos >= len(dates):
        return pd.NaT
    return pd.Timestamp(dates[pos])


def build_panel(events: pd.DataFrame, peers: pd.DataFrame) -> pd.DataFrame:
    panel = events.merge(peers, on="focal_code", how="inner")
    panel = panel[panel["peer_code"].ne(panel["focal_code"])].copy()
    by_peer = next_event_dates(events)
    next_dates = []
    for row in panel.itertuples(index=False):
        next_dates.append(next_after(by_peer.get(row.peer_code, np.array([], dtype="datetime64[D]")), row.event_date))
    panel["next_peer_event_date"] = next_dates
    panel["days_to_peer_event"] = (panel["next_peer_event_date"] - panel["event_date"]).dt.days
    for w in [30, 60, 90]:
        panel[f"full_window_{w}"] = panel["event_date"].le(DATA_END - pd.Timedelta(days=w))
        panel[f"response_{w}"] = panel["days_to_peer_event"].between(1, w, inclusive="both").fillna(False).astype(int)
    return panel


def event_fe_ols(panel: pd.DataFrame, y_col: str, top_n: int) -> dict[str, object]:
    d = panel[panel["peer_rank"].le(top_n) & panel[y_col.replace("response", "full_window")]].copy()
    if d.empty or d[y_col].sum() == 0:
        return {"top_n": top_n, "y": y_col, "obs": len(d), "events": 0, "coef_interaction": np.nan, "t_interaction": np.nan, "p_interaction_norm": np.nan}

    d["similarity_z"] = (d["product_similarity"] - d["product_similarity"].mean()) / d["product_similarity"].std(ddof=0)
    d["specificity_z"] = (d["specificity"] - d["specificity"].mean()) / d["specificity"].std(ddof=0)
    d["x_interaction"] = d["similarity_z"] * d["specificity_z"]

    # Focal-event fixed effects by within-event demeaning.
    for col in [y_col, "similarity_z", "x_interaction"]:
        d[col + "_dm"] = d[col] - d.groupby("event_id")[col].transform("mean")

    y = d[y_col + "_dm"].to_numpy(float)
    x = d[["similarity_z_dm", "x_interaction_dm"]].to_numpy(float)
    valid = np.isfinite(y) & np.isfinite(x).all(axis=1)
    y = y[valid]
    x = x[valid]
    if len(y) <= x.shape[1] + 2:
        return {"top_n": top_n, "y": y_col, "obs": len(y), "events": d["event_id"].nunique(), "coef_interaction": np.nan, "t_interaction": np.nan, "p_interaction_norm": np.nan}

    xtx = x.T @ x
    try:
        inv = np.linalg.inv(xtx)
    except np.linalg.LinAlgError:
        inv = np.linalg.pinv(xtx)
    beta = inv @ (x.T @ y)
    resid = y - x @ beta
    dof = max(1, len(y) - x.shape[1])
    sigma2 = float((resid @ resid) / dof)
    se = np.sqrt(np.diag(inv) * sigma2)
    t = beta / se
    p_norm = [math.erfc(abs(float(v)) / math.sqrt(2)) for v in t]
    return {
        "top_n": top_n,
        "y": y_col,
        "obs": int(len(y)),
        "events": int(d["event_id"].nunique()),
        "focal_firms": int(d["focal_code"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "response_events": int(d[y_col].sum()),
        "response_rate": float(d[y_col].mean()),
        "coef_similarity": float(beta[0]),
        "t_similarity": float(t[0]),
        "p_similarity_norm": float(p_norm[0]),
        "coef_interaction": float(beta[1]),
        "t_interaction": float(t[1]),
        "p_interaction_norm": float(p_norm[1]),
    }


def table(df: pd.DataFrame, max_rows: int = 40) -> str:
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

    events = load_events()
    companies = load_companies()
    print(f"events={len(events)}, firms={events['stock_code'].nunique()}", flush=True)
    print(f"companies={len(companies)}", flush=True)
    peers = build_peer_network(events, companies, top_n=10)
    print(f"peer links={len(peers)}, focal firms={peers['focal_code'].nunique()}", flush=True)
    panel = build_panel(events, peers)

    events.to_csv(OUT_DIR / "csmar_conservative_focal_events_2023_2026.csv", index=False, encoding="utf-8-sig")
    peers.to_csv(OUT_DIR / "csmar_product_peer_network_top10.csv", index=False, encoding="utf-8-sig")
    panel.to_csv(OUT_DIR / "csmar_v5_1_response_panel_top10.csv", index=False, encoding="utf-8-sig")

    summary = []
    for w in [30, 60, 90]:
        for top_n in [5, 10]:
            d = panel[panel["peer_rank"].le(top_n) & panel[f"full_window_{w}"]].copy()
            summary.append(
                {
                    "window": w,
                    "top_n": top_n,
                    "obs": len(d),
                    "focal_events": d["event_id"].nunique(),
                    "focal_firms": d["focal_code"].nunique(),
                    "peer_firms": d["peer_code"].nunique(),
                    "response_events": int(d[f"response_{w}"].sum()) if not d.empty else 0,
                    "response_rate": float(d[f"response_{w}"].mean()) if not d.empty else np.nan,
                }
            )
    summary_df = pd.DataFrame(summary)
    regs = pd.DataFrame([event_fe_ols(panel, f"response_{w}", top_n) for w in [30, 60, 90] for top_n in [5, 10]])
    summary_df.to_csv(OUT_DIR / "csmar_v5_1_response_summary.csv", index=False, encoding="utf-8-sig")
    regs.to_csv(OUT_DIR / "csmar_v5_1_event_fe_ols.csv", index=False, encoding="utf-8-sig")

    qrows = []
    for w in [30, 60, 90]:
        d = panel[panel[f"full_window_{w}"]].copy()
        if d.empty:
            continue
        d["sim_quartile"] = pd.qcut(d["product_similarity"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"], duplicates="drop")
        q = (
            d.groupby("sim_quartile", observed=True)
            .agg(obs=("event_id", "size"), response_rate=(f"response_{w}", "mean"), response_events=(f"response_{w}", "sum"))
            .reset_index()
        )
        q["window"] = w
        qrows.append(q)
    qdf = pd.concat(qrows, ignore_index=True) if qrows else pd.DataFrame()
    qdf.to_csv(OUT_DIR / "csmar_v5_1_response_by_similarity_quartile.csv", index=False, encoding="utf-8-sig")

    report = f"""# CSMAR v5.1 Rival Disclosure Response Smoke Test

日期：2026-05-23

## 口径

焦点事件和竞品响应事件均来自 CSMAR 新事件库，但使用保守 GenAI 词表：

- 只保留 2023-01-01 之后事件；
- 排除单独 `GPT`、单独 `RAG`、单独 `智能体`、单独 `多模态` 这类容易误伤的命中；
- 竞品为 CSMAR 公司业务文本构造的全市场 Top10 文本相似公司。

## 样本

| item | value |
|---|---:|
| conservative focal firm-day events | {len(events)} |
| focal firms | {events['stock_code'].nunique()} |
| companies with product text | {len(companies)} |
| focal firms with peer network | {peers['focal_code'].nunique()} |
| event-peer observations Top10 | {len(panel)} |

## 响应率

{table(summary_df)}

## Event-FE smoke regression

模型为事件固定效应的去均值 OLS：

```text
RivalResponse_ij,t+w = beta1 Similarity_ij + beta2 Specificity_i,t * Similarity_ij + event FE
```

这里的 p 值是普通正态近似，只用于方向诊断，不是正式聚类标准误。

{table(regs)}

## 相似度分组响应率

{table(qdf, max_rows=20)}

## 初步读法

如果 `coef_interaction` 在 30/60/90 天和 Top5/Top10 中稳定为正，才支持 v5.1 的
“越具体的焦点披露越会触发相似竞品跟进披露”。若方向不稳定，说明同源 IIP/IR 文本事件
更可能反映行业 AI-wave 聚集，而不是点对点竞争响应。
"""
    DOC_OUT.write_text(report, encoding="utf-8")
    print(summary_df.to_string(index=False))
    print(regs.to_string(index=False))
    print(f"Wrote {OUT_DIR}")
    print(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
