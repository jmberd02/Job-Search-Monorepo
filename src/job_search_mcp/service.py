"""Filesystem service layer for job-search-mcp."""

import os
import re
from datetime import date
from pathlib import Path
from typing import Optional

from .paths import (
    get_vault_root,
    get_companies_dir,
    get_applications_dir,
    get_daily_dir,
    get_tracker_path,
    get_profile_path,
    get_performance_path,
)
from .notes.company import parse_company_note, render_company_note
from .notes.application import parse_application_note, render_application_note
from .notes.tracker import parse_company_tracking, render_company_tracking, CompanyTracking
from .notes.daily import parse_daily_note, render_daily_note, DailyNote
from .notes.profile import parse_candidate_profile, render_candidate_profile, CandidateProfile
from .notes.performance import parse_performance_summary, render_performance_summary, PerformanceSummary
from .models import CompanyRecord, ApplicationRecord


class JobSearchService:
    """Service for reading and writing Obsidian vault notes."""

    def __init__(self, vault_root: Optional[str] = None, config_path: Optional[Path] = None):
        """
        Initialize the service with a vault root path.

        Args:
            vault_root: Optional explicit vault root path
            config_path: Optional path to config file
        """
        if vault_root:
            self._vault_root = Path(vault_root)
        else:
            self._vault_root = get_vault_root(config_path)

        # Ensure directories exist
        self._ensure_directories()
        
        # Cache for tracker to avoid repeated reads; invalidated when file mtime changes
        self._tracker_cache: Optional[CompanyTracking] = None
        self._tracker_mtime: Optional[float] = None

    def _ensure_directories(self):
        """Ensure required directories exist."""
        get_companies_dir(self._vault_root).mkdir(parents=True, exist_ok=True)
        get_applications_dir(self._vault_root).mkdir(parents=True, exist_ok=True)
        get_daily_dir(self._vault_root).mkdir(parents=True, exist_ok=True)

    @property
    def vault_root(self) -> Path:
        """Get the vault root path."""
        return self._vault_root

    # Company Note Operations

    def read_company_note(self, company_key: str) -> Optional[CompanyRecord]:
        """Read a company note from the vault."""
        # Primary: direct lookup by company_key slug (files written by write_company_note)
        direct_path = get_companies_dir(self._vault_root) / f"{company_key}.md"
        if direct_path.exists():
            return parse_company_note(direct_path.read_text())

        # Fallback: tracker-based lookup for legacy files named by display name
        tracker = self.read_company_tracking()
        if not tracker or company_key not in tracker.companies:
            return None

        company_entry = tracker.companies[company_key]

        note_path = None
        if "company_note_path" in company_entry:
            note_path = self._vault_root / company_entry["company_note_path"]
        elif "notes" in company_entry:
            notes = company_entry["notes"]
            match = re.search(r'\[\[([^\]]+)\]\]', notes)
            if match:
                link = match.group(1)
                note_path = self._vault_root / (link + ".md" if not link.endswith(".md") else link)

        if not note_path or not note_path.exists():
            return None

        return parse_company_note(note_path.read_text())

    def write_company_note(self, record: CompanyRecord) -> None:
        """Write a company note to the vault."""
        companies_dir = get_companies_dir(self._vault_root)
        file_path = companies_dir / f"{record.company_key}.md"
        text = render_company_note(record)
        file_path.write_text(text)

    def list_company_notes(self) -> list[str]:
        """List all company keys in the vault."""
        tracker = self.read_company_tracking()
        return list(tracker.companies.keys())

    # Application Note Operations

    def read_application_note(self, application_key: str) -> Optional[ApplicationRecord]:
        """Read an application note from the vault."""
        # Try index lookup first
        tracker = self.read_company_tracking()
        if tracker and application_key in tracker.applications:
            note_path = self._vault_root / tracker.applications[application_key]
            if note_path.exists():
                content = note_path.read_text()
                return parse_application_note(content)
        
        # Fallback to scanning (for backward compatibility)
        apps_dir = get_applications_dir(self._vault_root)
        for file_path in apps_dir.rglob("*.md"):
            content = file_path.read_text()
            if f"application_key: {application_key}" in content:
                return parse_application_note(content)
        return None

    def write_application_note(self, record: ApplicationRecord) -> None:
        """Write an application note to the vault."""
        apps_dir = get_applications_dir(self._vault_root)
        apps_dir.mkdir(parents=True, exist_ok=True)
        file_path = apps_dir / f"{record.company} - {record.role}.md"
        text = render_application_note(record)
        file_path.write_text(text)
        
        # Update application index
        tracker = self.read_company_tracking()
        relative_path = file_path.relative_to(self._vault_root)
        tracker.applications[record.application_key] = str(relative_path)
        self.write_company_tracking(tracker)

    # Company Tracking Operations

    def read_company_tracking(self) -> CompanyTracking:
        """Read the company tracking note, refreshing from disk if the file has changed."""
        tracker_path = get_tracker_path(self._vault_root)
        current_mtime = tracker_path.stat().st_mtime if tracker_path.exists() else None

        if self._tracker_cache is not None and current_mtime == self._tracker_mtime:
            return self._tracker_cache

        if tracker_path.exists():
            self._tracker_cache = parse_company_tracking(tracker_path.read_text())
            self._tracker_mtime = current_mtime
        else:
            self._tracker_cache = CompanyTracking()
            self._tracker_mtime = None
        return self._tracker_cache

    def write_company_tracking(self, tracker: CompanyTracking) -> None:
        """Write the company tracking note."""
        tracker_path = get_tracker_path(self._vault_root)
        text = render_company_tracking(tracker)
        tracker_path.write_text(text)
        self._tracker_cache = tracker
        self._tracker_mtime = tracker_path.stat().st_mtime

    def upsert_company_tracking_entry(
        self,
        company_key: str,
        company_name: str,
        status: str,
        interest: int,
        current_state: str,
        next_action: str,
        due_date: Optional[date] = None,
        applications: Optional[list[str]] = None,
        contacts: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Add or update a company entry in the tracker."""
        tracker = self.read_company_tracking()
        from .notes.tracker import upsert_company_tracking_entry
        tracker = upsert_company_tracking_entry(
            tracker,
            company_key=company_key,
            company_name=company_name,
            status=status,
            interest=interest,
            current_state=current_state,
            next_action=next_action,
            due_date=due_date,
            applications=applications,
            contacts=contacts,
            notes=notes,
        )
        self.write_company_tracking(tracker)

    # Daily Note Operations

    def read_daily_note(self, note_date: date) -> Optional[DailyNote]:
        """Read a daily note."""
        daily_path = get_daily_dir(self._vault_root) / f"{note_date.isoformat()}.md"
        if daily_path.exists():
            return parse_daily_note(daily_path.read_text())
        return None

    def write_daily_note(self, daily: DailyNote) -> None:
        """Write a daily note."""
        daily_path = get_daily_dir(self._vault_root) / f"{daily.date.isoformat()}.md"
        text = render_daily_note(daily)
        daily_path.write_text(text)

    # Candidate Profile Operations

    def read_candidate_profile(self) -> Optional[CandidateProfile]:
        """Read the candidate profile note."""
        profile_path = get_profile_path(self._vault_root)
        if profile_path.exists():
            return parse_candidate_profile(profile_path.read_text())
        return None

    def write_candidate_profile(self, profile: CandidateProfile) -> None:
        """Write the candidate profile note."""
        profile_path = get_profile_path(self._vault_root)
        text = render_candidate_profile(profile)
        profile_path.write_text(text)

    # Performance Summary Operations

    def read_performance_summary(self) -> Optional[PerformanceSummary]:
        """Read the performance summary note."""
        perf_path = get_performance_path(self._vault_root)
        if perf_path.exists():
            return parse_performance_summary(perf_path.read_text())
        return None

    def write_performance_summary(self, perf: PerformanceSummary) -> None:
        """Write the performance summary note."""
        perf_path = get_performance_path(self._vault_root)
        text = render_performance_summary(perf)
        perf_path.write_text(text)
