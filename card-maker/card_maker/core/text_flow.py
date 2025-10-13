from __future__ import annotations
from typing import List
from PIL import ImageFont, ImageDraw, Image

def _is_cjk(ch: str) -> bool:
    code = ord(ch)
    return (
        0x4E00 <= code <= 0x9FFF or
        0x3400 <= code <= 0x4DBF or
        0x20000 <= code <= 0x2A6DF or
        0x2A700 <= code <= 0x2B73F or
        0x2B740 <= code <= 0x2B81F or
        0x2B820 <= code <= 0x2CEAF or
        0xF900 <= code <= 0xFAFF or
        0x2F800 <= code <= 0x2FA1F
    )

class TextFlow:
    def __init__(self):
        # dummy draw for textlength fallback
        self._dummy = Image.new("RGB", (1,1))
        self._draw = ImageDraw.Draw(self._dummy)

    def text_width(self, font: ImageFont.FreeTypeFont, text: str) -> int:
        try:
            return int(self._draw.textlength(text, font=font))
        except Exception:
            bbox = font.getbbox(text)
            return int(bbox[2] - bbox[0])

    def wrap_text(self, font: ImageFont.FreeTypeFont, text: str, max_width: int) -> List[str]:
        if not text:
            return [""]
        # if contains space, prefer space-based wrapping, otherwise char-based (CJK)
        if any(ch.isspace() for ch in text):
            return self._wrap_by_word(font, text, max_width)
        if any(_is_cjk(ch) for ch in text):
            return self._wrap_by_char(font, text, max_width)
        # fallback to word
        return self._wrap_by_word(font, text, max_width)

    def _wrap_by_char(self, font, text, max_width) -> List[str]:
        line = ""
        lines = []
        for ch in text:
            w = self.text_width(font, line + ch)
            if w <= max_width or not line:
                line += ch
            else:
                lines.append(line)
                line = ch
        if line:
            lines.append(line)
        return lines

    def _wrap_by_word(self, font, text, max_width) -> List[str]:
        words = text.split()
        lines = []
        line = ""
        for w in words:
            cand = (line + " " + w).strip()
            if self.text_width(font, cand) <= max_width or not line:
                line = cand
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines
