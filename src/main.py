import argparse
import json
import config
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from exporter import (
    save_raw_jobs,
    save_jobs_snapshot,
    export_jobs_for_ai_jsonl,
    export_update_summary,
    build_job_analysis_item,
    export_job_analysis_results,
    export_jobs_to_json,
    export_ranked_job_analysis_results,
)
from job_filter import filter_expired_jobs
from fetcher import fetch_html
from models import Job
from openai_client import analyze_job
from parser import parse_jobs
from parser import parse_job_detail
from ranking import rank_job_analysis_results
from ranking_display import format_ranked_jobs
from report_exporter import export_ranked_jobs_report
from job_collector import collect_jobs_from_url
from importer import load_jobs_from_json
from job_store import remove_expired_jobs, update_job_store

_JST = ZoneInfo("Asia/Tokyo")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 src/main.py",
        description="CrowdWorks AI Analyzer",
    )

    parser.add_argument(
        "--collect-jobs",
        action="store_true",
        help=(
            "指定したCrowdWorks URLから案件一覧と詳細情報を取得して "
            f"{config.OUTPUT_JOBS_FILENAME} を生成する"
        ),
    )

    parser.add_argument(
        "--url",
        type=str,
        help="案件一覧を取得するCrowdWorks URL",
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help=(
            f"output/{config.OUTPUT_JOBS_FILENAME} を読み込んで AI 分析し "
            f"output/{config.OUTPUT_ANALYSIS_RESULTS_FILENAME} を生成する"
        ),
    )

    parser.add_argument(
        "--rank",
        action="store_true",
        help=(
            "分析結果をランキングして "
            f"output/{config.OUTPUT_RANKED_JOBS_FILENAME} を生成する"
        ),
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


def _fill_application_deadline_from_jobs_json(
    output_dir: Path,
    analysis_items: list[dict],
) -> list[dict]:
    jobs_path = output_dir / config.OUTPUT_JOBS_FILENAME
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


def _run_collect_pipeline(args: argparse.Namespace, output_dir: Path) -> None:
    now = datetime.now(_JST).isoformat()
    jobs_path = output_dir / config.OUTPUT_JOBS_FILENAME

    existing_jobs = load_jobs_from_json(jobs_path) if jobs_path.exists() else []
    collected_jobs = collect_jobs_from_url(args.url, limit=args.limit)
    updated_jobs = update_job_store(existing_jobs, collected_jobs, args.url, now)

    raw_output_path = save_raw_jobs(collected_jobs, args.url, output_dir=output_dir)
    export_jobs_to_json(updated_jobs, jobs_path)
    snapshot_path = save_jobs_snapshot(updated_jobs, output_dir, now)
    jobs_for_ai_path = output_dir / config.OUTPUT_JOBS_FOR_AI_FILENAME
    export_jobs_for_ai_jsonl(updated_jobs, jobs_for_ai_path)
    update_summary = {
        "updated_at": now,
        "source_url": args.url,
        "existing_count": len(existing_jobs),
        "collected_count": len(collected_jobs),
        "saved_count": len(updated_jobs),
        "output_files": {
            "jobs_json": str(jobs_path),
            "snapshot": str(snapshot_path),
            "jobs_for_ai": str(jobs_for_ai_path),
        },
    }
    update_summary_path = output_dir / config.OUTPUT_UPDATE_SUMMARY_FILENAME
    export_update_summary(update_summary, update_summary_path)

    print(f"Saved raw jobs: {raw_output_path}")
    print(f"Saved pipeline jobs: {jobs_path}")
    print(f"Saved snapshot: {snapshot_path}")
    print(f"Saved jobs for AI: {jobs_for_ai_path}")
    print(f"Saved update summary: {update_summary_path}")
    print(f"Collected {len(collected_jobs)} jobs.")
    print(f"Saved {len(updated_jobs)} jobs after update.")


def _run_analyze_pipeline(args: argparse.Namespace, output_dir: Path) -> bool:
    jobs_path = output_dir / config.OUTPUT_JOBS_FILENAME
    try:
        jobs = load_jobs_from_json(jobs_path)
    except FileNotFoundError:
        print(f"jobs.json not found: {jobs_path}")
        print("Run with --collect-jobs first.")
        return False

    filtered_jobs = remove_expired_jobs(jobs)
    skipped_count = len(jobs) - len(filtered_jobs)
    target_jobs = filtered_jobs[: args.limit]

    export_results = []
    for job in target_jobs:
        result = analyze_job(job)
        export_results.append(build_job_analysis_item(job, result))

    analysis_results_path = output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME
    export_job_analysis_results(export_results, analysis_results_path)

    if skipped_count > 0:
        print(f"Skipped expired jobs: {skipped_count}")
    print(f"Saved analysis results: {analysis_results_path}")
    print(f"Analyzed {len(export_results)} jobs.")
    return True


def _run_rank_pipeline(output_dir: Path) -> list[dict]:
    analysis_results_path = output_dir / config.OUTPUT_ANALYSIS_RESULTS_FILENAME
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
        ranked_job_items, output_dir / config.OUTPUT_RANKED_JOBS_FILENAME
    )
    return ranked_job_items


def _run_display_ranking_pipeline(ranked_job_items: list[dict], limit: int) -> None:
    ranked_text = format_ranked_jobs(ranked_job_items, limit)
    print(ranked_text)


def _run_export_report_pipeline(
    ranked_job_items: list[dict], output_dir: Path, limit: int
) -> None:
    export_ranked_jobs_report(
        ranked_job_items,
        str(output_dir / config.OUTPUT_RANKED_REPORT_FILENAME),
        limit=limit,
    )


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

    ### 収集
    if args.collect_jobs:
        _run_collect_pipeline(args, output_dir)

    ### 分析
    if args.analyze:
        if not _run_analyze_pipeline(args, output_dir):
            return 0

    ### ランキング
    ranked_job_items: list[dict] = []
    if args.rank:
        ranked_job_items = _run_rank_pipeline(output_dir)

    ### ランキング読込
    ranked_jobs_path = output_dir / config.OUTPUT_RANKED_JOBS_FILENAME
    if not ranked_job_items and ranked_jobs_path.exists():
        ranked_job_items = load_json(ranked_jobs_path)

    if ranked_job_items:
        ranked_job_items, skipped_count = filter_expired_jobs(ranked_job_items)
        if skipped_count > 0:
            print(f"Skipped expired jobs: {skipped_count}")
            export_ranked_job_analysis_results(ranked_job_items, ranked_jobs_path)

    ### 表示
    if args.display_ranking:
        _run_display_ranking_pipeline(ranked_job_items, args.limit)

    ### レポート出力
    if args.export_report:
        _run_export_report_pipeline(ranked_job_items, output_dir, args.limit)

    return 0


def load_debug_html(filename: str) -> str:
    """debug フォルダから HTML ファイルを読み込みます。"""
    current_dir = Path(__file__).resolve().parent
    debug_path = current_dir.parent / config.DEBUG_DIR / filename
    with open(debug_path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    raise SystemExit(main())
