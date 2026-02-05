from __future__ import annotations

import json
from pathlib import Path


def write_run_metadata(output_path: str, metadata: dict) -> None:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
