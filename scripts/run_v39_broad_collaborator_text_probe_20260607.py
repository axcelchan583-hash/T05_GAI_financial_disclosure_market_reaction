#!/usr/bin/env python3
"""Text-probe broad collaborators around v36 GenAI events.

This run extends v38 beyond supply-chain links. It extracts listed firms named
near cooperation/contract/investment language in event texts and in the
available pre-event CNINFO text corpus, then compares those broad cooperative
links against product-market competitors.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_v38_wide_collaborator_competitor_probe_20260607 as v38  # noqa: E402


RUN_ID = "v39_broad_collaborator_text_probe_20260607"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "103_v39_broad_collaborator_text_probe_20260607.md"

QIAN_ROOT = ROOT.parent / "T05-qian-supplier-replication-cn"
DIRECT_MANIFEST_PATH = (
    QIAN_ROOT
    / "results"
    / "v34_llm_loose_qian_validation_20260604"
    / "direct_event_414"
    / "direct_event_414_manifest.csv"
)

TEXT_DIRS = [
    QIAN_ROOT / "results" / "v34_llm_loose_qian_validation_20260604" / "direct_event_414" / "text",
    QIAN_ROOT / "data" / "raw" / "cninfo_priority_pdf_audit_20260603" / "text",
    QIAN_ROOT / "data" / "raw" / "cninfo_priority_pdf_audit_2023_2026_20260603" / "text",
    QIAN_ROOT / "data" / "raw" / "cninfo_formal_event_rebuild_20260602" / "text",
    ROOT / "data" / "raw" / "cninfo_genai_announcements_20260522" / "text",
]
ANNUAL_REPORT_NAME_DIR = ROOT / "data" / "raw" / "annual_reports_2025_txt" / "年报txt"

RELATION_KEYWORDS = [
    "合作",
    "战略合作",
    "联合",
    "共建",
    "共同",
    "签署",
    "协议",
    "框架协议",
    "合同",
    "中标",
    "供应",
    "采购",
    "客户",
    "伙伴",
    "生态",
    "合资",
    "投资",
    "增资",
    "收购",
    "受让",
    "设立",
    "授权",
    "服务",
    "联盟",
    "委托",
]

TITLE_RELATION_KEYWORDS = [
    "合作",
    "协议",
    "合同",
    "中标",
    "投资",
    "增资",
    "收购",
    "设立",
    "合资",
]

GENERIC_STOCK_ALIAS_STOPLIST = {
    "机器人",
    "数字人",
    "线上线下",
    "驱动力",
    "农产品",
    "太阳能",
    "新产业",
    "海量数据",
    "出版传媒",
    "信息发展",
    "先进数通",
    "普联软件",
}

INTERMEDIARY_CONTEXT_KEYWORDS = [
    "核查意见",
    "保荐",
    "财务顾问",
    "法律意见",
    "律师事务所",
    "证券股份有限公司关于",
    "承销",
    "战略配售",
    "首次公开发行股票",
    "发行人",
]


def code6(value: object) -> str:
    return v38.code6(value)


def clean_id(value: object) -> str:
    return v38.clean_id(value)


def clean_name(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = text.replace("_em_", "").replace("__em__", "").replace("em", "")
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("*", "").replace(" ", "").replace("　", "").replace("_", "")
    text = re.sub(r"\s+", "", text)
    text = text.strip("：:（）()[]【】")
    return text


def alias_variants(name: str) -> set[str]:
    name = clean_name(name)
    if not name:
        return set()
    variants = {name}
    no_st = re.sub(r"^(ST|S|N|XD|XR|DR)", "", name, flags=re.I)
    if no_st and no_st != name:
        variants.add(no_st)
    if name.endswith("A") and len(name) > 3:
        variants.add(name[:-1])
    return {v for v in variants if len(v) >= 3 and not v.isdigit()}


def add_name(records: list[dict], code: object, name: object, source: str) -> None:
    c = code6(code)
    n = clean_name(name)
    if not c or not n:
        return
    for alias in alias_variants(n):
        records.append({"stock_code": c, "stock_name": n, "alias": alias, "name_source": source})


def parse_cninfo_text_file(path: Path) -> dict | None:
    stem = path.stem
    parts = stem.split("_")
    if len(parts) < 4:
        return None
    if not re.match(r"\d{4}-\d{2}-\d{2}$", parts[0]):
        return None
    code = code6(parts[1])
    if not code:
        return None
    id_idx = None
    for i in range(2, len(parts)):
        if re.fullmatch(r"\d{8,12}", parts[i]):
            id_idx = i
            break
    if id_idx is None or id_idx <= 2:
        return None
    name = clean_name("".join(parts[2:id_idx]))
    ann_id = parts[id_idx]
    title = "_".join(parts[id_idx + 1 :])
    return {
        "path": path,
        "doc_date": pd.to_datetime(parts[0], errors="coerce"),
        "sec_code": code,
        "sec_name": name,
        "announcement_id": clean_id(ann_id),
        "announcement_title": title,
    }


def build_company_dictionary(events: pd.DataFrame, competitor: pd.DataFrame) -> pd.DataFrame:
    records: list[dict] = []
    for _, row in events.iterrows():
        add_name(records, row.get("focal_code"), row.get("focal_name"), "v36_event_focal")
    for _, row in competitor[["peer_code", "peer_name"]].drop_duplicates().iterrows():
        add_name(records, row.get("peer_code"), row.get("peer_name"), "v36_peer_panel")
    for _, row in competitor[["focal_code", "sec_name"]].drop_duplicates().iterrows():
        add_name(records, row.get("focal_code"), row.get("sec_name"), "v36_peer_panel_focal")

    if DIRECT_MANIFEST_PATH.exists():
        direct = pd.read_csv(DIRECT_MANIFEST_PATH, dtype=str, low_memory=False)
        for _, row in direct[["sec_code", "sec_name"]].drop_duplicates().iterrows():
            add_name(records, row.get("sec_code"), row.get("sec_name"), "direct_event_manifest")

    if ANNUAL_REPORT_NAME_DIR.exists():
        for path in ANNUAL_REPORT_NAME_DIR.glob("*.txt"):
            parts = path.stem.split("_")
            if len(parts) >= 2:
                add_name(records, parts[0], parts[1], "annual_report_filename")

    for text_dir in TEXT_DIRS:
        if not text_dir.exists():
            continue
        for path in text_dir.glob("*.txt"):
            meta = parse_cninfo_text_file(path)
            if meta:
                add_name(records, meta["sec_code"], meta["sec_name"], "cninfo_text_filename")

    dictionary = pd.DataFrame(records).drop_duplicates()
    if dictionary.empty:
        return dictionary
    dictionary["alias_len"] = dictionary["alias"].str.len()
    dictionary = dictionary.sort_values(["alias_len", "alias"], ascending=[False, True])
    dictionary = dictionary.drop_duplicates(["stock_code", "alias"], keep="first")
    dictionary = dictionary[
        ~dictionary["alias"].isin({"股份有限公司", "有限责任公司", "集团股份", "科技股份"})
        & ~dictionary["alias"].isin(GENERIC_STOCK_ALIAS_STOPLIST)
    ].copy()
    return dictionary.reset_index(drop=True)


def build_text_index() -> pd.DataFrame:
    rows = []
    for text_dir in TEXT_DIRS:
        if not text_dir.exists():
            continue
        for path in text_dir.glob("*.txt"):
            meta = parse_cninfo_text_file(path)
            if meta:
                rows.append(meta)
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows).drop_duplicates("path")
    out = out[out["doc_date"].notna()].copy()
    return out.reset_index(drop=True)


def load_direct_text_map() -> dict[str, str]:
    text_map: dict[str, str] = {}
    if DIRECT_MANIFEST_PATH.exists():
        manifest = pd.read_csv(DIRECT_MANIFEST_PATH, dtype=str, low_memory=False)
        for _, row in manifest.iterrows():
            event_id = clean_id(row.get("event_id") or row.get("announcement_id"))
            if not event_id:
                continue
            content = ""
            for col in ["announcement_content", "pdf_genai_context", "llm_evidence", "llm_reason"]:
                val = row.get(col)
                if isinstance(val, str) and val.strip():
                    content += "\n" + val
            text_map[event_id] = content
    for text_dir in TEXT_DIRS:
        if not text_dir.exists():
            continue
        for path in text_dir.glob("*.txt"):
            meta = parse_cninfo_text_file(path)
            if not meta:
                continue
            event_id = clean_id(meta["announcement_id"])
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            existing = text_map.get(event_id, "")
            if len(text) > len(existing):
                text_map[event_id] = text
    return text_map


def contains_relation_keyword(text: str) -> bool:
    return any(k in text for k in RELATION_KEYWORDS)


def is_intermediary_context(text: str) -> bool:
    return any(k in text for k in INTERMEDIARY_CONTEXT_KEYWORDS)


def extract_listed_partners_from_text(
    *,
    event: pd.Series,
    text: str,
    dictionary: pd.DataFrame,
    source: str,
    doc_date: pd.Timestamp | None = None,
    doc_id: str = "",
    doc_title: str = "",
    context_window: int = 90,
) -> list[dict]:
    if not isinstance(text, str) or not text.strip():
        return []
    focal_code = code6(event.get("focal_code"))
    title = str(event.get("announcement_title") or "")
    if doc_title:
        title = doc_title

    records = []
    best_by_code: dict[str, dict] = {}
    for _, cand in dictionary.iterrows():
        related_code = cand["stock_code"]
        if related_code == focal_code:
            continue
        if clean_name(cand["stock_name"]) == clean_name(event.get("focal_name")):
            continue
        alias = cand["alias"]
        pos = text.find(alias)
        if pos < 0 and alias not in title:
            continue

        title_hit = alias in title and any(k in title for k in TITLE_RELATION_KEYWORDS)
        contexts = []
        start_pos = pos
        while start_pos >= 0:
            left = max(0, start_pos - context_window)
            right = min(len(text), start_pos + len(alias) + context_window)
            context = text[left:right].replace("\n", " ")
            if contains_relation_keyword(context):
                contexts.append(context)
                break
            start_pos = text.find(alias, start_pos + len(alias))
        if not contexts and not title_hit:
            continue

        evidence = contexts[0] if contexts else title
        if is_intermediary_context(evidence):
            continue
        score = (3 if title_hit else 0) + (2 if "战略合作" in evidence or "合作协议" in evidence else 0) + 1
        row = {
            "sample_name": event.get("sample_name"),
            "event_id": clean_id(event.get("event_id")),
            "event_key": event.get("event_key"),
            "focal_code": focal_code,
            "focal_name": event.get("focal_name"),
            "event_date": event.get("event_date"),
            "event_year": event.get("event_year"),
            "announcement_title": event.get("announcement_title"),
            "auto_pdf_label": event.get("auto_pdf_label"),
            "candidate_row_type": event.get("candidate_row_type"),
            "related_code": related_code,
            "related_name": cand["stock_name"],
            "matched_alias": alias,
            "relation_type": source,
            "relation_group": "cooperative",
            "relation_year": pd.to_datetime(doc_date if doc_date is not None else event.get("event_date")).year,
            "source_doc_date": doc_date if doc_date is not None else event.get("event_date"),
            "source_doc_id": clean_id(doc_id),
            "source_doc_title": doc_title,
            "match_score": score,
            "match_evidence": evidence[:500],
        }
        prev = best_by_code.get(related_code)
        if prev is None or row["match_score"] > prev["match_score"]:
            best_by_code[related_code] = row
    records.extend(best_by_code.values())
    return records


def build_event_named_links(events: pd.DataFrame, dictionary: pd.DataFrame) -> pd.DataFrame:
    text_map = load_direct_text_map()
    rows = []
    for _, event in events.iterrows():
        event_id = clean_id(event.get("event_id"))
        text = "\n".join(
            [
                str(event.get("announcement_title") or ""),
                str(event.get("llm_reason") or ""),
                str(event.get("llm_evidence") or ""),
                text_map.get(event_id, ""),
            ]
        )
        rows.extend(
            extract_listed_partners_from_text(
                event=event,
                text=text,
                dictionary=dictionary,
                source="event_named_listed_partner",
                doc_date=event.get("event_date"),
                doc_id=event_id,
                doc_title=str(event.get("announcement_title") or ""),
            )
        )
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out = out.sort_values(["event_key", "related_code", "match_score"], ascending=[True, True, False])
    return out.drop_duplicates(["event_key", "related_code"], keep="first").reset_index(drop=True)


def build_historical_text_links(events: pd.DataFrame, dictionary: pd.DataFrame, text_index: pd.DataFrame) -> pd.DataFrame:
    if text_index.empty:
        return pd.DataFrame()
    rows = []
    text_index = text_index.sort_values("doc_date").copy()
    events_by_code = events.groupby("focal_code")
    for focal_code, group in events_by_code:
        docs = text_index[text_index["sec_code"].eq(focal_code)].copy()
        if docs.empty:
            continue
        for _, event in group.iterrows():
            event_date = pd.to_datetime(event.get("event_date"), errors="coerce")
            event_id = clean_id(event.get("event_id"))
            if pd.isna(event_date):
                continue
            prior_docs = docs[
                (docs["doc_date"] < event_date)
                & (docs["doc_date"] >= event_date - pd.DateOffset(years=5))
                & docs["announcement_id"].map(clean_id).ne(event_id)
            ].copy()
            if prior_docs.empty:
                continue
            # Keep relation-like historical documents; otherwise full scan is too noisy.
            prior_docs = prior_docs[
                prior_docs["announcement_title"].fillna("").map(lambda t: any(k in str(t) for k in TITLE_RELATION_KEYWORDS))
            ].copy()
            for _, doc in prior_docs.iterrows():
                try:
                    text = Path(doc["path"]).read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                rows.extend(
                    extract_listed_partners_from_text(
                        event=event,
                        text=text,
                        dictionary=dictionary,
                        source="historical_text_listed_partner",
                        doc_date=doc["doc_date"],
                        doc_id=doc["announcement_id"],
                        doc_title=doc["announcement_title"],
                    )
                )
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out = out.sort_values(
        ["event_key", "related_code", "source_doc_date", "match_score"],
        ascending=[True, True, False, False],
    )
    return out.drop_duplicates(["event_key", "related_code"], keep="first").reset_index(drop=True)


def union_broad_links(parts: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    nonempty = [p.copy() for p in parts if p is not None and not p.empty]
    if not nonempty:
        return pd.DataFrame(), pd.DataFrame()
    direction = pd.concat(nonempty, ignore_index=True)
    direction["related_code"] = direction["related_code"].map(code6)
    direction = direction[
        direction["related_code"].ne("")
        & direction["focal_code"].map(code6).ne(direction["related_code"])
    ].copy()
    direction = direction.sort_values(["event_key", "related_code", "match_score"], ascending=[True, True, False])
    direction = direction.drop_duplicates(["event_key", "related_code", "relation_type"], keep="first").copy()

    union = (
        direction.groupby(["sample_name", "event_id", "event_key", "focal_code", "related_code"], as_index=False)
        .agg(
            focal_name=("focal_name", "first"),
            event_date=("event_date", "first"),
            event_year=("event_year", "first"),
            announcement_title=("announcement_title", "first"),
            auto_pdf_label=("auto_pdf_label", "first"),
            candidate_row_type=("candidate_row_type", "first"),
            related_name=("related_name", "first"),
            matched_alias=("matched_alias", lambda s: ";".join(sorted(set(s.astype(str))))),
            relation_type=("relation_type", lambda s: "broad_collaborator_union"),
            source_types=("relation_type", lambda s: ";".join(sorted(set(s.astype(str))))),
            source_doc_date=("source_doc_date", "max"),
            source_doc_title=("source_doc_title", "first"),
            match_score=("match_score", "max"),
            match_evidence=("match_evidence", "first"),
        )
        .copy()
    )
    for source in ["event_named_listed_partner", "historical_text_listed_partner", "supply_chain_existing"]:
        union[f"is_{source}"] = union["source_types"].fillna("").str.contains(source).astype(int)
    return direction.reset_index(drop=True), union.reset_index(drop=True)


def convert_supply_chain_to_broad(union: pd.DataFrame) -> pd.DataFrame:
    if union.empty:
        return union.copy()
    out = union.copy()
    out["relation_type"] = "supply_chain_existing"
    out["related_name"] = ""
    out["matched_alias"] = ""
    out["source_doc_date"] = out["event_date"]
    out["source_doc_id"] = ""
    out["source_doc_title"] = out["announcement_title"]
    out["match_score"] = 1
    out["match_evidence"] = out.get("edge_sources", "")
    return out


def standardize_plus(df: pd.DataFrame, relation_group: str) -> pd.DataFrame:
    out = v38.standardize_relation_panel(df, relation_group)
    extra_cols = [
        "related_name",
        "matched_alias",
        "source_types",
        "match_score",
        "match_evidence",
        "is_event_named_listed_partner",
        "is_historical_text_listed_partner",
        "is_supply_chain_existing",
    ]
    for col in extra_cols:
        out[col] = df[col].values if col in df.columns and len(df) == len(out) else np.nan
    return out


def prepare_stacks(competitor: pd.DataFrame, broad_union: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    comp = standardize_plus(competitor, "competitor")
    coop = standardize_plus(broad_union, "cooperative")
    comp["cooperative"] = 0
    coop["cooperative"] = 1
    for col in ["is_event_named_listed_partner", "is_historical_text_listed_partner", "is_supply_chain_existing"]:
        comp[col] = 0
        coop[col] = pd.to_numeric(coop[col], errors="coerce").fillna(0).astype(int)

    coop_keys = set(zip(coop["event_key"], coop["related_code"]))
    comp = comp[
        ~pd.Series(list(zip(comp["event_key"], comp["related_code"])), index=comp.index).isin(coop_keys)
    ].copy()
    stack_union = pd.concat([comp, coop], ignore_index=True)
    stack_sources = stack_union.copy()
    return stack_union, stack_sources


def prepare_relation_type_stack(relation_panel: pd.DataFrame, relation_type: str) -> pd.DataFrame:
    comp = relation_panel[relation_panel["relation_type"].eq("competitor")].copy()
    coop = relation_panel[relation_panel["relation_type"].eq(relation_type)].copy()
    comp["cooperative"] = 0
    coop["cooperative"] = 1
    coop_keys = set(zip(coop["event_key"], coop["related_code"]))
    comp = comp[
        ~pd.Series(list(zip(comp["event_key"], comp["related_code"])), index=comp.index).isin(coop_keys)
    ].copy()
    return pd.concat([comp, coop], ignore_index=True)


def summarize_sources(direction: pd.DataFrame, union: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, df in [
        ("event_named_listed_partner_raw", direction[direction["relation_type"].eq("event_named_listed_partner")]),
        ("historical_text_listed_partner_raw", direction[direction["relation_type"].eq("historical_text_listed_partner")]),
        ("supply_chain_existing_raw", direction[direction["relation_type"].eq("supply_chain_existing")]),
        ("broad_collaborator_union_raw", union),
    ]:
        rows.append(
            {
                "layer": name,
                "linked_rows": len(df),
                "events": df["event_key"].nunique() if "event_key" in df.columns else 0,
                "focal_firms": df["focal_code"].nunique() if "focal_code" in df.columns else 0,
                "related_firms": df["related_code"].nunique() if "related_code" in df.columns else 0,
            }
        )
    return pd.DataFrame(rows)


def build_sample_flow(
    events: pd.DataFrame,
    competitor: pd.DataFrame,
    source_summary: pd.DataFrame,
    relation_panel: pd.DataFrame,
) -> pd.DataFrame:
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
            "clean_car0p1_rows": int(
                (
                    competitor["complete_clean_m1_p1"].eq(1)
                    & competitor["peer_car_0_p1_mm"].notna()
                ).sum()
            ),
            "clean_car0p1_events": competitor[
                competitor["complete_clean_m1_p1"].eq(1) & competitor["peer_car_0_p1_mm"].notna()
            ]["event_key"].nunique(),
        },
    ]
    for _, r in source_summary.iterrows():
        rt = r["layer"].replace("_raw", "")
        if rt == "broad_collaborator_union":
            mask = relation_panel["relation_type"].eq("broad_collaborator_union")
        else:
            mask = relation_panel["relation_type"].eq(rt)
        df = relation_panel[mask].copy()
        clean = df[df["complete_clean_m1_p1"].eq(1) & df["peer_car_0_p1_mm"].notna()]
        rows.append(
            {
                "layer": r["layer"].replace("_raw", "_returns"),
                "linked_rows": len(df),
                "events": df["event_key"].nunique(),
                "focal_firms": df["focal_code"].nunique(),
                "related_firms": df["related_code"].nunique(),
                "clean_car0p1_rows": len(clean),
                "clean_car0p1_events": clean["event_key"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def write_report(
    flow: pd.DataFrame,
    source_summary: pd.DataFrame,
    event_study: pd.DataFrame,
    regressions: pd.DataFrame,
    examples: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    car = event_study[event_study["window"].eq("CAR[0,+1]")].copy()
    lines = [
        "# v39 Broad Collaborator Text Probe",
        "",
        "Date: 2026-06-07",
        "",
        "## Scope",
        "",
        "This run expands v38 beyond supply-chain links. It uses machine text matching to extract listed broad collaborators from:",
        "",
        "- event announcement text around the v36 first-event sample;",
        "- available pre-event CNINFO texts in the local corpus;",
        "- existing supplier/customer links from CSMAR supply-chain tables.",
        "",
        "This is a screening run. Text-matched partner rows require manual validation before they can be used as final paper evidence.",
        "",
        "## Source Coverage",
        "",
        v38.md_table(source_summary),
        "",
        "## Sample Flow",
        "",
        v38.md_table(flow),
        "",
        "## CAR[0,+1] by Relation Type",
        "",
        v38.md_table(
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
        ),
        "",
        "## Stacked Event-FE Regressions",
        "",
        "Baseline group is product-market competitors. Competitor event-firm rows overlapping with broad collaborators are removed.",
        "",
        v38.md_table(
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
            else regressions
        ),
        "",
        "## Match Examples",
        "",
        v38.md_table(
            examples[
                [
                    "event_date",
                    "focal_code",
                    "focal_name",
                    "related_code",
                    "related_name",
                    "relation_type",
                    "matched_alias",
                    "announcement_title",
                    "match_evidence",
                ]
            ],
            max_rows=30,
        ),
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/company_dictionary.csv`",
        f"- `results/{RUN_ID}/broad_collaborator_links_raw.csv`",
        f"- `results/{RUN_ID}/relation_event_study.csv`",
        f"- `results/{RUN_ID}/stacked_regressions.csv`",
        f"- `results/{RUN_ID}/relation_panel.csv.gz`",
        f"- `results/{RUN_ID}/stack_union_panel.csv.gz`",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    events = v38.load_v36_first_events()
    competitor, placebo = v38.load_competitor_panel()
    dictionary = build_company_dictionary(events, competitor)
    text_index = build_text_index()
    print(f"dictionary aliases={len(dictionary):,}, stocks={dictionary['stock_code'].nunique():,}")
    print(f"text index={len(text_index):,}")

    event_named = build_event_named_links(events, dictionary)
    historical = build_historical_text_links(events, dictionary, text_index)
    _, supply_union = v38.build_cooperative_links(events)
    supply = convert_supply_chain_to_broad(supply_union)

    direction_raw, broad_union_raw = union_broad_links([event_named, historical, supply])
    source_summary = summarize_sources(direction_raw, broad_union_raw)
    print(source_summary.to_string(index=False))

    stock_model = v38.pe.load_stock_model()
    broad_union_returns = v38.attach_returns(broad_union_raw, stock_model)
    direction_returns = v38.attach_returns(direction_raw, stock_model)

    relation_panel = pd.concat(
        [
            standardize_plus(competitor, "competitor"),
            standardize_plus(placebo, "placebo"),
            standardize_plus(direction_returns, "cooperative"),
            standardize_plus(broad_union_returns, "cooperative"),
        ],
        ignore_index=True,
    )
    relation_panel.loc[relation_panel["relation_group"].eq("competitor"), "relation_type"] = "competitor"
    relation_panel.loc[relation_panel["relation_group"].eq("placebo"), "relation_type"] = "placebo_low_similarity"

    flow = build_sample_flow(events, competitor, source_summary, relation_panel)
    event_study = v38.relation_event_study(relation_panel)

    stack_union, stack_sources = prepare_stacks(competitor, broad_union_returns)
    regs = []
    for outcome, _ in v38.OUTCOMES:
        regs.append(v38.fit_event_fe(stack_union, outcome, ["cooperative"], "broad_union_vs_competitor"))
        regs.append(
            v38.fit_event_fe(
                stack_sources,
                outcome,
                [
                    "is_event_named_listed_partner",
                    "is_historical_text_listed_partner",
                    "is_supply_chain_existing",
                ],
                "source_flags_vs_competitor",
            )
        )
        for relation_type in [
            "event_named_listed_partner",
            "supply_chain_existing",
            "historical_text_listed_partner",
        ]:
            regs.append(
                v38.fit_event_fe(
                    prepare_relation_type_stack(relation_panel, relation_type),
                    outcome,
                    ["cooperative"],
                    f"{relation_type}_vs_competitor",
                )
            )
    regressions = pd.concat([r for r in regs if not r.empty], ignore_index=True) if regs else pd.DataFrame()

    examples = direction_raw.sort_values(["match_score", "event_date"], ascending=[False, True]).head(80).copy()

    dictionary.to_csv(OUT_DIR / "company_dictionary.csv", index=False, encoding="utf-8-sig")
    text_index.drop(columns=["path"], errors="ignore").to_csv(OUT_DIR / "text_index.csv", index=False, encoding="utf-8-sig")
    event_named.to_csv(OUT_DIR / "event_named_collaborator_matches.csv", index=False, encoding="utf-8-sig")
    historical.to_csv(OUT_DIR / "historical_text_collaborator_matches.csv", index=False, encoding="utf-8-sig")
    direction_raw.to_csv(OUT_DIR / "broad_collaborator_links_raw.csv", index=False, encoding="utf-8-sig")
    broad_union_raw.to_csv(OUT_DIR / "broad_collaborator_union_raw.csv", index=False, encoding="utf-8-sig")
    flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")
    source_summary.to_csv(OUT_DIR / "source_coverage.csv", index=False, encoding="utf-8-sig")
    event_study.to_csv(OUT_DIR / "relation_event_study.csv", index=False, encoding="utf-8-sig")
    regressions.to_csv(OUT_DIR / "stacked_regressions.csv", index=False, encoding="utf-8-sig")
    relation_panel.to_csv(OUT_DIR / "relation_panel.csv.gz", index=False)
    stack_union.to_csv(OUT_DIR / "stack_union_panel.csv.gz", index=False)
    stack_sources.to_csv(OUT_DIR / "stack_sources_panel.csv.gz", index=False)

    write_report(flow, source_summary, event_study, regressions, examples)
    car = event_study[event_study["window"].eq("CAR[0,+1]")]
    print(car[["relation_type", "mean", "p", "nobs", "events", "related_firms", "event_weighted_mean", "event_weighted_p"]].to_string(index=False))
    if not regressions.empty:
        print(regressions[["sample", "outcome", "regressor", "coef", "p_event_cluster", "p_two_way", "nobs", "events"]].to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
