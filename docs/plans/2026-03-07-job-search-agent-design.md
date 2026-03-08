# Job Search Agent Design

**Date:** 2026-03-07

**Purpose:** Capture the approved implementation-ready design for the job-search agent so implementation can proceed without re-deciding schema or note ownership.

## Scope

This design covers:

- the canonical Obsidian note boundaries
- the normalized company/application/tracker model
- MCP ownership rules for machine-managed versus human-managed sections
- idempotent signal ingestion requirements
- the recommended v1 implementation order

This design does not define:

- production hosting
- Discord/OpenClaw deployment details
- Gmail/Calendar/LinkedIn auth specifics
- long-term storage beyond the markdown vault

## Core Model

The normalized model is company-first.

- `Companies/*.md` is the canonical detailed company note
- `Applications/**` is a subordinate per-role record store
- `Company Tracking.md` is the top-level operational tracker and search index
- a company may exist before any application exists
- signals may attach to a company even when no application exists yet

## Canonical Note Roles

### `Companies/<Company>.md`

Purpose:

- stable company facts
- current company snapshot
- chronology of signals and interactions
- freeform human notes

Machine-managed sections:

- `Snapshot`
- `Active Applications`
- `Timeline`

Human-friendly sections:

- `Notes`
- most of `Context`
- ad hoc related links and annotations

Required frontmatter:

```yaml
tags:
  - job-search
  - company
company: <canonical company name>
company_key: <stable slug>
status: <active|waiting|closed|networking>
interest: <1-5>
last_updated: YYYY-MM-DD
```

Required headings:

- `## Snapshot`
- `## Notes`
- `## Contacts`
- `## Active Applications`
- `## Context`
- `## Timeline`
- `## Open Questions`
- `## Related`

### `Applications/**`

Purpose:

- one note per role or concrete opportunity
- role-specific process state
- materials used
- interview loop
- role-specific tasks and outcome

Required frontmatter:

```yaml
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
```

Required headings:

- `## Snapshot`
- `## Materials`
- `## Interview Process`
- `## Role-Specific Notes`
- `## Tasks`
- `## Outcome`

### `Company Tracking.md`

Purpose:

- top-level operational read model
- top-level search/index surface
- bridge back to detailed company and application notes

Rules:

- tracker organization is company-first
- company entries may link to zero, one, or many applications
- tracker is authoritative for current operational state
- tracker is not authoritative for full chronology or raw detail

## Workflow Rules

### Detail-first write flow

1. Normalize the incoming artifact into a `company signal`
2. Resolve the company identity
3. Write the signal into `Companies/<Company>.md` first
4. Update any affected application note second, if the signal is role-specific
5. Distill operational state into `Company Tracking.md`

### Tracker-first read flow

1. Read `Company Tracking.md` first for planning, follow-up, and prioritization
2. Read `Companies/<Company>.md` for rich context
3. Read `Applications/**` only when the role-specific process matters

## Ownership Rules

To preserve human edits:

- MCP may rewrite company `Snapshot`, `Active Applications`, and `Timeline`
- MCP may append to company `Notes`, but should not aggressively rewrite it
- MCP may manage application `Snapshot`, `Interview Process`, `Tasks`, and `Outcome`
- MCP may rewrite structured sections in `Company Tracking.md`
- freeform human content should be preserved unless explicitly targeted

## Idempotency Rules

The note layer should not accumulate duplicate logical events.

- company identity is keyed by `company_key`
- application identity is keyed by `application_key`
- ingested artifacts should carry source markers where possible
- source markers should include email IDs, calendar event IDs, LinkedIn message IDs, or stable manual markers
- a matching source marker should update an existing entry rather than append a duplicate

## Open V1 Decisions

These are implementation decisions, not design blockers:

- define the minimal schema for `Candidate Profile.md`
- decide whether old daily notes are migrated or only new notes use the new format
- keep `Company Tracking.md` flexible in prose but strict in machine-managed subsections
- define enum values in code for signal types, task states, and stage names

## Git Attribution Rule

If an implementation agent creates commits for this work, it must not assume the default Git identity.

- before the first commit, ask the user which commit author identity to use
- use per-commit Git configuration rather than changing global Git config
- example pattern:

```bash
git -c user.name="<chosen name>" -c user.email="<chosen email>" commit -m "..."
```

## Recommended V1 Build Order

1. Local vault MCP layer only
2. Company note read/write and tracker maintenance
3. Application note support
4. Candidate profile and top-level performance summary
5. Daily note write and append behavior
6. External ingestion adapters

## Source of Truth

The authoritative living design is also maintained in:

- [job-search-agent-summary.md](/home/jacob/workspace/job_monorepo/job-search-agent-summary.md)
