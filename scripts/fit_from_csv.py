"""Script para ajustar datos experimentales de OFC."""
from __future__ import annotations

import argparse
from pathlib import Path

from ofc_model.io import ensure_directory, load_yaml, read_concentration_csv
from ofc_model.report import save_fit
from ofc_model.workflows import run_fit_workflow


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ajusta mediciones de concentración en una cámara OFC")
    parser.add_argument("--config", required=True, help="Ruta al YAML de configuración")
    parser.add_argument("--in", dest="input_csv", required=True, help="CSV con columnas time_s,C_ppm")
    parser.add_argument("--output", help="Ruta del archivo JSON de salida")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = load_yaml(args.config)
    time_s, concentration = read_concentration_csv(args.input_csv)

    workflow = run_fit_workflow(config, time_s, concentration)

    output_dir = ensure_directory(config.get("output", {}).get("folder", "data/processed"))
    output_path = Path(args.output) if args.output else output_dir / (Path(args.input_csv).stem + "_fit.json")

    save_path, plot_path, persisted_summary = save_fit(workflow, output_path)
    for key, value in persisted_summary.items():
        print(f"{key}: {value}")

    print(f"Resumen guardado en {save_path} | Plot: {plot_path}")


if __name__ == "__main__":
    main()
