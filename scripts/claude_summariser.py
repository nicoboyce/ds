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
        
        prompt = f"""You are a Zendesk expert providing {timeframe} briefing to administrators managing Zendesk instances. Your audience needs specific, actionable insights - not generic summaries.

TARGET AUDIENCE: Zendesk administrators, solution partners, technical leads who need to know what requires immediate attention vs longer-term planning.

ARTICLES TO ANALYSE:
"""
        
        for i, article in enumerate(articles, 1):
            prompt += f"\n{i}. **{article['title']}** (Source: {article['source']})\n"
            if article['description']:
                prompt += f"   Details: {article['description'][:150]}...\n"
        
        prompt += f"""

ANALYSIS FOCUS:
- IMMEDIATE ACTIONS: What needs administrator attention this week?
- FEATURE ROLLOUTS: Which new features are rolling out and impact on workflows?
- SECURITY/COMPLIANCE: Any security updates, compliance changes, or vulnerabilities?
- INTEGRATIONS/APIs: Breaking changes or new API capabilities?
- EARLY ACCESS: New EAPs, beta programs, or limited availability features?

AVOID: Generic "monitor updates" advice. Focus on specific, actionable insights.

FORMAT (keep concise):

**{focus.replace('immediate implementation impacts and action items', 'Critical Updates').replace('strategic planning considerations and longer-term trends', 'Strategic Trends')}**:
[2-3 sentence summary of what Zendesk admins need to know RIGHT NOW]

**Priority Actions**:
• **[HIGH/MEDIUM/LOW]**: [Specific action required] - [Timeline if known]
• **[HIGH/MEDIUM/LOW]**: [Specific action required] - [Timeline if known]
• **[HIGH/MEDIUM/LOW]**: [Specific action required] - [Timeline if known]

**Bottom Line**: [One sentence: the single most important thing for Zendesk professionals to know from these updates]

Be specific. Use exact feature names, dates, and impacts. Skip generic advice."""

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
        
        # Create focused summary in new format
        critical_updates = f"{len(articles)} Zendesk updates available"
        if announcements:
            critical_updates += f" including {len(announcements)} new feature rollouts"
        if service_issues:
            critical_updates += f" and {len(service_issues)} service notifications"
        critical_updates += ". Key items require immediate administrator review."
        
        # Build priority actions
        actions = []
        if service_issues:
            actions.append("**HIGH**: Review service incidents and maintenance windows - Immediate")
        if security_items:
            actions.append("**HIGH**: Assess security updates and apply necessary patches - This week")
        if announcements:
            actions.append("**MEDIUM**: Evaluate new features for workflow impact - Planning phase")
        if dev_updates:
            actions.append("**MEDIUM**: Review API changes for integration compatibility - Testing phase")
        
        if not actions:
            actions.append("**LOW**: Monitor general platform updates - Ongoing")
        
        bottom_line = "Multiple feature announcements require workflow assessment" if announcements else \
                     "Service stability issues need immediate attention" if service_issues else \
                     "Routine platform updates available for review"
        
        return f"""**Critical Updates**: {critical_updates}

**Priority Actions**:
{chr(10).join([f"• {action}" for action in actions[:3]])}

**Bottom Line**: {bottom_line}."""
    
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