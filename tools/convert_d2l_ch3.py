import re
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/d2l-ai/d2l-zh/master/chapter_linear-networks"
CHAPTERS = [
    ("linear-regression.md", "线性回归", "https://zh.d2l.ai/chapter_linear-networks/linear-regression.html", "2026-07-01 09:00:00"),
    ("linear-regression-scratch.md", "线性回归的从零开始实现", "https://zh.d2l.ai/chapter_linear-networks/linear-regression-scratch.html", "2026-07-01 10:00:00"),
    ("linear-regression-concise.md", "线性回归的简洁实现", "https://zh.d2l.ai/chapter_linear-networks/linear-regression-concise.html", "2026-07-01 11:00:00"),
    ("softmax-regression.md", "softmax回归", "https://zh.d2l.ai/chapter_linear-networks/softmax-regression.html", "2026-07-01 12:00:00"),
    ("image-classification-dataset.md", "图像分类数据集", "https://zh.d2l.ai/chapter_linear-networks/image-classification-dataset.html", "2026-07-01 13:00:00"),
    ("softmax-regression-scratch.md", "softmax回归的从零开始实现", "https://zh.d2l.ai/chapter_linear-networks/softmax-regression-scratch.html", "2026-07-01 14:00:00"),
    ("softmax-regression-concise.md", "softmax回归的简洁实现", "https://zh.d2l.ai/chapter_linear-networks/softmax-regression-concise.html", "2026-07-01 15:00:00"),
]
OUT = Path(r"e:/博客/myblog/myblog/source/_posts/深度学习/线性神经网络")

NUMREF = {
    "sec_linear_regression": "线性回归",
    "sec_linear_scratch": "线性回归的从零开始实现",
    "sec_linear_concise": "线性回归的简洁实现",
    "sec_softmax": "softmax回归",
    "sec_softmax_scratch": "softmax回归的从零开始实现",
    "sec_softmax_concise": "softmax回归的简洁实现",
    "sec_fashion_mnist": "图像分类数据集",
    "sec_autograd": "自动微分",
    "subsec_broadcasting": "广播机制",
    "subsec_normal_distribution_and_squared_loss": "正态分布与平方损失",
    "subseq_lin-alg-reduction": "张量降维",
    "subseq_lin-alg-non-reduction": "非降维求和",
    "sec_prob": "概率",
    "fig_single_neuron": "单层网络架构图",
    "fig_softmaxreg": "softmax回归网络图",
    "chap_optimization": "优化算法",
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


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read().decode("utf-8")


def replace_numref(text: str) -> str:
    def repl(m):
        key = m.group(1)
        return NUMREF.get(key, key)

    return re.sub(r":numref:`([^`]+)`", repl, text)


def replace_eqref(text: str) -> str:
    return re.sub(r":eqref:`([^`]+)`", "上式", text)


def clean_prose(text: str) -> str:
    text = replace_numref(text)
    text = replace_eqref(text)
    text = re.sub(r":label:`[^`]*`", "", text)
    text = re.sub(r":eqlabel:`[^`]*`", "", text)
    text = re.sub(r":cite:`[^`]*`", "", text)
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
    for i, part in enumerate(parts):
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
  - 线性神经网络
---

> 本文基于 [《动手学深度学习》{title}]({url}) 整理。

{body}
"""
        out_path = OUT / f"深度学习{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote {out_path} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
