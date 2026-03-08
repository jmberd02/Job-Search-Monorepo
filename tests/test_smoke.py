"""Smoke test for job_search_mcp package."""
import pytest


def test_package_import():
    """Package should be importable."""
    import job_search_mcp
    assert job_search_mcp is not None


def test_version():
    """Package should have a version."""
    import job_search_mcp
    assert job_search_mcp.__version__ == "0.1.0"


def test_config_import():
    """Config module should be importable."""
    from job_search_mcp import config
    assert config is not None


def test_paths_import():
    """Paths module should be importable."""
    from job_search_mcp import paths
    assert paths is not None
