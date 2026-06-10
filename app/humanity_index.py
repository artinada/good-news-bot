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


def average(values, default=0):
    values = [value for value in values if value is not None]
    if not values:
        return default
    return sum(values) / len(values)


def source_quality_score(news_items):
    stars = []
    for item in news_items:
        trust = item.get("source_trust") or ""
        star_count = trust.count("⭐")
        if star_count:
            stars.append(star_count * 2)
    return average(stars, default=6)


def diversity_score(news_items):
    categories = {
        item.get("category")
        for item in news_items
        if item.get("category")
    }
    return min(10, 4 + len(categories) * 1.5)


def volume_score(news_items):
    return min(10, len(news_items) * 2)


def fallback_index(news_items):
    if not news_items:
        return {
            "index": 0,
            "reason": "No positive stories found",
        }

    kindness = average([item.get("humanity_score") for item in news_items], default=7)
    hope = average([item.get("hope_score") for item in news_items], default=7)
    warmth = average([item.get("warmth_score") for item in news_items], default=7)
    credibility = average([item.get("credibility_score") for item in news_items], default=7)
    tragedy_safety = average([
        10 - item.get("tragedy_level", 5)
        for item in news_items
    ], default=7)
    article_quality = average([
        item.get("classification_score")
        for item in news_items
    ], default=7)

    source_quality = source_quality_score(news_items)
    diversity = diversity_score(news_items)
    volume = volume_score(news_items)

    weighted_index = (
        kindness * 0.16
        + hope * 0.16
        + warmth * 0.12
        + article_quality * 0.16
        + credibility * 0.10
        + tragedy_safety * 0.10
        + source_quality * 0.08
        + diversity * 0.07
        + volume * 0.05
    )

    return {
        "kindness": round(kindness, 1),
        "hope": round(hope, 1),
        "warmth": round(warmth, 1),
        "credibility": round(credibility, 1),
        "source_quality": round(source_quality, 1),
        "diversity": round(diversity, 1),
        "tragedy_safety": round(tragedy_safety, 1),
        "volume": round(volume, 1),
        "index": round(weighted_index, 1),
        "reason": "Calculated from weighted story quality, source trust, diversity, and volume",
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
Source trust: {item.get('source_trust')}
Category: {item.get('category')}
Humanity score: {item.get('humanity_score')}
Hope score: {item.get('hope_score')}
Warmth score: {item.get('warmth_score')}
Credibility score: {item.get('credibility_score')}
Tragedy level: {item.get('tragedy_level')}
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
