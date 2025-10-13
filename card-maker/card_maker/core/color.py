from __future__ import annotations
from typing import Tuple

def clamp(x, a=0, b=255):
    return max(a, min(b, x))

def hex_to_rgb(s: str) -> Tuple[int, int, int]:
    if not s:
        return (240, 240, 240)
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join([c*2 for c in s])
    if len(s) != 6:
        return (240, 240, 240)
    try:
        return tuple(int(s[i:i+2], 16) for i in (0,2,4))  # type: ignore
    except Exception:
        return (240, 240, 240)

def rgb_to_hex(c: Tuple[int,int,int]) -> str:
    return "#%02x%02x%02x" % tuple(clamp(v) for v in c)

def relative_luminance(rgb: Tuple[int,int,int]) -> float:
    # sRGB to linear
    def srgb_to_linear(v):
        v = v/255.0
        return v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4
    r,g,b = rgb
    R,G,B = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    return 0.2126*R + 0.7152*G + 0.0722*B

def contrast_ratio(c1, c2) -> float:
    L1, L2 = relative_luminance(c1), relative_luminance(c2)
    light, dark = (L1, L2) if L1 >= L2 else (L2, L1)
    return (light + 0.05) / (dark + 0.05)

def pick_text_color(bg: Tuple[int,int,int]) -> Tuple[int,int,int]:
    black = (0,0,0)
    white = (255,255,255)
    return white if contrast_ratio(bg, white) >= contrast_ratio(bg, black) else black

def mix(a, b, t: float) -> Tuple[int,int,int]:
    t = max(0.0, min(1.0, t))
    return (int(a[0]*(1-t)+b[0]*t), int(a[1]*(1-t)+b[1]*t), int(a[2]*(1-t)+b[2]*t))
