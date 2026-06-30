import re


def extract_number(text: str | None) -> int | None:
    if text is None:
        return None

    match = re.search(r"\d+", text)
    return int(match.group()) if match else None
