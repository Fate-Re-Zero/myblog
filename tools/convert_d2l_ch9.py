import re
import time
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/d2l-ai/d2l-zh/master/chapter_recurrent-neural-networks"
CHAPTERS = [
    ("sequence.md", "序列模型", "https://zh.d2l.ai/chapter_recurrent-neural-networks/sequence.html", "2026-07-07 09:00:00"),
    ("text-preprocessing.md", "文本预处理", "https://zh.d2l.ai/chapter_recurrent-neural-networks/text-preprocessing.html", "2026-07-07 10:00:00"),
    ("language-models-and-dataset.md", "语言模型和数据集", "https://zh.d2l.ai/chapter_recurrent-neural-networks/language-models-and-dataset.html", "2026-07-07 11:00:00"),
    ("rnn.md", "循环神经网络", "https://zh.d2l.ai/chapter_recurrent-neural-networks/rnn.html", "2026-07-07 12:00:00"),
    ("rnn-scratch.md", "循环神经网络的从零开始实现", "https://zh.d2l.ai/chapter_recurrent-neural-networks/rnn-scratch.html", "2026-07-07 13:00:00"),
    ("rnn-concise.md", "循环神经网络的简洁实现", "https://zh.d2l.ai/chapter_recurrent-neural-networks/rnn-concise.html", "2026-07-07 14:00:00"),
    ("bptt.md", "通过时间反向传播", "https://zh.d2l.ai/chapter_recurrent-neural-networks/bptt.html", "2026-07-07 15:00:00"),
]
OUT = Path(r"e:/博客/myblog/myblog/source/_posts/深度学习/循环神经网络")

NUMREF = {
    "chap_linear": "线性神经网络",
    "chap_perceptrons": "多层感知机",
    "chap_computation": "深度学习计算",
    "chap_cnn": "卷积神经网络",
    "chap_modern_cnn": "现代卷积神经网络",
    "chap_cv": "计算机视觉",
    "chap_rnn": "循环神经网络",
    "sec_sequence": "序列模型",
    "sec_text_preprocessing": "文本预处理",
    "sec_language_model": "语言模型和数据集",
    "sec_rnn": "循环神经网络",
    "sec_rnn_scratch": "循环神经网络的从零开始实现",
    "sec_rnn_concise": "循环神经网络的简洁实现",
    "sec_bptt": "通过时间反向传播",
    "sec_mlp": "多层感知机",
    "sec_autograd": "自动微分",
    "sec_fashion_mnist": "图像分类数据集",
    "sec_use_gpu": "GPU",
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
  - 循环神经网络
---

> 本文基于 [《动手学深度学习》{title}]({url}) 整理。

{body}
"""
        out_path = OUT / f"深度学习{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote {out_path} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
