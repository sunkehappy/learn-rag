# Handbook Eval Questions and Pytest Markers

## Overview

Handbook Q&A evaluation lives entirely in **pytest**. There is no separate `eval.py` runner.

| Layer | Command | LLM? | Data |
|-------|---------|------|------|
| Unit (default) | `pytest` | No | `tests/`, `tests/fixtures/` |
| Retrieval | `pytest -m retrieval` | Embedding only | [`eval/handbook_retrieval.json`](../eval/handbook_retrieval.json) (~200+) |
| RAG smoke | `pytest -m llm` | Chat + embedding | [`eval/handbook_rag_smoke.json`](../eval/handbook_rag_smoke.json) (~12) |

Default `pytest` uses `addopts = -m "not retrieval and not llm"` so CI stays fast.

## Retrieval case schema

```json
{
  "id": "pto-001",
  "topic": "time_off",
  "question": "病假最多有多少天？",
  "search_query": "sick time policy 25 paid sick days rolling 12 months",
  "expected_source": "gitlab_handbook/people-group/time-off-and-absence/time-off-types.md",
  "expected_section": "Sick Time",
  "expected_country_code": null,
  "expected_entity": null
}
```

- `question`: 用户侧问法（多为中文），便于阅读与未来答案评测。
- `search_query`: **向量检索专用**英文关键词（对齐 handbook 用语）。`-m retrieval` 用该字段调用 `search_chunks`；缺省时才退回 `question`。
- `expected_source` 必须等于 Chroma metadata `relative_path`（`docs/` 下相对路径）。
- `expected_country_code` / `expected_entity` 只用于 metadata 过滤（多级 specific → general → broad），**不要**写进 `search_query`。

## 出题规范（避免假覆盖）

禁止：

- `销售相关：_index？` / `产品相关：_index？` 等模板
- 多条用例共用同一 `question` 却期望不同 `expected_source`
- 用 Hugo 文件名 `_index` 当主题
- 给 `search_query` 追加「整主题词袋」后缀（如每条 eng 题都挂 `code review engineering workflow iteration`）——会污染 embedding
- `search_query` 过短/过泛（单字如 `Email` / `Scope` / `Collaboration`）——与词袋一样会漂到无关文档
- 以几乎无正文的 `_index`、纯 `include`、空壳页作为 `expected_source`

推荐：

- 每条题对应**有实质正文**的章节；`search_query` 只用**该页专有**英文术语
- `country_code` / `entity` 只做 metadata 过滤，与 `expected_source` 一致（例如 US 过滤应对美国 leave 页，而非全球 time-off 页）
- 同名多文档时：改期望为检索会稳定命中的那篇，或把 query 写到足以区分
- 主题覆盖靠**合格题配额**，不靠灌水数量

## 常用命令

```bash
pytest                              # 快：仅单测
pytest -o addopts= -m "not llm"     # 单测 + retrieval（跳过 smoke）
pytest -o addopts= -m retrieval     # 仅检索题库
pytest -m llm                       # RAG smoke（慢）
```

## Topic coverage (approx.)

People / time-off / benefits / values, culture / hiring / communication / finance, engineering workflow + light architecture, security standards, support workflows, sales / CS / product.

## Intent fixtures (no LLM)

[`tests/fixtures/intent_cases.json`](../tests/fixtures/intent_cases.json) drives parameterized rules tests in `tests/test_intent_fixtures.py`.

## Requirements

- Retrieval: local Chroma index + `QWEN_API_KEY` + `QWEN_EMBEDDING_MODEL`
- LLM smoke: also `QWEN_MODEL`
