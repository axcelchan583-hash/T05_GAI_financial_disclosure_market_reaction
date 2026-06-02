#!/usr/bin/env python3
"""Build Cao-style open-ended DeepSeek product-market peers and test PeerCAR.

This script is deliberately separate from v17. The v17 peer network asks
DeepSeek to select peers from an auditable candidate menu. This v18 diagnostic
follows Cao, Chen, Tucker, and Wan (2025) more closely: it asks the model to
generate A-share product-market competitors without a candidate menu, then
matches the generated names/codes back to the local A-share universe.

The API key is read from DEEPSEEK_API_KEY and is never written to outputs.
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

from run_v15_alternative_peer_definitions_20260531 import (
    attach_ai_flags,
    attach_returns,
    format_table,
    run_model,
    source_summary,
)
from run_v16_full_semantic_reranked_peer_network_20260531 import build_event_peer_panel
from run_v17_deepseek_flash_peer_coding_20260531 import post_chat
from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    attach_announcement_flags,
    build_announcement_stock_day_flags,
)
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    load_stock_model,
)


OUT_DIR = ROOT / "results" / "v18_cao_style_open_ended_deepseek_peers_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "82_v18_cao_style_open_ended_deepseek_peers_20260531.md"
SCORED_CANDIDATES = (
    ROOT / "results" / "v16_full_semantic_reranked_peers_20260531" / "full_semantic_candidate_scores.csv.gz"
)


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(6) if digits else ""


def norm_name(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[（）()【】\\[\\]·,，.。:：;；'\"“”‘’]", "", text)
    for token in ["股份有限公司", "有限责任公司", "集团股份", "集团", "股份", "有限", "公司", "控股"]:
        text = text.replace(token, "")
    text = text.replace("Ａ", "A").replace("Ｂ", "B")
    return text.upper()


def compact_text(value: object, n: int = 160) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\s+", "", str(value)).replace('"', "'")
    return text[:n]


def load_universe_and_focals() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(SCORED_CANDIDATES, dtype={"focal_code": str, "peer_code": str})
    df["focal_code"] = df["focal_code"].map(code6)
    df["peer_code"] = df["peer_code"].map(code6)

    focal = df[
        [
            "focal_code",
            "focal_name_final",
            "focal_industry_final",
            "focal_scope_excerpt",
        ]
    ].drop_duplicates("focal_code")
    focal = focal.rename(
        columns={
            "focal_code": "stock_code",
            "focal_name_final": "stock_name",
            "focal_industry_final": "industry",
            "focal_scope_excerpt": "business",
        }
    )
    peer = df[
        [
            "peer_code",
            "peer_name_final",
            "peer_industry_final",
            "peer_scope_excerpt",
        ]
    ].drop_duplicates("peer_code")
    peer = peer.rename(
        columns={
            "peer_code": "stock_code",
            "peer_name_final": "stock_name",
            "peer_industry_final": "industry",
            "peer_scope_excerpt": "business",
        }
    )
    universe = pd.concat([focal, peer], ignore_index=True)
    universe["stock_code"] = universe["stock_code"].map(code6)
    universe = universe[universe["stock_code"].ne("")]
    universe = universe.drop_duplicates("stock_code", keep="first")
    universe["name_key"] = universe["stock_name"].map(norm_name)

    focals = focal.copy()
    focals["stock_code"] = focals["stock_code"].map(code6)
    focals = focals[focals["stock_code"].ne("")]
    focals = focals.drop_duplicates("stock_code", keep="first")
    return universe, focals


def build_items(focals: pd.DataFrame) -> list[dict[str, str]]:
    items = []
    for _, r in focals.sort_values("stock_code").iterrows():
        items.append(
            {
                "code": r["stock_code"],
                "name": str(r.get("stock_name", "")),
                "industry": str(r.get("industry", "")),
                "business": compact_text(r.get("business", ""), 160),
            }
        )
    return items


def chunks(items: list[dict[str, str]], batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def make_messages(batch: list[dict[str, str]], as_of_year: int) -> list[dict[str, str]]:
    system = (
        "You identify direct product-market competitors among Chinese A-share listed firms. "
        "Use product/service overlap, customer/use-case overlap, and market substitution. "
        "Do not list suppliers, customers, or infrastructure complements unless they sell substitute products. "
        "Return compact valid JSON only."
    )
    user = {
        "task": "For each focal firm, list up to 5 closest product-market competitors among Chinese A-share listed companies.",
        "as_of": f"end of {as_of_year}",
        "output_schema": {
            "results": [
                {
                    "focal": "000001",
                    "peers": [
                        {"code": "600000", "name": "浦发银行"},
                        {"code": "601398", "name": "工商银行"},
                    ],
                }
            ]
        },
        "rules": [
            "Only include A-share listed companies.",
            "Return six-digit stock code when known; also return the Chinese stock short name.",
            "Rank peers from closest to less close.",
            "Return fewer than 5 if uncertain.",
            "Do not include explanations or fields other than focal and peers.",
        ],
        "focal_firms": batch,
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False, separators=(",", ":"))},
    ]


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


def build_match_maps(universe: pd.DataFrame) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    by_code = universe.set_index("stock_code").to_dict("index")
    by_name: dict[str, list[str]] = {}
    for _, r in universe.iterrows():
        key = r["name_key"]
        if key:
            by_name.setdefault(key, []).append(r["stock_code"])
    return by_code, by_name


def match_peer(raw_peer: object, by_code: dict[str, dict[str, Any]], by_name: dict[str, list[str]]) -> tuple[str, str]:
    if isinstance(raw_peer, dict):
        raw_code = raw_peer.get("code", "")
        raw_name = raw_peer.get("name", "")
    else:
        raw_code = raw_peer
        raw_name = raw_peer
    code = code6(raw_code)
    if code in by_code:
        return code, "code"
    name_key = norm_name(raw_name)
    candidates = by_name.get(name_key, [])
    if len(candidates) == 1:
        return candidates[0], "exact_name"
    return "", "unmatched"


def validate_results(
    batch: list[dict[str, str]],
    results: list[dict[str, Any]],
    by_code: dict[str, dict[str, Any]],
    by_name: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    requested = {x["code"] for x in batch}
    matched: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    for res in results:
        focal = code6(res.get("focal"))
        if focal not in requested:
            continue
        seen: set[str] = set()
        rank = 0
        peers = res.get("peers", [])
        if not isinstance(peers, list):
            continue
        for raw_peer in peers:
            peer_code, match_method = match_peer(raw_peer, by_code, by_name)
            raw_code = raw_peer.get("code", "") if isinstance(raw_peer, dict) else raw_peer
            raw_name = raw_peer.get("name", "") if isinstance(raw_peer, dict) else raw_peer
            if not peer_code:
                unmatched.append(
                    {
                        "focal_code": focal,
                        "raw_peer_code": raw_code,
                        "raw_peer_name": raw_name,
                        "match_status": match_method,
                    }
                )
                continue
            if peer_code == focal or peer_code in seen:
                continue
            seen.add(peer_code)
            rank += 1
            matched.append(
                {
                    "focal_code": focal,
                    "peer_code": peer_code,
                    "llm_rank": rank,
                    "raw_peer_code": raw_code,
                    "raw_peer_name": raw_name,
                    "match_method": match_method,
                }
            )
            if rank >= 5:
                break
    return matched, unmatched


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
            if obj.get("status") == "ok":
                done.update(code6(x) for x in obj.get("focals", []))
    return done


def write_network(coded: pd.DataFrame, universe: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    if coded.empty:
        coded.to_csv(out_path, index=False)
        return coded
    u_peer = universe.rename(
        columns={
            "stock_code": "peer_code",
            "stock_name": "peer_name",
            "industry": "peer_industry_d",
        }
    )[["peer_code", "peer_name", "peer_industry_d"]]
    u_focal = universe.rename(
        columns={
            "stock_code": "focal_code",
            "stock_name": "focal_name",
            "industry": "focal_industry_d",
        }
    )[["focal_code", "focal_name", "focal_industry_d"]]
    net = coded.merge(u_focal, on="focal_code", how="left")
    net = net.merge(u_peer, on="peer_code", how="left")
    net = net.sort_values(["focal_code", "llm_rank"])
    net["peer_source"] = "deepseek_open_ended_cao_style"
    net["top_n"] = 5
    net["peer_similarity"] = pd.NA
    net["candidate_source_system"] = "open_ended_llm"
    net["source_rank"] = pd.NA
    net = net.rename(columns={"llm_rank": "peer_rank"})
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
        "raw_peer_code",
        "raw_peer_name",
        "match_method",
    ]
    net[keep].to_csv(out_path, index=False)
    return net[keep]


def run_main_effect(network_path: Path, tag: str) -> pd.DataFrame:
    network = pd.read_csv(network_path, dtype={"focal_code": str, "peer_code": str})
    if network.empty:
        return pd.DataFrame()
    network["peer_source"] = "deepseek_open_ended_cao_style"
    lookup = build_return_lookup(load_stock_model())
    ann_flags = build_announcement_stock_day_flags()
    panel = build_event_peer_panel(network)
    panel = attach_returns(panel, lookup)
    panel = attach_announcement_flags(panel, ann_flags)
    panel = attach_ai_flags(panel)
    panel.to_csv(OUT_DIR / f"deepseek_open_ended_event_peer_panel_{tag}.csv.gz", index=False, compression="gzip")

    summaries = pd.DataFrame([source_summary(panel, "deepseek_open_ended_cao_style")])
    regs = []
    for top_n in [3, 5]:
        for ai_def in ["ext_any", "current_text_history", "ext_no_hiring", "ext_plus_history"]:
            regs.append(run_model(panel, ai_def, "deepseek_open_ended_cao_style", top_n))
    res = pd.DataFrame(regs)
    summaries.to_csv(OUT_DIR / f"deepseek_open_ended_coverage_summary_{tag}.csv", index=False)
    res.to_csv(OUT_DIR / f"deepseek_open_ended_main_effects_{tag}.csv", index=False)
    return res


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--sleep", type=float, default=0.15)
    parser.add_argument("--tag", default="pilot")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--as-of-year", type=int, default=2025)
    parser.add_argument("--skip-api", action="store_true")
    parser.add_argument("--run-regression", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    universe, focals = load_universe_and_focals()
    universe.to_csv(OUT_DIR / "ashare_universe_for_open_ended_matching.csv", index=False)
    items = build_items(focals)
    items = items[args.offset :]
    if args.limit is not None:
        items = items[: args.limit]

    raw_path = OUT_DIR / f"deepseek_open_ended_raw_{args.tag}.jsonl"
    coded_path = OUT_DIR / f"deepseek_open_ended_peer_choices_{args.tag}.csv"
    unmatched_path = OUT_DIR / f"deepseek_open_ended_unmatched_{args.tag}.csv"
    network_path = OUT_DIR / f"deepseek_open_ended_peer_network_top5_{args.tag}.csv"
    log_path = OUT_DIR / f"deepseek_open_ended_run_log_{args.tag}.csv"
    summary_path = OUT_DIR / f"deepseek_open_ended_summary_{args.tag}.json"

    coded_rows: list[dict[str, Any]] = []
    unmatched_rows: list[dict[str, Any]] = []
    log_rows: list[dict[str, Any]] = []
    if coded_path.exists() and args.resume:
        coded_rows.extend(pd.read_csv(coded_path, dtype={"focal_code": str, "peer_code": str}).to_dict("records"))
    if unmatched_path.exists() and args.resume:
        unmatched_rows.extend(pd.read_csv(unmatched_path, dtype=str).to_dict("records"))
    if log_path.exists() and args.resume:
        log_rows.extend(pd.read_csv(log_path, dtype=str).to_dict("records"))

    if not args.skip_api:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise SystemExit("DEEPSEEK_API_KEY is required unless --skip-api is set")
        by_code, by_name = build_match_maps(universe)
        done = load_done(raw_path) if args.resume else set()
        todo = [x for x in items if x["code"] not in done]
        start_batch_id = len(log_rows) + 1
        for batch_id, batch in enumerate(chunks(todo, args.batch_size), start=start_batch_id):
            focals_in_batch = [x["code"] for x in batch]
            messages = make_messages(batch, args.as_of_year)
            started = time.time()
            status = "ok"
            error = ""
            usage: dict[str, Any] = {}
            matched: list[dict[str, Any]] = []
            unmatched: list[dict[str, Any]] = []
            for attempt in range(3):
                try:
                    data = post_chat(api_key, args.model, messages, timeout=120)
                    results, usage = parse_response(data)
                    matched, unmatched = validate_results(batch, results, by_code, by_name)
                    break
                except (
                    urllib.error.HTTPError,
                    urllib.error.URLError,
                    TimeoutError,
                    json.JSONDecodeError,
                    KeyError,
                    ValueError,
                ) as exc:
                    status = "error"
                    error = f"{type(exc).__name__}: {exc}"
                    if attempt == 2:
                        break
                    time.sleep(1.5 * (attempt + 1))
            elapsed = time.time() - started
            if matched:
                coded_rows.extend(matched)
                unmatched_rows.extend(unmatched)
                status = "ok"
                error = ""
            log_rows.append(
                {
                    "batch_id": batch_id,
                    "focals": ",".join(focals_in_batch),
                    "status": status,
                    "error": error,
                    "elapsed_sec": round(elapsed, 3),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                    "matched_rows": len(matched),
                    "unmatched_rows": len(unmatched),
                }
            )
            with raw_path.open("a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "batch_id": batch_id,
                            "focals": focals_in_batch,
                            "status": status,
                            "error": error,
                            "usage": usage,
                            "matched": matched,
                            "unmatched": unmatched,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            pd.DataFrame(coded_rows).drop_duplicates(["focal_code", "peer_code"]).to_csv(coded_path, index=False)
            pd.DataFrame(unmatched_rows).to_csv(unmatched_path, index=False)
            pd.DataFrame(log_rows).to_csv(log_path, index=False)
            if batch_id % 10 == 0 or batch_id == 1:
                print(
                    {
                        "batch": batch_id,
                        "done_focals": min(batch_id * args.batch_size, len(todo)),
                        "matched_rows": len(coded_rows),
                        "unmatched_rows": len(unmatched_rows),
                        "last_status": status,
                        "last_tokens": usage.get("total_tokens"),
                    },
                    flush=True,
                )
            time.sleep(args.sleep)

    coded = (
        pd.DataFrame(coded_rows)
        if coded_rows
        else pd.read_csv(coded_path, dtype={"focal_code": str, "peer_code": str})
        if coded_path.exists()
        else pd.DataFrame()
    )
    if not coded.empty:
        coded["focal_code"] = coded["focal_code"].map(code6)
        coded["peer_code"] = coded["peer_code"].map(code6)
        coded = coded.drop_duplicates(["focal_code", "peer_code"], keep="first")
    coded.to_csv(coded_path, index=False)
    network = write_network(coded, universe, network_path)

    log_df = pd.DataFrame(log_rows)
    total_prompt = pd.to_numeric(log_df.get("prompt_tokens"), errors="coerce").sum() if not log_df.empty else None
    total_completion = pd.to_numeric(log_df.get("completion_tokens"), errors="coerce").sum() if not log_df.empty else None
    summary = {
        "tag": args.tag,
        "model": args.model,
        "as_of_year": args.as_of_year,
        "input_focals": len(items),
        "selected_pairs": int(len(coded)),
        "network_pairs": int(len(network)),
        "focals_with_at_least_one_peer": int(network["focal_code"].nunique()) if not network.empty else 0,
        "prompt_tokens": int(total_prompt) if total_prompt is not None and pd.notna(total_prompt) else None,
        "completion_tokens": int(total_completion) if total_completion is not None and pd.notna(total_completion) else None,
        "output_network": str(network_path),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    regs = pd.DataFrame()
    if args.run_regression:
        regs = run_main_effect(network_path, args.tag)

    doc = f"""# v18 Cao-Style Open-Ended DeepSeek Peers

Date: 2026-05-31

Purpose: diagnostic peer definition closer to Cao, Chen, Tucker, and Wan (2025).
Unlike v17, this pass does **not** provide a candidate menu. DeepSeek is asked to
generate up to five A-share product-market competitors for each focal firm, and
the generated names/codes are matched back to the local A-share universe.

## Setup

- Model: `{args.model}`
- As-of year in prompt: `{args.as_of_year}`
- Candidate menu: none
- Matching: generated six-digit code first; exact normalized Chinese short name
  second.
- API key source: `DEEPSEEK_API_KEY`; not stored in outputs.

## Summary

```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```

## Main Effects

Specification is identical to v17:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

{format_table(regs, ['peer_source','top_n','ai_def','coef','se','p','nobs','events','focal_firms','peer_firms','mean_y','mean_ai']) if not regs.empty else 'Regression not run.'}

## Interpretation Boundary

This is closer to Cao et al. than v17, but it is also noisier in China because
open-ended generation can produce HK/US firms, subsidiaries, private firms, or
historically unavailable competitors. For this reason it should be read as a
robustness check against the auditable candidate-menu DeepSeek network, not as a
drop-in replacement unless validation quality is high.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(summary, flush=True)
    if not regs.empty:
        print(regs.to_string(index=False), flush=True)
    print(f"Wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
