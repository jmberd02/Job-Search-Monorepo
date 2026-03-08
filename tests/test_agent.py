"""Tests for job search agent."""
import pytest
from datetime import date, timedelta
import tempfile


class TestJobSearchAgent:
    """Tests for the job search agent."""

    def test_agent_initialization(self):
        """Agent should initialize with service."""
        from job_search_agent.agent import JobSearchAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = JobSearchAgent(vault_root=tmp)
            assert agent.service is not None
            assert agent.skills is not None

    def test_skills_initialization(self):
        """Skills should initialize with service."""
        from job_search_agent.skills import JobSearchSkills
        from job_search_mcp.service import JobSearchService

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)
            skills = JobSearchSkills(service)
            assert skills.service is not None

    def test_generate_plan(self):
        """generate_plan should return a plan string."""
        from job_search_agent.skills import JobSearchSkills
        from job_search_mcp.service import JobSearchService

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)
            skills = JobSearchSkills(service)
            plan = skills.generate_plan(date.today())
            assert "# " + date.today().isoformat() in plan
            assert "## Schedule" in plan

    def test_analyze_leetcode(self):
        """analyze_leetcode should append to daily activity."""
        from job_search_agent.skills import JobSearchSkills
        from job_search_mcp.service import JobSearchService

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)
            skills = JobSearchSkills(service)
            result = skills.analyze_leetcode(
                problem="Two Sum",
                notes="Solved with hash map",
            )
            assert "Two Sum" in result
            assert "Done" in result

    def test_list_pending_followups(self):
        """list_pending_followups should return empty list initially."""
        from job_search_agent.skills import JobSearchSkills
        from job_search_mcp.service import JobSearchService

        with tempfile.TemporaryDirectory() as tmp:
            service = JobSearchService(vault_root=tmp)
            skills = JobSearchSkills(service)
            pending = skills.list_pending_followups()
            assert pending == []

    def test_handle_plan_message(self):
        """handle_message should process plan commands."""
        from job_search_agent.agent import JobSearchAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = JobSearchAgent(vault_root=tmp)
            response = agent.handle_message("plan tomorrow")
            assert "plan" in response.lower()

    def test_handle_recommendation_message(self):
        """handle_message should process practice commands."""
        from job_search_agent.agent import JobSearchAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = JobSearchAgent(vault_root=tmp)
            response = agent.handle_message("what should I practice")
            assert response is not None
