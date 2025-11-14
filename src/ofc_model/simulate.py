"""Funciones reutilizables para ejecutar simulaciones OFC."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from .airflow import flow_from_area_velocity, flow_from_orifice, load_flow_timeseries
from .physics import ChamberGeometry, simulate_chamber_response


@dataclass(frozen=True)
class SimulationResult:
    """Serie simulada y metadatos clave."""

    time_s: np.ndarray
    concentration_ppm: np.ndarray
    geometry: ChamberGeometry
    flow_m3_s: float
    ambient_ppm: float
    target_cg_ppm: float
    scenario_label: str
    noise_ppm_std: Optional[float] = None


def run_simulation(config: Dict, duration_override: Optional[float] = None) -> SimulationResult:
    """Genera la respuesta temporal de una cámara a partir de un dict de config."""

    geometry = ChamberGeometry(
        volume_m3=config["camera"]["Vc_m3"],
        area_m2=config["camera"]["Ac_m2"],
    )
    ambient_cfg = config.get("ambient", {})
    c_ambient = float(ambient_cfg.get("CA_ppm", 420.0))
    sim_cfg = config.get("simulation", {})
    target_cg = float(sim_cfg.get("target_cg_ppm", c_ambient + 60.0))
    scenario_label = config.get("scenario", {}).get("label", "default")

    duration = duration_override or config.get("scenario", {}).get("duration_s", 180.0)
    num_samples = max(int(duration) + 1, 2)
    time_vector = np.linspace(0.0, duration, num=num_samples)

    flow_m3_s = _resolve_flow(config.get("inflow", {}))

    concentrations = simulate_chamber_response(
        time_vector,
        c0=c_ambient,
        ca=c_ambient,
        geometry=geometry,
        flow_m3_s=flow_m3_s,
        equilibrium_concentration=target_cg,
    )

    noise_std = float(sim_cfg.get("noise_ppm_std", 0.0)) if sim_cfg.get("noise_ppm_std") else None
    if noise_std:
        rng = np.random.default_rng(sim_cfg.get("noise_seed", 42))
        noise = rng.normal(0.0, noise_std, size=concentrations.shape)
        concentrations = concentrations + noise

    return SimulationResult(
        time_s=time_vector,
        concentration_ppm=concentrations,
        geometry=geometry,
        flow_m3_s=flow_m3_s,
        ambient_ppm=c_ambient,
        target_cg_ppm=target_cg,
        scenario_label=scenario_label,
        noise_ppm_std=noise_std,
    )


def _resolve_flow(inflow_cfg: Dict) -> float:
    mode = inflow_cfg.get("mode", "area_velocity")
    if mode == "area_velocity":
        return flow_from_area_velocity(inflow_cfg["area_m2"], inflow_cfg["velocity_ms"])
    if mode == "orifice":
        return flow_from_orifice(
            discharge_coeff=inflow_cfg.get("Cd", 0.62),
            area_m2=inflow_cfg.get("area_m2", 0.0005),
            delta_p_pa=inflow_cfg.get("dP_Pa", 10.0),
            fluid_density_kg_m3=inflow_cfg.get("rho_air", 1.2),
        )
    if mode == "timeseries":
        series = load_flow_timeseries(inflow_cfg["file"])
        return float(series.flow_m3_s.mean())
    raise ValueError(f"Modo de inflow no soportado: {mode}")
