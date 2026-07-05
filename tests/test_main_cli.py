import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import TypedDict

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import config
import main
import job_collector
import job_filter
import job_store
from models import AnalysisResult


class _CollectedArgs(TypedDict):
    url: str | None
    limit: int | None


def test_build_parser_defines_expected_flags() -> None:
    parser = main.build_parser()
    args = parser.parse_args(
        [
            "--analyze",
            "--rank",
            "--display-ranking",
            "--export-report",
            "--limit",
            "3",
        ]
    )

    assert args.analyze is True
    assert args.rank is True
    assert args.display_ranking is True
    assert args.export_report is True
    assert args.limit == 3


def test_main_rank_only_generates_ranked_jobs_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    analysis_results_path = output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME
    analysis_results_path.write_text(
        json.dumps(
            [
                {
                    "job": {"title": "低スコア案件"},
                    "analysis": {
                        "reward_score": 2,
                        "competition_score": 3,
                        "ai_score": 4,
                        "continuity_score": 2,
                        "quality_score": 3,
                        "total_score": 80,
                    },
                },
                {
                    "job": {"title": "高スコア案件"},
                    "analysis": {
                        "reward_score": 4,
                        "competition_score": 3,
                        "ai_score": 5,
                        "continuity_score": 4,
                        "quality_score": 5,
                        "total_score": 95,
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main.main(["--rank"])

    assert exit_code == 0
    assert (output_dir / config.OUTPUT_RANKED_JOBS_FILENAME).exists()

    ranked_items = json.loads(
        (output_dir / config.OUTPUT_RANKED_JOBS_FILENAME).read_text(encoding="utf-8")
    )
    assert len(ranked_items) == 2
    assert ranked_items[0]["rank"] == 1
    assert ranked_items[0]["job"]["title"] == "高スコア案件"
    assert ranked_items[1]["rank"] == 2
    assert ranked_items[1]["job"]["title"] == "低スコア案件"


def test_main_display_ranking_outputs_limited_ranked_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    ranked_jobs_path = output_dir / config.OUTPUT_RANKED_JOBS_FILENAME
    ranked_jobs_path.write_text(
        json.dumps(
            [
                {
                    "rank": 1,
                    "job": {"title": "案件A", "url": "https://example.com/a"},
                    "analysis": {
                        "total_score": 95,
                        "recommendation_reasons": ["理由A"],
                        "concerns": ["注意A"],
                        "application_strategy": ["戦略A"],
                        "overall_comment": "総評A",
                    },
                },
                {
                    "rank": 2,
                    "job": {"title": "案件B", "url": "https://example.com/b"},
                    "analysis": {
                        "total_score": 90,
                        "recommendation_reasons": ["理由B"],
                        "concerns": ["注意B"],
                        "application_strategy": ["戦略B"],
                        "overall_comment": "総評B",
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(["--display-ranking", "--limit", "1"])

    assert exit_code == 0
    assert "案件A" in output.getvalue()
    assert "案件B" not in output.getvalue()


def test_main_export_report_writes_markdown_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    ranked_jobs_path = output_dir / config.OUTPUT_RANKED_JOBS_FILENAME
    ranked_jobs_path.write_text(
        json.dumps(
            [
                {
                    "rank": 1,
                    "job": {"title": "案件A"},
                    "analysis": {
                        "total_score": 95,
                        "reward_score": 4,
                        "competition_score": 3,
                        "ai_score": 5,
                        "continuity_score": 4,
                        "quality_score": 5,
                        "recommendation_reasons": ["理由A"],
                        "concerns": ["注意A"],
                        "application_strategy": ["戦略A"],
                        "overall_comment": "総評A",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main.main(["--export-report", "--limit", "1"])

    assert exit_code == 0
    report_text = (output_dir / config.OUTPUT_RANKED_REPORT_FILENAME).read_text(
        encoding="utf-8"
    )
    assert "# CrowdWorks Job Ranking Report" in report_text
    assert "案件A" in report_text
    assert "Displayed Jobs: 1" in report_text


def test_main_limit_affects_display_and_report_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    ranked_jobs_path = output_dir / config.OUTPUT_RANKED_JOBS_FILENAME
    ranked_jobs_path.write_text(
        json.dumps(
            [
                {
                    "rank": 1,
                    "job": {"title": "案件A"},
                    "analysis": {"total_score": 95},
                },
                {
                    "rank": 2,
                    "job": {"title": "案件B"},
                    "analysis": {"total_score": 90},
                },
            ]
        ),
        encoding="utf-8",
    )

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(["--display-ranking", "--limit", "1"])

    assert exit_code == 0
    assert "案件A" in output.getvalue()
    assert "案件B" not in output.getvalue()


def test_main_multiple_options_run_in_expected_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    ranked_jobs_path = output_dir / config.OUTPUT_RANKED_JOBS_FILENAME
    ranked_jobs_path.write_text(
        json.dumps(
            [
                {
                    "rank": 1,
                    "job": {"title": "案件A"},
                    "analysis": {"total_score": 95},
                }
            ]
        ),
        encoding="utf-8",
    )

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(["--display-ranking", "--export-report", "--limit", "1"])

    assert exit_code == 0
    assert "案件A" in output.getvalue()
    assert (output_dir / config.OUTPUT_RANKED_REPORT_FILENAME).exists()


def test_main_shows_help_and_skips_work_when_no_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    help_output = io.StringIO()
    with redirect_stdout(help_output):
        exit_code = main.main([])

    assert exit_code == 0
    assert "python3 src/main.py" in help_output.getvalue()
    assert "--analyze" in help_output.getvalue()
    assert "--rank" in help_output.getvalue()
    assert f"output/{config.OUTPUT_RANKED_JOBS_FILENAME}" in help_output.getvalue()
    assert "default: 10000" in help_output.getvalue()
    assert not (output_dir / config.OUTPUT_RANKED_JOBS_FILENAME).exists()
    assert not (output_dir / config.OUTPUT_RANKED_REPORT_FILENAME).exists()


def test_main_analyze_writes_analysis_results_with_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    jobs_path = output_dir / config.OUTPUT_JOBS_FILENAME
    jobs_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "title": "案件A",
                    "url": "https://example.com/jobs/1",
                },
                {
                    "id": 2,
                    "title": "案件B",
                    "url": "https://example.com/jobs/2",
                },
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(main, "remove_expired_jobs", lambda jobs: jobs)

    calls: list[int] = []

    def fake_analyze_job(job: job_collector.Job) -> AnalysisResult:
        calls.append(job.id)
        return AnalysisResult.from_dict(
            {
                "reward_score": 3,
                "competition_score": 3,
                "ai_score": 3,
                "continuity_score": 3,
                "quality_score": 3,
                "total_score": 75,
                "recommendation_reasons": [],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "ok",
            }
        )

    monkeypatch.setattr(main, "analyze_job", fake_analyze_job)

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(["--analyze", "--limit", "1"])

    assert exit_code == 0
    assert calls == [1]
    assert (output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME).exists()

    payload = json.loads(
        (output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME).read_text("utf-8")
    )
    assert len(payload) == 1
    assert payload[0]["job"]["id"] == 1
    assert "Saved analysis results:" in output.getvalue()
    assert "Analyzed 1 jobs." in output.getvalue()


def test_main_analyze_excludes_expired_deadline_jobs_and_prints_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    jobs_path = output_dir / config.OUTPUT_JOBS_FILENAME
    jobs_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "title": "期限切れ案件",
                    "url": "https://example.com/jobs/1",
                    "application_deadline": "2026年07月01日",
                },
                {
                    "id": 2,
                    "title": "募集中案件",
                    "url": "https://example.com/jobs/2",
                    "application_deadline": "2026年07月02日",
                },
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        main,
        "remove_expired_jobs",
        lambda jobs: [
            job for job in jobs if job.application_deadline != "2026年07月01日"
        ],
    )

    calls: list[int] = []

    def fake_analyze_job(job: job_collector.Job) -> AnalysisResult:
        calls.append(job.id)
        return AnalysisResult.from_dict(
            {
                "reward_score": 3,
                "competition_score": 3,
                "ai_score": 3,
                "continuity_score": 3,
                "quality_score": 3,
                "total_score": 75,
                "recommendation_reasons": [],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "ok",
            }
        )

    monkeypatch.setattr(main, "analyze_job", fake_analyze_job)

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(["--analyze"])

    assert exit_code == 0
    assert calls == [2]
    assert "Skipped expired jobs: 1" in output.getvalue()
    assert "Analyzed 1 jobs." in output.getvalue()


def test_build_parser_supports_collect_jobs_and_url() -> None:
    parser = main.build_parser()
    args = parser.parse_args(["--collect-jobs", "--url", "https://example.com/jobs"])

    assert args.collect_jobs is True
    assert args.url == "https://example.com/jobs"


def test_main_collect_jobs_requires_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    with pytest.raises(SystemExit) as exc_info:
        main.main(["--collect-jobs"])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "--collect-jobs を使用する場合は --url を指定してください。" in captured.err


def test_main_collect_jobs_passes_limit_to_collector(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    captured: _CollectedArgs = {"url": None, "limit": None}

    def fake_collect_jobs_from_url(
        url: str, limit: int | None = None
    ) -> list[job_collector.Job]:
        captured["url"] = url
        captured["limit"] = limit
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
                "https://example.com/public/jobs/group/development?page=2",
                "--limit",
                "2",
            ]
        )

    assert exit_code == 0
    assert captured["url"] == "https://example.com/public/jobs/group/development?page=2"
    assert captured["limit"] == 2
    assert (output_dir / config.OUTPUT_JOBS_FILENAME).exists()
    raw_files = list((output_dir / "raw").glob("jobs_*_development_02.json"))
    assert len(raw_files) == 1
    assert "Saved raw jobs:" in output.getvalue()
    assert "Saved pipeline jobs:" in output.getvalue()
    assert "Saved snapshot:" in output.getvalue()
    assert "Saved jobs for AI:" in output.getvalue()
    assert "Saved update summary:" in output.getvalue()


def test_main_collect_jobs_excludes_expired_deadline_jobs(
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
                title="期限切れ案件",
                url="https://example.com/jobs/1",
                application_deadline="2026年07月01日",
            ),
            job_collector.Job(
                id=2,
                title="募集中案件",
                url="https://example.com/jobs/2",
                application_deadline="2026年07月02日",
            ),
        ]

    monkeypatch.setattr(main, "collect_jobs_from_url", fake_collect_jobs_from_url)
    monkeypatch.setattr(
        job_store,
        "should_exclude_by_deadline",
        lambda deadline, today=None: deadline == "2026年07月01日",
    )

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(
            [
                "--collect-jobs",
                "--url",
                "https://example.com/public/jobs/group/development",
            ]
        )

    assert exit_code == 0
    jobs_payload = json.loads(
        (output_dir / config.OUTPUT_JOBS_FILENAME).read_text(encoding="utf-8")
    )
    assert len(jobs_payload) == 1
    assert jobs_payload[0]["title"] == "募集中案件"
    assert "Saved snapshot:" in output.getvalue()
    assert "Saved jobs for AI:" in output.getvalue()
    assert "Saved update summary:" in output.getvalue()
    assert "Collected 2 jobs." in output.getvalue()
    assert "Saved 1 jobs after update." in output.getvalue()


def test_main_rank_excludes_expired_deadline_jobs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    analysis_results_path = output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME
    analysis_results_path.write_text(
        json.dumps(
            [
                {
                    "job": {
                        "id": 1,
                        "title": "期限切れ案件",
                        "application_deadline": "2026年07月01日",
                    },
                    "analysis": {"total_score": 90},
                },
                {
                    "job": {
                        "id": 2,
                        "title": "募集中案件",
                        "application_deadline": "2026年07月02日",
                    },
                    "analysis": {"total_score": 80},
                },
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        job_filter,
        "should_exclude_by_deadline",
        lambda deadline, today=None: deadline == "2026年07月01日",
    )

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(["--rank"])

    assert exit_code == 0
    ranked_items = json.loads(
        (output_dir / config.OUTPUT_RANKED_JOBS_FILENAME).read_text(encoding="utf-8")
    )
    assert len(ranked_items) == 1
    assert ranked_items[0]["job"]["title"] == "募集中案件"
    assert "Skipped expired jobs: 1" in output.getvalue()


def test_main_runs_rank_display_and_report_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    analysis_results_path = output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME
    analysis_results_path.write_text(
        json.dumps(
            [
                {
                    "reward_score": 4,
                    "competition_score": 3,
                    "ai_score": 5,
                    "continuity_score": 4,
                    "quality_score": 5,
                    "total_score": 91,
                    "recommendation_reasons": ["AI活用できる"],
                    "concerns": ["競争が激しい"],
                    "application_strategy": ["実績を添える"],
                    "overall_comment": "おすすめです。",
                }
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main.main(
        ["--rank", "--display-ranking", "--export-report", "--limit", "1"]
    )

    assert exit_code == 0
    assert (output_dir / config.OUTPUT_RANKED_JOBS_FILENAME).exists()
    assert (output_dir / config.OUTPUT_RANKED_REPORT_FILENAME).exists()


def test_main_analyze_and_rank_generate_both_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    jobs_path = output_dir / config.OUTPUT_JOBS_FILENAME
    jobs_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "title": "案件A",
                    "url": "https://example.com/jobs/1",
                },
                {
                    "id": 2,
                    "title": "案件B",
                    "url": "https://example.com/jobs/2",
                },
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(main, "remove_expired_jobs", lambda jobs: jobs)

    def fake_analyze_job(job: job_collector.Job) -> AnalysisResult:
        score = 90 if job.id == 1 else 80
        return AnalysisResult.from_dict(
            {
                "reward_score": 3,
                "competition_score": 3,
                "ai_score": 3,
                "continuity_score": 3,
                "quality_score": 3,
                "total_score": score,
                "recommendation_reasons": [],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "ok",
            }
        )

    monkeypatch.setattr(main, "analyze_job", fake_analyze_job)

    exit_code = main.main(["--analyze", "--rank"])

    assert exit_code == 0
    assert (output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME).exists()
    assert (output_dir / config.OUTPUT_RANKED_JOBS_FILENAME).exists()

    analysis_payload = json.loads(
        (output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME).read_text(
            encoding="utf-8"
        )
    )
    ranked_payload = json.loads(
        (output_dir / config.OUTPUT_RANKED_JOBS_FILENAME).read_text(encoding="utf-8")
    )

    assert len(analysis_payload) == 2
    assert len(ranked_payload) == 2
    assert ranked_payload[0]["job"]["id"] == 1
    assert ranked_payload[0]["rank"] == 1


def test_main_analyze_without_jobs_json_prints_message_and_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(["--analyze"])

    assert exit_code == 0
    assert "Saved analysis results:" in output.getvalue()
    assert "Analyzed 0 jobs." in output.getvalue()


def test_main_collect_jobs_and_analyze_runs_both_pipelines(
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
    monkeypatch.setattr(main, "remove_expired_jobs", lambda jobs: jobs)

    calls: list[int] = []

    def fake_analyze_job(job: job_collector.Job) -> AnalysisResult:
        calls.append(job.id)
        return AnalysisResult.from_dict(
            {
                "reward_score": 3,
                "competition_score": 3,
                "ai_score": 3,
                "continuity_score": 3,
                "quality_score": 3,
                "total_score": 75,
                "recommendation_reasons": [],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "ok",
            }
        )

    monkeypatch.setattr(main, "analyze_job", fake_analyze_job)

    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main.main(
            [
                "--collect-jobs",
                "--analyze",
                "--url",
                "https://example.com/public/jobs/group/ai_bpo",
                "--limit",
                "5",
            ]
        )

    assert exit_code == 0
    assert calls == [1]
    assert (output_dir / config.OUTPUT_JOBS_FILENAME).exists()
    assert (output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME).exists()
    assert "Saved snapshot:" in output.getvalue()
    assert "Saved jobs for AI:" in output.getvalue()
    assert "Saved update summary:" in output.getvalue()
    assert "Collected 1 jobs." in output.getvalue()
    assert "Analyzed 1 jobs." in output.getvalue()
