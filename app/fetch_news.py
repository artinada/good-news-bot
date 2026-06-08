import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_COUNTRY = os.getenv("NEWS_COUNTRY")

URL = "https://newsapi.org/v2/top-headlines"

COUNTRY_BY_CODE = {
    "au": "Australia",
    "ca": "Canada",
    "de": "Germany",
    "fr": "France",
    "gb": "United Kingdom",
    "ie": "Ireland",
    "in": "India",
    "nz": "New Zealand",
    "ua": "Ukraine",
    "uk": "United Kingdom",
    "us": "United States",
}


def detect_country(article):
    if NEWS_COUNTRY:
        return COUNTRY_BY_CODE.get(NEWS_COUNTRY.lower(), NEWS_COUNTRY.upper())

    url = article.get("url")
    if not url:
        return None

    hostname = urlparse(url).hostname or ""
    domain_parts = hostname.lower().split(".")
    if len(domain_parts) < 2:
        return None

    country_code = domain_parts[-1]
    return COUNTRY_BY_CODE.get(country_code)


def fetch_news():
    params = {
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 20,
    }

    if NEWS_COUNTRY:
        params["country"] = NEWS_COUNTRY

    response = requests.get(URL, params=params)
    response.raise_for_status()

    data = response.json()

    articles = []

    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "source": (article.get("source") or {}).get("name"),
            "url": article.get("url"),
            "published_at": article.get("publishedAt"),
            "country": detect_country(article),
        })

    return articles
