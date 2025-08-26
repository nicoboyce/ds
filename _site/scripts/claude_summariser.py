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
        """Generate intelligent fallback summary with specific feature names"""
        if not articles:
            return "No new articles available."
        
        # Extract specific features and issues
        features = []
        eaps = []
        api_changes = []
        security_items = []
        service_issues = []
        
        for article in articles:
            title = article['title']
            title_lower = title.lower()
            
            if 'announcing' in title_lower:
                if 'eap' in title_lower or 'early access' in title_lower:
                    # Extract EAP name
                    eap_name = title.replace('Announcing ', '').replace(' EAP', '').replace(' - Zendesk Announcements', '')
                    eaps.append(eap_name)
                else:
                    # Extract feature name
                    feature_name = title.replace('Announcing ', '').replace(' - Zendesk Announcements', '')
                    features.append(feature_name)
            elif 'service incident' in title_lower or 'maintenance' in title_lower:
                service_issues.append(title)
            elif 'oauth' in title_lower or 'api' in title_lower or 'deprecation' in title_lower:
                api_changes.append(title)
            elif 'security' in title_lower or 'authentication' in title_lower or 'vulnerability' in title_lower:
                security_items.append(title)
        
        # Build specific summary
        summary_parts = []
        
        if features:
            # Show specific feature names, not just count
            feature_list = features[:3]  # Show first 3
            if len(features) == 1:
                summary_parts.append(f"**New Feature**: {feature_list[0]}")
            elif len(features) <= 3:
                summary_parts.append(f"**New Features**: {', '.join(feature_list[:-1])} and {feature_list[-1]}")
            else:
                summary_parts.append(f"**New Features**: {', '.join(feature_list)}, plus {len(features)-3} more")
        
        if eaps:
            summary_parts.append(f"**Early Access**: {', '.join(eaps)}")
        
        if api_changes:
            api_list = [title.replace(' - Zendesk Developer Updates', '') for title in api_changes[:2]]
            summary_parts.append(f"**API Updates**: {', '.join(api_list)}")
        
        if security_items:
            security_list = [title.replace(' - Zendesk Announcements', '') for title in security_items[:2]]
            summary_parts.append(f"**Security**: {', '.join(security_list)}")
        
        if service_issues:
            summary_parts.append(f"**Service Issues**: {len(service_issues)} incidents/maintenance")
        
        if not summary_parts:
            return "No significant Zendesk platform updates."
        
        # Create concise summary
        if len(summary_parts) == 1:
            return summary_parts[0]
        elif len(summary_parts) == 2:
            return f"{summary_parts[0]}. {summary_parts[1]}."
        else:
            return f"{summary_parts[0]}. {summary_parts[1]}. {summary_parts[2]}."
    
    def generate_summaries(self):
        """Generate daily and weekly summaries"""
        articles = self.load_articles()
        
        summaries = {}
        
        # Latest summary (last 48 hours)
        latest_articles = articles.get('latest', articles.get('current', []))  # Fallback to 'current' for compatibility
        if latest_articles:
            print(f"Generating latest summary for {len(latest_articles)} articles...")
            if self.api_key:
                latest_prompt = self.build_zendesk_prompt(latest_articles[:10], 'latest')
                latest_summary = self.call_claude_api(latest_prompt)
                summaries['latest'] = latest_summary if latest_summary else self.fallback_summary(latest_articles[:10])
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
                summaries['weekly'] = weekly_summary if weekly_summary else self.fallback_summary(week_articles[:20])
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
                summaries['monthly'] = monthly_summary if monthly_summary else self.fallback_summary(month_articles[:20])
            else:
                summaries['monthly'] = self.fallback_summary(month_articles[:20])
        else:
            summaries['monthly'] = "No articles in the past month."
        
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
    
    print("\nLatest Summary Preview:")
    print("=" * 50)
    latest = summaries.get('latest', 'No latest summary')
    print(latest[:200] + "..." if len(latest) > 200 else latest)