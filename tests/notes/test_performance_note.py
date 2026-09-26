"""Tests for performance summary note parsing and rendering."""
import pytest
from datetime import date


class TestParsePerformanceSummary:
    """Tests for parsing performance summary notes."""

    def test_parse_minimal_performance(self):
        """Should parse a minimal performance summary."""
        from job_search_mcp.notes.performance import parse_performance_summary

        text = """---
tags:
  - job-search
  - performance
last_updated: 2026-03-07
---

# Performance Summary

## Overall Assessment

## LeetCode Progress

## Interview Prep Status

## Weak Areas

## Strengths

## Recommendations
"""
        perf = parse_performance_summary(text)
        assert perf is not None

    def test_parse_performance_with_content(self):
        """Should parse a performance summary with content."""
        from job_search_mcp.notes.performance import parse_performance_summary

        text = """---
tags:
  - job-search
  - performance
last_updated: 2026-03-07
---

# Performance Summary

## Overall Assessment
Strong fundamentals, need to improve system design.

## LeetCode Progress
- 150 problems solved
- 80% acceptance rate
- Focus: Dynamic programming

## Interview Prep Status
- Completed 3 mock interviews
- Need more practice with graphs

## Weak Areas
- Dynamic programming
- System design
- Concurrency

## Strengths
- Arrays and strings
- Binary trees
- Problem decomposition

## Recommendations
1. Focus on DP patterns
2. Practice system design
3. Review concurrency patterns
"""
        perf = parse_performance_summary(text)
        assert "Strong fundamentals" in perf.overall_assessment
        assert "150 problems solved" in perf.leetcode_progress
        assert "Dynamic programming" in perf.weak_areas
        assert "Arrays and strings" in perf.strengths


class TestRenderPerformanceSummary:
    """Tests for rendering performance summary notes."""

    def test_render_minimal_performance(self):
        """Should render a minimal performance summary."""
        from job_search_mcp.notes.performance import render_performance_summary, PerformanceSummary

        perf = PerformanceSummary()
        text = render_performance_summary(perf)
        assert "# Performance Summary" in text
        assert "## Overall Assessment" in text
        assert "## LeetCode Progress" in text

    def test_render_performance_with_content(self):
        """Should render a performance summary with content."""
        from job_search_mcp.notes.performance import render_performance_summary, PerformanceSummary

        perf = PerformanceSummary(
            overall_assessment="Strong fundamentals",
            leetcode_progress="150 problems solved",
            interview_prep_status="3 mock interviews completed",
            weak_areas="Dynamic programming",
            strengths="Arrays and strings",
            recommendations="Focus on DP patterns",
        )
        text = render_performance_summary(perf)
        assert "Strong fundamentals" in text
        assert "150 problems solved" in text
        assert "Dynamic programming" in text
