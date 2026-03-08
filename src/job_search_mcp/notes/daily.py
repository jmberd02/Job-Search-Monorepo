"""Daily note parsing and rendering."""

from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional
import yaml


@dataclass
class ScheduleBlock:
    """Schedule block for daily notes."""

    start_time: time
    end_time: time
    description: str


@dataclass
class ActivityBlock:
    """Activity block for daily notes."""

    start_time: time
    end_time: time
    description: str
    status: str
    note: str = ""


@dataclass
class DailyNote:
    """Daily note record."""

    date: date
    schedule: list[ScheduleBlock] = field(default_factory=list)
    activity: list[ActivityBlock] = field(default_factory=list)
    schedule_vs_activity: str = ""


def parse_daily_note(text: str) -> DailyNote:
    """Parse a daily note into a DailyNote."""
    # Split frontmatter and content
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid daily note format: missing frontmatter")

    frontmatter = yaml.safe_load(parts[1])
    content = parts[2] if len(parts) > 2 else ""

    # Extract date from frontmatter
    date_str = frontmatter.get("date", "")
    if isinstance(date_str, date):
        note_date = date_str
    elif date_str:
        note_date = date.fromisoformat(date_str)
    else:
        note_date = date.today()

    daily = DailyNote(date=note_date)

    # Parse content sections
    sections = _parse_sections(content)

    # Parse Schedule
    if "schedule" in sections:
        daily.schedule = _parse_schedule_blocks(sections["schedule"])

    # Parse Daily Activity
    if "daily activity" in sections:
        daily.activity = _parse_activity_blocks(sections["daily activity"])

    # Parse Schedule vs Activity
    if "schedule vs activity" in sections:
        daily.schedule_vs_activity = sections["schedule vs activity"].strip()

    return daily


def render_daily_note(daily: DailyNote) -> str:
    """Render a DailyNote into markdown text."""
    # Frontmatter
    frontmatter = {
        "tags": ["job-search", "daily"],
        "date": daily.date.isoformat(),
    }

    frontmatter_str = "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n"

    # Content
    content = f"# {daily.date.isoformat()}\n\n"

    # Schedule
    content += "## Schedule\n"
    for block in daily.schedule:
        start_str = _format_time(block.start_time)
        end_str = _format_time(block.end_time)
        content += f"- {start_str} - {end_str}: {block.description}\n"
    content += "\n"

    # Daily Activity
    content += "## Daily Activity\n"
    for block in daily.activity:
        start_str = _format_time(block.start_time)
        end_str = _format_time(block.end_time)
        content += f"- {start_str} - {end_str}: {block.description} - {block.status}"
        if block.note:
            content += f" - {block.note}"
        content += "\n"
    content += "\n"

    # Schedule vs Activity
    content += "## Schedule vs Activity\n"
    content += daily.schedule_vs_activity if daily.schedule_vs_activity else ""
    content += "\n"

    return frontmatter_str + content


def append_daily_activity(
    daily: DailyNote,
    start_time: time,
    end_time: time,
    description: str,
    status: str,
    note: str = "",
) -> DailyNote:
    """Append an activity block to the daily note."""
    block = ActivityBlock(
        start_time=start_time,
        end_time=end_time,
        description=description,
        status=status,
        note=note,
    )
    daily.activity.append(block)
    return daily


def refresh_schedule_vs_activity(daily: DailyNote) -> DailyNote:
    """Generate or update the schedule vs activity comparison."""
    if not daily.schedule or not daily.activity:
        daily.schedule_vs_activity = ""
        return daily

    lines = ["### Schedule vs Activity\n"]
    lines.append("| Scheduled | Actual | Status | Notes |")
    lines.append("|-----------|--------|--------|-------|")

    # Match schedule blocks to activity blocks
    for sched in daily.schedule:
        sched_desc = sched.description.lower()
        matched = None
        for act in daily.activity:
            if act.description.lower() == sched_desc:
                matched = act
                break

        if matched:
            status = matched.status
            note = matched.note or ""
        else:
            status = "Not done"
            note = ""

        lines.append(f"| {sched.description} | {matched.description if matched else '-'} | {status} | {note} |")

    daily.schedule_vs_activity = "\n".join(lines)
    return daily


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


def _parse_schedule_blocks(schedule_text: str) -> list[ScheduleBlock]:
    """Parse schedule blocks from markdown."""
    blocks = []
    for line in schedule_text.split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()

        # Parse time range: "9:00 AM - 11:00 AM: Description"
        if ":" not in line:
            continue

        # Find the last colon that separates time from description
        colon_idx = line.rfind(":")
        if colon_idx == -1:
            continue

        time_part = line[:colon_idx].strip()
        description = line[colon_idx + 1:].strip()

        # Parse time range
        if "-" not in time_part:
            continue

        time_parts = time_part.split("-")
        if len(time_parts) != 2:
            continue

        start_str = time_parts[0].strip()
        end_str = time_parts[1].strip()

        start_time = _parse_time(start_str)
        end_time = _parse_time(end_str)

        if start_time and end_time:
            blocks.append(ScheduleBlock(start_time=start_time, end_time=end_time, description=description))

    return blocks


def _parse_activity_blocks(activity_text: str) -> list[ActivityBlock]:
    """Parse activity blocks from markdown."""
    blocks = []
    for line in activity_text.split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()

        # Parse: "9:00 AM - 11:00 AM: Description - Status - Note"
        if ":" not in line:
            continue

        colon_idx = line.rfind(":")
        if colon_idx == -1:
            continue

        time_part = line[:colon_idx].strip()
        rest = line[colon_idx + 1:].strip()

        # Parse time range
        if "-" not in time_part:
            continue

        time_parts = time_part.split("-")
        if len(time_parts) != 2:
            continue

        start_str = time_parts[0].strip()
        end_str = time_parts[1].strip()

        start_time = _parse_time(start_str)
        end_time = _parse_time(end_str)

        if not start_time or not end_time:
            continue

        # Parse description, status, and note
        parts = rest.split(" - ")
        description = parts[0] if parts else ""
        status = parts[1] if len(parts) > 1 else ""
        note = parts[2] if len(parts) > 2 else ""

        blocks.append(ActivityBlock(start_time=start_time, end_time=end_time, description=description, status=status, note=note))

    return blocks


def _parse_time(time_str: str) -> Optional[time]:
    """Parse a time string like '9:00 AM' or '14:30'."""
    time_str = time_str.strip()

    # Try various formats
    formats = [
        "%I:%M %p",  # 9:00 AM
        "%H:%M",     # 14:30
        "%I %p",     # 9 AM
        "%H",        # 14
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue

    return None


def _format_time(t: time) -> str:
    """Format a time for display."""
    return t.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
