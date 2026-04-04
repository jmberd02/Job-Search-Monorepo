# tests/test_config.py
import pytest
from pathlib import Path
import json
import tempfile
import os
from job_search_mcp.config import load_config, get_vault_path, save_config, ConfigError


def test_load_config_missing_file():
    """Test that loading config fails when file doesn't exist"""
    # Point to non-existent location
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"

        with pytest.raises(ConfigError, match="Configuration not found"):
            load_config(config_path)


def test_load_config_success(tmp_path):
    """Test successful config loading"""
    config_path = tmp_path / "config.json"
    config_data = {
        "vault_path": "/home/user/JobSearch",
        "user_context": {
            "name": "Test User",
            "roles": ["Engineer"]
        }
    }
    config_path.write_text(json.dumps(config_data))

    result = load_config(config_path)
    assert result == config_data


def test_get_vault_path(tmp_path):
    """Test extracting vault path from config"""
    config_path = tmp_path / "config.json"
    vault_path = str(tmp_path / "vault")
    config_data = {"vault_path": vault_path}
    config_path.write_text(json.dumps(config_data))

    result = get_vault_path(config_path)
    assert result == Path(vault_path)


def test_save_config(tmp_path):
    """Test saving config to file"""
    config_path = tmp_path / "config.json"
    config_data = {
        "vault_path": "/test/path",
        "user_context": {"name": "User"}
    }

    save_config(config_path, config_data)

    assert config_path.exists()
    loaded = json.loads(config_path.read_text())
    assert loaded == config_data
