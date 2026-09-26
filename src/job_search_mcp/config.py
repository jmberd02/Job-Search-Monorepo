"""Configuration management for job-search-mcp."""

from pathlib import Path
import json
from typing import Any


class ConfigError(Exception):
    """Configuration-related errors."""
    pass


def get_default_config_path() -> Path:
    """Get default config file location."""
    return Path.home() / ".job-search" / "config.json"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """
    Load configuration from file.

    Args:
        config_path: Path to config file (defaults to ~/.job-search/config.json)

    Returns:
        Configuration dictionary

    Raises:
        ConfigError: If config file not found
    """
    if config_path is None:
        config_path = get_default_config_path()

    if not config_path.exists():
        raise ConfigError(
            f"Configuration not found at {config_path}. "
            "Run /setup-job-search in Claude Code to create it."
        )

    try:
        return json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}")


def get_vault_path(config_path: Path | None = None) -> Path:
    """
    Get vault path from config.

    Args:
        config_path: Path to config file

    Returns:
        Path to Obsidian vault
    """
    config = load_config(config_path)
    vault_path = config.get("vault_path")

    if not vault_path:
        raise ConfigError("vault_path not set in config")

    return Path(vault_path)


def save_config(config_path: Path | None, data: dict[str, Any]) -> None:
    """
    Save configuration to file.

    Args:
        config_path: Path to config file
        data: Configuration data to save
    """
    if config_path is None:
        config_path = get_default_config_path()

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write config
    config_path.write_text(json.dumps(data, indent=2))
