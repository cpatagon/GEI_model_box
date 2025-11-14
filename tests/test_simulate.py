from __future__ import annotations

import numpy as np

from ofc_model.simulate import SimulationResult, run_simulation


def test_run_simulation_with_noise(tmp_path):
    config = {
        "camera": {"Vc_m3": 0.01, "Ac_m2": 0.01},
        "ambient": {"CA_ppm": 420},
        "simulation": {"target_cg_ppm": 450, "noise_ppm_std": 1.0, "noise_seed": 123},
        "scenario": {"duration_s": 10, "label": "test"},
        "inflow": {"mode": "area_velocity", "area_m2": 0.01, "velocity_ms": 0.002},
    }
    result = run_simulation(config)
    assert isinstance(result, SimulationResult)
    assert result.noise_ppm_std == 1.0
    result2 = run_simulation(config)
    np.testing.assert_allclose(result.concentration_ppm, result2.concentration_ppm)
