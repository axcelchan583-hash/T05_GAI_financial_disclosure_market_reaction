#!/usr/bin/env python3
"""Probe CAC filing / algorithm-filing language as a GenAI disclosure recall arm."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
QIAN_ROOT = ROOT.parent / "T05-qian-supplier-replication-cn"
RUN_ID = "v62_filing_recall_probe_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "122_v62_filing_recall_probe_20260612.md"

SOURCE_PATHS = [
    (
        "v26_111k_genai_fulltext",
        QIAN_ROOT / "results/v26_cninfo_fulltext_harvest_20260603/cninfo_fulltext_a_share_announcements.csv.gz",
    ),
    (
        "v49_b_group_fulltext",
        QIAN_ROOT / "results/v49_cninfo_fulltext_b_group_harvest_20260608/cninfo_fulltext_a_share_announcements.csv.gz",
    ),
]

V56_EVENTS = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_event_samples.csv"
V60_EVENTS = ROOT / "results/v60_core_clean_launch_event_study_20260612/core_event_samples.csv"
V61_EVENTS = ROOT / "results/v61_modelapp_layer_event_study_20260612/modelapp_event_samples.csv"
CAC_RECORDS = ROOT / "data/interim/cac_genai_service_filing_records.csv"

SCAN_COLS = [
    "announcement_title",
    "short_title",
    "announcement_content",
    "action_snippet",
]

KEEP_COLS = [
    "announcement_id",
    "sec_code",
    "sec_name",
    "announcement_title",
    "short_title",
    "announcement_date",
    "announcement_year",
    "adjunct_url",
    "pdf_url",
    "page_column",
    "announcement_type",
    "title_excluded",
    "title_exclusion_reason",
    "candidate_tier",
    "qian_recall_score",
    "is_a_share_formal_row",
    *SCAN_COLS,
]

GENAI_RE = re.compile(
    r"生成式人工智能|生成式AI|生成式\s*AI|AIGC|ChatGPT|GPT|大模型|大语言模型|语言大模型|"
    r"多模态大模型|通用大模型|行业大模型|垂类大模型|基础模型|预训练模型|"
    r"文心一言|通义千问|讯飞星火|星火认知|盘古大模型|混元大模型|豆包大模型|"
    r"百川大模型|智谱|ChatGLM|GLM|DeepSeek|Kimi|Moonshot|日日新|天工大模型|“天工”|书生浦语|商量大模型"
)

FILING_RE = re.compile(
    r"备案|算法备案|大模型算法备案|生成式人工智能服务备案|生成式人工智能服务已备案|"
    r"生成式人工智能服务登记|已备案|备案通过|通过备案|备案成功|获.*?备案|取得.*?备案|"
    r"完成.*?备案|网信办.*?备案|国家互联网信息办公室.*?备案|互联网信息服务算法备案|"
    r"深度合成服务算法备案|生成式人工智能服务.*?安全评估"
)

STRONG_FILING_RE = re.compile(
    r"生成式人工智能服务.{0,30}(备案|登记|安全评估)|"
    r"(大模型|大语言模型).{0,25}(算法备案|备案通过|通过.{0,10}备案|完成.{0,10}备案|"
    r"成功.{0,10}备案|已.{0,10}备案|获.{0,10}备案|取得.{0,10}备案|申报.{0,10}备案|"
    r"备案号|备案许可|备案资格|备案审核|备案评测|备案中)|"
    r"(算法备案|深度合成服务算法备案|互联网信息服务算法备案).{0,35}(大模型|生成式|AIGC|深度合成|文本生成|图像生成|语音生成)|"
    r"深度合成.{0,20}算法备案|网信办.{0,35}(大模型|生成式|算法).{0,35}备案|"
    r"(大模型|生成式人工智能|AIGC).{0,35}(备案通过|通过备案|完成备案|备案成功|已备案|获.{0,10}备案|取得.{0,10}备案)|"
    r"生成式人工智能服务.*?安全评估"
)

ALGORITHM_GENAI_RE = re.compile(
    r"深度合成|生成式|AIGC|大模型|大语言模型|文本生成|图像生成|语音生成|视频生成|数字人|虚拟人|"
    r"自然语言生成|对话生成|智能问答|内容生成"
)

BAD_MODEL_RE = re.compile(
    r"估值模型|减值模型|定价模型|信用损失模型|预期信用损失模型|评估模型|测算模型|财务模型|"
    r"数学模型|业务模型|商业模型|盈利模型|模型计算|模型测算|模型预测|风险模型|回归模型|"
    r"Black[- ]?Scholes|二叉树模型|期权.*模型|计量模型|水文模型|气象模型|仿真模型"
)

BAD_FILING_RE = re.compile(
    r"国资委备案|发改委备案|项目备案|项目.{0,25}备案|投资项目备案|备案文件|备案证|"
    r"环评备案|环保备案|工商备案|工商.{0,10}备案|登记备案|备案登记|备案制|"
    r"公司章程备案|证券交易所备案|交易所备案|募集资金.*?备案|私募.*?备案|基金.*?备案|"
    r"基金业协会|专业投资机构共同投资|"
    r"ICP备案|域名备案|海关备案|税务备案|房屋.*?备案|土地.*?备案|车辆.*?备案|"
    r"药品.*?备案|医疗器械.*?备案|高新技术企业备案|科技型中小企业备案|合同备案|招投标备案"
)

NOISY_TITLE_RE = re.compile(
    r"年度报告|半年度报告|季度报告|募集说明书|上市保荐书|法律意见书|审计报告|资产评估报告|"
    r"问询函|关注函|回复|反馈意见|审核问询|投资者关系活动记录表|调研活动信息|业绩说明会|"
    r"董事会|监事会|股东大会|决议|独立董事|向特定对象发行|发行股票|可转换公司债券|"
    r"重组报告书|独立财务顾问|股权激励|公司章程|可行性研究|可研|募集资金|"
    r"收购报告书|权益变动报告书|社会责任报告|环境、社会及治理报告|ESG报告"
)

ANCHOR_RE = re.compile(r"备案|安全评估|网信办|国家互联网信息办公室|算法备案|深度合成")
OFFICIAL_FILING_CONTEXT_RE = re.compile(
    r"网信办|国家互联网信息办公室|生成式人工智能服务|算法备案|备案号|备案许可|备案资格|备案审核|备案评测|深度合成"
)


def clean_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value)
    text = re.sub(r"\s+", "", text)
    return text


def short(value: object, width: int = 180) -> str:
    text = clean_text(value)
    return text[:width]


def truthy(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.lower().isin(["true", "1", "yes", "y"])


def read_source(label: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    head = pd.read_csv(path, nrows=0)
    usecols = [col for col in KEEP_COLS if col in head.columns]
    df = pd.read_csv(path, dtype=str, low_memory=False, usecols=usecols)
    for col in KEEP_COLS:
        if col not in df.columns:
            df[col] = ""
    df["source_universe"] = label
    return df


def combine_sources() -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = [read_source(label, path) for label, path in SOURCE_PATHS]
    raw = pd.concat(frames, ignore_index=True)
    raw["is_formal_bool"] = truthy(raw["is_a_share_formal_row"])
    raw = raw[raw["is_formal_bool"]].copy()
    raw["announcement_id"] = raw["announcement_id"].astype(str)

    source_map = (
        raw.groupby("announcement_id")["source_universe"]
        .apply(lambda s: ";".join(sorted(set(s.astype(str)))))
        .rename("source_universes")
    )
    dedup = raw.sort_values(["announcement_id", "source_universe"]).drop_duplicates("announcement_id").copy()
    dedup = dedup.merge(source_map, on="announcement_id", how="left")
    flow = pd.DataFrame(
        [
            {"metric": "raw_source_rows", "value": len(pd.concat(frames, ignore_index=True))},
            {"metric": "formal_source_rows", "value": len(raw)},
            {"metric": "dedup_formal_announcements", "value": dedup["announcement_id"].nunique()},
            {"metric": "dedup_formal_firms", "value": dedup["sec_code"].nunique()},
        ]
    )
    return dedup, flow


def extract_windows(text: str, radius: int = 120, max_windows: int = 5) -> list[str]:
    if not text:
        return []
    windows: list[str] = []
    for match in ANCHOR_RE.finditer(text):
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        window = text[start:end]
        if window not in windows:
            windows.append(window)
        if len(windows) >= max_windows:
            break
    return windows


def window_is_candidate(window: str) -> bool:
    if not window:
        return False
    has_filing = bool(FILING_RE.search(window))
    has_strong_filing = bool(STRONG_FILING_RE.search(window))
    has_genai = bool(GENAI_RE.search(window))
    has_algorithm_genai = bool(re.search(r"算法备案|深度合成服务算法备案|互联网信息服务算法备案", window)) and bool(
        ALGORITHM_GENAI_RE.search(window)
    )
    official_context = bool(OFFICIAL_FILING_CONTEXT_RE.search(window))
    bad_model_only = bool(BAD_MODEL_RE.search(window)) and not has_strong_filing
    bad_filing_only = bool(BAD_FILING_RE.search(window)) and not official_context
    return has_filing and (has_strong_filing or has_genai or has_algorithm_genai) and not bad_model_only and not bad_filing_only


def classify_row(row: pd.Series) -> pd.Series:
    title_text = clean_text(row.get("announcement_title", "")) + clean_text(row.get("short_title", ""))
    body_text = clean_text(row.get("announcement_content", "")) + clean_text(row.get("action_snippet", ""))

    title_has_filing = bool(FILING_RE.search(title_text))
    title_has_genai = bool(GENAI_RE.search(title_text) or STRONG_FILING_RE.search(title_text))
    title_bad = bool(BAD_MODEL_RE.search(title_text)) or (
        bool(BAD_FILING_RE.search(title_text)) and not bool(OFFICIAL_FILING_CONTEXT_RE.search(title_text))
    )
    title_candidate = title_has_filing and title_has_genai and not title_bad

    body_windows = extract_windows(body_text)
    matched_body_windows = [window for window in body_windows if window_is_candidate(window)]
    any_window = matched_body_windows[0] if matched_body_windows else ""

    scan_text = title_text + any_window
    strong_phrase = bool(STRONG_FILING_RE.search(scan_text))
    algorithm_genai = bool(re.search(r"算法备案|深度合成服务算法备案|互联网信息服务算法备案", scan_text)) and bool(
        ALGORITHM_GENAI_RE.search(scan_text)
    )
    official_context = bool(OFFICIAL_FILING_CONTEXT_RE.search(scan_text))
    bad_context = bool(BAD_MODEL_RE.search(scan_text) and not strong_phrase) or bool(
        BAD_FILING_RE.search(scan_text) and not official_context
    )
    noisy_title = bool(NOISY_TITLE_RE.search(title_text))

    hit_source = []
    if title_candidate:
        hit_source.append("title")
    if matched_body_windows:
        hit_source.append("body_window")

    strict = bool(hit_source) and not bad_context
    high_precision = strict and (title_candidate or strong_phrase)
    eventlike = strict and not noisy_title

    score = 0
    score += 3 if title_candidate else 0
    score += 2 if matched_body_windows else 0
    score += 2 if strong_phrase else 0
    score += 1 if algorithm_genai else 0
    score -= 2 if noisy_title else 0
    score -= 3 if bad_context else 0

    return pd.Series(
        {
            "title_filing_genai_hit": title_candidate,
            "body_window_filing_genai_hit": bool(matched_body_windows),
            "strong_filing_phrase_hit": strong_phrase,
            "algorithm_genai_filing_hit": algorithm_genai,
            "bad_context_hit": bad_context,
            "noisy_title_form": noisy_title,
            "strict_filing_candidate": strict,
            "high_precision_filing_candidate": high_precision,
            "eventlike_filing_candidate": eventlike,
            "filing_recall_score": score,
            "hit_source": ";".join(hit_source),
            "matched_filing_window": any_window,
        }
    )


def load_event_ids(path: Path, sample_filter: str | None = None) -> set[str]:
    if not path.exists():
        return set()
    df = pd.read_csv(path, dtype=str, low_memory=False)
    if sample_filter and "sample_name" in df.columns:
        df = df[df["sample_name"].eq(sample_filter)].copy()
    key = "event_id" if "event_id" in df.columns else "announcement_id"
    return set(df[key].dropna().astype(str))


def add_overlaps(candidates: pd.DataFrame) -> pd.DataFrame:
    v56_ids = load_event_ids(V56_EVENTS, "A_all")
    v60_ids = load_event_ids(V60_EVENTS)
    v61_ids = load_event_ids(V61_EVENTS)
    out = candidates.copy()
    out["in_v56_A_all"] = out["announcement_id"].astype(str).isin(v56_ids)
    out["in_v60_strict_core"] = out["announcement_id"].astype(str).isin(v60_ids)
    out["in_v61_modelapp"] = out["announcement_id"].astype(str).isin(v61_ids)
    out["outside_v56_A_all"] = ~out["in_v56_A_all"]
    return out


def cac_match_candidates(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty or not CAC_RECORDS.exists():
        candidates["cac_model_or_entity_window_hit"] = False
        candidates["cac_matched_terms"] = ""
        return candidates
    cac = pd.read_csv(CAC_RECORDS, dtype=str).fillna("")
    terms: set[str] = set()
    for col in ["model_name", "filing_entity"]:
        for value in cac[col].astype(str):
            value = clean_text(value)
            if len(value) >= 3:
                terms.add(value)
            for part in re.split(r"[（）()、,，/；;\\s]+", value):
                part = part.strip()
                if len(part) >= 4 and not re.search(r"有限公司|股份|科技|信息|北京|上海|深圳|广州|杭州|南京|成都|中国", part):
                    terms.add(part)
    ordered_terms = sorted(terms, key=len, reverse=True)

    matches: list[list[str]] = []
    for _, row in candidates.iterrows():
        text = clean_text(row.get("announcement_title", "")) + clean_text(row.get("matched_filing_window", ""))
        found = [term for term in ordered_terms if term and term in text][:8]
        matches.append(found)
    out = candidates.copy()
    out["cac_model_or_entity_window_hit"] = [bool(m) for m in matches]
    out["cac_matched_terms"] = [";".join(m) for m in matches]
    return out


def sample_counts(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    sample_defs = {
        "title_filing_genai_hit": "title_filing_genai_hit",
        "body_window_filing_genai_hit": "body_window_filing_genai_hit",
        "strict_filing_candidate": "strict_filing_candidate",
        "high_precision_filing_candidate": "high_precision_filing_candidate",
        "eventlike_filing_candidate": "eventlike_filing_candidate",
        "eventlike_outside_v56": "eventlike_outside_v56",
        "high_precision_outside_v56": "high_precision_outside_v56",
    }
    for label, col in sample_defs.items():
        if col not in df.columns:
            continue
        sub = df[df[col]].copy()
        rows.append(
            {
                "sample": label,
                "events": sub["announcement_id"].nunique(),
                "firms": sub["sec_code"].nunique(),
                "first_date": sub["announcement_date"].min() if not sub.empty else "",
                "last_date": sub["announcement_date"].max() if not sub.empty else "",
                "outside_v56_events": sub.loc[sub["outside_v56_A_all"], "announcement_id"].nunique() if "outside_v56_A_all" in sub else np.nan,
                "overlap_v56_A_events": sub.loc[sub["in_v56_A_all"], "announcement_id"].nunique() if "in_v56_A_all" in sub else np.nan,
            }
        )
    return pd.DataFrame(rows)


def by_year(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    for sample, col in [
        ("strict", "strict_filing_candidate"),
        ("high_precision", "high_precision_filing_candidate"),
        ("eventlike", "eventlike_filing_candidate"),
        ("eventlike_outside_v56", "eventlike_outside_v56"),
    ]:
        sub = df[df[col]].copy()
        if sub.empty:
            continue
        g = (
            sub.groupby("announcement_year", dropna=False)
            .agg(events=("announcement_id", "nunique"), firms=("sec_code", "nunique"))
            .reset_index()
        )
        g["sample"] = sample
        rows.append(g)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def first_per_firm(df: pd.DataFrame, col: str) -> pd.DataFrame:
    sub = df[df[col]].copy()
    if sub.empty:
        return sub
    sub["announcement_date_dt"] = pd.to_datetime(sub["announcement_date"], errors="coerce")
    return sub.sort_values(["sec_code", "announcement_date_dt", "announcement_id"]).drop_duplicates("sec_code")


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    out = out.head(limit).copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    lines = ["| " + " | ".join(out.columns) + " |", "|" + "|".join("---" for _ in out.columns) + "|"]
    for _, row in out.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]).replace("|", "\\|") for c in out.columns) + " |")
    return "\n".join(lines)


def write_doc(
    flow: pd.DataFrame,
    counts: pd.DataFrame,
    year_counts: pd.DataFrame,
    candidates: pd.DataFrame,
    outside: pd.DataFrame,
    first_eventlike: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    preview_cols = [
        "announcement_date",
        "sec_code",
        "sec_name",
        "announcement_title",
        "filing_recall_score",
        "hit_source",
        "matched_filing_window",
        "in_v56_A_all",
        "in_v60_strict_core",
        "in_v61_modelapp",
        "cac_model_or_entity_window_hit",
        "cac_matched_terms",
    ]
    lines = [
        "# v62 Filing-Based GenAI Recall Probe",
        "",
        "## Purpose",
        "",
        "This probe tests whether CAC GenAI service filing / algorithm-filing language can recover credible GenAI announcement events outside the current v56 A sample.",
        "",
        "Key guardrail: the matcher scans only actual announcement title, short title, full text, and action snippet. It deliberately excludes `query_terms` and `matched_genai_terms`, because those fields can concatenate retrieval keywords with unrelated filing language and create false `model + filing` hits.",
        "",
        "## Source Flow",
        "",
        md_table(flow),
        "",
        "## Recall Counts",
        "",
        md_table(counts),
        "",
        "## By Year",
        "",
        md_table(year_counts, limit=80),
        "",
        "## High-Precision / Event-Like Candidates Outside v56",
        "",
        md_table(outside[preview_cols], limit=80),
        "",
        "## First Event-Like Filing Candidate Per Firm",
        "",
        md_table(first_eventlike[preview_cols], limit=80),
        "",
        "## Interpretation",
        "",
        "- Filing-based retrieval is useful only when matching is window-based. A naive global `model + filing` rule is not usable because ordinary announcements contain valuation models, impairment models, project filings, corporate filings, and other non-GenAI filing language.",
        "- `eventlike_filing_candidate` is the preferred review queue for possible event-study expansion. `high_precision_filing_candidate` keeps strong filing phrases even when the announcement title form is noisy, so it is better for completeness auditing than direct event-study use.",
        "- The next step is to send the v56-outside event-like candidates to the same v3.3 LLM coding prompt, then append accepted A events to the expanded sample and rerun the v56/v58/v59 tables.",
        "",
        "## Outputs",
        "",
        f"- `{OUT_DIR / 'filing_recall_candidates.csv'}`",
        f"- `{OUT_DIR / 'filing_recall_candidates_outside_v56.csv'}`",
        f"- `{OUT_DIR / 'filing_recall_first_eventlike_per_firm.csv'}`",
        f"- `{OUT_DIR / 'filing_recall_summary.csv'}`",
        f"- `{OUT_DIR / 'filing_recall_by_year.csv'}`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df, flow = combine_sources()

    classifications = df.apply(classify_row, axis=1)
    scored = pd.concat([df.reset_index(drop=True), classifications.reset_index(drop=True)], axis=1)
    candidates = scored[scored["strict_filing_candidate"]].copy()
    candidates = add_overlaps(candidates)
    candidates["eventlike_outside_v56"] = candidates["eventlike_filing_candidate"] & candidates["outside_v56_A_all"]
    candidates["high_precision_outside_v56"] = candidates["high_precision_filing_candidate"] & candidates["outside_v56_A_all"]
    candidates = cac_match_candidates(candidates)

    sort_cols = ["filing_recall_score", "eventlike_filing_candidate", "title_filing_genai_hit", "body_window_filing_genai_hit"]
    candidates = candidates.sort_values(sort_cols + ["announcement_date"], ascending=[False, False, False, False, True])

    outside = candidates[candidates["eventlike_outside_v56"] | candidates["high_precision_outside_v56"]].copy()
    outside = outside.sort_values(sort_cols + ["announcement_date"], ascending=[False, False, False, False, True])

    first_eventlike = first_per_firm(candidates, "eventlike_filing_candidate")

    counts = sample_counts(candidates)
    year_counts = by_year(candidates)

    candidates.to_csv(OUT_DIR / "filing_recall_candidates.csv", index=False)
    outside.to_csv(OUT_DIR / "filing_recall_candidates_outside_v56.csv", index=False)
    first_eventlike.to_csv(OUT_DIR / "filing_recall_first_eventlike_per_firm.csv", index=False)
    counts.to_csv(OUT_DIR / "filing_recall_summary.csv", index=False)
    year_counts.to_csv(OUT_DIR / "filing_recall_by_year.csv", index=False)
    flow.to_csv(OUT_DIR / "filing_recall_source_flow.csv", index=False)

    write_doc(flow, counts, year_counts, candidates, outside, first_eventlike)
    print(f"Wrote {OUT_DIR}")
    print(f"Wrote {DOC_PATH}")
    print(counts.to_string(index=False))


if __name__ == "__main__":
    main()
