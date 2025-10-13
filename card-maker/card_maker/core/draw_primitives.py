from __future__ import annotations
from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFilter
from .color import pick_text_color, mix

def rounded_rect(img: Image.Image, bbox, radius: int, fill, outline=None, width=1):
    draw = ImageDraw.Draw(img)
    try:
        draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)
    except Exception:
        # Fallback simple rectangle
        draw.rectangle(bbox, fill=fill, outline=outline, width=width)

def rounded_rect_with_shadow(base: Image.Image, bbox, radius: int, fill, shadow_color=(0,0,0), shadow_opacity=80, shadow_radius=16, shadow_offset=(0,8)):
    x1,y1,x2,y2 = bbox
    w = int(x2-x1); h = int(y2-y1)
    if w <= 0 or h <= 0:
        return
    # shadow layer
    shadow = Image.new("RGBA", (w, h), (0,0,0,0))
    rounded_rect(shadow, (0,0,w,h), radius, fill=(0,0,0,0), outline=None, width=0)
    # fill alpha mask
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    try:
        d.rounded_rectangle((0,0,w,h), radius=radius, fill=255)
    except Exception:
        d.rectangle((0,0,w,h), fill=255)
    # apply blur to mask -> for soft edge
    blurred = mask.filter(ImageFilter.GaussianBlur(radius=shadow_radius))
    sh = Image.new("RGBA", (w, h), shadow_color + (shadow_opacity,))
    sh.putalpha(blurred)
    # paste shadow
    sx = int(x1 + shadow_offset[0]); sy = int(y1 + shadow_offset[1])
    base.alpha_composite(sh, dest=(sx, sy))
    # card
    card = Image.new("RGBA", (w, h), (0,0,0,0))
    rounded_rect(card, (0,0,w,h), radius, fill=fill)
    base.alpha_composite(card, dest=(int(x1), int(y1)))

def draw_underline(img: Image.Image, center_x: int, y: int, length: int, thickness: int, color, radius=999):
    x1 = int(center_x - length/2)
    x2 = int(center_x + length/2)
    rounded_rect(img, (x1, y, x2, y + thickness), radius=min(radius, thickness//2), fill=color)

def draw_rotated_square(img: Image.Image, center: Tuple[int,int], size: int, color, angle=45):
    x,y = center
    sq = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(sq)
    d.rectangle((0,0,size,size), fill=color)
    rsq = sq.rotate(angle, expand=True)
    img.alpha_composite(rsq, dest=(int(x - rsq.width/2), int(y - rsq.height/2)))

def draw_decorations(img: Image.Image, items: List[dict], accent_color, bg_color):
    fg_light = mix(accent_color, (255,255,255), 0.15)
    fg_dark = mix(accent_color, (0,0,0), 0.15)
    use = fg_light if sum(bg_color)/3 < 128 else fg_dark
    w,h = img.size
    for it in items or []:
        cx = int((it.get("x", 0.1)) * w)
        cy = int((it.get("y", 0.1)) * h)
        size = int((it.get("size", 0.02)) * min(w,h))
        draw_rotated_square(img, (cx,cy), size, use, angle=45)

def draw_bullet_list(img: Image.Image, font, bullets: List[str], area, fill, bullet_color, line_spacing=1.15, bullet_radius_ratio=0.38, text_drawer=None):
    """
    area: (x1,y1,x2,y2)
    """
    draw = ImageDraw.Draw(img)
    x1,y1,x2,y2 = area
    line_h = int(font.getbbox("Hg")[3] - font.getbbox("Hg")[1])
    bullet_r = max(2, int(line_h * bullet_radius_ratio))
    gap = max(8, bullet_r*2)  # between dot and text
    y = y1
    for t in bullets:
        # wrap line by available width
        # approximate: occupy dot + gap
        avail = (x2 - x1) - (bullet_r*2 + gap)
        lines = text_drawer.wrap_text(font, t, avail)
        for i, ln in enumerate(lines):
            if y + line_h > y2:
                return
            if i == 0:
                # dot
                cx = x1 + bullet_r
                cy = y + line_h//2
                draw.ellipse((cx-bullet_r, cy-bullet_r, cx+bullet_r, cy+bullet_r), fill=bullet_color)
                tx = x1 + bullet_r*2 + gap
            else:
                tx = x1 + bullet_r*2 + gap
            draw.text((tx, y), ln, fill=fill, font=font)
            y += int(line_h * line_spacing)
