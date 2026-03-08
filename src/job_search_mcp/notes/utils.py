"""Shared utilities for note parsing."""

from datetime import date
from typing import Optional


def parse_sections(content: str) -> dict[str, str]:
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


def parse_date_field(value, default: Optional[date] = None) -> date:
    """Parse a date field from frontmatter or content."""
    if isinstance(value, date):
        return value
    if value:
        try:
            return date.fromisoformat(str(value))
        except (ValueError, AttributeError):
            pass
    return default or date.today()


def escape_table_cell(text: str) -> str:
    """Escape pipe characters in table cell content."""
    return str(text).replace("|", "\\|")
