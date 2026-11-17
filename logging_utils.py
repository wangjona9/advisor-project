from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime, timezone


def append_log(record: dict, log_dir: str | Path = "logs") -> Path:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "interactions.jsonl"
    record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), **record}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path
