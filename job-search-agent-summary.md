# Job Search Agent — Conversation Summary + Spec

## What We're Building

A personal job search automation system for Jacob Berdichevsky, a backend engineer actively job searching in SF targeting robotics/AI companies at $200k+. The system automates daily planning, pipeline tracking, recruiter email processing, interview transcript analysis, and LeetCode performance tracking. Everything is grounded in an Obsidian vault as the single source of truth.

---

## Key Architecture Decisions

### Why not pure OpenClaw
Context bloat. Pasting emails and transcripts into chat creates permanent user/assistant messages that never get pruned and accumulate across the day. OpenClaw is good at lightweight synthesis, bad at content-heavy ingestion.

### Why not LangGraph
Overkill for current workflows. Every interaction is linear — read data, call LLM, write result. No branching, no loops, no multi-agent coordination needed. LangGraph adds architecture without adding value. Revisit if complexity grows.

### Why MCP + OpenClaw
MCP servers are the dumb data layer (read/write only, no LLM calls). OpenClaw's built-in agent loop handles linear orchestration for free. Skills define the LLM behavior. Clean separation, nothing reinvented.

### Why Discord channels for isolation
Each Discord channel = isolated OpenClaw session. Sessions reset at 4AM. Context never grows beyond a single day's lightweight conversation. Cross-day continuity lives in Obsidian, not chat history.

### Why git via Obsidian Git plugin
Handles backup and atomic writes automatically on file save. Pushes to private GitHub repo. Full history of every change. No extra infrastructure needed — just a plugin.

---

## Architecture

```
You → Discord → OpenClaw (agent loop + skills) → MCP tools → Obsidian / Gmail / Calendar
```

### Principles
- MCP servers are dumb — read/write data and APIs only, no LLM calls
- All LLM intelligence lives in OpenClaw skills
- Obsidian is the single source of truth across all interactions
- Discord channels are isolated sessions — no context bleed between concerns
- Context never accumulates across days — OpenClaw resets at 4AM, continuity lives in Obsidian
- Git via Obsidian Git plugin handles backup and atomic writes automatically

### Stack
- **OpenClaw** — agent loop, skills, proactive reminders, runs on VM/server with GUI
- **MCP servers** — data layer (Obsidian, Gmail, Google Calendar)
- **Discord** — trigger interface, three isolated channels
- **Obsidian** — persistent storage, markdown files, git-backed
- **Obsidian Git plugin** — auto-commits on save, pushes to private GitHub repo

---

## Obsidian Vault Structure

```
vault/
  daily/
    2026-03-07.md         ← daily schedule files (planned + actual)
    2026-03-08.md
    ...
  Company_Tracking.md     ← full pipeline tracker
  PERFORMANCE_SUMMARY.md  ← LC performance + interview coaching notes
  learning_roadmap.md     ← skills gap analysis and learning priorities
```

### Daily Note Format
Follows Jacob's existing `Daily_Schedule_Prompt.md` exactly:
1. Calendar Events
2. Yesterday's Progress (✅ ❌ 📝)
3. Schedule (time-blocked, checkboxes)
4. Pending Follow-Ups
5. Success Criteria
6. Interview Prep Section (if applicable)
7. **Actual vs Planned** (new — appended throughout day via pings)

---

## MCP Servers

### job-search-mcp
Core data layer. Reads and writes Obsidian vault files directly.

```
read_daily_note(date)                      → returns markdown string
write_daily_note(date, content)            → writes to vault/daily/YYYY-MM-DD.md
read_company_tracking()                    → returns Company_Tracking.md
update_company(company, data)              → updates specific company entry
read_performance_summary()                 → returns PERFORMANCE_SUMMARY.md
update_performance(data)                   → appends/updates performance log
read_learning_roadmap()                    → returns learning_roadmap.md
list_pending_followups()                   → parses Company_Tracking.md, returns overdue items
log_actual(date, block, status, notes)     → appends actual vs planned entry to daily note
generate_actual_summary(date)              → diffs planned vs actual, writes summary section
```

### calendar-mcp
Google Calendar integration.

```
get_events(date)                           → returns events for a given day
get_events_range(start, end)               → returns events across date range
create_event(title, date, time, notes)     → creates calendar event
```

### email-mcp
Conditional — only processes emails explicitly forwarded to recruiting alias.

```
fetch_recruiting_label()                   → fetches unread from Gmail +recruiting label
mark_processed(email_id)                   → marks email so it isn't reprocessed
```

**Trigger pattern:** Jacob forwards recruiting emails to `jacob+recruiting@gmail.com`. Gmail auto-labels them "recruiting". MCP watches that label. Nothing enters the pipeline unless explicitly forwarded.

---

## Discord Channels

```
#daily-plan     → planning, schedule reminders, actual vs planned tracking
#job-search     → email processing, transcript analysis, pipeline queries
#leetcode       → problem debriefs, performance analysis, recommendations
```

Each channel = isolated OpenClaw session. All reset at 4AM independently.

---

## OpenClaw Skills

All LLM calls live here. Skills call MCP tools to fetch data, run the LLM, write results back via MCP. OpenClaw's built-in agent loop handles the linear orchestration.

### generate_plan(date)
Triggered by: "plan tomorrow" in #daily-plan

```
1. read_daily_note(yesterday)      → extract ✅ ❌ items
2. get_events(tomorrow)            → calendar blocks
3. get_events(day_after)           → preview
4. read_company_tracking()         → pending follow-ups, deadlines
5. read_performance_summary()      → weak areas, upcoming interviews
6. read_learning_roadmap()         → current priorities
7. Assemble context
8. Run LLM with Daily_Schedule_Prompt.md template
9. Present to Jacob for conversational iteration
10. write_daily_note(tomorrow, approved_content)
```

### process_email()
Triggered by: "process recruiting emails" in #job-search

```
1. fetch_recruiting_label()        → get unread recruiting emails
2. LLM extracts: company, recruiter, role, stage, sentiment, next action
3. read_company_tracking()         → check if company exists
4. update_company(company, data)   → create or update entry
5. mark_processed(email_id)
6. Return summary to Discord
```

### analyze_transcript(company, transcript)
Triggered by: "here's my transcript with [company]" in #job-search

```
1. LLM analyzes: key topics, red flags, green flags, next steps, fit signals
2. read_company_tracking()         → find company entry
3. update_company(company, data)   → append interview notes
4. Return structured summary to Discord
```

### analyze_leetcode(problem, notes, solution)
Triggered by: "just did [problem]" in #leetcode

```
1. read_performance_summary()      → load existing performance data
2. LLM analyzes: approach, time, mistakes, pattern category
3. update_performance(data)        → append new entry
4. Return analysis + pattern summary
```

### get_recommendation(context)
Triggered by: "what should I practice" or "I have [company] interview Friday" in #leetcode

```
1. read_performance_summary()      → weak areas, recent problems
2. read_company_tracking()         → upcoming interviews, company signals
3. LLM generates tailored recommendation
4. Return recommendation with rationale
```

### end_of_day()
Triggered explicitly by Jacob, ~end of day in #daily-plan

```
1. read_daily_note(today)          → load planned schedule
2. Review logged actual entries    → from ping responses throughout day
3. generate_actual_summary(today)  → diff planned vs actual, write to daily note
4. fetch_recruiting_label()        → sweep for anything that came in today
5. Prompt Jacob: "Found: [list]. Anything else from LinkedIn?"
6. Jacob fills gaps conversationally
7. update_company() for any new items
```

### schedule_reminder (cron)
Runs throughout the day in #daily-plan

```
1. read_daily_note(today)          → parse time blocks
2. Ping Jacob at each block start
3. Capture Jacob's response
4. log_actual(today, block, status, notes)
```

---

## Interaction Flows

### End of Day Planning
```
You (evening): "plan tomorrow"
OpenClaw: assembles context from Obsidian + Calendar
          generates schedule using Daily_Schedule_Prompt.md
          presents to you
You: "move LC block to morning"
OpenClaw: updates, re-presents
You: "looks good"
OpenClaw: write_daily_note(tomorrow, final_content)
--- 4AM reset, clean slate ---
Next day: generate_plan reads yesterday's note fresh from Obsidian
```

### Recruiter Email Processing
```
You (phone): forward email to jacob+recruiting@gmail.com
             Gmail auto-labels "recruiting"

Later in #job-search:
You: "process recruiting emails"
OpenClaw: fetches unread from label
          processes each, updates Company_Tracking.md
          "3 emails processed: Beacon AI follow-up, Pave Robotics inbound,
           T Robotics wants to schedule"
```

### Schedule Reminders + Actual Tracking
```
OpenClaw (9:00AM): "Morning block starting. Ready?"
You: "yep"
OpenClaw: logs start

OpenClaw (10:30AM): "LC practice block"
You: "still finishing write-up, 20 more min"
OpenClaw: logs delay

OpenClaw (11:00AM): "LC practice — ready now?"
You: "yes"
OpenClaw: logs actual start
```

### End of Day Debrief
```
You: "end of day"
OpenClaw: generates actual vs planned diff, appends to today's note
          sweeps recruiting label
          "Found: Beacon AI reply, Pave Robotics inbound.
           Anything else from LinkedIn?"
You: "yeah Grit Robotics reached out"
OpenClaw: update_company(Grit Robotics, ...)
```

### LeetCode Debrief
```
You (#leetcode): "just did two sum, knew it was hash map but blanked on impl"
OpenClaw: analyzes, updates PERFORMANCE_SUMMARY.md
          "Pattern: recognizing hash map problems correctly but struggling
           with implementation under pressure. 4th time this pattern."
```

### On-the-fly LC Recommendation
```
You (#leetcode): "what should I practice, I have Beacon AI round 2 Friday"
OpenClaw: reads weak areas + Beacon AI context
          "Beacon AI is sensor fusion / C++ live coding.
           Weak areas: tree traversal, hash map impl under pressure.
           Recommend: sliding window today, C++ Kalman filter tomorrow."
```

---

## Actual vs Planned Feedback Loop

Throughout the day OpenClaw pings Jacob at each scheduled block and captures his response. At end of day `end_of_day()` generates a diff:

```
Planned vs Actual — 2026-03-07:
  Distributed systems write-up: planned 9:00-10:30 → actual 9:00-11:00 (ran 30min over)
  LC practice:                  planned 10:30-11:30 → actual 11:00-12:00
  Outreach block:               planned 2:00-2:30   → skipped ❌
  Beacon AI prep:               planned 3:00-4:00   → actual 3:00-3:45 ✅
```

Over time this feeds back into `generate_plan()` — the system learns real work patterns and adjusts scheduling automatically.

---

## Context Management

### Why context stays small
- MCP tool results get pruned after cache TTL (default 5min for Anthropic)
- User/assistant messages are lightweight back-and-forth, not raw content
- Sessions reset at 4AM — each day starts clean
- Heavy content is processed inside skills and written to Obsidian, never accumulated in chat

### Cross-day continuity
Lives in Obsidian, not chat history. `generate_plan()` reads yesterday's note fresh from disk every time. The 4AM reset doesn't lose anything important.

---

## Build Order

1. **job-search-mcp** — core, everything touches it. Start with read/write daily notes + company tracking.
2. **calendar-mcp** — needed for planning. Google Calendar read/write.
3. **OpenClaw skills** — wire `generate_plan()` first, test end-to-end planning flow.
4. **Discord channels** — set up #daily-plan, #job-search, #leetcode with correct session isolation config.
5. **Reminder/ping system** — OpenClaw reads daily note, pings at time blocks, captures responses.
6. **analyze_leetcode + get_recommendation** — LC workflow.
7. **email-mcp** — Gmail +recruiting label. Can forward manually in the meantime.
8. **end_of_day skill** — sweep + actual vs planned summary.

---

## Deferred / Open Questions

- **RAG / SQLite layer** — markdown files sufficient for now, revisit if Company_Tracking.md gets unwieldy at scale
- **Structured ping responses** — free-form accepted, Jacob corrects misinterpretations manually
- **LinkedIn inbound automation** — handled via end_of_day() conversational gap-fill only, no scraping
- **LangGraph** — not needed for current linear workflows, revisit if branching logic or multi-agent coordination becomes necessary

---

## Reference Files

These files exist in Jacob's Obsidian vault and should be provided to the implementation agent:

- `Daily_Schedule_Prompt.md` — full planning prompt, defines schedule format and all scheduling rules
- `Company_Tracking.md` — pipeline tracker with all active companies, recruiters, and status
- `PERFORMANCE_SUMMARY.md` — LC performance log and interview coaching notes
- `learning_roadmap.md` — skills gap analysis and current learning priorities
- `Jacob_Berdichevsky_Resume.pdf` — resume for company research context
