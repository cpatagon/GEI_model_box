"""Rutinas de ajuste exponencial para series de cámaras OFC."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Tuple

import numpy as np

from .physics import concentration_transient


@dataclass(frozen=True)
class ExponentialFitResult:
    """Encapsula los parámetros estimados y métricas de calidad."""

    c0: float
    cg: float
    theta_s: float
    rmse: float
    r2: float
    nt: float
    residuals: np.ndarray = field(repr=False)

    def predict(self, time_s: Iterable[float] | np.ndarray) -> np.ndarray:
        return concentration_transient(time_s, c0=self.c0, cg=self.cg, theta_s=self.theta_s)


def fit_exponential_response(time_s: Iterable[float], concentration: Iterable[float]) -> ExponentialFitResult:
    """Ajusta ``C(t) = C_G - (C_G - C_0)e^{-t/\theta}`` usando regresión logarítmica."""

    time = np.asarray(list(time_s), dtype=float)
    conc = np.asarray(list(concentration), dtype=float)
    if time.ndim != 1 or conc.ndim != 1 or len(time) != len(conc):
        raise ValueError("time y concentration deben ser vectores 1D del mismo tamaño")
    if len(time) < 3:
        raise ValueError("Se requieren al menos tres observaciones para ajustar")
    if np.any(np.diff(time) < 0):
        raise ValueError("El vector de tiempo debe estar ordenado de manera no decreciente")

    duration = max(time[-1] - time[0], 1e-6)
    c0 = float(conc[0])

    cg, theta = _grid_search_parameters(time, conc, c0, duration)
    cg, theta = _refine_with_gauss_newton(time, conc, c0, cg, theta)

    predictions = concentration_transient(time, c0=c0, cg=cg, theta_s=theta)
    residuals = predictions - conc
    rmse = float(np.sqrt(np.mean(residuals**2)))

    ss_tot = float(np.sum((conc - conc.mean()) ** 2))
    ss_res = float(np.sum(residuals**2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    sample_sd = float(conc.std(ddof=1)) if len(conc) > 1 else 0.0
    if rmse == 0:
        nt = float("inf")
    else:
        nt = sample_sd / rmse - 1.0

    return ExponentialFitResult(c0=c0, cg=float(cg), theta_s=float(theta), rmse=rmse, r2=r2, nt=nt, residuals=residuals)


def _grid_search_parameters(
    time: np.ndarray,
    conc: np.ndarray,
    c0: float,
    duration: float,
) -> Tuple[float, float]:
    """Estimación iterativa de ``C_G`` y ``theta``.

    Se hace una búsqueda unidimensional sobre ``C_G`` y se deriva ``theta`` por
    regresión lineal en el espacio logarítmico.
    """

    cg_floor = max(conc.max(), c0 + 1e-6)
    cg_ceiling = cg_floor + max(5.0, 0.2 * abs(cg_floor))

    best_error = np.inf
    best_params = None

    low, high = cg_floor, cg_ceiling
    for _ in range(4):
        candidates = np.linspace(low, high, num=120)
        for cg in candidates:
            theta = _theta_from_candidate(time, conc, cg)
            if theta is None or theta <= 0:
                continue
            preds = concentration_transient(time, c0=c0, cg=cg, theta_s=theta)
            error = float(np.mean((preds - conc) ** 2))
            if error < best_error:
                best_error = error
                best_params = (float(cg), float(theta))
        span = high - low
        if best_params is None:
            break
        best_cg = best_params[0]
        low = max(c0 + 1e-6, best_cg - span / 4)
        high = best_cg + span / 4

    if best_params is None:
        raise ValueError("No se pudo estimar C_G; verifique que la serie sea monótona")

    return best_params


def _theta_from_candidate(time: np.ndarray, conc: np.ndarray, cg: float) -> float | None:
    """Calcula ``theta`` usando regresión lineal sobre ``ln(C_G - C(t))``."""

    diff = cg - conc
    if np.any(diff <= 0):
        return None
    log_diff = np.log(diff)
    x_mean = float(time.mean())
    y_mean = float(log_diff.mean())
    cov = float(np.mean((time - x_mean) * (log_diff - y_mean)))
    var = float(np.mean((time - x_mean) ** 2))
    if var == 0:
        return None
    slope = cov / var
    if slope >= 0:
        return None
    theta = -1.0 / slope
    return theta


def _refine_with_gauss_newton(
    time: np.ndarray,
    conc: np.ndarray,
    c0: float,
    cg_init: float,
    theta_init: float,
) -> Tuple[float, float]:
    """Refina ``C_G`` y ``theta`` mediante un Gauss-Newton de dos parámetros."""

    cg = float(cg_init)
    theta = max(float(theta_init), 1e-6)

    for _ in range(8):
        exp_term = np.exp(-time / theta)
        preds = cg - (cg - c0) * exp_term
        residual = preds - conc
        df_dcg = 1.0 - exp_term
        df_dtheta = -(cg - c0) * exp_term * (time / theta**2)

        j11 = float(np.dot(df_dcg, df_dcg))
        j22 = float(np.dot(df_dtheta, df_dtheta))
        j12 = float(np.dot(df_dcg, df_dtheta))
        det = j11 * j22 - j12 * j12
        if abs(det) < 1e-12:
            break
        rhs0 = -float(np.dot(df_dcg, residual))
        rhs1 = -float(np.dot(df_dtheta, residual))
        delta_cg = (rhs0 * j22 - j12 * rhs1) / det
        delta_theta = (j11 * rhs1 - j12 * rhs0) / det

        cg = max(c0 + 1e-6, cg + delta_cg)
        theta = max(1e-6, theta + delta_theta)
        if abs(delta_cg) < 1e-6 and abs(delta_theta) < 1e-6:
            break

    return cg, theta
