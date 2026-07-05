from dataclasses import asdict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from models import Job, JobMetadata, JobSourceMetadata


def test_job_can_be_created_without_metadata() -> None:
    job = Job(id=1, title="案件タイトル", url="https://example.com/jobs/1")

    assert job.metadata is None


def test_job_can_be_created_with_metadata() -> None:
    metadata = JobMetadata(
        first_seen_at="2026-07-05T00:00:00Z",
        last_seen_at="2026-07-05T01:00:00Z",
        updated_at="2026-07-05T01:00:00Z",
        sources=[
            JobSourceMetadata(
                url="https://crowdworks.jp/public/jobs/search?...",
                first_seen_at="2026-07-05T00:00:00Z",
                last_seen_at="2026-07-05T01:00:00Z",
            )
        ],
    )
    job = Job(
        id=1,
        title="案件タイトル",
        url="https://example.com/jobs/1",
        metadata=metadata,
    )

    assert job.metadata is metadata
    assert job.metadata.first_seen_at == "2026-07-05T00:00:00Z"


def test_job_metadata_sources_default_is_empty_list() -> None:
    metadata = JobMetadata()

    assert metadata.sources == []


def test_job_source_metadata_seen_count_default_is_one() -> None:
    source = JobSourceMetadata(
        url="https://crowdworks.jp/public/jobs/search?...",
        first_seen_at="2026-07-05T00:00:00Z",
        last_seen_at="2026-07-05T00:00:00Z",
    )

    assert source.seen_count == 1


def test_asdict_job_includes_metadata() -> None:
    job = Job(
        id=1,
        title="案件タイトル",
        url="https://example.com/jobs/1",
        metadata=JobMetadata(
            first_seen_at="2026-07-05T00:00:00Z",
            last_seen_at="2026-07-05T00:00:00Z",
            updated_at="2026-07-05T00:00:00Z",
            sources=[
                JobSourceMetadata(
                    url="https://crowdworks.jp/public/jobs/search?...",
                    first_seen_at="2026-07-05T00:00:00Z",
                    last_seen_at="2026-07-05T00:00:00Z",
                )
            ],
        ),
    )

    payload = asdict(job)

    assert "metadata" in payload
    assert payload["metadata"]["first_seen_at"] == "2026-07-05T00:00:00Z"
    assert payload["metadata"]["sources"][0]["seen_count"] == 1
