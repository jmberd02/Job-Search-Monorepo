"""Candidate profile note parsing and rendering."""

from dataclasses import dataclass
import yaml


@dataclass
class CandidateProfile:
    """Candidate profile note record."""

    background_summary: str = ""
    target_roles: list[str] = None
    compensation_targets: str = ""
    location_constraints: str = ""
    search_priorities: str = ""
    scheduling_preferences: str = ""
    daily_capacity_limits: str = ""
    recurring_commitments: str = ""

    def __post_init__(self):
        if self.target_roles is None:
            self.target_roles = []


def parse_candidate_profile(text: str) -> CandidateProfile:
    """Parse a candidate profile note into a CandidateProfile."""
    # Split frontmatter and content
    parts = text.split("---", 2)
    if len(parts) < 3:
        return CandidateProfile()

    frontmatter = yaml.safe_load(parts[1])
    content = parts[2] if len(parts) > 2 else ""

    profile = CandidateProfile()

    # Parse content sections
    sections = _parse_sections(content)

    if "background summary" in sections:
        profile.background_summary = sections["background summary"].strip()

    if "target roles" in sections:
        lines = sections["target roles"].strip().split("\n")
        profile.target_roles = [line.lstrip("- ").strip() for line in lines if line.strip()]

    if "compensation targets" in sections:
        profile.compensation_targets = sections["compensation targets"].strip()

    if "location constraints" in sections:
        profile.location_constraints = sections["location constraints"].strip()

    if "search priorities" in sections:
        profile.search_priorities = sections["search priorities"].strip()

    if "scheduling preferences" in sections:
        profile.scheduling_preferences = sections["scheduling preferences"].strip()

    if "daily capacity limits" in sections:
        profile.daily_capacity_limits = sections["daily capacity limits"].strip()

    if "recurring commitments" in sections:
        profile.recurring_commitments = sections["recurring commitments"].strip()

    return profile


def render_candidate_profile(profile: CandidateProfile) -> str:
    """Render a CandidateProfile into markdown text."""
    # Frontmatter
    frontmatter = {
        "tags": ["job-search", "profile"],
    }

    frontmatter_str = "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n"

    # Content
    content = "# Candidate Profile\n\n"

    # Background Summary
    content += "## Background Summary\n"
    content += profile.background_summary if profile.background_summary else ""
    content += "\n\n"

    # Target Roles
    content += "## Target Roles\n"
    if profile.target_roles:
        for role in profile.target_roles:
            content += f"- {role}\n"
    content += "\n"

    # Compensation Targets
    content += "## Compensation Targets\n"
    content += profile.compensation_targets if profile.compensation_targets else ""
    content += "\n\n"

    # Location Constraints
    content += "## Location Constraints\n"
    content += profile.location_constraints if profile.location_constraints else ""
    content += "\n\n"

    # Search Priorities
    content += "## Search Priorities\n"
    content += profile.search_priorities if profile.search_priorities else ""
    content += "\n\n"

    # Scheduling Preferences
    content += "## Scheduling Preferences\n"
    content += profile.scheduling_preferences if profile.scheduling_preferences else ""
    content += "\n\n"

    # Daily Capacity Limits
    content += "## Daily Capacity Limits\n"
    content += profile.daily_capacity_limits if profile.daily_capacity_limits else ""
    content += "\n\n"

    # Recurring Commitments
    content += "## Recurring Commitments\n"
    content += profile.recurring_commitments if profile.recurring_commitments else ""
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
