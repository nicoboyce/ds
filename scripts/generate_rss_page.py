#!/usr/bin/env python3
"""
Generate RSS feeds page from ingested articles and Claude summaries
Updates the Jekyll markdown with fresh content
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys
import re

class RSSPageGenerator:
    def __init__(self, data_dir='_data/rss', page_path='news.md'):
        self.data_dir = Path(data_dir)
        self.page_path = Path(page_path)
        
    def load_data(self):
        """Load articles, summaries, and stats"""
        try:
            with open(self.data_dir / 'categorised.json', 'r') as f:
                articles = json.load(f)
            
            with open(self.data_dir / 'summaries.json', 'r') as f:
                summaries = json.load(f)
                
            with open(self.data_dir / 'stats.json', 'r') as f:
                stats = json.load(f)
                
            return articles, summaries, stats
        except FileNotFoundError as e:
            print(f"ERROR: Required data file not found: {e}")
            sys.exit(1)
    
    def format_time_ago(self, pub_date_str):
        """Convert publication date to human-readable time ago"""
        try:
            # Handle various date formats
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S']:
                try:
                    pub_date = datetime.strptime(pub_date_str.split('+')[0].split('-')[0].strip(), fmt.split('%z')[0].strip())
                    break
                except:
                    continue
            else:
                return "recently"
            
            now = datetime.now()
            diff = now - pub_date
            
            if diff.days == 0:
                hours = diff.seconds // 3600
                if hours == 0:
                    minutes = diff.seconds // 60
                    return f"{minutes} minutes ago" if minutes > 1 else "1 minute ago"
                return f"{hours} hours ago" if hours > 1 else "1 hour ago"
            elif diff.days == 1:
                return "yesterday"
            else:
                return f"{diff.days} days ago"
                
        except:
            return "recently"
    
    def format_article_html(self, article, include_description=False):
        """Format article as HTML"""
        time_ago = self.format_time_ago(article.get('pub_date', ''))
        source = article.get('source', '')
        link = article.get('link', '#')
        
        # Extract direct URL from Google News redirects
        if 'Google News' in source and 'news.google.com/rss/articles/' in link:
            # Google News URLs are redirects, but we can't easily extract the real URL
            # Just use the Google redirect for now
            pass
        
        # Format source badge based on source type
        source_badge = ''
        if source == 'Internal Note':
            # Make Internal Note badge clickable to the website
            source_badge = '<a href="https://internalnote.com" target="_blank" class="source-badge text-white">Internal Note</a>'
        elif 'Google News' not in source:
            # Show badge for all sources except Google News
            source_badge = f'<span class="source-badge">{source}</span>'
        # Else: Google News articles don't get a badge
        
        if include_description and article.get('description'):
            return f"""        <article class="feed-item border-bottom py-3">
            <div class="row">
                <div class="col-md-12">
                    <h5 class="item-title">
                        <a href="{link}" class="text-dark">{article['title']}</a>
                        {source_badge}
                    </h5>
                    <p class="item-summary text-muted">
                        {article['description']}
                    </p>
                    <small class="text-muted">
                        <i class="far fa-clock"></i> {time_ago}
                    </small>
                </div>
            </div>
        </article>"""
        else:
            return f"""        <article class="feed-item border-bottom py-3">
            <h6 class="item-title">
                <a href="{link}" class="text-dark">{article['title']}</a>
                {source_badge}
            </h6>
            <small class="text-muted">
                <i class="far fa-clock"></i> {time_ago}
            </small>
        </article>"""
    
    def format_claude_summary(self, summary_text, articles=None):
        """Format Claude summary for HTML"""
        if not summary_text or summary_text == "No new articles today.":
            return """            <p class="lead">No new Zendesk updates today. Check back tomorrow for the latest platform developments.</p>"""
        
        # Convert markdown-style formatting to HTML
        html = summary_text
        
        # Convert **bold** to <strong>
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Check if this is a security alert and make it clickable
        if articles and '**Security**:' in summary_text:
            # Find the security article
            for article in articles:
                title = article.get('title', '')
                if ('security' in title.lower() or 'vulnerability' in title.lower() or 
                    '0-click' in title.lower() or 'flaw' in title.lower()):
                    # Extract the security part and make it a link
                    security_match = re.search(r'<strong>Security</strong>: (.*?)(?:\s*-\s*CyberSecurityNews|\s*-\s*GBHackers.*?)?$', html)
                    if security_match:
                        security_text = security_match.group(1).strip()
                        link = self.get_direct_url(article)
                        # Replace the security text with a linked version
                        html = html.replace(
                            f'<strong>Security</strong>: {security_text}',
                            f'<strong>Security</strong>: <a href="{link}" target="_blank" class="alert-link">{security_text}</a>'
                        )
                    break
        
        # Convert bullet points to HTML list
        lines = html.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('- **') or line.startswith('• **'):
                if not in_list:
                    formatted_lines.append('<ul class="summary-points">')
                    in_list = True
                formatted_lines.append(f'<li>{line[2:].strip()}</li>')
            elif line.startswith('**') and line.endswith('**'):
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(f'<p class="lead">{line}</p>')
            elif line.startswith('**Strategic Insight**') or line.startswith('**Key Insight**'):
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(f'<p class="summary-insight"><em>{line}</em></p>')
            elif line:
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(f'<p>{line}</p>')
        
        if in_list:
            formatted_lines.append('</ul>')
        
        return '\n            '.join(formatted_lines)
    
    def generate_release_notes_panel(self, summaries):
        """Generate the dedicated release notes panel"""
        release_notes = summaries.get('release_notes', {})
        
        if not release_notes or not release_notes.get('summary'):
            return ""
        
        article = release_notes.get('article', {})
        summary = release_notes.get('summary', '')
        title = article.get('title', '').replace('Release notes through ', '')
        link = article.get('link', '#')
        
        return f"""<!-- Latest Zendesk Release Notes -->
<div class="release-notes-panel mb-4">
    <div class="card border-primary">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0">
                <i class="fas fa-clipboard-list"></i> Latest Zendesk Release Notes
                <span class="float-right badge badge-light">{title}</span>
            </h5>
        </div>
        <div class="card-body">
            <p class="mb-2"><strong>Key Changes:</strong> {summary}</p>
            <a href="{link}" class="btn btn-sm btn-outline-primary" target="_blank">
                <i class="fas fa-external-link-alt"></i> View Full Release Notes
            </a>
        </div>
    </div>
</div>
"""
    
    def get_direct_url(self, article):
        """Try to get direct URL for security articles"""
        title = article.get('title', '')
        source = article.get('source', '')
        link = article.get('link', '')
        
        # For security articles from Google News, try to use direct site
        if 'security' in title.lower() or 'vulnerability' in title.lower() or '0-click' in title.lower():
            if 'CyberSecurityNews' in title:
                # We can't easily extract the real URL, but we know it's from cybersecuritynews.com
                # For now, just return the Google redirect
                return link
            elif 'GBHackers' in title:
                return link
        
        return link
    
    def generate_page_content(self, articles, summaries, stats):
        """Generate the complete RSS feeds page content"""
        now = datetime.now()
        today_str = now.strftime("%d %B %Y") 
        archive_date = now.strftime('%Y-%m-%d')
        archive_url = f"https://deltastring.com/news-{archive_date}/"
        
        # Recalculate stats excluding release notes
        def exclude_release_notes(article_list):
            return [a for a in article_list if 'Release notes through' not in a.get('title', '')]
        
        filtered_stats = {
            'latest_count': len(exclude_release_notes(articles.get('latest', []))),
            'week_count': len(exclude_release_notes(articles.get('this_week', []))),
            'month_count': len(exclude_release_notes(articles.get('this_month', [])))
        }
        
        
        content = f"""---
layout: page
title: Zendesk news, from Deltastring
background: grey
---

<link rel="stylesheet" href="/assets/css/rss-feeds.css">

<div class="row">
    <div class="col-lg-12">
        <p class="text-muted text-center mb-4">Daily and weekly summaries of Zendesk ecosystem news, curated and analysed.</p>
    </div>
</div>

{self.generate_release_notes_panel(summaries)}

{{% include nicos-commentary.html %}}

<!-- Latest Summary (Last 48 Hours) -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-clock text-primary"></i>
        Latest - Last 48 Hours
        <span class="badge badge-primary ml-2">{filtered_stats['latest_count']} articles</span>
    </h2>
    
    <div class="claude-summary mb-4">
        <div class="summary-header">
            <h4><i class="fas fa-robot text-info"></i> AI Summary</h4>
            <small class="text-muted">Generated at {now.strftime('%H:%M')} today | <a href="/news-{archive_date}/">Permanent link</a></small>
        </div>
        <div class="summary-content">
{self.format_claude_summary(summaries.get('latest', summaries.get('daily', '')), articles.get('latest', []))}
        </div>
        <div class="share-buttons mt-2">
            <small>Share: 
                <a href="mailto:?subject=Zendesk%20Latest%20Updates%20-%20{today_str.replace(' ', '%20')}&body=Check%20out%20today's%20Zendesk%20updates%20at%20{archive_url}" class="text-muted mx-1"><i class="fas fa-envelope"></i> Email</a>
                <a href="https://www.linkedin.com/sharing/share-offsite/?url={archive_url}" class="text-muted mx-1" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a>
                <a href="#" onclick="navigator.clipboard.writeText('Zendesk Updates {today_str}: {archive_url}'); alert('Copied to clipboard!'); return false;" class="text-muted mx-1"><i class="fas fa-copy"></i> Copy</a>
            </small>
        </div>
    </div>

    <div class="date-articles">
"""
        
        # Latest articles (48h) - excluding release notes since they have their own panel
        all_latest = articles.get('latest', articles.get('today', []))
        latest_articles = [a for a in all_latest if 'Release notes through' not in a.get('title', '')][:10]  # Filter release notes
        for i, article in enumerate(latest_articles):
            include_desc = i == 0  # Only first article gets description
            content += self.format_article_html(article, include_desc) + "\n"
        
        if not latest_articles:
            content += """        <div class="alert alert-light">
            <i class="fas fa-info-circle text-muted"></i>
            No new articles in the last 48 hours. Check back later for updates.
        </div>
"""
        
        content += f"""    </div>
</div>

<!-- This Week's Summary -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-calendar-week text-success"></i>
        This Week
        <span class="badge badge-success ml-2">{filtered_stats['week_count']} articles</span>
    </h2>
    
    <div class="claude-summary mb-4">
        <div class="summary-header">
            <h4><i class="fas fa-robot text-info"></i> Weekly AI Analysis</h4>
            <small class="text-muted">Generated this morning</small>
        </div>
        <div class="summary-content">
{self.format_claude_summary(summaries.get('weekly', ''))}
        </div>
    </div>

    <div class="collapsed-articles">
        <small class="text-muted">
            <a href="#" data-toggle="collapse" data-target="#week-list" class="text-decoration-none">
                <i class="fas fa-chevron-right"></i> Show all {filtered_stats['week_count']} articles from this week
            </a>
        </small>
        <div class="collapse" id="week-list">
"""  
        # Add week articles - excluding release notes
        week_filtered = exclude_release_notes(articles.get('this_week', []))
        for article in week_filtered[:20]:  # Show up to 20 articles
            source_badge = ''
            if article['source'] == 'Internal Note':
                source_badge = '<a href="https://internalnote.com" target="_blank" class="source-badge text-white">Internal Note</a>'
            elif 'Google News' not in article['source']:
                source_badge = f'<span class="source-badge">{article["source"]}</span>'
            
            content += f"""            <article class="feed-item border-bottom py-2 mt-3">
                <h6 class="item-title">
                    <a href="{article.get('link', '#')}" class="text-dark">{article['title']}</a>
                    {source_badge}
                </h6>
                <small class="text-muted"><i class="far fa-clock"></i> {self.format_time_ago(article.get('pub_date', ''))}</small>
            </article>
"""
        
        content += f"""        </div>
    </div>
</div>

<!-- This Month's Summary -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-calendar text-info"></i>
        This Month
        <span class="badge badge-info ml-2">{filtered_stats['month_count']} articles</span>
    </h2>
    
    <div class="collapsed-articles">
        <small class="text-muted">
            <a href="#" data-toggle="collapse" data-target="#month-list" class="text-decoration-none">
                <i class="fas fa-chevron-right"></i> Show {filtered_stats['month_count']} articles from this month
            </a>
        </small>
        <div class="collapse" id="month-list">
"""  
        # Add month articles - excluding release notes
        month_filtered = exclude_release_notes(articles.get('this_month', []))
        for article in month_filtered[:30]:  # Show up to 30 articles
            source_badge = ''
            if article['source'] == 'Internal Note':
                source_badge = '<a href="https://internalnote.com" target="_blank" class="source-badge text-white">Internal Note</a>'
            elif 'Google News' not in article['source']:
                source_badge = f'<span class="source-badge">{article["source"]}</span>'
            
            content += f"""            <article class="feed-item border-bottom py-2 mt-3">
                <h6 class="item-title">
                    <a href="{article.get('link', '#')}" class="text-dark">{article['title']}</a>
                    {source_badge}
                </h6>
                <small class="text-muted"><i class="far fa-clock"></i> {self.format_time_ago(article.get('pub_date', ''))}</small>
            </article>
"""
        
        content += f"""        </div>
    </div>
</div>

<!-- Stats Summary -->
<div class="row mt-5">
    <div class="col-lg-12">
        <div class="alert alert-info">
            <h6><i class="fas fa-chart-line"></i> Feed Analytics</h6>
            <div class="row text-center">
                <div class="col-md-3">
                    <strong>{stats['total_articles']}</strong><br>
                    <small class="text-muted">Total Articles</small>
                </div>
                <div class="col-md-3">
                    <strong>{stats['feeds_processed']}</strong><br>
                    <small class="text-muted">RSS Sources</small>
                </div>
                <div class="col-md-3">
                    <strong>{now.strftime('%d/%m/%Y')}</strong><br>
                    <small class="text-muted">Last Updated</small>
                </div>
                <div class="col-md-3">
                    <strong>Tomorrow 09:00 UTC</strong><br>
                    <small class="text-muted">Next Update</small>
                </div>
            </div>
        </div>
    </div>
</div>"""
        
        return content
    
    def create_archive(self, articles, summaries, stats):
        """Create a daily archive of the news page"""
        now = datetime.now()
        archive_date = now.strftime('%Y-%m-%d')
        archive_file = Path(f'news-{archive_date}.md')
        
        # Generate archive content (same as regular but with archive notice)
        content = self.generate_page_content(articles, summaries, stats)
        
        # Add archive header
        archive_header = f"""---
layout: page
title: Industry RSS Feeds - {now.strftime('%d %B %Y')} Archive
background: grey
---

<link rel="stylesheet" href="/assets/css/rss-feeds.css">

<div class="alert alert-warning mb-4">
    <i class="fas fa-archive"></i> This is an archived version from {now.strftime('%d %B %Y')}. 
    <a href="/news/">View latest updates</a>
</div>

"""
        
        # Write archive file
        with open(archive_file, 'w') as f:
            f.write(archive_header + content)
        
        print(f"Archive created: {archive_file.name}")
    
    def update_page(self):
        """Update the RSS feeds page with new content"""
        articles, summaries, stats = self.load_data()
        
        print("Generating RSS feeds page...")
        content = self.generate_page_content(articles, summaries, stats)
        
        # Create daily archive
        self.create_archive(articles, summaries, stats)
        
        # Write to file
        with open(self.page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"News page updated: {self.page_path}")
        print(f"  Latest (48h): {stats['latest_count']} articles")
        print(f"  This week (3-7d): {stats['week_count']} articles")
        print(f"  This month (8-35d): {stats.get('month_count', 0)} articles")
        
        return stats

if __name__ == '__main__':
    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    generator = RSSPageGenerator()
    stats = generator.update_page()