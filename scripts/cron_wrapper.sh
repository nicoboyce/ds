#!/bin/bash
# Cron wrapper script - sets up environment and runs RSS automation

# Set up PATH for cron environment
export PATH="/usr/local/bin:/usr/bin:/bin"

# Preserve Claude API key if set
if [ -n "$CLAUDE_API_KEY" ]; then
    export CLAUDE_API_KEY="$CLAUDE_API_KEY"
fi

# Change to site directory and run automation
cd "/Users/nico/ds/ds"
python3 scripts/daily_rss_update.py >> _data/rss/cron.log 2>&1
