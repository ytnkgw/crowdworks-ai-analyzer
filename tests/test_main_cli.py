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


class _CollectedArgs(TypedDict):
    url: str | None
    limit: int | None


def test_build_parser_defines_expected_flags() -> None:
    parser = main.build_parser()
    args = parser.parse_args(
        ["--rank", "--display-ranking", "--export-report", "--limit", "3"]
    )

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

    analysis_results_path = output_dir / "analysis_results.json"
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
    assert (output_dir / "ranked_jobs.json").exists()

    ranked_items = json.loads(
        (output_dir / "ranked_jobs.json").read_text(encoding="utf-8")
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

    ranked_jobs_path = output_dir / "ranked_jobs.json"
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

    ranked_jobs_path = output_dir / "ranked_jobs.json"
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
    report_text = (output_dir / "ranked_jobs_report.md").read_text(encoding="utf-8")
    assert "# CrowdWorks Job Ranking Report" in report_text
    assert "案件A" in report_text
    assert "Displayed Jobs: 1" in report_text


def test_main_limit_affects_display_and_report_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    ranked_jobs_path = output_dir / "ranked_jobs.json"
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

    ranked_jobs_path = output_dir / "ranked_jobs.json"
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
    assert (output_dir / "ranked_jobs_report.md").exists()


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
    assert "--rank" in help_output.getvalue()
    assert "output/ranked_jobs.json" in help_output.getvalue()
    assert "default: 5" in help_output.getvalue()
    assert not (output_dir / "ranked_jobs.json").exists()
    assert not (output_dir / "ranked_jobs_report.md").exists()


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
    assert (output_dir / "jobs.json").exists()
    raw_files = list((output_dir / "raw").glob("jobs_*_development_02.json"))
    assert len(raw_files) == 1
    assert "Saved raw jobs:" in output.getvalue()
    assert "Saved pipeline jobs:" in output.getvalue()


def test_main_runs_rank_display_and_report_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output_dir))

    analysis_results_path = output_dir / "analysis_results.json"
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
    assert (output_dir / "ranked_jobs.json").exists()
    assert (output_dir / "ranked_jobs_report.md").exists()
