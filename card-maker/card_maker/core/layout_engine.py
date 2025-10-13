from __future__ import annotations
from typing import Dict, Tuple
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .color import hex_to_rgb, pick_text_color, mix
from .draw_primitives import rounded_rect_with_shadow, draw_underline, draw_decorations, draw_bullet_list
from .text_flow import TextFlow

PKG_DIR = Path(__file__).resolve().parent.parent
FONTS_DIR = PKG_DIR / "assets" / "fonts"
TEXTURES_DIR = PKG_DIR / "assets" / "textures"

def _try_load_font(path: Path, size: int):
    """
    [RAQM_LAYOUT] Prefer RAQM when available for better CJK shaping/kerning.
    """
    try:
        # defer import to keep scope local as requested
        from PIL import features
        use_layout = ImageFont.LAYOUT_RAQM if features.check("raqm") else ImageFont.LAYOUT_BASIC
    except Exception:
        # ultra-defensive fallback
        use_layout = getattr(ImageFont, "LAYOUT_BASIC", 0)

    try:
        return ImageFont.truetype(str(path), size=size, layout_engine=use_layout)
    except Exception:
        return None

def _fallback_font(size: int):
    """
    [CJK_FIRST_FALLBACK] Prefer Chinese system fonts; only then default bitmap.
    """
    # Check RAQM availability here as well
    try:
        from PIL import features
        use_layout = ImageFont.LAYOUT_RAQM if features.check("raqm") else ImageFont.LAYOUT_BASIC
    except Exception:
        use_layout = getattr(ImageFont, "LAYOUT_BASIC", 0)

    cjk_candidates = [
        "msyh.ttc",                 # Microsoft YaHei (Windows)
        "Microsoft YaHei.ttf",      # alt name (some envs)
        "SimHei.ttf",               # 黑体 (Windows)
        str(FONTS_DIR / "NotoSansSC-Regular.ttf"),  # package asset (if present)
    ]
    for name in cjk_candidates:
        try:
            return ImageFont.truetype(name, size=size, layout_engine=use_layout)
        except Exception:
            continue
    return ImageFont.load_default()

def _load_fonts(title_size: int, text_size: int, family: str = "NotoSansSC", force_cjk: bool = True):
    """
    [UNIFY_CJK_FAMILY] Title/Body/Brand use the same CJK family.
    - Title prefers Bold -> Regular
    - Body & Brand use Regular (fallback to Bold if Regular missing)
    - No Inter/DejaVuSans trials
    """
    # Build candidate lists (CJK-only when force_cjk is True)
    bold_candidates = [
        FONTS_DIR / f"{family}-Bold.ttf",
        FONTS_DIR / f"{family}-Medium.ttf",  # optional mid-weight
        FONTS_DIR / f"{family}-Regular.ttf",
    ]
    regular_candidates = [
        FONTS_DIR / f"{family}-Regular.ttf",
        FONTS_DIR / f"{family}-Medium.ttf",
        FONTS_DIR / f"{family}-Bold.ttf",
    ]

    # Optional extra CJK system fallbacks (still CJK)
    if force_cjk:
        regular_sys = [Path("msyh.ttc"), Path("Microsoft YaHei.ttf"), Path("SimHei.ttf")]
        bold_sys = regular_sys  # styles may be embedded; try same files
        bold_candidates += bold_sys
        regular_candidates += regular_sys

    # Title font: Bold -> Regular -> _fallback_font
    title = None
    for pth in bold_candidates:
        title = _try_load_font(pth, title_size)
        if title:
            break
    if not title:
        title = _fallback_font(title_size)

    # Body font: Regular -> Bold -> _fallback_font
    text = None
    for pth in regular_candidates:
        text = _try_load_font(pth, text_size)
        if text:
            break
    if not text:
        text = _fallback_font(text_size)

    # Brand font: same family as body, slightly smaller, no Inter
    brand_size = int(text_size * 0.9)
    brand = None
    for pth in regular_candidates:
        brand = _try_load_font(pth, brand_size)
        if brand:
            break
    if not brand:
        brand = _fallback_font(brand_size)

    # [DEBUG_FONT_LOAD] Optional inspection
    if os.getenv("CARD_MAKER_DEBUG") == "1":
        def _finfo(f):
            name = None
            try:
                name = "/".join([n for n in f.getname() if n])  # (family, style)
            except Exception:
                name = "<?>"
            path = getattr(f, "path", None)
            return f"name={name}, path={path}"
        print(f"[card_maker] title_font: {_finfo(title)}")
        print(f"[card_maker] body_font : {_finfo(text)}")
        print(f"[card_maker] brand_font: {_finfo(brand)}")

    return title, text, brand

def _maybe_texture(bg_img: Image.Image, mode: str):
    if mode == "noise":
        # simple gaussian noise
        import random
        px = bg_img.load()
        w,h = bg_img.size
        for y in range(h):
            for x in range(w):
                r,g,b = px[x,y]
                d = random.randint(-4,4)
                px[x,y] = (max(0,min(255,r+d)), max(0,min(255,g+d)), max(0,min(255,b+d)))
    return bg_img

def render_card(p: Dict, theme: Dict) -> Image.Image:
    w,h = p["width"], p["height"]
    bg = hex_to_rgb(p["bg"])
    accent = hex_to_rgb(p["accent"])
    fg = pick_text_color(bg)

    img = Image.new("RGBA", (w,h), bg + (255,))
    _maybe_texture(img, p.get("texture", "none"))
    draw = ImageDraw.Draw(img)
    flow = TextFlow()

    safe = int(min(w,h) * p["safe_area_pct"])
    content_w = w - safe*2
    content_x = safe

    # brand/top area
    brand_txt = p.get("brand", "").strip()
    brand_h = int(h * 0.08) if brand_txt else 0
    title_top = safe + (brand_h if brand_txt else 0)

    # dynamic title sizing
    # try from max to min percent of canvas height
    title_area_h = int(h * 0.40)
    max_pct = 0.16
    min_pct = 0.08
    target_lines = 2
    best_font = None
    best_lines = None

    for pct in [max_pct - i*0.01 for i in range(int((max_pct-min_pct)/0.01)+1)]:
        fsize = max(12, int(h * pct))
        # [PASS_FAMILY_PARAMS] forward font family & cjk-only flags
        title_font, body_font, brand_font = _load_fonts(
            fsize,
            int(h*0.035),
            family=p.get("font_family", "NotoSansSC"),
            force_cjk=p.get("cjk_only", True),
        )
        # wrap title to at most two lines by width
        avail_w = content_w if p["title_align"] == "center" else int(content_w*0.86)
        lines = flow.wrap_text(title_font, p["title"], avail_w)
        if len(lines) > target_lines:
            continue  # too big, try smaller
        # compute total title height
        line_h = int(title_font.getbbox("Hg")[3] - title_font.getbbox("Hg")[1])
        total_h = int(line_h * (len(lines) + (0.15*(len(lines)-1))))
        if total_h <= title_area_h:
            best_font, best_lines = (title_font, body_font, brand_font), lines
            break
        best_font, best_lines = (title_font, body_font, brand_font), lines  # keep last as fallback

    title_font, body_font, brand_font = best_font
    # brand draw
    if brand_txt:
        brand_y = safe
        draw.text((content_x, brand_y), brand_txt, fill=fg, font=brand_font)

    # title
    line_h = int(title_font.getbbox("Hg")[3] - title_font.getbbox("Hg")[1])
    title_lines = best_lines
    if p["title_align"] == "center":
        y = title_top + int((title_area_h - line_h*len(title_lines)) * 0.35)
        for ln in title_lines:
            tw = flow.text_width(title_font, ln)
            x = int(w/2 - tw/2)
            draw.text((x, y), ln, fill=fg, font=title_font)
            y += int(line_h * 1.15)
        # underline relative to text width or canvas
        underline_len = max(int(min(w*0.28, flow.text_width(title_font, "".join(title_lines))*0.9)), int(w*0.18))
        draw_underline(img, w//2, y + int(h*0.01), underline_len, max(6, int(h*0.008)), accent)
    else:
        # left aligned
        y = title_top
        x0 = content_x
        for ln in title_lines:
            draw.text((x0, y), ln, fill=fg, font=title_font)
            y += int(line_h * 1.15)
        underline_len = max(int(min(w*0.30, flow.text_width(title_font, "".join(title_lines))*0.9)), int(w*0.18))
        draw_underline(img, x0 + underline_len//2, y + int(h*0.01), underline_len, max(6, int(h*0.008)), accent)

    # info card area
    card_h = int(h * 0.25)
    card_w = int(content_w * 0.74)
    card_x = int(w/2 - card_w/2)
    card_y = h - safe - card_h
    card_radius = int(min(w,h) * 0.03)
    card_bg = (255,255,255)
    rounded_rect_with_shadow(img, (card_x, card_y, card_x+card_w, card_y+card_h),
                             radius=card_radius, fill=card_bg, shadow_color=mix(bg, (0,0,0), 0.7),
                             shadow_opacity=90 if sum(bg)/3>128 else 140,
                             shadow_radius=int(min(w,h)*0.02), shadow_offset=(0,int(h*0.01)))

    # bullets inside card
    pad_x = int(card_w * 0.06)
    pad_y = int(card_h * 0.12)
    bullet_area = (card_x + pad_x, card_y + pad_y, card_x + card_w - pad_x, card_y + card_h - pad_y)
    bullet_color = accent
    draw_bullet_list(img, body_font, p["bullets"], bullet_area, fill=(0,0,0), bullet_color=bullet_color, text_drawer=flow)

    # decorations
    deco = p.get("decorations", [
        {"x":0.08, "y":0.82, "size":0.035},
        {"x":0.93, "y":0.18, "size":0.028}
    ])
    draw_decorations(img, deco, accent_color=accent, bg_color=bg)

    # watermark (use same CJK family; no Inter)
    wm = p.get("watermark", "").strip()
    if wm:
        family = p.get("font_family", "NotoSansSC")
        wm_size = int(h*0.025)
        wm_font = (_try_load_font(FONTS_DIR / f"{family}-Regular.ttf", wm_size) or
                   _try_load_font(FONTS_DIR / f"{family}-Bold.ttf", wm_size) or
                   _fallback_font(wm_size))
        tw = flow.text_width(wm_font, wm)
        tx = w - safe - tw
        ty = h - safe - int(h*0.02)
        draw.text((tx, ty), wm, fill=mix(bg,(0,0,0),0.4), font=wm_font)

    return img
