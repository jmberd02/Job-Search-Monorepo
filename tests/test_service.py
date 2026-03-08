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
