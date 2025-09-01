#!/usr/bin/env python3
"""
Generate RSS feeds page from ingested articles and Claude summaries
Updates the Jekyll markdown with fresh content

Now includes article deduplication and topic categorisation for better
organisation of Zendesk news content.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys
import re

# Import the deduplicator for article processing
from article_deduplicator import ArticleDeduplicator

class RSSPageGenerator:
    def __init__(self, data_dir='_data/rss', page_path='news.md'):
        self.data_dir = Path(data_dir)
        self.page_path = Path(page_path)
        # Initialise the deduplicator
        self.deduplicator = ArticleDeduplicator(self.data_dir)
        
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
    
    def format_deduplicated_article_html(self, article, include_description=False):
        """
        Format HTML for a deduplicated article with source count indicator.
        
        Args:
            article: Deduplicated article dictionary with source_count
            include_description: Whether to include article description
            
        Returns:
            HTML string for the article
        """
        time_ago = self.format_time_ago(article.get('pub_date', ''))
        link = article.get('link', '#')
        source = article.get('source', 'Unknown')
        source_count = article.get('source_count', 1)
        
        # Format source badge with count if multiple sources
        source_badge = ''
        if source == 'Internal Note':
            source_badge = '<a href="https://internalnote.com" target="_blank" class="source-badge text-white">Internal Note</a>'
        elif 'Google News' not in source:
            source_badge = f'<span class="source-badge">{source}</span>'
        
        # Add source count indicator if multiple sources
        source_indicator = ''
        if source_count > 1:
            sources_list = ', '.join(article.get('sources', []))
            source_indicator = f' <small class="text-info" title="{sources_list}">[{source_count} sources]</small>'
        
        # Add update indicator if this is an updated story
        update_indicator = ''
        if article.get('is_update'):
            update_indicator = ' <span class="badge badge-warning ml-2">Updated</span>'
        
        if include_description and article.get('description'):
            return f"""        <article class="feed-item border-bottom py-3">
            <div class="row">
                <div class="col-md-12">
                    <h5 class="item-title">
                        <a href="{link}" class="text-dark">{article['title']}</a>
                        {source_badge}{source_indicator}{update_indicator}
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
                {source_badge}{source_indicator}{update_indicator}
            </h6>
            <small class="text-muted">
                <i class="far fa-clock"></i> {time_ago}
            </small>
        </article>"""

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
    
    def convert_references_to_links(self, summary_text, articles, section_id):
        """Convert [N] references to HTML links pointing to specific articles"""
        if not articles:
            return summary_text
        
        import re
        
        # First handle combined references like [1,2] by splitting them  
        combined_refs = re.findall(r'\[(\d+(?:,\d+)+)\]', summary_text)
        for combined in combined_refs:
            refs = combined.split(',')
            # Replace with individual linked references but check bounds
            valid_refs = [r for r in refs if int(r) <= len(articles)]
            if valid_refs:
                replacement = ', '.join([f'<a href="#{section_id}-article-{r}" class="ref-link" data-section="{section_id}">[{r}]</a>' 
                                        for r in valid_refs])
            else:
                replacement = f'[{combined}]'  # Keep original if no valid refs
            summary_text = summary_text.replace(f'[{combined}]', replacement)
        
        # Convert each single [N] reference to a link
        def replace_ref(match):
            ref_num = int(match.group(1))
            if ref_num <= len(articles):
                article_id = f"{section_id}-article-{ref_num}"
                return f'<a href="#{article_id}" class="ref-link" data-section="{section_id}">[{ref_num}]</a>'
            return match.group(0)
        
        # Replace all single [N] patterns
        result = re.sub(r'\[(\d+)\]', replace_ref, summary_text)
        return result
    
    def format_claude_summary(self, summary_text, articles=None, section_id='latest'):
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
        current_section = None
        section_items = []
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers (Critical:, Latest:, This week:, This month:, Meanwhile:)
            if line in ['Critical:', 'Latest:', 'This week:', 'This month:', 'Meanwhile:']:
                # Output previous section if exists
                if current_section and section_items:
                    formatted_lines.append(f'<p><strong>{current_section}</strong> {" ".join(section_items)}</p>')
                    section_items = []
                current_section = line[:-1]  # Remove colon
                continue
                
            # If we're in a section, collect items
            if current_section:
                if line:
                    section_items.append(line)
            # Original bullet point handling
            elif line.startswith('- **') or line.startswith('• **'):
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
        
        # Output last section if exists
        if current_section and section_items:
            formatted_lines.append(f'<p><strong>{current_section}</strong> {" ".join(section_items)}</p>')
        
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
            <div class="card-header text-white d-flex align-items-center justify-content-between blended-gradient-container" data-start="#D4914A" data-end="#1C5AA3" data-blend="60" data-direction="to left" style="height: 60px;">
            <div class="d-flex align-items-center">
                <i class="fas fa-clipboard-list mr-2"></i>
                <h5 class="mb-0">Latest Zendesk Release Notes</h5>
            </div>
            <span class="badge badge-light">{title}</span>
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
    
    def generate_dont_miss(self, articles):
        """
        Generate the "Don't Miss" highlight - the most significant item from the recent period.
        
        Args:
            articles: Dictionary of articles by timeframe
            
        Returns:
            HTML string for the Don't Miss section
        """
        # Combine recent articles
        recent = []
        recent.extend(articles.get('this_week', []))
        recent.extend(articles.get('this_month', [])[:20])
        
        if not recent:
            return "<p class='text-muted'>No significant updates in the recent period.</p>"
        
        # Prioritise by significance
        # 1. Security vulnerabilities
        # 2. Major feature announcements (EAPs, new capabilities)
        # 3. Breaking changes/deprecations
        # 4. Service incidents with wide impact
        
        dont_miss = None
        
        for article in recent:
            title_lower = article.get('title', '').lower()
            
            # Security always wins
            if 'vulnerability' in title_lower or 'security' in title_lower:
                dont_miss = article
                break
                
            # Major features
            if 'eap' in title_lower or 'early access' in title_lower:
                if not dont_miss:
                    dont_miss = article
                    
            # OAuth/Auth changes are critical
            if 'oauth' in title_lower or 'authentication' in title_lower:
                if not dont_miss or 'eap' not in dont_miss.get('title', '').lower():
                    dont_miss = article
                    
        # Default to first article if nothing special found
        if not dont_miss and recent:
            dont_miss = recent[0]
            
        # Format the highlight
        if dont_miss:
            link = dont_miss.get('link', '#')
            title = dont_miss['title']
            source = dont_miss.get('source', '')
            time_ago = self.format_time_ago(dont_miss.get('pub_date', ''))
            
            # Add context about why this matters
            context = ""
            title_lower = title.lower()
            if 'oauth' in title_lower or 'authentication' in title_lower:
                context = "This fundamentally changes how you'll manage third-party integrations."
            elif 'eap' in title_lower:
                context = "Early access to test upcoming features before general release."
            elif 'vulnerability' in title_lower:
                context = "Critical security issue requiring immediate attention."
            elif 'deprecat' in title_lower:
                context = "Breaking change that may affect your integrations."
            else:
                context = "Significant platform update affecting Zendesk administrators."
                
            return f"""
                <h6><a href="{link}" class="text-dark" target="_blank">{title}</a></h6>
                <p class="mb-2">{context}</p>
                <small class="text-muted">{source} • {time_ago}</small>
            """
            
        return "<p class='text-muted'>No significant updates in the recent period.</p>"
    
    def generate_categorised_section(self, deduplicated_articles, section_title="Latest Updates"):
        """
        Generate HTML for a categorised section with deduplicated articles.
        
        Args:
            deduplicated_articles: Dictionary of categorised, deduplicated articles
            section_title: Title for the section
            
        Returns:
            HTML string for the categorised section
        """
        html = ""
        
        # Process categories in priority order
        category_order = [
            'incidents_security',
            'product_updates', 
            'operations',
            'business',
            'resources'
        ]
        
        for cat_key in category_order:
            if cat_key not in deduplicated_articles or not deduplicated_articles[cat_key]:
                continue
                
            # Get category info
            cat_info = self.deduplicator.CATEGORIES[cat_key]
            cat_name = cat_info['name']
            articles = deduplicated_articles[cat_key]
            
            # Generate category section
            html += f"""
    <div class="category-section mb-4">
        <h5 class="category-title">
            {cat_name}
            <span class="badge badge-secondary ml-2">{len(articles)}</span>
        </h5>
        <div class="category-articles">
"""
            
            # Add articles (first one gets description)
            for i, article in enumerate(articles):
                include_desc = (i == 0 and cat_key == 'incidents_security')  # Only first security item gets description
                html += self.format_deduplicated_article_html(article, include_desc)
                
            html += """        </div>
    </div>
"""
        
        return html
    
    def generate_page_content(self, articles, summaries, stats):
        """Generate the complete RSS feeds page content"""
        now = datetime.now()
        today_str = now.strftime("%d %B %Y") 
        archive_date = now.strftime('%Y-%m-%d')
        archive_url = f"https://deltastring.com/news-{archive_date}/"
        
        # Calculate deduplicated stats
        def get_deduplicated_count(article_list, timeframe):
            filtered = [a for a in article_list if 'Release notes through' not in a.get('title', '')]
            deduped = self.deduplicator.deduplicate_articles(filtered, timeframe)
            return sum(len(arts) for arts in deduped.values())
        
        # Combine week and month for recently count
        recently_combined = []
        recently_combined.extend(articles.get('this_week', []))
        recently_combined.extend(articles.get('this_month', [])[:20])
        
        filtered_stats = {
            'latest_count': get_deduplicated_count(articles.get('latest', []), 'latest'),
            'recently_count': get_deduplicated_count(recently_combined, 'recently'),
            'week_count': get_deduplicated_count(articles.get('this_week', []), 'week'),
            'month_count': get_deduplicated_count(articles.get('this_month', []), 'month')
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

<!-- Latest (Last 48 Hours) -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-clock text-primary"></i>
        Latest - Last 48 Hours
        <span class="badge badge-primary ml-2">{filtered_stats['latest_count']} stories</span>
    </h2>

"""
        
        # Deduplicate and categorise latest articles
        all_latest = articles.get('latest', articles.get('today', []))
        # Filter out release notes as they have their own panel
        latest_filtered = [a for a in all_latest if 'Release notes through' not in a.get('title', '')]
        
        # Run deduplication
        deduplicated_latest = self.deduplicator.deduplicate_articles(latest_filtered, 'latest')
        
        # Generate categorised sections
        content += self.generate_categorised_section(deduplicated_latest, "Latest 48 Hours")
        
        # If no articles at all
        total_articles = sum(len(arts) for arts in deduplicated_latest.values())
        if total_articles == 0:
            content += """        <div class="alert alert-light">
            <i class="fas fa-info-circle text-muted"></i>
            No new articles in the last 48 hours. Check back later for updates.
        </div>
"""
        
        content += f"""
</div>

<!-- Recently (3 weeks prior) -->
<div class="summary-section mb-5">
    <h2 class="summary-title">
        <i class="fas fa-history text-info"></i>
        Recently
        <span class="badge badge-info ml-2">{filtered_stats['recently_count']} stories</span>
    </h2>
    
    <!-- Don't Miss Highlight -->
    <div class="dont-miss mb-4">
        <div class="card border-warning">
            <div class="card-header text-white d-flex align-items-center blended-gradient-container" data-start="#D4914A" data-end="#1C5AA3" data-blend="60" data-direction="to right" style="height: 60px;">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <h5 class="mb-0">Don't Miss</h5>
            </div>
            <div class="card-body">
                {self.generate_dont_miss(articles)}
            </div>
        </div>
    </div>
    
    <!-- AI Narrative Analysis -->
    <div class="claude-summary mb-4">
        <div class="summary-header">
            <h4><i class="fas fa-robot text-info"></i> Analysis</h4>
            <small class="text-muted">Generated this morning</small>
        </div>
        <div class="summary-content">
            {self.format_claude_summary(summaries.get('recently_narrative', ''), None, 'recently')}
        </div>
    </div>
    
    <!-- Collapsed topic-based articles -->
    <div class="collapsed-articles">
        <small class="text-muted">
            <a href="#" data-toggle="collapse" data-target="#recently-list" class="text-decoration-none">
                <i class="fas fa-chevron-right"></i> Show all {filtered_stats['recently_count']} stories by topic
            </a>
        </small>
        <div class="collapse" id="recently-list">
"""  
        # Combine week and month articles for "recently" (3 weeks)
        recently_articles = []
        recently_articles.extend(articles.get('this_week', []))
        recently_articles.extend(articles.get('this_month', [])[:20])  # Limit older articles
        
        # Filter and deduplicate
        recently_filtered = [a for a in recently_articles if 'Release notes through' not in a.get('title', '')]
        deduplicated_recently = self.deduplicator.deduplicate_articles(recently_filtered, 'recently')
        
        # Generate categorised sections within collapse
        content += self.generate_categorised_section(deduplicated_recently, "Recent Updates")
        
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
                    <strong>12:00 (London)</strong><br>
                    <small class="text-muted">Next Update</small>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- JavaScript for reference links -->
<script>
document.addEventListener('DOMContentLoaded', function() {{
    // Handle reference link clicks
    document.querySelectorAll('.ref-link').forEach(link => {{
        link.addEventListener('click', function(e) {{
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {{
                // Function to scroll with navbar offset
                const scrollToElement = () => {{
                    const navbarHeight = document.getElementById('mainNav') ? 
                                         document.getElementById('mainNav').offsetHeight : 70;
                    const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
                    const offsetPosition = elementPosition - navbarHeight - 20; // 20px extra padding
                    
                    window.scrollTo({{
                        top: offsetPosition,
                        behavior: 'smooth'
                    }});
                    
                    // Highlight the article briefly
                    targetElement.style.backgroundColor = '#fff3cd';
                    setTimeout(() => {{
                        targetElement.style.transition = 'background-color 1s';
                        targetElement.style.backgroundColor = '';
                    }}, 1000);
                }};
                
                // Check if element is in a collapsed section
                const collapse = targetElement.closest('.collapse');
                if (collapse && !collapse.classList.contains('show')) {{
                    // Expand the section first
                    $(collapse).collapse('show');
                    
                    // Update chevron icon immediately
                    const toggleLink = document.querySelector(`[data-target="#${{collapse.id}}"]`);
                    if (toggleLink) {{
                        const icon = toggleLink.querySelector('.fa-chevron-right, .fa-chevron-down');
                        if (icon) {{
                            icon.classList.remove('fa-chevron-right');
                            icon.classList.add('fa-chevron-down');
                        }}
                    }}
                    
                    // Wait for animation to complete then scroll
                    setTimeout(scrollToElement, 400);
                }} else {{
                    // Already visible, just scroll
                    scrollToElement();
                }}
            }}
        }});
    }});
    
    // Update chevron icons when collapsing/expanding
    $('.collapse').on('show.bs.collapse', function() {{
        $(this).parent().find('.fa-chevron-right').first()
            .removeClass('fa-chevron-right')
            .addClass('fa-chevron-down');
    }});
    
    $('.collapse').on('hide.bs.collapse', function() {{
        $(this).parent().find('.fa-chevron-down').first()
            .removeClass('fa-chevron-down')
            .addClass('fa-chevron-right');
    }});
}});
</script>

<style>
.ref-link {{
    color: #007bff;
    text-decoration: none;
    font-weight: 600;
}}
.ref-link:hover {{
    text-decoration: underline;
}}
</style>"""
        
        return content
    
    def create_archive(self, articles, summaries, stats):
        """Create a daily archive of the news page"""
        now = datetime.now()
        archive_date = now.strftime('%Y-%m-%d')
        archive_file = Path(f'news-{archive_date}.md')
        
        # Generate archive content (same as regular but with archive notice)
        content = self.generate_page_content(articles, summaries, stats)
        
        # Replace the title in existing frontmatter instead of adding new frontmatter
        content = content.replace(
            'title: Zendesk news, from Deltastring',
            f'title: Industry RSS Feeds - {now.strftime("%d %B %Y")} Archive'
        )
        
        # Add archive notice after frontmatter
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if i > 0 and line == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end != -1:
            archive_notice = f"""
<div class="alert alert-warning mb-4">
    <i class="fas fa-archive"></i> This is an archived version from {now.strftime('%d %B %Y')}. 
    <a href="/news/">View latest updates</a>
</div>
"""
            lines.insert(frontmatter_end + 3, archive_notice)
            content = '\n'.join(lines)
        
        # Write archive file
        with open(archive_file, 'w') as f:
            f.write(content)
        
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