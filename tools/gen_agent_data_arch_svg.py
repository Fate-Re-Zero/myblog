# -*- coding: utf-8 -*-
"""Agent 数据架构图：参考数据中台布局（双侧栏 + 中部三层 + 底部服务/应用）。"""
from __future__ import annotations

OUT = r"e:\博客\myblog\myblog\source\images\Agent\Agent数据架构图.svg"

W, H = 1200, 980
L: list[str] = []

# palette close to reference
PURPLE_BG = "#f3e8ff"
PURPLE_BD = "#a78bfa"
PURPLE_TITLE = "#6d28d9"
BLUE_BG = "#e0f2fe"
BLUE_BD = "#38bdf8"
BLUE_TITLE = "#0369a1"
CYAN_BG = "#cffafe"
CYAN_BD = "#22d3ee"
CYAN_TITLE = "#0e7490"
PINK_BG = "#fce7f3"
PINK_BD = "#f9a8d4"
PINK_TITLE = "#be185d"
SIDE_BG = "#f5f3ff"
SIDE_BD = "#c4b5fd"
WHITE = "#ffffff"
INK = "#1f2937"


def A(s: str) -> None:
    L.append(s)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x, y, w, h, rx=8, fill=WHITE, stroke="#333", sw=1.2):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def text(x, y, s, size=12, weight=600, fill=INK, anchor="middle"):
    fam = "Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" '
        f'font-family="{fam}" font-size="{size}" font-weight="{weight}">{esc(s)}</text>'
    )


def pill(x, y, w, h, label, fill=WHITE, stroke="#94a3b8"):
    A(rect(x, y, w, h, 6, fill, stroke, 1))
    A(text(x + w / 2, y + h / 2 + 4, label, 11, 600))


def group_box(x, y, w, h, title, items, bg, bd, title_c):
    """A sub-group with title + 3 item pills."""
    A(rect(x, y, w, h, 8, bg, bd, 1.4))
    A(text(x + w / 2, y + 22, title, 13, 700, title_c))
    iw = w - 24
    ih = 28
    gap = 8
    start = y + 36
    for i, it in enumerate(items):
        pill(x + 12, start + i * (ih + gap), iw, ih, it)


def main() -> None:
    global L
    L = []
    A('<?xml version="1.0" encoding="UTF-8"?>')
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    A(f'<rect width="{W}" height="{H}" fill="#fafafa"/>')

    # title
    A(rect(24, 16, W - 48, 44, 8, CYAN_BG, CYAN_BD, 1.5))
    A(text(W / 2, 44, "Agent 数据架构图", 18, 700, CYAN_TITLE))

    # geometry
    side_w = 110
    left_x = 24
    right_x = W - 24 - side_w
    mid_x = left_x + side_w + 12
    mid_w = right_x - mid_x - 12
    top = 76

    # sidebars span collection+storage+compute
    core_h = 520
    A(rect(left_x, top, side_w, core_h, 10, SIDE_BG, SIDE_BD, 1.5))
    A(text(left_x + side_w / 2, top + 28, "治理与安全", 13, 700, PURPLE_TITLE))
    left_items = [
        ("数据标准", "口径·命名·枚举"),
        ("数据质量", "完整性·一致性"),
        ("数据安全", "脱敏·权限·留存"),
        ("元数据管理", "目录·版本·映射"),
    ]
    lh = (core_h - 50) / 4
    for i, (t, s) in enumerate(left_items):
        y = top + 44 + i * lh
        A(rect(left_x + 10, y, side_w - 20, lh - 12, 8, WHITE, SIDE_BD, 1.2))
        A(text(left_x + side_w / 2, y + (lh - 12) / 2 - 2, t, 12, 700, PURPLE_TITLE))
        A(text(left_x + side_w / 2, y + (lh - 12) / 2 + 16, s, 9, 400, "#64748b"))

    A(rect(right_x, top, side_w, core_h, 10, SIDE_BG, SIDE_BD, 1.5))
    A(text(right_x + side_w / 2, top + 28, "运维与工具", 13, 700, PURPLE_TITLE))
    right_items = [
        ("任务调度", "索引·评测任务"),
        ("运行监控", "队列·Worker·延迟"),
        ("数据血缘", "Trace·工具链路"),
        ("观测平台", "Langfuse·告警"),
    ]
    for i, (t, s) in enumerate(right_items):
        y = top + 44 + i * lh
        A(rect(right_x + 10, y, side_w - 20, lh - 12, 8, WHITE, SIDE_BD, 1.2))
        A(text(right_x + side_w / 2, y + (lh - 12) / 2 - 2, t, 12, 700, PURPLE_TITLE))
        A(text(right_x + side_w / 2, y + (lh - 12) / 2 + 16, s, 9, 400, "#64748b"))

    # ---- 数据采集层 ----
    ly = top
    lh1 = 160
    A(rect(mid_x, ly, mid_w, lh1, 10, PURPLE_BG, PURPLE_BD, 1.5))
    A(text(mid_x + mid_w / 2, ly + 24, "数据采集层", 14, 700, PURPLE_TITLE))
    gw = (mid_w - 48) / 3
    gh = lh1 - 44
    groups1 = [
        ("业务系统同步", ["认证 / 账号 API", "支付 / 商城 API", "风控服务 API"]),
        ("知识与文档采集", ["飞书知识库", "政策 / 规范文档", "社区 UGC"]),
        ("运行与事件采集", ["Agent 运行日志", "SSE / Trace 事件", "Run Queue 消息"]),
    ]
    for i, (title, items) in enumerate(groups1):
        group_box(mid_x + 16 + i * (gw + 8), ly + 36, gw, gh, title, items, WHITE, PURPLE_BD, PURPLE_TITLE)

    # ---- 数据存储层 ----
    ly2 = ly + lh1 + 12
    lh2 = 160
    A(rect(mid_x, ly2, mid_w, lh2, 10, PURPLE_BG, PURPLE_BD, 1.5))
    A(text(mid_x + mid_w / 2, ly2 + 24, "数据存储层", 14, 700, PURPLE_TITLE))
    groups2 = [
        ("业务与状态库", ["PostgreSQL 主数据", "LangGraph Checkpoint", "Eval Outbox"]),
        ("会话与缓存", ["Redis / Tair 会话", "限流·锁·幂等", "短期槽位记忆"]),
        ("知识与向量", ["向量索引 (RAG)", "文档 / 对象存储", "Langfuse 存储"]),
    ]
    for i, (title, items) in enumerate(groups2):
        group_box(mid_x + 16 + i * (gw + 8), ly2 + 36, gw, gh, title, items, WHITE, PURPLE_BD, PURPLE_TITLE)

    # ---- 数据计算层 ----
    ly3 = ly2 + lh2 + 12
    lh3 = 160
    A(rect(mid_x, ly3, mid_w, lh3, 10, BLUE_BG, BLUE_BD, 1.5))
    A(text(mid_x + mid_w / 2, ly3 + 24, "数据计算层", 14, 700, BLUE_TITLE))
    groups3 = [
        ("批处理", ["知识切片 / Embedding", "评测样本离线计算", "主数据对账清洗"]),
        ("流式处理", ["会话事件流", "工具调用实时落库", "告警与异常流"]),
        ("在线查询", ["业务 API 实时查", "RAG 向量检索", "Checkpoint 读写"]),
    ]
    for i, (title, items) in enumerate(groups3):
        group_box(mid_x + 16 + i * (gw + 8), ly3 + 36, gw, gh, title, items, WHITE, BLUE_BD, BLUE_TITLE)

    # ---- 数据服务层 (full width) ----
    sy = top + core_h + 14
    sh = 150
    A(rect(24, sy, W - 48, sh, 10, CYAN_BG, CYAN_BD, 1.5))
    A(text(W / 2, sy + 24, "数据服务层", 14, 700, CYAN_TITLE))
    sw = (W - 48 - 48) / 3
    groups4 = [
        ("查询服务", ["业务事实查询 API", "工具网关读接口", "权限二次校验"]),
        ("智能数据服务", ["RAG 检索服务", "会话 / 长期记忆", "Skill 配置读取"]),
        ("质量与资产", ["Evaluation Outbox", "数据目录 / 映射", "Trace 关联查询"]),
    ]
    for i, (title, items) in enumerate(groups4):
        group_box(40 + i * (sw + 8), sy + 36, sw, sh - 48, title, items, WHITE, CYAN_BD, CYAN_TITLE)

    # ---- 数据应用层 ----
    ay = sy + sh + 12
    ah = 100
    A(rect(24, ay, W - 48, ah, 10, PINK_BG, PINK_BD, 1.5))
    A(text(W / 2, ay + 24, "数据应用层", 14, 700, PINK_TITLE))
    apps = [
        "登录认证 Agent",
        "支付业务 Agent",
        "风控 Agent",
        "知识助手",
        "接入自检",
        "质量评测 / 运营分析",
    ]
    aw = (W - 48 - 28 - 5 * 10) / 6
    for i, name in enumerate(apps):
        x = 38 + i * (aw + 10)
        A(rect(x, ay + 42, aw, 42, 8, WHITE, PINK_BD, 1.2))
        A(text(x + aw / 2, ay + 68, name, 11, 600, PINK_TITLE))

    A("</svg>")
    svg = "\n".join(L)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    from xml.etree import ElementTree as ET

    ET.parse(OUT)
    assert "数据采集层".encode("utf-8") in open(OUT, "rb").read()
    print("saved", OUT)


if __name__ == "__main__":
    main()
