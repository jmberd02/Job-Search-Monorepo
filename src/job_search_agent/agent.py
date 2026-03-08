"""Job search agent wrapper for OpenClaw."""

from datetime import date
from typing import Optional

from job_search_mcp.service import JobSearchService
from .skills import JobSearchSkills


class JobSearchAgent:
    """Job search agent for OpenClaw integration."""

    def __init__(self, vault_root: Optional[str] = None):
        self.service = JobSearchService(vault_root=vault_root)
        self.skills = JobSearchSkills(self.service)

    def handle_message(self, message: str) -> str:
        """Handle an incoming message and return a response."""
        msg = message.lower().strip()

        # Plan commands
        if "plan tomorrow" in msg:
            target = date.today() + __import__("datetime").timedelta(days=1)
            plan = self.skills.generate_plan(target)
            return f"Here's your plan for {target.isoformat()}:\n\n{plan}"

        # Ingest commands
        if "ingest" in msg or "signal" in msg:
            # Simple parsing - in real usage, OpenClaw would extract entities
            return "Use ingest_company_signal skill with company_key, signal_type, and summary"

        # LeetCode commands
        if "just did" in msg or "leetcode" in msg:
            return self.skills.analyze_leetcode(
                problem="problem name",
                notes=msg,
            )

        # Recommendation commands
        if "practice" in msg or "recommend" in msg:
            return self.skills.get_recommendation()

        # End of day
        if "end of day" in msg or "eod" in msg:
            return self.skills.end_of_day()

        # Pending follow-ups
        if "pending" in msg or "follow-up" in msg:
            pending = self.skills.list_pending_followups()
            if not pending:
                return "No pending follow-ups."
            lines = ["Pending follow-ups:"]
            for p in pending:
                lines.append(f"- {p['company']}: {p.get('next_action', '')} (due: {p.get('due', '')})")
            return "\n".join(lines)

        return "Available commands: plan tomorrow, practice?, end of day, pending?"
