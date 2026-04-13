#!/bin/bash

set -e

echo "=== Job Search Agent Setup ==="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "Please install Python 3.10 or higher:"
    echo "  - Mac: brew install python@3.10"
    echo "  - Linux: sudo apt install python3.10"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION detected"

# Check minimum version
REQUIRED="3.10"
if [ "$(printf '%s\n' "$REQUIRED" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED" ]; then
    echo "❌ Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi

# Install MCP server package
echo ""
echo "Installing job-search-mcp..."
pip install -e . || {
    echo "❌ Failed to install MCP server"
    exit 1
}
echo "✓ job-search-mcp installed"

# Find Claude Code config directory
CLAUDE_CONFIG="$HOME/.claude"
if [ ! -d "$CLAUDE_CONFIG" ]; then
    echo "⚠️  Claude Code config directory not found at $CLAUDE_CONFIG"
    echo "Creating it now..."
    mkdir -p "$CLAUDE_CONFIG"
fi

# Create plugin directory structure
PLUGIN_DIR="$CLAUDE_CONFIG/plugins/local/job-search"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "Installing Claude Code plugin..."

# Remove old plugin if exists
if [ -d "$PLUGIN_DIR" ]; then
    rm -rf "$PLUGIN_DIR"
fi

# Create plugin structure
mkdir -p "$PLUGIN_DIR/.claude-plugin"
mkdir -p "$PLUGIN_DIR/skills"

# Create plugin metadata
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<EOF
{
  "name": "job-search",
  "description": "Job search automation with pipeline tracking, daily planning, email processing, and LeetCode analysis",
  "author": {
    "name": "Job Search Agent",
    "email": "support@example.com"
  },
  "version": "1.0.0"
}
EOF

# Create MCP server config
cat > "$PLUGIN_DIR/.mcp.json" <<EOF
{
  "job-search": {
    "command": "python3",
    "args": ["-m", "job_search_mcp"]
  }
}
EOF

# Copy skills
if [ -d "$REPO_DIR/.claude/skills" ]; then
    cp -r "$REPO_DIR/.claude/skills/"* "$PLUGIN_DIR/skills/" 2>/dev/null || true
    echo "  ✓ Installed skills"
fi

# Create plugin README
cat > "$PLUGIN_DIR/README.md" <<EOF
# Job Search Agent Plugin

Automate your job search workflow with Claude Code.

## Features

- 📅 Daily Planning - AI-powered daily job search plans
- 🏢 Pipeline Tracking - Organize companies and applications
- 📧 Email Processing - Parse recruiter messages automatically
- 💻 LeetCode Analysis - Track practice and get recommendations

## Usage

### MCP Tools
This plugin provides MCP tools for:
- \`initialize_vault\` - Set up a new job search vault
- \`ingest_signal\` - Process recruiter messages
- \`upsert_company_tracking_entry\` - Track companies
- \`append_daily_activity\` - Log daily activities
- And more...

### Skills
Available skills:
- \`/setup-wizard\` - Set up your vault
- \`/plan-day\` - Plan your job search day
- \`/track-company\` - Track a company
- \`/ingest-email\` - Process recruiter emails
- \`/analyze-leetcode\` - Analyze LeetCode practice
- \`/help\` - Show all commands

## Installation

This plugin was installed by running \`setup.sh\` from the job-search-agent repository.

To update:
1. Pull latest changes from the repo
2. Run \`./setup.sh\` again
EOF

echo "✓ Plugin installed at $PLUGIN_DIR"

# Test MCP server
echo ""
echo "Testing MCP server..."
timeout 5 python3 -c "import job_search_mcp; print('✓ Package OK')" 2>/dev/null || {
    echo "⚠️  Could not import package — check that installation succeeded"
}

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to load the plugin"
echo "  2. Run: /setup-wizard"
echo "  3. Follow the setup wizard to create your vault"
echo ""
echo "The plugin is installed at:"
echo "  $PLUGIN_DIR"
echo ""
