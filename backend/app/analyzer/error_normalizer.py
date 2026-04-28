import json
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""

    return str(text).replace("\r", " ").replace("\n", " ").strip()


def parse_json_text(text: Optional[str]):
    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        return None


def extract_error_from_result_data(test_result_data: Optional[str]) -> str:
    if not test_result_data:
        return ""

    obj = parse_json_text(test_result_data)
    if obj is None:
        return clean_text(test_result_data)

    if isinstance(obj, dict):
        error_data = obj.get("errorData")
        if isinstance(error_data, list):
            return clean_text(" | ".join([str(x) for x in error_data if x]))

        if isinstance(error_data, str):
            return clean_text(error_data)

        if obj.get("message"):
            return clean_text(obj.get("message"))

    return clean_text(test_result_data)


def normalize_error(error_text: Optional[str]) -> dict:
    raw_error = clean_text(error_text)
    clean_error = raw_error.lower()

    return {
        "raw_error": raw_error,
        "clean_error": clean_error,
        "match_text": clean_error,
    }


def shorten_text(text: Optional[str], limit: int = 220) -> str:
    value = clean_text(text)

    if len(value) <= limit:
        return value

    return value[:limit] + "..."
