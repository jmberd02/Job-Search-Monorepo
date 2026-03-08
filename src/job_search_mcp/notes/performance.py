"""Performance summary note parsing and rendering."""

from dataclasses import dataclass
from datetime import date
import yaml

from .utils import parse_sections, parse_date_field


@dataclass
class PerformanceSummary:
    """Performance summary note record."""

    last_updated: date = None
    overall_assessment: str = ""
    leetcode_progress: str = ""
    interview_prep_status: str = ""
    weak_areas: str = ""
    strengths: str = ""
    recommendations: str = ""


def parse_performance_summary(text: str) -> PerformanceSummary:
    """Parse a performance summary note into a PerformanceSummary."""
    # Split frontmatter and content
    parts = text.split("---", 2)
    if len(parts) < 3:
        return PerformanceSummary()

    frontmatter = yaml.safe_load(parts[1])
    content = parts[2] if len(parts) > 2 else ""

    perf = PerformanceSummary()

    # Parse last_updated from frontmatter
    perf.last_updated = parse_date_field(frontmatter.get("last_updated", ""), default=None)

    # Parse content sections
    sections = parse_sections(content)

    if "overall assessment" in sections:
        perf.overall_assessment = sections["overall assessment"].strip()

    if "leetcode progress" in sections:
        perf.leetcode_progress = sections["leetcode progress"].strip()

    if "interview prep status" in sections:
        perf.interview_prep_status = sections["interview prep status"].strip()

    if "weak areas" in sections:
        perf.weak_areas = sections["weak areas"].strip()

    if "strengths" in sections:
        perf.strengths = sections["strengths"].strip()

    if "recommendations" in sections:
        perf.recommendations = sections["recommendations"].strip()

    return perf


def render_performance_summary(perf: PerformanceSummary) -> str:
    """Render a PerformanceSummary into markdown text."""
    parts = []
    
    # Frontmatter
    frontmatter = {"tags": ["job-search", "performance"]}
    if perf.last_updated:
        frontmatter["last_updated"] = perf.last_updated.isoformat()
    parts.append("---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n")

    # Content
    parts.append("# Performance Summary\n\n")

    # Overall Assessment
    parts.append("## Overall Assessment\n")
    parts.append(perf.overall_assessment if perf.overall_assessment else "")
    parts.append("\n\n")

    # LeetCode Progress
    parts.append("## LeetCode Progress\n")
    parts.append(perf.leetcode_progress if perf.leetcode_progress else "")
    parts.append("\n\n")

    # Interview Prep Status
    parts.append("## Interview Prep Status\n")
    parts.append(perf.interview_prep_status if perf.interview_prep_status else "")
    parts.append("\n\n")

    # Weak Areas
    parts.append("## Weak Areas\n")
    parts.append(perf.weak_areas if perf.weak_areas else "")
    parts.append("\n\n")

    # Strengths
    parts.append("## Strengths\n")
    parts.append(perf.strengths if perf.strengths else "")
    parts.append("\n\n")

    # Recommendations
    parts.append("## Recommendations\n")
    parts.append(perf.recommendations if perf.recommendations else "")
    parts.append("\n")

    return "".join(parts)
