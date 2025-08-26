#!/usr/bin/env python3
"""
Production RSS ingestion script for Zendesk RSS aggregation
Fetches RSS feeds and stores structured data for Claude processing
"""

import requests
import xml.etree.ElementTree as ET
import json
import yaml
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import hashlib

class RSSIngestion:
    def __init__(self, config_path='_data/rss_feeds.yml', data_dir='_data/rss'):
        self.config_path = config_path
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Load RSS feeds configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def generate_article_id(self, title, pub_date):
        """Generate unique ID for article deduplication"""
        content = f"{title}{pub_date}".encode('utf-8')
        return hashlib.md5(content).hexdigest()[:12]
    
    def fetch_feed(self, feed_config, max_items=50):
        """Fetch and parse RSS feed"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"Fetching: {feed_config['name']}")
            response = requests.get(feed_config['url'], timeout=15, headers=headers)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            articles = []
            
            # Handle both RSS and Atom formats
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            print(f"  Found {len(items)} raw items in feed")
            
            for i, item in enumerate(items[:max_items]):
                # Fix the element finding logic
                title_elem = item.find('title')
                if title_elem is None:
                    title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
                
                link_elem = item.find('link')
                if link_elem is None:
                    link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
                
                desc_elem = item.find('description')
                if desc_elem is None:
                    desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
                
                pub_date_elem = item.find('pubDate')
                if pub_date_elem is None:
                    pub_date_elem = item.find('.//{http://www.w3.org/2005/Atom}published')
                
                if title_elem is not None and title_elem.text:
                    # Handle Atom link element
                    link = link_elem.text if link_elem is not None and link_elem.text else ''
                    if hasattr(link_elem, 'attrib') and 'href' in link_elem.attrib:
                        link = link_elem.attrib['href']
                    
                    pub_date = pub_date_elem.text if pub_date_elem is not None else ''
                    description = desc_elem.text if desc_elem is not None and desc_elem.text else ''
                    
                    # Clean description of HTML tags
                    import re
                    description = re.sub(r'<[^>]+>', '', description).strip()
                    
                    
                    # Extract real URL from Google News links
                    if 'Google News' in feed_config['name'] and 'news.google.com/rss/articles/' in link:
                        try:
                            import base64
                            import urllib.parse
                            # Extract the encoded part after 'articles/'
                            encoded_part = link.split('articles/')[-1].split('?')[0]
                            # Try to decode - Google News uses a proprietary encoding
                            # For now, keep the Google News link but add a flag
                            original_link = link
                            # We'll need to fetch the redirect URL later
                        except:
                            pass
                    
                    article = {
                        'id': self.generate_article_id(title_elem.text.strip(), pub_date),
                        'title': title_elem.text.strip(),
                        'link': link,
                        'description': description[:300] + '...' if len(description) > 300 else description,
                        'pub_date': pub_date,
                        'source': feed_config['name'],
                        'category': feed_config['category'],
                        'colour': feed_config['colour'],
                        'fetched_at': datetime.now().isoformat()
                    }
                    articles.append(article)
            
            print(f"  Found {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"Error fetching {feed_config['name']}: {e}")
            return []
    
    def deduplicate_articles(self, all_articles):
        """Remove duplicate articles based on ID"""
        seen_ids = set()
        deduplicated = []
        
        for article in all_articles:
            if article['id'] not in seen_ids:
                seen_ids.add(article['id'])
                deduplicated.append(article)
        
        return deduplicated
    
    def categorise_by_date(self, articles):
        """Categorise articles by date (current 48h, rolling week, rolling month)"""
        now = datetime.now()
        today = now.date()
        two_days_ago = today - timedelta(days=2)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        categorised = {
            'latest': [],       # Last 48 hours
            'this_week': [],    # 2-7 days ago (excluding current)
            'this_month': [],   # 7-30 days ago (excluding current and week)
            'older': [],        # More than 30 days
            'latest_release_notes': None,  # Most recent Zendesk release notes
            # Keep legacy keys for compatibility
            'today': [],
            'yesterday': []
        }
        
        # First, find the latest release notes article
        release_notes = [a for a in articles if 'Release notes through' in a.get('title', '')]
        if release_notes:
            # Sort by publication date to get the most recent
            release_notes.sort(key=lambda x: self._parse_date_str(x.get('pub_date', '')), reverse=True)
            categorised['latest_release_notes'] = release_notes[0]
        
        for article in articles:
            # Parse publication date
            try:
                # Handle various date formats
                pub_date_str = article['pub_date']
                pub_date = None  # Don't default to today - force proper parsing
                
                if pub_date_str:
                    # Try common RSS date formats
                    formats = [
                        '%a, %d %b %Y %H:%M:%S %Z',  # Mon, 25 Aug 2025 14:08:26 GMT
                        '%a, %d %b %Y %H:%M:%S %z',  # With timezone offset
                        '%a, %d %b %Y %H:%M:%S',     # Without timezone
                        '%Y-%m-%dT%H:%M:%S%z',       # ISO format
                        '%Y-%m-%d %H:%M:%S',         # Simple format
                        '%d %b %Y %H:%M:%S',         # Without day name
                    ]
                    
                    for fmt in formats:
                        try:
                            # Try parsing with different timezone handling
                            clean_date = pub_date_str.replace(' GMT', '').replace(' UTC', '').replace(' +0000', '').strip()
                            pub_date = datetime.strptime(clean_date, fmt.replace(' %Z', '').replace(' %z', '')).date()
                            break
                        except ValueError:
                            continue
                    
                    # If all formats failed, try manual parsing
                    if pub_date is None:
                        print(f"  WARNING: Could not parse date '{pub_date_str}' for article '{article['title'][:50]}...'")
                        pub_date = datetime(2020, 1, 1).date()  # Put unparseable dates in 'older'
                else:
                    pub_date = datetime(2020, 1, 1).date()  # Put undated articles in 'older'
            except Exception as e:
                print(f"  ERROR parsing date for '{article['title'][:50]}...': {e}")
                pub_date = datetime(2020, 1, 1).date()
            
            # Categorise by date - exclusive periods
            if pub_date >= two_days_ago:
                categorised['latest'].append(article)
                # Also add to legacy categories for backward compatibility
                if pub_date == today:
                    categorised['today'].append(article)
                elif pub_date == today - timedelta(days=1):
                    categorised['yesterday'].append(article)
            elif pub_date >= week_ago:
                categorised['this_week'].append(article)
            elif pub_date >= month_ago:
                categorised['this_month'].append(article)
            else:
                categorised['older'].append(article)
        
        return categorised
    
    def _parse_date_str(self, date_str):
        """Helper to parse date string for sorting"""
        if not date_str:
            return datetime(2020, 1, 1)
        
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
            '%d %b %Y %H:%M:%S',
        ]
        
        clean_date = date_str.replace(' GMT', '').replace(' UTC', '').replace(' +0000', '').strip()
        for fmt in formats:
            try:
                return datetime.strptime(clean_date, fmt.replace(' %Z', '').replace(' %z', ''))
            except:
                continue
        
        return datetime(2020, 1, 1)
    
    def save_data(self, articles, categorised):
        """Save articles and categorised data"""
        # Sort articles by publication date (newest first) before saving
        from datetime import datetime
        def parse_pub_date(article):
            try:
                pub_date_str = article.get('pub_date', '')
                if pub_date_str:
                    # Remove timezone info for parsing
                    clean = pub_date_str.replace(' GMT', '').replace(' UTC', '').replace(' +0000', '').strip()
                    # Try common format
                    try:
                        return datetime.strptime(clean, '%a, %d %b %Y %H:%M:%S')
                    except:
                        return datetime(2020, 1, 1)
                return datetime(2020, 1, 1)
            except:
                return datetime(2020, 1, 1)
        
        articles.sort(key=parse_pub_date, reverse=True)
        
        # Save raw articles (now sorted)
        with open(self.data_dir / 'articles.json', 'w') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        # Sort each category by publication date
        for category in categorised:
            if isinstance(categorised[category], list):
                categorised[category].sort(key=parse_pub_date, reverse=True)
        
        # Save categorised articles (now sorted)
        with open(self.data_dir / 'categorised.json', 'w') as f:
            json.dump(categorised, f, indent=2, ensure_ascii=False)
        
        # Save summary stats
        stats = {
            'total_articles': len(articles),
            'latest_count': len(categorised['latest']),
            'today_count': len(categorised['today']),
            'yesterday_count': len(categorised['yesterday']),
            'week_count': len(categorised['this_week']),
            'month_count': len(categorised['this_month']),
            'last_updated': datetime.now().isoformat(),
            'feeds_processed': len(self.config['feeds'])
        }
        
        with open(self.data_dir / 'stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def run(self):
        """Run the complete RSS ingestion process"""
        print("Starting RSS ingestion...")
        print(f"Processing {len(self.config['feeds'])} feeds")
        
        all_articles = []
        
        # Fetch all feeds
        for feed_config in self.config['feeds']:
            articles = self.fetch_feed(feed_config)
            all_articles.extend(articles)
        
        # Deduplicate and sort by date
        all_articles = self.deduplicate_articles(all_articles)
        all_articles.sort(key=lambda x: x['pub_date'], reverse=True)
        
        # Categorise by date
        categorised = self.categorise_by_date(all_articles)
        
        # Save data
        stats = self.save_data(all_articles, categorised)
        
        print(f"\nIngestion complete:")
        print(f"  Total articles: {stats['total_articles']}")
        print(f"  Latest (48h): {stats['latest_count']}")
        print(f"  This week (2-7d): {stats['week_count']}")
        print(f"  This month (7-30d): {stats['month_count']}")
        print(f"  Data saved to: {self.data_dir}")
        
        return stats

if __name__ == '__main__':
    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    ingestion = RSSIngestion()
    stats = ingestion.run()
    
    # No articles found is normal behaviour - not an error
    if stats['total_articles'] == 0:
        print("INFO: No new articles found in this run.")
    else:
        print(f"SUCCESS: Found {stats['total_articles']} articles (Latest: {stats.get('latest_count', 0)}, Week: {stats.get('week_count', 0)}, Month: {stats.get('month_count', 0)})")
    
    # Always exit successfully - empty feeds are normal