import asyncio
from datetime import datetime

from deduplication import is_duplicate_article
from fetch_news import fetch_additional_news, fetch_news
from classify_news import classify_article
from humanity_index import calculate_humanity_index
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


def format_humanity_index_message(index_result):
    return f"Сьогоднішній індекс віри в людство: {float(index_result['index']):.1f}/10"


def classification_score(result):
    scores = [
        result.get("humanity_score"),
        result.get("hope_score"),
        result.get("warmth_score"),
        result.get("credibility_score"),
        10 - result.get("tragedy_level", 10),
    ]
    scores = [score for score in scores if score is not None]
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 1)


def is_good_result(result):
    return (
        result.get("is_good") is True
        and result.get("humanity_score", 0) >= 7
        and result.get("hope_score", 0) >= 7
        and result.get("warmth_score", 0) >= 6
        and result.get("credibility_score", 0) >= 6
        and result.get("tragedy_level", 10) <= 4
    )


def process_articles(articles, good_articles, seen_urls, seen_titles, target_count=5):
    for article in articles:
        if len(good_articles) >= target_count:
            break

        if not article["title"]:
            continue

        if is_duplicate_article(article, seen_urls, seen_titles):
            continue

        source_quality = check_source_quality(article)
        if not source_quality["is_allowed"]:
            continue

        result = classify_article(article)

        if is_good_result(result):
            summary = summarize_article(article)
            news_item = build_news_item(article, summary, source_quality)
            news_item["classification_score"] = classification_score(result)
            news_item["category"] = result.get("category")
            good_articles.append(news_item)


async def run():
    articles = fetch_news()

    good_articles = []
    seen_urls = set()
    seen_titles = set()

    process_articles(articles, good_articles, seen_urls, seen_titles)

    if len(good_articles) < 3:
        additional_articles = fetch_additional_news()
        process_articles(additional_articles, good_articles, seen_urls, seen_titles)

    if not good_articles:
        await send_message(
            "Сьогодні не знайшлося достатньо теплих новин 🌙"
        )
        return

    humanity_index = calculate_humanity_index(good_articles[:5])
    await send_message(format_humanity_index_message(humanity_index))

    for article in good_articles[:5]:
        await send_message(format_article_message(article, article["summary"]))


if __name__ == "__main__":
    asyncio.run(run())
