import json
import logging
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from ask import generate_answer
from config import BASE_DIR

logger = logging.getLogger(__name__)

EVAL_FILE = BASE_DIR / "eval" / "questions.json"


@dataclass
class EvalCase:
    question: str
    expected_source: str
    expected_section: str
    expected_keywords: list[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Self:
        required_fields = ("question", "expected_source", "expected_section", "expected_keywords")
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Eval case missing required fields: {', '.join(missing)}")

        expected_keywords = data["expected_keywords"]
        if not isinstance(expected_keywords, list):
            raise ValueError("Eval case field 'expected_keywords' must be a list")

        return cls(
            question=str(data["question"]),
            expected_source=str(data["expected_source"]),
            expected_section=str(data["expected_section"]),
            expected_keywords=[str(keyword) for keyword in expected_keywords],
        )


@dataclass
class EvalResult:
    question: str
    answer: str
    expected_source: str
    expected_section: str
    top_source: str | None
    top_section: str | None
    source_hit: bool
    section_hit: bool
    keyword_hit_count: int
    keyword_total: int
    latency_ms: float


def load_eval_cases() -> list[EvalCase]:
    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    cases = [EvalCase.from_dict(case) for case in data]
    logger.info("eval cases loaded count=%d file=%s", len(cases), EVAL_FILE)
    return cases


def calculate_keyword_hit_count(answer: str, expected_keywords: list[str]) -> int:
    return sum(1 for keyword in expected_keywords if keyword in answer)


def evaluate_case(case: EvalCase) -> EvalResult:
    start_time = time.perf_counter()
    answer, matches = generate_answer(case.question)
    latency_ms = (time.perf_counter() - start_time) * 1000
    top_match = matches[0] if matches else None
    top_source = top_match.metadata.document if top_match else None
    top_section = top_match.metadata.section if top_match else None

    source_hit = top_source == case.expected_source
    section_hit = top_section == case.expected_section

    keyword_hit_count = calculate_keyword_hit_count(answer or "", case.expected_keywords)
    keyword_total = len(case.expected_keywords)
    passed = source_hit and keyword_hit_count > 0

    logger.info(
        "eval case done status=%s question=%r source_hit=%s section_hit=%s keyword_hit=%d/%d latency_ms=%.1f top_source=%s",
        "PASS" if passed else "FAIL",
        case.question,
        source_hit,
        section_hit,
        keyword_hit_count,
        keyword_total,
        latency_ms,
        top_source,
    )

    return EvalResult(
        question=case.question,
        answer=answer or "",
        expected_source=case.expected_source,
        expected_section=case.expected_section,
        top_source=top_source,
        top_section=top_section,
        source_hit=source_hit,
        section_hit=section_hit,
        keyword_hit_count=keyword_hit_count,
        keyword_total=keyword_total,
        latency_ms=latency_ms)


def print_eval_result(result: EvalResult):    
    status = "PASS" if result.source_hit and result.keyword_hit_count > 0 else "FAIL"
    print("=" * 80)
    print(f" {status}")

    print(f"Question: {result.question}")
    print(f"Answer: {result.answer}")
    print(f"Expected Source: {result.expected_source}")
    print(f"Expected Section: {result.expected_section}")
    print(f"Top Source: {result.top_source}")
    print(f"Top Section: {result.top_section}")
    print(f"Source Hit: {result.source_hit}")
    print(f"Section Hit: {result.section_hit}")
    print(f"Keyword Hit Count: {result.keyword_hit_count}")
    print(f"Keyword Total: {result.keyword_total}")
    print(f"Latency: {result.latency_ms}ms")


def main():
    from logging_config import setup_logging

    setup_logging()
    logger.info("eval run start")
    cases = load_eval_cases()
    total = len(cases)
    pass_count = 0
    fail_count = 0
    for index, case in enumerate(cases, start=1):
        logger.info("eval case start index=%d/%d question=%r", index, total, case.question)
        result = evaluate_case(case)
        print_eval_result(result)
        if result.source_hit and result.keyword_hit_count > 0:
            pass_count += 1
        else:
            fail_count += 1

    pass_rate = pass_count / total * 100 if total else 0.0
    logger.info(
        "eval run complete total=%d pass=%d fail=%d pass_rate=%.2f%%",
        total,
        pass_count,
        fail_count,
        pass_rate,
    )

    print("=" * 80)
    print(f"Total: {total}")
    print(f"Pass: {pass_count}")
    print(f"Fail: {fail_count}")
    print(f"Pass Rate: {pass_rate:.2f}%")

if __name__ == "__main__":
    main()