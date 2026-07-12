---
title: Localization Engineering
description: Technical details of GitLab's localization infrastructure and engineering processes.
---

Technical overview of GitLab's localization infrastructure and engineering processes across documentation and product interfaces. Includes translation environments, branch management, development workflows, and preview systems for internationalized content.

For the full localization technology stack, see [Localization Technology Management at GitLab](/handbook/marketing/localization/localization_technology/). For product documentation localization architecture and workflows, see [GitLab Product Documentation Localization](/handbook/marketing/localization/tech_docs_localization/).

## Team

- [Rasam Hossain](https://gitlab.com/rasamhossain), Senior Fullstack Engineer
- [Lauren Barker](https://gitlab.com/laurenbarker), Staff Fullstack Engineer
- [Oleksandr Pysaryuk](https://gitlab.com/opysaryuk), Senior Manager, Globalization Technology

### Communication channels

- `#localization-engineering`: localization engineering team working channel
- `#localization-alerts`: automated failure reports for fork sync pipelines and Translation MR notifications
- `#spartan-software`: direct communication with Spartan Software engineering team
- `#argos_multilingual`: direct communication with Argos Multilingual engineering team

For the full list of localization Slack channels, see the [Localization handbook](/handbook/marketing/localization/#contact-us).

## Scope

The Localization Engineering team owns and maintains the infrastructure that enables GitLab content and product to be delivered in multiple languages.

**Content streams we support:**

- **GDATP / [GitLab Translation Agent](https://gitlab.com/explore/ai-catalog/agents/532/)**: GitLab-native AI translation platform built on the Duo Agent Platform. It is used for translating ad hoc and high-impact marketing content, such as pricing page, landing pages, blogs, and coordinated multilingual launches. Content Managers, Program Managers and Engineers use GDATP as a self-serve translation tool. The engineering team owns the platform, system prompt architecture, language specifications, and workflow development.
- **Product documentation** (docs.gitlab.com): localization architecture with internationalization layer and connected tooling, such as Argo orchestration platform, Phrase TMS, and AI-powered translation. The engineering team owns the fork sync automation, Translation MR creation, upstream push process and automation, Hugo internationalization configuration, and continuous localization pipeline development. For full architecture details, see [GitLab Product Documentation Localization](/handbook/marketing/localization/tech_docs_localization/).
- **Marketing website** (about.gitlab.com): continuous localization across 6 languages through GDATP for net new pages and high-profile content, and the Argo-Phrase pipeline for volume and async updates.
- **Product UI**: community-driven translation through [Crowdin](https://docs.gitlab.com/development/i18n/), supported by the [GitLab String Search](https://gitlab.com/gitlab-com/localization/gitlab-string-search) tool and [Crowdin Automation](https://gitlab.com/gitlab-com/localization/crowdin-automation) scripts.

## Iteration process

We start our iteration on a Tuesday. We release throughout the iteration. Iterations are 2 weeks long. See our [Localization engineering iterations here](https://gitlab.com/groups/gitlab-com/localization/-/cadences/).

We use two boards to track engineering work:

- [By Assignee](https://gitlab.com/groups/gitlab-com/localization/-/boards/9140637): shows all work items with `~"L10n-engineering"` label, grouped by team member
- [By Status](https://gitlab.com/groups/gitlab-com/localization/-/boards/11195951): shows workflow progression through Refinement -> Ready for development -> In dev -> In review -> Complete

## Review workflow

The process of reviewing merge requests by the Localization Engineering team aligns with the GitLab [Code Review Guidelines](https://docs.gitlab.com/development/code_review/).

Localization Engineering team reviews each other's merge requests and [Translation MRs](https://gitlab.com/gitlab-com/localization/argo-gitlab-integration/-/blob/main/doc/en-US/merge_requests.md?ref_type=heads#translation-mr). Translation MRs are created by [@gitlab-argo-bot](https://gitlab.com/gitlab-argo-bot) when translations are complete in Argo for the Marketing website and GitLab product documentation.

Localization Engineering helps review MRs that are authored in Decap CMS by the Localization Content Managers who own and maintain [Blog](https://about.gitlab.com/blog/) in multiple languages. Blog update MRs from Decap are typically content-only changes that help with deployment agility and can use lightweight review processes. Content Managers may request a review from a Localization Engineer or a [Digital Experience (DEX)](/handbook/marketing/digital-experience/) engineer for complex changes, code, or troubleshooting.

### Vendor engineering partnerships

- [Spartan Software](https://gitlab.com/groups/gitlab-com/localization/-/work_items/60) - Argo orchestration platform development and maintenance
- [Argos Multilingual](https://gitlab.com/groups/gitlab-com/localization/-/work_items/60) - AI translation pipelines and projects, linguistic services, translation management systems configuration, Crowdin engineering
