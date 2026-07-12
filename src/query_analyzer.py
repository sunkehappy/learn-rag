from __future__ import annotations

import json
import logging
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

from config import BASE_URL, QWEN_API_KEY, QWEN_MODEL
from intent_config import apply_requirement_rules
from logging_config import log_progress
from models import ClarificationSession, QueryAnalysis

load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(api_key=QWEN_API_KEY, base_url=BASE_URL)

ANALYZER_PROMPT = """You are a query analyzer for a GitLab Handbook RAG assistant.

Return JSON only. No markdown. No explanation.

Tasks:
1. Detect user language.
2. Identify intent.
3. Extract country and GitLab entity if mentioned.
4. Decide whether clarification is needed.
5. If clarification is needed, generate a question in the user's language.

Country-required intents:
sick_leave, statutory_leave, public_holiday, vacation_minimum,
parental_leave, maternity_leave, paternity_leave, family_care_leave

Entity-required intents:
medical_insurance, dental_insurance, vision_insurance,
life_insurance, disability_insurance, retirement_plan, 401k,
pension, fertility_family_planning, employee_assistance_program,
benefit_enrollment, cobra, tax_forms,
payroll_specific_benefits, provider_or_vendor_info

Rules:
- Missing required country/entity => needs_clarification=true.
- Generate clarification_question in user's language.
- Do not guess country or entity.
- Normalize country to ISO 3166-1 alpha-2 when possible.
- Unknown intent => intent="unknown".

search_query rules (for vector retrieval only):
- Write search_query in English using intent-specific handbook keywords.
- Do NOT include country names, country codes, or GitLab entity names in search_query.
- Country and entity are used separately for metadata filtering, not in search_query.
- Focus on policy topic terms (e.g. sick_leave => "sick time policy 25 paid sick days Workday Out Sick reporting statutory").
- search_query must help find the relevant handbook section, not the user's location.

Return:

{
  "language": "",
  "intent": "",
  "country": null,
  "country_code": null,
  "entity": null,
  "needs_clarification": false,
  "missing_fields": [],
  "clarification_question": null,
  "search_query": ""
}

User question:
{{USER_QUESTION}}"""

_JSON_FENCE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _strip_json_fence(text: str) -> str:
    match = _JSON_FENCE_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _call_analyzer(user_question: str) -> QueryAnalysis:
    prompt = ANALYZER_PROMPT.replace("{{USER_QUESTION}}", user_question)
    log_progress(f"正在调用 LLM 进行意图分析 (model={QWEN_MODEL})...")
    start_time = time.perf_counter()
    response = client.chat.completions.create(
        model=str(QWEN_MODEL),
        messages=[{"role": "user", "content": prompt}],
    )
    latency_ms = (time.perf_counter() - start_time) * 1000
    content = response.choices[0].message.content or ""
    analysis = parse_analyzer_response(content)
    logger.info(
        "query analyzer LLM done latency_ms=%.1f intent=%s language=%s "
        "needs_clarification=%s missing_fields=%s search_query=%r",
        latency_ms,
        analysis.intent,
        analysis.language,
        analysis.needs_clarification,
        analysis.missing_fields,
        analysis.search_query,
    )
    log_progress(f"LLM 意图分析完成 ({latency_ms:.0f}ms): intent={analysis.intent}")
    return analysis


def parse_analyzer_response(content: str) -> QueryAnalysis:
    try:
        payload = json.loads(_strip_json_fence(content))
        if not isinstance(payload, dict):
            raise ValueError("analyzer response is not a JSON object")
        return QueryAnalysis.from_llm_json(payload)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        logger.warning("query analyzer parse failed: %s content=%r", exc, content[:500])
        return QueryAnalysis(
            language="en",
            intent="unknown",
            country=None,
            country_code=None,
            entity=None,
            needs_clarification=False,
            missing_fields=[],
            clarification_question=None,
            search_query="",
        )


def analyze_question(question: str) -> QueryAnalysis:
    analysis = _call_analyzer(question)
    log_progress("正在应用 intent 规则校验...")
    result = apply_requirement_rules(analysis)
    logger.info(
        "query analysis result intent=%s country_code=%s entity=%s "
        "needs_clarification=%s missing_fields=%s search_query=%r",
        result.intent,
        result.country_code,
        result.entity,
        result.needs_clarification,
        result.missing_fields,
        result.search_query,
    )
    return result


def merge_clarification(session: ClarificationSession, user_reply: str) -> QueryAnalysis:
    merged_question = (
        f"Original question: {session.original_question}\n"
        f"Clarification asked: {session.last_clarification_question or ''}\n"
        f"User clarification: {user_reply}"
    )
    log_progress("正在合并澄清回复并重新分析...")
    analysis = _call_analyzer(merged_question)
    if not analysis.search_query:
        analysis = QueryAnalysis(
            language=analysis.language or session.language,
            intent=analysis.intent or session.intent,
            country=analysis.country,
            country_code=analysis.country_code,
            entity=analysis.entity,
            needs_clarification=analysis.needs_clarification,
            missing_fields=analysis.missing_fields,
            clarification_question=analysis.clarification_question,
            search_query=session.search_query,
        )
    log_progress("正在应用 intent 规则校验...")
    result = apply_requirement_rules(analysis)
    logger.info(
        "merge clarification result intent=%s country_code=%s entity=%s "
        "needs_clarification=%s missing_fields=%s",
        result.intent,
        result.country_code,
        result.entity,
        result.needs_clarification,
        result.missing_fields,
    )
    return result
