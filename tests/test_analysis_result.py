import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from models import AnalysisResult


@pytest.fixture
def sample_data() -> dict:
    sample_path = (
        Path(__file__).resolve().parent / "data" / "prompt_design_doc_sample.json"
    )
    with sample_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_analysis_result_from_dict_creates_expected_object(sample_data: dict) -> None:
    result = AnalysisResult.from_dict(sample_data)

    assert result.reward_score == sample_data["reward_score"]
    assert result.competition_score == sample_data["competition_score"]
    assert result.ai_score == sample_data["ai_score"]
    assert result.continuity_score == sample_data["continuity_score"]
    assert result.quality_score == sample_data["quality_score"]
    assert result.total_score == sample_data["total_score"]
    assert result.recommendation_reasons == sample_data["recommendation_reasons"]
    assert result.concerns == sample_data["concerns"]
    assert result.application_strategy == sample_data["application_strategy"]
    assert result.overall_comment == sample_data["overall_comment"]


def test_analysis_result_from_dict_raises_for_missing_keys() -> None:
    incomplete_data = {
        "reward_score": 4,
        "competition_score": 3,
        "ai_score": 5,
        "continuity_score": 4,
        "quality_score": 5,
        "total_score": 91,
    }

    with pytest.raises(ValueError, match="Missing required keys"):
        AnalysisResult.from_dict(incomplete_data)
