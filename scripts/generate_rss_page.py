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
    def __init__(self, data_dir='_data/rss', page_path='rss-feeds.md'):
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
        
        if include_description and article.get('description'):
            return f"""        <article class="feed-item border-bottom py-3">
            <div class="row">
                <div class="col-md-12">
                    <h5 class="item-title">
                        <a href="{article.get('link', '#')}" class="text-dark">{article['title']}</a>
                        <span class="source-badge">{article['source']}</span>
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
                <a href="{article.get('link', '#')}" class="text-dark">{article['title']}</a>
                <span class="source-badge">{article['source']}</span>
            </h6>
            <small class="text-muted">
                <i class="far fa-clock"></i> {time_ago}
            </small>
        </article>"""
    
    def format_claude_summary(self, summary_text):
        """Format Claude summary for HTML"""
        if not summary_text or summary_text == "No new articles today.":
            return """            <p class="lead">No new Zendesk updates today. Check back tomorrow for the latest platform developments.</p>"""
        
        # Convert markdown-style formatting to HTML
        html = summary_text
        
        # Convert **bold** to <strong>
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
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
    
    def generate_page_content(self, articles, summaries, stats):
        """Generate the complete RSS feeds page content"""
        now = datetime.now()
        today_str = now.strftime("%d %B %Y") 
        yesterday_str = (now - timedelta(days=1)).strftime("%d %B %Y")
        
        # Week range
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        week_str = f"{week_start.strftime('%d')}-{week_end.strftime('%d %B %Y')}"
        
        content = f"""---
layout: page
title: Industry RSS Feeds
background: grey
---

<div class="row">
    <div class="col-lg-12">
        <p class="text-muted text-center mb-4">Daily and weekly summaries of Zendesk ecosystem news, curated and analysed.</p>
    </div>
</div>

<!-- Today's Summary (Generated by Claude) -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-calendar-day text-primary"></i>
        Today - {today_str}
        <span class="badge badge-primary ml-2">{stats['today_count']} articles</span>
    </h2>
    
    <div class="claude-summary mb-4">
        <div class="summary-header">
            <h4><i class="fas fa-robot text-info"></i> AI Summary</h4>
            <small class="text-muted">Generated at {now.strftime('%H:%M')} this morning</small>
        </div>
        <div class="summary-content">
{self.format_claude_summary(summaries.get('daily', ''))}
        </div>
    </div>

    <div class="date-articles">
"""
        
        # Today's articles
        today_articles = articles['today'][:5]  # Limit to 5 most recent
        for i, article in enumerate(today_articles):
            include_desc = i == 0  # Only first article gets description
            content += self.format_article_html(article, include_desc) + "\n"
        
        if not today_articles:
            content += """        <div class="alert alert-light">
            <i class="fas fa-info-circle text-muted"></i>
            No new articles today. Check back later for updates.
        </div>
"""
        
        content += """    </div>
</div>

<!-- Yesterday's Summary -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-calendar-alt text-secondary"></i>
        Yesterday - """ + yesterday_str + f"""
        <span class="badge badge-secondary ml-2">{stats['yesterday_count']} articles</span>
    </h2>
    
    <div class="collapsed-articles">
        <small class="text-muted">
            <a href="#" data-toggle="collapse" data-target="#yesterday-list" class="text-decoration-none">
                <i class="fas fa-chevron-right"></i> Show {stats['yesterday_count']} articles from yesterday
            </a>
        </small>
        <div class="collapse" id="yesterday-list">
"""
        
        # Yesterday's articles
        for article in articles['yesterday'][:8]:
            content += f"""            <article class="feed-item border-bottom py-2 mt-3">
                <h6 class="item-title">
                    <a href="{article.get('link', '#')}" class="text-dark">{article['title']}</a>
                    <span class="source-badge">{article['source']}</span>
                </h6>
                <small class="text-muted"><i class="far fa-clock"></i> {self.format_time_ago(article.get('pub_date', ''))}</small>
            </article>
"""
        
        content += f"""        </div>
    </div>
</div>

<!-- This Week's Summary -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-calendar-week text-success"></i>
        This Week - {week_str}
        <span class="badge badge-success ml-2">{stats['week_count']} articles</span>
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
                <i class="fas fa-chevron-right"></i> Show all {stats['week_count']} articles from this week
            </a>
        </small>
        <div class="collapse" id="week-list">
            <div class="mt-3">
                <small class="text-muted">Articles grouped by day - click to expand individual days</small>
            </div>
        </div>
    </div>
</div>

<!-- Stats Summary -->
<div class="row mt-5">
    <div class="col-lg-12">
        <div class="alert alert-info">
            <h6><i class="fas fa-chart-line"></i> Feed Analytics</h6>
            <div class="row text-center">
                <div class="col-md-3">
                    <strong>{stats['week_count']}</strong><br>
                    <small class="text-muted">Articles This Week</small>
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
                    <strong>Tomorrow 09:00</strong><br>
                    <small class="text-muted">Next Update</small>
                </div>
            </div>
        </div>
    </div>
</div>"""
        
        return content
    
    def update_page(self):
        """Update the RSS feeds page with new content"""
        articles, summaries, stats = self.load_data()
        
        print("Generating RSS feeds page...")
        content = self.generate_page_content(articles, summaries, stats)
        
        # Write to file
        with open(self.page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"RSS feeds page updated: {self.page_path}")
        print(f"  Today: {stats['today_count']} articles")
        print(f"  Total this week: {stats['week_count']} articles")
        
        return stats

if __name__ == '__main__':
    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    generator = RSSPageGenerator()
    stats = generator.update_page()