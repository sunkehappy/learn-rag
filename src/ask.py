import logging
import os
import sys
import time
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from config import BASE_URL, QWEN_API_KEY, QWEN_MODEL, validate_config
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
"""


def build_context(matches: list[dict[str, Any]]):
    context_parts: list[str] = []
    for index, match in enumerate(matches, start=1):
        metadata = match['metadata']
        context_parts.append(
          f"""
[Source {index}]
[Document: {metadata['document']}]
[Category: {metadata['category']}]
[Title: {metadata['title']}]
[Content: {match['text']}]
          """
        )
    return "\n".join(context_parts)


def build_user_input(question: str, context: str):
    return f"""
请根据下面的知识库资料回答用户的问题
用户问题: {question}
知识库资料: {context}
"""


def generate_answer(question: str, top_k: int = 3):
    logger.info("generate answer start question=%r top_k=%d", question, top_k)
    start_time = time.perf_counter()

    matches = search_chunks(question, top_k)
    if not matches:
        logger.warning("generate answer no context question=%r", question)

    context = build_context(matches)
    user_input = build_user_input(question, context)

    llm_start = time.perf_counter()
    response = client.chat.completions.create(
        model=str(QWEN_MODEL),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
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


def print_source(matches: list[dict[str, Any]]):
    for match in matches:
        metadata = match['metadata']
        print(f"Source: {metadata['document']}")
        print(f"Category: {metadata['category']}")
        print(f"Title: {metadata['title']}")
        print(f"Content: {match['text']}")
        print("-" * 100)


def ask_once(question: str):
    answer, matches = generate_answer(question)
    logger.info("ask once complete question=%r", question)
    print(f"Answer: {answer}")
    print_source(matches)
    return answer


def interactive_mode():
    while True:
        question = input("请输入问题: ").strip()
        if not question:
            continue
        if question.lower() in ["exit", "quit", "q"]:
            break
        ask_once(question)


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    interactive_mode()