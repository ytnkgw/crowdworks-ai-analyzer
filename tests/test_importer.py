import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from importer import load_jobs_from_json
from models import Job


def test_load_jobs_from_json_returns_empty_list_when_file_missing(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "jobs.json"

    jobs = load_jobs_from_json(missing_path)

    assert jobs == []


def test_load_jobs_from_json_loads_existing_json_file(tmp_path: Path) -> None:
    file_path = tmp_path / "jobs.json"
    payload = [
        {
            "id": 1,
            "title": "テスト案件",
            "url": "https://example.com/jobs/1",
        }
    ]
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    jobs = load_jobs_from_json(file_path)

    assert len(jobs) == 1
    assert isinstance(jobs[0], Job)
    assert jobs[0].id == 1
    assert jobs[0].title == "テスト案件"
    assert jobs[0].url == "https://example.com/jobs/1"


def test_load_jobs_from_json_loads_japanese_content(tmp_path: Path) -> None:
    file_path = tmp_path / "jobs_ja.json"
    payload = [
        {
            "id": 2,
            "title": "日本語タイトル",
            "url": "https://example.com/jobs/2",
            "description": "案件の説明文です。",
            "client_name": "株式会社テスト",
        }
    ]
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    jobs = load_jobs_from_json(file_path)

    assert jobs[0].title == "日本語タイトル"
    assert jobs[0].description == "案件の説明文です。"


def test_load_jobs_from_json_raises_value_error_when_root_is_not_list(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "invalid_root.json"
    payload = {
        "id": 1,
        "title": "配列ではないJSON",
    }
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError):
        load_jobs_from_json(file_path)


def test_load_jobs_from_json_restores_job_metadata(tmp_path: Path) -> None:
    file_path = tmp_path / "jobs_with_metadata.json"
    payload = [
        {
            "id": 3,
            "title": "metadata付き案件",
            "url": "https://example.com/jobs/3",
            "metadata": {
                "first_seen_at": "2026-07-05T00:00:00Z",
                "last_seen_at": "2026-07-05T01:00:00Z",
                "updated_at": "2026-07-05T01:00:00Z",
                "sources": [
                    {
                        "url": "https://crowdworks.jp/public/jobs/search?...",
                        "first_seen_at": "2026-07-05T00:00:00Z",
                        "last_seen_at": "2026-07-05T01:00:00Z",
                        "seen_count": 2,
                    }
                ],
            },
        }
    ]
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    jobs = load_jobs_from_json(file_path)

    assert jobs[0].metadata is not None
    assert jobs[0].metadata.first_seen_at == "2026-07-05T00:00:00Z"
    assert jobs[0].metadata.last_seen_at == "2026-07-05T01:00:00Z"
    assert jobs[0].metadata.updated_at == "2026-07-05T01:00:00Z"
    assert len(jobs[0].metadata.sources) == 1
    assert (
        jobs[0].metadata.sources[0].url
        == "https://crowdworks.jp/public/jobs/search?..."
    )
    assert jobs[0].metadata.sources[0].seen_count == 2
