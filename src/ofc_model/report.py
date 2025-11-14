"""Utilidades para persistir resultados de simulación y ajuste."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

from .io import (
    ensure_directory,
    write_json,
    write_timeseries_csv,
    write_timeseries_parquet,
)
from .plotting import plot_fit, plot_simulation
from .simulate import SimulationResult
from .workflows import FitWorkflowResult


def save_simulation(result: SimulationResult, output_path: Path) -> Tuple[Path, Optional[Path], Path]:
    """Guarda CSV, Parquet y PNG para una simulación dada."""

    ensure_directory(output_path.parent)
    csv_path = write_timeseries_csv(output_path, result.time_s, result.concentration_ppm, header=("time_s", "C_ppm"))
    parquet_path = write_timeseries_parquet(
        output_path.with_suffix(".parquet"),
        result.time_s,
        result.concentration_ppm,
        ("time_s", "C_ppm"),
    )
    plot_path = output_path.with_suffix(".png")
    plot_simulation(
        result.time_s,
        result.concentration_ppm,
        plot_path,
        title=f"Simulación OFC - {result.scenario_label}",
    )
    return csv_path, parquet_path, plot_path


def save_fit(result: FitWorkflowResult, output_path: Path) -> Tuple[Path, Path, Dict[str, float]]:
    """Guarda JSON + PNG y devuelve el resumen utilizado."""

    ensure_directory(output_path.parent)
    summary = {
        "c0_ppm": result.fit.c0,
        "cg_ppm": result.fit.cg,
        "theta_s": result.fit.theta_s,
        "rmse_ppm": result.fit.rmse,
        "r2": result.fit.r2,
        "nt": result.fit.nt,
        "flux_mg_m2_h": result.flux_mg_m2_h,
        "ambient_ppm": result.ambient_ppm,
    }
    if result.bootstrap:
        summary.update(
            {
                "cg_ppm_ci": result.bootstrap.cg_ppm,
                "theta_s_ci": result.bootstrap.theta_s,
                "flux_mg_m2_h_ci": result.bootstrap.flux_mg_m2_h,
            }
        )
    json_path = write_json(output_path, summary)
    plot_path = output_path.with_suffix(".png")
    plot_fit(
        result.time_s,
        result.observed_ppm,
        result.predicted_ppm,
        plot_path,
        title="Ajuste OFC",
    )
    return json_path, plot_path, summary
