import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from main import load_jobs_from_json
from models import Job


def test_load_jobs_from_json_creates_job_list(tmp_path: Path) -> None:
    output_path = tmp_path / "jobs.json"
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
            "application_count": 2,
            "contract_count": 0,
            "recruitment_count": 1,
            "favorite_count": 42,
        }
    ]
    output_path.write_text(json.dumps(payload), encoding="utf-8")

    jobs = load_jobs_from_json(output_path)

    assert len(jobs) == 1
    assert isinstance(jobs[0], Job)
    assert jobs[0].title == "テスト案件"
    assert jobs[0].category == "AI-BPO（AI活用の業務改善）"
    assert jobs[0].sub_category == "AIバックオフィス支援"
    assert jobs[0].application_count == 2
    assert jobs[0].contract_count == 0
    assert jobs[0].recruitment_count == 1
    assert jobs[0].favorite_count == 42
