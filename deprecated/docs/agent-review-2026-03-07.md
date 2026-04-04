# Code Review: Agent Layer

**Date:** 2026-03-07  
**Reviewer:** kiro-sonnet  
**Scope:** job_search_agent module

## Issues Found

### 1. **Hardcoded Time Values**
**Location:** `skills.py:90-95`

```python
daily = append_daily_activity(
    daily,
    start_time=time(9, 0),
    end_time=time(11, 0),  # Hardcoded times
    description=f"LeetCode: {problem}",
    status=status,
    note=notes,
)
```

**Issue:** Hardcoded 9-11 AM time range doesn't reflect actual activity time

**Impact:** Medium - inaccurate activity logging

**Recommendation:** Accept time parameters or use current time

---

### 2. **Incomplete Message Parsing**
**Location:** `agent.py:18-56`

**Issue:** 
- Simple string matching for commands
- No entity extraction
- Comment says "OpenClaw would extract entities" but doesn't
- Returns placeholder strings instead of calling skills

**Impact:** High - agent doesn't actually work

**Recommendation:** Either implement proper parsing or document this is a stub

---

### 3. **Unused Imports**
**Location:** `agent.py:3`

```python
from datetime import date
```

Used inline with `__import__("datetime")` instead - inconsistent

**Impact:** Low - code smell

---

### 4. **No Error Handling**
**Location:** Both files

**Issue:** No try/except blocks, no validation, no error messages

**Impact:** Medium - will crash on invalid input

---

### 5. **Hardcoded Plan Template**
**Location:** `skills.py:23-32`

```python
plan_lines.extend([
    "- 9:00 AM - 11:00 AM: LeetCode practice",
    "- 2:00 PM - 4:00 PM: Job search activities",
    "", "## Daily Activity", "", "## Schedule vs Activity",
])
```

**Issue:** 
- Ignores profile scheduling preferences
- Ignores tracker pending items
- Ignores performance summary
- Doesn't use yesterday's note
- Doesn't check calendar

**Impact:** High - plan generation doesn't work as designed

---

### 6. **Missing Context Usage**
**Location:** `skills.py:18-22`

```python
yesterday_note = self.service.read_daily_note(yesterday)
tracker = self.service.read_company_tracking()
profile = self.service.read_candidate_profile()
perf = self.service.read_performance_summary()
```

**Issue:** Reads all context but doesn't use any of it

**Impact:** High - wasted I/O, misleading code

---

### 7. **Weak Recommendation Logic**
**Location:** `skills.py:102-106`

```python
def get_recommendation(self) -> str:
    perf = self.service.read_performance_summary()
    if perf and perf.weak_areas:
        return f"Focus on: {perf.weak_areas}"
    return "Practice dynamic programming and system design"
```

**Issue:** 
- Just returns raw weak_areas text
- Fallback is hardcoded generic advice
- Doesn't consider upcoming interviews
- Doesn't check tracker for company context

**Impact:** Medium - recommendations not useful

---

### 8. **No Service Caching Benefit**
**Location:** `skills.py`

**Issue:** Each skill method calls `self.service.read_*()` independently, doesn't benefit from service-level caching across skill calls

**Impact:** Low - but could optimize

---

### 9. **Inconsistent Return Types**
**Location:** `skills.py`

**Issue:** 
- Some methods return strings
- `list_pending_followups` returns list[dict]
- No consistent response format

**Impact:** Low - but makes integration harder

---

### 10. **Missing Skills from Architecture**
**Location:** Both files

**Issue:** Architecture doc mentions these skills but they're not implemented:
- `analyze_transcript`
- `leetcode_help` (active help)
- `schedule_reminder`
- Polling/ingestion flows

**Impact:** High - incomplete implementation

---

## Summary

**Critical:** 2 (incomplete message parsing, plan generation doesn't work)  
**High Priority:** 3 (missing skills, no error handling, unused context)  
**Medium Priority:** 3 (hardcoded times, weak recommendations, inaccurate logging)  
**Low Priority:** 2 (unused imports, inconsistent returns)

## Assessment

The agent layer is a **stub/prototype** that doesn't implement the architecture as designed. It:
- ✅ Has correct structure (service + skills separation)
- ✅ Uses MCP layer correctly
- ❌ Doesn't implement actual skill logic
- ❌ Doesn't parse messages properly
- ❌ Doesn't use gathered context
- ❌ Missing most skills from architecture

## Recommendation

**Option 1:** Document this as a stub/example and mark as TODO  
**Option 2:** Implement the skills properly per architecture  
**Option 3:** Remove agent layer until ready to implement

The MCP layer is production-ready. The agent layer is not.
