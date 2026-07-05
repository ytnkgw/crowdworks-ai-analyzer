import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import config
from importer import load_jobs_from_json
from models import Job


def test_load_jobs_from_json_creates_job_list(tmp_path: Path) -> None:
    output_path = tmp_path / config.OUTPUT_JOBS_FILENAME
    payload = [
        {
            "id": 1,
            "title": "テスト案件",
            "url": "https://example.com/jobs/1",
            "category": "AI-BPO（AI活用の業務改善）",
            "sub_category": "AIバックオフィス支援",
            "description": "説明",
            "reward": "1000円",
            "application_deadline": None,
            "published_at": None,
            "delivery_deadline": None,
            "is_remote": True,
            "application_count": 2,
            "contract_count": 0,
            "recruitment_count": 1,
            "favorite_count": 42,
            "client": {
                "id": 6576565,
                "name": "デジハナ採用担当",
                "rating": 5.0,
                "identity_verified": False,
                "rule_checked": False,
                "jobs_posted_count": 32,
                "project_finished_rate": 75,
                "profile_description": "弊社沖縄発のSES企業でございます。",
            },
        }
    ]
    output_path.write_text(json.dumps(payload), encoding="utf-8")

    jobs = load_jobs_from_json(output_path)

    assert len(jobs) == 1
    assert isinstance(jobs[0], Job)
    assert jobs[0].title == "テスト案件"
    assert jobs[0].category == "AI-BPO（AI活用の業務改善）"
    assert jobs[0].sub_category == "AIバックオフィス支援"
    assert jobs[0].delivery_deadline is None
    assert jobs[0].is_remote is True
    assert jobs[0].application_count == 2
    assert jobs[0].contract_count == 0
    assert jobs[0].recruitment_count == 1
    assert jobs[0].favorite_count == 42
    assert jobs[0].client is not None
    assert jobs[0].client.id == 6576565
    assert jobs[0].client.name == "デジハナ採用担当"
    assert jobs[0].client.rating == 5.0
    assert jobs[0].client.identity_verified is False
    assert jobs[0].client.rule_checked is False
    assert jobs[0].client.jobs_posted_count == 32
    assert jobs[0].client.project_finished_rate == 75
    assert jobs[0].client.profile_description == "弊社沖縄発のSES企業でございます。"
