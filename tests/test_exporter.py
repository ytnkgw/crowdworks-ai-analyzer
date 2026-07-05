import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import config
from exporter import (
    build_raw_jobs_filename,
    build_job_analysis_item,
    export_job_analysis_results,
    export_jobs_for_ai_jsonl,
    export_jobs_to_json,
    save_jobs_snapshot,
    save_raw_jobs,
)
from models import (
    AnalysisResult,
    Client,
    Job,
    JobMetadata,
    JobSourceMetadata,
)


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
    output_path = tmp_path / config.OUTPUT_ANALYSIS_RESULTS_FILENAME
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
            delivery_deadline=None,
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
    ]

    output_path = tmp_path / config.OUTPUT_JOBS_FILENAME
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
    assert written[0]["delivery_deadline"] is None
    assert written[0]["is_remote"] is True
    assert written[0]["application_count"] == 9
    assert written[0]["contract_count"] == 0
    assert written[0]["recruitment_count"] == 1
    assert written[0]["favorite_count"] == 42
    assert written[0]["client"]["id"] == 6576565
    assert written[0]["client"]["name"] == "デジハナ採用担当"
    assert written[0]["client"]["rating"] == 5.0
    assert written[0]["client"]["identity_verified"] is False
    assert written[0]["client"]["rule_checked"] is False
    assert written[0]["client"]["jobs_posted_count"] == 32
    assert written[0]["client"]["project_finished_rate"] == 75
    assert (
        written[0]["client"]["profile_description"]
        == "弊社沖縄発のSES企業でございます。"
    )


def test_export_jobs_to_json_saves_job_list(tmp_path: Path) -> None:
    jobs = [
        Job(
            id=1,
            title="案件1",
            url="https://example.com/jobs/1",
        ),
        Job(
            id=2,
            title="案件2",
            url="https://example.com/jobs/2",
        ),
    ]

    output_path = tmp_path / "jobs.json"
    export_jobs_to_json(jobs, output_path)

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert isinstance(written, list)
    assert len(written) == 2
    assert written[0]["id"] == 1
    assert written[1]["id"] == 2


def test_export_jobs_to_json_writes_utf8_and_unescaped_japanese(tmp_path: Path) -> None:
    jobs = [
        Job(
            id=1,
            title="日本語タイトル",
            url="https://example.com/jobs/1",
            description="案件の説明文です。",
        )
    ]

    output_path = tmp_path / "jobs_ja.json"
    export_jobs_to_json(jobs, output_path)

    text = output_path.read_text(encoding="utf-8")

    assert "日本語タイトル" in text
    assert "案件の説明文です。" in text
    assert "\\u65e5\\u672c" not in text
    assert "\n  {" in text


def test_export_jobs_to_json_creates_parent_directories(tmp_path: Path) -> None:
    jobs = [
        Job(
            id=1,
            title="案件タイトル",
            url="https://example.com/jobs/1",
        )
    ]

    output_path = tmp_path / "nested" / "deep" / "jobs.json"
    export_jobs_to_json(jobs, output_path)

    assert output_path.exists()

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written[0]["id"] == 1


def test_build_raw_jobs_filename_uses_category_date_and_page() -> None:
    filename = build_raw_jobs_filename(
        "https://crowdworks.jp/public/jobs/group/development?page=2",
        date="20260702",
    )

    assert filename == "jobs_20260702_development_02.json"


def test_save_raw_jobs_writes_page_scoped_json(tmp_path: Path) -> None:
    jobs = [
        Job(
            id=1,
            title="案件タイトル",
            url="https://crowdworks.jp/public/jobs/1",
        )
    ]

    saved_path = save_raw_jobs(
        jobs,
        "https://crowdworks.jp/public/jobs/group/ai_bpo?page=2",
        output_dir=tmp_path / "output",
        date="20260702",
    )

    assert saved_path == tmp_path / "output" / "raw" / "jobs_20260702_ai_bpo_02.json"

    written = json.loads(saved_path.read_text(encoding="utf-8"))
    assert written[0]["id"] == 1
    assert written[0]["title"] == "案件タイトル"


def test_save_jobs_snapshot_creates_file_and_returns_path(tmp_path: Path) -> None:
    jobs = [
        Job(
            id=1,
            title="案件タイトル",
            url="https://example.com/jobs/1",
        )
    ]

    output_dir = tmp_path / "output"
    saved_path = save_jobs_snapshot(jobs, output_dir, "2026-07-05T13:14:15+09:00")

    assert saved_path == output_dir / "snapshots" / "jobs_20260705_131415.json"
    assert saved_path.exists()
    assert (output_dir / "snapshots").is_dir()

    written = json.loads(saved_path.read_text(encoding="utf-8"))
    assert written[0]["id"] == 1
    assert written[0]["title"] == "案件タイトル"
    assert written[0]["url"] == "https://example.com/jobs/1"


def test_export_jobs_for_ai_jsonl_writes_single_job_as_one_line(tmp_path: Path) -> None:
    jobs = [
        Job(
            id=1,
            title="案件A",
            url="https://example.com/jobs/1",
        )
    ]

    output_path = tmp_path / "nested" / "ai" / "jobs.jsonl"
    export_jobs_for_ai_jsonl(jobs, output_path)

    assert output_path.exists()
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    row = json.loads(lines[0])
    assert row["id"] == 1
    assert row["title"] == "案件A"
    assert row["metadata"] is None


def test_export_jobs_for_ai_jsonl_writes_multiple_lines_with_utf8_and_metadata(
    tmp_path: Path,
) -> None:
    jobs = [
        Job(
            id=1,
            title="日本語タイトル",
            url="https://example.com/jobs/1",
            metadata=JobMetadata(
                first_seen_at="2026-07-05T10:00:00+09:00",
                last_seen_at="2026-07-05T10:00:00+09:00",
                updated_at="2026-07-05T10:00:00+09:00",
                sources=[
                    JobSourceMetadata(
                        url="https://crowdworks.jp/public/jobs/group/ai_bpo",
                        first_seen_at="2026-07-05T10:00:00+09:00",
                        last_seen_at="2026-07-05T10:00:00+09:00",
                        seen_count=1,
                    )
                ],
            ),
        ),
        Job(
            id=2,
            title="案件B",
            url="https://example.com/jobs/2",
        ),
    ]

    output_path = tmp_path / "jobs_ai.jsonl"
    export_jobs_for_ai_jsonl(jobs, output_path)

    text = output_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) == 2
    assert "日本語タイトル" in text
    assert "\\u65e5\\u672c" not in text

    first = json.loads(lines[0])
    assert first["metadata"] is not None
    assert first["metadata"]["sources"][0]["seen_count"] == 1
