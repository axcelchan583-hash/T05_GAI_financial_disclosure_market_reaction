#!/usr/bin/env python3
"""Annual-report broad-collaborator probe for v36 GenAI events.

This run builds a pre-event broad collaborator set from focal firms' latest
available annual reports. It then compares the stock-market reaction of these
listed collaborators with the existing product-market competitor panel.
"""

from __future__ import annotations

import math
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_v38_wide_collaborator_competitor_probe_20260607 as v38  # noqa: E402
import run_v39_broad_collaborator_text_probe_20260607 as v39  # noqa: E402


RUN_ID = "v40_annual_report_collaborator_probe_20260607"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "104_v40_annual_report_collaborator_probe_20260607.md"

ANNUAL_TXT_ZIP_DIR = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司年报信息/年报文本/2001~2024年年报/2001-2024年A股年报TXT格式"
)
ANNUAL_2025_TXT_DIR = ROOT / "data" / "raw" / "annual_reports_2025_txt" / "年报txt"

REPORT_YEARS = range(2020, 2025)
ASSUMED_2025_DISCLOSURE_DATE = pd.Timestamp("2026-04-30")

ANNUAL_RELATION_KEYWORDS = [
    "战略合作",
    "合作伙伴",
    "合作方",
    "合作协议",
    "框架协议",
    "联合研发",
    "共同研发",
    "联合开发",
    "共同开发",
    "共建",
    "生态伙伴",
    "产业链伙伴",
    "业务合作",
    "项目合作",
    "签署",
    "中标",
    "合同",
    "订单",
    "采购",
    "供应",
    "供应商",
    "客户",
    "主要客户",
    "前五大客户",
    "主要供应商",
    "前五大供应商",
    "销售给",
    "采购自",
    "委托",
    "授权",
    "服务于",
    "参股",
    "合资",
]

ANNUAL_CONTEXT_EXCLUDE_KEYWORDS = [
    "保荐",
    "承销",
    "律师事务所",
    "会计师事务所",
    "审计机构",
    "法律意见",
    "核查意见",
    "募集资金",
    "受托管理",
    "独立财务顾问",
    "评级机构",
    "证券事务",
    "股东大会见证",
    "授信",
    "贷款",
    "质押",
    "抵押",
    "担保",
    "银行承兑",
    "保理",
    "融资租赁",
    "理财产品",
    "募集资金专户",
    "曾任",
    "历任",
    "出生",
    "个人简历",
    "履历",
    "学历",
    "任职资格",
    "董事",
    "监事",
    "高级管理人员",
]

ANNUAL_ALIAS_STOPLIST = {
    # Short stock names that frequently appear as common nouns or substrings in
    # annual reports rather than as listed counterparties.
    "中关村",
    "新世界",
    "东方集团",
    "氯碱化工",
    "数码科技",
}


def code6(value: object) -> str:
    return v38.code6(value)


def clean_id(value: object) -> str:
    return v38.clean_id(value)


def annual_report_zips() -> list[Path]:
    paths = []
    for year in REPORT_YEARS:
        matches = sorted(ANNUAL_TXT_ZIP_DIR.glob(f"{year}_*.zip"))
        if matches:
            paths.append(matches[0])
    return paths


def parse_zip_member(zip_path: Path, member: str) -> dict[str, object] | None:
    if not member.endswith(".txt"):
        return None
    name = Path(member).name
    parts = name[:-4].split("_")
    if len(parts) < 5:
        return None
    code = code6(parts[0])
    report_year = pd.to_numeric(parts[1], errors="coerce")
    disclosure_date = pd.to_datetime(parts[-1], errors="coerce")
    if not code or pd.isna(report_year) or pd.isna(disclosure_date):
        return None
    stock_name = v39.clean_name(parts[2])
    title = "_".join(parts[3:-1])
    return {
        "stock_code": code,
        "stock_name": stock_name,
        "report_year": int(report_year),
        "report_title": title,
        "disclosure_date": disclosure_date,
        "disclosure_date_source": "filename",
        "storage_type": "zip",
        "container_path": str(zip_path),
        "member_path": member,
        "file_path": "",
    }


def parse_2025_file(path: Path) -> dict[str, object] | None:
    parts = path.stem.split("_")
    if len(parts) < 3:
        return None
    code = code6(parts[0])
    report_year = pd.to_numeric(parts[-1], errors="coerce")
    if not code or pd.isna(report_year) or int(report_year) != 2025:
        return None
    stock_name = v39.clean_name("_".join(parts[1:-1]))
    return {
        "stock_code": code,
        "stock_name": stock_name,
        "report_year": 2025,
        "report_title": "2025年年度报告",
        "disclosure_date": ASSUMED_2025_DISCLOSURE_DATE,
        "disclosure_date_source": "assumed_2026_04_30_from_annual_report_deadline",
        "storage_type": "file",
        "container_path": "",
        "member_path": "",
        "file_path": str(path),
    }


def build_annual_report_index() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for zip_path in annual_report_zips():
        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.namelist():
                row = parse_zip_member(zip_path, member)
                if row is not None:
                    rows.append(row)
    if ANNUAL_2025_TXT_DIR.exists():
        for path in ANNUAL_2025_TXT_DIR.glob("*.txt"):
            row = parse_2025_file(path)
            if row is not None:
                rows.append(row)
    idx = pd.DataFrame(rows)
    if idx.empty:
        return idx
    idx["disclosure_date"] = pd.to_datetime(idx["disclosure_date"], errors="coerce")
    idx = idx[idx["disclosure_date"].notna()].copy()
    idx = idx.sort_values(["stock_code", "disclosure_date", "report_year"])
    return idx.reset_index(drop=True)


def add_annual_names(dictionary: pd.DataFrame, annual_index: pd.DataFrame) -> pd.DataFrame:
    records = dictionary.to_dict("records") if not dictionary.empty else []
    for _, row in annual_index[["stock_code", "stock_name"]].drop_duplicates().iterrows():
        v39.add_name(records, row["stock_code"], row["stock_name"], "annual_report_index")
    out = pd.DataFrame(records).drop_duplicates()
    if out.empty:
        return out
    out["alias_len"] = out["alias"].str.len()
    out = out.sort_values(["alias_len", "alias"], ascending=[False, True])
    out = out.drop_duplicates(["stock_code", "alias"], keep="first")
    out = out[
        ~out["alias"].isin({"股份有限公司", "有限责任公司", "集团股份", "科技股份"})
        & ~out["alias"].isin(v39.GENERIC_STOCK_ALIAS_STOPLIST)
        & ~out["alias"].isin(ANNUAL_ALIAS_STOPLIST)
    ].copy()
    return out.reset_index(drop=True)


def select_pre_event_reports(events: pd.DataFrame, annual_index: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    by_code = {code: d.copy() for code, d in annual_index.groupby("stock_code")}
    for _, event in events.iterrows():
        event_date = pd.to_datetime(event.get("event_date"), errors="coerce")
        focal_code = code6(event.get("focal_code"))
        if not focal_code or pd.isna(event_date):
            continue
        candidates = by_code.get(focal_code)
        if candidates is None or candidates.empty:
            continue
        strict = candidates[candidates["disclosure_date"] < event_date].copy()
        # The 2025 file names do not contain exact disclosure dates. Keep the
        # conservative deadline-based proxy only for events after Apr. 30, 2026.
        if event_date <= ASSUMED_2025_DISCLOSURE_DATE:
            strict = strict[~strict["disclosure_date_source"].str.startswith("assumed_", na=False)].copy()
        if strict.empty:
            continue
        chosen = strict.sort_values(["disclosure_date", "report_year"]).iloc[-1].to_dict()
        row = {**event.to_dict(), **{f"report_{k}": v for k, v in chosen.items()}}
        rows.append(row)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["report_disclosure_date"] = pd.to_datetime(out["report_disclosure_date"], errors="coerce")
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["report_lag_days"] = (out["event_date"] - out["report_disclosure_date"]).dt.days
    return out.reset_index(drop=True)


def read_report_text(row: pd.Series) -> str:
    storage_type = str(row.get("report_storage_type") or "")
    if storage_type == "zip":
        zip_path = Path(str(row.get("report_container_path") or ""))
        member = str(row.get("report_member_path") or "")
        if not zip_path.exists() or not member:
            return ""
        try:
            with zipfile.ZipFile(zip_path) as zf:
                raw = zf.read(member)
        except Exception:
            return ""
    else:
        path = Path(str(row.get("report_file_path") or ""))
        if not path.exists():
            return ""
        try:
            raw = path.read_bytes()
        except Exception:
            return ""
    for encoding in ["utf-8", "gb18030", "gbk"]:
        try:
            return raw.decode(encoding, errors="ignore")
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")


def relation_context_text(text: str, window: int = 180, max_chars: int = 450_000) -> str:
    if not isinstance(text, str) or not text:
        return ""
    spans: list[tuple[int, int]] = []
    for keyword in ANNUAL_RELATION_KEYWORDS:
        start = 0
        while True:
            pos = text.find(keyword, start)
            if pos < 0:
                break
            spans.append((max(0, pos - window), min(len(text), pos + len(keyword) + window)))
            start = pos + len(keyword)
    if not spans:
        return ""
    spans.sort()
    merged: list[list[int]] = []
    for left, right in spans:
        if not merged or left > merged[-1][1] + 30:
            merged.append([left, right])
        else:
            merged[-1][1] = max(merged[-1][1], right)
    chunks = []
    total = 0
    for left, right in merged:
        chunk = text[left:right]
        if any(k in chunk for k in ANNUAL_CONTEXT_EXCLUDE_KEYWORDS):
            continue
        chunks.append(chunk)
        total += len(chunk)
        if total >= max_chars:
            break
    return "\n".join(chunks)


def has_prefix_boundary(text: str, alias: str) -> bool:
    for match in re.finditer(re.escape(alias), text):
        if match.start() == 0:
            return True
        before = text[match.start() - 1]
        if not ("\u4e00" <= before <= "\u9fff") and not before.isalnum():
            return True
    return False


def plausible_annual_match(row: pd.Series) -> bool:
    evidence = str(row.get("match_evidence") or "")
    alias = str(row.get("matched_alias") or "")
    if not evidence or not alias:
        return False
    if any(k in evidence for k in ANNUAL_CONTEXT_EXCLUDE_KEYWORDS):
        return False
    if not has_prefix_boundary(evidence, alias):
        return False
    strong_keywords = "(战略合作|合作协议|框架协议|合作伙伴|合作方|联合研发|共同研发|共建|签署|合同|中标|客户|供应商|采购|销售)"
    escaped = re.escape(alias)
    patterns = [
        rf"与[^。；\n\r]{{0,50}}{escaped}[^。；\n\r]{{0,100}}{strong_keywords}",
        rf"{escaped}[^。；\n\r]{{0,100}}{strong_keywords}",
        rf"(客户|供应商|合作伙伴|合作方|战略客户|战略合作客户)[^。；\n\r]{{0,120}}{escaped}",
        rf"(包括|涵盖|如|例如)[^。；\n\r]{{0,120}}{escaped}[^。；\n\r]{{0,80}}(客户|供应商|合作伙伴|合作关系|战略合作)",
    ]
    return any(re.search(pattern, evidence) for pattern in patterns)


def build_annual_report_links(selected_reports: pd.DataFrame, dictionary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    for i, (_, selected) in enumerate(selected_reports.iterrows(), start=1):
        text = read_report_text(selected)
        context = relation_context_text(text)
        if not context:
            continue
        event = pd.Series(
            {
                "sample_name": selected.get("sample_name"),
                "event_id": selected.get("event_id"),
                "event_key": selected.get("event_key"),
                "focal_code": selected.get("focal_code"),
                "focal_name": selected.get("focal_name"),
                "event_date": selected.get("event_date"),
                "event_year": selected.get("event_year"),
                "announcement_title": selected.get("announcement_title"),
                "auto_pdf_label": selected.get("auto_pdf_label"),
                "candidate_row_type": selected.get("candidate_row_type"),
            }
        )
        links = v39.extract_listed_partners_from_text(
            event=event,
            text=context,
            dictionary=dictionary,
            source="annual_report_listed_collaborator",
            doc_date=selected.get("report_disclosure_date"),
            doc_id=f"{selected.get('report_stock_code')}_{selected.get('report_report_year')}",
            doc_title=str(selected.get("report_report_title") or ""),
            context_window=110,
        )
        for link in links:
            link["relation_year"] = int(selected.get("report_report_year"))
            link["report_year"] = int(selected.get("report_report_year"))
            link["report_disclosure_date"] = selected.get("report_disclosure_date")
            link["report_disclosure_date_source"] = selected.get("report_disclosure_date_source")
            link["report_title"] = selected.get("report_report_title")
            link["report_lag_days"] = selected.get("report_lag_days")
        rows.extend(links)
        if i % 50 == 0:
            print(f"processed annual reports: {i:,}/{len(selected_reports):,}; links={len(rows):,}")
    if not rows:
        return pd.DataFrame(), pd.DataFrame()
    raw = pd.DataFrame(rows)
    raw = raw.sort_values(
        ["event_key", "related_code", "match_score", "report_disclosure_date"],
        ascending=[True, True, False, False],
    )
    raw = raw.drop_duplicates(["event_key", "related_code"], keep="first").reset_index(drop=True)
    strict = raw[raw.apply(plausible_annual_match, axis=1)].copy().reset_index(drop=True)
    return raw, strict


def annual_source_summary(
    events: pd.DataFrame,
    annual_index: pd.DataFrame,
    selected_reports: pd.DataFrame,
    candidate_links: pd.DataFrame,
    strict_links: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        {
            "layer": "v36_first_events",
            "rows": len(events),
            "events": events["event_key"].nunique(),
            "focal_firms": events["focal_code"].nunique(),
            "related_firms": np.nan,
        },
        {
            "layer": "annual_report_index_2020_2025",
            "rows": len(annual_index),
            "events": np.nan,
            "focal_firms": annual_index["stock_code"].nunique() if not annual_index.empty else 0,
            "related_firms": np.nan,
        },
        {
            "layer": "selected_latest_pre_event_report",
            "rows": len(selected_reports),
            "events": selected_reports["event_key"].nunique() if not selected_reports.empty else 0,
            "focal_firms": selected_reports["focal_code"].nunique() if not selected_reports.empty else 0,
            "related_firms": np.nan,
        },
        {
            "layer": "annual_report_listed_collaborator_candidates_raw",
            "rows": len(candidate_links),
            "events": candidate_links["event_key"].nunique() if not candidate_links.empty else 0,
            "focal_firms": candidate_links["focal_code"].nunique() if not candidate_links.empty else 0,
            "related_firms": candidate_links["related_code"].nunique() if not candidate_links.empty else 0,
        },
        {
            "layer": "annual_report_listed_collaborator_high_precision",
            "rows": len(strict_links),
            "events": strict_links["event_key"].nunique() if not strict_links.empty else 0,
            "focal_firms": strict_links["focal_code"].nunique() if not strict_links.empty else 0,
            "related_firms": strict_links["related_code"].nunique() if not strict_links.empty else 0,
        },
    ]
    return pd.DataFrame(rows)


def build_sample_flow(events: pd.DataFrame, competitor: pd.DataFrame, annual_returns: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "layer": "v36_first_events",
            "linked_rows": len(events),
            "events": events["event_key"].nunique(),
            "focal_firms": events["focal_code"].nunique(),
            "related_firms": np.nan,
            "clean_car0p1_rows": np.nan,
            "clean_car0p1_events": np.nan,
        },
        {
            "layer": "competitor_returns",
            "linked_rows": len(competitor),
            "events": competitor["event_key"].nunique(),
            "focal_firms": competitor["focal_code"].nunique(),
            "related_firms": competitor["related_code"].nunique(),
            "clean_car0p1_rows": int((competitor["complete_clean_m1_p1"].eq(1) & competitor["peer_car_0_p1_mm"].notna()).sum()),
            "clean_car0p1_events": competitor[
                competitor["complete_clean_m1_p1"].eq(1) & competitor["peer_car_0_p1_mm"].notna()
            ]["event_key"].nunique(),
        },
    ]
    for relation_type, df in annual_returns.groupby("relation_type", dropna=False):
        clean = df[df["complete_clean_m1_p1"].eq(1) & df["peer_car_0_p1_mm"].notna()]
        rows.append(
            {
                "layer": f"{relation_type}_returns",
                "linked_rows": len(df),
                "events": df["event_key"].nunique(),
                "focal_firms": df["focal_code"].nunique(),
                "related_firms": df["related_code"].nunique(),
                "clean_car0p1_rows": len(clean),
                "clean_car0p1_events": clean["event_key"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def standardize_plus(df: pd.DataFrame, relation_group: str) -> pd.DataFrame:
    out = v39.standardize_plus(df, relation_group)
    extra_cols = [
        "related_name",
        "matched_alias",
        "report_year",
        "report_disclosure_date",
        "report_disclosure_date_source",
        "report_title",
        "report_lag_days",
        "match_score",
        "match_evidence",
    ]
    for col in extra_cols:
        if col in df.columns and len(df) == len(out):
            out[col] = df[col].values
        elif col not in out.columns:
            out[col] = np.nan
    return out


def prepare_stack(competitor: pd.DataFrame, annual_returns: pd.DataFrame) -> pd.DataFrame:
    comp = standardize_plus(competitor, "competitor")
    annual = standardize_plus(annual_returns, "cooperative")
    comp["cooperative"] = 0
    annual["cooperative"] = 1
    annual_keys = set(zip(annual["event_key"], annual["related_code"]))
    comp = comp[~pd.Series(list(zip(comp["event_key"], comp["related_code"])), index=comp.index).isin(annual_keys)].copy()
    return pd.concat([comp, annual], ignore_index=True)


def write_report(
    source_summary: pd.DataFrame,
    flow: pd.DataFrame,
    event_study: pd.DataFrame,
    regressions: pd.DataFrame,
    examples: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    car = event_study[event_study["window"].eq("CAR[0,+1]")].copy()
    text = f"""# v40 Annual-Report Collaborator Probe

Date: 2026-06-07

## Scope

This run responds to the redesigned Y idea: compare product-market competitors with broad pre-existing collaborators. Collaborators are not limited to GenAI-specific partners. For each v36 first GenAI event, we select the focal firm's latest annual report whose disclosure date is before the event date, then extract listed firms named near cooperation, customer, supplier, contract, joint R&D, and strategic-partner language.

The event-study panel below uses the high-precision rule set. The wider raw candidate pool is kept for manual validation, because short Chinese stock names can be false matches in annual reports.

The 2020-2024 annual-report files are read directly from the CSMAR TXT zip archive. Their filenames include exact disclosure dates. The local 2025 annual-report text files do not include exact disclosure dates, so they are used only for events after 2026-04-30 and are flagged as deadline-assumed.

## Source Summary

{v38.md_table(source_summary, max_rows=80)}

## Sample Flow

{v38.md_table(flow, max_rows=80)}

## CAR[0,+1] by Relation Type

{v38.md_table(
        car[
            [
                "relation_type",
                "mean",
                "se",
                "p",
                "nobs",
                "events",
                "related_firms",
                "positive_share",
                "event_weighted_mean",
                "event_weighted_p",
                "event_weighted_events",
            ]
        ]
        if not car.empty
        else car,
        max_rows=80,
    )}

## Stacked Event-FE Regression

Baseline group is product-market competitors. Competitor rows overlapping with annual-report collaborators are removed.

{v38.md_table(
        regressions[
            [
                "sample",
                "outcome",
                "regressor",
                "coef_event_fmt",
                "p_event_cluster",
                "coef_two_way_fmt",
                "p_two_way",
                "nobs",
                "events",
                "related_firms",
                "r2",
            ]
        ]
        if not regressions.empty
        else regressions,
        max_rows=80,
    )}

## Match Examples

{v38.md_table(
        examples[
            [
                "event_date",
                "focal_code",
                "focal_name",
                "related_code",
                "related_name",
                "report_year",
                "report_disclosure_date",
                "matched_alias",
                "match_score",
                "match_evidence",
            ]
        ]
        if not examples.empty
        else examples,
        max_rows=30,
    )}

## Reading Rules

- This is a machine-screening sample. Rows still need manual validation before entering a final paper table.
- Positive absolute collaborator CAR would support a clean collaborator-opportunity story.
- A positive stacked coefficient with non-positive absolute CAR would still mean collaborators are less damaged than competitors.
- A negative or null stacked coefficient means annual-report broad collaborators should not replace the competitor main Y without further hand cleaning.

## Output Files

- `results/{RUN_ID}/annual_report_index.csv`
- `results/{RUN_ID}/selected_pre_event_annual_reports.csv`
- `results/{RUN_ID}/annual_report_collaborator_candidates_raw.csv`
- `results/{RUN_ID}/annual_report_collaborator_links_high_precision.csv`
- `results/{RUN_ID}/annual_report_relation_event_study.csv`
- `results/{RUN_ID}/annual_report_stacked_regressions.csv`
- `results/{RUN_ID}/annual_report_relation_panel.csv.gz`
"""
    DOC_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    events = v38.load_v36_first_events()
    competitor, placebo = v38.load_competitor_panel()
    annual_index = build_annual_report_index()
    dictionary = add_annual_names(v39.build_company_dictionary(events, competitor), annual_index)
    selected_reports = select_pre_event_reports(events, annual_index)

    print(f"events={len(events):,}, competitor_rows={len(competitor):,}")
    print(
        f"annual_index_rows={len(annual_index):,}, stocks={annual_index['stock_code'].nunique() if not annual_index.empty else 0:,}"
    )
    print(f"dictionary_aliases={len(dictionary):,}, stocks={dictionary['stock_code'].nunique() if not dictionary.empty else 0:,}")
    print(f"selected_pre_event_reports={len(selected_reports):,}, events={selected_reports['event_key'].nunique() if not selected_reports.empty else 0:,}")

    candidate_links, links = build_annual_report_links(selected_reports, dictionary)
    source_summary = annual_source_summary(events, annual_index, selected_reports, candidate_links, links)
    print(source_summary.to_string(index=False))

    stock_model = v38.pe.load_stock_model()
    annual_returns = v38.attach_returns(links, stock_model) if not links.empty else links.copy()

    relation_panel = pd.concat(
        [
            standardize_plus(competitor, "competitor"),
            standardize_plus(placebo, "placebo"),
            standardize_plus(annual_returns, "cooperative"),
        ],
        ignore_index=True,
    )
    relation_panel.loc[relation_panel["relation_group"].eq("competitor"), "relation_type"] = "competitor"
    relation_panel.loc[relation_panel["relation_group"].eq("placebo"), "relation_type"] = "placebo_low_similarity"

    flow = build_sample_flow(events, competitor, annual_returns)
    event_study = v38.relation_event_study(relation_panel)
    stack = prepare_stack(competitor, annual_returns)
    regs = []
    for outcome, _ in v38.OUTCOMES:
        regs.append(v38.fit_event_fe(stack, outcome, ["cooperative"], "annual_report_collaborator_vs_competitor"))
    regressions = pd.concat([r for r in regs if not r.empty], ignore_index=True) if regs else pd.DataFrame()

    examples = links.sort_values(["match_score", "event_date"], ascending=[False, True]).head(100).copy() if not links.empty else pd.DataFrame()

    annual_index.to_csv(OUT_DIR / "annual_report_index.csv", index=False, encoding="utf-8-sig")
    dictionary.to_csv(OUT_DIR / "company_dictionary.csv", index=False, encoding="utf-8-sig")
    selected_reports.to_csv(OUT_DIR / "selected_pre_event_annual_reports.csv", index=False, encoding="utf-8-sig")
    candidate_links.to_csv(OUT_DIR / "annual_report_collaborator_candidates_raw.csv", index=False, encoding="utf-8-sig")
    links.to_csv(OUT_DIR / "annual_report_collaborator_links_high_precision.csv", index=False, encoding="utf-8-sig")
    source_summary.to_csv(OUT_DIR / "source_summary.csv", index=False, encoding="utf-8-sig")
    flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")
    event_study.to_csv(OUT_DIR / "annual_report_relation_event_study.csv", index=False, encoding="utf-8-sig")
    regressions.to_csv(OUT_DIR / "annual_report_stacked_regressions.csv", index=False, encoding="utf-8-sig")
    relation_panel.to_csv(OUT_DIR / "annual_report_relation_panel.csv.gz", index=False)
    stack.to_csv(OUT_DIR / "annual_report_stack_panel.csv.gz", index=False)

    write_report(source_summary, flow, event_study, regressions, examples)

    car = event_study[event_study["window"].eq("CAR[0,+1]")]
    print(car[["relation_type", "mean", "p", "nobs", "events", "related_firms", "event_weighted_mean", "event_weighted_p"]].to_string(index=False))
    if not regressions.empty:
        print(regressions[["sample", "outcome", "regressor", "coef", "p_event_cluster", "p_two_way", "nobs", "events"]].to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
