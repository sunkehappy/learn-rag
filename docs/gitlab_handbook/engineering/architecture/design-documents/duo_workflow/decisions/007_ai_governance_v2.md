---
title: "AI Governance Architecture: v2 Deferred Capabilities"
status: proposed
creation-date: "2026-03-13"
authors: [ "@dbernardi" ]
coach: [  ]
approvers: [ ]
owning-stage: "~devops::ai_powered"
participating-stages: []
toc_hide: true
description: "Tracks capabilities deferred from the v1 AI Governance rules engine, glob/regex argument matching, audit-only mode, compliance presets, and user-level opt-in."
---

{{< engineering/design-document-header >}}

## Overview

This document tracks capabilities deferred from the v1 AI Governance rules engine ([AI Governance Architecture: Persistent Tool Rules Engine](007_ai_governance.md)).

These are not speculative features — they are known needs that were scoped out of v1 to keep the initial delivery focused on the core governance model and hierarchical resolution.

---

## 1. Glob and Regex Argument Matching

**What:** A `match_type` column on `ai_tool_rules` that controls how `tool_arguments` is matched: `0` = exact (v1, current), `1` = glob, `2` = regex.

**Why deferred:** v1 stores `tool_arguments` on the table but does not use it in resolution. Glob and regex introduce complexity in the resolver (specificity-based precedence — see item 6) and in the UI (users need to understand matching semantics).

**When to prioritise:** When users need rules like "allow `read_file` for anything under `/src/*`" or "deny `run_command` matching `rm -rf.*`".

**Schema addition:**

```ruby
t.integer :match_type, default: 0, limit: 2  # 0: exact, 1: glob, 2: regex
```

---

## 2. GIN Index on `tool_arguments`

**What:** A PostgreSQL GIN index on the `tool_arguments` JSONB column.

**Why deferred:** GIN indexes support containment operators (`@>`, `?`, `?|`) which are useful for glob/regex matching where the resolver needs to find rules whose argument patterns contain or overlap with the provided arguments. In v1, `tool_arguments` is stored but not used in resolution.

**When to prioritise:** Ships alongside glob/regex matching (item 2).

**Schema addition:**

```ruby
add_index :ai_tool_rules, :tool_arguments, using: :gin
```

---

## 3. Audit-Only Mode

**What:** An `audit_only` boolean column on `ai_tool_rules`. When true, governance decisions are logged but not enforced — the tool proceeds as if no rule existed, but the audit trail records what *would* have happened.

**Why deferred:** Requires integration with the audit logging pipeline to be meaningful. Also requires careful UX design — users need to understand that audit-only rules are not protecting them.

**When to prioritise:** When security teams request the ability to test new policies in production without disrupting developer workflows. Likely needed before any large-scale compliance preset rollout (item 5).

**Schema addition:**

```ruby
t.boolean :audit_only, default: false, null: false
```

---

## 4. Compliance Presets

**What:** Pre-built rule templates (for example, SOC2, HIPAA) that administrators can apply to instantly create `deny` rules for specific tools across an entire organisation.

**Why deferred:** Requires bulk mutations (item 1) and likely audit-only mode (item 4) for safe rollout. Also requires legal/compliance review to ensure presets accurately reflect framework requirements.

**When to prioritise:** When Enterprise customers require one-click compliance posture for AI tool governance. This is the capstone feature that ties together items 1 and 4.

---

## 5. Specificity-Based Precedence

**What:** When multiple rules apply to the same tool (for example, a glob rule for `/etc/*` and a more specific rule for `/etc/passwd`), the resolver prioritises the most specific argument match before applying hierarchical logic.

**Why deferred:** Only meaningful when glob/regex matching (item 2) is supported. With no argument matching in v1, a rule either matches the tool name or it doesn't — there is no ambiguity to resolve.

**When to prioritise:** Ships alongside glob/regex matching (item 2). The resolver logic must be designed together with the matching semantics.

---

## 6. Denied Tool Prompt Filtering

**What:** When a tool is blocked by a `deny` rule, exclude it from the tool list sent to the LLM entirely. The model never sees tools it cannot use.

**Note:** In v1, denied tools are already stripped from the toolset before DWS presents tools to the LLM — the model never sees denied tools. This item tracks the deeper integration of filtering at the prompt assembly level within DWS rather than at the toolset level.

**Why deferred:** Prompt-level filtering requires integration with the tool list assembly pipeline that constructs the LLM's system prompt. This is a deeper integration than the current toolset-level filtering.

**When to prioritise:** When the current toolset-level filtering proves insufficient for a particular surface or workflow type.

---

## 7. User-Level Auto-Approve Opt-In

**What:** Allow individual users to opt into auto-approve for specific tools, bypassing the approval prompt for tools they've explicitly pre-approved. This requires adding `user_id` as a scoping column to `ai_tool_rules` and a third resolution pass after namespace and project rules.

**Why deferred:** The primary use case is IDE/Editor Extensions — a user who is frequently prompted to approve a specific tool in their local workflow can opt into auto-approve for that tool. From a governance perspective, users should not be able to bypass HITL enforcement set by an admin. The intended model is that admins can unlock user-level settings, and users can then set their own preferences within the bounds of the admin policy. This is post-GA scope.

**When to prioritise:** When Editor Extensions surface user-facing HITL friction that warrants a user-level opt-in mechanism.

**Schema addition:**

```ruby
t.references :user, null: true, foreign_key: { on_delete: :cascade }
```

---

## 8. Instance-Level Rules

**What:** Rules set at the instance level, above the top-level group (TLG), applying a single policy across all groups on a self-managed instance.

**Why deferred:** The current TLG-level rules already cascade to all projects within a group, covering most enterprise use cases. Instance-level rules are needed for self-managed customers who want a single policy across all groups on an instance. Post-GA scope.

**When to prioritise:** When self-managed customers require instance-wide governance policies that cannot be delegated to individual group owners.

---

## 9. Traversal IDs Single Query Optimisation

**What:** Use GitLab's `traversal_ids` (materialised path on namespaces) to fetch all rules across the entire ancestor hierarchy in a single query, replacing the current two-query approach (separate queries for namespace and project rules).

**Why deferred:** The current two-query approach is clean and easy to reason about. At the current scale of the rule table and tool registry this is efficient. Production data is needed to determine whether this optimisation is warranted.

**When to prioritise:** When production query frequency or deep group hierarchies indicate the two-query approach is a performance bottleneck.
