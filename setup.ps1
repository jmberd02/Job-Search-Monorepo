# setup.ps1
Write-Host "=== Job Search Agent Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from python.org"
    exit 1
}

# Check minimum version
$version = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
if ([version]$version -lt [version]"3.10") {
    Write-Host "❌ Python 3.10+ required, found $version" -ForegroundColor Red
    exit 1
}

# Install MCP server
Write-Host ""
Write-Host "Installing job-search-mcp..." -ForegroundColor Cyan
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install MCP server" -ForegroundColor Red
    exit 1
}
Write-Host "✓ job-search-mcp installed" -ForegroundColor Green

# Find Claude Code config directory
$claudeConfig = "$env:USERPROFILE\.claude"
if (!(Test-Path $claudeConfig)) {
    Write-Host "⚠️  Claude Code config directory not found" -ForegroundColor Yellow
    Write-Host "Creating it now..."
    New-Item -ItemType Directory -Path $claudeConfig -Force | Out-Null
}

# Configure MCP server
$mcpConfig = "$claudeConfig\mcp_servers.json"
$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "Configuring Claude Code MCP server..." -ForegroundColor Cyan

# Backup existing config
if (Test-Path $mcpConfig) {
    Copy-Item $mcpConfig "$mcpConfig.backup"
    Write-Host "  (Backed up existing config)" -ForegroundColor Gray
}

# Add job-search entry
$config = @{
    "job-search" = @{
        "command" = "python"
        "args" = @("-m", "job_search_mcp.server")
        "cwd" = $repoDir
    }
}

$config | ConvertTo-Json -Depth 10 | Set-Content $mcpConfig
Write-Host "✓ Claude Code configured" -ForegroundColor Green

# Install skills
Write-Host ""
Write-Host "Installing skills..." -ForegroundColor Cyan
$skillsDir = "$claudeConfig\skills"
if (!(Test-Path $skillsDir)) {
    New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
}

# Copy each skill from the repo (.claude\skills\)
Get-ChildItem "$repoDir\.claude\skills" -Directory | ForEach-Object {
    $skillName = $_.Name
    $source = $_.FullName
    $target = "$skillsDir\$skillName"

    # Remove existing directory if present
    if (Test-Path $target) {
        Remove-Item $target -Force -Recurse
    }

    # Copy skill directory
    Copy-Item -Path $source -Destination $target -Recurse -Force
    Write-Host "  ✓ Installed $skillName" -ForegroundColor Green
}

Write-Host "✓ Skills installed" -ForegroundColor Green

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Open Claude Code (or restart if already open)"
Write-Host "  2. Run: /setup-wizard"
Write-Host "  3. Follow the setup wizard"
Write-Host ""
Write-Host "Or use Claude Windows Companion app!"
