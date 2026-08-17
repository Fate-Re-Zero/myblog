# -*- coding: utf-8 -*-
"""Wrap Agent运行时设计.png into pixel-perfect SVG (embedded + reference)."""
from __future__ import annotations

import base64
import os

PNG = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.png"
OUT_EMBED = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计.svg"
OUT_REF = r"e:\博客\myblog\myblog\source\images\Agent\Agent运行时设计-引用.svg"
W, H = 865, 1025


def main() -> None:
    raw = open(PNG, "rb").read()
    print("png_bytes", len(raw))

    b64 = base64.b64encode(raw).decode("ascii")
    svg_embed = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Agent 运行时设计</title>
  <image width="{W}" height="{H}" href="data:image/png;base64,{b64}"/>
</svg>
"""
    with open(OUT_EMBED, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg_embed)
    print("embedded", OUT_EMBED, "bytes", os.path.getsize(OUT_EMBED))

    svg_ref = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Agent 运行时设计</title>
  <!-- 与同目录 PNG 1:1；修改画面请替换 Agent运行时设计.png 后重新生成嵌入版 -->
  <image width="{W}" height="{H}" href="Agent运行时设计.png" xlink:href="Agent运行时设计.png"/>
</svg>
"""
    with open(OUT_REF, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg_ref)
    print("ref", OUT_REF)


if __name__ == "__main__":
    main()
