import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from models import Job


def export_jobs_to_json(jobs: Sequence[Job], file_path: str | Path) -> None:
    """Job オブジェクトの配列を UTF-8 形式の JSON ファイルとして保存します。"""
    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    json_text = (
        json.dumps([asdict(job) for job in jobs], ensure_ascii=False, indent=2) + "\n"
    )
    output_path.write_text(json_text, encoding="utf-8")
