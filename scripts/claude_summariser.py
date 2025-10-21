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
from bs4 import BeautifulSoup
import re

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
- Write concise but informative descriptions (5-15 words per item)
- For critical items: emphasise the risk/impact
- For features: clarify what it does and who it affects
- For EAPs: name the specific program
- Group related items together with commas
- Start each section on a new line
- Only include sections that have content
- Use exact feature names from the titles, don't abbreviate
- Do NOT include reference numbers like [1] or [2]"""

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
                'max_tokens': 1500,  # Increased for more detailed summaries
                'temperature': 0.1,  # Very low for maximum factual accuracy
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

    def generate_dont_miss_context(self, article):
        """
        Generate a contextual comment for the "Don't Miss" article using Claude.

        Args:
            article: Dictionary with title, description, source

        Returns:
            String: 1-2 sentence contextual explanation, or None if API fails
        """
        if not self.api_key:
            return None

        title = article.get('title', '')
        description = article.get('description', '')
        source = article.get('source', '')

        prompt = f"""You are a technical editor for Zendesk administrators.

Article: {title}
Description: {description}
Source: {source}

Write ONE compelling sentence (under 25 words) explaining why this specific article matters to Zendesk admins. Be specific and practical, referencing technical details from the article. Use British English."""

        try:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01'
            }

            payload = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 150,
                'temperature': 0.3,
                'messages': [{'role': 'user', 'content': prompt}]
            }

            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=10
            )

            response.raise_for_status()
            result = response.json()
            return result['content'][0]['text'].strip()

        except Exception as e:
            print(f"Don't Miss context generation failed: {e}")
            return None

    def fallback_summary(self, articles):
        """Generate comprehensive fallback summary matching the new format"""
        if not articles:
            return "No new articles available."
        
        critical_items = []
        latest_items = []
        meanwhile_items = []
        
        for article in articles:
            title = article['title']
            title_lower = title.lower()
            
            # Critical items (security, outages)
            if any(term in title_lower for term in ['vulnerability', '0-day', '0-click', 'exploit', 'takeover', 'hijack']):
                desc = title.replace(' - CyberSecurityNews', '').replace(' - GBHackers', '')
                critical_items.append(desc)
            elif 'service incident' in title_lower or 'degradation' in title_lower or 'outage' in title_lower:
                critical_items.append(title)
            
            # Latest items (features, updates, releases)  
            elif 'announcing' in title_lower or 'release notes' in title_lower:
                if 'eap' in title_lower or 'early access' in title_lower:
                    desc = title.replace('Announcing ', '').replace(' - Zendesk Announcements', '')
                    latest_items.append(f"EAP: {desc}")
                else:
                    desc = title.replace('Announcing ', '').replace(' - Zendesk Announcements', '')
                    latest_items.append(desc)
            elif any(term in title_lower for term in ['api', 'oauth', 'deprecat', 'integration', 'update']):
                desc = title.replace(' - Zendesk Developer Updates', '').replace(' - Zendesk Announcements', '')
                latest_items.append(desc)
            
            # Meanwhile items (business, reviews, ecosystem)
            elif any(term in title_lower for term in ['auction', 'headquarters', 'hq', 'funding', 'acquisition', 'partner', 'review', 'killer', 'alternative']):
                desc = title.replace(' - Google News', '').replace(' - Zendesk', '')
                meanwhile_items.append(desc)
        
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
    
    def generate_fallback_narrative(self, articles):
        """Generate basic fallback when Claude API unavailable"""

        if not articles:
            return "No recent activity to analyse."

        # Simple rule-based analysis
        security_count = sum(1 for a in articles if any(term in a['title'].lower() for term in ['vulnerability', 'security', 'exploit', 'breach']))
        incident_count = sum(1 for a in articles if any(term in a['title'].lower() for term in ['incident', 'outage', 'degradation', 'down']))
        feature_count = sum(1 for a in articles if any(term in a['title'].lower() for term in ['announcing', 'eap', 'release', 'feature', 'copilot', 'ai']))

        # Priority-based simple analysis
        if security_count >= 2:
            return f"Multiple security issues detected requiring immediate administrator attention. Review {security_count} security-related updates for critical patches and configuration changes."
        elif incident_count >= 3:
            return f"Service stability concerns with {incident_count} incidents reported. Administrators should review monitoring and incident response procedures."
        elif feature_count >= 5:
            return f"Heavy development activity with {feature_count} feature announcements. Plan testing cycles for new capabilities before production deployment."
        else:
            return f"Standard ecosystem activity with {len(articles)} updates across Zendesk products and services. Regular maintenance and review procedures recommended."
    
    def build_narrative_prompt(self, articles):
        """Build prompt for narrative analysis that leverages Claude's pattern recognition"""

        prompt = f"""You are a Zendesk ecosystem analyst. Read these {len(articles)} recent article titles and identify the most significant operational pattern that administrators need to understand.

ARTICLES:
"""

        for i, article in enumerate(articles, 1):
            prompt += f"\n[{i}] {article['title']}\n"

        prompt += f"""

Look for patterns across these titles that simple keyword counting would miss:
- Timing coincidences (multiple related issues happening simultaneously)
- Product area concentrations (problems clustering in specific Zendesk products)
- Contradictory signals (expansion announcements during stability issues)
- Escalating severity (minor issues becoming major incidents)
- Strategic shifts (feature directions indicating platform changes)
- External pressures (competitor moves, regulatory changes affecting Zendesk)

Write exactly 2 sentences that:
1. Identify the most important pattern you observe
2. Explain what this means for Zendesk administrators operationally

Focus on insights that emerge from reading the titles together, not just counting categories. What story do these titles tell when viewed as a whole?

EXAMPLES OF GOOD PATTERN RECOGNITION:
"Three messaging-related incidents coincided with the rollout of AI-powered conversation routing, suggesting the new AI features may be destabilising core communication infrastructure. Administrators should test AI routing thoroughly in staging environments before enabling in production."

"Zendesk announced major Copilot expansions while simultaneously responding to Atlassian's Jira end-of-life notice, indicating pressure to strengthen integrations as partners exit the market. This creates both opportunity and risk for administrators managing multi-tool workflows."

YOUR ANALYSIS (exactly 2 sentences):"""

        return prompt

    def generate_summaries(self):
        """Generate summaries including narrative analysis for recently section"""
        articles = self.load_articles()
        
        summaries = {}
        
        # No longer generate latest summary (removed from UI)
        summaries['latest'] = ""
        
        # Generate narrative for "recently" section (combines week + month)
        recently_articles = []
        recently_articles.extend(articles.get('this_week', []))
        recently_articles.extend(articles.get('this_month', [])[:20])
        
        if recently_articles:
            print(f"Generating narrative analysis for {len(recently_articles)} recent articles...")
            if self.api_key:
                narrative_prompt = self.build_narrative_prompt(recently_articles[:30])
                narrative_summary = self.call_claude_api(narrative_prompt)
                if narrative_summary:
                    summaries['recently_narrative'] = narrative_summary
                else:
                    # Fallback narrative
                    summaries['recently_narrative'] = self.generate_fallback_narrative(recently_articles)
            else:
                summaries['recently_narrative'] = self.generate_fallback_narrative(recently_articles)
        else:
            summaries['recently_narrative'] = "No significant updates in the recent period."
        
        # Keep weekly and monthly for backwards compatibility but they won't be shown
        summaries['weekly'] = ""
        summaries['monthly'] = ""
        
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
    
    def clean_release_notes_content(self, content):
        """Clean up extracted release notes content for better readability"""
        
        # Remove irrelevant sections
        content = re.sub(r'App Marketplace.*?(?=\n[A-Z]|$)', '', content, flags=re.DOTALL)
        content = re.sub(r'Products with no updates.*?(?=\n[A-Z]|$)', '', content, flags=re.DOTALL)
        
        # Fix broken line breaks within sentences
        content = re.sub(r'\n(?=[a-z])', ' ', content)  # Join lines that start with lowercase
        content = re.sub(r'\n(?=\w)', ' ', content)  # Join most broken lines
        
        # Remove duplicate section headers
        lines = content.split('\n')
        seen_headers = set()
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a duplicate section header
            if line in ['Admin Center', 'Copilot', 'AI Agents Advanced', 'Support', 'Mobile'] and line in seen_headers:
                continue
            
            if line in ['Admin Center', 'Copilot', 'AI Agents Advanced', 'Support', 'Mobile']:
                seen_headers.add(line)
            
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Normalize whitespace
        content = re.sub(r' +', ' ', content)  # Multiple spaces to single space
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Multiple newlines to double
        
        return content.strip()

    def extract_release_notes_content(self, url):
        """Extract release notes content from URL"""
        try:
            print(f"Fetching full release notes from: {url}")
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
            except requests.Timeout:
                print(f"ERROR: Timeout fetching {url} after 15 seconds")
                return None
            except requests.RequestException as e:
                print(f"ERROR: Failed to fetch {url}: {e}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the article content area - try multiple selectors
            article_body = None
            for selector in ['main', 'article', '.article-body', '[class*=article]', '.article-content']:
                article_body = soup.select_one(selector)
                if article_body:
                    break
                    
            if not article_body:
                print("WARNING: Could not find content container, using fallback")
                return None
                
            # Get all text content
            full_text = article_body.get_text(separator='\n', strip=True)
            
            # Start AFTER "Products with no updates this week"
            start_marker = "Products with no updates this week"
            start_idx = full_text.find(start_marker)
            if start_idx == -1:
                print("WARNING: Could not find start marker, using fallback")
                return None
            
            # Move past the marker line itself
            start_idx += len(start_marker)
            content_from_start = full_text[start_idx:]
            
            # Find App Marketplace that comes at the end
            end_marker = "App Marketplace"
            end_idx = content_from_start.find(end_marker)
            
            if end_idx != -1:
                content = content_from_start[:end_idx].strip()
            else:
                # If no ending App Marketplace found, take a large chunk
                content = content_from_start[:5000].strip()
            
            # Clean up the content
            content = re.sub(r'\n\s*\n', '\n\n', content)  # Normalize line breaks
            content = content.strip()
            
            print(f"Extracted {len(content)} characters of release notes content")
            
            return content
            
        except Exception as e:
            print(f"ERROR fetching release notes content: {e}")
            return None

    def summarise_release_notes(self, release_notes):
        """Generate focused summary for Zendesk release notes"""
        if not release_notes:
            return None
        
        if not self.api_key:
            return self.fallback_release_notes_summary(release_notes)
        
        # Extract full content from the release notes URL
        title = release_notes.get('title', '')
        url = release_notes.get('link', '')
        
        # Try to get full content from URL first
        full_content = None
        if url:
            full_content = self.extract_release_notes_content(url)
        
        # Fall back to description if URL extraction fails
        if not full_content:
            print("Falling back to truncated RSS description")
            full_content = release_notes.get('description', '')[:3000]
        
        prompt = f"""CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY:

1. Extract ONLY concrete, specific changes from the release notes below
2. Use the EXACT feature names as they appear in the text
3. Include ALL numbers, percentages, dates, and technical details
4. NEVER use vague words like "improvements", "enhancements", "updates", "notable", "unveiled", "capabilities"
5. Write dense, information-packed sentences

BANNED WORDS (DO NOT USE):
- improvements, enhancements, updates, notable, unveiled
- capabilities, streamline, optimize, advanced, robust
- various, several, multiple (use exact numbers instead)
- helps, aims, designed to, intended to

REQUIRED FORMAT:
Write exactly 2-3 sentences. Pack multiple specific changes into each sentence using commas. 

GOOD EXAMPLE:
"Support added sender authentication auto-detection for Gmail and Office 365 domains, eliminating manual DKIM/SPF configuration. Copilot introduced 15 new recommendation types for refunds and escalations, macro suggestions in auto-assist procedures, and conversation summarisation for Slack channels. WFM now exports agent activity timelines to CSV, with scheduled reports available via email delivery."

BAD EXAMPLE (NEVER WRITE LIKE THIS):
"The latest release introduces several enhancements to improve the platform. New features help streamline operations."

RELEASE NOTES CONTENT:
{full_content}

YOUR SUMMARY (2-3 fact-packed sentences with specific feature names and numbers):"""
        
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
                    'max_tokens': 800,  # Much higher to allow Haiku to be more detailed
                    'temperature': 0.1,  # Very low for maximum factual accuracy
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
    # Only run at 6am, 12pm, and 6pm to avoid unnecessary API calls
    current_hour = datetime.now().hour
    if current_hour not in [6, 12, 18]:
        print(f"Skipping summary generation (current hour: {current_hour}). Only runs at 6am, 12pm, and 6pm.")
        sys.exit(0)

    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)

    summariser = ClaudeSummariser()
    summaries = summariser.generate_summaries()

    print("\nLatest Summary Preview:")
    print("=" * 50)
    latest = summaries.get('latest', 'No latest summary')
    print(latest[:200] + "..." if len(latest) > 200 else latest)