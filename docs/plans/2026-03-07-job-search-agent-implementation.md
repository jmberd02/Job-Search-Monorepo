# Job Search Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a v1 local `job-search-mcp` that can read and update the Obsidian vault using the approved company-first schema.

**Architecture:** Start with a pure local vault integration layer and no external services. Implement strict markdown note parsing and rendering for company notes, application notes, company tracking, candidate profile, and daily notes, then add signal ingestion on top of those primitives.

**Tech Stack:** Python 3, pytest, markdown/frontmatter parsing, local filesystem I/O

---

## Commit Identity Rule

Before creating any commit for this plan, stop and ask the user which Git author identity should be used.

- do not assume the default local Git identity
- do not change global Git config
- use per-commit author configuration, for example:

```bash
git -c user.name="<chosen name>" -c user.email="<chosen email>" commit -m "..."
```

## Assumed Repo Layout

This repo does not currently contain the MCP implementation. This plan assumes the implementation will be created here with the following structure:

- `pyproject.toml`
- `src/job_search_mcp/__init__.py`
- `src/job_search_mcp/config.py`
- `src/job_search_mcp/models.py`
- `src/job_search_mcp/paths.py`
- `src/job_search_mcp/notes/company.py`
- `src/job_search_mcp/notes/application.py`
- `src/job_search_mcp/notes/tracker.py`
- `src/job_search_mcp/notes/daily.py`
- `src/job_search_mcp/notes/profile.py`
- `src/job_search_mcp/service.py`
- `tests/...`

If implementation happens in a different repo, preserve the task order but rebase the file paths.

### Task 1: Scaffold the Python package

**Files:**
- Create: `pyproject.toml`
- Create: `src/job_search_mcp/__init__.py`
- Create: `src/job_search_mcp/config.py`
- Create: `src/job_search_mcp/paths.py`
- Create: `tests/test_smoke.py`

**Step 1: Write the failing test**

Create `tests/test_smoke.py` with a basic import test for `job_search_mcp`.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL because the package does not exist yet.

**Step 3: Write minimal implementation**

- define package metadata in `pyproject.toml`
- create the package directory
- add a minimal importable module
- add config/path helpers for the Obsidian vault root

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add pyproject.toml src/job_search_mcp/__init__.py src/job_search_mcp/config.py src/job_search_mcp/paths.py tests/test_smoke.py
git commit -m "feat: scaffold job search mcp package"
```

### Task 2: Define core models and enums

**Files:**
- Create: `src/job_search_mcp/models.py`
- Create: `tests/test_models.py`

**Step 1: Write the failing test**

Cover:

- `CompanyRecord`
- `ApplicationRecord`
- `CompanySignal`
- enums for company status, application status, signal type, task state

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL because the models do not exist.

**Step 3: Write minimal implementation**

Use dataclasses or pydantic models with explicit field names matching the approved schema.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/models.py tests/test_models.py
git commit -m "feat: add core note and signal models"
```

### Task 3: Implement company note parser and renderer

**Files:**
- Create: `src/job_search_mcp/notes/company.py`
- Create: `tests/notes/test_company_note.py`

**Step 1: Write the failing test**

Cover:

- parsing frontmatter into `CompanyRecord`
- locating required headings
- round-tripping a company note
- preserving freeform `Notes`
- appending a timeline row without duplicating a source marker

**Step 2: Run test to verify it fails**

Run: `pytest tests/notes/test_company_note.py -v`
Expected: FAIL because the parser does not exist.

**Step 3: Write minimal implementation**

Implement:

- `parse_company_note(text)`
- `render_company_note(record)`
- `append_company_timeline(record, signal)`

**Step 4: Run test to verify it passes**

Run: `pytest tests/notes/test_company_note.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/notes/company.py tests/notes/test_company_note.py
git commit -m "feat: support company note parsing and rendering"
```

### Task 4: Implement application note parser and renderer

**Files:**
- Create: `src/job_search_mcp/notes/application.py`
- Create: `tests/notes/test_application_note.py`

**Step 1: Write the failing test**

Cover:

- parsing frontmatter and `Snapshot`
- round-tripping role-specific notes and tasks
- updating interview process rows
- matching on `application_key`

**Step 2: Run test to verify it fails**

Run: `pytest tests/notes/test_application_note.py -v`
Expected: FAIL because the parser does not exist.

**Step 3: Write minimal implementation**

Implement:

- `parse_application_note(text)`
- `render_application_note(record)`
- `upsert_application_interview_event(record, event)`

**Step 4: Run test to verify it passes**

Run: `pytest tests/notes/test_application_note.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/notes/application.py tests/notes/test_application_note.py
git commit -m "feat: support application note parsing and rendering"
```

### Task 5: Implement company tracking parser and renderer

**Files:**
- Create: `src/job_search_mcp/notes/tracker.py`
- Create: `tests/notes/test_tracker_note.py`

**Step 1: Write the failing test**

Cover:

- parsing company-first tracker sections
- updating current operational state for a company
- linking zero, one, or many application notes
- preserving company-first structure

**Step 2: Run test to verify it fails**

Run: `pytest tests/notes/test_tracker_note.py -v`
Expected: FAIL because the tracker parser does not exist.

**Step 3: Write minimal implementation**

Implement:

- `parse_company_tracking(text)`
- `render_company_tracking(tracker)`
- `upsert_company_tracking_entry(tracker, company_entry)`

**Step 4: Run test to verify it passes**

Run: `pytest tests/notes/test_tracker_note.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/notes/tracker.py tests/notes/test_tracker_note.py
git commit -m "feat: support company tracking read and write"
```

### Task 6: Implement candidate profile and top-level performance summary support

**Files:**
- Create: `src/job_search_mcp/notes/profile.py`
- Create: `src/job_search_mcp/notes/performance.py`
- Create: `tests/notes/test_profile_note.py`
- Create: `tests/notes/test_performance_note.py`

**Step 1: Write the failing tests**

Cover:

- reading/writing a minimal candidate profile schema
- reading/writing the top-level performance summary

**Step 2: Run tests to verify they fail**

Run: `pytest tests/notes/test_profile_note.py tests/notes/test_performance_note.py -v`
Expected: FAIL because the modules do not exist.

**Step 3: Write minimal implementation**

Implement parsing and rendering utilities for both note types.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/notes/test_profile_note.py tests/notes/test_performance_note.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/notes/profile.py src/job_search_mcp/notes/performance.py tests/notes/test_profile_note.py tests/notes/test_performance_note.py
git commit -m "feat: add profile and performance summary support"
```

### Task 7: Implement daily note support for new-format writes

**Files:**
- Create: `src/job_search_mcp/notes/daily.py`
- Create: `tests/notes/test_daily_note.py`

**Step 1: Write the failing test**

Cover:

- creating a new daily note in the target format
- appending `Daily Activity`
- generating `Schedule vs Activity`
- leaving legacy daily notes readable even if not migrated

**Step 2: Run test to verify it fails**

Run: `pytest tests/notes/test_daily_note.py -v`
Expected: FAIL because the parser does not exist.

**Step 3: Write minimal implementation**

Implement:

- `parse_daily_note(text)`
- `render_daily_note(record)`
- `append_daily_activity(record, block, status, note)`
- `refresh_schedule_vs_activity(record)`

**Step 4: Run test to verify it passes**

Run: `pytest tests/notes/test_daily_note.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/notes/daily.py tests/notes/test_daily_note.py
git commit -m "feat: support daily note writes and activity logging"
```

### Task 8: Implement filesystem service layer

**Files:**
- Create: `src/job_search_mcp/service.py`
- Create: `tests/test_service.py`

**Step 1: Write the failing test**

Cover:

- `read_company_note`
- `upsert_company_note`
- `read_company_tracking`
- `upsert_company_tracking_entry`
- `read_daily_note`
- `write_daily_note`

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_service.py -v`
Expected: FAIL because the service layer does not exist.

**Step 3: Write minimal implementation**

Wire the note parsers/renderers to real files under the vault root.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_service.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/service.py tests/test_service.py
git commit -m "feat: add local vault service layer"
```

### Task 9: Implement normalized signal ingestion

**Files:**
- Create: `src/job_search_mcp/ingestion.py`
- Create: `tests/test_ingestion.py`

**Step 1: Write the failing test**

Cover:

- classify a manual note into a `CompanySignal`
- resolve company identity
- append signal to company timeline
- update tracker state
- avoid duplicate writes using source markers

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ingestion.py -v`
Expected: FAIL because the ingestion layer does not exist.

**Step 3: Write minimal implementation**

Implement local-only ingestion primitives for manual/company-note inputs first.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ingestion.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/ingestion.py tests/test_ingestion.py
git commit -m "feat: add normalized company signal ingestion"
```

### Task 10: Add a minimal MCP tool surface

**Files:**
- Create: `src/job_search_mcp/server.py`
- Create: `tests/test_server.py`

**Step 1: Write the failing test**

Cover:

- exported operations for note read/write
- exported operations for tracker updates
- exported operations for daily activity append

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_server.py -v`
Expected: FAIL because the server entrypoint does not exist.

**Step 3: Write minimal implementation**

Expose the local vault service operations behind a simple MCP-compatible interface.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_server.py -v`
Expected: PASS

**Step 5: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add src/job_search_mcp/server.py tests/test_server.py
git commit -m "feat: expose initial mcp tool surface"
```

### Task 11: Run the full test suite

**Files:**
- Modify: `README.md` if needed

**Step 1: Run all tests**

Run: `pytest -v`
Expected: PASS

**Step 2: Fix any failures**

Address issues without expanding scope.

**Step 3: Document local usage**

Add concise setup and test instructions if a `README.md` is created.

**Step 4: Commit**

Before committing, ask the user which Git author identity to use for this work.

```bash
git add .
git commit -m "test: verify initial local job search mcp implementation"
```

## Notes

- Do not add Gmail, Calendar, or LinkedIn integrations in v1.
- Do not migrate historical daily notes in the first pass.
- Preserve human-authored freeform note content whenever possible.
