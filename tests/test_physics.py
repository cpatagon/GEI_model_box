"""Pruebas unitarias básicas para el módulo `physics`."""
from __future__ import annotations

import math
import unittest

import numpy as np

from ofc_model.physics import (
    ChamberGeometry,
    characteristic_time,
    concentration_transient,
    flux_from_exponential_fit,
    simulate_chamber_response,
)


class ChamberGeometryTest(unittest.TestCase):
    def test_geometry_validation(self) -> None:
        with self.assertRaises(ValueError):
            ChamberGeometry(volume_m3=0, area_m2=1)
        with self.assertRaises(ValueError):
            ChamberGeometry(volume_m3=1, area_m2=-1)


class CharacteristicTimeTest(unittest.TestCase):
    def test_positive_values(self) -> None:
        self.assertTrue(math.isclose(characteristic_time(0.01, 0.001), 10.0))
        with self.assertRaises(ValueError):
            characteristic_time(-1, 1)
        with self.assertRaises(ValueError):
            characteristic_time(1, 0)


class ConcentrationTransientTest(unittest.TestCase):
    def test_limits(self) -> None:
        result = concentration_transient([0.0, 10.0], c0=400, cg=460, theta_s=5)
        self.assertTrue(math.isclose(result[0], 400.0))
        self.assertGreater(result[-1], 450.0)
        with self.assertRaises(ValueError):
            concentration_transient(1.0, 400, 450, theta_s=0)


class FluxFromFitTest(unittest.TestCase):
    def test_matches_manual_expression(self) -> None:
        geom = ChamberGeometry(volume_m3=0.011, area_m2=0.071)
        flux = flux_from_exponential_fit(geom, theta_s=2.0, cg=480, ca=420)
        manual = (0.011 / 2.0) * (480 - 420) / 0.071
        self.assertTrue(math.isclose(flux, manual))
        with self.assertRaises(ValueError):
            flux_from_exponential_fit(geom, theta_s=0, cg=480, ca=420)


class SimulateChamberResponseTest(unittest.TestCase):
    def test_matches_direct_solution(self) -> None:
        geom = ChamberGeometry(volume_m3=0.011, area_m2=0.071)
        response = simulate_chamber_response(
            time_s=np.array([0, 5, 10]),
            c0=420,
            ca=420,
            geometry=geom,
            flow_m3_s=0.0022,
            equilibrium_concentration=480,
        )
        theta = characteristic_time(0.011, 0.0022)
        expected = concentration_transient([0, 5, 10], 420, 480, theta)
        np.testing.assert_allclose(response, expected)


if __name__ == "__main__":
    unittest.main()
