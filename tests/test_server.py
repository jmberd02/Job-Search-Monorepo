"""Tests for the MCP server interface."""
import pytest
from datetime import date
import tempfile


class TestMCPTools:
    """Tests for MCP tool exports."""

    def test_service_operations_available(self):
        """Service operations should be importable."""
        from job_search_mcp.server import (
            read_company_note,
            write_company_note,
            read_company_tracking,
            upsert_company_tracking_entry,
            read_daily_note,
            write_daily_note,
            append_daily_activity,
        )

        assert read_company_note is not None
        assert write_company_note is not None
        assert read_company_tracking is not None
        assert upsert_company_tracking_entry is not None
        assert read_daily_note is not None
        assert write_daily_note is not None
        assert append_daily_activity is not None

    def test_ingestion_operations_available(self):
        """Ingestion operations should be importable."""
        from job_search_mcp.server import (
            classify_signal,
            ingest_signal,
        )

        assert classify_signal is not None
        assert ingest_signal is not None

    def test_read_company_note_operation(self):
        """read_company_note should work with a service."""
        from job_search_mcp.server import read_company_note
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.models import CompanyRecord, CompanyStatus
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)

            # Create tracker entry first
            from job_search_mcp.notes.tracker import CompanyTracking, render_company_tracking
            tracker = CompanyTracking()
            tracker.companies["acme-corp"] = {
                "name": "Acme Corp",
                "status": "active",
                "notes": "[[Companies/Acme Corp]]",
                "company_note": "[[Companies/Acme Corp]]",
                "company_note_link": "Companies/Acme Corp",
                "company_note_path": "Companies/Acme Corp.md",
            }
            tracker_path = Path(tmp) / "Company Tracking.md"
            tracker_path.write_text(render_company_tracking(tracker))

            # Create a company note
            record = CompanyRecord(
                company="Acme Corp",
                company_key="acme-corp",
                status=CompanyStatus.ACTIVE,
                interest=4,
                last_updated=date(2026, 3, 7),
            )
            service.write_company_note(record)

            # Read via operation
            result = read_company_note(service, "acme-corp")

            assert result is not None
            assert result.company == "Acme Corp"
            assert result.company_key == "acme-corp"

    def test_write_company_note_operation(self):
        """write_company_note should work with a service."""
        from job_search_mcp.server import write_company_note, read_company_note
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.models import CompanyRecord, CompanyStatus
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)

            # Create tracker entry first
            from job_search_mcp.notes.tracker import CompanyTracking, render_company_tracking
            tracker = CompanyTracking()
            tracker.companies["beta-inc"] = {
                "name": "Beta Inc",
                "status": "active",
                "notes": "[[Companies/Beta Inc]]",
                "company_note": "[[Companies/Beta Inc]]",
                "company_note_link": "Companies/Beta Inc",
                "company_note_path": "Companies/Beta Inc.md",
            }
            tracker_path = Path(tmp) / "Company Tracking.md"
            tracker_path.write_text(render_company_tracking(tracker))

            # Write via operation
            record = CompanyRecord(
                company="Beta Inc",
                company_key="beta-inc",
                status=CompanyStatus.ACTIVE,
                interest=3,
                last_updated=date(2026, 3, 7),
            )
            write_company_note(service, record)

            # Read back
            result = read_company_note(service, "beta-inc")

            assert result is not None
            assert result.company == "Beta Inc"
            assert result.company_key == "beta-inc"

    def test_upsert_tracker_entry_operation(self):
        """upsert_company_tracking_entry should work."""
        from job_search_mcp.server import upsert_company_tracking_entry, read_company_tracking
        from job_search_mcp.service import JobSearchService

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)

            # Upsert via operation
            upsert_company_tracking_entry(
                service,
                company_key="acme-corp",
                company_name="Acme Corp",
                status="active",
                interest=4,
                current_state="Phone screen",
                next_action="Prepare for onsite",
                due_date=date(2026, 3, 15),
            )

            # Read tracker
            tracker = read_company_tracking(service)

            assert "acme-corp" in tracker.companies
            assert tracker.companies["acme-corp"]["interest"] == 4
            assert tracker.companies["acme-corp"]["current_state"] == "Phone screen"

    def test_append_daily_activity_operation(self):
        """append_daily_activity should work."""
        from job_search_mcp.server import append_daily_activity, read_daily_note
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.notes.daily import DailyNote
        from datetime import time

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)

            # Create a daily note
            daily = DailyNote(date=date(2026, 3, 7))
            service.write_daily_note(daily)

            # Append activity
            append_daily_activity(
                service,
                note_date=date(2026, 3, 7),
                start_time="09:00",
                end_time="11:00",
                description="LeetCode practice",
                status="Done",
                note="Solved 3 problems",
            )

            # Read back
            result = read_daily_note(service, date(2026, 3, 7))

            assert result is not None
            assert len(result.activity) == 1
            assert result.activity[0].description == "LeetCode practice"
            assert result.activity[0].status == "Done"
