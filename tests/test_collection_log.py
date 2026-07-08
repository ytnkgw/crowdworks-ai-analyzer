import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import config
import job_collector
import main


def _read_collection_log_records(output_dir: Path) -> list[dict]:
    log_files = list((output_dir / "logs").glob("collection_log_*.jsonl"))
    assert len(log_files) == 1

    return [
        json.loads(line)
        for line in log_files[0].read_text(encoding="utf-8").splitlines()
    ]


def test_main_collect_jobs_writes_success_collection_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    def fake_collect_jobs_from_url(
        url: str, limit: int | None = None
    ) -> list[job_collector.Job]:
        return [
            job_collector.Job(
                id=1,
                title="案件A",
                url="https://example.com/jobs/1",
            )
        ]

    monkeypatch.setattr(main, "collect_jobs_from_url", fake_collect_jobs_from_url)

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(
            [
                "--collect-jobs",
                "--url",
                "https://example.com/public/jobs/group/development",
                "--limit",
                "5",
            ]
        )

    assert exit_code == 0

    records = _read_collection_log_records(output_dir)
    assert len(records) == 1

    record = records[0]
    assert record["source_url"] == "https://example.com/public/jobs/group/development"
    assert record["status"] == "success"
    assert record["limit"] == 5
    assert record["collected_count"] == 1
    assert record["added_count"] == 1
    assert record["updated_count"] == 0
    assert record["expired_removed_count"] == 0
    assert record["saved_count"] == 1
    assert isinstance(record["started_at"], str)
    assert isinstance(record["finished_at"], str)
    assert isinstance(record["duration_seconds"], float)
    assert "Saved collection log:" in output.getvalue()


def test_main_collect_jobs_writes_error_collection_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    def fake_collect_jobs_from_url(
        url: str, limit: int | None = None
    ) -> list[job_collector.Job]:
        raise RuntimeError("collection failed")

    monkeypatch.setattr(main, "collect_jobs_from_url", fake_collect_jobs_from_url)

    output = io.StringIO()
    with pytest.raises(RuntimeError), redirect_stdout(output):
        main.main(
            [
                "--collect-jobs",
                "--url",
                "https://example.com/public/jobs/group/development",
                "--limit",
                "5",
            ]
        )

    records = _read_collection_log_records(output_dir)
    assert len(records) == 1

    record = records[0]
    assert record["source_url"] == "https://example.com/public/jobs/group/development"
    assert record["status"] == "error"
    assert record["limit"] == 5
    assert record["error_type"] == "RuntimeError"
    assert record["error_message"] == "collection failed"
    assert isinstance(record["started_at"], str)
    assert isinstance(record["finished_at"], str)
    assert isinstance(record["duration_seconds"], float)
    assert "Saved collection log:" in output.getvalue()
