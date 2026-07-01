from fetcher import fetch_html
from models import Job
from parser import parse_job_detail, parse_jobs


def collect_jobs_from_url(url: str, limit: int | None = None) -> list[Job]:
    """指定URLから案件一覧と詳細情報を取得し、Job配列を返す。"""
    list_html = fetch_html(url)
    jobs = parse_jobs(list_html)

    if limit is not None:
        jobs = jobs[:limit]

    for job in jobs:
        detail_html = fetch_html(job.url)
        parse_job_detail(job, detail_html)

    return jobs
