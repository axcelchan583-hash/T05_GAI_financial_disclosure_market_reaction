#!/usr/bin/env python3
"""First-pass supplemental data diagnostics for the T05 peer event study.

This script uses the current v29 product-peer event-study sample and adds:
1. focal-firm market-model AR/CAR;
2. peer long-window market-model CARs;
3. peer own GenAI event and CSMAR announcement pollution flags.

The goal is diagnostic: identify whether the current negative peer reaction
survives basic pollution screens and whether focal-peer mirror evidence is
directionally consistent with competitive revaluation.
"""

from __future__ import annotations

import math
import re
import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
QIAN_ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05-qian-supplier-replication-cn")
CSMAR_ANN_DIR = Path(
    "/Users/mac/computerscience/第三方资料/04_项目专用资料/"
    "T05_GAI_financial_disclosure_market_reaction/csmar_downloads_20260524"
)

OUT = ROOT / "results/v33_supplement_data_probe_20260605"
DOC = ROOT / "docs/empirical_runs/97_v33_supplement_data_probe_20260605.md"

SAMPLE_PATH = ROOT / "results/v29_pom_style_peer_results_20260605/analysis_sample_used_in_table3.csv"
RETURNS_PATH = ROOT / "results/v6_supplement_market_model_placebo_20260524/stock_returns_with_market_model_params.csv"

STRICT_GENAI_EVENT_PATHS = [
    ROOT / "results/v26_v36_x_peer_retest_20260604/v36_event_samples.csv",
    QIAN_ROOT / "results/v36_candidate_x_supplier_replication_20260604/v36_candidate_x_unique_events.csv",
]

MAJOR_TITLE_RE = re.compile(
    r"年度报告|季度报告|半年度报告|业绩预告|业绩快报|利润分配|权益分派|分红|"
    r"重大资产|资产重组|收购|并购|发行股份|非公开发行|定增|增发|配股|"
    r"可转换公司债|可转债|募集资金|对外投资|重大合同|中标|诉讼|仲裁|"
    r"行政处罚|立案|监管函|问询函|关注函|风险提示|停牌|复牌|"
    r"股票交易异常波动|异动|减持|增持|回购|股权激励|质押|担保|"
    r"关联交易|控制权|实控人|控股股东"
)


def norm_code(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s:
        return None
    if "." in s:
        try:
            s = str(int(float(s)))
        except ValueError:
            pass
    s = re.sub(r"\D", "", s)
    if not s:
        return None
    return s.zfill(6)


def norm_date(x) -> pd.Timestamp | pd.NaT:
    return pd.to_datetime(x, errors="coerce").normalize()


def two_way_cluster_mean(df: pd.DataFrame, y: str) -> dict:
    d = df.dropna(subset=[y, "event_key", "peer_code_norm"]).copy()
    if d.empty:
        return {"nobs": 0, "events": 0, "peer_firms": 0, "mean": np.nan, "se": np.nan, "z": np.nan, "p": np.nan}
    yv = d[y].astype(float)
    X = np.ones((len(d), 1))
    model = sm.OLS(yv, X).fit()
    g0 = pd.factorize(d["event_key"].astype(str))[0]
    g1 = pd.factorize(d["peer_code_norm"].astype(str))[0]
    cov, _, _ = cov_cluster_2groups(model, g0, g1, use_correction=True)
    se = float(np.sqrt(max(cov[0, 0], 0)))
    mean = float(model.params.iloc[0])
    z = mean / se if se else np.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
    return {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d["peer_code_norm"].nunique()),
        "mean": mean,
        "se": se,
        "z": z,
        "p": p,
        "positive_rate": float((yv > 0).mean()),
    }


def two_way_cluster_slope(df: pd.DataFrame, y: str, x: str) -> dict:
    d = df.dropna(subset=[y, x, "event_key", "peer_code_norm"]).copy()
    if d.empty or d[x].nunique() < 2:
        return {"nobs": len(d), "coef": np.nan, "se": np.nan, "z": np.nan, "p": np.nan}
    X = sm.add_constant(d[[x]].astype(float), has_constant="add")
    model = sm.OLS(d[y].astype(float), X).fit()
    g0 = pd.factorize(d["event_key"].astype(str))[0]
    g1 = pd.factorize(d["peer_code_norm"].astype(str))[0]
    cov, _, _ = cov_cluster_2groups(model, g0, g1, use_correction=True)
    se = float(np.sqrt(max(cov[1, 1], 0)))
    coef = float(model.params[x])
    z = coef / se if se else np.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
    return {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d["peer_code_norm"].nunique()),
        "coef": coef,
        "se": se,
        "z": z,
        "p": p,
    }


def hc1_slope(df: pd.DataFrame, y: str, x: str) -> dict:
    d = df.dropna(subset=[y, x]).copy()
    if d.empty or d[x].nunique() < 2:
        return {"nobs": len(d), "coef": np.nan, "se": np.nan, "t": np.nan, "p": np.nan}
    X = sm.add_constant(d[[x]].astype(float), has_constant="add")
    model = sm.OLS(d[y].astype(float), X).fit(cov_type="HC1")
    return {
        "nobs": int(len(d)),
        "coef": float(model.params[x]),
        "se": float(model.bse[x]),
        "t": float(model.tvalues[x]),
        "p": float(model.pvalues[x]),
    }


def load_current_sample() -> pd.DataFrame:
    panel = pd.read_csv(SAMPLE_PATH)
    panel["focal_code_norm"] = panel["focal_code"].map(norm_code)
    panel["peer_code_norm"] = panel["peer_code"].map(norm_code)
    panel["event_dt"] = panel["date_0"].map(norm_date)
    panel["event_date_raw_dt"] = panel["event_date"].map(norm_date)
    return panel


def load_returns(codes: Iterable[str], min_dt: pd.Timestamp, max_dt: pd.Timestamp) -> pd.DataFrame:
    code_set = {str(c).zfill(6) for c in codes if c}
    usecols = ["peer_code", "date", "ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm", "est_obs"]
    chunks = []
    for chunk in pd.read_csv(RETURNS_PATH, usecols=usecols, chunksize=1_500_000):
        chunk["code_norm"] = chunk["peer_code"].map(norm_code)
        chunk = chunk[chunk["code_norm"].isin(code_set)]
        if chunk.empty:
            continue
        chunk["date_dt"] = pd.to_datetime(chunk["date"], errors="coerce")
        chunk = chunk[(chunk["date_dt"] >= min_dt) & (chunk["date_dt"] <= max_dt)]
        if chunk.empty:
            continue
        for c in ["ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm", "est_obs"]:
            chunk[c] = pd.to_numeric(chunk[c], errors="coerce")
        chunk["ar_mm"] = chunk["ret"] - (chunk["alpha_mm"] + chunk["beta_mm"] * chunk["mkt_ret"])
        chunk["valid_ar"] = (
            chunk["ret"].notna()
            & chunk["mkt_ret"].notna()
            & chunk["alpha_mm"].notna()
            & chunk["beta_mm"].notna()
            & chunk["est_obs"].notna()
            & (chunk["trdsta"] == 1)
            & (chunk["limit_status"] == 0)
        )
        chunks.append(chunk[["code_norm", "date_dt", "ar_mm", "valid_ar"]])
    if not chunks:
        return pd.DataFrame(columns=["code_norm", "date_dt", "ar_mm", "valid_ar", "t_ix"])
    ret = pd.concat(chunks, ignore_index=True)
    ret = ret.drop_duplicates(["code_norm", "date_dt"]).sort_values(["code_norm", "date_dt"])
    ret["t_ix"] = ret.groupby("code_norm").cumcount()
    return ret


def build_return_lookup(ret: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        code: g.reset_index(drop=True)
        for code, g in ret.groupby("code_norm", sort=False)
    }


def car_for(lookup: dict[str, pd.DataFrame], code: str | None, event_dt: pd.Timestamp, start: int, end: int) -> tuple[float, int]:
    if not code or pd.isna(event_dt) or code not in lookup:
        return (np.nan, 0)
    g = lookup[code]
    hit = g.index[g["date_dt"].eq(event_dt)]
    if len(hit) == 0:
        return (np.nan, 0)
    base = int(hit[0])
    lo, hi = base + start, base + end
    if lo < 0 or hi >= len(g):
        return (np.nan, 0)
    w = g.iloc[lo : hi + 1]
    need = end - start + 1
    valid = w["valid_ar"].fillna(False)
    if len(w) != need or int(valid.sum()) != need:
        return (np.nan, int(valid.sum()))
    return (float(w["ar_mm"].sum()), int(valid.sum()))


def add_return_windows(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    codes = set(panel["peer_code_norm"].dropna()) | set(panel["focal_code_norm"].dropna())
    min_dt = panel["event_dt"].min() - pd.Timedelta(days=10)
    max_dt = panel["event_dt"].max() + pd.Timedelta(days=130)
    ret = load_returns(codes, min_dt, max_dt)
    lookup = build_return_lookup(ret)

    event_focal = panel[["event_key", "focal_code_norm", "event_dt"]].drop_duplicates("event_key").copy()
    focal_windows = {
        "focal_ar0_mm": (0, 0),
        "focal_car_0_p1_mm": (0, 1),
        "focal_car_m1_p1_mm": (-1, 1),
    }
    for name, (start, end) in focal_windows.items():
        vals = [car_for(lookup, r.focal_code_norm, r.event_dt, start, end) for r in event_focal.itertuples(index=False)]
        event_focal[name] = [v[0] for v in vals]
        event_focal[f"{name}_valid_days"] = [v[1] for v in vals]

    peer_windows = {
        "peer_car_0_p5_mm": (0, 5),
        "peer_car_0_p20_mm": (0, 20),
        "peer_car_0_p60_mm": (0, 60),
    }
    for name, (start, end) in peer_windows.items():
        vals = [car_for(lookup, r.peer_code_norm, r.event_dt, start, end) for r in panel.itertuples(index=False)]
        panel[name] = [v[0] for v in vals]
        panel[f"{name}_valid_days"] = [v[1] for v in vals]

    panel = panel.merge(event_focal.drop(columns=["focal_code_norm", "event_dt"]), on="event_key", how="left")
    coverage = []
    for col in list(focal_windows) + list(peer_windows):
        source = "focal" if col.startswith("focal") else "peer"
        frame = event_focal if source == "focal" else panel
        coverage.append(
            {
                "variable": col,
                "unit": "event" if source == "focal" else "event_peer",
                "nonmissing_rows": int(frame[col].notna().sum()),
                "total_rows": int(len(frame)),
                "coverage": float(frame[col].notna().mean()),
            }
        )
    return panel, pd.DataFrame(coverage)


def load_strict_genai_events() -> pd.DataFrame:
    frames = []
    for p in STRICT_GENAI_EVENT_PATHS:
        if not p.exists():
            continue
        df = pd.read_csv(p)
        code_col = "focal_code" if "focal_code" in df.columns else "stock_code"
        date_col = "event_date" if "event_date" in df.columns else "event_date_str"
        title_col = "announcement_title" if "announcement_title" in df.columns else None
        keep = pd.DataFrame(
            {
                "code_norm": df[code_col].map(norm_code),
                "genai_event_dt": df[date_col].map(norm_date),
                "title": df[title_col].astype(str) if title_col else "",
                "source_file": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
            }
        )
        frames.append(keep)
    if not frames:
        return pd.DataFrame(columns=["code_norm", "genai_event_dt", "title", "source_file"])
    out = pd.concat(frames, ignore_index=True)
    out = out.dropna(subset=["code_norm", "genai_event_dt"]).drop_duplicates(["code_norm", "genai_event_dt", "title"])
    return out


def add_peer_genai_pollution(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    genai = load_strict_genai_events()
    if genai.empty:
        panel["peer_own_strict_genai_m2_p2"] = False
        return panel, genai

    target_pairs = panel[["event_key", "peer_code_norm", "event_dt"]].copy()
    target_pairs["lo"] = target_pairs["event_dt"] - pd.Timedelta(days=2)
    target_pairs["hi"] = target_pairs["event_dt"] + pd.Timedelta(days=2)

    hits = target_pairs.merge(genai, left_on="peer_code_norm", right_on="code_norm", how="left")
    hits = hits[(hits["genai_event_dt"] >= hits["lo"]) & (hits["genai_event_dt"] <= hits["hi"])]
    hit_keys = set(hits["event_key"].astype(str) + "||" + hits["peer_code_norm"].astype(str))
    row_keys = panel["event_key"].astype(str) + "||" + panel["peer_code_norm"].astype(str)
    panel["peer_own_strict_genai_m2_p2"] = row_keys.isin(hit_keys)
    return panel, hits


def iter_security_csvs() -> Iterable[tuple[Path, str]]:
    for zpath in sorted(CSMAR_ANN_DIR.glob("公告证券关联表*.zip")):
        with zipfile.ZipFile(zpath) as zf:
            for name in zf.namelist():
                if name.endswith(".csv") and "ANN_Security" in name:
                    yield zpath, name


def add_announcement_pollution(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    target_codes = set(panel["peer_code_norm"].dropna())
    min_dt = panel["event_dt"].min() - pd.Timedelta(days=2)
    max_dt = panel["event_dt"].max() + pd.Timedelta(days=2)
    hits = []
    usecols = ["AnnouncementID", "DeclareDate", "Title", "Symbol", "SecurityType"]
    for zpath, member in iter_security_csvs():
        with zipfile.ZipFile(zpath) as zf:
            with zf.open(member) as f:
                for chunk in pd.read_csv(
                    f,
                    usecols=lambda c: c in usecols,
                    dtype={
                        "AnnouncementID": str,
                        "DeclareDate": str,
                        "Title": str,
                        "Symbol": str,
                        "SecurityType": str,
                    },
                    chunksize=500_000,
                    encoding="utf-8-sig",
                ):
                    if "Symbol" not in chunk.columns or "DeclareDate" not in chunk.columns:
                        continue
                    chunk["peer_code_norm"] = chunk["Symbol"].map(norm_code)
                    chunk = chunk[chunk["peer_code_norm"].isin(target_codes)]
                    if chunk.empty:
                        continue
                    chunk["declare_dt"] = chunk["DeclareDate"].map(norm_date)
                    chunk = chunk[(chunk["declare_dt"] >= min_dt) & (chunk["declare_dt"] <= max_dt)]
                    if chunk.empty:
                        continue
                    chunk["major_title_flag"] = chunk["Title"].astype(str).str.contains(MAJOR_TITLE_RE)
                    chunk["source_zip"] = zpath.name
                    hits.append(chunk)
    ann = pd.concat(hits, ignore_index=True) if hits else pd.DataFrame(columns=usecols + ["peer_code_norm", "declare_dt", "major_title_flag", "source_zip"])
    if ann.empty:
        panel["peer_any_announcement_m2_p2"] = False
        panel["peer_major_announcement_m2_p2"] = False
        return panel, ann

    target = panel[["event_key", "peer_code_norm", "event_dt"]].copy()
    target["lo"] = target["event_dt"] - pd.Timedelta(days=2)
    target["hi"] = target["event_dt"] + pd.Timedelta(days=2)
    merged = target.merge(ann, on="peer_code_norm", how="left")
    merged = merged[(merged["declare_dt"] >= merged["lo"]) & (merged["declare_dt"] <= merged["hi"])]
    merged["row_key"] = merged["event_key"].astype(str) + "||" + merged["peer_code_norm"].astype(str)
    any_keys = set(merged["row_key"])
    major_keys = set(merged.loc[merged["major_title_flag"].fillna(False), "row_key"])

    row_keys = panel["event_key"].astype(str) + "||" + panel["peer_code_norm"].astype(str)
    panel["peer_any_announcement_m2_p2"] = row_keys.isin(any_keys)
    panel["peer_major_announcement_m2_p2"] = row_keys.isin(major_keys)
    return panel, merged


def sample_tests(panel: pd.DataFrame) -> pd.DataFrame:
    samples = {
        "all_v29_table3": pd.Series(True, index=panel.index),
        "drop_peer_own_strict_genai_m2_p2": ~panel["peer_own_strict_genai_m2_p2"].fillna(False),
        "drop_peer_major_announcement_m2_p2": ~panel["peer_major_announcement_m2_p2"].fillna(False),
        "drop_peer_any_announcement_m2_p2": ~panel["peer_any_announcement_m2_p2"].fillna(False),
        "drop_peer_genai_or_major_announcement": ~(panel["peer_own_strict_genai_m2_p2"].fillna(False) | panel["peer_major_announcement_m2_p2"].fillna(False)),
    }
    outcomes = ["peer_ar0_mm", "peer_ar_p1_mm", "peer_car_0_p1_mm", "peer_car_0_p5_mm", "peer_car_0_p20_mm", "peer_car_0_p60_mm"]
    rows = []
    for sname, mask in samples.items():
        d = panel[mask].copy()
        for y in outcomes:
            res = two_way_cluster_mean(d, y)
            rows.append({"sample": sname, "outcome": y, **res})
    return pd.DataFrame(rows)


def sample_flow(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    flags = [
        "peer_own_strict_genai_m2_p2",
        "peer_any_announcement_m2_p2",
        "peer_major_announcement_m2_p2",
    ]
    rows.append({"metric": "base_rows", "value": len(panel)})
    rows.append({"metric": "base_events", "value": panel["event_key"].nunique()})
    rows.append({"metric": "base_peer_firms", "value": panel["peer_code_norm"].nunique()})
    for f in flags:
        rows.append({"metric": f"{f}_rows", "value": int(panel[f].sum())})
        rows.append({"metric": f"{f}_share", "value": float(panel[f].mean())})
        rows.append({"metric": f"{f}_events", "value": int(panel.loc[panel[f], "event_key"].nunique())})
    both = panel["peer_own_strict_genai_m2_p2"].fillna(False) | panel["peer_major_announcement_m2_p2"].fillna(False)
    rows.append({"metric": "genai_or_major_rows", "value": int(both.sum())})
    rows.append({"metric": "genai_or_major_share", "value": float(both.mean())})
    return pd.DataFrame(rows)


def mirror_tests(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    event_level = panel.groupby("event_key", as_index=False).agg(
        focal_code_norm=("focal_code_norm", "first"),
        event_dt=("event_dt", "first"),
        focal_car_0_p1_mm=("focal_car_0_p1_mm", "first"),
        focal_ar0_mm=("focal_ar0_mm", "first"),
        mean_peer_car_0_p1_mm=("peer_car_0_p1_mm", "mean"),
        mean_peer_ar0_mm=("peer_ar0_mm", "mean"),
        n_peers=("peer_code_norm", "nunique"),
    )
    rows = []
    for y, x in [
        ("mean_peer_car_0_p1_mm", "focal_car_0_p1_mm"),
        ("mean_peer_ar0_mm", "focal_ar0_mm"),
    ]:
        rows.append({"unit": "event_mean_peer", "outcome": y, "regressor": x, **hc1_slope(event_level, y, x)})
    for y, x in [
        ("peer_car_0_p1_mm", "focal_car_0_p1_mm"),
        ("peer_ar0_mm", "focal_ar0_mm"),
    ]:
        rows.append({"unit": "event_peer_rows", "outcome": y, "regressor": x, **two_way_cluster_slope(panel, y, x)})
    return pd.DataFrame(rows), event_level


def write_doc(flow: pd.DataFrame, coverage: pd.DataFrame, tests: pd.DataFrame, mirror: pd.DataFrame, ann: pd.DataFrame, genai_hits: pd.DataFrame) -> None:
    def md_table(df: pd.DataFrame, cols: list[str] | None = None, n: int | None = None) -> str:
        d = df.copy()
        if cols:
            d = d[cols]
        if n:
            d = d.head(n)
        return d.to_markdown(index=False)

    key_tests = tests[
        tests["outcome"].isin(["peer_ar0_mm", "peer_ar_p1_mm", "peer_car_0_p1_mm", "peer_car_0_p20_mm", "peer_car_0_p60_mm"])
    ].copy()
    for col in ["mean", "se", "z", "p", "positive_rate"]:
        if col in key_tests:
            key_tests[col] = key_tests[col].astype(float).round(6)
    mirror2 = mirror.copy()
    for col in ["coef", "se", "z", "t", "p"]:
        if col in mirror2:
            mirror2[col] = pd.to_numeric(mirror2[col], errors="coerce").round(6)
    coverage2 = coverage.copy()
    coverage2["coverage"] = coverage2["coverage"].round(4)

    lines = [
        "# v33 supplemental data probe",
        "",
        "## Scope",
        "",
        "- Input sample: v29 Table 3 sample, `combined_first_event_per_firm` and `liu_product_tfidf_same_industry_d_top10`.",
        "- Additions: focal CAR, peer long-window CAR, peer own strict GenAI event flag, and CSMAR announcement pollution flags.",
        "- This is a diagnostic pass, not the final cleaned main table.",
        "",
        "## Sample Flow and Pollution Flags",
        "",
        md_table(flow),
        "",
        "## Return-Window Coverage",
        "",
        md_table(coverage2),
        "",
        "## Cleaned Event-Study Tests",
        "",
        md_table(
            key_tests,
            ["sample", "outcome", "nobs", "events", "peer_firms", "mean", "se", "z", "p", "positive_rate"],
        ),
        "",
        "## Focal-Peer Mirror Tests",
        "",
        md_table(mirror2),
        "",
        "## Announcement Hit Examples",
        "",
    ]
    if ann.empty:
        lines.append("No CSMAR announcement hits found in the event windows.")
    else:
        ex = ann.drop_duplicates(["event_key", "peer_code_norm", "AnnouncementID"]).copy()
        ex = ex.sort_values(["event_key", "peer_code_norm", "declare_dt"]).head(20)
        keep_cols = [c for c in ["event_key", "peer_code_norm", "declare_dt", "Title", "major_title_flag"] if c in ex.columns]
        lines.append(md_table(ex, keep_cols))
    lines += [
        "",
        "## Peer Own GenAI Hit Examples",
        "",
    ]
    if genai_hits.empty:
        lines.append("No peer own strict GenAI hits found in the event windows.")
    else:
        ex = genai_hits.drop_duplicates(["event_key", "peer_code_norm", "genai_event_dt", "title"]).head(20)
        keep_cols = [c for c in ["event_key", "peer_code_norm", "genai_event_dt", "title"] if c in ex.columns]
        lines.append(md_table(ex, keep_cols))
    lines += [
        "",
        "## Output Files",
        "",
        "- `results/v33_supplement_data_probe_20260605/panel_with_supplement_flags.csv.gz`",
        "- `results/v33_supplement_data_probe_20260605/sample_flow.csv`",
        "- `results/v33_supplement_data_probe_20260605/return_window_coverage.csv`",
        "- `results/v33_supplement_data_probe_20260605/cleaned_event_study_tests.csv`",
        "- `results/v33_supplement_data_probe_20260605/focal_peer_mirror_tests.csv`",
        "- `results/v33_supplement_data_probe_20260605/event_level_mirror_panel.csv`",
        "- `results/v33_supplement_data_probe_20260605/peer_announcement_window_hits.csv.gz`",
        "- `results/v33_supplement_data_probe_20260605/peer_own_genai_window_hits.csv`",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = load_current_sample()
    panel, coverage = add_return_windows(panel)
    panel, genai_hits = add_peer_genai_pollution(panel)
    panel, ann_hits = add_announcement_pollution(panel)

    flow = sample_flow(panel)
    tests = sample_tests(panel)
    mirror, event_level = mirror_tests(panel)

    panel.to_csv(OUT / "panel_with_supplement_flags.csv.gz", index=False, compression="gzip")
    flow.to_csv(OUT / "sample_flow.csv", index=False)
    coverage.to_csv(OUT / "return_window_coverage.csv", index=False)
    tests.to_csv(OUT / "cleaned_event_study_tests.csv", index=False)
    mirror.to_csv(OUT / "focal_peer_mirror_tests.csv", index=False)
    event_level.to_csv(OUT / "event_level_mirror_panel.csv", index=False)
    ann_hits.to_csv(OUT / "peer_announcement_window_hits.csv.gz", index=False, compression="gzip")
    genai_hits.to_csv(OUT / "peer_own_genai_window_hits.csv", index=False)
    write_doc(flow, coverage, tests, mirror, ann_hits, genai_hits)

    print(f"wrote {OUT}")
    print(flow.to_string(index=False))
    print(tests[tests["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm", "peer_car_0_p20_mm", "peer_car_0_p60_mm"])].to_string(index=False))
    print(mirror.to_string(index=False))


if __name__ == "__main__":
    main()
