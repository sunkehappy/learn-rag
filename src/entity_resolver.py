from __future__ import annotations

import re
from dataclasses import dataclass

FLAG_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F3F4"
    "\uFE0F"
    "\u200D"
    "]",
    flags=re.UNICODE,
)

COUNTRY_NAME_TO_CODE: dict[str, str] = {
    "austria": "AT",
    "belgium": "BE",
    "brazil": "BR",
    "chile": "CL",
    "costa rica": "CR",
    "denmark": "DK",
    "kenya": "KE",
    "latvia": "LV",
    "mexico": "MX",
    "philippines": "PH",
    "south africa": "ZA",
    "united arab emirates": "AE",
    "uae": "AE",
    "sweden": "SE",
    "italy": "IT",
    "switzerland": "CH",
    "hungary": "HU",
    "luxembourg": "LU",
    "spain": "ES",
    "germany": "DE",
    "india": "IN",
    "israel": "IL",
    "france": "FR",
    "ireland": "IE",
    "united kingdom": "GB",
    "uk": "GB",
    "canada": "CA",
    "united states": "US",
    "usa": "US",
    "australia": "AU",
    "new zealand": "NZ",
    "japan": "JP",
    "korea": "KR",
    "south korea": "KR",
    "singapore": "SG",
    "netherlands": "NL",
    "finland": "FI",
}

MULTI_COUNTRY_FILES = frozenset(
    {
        "gitlab_handbook/total-rewards/benefits/general-and-entity-benefits/global-expansion.md",
        "gitlab_handbook/total-rewards/benefits/general-and-entity-benefits/remote-com.md",
    }
)

# Longer patterns first to avoid partial matches (e.g. new-zealand before zealand).
PATH_RULES: list[tuple[str, str, str]] = [
    ("entity/iberia-srl-spain.md", "GitLab Iberia s.r.l.", "ES"),
    ("entity/gmbh-germany.md", "GitLab GmbH", "DE"),
    ("entity/india-pvt-ltd.md", "GitLab India Pvt Ltd", "IN"),
    ("entity/israel-ltd.md", "GitLab Israel Ltd.", "IL"),
    ("bv-benefits-belgium.md", "GitLab BV", "BE"),
    ("bv-benefits-netherlands.md", "GitLab BV", "NL"),
    ("bv-benefits-finland.md", "GitLab BV", "FI"),
    ("france-sas.md", "GitLab France S.A.S.", "FR"),
    ("people-policies/france-sas/", "GitLab France S.A.S.", "FR"),
    ("ltd-benefits-uk.md", "GitLab LTD", "GB"),
    ("gitlab-ireland-ltd.md", "GitLab Ireland LTD", "IE"),
    ("people-policies/ireland-ltd/", "GitLab Ireland LTD", "IE"),
    ("canada-corp-benefits.md", "GitLab Canada Corp.", "CA"),
    ("inc-usa.md", "GitLab Inc.", "US"),
    ("inc-benefits-us/", "GitLab Inc.", "US"),
    ("leave-of-absence/us.md", "GitLab Inc.", "US"),
    ("pty-benefits-australia.md", "GitLab PTY", "AU"),
    ("pty-benefits-new-zealand.md", "GitLab PTY", "NZ"),
    ("gitlab-gk.md", "GitLab GK", "JP"),
    ("korea-ltd-benefits.md", "GitLab Korea LTD", "KR"),
    ("singapore-pte-ltd.md", "GitLab Singapore Pte Ltd", "SG"),
    ("people-policies/india-ltd/", "GitLab India Pvt Ltd", "IN"),
    (
        "total-rewards/benefits/general-and-entity-benefits/global-expansion.md",
        "Global Expansion",
        "",
    ),
    (
        "total-rewards/benefits/general-and-entity-benefits/remote-com.md",
        "Remote.com",
        "",
    ),
]


@dataclass
class EntityInfo:
    entity: str = ""
    country_code: str = ""


def _normalize_path(relative_path: str) -> str:
    return relative_path.replace("\\", "/").lower()


def resolve_from_path(relative_path: str) -> EntityInfo:
    normalized = _normalize_path(relative_path)
    for pattern, entity, country_code in PATH_RULES:
        if pattern in normalized:
            return EntityInfo(entity=entity, country_code=country_code)
    return EntityInfo()


def _clean_section_title(section: str) -> str:
    cleaned = section.strip()
    cleaned = cleaned.replace("**", "")
    cleaned = FLAG_EMOJI_PATTERN.sub("", cleaned)
    return " ".join(cleaned.split())


def _country_code_from_section(section: str) -> str:
    cleaned = _clean_section_title(section).lower()
    if not cleaned:
        return ""

    if cleaned in COUNTRY_NAME_TO_CODE:
        return COUNTRY_NAME_TO_CODE[cleaned]

    for name, code in sorted(COUNTRY_NAME_TO_CODE.items(), key=lambda item: len(item[0]), reverse=True):
        if cleaned == name or cleaned.startswith(f"{name} "):
            return code

    return ""


def _is_multi_country_file(relative_path: str) -> bool:
    normalized = _normalize_path(relative_path)
    return any(marker in normalized for marker in MULTI_COUNTRY_FILES)


def resolve_from_section(base: EntityInfo, section: str, relative_path: str = "") -> EntityInfo:
    if base.country_code:
        return base

    if relative_path and not _is_multi_country_file(relative_path):
        return base

    country_code = _country_code_from_section(section)
    if not country_code:
        return base

    return EntityInfo(entity=base.entity, country_code=country_code)
