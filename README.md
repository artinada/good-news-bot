# Good News Bot

Telegram bot that collects positive world news and sends uplifting stories daily.

## Features

- Fetches latest news
- Checks source quality before AI processing
- Uses AI to filter humane/uplifting stories
- Rejects toxic/ragebait content
- Creates warm summaries
- Sends results to Telegram with title, summary, source trust level, source, original link, publish date, and country when available

## Trusted Sources

The bot processes news only from a trusted allowlist:

- Reuters
- Associated Press
- BBC
- NPR
- The Guardian
- Nature
- Science

It rejects unknown aggregators, clickbait-heavy sources, anonymous blogs, and AI-generated news sites without a clear editorial source.

Trusted allowlist sources are shown with `⭐⭐⭐⭐⭐ Висока надійність`.
Other named sources with a public URL can pass as `⭐⭐⭐ Середня надійність`.

## Setup

### 1. Clone repository

```bash
git clone <repo_url>
cd good-news-bot
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

Create a local `.env` file:

```env
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
NEWS_COUNTRY=us
```

### 4. Run

```bash
python app/main.py
```

## Troubleshooting

If NewsAPI returns `401 Unauthorized`, the `NEWS_API_KEY` value was loaded but rejected. Check that the key is copied from your NewsAPI account, active, and not expired or revoked.
