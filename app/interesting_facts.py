from dotenv import load_dotenv
from openai import OpenAI
from prompts import INTERESTING_FACTS_PROMPT

load_dotenv()

client = OpenAI()

FALLBACK_FACTS = """🔎 Цікаві факти дня

🐾 Ворони здатні розпізнавати людські обличчя і запам'ятовувати, хто поводився з ними безпечно.
🌌 Світло від Сонця долітає до Землі приблизно за вісім хвилин.
🔬 ДНК у клітинах працює як інструкція, за якою організм будує і підтримує себе.
🩺 Регулярний сон допомагає мозку краще закріплювати пам'ять і відновлювати увагу."""


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
                    "content": "Generate today's evergreen facts section.",
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
