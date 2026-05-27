#!/usr/bin/env python3
"""Build the 300-event specificity validation sample and coding templates."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FOCAL_EVENTS = (
    ROOT
    / "results"
    / "csmar_v5_1_response_smoke_20260523"
    / "csmar_conservative_focal_events_2023_2026.csv"
)
HEADLINE_SAMPLE = (
    ROOT
    / "results"
    / "v6_focal_good_news_pretrend_checks_20260525"
    / "analysis_sample_top5.csv.gz"
)
OUT_DIR = ROOT / "data" / "specificity_validation"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "55_specificity_validation_sample_20260525.md"
SEED = 20260525
TARGET_N = 300


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def source_group(sources: object) -> str:
    text = str(sources or "")
    has_iip = "csmar_investor_interaction" in text
    has_irqa = "csmar_ir_meeting_qa" in text
    if has_iip and has_irqa:
        return "mixed_iip_irqa"
    if has_iip:
        return "iip_only"
    if has_irqa:
        return "irqa_only"
    return "other"


def clean_text(value: object, max_len: int = 1800) -> str:
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def load_events() -> pd.DataFrame:
    focal = pd.read_csv(FOCAL_EVENTS, dtype={"event_id": str, "focal_code": str, "stock_code": str})
    focal["focal_code"] = focal["focal_code"].map(code6)
    focal["event_date"] = pd.to_datetime(focal["event_date"], errors="coerce")

    headline = pd.read_csv(
        HEADLINE_SAMPLE,
        dtype={"event_id": str, "focal_code": str, "peer_code": str},
        usecols=["event_id", "focal_code", "event_date", "specificity_z"],
    )
    headline["focal_code"] = headline["focal_code"].map(code6)
    headline["event_date"] = pd.to_datetime(headline["event_date"], errors="coerce")
    headline_events = (
        headline.drop_duplicates("event_id")[["event_id", "specificity_z"]]
        .rename(columns={"specificity_z": "headline_specificity_z"})
        .copy()
    )

    events = focal.merge(headline_events, on="event_id", how="inner")
    events = events.drop_duplicates("event_id").copy()
    events["specificity_z"] = pd.to_numeric(events["headline_specificity_z"], errors="coerce")
    events["specificity"] = pd.to_numeric(events["specificity"], errors="coerce")
    events["event_year"] = events["event_date"].dt.year
    events["source_group"] = events["sources"].map(source_group)
    events["sample_answer"] = events["sample_answer"].map(clean_text)
    events["sample_question"] = events["sample_question"].map(lambda x: clean_text(x, 900))
    events = events.dropna(subset=["specificity_z", "event_date", "sample_answer"])
    events["specificity_bin"] = pd.qcut(
        events["specificity_z"].rank(method="first"),
        q=3,
        labels=["low", "mid", "high"],
    )
    return events


def draw_sample(events: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    events = events.copy()
    events["sample_random"] = rng.random(len(events))

    selected_parts = []
    per_bin = TARGET_N // 3
    for label in ["low", "mid", "high"]:
        sub = events[events["specificity_bin"].astype(str).eq(label)].copy()
        take = min(per_bin, len(sub))
        selected_parts.append(sub.sort_values("sample_random").head(take))

    selected = pd.concat(selected_parts, ignore_index=True)
    remaining_n = TARGET_N - len(selected)
    if remaining_n > 0:
        rest = events[~events["event_id"].isin(selected["event_id"])].copy()
        selected = pd.concat([selected, rest.sort_values("sample_random").head(remaining_n)], ignore_index=True)
    elif len(selected) > TARGET_N:
        selected = selected.sort_values("sample_random").head(TARGET_N).copy()

    selected = selected.sort_values(["specificity_bin", "source_group", "event_date", "event_id"]).reset_index(drop=True)
    selected.insert(0, "validation_id", [f"SV{idx:04d}" for idx in range(1, len(selected) + 1)])
    return selected


def add_coding_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    prefix_cols = ["coder_id", "coding_date"]
    for col in reversed(prefix_cols):
        out.insert(0, col, "")
    coding_cols = [
        "has_specific_product_service",
        "has_model_platform_name",
        "has_specific_use_case",
        "has_customer_or_industry",
        "has_partner_or_org",
        "has_deployment_status",
        "has_commercialization_or_timeline",
        "has_quantitative_commitment",
        "specificity_score_0_4",
        "uncertain_flag",
        "evidence_snippet",
        "coder_notes",
    ]
    for col in coding_cols:
        out[col] = ""
    return out


def write_jsonl(df: pd.DataFrame, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            rec = {
                "validation_id": row["validation_id"],
                "event_id": row["event_id"],
                "company_name": row.get("company_name", ""),
                "focal_code": row.get("focal_code", ""),
                "event_date": str(pd.Timestamp(row["event_date"]).date()),
                "sources": row.get("sources", ""),
                "specificity_bin": str(row.get("specificity_bin", "")),
                "sample_question": row.get("sample_question", ""),
                "sample_answer": row.get("sample_answer", ""),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    events = load_events()
    sample = draw_sample(events)

    keep_cols = [
        "validation_id",
        "event_id",
        "focal_code",
        "company_name",
        "event_date",
        "event_year",
        "sources",
        "source_group",
        "answer_level_events",
        "answer_terms",
        "question_terms",
        "specificity",
        "specificity_z",
        "specificity_bin",
        "total_specific_items",
        "total_genai_span_tokens",
        "total_genai_mentions",
        "sample_question",
        "sample_answer",
    ]
    sample_out = sample[keep_cols].copy()
    sample_out["event_date"] = sample_out["event_date"].dt.strftime("%Y-%m-%d")

    coding_template = add_coding_columns(sample_out)

    sample_path = OUT_DIR / "specificity_validation_sample_300_20260525.csv"
    template_path = OUT_DIR / "specificity_validation_coding_template_300_20260525.csv"
    llm_path = OUT_DIR / "specificity_validation_llm_input_300_20260525.jsonl"
    summary_path = OUT_DIR / "specificity_validation_sample_summary_20260525.csv"

    sample_out.to_csv(sample_path, index=False)
    coding_template.to_csv(template_path, index=False)
    write_jsonl(sample_out, llm_path)

    summary = (
        sample_out.groupby(["specificity_bin", "source_group", "event_year"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values(["specificity_bin", "source_group", "event_year"])
    )
    summary.to_csv(summary_path, index=False)

    by_bin = sample_out.groupby("specificity_bin").size().to_dict()
    by_source = sample_out.groupby("source_group").size().to_dict()
    by_year = sample_out.groupby("event_year").size().to_dict()

    doc = f"""# Specificity Validation Sample

Date: 2026-05-25

Purpose: create a frozen 300-event sample for human + LLM validation of `Specificity_z`.

## Sampling Frame

Sampling frame is the focal-event universe used by the current headline Top5 peer-CAR specification:

```text
first focal GenAI events
Top5 product-market peer analysis sample
announcement-cleaned market-reaction pipeline
eligible focal events = {events['event_id'].nunique():,}
```

## Sample Construction

The script draws 300 events with deterministic seed `{SEED}`. It balances across `Specificity_z` terciles:

```text
{by_bin}
```

Source distribution:

```text
{by_source}
```

Year distribution:

```text
{by_year}
```

## Output Files

- `data/specificity_validation/specificity_validation_sample_300_20260525.csv`
- `data/specificity_validation/specificity_validation_coding_template_300_20260525.csv`
- `data/specificity_validation/specificity_validation_llm_input_300_20260525.jsonl`
- `data/specificity_validation/specificity_validation_sample_summary_20260525.csv`

## Coding Files

Use the codebook:

```text
docs/design/06_specificity_validation_codebook_20260525.md
```

Use the LLM prompt:

```text
docs/prompts/55_specificity_validation_llm_coding_prompt_20260525.md
```

## Next Step

1. Run LLM coding on the JSONL input.
2. Human-code the CSV template or a fully overlapping subset.
3. Compute agreement and construct-validation regressions.
4. Use future CAC / AI patent / AI hiring / product launch only as convergent validity, not as main Y.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"eligible events: {events['event_id'].nunique():,}")
    print(f"sample events: {len(sample_out):,}")
    print(f"wrote {sample_path}")
    print(f"wrote {template_path}")
    print(f"wrote {llm_path}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
