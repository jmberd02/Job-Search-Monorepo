# Manual Verification Checklist

## Setup Testing

### 1. Test setup.sh (Mac/Linux)
- [ ] Run `./setup.sh` on clean environment
- [ ] Verify Python version check works
- [ ] Verify MCP server installs
- [ ] Check `~/.claude/mcp_servers.json` created correctly
- [ ] Verify no errors during setup

### 2. Test setup wizard in Claude Code
- [ ] Open Claude Code
- [ ] Run `/setup-job-search`
- [ ] Follow wizard prompts
- [ ] Provide vault location
- [ ] Answer user context questions
- [ ] Verify vault created at specified location
- [ ] Check all folders and files exist

### 3. Verify vault structure
- [ ] Open vault in Obsidian
- [ ] Check folders: Companies/, Applications/, Day/, etc.
- [ ] Verify `.claude/` folder with skills
- [ ] Check `.claude/CLAUDE.md` has user context
- [ ] Verify Company Tracking.md exists
- [ ] Check README.md has quick start guide

## Workflow Testing

### 4. Test daily planning
- [ ] Run `/plan tomorrow` in Claude Code
- [ ] Verify plan is created
- [ ] Check plan reads context (tracker, performance)
- [ ] Make adjustments
- [ ] Verify plan saved to vault

### 5. Test company tracking
- [ ] Run `/track Got email from TestCo`
- [ ] Verify company note created
- [ ] Check Company Tracking.md updated
- [ ] Verify timeline entry added

### 6. Test email ingestion
- [ ] Run `/ingest [paste test email]`
- [ ] Verify email parsed correctly
- [ ] Check company/role extracted
- [ ] Verify notes updated

### 7. Test LeetCode tracking
- [ ] Run `/leetcode Did Two Sum, 15min, solved it`
- [ ] Verify analysis provided
- [ ] Check suggestions given
- [ ] Verify logged in daily activity

### 8. Test help command
- [ ] Run `/help`
- [ ] Verify all commands shown
- [ ] Check examples displayed

## Integration Testing

### 9. Full day workflow
- [ ] Morning: Plan day
- [ ] During: Track company updates
- [ ] During: Log LeetCode practice
- [ ] Evening: Review day
- [ ] Verify all notes updated correctly

### 10. Obsidian integration
- [ ] Open vault in Obsidian
- [ ] Manually edit a note
- [ ] Run command in Claude Code
- [ ] Verify Claude sees the changes
- [ ] Make change via Claude
- [ ] Refresh Obsidian
- [ ] Verify changes visible

## Cross-Platform (if possible)

### 11. Windows testing
- [ ] Test setup.ps1
- [ ] Verify path handling
- [ ] Test with Windows Companion app

## Notes

Document any issues found:
-
