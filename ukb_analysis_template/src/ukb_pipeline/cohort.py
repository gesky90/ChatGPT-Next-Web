from __future__ import annotations

import pandas as pd


def build_model_dataset(
    df: pd.DataFrame,
    outcome_cols: list[str],
    exposure_cols: list[str],
    covariate_cols: list[str],
    dropna_strategy: str,
) -> pd.DataFrame:
    needed = list(dict.fromkeys(outcome_cols + exposure_cols + covariate_cols))
    data = df[needed].copy()

    if dropna_strategy in {"modelwise", "complete_case"}:
        data = data.dropna()
    else:
        raise ValueError(f"Unsupported dropna strategy: {dropna_strategy}")

    return data


def cohort_flow_report(df_before: pd.DataFrame, df_after: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"step": "input_rows", "n": len(df_before)},
            {"step": "analysis_rows", "n": len(df_after)},
            {"step": "excluded_rows", "n": len(df_before) - len(df_after)},
        ]
    )
