from __future__ import annotations
from io import BytesIO
from pathlib import Path
from PIL import Image

def _ensure_ratio(width: int, height: int):
    # enforce 16:9
    if abs(width*9 - height*16) != 0:
        # silently adjust height to match width
        height = int(round(width * 9 / 16))
    return width, height

def save_image(img: Image.Image, out_path: str, fmt: str = "png", max_mb: float = 5.0, allow_jpeg_fallback: bool = False) -> Path:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = fmt.lower()
    if fmt == "jpeg": fmt = "jpg"

    # try save with iterative compression
    max_bytes = int(max_mb * 1024 * 1024)
    attempt_img = img.convert("RGB") if fmt in ("jpg","jpeg") else img
    quality = 92
    scale = 1.0

    while True:
        bio = BytesIO()
        save_kwargs = {}
        if fmt in ("jpg","jpeg"):
            save_kwargs.update({"quality": quality, "optimize": True, "progressive": True})
        else:
            save_kwargs.update({"optimize": True, "compress_level": 6})
        tmp = attempt_img
        if scale < 1.0:
            w,h = attempt_img.size
            tmp = attempt_img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        tmp.save(bio, format="JPEG" if fmt in ("jpg","jpeg") else "PNG", **save_kwargs)
        size = bio.tell()
        if size <= max_bytes or (quality <= 70 and scale <= 0.7):
            # write to disk
            with open(path, "wb") as f:
                f.write(bio.getbuffer())
            break
        # else iterate
        if fmt in ("jpg","jpeg") and quality > 70:
            quality -= 5
        else:
            scale *= 0.95  # gentle downscale
    return path
