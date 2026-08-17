# -*- coding: utf-8 -*-
"""Agent 应用架构图：参考微服务分层色块布局，内容为 Agent 技术栈。"""
from __future__ import annotations

OUT = r"e:\博客\myblog\myblog\source\images\Agent\Agent应用架构图.svg"

# palette from reference
PINK = "#f8cecc"
PINK_BORDER = "#b85450"
GREEN_SIDE = "#d5e8d4"
GREEN_SIDE_BORDER = "#82b366"
ORANGE = "#ffe6cc"
ORANGE_BORDER = "#d79b00"
MINT = "#d5e8d4"
MINT_BORDER = "#82b366"
BRIGHT_GREEN = "#82b366"
BRIGHT_GREEN_BORDER = "#507e32"
BLUE = "#dae8fc"
BLUE_BORDER = "#6c8ebf"
PURPLE = "#e1d5e7"
PURPLE_BORDER = "#9673a6"
WHITE = "#ffffff"
INK = "#1a1a1a"
GRID = "#ececec"

W, H = 1100, 780
L: list[str] = []


def A(s: str) -> None:
    L.append(s)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x, y, w, h, rx=6, fill=WHITE, stroke="#333333", sw=1.2):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def text(x, y, s, size=13, weight=600, fill=INK, anchor="middle", family=None):
    fam = family or "Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" '
        f'font-family="{fam}" font-size="{size}" font-weight="{weight}">{esc(s)}</text>'
    )


def cylinder(cx, cy, rw=48, rh=18, body_h=36):
    """DB cylinder: top ellipse + body. Bottom rim drawn after text by caller if needed."""
    top = cy
    # body first
    A(
        f'<path d="M{cx-rw},{top} L{cx-rw},{top+body_h} '
        f'A{rw},{rh} 0 0 0 {cx+rw},{top+body_h} L{cx+rw},{top} Z" '
        f'fill="{WHITE}" stroke="#333" stroke-width="1.2"/>'
    )
    # top lid
    A(
        f'<ellipse cx="{cx}" cy="{top}" rx="{rw}" ry="{rh}" '
        f'fill="{WHITE}" stroke="#333" stroke-width="1.2"/>'
    )
    # bottom rim (stroke only so text stays visible on body)
    A(
        f'<ellipse cx="{cx}" cy="{top+body_h}" rx="{rw}" ry="{rh}" '
        f'fill="none" stroke="#333" stroke-width="1.2"/>'
    )


def cylinder_with_label(cx, cy, title, subtitle, rw=28, rh=8, body_h=56):
    """Cylinder with labels centered on the body face."""
    cylinder(cx, cy, rw=rw, rh=rh, body_h=body_h)
    # text on cylinder face (after shapes so it paints on top)
    mid_y = cy + body_h * 0.55
    A(text(cx, mid_y - 8, title, 12, 700))
    if subtitle:
        A(text(cx, mid_y + 10, subtitle, 9, 400, "#555555"))


def grid_bg():
    A(f'<rect width="{W}" height="{H}" fill="#fafafa"/>')
    step = 20
    for x in range(0, W + 1, step):
        A(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{GRID}" stroke-width="0.6"/>')
    for y in range(0, H + 1, step):
        A(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{GRID}" stroke-width="0.6"/>')


def white_card(x, y, w, h, title, sub=None):
    A(rect(x, y, w, h, 4, WHITE, "#333333", 1.2))
    if sub:
        A(text(x + w / 2, y + h / 2 - 4, title, 12, 700))
        A(text(x + w / 2, y + h / 2 + 14, sub, 10, 400, "#555555"))
    else:
        A(text(x + w / 2, y + h / 2 + 4, title, 12, 700))


def main() -> None:
    global L
    L = []
    A('<?xml version="1.0" encoding="UTF-8"?>')
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    grid_bg()

    # ---- top apps ----
    apps = ["Vue / 企业用户", "飞书 / 聊天 APP", "工单系统", "Open API"]
    top_y, top_h = 24, 56
    gap = 18
    side_m = 70
    usable = W - side_m * 2
    aw = (usable - gap * 3) / 4
    for i, name in enumerate(apps):
        x = side_m + i * (aw + gap)
        A(rect(x, top_y, aw, top_h, 8, PINK, PINK_BORDER, 1.5))
        A(text(x + aw / 2, top_y + top_h / 2 + 5, name, 13, 700, "#7a2e2a"))

    # layout for middle
    stack_top = 100
    left_w, right_w = 56, 56
    left_x = 24
    right_x = W - 24 - right_w
    stack_x = left_x + left_w + 14
    stack_w = right_x - stack_x - 14
    stack_h = H - stack_top - 24
    layer_gap = 10
    layer_h = (stack_h - layer_gap * 4) / 5

    # sidebars
    A(rect(left_x, stack_top, left_w, stack_h, 10, GREEN_SIDE, GREEN_SIDE_BORDER, 1.5))
    A(
        f'<text x="{left_x + left_w / 2}" y="{stack_top + stack_h / 2}" '
        f'text-anchor="middle" fill="#b85450" font-family="Microsoft YaHei,PingFang SC,sans-serif" '
        f'font-size="16" font-weight="700" '
        f'transform="rotate(-90 {left_x + left_w / 2} {stack_top + stack_h / 2})">配置中心</text>'
    )
    A(text(left_x + left_w / 2, stack_top + stack_h - 28, "Prompt", 9, 400, "#666", "middle"))
    A(text(left_x + left_w / 2, stack_top + stack_h - 14, "Skill", 9, 400, "#666", "middle"))

    A(rect(right_x, stack_top, right_w, stack_h, 10, PINK, PINK_BORDER, 1.5))
    A(
        f'<text x="{right_x + right_w / 2}" y="{stack_top + stack_h / 2}" '
        f'text-anchor="middle" fill="#b85450" font-family="Microsoft YaHei,PingFang SC,sans-serif" '
        f'font-size="16" font-weight="700" '
        f'transform="rotate(-90 {right_x + right_w / 2} {stack_top + stack_h / 2})">注册中心</text>'
    )
    A(text(right_x + right_w / 2, stack_top + stack_h - 28, "Worker", 9, 400, "#666", "middle"))
    A(text(right_x + right_w / 2, stack_top + stack_h - 14, "Tool", 9, 400, "#666", "middle"))

    layers = [
        {
            "title": "网关层",
            "fill": ORANGE,
            "stroke": ORANGE_BORDER,
            "cards": [
                ("ALB / Nginx", "负载均衡"),
                ("FastAPI Gateway", "请求接入"),
                ("SSE Gateway", "流式回写"),
                ("LLM Gateway", "模型路由"),
            ],
        },
        {
            "title": "编排调度层",
            "fill": MINT,
            "stroke": MINT_BORDER,
            "cards": [
                ("Redis / Tair", "限流 · 锁 · 幂等"),
                ("Agent Run Queue", "任务队列"),
                ("Agent Worker", "规划与执行"),
                ("SSE Event Stream", "事件流"),
            ],
        },
        {
            "title": "智能服务层",
            "fill": BRIGHT_GREEN,
            "stroke": BRIGHT_GREEN_BORDER,
            "cards": [
                ("意图理解", "槽位 · 路由"),
                ("DeepSeek", "通用推理"),
                ("智谱通用模型", "业务生成"),
                ("Tool / Skill", "工具调用"),
            ],
        },
        {
            "title": "数据访问层",
            "fill": BLUE,
            "stroke": BLUE_BORDER,
            "cards": [
                ("RAG 检索", "知识召回"),
                ("LangGraph Checkpoint", "状态检查点"),
                ("会话 / 长期记忆", "上下文读写"),
                ("Eval Outbox", "评测投递"),
            ],
        },
        {
            "title": "持久化与观测层",
            "fill": PURPLE,
            "stroke": PURPLE_BORDER,
            "cylinders": [
                ("PostgreSQL", "业务 · Checkpoint"),
                ("Redis / Tair", "会话状态"),
                ("向量索引", "RAG 向量"),
                ("Langfuse", "Trace · Score"),
            ],
        },
    ]

    card_gap = 14
    for li, layer in enumerate(layers):
        y = stack_top + li * (layer_h + layer_gap)
        A(rect(stack_x, y, stack_w, layer_h, 8, layer["fill"], layer["stroke"], 1.5))
        title_fill = layer.get("title_fill", INK)
        A(text(stack_x + stack_w / 2, y + 22, layer["title"], 15, 700, title_fill))

        # yellow cube hint (top-right)
        cx, cy = stack_x + stack_w - 22, y + 16
        A(
            f'<rect x="{cx-8}" y="{cy-8}" width="14" height="14" fill="#f1c40f" '
            f'stroke="#b7950b" stroke-width="1" transform="rotate(15 {cx} {cy})"/>'
        )

        inner_top = y + 36
        inner_h = layer_h - 48
        if "cylinders" in layer:
            items = layer["cylinders"]
            cw = (stack_w - 40 - card_gap * 3) / 4
            for i, (t, s) in enumerate(items):
                x = stack_x + 20 + i * (cw + card_gap)
                mid = x + cw / 2
                cyl_top = inner_top + 4
                cylinder_with_label(
                    mid,
                    cyl_top,
                    t,
                    s,
                    rw=min(38, cw / 2 - 6),
                    rh=9,
                    body_h=58,
                )
        else:
            items = layer["cards"]
            cw = (stack_w - 40 - card_gap * 3) / 4
            for i, (t, s) in enumerate(items):
                x = stack_x + 20 + i * (cw + card_gap)
                white_card(x, inner_top, cw, inner_h, t, s)

    A("</svg>")
    svg = "\n".join(L)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    from xml.etree import ElementTree as ET

    ET.parse(OUT)
    print("saved", OUT, "H=", H, "xml=ok")


if __name__ == "__main__":
    main()
