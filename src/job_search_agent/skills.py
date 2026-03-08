"""OpenClaw skills for job search agent."""

from datetime import date, datetime, timedelta
from typing import Optional

from job_search_mcp.service import JobSearchService
from job_search_mcp.models import CompanySignal, SignalType
from job_search_mcp.ingestion import ingest_signal, classify_signal


class JobSearchSkills:
    """Job search skills for OpenClaw."""

    def __init__(self, service: JobSearchService):
        self.service = service

    def generate_plan(self, target_date: date) -> str:
        """Generate a daily plan for the target date."""
        yesterday = target_date - timedelta(days=1)
        
        # Gather context
        yesterday_note = self.service.read_daily_note(yesterday)
        tracker = self.service.read_company_tracking()
        profile = self.service.read_candidate_profile()
        perf = self.service.read_performance_summary()
        
        # Build plan structure
        plan_lines = [f"# {target_date.isoformat()}", "", "## Schedule", ""]
        
        # Add default blocks
        plan_lines.extend([
            "- 9:00 AM - 11:00 AM: LeetCode practice",
            "- 2:00 PM - 4:00 PM: Job search activities",
            "", "## Daily Activity", "", "## Schedule vs Activity",
        ])
        
        return "\n".join(plan_lines)

    def ingest_company_signal(
        self,
        company_key: str,
        signal_type: str,
        summary: str,
        source_marker: Optional[str] = None,
        stage: Optional[str] = None,
        sentiment: Optional[str] = None,
        next_action: Optional[str] = None,
        due_date: Optional[date] = None,
    ) -> str:
        """Ingest a company signal into the vault."""
        signal = classify_signal(
            company_key=company_key,
            signal_type=signal_type,
            summary=summary,
            source_marker=source_marker,
            stage=stage,
            sentiment=sentiment,
            next_action=next_action,
            due_date=due_date,
        )
        company = ingest_signal(self.service, signal)
        return f"Updated {company.company}: {summary}"

    def analyze_leetcode(
        self,
        problem: str,
        notes: str,
        status: str = "Done",
    ) -> str:
        """Analyze and log a LeetCode problem attempt."""
        today = date.today()
        
        # Append to daily activity
        from job_search_mcp.notes.daily import DailyNote, append_daily_activity
        from datetime import time
        
        daily = self.service.read_daily_note(today)
        if daily is None:
            daily = DailyNote(date=today)
        
        daily = append_daily_activity(
            daily,
            start_time=time(9, 0),
            end_time=time(11, 0),
            description=f"LeetCode: {problem}",
            status=status,
            note=notes,
        )
        self.service.write_daily_note(daily)
        return f"Logged {problem} - {status}"

    def get_recommendation(self) -> str:
        """Get a practice recommendation based on performance."""
        perf = self.service.read_performance_summary()
        if perf and perf.weak_areas:
            return f"Focus on: {perf.weak_areas}"
        return "Practice dynamic programming and system design"

    def end_of_day(self, target_date: Optional[date] = None) -> str:
        """Run end-of-day processing."""
        target_date = target_date or date.today()
        
        # Refresh schedule vs activity
        from job_search_mcp.notes.daily import refresh_schedule_vs_activity
        daily = self.service.read_daily_note(target_date)
        if daily:
            daily = refresh_schedule_vs_activity(daily)
            self.service.write_daily_note(daily)
        
        # Check tracker for pending items
        tracker = self.service.read_company_tracking()
        pending = [
            c for c in tracker.companies.values()
            if c.get("next_action") and c.get("due")
        ]
        
        if pending:
            return f"End of day complete. {len(pending)} items pending."
        return "End of day complete. All caught up!"

    def list_pending_followups(self) -> list[dict]:
        """List companies with pending follow-ups."""
        tracker = self.service.read_company_tracking()
        return [
            {"company": k, **v}
            for k, v in tracker.companies.items()
            if v.get("next_action") and v.get("due")
        ]
