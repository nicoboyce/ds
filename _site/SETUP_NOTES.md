# RSS Automation Setup Notes

## Context for New Claude Instance

You are helping to set up the RSS feeds automation system that was developed on another machine. The complete system has been built and committed to git - you just need to deploy it.

## What This System Does

**RSS Aggregation & AI Summarisation for Zendesk Professionals:**
- Fetches RSS feeds from Zendesk ecosystem sources (official announcements, developer updates, industry blogs)
- Generates AI-powered daily/weekly summaries optimised for Zendesk administrators
- Updates Jekyll site with date-focused content (emphasises when things happened, not just sources)
- Automatically deploys to GitHub Pages via daily cron job

## System Architecture

**Daily Pipeline:** `git pull` → `RSS ingestion` → `Claude summaries` → `page generation` → `Jekyll build` → `git commit/push`

**Key Files:**
- `rss-feeds.md` - The main RSS page (date-focused design with Claude AI summaries)
- `_data/rss_feeds.yml` - RSS sources configuration  
- `scripts/` - Complete automation system
- `_data/rss/` - Generated data storage

## Your Task

Help the user set up the automation on this machine. The system is completely ready - just needs deployment.

## Setup Process

1. **Pull latest code** (system was just committed)
2. **Optional: Configure Claude API key** for AI summaries
3. **Run setup script** (`scripts/setup_cron.sh`)
4. **Test execution** to ensure it works

## Important Details

**Target Audience:** The Claude AI summaries are specifically optimised for Zendesk instance administrators, solution partners, and technical decision-makers. Focus on implementation impacts, not general tech news.

**RSS Sources Currently Configured:**
- Zendesk Announcements (FetchRSS)
- Zendesk What's New (FetchRSS)  
- Zendesk Developer Updates (FetchRSS)
- Zendesk Release Notes (FetchRSS)
- Zendesk Service Notifications (FetchRSS)
- Deltastring YouTube (FetchRSS)
- Internal Note blog
- Google News - Zendesk

**Cron Schedule:** Daily at 9:00 AM GMT (catches overnight Zendesk updates)

**Error Handling:** System continues even if some feeds fail or Claude API is unavailable

## Troubleshooting

If setup fails:
- Check `scripts/README.md` for detailed troubleshooting
- Logs are in `_data/rss/automation.log`
- Manual test: `python3 scripts/daily_rss_update.py`

## Success Indicators

- Cron job installed: `crontab -l`
- Test run completes without errors
- RSS page updates at `/rss-feeds` 
- Site builds and deploys to GitHub Pages

## Next Steps After Setup

Once automation is running:
- Monitor logs for first few days
- Check RSS page updates daily
- Consider adding more RSS sources via `_data/rss_feeds.yml`
- Claude API summaries can be tweaked in `scripts/claude_summariser.py`

The system is designed to be low-maintenance once running. It handles errors gracefully and continues operating even if individual components fail.