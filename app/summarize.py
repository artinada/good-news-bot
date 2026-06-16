import json

from dotenv import load_dotenv
from openai import OpenAI

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


def summarize_article(article):
    prompt = f"""
Create a precise Ukrainian title and a short warm Ukrainian summary of this positive news.

Title:
{article['title']}

Description:
{article['description']}

Source:
{article.get('source')}

Published at:
{article.get('published_at')}

Requirements:
- warm tone
- 2-3 sentences
- no exaggeration
- restore faith in humanity
- do not use clickbait
- do not make the title more dramatic than the article
- title must be factual, specific, and calm
- summary must preserve what is known and avoid unsupported claims

Return only valid JSON:
{{
  "title": "precise non-clickbait Ukrainian title",
  "summary": "2-3 sentence Ukrainian summary"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    text = response.choices[0].message.content

    try:
        result = parse_json_response(text)
        return {
            "title": result.get("title") or article["title"],
            "summary": result.get("summary") or text,
        }
    except Exception:
        return {
            "title": article["title"],
            "summary": text,
        }
