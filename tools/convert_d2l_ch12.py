import re
import time
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/d2l-ai/d2l-zh/master/chapter_optimization"
CHAPTERS = [
    ("optimization-intro.md", "优化和深度学习", "https://zh.d2l.ai/chapter_optimization/optimization-intro.html", "2026-07-10 09:00:00"),
    ("convexity.md", "凸性", "https://zh.d2l.ai/chapter_optimization/convexity.html", "2026-07-10 10:00:00"),
    ("gd.md", "梯度下降", "https://zh.d2l.ai/chapter_optimization/gd.html", "2026-07-10 11:00:00"),
    ("sgd.md", "随机梯度下降", "https://zh.d2l.ai/chapter_optimization/sgd.html", "2026-07-10 12:00:00"),
    ("minibatch-sgd.md", "小批量随机梯度下降", "https://zh.d2l.ai/chapter_optimization/minibatch-sgd.html", "2026-07-10 13:00:00"),
    ("momentum.md", "动量法", "https://zh.d2l.ai/chapter_optimization/momentum.html", "2026-07-10 14:00:00"),
    ("adagrad.md", "AdaGrad算法", "https://zh.d2l.ai/chapter_optimization/adagrad.html", "2026-07-10 15:00:00"),
    ("rmsprop.md", "RMSProp算法", "https://zh.d2l.ai/chapter_optimization/rmsprop.html", "2026-07-10 16:00:00"),
    ("adadelta.md", "AdaDelta算法", "https://zh.d2l.ai/chapter_optimization/adadelta.html", "2026-07-10 17:00:00"),
    ("adam.md", "Adam算法", "https://zh.d2l.ai/chapter_optimization/adam.html", "2026-07-10 18:00:00"),
    ("lr-scheduler.md", "学习率调度器", "https://zh.d2l.ai/chapter_optimization/lr-scheduler.html", "2026-07-10 19:00:00"),
]
OUT = Path(r"e:/博客/myblog/myblog/source/_posts/深度学习/优化算法")

NUMREF = {
    "chap_optimization": "优化算法",
    "sec_model_selection": "模型选择、欠拟合和过拟合",
    "sec_linear_regression": "线性回归",
    "subsec_empirical-risk-and-risk": "经验风险与风险",
    "subsec_activation_functions": "激活函数",
    "sec_optimization_intro": "优化和深度学习",
    "sec_convexity": "凸性",
    "sec_gd": "梯度下降",
    "sec_sgd": "随机梯度下降",
    "sec_minibatch_sgd": "小批量随机梯度下降",
    "sec_momentum": "动量法",
    "sec_adagrad": "AdaGrad算法",
    "sec_rmsprop": "RMSProp算法",
    "sec_adadelta": "AdaDelta算法",
    "sec_adam": "Adam算法",
    "sec_lr_scheduler": "学习率调度器",
    "sec_mlp": "多层感知机",
    "sec_rnn": "循环神经网络",
}

MXNET_MARKERS = (
    "attach_grad",
    "npx.",
    "gluon",
    "autograd.record",
    "from mxnet",
    "import mxnet",
)
OTHER_FW_MARKERS = ("tensorflow", "tf.", "paddle.", "from paddle", "import paddle")


def fetch(url: str, retries: int = 5) -> str:
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 10))
    raise last_err


def replace_numref(text: str) -> str:
    def repl(m):
        return NUMREF.get(m.group(1), m.group(1))

    return re.sub(r":numref:`([^`]+)`", repl, text)


def replace_eqref(text: str) -> str:
    return re.sub(r":eqref:`([^`]+)`", "上式", text)


def clean_prose(text: str) -> str:
    text = replace_numref(text)
    text = replace_eqref(text)
    text = re.sub(r":label:`[^`]*`", "", text)
    text = re.sub(r":eqlabel:`[^`]*`", "", text)
    text = re.sub(r":cite:`[^`]*`", "", text)
    text = re.sub(r":width:`[^`]*`", "", text)
    text = re.sub(r":height:`[^`]*`", "", text)
    text = re.sub(r":begin_tab:`[^`]*`[\s\S]*?:end_tab:", "", text)
    text = re.sub(r"\(\*\*\)", "", text)
    text = re.sub(r"\(\~\~[^~]*\~\~\)", "", text)
    text = re.sub(r"\(\*\*([\s\S]*?)\*\*\)", r"\1", text)
    text = re.sub(r"\[\*\*([\s\S]*?)\*\*\]", r"\1", text)
    text = re.sub(r"\*\*\(\*\*([^*]+)\*\*\)", r"\1", text)
    text = re.sub(r"\*\*\(([^)]*)\)\*\*", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"（图：\1）", text)
    text = re.sub(r"\[Discussions\]\([^\)]+\)", "", text)
    return text


def clean_document(md: str) -> str:
    parts = re.split(r"(```[\s\S]*?```)", md)
    cleaned = []
    for part in parts:
        if part.startswith("```"):
            cleaned.append(part)
        else:
            prose = clean_prose(part)
            prose = re.sub(r"[^\S\n]+", " ", prose)
            prose = re.sub(r" *\n", "\n", prose)
            cleaned.append(prose)
    return "".join(cleaned)


def is_non_pytorch_code(code: str) -> bool:
    if "torch" in code or "pytorch" in code.lower():
        return False
    if any(m in code for m in MXNET_MARKERS):
        return True
    if any(m in code for m in OTHER_FW_MARKERS):
        return True
    if "attach_grad" in code:
        return True
    return False


def extract_pytorch_code(block: str) -> str:
    block = block.strip()
    if block.startswith("{.python .input}"):
        block = block[len("{.python .input}") :].lstrip("\n")

    lines = block.split("\n")
    if not any("#@tab" in l for l in lines):
        code = [l for l in lines if not l.strip().startswith("#@tab")]
        joined = "\n".join(code).strip()
        if is_non_pytorch_code(joined):
            return ""
        return joined

    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in lines:
        m = re.match(r"#@tab\s+(.+)", line.strip())
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()

    for key in ["pytorch", "all", "mxnet, pytorch, paddle", "pytorch, paddle"]:
        if key in sections and sections[key]:
            return sections[key]
    return ""


def convert_code_blocks(md: str) -> str:
    pattern = re.compile(r"```(?:\{\.python \.input\})?\n([\s\S]*?)```", re.MULTILINE)

    def repl(m):
        code = extract_pytorch_code(m.group(1))
        if not code:
            return ""
        return f"\n```python\n{code}\n```\n"

    return pattern.sub(repl, md)


def convert(md: str) -> str:
    md = convert_code_blocks(md)
    md = clean_document(md)
    lines = []
    for line in md.split("\n"):
        if line.strip().startswith(":begin_tab:") or line.strip().startswith(":end_tab:"):
            continue
        lines.append(line.rstrip())
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for fname, title, url, date in CHAPTERS:
        print(f"Fetching {fname}...")
        raw = fetch(f"{BASE}/{fname}")
        body = convert(raw)
        if not body.startswith("#"):
            body = f"# {title}\n\n{body}"

        content = f"""---
title: {title}
date: {date}
tags:
  - 深度学习
  - 动手学深度学习
  - 优化算法
---

> 本文基于 [《动手学深度学习》{title}]({url}) 整理。

{body}
"""
        out_path = OUT / f"深度学习{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote {out_path} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
