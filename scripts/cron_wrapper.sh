#!/bin/bash
# Cron wrapper script - sets up environment and runs RSS automation

# Set up PATH for cron environment including rbenv
export PATH="/Users/nico/.rbenv/shims:/Users/nico/.rbenv/bin:/usr/local/bin:/usr/bin:/bin"

# Preserve Claude API key if set
if [ -n "$CLAUDE_API_KEY" ]; then
    export CLAUDE_API_KEY="$CLAUDE_API_KEY"
fi

# Change to site directory and run automation
cd "/Users/nico/ds/ds" || exit 1

# Run with explicit error capture
echo "=== LaunchAgent execution started at $(date) ===" >> _data/rss/cron.log 2>&1
python3 scripts/daily_rss_update.py >> _data/rss/cron.log 2>&1
exit_code=$?
echo "=== LaunchAgent execution ended with exit code $exit_code at $(date) ===" >> _data/rss/cron.log 2>&1
exit $exit_code
