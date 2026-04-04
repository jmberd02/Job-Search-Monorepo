"""MCP server interface for job-search-mcp.

This module exposes the core operations as simple functions that can be
wrapped by an MCP server implementation.
"""

from datetime import date, time
from typing import Optional

from .service import JobSearchService
from .models import CompanyRecord, ApplicationRecord, CompanySignal
from .notes.daily import DailyNote
from .notes.tracker import CompanyTracking
from .ingestion import classify_signal as _classify_signal, ingest_signal as _ingest_signal


# =============================================================================
# Note Read Operations
# =============================================================================

def read_company_note(service: JobSearchService, company_key: str) -> Optional[CompanyRecord]:
    """Read a company note from the vault."""
    return service.read_company_note(company_key)


def read_company_tracking(service: JobSearchService) -> CompanyTracking:
    """Read the company tracking note."""
    return service.read_company_tracking()


def read_daily_note(service: JobSearchService, note_date: date) -> Optional[DailyNote]:
    """Read a daily note."""
    return service.read_daily_note(note_date)


def read_candidate_profile(service: JobSearchService):
    """Read the candidate profile note."""
    return service.read_candidate_profile()


# =============================================================================
# Note Write Operations
# =============================================================================

def write_company_note(service: JobSearchService, record: CompanyRecord) -> None:
    """Write a company note to the vault."""
    service.write_company_note(record)


def write_company_tracking(service: JobSearchService, tracker: CompanyTracking) -> None:
    """Write the company tracking note."""
    service.write_company_tracking(tracker)


def write_daily_note(service: JobSearchService, daily: DailyNote) -> None:
    """Write a daily note."""
    service.write_daily_note(daily)


def write_candidate_profile(service: JobSearchService, profile) -> None:
    """Write the candidate profile note."""
    service.write_candidate_profile(profile)


# =============================================================================
# Tracker Operations
# =============================================================================

def upsert_company_tracking_entry(
    service: JobSearchService,
    company_key: str,
    company_name: str,
    status: str,
    interest: int,
    current_state: str,
    next_action: str,
    due_date: Optional[date] = None,
    applications: Optional[list[str]] = None,
    contacts: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    """Add or update a company entry in the tracker."""
    service.upsert_company_tracking_entry(
        company_key=company_key,
        company_name=company_name,
        status=status,
        interest=interest,
        current_state=current_state,
        next_action=next_action,
        due_date=due_date,
        applications=applications,
        contacts=contacts,
        notes=notes,
    )


# =============================================================================
# Daily Activity Operations
# =============================================================================

def append_daily_activity(
    service: JobSearchService,
    note_date: date,
    start_time: str,
    end_time: str,
    description: str,
    status: str,
    note: str = "",
) -> None:
    """Append an activity block to a daily note."""
    daily = service.read_daily_note(note_date)
    if daily is None:
        daily = DailyNote(date=note_date)

    # Parse time strings
    start = _parse_time(start_time)
    end = _parse_time(end_time)

    if start is None or end is None:
        raise ValueError(f"Invalid time format: {start_time} - {end_time}")

    from .notes.daily import append_daily_activity as _append
    daily = _append(daily, start, end, description, status, note)
    service.write_daily_note(daily)


def refresh_schedule_vs_activity(service: JobSearchService, note_date: date) -> None:
    """Refresh the schedule vs activity comparison for a daily note."""
    daily = service.read_daily_note(note_date)
    if daily is None:
        return

    from .notes.daily import refresh_schedule_vs_activity as _refresh
    daily = _refresh(daily)
    service.write_daily_note(daily)


# =============================================================================
# Ingestion Operations
# =============================================================================

def classify_signal(
    company_key: str,
    signal_type: str,
    summary: str,
    source_marker: Optional[str] = None,
    stage: Optional[str] = None,
    sentiment: Optional[str] = None,
    next_action: Optional[str] = None,
    due_date: Optional[date] = None,
) -> CompanySignal:
    """Classify a raw signal into a normalized CompanySignal."""
    return _classify_signal(
        company_key=company_key,
        signal_type=signal_type,
        summary=summary,
        source_marker=source_marker,
        stage=stage,
        sentiment=sentiment,
        next_action=next_action,
        due_date=due_date,
    )


def ingest_signal(service: JobSearchService, signal: CompanySignal) -> CompanyRecord:
    """Ingest a signal and update company note and tracker."""
    return _ingest_signal(service, signal)


# =============================================================================
# Setup Tools
# =============================================================================

def initialize_vault(path: str, user_context: dict) -> str:
    """
    Initialize a new job search vault at specified path.

    Args:
        path: Absolute path for new vault
        user_context: User profile data (name, roles, preferences)

    Returns:
        Success message with vault location
    """
    from pathlib import Path
    import shutil
    from .config import save_config

    vault_path = Path(path)

    # Create directory structure
    folders = [
        "Companies",
        "Applications",
        "Day",
        "Calls",
        "Leetcode",
        "Templates",
        "Prompts",
        ".claude/skills"
    ]

    for folder in folders:
        (vault_path / folder).mkdir(parents=True, exist_ok=True)

    # Copy skill templates from repo skills/ directory
    repo_root = Path(__file__).parent.parent.parent
    skills_source = repo_root / "skills"
    skills_dest = vault_path / ".claude" / "skills"

    if skills_source.exists():
        for skill_dir in skills_source.iterdir():
            if skill_dir.is_dir():
                shutil.copytree(
                    skill_dir,
                    skills_dest / skill_dir.name,
                    dirs_exist_ok=True
                )

    # Create .claude/CLAUDE.md from template
    claude_md = f"""# Job Search Agent

You are a job search assistant helping {user_context.get('name', 'the user')} find their next role.

## About {user_context.get('name', 'User')}
- Name: {user_context.get('name', 'User')}
- Target roles: {', '.join(user_context.get('target_roles', []))}
- Focus areas: {', '.join(user_context.get('focus_areas', []))}
- Compensation: {user_context.get('compensation', 'Not specified')}
- Location: {user_context.get('location', 'Not specified')}

## Your Role
- Help plan daily job search activities
- Track companies and applications
- Process recruiter communications
- Analyze LeetCode practice sessions
- Provide interview prep support

## Context
This vault contains {user_context.get('name', 'the user')}'s job search pipeline, daily plans,
company research, and interview prep notes. Always read relevant notes before making suggestions.
"""

    (vault_path / ".claude" / "CLAUDE.md").write_text(claude_md)

    # Create initial tracker
    tracker_content = """# Company Tracking

## Needs Action This Week
| Company | Status | Next Action | Due |
|---------|--------|-------------|-----|
| _Add companies here as you progress_ | | | |

## Active Interview Pipeline

_Companies will appear here when you track them_

## Applied / Waiting

## Networking Leads

## Closed Out
"""

    (vault_path / "Company Tracking.md").write_text(tracker_content)

    # Create Candidate Profile template
    profile_content = f"""---
created: {date.today().isoformat()}
updated: {date.today().isoformat()}
---

# Candidate Profile

## Basic Info
- **Name:** {user_context.get('name', '')}
- **Target Roles:** {', '.join(user_context.get('target_roles', []))}
- **Focus Areas:** {', '.join(user_context.get('focus_areas', []))}
- **Compensation Target:** {user_context.get('compensation', '')}
- **Location:** {user_context.get('location', '')}

## Preferences
- **Work Style:** [Remote/Hybrid/Onsite]
- **Company Size:** [Startup/Mid/Large/Any]
- **Industries:** [Tech, AI/ML, etc.]

## Constraints
- **Commute:** Max [X] minutes
- **Availability:** [When can you interview]
- **Notice Period:** [Current job notice]

## Notes
[Add personal notes about search priorities]
"""

    (vault_path / "Candidate Profile.md").write_text(profile_content)

    # Create Progress hub
    progress_content = """# Job Search Progress

## Quick Links
- [[Company Tracking]] - Pipeline at a glance
- [[Candidate Profile]] - Your profile and preferences

## Recent Activity
- Check [[Day/]] for daily notes

## Active Focus
[Add current focus areas]
"""

    (vault_path / "Progress.md").write_text(progress_content)

    # Create README
    readme_content = """# Job Search Vault

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
"""

    (vault_path / "README.md").write_text(readme_content)

    # Save config
    config_data = {
        "vault_path": str(vault_path.absolute()),
        "user_context": user_context
    }
    save_config(None, config_data)  # Uses default path

    return f"✓ Vault created at {vault_path}\n✓ Configuration saved\n✓ Skills installed"


def get_pending_actions_from_tracker(config_path: Optional[str] = None) -> list[dict]:
    """
    Extract pending actions from Company Tracking.md.

    Args:
        config_path: Optional path to config file

    Returns:
        List of pending actions with company, action, and due date
    """
    from pathlib import Path
    from .paths import get_tracker_path, get_vault_root

    # Get vault root from config
    if config_path:
        vault_root = get_vault_root(Path(config_path))
    else:
        vault_root = get_vault_root()

    # Read tracker file directly
    tracker_path = get_tracker_path(vault_root)
    if not tracker_path.exists():
        return []

    tracker_text = tracker_path.read_text()
    actions = []

    # Parse "Needs Action This Week" table
    lines = tracker_text.split('\n')
    in_table = False

    for line in lines:
        if '## Needs Action This Week' in line:
            in_table = True
            continue

        if in_table and line.startswith('|') and not line.startswith('|---'):
            # Skip header
            if 'Company' in line and 'Status' in line:
                continue

            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4 and parts[0] and parts[0] != '_Add companies':
                actions.append({
                    "company": parts[0],
                    "status": parts[1],
                    "next_action": parts[2],
                    "due": parts[3]
                })

        if in_table and line.startswith('##') and 'Needs Action' not in line:
            break

    return actions


# =============================================================================
# Utility Functions
# =============================================================================

def _parse_time(time_str: str) -> Optional[time]:
    """Parse a time string like '9:00 AM' or '14:30'."""
    time_str = time_str.strip()

    # Try various formats
    formats = [
        "%I:%M %p",  # 9:00 AM
        "%H:%M",     # 14:30
        "%I %p",     # 9 AM
        "%H",        # 14
    ]

    from datetime import datetime
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue

    return None


# =============================================================================
# MCP Server Export (for use with mcp CLI)
# =============================================================================

def get_mcp_tools():
    """Return a list of tool definitions for MCP server registration."""
    return [
        {
            "name": "read_company_note",
            "description": "Read a company note from the vault",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "company_key": {"type": "string", "description": "The company key (slug)"},
                },
                "required": ["company_key"],
            },
        },
        {
            "name": "write_company_note",
            "description": "Write a company note to the vault",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name"},
                    "company_key": {"type": "string", "description": "Company key (slug)"},
                    "status": {"type": "string", "description": "Company status"},
                    "interest": {"type": "integer", "description": "Interest level (1-5)"},
                },
                "required": ["company", "company_key", "status", "interest"],
            },
        },
        {
            "name": "read_company_tracking",
            "description": "Read the company tracking note",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "upsert_company_tracking_entry",
            "description": "Add or update a company entry in the tracker",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "company_key": {"type": "string"},
                    "company_name": {"type": "string"},
                    "status": {"type": "string"},
                    "interest": {"type": "integer"},
                    "current_state": {"type": "string"},
                    "next_action": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"},
                },
                "required": ["company_key", "company_name", "status", "interest", "current_state", "next_action"],
            },
        },
        {
            "name": "read_daily_note",
            "description": "Read a daily note",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["date"],
            },
        },
        {
            "name": "write_daily_note",
            "description": "Write a daily note",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["date"],
            },
        },
        {
            "name": "append_daily_activity",
            "description": "Append an activity block to a daily note",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["date", "start_time", "end_time", "description", "status"],
            },
        },
        {
            "name": "classify_signal",
            "description": "Classify a raw signal into a normalized CompanySignal",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "company_key": {"type": "string"},
                    "signal_type": {"type": "string"},
                    "summary": {"type": "string"},
                    "source_marker": {"type": "string"},
                    "stage": {"type": "string"},
                    "sentiment": {"type": "string"},
                    "next_action": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"},
                },
                "required": ["company_key", "signal_type", "summary"],
            },
        },
        {
            "name": "ingest_signal",
            "description": "Ingest a signal and update company note and tracker",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "company_key": {"type": "string"},
                    "signal_type": {"type": "string"},
                    "summary": {"type": "string"},
                    "source_marker": {"type": "string"},
                    "stage": {"type": "string"},
                    "sentiment": {"type": "string"},
                    "next_action": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"},
                },
                "required": ["company_key", "signal_type", "summary"],
            },
        },
    ]
