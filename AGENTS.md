# Repository Guidelines

## Project Structure & Module Organization
The Python package vive en `src/ofc_model/` y se divide por responsabilidad: `physics.py` resuelve el modelo analítico, `airflow.py` calcula caudales, `simulate.py` expone `run_simulation`, `fitting.py` ajusta la curva exponencial y `workflows.py` combina fitting + bootstrap. `report.py`/`plotting.py` generan CSV/JSON/PNG (y `.parquet` cuando hay `pyarrow|fastparquet`). Datos crudos residen en `data/raw/`, derivados en `data/processed/`. Configs reproducibles van en `configs/` (usa `configs/examples/` para copiar patrones) y consideran el supuesto físico actual: `Ac = Ain` para cámaras apoyadas en el agua, `Aout` puede reducirse (p.ej. tubería ½''). Las simulaciones aceptan `simulation.noise_ppm_std` para introducir error aleatorio en la medición. Notebooks guiados están en `notebooks/`, y los scripts CLI (`simulate_case.py`, `fit_from_csv.py`) sólo delegan en las APIs internas. Cada módulo tiene su espejo en `tests/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: entorno aislado.
- `pip install -r requirements.txt && pip install notebook nbconvert`: dependencias + tooling de notebooks.
- `export PYTHONPATH=$PWD/src` (o `pip install -e .`) para que `ofc_model` sea importable.
- `PYTHONPATH=src python scripts/simulate_case.py --config configs/examples/bench_small.yaml`: simulación de referencia (produce CSV + PNG y opcionalmente Parquet).
- `PYTHONPATH=src python scripts/fit_from_csv.py --config configs/default.yaml --in data/raw/demo_CO2.csv`: ajuste con bootstrap = reportes JSON/PNG.
- `pytest`: corre la suite; `python -m unittest tests.test_scripts` revisa los CLI contra fixtures.

## Coding Style & Naming Conventions
Use Black-compatible formatting (PEP 8, 4-space indents) y agrega type hints en todas las APIs. Las configs siguen `bench_<descriptor>.yaml`; documenta nuevas claves en `README_FULL.md`. Mantén los notebooks con una celda inicial que inserte `../src` en `sys.path` cuando añadas cuadernos nuevos.

## Testing Guidelines
Cada feature debe traer su prueba en `tests/` (o ampliar `tests/test_scripts.py` si afecta a los CLI). Asegura cobertura para reportes (`io.write_timeseries_parquet`, `save_fit`) mockeando el filesystem cuando sea posible. Usa fixtures dentro de `tests/fixtures/` para validar artefactos binarios (CSV/PNG) y mantenlos regenerados mediante los scripts oficiales.

## Commit & Pull Request Guidelines
Follow Conventional Commits (`feat:`, `fix:`, `docs:`) and mention the impacted module or script in the subject. Keep bodies concise, listing data/config files touched. PRs need: summary of intent, sample command output (pytest snippet or script run), links to issues, and screenshots of plots/report excerpts when relevant. Flag any config or data migrations and state rollback steps.

## Configuration & Data Safety
Evita versionar datasets pesados; limita `data/raw/` a archivos <50 MB y prefiere CSV. El `.parquet` que generan los scripts sólo se crea si hay motor instalado, así que no subas binarios redundantes. Variables sensibles deben inyectarse vía `${ENV_VAR}` en las YAML. Cualquier nuevo flag en `camera`, `inflow` o `fitting` debe describirse en `README_FULL.md` y en un ejemplo dentro de `configs/examples/`.
