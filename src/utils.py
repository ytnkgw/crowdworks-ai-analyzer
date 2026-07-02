import re


def extract_number(text: str | None) -> int | None:
    if text is None:
        return None

    normalized = text.strip()
    if not normalized or normalized == "-":
        return None

    normalized = normalized.replace(",", "")

    match = re.search(r"\d+", normalized)
    return int(match.group()) if match else None
