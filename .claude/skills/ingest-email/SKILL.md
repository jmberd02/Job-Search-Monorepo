---
name: ingest-email
trigger: slash-command
description: Process recruiter emails and messages
---

# Email Ingestion Skill

You process recruiter emails and messages.

## Instructions

When user runs `/ingest` with an email or message:

### 1. Parse the Email
Extract:
- Sender name and company
- Subject line
- Main points
- Any role/position mentioned
- Any dates or deadlines
- Next steps or call to action

### 2. Classify the Signal
Determine:
- Is this initial outreach, follow-up, interview invite, rejection?
- What stage is this company at?
- What action is requested?

### 3. Normalize to Company Signal
Use MCP tool `ingest_company_signal` with:
```python
{
  "type": "recruiter_message",
  "company": "[extracted company]",
  "role": "[role if mentioned]",
  "stage": "[current stage]",
  "content": "[key points]",
  "next_action": "[what to do]",
  "due_date": "[deadline if any]",
  "source": "email"
}
```

### 4. Present Summary and Ask
Show:
```
Found:
- Company: [Company]
- From: [Person, Role]
- Role: [Position] (if mentioned)
- Stage: [Inbound outreach / Follow-up / Interview invite]
- Next step: [Action requested]

Should I:
1. Add to Active Pipeline
2. Add to Networking Leads (interested but not applying yet)
3. Skip (not interested)
```

Wait for their decision.

### 5. Update Based on Decision
Based on their choice:
- **Active Pipeline**: Create/update company note, add to Active section
- **Networking**: Create/update company note, add to Networking section
- **Skip**: Don't create notes, maybe add to closed if it was follow-up

### 6. Confirm
```
✓ [Company] added to [Pipeline Section]
✓ Timeline updated
✓ Next action: [action]

Want me to help draft a response?
```

## Examples

**Example 1: Cold recruiter email**
```
From: sarah@techco.com
Subject: Senior Engineer opportunity

Hi, we're hiring for a Senior Backend Engineer role...
```

You extract:
- Company: TechCo
- Person: Sarah (recruiter)
- Role: Senior Backend Engineer
- Stage: Initial outreach

Then ask if they want to pursue it.

**Example 2: Interview invitation**
```
From: mike@startup.io
Subject: Interview next week?

Following up on our call. Want to schedule technical interview?
Available Mon/Wed/Fri next week.
```

You extract:
- Company: StartupCo (recognize from existing notes)
- Person: Mike
- Stage: Moving to technical interview
- Action: Schedule interview
- Options: Mon/Wed/Fri

Update company note and suggest responding.

## Notes
- Don't make assumptions - ask if unclear
- Preserve important details from email in notes
- Be concise in summaries but capture key info
- Suggest helpful next steps
