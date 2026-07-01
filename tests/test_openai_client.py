import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from models import AnalysisResult, Job
import openai_client


def test_analyze_job_returns_analysis_result(monkeypatch: pytest.MonkeyPatch) -> None:
    job = Job(
        id=1,
        title="テスト案件",
        url="https://example.com/jobs/1",
        description="生成AIを使う案件です。",
        reward="5000円",
    )

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"reward_score": 4, "competition_score": 3, "ai_score": 5, "continuity_score": 4, "quality_score": 5, "total_score": 91, "recommendation_reasons": ["おすすめ"], "concerns": ["注意点"], "application_strategy": ["戦略"], "overall_comment": "良い案件です"}'
                )
            )
        ]
    )

    class FakeCompletions:
        def create(self, **kwargs):
            return fake_response

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(openai_client, "_CLIENT", FakeClient())
    monkeypatch.setenv("CW_AI_ANALYZER_OPENAI_API_KEY", "test-key")

    result = openai_client.analyze_job(job)

    assert isinstance(result, AnalysisResult)
    assert result.reward_score == 4
    assert result.total_score == 91
    assert result.recommendation_reasons == ["おすすめ"]
