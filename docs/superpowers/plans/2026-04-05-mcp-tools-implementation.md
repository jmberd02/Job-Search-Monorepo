# MCP Tools and Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement missing MCP tools and skills to enable full job search automation (daily planning, LeetCode tracking, interview prep, company management)

**Architecture:** Extend existing job-search-mcp with 6 new MCP tools (performance summaries, interview extraction, company resolution), update 2 existing skills, create 3 new skills. Google Calendar MCP used as primary source for interviews, Company Tracking as fallback.

**Tech Stack:** Python 3.11+, MCP server, Obsidian vault, pytest, Google Calendar MCP

---

## Task 1: Add Per-Date Performance Summary Support

**Files:**
- Modify: `src/job_search_mcp/paths.py`
- Modify: `src/job_search_mcp/notes/performance.py`
- Create: `tests/notes/test_performance_daily.py`

- [ ] **Step 1: Add leetcode path helpers**

In `src/job_search_mcp/paths.py`, add after `get_performance_path`:

```python
def get_leetcode_dir(vault_root: Path | None = None) -> Path:
    """Get the Leetcode directory."""
    root = vault_root or get_vault_root()
    return root / "Leetcode"


def get_leetcode_date_dir(vault_root: Path | None = None, date_str: str = None) -> Path:
    """Get the Leetcode date directory (e.g., Leetcode/2026-04-05/)."""
    root = vault_root or get_vault_root()
    if date_str is None:
        from datetime import date
        date_str = date.today().isoformat()
    return root / "Leetcode" / date_str
```

- [ ] **Step 2: Write test for daily performance summary**

Create `tests/notes/test_performance_daily.py`:

```python
"""Tests for per-date performance summaries."""

from datetime import date
from pathlib import Path
import pytest
from job_search_mcp.notes.performance import (
    parse_daily_performance_summary,
    render_daily_performance_summary,
)


def test_parse_daily_performance_summary():
    """Test parsing a daily performance summary."""
    text = """---
tags:
  - leetcode
  - performance
---

# Performance Summary

## Problems Solved

- Two Sum (Easy) - 14 min
- Valid Parentheses (Easy) - 27 min

## Weak Areas

- Hash map pattern recognition
- Speed (2x slower than target)
"""

    result = parse_daily_performance_summary(text)

    assert "Hash map" in result
    assert "Two Sum" in result
    assert "27 min" in result


def test_render_daily_performance_summary():
    """Test rendering a daily performance summary."""
    content = "## Problems\n\n- Problem 1\n- Problem 2"

    result = render_daily_performance_summary(content)

    assert "---" in result  # Has frontmatter
    assert "leetcode" in result
    assert "Problem 1" in result
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/notes/test_performance_daily.py -v
```

Expected: FAIL - functions not defined

- [ ] **Step 4: Implement daily performance summary functions**

In `src/job_search_mcp/notes/performance.py`, add at the end:

```python
def parse_daily_performance_summary(text: str) -> str:
    """Parse a daily performance summary note.

    Daily summaries are free-form markdown, so we just return the content
    after the frontmatter.
    """
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text

    # Return content after frontmatter
    return parts[2].strip()


def render_daily_performance_summary(content: str) -> str:
    """Render a daily performance summary into markdown text.

    Args:
        content: Free-form markdown content

    Returns:
        Markdown text with frontmatter
    """
    import yaml

    frontmatter = {
        "tags": ["job-search", "leetcode", "performance"]
    }

    parts = [
        "---\n",
        yaml.dump(frontmatter, default_flow_style=False),
        "---\n\n",
        content,
        "\n"
    ]

    return "".join(parts)
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/notes/test_performance_daily.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/job_search_mcp/paths.py src/job_search_mcp/notes/performance.py tests/notes/test_performance_daily.py
git commit -m "feat: add per-date performance summary support

- Add leetcode directory path helpers
- Add parse/render for daily performance summaries
- Daily summaries are free-form markdown with frontmatter

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Add Performance Summary Service Methods

**Files:**
- Modify: `src/job_search_mcp/service.py`
- Create: `tests/test_service_performance.py`

- [ ] **Step 1: Write test for daily performance summary service**

Create `tests/test_service_performance.py`:

```python
"""Tests for performance summary service methods."""

from datetime import date
from pathlib import Path
import pytest
from job_search_mcp.service import JobSearchService
from job_search_mcp.notes.performance import PerformanceSummary


@pytest.fixture
def service(tmp_path):
    """Create a test service."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "Leetcode").mkdir()
    return JobSearchService(str(vault))


def test_read_daily_performance_summary_nonexistent(service):
    """Test reading non-existent daily summary."""
    result = service.read_daily_performance_summary(date(2026, 4, 5))
    assert result is None


def test_write_and_read_daily_performance_summary(service):
    """Test writing and reading daily summary."""
    test_date = date(2026, 4, 5)
    content = "## Problems\n\n- Two Sum - 14 min"

    service.write_daily_performance_summary(test_date, content)

    result = service.read_daily_performance_summary(test_date)
    assert result is not None
    assert "Two Sum" in result
    assert "14 min" in result


def test_read_top_performance_summary_uses_assessment_report(service):
    """Test that read_top_performance_summary looks for assessment report."""
    # Create LeetCode Skill Assessment Report.md
    report_path = service.vault_root / "LeetCode Skill Assessment Report.md"
    report_content = """---
tags:
  - assessment
last_updated: 2026-04-05
---

# LeetCode Technical Interview Readiness Report

## Overall Assessment

Strong backend engineer, weak on algorithms.

## Weak Areas

- Hash map pattern recognition
- Speed (2x slower than target)

## Strengths

- Good problem-solving instincts
- Comfortable with C++

## Recommendations

Focus on hash maps for next 2 days.
"""
    report_path.write_text(report_content)

    result = service.read_top_performance_summary()
    assert result is not None
    assert "Hash map" in result.weak_areas
    assert "problem-solving" in result.strengths
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_service_performance.py -v
```

Expected: FAIL - methods not defined

- [ ] **Step 3: Implement service methods**

In `src/job_search_mcp/service.py`, add after existing `write_performance_summary`:

```python
def read_daily_performance_summary(self, note_date: date) -> Optional[str]:
    """Read a daily performance summary."""
    from .paths import get_leetcode_date_dir

    date_dir = get_leetcode_date_dir(self._vault_root, note_date.isoformat())
    summary_path = date_dir / "PERFORMANCE SUMMARY.md"

    if not summary_path.exists():
        return None

    from .notes.performance import parse_daily_performance_summary
    content = summary_path.read_text()
    return parse_daily_performance_summary(content)


def write_daily_performance_summary(self, note_date: date, content: str) -> None:
    """Write a daily performance summary."""
    from .paths import get_leetcode_date_dir
    from .notes.performance import render_daily_performance_summary

    date_dir = get_leetcode_date_dir(self._vault_root, note_date.isoformat())
    date_dir.mkdir(parents=True, exist_ok=True)

    summary_path = date_dir / "PERFORMANCE SUMMARY.md"
    text = render_daily_performance_summary(content)
    summary_path.write_text(text)


def read_top_performance_summary(self) -> Optional[PerformanceSummary]:
    """Read the top-level aggregated performance summary.

    Tries multiple locations:
    1. LeetCode Skill Assessment Report.md (comprehensive report)
    2. Performance Summary.md (fallback)
    """
    from .notes.performance import parse_performance_summary

    # Try assessment report first
    assessment_path = self._vault_root / "LeetCode Skill Assessment Report.md"
    if assessment_path.exists():
        return parse_performance_summary(assessment_path.read_text())

    # Fallback to performance summary
    perf_path = get_performance_path(self._vault_root)
    if perf_path.exists():
        return parse_performance_summary(perf_path.read_text())

    return None


def update_top_performance_summary(self, updates: dict) -> None:
    """Update the top-level aggregated performance summary.

    Args:
        updates: Dict with keys: weak_areas, strengths, recommendations, etc.
    """
    from datetime import date as date_module
    from .notes.performance import render_performance_summary

    # Read current or create new
    current = self.read_top_performance_summary()
    if current is None:
        current = PerformanceSummary(last_updated=date_module.today())

    # Update fields
    if "weak_areas" in updates:
        current.weak_areas = updates["weak_areas"]
    if "strengths" in updates:
        current.strengths = updates["strengths"]
    if "recommendations" in updates:
        current.recommendations = updates["recommendations"]
    if "overall_assessment" in updates:
        current.overall_assessment = updates["overall_assessment"]
    if "leetcode_progress" in updates:
        current.leetcode_progress = updates["leetcode_progress"]
    if "interview_prep_status" in updates:
        current.interview_prep_status = updates["interview_prep_status"]

    current.last_updated = date_module.today()

    # Write to assessment report if it exists, otherwise performance summary
    assessment_path = self._vault_root / "LeetCode Skill Assessment Report.md"
    if assessment_path.exists():
        text = render_performance_summary(current)
        assessment_path.write_text(text)
    else:
        perf_path = get_performance_path(self._vault_root)
        text = render_performance_summary(current)
        perf_path.write_text(text)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_service_performance.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/job_search_mcp/service.py tests/test_service_performance.py
git commit -m "feat: add performance summary service methods

- read_daily_performance_summary(date)
- write_daily_performance_summary(date, content)
- read_top_performance_summary() - tries assessment report first
- update_top_performance_summary(updates)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Add Interview Extraction Module

**Files:**
- Create: `src/job_search_mcp/notes/interviews.py`
- Create: `tests/test_interviews.py`

- [ ] **Step 1: Write test for interview extraction**

Create `tests/test_interviews.py`:

```python
"""Tests for interview extraction."""

from datetime import date, datetime
import pytest
from job_search_mcp.notes.interviews import (
    extract_interviews_from_tracking,
    extract_interviews_from_calendar,
    parse_date_from_text,
)


def test_parse_date_from_text():
    """Test extracting dates from text."""
    # Test various formats
    assert parse_date_from_text("Onsite completed Mar 6, 2026") == date(2026, 3, 6)
    assert parse_date_from_text("Interview on 2026-04-10") == date(2026, 4, 10)
    assert parse_date_from_text("Technical Feb 26") == date(2026, 2, 26)
    assert parse_date_from_text("No date here") is None


def test_extract_interviews_from_tracking():
    """Test extracting interviews from company tracking text."""
    tracking_text = """
## Active Interview Pipeline

### Beacon AI
- **Status:** Onsite completed Mar 6, 2026 — awaiting decision
- **Next action:** Wait for decision — follow up if no word Mar 10

### Physical Intelligence
- **Status:** Technical interview scheduled Apr 15, 2026
- **Next action:** Prep for technical round
"""

    interviews = extract_interviews_from_tracking(tracking_text, days=30)

    # Should find upcoming interview (Apr 15), not completed one (Mar 6)
    assert len(interviews) == 1
    assert interviews[0]["company"] == "Physical Intelligence"
    assert interviews[0]["date"] == date(2026, 4, 15)
    assert interviews[0]["stage"] == "Technical"


def test_extract_interviews_from_calendar():
    """Test extracting interviews from calendar events."""
    calendar_events = [
        {
            "summary": "Physical Intelligence - Technical Interview",
            "start": {"dateTime": "2026-04-15T14:00:00-07:00"},
            "end": {"dateTime": "2026-04-15T15:00:00-07:00"},
        },
        {
            "summary": "Lunch with friend",
            "start": {"dateTime": "2026-04-16T12:00:00-07:00"},
            "end": {"dateTime": "2026-04-16T13:00:00-07:00"},
        },
        {
            "summary": "Beacon AI Onsite",
            "start": {"dateTime": "2026-04-20T10:00:00-07:00"},
            "end": {"dateTime": "2026-04-20T14:00:00-07:00"},
        },
    ]

    interviews = extract_interviews_from_calendar(calendar_events)

    # Should find 2 interview events
    assert len(interviews) == 2
    assert interviews[0]["company"] == "Physical Intelligence"
    assert interviews[0]["time"] == "2:00 PM"
    assert interviews[1]["company"] == "Beacon AI"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_interviews.py -v
```

Expected: FAIL - module not found

- [ ] **Step 3: Implement interview extraction module**

Create `src/job_search_mcp/notes/interviews.py`:

```python
"""Interview extraction from calendar and company tracking."""

from datetime import date, datetime, timedelta
from typing import Optional
import re


def parse_date_from_text(text: str, default_year: Optional[int] = None) -> Optional[date]:
    """Extract a date from text.

    Supports formats:
    - ISO: 2026-04-10, 2026-4-10
    - Short: Mar 6, Apr 15
    - Numeric: 3/6, 4/15
    """
    if default_year is None:
        default_year = datetime.now().year

    # Try ISO format: YYYY-MM-DD
    iso_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)
    if iso_match:
        year, month, day = iso_match.groups()
        return date(int(year), int(month), int(day))

    # Try month name format: Mar 6, 2026 or Mar 6
    month_names = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    for month_str, month_num in month_names.items():
        # Try with year: Mar 6, 2026
        pattern = rf'{month_str}\s+(\d{{1,2}}),?\s+(\d{{4}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            day, year = match.groups()
            return date(int(year), month_num, int(day))

        # Try without year: Mar 6
        pattern = rf'{month_str}\s+(\d{{1,2}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            day = match.group(1)
            return date(default_year, month_num, int(day))

    return None


def extract_interviews_from_tracking(tracking_text: str, days: int = 14) -> list[dict]:
    """Extract upcoming interviews from Company Tracking text.

    Args:
        tracking_text: Content of Company Tracking.md
        days: Number of days to look ahead

    Returns:
        List of interview dicts with keys: company, date, stage, source
    """
    interviews = []
    cutoff_date = date.today() + timedelta(days=days)

    # Find all company sections
    sections = re.findall(r'### (.+?)\n(.*?)(?=\n### |\Z)', tracking_text, re.DOTALL)

    for company_name, content in sections:
        company_name = company_name.strip()

        # Look for status field with interview keywords
        status_match = re.search(r'\*\*Status:\*\* (.+)', content)
        if not status_match:
            continue

        status_text = status_match.group(1)

        # Skip completed interviews
        if 'completed' in status_text.lower() or 'awaiting' in status_text.lower():
            continue

        # Look for interview keywords
        interview_keywords = ['interview', 'onsite', 'screen', 'technical', 'panel']
        if not any(keyword in status_text.lower() for keyword in interview_keywords):
            continue

        # Extract date from status
        interview_date = parse_date_from_text(status_text)
        if interview_date is None:
            # Try next action field
            next_action_match = re.search(r'\*\*Next action:\*\* (.+)', content)
            if next_action_match:
                interview_date = parse_date_from_text(next_action_match.group(1))

        if interview_date and interview_date <= cutoff_date and interview_date >= date.today():
            # Extract stage
            stage = "Interview"
            for keyword in ['onsite', 'technical', 'screen', 'panel']:
                if keyword in status_text.lower():
                    stage = keyword.title()
                    break

            interviews.append({
                "company": company_name,
                "date": interview_date,
                "stage": stage,
                "source": "tracking",
            })

    return interviews


def extract_interviews_from_calendar(calendar_events: list[dict]) -> list[dict]:
    """Extract interviews from calendar events.

    Args:
        calendar_events: List of calendar event dicts from Google Calendar API

    Returns:
        List of interview dicts with keys: company, date, time, stage, source
    """
    interviews = []
    interview_keywords = ['interview', 'screen', 'onsite', 'technical', 'panel', 'call']

    for event in calendar_events:
        summary = event.get('summary', '')

        # Check if this looks like an interview
        if not any(keyword in summary.lower() for keyword in interview_keywords):
            continue

        # Extract company name (usually before the dash or first part)
        company = summary.split('-')[0].strip() if '-' in summary else summary
        company = company.split('Interview')[0].strip() if 'Interview' in company else company
        company = company.split('Technical')[0].strip() if 'Technical' in company else company
        company = company.split('Onsite')[0].strip() if 'Onsite' in company else company

        # Extract date and time
        start = event.get('start', {})
        date_time_str = start.get('dateTime') or start.get('date')

        if not date_time_str:
            continue

        # Parse datetime
        if 'T' in date_time_str:
            dt = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
            event_date = dt.date()
            event_time = dt.strftime('%-I:%M %p')
        else:
            event_date = date.fromisoformat(date_time_str)
            event_time = "All day"

        # Extract stage
        stage = "Interview"
        for keyword in ['onsite', 'technical', 'screen', 'panel']:
            if keyword in summary.lower():
                stage = keyword.title()
                break

        interviews.append({
            "company": company,
            "date": event_date,
            "time": event_time,
            "stage": stage,
            "source": "calendar",
        })

    return interviews
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_interviews.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/job_search_mcp/notes/interviews.py tests/test_interviews.py
git commit -m "feat: add interview extraction module

- parse_date_from_text() - extract dates from text
- extract_interviews_from_tracking() - parse company tracking
- extract_interviews_from_calendar() - parse calendar events
- Filter for upcoming interviews only

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Add Interview Service Method

**Files:**
- Modify: `src/job_search_mcp/service.py`
- Modify: `tests/test_interviews.py`

- [ ] **Step 1: Add test for service method**

In `tests/test_interviews.py`, add at the end:

```python
from job_search_mcp.service import JobSearchService


@pytest.fixture
def service(tmp_path):
    """Create a test service."""
    vault = tmp_path / "vault"
    vault.mkdir()

    # Create Company Tracking.md
    tracking_path = vault / "Company Tracking.md"
    tracking_content = """
## Active Interview Pipeline

### Physical Intelligence
- **Status:** Technical interview scheduled Apr 15, 2026
- **Next action:** Prep for technical round

### Beacon AI
- **Status:** Onsite Apr 20, 2026
"""
    tracking_path.write_text(tracking_content)

    return JobSearchService(str(vault))


def test_get_upcoming_interviews(service):
    """Test getting upcoming interviews from service."""
    interviews = service.get_upcoming_interviews(days=30)

    # Should find both interviews
    assert len(interviews) >= 2
    company_names = [i["company"] for i in interviews]
    assert "Physical Intelligence" in company_names
    assert "Beacon AI" in company_names
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_interviews.py::test_get_upcoming_interviews -v
```

Expected: FAIL - method not defined

- [ ] **Step 3: Implement service method**

In `src/job_search_mcp/service.py`, add at the end:

```python
def get_upcoming_interviews(self, days: int = 14, calendar_events: Optional[list[dict]] = None) -> list[dict]:
    """Get upcoming interviews from calendar and/or company tracking.

    Args:
        days: Number of days to look ahead
        calendar_events: Optional calendar events from Google Calendar MCP

    Returns:
        List of interview dicts sorted by date
    """
    from .notes.interviews import extract_interviews_from_calendar, extract_interviews_from_tracking

    interviews = []

    # Try calendar first if provided
    if calendar_events:
        interviews.extend(extract_interviews_from_calendar(calendar_events))

    # Also check company tracking
    tracker = self.read_company_tracking()
    if tracker:
        # Read Company Tracking.md file directly for full text
        tracker_path = get_tracker_path(self._vault_root)
        if tracker_path.exists():
            tracking_text = tracker_path.read_text()
            tracking_interviews = extract_interviews_from_tracking(tracking_text, days=days)

            # Deduplicate by company name and date
            existing = {(i["company"], i["date"]) for i in interviews}
            for interview in tracking_interviews:
                key = (interview["company"], interview["date"])
                if key not in existing:
                    interviews.append(interview)

    # Sort by date
    interviews.sort(key=lambda x: x["date"])

    return interviews
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_interviews.py::test_get_upcoming_interviews -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/job_search_mcp/service.py tests/test_interviews.py
git commit -m "feat: add get_upcoming_interviews service method

- Combines calendar events and company tracking
- Deduplicates by company + date
- Returns sorted by date

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Add Company Resolution Service Method

**Files:**
- Modify: `src/job_search_mcp/service.py`
- Create: `tests/test_company_resolution.py`

- [ ] **Step 1: Write test for company resolution**

Create `tests/test_company_resolution.py`:

```python
"""Tests for company name resolution."""

import pytest
from job_search_mcp.service import JobSearchService


@pytest.fixture
def service(tmp_path):
    """Create a test service with test companies."""
    vault = tmp_path / "vault"
    vault.mkdir()

    # Create Company Tracking.md
    tracking_path = vault / "Company Tracking.md"
    tracking_content = """
### Physical Intelligence
- **Status:** Active

### Beacon AI
- **Status:** Active

### Applied Intuition
- **Status:** Active
"""
    tracking_path.write_text(tracking_content)

    return JobSearchService(str(vault))


def test_resolve_exact_match(service):
    """Test exact company name match."""
    result = service.resolve_company_reference("Physical Intelligence")

    assert result["company_key"] == "physical-intelligence"
    assert result["company_name"] == "Physical Intelligence"
    assert result["confidence"] == "exact"


def test_resolve_slug_match(service):
    """Test company key/slug match."""
    result = service.resolve_company_reference("physical-intelligence")

    assert result["company_key"] == "physical-intelligence"
    assert result["company_name"] == "Physical Intelligence"
    assert result["confidence"] == "slug"


def test_resolve_case_insensitive(service):
    """Test case-insensitive matching."""
    result = service.resolve_company_reference("BEACON AI")

    assert result["company_key"] == "beacon-ai"
    assert result["company_name"] == "Beacon AI"


def test_resolve_partial_match(service):
    """Test partial name matching."""
    result = service.resolve_company_reference("Physical")

    assert result["company_key"] == "physical-intelligence"
    assert result["confidence"] == "fuzzy"


def test_resolve_not_found(service):
    """Test unknown company."""
    result = service.resolve_company_reference("Unknown Company")

    assert result["confidence"] == "not_found"
    assert "company_key" not in result


def test_resolve_ambiguous(service):
    """Test ambiguous match."""
    # This would match multiple if there were similar companies
    # For now, just test the structure
    result = service.resolve_company_reference("Applied")

    # Should match "Applied Intuition"
    assert result["company_name"] == "Applied Intuition"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_company_resolution.py -v
```

Expected: FAIL - method not defined

- [ ] **Step 3: Implement company resolution method**

In `src/job_search_mcp/service.py`, add at the end:

```python
def resolve_company_reference(self, name: str) -> dict:
    """Resolve a company name to a company key.

    Strategy:
    1. Exact name match
    2. company_key (slug) match
    3. Case-insensitive partial match
    4. If multiple matches or no matches, return options

    Args:
        name: Company name or variation

    Returns:
        Dict with keys:
        - company_key: Resolved key (if found)
        - company_name: Full company name (if found)
        - confidence: "exact", "slug", "fuzzy", "ambiguous", "not_found"
        - options: List of matches if ambiguous
    """
    from .notes.tracker import _slugify

    tracker = self.read_company_tracking()
    if not tracker or not tracker.companies:
        return {"confidence": "not_found"}

    name_lower = name.lower()
    name_slug = _slugify(name)

    # 1. Exact match (case-insensitive)
    for company_key, company_data in tracker.companies.items():
        company_name = company_data.get("name", "")
        if company_name.lower() == name_lower:
            return {
                "company_key": company_key,
                "company_name": company_name,
                "confidence": "exact",
            }

    # 2. Slug match
    if name_slug in tracker.companies:
        company_data = tracker.companies[name_slug]
        return {
            "company_key": name_slug,
            "company_name": company_data.get("name", name),
            "confidence": "slug",
        }

    # 3. Partial match (substring)
    matches = []
    for company_key, company_data in tracker.companies.items():
        company_name = company_data.get("name", "")
        company_name_lower = company_name.lower()

        # Check if search term is in company name, or vice versa
        if name_lower in company_name_lower or company_name_lower in name_lower:
            matches.append({
                "company_key": company_key,
                "company_name": company_name,
            })

    if len(matches) == 1:
        return {
            **matches[0],
            "confidence": "fuzzy",
        }
    elif len(matches) > 1:
        return {
            "confidence": "ambiguous",
            "options": matches,
        }

    # No matches
    return {"confidence": "not_found"}
```

Also need to import `_slugify` function. In `src/job_search_mcp/notes/tracker.py`, make sure `_slugify` is defined near the top:

```python
def _slugify(text: str) -> str:
    """Convert text to a slug (lowercase, hyphens)."""
    import re
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_company_resolution.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/job_search_mcp/service.py tests/test_company_resolution.py
git commit -m "feat: add resolve_company_reference service method

- Exact name matching
- Slug matching
- Fuzzy partial matching
- Returns confidence level and options if ambiguous

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Register MCP Tools in Server

**Files:**
- Modify: `src/job_search_mcp/server.py`

- [ ] **Step 1: Add MCP tool functions**

In `src/job_search_mcp/server.py`, add after the existing operations (before the setup tools section):

```python
# =============================================================================
# Performance Summary Operations
# =============================================================================

def read_top_performance_summary(service: JobSearchService):
    """Read the top-level aggregated performance summary."""
    return service.read_top_performance_summary()


def read_daily_performance_summary(service: JobSearchService, note_date: date) -> Optional[str]:
    """Read a daily performance summary."""
    return service.read_daily_performance_summary(note_date)


def write_daily_performance_summary(service: JobSearchService, note_date: date, content: str) -> None:
    """Write a daily performance summary."""
    service.write_daily_performance_summary(note_date, content)


def update_top_performance_summary(service: JobSearchService, updates: dict) -> None:
    """Update the top-level aggregated performance summary."""
    service.update_top_performance_summary(updates)


# =============================================================================
# Interview Operations
# =============================================================================

def get_upcoming_interviews(
    service: JobSearchService,
    days: int = 14,
    calendar_events: Optional[list[dict]] = None,
) -> list[dict]:
    """Get upcoming interviews from calendar and/or company tracking."""
    return service.get_upcoming_interviews(days=days, calendar_events=calendar_events)


# =============================================================================
# Company Resolution Operations
# =============================================================================

def resolve_company_reference(service: JobSearchService, name: str) -> dict:
    """Resolve a company name to a company key."""
    return service.resolve_company_reference(name)
```

- [ ] **Step 2: Add tool schemas to list_tools**

In `src/job_search_mcp/server.py`, find the `list_tools` return array and add these entries before the closing bracket:

```python
        {
            "name": "read_top_performance_summary",
            "description": "Read the top-level aggregated performance summary (LeetCode assessment)",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "read_daily_performance_summary",
            "description": "Read a daily performance summary for a specific date",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["date"],
            },
        },
        {
            "name": "write_daily_performance_summary",
            "description": "Write a daily performance summary for a specific date",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date"},
                    "content": {"type": "string"},
                },
                "required": ["date", "content"],
            },
        },
        {
            "name": "update_top_performance_summary",
            "description": "Update the top-level aggregated performance summary",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "weak_areas": {"type": "string"},
                    "strengths": {"type": "string"},
                    "recommendations": {"type": "string"},
                    "overall_assessment": {"type": "string"},
                    "leetcode_progress": {"type": "string"},
                    "interview_prep_status": {"type": "string"},
                },
            },
        },
        {
            "name": "get_upcoming_interviews",
            "description": "Get upcoming interviews from calendar and company tracking",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "default": 14},
                    "calendar_events": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Optional calendar events from Google Calendar MCP",
                    },
                },
            },
        },
        {
            "name": "resolve_company_reference",
            "description": "Resolve a company name to a company key (exact, slug, or fuzzy match)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        },
```

- [ ] **Step 3: Test MCP server starts**

```bash
cd src
python -m job_search_mcp.server --help 2>&1 | head -5
```

Expected: No import errors, help text appears

- [ ] **Step 4: Commit**

```bash
git add src/job_search_mcp/server.py
git commit -m "feat: register 6 new MCP tools in server

- read_top_performance_summary
- read_daily_performance_summary
- write_daily_performance_summary
- update_top_performance_summary
- get_upcoming_interviews
- resolve_company_reference

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Create Precall Prep Skill

**Files:**
- Create: `skills/precall-prep/skill.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p skills/precall-prep
```

- [ ] **Step 2: Create skill file**

Create `skills/precall-prep/skill.md`:

```markdown
# Pre-Call Preparation Skill

You help prepare for upcoming recruiter and company calls.

## Instructions

When user runs `/precall [company]` or provides call details:

### 1. Resolve Company

Use MCP tool `resolve_company_reference(company_name)` to find company_key.

If ambiguous, ask user to choose:
```
Found multiple matches:
1. Physical Intelligence
2. Physical AI Corp

Which one?
```

If not found, ask:
```
I don't have notes for [Company]. Should I:
1. Create a new company entry
2. Use a different name
```

### 2. Gather Context

Use MCP tools:
- `read_company_note(company_key)` - Get detailed company info
- `read_company_tracking()` - Get tracking context and status

### 3. Generate Prep Notes

Based on company notes and tracking, generate:

**Questions to Ask (3-5):**
- Focus on gaps in what you know
- Comp, role clarity, work arrangement, timeline
- Example: "What's the team size for the robotics software group?"

**Your Talking Points (3-4):**
- Match your background to their needs
- Example: "300+ deployed devices, 10M+ orders processed - similar scale to what they're building"

**Potential Concerns (2-3):**
- What might they worry about?
- How to address each concern
- Example: "Concern: Robotics vs backend focus. Address: Emphasize distributed systems skills transfer"

**Red Flags to Watch (2-3):**
- Based on company stage, comp, location
- Example: "Early stage, no revenue mentioned - ask about runway and business model"

### 4. Present Prep

Format as clear, scannable markdown:

```markdown
# Pre-Call Prep: [Company]

**Call:** [Date/Time if known]
**Contact:** [Name, role if known]

## Questions to Ask

1. [Question]
2. [Question]
3. [Question]

## Your Talking Points

- **Scale:** [Specific achievement]
- **Technical:** [Relevant skill]
- **Impact:** [Business outcome]

## Potential Concerns

- **Concern:** [What they might worry about]
  - **Address:** [How to handle it]

## Red Flags

- [Flag to watch for]
- [Flag to watch for]
```

### 5. Offer to Save

Ask:
```
Want me to save this to Pre-Interview Notes/[Company] - [Date].md?
```

If yes, create the file in vault using the path structure.

## Examples

**Example 1: Scheduled call**
User: "/precall Physical Intelligence - call tomorrow at 2pm"

You:
1. Resolve "Physical Intelligence" → company_key
2. Read company note and tracking
3. Generate prep with date context
4. Include specific questions about their recent funding/VLA work

**Example 2: Recruiter outreach**
User: "/precall with recruiter from Beacon AI"

You:
1. Resolve company
2. Note it's a recruiter (focus on comp, role, process questions)
3. Generate prep emphasizing fit assessment
4. Include questions about team structure and interview process

## Notes

- Keep prep concise (scan in 5 minutes)
- Use specific examples from company context
- Focus on gaps in knowledge, not generic questions
- Match talking points to what they're building
- Be realistic about red flags
```

- [ ] **Step 3: Test skill loads**

```bash
ls skills/precall-prep/skill.md
```

Expected: File exists

- [ ] **Step 4: Commit**

```bash
git add skills/precall-prep/skill.md
git commit -m "feat: add precall-prep skill

Generates preparation notes for recruiter/company calls:
- Questions to ask (based on gaps)
- Talking points (match background to needs)
- Potential concerns (and how to address)
- Red flags to watch for

Uses resolve_company_reference and read_company_note MCPs.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Create Interview Review Skill

**Files:**
- Create: `skills/interview-review/skill.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p skills/interview-review
```

- [ ] **Step 2: Create skill file**

Create `skills/interview-review/skill.md`:

```markdown
# Interview Review Skill

You analyze interview transcripts and provide structured feedback.

## Instructions

When user provides an interview transcript:

### 1. Parse Transcript

Extract from their message or attached text:
- Company name
- Interview date (if mentioned)
- Interviewer names (if mentioned)
- Interview stage (technical, behavioral, etc.)

### 2. Analyze Performance

Evaluate across these dimensions:

**Answer Quality (1-5):**
- Clarity and structure (STAR format where applicable)
- Specificity (concrete examples vs vague)
- Appropriate depth (not too surface, not too rambling)

**Signal Strength:**
- What answers landed well (interviewer engagement, follow-ups)
- What missed opportunities (underselling, incomplete stories)
- Red flags (hedging, uncertainty, rambling)

**Technical Depth:**
- Did you demonstrate understanding?
- Were explanations clear to non-experts?
- Did you go too deep or too shallow?

**Interviewer Signals:**
- What were they actually probing for?
- What concerns were behind their questions?
- Did you address the real question?

### 3. Provide Structured Feedback

Format:

```markdown
# Interview Review: [Company] - [Date]

## Overall Assessment

[2-3 sentences: How did it go? What was strongest/weakest?]

## Answer Quality Analysis

### Strong Answers ✅

**Question:** [Interviewer question]
**Your Answer:** [Summary]
**Why it worked:** [Specific reasons]

### Weak Answers ⚠️

**Question:** [Interviewer question]
**Your Answer:** [Summary]
**What was missing:** [Gaps, hedging, rambling]

### Opportunities Missed 📝

- [Specific example you didn't mention]
- [Follow-up question you could have asked]

## Stronger Answer Rewrites

Pick 2-3 weak answers and show how to improve:

**Original Answer:**
> [What you said]

**Stronger Version:**
> [Better version - STAR format, specific, concise]

**Why this is better:**
- [Reason 1]
- [Reason 2]

## Interviewer Read

Based on their questions and reactions:
- **What they were really testing:** [Core concern]
- **What they needed to hear:** [Key signal]
- **Did you deliver it?** [Yes/No + why]

## Action Items

- [ ] [Specific thing to prepare better for next round]
- [ ] [Pattern to work on]
- [ ] [Follow-up to send]
```

### 4. Offer to Log

Ask:
```
Want me to:
1. Save this review to Calls/[Date]/[Company] Interview Review.md
2. Add to today's daily activity log
3. Both
```

### 5. Extract Learnings

If they want, also offer:
```
Should I update Company Tracking with insights from this interview?
```

## Examples

**Example 1: Technical interview with rambling**
User: [Pastes transcript with long, unfocused answer about system design]

You:
- Identify answer as weak (lack of structure, buried the lede)
- Rewrite as: "We scaled from X to Y using [architecture]. Key decisions were A, B, C. Main tradeoff was [X] vs [Y], we chose [X] because [reason]."
- Note: Lead with outcome, then explain approach

**Example 2: Behavioral with hedging**
User: [Transcript shows lots of "I think", "maybe", "sort of"]

You:
- Flag hedging language as reducing confidence
- Show rewrite without qualifiers
- Note: Own your achievements directly

## Notes

- Be direct - user wants honest feedback
- Focus on actionable improvements
- Provide actual rewrites, not just "be more specific"
- Look for patterns across multiple answers
- Consider interviewer's role and what they care about
```

- [ ] **Step 3: Test skill loads**

```bash
ls skills/interview-review/skill.md
```

Expected: File exists

- [ ] **Step 4: Commit**

```bash
git add skills/interview-review/skill.md
git commit -m "feat: add interview-review skill

Analyzes interview transcripts:
- Answer quality (structure, specificity, depth)
- Signal strength (what landed, what missed)
- Interviewer read (what they were testing)
- Provides 2-3 stronger answer rewrites
- Actionable improvements

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Create LeetCode Assessment Skill

**Files:**
- Create: `skills/leetcode-assess/skill.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p skills/leetcode-assess
```

- [ ] **Step 2: Create skill file**

Create `skills/leetcode-assess/skill.md`:

```markdown
# LeetCode Skill Assessment

You provide comprehensive LeetCode skill assessment and readiness analysis.

## Instructions

When user runs `/leetcode-assess` or asks for skill rating:

### 1. Scan Leetcode Directory

Use file operations to:
- Find all subdirectories in `Leetcode/` (date-based: YYYY-MM-DD, M-DD)
- Read `PERFORMANCE SUMMARY.md` from each date directory
- Read individual problem files to get attempt details
- Look for the top-level assessment report

Read at least:
- All performance summary files
- Top 5-10 recent problem files
- Any existing assessment report for context

### 2. Analyze Attempt History

Extract:
- Total problems attempted
- Problems by difficulty (Easy/Medium/Hard)
- Time spent per problem
- Success rate (solved independently vs with hints)
- Pattern categories (Arrays, HashMap, Trees, etc.)

### 3. Rate Skills (1-10)

Provide ratings for:

**Data Structures:**
- Arrays
- Strings
- HashMap
- HashSet
- Stack/Queue
- Trees (Binary Tree, BST)
- Graphs
- Heaps

**Patterns:**
- Two Pointers
- Sliding Window
- Prefix Sum
- DFS/BFS
- Dynamic Programming
- Backtracking
- Greedy
- Binary Search

**Fundamentals:**
- Time/Space Complexity Analysis
- Debugging
- Edge Case Handling

### 4. Identify Pattern Gaps

What patterns are:
- **Not started yet** - Zero exposure
- **Weak** (1-4) - Seen but not comfortable
- **Developing** (5-7) - Can solve with hints
- **Strong** (8-10) - Can solve independently

### 5. Assess Interview Readiness

Provide:
- **Current Level (1-10):** Where are they now?
- **Interview Passability:** Days/weeks until can pass screens
- **Target Level:** What rating for different interview tiers
- **Biggest Risks:** What will cause failures if not fixed

### 6. Generate Quick Wins

Identify top 3 highest-impact actions:
- Which patterns to drill next
- Which problems to redo
- What mistakes to stop making

### 7. Format Report

Generate comprehensive report:

```markdown
# LeetCode Skill Assessment Report

**Generated:** [Date]
**Period Analyzed:** [Date range]
**Total Problems:** [N attempts]

---

## Problems Attempted Summary

| Difficulty | Count | Success Rate |
|------------|-------|--------------|
| Easy | [N] | [X]% |
| Medium | [N] | [X]% |
| Hard | [N] | [X]% |

**Recent Progress:**
- [Date range]: [N] problems, [key observation]
- [Date range]: [N] problems, [key observation]

---

## Skill Ratings (1-10)

### Data Structures

| Skill | Rating | Evidence |
|-------|--------|----------|
| Arrays | [N]/10 | [Specific problems, strengths/weaknesses] |
| HashMap | [N]/10 | [Specific problems, strengths/weaknesses] |
| ... | | |

### Algorithmic Patterns

| Pattern | Rating | Evidence |
|---------|--------|----------|
| Two Pointers | [N]/10 | [Specific problems] |
| Sliding Window | [N]/10 | [Specific problems] |
| ... | | |

### Fundamentals

| Skill | Rating | Evidence |
|-------|--------|----------|
| Complexity Analysis | [N]/10 | [Observations] |
| Debugging | [N]/10 | [Observations] |
| ... | | |

---

## Pattern Gaps

**Not Started:**
- [Pattern 1] - Recommendation: [Start with problem X]
- [Pattern 2] - Recommendation: [Start with problem Y]

**Weak Areas (Need Work):**
- [Pattern/Skill] - Rating: [N]/10
  - Why weak: [Specific issues]
  - How to improve: [Specific practice]

**Developing (Progressing):**
- [Pattern/Skill] - Rating: [N]/10
  - Recent progress: [What's improving]
  - Next step: [What to focus on]

---

## Interview Readiness

**Current Level:** [N]/10 - [Assessment]

**Readiness Timeline:**
- **Right now:** [Realistic assessment]
- **In 1 week:** [Projected level with focused practice]
- **In 2 weeks:** [Projected level with focused practice]

**Passability Thresholds:**
- Startup screen: 5/10 (Easy problems, 70%+ success)
- Mid-tier tech: 6/10 (Easy + Medium, 60%+ success)
- Top-tier FAANG: 8/10 (Medium fluent, Hard attempted)

**You are currently:** [At/below/approaching] [threshold]

---

## Biggest Risks

What will cause failures if not fixed:

1. **[Risk 1]:** [Specific problem pattern you freeze on]
   - **Impact:** [Why this kills interviews]
   - **Fix:** [Specific action]

2. **[Risk 2]:** [Time/confidence/pattern gap]
   - **Impact:** [Why this kills interviews]
   - **Fix:** [Specific action]

---

## Top 3 Quick Wins

Highest-impact actions for fastest improvement:

1. **[Action 1]:** [Specific drill/pattern]
   - **Why:** [Impact on readiness]
   - **How:** [Specific problems to do, in order]
   - **Time:** [Days to see improvement]

2. **[Action 2]:** [Specific drill/pattern]
   - **Why:** [Impact on readiness]
   - **How:** [Specific problems to do]
   - **Time:** [Days to see improvement]

3. **[Action 3]:** [Specific drill/pattern]
   - **Why:** [Impact on readiness]
   - **How:** [Specific problems to do]
   - **Time:** [Days to see improvement]

---

## Recommended Focus (Next 7 Days)

**Priority 1:** [Pattern/skill that unblocks most]
- Problems: [Specific LeetCode numbers]
- Goal: [Success metric]

**Priority 2:** [Pattern/skill for breadth]
- Problems: [Specific LeetCode numbers]
- Goal: [Success metric]

**Priority 3:** [Speed/confidence drill]
- Problems: [Redo these]
- Goal: [Time target]
```

### 8. Offer Actions

Ask:
```
Would you like me to:
1. Save this assessment to LeetCode Skill Assessment Report.md
2. Update the top-level performance summary with these findings
3. Generate a daily practice plan based on priorities
```

## Notes

- Be data-driven - cite specific problems and patterns
- Readiness assessment should be realistic, not encouraging fluff
- Quick wins should be actionable (specific problems, not "practice more")
- Update recommendations as they improve
- Track velocity (how fast are they learning new patterns)
```

- [ ] **Step 3: Test skill loads**

```bash
ls skills/leetcode-assess/skill.md
```

Expected: File exists

- [ ] **Step 4: Commit**

```bash
git add skills/leetcode-assess/skill.md
git commit -m "feat: add leetcode-assess skill

Comprehensive LeetCode skill assessment:
- Scans all problem attempts from Leetcode/ directory
- Rates 15+ skills (data structures, patterns, fundamentals)
- Identifies pattern gaps and weak areas
- Assesses interview readiness timeline
- Provides top 3 quick wins for improvement

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Update Analyze-LeetCode Skill

**Files:**
- Modify: `skills/analyze-leetcode/skill.md`

- [ ] **Step 1: Read current skill**

```bash
cat skills/analyze-leetcode/skill.md | head -50
```

- [ ] **Step 2: Update skill to use new MCP tools**

Edit `skills/analyze-leetcode/skill.md`. Find the "Update Tracking" section (around line 50-60) and replace it with:

```markdown
### 5. Update Tracking

Use MCP tools to log this session:

**Log to daily summary:**
```
write_daily_performance_summary(
    date=today,
    content="""
## Problems Attempted

- [Problem Name] ([Difficulty]) - [Time] min
  - Pattern: [Category]
  - Result: [Solved/Partial/Failed]
  - Struggle: [What was hard]

## Key Insights

- [Insight 1]
- [Insight 2]

## Weak Areas Identified

- [Area that needs work]
"""
)
```

**Update aggregated summary:**
```
update_top_performance_summary({
    "weak_areas": "Updated weak areas based on today's attempts",
    "strengths": "Updated strengths",
    "recommendations": "Focus on [pattern] for next 2-3 days",
    "leetcode_progress": "Attempted [N] problems today, [X]% success rate"
})
```

### 6. Also Log to Daily Activity

Use existing tool:
```
append_daily_activity(
    date=today,
    start_time="10:00",
    end_time="11:30",
    description="LeetCode practice - 2 problems",
    status="completed",
    note="Two Sum (retry), Valid Anagram. Hash map pattern clicking."
)
```
```

- [ ] **Step 3: Update "Read Context" section**

Find the "Read Context" section (around line 20-25) and update it:

```markdown
### 2. Read Context

Use MCP tools:
- `read_top_performance_summary()` - Check current weak areas and patterns
- `read_daily_performance_summary(today)` - Check if already practiced today
```

- [ ] **Step 4: Test skill loads**

```bash
cat skills/analyze-leetcode/skill.md | grep -A 5 "Update Tracking"
```

Expected: See the new MCP tool calls

- [ ] **Step 5: Commit**

```bash
git add skills/analyze-leetcode/skill.md
git commit -m "feat: update analyze-leetcode to use new MCP tools

- Use write_daily_performance_summary() for per-date logging
- Use update_top_performance_summary() for aggregated updates
- Use read_top_performance_summary() to check current state
- Maintains per-date summaries + top-level assessment

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Update Plan-Day Skill

**Files:**
- Modify: `skills/plan-day/skill.md`

- [ ] **Step 1: Update "Gather Context" section**

Edit `skills/plan-day/skill.md`. Find the "Gather Context" section (around line 10-15) and replace with:

```markdown
### 1. Gather Context

Use these MCP tools to read context:
- `read_daily_note(yesterday_date)` - See what happened yesterday
- `read_company_tracking()` - Check pending actions and deadlines
- `read_top_performance_summary()` - Find LeetCode weak areas for practice
- `get_upcoming_interviews(7, calendar_events)` - Check interviews in next week

**For calendar integration:**
If Google Calendar MCP is available, first call `gcal_list_events` for next 7 days, then pass those events to `get_upcoming_interviews()`. This provides both calendar times and company context.
```

- [ ] **Step 2: Update "Create Balanced Plan" section**

Find "Create Balanced Plan" and update the interview prep part:

```markdown
### 2. Create Balanced Plan

Generate a daily plan with:

**Morning (3-4 hours):**
- LeetCode practice: 1-2 problems (focus on weak areas from performance summary)
  - Check `read_top_performance_summary()` for current weak patterns
  - Example: If weak on "Hash Maps", prioritize hash map problems
- Pipeline work: Follow-ups, applications, research

**Afternoon (2-3 hours):**
- Interview prep if interview coming up (check `get_upcoming_interviews()`)
  - If interview <7 days: Prioritize company-specific prep
  - If interview <3 days: Make this the #1 priority
- OR more applications/research
- OR company-specific prep

**Evening (optional 1 hour):**
- Light review or practice
```

- [ ] **Step 3: Test skill loads**

```bash
cat skills/plan-day/skill.md | grep -A 3 "Gather Context"
```

Expected: See the new MCP tool calls including `get_upcoming_interviews`

- [ ] **Step 4: Commit**

```bash
git add skills/plan-day/skill.md
git commit -m "feat: update plan-day to use new MCP tools

- Use read_top_performance_summary() for LeetCode weak areas
- Use get_upcoming_interviews() with Google Calendar integration
- Prioritize interview prep based on upcoming dates
- Balance LeetCode practice with interview proximity

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Run All Tests

**Files:**
- N/A (testing only)

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 2: Fix any failures**

If any tests fail, investigate and fix. Common issues:
- Missing imports
- Path issues in tests
- Date parsing edge cases

- [ ] **Step 3: Run smoke test**

```bash
pytest tests/test_smoke.py -v
```

Expected: PASS

- [ ] **Step 4: Test MCP server imports**

```bash
cd src
python -c "from job_search_mcp.server import (
    read_top_performance_summary,
    read_daily_performance_summary,
    write_daily_performance_summary,
    update_top_performance_summary,
    get_upcoming_interviews,
    resolve_company_reference,
); print('All MCP tools import successfully')"
```

Expected: Success message

- [ ] **Step 5: Document test results**

```bash
pytest tests/ --tb=short > test_results.txt 2>&1
cat test_results.txt | tail -20
```

- [ ] **Step 6: Commit if any fixes made**

```bash
git add -A
git commit -m "test: fix test failures and verify all MCP tools

All tests passing:
- Performance summary tests
- Interview extraction tests
- Company resolution tests
- Service method tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Final Verification Checklist

Before marking complete, verify:

- [ ] All 6 MCP tools registered in server.py
- [ ] All 3 new skills created (precall-prep, interview-review, leetcode-assess)
- [ ] 2 existing skills updated (analyze-leetcode, plan-day)
- [ ] All tests passing
- [ ] MCP server imports successfully
- [ ] Skills reference correct MCP tool names
- [ ] Documentation complete (spec + plan committed)

---

## Testing the Implementation

After implementation, test end-to-end:

1. **Test performance summary:**
   ```python
   from job_search_mcp.service import JobSearchService
   from datetime import date

   service = JobSearchService("/path/to/vault")

   # Write daily summary
   service.write_daily_performance_summary(
       date.today(),
       "## Problems\n- Two Sum - 14 min"
   )

   # Read it back
   content = service.read_daily_performance_summary(date.today())
   assert "Two Sum" in content

   # Read top summary
   top = service.read_top_performance_summary()
   print(top.weak_areas if top else "No top summary")
   ```

2. **Test interview extraction:**
   ```python
   interviews = service.get_upcoming_interviews(days=30)
   print(f"Found {len(interviews)} upcoming interviews")
   for i in interviews:
       print(f"  {i['company']} on {i['date']}")
   ```

3. **Test company resolution:**
   ```python
   result = service.resolve_company_reference("Physical")
   print(f"Resolved to: {result.get('company_name', 'Not found')}")
   print(f"Confidence: {result['confidence']}")
   ```

4. **Test skills in Claude Code:**
   - Run `/precall Physical Intelligence`
   - Run `/leetcode-assess`
   - Run `/plan tomorrow`
   - Verify skills use MCP tools correctly

---

## Success Criteria

Implementation is complete when:

1. ✅ All 6 MCP tools work (tested via service methods)
2. ✅ All 3 new skills load and reference correct MCPs
3. ✅ Updated skills use new MCP tools
4. ✅ All tests pass
5. ✅ Can run skills in Claude Code
6. ✅ End-to-end workflow tested:
   - LeetCode practice → log to daily summary → update aggregated
   - Plan day → reads performance + interviews → generates schedule
   - Precall prep → resolves company → generates prep notes
