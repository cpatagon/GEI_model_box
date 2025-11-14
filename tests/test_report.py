"""Pruebas para las utilidades de reporte."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np

from ofc_model.physics import ChamberGeometry
from ofc_model.report import save_fit, save_simulation
from ofc_model.simulate import SimulationResult
from ofc_model.workflows import BootstrapIntervals, FitWorkflowResult
from ofc_model.fitting import ExponentialFitResult


def test_save_simulation_creates_artifacts() -> None:
    result = SimulationResult(
        time_s=np.array([0.0, 1.0, 2.0]),
        concentration_ppm=np.array([400.0, 410.0, 418.0]),
        geometry=ChamberGeometry(volume_m3=0.01, area_m2=0.07),
        flow_m3_s=0.002,
        ambient_ppm=400.0,
        target_cg_ppm=420.0,
        scenario_label="test_case",
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "sim.csv"
        csv_path, parquet_path, plot_path = save_simulation(result, output)
        assert csv_path.exists()
        assert plot_path.exists()
        if parquet_path is not None:
            assert parquet_path.exists()


def test_save_fit_writes_summary_with_intervals() -> None:
    fit = ExponentialFitResult(
        c0=420.0,
        cg=480.0,
        theta_s=12.0,
        rmse=0.1,
        r2=0.99,
        nt=10.0,
        residuals=np.array([0.0, 0.0]),
    )
    workflow_result = FitWorkflowResult(
        time_s=np.array([0.0, 1.0]),
        observed_ppm=np.array([420.0, 430.0]),
        fit=fit,
        geometry=ChamberGeometry(volume_m3=0.01, area_m2=0.07),
        ambient_ppm=420.0,
        flux_mg_m2_h=2.0,
        bootstrap=BootstrapIntervals(cg_ppm=(470.0, 490.0), theta_s=(11.0, 13.0), flux_mg_m2_h=(1.8, 2.2)),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "fit.json"
        json_path, plot_path, summary = save_fit(workflow_result, output)
        assert json_path.exists()
        assert plot_path.exists()
        data = json.loads(json_path.read_text())
        assert "cg_ppm_ci" in data
        assert "theta_s_ci" in data
        assert "flux_mg_m2_h_ci" in data
        assert tuple(data["cg_ppm_ci"]) == (470.0, 490.0)
        assert summary["cg_ppm"] == 480.0
