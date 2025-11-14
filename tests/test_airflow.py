"""Pruebas unitarias para `ofc_model.airflow`."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from ofc_model.airflow import (
    FlowTimeseries,
    flow_from_area_velocity,
    flow_from_orifice,
    load_flow_timeseries,
    resample_flow,
)


class FlowFromAreaVelocityTest(unittest.TestCase):
    def test_simple_product(self) -> None:
        self.assertAlmostEqual(flow_from_area_velocity(0.01, 2.0), 0.02)
        with self.assertRaises(ValueError):
            flow_from_area_velocity(0.0, 1.0)


class FlowFromOrificeTest(unittest.TestCase):
    def test_expected_range(self) -> None:
        value = flow_from_orifice(discharge_coeff=0.8, area_m2=0.0005, delta_p_pa=15.0)
        self.assertGreater(value, 0)
        with self.assertRaises(ValueError):
            flow_from_orifice(0, 0.0005, 10)


class LoadFlowTimeseriesTest(unittest.TestCase):
    def test_loads_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "flow.csv"
            path.write_text("time_s,flow_m3_s\n0,0.001\n1,0.002\n")
            series = load_flow_timeseries(path)
            self.assertIsInstance(series, FlowTimeseries)
            np.testing.assert_array_equal(series.time_s, np.array([0.0, 1.0]))
            np.testing.assert_array_equal(series.flow_m3_s, np.array([0.001, 0.002]))

    def test_missing_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "flow.csv"
            path.write_text("foo,bar\n0,1\n")
            with self.assertRaises(ValueError):
                load_flow_timeseries(path)


class ResampleFlowTest(unittest.TestCase):
    def test_linear_interpolation(self) -> None:
        series = FlowTimeseries(
            time_s=np.array([0.0, 1.0, 2.0]),
            flow_m3_s=np.array([0.0, 1.0e-3, 2.0e-3]),
        )
        new_values = resample_flow(series, [0.5, 1.5])
        np.testing.assert_allclose(new_values, [0.5e-3, 1.5e-3])


if __name__ == "__main__":
    unittest.main()
