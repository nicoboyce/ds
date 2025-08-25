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
            
            for item in items[:max_items]:
                title_elem = item.find('title') or item.find('.//{http://www.w3.org/2005/Atom}title')
                link_elem = item.find('link') or item.find('.//{http://www.w3.org/2005/Atom}link')
                desc_elem = item.find('description') or item.find('.//{http://www.w3.org/2005/Atom}summary')
                pub_date_elem = item.find('pubDate') or item.find('.//{http://www.w3.org/2005/Atom}published')
                
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
        """Categorise articles by date (today, yesterday, this week, this month)"""
        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        categorised = {
            'today': [],
            'yesterday': [], 
            'this_week': [],
            'this_month': [],
            'older': []
        }
        
        for article in articles:
            # Parse publication date
            try:
                # Handle various date formats
                pub_date_str = article['pub_date']
                if pub_date_str:
                    # Try common RSS date formats
                    for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S']:
                        try:
                            pub_date = datetime.strptime(pub_date_str.split('+')[0].split('-')[0].strip(), fmt.split('%z')[0].strip()).date()
                            break
                        except:
                            continue
                    else:
                        # Fallback to today if parsing fails
                        pub_date = today
                else:
                    pub_date = today
            except:
                pub_date = today
            
            # Categorise by date
            if pub_date == today:
                categorised['today'].append(article)
            elif pub_date == yesterday:
                categorised['yesterday'].append(article)
            elif pub_date >= week_start:
                categorised['this_week'].append(article)
            elif pub_date >= month_start:
                categorised['this_month'].append(article)
            else:
                categorised['older'].append(article)
        
        return categorised
    
    def save_data(self, articles, categorised):
        """Save articles and categorised data"""
        # Save raw articles
        with open(self.data_dir / 'articles.json', 'w') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        # Save categorised articles
        with open(self.data_dir / 'categorised.json', 'w') as f:
            json.dump(categorised, f, indent=2, ensure_ascii=False)
        
        # Save summary stats
        stats = {
            'total_articles': len(articles),
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
        print(f"  Today: {stats['today_count']}")
        print(f"  Yesterday: {stats['yesterday_count']}")
        print(f"  This week: {stats['week_count']}")
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
        print(f"SUCCESS: Found {stats['total_articles']} articles")
    
    # Always exit successfully - empty feeds are normal