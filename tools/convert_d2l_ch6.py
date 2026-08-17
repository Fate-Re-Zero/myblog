import re
import time
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/d2l-ai/d2l-zh/master/chapter_convolutional-neural-networks"
CHAPTERS = [
    ("why-conv.md", "从全连接层到卷积", "https://zh.d2l.ai/chapter_convolutional-neural-networks/why-conv.html", "2026-07-04 09:00:00"),
    ("conv-layer.md", "卷积层", "https://zh.d2l.ai/chapter_convolutional-neural-networks/conv-layer.html", "2026-07-04 10:00:00"),
    ("padding-and-strides.md", "填充和步幅", "https://zh.d2l.ai/chapter_convolutional-neural-networks/padding-and-strides.html", "2026-07-04 11:00:00"),
    ("channels.md", "多通道", "https://zh.d2l.ai/chapter_convolutional-neural-networks/channels.html", "2026-07-04 12:00:00"),
    ("pooling.md", "汇聚层", "https://zh.d2l.ai/chapter_convolutional-neural-networks/pooling.html", "2026-07-04 13:00:00"),
    ("lenet.md", "卷积神经网络（LeNet）", "https://zh.d2l.ai/chapter_convolutional-neural-networks/lenet.html", "2026-07-04 14:00:00"),
]
OUT = Path(r"e:/博客/myblog/myblog/source/_posts/深度学习/卷积神经网络")

NUMREF = {
    "chap_linear": "线性神经网络",
    "chap_perceptrons": "多层感知机",
    "chap_computation": "深度学习计算",
    "chap_cnn": "卷积神经网络",
    "sec_why-conv": "从全连接层到卷积",
    "sec_conv_layer": "卷积层",
    "sec_padding-and-strides": "填充和步幅",
    "sec_channels": "多通道",
    "sec_pooling": "汇聚层",
    "sec_lenet": "卷积神经网络（LeNet）",
    "sec_mlp": "多层感知机",
    "sec_mlp_scratch": "多层感知机的从零开始实现",
    "sec_mlp_concise": "多层感知机的简洁实现",
    "sec_softmax_scratch": "softmax回归的从零开始实现",
    "sec_fashion_mnist": "图像分类数据集",
    "sec_model_construction": "层和块",
    "sec_parameters": "参数管理",
    "sec_custom_layer": "自定义层",
    "sec_use_gpu": "GPU",
    "img_waldo": "沃尔多游戏示例图",
    "fig_waldo_mask": "发现沃尔多",
    "subsec_why-conv-channels": "通道",
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
  - 卷积神经网络
---

> 本文基于 [《动手学深度学习》{title}]({url}) 整理。

{body}
"""
        out_path = OUT / f"深度学习{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote {out_path} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
