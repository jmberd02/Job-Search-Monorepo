# PowerShell setup script for Windows

$ErrorActionPreference = "Stop"

Write-Host "=== Job Search Agent Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1 | Select-String -Pattern "(\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
    Write-Host "✓ Python $pythonVersion detected" -ForegroundColor Green

    if ([version]$pythonVersion -lt [version]"3.10") {
        Write-Host "❌ Python 3.10+ required, found $pythonVersion" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from python.org"
    exit 1
}

# Install package
Write-Host ""
Write-Host "Installing job-search-mcp..."
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install MCP server" -ForegroundColor Red
    exit 1
}
Write-Host "✓ job-search-mcp installed" -ForegroundColor Green

# Find Claude directory
$claudeConfig = "$env:USERPROFILE\.claude"
if (-not (Test-Path $claudeConfig)) {
    Write-Host "⚠️  Claude Code config directory not found" -ForegroundColor Yellow
    Write-Host "Creating $claudeConfig..."
    New-Item -ItemType Directory -Path $claudeConfig -Force | Out-Null
}

# Create plugin directory
$pluginDir = "$claudeConfig\plugins\local\job-search"
$repoDir = $PSScriptRoot

Write-Host ""
Write-Host "Installing Claude Code plugin..."

# Remove old plugin
if (Test-Path $pluginDir) {
    Remove-Item -Recurse -Force $pluginDir
}

# Create structure
New-Item -ItemType Directory -Path "$pluginDir\.claude-plugin" -Force | Out-Null
New-Item -ItemType Directory -Path "$pluginDir\skills" -Force | Out-Null

# Create plugin metadata
$pluginJson = @{
    name = "job-search"
    description = "Job search automation with pipeline tracking, daily planning, email processing, and LeetCode analysis"
    author = @{
        name = "Job Search Agent"
        email = "support@example.com"
    }
    version = "1.0.0"
} | ConvertTo-Json -Depth 10

$pluginJson | Out-File -FilePath "$pluginDir\.claude-plugin\plugin.json" -Encoding utf8

# Create MCP config
$mcpJson = @{
    "job-search" = @{
        command = "python"
        args = @("-m", "job_search_mcp")
    }
} | ConvertTo-Json -Depth 10

$mcpJson | Out-File -FilePath "$pluginDir\.mcp.json" -Encoding utf8

# Copy skills
if (Test-Path "$repoDir\.claude\skills") {
    Copy-Item -Path "$repoDir\.claude\skills\*" -Destination "$pluginDir\skills\" -Recurse -Force
    Write-Host "  ✓ Installed skills" -ForegroundColor Green
}

# Create README
$readme = @"
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
- ``initialize_vault`` - Set up a new job search vault
- ``ingest_signal`` - Process recruiter messages
- ``upsert_company_tracking_entry`` - Track companies
- ``append_daily_activity`` - Log daily activities
- And more...

### Skills
Available skills:
- ``/setup-wizard`` - Set up your vault
- ``/plan-day`` - Plan your job search day
- ``/track-company`` - Track a company
- ``/ingest-email`` - Process recruiter emails
- ``/analyze-leetcode`` - Analyze LeetCode practice
- ``/help`` - Show all commands

## Installation

This plugin was installed by running ``setup.ps1`` from the job-search-agent repository.

To update:
1. Pull latest changes from the repo
2. Run ``.\setup.ps1`` again
"@

$readme | Out-File -FilePath "$pluginDir\README.md" -Encoding utf8

Write-Host "✓ Plugin installed at $pluginDir" -ForegroundColor Green

# Test
Write-Host ""
Write-Host "Testing MCP server..."
try {
    python -c "import job_search_mcp; print('✓ Package OK')"
} catch {
    Write-Host "⚠️  Could not import package" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart Claude Code to load the plugin"
Write-Host "  2. Run: /setup-wizard"
Write-Host "  3. Follow the setup wizard to create your vault"
Write-Host ""
Write-Host "The plugin is installed at:"
Write-Host "  $pluginDir"
Write-Host ""
