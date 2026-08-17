# -*- coding: utf-8 -*-
"""Remove only red badge pixels; keep surrounding title text intact."""
from __future__ import annotations

import base64
import os
import shutil

from PIL import Image
from rapidocr_onnxruntime import RapidOCR

SRC = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.png"
BAK = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.bak.png"
OUT_SVG = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.svg"


def is_badge_red(r: int, g: int, b: int) -> bool:
    # red / orange-red pill and icon
    return r > 160 and r > g + 40 and r > b + 40


def cover_red_in_roi(im: Image.Image, roi, bg_xy) -> int:
    x0, y0, x1, y1 = roi
    bg = im.getpixel(bg_xy)
    px = im.load()
    n = 0
    # also cover near-white text on red? Better: flood from red, then fill bounding of red cluster with bg
    red_pts = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if is_badge_red(r, g, b):
                red_pts.append((x, y))
    if not red_pts:
        return 0
    xs = [p[0] for p in red_pts]
    ys = [p[1] for p in red_pts]
    # expand a few px to include white text inside pill
    pad = 3
    bx0, bx1 = max(x0, min(xs) - pad), min(x1 - 1, max(xs) + pad)
    by0, by1 = max(y0, min(ys) - pad), min(y1 - 1, max(ys) + pad)
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            # only paint if close to red cluster (inside pill), avoid eating title
            # use: pixel is red OR (inside bbox of red and not dark text of title)
            r, g, b = px[x, y]
            if is_badge_red(r, g, b):
                px[x, y] = bg
                n += 1
            elif bx0 <= x <= bx1 and by0 <= y <= by1:
                # inside red pill bbox: also cover light pixels (white text on badge)
                # but skip if looks like dark title text (dark gray/black)
                if r > 100 or g > 100 or b > 100:  # not dark title
                    # only if near any red pixel
                    if any(abs(x - rx) <= 6 and abs(y - ry) <= 6 for rx, ry in red_pts[::3]):
                        px[x, y] = bg
                        n += 1
    print("roi", roi, "bbox", (bx0, by0, bx1, by1), "painted", n, "bg", bg)
    return n


def main() -> None:
    shutil.copy2(BAK, SRC)
    im = Image.open(SRC).convert("RGB")

    # ROIs around the three badges (from OCR), bg sampled from layer empty area
    jobs = [
        ((545, 105, 635, 145), (700, 125)),  # 最关键
        ((515, 485, 655, 530), (580, 485)),  # 缺失
        ((535, 700, 680, 745), (700, 720)),  # 得0分
    ]
    for roi, bg_xy in jobs:
        cover_red_in_roi(im, roi, bg_xy)

    # second pass: fill remaining holes inside badge areas with bg using rounded cover
    # only on detected red bbox — already done

    im.save(SRC, "PNG", optimize=True)

    ocr = RapidOCR()
    result, _ = ocr(SRC)
    hits = [t for _, t, _ in result if any(k in t for k in ("最关键", "缺失", "0分", "得0"))]
    print("remaining", hits)

    # check Memory Layer full title
    crop = im.crop((200, 690, 700, 750))
    crop.save(r"e:\博客\myblog\myblog\tools\crop_mem_check.png")
    r2, _ = ocr(r"e:\博客\myblog\myblog\tools\crop_mem_check.png")
    print("mem_title", [t for _, t, _ in r2])

    w, h = im.size
    b64 = base64.b64encode(open(SRC, "rb").read()).decode("ascii")
    with open(OUT_SVG, "w", encoding="utf-8", newline="\n") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">\n'
            "  <title>Agent 运行时设计</title>\n"
            f'  <image width="{w}" height="{h}" href="data:image/png;base64,{b64}"/>\n'
            "</svg>\n"
        )
    print("saved", os.path.getsize(SRC), os.path.getsize(OUT_SVG))


if __name__ == "__main__":
    main()
