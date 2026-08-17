import re
import time
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/d2l-ai/d2l-zh/master/chapter_computer-vision"
CHAPTERS = [
    ("image-augmentation.md", "图像增广", "https://zh.d2l.ai/chapter_computer-vision/image-augmentation.html", "2026-07-06 09:00:00"),
    ("fine-tuning.md", "微调", "https://zh.d2l.ai/chapter_computer-vision/fine-tuning.html", "2026-07-06 10:00:00"),
    ("bounding-box.md", "边界框", "https://zh.d2l.ai/chapter_computer-vision/bounding-box.html", "2026-07-06 11:00:00"),
    ("anchor.md", "锚框", "https://zh.d2l.ai/chapter_computer-vision/anchor.html", "2026-07-06 12:00:00"),
    ("multiscale-object-detection.md", "多尺度目标检测", "https://zh.d2l.ai/chapter_computer-vision/multiscale-object-detection.html", "2026-07-06 13:00:00"),
    ("object-detection-dataset.md", "目标检测数据集", "https://zh.d2l.ai/chapter_computer-vision/object-detection-dataset.html", "2026-07-06 14:00:00"),
    ("ssd.md", "单发多框检测（SSD）", "https://zh.d2l.ai/chapter_computer-vision/ssd.html", "2026-07-06 15:00:00"),
    ("rcnn.md", "区域卷积神经网络（R-CNN）", "https://zh.d2l.ai/chapter_computer-vision/rcnn.html", "2026-07-06 16:00:00"),
    ("semantic-segmentation-and-dataset.md", "语义分割和数据集", "https://zh.d2l.ai/chapter_computer-vision/semantic-segmentation-and-dataset.html", "2026-07-06 17:00:00"),
    ("transposed-conv.md", "转置卷积", "https://zh.d2l.ai/chapter_computer-vision/transposed-conv.html", "2026-07-06 18:00:00"),
    ("fcn.md", "全卷积网络", "https://zh.d2l.ai/chapter_computer-vision/fcn.html", "2026-07-06 19:00:00"),
    ("neural-style.md", "样式迁移", "https://zh.d2l.ai/chapter_computer-vision/neural-style.html", "2026-07-06 20:00:00"),
    ("kaggle-cifar10.md", "实战Kaggle比赛：CIFAR-10", "https://zh.d2l.ai/chapter_computer-vision/kaggle-cifar10.html", "2026-07-06 21:00:00"),
    ("kaggle-dog.md", "实战Kaggle比赛：狗品种识别", "https://zh.d2l.ai/chapter_computer-vision/kaggle-dog.html", "2026-07-06 22:00:00"),
]
OUT = Path(r"e:/博客/myblog/myblog/source/_posts/深度学习/计算机视觉")

NUMREF = {
    "chap_linear": "线性神经网络",
    "chap_perceptrons": "多层感知机",
    "chap_computation": "深度学习计算",
    "chap_cnn": "卷积神经网络",
    "chap_modern_cnn": "现代卷积神经网络",
    "chap_cv": "计算机视觉",
    "sec_lenet": "卷积神经网络（LeNet）",
    "sec_alexnet": "深度卷积神经网络（AlexNet）",
    "sec_vgg": "使用块的网络（VGG）",
    "sec_resnet": "残差网络（ResNet）",
    "sec_fashion_mnist": "图像分类数据集",
    "sec_use_gpu": "GPU",
    "sec_image_augmentation": "图像增广",
    "sec_fine_tuning": "微调",
    "sec_bbox": "边界框",
    "sec_anchor": "锚框",
    "sec_multiscale_detection": "多尺度目标检测",
    "sec_object_detection_dataset": "目标检测数据集",
    "sec_ssd": "单发多框检测（SSD）",
    "sec_rcnn": "区域卷积神经网络（R-CNN）",
    "sec_semantic_segmentation": "语义分割和数据集",
    "sec_transposed_conv": "转置卷积",
    "sec_fcn": "全卷积网络",
    "sec_neural_style": "样式迁移",
    "sec_kaggle_cifar10": "实战Kaggle比赛：CIFAR-10",
    "sec_kaggle_dog": "实战Kaggle比赛：狗品种识别",
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
  - 计算机视觉
---

> 本文基于 [《动手学深度学习》{title}]({url}) 整理。

{body}
"""
        out_path = OUT / f"深度学习{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote {out_path} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
