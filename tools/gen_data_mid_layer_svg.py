# -*- coding: utf-8 -*-
"""彩色数据中台分层架构图 SVG。"""
from __future__ import annotations

OUT = r"e:\博客\myblog\myblog\source\images\Agent\数据中台分层架构图.svg"

W, H = 1100, 780


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    L: list[str] = []

    def A(s: str) -> None:
        L.append(s)

    def rect(x, y, w, h, rx=10, fill="#fff", stroke="#333", sw=1.5):
        A(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def text(x, y, s, size=13, weight=700, fill="#1a1a1a", anchor="middle"):
        fam = "Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
        A(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" '
            f'font-family="{fam}" font-size="{size}" font-weight="{weight}">{esc(s)}</text>'
        )

    layers = [
        {
            "title": "数据应用层",
            "items": ["精准营销", "智能推荐", "风控", "BI", "AI", "运营"],
            "bg": "#fce7f3",
            "bd": "#ec4899",
            "title_c": "#be185d",
            "chip_bd": "#f9a8d4",
        },
        {
            "title": "数据服务层",
            "items": ["API 网关", "数据服务", "标签服务", "指标服务"],
            "bg": "#e0f2fe",
            "bd": "#0ea5e9",
            "title_c": "#0369a1",
            "chip_bd": "#7dd3fc",
        },
        {
            "title": "数据开发层",
            "items": ["ETL", "数据建模", "任务调度", "数据质量", "数据血缘"],
            "bg": "#ecfdf5",
            "bd": "#10b981",
            "title_c": "#047857",
            "chip_bd": "#6ee7b7",
        },
        {
            "title": "数据资产层",
            "items": ["ODS", "DWD", "DWS", "ADS", "数据标准", "元数据"],
            "bg": "#fef3c7",
            "bd": "#f59e0b",
            "title_c": "#b45309",
            "chip_bd": "#fcd34d",
        },
        {
            "title": "数据集成层",
            "items": ["批处理", "流处理", "API", "文件", "消息队列"],
            "bg": "#ede9fe",
            "bd": "#8b5cf6",
            "title_c": "#6d28d9",
            "chip_bd": "#c4b5fd",
        },
        {
            "title": "数据存储层",
            "items": ["数据湖", "数据仓库", "缓存", "搜索引擎", "图数据库"],
            "bg": "#e0e7ff",
            "bd": "#6366f1",
            "title_c": "#4338ca",
            "chip_bd": "#a5b4fc",
        },
    ]

    A('<?xml version="1.0" encoding="UTF-8"?>')
    A(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">'
    )
    A(f'<rect width="{W}" height="{H}" fill="#f8fafc"/>')
    text(W / 2, 40, "数据中台分层架构图", 22, 700, "#0f172a")

    margin_x = 40
    layer_w = W - margin_x * 2
    top = 64
    gap = 12
    layer_h = (H - top - 28 - gap * 5) / 6

    for i, layer in enumerate(layers):
        y = top + i * (layer_h + gap)
        rect(margin_x, y, layer_w, layer_h, 12, layer["bg"], layer["bd"], 2)

        badge_w = 120
        rect(margin_x + 16, y + 16, badge_w, layer_h - 32, 8, layer["bd"])
        text(
            margin_x + 16 + badge_w / 2,
            y + layer_h / 2 + 5,
            layer["title"],
            15,
            700,
            "#ffffff",
        )

        items = layer["items"]
        n = len(items)
        area_x = margin_x + 16 + badge_w + 20
        area_w = layer_w - badge_w - 52
        chip_gap = 12
        chip_w = (area_w - chip_gap * (n - 1)) / n
        chip_h = 48
        chip_y = y + (layer_h - chip_h) / 2
        for j, name in enumerate(items):
            cx = area_x + j * (chip_w + chip_gap)
            rect(cx, chip_y, chip_w, chip_h, 8, "#ffffff", layer["chip_bd"], 1.5)
            text(
                cx + chip_w / 2,
                chip_y + chip_h / 2 + 5,
                name,
                14,
                600,
                layer["title_c"],
            )

    A("</svg>")
    svg = "\n".join(L)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    from xml.etree import ElementTree as ET

    ET.parse(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
