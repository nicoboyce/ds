#!/bin/bash
# Setup script for RSS automation - corrected for local machine
# Run this script to configure the cron job and environment

# Configuration
SITE_DIR="$HOME/ds"
PYTHON_PATH="$(which python3)"
CRON_TIME="0 9 * * *"  # Daily at 9:00 AM

echo "=== RSS Automation Setup ==="
echo "Site directory: $SITE_DIR"
echo "Python path: $PYTHON_PATH"
echo "Cron schedule: $CRON_TIME (9:00 AM daily)"
echo ""

# Check if site directory exists
if [ ! -d "$SITE_DIR" ]; then
    echo "ERROR: Site directory does not exist: $SITE_DIR"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3."
    exit 1
fi

# Check required Python packages
echo "Checking Python dependencies..."
python3 -c "import requests" 2>/dev/null || {
    echo "Installing requests..."
    pip3 install --user requests
}
python3 -c "import yaml" 2>/dev/null || {
    echo "Installing pyyaml..."
    pip3 install --user pyyaml
}

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$SITE_DIR/scripts/"*.py
chmod +x "$SITE_DIR/scripts/"*.sh

# Create data directory
mkdir -p "$SITE_DIR/_data/rss"

# Check for Claude API key (optional)
if [ -z "$CLAUDE_API_KEY" ]; then
    echo ""
    echo "NOTE: CLAUDE_API_KEY environment variable not set"
    echo "The automation will work but Claude AI summaries will be disabled."
    echo "The system will use fallback summaries instead."
    echo ""
    echo "To enable Claude summaries later:"
    echo "1. Get your API key from: https://console.anthropic.com/"
    echo "2. Add to your shell profile (~/.bashrc):"
    echo "   export CLAUDE_API_KEY='your-api-key-here'"
    echo "3. Reload your shell: source ~/.bashrc"
    echo ""
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

# Verify cron installation
echo "Verifying cron installation..."
if crontab -l | grep -q "daily_rss_update.py"; then
    echo "✓ Cron job successfully installed"
else
    echo "✗ Cron job installation may have failed"
fi
echo ""

echo "=== SETUP COMPLETE ==="
echo ""
echo "Daily RSS automation is now configured!"
echo "Schedule: $CRON_TIME (9:00 AM daily)"
echo "Logs: $SITE_DIR/_data/rss/automation.log"
echo "Cron log: $SITE_DIR/_data/rss/cron.log"
echo ""
echo "To test manually: cd $SITE_DIR && python3 scripts/daily_rss_update.py"
echo "To check cron jobs: crontab -l"
echo "To remove: crontab -e (delete the line)"
echo ""
echo "Next step: Run a manual test to verify everything works"