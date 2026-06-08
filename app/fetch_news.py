import os

import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

URL = "https://newsapi.org/v2/top-headlines"


def fetch_news():
    params = {
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 20,
    }

    response = requests.get(URL, params=params)
    response.raise_for_status()

    data = response.json()

    articles = []

    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
        })

    return articles
