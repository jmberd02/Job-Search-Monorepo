"""Tests for daily note parsing and rendering."""
import pytest
from datetime import date, time


class TestParseDailyNote:
    """Tests for parsing daily notes."""

    def test_parse_minimal_daily_note(self):
        """Should parse a minimal daily note."""
        from job_search_mcp.notes.daily import parse_daily_note

        text = """---
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
        daily = parse_daily_note(text)
        assert daily.date == date(2026, 3, 7)

    def test_parse_daily_note_with_schedule(self):
        """Should parse a daily note with schedule."""
        from job_search_mcp.notes.daily import parse_daily_note

        text = """---
tags:
  - job-search
  - daily
date: 2026-03-07
---

# 2026-03-07

## Schedule
- 9:00 AM - 11:00 AM: LeetCode practice
- 2:00 PM - 3:00 PM: Interview prep

## Daily Activity

## Schedule vs Activity
"""
        daily = parse_daily_note(text)
        assert len(daily.schedule) == 2
        assert daily.schedule[0].start_time == time(9, 0)
        assert "LeetCode practice" in daily.schedule[0].description

    def test_parse_daily_note_with_activity(self):
        """Should parse a daily note with activity log."""
        from job_search_mcp.notes.daily import parse_daily_note

        text = """---
tags:
  - job-search
  - daily
date: 2026-03-07
---

# 2026-03-07

## Schedule

## Daily Activity
- 9:00 AM - 11:00 AM: LeetCode practice - Done - Solved 3 problems
- 2:00 PM - 3:00 PM: Interview prep - Partial - Only had time for system design

## Schedule vs Activity
"""
        daily = parse_daily_note(text)
        assert len(daily.activity) == 2
        assert daily.activity[0].status == "Done"
        assert "Solved 3 problems" in daily.activity[0].note


class TestRenderDailyNote:
    """Tests for rendering daily notes."""

    def test_render_minimal_daily_note(self):
        """Should render a minimal daily note."""
        from job_search_mcp.notes.daily import render_daily_note, DailyNote

        daily = DailyNote(date=date(2026, 3, 7))
        text = render_daily_note(daily)
        assert "# 2026-03-07" in text
        assert "## Schedule" in text
        assert "## Daily Activity" in text
        assert "## Schedule vs Activity" in text

    def test_render_daily_note_with_schedule(self):
        """Should render a daily note with schedule."""
        from job_search_mcp.notes.daily import render_daily_note, DailyNote, ScheduleBlock

        daily = DailyNote(date=date(2026, 3, 7))
        daily.schedule = [
            ScheduleBlock(start_time=time(9, 0), end_time=time(11, 0), description="LeetCode practice"),
            ScheduleBlock(start_time=time(14, 0), end_time=time(15, 0), description="Interview prep"),
        ]
        text = render_daily_note(daily)
        assert "9:00 AM - 11:00 AM" in text
        assert "LeetCode practice" in text
        assert "2:00 PM - 3:00 PM" in text


class TestAppendDailyActivity:
    """Tests for appending daily activity."""

    def test_append_activity_block(self):
        """Should append an activity block to daily note."""
        from job_search_mcp.notes.daily import append_daily_activity, DailyNote

        daily = DailyNote(date=date(2026, 3, 7))
        daily = append_daily_activity(
            daily,
            start_time=time(9, 0),
            end_time=time(11, 0),
            description="LeetCode practice",
            status="Done",
            note="Solved 3 problems",
        )

        assert len(daily.activity) == 1
        assert daily.activity[0].description == "LeetCode practice"
        assert daily.activity[0].status == "Done"
        assert "Solved 3 problems" in daily.activity[0].note


class TestRefreshScheduleVsActivity:
    """Tests for refreshing schedule vs activity comparison."""

    def test_refresh_comparison(self):
        """Should generate schedule vs activity comparison."""
        from job_search_mcp.notes.daily import refresh_schedule_vs_activity, DailyNote, ScheduleBlock, ActivityBlock

        daily = DailyNote(date=date(2026, 3, 7))
        daily.schedule = [
            ScheduleBlock(start_time=time(9, 0), end_time=time(11, 0), description="LeetCode practice"),
        ]
        daily.activity = [
            ActivityBlock(start_time=time(9, 0), end_time=time(11, 0), description="LeetCode practice", status="Done", note=""),
        ]

        daily = refresh_schedule_vs_activity(daily)

        assert daily.schedule_vs_activity is not None
        assert "LeetCode practice" in daily.schedule_vs_activity
