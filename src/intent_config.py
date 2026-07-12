from __future__ import annotations

import re

from entity_resolver import COUNTRY_NAME_TO_CODE, PATH_RULES
from models import QueryAnalysis

COUNTRY_REQUIRED_INTENTS = frozenset(
    {
        "sick_leave",
        "statutory_leave",
        "public_holiday",
        "vacation_minimum",
        "parental_leave",
        "maternity_leave",
        "paternity_leave",
        "family_care_leave",
    }
)

ENTITY_REQUIRED_INTENTS = frozenset(
    {
        "medical_insurance",
        "dental_insurance",
        "vision_insurance",
        "life_insurance",
        "disability_insurance",
        "retirement_plan",
        "401k",
        "pension",
        "fertility_family_planning",
        "employee_assistance_program",
        "benefit_enrollment",
        "cobra",
        "tax_forms",
        "payroll_specific_benefits",
        "provider_or_vendor_info",
    }
)

KNOWN_ENTITIES: tuple[str, ...] = tuple(
    dict.fromkeys(entity for _, entity, _ in PATH_RULES if entity)
)

INTENT_SEARCH_HINTS: dict[str, str] = {
    "sick_leave": (
        "sick time policy eligibility 25 paid sick days rolling 12 months "
        "reporting Workday Out Sick statutory leave complement"
    ),
    "statutory_leave": "statutory sick leave policy country location requirements entitlements",
    "public_holiday": "public holiday policy balance accrual Workday",
    "vacation_minimum": "flexible paid time off PTO vacation minimum policy",
    "parental_leave": "parental leave policy eligibility pay duration",
    "maternity_leave": "maternity leave policy parental leave",
    "paternity_leave": "paternity leave policy parental leave",
    "family_care_leave": "caregiver sick time family care leave policy",
    "medical_insurance": "medical insurance health benefits coverage",
    "dental_insurance": "dental insurance benefits coverage",
    "vision_insurance": "vision insurance benefits coverage",
    "life_insurance": "life insurance benefits coverage",
    "disability_insurance": "disability insurance benefits coverage",
    "retirement_plan": "retirement plan pension benefits",
    "401k": "401k retirement savings plan benefits",
    "pension": "pension retirement benefits",
    "fertility_family_planning": "fertility family planning benefits",
    "employee_assistance_program": "employee assistance program EAP benefits",
    "benefit_enrollment": "benefits enrollment open enrollment eligibility",
    "cobra": "COBRA continuation coverage benefits",
    "tax_forms": "tax forms W-2 payroll tax documents",
    "payroll_specific_benefits": "payroll benefits compensation",
    "provider_or_vendor_info": "benefits provider vendor insurance carrier",
}

_ENTITY_NORMALIZE_PATTERN = re.compile(r"[^a-z0-9]+")


def _normalize_token(value: str) -> str:
    return _ENTITY_NORMALIZE_PATTERN.sub("", value.lower())


def normalize_country_code(country: str | None, country_code: str | None) -> str | None:
    if country_code:
        return country_code.upper()
    if not country:
        return None

    cleaned = country.strip().lower()
    if not cleaned:
        return None

    if cleaned in COUNTRY_NAME_TO_CODE:
        return COUNTRY_NAME_TO_CODE[cleaned]

    for name, code in sorted(COUNTRY_NAME_TO_CODE.items(), key=lambda item: len(item[0]), reverse=True):
        if cleaned == name or cleaned.startswith(f"{name} "):
            return code

    if len(cleaned) == 2 and cleaned.isalpha():
        return cleaned.upper()

    return None


def normalize_entity(entity: str | None) -> str | None:
    if not entity:
        return None

    cleaned = entity.strip()
    if not cleaned:
        return None

    for known in KNOWN_ENTITIES:
        if cleaned == known:
            return known

    normalized_input = _normalize_token(cleaned)
    for known in KNOWN_ENTITIES:
        if _normalize_token(known) == normalized_input:
            return known

    return cleaned


def _strip_terms_from_query(query: str, terms: list[str]) -> str:
    result = query
    for term in sorted({t for t in terms if t}, key=len, reverse=True):
        result = re.sub(re.escape(term), " ", result, flags=re.IGNORECASE)
    return " ".join(result.split())


def normalize_search_query(
    intent: str,
    search_query: str,
    *,
    country: str | None = None,
    country_code: str | None = None,
    entity: str | None = None,
) -> str:
    query = search_query.strip()
    if not query:
        query = INTENT_SEARCH_HINTS.get(intent, "")

    strip_terms: list[str] = []
    if country:
        strip_terms.append(country)
    if country_code:
        strip_terms.append(country_code)
    if entity:
        strip_terms.append(entity)

    cleaned = _strip_terms_from_query(query, strip_terms)
    if cleaned:
        return cleaned

    return INTENT_SEARCH_HINTS.get(intent, intent.replace("_", " "))


def _is_chinese(language: str) -> bool:
    return language.lower().startswith("zh")


def _default_clarification_question(language: str, missing_fields: list[str]) -> str:
    if _is_chinese(language):
        if missing_fields == ["country"]:
            return "请问您所在的国家或地区是哪里？"
        if missing_fields == ["entity"]:
            return "请问您所属的 GitLab 法律实体是哪家？"
        return "请补充您所在的国家/地区以及所属的 GitLab 法律实体。"

    if missing_fields == ["country"]:
        return "Which country or region are you in?"
    if missing_fields == ["entity"]:
        return "Which GitLab legal entity are you part of?"
    return "Please provide your country/region and GitLab legal entity."


def apply_requirement_rules(analysis: QueryAnalysis) -> QueryAnalysis:
    country_code = normalize_country_code(analysis.country, analysis.country_code)
    entity = normalize_entity(analysis.entity)

    missing_fields: list[str] = []
    if analysis.intent in COUNTRY_REQUIRED_INTENTS and not country_code:
        missing_fields.append("country")
    if analysis.intent in ENTITY_REQUIRED_INTENTS and not entity:
        missing_fields.append("entity")

    needs_clarification = bool(missing_fields)
    clarification_question = analysis.clarification_question
    if needs_clarification and not clarification_question:
        clarification_question = _default_clarification_question(analysis.language, missing_fields)

    search_query = normalize_search_query(
        analysis.intent,
        analysis.search_query,
        country=analysis.country,
        country_code=country_code,
        entity=entity,
    )

    return QueryAnalysis(
        language=analysis.language,
        intent=analysis.intent,
        country=analysis.country,
        country_code=country_code,
        entity=entity,
        needs_clarification=needs_clarification,
        missing_fields=missing_fields,
        clarification_question=clarification_question if needs_clarification else None,
        search_query=search_query,
    )
