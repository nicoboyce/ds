#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.claude_summariser import ClaudeSummariser

# Create summariser
summariser = ClaudeSummariser()

# Extract from the URL
url = "https://support.zendesk.com/hc/en-us/articles/9688299927962-Release-notes-through-2025-09-05"
content = summariser.extract_release_notes_content(url)

if content:
    print("\n" + "=" * 80)
    print("FULL EXTRACTED CONTENT:")
    print("=" * 80)
    print(content)
    print("=" * 80)
    print(f"\nTotal length: {len(content)} characters")
else:
    print("Failed to extract content!")