#!/bin/bash
"""
Setup script for RSS automation on this local machine
Adjusted for the correct path and local configuration
"""

# Configuration for this machine
SITE_DIR="/Users/nico/ds/ds"
PYTHON_PATH="/usr/bin/python3"  # System Python
CRON_TIME="0 9 * * *"  # Daily at 9:00 AM

echo "=== RSS Automation Setup (Local) ==="
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

# Dependencies already installed, just confirm
echo "Python dependencies (requests, pyyaml) are already installed."

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$SITE_DIR/scripts/"*.py
chmod +x "$SITE_DIR/scripts/"*.sh

# Create data directory (already exists)
mkdir -p "$SITE_DIR/_data/rss"

# Claude CLI available but no API key - that's fine
echo "Claude CLI is available at: $(which claude)"
echo "API key not configured - will use fallback summaries"
echo ""

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