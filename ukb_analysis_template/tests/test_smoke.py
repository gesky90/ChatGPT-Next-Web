from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ukb_pipeline.pipeline import run_pipeline


def test_binary_pipeline_smoke(tmp_path: Path) -> None:
    n = 500
    rng = np.random.default_rng(42)
    x = rng.normal(size=n)
    age = rng.normal(55, 8, size=n)
    sex = rng.integers(0, 2, size=n)
    logits = -1 + 0.6 * x + 0.02 * age + 0.2 * sex
    p = 1 / (1 + np.exp(-logits))
    y = rng.binomial(1, p)

    df = pd.DataFrame(
        {
            "raw_x": x,
            "raw_age": age,
            "raw_sex": sex,
            "raw_y": y,
        }
    )
    data_path = tmp_path / "demo.csv"
    df.to_csv(data_path, index=False)

    project = {
        "project": {"name": "demo", "seed": 42},
        "data": {"input_path": str(data_path), "format": "csv", "id_column": "eid"},
        "analysis": {
            "outcome": {"type": "binary", "column": "y"},
            "exposure": {"columns": ["x"]},
            "covariates": {"columns": ["age", "sex"]},
            "options": {"standardize_numeric": False, "dropna_strategy": "modelwise", "min_rows": 100},
        },
        "output": {
            "table_dir": str(tmp_path / "tables"),
            "model_dir": str(tmp_path / "models"),
            "figure_dir": str(tmp_path / "figures"),
            "log_file": str(tmp_path / "logs" / "pipeline.log"),
        },
    }

    fields = {
        "fields": {
            "rename_map": {
                "raw_x": "x",
                "raw_age": "age",
                "raw_sex": "sex",
                "raw_y": "y",
            },
            "missing_codes": [],
            "category_maps": {},
            "numeric_bounds": {},
        }
    }

    project_path = tmp_path / "project.yaml"
    fields_path = tmp_path / "fields.yaml"
    project_path.write_text(yaml.safe_dump(project, sort_keys=False), encoding="utf-8")
    fields_path.write_text(yaml.safe_dump(fields, sort_keys=False), encoding="utf-8")

    run_pipeline(str(project_path), str(fields_path))

    out = tmp_path / "tables" / "model_summary.csv"
    assert out.exists()
    result = pd.read_csv(out)
    assert "x" in set(result["term"])
