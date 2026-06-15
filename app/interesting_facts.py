from dotenv import load_dotenv
from openai import OpenAI
from fact_history import load_fact_history, normalize_fact, remember_facts
from prompts import INTERESTING_FACTS_PROMPT

load_dotenv()

client = OpenAI()

FACT_EMOJIS = ("🐾", "🌌", "🔬", "🩺")

FALLBACK_FACT_BANK = {
    "🐾": [
        "🐾 Восьминоги можуть відкривати банки й розрізняти людей, хоча значна частина їхніх нейронів працює не в мозку, а в щупальцях.",
        "🐾 Деякі види мурах ведуть справжнє «сільське господарство», вирощуючи грибки як їжу для колонії.",
        "🐾 Морські видри тримаються за лапи під час відпочинку на воді, щоб течія не рознесла їх далеко одна від одної.",
    ],
    "🌌": [
        "🌌 На супутнику Сатурна Енцеладі з-під крижаної кори вириваються шлейфи водяної пари, тому він вважається перспективним місцем для пошуку умов, придатних для життя.",
        "🌌 Венера обертається навколо своєї осі так повільно, що її день довший за її рік.",
        "🌌 У міжзоряному просторі знайдено складні органічні молекули, що показує: хімія життя може починатися задовго до появи планет.",
    ],
    "🔬": [
        "🔬 Деякі бактерії здатні виробляти електричний струм, передаючи електрони назовні клітини через спеціальні білкові структури.",
        "🔬 Аерогелі можуть бути майже повністю повітряними за об'ємом, але все одно працювати як ефективні теплоізолятори.",
        "🔬 Графен завтовшки лише в один атом проводить електрику і тепло так добре, що його досліджують для гнучкої електроніки.",
    ],
    "🩺": [
        "🩺 Плацебо-ефект може працювати навіть тоді, коли людина знає, що отримує плацебо, якщо ритуал лікування підтримує очікування полегшення.",
        "🩺 Мікробіом кишківника бере участь не лише в травленні, а й у роботі імунної системи та обміні речовин.",
        "🩺 Під час загоєння рани клітини шкіри координовано рухаються до пошкодженої ділянки, ніби закриваючи її живою тканиною.",
    ],
}


def parse_fact_lines(text):
    facts = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        for emoji in FACT_EMOJIS:
            if line.startswith(emoji):
                facts[emoji] = line
                break
    return facts


def build_fact_section(facts):
    lines = ["🔎 Цікаві факти дня", ""]
    lines.extend(facts[emoji] for emoji in FACT_EMOJIS if emoji in facts)
    return "\n".join(lines)


def fill_unique_facts(generated_text, history):
    history_set = set(history)
    selected = {}
    generated_facts = parse_fact_lines(generated_text)

    for emoji in FACT_EMOJIS:
        fact = generated_facts.get(emoji)
        if fact and normalize_fact(fact) not in history_set:
            selected[emoji] = fact
            history_set.add(normalize_fact(fact))

    for emoji in FACT_EMOJIS:
        if emoji in selected:
            continue
        for fact in FALLBACK_FACT_BANK[emoji]:
            normalized = normalize_fact(fact)
            if normalized not in history_set:
                selected[emoji] = fact
                history_set.add(normalized)
                break

    if len(selected) < len(FACT_EMOJIS):
        for emoji in FACT_EMOJIS:
            selected.setdefault(emoji, FALLBACK_FACT_BANK[emoji][0])

    return build_fact_section(selected)


def generate_interesting_facts():
    history = load_fact_history()
    recent_history = "\n".join(f"- {fact}" for fact in history[-40:])

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
                    "content": (
                        "Generate today's lesser-known evergreen facts section. "
                        "Avoid obvious trivia and do not repeat these normalized previous facts:\n"
                        f"{recent_history}"
                    ),
                },
            ],
            temperature=0.8,
        )

        text = response.choices[0].message.content
        if not text:
            text = ""

        facts = fill_unique_facts(text, history)
    except Exception:
        facts = fill_unique_facts("", history)

    remember_facts(parse_fact_lines(facts).values())
    return facts
