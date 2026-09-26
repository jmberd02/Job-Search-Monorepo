# tests/test_setup_tools.py
import pytest
from pathlib import Path
import json


def test_initialize_vault(tmp_path):
    """Test vault initialization"""
    from job_search_mcp.server import initialize_vault

    vault_path = tmp_path / "vault"
    user_context = {
        "name": "Test User",
        "target_roles": ["Engineer"],
        "focus_areas": ["Python"]
    }

    result = initialize_vault(str(vault_path), user_context)

    # Check vault created
    assert vault_path.exists()
    assert (vault_path / "Companies").exists()
    assert (vault_path / "Applications").exists()
    assert (vault_path / "Day").exists()
    assert (vault_path / ".claude").exists()
    assert (vault_path / ".claude" / "skills").exists()
    assert (vault_path / ".claude" / "CLAUDE.md").exists()
    assert (vault_path / "Company Tracking.md").exists()

    # Check CLAUDE.md has user context
    claude_md = (vault_path / ".claude" / "CLAUDE.md").read_text()
    assert "Test User" in claude_md


def test_get_pending_actions(tmp_path):
    """Test extracting pending actions from tracker"""
    from job_search_mcp.server import get_pending_actions_from_tracker

    # Create minimal vault with tracker
    vault_path = tmp_path / "vault"
    vault_path.mkdir()

    tracker_content = """# Company Tracking

## Needs Action This Week
| Company | Status | Next Action | Due |
|---------|--------|-------------|-----|
| Acme Corp | Active | Schedule call | 2026-04-05 |
| TechCo | Waiting | Follow up | 2026-04-06 |

## Active Interview Pipeline

### StartupCo
- Status: Interview
- Next action: Prepare for onsite
- Due: 2026-04-10
"""

    (vault_path / "Company Tracking.md").write_text(tracker_content)

    # Save config
    config_path = tmp_path / "config.json"
    config_data = {"vault_path": str(vault_path)}
    config_path.write_text(json.dumps(config_data))

    actions = get_pending_actions_from_tracker(str(config_path))

    assert len(actions) >= 2
    assert any("Acme Corp" in a["company"] for a in actions)
    assert any("TechCo" in a["company"] for a in actions)
