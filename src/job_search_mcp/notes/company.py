"""Company note parsing and rendering."""

import re
from datetime import date
from typing import Optional
import yaml

from job_search_mcp.models import (
    CompanyRecord,
    CompanyStatus,
    TimelineEntry,
    Contact,
    CompanySignal,
)


def parse_company_note(text: str) -> CompanyRecord:
    """Parse a company note into a CompanyRecord."""
    # Split frontmatter and content
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid company note format: missing frontmatter")

    frontmatter = yaml.safe_load(parts[1])
    content = parts[2] if len(parts) > 2 else ""

    # Extract frontmatter fields
    company = frontmatter.get("company", "")
    company_key = frontmatter.get("company_key", "")
    status_str = frontmatter.get("status", "active")
    interest = frontmatter.get("interest", 3)
    last_updated_str = frontmatter.get("last_updated", "")

    status = CompanyStatus(status_str)
    if isinstance(last_updated_str, date):
        last_updated = last_updated_str
    elif last_updated_str:
        last_updated = date.fromisoformat(last_updated_str)
    else:
        last_updated = date.today()

    # Initialize record
    record = CompanyRecord(
        company=company,
        company_key=company_key,
        status=status,
        interest=interest,
        last_updated=last_updated,
    )

    # Parse content sections
    sections = _parse_sections(content)

    # Parse Snapshot
    if "snapshot" in sections:
        snapshot_lines = sections["snapshot"].strip().split("\n")
        for line in snapshot_lines:
            line = line.strip().lstrip("- ")
            # Remove markdown bold markers
            line = line.replace("**", "").strip()
            if ":" in line:
                key, value = line.split(":", 1)
                value = value.strip()
                if "Primary next action" in key:
                    record.primary_next_action = value
                elif "Next action due" in key:
                    try:
                        record.next_action_due = date.fromisoformat(value)
                    except ValueError:
                        pass
                elif "Best current role" in key:
                    record.best_current_role = value
                elif "Location" in key:
                    record.location = value
                elif "Commute fit" in key:
                    record.commute_fit = value
                elif "Comp / range" in key:
                    record.comp_range = value

    # Parse Notes
    if "notes" in sections:
        record.notes = sections["notes"].strip()

    # Parse Contacts table
    if "contacts" in sections:
        record.contacts = _parse_contacts_table(sections["contacts"])

    # Parse Timeline
    if "timeline" in sections:
        record.timeline = _parse_timeline_table(sections["timeline"])

    return record


def render_company_note(record: CompanyRecord) -> str:
    """Render a CompanyRecord into markdown text."""
    # Frontmatter
    frontmatter = {
        "tags": ["job-search", "company"],
        "company": record.company,
        "company_key": record.company_key,
        "status": record.status.value,
        "interest": record.interest,
        "last_updated": record.last_updated.isoformat(),
    }

    frontmatter_str = "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n"

    # Content
    content = f"# {record.company}\n\n"

    # Snapshot
    content += "## Snapshot\n"
    snapshot_items = [
        f"- **Status:** {record.status.value}",
        f"- **Interest:** {record.interest}",
    ]
    if record.primary_next_action:
        snapshot_items.append(f"- **Primary next action:** {record.primary_next_action}")
    if record.next_action_due:
        snapshot_items.append(f"- **Next action due:** {record.next_action_due.isoformat()}")
    if record.best_current_role:
        snapshot_items.append(f"- **Best current role:** {record.best_current_role}")
    if record.location:
        snapshot_items.append(f"- **Location:** {record.location}")
    if record.commute_fit:
        snapshot_items.append(f"- **Commute fit:** {record.commute_fit}")
    if record.comp_range:
        snapshot_items.append(f"- **Comp / range:** {record.comp_range}")

    content += "\n".join(snapshot_items) + "\n\n"

    # Notes
    content += "## Notes\n"
    content += record.notes if record.notes else ""
    content += "\n\n"

    # Contacts
    content += "## Contacts\n"
    if record.contacts:
        content += "| Name | Role | Source | Last Contact | Notes |\n"
        content += "|------|------|--------|--------------|-------|\n"
        for contact in record.contacts:
            last_contact = contact.last_contact.isoformat() if contact.last_contact else ""
            content += f"| {contact.name} | {contact.role} | {contact.source} | {last_contact} | {contact.notes} |\n"
    content += "\n"

    # Active Applications
    content += "## Active Applications\n\n"

    # Context
    content += "## Context\n\n"

    # Timeline
    content += "## Timeline\n"
    if record.timeline:
        content += "| Date | Type | Summary | Source | Linked Note |\n"
        content += "|------|------|---------|--------|-------------|\n"
        for entry in record.timeline:
            content += f"| {entry.date.isoformat()} | {entry.entry_type} | {entry.summary} | {entry.source} | {entry.linked_note} |\n"
    content += "\n"

    # Open Questions
    content += "## Open Questions\n\n"

    # Related
    content += "## Related\n"

    return frontmatter_str + content


def append_company_timeline(record: CompanyRecord, signal: CompanySignal) -> CompanyRecord:
    """Append a signal to the company timeline, avoiding duplicates."""
    # Check for duplicate source marker
    if signal.source_marker:
        for entry in record.timeline:
            if entry.source == signal.source_marker:
                # Update existing entry instead of appending
                entry.summary = signal.summary
                entry.entry_type = signal.signal_type.value
                return record

    # Create new timeline entry
    entry_date = signal.due_date or date.today()
    entry = TimelineEntry(
        date=entry_date,
        entry_type=signal.signal_type.value,
        summary=signal.summary,
        source=signal.source_marker or "",
    )
    record.timeline.append(entry)
    record.last_updated = date.today()
    return record


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


def _parse_contacts_table(table_text: str) -> list[Contact]:
    """Parse a contacts markdown table."""
    contacts = []
    lines = table_text.strip().split("\n")

    # Skip header and separator
    for line in lines[2:]:
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 5:
            last_contact = None
            if parts[3]:
                try:
                    last_contact = date.fromisoformat(parts[3])
                except ValueError:
                    pass
            contacts.append(
                Contact(
                    name=parts[0],
                    role=parts[1],
                    source=parts[2],
                    last_contact=last_contact,
                    notes=parts[4],
                )
            )
    return contacts


def _parse_timeline_table(table_text: str) -> list[TimelineEntry]:
    """Parse a timeline markdown table."""
    entries = []
    lines = [l for l in table_text.strip().split("\n") if l.strip().startswith("|")]

    # Skip header and separator
    for line in lines[2:]:
        if not line.strip():
            continue
        # Remove leading and trailing pipes, then split
        line = line.strip().strip("|")
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5:
            entry_date = None
            if parts[0]:
                try:
                    entry_date = date.fromisoformat(parts[0])
                except ValueError:
                    pass
            entries.append(
                TimelineEntry(
                    date=entry_date or date.today(),
                    entry_type=parts[1],
                    summary=parts[2],
                    source=parts[3],
                    linked_note=parts[4],
                )
            )
    return entries
