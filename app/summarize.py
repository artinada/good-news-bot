from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def summarize_article(article):
    prompt = f"""
Create a short warm summary of this positive news.

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

    return response.choices[0].message.content
