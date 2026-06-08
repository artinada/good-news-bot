import json

from dotenv import load_dotenv
from openai import OpenAI
from prompts import FILTER_PROMPT

load_dotenv()

client = OpenAI()


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
            "score": 0,
            "reason": "Parsing failed"
        }
