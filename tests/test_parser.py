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
