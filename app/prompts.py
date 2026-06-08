FILTER_PROMPT = """
You are filtering world news.

Your task:
Return ONLY positive, humane, uplifting news.

Good categories:
- kindness
- scientific progress
- helping people
- helping animals
- environmental recovery
- community support
- inspiring human actions

Reject:
- politics
- wars
- disasters
- crime
- celebrity gossip
- ragebait
- tragedy-based positivity

Return JSON:
{
  "is_good": true/false,
  "score": 1-10,
  "reason": "short reason"
}
"""
