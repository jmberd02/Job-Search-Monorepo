"""Tests for candidate profile note parsing and rendering."""
import pytest
from datetime import date


class TestParseCandidateProfile:
    """Tests for parsing candidate profile notes."""

    def test_parse_minimal_profile(self):
        """Should parse a minimal candidate profile."""
        from job_search_mcp.notes.profile import parse_candidate_profile

        text = """---
tags:
  - job-search
  - profile
---

# Candidate Profile

## Background Summary

## Target Roles

## Compensation Targets

## Location Constraints

## Search Priorities

## Scheduling Preferences

## Daily Capacity Limits

## Recurring Commitments
"""
        profile = parse_candidate_profile(text)
        assert profile is not None

    def test_parse_profile_with_content(self):
        """Should parse a candidate profile with content."""
        from job_search_mcp.notes.profile import parse_candidate_profile

        text = """---
tags:
  - job-search
  - profile
---

# Candidate Profile

## Background Summary
Experienced software engineer with 8 years in distributed systems.

## Target Roles
- Senior Software Engineer
- Staff Engineer
- Engineering Manager

## Compensation Targets
$200-250k base, equity negotiable

## Location Constraints
Remote-first, Bay Area preferred for hybrid

## Search Priorities
1. Mission-driven companies
2. Technical depth
3. Work-life balance

## Scheduling Preferences
- Mornings best for interviews
- Block 2-4pm for deep work

## Daily Capacity Limits
- 6 hours of focused work
- 2 hours for meetings

## Recurring Commitments
- Weekly team sync (Tue 10am)
- Monthly board meeting (last Fri)
"""
        profile = parse_candidate_profile(text)
        assert profile.background_summary == "Experienced software engineer with 8 years in distributed systems."
        assert "Senior Software Engineer" in profile.target_roles
        assert "$200-250k" in profile.compensation_targets
        assert "Remote-first" in profile.location_constraints


class TestRenderCandidateProfile:
    """Tests for rendering candidate profile notes."""

    def test_render_minimal_profile(self):
        """Should render a minimal candidate profile."""
        from job_search_mcp.notes.profile import render_candidate_profile, CandidateProfile

        profile = CandidateProfile()
        text = render_candidate_profile(profile)
        assert "# Candidate Profile" in text
        assert "## Background Summary" in text
        assert "## Target Roles" in text

    def test_render_profile_with_content(self):
        """Should render a candidate profile with content."""
        from job_search_mcp.notes.profile import render_candidate_profile, CandidateProfile

        profile = CandidateProfile(
            background_summary="Experienced software engineer",
            target_roles=["Senior Engineer", "Staff Engineer"],
            compensation_targets="$200-250k",
            location_constraints="Remote-first",
            search_priorities="Mission-driven companies",
            scheduling_preferences="Mornings best",
            daily_capacity_limits="6 hours focused work",
            recurring_commitments="Weekly sync",
        )
        text = render_candidate_profile(profile)
        assert "Experienced software engineer" in text
        assert "Senior Engineer" in text
        assert "$200-250k" in text
        assert "Remote-first" in text
