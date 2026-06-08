# Good News Bot

Telegram bot that collects positive world news and sends uplifting stories daily.

## Features

- Fetches latest news
- Checks source quality before AI processing
- Removes duplicate stories by normalized URL and similar titles
- Searches science, environmental, and volunteering topics when fewer than three good stories are found
- Prioritizes animal stories, scientific breakthroughs, and everyday people helping others
- Uses AI to filter humane/uplifting stories
- Calculates a daily faith-in-humanity index from AI quality criteria
- Evaluates candidate stories by humanity, hope, warmth, credibility, and tragedy level
- Rejects toxic/ragebait content
- De-prioritizes corporate PR, product launches, awards, partnerships, and vague business positivity
- Creates warm summaries
- Generates a ready-to-publish Ukrainian Facebook post for a group
- Sends results to Telegram with category, title, summary, source trust level, source, original link, publish date, and country when available

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

## Faith In Humanity Index

Before sending the selected stories, the bot calculates a daily index:

```text
Сьогоднішній індекс віри в людство: 8.7/10
```

The index is calculated by AI from the final set of good news using these criteria:

- kindness
- impact on people
- long-term benefit
- inspiration
- scale

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

## AWS Lambda Deployment

This project is designed to run on AWS Lambda and be triggered by EventBridge Scheduler.

Lambda handler:

```text
app/lambda_function.lambda_handler
```

Required Lambda environment variables:

```env
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
NEWS_COUNTRY=us
```

Recommended runtime:

```text
Python 3.10+
```

### EventBridge Scheduler

Create an EventBridge Scheduler rule that invokes the Lambda once per day.

Example schedule for every morning at 07:00 in Berlin:

```text
cron(0 7 * * ? *)
```

Set the scheduler timezone to:

```text
Europe/Berlin
```

### Packaging

Install dependencies into a build folder and include the `app/` directory in the deployment package:

```bash
mkdir -p package
pip install -r requirements.txt -t package
cp -r app package/
cd package
zip -r ../good-news-bot.zip .
```

Upload `good-news-bot.zip` to Lambda, then set the handler to `app/lambda_function.lambda_handler`.

## Troubleshooting

If NewsAPI returns `401 Unauthorized`, the `NEWS_API_KEY` value was loaded but rejected. Check that the key is copied from your NewsAPI account, active, and not expired or revoked.
