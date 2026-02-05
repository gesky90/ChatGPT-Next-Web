from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from ukb_pipeline.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run generic UKB analysis pipeline")
    parser.add_argument("--project", required=True, help="Path to project yaml")
    parser.add_argument("--fields", required=True, help="Path to fields yaml")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.project, args.fields)
