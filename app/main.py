import asyncio
from datetime import datetime

from fetch_news import fetch_news
from classify_news import classify_article
from source_quality import check_source_quality
from summarize import summarize_article
from telegram_sender import send_message


def format_published_at(value):
    if not value:
        return "Unknown"

    try:
        published_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return published_at.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value


def format_article_message(article, summary):
    country_line = ""
    if article.get("country"):
        country_line = f"\nКраїна: {article['country']}"

    return f"""
🌿 {article['title']}

Короткий переказ:
{summary}

Джерело: {article.get('source') or 'Unknown'}
Оригінал:
{article.get('url') or 'Unknown'}
Дата публікації: {format_published_at(article.get('published_at'))}{country_line}
"""


def build_news_item(article, summary):
    return {
        "title": article.get("title"),
        "summary": summary,
        "source": article.get("source"),
        "url": article.get("url"),
        "published_at": article.get("published_at"),
        "country": article.get("country"),
    }


async def run():
    articles = fetch_news()

    good_articles = []

    for article in articles:
        if not article["title"]:
            continue

        source_quality = check_source_quality(article)
        if not source_quality["is_allowed"]:
            continue

        result = classify_article(article)

        if result["is_good"] and result["score"] >= 7:
            summary = summarize_article(article)
            good_articles.append(build_news_item(article, summary))

    if not good_articles:
        await send_message(
            "Сьогодні не знайшлося достатньо теплих новин 🌙"
        )
        return

    for article in good_articles[:5]:
        await send_message(format_article_message(article, article["summary"]))


if __name__ == "__main__":
    asyncio.run(run())
