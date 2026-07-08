import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Sequence
from urllib.parse import parse_qs, urlparse
import re

import config

from models import AnalysisResult, Job

MAX_CLIENT_PROFILE_DESCRIPTION_LENGTH = 200


def _write_json_file(data: object, output_path: str | Path) -> None:
    """JSON データを UTF-8 形式で整形して保存します。"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    json_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(json_text, encoding="utf-8")


def _jobs_to_dicts(jobs: Sequence[Job]) -> list[dict]:
    return [asdict(job) for job in jobs]


def build_raw_jobs_filename(url: str, date: str | None = None) -> str:
    """取得URLから raw 保存用ファイル名を生成します。"""
    parsed = urlparse(url)
    date_part = date or datetime.now().strftime("%Y%m%d")

    path_parts = [part for part in parsed.path.split("/") if part]
    category = "unknown"
    if len(path_parts) >= 4 and path_parts[:3] == ["public", "jobs", "group"]:
        category = path_parts[3]

    safe_category = re.sub(r"[^A-Za-z0-9_-]+", "_", category).strip("_") or "unknown"

    page_values = parse_qs(parsed.query).get("page", ["1"])
    try:
        page = int(page_values[0])
    except (TypeError, ValueError):
        page = 1

    return f"jobs_{date_part}_{safe_category}_{page:02d}.json"


def save_raw_jobs(
    jobs: Sequence[Job],
    source_url: str,
    output_dir: str | Path | None = None,
    date: str | None = None,
) -> Path:
    """ページ単位の raw 案件データを output/raw 配下へ保存します。"""
    base_dir = Path(output_dir) if output_dir is not None else Path(config.OUTPUT_DIR)
    file_path = base_dir / "raw" / build_raw_jobs_filename(source_url, date=date)
    _write_json_file(_jobs_to_dicts(jobs), file_path)
    return file_path


def save_jobs_snapshot(jobs: list[Job], output_dir: Path, now: str) -> Path:
    """案件データのスナップショットを output/snapshots 配下へ保存します。"""
    try:
        dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        timestamp = dt.strftime("%Y%m%d_%H%M%S")
    except ValueError:
        digits = "".join(ch for ch in now if ch.isdigit())
        if len(digits) < 14:
            raise ValueError(f"Invalid ISO datetime string: {now}")
        timestamp = f"{digits[:8]}_{digits[8:14]}"

    file_path = output_dir / "snapshots" / f"jobs_{timestamp}.json"
    export_jobs_to_json(jobs, file_path)
    return file_path


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
    _write_json_file(_jobs_to_dicts(jobs), file_path)


def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _normalize_client_profile_description(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = re.sub(r"\s+", " ", value.strip())
    if len(normalized) <= MAX_CLIENT_PROFILE_DESCRIPTION_LENGTH:
        return normalized

    return normalized[: MAX_CLIENT_PROFILE_DESCRIPTION_LENGTH - 3] + "..."


def _build_ai_client(client: dict | None) -> dict | None:
    if client is None:
        return None

    return {
        "name": client.get("name"),
        "rating": client.get("rating"),
        "identity_verified": client.get("identity_verified"),
        "rule_checked": client.get("rule_checked"),
        "jobs_posted_count": client.get("jobs_posted_count"),
        "project_finished_rate": client.get("project_finished_rate"),
        "profile_description": _normalize_client_profile_description(
            client.get("profile_description")
        ),
    }


def _has_detail_for_ai(job_dict: dict) -> bool:
    detail_values = [
        job_dict.get("category"),
        job_dict.get("sub_category"),
        job_dict.get("description"),
        job_dict.get("reward"),
        job_dict.get("application_deadline"),
        job_dict.get("published_at"),
        job_dict.get("application_count"),
        job_dict.get("contract_count"),
        job_dict.get("recruitment_count"),
        job_dict.get("favorite_count"),
    ]

    if any(not _is_blank(value) for value in detail_values):
        return True

    client = _build_ai_client(job_dict.get("client"))
    if client is None:
        return False

    return any(not _is_blank(value) for value in client.values())


def _build_ai_job_record(job: Job) -> dict | None:
    job_dict = asdict(job)
    if not _has_detail_for_ai(job_dict):
        return None

    return {
        "id": job_dict.get("id"),
        "title": job_dict.get("title"),
        "url": job_dict.get("url"),
        "category": job_dict.get("category"),
        "sub_category": job_dict.get("sub_category"),
        "description": job_dict.get("description"),
        "reward": job_dict.get("reward"),
        "application_deadline": job_dict.get("application_deadline"),
        "published_at": job_dict.get("published_at"),
        "application_count": job_dict.get("application_count"),
        "contract_count": job_dict.get("contract_count"),
        "recruitment_count": job_dict.get("recruitment_count"),
        "favorite_count": job_dict.get("favorite_count"),
        "client": _build_ai_client(job_dict.get("client")),
    }


def export_jobs_for_ai_jsonl(jobs: list[Job], file_path: str | Path) -> None:
    """AI 入力用に Job 配列を JSON Lines 形式で保存します。"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for job in jobs:
            record = _build_ai_job_record(job)
            if record is None:
                continue
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def export_update_summary(summary: dict, file_path: str | Path) -> None:
    """更新サマリーを UTF-8 形式の JSON ファイルとして保存します。"""
    _write_json_file(summary, file_path)


def export_job_analysis_results(items: list[dict], output_path: str | Path) -> None:
    """job/analysis のペアを UTF-8 形式の JSON ファイルとして保存します。"""
    _write_json_file(items, output_path)


def export_ranked_job_analysis_results(
    items: list[dict], output_path: str | Path
) -> None:
    """rank 情報を含む分析結果を UTF-8 形式の JSON ファイルとして保存します。"""
    export_job_analysis_results(items, output_path)
