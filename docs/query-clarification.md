# Query Clarification and Multi-turn Sessions

## Overview

Before answering, SmartKB runs a **query analyzer** to detect intent and extract `country` / `entity`. Some intents require one or both fields. If missing, the assistant asks a clarification question and stores session state in **Redis** until the user replies.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | Yes | — | Redis connection URL, e.g. `redis://localhost:6379/0` |
| `SESSION_TTL_SECONDS` | No | `1800` | Clarification session TTL (30 minutes) |

`validate_config()` also requires `REDIS_URL`.

## Intent Groups

**Country required:**

- `sick_leave`, `statutory_leave`, `public_holiday`, `vacation_minimum`
- `parental_leave`, `maternity_leave`, `paternity_leave`, `family_care_leave`

**Entity required:**

- `medical_insurance`, `dental_insurance`, `vision_insurance`, `life_insurance`
- `disability_insurance`, `retirement_plan`, `401k`, `pension`
- `fertility_family_planning`, `employee_assistance_program`, `benefit_enrollment`
- `cobra`, `tax_forms`, `payroll_specific_benefits`, `provider_or_vendor_info`

## CLI Multi-turn Example

```bash
export REDIS_URL=redis://localhost:6379/0
python src/ask.py
```

```
Session ID: 8f3c2a1b-...
请输入问题: 病假怎么请？
Clarification: 请问您所在的国家或地区是哪里？
请输入问题: Spain
Answer: ...
```

Flow:

1. First message → analyzer detects `sick_leave`, missing country → save session to Redis
2. Second message → merge with stored session → `country_code=ES` → search with filter → answer
3. Session deleted after successful answer

## Redis Key Format

```
smartkb:session:{session_id}
```

Value: JSON-serialized `ClarificationSession`.

## Search Filtering

`search_query` is English intent keywords for vector retrieval only. Country and entity names are **not** included in `search_query`; they are used as Chroma metadata filters separately.

Tiered retrieval in `search_chunks()`:

1. **specific** — filter by user's `country_code` / `entity`
2. **general** — filter by empty `country_code` or `entity` (global handbook policies, e.g. `time-off-types.md`)
3. **broad** — no filter

If the user asked about a country with no dedicated handbook section (e.g. China sick leave), tier 2 returns the global Sick Time policy. The answer LLM is instructed to note the absence of country-specific content.

## Key Modules

| File | Role |
|------|------|
| `src/query_analyzer.py` | LLM intent/country/entity extraction |
| `src/intent_config.py` | Hard-coded intent rules + normalization |
| `src/session_store.py` | Redis session persistence |
| `src/ask.py` | `handle_question()` orchestration |

## Tests

```bash
pytest                          # unit only (default)
pytest -m retrieval             # handbook retrieval bank
pytest -m llm                   # RAG smoke
```

See also [`docs/eval-handbook.md`](eval-handbook.md).
