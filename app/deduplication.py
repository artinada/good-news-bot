import re
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
}


def normalize_url(url):
    if not url:
        return None

    parsed = urlparse(url.strip())
    hostname = parsed.hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]

    query_params = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        key_lower = key.lower()
        if key_lower in TRACKING_QUERY_PARAMS:
            continue
        if key_lower.startswith(TRACKING_QUERY_PREFIXES):
            continue
        query_params.append((key, value))

    return urlunparse((
        parsed.scheme.lower(),
        hostname.lower(),
        parsed.path.rstrip("/"),
        "",
        urlencode(query_params),
        "",
    ))


def normalize_title(title):
    if not title:
        return None

    normalized = title.lower()
    normalized = re.sub(r"\s+-\s+[^-]+$", "", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def is_similar_title(title, seen_titles, threshold=0.9):
    if not title:
        return False

    return any(
        SequenceMatcher(None, title, seen_title).ratio() >= threshold
        for seen_title in seen_titles
    )


def is_duplicate_article(article, seen_urls, seen_titles):
    normalized_url = normalize_url(article.get("url"))
    normalized_title = normalize_title(article.get("title"))

    if normalized_url and normalized_url in seen_urls:
        return True

    if normalized_title and (
        normalized_title in seen_titles or is_similar_title(normalized_title, seen_titles)
    ):
        return True

    if normalized_url:
        seen_urls.add(normalized_url)
    if normalized_title:
        seen_titles.add(normalized_title)

    return False
