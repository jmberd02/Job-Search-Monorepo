"""Performance summary note parsing and rendering."""

from dataclasses import dataclass
from datetime import date
import yaml


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
    last_updated_str = frontmatter.get("last_updated", "")
    if last_updated_str:
        if isinstance(last_updated_str, date):
            perf.last_updated = last_updated_str
        else:
            try:
                perf.last_updated = date.fromisoformat(last_updated_str)
            except (ValueError, TypeError):
                pass

    # Parse content sections
    sections = _parse_sections(content)

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
    # Frontmatter
    frontmatter = {
        "tags": ["job-search", "performance"],
    }
    if perf.last_updated:
        frontmatter["last_updated"] = perf.last_updated.isoformat()

    frontmatter_str = "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n"

    # Content
    content = "# Performance Summary\n\n"

    # Overall Assessment
    content += "## Overall Assessment\n"
    content += perf.overall_assessment if perf.overall_assessment else ""
    content += "\n\n"

    # LeetCode Progress
    content += "## LeetCode Progress\n"
    content += perf.leetcode_progress if perf.leetcode_progress else ""
    content += "\n\n"

    # Interview Prep Status
    content += "## Interview Prep Status\n"
    content += perf.interview_prep_status if perf.interview_prep_status else ""
    content += "\n\n"

    # Weak Areas
    content += "## Weak Areas\n"
    content += perf.weak_areas if perf.weak_areas else ""
    content += "\n\n"

    # Strengths
    content += "## Strengths\n"
    content += perf.strengths if perf.strengths else ""
    content += "\n\n"

    # Recommendations
    content += "## Recommendations\n"
    content += perf.recommendations if perf.recommendations else ""
    content += "\n"

    return frontmatter_str + content


def _parse_sections(content: str) -> dict[str, str]:
    """Parse markdown content into sections."""
    sections = {}
    current_section = ""
    current_content = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section.lower()] = "\n".join(current_content)
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section.lower()] = "\n".join(current_content)

    return sections
