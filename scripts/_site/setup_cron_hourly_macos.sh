#!/bin/bash
"""
Setup script for hourly RSS automation on macOS
Run this script to configure the cron job and environment for hourly execution
"""

# Configuration for this machine
SITE_DIR="/Users/nico/ds/ds"
PYTHON_PATH="/usr/bin/python3"  # macOS system Python3
CRON_TIME="0 * * * *"  # Hourly on the hour

echo "=== Hourly RSS Automation Setup (macOS) ==="
echo "Site directory: $SITE_DIR"
echo "Python path: $PYTHON_PATH"
echo "Cron schedule: $CRON_TIME (every hour on the hour)"
echo ""

# Check if site directory exists
if [ ! -d "$SITE_DIR" ]; then
    echo "ERROR: Site directory does not exist: $SITE_DIR"
    echo "Please check the path - this should be the current working directory."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3."
    exit 1
fi

# Check required Python packages
echo "Checking Python dependencies..."
python3 -c "import requests, yaml, bs4" 2>/dev/null || {
    echo "Missing Python packages detected. Installing required packages..."
    pip3 install requests pyyaml beautifulsoup4
}

# Check Ruby/Jekyll setup
echo "Checking Jekyll setup..."
cd "$SITE_DIR"
if ! command -v bundle &> /dev/null; then
    echo "ERROR: bundle not found. Please install bundler: gem install bundler"
    exit 1
fi

# Install Jekyll dependencies if needed
if [ ! -d "vendor/bundle" ]; then
    echo "Installing Jekyll dependencies..."
    bundle install
fi

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
    echo "3. Reload your shell: source ~/.bashrc (or ~/.zshrc)"
    echo ""
    read -p "Continue without Claude API? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Please configure CLAUDE_API_KEY first."
        exit 1
    fi
fi

# Create cron job with proper environment
echo "Setting up cron job for hourly execution..."

# Create wrapper script that sets up environment for cron
WRAPPER_SCRIPT="$SITE_DIR/scripts/cron_wrapper.sh"
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
# Cron wrapper script - sets up environment and runs RSS automation

# Set up PATH for cron environment
export PATH="/usr/local/bin:/usr/bin:/bin"

# Set up rbenv if it exists
if [ -d "$HOME/.rbenv" ]; then
    export PATH="$HOME/.rbenv/bin:$PATH"
    eval "$(rbenv init -)"
fi

# Preserve Claude API key if set
if [ -n "$CLAUDE_API_KEY" ]; then
    export CLAUDE_API_KEY="$CLAUDE_API_KEY"
fi

# Change to site directory and run automation
cd "/Users/nico/ds/ds"
python3 scripts/daily_rss_update.py >> _data/rss/cron.log 2>&1
EOF

chmod +x "$WRAPPER_SCRIPT"

# Remove existing RSS cron jobs
(crontab -l 2>/dev/null | grep -v "daily_rss_update.py" | grep -v "cron_wrapper.sh") | crontab -

# Add new hourly cron job using wrapper script
(crontab -l 2>/dev/null; echo "$CRON_TIME $WRAPPER_SCRIPT") | crontab -

echo "Cron job installed:"
echo "$CRON_TIME $WRAPPER_SCRIPT"
echo ""

# Test run
echo "Running test execution..."
cd "$SITE_DIR"
python3 scripts/daily_rss_update.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=== SETUP COMPLETE ==="
    echo "Hourly RSS automation is now configured!"
    echo ""
    echo "Schedule: $CRON_TIME (every hour on the hour)"
    echo "Logs: $SITE_DIR/_data/rss/automation.log"
    echo "Cron log: $SITE_DIR/_data/rss/cron.log"
    echo ""
    echo "To check cron jobs: crontab -l"
    echo "To remove: crontab -e (delete the RSS line)"
    echo ""
    echo "Manual run: cd $SITE_DIR && python3 scripts/daily_rss_update.py"
else
    echo ""
    echo "ERROR: Test run failed. Please check the error messages above."
    echo "Cron job was installed but may not work correctly."
    exit 1
fi