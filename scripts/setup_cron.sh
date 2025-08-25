#!/bin/bash
"""
Setup script for RSS automation on your other machine
Run this script to configure the cron job and environment
"""

# Configuration
SITE_DIR="$HOME/deltastringdotcom/ds"
PYTHON_PATH="/usr/local/bin/python3"  # Adjust if needed
CRON_TIME="0 9 * * *"  # Daily at 9:00 AM

echo "=== RSS Automation Setup ==="
echo "Site directory: $SITE_DIR"
echo "Python path: $PYTHON_PATH"
echo "Cron schedule: $CRON_TIME (9:00 AM daily)"
echo ""

# Check if site directory exists
if [ ! -d "$SITE_DIR" ]; then
    echo "ERROR: Site directory does not exist: $SITE_DIR"
    echo "Please clone the repository first:"
    echo "  git clone https://github.com/nicoboyce/ds.git $SITE_DIR"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3."
    exit 1
fi

# Check required Python packages
echo "Checking Python dependencies..."
python3 -c "import requests, yaml" 2>/dev/null || {
    echo "Installing required Python packages..."
    pip3 install requests pyyaml
}

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$SITE_DIR/scripts/"*.py
chmod +x "$SITE_DIR/scripts/"*.sh

# Create data directory
mkdir -p "$SITE_DIR/_data/rss"

# Check for Claude API key
if [ -z "$CLAUDE_API_KEY" ]; then
    echo ""
    echo "WARNING: CLAUDE_API_KEY environment variable not set"
    echo "The automation will work but Claude summaries will be disabled."
    echo ""
    echo "To enable Claude summaries:"
    echo "1. Get your API key from: https://console.anthropic.com/"
    echo "2. Add to your shell profile (~/.bashrc or ~/.zshrc):"
    echo "   export CLAUDE_API_KEY='your-api-key-here'"
    echo "3. Reload your shell: source ~/.bashrc"
    echo ""
    read -p "Continue without Claude API? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Please configure CLAUDE_API_KEY first."
        exit 1
    fi
fi

# Create cron job
echo "Setting up cron job..."
CRON_COMMAND="cd $SITE_DIR && $PYTHON_PATH scripts/daily_rss_update.py >> _data/rss/cron.log 2>&1"

# Remove existing cron job if exists
(crontab -l 2>/dev/null | grep -v "daily_rss_update.py") | crontab -

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_TIME $CRON_COMMAND") | crontab -

echo "Cron job installed:"
echo "$CRON_TIME $CRON_COMMAND"
echo ""

# Test run (dry run)
echo "Running test execution..."
cd "$SITE_DIR"
python3 scripts/daily_rss_update.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=== SETUP COMPLETE ==="
    echo "Daily RSS automation is now configured!"
    echo ""
    echo "Schedule: $CRON_TIME (9:00 AM daily)"
    echo "Logs: $SITE_DIR/_data/rss/automation.log"
    echo "Cron log: $SITE_DIR/_data/rss/cron.log"
    echo ""
    echo "To check cron jobs: crontab -l"
    echo "To remove: crontab -e (delete the line)"
    echo ""
    echo "Manual run: cd $SITE_DIR && python3 scripts/daily_rss_update.py"
else
    echo ""
    echo "ERROR: Test run failed. Please check the error messages above."
    echo "Cron job was installed but may not work correctly."
    exit 1
fi