#!/usr/bin/env python3
"""Rebuild a Qian-style GenAI initiative event set for supplier replication.

This script does not rerun supplier returns. It creates a review package so the
treatment can be manually audited before any AR/CAR result is interpreted.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v24_qian_initiative_event_rebuild_20260602"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "87_v24_qian_initiative_event_rebuild_20260602.md"

FORMAL_PATH = (
    ROOT
    / "results"
    / "v3_event_library_expansion_diagnostic"
    / "formal_all_events_events_before_car.csv"
)
IRQA_PATH = (
    ROOT
    / "results"
    / "v3_event_library_expansion_diagnostic"
    / "irqa_all_events_supplement_events_before_car.csv"
)
CSMAR_PATH = (
    ROOT
    / "results"
    / "v7_ai_supply_chain_disclosure_diagnostic_20260527"
    / "all_focal_events_supply_chain_codes.csv"
)
V23_FIRST_PATH = (
    ROOT
    / "results"
    / "v23_qian_supplier_replication_20260602"
    / "analysis_sample_first_valid_events.csv.gz"
)
CSMAR_CHAIN_ALL_PATH = (
    ROOT
    / "results"
    / "v21_supplier_specificity_smoke_20260601"
    / "chain_event_panel_all_events_with_car.csv.gz"
)
FORMAL_CHAIN_PATH = (
    ROOT
    / "results"
    / "v3_supplier_spillover_sample_diagnostic"
    / "formal_union_supplier_event_panel_before_car.csv"
)
IRQA_CHAIN_PATH = (
    ROOT
    / "results"
    / "v3_supplier_spillover_sample_diagnostic"
    / "irqa_union_supplier_event_panel_before_car.csv"
)


GENAI_TERMS = [
    "ChatGPT",
    "GPT",
    "GPT-4",
    "GPT4",
    "GenAI",
    "AIGC",
    "DeepSeek",
    "大模型",
    "大语言模型",
    "语言大模型",
    "生成式AI",
    "生成式人工智能",
    "生成式人工智慧",
    "generative AI",
    "large language model",
    "LLM",
    "文心一言",
    "文心",
    "通义千问",
    "通义",
    "讯飞星火",
    "星火",
    "盘古",
    "混元",
    "Kimi",
    "智谱",
    "ChatGLM",
    "GLM",
    "豆包",
    "百川",
    "MiniMax",
    "月之暗面",
    "Claude",
    "Gemini",
    "LLaMA",
    "Sora",
    "多模态大模型",
]
GENAI_PAT = re.compile("|".join(re.escape(x) for x in GENAI_TERMS), re.I)
GENERIC_AI_PAT = re.compile(
    r"(?:人工智能|AI|智能化|算法|机器学习|深度学习|自然语言处理|NLP|RAG|Agent|智能体|知识图谱)",
    re.I,
)

NEGATIVE_PAT = re.compile(
    r"(?:暂不|暂未|尚未|未|无|没有|不|暂无|尚无).{0,18}"
    r"(?:涉及|开展|布局|接入|应用|使用|推出|发布|相关业务|相关产品|相关技术|合作|业务往来|应用场景)|"
    r"(?:不涉及|未涉及|暂无涉及|暂不涉及|暂未涉及|尚未涉及|没有涉及).{0,30}"
    r"(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能|DeepSeek)|"
    r"(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能|DeepSeek|相关技术|该技术).{0,35}"
    r"(?:暂不涉及|暂未涉及|不涉及|未涉及|暂无|尚无|没有|无|未应用|尚未应用|未接入|尚未接入|无合作|无业务往来)|"
    r"(?:没有将|尚未将|暂未将).{0,35}"
    r"(?:ChatGPT|GPT|AIGC|大模型|生成式|人工智能|DeepSeek|该技术).{0,35}"
    r"(?:应用|接入|用于|部署|商业化)",
    re.I,
)
NEG_WORD_PAT = re.compile(r"(?:暂不|暂未|尚未|未|无|没有|不涉及|暂无|尚无|没有将|尚未将|暂未将)", re.I)
NEG_ACTION_PAT = re.compile(
    r"(?:涉及|开展|布局|接入|应用|使用|推出|发布|合作|业务往来|应用场景|落地|部署|商业化)",
    re.I,
)

POS_ACTION_PAT = re.compile(
    r"(?:已|已经|正在|正式|完成|上线|发布|推出|部署|接入|集成|落地|应用|使用|内测|公测|试点|训练|"
    r"开发|研发|打造|建设|投建|投资|采购|中标|签署|签订|合作|联合|商用|商业化|交付|备案|升级|"
    r"推出了|发布了|上线了|落地了|应用于|用于).{0,45}"
    r"(?:ChatGPT|GPT|DeepSeek|Kimi|通义|文心|智谱|星火|盘古|混元|豆包|AIGC|生成式|大模型|"
    r"大语言模型|LLM|多模态)|"
    r"(?:ChatGPT|GPT|DeepSeek|Kimi|通义|文心|智谱|星火|盘古|混元|豆包|AIGC|生成式|大模型|"
    r"大语言模型|LLM|多模态).{0,45}"
    r"(?:上线|发布|推出|部署|接入|集成|落地|应用|使用|内测|公测|试点|训练|开发|研发|打造|建设|"
    r"投建|投资|采购|中标|签署|签订|合作|联合|商用|商业化|交付|备案|升级)",
    re.I,
)
COMPANY_ACTION_PAT = re.compile(
    r"(?:公司|本公司|我司|我们|集团|子公司|控股子公司|旗下|团队|平台).{0,80}"
    r"(?:已|已经|正在|正式|推出|发布|接入|集成|应用|使用|部署|落地|研发|开发|训练|测试|内测|试点|"
    r"合作|签署|签订|商业化|上线|升级|打造|建设|采购|中标|投建|投资)",
    re.I,
)
COMPANY_ACTOR_CUE_PAT = re.compile(
    r"(?:公司|本公司|我司|我们|集团|子公司|控股子公司|旗下|团队|自研|自主研发|自主|项目|产品|平台|系统|"
    r"模型|方案|业务|客户|用户|合同|订单|采购|中标|签署|签订|合作|联合|共建|接入|集成|部署|应用于|用于)",
    re.I,
)
THIRD_PARTY_EXPLANATION_PAT = re.compile(
    r"(?:ChatGPT是由|ChatGPT是|GPT作为|OpenAI.{0,20}发布|微软.{0,20}OpenAI|最新推出的一种|"
    r"一款人工智能技术驱动|可以完成|带来.{0,20}机会|展现了|预计将|市场.{0,20}快速成长|"
    r"业界.{0,20}感受到|预训练大模型.{0,20}方法)",
    re.I,
)
WEAK_ATTENTION_PAT = re.compile(
    r"(?:密切关注|持续关注|积极关注|高度关注|关注前沿|关注.{0,12}(?:技术|市场|趋势|发展|动向)|"
    r"探索|研究|储备|跟踪|研判|学习|考虑|机会|可能|未来|以公司公开披露|以公告为准|"
    r"请以.{0,12}(?:公告|披露|公开信息)为准|感谢.{0,12}关注)",
    re.I,
)
PURE_QUESTION_PAT = re.compile(r"(?:请问|是否|有没有|能否|是不是|建议公司|请介绍|是否有|有无)", re.I)
PRODUCT_OR_WORKFLOW_PAT = re.compile(
    r"(?:产品|服务|平台|系统|软件|APP|应用|方案|工具|机器人|助手|模块|解决方案|智能体|Agent|"
    r"座舱|客服|模型平台|大模型平台|一体机|数字人|知识库|工作流|流程|运营|办公|生产|研发|营销|"
    r"金融|医疗|教育|政务|电力|制造|水电|新能源|客服|投研|风控|质检|代码|编程|问答|搜索|推荐|"
    r"训练|翻译|图像|视频|绘画|内容生成|数据分析|供应链|审计)",
    re.I,
)
DEPLOYMENT_PAT = re.compile(
    r"(?:已上线|已经上线|正式上线|已发布|已经发布|正式发布|已推出|已经推出|已备案|备案通过|"
    r"已通过|已落地|已经落地|已部署|已经部署|已接入|已经接入|已集成|已经集成|已应用|已经应用|"
    r"应用于|试点|内测|公测|完成训练|正在训练|签署|签订|已签约|商业化|商用|量产|交付|采购|中标)",
    re.I,
)
PARTNER_PAT = re.compile(
    r"(?:合作|伙伴|联合|共建|生态|签署|签订|中标|采购|客户|用户|供应商|阿里|百度|腾讯|华为|微软|"
    r"OpenAI|英伟达|商汤|讯飞|京东|字节|火山|智谱|清华|北大|大学|研究院|实验室|银行|医院|政府)",
    re.I,
)
NUMERIC_PAT = re.compile(
    r"(?:\d+(?:\.\d+)?(?:亿元|万元|元|万美元|美元|人民币|%|％|个|项|款|台|套|人|家|年|月|日|"
    r"亿|万|次|小时|天|倍|G|GB|TB|PB|亿参数|参数|P|T)|Q[1-4]|[一二三四1234]季度|20[2-9]\d年)",
    re.I,
)


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def clean_text(value: object, max_len: int = 2400) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()[:max_len]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？；;.!?])", text)
    return [p.strip() for p in parts if len(p.strip()) >= 3]


def genai_context(text: str, max_len: int = 1600) -> str:
    text = clean_text(text, max_len=5000)
    sentences = split_sentences(text)
    selected: list[str] = []
    for idx, sent in enumerate(sentences):
        if GENAI_PAT.search(sent):
            if idx > 0 and len(sentences[idx - 1]) <= 220:
                selected.append(sentences[idx - 1])
            selected.append(sent)
            if idx + 1 < len(sentences) and len(sentences[idx + 1]) <= 220:
                selected.append(sentences[idx + 1])
    if not selected:
        return text[:max_len]
    out: list[str] = []
    for item in selected:
        if item not in out:
            out.append(item)
    return " ".join(out)[:max_len]


def first_snippet(text: str, pat: re.Pattern[str] | None = None, max_len: int = 180) -> str:
    text = clean_text(text, max_len=4000)
    for sent in split_sentences(text):
        if pat is None:
            if GENAI_PAT.search(sent):
                return sent[:max_len]
        elif pat.search(sent):
            return sent[:max_len]
    return text[:max_len]


def sentence_is_negative(sent: str) -> bool:
    if NEGATIVE_PAT.search(sent):
        return True
    if not GENAI_PAT.search(sent):
        return False
    return bool(NEG_WORD_PAT.search(sent) and NEG_ACTION_PAT.search(sent))


def sentence_is_positive_action(sent: str) -> bool:
    if sentence_is_negative(sent):
        return False
    if THIRD_PARTY_EXPLANATION_PAT.search(sent) and not COMPANY_ACTION_PAT.search(sent):
        return False
    if POS_ACTION_PAT.search(sent) and COMPANY_ACTOR_CUE_PAT.search(sent):
        return True
    return bool(COMPANY_ACTION_PAT.search(sent) and GENAI_PAT.search(sent))


def bool_int(value: bool) -> int:
    return int(bool(value))


def normalize_formal() -> pd.DataFrame:
    if not FORMAL_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(FORMAL_PATH, dtype=str)
    out = pd.DataFrame(
        {
            "source_record_id": "FORMAL_" + df["announcement_id"].astype(str),
            "event_id": "FORMAL_" + df["announcement_id"].astype(str),
            "focal_code": df["sec_code"].map(code6),
            "company_name": df.get("sec_name", ""),
            "event_date": pd.to_datetime(df["announcement_date"], errors="coerce"),
            "source_type": "formal_cninfo_announcement",
            "source_priority": 1,
            "title": df.get("announcement_title", ""),
            "answer_terms": df.get("matched_genai_terms", ""),
            "question_terms": "",
            "company_text": df.get("genai_span_examples", ""),
            "question_text": "",
            "source_url": df.get("pdf_url", ""),
            "local_text_file": df.get("txt_file", ""),
            "raw_sample_layer": df.get("sample_layer", ""),
        }
    )
    return out


def normalize_irqa() -> pd.DataFrame:
    if not IRQA_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(IRQA_PATH, dtype=str)
    out = pd.DataFrame(
        {
            "source_record_id": "IRQA_" + df["announcement_id"].astype(str),
            "event_id": "IRQA_" + df["announcement_id"].astype(str),
            "focal_code": df["sec_code"].map(code6),
            "company_name": df.get("sec_name", ""),
            "event_date": pd.to_datetime(df["announcement_date"], errors="coerce"),
            "source_type": "supplemental_irqa_answer",
            "source_priority": 3,
            "title": df.get("announcement_title", ""),
            "answer_terms": df.get("matched_genai_terms", ""),
            "question_terms": "",
            "company_text": df.get("genai_span_examples", ""),
            "question_text": "",
            "source_url": df.get("source_url", ""),
            "local_text_file": "",
            "raw_sample_layer": df.get("sample_layer", ""),
        }
    )
    return out


def normalize_csmar() -> pd.DataFrame:
    if not CSMAR_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(CSMAR_PATH, dtype={"event_id": str, "focal_code": str, "stock_code": str})
    out = pd.DataFrame(
        {
            "source_record_id": "CSMAR_" + df["event_id"].astype(str),
            "event_id": df["event_id"].astype(str),
            "focal_code": df["focal_code"].map(code6),
            "company_name": df.get("company_name", ""),
            "event_date": pd.to_datetime(df["event_date"], errors="coerce"),
            "source_type": df.get("sources", ""),
            "source_priority": 2,
            "title": "",
            "answer_terms": df.get("answer_terms", ""),
            "question_terms": df.get("question_terms", ""),
            "company_text": df.get("sample_answer", ""),
            "question_text": df.get("sample_question", ""),
            "source_url": "",
            "local_text_file": "",
            "raw_sample_layer": "csmar_focal_event_library",
        }
    )
    return out


def load_v23_upstream_event_stats() -> pd.DataFrame:
    if not V23_FIRST_PATH.exists():
        return pd.DataFrame(columns=["event_id"])
    df = pd.read_csv(V23_FIRST_PATH, dtype={"event_id": str, "focal_code": str, "affected_code": str})
    df = df[df["relation"].eq("upstream_supplier")].copy()
    if df.empty:
        return pd.DataFrame(columns=["event_id"])
    df["ok_0_int"] = df.get("ok_0", False).astype(str).str.lower().isin(["true", "1"]).astype(int)
    out = (
        df.groupby("event_id", dropna=False)
        .agg(
            v23_upstream_supplier_links=("affected_code", "nunique"),
            v23_upstream_rows=("affected_code", "size"),
            v23_upstream_ar0_valid_rows=("ok_0_int", "sum"),
        )
        .reset_index()
    )
    out["in_v23_upstream_first"] = 1
    return out


def load_supplier_link_stats() -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    if CSMAR_CHAIN_ALL_PATH.exists():
        csmar = pd.read_csv(
            CSMAR_CHAIN_ALL_PATH,
            dtype={"event_id": str, "affected_code": str, "focal_code": str},
            usecols=lambda c: c
            in {
                "event_id",
                "affected_code",
                "relation",
                "chain_car_0_p1_mm",
            },
        )
        if "relation" in csmar.columns:
            csmar = csmar[csmar["relation"].eq("upstream_supplier")].copy()
        csmar["event_id"] = csmar["event_id"].astype(str)
        csmar["affected_code"] = csmar["affected_code"].map(code6)
        csmar["has_return_proxy"] = pd.to_numeric(csmar.get("chain_car_0_p1_mm"), errors="coerce").notna().astype(int)
        parts.append(
            csmar.groupby("event_id", dropna=False)
            .agg(
                supplier_linked_rows=("affected_code", "size"),
                supplier_linked_unique_suppliers=("affected_code", "nunique"),
                supplier_linked_return_rows=("has_return_proxy", "sum"),
            )
            .reset_index()
        )

    for path, prefix in [(FORMAL_CHAIN_PATH, "FORMAL_"), (IRQA_CHAIN_PATH, "IRQA_")]:
        if not path.exists():
            continue
        df = pd.read_csv(path, dtype={"announcement_id": str, "supplier_code": str})
        if "announcement_id" not in df.columns or "supplier_code" not in df.columns:
            continue
        df["event_id"] = prefix + df["announcement_id"].astype(str)
        df["supplier_code"] = df["supplier_code"].map(code6)
        parts.append(
            df.groupby("event_id", dropna=False)
            .agg(
                supplier_linked_rows=("supplier_code", "size"),
                supplier_linked_unique_suppliers=("supplier_code", "nunique"),
                supplier_linked_return_rows=("supplier_code", "size"),
            )
            .reset_index()
        )

    if not parts:
        return pd.DataFrame(
            columns=[
                "event_id",
                "supplier_linked_rows",
                "supplier_linked_unique_suppliers",
                "supplier_linked_return_rows",
            ]
        )
    stats = pd.concat(parts, ignore_index=True)
    stats = (
        stats.groupby("event_id", dropna=False)
        .agg(
            supplier_linked_rows=("supplier_linked_rows", "sum"),
            supplier_linked_unique_suppliers=("supplier_linked_unique_suppliers", "sum"),
            supplier_linked_return_rows=("supplier_linked_return_rows", "sum"),
        )
        .reset_index()
    )
    stats["has_supplier_link"] = (stats["supplier_linked_unique_suppliers"] > 0).astype(int)
    return stats


def classify_row(row: pd.Series) -> dict[str, object]:
    company_text = clean_text(row.get("company_text", ""), max_len=5000)
    question_text = clean_text(row.get("question_text", ""), max_len=1800)
    title = clean_text(row.get("title", ""), max_len=500)
    answer_terms = clean_text(row.get("answer_terms", ""), max_len=500)
    question_terms = clean_text(row.get("question_terms", ""), max_len=500)

    company_core = " ".join([title, company_text])
    company_blob = " ".join([company_core, answer_terms])
    question_blob = " ".join([question_terms, question_text])
    all_blob = " ".join([company_blob, question_blob])
    context = genai_context(company_core)

    strict_company = bool(GENAI_PAT.search(company_blob))
    strict_question = bool(GENAI_PAT.search(question_blob))
    strict_any = bool(GENAI_PAT.search(all_blob))
    generic_any = bool(GENERIC_AI_PAT.search(all_blob))
    question_only = strict_question and not strict_company

    sentences = split_sentences(context)
    has_negative_sentence = any(sentence_is_negative(sent) for sent in sentences)
    has_positive_action_sentence = any(sentence_is_positive_action(sent) for sent in sentences)
    has_boilerplate = bool(WEAK_ATTENTION_PAT.search(context))
    has_product_or_workflow = bool(PRODUCT_OR_WORKFLOW_PAT.search(context))
    has_deployment = any(
        DEPLOYMENT_PAT.search(sent)
        and not (THIRD_PARTY_EXPLANATION_PAT.search(sent) and not COMPANY_ACTION_PAT.search(sent))
        and (COMPANY_ACTOR_CUE_PAT.search(sent) or COMPANY_ACTION_PAT.search(sent))
        for sent in sentences
    )
    has_partner = bool(PARTNER_PAT.search(context))
    has_numeric = bool(NUMERIC_PAT.search(context))
    has_pure_question = bool(PURE_QUESTION_PAT.search(question_blob))
    is_formal = row.get("source_type") == "formal_cninfo_announcement"

    evidence_score = (
        2 * bool_int(has_positive_action_sentence)
        + bool_int(has_product_or_workflow)
        + bool_int(has_deployment)
        + bool_int(has_partner)
        + bool_int(has_numeric)
        + bool_int(is_formal)
    )
    clear_denial_only = has_negative_sentence and not has_positive_action_sentence
    clear_boilerplate_only = has_boilerplate and not has_positive_action_sentence and not has_deployment

    if not strict_any and generic_any:
        label = "exclude_generic_or_legacy_ai_only"
        keep_candidate = 0
    elif question_only:
        label = "exclude_question_only_trigger"
        keep_candidate = 0
    elif clear_denial_only:
        label = "exclude_denial_no_current_business"
        keep_candidate = 0
    elif strict_company and has_positive_action_sentence and evidence_score >= 4:
        label = "keep_candidate_strong_specific_initiative"
        keep_candidate = 1
    elif strict_company and has_positive_action_sentence and evidence_score >= 3:
        label = "review_possible_specific_initiative"
        keep_candidate = 1
    elif strict_company and is_formal and evidence_score >= 3 and not clear_denial_only:
        label = "review_formal_possible_project"
        keep_candidate = 1
    elif strict_company and clear_boilerplate_only:
        label = "exclude_boilerplate_attention_only"
        keep_candidate = 0
    elif strict_company:
        label = "review_ambiguous_strict_genai"
        keep_candidate = 0
    else:
        label = "exclude_no_strict_genai"
        keep_candidate = 0

    exclusion_hint = ""
    if label.startswith("exclude_denial"):
        exclusion_hint = "denial/no-current-business"
    elif label.startswith("exclude_question"):
        exclusion_hint = "strict term appears only in investor/question text"
    elif label.startswith("exclude_boilerplate"):
        exclusion_hint = "attention/exploration boilerplate without concrete action"
    elif label.startswith("exclude_generic"):
        exclusion_hint = "generic AI/RAG/Agent/NLP without strict GenAI initiative"
    elif label.startswith("exclude_no_strict"):
        exclusion_hint = "no strict GenAI term"

    return {
        "has_strict_genai_any": bool_int(strict_any),
        "has_strict_genai_company_text": bool_int(strict_company),
        "has_strict_genai_question_text": bool_int(strict_question),
        "generic_ai_any": bool_int(generic_any),
        "question_only_trigger": bool_int(question_only),
        "negative_no_current_flag": bool_int(clear_denial_only),
        "boilerplate_attention_flag": bool_int(clear_boilerplate_only),
        "positive_initiative_action_flag": bool_int(has_positive_action_sentence),
        "product_or_workflow_flag": bool_int(has_product_or_workflow),
        "deployment_or_contract_flag": bool_int(has_deployment),
        "partner_or_customer_flag": bool_int(has_partner),
        "numeric_or_timeline_flag": bool_int(has_numeric),
        "pure_question_form_flag": bool_int(has_pure_question),
        "qian_auto_label": label,
        "qian_auto_keep_candidate": keep_candidate,
        "qian_evidence_score": evidence_score,
        "auto_exclusion_hint": exclusion_hint,
        "genai_context": context,
        "action_snippet": first_snippet(context, POS_ACTION_PAT),
        "denial_snippet": first_snippet(context, NEGATIVE_PAT),
    }


def add_classification(events: pd.DataFrame) -> pd.DataFrame:
    classified = pd.DataFrame([classify_row(row) for _, row in events.iterrows()])
    out = pd.concat([events.reset_index(drop=True), classified], axis=1)
    out["event_year"] = out["event_date"].dt.year
    out["firm_date_key"] = out["focal_code"] + "_" + out["event_date"].dt.strftime("%Y-%m-%d").fillna("")
    out["source_priority"] = pd.to_numeric(out["source_priority"], errors="coerce").fillna(9).astype(int)
    out = out.sort_values(["event_date", "source_priority", "focal_code", "event_id"]).reset_index(drop=True)
    return out


def with_manual_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    manual_cols = [
        "manual_keep_qian_0_1",
        "manual_exclusion_reason",
        "manual_product_or_process",
        "manual_company_is_actor_0_1",
        "manual_event_date_verified_0_1",
        "manual_confidence_1_3",
        "manual_notes",
    ]
    for col in reversed(manual_cols):
        out.insert(0, col, "")
    return out


def review_columns() -> list[str]:
    return [
        "manual_keep_qian_0_1",
        "manual_exclusion_reason",
        "manual_product_or_process",
        "manual_company_is_actor_0_1",
        "manual_event_date_verified_0_1",
        "manual_confidence_1_3",
        "manual_notes",
        "review_id",
        "qian_auto_label",
        "qian_auto_keep_candidate",
        "qian_evidence_score",
        "auto_exclusion_hint",
        "in_v23_upstream_first",
        "v23_upstream_supplier_links",
        "v23_upstream_ar0_valid_rows",
        "has_supplier_link",
        "supplier_linked_unique_suppliers",
        "supplier_linked_return_rows",
        "event_id",
        "focal_code",
        "company_name",
        "event_date",
        "event_year",
        "source_type",
        "title",
        "answer_terms",
        "question_terms",
        "has_strict_genai_company_text",
        "has_strict_genai_question_text",
        "question_only_trigger",
        "negative_no_current_flag",
        "boilerplate_attention_flag",
        "positive_initiative_action_flag",
        "product_or_workflow_flag",
        "deployment_or_contract_flag",
        "partner_or_customer_flag",
        "numeric_or_timeline_flag",
        "genai_context",
        "question_text",
        "source_url",
        "local_text_file",
    ]


def prepare_review(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["event_date"] = out["event_date"].dt.strftime("%Y-%m-%d")
    out["review_id"] = [f"QIAN{idx:05d}" for idx in range(1, len(out) + 1)]
    out = with_manual_columns(out)
    cols = [c for c in review_columns() if c in out.columns]
    return out[cols]


def first_candidate_per_firm(df: pd.DataFrame) -> pd.DataFrame:
    cand = df[df["qian_auto_keep_candidate"].eq(1)].copy()
    if cand.empty:
        return cand
    cand = cand.sort_values(["focal_code", "event_date", "source_priority", "qian_auto_label", "event_id"])
    first = cand.groupby("focal_code", as_index=False).head(1).reset_index(drop=True)
    return first.sort_values(["event_date", "source_priority", "focal_code"]).reset_index(drop=True)


def pct(value: int, denom: int) -> float:
    if denom == 0:
        return math.nan
    return round(100 * value / denom, 2)


def markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_empty_"
    show = df.head(max_rows).copy()
    return show.to_markdown(index=False)


def write_outputs(events: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    v23_stats = load_v23_upstream_event_stats()
    events = events.merge(v23_stats, on="event_id", how="left")
    events["in_v23_upstream_first"] = events["in_v23_upstream_first"].fillna(0).astype(int)
    events["v23_upstream_supplier_links"] = events["v23_upstream_supplier_links"].fillna(0).astype(int)
    events["v23_upstream_ar0_valid_rows"] = events["v23_upstream_ar0_valid_rows"].fillna(0).astype(int)

    supplier_stats = load_supplier_link_stats()
    events = events.merge(supplier_stats, on="event_id", how="left")
    for col in [
        "supplier_linked_rows",
        "supplier_linked_unique_suppliers",
        "supplier_linked_return_rows",
        "has_supplier_link",
    ]:
        events[col] = events[col].fillna(0).astype(int)
    events["supplier_linked_unique_suppliers"] = events[
        ["supplier_linked_unique_suppliers", "v23_upstream_supplier_links"]
    ].max(axis=1)
    events["supplier_linked_rows"] = events[["supplier_linked_rows", "v23_upstream_rows"]].max(axis=1)
    events["supplier_linked_return_rows"] = events[
        ["supplier_linked_return_rows", "v23_upstream_ar0_valid_rows"]
    ].max(axis=1)
    events["has_supplier_link"] = (
        (events["has_supplier_link"].eq(1)) | (events["v23_upstream_supplier_links"].gt(0))
    ).astype(int)

    all_path = OUT_DIR / "event_universe_auto_classified.csv.gz"
    strict_path = OUT_DIR / "manual_review_all_strict_events.csv.gz"
    v23_path = OUT_DIR / "manual_review_v23_upstream_focal_events.csv"
    cand_path = OUT_DIR / "manual_review_qian_candidate_events.csv"
    first_path = OUT_DIR / "manual_review_first_auto_candidate_per_firm.csv"
    supplier_cand_path = OUT_DIR / "manual_review_supplier_linked_candidate_events.csv"
    supplier_first_path = OUT_DIR / "manual_review_first_supplier_linked_auto_candidate_per_firm.csv"
    instructions_path = OUT_DIR / "manual_review_instructions.md"

    events.to_csv(all_path, index=False, compression="gzip", encoding="utf-8-sig")

    strict = events[events["has_strict_genai_any"].eq(1)].copy()
    strict_review = prepare_review(strict.sort_values(["event_date", "source_priority", "focal_code", "event_id"]))
    strict_review.to_csv(strict_path, index=False, compression="gzip", encoding="utf-8-sig")

    v23 = events[events["in_v23_upstream_first"].eq(1)].copy()
    v23 = v23.drop_duplicates("event_id").sort_values(
        ["qian_auto_keep_candidate", "qian_auto_label", "event_date", "focal_code"],
        ascending=[False, True, True, True],
    )
    prepare_review(v23).to_csv(v23_path, index=False, encoding="utf-8-sig")

    candidate_labels = {
        "keep_candidate_strong_specific_initiative",
        "review_possible_specific_initiative",
        "review_formal_possible_project",
        "review_ambiguous_strict_genai",
    }
    candidates = events[events["qian_auto_label"].isin(candidate_labels)].copy()
    candidates = candidates.sort_values(
        ["qian_auto_keep_candidate", "event_date", "source_priority", "focal_code", "event_id"],
        ascending=[False, True, True, True, True],
    )
    prepare_review(candidates).to_csv(cand_path, index=False, encoding="utf-8-sig")

    first = first_candidate_per_firm(events)
    prepare_review(first).to_csv(first_path, index=False, encoding="utf-8-sig")

    supplier_candidates = candidates[candidates["has_supplier_link"].eq(1)].copy()
    supplier_candidates = supplier_candidates.sort_values(
        [
            "qian_auto_keep_candidate",
            "supplier_linked_unique_suppliers",
            "event_date",
            "source_priority",
            "focal_code",
            "event_id",
        ],
        ascending=[False, False, True, True, True, True],
    )
    prepare_review(supplier_candidates).to_csv(supplier_cand_path, index=False, encoding="utf-8-sig")

    supplier_first = first_candidate_per_firm(events[events["has_supplier_link"].eq(1)].copy())
    prepare_review(supplier_first).to_csv(supplier_first_path, index=False, encoding="utf-8-sig")

    label_counts = (
        events.groupby(["source_type", "qian_auto_label"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values(["source_type", "n"], ascending=[True, False])
    )
    label_counts.to_csv(OUT_DIR / "auto_label_counts_by_source.csv", index=False, encoding="utf-8-sig")

    v23_label_counts = (
        v23.groupby("qian_auto_label", dropna=False)
        .agg(events=("event_id", "nunique"), supplier_links=("v23_upstream_supplier_links", "sum"))
        .reset_index()
        .sort_values("events", ascending=False)
    )
    v23_label_counts.to_csv(OUT_DIR / "v23_upstream_auto_label_counts.csv", index=False, encoding="utf-8-sig")

    candidate_year_source = (
        candidates.groupby(["event_year", "source_type", "qian_auto_label"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values(["event_year", "source_type", "qian_auto_label"])
    )
    candidate_year_source.to_csv(OUT_DIR / "candidate_counts_by_year_source_label.csv", index=False, encoding="utf-8-sig")

    examples = (
        events.sort_values(["qian_auto_label", "event_date", "source_priority"])
        .groupby("qian_auto_label", as_index=False)
        .head(5)
        [
            [
                "qian_auto_label",
                "event_date",
                "focal_code",
                "company_name",
                "source_type",
                "title",
                "genai_context",
                "question_text",
            ]
        ]
    )
    examples.to_csv(OUT_DIR / "examples_by_auto_label.csv", index=False, encoding="utf-8-sig")

    total = len(events)
    v23_n = v23["event_id"].nunique()
    v23_excluded = int(v23["qian_auto_keep_candidate"].eq(0).sum())
    summary = pd.DataFrame(
        [
            {"metric": "all_event_rows", "value": total},
            {"metric": "all_unique_firms", "value": events["focal_code"].nunique()},
            {"metric": "strict_genai_any_rows", "value": int(events["has_strict_genai_any"].sum())},
            {"metric": "strict_genai_company_text_rows", "value": int(events["has_strict_genai_company_text"].sum())},
            {"metric": "auto_keep_candidate_rows", "value": int(events["qian_auto_keep_candidate"].sum())},
            {"metric": "auto_keep_candidate_unique_firms", "value": events.loc[events["qian_auto_keep_candidate"].eq(1), "focal_code"].nunique()},
            {"metric": "first_auto_candidate_unique_firms", "value": first["focal_code"].nunique() if not first.empty else 0},
            {"metric": "supplier_linked_event_rows", "value": int(events["has_supplier_link"].sum())},
            {"metric": "supplier_linked_auto_keep_candidate_rows", "value": int(((events["has_supplier_link"].eq(1)) & (events["qian_auto_keep_candidate"].eq(1))).sum())},
            {"metric": "supplier_linked_auto_keep_candidate_unique_firms", "value": events.loc[events["has_supplier_link"].eq(1) & events["qian_auto_keep_candidate"].eq(1), "focal_code"].nunique()},
            {"metric": "first_supplier_linked_auto_candidate_unique_firms", "value": supplier_first["focal_code"].nunique() if not supplier_first.empty else 0},
            {"metric": "v23_upstream_unique_focal_events", "value": v23_n},
            {"metric": "v23_upstream_auto_keep_candidate_events", "value": int(v23["qian_auto_keep_candidate"].sum())},
            {"metric": "v23_upstream_auto_excluded_events", "value": v23_excluded},
            {"metric": "v23_upstream_auto_excluded_pct", "value": pct(v23_excluded, v23_n)},
        ]
    )
    summary.to_csv(OUT_DIR / "event_rebuild_summary.csv", index=False, encoding="utf-8-sig")

    instructions = """# Qian-Style GenAI Initiative Manual Review

Code the company-side disclosure, not the investor question alone.

`manual_keep_qian_0_1 = 1` only if all conditions hold:

1. The focal listed company is the actor or direct adopter.
2. The text explicitly refers to a strict GenAI technology, such as ChatGPT, GPT, AIGC, DeepSeek, large language models, generative AI, or a named large-model platform.
3. The disclosure contains a specific initiative: investment, adoption, product integration, product launch, deployment, procurement, contract, pilot, commercialization, or workflow incorporation.
4. The event date/source is verifiable from the disclosure record.

Set `manual_keep_qian_0_1 = 0` for:

- denial/no-current-business answers;
- pure investor-question triggers where the company does not affirm an initiative;
- attention/exploration boilerplate, including "密切关注" and "以公告为准";
- generic AI, RAG, Agent, NLP, algorithm, or intelligent-manufacturing mentions without strict GenAI initiative evidence;
- broad industry trend discussion where the company is not taking a concrete action.

`manual_product_or_process`:

- `product`: GenAI is integrated into products, services, customer-facing features, or external offerings.
- `process`: GenAI is mainly used in internal workflow, production, R&D, customer service, office, or operations.
- `both`, `unclear`, or blank are allowed during first-pass review.

Recommended order:

1. Review `manual_review_v23_upstream_focal_events.csv` first to audit the contaminated v23 treatment.
2. Review `manual_review_first_supplier_linked_auto_candidate_per_firm.csv` as the Qian-style first-pass treatment queue.
3. Use `manual_review_supplier_linked_candidate_events.csv` to recover an alternative earlier/later event if the first machine candidate is rejected.
4. Use `manual_review_qian_candidate_events.csv` only for broader event-library backtracking.
5. After manual labels are complete, rerun supplier AR only on the first kept event per focal firm.
"""
    instructions_path.write_text(instructions, encoding="utf-8")

    doc = f"""# v24 Qian Supplier Replication Event Rebuild

Date: 2026-06-02

Purpose: rebuild the treatment side before rerunning the Qian-style supplier event study. v23 should be treated as a keyword-triggered audit, not as a clean replication of Qian et al.'s GenAI initiative sample.

## Qian Screen Implemented Here

Qian et al. manually reviewed firm announcements, retained explicit GenAI initiatives, excluded broad GenAI/IT mentions, kept the earliest initiative per firm, verified announcement dates, and then linked downstream customers to listed suppliers. This v24 run mirrors the event-screening part only.

The intended funnel is therefore: broad GenAI retrieval -> listed-company event universe -> manual initiative screen -> first initiative per firm -> supplier-link and return-data filters. The broad retrieval is not the treatment.

## Inputs

- Formal CNINFO events: `{FORMAL_PATH.relative_to(ROOT)}`
- Supplemental IR/QA events: `{IRQA_PATH.relative_to(ROOT)}`
- CSMAR focal events used by prior T05 panels: `{CSMAR_PATH.relative_to(ROOT)}`
- v23 first-event supplier sample markers: `{V23_FIRST_PATH.relative_to(ROOT)}`

## Output Files

- `event_universe_auto_classified.csv.gz`: all normalized events with rule flags.
- `manual_review_v23_upstream_focal_events.csv`: one row per v23 upstream focal event for contamination audit.
- `manual_review_qian_candidate_events.csv`: machine-prioritized candidate/review rows for building the corrected treatment.
- `manual_review_first_auto_candidate_per_firm.csv`: earliest machine-kept candidate per focal firm, not final until manually coded.
- `manual_review_supplier_linked_candidate_events.csv`: candidate/review rows that have an upstream listed-supplier link.
- `manual_review_first_supplier_linked_auto_candidate_per_firm.csv`: recommended first-pass manual queue for the replication sample.
- `manual_review_all_strict_events.csv.gz`: all strict GenAI rows for backtracking.
- `manual_review_instructions.md`: coding rules for one-by-one review.

## Summary

{markdown_table(summary)}

## v23 Upstream Event Auto Labels

{markdown_table(v23_label_counts)}

## Candidate Counts by Source and Label

{markdown_table(label_counts[label_counts["qian_auto_label"].isin(candidate_labels)], 40)}

## Interpretation

The decisive next step is manual coding, not another return regression. Start with `manual_review_first_supplier_linked_auto_candidate_per_firm.csv` (200 rows). `manual_keep_qian_0_1` must become the gate for the corrected event sample. Only after that should the supplier AR0 and CAR[0,+1] tables be rerun.

## Current Limitation

The rule labels are conservative triage labels. They help sort and identify obvious exclusions, but they do not replace reading the announcement/answer text and verifying whether the company itself announced a concrete GenAI initiative.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")


def main() -> None:
    parts = [normalize_formal(), normalize_irqa(), normalize_csmar()]
    parts = [p for p in parts if not p.empty]
    if not parts:
        raise FileNotFoundError("No event source files were available.")
    events = pd.concat(parts, ignore_index=True)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    for col in ["company_text", "question_text", "title", "answer_terms", "question_terms", "source_url", "local_text_file"]:
        events[col] = events[col].map(clean_text)
    events = events.dropna(subset=["event_date"]).copy()
    events = events[events["focal_code"].astype(str).str.len().eq(6)].copy()
    events = events.drop_duplicates(["source_record_id"]).reset_index(drop=True)
    events = add_classification(events)
    write_outputs(events)
    print(f"Wrote {OUT_DIR}")
    print(f"Wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
