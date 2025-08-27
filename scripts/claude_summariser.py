#!/usr/bin/env python3
"""
Claude API integration for generating Zendesk-focused summaries
Optimised for Zendesk administrators and solution partners
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
import sys

class ClaudeSummariser:
    def __init__(self, data_dir='_data/rss', api_key=None):
        self.data_dir = Path(data_dir)
        self.api_key = api_key or os.environ.get('CLAUDE_API_KEY')
        
        if not self.api_key:
            print("WARNING: CLAUDE_API_KEY environment variable not set - using fallback summaries only")
    
    def load_articles(self):
        """Load categorised articles from ingestion"""
        try:
            with open(self.data_dir / 'categorised.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("ERROR: No categorised articles found. Run RSS ingestion first.")
            sys.exit(1)
    
    def build_zendesk_prompt(self, articles, timeframe='latest'):
        """Build Claude prompt optimised for Zendesk administrators"""
        
        if timeframe == 'latest':
            context = "the latest Zendesk ecosystem updates (last 48 hours)"
            focus = "immediate implementation impacts and action items"
        elif timeframe == 'weekly':
            context = "this week's Zendesk ecosystem trends (2-7 days ago)"
            focus = "recent updates and planning considerations"
        else:
            context = "this month's Zendesk ecosystem changes (7-30 days ago)"
            focus = "strategic trends and longer-term developments"
        
        prompt = f"""Create a comprehensive Zendesk news digest for Zendesk administrators and consultants.

ARTICLES:
"""
        
        for i, article in enumerate(articles, 1):
            prompt += f"\n[{i}] {article['title']}\n"
        
        prompt += f"""

Create a structured summary covering ALL relevant items from the articles above:

Critical:
(Security vulnerabilities, 0-day exploits, service outages, urgent incidents requiring immediate action)

{('Latest' if timeframe == 'latest' else 'This week' if timeframe == 'weekly' else 'This month')}:
(New features, early access programs, product updates, API changes, deprecations, release notes)

Meanwhile:
(Industry news, business developments, competitor updates, reviews, acquisitions, general Zendesk ecosystem news)

REQUIREMENTS:
- Include EVERY article that fits each category - don't limit the count
- Use [N] to reference specific article numbers
- Write concise but informative descriptions (5-15 words per item)
- For critical items: emphasise the risk/impact
- For features: clarify what it does and who it affects
- For EAPs: name the specific program
- Group related items together with commas
- Start each section on a new line
- Only include sections that have content
- Use exact feature names from the titles, don't abbreviate"""

        return prompt
    
    def call_claude_api(self, prompt):
        """Call Claude API for summary generation
        
        Uses the Anthropic Messages API to generate summaries optimised for
        Zendesk administrators. Falls back gracefully if API is unavailable.
        """
        try:
            # Configure API headers with authentication
            # API version must match the model capabilities
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01'  # Required API version
            }
            
            # Build the request payload
            # Using Sonnet model for balanced speed and quality
            payload = {
                'model': 'claude-3-haiku-20240307',  # Using Haiku - only model available with this API key
                'max_tokens': 1000,  # Sufficient for our concise summaries
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            print("Calling Claude API...")
            # Make the API request with a reasonable timeout
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=30  # 30 second timeout for API calls
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            result = response.json()
            
            # Extract the text from Claude's response
            # The API returns content in a structured format
            return result['content'][0]['text']
            
        except Exception as e:
            # Log the error but don't fail the pipeline
            # Fallback summaries will be used instead
            print(f"Claude API error: {e}")
            return None  # Will be handled by caller
    
    def fallback_summary(self, articles):
        """Generate comprehensive fallback summary matching the new format"""
        if not articles:
            return "No new articles available."
        
        # Track article indices for references
        critical_items = []
        latest_items = []
        meanwhile_items = []
        
        for i, article in enumerate(articles, 1):
            title = article['title']
            title_lower = title.lower()
            
            # Critical items (security, outages)
            if any(term in title_lower for term in ['vulnerability', '0-day', '0-click', 'exploit', 'takeover', 'hijack']):
                desc = title.replace(' - CyberSecurityNews', '').replace(' - GBHackers', '')
                critical_items.append(f"[{i}] {desc}")
            elif 'service incident' in title_lower or 'degradation' in title_lower or 'outage' in title_lower:
                critical_items.append(f"[{i}] {title}")
            
            # Latest items (features, updates, releases)  
            elif 'announcing' in title_lower or 'release notes' in title_lower:
                if 'eap' in title_lower or 'early access' in title_lower:
                    desc = title.replace('Announcing ', '').replace(' - Zendesk Announcements', '')
                    latest_items.append(f"[{i}] EAP: {desc}")
                else:
                    desc = title.replace('Announcing ', '').replace(' - Zendesk Announcements', '')
                    latest_items.append(f"[{i}] {desc}")
            elif any(term in title_lower for term in ['api', 'oauth', 'deprecat', 'integration', 'update']):
                desc = title.replace(' - Zendesk Developer Updates', '').replace(' - Zendesk Announcements', '')
                latest_items.append(f"[{i}] {desc}")
            
            # Meanwhile items (business, reviews, ecosystem)
            elif any(term in title_lower for term in ['auction', 'headquarters', 'hq', 'funding', 'acquisition', 'partner', 'review', 'killer', 'alternative']):
                desc = title.replace(' - Google News', '').replace(' - Zendesk', '')
                meanwhile_items.append(f"[{i}] {desc}")
        
        # Build the summary in the new format
        summary_parts = []
        
        if critical_items:
            summary_parts.append("Critical:\n" + ", ".join(critical_items))
        
        if latest_items:
            summary_parts.append("Latest:\n" + ", ".join(latest_items))
        
        if meanwhile_items:
            summary_parts.append("Meanwhile:\n" + ", ".join(meanwhile_items))
        
        if not summary_parts:
            return "No significant updates to report."
        
        return "\n\n".join(summary_parts)
    
    
    def generate_summaries(self):
        """Generate daily and weekly summaries with clickable references"""
        articles = self.load_articles()
        
        summaries = {}
        
        # Latest summary (last 48 hours)
        latest_articles = articles.get('latest', articles.get('current', []))  # Fallback to 'current' for compatibility
        if latest_articles:
            print(f"Generating latest summary for {len(latest_articles)} articles...")
            if self.api_key:
                latest_prompt = self.build_zendesk_prompt(latest_articles[:10], 'latest')
                latest_summary = self.call_claude_api(latest_prompt)
                if latest_summary:
                    summaries['latest'] = latest_summary
                else:
                    summaries['latest'] = self.fallback_summary(latest_articles[:10])
            else:
                summaries['latest'] = self.fallback_summary(latest_articles[:10])
        else:
            summaries['latest'] = "No new articles in the last 48 hours."
        
        # Weekly summary (2-7 days ago, excluding current)
        week_articles = articles.get('this_week', [])
        if week_articles:
            print(f"Generating weekly summary for {len(week_articles)} articles...")
            if self.api_key:
                weekly_prompt = self.build_zendesk_prompt(week_articles[:20], 'weekly')
                weekly_summary = self.call_claude_api(weekly_prompt)
                if weekly_summary:
                    summaries['weekly'] = weekly_summary
                else:
                    summaries['weekly'] = self.fallback_summary(week_articles[:20])
            else:
                summaries['weekly'] = self.fallback_summary(week_articles[:20])
        else:
            summaries['weekly'] = "No articles this week."
        
        # Monthly summary (7-30 days ago, excluding current and week)
        month_articles = articles.get('this_month', [])
        if month_articles:
            print(f"Generating monthly summary for {len(month_articles)} articles...")
            if self.api_key:
                monthly_prompt = self.build_zendesk_prompt(month_articles[:20], 'monthly')
                monthly_summary = self.call_claude_api(monthly_prompt)
                if monthly_summary:
                    summaries['monthly'] = monthly_summary
                else:
                    summaries['monthly'] = self.fallback_summary(month_articles[:20])
            else:
                summaries['monthly'] = self.fallback_summary(month_articles[:20])
        else:
            summaries['monthly'] = "No articles in the past month."
        
        # Save summaries
        summaries['generated_at'] = datetime.now().isoformat()
        
        # Generate release notes summary only if there's a new one
        if articles.get('latest_release_notes'):
            latest_release = articles['latest_release_notes']
            
            # Check if we already have a summary for this release
            existing_summaries = {}
            try:
                with open(self.data_dir / 'summaries.json', 'r') as f:
                    existing_summaries = json.load(f)
            except:
                pass
            
            existing_release_notes = existing_summaries.get('release_notes', {})
            existing_article_id = existing_release_notes.get('article', {}).get('id', '')
            
            # Only regenerate if it's a different release notes article
            if latest_release.get('id') != existing_article_id:
                print(f"New release notes detected: {latest_release.get('title', 'Unknown')}")
                release_notes_summary = self.summarise_release_notes(latest_release)
                if release_notes_summary:
                    summaries['release_notes'] = {
                        'summary': release_notes_summary,
                        'article': latest_release,
                        'generated_at': datetime.now().isoformat()
                    }
            elif existing_release_notes:
                # Keep the existing summary
                summaries['release_notes'] = existing_release_notes
        
        with open(self.data_dir / 'summaries.json', 'w') as f:
            json.dump(summaries, f, indent=2, ensure_ascii=False)
        
        print(f"Summaries saved to: {self.data_dir / 'summaries.json'}")
        return summaries
    
    def summarise_release_notes(self, release_notes):
        """Generate focused summary for Zendesk release notes"""
        if not release_notes:
            return None
        
        if not self.api_key:
            return self.fallback_release_notes_summary(release_notes)
        
        # Extract just the key changes from the description
        description = release_notes.get('description', '')
        title = release_notes.get('title', '')
        
        prompt = f"""You are analysing the latest Zendesk release notes for administrators. Extract ONLY the most important feature changes and updates that directly impact administrators.

Release: {title}

Content:
{description[:1500]}

Provide a 1-2 sentence summary focusing ONLY on:
- Key new features (not marketplace apps)
- Major UI/workflow changes  
- Security or compliance updates
- API or integration changes

Ignore marketplace app updates. Format as: "Feature: description. Feature: description."
Be extremely concise and specific. Use product names (Copilot, AI Agents, Admin Center) not generic terms."""
        
        try:
            # Use requests library for API call
            # This is specifically for release notes which need quick, focused summaries
            import requests
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01',  # Required API version
                    'content-type': 'application/json'
                },
                json={
                    'model': 'claude-3-haiku-20240307',  # Using Haiku - only model available with this API key
                    'max_tokens': 150,  # Keep release notes summaries brief
                    'temperature': 0.3,  # Lower temperature for factual accuracy
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['content'][0]['text'].strip()
            else:
                print(f"Claude API error: {response.status_code}")
                return self.fallback_release_notes_summary(release_notes)
        
        except Exception as e:
            print(f"Error calling Claude API for release notes: {e}")
            return self.fallback_release_notes_summary(release_notes)
    
    def fallback_release_notes_summary(self, release_notes):
        """Fallback summary for release notes when Claude API unavailable"""
        description = release_notes.get('description', '')
        
        # More specific parsing for common patterns
        features = []
        
        # Look for Copilot updates
        if 'Copilot' in description:
            if 'macros' in description.lower() and 'auto assist' in description.lower():
                features.append("Copilot: auto assist can now suggest existing macros to agents")
            elif 'add existing macros' in description.lower():
                features.append("Copilot: admins can add existing macros to auto assist procedures")
            elif 'copilot' in description.lower():
                # Extract what follows Copilot mention
                copilot_match = description[description.find('Copilot'):]
                if 'New:' in copilot_match[:100]:
                    feature = copilot_match.split('New:')[1].split('.')[0].strip()[:80]
                    if feature:
                        features.append(f"Copilot: {feature}")
        
        # Look for AI Agents updates  
        if 'AI Agents' in description:
            if 'UI' in description or 'interface' in description.lower() or 'block' in description.lower():
                features.append("AI Agents Advanced: improved UI for managing dialogue builder blocks")
            elif 'AI Agents Advanced' in description:
                # Extract what follows
                ai_match = description[description.find('AI Agents'):]
                if 'New:' in ai_match[:150]:
                    feature = ai_match.split('New:')[1].split('.')[0].strip()[:80]
                    if feature:
                        features.append(f"AI Agents: {feature}")
        
        # Look for other key updates
        for keyword in ['Support', 'Admin Center', 'Talk', 'Messaging', 'Knowledge', 'QA']:
            if keyword in description and 'New:' in description:
                idx = description.find(keyword)
                if idx != -1:
                    context = description[idx:idx+200]
                    if 'New:' in context:
                        feature = context.split('New:')[1].split('.')[0].strip()[:60]
                        if feature and len(feature) > 10:
                            features.append(f"{keyword}: {feature}")
                            break
        
        if features:
            # Return the most specific features
            return '. '.join(features[:2])
        else:
            # Last resort - try to extract anything after "New:"
            if 'New:' in description:
                first_new = description.split('New:')[1].split('.')[0].strip()[:100]
                if first_new:
                    return f"Latest updates: {first_new}"
            
            # Generic fallback
            title = release_notes.get('title', '')
            date = title.replace('Release notes through ', '') if 'Release notes through' in title else 'Latest'
            return f"Zendesk release notes for {date} available. Check for updates to your products."

if __name__ == '__main__':
    # Change to script directory  
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    summariser = ClaudeSummariser()
    summaries = summariser.generate_summaries()
    
    print("\nLatest Summary Preview:")
    print("=" * 50)
    latest = summaries.get('latest', 'No latest summary')
    print(latest[:200] + "..." if len(latest) > 200 else latest)