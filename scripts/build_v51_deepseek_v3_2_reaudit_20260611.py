#!/usr/bin/env python3
"""Build a v3.2 DeepSeek re-audit batch for the previously reviewed 118 cases."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
DEFAULT_OUT_DIR = BASE / "results/v51_deepseek_v3_2_reaudit118_20260611"
PROMPT_MD = BASE / "docs/prompts/56_genai_announcement_llm_precoding_prompt_v3_2_20260611.md"
V49_DIR = BASE / "results/v49_deepseek_v3_1_pilot_20260610"
V50_DIR = BASE / "results/v50_deepseek_v3_1_batch100_20260610"

sys.path.insert(0, str(BASE / "scripts"))
from build_v49_deepseek_v3_1_pilot_20260610 import build_case, clean, read_rows  # noqa: E402


def extract_system_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    marker = "## SYSTEM PROMPT"
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Cannot find SYSTEM PROMPT marker in {path}")
    match = re.search(r"```text\n(.*?)\n```", text[start:], flags=re.S)
    if not match:
        raise RuntimeError(f"Cannot find fenced text prompt in {path}")
    return match.group(1).strip()


def build_web_prompt_lines(system_prompt: str, cases: list[dict[str, object]]) -> list[str]:
    lines = [
        "# DeepSeek v3.2 re-audit prompt",
        "",
        "## System / rules",
        "",
        system_prompt,
        "",
        "## Cases",
        "",
        "请对下面每个 case 分别输出一行严格 JSON。",
        "",
        "```jsonl",
    ]
    for case in cases:
        lines.append(json.dumps(llm_case(case), ensure_ascii=False))
    lines.extend(["```", ""])
    return lines


def llm_case(case: dict[str, object]) -> dict[str, object]:
    """Remove previous-run labels from the model-facing payload."""
    blocked = {"source"}
    return {
        key: value
        for key, value in case.items()
        if key not in blocked and not key.startswith("old_v31_")
    }


def read_previous_run(source: str, base_dir: Path) -> list[dict[str, str]]:
    manifest_path = base_dir / "manifest.csv"
    parsed_path = base_dir / "siliconflow_parsed_outputs.csv"
    with manifest_path.open(newline="", encoding="utf-8-sig") as f:
        manifest = {r["id"]: r for r in csv.DictReader(f)}
    with parsed_path.open(newline="", encoding="utf-8-sig") as f:
        parsed = {r["id"]: r for r in csv.DictReader(f)}

    rows: list[dict[str, str]] = []
    for case_id, m in manifest.items():
        p = parsed.get(case_id, {})
        rows.append(
            {
                "source": source,
                "id": case_id,
                "old_machine_pred": clean(m.get("machine_pred")),
                "old_v31_verdict": clean(p.get("model_verdict")),
                "old_v31_out": clean(p.get("out")),
                "old_v31_mode": clean(p.get("mode")),
                "old_v31_realized": clean(p.get("realized")),
                "old_v31_reason": clean(p.get("reason")),
            }
        )
    return rows


def previous_cases() -> list[dict[str, str]]:
    rows = []
    rows.extend(read_previous_run("v49_pilot18", V49_DIR))
    rows.extend(read_previous_run("v50_batch100", V50_DIR))
    return rows


def select_previous(rows: list[dict[str, str]], mode: str) -> list[dict[str, str]]:
    if mode == "all118":
        return rows
    if mode == "conflicts":
        return [r for r in rows if r["old_machine_pred"] and r["old_machine_pred"] != r["old_v31_verdict"]]
    if mode == "compute_boundary":
        terms = ("算力", "服务器", "智算", "数据中心", "芯片", "GPU", "compute")
        selected = []
        machine_rows = {clean(r.get("pack_row_id")): r for r in read_rows()}
        for row in rows:
            m = machine_rows.get(row["id"], {})
            haystack = " ".join(
                [
                    clean(m.get("announcement_title")),
                    clean(m.get("primary_pom_like_category")),
                    clean(m.get("priority_evidence")),
                    clean(m.get("metadata_snippet")),
                    clean(row.get("old_v31_reason")),
                ]
            )
            if any(term.lower() in haystack.lower() for term in terms):
                selected.append(row)
        return selected
    raise ValueError(f"Unknown mode: {mode}")


def write_manifest(out_dir: Path, cases: list[dict[str, object]]) -> None:
    fields = [
        "id",
        "date",
        "sec_code",
        "sec_name",
        "machine_pred",
        "old_v31_verdict",
        "old_v31_out",
        "old_v31_mode",
        "old_v31_realized",
        "source",
        "framework_flags",
        "title",
        "category",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            writer.writerow({k: case.get(k, "") for k in fields})


def write_cases(out_dir: Path, cases: list[dict[str, object]], system_prompt: str, chunk_size: int) -> None:
    jsonl_path = out_dir / "deepseek_cases.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for case in cases:
            user_payload = {
                "instruction": "请按 T05 v3.2 规则预编码这一条公告，只输出严格 JSON。",
                "case": llm_case(case),
            }
            f.write(json.dumps({"system": system_prompt, "user": user_payload}, ensure_ascii=False) + "\n")

    (out_dir / "deepseek_web_prompt.md").write_text(
        "\n".join(build_web_prompt_lines(system_prompt, cases)),
        encoding="utf-8",
    )
    chunk_paths = []
    for i in range(0, len(cases), chunk_size):
        chunk = cases[i : i + chunk_size]
        path = out_dir / f"deepseek_web_prompt_chunk_{i // chunk_size + 1:02d}.md"
        path.write_text("\n".join(build_web_prompt_lines(system_prompt, chunk)), encoding="utf-8")
        chunk_paths.append(path)

    write_manifest(out_dir, cases)

    char_count = sum(len(json.dumps(c, ensure_ascii=False)) for c in cases) + len(system_prompt)
    summary = [
        "# v51 DeepSeek v3.2 re-audit",
        "",
        f"cases: {len(cases)}",
        f"approx_chars: {char_count}",
        f"rough_input_tokens: {round(char_count * 0.9)} - {round(char_count * 1.2)}",
        "",
        "files:",
        f"- {jsonl_path}",
        f"- {out_dir / 'deepseek_web_prompt.md'}",
    ]
    summary.extend(f"- {p}" for p in chunk_paths)
    summary.extend(
        [
            f"- {out_dir / 'manifest.csv'}",
            "",
            "note: no API call is made by this script.",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--mode", choices=["all118", "conflicts", "compute_boundary"], default="all118")
    parser.add_argument("--chunk-size", type=int, default=10)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    system_prompt = extract_system_prompt(PROMPT_MD)
    previous = select_previous(previous_cases(), args.mode)
    machine_rows = {clean(r.get("pack_row_id")): r for r in read_rows()}

    cases: list[dict[str, object]] = []
    for prev in previous:
        row = machine_rows.get(prev["id"])
        if not row:
            continue
        case = build_case(row)
        case["source"] = prev["source"]
        case["old_v31_verdict"] = prev["old_v31_verdict"]
        case["old_v31_out"] = prev["old_v31_out"]
        case["old_v31_mode"] = prev["old_v31_mode"]
        case["old_v31_realized"] = prev["old_v31_realized"]
        cases.append(case)

    write_cases(args.out_dir, cases, system_prompt, args.chunk_size)


if __name__ == "__main__":
    main()
