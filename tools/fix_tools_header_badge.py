# -*- coding: utf-8 -*-
"""Remove Tools badge: restore column from bak, solid-fill badge rect, keep top border."""
from __future__ import annotations

import base64
import os

from PIL import Image
from rapidocr_onnxruntime import RapidOCR

SRC = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.png"
BAK = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.bak.png"
OUT_SVG = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.svg"
PREVIEW = r"e:\博客\myblog\myblog\tools\tools_header_preview.png"

TOOLS_ROI = (420, 465, 690, 700)


def is_blackish(p) -> bool:
    return p[0] < 55 and p[1] < 55 and p[2] < 55


def is_badge(p) -> bool:
    r, g, b = p
    if r >= 160 and g <= 130 and b <= 130 and r >= g + 40:
        return True
    if r >= 200 and g >= 150 and b <= 130 and r >= b + 50:
        return True
    return False


def main() -> None:
    bak = Image.open(BAK).convert("RGB")
    cur = Image.open(SRC).convert("RGB")
    cur.paste(bak.crop(TOOLS_ROI), (TOOLS_ROI[0], TOOLS_ROI[1]))

    fill = bak.getpixel((520, 518))
    px = cur.load()
    bp = bak.load()

    xs, ys = [], []
    for y in range(492, 522):
        for x in range(525, 645):
            if is_badge(bp[x, y]):
                xs.append(x)
                ys.append(y)
    # Tight geometric wipe — do not go above y=493 (preserve top border 489-491)
    bx0, bx1 = min(xs) - 3, max(xs) + 4
    by0, by1 = max(min(ys) - 3, 493), max(ys) + 3
    print("wipe rect", bx0, by0, bx1, by1)

    EDGE_Y = 520
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            if is_blackish(px[x, y]):
                continue
            if x >= 638:
                px[x, y] = bp[x, EDGE_Y]
            else:
                px[x, y] = fill

    # Catch any stray badge-colored pixels just outside rect (same band)
    for y in range(493, 522):
        for x in range(520, 650):
            if is_blackish(px[x, y]):
                continue
            if is_badge(px[x, y]):
                px[x, y] = bp[x, EDGE_Y] if x >= 638 else fill

    # Top border must remain identical to bak
    for x in range(420, 660):
        px[x, 489] = bp[x, 489]
        px[x, 490] = bp[x, 490]
        px[x, 491] = bp[x, 491]

    cur.save(SRC, "PNG", optimize=True)
    cur.crop((420, 465, 690, 560)).save(PREVIEW)
    cur.crop((500, 470, 680, 545)).resize((540, 225), Image.NEAREST).save(
        r"e:\博客\myblog\myblog\tools\_zoom.png"
    )

    # quality checks
    n = sum(1 for y in range(485, 525) for x in range(525, 650) if is_badge(px[x, y]))
    diff490 = sum(1 for x in range(430, 645) if px[x, 490] != bp[x, 490])
    fill_arr = []
    for y in range(498, 518):
        for x in range(540, 630):
            fill_arr.append(px[x, y])
    import statistics as st

    rs = [p[0] for p in fill_arr]
    print("badge left", n, "top diff", diff490, "fill mean", (st.mean(rs), st.mean(p[1] for p in fill_arr), st.mean(p[2] for p in fill_arr)), "fill std-ish", st.pstdev(rs))

    ocr = RapidOCR()
    result, _ = ocr(SRC)
    hits = [t for _, t, _ in (result or []) if any(k in t for k in ("缺失", "最关键", "0分"))]
    print("badge hits", hits)

    w, h = cur.size
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
    print("ok", os.path.getsize(SRC))


if __name__ == "__main__":
    main()
