---
title: Python模块与包管理
date: 2023-04-09 17:00:00
tags:
  - python
---

# 模块与包管理

## 模块（Module）

一个 `.py` 文件即一个模块：

```python
# mathutil.py
PI = 3.14159

def add(a: int, b: int) -> int:
    return a + b
```

```python
# main.py
import mathutil
from mathutil import add, PI
from mathutil import add as mu_add

print(mathutil.add(1, 2))
print(add(1, 2))
```

## 包（Package）

含 `__init__.py` 的目录（Python 3.3+ 命名空间包可省略，但显式 `__init__.py` 仍推荐）：

```
myproject/
├── pyproject.toml
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
└── tests/
    └── test_user.py
```

```python
from myapp.models.user import User
from myapp.utils.helpers import format_date
```

## `__init__.py`

控制包的公开接口：

```python
# myapp/models/__init__.py
from .user import User
from .order import Order

__all__ = ["User", "Order"]
```

## 相对导入

包内部模块互相引用：

```python
# 在 myapp/models/order.py 中
from .user import User
from ..utils.helpers import format_date
```

## `if __name__ == "__main__"`

模块被直接运行时执行，被 import 时不执行：

```python
def main():
    print("running as script")

if __name__ == "__main__":
    main()
```

## pip 与 requirements.txt

```bash
pip install requests
pip freeze > requirements.txt
pip install -r requirements.txt
```

## pyproject.toml（现代标准）

PEP 517/518 推荐的项目配置：

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

安装开发依赖：

```bash
pip install -e ".[dev]"
```

## 虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -e .
```

## 常用工具

| 工具 | 用途 |
| ---- | ---- |
| pip | 包安装 |
| venv | 虚拟环境 |
| poetry / uv | 依赖与项目管理 |
| ruff | 极速 linter + formatter |
| mypy | 静态类型检查 |

## `sys.path` 与 PYTHONPATH

Python 按以下顺序查找模块：

1. 当前目录
2. `PYTHONPATH` 环境变量
3. 标准库
4. site-packages

避免随意修改 `sys.path`，用包结构和 `-e` 可编辑安装。

## 小结

- 模块是 `.py` 文件，包是含 `__init__.py` 的目录
- 项目用 `pyproject.toml` + 虚拟环境管理依赖
- 相对导入仅在包内使用
- `if __name__ == "__main__"` 区分脚本入口与模块导入
