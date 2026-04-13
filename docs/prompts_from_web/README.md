# Job Search AI Prompts

This directory contains all the AI prompts used for managing Jacob's job search. These prompts are designed to work with Claude or other LLMs to automate and streamline various job search tasks.

## Prompt Categories

### Daily Planning & Organization

**Daily Schedule.md**
- Generates time-blocked daily schedules for job search activities
- Considers calendar events, previous day's progress, energy management
- Includes interview prep priorities and follow-up tracking
- **When to use:** Start of each day or night before to plan the next day
- **Inputs needed:** Previous day's plan, Google Calendar, Company Tracking doc

### Call & Interview Management

**Precall Prep.md**
- Prepares you for upcoming recruiter/company calls
- Generates questions to ask, talking points, and red flags to watch for
- **When to use:** 5-15 minutes before any call
- **Inputs needed:** Company tracking entry for the company you're meeting with

**Transcript Storage.md**
- Extracts structured call summaries from transcripts
- Formats: contact info, compensation, tech stack, next steps, interest level
- **When to use:** Immediately after a recruiter or intro call
- **Inputs needed:** Call transcript (from Otter.ai, Fireflies, etc.)

**Interview Review.md**
- Analyzes interview transcripts and provides structured feedback
- Identifies answer quality, signal strength, gaps, and provides rewrites
- **When to use:** After technical or behavioral interviews
- **Inputs needed:** Interview transcript

### Company & Pipeline Tracking

**Company Tracking Update.md**
- Updates your Company Tracking doc from call notes
- Moves companies between tiers, updates next actions
- **When to use:** After processing call notes, to sync to main tracking doc
- **Inputs needed:** Current Company Tracking doc + call notes document

**Job Search Project Prompt.md**
- General-purpose career coach prompt
- Provides context about Jacob's background, experience, and targets
- **When to use:** Starting new conversations or as base context for other tasks
- **Inputs needed:** None (standalone)

### Technical Interview Prep

**LeetCode Performance Analysis.md**
- Analyzes specific LeetCode problem attempts
- Provides structured feedback on approaches, patterns, and gaps
- Gives strength assessment and interview readiness timeline
- **When to use:** After completing a set of 5-10 LeetCode problems
- **Inputs needed:** Problem attempts with code, time taken, struggles

**LeetCode Skill Assessment.md**
- Comprehensive skill rating across all attempted problems
- Reviews conversation history to find all coding practice
- **When to use:** Weekly or before interviews to assess overall progress
- **Inputs needed:** Access to chat history (Claude can search its own memory)

## Usage Workflow

### Typical Daily Flow
1. **Morning:** Use `Daily Schedule.md` to plan the day
2. **Before calls:** Use `Precall Prep.md` with company info
3. **After calls:** Use `Transcript Storage.md` to extract summary
4. **After interviews:** Use `Interview Review.md` for feedback
5. **Weekly:** Use `Company Tracking Update.md` to sync everything

### Interview Prep Flow
1. Start with `LeetCode Performance Analysis.md` after each practice session
2. Use `LeetCode Skill Assessment.md` weekly to track progress
3. Use `Interview Review.md` after real interviews to improve

## File Locations

- **This directory:** `/docs/prompts_from_web/` - Canonical source, organized and categorized
- **Vault location:** `gdrive_jobsearch/Job Search Obsidian/Job Search/Prompts/` - Original location, may have older versions

## Notes for Skills Integration

These prompts are designed to be used:
1. **Manually:** Copy/paste into Claude conversations
2. **Via Skills:** Some may be integrated into Claude Code skills
3. **Via Templates:** Reference from Obsidian templates when creating new notes

For skills development, these prompts provide the foundational instructions that can be wrapped with tool calls and automation.
