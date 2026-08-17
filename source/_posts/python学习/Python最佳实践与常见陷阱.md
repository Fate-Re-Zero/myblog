---
title: Python最佳实践与常见陷阱
date: 2023-04-15 22:00:00
tags:
  - python
---

# 最佳实践与常见陷阱

## 代码风格 PEP 8

Python 官方风格指南，核心要点：

```python
# 好
def calculate_total(items: list[float]) -> float:
    return sum(items)

MAX_RETRIES = 3
user_name = "alice"

# 命名
# 变量/函数: snake_case
# 类: PascalCase
# 常量: UPPER_SNAKE_CASE
# 私有: _leading_underscore
```

工具自动格式化：

```bash
ruff format .
ruff check --fix .
```

## 常见陷阱

### 可变默认参数

```python
# 错误：默认值只创建一次
def append_item(item, lst=[]):
    lst.append(item)
    return lst

append_item(1)   # [1]
append_item(2)   # [1, 2]  意外共享

# 正确
def append_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### 循环中捕获变量

```python
# 错误
funcs = []
for i in range(3):
    funcs.append(lambda: i)
[f() for f in funcs]   # [2, 2, 2]

# 正确
funcs = [lambda x=i: x for i in range(3)]
[f() for f in funcs]   # [0, 1, 2]
```

### 浅拷贝

```python
a = [[1, 2], [3, 4]]
b = a.copy()           # 或 list(a)、a[:]
a[0][0] = 99
# b[0][0] 也是 99

import copy
c = copy.deepcopy(a)   # 深拷贝
```

### `is` vs `==`

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b    # True，值相等
a is b    # False，不同对象

# 不要用 is 比较字符串、数字内容
# 例外：与 None 比较用 is None
if x is None:
    ...
```

### 浮点精度

```python
0.1 + 0.2 == 0.3   # False

from decimal import Decimal
Decimal("0.1") + Decimal("0.2") == Decimal("0.3")   # True

import math
math.isclose(0.1 + 0.2, 0.3)   # True
```

### 闭包延迟绑定

```python
# 错误
buttons = []
for i in range(3):
    buttons.append(lambda: print(i))
# 全部打印 2

# 正确：默认参数绑定
buttons = [lambda i=i: print(i) for i in range(3)]
```

## Pythonic 写法

```python
# 交换
a, b = b, a

# 遍历带索引
for i, val in enumerate(items):
    ...

# 同时遍历多个序列
for a, b in zip(list_a, list_b):
    ...

# 字典默认值
d.get(key, default)
collections.defaultdict(list)

# 解包
first, *middle, last = [1, 2, 3, 4, 5]

# 成员检测
if item in collection:
    ...

# 真值测试
if items:          # 非空
    ...
if not items:      # 空
    ...
```

## 性能建议

| 场景 | 建议 |
| ---- | ---- |
| 字符串拼接 | `"".join(parts)` |
| 成员检测 | set 而非 list |
| 数值计算 | NumPy 向量化 |
| IO 密集 | 异步 asyncio 或多线程 |
| CPU 密集 | multiprocessing（绕过 GIL） |

## GIL 简述

CPython 的全局解释器锁（GIL）使同一进程内多线程无法并行执行 Python 字节码。多线程适合 IO 密集；CPU 密集任务用 `multiprocessing` 或调用 C 扩展（NumPy 等）。

## 项目结构参考

```
myproject/
├── pyproject.toml
├── README.md
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       ├── services/
│       └── api/
├── tests/
│   ├── conftest.py
│   └── test_*.py
└── .venv/
```

## 学习路线建议

```
入门 → 语法 / 数据类型 / 流程控制
     → 列表 / 字典 / 字符串
     → 面向对象 / 异常 / 文件 IO
     → 模块 / 迭代器 / 装饰器
     → 标准库 / 测试
     → Web（Flask/FastAPI）/ 数据分析（Pandas）/ 自动化
     → 异步 asyncio / 类型系统 / 源码阅读
```

## 系列目录

| 章节 | 主题 |
| ---- | ---- |
| 1 | Python语言入门与环境搭建 |
| 2 | Python基础语法与数据类型 |
| 3 | Python流程控制与函数 |
| 4 | Python列表字典与集合 |
| 5 | Python字符串与正则表达式 |
| 6 | Python面向对象编程 |
| 7 | Python异常处理 |
| 8 | Python文件与IO |
| 9 | Python模块与包管理 |
| 10 | Python迭代器与生成器 |
| 11 | Python装饰器与上下文管理器 |
| 12 | Python标准库实战 |
| 13 | Python测试与调试 |
| 14 | Python最佳实践与常见陷阱（本文） |

## 小结

Python 强调可读性与开发效率。避开可变默认值、浅拷贝、闭包绑定等经典陷阱，配合 pytest、ruff、mypy 等工具，即可写出健壮、易维护的代码。进阶方向包括 Web 框架、数据科学、自动化运维和 asyncio 异步编程。
