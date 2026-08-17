---
title: Python语言入门与环境搭建
date: 2023-04-12 09:00:00
tags:
  - python
---

# Python 语言入门

Python 是一门解释型、动态类型的高级编程语言，由 Guido van Rossum 于 1991 年发布。语法简洁、生态丰富，广泛应用于 Web 开发、数据分析、机器学习、自动化运维和脚本工具。

## 为什么选择 Python

| 特点 | 说明 |
| ---- | ---- |
| 语法简洁 | 可读性强，适合快速开发 |
| 生态丰富 | PyPI 拥有海量第三方库 |
| 跨平台 | Windows、macOS、Linux 均可运行 |
| 多范式 | 支持面向对象、函数式、过程式 |
| 交互式 | REPL 适合探索与数据分析 |
| 社区活跃 | 文档完善，问题容易找到答案 |

常见应用场景：Django/Flask Web 服务、Pandas 数据分析、PyTorch/TensorFlow 深度学习、爬虫、自动化测试、DevOps 脚本等。

## 环境安装

### 1. 官方安装

访问 [https://www.python.org/downloads/](https://www.python.org/downloads/) 下载 Python 3.x（推荐 3.10+）。Windows 安装时勾选 **Add Python to PATH**。

验证安装：

```bash
python --version
# Python 3.12.0

python -m pip --version
```

### 2. 使用 pyenv（推荐 macOS/Linux）

管理多版本 Python：

```bash
pyenv install 3.12.0
pyenv global 3.12.0
```

### 3. 虚拟环境

每个项目应使用独立虚拟环境，避免依赖冲突：

```bash
# 创建虚拟环境
python -m venv .venv

# 激活（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 激活（macOS/Linux）
source .venv/bin/activate

# 退出
deactivate
```

## 第一个程序

创建 `hello.py`：

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("Python"))
```

运行：

```bash
python hello.py
# Hello, Python!
```

## 交互式 REPL

直接输入 `python` 进入交互模式，适合快速验证语法：

```python
>>> 2 + 3
5
>>> [x ** 2 for x in range(5)]
[0, 1, 4, 9, 16]
>>> exit()
```

IPython 提供更强大的交互体验：

```bash
pip install ipython
ipython
```

## 包管理 pip

```bash
pip install requests          # 安装包
pip install numpy==1.26.0     # 指定版本
pip list                      # 已安装列表
pip freeze > requirements.txt # 导出依赖
pip install -r requirements.txt
```

现代项目推荐使用 `pyproject.toml` + 虚拟环境（详见包管理章节）。

## 常用 IDE / 编辑器

| 工具 | 说明 |
| ---- | ---- |
| VS Code + Python 插件 | 轻量、免费、调试方便 |
| PyCharm | JetBrains 出品，功能全面 |
| Cursor | AI 辅助编程 |

## Python 2 vs Python 3

Python 2 已于 2020 年停止维护，**新项目一律使用 Python 3**。注意旧资料中的 `print "hello"` 语法在 Python 3 中已改为 `print("hello")`。

## 小结

- Python 3 是当前唯一选择，安装后配置虚拟环境
- `pip` 安装第三方库，`requirements.txt` 或 `pyproject.toml` 管理依赖
- REPL 适合快速实验，正式项目用 `.py` 文件组织代码
