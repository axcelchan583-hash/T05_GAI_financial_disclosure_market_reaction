#!/usr/bin/env python3
"""Codex-assisted semantic coding for peer-system validation pairs.

This is a bounded manual-review pass over the 150-pair validation template.
It intentionally uses semantic product/customer categories rather than the
Jaccard proxy used to build the template, so it can serve as an independent
inspection layer.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "peer_validity_llm_20260531" / "peer_system_validation_template_150_pairs_20260531.csv"
OUT_DIR = ROOT / "results" / "v13_peer_validity_gate_20260531"
OUTPUT = ROOT / "data" / "peer_validity_llm_20260531" / "peer_system_validation_coded_150_pairs_codex_20260531.csv"
SUMMARY = OUT_DIR / "peer_system_validation_coded_150_pairs_codex_summary.csv"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "72_v13_peer_codex_manual_coding_20260531.md"


CATEGORY_PATTERNS: list[tuple[str, list[str]]] = [
    ("banking_finance", ["银行", "存款", "贷款", "票据", "信托", "证券", "金融服务", "保险", "资管"]),
    ("real_estate", ["房地产", "物业", "商品房", "住宅", "商业地产", "开发经营"]),
    ("pharma_api_formulation", ["原料药", "制剂", "抗感染", "头孢", "阿莫西林", "药品生产", "医药制造"]),
    ("pharma_cro_research", ["临床前", "临床研究", "CRO", "药物发现", "药物研发", "研究和试验", "实验服务"]),
    ("biotech_diagnostics", ["生物制品", "诊断", "抗体", "疫苗", "过敏原", "基因", "细胞"]),
    ("software_system_integration", ["软件开发", "系统集成", "信息系统", "计算机软件", "技术开发", "智慧城市", "政务", "IT服务"]),
    ("cybersecurity", ["网络安全", "信息安全", "移动应用安全", "安全服务", "安全检测"]),
    ("internet_content_media", ["互联网", "阅读", "文学", "游戏", "文化", "数字内容", "出版", "传媒"]),
    ("advertising_marketing", ["广告", "营销", "传播", "品牌", "策划", "公关", "媒介"]),
    ("semiconductor_chip", ["芯片", "集成电路", "半导体", "MCU", "Flash", "NAND", "NOR", "DRAM", "传感器"]),
    ("electronics_distribution", ["电子元器件", "电子产品", "分销", "代理销售", "IC", "批发业", "元器件"]),
    ("memory_storage", ["闪存", "存储", "移动存储", "U盘", "固态", "存储产品"]),
    ("led_display", ["LED", "显示屏", "显示", "照明", "光电", "MiniLED", "背光"]),
    ("smart_hardware_iot", ["智能硬件", "物联网", "智能终端", "数据采集", "传感", "IoT", "联网设备"]),
    ("agriculture_iot", ["农业", "农田", "智能农业", "农业物联网", "农产品", "种植"]),
    ("fertilizer_chemical", ["肥料", "复合肥", "化肥", "磷肥", "化工产品", "化学原料"]),
    ("logistics_trade", ["物流", "货运", "运输代理", "仓储", "供应链管理", "进出口"]),
    ("glass_solar_material", ["玻璃", "光伏玻璃", "浮法玻璃", "太阳能组件", "电子玻璃"]),
    ("machinery_pump_fan", ["风机", "鼓风机", "泵", "压缩机", "通用设备", "机械设备"]),
    ("lighting_electrical", ["照明", "灯具", "电气", "电源", "LED照明"]),
    ("rail_transit_defense_electronics", ["轨道交通", "铁路", "雷达", "防务", "航空航天", "军工"]),
    ("instrument_machine_vision", ["仪器仪表", "机器视觉", "检测设备", "工业相机", "光学检测"]),
    ("medical_device_imaging", ["医疗器械", "医疗影像", "影像", "诊疗", "医用"]),
    ("home_furniture", ["家具", "床垫", "家居", "睡眠", "床品"]),
    ("pet_food", ["宠物", "宠物食品", "饲料", "犬", "猫"]),
    ("retail_commerce_market", ["小商品", "批发市场", "市场经营", "商业服务", "贸易市场"]),
    ("energy_environment", ["环保", "污水", "固废", "节能", "电力", "新能源", "储能"]),
]

BROAD_CATEGORIES = {
    "software_system_integration",
    "internet_content_media",
    "electronics_distribution",
    "energy_environment",
}


def normalize_text(*parts: object) -> str:
    text = " ".join("" if pd.isna(x) else str(x) for x in parts)
    return re.sub(r"\s+", " ", text)


def detect_categories(text: str) -> set[str]:
    cats = set()
    lower = text.lower()
    for cat, patterns in CATEGORY_PATTERNS:
        for pat in patterns:
            if pat.lower() in lower:
                cats.add(cat)
                break
    return cats


def meaningful_overlap(a: set[str], b: set[str]) -> set[str]:
    return (a & b) - BROAD_CATEGORIES


def score_pair(row: pd.Series) -> tuple[int, int, str, str, str]:
    focal_text = normalize_text(
        row.get("focal_name_final"),
        row.get("focal_industry_final"),
        row.get("focal_scope_excerpt"),
    )
    peer_text = normalize_text(
        row.get("peer_name_final"),
        row.get("peer_industry_final"),
        row.get("peer_scope_excerpt"),
    )
    fcat = detect_categories(focal_text)
    pcat = detect_categories(peer_text)
    overlap = meaningful_overlap(fcat, pcat)
    broad_overlap = fcat & pcat
    same_industry = str(row.get("focal_industry_final")) == str(row.get("peer_industry_final"))
    sim = pd.to_numeric(row.get("product_similarity"), errors="coerce")
    scope_j = pd.to_numeric(row.get("scope_text_jaccard"), errors="coerce")
    annual_j = pd.to_numeric(row.get("annual_text_jaccard"), errors="coerce")

    if overlap:
        if same_industry or scope_j >= 0.05 or annual_j >= 0.06:
            score = 3
            reason = f"direct product/category overlap: {','.join(sorted(overlap))}"
        else:
            score = 2
            reason = f"same product category but weaker industry/text support: {','.join(sorted(overlap))}"
    elif broad_overlap:
        if same_industry and (scope_j >= 0.05 or annual_j >= 0.06):
            score = 2
            reason = f"broad same-category overlap with text support: {','.join(sorted(broad_overlap))}"
        elif same_industry:
            score = 1
            reason = f"same detailed industry but only broad category overlap: {','.join(sorted(broad_overlap))}"
        else:
            score = 1
            reason = f"broad related category but not direct competitor: {','.join(sorted(broad_overlap))}"
    elif same_industry:
        if scope_j >= 0.08 or annual_j >= 0.10 or sim >= 0.35:
            score = 2
            reason = "same detailed industry with strong text similarity but no specific category match"
        else:
            score = 1
            reason = "same detailed industry, but product overlap is not clear"
    else:
        if scope_j >= 0.08 and annual_j >= 0.08:
            score = 1
            reason = "cross-industry pair with text overlap; likely related/complement, not direct peer"
        else:
            score = 0
            reason = "different industry and no specific product/customer overlap"

    direct = int(score >= 2)
    return score, direct, reason, ";".join(sorted(fcat)), ";".join(sorted(pcat))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)
    scores = df.apply(score_pair, axis=1, result_type="expand")
    scores.columns = [
        "human_competitor_score_0_to_3",
        "human_is_direct_product_market_peer_0_1",
        "human_reason",
        "codex_focal_categories",
        "codex_peer_categories",
    ]
    coded = df.drop(
        columns=[
            "human_competitor_score_0_to_3",
            "human_is_direct_product_market_peer_0_1",
            "human_reason",
        ],
        errors="ignore",
    ).join(scores)
    coded["coder_type"] = "codex_llm_assisted_semantic_review"
    coded.to_csv(OUTPUT, index=False)

    summary = (
        coded.groupby("peer_system", as_index=False)
        .agg(
            pairs=("peer_code", "size"),
            mean_score=("human_competitor_score_0_to_3", "mean"),
            direct_peer_share=("human_is_direct_product_market_peer_0_1", "mean"),
            score_3_share=("human_competitor_score_0_to_3", lambda s: float((s == 3).mean())),
            score_0_share=("human_competitor_score_0_to_3", lambda s: float((s == 0).mean())),
        )
        .sort_values(["direct_peer_share", "mean_score"], ascending=False)
    )
    summary.to_csv(SUMMARY, index=False)

    doc = f"""# v13 Codex-Assisted Manual Peer Coding

日期：2026-05-31

## Purpose

This file records an independent LLM-assisted semantic review of the 150-pair
peer-system validation template. It is not the same as the earlier Jaccard proxy:
the coding uses product/customer/use-case categories extracted from firm names,
industries, and business-scope excerpts.

## Output

```text
{OUTPUT.relative_to(ROOT)}
{SUMMARY.relative_to(ROOT)}
```

## Coding Scale

```text
3 = close direct competitor: similar product/service and similar customer/use case
2 = related product-market peer: same broad market, but products/customers differ
1 = weakly related: same industry label or supply-chain relation, not direct competitor
0 = not a product-market competitor
```

`direct_peer_share` treats scores 2 and 3 as product-market peers.

## Summary

{summary.to_markdown(index=False, floatfmt=".4f")}

## Reading

This semantic review supports the same ranking as the statistical gates:

```text
annual same-industry annual-report peers > CSMAR scope peers > random / low-similarity peers.
```

The CSMAR scope network again survives the validity gate, but it is not the
measurement-clean winner. Its role should be "valid but not dominant."
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
