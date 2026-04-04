# Job Search Agent - Shareable Distribution Design

**Date:** 2026-04-04
**Purpose:** Enable friends to use the job search automation workflow with minimal technical knowledge

## Overview

Transform the existing job-search-mcp system from a personal tool into a shareable package that friends can install and use with Claude Code. The system should be non-technical-friendly while maintaining the full workflow capabilities.

## Goals

1. **Easy setup** - Clone repo, run setup script, done
2. **Claude Code native** - Replace OpenClaw/Discord with Claude Code skills
3. **Non-technical friendly** - Conversational setup, clear documentation
4. **Local execution** - Each user runs their own instance
5. **Workflow correctness** - Users understand how to use it effectively

## Architecture

### Components

```
User's Machine:
  ├─ Claude Code (CLI or Windows Companion)
  │  ├─ Job Search Skills (from vault's .claude/skills/)
  │  └─ MCP Client (connects to job-search-mcp)
  │
  ├─ job-search-mcp Server
  │  ├─ Reads config from ~/.job-search/config.json
  │  ├─ Obsidian vault operations
  │  ├─ Company/application/tracker management
  │  └─ Optional: Gmail/Calendar integration (disabled by default)
  │
  └─ Obsidian Vault (user-specified location)
     ├─ .claude/
     │  ├─ CLAUDE.md (user context, agent identity)
     │  └─ skills/ (workflow skills)
     ├─ Companies/
     ├─ Applications/
     ├─ Day/
     ├─ Company Tracking.md
     └─ Templates/
```

### Key Design Decisions

**Skills in vault (.claude/skills/):**
- Users can customize if needed
- Contains user context in `.claude/CLAUDE.md`
- Skills are part of the vault, versioned with user's data
- Setup wizard populates with good defaults

**No OpenClaw/Discord:**
- All interactions through Claude Code conversations
- No channel separation needed
- Skills handle workflow logic
- User drives interactions

**Configuration:**
- Vault location stored in `~/.job-search/config.json`
- User specifies location during setup
- MCP reads config on startup

**Automation:**
- User-initiated (no autonomous background polling for MVP)
- Skills guide users through workflows
- Claude Code conversation handles timing/reminders

## Installation & Setup

### Repository Structure

```
job-search-agent/
  setup.sh                  # Mac/Linux setup
  setup.ps1                 # Windows setup
  README.md                 # Installation instructions

  src/
    job_search_mcp/         # MCP server code
      server.py
      config.py             # Config file handling
      notes/                # Note operations
      models.py
      ...

  skills/                   # Skill templates (copied to vault)
    plan-day/
    track-company/
    ingest-email/
    analyze-leetcode/
    help/

  templates/                # Vault templates (copied to vault)
    company-note-template.md
    daily-note-template.md
    ...

  tests/
  pyproject.toml
```

### Setup Flow

**1. Clone repository:**
```bash
git clone https://github.com/yourusername/job-search-agent.git
cd job-search-agent
```

**2. Run setup script:**
```bash
./setup.sh  # Mac/Linux
./setup.ps1 # Windows
```

**What setup.sh does:**
- Checks for Python 3.10+ (errors with install instructions if missing)
- Runs `pip install -e .` (installs MCP server)
- Configures Claude Code's `~/.claude/mcp_servers.json`:
  ```json
  {
    "job-search": {
      "command": "python",
      "args": ["-m", "job_search_mcp.server"],
      "cwd": "/path/to/cloned/repo"
    }
  }
  ```
- Tests MCP server connection
- Prints next steps

**3. Run setup wizard:**
```
Open Claude Code
Run: /setup-job-search
Follow conversational setup
```

**4. Open Obsidian:**
```
Point Obsidian to the vault location chosen during setup
```

### Setup Wizard Skill (`/setup-job-search`)

**Conversational flow:**

1. **Welcome & vault location:**
   ```
   Hi! I'll help you set up your job search agent.

   Where should I create your vault?
   (e.g., ~/Documents/JobSearch or C:\Users\You\JobSearch)
   ```

2. **Create vault structure:**
   - Folders: `Companies/`, `Applications/`, `Day/`, `Calls/`, `Leetcode/`, `Templates/`, `Prompts/`
   - Top-level files: `Company Tracking.md`, `Candidate Profile.md`, `Progress.md`, `README.md`
   - `.claude/` folder with skills
   - `.claude/CLAUDE.md` template

3. **Gather user context:**
   - Name
   - Target roles
   - Technologies/domains
   - Compensation range (optional)
   - Location preferences

4. **Write configuration:**
   - `~/.job-search/config.json` with vault path and preferences

5. **Create example notes:**
   - Sample company note
   - Sample daily note for today
   - Template files

6. **Next steps:**
   ```
   ✓ Vault created at ~/Documents/JobSearch
   ✓ Skills installed
   ✓ Configuration saved

   Next steps:
   1. Open Obsidian
   2. Open vault at: ~/Documents/JobSearch
   3. Come back here and try: /plan tomorrow

   Optional: Install Obsidian Git plugin for backups
   ```

## MCP Server Changes

### Configuration System

**Replace environment variable with config file:**

```python
# src/job_search_mcp/config.py
from pathlib import Path
import json

def load_config() -> dict:
    """Load config from ~/.job-search/config.json"""
    config_path = Path.home() / ".job-search" / "config.json"
    if not config_path.exists():
        raise ConfigError(
            "Configuration not found. Run /setup-job-search first."
        )
    return json.loads(config_path.read_text())

def get_vault_path() -> Path:
    """Get vault path from config"""
    config = load_config()
    return Path(config["vault_path"])

def get_user_context() -> dict:
    """Get user context from config"""
    config = load_config()
    return config.get("user_context", {})
```

### New MCP Tools

**Vault initialization:**
```python
@mcp.tool()
def initialize_vault(path: str, user_context: dict) -> str:
    """
    Create complete vault structure at specified path.

    Args:
        path: Absolute path for vault
        user_context: User profile data (name, roles, preferences)

    Returns:
        Success message with vault location
    """
```

**Helper tools for skills:**
```python
@mcp.tool()
def get_user_context() -> dict:
    """Read user context from .claude/CLAUDE.md"""

@mcp.tool()
def list_pending_actions() -> list:
    """Parse Company Tracking.md for items needing action"""

@mcp.tool()
def get_upcoming_interviews(days: int = 7) -> list:
    """Find companies with interviews in next N days"""
```

### Optional Integration Tools

**Gmail/Calendar (disabled by default):**
```python
@mcp.tool()
def fetch_recruiting_emails(label: str = "job-search") -> list:
    """
    Fetch emails from Gmail label.
    Requires OAuth setup via /setup-integrations.
    """

@mcp.tool()
def get_calendar_events(date: str) -> list:
    """
    Get Google Calendar events for date.
    Requires OAuth setup via /setup-integrations.
    """
```

Users can enable via `/setup-integrations` skill in v2.

### Existing Tools Unchanged

All current MCP tools remain functional:
- `read_daily_note`, `write_daily_note`, `append_daily_activity`
- `read_company_note`, `upsert_company_note`
- `read_company_tracking`, `upsert_company_tracking_entry`
- `ingest_company_signal`, `resolve_company_reference`
- `read_top_performance_summary`, `update_top_performance_summary`

No breaking changes to existing interfaces.

## Claude Code Skills

Skills created in `.claude/skills/` in the user's vault. Each skill is a self-contained workflow.

### Core Skills

**1. plan-day/** - Daily Planning

```markdown
# Daily Planning Skill

You help plan the user's job search day by:
1. Reading yesterday's daily note for context
2. Checking Company Tracking for pending actions
3. Reading performance summary for weak areas
4. Creating balanced schedule with time blocks

Use MCP tools:
- read_daily_note(yesterday)
- read_company_tracking()
- read_top_performance_summary()
- get_upcoming_interviews(7)
- write_daily_note(date, content)

Format:
## Schedule
- 9:00-10:00 - [Activity]
- 10:00-12:00 - [Activity]

## Daily Activity
[Append-only execution log]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

**2. track-company/** - Company Tracking

```markdown
# Company Tracking Skill

You help track companies in the job search pipeline by:
1. Creating/updating company notes
2. Updating Company Tracking.md
3. Logging timeline entries

Use MCP tools:
- upsert_company_note(company, data)
- upsert_company_tracking_entry(company, data)
- resolve_company_reference(signal)

Always confirm before major changes.
```

**3. ingest-email/** - Email Processing

```markdown
# Email Ingestion Skill

You process recruiter emails by:
1. Parsing company, role, stage, dates
2. Classifying signal type
3. Creating/updating notes
4. Asking user for decisions

Use MCP tools:
- ingest_company_signal(signal)
- classify_company_signal(signal)

Always ask before adding to pipeline.
```

**4. analyze-leetcode/** - LeetCode Analysis

```markdown
# LeetCode Analysis Skill

You analyze practice sessions by:
1. Reading performance history
2. Identifying patterns and weak areas
3. Suggesting next problems
4. Logging in daily activity

Use MCP tools:
- read_top_performance_summary()
- update_top_performance_summary(data)
- append_daily_activity(date, block, status, note)

Focus on constructive feedback.
```

**5. help/** - Command Reference

```markdown
# Help Skill

Show available commands and usage examples.
Keep it concise and friendly.
```

### Skill Design Principles

1. **Self-contained** - Each skill is independent
2. **Conversational** - Natural language interaction
3. **Confirmations** - Ask before major changes
4. **Context-aware** - Read relevant notes automatically
5. **Helpful** - Suggest next steps, don't nag

## Vault Structure

Complete structure created by setup wizard:

```
JobSearch/                          # User-specified location
  .claude/
    CLAUDE.md                       # User context, agent identity
    skills/
      plan-day/skill.md
      track-company/skill.md
      ingest-email/skill.md
      analyze-leetcode/skill.md
      help/skill.md

  Companies/                        # Detailed company notes
    _template.md

  Applications/                     # Per-role applications
    2026-04/
      _template.md

  Day/                              # Daily notes
    2026-04-04.md                   # Example

  Calls/                            # Interview/recruiter calls
    2026-04/

  Leetcode/                         # Practice tracking
    2026-04/
      PERFORMANCE SUMMARY.md

  Templates/                        # Reusable templates
    daily-note-template.md
    company-note-template.md
    application-note-template.md

  Prompts/                          # Optional system prompts
    Daily Schedule Prompt.md
    LeetCode Feedback Prompt.md

  Company Tracking.md               # Main pipeline tracker
  Candidate Profile.md              # User profile/preferences
  Progress.md                       # Navigation hub
  README.md                         # Quick start guide
```

### Key Files

**`.claude/CLAUDE.md`** (filled by setup wizard):
```markdown
# Job Search Agent

You are a job search assistant helping [Name] find their next role.

## About [Name]
- Name: [Name]
- Target roles: [Roles]
- Focus areas: [Technologies]
- Compensation: [Range]
- Location: [Preferences]

## Your Role
- Help plan daily job search activities
- Track companies and applications
- Process recruiter communications
- Analyze LeetCode practice sessions
- Provide interview prep support

## Context
This vault contains [Name]'s job search pipeline, daily plans,
company research, and interview prep notes. Always read relevant
notes before making suggestions.
```

**`README.md`** (vault quick start):
```markdown
# Job Search Vault

This vault tracks your job search using Claude Code.

## Quick Start

Open Claude Code in this directory and try:
- `/plan tomorrow` - Create tomorrow's plan
- `/track` - Add a company to your pipeline
- `/help` - See all commands

## Files
- **Company Tracking.md** - Your pipeline at a glance
- **Companies/** - Detailed company research
- **Day/** - Daily plans and activity logs

## Tips
- Use Obsidian to browse and manually edit notes
- Claude will read/write these notes automatically
- Install Obsidian Git plugin for backups
```

## Daily Workflows

### Morning Routine

**Plan the day:**
```
User: /plan tomorrow

Claude:
[Reads context, creates plan]
Here's what I'm thinking...

User: Add 30min prep for TechCo interview

Claude: Updated! [Shows plan]
```

### During the Day

**Track opportunities:**
```
User: /track Got LinkedIn message from Stripe

Claude: Let me add that...
[Updates tracking]
What role or wait for details?
```

**Process emails:**
```
User: /ingest [pastes email]

Claude:
[Parses email]
Found: Acme Corp, Senior Engineer
Add to Active Pipeline?
```

**LeetCode practice:**
```
User: /leetcode Did "Word Ladder", 45min, struggled with BFS

Claude:
[Updates tracking]
Good work! Word Ladder is classic BFS...
Logged in today's activity.
```

### End of Day

**Review:**
```
User: /eod

Claude:
[Compares plan vs actual]
Completed 3.5/4 hours planned
Tomorrow's priorities: TechCo interview prep
Want me to draft tomorrow's plan?
```

## Distribution & Updates

### How Friends Get It

**GitHub repository distribution:**

1. Share link: `github.com/yourusername/job-search-agent`
2. Friends click "Use this template" or clone
3. Follow README:
   - Run `./setup.sh`
   - Open Claude Code
   - Run `/setup-job-search`

### Updates

**For MCP updates:**
```bash
cd job-search-agent
git pull origin main
pip install -e . --force-reinstall
```

**For skill updates:**
- Users run `git pull` to get updates
- If skills customized, manual merge needed (or upgrade script in v2)

**For vault structure updates:**
- Non-breaking
- New folders/templates are optional

## Future Enhancements (Post-MVP)

**v2 Features:**
- `/setup-integrations` - Gmail/Calendar OAuth setup
- Automatic update checker
- Export pipeline to CSV/JSON
- Interview prep flashcards
- Job board integrations

**Distribution improvements:**
- PyPI package: `pip install job-search-agent`
- Homebrew: `brew install job-search-agent`
- Pre-built installers for Windows/Mac

**For MVP:** Keep it simple with GitHub repo and manual setup.

## Success Criteria

**Technical:**
- [ ] MCP config system working
- [ ] Setup wizard creates complete vault
- [ ] All core skills functional
- [ ] Works with Claude Code CLI and Windows Companion
- [ ] Cross-platform (Windows/Mac/Linux)

**User Experience:**
- [ ] Non-technical friend can set up in <10 minutes
- [ ] Clear documentation with examples
- [ ] Workflow feels natural
- [ ] Users understand how to use skills

**Quality:**
- [ ] All existing tests still pass
- [ ] New config system tested
- [ ] Setup wizard tested
- [ ] Documentation complete

## Implementation Notes

### Minimal Changes to Existing Code

- Keep all existing MCP tools intact
- Add config system alongside (not replacing current code)
- New tools are additions, not modifications
- Backward compatible for current personal use

### Testing Strategy

1. Test setup script on clean machine
2. Test setup wizard creates valid vault
3. Test each skill individually
4. Test with non-technical user
5. Test on Windows, Mac, Linux

### Documentation Requirements

1. Main README.md with installation
2. Vault README.md with usage
3. Each skill has examples
4. Troubleshooting guide
5. FAQ for common issues

## Open Questions / Decisions

**Resolved:**
- ✅ Use Claude Code instead of OpenClaw
- ✅ Skills in vault's `.claude/` folder
- ✅ Config file instead of env variable
- ✅ User specifies vault location
- ✅ GitHub repo distribution
- ✅ Non-technical setup priority

**For implementation:**
- Error handling strategy for setup wizard
- Vault path validation (what if invalid location?)
- Handling existing vault at specified location
- Skill update mechanism (if user customized)
- Windows path handling specifics

## Summary

**What we're building:**
- Clone repo + run setup script
- MCP server with config file system
- Setup wizard skill creates personalized vault
- Daily-use skills for planning, tracking, analysis
- Works with Claude Code CLI or Windows Companion
- Non-technical friendly with conversational setup

**Key benefits for friends:**
- Easy to install and set up
- Natural conversation-based workflow
- Fully local, private data
- Customizable if they want
- Works with their Claude instance

**Next step:** Create detailed implementation plan.
