#!/usr/bin/env python3
"""Try alternative peer definitions for the T05 GenAI peer-CAR design.

Peer systems tested:
1. patent/technology peers: lagged fine IPC-section vectors from CSMAR annual
   patent-classification files;
2. common-analyst peers: lagged analyst-coverage vectors from CSMAR analyst
   forecast files;
3. LLM/semantic re-ranked peers: the existing 200-focal code-safe semantic
   re-ranking file.

The outcome and specification are kept close to the current headline design:
PeerCAR[0,+1] on Specificity_z x AIActivePeer, event FE + peer industry-week FE,
two-way clustered by focal event and peer firm.
"""

from __future__ import annotations

import io
import itertools
import math
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    attach_announcement_flags,
    base_clean_sample,
    build_announcement_stock_day_flags,
)
from run_v6_external_ai_active_checks_20260524 import (
    attach_external_flags,
    load_first_dates,
    load_hiring_lookup,
)
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    fit_absorbed,
    load_panel,
    load_stock_model,
    window_sum,
)


TRUE_EXT_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "true_panel_with_external_ai_active.csv.gz"
)
PATENT_FINE_XLSX = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司年报信息/上市公司发明申请专利细分分类号.7z;filename_=上市公司发明申请专利细分分类号/"
    "上市公司发明申请专利细分分类号.xlsx"
)
ANALYST_ZIP = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司财务信息/分析师预测指标文件130441749(仅供四川大学使用).zip"
)
LLM_NETWORK = ROOT / "results" / "v13_peer_validity_gate_20260531" / "llm_semantic_reranked_peer_network_top5_200.csv"

OUT_DIR = ROOT / "results" / "v15_alternative_peer_definitions_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "78_v15_alternative_peer_definitions_20260531.md"

PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
OUTCOME = "peer_car_0_p1_mm"
FE = ["event_id", "peer_industry_week"]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.nan, index=s.index)
    return (x - x.mean()) / sd


def safe_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)
    return out


def topk_cosine_from_vectors(
    df: pd.DataFrame,
    id_col: str,
    year_col: str,
    vector_cols: list[str],
    top_k: int = 10,
    system_name: str = "peer_system",
    min_vector_sum: float = 1.0,
) -> pd.DataFrame:
    rows = []
    try:
        from sklearn.neighbors import NearestNeighbors
    except Exception as exc:  # pragma: no cover - local environment fallback
        raise RuntimeError("scikit-learn is required for nearest-neighbor peer construction") from exc

    d0 = df[[id_col, year_col, *vector_cols]].copy()
    d0[id_col] = d0[id_col].map(code6)
    d0[year_col] = pd.to_numeric(d0[year_col], errors="coerce")
    d0 = d0[d0[id_col].ne("") & d0[year_col].notna()].copy()
    d0 = safe_numeric(d0, vector_cols)
    d0["vector_sum"] = d0[vector_cols].sum(axis=1)
    d0 = d0[d0["vector_sum"].ge(min_vector_sum)].copy()
    for year, sub in d0.groupby(year_col, sort=True):
        sub = sub.drop_duplicates(id_col).reset_index(drop=True)
        if len(sub) <= 2:
            continue
        x = sub[vector_cols].to_numpy(dtype=float)
        k = min(top_k + 1, len(sub))
        nn = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
        nn.fit(x)
        distances, indices = nn.kneighbors(x)
        codes = sub[id_col].to_numpy()
        for i, focal in enumerate(codes):
            rank = 0
            for dist, idx in zip(distances[i], indices[i]):
                peer = codes[idx]
                if peer == focal:
                    continue
                rank += 1
                rows.append(
                    {
                        "peer_source": system_name,
                        "lag_year": int(year),
                        "focal_code": focal,
                        "peer_code": peer,
                        "peer_rank": rank,
                        "peer_similarity": float(1.0 - dist),
                    }
                )
                if rank >= top_k:
                    break
    return pd.DataFrame(rows)


def load_patent_vectors() -> pd.DataFrame:
    cache = OUT_DIR / "patent_fine_vectors.csv.gz"
    if cache.exists():
        return pd.read_csv(cache, dtype={"focal_code": str})
    df = pd.read_excel(PATENT_FINE_XLSX, skiprows=[1, 2])
    df["focal_code"] = df["Scode"].map(code6)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    # Main firm, post-listing application-time rows are closest to a stable
    # listed-firm technology stock. Keep all rows if labels are unexpectedly
    # missing.
    if "Ftyp" in df.columns:
        keep = df["Ftyp"].fillna("").astype(str).str.contains("上市公司本身", regex=False)
        if keep.any():
            df = df[keep].copy()
    if "Aplctm" in df.columns:
        keep = df["Aplctm"].fillna("").astype(str).str.contains("上市后", regex=False)
        if keep.any():
            df = df[keep].copy()
    num_cols = [c for c in df.columns if c.startswith("Inva_") and c.endswith("num")]
    keep_cols = ["focal_code", "Year", *num_cols]
    out = df[keep_cols].copy()
    out = safe_numeric(out, num_cols)
    # Aggregate in case multiple rows per firm-year remain.
    out = out.groupby(["focal_code", "Year"], as_index=False)[num_cols].sum()
    out.to_csv(cache, index=False, compression="gzip")
    return out


def build_patent_peer_network() -> pd.DataFrame:
    cache = OUT_DIR / "patent_technology_peer_network_top10.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype={"focal_code": str, "peer_code": str})
    vec = load_patent_vectors()
    vector_cols = [c for c in vec.columns if c.startswith("Inva_") and c.endswith("num")]
    peers = topk_cosine_from_vectors(
        vec,
        id_col="focal_code",
        year_col="Year",
        vector_cols=vector_cols,
        top_k=10,
        system_name="patent_fine_ipc_lagged",
        min_vector_sum=1,
    )
    peers.to_csv(cache, index=False)
    return peers


def read_analyst_forecasts() -> pd.DataFrame:
    cache = OUT_DIR / "analyst_coverage_code_year_sets.csv.gz"
    if cache.exists():
        return pd.read_csv(cache, dtype={"focal_code": str})
    pieces = []
    with zipfile.ZipFile(ANALYST_ZIP) as zf:
        members = [m for m in zf.namelist() if m.endswith(".xlsx")]
        for member in members:
            data = zf.read(member)
            df = pd.read_excel(
                io.BytesIO(data),
                skiprows=[1, 2],
                usecols=["Stkcd", "DeclareDate", "AnanmID", "InstitutionID"],
            )
            df["focal_code"] = df["Stkcd"].map(code6)
            df["DeclareDate"] = pd.to_datetime(df["DeclareDate"], errors="coerce")
            df = df[df["focal_code"].ne("") & df["DeclareDate"].notna()].copy()
            # Keep years that can be lagged into 2023-2026 events.
            df = df[df["DeclareDate"].dt.year.between(2021, 2025)].copy()
            if df.empty:
                continue
            pieces.append(df[["focal_code", "DeclareDate", "AnanmID", "InstitutionID"]])
    raw = pd.concat(pieces, ignore_index=True).drop_duplicates()
    rows = []
    for _, row in raw.iterrows():
        code = row["focal_code"]
        year = int(row["DeclareDate"].year)
        analyst_ids = str(row["AnanmID"] if pd.notna(row["AnanmID"]) else "").split(",")
        analyst_ids = [a.strip() for a in analyst_ids if re.search(r"\d", a.strip())]
        inst = str(row["InstitutionID"] if pd.notna(row["InstitutionID"]) else "").strip()
        for aid in analyst_ids:
            rows.append({"focal_code": code, "coverage_year": year, "coverage_id": f"A:{aid}"})
        if inst and re.search(r"\d", inst):
            # Brokerage coverage is a fallback signal. It is weaker than analyst
            # identity, so it is kept in a separate source prefix.
            rows.append({"focal_code": code, "coverage_year": year, "coverage_id": f"B:{inst}"})
    out = pd.DataFrame(rows).drop_duplicates()
    out.to_csv(cache, index=False, compression="gzip")
    return out


def build_common_analyst_peer_network() -> pd.DataFrame:
    cache = OUT_DIR / "common_analyst_peer_network_top10.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype={"focal_code": str, "peer_code": str})
    cov = read_analyst_forecasts()
    try:
        from sklearn.preprocessing import MultiLabelBinarizer
        from sklearn.neighbors import NearestNeighbors
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("scikit-learn is required for common-analyst peer construction") from exc

    rows = []
    for year, sub in cov.groupby("coverage_year", sort=True):
        sets = sub.groupby("focal_code")["coverage_id"].agg(lambda x: sorted(set(x))).reset_index()
        if len(sets) <= 2:
            continue
        mlb = MultiLabelBinarizer(sparse_output=True)
        x = mlb.fit_transform(sets["coverage_id"])
        row_sums = np.asarray(x.sum(axis=1)).ravel()
        keep = row_sums > 0
        x = x[keep]
        codes = sets.loc[keep, "focal_code"].to_numpy()
        if len(codes) <= 2:
            continue
        k = min(11, len(codes))
        nn = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
        nn.fit(x)
        distances, indices = nn.kneighbors(x)
        for i, focal in enumerate(codes):
            rank = 0
            for dist, idx in zip(distances[i], indices[i]):
                peer = codes[idx]
                if peer == focal:
                    continue
                sim = float(1.0 - dist)
                if sim <= 0:
                    continue
                rank += 1
                rows.append(
                    {
                        "peer_source": "common_analyst_lagged",
                        "lag_year": int(year),
                        "focal_code": focal,
                        "peer_code": peer,
                        "peer_rank": rank,
                        "peer_similarity": sim,
                    }
                )
                if rank >= 10:
                    break
    out = pd.DataFrame(rows)
    out.to_csv(cache, index=False)
    return out


def load_llm_peer_network() -> pd.DataFrame:
    df = pd.read_csv(LLM_NETWORK, dtype={"focal_code": str, "peer_code": str})
    df["focal_code"] = df["focal_code"].map(code6)
    df["peer_code"] = df["peer_code"].map(code6)
    df = df.rename(columns={"product_similarity": "peer_similarity"})
    df["peer_source"] = "llm_semantic_reranked_200"
    df["lag_year"] = np.nan
    return df[["peer_source", "lag_year", "focal_code", "peer_code", "peer_rank", "peer_similarity"]].copy()


def load_event_base() -> pd.DataFrame:
    panel = load_panel(TRUE_EXT_PANEL)
    cols = [
        "event_id",
        "focal_code",
        "focal_name",
        "focal_industry_d",
        "event_date",
        "date_m1",
        "date_0",
        "date_p1",
        "specificity",
        "specificity_z",
        "is_first_focal_event",
    ]
    ev = panel[cols].drop_duplicates("event_id").copy()
    ev["focal_code"] = ev["focal_code"].map(code6)
    ev["event_date"] = pd.to_datetime(ev["event_date"], errors="coerce")
    ev["lag_year"] = ev["event_date"].dt.year - 1
    return ev


def load_code_info() -> pd.DataFrame:
    panel = load_panel(TRUE_EXT_PANEL)
    f = panel[["focal_code", "focal_name", "focal_industry_d"]].rename(
        columns={"focal_code": "code", "focal_name": "name", "focal_industry_d": "industry_d"}
    )
    p = panel[["peer_code", "peer_name", "peer_industry_d"]].rename(
        columns={"peer_code": "code", "peer_name": "name", "peer_industry_d": "industry_d"}
    )
    info = pd.concat([f, p], ignore_index=True).dropna(subset=["code"])
    info["code"] = info["code"].map(code6)
    info = info[info["code"].ne("")].drop_duplicates("code")
    return info


def build_event_peer_panel(peer_network: pd.DataFrame, source_name: str) -> pd.DataFrame:
    ev = load_event_base()
    if source_name == "llm_semantic_reranked_200":
        d = ev.merge(peer_network, on="focal_code", how="inner")
    else:
        d = ev.merge(peer_network, on=["focal_code", "lag_year"], how="inner")
    d = d[d["peer_code"].ne(d["focal_code"])].copy()
    info = load_code_info()
    d = d.merge(info.rename(columns={"code": "peer_code", "name": "peer_name", "industry_d": "peer_industry_d"}), on="peer_code", how="left")
    d["peer_industry_d"] = d["peer_industry_d"].fillna("UNKNOWN").astype(str)
    d["event_week"] = pd.to_datetime(d["date_0"], errors="coerce").dt.strftime("%Y-%U")
    d["peer_industry_week"] = d["peer_industry_d"] + "|" + d["event_week"].fillna("")
    return d


def attach_returns(panel: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    specs = [
        ("peer_car_0_p1_mm", 0, 1, 2),
        ("peer_car_m1_p1_mm", -1, 1, 3),
        ("peer_car_pre10_m2_mm", -10, -2, 7),
        ("peer_car_pre20_m2_mm", -20, -2, 15),
    ]
    out = panel.copy()
    for name, start, end, min_valid in specs:
        vals, obs, ok = [], [], []
        for code, date0 in zip(out["peer_code"], out["date_0"]):
            v, n, k = window_sum(lookup, code, pd.Timestamp(date0), start, end, min_valid)
            vals.append(v)
            obs.append(n)
            ok.append(k)
        out[name] = vals
        out[f"obs_{name}"] = obs
        out[f"ok_{name}"] = ok
    out["obs_peer_car_m1_p1_mm"] = out["obs_peer_car_m1_p1_mm"]
    out["normal_trading_m1_p1"] = out["ok_peer_car_m1_p1_mm"].ge(3).astype(int)
    out["no_limit_m1_p1"] = out["ok_peer_car_m1_p1_mm"].ge(3).astype(int)
    out["alpha_mm"] = 1.0
    out["beta_mm"] = 1.0
    return out


def attach_ai_flags(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel.copy()
    d["ai_active_peer_tminus5"] = 0
    d = attach_external_flags(d, load_first_dates(), load_hiring_lookup())
    # For newly constructed peer panels, use the externally built historical
    # disclosure date as the text-history flag.
    if "prior_history_genai_disclosure" in d.columns:
        d["current_text_history"] = d["prior_history_genai_disclosure"].fillna(0).astype(int)
    return d


def add_terms(df: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    out = df.copy()
    out["ai"] = out[ai_def].fillna(0).astype(float)
    out["spec_ai"] = out["specificity_z"].astype(float) * out["ai"]
    return out


def run_model(data: pd.DataFrame, ai_def: str, source_name: str, top_n: int) -> dict[str, object]:
    d = data[data["peer_rank"].le(top_n)].copy()
    d = base_clean_sample(d)
    d = d[d["either_cleaning_ann"].eq(0)].copy()
    d = d.dropna(subset=[OUTCOME, *PRE_CONTROLS, "peer_industry_week"])
    d = add_terms(d, ai_def)
    rows = fit_absorbed(
        d,
        OUTCOME,
        ["ai", "spec_ai", *PRE_CONTROLS],
        FE,
        model=f"{source_name}_top{top_n}_{ai_def}",
        term_focus="spec_ai",
    )
    if not rows:
        return {
            "peer_source": source_name,
            "top_n": top_n,
            "ai_def": ai_def,
            "coef": np.nan,
            "se": np.nan,
            "p": np.nan,
            "nobs": 0,
            "events": 0,
            "focal_firms": 0,
            "peer_firms": 0,
            "mean_y": np.nan,
            "mean_ai": np.nan,
        }
    r = rows[0]
    r.update(
        {
            "peer_source": source_name,
            "top_n": top_n,
            "ai_def": ai_def,
            "focal_firms": d["focal_code"].nunique(),
            "mean_ai": d["ai"].mean(),
        }
    )
    return r


def source_summary(panel: pd.DataFrame, source_name: str) -> dict[str, object]:
    return {
        "peer_source": source_name,
        "raw_rows": len(panel),
        "raw_events": panel["event_id"].nunique(),
        "raw_focal_firms": panel["focal_code"].nunique(),
        "raw_peer_firms": panel["peer_code"].nunique(),
        "raw_top5_rows": int(panel["peer_rank"].le(5).sum()),
        "mean_peer_similarity_top5": float(panel.loc[panel["peer_rank"].le(5), "peer_similarity"].mean()),
        "median_peer_similarity_top5": float(panel.loc[panel["peer_rank"].le(5), "peer_similarity"].median()),
    }


def format_table(df: pd.DataFrame, cols: list[str]) -> str:
    out = df[cols].copy()
    for c in ["coef", "se", "p", "mean_y", "mean_ai", "mean_peer_similarity_top5", "median_peer_similarity_top5"]:
        if c in out.columns:
            out[c] = out[c].map(lambda x: "" if pd.isna(x) else f"{float(x):.4f}")
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Building peer networks...", flush=True)
    networks = {
        "patent_fine_ipc_lagged": build_patent_peer_network(),
        "common_analyst_lagged": build_common_analyst_peer_network(),
        "llm_semantic_reranked_200": load_llm_peer_network(),
    }

    lookup = build_return_lookup(load_stock_model())
    flags = build_announcement_stock_day_flags()
    summaries = []
    regs = []
    for name, net in networks.items():
        print(f"Running {name}...", flush=True)
        net.to_csv(OUT_DIR / f"{name}_network_top10.csv", index=False)
        panel = build_event_peer_panel(net, name)
        panel = attach_returns(panel, lookup)
        panel = attach_announcement_flags(panel, flags)
        panel = attach_ai_flags(panel)
        panel.to_csv(OUT_DIR / f"{name}_event_peer_panel.csv.gz", index=False, compression="gzip")
        summaries.append(source_summary(panel, name))
        for top_n in [5, 10]:
            if name == "llm_semantic_reranked_200" and top_n == 10:
                continue
            for ai_def in ["ext_any", "current_text_history", "ext_no_hiring", "ext_plus_history"]:
                regs.append(run_model(panel, ai_def, name, top_n))

    summary = pd.DataFrame(summaries)
    res = pd.DataFrame(regs)
    summary.to_csv(OUT_DIR / "alternative_peer_coverage_summary.csv", index=False)
    res.to_csv(OUT_DIR / "alternative_peer_main_effects.csv", index=False)

    doc = f"""# v15 Alternative Peer Definitions

Date: 2026-05-31

Purpose: try peer definitions with clearer literature support beyond the old
CSMAR scope peer network.

## Peer Systems

1. `patent_fine_ipc_lagged`: lagged fine patent-class vectors. This follows the
   technological-proximity tradition (Jaffe-style technology space; Bloom,
   Schankerman, and Van Reenen-style technology spillovers; Cao, Ma, Tucker, and
   Wan-style technological peer pressure).
2. `common_analyst_lagged`: lagged common analyst / brokerage coverage. This
   follows the common-analyst / information-peer tradition.
3. `llm_semantic_reranked_200`: code-safe semantic re-ranking from the existing
   200-focal LLM/semantic gate.

## Coverage

{format_table(summary, ['peer_source','raw_rows','raw_events','raw_focal_firms','raw_peer_firms','raw_top5_rows','mean_peer_similarity_top5','median_peer_similarity_top5'])}

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

{format_table(res, ['peer_source','top_n','ai_def','coef','se','p','nobs','events','focal_firms','peer_firms','mean_y','mean_ai'])}

## Interpretation

- A usable replacement peer system should have enough event coverage and a
  stable negative coefficient under external `ext_any`.
- A peer system with strong literature support but null main effects is still
  useful as a replacement-test / falsification system, not as the headline peer
  definition.
- If only the old CSMAR scope peer system preserves the negative coefficient,
  the paper must either defend that old system directly or abandon the current
  competitive-risk main-effect framing.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(summary.to_string(index=False), flush=True)
    print(res.to_string(index=False), flush=True)
    print(f"Wrote {OUT_DIR}", flush=True)
    print(f"Wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
