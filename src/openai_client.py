import json
import os

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from models import AnalysisResult, Job
from prompt_builder import build_system_prompt, build_user_prompt

CLIENT = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def analyze_job(job: Job) -> AnalysisResult:
    """案件情報を OpenAI API で分析し、AnalysisResult を返す。"""

    if not OPENAI_API_KEY or CLIENT is None:
        raise ValueError("OpenAI API key is not set")

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(job)

    response = CLIENT.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI response did not contain any content")

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("OpenAI response was not valid JSON") from exc

    return AnalysisResult.from_dict(payload)
