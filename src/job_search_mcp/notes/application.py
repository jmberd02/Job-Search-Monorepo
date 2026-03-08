"""Application note parsing and rendering."""

from datetime import date
from typing import Optional
import yaml

from job_search_mcp.models import (
    ApplicationRecord,
    ApplicationStatus,
    InterviewEvent,
    Task,
    TaskState,
)
from .utils import parse_sections, parse_date_field, escape_table_cell


def parse_application_note(text: str) -> ApplicationRecord:
    """Parse an application note into an ApplicationRecord."""
    # Split frontmatter and content
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid application note format: missing frontmatter")

    frontmatter = yaml.safe_load(parts[1])
    content = parts[2] if len(parts) > 2 else ""

    # Extract frontmatter fields
    company = frontmatter.get("company", "")
    company_key = frontmatter.get("company_key", "")
    role = frontmatter.get("role", "")
    application_key = frontmatter.get("application_key", "")
    status_str = frontmatter.get("status", "drafted")
    created = parse_date_field(frontmatter.get("created", ""))
    last_updated = parse_date_field(frontmatter.get("last_updated", ""))

    status = ApplicationStatus(status_str)

    # Initialize record
    record = ApplicationRecord(
        company=company,
        company_key=company_key,
        role=role,
        application_key=application_key,
        status=status,
        created=created,
        last_updated=last_updated,
    )

    # Parse content sections
    sections = parse_sections(content)

    # Parse Snapshot
    if "snapshot" in sections:
        snapshot_lines = sections["snapshot"].strip().split("\n")
        for line in snapshot_lines:
            line = line.strip().lstrip("- ")
            line = line.replace("**", "").strip()
            if ":" in line:
                key, value = line.split(":", 1)
                value = value.strip()
                if "Applied on" in key:
                    record.applied_on = parse_date_field(value, default=None)
                elif "Current stage" in key:
                    record.current_stage = value
                elif "Next action" in key:
                    record.next_action = value
                elif "Due" in key:
                    record.due_date = parse_date_field(value, default=None)
                elif "Priority / Interest" in key:
                    try:
                        record.priority_interest = int(value)
                    except ValueError:
                        pass
                elif "Comp" in key:
                    record.comp = value
                elif "Location" in key:
                    record.location = value

    # Parse Materials
    if "materials" in sections:
        materials_text = sections["materials"].strip()
        for line in materials_text.split("\n"):
            line = line.strip().lstrip("- ")
            if ":" in line:
                key, value = line.split(":", 1)
                record.materials[key.strip()] = value.strip()

    # Parse Interview Process
    if "interview process" in sections:
        record.interview_process = _parse_interview_table(sections["interview process"])

    # Parse Tasks
    if "tasks" in sections:
        record.tasks = _parse_tasks_list(sections["tasks"])

    return record


def render_application_note(record: ApplicationRecord) -> str:
    """Render an ApplicationRecord into markdown text."""
    parts = []
    
    # Frontmatter
    frontmatter = {
        "tags": ["job-search", "application"],
        "company": record.company,
        "company_key": record.company_key,
        "role": record.role,
        "application_key": record.application_key,
        "status": record.status.value,
        "created": record.created.isoformat(),
        "last_updated": record.last_updated.isoformat(),
    }
    parts.append("---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n")

    # Content
    parts.append(f"# {record.company} - {record.role}\n\n")

    # Snapshot
    parts.append("## Snapshot\n")
    snapshot_items = [
        f"- **Company:** [[Companies/{record.company}]]",
        f"- **Role:** {record.role}",
        f"- **Status:** {record.status.value}",
    ]
    if record.applied_on:
        snapshot_items.append(f"- **Applied on:** {record.applied_on.isoformat()}")
    if record.current_stage:
        snapshot_items.append(f"- **Current stage:** {record.current_stage}")
    if record.next_action:
        snapshot_items.append(f"- **Next action:** {record.next_action}")
    if record.due_date:
        snapshot_items.append(f"- **Due:** {record.due_date.isoformat()}")
    if record.priority_interest:
        snapshot_items.append(f"- **Priority / Interest:** {record.priority_interest}")
    if record.comp:
        snapshot_items.append(f"- **Comp:** {record.comp}")
    if record.location:
        snapshot_items.append(f"- **Location:** {record.location}")
    parts.append("\n".join(snapshot_items) + "\n\n")

    # Materials
    parts.append("## Materials\n")
    if record.materials:
        for key, value in record.materials.items():
            parts.append(f"- {key}: {value}\n")
    parts.append("\n")

    # Interview Process
    parts.append("## Interview Process\n")
    if record.interview_process:
        parts.append("| Date | Stage | People | Outcome | Notes |\n")
        parts.append("|------|-------|--------|---------|-------|\n")
        for event in record.interview_process:
            parts.append(f"| {event.date.isoformat()} | {escape_table_cell(event.stage)} | {escape_table_cell(event.people)} | {escape_table_cell(event.outcome)} | {escape_table_cell(event.notes)} |\n")
    parts.append("\n")

    # Role-Specific Notes
    parts.append("## Role-Specific Notes\n\n")

    # Tasks
    parts.append("## Tasks\n")
    for task in record.tasks:
        checkbox = "[ ]" if task.state == TaskState.PENDING else "[x]"
        due = f" (due: {task.due_date.isoformat()})" if task.due_date else ""
        parts.append(f"- {checkbox} {task.description}{due}\n")
    parts.append("\n")

    # Outcome
    parts.append("## Outcome\n")

    return "".join(parts)


def upsert_application_interview_event(
    record: ApplicationRecord, event: InterviewEvent
) -> ApplicationRecord:
    """Add or update an interview event in the application."""
    # Check if event already exists (by date and stage)
    for i, existing in enumerate(record.interview_process):
        if existing.date == event.date and existing.stage == event.stage:
            # Update existing
            record.interview_process[i] = event
            record.last_updated = date.today()
            return record

    # Add new event
    record.interview_process.append(event)
    record.interview_process.sort(key=lambda e: e.date)
    record.last_updated = date.today()
    return record


def _parse_interview_table(table_text: str) -> list[InterviewEvent]:
    """Parse an interview process markdown table."""
    events = []
    lines = table_text.strip().split("\n")

    # Skip header and separator, process data rows
    for i, line in enumerate(lines):
        if i < 2 or not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) >= 5:
            events.append(
                InterviewEvent(
                    date=parse_date_field(parts[0]),
                    stage=parts[1],
                    people=parts[2],
                    outcome=parts[3],
                    notes=parts[4],
                )
            )
    return events


def _parse_tasks_list(tasks_text: str) -> list[Task]:
    """Parse a tasks markdown list."""
    tasks = []
    for line in tasks_text.split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()
        if line.startswith("[ ]"):
            state = TaskState.PENDING
            desc = line[3:].strip()
        elif line.startswith("[x]"):
            state = TaskState.DONE
            desc = line[3:].strip()
        else:
            state = TaskState.PENDING
            desc = line

        # Check for due date
        due_date = None
        if "(due:" in desc:
            match = desc.rsplit("(due:", 1)
            if len(match) == 2:
                due_str = match[1].rstrip(")").strip()
                due_date = parse_date_field(due_str, default=None)
                desc = match[0].strip()

        tasks.append(Task(description=desc, state=state, due_date=due_date))
    return tasks
