---
title: "Database Excellence Stage"
description: "The Database Excellence section ensures GitLab's databases run reliably at scale while enabling teams to make informed decisions about data architecture, placement, and lifecycle management across all datastores."
---

## Mission

Keep GitLab's databases running reliably through proactive health management, operational excellence, and strategic enablement. We maintain operational runway by identifying and mitigating saturation points, operate infrastructure with automated and scalable processes, and provide tools and frameworks that help teams build features sustainably. While our primary focus is GitLab.com, we are expanding our scope to provide database health frameworks and tooling that benefit self-managed customers as well.

## Stage Leadership

{{< group-by-slugs alexives rsontam >}}

## Groups

This stage consists of the following groups:

### Database Architecture

The [Database Architecture](/handbook/engineering/data-engineering/database-excellence/database-architecture/) group enables teams to build sustainably with data by providing decision frameworks for data placement, data growth controls, and coordinating the database review process across all datastores.

Priorities:

* Enabling teams to make sustainable data architecture decisions
* Preventing database performance issues before they reach production
* Establishing and maintaining data lifecycle best practices

{{< group-by-slugs alexander-sosna imanpalsingh l.rosa maximeorefice panoskanell praba.m7n vporalla >}}

### Database Health

The [Database Health](/handbook/engineering/data-engineering/database-excellence/database-health/) group provides the monitoring, observability, and health frameworks that keep databases healthy across both GitLab.com and self-managed deployments, including shift-left identification of saturation points.

Priorities:

* Maintaining operational runway by proactively managing database saturation points
* Providing visibility into database health across all deployment types
* Optimizing database resource utilization and cost efficiency

{{< group-by-slugs alexives krasimirangelov meiyang nbelokolodov rhenchen.gitlab stomlinson >}}

### Database Automation

The [Database Automation](/handbook/engineering/data-engineering/database-excellence/database-automation) group owns the automation frameworks, tools, and templates that make GitLab's Postgres databases easier to operate at scale — replacing manual, bespoke processes with standardized, repeatable automation. All three teams contribute automations, but Database Automation owns the frameworks and manages the planning load for infrastructure changes.

Priorities:

* Replacing manual database operations with standardized, automated processes
* Building reusable tooling for database provisioning, configuration, and upgrades
* Enabling reliable, repeatable database operations across deployment types

{{< group-by-slugs dazhu1 bshah11 saadullah707 mattkasa jon_jenkins pmistry2 amritasinha >}}

### Previous Teams

Previously, this stage consisted of 2 teams: Database Frameworks and Database Operations. These teams had a very large and overlapping scope covering our production database systems, but had different tools at their disposal. This resulted in difficulty for teams in two respects: the teams would pursue different projects with the same goals and different tools, and the teams each had more scope than they could reasonably plan for or accomplish.

In Q1 of FY27, we reorganized the teams into their current structure in order to accomplish a few things:

* Narrow team's scope to prevent fatigue from jumping between projects and areas
* Provide more management support allowing the teams to grow beyond their current size limitations
* Expand the department's overall scope to include topics that impact self-managed customers

#### Database Frameworks

The [Database Frameworks](/handbook/engineering/data-engineering/database-excellence/database-frameworks/) group managed the Rails application code that interfaces and communicates with our database systems.

#### Database Operations

The [Database Operations](/handbook/engineering/data-engineering/database-excellence/database-operations) group managed the infrastructure and automation that power GitLab.com's PostgreSQL databases.

## How We Work

Each team within Database Excellence is composed of a mix of backend engineers and reliability engineers (SRE/DBRE). The balance varies by team — Database Architecture and Database Health are primarily backend engineers, while Database Automation is primarily reliability engineers — but every team has both disciplines represented.

While each team has a distinct focus area, several responsibilities are shared across the entire stage. Database reviews are coordinated by Database Architecture but staffed by members of all three teams. Oncall rotations draw from reliability engineers across the stage. Operational needs such as saturation mitigation and incident response are distributed across all teams rather than owned by any single group. Infrastructure management and database upgrades are also shared across teams, as the regional distribution of the three groups — spanning AMER, EMEA, and APAC — enables the potential for follow-the-sun coverage. This shared model ensures that operational knowledge stays broad and no single team becomes a bottleneck.

## Requesting Help

For a complete guide to getting help with database issues — including emergencies, support escalations, and identifying the responsible team — see [Getting Help with Database Issues](/handbook/engineering/data-engineering/database-excellence/help/).

### Incident Escalation

Database incident escalations use [incident.io](https://app.incident.io/gitlab/on-call/schedules/01JXJ7MN4T14008GQKWYYNT6E8) for on-call routing.

* **Scope**: GitLab.com S1 and S2 production incidents raised by the Incident Manager On Call, Engineer On Call, and Security teams. GitLab Dedicated support is consultative. Self-managed support is discretionary and evaluated case-by-case.
* **Escalation**: Use `/inc escalate` in the incident Slack channel. For non-urgent issues, use the [triage rotation](#triage-rotations) or post in `#s_database_excellence`.
* **Response**: Best effort, local timezone, weekday coverage only (24/5). The on-call engineer joins as a subject matter expert in a consultative capacity.
* **Process details**: See the [full escalation process](/handbook/engineering/data-engineering/database-excellence/help/#step-4-escalate-to-database-excellence) for responding procedures and shadowing instructions.

### Reliability Requests

TBD

### Tier-2 On-Call

[Database Tier-2](/handbook/engineering/infrastructure-platforms/incident-management/on-call/tier-2/#database-operations-dbo) is staffed as a 24/5 response with team members responding on a "Best Effort" basis. This means it's possible that pages to this rotation may occasionally go unacknowledged. The limited availability of database operators has made it difficult to commit beyond that.

We may readdress this rotation in FY27-Q2 in response to the recent reorganization.

### Long Term Stable Counterpart or Reviewer requests

Longer term requests, such as stable counterpart or reviewers, are handled at the stage level. These requests should be submitted as a [counterpart request](https://gitlab.com/gitlab-org/database-team/team-tasks/-/work_items/new?description_template=counterpart_request)

### Triage Rotations

Database Excellence has a [weekly triage issue](https://gitlab.com/gitlab-org/database-team/team-tasks/-/work_items?state=opened&label_name[]=database::triage),
this issue gets automatically created every week by an [automation](https://gitlab.com/gitlab-org/database-team/update_status/-/blob/main/team_triage_issue.rb) which builds different
sections that need Database excellence's input and continuous monitoring (eg: DB saturation, Table size monitoring, etc.,).

It is staffed by a Backend engineer and an SRE from the Database excellence stage.
They will share the responsibilities and tag the right person (ie: BE for application related items and SRE for infra related ones) as needed.

{{% alert title="Note" color="info" %}}
Next step: Sections in the triage issue will be classified as `backend`, `infra` and `shared`. So that the assigned DRIs will not have to
triage the same issues.
{{% /alert %}}

## Planning Process

TBA
