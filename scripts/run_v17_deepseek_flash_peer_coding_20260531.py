#!/usr/bin/env python3
"""Use DeepSeek Flash to select product-market peers from compact candidates.

The script reads the v16 no-random candidate pool, sends compact focal/candidate
menus to an OpenAI-compatible DeepSeek endpoint, and writes an auditable peer
network. It deliberately reads the API key from DEEPSEEK_API_KEY and never
stores the key in outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

from run_v6_announcement_clean_checks_20260524 import ROOT


OUT_DIR = ROOT / "results" / "v17_deepseek_flash_peer_coding_20260531"
SCORED_CANDIDATES = (
    ROOT / "results" / "v16_full_semantic_reranked_peers_20260531" / "full_semantic_candidate_scores.csv.gz"
)

NO_RANDOM_SOURCES = ["annual_same_industry", "csmar_scope", "annual_global_ai_stripped"]
SOURCE_QUOTAS = {
    "annual_same_industry": 6,
    "csmar_scope": 6,
    "annual_global_ai_stripped": 3,
}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(6) if digits else ""


def compact_text(value: object, n: int) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\s+", "", str(value))
    text = text.replace('"', "'")
    return text[:n]


def load_candidate_rows(max_candidates: int) -> pd.DataFrame:
    df = pd.read_csv(SCORED_CANDIDATES, dtype={"focal_code": str, "peer_code": str})
    df = df[df["candidate_source_system"].isin(NO_RANDOM_SOURCES)].copy()
    df["focal_code"] = df["focal_code"].map(code6)
    df["peer_code"] = df["peer_code"].map(code6)
    for col in ["source_priority", "source_rank", "product_similarity", "semantic_score_0_3", "semantic_direct_peer"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    rows: list[pd.DataFrame] = []
    for focal, g in df.groupby("focal_code", sort=True):
        selected_parts = []
        for source, quota in SOURCE_QUOTAS.items():
            s = g[g["candidate_source_system"].eq(source)].sort_values(
                ["source_rank", "product_similarity"], ascending=[True, False]
            )
            selected_parts.append(s.head(quota))
        selected = pd.concat(selected_parts, ignore_index=True)
        if selected.empty:
            continue
        selected = selected.drop_duplicates("peer_code", keep="first")
        if len(selected) < max_candidates:
            fill = g.sort_values(
                [
                    "semantic_score_0_3",
                    "semantic_direct_peer",
                    "source_priority",
                    "product_similarity",
                    "source_rank",
                ],
                ascending=[False, False, True, False, True],
            )
            selected = pd.concat([selected, fill], ignore_index=True).drop_duplicates(
                "peer_code", keep="first"
            )
        selected = selected.head(max_candidates).copy()
        selected["candidate_order"] = range(1, len(selected) + 1)
        rows.append(selected)
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    return out


def build_items(candidates: pd.DataFrame) -> list[dict[str, Any]]:
    items = []
    for focal, g in candidates.groupby("focal_code", sort=True):
        first = g.iloc[0]
        item = {
            "focal": focal,
            "name": str(first.get("focal_name_final", "")),
            "industry": str(first.get("focal_industry_final", "")),
            "business": compact_text(first.get("focal_scope_excerpt", ""), 120),
            "candidates": [],
        }
        for _, r in g.sort_values("candidate_order").iterrows():
            item["candidates"].append(
                {
                    "code": r["peer_code"],
                    "name": str(r.get("peer_name_final", "")),
                    "industry": str(r.get("peer_industry_final", "")),
                    "source": str(r.get("candidate_source_system", "")),
                    "business": compact_text(r.get("peer_scope_excerpt", ""), 70),
                }
            )
        items.append(item)
    return items


def chunks(items: list[dict[str, Any]], batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def make_messages(batch: list[dict[str, Any]]) -> list[dict[str, str]]:
    system = (
        "You identify direct product-market peer firms for Chinese listed companies. "
        "Choose peers that sell similar products/services to similar customers/use cases. "
        "Do not choose suppliers, customers, infrastructure complements, or firms that only share generic labels. "
        "Use only candidate codes provided. Return compact valid JSON only."
    )
    user = {
        "task": "For each focal firm, select up to 5 closest direct product-market peers from candidates.",
        "output_schema": {
            "results": [
                {
                    "focal": "000001",
                    "peers": ["600000", "601398", "601939", "601288", "601328"],
                }
            ]
        },
        "rules": [
            "peers must be chosen from the candidate list for the same focal",
            "rank from closest to less close",
            "if fewer than 5 direct product-market peers exist, return fewer",
            "do not include explanations or fields other than focal and peers",
        ],
        "items": batch,
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False, separators=(",", ":"))},
    ]


def post_chat(api_key: str, model: str, messages: list[dict[str, str]], timeout: int = 90) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": 1200,
        "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data


def parse_response(data: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    usage = data.get("usage", {})
    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    if isinstance(parsed, list):
        results = parsed
    elif isinstance(parsed, dict):
        results = parsed.get("results", [])
    else:
        results = []
    if not isinstance(results, list):
        raise ValueError("results is not a list")
    return results, usage


def validate_results(batch: list[dict[str, Any]], results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = {item["focal"]: {c["code"] for c in item["candidates"]} for item in batch}
    out = []
    for res in results:
        focal = code6(res.get("focal"))
        if focal not in allowed:
            continue
        seen: set[str] = set()
        rank = 0
        peers = res.get("peers", [])
        if not isinstance(peers, list):
            continue
        for p in peers:
            code = code6(p.get("code") if isinstance(p, dict) else p)
            if code not in allowed[focal] or code in seen:
                continue
            seen.add(code)
            rank += 1
            reason = p.get("reason", "") if isinstance(p, dict) else ""
            out.append(
                {
                    "focal_code": focal,
                    "peer_code": code,
                    "llm_rank": rank,
                    "llm_reason": str(reason)[:40],
                }
            )
            if rank >= 5:
                break
    return out


def load_done(raw_path: Path) -> set[str]:
    if not raw_path.exists():
        return set()
    done = set()
    with raw_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            for focal in obj.get("focals", []):
                done.add(code6(focal))
    return done


def write_network(coded: pd.DataFrame, candidates: pd.DataFrame, out_path: Path) -> None:
    if coded.empty:
        coded.to_csv(out_path, index=False)
        return
    meta_cols = [
        "focal_code",
        "peer_code",
        "focal_name_final",
        "peer_name_final",
        "focal_industry_final",
        "peer_industry_final",
        "candidate_source_system",
        "source_rank",
        "product_similarity",
    ]
    meta = candidates[meta_cols].drop_duplicates(["focal_code", "peer_code"])
    net = coded.merge(meta, on=["focal_code", "peer_code"], how="left")
    net = net.sort_values(["focal_code", "llm_rank"])
    net["peer_source"] = "deepseek_flash_peer"
    net["top_n"] = 5
    net = net.rename(
        columns={
            "llm_rank": "peer_rank",
            "product_similarity": "peer_similarity",
            "focal_name_final": "focal_name",
            "peer_name_final": "peer_name",
            "focal_industry_final": "focal_industry_d",
            "peer_industry_final": "peer_industry_d",
        }
    )
    keep = [
        "peer_source",
        "top_n",
        "focal_code",
        "peer_code",
        "peer_rank",
        "peer_similarity",
        "focal_name",
        "peer_name",
        "focal_industry_d",
        "peer_industry_d",
        "candidate_source_system",
        "source_rank",
        "llm_reason",
    ]
    net[keep].to_csv(out_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--max-candidates", type=int, default=15)
    parser.add_argument("--sleep", type=float, default=0.15)
    parser.add_argument("--tag", default="pilot")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY is required")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_candidate_rows(args.max_candidates)
    items = build_items(candidates)
    items = items[args.offset :]
    if args.limit is not None:
        items = items[: args.limit]

    raw_path = OUT_DIR / f"deepseek_flash_raw_{args.tag}.jsonl"
    coded_path = OUT_DIR / f"deepseek_flash_peer_choices_{args.tag}.csv"
    network_path = OUT_DIR / f"deepseek_flash_peer_network_top5_{args.tag}.csv"
    log_path = OUT_DIR / f"deepseek_flash_run_log_{args.tag}.csv"

    done = load_done(raw_path) if args.resume else set()
    coded_rows: list[dict[str, Any]] = []
    log_rows: list[dict[str, Any]] = []
    if coded_path.exists() and args.resume:
        coded_rows.extend(pd.read_csv(coded_path, dtype={"focal_code": str, "peer_code": str}).to_dict("records"))

    todo = [x for x in items if x["focal"] not in done]
    for batch_id, batch in enumerate(chunks(todo, args.batch_size), start=1):
        focals = [x["focal"] for x in batch]
        messages = make_messages(batch)
        started = time.time()
        status = "ok"
        error = ""
        usage: dict[str, Any] = {}
        choices: list[dict[str, Any]] = []
        for attempt in range(3):
            try:
                data = post_chat(api_key, args.model, messages)
                results, usage = parse_response(data)
                choices = validate_results(batch, results)
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
                status = "error"
                error = f"{type(exc).__name__}: {exc}"
                if attempt == 2:
                    break
                time.sleep(1.5 * (attempt + 1))
        elapsed = time.time() - started
        if choices:
            coded_rows.extend(choices)
            status = "ok"
            error = ""
        log_rows.append(
            {
                "batch_id": batch_id,
                "focals": ",".join(focals),
                "status": status,
                "error": error,
                "elapsed_sec": round(elapsed, 3),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "selected_rows": len(choices),
            }
        )
        with raw_path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "batch_id": batch_id,
                        "focals": focals,
                        "status": status,
                        "error": error,
                        "usage": usage,
                        "choices": choices,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        pd.DataFrame(coded_rows).drop_duplicates(["focal_code", "peer_code"]).to_csv(coded_path, index=False)
        pd.DataFrame(log_rows).to_csv(log_path, index=False)
        if batch_id % 10 == 0 or batch_id == 1:
            print(
                {
                    "batch": batch_id,
                    "done_focals": min(batch_id * args.batch_size, len(todo)),
                    "choices": len(coded_rows),
                    "last_status": status,
                    "last_tokens": usage.get("total_tokens"),
                },
                flush=True,
            )
        time.sleep(args.sleep)

    coded = pd.DataFrame(coded_rows).drop_duplicates(["focal_code", "peer_code"])
    coded.to_csv(coded_path, index=False)
    write_network(coded, candidates, network_path)

    total_prompt = pd.to_numeric(pd.DataFrame(log_rows).get("prompt_tokens"), errors="coerce").sum()
    total_completion = pd.to_numeric(pd.DataFrame(log_rows).get("completion_tokens"), errors="coerce").sum()
    summary = {
        "tag": args.tag,
        "model": args.model,
        "input_focals": len(items),
        "attempted_focals": len(todo),
        "selected_pairs": int(len(coded)),
        "prompt_tokens": int(total_prompt) if pd.notna(total_prompt) else None,
        "completion_tokens": int(total_completion) if pd.notna(total_completion) else None,
        "output_network": str(network_path),
    }
    (OUT_DIR / f"deepseek_flash_summary_{args.tag}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(summary, flush=True)


if __name__ == "__main__":
    main()
