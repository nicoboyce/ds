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
            return self.fallback_summary(len(prompt.split('ARTICLES TO ANALYSE:')[1].split('\n\nANALYSIS REQUIREMENTS:')[0].split('\n\n')))
    
    def fallback_summary(self, article_count):
        """Fallback summary if Claude API fails"""
        return f"""**Lead Summary**: {article_count} Zendesk ecosystem updates available requiring administrator review.

**Key Developments**:
- **Platform Updates**: Multiple feature releases and configuration changes
- **Integration Changes**: API and workflow modifications may impact existing setups
- **Security Updates**: Review new security and compliance features

**Strategic Insight**: Regular monitoring of official Zendesk updates essential for maintaining optimal instance performance."""
    
    def generate_summaries(self):
        """Generate daily and weekly summaries"""
        articles = self.load_articles()
        
        summaries = {}
        
        # Daily summary (today's articles)
        if articles['today']:
            print(f"Generating daily summary for {len(articles['today'])} articles...")
            daily_prompt = self.build_zendesk_prompt(articles['today'][:10], 'daily')
            summaries['daily'] = self.call_claude_api(daily_prompt)
        else:
            summaries['daily'] = "No new articles today."
        
        # Weekly summary (this week's articles)
        week_articles = articles['today'] + articles['yesterday'] + articles['this_week']
        if week_articles:
            print(f"Generating weekly summary for {len(week_articles)} articles...")
            weekly_prompt = self.build_zendesk_prompt(week_articles[:20], 'weekly')
            summaries['weekly'] = self.call_claude_api(weekly_prompt)
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