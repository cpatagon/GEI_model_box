"""Utilidades de entrada/salida utilizadas a lo largo del proyecto."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml


def load_yaml(path: str | Path) -> dict:
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(file)
    with file.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def dump_yaml(path: str | Path, payload: dict) -> Path:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(payload, fh, sort_keys=False)
    return file


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_concentration_csv(path: str | Path, time_key: str = "time_s", value_key: str = "C_ppm") -> Tuple[np.ndarray, np.ndarray]:
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(file)

    times: list[float] = []
    values: list[float] = []
    with file.open("r", newline="") as fh:
        reader = csv.DictReader(fh)
        expected = {time_key, value_key}
        if not reader.fieldnames or expected - set(reader.fieldnames):
            raise ValueError(f"El CSV debe contener las columnas {time_key} y {value_key}")
        for row in reader:
            if row[time_key] == "" or row[value_key] == "":
                continue
            times.append(float(row[time_key]))
            values.append(float(row[value_key]))
    if not times:
        raise ValueError("El CSV de concentración está vacío")
    return np.array(times, dtype=float), np.array(values, dtype=float)


def write_timeseries_csv(path: str | Path, time: Iterable[float], values: Iterable[float], header: Tuple[str, str]) -> Path:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    rows = list(zip(time, values))
    with file.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    return file


def write_timeseries_parquet(
    path: str | Path,
    time: Sequence[float],
    values: Sequence[float],
    columns: Tuple[str, str],
) -> Optional[Path]:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({columns[0]: time, columns[1]: values})
    try:
        df.to_parquet(file, index=False)
    except ImportError:
        return None
    return file


def write_json(path: str | Path, payload: dict) -> Path:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return file
