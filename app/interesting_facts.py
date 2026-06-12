from dotenv import load_dotenv
from openai import OpenAI
from prompts import INTERESTING_FACTS_PROMPT

load_dotenv()

client = OpenAI()

FALLBACK_FACTS = """🔎 Цікаві факти дня

🐾 Восьминоги можуть відкривати банки й розрізняти людей, хоча їхня нервова система розподілена так, що значна частина нейронів працює в щупальцях.
🌌 На супутнику Сатурна Енцеладі з-під крижаної кори вириваються шлейфи водяної пари, тому він вважається одним із найцікавіших місць для пошуку умов, придатних для життя.
🔬 Деякі бактерії здатні виробляти електричний струм, передаючи електрони назовні клітини через спеціальні білкові структури.
🩺 Плацебо-ефект може працювати навіть тоді, коли людина знає, що отримує плацебо, якщо ритуал лікування підтримує очікування полегшення."""


def generate_interesting_facts():
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": INTERESTING_FACTS_PROMPT,
                },
                {
                    "role": "user",
                    "content": "Generate today's lesser-known evergreen facts section. Avoid obvious trivia.",
                },
            ],
            temperature=0.5,
        )

        text = response.choices[0].message.content
        if not text:
            return FALLBACK_FACTS

        return text.strip()
    except Exception:
        return FALLBACK_FACTS
