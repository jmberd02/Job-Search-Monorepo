# MCP Tools and Skills Implementation

**Date:** 2026-04-05
**Status:** Approved - Full Implementation

## Overview

Implement missing MCP tools and skills to complete the job-search-mcp functionality, enabling full automation of daily planning, LeetCode tracking, interview prep, and company management workflows.

## Requirements

### Missing MCP Tools (6 tools)

1. **Performance Summary Tools (4 tools)**
   - `read_top_performance_summary()` - Read aggregated assessment report
   - `read_daily_performance_summary(date)` - Read specific date's summary from `Leetcode/DATE/PERFORMANCE SUMMARY.md`
   - `write_daily_performance_summary(date, content)` - Write per-date summary
   - `update_top_performance_summary(data)` - Update aggregated report

2. **Interview Tracking**
   - `get_upcoming_interviews(days)` - Extract interviews from Google Calendar (primary) and Company Tracking (fallback)
   - Returns: List of interview events with company, date, time, stage, people

3. **Company Resolution**
   - `resolve_company_reference(name)` - Match company name variations
   - Strategy: Exact match → company_key (slug) match → ask user if ambiguous
   - Returns: company_key or ambiguity prompt

### Missing Skills (3 skills)

4. **precall-prep** - Generates preparation notes for recruiter/company calls
   - Input: Company name
   - Reads: Company note, Company Tracking entry
   - Output: Questions to ask, talking points, concerns, red flags

5. **interview-review** - Analyzes interview transcripts
   - Input: Transcript text
   - Output: Answer quality analysis, signal strength, gaps, suggested rewrites

6. **leetcode-assess** - Comprehensive LeetCode skill assessment
   - Reads: All files in `Leetcode/` directory
   - Output: Skill ratings (1-10), pattern gaps, interview readiness, quick wins

### Skill Updates (2 skills)

7. **analyze-leetcode** - Update to use new performance summary tools
   - Add calls to `write_daily_performance_summary()`
   - Add calls to `update_top_performance_summary()`

8. **plan-day** - Update to use new tools
   - Replace placeholder `read_top_performance_summary()` with real call
   - Replace placeholder `get_upcoming_interviews()` with real call

## Architecture

### Layer Structure

```
Skills (skills/*.md)
    ↓ invoke
MCP Tools (server.py)
    ↓ delegate
Service Layer (service.py)
    ↓ call
Notes Layer (notes/*.py)
    ↓ read/write
Vault Files (Obsidian)
```

### File Changes

**New Files:**
- `src/job_search_mcp/notes/interviews.py` - Interview extraction logic
- `skills/precall-prep/skill.md` - Precall prep skill
- `skills/interview-review/skill.md` - Interview review skill
- `skills/leetcode-assess/skill.md` - LeetCode assessment skill

**Modified Files:**
- `src/job_search_mcp/server.py` - Add 6 new MCP tool registrations
- `src/job_search_mcp/service.py` - Add new service methods
- `src/job_search_mcp/notes/performance.py` - Support per-date summaries
- `skills/analyze-leetcode/skill.md` - Use new MCP tools
- `skills/plan-day/skill.md` - Use new MCP tools

## Component Designs

### 1. Performance Summary Tools

**Data Structure:**
- Per-date: `Leetcode/YYYY-MM-DD/PERFORMANCE SUMMARY.md`
- Aggregated: `LeetCode Skill Assessment Report.md` (or `Performance Summary.md`)

**read_top_performance_summary()**
- Reads aggregated assessment report
- Returns: PerformanceSummary object with weak_areas, strengths, recommendations

**read_daily_performance_summary(date)**
- Reads `Leetcode/{date}/PERFORMANCE SUMMARY.md`
- Returns: Text content of that day's summary

**write_daily_performance_summary(date, content)**
- Ensures `Leetcode/{date}/` directory exists
- Writes content to `PERFORMANCE SUMMARY.md` in that directory
- Creates new file if doesn't exist

**update_top_performance_summary(data)**
- Reads current aggregated report
- Merges new data (updates weak areas, strengths, adds to history)
- Writes back to aggregated report

### 2. Interview Tracking

**get_upcoming_interviews(days)**

Strategy:
1. Try Google Calendar MCP first
   - Query calendar for next `days` days
   - Filter events with interview-related keywords (interview, call, screen, onsite, technical)
   - Extract: title, date, time, attendees
2. Fallback to Company Tracking
   - Parse "Active Interview Pipeline" section
   - Extract dates from status fields (regex: `\w+ \d+`, `\d{4}-\d{2}-\d{2}`)
   - Match companies with upcoming dates

Returns:
```python
[{
  "company": "Physical Intelligence",
  "date": "2026-04-10",
  "time": "2:00 PM",
  "stage": "Technical Screen",
  "source": "calendar" | "tracking"
}]
```

### 3. Company Resolution

**resolve_company_reference(name)**

Matching strategy (in order):
1. Exact name match in Company Tracking
2. company_key (slug) match: `name.lower().replace(" ", "-")`
3. Check if name is substring of any company name
4. Check if any company name is substring of name
5. If multiple matches or no matches: return list for user to choose

Returns:
```python
{
  "company_key": "physical-intelligence",
  "company_name": "Physical Intelligence",
  "confidence": "exact" | "slug" | "fuzzy" | "ambiguous"
}
```

### 4. New Skills

**precall-prep skill:**
```markdown
Instructions:
1. Use resolve_company_reference(company_name) to get company_key
2. Use read_company_note(company_key) to get details
3. Use read_company_tracking() to get tracking context
4. Generate:
   - 3 questions to ask (based on gaps in knowledge)
   - Talking points (relevant background match)
   - Potential concerns (and how to address)
   - Red flags to watch for
```

**interview-review skill:**
```markdown
Instructions:
1. Parse transcript (provided by user)
2. Analyze:
   - Answer quality (STAR format, clarity, specificity)
   - Signal strength (what landed, what missed)
   - Gaps (underselling, rambling, incomplete)
   - Interviewer signals (what they were probing for)
3. Provide 2-3 stronger answer rewrites
4. Optionally log to vault using append_daily_activity()
```

**leetcode-assess skill:**
```markdown
Instructions:
1. Use glob to find all files in Leetcode/ directory
2. Read performance summaries and problem files
3. Analyze:
   - Problems attempted (list with status, time, approach)
   - Skill ratings 1-10 (arrays, strings, HashMap, trees, etc.)
   - Pattern gaps (which patterns not recognizing)
   - Interview readiness (days/weeks to passable/strong)
4. Generate top 3 quick wins
5. Optionally update_top_performance_summary() with findings
```

## Error Handling

- Missing vault files: Return None or empty structures, don't error
- Google Calendar unavailable: Gracefully fall back to Company Tracking
- Ambiguous company names: Return options list, ask user to clarify
- Invalid dates: Validate date format, return clear error message
- Missing directories: Create them (e.g., `Leetcode/DATE/`)

## Testing Strategy

- **Unit tests:** Each new service method
- **Integration tests:** MCP tools with test vault
- **End-to-end tests:** Skills with real vault data
- **Manual testing:** Run each skill via Claude Code

## Success Criteria

1. All 8 tasks from gap analysis completed
2. `plan-day` skill uses real performance summary and interview data
3. `analyze-leetcode` skill logs to per-date summaries and updates aggregated
4. New skills (`precall-prep`, `interview-review`, `leetcode-assess`) functional
5. All tests passing
6. User can test end-to-end workflows

## Implementation Order

1. Performance summary tools (MCP + service + notes layer)
2. Interview extraction (MCP + service + new interviews module)
3. Company resolution (MCP + service, uses existing tracker code)
4. Update existing skills (analyze-leetcode, plan-day)
5. Create new skills (precall-prep, interview-review, leetcode-assess)
6. Testing and validation

## Notes

- Google Calendar MCP already available (confirmed in system)
- Performance summary infrastructure already exists, just needs per-date support
- Company Tracking parsing already works, just needs interview date extraction
- Skills follow existing patterns from analyze-leetcode, track-company, plan-day
