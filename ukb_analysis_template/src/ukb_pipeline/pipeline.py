from __future__ import annotations

from pathlib import Path

from .cohort import build_model_dataset, cohort_flow_report
from .config import load_yaml, validate_placeholder, validate_project_config
from .evaluation import results_to_dataframe
from .io import read_dataset, write_table
from .models import fit_binary, fit_continuous, fit_survival
from .preprocess import (
    apply_category_maps,
    clip_numeric_bounds,
    profile_dataframe,
    rename_columns,
    replace_missing_codes,
    standardize_numeric_columns,
)
from .report import write_run_metadata
from .utils import set_global_seed, setup_logger


def run_pipeline(project_config_path: str, fields_config_path: str) -> None:
    project = load_yaml(project_config_path)
    fields = load_yaml(fields_config_path)

    validate_project_config(project)
    placeholders = validate_placeholder(project) + validate_placeholder(fields)
    if placeholders:
        msg = "Please replace placeholders before running:\n - " + "\n - ".join(placeholders)
        raise ValueError(msg)

    logger = setup_logger(project["output"]["log_file"])
    set_global_seed(int(project["project"].get("seed", 42)))

    logger.info("Loading dataset")
    df = read_dataset(project["data"]["input_path"], project["data"]["format"])

    field_cfg = fields.get("fields", {})
    df = rename_columns(df, field_cfg.get("rename_map", {}))
    df = replace_missing_codes(df, field_cfg.get("missing_codes", []))
    df = apply_category_maps(df, field_cfg.get("category_maps", {}))
    df = clip_numeric_bounds(df, field_cfg.get("numeric_bounds", {}))

    outcome_cfg = project["analysis"]["outcome"]
    exposure_cols = project["analysis"]["exposure"]["columns"]
    covariate_cols = project["analysis"]["covariates"]["columns"]

    numeric_to_standardize = exposure_cols + covariate_cols
    if project["analysis"]["options"].get("standardize_numeric", False):
        df = standardize_numeric_columns(df, numeric_to_standardize)

    outcome_cols = [outcome_cfg["column"]]
    if outcome_cfg["type"] == "survival":
        outcome_cols = [outcome_cfg["time_column"], outcome_cfg["event_column"]]

    model_df = build_model_dataset(
        df,
        outcome_cols=outcome_cols,
        exposure_cols=exposure_cols,
        covariate_cols=covariate_cols,
        dropna_strategy=project["analysis"]["options"].get("dropna_strategy", "modelwise"),
    )

    min_rows = int(project["analysis"]["options"].get("min_rows", 30))
    if len(model_df) < min_rows:
        raise ValueError(f"Rows after filtering ({len(model_df)}) < min_rows ({min_rows})")

    results = []
    for x in exposure_cols:
        if outcome_cfg["type"] == "continuous":
            results.extend(fit_continuous(model_df, outcome_cfg["column"], x, covariate_cols))
        elif outcome_cfg["type"] == "binary":
            results.extend(fit_binary(model_df, outcome_cfg["column"], x, covariate_cols))
        else:
            results.extend(
                fit_survival(
                    model_df,
                    time_col=outcome_cfg["time_column"],
                    event_col=outcome_cfg["event_column"],
                    x=x,
                    covars=covariate_cols,
                )
            )

    table_dir = Path(project["output"]["table_dir"])
    write_table(results_to_dataframe(results), str(table_dir / "model_summary.csv"))
    write_table(cohort_flow_report(df, model_df), str(table_dir / "cohort_flow.csv"))
    write_table(profile_dataframe(df), str(table_dir / "data_profile.csv"))

    write_run_metadata(
        str(table_dir / "run_metadata.json"),
        {
            "project": project["project"],
            "n_input": len(df),
            "n_analysis": len(model_df),
            "outcome_type": outcome_cfg["type"],
            "exposures": exposure_cols,
        },
    )
    logger.info("Pipeline done. Results in %s", table_dir)
