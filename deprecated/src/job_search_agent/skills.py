"""OpenClaw skills for job search agent."""

from datetime import date, datetime, time, timedelta
from typing import Optional

from job_search_mcp.service import JobSearchService
from job_search_mcp.models import CompanySignal, SignalType
from job_search_mcp.ingestion import ingest_signal, classify_signal
from job_search_mcp.notes.daily import DailyNote, append_daily_activity, refresh_schedule_vs_activity


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
        
        plan_lines = [f"# {target_date.isoformat()}", "", "## Schedule", ""]
        
        # Use profile scheduling preferences if available
        if profile and profile.scheduling_preferences:
            plan_lines.append(profile.scheduling_preferences)
        else:
            # Default schedule
            plan_lines.extend([
                "- 9:00 AM - 11:00 AM: LeetCode practice",
                "- 2:00 PM - 4:00 PM: Job search activities",
            ])
        
        # Add pending follow-ups from tracker
        pending = [
            (k, v) for k, v in tracker.companies.items()
            if v.get("next_action") and v.get("due")
        ]
        if pending:
            plan_lines.extend(["", "## Pending Follow-ups", ""])
            for company_key, company in pending:
                due = company.get("due", "")
                action = company.get("next_action", "")
                plan_lines.append(f"- {company_key}: {action} (due: {due})")
        
        # Add weak areas from performance
        if perf and perf.weak_areas:
            plan_lines.extend(["", "## Focus Areas", "", f"- {perf.weak_areas}"])
        
        plan_lines.extend(["", "## Daily Activity", "", "## Schedule vs Activity"])
        
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
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
    ) -> str:
        """Analyze and log a LeetCode problem attempt."""
        today = date.today()
        now = datetime.now()
        
        # Default to current time if not provided
        if start_time is None:
            start_time = now.time()
        if end_time is None:
            end_time = now.time()
        
        daily = self.service.read_daily_note(today)
        if daily is None:
            daily = DailyNote(date=today)
        
        daily = append_daily_activity(
            daily,
            start_time=start_time,
            end_time=end_time,
            description=f"LeetCode: {problem}",
            status=status,
            note=notes,
        )
        self.service.write_daily_note(daily)
        return f"Logged {problem} - {status}"

    def get_recommendation(self) -> str:
        """Get a practice recommendation based on performance."""
        # Check for upcoming interviews
        tracker = self.service.read_company_tracking()
        upcoming = [
            (k, v) for k, v in tracker.companies.items()
            if v.get("stage") in ["Interviewing", "Technical Screen"]
        ]
        
        if upcoming:
            companies = ", ".join(k for k, _ in upcoming)
            perf = self.service.read_performance_summary()
            if perf and perf.weak_areas:
                return f"Upcoming interviews at {companies}. Focus on: {perf.weak_areas}"
            return f"Upcoming interviews at {companies}. Review fundamentals."
        
        # No interviews, use performance data
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

    def analyze_transcript(
        self,
        company_key: str,
        transcript: str,
        interview_type: str = "technical",
    ) -> str:
        """Analyze interview transcript and update notes."""
        # Extract key information
        lines = transcript.split("\n")
        questions = [l for l in lines if "?" in l]
        
        # Update company note with interview details
        company = self.service.read_company_note(company_key)
        if not company:
            return f"Company {company_key} not found"
        
        # Add to interview history
        today = date.today()
        summary = f"{interview_type.title()} interview on {today.isoformat()}\n"
        summary += f"Questions asked: {len(questions)}\n"
        summary += f"Transcript length: {len(transcript)} chars"
        
        # Ingest as signal
        signal = classify_signal(
            company_key=company_key,
            signal_type="interview_transcript",
            summary=summary,
        )
        company = ingest_signal(self.service, signal)
        
        return f"Analyzed transcript for {company.company}: {len(questions)} questions identified"

    def leetcode_help(
        self,
        problem: str,
        current_approach: Optional[str] = None,
    ) -> str:
        """Get help with a LeetCode problem based on weak areas."""
        perf = self.service.read_performance_summary()
        
        hints = []
        if perf and perf.weak_areas:
            hints.append(f"Consider your weak areas: {perf.weak_areas}")
        
        if current_approach:
            hints.append("Review time/space complexity of your current approach")
            hints.append("Consider alternative data structures")
        else:
            hints.append("Start by identifying the problem pattern")
            hints.append("Draw out examples and look for patterns")
        
        return "\n".join(hints)

    def schedule_reminder(
        self,
        company_key: str,
        action: str,
        due_date: date,
    ) -> str:
        """Schedule a follow-up reminder for a company."""
        company = self.service.read_company_note(company_key)
        if not company:
            return f"Company {company_key} not found"
        
        # Update company with next action
        signal = classify_signal(
            company_key=company_key,
            signal_type="manual_note",
            summary=f"Reminder: {action}",
            next_action=action,
            due_date=due_date,
        )
        company = ingest_signal(self.service, signal)
        
        return f"Scheduled reminder for {company.company}: {action} on {due_date.isoformat()}"
