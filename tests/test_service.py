"""Tests for the filesystem service layer."""
import pytest
import os
import tempfile
from datetime import date
from pathlib import Path


class TestServiceReadWrite:
    """Tests for reading and writing notes via the service layer."""

    def test_read_company_note(self, tmp_path):
        """Should read a company note from the vault."""
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.models import CompanyStatus

        # Create a test vault
        vault_root = tmp_path / "Job Search"
        vault_root.mkdir()
        (vault_root / "Companies").mkdir()

        # Write a test company note
        company_text = """---
tags:
  - job-search
  - company
company: Acme Corp
company_key: acme-corp
status: active
interest: 4
last_updated: 2026-03-07
---

# Acme Corp

## Snapshot

## Notes

## Contacts

## Active Applications

## Context

## Timeline

## Open Questions

## Related
"""
        (vault_root / "Companies" / "Acme Corp.md").write_text(company_text)

        # Read via service
        service = JobSearchService(vault_root=str(vault_root))
        record = service.read_company_note("acme-corp")

        assert record is not None
        assert record.company == "Acme Corp"
        assert record.company_key == "acme-corp"
        assert record.status == CompanyStatus.ACTIVE
        assert record.interest == 4

    def test_write_company_note(self, tmp_path):
        """Should write a company note to the vault."""
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.models import CompanyRecord, CompanyStatus

        # Create a test vault
        vault_root = tmp_path / "Job Search"
        vault_root.mkdir()
        (vault_root / "Companies").mkdir()

        # Write via service
        service = JobSearchService(vault_root=str(vault_root))
        record = CompanyRecord(
            company="Beta Inc",
            company_key="beta-inc",
            status=CompanyStatus.ACTIVE,
            interest=3,
            last_updated=date(2026, 3, 7),
        )
        service.write_company_note(record)

        # Verify file was created
        file_path = vault_root / "Companies" / "Beta Inc.md"
        assert file_path.exists()
        content = file_path.read_text()
        assert "company: Beta Inc" in content
        assert "company_key: beta-inc" in content

    def test_read_company_tracking(self, tmp_path):
        """Should read the company tracking note."""
        from job_search_mcp.service import JobSearchService

        # Create a test vault
        vault_root = tmp_path / "Job Search"
        vault_root.mkdir()

        # Write a test tracker
        tracker_text = """# Company Tracking

## Active Interview Pipeline

### Acme Corp
- **Status:** active
- **Interest:** 4
- **Current state:** Phone screen
- **Next action:** Prepare for onsite
- **Due:** 2026-03-15

"""
        (vault_root / "Company Tracking.md").write_text(tracker_text)

        # Read via service
        service = JobSearchService(vault_root=str(vault_root))
        tracker = service.read_company_tracking()

        assert tracker is not None
        assert "acme-corp" in tracker.companies

    def test_write_company_tracking(self, tmp_path):
        """Should write the company tracking note."""
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.notes.tracker import CompanyTracking

        # Create a test vault
        vault_root = tmp_path / "Job Search"
        vault_root.mkdir()

        # Write via service
        service = JobSearchService(vault_root=str(vault_root))
        tracker = CompanyTracking()
        tracker.companies["beta-inc"] = {
            "name": "Beta Inc",
            "status": "active",
            "interest": 3,
            "current_state": "Applied",
            "next_action": "Follow up",
        }
        service.write_company_tracking(tracker)

        # Verify file was created
        file_path = vault_root / "Company Tracking.md"
        assert file_path.exists()
        content = file_path.read_text()
        assert "### Beta Inc" in content
        assert "**Status:** active" in content

    def test_read_daily_note(self, tmp_path):
        """Should read a daily note."""
        from job_search_mcp.service import JobSearchService

        # Create a test vault
        vault_root = tmp_path / "Job Search"
        vault_root.mkdir()
        (vault_root / "Day").mkdir()

        # Write a test daily note
        daily_text = """---
tags:
  - job-search
  - daily
date: 2026-03-07
---

# 2026-03-07

## Schedule

## Daily Activity

## Schedule vs Activity
"""
        (vault_root / "Day" / "2026-03-07.md").write_text(daily_text)

        # Read via service
        service = JobSearchService(vault_root=str(vault_root))
        daily = service.read_daily_note(date(2026, 3, 7))

        assert daily is not None
        assert daily.date == date(2026, 3, 7)

    def test_write_daily_note(self, tmp_path):
        """Should write a daily note."""
        from job_search_mcp.service import JobSearchService
        from job_search_mcp.notes.daily import DailyNote

        # Create a test vault
        vault_root = tmp_path / "Job Search"
        vault_root.mkdir()
        (vault_root / "Day").mkdir()

        # Write via service
        service = JobSearchService(vault_root=str(vault_root))
        daily = DailyNote(date=date(2026, 3, 7))
        service.write_daily_note(daily)

        # Verify file was created
        file_path = vault_root / "Day" / "2026-03-07.md"
        assert file_path.exists()
        content = file_path.read_text()
        assert "# 2026-03-07" in content

    def test_upsert_company_tracking_entry(self, tmp_path):
        """Should add or update a company in the tracker."""
        from job_search_mcp.service import JobSearchService

        # Create a test vault
        vault_root = tmp_path / "Job Search"
        vault_root.mkdir()

        # Write via service
        service = JobSearchService(vault_root=str(vault_root))
        service.upsert_company_tracking_entry(
            company_key="acme-corp",
            company_name="Acme Corp",
            status="active",
            interest=4,
            current_state="Phone screen",
            next_action="Prepare for onsite",
            due_date=date(2026, 3, 15),
        )

        # Verify file was created
        file_path = vault_root / "Company Tracking.md"
        assert file_path.exists()
        content = file_path.read_text()
        assert "### Acme Corp" in content
        assert "**Status:** active" in content
