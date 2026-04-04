"""Path utilities for job-search-mcp."""

from pathlib import Path
import os
from .config import get_vault_path, ConfigError

# Default vault root (used when no custom root is provided)
_default_vault_root: Path | None = None


def set_vault_root(path: Path | str):
    """Set the default vault root for path operations."""
    global _default_vault_root
    _default_vault_root = Path(path)


def get_vault_root(config_path: Path | None = None) -> Path:
    """
    Get the Obsidian vault root directory.

    Args:
        config_path: Optional path to config file

    Returns:
        Path to vault root

    Priority:
        1. Programmatically set vault root (_default_vault_root)
        2. Config file (if exists)
        3. OBSIDIAN_VAULT_ROOT env variable (backward compatibility)

    Raises:
        ConfigError: If no vault path configured
    """
    # Check programmatically set root first
    if _default_vault_root is not None:
        return _default_vault_root

    # Try config file
    try:
        return get_vault_path(config_path)
    except ConfigError:
        pass

    # Fall back to env variable for backward compatibility
    vault_root = os.getenv("OBSIDIAN_VAULT_ROOT")
    if vault_root:
        return Path(vault_root)

    raise ConfigError(
        "No vault path configured. Either:\n"
        "1. Run /setup-job-search in Claude Code, or\n"
        "2. Set OBSIDIAN_VAULT_ROOT environment variable"
    )


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
