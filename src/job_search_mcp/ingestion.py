"""Normalized signal ingestion for job-search-mcp."""

from datetime import date
from typing import Optional

from .models import CompanyRecord, CompanySignal, SignalType
from .notes.company import append_company_timeline
from .service import JobSearchService


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
    return CompanySignal(
        company_key=company_key,
        signal_type=SignalType(signal_type),
        summary=summary,
        source_marker=source_marker,
        stage=stage,
        sentiment=sentiment,
        next_action=next_action,
        due_date=due_date,
    )


def ingest_signal(service: JobSearchService, signal: CompanySignal) -> CompanyRecord:
    """Ingest a signal and update company note and tracker.

    This implements the detail-first write flow:
    1. fs_read or create the company note
    2. Append the signal to the timeline (avoiding duplicates)
    3. Update operational state
    4. Update the tracker
    """
    # Step 1: Read or create company note
    existing = service.read_company_note(signal.company_key)

    if existing is None:
        # Create new company record
        existing = CompanyRecord(
            company=signal.company_key.replace("-", " ").title(),
            company_key=signal.company_key,
            status=_infer_status(signal),
            interest=3,
            last_updated=date.today(),
        )

    # Step 2: Append signal to timeline (idempotent)
    existing = append_company_timeline(existing, signal)

    # Step 3: Update operational state from signal
    if signal.next_action:
        existing.primary_next_action = signal.next_action
    if signal.due_date:
        existing.next_action_due = signal.due_date
    if signal.stage:
        existing.status = _stage_to_status(signal.stage)

    existing.last_updated = date.today()

    # Step 4: Write company note
    service.write_company_note(existing)

    # Step 5: Update tracker
    _update_tracker_from_company(service, existing, signal.stage)

    return existing


def _infer_status(signal: CompanySignal) -> "CompanyStatus":
    """Infer company status from signal type."""
    from .models import CompanyStatus

    if signal.signal_type == SignalType.RECRUITER_MESSAGE:
        return CompanyStatus.NETWORKING
    elif signal.signal_type == SignalType.APPLICATION_EVENT:
        return CompanyStatus.ACTIVE
    elif signal.signal_type == SignalType.INTERVIEW_TRANSCRIPT:
        return CompanyStatus.ACTIVE
    else:
        return CompanyStatus.ACTIVE


def _stage_to_status(stage: str) -> "CompanyStatus":
    """Convert a stage string to company status."""
    from .models import CompanyStatus

    stage_lower = stage.lower()
    if stage_lower in ("applied", "screening", "screen"):
        return CompanyStatus.ACTIVE
    elif stage_lower in ("interview", "onsite"):
        return CompanyStatus.ACTIVE
    elif stage_lower in ("offer"):
        return CompanyStatus.ACTIVE
    elif stage_lower in ("rejected", "withdrawn", "ghosted"):
        return CompanyStatus.CLOSED
    else:
        return CompanyStatus.ACTIVE


def _update_tracker_from_company(service: JobSearchService, company: CompanyRecord, stage: str = None):
    """Update the tracker entry for a company from the company record."""
    current_state = stage or company.status.value
    service.upsert_company_tracking_entry(
        company_key=company.company_key,
        company_name=company.company,
        status=company.status.value,
        interest=company.interest,
        current_state=current_state,
        next_action=company.primary_next_action,
        due_date=company.next_action_due,
    )
