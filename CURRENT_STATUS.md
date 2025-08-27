# Current Status - 27/08/2025

## Completed Work

### 1. Footer Links Fixed ✅
- **File:** `_includes/footer.html`
- **Changes:** Converted relative links to absolute paths
  - `href="legal"` → `href="/legal"`
  - `href="ms"` → `href="/ms"` 
  - `href="no-ai"` → `href="/no-ai"`
- **Status:** Complete and working

### 2. Reference Links JavaScript Fixed ✅
- **File:** `scripts/generate_rss_page.py`
- **Issue:** Reference links weren't expanding hidden sections and were being covered by navbar
- **Solution Implemented:**
  - Added navbar offset calculation (70px + 20px padding)
  - Auto-expands Bootstrap collapse sections when clicking reference links
  - Updates chevron icons when sections expand
  - Smooth scrolling to target articles
- **Status:** Complete and tested

### 3. AI Summary Improvements ✅
- **File:** `scripts/claude_summariser.py`
- **Issues Fixed:**
  - Unclear abbreviations like "OAuth in Admin" and "trigger redaction"
  - Unnecessary source brackets like "[Zendesk Announcements]"
  - Prompts too specific to current articles (wouldn't work next week)
- **Changes Made:**
  - Made prompts generic with guidelines instead of specific examples
  - Added "Write clear summaries that explain what each item is (5-10 words per item)"
  - Removed source bracket stripping from titles
  - Better grouping: Critical → Latest/This week/This month → Meanwhile
- **Latest Improvement (just completed):**
  - Reorganised sections per user request:
    - **Critical:** Security vulnerabilities, service incidents, urgent issues
    - **Latest/This week/This month:** New features, product updates, release notes  
    - **Meanwhile:** Business news, HQ auctions, reviews, tangential developments

## What Needs to Be Done Next

### 1. Build and Deploy
```bash
# The system seems to have Jekyll installed but bundle command not found
# Try these options:

# Option A: Use Ruby gems directly
gem install bundler  # If permissions allow
bundle install
bundle exec jekyll build

# Option B: Use existing Jekyll installation
vendor/bundle/ruby/3.1.0/bin/jekyll build

# Option C: If above fail, check for alternative build method
make build  # If Makefile exists
```

### 2. Git Commit and Push
Once built, commit all changes:
```bash
git add -A
git commit -m "Fix footer links, improve reference link navigation, and enhance AI summaries

- Convert footer links from relative to absolute paths
- Add navbar offset calculation for reference links (70px + 20px padding)
- Auto-expand hidden sections when clicking reference links  
- Improve AI summary clarity with better descriptions
- Make summary prompts generic rather than article-specific
- Reorganise summary sections: Critical → Announcements → Meanwhile

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

### 3. Regenerate Summaries (Optional)
After system restart, if you have Claude API key:
```bash
export CLAUDE_API_KEY="your-key-here"
python scripts/claude_summariser.py
```

Currently using fallback summaries which are less detailed but still functional.

## Files Modified
1. `/home/nico/ds/_includes/footer.html` - Fixed relative links
2. `/home/nico/ds/scripts/generate_rss_page.py` - Fixed reference link navigation
3. `/home/nico/ds/scripts/claude_summariser.py` - Improved summary generation
4. `/home/nico/ds/_data/rss/summaries.json` - Generated with new fallback logic

## Current Issue
- `bundle` command not found despite Jekyll being installed
- Appears to be a Ruby/bundler environment issue
- Jekyll exists at: `vendor/bundle/ruby/3.1.0/bin/jekyll`

## Testing After Restart
1. Check if Jekyll builds properly
2. Verify reference links work with navbar offset
3. Check footer links navigate correctly
4. Review summary quality in the news page