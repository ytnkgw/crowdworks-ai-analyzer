import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from job_store import (
    build_job_index,
    has_meaningful_changes,
    initialize_job_metadata,
    update_job_if_changed,
    update_seen_metadata,
)
from models import Client, Job, JobMetadata, JobSourceMetadata


def test_build_job_index_returns_empty_dict_when_jobs_is_empty() -> None:
    index = build_job_index([])

    assert index == {}


def test_build_job_index_returns_id_keyed_dict() -> None:
    job1 = Job(id=1, title="案件1", url="https://example.com/jobs/1")
    job2 = Job(id=2, title="案件2", url="https://example.com/jobs/2")

    index = build_job_index([job1, job2])

    assert set(index.keys()) == {1, 2}
    assert index[1].title == "案件1"
    assert index[2].title == "案件2"


def test_build_job_index_values_are_original_job_objects() -> None:
    job = Job(id=10, title="同一参照確認", url="https://example.com/jobs/10")

    index = build_job_index([job])

    assert index[10] is job


def test_build_job_index_raises_value_error_when_duplicate_id_exists() -> None:
    job1 = Job(id=1, title="案件1", url="https://example.com/jobs/1")
    job2 = Job(id=1, title="案件1重複", url="https://example.com/jobs/1-dup")

    with pytest.raises(ValueError):
        build_job_index([job1, job2])


def _build_base_job() -> Job:
    return Job(
        id=1,
        title="案件タイトル",
        url="https://example.com/jobs/1",
        category="AI-BPO（AI活用の業務改善）",
        sub_category="AIバックオフィス支援",
        description="案件詳細本文",
        reward="ワーカーと相談する",
        application_deadline="2026年07月05日",
        published_at="2026年06月21日",
        delivery_deadline="2026年07月31日",
        is_remote=True,
        application_count=9,
        contract_count=0,
        recruitment_count=1,
        favorite_count=42,
        client=Client(
            id=6576565,
            name="デジハナ採用担当",
            rating=5.0,
            identity_verified=False,
            rule_checked=False,
            jobs_posted_count=32,
            project_finished_rate=75,
            profile_description="弊社沖縄発のSES企業でございます。",
        ),
    )


def test_has_meaningful_changes_returns_false_when_all_fields_equal() -> None:
    existing_job = _build_base_job()
    new_job = _build_base_job()

    assert has_meaningful_changes(existing_job, new_job) is False


def test_has_meaningful_changes_returns_true_when_title_changed() -> None:
    existing_job = _build_base_job()
    new_job = _build_base_job()
    new_job.title = "変更後タイトル"

    assert has_meaningful_changes(existing_job, new_job) is True


def test_has_meaningful_changes_returns_true_when_reward_changed() -> None:
    existing_job = _build_base_job()
    new_job = _build_base_job()
    new_job.reward = "固定報酬5,000円"

    assert has_meaningful_changes(existing_job, new_job) is True


def test_has_meaningful_changes_returns_true_when_application_deadline_changed() -> (
    None
):
    existing_job = _build_base_job()
    new_job = _build_base_job()
    new_job.application_deadline = "2026年07月06日"

    assert has_meaningful_changes(existing_job, new_job) is True


def test_has_meaningful_changes_returns_true_when_application_count_changed() -> None:
    existing_job = _build_base_job()
    new_job = _build_base_job()
    new_job.application_count = 10

    assert has_meaningful_changes(existing_job, new_job) is True


def test_has_meaningful_changes_returns_true_when_description_changed() -> None:
    existing_job = _build_base_job()
    new_job = _build_base_job()
    new_job.description = "更新後の案件詳細本文"

    assert has_meaningful_changes(existing_job, new_job) is True


def test_has_meaningful_changes_returns_true_when_client_changed() -> None:
    existing_job = _build_base_job()
    new_job = _build_base_job()
    new_job.client = Client(
        id=6576565,
        name="別クライアント名",
        rating=5.0,
        identity_verified=False,
        rule_checked=False,
        jobs_posted_count=32,
        project_finished_rate=75,
        profile_description="弊社沖縄発のSES企業でございます。",
    )

    assert has_meaningful_changes(existing_job, new_job) is True


def test_initialize_job_metadata_sets_metadata_on_job_without_metadata() -> None:
    now = "2026-07-05T12:34:56Z"
    source_url = "https://crowdworks.jp/public/jobs/search?..."
    job = Job(id=100, title="新規案件", url="https://example.com/jobs/100")

    updated = initialize_job_metadata(job, source_url, now)

    assert isinstance(updated, Job)
    assert updated.metadata is not None
    assert updated.metadata.first_seen_at == now
    assert updated.metadata.last_seen_at == now
    assert updated.metadata.updated_at == now
    assert len(updated.metadata.sources) == 1
    assert updated.metadata.sources[0].url == source_url
    assert updated.metadata.sources[0].first_seen_at == now
    assert updated.metadata.sources[0].last_seen_at == now
    assert updated.metadata.sources[0].seen_count == 1


def _build_job_with_metadata() -> Job:
    return Job(
        id=200,
        title="既存案件",
        url="https://example.com/jobs/200",
        metadata=JobMetadata(
            first_seen_at="2026-07-01T00:00:00Z",
            last_seen_at="2026-07-02T00:00:00Z",
            updated_at="2026-07-03T00:00:00Z",
            sources=[
                JobSourceMetadata(
                    url="https://crowdworks.jp/public/jobs/search?keyword=ai",
                    first_seen_at="2026-07-01T00:00:00Z",
                    last_seen_at="2026-07-02T00:00:00Z",
                    seen_count=2,
                )
            ],
        ),
    )


def test_update_seen_metadata_initializes_when_metadata_is_none() -> None:
    now = "2026-07-05T12:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    job = Job(id=300, title="新規案件", url="https://example.com/jobs/300")

    updated = update_seen_metadata(job, source_url, now)

    assert updated.metadata is not None
    assert updated.metadata.first_seen_at == now
    assert updated.metadata.last_seen_at == now
    assert updated.metadata.updated_at == now
    assert len(updated.metadata.sources) == 1
    assert updated.metadata.sources[0].url == source_url
    assert updated.metadata.sources[0].first_seen_at == now
    assert updated.metadata.sources[0].last_seen_at == now
    assert updated.metadata.sources[0].seen_count == 1


def test_update_seen_metadata_updates_metadata_last_seen_at() -> None:
    now = "2026-07-05T13:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    job = _build_job_with_metadata()

    updated = update_seen_metadata(job, source_url, now)

    assert updated.metadata is not None
    assert updated.metadata.last_seen_at == now


def test_update_seen_metadata_does_not_update_metadata_updated_at() -> None:
    now = "2026-07-05T13:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    job = _build_job_with_metadata()
    previous_updated_at = job.metadata.updated_at

    updated = update_seen_metadata(job, source_url, now)

    assert updated.metadata is not None
    assert updated.metadata.updated_at == previous_updated_at


def test_update_seen_metadata_updates_existing_source_last_seen_at() -> None:
    now = "2026-07-05T13:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    job = _build_job_with_metadata()

    updated = update_seen_metadata(job, source_url, now)

    assert updated.metadata is not None
    assert updated.metadata.sources[0].last_seen_at == now


def test_update_seen_metadata_increments_existing_source_seen_count() -> None:
    now = "2026-07-05T13:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    job = _build_job_with_metadata()

    updated = update_seen_metadata(job, source_url, now)

    assert updated.metadata is not None
    assert updated.metadata.sources[0].seen_count == 3


def test_update_seen_metadata_keeps_existing_source_first_seen_at() -> None:
    now = "2026-07-05T13:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    job = _build_job_with_metadata()
    previous_first_seen_at = job.metadata.sources[0].first_seen_at

    updated = update_seen_metadata(job, source_url, now)

    assert updated.metadata is not None
    assert updated.metadata.sources[0].first_seen_at == previous_first_seen_at


def test_update_seen_metadata_appends_new_source_when_url_not_found() -> None:
    now = "2026-07-05T13:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=python"
    job = _build_job_with_metadata()

    updated = update_seen_metadata(job, source_url, now)

    assert updated.metadata is not None
    assert len(updated.metadata.sources) == 2
    new_source = updated.metadata.sources[1]
    assert new_source.url == source_url
    assert new_source.first_seen_at == now
    assert new_source.last_seen_at == now
    assert new_source.seen_count == 1


def _build_existing_job_for_update_test() -> Job:
    return Job(
        id=400,
        title="既存タイトル",
        url="https://example.com/jobs/400",
        category="カテゴリA",
        sub_category="サブA",
        description="既存説明",
        reward="1000円",
        application_deadline="2026-07-10",
        published_at="2026-07-01",
        delivery_deadline="2026-07-31",
        is_remote=True,
        application_count=3,
        contract_count=0,
        recruitment_count=1,
        favorite_count=10,
        client=Client(id=1, name="既存クライアント"),
        metadata=JobMetadata(
            first_seen_at="2026-07-01T00:00:00Z",
            last_seen_at="2026-07-05T00:00:00Z",
            updated_at="2026-07-05T00:00:00Z",
            sources=[
                JobSourceMetadata(
                    url="https://crowdworks.jp/public/jobs/search?keyword=ai",
                    first_seen_at="2026-07-01T00:00:00Z",
                    last_seen_at="2026-07-05T00:00:00Z",
                    seen_count=2,
                )
            ],
        ),
    )


def _build_new_job_for_update_test() -> Job:
    return Job(
        id=400,
        title="既存タイトル",
        url="https://example.com/jobs/400",
        category="カテゴリA",
        sub_category="サブA",
        description="既存説明",
        reward="1000円",
        application_deadline="2026-07-10",
        published_at="2026-07-01",
        delivery_deadline="2026-07-31",
        is_remote=True,
        application_count=3,
        contract_count=0,
        recruitment_count=1,
        favorite_count=10,
        client=Client(id=1, name="既存クライアント"),
    )


def test_update_job_if_changed_returns_existing_job_without_changes() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated is existing_job
    assert updated.title == "既存タイトル"


def test_update_job_if_changed_does_not_update_updated_at_without_changes() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    previous_updated_at = existing_job.metadata.updated_at

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.updated_at == previous_updated_at


def test_update_job_if_changed_updates_title_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.title = "更新タイトル"

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.title == "更新タイトル"


def test_update_job_if_changed_updates_reward_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.reward = "3000円"

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.reward == "3000円"


def test_update_job_if_changed_updates_application_count_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.application_count = 8

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.application_count == 8


def test_update_job_if_changed_updates_client_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.client = Client(id=2, name="更新クライアント")

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.client == new_job.client


def test_update_job_if_changed_updates_metadata_updated_at_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.title = "更新タイトル"

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.updated_at == now


def test_update_job_if_changed_keeps_metadata_first_seen_at_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.title = "更新タイトル"
    previous_first_seen_at = existing_job.metadata.first_seen_at

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.first_seen_at == previous_first_seen_at


def test_update_job_if_changed_keeps_metadata_last_seen_at_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.title = "更新タイトル"
    previous_last_seen_at = existing_job.metadata.last_seen_at

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.last_seen_at == previous_last_seen_at


def test_update_job_if_changed_keeps_metadata_sources_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.title = "更新タイトル"
    previous_sources = existing_job.metadata.sources

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.sources is previous_sources
