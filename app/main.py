import asyncio

from fetch_news import fetch_news
from classify_news import classify_article
from summarize import summarize_article
from telegram_sender import send_message


async def run():
    articles = fetch_news()

    good_articles = []

    for article in articles:
        if not article["title"]:
            continue

        result = classify_article(article)

        if result["is_good"] and result["score"] >= 7:
            summary = summarize_article(article)

            message = f"""
🌿 {article['title']}

{summary}

Source:
{article['url']}
"""

            good_articles.append(message)

    if not good_articles:
        await send_message(
            "Сьогодні не знайшлося достатньо теплих новин 🌙"
        )
        return

    for article in good_articles[:5]:
        await send_message(article)


if __name__ == "__main__":
    asyncio.run(run())
