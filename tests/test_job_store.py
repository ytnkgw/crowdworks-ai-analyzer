import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from job_store import build_job_index, has_meaningful_changes
from models import Client, Job


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
