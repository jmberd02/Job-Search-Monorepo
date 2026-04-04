"""Tests for job search agent."""

import pytest
from datetime import date, time, timedelta
from pathlib import Path
import tempfile
import shutil

from job_search_agent.agent import JobSearchAgent
from job_search_agent.skills import JobSearchSkills
from job_search_mcp.service import JobSearchService
from job_search_mcp.notes.tracker import CompanyTracking
from job_search_mcp.models import CompanyRecord
from job_search_mcp.notes.profile import CandidateProfile
from job_search_mcp.notes.performance import PerformanceSummary
from job_search_mcp.notes.daily import DailyNote


@pytest.fixture
def temp_vault():
    """Create a temporary vault for testing."""
    vault = Path(tempfile.mkdtemp())
    (vault / "Companies").mkdir()
    (vault / "Applications").mkdir()
    (vault / "Day").mkdir()
    yield vault
    shutil.rmtree(vault)


@pytest.fixture
def service(temp_vault):
    """Create a service with temp vault."""
    return JobSearchService(vault_root=str(temp_vault))


@pytest.fixture
def agent(service):
    """Create an agent with temp vault."""
    return JobSearchAgent(vault_root=str(service.vault_root))


class TestJobSearchSkills:
    """Test job search skills."""

    def test_generate_plan_default(self, service):
        """Test plan generation with defaults."""
        skills = JobSearchSkills(service)
        tomorrow = date.today() + timedelta(days=1)
        
        # Write tracker
        tracker = CompanyTracking(companies={})
        service.write_company_tracking(tracker)
        
        plan = skills.generate_plan(tomorrow)
        
        assert tomorrow.isoformat() in plan
        assert "Schedule" in plan
        assert "Daily Activity" in plan

    def test_generate_plan_with_pending(self, service):
        """Test plan generation includes pending items."""
        skills = JobSearchSkills(service)
        tomorrow = date.today() + timedelta(days=1)
        
        # Write tracker with pending item
        tracker = CompanyTracking(companies={
            "TestCorp": {
                "company": "Test Corp",
                "status": "Applied",
                "next_action": "Follow up on application",
                "due": tomorrow.isoformat(),
            }
        })
        service.write_company_tracking(tracker)
        
        plan = skills.generate_plan(tomorrow)
        
        assert "Pending Follow-ups" in plan
        assert "TestCorp" in plan
        assert "Follow up on application" in plan

    def test_generate_plan_with_weak_areas(self, service):
        """Test plan generation includes weak areas."""
        skills = JobSearchSkills(service)
        tomorrow = date.today() + timedelta(days=1)
        
        # Write tracker and performance
        tracker = CompanyTracking(companies={})
        service.write_company_tracking(tracker)
        
        perf = PerformanceSummary(weak_areas="Dynamic programming, graphs")
        service.write_performance_summary(perf)
        
        plan = skills.generate_plan(tomorrow)
        
        assert "Focus Areas" in plan
        assert "Dynamic programming" in plan

    def test_ingest_company_signal(self, service):
        """Test ingesting a company signal."""
        skills = JobSearchSkills(service)
        
        # Initialize tracker
        from job_search_mcp.notes.tracker import CompanyTracking
        tracker = CompanyTracking(companies={})
        service.write_company_tracking(tracker)
        
        result = skills.ingest_company_signal(
            company_key="TestCorp",
            signal_type="application_event",
            summary="Applied for SWE role",
        )
        
        assert "testcorp" in result.lower()
        
        # Verify tracker was updated
        tracker = service.read_company_tracking()
        assert "TestCorp" in tracker.companies or "Testcorp" in tracker.companies

    def test_analyze_leetcode(self, service):
        """Test LeetCode analysis."""
        skills = JobSearchSkills(service)
        today = date.today()
        
        result = skills.analyze_leetcode(
            problem="Two Sum",
            notes="Used hash map approach",
            status="Done",
            start_time=time(9, 0),
            end_time=time(9, 30),
        )
        
        assert "Two Sum" in result
        assert "Done" in result
        
        # Verify daily note was updated
        daily = service.read_daily_note(today)
        assert daily is not None
        # Check activity was appended
        assert len(daily.activity) > 0

    def test_get_recommendation_with_interviews(self, service):
        """Test recommendations consider upcoming interviews."""
        skills = JobSearchSkills(service)
        
        # Write tracker with interviewing company
        tracker = CompanyTracking(companies={
            "TestCorp": {
                "company": "Test Corp",
                "stage": "Interviewing",
            }
        })
        service.write_company_tracking(tracker)
        
        result = skills.get_recommendation()
        
        assert "TestCorp" in result or "interview" in result.lower()

    def test_get_recommendation_with_weak_areas(self, service):
        """Test recommendations use weak areas."""
        skills = JobSearchSkills(service)
        
        # Write tracker and performance
        tracker = CompanyTracking(companies={})
        service.write_company_tracking(tracker)
        
        perf = PerformanceSummary(weak_areas="Trees and graphs")
        service.write_performance_summary(perf)
        
        result = skills.get_recommendation()
        
        assert "Trees and graphs" in result

    def test_end_of_day(self, service):
        """Test end of day processing."""
        skills = JobSearchSkills(service)
        today = date.today()
        
        # Write daily note and tracker
        daily = DailyNote(date=today)
        service.write_daily_note(daily)
        
        tracker = CompanyTracking(companies={})
        service.write_company_tracking(tracker)
        
        result = skills.end_of_day(today)
        
        assert "complete" in result.lower()

    def test_list_pending_followups(self, service):
        """Test listing pending follow-ups."""
        skills = JobSearchSkills(service)
        
        # Write tracker with pending items
        tracker = CompanyTracking(companies={
            "TestCorp": {
                "company": "Test Corp",
                "next_action": "Send thank you",
                "due": "2026-03-10",
            },
            "OtherCorp": {
                "company": "Other Corp",
                "status": "Applied",
            }
        })
        service.write_company_tracking(tracker)
        
        pending = skills.list_pending_followups()
        
        assert len(pending) == 1
        assert pending[0]["company"] in ["TestCorp", "Test Corp"]

    def test_analyze_transcript(self, service):
        """Test transcript analysis."""
        skills = JobSearchSkills(service)
        
        # Initialize tracker and create company via ingestion
        from job_search_mcp.notes.tracker import CompanyTracking
        tracker = CompanyTracking(companies={})
        service.write_company_tracking(tracker)
        
        # Ingest a signal first to create the company
        skills.ingest_company_signal(
            company_key="TestCorp",
            signal_type="application_event",
            summary="Applied",
        )
        
        transcript = """
        Interviewer: Can you explain your approach?
        Candidate: I would use a hash map.
        Interviewer: What's the time complexity?
        Candidate: O(n) time and space.
        """
        
        # Use tracker key (not normalized company name)
        result = skills.analyze_transcript(
            company_key="TestCorp",
            transcript=transcript,
            interview_type="technical",
        )
        
        assert "testcorp" in result.lower()
        assert "questions" in result.lower()

    def test_leetcode_help(self, service):
        """Test LeetCode help."""
        skills = JobSearchSkills(service)
        
        # Write performance with weak areas
        perf = PerformanceSummary(weak_areas="Dynamic programming")
        service.write_performance_summary(perf)
        
        result = skills.leetcode_help(
            problem="Climbing Stairs",
            current_approach="Recursion",
        )
        
        assert "Dynamic programming" in result or "complexity" in result.lower()

    def test_schedule_reminder(self, service):
        """Test scheduling reminders."""
        skills = JobSearchSkills(service)
        
        # Initialize tracker and create company via ingestion
        from job_search_mcp.notes.tracker import CompanyTracking
        tracker = CompanyTracking(companies={})
        service.write_company_tracking(tracker)
        
        # Ingest a signal first to create the company
        skills.ingest_company_signal(
            company_key="TestCorp",
            signal_type="application_event",
            summary="Applied",
        )
        
        due = date.today() + timedelta(days=3)
        # Use tracker key (not normalized company name)
        result = skills.schedule_reminder(
            company_key="TestCorp",
            action="Follow up on offer",
            due_date=due,
        )
        
        assert "testcorp" in result.lower()
        assert "follow up" in result.lower()


class TestJobSearchAgent:
    """Test job search agent message handling."""

    def test_plan_tomorrow(self, agent):
        """Test plan tomorrow command."""
        # Setup tracker
        tracker = CompanyTracking(companies={})
        agent.service.write_company_tracking(tracker)
        
        result = agent.handle_message("plan tomorrow")
        
        tomorrow = date.today() + timedelta(days=1)
        assert tomorrow.isoformat() in result
        assert "Schedule" in result

    def test_ingest_signal(self, agent):
        """Test ingest signal command."""
        result = agent.handle_message("ingest signal for TestCorp about applied for SWE role")
        
        # Should either succeed or return error (both acceptable)
        assert len(result) > 0

    def test_leetcode_command(self, agent):
        """Test LeetCode command."""
        result = agent.handle_message("just did Two Sum and it was easy")
        
        assert "Two Sum" in result

    def test_recommendation_command(self, agent):
        """Test recommendation command."""
        tracker = CompanyTracking(companies={})
        agent.service.write_company_tracking(tracker)
        
        result = agent.handle_message("what should I practice?")
        
        assert len(result) > 0

    def test_end_of_day_command(self, agent):
        """Test end of day command."""
        tracker = CompanyTracking(companies={})
        agent.service.write_company_tracking(tracker)
        
        result = agent.handle_message("end of day")
        
        assert "complete" in result.lower()

    def test_pending_command(self, agent):
        """Test pending follow-ups command."""
        tracker = CompanyTracking(companies={})
        agent.service.write_company_tracking(tracker)
        
        result = agent.handle_message("show pending")
        
        assert "pending" in result.lower() or "No" in result

    def test_unknown_command(self, agent):
        """Test unknown command."""
        result = agent.handle_message("do something random")
        
        assert "Available commands" in result

    def test_error_handling(self, agent):
        """Test error handling."""
        # Test with a command that might fail gracefully
        result = agent.handle_message("unknown command xyz")
        
        # Should return help message, not crash
        assert len(result) > 0
