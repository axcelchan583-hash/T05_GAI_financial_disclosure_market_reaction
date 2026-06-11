#!/usr/bin/env python3
"""Run the v49 DeepSeek v3.1 pilot batch through SiliconFlow chat completions."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
PILOT_DIR = BASE / "results/v49_deepseek_v3_1_pilot_20260610"
INPUT_JSONL = PILOT_DIR / "deepseek_pilot_cases.jsonl"
OUT_RAW_JSONL = PILOT_DIR / "siliconflow_raw_outputs.jsonl"
OUT_PARSED_CSV = PILOT_DIR / "siliconflow_parsed_outputs.csv"
OUT_SUMMARY = PILOT_DIR / "siliconflow_run_summary.md"


DEFAULT_MODEL = "Pro/deepseek-ai/DeepSeek-V3.2"


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_cases(limit: int | None = None) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    with INPUT_JSONL.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cases.append(json.loads(line))
            if limit is not None and len(cases) >= limit:
                break
    return cases


def call_siliconflow(case: dict[str, object], model: str, timeout: int = 120) -> dict[str, object]:
    base_url = os.environ["SILICONFLOW_BASE_URL"].rstrip("/")
    api_key = os.environ["SILICONFLOW_API_KEY"]
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": case["system"]},
            {"role": "user", "content": json.dumps(case["user"], ensure_ascii=False)},
        ],
        "temperature": 0.1,
        "max_tokens": 900,
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        base_url + "/chat/completions",
        data=body,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Some SiliconFlow models may not support response_format. Retry without it.
        detail = exc.read().decode("utf-8", errors="ignore")
        if "response_format" not in detail:
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
        payload.pop("response_format", None)
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            base_url + "/chat/completions",
            data=body,
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


def response_content(resp: dict[str, object]) -> str:
    try:
        return clean(resp["choices"][0]["message"]["content"])  # type: ignore[index]
    except Exception:
        return ""


def extract_json_object(text: str) -> tuple[dict[str, object] | None, str]:
    text = clean(text)
    if not text:
        return None, "empty_content"
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    candidate = fenced.group(1) if fenced else text
    candidate = candidate.strip()
    if not candidate.startswith("{"):
        first = candidate.find("{")
        last = candidate.rfind("}")
        if first >= 0 and last > first:
            candidate = candidate[first : last + 1]
    try:
        return json.loads(candidate), ""
    except json.JSONDecodeError as exc:
        return None, f"json_parse_error: {exc}"


def normalize_result(case: dict[str, object], raw_resp: dict[str, object], err: str = "") -> dict[str, str]:
    user = case.get("user", {})
    case_obj = user.get("case", {}) if isinstance(user, dict) else {}
    case_id = clean(case_obj.get("id") if isinstance(case_obj, dict) else "")
    content = response_content(raw_resp) if raw_resp else ""
    parsed, parse_error = extract_json_object(content)
    parsed = parsed or {}
    return {
        "id": case_id,
        "model_verdict": clean(parsed.get("verdict")),
        "out": clean(parsed.get("out")),
        "mode": clean(parsed.get("mode")),
        "realized": clean(parsed.get("realized")),
        "event_date": clean(parsed.get("event_date")),
        "evidence": clean(parsed.get("evidence")),
        "reason": clean(parsed.get("reason")),
        "uncertainty": clean(parsed.get("uncertainty")),
        "review_priority": clean(parsed.get("review_priority")),
        "parse_error": parse_error,
        "api_error": err,
        "raw_content": content,
    }


def write_outputs(raw_records: list[dict[str, object]], parsed_rows: list[dict[str, str]], model: str) -> None:
    with OUT_RAW_JSONL.open("w", encoding="utf-8") as f:
        for record in raw_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    fields = [
        "id",
        "model_verdict",
        "out",
        "mode",
        "realized",
        "event_date",
        "evidence",
        "reason",
        "uncertainty",
        "review_priority",
        "parse_error",
        "api_error",
        "raw_content",
    ]
    with OUT_PARSED_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(parsed_rows)

    verdict_counts: dict[str, int] = {}
    parse_errors = 0
    api_errors = 0
    for row in parsed_rows:
        verdict = row["model_verdict"] or "missing"
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        if row["parse_error"]:
            parse_errors += 1
        if row["api_error"]:
            api_errors += 1

    lines = [
        "# SiliconFlow v49 pilot run",
        "",
        f"model: `{model}`",
        f"cases: {len(parsed_rows)}",
        f"parse_errors: {parse_errors}",
        f"api_errors: {api_errors}",
        "",
        "verdict_counts:",
    ]
    for verdict, count in sorted(verdict_counts.items()):
        lines.append(f"- `{verdict}`: {count}")
    lines.extend(
        [
            "",
            "files:",
            f"- {OUT_RAW_JSONL}",
            f"- {OUT_PARSED_CSV}",
        ]
    )
    OUT_SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("SILICONFLOW_MODEL", DEFAULT_MODEL))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.6)
    args = parser.parse_args()

    cases = load_cases(args.limit)
    raw_records: list[dict[str, object]] = []
    parsed_rows: list[dict[str, str]] = []

    for idx, case in enumerate(cases, 1):
        case_id = case.get("user", {}).get("case", {}).get("id", "")  # type: ignore[union-attr]
        print(f"[{idx}/{len(cases)}] {case_id}", flush=True)
        error = ""
        response: dict[str, object] = {}
        try:
            response = call_siliconflow(case, args.model)
        except Exception as exc:
            error = str(exc)
        raw_records.append({"case_id": case_id, "response": response, "api_error": error})
        parsed_rows.append(normalize_result(case, response, error))
        if idx < len(cases):
            time.sleep(args.sleep)

    write_outputs(raw_records, parsed_rows, args.model)
    print(f"Wrote {OUT_PARSED_CSV}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
