from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
from lifelines import CoxPHFitter


@dataclass
class ModelResult:
    model_type: str
    exposure: str
    term: str
    coef: float
    lower_ci: float
    upper_ci: float
    p_value: float
    effect: float


def fit_continuous(df: pd.DataFrame, y: str, x: str, covars: list[str]) -> list[ModelResult]:
    data = df[[y, x] + covars].dropna()
    X = sm.add_constant(data[[x] + covars], has_constant="add")
    model = sm.OLS(data[y], X).fit()
    return _extract_sm_results(model, "linear", x)


def fit_binary(df: pd.DataFrame, y: str, x: str, covars: list[str]) -> list[ModelResult]:
    data = df[[y, x] + covars].dropna()
    X = sm.add_constant(data[[x] + covars], has_constant="add")
    model = sm.Logit(data[y], X).fit(disp=0)
    return _extract_sm_results(model, "logistic", x, exp_effect=True)


def fit_survival(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    x: str,
    covars: list[str],
) -> list[ModelResult]:
    cols = [time_col, event_col, x] + covars
    data = df[cols].dropna().copy()

    cph = CoxPHFitter()
    cph.fit(data, duration_col=time_col, event_col=event_col)

    summary = cph.summary
    if x not in summary.index:
        raise ValueError(f"Exposure {x} not found in Cox summary")

    row = summary.loc[x]
    return [
        ModelResult(
            model_type="cox",
            exposure=x,
            term=x,
            coef=float(row["coef"]),
            lower_ci=float(row["coef lower 95%"]),
            upper_ci=float(row["coef upper 95%"]),
            p_value=float(row["p"]),
            effect=float(np.exp(row["coef"])),
        )
    ]


def _extract_sm_results(model, model_type: str, exposure: str, exp_effect: bool = False) -> list[ModelResult]:
    conf = model.conf_int()
    rows: list[ModelResult] = []

    for term in model.params.index:
        if term == "const":
            continue
        coef = float(model.params[term])
        lower = float(conf.loc[term, 0])
        upper = float(conf.loc[term, 1])
        effect = float(np.exp(coef)) if exp_effect else coef

        rows.append(
            ModelResult(
                model_type=model_type,
                exposure=exposure,
                term=term,
                coef=coef,
                lower_ci=lower,
                upper_ci=upper,
                p_value=float(model.pvalues[term]),
                effect=effect,
            )
        )

    return rows
