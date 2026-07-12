---
title: Growth Milestone Planning, Refinement and Estimation
description: "Continuous refinement process and estimation guidelines for Growth teams"
---

## Milestone Planning Phase

Growth operates on a continuous flow model anchored by milestone planning. The milestone planning issue serves as the central coordination hub, aligning priorities, ownership, and timelines.

- Milestone planning starts at-least two weeks before the actual start date of milestones
- A milestone planning Issue is created following [milestone planning template](https://gitlab.com/gitlab-org/growth/team-tasks/-/blob/master/.gitlab/issue_templates/milestone-planning-issue.md)
- Planning Issue includes strategic themes, focused work tracks for Design, Feature work, Tech Debt, Bugs and available capacity of the Engineers
- PM, EM, UXM, Designers and Engineers identifies epics and Issues for the target milestone across the feature, experiment, bugs and annotate with target milestone
- PMs work with EM to break down priority projects into implementation Issues usually before milestone start date (as required)
- Ideally, issues assigned to a target milestone should have cleared the design stage before milestone begins. This gives engineering enough clarity to scope and plan delivery with confidence. If market commitments require locking a target milestone before design is complete, we will treat it as an exception.
- EM organizes a milestone kickoff meeting on the start date of the target milestone. Engineers are expected to review the milestone issues ahead of time and self-assign [DRI](./engineering_dri.md) based on interest, capacity, and complexity. The kickoff is a discussion forum and not an assignment session for surfacing blockers, dependencies, and open questions before work begins.

## Execution Phase

- DRIs coordinate work across Issues, manage dependencies, and flag blockers immediately
- The complete development process follows [Work Progression Guidelines](#work-progression-guidelines)
- The priority projects and work listed in milestone planning take precedence. Once those are completed and there is available capacity, engineers can pick up additional Issues from the [Growth Kanban Board](https://gitlab.com/groups/gitlab-org/-/boards/4152639?label_name%5B%5D=Next+Up&label_name%5B%5D=section%3A%3Agrowth) queue.
- Bot posts weekly progress update in milestone planning Issue showing work completed, in-progress, blocked, risks, and velocity
- Bot creates a retrospective thread and ask for feedback starting from the first day of milestone execution

## Milestone Closure Phase

- Bot summarizes outcomes, generates velocity metrics (cycle time, completion rate etc), and auto-forwards incomplete work to next milestone with efficiency analysis
- Bot manages the spill over by adding a milestone missed label to the issues still open and move them into next milestone
- Bot closes the milestone

## Work Progression Guidelines

**Problem Validation**

- Product Manager validates that the problem is clearly defined, worth solving, and free of blockers
- Product Manager moves the status of the Epic/Issue to `Ready for Design`

**In-Design**

- Product Designer creates an Issue under the Epic to create necessary Design
- Designer iterates on designs and gathers early feedback
- Designer refines designs based on discussion
- When the scope is clear and the discussions have been addressed, Designer/PM moves the Issue to `Planning Breakdown` status
- If there is no Design Issue, Product Managers creates a bare minimal implementation Issues using [Experiment Implementation](https://gitlab.com/gitlab-org/gitlab/-/Issues/new?description_template=Experiment%20Implementation) or [Implementation](https://gitlab.com/gitlab-org/gitlab/-/Issues/new?description_template=Implementation) and proceed to `Planning Breakdown` status

**Refinement**

- Issues are moved from `~"workflow::planning breakdown"` to `~"workflow::refinement"` automatically by the triage bot in order of priority (from top to bottom). The bot will only move Issues to refinement if there is room in refinement column, meaning there is less Issues than maximum limit for this column. This is first chance for PMs to prioritize Issues by moving them higher in the `planning breakdown` column. After the Issue is moved to refinement, a dedicated `refinement thread` is created, which acts as a place for discussion and weight estimation.
  - 💡 Hint: In rare case when an Issue has to be expedited, it's possible to move it to refinement manually by adding the `~"workflow::refinement"` label. This will invoke a reaction from triage bot, which will add `refinement thread` for such Issue instantly so the refinement can proceed the same way as with automated path.
- During refinement the team ensures that the Issue is well described and requirements are clear. They can use the `refinement thread` to discuss but they should make sure that any changes and decisions made there are also reflected in Issue's description. Once each engineer is comfortable with the way the Issue is described, they can vote their estimation of weight based on our [guidelines](#estimation-guidelines). The voting happens by reacting to the thread with one of few possible weight estimates: 1️⃣ 2️⃣ 3️⃣ 5️⃣ or 🚀 (indicates 5+).
- If an issue has a weight of `5` or higher, it likely needs to be broken down into smaller issues. If the associated Epic has a DRI assigned, the bot will notify the DRI to split the issue and move the new issues to refinement (otherwise, it will notify the EM). The bot will not allow the issue to progress until it has been properly broken down.

> ⚠️ Once design and refinement are complete, the planned design, functionality, and UX approach should be treated as stable. Changes proposed during development or review are expensive and disruptive. Use the design and refinement phases to get as confident as possible in the implementation plan before the development phase begins.

**Development Phase**

- Each day the triage bot checks all Issues in `~"workflow::refinement"` column and if an Issue has required minimum number of estimation votes (see `MIN_REACTIONS` constant [here](https://gitlab.com/gitlab-org/quality/triage-ops/-/blob/master/lib/growth_refine_automation_helper.rb?ref_type=heads#L16) for the current setting) it will be moved to `~"workflow::scheduling"`.
  - 💡 Hint: If there is some problem with the Issue and it shouldn't be moved forward even if enough engineers estimate it, ❌ reaction can be added to the thread which will stop the bot from transitioning the Issue to `~"workflow::scheduling"` as long as this reaction sticks to the thread. This means that whoever put it is also responsible for removing it once the problem is gone.
- Once the Issue is in `~"workflow::scheduling"`, it is awaiting final prioritization by PMs - it has to be manually moved to `~"workflow::ready for development"` depending on the current priorities. This part of the process is PMs responsibility. This allows for additional fine-tuning of priorities and acts as a buffer for our ready for development column.
- Engineers pick the Issue from from `Ready for Development` and move the status to `In Dev`
- Once the MR associated with the Issue reaches to review stage, the status of the Issue is changed to `In Review`
- Once the MR is merged and MR changes is deployed to production, the status of the Issue is changed to `Verification`

**Verification**

- The Engineering DRI determines the appropriate verification level - either mentioning the PM and closing for straightforward completions, or requesting formal PM verification for complex changes.

## Estimation Guidelines

[The development estimation is the time during `~"workflow::in dev"` until moved to `~"workflow::complete"`, key factor is the review cycle that is uncertain with pipeline failures and reviewer availability]

| Weight | Usual Timeline | Description                                                                                                                                                                                                                                                                                      |
| ------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1      | < 1 week            | The simplest possible change. We are confident there will be no side effects.                                                                                                                                                                                                                    |
| 2      | 1-2 weeks         | A simple change (minimal code changes), where we understand all of the requirements.                                                                                                                                                                                                             |
| 3      | 2-3 weeks            | A simple change, but the code footprint is bigger (e.g. lots of different files, or tests affected). The requirements are clear.                                                                                                                                                                 |
| 5      | 3-4 weeks          | A more complex change that will impact multiple areas of the codebase, there may also be some refactoring involved. Requirements are understood but you feel there are likely to be some gaps along the way.                                                                                     |
| 5+     | 4 weeks+            | A significant change that may have dependencies (other teams or third-parties) and we likely still don't understand all of the requirements. It's unlikely we would commit to this in a milestone, and the preference would be to further clarify requirements and/or break into smaller Issues. |

In planning and estimation, we value [velocity over predictability](/handbook/engineering/development/principles/#velocity). The main goal of our planning and estimation is to focus on the [MVC](/handbook/values/#minimal-valuable-change-mvc), uncover blind spots, and help us achieve a baseline level of predictability without over optimizing. We aim for 70% predictability instead of 90%. We believe that optimizing for velocity (merge request rate) enables our Growth teams to achieve a [weekly experimentation cadence](/handbook/product/groups/growth/#weekly-growth-meeting).

- If an Issue has many unknowns where it's unclear if it's a 1 or a 5, we will be cautious and estimate high (5).
- If an Issue has many unknowns, we can break it into two Issues. The first Issue is for research, also referred to as a [Spike](<https://en.wikipedia.org/wiki/Spike_(software_development)>), where we de-risk the unknowns and explore potential solutions. The second Issue is for the implementation.
- If an initial estimate is incorrect and needs to be adjusted, we revise the estimate immediately and inform the Product Manager. The Product Manager and team will decide if a milestone commitment needs to be adjusted.

## Team Participation in Refinement

Operating asynchronously means refinement can't rely on scheduled meetings where everyone shows up at the same time. Instead, the team should adopt a continuous refinement mindset where engineers regularly check the [growth Epic board](https://gitlab.com/groups/gitlab-org/-/epic_boards/2079888) and Issue kanban board for items in refinement status. When an Epic appears in ~"workflow::refinement", engineers should review the refinement thread, ask clarifying questions, evaluate technical feasibility, and provide feedback on the proposed direction. Engineers who develop interest and context during refinement are encouraged to volunteer as the Engineering DRI by self-assigning the Epic. Once satisfied with the refinement, engineers add a ✅ reaction to the refinement thread to signal completion. This isn't a passive activity - the goal is to surface concerns, suggest alternatives, ensure the Epic is well-understood, and ideally volunteer to own the breakdown and implementation.

Similarly, the Issue kanban board should be monitored for Issues in ~"workflow::refinement", ~"workflow::scheduling", and ~"workflow::ready for development". Issues in refinement need estimation votes and technical feedback. Issues in scheduling are waiting for final prioritization but are already well-defined and could be moved to ready for development if priorities shift. Issues in ready for development are immediately available for pickup. By regularly scanning these columns, engineers maintain awareness of upcoming work, can identify Issues that align with their expertise or interests, and keep the pipeline moving.

Currently, the team should prioritize any work labeled with ~"Growth::Driving First Orders". These represent high-priority items that need immediate attention.

## Issue sequencing

In order to convey Issue implementation order and blocking concepts, we leverage the [blocking Issue linking feature](https://docs.gitlab.com/ee/user/project/Issues/related_Issues.html#blocking-Issues).

More on the discussion can be seen in https://gitlab.com/gitlab-org/growth/team-tasks/-/Issues/752.

## Labelling Issues & Epics

We use workflow boards to track Issue progress throughout a milestone. Workflow boards should be viewed at the highest group level for visibility into all nested projects in a group.

The Growth stage uses the `~"devops::growth"` label and the following groups for tracking merge request rate and ownership of Issues and merge requests.

| Name          | Label                   | gitlab-org                                                                                                                          | All Groups                                                                                                                                         |
| ------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Growth        | `~"devops::growth"`     | [Growth Workflow](https://gitlab.com/groups/gitlab-org/-/boards/4152639)                                                            | [-](https://gitlab.com/dashboard/Issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=devops%3A%3Agrowth)                                     |
| Acquisition   | `~"group::acquisition"` | [Acquisition Workflow](https://gitlab.com/groups/gitlab-org/-/boards/4152639)                                                       | [-](https://gitlab.com/dashboard/Issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=devops%3A%3Agrowth&label_name[]=group%3A%3Aacquisition) |
| Activation    | `~"group::activation"`  | [Activation Workflow](https://gitlab.com/groups/gitlab-org/-/boards/4152639)                                                        | [-](https://gitlab.com/dashboard/Issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=devops%3A%3Agrowth&label_name[]=group%3A%3Aactivation)  |
| Engagement    | `~"group::engagement"`  | [Engagement Workflow](https://gitlab.com/groups/gitlab-org/-/boards/4152639)                                                        | [-](https://gitlab.com/dashboard/Issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=devops%3A%3Agrowth&label_name[]=group%3A%3Aengagement)  |
| Experiments   | `~"experiment-rollout"` | [Experiment tracking](https://gitlab.com/groups/gitlab-org/-/boards/1352542)                                                        | [-](https://gitlab.com/dashboard/Issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=experiment-rollout)                                     |
| Feature Flags | `~"feature flag"`       | [Feature flags](https://gitlab.com/groups/gitlab-org/-/boards/1725470?&label_name[]=devops%3A%3Agrowth&label_name[]=feature%20flag) |                                                                                                                                                    |

Growth teams work across the GitLab codebase on multiple groups and projects including:

- The [gitlab.com/gitlab-org](https://gitlab.com/gitlab-org/) group
- [gitlab](https://gitlab.com/gitlab-org/gitlab)
- [GLEX](https://gitlab.com/gitlab-org/ruby/gems/gitlab-experiment)
- [customers-gitlab-com](https://gitlab.com/gitlab-org/customers-gitlab-com)
- The [gitlab.com/gitlab-com](https://gitlab.com/gitlab-com/) group
- [about.gitlab.com](https://gitlab.com/gitlab-com/marketing/digital-experience/about-gitlab-com)
