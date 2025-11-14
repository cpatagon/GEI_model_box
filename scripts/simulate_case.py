"""Script utilitario para simular una cámara de flujo abierta."""
from __future__ import annotations

import argparse
from pathlib import Path

from ofc_model.io import ensure_directory, load_yaml
from ofc_model.report import save_simulation
from ofc_model.simulate import run_simulation


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simula la concentración en una cámara OFC")
    parser.add_argument("--config", required=True, help="Ruta al YAML de configuración")
    parser.add_argument("--duration", type=float, default=None, help="Sobrescribe la duración en segundos")
    parser.add_argument("--output", default=None, help="Ruta de salida opcional")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = load_yaml(args.config)
    result = run_simulation(config, duration_override=args.duration)
    output_dir = ensure_directory(config.get("output", {}).get("folder", "data/processed"))
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = output_dir / f"simulation_{result.scenario_label}.csv"

    csv_path, parquet_path, plot_path = save_simulation(result, output_path)
    parquet_msg = f" | Parquet: {parquet_path}" if parquet_path else ""
    print(f"Simulación completada. CSV: {csv_path}{parquet_msg} | Plot: {plot_path}")


if __name__ == "__main__":
    main()
