"""Tests for application note parsing and rendering."""
import pytest
from datetime import date
from job_search_mcp.models import ApplicationRecord, ApplicationStatus, InterviewEvent, Task, TaskState


class TestParseApplicationNote:
    """Tests for parsing application notes."""

    def test_parse_minimal_application_note(self):
        """Should parse a minimal application note with frontmatter."""
        from job_search_mcp.notes.application import parse_application_note

        text = """---
tags:
  - job-search
  - application
company: Acme Corp
company_key: acme-corp
role: Senior Engineer
application_key: acme-corp-senior-engineer
status: applied
created: 2026-03-01
last_updated: 2026-03-07
---

# Acme Corp - Senior Engineer

## Snapshot

## Materials

## Interview Process

## Role-Specific Notes

## Tasks

## Outcome
"""
        record = parse_application_note(text)
        assert record.company == "Acme Corp"
        assert record.company_key == "acme-corp"
        assert record.role == "Senior Engineer"
        assert record.application_key == "acme-corp-senior-engineer"
        assert record.status == ApplicationStatus.APPLIED
        assert record.created == date(2026, 3, 1)

    def test_parse_application_note_with_snapshot(self):
        """Should parse application note with snapshot fields."""
        from job_search_mcp.notes.application import parse_application_note

        text = """---
tags:
  - job-search
  - application
company: Acme Corp
company_key: acme-corp
role: Senior Engineer
application_key: acme-corp-senior-engineer
status: interview
created: 2026-03-01
last_updated: 2026-03-07
---

# Acme Corp - Senior Engineer

## Snapshot
- **Company:** [[Companies/Acme Corp]]
- **Role:** Senior Engineer
- **Status:** interview
- **Applied on:** 2026-03-05
- **Current stage:** Phone screen
- **Next action:** Prepare for onsite
- **Due:** 2026-03-15
- **Priority / Interest:** 4
- **Comp:** $180-220k
- **Location:** San Francisco

## Materials

## Interview Process

## Role-Specific Notes

## Tasks

## Outcome
"""
        record = parse_application_note(text)
        assert record.current_stage == "Phone screen"
        assert record.next_action == "Prepare for onsite"
        assert record.due_date == date(2026, 3, 15)
        assert record.priority_interest == 4
        assert record.comp == "$180-220k"

    def test_parse_application_note_with_interview_process(self):
        """Should parse application note with interview process entries."""
        from job_search_mcp.notes.application import parse_application_note

        text = """---
tags:
  - job-search
  - application
company: Acme Corp
company_key: acme-corp
role: Senior Engineer
application_key: acme-corp-senior-engineer
status: interview
created: 2026-03-01
last_updated: 2026-03-07
---

# Acme Corp - Senior Engineer

## Snapshot

## Materials

## Interview Process
| Date | Stage | People | Outcome | Notes |
|------|-------|--------|---------|-------|
| 2026-03-10 | Phone screen | John Doe | Passed | Went well |
| 2026-03-20 | Onsite | Team | Pending | 4 rounds |

## Role-Specific Notes

## Tasks

## Outcome
"""
        record = parse_application_note(text)
        assert len(record.interview_process) == 2
        assert record.interview_process[0].date == date(2026, 3, 10)
        assert record.interview_process[0].stage == "Phone screen"
        assert record.interview_process[0].people == "John Doe"
        assert record.interview_process[0].outcome == "Passed"


class TestRenderApplicationNote:
    """Tests for rendering application notes."""

    def test_render_minimal_application_note(self):
        """Should render a minimal application note."""
        from job_search_mcp.notes.application import render_application_note

        record = ApplicationRecord(
            company="Acme Corp",
            company_key="acme-corp",
            role="Senior Engineer",
            application_key="acme-corp-senior-engineer",
            status=ApplicationStatus.APPLIED,
            created=date(2026, 3, 1),
            last_updated=date(2026, 3, 7),
        )
        text = render_application_note(record)
        assert "company: Acme Corp" in text
        assert "role: Senior Engineer" in text
        assert "status: applied" in text
        assert "## Snapshot" in text
        assert "## Materials" in text

    def test_render_application_note_with_all_fields(self):
        """Should render an application note with all fields."""
        from job_search_mcp.notes.application import render_application_note

        record = ApplicationRecord(
            company="Acme Corp",
            company_key="acme-corp",
            role="Senior Engineer",
            application_key="acme-corp-senior-engineer",
            status=ApplicationStatus.INTERVIEW,
            created=date(2026, 3, 1),
            last_updated=date(2026, 3, 7),
            current_stage="Phone screen",
            next_action="Prepare for onsite",
            due_date=date(2026, 3, 15),
            priority_interest=4,
            comp="$180-220k",
            location="San Francisco",
        )
        text = render_application_note(record)
        assert "**Current stage:** Phone screen" in text
        assert "**Next action:** Prepare for onsite" in text
        assert "**Priority / Interest:** 4" in text


class TestUpsertApplicationInterviewEvent:
    """Tests for upserting interview events."""

    def test_add_interview_event(self):
        """Should add a new interview event."""
        from job_search_mcp.notes.application import upsert_application_interview_event

        record = ApplicationRecord(
            company="Acme Corp",
            company_key="acme-corp",
            role="Senior Engineer",
            application_key="acme-corp-senior-engineer",
            status=ApplicationStatus.INTERVIEW,
            created=date(2026, 3, 1),
            last_updated=date(2026, 3, 7),
        )

        event = InterviewEvent(
            date=date(2026, 3, 10),
            stage="Phone screen",
            people="John Doe",
            outcome="Passed",
            notes="Went well",
        )

        updated = upsert_application_interview_event(record, event)

        assert len(updated.interview_process) == 1
        assert updated.interview_process[0].stage == "Phone screen"
        assert updated.interview_process[0].outcome == "Passed"
