import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from exporter import build_job_analysis_item, export_job_analysis_results
from models import AnalysisResult, Job


def test_build_job_analysis_item_creates_expected_dict() -> None:
    job = Job(
        id=13253877,
        title="案件タイトル",
        url="https://crowdworks.jp/public/jobs/13253877",
    )
    analysis = AnalysisResult(
        reward_score=4,
        competition_score=3,
        ai_score=5,
        continuity_score=4,
        quality_score=5,
        total_score=91,
        recommendation_reasons=["生成AIを活用できる案件である"],
        concerns=["応募人数が多く競争率が高い"],
        application_strategy=["AI活用経験を具体例付きでアピールする"],
        overall_comment="AIスキルとの親和性が高く、応募価値の高い案件です。",
    )

    item = build_job_analysis_item(job, analysis)

    assert item["job"]["id"] == job.id
    assert item["analysis"]["total_score"] == analysis.total_score
    assert item["analysis"]["recommendation_reasons"] == analysis.recommendation_reasons


def test_export_job_analysis_results_writes_expected_json(tmp_path: Path) -> None:
    print(tmp_path)
    output_path = tmp_path / "analysis_results.json"
    items = [
        {
            "job": {
                "id": 13253877,
                "title": "案件タイトル",
                "url": "https://crowdworks.jp/public/jobs/13253877",
            },
            "analysis": {
                "reward_score": 4,
                "competition_score": 3,
                "ai_score": 5,
                "continuity_score": 4,
                "quality_score": 5,
                "total_score": 91,
                "recommendation_reasons": ["生成AIを活用できる案件である"],
                "concerns": ["応募人数が多く競争率が高い"],
                "application_strategy": ["AI活用経験を具体例付きでアピールする"],
                "overall_comment": "AIスキルとの親和性が高く、応募価値の高い案件です。",
            },
        }
    ]

    export_job_analysis_results(items, output_path)

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert written == items
