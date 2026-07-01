import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from models import AnalysisResult, Job


def _write_json_file(data: object, output_path: str | Path) -> None:
    """JSON データを UTF-8 形式で整形して保存します。"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    json_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(json_text, encoding="utf-8")


def build_job_analysis_item(job: Job, analysis: AnalysisResult) -> dict:
    """Job と AnalysisResult から job/analysis 形式の dict を作成します。"""
    return {
        "job": {
            "id": job.id,
            "title": job.title,
            "url": job.url,
        },
        "analysis": analysis.to_dict(),
    }


def export_jobs_to_json(jobs: Sequence[Job], file_path: str | Path) -> None:
    """Job オブジェクトの配列を UTF-8 形式の JSON ファイルとして保存します。"""
    _write_json_file([asdict(job) for job in jobs], file_path)


def export_job_analysis_results(items: list[dict], output_path: str | Path) -> None:
    """job/analysis のペアを UTF-8 形式の JSON ファイルとして保存します。"""
    _write_json_file(items, output_path)


def export_ranked_job_analysis_results(
    items: list[dict], output_path: str | Path
) -> None:
    """rank 情報を含む分析結果を UTF-8 形式の JSON ファイルとして保存します。"""
    export_job_analysis_results(items, output_path)
