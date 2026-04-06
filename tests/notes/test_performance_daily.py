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
