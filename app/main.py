import asyncio
from datetime import datetime

from classify_news import classify_article, is_high_quality_good_news
from deduplication import is_duplicate_article
from facebook_post import generate_facebook_post
from fetch_news import fetch_additional_news, fetch_news
from humanity_index import calculate_humanity_index
from source_quality import check_source_quality
from summarize import summarize_article
from telegram_sender import send_message


PREFERRED_CATEGORIES = {
    "Animals": 3,
    "Science": 3,
    "Health": 2,
    "Community": 2,
    "Kindness": 2,
    "Environment": 1,
    "Education": 1,
}

PREFERRED_TEXT_KEYWORDS = {
    "animal": 2,
    "breakthrough": 2,
    "community": 1,
    "discovered": 2,
    "helped": 1,
    "people": 1,
    "rescue": 2,
    "research": 2,
    "scientist": 2,
    "shelter": 2,
    "stranger": 2,
    "volunteer": 2,
    "wildlife": 2,
}

CORPORATE_PR_KEYWORDS = {
    "award",
    "brand",
    "business",
    "company",
    "corporate",
    "funding",
    "launch",
    "market",
    "partnership",
    "press release",
    "product",
    "startup",
}


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

    category = article.get("category") or "Good news"
    source_name = article.get("source") or article.get("source_name") or "Unknown source"
    published_at = format_published_at(article.get("published_at"))
    trust_line = article.get("source_trust", "Надійність джерела: Unknown")

    return f"""
🌿 {category}

{article['title']}

Короткий переказ:
{summary}

{trust_line}
📰 Source: {source_name}
📅 Date: {published_at}
🔗 {article.get('url') or 'Unknown'}{country_line}
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
        "category": article.get("category"),
    }


def format_humanity_index_message(index_result):
    return f"Сьогоднішній індекс віри в людство: {float(index_result['index']):.1f}/10"


def format_facebook_post_message(good_articles, humanity_index):
    post = generate_facebook_post(good_articles, humanity_index.get("index"))
    return f"📝 Готовий пост для Facebook\n\n{post}"


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


def content_priority_score(news_item):
    category = news_item.get("category") or ""
    text = " ".join([
        news_item.get("title") or "",
        news_item.get("summary") or "",
    ]).lower()

    score = PREFERRED_CATEGORIES.get(category, 0)
    score += sum(weight for keyword, weight in PREFERRED_TEXT_KEYWORDS.items() if keyword in text)
    score -= sum(2 for keyword in CORPORATE_PR_KEYWORDS if keyword in text)
    score += news_item.get("classification_score", 0) / 10
    return score


def prioritize_good_articles(good_articles):
    good_articles.sort(
        key=lambda article: (
            content_priority_score(article),
            article.get("classification_score", 0),
        ),
        reverse=True,
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

        if is_high_quality_good_news(result):
            summary = summarize_article(article)
            article["category"] = result.get("category", "Good news")
            news_item = build_news_item(article, summary, source_quality)
            news_item["classification_score"] = classification_score(result)
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

    prioritize_good_articles(good_articles)

    humanity_index = calculate_humanity_index(good_articles[:5])
    await send_message(format_humanity_index_message(humanity_index))
    await send_message(format_facebook_post_message(good_articles[:5], humanity_index))

    for article in good_articles[:5]:
        await send_message(format_article_message(article, article["summary"]))


if __name__ == "__main__":
    asyncio.run(run())
