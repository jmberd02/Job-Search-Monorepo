## Goal

Reorganize `Company Tracking.md` so it is faster to scan, easier to maintain, and better suited for agent updates.

## Problems With Current Structure

- Too much narrative detail lives directly in the tracking doc.
- Company status, recruiter info, interview notes, lessons learned, and general reflections are mixed together.
- It is useful for deep reading, but inefficient for daily action-taking.
- Heavy notes belong in linked documents, not in the main dashboard.

## Target Design

Make `Company Tracking.md` the high-signal operating dashboard.

It should answer, at a glance:
- What is active right now?
- What needs action this week?
- What is blocked / waiting?
- What is closed out?
- Who are the key contacts?
- What should I follow up on next?

## Proposed Structure

### 1. Needs Action This Week
Purpose:
- Top-priority section
- Only companies or contacts requiring an explicit action soon

Each entry should include:
- company
- current status
- next action
- due date
- linked notes

### 2. Active Interview Pipeline
Purpose:
- Companies currently in motion
- Recruiter screen, technical rounds, onsite, references, etc.

Each entry should include:
- company
- role
- status/stage
- contacts
- comp
- location
- interest
- next action
- related links

### 3. Waiting / In Flight
Purpose:
- Applied or interviewed, but waiting on response
- No immediate action unless a deadline passes

Each entry should include:
- company
- latest event
- waiting for
- follow-up date
- related links

### 4. Applied / No Response
Purpose:
- Applications submitted, no active conversation yet

Each entry should include:
- company
- role
- application date
- priority
- follow-up date
- related links

### 5. Networking Leads
Purpose:
- Warm leads, referrals, recruiters, exploratory contacts
- Not yet in a formal interview process

Each entry should include:
- company/person
- source of intro
- current state
- next action
- related links

### 6. Closed Out
Purpose:
- Rejected, declined, or not pursuing
- Keep compact for reference, not storytelling

Each entry should include:
- company
- outcome
- date
- short reason
- related links

### 7. Recruiters & Contacts
Purpose:
- Keep recruiter/contact records in the same file for now
- Separate from pipeline sections so they do not clutter company workflow

Each entry should include:
- name
- company / firm
- what they recruit for
- last contact
- next action
- notes

## What Should Move Out Of Company Tracking

These should live in separate linked notes:
- raw recruiter call transcripts
- detailed interview notes
- long-form company research
- role-specific application tailoring
- pre-interview prep notes
- deep postmortems
- long lessons learned

## What Should Stay In Company Tracking

Keep only high-signal operational data:
- current stage
- current role
- contact names
- comp range
- location / commute reality
- interest level
- next action
- due date
- one-line notes
- links to detailed notes

## Suggested Entry Format

Example:

### Beacon AI
- Status: Onsite completed Mar 6, 2026
- Role: APAS Engineer
- Contacts: Rebecca, Michael, Rohan
- Comp: L4 160-180k / L5 175-200k + equity
- Location: San Carlos hybrid
- Interest: 3.5/5
- Next action: Wait for next-step update
- Due: Mar 10, 2026
- Summary: Strong fit, interesting technical scope, commute and work-hours are concerns
- Related:
  - [[Calls/Feb 23/Beacon AI Technical Interview]]
  - [[Calls/Feb 11/Beacon AI Call]]

## Benefits Of This Reorg

- Faster daily review
- Easier agent updates
- Less duplication
- Cleaner separation between source notes and dashboard state
- Better prioritization of follow-ups and deadlines
- Easier to maintain as pipeline grows

## Guiding Rule

`Company Tracking.md` should be a control panel, not a transcript archive.
