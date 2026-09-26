"""Tests for normalized signal ingestion."""
import pytest
from datetime import date
from pathlib import Path
import tempfile


class TestSignalIngestion:
    """Tests for signal ingestion logic."""

    def test_classify_manual_note(self):
        """Should classify a manual note into a CompanySignal."""
        from job_search_mcp.ingestion import classify_signal

        signal = classify_signal(
            company_key="acme-corp",
            signal_type="manual_note",
            summary="Follow up with recruiter",
            source_marker="manual:2026-03-07:followup",
        )

        assert signal.company_key == "acme-corp"
        assert signal.signal_type.value == "manual_note"
        assert signal.summary == "Follow up with recruiter"
        assert signal.source_marker == "manual:2026-03-07:followup"

    def test_classify_recruiter_message(self):
        """Should classify a recruiter message signal."""
        from job_search_mcp.ingestion import classify_signal
        from job_search_mcp.models import SignalType

        signal = classify_signal(
            company_key="acme-corp",
            signal_type="recruiter_message",
            summary="Recruiter reached out about senior roles",
            source_marker="email:12345",
            stage="outreach",
            sentiment="positive",
        )

        assert signal.signal_type == SignalType.RECRUITER_MESSAGE
        assert signal.stage == "outreach"
        assert signal.sentiment == "positive"

    def test_ingest_company_signal(self):
        """Should ingest a signal and update company note."""
        from job_search_mcp.ingestion import ingest_signal
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.models import CompanyRecord, CompanyStatus, SignalType, CompanySignal

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)

            # Create initial company note
            record = CompanyRecord(
                company="Acme Corp",
                company_key="acme-corp",
                status=CompanyStatus.ACTIVE,
                interest=4,
                last_updated=date(2026, 3, 1),
            )
            service.write_company_note(record)

            # Ingest a signal
            signal = CompanySignal(
                company_key="acme-corp",
                signal_type=SignalType.MANUAL_NOTE,
                summary="Follow up with recruiter",
                source_marker="manual:2026-03-07:1",
                next_action="Send follow-up email",
                due_date=date(2026, 3, 10),
            )

            updated = ingest_signal(service, signal)

            # Verify company was updated
            assert updated is not None
            assert len(updated.timeline) == 1
            assert updated.timeline[0].summary == "Follow up with recruiter"
            assert updated.primary_next_action == "Send follow-up email"
            assert updated.next_action_due == date(2026, 3, 10)

    def test_avoid_duplicate_signals(self):
        """Should not create duplicate timeline entries."""
        from job_search_mcp.ingestion import ingest_signal
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.models import CompanyRecord, CompanyStatus, SignalType, TimelineEntry, CompanySignal

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)

            # Create company note with existing timeline entry
            record = CompanyRecord(
                company="Acme Corp",
                company_key="acme-corp",
                status=CompanyStatus.ACTIVE,
                interest=4,
                last_updated=date(2026, 3, 1),
                timeline=[
                    TimelineEntry(
                        date=date(2026, 3, 1),
                        entry_type="manual_note",
                        summary="Initial note",
                        source="manual:2026-03-07:1",
                    )
                ],
            )
            service.write_company_note(record)

            # Ingest same signal again
            signal = CompanySignal(
                company_key="acme-corp",
                signal_type=SignalType.MANUAL_NOTE,
                summary="Initial note",
                source_marker="manual:2026-03-07:1",
            )

            updated = ingest_signal(service, signal)

            # Should still have only 1 entry
            assert len(updated.timeline) == 1

    def test_update_tracker_after_ingestion(self):
        """Should update tracker after ingesting a signal."""
        from job_search_mcp.ingestion import ingest_signal
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.models import CompanyRecord, CompanyStatus, SignalType, CompanySignal

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)

            # Create initial company note
            record = CompanyRecord(
                company="Acme Corp",
                company_key="acme-corp",
                status=CompanyStatus.ACTIVE,
                interest=4,
                last_updated=date(2026, 3, 1),
            )
            service.write_company_note(record)

            # Ingest a signal
            signal = CompanySignal(
                company_key="acme-corp",
                signal_type=SignalType.MANUAL_NOTE,
                summary="Applied to role",
                source_marker="manual:2026-03-07:apply",
                stage="applied",
            )

            ingest_signal(service, signal)

            # Verify tracker was updated
            tracker = service.read_company_tracking()
            assert "acme-corp" in tracker.companies
            assert tracker.companies["acme-corp"]["current_state"] == "applied"
