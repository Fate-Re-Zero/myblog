# -*- coding: utf-8 -*-
"""Generate editable industrial AI Agent architecture SVG."""
from __future__ import annotations

OUT = r"e:\博客\myblog\myblog\source\images\Agent\工业AI-Agent企业架构图.svg"

W = 1280
# Layer heights (must match drawing below)
Y0, LH1 = 16, 110
Y2, LH2 = Y0 + LH1 + 12, 280
Y3, LH3 = Y2 + LH2 + 12, 270
Y4, LH4 = Y3 + LH3 + 12, 210
Y5, LH5 = Y4 + LH4 + 12, 140
CONTENT_BOTTOM = Y5 + LH5  # ends at 基础层; no 执行层
H = CONTENT_BOTTOM + 16
L: list[str] = []


def A(s: str) -> None:
    L.append(s)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(
    x,
    y,
    w,
    h,
    rx=8,
    fill=None,
    stroke=None,
    sw=1,
    dash=None,
    opacity=None,
) -> str:
    attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"', f'rx="{rx}"']
    if fill:
        attrs.append(f'fill="{fill}"')
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{sw}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return "<rect " + " ".join(attrs) + "/>"


def text(x, y, s, cls, anchor=None) -> str:
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="{cls}"{a}>{esc(s)}</text>'


def icon(cx, cy, color, r=10) -> None:
    A(f'<circle cx="{cx}" cy="{cy}" r="{r + 5}" fill="{color}" opacity="0.18"/>')
    A(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')


def main() -> None:
    A('<?xml version="1.0" encoding="UTF-8"?>')
    A(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">'
    )
    A("<defs>")
    A('<style type="text/css"><![CDATA[')
    A(
        '.lbl-main{font:700 13px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#fff;}'
    )
    A(
        '.lbl-sub{font:600 11px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#e8f0ff;}'
    )
    A(
        '.h1{font:700 14px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#1a2332;}'
    )
    A(
        '.h2{font:700 12px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#243044;}'
    )
    A(
        '.body{font:11px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#4a5568;}'
    )
    A(
        '.tiny{font:10px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#6b7785;}'
    )
    A(
        '.sec{font:700 13px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#1e3a8a;}'
    )
    A(
        '.flow{font:600 12px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#2563eb;}'
    )
    A(
        '.white{font:600 12px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#fff;}'
    )
    A(
        '.wsm{font:11px "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;fill:#fff;}'
    )
    A("]]></style>")
    A(
        '<marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">'
        '<path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/></marker>'
    )
    A("</defs>")
    A(rect(0, 0, W, H, 0, fill="#f0f3f8"))

    ML, CW = 16, 70
    GX = 96
    SX, SW = 1130, 130
    RW = SX - GX - 16

    # ----- Layer 1: 价值层 -----
    y0, lh1 = Y0, LH1
    A("<!-- 价值层 -->")
    A(rect(8, y0, SX - 16, lh1, 10, fill="#e8f1ff", stroke="#b6c9ef"))
    A(rect(ML, y0 + 12, CW, 86, 8, fill="#1e40af"))
    A(text(ML + 35, y0 + 42, "价值层", "lbl-main", "middle"))
    A(text(ML + 35, y0 + 62, "业务效果", "lbl-sub", "middle"))
    vals = [
        ("降本增效", "人效提升 50%+"),
        ("提高交付", "交期准时率提升"),
        ("质量提升", "任务完成度提高"),
        ("系统稳定", "柔性应对力提升"),
        ("决策智能", "数据驱动决策"),
    ]
    vw = 170
    for i, (t, s) in enumerate(vals):
        x = GX + 20 + i * (vw + 18)
        icon(x + vw / 2, y0 + 32, "#2563eb")
        A(text(x + vw / 2, y0 + 68, t, "h1", "middle"))
        A(text(x + vw / 2, y0 + 88, s, "tiny", "middle"))

    # ----- Sidebar (height aligns with 基础层 bottom) -----
    sy, sh = y0, CONTENT_BOTTOM - y0
    A("<!-- 保障体系 -->")
    A(rect(SX, sy, SW, sh, 10, fill="#dbe7ff", stroke="#9db6e8"))
    A(rect(SX + 8, sy + 10, SW - 16, 36, 6, fill="#1e40af"))
    A(text(SX + SW / 2, sy + 33, "保障体系", "white", "middle"))
    side_items = [
        ("数据安全", ["数据脱敏", "访问控制", "模型自部署"]),
        ("权限管理", ["角色权限", "细粒度控制"]),
        ("运维监控", ["性能监控", "日志审计", "告警管理"]),
        ("持续优化", ["效果评估", "模型优化", "能力迭代"]),
    ]
    si_h = (sh - 60) / 4
    for i, (title, bullets) in enumerate(side_items):
        iy = sy + 60 + i * si_h
        icon(SX + SW / 2, iy + 18, "#2563eb", 8)
        A(text(SX + SW / 2, iy + 48, title, "h2", "middle"))
        for j, b in enumerate(bullets):
            A(text(SX + SW / 2, iy + 66 + j * 16, "· " + b, "tiny", "middle"))

    # ----- Layer 2: 应用层 -----
    y2, lh2 = Y2, LH2
    A("<!-- 应用层 -->")
    A(rect(8, y2, SX - 16, lh2, 10, fill="#eef4ff", stroke="#b6c9ef"))
    A(rect(ML, y2 + 20, CW, 200, 8, fill="#2563eb"))
    A(text(ML + 35, y2 + 100, "应用层", "lbl-main", "middle"))
    A(text(ML + 35, y2 + 120, "智能体阵列", "lbl-sub", "middle"))

    agents = [
        (
            "登录认证 Agent",
            ["认证知识查询", "认证日志分析", "业务问题处理", "持续进化处理问题的能力"],
            "#1d4ed8",
        ),
        (
            "支付业务 Agent",
            ["支付知识查询", "支付日志分析", "订单补单", "退款问题处理"],
            "#0891b2",
        ),
        (
            "部门业务对接 Agent",
            ["部门能力查询", "能力对接指导", "对接异常排查", "持续集成、持续进化"],
            "#7c3aed",
        ),
        (
            "设备运维 Agent",
            ["设备监控", "故障预测", "修复建议", "工单生成"],
            "#ea580c",
        ),
        (
            "质量分析 Agent",
            ["缺陷识别", "原因分析", "质量追溯", "改进建议"],
            "#16a34a",
        ),
    ]
    aw, ah = 150, 168
    for i, (title, bullets, accent) in enumerate(agents):
        x = GX + 8 + i * (aw + 10)
        A(rect(x, y2 + 16, aw, ah, 8, fill="#ffffff", stroke="#d0d7e2"))
        A(rect(x, y2 + 16, aw, 6, 3, fill=accent))
        icon(x + aw / 2, y2 + 40, accent, 7)
        A(text(x + aw / 2, y2 + 68, title, "h2", "middle"))
        for j, b in enumerate(bullets):
            # long lines use smaller class
            cls = "tiny" if len(b) > 10 else "body"
            A(text(x + aw / 2, y2 + 92 + j * 18, "· " + b, cls, "middle"))

    x = GX + 8 + 5 * (aw + 10)
    A(rect(x, y2 + 16, aw, ah, 8, fill="#f7f9fc", stroke="#60a5fa", sw=1.5, dash="5 4"))
    A(text(x + aw / 2, y2 + 50, "更多 Agent", "h2", "middle"))
    for j, b in enumerate(["风控 Agent", "财务 Agent", "前端 Agent", "..."]):
        A(text(x + aw / 2, y2 + 90 + j * 20, b, "body", "middle"))

    fy = y2 + lh2 - 42
    flows = ["自然语言交互", "任务理解与规划", "调用工具与知识", "执行任务与反馈"]
    fw = 200
    for i, f in enumerate(flows):
        fx = GX + 40 + i * (fw + 30)
        A(text(fx, fy + 8, f, "flow", "middle"))
        if i < 3:
            A(
                f'<line x1="{fx + 90}" y1="{fy}" x2="{fx + fw - 70}" y2="{fy}" '
                f'stroke="#3b82f6" stroke-width="2" marker-end="url(#arr)"/>'
            )

    # ----- Layer 3: 能力层 -----
    y3, lh3 = Y3, LH3
    A("<!-- 能力层 -->")
    A(rect(8, y3, SX - 16, lh3, 10, fill="#e8f8ef", stroke="#9ed4b0"))
    A(rect(ML, y3 + 30, CW, 200, 8, fill="#16a34a"))
    A(text(ML + 35, y3 + 100, "能力层", "lbl-main", "middle"))
    A(text(ML + 35, y3 + 120, "AI Agent", "lbl-sub", "middle"))
    A(text(ML + 35, y3 + 138, "核心能力", "lbl-sub", "middle"))
    A(text(GX + RW / 2 - 20, y3 + 28, "AI Agent 核心能力引擎", "sec", "middle"))

    caps = [
        ("意图理解", "理解业务需求", "识别任务目标"),
        ("知识检索", "企业知识库检索", "文档/规则/案例"),
        ("推理决策", "数据分析推理", "生成最优方案"),
        ("工具调用", "调用系统API", "执行操作指令"),
        ("工作流编排", "多步骤任务拆解", "流程自动化执行"),
        ("学习优化", "持续学习反馈", "不断优化能力"),
    ]
    cw, ch = 145, 118
    for i, (t, a, b) in enumerate(caps):
        x = GX + 8 + i * (cw + 12)
        A(rect(x, y3 + 42, cw, ch, 8, fill="#ffffff", stroke="#86efac"))
        icon(x + cw / 2, y3 + 62, "#16a34a", 7)
        A(text(x + cw / 2, y3 + 90, t, "h2", "middle"))
        A(text(x + cw / 2, y3 + 112, a, "tiny", "middle"))
        A(text(x + cw / 2, y3 + 128, b, "tiny", "middle"))

    A(text(GX + 8, y3 + 185, "智能体运行框架", "h2"))
    fws = [
        ("大模型 (LLM)", 140),
        ("RAG知识增强", 130),
        ("Agent框架 (规划/记忆/行动)", 210),
        ("扩展插件 (skill/工具集)", 170),
        ("权限与安全控制", 150),
    ]
    fx = GX + 8
    for f, ww in fws:
        A(rect(fx, y3 + 200, ww, 36, 6, fill="#22c55e"))
        A(text(fx + ww / 2, y3 + 223, f, "wsm", "middle"))
        fx += ww + 10

    # ----- Layer 4: 数据层 -----
    y4, lh4 = Y4, LH4
    A("<!-- 数据层 -->")
    A(rect(8, y4, SX - 16, lh4, 10, fill="#fff4e8", stroke="#f0c28a"))
    A(rect(ML, y4 + 20, CW, 160, 8, fill="#ea580c"))
    A(text(ML + 35, y4 + 80, "数据层", "lbl-main", "middle"))
    A(text(ML + 35, y4 + 100, "企业数据资产", "lbl-sub", "middle"))

    datas = [
        ("认证数据", "游戏 / 下载器 / 官方APP", "登录 / 注册 / 注销 / 实名"),
        ("支付数据", "游戏内充值 / 商城 / 官方APP", "支付 / 退款 / 消耗"),
        ("风控数据", "游戏 / 官方网站 / 官方APP", "登录行为 / 支付行为 / 消耗行为"),
        ("社区数据", "内容数据 / 互动数据 / 行为数据", "发帖 / 评论 / 点赞"),
        ("计费数据", "供应商 / 市场 / 行业", "充值 / 消耗 / 冻结"),
    ]
    dw = 175
    for i, (t, a, b) in enumerate(datas):
        x = GX + 8 + i * (dw + 14)
        A(rect(x, y4 + 16, dw, 110, 8, fill="#ffffff", stroke="#fdba74"))
        icon(x + dw / 2, y4 + 38, "#ea580c", 6)
        A(text(x + dw / 2, y4 + 66, t, "h2", "middle"))
        A(text(x + dw / 2, y4 + 88, a, "tiny", "middle"))
        A(text(x + dw / 2, y4 + 106, b, "tiny", "middle"))

    A(rect(GX + 8, y4 + 140, RW - 40, 40, 8, fill="#f97316"))
    A(
        text(
            GX + RW / 2 - 20,
            y4 + 165,
            "数据治理与集成平台（数据清洗 / 标准化 / 主数据管理 / 数据安全）",
            "white",
            "middle",
        )
    )

    # ----- Layer 5: 基础层 -----
    y5, lh5 = Y5, LH5
    A("<!-- 基础层 -->")
    A(rect(8, y5, SX - 16, lh5, 10, fill="#f3eefc", stroke="#c4b5e0"))
    A(rect(ML, y5 + 20, CW, 100, 8, fill="#7c3aed"))
    A(text(ML + 35, y5 + 58, "基础层", "lbl-main", "middle"))
    A(text(ML + 35, y5 + 78, "技术支撑", "lbl-sub", "middle"))

    bases = [
        ("云计算 / 私有化部署", "弹性计算 / 高可用"),
        ("大模型服务", "通用大模型 / 行业模型"),
        ("向量数据库", "知识向量存储 / 检索"),
        ("中间件 / API网关", "系统集成 / 接口管理"),
        ("安全防护", "安全沙箱 / 权限管理"),
    ]
    bw = 175
    for i, (t, s) in enumerate(bases):
        x = GX + 8 + i * (bw + 14)
        A(rect(x, y5 + 20, bw, 100, 8, fill="#ffffff", stroke="#c4b5fd"))
        icon(x + bw / 2, y5 + 42, "#7c3aed", 6)
        A(text(x + bw / 2, y5 + 72, t, "h2", "middle"))
        A(text(x + bw / 2, y5 + 94, s, "tiny", "middle"))

    A("</svg>")

    svg = "\n".join(L)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    raw = open(OUT, "rb").read()
    assert "价值层".encode("utf-8") in raw
    print("saved:", OUT)
    print("bytes:", len(raw))


if __name__ == "__main__":
    main()
