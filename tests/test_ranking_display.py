import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from ranking_display import format_ranked_job, format_ranked_jobs


def test_format_ranked_job_includes_rank_score_title_url_and_analysis() -> None:
    item = {
        "rank": 1,
        "job": {
            "id": 2,
            "title": "高評価案件",
            "url": "https://example.com/jobs/2",
        },
        "analysis": {
            "total_score": 90,
            "recommendation_reasons": ["AI活用できる"],
            "concerns": ["競争が激しい"],
            "application_strategy": ["実績を添える"],
            "overall_comment": "おすすめです。",
        },
    }

    text = format_ranked_job(item)

    assert "#1 90点" in text
    assert "高評価案件" in text
    assert "https://example.com/jobs/2" in text
    assert "おすすめ理由:" in text
    assert "注意点:" in text
    assert "応募戦略:" in text
    assert "総評:" in text


def test_format_ranked_jobs_returns_message_for_empty_input() -> None:
    assert format_ranked_jobs([]) == "ランキング結果がありません。"


def test_format_ranked_jobs_limits_output_to_given_count() -> None:
    items = [
        {
            "rank": 1,
            "job": {"title": "A", "url": "https://example.com/1"},
            "analysis": {
                "total_score": 90,
                "recommendation_reasons": ["A"],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "A",
            },
        },
        {
            "rank": 2,
            "job": {"title": "B", "url": "https://example.com/2"},
            "analysis": {
                "total_score": 80,
                "recommendation_reasons": ["B"],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "B",
            },
        },
        {
            "rank": 3,
            "job": {"title": "C", "url": "https://example.com/3"},
            "analysis": {
                "total_score": 70,
                "recommendation_reasons": ["C"],
                "concerns": [],
                "application_strategy": [],
                "overall_comment": "C",
            },
        },
    ]

    text = format_ranked_jobs(items, limit=2)

    assert "A" in text
    assert "B" in text
    assert "C" not in text
    assert text.count("========================================") == 2 * 2
