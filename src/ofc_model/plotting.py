"""Gráficos livianos generados con Pillow para entornos sin GUI."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

_CANVAS = (800, 500)
_MARGIN = 60
_FONT = ImageFont.load_default()


def _compute_scale(values: Sequence[float]) -> Tuple[float, float]:
    v_min = min(values)
    v_max = max(values)
    if v_min == v_max:
        v_min -= 1.0
        v_max += 1.0
    return v_min, v_max


def _project_series(xs: Sequence[float], ys: Sequence[float], bounds: Tuple[float, float, float, float]):
    x_min, x_max, y_min, y_max = bounds
    width, height = _CANVAS
    coords = []
    for x, y in zip(xs, ys):
        x_norm = (x - x_min) / (x_max - x_min)
        y_norm = (y - y_min) / (y_max - y_min)
        xp = _MARGIN + x_norm * (width - 2 * _MARGIN)
        yp = height - _MARGIN - y_norm * (height - 2 * _MARGIN)
        coords.append((xp, yp))
    return coords


def _init_canvas(title: str | None) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", _CANVAS, color="white")
    draw = ImageDraw.Draw(img)
    if title:
        draw.text((_MARGIN, 15), title, fill="black", font=_FONT)
    width, height = _CANVAS
    draw.line((_MARGIN, _MARGIN, _MARGIN, height - _MARGIN), fill="#444444", width=2)
    draw.line((_MARGIN, height - _MARGIN, width - _MARGIN, height - _MARGIN), fill="#444444", width=2)
    return img, draw


def plot_simulation(time_s: Iterable[float], concentration_ppm: Iterable[float], output_path: str | Path, title: str | None = None) -> Path:
    """Genera PNG con la serie simulada."""

    times = list(map(float, time_s))
    values = list(map(float, concentration_ppm))
    bounds = (*_compute_scale(times), *_compute_scale(values))
    coords = _project_series(times, values, bounds)

    img, draw = _init_canvas(title)
    draw.line(coords, fill="#1f77b4", width=3)
    _draw_ticks(draw, bounds[0], bounds[1], axis="x", label="Tiempo (s)")
    _draw_ticks(draw, bounds[2], bounds[3], axis="y", label="Concentración (ppm)")
    draw.text((_MARGIN + 5, 25), "Simulación", fill="#1f77b4", font=_FONT)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")
    return path


def plot_fit(time_s: Iterable[float], observed_ppm: Iterable[float], fitted_ppm: Iterable[float], output_path: str | Path, title: str | None = None) -> Path:
    """Genera PNG comparando observaciones vs ajuste."""

    times = list(map(float, time_s))
    observed = list(map(float, observed_ppm))
    fitted = list(map(float, fitted_ppm))
    bounds = (*_compute_scale(times), *_compute_scale(observed + fitted))
    obs_coords = _project_series(times, observed, bounds)
    fit_coords = _project_series(times, fitted, bounds)

    img, draw = _init_canvas(title)
    for x, y in obs_coords:
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill="#ff7f0e")
    draw.line(fit_coords, fill="#1f77b4", width=3)
    _draw_ticks(draw, bounds[0], bounds[1], axis="x", label="Tiempo (s)")
    _draw_ticks(draw, bounds[2], bounds[3], axis="y", label="Concentración (ppm)")
    draw.text((_MARGIN + 5, 25), "Observado", fill="#ff7f0e", font=_FONT)
    draw.text((_MARGIN + 120, 25), "Ajuste", fill="#1f77b4", font=_FONT)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")
    return path


def _draw_ticks(draw: ImageDraw.ImageDraw, v_min: float, v_max: float, axis: str, label: str | None = None) -> None:
    width, height = _CANVAS
    num_ticks = 4
    for i in range(num_ticks + 1):
        frac = i / num_ticks
        if axis == "x":
            x = _MARGIN + frac * (width - 2 * _MARGIN)
            draw.line((x, height - _MARGIN, x, height - _MARGIN + 6), fill="#444444")
            value = v_min + frac * (v_max - v_min)
            draw.text((x - 15, height - _MARGIN + 10), f"{value:.0f}", fill="black", font=_FONT)
            if label and i == num_ticks:
                draw.text((width / 2 - 40, height - _MARGIN + 30), label, fill="black", font=_FONT)
        else:
            y = height - _MARGIN - frac * (height - 2 * _MARGIN)
            draw.line((_MARGIN - 6, y, _MARGIN, y), fill="#444444")
            value = v_min + frac * (v_max - v_min)
            draw.text((_MARGIN - 55, y - 5), f"{value:.0f}", fill="black", font=_FONT)
            if label and i == 0:
                draw.text((_MARGIN - 55, _MARGIN - 30), label, fill="black", font=_FONT)
