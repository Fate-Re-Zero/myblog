---
title: Python基础语法与数据类型
date: 2023-04-05 10:00:00
tags:
  - python
---

# 基础语法与数据类型

## 变量与赋值

Python 是动态类型语言，无需声明类型：

```python
x = 10
x = "hello"   # 合法，类型可变
name = "Alice"
age = 25
```

多重赋值：

```python
a, b, c = 1, 2, 3
x, y = y, x   # 交换
```

## 基本数据类型

| 类型 | 示例 | 说明 |
| ---- | ---- | ---- |
| `int` | `42`, `-100` | 任意精度整数 |
| `float` | `3.14`, `1e-5` | 双精度浮点 |
| `bool` | `True`, `False` | 布尔值 |
| `str` | `"hello"`, `'world'` | 字符串 |
| `None` | `None` | 空值，类似 null |

类型检查与转换：

```python
type(42)           # <class 'int'>
isinstance(x, int) # True

int("42")          # 42
float("3.14")      # 3.14
str(100)           # "100"
bool(0)            # False
bool("")           # False
```

## 运算符

```python
# 算术
10 + 3    # 13
10 // 3   # 3（整除）
10 % 3    # 1
2 ** 10   # 1024

# 比较
a == b
a != b
a < b

# 逻辑
a and b
a or b
not a

# 成员
"x" in "hello"     # True
3 in [1, 2, 3]     # True

# 身份（比较对象 id）
a is b
a is not b
```

**注意**：`==` 比较值，`is` 比较是否为同一对象。小整数缓存导致 `a is b` 有时为 True，不要用 `is` 比较字符串内容。

## 字符串基础

```python
s = "Hello"
s = 'World'
s = """多行
字符串"""

# f-string（Python 3.6+，推荐）
name = "Alice"
msg = f"Hello, {name}!"

# 常用方法
"hello".upper()       # "HELLO"
"  trim  ".strip()    # "trim"
"a,b,c".split(",")    # ["a", "b", "c"]
"-".join(["a", "b"])  # "a-b"
```

## 输入输出

```python
name = input("请输入姓名: ")
print("Hello,", name)
print(f"年龄: {age}", end="\n")
```

## 注释与文档

```python
# 单行注释

"""
多行字符串，也可作模块/函数文档
"""

def add(a: int, b: int) -> int:
    """返回两数之和。"""
    return a + b

print(add.__doc__)
```

## 类型注解（Type Hints）

Python 3.5+ 支持类型提示，运行时不强制检查，供 IDE 和 mypy 使用：

```python
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}! " * times).strip()

scores: list[int] = [90, 85, 92]
user: dict[str, int] = {"age": 25}
```

## 常量约定

Python 无真正常量，约定全大写表示不应修改：

```python
MAX_SIZE = 1024
DEFAULT_TIMEOUT = 30
```

## 小结

- 动态类型，变量无需声明
- 基本类型：int、float、bool、str、None
- f-string 是字符串格式化的首选方式
- 类型注解提升可读性和工具支持，但不影响运行时行为
