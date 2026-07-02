import argparse
import json
import config
from pathlib import Path
from exporter import (
    save_raw_jobs,
    build_job_analysis_item,
    export_job_analysis_results,
    export_jobs_to_json,
    export_ranked_job_analysis_results,
)
from deadline_filter import should_exclude_by_deadline, filter_expired_jobs
from fetcher import fetch_html
from models import Client, Job
from openai_client import analyze_job
from parser import parse_jobs
from parser import parse_job_detail
from ranking import rank_job_analysis_results
from ranking_display import format_ranked_jobs
from report_exporter import export_ranked_jobs_report
from job_collector import collect_jobs_from_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 src/main.py",
        description="CrowdWorks AI Analyzer",
    )

    parser.add_argument(
        "--collect-jobs",
        action="store_true",
        help="指定したCrowdWorks URLから案件一覧と詳細情報を取得して jobs.json を生成する",
    )

    parser.add_argument(
        "--url",
        type=str,
        help="案件一覧を取得するCrowdWorks URL",
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help="output/jobs.json を読み込んで AI 分析し output/analysis_results.json を生成する",
    )

    parser.add_argument(
        "--rank",
        action="store_true",
        help="分析結果をランキングして output/ranked_jobs.json を生成する",
    )

    parser.add_argument(
        "--display-ranking",
        action="store_true",
        help="ランキング結果をターミナルに表示する",
    )

    parser.add_argument(
        "--export-report",
        action="store_true",
        help="ランキング結果をMarkdownレポートとして出力する",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10000,
        help="表示・出力する上位件数を指定する（default: 10000）",
    )

    return parser


def load_json(path: str | Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _filter_jobs_by_deadline(jobs: list[Job]) -> tuple[list[Job], int]:
    filtered: list[Job] = []
    skipped = 0

    for job in jobs:
        if should_exclude_by_deadline(job.application_deadline):
            skipped += 1
            continue
        filtered.append(job)

    return filtered, skipped


def _fill_application_deadline_from_jobs_json(
    output_dir: Path,
    analysis_items: list[dict],
) -> list[dict]:
    jobs_path = output_dir / "jobs.json"
    if not jobs_path.exists():
        return analysis_items

    try:
        jobs_payload = load_json(jobs_path)
    except (json.JSONDecodeError, OSError):
        return analysis_items

    deadline_by_id: dict[int, str | None] = {}
    for job in jobs_payload:
        if not isinstance(job, dict):
            continue

        job_id = job.get("id")
        if isinstance(job_id, int):
            deadline_by_id[job_id] = job.get("application_deadline")

    hydrated: list[dict] = []
    for item in analysis_items:
        if not isinstance(item, dict):
            hydrated.append(item)
            continue

        job = item.get("job")
        if not isinstance(job, dict):
            hydrated.append(item)
            continue

        if job.get("application_deadline"):
            hydrated.append(item)
            continue

        job_id = job.get("id")
        if not isinstance(job_id, int) or job_id not in deadline_by_id:
            hydrated.append(item)
            continue

        new_job = dict(job)
        new_job["application_deadline"] = deadline_by_id[job_id]

        new_item = dict(item)
        new_item["job"] = new_job
        hydrated.append(new_item)

    return hydrated


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.collect_jobs and not args.url:
        parser.error("--collect-jobs を使用する場合は --url を指定してください。")

    if not any(
        [
            args.collect_jobs,
            args.analyze,
            args.rank,
            args.display_ranking,
            args.export_report,
        ]
    ):
        parser.print_help()
        return 0

    current_dir = Path(__file__).resolve().parent
    output_dir = current_dir.parent / config.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    ### Pipline: 案件情報の収集と JSON ファイルへの保存
    if args.collect_jobs:
        jobs = collect_jobs_from_url(args.url, limit=args.limit)
        filtered_jobs, skipped_count = _filter_jobs_by_deadline(jobs)

        raw_output_path = save_raw_jobs(filtered_jobs, args.url, output_dir=output_dir)
        export_jobs_to_json(filtered_jobs, output_dir / "jobs.json")
        print(f"Saved raw jobs: {raw_output_path}")
        print(f"Saved pipeline jobs: {output_dir / 'jobs.json'}")
        if skipped_count > 0:
            print(f"Skipped expired jobs: {skipped_count}")
        print(f"Collected {len(filtered_jobs)} jobs.")

    ### Pipline: 案件情報の JSON ファイルからの読み込、分析、保存
    if args.analyze:
        jobs = load_jobs_from_json(output_dir / "jobs.json")
        filtered_jobs, skipped_count = _filter_jobs_by_deadline(jobs)
        target_jobs = filtered_jobs[: args.limit]

        export_results = []
        for job in target_jobs:
            result = analyze_job(job)
            export_results.append(build_job_analysis_item(job, result))

        analysis_results_path = output_dir / "analysis_results.json"
        export_job_analysis_results(export_results, analysis_results_path)

        if skipped_count > 0:
            print(f"Skipped expired jobs: {skipped_count}")
        print(f"Saved analysis results: {analysis_results_path}")
        print(f"Analyzed {len(export_results)} jobs.")

    ### Pipline: 案件情報の分析結果の JSON ファイルからの読み込み
    ### Pipline: 案件情報の分析結果のランキング付け
    ### Pipline: 案件情報の分析結果のランキング付けの JSON ファイルへの保存
    ranked_job_items: list[dict] = []
    if args.rank:
        analysis_results_path = output_dir / "analysis_results.json"
        analysis_results = load_json(analysis_results_path)
        analysis_results = _fill_application_deadline_from_jobs_json(
            output_dir, analysis_results
        )
        analysis_results, skipped_count = filter_expired_jobs(analysis_results)
        if skipped_count > 0:
            print(f"Skipped expired jobs: {skipped_count}")
        export_job_analysis_results(analysis_results, analysis_results_path)
        ranked_job_items = rank_job_analysis_results(analysis_results)
        export_ranked_job_analysis_results(
            ranked_job_items, output_dir / "ranked_jobs.json"
        )
    ### Pipline: 案件情報の分析結果のランキング付けの JSON ファイルからの読み込み
    if not ranked_job_items and (output_dir / "ranked_jobs.json").exists():
        ranked_job_items = load_json(output_dir / "ranked_jobs.json")

    if ranked_job_items:
        ranked_job_items, skipped_count = filter_expired_jobs(ranked_job_items)
        if skipped_count > 0:
            print(f"Skipped expired jobs: {skipped_count}")
            export_ranked_job_analysis_results(
                ranked_job_items, output_dir / "ranked_jobs.json"
            )

    ### Pipline: ランキング結果の表示用整形
    if args.display_ranking:
        ranked_text = format_ranked_jobs(ranked_job_items, args.limit)
        print(ranked_text)

    ### Pipline: ランキング結果の Markdown レポート出力
    if args.export_report:
        export_ranked_jobs_report(
            ranked_job_items,
            str(output_dir / "ranked_jobs_report.md"),
            limit=args.limit,
        )

    return 0


def load_jobs_from_json(file_path: str | Path) -> list[Job]:
    """JSON ファイルから Job オブジェクトの配列を読み込みます。"""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        raw_jobs = json.load(f)

    jobs: list[Job] = []
    for item in raw_jobs:
        client_data = item.get("client")
        client = None
        if isinstance(client_data, dict):
            client = Client(
                id=client_data.get("id"),
                name=client_data.get("name"),
                rating=client_data.get("rating"),
                identity_verified=client_data.get("identity_verified"),
                rule_checked=client_data.get("rule_checked"),
                jobs_posted_count=client_data.get("jobs_posted_count"),
                project_finished_rate=client_data.get("project_finished_rate"),
                profile_description=client_data.get("profile_description"),
            )

        jobs.append(
            Job(
                id=item["id"],
                title=item["title"],
                url=item["url"],
                category=item.get("category"),
                sub_category=item.get("sub_category"),
                description=item.get("description"),
                reward=item.get("reward"),
                application_deadline=item.get("application_deadline"),
                published_at=item.get("published_at"),
                delivery_deadline=item.get("delivery_deadline"),
                is_remote=item.get("is_remote"),
                application_count=item.get("application_count"),
                contract_count=item.get("contract_count"),
                recruitment_count=item.get("recruitment_count"),
                favorite_count=item.get("favorite_count"),
                client=client,
            )
        )

    return jobs


def load_debug_html(filename: str) -> str:
    """debug フォルダから HTML ファイルを読み込みます。"""
    current_dir = Path(__file__).resolve().parent
    debug_path = current_dir.parent / config.DEBUG_DIR / filename
    with open(debug_path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    raise SystemExit(main())
