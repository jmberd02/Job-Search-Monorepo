# Job Search Agent

Automate your job search workflow with Claude Code and Obsidian.

## Features

- 📅 **Daily Planning** - AI-powered daily job search plans
- 🏢 **Pipeline Tracking** - Organize companies and applications
- 📧 **Email Processing** - Parse recruiter messages automatically
- 💻 **LeetCode Analysis** - Track practice and get recommendations
- 📝 **Obsidian Integration** - All data in markdown, local and private

## Installation

### Prerequisites
- Python 3.10 or higher
- Claude Code (CLI or Windows Companion)
- Obsidian (optional but recommended)

### Quick Start

**1. Clone this repository:**
```bash
git clone https://github.com/yourusername/job-search-agent.git
cd job-search-agent
```

**2. Run setup:**
```bash
./setup.sh  # Mac/Linux
./setup.ps1 # Windows
```

**3. Create your vault:**
```bash
# Open Claude Code
claude

# Run setup wizard
/setup-job-search
```

**4. Open in Obsidian:**
- Open Obsidian
- Open the vault at the path you chose during setup
- Start tracking your job search!

## Usage

### Daily Workflow

**Morning:**
```
/plan tomorrow
```
Claude creates a balanced daily plan with LeetCode practice, pipeline work, and interview prep.

**During the day:**
```
/track Got email from Acme Corp wanting to schedule call
```
Claude updates your pipeline automatically.

**Process recruiter emails:**
```
/ingest [paste email]
```
Claude extracts company, role, and next steps.

**After LeetCode:**
```
/leetcode Did "Word Ladder", 45min, struggled with BFS
```
Claude tracks progress and suggests next problems.

**End of day:**
```
/eod
```
Claude reviews your day and suggests tomorrow's priorities.

### See All Commands
```
/help
```

## Vault Structure

Your vault contains:
- `Company Tracking.md` - Pipeline dashboard
- `Companies/` - Detailed company notes
- `Applications/` - Per-role application tracking
- `Day/` - Daily plans and activity logs
- `Leetcode/` - Practice tracking
- `.claude/skills/` - Workflow skills

## Tips

- Use Obsidian to browse and manually edit notes
- Install Obsidian Git plugin for automatic backups
- Talk naturally with Claude - slash commands are optional
- Your data stays local and private

## Sharing with Friends

1. Share this repository link
2. They follow the installation steps above
3. Each person gets their own private vault

## Development

**Run tests:**
```bash
pytest tests/ -v
```

**Install for development:**
```bash
pip install -e ".[dev]"
```

## Architecture

```
Claude Code ↔ MCP Server ↔ Obsidian Vault
    ↑              ↑              ↑
  Skills      Read/Write      Markdown
```

- **Skills** - Conversational workflows in `.claude/skills/`
- **MCP Server** - Data layer for vault operations
- **Vault** - Obsidian markdown notes (local, private)

## License

MIT

## Contributing

Issues and PRs welcome!
