import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from ranking import rank_job_analysis_results


def test_rank_job_analysis_results_sorts_by_total_score_and_assigns_ranks() -> None:
    items = [
        {
            "job": {"id": 1, "title": "低評価", "url": "https://example.com/1"},
            "analysis": {"total_score": 50},
        },
        {
            "job": {"id": 2, "title": "高評価", "url": "https://example.com/2"},
            "analysis": {"total_score": 90},
        },
        {
            "job": {"id": 3, "title": "中評価", "url": "https://example.com/3"},
            "analysis": {"total_score": 70},
        },
    ]

    ranked = rank_job_analysis_results(items)

    assert [item["job"]["id"] for item in ranked] == [2, 3, 1]
    assert [item["rank"] for item in ranked] == [1, 2, 3]
    assert ranked[0]["rank"] == 1
    assert ranked[0]["job"]["id"] == 2
    assert ranked[0]["analysis"]["total_score"] == 90


def test_rank_job_analysis_results_keeps_input_order_for_ties() -> None:
    items = [
        {
            "job": {"id": 1, "title": "first", "url": "https://example.com/1"},
            "analysis": {"total_score": 80},
        },
        {
            "job": {"id": 2, "title": "second", "url": "https://example.com/2"},
            "analysis": {"total_score": 80},
        },
        {
            "job": {"id": 3, "title": "third", "url": "https://example.com/3"},
            "analysis": {"total_score": 70},
        },
    ]

    ranked = rank_job_analysis_results(items)

    assert [item["job"]["id"] for item in ranked] == [1, 2, 3]
    assert [item["rank"] for item in ranked] == [1, 2, 3]


def test_rank_job_analysis_results_returns_empty_list_for_empty_input() -> None:
    ranked = rank_job_analysis_results([])

    assert ranked == []
