from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_dataset(path: str, data_format: str) -> pd.DataFrame:
    fmt = data_format.lower()
    if fmt == "csv":
        return pd.read_csv(path, low_memory=False)
    if fmt == "tsv":
        return pd.read_csv(path, sep="\t", low_memory=False)
    if fmt == "parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported data format: {data_format}")


def write_table(df: pd.DataFrame, output_path: str) -> None:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
