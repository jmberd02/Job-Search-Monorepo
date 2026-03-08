"""Company tracking note parsing and rendering."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import re


@dataclass
class CompanyTracking:
    """Company tracking note record."""

    companies: dict[str, dict] = field(default_factory=dict)


def parse_company_tracking(text: str) -> CompanyTracking:
    """Parse a company tracking note into a CompanyTracking."""
    tracker = CompanyTracking()

    # Find company sections (### Company Name)
    company_pattern = r"### (.+?)\n((?:(?!\n### ).)*)"
    matches = re.findall(company_pattern, text, re.DOTALL)

    for name_match in matches:
        company_name = name_match[0]
        content = name_match[1]

        # Generate company_key from name
        company_key = _slugify(company_name)

        # Parse company properties
        company_data = _parse_company_properties(content)
        company_data["name"] = company_name

        tracker.companies[company_key] = company_data

    return tracker


def render_company_tracking(tracker: CompanyTracking) -> str:
    """Render a CompanyTracking into markdown text."""
    content = "# Company Tracking\n\n"

    # Active Interview Pipeline
    content += "## Active Interview Pipeline\n\n"

    for company_key, company in tracker.companies.items():
        name = company.get("name", company_key)
        content += f"### {name}\n"
        content += f"- **Status:** {company.get('status', 'unknown')}\n"
        content += f"- **Interest:** {company.get('interest', 3)}\n"
        content += f"- **Current state:** {company.get('current_state', '')}\n"
        content += f"- **Next action:** {company.get('next_action', '')}\n"

        if company.get("due"):
            due = company["due"]
            due_str = due.isoformat() if isinstance(due, date) else str(due)
            content += f"- **Due:** {due_str}\n"

        if company.get("applications"):
            content += "- **Applications:**\n"
            for app in company["applications"]:
                content += f"  - {app}\n"

        if company.get("contacts"):
            content += f"- **Contacts:** {company['contacts']}\n"

        if company.get("notes"):
            content += f"- **Notes:** {company['notes']}\n"

        content += "\n"

    # Waiting / In Flight
    content += "## Waiting / In Flight\n\n"

    # Applied / No Response
    content += "## Applied / No Response\n\n"

    # Networking Leads
    content += "## Networking Leads\n\n"

    # Closed Out
    content += "## Closed Out\n\n"

    return content


def upsert_company_tracking_entry(
    tracker: CompanyTracking,
    company_key: str,
    company_name: str,
    status: str,
    interest: int,
    current_state: str,
    next_action: str,
    due_date: Optional[date] = None,
    applications: Optional[list[str]] = None,
    contacts: Optional[str] = None,
    notes: Optional[str] = None,
) -> CompanyTracking:
    """Add or update a company entry in the tracker."""
    if company_key not in tracker.companies:
        tracker.companies[company_key] = {}

    tracker.companies[company_key].update({
        "name": company_name,
        "status": status,
        "interest": interest,
        "current_state": current_state,
        "next_action": next_action,
        "due": due_date,
        "applications": applications or [],
        "contacts": contacts or "",
        "notes": notes or "",
    })

    return tracker


def _slugify(text: str) -> str:
    """Convert text to a slug."""
    return text.lower().replace(" ", "-").replace("_", "-")


def _parse_company_properties(content: str) -> dict:
    """Parse company properties from markdown content."""
    properties = {}

    for line in content.split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()  # Remove leading dash
        # Remove bold markdown
        line = line.replace("**", "")
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        # Handle special fields
        if key == "Due" and value:
            try:
                value = date.fromisoformat(value)
            except ValueError:
                pass
        elif key == "Interest":
            try:
                value = int(value)
            except ValueError:
                pass
        elif key == "Applications":
            # Parse list of applications
            value = [v.strip() for v in value.split(",")]

        properties[key.lower().replace(" ", "_")] = value

    # Extract company note link if present
    if "company_note" in properties:
        note_value = properties["company_note"]
        # Extract first wiki link
        import re
        match = re.search(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", note_value)
        if match:
            link = match.group(1)
            properties["company_note_link"] = link
            properties["company_note_path"] = link + (".md" if not link.endswith(".md") else "")

    return properties
