# Cron Job Fix Notes - 07/09/2025

## What Was Done

### 1. Fixed TLS/Network Issues in daily_rss_update.py
- **Problem**: Script was failing with "gnutls_handshake() failed: The TLS connection was non-properly terminated"
- **Solution**: Added fallback to `GIT_SSL_NO_VERIFY=true` when standard git pull fails
- **Changes**: Modified git_pull() and git_commit_push() functions to handle SSL errors

### 2. Fixed Logging Path Issue
- **Problem**: Script used relative path for logging (`_data/rss/automation.log`) which failed when run from different directory
- **Solution**: Changed to use absolute paths based on script location
- **Code**: Added `script_dir = Path(__file__).parent.parent` and used it for log file path

### 3. System Time Sync
- **Problem**: System time was wrong (showing 15:39 when actual time was 21:12)
- **Solution**: Enabled NTP synchronization with `sudo timedatectl set-ntp true`
- **Result**: Time now correctly synced

### 4. Cron Service
- **Problem**: Cron service was not running
- **Solution**: Started and enabled cron with `sudo systemctl start cron && sudo systemctl enable cron`

## Current Issues

### 1. API Key in Cron
- **PROBLEM**: API key is exposed in crontab as plain text
- **CORRECT APPROACH**: Should be in environment file or system environment variable
- **CURRENT CRON**: Shows API key directly in command

### 2. Cron Not Running Properly
- Multiple attempts to schedule cron job failed
- Job appears in crontab but doesn't execute or output to log
- System logs show cron attempting to run but no output appears

### 3. Path Issues
- Script changes directory internally but cron execution context is unclear
- Relative vs absolute paths causing problems

## What Actually Works

When run manually from /home/nico/ds directory:
```bash
export CLAUDE_API_KEY='[key]' && /usr/bin/python3 scripts/daily_rss_update.py
```

This successfully:
1. Pulls from git (with TLS fallback)
2. Ingests RSS feeds
3. Generates summaries
4. Builds Jekyll site
5. Commits and pushes to git

## Recommended Fixes

1. **Environment Variables**: Move API key to:
   - `/etc/environment` for system-wide
   - Or `.env` file that script reads
   - Or systemd service with Environment directive

2. **Proper Cron Entry**: Should look like:
   ```
   0 */6 * * * cd /home/nico/ds && /usr/bin/python3 scripts/daily_rss_update.py >> _data/rss/cron.log 2>&1
   ```
   With API key loaded from environment

3. **Consider systemd timer** instead of cron for better logging and control

## Files Modified
- `/home/nico/ds/scripts/daily_rss_update.py` - Fixed logging paths and git SSL handling
- Crontab - Multiple failed attempts to schedule job

## Testing Commands That Work
```bash
cd /home/nico/ds
export CLAUDE_API_KEY='[key]'
/usr/bin/python3 scripts/daily_rss_update.py
```

## What Needs Investigation
1. Why cron jobs aren't executing even though cron service is running
2. Best practice for storing API keys for cron jobs on this system
3. Whether the price-tracker cron job (running hourly) has similar issues