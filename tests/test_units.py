"""Pruebas para conversiones de `ofc_model.units`."""
from __future__ import annotations

import math
import unittest

from ofc_model import units


class PpmConversionsTest(unittest.TestCase):
    def test_ppm_mol_fraction_roundtrip(self) -> None:
        mol_fraction = units.ppm_to_mol_fraction(420)
        ppm = units.mol_fraction_to_ppm(mol_fraction)
        self.assertTrue(math.isclose(ppm, 420))
        with self.assertRaises(ValueError):
            units.ppm_to_mol_fraction(-1)

    def test_ppm_mg_m3_roundtrip(self) -> None:
        ppm = 500.0
        mg_m3 = units.ppm_to_mg_m3(ppm, molar_mass_g_mol=44.01, temperature_K=298.15)
        back = units.mg_m3_to_ppm(mg_m3, molar_mass_g_mol=44.01, temperature_K=298.15)
        self.assertTrue(math.isclose(ppm, back, rel_tol=1e-6))


class ConcentrationMassTest(unittest.TestCase):
    def test_mol_fraction_to_mg_m3(self) -> None:
        mol_fraction = 420 / 1e6
        mg_m3 = units.mol_fraction_to_mg_m3(mol_fraction, molar_mass_g_mol=44.01, temperature_K=298.15)
        back = units.mg_m3_to_mol_fraction(mg_m3, molar_mass_g_mol=44.01, temperature_K=298.15)
        self.assertTrue(math.isclose(mol_fraction, back, rel_tol=1e-6))


class SurfaceFluxConversionsTest(unittest.TestCase):
    def test_mg_m2_h_to_mmol_m2_h(self) -> None:
        value = units.mg_m2_h_to_mmol_m2_h(100.0, molar_mass_g_mol=44.01)
        back = units.mmol_m2_h_to_mg_m2_h(value, molar_mass_g_mol=44.01)
        self.assertTrue(math.isclose(back, 100.0))


if __name__ == "__main__":
    unittest.main()
