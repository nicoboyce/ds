# Zendesk Release Notes Summarisation - Prompt Recommendations

## Current Problem
The current summaries are generic marketing fluff:
> "The latest release introduces several notable enhancements to Zendesk's capabilities. On September 5th, 2025, the company unveiled an advanced AI agent feature..."

This tells administrators nothing useful.

## Recommended Approach

### 1. Change the Model
```python
# CURRENT (BAD)
'model': 'claude-3-haiku-20240307'  # Cheapest, fastest, worst quality

# RECOMMENDED
'model': 'claude-3-sonnet-20240229'  # Better at following instructions
# OR if budget allows:
'model': 'claude-3-5-sonnet-20241022'  # Best quality
```

### 2. Increase Token Limit
```python
# CURRENT (TOO RESTRICTIVE)
'max_tokens': 300

# RECOMMENDED
'max_tokens': 450  # Allows for proper detail
```

### 3. Lower Temperature
```python
# ADD THIS
'temperature': 0.2  # More factual, less creative
```

### 4. Better Prompts

#### Option A: "Technical Bullets" (Recommended)
```python
prompt = f"""Extract ONLY the concrete technical changes from these release notes. Focus on:
- New UI elements (exact names like "External OAuth clients page")
- Configuration changes (what settings were added/removed)
- Feature additions (with exact feature names)
- API changes or deprecations
- Specific numbers or limits mentioned

Content:
{full_content}

Format: Write 2-3 sentences. Each sentence should contain 2-3 specific changes. Use exact feature names from the release notes.
Example good output: "Support added sender authentication auto-detection for Gmail/Office365, removing manual DKIM setup. Copilot expanded with 15 new recommendation types and can now suggest existing macros in auto-assist procedures."
Example bad output: "Zendesk unveiled advanced features to enhance the platform."
"""
```

#### Option B: "Admin Focus"
```python
prompt = f"""You are writing for busy Zendesk administrators who need to know EXACTLY what changed.

From these release notes, extract:
1. Specific features/settings that were added or changed (use exact names)
2. What administrators need to do differently
3. Any deprecations or removals
4. Numbers, dates, or limits mentioned

Content:
{full_content}

Write 2-3 dense sentences packed with specifics. No marketing language. No "enhancements" or "improvements" - say what actually changed.
"""
```

#### Option C: "What Changed" (Most Direct)
```python
prompt = f"""List exactly what changed in this release. Rules:
- Use the exact feature names from the release notes
- Include ALL numbers, dates, or technical details
- Group by product (Support, Copilot, Admin Center, etc.)
- Skip all marketing language

Content:
{full_content}

Write 2-3 fact-packed sentences. Only include concrete changes that admins can act on.
"""
```

## Expected Output Examples

### BAD (Current):
"The latest release introduces several notable enhancements to Zendesk's capabilities. The Workflow Management system has been updated with improved tools."

### GOOD (With new prompts):
"Support now auto-detects sender authentication for Gmail and Office 365, eliminating manual DKIM/SPF configuration. Copilot added 15 new recommendation types and can suggest existing macros in auto-assist procedures, while WFM introduced CSV exports for agent activity timelines."

### GOOD (Alternative):
"Admin Center displays external OAuth clients on a new dedicated page, with password access removed for API authentication on inactive accounts. Knowledge base search indexing increased to 10,000 articles per workspace, and AI Agents Advanced supports custom webhook timeouts up to 30 seconds."

## Implementation in claude_summariser.py

Replace lines 449-456 with:

```python
prompt = f"""Extract ONLY the concrete technical changes from these release notes. Focus on:
- New UI elements (exact names)
- Configuration changes
- Feature additions (exact names)
- Deprecations or removals
- Specific numbers or limits

Content:
{full_content}

Write 2-3 sentences listing specific changes. Use exact feature names. Example: "Support added sender authentication auto-detection for Gmail/Office365. Copilot expanded with 15 new recommendation types and macro suggestions in auto-assist."

DO NOT use words like: improvements, enhancements, notable, unveiled, capabilities, streamline, optimize.
ONLY state what specifically changed."""

# And update the API call (lines 469-474):
'model': 'claude-3-sonnet-20240229',  # Much better model
'max_tokens': 450,  # More space for details
'temperature': 0.2,  # Factual, not creative
```

## Testing Protocol

1. Test each prompt on the last 5 release notes
2. Compare outputs for specificity and usefulness
3. Check that outputs avoid marketing language
4. Verify technical details are preserved
5. Ensure output fits within 2-3 sentences

## Cost Considerations

- Haiku: ~$0.25 per million input tokens
- Sonnet: ~$3 per million input tokens
- For ~100 release notes per month at 3000 chars each: 
  - Haiku: ~$0.01/month
  - Sonnet: ~$0.10/month
  
The 10x cost difference is worth it for actually useful summaries.