import os

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=BOT_TOKEN)


async def send_message(text):
    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        disable_web_page_preview=False
    )
