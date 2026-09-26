#!/usr/bin/env python3
"""Demonstration of the application lookup optimization."""

from pathlib import Path
import tempfile
from datetime import date

from job_search_mcp.service import JobSearchService
from job_search_mcp.models import ApplicationRecord, ApplicationStatus


def demo():
    """Demonstrate the application index optimization."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = Path(tmpdir) / "vault"
        vault_root.mkdir()
        
        service = JobSearchService(vault_root=str(vault_root))
        
        print("=== Application Lookup Optimization Demo ===\n")
        
        # Create an application
        print("1. Creating application note...")
        app = ApplicationRecord(
            company="Acme Corp",
            company_key="acme-corp",
            role="Senior Engineer",
            application_key="acme-corp-senior-engineer",
            status=ApplicationStatus.APPLIED,
            created=date(2026, 3, 1),
            last_updated=date(2026, 3, 7),
        )
        service.write_application_note(app)
        print("   ✓ Application note created")
        
        # Check the tracker
        print("\n2. Checking Company Tracking note...")
        tracker = service.read_company_tracking()
        print(f"   Applications in index: {len(tracker.applications)}")
        if "acme-corp-senior-engineer" in tracker.applications:
            path = tracker.applications["acme-corp-senior-engineer"]
            print(f"   ✓ Index entry: acme-corp-senior-engineer -> {path}")
        
        # Read it back
        print("\n3. Reading application via index...")
        read_app = service.read_application_note("acme-corp-senior-engineer")
        if read_app:
            print(f"   ✓ Found: {read_app.company} - {read_app.role}")
            print(f"   Status: {read_app.status.value}")
        
        # Show the tracker content
        print("\n4. Company Tracking note content:")
        tracker_path = vault_root / "Company Tracking.md"
        content = tracker_path.read_text()
        print("   " + "\n   ".join(content.split("\n")))
        
        print("\n=== Performance Benefit ===")
        print("Before: O(n × file_size) - scan all application files")
        print("After:  O(1) - direct path lookup from index")
        print("\nWith 100 applications:")
        print("  Before: Read 100 files, search each for matching key")
        print("  After:  Read 1 file directly from index")


if __name__ == "__main__":
    demo()
