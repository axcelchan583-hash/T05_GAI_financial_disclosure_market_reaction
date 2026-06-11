#!/usr/bin/env python3
"""Build a larger DeepSeek/SiliconFlow batch for v3.1 announcement coding."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
DEFAULT_OUT_DIR = BASE / "results/v50_deepseek_v3_1_batch100_20260610"
V49_DIR = BASE / "results/v49_deepseek_v3_1_pilot_20260610"

sys.path.insert(0, str(BASE / "scripts"))
from build_v49_deepseek_v3_1_pilot_20260610 import (  # noqa: E402
    SYSTEM_PROMPT,
    build_case,
    build_web_prompt_lines,
    clean,
    read_rows,
)


def read_skip_ids(paths: list[Path]) -> set[str]:
    ids: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                value = clean(row.get("id") or row.get("pack_row_id"))
                if value:
                    ids.add(value)
    return ids


def evenly_spaced(rows: list[dict[str, str]], n: int) -> list[dict[str, str]]:
    if n <= 0 or not rows:
        return []
    if len(rows) <= n:
        return list(rows)
    if n == 1:
        return [rows[0]]
    step = (len(rows) - 1) / (n - 1)
    picked: list[dict[str, str]] = []
    seen: set[str] = set()
    for i in range(n):
        idx = round(i * step)
        row = rows[idx]
        row_id = clean(row.get("pack_row_id"))
        if row_id not in seen:
            picked.append(row)
            seen.add(row_id)
    if len(picked) < n:
        for row in rows:
            row_id = clean(row.get("pack_row_id"))
            if row_id not in seen:
                picked.append(row)
                seen.add(row_id)
                if len(picked) >= n:
                    break
    return picked[:n]


def select_a_rows(rows: list[dict[str, str]], n: int) -> list[dict[str, str]]:
    rows = sorted(rows, key=lambda r: (clean(r.get("announcement_date")), clean(r.get("pack_row_id"))))
    product = [
        r
        for r in rows
        if clean(r.get("primary_pom_like_category")) == "产品/平台/模型发布、上线、成果发布"
    ]
    picked = list(product[: min(len(product), 15, n)])
    picked_ids = {clean(r.get("pack_row_id")) for r in picked}
    remaining = [r for r in rows if clean(r.get("pack_row_id")) not in picked_ids]
    picked.extend(evenly_spaced(remaining, n - len(picked)))
    return picked[:n]


def select_batch(
    rows: list[dict[str, str]],
    skip_ids: set[str],
    quotas: dict[str, int],
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()
    for verdict, n in quotas.items():
        subset = [
            r
            for r in rows
            if clean(r.get("machine_pred_verdict")) == verdict
            and clean(r.get("pack_row_id")) not in skip_ids
            and clean(r.get("pack_row_id")) not in selected_ids
        ]
        subset = sorted(subset, key=lambda r: (clean(r.get("announcement_date")), clean(r.get("pack_row_id"))))
        picked = select_a_rows(subset, n) if verdict == "A" else evenly_spaced(subset, n)
        selected.extend(picked)
        selected_ids.update(clean(r.get("pack_row_id")) for r in picked)
    return selected


def write_manifest(out_dir: Path, cases: list[dict[str, object]]) -> None:
    fields = [
        "id",
        "date",
        "sec_code",
        "sec_name",
        "machine_pred",
        "framework_flags",
        "title",
        "category",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            writer.writerow({k: case.get(k, "") for k in fields})


def write_cases(out_dir: Path, cases: list[dict[str, object]], chunk_size: int) -> None:
    jsonl_path = out_dir / "deepseek_cases.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for case in cases:
            user_payload = {
                "instruction": "请按 T05 v3.1 规则预编码这一条公告，只输出严格 JSON。",
                "case": case,
            }
            f.write(json.dumps({"system": SYSTEM_PROMPT, "user": user_payload}, ensure_ascii=False) + "\n")

    (out_dir / "deepseek_web_prompt.md").write_text(
        "\n".join(build_web_prompt_lines(cases)),
        encoding="utf-8",
    )
    chunk_paths = []
    for i in range(0, len(cases), chunk_size):
        chunk = cases[i : i + chunk_size]
        path = out_dir / f"deepseek_web_prompt_chunk_{i // chunk_size + 1:02d}.md"
        path.write_text("\n".join(build_web_prompt_lines(chunk)), encoding="utf-8")
        chunk_paths.append(path)

    write_manifest(out_dir, cases)

    char_count = sum(len(json.dumps(c, ensure_ascii=False)) for c in cases) + len(SYSTEM_PROMPT)
    summary = [
        "# v50 DeepSeek v3.1 batch",
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
    parser.add_argument("--skip-manifest", type=Path, action="append", default=[V49_DIR / "manifest.csv"])
    parser.add_argument("--n-a", type=int, default=60)
    parser.add_argument("--n-dfw", type=int, default=20)
    parser.add_argument("--n-b", type=int, default=10)
    parser.add_argument("--n-d", type=int, default=10)
    parser.add_argument("--chunk-size", type=int, default=10)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    skip_ids = read_skip_ids(args.skip_manifest)
    quotas = {
        "A": args.n_a,
        "D-fw": args.n_dfw,
        "B": args.n_b,
        "D": args.n_d,
    }
    rows = read_rows()
    batch_rows = select_batch(rows, skip_ids, quotas)
    cases = [build_case(row) for row in batch_rows]
    write_cases(args.out_dir, cases, args.chunk_size)


if __name__ == "__main__":
    main()
