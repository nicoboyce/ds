# RSS Automation Scripts

Automated RSS aggregation and summarisation system for Zendesk ecosystem content.

## Overview

Daily automation pipeline that:
1. **Git pull** - Gets latest website changes
2. **RSS ingestion** - Fetches feeds, deduplicates articles
3. **Claude summaries** - Generates AI analysis for Zendesk professionals
4. **Page generation** - Updates `rss-feeds.md` with fresh content
5. **Jekyll build** - Builds static site
6. **Git push** - Deploys to GitHub Pages

## Files

### Core Scripts
- `rss_ingestion.py` - Fetches and processes RSS feeds
- `claude_summariser.py` - Generates AI summaries via Claude API
- `generate_rss_page.py` - Updates Jekyll markdown page
- `daily_rss_update.py` - Complete automation pipeline

### Setup
- `setup_cron.sh` - One-time setup script for cron job
- `README.md` - This documentation

## Quick Start

On your automation machine:

```bash
# 1. Clone/pull latest code
git clone https://github.com/nicoboyce/ds.git ~/deltastringdotcom/ds
cd ~/deltastringdotcom/ds

# 2. Set up Claude API key (optional but recommended)
export CLAUDE_API_KEY='your-api-key-here'
echo 'export CLAUDE_API_KEY="your-api-key-here"' >> ~/.bashrc

# 3. Run setup script
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh

# 4. Test manual run
python3 scripts/daily_rss_update.py
```

## Configuration

### RSS Feeds
Edit `_data/rss_feeds.yml` to add/remove feeds:

```yaml
feeds:
  - name: "Feed Name"
    url: "https://example.com/feed.xml"
    category: "zendesk"
    colour: "primary"
    description: "Feed description"
```

### Cron Schedule
Default: Daily at 9:00 AM GMT

To change: `crontab -e` and modify the schedule.

## Claude API Integration

### Getting API Key
1. Sign up at https://console.anthropic.com/
2. Generate API key
3. Set environment variable: `export CLAUDE_API_KEY='sk-...'`

### Summary Optimisation
Prompts target Zendesk administrators and focus on:
- Implementation impacts and timelines
- Feature changes affecting workflows
- Security and compliance implications
- Agent training requirements

## Data Storage

### `_data/rss/` Directory
- `articles.json` - All fetched articles
- `categorised.json` - Articles grouped by date
- `summaries.json` - Claude-generated summaries  
- `stats.json` - Processing statistics
- `automation.log` - Detailed execution logs
- `cron.log` - Cron job output

## Manual Operations

### Run Full Pipeline
```bash
cd ~/deltastringdotcom/ds
python3 scripts/daily_rss_update.py
```

### Individual Scripts
```bash
# Just fetch RSS feeds
python3 scripts/rss_ingestion.py

# Just generate summaries
python3 scripts/claude_summariser.py

# Just update page
python3 scripts/generate_rss_page.py
```

### View Logs
```bash
tail -f _data/rss/automation.log
tail -f _data/rss/cron.log
```

## Troubleshooting

### Common Issues

**No articles found:**
- Check RSS feed URLs are working
- Verify internet connection
- Some feeds may be temporarily down

**Claude API errors:**
- Check API key is set: `echo $CLAUDE_API_KEY`
- Verify API key is valid at https://console.anthropic.com/
- Scripts will continue with fallback summaries

**Git push failures:**
- Check SSH keys are configured
- Verify repository permissions
- May need to resolve merge conflicts

**Jekyll build errors:**
- Check Ruby/Bundle versions
- Run `bundle install` if gems missing
- Verify `_config.yml` is valid

### Reset Pipeline
```bash
# Clear data and logs
rm -rf _data/rss/*

# Fresh start
python3 scripts/daily_rss_update.py
```

### Check Cron Job
```bash
# List cron jobs
crontab -l

# Edit cron jobs  
crontab -e

# Check cron service
sudo service cron status    # Ubuntu/Debian
sudo launchctl list | grep cron    # macOS
```

## Monitoring

The system logs all operations to `_data/rss/automation.log` with timestamps and detailed error messages.

Key metrics tracked:
- Articles fetched per feed
- Processing time per step
- Success/failure rates
- API call statistics

## Security Notes

- Claude API key should be kept secure
- Git operations use existing SSH configuration
- No sensitive data is logged
- All operations are read-only except for site updates

## Support

For issues with the automation scripts, check:
1. Log files in `_data/rss/`
2. Cron job configuration: `crontab -l`
3. Manual script execution for debugging
4. RSS feed accessibility via browser