import json

from dotenv import load_dotenv
from openai import OpenAI
from prompts import FILTER_PROMPT

load_dotenv()

client = OpenAI()


def is_high_quality_good_news(result):
    return (
        result.get("is_good") is True
        and result.get("humanity_score", 0) >= 7
        and result.get("hope_score", 0) >= 7
        and result.get("warmth_score", 0) >= 6
        and result.get("credibility_score", 0) >= 6
        and result.get("tragedy_level", 10) <= 4
    )


def classify_article(article):
    content = f"""
Title: {article['title']}

Description:
{article['description']}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": FILTER_PROMPT
            },
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0.3
    )

    text = response.choices[0].message.content

    try:
        result = json.loads(text)
        return result
    except Exception:
        return {
            "is_good": False,
            "category": "Other",
            "humanity_score": 0,
            "hope_score": 0,
            "warmth_score": 0,
            "credibility_score": 0,
            "tragedy_level": 10,
            "reason": "Parsing failed"
        }
