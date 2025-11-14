"""Modelos simples de caudal de aire descritos en el README."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np


@dataclass(frozen=True)
class FlowTimeseries:
    """Serie de caudal proveniente de sensores o archivos CSV."""

    time_s: np.ndarray
    flow_m3_s: np.ndarray

    def __post_init__(self) -> None:
        if self.time_s.shape != self.flow_m3_s.shape:
            raise ValueError("El vector de tiempo debe coincidir con el de caudales")
        if np.any(self.time_s < 0):
            raise ValueError("El tiempo no puede ser negativo")


def flow_from_area_velocity(area_m2: float, velocity_m_s: float) -> float:
    """Modelo "Q = A * v"."""

    if area_m2 <= 0:
        raise ValueError("area_m2 debe ser positivo")
    return area_m2 * velocity_m_s


def flow_from_orifice(
    discharge_coeff: float,
    area_m2: float,
    delta_p_pa: float,
    fluid_density_kg_m3: float = 1.2,
) -> float:
    """Caudal estimado mediante orificio: ``Q = Cd * A * sqrt(2ΔP / ρ)``."""

    if not 0 < discharge_coeff <= 1:
        raise ValueError("Cd debe estar en (0, 1]")
    if area_m2 <= 0:
        raise ValueError("area_m2 debe ser positivo")
    if delta_p_pa < 0 or fluid_density_kg_m3 <= 0:
        raise ValueError("ΔP y densidad deben ser positivos")
    return discharge_coeff * area_m2 * np.sqrt(2.0 * delta_p_pa / fluid_density_kg_m3)


def load_flow_timeseries(csv_path: str | Path) -> FlowTimeseries:
    """Carga un CSV con columnas ``time_s`` y ``flow_m3_s``."""

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(path)

    times: List[float] = []
    flows: List[float] = []
    with path.open("r", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or {"time_s", "flow_m3_s"} - set(reader.fieldnames):
            raise ValueError("El CSV debe contener columnas time_s y flow_m3_s")
        for row in reader:
            times.append(float(row["time_s"]))
            flows.append(float(row["flow_m3_s"]))

    if not times:
        raise ValueError("El CSV no contiene datos")

    return FlowTimeseries(time_s=np.array(times, dtype=float), flow_m3_s=np.array(flows, dtype=float))


def resample_flow(timeseries: FlowTimeseries, new_time: Iterable[float]) -> np.ndarray:
    """Reinterpolación lineal para alinear caudales con simulaciones."""

    new_time_arr = np.asarray(list(new_time), dtype=float)
    if new_time_arr.ndim != 1:
        raise ValueError("new_time debe ser un vector 1D")
    return np.interp(new_time_arr, timeseries.time_s, timeseries.flow_m3_s)
