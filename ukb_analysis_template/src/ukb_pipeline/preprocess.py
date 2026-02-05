from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def rename_columns(df: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    return df.rename(columns=rename_map)


def replace_missing_codes(df: pd.DataFrame, missing_codes: list[Any]) -> pd.DataFrame:
    return df.replace(missing_codes, np.nan)


def apply_category_maps(df: pd.DataFrame, category_maps: dict[str, dict[Any, Any]]) -> pd.DataFrame:
    out = df.copy()
    for col, mapping in category_maps.items():
        if col in out.columns:
            out[col] = out[col].map(lambda x: mapping.get(x, x))
    return out


def clip_numeric_bounds(df: pd.DataFrame, numeric_bounds: dict[str, dict[str, float]]) -> pd.DataFrame:
    out = df.copy()
    for col, bound in numeric_bounds.items():
        if col in out.columns:
            lower = bound.get("lower", -np.inf)
            upper = bound.get("upper", np.inf)
            out[col] = out[col].clip(lower=lower, upper=upper)
    return out


def standardize_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns and pd.api.types.is_numeric_dtype(out[col]):
            std = out[col].std()
            if std and std > 0:
                out[col] = (out[col] - out[col].mean()) / std
    return out


def profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append(
            {
                "column": col,
                "dtype": str(s.dtype),
                "n_missing": int(s.isna().sum()),
                "missing_rate": float(s.isna().mean()),
                "n_unique": int(s.nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)
