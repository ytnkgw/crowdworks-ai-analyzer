import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import config
from report_exporter import (
    export_ranked_jobs_report,
    format_ranked_job_as_markdown,
    format_ranked_jobs_report,
)


def test_format_ranked_job_as_markdown_includes_expected_sections() -> None:
    item = {
        "rank": 1,
        "job": {
            "title": "高評価案件",
            "url": "https://example.com/jobs/2",
        },
        "analysis": {
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
        },
    }

    text = format_ranked_job_as_markdown(item)

    assert "## #1 : 91点" in text
    assert "### 案件情報" in text
    assert "- Title: 高評価案件" in text
    assert "| 報酬 | 4 |" in text
    assert "### おすすめ理由" in text
    assert "- AI活用できる" in text


def test_format_ranked_jobs_report_returns_message_for_empty_input() -> None:
    assert format_ranked_jobs_report([]).startswith("# CrowdWorks Job Ranking Report")
    assert "ランキング結果がありません。" in format_ranked_jobs_report([])


def test_export_ranked_jobs_report_writes_markdown_file(tmp_path: Path) -> None:
    output_path = tmp_path / config.OUTPUT_RANKED_REPORT_FILENAME
    items = [
        {
            "rank": 1,
            "job": {"title": "A", "url": "https://example.com/1"},
            "analysis": {
                "reward_score": 4,
                "competition_score": 3,
                "ai_score": 5,
                "continuity_score": 4,
                "quality_score": 5,
                "total_score": 91,
                "recommendation_reasons": ["A"],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "A",
            },
        }
    ]

    export_ranked_jobs_report(items, str(output_path))

    written = output_path.read_text(encoding="utf-8")
    assert "# CrowdWorks Job Ranking Report" in written
    assert "## #1 : 91点" in written
