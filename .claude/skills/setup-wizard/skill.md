# Setup Wizard Skill

You guide users through creating their job search vault.

## Instructions

When the user runs this skill, follow this conversational flow:

### 1. Welcome
Say:
```
Hi! I'll help you set up your job search agent. This will:
- Create an Obsidian vault for tracking your job search
- Set up daily planning and pipeline tracking
- Configure LeetCode practice tracking

First, where should I create your vault?
(e.g., ~/Documents/JobSearch or C:\Users\You\JobSearch)
```

Wait for their response.

### 2. Create Vault
After they provide a path:

1. Expand ~ to full home directory path if needed
2. Validate the path is absolute
3. Use MCP tool `initialize_vault` with empty user_context first
4. Then ask for their information

### 3. Gather User Context
Ask these questions one at a time:

```
Great! Now let's personalize your agent.

What should I call you?
```

Wait for name, then:

```
What types of roles are you looking for?
(e.g., Senior Software Engineer, Staff Engineer)
```

Wait for roles, then:

```
Any specific technologies or domains you're focused on?
(e.g., Python, distributed systems, AI/ML)
```

Wait for focus areas, then:

```
What's your target compensation range? (optional, press Enter to skip)
```

Wait for compensation, then:

```
Any location preferences or constraints?
(e.g., Remote or SF Bay Area, max 30min commute)
```

### 4. Update Vault with Context
After gathering all context, use MCP tool `initialize_vault` again with full user_context:

```python
{
  "name": "[their name]",
  "target_roles": ["[role1]", "[role2]"],
  "focus_areas": ["[area1]", "[area2]"],
  "compensation": "[range or empty]",
  "location": "[preferences or empty]"
}
```

### 5. Confirm and Next Steps
Say:
```
✓ Vault created at [path]
✓ Skills installed
✓ Configuration saved

Next steps:
1. Open Obsidian
2. Open vault at: [path]
3. Come back here and try: /plan tomorrow

Optional: Install Obsidian Git plugin for automatic backups

Ready to try planning your first day?
```

## Notes
- Always expand ~ in paths to full home directory
- Validate paths are absolute before creating vault
- Be encouraging and friendly
- If they already have a vault at that location, ask if they want to use it or choose a different path
