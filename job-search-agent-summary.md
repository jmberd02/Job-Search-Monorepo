# Job Search Agent — Conversation Summary + Spec

## What We're Building

A job-search automation system grounded in an Obsidian vault, designed to support daily planning, pipeline tracking, recruiting-message ingestion, interview note synthesis, and technical interview practice. Obsidian remains the single source of truth.

This spec is intentionally dual-layer:

- It describes the current Obsidian vault as it actually exists today.
- It also defines the normalized MCP-facing model the agent layer should expose and maintain on top of that vault.

---

## Key Architecture Decisions

### Why not pure OpenClaw
Context bloat. Pasting recruiter emails, transcripts, and long interview notes directly into chat creates permanent user and assistant messages that accumulate across the day. OpenClaw is good at lightweight synthesis and orchestration, not as the long-term home for heavy raw content.

### Why not LangGraph
Overkill for the current workflow. The core jobs are still linear: read notes or APIs, run an LLM step, write the result back. There is no meaningful branching, looping, or multi-agent graph logic yet. Revisit if the workflows become materially more stateful or conditional.

### Why MCP + OpenClaw
MCP servers are the data and integration layer: read/write notes, fetch Gmail, fetch Calendar, maintain normalized records. OpenClaw handles the agent loop, conversational iteration, and skill logic. This keeps the architecture simple:

- MCP owns storage and integrations
- OpenClaw owns reasoning and orchestration
- Obsidian owns persistence

### Why Discord channels for isolation
Each Discord channel is an isolated OpenClaw session. Sessions reset at 4AM. Context does not accumulate across days, while continuity lives in Obsidian notes rather than chat history.

### Why git via Obsidian Git plugin
Obsidian Git provides simple backup, history, and atomic saves without extra infrastructure. It is sufficient for this notebook-style workflow.

---

## Architecture

```text
You -> Discord -> OpenClaw (agent loop + skills) -> MCP tools -> Obsidian / Gmail / Calendar
```

### Principles

- Obsidian is the source of truth across planning, pipeline tracking, prep, and retrospectives.
- MCP servers are data and integration tools only; they do not contain LLM logic.
- OpenClaw skills perform all LLM-driven synthesis and decision support.
- Discord channels isolate concerns and keep daily context small.
- Cross-day continuity lives in notes, not chat history.
- The MCP must reconcile an irregular but structured vault into a stable operational interface.

### Stack

- **OpenClaw** — agent loop, skills, reminders, conversational orchestration
- **MCP servers** — Obsidian/Gmail/Calendar integration plus normalization logic
- **Discord** — trigger and chat interface
- **Obsidian** — durable markdown knowledge base
- **Obsidian Git plugin** — note backup and history

---

## Current Vault Reality vs Canonical MCP Layer

### Current Vault Reality

The current vault is not a flat four-file store. It is a structured notebook with a small number of canonical top-level notes plus a larger body of supporting notes.

Today the notebook includes:

- top-level hub/index notes such as `Progress.md`
- candidate-specific profile and planning notes such as `Candidate Profile.md`
- top-level canonical trackers such as `Company Tracking.md`
- daily planning notes under `Day/`
- rich company notes under `Companies/`
- call and interview notes under `Calls/`
- application notes under `Applications/`
- detailed LeetCode notes and dated summaries under `Leetcode/`
- prompt and workflow notes under `Prompts/`
- pre-interview notes under `Pre-Interview Notes/`

The vault is already useful and structured, but it is not fully normalized. The same topic can appear at multiple levels: for example, a company can exist in `Company Tracking.md`, `Companies/<Company>.md`, call notes, application notes, and daily plans.

### Canonical MCP Layer

The MCP should present a stable operational model over that notebook rather than pretending the raw vault is already normalized.

The MCP layer should:

- read and write the existing canonical notes
- traverse supporting notes when richer context is needed
- create and maintain a small number of normalized top-level artifacts
- keep index notes lightweight and non-authoritative
- reconcile detailed note ingestion into concise operational summaries

This means the MCP is not just a file reader. It is the normalization layer between a real-world notebook and a reliable automation interface.

---

## Obsidian Vault Structure

Current high-level structure:

```text
Job Search/
  Progress.md
  Candidate Profile.md
  Company Tracking.md
  LeetCode Skill Assessment Report.md
  Day/
    YYYY-MM-DD.md
  Companies/
    <Company>.md
  Calls/
    <Date or Month>/
      <Call Note>.md
  Applications/
    <Date Bucket>/
      <Application Note>.md
  Leetcode/
    <Date Bucket>/
      <Problem Notes>.md
      PERFORMANCE SUMMARY.md
  Pre-Interview Notes/
    <Prep Note>.md
  Prompts/
    Daily Schedule Prompt.md
    LeetCode Performance Feedback Prompt.md
```

### Canonical note roles

- `Progress.md`
  top-level hub/index only. It should link to canonical notes and recent working notes for easier navigation and search. It is not a source of truth.

- `Candidate Profile.md`
  canonical private candidate context note. It should hold persistent information the system needs for personalization, such as background summary, target roles, compensation targets, commute/location constraints, search priorities, scheduling preferences, daily capacity limits, recurring commitments, and other standing planning notes that should shape daily schedules and recommendations.

- `Company Tracking.md`
  canonical top-level job pipeline record and search index. It is authoritative for current operational state, next action, due date, waiting state, and follow-up planning, but not for rich historical detail.

- `Day/*.md`
  canonical daily planning and execution history.

- `Companies/*.md`
  canonical detailed company context and chronology. These notes hold richer raw information, such as interview history, recruiter details, comp notes, pros/cons, qualitative signals, and freeform human notes.

- New top-level `Performance Summary.md`
  canonical high-level interview-prep and LeetCode performance summary, maintained by MCP from detailed LeetCode notes and assessment notes. This is a new normalized artifact, not a file that already exists today.

### Supporting detail stores

- `Calls/**` — detailed recruiter/interview/networking notes
- `Applications/**` — per-role application records
- `Pre-Interview Notes/**` — interview-specific prep context
- `Leetcode/**` — detailed problem attempts and dated performance summaries
- `Prompts/**` — reusable planning and feedback prompt documents

### Daily note format

Current daily notes already follow `Prompts/Daily Schedule Prompt.md` closely:

1. Calendar Events
2. Yesterday's Progress
3. Schedule
4. Pending Follow-Ups
5. Success Criteria
6. Interview Prep Section

The intended target structure is:

1. Schedule
2. Daily Activity
3. Schedule vs Activity

`Daily Activity` should be the append-only execution log for what actually happened during the day. `Schedule vs Activity` should be a derived comparison section, generated on demand or at end of day. That structure does not currently exist consistently across the notebook; MCP writing should add and maintain it going forward.

---

## MCP Servers

### job-search-mcp

Core data and normalization layer for Obsidian.

Responsibilities:

- read/write canonical top-level notes
- read candidate profile and standing planning constraints
- read/update detailed company notes
- read call/interview/application notes when needed for synthesis
- read LeetCode detail notes and dated summaries
- maintain the new top-level `Performance Summary.md`
- update `Progress.md` lightly as an index, not as an authoritative dashboard

Suggested interface shape:

```text
read_daily_note(date)                           -> returns Day/YYYY-MM-DD.md
write_daily_note(date, content)                 -> writes Day/YYYY-MM-DD.md
append_daily_activity(date, block, status, note)-> appends execution updates to Daily Activity
refresh_schedule_vs_activity(date)              -> writes/updates derived Schedule vs Activity section

read_progress_hub()                             -> returns Progress.md
update_progress_hub(data)                       -> lightly updates index links/sections

read_candidate_profile()                        -> returns Candidate Profile.md
update_candidate_profile(data)                  -> updates persistent candidate/search constraints

read_company_tracking()                         -> returns Company Tracking.md
upsert_company_tracking_entry(company, data)    -> updates canonical pipeline state
list_pending_followups()                        -> parses Company Tracking.md for actionable items

read_company_note(company)                      -> returns Companies/<Company>.md
upsert_company_note(company, data)              -> creates or updates detailed company note

list_company_call_notes(company)                -> returns related Calls/** notes
list_company_application_notes(company)         -> returns related Applications/** notes
list_company_prep_notes(company)                -> returns related Pre-Interview Notes/** notes

ingest_company_signal(signal)                   -> normalizes a recruiter message, transcript, event, or manual note
resolve_company_reference(signal)               -> maps a signal to an existing company or flags ambiguity
classify_company_signal(signal)                 -> extracts stage, sentiment, next action, dates, and note payload

read_top_performance_summary()                  -> returns top-level Performance Summary.md
update_top_performance_summary(data)            -> updates normalized performance summary
list_leetcode_notes(range_or_tag)               -> returns relevant Leetcode/** notes
```

### Company workflow rule

Company ingestion uses **detail-first write flow, tracker-first read flow**.

That means:

1. write rich/raw information into `Companies/*.md` first
2. distill the operational state into `Company Tracking.md`
3. read `Company Tracking.md` first for planning and follow-up workflows
4. drill into `Companies/*.md` and related notes only when deeper context is needed

This is intentional. It keeps rich context in the detailed note while preserving a reliable top-level operational tracker.

### Company/application/tracker boundary

The normalized model is **company-first**, not application-first.

- a company may exist before any application exists
- recruiter outreach, networking, referrals, and ambiguous inbound signals may belong only to the company layer
- applications are subordinate per-role records under a company
- `Company Tracking.md` is organized by company, with zero or more application links under each company entry

This matches the actual workflow better than making applications the top-level entity. The company is the stable identity anchor; applications are optional role-specific processes attached to it.

### Canonical schema contracts

The schemas below are the implementation contracts the MCP should code against. The current vault may not satisfy them perfectly yet, but new writes and migrations should converge toward them.

#### `Companies/<Company>.md`

Purpose:

- canonical detailed company note
- stable company facts and high-level operational snapshot
- chronology of inbound and outbound signals
- human-editable notes area for quick context capture

Suggested structure:

```text
---
tags:
  - job-search
  - company
company: <canonical company name>
company_key: <stable slug>
status: <active|waiting|closed|networking>
interest: <1-5>
last_updated: YYYY-MM-DD
---

# <Company Name>

## Snapshot
- **Status:** ...
- **Interest:** 1-5
- **Primary next action:** ...
- **Next action due:** YYYY-MM-DD or TBD
- **Best current role:** ...
- **Location:** ...
- **Commute fit:** ...
- **Comp / range:** ...
- **Company Tracking:** [[Company Tracking]]

## Notes
- freeform human notes
- quick thoughts worth preserving
- ad hoc details that may later inform synthesis

## Contacts
| Name | Role | Source | Last Contact | Notes |
|------|------|--------|--------------|-------|

## Active Applications
- [[Applications/<bucket>/<Company> - <Role>.md]]

## Context
- company description
- pros / cons
- business model
- risks / signals
- prep-relevant notes

## Timeline
| Date | Type | Summary | Source | Linked Note |
|------|------|---------|--------|-------------|

## Open Questions
- ...

## Related
- [[Calls/...]]
- [[Pre-Interview Notes/...]]
- [[Applications/...]]
```

Rules:

- `Snapshot` is the MCP-owned operational summary for the company note
- `Notes` is intentionally human-friendly and should allow ad hoc additions
- `Timeline` is append-only and is the first destination for ingested company signals
- role-specific signals may appear in `Timeline`, but their detailed process state belongs in the application note
- company notes may exist with zero applications

#### `Applications/**`

Purpose:

- one note per concrete role/application
- role-specific process state, materials, interview loop, and outcome

Suggested structure:

```text
---
tags:
  - job-search
  - application
company: <canonical company name>
company_key: <stable slug>
role: <role title>
application_key: <stable slug>
status: <drafted|applied|screen|interview|onsite|offer|rejected|withdrawn|ghosted>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
---

# <Company> - <Role>

## Snapshot
- **Company:** [[Companies/<Company>]]
- **Role:** ...
- **Status:** ...
- **Applied on:** YYYY-MM-DD
- **Current stage:** ...
- **Next action:** ...
- **Due:** YYYY-MM-DD or TBD
- **Priority / Interest:** ...
- **Comp:** ...
- **Location:** ...

## Materials
- resume version used
- cover letter
- job link
- referral / intro path

## Interview Process
| Date | Stage | People | Outcome | Notes |
|------|-------|--------|---------|-------|

## Role-Specific Notes
- why this role
- fit / gaps
- prep points
- custom requirements

## Tasks
- [ ] ...

## Outcome
- rejection / withdrawal / offer details when closed
```

Rules:

- create one application note per distinct role or opportunity
- if there is company-level interest but no concrete role yet, do not create an application note
- application notes should not duplicate broad company context unless needed for the role
- role-specific tasks belong here; general networking or company-level follow-up belongs in the company layer or tracker

#### `Company Tracking.md`

Purpose:

- authoritative operational read model
- top-level search/index surface for the job search
- compact bridge to company and application detail notes

Suggested structure:

```text
# Company Tracking

## Needs Action This Week
| Company | Status | Next Action | Due |
|---------|--------|-------------|-----|

## Active Interview Pipeline

### <Company>
- **Status:** ...
- **Interest:** 1-5
- **Current state:** ...
- **Next action:** ...
- **Due:** ...
- **Applications:**
  - [[Applications/...]]
- **Contacts:** ...
- **Notes:** [[Companies/<Company>]]

## Waiting / In Flight
... company-first entries ...

## Applied / No Response
... company-first entries ...

## Networking Leads
... company-first entries ...

## Closed Out
... company-first entries ...
```

Rules:

- tracker organization is company-first, because companies may have inbound activity before any application exists
- a company entry may link to zero, one, or many application notes
- tracker entries should be compact and operational; they are not the place for full chronology
- tracker sections may use tables, company subsections, or a mixed format, but the top-level entity is always the company
- tracker content should optimize for searchability and rapid planning reads

### Update ownership rules

To keep human edits safe and MCP updates predictable:

- MCP may rewrite `Snapshot`, `Active Applications`, and `Timeline` in company notes
- MCP may append to `Notes`, but should not aggressively rewrite or normalize human freeform notes
- MCP may fully manage role `Snapshot`, `Interview Process`, `Tasks`, and `Outcome` in application notes
- MCP may rewrite the structured operational portions of `Company Tracking.md`
- humans may write anywhere, but machine-generated updates should preserve clearly human-authored freeform content where possible

### Identity and idempotency rules

The normalized layer should aim for no duplicate logical entries, but source systems may still emit duplicate or repeated artifacts. MCP writes therefore need idempotency rules.

- company identity is keyed by `company_key`
- application identity is keyed by `application_key`
- ingested signals should carry a source marker when possible, such as:
  - email id
  - calendar event id
  - linkedin thread/message id
  - `manual:<date>:<slug>`
- `Timeline` and application process updates should check for an existing matching source marker before appending a new row
- duplicate source artifacts should update existing operational state rather than creating duplicate note content

### Unified company-signal ingestion model

Email, LinkedIn messages, interview transcripts, and recruiting calendar events should converge into one normalized ingestion path after source-specific fetching.

The model is:

1. source adapter fetches a raw artifact
2. MCP normalizes it into a `company signal`
3. MCP resolves whether it maps to an existing company
4. detailed company note is updated first
5. `Company Tracking.md` is updated second if the operational state changes

Suggested normalized signal types:

- `recruiter_message`
- `interview_transcript`
- `calendar_event`
- `application_event`
- `manual_note`

The normalized company-signal layer is shared. The fetch path is still source-specific.

### calendar-mcp

Google Calendar integration for both planning and event-derived job-search signals.

```text
get_events(date)                           -> returns events for a given day
get_events_range(start, end)               -> returns events across date range
create_event(title, date, time, notes)     -> creates calendar event
list_recruiting_events(range)              -> returns interviews/recruiter events relevant to the pipeline
```

Calendar event rule:

- if an event maps clearly to an existing company, update that company automatically
- if the event does not map cleanly to a known company, ask the user what it is before creating or updating company records
- if the company is known but the event meaning is ambiguous, enrich conservatively and avoid inventing stage changes

### email-mcp

Source adapter for recruiting emails explicitly routed into the recruiting inbox/label.

```text
fetch_recruiting_label()                   -> fetches unread recruiting-labeled mail
mark_processed(email_id)                   -> marks item as processed
```

Trigger pattern:

- the user labels a message for job-search ingestion in Gmail
- MCP processes only that inbox slice

Nothing enters the job-search pipeline unless it is explicitly labeled or otherwise captured intentionally.

### linkedin-mcp

Source adapter for LinkedIn recruiter and hiring-manager outreach.

```text
fetch_recruiting_messages()                -> fetches LinkedIn messages relevant to job search
mark_message_processed(message_id)         -> marks LinkedIn thread/message as processed
```

This feeds inbound recruiter conversations into the shared company-signal ingestion path.

---

## Discord Channels

```text
#daily-plan           -> planning, reminders, daily activity, schedule vs activity
#job-pipeline-inbox   -> email, LinkedIn, transcript, and calendar-derived pipeline ingestion
#job-search-qa        -> general questions, strategy, and interpretation
#leetcode             -> debriefs, recommendations, performance updates
#leetcode threads     -> active problem help and hint sessions, if thread isolation is supported
```

Each channel is an isolated OpenClaw session. All reset independently at 4AM.

Channel intent matters:

- `#job-pipeline-inbox` is for ingestion and pipeline updates, not general discussion
- `#job-search-qa` is for ad hoc questions and strategy
- `#leetcode` should stay lightweight unless active-help sessions are isolated into threads

---

## OpenClaw Skills

All LLM calls live in skills. Skills fetch structured and unstructured context through MCP, run synthesis, and write results back through MCP.

### generate_plan(date)
Triggered by: `plan tomorrow` in `#daily-plan`

```text
1. read_daily_note(yesterday)               -> extract completed/incomplete items
2. get_events(tomorrow)                     -> calendar blocks
3. get_events(day_after)                    -> preview
4. read_candidate_profile()                 -> persistent constraints and planning preferences
5. read_company_tracking()                  -> pending follow-ups and deadlines
6. read_top_performance_summary()           -> weak areas and current interview-prep themes
7. optionally read external roadmap/context -> only if useful and available
8. assemble context
9. run LLM with Prompts/Daily Schedule Prompt.md
10. present draft for conversational iteration
11. write_daily_note(tomorrow, approved_content)
```

### ingest_company_signal(signal)
Triggered by: source-specific fetch flows in `#job-pipeline-inbox`

```text
1. classify_company_signal(signal)            -> extract company, people, role, stage, sentiment, dates, and next action
2. resolve_company_reference(signal)          -> map to a known company or flag ambiguity
3. if company is unknown or ambiguous         -> ask the user before creating/updating pipeline state
4. upsert_company_note(company, detail)       -> rich details first
5. upsert_company_tracking_entry(company, state_if_changed)
6. return summary to Discord
```

### analyze_transcript(company, transcript)
Triggered by: transcript ingestion in `#job-pipeline-inbox`

```text
1. convert transcript into an `interview_transcript` company signal
2. run interview-specific analysis for topics, signals, risks, and next steps
3. pass normalized output through ingest_company_signal(signal)
4. return structured summary to Discord
```

### analyze_leetcode(problem, notes, solution)
Triggered by: `just did [problem]` in `#leetcode`

```text
1. list_leetcode_notes(relevant_range)        -> load supporting performance history
2. read_top_performance_summary()             -> load current normalized summary
3. LLM analyzes approach, time, mistakes, and pattern category
4. append_daily_activity(today, leetcode_block, status, note_if_relevant)
5. write/update detailed Leetcode note(s)
6. update_top_performance_summary(data)
7. return analysis and pattern summary
```

### get_recommendation(context)
Triggered by: `what should I practice` or `I have [company] interview Friday` in `#leetcode`

```text
1. read_top_performance_summary()             -> weak areas and recent themes
2. read_company_tracking()                    -> upcoming interviews and company signals
3. optionally read Companies/<Company>.md     -> if deeper context is needed
4. LLM generates tailored recommendation
5. return recommendation with rationale
```

### leetcode_help(problem_context)
Triggered by: active help requests in `#leetcode` or a `#leetcode` thread

```text
1. detect whether this is an active-help session rather than a debrief
2. if thread isolation is supported, keep problem-specific help in its own thread/session
3. provide hints, nudges, and next-step guidance without forcing a full solution unless asked
4. when the attempt ends, optionally hand off to analyze_leetcode(...)
```

### end_of_day()
Triggered explicitly by the user in `#daily-plan`

```text
1. read_daily_note(today)                     -> load planned schedule
2. review logged actual entries               -> from reminder responses
3. refresh_schedule_vs_activity(today)        -> write/update derived Schedule vs Activity section
4. fetch_recruiting_label()                   -> sweep for anything new today
5. prompt for missing inbound items
6. update company note(s) first, then tracker entries
```

### schedule_reminder
Runs throughout the day in `#daily-plan`

```text
1. read_daily_note(today)                     -> parse time blocks
2. ping the user at each block start
3. capture response
4. append_daily_activity(today, block, status, note)
```

`schedule_reminder` is an OpenClaw orchestration behavior, not an MCP behavior. MCP only reads and writes notes; OpenClaw owns timers, polling, reminders, and escalation messages.

### polling and ambiguity handling

OpenClaw should poll ingestion sources on a timer:

- Gmail label polling
- LinkedIn message polling
- recruiting/interview calendar event polling

When ingestion is clear, OpenClaw should update notes automatically through MCP. When mapping or intent is ambiguous, OpenClaw should message the user instead of guessing.

---

## Interaction Flows

### End-of-day planning

```text
You: "plan tomorrow"
OpenClaw: reads today's daily note, Company Tracking.md, calendar, and performance summary
OpenClaw: drafts tomorrow's plan using Prompts/Daily Schedule Prompt.md
You: "move LC block to morning"
OpenClaw: updates and re-presents
You: "looks good"
OpenClaw: writes Day/YYYY-MM-DD.md
```

### Recruiter email processing

```text
OpenClaw: polls the Gmail job-search label
OpenClaw: normalizes each email into a company signal
OpenClaw: updates Companies/<Company>.md first
OpenClaw: updates Company Tracking.md second
If ambiguous:
OpenClaw: asks the user for clarification in #job-pipeline-inbox
```

### LinkedIn message processing

```text
You: "process LinkedIn messages"
OpenClaw: fetches inbound recruiter/hiring-manager threads
OpenClaw: normalizes each thread/message into a company signal
OpenClaw: updates Companies/<Company>.md first
OpenClaw: updates Company Tracking.md second
OpenClaw: returns a concise summary
```

### Calendar event ingestion

```text
OpenClaw: reads recruiting/interview events from calendar
If company match is clear:
OpenClaw: normalizes the event into a company signal
OpenClaw: updates the existing company note and tracker entry
If company match is not clear:
OpenClaw: asks the user what the event is before creating or updating company records
```

### Schedule reminders and execution logging

```text
OpenClaw: "Morning block starting. Ready?"
You: "still finishing write-up, 20 more min"
OpenClaw: appends execution notes to today's daily note
Later:
OpenClaw: generates a Schedule vs Activity section from those logs
```

### LeetCode debrief

```text
You: "just did two sum, knew it was hash map but blanked on impl"
OpenClaw: reads recent Leetcode/** notes plus the top-level Performance Summary.md
OpenClaw: appends a Daily Activity note if the work session should be reflected in the day log
OpenClaw: updates the detailed note/history
OpenClaw: updates the top-level performance summary
OpenClaw: returns the distilled pattern readout
```

### Active LeetCode help

```text
You: ask for help while actively working on a problem
Preferred:
OpenClaw: handles this in a dedicated #leetcode thread/session
OpenClaw: gives hints and step guidance while keeping main #leetcode context small
Fallback if thread isolation is not available:
use a separate help-oriented session/channel rather than overloading the main #leetcode session
```

---

## Context Management

### Why context stays small

- heavy raw content is stored in notes, not chat
- channels are isolated by concern
- sessions reset daily
- MCP reads only the notes needed for a given workflow
- top-level canonical notes reduce the need to re-parse every detailed note on every run

### Context hygiene and session drift

OpenClaw should monitor context growth and session drift heuristically.

It should watch for:

- long active-help exchanges
- mixed intents inside an ingestion session
- too much raw pasted content in one session
- repeated back-and-forth that no longer matches the channel's purpose

When drift is detected, OpenClaw should:

- suggest moving to a more appropriate channel or thread
- summarize the current state before redirecting
- keep ingestion sessions narrow and operational
- prefer isolated threads/sessions for active LeetCode help

### Cross-day continuity

Cross-day continuity lives in Obsidian. Daily planning reads prior notes and canonical trackers fresh from disk. Chat resets do not matter as long as the notes are updated correctly.

---

## New Notebook Bootstrap Workflow

This system also needs a dedicated setup skill or equivalent workflow for initializing a fresh Obsidian notebook. Runtime MCP tools should not be the only place this knowledge lives.

### v1 setup responsibilities

The bootstrap workflow should perform full environment bootstrap for a new notebook:

- create the canonical folder structure
- create seed top-level notes such as `Progress.md`, `Candidate Profile.md`, `Company Tracking.md`, and top-level `Performance Summary.md`
- create prompt notes and note templates
- establish Git/bootstrap expectations
- document or configure required plugin/environment setup needed for the notebook to behave correctly

This is separate from runtime MCP operation. The setup workflow initializes the notebook; MCP and OpenClaw operate on it afterward.

---

## Build Order

1. **job-search-mcp**
   start with daily-note read/write, `Candidate Profile.md`, company-note updates, and `Company Tracking.md` maintenance
2. **top-level performance summary support**
   add normalized performance-summary maintenance over existing `Leetcode/**` detail notes
3. **calendar-mcp**
   support planning, preview flows, and calendar-derived recruiting/interview event reads
4. **OpenClaw skills**
   wire `generate_plan()` first, then the unified company-signal ingestion flow, then LeetCode flows
5. **reminder/ping system**
   append `Daily Activity` logs and generate derived `Schedule vs Activity`
6. **email-mcp**
   fetch recruiter emails into the shared company-signal ingestion flow
7. **linkedin-mcp**
   fetch LinkedIn recruiter/hiring-manager messages into the shared company-signal ingestion flow
8. **context hygiene / thread strategy**
   enforce channel intent, drift detection, and isolated LeetCode help sessions
9. **new notebook bootstrap skill/workflow**
   make the system reusable for future Obsidian notebooks

---

## Deferred / Open Questions

- **RAG / SQLite layer** — not needed yet; revisit only if markdown scale becomes a real operational bottleneck
- **Conflict handling across duplicated note layers** — the intended steady state is detail-first writes and tracker-first operational reads
- **LangGraph** — still unnecessary unless the workflows become materially more branching or state-machine-like

---

## Reference Files and Inputs

Current vault files that matter operationally:

- `Job Search/Progress.md` — index/hub only
- `Job Search/Candidate Profile.md` — persistent candidate context, planning constraints, and standing preferences
- `Job Search/Company Tracking.md` — canonical pipeline tracker
- `Job Search/Prompts/Daily Schedule Prompt.md` — daily planning template and constraints
- `Job Search/Prompts/LeetCode Performance Feedback Prompt.md` — LeetCode feedback prompt
- `Job Search/LeetCode Skill Assessment Report.md` — current high-level assessment note
- `Job Search/Day/*.md` — daily plans and execution history
- `Job Search/Companies/*.md` — detailed company notes
- `Job Search/Calls/**` — supporting call/interview detail
- `Job Search/Applications/**` — per-role application records
- `Job Search/Leetcode/**` — detailed LeetCode history

Optional external/supporting inputs:

- `learning_roadmap.md` or similar roadmap notes, if present
- resume files or other supporting artifacts, whether stored in the vault or outside it

These optional inputs may improve synthesis, but core workflows must not depend on them.
