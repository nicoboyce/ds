#!/usr/bin/env python3
"""
One-time script to update existing archive files with SEO improvements
Updates titles, adds meta descriptions, canonicals, and freshness for recent files
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

def update_archive_file(file_path):
    """Update a single archive file with SEO improvements"""
    # Extract date from filename
    date_match = re.search(r'news-(\d{4}-\d{2}-\d{2})\.md', file_path.name)
    if not date_match:
        return False

    archive_date = date_match.group(1)
    page_date = datetime.strptime(archive_date, '%Y-%m-%d')
    days_old = (datetime.now() - page_date).days

    # Read content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Update title based on age
    display_date = page_date.strftime('%d %B %Y')
    if days_old <= 7:
        new_title = f'Zendesk News Today - {display_date} | Deltastring'
    else:
        new_title = f'Zendesk News Archive - {display_date} | Deltastring'

    # Replace old title patterns
    content = re.sub(
        r'title:\s*["\']?Industry RSS Feeds - .+?["\']?\s*\n',
        f'title: "{new_title}"\n',
        content
    )
    content = re.sub(
        r'title:\s*["\']?Zendesk news, from Deltastring["\']?\s*\n',
        f'title: "{new_title}"\n',
        content
    )

    # Add meta description if missing
    meta_desc = f'Latest Zendesk news and platform updates for {display_date}. Service incidents, product announcements, and industry developments updated today.'

    if 'description:' not in content:
        # Insert after title line
        content = re.sub(
            r'(title: "[^"]+"\n)',
            f'\\1date: {archive_date}\n',
            content
        )
        content = re.sub(
            r'(date: \d{4}-\d{2}-\d{2}\n)',
            f'\\1description: "{meta_desc}"\n',
            content
        )

    # Add canonical for old pages (older than 2 days)
    if days_old > 2 and 'rel="canonical"' not in content:
        canonical_tag = '<link rel="canonical" href="https://deltastring.com/news/" />\n'

        # Insert after frontmatter
        content = re.sub(
            r'(---\n)(.*?)(\n---\n)',
            f'\\1\\2\\3\n{canonical_tag}',
            content,
            count=1,
            flags=re.DOTALL
        )

    # Update archive notice styling based on age
    if days_old <= 7:
        # Recent pages get info styling
        content = re.sub(
            r'<div class="alert alert-warning mb-4">\s*<i class="fas fa-archive"></i>',
            f'<div class="alert alert-info mb-4">\n    <i class="fas fa-clock"></i> <strong>Viewing news from {display_date}</strong><br>\n    <a href="/news/" class="alert-link">View today\'s latest Zendesk news</a>\n</div>\n<div class="alert alert-info mb-4" style="display:none;">\n    <i class="fas fa-archive"></i>',
            content
        )

    # Update dateModified in schema for recent pages
    if days_old <= 7:
        iso_now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        content = re.sub(
            r'"dateModified":\s*"[^"]*"',
            f'"dateModified": "{iso_now}"',
            content
        )

    # Add visible "Last updated" timestamp if missing
    if 'Last updated:' not in content and days_old <= 7:
        now_display = datetime.now().strftime('%H:%M GMT, %d %B %Y')
        content = re.sub(
            r'(<p class="text-muted text-center mb-4">.*?</p>)',
            f'\\1\n        <p class="text-muted text-center small mb-4">\n            <i class="far fa-clock"></i> Last updated: {now_display}\n        </p>',
            content,
            count=1
        )

    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False

def main():
    """Update all existing archive files"""
    archive_files = list(Path('.').glob('news-2025-*.md'))

    print(f"Found {len(archive_files)} archive files")
    updated = 0

    for file_path in sorted(archive_files):
        try:
            if update_archive_file(file_path):
                print(f"✓ Updated: {file_path.name}")
                updated += 1
            else:
                print(f"- No changes: {file_path.name}")
        except Exception as e:
            print(f"✗ Error updating {file_path.name}: {e}")

    print(f"\nUpdated {updated}/{len(archive_files)} files")

if __name__ == '__main__':
    main()
