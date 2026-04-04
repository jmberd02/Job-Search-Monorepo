# Deprecated Code

This directory contains code that has been deprecated but preserved for future reference.

## Contents

- `src/job_search_agent/` - OpenClaw agent integration layer
- `tests/test_agent.py` - Tests for the agent layer
- `docs/agent-review-2026-03-07.md` - Original code review
- `demo_optimization.py` - Performance optimization demo script

---

## `job_search_agent` - OpenClaw Integration Layer

**Status:** Deprecated (April 2026)
**Original Purpose:** Message handler for OpenClaw integration
**Why Deprecated:** Project pivoted to Claude Code skills architecture

### What It Was

The `job_search_agent` module provided:

1. **`JobSearchAgent`** - Message handler that parsed natural language commands
   - Simple keyword matching ("plan tomorrow", "just did Two Sum", etc.)
   - Designed for OpenClaw chat interface
   - Never fully implemented (see code review)

2. **`JobSearchSkills`** - Business logic wrapper around MCP service
   - Plan generation
   - Signal ingestion
   - LeetCode tracking
   - Recommendation engine
   - Interview analysis
   - Reminder scheduling

### Why It Was Deprecated

The project architecture shifted to **Claude Code skills** instead:

✅ **Claude Code skills are better because:**
- More conversational and flexible
- Leverage Claude's natural language understanding directly
- No need for keyword matching or entity extraction
- Easier to maintain and extend
- Work seamlessly with MCP tools

❌ **The agent layer had issues:**
- Only a stub/prototype (per code review)
- Hardcoded values and incomplete parsing
- Redundant with Claude's conversational abilities
- Added unnecessary abstraction layer

### Useful Ideas Worth Salvaging

Several features in `JobSearchSkills` **are not yet implemented** in the current Claude Code skills and could be valuable:

#### 1. **End of Day Processing**
**Code:** `skills.py:141-161` - `end_of_day()`

```python
def end_of_day(self, target_date: Optional[date] = None) -> str:
    """Run end-of-day processing."""
    # Refreshes schedule vs activity comparison
    # Checks tracker for pending items
    # Provides summary: "X items pending" or "All caught up!"
```

**Value:** Daily review ritual and accountability tracking

**How to implement:**
- Create `/eod` Claude Code skill
- Call `refresh_schedule_vs_activity()` on today's daily note
- Read company tracking to list pending follow-ups
- Generate end-of-day summary

---

#### 2. **Interview Transcript Analysis**
**Code:** `skills.py:172-202` - `analyze_transcript()`

```python
def analyze_transcript(
    self,
    company_key: str,
    transcript: str,
    interview_type: str = "technical",
) -> str:
    """Analyze interview transcript and update notes."""
    # Extracts questions from transcript (looks for "?")
    # Updates company note with interview details
    # Tracks: date, type, questions asked, transcript length
```

**Value:** Post-interview tracking and pattern recognition

**How to implement:**
- Create `/analyze-interview` Claude Code skill
- Parse transcript for questions and key points
- Use signal ingestion to update company note
- Track interview history for pattern analysis

---

#### 3. **LeetCode Active Help**
**Code:** `skills.py:204-223` - `leetcode_help()`

```python
def leetcode_help(
    self,
    problem: str,
    current_approach: Optional[str] = None,
) -> str:
    """Get help with a LeetCode problem based on weak areas."""
    # Reads performance summary for weak areas
    # Provides contextual hints based on problem and approach
    # Different from post-analysis - helps DURING problem
```

**Value:** Real-time assistance when stuck

**Difference from current `/analyze-leetcode`:**
- Current skill: Post-practice analysis and tracking
- This feature: Active help while solving

**How to implement:**
- Enhance `/analyze-leetcode` skill with a "help mode"
- Or create separate `/leetcode-hint` skill
- Read performance summary to tailor hints
- Provide scaffolded help without giving away solution

---

#### 4. **Schedule Reminders**
**Code:** `skills.py:225-246` - `schedule_reminder()`

```python
def schedule_reminder(
    self,
    company_key: str,
    action: str,
    due_date: date,
) -> str:
    """Schedule a follow-up reminder for a company."""
    # Updates company note with next_action and due date
    # Uses signal ingestion system
    # Appears in daily plans automatically
```

**Value:** Proactive follow-up tracking

**How to implement:**
- Enhance `/track-company` skill
- Add "set reminder for [Company] to [action] by [date]" flow
- Use signal ingestion with `next_action` and `due_date` fields
- Reminders auto-populate in daily plans via `generate_plan()`

---

#### 5. **Smart Practice Recommendations**
**Code:** `skills.py:118-139` - `get_recommendation()`

```python
def get_recommendation(self) -> str:
    """Get practice recommendation based on performance."""
    # Checks company tracking for upcoming interviews
    # If interviews coming up: focus on weak areas for those
    # Otherwise: general practice recommendations
    # Prioritizes based on interview timeline
```

**Value:** Interview-aware practice planning

**Current gap:**
- `/analyze-leetcode` does post-practice analysis
- `/plan-day` creates daily plans
- Neither suggests "what to practice next" based on interview schedule

**How to implement:**
- Add "What should I practice?" flow to `/analyze-leetcode`
- Check `get_upcoming_interviews(7)` for imminent interviews
- Combine with performance summary weak areas
- Prioritize practice based on interview timeline

---

### Implementation Priority

If adding these features, suggested order:

1. **Schedule Reminders** (Low effort, high value)
   - Just enhance `/track-company` skill
   - Infrastructure already exists in signal ingestion

2. **End of Day Processing** (Low effort, medium value)
   - Simple new skill
   - Calls existing MCP functions

3. **Smart Practice Recommendations** (Medium effort, high value)
   - Enhance existing `/analyze-leetcode` skill
   - Combines existing data in new way

4. **LeetCode Active Help** (Medium effort, medium value)
   - New interaction mode
   - Requires careful design to avoid spoiling solutions

5. **Interview Transcript Analysis** (Higher effort, medium value)
   - New skill and workflow
   - Valuable but less frequently used

---

### Architecture Differences

**Old (Deprecated) Architecture:**
```
User Message → JobSearchAgent.handle_message()
             → Keyword matching
             → JobSearchSkills.method()
             → JobSearchService (MCP)
             → Vault
```

**Current Architecture:**
```
User Message → Claude Code Skill
             → Claude's natural understanding
             → MCP Tools (directly)
             → JobSearchService
             → Vault
```

**Why current is better:**
- Claude handles natural language (no keyword matching needed)
- Direct MCP tool calls (no wrapper layer)
- More flexible conversations
- Easier to extend and maintain

---

### Files in This Directory

```
deprecated/
├── README.md (this file)
├── demo_optimization.py     # Performance demo (see below)
├── src/
│   └── job_search_agent/
│       ├── __init__.py
│       ├── agent.py         # Message handler (stub)
│       └── skills.py        # Business logic wrapper
├── tests/
│   └── test_agent.py        # Comprehensive tests for both classes
└── docs/
    └── agent-review-2026-03-07.md  # Original code review
```

### Code Review Summary

The March 2026 code review identified **10 issues** including:

**Critical (2):**
- Incomplete message parsing (doesn't actually work)
- Plan generation doesn't use gathered context

**High Priority (3):**
- Missing skills from architecture
- No error handling
- Reads context but doesn't use it

See `docs/agent-review-2026-03-07.md` for full details.

---

## How to Use This Code

**Don't use it directly** - it's a stub/prototype and has known issues.

**Do reference it for:**
- Feature ideas (see "Useful Ideas Worth Salvaging" above)
- Understanding original architecture intent
- Examples of wrapping MCP service with business logic
- Test patterns for conversation flows

If you want to implement any of the features above, use the **current Claude Code skills architecture** instead of resurrecting this code.

---

## `demo_optimization.py` - Performance Demo

**Status:** Deprecated (April 2026)
**Original Purpose:** Demonstrate application lookup optimization
**Why Deprecated:** Served its purpose, not needed for runtime

### What It Was

A standalone demo script (67 lines) that demonstrates the performance improvement from adding an application index to the Company Tracking note.

**Commit:** `7c8cdb2` (March 7, 2026)
**Feature:** Optimized application lookup from O(n × file_size) to O(1)

### What It Demonstrates

```python
# Before: Read all application files and search each one
for app_file in vault.glob("Applications/*.md"):
    content = app_file.read_text()
    if key in content:  # Slow!
        return parse(content)

# After: Direct lookup from index
path = tracker.applications[key]  # O(1)
return read_and_parse(path)
```

### The Demo Flow

1. Creates a temporary vault
2. Writes an application note
3. Shows the application index in Company Tracking note
4. Reads the application back using the index
5. Prints performance comparison

### Output Example

```
=== Application Lookup Optimization Demo ===

1. Creating application note...
   ✓ Application note created

2. Checking Company Tracking note...
   Applications in index: 1
   ✓ Index entry: acme-corp-senior-engineer -> Applications/Acme Corp/Senior Engineer.md

3. Reading application via index...
   ✓ Found: Acme Corp - Senior Engineer
   Status: applied

=== Performance Benefit ===
Before: O(n × file_size) - scan all application files
After:  O(1) - direct path lookup from index

With 100 applications:
  Before: Read 100 files, search each for matching key
  After:  Read 1 file directly from index
```

### Why Deprecated

- ✅ Feature was successfully implemented and tested
- ✅ Demo served its purpose during development
- ❌ Not referenced in documentation or README
- ❌ Not needed for runtime operation
- ❌ Adds clutter to project root

The optimization itself is **still active** in the codebase:
- `src/job_search_mcp/notes/tracker.py` - Index parsing/rendering
- `src/job_search_mcp/service.py` - Index-based lookup with fallback
- `tests/test_service.py` - Comprehensive tests for the feature

### How to Use This Code

**To run the demo:**
```bash
python deprecated/demo_optimization.py
```

**To understand the optimization:**
See the actual implementation in:
- `src/job_search_mcp/notes/tracker.py:22-44` - Index management
- `src/job_search_mcp/service.py:167-185` - Index-based lookup
- `tests/test_service.py:267-299` - Tests

---

**Deprecated:** April 4, 2026
**Reason:** Architecture pivot to Claude Code skills
**Replacement:** Claude Code skills in `/skills/` directory
