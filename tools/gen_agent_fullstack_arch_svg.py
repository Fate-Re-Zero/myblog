# -*- coding: utf-8 -*-
"""
Agent 全栈技术架构图 — 对齐原图布局与配色
（白底、柔和色块层、ReAct 彩色步骤、三列技能/工具/环境、红标、底流程）
"""
from __future__ import annotations

OUT = r"e:\博客\myblog\myblog\source\images\Agent\Agent全栈技术架构图.svg"

W = 1400
# computed at end-ish; set large then we use fixed layout coords
H = 1980
L: list[str] = []


def A(s: str) -> None:
    L.append(s)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x, y, w, h, rx=12, fill="#fff", stroke="#e2e8f0", sw=1, dash=None, opacity=None):
    extra = ""
    if dash:
        extra += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    A(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'
    )


def text(x, y, s, size=12, weight=600, fill="#1e293b", anchor="middle"):
    fam = "Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    A(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" '
        f'font-family="{fam}" font-size="{size}" font-weight="{weight}">{esc(s)}</text>'
    )


def soft_shadow():
    A(
        '<filter id="sh" x="-8%" y="-8%" width="116%" height="120%">'
        '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#94a3b8" flood-opacity="0.28"/>'
        "</filter>"
    )


def badge(x, y, label, fill="#ef4444"):
    # approximate width by chars
    tw = max(72, 9 * len(label) + 20)
    A(f'<rect x="{x}" y="{y}" width="{tw}" height="22" rx="11" fill="{fill}"/>')
    text(x + tw / 2, y + 15, label, 10, 700, "#fff")


def icon(cx, cy, color, kind="dot"):
    """Simple geometric icons approximating original style."""
    if kind == "dot":
        A(f'<circle cx="{cx}" cy="{cy}" r="14" fill="{color}" opacity="0.15"/>')
        A(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{color}"/>')
    elif kind == "brain":
        A(f'<circle cx="{cx}" cy="{cy}" r="16" fill="{color}" opacity="0.2"/>')
        A(f'<circle cx="{cx-5}" cy="{cy-2}" r="7" fill="{color}" opacity="0.85"/>')
        A(f'<circle cx="{cx+5}" cy="{cy-2}" r="7" fill="{color}" opacity="0.85"/>')
        A(f'<circle cx="{cx}" cy="{cy+6}" r="6" fill="{color}" opacity="0.85"/>')
    elif kind == "eye":
        A(f'<ellipse cx="{cx}" cy="{cy}" rx="14" ry="9" fill="{color}" opacity="0.2"/>')
        A(f'<ellipse cx="{cx}" cy="{cy}" rx="10" ry="6" fill="none" stroke="{color}" stroke-width="2"/>')
        A(f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{color}"/>')
    elif kind == "user":
        A(f'<circle cx="{cx}" cy="{cy-5}" r="7" fill="{color}"/>')
        A(f'<path d="M{cx-12},{cy+14} Q{cx},{cy+2} {cx+12},{cy+14}" fill="{color}"/>')


def white_card(x, y, w, h, title, en="", sub="", icon_color="#3b82f6", icon_kind="dot"):
    A(f'<g filter="url(#sh)">')
    rect(x, y, w, h, 14, "#ffffff", "#e2e8f0", 1)
    A("</g>")
    icon(x + w / 2, y + 22, icon_color, icon_kind)
    text(x + w / 2, y + 48, title, 13, 700, "#0f172a")
    if en:
        text(x + w / 2, y + 66, en, 10, 500, "#64748b")
    if sub:
        text(x + w / 2, y + (84 if en else 66), sub, 9, 400, "#94a3b8")


def main() -> None:
    global L
    L = []
    A('<?xml version="1.0" encoding="UTF-8"?>')
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    A("<defs>")
    soft_shadow()
    A(
        '<marker id="arr" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">'
        '<path d="M0,0 L8,3 L0,6 Z" fill="#3b82f6"/></marker>'
    )
    A("</defs>")

    # page — 原图偏白
    A(f'<rect width="{W}" height="{H}" fill="#f8fafc"/>')

    mx = 28
    cw = W - 56

    # ========== Layer 1: 输入理解层 — 浅蓝 ==========
    y = 24
    h1 = 168
    rect(mx, y, cw, h1, 16, "#e8f3ff", "#bfdbfe", 1.5)
    text(mx + 20, y + 32, "输入理解层（感知层）", 16, 700, "#1e40af", "start")
    text(mx + 220, y + 32, "Perception Layer", 12, 500, "#60a5fa", "start")

    # user
    A('<g filter="url(#sh)">')
    rect(mx + 18, y + 52, 118, 96, 14, "#fff", "#93c5fd", 1.2)
    A("</g>")
    icon(mx + 77, y + 78, "#2563eb", "user")
    text(mx + 77, y + 112, "企业用户", 13, 700)
    text(mx + 77, y + 130, "员工/客户/设备/文件", 9, 400, "#64748b")
    A(
        f'<line x1="{mx+136}" y1="{y+100}" x2="{mx+162}" y2="{y+100}" '
        f'stroke="#3b82f6" stroke-width="2.5" marker-end="url(#arr)"/>'
    )

    percep = [
        ("意图识别", "Intent", "#3b82f6"),
        ("信息抽取", "Entity", "#0ea5e9"),
        ("上下文理解", "Context", "#06b6d4"),
        ("图像识别", "Vision / OCR", "#8b5cf6"),
        ("历史记录", "History", "#6366f1"),
        ("外部事件", "Event", "#f59e0b"),
    ]
    pw = 158
    gap = 12
    start_x = mx + 178
    for i, (t, e, c) in enumerate(percep):
        white_card(start_x + i * (pw + gap), y + 50, pw, 100, t, e, "", c)

    # ========== Layer 2: Core Runtime — 淡紫蓝 ==========
    y = 208
    h2 = 310
    rect(mx, y, cw, h2, 16, "#eef2ff", "#c7d2fe", 1.5)
    text(mx + 20, y + 32, "Agent 核心运行层", 16, 700, "#3730a3", "start")
    text(mx + 190, y + 32, "Core Runtime", 12, 500, "#818cf8", "start")
    text(mx + cw / 2, y + 58, "ReAct 循环（持续迭代，直到任务完成）", 13, 600, "#4f46e5")

    # colorful ReAct steps — 对齐原图配色
    steps = [
        ("1. Observe", "观察", "接收输入，感知状态", "#dbeafe", "#2563eb"),
        ("2. Think", "思考 / 推理", "问题分析，任务分解", "#fef9c3", "#ca8a04"),
        ("3. Plan", "规划", "制定策略，拆解步骤", "#dcfce7", "#16a34a"),
        ("4. Act", "行动", "调用工具，执行操作", "#ffedd5", "#ea580c"),
        ("5. Observe", "观察结果", "收集反馈，环境变化", "#bfdbfe", "#1d4ed8"),
        ("6. Reflect", "反思", "结果评估，调整策略", "#ede9fe", "#7c3aed"),
    ]
    sw = 190
    sg = 14
    sx0 = mx + 36
    for i, (en, zh, sub, bg, fg) in enumerate(steps):
        x = sx0 + i * (sw + sg)
        A('<g filter="url(#sh)">')
        rect(x, y + 78, sw, 118, 14, bg, fg, 1.8)
        A("</g>")
        icon(x + sw / 2, y + 100, fg, "eye" if "Observe" in en else "dot")
        text(x + sw / 2, y + 128, en, 12, 700, fg)
        text(x + sw / 2, y + 150, zh, 15, 700, "#0f172a")
        text(x + sw / 2, y + 172, sub, 10, 400, "#475569")
        if i < 5:
            A(
                f'<line x1="{x+sw+1}" y1="{y+137}" x2="{x+sw+sg-1}" y2="{y+137}" '
                f'stroke="#3b82f6" stroke-width="2.5" marker-end="url(#arr)"/>'
            )

    states = [
        ("任务状态", "State", "#6366f1"),
        ("上下文", "Context", "#8b5cf6"),
        ("记忆管理", "Memory", "#a855f7"),
        ("验证自检", "Verify", "#06b6d4"),
        ("错误处理", "Error", "#f43f5e"),
        ("成本控制", "Cost", "#f59e0b"),
        ("运行日志", "Log", "#64748b"),
    ]
    tw = 160
    for i, (t, e, c) in enumerate(states):
        white_card(mx + 50 + i * (tw + 14), y + 218, tw, 74, t, e, "", c)

    # ========== Layer 3: LLM — 浅粉 ==========
    y = 536
    h3 = 240
    rect(mx, y, cw, h3, 16, "#fdf2f8", "#f9a8d4", 1.5)
    text(mx + 20, y + 32, "智能大脑层", 16, 700, "#9d174d", "start")
    text(mx + 140, y + 32, "LLM Layer", 12, 500, "#f472b6", "start")

    # left
    A('<g filter="url(#sh)">')
    rect(mx + 18, y + 52, 300, 170, 14, "#fff", "#fbcfe8", 1.2)
    A("</g>")
    text(mx + 168, y + 78, "模型管理 Model Router", 13, 700, "#be185d")
    for i, t in enumerate(
        ["模型选择（按任务 / 成本 / 性能）", "多模型协同（主模型 + 辅助模型）", "备用降级 Fallback"]
    ):
        rect(mx + 34, y + 96 + i * 38, 268, 32, 8, "#fce7f3", "#fbcfe8", 1)
        text(mx + 168, y + 117 + i * 38, t, 11, 500, "#9d174d")

    # center
    A('<g filter="url(#sh)">')
    rect(mx + 334, y + 52, 540, 170, 14, "#fff", "#fbcfe8", 1.2)
    A("</g>")
    text(mx + 604, y + 78, "LLM 推理引擎 Reasoning", 13, 700, "#be185d")
    icon(mx + 604, y + 108, "#ec4899", "brain")
    reasons = ["理解（意图）", "推理（逻辑）", "规划（生成计划）", "决策（选工具）", "生成（输出）", "反思（自评）"]
    rw = 78
    for i, t in enumerate(reasons):
        x = mx + 354 + i * (rw + 8)
        rect(x, y + 132, rw, 70, 10, "#fce7f3", "#f9a8d4", 1)
        text(x + rw / 2, y + 162, t[:2], 13, 700, "#9d174d")
        text(x + rw / 2, y + 182, t[2:], 9, 400, "#64748b")

    # right
    A('<g filter="url(#sh)">')
    rect(mx + 890, y + 52, 300, 170, 14, "#fff", "#fbcfe8", 1.2)
    A("</g>")
    text(mx + 1040, y + 78, "提示词工程 Prompt System", 13, 700, "#be185d")
    for i, t in enumerate(
        [
            "系统提示词（System Prompt）",
            "场景模板（Template）",
            "少样本示例（Few-shot）",
            "动态优化（Auto-optimize）",
        ]
    ):
        rect(mx + 906, y + 94 + i * 30, 268, 26, 8, "#fce7f3", "#fbcfe8", 1)
        text(mx + 1040, y + 112 + i * 30, t, 11, 500, "#9d174d")

    # ========== 三列 Skills / Tools / Environment ==========
    y = 796
    h4 = 340
    col = (cw - 24) / 3

    # Skills — 绿
    A('<g filter="url(#sh)">')
    rect(mx, y, col, h4, 16, "#f0fdf4", "#86efac", 2)
    A("</g>")
    text(mx + col / 2, y + 32, "能力技能层 Skills", 15, 700, "#15803d")
    skills = [
        "算料 / 计算技能",
        "质检分析技能",
        "报价生成技能",
        "排程优化技能",
        "报告生成技能",
        "+ 自定义业务技能",
    ]
    for i, s in enumerate(skills):
        A('<g filter="url(#sh)">')
        rect(mx + 18, y + 54 + i * 44, col - 36, 38, 10, "#fff", "#bbf7d0", 1.2)
        A("</g>")
        text(mx + col / 2, y + 78 + i * 44, s, 13, 600, "#166534")

    # Tools — 橙
    tx = mx + col + 12
    A('<g filter="url(#sh)">')
    rect(tx, y, col, h4, 16, "#fff7ed", "#fdba74", 2)
    A("</g>")
    text(tx + 20, y + 32, "工具集成层 Tools", 15, 700, "#c2410c", "start")

    # black gateway bar
    rect(tx + 14, y + 48, col - 28, 40, 8, "#0f172a", "#0f172a", 0)
    text(tx + col / 2, y + 66, "工具网关 Tool Gateway", 12, 700, "#fff")
    text(tx + col / 2, y + 82, "统一入口 · 鉴权 · 限流 · 日志 · 重试", 9, 400, "#94a3b8")

    tw = (col - 40) / 3
    tool_cols = [
        ("MCP 协议工具", ["ERP 系统接口", "MES 系统接口", "数据库 MCP", "文件系统 MCP"]),
        ("函数调用", ["Function Call", "内置计算函数", "自定义函数", "业务 API"]),
        ("其他集成", ["IoT 设备", "第三方平台", "WebSocket", "HTTP API"]),
    ]
    for i, (title, items) in enumerate(tool_cols):
        x = tx + 14 + i * (tw + 6)
        rect(x, y + 100, tw, 148, 10, "#fff", "#fed7aa", 1.2)
        text(x + tw / 2, y + 122, title, 11, 700, "#c2410c")
        for j, it in enumerate(items):
            text(x + tw / 2, y + 148 + j * 24, it, 10, 400, "#78716c")

    rect(tx + 14, y + 262, col - 28, 58, 8, "#0f172a", "#0f172a", 0)
    text(tx + col / 2, y + 284, "执行沙箱 Sandbox", 12, 700, "#fff")
    text(tx + col / 2, y + 304, "本地命令 · Python · 浏览器自动化 · Docker", 9, 400, "#94a3b8")

    # Environment — 蓝
    ex = tx + col + 12
    A('<g filter="url(#sh)">')
    rect(ex, y, col, h4, 16, "#eff6ff", "#93c5fd", 2)
    A("</g>")
    text(ex + col / 2, y + 32, "执行环境 Environment", 15, 700, "#1d4ed8")
    envs = [
        ("文件系统", "读写 · 目录操作"),
        ("终端 Shell", "命令执行"),
        ("数据库", "查询 · 更新"),
        ("网络浏览器", "访问 · 爬虫"),
        ("外部服务", "第三方 API"),
    ]
    for i, (a, b) in enumerate(envs):
        A('<g filter="url(#sh)">')
        rect(ex + 18, y + 56 + i * 52, col - 36, 44, 10, "#fff", "#bfdbfe", 1.2)
        A("</g>")
        text(ex + col / 2, y + 76 + i * 52, a, 13, 700, "#1e40af")
        text(ex + col / 2, y + 94 + i * 52, b, 10, 400, "#64748b")

    # ========== Memory — 浅黄 ==========
    y = 1156
    h5 = 175
    rect(mx, y, cw, h5, 16, "#fefce8", "#fde047", 1.5)
    text(mx + 20, y + 32, "记忆知识层", 16, 700, "#a16207", "start")
    text(mx + 140, y + 32, "Memory Layer", 12, 500, "#eab308", "start")

    mems = [
        ("短期记忆", "Short-term", "对话历史 / 当前上下文", "#3b82f6"),
        ("长期记忆", "Long-term", "用户偏好 / 历史档案", "#8b5cf6"),
        ("向量记忆", "Vector DB", "知识检索 / 语义搜索", "#06b6d4"),
        ("结构化记忆", "Structured", "任务状态 / 配置信息", "#10b981"),
        ("企业知识库", "Knowledge", "工艺文档 / 领域经验", "#f59e0b"),
        ("工作记忆", "Working", "当前任务 / 临时信息", "#ec4899"),
    ]
    mw = 198
    for i, (t, e, s, c) in enumerate(mems):
        white_card(mx + 40 + i * (mw + 12), y + 52, mw, 105, t, e, s, c)

    # ========== Infra — 浅绿灰 ==========
    y = 1350
    h6 = 140
    rect(mx, y, cw, h6, 16, "#f0fdf4", "#bbf7d0", 1.5)
    text(mx + 20, y + 32, "基础设施层", 16, 700, "#166534", "start")
    text(mx + 140, y + 32, "Infrastructure", 12, 500, "#4ade80", "start")

    infras = [
        ("大模型", "API 服务", "#6366f1"),
        ("向量库", "Vector DB", "#06b6d4"),
        ("关系库", "MySQL / PG", "#3b82f6"),
        ("对象存储", "OSS / MinIO", "#8b5cf6"),
        ("缓存", "Redis", "#ef4444"),
        ("消息队列", "Kafka / MQ", "#f59e0b"),
        ("监控告警", "Prometheus", "#10b981"),
        ("日志系统", "ELK / Loki", "#64748b"),
    ]
    iw = 145
    for i, (t, e, c) in enumerate(infras):
        white_card(mx + 42 + i * (iw + 12), y + 48, iw, 76, t, e, "", c)

    # ========== End-to-end ==========
    y = 1512
    h7 = 300
    flow_w = cw - 210
    A('<g filter="url(#sh)">')
    rect(mx, y, flow_w, h7, 16, "#ffffff", "#e2e8f0", 1.5)
    A("</g>")
    text(mx + 20, y + 34, "完整业务流程（端到端）", 16, 700, "#0f172a", "start")
    text(mx + 250, y + 34, "End-to-End", 12, 500, "#94a3b8", "start")

    flow = [
        ("①", "员工", "提需求"),
        ("②", "意图", "理解"),
        ("③", "任务", "规划"),
        ("④", "选择", "工具"),
        ("⑤", "执行", "操作"),
        ("⑥", "获取", "结果"),
        ("⑦", "反思", "优化"),
        ("⑧", "完成", "交付"),
    ]
    for i, (n, a, b) in enumerate(flow):
        x = mx + 70 + i * 130
        A(f'<circle cx="{x}" cy="{y+120}" r="32" fill="#dbeafe" stroke="#3b82f6" stroke-width="2.5"/>')
        text(x, y + 112, n, 13, 700, "#1d4ed8")
        text(x, y + 130, a, 12, 700, "#0f172a")
        text(x, y + 172, b, 12, 500, "#475569")
        if i < 7:
            A(
                f'<line x1="{x+34}" y1="{y+120}" x2="{x+96}" y2="{y+120}" '
                f'stroke="#3b82f6" stroke-width="2.5" marker-end="url(#arr)"/>'
            )

    # dashed loop
    A(
        f'<path d="M{mx+850},{y+165} C{mx+920},{y+230} {mx+200},{y+230} {mx+200},{y+165}" '
        f'fill="none" stroke="#60a5fa" stroke-width="2" stroke-dasharray="7 5" '
        f'marker-end="url(#arr)"/>'
    )
    text(
        mx + flow_w / 2,
        y + 250,
        "循环迭代：根据结果持续优化，直到任务完成（⑦ → ②）",
        13,
        600,
        "#2563eb",
    )

    # 核心特性
    A('<g filter="url(#sh)">')
    rect(mx + flow_w + 14, y, 196, h7, 16, "#f0fdf4", "#86efac", 2)
    A("</g>")
    text(mx + flow_w + 112, y + 36, "核心特性", 15, 700, "#15803d")
    feats = [
        "自主规划与决策",
        "工具灵活调用",
        "持续学习与记忆",
        "反思与自我改进",
        "可扩展与可观测",
        "安全与可控",
    ]
    for i, f in enumerate(feats):
        rect(mx + flow_w + 28, y + 58 + i * 36, 168, 30, 8, "#fff", "#bbf7d0", 1)
        text(mx + flow_w + 112, y + 78 + i * 36, "✓  " + f, 12, 600, "#166534")

    text(W / 2, H - 28, "Agent 全栈技术架构", 11, 400, "#94a3b8")

    A("</svg>")
    svg = "\n".join(L)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    from xml.etree import ElementTree as ET

    ET.parse(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
