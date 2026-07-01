import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import job_collector
from models import Job


def test_collect_jobs_from_url_fetches_details_and_applies_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    htmls: dict[str, str] = {}

    def fake_fetch_html(url: str) -> str:
        return htmls[url]

    def fake_parse_jobs(html: str) -> list[Job]:
        assert html == "<html>list</html>"
        return [
            Job(id=1, title="案件1", url="https://example.com/jobs/1"),
            Job(id=2, title="案件2", url="https://example.com/jobs/2"),
            Job(id=3, title="案件3", url="https://example.com/jobs/3"),
        ]

    def fake_parse_job_detail(job: Job, html: str) -> Job:
        job.description = f"detail:{job.id}"
        job.reward = "固定報酬制"
        job.application_deadline = "2026年07月05日"
        job.published_at = "2026年06月21日"
        job.application_count = 9
        job.recruitment_count = 1
        return job

    monkeypatch.setattr(job_collector, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(job_collector, "parse_jobs", fake_parse_jobs)
    monkeypatch.setattr(job_collector, "parse_job_detail", fake_parse_job_detail)

    htmls["https://example.com/jobs"] = "<html>list</html>"
    htmls["https://example.com/jobs/1"] = "<html>detail1</html>"
    htmls["https://example.com/jobs/2"] = "<html>detail2</html>"
    htmls["https://example.com/jobs/3"] = "<html>detail3</html>"

    jobs = job_collector.collect_jobs_from_url("https://example.com/jobs", limit=2)

    assert len(jobs) == 2
    assert jobs[0].id == 1
    assert jobs[0].description == "detail:1"
    assert jobs[0].reward == "固定報酬制"
    assert jobs[0].application_deadline == "2026年07月05日"
    assert jobs[0].published_at == "2026年06月21日"
    assert jobs[0].application_count == 9
    assert jobs[0].recruitment_count == 1
