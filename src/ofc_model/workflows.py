"""Workflows que combinan fitting y cálculo de flujo.""" 
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

import numpy as np

from .fitting import ExponentialFitResult, fit_exponential_response
from .physics import ChamberGeometry, flux_from_exponential_fit


@dataclass(frozen=True)
class BootstrapIntervals:
    cg_ppm: Tuple[float, float]
    theta_s: Tuple[float, float]
    flux_mg_m2_h: Tuple[float, float]


@dataclass(frozen=True)
class FitWorkflowResult:
    time_s: np.ndarray
    observed_ppm: np.ndarray
    fit: ExponentialFitResult
    geometry: ChamberGeometry
    ambient_ppm: float
    flux_mg_m2_h: float
    bootstrap: Optional[BootstrapIntervals] = None

    @property
    def predicted_ppm(self) -> np.ndarray:
        return self.fit.predict(self.time_s)


def run_fit_workflow(config: Dict, time_s: Iterable[float], concentration_ppm: Iterable[float]) -> FitWorkflowResult:
    time_arr = np.asarray(list(time_s), dtype=float)
    conc_arr = np.asarray(list(concentration_ppm), dtype=float)
    fit_cfg = config.get("fitting", {})
    time_arr, conc_arr = _apply_window(time_arr, conc_arr, fit_cfg)

    fit_result = fit_exponential_response(time_arr, conc_arr)
    geometry = ChamberGeometry(
        volume_m3=config["camera"]["Vc_m3"],
        area_m2=config["camera"]["Ac_m2"],
    )
    ambient = config.get("ambient", {})
    ca = float(ambient.get("CA_ppm", conc_arr[0]))
    flux = flux_from_exponential_fit(geometry, theta_s=fit_result.theta_s, cg=fit_result.cg, ca=ca)

    bootstrap = None
    if fit_cfg.get("use_bootstrap"):
        bootstrap = _bootstrap_intervals(time_arr, conc_arr, geometry, ca, fit_cfg)

    return FitWorkflowResult(
        time_s=time_arr,
        observed_ppm=conc_arr,
        fit=fit_result,
        geometry=geometry,
        ambient_ppm=ca,
        flux_mg_m2_h=flux,
        bootstrap=bootstrap,
    )


def _apply_window(time: np.ndarray, conc: np.ndarray, fit_cfg: Dict) -> Tuple[np.ndarray, np.ndarray]:
    min_window = float(fit_cfg.get("min_window_s", 0)) or None
    max_window = float(fit_cfg.get("max_window_s", 0)) or None
    if min_window is None and max_window is None:
        return time, conc

    latest_time = time[-1]
    start_time = time[0]
    if max_window:
        start_time = max(start_time, latest_time - max_window)
    if min_window:
        start_time = min(start_time, latest_time - min_window)

    start_idx = np.searchsorted(time, start_time)
    return time[start_idx:], conc[start_idx:]


def _bootstrap_intervals(
    time: np.ndarray,
    conc: np.ndarray,
    geometry: ChamberGeometry,
    ambient_ppm: float,
    fit_cfg: Dict,
) -> BootstrapIntervals:
    n_samples = int(fit_cfg.get("n_bootstrap", 200))
    rng = np.random.default_rng(int(fit_cfg.get("bootstrap_seed", 1234)))
    cg_values = []
    theta_values = []
    flux_values = []
    indices = np.arange(len(time))
    for _ in range(max(n_samples, 1)):
        sample_idx = rng.choice(indices, size=len(indices), replace=True)
        sample_idx.sort()
        sample_time = time[sample_idx]
        sample_conc = conc[sample_idx]
        fit = fit_exponential_response(sample_time, sample_conc)
        cg_values.append(fit.cg)
        theta_values.append(fit.theta_s)
        flux_values.append(
            flux_from_exponential_fit(geometry, theta_s=fit.theta_s, cg=fit.cg, ca=ambient_ppm)
        )

    def _interval(data):
        arr = np.array(data)
        return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))

    return BootstrapIntervals(
        cg_ppm=_interval(cg_values),
        theta_s=_interval(theta_values),
        flux_mg_m2_h=_interval(flux_values),
    )
