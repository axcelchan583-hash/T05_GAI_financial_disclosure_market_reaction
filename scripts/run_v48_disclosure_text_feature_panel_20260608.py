#!/usr/bin/env python3
"""Build preliminary GenAI disclosure text features and run first-pass tests.

This is a machine-audit pass. It uses v36 candidate-event titles plus the
available LLM reason/evidence snippets, not full manually verified公告正文.
The output is meant to guide manual validation and model selection.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402


RUN_ID = "v48_disclosure_text_feature_panel_20260608"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "112_v48_disclosure_text_feature_panel_20260608.md"

QIAN_ROOT = ROOT.parent / "T05-qian-supplier-replication-cn"
V36_DIR = QIAN_ROOT / "results" / "v36_candidate_x_supplier_replication_20260604"
V36_FIRST = V36_DIR / "v36_candidate_x_first_event_per_firm.csv"
V36_UNIQUE = V36_DIR / "v36_candidate_x_unique_events.csv"

COMPETITOR_PANEL = (
    ROOT / "results" / "v36_spec_ai_firm_char_guard_20260605" / "analysis_panel_with_firm_chars.csv.gz"
)
FACTSET_STACK_PANEL = (
    ROOT / "results" / "v43_factset_grouped_relationship_results_20260607" / "factset_core_stack_panel.csv.gz"
)

OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
EVENT_FE = ["event_key"]


TEXT_COLUMNS = [
    "announcement_title",
    "candidate_tier",
    "query_terms",
    "matched_genai_terms",
    "fulltext_matched_genai_terms",
    "llm_category",
    "llm_reason",
    "llm_evidence",
    "backfill_matched_keywords",
    "backfill_match_reasons",
]

FEATURE_GROUPS = {
    "hard_info": [
        r"\d+",
        r"金额",
        r"亿元",
        r"万元",
        r"合同",
        r"订单",
        r"客户数量",
        r"参数",
        r"备案",
        r"期限",
        r"收入",
        r"交付",
    ],
    "implemented_action": [
        r"已上线",
        r"已发布",
        r"正式发布",
        r"已推出",
        r"推出",
        r"上线",
        r"发布",
        r"已落地",
        r"落地",
        r"已应用",
        r"应用",
        r"已部署",
        r"部署",
        r"接入",
        r"签署",
        r"签订",
        r"商用",
        r"商业化",
        r"中标",
    ],
    "commercialization": [
        r"商业化",
        r"客户",
        r"订单",
        r"收入",
        r"付费",
        r"销售",
        r"SaaS",
        r"解决方案",
        r"产品",
        r"服务",
        r"交付",
        r"市场",
    ],
    "own_capability": [
        r"自研",
        r"自主研发",
        r"自有",
        r"训练",
        r"模型",
        r"算法",
        r"算力",
        r"数据",
        r"平台",
        r"大模型",
        r"语言模型",
        r"垂直模型",
        r"备案",
    ],
    "named_partner": [
        r"合作伙伴",
        r"合作方",
        r"与.+签",
        r"联合",
        r"共建",
        r"伙伴",
        r"客户",
        r"供应商",
        r"大学",
        r"研究院",
        r"科技",
        r"集团",
        r"云",
    ],
    "bigtech_partner": [
        r"华为",
        r"腾讯",
        r"百度",
        r"阿里",
        r"阿里云",
        r"京东",
        r"字节",
        r"火山引擎",
        r"微软",
        r"OpenAI",
        r"AWS",
        r"亚马逊",
        r"商汤",
        r"科大讯飞",
        r"讯飞",
        r"智谱",
        r"澜舟",
        r"寒武纪",
    ],
    "equity_tie": [
        r"投资",
        r"参股",
        r"控股",
        r"持股",
        r"股权",
        r"基金",
        r"合资",
        r"并购",
        r"战略投资",
        r"全资子公司",
    ],
    "alliance_action": [
        r"战略合作",
        r"合作协议",
        r"签署",
        r"签订",
        r"联合研发",
        r"联合发布",
        r"联合",
        r"共建",
        r"生态",
        r"伙伴",
    ],
    "customer_usecase": [
        r"客户",
        r"场景",
        r"应用场景",
        r"行业",
        r"医疗",
        r"金融",
        r"教育",
        r"政务",
        r"传媒",
        r"游戏",
        r"制造",
        r"办公",
        r"营销",
        r"创作",
        r"客服",
    ],
    "vague_future": [
        r"拟",
        r"计划",
        r"未来",
        r"探索",
        r"关注",
        r"积极布局",
        r"布局",
        r"持续跟踪",
        r"密切关注",
        r"储备",
        r"研究",
        r"推进中",
    ],
    "denial": [
        r"暂无",
        r"不涉及",
        r"尚无",
        r"无相关",
        r"未开展",
        r"未产生收入",
        r"没有.*业务",
        r"无.*业务",
        r"不直接涉及",
    ],
    "promotional_tone": [
        r"赋能",
        r"引领",
        r"领先",
        r"突破",
        r"全面",
        r"深度",
        r"创新",
        r"打造",
        r"提升",
        r"生态",
        r"前沿",
        r"变革",
        r"核心竞争力",
    ],
    "ai_keyword": [
        r"AIGC",
        r"ChatGPT",
        r"GPT",
        r"DeepSeek",
        r"生成式AI",
        r"生成式人工智能",
        r"大模型",
        r"大语言模型",
        r"语言模型",
        r"人工智能",
        r"AI",
        r"LLM",
    ],
}

FEATURE_SUPPORT_SOURCE = {
    "hard_info_count_log_z": "hard_info_count",
    "implemented_action_count_log_z": "implemented_action_count",
    "commercialization_count_log_z": "commercialization_count",
    "own_capability_count_log_z": "own_capability_count",
    "named_partner_count_log_z": "named_partner_count",
    "bigtech_partner_count_log_z": "bigtech_partner_count",
    "equity_tie_count_log_z": "equity_tie_count",
    "alliance_action_count_log_z": "alliance_action_count",
    "customer_usecase_count_log_z": "customer_usecase_count",
    "vague_future_count_log_z": "vague_future_count",
    "denial_count_log_z": "denial_count",
    "promotional_tone_count_log_z": "promotional_tone_count",
    "ai_keyword_count_log_z": "ai_keyword_count",
    "numeric_token_count_log_z": "numeric_token_count",
    "org_suffix_count_log_z": "org_suffix_count",
    "buzz_no_detail_log_z": "buzz_no_detail",
}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6)[-6:] if digits else ""


def clean_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") else text


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


def zscore(series: pd.Series) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    std = x.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.nan, index=series.index)
    return (x - x.mean()) / std


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    if text.lower() == "nan":
        return ""
    return text.replace("\n", " ").replace("\r", " ").strip()


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"[。！？；;.!?]", text)
    return [p.strip() for p in parts if p and p.strip()]


def count_patterns(text: str, patterns: list[str]) -> int:
    if not text:
        return 0
    total = 0
    for pat in patterns:
        total += len(re.findall(pat, text, flags=re.IGNORECASE))
    return int(total)


def evidence_sentences(text: str, patterns: list[str], max_sentences: int = 3) -> list[str]:
    out = []
    for sent in split_sentences(text):
        if any(re.search(pat, sent, flags=re.IGNORECASE) for pat in patterns):
            out.append(sent[:180])
        if len(out) >= max_sentences:
            break
    return out


def load_events(path: Path, sample_name: str) -> pd.DataFrame:
    events = pd.read_csv(path, dtype=str, low_memory=False)
    events["sample_name"] = sample_name
    events["event_id"] = events["event_id"].map(clean_id)
    events["event_key"] = events["sample_name"] + "::" + events["event_id"]
    events["focal_code"] = events["focal_code"].map(code6)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events = events[events["event_id"].ne("") & events["focal_code"].ne("")].copy()
    return events


def build_text_features(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = events.copy()
    for col in TEXT_COLUMNS:
        if col not in out.columns:
            out[col] = ""
    out["feature_text"] = out[TEXT_COLUMNS].apply(
        lambda row: "。".join(normalize_text(row[col]) for col in TEXT_COLUMNS if normalize_text(row[col])),
        axis=1,
    )
    out["feature_text_len"] = out["feature_text"].str.len()
    out["feature_sentence_count"] = out["feature_text"].map(lambda x: len(split_sentences(x)))
    out["numeric_token_count"] = out["feature_text"].map(lambda x: len(re.findall(r"\d+", x)))
    out["org_suffix_count"] = out["feature_text"].map(
        lambda x: len(re.findall(r"(公司|集团|大学|研究院|科技|股份|有限|实验室|中心|云)", x))
    )

    evidence_rows = []
    for feature, patterns in FEATURE_GROUPS.items():
        count_col = f"{feature}_count"
        out[count_col] = out["feature_text"].map(lambda x, p=patterns: count_patterns(x, p))
        for _, row in out[["event_key", "event_id", "focal_code", "focal_name", "announcement_title", "feature_text"]].iterrows():
            sents = evidence_sentences(row["feature_text"], patterns)
            if not sents:
                continue
            evidence_rows.append(
                {
                    "event_key": row["event_key"],
                    "event_id": row["event_id"],
                    "focal_code": row["focal_code"],
                    "focal_name": row.get("focal_name", ""),
                    "announcement_title": row.get("announcement_title", ""),
                    "feature": feature,
                    "evidence_sentences": " || ".join(sents),
                }
            )

    out["buzz_no_detail"] = (
        (out["ai_keyword_count"] >= out["ai_keyword_count"].median())
        & (out["hard_info_count"].fillna(0) <= out["hard_info_count"].median())
        & (out["implemented_action_count"].fillna(0) <= out["implemented_action_count"].median())
    ).astype(int)

    component_cols = [
        "hard_info_count",
        "implemented_action_count",
        "commercialization_count",
        "own_capability_count",
        "named_partner_count",
        "bigtech_partner_count",
        "equity_tie_count",
        "alliance_action_count",
        "customer_usecase_count",
        "vague_future_count",
        "denial_count",
        "promotional_tone_count",
        "ai_keyword_count",
        "numeric_token_count",
        "org_suffix_count",
        "buzz_no_detail",
    ]
    for col in component_cols:
        out[f"{col}_log_z"] = zscore(np.log1p(pd.to_numeric(out[col], errors="coerce").fillna(0)))

    out["credible_implementation_z"] = out[
        [
            "hard_info_count_log_z",
            "implemented_action_count_log_z",
            "commercialization_count_log_z",
            "own_capability_count_log_z",
            "numeric_token_count_log_z",
        ]
    ].mean(axis=1)
    out["strategic_embeddedness_z"] = out[
        [
            "named_partner_count_log_z",
            "equity_tie_count_log_z",
            "alliance_action_count_log_z",
            "customer_usecase_count_log_z",
            "org_suffix_count_log_z",
        ]
    ].mean(axis=1)
    out["promotional_washing_z"] = out[
        [
            "ai_keyword_count_log_z",
            "vague_future_count_log_z",
            "promotional_tone_count_log_z",
            "denial_count_log_z",
            "buzz_no_detail_log_z",
        ]
    ].mean(axis=1)
    out["credible_minus_washing_z"] = zscore(out["credible_implementation_z"] - out["promotional_washing_z"])

    index_cols = [
        "credible_implementation_z",
        "strategic_embeddedness_z",
        "promotional_washing_z",
        "credible_minus_washing_z",
    ]
    for col in index_cols:
        out[col] = zscore(out[col])

    keep_cols = [
        "sample_name",
        "event_id",
        "event_key",
        "focal_code",
        "focal_name",
        "event_date",
        "announcement_title",
        "auto_pdf_label",
        "candidate_row_type",
        "candidate_tier",
        "qian_recall_score",
        "llm_category",
        "llm_reason",
        "llm_evidence",
        "feature_text_len",
        "feature_sentence_count",
        *component_cols,
        *[f"{col}_log_z" for col in component_cols],
        *index_cols,
    ]
    for col in keep_cols:
        if col not in out.columns:
            out[col] = np.nan
    return out[keep_cols].copy(), pd.DataFrame(evidence_rows)


def summarize_features(features: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "feature_text_len",
        "feature_sentence_count",
        "hard_info_count",
        "implemented_action_count",
        "commercialization_count",
        "own_capability_count",
        "named_partner_count",
        "equity_tie_count",
        "alliance_action_count",
        "vague_future_count",
        "denial_count",
        "promotional_tone_count",
        "ai_keyword_count",
        "buzz_no_detail",
        "credible_implementation_z",
        "strategic_embeddedness_z",
        "promotional_washing_z",
        "credible_minus_washing_z",
    ]
    rows = []
    for col in cols:
        x = pd.to_numeric(features[col], errors="coerce")
        rows.append(
            {
                "variable": col,
                "n": int(x.notna().sum()),
                "mean": float(x.mean()) if x.notna().any() else np.nan,
                "std": float(x.std(ddof=1)) if x.notna().sum() > 1 else np.nan,
                "p25": float(x.quantile(0.25)) if x.notna().any() else np.nan,
                "median": float(x.quantile(0.50)) if x.notna().any() else np.nan,
                "p75": float(x.quantile(0.75)) if x.notna().any() else np.nan,
                "max": float(x.max()) if x.notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def correlation_table(features: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "feature_text_len",
        "qian_recall_score",
        "hard_info_count",
        "implemented_action_count",
        "named_partner_count",
        "equity_tie_count",
        "vague_future_count",
        "denial_count",
        "ai_keyword_count",
        "credible_implementation_z",
        "strategic_embeddedness_z",
        "promotional_washing_z",
        "credible_minus_washing_z",
    ]
    d = features[cols].apply(pd.to_numeric, errors="coerce")
    corr = d.corr()
    return corr.reset_index().rename(columns={"index": "variable"})


def feature_nonzero_events(features: pd.DataFrame, feature_col: str) -> int:
    source_col = FEATURE_SUPPORT_SOURCE.get(feature_col, feature_col)
    if source_col not in features.columns:
        return int(features.loc[features[feature_col].notna(), "event_key"].nunique()) if feature_col in features.columns else 0
    x = pd.to_numeric(features[source_col], errors="coerce").fillna(0)
    return int(features.loc[x.ne(0), "event_key"].nunique())


def feature_support_warning(features: pd.DataFrame, feature_col: str) -> str:
    if feature_col in {
        "credible_implementation_z",
        "strategic_embeddedness_z",
        "promotional_washing_z",
        "credible_minus_washing_z",
        "legacy_spec_z",
    }:
        return ""
    return "low_support_do_not_interpret" if feature_nonzero_events(features, feature_col) < 10 else ""


def flatten_absorbed_result(
    res: dict[str, object] | None,
    model: str,
    outcome: str,
    focus_terms: list[str],
) -> pd.DataFrame:
    if not res:
        return pd.DataFrame(
            [
                {
                    "model": model,
                    "outcome": outcome,
                    "term": term,
                    "coef": np.nan,
                    "se": np.nan,
                    "p": np.nan,
                    "nobs": 0,
                    "events": 0,
                    "related_firms": 0,
                    "r2": np.nan,
                }
                for term in focus_terms
            ]
        )
    rows = []
    for term in focus_terms:
        coef = res.get(f"{term}_coef")
        se = res.get(f"{term}_se")
        p = res.get(f"{term}_p")
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": coef,
                "se": se,
                "p": p,
                "nobs": res.get("nobs", 0),
                "events": res.get("events", 0),
                "related_firms": res.get("peer_firms", 0),
                "r2": res.get("r2", np.nan),
                "fe_cols": res.get("fe_cols", ""),
            }
        )
    return pd.DataFrame(rows)


def run_competitor_tests(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(
        COMPETITOR_PANEL,
        dtype={"event_key": str, "event_id": str, "focal_code": str, "peer_code": str},
        low_memory=False,
    )
    panel["peer_code"] = panel["peer_code"].map(code6)
    keep_features = [
        "event_key",
        "credible_implementation_z",
        "strategic_embeddedness_z",
        "promotional_washing_z",
        "credible_minus_washing_z",
        "hard_info_count_log_z",
        "implemented_action_count_log_z",
        "named_partner_count_log_z",
        "equity_tie_count_log_z",
        "vague_future_count_log_z",
        "denial_count_log_z",
        "ai_keyword_count_log_z",
    ]
    d = panel.merge(features[keep_features], on="event_key", how="left", validate="many_to_one")
    d = d[d["complete_clean_m1_p1"].eq(1)].copy()
    for col in ["ai", OUTCOME, *PRE_CONTROLS]:
        d[col] = pd.to_numeric(d[col], errors="coerce")

    x_specs = [
        ("credible_implementation", "credible_implementation_z"),
        ("strategic_embeddedness", "strategic_embeddedness_z"),
        ("promotional_washing", "promotional_washing_z"),
        ("credible_minus_washing", "credible_minus_washing_z"),
        ("hard_info", "hard_info_count_log_z"),
        ("implemented_action", "implemented_action_count_log_z"),
        ("named_partner", "named_partner_count_log_z"),
        ("equity_tie", "equity_tie_count_log_z"),
        ("vague_future", "vague_future_count_log_z"),
        ("denial", "denial_count_log_z"),
        ("ai_keyword", "ai_keyword_count_log_z"),
    ]
    rows = []
    for label, col in x_specs:
        int_col = f"{label}_x_ai"
        d[int_col] = d[col] * d["ai"]
        xvars = ["ai", int_col, *PRE_CONTROLS]
        res = v25.fit_absorbed_ols(d, OUTCOME, xvars, EVENT_FE)
        one = flatten_absorbed_result(res, f"single_{label}_x_ai", OUTCOME, [int_col])
        one["feature"] = col
        one["feature_nonzero_events"] = feature_nonzero_events(features, col)
        one["feature_source_warning"] = feature_support_warning(features, col)
        rows.append(one)

    # Old benchmark from the current mechanism.
    if "spec_ai" in d.columns:
        res = v25.fit_absorbed_ols(d, OUTCOME, ["ai", "spec_ai", *PRE_CONTROLS], EVENT_FE)
        one = flatten_absorbed_result(res, "benchmark_old_spec_x_ai", OUTCOME, ["spec_ai"])
        one["feature"] = "legacy_spec_z"
        one["feature_nonzero_events"] = features["event_key"].nunique()
        one["feature_source_warning"] = ""
        rows.append(one)

    horse_terms = []
    for label, col in [
        ("credible_implementation", "credible_implementation_z"),
        ("strategic_embeddedness", "strategic_embeddedness_z"),
        ("promotional_washing", "promotional_washing_z"),
    ]:
        int_col = f"horse_{label}_x_ai"
        d[int_col] = d[col] * d["ai"]
        horse_terms.append(int_col)
    res = v25.fit_absorbed_ols(d, OUTCOME, ["ai", *horse_terms, *PRE_CONTROLS], EVENT_FE)
    horse = flatten_absorbed_result(res, "horse_three_indices_x_ai", OUTCOME, horse_terms)
    horse["feature_nonzero_events"] = features["event_key"].nunique()
    horse["feature_source_warning"] = ""

    out = pd.concat(rows, ignore_index=True)
    return out, horse


def run_relationship_tests(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    stack = pd.read_csv(
        FACTSET_STACK_PANEL,
        dtype={"event_key": str, "event_id": str, "focal_code": str, "peer_code": str, "related_code": str},
        low_memory=False,
    )
    stack["peer_code"] = stack["peer_code"].map(code6)
    stack["related_code"] = stack["related_code"].map(code6)
    stack = stack.merge(
        features[
            [
                "event_key",
                "credible_implementation_z",
                "strategic_embeddedness_z",
                "promotional_washing_z",
                "credible_minus_washing_z",
            ]
        ],
        on="event_key",
        how="left",
        validate="many_to_one",
    )
    for flag in [
        "is_factset_competitor",
        "is_factset_upstream_supplier",
        "is_factset_downstream_customer",
        "is_factset_partner_high_confidence",
        "is_factset_partner_investment",
    ]:
        if flag not in stack.columns:
            stack[flag] = 0
        stack[flag] = pd.to_numeric(stack[flag], errors="coerce").fillna(0).astype(float)
    base_flags = [
        "is_factset_competitor",
        "is_factset_upstream_supplier",
        "is_factset_downstream_customer",
        "is_factset_partner_high_confidence",
        "is_factset_partner_investment",
    ]

    rows = []
    for label, col in [
        ("credible_implementation", "credible_implementation_z"),
        ("strategic_embeddedness", "strategic_embeddedness_z"),
        ("promotional_washing", "promotional_washing_z"),
        ("credible_minus_washing", "credible_minus_washing_z"),
    ]:
        for rel_flag in ["is_factset_partner_investment", "is_factset_partner_high_confidence"]:
            int_col = f"{rel_flag.removeprefix('is_factset_')}_x_{label}"
            stack[int_col] = stack[rel_flag] * pd.to_numeric(stack[col], errors="coerce")
            xvars = [*base_flags, int_col]
            for outcome in ["peer_ar0_mm", "peer_car_0_p1_mm", "peer_car_m1_p1_mm"]:
                res = v25.fit_absorbed_ols(stack, outcome, xvars, EVENT_FE)
                one = flatten_absorbed_result(res, f"stack_{label}_{rel_flag}", outcome, [int_col])
                one["feature"] = col
                one["feature_nonzero_events"] = feature_nonzero_events(features, col)
                one["feature_source_warning"] = feature_support_warning(features, col)
                rows.append(one)
    rel = pd.concat(rows, ignore_index=True)

    # Event-weighted investment-partner CAR by event, used as a small-sample diagnostic.
    inv = stack[
        stack["is_factset_partner_investment"].eq(1)
        & stack["complete_clean_m1_p1"].eq(1)
        & stack["peer_car_0_p1_mm"].notna()
    ].copy()
    event = (
        inv.groupby("event_key", as_index=False)
        .agg(
            mean_partner_car0p1=("peer_car_0_p1_mm", "mean"),
            rows=("peer_code", "size"),
            related_firms=("peer_code", "nunique"),
            credible_implementation_z=("credible_implementation_z", "first"),
            strategic_embeddedness_z=("strategic_embeddedness_z", "first"),
            promotional_washing_z=("promotional_washing_z", "first"),
            credible_minus_washing_z=("credible_minus_washing_z", "first"),
        )
        .copy()
    )
    corr_rows = []
    for col in [
        "credible_implementation_z",
        "strategic_embeddedness_z",
        "promotional_washing_z",
        "credible_minus_washing_z",
    ]:
        x = event[[col, "mean_partner_car0p1"]].dropna()
        corr_rows.append(
            {
                "sample": "investment_partner_event_weighted",
                "x": col,
                "events": len(x),
                "corr_with_mean_partner_car0p1": float(x[col].corr(x["mean_partner_car0p1"])) if len(x) > 2 else np.nan,
                "mean_partner_car0p1": float(x["mean_partner_car0p1"].mean()) if len(x) else np.nan,
            }
        )
    return rel, pd.DataFrame(corr_rows)


def manual_validation_sample(features: pd.DataFrame) -> pd.DataFrame:
    parts = []
    sort_specs = [
        ("top_credible", "credible_implementation_z", False),
        ("bottom_credible", "credible_implementation_z", True),
        ("top_strategic", "strategic_embeddedness_z", False),
        ("top_washing", "promotional_washing_z", False),
        ("top_denial", "denial_count", False),
    ]
    for label, col, asc in sort_specs:
        d = features.sort_values(col, ascending=asc).head(30).copy()
        d["validation_bucket"] = label
        parts.append(d)
    sample = pd.concat(parts, ignore_index=True).drop_duplicates("event_key", keep="first")
    keep = [
        "validation_bucket",
        "event_key",
        "event_date",
        "focal_code",
        "focal_name",
        "announcement_title",
        "auto_pdf_label",
        "candidate_row_type",
        "llm_reason",
        "llm_evidence",
        "credible_implementation_z",
        "strategic_embeddedness_z",
        "promotional_washing_z",
        "denial_count",
        "ai_keyword_count",
    ]
    return sample[keep].head(120).copy()


def fmt_coef(coef: object, p: object) -> str:
    if coef is None or pd.isna(coef):
        return ""
    p_val = float(p) if p is not None and pd.notna(p) else np.nan
    stars = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.10 else ""
    return f"{float(coef):.4f}{stars}"


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(max_rows).copy()
    for col in show.select_dtypes(include=[np.number]).columns:
        show[col] = show[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, row in show.iterrows():
        vals = ["" if pd.isna(row[c]) else str(row[c]).replace("|", "\\|") for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(
    features: pd.DataFrame,
    summary: pd.DataFrame,
    competitor: pd.DataFrame,
    competitor_horse: pd.DataFrame,
    relationship: pd.DataFrame,
    investment_corr: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    comp_show = competitor.copy()
    comp_show["coef_fmt"] = comp_show.apply(lambda r: fmt_coef(r["coef"], r["p"]), axis=1)
    comp_show = comp_show[
        [
            "model",
            "term",
            "coef_fmt",
            "se",
            "p",
            "feature_nonzero_events",
            "feature_source_warning",
            "nobs",
            "events",
            "related_firms",
            "r2",
        ]
    ]

    horse_show = competitor_horse.copy()
    horse_show["coef_fmt"] = horse_show.apply(lambda r: fmt_coef(r["coef"], r["p"]), axis=1)
    horse_show = horse_show[["model", "term", "coef_fmt", "se", "p", "nobs", "events", "related_firms", "r2"]]

    rel_show = relationship.copy()
    rel_show["coef_fmt"] = rel_show.apply(lambda r: fmt_coef(r["coef"], r["p"]), axis=1)
    rel_show = rel_show[
        [
            "model",
            "outcome",
            "term",
            "coef_fmt",
            "se",
            "p",
            "feature_nonzero_events",
            "feature_source_warning",
            "nobs",
            "events",
            "related_firms",
            "r2",
        ]
    ]

    text = f"""# v48 GenAI Disclosure Text Feature Panel

Date: 2026-06-08

## Purpose

This run operationalizes the new disclosure-text design in `docs/design/重新构造X和Y/03_disclosure_text_feature_design_20260608.md`.

It is a machine-audit pass, not a final manual text-coding result. The text source is the v36 event title plus existing LLM reason/evidence snippets and keyword/backfill traces. It does not yet parse the full PDF body sentence by sentence.

## Verdict

The current rule-based text-feature indices do **not** replace the legacy `Specificity x AIActivePeer` mechanism.

- In the competitor panel, `CredibleImplementation x AIActivePeer` is not negative and is not significant.
- `StrategicEmbeddedness x AIActivePeer` is negative but weak and insignificant.
- The legacy `Spec x AIActivePeer` remains the only clean competitor text mechanism in this pass.
- Any `Denial` coefficient should be ignored because the feature has too few nonzero events.
- In the relationship stack, investment-linked partner interactions are positive in several windows but generally insignificant; the most useful signal is still the level/event-weighted investment-linked partner result from v47, not the v48 text interaction.

Interpretation: v48 is useful for building a manual validation sample and refining the codebook, but it is not yet evidence that the new composite text indices should become the main X.

## Event Text Feature Coverage

- Events with text features: {features['event_key'].nunique()}
- Focal firms: {features['focal_code'].nunique()}
- Direct candidates: {int(features['candidate_row_type'].fillna('').eq('direct_event_date_candidate').sum())}
- Keyword/backfill candidates: {int(features['candidate_row_type'].fillna('').str.contains('keyword', case=False).sum())}

## Text Feature Summary

{md_table(summary, max_rows=120)}

## Competitor Mechanism: Text Feature x AIActivePeer

Specification:

`PeerCAR[0,+1] ~ AIActive + TextFeature x AIActive + PeerCAR[-10,-2] + PeerCAR[-20,-2] + event FE`

SE: two-way clustered by event and peer firm through the existing absorbed-OLS helper.

{md_table(comp_show, max_rows=120)}

## Competitor Horse Race: Three Text Indices

{md_table(horse_show, max_rows=40)}

## Relationship Stacked Tests

Baseline is the product-market competitor panel. Event FE absorbs the focal GenAI event. The reported term is a relation-type indicator interacted with the event-level text feature.

{md_table(rel_show, max_rows=160)}

## Investment-Linked Partner Event-Weighted Diagnostic

{md_table(investment_corr, max_rows=20)}

## Reading

This pass should be read as a screen:

- If `CredibleImplementation x AIActivePeer` is negative, it supports treating concrete implementation language as a competitive-risk signal.
- If `StrategicEmbeddedness x investment-linked partner` is positive, it supports the investment-linked partner route.
- If `PromotionalWashing x AIActivePeer` is negative in the same way as credible implementation, the text measure is not discriminating enough and needs manual recoding.

## Required Next Step

Manual validation should prioritize:

1. top and bottom `CredibleImplementation`;
2. top `StrategicEmbeddedness`;
3. top `PromotionalWashing` and `Denial`;
4. investment-linked partner events with large positive or negative CAR.

## Output Files

- `results/{RUN_ID}/event_text_features.csv`
- `results/{RUN_ID}/event_text_feature_evidence_sentences.csv`
- `results/{RUN_ID}/text_feature_summary.csv`
- `results/{RUN_ID}/text_feature_correlations.csv`
- `results/{RUN_ID}/competitor_text_feature_regressions.csv`
- `results/{RUN_ID}/competitor_text_feature_horserace.csv`
- `results/{RUN_ID}/relationship_text_feature_regressions.csv`
- `results/{RUN_ID}/investment_partner_event_feature_correlations.csv`
- `results/{RUN_ID}/manual_validation_sample.csv`
"""
    DOC_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    first = load_events(V36_FIRST, "combined_first_event_per_firm")
    features, evidence = build_text_features(first)
    summary = summarize_features(features)
    corr = correlation_table(features)
    comp, comp_horse = run_competitor_tests(features)
    rel, invest_corr = run_relationship_tests(features)
    validation = manual_validation_sample(features)

    features.to_csv(OUT_DIR / "event_text_features.csv", index=False)
    evidence.to_csv(OUT_DIR / "event_text_feature_evidence_sentences.csv", index=False)
    summary.to_csv(OUT_DIR / "text_feature_summary.csv", index=False)
    corr.to_csv(OUT_DIR / "text_feature_correlations.csv", index=False)
    comp.to_csv(OUT_DIR / "competitor_text_feature_regressions.csv", index=False)
    comp_horse.to_csv(OUT_DIR / "competitor_text_feature_horserace.csv", index=False)
    rel.to_csv(OUT_DIR / "relationship_text_feature_regressions.csv", index=False)
    invest_corr.to_csv(OUT_DIR / "investment_partner_event_feature_correlations.csv", index=False)
    validation.to_csv(OUT_DIR / "manual_validation_sample.csv", index=False)

    write_report(features, summary, comp, comp_horse, rel, invest_corr)
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
