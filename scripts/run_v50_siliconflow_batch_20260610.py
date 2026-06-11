#!/usr/bin/env python3
"""Run a DeepSeek-compatible JSONL batch with retries and structured outputs."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
DEFAULT_BATCH_DIR = BASE / "results/v50_deepseek_v3_1_batch100_20260610"
DEFAULT_PROVIDER = "siliconflow"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V4-Pro"
PROVIDER_ENV = {
    "siliconflow": ("SILICONFLOW_BASE_URL", "SILICONFLOW_API_KEY"),
    "deepseek": ("DEEPSEEK_BASE_URL", "DEEPSEEK_API_KEY"),
}


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_cases(input_jsonl: Path, limit: int | None = None) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    with input_jsonl.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cases.append(json.loads(line))
            if limit is not None and len(cases) >= limit:
                break
    return cases


def load_existing_outputs(out_dir: Path) -> tuple[list[dict[str, object]], list[dict[str, str]], set[str]]:
    raw_records: list[dict[str, object]] = []
    parsed_rows: list[dict[str, str]] = []
    completed: set[str] = set()

    raw_path = out_dir / "siliconflow_raw_outputs.jsonl"
    if raw_path.exists():
        with raw_path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    raw_records.append(json.loads(line))

    parsed_path = out_dir / "siliconflow_parsed_outputs.csv"
    if parsed_path.exists():
        with parsed_path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                row = {k: clean(v) for k, v in row.items()}
                parsed_rows.append(row)
                if row.get("id") and row.get("model_verdict") and not row.get("parse_error") and not row.get("api_error"):
                    completed.add(row["id"])
    return raw_records, parsed_rows, completed


def case_id(case: dict[str, object]) -> str:
    user = case.get("user")
    if not isinstance(user, dict):
        return ""
    case_obj = user.get("case")
    if not isinstance(case_obj, dict):
        return ""
    return clean(case_obj.get("id"))


def call_chat_completion(
    case: dict[str, object],
    provider: str,
    model: str,
    timeout: int,
    use_response_format: bool,
) -> dict[str, object]:
    base_env, key_env = PROVIDER_ENV[provider]
    base_url = os.environ[base_env].rstrip("/")
    api_key = os.environ[key_env]
    payload: dict[str, object] = {
        "model": model,
        "messages": [
            {"role": "system", "content": case["system"]},
            {"role": "user", "content": json.dumps(case["user"], ensure_ascii=False)},
        ],
        "temperature": 0.1,
        "max_tokens": 900,
    }
    if use_response_format:
        payload["response_format"] = {"type": "json_object"}
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
    content = response_content(raw_resp) if raw_resp else ""
    parsed, parse_error = extract_json_object(content)
    parsed = parsed or {}
    return {
        "id": case_id(case),
        "model_verdict": clean(parsed.get("verdict")),
        "out": clean(parsed.get("out")),
        "mode": clean(parsed.get("mode")),
        "layer": clean(parsed.get("layer")),
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


def run_one(
    case: dict[str, object],
    provider: str,
    model: str,
    timeout: int,
    attempts: int,
    retry_sleep: float,
) -> tuple[list[dict[str, object]], dict[str, str]]:
    records: list[dict[str, object]] = []
    last_error = ""
    for attempt in range(1, attempts + 1):
        for response_format in (True, False):
            response: dict[str, object] = {}
            error = ""
            try:
                response = call_chat_completion(case, provider, model, timeout, response_format)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="ignore")
                error = f"HTTP {exc.code}: {detail}"
                if response_format and "response_format" in detail:
                    records.append(
                        {
                            "case_id": case_id(case),
                            "provider": provider,
                            "attempt": attempt,
                            "response_format": response_format,
                            "response": response,
                            "api_error": error,
                        }
                    )
                    continue
            except Exception as exc:
                error = str(exc)

            records.append(
                {
                    "case_id": case_id(case),
                    "provider": provider,
                    "attempt": attempt,
                    "response_format": response_format,
                    "response": response,
                    "api_error": error,
                }
            )
            if response and not error:
                parsed = normalize_result(case, response, "")
                if parsed["model_verdict"] and not parsed["parse_error"]:
                    return records, parsed
                last_error = parsed["parse_error"] or "missing_model_verdict"
            else:
                last_error = error
            break
        if attempt < attempts:
            time.sleep(retry_sleep)
    return records, normalize_result(case, {}, last_error)


def run_with_optional_fallback(
    case: dict[str, object],
    provider: str,
    model: str,
    fallback_provider: str | None,
    fallback_model: str,
    timeout: int,
    attempts: int,
    retry_sleep: float,
) -> tuple[str, list[dict[str, object]], dict[str, str], bool]:
    records, parsed = run_one(case, provider, model, timeout, attempts, retry_sleep)
    used_fallback = False
    if parsed["api_error"] and fallback_provider:
        fallback_records, parsed = run_one(
            case,
            fallback_provider,
            fallback_model,
            timeout,
            attempts,
            retry_sleep,
        )
        records.extend(fallback_records)
        used_fallback = True
    return case_id(case), records, parsed, used_fallback


def usage_totals(raw_records: list[dict[str, object]]) -> dict[str, int]:
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for record in raw_records:
        response = record.get("response")
        if not isinstance(response, dict):
            continue
        usage = response.get("usage")
        if not isinstance(usage, dict):
            continue
        for key in totals:
            try:
                totals[key] += int(usage.get(key) or 0)
            except (TypeError, ValueError):
                continue
    return totals


def write_outputs(
    out_dir: Path,
    raw_records: list[dict[str, object]],
    parsed_rows: list[dict[str, str]],
    provider: str,
    model: str,
) -> None:
    raw_path = out_dir / "siliconflow_raw_outputs.jsonl"
    parsed_path = out_dir / "siliconflow_parsed_outputs.csv"
    summary_path = out_dir / "siliconflow_run_summary.md"
    with raw_path.open("w", encoding="utf-8") as f:
        for record in raw_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    fields = [
        "id",
        "model_verdict",
        "out",
        "mode",
        "layer",
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
    with parsed_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(parsed_rows)

    verdict_counts: dict[str, int] = {}
    layer_counts: dict[str, int] = {}
    usage = usage_totals(raw_records)
    parse_errors = 0
    api_errors = 0
    for row in parsed_rows:
        verdict = row["model_verdict"] or "missing"
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        layer = row["layer"] or "missing"
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        if row["parse_error"]:
            parse_errors += 1
        if row["api_error"]:
            api_errors += 1

    lines = [
        "# DeepSeek-compatible batch run",
        "",
        f"provider: `{provider}`",
        f"model: `{model}`",
        f"cases: {len(parsed_rows)}",
        f"parsed_success: {len(parsed_rows) - parse_errors - api_errors}",
        f"parse_errors: {parse_errors}",
        f"api_errors_after_retry: {api_errors}",
        f"prompt_tokens: {usage['prompt_tokens']}",
        f"completion_tokens: {usage['completion_tokens']}",
        f"total_tokens: {usage['total_tokens']}",
        "",
        "verdict_counts:",
    ]
    for verdict, count in sorted(verdict_counts.items()):
        lines.append(f"- `{verdict}`: {count}")
    lines.extend(["", "layer_counts:"])
    for layer, count in sorted(layer_counts.items()):
        lines.append(f"- `{layer}`: {count}")
    lines.extend(
        [
            "",
            "files:",
            f"- {raw_path}",
            f"- {parsed_path}",
        ]
    )
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-dir", type=Path, default=DEFAULT_BATCH_DIR)
    parser.add_argument("--input-jsonl", type=Path, default=None)
    parser.add_argument("--provider", choices=sorted(PROVIDER_ENV), default=os.environ.get("LLM_PROVIDER", DEFAULT_PROVIDER))
    parser.add_argument("--model", default=os.environ.get("SILICONFLOW_MODEL", DEFAULT_MODEL))
    parser.add_argument("--fallback-provider", choices=sorted(PROVIDER_ENV), default=None)
    parser.add_argument("--fallback-model", default=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.8)
    parser.add_argument("--retry-sleep", type=float, default=2.0)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--no-incremental-write", action="store_true")
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    batch_dir = args.batch_dir
    input_jsonl = args.input_jsonl or batch_dir / "deepseek_cases.jsonl"
    cases = load_cases(input_jsonl, args.limit)

    if args.restart:
        raw_records: list[dict[str, object]] = []
        parsed_rows: list[dict[str, str]] = []
        completed_ids: set[str] = set()
    else:
        raw_records, parsed_rows, completed_ids = load_existing_outputs(batch_dir)
        if completed_ids:
            print(f"Resuming: {len(completed_ids)} completed cases already parsed", flush=True)
    pending_cases: list[tuple[int, dict[str, object]]] = []
    for idx, case in enumerate(cases, 1):
        cid = case_id(case)
        if cid in completed_ids:
            print(f"[{idx}/{len(cases)}] {cid} skip", flush=True)
            continue
        pending_cases.append((idx, case))

    if args.workers <= 1:
        for idx, case in pending_cases:
            cid = case_id(case)
            print(f"[{idx}/{len(cases)}] {cid}", flush=True)
            cid, records, parsed, used_fallback = run_with_optional_fallback(
                case,
                args.provider,
                args.model,
                args.fallback_provider,
                args.fallback_model,
                args.timeout,
                args.attempts,
                args.retry_sleep,
            )
            if used_fallback:
                print(f"  {cid} fallback -> {args.fallback_provider}", flush=True)
            raw_records.extend(records)
            parsed_rows.append(parsed)
            if not args.no_incremental_write:
                write_outputs(batch_dir, raw_records, parsed_rows, args.provider, args.model)
            time.sleep(args.sleep)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {}
            for idx, case in pending_cases:
                cid = case_id(case)
                print(f"[{idx}/{len(cases)}] {cid} submit", flush=True)
                fut = executor.submit(
                    run_with_optional_fallback,
                    case,
                    args.provider,
                    args.model,
                    args.fallback_provider,
                    args.fallback_model,
                    args.timeout,
                    args.attempts,
                    args.retry_sleep,
                )
                futures[fut] = (idx, cid)
                if args.sleep:
                    time.sleep(args.sleep)
            finished = 0
            for fut in as_completed(futures):
                idx, cid = futures[fut]
                finished += 1
                try:
                    cid, records, parsed, used_fallback = fut.result()
                except Exception as exc:
                    records = []
                    parsed = normalize_result({"user": {"case": {"id": cid}}}, {}, str(exc))
                    used_fallback = False
                status = parsed["model_verdict"] or "ERR"
                suffix = f", fallback={args.fallback_provider}" if used_fallback else ""
                print(f"[done {finished}/{len(pending_cases)} | original {idx}/{len(cases)}] {cid} {status}{suffix}", flush=True)
                raw_records.extend(records)
                parsed_rows.append(parsed)
                if not args.no_incremental_write:
                    write_outputs(batch_dir, raw_records, parsed_rows, args.provider, args.model)

    write_outputs(batch_dir, raw_records, parsed_rows, args.provider, args.model)
    print(f"Wrote {batch_dir / 'siliconflow_parsed_outputs.csv'}")
    print(f"Wrote {batch_dir / 'siliconflow_run_summary.md'}")


if __name__ == "__main__":
    main()
