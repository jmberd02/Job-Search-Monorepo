"""MCP server entry point for job-search-mcp.

Run with: python3 -m job_search_mcp
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, time
from enum import Enum
from typing import Optional

from mcp.server.fastmcp import FastMCP

from . import server as _ops
from .service import JobSearchService

mcp = FastMCP("job-search")

_service: Optional[JobSearchService] = None


def _get_service() -> JobSearchService:
    global _service
    if _service is None:
        _service = JobSearchService()
    return _service


def _serialize(obj) -> str:
    """Serialize a dataclass (with date/enum fields) to a JSON string."""
    def _default(o):
        if isinstance(o, (date, time)):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        return str(o)
    return json.dumps(asdict(obj), default=_default)


@mcp.tool()
def read_company_note(company_key: str) -> str:
    """Read a company note from the vault by its key (slug)."""
    result = _ops.read_company_note(_get_service(), company_key)
    if result is None:
        return json.dumps({"error": f"No company note found for key: {company_key}"})
    return _serialize(result)


@mcp.tool()
def write_company_note(company: str, company_key: str, status: str, interest: int) -> str:
    """Write a company note. status: active/waiting/closed/networking. interest: 1-5."""
    from .models import CompanyRecord, CompanyStatus
    record = CompanyRecord(
        company=company,
        company_key=company_key,
        status=CompanyStatus(status),
        interest=interest,
        last_updated=date.today(),
    )
    _ops.write_company_note(_get_service(), record)
    return json.dumps({"ok": True})


@mcp.tool()
def read_company_tracking() -> str:
    """Read the company tracking dashboard."""
    result = _ops.read_company_tracking(_get_service())
    return json.dumps({
        "companies": list(result.companies.keys()),
        "application_count": len(result.applications),
    })


@mcp.tool()
def upsert_company_tracking_entry(
    company_key: str,
    company_name: str,
    status: str,
    interest: int,
    current_state: str,
    next_action: str,
    due_date: Optional[str] = None,
    contacts: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Add or update a company entry in the tracker. due_date format: YYYY-MM-DD."""
    parsed_due = date.fromisoformat(due_date) if due_date else None
    _ops.upsert_company_tracking_entry(
        _get_service(),
        company_key=company_key,
        company_name=company_name,
        status=status,
        interest=interest,
        current_state=current_state,
        next_action=next_action,
        due_date=parsed_due,
        contacts=contacts,
        notes=notes,
    )
    return json.dumps({"ok": True})


@mcp.tool()
def read_daily_note(note_date: str) -> str:
    """Read a daily note. note_date format: YYYY-MM-DD."""
    result = _ops.read_daily_note(_get_service(), date.fromisoformat(note_date))
    if result is None:
        return json.dumps({"error": f"No daily note for {note_date}"})
    return _serialize(result)


@mcp.tool()
def append_daily_activity(
    note_date: str,
    start_time: str,
    end_time: str,
    description: str,
    status: str,
    note: str = "",
) -> str:
    """Append an activity to a daily note. note_date: YYYY-MM-DD. Times: 'HH:MM' or 'H:MM AM/PM'."""
    _ops.append_daily_activity(
        _get_service(),
        note_date=date.fromisoformat(note_date),
        start_time=start_time,
        end_time=end_time,
        description=description,
        status=status,
        note=note,
    )
    return json.dumps({"ok": True})


@mcp.tool()
def classify_signal(
    company_key: str,
    signal_type: str,
    summary: str,
    source_marker: Optional[str] = None,
    stage: Optional[str] = None,
    sentiment: Optional[str] = None,
    next_action: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Classify a raw signal. signal_type: recruiter_message/interview_transcript/calendar_event/application_event/manual_note."""
    parsed_due = date.fromisoformat(due_date) if due_date else None
    result = _ops.classify_signal(
        company_key=company_key,
        signal_type=signal_type,
        summary=summary,
        source_marker=source_marker,
        stage=stage,
        sentiment=sentiment,
        next_action=next_action,
        due_date=parsed_due,
    )
    return _serialize(result)


@mcp.tool()
def ingest_signal(
    company_key: str,
    signal_type: str,
    summary: str,
    source_marker: Optional[str] = None,
    stage: Optional[str] = None,
    sentiment: Optional[str] = None,
    next_action: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Ingest a signal and update the company note and tracker. signal_type: recruiter_message/interview_transcript/calendar_event/application_event/manual_note."""
    parsed_due = date.fromisoformat(due_date) if due_date else None
    signal = _ops.classify_signal(
        company_key=company_key,
        signal_type=signal_type,
        summary=summary,
        source_marker=source_marker,
        stage=stage,
        sentiment=sentiment,
        next_action=next_action,
        due_date=parsed_due,
    )
    result = _ops.ingest_signal(_get_service(), signal)
    return _serialize(result)


@mcp.tool()
def initialize_vault(
    path: str,
    user_name: str,
    target_roles: str,
    focus_areas: str,
    compensation: str = "",
    location: str = "",
) -> str:
    """Initialize a new job search vault. target_roles and focus_areas are comma-separated."""
    user_context = {
        "name": user_name,
        "target_roles": [r.strip() for r in target_roles.split(",")],
        "focus_areas": [f.strip() for f in focus_areas.split(",")],
        "compensation": compensation,
        "location": location,
    }
    return _ops.initialize_vault(path, user_context)


@mcp.tool()
def get_pending_actions() -> str:
    """Get pending actions from the company tracker."""
    result = _ops.get_pending_actions_from_tracker()
    return json.dumps(result)


if __name__ == "__main__":
    mcp.run()
