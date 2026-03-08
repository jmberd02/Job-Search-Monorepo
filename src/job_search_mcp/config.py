"""Configuration for job-search-mcp."""

import os
from pathlib import Path


def get_vault_root() -> Path:
    """Get the Obsidian vault root directory."""
    vault_root = os.environ.get("OBSIDIAN_VAULT_ROOT")
    if vault_root:
        return Path(vault_root)
    # Default to a Job Search folder in the user's home
    return Path.home() / "Job Search"
