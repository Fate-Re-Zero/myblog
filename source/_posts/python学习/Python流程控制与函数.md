---
title: Python流程控制与函数
date: 2023-04-07 11:00:00
tags:
  - python
---

# 流程控制与函数

## 条件语句

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"

# 三元表达式
grade = "A" if score >= 90 else "B"

# match-case（Python 3.10+）
match status:
    case 200:
        print("OK")
    case 404:
        print("Not Found")
    case _:
        print("Unknown")
```

## 循环

### for 循环

```python
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2):  # 2, 4, 6, 8
    print(i)

fruits = ["apple", "banana"]
for fruit in fruits:
    print(fruit)

for idx, fruit in enumerate(fruits):
    print(idx, fruit)
```

### while 循环

```python
n = 0
while n < 5:
    print(n)
    n += 1
```

### break 与 continue

```python
for i in range(10):
    if i == 3:
        continue   # 跳过本次
    if i == 7:
        break      # 退出循环
    print(i)
```

### else 子句

循环正常结束（未 break）时执行 else：

```python
for x in data:
    if x < 0:
        print("found negative")
        break
else:
    print("all positive")
```

## 函数定义

```python
def add(a: int, b: int) -> int:
    """返回 a + b。"""
    return a + b

# 默认参数（默认值在定义时求值，可变默认值是常见陷阱）
def greet(name: str, prefix: str = "Hello") -> str:
    return f"{prefix}, {name}!"

# 关键字参数
greet(name="Alice", prefix="Hi")
greet("Bob")  # 位置参数
```

### 可变参数

```python
def sum_all(*args: int) -> int:
    return sum(args)

sum_all(1, 2, 3, 4)  # 10

def print_info(**kwargs) -> None:
    for k, v in kwargs.items():
        print(f"{k}={v}")

print_info(name="Alice", age=25)
```

### 仅关键字参数

```python
def connect(host: str, *, port: int = 5432, timeout: int = 30):
    ...

connect("localhost", port=8080)  # host 位置，port/timeout 必须关键字
```

## Lambda 表达式

匿名函数，适合简单场景：

```python
square = lambda x: x ** 2
sorted(items, key=lambda x: x["score"], reverse=True)
```

复杂逻辑应使用 `def`，lambda 仅一行表达式。

## 作用域 LEGB

查找顺序：**L**ocal → **E**nclosing → **G**lobal → **B**uilt-in

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)
    inner()

outer()  # local
```

修改外层变量用 `nonlocal`，修改全局用 `global`（尽量少用）：

```python
def counter():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc
```

## 推导式

```python
# 列表推导
squares = [x ** 2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]

# 字典推导
{d: d ** 2 for d in range(5)}

# 集合推导
{x % 3 for x in range(10)}

# 生成器表达式（惰性，省内存）
sum(x ** 2 for x in range(1000000))
```

## 小结

- `if/elif/else`、`for`、`while` 构成流程控制主干
- 函数支持默认参数、`*args`、`**kwargs`
- 避免可变默认参数 `[ ]` 或 `{}`，改用 `None`
- 列表推导式简洁，但复杂逻辑仍用普通循环
