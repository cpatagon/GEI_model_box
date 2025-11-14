"""Pruebas de integración para los scripts CLI usando fixtures."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"


def _run_cli(command: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{SRC_PATH}{os.pathsep}" + env.get("PYTHONPATH", "")
    subprocess.run(command, check=True, cwd=REPO_ROOT, env=env)


class SimulateCaseScriptTest(unittest.TestCase):
    def test_output_matches_fixture(self) -> None:
        expected_csv = (REPO_ROOT / "tests/fixtures/expected_simulation.csv").read_text()
        expected_png = (REPO_ROOT / "tests/fixtures/expected_simulation.png").read_bytes()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_csv = Path(tmpdir) / "sim.csv"
            _run_cli(
                [
                    "python",
                    "scripts/simulate_case.py",
                    "--config",
                    "tests/fixtures/sim_config.yaml",
                    "--output",
                    str(output_csv),
                ]
            )
            self.assertTrue(output_csv.exists())
            self.assertEqual(output_csv.read_text(), expected_csv)

            output_png = output_csv.with_suffix(".png")
            self.assertTrue(output_png.exists())
            self.assertEqual(output_png.read_bytes(), expected_png)


class FitFromCsvScriptTest(unittest.TestCase):
    def test_output_matches_fixture(self) -> None:
        expected_json = json.loads((REPO_ROOT / "tests/fixtures/expected_fit.json").read_text())
        expected_png = (REPO_ROOT / "tests/fixtures/expected_fit.png").read_bytes()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "fit.json"
            _run_cli(
                [
                    "python",
                    "scripts/fit_from_csv.py",
                    "--config",
                    "tests/fixtures/fit_config.yaml",
                    "--in",
                    "tests/fixtures/fit_input.csv",
                    "--output",
                    str(output_json),
                ]
            )
            data = json.loads(output_json.read_text())
            for key, value in expected_json.items():
                self.assertIn(key, data)
                if isinstance(value, float):
                    self.assertAlmostEqual(value, data[key], places=6)
                else:
                    self.assertEqual(value, data[key])

            output_png = output_json.with_suffix(".png")
            self.assertTrue(output_png.exists())
            self.assertEqual(output_png.read_bytes(), expected_png)


if __name__ == "__main__":
    unittest.main()
