#!/usr/bin/env python3
"""Build publication-style empirical tables for the two current T05 main effects."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "v25_empirical_table_pack_20260604"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "89_v25_empirical_table_pack_20260604.md"

V24_DIR = ROOT / "results" / "v24_cninfo_specificity_peer_grid_20260604"
PANEL_PATH = V24_DIR / "analysis_panel_with_specificity_ai.csv.gz"
EVENT_PATH = V24_DIR / "event_specificity_measures.csv"
GRID_PATH = V24_DIR / "grid_heterogeneity_regressions.csv"

OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
MAIN_EVENT_DEF = "E2_likely_or_possible"
MAIN_SPEC = "legacy_detail_density"
MAIN_SPEC_RAW = "legacy_detail_density_raw"
MAIN_AI = "ext_any"

SPEC_RAW_COLS = {
    "legacy_detail_density": "legacy_detail_density_raw",
    "genai_concreteness_raw": "genai_concreteness_raw",
    "machine_component_sum": "machine_component_sum",
    "machine_specificity_score": "machine_specificity_score_0_4",
    "auto_action_score": "auto_action_score",
}

VAR_LABELS = {
    "peer_car_0_p1_mm": "PeerCAR[0,+1]",
    "peer_car_pre10_m2_mm": "PeerCAR[-10,-2]",
    "peer_car_pre20_m2_mm": "PeerCAR[-20,-2]",
    "spec_z": "Spec",
    "ai": "AIActive",
    "spec_ai": "Spec x AIActive",
    "peer_rank": "PeerRank",
    "legacy_detail_density_raw": "DetailDensity",
    "current_text_history": "TextHistory",
}


@dataclass(frozen=True)
class MainEffect:
    slug: str
    title: str
    method_variant: str
    peer_note: str
    alt_top_method: str
    same_industry_method: str


MAIN_EFFECTS = [
    MainEffect(
        slug="ren_wang_binary_global_top10",
        title="Ren-Wang binary product peer, global Top10",
        method_variant="ren_wang_binary_global_top10",
        peer_note=(
            "Prior-year Ren-Wang-style binary product-term peer network; "
            "global Top10 peers."
        ),
        alt_top_method="ren_wang_binary_global_top5",
        same_industry_method="ren_wang_binary_same_industry_d_top10",
    ),
    MainEffect(
        slug="liu_product_tfidf_global_top5",
        title="Liu product-TF-IDF peer, global Top5",
        method_variant="liu_product_tfidf_global_top5",
        peer_note=(
            "Prior-year Liu-style product TF-IDF peer network from CSMAR business text; "
            "global Top5 peers."
        ),
        alt_top_method="liu_product_tfidf_global_top10",
        same_industry_method="liu_product_tfidf_same_industry_d_top5",
    ),
]


def code_float(x: object) -> float:
    return float(pd.to_numeric(pd.Series([x]), errors="coerce").iloc[0])


def winsorize(series: pd.Series, lo: float = 0.01, hi: float = 0.99) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    if x.notna().sum() < 10:
        return x
    return x.clip(x.quantile(lo), x.quantile(hi))


def zscore(series: pd.Series) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    std = x.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.nan, index=series.index)
    return (x - x.mean()) / std


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


def event_definition_mask(events: pd.DataFrame, definition: str) -> pd.Series:
    label = events["auto_pdf_label"].fillna("unknown")
    reviewable = ~label.isin(
        [
            "review_denial_or_uncertain",
            "exclude_mention_without_initiative",
            "exclude_no_fulltext_genai",
        ]
    )
    likely_possible = label.isin(["likely_qian_initiative", "review_possible_initiative"])
    likely = label.eq("likely_qian_initiative")
    if definition == "E0_all_1055":
        return pd.Series(True, index=events.index)
    if definition == "E1_reviewable_no_denial":
        return reviewable
    if definition == "E2_likely_or_possible":
        return likely_possible
    if definition == "E3_likely_only":
        return likely
    if definition == "E4_first_likely_or_possible":
        base = likely_possible
    elif definition == "E5_first_reviewable_no_denial":
        base = reviewable
    else:
        raise ValueError(definition)
    tmp = (
        events[base]
        .sort_values(["focal_code", "event_date", "event_id"])
        .drop_duplicates("focal_code")
    )
    return events["event_key"].isin(tmp["event_key"])


def absorb_frame(df: pd.DataFrame, cols: list[str], fe_cols: list[str], iterations: int = 12) -> pd.DataFrame:
    mat = df[cols].astype(float).copy()
    for _ in range(iterations):
        for fe in fe_cols:
            codes = df[fe].fillna("MISSING").astype(str)
            mat = mat - mat.groupby(codes).transform("mean")
    return mat


def cluster_meat(x: np.ndarray, resid: np.ndarray, groups: pd.Series) -> np.ndarray:
    score = pd.DataFrame(x * resid[:, None])
    score["_g"] = groups.fillna("MISSING").astype(str).to_numpy()
    summed = score.groupby("_g").sum().to_numpy()
    return summed.T @ summed


def fit_absorbed_ols(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
    cluster_cols: tuple[str, str] = ("event_key", "peer_code"),
) -> dict[str, object] | None:
    need = [outcome, *xvars, *fe_cols, *cluster_cols, "event_key", "peer_code", "focal_code"]
    d = data.dropna(subset=list(dict.fromkeys(need))).copy()
    if len(d) < 80 or d["event_key"].nunique() < 8 or d["peer_code"].nunique() < 20:
        return None
    dm = absorb_frame(d, [outcome, *xvars], fe_cols)
    y = dm[outcome].to_numpy(dtype=float)
    x = dm[xvars].to_numpy(dtype=float)
    keep = np.nanstd(x, axis=0) > 1e-12
    if not keep.all():
        xvars = [var for var, ok in zip(xvars, keep) if ok]
        x = x[:, keep]
        if x.shape[1] == 0:
            return None
    xtx = x.T @ x
    bread = np.linalg.pinv(xtx)
    beta = bread @ (x.T @ y)
    resid = y - x @ beta
    meat_a = cluster_meat(x, resid, d[cluster_cols[0]])
    meat_b = cluster_meat(x, resid, d[cluster_cols[1]])
    pair_group = d[cluster_cols[0]].astype(str) + "|" + d[cluster_cols[1]].astype(str)
    meat_pair = cluster_meat(x, resid, pair_group)
    cov = bread @ (meat_a + meat_b - meat_pair) @ bread
    within_tss = float(np.sum((y - y.mean()) ** 2))
    rss = float(np.sum(resid**2))
    raw_y = d[outcome].to_numpy(dtype=float)
    overall_tss = float(np.sum((raw_y - raw_y.mean()) ** 2))
    within_r2 = 1.0 - rss / within_tss if within_tss > 0 else math.nan
    overall_r2 = 1.0 - rss / overall_tss if overall_tss > 0 else math.nan
    out: dict[str, object] = {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "focal_firms": int(d["focal_code"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "r2": overall_r2,
        "overall_r2": overall_r2,
        "within_r2": within_r2,
        "fe_cols": ",".join(fe_cols),
    }
    for i, var in enumerate(xvars):
        var_se = math.sqrt(float(cov[i, i])) if float(cov[i, i]) >= 0 else math.nan
        coef = float(beta[i])
        z_value = coef / var_se if var_se and var_se > 0 else math.nan
        out[f"{var}_coef"] = coef
        out[f"{var}_se"] = var_se
        out[f"{var}_z"] = z_value
        out[f"{var}_p"] = p_from_z(z_value)
    return out


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(
        PANEL_PATH,
        dtype={"focal_code": str, "peer_code": str, "event_id": str},
        low_memory=False,
    )
    events = pd.read_csv(EVENT_PATH, dtype={"focal_code": str, "event_id": str}, low_memory=False)
    grid = pd.read_csv(GRID_PATH, low_memory=False)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    panel["event_date"] = pd.to_datetime(panel["event_date"], errors="coerce")
    panel["date_0"] = pd.to_datetime(panel["date_0"], errors="coerce")
    return panel, events, grid


def add_spec_z(panel: pd.DataFrame, events: pd.DataFrame, event_def: str, spec_name: str) -> pd.DataFrame:
    raw_col = SPEC_RAW_COLS[spec_name]
    keys = set(events.loc[event_definition_mask(events, event_def), "event_key"])
    event_sub = events[events["event_key"].isin(keys)].copy()
    event_sub["spec_z"] = zscore(winsorize(event_sub[raw_col]))
    event_sub = event_sub[["event_key", raw_col, "spec_z"]].rename(columns={raw_col: "spec_raw"})
    out = panel[panel["event_key"].isin(keys)].copy()
    out = out.merge(event_sub, on="event_key", how="left")
    return out


def regression_sample(
    panel: pd.DataFrame,
    events: pd.DataFrame,
    event_def: str,
    method_variant: str,
    spec_name: str = MAIN_SPEC,
    ai_def: str = MAIN_AI,
) -> pd.DataFrame:
    d = add_spec_z(panel, events, event_def, spec_name)
    d = d[d["method_variant"].eq(method_variant)].copy()
    d = d[d["time_valid_prior_year"].eq(1)].copy()
    d = d[d["complete_clean_m1_p1"].eq(1)].copy()
    d = d.dropna(
        subset=[
            OUTCOME,
            *PRE_CONTROLS,
            "spec_z",
            ai_def,
            "peer_industry_week",
            "focal_industry_week",
            "event_key",
            "peer_code",
        ]
    ).copy()
    d["ai"] = pd.to_numeric(d[ai_def], errors="coerce").fillna(0.0).astype(float)
    d["spec_ai"] = d["spec_z"] * d["ai"]
    d["legacy_detail_density_raw"] = d["spec_raw"]
    return d


def desc_table(d: pd.DataFrame) -> pd.DataFrame:
    desc_vars = [
        ("PeerCAR[0,+1]", OUTCOME),
        ("DetailDensity", "legacy_detail_density_raw"),
        ("Spec", "spec_z"),
        ("AIActive", "ai"),
        ("Spec x AIActive", "spec_ai"),
        ("PeerCAR[-10,-2]", "peer_car_pre10_m2_mm"),
        ("PeerCAR[-20,-2]", "peer_car_pre20_m2_mm"),
        ("TextHistory", "current_text_history"),
        ("PeerRank", "peer_rank"),
    ]
    rows = []
    for label, col in desc_vars:
        x = pd.to_numeric(d[col], errors="coerce")
        rows.append(
            {
                "变量": label,
                "观测值": int(x.notna().sum()),
                "均值": x.mean(),
                "标准差": x.std(ddof=0),
                "最小值": x.min(),
                "中位数": x.median(),
                "最大值": x.max(),
            }
        )
    return pd.DataFrame(rows)


def baseline_models(d: pd.DataFrame) -> list[dict[str, object]]:
    specs = [
        {
            "col": "(1)",
            "title": "事件固定效应",
            "xvars": ["ai", "spec_ai"],
            "fe": ["event_key"],
            "ai_label": "AIActive",
        },
        {
            "col": "(2)",
            "title": "加入预收益控制",
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key"],
            "ai_label": "AIActive",
        },
        {
            "col": "(3)",
            "title": "Peer行业x周",
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key", "peer_industry_week"],
            "ai_label": "AIActive",
        },
        {
            "col": "(4)",
            "title": "Peer公司固定效应",
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key", "peer_code"],
            "ai_label": "AIActive",
        },
        {
            "col": "(5)",
            "title": "Peer行业周+公司",
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key", "peer_industry_week", "peer_code"],
            "ai_label": "AIActive",
        },
    ]
    rows = []
    for spec in specs:
        res = fit_absorbed_ols(d, OUTCOME, spec["xvars"], spec["fe"])
        rows.append({**spec, **(res or {})})

    d_text = d.copy()
    d_text["ai"] = pd.to_numeric(d_text["current_text_history"], errors="coerce").fillna(0.0).astype(float)
    d_text["spec_ai"] = d_text["spec_z"] * d_text["ai"]
    res_text = fit_absorbed_ols(
        d_text,
        OUTCOME,
        ["ai", "spec_ai", *PRE_CONTROLS],
        ["event_key", "peer_industry_week"],
    )
    rows.append(
        {
            "col": "(6)",
            "title": "替换AI口径",
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key", "peer_industry_week"],
            "ai_label": "TextHistory",
            **(res_text or {}),
        }
    )
    return rows


def robustness_models(panel: pd.DataFrame, events: pd.DataFrame, effect: MainEffect) -> list[dict[str, object]]:
    specs = [
        {
            "col": "(1)",
            "title": "首次事件",
            "event_def": "E4_first_likely_or_possible",
            "method_variant": effect.method_variant,
            "spec_name": MAIN_SPEC,
            "ai_def": MAIN_AI,
        },
        {
            "col": "(2)",
            "title": "Likely only",
            "event_def": "E3_likely_only",
            "method_variant": effect.method_variant,
            "spec_name": MAIN_SPEC,
            "ai_def": MAIN_AI,
        },
        {
            "col": "(3)",
            "title": "替换TopN",
            "event_def": MAIN_EVENT_DEF,
            "method_variant": effect.alt_top_method,
            "spec_name": MAIN_SPEC,
            "ai_def": MAIN_AI,
        },
        {
            "col": "(4)",
            "title": "同行业内peer",
            "event_def": MAIN_EVENT_DEF,
            "method_variant": effect.same_industry_method,
            "spec_name": MAIN_SPEC,
            "ai_def": MAIN_AI,
        },
        {
            "col": "(5)",
            "title": "替换AI口径",
            "event_def": MAIN_EVENT_DEF,
            "method_variant": effect.method_variant,
            "spec_name": MAIN_SPEC,
            "ai_def": "current_text_history",
        },
        {
            "col": "(6)",
            "title": "替换X:文本具体性",
            "event_def": MAIN_EVENT_DEF,
            "method_variant": effect.method_variant,
            "spec_name": "genai_concreteness_raw",
            "ai_def": MAIN_AI,
        },
        {
            "col": "(7)",
            "title": "替换X:机器成分",
            "event_def": MAIN_EVENT_DEF,
            "method_variant": effect.method_variant,
            "spec_name": "machine_component_sum",
            "ai_def": MAIN_AI,
        },
    ]
    rows = []
    for spec in specs:
        d = regression_sample(
            panel,
            events,
            spec["event_def"],
            spec["method_variant"],
            spec["spec_name"],
            spec["ai_def"],
        )
        res = fit_absorbed_ols(
            d,
            OUTCOME,
            ["ai", "spec_ai", *PRE_CONTROLS],
            ["event_key", "peer_industry_week"],
        )
        rows.append({**spec, **(res or {})})
    return rows


def stars(p_value: float) -> str:
    if not np.isfinite(p_value):
        return ""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def fmt_num(value: object, digits: int = 4) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def fmt_coef(row: dict[str, object], var: str) -> str:
    coef = row.get(f"{var}_coef")
    se = row.get(f"{var}_se")
    p_value = row.get(f"{var}_p")
    if coef is None or pd.isna(coef):
        return ""
    return f"{fmt_num(coef)}{stars(code_float(p_value))}"


def fmt_se(row: dict[str, object], var: str) -> str:
    se = row.get(f"{var}_se")
    if se is None or pd.isna(se):
        return ""
    return f"({fmt_num(se)})"


def format_desc(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["均值", "标准差", "最小值", "中位数", "最大值"]:
        out[col] = out[col].map(lambda x: fmt_num(x, 4))
    return out


def regression_table(rows: list[dict[str, object]], include_ai_row: bool = True) -> pd.DataFrame:
    cols = [row["col"] for row in rows]
    title_row = {"变量": ""}
    for row in rows:
        title_row[row["col"]] = row["title"]
    table_rows: list[dict[str, str]] = [title_row]

    for var, label in [("spec_ai", "Spec x AIActive"), ("ai", "AIActive / TextHistory")]:
        if var == "ai" and not include_ai_row:
            continue
        table_rows.append({"变量": label, **{row["col"]: fmt_coef(row, var) for row in rows}})
        table_rows.append({"变量": "", **{row["col"]: fmt_se(row, var) for row in rows}})

    for var in PRE_CONTROLS:
        table_rows.append({"变量": VAR_LABELS[var], **{row["col"]: fmt_coef(row, var) for row in rows}})
        table_rows.append({"变量": "", **{row["col"]: fmt_se(row, var) for row in rows}})

    table_rows.extend(
        [
            {
                "变量": "Event FE",
                **{row["col"]: "YES" if "event_key" in row.get("fe", ["event_key"]) else "NO" for row in rows},
            },
            {
                "变量": "PeerInd x Week FE",
                **{row["col"]: "YES" if "peer_industry_week" in row.get("fe", []) else "NO" for row in rows},
            },
            {
                "变量": "Peer Firm FE",
                **{row["col"]: "YES" if "peer_code" in row.get("fe", []) else "NO" for row in rows},
            },
            {"变量": "N", **{row["col"]: str(row.get("nobs", "")) for row in rows}},
            {"变量": "Events", **{row["col"]: str(row.get("events", "")) for row in rows}},
            {"变量": "Peer firms", **{row["col"]: str(row.get("peer_firms", "")) for row in rows}},
            {"变量": "Overall R2", **{row["col"]: fmt_num(row.get("overall_r2", row.get("r2")), 3) for row in rows}},
            {"变量": "Within R2", **{row["col"]: fmt_num(row.get("within_r2"), 3) for row in rows}},
        ]
    )
    return pd.DataFrame(table_rows, columns=["变量", *cols])


def robustness_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    cols = [row["col"] for row in rows]
    title_row = {"变量": ""}
    for row in rows:
        title_row[row["col"]] = row["title"]
    method_row = {"变量": "Peer/Event/X"}
    for row in rows:
        method_row[row["col"]] = f"{row['event_def']}<br>{row['method_variant']}<br>{row['spec_name']}"
    table_rows: list[dict[str, str]] = [title_row, method_row]
    table_rows.append({"变量": "X x AI proxy", **{row["col"]: fmt_coef(row, "spec_ai") for row in rows}})
    table_rows.append({"变量": "", **{row["col"]: fmt_se(row, "spec_ai") for row in rows}})
    table_rows.extend(
        [
            {"变量": "控制变量", **{row["col"]: "YES" for row in rows}},
            {"变量": "Event FE", **{row["col"]: "YES" for row in rows}},
            {"变量": "PeerInd x Week FE", **{row["col"]: "YES" for row in rows}},
            {"变量": "N", **{row["col"]: str(row.get("nobs", "")) for row in rows}},
            {"变量": "Events", **{row["col"]: str(row.get("events", "")) for row in rows}},
            {"变量": "Peer firms", **{row["col"]: str(row.get("peer_firms", "")) for row in rows}},
            {"变量": "Overall R2", **{row["col"]: fmt_num(row.get("overall_r2", row.get("r2")), 3) for row in rows}},
            {"变量": "Within R2", **{row["col"]: fmt_num(row.get("within_r2"), 3) for row in rows}},
        ]
    )
    return pd.DataFrame(table_rows, columns=["变量", *cols])


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    rows = [
        "| " + " | ".join(df.columns) + " |",
        "|" + "|".join("---" for _ in df.columns) + "|",
    ]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(row[col]) else str(row[col]) for col in df.columns) + " |")
    return "\n".join(rows)


def save_table(df: pd.DataFrame, stem: str) -> str:
    csv_path = OUT_DIR / f"{stem}.csv"
    md_path = OUT_DIR / f"{stem}.md"
    df.to_csv(csv_path, index=False)
    md_path.write_text(markdown_table(df) + "\n", encoding="utf-8")
    return str(csv_path.relative_to(ROOT))


def save_workbook(table_sections: list[dict[str, object]]) -> str | None:
    xlsx_path = OUT_DIR / f"{RUN_ID}.xlsx"
    try:
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            for section in table_sections:
                effect: MainEffect = section["effect"]  # type: ignore[assignment]
                prefix = "Ren" if effect.slug.startswith("ren_") else "Liu"
                sheets = [
                    (f"{prefix}_Table1", section["desc"]),
                    (f"{prefix}_Table2", section["baseline"]),
                    (f"{prefix}_Table3", section["robust"]),
                ]
                for sheet_name, table in sheets:
                    df = table.copy()  # type: ignore[union-attr]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    ws = writer.book[sheet_name]
                    for col in ws.columns:
                        max_len = max(len(str(cell.value or "")) for cell in col)
                        ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 45)
    except Exception as exc:  # pragma: no cover - convenience output only
        print(f"Workbook export skipped: {exc}", flush=True)
        return None
    return str(xlsx_path.relative_to(ROOT))


def sample_flow(panel: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    e2_keys = set(events.loc[event_definition_mask(events, MAIN_EVENT_DEF), "event_key"])
    rows = []
    for effect in MAIN_EFFECTS:
        d0 = panel[panel["method_variant"].eq(effect.method_variant) & panel["event_key"].isin(e2_keys)].copy()
        d1 = d0[d0["time_valid_prior_year"].eq(1)].copy()
        d2 = d1[d1["complete_clean_m1_p1"].eq(1)].copy()
        d3 = d2.dropna(
            subset=[
                OUTCOME,
                *PRE_CONTROLS,
                MAIN_AI,
                "peer_industry_week",
                "focal_industry_week",
            ]
        ).copy()
        top_n = int(pd.to_numeric(d0["method_top_n"], errors="coerce").dropna().mode().iloc[0])
        rows.append(
            {
                "method_variant": effect.method_variant,
                "TopN": top_n,
                "E2_events_total": len(e2_keys),
                "events_with_peer_links": int(d0["event_key"].nunique()),
                "raw_event_peer_rows": int(len(d0)),
                "complete_clean_rows": int(len(d2)),
                "final_regression_N": int(len(d3)),
                "final_events": int(d3["event_key"].nunique()),
                "final_peer_firms": int(d3["peer_code"].nunique()),
                "avg_final_rows_per_event": round(float(len(d3) / d3["event_key"].nunique()), 2),
            }
        )
    return pd.DataFrame(rows)


def write_doc(
    table_sections: list[dict[str, object]],
    grid: pd.DataFrame,
    flow: pd.DataFrame,
    extra_paths: list[str] | None = None,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# v25 empirical table pack: specificity x AI-active peers",
        "",
        "## Scope",
        "",
        "This table pack formats the two currently significant main effects from the v24 specification grid.",
        "Both use `E2_likely_or_possible`, `legacy_detail_density`, `ext_any`, strict prior-year product-market peers, and the outcome `PeerCAR[0,+1]`.",
        "",
        "## v24 Anchor Results",
        "",
    ]
    anchor = grid[
        grid["method_variant"].isin([effect.method_variant for effect in MAIN_EFFECTS])
        & grid["event_def"].eq(MAIN_EVENT_DEF)
        & grid["specificity"].eq(MAIN_SPEC)
        & grid["ai_def"].eq(MAIN_AI)
    ][["method_variant", "coef", "se", "p", "q_bh_all", "nobs", "events", "peer_firms"]].copy()
    for col in ["coef", "se", "p", "q_bh_all"]:
        anchor[col] = anchor[col].map(lambda x: fmt_num(x, 6))
    lines.append(markdown_table(anchor))
    lines.append("")
    lines.extend(
        [
            "## Why the Two Main N's Differ",
            "",
            "`N` is the number of event-peer observations, not the number of GenAI disclosure events.",
            "The Ren-Wang significant specification uses global Top10 peers, while the Liu significant specification uses global Top5 peers; therefore the raw event-peer panel is roughly twice as large for Ren-Wang.",
            "The final event counts are almost the same, so the N gap mainly comes from peer-set size rather than a different event sample.",
            "",
            markdown_table(flow),
            "",
        ]
    )

    for section in table_sections:
        effect: MainEffect = section["effect"]  # type: ignore[assignment]
        lines.extend(
            [
                f"## {effect.title}",
                "",
                f"- Peer construction: {effect.peer_note}",
                "- Main model: `PeerCAR[0,+1] = Spec x AIActivePeer + AIActivePeer + pre-event peer returns + event FE + peer-industry-week FE`.",
                "",
                "### Table 1. 变量的描述性统计",
                "",
                markdown_table(section["desc"]),  # type: ignore[arg-type]
                "",
                "### Table 2. 基准回归检验",
                "",
                markdown_table(section["baseline"]),  # type: ignore[arg-type]
                "",
                "### Table 3. 稳健性检验",
                "",
                markdown_table(section["robust"]),  # type: ignore[arg-type]
                "",
            ]
        )

    lines.extend(
        [
            "## Notes",
            "",
            "- Parentheses report two-way clustered standard errors by event and peer firm.",
            "- `***`, `**`, and `*` denote significance at 1%, 5%, and 10%, respectively.",
            "- `Spec` is the within-event-definition winsorized z-score of the stated specificity measure.",
            "- These are result-organization tables for the current working specification, not a final manuscript table set.",
            "",
            "## Output Files",
            "",
        ]
    )
    for section in table_sections:
        for path in section["paths"]:  # type: ignore[union-attr]
            lines.append(f"- `{path}`")
    for path in extra_paths or []:
        lines.append(f"- `{path}`")
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel, events, grid = load_inputs()
    flow = sample_flow(panel, events)
    flow.to_csv(OUT_DIR / "main_effect_sample_flow.csv", index=False)
    table_sections: list[dict[str, object]] = []
    for effect in MAIN_EFFECTS:
        d = regression_sample(panel, events, MAIN_EVENT_DEF, effect.method_variant, MAIN_SPEC, MAIN_AI)
        desc = format_desc(desc_table(d))
        baseline = regression_table(baseline_models(d))
        robust = robustness_table(robustness_models(panel, events, effect))

        paths = [
            save_table(desc, f"{effect.slug}_table1_descriptive"),
            save_table(baseline, f"{effect.slug}_table2_baseline"),
            save_table(robust, f"{effect.slug}_table3_robustness"),
        ]
        table_sections.append(
            {
                "effect": effect,
                "desc": desc,
                "baseline": baseline,
                "robust": robust,
                "paths": paths,
            }
        )
        print(
            f"{effect.slug}: main sample N={len(d):,}, events={d['event_key'].nunique():,}, "
            f"peers={d['peer_code'].nunique():,}",
            flush=True,
        )
    workbook_path = save_workbook(table_sections)
    extra_paths = ["results/v25_empirical_table_pack_20260604/main_effect_sample_flow.csv"]
    if workbook_path:
        extra_paths.append(workbook_path)
    write_doc(table_sections, grid, flow, extra_paths)
    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
