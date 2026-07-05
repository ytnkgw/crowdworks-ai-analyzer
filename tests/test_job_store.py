from datetime import date
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from job_store import (
    build_job_index,
    has_meaningful_changes,
    initialize_job_metadata,
    merge_jobs,
    remove_expired_jobs,
    update_job_if_changed,
    update_job_store,
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


def test_initialize_job_metadata_does_nothing_when_metadata_already_exists() -> None:
    now = "2026-07-05T12:34:56Z"
    source_url = "https://crowdworks.jp/public/jobs/search?..."
    existing_source = JobSourceMetadata(
        url="https://crowdworks.jp/public/jobs/search?keyword=ai",
        first_seen_at="2026-07-01T00:00:00Z",
        last_seen_at="2026-07-02T00:00:00Z",
        seen_count=2,
    )
    job = Job(
        id=101,
        title="既存metadata案件",
        url="https://example.com/jobs/101",
        metadata=JobMetadata(
            first_seen_at="2026-07-01T00:00:00Z",
            last_seen_at="2026-07-02T00:00:00Z",
            updated_at="2026-07-03T00:00:00Z",
            sources=[existing_source],
        ),
    )

    previous_metadata = job.metadata
    updated = initialize_job_metadata(job, source_url, now)

    assert updated is job
    assert updated.metadata is previous_metadata
    assert updated.metadata is not None
    assert updated.metadata.first_seen_at == "2026-07-01T00:00:00Z"
    assert updated.metadata.last_seen_at == "2026-07-02T00:00:00Z"
    assert updated.metadata.updated_at == "2026-07-03T00:00:00Z"
    assert len(updated.metadata.sources) == 1
    assert updated.metadata.sources[0] is existing_source


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
    assert job.metadata is not None
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
    assert job.metadata is not None
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
    assert existing_job.metadata is not None
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
    assert existing_job.metadata is not None
    previous_first_seen_at = existing_job.metadata.first_seen_at

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.first_seen_at == previous_first_seen_at


def test_update_job_if_changed_keeps_metadata_last_seen_at_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.title = "更新タイトル"
    assert existing_job.metadata is not None
    previous_last_seen_at = existing_job.metadata.last_seen_at

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.last_seen_at == previous_last_seen_at


def test_update_job_if_changed_keeps_metadata_sources_when_changed() -> None:
    now = "2026-07-06T00:00:00Z"
    existing_job = _build_existing_job_for_update_test()
    new_job = _build_new_job_for_update_test()
    new_job.title = "更新タイトル"
    assert existing_job.metadata is not None
    previous_sources = existing_job.metadata.sources

    updated = update_job_if_changed(existing_job, new_job, now)

    assert updated.metadata is not None
    assert updated.metadata.sources is previous_sources


def test_merge_jobs_adds_collected_jobs_when_existing_is_empty() -> None:
    now = "2026-07-07T00:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    collected_jobs = [
        Job(id=1, title="新規1", url="https://example.com/jobs/1"),
        Job(id=2, title="新規2", url="https://example.com/jobs/2"),
    ]

    merged = merge_jobs([], collected_jobs, source_url, now)

    assert [job.id for job in merged] == [1, 2]


def test_merge_jobs_initializes_metadata_for_new_job() -> None:
    now = "2026-07-07T00:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    collected_job = Job(id=3, title="新規3", url="https://example.com/jobs/3")

    merged = merge_jobs([], [collected_job], source_url, now)

    assert merged[0].metadata is not None
    assert merged[0].metadata.first_seen_at == now
    assert merged[0].metadata.last_seen_at == now
    assert merged[0].metadata.updated_at == now
    assert len(merged[0].metadata.sources) == 1
    assert merged[0].metadata.sources[0].url == source_url


def test_merge_jobs_does_not_duplicate_when_id_already_exists() -> None:
    now = "2026-07-07T00:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    existing_job = _build_job_with_metadata()
    existing_job.id = 10
    collected_job = Job(id=10, title="既存案件", url="https://example.com/jobs/200")

    merged = merge_jobs([existing_job], [collected_job], source_url, now)

    assert len(merged) == 1
    assert merged[0] is existing_job


def test_merge_jobs_updates_last_seen_and_seen_count_for_existing_job() -> None:
    now = "2026-07-07T01:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    existing_job = _build_job_with_metadata()
    existing_job.id = 11
    assert existing_job.metadata is not None
    previous_seen_count = existing_job.metadata.sources[0].seen_count
    collected_job = Job(id=11, title="既存案件", url="https://example.com/jobs/200")

    merged = merge_jobs([existing_job], [collected_job], source_url, now)

    assert merged[0].metadata is not None
    assert merged[0].metadata.last_seen_at == now
    assert merged[0].metadata.sources[0].seen_count == previous_seen_count + 1


def test_merge_jobs_updates_existing_job_body_and_updated_at_when_changed() -> None:
    now = "2026-07-07T02:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    existing_job = _build_existing_job_for_update_test()
    collected_job = _build_new_job_for_update_test()
    collected_job.title = "変更後タイトル"
    collected_job.reward = "5000円"

    merged = merge_jobs([existing_job], [collected_job], source_url, now)

    assert merged[0].title == "変更後タイトル"
    assert merged[0].reward == "5000円"
    assert merged[0].metadata is not None
    assert merged[0].metadata.updated_at == now


def test_merge_jobs_keeps_uncollected_existing_jobs() -> None:
    now = "2026-07-07T03:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    existing1 = _build_existing_job_for_update_test()
    existing1.id = 20
    existing2 = _build_existing_job_for_update_test()
    existing2.id = 21
    collected_jobs = [
        Job(id=20, title="既存タイトル", url="https://example.com/jobs/400")
    ]

    merged = merge_jobs([existing1, existing2], collected_jobs, source_url, now)

    assert [job.id for job in merged] == [20, 21]


def test_merge_jobs_preserves_existing_order_and_appends_new_jobs_to_end() -> None:
    now = "2026-07-07T04:00:00Z"
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    existing1 = _build_existing_job_for_update_test()
    existing1.id = 30
    existing2 = _build_existing_job_for_update_test()
    existing2.id = 31
    collected_jobs = [
        Job(id=31, title="既存タイトル", url="https://example.com/jobs/400"),
        Job(id=32, title="新規32", url="https://example.com/jobs/32"),
        Job(id=33, title="新規33", url="https://example.com/jobs/33"),
    ]

    merged = merge_jobs([existing1, existing2], collected_jobs, source_url, now)

    assert [job.id for job in merged] == [30, 31, 32, 33]


def test_remove_expired_jobs_excludes_expired_jobs() -> None:
    jobs = [
        Job(
            id=1,
            title="期限切れ",
            url="https://example.com/jobs/1",
            application_deadline="2026年07月01日",
        ),
        Job(
            id=2,
            title="期限内",
            url="https://example.com/jobs/2",
            application_deadline="2026年07月03日",
        ),
    ]

    filtered = remove_expired_jobs(jobs, today=date(2026, 7, 2))

    assert [job.id for job in filtered] == [2]


def test_remove_expired_jobs_keeps_jobs_with_no_deadline() -> None:
    jobs = [
        Job(
            id=3,
            title="期限不明",
            url="https://example.com/jobs/3",
            application_deadline=None,
        )
    ]

    filtered = remove_expired_jobs(jobs, today=date(2026, 7, 2))

    assert [job.id for job in filtered] == [3]


def test_remove_expired_jobs_keeps_jobs_with_unparseable_deadline() -> None:
    jobs = [
        Job(
            id=4,
            title="解析不能期限",
            url="https://example.com/jobs/4",
            application_deadline="応募期限未定",
        )
    ]

    filtered = remove_expired_jobs(jobs, today=date(2026, 7, 2))

    assert [job.id for job in filtered] == [4]


def test_remove_expired_jobs_preserves_original_order() -> None:
    jobs = [
        Job(
            id=5,
            title="期限内A",
            url="https://example.com/jobs/5",
            application_deadline="2026年07月03日",
        ),
        Job(
            id=6,
            title="期限切れ",
            url="https://example.com/jobs/6",
            application_deadline="2026年07月01日",
        ),
        Job(
            id=7,
            title="期限内B",
            url="https://example.com/jobs/7",
            application_deadline="2026年07月04日",
        ),
        Job(
            id=8,
            title="期限なし",
            url="https://example.com/jobs/8",
            application_deadline=None,
        ),
        Job(
            id=9,
            title="解析不能",
            url="https://example.com/jobs/9",
            application_deadline="応募期限未定",
        ),
    ]

    filtered = remove_expired_jobs(jobs, today=date(2026, 7, 2))

    assert [job.id for job in filtered] == [5, 7, 8, 9]


def test_update_job_store_adds_new_updates_existing_and_removes_expired() -> None:
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    now = "2026-07-08T00:00:00Z"
    today = date(2026, 7, 2)

    existing_job = _build_existing_job_for_update_test()
    existing_job.id = 50
    existing_job.title = "既存タイトル"
    existing_job.application_deadline = "2026年07月10日"

    collected_updated = _build_new_job_for_update_test()
    collected_updated.id = 50
    collected_updated.title = "更新後タイトル"
    collected_updated.application_deadline = "2026年07月10日"

    collected_new_alive = Job(
        id=51,
        title="新規期限内",
        url="https://example.com/jobs/51",
        application_deadline="2026年07月03日",
    )
    collected_new_expired = Job(
        id=52,
        title="新規期限切れ",
        url="https://example.com/jobs/52",
        application_deadline="2026年07月01日",
    )

    updated = update_job_store(
        [existing_job],
        [collected_updated, collected_new_alive, collected_new_expired],
        source_url,
        now,
        today=today,
    )

    assert [job.id for job in updated] == [50, 51]
    assert updated[0].title == "更新後タイトル"
    assert updated[1].metadata is not None


def test_update_job_store_keeps_uncollected_existing_job_if_not_expired() -> None:
    source_url = "https://crowdworks.jp/public/jobs/search?keyword=ai"
    now = "2026-07-08T00:00:00Z"
    today = date(2026, 7, 2)

    existing_collected = _build_existing_job_for_update_test()
    existing_collected.id = 60
    existing_collected.application_deadline = "2026年07月03日"

    existing_uncollected = _build_existing_job_for_update_test()
    existing_uncollected.id = 61
    existing_uncollected.application_deadline = "2026年07月04日"

    collected = [
        Job(
            id=60,
            title="既存タイトル",
            url="https://example.com/jobs/400",
            application_deadline="2026年07月03日",
        )
    ]

    updated = update_job_store(
        [existing_collected, existing_uncollected],
        collected,
        source_url,
        now,
        today=today,
    )

    assert [job.id for job in updated] == [60, 61]
