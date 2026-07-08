import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import config

_JST = ZoneInfo("Asia/Tokyo")


def build_collection_log_path(
    output_dir: str | Path,
    log_datetime: datetime | None = None,
) -> Path:
    """日付別の収集ログ JSONL ファイルパスを生成する。"""
    dt = log_datetime or datetime.now(_JST)
    date_part = dt.astimezone(_JST).strftime("%Y%m%d")
    return (
        Path(output_dir)
        / config.OUTPUT_LOGS_DIRNAME
        / f"{config.OUTPUT_COLLECTION_LOG_PREFIX}_{date_part}.jsonl"
    )


def append_collection_log(
    record: dict,
    output_dir: str | Path,
    log_datetime: datetime | None = None,
) -> Path:
    """収集ログを JSON Lines 形式で1行追記する。"""
    log_path = build_collection_log_path(output_dir, log_datetime=log_datetime)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return log_path
