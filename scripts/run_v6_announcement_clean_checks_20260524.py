#!/usr/bin/env python3
"""Announcement-contamination checks for the v6 market-reaction design.

This script uses the CSMAR announcement downloads added on 2026-05-24 to build
stock-day announcement flags, then reruns the v6 market-model CAR tests after
excluding focal/peer observations contaminated by periodic, earnings, material,
or stock-price-risk announcements.
"""

from __future__ import annotations

import csv
import gzip
import io
import math
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
ANN_DIR = Path(
    "/Users/mac/computerscience/第三方资料/04_项目专用资料/"
    "T05_GAI_financial_disclosure_market_reaction/csmar_downloads_20260524"
)
BASE_DIR = ROOT / "results" / "v6_supplement_market_model_placebo_20260524"
OUT_DIR = ROOT / "results" / "v6_announcement_clean_checks_20260524"

TRUE_PANEL = BASE_DIR / "true_peer_market_model_car_panel.csv"
PLACEBO_PANEL = BASE_DIR / "placebo_peer_market_model_car_panel.csv"

OUTCOMES = ["peer_car_0_p1_mm", "peer_car_m1_p1_mm"]
BIT_PERIODIC = 1
BIT_EARNINGS = 2
BIT_MATERIAL = 4
BIT_PRICE_RISK = 8
BIT_IR = 16


PERIODIC_PAT = re.compile(
    r"年度报告|半年度报告|季度报告|一季度报告|三季度报告|第一季度报告|第三季度报告|"
    r"定期报告|年报|中报|半年报|一季报|三季报"
)
EARNINGS_PAT = re.compile(r"业绩预告|业绩快报|盈利预测|业绩修正|业绩预增|业绩预减|业绩补偿")
MATERIAL_PAT = re.compile(
    r"重大资产|资产重组|重组|收购|出售资产|对外投资|重大合同|担保|关联交易|"
    r"重大诉讼|仲裁|股权激励|股份质押|股份冻结|减持|增持|回购|发行股份|"
    r"非公开发行|定向增发|可转换公司债券|可转债|停牌|复牌|控制权|实际控制人|"
    r"权益变动|要约收购|吸收合并|分立|破产|清算|重大事项"
)
PRICE_RISK_PAT = re.compile(r"股票交易异常波动|严重异常波动|异常波动|风险提示|退市风险|其他风险警示")
IR_PAT = re.compile(r"调研活动|投资者关系|投资者交流|业绩说明会")


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def text_mask(text: str) -> int:
    text = text or ""
    mask = 0
    if PERIODIC_PAT.search(text):
        mask |= BIT_PERIODIC
    if EARNINGS_PAT.search(text):
        mask |= BIT_EARNINGS
    if MATERIAL_PAT.search(text):
        mask |= BIT_MATERIAL
    if PRICE_RISK_PAT.search(text):
        mask |= BIT_PRICE_RISK
    if IR_PAT.search(text):
        mask |= BIT_IR
    return mask


def iter_zip_csv(prefix: str):
    for zpath in sorted(ANN_DIR.glob(f"{prefix}*.zip")):
        with zipfile.ZipFile(zpath) as zf:
            for member in zf.namelist():
                if not member.lower().endswith(".csv"):
                    continue
                with zf.open(member) as bf:
                    wrapper = io.TextIOWrapper(bf, encoding="utf-8-sig", newline="")
                    yield zpath.name, member, csv.DictReader(wrapper)


def build_announcement_stock_day_flags(refresh: bool = False) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / "announcement_stock_day_flags_2023_2026.csv.gz"
    if cache.exists() and not refresh:
        return pd.read_csv(cache, dtype={"stock_code": str})

    print("Aggregating announcement classification flags...", flush=True)
    ann_mask: dict[str, int] = defaultdict(int)
    class_rows = 0
    for _, _, reader in iter_zip_csv("公告分类关联表"):
        for row in reader:
            ann_id = (row.get("AnnouncementID") or "").strip()
            if not ann_id:
                continue
            ann_mask[ann_id] |= text_mask(
                f"{row.get('ClassifyName') or ''} {row.get('Title') or ''}"
            )
            class_rows += 1

    print("Aggregating A-share stock-day announcement flags...", flush=True)
    stock_day: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    security_rows = 0
    ashare_rows = 0
    for _, _, reader in iter_zip_csv("公告证券关联表"):
        for row in reader:
            security_rows += 1
            if (row.get("SecurityType") or "").strip() != "A股":
                continue
            code = code6(row.get("Symbol"))
            date = (row.get("DeclareDate") or "")[:10]
            ann_id = (row.get("AnnouncementID") or "").strip()
            if not code or not date:
                continue
            ashare_rows += 1
            mask = ann_mask.get(ann_id, 0) | text_mask(row.get("Title") or "")
            vals = stock_day[(code, date)]
            vals[0] += 1
            vals[1] += int(bool(mask & BIT_PERIODIC))
            vals[2] += int(bool(mask & BIT_EARNINGS))
            vals[3] += int(bool(mask & BIT_MATERIAL))
            vals[4] += int(bool(mask & BIT_PRICE_RISK))
            vals[5] += int(bool(mask & BIT_IR))

    rows = []
    for (code, date), vals in stock_day.items():
        any_count, periodic, earnings, material, price_risk, ir = vals
        rows.append(
            {
                "stock_code": code,
                "declare_date": date,
                "ann_any_count": any_count,
                "ann_periodic_count": periodic,
                "ann_earnings_count": earnings,
                "ann_material_count": material,
                "ann_price_risk_count": price_risk,
                "ann_ir_count": ir,
                "ann_cleaning_count": periodic + earnings + material + price_risk,
            }
        )
    out = pd.DataFrame(rows).sort_values(["stock_code", "declare_date"])
    out.to_csv(cache, index=False, compression="gzip")

    meta = pd.DataFrame(
        [
            {
                "class_rows_read": class_rows,
                "security_rows_read": security_rows,
                "a_share_security_rows": ashare_rows,
                "stock_day_rows": len(out),
                "first_date": out["declare_date"].min(),
                "last_date": out["declare_date"].max(),
                "stock_codes": out["stock_code"].nunique(),
            }
        ]
    )
    meta.to_csv(OUT_DIR / "announcement_stock_day_flags_summary.csv", index=False)
    return out


def load_panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    true = pd.read_csv(TRUE_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    placebo = pd.read_csv(
        PLACEBO_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str}
    )
    for df in [true, placebo]:
        df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
        for col in ["date_m1", "date_0", "date_p1"]:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        df["focal_code"] = df["focal_code"].map(code6)
        df["peer_code"] = df["peer_code"].map(code6)
        df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
        df["peer_industry_d"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str)
        df["peer_industry_week"] = df["peer_industry_d"] + "|" + df["event_week"].fillna("")
    return true, placebo


def attach_announcement_flags(panel: pd.DataFrame, flags: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    flag_cols = [
        "ann_any_count",
        "ann_periodic_count",
        "ann_earnings_count",
        "ann_material_count",
        "ann_price_risk_count",
        "ann_ir_count",
        "ann_cleaning_count",
    ]
    lookup = flags.set_index(["stock_code", "declare_date"])[flag_cols]

    def count_for(code_s: pd.Series, date_s: pd.Series, prefix: str) -> None:
        idx = pd.MultiIndex.from_arrays(
            [code_s.astype(str), pd.to_datetime(date_s, errors="coerce").dt.strftime("%Y-%m-%d")]
        )
        vals = lookup.reindex(idx).reset_index(drop=True).fillna(0)
        for col in flag_cols:
            out[f"{prefix}_{col}"] = vals[col].astype(int).to_numpy()

    count_for(out["focal_code"], out["event_date"], "focal_event_date")
    count_for(out["focal_code"], out["date_0"], "focal_trading0")
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        count_for(out["peer_code"], out[date_col], f"peer_{suffix}")

    for col in flag_cols:
        out[f"peer_m1_p1_{col}"] = (
            out[f"peer_m1_{col}"] + out[f"peer_0_{col}"] + out[f"peer_p1_{col}"]
        )
        out[f"focal_event_or_0_{col}"] = (
            out[f"focal_event_date_{col}"] + out[f"focal_trading0_{col}"]
        )

    out["peer_cleaning_ann_m1_p1"] = (out["peer_m1_p1_ann_cleaning_count"] > 0).astype(int)
    out["focal_cleaning_ann_event_or_0"] = (
        out["focal_event_or_0_ann_cleaning_count"] > 0
    ).astype(int)
    out["either_cleaning_ann"] = (
        out["peer_cleaning_ann_m1_p1"].eq(1) | out["focal_cleaning_ann_event_or_0"].eq(1)
    ).astype(int)
    out["peer_any_ann_m1_p1"] = (out["peer_m1_p1_ann_any_count"] > 0).astype(int)
    out["focal_any_ann_event_or_0"] = (out["focal_event_or_0_ann_any_count"] > 0).astype(int)
    return out


def base_clean_sample(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        (df["is_first_focal_event"].eq(1))
        & (df["obs_peer_car_m1_p1_mm"].eq(3))
        & (df["normal_trading_m1_p1"].eq(1))
        & (df["no_limit_m1_p1"].eq(1))
        & df["alpha_mm"].notna()
        & df["beta_mm"].notna()
    ].copy()


def absorb_fixed_effects(data: pd.DataFrame, cols: list[str], fe_cols: list[str]) -> pd.DataFrame:
    arr = data[cols].astype(float).to_numpy(copy=True)
    codes = [pd.Categorical(data[fe]).codes for fe in fe_cols]
    for _ in range(30):
        old = arr.copy()
        for code in codes:
            tmp = pd.DataFrame(arr, columns=cols)
            tmp["_fe"] = code
            arr -= tmp.groupby("_fe", sort=False)[cols].transform("mean").to_numpy()
        if np.nanmax(np.abs(arr - old)) < 1e-10:
            break
    out = data[["event_id", "peer_code"]].copy()
    for idx, col in enumerate(cols):
        out[col] = arr[:, idx]
    return out


def fit_absorbed_model(
    data: pd.DataFrame, outcome: str, xvars: list[str], fe_cols: list[str]
) -> list[dict[str, object]]:
    d = data.dropna(subset=[outcome, *xvars, "event_id", "peer_code", *fe_cols]).copy()
    if d.empty:
        return []
    dm = absorb_fixed_effects(d, [outcome, *xvars], fe_cols)
    model = sm.OLS(dm[outcome].to_numpy(), dm[xvars].to_numpy()).fit()
    cov_two, _, _ = cov_cluster_2groups(
        model, pd.Categorical(dm["event_id"]).codes, pd.Categorical(dm["peer_code"]).codes
    )
    se = np.sqrt(np.diag(np.asarray(cov_two)))
    rows = []
    for idx, term in enumerate(xvars):
        z = model.params[idx] / se[idx] if se[idx] > 0 else math.nan
        p = 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan
        rows.append(
            {
                "outcome": outcome,
                "term": term,
                "coef": float(model.params[idx]),
                "se": float(se[idx]),
                "z": float(z),
                "p": float(p),
                "nobs": int(model.nobs),
                "events": int(d["event_id"].nunique()),
                "peer_firms": int(d["peer_code"].nunique()),
                "mean_y": float(d[outcome].mean()),
                "mean_ai_active": float(d["ai_active_peer_tminus5"].mean()),
                "peer_cleaning_ann_rate": float(d["peer_cleaning_ann_m1_p1"].mean()),
                "focal_cleaning_ann_rate": float(d["focal_cleaning_ann_event_or_0"].mean()),
            }
        )
    return rows


def run_models(panel: pd.DataFrame, peer_group: str, top_n: int) -> tuple[list[dict], list[dict]]:
    sample0 = base_clean_sample(panel)
    samples = [
        ("base_no_announcement_filter", sample0),
        (
            "drop_peer_cleaning_ann_m1_p1",
            sample0[sample0["peer_cleaning_ann_m1_p1"].eq(0)].copy(),
        ),
        (
            "drop_focal_cleaning_ann_event_or_0",
            sample0[sample0["focal_cleaning_ann_event_or_0"].eq(0)].copy(),
        ),
        ("drop_either_cleaning_ann", sample0[sample0["either_cleaning_ann"].eq(0)].copy()),
    ]
    fe_specs = [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]
    summaries: list[dict] = []
    regs: list[dict] = []
    for sample_name, sample in samples:
        summaries.append(
            {
                "peer_group": peer_group,
                "top_n": top_n,
                "sample": sample_name,
                "obs": len(sample),
                "events": sample["event_id"].nunique(),
                "focal_firms": sample["focal_code"].nunique(),
                "peer_firms": sample["peer_code"].nunique(),
                "mean_ai_active": sample["ai_active_peer_tminus5"].mean(),
                "mean_peer_cleaning_ann": sample["peer_cleaning_ann_m1_p1"].mean(),
                "mean_focal_cleaning_ann": sample["focal_cleaning_ann_event_or_0"].mean(),
                "mean_car_0_p1_mm": sample["peer_car_0_p1_mm"].mean(),
                "mean_car_m1_p1_mm": sample["peer_car_m1_p1_mm"].mean(),
            }
        )
        for fe_name, fe_cols in fe_specs:
            for outcome in OUTCOMES:
                for row in fit_absorbed_model(
                    sample, outcome, ["ai_active_peer_tminus5", "specz_ai_active"], fe_cols
                ):
                    row.update(
                        {
                            "peer_group": peer_group,
                            "top_n": top_n,
                            "sample": sample_name,
                            "fe_spec": fe_name,
                            "model": "M1_specz_x_ai_active",
                        }
                    )
                    regs.append(row)
    return summaries, regs


def run_true_vs_low_difference(true: pd.DataFrame, low: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    true5 = true[true["peer_rank"].le(5)].copy()
    low10 = low.copy()
    true5["is_true_peer"] = 1
    low10["is_true_peer"] = 0
    combined = pd.concat([true5, low10], ignore_index=True, sort=False)
    combined["ai_active_true"] = combined["ai_active_peer_tminus5"] * combined["is_true_peer"]
    combined["specz_ai_active_true"] = combined["specz_ai_active"] * combined["is_true_peer"]

    sample0 = base_clean_sample(combined)
    samples = [
        ("base_no_announcement_filter", sample0),
        (
            "drop_peer_cleaning_ann_m1_p1",
            sample0[sample0["peer_cleaning_ann_m1_p1"].eq(0)].copy(),
        ),
        (
            "drop_focal_cleaning_ann_event_or_0",
            sample0[sample0["focal_cleaning_ann_event_or_0"].eq(0)].copy(),
        ),
        ("drop_either_cleaning_ann", sample0[sample0["either_cleaning_ann"].eq(0)].copy()),
    ]
    fe_specs = [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]
    xvars = [
        "ai_active_peer_tminus5",
        "specz_ai_active",
        "is_true_peer",
        "ai_active_true",
        "specz_ai_active_true",
    ]
    for sample_name, sample in samples:
        for fe_name, fe_cols in fe_specs:
            for outcome in OUTCOMES:
                for row in fit_absorbed_model(sample, outcome, xvars, fe_cols):
                    row.update(
                        {
                            "comparison": "true_top5_vs_low_similarity_same_industry",
                            "sample": sample_name,
                            "fe_spec": fe_name,
                        }
                    )
                    rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    flags = build_announcement_stock_day_flags()
    true, placebo = load_panels()
    true = attach_announcement_flags(true, flags)
    placebo = attach_announcement_flags(placebo, flags)

    true.to_csv(OUT_DIR / "true_peer_market_model_car_panel_with_ann_flags.csv.gz", index=False, compression="gzip")
    placebo.to_csv(
        OUT_DIR / "placebo_peer_market_model_car_panel_with_ann_flags.csv.gz",
        index=False,
        compression="gzip",
    )

    all_summaries: list[dict] = []
    all_regs: list[dict] = []
    groups = [
        ("true_top5", true[true["peer_rank"].le(5)].copy(), 5),
        ("true_top10", true[true["peer_rank"].le(10)].copy(), 10),
        (
            "low_similarity_same_industry",
            placebo[placebo["peer_group"].eq("low_similarity_same_industry")].copy(),
            10,
        ),
        (
            "random_same_industry_one_draw",
            placebo[placebo["peer_group"].eq("random_same_industry")].copy(),
            10,
        ),
    ]
    for peer_group, panel, top_n in groups:
        summaries, regs = run_models(panel, peer_group, top_n)
        all_summaries.extend(summaries)
        all_regs.extend(regs)

    summary = pd.DataFrame(all_summaries)
    regs = pd.DataFrame(all_regs)
    summary.to_csv(OUT_DIR / "v6_announcement_clean_sample_summary.csv", index=False)
    regs.to_csv(OUT_DIR / "v6_announcement_clean_regressions.csv", index=False)
    low = placebo[placebo["peer_group"].eq("low_similarity_same_industry")].copy()
    diff = run_true_vs_low_difference(true, low)
    diff.to_csv(OUT_DIR / "v6_announcement_clean_true_vs_low_difference.csv", index=False)

    key = regs[
        regs["term"].eq("specz_ai_active")
        & regs["peer_group"].isin(["true_top5", "true_top10", "low_similarity_same_industry"])
        & regs["outcome"].isin(OUTCOMES)
    ].copy()
    diff_key = diff[diff["term"].eq("specz_ai_active_true")].copy()
    print(summary.to_string(index=False), flush=True)
    print(key.to_string(index=False), flush=True)
    print(diff_key.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
