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
