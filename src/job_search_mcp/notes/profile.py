"""Candidate profile note parsing and rendering."""

from dataclasses import dataclass
import yaml

from .utils import parse_sections


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
    sections = parse_sections(content)

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
    parts = []
    
    # Frontmatter
    frontmatter = {"tags": ["job-search", "profile"]}
    parts.append("---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n")

    # Content
    parts.append("# Candidate Profile\n\n")

    # Background Summary
    parts.append("## Background Summary\n")
    parts.append(profile.background_summary if profile.background_summary else "")
    parts.append("\n\n")

    # Target Roles
    parts.append("## Target Roles\n")
    if profile.target_roles:
        for role in profile.target_roles:
            parts.append(f"- {role}\n")
    parts.append("\n")

    # Compensation Targets
    parts.append("## Compensation Targets\n")
    parts.append(profile.compensation_targets if profile.compensation_targets else "")
    parts.append("\n\n")

    # Location Constraints
    parts.append("## Location Constraints\n")
    parts.append(profile.location_constraints if profile.location_constraints else "")
    parts.append("\n\n")

    # Search Priorities
    parts.append("## Search Priorities\n")
    parts.append(profile.search_priorities if profile.search_priorities else "")
    parts.append("\n\n")

    # Scheduling Preferences
    parts.append("## Scheduling Preferences\n")
    parts.append(profile.scheduling_preferences if profile.scheduling_preferences else "")
    parts.append("\n\n")

    # Daily Capacity Limits
    parts.append("## Daily Capacity Limits\n")
    parts.append(profile.daily_capacity_limits if profile.daily_capacity_limits else "")
    parts.append("\n\n")

    # Recurring Commitments
    parts.append("## Recurring Commitments\n")
    parts.append(profile.recurring_commitments if profile.recurring_commitments else "")
    parts.append("\n")

    return "".join(parts)
