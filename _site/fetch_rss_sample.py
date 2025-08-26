#!/usr/bin/env python3
"""
Quick RSS fetcher to get real headlines for mockup
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import yaml

def fetch_feed(url, max_items=3):
    """Fetch RSS feed and return list of articles"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        articles = []
        
        # Handle both RSS and Atom formats
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        for item in items[:max_items]:
            title = item.find('title') or item.find('.//{http://www.w3.org/2005/Atom}title')
            link = item.find('link') or item.find('.//{http://www.w3.org/2005/Atom}link')
            desc = item.find('description') or item.find('.//{http://www.w3.org/2005/Atom}summary')
            pub_date = item.find('pubDate') or item.find('.//{http://www.w3.org/2005/Atom}published')
            
            if title is not None and title.text:
                article = {
                    'title': title.text.strip(),
                    'link': link.text if link is not None and link.text else '#',
                    'description': desc.text.strip()[:200] + '...' if desc is not None and desc.text and len(desc.text.strip()) > 200 else (desc.text.strip() if desc is not None and desc.text else ''),
                    'pub_date': pub_date.text if pub_date is not None else ''
                }
                articles.append(article)
                
        return articles
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    # Load feed configuration
    with open('_data/rss_feeds.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("Fetching sample RSS data...\n")
    
    for feed in config['feeds']:
        print(f"Fetching: {feed['name']}")
        articles = fetch_feed(feed['url'])
        
        if articles:
            print(f"  Found {len(articles)} articles:")
            for article in articles:
                print(f"    - {article['title']}")
        else:
            print("  No articles found")
        print()

if __name__ == '__main__':
    main()