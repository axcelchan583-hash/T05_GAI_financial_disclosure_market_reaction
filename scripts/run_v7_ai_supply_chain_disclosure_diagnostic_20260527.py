#!/usr/bin/env python3
"""Diagnostic: is the current Specificity_z actually picking up AI supply-chain disclosure?

This script is deliberately diagnostic. It does not replace the v6 headline
design. It asks whether the stronger textual signal may be about firms disclosing
their exposure to AI/large-model demand through hardware, compute, data-center,
semiconductor, optical, cooling, AIPC, or data-resource supply chains.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_final_review_checks_20260525 import OUTCOME, STRONG_FE, add_ai_terms
from run_v6_identification_strengthening_checks_20260524 import fit_absorbed


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v7_ai_supply_chain_disclosure_diagnostic_20260527"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "57_v7_ai_supply_chain_disclosure_diagnostic_20260527.md"

EVENT_PATH = (
    ROOT
    / "results"
    / "csmar_v5_1_response_smoke_20260523"
    / "csmar_conservative_focal_events_2023_2026.csv"
)
ANALYSIS_SAMPLE_PATH = (
    ROOT
    / "results"
    / "v6_focal_good_news_pretrend_checks_20260525"
    / "analysis_sample_top5.csv.gz"
)
MANUAL_SAMPLE_PATH = (
    ROOT
    / "claude_project"
    / "3"
    / "validation_sample"
    / "manual_review"
    / "manual_review_raw_300_20260525.csv"
)
CLAUDE_CODES_PATH = (
    ROOT
    / "claude_project"
    / "3"
    / "validation_sample"
    / "claude_coding"
    / "claude_manual_codes_300_20260526.csv"
)
AGENT_CODES_PATH = (
    ROOT
    / "claude_project"
    / "3"
    / "validation_sample"
    / "agent_coding"
    / "agent1_manual_codes_300_20260526.csv"
)


GENAI_PAT = re.compile(
    r"ChatGPT|GPT|DeepSeek|Kimi|通义|文心|智谱|星火|盘古|混元|豆包|AIGC|生成式|大模型|大语言模型|LLM|多模态|人工智能生成",
    re.I,
)

SUPPLY_PATTERNS = {
    "supply_compute_datacenter": re.compile(
        r"算力|智算|数据中心|IDC|服务器|AI服务器|推理服务器|训练服务器|云计算|云服务|GPU|CPU|NPU|算力中心|超算|机柜|交换机|路由器",
        re.I,
    ),
    "supply_cooling_power": re.compile(
        r"液冷|散热|热管理|冷却|水冷|温控|制冷|电源|变压器|UPS|储能|配电|能耗|PUE",
        re.I,
    ),
    "supply_optical_network": re.compile(
        r"光模块|光通信|光芯片|光器件|光纤|光缆|CPO|800G|400G|1\.6T|高速率|以太网|网络设备|通信模块",
        re.I,
    ),
    "supply_semiconductor_component": re.compile(
        r"芯片|半导体|晶圆|硅片|单晶硅|封装|HBM|存储|存储器|SRAM|DRAM|PCB|载板|引线框架|电子元器件|传感器|连接器|功率器件",
        re.I,
    ),
    "supply_device_terminal": re.compile(
        r"AIPC|AI\s*PC|AI手机|AI眼镜|AR眼镜|智能终端|终端品牌|消费电子|结构件|显示屏|面板|整机|端侧|边缘计算",
        re.I,
    ),
    "supply_data_resource": re.compile(
        r"数据集|数据资源|数据湖|语料|语料库|标注|数据标注|训练数据|训练资源|知识库|数据服务|数据要素",
        re.I,
    ),
}

DEMAND_LINK_PAT = re.compile(
    r"需求|受益|带动|拉动|推升|增长|放量|扩容|景气|机遇|赋能|支持|支撑|提供|应用于|用于|适用于|客户|供货|配套|建设|项目|订单|出货|市场空间",
    re.I,
)

OWN_IMPL_PAT = re.compile(
    r"(已|已经|正在|完成|上线|发布|推出|部署|接入|落地|应用|使用|内测|试点|训练|开发|研发|打造|建设).{0,35}"
    r"(ChatGPT|GPT|DeepSeek|Kimi|通义|文心|智谱|星火|盘古|混元|豆包|AIGC|生成式|大模型|大语言模型|LLM|多模态)|"
    r"(ChatGPT|GPT|DeepSeek|Kimi|通义|文心|智谱|星火|盘古|混元|豆包|AIGC|生成式|大模型|大语言模型|LLM|多模态).{0,35}"
    r"(上线|发布|推出|部署|接入|落地|应用|使用|内测|试点|训练|开发|研发|打造|建设)",
    re.I,
)

NEG_PAT = re.compile(r"暂不|暂未|尚未|没有|不涉及|未涉及|暂无|尚无|无合作|无业务往来|未接入|尚未接入", re.I)


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def code6(value: object) -> str:
    text = re.sub(r"\.0$", "", str(value).strip()) if not pd.isna(value) else ""
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    std = x.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.zeros(len(x)), index=s.index)
    return (x - x.mean()) / std


def supply_chain_codes(text: object) -> dict[str, object]:
    ans = clean_text(text)
    has_genai = bool(GENAI_PAT.search(ans))
    subtype_hits = {name: int(bool(pat.search(ans))) for name, pat in SUPPLY_PATTERNS.items()}
    subtype_sum = int(sum(subtype_hits.values()))
    has_demand_link = bool(DEMAND_LINK_PAT.search(ans))
    is_negative_only = bool(NEG_PAT.search(ans)) and not bool(OWN_IMPL_PAT.search(ans))
    ai_supply = int(has_genai and subtype_sum > 0 and has_demand_link and not is_negative_only)
    own_impl = int(has_genai and bool(OWN_IMPL_PAT.search(ans)) and not is_negative_only)
    generic = int(has_genai and not ai_supply and not own_impl and not is_negative_only)
    denial = int(has_genai and is_negative_only and not ai_supply and not own_impl)
    return {
        "ai_supply_chain_exposure": ai_supply,
        "own_genai_implementation_regex": own_impl,
        "generic_ai_attention_regex": generic,
        "denial_no_current_regex": denial,
        "supply_subtype_count": subtype_sum,
        "has_supply_demand_link": int(has_demand_link),
        **subtype_hits,
    }


def add_supply_codes(df: pd.DataFrame, text_col: str = "sample_answer") -> pd.DataFrame:
    codes = pd.DataFrame([supply_chain_codes(x) for x in df[text_col]])
    return pd.concat([df.reset_index(drop=True), codes], axis=1)


def corr_row(df: pd.DataFrame, x: str, y: str) -> dict[str, object]:
    a = pd.to_numeric(df[x], errors="coerce")
    b = pd.to_numeric(df[y], errors="coerce")
    ok = a.notna() & b.notna()
    if ok.sum() < 3:
        return {"x": x, "y": y, "n": int(ok.sum()), "pearson": math.nan, "spearman": math.nan}
    return {
        "x": x,
        "y": y,
        "n": int(ok.sum()),
        "pearson": float(a[ok].corr(b[ok], method="pearson")),
        "spearman": float(a[ok].rank().corr(b[ok].rank(), method="pearson")),
    }


def run_reg(data: pd.DataFrame, xvar: str, ai_def: str, model: str, extra_controls: list[str] | None = None) -> dict[str, object]:
    d = data.copy()
    d["ai"] = d[ai_def].fillna(0).astype(float)
    d["xmain"] = d[xvar].fillna(0).astype(float)
    d["x_ai"] = d["xmain"] * d["ai"]
    xvars = ["ai", "x_ai", *(extra_controls or [])]
    rows = fit_absorbed(d, OUTCOME, xvars, STRONG_FE, model=model, term_focus="x_ai")
    if not rows:
        return {
            "model": model,
            "xvar": xvar,
            "ai_def": ai_def,
            "term": "x_ai",
            "coef": math.nan,
            "se": math.nan,
            "z": math.nan,
            "p": math.nan,
            "nobs": 0,
            "events": 0,
            "peer_firms": 0,
            "controls": "|".join(extra_controls or []),
        }
    row = rows[0]
    row.update({"xvar": xvar, "ai_def": ai_def, "controls": "|".join(extra_controls or [])})
    return row


def run_event_level_reg(
    data: pd.DataFrame,
    xvars: list[str],
    term_focus: str,
    model: str,
    fe_cols: list[str],
    extra_controls: list[str] | None = None,
) -> list[dict[str, object]]:
    d = data.copy()
    xall = [*xvars, *(extra_controls or [])]
    rows = fit_absorbed(d, OUTCOME, xall, fe_cols, model=model, term_focus=term_focus)
    for row in rows:
        row.update(
            {
                "xvar": term_focus,
                "ai_def": "",
                "controls": "|".join(extra_controls or []),
                "fe_spec": "+".join(fe_cols),
            }
        )
    return rows


def make_table(df: pd.DataFrame, cols: list[str] | None = None) -> str:
    if cols is not None:
        df = df[cols]
    return df.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    manual = pd.read_csv(MANUAL_SAMPLE_PATH, dtype={"event_id": str, "focal_code": str})
    manual = add_supply_codes(manual)
    manual.to_csv(OUT_DIR / "manual_300_supply_chain_codes.csv", index=False)

    claude = pd.read_csv(CLAUDE_CODES_PATH, dtype={"event_id": str, "focal_code": str})
    agent = pd.read_csv(AGENT_CODES_PATH, dtype={"event_id": str, "focal_code": str})
    component_cols = [
        "has_specific_product_service",
        "has_model_platform_name",
        "has_specific_use_case",
        "has_customer_or_industry",
        "has_partner_or_org",
        "has_deployment_status",
        "has_commercialization_or_timeline",
        "has_quantitative_commitment",
    ]
    for label, df in [("claude", claude), ("agent1", agent)]:
        df[f"{label}_component_sum"] = df[component_cols].sum(axis=1)
    m = (
        manual.merge(
            claude[["validation_id", "specificity_score_0_4", "claude_component_sum"]],
            on="validation_id",
            how="left",
        )
        .rename(columns={"specificity_score_0_4": "claude_score"})
        .merge(
            agent[["validation_id", "specificity_score_0_4", "agent1_component_sum"]],
            on="validation_id",
            how="left",
        )
        .rename(columns={"specificity_score_0_4": "agent1_score"})
    )

    vars_for_corr = [
        "ai_supply_chain_exposure",
        "own_genai_implementation_regex",
        "generic_ai_attention_regex",
        "denial_no_current_regex",
        "supply_subtype_count",
    ]
    outcomes = ["specificity_z", "specificity", "total_specific_items", "claude_score", "agent1_score"]
    corr = pd.DataFrame([corr_row(m, x, y) for x in vars_for_corr for y in outcomes])
    corr.to_csv(OUT_DIR / "manual_300_supply_chain_correlations.csv", index=False)

    summary_rows: list[dict[str, object]] = []
    group_cols = [
        "ai_supply_chain_exposure",
        "own_genai_implementation_regex",
        "generic_ai_attention_regex",
        "denial_no_current_regex",
    ]
    for col in group_cols:
        sub = m[m[col].eq(1)]
        summary_rows.append(
            {
                "group": col,
                "n": int(len(sub)),
                "mean_specificity_z": float(sub["specificity_z"].mean()) if len(sub) else math.nan,
                "mean_claude_score": float(sub["claude_score"].mean()) if len(sub) else math.nan,
                "mean_agent1_score": float(sub["agent1_score"].mean()) if len(sub) else math.nan,
            }
        )
    summary_rows.append(
        {
            "group": "all_manual_300",
            "n": int(len(m)),
            "mean_specificity_z": float(m["specificity_z"].mean()),
            "mean_claude_score": float(m["claude_score"].mean()),
            "mean_agent1_score": float(m["agent1_score"].mean()),
        }
    )
    manual_summary = pd.DataFrame(summary_rows)
    manual_summary.to_csv(OUT_DIR / "manual_300_supply_chain_summary.csv", index=False)

    examples = m[m["ai_supply_chain_exposure"].eq(1)].copy()
    examples = examples.sort_values("specificity_z", ascending=False)[
        [
            "validation_id",
            "focal_code",
            "company_name",
            "event_date",
            "specificity_bin",
            "specificity_z",
            "claude_score",
            "agent1_score",
            "sample_answer",
        ]
    ].head(30)
    examples.to_csv(OUT_DIR / "manual_300_supply_chain_examples.csv", index=False)

    events = pd.read_csv(EVENT_PATH, dtype={"event_id": str, "focal_code": str, "stock_code": str})
    events["focal_code"] = events["focal_code"].map(code6)
    events = add_supply_codes(events)
    events["ai_supply_chain_z"] = zscore(events["ai_supply_chain_exposure"])
    events["supply_subtype_count_z"] = zscore(events["supply_subtype_count"])
    events.to_csv(OUT_DIR / "all_focal_events_supply_chain_codes.csv", index=False)

    panel = pd.read_csv(ANALYSIS_SAMPLE_PATH, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    event_codes = events[
        [
            "event_id",
            "ai_supply_chain_exposure",
            "own_genai_implementation_regex",
            "generic_ai_attention_regex",
            "denial_no_current_regex",
            "supply_subtype_count",
            "ai_supply_chain_z",
            "supply_subtype_count_z",
            *SUPPLY_PATTERNS.keys(),
        ]
    ].drop_duplicates("event_id")
    panel = panel.merge(event_codes, on="event_id", how="left")
    panel["focal_industry_week"] = panel["focal_industry_d"].fillna("UNKNOWN").astype(str) + "|" + panel[
        "event_week"
    ].fillna("").astype(str)
    panel.to_csv(OUT_DIR / "analysis_sample_top5_with_supply_chain_codes.csv.gz", index=False, compression="gzip")

    reg_rows: list[dict[str, object]] = []
    reg_sample = panel.dropna(
        subset=[
            OUTCOME,
            "peer_car_pre10_m2_mm",
            "peer_car_pre20_m2_mm",
            "event_id",
            "peer_code",
            "peer_industry_week",
        ]
    ).copy()
    controls = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
    for ai_def in ["ext_any", "current_text_history"]:
        for xvar in [
            "specificity_z",
            "ai_supply_chain_exposure",
            "supply_subtype_count_z",
            "own_genai_implementation_regex",
        ]:
            reg_rows.append(run_reg(reg_sample, xvar, ai_def, f"{xvar}_x_{ai_def}", controls))
        # Horse race: original Specificity_z and supply-chain exposure both interacted with AIActive.
        d = add_ai_terms(reg_sample, ai_def)
        d["supply_ai"] = d["ai_supply_chain_exposure"].fillna(0).astype(float) * d["ai"]
        rows = fit_absorbed(
            d,
            OUTCOME,
            ["ai", "spec_ai", "supply_ai", *controls],
            STRONG_FE,
            model=f"horse_race_specz_supply_x_{ai_def}",
            term_focus=None,
        )
        for row in rows:
            if row["term"] in {"spec_ai", "supply_ai"}:
                row.update(
                    {
                        "xvar": row["term"],
                        "ai_def": ai_def,
                        "controls": "peer_car_pre10_m2_mm|peer_car_pre20_m2_mm|horse_race",
                    }
                )
                reg_rows.append(row)

    regressions = pd.DataFrame(reg_rows)
    regressions.to_csv(OUT_DIR / "supply_chain_peer_car_regressions.csv", index=False)

    event_level_rows: list[dict[str, object]] = []
    event_fe_sets = {
        "week_peer_industry_week": ["event_week", "peer_industry_week"],
        "focal_industry_week_peer_industry_week": ["focal_industry_week", "peer_industry_week"],
    }
    for fe_name, fe_cols in event_fe_sets.items():
        event_level_rows.extend(
            run_event_level_reg(
                reg_sample,
                ["ai_supply_chain_exposure"],
                "ai_supply_chain_exposure",
                f"supply_main_{fe_name}",
                fe_cols,
                controls,
            )
        )
        event_level_rows.extend(
            run_event_level_reg(
                reg_sample,
                ["specificity_z"],
                "specificity_z",
                f"specz_main_{fe_name}",
                fe_cols,
                controls,
            )
        )
        event_level_rows.extend(
            run_event_level_reg(
                reg_sample,
                ["specificity_z", "ai_supply_chain_exposure"],
                "ai_supply_chain_exposure",
                f"horse_race_supply_specz_{fe_name}",
                fe_cols,
                controls,
            )
        )
        event_level_rows.extend(
            run_event_level_reg(
                reg_sample,
                ["specificity_z", "ai_supply_chain_exposure"],
                "specificity_z",
                f"horse_race_supply_specz_{fe_name}",
                fe_cols,
                controls,
            )
        )
    event_level = pd.DataFrame(event_level_rows)
    event_level.to_csv(OUT_DIR / "supply_chain_event_level_peer_car_regressions.csv", index=False)

    event_summary = pd.DataFrame(
        [
            {
                "sample": "all_focal_events",
                "events": int(events["event_id"].nunique()),
                "supply_events": int(events["ai_supply_chain_exposure"].sum()),
                "supply_share": float(events["ai_supply_chain_exposure"].mean()),
                "own_impl_regex_events": int(events["own_genai_implementation_regex"].sum()),
                "denial_events": int(events["denial_no_current_regex"].sum()),
            },
            {
                "sample": "headline_analysis_events",
                "events": int(panel["event_id"].nunique()),
                "supply_events": int(panel.drop_duplicates("event_id")["ai_supply_chain_exposure"].sum()),
                "supply_share": float(panel.drop_duplicates("event_id")["ai_supply_chain_exposure"].mean()),
                "own_impl_regex_events": int(panel.drop_duplicates("event_id")["own_genai_implementation_regex"].sum()),
                "denial_events": int(panel.drop_duplicates("event_id")["denial_no_current_regex"].sum()),
            },
        ]
    )
    event_summary.to_csv(OUT_DIR / "supply_chain_event_summary.csv", index=False)

    doc = f"""# V7 AI Supply-Chain Disclosure Diagnostic

Date: 2026-05-27

Purpose: test whether the existing `Specificity_z` signal is closer to AI supply-chain exposure disclosure than to own GenAI implementation specificity.

## Manual 300-Row Diagnostic

```text
{manual_summary.to_string(index=False)}
```

## Correlations in Manual 300 Sample

```text
{corr.to_string(index=False)}
```

## Event-Level Prevalence

```text
{event_summary.to_string(index=False)}
```

## Peer-CAR Regressions

All regressions use the current headline Top5 sample, announcement-cleaned rows, `PeerCAR[0,+1]`, event FE + peer industry-week FE, two-way clustered by event and peer firm. Controls include `PeerCAR[-10,-2]` and `PeerCAR[-20,-2]`.

```text
{regressions[['model','term','coef','se','z','p','nobs','events','peer_firms','xvar','ai_def','controls']].to_string(index=False)}
```

## Event-Level Supply-Chain Disclosure Regressions

These regressions estimate the average Top5 peer revaluation effect of event-level supply-chain exposure. They do not include event FE because the supply-chain variable is focal-event-level. They instead use calendar-week or focal-industry-week controls plus peer industry-week FE, with the same two-way event/peer clustering.

```text
{event_level[['model','term','coef','se','z','p','nobs','events','peer_firms','fe_spec','controls']].to_string(index=False)}
```

## Supply-Chain Examples

```text
{examples[['validation_id','company_name','event_date','specificity_bin','specificity_z','claude_score','agent1_score']].to_string(index=False)}
```

## Initial Interpretation

This diagnostic separates two constructs:

1. `own_genai_implementation_regex`: focal firm says it deploys, connects, develops, or uses GenAI / large-model systems itself.
2. `ai_supply_chain_exposure`: focal firm links GenAI / large-model demand to its hardware, compute, data-center, optical, semiconductor, cooling, AIPC, or data-resource products.

If `ai_supply_chain_exposure × AIActivePeer` explains peer CAR better than original `Specificity_z × AIActivePeer`, the paper should pivot toward AI supply-chain exposure disclosure. If it does not, keep this only as a measurement diagnostic and do not rewrite the study around it.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
