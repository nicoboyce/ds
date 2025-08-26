# RSS News System TODOs

## Features to Implement

### Group Duplicate Articles
- Google News often returns multiple articles about the same story
- Implement deduplication/grouping logic to combine similar articles
- Could use title similarity matching or URL domain grouping
- Display as a single item with multiple sources listed

### Implementation Ideas
- Use fuzzy string matching on titles (e.g., Levenshtein distance)
- Group articles with >80% title similarity
- Show primary article with '+ 3 more sources' link
- Consider grouping by story/event rather than exact duplicates

