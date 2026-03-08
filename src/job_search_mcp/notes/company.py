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
from .utils import parse_sections, parse_date_field, escape_table_cell


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
    last_updated = parse_date_field(frontmatter.get("last_updated", ""))

    status = CompanyStatus(status_str)

    # Initialize record
    record = CompanyRecord(
        company=company,
        company_key=company_key,
        status=status,
        interest=interest,
        last_updated=last_updated,
    )

    # Parse content sections
    sections = parse_sections(content)

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
                    record.next_action_due = parse_date_field(value, default=None)
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
    parts = []
    
    # Frontmatter
    frontmatter = {
        "tags": ["job-search", "company"],
        "company": record.company,
        "company_key": record.company_key,
        "status": record.status.value,
        "interest": record.interest,
        "last_updated": record.last_updated.isoformat(),
    }
    parts.append("---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n")

    # Content
    parts.append(f"# {record.company}\n\n")

    # Snapshot
    parts.append("## Snapshot\n")
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
    parts.append("\n".join(snapshot_items) + "\n\n")

    # Notes
    parts.append("## Notes\n")
    parts.append(record.notes if record.notes else "")
    parts.append("\n\n")

    # Contacts
    parts.append("## Contacts\n")
    if record.contacts:
        parts.append("| Name | Role | Source | Last Contact | Notes |\n")
        parts.append("|------|------|--------|--------------|-------|\n")
        for contact in record.contacts:
            last_contact = contact.last_contact.isoformat() if contact.last_contact else ""
            parts.append(f"| {escape_table_cell(contact.name)} | {escape_table_cell(contact.role)} | {escape_table_cell(contact.source)} | {last_contact} | {escape_table_cell(contact.notes)} |\n")
    parts.append("\n")

    # Active Applications
    parts.append("## Active Applications\n\n")

    # Context
    parts.append("## Context\n\n")

    # Timeline
    parts.append("## Timeline\n")
    if record.timeline:
        parts.append("| Date | Type | Summary | Source | Linked Note |\n")
        parts.append("|------|------|---------|--------|-------------|\n")
        for entry in record.timeline:
            parts.append(f"| {entry.date.isoformat()} | {escape_table_cell(entry.entry_type)} | {escape_table_cell(entry.summary)} | {escape_table_cell(entry.source)} | {escape_table_cell(entry.linked_note)} |\n")
    parts.append("\n")

    # Open Questions
    parts.append("## Open Questions\n\n")

    # Related
    parts.append("## Related\n")

    return "".join(parts)


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


def _parse_contacts_table(table_text: str) -> list[Contact]:
    """Parse a contacts markdown table."""
    contacts = []
    lines = table_text.strip().split("\n")

    # Skip header and separator, process data rows
    for i, line in enumerate(lines):
        if i < 2 or not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) >= 5:
            contacts.append(
                Contact(
                    name=parts[0],
                    role=parts[1],
                    source=parts[2],
                    last_contact=parse_date_field(parts[3], default=None) if parts[3] else None,
                    notes=parts[4],
                )
            )
    return contacts


def _parse_timeline_table(table_text: str) -> list[TimelineEntry]:
    """Parse a timeline markdown table."""
    entries = []
    lines = table_text.strip().split("\n")

    # Skip header and separator, process data rows
    for i, line in enumerate(lines):
        if i < 2 or not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) >= 5:
            entries.append(
                TimelineEntry(
                    date=parse_date_field(parts[0]),
                    entry_type=parts[1],
                    summary=parts[2],
                    source=parts[3],
                    linked_note=parts[4],
                )
            )
    return entries
