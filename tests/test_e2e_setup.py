"""End-to-end test of complete setup flow."""

import pytest
from pathlib import Path
import json


def test_complete_setup_flow(tmp_path):
    """Test complete setup from config to vault creation"""
    from job_search_mcp.config import save_config, load_config
    from job_search_mcp.server import initialize_vault

    # 1. User context
    user_context = {
        "name": "Test User",
        "target_roles": ["Senior Engineer", "Staff Engineer"],
        "focus_areas": ["Python", "Distributed Systems"],
        "compensation": "$200k-$250k",
        "location": "Remote or SF Bay Area"
    }

    # 2. Initialize vault (simulating setup wizard)
    vault_path = tmp_path / "JobSearch"
    result = initialize_vault(str(vault_path), user_context)

    assert "✓ Vault created" in result

    # 3. Verify vault structure
    assert vault_path.exists()
    assert (vault_path / "Companies").is_dir()
    assert (vault_path / "Applications").is_dir()
    assert (vault_path / "Day").is_dir()
    assert (vault_path / ".claude").is_dir()
    assert (vault_path / ".claude" / "skills").is_dir()

    # 4. Verify CLAUDE.md has user context
    claude_md = (vault_path / ".claude" / "CLAUDE.md").read_text()
    assert "Test User" in claude_md
    assert "Senior Engineer" in claude_md
    assert "Python" in claude_md

    # 5. Verify config saved
    config_path = Path.home() / ".job-search" / "config.json"
    if config_path.exists():
        config = load_config(config_path)
        assert "vault_path" in config
        assert "user_context" in config

    # 6. Verify Company Tracking exists
    tracker = vault_path / "Company Tracking.md"
    assert tracker.exists()
    assert "Needs Action This Week" in tracker.read_text()

    # 7. Verify README exists
    readme = vault_path / "README.md"
    assert readme.exists()
    assert "Quick Start" in readme.read_text()

    print("✓ End-to-end setup test passed!")


def test_config_integration(tmp_path):
    """Test config system integrates with service"""
    from job_search_mcp.config import save_config
    from job_search_mcp.service import JobSearchService

    # Create config and vault
    config_path = tmp_path / "config.json"
    vault_path = tmp_path / "vault"
    vault_path.mkdir()

    # Ensure required directories exist
    (vault_path / "Companies").mkdir()
    (vault_path / "Applications").mkdir()
    (vault_path / "Day").mkdir()

    save_config(config_path, {"vault_path": str(vault_path)})

    # Create service with config
    service = JobSearchService(config_path=config_path)

    assert service.vault_root == vault_path

    print("✓ Config integration test passed!")
