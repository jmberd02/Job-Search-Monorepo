"""Path utilities for job-search-mcp."""

from pathlib import Path
from .config import get_vault_root


def get_companies_dir() -> Path:
    """Get the Companies directory."""
    return get_vault_root() / "Companies"


def get_applications_dir() -> Path:
    """Get the Applications directory."""
    return get_vault_root() / "Applications"


def get_daily_dir() -> Path:
    """Get the Day directory."""
    return get_vault_root() / "Day"


def get_tracker_path() -> Path:
    """Get the Company Tracking.md path."""
    return get_vault_root() / "Company Tracking.md"


def get_profile_path() -> Path:
    """Get the Candidate Profile.md path."""
    return get_vault_root() / "Candidate Profile.md"


def get_performance_path() -> Path:
    """Get the Performance Summary.md path."""
    return get_vault_root() / "Performance Summary.md"
