from __future__ import annotations
from typing import Dict
from .color import hex_to_rgb, rgb_to_hex

def normalize_params(p: Dict, theme: Dict) -> Dict:
    out = dict(p or {})
    # size
    width = int(out.get("width") or 1920)
    height = int(out.get("height") or round(width * 9 / 16))
    if width < 480:
        width = 480
        height = int(round(width * 9 / 16))
    if height < 480:
        height = 480
        width = int(round(height * 16 / 9))
    out["width"], out["height"] = width, height

    # essentials
    out["title_align"] = out.get("title_align") or "center"
    out["safe_area_pct"] = float(out.get("safe_area_pct") or 0.06)
    out["format"] = (out.get("format") or "png").lower()
    out["max_file_mb"] = float(out.get("max_file_mb") or 5.0)
    out["texture"] = out.get("texture") or "none"

    # fonts (new defaults)
    out["font_family"] = out.get("font_family") or "NotoSansSC"
    out["cjk_only"] = True if out.get("cjk_only") is None else bool(out["cjk_only"])

    # colors: preset/theme default
    theme_bg = (theme.get("colors") or {}).get("bg_default", "#EFEFEF")
    theme_accent = (theme.get("colors") or {}).get("accent_default", "#F0A020")
    out["bg"] = out.get("bg") or theme_bg
    out["accent"] = out.get("accent") or theme_accent

    # bullets
    bullets = out.get("bullets") or []
    bullets = [str(x).strip() for x in bullets if str(x).strip()]
    if not bullets:
        bullets = ["—"]  # 保证可运行
    out["bullets"] = bullets

    # file
    if not out.get("out"):
        out["out"] = "output/card.png"

    # decorations may be provided by preset; otherwise leave default in layout
    return out
