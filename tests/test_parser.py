from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from models import Job
from parser import parse_job_detail


def test_parse_job_detail_extracts_category_and_sub_category_from_breadcrumb() -> None:
    debug_html_path = (
        Path(__file__).resolve().parents[1] / "debug" / "cw_job_detail.html"
    )
    html = debug_html_path.read_text(encoding="utf-8")

    job = Job(
        id=13247976,
        title="dummy",
        url="https://crowdworks.jp/public/jobs/13247976",
    )

    parsed = parse_job_detail(job, html)

    assert parsed.category == "AI-BPO（AI活用の業務改善）"
    assert parsed.sub_category == "AIバックオフィス支援"
    assert parsed.application_count == 27
    assert parsed.contract_count == 0
    assert parsed.recruitment_count == 3
    assert parsed.favorite_count == 42
    assert parsed.client is not None
    assert parsed.client.id == 6576565
    assert parsed.client.name == "デジハナ採用担当"
    assert parsed.client.rating == 5.0
    assert parsed.client.identity_verified is False
    assert parsed.client.rule_checked is False
    assert parsed.client.jobs_posted_count == 32
    assert parsed.client.project_finished_rate == 75
