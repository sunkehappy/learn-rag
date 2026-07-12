import logging
import time
import uuid

from dotenv import load_dotenv
from openai import OpenAI

from config import BASE_URL, QWEN_API_KEY, QWEN_MODEL
from logging_config import log_progress
from models import AskResult, ClarificationSession, SearchMatch
from query_analyzer import analyze_question, merge_clarification
from session_store import get_session_store
from vector_store import search_chunks

load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(api_key=QWEN_API_KEY, base_url=BASE_URL)


SYSTEM_PROMPT = """
You are SmartKB, an enterprise knowledge base assistant.

Rules:
1. Answer only based on the provided context.
2. If the context does not contain enough information, say: "知识库中没有找到明确依据。"
3. Do not invent company policies, API behavior, numbers, deadlines, or approval rules.
4. Answer in Chinese.
5. Keep the answer concise and practical.
6. When possible, mention which source supports the answer.
7. If the user asked about a specific country or GitLab entity but the context only contains GitLab global/general policies (not country- or entity-specific), clearly state that the handbook has no dedicated section for that country/entity and answer based on the global policy in the context. Mention that local statutory requirements or employment contract may also apply.
"""


def build_context(matches: list[SearchMatch]):
    context_parts: list[str] = []
    for index, match in enumerate(matches, start=1):
        metadata = match.metadata
        context_parts.append(
          f"""
[Source {index}]
[Document: {metadata.document}]
[Category: {metadata.category}]
[Title: {metadata.title}]
[Content: {match.text}]
          """
        )
    return "\n".join(context_parts)


def build_user_input(
    question: str,
    context: str,
    *,
    country: str | None = None,
    country_code: str | None = None,
    entity: str | None = None,
):
    lines = [f"用户问题: {question}"]
    if country or country_code:
        location = country or country_code or ""
        if country and country_code:
            location = f"{country} ({country_code})"
        lines.append(f"用户所在国家/地区: {location}")
    if entity:
        lines.append(f"用户所属 GitLab 法律实体: {entity}")
    lines.append(f"知识库资料: {context}")
    return "\n".join(lines)


def generate_answer(
    question: str,
    top_k: int = 3,
    *,
    country_code: str | None = None,
    entity: str | None = None,
    search_query: str | None = None,
    country: str | None = None,
):
    logger.info(
        "generate answer start question=%r top_k=%d country_code=%r entity=%r",
        question,
        top_k,
        country_code,
        entity,
    )
    start_time = time.perf_counter()

    query = search_query or question
    matches = search_chunks(query, top_k, country_code=country_code, entity=entity)
    context = build_context(matches)
    user_input = build_user_input(
        question,
        context,
        country=country,
        country_code=country_code,
        entity=entity,
    )

    llm_start = time.perf_counter()
    response = client.chat.completions.create(
        model=str(QWEN_MODEL),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请根据下面的知识库资料回答用户的问题\n{user_input}"},
        ],
    )
    llm_latency_ms = (time.perf_counter() - llm_start) * 1000
    answer = response.choices[0].message.content
    total_latency_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "generate answer done match_count=%d answer_length=%d llm_latency_ms=%.1f total_latency_ms=%.1f",
        len(matches),
        len(answer or ""),
        llm_latency_ms,
        total_latency_ms,
    )
    return answer, matches


def print_source(matches: list[SearchMatch]):
    for match in matches:
        metadata = match.metadata
        print(f"Source: {metadata.document}")
        print(f"Category: {metadata.category}")
        print(f"Title: {metadata.title}")
        print(f"Content: {match.text}")
        print("-" * 100)


def handle_question(session_id: str, question: str, top_k: int = 3) -> AskResult:
    total_start = time.perf_counter()
    log_progress(f"开始处理问题 (session={session_id[:8]}...)")

    store = get_session_store()
    log_progress("检查 Redis 是否有待澄清会话...")
    pending = store.get_session(session_id)

    if pending:
        logger.info(
            "pending session found session_id=%s original_question=%r intent=%s",
            session_id,
            pending.original_question,
            pending.intent,
        )
        log_progress("发现待澄清会话，合并您的回复...")
        analysis = merge_clarification(pending, question)
        original_question = pending.original_question
    else:
        logger.info("no pending session session_id=%s", session_id)
        log_progress("无待澄清会话，开始意图分析...")
        analysis = analyze_question(question)
        original_question = question

    if analysis.needs_clarification:
        log_progress(
            f"需要补充信息: {analysis.missing_fields}，正在保存会话到 Redis..."
        )
        session = ClarificationSession.from_analysis(session_id, original_question, analysis)
        store.save_session(session)
        total_ms = (time.perf_counter() - total_start) * 1000
        logger.info(
            "clarification needed missing_fields=%s total_latency_ms=%.1f",
            analysis.missing_fields,
            total_ms,
        )
        log_progress(f"处理完成 ({total_ms:.0f}ms)，等待用户补充")
        return AskResult(
            needs_clarification=True,
            clarification_question=analysis.clarification_question,
            answer=None,
            analysis=analysis,
        )

    log_progress("信息齐全，开始向量检索并生成答案...")
    store.delete_session(session_id)
    answer, matches = generate_answer(
        original_question,
        top_k,
        country_code=analysis.country_code,
        entity=analysis.entity,
        search_query=analysis.search_query or None,
        country=analysis.country,
    )
    total_ms = (time.perf_counter() - total_start) * 1000
    log_progress(f"处理完成 ({total_ms:.0f}ms)")
    return AskResult(
        needs_clarification=False,
        clarification_question=None,
        answer=answer,
        matches=matches,
        analysis=analysis,
    )


def ask_once(question: str, session_id: str | None = None):
    resolved_session_id = session_id or str(uuid.uuid4())
    result = handle_question(resolved_session_id, question)
    logger.info("ask once complete question=%r needs_clarification=%s", question, result.needs_clarification)

    if result.needs_clarification:
        print(f"Clarification: {result.clarification_question}")
        return result

    print(f"Answer: {result.answer}")
    print_source(result.matches)
    return result


def interactive_mode():
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")

    awaiting_clarification = False
    while True:
        prompt = "请输入: " if awaiting_clarification else "请输入问题: "
        question = input(prompt).strip()
        if not question:
            continue
        if question.lower() in ["exit", "quit", "q"]:
            break

        result = handle_question(session_id, question)
        if result.needs_clarification:
            print(f"Clarification: {result.clarification_question}")
            awaiting_clarification = True
            continue

        awaiting_clarification = False
        print(f"Answer: {result.answer}")
        print_source(result.matches)


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    interactive_mode()
