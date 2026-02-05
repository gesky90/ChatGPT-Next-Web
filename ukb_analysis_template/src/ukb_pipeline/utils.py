from __future__ import annotations

import logging
import os
import random
from pathlib import Path

import numpy as np


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def setup_logger(log_file: str) -> logging.Logger:
    ensure_dir(Path(log_file).parent)
    logger = logging.getLogger("ukb_pipeline")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    logger.info("Logger initialized. PID=%s", os.getpid())
    return logger
