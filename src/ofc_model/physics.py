"""Core ecuaciones del modelo de cámara de flujo abierta (OFC).

El README describe dos expresiones clave:
- Respuesta exponencial del gas dentro de la cámara: ``C(t) = C_G - (C_G - C_0)e^{-t/\theta_G}``
- Flujo superficial derivado a partir del ajuste: ``F = \frac{V_C}{\theta_G} \frac{(C_G - C_A)}{A_C}``

Este módulo implementa utilidades vectorizadas para evaluar esas expresiones y
realizar validaciones básicas de parámetros. Los scripts y módulos de fitting
consumirán estas funciones para simular cámaras y computar flujos.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Union

import numpy as np

Number = Union[float, np.ndarray]


@dataclass(frozen=True)
class ChamberGeometry:
    """Parámetros geométricos mínimos de una cámara OFC."""

    volume_m3: float
    area_m2: float

    def __post_init__(self) -> None:
        if self.volume_m3 <= 0:
            raise ValueError("volume_m3 debe ser positivo")
        if self.area_m2 <= 0:
            raise ValueError("area_m2 debe ser positiva")


def characteristic_time(volume_m3: float, flow_m3_s: float) -> float:
    """Calcula ``theta_G = Vc / Qg`` validando entradas."""

    if volume_m3 <= 0:
        raise ValueError("volume_m3 debe ser positivo")
    if flow_m3_s <= 0:
        raise ValueError("flow_m3_s debe ser positivo")
    return volume_m3 / flow_m3_s


def concentration_transient(
    time_s: Union[Number, Iterable[float]],
    c0: float,
    cg: float,
    theta_s: float,
) -> Number:
    """Evalúa la solución analítica ``C(t) = C_G - (C_G - C_0)e^{-t/theta}``.

    El tiempo puede ser un escalar o un array. Usa numpy internamente para
    vectorizar el cálculo y devolver el mismo tipo entrante cuando sea posible.
    """

    if theta_s <= 0:
        raise ValueError("theta_s debe ser positivo")
    t = np.asarray(time_s, dtype=float)
    response = cg - (cg - c0) * np.exp(-t / theta_s)
    # Devuelve escalar si la entrada era escalar para comodidad de los scripts
    if np.isscalar(time_s):
        return float(response)
    return response


def flux_from_exponential_fit(
    geometry: ChamberGeometry,
    theta_s: float,
    cg: float,
    ca: float,
) -> float:
    """Calcula el flujo superficial ``F`` a partir de ``theta`` y concentraciones.

    La fórmula proviene del README: ``F = (Vc/\theta) * (C_G - C_A) / A_c``.
    """

    if theta_s <= 0:
        raise ValueError("theta_s debe ser positivo")
    return (geometry.volume_m3 / theta_s) * (cg - ca) / geometry.area_m2


def simulate_chamber_response(
    time_s: Union[Number, Iterable[float]],
    c0: float,
    ca: float,
    geometry: ChamberGeometry,
    flow_m3_s: float,
    equilibrium_concentration: float,
) -> Number:
    """Conveniencia que encadena ``characteristic_time`` y ``concentration``.

    Útil para scripts que necesitan la serie temporal completa a partir de los
    parámetros físicos: volumen, caudal y concentración de equilibrio.
    """

    theta = characteristic_time(geometry.volume_m3, flow_m3_s)
    return concentration_transient(time_s, c0=c0, cg=equilibrium_concentration, theta_s=theta)
