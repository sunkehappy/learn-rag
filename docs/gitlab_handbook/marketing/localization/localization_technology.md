---
title: "Localization Technology Management at GitLab"
description: "Comprehensive overview of GitLab's localization technology ecosystem, workflows, and AI-powered translation infrastructure enabling global content delivery."
---

## Mission and vision

[Localization technology at GitLab - mission and vision](https://gitlab.com/gitlab-com/localization/localization-team/-/issues/453)

## Localization technology stack - Overview

The Localization team manages a sophisticated technology ecosystem designed to automate and enhance translation workflows across GitLab's global content. Our technology stack consists of purpose-built custom solutions, commercial Language Technology Platforms (LTPs), and emerging AI-powered services that collectively enable localization of GitLab's product UI, marketing content, and product documentation.

## Localization technology stack - Components

See more details and visuals in the [Localization management technology stack at GitLab](https://gitlab.com/gitlab-com/localization/localization-team/-/issues/452) issue.

### Tools inventory

Commercial Tools:

- Argo as a platform, aka Request Management System and its components (by Spartan Software)
- Phrase TMS (by Phrase)
- TranslationOS (TOS) and Matecat (by Translated)
- Crowdin (by Crowdin)

At GitLab:

- Google Cloud Platform sandbox with ai-machine-transl project
- Anthropic Claude UI with emerging standalone projects

### Orchestration platform

[Argo](https://gitlab.com/groups/gitlab-com/localization/-/epics/35) - Localization Request Management system serving as the central orchestration hub, consisting of the following specialized services:

- Argo web client (UI) - Argo web UI used by localization program managers, stakeholders and vendors
- Argo web services - backend/API orchestration engine  
- Argo-Phrase integration - service for GitLab product docs localization workflow
- Argo-TOS integration - service for marketing localization workflow
- Argo-GitLab integration - service handling webhooks
- Argo GitLab agent - service for preprocessing GitLab product docs markdown files
- Database & reporting - business analytics and tracking, available within Argo UI

### GitLab integration services

- [Argo GitLab Integration](https://gitlab.com/gitlab-com/localization/argo-gitlab-integration) - [GitLab Translation Service](/handbook/engineering/architecture/design-documents/gitlab_translation_service/) that bridges GitLab projects with translation management systems through webhook automation and Translation MR delivery
- [Argo GitLab Agent](https://gitlab.com/gitlab-com/localization/argo-gitlab-agent) - specialized service for GitLab markdown preprocessing and other content processing tasks

### Integrations with Language Technology Platforms

- [TranslationOS integration](https://gitlab.com/groups/gitlab-com/localization/-/epics/92) - for semi-automated translation workflow for marketing content, via Translated
- [Phrase TMS integration](https://gitlab.com/groups/gitlab-com/localization/-/epics/95) - for automated product documentation translation via Argos Multilingual, with AI enhancement capabilities
- [Crowdin integration](/handbook/business-technology/tech-stack/#crowdincom) - for community-driven product UI translation

### AI-powered translation

- [Tech Docs AI-powered translation](https://gitlab.com/gitlab-com/localization/tech-docs-ai-powered-translation) - Google Cloud Vertex AI with Gemini LLM processing GitLab product documentation, using advanced NLP, chained prompt systems, multiple glossaries and style guide injection, and file transformations and validations
- [GitLab Duo Agent Translation Platform](https://gitlab.com/gitlab-com/localization/gitlab-duo-agent-translation-platform) project with configurations and specifications for the custom [GitLab Translation Agent](https://gitlab.com/explore/ai-catalog/agents/532/)
- Emerging AI tools - standalone projects in Claude in the early stages of prototype

### Content management system integrations

- [Decap CMS integration](https://gitlab.com/groups/gitlab-com/localization/-/epics/83) - Marketing website content workflow automation through GitLab repositories
- Legacy integrations: [Contentful](https://gitlab.com/groups/gitlab-com/localization/-/epics/27)

### Supporting tools and services

- [GitLab String Search](https://gitlab.com/gitlab-com/localization/gitlab-string-search) - web interface for searching GitLab's translatable source code strings. The website is used by wider community translators on Crowdin. For details, see this [implementation epic](https://gitlab.com/gitlab-com/localization/localization-team/-/issues/342)
- [Crowdin Automation](https://gitlab.com/gitlab-com/localization/crowdin-automation) - automation scripts for adding context to strings on Crowdin, tracking translator contributions, analyzing comments in Crowdin
- [Kalcium Quickterm](https://gitlab.com/groups/gitlab-com/localization/-/epics/51) - terminology management system

## Central content repository

All localization workflows converge through GitLab as the single source of truth for content management and translations. This GitLab-centric approach ensures:

- Version control for all source and translated content
- Unified delivery mechanism through Translation MRs
- Consistent quality gates and approval workflows
- Integrated CI/CD pipelines for content publishing
