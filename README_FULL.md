# 🧪 Modelo de Caja Abierta (Open Flux Chamber – OFC)

Este proyecto implementa un **modelo físico-matemático** para estimar **flujos de gases (CO₂, CH₄, etc.)** desde el agua hacia la atmósfera utilizando una **cámara de flujo abierta (OFC)**.  
El sistema permite **simular, ajustar y analizar** datos experimentales de concentración dentro de la cámara, y calcular el flujo superficial emitido.

---

## 🎯 Objetivos del modelo

- Simular y estimar el **flujo de emisión superficial** desde una cámara OFC.
- Permitir ajustar parámetros físicos:
  - Volumen de la cámara (Vc)
  - Área cubierta por la cámara (Ac)
  - Áreas de entrada/salida de aire (Ain, Aout)
  - Caudales de aire (QG)
- Aceptar **flujos reales** provenientes de estanques o reactores aireados.
- Generar reportes, gráficos y archivos exportables (CSV, Parquet).
- Diseño modular, mantenible y validable con tests.

---

## 📁 Estructura del proyecto

```
ofc-model/
├─ pyproject.toml / requirements.txt
├─ README.md
├─ data/
│  ├─ raw/
│  └─ processed/
├─ configs/
│  ├─ default.yaml
│  └─ examples/
│     ├─ bench_small.yaml
│     └─ bench_large.yaml
├─ notebooks/
│  ├─ 00_quickstart.ipynb
│  └─ 01_fit_from_timeseries.ipynb
├─ src/
│  └─ ofc_model/
│     ├─ __init__.py
│     ├─ io.py
│     ├─ physics.py
│     ├─ simulate.py
│     ├─ fitting.py
│     ├─ airflow.py
│     ├─ units.py
│     ├─ plotting.py
│     └─ report.py
├─ tests/
│  ├─ test_physics.py
│  ├─ test_fitting.py
│  └─ test_airflow.py
└─ scripts/
   ├─ simulate_case.py
   └─ fit_from_csv.py
```

---

## 🧪 Ecuaciones implementadas

### 1. Modelo de caja abierta general

\[
V rac{dC}{dt} = Q_{in} C_{in} - Q_{out} C + S - kVC
\]

Asumiendo \(Q_{in}=Q_{out}=Q\):

\[
rac{dC}{dt} = rac{Q}{V}(C_{in} - C) + rac{S}{V} - kC
\]

---

### 2. Modelo OFC (Open Flux Chamber)

Transitorio ajustado dentro del cabezal de la cámara:

\[
C(t) = C_G - (C_G - C_0)e^{-t/	heta_G}
\]

donde:

- \(C_G\): concentración de equilibrio en cámara  
- \(	heta_G = rac{V_C}{Q_G}\): tiempo característico del gas dentro de la cámara  

Flujo superficial:

\[
F = rac{V_C}{	heta_G} rac{(C_G - C_A)}{A_C}
\]

---

## ⚙️ Módulos implementados

### `physics.py`
- Solución analítica del modelo.
- Cálculo de flujo desde parámetros ajustados.
- El área de captura `Ac` se asume igual a la sección de entrada `Ain` cuando la cámara descansa directamente sobre la lámina de agua; todo el gas capturado sale por `Aout`.

### `simulate.py`
- API de alto nivel `run_simulation` utilizada por scripts y notebooks.
- Retorna series de tiempo + metadatos para construir reportes consistentes.

### `airflow.py`
Modelos de caudal:
- `Q = A * v`
- Orificio: `Q = Cd * A * sqrt(2ΔP/ρ)`
- Series temporales reales desde CSV.

### `fitting.py`
- Ajuste del exponencial \(C(t)\).
- Estimación de:
  - θ_G
  - C_G
  - F
- Intervalos de confianza y métricas:
  - RMSE
  - R²
  - nt = SD/RMSE - 1

### `workflows.py`
- Encapsula el ajuste completo (`run_fit_workflow`).
- Aplica ventanas temporales (`min_window_s`, `max_window_s`) y bootstrap opcional.
- Devuelve flujos y bandas de confianza 95 % para C_G, θ y F.

### `units.py`
- Conversiones:
  - ppm ↔ mol fracción ↔ mg/m³
  - mg m⁻² h⁻¹ ↔ mmol m⁻² h⁻¹

### `plotting.py`
- Gráficos de ajuste y curvas simuladas (renderizados sin dependencias GUI).

### `report.py`
- Exportación en CSV (si hay motor parquet disponible también genera `.parquet`).
- JSON con métricas + intervalos de confianza.
- Generación de PNG para simulaciones y ajustes.

---

## 📝 Ejemplo de configuración YAML

```yaml
gas: CO2
T_K: 298.15
P_Pa: 101325

camera:
  Vc_m3: 0.1
  Ac_m2: 0.01   # huella = sección de entrada (cubo 0.1 m de lado)
  Ain_m2: 0.01
  Aout_m2: 0.000127  # tubería de 1/2" (~1.27e-4 m²)

simulation:
  target_cg_ppm: 470
  noise_ppm_std: 1.5
  noise_seed: 2024

fitting:
  use_bootstrap: true
  n_bootstrap: 200
  min_window_s: 10
  max_window_s: 180

ambient:
  CA_ppm: 420

inflow:
  mode: "timeseries"   # "timeseries", "area_velocity", "orifice"
  file: "data/raw/qg_series.csv"
  area_m2: null
  velocity_ms: null
  Cd: null
  dP_Pa: null
  rho_air: 1.2

output:
  folder: "data/processed/"
```

---

## 📊 Uso mediante scripts

### Simulación
```bash
PYTHONPATH=src python scripts/simulate_case.py --config configs/examples/bench_small.yaml
```
Guarda `simulation_<escenario>.csv` + PNG y, si existe `pyarrow`/`fastparquet`, también un `.parquet`.

### Ajuste de datos reales
```bash
PYTHONPATH=src python scripts/fit_from_csv.py --config configs/default.yaml --in data/raw/demo_CO2.csv
```
Emite métricas en consola y persiste un JSON con los intervalos bootstrap.

> Nota: `PYTHONPATH=src` asegura que Python encuentre el paquete `ofc_model`. Alternativamente activá un entorno e instala el paquete editable (`pip install -e .`).

### Notebooks
Ambos cuadernos (`notebooks/00_quickstart.ipynb`, `notebooks/01_fit_from_timeseries.ipynb`) incluyen una celda inicial que agrega `../src` al `sys.path`. Si ejecutás `nbconvert` señalá el mismo `PYTHONPATH` que en los scripts:

```bash
export PYTHONPATH=$PWD/src
jupyter nbconvert --to notebook --execute notebooks/00_quickstart.ipynb --output notebooks/00_quickstart_executed.ipynb
```

---

## Dataset de ejemplo

`data/raw/demo_CO2.csv`:

```
time_s,C_ppm
0,420
1,435
2,460
...
```

---

## 🧪 Tests

Ejecutar:

```bash
pytest tests/
```

Incluyen:
- Comparación solución analítica vs numérica
- Verificación de fitting con datos sintéticos
- Chequeo de unidades y conversiones

---

## 💻 Requisitos

- Python 3.10+
- numpy  
- scipy  
- pandas  
- matplotlib  
- pyyaml  
- pydantic  
- pytest  

---

## 📘 Licencia

MIT License © 2025 — Luis Gómez

---

## 📚 Referencias clave

Basado en el método de cámara abierta descrito en:  
**Morales-Rico et al. (2024)** — *Journal of Water and Climate Change*, 15(5), 2127–2140.
