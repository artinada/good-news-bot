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

HUMANITY_INDEX_PROMPT = """
You calculate a daily "faith in humanity" index from selected positive news.

Evaluate the whole set of stories using these criteria:
- kindness
- impact on people
- long-term benefit
- inspiration
- scale

Each criterion should be scored from 1 to 10.
The final index should be a single number from 1 to 10 with one decimal place.

Return JSON only:
{
  "kindness": 1-10,
  "impact_on_people": 1-10,
  "long_term_benefit": 1-10,
  "inspiration": 1-10,
  "scale": 1-10,
  "index": 1-10,
  "reason": "short reason"
}
"""
