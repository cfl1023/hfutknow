# -*- coding: utf-8 -*-
"""生成 PWA 图标（192/512）。"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "assets"


def make(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(size * 0.22)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=(166, 58, 46, 255))
    m = size * 0.22
    w = max(2, int(size * 0.055))
    # 三条“列表”线
    for i in range(3):
        y = m + i * size * 0.17
        x2 = size - m - (size * 0.12 if i == 2 else 0)
        d.line([m, y, x2, y], fill=(255, 255, 255, 150), width=w)
    # 放大镜
    cx, cy = size * 0.66, size * 0.66
    rad = size * 0.115
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(255, 255, 255, 255), width=w)
    d.line([cx + rad * 0.72, cy + rad * 0.72, cx + rad * 1.55, cy + rad * 1.55],
           fill=(255, 255, 255, 255), width=w)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for size in (192, 512):
        make(size).save(OUT / f"icon-{size}.png")
    print("icons:", OUT)


if __name__ == "__main__":
    main()
