---
title: "AI Agent Setup"
description: "Data Team guide for setting up agentic AI tools for development"
---

[TOC]

## Context

The data team doesn't have a standard approach for AI-assisted development — this guide fills that gap. It's based on what's already been working for several teammates, so everyone has a solid starting point rather than figuring it out from scratch.

This guide covers setup for:

- **OpenCode** — a terminal-based AI coding agent
- **Snowflake/dbt MCP servers** (optional, but highly recommended)
- **MacWhisper** — voice-driven prompting (optional)

---

## OpenCode Setup

A more comprehensive guide is available in the [internal handbook](https://internal.gitlab.com/handbook/ai-security-at-gitlab/guides/setup-guides/opencode-setup/). The steps below are a simplified, data-team-specific version.

### Step 1: Install OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
```

### Step 2: Verify the installation

Check that OpenCode is available in your PATH:

```bash
which opencode
```

**If `which opencode` returns nothing**, add OpenCode to your PATH by running:

```bash
echo 'export PATH=~/.opencode/bin:$PATH' >> ~/.zshrc && source ~/.zshrc
```

Now verify the installation:

```bash
opencode --version
```

You should see the installed version number.

### Step 3: Start OpenCode from the analytics repo

```bash
jump analytics
opencode
```

### Step 4: Configure GitLab Duo as your AI provider

GitLab Duo uses OAuth — no token to create or manage.

1. Run `/connect` inside OpenCode and select **GitLab Duo**
2. OpenCode will open your browser to complete the OAuth flow
3. Sign in with your `@gitlab.com` account and authorise the app
4. You'll be redirected back to OpenCode automatically

### Step 4.5: Test the connection

Once connected, test it by saying `hi` to verify OpenCode responds.

### Step 5: Apply the Golden Config

Apply the config from the [OpenCode Golden Path](https://internal.gitlab.com/handbook/ai-security-at-gitlab/guides/golden-configs/opencode/#golden-path-config).

> **Note:** Use `~/.config/opencode/opencode.jsonc` rather than `opencode.json` — the `.jsonc` extension allows comments, which is useful for annotating your config.

### Step 6: Set `plan` as your default agent

Open `~/.config/opencode/config.json` (this is a separate file from the `opencode.jsonc` Golden Config in Step 5) and add `default_agent`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  ...
  "default_agent": "plan"
}
```

This keeps you in the safer, more deliberate mode by default — you switch to Build explicitly when you're ready to execute.

### Step 7: Review the Agent Usage Guide

Before you start using OpenCode, review the [Agent Usage Guide](agent-usage-guide.md) to understand:

- How agents and MCPs work
- Configuration best practices (global vs project-level)
- When to use Plan vs Build mode
- Prompting best practices and context management
- Available skills and agents

### Video Resources

Requires using **GitLab Unfiltered** account:

- [OpenCode Setup Tutorial](https://www.youtube.com/watch?v=80vTUzgQzoY) (3m 30s)
- [OpenCode Demo](https://www.youtube.com/watch?v=nClVkkI-MFo) (5m 30s)

---

## MCP Server Setup

### Snowflake MCP Server (Optional but Highly Recommended)

Connecting OpenCode to Snowflake MCP allows an LLM agent to query Snowflake directly during an OpenCode session.

To set up, run the [setup_mcp_analytics.sh script](https://gitlab.com/gitlab-data/analytics/-/blob/master/admin/setup_mcp_analytics.sh?ref_type=heads) with these commands:

```bash
jump analytics
git checkout master && git pull && ./admin/setup_mcp_analytics.sh
```

The script will prompt you for your GitLab username and analytics repo path.

> **Important:** The script will prompt for your computer login password and request keychain access. Enter your password and click **"Always Allow"** when prompted.

**Verify the connection:**

Start OpenCode (`jump analytics && opencode`), type `hi`, then look to the right side of the interface. You should see the Snowflake MCP name listed with a green dot indicating "connected".

<details>
<summary>More detail on what gets created</summary>

The script generates two files:

**`~/.config/mcp/snowflake-mcp/snowflake_mcp_config.yml`**

Controls which Snowflake tool groups are enabled and which SQL statement types are permitted. The defaults enable object inspection and query execution while disabling destructive operations (`Drop`, `Delete`).

**`~/.config/mcp/snowflake-mcp/snowflake_mcp.env`**

```env
SNOWFLAKE_USER=<your GitLab email>
SNOWFLAKE_ACCOUNT=gitlab
SNOWFLAKE_ROLE=<the portion of your email before the @>
```

</details>

### dbt MCP Server

If you ran `setup_snowflake_mcp.sh` above, this is already configured. The script adds the following environment variables to your `~/.zshrc`:

```bash
# Analytics MCP Environment Variables
export ANALYTICS_DIR="~/repos/analytics/"
export DBT_PROJECT_DIR="$ANALYTICS_DIR/transform/snowflake-dbt"
export DBT_PATH="$DBT_PROJECT_DIR/.venv/bin/dbt"
```

The only other prerequisite is having the dbt virtualenv set up. To verify or set it up:

```bash
jump analytics
make run-dbt
ls .venv/bin/dbt  # Should show the dbt executable
```

If `ls .venv/bin/dbt` returns the file path, you're good to go.

**Verify the connection:**

Start OpenCode (`jump analytics && opencode`), type `hi`, then look to the right side of the interface. You should see the dbt MCP name listed with a green dot indicating "connected".

---

## MacWhisper for Voice Prompting (Optional)

Typing out detailed prompts is slow. [MacWhisper](https://goodsnooze.gumroad.com/l/macwhisper) is a macOS voice-to-text app that makes it much faster to describe context and work through problems out loud — particularly for longer prompts where you'd otherwise spend more time typing than thinking.

It's noticeably more accurate than built-in macOS Dictation app, and unlike cloud-based transcription it runs entirely on-device, so nothing leaves your machine.

## Skills Setup

Skills provide reusable workflows and conventions that agents can automatically invoke. To use all available Data Team skills:

1. Complete the OpenCode setup steps above
2. Complete the MCP setup steps above (Snowflake/dbt)
3. Clone and symlink the `data-team-agentic-skills` repo by following the [setup instructions](https://gitlab.com/gitlab-data/data-team-agentic-skills#setup-opencode)
