import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from requests import HTTPError

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
    if not NEWS_API_KEY:
        raise RuntimeError("NEWS_API_KEY is missing. Add it to your .env file.")

    params = {
        "apiKey": NEWS_API_KEY.strip(),
        "language": "en",
        "pageSize": 20,
    }

    if NEWS_COUNTRY:
        params["country"] = NEWS_COUNTRY

    response = requests.get(URL, params=params, timeout=20)

    try:
        response.raise_for_status()
    except HTTPError as error:
        message = "NewsAPI request failed"

        try:
            error_data = response.json()
            api_message = error_data.get("message")
            api_code = error_data.get("code")
            if api_message:
                message = f"{message}: {api_message}"
            if api_code:
                message = f"{message} ({api_code})"
        except ValueError:
            if response.text:
                message = f"{message}: {response.text[:200]}"

        raise RuntimeError(message) from error

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
