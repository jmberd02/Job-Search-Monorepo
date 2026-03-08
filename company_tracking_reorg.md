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

## Folder Structure

```
Job Search Obsidian/Job Search/
├── Company Tracking.md          ← dashboard + Recruiters & Contacts section
├── Companies/                   ← one file per company
│   ├── Beacon AI.md
│   ├── Applied Intuition.md
│   ├── Atomic Machines.md
│   ├── Zoox.md
│   └── ...
├── Calls/                       ← call transcripts, referenced from company files
├── Applications/                ← application notes, referenced from company files
├── Pre-Interview Notes/         ← prep notes, referenced from company files
├── Day/                         ← daily notes
└── Leetcode/                    ← unchanged
```

Each `Companies/<Company Name>.md` contains all detail for that company:
- Role, stage, comp, location, interest level
- Contacts list
- Interview history and outcomes
- Links to relevant `Calls/` and `Applications/` notes
- Summary notes and lessons

`Company Tracking.md` references company files via `[[Companies/Beacon AI]]` etc.

`Recruiters.md` is dissolved — recruiter and contact records live in the Recruiters & Contacts section of `Company Tracking.md`.

## Proposed Structure of Company Tracking.md

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
- company (link to `[[Companies/Name]]`)
- role
- status/stage
- contacts
- comp
- location
- interest
- next action

### 3. Waiting / In Flight
Purpose:
- Applied or interviewed, but waiting on response
- No immediate action unless a deadline passes

Each entry should include:
- company (link to `[[Companies/Name]]`)
- latest event
- waiting for
- follow-up date

### 4. Applied / No Response
Purpose:
- Applications submitted, no active conversation yet

Each entry should include:
- company (link to `[[Companies/Name]]`)
- role
- application date
- priority
- follow-up date

### 5. Networking Leads
Purpose:
- Warm leads, referrals, recruiters, exploratory contacts
- Not yet in a formal interview process

Each entry should include:
- company/person
- source of intro
- current state
- next action

### 6. Closed Out
Purpose:
- Rejected, declined, or not pursuing
- Keep compact for reference, not storytelling

Each entry should include:
- company (link to `[[Companies/Name]]`)
- outcome
- date
- short reason

### 7. Recruiters & Contacts
Purpose:
- Lives directly in Company Tracking.md — no separate file
- Separate from pipeline sections so they do not clutter company workflow

Each entry should include:
- name
- company / firm
- what they recruit for
- last contact
- next action
- notes

## What Should Move Out Of Company Tracking

These should live in `Companies/<Name>.md` or existing linked notes:
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
- links to `[[Companies/Name]]`

## Suggested Entry Format

### Company Tracking.md entry

```
### Beacon AI
- Status: Onsite completed Mar 6, 2026
- Role: APAS Engineer
- Contacts: Rebecca, Michael, Rohan
- Comp: L4 160-180k / L5 175-200k + equity
- Location: San Carlos hybrid
- Interest: 3.5/5
- Next action: Wait for next-step update
- Due: Mar 10, 2026
- Notes: [[Companies/Beacon AI]]
```

### Companies/Beacon AI.md

```
## Beacon AI

- Role: APAS Engineer
- Stage: Onsite completed Mar 6, 2026
- Contacts: Rebecca (recruiter), Michael (hiring manager), Rohan (tech interviewer)
- Comp: L4 160-180k / L5 175-200k + equity
- Location: San Carlos hybrid
- Interest: 3.5/5
- Summary: Strong fit, interesting technical scope, commute and work-hours are concerns

## Interview History

| Date | Event | Notes |
|------|-------|-------|
| Feb 11 | Recruiter call | [[Calls/Feb 11/Beacon AI Call]] |
| Feb 23 | Technical interview with Rohan | [[Calls/Feb 23/Beacon AI Technical Interview]] |
| Mar 6 | Onsite | — |

## Notes

...
```

## Benefits Of This Reorg

- Faster daily review
- Easier agent updates
- Less duplication
- Cleaner separation between source notes and dashboard state
- Better prioritization of follow-ups and deadlines
- Easier to maintain as pipeline grows
- One canonical file per company for all deep context

## Guiding Rule

`Company Tracking.md` should be a control panel, not a transcript archive.
Each company's full story lives in `Companies/<Name>.md`.
