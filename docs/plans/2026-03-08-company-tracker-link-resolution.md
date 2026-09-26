# Company Tracker Link Resolution Implementation Plan
 

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

Ask what identity to use before implementing

**Goal:** Make `read_company_note(company_key)` resolve company note files through the `Company Note` field in `Company Tracking.md` instead of scanning every file in `Companies/`.

**Architecture:** Treat `Company Tracking.md` as the canonical machine index for company note lookup. Parse the `- **Company Note:** [[Companies/<Company>]]` field into structured tracker data, then use that structured link in the service layer to open a single file directly. Preserve a strict tracker-first read path and ensure tracker writes continue to include the company note link so the index remains authoritative.

**Tech Stack:** Python, pytest, markdown parsing via existing tracker parser, pathlib-based filesystem access

---

### Task 1: Add parser tests for structured company-note link extraction

**Files:**
- Modify: `tests/notes/test_tracker_note.py`

**Step 1: Write the failing test**

Add a test that parses a tracker entry like:

```markdown
### Acme Corp
- **Status:** active
- **Company Note:** [[Companies/Acme Corp]]
```

Assert that:
- `tracker.companies["acme-corp"]["notes"] == "[[Companies/Acme Corp]]"`
- `tracker.companies["acme-corp"]["company_note_link"] == "Companies/Acme Corp"`
- `tracker.companies["acme-corp"]["company_note_path"] == "Companies/Acme Corp.md"`

Add a second test for an aliased wiki link:

```markdown
- **Company Note:** [[Companies/Acme Corp|Acme]]
```

Assert the same `company_note_link` and `company_note_path` values.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/notes/test_tracker_note.py -k company_note -v
```

Expected: FAIL because the parsed tracker dict does not yet expose structured link fields.

**Step 3: Write minimal implementation**

Update the tracker parser to extract the first Obsidian wiki link from the `Company Note` field and store:
- the raw link target without alias as `company_note_link`
- the normalized markdown filename path as `company_note_path`

Implementation notes:
- Keep `company_note` as the original raw string for round-tripping.
- Support both `[[Companies/Acme Corp]]` and `[[Companies/Acme Corp|Acme]]`.
- Append `.md` when building `company_note_path` if the target lacks it.
- Do not parse arbitrary free text beyond extracting the first wiki link.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/notes/test_tracker_note.py -k company_note -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/notes/test_tracker_note.py src/job_search_mcp/notes/tracker.py
git commit -m "fix: parse company note links from tracker notes" \
  -m "Extract structured company note targets from Company Tracking.md notes fields." \
  -m "This makes the tracker usable as the canonical machine index instead of treating note links as opaque text."
```

### Task 2: Add service tests for tracker-first company-note resolution

**Files:**
- Modify: `tests/test_service.py`

**Step 1: Write the failing test**

Add a test that creates:
- `Company Tracking.md` with an `Acme Corp` entry containing `- **Company Note:** [[Companies/Acme Corp]]`
- `Companies/Acme Corp.md` with frontmatter containing `company_key: acme-corp`
- an extra unrelated company note to prove no directory scan is needed conceptually

Call:

```python
record = service.read_company_note("acme-corp")
```

Assert:
- `record is not None`
- `record.company == "Acme Corp"`
- `record.company_key == "acme-corp"`

Add another test where the tracker entry exists but has no `Company Note` field and assert `read_company_note("acme-corp") is None`.

Add another test where the tracker note link points to a missing company file and assert `read_company_note("acme-corp") is None`.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_service.py -k read_company_note -v
```

Expected: FAIL because the service still scans `Companies/*.md` and ignores tracker links.

**Step 3: Write minimal implementation**

Update `JobSearchService.read_company_note()` to:
1. read tracker data first
2. look up the `company_key` in `tracker.companies`
3. read `company_note_path` from the tracker entry
4. open exactly that file relative to the vault root
5. parse and return the company note record
6. return `None` if the tracker entry is missing, has no resolvable note path, or points to a missing file

Implementation notes:
- Do not keep the old full-directory content scan as silent fallback unless the user explicitly asks for a compatibility fallback.
- Keep path resolution strict to the vault root.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_service.py -k read_company_note -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_service.py src/job_search_mcp/service.py
git commit -m "fix: resolve company notes through tracker links" \
  -m "Change company note reads to resolve through Company Tracking.md before opening a company file." \
  -m "This removes the full Companies/ scan and aligns reads with the tracker-first design in the spec."
```

### Task 3: Ensure tracker writes preserve the authoritative company-note link

**Files:**
- Modify: `tests/notes/test_tracker_note.py`
- Modify: `tests/test_service.py`
- Modify: `src/job_search_mcp/notes/tracker.py`
- Modify: `src/job_search_mcp/service.py`
- Check for impact: `src/job_search_mcp/ingestion.py`

**Step 1: Write the failing test**

Add a tracker upsert/render test asserting that when a company entry is created or updated without an explicit `notes` value, the rendered tracker still contains:

```markdown
- **Notes:** [[Companies/Acme Corp]]
```

If service-level coverage is clearer, add a test around `service.upsert_company_tracking_entry(...)` that verifies the written `Company Tracking.md` contains the company note link for the same company.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/notes/test_tracker_note.py tests/test_service.py -k "tracking and Notes" -v
```

Expected: FAIL if upserted tracker entries omit the note link or overwrite it with an empty string.

**Step 3: Write minimal implementation**

Adjust tracker entry creation/update so the company note link remains authoritative:
- when `company_note` is explicitly provided, preserve it
- when `company_note` is omitted or empty, default it to `[[Companies/{company_name}]]`

Implementation notes:
- This keeps `Company Tracking.md` usable as the canonical index after ingestion updates.
- If needed, make the defaulting logic live in `upsert_company_tracking_entry()` so all callers benefit.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/notes/test_tracker_note.py tests/test_service.py -k "tracking or read_company_note" -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/notes/test_tracker_note.py tests/test_service.py src/job_search_mcp/notes/tracker.py src/job_search_mcp/service.py src/job_search_mcp/ingestion.py
git commit -m "fix: keep tracker note links authoritative" \
  -m "Preserve or default the company note link when tracker entries are created or updated." \
  -m "This prevents ingestion and tracker writes from eroding the canonical lookup path over time."
```

### Task 4: Run focused regression coverage

**Files:**
- No code changes expected

**Step 1: Run tracker and service tests**

Run:

```bash
pytest tests/notes/test_tracker_note.py tests/test_service.py -v
```

Expected: PASS

**Step 2: Run adjacent ingestion and server tests**

Run:

```bash
pytest tests/test_ingestion.py tests/test_server.py -v
```

Expected: PASS

**Step 3: Investigate any failures before proceeding**

If failures appear:
- verify whether they assume tracker entries can exist without note links
- update tests only if the behavior change is intentional and aligned with the new tracker-first contract
- otherwise fix the implementation

**Step 4: Commit verification-only changes if needed**

```bash
git add -A
git commit -m "test: align tracker-first company note resolution coverage" \
  -m "Update regression coverage around tracker parsing and tracker-based company note reads." \
  -m "This documents the intended contract so future changes do not reintroduce file scanning or missing links."
```

### Task 5: Optional cleanup if the implementation introduces helper functions

**Files:**
- Modify: `src/job_search_mcp/notes/tracker.py`
- Modify: `src/job_search_mcp/service.py`

**Step 1: Refactor only after green**

If parsing or path resolution logic became noisy, extract helpers such as:
- `_extract_first_wikilink(value: str) -> str | None`
- `_company_note_path_from_tracker_entry(entry: dict) -> Path | None`

**Step 2: Re-run focused tests**

Run:

```bash
pytest tests/notes/test_tracker_note.py tests/test_service.py tests/test_ingestion.py tests/test_server.py -v
```

Expected: PASS

**Step 3: Commit**

```bash
git add src/job_search_mcp/notes/tracker.py src/job_search_mcp/service.py
git commit -m "refactor: simplify tracker-based company note resolution" \
  -m "Extract small helpers around wiki-link parsing and tracker path resolution after behavior is green." \
  -m "This keeps the tracker-first lookup path readable without changing the new contract."
```

## Notes For The Implementing Agent

- The spec in `job-search-agent-summary.md` says `Company Tracking.md` is the canonical search index and read path.
- The canonical tracker field for this change is `Company Note`, not `Notes`.
- Avoid adding a broad fallback scan unless the human explicitly asks for backward compatibility. The point of this change is to make tracker data authoritative.
- Keep the change narrow. Do not redesign the tracker schema beyond parsing and preserving the existing note link.
