"""Tests for the service layer."""
import pytest
from datetime import date
from pathlib import Path
import tempfile
import os

from job_search_mcp.service import JobSearchService
from job_search_mcp.models import CompanyRecord, CompanyStatus, ApplicationStatus


class TestServiceCompanyNoteResolution:
    """Tests for company note resolution through tracker."""

    def test_read_company_note_via_tracker(self, tmp_path):
        """Test reading company note via tracker link."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        # Create tracker with company note link
        tracker_path = vault_root / "Company Tracking.md"
        tracker_content = """# Company Tracking

## Active Interview Pipeline

### Acme Corp
- **Status:** active
- **Company Note:** [[Companies/Acme Corp]]
- **Interest:** 4
- **Current state:** Phone screen
- **Next action:** Follow up
"""
        tracker_path = vault_root / "Company Tracking.md"
        tracker_path.write_text(tracker_content)
        
        # Create company note
        companies_dir = vault_root / "Companies"
        companies_dir.mkdir(parents=True)
        company_note_path = companies_dir / "Acme Corp.md"
        company_note_path.write_text("""---
company: Acme Corp
company_key: acme-corp
status: active
---

# Acme Corp

Test company note.
""")
        
        service = JobSearchService(vault_root=str(vault_root))
        company = service.read_company_note("acme-corp")
        
        assert company is not None
        assert company.company == "Acme Corp"
        assert company.company_key == "acme-corp"
        assert company.status == CompanyStatus.ACTIVE

    def test_read_company_note_no_tracker_entry(self, tmp_path):
        """Test reading company note when tracker has no entry."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        service = JobSearchService(vault_root=str(vault_root))
        company = service.read_company_note("nonexistent")
        assert company is None

    def test_read_company_note_missing_file(self, tmp_path):
        """Test reading company note when file doesn't exist."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        # Create tracker with broken link
        tracker_path = vault_root / "Company Tracking.md"
        tracker_path.write_text("""# Company Tracking

## Active Interview Pipeline

### Broken Corp
- **Status:** active
- **Company Note:** [[Companies/Broken Corp]]
""")
        
        service = JobSearchService(vault_root=str(vault_root))
        company = service.read_company_note("broken-corp")
        assert company is None

    def test_read_company_note_no_tracker(self, tmp_path):
        """Test reading company note when no tracker exists."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        service = JobSearchService(vault_root=str(vault_root))
        company = service.read_company_note("any")
        assert company is None


class TestServiceApplicationNoteResolution:
    """Tests for application note resolution through index."""

    def test_read_application_note_via_index(self, tmp_path):
        """Test reading application note via application index."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        # Create tracker with application index
        tracker_path = vault_root / "Company Tracking.md"
        tracker_content = """# Company Tracking

## Application Index

- acme-corp-senior-engineer: Applications/Acme Corp - Senior Engineer.md

"""
        tracker_path.write_text(tracker_content)
        
        # Create application note
        apps_dir = vault_root / "Applications"
        apps_dir.mkdir(parents=True)
        app_note_path = apps_dir / "Acme Corp - Senior Engineer.md"
        app_note_path.write_text("""---
company: Acme Corp
company_key: acme-corp
role: Senior Engineer
application_key: acme-corp-senior-engineer
status: applied
created: 2026-03-01
last_updated: 2026-03-07
---

# Acme Corp - Senior Engineer

Test application note.
""")
        
        service = JobSearchService(vault_root=str(vault_root))
        app = service.read_application_note("acme-corp-senior-engineer")
        
        assert app is not None
        assert app.company == "Acme Corp"
        assert app.application_key == "acme-corp-senior-engineer"
        assert app.status == ApplicationStatus.APPLIED

    def test_read_application_note_fallback_to_scan(self, tmp_path):
        """Test reading application note falls back to scanning when not in index."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        # Create empty tracker (no index)
        tracker_path = vault_root / "Company Tracking.md"
        tracker_path.write_text("# Company Tracking\n")
        
        # Create application note
        apps_dir = vault_root / "Applications"
        apps_dir.mkdir(parents=True)
        app_note_path = apps_dir / "Acme Corp - Senior Engineer.md"
        app_note_path.write_text("""---
company: Acme Corp
company_key: acme-corp
role: Senior Engineer
application_key: acme-corp-senior-engineer
status: applied
created: 2026-03-01
last_updated: 2026-03-07
---

# Acme Corp - Senior Engineer
""")
        
        service = JobSearchService(vault_root=str(vault_root))
        app = service.read_application_note("acme-corp-senior-engineer")
        
        assert app is not None
        assert app.application_key == "acme-corp-senior-engineer"

    def test_write_application_note_updates_index(self, tmp_path):
        """Test writing application note updates the index."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        # Create empty tracker
        tracker_path = vault_root / "Company Tracking.md"
        tracker_path.write_text("# Company Tracking\n")
        
        service = JobSearchService(vault_root=str(vault_root))
        
        from job_search_mcp.models import ApplicationRecord
        app = ApplicationRecord(
            company="Acme Corp",
            company_key="acme-corp",
            role="Senior Engineer",
            application_key="acme-corp-senior-engineer",
            status=ApplicationStatus.APPLIED,
            created=date(2026, 3, 1),
            last_updated=date(2026, 3, 7),
        )
        
        service.write_application_note(app)
        
        # Verify index was updated
        tracker = service.read_company_tracking()
        assert "acme-corp-senior-engineer" in tracker.applications
        assert tracker.applications["acme-corp-senior-engineer"] == "Applications/Acme Corp - Senior Engineer.md"
        
        # Verify we can read it back via index
        read_app = service.read_application_note("acme-corp-senior-engineer")
        assert read_app is not None
        assert read_app.application_key == "acme-corp-senior-engineer"
