import re
import time
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/d2l-ai/d2l-zh/master/chapter_multilayer-perceptrons"
CHAPTERS = [
    ("mlp.md", "多层感知机", "https://zh.d2l.ai/chapter_multilayer-perceptrons/mlp.html", "2026-07-02 09:00:00"),
    ("mlp-scratch.md", "多层感知机的从零开始实现", "https://zh.d2l.ai/chapter_multilayer-perceptrons/mlp-scratch.html", "2026-07-02 10:00:00"),
    ("mlp-concise.md", "多层感知机的简洁实现", "https://zh.d2l.ai/chapter_multilayer-perceptrons/mlp-concise.html", "2026-07-02 11:00:00"),
    ("underfit-overfit.md", "模型选择、欠拟合和过拟合", "https://zh.d2l.ai/chapter_multilayer-perceptrons/model-selection.html", "2026-07-02 12:00:00"),
    ("weight-decay.md", "权重衰减", "https://zh.d2l.ai/chapter_multilayer-perceptrons/weight-decay.html", "2026-07-02 13:00:00"),
    ("dropout.md", "暂退法（Dropout）", "https://zh.d2l.ai/chapter_multilayer-perceptrons/dropout.html", "2026-07-02 14:00:00"),
    ("backprop.md", "前向传播、反向传播和计算图", "https://zh.d2l.ai/chapter_multilayer-perceptrons/backprop.html", "2026-07-02 15:00:00"),
    ("numerical-stability-and-init.md", "数值稳定性和模型初始化", "https://zh.d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html", "2026-07-02 16:00:00"),
    ("environment.md", "环境和分布偏移", "https://zh.d2l.ai/chapter_multilayer-perceptrons/environment-and-distribution-shift.html", "2026-07-02 17:00:00"),
    ("kaggle-house-price.md", "实战Kaggle比赛：预测房价", "https://zh.d2l.ai/chapter_multilayer-perceptrons/kaggle-house-price.html", "2026-07-02 18:00:00"),
]
OUT = Path(r"e:/博客/myblog/myblog/source/_posts/深度学习/多层感知机")

NUMREF = {
    "chap_linear": "线性神经网络",
    "chap_perceptrons": "多层感知机",
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
    "subsec_linear_model": "线性模型",
    "subsec_parameterization-cost-fc-layers": "全连接层的参数开销",
    "subsec_softmax_vectorization": "小批量样本的矢量化",
    "subsec_softmax-implementation-revisited": "重新审视Softmax的实现",
    "subseq_lin-alg-reduction": "张量降维",
    "subseq_lin-alg-non-reduction": "非降维求和",
    "sec_prob": "概率",
    "fig_single_neuron": "单层网络架构图",
    "fig_softmaxreg": "softmax回归网络图",
    "fig_mlp": "多层感知机网络图",
    "fig_forward": "前向传播计算图",
    "chap_optimization": "优化算法",
    "sec_mlp": "多层感知机",
    "sec_mlp_scratch": "多层感知机的从零开始实现",
    "sec_mlp_concise": "多层感知机的简洁实现",
    "sec_model_selection": "模型选择、欠拟合和过拟合",
    "sec_weight_decay": "权重衰减",
    "sec_dropout": "暂退法",
    "sec_backprop": "前向传播、反向传播和计算图",
    "sec_numerical_stability": "数值稳定性和模型初始化",
    "sec_distribution_shift": "环境和分布偏移",
    "sec_kaggle_house": "实战Kaggle比赛：预测房价",
    "subsec_activation_functions": "激活函数",
    "subsec_xavier": "Xavier初始化",
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
  - 多层感知机
---

> 本文基于 [《动手学深度学习》{title}]({url}) 整理。

{body}
"""
        out_path = OUT / f"深度学习{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote {out_path} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
