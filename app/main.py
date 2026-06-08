import asyncio
from datetime import datetime

from fetch_news import fetch_additional_news, fetch_news
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

    trust_line = article.get("source_trust", "Надійність джерела: Unknown")

    return f"""
🌿 {article['title']}

Короткий переказ:
{summary}

{trust_line}
Джерело: {article.get('source') or 'Unknown'}
Оригінал:
{article.get('url') or 'Unknown'}
Дата публікації: {format_published_at(article.get('published_at'))}{country_line}
"""


def build_news_item(article, summary, source_quality):
    return {
        "title": article.get("title"),
        "summary": summary,
        "source": article.get("source"),
        "source_trust": source_quality.get("display"),
        "source_trust_reason": source_quality.get("reason"),
        "url": article.get("url"),
        "published_at": article.get("published_at"),
        "country": article.get("country"),
    }


def article_key(article):
    return article.get("url") or article.get("title")


def process_articles(articles, good_articles, seen_article_keys, target_count=5):
    for article in articles:
        if len(good_articles) >= target_count:
            break

        if not article["title"]:
            continue

        key = article_key(article)
        if not key or key in seen_article_keys:
            continue

        seen_article_keys.add(key)

        source_quality = check_source_quality(article)
        if not source_quality["is_allowed"]:
            continue

        result = classify_article(article)

        if result["is_good"] and result["score"] >= 7:
            summary = summarize_article(article)
            good_articles.append(build_news_item(article, summary, source_quality))


async def run():
    articles = fetch_news()

    good_articles = []
    seen_article_keys = set()

    process_articles(articles, good_articles, seen_article_keys)

    if len(good_articles) < 3:
        additional_articles = fetch_additional_news()
        process_articles(additional_articles, good_articles, seen_article_keys)

    if not good_articles:
        await send_message(
            "Сьогодні не знайшлося достатньо теплих новин 🌙"
        )
        return

    for article in good_articles[:5]:
        await send_message(format_article_message(article, article["summary"]))


if __name__ == "__main__":
    asyncio.run(run())
