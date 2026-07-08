import requests
import time
import config

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
        try:
            detail_html = fetch_html(job.url)
            parse_job_detail(job, detail_html)
        except requests.exceptions.HTTPError as e:
            # 一部案件は詳細ページが 403 になるため、収集全体を止めずに次へ進む
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 403:
                print(
                    "Skip job detail parse due to 403: "
                    f"id={job.id}, title={job.title}, url={job.url}"
                )
                continue
            raise
        finally:
            time.sleep(config.REQUEST_SLEEP_SECONDS)

    return jobs
