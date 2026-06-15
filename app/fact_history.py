import json
import os
import re

PARAMETER_NAME = os.getenv("FACT_HISTORY_SSM_PARAMETER", "/good-news-bot/interesting-facts-history")
MAX_FACT_HISTORY = int(os.getenv("MAX_FACT_HISTORY", "120"))


def normalize_fact(fact):
    normalized = re.sub(r"^[^\wА-Яа-яІіЇїЄєҐґ]+", "", fact or "")
    normalized = normalized.lower()
    normalized = re.sub(r"[^\w\sА-Яа-яІіЇїЄєҐґ]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def get_ssm_client():
    try:
        import boto3
    except ImportError:
        return None

    return boto3.client("ssm")


def load_fact_history():
    client = get_ssm_client()
    if client is None:
        return []

    try:
        response = client.get_parameter(Name=PARAMETER_NAME)
        data = json.loads(response["Parameter"]["Value"])
        return data.get("facts", [])
    except client.exceptions.ParameterNotFound:
        return []
    except Exception:
        return []


def save_fact_history(facts):
    client = get_ssm_client()
    if client is None:
        return

    unique_facts = []
    for fact in facts:
        if fact and fact not in unique_facts:
            unique_facts.append(fact)

    payload = {
        "facts": unique_facts[-MAX_FACT_HISTORY:],
    }

    try:
        client.put_parameter(
            Name=PARAMETER_NAME,
            Value=json.dumps(payload, ensure_ascii=False),
            Type="String",
            Overwrite=True,
        )
    except Exception:
        return


def remember_facts(facts):
    history = load_fact_history()
    normalized_facts = [normalize_fact(fact) for fact in facts]
    save_fact_history(history + normalized_facts)
