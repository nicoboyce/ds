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
            print("ERROR: CLAUDE_API_KEY environment variable not set")
            sys.exit(1)
    
    def load_articles(self):
        """Load categorised articles from ingestion"""
        try:
            with open(self.data_dir / 'categorised.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("ERROR: No categorised articles found. Run RSS ingestion first.")
            sys.exit(1)
    
    def build_zendesk_prompt(self, articles, timeframe='daily'):
        """Build Claude prompt optimised for Zendesk administrators"""
        
        if timeframe == 'daily':
            context = "today's Zendesk ecosystem updates"
            focus = "immediate implementation impacts and action items"
        else:
            context = "this week's Zendesk ecosystem trends"
            focus = "strategic planning considerations and longer-term trends"
        
        prompt = f"""You are analysing {context} for Zendesk instance administrators, solution partners, and technical decision-makers who manage Zendesk implementations.

Your audience includes:
- Zendesk administrators managing enterprise instances
- Solution partners implementing Zendesk for clients  
- Technical leads planning Zendesk configurations
- Operations managers overseeing customer support workflows

ARTICLES TO ANALYSE:
"""
        
        for i, article in enumerate(articles, 1):
            prompt += f"\n{i}. **{article['title']}** (Source: {article['source']})\n"
            if article['description']:
                prompt += f"   Summary: {article['description']}\n"
        
        prompt += f"""

ANALYSIS REQUIREMENTS:

Focus specifically on:
- Implementation impacts and required timeline actions
- Feature changes affecting existing workflows and agent training
- Migration, upgrade, or configuration considerations  
- Security, compliance, and governance implications
- Budget planning for new features or licensing changes
- Integration impacts with existing systems
- User adoption and change management considerations

Avoid generic tech commentary. Be specific about operational impact for Zendesk professionals.

FORMAT YOUR RESPONSE:

**Lead Summary** (1-2 sentences): {focus}

**Key Developments** (3-4 bullet points):
- **[Category]:** Specific operational impact and what administrators need to do
- **[Category]:** Implementation timeline and planning considerations
- **[Category]:** Technical or workflow changes requiring action

**Strategic Insight** (1 sentence): One key trend or pattern across these updates that Zendesk professionals should monitor.

Write for professionals who need actionable intelligence, not general tech news consumers."""

        return prompt
    
    def call_claude_api(self, prompt):
        """Call Claude API for summary generation"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': 'claude-3-sonnet-20240229',
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            print("Calling Claude API...")
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['content'][0]['text']
            
        except Exception as e:
            print(f"Claude API error: {e}")
            return None  # Will be handled by caller
    
    def fallback_summary(self, articles):
        """Generate intelligent fallback summary from article analysis"""
        if not articles:
            return "No new articles available."
        
        # Analyze articles by source and content
        zendesk_official = []
        dev_updates = []
        security_items = []
        service_issues = []
        announcements = []
        
        for article in articles:
            title = article['title'].lower()
            source = article['source'].lower()
            
            if 'announcement' in title or 'announcing' in title:
                announcements.append(article['title'])
            elif 'service incident' in title or 'maintenance' in title:
                service_issues.append(article['title'])
            elif 'security' in title or 'vulnerability' in title or 'oauth' in title:
                security_items.append(article['title'])
            elif 'api' in title or 'developer' in source:
                dev_updates.append(article['title'])
            elif 'zendesk' in source:
                zendesk_official.append(article['title'])
        
        # Build intelligent summary
        key_points = []
        
        if announcements:
            key_points.append(f"**New Features**: {len(announcements)} feature announcements including {announcements[0][:60]}...")
        if service_issues:
            key_points.append(f"**Service Updates**: {len(service_issues)} service notifications requiring attention")
        if security_items:
            key_points.append(f"**Security**: {len(security_items)} security-related updates requiring review")
        if dev_updates:
            key_points.append(f"**Developer**: {len(dev_updates)} API and integration changes")
        
        if not key_points:
            key_points.append("**Platform Updates**: General Zendesk ecosystem updates available")
        
        # Create summary
        lead_summary = f"**Lead Summary**: {len(articles)} Zendesk updates available"
        if announcements:
            lead_summary += f" with {len(announcements)} major feature announcements"
        if service_issues:
            lead_summary += f" and {len(service_issues)} service notifications"
        lead_summary += "."
        
        return f"""{lead_summary}

**Key Developments**:
{chr(10).join([f"- {point}" for point in key_points[:4]])}

**Strategic Insight**: {'Security and service stability updates require immediate review' if security_items or service_issues else 'Feature rollouts may impact existing workflows and require planning'}."""
    
    def generate_summaries(self):
        """Generate daily and weekly summaries"""
        articles = self.load_articles()
        
        summaries = {}
        
        # Daily summary (today's articles)
        if articles['today']:
            print(f"Generating daily summary for {len(articles['today'])} articles...")
            daily_prompt = self.build_zendesk_prompt(articles['today'][:10], 'daily')
            daily_summary = self.call_claude_api(daily_prompt)
            summaries['daily'] = daily_summary if daily_summary else self.fallback_summary(articles['today'][:10])
        else:
            summaries['daily'] = "No new articles today."
        
        # Weekly summary (this week's articles)
        week_articles = articles['today'] + articles['yesterday'] + articles['this_week']
        if week_articles:
            print(f"Generating weekly summary for {len(week_articles)} articles...")
            weekly_prompt = self.build_zendesk_prompt(week_articles[:20], 'weekly')
            weekly_summary = self.call_claude_api(weekly_prompt)
            summaries['weekly'] = weekly_summary if weekly_summary else self.fallback_summary(week_articles[:20])
        else:
            summaries['weekly'] = "No articles this week."
        
        # Save summaries
        summaries['generated_at'] = datetime.now().isoformat()
        
        with open(self.data_dir / 'summaries.json', 'w') as f:
            json.dump(summaries, f, indent=2, ensure_ascii=False)
        
        print(f"Summaries saved to: {self.data_dir / 'summaries.json'}")
        return summaries

if __name__ == '__main__':
    # Change to script directory  
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    summariser = ClaudeSummariser()
    summaries = summariser.generate_summaries()
    
    print("\nDaily Summary Preview:")
    print("=" * 50)
    print(summaries['daily'][:200] + "..." if len(summaries['daily']) > 200 else summaries['daily'])