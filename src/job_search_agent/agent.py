"""Job search agent wrapper for OpenClaw."""

from datetime import date, datetime, timedelta
from typing import Optional
import re

from job_search_mcp.service import JobSearchService
from .skills import JobSearchSkills


class JobSearchAgent:
    """Job search agent for OpenClaw integration."""

    def __init__(self, vault_root: Optional[str] = None):
        self.service = JobSearchService(vault_root=vault_root)
        self.skills = JobSearchSkills(self.service)

    def handle_message(self, message: str) -> str:
        """Handle an incoming message and return a response."""
        try:
            msg = message.lower().strip()

            # Plan commands
            if "plan tomorrow" in msg:
                target = date.today() + timedelta(days=1)
                plan = self.skills.generate_plan(target)
                return f"Here's your plan for {target.isoformat()}:\n\n{plan}"

            # Ingest commands - extract company and signal
            if "ingest" in msg or "signal" in msg:
                # Try to extract company name (simple pattern)
                company_match = re.search(r"(?:for|at|from)\s+([A-Z][a-zA-Z0-9\s]+?)(?:\s+(?:that|about|:|$))", message)
                if company_match:
                    company = company_match.group(1).strip()
                    # Extract signal type
                    signal_type = "general"
                    if "rejection" in msg or "rejected" in msg:
                        signal_type = "rejection"
                    elif "interview" in msg:
                        signal_type = "interview_scheduled"
                    elif "offer" in msg:
                        signal_type = "offer"
                    elif "applied" in msg or "application" in msg:
                        signal_type = "application_submitted"
                    
                    return self.skills.ingest_company_signal(
                        company_key=company.replace(" ", "_"),
                        signal_type=signal_type,
                        summary=message,
                    )
                return "Please specify company name: 'ingest signal for [Company] about [details]'"

            # LeetCode commands - extract problem name
            if "just did" in msg or "leetcode" in msg:
                problem_match = re.search(r"(?:did|solved|completed)\s+([A-Za-z0-9\s\-]+?)(?:\s+(?:and|,|$))", message)
                problem = problem_match.group(1).strip() if problem_match else "problem"
                
                # Extract status
                status = "Done"
                if "struggled" in msg or "hard" in msg or "couldn't" in msg:
                    status = "Struggled"
                elif "easy" in msg or "quick" in msg:
                    status = "Easy"
                
                return self.skills.analyze_leetcode(
                    problem=problem,
                    notes=message,
                    status=status,
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
        
        except Exception as e:
            return f"Error: {str(e)}"
