#!/usr/bin/env python3
"""Build event-level GenAI disclosure concreteness measures.

The measure is intentionally textual. It captures observable disclosure
concreteness available to investors at the event date, not real GenAI capability,
investment, or commercialization success.

Literature anchor:
1. Hope, Hu, and Lu (2016): specificity as density of concrete/verifiable
   details in qualitative disclosure.
2. Cheng, De Franco, Jiang, and Lin (2019): technology-mania disclosures should
   distinguish generic/speculative talk from existing/substantive activity.
"""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

try:
    import jieba  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    jieba = None


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    ROOT
    / "results"
    / "csmar_v5_1_response_smoke_20260523"
    / "csmar_conservative_focal_events_2023_2026.csv"
)
DEFAULT_OUT_PARENT = ROOT / "results"

GENERIC_AI_CONTEXT_TERMS = [
    "大模型",
    "大语言模型",
    "生成式",
    "AIGC",
    "GPT",
    "ChatGPT",
    "DeepSeek",
    "LLM",
    "多模态",
    "智能体",
    "Agent",
    "AI助手",
    "AI客服",
    "AI编程",
    "模型",
    "应用",
    "部署",
    "上线",
    "接入",
    "发布",
    "推出",
    "训练",
    "推理",
    "RAG",
    "知识库",
]

GENAI_KEYWORDS = [
    "生成式人工智能",
    "生成式AI",
    "生成式 AI",
    "人工智能生成内容",
    "AI生成",
    "AIGC",
    "大模型",
    "AI大模型",
    "人工智能大模型",
    "大语言模型",
    "语言大模型",
    "LLM",
    "ChatGPT",
    "GPT",
    "DeepSeek",
    "Kimi",
    "通义千问",
    "通义",
    "文心一言",
    "文心",
    "盘古",
    "混元",
    "智谱",
    "ChatGLM",
    "百川",
    "讯飞星火",
    "星火",
    "豆包",
    "商汤日日新",
    "日日新",
    "MiniMax",
    "月之暗面",
    "多模态",
    "智能体",
    "Agent",
    "AI助手",
    "AI客服",
    "AI编程",
    "AI应用",
    "AI Agent",
    "RAG",
    "检索增强",
    "MaaS",
    "Sora",
]

GENAI_STRONG_PAT = re.compile(
    "|".join(re.escape(x) for x in sorted(GENAI_KEYWORDS, key=len, reverse=True)),
    flags=re.I,
)
GENERIC_AI_PAT = re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])|人工智能", flags=re.I)
GENERIC_AI_CONTEXT_PAT = re.compile(
    "|".join(re.escape(x) for x in sorted(GENERIC_AI_CONTEXT_TERMS, key=len, reverse=True)),
    flags=re.I,
)
POSITIVE_GENAI_CONTEXT_PAT = re.compile(
    "|".join(
        re.escape(x)
        for x in sorted(
            [
                "生成内容",
                "自然语言处理",
                "智能客服",
                "AI客服",
                "AI助手",
                "AI编程",
                "智能体",
                "多模态",
                "检索增强",
                "知识库",
                "RAG",
                "MaaS",
                "大语言",
                "大参数",
                "对话机器人",
                "chatbot",
            ],
            key=len,
            reverse=True,
        )
    ),
    flags=re.I,
)

MODEL_OR_PARTNER_TERMS = [
    "ChatGPT",
    "GPT-4",
    "GPT4",
    "DeepSeek",
    "Kimi",
    "通义千问",
    "通义",
    "文心一言",
    "文心",
    "盘古",
    "混元",
    "智谱",
    "ChatGLM",
    "百川",
    "讯飞星火",
    "星火",
    "豆包",
    "商汤日日新",
    "日日新",
    "MiniMax",
    "月之暗面",
    "OpenAI",
    "Microsoft",
    "微软",
    "华为",
    "百度",
    "阿里",
    "腾讯",
    "字节",
    "科大讯飞",
    "商汤",
    "英伟达",
    "NVIDIA",
    "LLaMA",
    "Gemini",
    "Claude",
]

GENERIC_ENTITY_STOP = {
    "人工智能",
    "大模型",
    "数字化",
    "智能化",
    "平台",
    "系统",
    "产品",
    "客户",
    "生态",
    "技术",
    "业务",
    "应用",
    "服务",
    "解决方案",
    "软件",
    "模型",
    "行业",
    "公司",
}

NON_ENTITY_PHRASE_PAT = re.compile(
    r"(?:积极|拥抱|探索|未来|持续|赋能|发展|技术|布局|关注|研究|推动|推进|提升|助力|致力)"
)

NEGATION_TERMS = [
    "未",
    "暂无",
    "没有",
    "无",
    "尚未",
    "不涉及",
    "未涉及",
    "未应用",
    "暂未应用",
    "未布局",
    "未接入",
    "未使用",
    "不包含",
    "无相关",
]

DENIAL_PAT = re.compile(
    r"(?:"
    r"(?:暂无|没有|尚未|暂未|不涉及|未涉及|未应用|暂不直接涉及|未布局|未接入|未使用|无相关|无|未与|未给|未带来)"
    r"[^。！？；;]{0,36}"
    r"(?:ChatGPT|AIGC|GPT|DeepSeek|Kimi|通义|文心|盘古|混元|智谱|豆包|星火|大模型|生成式|人工智能|AI|LLM|OpenAI)"
    r"|"
    r"(?:ChatGPT|AIGC|GPT|DeepSeek|Kimi|通义|文心|盘古|混元|智谱|豆包|星火|大模型|生成式|人工智能|AI|LLM|OpenAI)"
    r"[^。！？；;]{0,50}"
    r"(?:暂无|没有|尚未|暂未|不涉及|未涉及|未应用|未布局|未接入|未使用|无相关|无|未给|未带来|暂时没有)"
    r")",
    flags=re.I,
)

ENTITY_PATTERNS = [
    re.compile(r"[《“\"]([^《》“”\"']{2,40})[》”\"]"),
    re.compile(
        r"[\u4e00-\u9fffA-Za-z0-9]{2,35}(?:大模型|模型平台|应用平台|平台|系统|软件|应用|"
        r"助手|机器人|智能体|模块|知识库|解决方案|SaaS|API|云服务)"
    ),
    re.compile(r"[\u4e00-\u9fffA-Za-z0-9]{2,35}(?:公司|集团|大学|研究院|实验室|中心|银行|医院|客户)"),
]

OPERATION_TERMS = [
    "发布",
    "推出",
    "上线",
    "接入",
    "部署",
    "落地",
    "试点",
    "内测",
    "公测",
    "应用于",
    "用于",
    "覆盖",
    "服务于",
    "集成",
    "训练",
    "微调",
    "推理",
    "备案",
    "通过备案",
    "商业化",
    "订单",
    "合同",
    "收费",
    "订阅",
    "API调用",
    "私有化部署",
]

SCENARIO_TERMS = [
    "智能客服",
    "代码生成",
    "办公助手",
    "内容生成",
    "营销文案",
    "风控",
    "投研",
    "医疗影像",
    "工业质检",
    "供应链排产",
    "知识库",
    "检索增强",
    "RAG",
    "客服机器人",
    "多轮问答",
    "金融客服",
    "智能座舱",
    "辅助诊断",
    "教育",
    "医疗",
    "工业",
    "政务",
    "金融",
]

COMMERCIAL_TERMS = [
    "商业化",
    "客户",
    "B端",
    "C端",
    "SaaS",
    "订阅",
    "订单",
    "合同",
    "收入",
    "收费",
    "API",
    "私有化",
    "交付",
    "上线试点",
]

INFRA_TERMS = [
    "算力",
    "GPU",
    "服务器",
    "芯片",
    "半导体",
    "数据中心",
    "IDC",
    "液冷",
    "光模块",
    "交换机",
    "存储",
    "云计算",
    "生态",
    "供应链",
    "训练集群",
    "推理集群",
    "智算中心",
    "电力",
    "冷却",
]

FUTURE_TERMS = ["未来", "将", "计划", "拟", "持续探索", "积极探索", "有望", "正在研究", "关注", "布局"]
GENERIC_TALK_TERMS = ["积极拥抱", "赋能", "前沿技术", "技术趋势", "保持关注", "持续关注", "探索AI", "探索人工智能"]
GOVERNANCE_TERMS = ["董事", "高管", "人员", "团队", "人才", "专家", "委员会", "实验室", "研究院", "首席"]
INVEST_PARTNER_TERMS = ["投资", "子公司", "参股", "控股", "收购", "合资", "合作", "战略合作", "签署", "共建"]
INDUSTRY_TREND_TERMS = ["行业趋势", "产业趋势", "技术发展趋势", "市场需求", "产业机会", "技术浪潮", "新赛道"]

QUANT_PATTERNS = [
    re.compile(r"(?:20[2-9]\d年\d{0,2}月?\d{0,2}日?|20[2-9]\d[-/]\d{1,2}(?:[-/]\d{1,2})?|[一二三四1234]季度|Q[1-4])", re.I),
    re.compile(r"\d+(?:\.\d+)?\s*(?:亿元|万元|元|人民币|美元|万美元|亿美元)"),
    re.compile(r"\d+(?:\.\d+)?\s*%"),
    re.compile(r"(?:超过|约|近|达到|不少于|不低于)?\s*\d+(?:\.\d+)?\s*(?:家客户|个客户|万用户|亿用户|名用户|个项目|项项目|个合同|项合同|个应用|款产品|套系统|个模型|亿参数|B参数|张GPU|块GPU|P算力|PFlops|PFLOPS|次调用|万次调用|亿次调用|QPS|token|tokens|人团队|名工程师)", re.I),
    re.compile(r"(?:同比|环比|增长|提升|下降|降低)\s*\d+(?:\.\d+)?\s*%"),
]


def clean_text(value: object) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def code6(value: object) -> str:
    text = re.sub(r"\.0$", "", clean_text(value))
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def split_sentences(text: object) -> list[str]:
    s = clean_text(text)
    if not s:
        return []
    parts = re.split(r"(?<=[。！？；;.!?])\s*", s)
    out: list[str] = []
    for p in parts:
        p = clean_text(p)
        if len(p) >= 4:
            out.append(p)
    return out


def sentence_has_genai_context(sentence: str) -> bool:
    if GENAI_STRONG_PAT.search(sentence):
        return True
    if GENERIC_AI_PAT.search(sentence) and GENERIC_AI_CONTEXT_PAT.search(sentence):
        return True
    return False


def extract_genai_sentences(text: object) -> list[str]:
    return [s for s in split_sentences(text) if sentence_has_genai_context(s)]


def count_ai_keywords(text: str) -> int:
    return len(GENAI_STRONG_PAT.findall(text))


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    if jieba is not None:
        return [t.strip() for t in jieba.lcut(text) if t.strip()]
    return re.findall(r"[\u4e00-\u9fff]|[A-Za-z]+(?:[-_][A-Za-z]+)*|\d+(?:\.\d+)?", text)


def unique_filtered(matches: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in matches:
        x = clean_text(item).strip("，,。.;；:：、（）()[]【】")
        if len(x) < 2:
            continue
        if x in GENERIC_ENTITY_STOP:
            continue
        if x.startswith(("公司", "本公司", "该公司")) and NON_ENTITY_PHRASE_PAT.search(x):
            continue
        if NON_ENTITY_PHRASE_PAT.search(x) and not has_any(x, MODEL_OR_PARTNER_TERMS):
            continue
        if re.fullmatch(r"(?:人工智能|AI|大模型|生成式|AIGC|平台|系统|产品|客户|生态|技术|应用|模型)+", x, re.I):
            continue
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def entity_concrete_terms(text: str) -> list[str]:
    matches: list[str] = []
    for term in MODEL_OR_PARTNER_TERMS:
        if re.search(re.escape(term), text, flags=re.I):
            matches.append(term)
    for pat in ENTITY_PATTERNS:
        matches.extend(m.group(1) if m.lastindex else m.group(0) for m in pat.finditer(text))
    return unique_filtered(matches)


def is_negated_position(text: str, start: int) -> bool:
    window = text[max(0, start - 8) : start + 2]
    return any(term in window for term in NEGATION_TERMS)


def count_terms(text: str, terms: Iterable[str], skip_negated: bool = False) -> int:
    total = 0
    for term in terms:
        for match in re.finditer(re.escape(term), text, flags=re.I):
            if skip_negated and is_negated_position(text, match.start()):
                continue
            total += 1
    return int(total)


def operational_concrete_count(text: str) -> int:
    return (
        count_terms(text, OPERATION_TERMS, skip_negated=True)
        + count_terms(text, SCENARIO_TERMS)
        + count_terms(text, COMMERCIAL_TERMS)
    )


def quant_concrete_count(text: str) -> int:
    return int(sum(len(p.findall(text)) for p in QUANT_PATTERNS))


def has_any(text: str, terms: Iterable[str]) -> bool:
    return any(re.search(re.escape(term), text, flags=re.I) for term in terms)


def has_denial_or_no_exposure(text: str) -> bool:
    return bool(DENIAL_PAT.search(text))


def has_positive_existing_signal(text: str) -> bool:
    for term in OPERATION_TERMS + COMMERCIAL_TERMS:
        for match in re.finditer(re.escape(term), text, flags=re.I):
            if not is_negated_position(text, match.start()):
                return True
    return bool(has_any(text, ["已完成", "已形成", "已具备", "自研", "客户", "订单", "合同", "收入", "商业化"]))


def remove_denial_fragments(text: str) -> str:
    return DENIAL_PAT.sub(" ", text)


def has_positive_genai_claim(text: str) -> bool:
    """Return true only when the firm appears to describe its own GenAI-related action/content.

    This guards against treating "未涉及 ChatGPT" or third-party descriptions of
    ChatGPT as high-concreteness focal-firm GenAI disclosures.
    """
    positive_text = remove_denial_fragments(text)
    if not positive_text.strip():
        return False
    has_genai_term = bool(GENAI_STRONG_PAT.search(positive_text) or POSITIVE_GENAI_CONTEXT_PAT.search(positive_text))
    if not has_genai_term:
        return False
    firm_context = has_any(
        positive_text,
        ["公司", "本公司", "子公司", "控股", "参股", "我们", "产品", "平台", "系统", "应用", "业务", "服务", "客户", "项目", "解决方案", "自研"],
    )
    firm_action = has_positive_existing_signal(positive_text) or has_any(
        positive_text,
        ["具备", "拥有", "开发", "研发", "训练", "微调", "推理", "能力", "场景", "模块", "功能"],
    )
    return bool(firm_context and firm_action)


def classify_content(
    text: str,
    entity_count: int,
    operational_count: int,
    quant_count: int,
    denial_or_no_exposure: int = 0,
    positive_genai_claim: int = 1,
) -> dict[str, object]:
    product_service = int(
        entity_count > 0
        or has_any(text, ["产品名称", "服务名称", "应用平台", "模型平台", "AI助手", "智能体", "客服机器人"])
        or (
            has_any(text, ["产品", "服务", "平台", "系统", "应用", "模型", "助手", "机器人"])
            and operational_count >= 2
        )
    )
    deployment_commercialization = int(operational_count > 0 and has_positive_existing_signal(text))
    customer_exposure = int(has_any(text, ["客户", "银行", "医院", "学校", "政府", "B端", "C端", "行业客户", "用户"]))
    infrastructure_ecosystem = int(has_any(text, INFRA_TERMS))
    investment_subsidiary_partner = int(has_any(text, INVEST_PARTNER_TERMS))
    governance_personnel = int(has_any(text, GOVERNANCE_TERMS))
    future_plan = int(has_any(text, FUTURE_TERMS))
    industry_trend_only = int(has_any(text, INDUSTRY_TREND_TERMS) and not (product_service or deployment_commercialization))
    generic_ai_talk = int(
        (has_any(text, GENERIC_TALK_TERMS) or count_ai_keywords(text) > 0)
        and entity_count == 0
        and operational_count <= 1
        and quant_count == 0
    )

    substantive_or_existing = int(
        positive_genai_claim
        and not denial_or_no_exposure
        and bool(product_service or deployment_commercialization or customer_exposure)
        and (entity_count + operational_count + quant_count > 0)
    )
    speculative_or_generic = int(
        bool((not positive_genai_claim) or denial_or_no_exposure or generic_ai_talk or future_plan or governance_personnel or industry_trend_only)
        and not bool(deployment_commercialization or customer_exposure or quant_count >= 2)
    )
    competitive_risk = int(
        positive_genai_claim
        and not denial_or_no_exposure
        and
        bool(product_service or deployment_commercialization or customer_exposure)
        and bool(entity_count > 0 or operational_count >= 2 or customer_exposure or quant_count >= 1)
        and not (infrastructure_ecosystem and not (deployment_commercialization or customer_exposure))
    )
    category_validation = int(bool(infrastructure_ecosystem) and not bool(deployment_commercialization and customer_exposure))

    # Priority rule: mutually-exclusive label only for table readability.
    # Binary flags above remain non-exclusive.
    if competitive_risk:
        primary = "competitive_risk_content"
    elif category_validation:
        primary = "category_validation_content"
    elif substantive_or_existing:
        primary = "substantive_or_existing_content"
    elif speculative_or_generic:
        primary = "speculative_or_generic_content"
    else:
        primary = "uncategorized_or_low_signal"

    return {
        "generic_ai_talk": generic_ai_talk,
        "future_plan": future_plan,
        "governance_personnel": governance_personnel,
        "product_service": product_service,
        "deployment_commercialization": deployment_commercialization,
        "customer_exposure": customer_exposure,
        "infrastructure_ecosystem": infrastructure_ecosystem,
        "investment_subsidiary_partner": investment_subsidiary_partner,
        "industry_trend_only": industry_trend_only,
        "denial_or_no_exposure_content": int(denial_or_no_exposure),
        "positive_genai_claim_content": int(positive_genai_claim),
        "competitive_risk_content": competitive_risk,
        "category_validation_content": category_validation,
        "speculative_or_generic_content": speculative_or_generic,
        "substantive_or_existing_content": substantive_or_existing,
        "content_category_primary": primary,
    }


def zscore(series: pd.Series) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    std = x.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.zeros(len(x)), index=series.index)
    return (x - x.mean()) / std


def residualized_z(df: pd.DataFrame) -> pd.Series:
    y = pd.to_numeric(df["genai_concreteness_raw"], errors="coerce").fillna(0.0).to_numpy(float)
    x_base = pd.DataFrame(
        {
            "const": 1.0,
            "log_token_count": np.log1p(pd.to_numeric(df["genai_token_count"], errors="coerce").fillna(0.0)),
            "log_char_count": np.log1p(pd.to_numeric(df["genai_char_count"], errors="coerce").fillna(0.0)),
            "ai_keyword_count": pd.to_numeric(df["ai_keyword_count"], errors="coerce").fillna(0.0),
            "genai_sentence_count": pd.to_numeric(df["genai_sentence_count"], errors="coerce").fillna(0.0),
        }
    )
    ym = pd.to_datetime(df["event_date"], errors="coerce").dt.to_period("M").astype(str).fillna("missing")
    dummies = pd.get_dummies(ym, prefix="ym", drop_first=True, dtype=float)
    xmat = pd.concat([x_base, dummies], axis=1).to_numpy(float)
    try:
        beta, *_ = np.linalg.lstsq(xmat, y, rcond=None)
        resid = y - xmat @ beta
    except np.linalg.LinAlgError:
        resid = y - np.nanmean(y)
    return zscore(pd.Series(resid, index=df.index))


def infer_column(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise ValueError(f"Cannot infer required column from candidates: {candidates}. Available: {list(df.columns)}")
    return None


def infer_text_column(df: pd.DataFrame) -> str:
    candidates = ["sample_answer", "answer_text", "ReplyContent", "Answer", "event_text", "genai_span"]
    scores: list[tuple[int, str]] = []
    for c in candidates:
        if c in df.columns:
            nonempty = df[c].map(clean_text).ne("").sum()
            scores.append((int(nonempty), c))
    if not scores:
        raise ValueError(f"Cannot infer disclosure text column. Available: {list(df.columns)}")
    scores.sort(reverse=True)
    return scores[0][1]


def build_measures(input_path: Path, sample: int | None = None) -> tuple[pd.DataFrame, dict[str, object]]:
    df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if sample is not None and sample > 0:
        df = df.head(sample).copy()

    event_col = infer_column(df, ["event_id"], required=False)
    focal_col = infer_column(df, ["focal_code", "stock_code", "Symbol"], required=True)
    date_col = infer_column(df, ["event_date", "event_date_str", "ReplyDate", "ReportDate", "DeclareDate"], required=True)
    text_col = infer_text_column(df)
    question_col = infer_column(df, ["sample_question", "question_text", "QuestionContent", "Question"], required=False)

    rows: list[dict[str, object]] = []
    for idx, row in df.iterrows():
        event_date = pd.to_datetime(row.get(date_col, ""), errors="coerce")
        event_id = clean_text(row.get(event_col, "")) if event_col else ""
        focal_code = code6(row.get(focal_col, ""))
        if not event_id:
            datestr = event_date.strftime("%Y%m%d") if pd.notna(event_date) else f"row{idx:06d}"
            event_id = f"GENAI_{focal_code}_{datestr}_{idx:06d}"

        raw_text = clean_text(row.get(text_col, ""))
        genai_sentences = extract_genai_sentences(raw_text)
        genai_text = " ".join(genai_sentences)
        counted_sentences = [s for s in genai_sentences if has_positive_genai_claim(s)]
        counted_genai_text = " ".join(counted_sentences)
        tokens = tokenize(counted_genai_text)
        token_count = len(tokens)
        char_count = len(re.sub(r"\s+", "", counted_genai_text))
        ai_keyword_count = count_ai_keywords(genai_text)
        entity_terms = entity_concrete_terms(counted_genai_text)
        entity_count = len(entity_terms)
        operational_count = operational_concrete_count(counted_genai_text)
        quant_count = quant_concrete_count(counted_genai_text)
        positive_genai_claim = int(bool(counted_sentences))
        denial_or_no_exposure = int(has_denial_or_no_exposure(genai_text) and not positive_genai_claim)
        if denial_or_no_exposure or not positive_genai_claim:
            entity_terms = []
            entity_count = 0
            operational_count = 0
            quant_count = 0
        total_count = entity_count + operational_count + quant_count
        classifications = classify_content(
            genai_text,
            entity_count,
            operational_count,
            quant_count,
            denial_or_no_exposure=denial_or_no_exposure,
            positive_genai_claim=positive_genai_claim,
        )

        rows.append(
            {
                "event_id": event_id,
                "focal_code": focal_code,
                "event_date": event_date.strftime("%Y-%m-%d") if pd.notna(event_date) else "",
                "genai_text": genai_text,
                "counted_genai_text": counted_genai_text,
                "raw_text_excerpt": raw_text[:1000],
                "sample_question": clean_text(row.get(question_col, "")) if question_col else "",
                "source_text_column": text_col,
                "genai_sentence_count": len(genai_sentences),
                "positive_genai_sentence_count": len(counted_sentences),
                "genai_token_count": token_count,
                "genai_char_count": char_count,
                "ai_keyword_count": ai_keyword_count,
                "entity_concrete_count": entity_count,
                "operational_concrete_count": operational_count,
                "quant_concrete_count": quant_count,
                "total_concrete_count": total_count,
                "entity_terms": ";".join(entity_terms),
                "entity_concrete_density": entity_count / max(token_count, 1),
                "operational_concrete_density": operational_count / max(token_count, 1),
                "quant_concrete_density": quant_count / max(token_count, 1),
                "genai_concreteness_raw": total_count / max(token_count, 1),
                "genai_concreteness_char_density": total_count / max(char_count, 1),
                **classifications,
            }
        )

    out = pd.DataFrame(rows)
    out["event_year"] = pd.to_datetime(out["event_date"], errors="coerce").dt.year
    out["event_year_month"] = pd.to_datetime(out["event_date"], errors="coerce").dt.to_period("M").astype(str)
    out["genai_concreteness_z"] = zscore(out["genai_concreteness_raw"])
    out["genai_concreteness_z_by_year"] = out.groupby("event_year", dropna=False)["genai_concreteness_raw"].transform(zscore)
    out["genai_concreteness_resid_z"] = residualized_z(out)

    required_order = [
        "event_id",
        "focal_code",
        "event_date",
        "genai_text",
        "counted_genai_text",
        "genai_sentence_count",
        "positive_genai_sentence_count",
        "genai_token_count",
        "genai_char_count",
        "ai_keyword_count",
        "entity_concrete_count",
        "operational_concrete_count",
        "quant_concrete_count",
        "total_concrete_count",
        "entity_concrete_density",
        "operational_concrete_density",
        "quant_concrete_density",
        "genai_concreteness_raw",
        "genai_concreteness_char_density",
        "genai_concreteness_z",
        "genai_concreteness_z_by_year",
        "genai_concreteness_resid_z",
        "competitive_risk_content",
        "category_validation_content",
        "speculative_or_generic_content",
        "substantive_or_existing_content",
        "content_category_primary",
    ]
    rest = [c for c in out.columns if c not in required_order]
    out = out[required_order + rest]

    meta = {
        "input_path": str(input_path),
        "rows_read": len(df),
        "events_processed": int(out["event_id"].nunique()),
        "missing_source_text_count": int(df[text_col].map(clean_text).eq("").sum()),
        "source_text_column": text_col,
        "event_col": event_col or "<constructed>",
        "focal_col": focal_col,
        "date_col": date_col,
        "question_col": question_col or "",
    }
    return out, meta


def summary_stats(out: pd.DataFrame, meta: dict[str, object]) -> pd.DataFrame:
    rows: list[dict[str, object]] = [
        {"metric": "input_path", "value": meta["input_path"]},
        {"metric": "events_processed", "value": meta["events_processed"]},
        {"metric": "missing_source_text_count", "value": meta["missing_source_text_count"]},
        {"metric": "source_text_column", "value": meta["source_text_column"]},
    ]
    for col in [
        "genai_sentence_count",
        "positive_genai_sentence_count",
        "genai_token_count",
        "genai_char_count",
        "ai_keyword_count",
        "entity_concrete_count",
        "operational_concrete_count",
        "quant_concrete_count",
        "total_concrete_count",
        "genai_concreteness_raw",
        "genai_concreteness_char_density",
        "genai_concreteness_z",
        "genai_concreteness_resid_z",
    ]:
        x = pd.to_numeric(out[col], errors="coerce")
        rows.extend(
            [
                {"metric": f"{col}_mean", "value": x.mean()},
                {"metric": f"{col}_sd", "value": x.std(ddof=0)},
                {"metric": f"{col}_p05", "value": x.quantile(0.05)},
                {"metric": f"{col}_p50", "value": x.quantile(0.50)},
                {"metric": f"{col}_p95", "value": x.quantile(0.95)},
            ]
        )
    for col in [
        "competitive_risk_content",
        "category_validation_content",
        "speculative_or_generic_content",
        "substantive_or_existing_content",
        "positive_genai_claim_content",
        "denial_or_no_exposure_content",
        "generic_ai_talk",
        "future_plan",
        "product_service",
        "deployment_commercialization",
        "customer_exposure",
        "infrastructure_ecosystem",
    ]:
        rows.append({"metric": f"{col}_share", "value": pd.to_numeric(out[col], errors="coerce").mean()})
    return pd.DataFrame(rows)


def correlation_table(out: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "genai_concreteness_raw",
        "genai_concreteness_z",
        "genai_concreteness_resid_z",
        "genai_token_count",
        "genai_char_count",
        "ai_keyword_count",
        "genai_sentence_count",
        "positive_genai_sentence_count",
        "entity_concrete_count",
        "operational_concrete_count",
        "quant_concrete_count",
    ]
    records: list[dict[str, object]] = []
    for x in ["genai_concreteness_raw", "genai_concreteness_z", "genai_concreteness_resid_z"]:
        for y in cols:
            if x == y:
                continue
            sx = pd.to_numeric(out[x], errors="coerce")
            sy = pd.to_numeric(out[y], errors="coerce")
            ok = sx.notna() & sy.notna()
            records.append(
                {
                    "x": x,
                    "y": y,
                    "pearson": sx[ok].corr(sy[ok], method="pearson") if ok.sum() >= 3 else np.nan,
                    "spearman": sx[ok].corr(sy[ok], method="spearman") if ok.sum() >= 3 else np.nan,
                    "n": int(ok.sum()),
                }
            )
    return pd.DataFrame(records)


def write_examples(out: pd.DataFrame, path: Path, n_each: int = 20) -> None:
    cols = [
        "event_id",
        "focal_code",
        "event_date",
        "genai_concreteness_raw",
        "genai_concreteness_resid_z",
        "entity_concrete_count",
        "operational_concrete_count",
        "quant_concrete_count",
        "content_category_primary",
        "raw_text_excerpt",
        "genai_text",
        "counted_genai_text",
    ]
    high = out.sort_values(["genai_concreteness_raw", "total_concrete_count"], ascending=False).head(n_each).copy()
    low = out.sort_values(["genai_concreteness_raw", "total_concrete_count"], ascending=True).head(n_each).copy()
    lines = ["# Top / Bottom GenAI Disclosure Concreteness Examples", ""]
    for title, data in [("High Concreteness", high), ("Low Concreteness", low)]:
        lines.extend([f"## {title}", ""])
        for _, row in data.iterrows():
            lines.extend(
                [
                    f"### {row['event_id']} | {row['focal_code']} | {row['event_date']}",
                    "",
                    "```text",
                    f"raw={row['genai_concreteness_raw']:.6f}, resid_z={row['genai_concreteness_resid_z']:.3f}, "
                    f"entity={row['entity_concrete_count']}, operational={row['operational_concrete_count']}, "
                    f"quant={row['quant_concrete_count']}, category={row['content_category_primary']}",
                    "```",
                    "",
                    "Raw excerpt:",
                    "",
                    "```text",
                    clean_text(row.get("raw_text_excerpt", ""))[:700],
                    "```",
                    "",
                    "Extracted GenAI sentences:",
                    "",
                    "```text",
                    clean_text(row.get("genai_text", ""))[:1000],
                    "```",
                    "",
                    "Counted positive GenAI sentences:",
                    "",
                    "```text",
                    clean_text(row.get("counted_genai_text", ""))[:1000],
                    "```",
                    "",
                ]
            )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_manual_validation_sample(out: pd.DataFrame, per_quintile: int = 30) -> pd.DataFrame:
    d = out.copy()
    d["concreteness_quintile"] = pd.qcut(
        d["genai_concreteness_raw"].rank(method="first"),
        5,
        labels=["Q1_low", "Q2", "Q3", "Q4", "Q5_high"],
    )
    chunks = []
    for _, sub in d.groupby("concreteness_quintile", observed=False):
        chunks.append(sub.sample(n=min(per_quintile, len(sub)), random_state=20260528))
    sample = pd.concat(chunks, ignore_index=True) if chunks else d.head(0).copy()
    keep = [
        "event_id",
        "focal_code",
        "event_date",
        "concreteness_quintile",
        "genai_concreteness_raw",
        "genai_concreteness_resid_z",
        "content_category_primary",
        "raw_text_excerpt",
        "genai_text",
        "counted_genai_text",
    ]
    sample = sample[keep].copy()
    sample["human_concreteness_score_1_to_5"] = ""
    sample["human_speculative_or_substantive"] = ""
    sample["human_competitive_or_category_validation"] = ""
    sample["coder_notes"] = ""
    return sample.sort_values(["concreteness_quintile", "event_id"])


def write_validation_instructions(path: Path) -> None:
    path.write_text(
        """# Manual Validation Instructions for GenAI_Disclosure_Concreteness

Score the extracted GenAI disclosure text, not the investor question alone.

`human_concreteness_score_1_to_5`:

1. Generic or boilerplate AI talk. The wording could apply to many firms.
2. Mentions GenAI/AIGC/large models but gives few firm-specific details.
3. Gives one concrete detail, such as a product, scenario, partner, or timeline.
4. Gives multiple firm-specific and verifiable details.
5. Gives highly concrete, firm-specific, verifiable details such as named product/model, deployment/customer/scenario, dates, numbers, or commercialization information.

`human_speculative_or_substantive`:

- `speculative`: future plan, general attention, personnel/governance, or trend-only discussion without concrete operating detail.
- `substantive`: existing product/service, deployment, customer exposure, commercialization, or current project detail.

`human_competitive_or_category_validation`:

- `competitive`: own product/service/application/deployment/customer details that could imply product-market competitive risk.
- `category_validation`: AI infrastructure, chips, servers, data centers, compute, supply-chain demand, ecosystem demand, or broad AI-industry validation.
- `both` or `neither` are allowed if needed.
""",
        encoding="utf-8",
    )


def write_log(path: Path, meta: dict[str, object], out: pd.DataFrame) -> None:
    missing_genai_sent = int(out["genai_sentence_count"].eq(0).sum())
    lines = [
        "GenAI Disclosure Concreteness Measurement Log",
        f"date={date.today().isoformat()}",
        f"input_path={meta['input_path']}",
        f"rows_read={meta['rows_read']}",
        f"events_processed={meta['events_processed']}",
        f"source_text_column={meta['source_text_column']}",
        f"event_col={meta['event_col']}",
        f"focal_col={meta['focal_col']}",
        f"date_col={meta['date_col']}",
        f"question_col={meta['question_col']}",
        f"missing_source_text_count={meta['missing_source_text_count']}",
        f"missing_genai_sentence_count={missing_genai_sent}",
        "",
        "Warnings:",
    ]
    if missing_genai_sent:
        lines.append(f"- {missing_genai_sent} events have no extracted GenAI sentence after strict sentence filtering.")
    lines.append("- This measure is textual concreteness only, not real GenAI capability.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(args: argparse.Namespace) -> Path:
    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUT_PARENT / f"genai_concreteness_measure_{date.today():%Y%m%d}"
    out_dir = out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    out, meta = build_measures(input_path, sample=args.sample)
    out.to_csv(out_dir / "event_genai_concreteness.csv", index=False, encoding="utf-8-sig")
    summary_stats(out, meta).to_csv(out_dir / "summary_stats.csv", index=False, encoding="utf-8-sig")
    correlation_table(out).to_csv(out_dir / "correlation_with_text_controls.csv", index=False, encoding="utf-8-sig")
    write_examples(out, out_dir / "top_bottom_examples.md", n_each=20)
    build_manual_validation_sample(out, per_quintile=args.validation_per_quintile).to_csv(
        out_dir / "manual_validation_sample.csv", index=False, encoding="utf-8-sig"
    )
    write_validation_instructions(out_dir / "manual_validation_instructions.md")
    write_log(out_dir / "measurement_log.txt", meta, out)

    print(f"input={input_path}")
    print(f"events_processed={meta['events_processed']}")
    print(f"missing_source_text_count={meta['missing_source_text_count']}")
    print(f"output_dir={out_dir}")
    return out_dir


def smoke_test() -> None:
    examples = pd.DataFrame(
        [
            {
                "event_id": "SMOKE_LOW",
                "focal_code": "000001",
                "event_date": "2024-05-01",
                "sample_answer": "公司积极拥抱人工智能和大模型技术，未来将持续探索AI赋能业务发展。",
            },
            {
                "event_id": "SMOKE_HIGH",
                "focal_code": "000002",
                "event_date": "2024-05-02",
                "sample_answer": "公司于2024年5月发布面向金融客服场景的XX大模型应用平台，已在12家银行客户上线试点，支持知识库检索增强和多轮问答，并计划通过SaaS订阅模式商业化。",
            },
        ]
    )
    tmp = ROOT / "results" / "_tmp_genai_concreteness_smoke.csv"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    examples.to_csv(tmp, index=False, encoding="utf-8-sig")
    out, _ = build_measures(tmp)
    low = out.loc[out["event_id"].eq("SMOKE_LOW")].iloc[0]
    high = out.loc[out["event_id"].eq("SMOKE_HIGH")].iloc[0]
    checks = [
        ("entity", high["entity_concrete_count"] > low["entity_concrete_count"]),
        ("operational", high["operational_concrete_count"] > low["operational_concrete_count"]),
        ("quant", high["quant_concrete_count"] > low["quant_concrete_count"]),
        ("total", high["total_concrete_count"] > low["total_concrete_count"]),
        ("raw", high["genai_concreteness_raw"] > low["genai_concreteness_raw"]),
    ]
    print(out[["event_id", "entity_concrete_count", "operational_concrete_count", "quant_concrete_count", "total_concrete_count", "genai_concreteness_raw", "content_category_primary"]].to_string(index=False))
    failed = [name for name, ok in checks if not ok]
    try:
        tmp.unlink()
    except OSError:
        pass
    if failed:
        raise SystemExit(f"Smoke test failed: {failed}")
    print("Smoke test passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build GenAI disclosure concreteness measures.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Event-level disclosure CSV.")
    parser.add_argument("--output-dir", default="", help="Output directory. Defaults to results/genai_concreteness_measure_YYYYMMDD.")
    parser.add_argument("--sample", type=int, default=None, help="Optional first-N rows for a small test run.")
    parser.add_argument("--validation-per-quintile", type=int, default=30, help="Rows per quintile in manual validation sample.")
    parser.add_argument("--smoke-test", action="store_true", help="Run deterministic hand-crafted examples and exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.smoke_test:
        smoke_test()
        return
    run_pipeline(args)


if __name__ == "__main__":
    main()
