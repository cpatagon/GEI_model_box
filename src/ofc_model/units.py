"""Conversiones de unidades utilizadas en los reportes."""
from __future__ import annotations

R_IDEAL_GAS = 8.314462618  # J/(mol·K)


def ppm_to_mol_fraction(ppm: float) -> float:
    """Convierte partes por millón a fracción molar."""

    if ppm < 0:
        raise ValueError("ppm no puede ser negativo")
    return ppm / 1e6


def mol_fraction_to_ppm(mol_fraction: float) -> float:
    if mol_fraction < 0:
        raise ValueError("La fracción molar no puede ser negativa")
    return mol_fraction * 1e6


def ppm_to_mg_m3(
    ppm: float,
    molar_mass_g_mol: float,
    temperature_K: float,
    pressure_Pa: float = 101_325.0,
) -> float:
    return mol_fraction_to_mg_m3(
        ppm_to_mol_fraction(ppm), molar_mass_g_mol, temperature_K, pressure_Pa
    )


def mg_m3_to_ppm(
    mg_m3: float,
    molar_mass_g_mol: float,
    temperature_K: float,
    pressure_Pa: float = 101_325.0,
) -> float:
    return mol_fraction_to_ppm(
        mg_m3_to_mol_fraction(mg_m3, molar_mass_g_mol, temperature_K, pressure_Pa)
    )


def mol_fraction_to_mg_m3(
    mol_fraction: float,
    molar_mass_g_mol: float,
    temperature_K: float,
    pressure_Pa: float = 101_325.0,
) -> float:
    _validate_state(molar_mass_g_mol, temperature_K, pressure_Pa)
    mol_concentration = mol_fraction * pressure_Pa / (R_IDEAL_GAS * temperature_K)
    return mol_concentration * molar_mass_g_mol * 1e3  # g/m3 -> mg/m3


def mg_m3_to_mol_fraction(
    mg_m3: float,
    molar_mass_g_mol: float,
    temperature_K: float,
    pressure_Pa: float = 101_325.0,
) -> float:
    _validate_state(molar_mass_g_mol, temperature_K, pressure_Pa)
    mol_concentration = (mg_m3 / 1e3) / molar_mass_g_mol  # mg -> g -> mol
    return mol_concentration * R_IDEAL_GAS * temperature_K / pressure_Pa


def mg_m2_h_to_mmol_m2_h(value_mg_m2_h: float, molar_mass_g_mol: float) -> float:
    if value_mg_m2_h < 0:
        raise ValueError("El flujo no puede ser negativo")
    if molar_mass_g_mol <= 0:
        raise ValueError("La masa molar debe ser positiva")
    mol_per_h = (value_mg_m2_h / 1e3) / molar_mass_g_mol  # mg -> g -> mol
    return mol_per_h * 1e3  # mol -> mmol


def mmol_m2_h_to_mg_m2_h(value_mmol_m2_h: float, molar_mass_g_mol: float) -> float:
    if value_mmol_m2_h < 0:
        raise ValueError("El flujo no puede ser negativo")
    if molar_mass_g_mol <= 0:
        raise ValueError("La masa molar debe ser positiva")
    mol_per_h = value_mmol_m2_h / 1e3
    grams_per_h = mol_per_h * molar_mass_g_mol
    return grams_per_h * 1e3  # g -> mg


def _validate_state(molar_mass_g_mol: float, temperature_K: float, pressure_Pa: float) -> None:
    if molar_mass_g_mol <= 0:
        raise ValueError("La masa molar debe ser positiva")
    if temperature_K <= 0:
        raise ValueError("La temperatura debe ser positiva")
    if pressure_Pa <= 0:
        raise ValueError("La presión debe ser positiva")
