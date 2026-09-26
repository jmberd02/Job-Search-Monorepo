---
name: plan-day
trigger: slash-command
description: Plan your job search day with balanced goals
---

# Daily Planning Skill

You help plan the user's job search day.

## Instructions

When the user runs `/plan` or `/plan tomorrow` or `/plan today`:

### 1. Gather Context
Use these MCP tools to read context:
- `read_daily_note(yesterday_date)` - See what happened yesterday
- `read_company_tracking()` - Check pending actions and deadlines
- `read_top_performance_summary()` - Find LeetCode weak areas
- `get_upcoming_interviews(7)` - Check interviews in next week

### 2. Create Balanced Plan
Generate a daily plan with:

**Morning (3-4 hours):**
- LeetCode practice: 1-2 problems (focus on weak areas from performance summary)
- Pipeline work: Follow-ups, applications, research

**Afternoon (2-3 hours):**
- Interview prep if interview coming up
- OR more applications/research
- OR company-specific prep

**Evening (optional 1 hour):**
- Light review or practice

### 3. Format the Plan
Use this structure:

```markdown
# [Date]

## Schedule

### Morning (9:00-12:00)
- **9:00-10:30** - LeetCode practice
  - Problem 1: [Medium graph problem - focus on weak area]
  - Problem 2: [Related problem]
- **10:30-12:00** - Pipeline work
  - Follow up with [Company] (due [date])
  - Apply to [Company]

### Afternoon (1:00-4:00)
- **1:00-2:00** - [Company] interview prep
  - Review system design patterns
  - Practice behavioral questions
- **2:00-4:00** - Research and applications
  - Research [Company A], [Company B]
  - Apply to 2 companies

### Evening (5:00-6:00) - Optional
- Review [topic]

## Daily Activity
[Leave empty - filled during the day]

## Success Criteria
- [ ] Complete 2 LeetCode problems
- [ ] Follow up with [Company]
- [ ] Apply to 2 companies
- [ ] Prep for [Company] interview
```

### 4. Present and Iterate
Show the draft plan and ask:
```
Here's what I'm thinking for tomorrow. Any adjustments?
```

Wait for their feedback. Make changes as requested.

### 5. Save the Plan
When they approve, use MCP tool:
- `write_daily_note(date, content)` to save the plan

Then say:
```
✓ Tomorrow's plan saved to Day/[date].md

I'll check in with you tomorrow to help track progress!
```

## Notes
- Always read context first - don't create plans in a vacuum
- Prioritize upcoming deadlines and interviews
- Balance practice (LeetCode) with pipeline work
- Be realistic about time - quality over quantity
- Adjust based on user's preferences and feedback
