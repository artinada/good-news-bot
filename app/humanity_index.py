import json

from dotenv import load_dotenv
from openai import OpenAI
from prompts import HUMANITY_INDEX_PROMPT

load_dotenv()

client = OpenAI()


def parse_json_response(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise
        return json.loads(text[start:end + 1])


def fallback_index(news_items):
    scores = [
        item.get("classification_score")
        for item in news_items
        if item.get("classification_score") is not None
    ]

    if not scores:
        return {
            "index": 7.0,
            "reason": "Calculated from selected positive stories",
        }

    return {
        "index": round(sum(scores) / len(scores), 1),
        "reason": "Calculated from article positivity scores",
    }


def calculate_humanity_index(news_items):
    if not news_items:
        return {
            "index": 0,
            "reason": "No positive stories found",
        }

    stories = []
    for item in news_items:
        stories.append(
            f"""
Title: {item.get('title')}
Summary: {item.get('summary')}
Source: {item.get('source')}
"""
        )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": HUMANITY_INDEX_PROMPT,
            },
            {
                "role": "user",
                "content": "\n---\n".join(stories),
            },
        ],
        temperature=0.2,
    )

    text = response.choices[0].message.content

    try:
        result = parse_json_response(text)
        result["index"] = round(float(result["index"]), 1)
        return result
    except Exception:
        return fallback_index(news_items)
