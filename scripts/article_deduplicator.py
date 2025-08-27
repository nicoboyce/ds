#!/usr/bin/env python3
"""
Article Deduplication and Categorisation System

This module handles:
1. Fuzzy matching to identify duplicate articles about the same story
2. Source ranking to prefer detailed, original sources
3. Story tracking to detect genuine updates vs rehashing
4. Topic categorisation for better organisation

Author: Deltastring
Date: August 2025
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional


class ArticleDeduplicator:
    """
    Deduplicates and categorises articles for the Zendesk news aggregator.
    
    Uses fuzzy matching to group related articles, tracks story lifecycle,
    and categorises content by topic for Zendesk professionals.
    """
    
    # Topic categories with keywords for classification
    CATEGORIES = {
        'incidents_security': {
            'name': '🚨 Incidents & Security',
            'keywords': ['incident', 'outage', 'degradation', 'vulnerability', 
                        'security', 'exploit', 'breach', 'hack', 'emergency',
                        'critical', '0-day', '0-click', 'takeover', 'hijack'],
            'priority': 1
        },
        'product_updates': {
            'name': '🚀 Product Updates',
            'keywords': ['announcing', 'release notes', 'new feature', 'eap',
                        'early access', 'api', 'deprecat', 'update', 'enhancement',
                        'improvement', 'beta', 'preview', 'admin center'],
            'priority': 2
        },
        'operations': {
            'name': '🔧 Operations & Maintenance',
            'keywords': ['maintenance', 'scheduled', 'migration', 'compliance',
                        'best practice', 'guide', 'how to', 'instructions'],
            'priority': 3
        },
        'business': {
            'name': '📊 Business & Strategy', 
            'keywords': ['pricing', 'acquisition', 'partner', 'investment',
                        'headquarter', 'hq', 'auction', 'valuation', 'funding',
                        'competitor', 'killer', 'alternative', 'market'],
            'priority': 4
        },
        'resources': {
            'name': '💡 Resources & Learning',
            'keywords': ['tutorial', 'webinar', 'community', 'developer',
                        'integration', 'app', 'marketplace', 'review', 
                        'case study', 'tips', 'tricks'],
            'priority': 5
        }
    }
    
    # Source quality rankings (higher = better)
    SOURCE_RANKINGS = {
        'Zendesk Announcements': 10,
        'Zendesk Service Notifications': 10,
        'Zendesk Developer Updates': 9,
        'Zendesk Release Notes': 9,
        'Internal Note': 8,
        'CyberSecurityNews': 7,
        'GBHackers': 7,
        'The Information': 6,
        'Computer Weekly': 6,
        'Google News': 3,  # Aggregator, prefer original sources
        'Unknown': 1
    }
    
    def __init__(self, data_dir: Path):
        """
        Initialise the deduplicator with data directory.
        
        Args:
            data_dir: Path to the data directory for storing tracking data
        """
        self.data_dir = data_dir
        self.stories_file = data_dir / 'tracked_stories.json'
        self.stories = self.load_stories()
        
    def load_stories(self) -> Dict:
        """
        Load tracked stories from JSON file.
        
        Returns:
            Dictionary of tracked stories with their history
        """
        if self.stories_file.exists():
            with open(self.stories_file, 'r') as f:
                return json.load(f)
        return {'stories': {}, 'last_updated': None}
    
    def save_stories(self):
        """Save tracked stories to JSON file."""
        self.stories['last_updated'] = datetime.now().isoformat()
        with open(self.stories_file, 'w') as f:
            json.dump(self.stories, f, indent=2, ensure_ascii=False)
    
    def fuzzy_match(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """
        Check if two texts are similar using fuzzy matching.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            threshold: Similarity threshold (0-1), default 0.8
            
        Returns:
            True if texts are similar above threshold
        """
        # Normalise texts for comparison
        def normalise(text):
            # Remove common prefixes
            text = re.sub(r'^(Announcing|Service Incident|Release notes)', '', text)
            # Remove dates
            text = re.sub(r'\d{4}-\d{2}-\d{2}|\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)', '', text)
            # Remove source suffixes
            text = re.sub(r'\s*-\s*(Zendesk|Google News|CyberSecurityNews).*$', '', text)
            # Lowercase and strip
            return text.lower().strip()
        
        norm1 = normalise(text1)
        norm2 = normalise(text2)
        
        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Also check for key term overlap for specific topics
        key_terms_1 = set(re.findall(r'\b\w+\b', norm1))
        key_terms_2 = set(re.findall(r'\b\w+\b', norm2))
        
        # Check for critical matching terms
        critical_terms = {'vulnerability', 'exploit', 'auction', 'hq', 'headquarters',
                         '0-click', '0-day', 'takeover', 'breach'}
        
        critical_match_1 = key_terms_1 & critical_terms
        critical_match_2 = key_terms_2 & critical_terms
        
        # If both contain same critical terms, lower the threshold
        if critical_match_1 and critical_match_1 == critical_match_2:
            threshold = 0.6
            
        return similarity >= threshold
    
    def get_source_rank(self, article: Dict) -> int:
        """
        Get quality ranking for an article's source.
        
        Args:
            article: Article dictionary with source information
            
        Returns:
            Integer ranking (higher = better quality source)
        """
        source = article.get('source', 'Unknown')
        
        # Check exact match first
        if source in self.SOURCE_RANKINGS:
            return self.SOURCE_RANKINGS[source]
        
        # Check partial matches
        for key, rank in self.SOURCE_RANKINGS.items():
            if key in source:
                return rank
                
        return self.SOURCE_RANKINGS['Unknown']
    
    def categorise_article(self, article: Dict) -> str:
        """
        Categorise an article into topic categories.
        
        Args:
            article: Article dictionary with title and description
            
        Returns:
            Category key (e.g., 'incidents_security')
        """
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        combined_text = f"{title} {description}"
        
        # Score each category based on keyword matches
        category_scores = {}
        
        for cat_key, cat_info in self.CATEGORIES.items():
            score = 0
            for keyword in cat_info['keywords']:
                if keyword in combined_text:
                    # Weight title matches higher than description
                    if keyword in title:
                        score += 2
                    else:
                        score += 1
                        
            if score > 0:
                # Adjust score by priority (higher priority = small boost)
                score += (6 - cat_info['priority']) * 0.1
                category_scores[cat_key] = score
        
        # Return category with highest score, or 'resources' as default
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return 'resources'
    
    def parse_date(self, date_str: str) -> str:
        """
        Parse various date formats and return ISO format string.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            ISO formatted date string
        """
        from datetime import datetime
        
        # Try various date formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',  # RSS format
            '%a, %d %b %Y %H:%M:%S GMT',  # RSS with GMT
            '%Y-%m-%dT%H:%M:%S%z',  # ISO with timezone
            '%Y-%m-%dT%H:%M:%S',  # ISO without timezone
            '%Y-%m-%d %H:%M:%S'  # Simple datetime
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.replace(' GMT', ' +0000'), fmt)
                return dt.isoformat()
            except:
                continue
                
        # If parsing fails, return current time
        return datetime.now().isoformat()
    
    def create_story_id(self, article: Dict) -> str:
        """
        Create a unique identifier for a story based on its key terms.
        
        Args:
            article: Article dictionary
            
        Returns:
            Story ID string
        """
        title = article.get('title', '').lower()
        
        # Extract key terms for story identification
        # Remove common words and source identifiers
        title = re.sub(r'\b(the|and|for|with|from|about|announces?|announcing)\b', '', title)
        title = re.sub(r'\s*-\s*(zendesk|google news).*$', '', title)
        
        # Extract important terms
        key_terms = []
        
        # Look for specific patterns
        if 'vulnerability' in title or 'exploit' in title:
            # Security story - extract vulnerability type
            if '0-click' in title or '0 click' in title:
                key_terms.append('0click-vulnerability')
            elif match := re.search(r'([\w\s]+)\s+vulnerability', title):
                key_terms.append(f"{match.group(1).strip()}-vulnerability")
                
        elif 'incident' in title:
            # Service incident - extract date and service
            if match := re.search(r'(\d{4}-\d{2}-\d{2}|\w+\s+\d+)', title):
                key_terms.append(f"incident-{match.group(1)}")
                
        elif 'headquarters' in title or 'hq' in title:
            # HQ story
            key_terms.append('zendesk-hq')
            
        elif 'release notes' in title:
            # Release notes - extract date
            if match := re.search(r'(\d{4}-\d{2}-\d{2})', title):
                key_terms.append(f"release-{match.group(1)}")
        
        # If no specific pattern, use first few significant words
        if not key_terms:
            words = re.findall(r'\b[a-z]{4,}\b', title)[:3]
            key_terms = words[:3] if words else ['unknown']
            
        return '-'.join(key_terms)
    
    def deduplicate_articles(self, articles: List[Dict], timeframe: str = 'latest') -> Dict:
        """
        Deduplicate and categorise articles.
        
        Groups related articles together, tracks story lifecycle,
        and organises by topic categories.
        
        Args:
            articles: List of article dictionaries
            timeframe: Time period ('latest', 'week', 'month')
            
        Returns:
            Dictionary with deduplicated, categorised articles
        """
        now = datetime.now()
        cutoff_48h = now - timedelta(hours=48)
        
        # Group articles by story
        story_groups = {}
        
        for article in articles:
            # Try to match with existing groups
            matched = False
            
            for story_id, group in story_groups.items():
                # Check if article matches any in the group
                for existing in group['articles']:
                    if self.fuzzy_match(article['title'], existing['title']):
                        group['articles'].append(article)
                        matched = True
                        break
                        
                if matched:
                    break
            
            # If no match, create new group
            if not matched:
                story_id = self.create_story_id(article)
                story_groups[story_id] = {
                    'articles': [article],
                    'category': self.categorise_article(article),
                    'first_seen': self.parse_date(article.get('pub_date', now.isoformat()))
                }
        
        # Process each story group
        processed_stories = {
            'incidents_security': [],
            'product_updates': [],
            'operations': [],
            'business': [],
            'resources': []
        }
        
        for story_id, group in story_groups.items():
            # Sort articles by source quality
            group['articles'].sort(key=lambda x: self.get_source_rank(x), reverse=True)
            
            # Pick the best article as primary
            primary = group['articles'][0]
            
            # Check if this is a known story that's been updated
            is_update = False
            if story_id in self.stories.get('stories', {}):
                stored_story = self.stories['stories'][story_id]
                # Check if there's new information (different title or description)
                if not self.fuzzy_match(primary['title'], stored_story.get('last_title', '')):
                    is_update = True
                    
            # Determine if story should be shown
            show_story = True
            if timeframe == 'latest':
                # For latest, check if story is new or updated in last 48h
                first_seen_str = group.get('first_seen', now.isoformat())
                # Parse the date properly
                if isinstance(first_seen_str, str):
                    try:
                        first_seen = datetime.fromisoformat(first_seen_str)
                    except:
                        # Fallback to parsing with our method
                        first_seen_str = self.parse_date(first_seen_str)
                        first_seen = datetime.fromisoformat(first_seen_str)
                else:
                    first_seen = now
                    
                if first_seen < cutoff_48h and not is_update:
                    show_story = False
                    
            if show_story:
                # Create deduplicated story entry
                story_entry = {
                    'title': primary['title'],
                    'link': primary['link'],
                    'description': primary.get('description', ''),
                    'source': primary.get('source', 'Unknown'),
                    'pub_date': primary.get('pub_date', ''),
                    'source_count': len(group['articles']),
                    'sources': [a.get('source', 'Unknown') for a in group['articles']],
                    'is_update': is_update
                }
                
                # Add to appropriate category
                category = group['category']
                processed_stories[category].append(story_entry)
                
                # Update tracking
                self.stories.setdefault('stories', {})[story_id] = {
                    'last_seen': now.isoformat(),
                    'last_title': primary['title'],
                    'first_seen': group.get('first_seen', now.isoformat()),
                    'update_count': stored_story.get('update_count', 0) + (1 if is_update else 0)
                        if story_id in self.stories.get('stories', {}) else 0
                }
        
        # Save updated story tracking
        self.save_stories()
        
        return processed_stories


if __name__ == '__main__':
    # Test the deduplicator
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    
    dedup = ArticleDeduplicator(Path('_data/rss'))
    print("Article Deduplicator initialised successfully")
    print(f"Tracking {len(dedup.stories.get('stories', {}))} stories")