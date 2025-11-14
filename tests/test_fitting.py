"""Pruebas para el módulo de ajuste exponencial."""
from __future__ import annotations

import math
import unittest

import numpy as np

from ofc_model import fitting
from ofc_model.physics import concentration_transient


class FitExponentialResponseTest(unittest.TestCase):
    def test_recovers_clean_parameters(self) -> None:
        time = np.linspace(0, 60, num=25)
        concentrations = concentration_transient(time, c0=420, cg=480, theta_s=12)
        result = fitting.fit_exponential_response(time, concentrations)
        self.assertTrue(math.isclose(result.cg, 480, rel_tol=1e-3))
        self.assertTrue(math.isclose(result.theta_s, 12, rel_tol=1e-3))
        self.assertLess(result.rmse, 1e-6)
        self.assertGreaterEqual(result.r2, 0.999)

    def test_handles_noisy_data_and_predict(self) -> None:
        rng = np.random.default_rng(123)
        time = np.linspace(0, 60, num=30)
        clean = concentration_transient(time, c0=415, cg=470, theta_s=8)
        noisy = clean + rng.normal(0, 0.5, size=clean.shape)
        result = fitting.fit_exponential_response(time, noisy)
        preds = result.predict(time)
        self.assertEqual(preds.shape, noisy.shape)
        self.assertLess(result.rmse, 2.0)
        self.assertGreater(result.r2, 0.8)

    def test_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            fitting.fit_exponential_response([0, 1], [1, 2])
        with self.assertRaises(ValueError):
            fitting.fit_exponential_response([1, 0, 2], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
