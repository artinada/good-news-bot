def format_source(article):
    source = article.get("source") or "Unknown source"
    url = article.get("url")
    if not url:
        return source
    return f"{source} - {url}"


def fallback_humanity_index(good_articles):
    scores = [
        article.get("classification_score")
        for article in good_articles
        if article.get("classification_score") is not None
    ]
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)


def generate_facebook_post(good_articles, humanity_index=None, facts=None):
    lines = [
        "🌍 Добрі новини дня",
        "",
    ]

    for index, article in enumerate(good_articles, start=1):
        lines.extend([
            f"{index}. {article.get('title', 'Без назви')}",
            "",
            article.get("summary", ""),
            "",
            f"Джерело: {format_source(article)}",
            "",
        ])

    if humanity_index is None:
        humanity_index = fallback_humanity_index(good_articles)

    if humanity_index is not None:
        lines.append(f"Індекс віри в людство: {float(humanity_index):.1f}/10")

    if facts:
        lines.extend([
            "",
            facts.strip(),
        ])

    return "\n".join(lines).strip()
