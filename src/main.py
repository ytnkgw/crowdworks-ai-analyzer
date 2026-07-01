import json
import config
from pathlib import Path
from exporter import (
    build_job_analysis_item,
    export_job_analysis_results,
    export_jobs_to_json,
)
from fetcher import fetch_html
from models import Job
from openai_client import analyze_job
from parser import parse_jobs
from parser import parse_job_detail


def main():
    current_dir = Path(__file__).resolve().parent
    output_dir = current_dir.parent / config.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # ### Pipline: 案件情報の取得
    # html = fetch_html(config.CW_JOB_LIST_URL)

    # ### Pipline: 案件情報の解析
    # jobs = parse_jobs(html)

    # ### Pipline: 案件詳細情報の解析
    # for job in jobs:
    #     detail_html = fetch_html(job.url)
    #     parse_job_detail(job, detail_html)

    # ### Pipline: 案件情報の JSON ファイルへの保存
    # current_dir = Path(__file__).resolve().parent
    # output_dir = current_dir.parent / config.OUTPUT_DIR
    # output_dir.mkdir(parents=True, exist_ok=True)
    # export_jobs_to_json(jobs, output_dir / "jobs.json")

    ### Pipline: 案件情報の JSON ファイルからの読み込み
    jobs = load_jobs_from_json(output_dir / "jobs.json")

    ### Pipline: 案件情報の分析
    export_results = []
    for job in jobs[:2]:
        result = analyze_job(job)
        export_results.append(build_job_analysis_item(job, result))
        print(result)

    ### Pipline: 案件情報の分析結果の JSON ファイルへの保存
    export_job_analysis_results(export_results, output_dir / "analysis_results.json")


def load_jobs_from_json(file_path: str | Path) -> list[Job]:
    """JSON ファイルから Job オブジェクトの配列を読み込みます。"""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        raw_jobs = json.load(f)

    return [
        Job(
            id=item["id"],
            title=item["title"],
            url=item["url"],
            description=item.get("description"),
            reward=item.get("reward"),
            application_deadline=item.get("application_deadline"),
            published_at=item.get("published_at"),
            application_count=item.get("application_count"),
            recruitment_count=item.get("recruitment_count"),
        )
        for item in raw_jobs
    ]


def load_debug_html(filename: str) -> str:
    """debug フォルダから HTML ファイルを読み込みます。"""
    current_dir = Path(__file__).resolve().parent
    debug_path = current_dir.parent / config.DEBUG_DIR / filename
    with open(debug_path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    main()
