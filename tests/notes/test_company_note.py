"""Tests for company note parsing and rendering."""
import pytest
from datetime import date
from job_search_mcp.models import CompanyRecord, CompanyStatus, TimelineEntry


class TestParseCompanyNote:
    """Tests for parsing company notes."""

    def test_parse_minimal_company_note(self):
        """Should parse a minimal company note with frontmatter."""
        from job_search_mcp.notes.company import parse_company_note

        text = """---
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
        record = parse_company_note(text)
        assert record.company == "Acme Corp"
        assert record.company_key == "acme-corp"
        assert record.status == CompanyStatus.ACTIVE
        assert record.interest == 4
        assert record.last_updated == date(2026, 3, 7)

    def test_parse_company_note_with_snapshot(self):
        """Should parse company note with snapshot fields."""
        from job_search_mcp.notes.company import parse_company_note

        text = """---
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
- **Status:** active
- **Interest:** 4
- **Primary next action:** Follow up with recruiter
- **Next action due:** 2026-03-10
- **Best current role:** Senior Engineer
- **Location:** San Francisco
- **Commute fit:** Good
- **Comp / range:** $180-220k

## Notes

## Contacts

## Active Applications

## Context

## Timeline

## Open Questions

## Related
"""
        record = parse_company_note(text)
        assert record.primary_next_action == "Follow up with recruiter"
        assert record.next_action_due == date(2026, 3, 10)
        assert record.best_current_role == "Senior Engineer"
        assert record.location == "San Francisco"
        assert record.comp_range == "$180-220k"

    def test_parse_company_note_with_timeline(self):
        """Should parse company note with timeline entries."""
        from job_search_mcp.notes.company import parse_company_note

        text = """---
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
| Date | Type | Summary | Source | Linked Note |
|------|------|---------|--------|-------------|
| 2026-03-01 | recruiter_message | Recruiter reached out | email:12345 | |
| 2026-03-05 | interview_scheduled | Phone screen on Friday | calendar:abc | [[Calls/2026-03-05]] |

## Open Questions

## Related
"""
        record = parse_company_note(text)
        assert len(record.timeline) == 2
        assert record.timeline[0].date == date(2026, 3, 1)
        assert record.timeline[0].entry_type == "recruiter_message"
        assert record.timeline[0].summary == "Recruiter reached out"
        assert record.timeline[0].source == "email:12345"


class TestRenderCompanyNote:
    """Tests for rendering company notes."""

    def test_render_minimal_company_note(self):
        """Should render a minimal company note."""
        from job_search_mcp.notes.company import render_company_note

        record = CompanyRecord(
            company="Acme Corp",
            company_key="acme-corp",
            status=CompanyStatus.ACTIVE,
            interest=4,
            last_updated=date(2026, 3, 7),
        )
        text = render_company_note(record)
        assert "company: Acme Corp" in text
        assert "company_key: acme-corp" in text
        assert "status: active" in text
        assert "## Snapshot" in text
        assert "## Notes" in text

    def test_render_company_note_with_all_fields(self):
        """Should render a company note with all fields."""
        from job_search_mcp.notes.company import render_company_note

        record = CompanyRecord(
            company="Acme Corp",
            company_key="acme-corp",
            status=CompanyStatus.ACTIVE,
            interest=4,
            last_updated=date(2026, 3, 7),
            primary_next_action="Follow up",
            next_action_due=date(2026, 3, 10),
            best_current_role="Senior Engineer",
            location="San Francisco",
            commute_fit="Good",
            comp_range="$180-220k",
            notes="Some notes here",
        )
        text = render_company_note(record)
        assert "**Primary next action:** Follow up" in text
        assert "**Next action due:** 2026-03-10" in text
        assert "**Best current role:** Senior Engineer" in text
        assert "## Notes" in text
        assert "Some notes here" in text


class TestAppendCompanyTimeline:
    """Tests for appending timeline entries."""

    def test_append_timeline_entry(self):
        """Should append a timeline entry without duplicating source marker."""
        from job_search_mcp.notes.company import append_company_timeline
        from job_search_mcp.models import CompanySignal, SignalType

        record = CompanyRecord(
            company="Acme Corp",
            company_key="acme-corp",
            status=CompanyStatus.ACTIVE,
            interest=4,
            last_updated=date(2026, 3, 7),
            timeline=[
                TimelineEntry(
                    date=date(2026, 3, 1),
                    entry_type="recruiter_message",
                    summary="Recruiter reached out",
                    source="email:12345",
                )
            ],
        )

        signal = CompanySignal(
            company_key="acme-corp",
            signal_type=SignalType.CALENDAR_EVENT,
            summary="Phone screen scheduled",
            source_marker="calendar:abc",
            due_date=date(2026, 3, 10),
        )

        updated = append_company_timeline(record, signal)

        # Should have 2 entries now
        assert len(updated.timeline) == 2
        # New entry should have the signal info
        assert updated.timeline[1].entry_type == "calendar_event"
        assert updated.timeline[1].summary == "Phone screen scheduled"
        assert updated.timeline[1].source == "calendar:abc"

    def test_skip_duplicate_source_marker(self):
        """Should not append if source marker already exists."""
        from job_search_mcp.notes.company import append_company_timeline
        from job_search_mcp.models import CompanySignal, SignalType

        record = CompanyRecord(
            company="Acme Corp",
            company_key="acme-corp",
            status=CompanyStatus.ACTIVE,
            interest=4,
            last_updated=date(2026, 3, 7),
            timeline=[
                TimelineEntry(
                    date=date(2026, 3, 1),
                    entry_type="recruiter_message",
                    summary="Recruiter reached out",
                    source="email:12345",
                )
            ],
        )

        # Same source marker
        signal = CompanySignal(
            company_key="acme-corp",
            signal_type=SignalType.RECRUITER_MESSAGE,
            summary="Duplicate message",
            source_marker="email:12345",
        )

        updated = append_company_timeline(record, signal)

        # Should still have only 1 entry
        assert len(updated.timeline) == 1
