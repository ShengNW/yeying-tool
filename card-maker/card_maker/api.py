from pathlib import Path
import json
import yaml

from .core.validate import normalize_params
from .core.layout_engine import render_card
from .core.export import save_image

PKG_DIR = Path(__file__).resolve().parent
THEMES_DIR = PKG_DIR / "themes"
PRESETS_DIR = PKG_DIR / "presets"

def _load_theme():
    theme_path = THEMES_DIR / "default.json"
    if theme_path.exists():
        with open(theme_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _load_preset(name: str):
    if not name or name == "none":
        return {}
    p = PRESETS_DIR / f"{name}.yaml"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    raise FileNotFoundError(f"Preset not found: {name}")

def _deep_merge(a: dict, b: dict) -> dict:
    """b overrides a"""
    out = dict(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def generate_card(params: dict) -> str:
    """
    Generate a card image. Returns output path string.
    :param params: dict fields like:
        preset, title, brand, bullets(list), bg, accent, width/height, format, out, ...
    """
    theme = _load_theme()
    preset_cfg = _load_preset(params.get("preset", "none"))
    # preset as defaults -> user params override
    merged = _deep_merge(preset_cfg, params)
    normalized = normalize_params(merged, theme)

    im = render_card(normalized, theme)
    out_path = save_image(
        im,
        normalized["out"],
        fmt=normalized["format"],
        max_mb=normalized["max_file_mb"],
        allow_jpeg_fallback=True if normalized["format"].lower() in ("jpg", "jpeg") else False
    )
    return str(out_path)
