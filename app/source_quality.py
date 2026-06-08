from urllib.parse import urlparse

TRUSTED_SOURCE_NAMES = {
    "associated press",
    "ap",
    "ap news",
    "bbc",
    "bbc news",
    "nature",
    "npr",
    "reuters",
    "science",
    "the associated press",
    "the guardian",
}

TRUSTED_DOMAINS = {
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "nature.com",
    "npr.org",
    "reuters.com",
    "science.org",
    "theguardian.com",
}

UNWANTED_SOURCE_KEYWORDS = {
    "aggregator",
    "anonymous",
    "blog",
    "clickbait",
    "corporate",
    "daily buzz",
    "generated",
    "gossip",
    "press release",
    "pr newswire",
    "rumor",
    "viral",
}


def normalize(value):
    return (value or "").strip().lower()


def get_domain(url):
    hostname = urlparse(url or "").hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname.lower()


def is_trusted_domain(domain):
    return any(domain == trusted or domain.endswith(f".{trusted}") for trusted in TRUSTED_DOMAINS)


def build_quality_result(is_allowed, stars, label, reason):
    return {
        "is_allowed": is_allowed,
        "stars": stars,
        "label": label,
        "display": f"{'⭐' * stars} {label}",
        "reason": reason,
    }


def check_source_quality(article):
    source = normalize(article.get("source"))
    domain = get_domain(article.get("url"))

    if not source and not domain:
        return build_quality_result(
            False,
            1,
            "Низька надійність",
            "Missing source and URL",
        )

    if any(keyword in source or keyword in domain for keyword in UNWANTED_SOURCE_KEYWORDS):
        return build_quality_result(
            False,
            1,
            "Низька надійність",
            "Source matches unwanted quality pattern",
        )

    if source in TRUSTED_SOURCE_NAMES or is_trusted_domain(domain):
        return build_quality_result(
            True,
            5,
            "Висока надійність",
            "Trusted editorial source",
        )

    if source and domain:
        return build_quality_result(
            True,
            3,
            "Середня надійність",
            "Named source with a public URL",
        )

    return build_quality_result(
        False,
        2,
        "Низька надійність",
        "Source is incomplete",
    )
