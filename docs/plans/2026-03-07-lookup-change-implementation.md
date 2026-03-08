# Application Lookup Optimization - Implementation Summary

## Problem

`read_application_note` was performing O(n × file_size) lookups by recursively scanning every markdown file in the Applications directory and reading each file body until finding a matching `application_key`. As the vault grows, this degrades response time significantly.

## Solution

Implemented an application index in the Company Tracking note, mirroring the existing pattern used for company notes:

1. **Added application index to CompanyTracking model** - New `applications: dict[str, str]` field maps `application_key -> note_path`

2. **Updated tracker parsing** - Parse "## Application Index" section from tracker note with format:
   ```
   ## Application Index
   
   - application_key: path/to/note.md
   ```

3. **Updated tracker rendering** - Render application index at end of tracker note

4. **Optimized read_application_note** - Try index lookup first (O(1)), fall back to scanning for backward compatibility

5. **Updated write_application_note** - Automatically maintain index when writing application notes

## Changes

### src/job_search_mcp/notes/tracker.py
- Added `applications` field to `CompanyTracking` dataclass
- Updated `parse_company_tracking` to parse application index section
- Updated `render_company_tracking` to render application index section

### src/job_search_mcp/service.py
- Updated `read_application_note` to use index with fallback to scanning
- Updated `write_application_note` to maintain the index

### tests/notes/test_tracker_note.py
- Added test for parsing application index
- Added test for rendering application index
- Updated empty tracker test to verify empty applications dict

### tests/test_service.py
- Added `TestServiceApplicationNoteResolution` test class
- Test index-based lookup
- Test fallback to scanning when not in index
- Test index is updated when writing notes

## Performance Impact

- **Before**: O(n × file_size) - scan all application files
- **After**: O(1) - direct path lookup from index
- **Backward compatible**: Falls back to scanning if index entry missing

## Migration Path

No migration needed. The system works with or without the index:
- New applications automatically get indexed when written
- Old applications without index entries fall back to scanning
- Index builds up naturally as applications are created/updated

## Test Results

All 80 tests pass, including 5 new tests specifically for the application index functionality.
