"""Core data models for job-search-mcp."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class CompanyStatus(Enum):
    """Company status enum."""

    ACTIVE = "active"
    WAITING = "waiting"
    CLOSED = "closed"
    NETWORKING = "networking"


class ApplicationStatus(Enum):
    """Application status enum."""

    DRAFTED = "drafted"
    APPLIED = "applied"
    SCREEN = "screen"
    INTERVIEW = "interview"
    ONSITE = "onsite"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    GHOSTED = "ghosted"


class SignalType(Enum):
    """Company signal type enum."""

    RECRUITER_MESSAGE = "recruiter_message"
    INTERVIEW_TRANSCRIPT = "interview_transcript"
    CALENDAR_EVENT = "calendar_event"
    APPLICATION_EVENT = "application_event"
    MANUAL_NOTE = "manual_note"


class TaskState(Enum):
    """Task state enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass
class Contact:
    """Contact information."""

    name: str
    role: str
    source: str = ""
    last_contact: Optional[date] = None
    notes: str = ""


@dataclass
class TimelineEntry:
    """Timeline entry for company notes."""

    date: date
    entry_type: str
    summary: str
    source: str = ""
    linked_note: str = ""


@dataclass
class InterviewEvent:
    """Interview event for application notes."""

    date: date
    stage: str
    people: str = ""
    outcome: str = ""
    notes: str = ""


@dataclass
class Task:
    """Task item for application notes."""

    description: str
    state: TaskState = TaskState.PENDING
    due_date: Optional[date] = None


@dataclass
class CompanyRecord:
    """Company note record."""

    company: str
    company_key: str
    status: CompanyStatus
    interest: int
    last_updated: date
    notes: str = ""
    contacts: list[Contact] = field(default_factory=list)
    timeline: list[TimelineEntry] = field(default_factory=list)
    # Snapshot fields
    primary_next_action: str = ""
    next_action_due: Optional[date] = None
    best_current_role: str = ""
    location: str = ""
    commute_fit: str = ""
    comp_range: str = ""


@dataclass
class ApplicationRecord:
    """Application note record."""

    company: str
    company_key: str
    role: str
    application_key: str
    status: ApplicationStatus
    created: date
    last_updated: date
    materials: dict[str, str] = field(default_factory=dict)
    interview_process: list[InterviewEvent] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    # Snapshot fields
    applied_on: Optional[date] = None
    current_stage: str = ""
    next_action: str = ""
    due_date: Optional[date] = None
    priority_interest: int = 3
    comp: str = ""
    location: str = ""


@dataclass
class CompanySignal:
    """Normalized company signal for ingestion."""

    company_key: str
    signal_type: SignalType
    summary: str
    source_marker: Optional[str] = None
    stage: Optional[str] = None
    sentiment: Optional[str] = None
    next_action: Optional[str] = None
    due_date: Optional[date] = None
