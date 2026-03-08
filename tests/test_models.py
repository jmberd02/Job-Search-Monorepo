"""Tests for core models and enums."""
import pytest
from datetime import date
from enum import Enum


class TestCompanyStatus:
    """Tests for CompanyStatus enum."""

    def test_status_values(self):
        """Status enum should have expected values."""
        from job_search_mcp.models import CompanyStatus
        assert CompanyStatus.ACTIVE.value == "active"
        assert CompanyStatus.WAITING.value == "waiting"
        assert CompanyStatus.CLOSED.value == "closed"
        assert CompanyStatus.NETWORKING.value == "networking"


class TestApplicationStatus:
    """Tests for ApplicationStatus enum."""

    def test_status_values(self):
        """Status enum should have expected values."""
        from job_search_mcp.models import ApplicationStatus
        assert ApplicationStatus.DRAFTED.value == "drafted"
        assert ApplicationStatus.APPLIED.value == "applied"
        assert ApplicationStatus.SCREEN.value == "screen"
        assert ApplicationStatus.INTERVIEW.value == "interview"
        assert ApplicationStatus.ONSITE.value == "onsite"
        assert ApplicationStatus.OFFER.value == "offer"
        assert ApplicationStatus.REJECTED.value == "rejected"
        assert ApplicationStatus.WITHDRAWN.value == "withdrawn"
        assert ApplicationStatus.GHOSTED.value == "ghosted"


class TestSignalType:
    """Tests for SignalType enum."""

    def test_signal_type_values(self):
        """SignalType enum should have expected values."""
        from job_search_mcp.models import SignalType
        assert SignalType.RECRUITER_MESSAGE.value == "recruiter_message"
        assert SignalType.INTERVIEW_TRANSCRIPT.value == "interview_transcript"
        assert SignalType.CALENDAR_EVENT.value == "calendar_event"
        assert SignalType.APPLICATION_EVENT.value == "application_event"
        assert SignalType.MANUAL_NOTE.value == "manual_note"


class TestTaskState:
    """Tests for TaskState enum."""

    def test_task_state_values(self):
        """TaskState enum should have expected values."""
        from job_search_mcp.models import TaskState
        assert TaskState.PENDING.value == "pending"
        assert TaskState.IN_PROGRESS.value == "in_progress"
        assert TaskState.DONE.value == "done"
        assert TaskState.BLOCKED.value == "blocked"


class TestCompanyRecord:
    """Tests for CompanyRecord model."""

    def test_company_record_creation(self):
        """CompanyRecord should be creatable with required fields."""
        from job_search_mcp.models import CompanyRecord, CompanyStatus

        record = CompanyRecord(
            company="Acme Corp",
            company_key="acme-corp",
            status=CompanyStatus.ACTIVE,
            interest=4,
            last_updated=date(2026, 3, 7),
        )
        assert record.company == "Acme Corp"
        assert record.company_key == "acme-corp"
        assert record.status == CompanyStatus.ACTIVE
        assert record.interest == 4

    def test_company_record_defaults(self):
        """CompanyRecord should have sensible defaults."""
        from job_search_mcp.models import CompanyRecord, CompanyStatus

        record = CompanyRecord(
            company="Acme Corp",
            company_key="acme-corp",
            status=CompanyStatus.ACTIVE,
            interest=3,
            last_updated=date(2026, 3, 7),
        )
        assert record.notes == ""
        assert record.contacts == []
        assert record.timeline == []


class TestApplicationRecord:
    """Tests for ApplicationRecord model."""

    def test_application_record_creation(self):
        """ApplicationRecord should be creatable with required fields."""
        from job_search_mcp.models import ApplicationRecord, ApplicationStatus

        record = ApplicationRecord(
            company="Acme Corp",
            company_key="acme-corp",
            role="Senior Engineer",
            application_key="acme-corp-senior-engineer",
            status=ApplicationStatus.APPLIED,
            created=date(2026, 3, 1),
            last_updated=date(2026, 3, 7),
        )
        assert record.company == "Acme Corp"
        assert record.role == "Senior Engineer"
        assert record.status == ApplicationStatus.APPLIED

    def test_application_record_defaults(self):
        """ApplicationRecord should have sensible defaults."""
        from job_search_mcp.models import ApplicationRecord, ApplicationStatus

        record = ApplicationRecord(
            company="Acme Corp",
            company_key="acme-corp",
            role="Senior Engineer",
            application_key="acme-corp-senior-engineer",
            status=ApplicationStatus.APPLIED,
            created=date(2026, 3, 1),
            last_updated=date(2026, 3, 7),
        )
        assert record.materials == {}
        assert record.interview_process == []
        assert record.tasks == []


class TestCompanySignal:
    """Tests for CompanySignal model."""

    def test_signal_creation(self):
        """CompanySignal should be creatable with required fields."""
        from job_search_mcp.models import CompanySignal, SignalType

        signal = CompanySignal(
            company_key="acme-corp",
            signal_type=SignalType.RECRUITER_MESSAGE,
            summary="Recruiter reached out about senior roles",
            source_marker="email:12345",
        )
        assert signal.company_key == "acme-corp"
        assert signal.signal_type == SignalType.RECRUITER_MESSAGE
        assert signal.summary == "Recruiter reached out about senior roles"

    def test_signal_defaults(self):
        """CompanySignal should have sensible defaults."""
        from job_search_mcp.models import CompanySignal, SignalType

        signal = CompanySignal(
            company_key="acme-corp",
            signal_type=SignalType.MANUAL_NOTE,
            summary="Manual note",
        )
        assert signal.source_marker is None
        assert signal.stage is None
        assert signal.sentiment is None
        assert signal.next_action is None
        assert signal.due_date is None
