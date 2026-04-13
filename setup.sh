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

# Install MCP server
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

# Configure MCP server
MCP_CONFIG="$CLAUDE_CONFIG/mcp_servers.json"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "Configuring Claude Code MCP server..."

# Create or update mcp_servers.json
if [ -f "$MCP_CONFIG" ]; then
    # Backup existing config
    cp "$MCP_CONFIG" "$MCP_CONFIG.backup"
    echo "  (Backed up existing config to $MCP_CONFIG.backup)"
fi

# Add job-search entry
cat > "$MCP_CONFIG" <<EOF
{
  "job-search": {
    "command": "python3",
    "args": ["-m", "job_search_mcp"],
    "cwd": "$REPO_DIR"
  }
}
EOF

echo "✓ Claude Code configured"

# Install skills
echo ""
echo "Installing skills..."
SKILLS_DIR="$CLAUDE_CONFIG/skills"
mkdir -p "$SKILLS_DIR"

# Link each skill from the repo
for skill_dir in "$REPO_DIR/skills/"*/; do
    skill_name=$(basename "$skill_dir")
    target="$SKILLS_DIR/$skill_name"

    # Remove existing link/directory if present
    if [ -e "$target" ] || [ -L "$target" ]; then
        rm -rf "$target"
    fi

    # Create symlink
    ln -s "$skill_dir" "$target"
    echo "  ✓ Linked $skill_name"
done

echo "✓ Skills installed"

# Test MCP server
echo ""
echo "Testing MCP server connection..."
timeout 5 python3 -c "import job_search_mcp; print('✓ Package OK')" 2>/dev/null || {
    echo "⚠️  Could not import package — check that installation succeeded"
}

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Open Claude Code"
echo "  2. Run: /setup-job-search"
echo "  3. Follow the setup wizard"
echo ""
echo "Or use Claude Windows Companion app!"
