"""Tests for company tracking note parsing and rendering."""
import pytest
from datetime import date
from job_search_mcp.models import CompanyStatus


class TestParseCompanyTracking:
    """Tests for parsing company tracking notes."""

    def test_parse_empty_tracker(self):
        """Should parse an empty tracker."""
        from job_search_mcp.notes.tracker import parse_company_tracking

        text = """# Company Tracking

"""
        tracker = parse_company_tracking(text)
        assert tracker is not None
        assert len(tracker.companies) == 0

    def test_parse_tracker_with_company(self):
        """Should parse a tracker with a company entry."""
        from job_search_mcp.notes.tracker import parse_company_tracking

        text = """# Company Tracking

## Active Interview Pipeline

### Acme Corp
- **Status:** active
- **Interest:** 4
- **Current state:** Phone screen
- **Next action:** Prepare for onsite
- **Due:** 2026-03-15
- **Applications:**
  - [[Applications/2026-03/Acme Corp - Senior Engineer.md]]
- **Contacts:** John Doe (recruiter)
- **Notes:** [[Companies/Acme Corp]]

"""
        tracker = parse_company_tracking(text)
        assert "acme-corp" in tracker.companies
        company = tracker.companies["acme-corp"]
        assert company["status"] == "active"
        assert company["interest"] == 4
        assert company["current_state"] == "Phone screen"
        assert company["next_action"] == "Prepare for onsite"
        assert company["due"] == date(2026, 3, 15)

    def test_parse_tracker_with_multiple_companies(self):
        """Should parse a tracker with multiple company entries."""
        from job_search_mcp.notes.tracker import parse_company_tracking

        text = """# Company Tracking

## Active Interview Pipeline

### Acme Corp
- **Status:** active
- **Interest:** 4
- **Current state:** Phone screen
- **Next action:** Prepare for onsite
- **Due:** 2026-03-15

### Beta Inc
- **Status:** waiting
- **Interest:** 3
- **Current state:** Applied
- **Next action:** Follow up
- **Due:** 2026-03-20

"""
        tracker = parse_company_tracking(text)
        assert len(tracker.companies) == 2
        assert "acme-corp" in tracker.companies
        assert "beta-inc" in tracker.companies


class TestRenderCompanyTracking:
    """Tests for rendering company tracking notes."""

    def test_render_empty_tracker(self):
        """Should render an empty tracker."""
        from job_search_mcp.notes.tracker import render_company_tracking, CompanyTracking

        tracker = CompanyTracking()
        text = render_company_tracking(tracker)
        assert "# Company Tracking" in text
        assert "## Active Interview Pipeline" in text

    def test_render_tracker_with_company(self):
        """Should render a tracker with a company entry."""
        from job_search_mcp.notes.tracker import render_company_tracking, CompanyTracking

        tracker = CompanyTracking()
        tracker.companies["acme-corp"] = {
            "name": "Acme Corp",
            "status": "active",
            "interest": 4,
            "current_state": "Phone screen",
            "next_action": "Prepare for onsite",
            "due": date(2026, 3, 15),
            "applications": ["[[Applications/2026-03/Acme Corp - Senior Engineer.md]]"],
            "contacts": "John Doe (recruiter)",
            "notes": "[[Companies/Acme Corp]]",
        }

        text = render_company_tracking(tracker)
        assert "### Acme Corp" in text
        assert "**Status:** active" in text
        assert "**Interest:** 4" in text
        assert "**Current state:** Phone screen" in text
        assert "**Next action:** Prepare for onsite" in text


class TestUpsertCompanyTrackingEntry:
    """Tests for upserting company tracking entries."""

    def test_add_new_company(self):
        """Should add a new company to the tracker."""
        from job_search_mcp.notes.tracker import upsert_company_tracking_entry, CompanyTracking

        tracker = CompanyTracking()
        tracker = upsert_company_tracking_entry(
            tracker,
            company_key="acme-corp",
            company_name="Acme Corp",
            status="active",
            interest=4,
            current_state="Phone screen",
            next_action="Prepare for onsite",
            due_date=date(2026, 3, 15),
        )

        assert "acme-corp" in tracker.companies
        assert tracker.companies["acme-corp"]["status"] == "active"
        assert tracker.companies["acme-corp"]["interest"] == 4

    def test_update_existing_company(self):
        """Should update an existing company entry."""
        from job_search_mcp.notes.tracker import upsert_company_tracking_entry, CompanyTracking

        tracker = CompanyTracking()
        tracker.companies["acme-corp"] = {
            "status": "active",
            "interest": 4,
            "current_state": "Phone screen",
            "next_action": "Prepare for onsite",
            "due": date(2026, 3, 15),
        }

        # Update the company
        tracker = upsert_company_tracking_entry(
            tracker,
            company_key="acme-corp",
            company_name="Acme Corp",
            status="interview",
            interest=5,
            current_state="Onsite",
            next_action="Wait for feedback",
            due_date=date(2026, 3, 25),
        )

        assert tracker.companies["acme-corp"]["status"] == "interview"
        assert tracker.companies["acme-corp"]["interest"] == 5
        assert tracker.companies["acme-corp"]["current_state"] == "Onsite"


class TestCompanyNoteLinkExtraction:
    """Tests for extracting company note links from tracker."""

    def test_parse_company_note_link(self):
        """Should parse company note link from tracker entry."""
        from job_search_mcp.notes.tracker import parse_company_tracking

        text = """# Company Tracking

## Active Interview Pipeline

### Acme Corp
- **Status:** active
- **Company Note:** [[Companies/Acme Corp]]

"""
        tracker = parse_company_tracking(text)
        assert "acme-corp" in tracker.companies
        company = tracker.companies["acme-corp"]
        assert company["company_note"] == "[[Companies/Acme Corp]]"
        assert company["company_note_link"] == "Companies/Acme Corp"
        assert company["company_note_path"] == "Companies/Acme Corp.md"

    def test_parse_company_note_link_with_alias(self):
        """Should parse company note link with alias."""
        from job_search_mcp.notes.tracker import parse_company_tracking

        text = """# Company Tracking

## Active Interview Pipeline

### Beta Inc
- **Status:** waiting
- **Company Note:** [[Companies/Beta Inc|Beta]]

"""
        tracker = parse_company_tracking(text)
        assert "beta-inc" in tracker.companies
        company = tracker.companies["beta-inc"]
        assert company["company_note"] == "[[Companies/Beta Inc|Beta]]"
        assert company["company_note_link"] == "Companies/Beta Inc"
        assert company["company_note_path"] == "Companies/Beta Inc.md"

    def test_upsert_preserves_company_note_link(self):
        """Should preserve company note link when upserting."""
        from job_search_mcp.notes.tracker import upsert_company_tracking_entry, CompanyTracking

        tracker = CompanyTracking()
        tracker = upsert_company_tracking_entry(
            tracker,
            company_key="acme-corp",
            company_name="Acme Corp",
            status="active",
            interest=4,
            current_state="Phone screen",
            next_action="Follow up",
            notes="[[Companies/Acme Corp]]",
        )
        
        assert tracker.companies["acme-corp"]["notes"] == "[[Companies/Acme Corp]]"

    def test_upsert_defaults_company_note_link(self):
        """Should default company note link when none provided."""
        from job_search_mcp.notes.tracker import upsert_company_tracking_entry, CompanyTracking

        tracker = CompanyTracking()
        tracker = upsert_company_tracking_entry(
            tracker,
            company_key="acme-corp",
            company_name="Acme Corp",
            status="active",
            interest=4,
            current_state="Phone screen",
            next_action="Follow up",
            # No notes provided
        )
        
        assert tracker.companies["acme-corp"]["notes"] == "[[Companies/Acme Corp]]"
