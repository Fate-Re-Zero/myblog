# -*- coding: utf-8 -*-
"""Agent 技术架构图：仿照 展示/通讯/服务/数据 四层 + 左侧箭头标签。"""
from __future__ import annotations

OUT = r"e:\博客\myblog\myblog\source\images\Agent\Agent技术架构图.svg"

W, H = 1180, 920
L: list[str] = []


def A(s: str) -> None:
    L.append(s)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x, y, w, h, rx=8, fill="#fff", stroke="#333", sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    A(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
    )


def text(x, y, s, size=12, weight=600, fill="#1a1a1a", anchor="middle"):
    fam = "Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    A(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" '
        f'font-family="{fam}" font-size="{size}" font-weight="{weight}">{esc(s)}</text>'
    )


def chevron(x, y, w, h, label, fill, stroke):
    """Right-pointing chevron / arrow label on the left."""
    tip = 18
    pts = (
        f"{x},{y} {x+w-tip},{y} {x+w},{y+h/2} "
        f"{x+w-tip},{y+h} {x},{y+h}"
    )
    A(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    text(x + (w - tip) / 2, y + h / 2 + 5, label, 14, 700, "#fff")


def box(x, y, w, h, title, sub=None, fill="#fff", stroke="#64748b"):
    rect(x, y, w, h, 8, fill, stroke, 1.3)
    if sub:
        text(x + w / 2, y + h / 2 - 6, title, 13, 700)
        text(x + w / 2, y + h / 2 + 14, sub, 10, 400, "#64748b")
    else:
        text(x + w / 2, y + h / 2 + 5, title, 13, 700)


def cylinder(cx, cy, title, sub, rw=46, rh=11, body_h=52):
    A(
        f'<path d="M{cx-rw},{cy} L{cx-rw},{cy+body_h} '
        f'A{rw},{rh} 0 0 0 {cx+rw},{cy+body_h} L{cx+rw},{cy} Z" '
        f'fill="#fff" stroke="#334155" stroke-width="1.2"/>'
    )
    A(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rw}" ry="{rh}" '
        f'fill="#fff" stroke="#334155" stroke-width="1.2"/>'
    )
    A(
        f'<ellipse cx="{cx}" cy="{cy+body_h}" rx="{rw}" ry="{rh}" '
        f'fill="none" stroke="#334155" stroke-width="1.2"/>'
    )
    text(cx, cy + body_h * 0.48, title, 12, 700)
    text(cx, cy + body_h * 0.72, sub, 9, 400, "#64748b")


def main() -> None:
    global L
    L = []
    A('<?xml version="1.0" encoding="UTF-8"?>')
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    A(f'<rect width="{W}" height="{H}" fill="#f8fafc"/>')
    text(W / 2, 36, "Agent 技术架构图", 20, 700, "#0f172a")

    # colors per layer
    C1 = ("#3b82f6", "#93c5fd", "#dbeafe")  # fill chevron, stroke, area
    C2 = ("#0d9488", "#5eead4", "#ccfbf1")
    C3 = ("#7c3aed", "#c4b5fd", "#f3e8ff")
    C4 = ("#ea580c", "#fdba74", "#ffedd5")

    LX, LW = 24, 88
    CX = LX + LW + 16
    CW = W - CX - 24

    # ===== 展示层 =====
    y1, h1 = 56, 120
    chevron(LX, y1 + 20, LW, h1 - 40, "展示层", C1[0], C1[0])
    rect(CX, y1, CW, h1, 10, C1[2], C1[1], 1.5, "6 4")
    show = [
        ("Vue / Web", "企业工作台"),
        ("飞书 / 聊天 APP", "IM 入口"),
        ("工单系统", "客服 / On-Call"),
        ("Open API", "Restful / SSE 客户端"),
    ]
    bw = (CW - 40 - 3 * 14) / 4
    for i, (t, s) in enumerate(show):
        box(CX + 20 + i * (bw + 14), y1 + 28, bw, 64, t, s, "#fff", C1[0])

    # ===== 通讯层 =====
    y2, h2 = y1 + h1 + 14, 100
    chevron(LX, y2 + 16, LW, h2 - 32, "通讯层", C2[0], C2[0])
    rect(CX, y2, CW, h2, 10, C2[2], C2[1], 1.5)
    comm = [
        ("ALB / Nginx", "负载均衡"),
        ("HTTP / HTTPS", "同步请求"),
        ("SSE", "流式回写"),
        ("WebSocket", "可选长连接"),
    ]
    cw = (CW - 40 - 3 * 14) / 4
    for i, (t, s) in enumerate(comm):
        box(CX + 20 + i * (cw + 14), y2 + 22, cw, 56, t, s, "#fff", C2[0])

    # ===== 服务层 =====
    y3, h3 = y2 + h2 + 14, 420
    chevron(LX, y3 + 40, LW, h3 - 80, "服务层", C3[0], C3[0])
    rect(CX, y3, CW, h3, 10, C3[2], C3[1], 1.8)

    # gateway
    rect(CX + 200, y3 + 16, 520, 56, 8, "#fff", C3[0], 1.3, "5 4")
    box(CX + 230, y3 + 26, 200, 36, "FastAPI / SSE Gateway", None, "#fff", C3[0])
    box(CX + 460, y3 + 26, 200, 36, "LLM Gateway", None, "#fff", C3[0])

    # left: 监控&保护
    rect(CX + 16, y3 + 86, 170, 200, 8, "#fff", C3[0], 1.2, "5 4")
    text(CX + 101, y3 + 108, "监控 & 保护", 12, 700, C3[0])
    for i, t in enumerate(["链路追踪 Trace", "Worker / 队列监控", "限流 · 熔断 · 重试"]):
        box(CX + 28, y3 + 122 + i * 48, 146, 40, t, None, "#faf5ff", C3[1])

    # center: Agent 业务集群
    rect(CX + 200, y3 + 86, 520, 200, 8, "#fff", C3[0], 1.2, "5 4")
    text(CX + 460, y3 + 108, "Agent 业务集群", 12, 700, C3[0])
    agents = [
        ("Agent Worker", "规划 · 执行"),
        ("意图 / 槽位", "路由技能包"),
        ("Tool / Skill", "工具调用"),
        ("记忆管理", "短/长期上下文"),
    ]
    aw = 230
    for i, (t, s) in enumerate(agents):
        r, c = divmod(i, 2)
        box(CX + 220 + c * (aw + 16), y3 + 124 + r * 70, aw, 56, t, s, "#faf5ff", C3[0])

    # right: 治理&配置
    rect(CX + 736, y3 + 86, 170, 200, 8, "#fff", C3[0], 1.2, "5 4")
    text(CX + 821, y3 + 108, "治理 & 配置", 12, 700, C3[0])
    for i, t in enumerate(["注册中心 Worker/Tool", "限流降级 · 幂等", "Prompt / Skill 配置"]):
        box(CX + 748, y3 + 122 + i * 48, 146, 40, t, None, "#faf5ff", C3[1])

    # bottom middleware row
    mids = [
        ("Agent Run Queue", "任务队列"),
        ("Redis / Tair", "会话锁 · 幂等"),
        ("Evaluation Queue", "评测异步"),
        ("模型服务", "DeepSeek / 智谱"),
    ]
    mw = (CW - 40 - 3 * 12) / 4
    for i, (t, s) in enumerate(mids):
        box(CX + 20 + i * (mw + 12), y3 + h3 - 100, mw, 72, t, s, "#fff", C3[0])

    # ===== 数据层 =====
    y4, h4 = y3 + h3 + 14, 140
    chevron(LX, y4 + 30, LW, h4 - 60, "数据层", C4[0], C4[0])
    rect(CX, y4, CW, h4, 10, C4[2], C4[1], 1.5)
    stores = [
        ("PostgreSQL", "主数据 · Checkpoint"),
        ("Redis", "会话缓存"),
        ("向量索引", "RAG 知识"),
        ("Langfuse", "Trace · Score"),
    ]
    for i, (t, s) in enumerate(stores):
        cx = CX + 90 + i * 230
        cylinder(cx, y4 + 28, t, s, rw=48, rh=10, body_h=70)

    A("</svg>")
    svg = "\n".join(L)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    from xml.etree import ElementTree as ET

    ET.parse(OUT)
    assert "Agent Worker".encode("utf-8") in open(OUT, "rb").read()
    print("saved", OUT)


if __name__ == "__main__":
    main()
