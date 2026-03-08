"""Path utilities for job-search-mcp."""

from pathlib import Path
from .config import get_vault_root as _get_vault_root

# Default vault root (used when no custom root is provided)
_default_vault_root: Path | None = None


def set_vault_root(path: Path | str):
    """Set the default vault root for path operations."""
    global _default_vault_root
    _default_vault_root = Path(path)


def get_vault_root() -> Path:
    """Get the Obsidian vault root directory."""
    if _default_vault_root is not None:
        return _default_vault_root
    return _get_vault_root()


def get_companies_dir(vault_root: Path | None = None) -> Path:
    """Get the Companies directory."""
    root = vault_root or get_vault_root()
    return root / "Companies"


def get_applications_dir(vault_root: Path | None = None) -> Path:
    """Get the Applications directory."""
    root = vault_root or get_vault_root()
    return root / "Applications"


def get_daily_dir(vault_root: Path | None = None) -> Path:
    """Get the Day directory."""
    root = vault_root or get_vault_root()
    return root / "Day"


def get_tracker_path(vault_root: Path | None = None) -> Path:
    """Get the Company Tracking.md path."""
    root = vault_root or get_vault_root()
    return root / "Company Tracking.md"


def get_profile_path(vault_root: Path | None = None) -> Path:
    """Get the Candidate Profile.md path."""
    root = vault_root or get_vault_root()
    return root / "Candidate Profile.md"


def get_performance_path(vault_root: Path | None = None) -> Path:
    """Get the Performance Summary.md path."""
    root = vault_root or get_vault_root()
    return root / "Performance Summary.md"
