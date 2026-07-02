import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from exporter import (
    build_job_analysis_item,
    export_job_analysis_results,
    export_jobs_to_json,
)
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


def test_export_jobs_to_json_includes_detail_fields(tmp_path: Path) -> None:
    jobs = [
        Job(
            id=13253877,
            title="案件タイトル",
            url="https://crowdworks.jp/public/jobs/13253877",
            category="AI-BPO（AI活用の業務改善）",
            sub_category="AIバックオフィス支援",
            description="案件詳細本文",
            reward="ワーカーと相談する",
            application_deadline="2026年07月05日",
            published_at="2026年06月21日",
            application_count=9,
            contract_count=0,
            recruitment_count=1,
            favorite_count=42,
        )
    ]

    output_path = tmp_path / "jobs.json"
    export_jobs_to_json(jobs, output_path)

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert written[0]["id"] == 13253877
    assert written[0]["title"] == "案件タイトル"
    assert written[0]["url"] == "https://crowdworks.jp/public/jobs/13253877"
    assert written[0]["category"] == "AI-BPO（AI活用の業務改善）"
    assert written[0]["sub_category"] == "AIバックオフィス支援"
    assert written[0]["description"] == "案件詳細本文"
    assert written[0]["reward"] == "ワーカーと相談する"
    assert written[0]["application_deadline"] == "2026年07月05日"
    assert written[0]["published_at"] == "2026年06月21日"
    assert written[0]["application_count"] == 9
    assert written[0]["contract_count"] == 0
    assert written[0]["recruitment_count"] == 1
    assert written[0]["favorite_count"] == 42
