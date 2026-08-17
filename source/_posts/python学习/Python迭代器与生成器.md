---
title: Python迭代器与生成器
date: 2023-04-04 18:00:00
tags:
  - python
---

# 迭代器与生成器

迭代是 Python 的核心机制，`for` 循环、列表推导、生成器表达式都建立在迭代协议之上。

## 可迭代对象与迭代器

**可迭代对象（Iterable）**：实现 `__iter__()`，返回迭代器。

**迭代器（Iterator）**：实现 `__iter__()` 和 `__next__()`，`__next__()` 结束时抛出 `StopIteration`。

```python
nums = [1, 2, 3]
it = iter(nums)
next(it)   # 1
next(it)   # 2
next(it)   # 3
next(it)   # StopIteration
```

内置可迭代：list、tuple、dict、set、str、文件对象等。

## 自定义迭代器

```python
class CountDown:
    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for n in CountDown(3):
    print(n)   # 3, 2, 1
```

## 生成器函数

用 `yield` 简化迭代器实现：

```python
def countdown(start: int):
    while start > 0:
        yield start
        start -= 1

for n in countdown(3):
    print(n)

gen = countdown(3)
next(gen)   # 3
next(gen)   # 2
```

生成器是**惰性**的：按需产生值，节省内存。

## 生成器表达式

```python
squares = (x ** 2 for x in range(1000000))  # 不立即计算
total = sum(x ** 2 for x in range(100))     # 可直接传给函数
```

与列表推导 `[...]` 的区别：生成器表达式用 `()`，返回生成器而非列表。

## yield from

委托子生成器：

```python
def chain(*iterables):
    for it in iterables:
        yield from it

list(chain([1, 2], [3, 4]))   # [1, 2, 3, 4]
```

## itertools 常用工具

```python
import itertools

# 无限迭代
itertools.count(10, 2)       # 10, 12, 14, ...
itertools.cycle("AB")        # A, B, A, B, ...
itertools.repeat(7, 3)       # 7, 7, 7

# 组合
itertools.chain([1, 2], [3, 4])
itertools.islice(range(100), 5, 10)
itertools.product([1, 2], ["a", "b"])
itertools.permutations([1, 2, 3], 2)
itertools.combinations([1, 2, 3], 2)

# 分组
for key, group in itertools.groupby("aaabbccc"):
    print(key, list(group))
```

## 应用场景

### 大文件处理

```python
def read_large_file(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.strip()
```

### 管道式数据处理

```python
def parse_lines(lines):
    for line in lines:
        yield line.split(",")

def filter_empty(records):
    for rec in records:
        if rec:
            yield rec

pipeline = filter_empty(parse_lines(read_large_file("data.csv")))
for row in pipeline:
    process(row)
```

## 小结

- 迭代协议：`__iter__` + `__next__`
- 生成器用 `yield`，惰性求值，适合大数据流
- `itertools` 提供丰富的迭代工具
- 列表推导求值全部元素，生成器表达式按需求值
