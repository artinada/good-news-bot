# Good News Bot

Telegram bot that collects positive world news and sends uplifting stories daily.

## Features

- Fetches latest news
- Uses AI to filter humane/uplifting stories
- Rejects toxic/ragebait content
- Creates warm summaries
- Sends results to Telegram

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
```

### 4. Run

```bash
python app/main.py
```
