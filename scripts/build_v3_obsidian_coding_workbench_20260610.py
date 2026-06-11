#!/usr/bin/env python3
"""Build the v3.1 Obsidian coding workbench for the T05 GenAI announcement audit."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote


SOURCE_CSV = Path(
    "/Users/mac/computerscience/第三方资料/04_项目专用资料/"
    "T05_GAI_financial_disclosure_market_reaction/"
    "cninfo_pom_like_active_announcements_20260609/tables/"
    "pom_like_active_announcements_review.csv"
)
OLD_WORKBENCH = Path(
    "/Users/mac/Documents/Obsidian Vault/23-5/"
    "T05_GenAI公告PDF人工审核_含分类字段_20260609.md"
)
OUT_DIR = Path("/Users/mac/Documents/Obsidian Vault/23-5")
LEGACY_V3_MD = OUT_DIR / "T05_GenAI公告PDF人工审核_v3_20260610.md"
OUT_MD = OUT_DIR / "T05_GenAI公告PDF人工审核_v3_1_20260610.md"
OUT_MACHINE = OUT_DIR / "T05_GenAI公告_v3_1_machine.csv"
OUT_CODING = OUT_DIR / "T05_GenAI公告_v3_1_coding.csv"


GROUP_LABELS = {
    "A1_direct_event_confirm": "A1 直接事件候选",
    "A2_backfill_date_recovery": "A2 需要回填事件日候选",
    "A3_old_pool_unresolved_confirm": "A3 旧1055未决复核",
    "Q1_reject_qc_sample_frame": "Q1 机器拒绝/边界样本抽查",
    "B1_low_priority_frame": "B1 低优先级抽查",
    "": "未进入 v53 优先队列的三类宽口径公告",
}

GROUP_ORDER = [
    "A1_direct_event_confirm",
    "A2_backfill_date_recovery",
    "A3_old_pool_unresolved_confirm",
    "Q1_reject_qc_sample_frame",
    "B1_low_priority_frame",
    "",
]


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def boolish(value: str) -> bool:
    return clean(value).lower() in {"true", "1", "yes", "是"}


def file_link(path: str) -> str:
    if not path:
        return ""
    return "file://" + quote(path)


def compact_snippet(text: str, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", clean(text))
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def read_text_sample(path: str, limit: int = 60000) -> str:
    p = Path(clean(path))
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def framework_flags(row: dict[str, str]) -> list[str]:
    text = " ".join(
        [
            clean(row.get("announcement_title")),
            clean(row.get("priority_evidence")),
            clean(row.get("metadata_snippet")),
            read_text_sample(clean(row.get("txt_local_path"))),
        ]
    )
    text = re.sub(r"\s+", "", text)
    flags: list[str] = []
    if re.search(r"框架性协议|框架协议|意向性(?:协议|文件|约定)|战略合作框架", text):
        flags.append("framework_or_intent")
    if re.search(r"不涉及具体(?:交易)?金额|暂不涉及具体(?:交易)?金额|无需提交(?:董事会|股东大会)|不需要提交(?:董事会|股东大会)", text):
        flags.append("no_amount_or_no_approval")
    if re.search(r"具体合作.*?(另行签|另行协商|另行确定|另行约定)|费用.*?(另行协商|另行确定|另行约定)|知识产权.*?(另行协商|另行确定|另行约定)", text):
        flags.append("future_contract_or_terms")
    if re.search(r"已(?:上线|发布|交付|签署具体|实现商业化)|具体合同|中标金额|合同金额|订单金额|实现收入", text):
        flags.append("implementation_override_signal")
    return flags


def read_source_rows() -> list[dict[str, str]]:
    with SOURCE_CSV.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_old_manual_fields() -> dict[str, dict[str, str]]:
    if not OLD_WORKBENCH.exists():
        return {}
    text = OLD_WORKBENCH.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^- \*\*(POM3_\d+)｜", text, flags=re.M))
    out: dict[str, dict[str, str]] = {}
    field_patterns = {
        "人工码": r"^[ \t]*- 人工码[：:][ \t]*(.*)$",
        "GenAI有效性": r"^[ \t]*- GenAI有效性[^：:]*[：:][ \t]*(.*)$",
        "POM方向": r"^[ \t]*- POM方向[^：:]*[：:][ \t]*(.*)$",
        "粗实施形态": r"^[ \t]*- 粗实施形态[^：:]*[：:][ \t]*(.*)$",
        "文件类型": r"^[ \t]*- 文件类型[^：:]*[：:][ \t]*(.*)$",
        "事件日可用": r"^[ \t]*- 事件日可用[^：:]*[：:][ \t]*(.*)$",
        "最终事件日": r"^[ \t]*- 最终事件日[：:][ \t]*(.*)$",
        "是否首次": r"^[ \t]*- 是否首次[：:][ \t]*(.*)$",
        "证据短句": r"^[ \t]*- 证据短句[：:][ \t]*(.*)$",
        "备注": r"^[ \t]*- 备注[：:][ \t]*(.*)$",
    }
    for i, match in enumerate(matches):
        row_id = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        fields: dict[str, str] = {}
        for field, pattern in field_patterns.items():
            m = re.search(pattern, block, flags=re.M)
            fields[field] = clean(m.group(1)) if m else ""
        out[row_id] = fields
    return out


def parse_existing_v3_manual_codes() -> dict[str, str]:
    source = OUT_MD if OUT_MD.exists() else LEGACY_V3_MD
    if not source.exists():
        return {}
    text = source.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^### (POM3_\d+) ｜", text, flags=re.M))
    out: dict[str, str] = {}
    for i, match in enumerate(matches):
        row_id = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        m = re.search(r"^[ \t]*人工码:[ \t]*(.*)$", block, flags=re.M)
        if m:
            out[row_id] = clean(m.group(1))
    return out


def is_no(value: str) -> bool:
    return clean(value).lower() in {"no", "否", "0", "false", "n"}


def is_yes(value: str) -> bool:
    return clean(value).lower() in {"yes", "是", "1", "true", "y"}


def convert_old_manual_to_v3(fields: dict[str, str]) -> tuple[str, str]:
    raw = clean(fields.get("人工码"))
    if raw:
        return raw, "旧人工码原样保留"

    validity = clean(fields.get("GenAI有效性")).lower()
    source_type = clean(fields.get("文件类型")).lower()
    usable = clean(fields.get("事件日可用")).lower()
    first = clean(fields.get("是否首次")).lower()
    evidence = clean(fields.get("证据短句"))
    note = clean(fields.get("备注"))
    pom = clean(fields.get("POM方向")).lower()
    mode = clean(fields.get("粗实施形态")).lower()

    if validity in {"no", "否"}:
        return "D", "旧字段 GenAI有效性=no"
    if source_type == "not_event":
        return "D", "旧字段 文件类型=not_event"
    if validity in {"uncertain", "不确定"}:
        suffix = f" | 备注={note}" if note else ""
        return "U" + suffix, "旧字段 GenAI有效性=uncertain"
    if source_type == "backfill_needed":
        clue = note or evidence
        suffix = f" | 线索={clue}" if clue else ""
        return "B" + suffix, "旧字段 文件类型=backfill_needed"
    if source_type == "duplicate_progress" or is_no(first):
        return "C", "旧字段 是否首次=否或duplicate_progress"
    if source_type == "direct_event" and is_yes(usable) and is_yes(first):
        parts = ["A"]
        if pom in {"product", "both"}:
            parts.append("OUT=1")
        elif pom in {"process", "unclear"}:
            parts.append("OUT=0")
        if mode:
            if mode in {"own_launch_or_deploy", "internal_process"}:
                parts.append("M=own")
            elif mode in {"relational_access", "resource_commitment"}:
                parts.append("M=ext")
        if evidence:
            parts.append(f"证={evidence}")
        return " | ".join(parts), "旧字段 direct_event 可用且首次"
    return "", ""


def category_suggestion(row: dict[str, str]) -> tuple[str, str, str]:
    category = clean(row.get("primary_pom_like_category"))
    title = clean(row.get("announcement_title"))
    evidence = clean(row.get("priority_evidence")) or clean(row.get("metadata_snippet"))
    text = title + " " + evidence

    if "产品/平台/模型发布" in category:
        return "1", "own", "产品/模型/平台发布类，通常为对外产品或商业化能力"
    if "签署战略合作" in category:
        return "?", "ext", "合作协议类，M=ext；OUT需人工看合作内容"
    if "投资/建设/增资/收购/智算中心/大模型项目" in category:
        if re.search(r"智算|算力|GPU|训练|推理|数据中心|算力中心|算力服务", text):
            return "0", "ext", "算力/智算资源承诺类，通常非直接对外产品"
        return "?", "ext", "投资/建设/收购类，M=ext；OUT需人工看项目用途"
    return "?", "?", "类别不足，需人工判断"


def machine_predict(row: dict[str, str], manual_prefill: str = "") -> dict[str, str]:
    group = clean(row.get("manual_priority_group"))
    candidate = clean(row.get("candidate_tier"))
    v34 = clean(row.get("v34_llm_category"))
    v52 = clean(row.get("v52_llm_label"))
    category = clean(row.get("primary_pom_like_category"))
    labels = " ".join([group, candidate, v34, v52]).lower()
    fw_flags = framework_flags(row)
    fw_gate = len([f for f in fw_flags if f != "implementation_override_signal"]) >= 2
    fw_override = "implementation_override_signal" in fw_flags
    has_genai_signal = boolish(row.get("has_strict_genai_context", "")) or "keep_direct_event" in labels

    verdict = "U"
    reason = "信息不足，人工判定"

    manual_lower = manual_prefill.lower()
    if manual_lower.startswith("d-fw") or (manual_lower.startswith("d") and re.search(r"框架|意向|fw", manual_prefill, flags=re.I)):
        verdict, reason = "D-fw", "现有人工码为框架协议placebo"
    elif manual_lower.startswith("c"):
        verdict, reason = "C", "旧人工字段显示非首次或重复"
    elif manual_lower.startswith("d"):
        verdict, reason = "D", "旧人工字段显示剔除"
    elif manual_lower.startswith("b"):
        verdict, reason = "B", "旧人工字段显示需回填"
    elif manual_lower.startswith("a"):
        verdict, reason = "A", "旧人工字段显示主样本候选"
    elif group == "A2_backfill_date_recovery" or "keep_backfill" in labels or "backfill_needed" in labels:
        verdict, reason = "B", "机器队列=A2或LLM标记keep_backfill_needed"
    elif fw_gate and has_genai_signal and not fw_override:
        verdict, reason = "D-fw", f"框架协议亮线命中{len(fw_flags)}项且无落地override"
    elif "reject_" in labels or "exclude_no_strict_genai_after_snippet" in labels:
        verdict, reason = "D", "机器队列显示无严格GenAI/泛AI/非公司行动等拒绝信号"
    elif boolish(row.get("denial_or_correction_flag", "")) or boolish(row.get("weak_attention_flag", "")):
        verdict, reason = "D", "机器标记为否认/弱关注"
    elif group == "A1_direct_event_confirm" or "keep_direct_event" in labels:
        verdict, reason = "A", "机器队列=A1或LLM标记keep_direct_event"
    elif group == "A3_old_pool_unresolved_confirm":
        verdict, reason = "U", "旧1055未决样本"
    elif group in {"Q1_reject_qc_sample_frame", "B1_low_priority_frame"}:
        verdict, reason = "D", "机器拒绝/低优先级抽查框"
    elif not boolish(row.get("has_strict_genai_context", "")):
        verdict, reason = "D", "无严格GenAI上下文"

    out, mode, suggestion_reason = "", "", ""
    if verdict == "A":
        out, mode, suggestion_reason = category_suggestion(row)

    return {
        "machine_pred_verdict": verdict,
        "machine_pred_reason": reason,
        "suggested_out": out,
        "suggested_mode": mode,
        "suggestion_reason": suggestion_reason,
        "framework_flags": ";".join(fw_flags),
        "machine_pred_text": format_machine_pred(verdict, reason, out, mode, suggestion_reason),
    }


def format_machine_pred(verdict: str, reason: str, out: str, mode: str, suggestion_reason: str) -> str:
    extras = []
    if out:
        extras.append(f"OUT={out}")
    if mode:
        extras.append(f"M={mode}")
    if extras:
        return f"{verdict}（{reason}；建议 {', '.join(extras)}）"
    return f"{verdict}（{reason}）"


def parse_v3_manual_code(raw: str, date: str) -> dict[str, str]:
    raw = clean(raw)
    result = {
        "verdict": "",
        "out": "",
        "mode": "",
        "realized": "",
        "event_date": "",
        "evidence": "",
        "note": "",
        "line_clue": "",
        "genai_validity": "",
        "source_event_type": "",
        "event_date_usable": "",
        "first_event": "",
    }
    if not raw:
        return result

    raw_for_split = raw.replace("｜", "|")
    parts = [clean(p) for p in raw_for_split.split("|")]
    verdict_token = clean(parts[0])
    verdict_upper = verdict_token.upper().replace("_", "-")
    if verdict_upper in {"D-FW", "DFW"} or (verdict_upper.startswith("D") and re.search(r"框架|意向|FW", raw, flags=re.I)):
        result["verdict"] = "D-fw"
    elif verdict_upper and verdict_upper[0] in {"A", "B", "C", "D", "U"}:
        result["verdict"] = verdict_upper[0]
    else:
        result["verdict"] = verdict_token
    if result["verdict"] == "A":
        result["event_date"] = date
    elif result["verdict"] == "D-fw":
        result["event_date"] = date

    for part in parts[1:]:
        part_upper = part.upper()
        if part_upper in {"R+", "R=+"} or part in {"r+"}:
            result["realized"] = "+"
            continue
        if part_upper in {"R-", "R=-"} or part in {"r-"}:
            result["realized"] = "-"
            continue
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = clean(key).upper()
        value = clean(value)
        if key in {"OUT", "CT"}:
            result["out"] = value
        elif key in {"M", "MODE"}:
            result["mode"] = value
        elif key in {"R", "REALIZED"}:
            result["realized"] = value.replace("r", "").replace("R", "")
        elif key in {"证", "EVIDENCE"}:
            result["evidence"] = value
        elif key in {"备注", "NOTE"}:
            result["note"] = value
        elif key in {"线索", "CLUE"}:
            result["line_clue"] = value
            result["note"] = value
        elif key in {"日", "DATE", "EVENT_DATE"}:
            result["event_date"] = value

    if result["verdict"] == "B":
        result["event_date"] = ""
    derive_v3_fields(result)
    return result


def derive_v3_fields(result: dict[str, str]) -> None:
    verdict = result.get("verdict", "")
    if verdict == "A":
        result["genai_validity"] = "yes"
        result["source_event_type"] = "direct_event"
        result["event_date_usable"] = "yes"
        result["first_event"] = "yes"
    elif verdict == "B":
        result["genai_validity"] = "yes"
        result["source_event_type"] = "backfill_needed"
        result["event_date_usable"] = "no"
        result["first_event"] = "unknown"
    elif verdict == "C":
        result["genai_validity"] = "yes_or_machine_inherit"
        result["source_event_type"] = "duplicate_or_non_first"
        result["event_date_usable"] = "no"
        result["first_event"] = "no"
    elif verdict == "D-fw":
        result["genai_validity"] = "no_commitment"
        result["source_event_type"] = "framework_placebo"
        result["event_date_usable"] = "yes"
        result["first_event"] = "no"
    elif verdict == "D":
        result["genai_validity"] = "no"
        result["source_event_type"] = "not_event"
        result["event_date_usable"] = "no"
        result["first_event"] = "no"
    elif verdict == "U":
        result["genai_validity"] = "uncertain"
        result["source_event_type"] = "uncertain"
        result["event_date_usable"] = "uncertain"
        result["first_event"] = "unknown"


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_outputs() -> None:
    rows = read_source_rows()
    old_manual = parse_old_manual_fields()
    existing_v3_codes = parse_existing_v3_manual_codes()

    enriched: list[dict[str, str]] = []
    machine_rows: list[dict[str, str]] = []
    coding_rows: list[dict[str, str]] = []

    for row in rows:
        rid = clean(row["pack_row_id"])
        fields = old_manual.get(rid, {})
        existing_v3_code = clean(existing_v3_codes.get(rid, ""))
        if existing_v3_code:
            manual_prefill, prefill_reason = existing_v3_code, "现有v3人工码保留"
        else:
            manual_prefill, prefill_reason = convert_old_manual_to_v3(fields)
        pred = machine_predict(row, manual_prefill)
        parsed = parse_v3_manual_code(manual_prefill, clean(row.get("announcement_date")))

        enriched_row = dict(row)
        enriched_row.update(pred)
        enriched_row["manual_code_prefill"] = manual_prefill
        enriched_row["manual_code_prefill_reason"] = prefill_reason
        enriched_row["old_manual_genai_validity"] = fields.get("GenAI有效性", "")
        enriched_row["old_manual_first"] = fields.get("是否首次", "")
        enriched.append(enriched_row)

        machine_rows.append(enriched_row)
        coding_rows.append(
            {
                "id": rid,
                "date": clean(row.get("announcement_date")),
                "sec_code": clean(row.get("sec_code")),
                "sec_name": clean(row.get("sec_name")),
                "verdict": parsed["verdict"],
                "genai_validity": parsed["genai_validity"],
                "source_event_type": parsed["source_event_type"],
                "event_date_usable": parsed["event_date_usable"],
                "first_event": parsed["first_event"],
                "out": parsed["out"],
                "mode": parsed["mode"],
                "realized": parsed["realized"],
                "event_date": parsed["event_date"],
                "evidence": parsed["evidence"],
                "note": parsed["note"],
                "line_clue": parsed["line_clue"],
                "pre_fw": "",
                "raw_manual_code": manual_prefill,
                "machine_pred_verdict": pred["machine_pred_verdict"],
                "machine_pred_reason": pred["machine_pred_reason"],
                "suggested_out": pred["suggested_out"],
                "suggested_mode": pred["suggested_mode"],
            }
        )

    add_pre_fw_flags(coding_rows)
    write_machine_csv(machine_rows)
    write_coding_csv(coding_rows)
    write_markdown(enriched, coding_rows)


def add_pre_fw_flags(rows: list[dict[str, str]]) -> None:
    fw_dates_by_firm: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        if row.get("verdict") == "D-fw" and row.get("event_date"):
            fw_dates_by_firm[row.get("sec_code", "")].append(row["event_date"])
    for dates in fw_dates_by_firm.values():
        dates.sort()
    for row in rows:
        if row.get("verdict") != "A" or not row.get("event_date"):
            row["pre_fw"] = ""
            continue
        prior = [d for d in fw_dates_by_firm.get(row.get("sec_code", ""), []) if d < row["event_date"]]
        row["pre_fw"] = "1" if prior else "0"


def write_machine_csv(rows: list[dict[str, str]]) -> None:
    source_fields = list(rows[0].keys()) if rows else []
    priority = [
        "pack_row_id",
        "announcement_date",
        "sec_code",
        "sec_name",
        "announcement_title",
        "primary_pom_like_category",
        "matched_genai_terms",
        "priority_evidence",
        "metadata_snippet",
        "manual_priority_group",
        "candidate_tier",
        "v34_llm_category",
        "v52_llm_label",
        "machine_pred_verdict",
        "machine_pred_reason",
        "suggested_out",
        "suggested_mode",
        "suggestion_reason",
        "framework_flags",
        "manual_code_prefill",
        "manual_code_prefill_reason",
    ]
    fields = priority + [f for f in source_fields if f not in priority]
    write_csv(OUT_MACHINE, rows, fields)


def write_coding_csv(rows: list[dict[str, str]]) -> None:
    fields = [
        "id",
        "date",
        "sec_code",
        "sec_name",
        "verdict",
        "genai_validity",
        "source_event_type",
        "event_date_usable",
        "first_event",
        "out",
        "mode",
        "realized",
        "event_date",
        "evidence",
        "note",
        "line_clue",
        "pre_fw",
        "raw_manual_code",
        "machine_pred_verdict",
        "machine_pred_reason",
        "suggested_out",
        "suggested_mode",
    ]
    write_csv(OUT_CODING, rows, fields)


def section_key(row: dict[str, str]) -> str:
    return clean(row.get("manual_priority_group"))


def write_markdown(rows: list[dict[str, str]], coding_rows: list[dict[str, str]]) -> None:
    pred_counts = Counter(clean(r.get("machine_pred_verdict")) for r in rows)
    manual_counts = Counter(clean(r.get("verdict")) or "未填" for r in coding_rows)
    group_counts = Counter(section_key(r) for r in rows)
    incomplete_a = sum(
        1
        for r in coding_rows
        if clean(r.get("verdict")) == "A"
        and (not clean(r.get("out")) or not clean(r.get("mode")) or not clean(r.get("evidence")))
    )

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[section_key(row)].append(row)

    lines: list[str] = []
    lines.extend(
        [
            "---",
            "project: T05",
            "purpose: CNINFO GenAI announcement v3.1 compact human coding workbench",
            "created: 2026-06-10",
            "design_version: v3.1",
            f"source_csv: \"{SOURCE_CSV}\"",
            f"machine_csv: \"{OUT_MACHINE}\"",
            f"coding_csv: \"{OUT_CODING}\"",
            f"total_rows: {len(rows)}",
            "---",
            "",
            "# T05 GenAI 公告 PDF 人工审核工作台 v3.1（20260610）",
            "",
            "这个版本只让人工填一行 `人工码:`。机器预判只是建议，人工可以确认或改判。",
            "",
            "## 快速语法",
            "",
            "```text",
            "人工码: A | OUT=1 | M=own | 证=公司发布大模型并同步发布商业应用成果 | R=+",
            "人工码: A | OUT=0 | M=ext | 证=智算中心为AIGC大模型训练推理提供算力支撑 | R=-",
            "人工码: B | 线索=年报追溯，查2023年3月新闻",
            "人工码: C",
            "人工码: D-fw",
            "人工码: D",
            "人工码: U | 备注=有大模型词但行动方疑似参股公司而非受控子公司",
            "```",
            "",
            "判定码：",
            "",
            "- `A`：进主样本，公告日本身是首次有效 GenAI 事件日。",
            "- `B`：真 GenAI 事件，但当前公告日不能用，需要回填更早首次日期。",
            "- `C`：真 GenAI 相关，但不是该公司首次事件，或只是重复/进展披露。",
            "- `D-fw`：GenAI 话题/框架协议/无实质承诺，保留公告日进入 placebo 池，不进主样本。",
            "- `D`：剔除，非有效 GenAI 行动。",
            "- `U`：待定，需要二次核验。",
            "",
            "A 类才需要填：",
            "",
            "- `OUT=1/0`：GenAI 相关产出是否面向外部客户收费或对外服务。不是“有没有竞争威胁”。`CT=1/0` 可写，解析时会并入 `OUT`。",
            "- `M=own/ext`：`own` 是自己发布/上线/备案/部署；`ext` 是合作、投资、收购、算力承诺等借外力。",
            "- `证=`：一句最关键原文。",
            "- `R=+/-`：可选，`+` 为已发布/上线/商业化，`-` 为计划/意向/框架。",
            "",
            "## 合作/框架协议规则",
            "",
            "合作类永远站在公告方判断：合作方有技术不够，必须看到公告方自己的 GenAI 动作或交付物。",
            "",
            "框架协议三标志中命中两项及以上，通常判 `D-fw`：",
            "",
            "1. 自称框架性协议、框架协议或意向性文件；",
            "2. 不涉及具体金额、无需董事会或股东大会审议；",
            "3. 具体合作、费用或知识产权另行签约、另行协商或另行确定。",
            "",
            "若同一公告已经披露上线、交付、具体合同、明确金额订单或商业化收入，可以 override 为 `A`。",
            "",
            "## 投资/增资规则",
            "",
            "投资类只问两个 gate：",
            "",
            "1. 承诺是否真实：正式协议、真金白银、支付安排；业绩对赌/补偿是强信号。",
            "2. 标的是否明确 GenAI：大模型训练/推理、AIGC 服务、或服务具体大模型公司。",
            "",
            "两者都成立且为首次，判 `A | M=ext`。参股比例低、不并表、焦点公司主业非 AI 不直接否决。",
            "",
            "## 进度面板",
            "",
            f"- 总条目：{len(rows)}",
            f"- 已有人工作业码：{len([r for r in coding_rows if clean(r.get('verdict'))])}",
            f"- 待人工填写：{len([r for r in coding_rows if not clean(r.get('verdict'))])}",
            f"- A 类已填但缺 `OUT/M/证`：{incomplete_a}",
            "",
            "机器预判分布：",
            "",
        ]
    )
    for verdict in ["A", "B", "C", "D-fw", "D", "U"]:
        lines.append(f"- `{verdict}`：{pred_counts.get(verdict, 0)}")
    lines.extend(["", "人工码分布：", ""])
    for verdict in ["A", "B", "C", "D-fw", "D", "U", "未填"]:
        lines.append(f"- `{verdict}`：{manual_counts.get(verdict, 0)}")

    lines.extend(["", "审核分组：", ""])
    for key in GROUP_ORDER:
        lines.append(f"- {GROUP_LABELS[key]}：{group_counts.get(key, 0)}")

    lines.extend(["", "## 条目", ""])
    for key in GROUP_ORDER:
        section_rows = grouped.get(key, [])
        if not section_rows:
            continue
        lines.extend(["", f"## {GROUP_LABELS[key]}（{len(section_rows)}）", ""])
        for row in section_rows:
            lines.extend(format_entry(row))

    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def format_entry(row: dict[str, str]) -> list[str]:
    rid = clean(row.get("pack_row_id"))
    date = clean(row.get("announcement_date"))
    sec_code = clean(row.get("sec_code"))
    sec_name = clean(row.get("sec_name"))
    category = clean(row.get("primary_pom_like_category"))
    matched_terms = clean(row.get("matched_genai_terms")) or clean(row.get("query_terms"))
    title = clean(row.get("announcement_title"))
    evidence = clean(row.get("priority_evidence")) or clean(row.get("metadata_snippet"))
    evidence = compact_snippet(evidence)
    pred = clean(row.get("machine_pred_text"))
    prefill = clean(row.get("manual_code_prefill"))
    link = file_link(clean(row.get("pdf_local_path")))
    pdf_line = f"[打开PDF]({link})" if link else "PDF缺失"
    terms_text = matched_terms if matched_terms else "无"

    return [
        f"### {rid} ｜ {date} ｜ {sec_code} {sec_name}",
        "",
        f"{pdf_line} ｜ {category} ｜ 命中: {terms_text}",
        f"**标题**: {title}",
        f"**证据提示**: {evidence}",
        f"**机器预判**: {pred}",
        "",
        f"人工码: {prefill}",
        "",
    ]


if __name__ == "__main__":
    build_outputs()
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_MACHINE}")
    print(f"Wrote {OUT_CODING}")
