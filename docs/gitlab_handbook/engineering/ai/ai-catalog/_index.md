---
title: AI Catalog Group
description: "The AI Catalog Group is focused on developing AI Catalog, a catalog of Agents, tools, and flows that can be created, curated, and shared across organizations, groups, and projects."
---

## Vision

The AI Catalog Group is focused on developing AI Catalog, a catalog of Agents, tools, and flows that can be created, curated, and shared across organizations, groups, and projects.

## Team members

**Engineering Manager & Engineers**

{{< team-by-manager-slug "sam-beckham" >}}

## How to reach us

Depending on the context here are the most appropriate ways to reach out to the AI Catalog group:

* Slack Channel: `#g_ai_catalog`
* GitLab group `@gitlab-org/ai-powered/ai-catalog/engineering` (just engineers)

## What we're working on

TBD

## How we work

We're just getting started and will be defining how we work as we settle in to the new team.
Here are some links to get us started:

* [Root Epic](https://gitlab.com/groups/gitlab-org/-/epics/11111): For grouping all the work and setting out a roadmap
* [Issue board](https://gitlab.com/groups/gitlab-org/-/boards/3871464): For all in-flight issues
* [Team tasks](https://gitlab.com/gitlab-org/ai-powered/ai-catalog/team-tasks/-/issues): For all non-product related team issues
* [Async updates](https://gitlab.com/gitlab-org/ai-powered/ai-catalog/team-tasks/-/issues/?label_name%5B%5D=async%20update)
* [Team Wiki](https://gitlab.com/gitlab-org/ai-powered/ai-catalog/team-tasks/-/wikis/home): For product decisions and useful information

### DRIs

When working on a large project, we'll split it into epics and issues.
The Directly Responsible Individual (DRI) for each epic serves as the single point of accountability for that domain.
The DRI doesn't necessarily do all the work, but owns the success of their epic.

DRI responsibilities:

1. Answer questions about epic status, scope, and technical decisions
2. Maintain accurate epic and issue descriptions
3. Monitor and communicate delivery health status
4. Curate the issue list. Include what's needed and remove what isn't
5. Keep delivery dates and issue statuses current
6. Coordinate with other DRIs when work spans multiple epics

### How we handle requests for help

When a customer is experiencing an issue with the catalog, our support team will
raise a [request for help](https://gitlab.com/gitlab-com/request-for-help).
If you wish to raise a request for help please read [this readme](https://gitlab.com/gitlab-com/request-for-help#please-read-the-following-before-submiting-a-request-for-help-to-the-gitlab-development-team-sections) for instructions on how and when to do so.

To handle requests for help in a timely manner without distracting the whole team, we nominate a goalkeeper for each milestone.
The goalkeeper is responsible for ensuring that incoming requests, questions, and issues are triaged and directed to the appropriate people or teams.

Each milestone, we assign a new goalkeeper and open a goalkeeping issue.

You can find more information in the [issue template](https://gitlab.com/gitlab-org/ai-powered/ai-catalog/team-tasks/-/blob/main/.gitlab/issue_templates/goalkeeper.md).

### Communication

The AI Catalog Team communicates based on the following guidelines:

* Always prefer async communication over sync meetings.
* Don't shy away from arranging a [sync call](/handbook/communication/#video-calls) when async is proving inefficient, however always record it to share with team members.
* By default communicate in the open.
* Prefer public channels (`#g_ai_catalog`) over private message for work-related Slack messaging.

### Frontend-Backend collaboration

We aim to foster high levels of collaboration between frontend and backend engineers to ensure
development velocity and code quality.

* **Schema-first development**: Before implementation begins, frontend and backend engineers collaborate
  to design a GraphQL API schema based on UI requirements, user experience needs, and performance considerations.
* **Parallel development processes**: Once the schema is agreed upon, the frontend can proceed
  using mock data, mock endpoints, or API stubs that match the agreed schema. The backend can
  focus on implementing the data model, business logic, and actual API schema.
* **Maintaining alignment**: We value great communication. When requirements or schema need to change, we communicate
  early through the relevant GitLab issue or in [`#g_ai_catalog`](https://gitlab.enterprise.slack.com/archives/C08T5J1KXKQ)
  so our frontend or backend counterparts stay informed of all changes and can provide feedback early to avoid late-stage blockers.

### AI stage collaboration

The AI Catalog relies on the
[Workflow Service](https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/tree/main/duo_workflow_service?ref_type=heads)
as a foundational backend service.
Most AI Catalog features require new capabilities to be developed within Workflow Service,
which means our engineers will need to contribute directly to that codebase in partnership with the
[Agent Foundations team](../agent-foundations/_index.md).

**Collaboration Requirements:**

* All Workflow Service contributions must be developed in close partnership with the Agent Foundations team
* Our implementations must align with their service architecture and vision
* We commit to supporting Workflow Service's broader goals and adhering to their technical standards

**Collaboration Process:**

* Reach out to relevant Agent Foundations contacts (listed below) during the planning phase
* Join their [`#g_duo-agent-platform`](https://gitlab.enterprise.slack.com/archives/C07035GQ0TB) channel
* Follow our [async communication preferences](#communication) by default, but schedule sync meetings
  when needed and ensure key outcomes are documented in GitLab issues

#### Primary Agent Foundations contacts

| Team Member | Expertise Area |
| ---      | ---     |
| [Mikołaj Wawrzyniak](https://gitlab.com/mikolaj_wawrzyniak) | Workflow Service architecture |
| [Frédéric Caplette](https://gitlab.com/f_caplette) | Client-side implementation |
| [Dylan Griffith](https://gitlab.com/DylanGriffith) | Workflow Executor architecture: remote execution environment and runner implementation |
| [Jessie Young](https://gitlab.com/jessieay) | Authorization and authentication |
| [Shekhar Patnaik](https://gitlab.com/shekharpatnaik)  / [Igor Drozdov](https://gitlab.com/igor.drozdov) | Duo Chat agent integration |
| [Sebastian Rehm](https://gitlab.com/bastirehm) | Engineering Manager, backup contact for any of the above |

### Planning cadence

We plan and align our work to GitLab's [product milestones](/handbook/product/product-processes/milestones/). Milestone planning happens during the week before the start of the next milestone.

### ~Deliverable label

The `~Deliverable` label is used to identify issues that the team has committed to deliver within a specific milestone.
This label serves multiple purposes:

* **Commitment signal**: Communicates to stakeholders and customers that we intend to complete this work in the milestone
* **Prioritization**: Helps team members identify which issues should be worked on first
* **Focus**: Clarifies which work is essential vs nice-to-have for the milestone

#### Who applies it and when

The Engineering Manager applies the `~Deliverable` label during the planning process before the start of a milestone.
This decision is made in collaboration with the Product Manager based on:

* Team capacity for the milestone
* Issue estimates and complexity
* Strategic priorities and customer commitments

#### Prioritization

Issues with the `~Deliverable` label take priority over other work in the milestone.
Team members should:

1. First, work on assigned `~Deliverable` issues in the current milestone
2. If all `~Deliverable` issues are complete or blocked, pick up other issues from the milestone
3. Consult with the Engineering Manager if priorities are unclear or if a `~Deliverable` issue needs to be deprioritized

**During the milestone:**

* If a `~Deliverable` issue becomes blocked or cannot be completed, communicate this early in `#g_ai_catalog` or the relevant issue
* The Engineering Manager may adjust `~Deliverable` labels during the milestone based on changing priorities or capacity

### Our tech stack

* GraphQL [backend](https://docs.gitlab.com/development/api_graphql_styleguide/) and
  [frontend](https://docs.gitlab.com/development/fe_guide/graphql/). All new schema items must be
  [marked experimental](https://docs.gitlab.com/development/api_graphql_styleguide/#mark-schema-items-as-experiments)
  to let us making breaking changes when we need.
* GraphQL [subscriptions](https://docs.gitlab.com/development/fe_guide/graphql/#subscriptions) rather than polling.
* Read the [AI Catalog Backend Architecture](../../../engineering/architecture/design-documents/ai_catalog/_index.md) design document (authored February 2026).

## Team meetings

### AI Catalog: Group meeting

* **Time**: Every Tuesday, alternating weekly between 05:30 UTC and 15:00 UTC.
* **Purpose**: This meeting serves as a general sync meeting to bring up any current issues and blockers.
* **Agenda**: [Google Doc (internal only)](https://docs.google.com/document/d/19zrzqN37ZVwwEJ9iYhy4QBsUzVN0Hd1j1yn8J0v4dqE)
* **Recordings**: [Google Drive (internal only)](https://drive.google.com/drive/folders/1I9s96jg9knqOwDLabhn9100H-MsvG2ne)
