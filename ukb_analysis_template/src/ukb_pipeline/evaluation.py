from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from .models import ModelResult


def results_to_dataframe(results: list[ModelResult]) -> pd.DataFrame:
    if not results:
        return pd.DataFrame(
            columns=[
                "model_type",
                "exposure",
                "term",
                "coef",
                "lower_ci",
                "upper_ci",
                "p_value",
                "effect",
            ]
        )
    return pd.DataFrame([asdict(r) for r in results])
