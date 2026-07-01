import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from models import AnalysisResult, Job


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
    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    json_text = (
        json.dumps([asdict(job) for job in jobs], ensure_ascii=False, indent=2) + "\n"
    )
    output_path.write_text(json_text, encoding="utf-8")


def export_job_analysis_results(items: list[dict], output_path: str | Path) -> None:
    """job/analysis のペアを UTF-8 形式の JSON ファイルとして保存します。"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    json_text = json.dumps(items, ensure_ascii=False, indent=2) + "\n"
    path.write_text(json_text, encoding="utf-8")
