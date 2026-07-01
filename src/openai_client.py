import json

from openai import OpenAI
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from config import OPENAI_API_KEY, OPENAI_MODEL
from models import AnalysisResult, Job
from prompt_builder import build_system_prompt, build_user_prompt

_CLIENT: OpenAI | None = None


def get_client() -> OpenAI:
    """OpenAI clientを取得する。"""

    global _CLIENT

    if _CLIENT is None:
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not set")

        _CLIENT = OpenAI(api_key=OPENAI_API_KEY)

    return _CLIENT


def analyze_job(job: Job) -> AnalysisResult:
    """案件情報を OpenAI API で分析し、AnalysisResult を返す。"""

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(job)

    try:
        response = get_client().chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
    except APITimeoutError as exc:
        raise RuntimeError("OpenAI API request timed out") from exc
    except RateLimitError as exc:
        raise RuntimeError("OpenAI API rate limit exceeded") from exc
    except APIConnectionError as exc:
        raise RuntimeError("OpenAI API connection failed") from exc
    except APIStatusError as exc:
        raise RuntimeError("OpenAI API returned an error status") from exc
    except Exception as exc:
        raise RuntimeError("OpenAI API request failed") from exc

    if not response.choices:
        raise ValueError("OpenAI response did not contain any choices")

    content = response.choices[0].message.content

    if not content:
        raise ValueError("OpenAI response did not contain any content")

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("OpenAI response was not valid JSON") from exc

    try:
        return AnalysisResult.from_dict(payload)
    except ValueError as exc:
        raise ValueError("OpenAI response did not match AnalysisResult schema") from exc
